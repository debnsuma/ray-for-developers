import os

os.environ["RAY_TRAIN_V2_ENABLED"] = "1"

import uuid
import torch
import ray.train.torch
from torch.distributed.fsdp import ShardingStrategy
from torchvision.models import VisionTransformer
from torch.optim.adam import Adam
from torch.nn import CrossEntropyLoss
import argparse


def build_visual_transformer(hidden_dim: int) -> VisionTransformer:
    return VisionTransformer(
        image_size=32,
        patch_size=4,
        num_layers=12,
        num_heads=8,
        hidden_dim=hidden_dim,
        mlp_dim=768,
        num_classes=10,
    )


def train_func(config):
    device = ray.train.torch.get_device()

    # Determine world size and rank
    world_size = ray.train.get_context().get_world_size()
    world_rank = ray.train.get_context().get_world_rank()

    # Build model and wrap with DDP or FSDP if needed
    model = build_visual_transformer(config.get("hidden_dim", 1920))

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")

    # Estimate size in float32 (4 bytes/param)
    size_bytes_fp32 = total_params * 4
    size_gb_fp32 = size_bytes_fp32 / (1024**3)
    print(f"Model size (float32): {size_gb_fp32:.4f} GB")

    if world_size > 1:
        fsdp_kwargs = config.get("fsdp_kwargs", {})
        model = ray.train.torch.prepare_model(
            model.to(device),
            parallel_strategy=config["distribution_strategy"],
            parallel_strategy_kwargs=fsdp_kwargs
        )
    else:
        model = model.to(device)

    optimizer = Adam(model.parameters(), lr=0.001)
    # Setup dummy input and labels for loss computation
    dummy = torch.randn(config["batch_size"] // world_size, 3, 32, 32, device=device)
    criterion = CrossEntropyLoss()
    labels = torch.randint(0, 10, (config["batch_size"] // world_size,), device=device)

    # Set up profiler to capture profile data
    log_dir = config["log_dir"]
    with torch.profiler.profile(
        schedule=torch.profiler.schedule(wait=1, warmup=1, active=3),
        on_trace_ready=torch.profiler.tensorboard_trace_handler(
            log_dir,
            worker_name=f"rank={world_rank}",
        ),
        record_shapes=True,
        profile_memory=True,
        with_stack=True,
    ) as prof:
        for _ in range(5):
            out = model(dummy)
            loss = criterion(out, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            prof.step()

    # Export memory timeline
    timeline_path = os.path.join(log_dir, f"memory_timeline_{world_rank}.html")
    prof.export_memory_timeline(timeline_path)
    print(f"Memory timeline exported to {timeline_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_workers", type=int, default=2)
    parser.add_argument("--distribution_strategy", choices=["ddp","fsdp"], default="fsdp")
    parser.add_argument("--hidden_dim", type=int, default=1920)
    args = parser.parse_args()

    num_workers = args.num_workers
    distribution_strategy = args.distribution_strategy
    hidden_dim = args.hidden_dim
    fsdp_kwargs = {"sharding_strategy": ShardingStrategy.FULL_SHARD} if distribution_strategy == "fsdp" else {}

    trainer = ray.train.torch.TorchTrainer(
        train_func,
        train_loop_config={
            "distribution_strategy": distribution_strategy,
            "fsdp_kwargs": fsdp_kwargs,
            "batch_size": 32,
            "hidden_dim": hidden_dim,
            "log_dir": f"/mnt/cluster_storage/profiler_logs/{distribution_strategy=}/{num_workers=}",
        },
        scaling_config=ray.train.ScalingConfig(
            num_workers=num_workers,
            resources_per_worker={"accelerator_type:T4": 0.001},
            use_gpu=True,
        ),
        run_config=ray.train.RunConfig(
            storage_path=f"/mnt/cluster_storage/exp/{distribution_strategy=}/{num_workers=}",
            name=f"{uuid.uuid4().hex}",
        ),
    )
    result = trainer.fit()
