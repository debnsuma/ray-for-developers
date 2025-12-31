"""
Ray Train with PyTorch FSDP (Fully Sharded Data Parallel)

This example shows how easy it is to switch from DDP to FSDP with Ray Train.
The ONLY difference from train_ray_ddp.py is ONE PARAMETER in prepare_model()!

What is FSDP?
=============
- DDP: Each GPU has a FULL copy of the model (memory scales with model size)
- FSDP: Model parameters are SHARDED across GPUs (memory scales with model size / num_GPUs)

When to use FSDP:
- Model is too large to fit on a single GPU
- Training billion+ parameter models
- Want to maximize memory efficiency

Model: VisionTransformer (same as DDP example)
Dataset: CIFAR-10 (same as DDP example)
Strategy: Fully Sharded Data Parallel (FSDP)

Key Change (marked with [FSDP] in code):
- Add parallel_strategy="fsdp" to prepare_model() - that's it!
"""

import os
import tempfile
import uuid
from typing import Dict

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.transforms import Normalize, ToTensor
from torchvision.models import VisionTransformer
from tqdm import tqdm
from filelock import FileLock
import argparse
from datetime import datetime

# Ray imports
import ray
import ray.train
from ray.train import RunConfig, ScalingConfig, CheckpointConfig
from ray.train.torch import TorchTrainer


def get_dataloaders(batch_size):
    """
    Create standard PyTorch DataLoaders.
    IDENTICAL to DDP version.
    """
    transform = transforms.Compose([
        ToTensor(),
        Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    with FileLock(os.path.expanduser("~/data.lock")):
        training_data = datasets.CIFAR10(
            root="~/data",
            train=True,
            download=True,
            transform=transform,
        )

        testing_data = datasets.CIFAR10(
            root="~/data",
            train=False,
            download=True,
            transform=transform,
        )

    train_dataloader = DataLoader(training_data, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(testing_data, batch_size=batch_size)

    return train_dataloader, test_dataloader


def train_func_per_worker(config: Dict):
    """
    Training function with FSDP.

    This is ALMOST IDENTICAL to the DDP version!
    The only difference is the parallel_strategy parameter.
    """
    lr = config["lr"]
    epochs = config["epochs"]
    batch_size = config["batch_size_per_worker"]

    # Get local rank for logging
    local_rank = ray.train.get_context().get_world_rank()
    world_size = ray.train.get_context().get_world_size()

    if local_rank == 0:
        print(f"\n{'='*60}")
        print(f"Ray Train FSDP Training")
        print(f"{'='*60}")
        print(f"World Size: {world_size}")
        print(f"Batch Size per Worker: {batch_size}")
        print(f"Global Batch Size: {batch_size * world_size}")
        print(f"Epochs: {epochs}")
        print(f"Learning Rate: {lr}")
        print(f"Strategy: FSDP (Fully Sharded Data Parallel)")
        print(f"{'='*60}\n")
        print(f"[Step 1/5] Loading data...")

    # Get data loaders
    train_dataloader, valid_dataloader = get_dataloaders(batch_size=batch_size)

    if local_rank == 0:
        print(f"[Step 2/5] Preparing data loaders for distributed training...")

    # Prepare data loaders for distributed training
    train_dataloader = ray.train.torch.prepare_data_loader(train_dataloader)
    valid_dataloader = ray.train.torch.prepare_data_loader(valid_dataloader)

    if local_rank == 0:
        print(f"[Step 3/5] Creating VisionTransformer model...")

    # Create model (same as DDP)
    model = VisionTransformer(
        image_size=32,
        patch_size=4,
        num_layers=12,
        num_heads=8,
        hidden_dim=384,
        mlp_dim=768,
        num_classes=10
    )

    if local_rank == 0:
        print(f"[Step 4/5] Wrapping model with FSDP (this may take a moment)...")

    # [FSDP] THIS IS THE ONLY CHANGE FROM DDP!
    # =========================================
    # Just add parallel_strategy="fsdp" and Ray handles everything:
    # - Shards model parameters across GPUs
    # - Sets up gradient sharding
    # - Handles all-gather/reduce-scatter operations
    # - Manages optimizer state sharding
    #
    # DDP version:  model = ray.train.torch.prepare_model(model)
    # FSDP version: model = ray.train.torch.prepare_model(model, parallel_strategy="fsdp")
    model = ray.train.torch.prepare_model(model, parallel_strategy="fsdp")

    if local_rank == 0:
        print(f"[Step 5/5] FSDP wrapping complete! Parameters sharded across {world_size} workers.")
        print(f"            Starting training...\n")

    # Create loss and optimizer (same as DDP)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)

    # Training loop (IDENTICAL to DDP!)
    for epoch in range(epochs):
        if local_rank == 0:
            print(f"\nEpoch {epoch + 1}/{epochs}")
            print("-" * 40)

        # Training phase
        model.train()
        train_loss = 0.0
        for X, y in tqdm(train_dataloader, desc=f"Train Epoch {epoch + 1}",
                        disable=local_rank != 0):
            pred = model(X)
            loss = loss_fn(pred, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        train_loss /= len(train_dataloader)

        # Validation phase
        model.eval()
        valid_loss, num_correct, num_total = 0, 0, 0
        with torch.no_grad():
            for X, y in tqdm(valid_dataloader, desc=f"Valid Epoch {epoch + 1}",
                           disable=local_rank != 0):
                pred = model(X)
                loss = loss_fn(pred, y)

                valid_loss += loss.item()
                num_total += y.shape[0]
                num_correct += (pred.argmax(1) == y).sum().item()

        valid_loss /= len(valid_dataloader)
        accuracy = num_correct / num_total

        if local_rank == 0:
            print(f"\nResults:")
            print(f"  Train Loss: {train_loss:.4f}")
            print(f"  Valid Loss: {valid_loss:.4f}")
            print(f"  Accuracy: {accuracy:.4f} ({100 * accuracy:.2f}%)")

        # Report metrics and checkpoints
        metrics = {
            "epoch": epoch + 1,
            "train_loss": train_loss,
            "valid_loss": valid_loss,
            "accuracy": accuracy,
        }

        # Save checkpoint every 5 epochs
        if (epoch + 1) % 5 == 0:
            with tempfile.TemporaryDirectory() as temp_checkpoint_dir:
                # Note: With FSDP, we need to use a different method to save
                # For simplicity, we're saving the full state dict
                # In production, you might want to use FSDP's native checkpointing
                torch.save(
                    model.module.state_dict(),  # .module to unwrap FSDP
                    os.path.join(temp_checkpoint_dir, "model.pt")
                )
                ray.train.report(
                    metrics,
                    checkpoint=ray.train.Checkpoint.from_directory(temp_checkpoint_dir)
                )
        else:
            ray.train.report(metrics)

    if local_rank == 0:
        print(f"\n{'='*60}")
        print(f"Training completed!")
        print(f"Final accuracy: {100 * accuracy:.2f}%")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Ray Train FSDP on CIFAR-10')
    parser.add_argument('--epochs', type=int, default=1, help='number of epochs')
    parser.add_argument('--batch-size', type=int, default=512,
                       help='global batch size (will be divided across workers)')
    parser.add_argument('--lr', type=float, default=1e-3, help='learning rate')
    parser.add_argument('--num-workers', type=int, default=None,
                       help='number of workers (default: num GPUs)')
    parser.add_argument('--no-gpu', dest='use_gpu', action='store_false', default=True,
                       help='disable GPU and use CPU for training')
    args = parser.parse_args()

    # Initialize Ray
    if not ray.is_initialized():
        ray.init()

    # Determine number of workers
    if args.num_workers is None:
        args.num_workers = torch.cuda.device_count() if args.use_gpu else 2
        if args.num_workers == 0:
            print("WARNING: No GPUs detected, using 2 CPU workers")
            args.num_workers = 2
            args.use_gpu = False

    print(f"\n{'='*60}")
    print(f"Ray Train FSDP Configuration")
    print(f"{'='*60}")
    print(f"Ray version: {ray.__version__}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Number of workers: {args.num_workers}")
    if args.use_gpu:
        print(f"Detected {torch.cuda.device_count()} GPU(s)")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"")
    print(f"NOTE: FSDP shards model parameters across {args.num_workers} workers")
    print(f"      Each worker uses ~1/{args.num_workers} of the model memory")
    print(f"{'='*60}\n")

    # Calculate batch size per worker
    global_batch_size = args.batch_size
    batch_size_per_worker = global_batch_size // args.num_workers

    train_config = {
        "lr": args.lr,
        "epochs": args.epochs,
        "batch_size_per_worker": batch_size_per_worker,
    }

    # Configure scaling
    scaling_config = ScalingConfig(
        num_workers=args.num_workers,
        use_gpu=args.use_gpu,
        resources_per_worker={
            "CPU": 2,
            "GPU": 1 if args.use_gpu else 0
        }
    )

    # Configure checkpointing
    checkpoint_config = CheckpointConfig(
        num_to_keep=2,
        checkpoint_score_attribute="accuracy",
        checkpoint_score_order="max"
    )

    # Configure the overall training run
    run_config = RunConfig(
        name=f"cifar10_fsdp_{uuid.uuid4().hex[:8]}",
        # /mnt/cluster_storage is an Anyscale-specific storage path shared across nodes
        # OSS users should use: storage_path=os.path.abspath("./ray_results")
        storage_path="/mnt/cluster_storage",
        checkpoint_config=checkpoint_config,
    )

    # Create TorchTrainer (IDENTICAL to DDP version!)
    trainer = TorchTrainer(
        train_loop_per_worker=train_func_per_worker,
        train_loop_config=train_config,
        scaling_config=scaling_config,
        run_config=run_config,
    )

    # Start training!
    print("Starting FSDP training...\n")
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
