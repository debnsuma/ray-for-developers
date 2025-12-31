"""
Ray Train with PyTorch FSDP2 (Low-Level API)

This example follows the official Ray documentation pattern for FSDP2:
https://docs.ray.io/en/latest/train/examples/pytorch/pytorch-fsdp/

Key differences from train_ray_fsdp.py:
1. Uses low-level FSDP2 API with fully_shard() instead of prepare_model()
2. Explicit device mesh configuration
3. Configurable sharding strategies (CPU offload, mixed precision, reshard after forward)
4. Selective layer sharding (only encoder blocks)
5. FSDP-aware checkpoint utilities
6. PyTorch profiler integration for memory analysis

Model: VisionTransformer (SAME as train_ray_fsdp.py)
Dataset: CIFAR-10 (SAME as train_ray_fsdp.py)
Strategy: FSDP2 with explicit configuration
"""

import os
# Enable Ray Train V2 API for better FSDP support
os.environ["RAY_TRAIN_V2_ENABLED"] = "1"

import tempfile
import uuid
import logging
from typing import Dict
import argparse
from datetime import datetime

import torch
import torch.profiler
from torch.nn import CrossEntropyLoss
from torch.optim import AdamW
from torch.utils.data import DataLoader

from torchvision import datasets, transforms
from torchvision.models import VisionTransformer
from torchvision.transforms import ToTensor, Normalize

# PyTorch FSDP2 imports (low-level API)
from torch.distributed.fsdp import (
    fully_shard,
    FSDPModule,
    CPUOffloadPolicy,
    MixedPrecisionPolicy,
)
from torch.distributed.device_mesh import init_device_mesh
from torch.distributed.checkpoint.state_dict import (
    get_state_dict,
    set_state_dict,
    StateDictOptions,
)

# Ray imports
import ray
import ray.train
import ray.train.torch
from ray.train import RunConfig, ScalingConfig, CheckpointConfig
from ray.train.torch import TorchTrainer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Model Initialization
# ============================================================================

def init_model() -> torch.nn.Module:
    """
    Initialize a Vision Transformer model for CIFAR-10 classification.

    Same configuration as train_ray_fsdp.py for consistency.
    """
    logger.info("Initializing Vision Transformer model for CIFAR-10...")

    model = VisionTransformer(
        image_size=32,          # CIFAR-10 is 32x32
        patch_size=4,           # 32/4 = 8 patches per dimension
        num_layers=12,          # 12 transformer layers
        num_heads=8,            # 8 attention heads
        hidden_dim=384,         # Hidden dimension
        mlp_dim=768,            # MLP dimension
        num_classes=10,         # 10 classes in CIFAR-10
    )

    return model


# ============================================================================
# FSDP2 Sharding Configuration
# ============================================================================

def shard_model(
    model: torch.nn.Module,
    cpu_offload: bool = False,
    mixed_precision: bool = False,
    reshard_after_forward: bool = True,
) -> FSDPModule:
    """
    Apply FSDP2 sharding to the model with configurable strategies.

    This follows the Ray documentation pattern with explicit FSDP configuration.

    Args:
        model: The model to shard
        cpu_offload: If True, offload parameters to CPU (saves GPU memory)
        mixed_precision: If True, use mixed precision (reduces memory)
        reshard_after_forward: If True, free all-gathered weights after forward pass

    Returns:
        FSDP-wrapped model
    """
    logger.info("Applying FSDP2 sharding to model...")
    logger.info(f"  CPU Offload: {cpu_offload}")
    logger.info(f"  Mixed Precision: {mixed_precision}")
    logger.info(f"  Reshard After Forward: {reshard_after_forward}")

    # Get world size and create device mesh
    world_size = ray.train.get_context().get_world_size()
    mesh = init_device_mesh("cuda", (world_size,))
    logger.info(f"  Device mesh initialized with world_size={world_size}")

    # Configure CPU offloading
    offload_policy = None
    if cpu_offload:
        offload_policy = CPUOffloadPolicy(offload_params=True)
        logger.info("  CPU offload enabled for parameters")

    # Configure mixed precision
    mp_policy = None
    if mixed_precision:
        mp_policy = MixedPrecisionPolicy()
        logger.info("  Mixed precision enabled")

    # Strategy 1: Shard only the encoder blocks (selective sharding)
    # This is the Ray docs recommended approach for Vision Transformer
    logger.info("  Sharding encoder blocks selectively...")

    for block in model.encoder.layers:
        fully_shard(
            block,
            mesh=mesh,
            reshard_after_forward=reshard_after_forward,
            offload_policy=offload_policy,
            mp_policy=mp_policy,
        )

    # Strategy 2: Shard the entire model
    # This wraps the whole model in FSDP
    model = fully_shard(
        model,
        mesh=mesh,
        reshard_after_forward=reshard_after_forward,
        offload_policy=offload_policy,
        mp_policy=mp_policy,
    )

    logger.info("  FSDP2 sharding complete!")
    return model


# ============================================================================
# Checkpoint Utilities (FSDP-aware)
# ============================================================================

def save_fsdp_checkpoint(
    model: FSDPModule,
    optimizer: torch.optim.Optimizer,
    metrics: Dict,
) -> None:
    """
    Save FSDP checkpoint using Ray Train.

    Uses FSDP-aware state dict extraction for proper distributed checkpointing.
    """
    world_rank = ray.train.get_context().get_world_rank()

    if world_rank == 0:
        logger.info("Saving FSDP checkpoint...")

    with tempfile.TemporaryDirectory() as temp_checkpoint_dir:
        # Use FSDP-aware state dict extraction
        # This handles sharded parameters correctly
        model_state_dict, optimizer_state_dict = get_state_dict(
            model,
            optimizer,
            options=StateDictOptions(
                full_state_dict=True,  # Gather full state dict on rank 0
                cpu_offload=True,      # Offload to CPU to save GPU memory
            ),
        )

        # Only rank 0 saves the checkpoint
        if world_rank == 0:
            checkpoint_path = os.path.join(temp_checkpoint_dir, "checkpoint.pt")
            torch.save(
                {
                    "model": model_state_dict,
                    "optimizer": optimizer_state_dict,
                    "metrics": metrics,
                },
                checkpoint_path,
            )

        # Report to Ray Train
        checkpoint = ray.train.Checkpoint.from_directory(temp_checkpoint_dir)
        ray.train.report(metrics, checkpoint=checkpoint)


def load_fsdp_checkpoint(
    model: FSDPModule,
    optimizer: torch.optim.Optimizer,
    checkpoint: ray.train.Checkpoint,
) -> Dict:
    """
    Load FSDP checkpoint using Ray Train.

    Uses FSDP-aware state dict loading for proper distributed checkpoint restoration.
    """
    logger.info("Loading FSDP checkpoint...")

    with checkpoint.as_directory() as checkpoint_dir:
        checkpoint_path = os.path.join(checkpoint_dir, "checkpoint.pt")
        checkpoint_data = torch.load(checkpoint_path)

        # Use FSDP-aware state dict loading
        set_state_dict(
            model,
            optimizer,
            model_state_dict=checkpoint_data["model"],
            optim_state_dict=checkpoint_data["optimizer"],
            options=StateDictOptions(
                strict=True,
            ),
        )

        logger.info("FSDP checkpoint loaded successfully!")
        return checkpoint_data.get("metrics", {})


# ============================================================================
# Training Function
# ============================================================================

def train_func(config: Dict):
    """
    Main training function integrating FSDP2 with Ray Train.

    This follows the official Ray documentation pattern with:
    - Explicit device management
    - Low-level FSDP2 API
    - Memory profiling
    - FSDP-aware checkpointing
    """
    # Get Ray Train context
    world_rank = ray.train.get_context().get_world_rank()
    world_size = ray.train.get_context().get_world_size()

    if world_rank == 0:
        logger.info("="*60)
        logger.info("Ray Train FSDP2 Training (Following Official Docs Pattern)")
        logger.info("="*60)
        logger.info(f"World Size: {world_size}")
        logger.info(f"Batch Size per Worker: {config['batch_size']}")
        logger.info(f"Global Batch Size: {config['batch_size'] * world_size}")
        logger.info(f"Epochs: {config['epochs']}")
        logger.info(f"Learning Rate: {config['learning_rate']}")
        logger.info("="*60)

    # Step 1: Initialize model
    if world_rank == 0:
        logger.info("[Step 1/6] Initializing model...")
    model = init_model()

    # Step 2: Move to GPU using Ray Train's device management
    if world_rank == 0:
        logger.info("[Step 2/6] Moving model to GPU...")
    device = ray.train.torch.get_device()
    torch.cuda.set_device(device)
    model.to(device)

    # Step 3: Apply FSDP2 sharding
    if world_rank == 0:
        logger.info("[Step 3/6] Applying FSDP2 sharding...")
    model = shard_model(
        model,
        cpu_offload=config.get("cpu_offload", False),
        mixed_precision=config.get("mixed_precision", False),
        reshard_after_forward=config.get("reshard_after_forward", True),
    )

    # Step 4: Create optimizer and loss
    if world_rank == 0:
        logger.info("[Step 4/6] Creating optimizer and loss function...")
    optimizer = AdamW(model.parameters(), lr=config["learning_rate"], weight_decay=1e-2)
    criterion = CrossEntropyLoss()

    # Step 5: Load checkpoint if resuming
    if world_rank == 0:
        logger.info("[Step 5/6] Checking for checkpoint to resume...")
    loaded_checkpoint = ray.train.get_checkpoint()
    if loaded_checkpoint:
        load_fsdp_checkpoint(model, optimizer, loaded_checkpoint)

    # Step 6: Prepare data
    if world_rank == 0:
        logger.info("[Step 6/6] Preparing data loaders...")

    transform = transforms.Compose([
        ToTensor(),
        Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))  # 3 channels for RGB
    ])

    # Download data (use ~/data directory like train_ray_fsdp.py)
    from filelock import FileLock

    data_dir = os.path.expanduser("~/data")

    # Download only on rank 0 to avoid conflicts
    with FileLock(os.path.expanduser("~/data.lock")):
        if world_rank == 0:
            datasets.CIFAR10(root=data_dir, train=True, download=True)

    train_data = datasets.CIFAR10(
        root=data_dir,
        train=True,
        download=False,
        transform=transform,
    )

    train_loader = DataLoader(
        train_data,
        batch_size=config["batch_size"],
        shuffle=True,
    )

    # Prepare data loader for distributed training
    train_loader = ray.train.torch.prepare_data_loader(train_loader)

    if world_rank == 0:
        logger.info("Starting training loop...")
        logger.info("="*60)

    # Training loop with profiler
    with torch.profiler.profile(
        activities=[
            torch.profiler.ProfilerActivity.CPU,
            torch.profiler.ProfilerActivity.CUDA,
        ],
        schedule=torch.profiler.schedule(
            wait=0,
            warmup=0,
            active=6,
            repeat=1
        ),
        record_shapes=True,
        profile_memory=True,
        with_stack=True,
    ) as prof:

        for epoch in range(config["epochs"]):
            if world_rank == 0:
                logger.info(f"\nEpoch {epoch + 1}/{config['epochs']}")
                logger.info("-" * 40)

            # Set epoch for distributed sampler
            if world_size > 1:
                train_loader.sampler.set_epoch(epoch)

            # Training phase
            model.train()
            running_loss = 0.0
            num_batches = 0

            for batch_idx, (images, labels) in enumerate(train_loader):
                # Forward pass
                outputs = model(images)
                loss = criterion(outputs, labels)

                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                # Profile step
                prof.step()

                # Accumulate metrics
                running_loss += loss.item()
                num_batches += 1

                # Log progress
                if world_rank == 0 and batch_idx % 100 == 0:
                    logger.info(f"  Batch {batch_idx}/{len(train_loader)}, Loss: {loss.item():.4f}")

            # Compute average loss
            avg_loss = running_loss / num_batches

            # Prepare metrics
            metrics = {
                "epoch": epoch + 1,
                "loss": avg_loss,
            }

            if world_rank == 0:
                logger.info(f"\nEpoch {epoch + 1} Results:")
                logger.info(f"  Average Loss: {avg_loss:.4f}")

            # Save checkpoint every N epochs
            if (epoch + 1) % config.get("checkpoint_frequency", 5) == 0:
                save_fsdp_checkpoint(model, optimizer, metrics)
            else:
                ray.train.report(metrics)

    # Export memory timeline
    if world_rank == 0:
        logger.info("\nExporting memory profiler timeline...")

    run_name = ray.train.get_context().get_experiment_name()
    profile_dir = config.get("profile_dir", "/tmp")
    os.makedirs(profile_dir, exist_ok=True)

    profile_path = os.path.join(
        profile_dir,
        f"{run_name}_rank{world_rank}_memory_profile.html"
    )
    prof.export_memory_timeline(profile_path)

    if world_rank == 0:
        logger.info(f"Memory profile saved to: {profile_path}")
        logger.info("="*60)
        logger.info("Training completed!")
        logger.info("="*60)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Ray Train FSDP2 on CIFAR-10 (Official Docs Pattern with Advanced Configuration)'
    )
    parser.add_argument('--epochs', type=int, default=5,
                        help='number of epochs (default: 5)')
    parser.add_argument('--batch-size', type=int, default=64,
                        help='batch size per worker (default: 64)')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='learning rate (default: 0.001)')
    parser.add_argument('--num-workers', type=int, default=None,
                        help='number of workers (default: num GPUs)')
    parser.add_argument('--cpu-offload', action='store_true',
                        help='enable CPU offload (reduces GPU memory)')
    parser.add_argument('--mixed-precision', action='store_true',
                        help='enable mixed precision (reduces memory)')
    parser.add_argument('--no-reshard', dest='reshard_after_forward',
                        action='store_false', default=True,
                        help='disable reshard after forward (increases memory)')
    parser.add_argument('--checkpoint-freq', type=int, default=5,
                        help='checkpoint frequency in epochs (default: 5)')
    parser.add_argument('--profile-dir', type=str, default="/tmp",
                        help='directory to save profiler output (default: /tmp)')
    args = parser.parse_args()

    # Initialize Ray
    if not ray.is_initialized():
        ray.init()

    # Determine number of workers
    if args.num_workers is None:
        args.num_workers = torch.cuda.device_count()
        if args.num_workers == 0:
            print("WARNING: No GPUs detected, using 2 CPU workers")
            args.num_workers = 2

    print(f"\n{'='*60}")
    print(f"Ray Train FSDP2 Configuration (Official Docs Pattern)")
    print(f"{'='*60}")
    print(f"Ray version: {ray.__version__}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Dataset: CIFAR-10 (32x32 RGB)")
    print(f"Model: VisionTransformer (same as train_ray_fsdp.py)")
    print(f"Number of workers: {args.num_workers}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size per worker: {args.batch_size}")
    print(f"Global batch size: {args.batch_size * args.num_workers}")
    print(f"Learning rate: {args.lr}")
    print(f"\nFSDP2 Configuration:")
    print(f"  CPU Offload: {args.cpu_offload}")
    print(f"  Mixed Precision: {args.mixed_precision}")
    print(f"  Reshard After Forward: {args.reshard_after_forward}")
    print(f"  Checkpoint Frequency: every {args.checkpoint_freq} epochs")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Training configuration
    train_config = {
        "learning_rate": args.lr,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "cpu_offload": args.cpu_offload,
        "mixed_precision": args.mixed_precision,
        "reshard_after_forward": args.reshard_after_forward,
        "checkpoint_frequency": args.checkpoint_freq,
        "profile_dir": args.profile_dir,
    }

    # Scaling configuration
    scaling_config = ScalingConfig(
        num_workers=args.num_workers,
        use_gpu=True,
        resources_per_worker={
            "CPU": 2,
            "GPU": 1,
        }
    )

    # Checkpoint configuration
    checkpoint_config = CheckpointConfig(
        num_to_keep=2,
        checkpoint_score_attribute="loss",
        checkpoint_score_order="min",  # Keep checkpoints with lowest loss
    )

    # Run configuration
    run_config = RunConfig(
        name=f"cifar10_fsdp2_{uuid.uuid4().hex[:8]}",
        storage_path="/mnt/cluster_storage",
        checkpoint_config=checkpoint_config,
    )

    # Create TorchTrainer
    trainer = TorchTrainer(
        train_loop_per_worker=train_func,
        train_loop_config=train_config,
        scaling_config=scaling_config,
        run_config=run_config,
    )

    # Start training
    print("Starting FSDP2 training...\n")
    start_time = datetime.now()

    result = trainer.fit()

    end_time = datetime.now()
    duration = end_time - start_time

    # Print results
    print(f"\n{'='*60}")
    print(f"Training Results")
    print(f"{'='*60}")
    print(f"Final metrics: {result.metrics}")
    if result.checkpoint:
        print(f"Best checkpoint: {result.checkpoint.path}")
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {duration}")
    print(f"{'='*60}\n")

    # Shutdown Ray
    ray.shutdown()


if __name__ == '__main__':
    main()
