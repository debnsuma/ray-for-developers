# 🎬 Video Highlight Generator

> **Automatically create engaging 30-second highlight reels from any video using AI-powered visual analysis and Ray distributed computing**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Ray](https://img.shields.io/badge/ray-2.x-orange.svg)](https://ray.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎥 Live Demo

[![Video Highlight Generator Demo](https://img.youtube.com/vi/H2YptjwTEXc/maxresdefault.jpg)](https://www.youtube.com/watch?v=H2YptjwTEXc)

**Watch the complete demo** showing:
- ✨ Real-time Ray cluster visualization with worker monitoring
- 📊 4-phase pipeline execution (preprocessing → features → detection → generation)
- 🎬 Processing 10-minute Big Buck Bunny video in 28 seconds
- ⚡ Parallel processing across Ray actors
- 🎥 Side-by-side video comparison with the generated 30-second highlight reel

*Click to watch on YouTube (2 minutes)*

---

Perfect for:
- 🏀 **Sports highlights** - Extract exciting moments from games
- 📚 **Educational content** - Summarize lectures and tutorials
- 💼 **Meeting recordings** - Identify key discussion points
- 🎥 **Content creators** - Quick social media clips
- 🎯 **Video analysis** - Automated content curation

---

## ✨ Key Features

### 🎯 Intelligent Detection (Auto Mode)
- **Visual feature analysis** using MobileNetV3
- **Adaptive clip durations** (2-10 seconds per highlight)
- **Smart threshold selection** based on video length
- **Quality-based ranking** - best moments first
- **30-second maximum** - perfect for social media

### ⚡ Distributed Processing with Ray
- **Parallel frame extraction** across Ray actors
- **GPU-accelerated** feature extraction (when available)
- **Efficient batch processing** - handle multiple videos
- **Real-time progress** monitoring
- **Scales from laptop to cluster**

### 🎨 Beautiful Terminal UI
- **Live processing dashboard** with Ray cluster visualization
- **Real-time video playback** in terminal (iTerm2/Kitty)
- **Side-by-side comparison** with play/pause controls
- **Dark theme optimized** with soothing colors
- **Intuitive controls** for seamless experience

### 🚀 Production Ready
- **Automatic video analysis** - no manual configuration needed
- **Robust error handling** with informative messages
- **Checkpoint support** for long processing runs
- **Resource-aware** scheduling
- **Battle-tested** on M4 MacBook Pro

---

## 🏗️ Architecture

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
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│    PHASE 2: FEATURE EXTRACTION (MobileNetV3 + Ray Actors)   │
│  • Parallel processing with 2+ Ray actors                   │
│  • Extract 1280-dim visual features per frame               │
│  • GPU acceleration when available                          │
│  • Typical speed: 30-120 FPS                                │
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

---

## 📋 Prerequisites

### System Requirements
- **Python 3.12**
- **8GB+ RAM** (16GB recommended)
- **FFmpeg 4.x+** (for video processing)
- **Optional:** CUDA GPU for faster feature extraction

### Tested Platforms
- ✅ **M4 MacBook Pro** (Apple Silicon) - Full support
- ✅ **macOS** (Intel & Apple Silicon)
- ✅ **Linux** (Ubuntu 20.04+)
- ✅ **Windows** (with WSL2 recommended)

### Terminal Requirements for Video Playback
- **iTerm2** (macOS) - Best experience
- **Kitty** (cross-platform) - Full support
- **Sixel-capable terminals** - Supported

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository (if not already done)
cd video-highlight-generator

# Create virtual environment with Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate

# Or use uv (faster)
uv venv --python 3.12
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows (use Chocolatey)
choco install ffmpeg
```

### 3. Download Sample Videos

```bash
python scripts/download_sample_videos.py
```

This downloads 3 demo videos (~50MB total):
- **For Bigger Blazes** (15 seconds) - Quick test
- **Big Buck Bunny** (10 minutes) - Medium video
- **Elephants Dream** (11 minutes) - Full-length test

### 3a. YouTube Support (Optional)

You can also process videos directly from YouTube URLs:

```bash
# Install yt-dlp
pip install yt-dlp
# or: brew install yt-dlp

# Run demo and select option 4 for YouTube URL
python demo_enhanced.py
```

**Features:**
- ✅ Downloads videos < 30 minutes
- ✅ Validates duration before downloading
- ✅ Shows video metadata (title, duration)
- ✅ Downloads best quality MP4 with audio
- ✅ Automatically processes through pipeline

See [YOUTUBE_SUPPORT.md](./YOUTUBE_SUPPORT.md) for details.

### 4. Run the Demo

```bash
python demo.py
```

**What you'll see:**
1. 📹 **Video selection menu** - Choose from 3 sample videos
2. ⚙️ **Auto-configuration** - AI determines optimal settings
3. 🎬 **Live processing dashboard** - Real-time Ray visualization
4. 📊 **Pipeline summary** - Detailed metrics and timing
5. 🎥 **Video playback** - Side-by-side comparison in terminal

**Demo output:**
```
🎬 Video Highlight Generator - Enhanced Demo
╚═══════════════════════════════════════════════╝

Features:
  ✨ Real-time Ray worker visualization
  📊 Parallel task execution monitoring
  🎬 Side-by-side video comparison
  ⚡ Complete pipeline in ~5-30 seconds

📹 Select Video Source
┌────────┬─────────────────────┬──────────┬──────────┐
│ Option │ Video               │ Duration │ Time     │
├────────┼─────────────────────┼──────────┼──────────┤
│ 1      │ 🔥 For Bigger Blazes│ 15 sec   │ ~5 sec   │
│ 2      │ 🐰 Big Buck Bunny   │ 10 min   │ ~25-30s  │
│ 3      │ 🐘 Elephants Dream  │ 11 min   │ ~28-33s  │
│ 4      │ 🎥 YouTube URL      │ < 30 min │ varies   │
└────────┴─────────────────────┴──────────┴──────────┘
```

---

## 📊 Usage Examples

### Basic Usage (Auto Mode)

```python
from src.pipeline import VideoHighlightPipeline

# Create pipeline with auto-detection
pipeline = VideoHighlightPipeline(
    num_actors=2,           # Parallel Ray actors
    target_fps=1.0,         # Extract 1 frame per second
    auto_detect=True,       # Intelligent auto-mode
    max_reel_duration=30.0  # 30-second limit
)

# Process video
results = pipeline.run(
    video_path="data/raw/demo/big_buck_bunny.mp4"
)

# Access results
print(f"Highlights: {results['highlights']['num_highlights']}")
print(f"Duration: {results['generation']['actual_duration']:.1f}s")
print(f"Output: {results['output_video']}")
```

### Custom Configuration

```python
# Manual mode with specific settings
pipeline = VideoHighlightPipeline(
    num_actors=4,              # More parallelism
    target_fps=2.0,            # Higher frame rate
    resolution=(320, 320),     # Larger frames
    num_highlights=5,          # Exact number
    clip_duration=5.0,         # Fixed 5s clips
    auto_detect=False,         # Manual mode
    max_reel_duration=60.0     # 60-second limit
)

results = pipeline.run(video_path="my_video.mp4")
```

### Batch Processing

```python
import glob
from pathlib import Path

# Process all videos in directory
video_paths = glob.glob("data/raw/*.mp4")

for video_path in video_paths:
    video_name = Path(video_path).stem
    print(f"\n🎬 Processing: {video_name}")

    pipeline = VideoHighlightPipeline(auto_detect=True)
    results = pipeline.run(
        video_path=video_path,
        output_dir=f"data/output/{video_name}"
    )

    if results['success']:
        print(f"✅ Complete: {results['output_video']}")
    else:
        print(f"❌ Failed: {results.get('error')}")
```

---

## 🎯 Features in Detail

### Intelligent Auto-Detection

The system automatically analyzes your video and determines:

**1. Optimal Number of Highlights**
- Short video (< 1 min): 1-2 highlights
- Medium video (1-5 min): 3-8 highlights
- Long video (> 5 min): 8-15 highlights
- Rule: ~1 highlight per 30 seconds

**2. Adaptive Clip Durations**
- Analyzes importance score around each peak
- Extends clips for sustained interesting moments
- Shrinks clips for brief events
- Range: 2-10 seconds per clip

**3. Quality-Based Selection**
- **Variance score** - Visual diversity and change
- **Novelty score** - Unique/rare scenes
- **Motion score** - Action intensity
- Combined into overall importance score

**4. Smart Thresholds**
- Short videos: 75th percentile (stricter)
- Medium videos: 70th percentile (balanced)
- Long videos: 65th percentile (more inclusive)

### 30-Second Duration Guarantee

All highlight reels are **automatically constrained to 30 seconds** (configurable):

**Stage 1: Proportional Reduction**
```python
# If total > 30s, reduce all clip durations proportionally
# Example: 8 clips × 5s = 40s → 8 clips × 3.75s = 30s
```

**Stage 2: Selective Inclusion**
```python
# If clips still too long, select top-scoring highlights
# Example: 15 clips → select top 10 that fit in 30s
```

**Minimum clip duration:** 2 seconds (ensures quality)

### Side-by-Side Video Player

Play original and highlight reel simultaneously:

**Features:**
- ✅ Real video playback (not ASCII art)
- ✅ Synchronized playback
- ✅ Play/Pause controls (SPACE key)
- ✅ Timestamps on each frame
- ✅ Progress indicator
- ✅ Labeled headers (ORIGINAL / PROCESSED)
- ✅ Dark theme optimized

**Controls:**
- **SPACE** - Play/Pause
- **Q** - Quit

```bash
# Test the player
python test_side_by_side.py
```

---

## 📁 Project Structure

```
video-highlight-generator/
├── src/
│   ├── models/
│   │   └── feature_extractors.py    # MobileNetV3 + Ray actors
│   ├── features/
│   │   ├── highlight_detector.py    # Auto-detection algorithm
│   │   └── video_generator.py       # FFmpeg video generation
│   ├── utils/
│   │   ├── timg_video_player.py     # Terminal video playback
│   │   └── side_by_side_player.py   # Comparison viewer
│   └── pipeline.py                  # End-to-end orchestration
│
├── scripts/
│   ├── download_sample_videos.py    # Get demo videos
│   └── preprocess_videos.py         # Batch preprocessing
│
├── data/
│   ├── raw/demo/                    # Sample input videos
│   ├── pipeline/                    # Processing outputs
│   │   ├── {video_name}/
│   │   │   ├── processed/           # Extracted frames
│   │   │   ├── *_features.npy       # Feature vectors
│   │   │   ├── *_highlights.json    # Detected highlights
│   │   │   ├── *_highlight_reel.mp4 # Final output
│   │   │   └── pipeline_results.json# Complete metrics
│
├── tests/
│   ├── test_01_environment.py       # Setup verification
│   ├── test_02_video_loading.py     # FFmpeg tests
│   ├── test_04_features.py          # Feature extraction
│   ├── test_05_highlights.py        # Detection algorithm
│   ├── test_06_generation.py        # Video generation
│   ├── test_07_pipeline.py          # Full pipeline
│   ├── test_auto_detection.py       # Auto mode tests
│   └── test_side_by_side.py         # Video player tests
│
├── docs/
│   ├── INTELLIGENT_DETECTION.md     # Auto-detection details
│   ├── MAX_DURATION_CONSTRAINT.md   # 30s limit explanation
│   ├── DARK_THEME_COLORS.md         # UI color scheme
│   ├── SIDE_BY_SIDE_PLAYER.md       # Video player docs
│   └── REAL_TERMINAL_VIDEO.md       # Terminal playback guide
│
├── demo_enhanced.py                 # Interactive demo (main)
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 🎓 How It Works

### Phase 1: Preprocessing
1. **Extract frames** using FFmpeg at target FPS (default: 1 FPS)
2. **Resize frames** to model input size (224×224 RGB)
3. **Extract audio** for future multimodal enhancements
4. **Save metadata** (FPS, duration, frame count)

### Phase 2: Feature Extraction
1. **Load MobileNetV3** pre-trained model (lightweight, fast)
2. **Create Ray actor pool** for parallel processing
3. **Process frames in batches** through model
4. **Extract 1280-dim features** from global average pooling layer
5. **Save features** as NumPy array (.npy)

### Phase 3: Highlight Detection
1. **Compute importance scores:**
   - Variance: `np.var(window)` - visual diversity
   - Novelty: Average distance to k-nearest neighbors
   - Motion: `np.linalg.norm(diff)` - frame-to-frame change

2. **Combine signals:**
   ```python
   importance = 0.4×variance + 0.3×novelty + 0.3×motion
   ```

3. **Detect peaks** using `scipy.signal.find_peaks`:
   - Adaptive threshold based on video duration
   - Minimum distance between peaks (10 frames)
   - Sort by importance score (descending)

4. **Determine clip durations:**
   - Find region where score > 60% of peak
   - Clamp to 2-10 seconds
   - Adaptive per highlight

### Phase 4: Video Generation
1. **Adjust for duration constraint:**
   - Calculate total duration
   - Apply proportional reduction if > 30s
   - Select top highlights if needed

2. **Extract clips:**
   - Use FFmpeg to extract segments
   - Center on timestamp: `start = timestamp - duration/2`
   - Include audio

3. **Add transitions:**
   - Fade in: 0.5s at start
   - Fade out: 0.5s at end
   - Smooth visual experience

4. **Concatenate:**
   - Use FFmpeg concat demuxer
   - Copy streams (no re-encoding)
   - Fast and efficient

---

## 📈 Performance

### M4 MacBook Pro (2024)
- **Preprocessing**: ~1-2 seconds for 10-minute video
- **Feature Extraction**: 30-60 FPS (CPU-only)
- **Highlight Detection**: < 1 second
- **Video Generation**: 1-2 seconds
- **Total**: 10-minute video → highlights in 5-30 seconds

### Scaling with Ray
```
Workers | FPS    | Speedup | Videos/Hour
--------|--------|---------|-------------
1       | 30     | 1.0x    | 18
2       | 58     | 1.9x    | 35
4       | 112    | 3.7x    | 67
8       | 216    | 7.2x    | 130
```

### Memory Usage
- **Base**: ~2GB (Python + Ray + PyTorch)
- **Per video**: ~200MB (features + frames)
- **Peak**: ~4GB for 10-minute video

---

## 🔧 Configuration

### Pipeline Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_actors` | 2 | Ray actors for parallel processing |
| `target_fps` | 1.0 | Frames extracted per second |
| `resolution` | (224, 224) | Frame size for model input |
| `auto_detect` | True | Use intelligent auto-detection |
| `num_highlights` | None | Manual: specific number of highlights |
| `clip_duration` | None | Manual: fixed clip duration |
| `max_reel_duration` | 30.0 | Maximum total output duration |

### Highlight Detector Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `variance_weight` | 0.4 | Weight for visual diversity signal |
| `novelty_weight` | 0.3 | Weight for uniqueness signal |
| `motion_weight` | 0.3 | Weight for action intensity signal |
| `min_distance` | 10 | Minimum frames between highlights |

### Video Generator Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `clip_duration` | 3.0 | Default clip duration (auto mode) |
| `fade_duration` | 0.5 | Transition fade time |
| `video_codec` | libx264 | Output video codec |
| `audio_codec` | aac | Output audio codec |

---

## 📚 Documentation

Comprehensive documentation in `docs/` directory:

- **[INTELLIGENT_DETECTION.md](./docs/INTELLIGENT_DETECTION.md)** - How auto-detection works
- **[MAX_DURATION_CONSTRAINT.md](./MAX_DURATION_CONSTRAINT.md)** - 30-second limit implementation
- **[YOUTUBE_SUPPORT.md](./YOUTUBE_SUPPORT.md)** - YouTube video download and processing
- **[DARK_THEME_COLORS.md](./DARK_THEME_COLORS.md)** - UI color scheme
- **[SIDE_BY_SIDE_PLAYER.md](./SIDE_BY_SIDE_PLAYER.md)** - Video player guide
- **[REAL_TERMINAL_VIDEO.md](./REAL_TERMINAL_VIDEO.md)** - Terminal playback setup

---

## 🧪 Testing

Run the test suite to verify your setup:

```bash
# Test environment
python test_01_environment.py

# Test video loading
python test_02_video_loading.py

# Test feature extraction
python test_04_features.py

# Test highlight detection
python test_05_highlights.py

# Test video generation
python test_06_generation.py

# Test full pipeline
python test_07_pipeline.py

# Test auto-detection
python test_auto_detection.py

# Test video player
python test_side_by_side.py

# Test YouTube download (requires yt-dlp)
python tests/test_youtube_download.py --no-process
```

---

## 🛠️ Troubleshooting

### FFmpeg Not Found
```bash
# Install FFmpeg first
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Linux
```

### Ray Import Error
```bash
# Reinstall Ray
pip uninstall ray
pip install -U ray[default]
```

### Out of Memory
```python
# Reduce resolution or FPS
pipeline = VideoHighlightPipeline(
    target_fps=0.5,        # Lower FPS
    resolution=(160, 160)  # Smaller frames
)
```

### Terminal Video Not Working
```bash
# Install timg for terminal graphics
brew install timg  # macOS

# Verify iTerm2/Kitty is being used
echo $TERM_PROGRAM
```

### Slow Feature Extraction
```python
# Increase Ray actors (if you have more CPU cores)
pipeline = VideoHighlightPipeline(
    num_actors=4  # Use 4 parallel workers
)
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add GPU acceleration for feature extraction
- [ ] Implement audio analysis (cheers, music peaks)
- [ ] Add text/speech analysis (transcription + keywords)
- [ ] Support more video formats
- [ ] Real-time streaming analysis
- [ ] Web UI with Gradio/Streamlit
- [ ] Cloud deployment examples (AWS, GCP, Azure)
- [ ] Fine-tuning on custom datasets
- [ ] Multi-language support
- [ ] Customizable highlight rules

---

## 📝 Citation

If you use this project:

```bibtex
@software{video_highlight_generator,
  title={AI-Powered Video Highlight Generator with Ray},
  author={Ray for Developers},
  year={2025},
  url={https://github.com/debnsuma/ray-for-developers}
}
```

---

## 📄 License

MIT License - See [LICENSE](../../LICENSE) for details

---

## 🙏 Acknowledgments

**Built with:**
- [Ray](https://ray.io/) - Distributed computing framework
- [PyTorch](https://pytorch.org/) - Deep learning framework
- [MobileNetV3](https://pytorch.org/vision/stable/models.html) - Efficient visual features
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal UI
- [timg](https://github.com/hzeller/timg) - Terminal graphics

**Sample videos:**
- Google Creative Lab - [For Bigger Blazes](https://opensource.google/projects/android)
- Blender Foundation - [Big Buck Bunny](https://peach.blender.org/), [Elephants Dream](https://orange.blender.org/)

---

## 🚀 Ready to Start?

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download sample videos
python scripts/download_sample_videos.py

# 3. Run the demo
python demo_enhanced.py
```

**Questions?** Check the [Documentation](#-documentation) or open an issue!

**Want to contribute?** See [Contributing](#-contributing) section!

---

**Made with ❤️ using Ray**
