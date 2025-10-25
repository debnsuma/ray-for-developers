# 03. Ray Train with FSDP (Fully Sharded Data Parallel)

## 🚀 For Large Models

This module shows how **ridiculously easy** it is to switch from DDP to FSDP with Ray Train. The change? **ONE PARAMETER** in `prepare_model()`.

**When to use:** Your model doesn't fit on a single GPU, or you want maximum memory efficiency for large models.

## DDP vs FSDP: The Memory Story

### Data Parallel (DDP)
```
GPU 0: [Full Model Copy] + [Data Batch 0]
GPU 1: [Full Model Copy] + [Data Batch 1]
GPU 2: [Full Model Copy] + [Data Batch 2]
GPU 3: [Full Model Copy] + [Data Batch 3]

Memory per GPU: Full model + gradients + optimizer states
Total Model Memory: 4x (redundant!)
```

### Fully Sharded Data Parallel (FSDP)
```
GPU 0: [Model Shard 0] + [Data Batch 0]
GPU 1: [Model Shard 1] + [Data Batch 1]
GPU 2: [Model Shard 2] + [Data Batch 2]
GPU 3: [Model Shard 3] + [Data Batch 3]

Memory per GPU: 1/4 model + gradients + optimizer states
Total Model Memory: 1x (efficient!)
```

## The One-Parameter Change

### DDP Version
```python
model = ray.train.torch.prepare_model(model)
```

### FSDP Version
```python
model = ray.train.torch.prepare_model(model, parallel_strategy="fsdp")
```

**That's literally it!** Ray handles:
- Model sharding across GPUs
- Gradient sharding
- All-gather operations during forward pass
- Reduce-scatter operations during backward pass
- Optimizer state sharding

## When to Use FSDP

### Use FSDP When:
- ✅ Model doesn't fit on a single GPU
- ✅ Training models with billions of parameters (LLMs, large vision models)
- ✅ Want to train larger models with limited GPU memory
- ✅ Memory is the bottleneck, not compute
- ✅ You have multiple GPUs available

### Stick with DDP When:
- ❌ Model comfortably fits on a single GPU
- ❌ Communication overhead would hurt performance
- ❌ You have very fast GPUs but slower interconnect
- ❌ Batch size is already very small

## Memory Savings Example

**Training a 1B parameter model (assuming fp32):**

### DDP (4 GPUs):
```
Model: 1B params × 4 bytes = 4 GB
Gradients: 4 GB
Optimizer (Adam): 8 GB (2 states)
---
Per GPU: ~16 GB
Total: ~64 GB
```

### FSDP (4 GPUs):
```
Model shard: 1B/4 params × 4 bytes = 1 GB
Gradient shard: 1 GB
Optimizer shard: 2 GB
---
Per GPU: ~4 GB
Total: ~16 GB (4x savings!)
```

## Running the Example

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Requires PyTorch 2.0+ for native FSDP support
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
```

### Basic Training
```bash
# Train with all available GPUs
python train_ray_fsdp.py

# Train with specific configuration
python train_ray_fsdp.py --epochs 20 --num-workers 4

# Compare with DDP
cd ../02-ray-train-ddp
python train_ray_ddp.py --epochs 20 --num-workers 4
```

### Expected Output
```
============================================================
Ray Train FSDP Configuration
============================================================
Number of workers: 4

NOTE: FSDP shards model parameters across 4 workers
      Each worker uses ~1/4 of the model memory
============================================================

Model wrapped with FSDP - parameters are sharded across GPUs!

Epoch 1/10
Results:
  Accuracy: 0.5678 (56.78%)
...
```

## Actual Training Results

**VisionTransformer on CIFAR-10 (10 epochs, 12 workers across 3 nodes):**

- **Training Time**: 4 minutes 12 seconds (252 seconds)
- **Final Accuracy**: 60.19%
- **Configuration**: 12 workers (3 nodes × 4 GPUs), batch_size=42 per worker (504 global)
- **Storage**: `/mnt/cluster_storage/cifar10_fsdp_b3f34120/`
- **Memory per GPU**: ~1/12 of full model (sharded across 12 workers)

**Performance Comparison:**
- **1.9x faster** than vanilla DDP (4 GPUs, 1 node): 4:12 vs 7:55
- **Nearly identical to Ray Train DDP**: 4:12 vs 4:01 (minimal FSDP overhead)
- **Better accuracy**: 60.19% vs 57.62% (vanilla DDP)
- **Memory efficiency**: Each GPU holds only 1/12 of model parameters

**Key Insight**: FSDP has minimal overhead for this model size. The memory savings become critical for models that don't fit on a single GPU!

## Code Walkthrough

The code is **99% identical** to the DDP version. Here's the complete diff:

```diff
  # Create model
  model = VisionTransformer(...)

  # Prepare model
- model = ray.train.torch.prepare_model(model)
+ model = ray.train.torch.prepare_model(model, parallel_strategy="fsdp")

  # Everything else is IDENTICAL!
  optimizer = torch.optim.AdamW(model.parameters(), ...)
  for epoch in range(epochs):
      # ... training loop ...
```

That's the entire change! The training loop, data loading, metric reporting - all stay the same.

## How FSDP Works Under the Hood

### Forward Pass:
1. Each GPU stores only its shard of parameters
2. Before computation: **All-gather** full layer parameters
3. Compute forward pass with full parameters
4. After computation: **Discard** gathered parameters (keep only shard)

### Backward Pass:
1. Each GPU computes gradients for full layer
2. After computation: **Reduce-scatter** gradients to shards
3. Each GPU updates only its parameter shard

### Result:
- ✅ Same computation as DDP (uses full parameters during forward/backward)
- ✅ Much lower memory (stores only sharded parameters)
- ⚠️ More communication (all-gather + reduce-scatter per layer)

## Performance Considerations

### Communication Overhead
FSDP has more communication than DDP:
- **DDP**: One all-reduce after backward pass
- **FSDP**: All-gather per layer (forward) + reduce-scatter per layer (backward)

**Mitigation:**
- Use fast interconnect (NVLink, InfiniBand)
- Increase batch size to amortize communication
- Use mixed precision (less data to transfer)

### Memory vs Communication Trade-off

```
Small Models (<1B params):
  DDP: ✅ Lower communication, ✅ fits in memory
  FSDP: ❌ Extra communication overhead

Large Models (>10B params):
  DDP: ❌ Doesn't fit in memory
  FSDP: ✅ Makes training possible!
```

## Advanced FSDP Configuration

Ray Train uses sensible defaults, but you can customize:

```python
from ray.train.torch import TorchConfig

torch_config = TorchConfig(
    backend="nccl",  # Communication backend
    fsdp_config={
        "sharding_strategy": "FULL_SHARD",  # or "SHARD_GRAD_OP", "NO_SHARD"
        "cpu_offload": False,  # Offload to CPU for even larger models
        "mixed_precision": True,  # Use fp16/bf16 for faster training
    }
)

trainer = TorchTrainer(
    ...,
    torch_config=torch_config
)
```

### Sharding Strategies:

1. **FULL_SHARD** (default):
   - Shard model, gradients, and optimizer states
   - Maximum memory savings

2. **SHARD_GRAD_OP**:
   - Shard gradients and optimizer states only
   - Keep full model on each GPU
   - Less memory savings, less communication

3. **NO_SHARD**:
   - Equivalent to DDP (no sharding)
   - Used for comparison

## Real-World Use Cases

### Training Large Language Models
```python
# GPT-3 style model (175B parameters)
# Would require ~700GB memory with DDP
# With FSDP on 64 GPUs: ~11GB per GPU

model = GPT3Model(n_params=175_000_000_000)
model = ray.train.torch.prepare_model(model, parallel_strategy="fsdp")
# Now trainable on 64 A100 GPUs!
```

### Training Large Vision Models
```python
# ViT-Giant (2B parameters)
# Would require ~8GB memory with DDP
# With FSDP on 8 GPUs: ~1GB per GPU

model = VisionTransformer(hidden_dim=6144, num_layers=48)
model = ray.train.torch.prepare_model(model, parallel_strategy="fsdp")
```

## Debugging Tips

### Check Memory Usage
```python
import torch
if local_rank == 0:
    print(f"GPU memory: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
```

### Verify Sharding
```python
# FSDP wraps each layer - check the model structure
if local_rank == 0:
    print(model)  # Should see FSDP wrapper around modules
```

### Compare DDP vs FSDP
Run both and compare:
1. Memory usage per GPU
2. Training throughput (samples/sec)
3. Communication overhead

## Combining FSDP with Other Techniques

### FSDP + Mixed Precision
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()
model = ray.train.torch.prepare_model(model, parallel_strategy="fsdp")

for inputs, targets in dataloader:
    with autocast():
        outputs = model(inputs)
        loss = criterion(outputs, targets)

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

### FSDP + Gradient Accumulation
```python
accumulation_steps = 4
model.train()

for i, (inputs, targets) in enumerate(dataloader):
    outputs = model(inputs)
    loss = criterion(outputs, targets) / accumulation_steps
    loss.backward()

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

### FSDP + CPU Offloading
```python
# For REALLY large models, offload to CPU
model = ray.train.torch.prepare_model(
    model,
    parallel_strategy="fsdp",
    fsdp_config={"cpu_offload": True}
)
# Even larger models, but slower training
```

## Comparison Summary

| Aspect | DDP | FSDP |
|--------|-----|------|
| Model memory per GPU | Full model | 1/N of model |
| Gradient memory | Full gradients | 1/N of gradients |
| Optimizer memory | Full state | 1/N of state |
| Communication | All-reduce (1x) | All-gather + reduce-scatter (Nx) |
| Peak memory | High | Low |
| Speed (small models) | Faster | Slower (overhead) |
| Speed (large models) | N/A (OOM) | Enables training |
| Code changes with Ray | `prepare_model(model)` | `prepare_model(model, parallel_strategy="fsdp")` |

## What's Next?

You've now seen the full progression:
1. **Single Machine** - Baseline PyTorch training
2. **Vanilla DDP** - Manual distributed setup (painful!)
3. **Ray Train DDP** - Clean distributed training (easy!)
4. **Ray Train FSDP** - Memory-efficient training (one parameter!)

**Next steps:**
- Try training larger models with FSDP
- Experiment with mixed precision training
- Scale to multiple nodes
- Integrate with Ray Tune for hyperparameter optimization

## Further Reading

- [Ray Train Documentation](https://docs.ray.io/en/latest/train/train.html)
- [PyTorch FSDP Tutorial](https://pytorch.org/tutorials/intermediate/FSDP_tutorial.html)
- [Scaling PyTorch models with FSDP](https://engineering.fb.com/2021/07/15/open-source/fsdp/)
