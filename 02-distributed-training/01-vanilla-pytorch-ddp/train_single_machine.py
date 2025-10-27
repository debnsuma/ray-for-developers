"""
Single Machine PyTorch Training (Baseline)

This is your starting point - a simple, single-GPU training script.
This serves as the baseline to compare against distributed approaches.

Model: VisionTransformer
Dataset: CIFAR-10
Hardware: Single GPU/MPS (or CPU)

This example shows standard PyTorch training without any distributed code.
"""

from typing import Any


import os
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


def get_dataloaders(batch_size):
    """
    Create standard PyTorch DataLoaders.
    This is vanilla PyTorch - no distributed code here.
    """
    # Transform to normalize the input images
    transform = transforms.Compose([
        ToTensor(),
        Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    with FileLock(os.path.expanduser("~/data.lock")):
        # Download training data from open datasets
        training_data = datasets.CIFAR10(
            root="~/data",
            train=True,
            download=True,
            transform=transform,
        )

        # Download test data from open datasets
        testing_data = datasets.CIFAR10(
            root="~/data",
            train=False,
            download=True,
            transform=transform,
        )

    # Create data loaders (standard PyTorch)
    train_dataloader = DataLoader(training_data, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(testing_data, batch_size=batch_size)

    return train_dataloader, test_dataloader


def train_func(lr=1e-3, epochs=10, batch_size=512):
    """
    Main training function - single machine, standard PyTorch.
    """
    print(f"\n{'='*60}")
    print(f"Single Machine PyTorch Training")
    print(f"{'='*60}")
    print(f"Epochs: {epochs}")
    print(f"Batch Size: {batch_size}")
    print(f"Learning Rate: {lr}")
    print(f"{'='*60}\n")

    # Get data loaders
    train_dataloader, valid_dataloader = get_dataloaders(batch_size=batch_size)

    # Create model
    model = VisionTransformer(
        image_size=32,   # CIFAR-10 image size is 32x32
        patch_size=4,    # Patch size is 4x4
        num_layers=12,   # Number of transformer layers
        num_heads=8,     # Number of attention heads
        hidden_dim=384,  # Hidden size
        mlp_dim=768,     # MLP dimension
        num_classes=10   # CIFAR-10 has 10 classes
    )

    # Move to GPU if available (CUDA or MPS)
    device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}\n")
    model.to(device)

    # Create loss and optimizer
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)

    # Training loop
    for epoch in range(epochs):
        print(f"\nEpoch {epoch + 1}/{epochs}")
        print("-" * 40)

        # Training phase
        model.train()
        train_loss = 0.0
        for X, y in tqdm(train_dataloader, desc=f"Train Epoch {epoch + 1}"):
            X, y = X.to(device), y.to(device)
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
            for X, y in tqdm(valid_dataloader, desc=f"Valid Epoch {epoch + 1}"):
                X, y = X.to(device), y.to(device)
                pred = model(X)
                loss = loss_fn(pred, y)

                valid_loss += loss.item()
                num_total += y.shape[0]
                num_correct += (pred.argmax(1) == y).sum().item()

        valid_loss /= len(valid_dataloader)
        accuracy = num_correct / num_total

        print(f"\nResults:")
        print(f"  Train Loss: {train_loss:.4f}")
        print(f"  Valid Loss: {valid_loss:.4f}")
        print(f"  Accuracy: {accuracy:.4f} ({100 * accuracy:.2f}%)")

    # Save checkpoint
    checkpoint = {
        'epoch': epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'accuracy': accuracy,
    }
    torch.save(checkpoint, 'checkpoint_single_machine.pth')
    print(f"\n{'='*60}")
    print(f"Training completed!")
    print(f"Final accuracy: {100 * accuracy:.2f}%")
    print(f"Checkpoint saved to checkpoint_single_machine.pth")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Single Machine PyTorch Training on CIFAR-10')
    parser.add_argument('--epochs', type=int, default=1, help='number of epochs')
    parser.add_argument('--batch-size', type=int, default=512, help='batch size')
    parser.add_argument('--lr', type=float, default=1e-3, help='learning rate')
    args = parser.parse_args()

    start_time = datetime.now()
    print(f"\nStarted at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    train_func(lr=args.lr, epochs=args.epochs, batch_size=args.batch_size)

    end_time = datetime.now()
    duration = end_time - start_time
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {duration}\n")
