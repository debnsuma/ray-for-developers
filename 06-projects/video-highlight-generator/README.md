# Video Highlight Generator

## Overview

A system that utomatically create short highlight reels from videos using Ray distributed computing and visual analysis. It identifies and extracts the most interesting moments from videos. Uses Ray for distributed processing and `MobileNetV3` for visual feature extraction.

## Getting Started with Anyscale (Recommended)

The easiest way to get started is using Anyscale Platform, which provides a ready-to-use Ray cluster:

1. **Create a free account** at [anyscale.com](https://console.anyscale.com/register/v2)
2. **Create a workspace** - Your Ray cluster will be automatically provisioned and ready to use
3. **Clone this repository** in your workspace
4. **Start coding** - The cluster is already up and running with all necessary Ray resources

This eliminates the need for local setup and gives you immediate access to GPU resources and distributed computing capabilities.

**For local development**, continue with the Installation section below.

## Installation

### 1. Prerequisites

```bash
# Python 3.12 required
python --version

# Install FFmpeg (system requirement)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg
```

### 2. Python Dependencies

```bash
cd video-highlight-generator

# Install dependencies
pip install -r requirements.txt
```

**Key Dependencies:**
- `ray[default,data]==2.47.0` - Distributed computing
- `torch==2.5.1` - Deep learning
- `opencv-python-headless==4.10.0.84` - Headless video processing
- `torchvision==0.20.1` - Pre-trained models

### 3. (Optional) Terminal Video Playback

```bash
# macOS only - for terminal video playback
brew install timg
```

---

## Quick Start

### Download Sample Videos

```bash
# Downloads 3 Creative Commons videos (~50MB)
python scripts/download_sample_videos.py
```

### Run Interactive Demo

```bash
python demo.py
```

The demo will:
1. Show menu with video sources (sample/custom/YouTube)
2. Preprocess video (extract frames at 1 FPS)
3. Extract visual features with MobileNetV3 (distributed)
4. Detect highlights using multi-signal analysis
5. Generate highlight reel (≤30 seconds)
6. Display results (with terminal playback if timg available)

### Run Tests

```bash
# Run tests sequentially
python tests/test_01_environment.py      # Ray + device detection
python tests/test_02_video_loading.py    # Parallel video loading
python tests/test_03_features.py         # Feature extraction (63+ FPS)
python tests/test_04_highlights.py       # Highlight detection
python tests/test_05_generation.py       # Video generation
python tests/test_06_pipeline.py         # End-to-end pipeline
```

---

## Project Structure

```
video-highlight-generator/
├── demo.py                        # Interactive CLI (1083 lines)
├── requirements.txt               # Python dependencies
├── src/
│   ├── pipeline.py                # Main orchestrator (380 lines)
│   ├── models/
│   │   └── feature_extractors.py  # Ray actors for ML inference
│   ├── features/
│   │   ├── highlight_detector.py  # Detection algorithms (558 lines)
│   │   └── video_generator.py     # FFmpeg wrapper
│   └── utils/
│       ├── ray_utils.py           # Cluster compatibility (144 lines)
│       ├── timg_video_player.py   # Terminal video playback
│       └── side_by_side_player.py # Comparison viewer
├── scripts/
│   ├── download_sample_videos.py  # Get demo videos
│   ├── preprocess_videos.py       # Batch preprocessing
│   └── cleanup.sh                 # Remove generated files
├── tests/                         # 6 comprehensive tests
└── data/                          # Local storage (or /mnt/cluster_storage on clusters)
```

---

## How It Works

**4-Phase Pipeline:**

1. **Preprocessing** - FFmpeg extracts frames (1 FPS) and audio
2. **Feature Extraction** - MobileNetV3 generates 576-dim visual features (distributed via Ray actors)
3. **Highlight Detection** - Multi-signal analysis (variance + novelty + motion) identifies peaks
4. **Video Generation** - FFmpeg extracts clips, adds transitions, concatenates to ≤30s

**Detection Algorithm:**
- Computes importance scores from visual features
- Uses adaptive thresholds based on video duration
- Detects peaks with SciPy local maxima
- Ranks highlights by importance score
- Enforces 30-second maximum duration

---

## Cluster Compatibility

The system runs on both local machines and Ray clusters without code changes.

**Automatic Features:**
- Environment detection (local vs cluster via `RAY_ADDRESS`)
- Storage path switching (`./data` → `/mnt/cluster_storage`)
- Headless OpenCV for worker nodes
- Graceful degradation (timg fallback to metadata display)
- Resource management (Ray handles CPU/GPU allocation)

**Cluster Test Results (Ray 2.47.0 + Tesla T4 GPUs):**
```
✅ test_01_environment.py - Ray initialization and device detection
✅ test_02_video_loading.py - Parallel video loading with Ray Data
✅ test_03_features.py - Distributed feature extraction (63+ FPS)
✅ test_04_highlights.py - Highlight detection with adaptive thresholds
✅ test_05_generation.py - Video highlight reel generation (11 clips)
✅ test_06_pipeline.py - End-to-end pipeline (15.1s total)
```

**Usage on Cluster:**
```bash
# Copy videos to cluster storage
cp video.mp4 /mnt/cluster_storage/raw/demo/

# Run (automatically detects cluster and uses cluster storage)
python demo.py
```

---

## Usage Examples

### Process Custom Video

```bash
python demo.py
# Select option 2 (Custom video)
# Enter path: /path/to/video.mp4
```

### Process YouTube Video

```bash
# Install yt-dlp first
pip install yt-dlp

python demo.py
# Select option 3 (YouTube URL)
# Enter URL: https://youtube.com/watch?v=...
```

### Batch Processing

```bash
# Preprocess all videos in data/raw/demo/
python scripts/preprocess_videos.py
```

### Cleanup Generated Files

```bash
bash scripts/cleanup.sh
```

---

## Configuration

The pipeline uses sensible defaults but can be customized:

**Pipeline Parameters:**
- `num_actors` - Number of Ray actors for parallel processing (default: 2)
- `target_fps` - Frame extraction rate (default: 1.0 FPS)
- `resolution` - Frame size for ML model (default: 224×224)

**Detection Parameters:**
- `variance_weight` - Visual diversity score weight (default: 0.4)
- `novelty_weight` - Uniqueness score weight (default: 0.3)
- `motion_weight` - Action intensity score weight (default: 0.3)

**Generation Parameters:**
- `clip_duration` - Individual clip length (default: 3.0s)
- `fade_duration` - Transition fade time (default: 0.5s)
- `max_duration` - Maximum highlight reel length (default: 30.0s)

## Technical Details

**Models:**
- MobileNetV3-small (pre-trained on ImageNet)
- 576-dimensional visual features
- Automatic device selection (CUDA > MPS > CPU)

**Algorithms:**
- Feature variance (visual diversity)
- Feature novelty (cosine distance from mean)
- Motion intensity (frame-to-frame difference)
- SciPy peak detection with adaptive thresholds

**Ray Patterns:**
- Actor pool for stateful workers
- Models loaded once per actor
- Distributed batch processing
- Automatic task distribution

## Resources

- [Ray Documentation](https://docs.ray.io/)
- [Ray Actors Guide](https://docs.ray.io/en/latest/ray-core/actors.html)
- [Ray Cluster Quickstart](https://docs.ray.io/en/latest/cluster/getting-started.html)
- [Module README](../README.md) - Learning path and context
