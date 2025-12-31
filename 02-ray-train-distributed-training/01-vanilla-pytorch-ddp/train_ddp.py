"""
Vanilla PyTorch Distributed Data Parallel (DDP) Training

This example shows the traditional way of doing distributed training with PyTorch DDP.
Compare this to train_ray_ddp.py to see how Ray Train eliminates the boilerplate.

Model: VisionTransformer
Dataset: CIFAR-10 (SAME as Ray Train example)
Strategy: Data Parallel

Notice all the manual boilerplate (marked with BOILERPLATE #1-8):
- Manual process spawning
- Manual distributed setup/cleanup
- Manual DistributedSampler
- Must remember to call sampler.set_epoch() every epoch
- No fault tolerance
- Complex error handling

Simplified version following official PyTorch DDP tutorial patterns.
This is ~330 lines vs ~250 lines for Ray Train (doing the EXACT same thing!)
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
from torchvision import datasets, transforms
from torchvision.transforms import Normalize, ToTensor
from torchvision.models import VisionTransformer
from tqdm import tqdm
from filelock import FileLock
import argparse
from datetime import datetime


# ============================================================================
# DISTRIBUTED SETUP (BOILERPLATE #1 & #2)
# ============================================================================

def setup_distributed(rank, world_size, backend='nccl'):
    """
    BOILERPLATE #1: Manual distributed process group initialization.

    You must:
    - Set environment variables (MASTER_ADDR, MASTER_PORT)
    - Choose the right backend (nccl for GPU, gloo for CPU)
    - Handle rank and world_size coordination
    - Initialize process group on each rank

    Ray Train: Automatic (ray.init() handles everything)
    """
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'

    # Initialize process group
    dist.init_process_group(backend, rank=rank, world_size=world_size)

    if rank == 0:
        print(f"Process group initialized with {world_size} workers")


def cleanup_distributed():
    """
    BOILERPLATE #2: Manual cleanup of distributed process group.

    Forget this and your processes will hang forever!

    Ray Train: Automatic cleanup
    """
    dist.destroy_process_group()


# ============================================================================
# DATA LOADING (BOILERPLATE #3)
# ============================================================================

def get_dataloaders(rank, world_size, batch_size):
    """
    BOILERPLATE #3: Manual DistributedSampler creation.

    You must:
    - Create DistributedSampler with correct rank and world_size
    - Pass sampler to DataLoader (can't use shuffle=True!)
    - Remember to call sampler.set_epoch(epoch) every epoch
    - Download data only on rank 0 to avoid conflicts
    - Use barrier to sync all ranks after download

    Ray Train: train.torch.prepare_data_loader() does this automatically
    """
    # Transform (same as Ray Train version)
    transform = transforms.Compose([
        ToTensor(),
        Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # Download only on rank 0 to avoid conflicts
    with FileLock(os.path.expanduser("~/data.lock")):
        if rank == 0:
            datasets.CIFAR10(root="~/data", train=True, download=True)
            datasets.CIFAR10(root="~/data", train=False, download=True)

    # Barrier to ensure download completes before other ranks access
    dist.barrier()

    # Load datasets
    training_data = datasets.CIFAR10(
        root="~/data",
        train=True,
        download=False,
        transform=transform,
    )

    testing_data = datasets.CIFAR10(
        root="~/data",
        train=False,
        download=False,
        transform=transform,
    )

    # CRITICAL: Must use DistributedSampler to partition data
    train_sampler = DistributedSampler(
        training_data,
        num_replicas=world_size,
        rank=rank,
        shuffle=True,
        seed=42
    )

    test_sampler = DistributedSampler(
        testing_data,
        num_replicas=world_size,
        rank=rank,
        shuffle=False
    )

    # Create data loaders (can't use shuffle=True, must use sampler!)
    train_dataloader = DataLoader(
        training_data,
        batch_size=batch_size,
        sampler=train_sampler,  # Must use sampler, not shuffle
        num_workers=2,
        pin_memory=True
    )

    test_dataloader = DataLoader(
        testing_data,
        batch_size=batch_size,
        sampler=test_sampler,
        num_workers=2,
        pin_memory=True
    )

    return train_dataloader, test_dataloader, train_sampler


# ============================================================================
# TRAINING FUNCTIONS (SAME AS Ray Train!)
# ============================================================================

def train_epoch(model, train_loader, criterion, optimizer, rank):
    """Train for one epoch - this part is identical to Ray Train!"""
    model.train()
    running_loss = 0.0

    for X, y in tqdm(train_loader, desc=f"Train", disable=rank != 0):
        X, y = X.cuda(rank), y.cuda(rank)

        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        # Comment clarification:
        # After loss.backward(), DDP synchronizes/averages gradients across all workers automatically,
        # and then optimizer.step() updates the weights on each process identically.
        optimizer.step()

        running_loss += loss.item()

    return running_loss / len(train_loader)


def validate(model, valid_loader, criterion, rank):
    """
    Validate the model on this process's data partition.

    Following official PyTorch DDP tutorial - no need for all_reduce() in validation.
    Each process computes metrics on its own data partition. This is sufficient
    for monitoring training progress.

    """
    model.eval()
    running_loss = 0.0
    num_correct = 0
    num_total = 0

    with torch.no_grad():
        for X, y in tqdm(valid_loader, desc=f"Valid", disable=rank != 0):
            X, y = X.cuda(rank), y.cuda(rank)
            outputs = model(X)
            loss = criterion(outputs, y)

            running_loss += loss.item()
            num_total += y.shape[0]
            num_correct += (outputs.argmax(1) == y).sum().item()

    # Compute local metrics 
    avg_loss = running_loss / len(valid_loader)
    accuracy = num_correct / num_total if num_total > 0 else 0.0

    return avg_loss, accuracy


# ============================================================================
# MAIN TRAINING WORKER (BOILERPLATE #4-7)
# ============================================================================

def train_worker(rank, world_size, args):
    """
    BOILERPLATE #4: Training function that runs on each process.

    You must:
    - Handle entire lifecycle: setup → train → cleanup
    - Manage errors on each rank independently
    - Ensure cleanup happens even on failure
    - Coordinate all ranks carefully

    Ray Train: Just write train_func_per_worker(), Ray handles lifecycle
    """
    try:
        # BOILERPLATE #1: Initialize distributed process group
        setup_distributed(rank, world_size, backend='nccl')

        if rank == 0:
            print(f"\n{'='*60}")
            print(f"Vanilla PyTorch DDP Training")
            print(f"{'='*60}")
            print(f"World Size: {world_size}")
            print(f"Batch Size per GPU: {args.batch_size}")
            print(f"Global Batch Size: {args.batch_size * world_size}")
            print(f"Epochs: {args.epochs}")
            print(f"Learning Rate: {args.lr}")
            print(f"{'='*60}\n")

        # Set device for this process
        torch.cuda.set_device(rank)

        # Create model (same as Ray Train)
        model = VisionTransformer(
            image_size=32,
            patch_size=4,
            num_layers=12,
            num_heads=8,
            hidden_dim=384,
            mlp_dim=768,
            num_classes=10
        )

        # BOILERPLATE #5: Manual DDP wrapping
        # Move to GPU then wrap with DDP
        model = model.cuda(rank)
        model = DDP(model, device_ids=[rank])

        # Create optimizer and loss (same as Ray Train)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-2)

        # BOILERPLATE #3: Get data loaders with manual DistributedSampler
        train_loader, valid_loader, train_sampler = get_dataloaders(
            rank, world_size, args.batch_size
        )

        # Training loop
        for epoch in range(1, args.epochs + 1):
            # BOILERPLATE #6: Must manually set epoch for proper shuffling
            # Forget this and your shuffling breaks!
            train_sampler.set_epoch(epoch)

            if rank == 0:
                print(f"\nEpoch {epoch}/{args.epochs}")
                print("-" * 40)

            # Train (this part is identical to Ray Train!)
            train_loss = train_epoch(model, train_loader, criterion, optimizer, rank)

            # Validate (simple local metrics, no all_reduce needed)
            valid_loss, accuracy = validate(model, valid_loader, criterion, rank)

            if rank == 0:
                print(f"\nResults:")
                print(f"  Train Loss: {train_loss:.4f}")
                print(f"  Valid Loss: {valid_loss:.4f}")
                print(f"  Accuracy: {accuracy:.4f} ({100 * accuracy:.2f}%)")

        # Save checkpoint (only rank 0)
        if rank == 0:
            checkpoint = {
                'epoch': args.epochs,
                'model_state_dict': model.module.state_dict(),  # .module to unwrap DDP
                'optimizer_state_dict': optimizer.state_dict(),
                'accuracy': accuracy,
            }
            torch.save(checkpoint, 'checkpoint_ddp.pth')

            print(f"\n{'='*60}")
            print(f"Training completed!")
            print(f"Final accuracy: {100 * accuracy:.2f}%")
            print(f"Checkpoint saved to checkpoint_ddp.pth")
            print(f"{'='*60}\n")

    except Exception as e:
        print(f"[Rank {rank}] Error during training: {e}")
        raise

    finally:
        # BOILERPLATE #7: Must manually clean up or processes hang
        cleanup_distributed()


# ============================================================================
# MAIN ENTRY POINT (BOILERPLATE #8)
# ============================================================================

def main():
    """
    BOILERPLATE #8: Manual process spawning with mp.spawn().

    You must:
    - Spawn one process per GPU manually
    - Pass all arguments through args tuple
    - Handle process coordination
    - Wait for all processes to complete

    Ray Train: Just call trainer.fit()
    """
    parser = argparse.ArgumentParser(description='Vanilla PyTorch DDP on CIFAR-10')
    parser.add_argument('--epochs', type=int, default=1, help='number of epochs')
    parser.add_argument('--batch-size', type=int, default=128,
                       help='batch size per GPU')
    parser.add_argument('--lr', type=float, default=1e-3, help='learning rate')
    parser.add_argument('--world-size', type=int, default=None,
                       help='number of processes (default: num GPUs)')
    args = parser.parse_args()

    # Determine world size
    if args.world_size is None:
        args.world_size = torch.cuda.device_count()

    if args.world_size == 0:
        print("ERROR: No CUDA devices found. This example requires GPUs.")
        print("For CPU training, use the single machine version.")
        return

    print(f"\n{'='*60}")
    print(f"Vanilla PyTorch DDP")
    print(f"{'='*60}")
    print(f"Detected {torch.cuda.device_count()} GPU(s)")
    print(f"Will spawn {args.world_size} processes")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    start_time = datetime.now()

    # BOILERPLATE #8: Manual process spawning
    # This creates a separate Python process for each GPU
    mp.spawn(
        train_worker,
        args=(args.world_size, args),
        nprocs=args.world_size,
        join=True  # Wait for all processes to complete
    )

    end_time = datetime.now()
    duration = end_time - start_time

    print(f"\n{'='*60}")
    print(f"All processes completed")
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {duration}")
    print(f"{'='*60}\n")

    print("\n" + "="*60)
    print("COMPARISON: What Ray Train saves you")
    print("="*60)
    print("This vanilla DDP code: ~330 lines")
    print("Ray Train equivalent: ~250 lines (24% less!)")
    print()
    print("Manual boilerplate steps in this code:")
    print("  #1: setup_distributed() - Manual process group init")
    print("  #2: cleanup_distributed() - Manual cleanup")
    print("  #3: DistributedSampler - Manual data partitioning")
    print("  #4: train_worker() - Manual lifecycle management")
    print("  #5: DDP() wrapping - Manual model wrapping")
    print("  #6: sampler.set_epoch() - Manual epoch setting")
    print("  #7: finally cleanup - Manual error handling")
    print("  #8: mp.spawn() - Manual process spawning")
    print()
    print("Ray Train equivalent:")
    print("  [1] train.torch.prepare_data_loader()")
    print("  [2] train.torch.prepare_model()")
    print("  [3] train.report()")
    print()
    print("8 manual steps → 3 automatic calls")
    print("That's why you should use Ray Train! 🚀")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
