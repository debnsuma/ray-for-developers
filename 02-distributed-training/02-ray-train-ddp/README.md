# 02. Ray Train with PyTorch DDP Backend

## ✅ Use This!

This module shows how **Ray Train dramatically simplifies** distributed training compared to vanilla PyTorch DDP. The training logic is identical to the single-machine version - only the setup changes!

**Key Benefit:** Same performance as vanilla DDP, but with 90% less boilerplate code!

## Quick Comparison

**Single Machine → Ray Train DDP requires just 3 changes:**

1. **Wrap DataLoaders**: `ray.train.torch.prepare_data_loader(loader)`
2. **Wrap Model**: `ray.train.torch.prepare_model(model)`
3. **Report Metrics**: `ray.train.report(metrics)`

That's it! No process spawning, no distributed setup, no manual cleanup.

## What Ray Train Does For You

Ray Train handles all the boilerplate:
- ✅ Process spawning across GPUs
- ✅ Distributed initialization and cleanup
- ✅ Data partitioning (DistributedSampler)
- ✅ Model wrapping (DistributedDataParallel)
- ✅ Metric aggregation across workers
- ✅ Checkpoint management and versioning
- ✅ Fault tolerance and recovery
- ✅ Multi-node coordination

## Code Comparison

### Single Machine (train_single_machine.py)
```python
def train_func():
    train_loader, valid_loader = get_dataloaders(batch_size=512)
    model = VisionTransformer(...)
    model.to(device)

    for epoch in range(epochs):
        # ... training loop ...
        print(f"Accuracy: {accuracy}")
```

### Ray Train DDP (train_ray_ddp.py)
```python
def train_func_per_worker(config):
    train_loader, valid_loader = get_dataloaders(batch_size)

    # [1] Prepare data loaders
    train_loader = ray.train.torch.prepare_data_loader(train_loader)
    valid_loader = ray.train.torch.prepare_data_loader(valid_loader)

    # [2] Prepare model
    model = VisionTransformer(...)
    model = ray.train.torch.prepare_model(model)

    for epoch in range(epochs):
        # ... training loop (IDENTICAL to single-machine!) ...

        # [3] Report metrics
        ray.train.report({"accuracy": accuracy})
```

### Launching Training

**Single Machine:**
```bash
python train_single_machine.py --epochs 10
```

**Ray Train DDP:**
```bash
python train_ray_ddp.py --epochs 10 --num-workers 4
```

## Running the Example

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Verify GPU availability (optional but recommended)
python -c "import torch; print(f'GPUs: {torch.cuda.device_count()}')"
```

### Basic Training
```bash
# Train with all available GPUs (default: 10 epochs)
python train_ray_ddp.py

# Train with specific configuration
python train_ray_ddp.py --epochs 20 --batch-size 512 --lr 1e-3

# Train with specific number of workers
python train_ray_ddp.py --num-workers 4

# Train on CPU (for testing without GPUs)
python train_ray_ddp.py --num-workers 2 --use-gpu False
```

### Expected Output
```
============================================================
Ray Train DDP Configuration
============================================================
Ray version: 2.39.0
Number of workers: 4
Detected 4 GPU(s)
...

World Size: 4
Batch Size per Worker: 128
Global Batch Size: 512

Epoch 1/10
Train Epoch 1: 100%|██████████| 98/98 [00:15<00:00]
Valid Epoch 1: 100%|██████████| 20/20 [00:02<00:00]

Results:
  Train Loss: 1.4532
  Valid Loss: 1.2341
  Accuracy: 0.5678 (56.78%)
...

Training Results
Final metrics: {'accuracy': 0.8734}
```

## Understanding the Key Changes

### [1] prepare_data_loader()

**What it does:**
- Automatically creates a `DistributedSampler` under the hood
- Partitions data across workers (each worker sees unique samples)
- Handles epoch-based shuffling automatically
- No need to manually call `sampler.set_epoch()`

**What you get:**
- Each worker processes different data
- Global batch size = batch_size_per_worker × num_workers
- Proper shuffling across epochs

### [2] prepare_model()

**What it does:**
- Moves model to the correct GPU automatically
- Wraps model with `DistributedDataParallel`
- Sets up gradient synchronization
- Handles device placement

**What you get:**
- Model replica on each GPU
- Synchronized gradients after each backward pass
- All models stay consistent

### [3] train.report()

**What it does:**
- Aggregates metrics across all workers automatically
- Saves checkpoints with versioning
- Enables experiment tracking
- Supports fault tolerance

**What you get:**
- Global metrics (not per-worker)
- Automatic checkpoint management
- Integration with MLflow, TensorBoard, etc.

## Benefits Over Vanilla PyTorch DDP

| Feature | Vanilla PyTorch | Ray Train |
|---------|----------------|-----------|
| Code complexity | ~350 lines | ~250 lines |
| Process spawning | Manual (`mp.spawn`) | Automatic |
| Distributed setup | Manual (9 steps) | Automatic (3 lines) |
| Data partitioning | Manual `DistributedSampler` | `prepare_data_loader()` |
| Model wrapping | Manual `DDP()` | `prepare_model()` |
| Metric aggregation | Manual `all_reduce` | `train.report()` |
| Checkpointing | Manual implementation | Built-in |
| Fault tolerance | None | Built-in |
| Multi-node | Complex setup | Config change |
| Experiment tracking | Must implement | Built-in |

## Multi-Node Training

**Vanilla PyTorch** requires complex setup:
```bash
# Node 0
export MASTER_ADDR=192.168.1.1
export MASTER_PORT=12355
python train.py --rank 0 --world-size 8

# Node 1
export MASTER_ADDR=192.168.1.1
export MASTER_PORT=12355
python train.py --rank 4 --world-size 8
```

**Ray Train** - just change the config:
```python
scaling_config = ScalingConfig(
    num_workers=8,  # Ray discovers nodes automatically
    use_gpu=True
)
```

## Advanced Features

### Checkpoint Management
```python
checkpoint_config = CheckpointConfig(
    num_to_keep=2,  # Keep last 2 checkpoints
    checkpoint_score_attribute="accuracy",
    checkpoint_score_order="max"  # Keep best accuracy
)
```

### Fault Tolerance
If a worker fails:
- Ray detects the failure automatically
- Restores from the last checkpoint
- Resumes training automatically
- No code changes needed!

### Hyperparameter Tuning
```python
from ray import tune

tuner = tune.Tuner(
    TorchTrainer(...),
    param_space={"train_loop_config": {"lr": tune.grid_search([1e-4, 1e-3, 1e-2])}}
)
results = tuner.fit()
```

## Performance Tips

1. **Batch Size**: Increase batch size proportionally with num_workers
   - Single GPU: batch_size=128
   - 4 GPUs: batch_size=512 (128 per GPU)

2. **Data Loading**: Use `num_workers=2` in DataLoader for each GPU

3. **Mixed Precision**: Add automatic mixed precision for faster training
   ```python
   from torch.cuda.amp import autocast, GradScaler
   scaler = GradScaler()

   with autocast():
       outputs = model(inputs)
       loss = criterion(outputs, targets)
   ```

## When to Use Ray Train DDP

**✅ Use Ray Train DDP when:**
- You want simple, clean distributed training code
- Model fits on a single GPU (but you want faster training)
- You need fault tolerance
- You're scaling to multiple nodes
- You want built-in experiment tracking
- You value developer productivity

**→ Upgrade to FSDP when:**
- Model is too large to fit on a single GPU
- Training models with billions of parameters
- Want to maximize memory efficiency

## What's Next?

**→ Module 03: Ray Train FSDP**

See how to switch from DDP to FSDP with just ONE parameter change:
```python
# DDP version
model = ray.train.torch.prepare_model(model)

# FSDP version
model = ray.train.torch.prepare_model(model, parallel_strategy="fsdp")
```

That's it! Same code, different strategy, 10-100x memory savings.
