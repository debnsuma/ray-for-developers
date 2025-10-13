# Dataset Guide

This guide covers all supported datasets for the Video Highlight Generator project, including download instructions, preprocessing steps, and usage recommendations.

## Table of Contents
1. [Quick Start Datasets](#quick-start-datasets)
2. [Sports Datasets](#sports-datasets)
3. [General Purpose Datasets](#general-purpose-datasets)
4. [Custom Dataset Preparation](#custom-dataset-preparation)
5. [Data Format Specifications](#data-format-specifications)

---

## Quick Start Datasets

Perfect for initial testing and prototyping.

### TVSum (TV Summaries)

**Best for**: Quick testing, algorithm development, benchmarking

**Details**:
- 50 videos from 10 categories (news, documentary, cooking, etc.)
- Average length: 4-5 minutes per video
- Human importance scores for each frame
- 20 annotators per video
- Total size: ~5 GB

**Download**:
```bash
# Automatic download
python scripts/download_data.py --dataset tvsum --output ./data/raw/tvsum

# Manual download
# 1. Visit: https://github.com/yalesong/tvsum
# 2. Download ydata-tvsum50.mat
# 3. Download videos from provided URLs
```

**Data Structure**:
```
data/raw/tvsum/
├── videos/
│   ├── video_1.mp4
│   ├── video_2.mp4
│   └── ...
└── annotations/
    └── ydata-tvsum50.mat  # Importance scores
```

**Preprocessing**:
```bash
python scripts/preprocess.py \
    --dataset tvsum \
    --input ./data/raw/tvsum \
    --output ./data/processed/tvsum \
    --fps 3 \
    --resolution 224
```

**Usage in Code**:
```python
from src.data.datasets import TVSumDataset

dataset = TVSumDataset(
    root="./data/processed/tvsum",
    split="train",
    transform=video_transform
)

# Iterate through dataset
for video, importance_scores, metadata in dataset:
    print(f"Video shape: {video.shape}")  # (T, H, W, C)
    print(f"Scores: {importance_scores.shape}")  # (T,)
```

---

### SumMe (Summary Me)

**Best for**: Video summarization benchmarks, comparison with TVSum

**Details**:
- 25 videos from various categories
- Average length: 2-3 minutes per video
- Multiple human-created summaries per video
- 15-18 annotators per video
- Total size: ~3 GB

**Download**:
```bash
# Automatic download
python scripts/download_data.py --dataset summe --output ./data/raw/summe

# Manual download
# 1. Visit: https://gyglim.github.io/me/vsum/index.html
# 2. Fill out request form
# 3. Download provided zip file
```

**Data Structure**:
```
data/raw/summe/
├── videos/
│   ├── Air_Force_One.mp4
│   ├── Base_jumping.mp4
│   └── ...
└── annotations/
    └── GT/  # Ground truth summaries
        ├── Air_Force_One.mat
        ├── Base_jumping.mat
        └── ...
```

---

## Sports Datasets

Perfect for conference demos with exciting, visually appealing content.

### SoccerNet ⭐ HIGHLY RECOMMENDED

**Best for**: Sports highlights, action spotting, conference demos

**Details**:
- 500+ complete broadcast soccer matches
- Annotations for: goals, cards, substitutions, corners, etc.
- Temporal action spotting challenges
- Multiple camera angles for some matches
- Total size: ~150 GB (can download subsets)

**Download**:
```bash
# Install SoccerNet pip package
uv pip install SoccerNet

# Download action spotting data (recommended for this project)
python scripts/download_data.py \
    --dataset soccernet \
    --task action-spotting \
    --output ./data/raw/soccernet \
    --num-matches 50  # Start with 50 matches (~15 GB)

# Download full dataset (optional)
python scripts/download_soccernet_full.py \
    --output ./data/raw/soccernet \
    --password YOUR_PASSWORD  # Register at soccer-net.org
```

**Data Structure**:
```
data/raw/soccernet/
├── england_epl/
│   ├── 2014-2015/
│   │   ├── 2014-08-16_-_18-00_Arsenal_1_-_2_Crystal_Palace/
│   │   │   ├── 1_720p.mkv  # First half
│   │   │   ├── 2_720p.mkv  # Second half
│   │   │   └── Labels-v2.json  # Annotations
│   │   └── ...
│   └── ...
└── ...
```

**Annotations Format** (Labels-v2.json):
```json
{
  "UrlLocal": "england_epl/2014-2015/...",
  "annotations": [
    {
      "gameTime": "1 - 00:32",
      "label": "Corner",
      "position": "32000",  # milliseconds
      "half": "1",
      "confidence": "1.0"
    },
    {
      "gameTime": "1 - 23:17",
      "label": "Goal",
      "position": "1397000",
      "half": "1",
      "confidence": "1.0"
    }
  ]
}
```

**Preprocessing**:
```bash
python scripts/preprocess.py \
    --dataset soccernet \
    --input ./data/raw/soccernet \
    --output ./data/processed/soccernet \
    --extract-highlights \
    --context-window 20  # seconds before/after event
```

**Usage in Code**:
```python
from src.data.datasets import SoccerNetDataset

dataset = SoccerNetDataset(
    root="./data/processed/soccernet",
    split="train",
    task="action-spotting",
    features=["visual", "audio"]
)

# Iterate through dataset
for video_clip, label, timestamp in dataset:
    print(f"Clip shape: {video_clip.shape}")  # (T, H, W, C)
    print(f"Label: {label}")  # "Goal", "Corner", etc.
    print(f"Timestamp: {timestamp}")  # Position in match
```

**Supported Labels**:
- Ball out of play (far)
- Ball out of play (close)
- Corner
- Foul
- Goal
- Kick-off
- Penalty
- Red card
- Substitution
- Yellow card

---

### NBA Player Tracking (Custom)

**Best for**: Basketball highlights, player tracking demonstrations

**Details**:
- Requires manual collection from NBA.com or YouTube
- Recommended: 20-30 games (~50 GB)
- Focus on: dunks, 3-pointers, blocks, assists
- Can use open-source basketball detection models

**Collection Guide**:
```bash
# Use yt-dlp to download games (ensure compliance with terms)
yt-dlp "https://youtube.com/watch?v=VIDEO_ID" \
    -f "best[height<=720]" \
    -o "./data/raw/nba/%(title)s.%(ext)s"

# Use our annotation tool
python scripts/annotate_highlights.py \
    --video ./data/raw/nba/game1.mp4 \
    --output ./data/raw/nba/game1_annotations.json
```

---

## General Purpose Datasets

Large-scale datasets for pre-training and fine-tuning.

### ActivityNet

**Best for**: Action recognition pre-training, diverse activities

**Details**:
- 20,000 videos from YouTube
- 200 activity classes
- Temporal annotations (start/end times)
- Average video length: 2 minutes
- Total size: ~500 GB (can download subsets)

**Download**:
```bash
# Install activitynet package
pip install activitynet

# Download subset (recommended)
python scripts/download_data.py \
    --dataset activitynet \
    --output ./data/raw/activitynet \
    --split val \
    --num-videos 1000  # ~25 GB
```

**Data Structure**:
```
data/raw/activitynet/
├── videos/
│   ├── v_--1DO2V4K74.mp4
│   └── ...
└── annotations/
    └── activity_net.v1-3.min.json
```

**Activity Classes** (sample):
- Sports: basketball dunk, soccer penalty, swimming
- Music: playing guitar, drumming, singing
- Home activities: cooking, cleaning, gardening
- Arts & crafts: painting, sculpting, knitting
- ...and 195 more

---

### Kinetics-700

**Best for**: Large-scale pre-training, transfer learning

**Details**:
- 700,000 video clips (10 seconds each)
- 700 human action classes
- Trimmed clips focused on single action
- Total size: ~450 GB

**Download**:
```bash
# Download Kinetics downloader
git clone https://github.com/cvdfoundation/kinetics-dataset.git
cd kinetics-dataset

# Download Kinetics-700 (this will take a while!)
python download.py \
    --dataset kinetics700 \
    --output_dir ../../data/raw/kinetics700 \
    --num_workers 8
```

**Note**: Many videos may no longer be available on YouTube. Expect ~60-70% success rate.

---

### WebVid-10M

**Best for**: Text-to-video alignment, large-scale pre-training

**Details**:
- 10 million video-text pairs
- Collected from stock footage sites
- Alt-text descriptions for each video
- Total size: ~5 TB (use subsets!)

**Download Subset**:
```bash
# Download 10K video subset (~50 GB)
python scripts/download_data.py \
    --dataset webvid \
    --output ./data/raw/webvid \
    --num-videos 10000 \
    --min-resolution 480
```

---

## Custom Dataset Preparation

### Recording Your Own Videos

**Recommended Settings**:
- Resolution: 1280x720 (720p) or 1920x1080 (1080p)
- Frame rate: 30 fps
- Format: MP4 (H.264 codec)
- Audio: AAC, 48kHz, stereo
- Bitrate: 5-10 Mbps

**Annotation Tool**:
```bash
# Launch web-based annotation interface
python scripts/annotation_tool.py \
    --video ./my_video.mp4 \
    --output ./my_video_annotations.json

# Opens browser at http://localhost:5000
# Mark highlight regions by clicking start/end times
```

**Annotation Format**:
```json
{
  "video_path": "./my_video.mp4",
  "duration": 600.5,
  "fps": 30,
  "highlights": [
    {
      "start_time": 45.2,
      "end_time": 52.8,
      "importance": 0.9,
      "label": "exciting_moment",
      "description": "Player scores winning goal"
    },
    {
      "start_time": 120.5,
      "end_time": 125.0,
      "importance": 0.7,
      "label": "key_moment",
      "description": "Coach tactical discussion"
    }
  ],
  "metadata": {
    "annotator": "user@example.com",
    "date": "2025-01-15",
    "version": "1.0"
  }
}
```

---

## Data Format Specifications

### Processed Video Format

After preprocessing, videos are converted to:

```
data/processed/{dataset_name}/
├── videos/
│   ├── video_001/
│   │   ├── frames/  # Extracted frames
│   │   │   ├── frame_0000.jpg
│   │   │   ├── frame_0001.jpg
│   │   │   └── ...
│   │   ├── audio.wav  # Extracted audio
│   │   ├── transcript.json  # Speech-to-text
│   │   └── metadata.json
│   └── ...
├── features/  # Pre-computed features (optional)
│   ├── video_001_visual.npy
│   ├── video_001_audio.npy
│   └── ...
└── annotations/
    ├── video_001.json
    └── ...
```

### Metadata Format

```json
{
  "video_id": "video_001",
  "original_path": "./data/raw/tvsum/video_1.mp4",
  "duration": 245.6,
  "fps": 30,
  "original_fps": 30,
  "sampling_fps": 3,
  "resolution": [224, 224],
  "num_frames": 738,
  "num_sampled_frames": 74,
  "audio": {
    "sample_rate": 16000,
    "channels": 1,
    "duration": 245.6
  },
  "processing": {
    "date": "2025-01-15T10:30:00",
    "config": "configs/preprocess.yaml",
    "version": "1.0"
  }
}
```

### Feature Format

Pre-computed features saved as NumPy arrays:

```python
import numpy as np

# Visual features: (num_frames, feature_dim)
visual_features = np.load("features/video_001_visual.npy")
# Shape: (74, 2048) for ResNet50 features

# Audio features: (num_segments, feature_dim)
audio_features = np.load("features/video_001_audio.npy")
# Shape: (246, 768) for Wav2Vec2 features

# Text features: (num_sentences, feature_dim)
text_features = np.load("features/video_001_text.npy")
# Shape: (25, 768) for BERT features
```

---

## Dataset Statistics

### Comparison Table

| Dataset | Videos | Hours | Annotations | Best For | Download Time | Size |
|---------|--------|-------|-------------|----------|---------------|------|
| TVSum | 50 | 4 | Frame importance | Testing | 10 min | 5 GB |
| SumMe | 25 | 1 | Human summaries | Benchmarking | 5 min | 3 GB |
| SoccerNet | 500+ | 800+ | Action spots | Sports demo | 2-4 hours | 150 GB |
| ActivityNet | 20K | 600 | Temporal segments | Pre-training | 1-2 days | 500 GB |
| Kinetics-700 | 700K | 2000+ | Action labels | Pre-training | 1-2 days | 450 GB |
| WebVid-10M | 10M | 52K | Text pairs | Text-video | N/A | 5 TB |

### Recommended Combinations

**For Conference Demo**:
1. Start with: TVSum (quick testing)
2. Main demo: SoccerNet (50 matches = 15 GB)
3. Backup demos: Custom videos (5-10 videos)

**For Research**:
1. Pre-training: Kinetics-700 subset
2. Fine-tuning: ActivityNet + SoccerNet
3. Evaluation: TVSum + SumMe

**For Production**:
1. Collect domain-specific dataset (1000+ videos)
2. Pre-train on: ActivityNet/Kinetics
3. Fine-tune on: Your custom dataset

---

## Data Loading with Ray Data

### Basic Loading

```python
import ray

# Load video dataset with Ray Data
ds = ray.data.read_binary_files(
    "data/processed/soccernet/videos/*/*.mp4",
    include_paths=True
)

print(f"Total videos: {ds.count()}")
print(f"Schema: {ds.schema()}")
```

### Parallel Preprocessing

```python
import ray

def extract_frames(batch):
    """Extract frames from video batch"""
    import cv2
    frames_list = []

    for video_bytes in batch["bytes"]:
        # Decode video
        cap = cv2.VideoCapture(video_bytes)
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        frames_list.append(frames)

    return {"frames": frames_list}

# Process videos in parallel
ds = ray.data.read_binary_files("data/*.mp4")
ds = ds.map_batches(extract_frames, batch_size=1, num_cpus=2)
```

### Feature Extraction Pipeline

```python
import ray
from ray.data import Dataset

def load_video_dataset(path: str) -> Dataset:
    """Complete video loading pipeline"""

    # Load videos
    ds = ray.data.read_binary_files(f"{path}/*.mp4")

    # Extract frames (parallel)
    ds = ds.map_batches(
        extract_frames,
        batch_size=1,
        num_cpus=2
    )

    # Extract audio (parallel)
    ds = ds.map_batches(
        extract_audio,
        batch_size=1,
        num_cpus=2
    )

    # Compute visual features (GPU)
    ds = ds.map_batches(
        compute_visual_features,
        batch_size=8,
        num_gpus=0.25
    )

    # Compute audio features (GPU)
    ds = ds.map_batches(
        compute_audio_features,
        batch_size=16,
        num_gpus=0.25
    )

    return ds

# Usage
dataset = load_video_dataset("data/processed/soccernet")
dataset.write_parquet("data/features/soccernet")
```

---

## Troubleshooting

### Common Issues

**Issue**: Videos fail to download
```bash
# Solution: Install yt-dlp
pip install yt-dlp

# Update yt-dlp
pip install --upgrade yt-dlp
```

**Issue**: FFmpeg not found
```bash
# Solution: Install FFmpeg
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Verify installation
ffmpeg -version
```

**Issue**: Out of disk space
```bash
# Solution: Process in batches
python scripts/preprocess.py \
    --input ./data/raw \
    --output ./data/processed \
    --batch-size 10 \
    --delete-after-process  # Delete raw after processing
```

**Issue**: Slow preprocessing
```bash
# Solution: Use more Ray workers
python scripts/preprocess.py \
    --input ./data/raw \
    --output ./data/processed \
    --num-workers 8 \
    --num-cpus-per-worker 4
```

---

## Next Steps

- **Architecture Guide**: Learn how datasets feed into the pipeline → [architecture.md](./architecture.md)
- **Model Guide**: Choose models for your dataset → [models.md](./models.md)
- **Training Guide**: Fine-tune models on your data → [training.md](./training.md)

---

**Questions?** Open an issue or check the [main README](../README.md).
