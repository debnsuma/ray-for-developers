# 01. Vanilla PyTorch Distributed Data Parallel (DDP)

## ⚠️ Learn but Don't Use

This module demonstrates the **traditional approach** to distributed training using PyTorch's native DistributedDataParallel (DDP). This example intentionally shows all the boilerplate code you need to write to get distributed training working.

**Purpose:** Understand the pain points so you appreciate how much Ray Train simplifies everything in the next module!

## What is Data Parallel Training?

**Data Parallel** means:
- Each GPU gets a **full copy** of the model
- The training data is **split across GPUs**
- Each GPU computes gradients on its subset of data
- Gradients are **synchronized** across all GPUs
- All models stay in sync

**Example with 4 GPUs:**
```
Batch size: 128 per GPU → Global batch size: 512

GPU 0: Model copy + samples 0-127
GPU 1: Model copy + samples 128-255
GPU 2: Model copy + samples 256-383
GPU 3: Model copy + samples 384-511

After backward pass:
- Each GPU has gradients from its samples
- All gradients are averaged across GPUs (all-reduce)
- Each GPU updates its model with averaged gradients
```

## The 9 Boilerplate Steps in Vanilla PyTorch DDP

Look at `train_ddp.py` - notice the numbered comments marking boilerplate:

### 1. **Manual Process Group Setup** (`setup_distributed`)
```python
os.environ['MASTER_ADDR'] = 'localhost'
os.environ['MASTER_PORT'] = '12355'
dist.init_process_group(backend, rank=rank, world_size=world_size)
```
- You must set environment variables
- You must choose the right backend (nccl/gloo)
- You must coordinate ranks manually

### 2. **Manual Cleanup** (`cleanup_distributed`)
```python
dist.destroy_process_group()
```
- Forget this and processes hang forever
- Must be called on every rank, even after errors

### 3. **DistributedSampler** (Data Partitioning)
```python
train_sampler = DistributedSampler(
    train_dataset,
    num_replicas=world_size,
    rank=rank,
    shuffle=True
)
```
- Forget this and all GPUs train on the same data!
- Must manually pass to DataLoader instead of `shuffle=True`

### 4. **Manual Metric Aggregation**
```python
dist.all_reduce(loss_tensor, op=dist.ReduceOp.SUM)
dist.all_reduce(correct_tensor, op=dist.ReduceOp.SUM)
```
- Each GPU has partial metrics
- You must manually reduce across all ranks
- Easy to mess up the aggregation logic

### 5. **Lifecycle Management** (`train_worker`)
- Every rank must: setup → train → cleanup
- Error handling must work across all ranks
- One rank failing can hang all others

### 6. **Model Wrapping with DDP**
```python
model = SimpleCNN().cuda(rank)
model = DDP(model, device_ids=[rank])
```
- Must wrap after moving to GPU
- Must remember to use `model.module` when saving

### 7. **Epoch Setting for Sampler**
```python
train_sampler.set_epoch(epoch)
```
- Forget this and shuffling doesn't work properly
- Must be called before each epoch

### 8. **Cleanup in Finally Block**
- Must ensure cleanup even if training fails
- Must coordinate cleanup across all ranks

### 9. **Process Spawning** (`mp.spawn`)
```python
mp.spawn(train_worker, args=(world_size, args), nprocs=world_size)
```
- Must manually spawn one process per GPU
- Must handle process coordination

## Running the Example

### Prerequisites
```bash
# Requires GPU(s)
pip install torch torchvision

# Check GPU availability
python -c "import torch; print(f'GPUs: {torch.cuda.device_count()}')"
```

### Basic Training
```bash
# Train with all available GPUs (default: 10 epochs)
python train_ddp.py

# Train with specific settings
python train_ddp.py --epochs 20 --batch-size 128 --lr 0.1

# Train with specific number of GPUs
python train_ddp.py --world-size 2
```

### Expected Output
```
==============================================================
PyTorch Distributed Data Parallel (DDP) Training
==============================================================
Detected 4 GPU(s)
Will spawn 4 processes
...

[Rank 0] Process group initialized (world_size=4)
[Rank 1] Process group initialized (world_size=4)
[Rank 2] Process group initialized (world_size=4)
[Rank 3] Process group initialized (world_size=4)

Training Configuration:
  World Size: 4
  Batch Size per GPU: 128
  Global Batch Size: 512
  Epochs: 10
  Learning Rate: 0.1

Epoch 1/10
  Train Loss: 1.523 | Train Acc: 45.32%
  Val Loss: 1.234 | Val Acc: 56.78%
...
```

## Pain Points with Vanilla PyTorch DDP

### 1. **Massive Boilerplate**
- ~300+ lines of code for a simple training script
- 9 manual steps that are error-prone
- Easy to forget critical steps (cleanup, sampler.set_epoch, etc.)

### 2. **No Fault Tolerance**
- One GPU fails → entire training crashes
- Must manually implement checkpointing and recovery
- No automatic retry logic

### 3. **Poor Resource Management**
- Hard to scale beyond single-node
- Must manually configure network settings for multi-node
- No automatic resource discovery

### 4. **Difficult Debugging**
- Errors happen across multiple processes
- Hard to know which rank failed and why
- Print statements get interleaved

### 5. **Manual Multi-Node Setup**
For multi-node training, you need:
```python
# Must set on each node
os.environ['MASTER_ADDR'] = '192.168.1.1'  # IP of node 0
os.environ['MASTER_PORT'] = '12355'
os.environ['RANK'] = str(node_rank)  # 0, 1, 2, ...
os.environ['WORLD_SIZE'] = str(total_nodes * gpus_per_node)

# Launch separately on each node
python train_ddp.py --node-rank $NODE_RANK --world-size $WORLD_SIZE
```

### 6. **No Built-in Experiment Tracking**
- Must manually log metrics
- Must manually save checkpoints
- Must manually implement early stopping

## When to Use Vanilla PyTorch DDP

**Use vanilla DDP when:**
- ✅ You need maximum control over every detail
- ✅ You're training on a single node with fixed hardware
- ✅ You're building a custom training framework
- ✅ Your infrastructure is very simple and stable

**Don't use vanilla DDP when:**
- ❌ You want quick experimentation and iteration
- ❌ You need fault tolerance and automatic recovery
- ❌ You're scaling to multiple nodes
- ❌ You want automatic hyperparameter tuning
- ❌ You need easy experiment tracking

## What's Next?

**→ Move to Module 02: Ray Train DDP**

See how Ray Train eliminates 90% of this boilerplate while adding:
- Automatic resource management
- Fault tolerance
- Easy multi-node scaling
- Built-in experiment tracking
- Much simpler code (~50 lines vs ~300)

The pain points you see here are **exactly why Ray Train exists**.
