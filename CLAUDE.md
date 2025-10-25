# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is **Ray for Developers** - a comprehensive learning repository for building scalable distributed applications using the Ray framework. The repository is organized into 5 learning modules, with the primary implementation being a production-ready Video Highlight Generator in module 03.

**Key characteristics:**
- Learning resource with hands-on examples and exercises
- Python 3.12 required
- Uses `uv` for fast package management
- Currently contains ~20 Python files, primarily in the video-highlight-generator project
- Modules 01, 02, 04, and 05 are framework placeholders (README-only) for future content

## Environment Setup

### Installation Commands

```bash
# Create virtual environment with Python 3.12
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Ray with all components (CPU version)
uv pip install "ray[default,train,tune,serve,rllib,data]"

# Install PyTorch (CPU version)
uv pip install torch torchvision torchaudio

# For GPU support with CUDA 12.1
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Verify Installation

```bash
python -c "import ray; ray.init(); print(f'Ray version: {ray.__version__}')"
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Video Highlight Generator Project

The primary implementation is in `03-multimodal-data-processing/video-highlight-generator/`. This is an AI-powered system that creates 30-second highlight reels using Ray distributed computing.

### Project Commands

```bash
cd 03-multimodal-data-processing/video-highlight-generator

# Install project dependencies
pip install -r requirements.txt

# Install FFmpeg (required)
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg

# Download sample videos (~50MB total)
python scripts/download_sample_videos.py

# Run the interactive demo
python demo.py

# Run test suite (in sequence)
python tests/test_01_environment.py       # Environment verification
python tests/test_02_video_loading.py     # FFmpeg integration
python tests/test_04_features.py          # Feature extraction
python tests/test_05_highlights.py        # Highlight detection
python tests/test_06_generation.py        # Video generation
python tests/test_07_pipeline.py          # Full pipeline integration
python tests/test_youtube_download.py     # YouTube support (requires yt-dlp)

# Batch preprocessing
python scripts/preprocess_videos.py

# Cleanup generated files
bash scripts/cleanup.sh
```

## Architecture Overview

### Video Highlight Generator Pipeline (4 Phases)

The system uses a 4-phase architecture orchestrated through `src/pipeline.py`:

1. **Preprocessing (FFmpeg + Ray)** - Extract frames at 1 FPS, resize to 224x224, extract audio
2. **Feature Extraction (MobileNetV3 + Ray Actors)** - Parallel processing with Ray actor pool, extract 1280-dim visual features per frame
3. **Highlight Detection (Custom ML Algorithm)** - Compute importance scores (variance + novelty + motion), detect peaks with adaptive thresholds
4. **Video Generation (FFmpeg)** - Extract clips, add fade transitions, enforce 30-second duration constraint

### Key Design Patterns

**Ray Actor Pattern** - Stateful distributed workers:
```python
@ray.remote
class VisualFeatureExtractor:
    def __init__(self):
        self.model = load_model()  # Loaded once per actor

    def extract_frame_features(self, frame_path):
        return self.model(frame)

# Create actor pool for parallel processing
actors = [VisualFeatureExtractor.remote() for _ in range(num_actors)]
futures = [actor.extract_video_features.remote(batch) for actor, batch in zip(actors, batches)]
results = ray.get(futures)
```

**Multi-Signal ML Algorithm** - Combined scoring approach:
```python
# Three signals combined with configurable weights
importance = 0.4 * variance + 0.3 * novelty + 0.3 * motion

# Adaptive thresholds based on video duration
if video_duration < 60:
    threshold_percentile = 75      # Stricter for short videos
elif video_duration < 300:
    threshold_percentile = 70      # Balanced for medium
else:
    threshold_percentile = 65      # Inclusive for long videos
```

**FFmpeg Subprocess Pattern** - External tool integration:
```python
subprocess.run(
    ['ffmpeg', '-i', input_video, '-vf', filters, output_video],
    capture_output=True, check=True
)
```

### Core Components

**`src/pipeline.py` (380 lines)** - Main orchestrator
- `VideoHighlightPipeline` class
- Methods: `initialize_ray()`, `preprocess_video()`, `extract_features()`, `detect_highlights()`, `generate_video()`, `run()`
- Handles Ray cluster setup/cleanup, progress callbacks, resource monitoring

**`src/models/feature_extractors.py` (226 lines)** - Distributed ML inference
- `VisualFeatureExtractor` Ray actor decorated with `@ray.remote`
- MobileNetV3-small model with MPS acceleration (Apple Silicon)
- Factory function: `create_feature_extractor_pool(num_actors)`

**`src/features/highlight_detector.py` (558 lines)** - ML algorithms
- `HighlightDetector` class
- Methods: `compute_variance_score()`, `compute_novelty_score()`, `compute_motion_score()`, `detect_highlights()`, `detect_peaks()`
- Auto-detection mode with adaptive threshold selection

**`src/features/video_generator.py`** - FFmpeg wrapper
- `VideoHighlightGenerator` class
- Methods: `extract_clips()`, `concatenate_clips()`, `add_transitions()`, `_adjust_for_max_duration()`
- Enforces 30-second maximum duration constraint

### File Organization

```
video-highlight-generator/
├── src/
│   ├── pipeline.py              # Main orchestrator
│   ├── models/
│   │   └── feature_extractors.py  # Ray actors for ML inference
│   ├── features/
│   │   ├── highlight_detector.py  # Detection algorithms
│   │   └── video_generator.py     # FFmpeg wrapper
│   └── utils/
│       ├── timg_video_player.py   # Terminal video playback
│       └── side_by_side_player.py # Comparison viewer
├── scripts/
│   ├── download_sample_videos.py  # Get demo videos
│   └── preprocess_videos.py       # Batch processing
├── tests/                       # 9 test files (hierarchical)
├── data/
│   ├── raw/demo/                # Input videos
│   └── pipeline/                # Processing outputs
├── docs/                        # Detailed documentation
├── demo.py                      # Interactive CLI (1083 lines)
└── requirements.txt             # Python dependencies
```

## Module Structure

### 01-ray-fundamentals/
**Status:** Placeholder (README-only)
**Topics:** Ray architecture, tasks, actors, object store, debugging, monitoring

### 02-distributed-training/
**Status:** Placeholder (README-only)
**Topics:** Data/model parallelism, Ray Train, hyperparameter tuning, RLHF, DPO, checkpointing

### 03-multimodal-data-processing/
**Status:** Full implementation
**Contents:** Video Highlight Generator project (see above)

### 04-inference/
**Status:** Placeholder (README-only)
**Topics:** Ray Serve, model deployment, batching, autoscaling, LLM inference, A/B testing

### 05-reinforcement-learning/
**Status:** Placeholder (README-only)
**Topics:** RLlib, policy optimization, multi-agent RL, custom environments, RLHF for LLMs

## Common Development Patterns

### Testing Pattern
Each test file follows consistent structure:
1. Header with test description
2. Setup and imports
3. Serial test cases (numbered)
4. Try-except with informative error messages
5. Success/failure printing
6. `sys.exit(1)` on critical failures

### Progress Monitoring Pattern
```python
class Pipeline:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def _log(self, message, phase="INFO"):
        print(f"[{phase}] {message}")
        if self.progress_callback:
            self.progress_callback(phase, message)
```

### Resource Management Pattern
```python
pipeline.initialize_ray()
try:
    results = pipeline.run(...)
finally:
    pipeline.shutdown_ray()
```

## Key Dependencies

**Core frameworks:**
- `ray[default,data]==2.39.0` - Distributed computing
- `torch==2.5.1` - Deep learning
- `torchvision==0.20.1` - Computer vision models

**Video/audio processing:**
- `opencv-python==4.10.0.84` - Image processing
- `av==13.1.0` - Video bindings
- `librosa==0.10.2` - Audio analysis

**ML models:**
- `transformers==4.46.3` - Hugging Face transformers
- `timm==1.0.11` - Pre-trained models

**Scientific computing:**
- `numpy==1.26.4` - Numerical arrays
- `scipy==1.14.1` - Scientific algorithms (peak detection)

**External dependencies:**
- FFmpeg (system-level, required for video processing)
- `timg` (optional, for terminal video playback)
- `yt-dlp` (optional, for YouTube support)

## Ray-Specific Patterns

### Actor Initialization
```python
# Initialize Ray cluster
ray.init(num_cpus=4, ignore_reinit_error=True)

# Create actor pool
@ray.remote
class Worker:
    def process(self, data):
        return result

actors = [Worker.remote() for _ in range(num_workers)]
```

### Parallel Task Distribution
```python
# Distribute batches across actors
futures = [actor.process.remote(batch) for actor, batch in zip(actors, batches)]

# Gather results (blocking)
results = ray.get(futures)
```

### Resource Management
```python
# Always shutdown Ray when done
try:
    ray.init()
    # ... work ...
finally:
    ray.shutdown()
```

## Important Notes

- **No compiled components** - Pure Python with external tools (FFmpeg)
- **No Makefile or setup.py** - Uses requirements.txt only
- **Configuration via constructor arguments** - No external config files
- **Tested on M4 MacBook Pro** - Apple Silicon with MPS acceleration support
- **Auto-detection is recommended** - Manual mode available but auto-mode handles adaptive thresholds
- **30-second constraint is enforced** - Two-stage reduction strategy (proportional + selective)
- **Ray actors are stateful** - Models loaded once per actor, not per frame
