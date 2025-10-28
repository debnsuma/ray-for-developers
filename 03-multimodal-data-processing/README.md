# 03. Multimodal Data Processing with Ray

Build scalable pipelines for processing video, images, and multimodal datasets using Ray's distributed computing framework.

## Overview

This module demonstrates building production-ready data pipelines that scale from a single machine to multi-node Ray clusters. Learn practical patterns for distributed video processing, feature extraction with deep learning models, and intelligent data analysis using Ray Core and Ray Actors.

## Project: AI-Powered Video Highlight Generator

**A complete, production-ready system** that automatically creates highlight reels from long-form videos using distributed computing and machine learning.

### [🎬 Video Highlight Generator](./video-highlight-generator/)

An end-to-end implementation demonstrating:
- **Ray Actors** for stateful distributed ML inference
- **MobileNetV3** for efficient visual feature extraction (576-dim features)
- **Multi-signal detection** combining variance, novelty, and motion analysis
- **Cluster compatibility** - runs on Mac, Linux, and Ray clusters without code changes
- **Terminal video playback** with automatic fallback for headless environments
- **YouTube support** for processing videos directly from URLs
- **Interactive CLI** with real-time progress monitoring

**Key Features:**
- ✅ Tested on Ray 2.47.0 clusters with Tesla T4 GPUs
- ✅ Cluster storage integration (`/mnt/cluster_storage`)
- ✅ Headless OpenCV for worker node compatibility
- ✅ 63+ FPS feature extraction on distributed workers
- ✅ 6 comprehensive tests covering all pipeline phases

**Perfect for learning:** Combines Ray fundamentals with practical ML and video processing patterns.

**[→ Start the project](./video-highlight-generator/README.md)**

## What You'll Learn

This project covers practical Ray patterns for building scalable ML pipelines:

### 1. Distributed Computing with Ray
- **Ray Actors** - Stateful workers for ML model inference
- **Ray Initialization** - Cluster detection and resource management
- **Cluster Storage** - Environment-aware path handling
- **Worker Distribution** - Automatic task distribution across nodes

### 2. Video Processing at Scale
- **FFmpeg Integration** - Frame extraction and video manipulation
- **Ray Data** - Parallel video loading and preprocessing
- **Batch Processing** - Efficient frame-level operations
- **Headless Compatibility** - OpenCV in server environments

### 3. Machine Learning Pipeline
- **Feature Extraction** - MobileNetV3 for visual embeddings (576-dim)
- **Distributed Inference** - Ray Actor pool pattern for parallel processing
- **Device Management** - CUDA/MPS/CPU detection and selection
- **Model Optimization** - Single load per actor for efficiency

### 4. Intelligent Detection Algorithms
- **Multi-Signal Analysis** - Variance, novelty, and motion scoring
- **Adaptive Thresholds** - Video duration-aware detection
- **Peak Detection** - SciPy-based local maxima identification
- **Automatic Mode** - Parameter-free highlight detection

### 5. Production Patterns
- **Environment Detection** - Automatic local vs cluster mode
- **Graceful Degradation** - Fallback strategies for missing dependencies
- **Progress Monitoring** - Real-time pipeline status updates
- **Comprehensive Testing** - 6-phase test suite for validation

## Prerequisites

- **Python 3.12** - Required for the project
- **Ray 2.47.0** - Installed via pip/uv (see main README)
- **PyTorch** - For MobileNetV3 model inference
- **FFmpeg** - System-level dependency for video processing
- **Basic Ray knowledge** - Understanding of tasks and actors helps
- **Optional:** GPU (CUDA/MPS) or Ray cluster access for faster processing

## Repository Structure

```
03-multimodal-data-processing/
├── README.md                          # This file
└── video-highlight-generator/         # Complete implementation
    ├── README.md                      # Comprehensive project documentation
    ├── demo.py                        # Interactive CLI (1083 lines)
    ├── requirements.txt               # Python dependencies
    ├── src/                           # Core implementation
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
    │   ├── download_sample_videos.py  # Get demo videos (~50MB)
    │   ├── preprocess_videos.py       # Batch preprocessing
    │   └── cleanup.sh                 # Remove generated files
    ├── tests/                         # Comprehensive test suite
    │   ├── test_01_environment.py     # Ray + device detection
    │   ├── test_02_video_loading.py   # Ray Data integration
    │   ├── test_03_features.py        # Feature extraction
    │   ├── test_04_highlights.py      # Detection algorithms
    │   ├── test_05_generation.py      # Video generation
    │   ├── test_06_pipeline.py        # End-to-end pipeline
    │   └── test_youtube_download.py   # YouTube support
    ├── data/                          # Local data storage
    │   ├── raw/demo/                  # Input videos
    │   ├── processed/demo/            # Preprocessed frames
    │   ├── features/demo/             # Extracted features
    │   ├── highlights/demo/           # Detection results
    │   ├── output/demo/               # Generated videos
    │   └── pipeline/                  # Pipeline outputs
    ├── docs/                          # Additional documentation
    └── models/                        # Pre-trained models cache
```

**Note:** On Ray clusters, the `data/` directory is replaced with `/mnt/cluster_storage/` automatically via `get_storage_path()` utility.

## Quick Start

```bash
# Navigate to project
cd 03-multimodal-data-processing/video-highlight-generator

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (system requirement)
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg

# Download sample videos (~50MB)
python scripts/download_sample_videos.py

# Run interactive demo
python demo.py

# Or run tests sequentially
python tests/test_01_environment.py
python tests/test_02_video_loading.py
python tests/test_03_features.py
python tests/test_04_highlights.py
python tests/test_05_generation.py
python tests/test_06_pipeline.py
```

**What the demo does:**
1. Presents menu to select video source (sample/custom/YouTube)
2. Preprocesses video (frame extraction at 1 FPS)
3. Extracts visual features using MobileNetV3 (distributed across Ray actors)
4. Detects highlights using multi-signal analysis
5. Generates highlight reel (≤30 seconds)
6. Shows results with terminal playback (if timg available)

## Use Cases

This implementation serves as a foundation for various video analysis applications:

- **Sports Analytics** - Generate highlight reels from game footage
- **Educational Content** - Extract key moments from lecture recordings
- **Meeting Summarization** - Identify important discussion segments
- **Content Creation** - Generate social media clips from long-form content
- **Media Monitoring** - Detect notable events in broadcast content
- **Event Recaps** - Create summary videos from conferences or events

## Technical Highlights

**4-Phase Pipeline Architecture:**
1. **Preprocessing** - FFmpeg frame extraction (1 FPS), audio extraction
2. **Feature Extraction** - Distributed MobileNetV3 inference via Ray actors
3. **Highlight Detection** - Multi-signal analysis (variance + novelty + motion)
4. **Video Generation** - FFmpeg clip extraction and concatenation

**Performance Metrics (Ray Cluster with Tesla T4 GPUs):**
- Feature extraction: 63+ FPS on distributed workers
- End-to-end pipeline: 15.1s for 16-second video
- Scalability: Linear speedup with additional Ray actors
- Cluster storage: Automatic `/mnt/cluster_storage` integration

**Production-Ready Features:**
- Automatic environment detection (local vs cluster)
- Graceful degradation for missing dependencies
- Comprehensive error handling and logging
- Progress monitoring with callbacks
- Extensive test coverage (6 test files)

## Resources

- [Ray Documentation](https://docs.ray.io/)
- [Ray Actors Guide](https://docs.ray.io/en/latest/ray-core/actors.html)
- [Ray Cluster Quickstart](https://docs.ray.io/en/latest/cluster/getting-started.html)
- [Project README](./video-highlight-generator/README.md) - Full documentation

## Next Steps

After completing this project, explore:
- **Module 01** - Ray fundamentals (tasks, actors, distributed patterns)
- **Module 02** - Distributed training with Ray Train
- **Module 04** - Model serving with Ray Serve
- **Module 05** - Reinforcement learning with RLlib

---

**Status:** ✅ Production-ready implementation with full cluster support
