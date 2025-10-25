# Quick Start Guide - Distributed Training

Get started with distributed training in 5 minutes!

## 🚀 Fastest Path to Success

```bash
# 1. Navigate to Ray Train DDP (recommended)
cd 02-distributed-training/02-ray-train-ddp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run training with auto-detected GPUs
python train_ray_ddp.py --epochs 1

# 4. See results in /mnt/cluster_storage/cifar10_ddp_*/
```

That's it! 🎉

---

## 📚 Learning Path (Recommended Order)

### Step 1: Understand the Baseline
```bash
cd 01-vanilla-pytorch-ddp
python train_single_machine.py --epochs 1
# Takes ~2 minutes on 1 GPU
```

### Step 2: See Vanilla DDP Pain (Optional)
```bash
python train_ddp.py --epochs 1 --world-size 4
# Notice: 426 lines of boilerplate code!
```

### Step 3: Try Ray Train DDP ⭐
```bash
cd ../02-ray-train-ddp
python train_ray_ddp.py --epochs 1 --num-workers 4
# Same performance, 25% less code!
```

### Step 4: Switch to FSDP
```bash
cd ../03-ray-train-fsdp
python train_ray_fsdp.py --epochs 1 --num-workers 4
# Just 1 parameter change!
```

---

## ⚙️ Common Commands

### Train with Specific Configuration
```bash
# 10 epochs, 4 workers, custom batch size
python train_ray_ddp.py --epochs 10 --num-workers 4 --batch-size 512

# Custom learning rate
python train_ray_ddp.py --epochs 10 --lr 1e-3
```

### Train on CPU (Testing)
```bash
python train_ray_ddp.py --num-workers 2 --no-gpu --epochs 1
```

### Compare DDP vs FSDP
```bash
# DDP (faster initialization)
cd 02-ray-train-ddp
time python train_ray_ddp.py --epochs 1

# FSDP (slower initialization, better for large models)
cd ../03-ray-train-fsdp
time python train_ray_fsdp.py --epochs 1
```

---

## 🎯 Choose Your Path

### I want to learn the fundamentals
→ Start with `01-vanilla-pytorch-ddp` to understand the pain points

### I want to train a model quickly
→ Jump to `02-ray-train-ddp` and start training immediately

### I have a large model that doesn't fit on 1 GPU
→ Use `03-ray-train-fsdp` for memory-efficient training

### I want to see the differences
→ Read `COMPARISON.md` for side-by-side code comparison

---

## 📊 What to Expect

### Training Output
```
============================================================
Ray Train DDP Configuration
============================================================
Number of workers: 4
Batch Size per Worker: 128
Global Batch Size: 512
Epochs: 1

[Step 1/5] Loading data...
[Step 2/5] Preparing data loaders...
[Step 3/5] Creating model...
[Step 4/5] Wrapping with DDP...
[Step 5/5] Starting training...

Epoch 1/1
Train Epoch 1: 100%|██████████| 98/98 [00:15<00:00]
Valid Epoch 1: 100%|██████████| 20/20 [00:02<00:00]

Results:
  Train Loss: 1.4532
  Valid Loss: 1.2341
  Accuracy: 0.5678 (56.78%)

Training completed!
Final accuracy: 56.78%
```

### Checkpoints Location
```
/mnt/cluster_storage/cifar10_ddp_<run_id>/
├── checkpoint_000005/
│   └── model.pt
└── params.json
```

---

## 🐛 Troubleshooting

### Issue: "No CUDA devices found"
**Solution:** Use CPU mode
```bash
python train_ray_ddp.py --num-workers 2 --no-gpu
```

### Issue: "Out of memory"
**Solution 1:** Reduce batch size
```bash
python train_ray_ddp.py --batch-size 256
```

**Solution 2:** Switch to FSDP
```bash
cd ../03-ray-train-fsdp
python train_ray_fsdp.py --num-workers 4
```

### Issue: Training hangs at FSDP initialization
**Solution:** Use fewer workers (1 per GPU)
```bash
python train_ray_fsdp.py --num-workers 4  # For 4 GPUs
```

### Issue: "URI has empty scheme"
**Solution:** Already fixed! Using `/mnt/cluster_storage` for shared storage

---

## 📈 Performance Tips

### Optimal Worker Configuration
- **Single Node (4 GPUs):** Use `--num-workers 4` (1 per GPU)
- **Multi Node (8+ GPUs):** Ray handles distribution automatically
- **CPU Testing:** Use `--num-workers 2` or `--num-workers 4`

### Batch Size Guidelines
- **Single GPU:** 128-256
- **4 GPUs with DDP:** 512 (128 per GPU)
- **4 GPUs with FSDP:** 512 (can go higher due to memory savings)

### When to Use What
| Model Size | Single GPU? | Use This |
|------------|-------------|----------|
| < 1B params | ✅ Fits | Ray Train DDP |
| 1-10B params | ❌ OOM | Ray Train FSDP |
| 10B+ params | ❌ OOM | Ray Train FSDP + optimizations |

---

## 📚 Next Steps

After completing distributed training:

1. **Read COMPARISON.md** - Understand the code differences
2. **Check README.md** - Deep dive into concepts
3. **Explore Module 03** - Apply to multimodal data processing
4. **Experiment** - Train your own models!

---

## 💡 Key Takeaways

✅ **Ray Train eliminates 90% of boilerplate** - Focus on your model, not infrastructure

✅ **Same performance as vanilla PyTorch** - Just better developer experience

✅ **Switch DDP ↔ FSDP with 1 parameter** - Adapt to any model size

✅ **Built-in fault tolerance** - Training continues even if workers fail

✅ **Multi-node ready** - Scale from 1 GPU to hundreds with config change

---

**Ready to start?** Pick your path above and begin training! 🚀
