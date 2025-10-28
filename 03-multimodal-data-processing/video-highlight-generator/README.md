# Video Highlight Generator

> Automatically create engaging 30-second highlight reels from any video using AI-powered visual analysis and Ray distributed computing

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Ray](https://img.shields.io/badge/ray-2.x-orange.svg)](https://ray.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Demo Video

[![Video Highlight Generator Demo](https://img.youtube.com/vi/H2YptjwTEXc/maxresdefault.jpg)](https://www.youtube.com/watch?v=H2YptjwTEXc)

*Watch the complete demo showcasing real-time Ray cluster visualization, 4-phase pipeline execution, and side-by-side video comparison (2 minutes)*

---

## Overview

The Video Highlight Generator is a production-ready system that automatically identifies and extracts the most interesting moments from long-form videos. Using distributed computing with Ray and deep learning-based visual analysis, it processes videos in parallel across multiple workers and generates polished highlight reels suitable for social media, content curation, and video analysis applications.

**Primary Use Cases:**
- **Sports highlights** - Extract exciting moments from games and matches
- **Educational content** - Summarize lectures, tutorials, and presentations
- **Meeting recordings** - Identify key discussion points and decisions
- **Content creation** - Generate quick clips for social media promotion
- **Video analysis** - Automated content curation and quality assessment

---

## Key Features

### Intelligent Detection System

The system employs a sophisticated automatic detection algorithm that analyzes visual features to identify highlight-worthy moments without manual configuration:

- **Visual Feature Analysis** - Uses MobileNetV3 neural network to extract 1280-dimensional feature vectors from each video frame
- **Multi-Signal Scoring** - Combines three importance metrics:
  - *Feature Variance* - Measures visual diversity and scene changes
  - *Feature Novelty* - Identifies unique and unusual content
  - *Motion Intensity* - Detects action-heavy sequences
- **Adaptive Clip Durations** - Automatically determines optimal clip length (2-10 seconds) based on content characteristics
- **Smart Threshold Selection** - Adjusts detection sensitivity based on video duration to ensure appropriate highlight density
- **Quality-Based Ranking** - Orders detected highlights by importance score to prioritize the best moments
- **30-Second Maximum** - Enforces duration constraint perfect for social media platforms

### Distributed Processing with Ray

Ray's distributed computing framework enables efficient parallel processing and scales from laptop to production cluster:

- **Parallel Frame Extraction** - Distributes video preprocessing across Ray actors for faster I/O
- **Actor-Based Architecture** - Creates stateful workers that load models once and process multiple batches
- **GPU Acceleration** - Automatically utilizes available GPUs (CUDA or MPS on Apple Silicon) for feature extraction
- **Efficient Batch Processing** - Handles multiple videos in sequence or parallel depending on cluster resources
- **Real-Time Progress Monitoring** - Provides live feedback on processing status across all workers
- **Horizontal Scalability** - Seamlessly scales from single machine to multi-node cluster without code changes

### Production-Ready Implementation

Built with real-world deployment considerations and tested on production workloads:

- **Automatic Analysis** - No manual parameter tuning required; system adapts to different video characteristics
- **Robust Error Handling** - Comprehensive error checking with informative messages for troubleshooting
- **Checkpoint Support** - Saves intermediate results for recovery from failures in long processing runs
- **Resource-Aware Scheduling** - Ray automatically manages CPU/GPU allocation across workers
- **Tested Hardware** - Validated on M4 MacBook Pro with Apple Silicon and standard x86 Linux systems

### Cluster Compatibility

The system seamlessly runs on both local machines and Ray clusters without code changes:

- **Automatic Environment Detection** - Detects cluster mode via `RAY_ADDRESS` environment variable or runtime connection
- **Cluster Storage Integration** - Uses `/mnt/cluster_storage` on clusters, `./data` locally via `get_storage_path()` utility
- **Distributed Execution** - Tasks and actors automatically distributed across cluster nodes
- **Headless OpenCV** - Uses `opencv-python-headless` for compatibility with headless worker nodes
- **Terminal Video Playback** - Automatic fallback from timg playback to metadata display in headless environments
- **Resource Management** - Ray handles CPU/GPU allocation without manual configuration
- **Tested on Anyscale** - Validated on Ray 2.47.0 with Tesla T4 GPUs and multi-node clusters

**Test Results on Ray Cluster:**
- ✅ test_01_environment.py - Ray initialization and device detection
- ✅ test_02_video_loading.py - Parallel video loading with Ray Data
- ✅ test_03_features.py - Distributed feature extraction with 63+ FPS
- ✅ test_04_highlights.py - Highlight detection with adaptive thresholds
- ✅ test_05_generation.py - Video highlight reel generation (3 videos, 11 clips total)
- ✅ test_06_pipeline.py - End-to-end pipeline (15.1s total time)

---

## Architecture

The system implements a 4-phase pipeline that processes videos from raw input to final highlight reel:

```
┌─────────────────────────────────────────────────────────────┐
│                     VIDEO INPUT (MP4)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         PHASE 1: PREPROCESSING (FFmpeg + Ray)               │
│  • Extract frames at target FPS (1.0 FPS default)           │
│  • Resize to model input size (224×224)                     │
│  • Extract audio for future enhancements                    │
│  • Distribute extraction across Ray workers                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│    PHASE 2: FEATURE EXTRACTION (MobileNetV3 + Ray Actors)   │
│  • Parallel processing with 2+ Ray actors                   │
│  • Extract 1280-dim visual features per frame               │
│  • GPU acceleration when available (CUDA/MPS)               │
│  • Typical speed: 30-120 FPS on modern hardware             │
│  • Models loaded once per actor for efficiency              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│       PHASE 3: HIGHLIGHT DETECTION (Intelligent Auto)       │
│  • Compute importance scores:                               │
│    - Feature variance (visual diversity)                    │
│    - Feature novelty (unique scenes)                        │
│    - Motion intensity (action level)                        │
│  • Auto-detect peaks using adaptive thresholds              │
│  • Determine optimal clip durations (2-10s)                 │
│  • Rank by importance scores                                │
│  • Apply 30-second maximum constraint                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│      PHASE 4: VIDEO GENERATION (FFmpeg + Transitions)       │
│  • Extract clips at detected timestamps                     │
│  • Add smooth fade transitions (0.5s)                       │
│  • Enforce 30-second maximum duration                       │
│  • Concatenate into final highlight reel                    │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              OUTPUT (≤30s MP4 + Metadata)                   │
│  • Highlight video with best moments                        │
│  • JSON with timestamps and scores                          │
│  • Processing statistics and metrics                        │
└─────────────────────────────────────────────────────────────┘
```

### Phase Details

**Phase 1: Preprocessing**
- Uses FFmpeg to extract video frames at specified frame rate (default 1 FPS)
- Resizes frames to 224×224 pixels to match neural network input requirements
- Extracts audio track for potential future audio-based highlight detection
- Leverages Ray for parallel frame extraction across multiple workers

**Phase 2: Feature Extraction**
- Employs MobileNetV3-small convolutional neural network pre-trained on ImageNet
- Extracts 1280-dimensional feature vectors representing visual content of each frame
- Uses Ray actors to maintain stateful workers with loaded models for efficiency
- Automatically detects and utilizes GPUs (CUDA or Apple MPS) when available
- Processes frames in batches to maximize throughput

**Phase 3: Highlight Detection**
- Analyzes feature vectors to compute three importance signals:
  - *Variance Score*: Measures how visually diverse the frame is compared to neighbors
  - *Novelty Score*: Quantifies how unique the frame is relative to the entire video
  - *Motion Score*: Estimates activity level based on feature changes between frames
- Combines signals using weighted sum (configurable weights: 0.4 variance, 0.3 novelty, 0.3 motion)
- Applies peak detection algorithm to identify local maxima in importance scores
- Adapts threshold percentile based on video duration (shorter videos use stricter thresholds)
- Determines clip duration based on importance magnitude and neighboring peak proximity

**Phase 4: Video Generation**
- Uses FFmpeg to extract video segments at detected highlight timestamps
- Applies fade-in and fade-out transitions (0.5 seconds each) for smooth viewing experience
- Enforces 30-second maximum duration through two-stage reduction:
  - First stage: Proportionally reduce all clip durations
  - Second stage: Selectively remove lowest-scored clips if still over limit
- Concatenates clips into final MP4 file with original video codec and quality

---

## Prerequisites

### System Requirements

- **Python 3.12** - Required for compatibility with latest Ray and PyTorch versions
- **Memory** - 8GB RAM minimum, 16GB recommended for processing longer videos
- **FFmpeg 4.x or later** - Required for video processing operations (frame extraction, clip generation)
- **GPU (Optional)** - NVIDIA GPU with CUDA support or Apple Silicon with MPS for accelerated feature extraction

### Tested Platforms

- **macOS (Local)** - Full support on both Intel and Apple Silicon (M1/M2/M3/M4)
- **Linux (Local or Ray Cluster)** - Tested on Ubuntu 20.04+ with CUDA support
- **Windows** - Supported via WSL2 (Windows Subsystem for Linux recommended)

### Deployment Options

The system supports two deployment modes:

**Local Mode** - Single machine execution:
- Runs on Mac, Linux, or Windows
- Suitable for development and small-scale processing
- Ray starts local cluster automatically

**Ray Cluster Mode** - Distributed execution:
- Connects to existing Ray cluster automatically
- Scales across multiple nodes for production workloads
- Same code works in both modes without modification

### Hardware Acceleration

The system automatically detects and uses the best available device:

**CUDA (NVIDIA GPUs)** - Highest performance:
- Supports T4, V100, A100, RTX series GPUs
- Typical speed: ~180 FPS feature extraction
- Automatic detection on Linux systems

**MPS (Apple Silicon)** - Optimized for Mac:
- M1, M2, M3, M4 chip support
- Typical speed: ~120 FPS feature extraction
- Automatic detection on macOS

**CPU (Fallback)** - Works everywhere:
- All platforms supported
- Typical speed: ~30 FPS feature extraction
- Automatic fallback when GPU unavailable

**Memory and Storage**:
- **Memory usage**: 2-4GB RAM for typical 10-minute videos
- **Storage**: Approximately 2-3x video file size for intermediate processing files
- **Scalability**: Horizontal scaling across cluster nodes for larger workloads

---

## Installation

### 1. Environment Setup

```bash
# Navigate to project directory
cd video-highlight-generator

# Create virtual environment with Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate

# Alternative: Use uv for faster installation
uv venv --python 3.12
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install FFmpeg

FFmpeg is required for all video processing operations:

```bash
# macOS (using Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg

# Verify installation
ffmpeg -version
```

### 3. (Optional) Install timg for Terminal Video Playback

For terminal video playback support, install timg:

```bash
# macOS (using Homebrew)
brew install timg

# Ubuntu/Debian (requires build from source)
# Visit: https://github.com/hzeller/timg

# Verify installation
timg --version
```

**Terminal Video Playback Features:**
- Real video playback in terminal using iTerm2/Kitty/Sixel graphics protocols
- Automatic fallback to video metadata display in headless environments
- Integrated in test_06_pipeline.py for immediate results viewing
- Optional - system works without it, showing file paths instead

### 4. Download Sample Videos

Download pre-configured test videos to verify installation:

```bash
python scripts/download_sample_videos.py
```

This downloads three Creative Commons licensed videos (~50MB total):
- **For Bigger Blazes** (15 seconds) - Quick test for pipeline validation
- **Big Buck Bunny** (10 minutes) - Medium-length video for realistic testing
- **Elephants Dream** (11 minutes) - Full-length test for performance evaluation

### 4. Ray Cluster Setup (Optional)

For production deployments on Ray clusters:

```bash
# The system automatically detects and connects to existing Ray clusters
# No code changes required - same scripts work on both local and cluster

# If Ray versions differ, upgrade to match cluster version:
pip install --upgrade ray==<cluster_version>

# Example: Upgrade to Ray 2.47.0
pip install --upgrade ray==2.47.0
```

**Important**: Ensure your local Ray version matches the cluster version to avoid connection errors.

### 5. Verify Installation

Run the test suite to confirm all components are working correctly:

```bash
# Run environment verification (works on both local and cluster)
python tests/test_01_environment.py

# Run video loading test
python tests/test_02_video_loading.py

# Run feature extraction test
python tests/test_04_features.py

# Run full pipeline test
python tests/test_07_pipeline.py
```

---

## Usage

### Interactive Demo

The easiest way to get started is using the interactive demo:

```bash
python demo.py
```

The demo provides a menu-driven interface with options to:
1. Process one of the downloaded sample videos
2. Process a custom video file from your filesystem
3. Process a video from a YouTube URL (requires `yt-dlp` installation)
4. View previously generated highlights

### Command-Line Interface

For automated workflows and scripting, use the direct pipeline interface:

```bash
# Process a single video with default settings
python -m src.pipeline --input data/raw/demo/big_buck_bunny.mp4

# Specify custom output directory
python -m src.pipeline \
    --input path/to/video.mp4 \
    --output results/

# Adjust number of Ray actors for feature extraction
python -m src.pipeline \
    --input video.mp4 \
    --num-actors 4

# Process with custom detection parameters
python -m src.pipeline \
    --input video.mp4 \
    --variance-weight 0.5 \
    --novelty-weight 0.3 \
    --motion-weight 0.2
```

### YouTube Video Processing

To process videos directly from YouTube:

```bash
# Install yt-dlp dependency
pip install yt-dlp
# or: brew install yt-dlp

# Run demo and select YouTube option
python demo.py
# Choose option 3 and paste YouTube URL
```

**YouTube Processing Features:**
- Automatic download of videos under 30 minutes
- Format selection (prefers 720p for balance of quality and processing speed)
- Progress indication during download
- Automatic cleanup of downloaded files after processing

### Terminal Video Playback

The system supports real video playback in terminal environments with `timg`:

**Local Environment (with timg installed):**
```bash
# Run pipeline test to see terminal video playback in action
python tests/test_06_pipeline.py

# Videos play directly in terminal using graphics protocols
# Supports iTerm2, Kitty, and terminals with Sixel support
```

**Cluster/Headless Environment (without timg):**
- Automatically falls back to displaying video metadata
- Shows resolution, codec, duration, and file size
- Provides file path for manual download
- No configuration needed - graceful degradation

**Video Playback Output:**
- ✅ Local: Real video frames rendered in terminal
- ✅ Cluster: Video metadata + download path
- ✅ Both: File verification and statistics

---

## Project Structure

```
video-highlight-generator/
├── src/
│   ├── pipeline.py                    # Main orchestrator (4-phase pipeline)
│   ├── models/
│   │   └── feature_extractors.py      # Ray actors for ML inference
│   ├── features/
│   │   ├── highlight_detector.py      # Detection algorithms
│   │   └── video_generator.py         # FFmpeg wrapper for clip generation
│   └── utils/
│       ├── timg_video_player.py       # Terminal video playback
│       └── side_by_side_player.py     # Comparison viewer
├── scripts/
│   ├── download_sample_videos.py      # Download demo videos
│   └── preprocess_videos.py           # Batch preprocessing utility
├── tests/                             # Comprehensive test suite
│   ├── test_01_environment.py         # Verify dependencies
│   ├── test_02_video_loading.py       # Test FFmpeg integration
│   ├── test_04_features.py            # Test feature extraction
│   ├── test_05_highlights.py          # Test detection algorithm
│   ├── test_06_generation.py          # Test video generation
│   └── test_07_pipeline.py            # End-to-end integration test
├── data/
│   ├── raw/demo/                      # Sample input videos
│   └── pipeline/                      # Processing outputs and metadata
├── demo.py                            # Interactive CLI demo
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

### Key Components

**`src/pipeline.py`** (Main Orchestrator)
- `VideoHighlightPipeline` class coordinates all processing phases
- Methods: `initialize_ray()`, `preprocess_video()`, `extract_features()`, `detect_highlights()`, `generate_video()`, `run()`
- Handles Ray cluster initialization/cleanup, progress callbacks, error recovery

**`src/models/feature_extractors.py`** (Distributed ML Inference)
- `VisualFeatureExtractor` Ray actor decorated with `@ray.remote`
- Loads MobileNetV3-small model once per actor for efficiency
- Supports automatic GPU detection (CUDA or Apple MPS)
- Factory function `create_feature_extractor_pool()` for actor management

**`src/features/highlight_detector.py`** (ML Algorithms)
- `HighlightDetector` class implements scoring and peak detection algorithms
- Methods: `compute_variance_score()`, `compute_novelty_score()`, `compute_motion_score()`, `detect_highlights()`
- Configurable weights for multi-signal combination
- Adaptive threshold selection based on video characteristics

**`src/features/video_generator.py`** (Video Assembly)
- `VideoHighlightGenerator` class wraps FFmpeg operations
- Methods: `extract_clips()`, `concatenate_clips()`, `add_transitions()`
- Enforces 30-second constraint through two-stage duration reduction
- Preserves original video quality and codec settings

---

## Configuration

### Detection Parameters

Customize highlight detection behavior through configuration options:

```python
from src.pipeline import VideoHighlightPipeline

pipeline = VideoHighlightPipeline()

# Adjust importance signal weights (must sum to 1.0)
config = {
    'variance_weight': 0.4,   # Visual diversity importance
    'novelty_weight': 0.3,    # Uniqueness importance
    'motion_weight': 0.3      # Action level importance
}

results = pipeline.run(
    video_path='input.mp4',
    config=config
)
```

### Ray Configuration

Control distributed computing resources:

```python
# Initialize Ray with specific resources
pipeline.initialize_ray(
    num_cpus=8,           # CPU cores for Ray workers
    num_gpus=1            # GPUs for feature extraction
)

# Specify number of feature extraction actors
results = pipeline.extract_features(
    preprocessed_dir='data/pipeline/frames/',
    num_actors=4          # Parallel workers
)
```

### Performance Tuning

Optimize for your specific hardware:

- **CPU-bound systems**: Reduce `num_actors` to 1-2 to avoid resource contention
- **GPU systems**: Increase `num_actors` to maximize GPU utilization (typically 2-4 actors per GPU)
- **Memory-constrained**: Lower frame extraction rate (`fps` parameter) to reduce memory usage
- **Storage-constrained**: Enable automatic cleanup of intermediate files

---

## Advanced Usage

### Batch Processing

Process multiple videos sequentially:

```bash
python scripts/preprocess_videos.py \
    --input-dir videos/ \
    --output-dir highlights/ \
    --num-actors 4
```

### Custom Detection Algorithms

Extend the detection system with custom algorithms:

```python
from src.features.highlight_detector import HighlightDetector

class CustomDetector(HighlightDetector):
    def compute_custom_score(self, features, timestamps):
        # Implement your scoring logic
        scores = your_algorithm(features)
        return scores

# Use custom detector in pipeline
detector = CustomDetector()
highlights = detector.detect_highlights(
    features=extracted_features,
    timestamps=frame_timestamps
)
```

### Integration with Existing Workflows

Integrate as a module in larger systems:

```python
from src.pipeline import VideoHighlightPipeline

def process_video_library(video_paths):
    pipeline = VideoHighlightPipeline()
    pipeline.initialize_ray()

    try:
        results = []
        for video_path in video_paths:
            result = pipeline.run(video_path)
            results.append(result)
        return results
    finally:
        pipeline.shutdown_ray()
```

---

## Performance Characteristics

### Processing Speed

Typical performance on different hardware configurations:

**M4 MacBook Pro (Apple Silicon)**
- 10-minute video: ~28 seconds total processing time
- Feature extraction: ~120 FPS with MPS acceleration
- End-to-end throughput: ~21x real-time speed

**Linux with NVIDIA RTX 3080**
- 10-minute video: ~20 seconds total processing time
- Feature extraction: ~180 FPS with CUDA
- End-to-end throughput: ~30x real-time speed

**CPU-only (8-core Intel i7)**
- 10-minute video: ~90 seconds total processing time
- Feature extraction: ~30 FPS
- End-to-end throughput: ~7x real-time speed

### Scalability

The system scales horizontally across multiple machines using Ray's distributed runtime:

- **Single machine**: Processes 1 video at a time with multiple workers
- **Small cluster (4 nodes)**: Processes 4 videos in parallel, or 1 video ~4x faster
- **Large cluster (16+ nodes)**: Suitable for production workloads with hundreds of videos

### Resource Usage

Typical resource consumption for 10-minute 1080p video:

- **Memory**: 2-4 GB RAM during processing
- **Storage**: 500-800 MB for intermediate files (frames, features)
- **GPU Memory**: 1-2 GB when using GPU acceleration
- **Network**: Minimal (only for distributed Ray clusters)

---

## Troubleshooting

### Common Issues

**Issue: "FFmpeg not found"**
- **Solution**: Install FFmpeg using your system package manager (see Installation section)
- **Verify**: Run `ffmpeg -version` to confirm installation

**Issue: "Out of memory during feature extraction"**
- **Solution**: Reduce number of Ray actors (`--num-actors 1` or `2`)
- **Alternative**: Lower frame extraction rate to process fewer frames

**Issue: "No highlights detected"**
- **Solution**: Video may lack sufficient visual diversity
- **Check**: View importance scores in output JSON to understand detection behavior
- **Adjust**: Lower detection thresholds or adjust signal weights

**Issue: "GPU not being utilized"**
- **Solution**: Verify PyTorch can access GPU: `python -c "import torch; print(torch.cuda.is_available())"`
- **Check**: Ensure CUDA drivers are installed for NVIDIA GPUs
- **Note**: Apple Silicon uses MPS instead of CUDA (automatic detection)

**Issue: "Ray version mismatch" when connecting to cluster**
- **Error**: `RuntimeError: Version mismatch: The cluster was started with Ray: X.X.X`
- **Solution**: Upgrade your local Ray to match cluster version: `pip install --upgrade ray==X.X.X`
- **Verify**: Check cluster version with `ray status` on cluster node

**Issue: "When connecting to an existing cluster, num_cpus and num_gpus must not be provided"**
- **Status**: This issue is automatically handled by the `safe_ray_init()` function
- **Verify**: Ensure you're using the latest code with `src/utils/ray_utils.py`

### Debug Mode

Enable verbose logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from src.pipeline import VideoHighlightPipeline
pipeline = VideoHighlightPipeline()
# Detailed logs will be printed during execution
```

### Getting Help

If you encounter issues:
1. Check the test suite: `python tests/test_01_environment.py`
2. Review error messages carefully - they include specific guidance
3. Check FFmpeg installation: `ffmpeg -version`
4. Verify Python version: `python --version` (must be 3.12)
5. Open an issue on GitHub with error logs and system information

---

## Technical Details

### Algorithm Details

**Multi-Signal Importance Scoring**

The system combines three complementary signals to identify highlight-worthy moments:

1. **Variance Score (Visual Diversity)**
   - Computes standard deviation of feature vectors in sliding temporal window
   - High variance indicates visually diverse content (scene changes, action sequences)
   - Window size: Configurable (default 5 frames ≈ 5 seconds at 1 FPS)

2. **Novelty Score (Uniqueness)**
   - Measures cosine distance from frame feature to mean of all features
   - High novelty indicates unusual or unique visual content
   - Effective for identifying special moments (goals, celebrations, dramatic scenes)

3. **Motion Score (Activity Level)**
   - Computes Euclidean distance between consecutive frame features
   - High motion indicates rapid visual changes (sports action, camera movement)
   - Smoothed using moving average to reduce noise

**Combined Score Calculation**
```
importance_score[i] = w1 * variance[i] + w2 * novelty[i] + w3 * motion[i]
```
Default weights: w1=0.4, w2=0.3, w3=0.3 (tuned empirically on diverse video corpus)

**Peak Detection**

Uses scipy's `find_peaks` algorithm with adaptive parameters:
- Minimum peak distance: 2 seconds (prevents overlapping highlights)
- Minimum peak height: Percentile-based threshold (adapts to video content)
- Threshold percentile: 65-75% depending on video duration (shorter videos use stricter thresholds)

**Duration Constraint Enforcement**

Two-stage reduction strategy to meet 30-second maximum:
1. **Proportional Reduction**: Scale all clip durations by ratio (total_duration / 30.0)
2. **Selective Removal**: If still over limit, iteratively remove lowest-scored clips

This ensures the most important highlights are always included within the time budget.

### Model Information

**MobileNetV3-Small**
- Architecture: Efficient convolutional neural network designed for mobile devices
- Parameters: ~2.5 million
- Input size: 224×224×3 RGB images
- Output: 1280-dimensional feature vector from penultimate layer
- Training: Pre-trained on ImageNet (1000 classes, 1.2M images)
- Inference speed: 30-180 FPS depending on hardware

The choice of MobileNetV3 balances accuracy with computational efficiency, enabling real-time processing on commodity hardware while maintaining sufficient discriminative power for highlight detection.

---

## Limitations and Future Work

### Current Limitations

- **Visual-only analysis**: Does not consider audio features (speech, music, crowd noise)
- **Fixed duration**: Hardcoded 30-second maximum (could be made configurable)
- **Single video input**: No support for multi-camera or multi-angle videos
- **No user feedback**: Cannot learn from user preferences or corrections
- **Limited temporal context**: 1 FPS frame rate may miss very short interesting moments

### Planned Enhancements

- **Audio analysis**: Integrate audio-based excitement detection (volume spikes, speech patterns)
- **Multi-modal fusion**: Combine visual and audio signals for improved detection
- **User feedback loop**: Allow users to rate highlights and retrain detection model
- **Temporal action detection**: Use video transformers (X3D, VideoMAE) for better understanding
- **Cloud deployment**: Add Ray Serve integration for production API deployment
- **Configurable output**: Support variable output durations (15s, 30s, 60s)

---

## Contributing

Contributions are welcome! Areas where contributions would be particularly valuable:

- **Audio analysis**: Implement audio-based highlight detection
- **Additional datasets**: Test on diverse video types and add benchmark results
- **Performance optimization**: Improve processing speed and memory efficiency
- **Documentation**: Add tutorials, examples, and architectural guides
- **Testing**: Expand test coverage and add edge case handling

Please open an issue before starting work on major changes to discuss approach and ensure alignment with project direction.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- **Ray Team** - For building an excellent distributed computing framework
- **PyTorch Team** - For the deep learning foundation
- **FFmpeg Project** - For powerful video processing capabilities
- **Blender Foundation** - For providing Creative Commons test videos (Big Buck Bunny, Elephants Dream)

---

## Citation

If you use this project in your research or production systems, please cite:

```
@software{video_highlight_generator,
  title = {Video Highlight Generator with Ray},
  author = {Ray for Developers},
  year = {2025},
  url = {https://github.com/debnsuma/ray-for-developers}
}
```
