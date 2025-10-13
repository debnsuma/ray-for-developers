# GPU Upgrade Guide - RTX 5090 & Multi-Node Ray Cluster

## Overview

This guide provides recommendations for upgrading your Video Highlight Generator from M4 MacBook Pro (MPS) to **RTX 5090 GPU** and scaling to a **multi-node Ray cluster**.

---

## Current Setup vs. RTX 5090

| Aspect | Current (M4 MPS) | RTX 5090 Target |
|--------|------------------|-----------------|
| **Model** | MobileNetV3-Small | CLIP ViT-L/14 or VideoMAE |
| **Device** | Apple MPS | CUDA (RTX 5090) |
| **Feature Dim** | 576 dims | 768-1024 dims |
| **Batch Size** | 1 (sequential) | 32-64 (batched) |
| **FPS** | 30-60 FPS | 500-1500 FPS |
| **Multi-GPU** | No | Yes (multi-node cluster) |
| **VRAM** | Shared (16GB) | 32GB dedicated |

---

## 🎯 Recommended Models for RTX 5090

### Option 1: CLIP ViT-L/14 (Recommended for General Videos)

**Best for**: General video content, multi-modal understanding

```python
from transformers import CLIPProcessor, CLIPModel

@ray.remote(num_gpus=1)
class VisualFeatureExtractor:
    def __init__(self):
        self.device = torch.device("cuda")

        # Load CLIP ViT-L/14
        self.model = CLIPModel.from_pretrained(
            "openai/clip-vit-large-patch14"
        ).to(self.device)

        self.processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-large-patch14"
        )

        self.model.eval()

    def extract_frame_features(self, frame_batch: List[Image]) -> np.ndarray:
        # Batch processing for efficiency
        inputs = self.processor(
            images=frame_batch,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            features = self.model.get_image_features(**inputs)

        return features.cpu().numpy()
```

**Specifications:**
- **Feature Dim**: 768 dimensions
- **Model Size**: ~890MB
- **VRAM Usage**: ~4GB per actor
- **Expected FPS**: 800-1200 on RTX 5090
- **Batch Size**: 32-64 frames
- **Multi-modal**: Can understand text + images

**Why CLIP?**
- ✅ Pre-trained on 400M image-text pairs
- ✅ Excellent semantic understanding
- ✅ Multi-modal (can use text prompts for highlight detection)
- ✅ Fast inference on modern GPUs
- ✅ 768-dim features (rich representation)
- ✅ Works well with Ray distributed processing

---

### Option 2: VideoMAE (Video-Specific, Highest Quality)

**Best for**: Maximum quality, video-specific features

```python
from transformers import VideoMAEFeatureExtractor, VideoMAEModel

@ray.remote(num_gpus=1)
class VisualFeatureExtractor:
    def __init__(self):
        self.device = torch.device("cuda")

        # Load VideoMAE (pre-trained on video data)
        self.model = VideoMAEModel.from_pretrained(
            "MCG-NJU/videomae-base"
        ).to(self.device)

        self.processor = VideoMAEFeatureExtractor.from_pretrained(
            "MCG-NJU/videomae-base"
        )

        self.model.eval()

    def extract_video_features(self, frames: List[Image]) -> np.ndarray:
        # VideoMAE expects temporal sequences (16 frames)
        inputs = self.processor(
            frames,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            features = outputs.last_hidden_state.mean(dim=1)  # Pool over time

        return features.cpu().numpy()
```

**Specifications:**
- **Feature Dim**: 768 dimensions
- **Model Size**: ~330MB
- **VRAM Usage**: ~6GB per actor
- **Expected FPS**: 500-800 on RTX 5090
- **Batch Size**: 16-32 frames (temporal sequences)
- **Temporal**: Understands motion and temporal context

**Why VideoMAE?**
- ✅ Pre-trained specifically on video data
- ✅ Understands temporal dynamics
- ✅ Best for motion/action detection
- ✅ Self-supervised learning (high quality features)
- ✅ Excellent for sports/action videos
- ❌ More VRAM intensive
- ❌ Requires sequential frames (16-frame chunks)

---

### Option 3: EfficientNet-B7 (Balanced Performance)

**Best for**: Balance between speed and quality

```python
from torchvision.models import efficientnet_b7, EfficientNet_B7_Weights

@ray.remote(num_gpus=1)
class VisualFeatureExtractor:
    def __init__(self):
        self.device = torch.device("cuda")

        # Load EfficientNet-B7
        self.model = efficientnet_b7(
            weights=EfficientNet_B7_Weights.IMAGENET1K_V1
        ).to(self.device)

        # Remove classifier
        self.model.classifier = torch.nn.Identity()
        self.model.eval()

    def extract_frame_features(self, frame_batch: List[Image]) -> np.ndarray:
        # Batch processing
        inputs = torch.stack([
            self.transform(frame) for frame in frame_batch
        ]).to(self.device)

        with torch.no_grad():
            features = self.model(inputs)

        return features.cpu().numpy()
```

**Specifications:**
- **Feature Dim**: 2560 dimensions
- **Model Size**: ~256MB
- **VRAM Usage**: ~3GB per actor
- **Expected FPS**: 1000-1500 on RTX 5090
- **Batch Size**: 64-128 frames
- **Accuracy**: 84.3% ImageNet top-1

**Why EfficientNet-B7?**
- ✅ Excellent accuracy/speed tradeoff
- ✅ Compact model size
- ✅ High-dimensional features (2560 dims)
- ✅ Very fast on modern GPUs
- ✅ Lower VRAM usage = more actors per GPU
- ❌ Image-only (no multi-modal or temporal)

---

### Option 4: DINO v2 (State-of-the-Art Self-Supervised)

**Best for**: Highest quality features, semantic understanding

```python
import torch
from transformers import AutoImageProcessor, AutoModel

@ray.remote(num_gpus=1)
class VisualFeatureExtractor:
    def __init__(self):
        self.device = torch.device("cuda")

        # Load DINOv2 ViT-L
        self.processor = AutoImageProcessor.from_pretrained(
            'facebook/dinov2-large'
        )
        self.model = AutoModel.from_pretrained(
            'facebook/dinov2-large'
        ).to(self.device)

        self.model.eval()

    def extract_frame_features(self, frame_batch: List[Image]) -> np.ndarray:
        inputs = self.processor(
            images=frame_batch,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            features = outputs.last_hidden_state[:, 0]  # CLS token

        return features.cpu().numpy()
```

**Specifications:**
- **Feature Dim**: 1024 dimensions
- **Model Size**: ~1.1GB
- **VRAM Usage**: ~5GB per actor
- **Expected FPS**: 600-900 on RTX 5090
- **Batch Size**: 32-48 frames
- **Quality**: State-of-the-art semantic features

**Why DINOv2?**
- ✅ State-of-the-art self-supervised features
- ✅ Excellent semantic understanding
- ✅ Works well for diverse content
- ✅ No labeled data needed for fine-tuning
- ✅ Great for unseen/novel content
- ❌ Larger model size
- ❌ Slightly slower than EfficientNet

---

## 🏆 Final Recommendation: CLIP ViT-L/14

**Why CLIP is the best choice for your use case:**

1. **Multi-modal Understanding**: Can combine visual + text analysis
2. **Rich Semantic Features**: 768 dims with excellent semantic meaning
3. **Fast on RTX 5090**: 800-1200 FPS expected
4. **Ray-Friendly**: Easy to batch and distribute
5. **Flexible**: Works for all video types (sports, lectures, vlogs)
6. **Future-Proof**: Can add text-based highlight detection later

### Enhanced Highlight Detection with CLIP

```python
def detect_highlights_with_text(self, features_path, text_prompts):
    """
    Use CLIP's multi-modal capabilities for text-guided highlights

    Example prompts:
    - "exciting moment"
    - "goal being scored"
    - "audience cheering"
    - "important point"
    """
    features = np.load(features_path)

    # Get text embeddings
    text_features = self.get_text_features(text_prompts)

    # Compute similarity scores
    similarity_scores = features @ text_features.T

    # Combine with visual importance scores
    combined_scores = (
        0.4 * visual_importance +
        0.6 * similarity_scores
    )

    return self.detect_peaks(combined_scores)
```

---

## 🚀 Multi-Node Ray Cluster Configuration

### Architecture for Multi-Node with RTX 5090s

```
┌─────────────────────────────────────────────────────┐
│                  Head Node (CPU Only)                │
│  • Ray cluster coordinator                          │
│  • Task scheduling                                  │
│  • Resource management                              │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Worker 1│  │ Worker 2│  │ Worker 3│
│ RTX 5090│  │ RTX 5090│  │ RTX 5090│
│ 4 actors│  │ 4 actors│  │ 4 actors│
│ 8GB VRAM│  │ 8GB VRAM│  │ 8GB VRAM│
│  each   │  │  each   │  │  each   │
└─────────┘  └─────────┘  └─────────┘
```

### Configuration Files

#### 1. Head Node Setup

```python
# head_node.py
import ray

ray.init(
    address='auto',  # Auto-detect in cluster
    _node_ip_address='192.168.1.100',  # Head node IP
    include_dashboard=True,
    dashboard_host='0.0.0.0',
    dashboard_port=8265
)

print("Ray cluster initialized")
print(f"Dashboard: http://192.168.1.100:8265")
```

#### 2. Worker Node Setup

```python
# worker_node.py
import ray

ray.init(
    address='ray://192.168.1.100:10001',  # Head node address
    _node_ip_address='auto',
    num_gpus=1,  # RTX 5090
    resources={'GPU_VRAM': 32000}  # 32GB VRAM
)

print(f"Worker connected to cluster")
```

#### 3. Enhanced Feature Extractor for Multi-GPU

```python
# src/models/feature_extractors_gpu.py

import ray
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Dict, List

@ray.remote(num_gpus=1)  # Each actor gets 1 GPU
class VisualFeatureExtractorGPU:
    """
    GPU-accelerated feature extractor for RTX 5090
    Uses CLIP ViT-L/14 for high-quality features
    """

    def __init__(self, model_name: str = "openai/clip-vit-large-patch14", batch_size: int = 32):
        """
        Initialize GPU-accelerated feature extractor

        Args:
            model_name: CLIP model variant
            batch_size: Batch size for processing (32-64 for RTX 5090)
        """
        print(f"🔧 Initializing GPU Feature Extractor (Ray Actor)...")

        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"   Device: {self.device}")
        print(f"   GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB"
              if torch.cuda.is_available() else "")

        # Load CLIP model
        print(f"   Loading {model_name}...")
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()

        # Enable optimizations
        if torch.cuda.is_available():
            # Use TF32 for faster inference on Ampere/Ada GPUs
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True

            # Optional: Compile model for extra speed (PyTorch 2.0+)
            try:
                self.model = torch.compile(self.model, mode="reduce-overhead")
                print(f"   ✅ Model compiled with torch.compile()")
            except:
                print(f"   ⚠️  torch.compile() not available, using eager mode")

        print(f"   ✅ Model loaded on {self.device}")

    def extract_frame_features_batch(self, frame_paths: List[str]) -> np.ndarray:
        """
        Extract features from a batch of frames (GPU-optimized)

        Args:
            frame_paths: List of paths to frame images

        Returns:
            Feature matrix (batch_size x 768)
        """
        # Load images
        images = [Image.open(fp).convert('RGB') for fp in frame_paths]

        # Preprocess batch
        inputs = self.processor(
            images=images,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        # Extract features
        with torch.no_grad(), torch.cuda.amp.autocast():  # Mixed precision
            features = self.model.get_image_features(**inputs)

        return features.cpu().numpy()

    def extract_video_features(
        self,
        video_dir: str,
        output_path: str = None
    ) -> Dict:
        """
        Extract features from all frames in a video directory (batched)

        Args:
            video_dir: Path to processed video directory
            output_path: Path to save features

        Returns:
            Dictionary with features and metadata
        """
        video_path = Path(video_dir)
        frames_dir = video_path / "frames"

        if not frames_dir.exists():
            return {'success': False, 'error': f'Frames directory not found: {frames_dir}'}

        # Get all frames
        frame_files = sorted(frames_dir.glob("frame_*.jpg"))

        if not frame_files:
            return {'success': False, 'error': f'No frames found in {frames_dir}'}

        print(f"\n📹 Extracting features: {video_path.name}")
        print(f"   Frames: {len(frame_files)}")
        print(f"   Batch size: {self.batch_size}")

        # Process in batches
        features_list = []

        for i in range(0, len(frame_files), self.batch_size):
            batch_files = frame_files[i:i + self.batch_size]
            batch_features = self.extract_frame_features_batch(
                [str(f) for f in batch_files]
            )
            features_list.append(batch_features)

            if (i + self.batch_size) % 100 == 0:
                print(f"   Processed {min(i + self.batch_size, len(frame_files))}/{len(frame_files)} frames...")

        # Concatenate all batches
        features_array = np.vstack(features_list)

        print(f"   ✅ Features shape: {features_array.shape}")

        result = {
            'success': True,
            'video_name': video_path.name,
            'features': features_array,
            'num_frames': len(frame_files),
            'feature_dim': features_array.shape[1]
        }

        # Save features
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(output_path, features_array)
            print(f"   💾 Saved features to {output_path}")
            result['output_path'] = str(output_path)

        return result

    def get_device_info(self) -> Dict:
        """Get GPU device information"""
        if torch.cuda.is_available():
            return {
                'device': str(self.device),
                'gpu_name': torch.cuda.get_device_name(0),
                'vram_total_gb': torch.cuda.get_device_properties(0).total_memory / 1e9,
                'vram_allocated_gb': torch.cuda.memory_allocated(0) / 1e9,
                'vram_reserved_gb': torch.cuda.memory_reserved(0) / 1e9,
                'cuda_version': torch.version.cuda
            }
        else:
            return {'device': 'cpu', 'gpu_available': False}


def create_feature_extractor_pool_gpu(num_actors: int = 4, batch_size: int = 32) -> List:
    """
    Create a pool of GPU-accelerated feature extractors

    Args:
        num_actors: Number of actors (GPUs available in cluster)
        batch_size: Batch size per actor (32-64 for RTX 5090)

    Returns:
        List of actor handles
    """
    print(f"\n🚀 Creating pool of {num_actors} GPU Feature Extractors...")
    print(f"   Batch size per actor: {batch_size}")

    actors = [
        VisualFeatureExtractorGPU.remote(
            model_name="openai/clip-vit-large-patch14",
            batch_size=batch_size
        )
        for _ in range(num_actors)
    ]

    print(f"✅ Created {num_actors} GPU actors")

    return actors
```

---

## 📊 Performance Comparison

### Single RTX 5090 (vs. M4)

| Model | Feature Dim | FPS (Single GPU) | Speedup vs M4 | VRAM Usage |
|-------|-------------|------------------|---------------|------------|
| MobileNetV3-Small (M4) | 576 | 30-60 | 1.0x | ~2GB |
| **CLIP ViT-L/14** | **768** | **800-1200** | **20-30x** | **~4GB** |
| EfficientNet-B7 | 2560 | 1000-1500 | 25-40x | ~3GB |
| VideoMAE | 768 | 500-800 | 15-20x | ~6GB |
| DINOv2 Large | 1024 | 600-900 | 18-25x | ~5GB |

### Multi-Node Cluster (3 RTX 5090s)

| Configuration | Total FPS | Videos/Hour | Speedup |
|---------------|-----------|-------------|---------|
| 1 GPU, 4 actors | 800-1200 | 288-432 | 1x |
| 3 GPUs, 12 actors | 2400-3600 | 864-1296 | 3x |
| 3 GPUs, optimal batching | 3000-4500 | 1080-1620 | 4-5x |

---

## 🛠️ Implementation Steps

### Step 1: Update Dependencies

```bash
# requirements-gpu.txt
ray[default,data]==2.39.0
torch==2.5.1+cu121  # CUDA 12.1 for RTX 5090
torchvision==0.20.1+cu121
transformers==4.46.3
accelerate==0.34.0  # For distributed training
bitsandbytes==0.44.0  # Optional: quantization
```

### Step 2: Create GPU-Optimized Pipeline

```python
# src/pipeline_gpu.py

class VideoHighlightPipelineGPU(VideoHighlightPipeline):
    """GPU-accelerated pipeline for RTX 5090"""

    def __init__(
        self,
        num_actors: int = 4,  # 4 actors per RTX 5090
        batch_size: int = 32,  # Optimal for RTX 5090
        model_name: str = "openai/clip-vit-large-patch14",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.num_actors = num_actors
        self.batch_size = batch_size
        self.model_name = model_name

    def extract_features(self, processed_dir: str, output_path: str) -> Dict:
        """GPU-accelerated feature extraction"""
        from src.models.feature_extractors_gpu import create_feature_extractor_pool_gpu

        # Create GPU actor pool
        actors = create_feature_extractor_pool_gpu(
            num_actors=self.num_actors,
            batch_size=self.batch_size
        )

        # Use first actor (or distribute across multiple videos)
        actor = actors[0]

        result = ray.get(actor.extract_video_features.remote(
            video_dir=processed_dir,
            output_path=output_path
        ))

        return result
```

### Step 3: Multi-Node Cluster Setup

```bash
# On Head Node (192.168.1.100)
ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265

# On Worker Node 1 (192.168.1.101)
ray start --address='192.168.1.100:6379' --num-gpus=1

# On Worker Node 2 (192.168.1.102)
ray start --address='192.168.1.100:6379' --num-gpus=1

# On Worker Node 3 (192.168.1.103)
ray start --address='192.168.1.100:6379' --num-gpus=1
```

### Step 4: Connect and Run

```python
# demo_gpu_cluster.py

import ray

# Connect to cluster
ray.init(address='ray://192.168.1.100:10001')

# Check resources
print(f"Available GPUs: {ray.available_resources().get('GPU', 0)}")

# Create pipeline with cluster-wide resources
pipeline = VideoHighlightPipelineGPU(
    num_actors=12,  # 4 actors per GPU × 3 GPUs
    batch_size=32,
    model_name="openai/clip-vit-large-patch14"
)

# Run pipeline
results = pipeline.run(video_path="my_video.mp4")
```

---

## 🎯 Quick Migration Path

### Minimal Changes Required

1. **Update feature extractor** (`src/models/feature_extractors.py`):
   - Change model from `mobilenet_v3_small` to CLIP
   - Update device from `mps` to `cuda`
   - Add batch processing

2. **Update pipeline** (`src/pipeline.py`):
   - Add `num_gpus=1` to actor decorator
   - Update feature dimension (576 → 768)
   - Adjust batch size parameter

3. **Test on single GPU first**:
   ```bash
   python demo_enhanced.py  # Should work with CLIP automatically
   ```

4. **Scale to multi-node**:
   - Start Ray cluster
   - Update `num_actors` to match total GPUs
   - No other code changes needed!

---

## 📈 Expected Performance

### 10-Minute Video Processing Time

| Configuration | Current (M4) | Single RTX 5090 | 3× RTX 5090 Cluster |
|---------------|--------------|-----------------|---------------------|
| Preprocessing | 2.3s | 2.3s | 2.3s |
| Feature Extraction | 14.1s | **0.5s** | **0.2s** |
| Highlight Detection | 0.8s | 0.8s | 0.8s |
| Video Generation | 11.2s | 11.2s | 11.2s |
| **Total** | **28.4s** | **14.8s** | **14.5s** |

**Note**: Main speedup is in feature extraction. To fully utilize multi-GPU cluster, process multiple videos in parallel.

### Batch Processing (10 Videos)

| Configuration | Total Time | Videos/Hour |
|---------------|------------|-------------|
| M4 MacBook Pro | 284s (4.7 min) | ~127 |
| Single RTX 5090 | 148s (2.5 min) | ~243 |
| 3× RTX 5090 (parallel) | **50s** | **720** |

---

## 🔧 Optimization Tips

### 1. Mixed Precision Training (FP16)
```python
with torch.cuda.amp.autocast():
    features = self.model(**inputs)
```
**Speedup**: 1.5-2x faster

### 2. Torch Compile (PyTorch 2.0+)
```python
self.model = torch.compile(self.model, mode="reduce-overhead")
```
**Speedup**: 1.2-1.5x faster

### 3. Optimal Batch Size
- RTX 5090 (32GB VRAM): Use batch_size=64
- Test with: `batch_size = 32, 64, 128` and measure FPS

### 4. TF32 Precision
```python
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
```
**Speedup**: 1.2-1.3x faster on Ampere/Ada GPUs

---

## ✅ Summary

### Best Setup for RTX 5090

1. **Model**: CLIP ViT-L/14 (`openai/clip-vit-large-patch14`)
2. **Actors per GPU**: 4 actors
3. **Batch Size**: 32-64 frames
4. **Expected FPS**: 800-1200 FPS (20-30x faster than M4)
5. **Multi-Node**: 3× RTX 5090 = 2400-3600 FPS

### Migration Checklist

- [ ] Install CUDA 12.1+ and PyTorch with CUDA support
- [ ] Update `feature_extractors.py` to use CLIP
- [ ] Test on single GPU with `demo_enhanced.py`
- [ ] Set up Ray cluster (head + 3 workers)
- [ ] Update `num_actors` to match GPU count
- [ ] Enable optimizations (mixed precision, torch.compile)
- [ ] Benchmark and tune batch size
- [ ] Scale to batch processing multiple videos

**Result**: 20-30x faster feature extraction on single GPU, 60-90x faster on 3-GPU cluster for batch processing!
