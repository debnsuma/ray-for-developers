import os

os.environ["RAY_TRAIN_V2_ENABLED"] = "1"

import uuid
import torch
import ray.train.torch
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP, ShardingStrategy
from torchvision.models import VisionTransformer
from torch.optim.adam import Adam


def log_mem(device, tag):
    torch.cuda.synchronize(device)
    alloc = torch.cuda.memory_allocated(device) / 1e9
    res = torch.cuda.memory_reserved(device) / 1e9
    peak = torch.cuda.max_memory_allocated(device) / 1e9
    print(f"[{tag}] alloc={alloc:.3f} GB  res={res:.3f} GB  peak={peak:.3f} GB")


def build_visual_transformer():
    model = VisionTransformer(
        image_size=32,  # CIFAR-10 image size is 32x32
        patch_size=4,  # Patch size is 4x4
        num_layers=12,  # Number of transformer layers
        num_heads=8,  # Number of attention heads
        hidden_dim=3840,  # Hidden size (can be adjusted)
        mlp_dim=768,  # MLP dimension (can be adjusted)
        num_classes=10,  # CIFAR-10 has 10 classes
    )
    # print out number of parameters in model

    return model


def train_func(config):
    # print("ENV VAR CHECK", os.environ["PYTORCH_CUDA_ALLOC_CONF"])
    device = ray.train.torch.get_device()
    print(f"{device=}")
    torch.cuda.reset_peak_memory_stats(device)
    log_mem(device, "before init")

    # Model
    model = build_visual_transformer()

    # 2) Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")

    # 3) Estimate size in float32 (4 bytes/param) and float16 (2 bytes/param)
    size_bytes_fp32 = total_params * 4
    size_gb_fp32 = size_bytes_fp32 / (1024**3)
    print(f"Model size (float32): {size_gb_fp32:.4f} GB")

    # 4) Wrap in FSDP if >1 worker
    world_size = ray.train.get_context().get_world_size()
    if world_size > 1:
        model = FSDP(
            model.to(device),
            sharding_strategy=config["sharding_strategy"],
        )
    else:
        model = model.to(device)

    log_mem(device, "after FSDP wrap")

    # optimizer init
    optimizer = Adam(model.parameters(), lr=0.001)
    log_mem(device, "after optimizer init")

    # Fake one‐batch forward + backward
    dummy = torch.randn(config["batch_size"] // world_size, 3, 32, 32, device=device)
    log_mem(device, "after creating batch")

    # Forward pass
    out = model(dummy)
    log_mem(device, "after forward pass")

    loss = out.sum()
    log_mem(device, "after computing loss")

    # Backward pass
    loss.backward()
    log_mem(device, "after backward")

    # Optimizer update
    optimizer.step()
    log_mem(device, "after optimizer step")


if __name__ == "__main__":
    num_workers = 2
    sharding_strategy = ShardingStrategy.FULL_SHARD

    trainer = ray.train.torch.TorchTrainer(
        train_func,
        train_loop_config={
            "sharding_strategy": sharding_strategy,
            "batch_size": 32,
        },
        scaling_config=ray.train.ScalingConfig(
            num_workers=num_workers,
            resources_per_worker={"accelerator_type:T4": 0.001},
            use_gpu=True,
        ),
        run_config=ray.train.RunConfig(
            storage_path="/mnt/cluster_storage/fsdp_checkpointing/",
            name=f"{uuid.uuid4().hex}",
            # worker_runtime_env={
            #     "env_vars": {"PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"}
            # },
        ),
    )
    result = trainer.fit()
