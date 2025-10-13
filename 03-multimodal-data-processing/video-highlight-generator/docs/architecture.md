# Architecture Guide

Complete system architecture for the AI-Powered Video Highlight Generator with Ray.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    VIDEO HIGHLIGHT GENERATOR                     │
│                                                                   │
│  Input: Long-form video (sports, lectures, meetings)            │
│  Output: AI-generated highlight reel with key moments           │
│  Technology: Ray Data + Ray Train + Ray Serve + PyTorch         │
└─────────────────────────────────────────────────────────────────┘
```

## Development Stages

### Stage 1: M4 MacBook Pro (Current)
- **Goal**: Build and test end-to-end pipeline
- **Dataset**: 5-10 short videos (~2GB)
- **Models**: Lightweight models (MobileNet, small transformers)
- **Processing**: CPU-only with MPS acceleration
- **Ray**: Local single-node deployment

### Stage 2: RTX 5090
- **Goal**: GPU acceleration and larger datasets
- **Dataset**: 50-100 videos (~15GB)
- **Models**: Full-size models (X3D, VideoMAE)
- **Processing**: GPU-accelerated inference
- **Ray**: Single-node with GPU scheduling

### Stage 3: Multi-GPU Cluster
- **Goal**: Production-scale processing
- **Dataset**: 500+ videos (~150GB)
- **Models**: Ensemble models with fine-tuning
- **Processing**: Distributed across cluster
- **Ray**: Multi-node cluster deployment

---

## Core Components

### 1. Data Ingestion Layer

**Purpose**: Load and validate input videos

**Ray Component**: Ray Data

**Implementation**:
```python
import ray
from ray.data import read_binary_files

# Load videos from directory
video_ds = ray.data.read_binary_files(
    "data/raw/*.mp4",
    include_paths=True,
    parallelism=4  # Adjust for M4: 4, RTX 5090: 8, Cluster: 32
)

# Validate videos
def validate_video(batch):
    """Check video format and duration"""
    valid_videos = []
    for video_path, video_bytes in zip(batch["path"], batch["bytes"]):
        try:
            import cv2
            import tempfile

            # Save temporarily to check
            with tempfile.NamedTemporaryFile(suffix='.mp4') as tmp:
                tmp.write(video_bytes)
                tmp.flush()

                cap = cv2.VideoCapture(tmp.name)
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    duration = frame_count / fps if fps > 0 else 0

                    valid_videos.append({
                        'path': video_path,
                        'bytes': video_bytes,
                        'fps': fps,
                        'duration': duration,
                        'valid': duration > 10  # Min 10 seconds
                    })
                cap.release()
        except Exception as e:
            print(f"Error validating {video_path}: {e}")

    return valid_videos

validated_ds = video_ds.map_batches(
    validate_video,
    batch_size=1,
    num_cpus=1
)
```

---

### 2. Preprocessing Pipeline

**Purpose**: Extract frames, audio, and metadata

**Ray Component**: Ray Data with parallel processing

**Stage-specific Configuration**:
```python
# M4 MacBook Pro
PREPROCESS_CONFIG_M4 = {
    "num_workers": 4,  # M4 has 10 cores, leave some for OS
    "batch_size": 1,
    "num_cpus_per_worker": 1,
    "target_fps": 1,  # Sample 1 frame per second
    "resolution": (224, 224),  # Smaller for faster processing
}

# RTX 5090
PREPROCESS_CONFIG_5090 = {
    "num_workers": 8,
    "batch_size": 4,
    "num_cpus_per_worker": 2,
    "target_fps": 3,
    "resolution": (224, 224),
}

# Multi-GPU Cluster
PREPROCESS_CONFIG_CLUSTER = {
    "num_workers": 32,
    "batch_size": 8,
    "num_cpus_per_worker": 4,
    "target_fps": 3,
    "resolution": (224, 224),
}
```

**Pipeline Implementation**:
```python
import ray
import cv2
import numpy as np
from typing import Dict, List

class VideoPreprocessor:
    def __init__(self, config: dict):
        self.config = config

    def extract_frames(self, batch: Dict) -> Dict:
        """Extract frames at target FPS"""
        results = []

        for video_bytes in batch["bytes"]:
            import tempfile

            with tempfile.NamedTemporaryFile(suffix='.mp4') as tmp:
                tmp.write(video_bytes)
                tmp.flush()

                cap = cv2.VideoCapture(tmp.name)
                original_fps = cap.get(cv2.CAP_PROP_FPS)
                frame_interval = int(original_fps / self.config["target_fps"])

                frames = []
                frame_idx = 0

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_idx % frame_interval == 0:
                        # Resize frame
                        frame_resized = cv2.resize(
                            frame,
                            self.config["resolution"]
                        )
                        frames.append(frame_resized)

                    frame_idx += 1

                cap.release()
                results.append({"frames": np.array(frames)})

        return results

    def extract_audio(self, batch: Dict) -> Dict:
        """Extract audio track"""
        results = []

        for video_bytes in batch["bytes"]:
            import tempfile
            import subprocess

            with tempfile.NamedTemporaryFile(suffix='.mp4') as video_tmp:
                video_tmp.write(video_bytes)
                video_tmp.flush()

                with tempfile.NamedTemporaryFile(suffix='.wav') as audio_tmp:
                    # Use ffmpeg to extract audio
                    subprocess.run([
                        'ffmpeg', '-i', video_tmp.name,
                        '-vn', '-acodec', 'pcm_s16le',
                        '-ar', '16000', '-ac', '1',
                        audio_tmp.name, '-y'
                    ], capture_output=True)

                    audio_tmp.seek(0)
                    audio_bytes = audio_tmp.read()
                    results.append({"audio": audio_bytes})

        return results

# Usage
preprocessor = VideoPreprocessor(PREPROCESS_CONFIG_M4)

frames_ds = video_ds.map_batches(
    preprocessor.extract_frames,
    batch_size=1,
    num_cpus=1
)

audio_ds = video_ds.map_batches(
    preprocessor.extract_audio,
    batch_size=1,
    num_cpus=1
)
```

---

### 3. Feature Extraction Layer

**Purpose**: Extract visual, audio, and text features using ML models

**Ray Component**: Ray Data + Ray Actors for model serving

**Models by Stage**:

| Stage | Visual Model | Audio Model | Text Model |
|-------|-------------|-------------|------------|
| M4 MacBook | MobileNetV3 | Wav2Vec2-Small | DistilBERT |
| RTX 5090 | X3D-M | Wav2Vec2-Base | BERT-Base |
| Cluster | X3D-L + VideoMAE | Wav2Vec2-Large | BERT-Large |

**Implementation**:
```python
import ray
import torch
from transformers import AutoModel, AutoProcessor

@ray.remote
class VisualFeatureExtractor:
    def __init__(self, model_name: str = "mobilenet_v3_small", device: str = "mps"):
        """
        M4 MacBook: use MPS (Metal Performance Shaders)
        RTX 5090: use CUDA
        """
        self.device = device

        if model_name == "mobilenet_v3_small":
            # Lightweight for M4
            import torchvision.models as models
            self.model = models.mobilenet_v3_small(pretrained=True)
            self.model.classifier = torch.nn.Identity()  # Remove classifier
        elif model_name == "x3d_m":
            # Heavier model for GPU
            import pytorchvideo.models as pv_models
            self.model = pv_models.x3d.create_x3d(
                model_num_class=400,
                model_size='m'
            )

        self.model.to(device)
        self.model.eval()

    def extract_features(self, frames: np.ndarray) -> np.ndarray:
        """Extract features from video frames"""
        with torch.no_grad():
            # frames shape: (T, H, W, C)
            frames_tensor = torch.from_numpy(frames).float()
            frames_tensor = frames_tensor.permute(0, 3, 1, 2)  # (T, C, H, W)
            frames_tensor = frames_tensor.to(self.device)

            # Process in batches to avoid OOM
            batch_size = 8
            features_list = []

            for i in range(0, len(frames_tensor), batch_size):
                batch = frames_tensor[i:i+batch_size]
                features = self.model(batch)
                features_list.append(features.cpu().numpy())

            return np.concatenate(features_list, axis=0)

@ray.remote
class AudioFeatureExtractor:
    def __init__(self, model_name: str = "facebook/wav2vec2-base", device: str = "mps"):
        self.device = device
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.to(device)
        self.model.eval()

    def extract_features(self, audio_bytes: bytes) -> np.ndarray:
        """Extract features from audio"""
        import soundfile as sf
        import io

        # Load audio
        audio, sr = sf.read(io.BytesIO(audio_bytes))

        # Process
        inputs = self.processor(
            audio,
            sampling_rate=16000,
            return_tensors="pt"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            features = outputs.last_hidden_state.mean(dim=1)  # Pool over time

        return features.cpu().numpy()

# Create actor pool for parallel processing
visual_extractors = [
    VisualFeatureExtractor.remote(device="mps")
    for _ in range(2)  # M4: 2 actors, RTX 5090: 4 actors, Cluster: 16 actors
]

audio_extractors = [
    AudioFeatureExtractor.remote(device="mps")
    for _ in range(2)
]

# Extract features in parallel
def extract_visual_features_batch(batch):
    futures = []
    for frames in batch["frames"]:
        # Round-robin across actors
        actor = visual_extractors[len(futures) % len(visual_extractors)]
        future = actor.extract_features.remote(frames)
        futures.append(future)

    features = ray.get(futures)
    return {"visual_features": features}

features_ds = frames_ds.map_batches(
    extract_visual_features_batch,
    batch_size=4,
    num_cpus=1
)
```

---

### 4. Multimodal Fusion & Highlight Detection

**Purpose**: Combine all modalities and detect highlight moments

**Ray Component**: Ray Actors for stateful processing

**Implementation**:
```python
import ray
import numpy as np
from scipy.signal import find_peaks

@ray.remote
class HighlightDetector:
    def __init__(self, config: dict):
        self.config = config
        self.weights = {
            'visual': 0.5,
            'audio': 0.3,
            'text': 0.2
        }

    def compute_importance_scores(
        self,
        visual_features: np.ndarray,
        audio_features: np.ndarray,
        text_features: np.ndarray = None
    ) -> np.ndarray:
        """
        Compute frame-level importance scores

        Returns:
            importance_scores: (T,) array of scores [0, 1]
        """
        T = len(visual_features)

        # Visual excitement score (based on feature variance)
        visual_scores = np.zeros(T)
        window_size = 10  # 10 frames

        for i in range(T):
            start = max(0, i - window_size // 2)
            end = min(T, i + window_size // 2)
            window = visual_features[start:end]
            visual_scores[i] = np.var(window)

        # Normalize
        visual_scores = (visual_scores - visual_scores.min()) / (
            visual_scores.max() - visual_scores.min() + 1e-6
        )

        # Audio excitement score (simplified, assume pre-computed)
        # In production, use audio classifier for cheers, applause, etc.
        audio_scores = np.random.rand(T) * 0.3  # Placeholder

        # Combine scores
        importance_scores = (
            self.weights['visual'] * visual_scores +
            self.weights['audio'] * audio_scores
        )

        # Temporal smoothing
        from scipy.ndimage import gaussian_filter1d
        importance_scores = gaussian_filter1d(importance_scores, sigma=3)

        return importance_scores

    def detect_highlights(
        self,
        importance_scores: np.ndarray,
        fps: float,
        top_k: int = 5,
        min_duration: float = 3.0,
        max_duration: float = 10.0
    ) -> List[Dict]:
        """
        Detect highlight segments

        Returns:
            highlights: List of {start_time, end_time, score}
        """
        # Find peaks in importance scores
        peaks, properties = find_peaks(
            importance_scores,
            prominence=0.2,
            distance=int(fps * min_duration)
        )

        # Sort by prominence
        peak_scores = properties['prominences']
        sorted_indices = np.argsort(peak_scores)[::-1][:top_k]

        highlights = []
        for idx in sorted_indices:
            peak_frame = peaks[idx]
            score = peak_scores[idx]

            # Define segment around peak
            duration_frames = int(fps * max_duration / 2)
            start_frame = max(0, peak_frame - duration_frames)
            end_frame = min(len(importance_scores), peak_frame + duration_frames)

            highlights.append({
                'start_time': start_frame / fps,
                'end_time': end_frame / fps,
                'peak_time': peak_frame / fps,
                'score': float(score)
            })

        return sorted(highlights, key=lambda x: x['start_time'])

# Usage
detector = HighlightDetector.remote(config={})

result = ray.get(detector.compute_importance_scores.remote(
    visual_features,
    audio_features
))
```

---

### 5. Video Generation Layer

**Purpose**: Create final highlight reel from detected segments

**Ray Component**: Ray Tasks for parallel video editing

**Implementation**:
```python
import ray
import subprocess

@ray.remote
def extract_video_segment(
    video_path: str,
    start_time: float,
    end_time: float,
    output_path: str
) -> str:
    """Extract video segment using ffmpeg"""
    duration = end_time - start_time

    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(start_time),
        '-t', str(duration),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-y',
        output_path
    ]

    subprocess.run(cmd, capture_output=True, check=True)
    return output_path

@ray.remote
def concatenate_videos(
    segment_paths: List[str],
    output_path: str,
    add_transitions: bool = True
) -> str:
    """Concatenate video segments"""
    import tempfile

    # Create concat file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for path in segment_paths:
            f.write(f"file '{path}'\n")
        concat_file = f.name

    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',
        '-y',
        output_path
    ]

    subprocess.run(cmd, capture_output=True, check=True)
    return output_path

# Parallel segment extraction
def generate_highlight_reel(
    video_path: str,
    highlights: List[Dict],
    output_path: str
) -> str:
    """Generate final highlight reel"""
    import tempfile
    import os

    # Extract segments in parallel
    segment_futures = []
    segment_paths = []

    for i, highlight in enumerate(highlights):
        segment_path = os.path.join(
            tempfile.gettempdir(),
            f"segment_{i}.mp4"
        )
        segment_paths.append(segment_path)

        future = extract_video_segment.remote(
            video_path,
            highlight['start_time'],
            highlight['end_time'],
            segment_path
        )
        segment_futures.append(future)

    # Wait for all segments
    ray.get(segment_futures)

    # Concatenate
    final_video = ray.get(
        concatenate_videos.remote(segment_paths, output_path)
    )

    # Cleanup
    for path in segment_paths:
        os.remove(path)

    return final_video
```

---

## Deployment Architecture

### M4 MacBook Pro (Development)

```
┌─────────────────────────────────────┐
│      M4 MacBook Pro (Local)         │
│                                      │
│  ┌──────────────────────────────┐  │
│  │   Ray Head Node              │  │
│  │   (localhost:8265)           │  │
│  └──────────────────────────────┘  │
│              │                      │
│  ┌───────────┴───────────┐         │
│  │                       │         │
│  ▼                       ▼         │
│  [Worker 1]         [Worker 2]     │
│  CPU: 2 cores       CPU: 2 cores   │
│  MPS: shared        MPS: shared    │
└─────────────────────────────────────┘
```

### RTX 5090 (Single GPU)

```
┌─────────────────────────────────────┐
│      Workstation (RTX 5090)         │
│                                      │
│  ┌──────────────────────────────┐  │
│  │   Ray Head Node              │  │
│  └──────────────────────────────┘  │
│              │                      │
│  ┌───────────┼───────────┐         │
│  │           │           │         │
│  ▼           ▼           ▼         │
│  [Worker 1]  [Worker 2]  [Worker 3]│
│  GPU: 0.33   GPU: 0.33   GPU: 0.33 │
│  CPU: 4      CPU: 4      CPU: 4    │
└─────────────────────────────────────┘
```

### Multi-GPU Cluster (Production)

```
┌─────────────────────────────────────────────────────────┐
│                    Ray Cluster                          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │   Head Node (Scheduler + Dashboard)              │  │
│  │   ray-head.local:8265                            │  │
│  └──────────────────────────────────────────────────┘  │
│                          │                              │
│      ┌───────────────────┼───────────────────┐         │
│      │                   │                   │         │
│      ▼                   ▼                   ▼         │
│  ┌────────┐         ┌────────┐         ┌────────┐     │
│  │ Worker │         │ Worker │         │ Worker │     │
│  │ Node 1 │         │ Node 2 │         │ Node 3 │     │
│  │────────│         │────────│         │────────│     │
│  │ 4xGPU  │         │ 4xGPU  │         │ 4xGPU  │     │
│  │ 32CPU  │         │ 32CPU  │         │ 32CPU  │     │
│  │ 128GB  │         │ 128GB  │         │ 128GB  │     │
│  └────────┘         └────────┘         └────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## Performance Optimization

### M4 MacBook Pro Tips

1. **Use MPS (Metal Performance Shaders)**:
```python
device = "mps" if torch.backends.mps.is_available() else "cpu"
```

2. **Limit Ray Workers**:
```python
ray.init(num_cpus=4, num_gpus=0)  # M4 has 10 cores, use 4
```

3. **Smaller Batch Sizes**:
```python
batch_size = 1  # Avoid OOM on M4
```

4. **Use Lightweight Models**:
- MobileNetV3 instead of ResNet50
- DistilBERT instead of BERT-Base
- Wav2Vec2-Small instead of Wav2Vec2-Large

5. **Optimize Video Resolution**:
```python
target_resolution = (224, 224)  # Smaller than 512x512
```

---

## Next Steps

- **Implementation**: See [training.md](./training.md) for model training
- **Deployment**: See [deployment.md](./deployment.md) for Ray Serve setup
- **Models**: See [models.md](./models.md) for model selection

---

*This architecture scales from laptop development to production clusters with minimal code changes.*
