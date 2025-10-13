# Quick Usage Guide

## ✅ Tested and Working on M4 MacBook Pro

All 7 phases of the project are complete and tested!

## 🚀 Quick Start (CLI)

### Option 1: Simple Python Script

```python
from src.pipeline import VideoHighlightPipeline

# Initialize pipeline
pipeline = VideoHighlightPipeline(
    num_actors=2,
    num_highlights=5,
    clip_duration=3.0
)

# Process video
results = pipeline.run('data/raw/demo/for_bigger_blazes.mp4')

print(f"✅ Output: {results['output_video']}")
print(f"⏱️  Time: {results['total_time']:.1f}s")
```

### Option 2: Test Script

```bash
# Run end-to-end pipeline test
python test_07_pipeline.py
```

## 📊 What Works

✅ **Phase 1**: Environment setup (Ray, PyTorch, MPS on M4)
✅ **Phase 2**: Video loading with Ray Data
✅ **Phase 3**: Preprocessing (frame & audio extraction)
✅ **Phase 4**: Feature extraction (MobileNetV3 @ 191 FPS!)
✅ **Phase 5**: Highlight detection (multi-signal algorithm)
✅ **Phase 6**: Video generation (FFmpeg with transitions)
✅ **Phase 7**: End-to-end pipeline (5s for 15s video!)

## 🎬 Demo Videos

Three sample videos are included:
- `for_bigger_blazes.mp4` - 15 seconds (fastest to test)
- `big_buck_bunny.mp4` - 10 minutes
- `elephants_dream.mp4` - 11 minutes

## 📈 Performance

**M4 MacBook Pro Results:**
- Short video (15s): **5 seconds** end-to-end
- Medium video (10min): **~25-30 seconds** estimated
- Feature extraction: **191 FPS** with MPS acceleration
- Ray workers: 2-4 actors

## 🧪 Full Test Suite

```bash
# Test everything step by step
python test_01_environment.py      # ✅ Environment
python test_02_video_loading.py    # ✅ Ray Data
python test_03_preprocessing.py    # ✅ Frame extraction
python test_04_features.py         # ✅ MobileNetV3
python test_05_highlights.py       # ✅ Detection
python test_06_generation.py       # ✅ FFmpeg
python test_07_pipeline.py         # ✅ End-to-end
```

## 🖥️ Ray Dashboard

Monitor Ray workers in real-time:
```
http://localhost:8265
```

View:
- Active tasks and workers
- Resource utilization (CPU, Memory, MPS)
- Object store usage
- Task timeline

## 📁 Output Structure

After processing, find your results in:
```
data/pipeline/{video_name}/
├── processed/              # Preprocessed frames & audio
├── {video_name}_features.npy        # Visual features
├── {video_name}_highlights.json     # Highlight timestamps
├── {video_name}_highlight_reel.mp4  # Final output! 🎉
└── pipeline_results.json            # Full statistics
```

## 🎯 Key Features Implemented

1. **Intelligent Detection**: Multi-signal (variance + novelty + motion)
2. **Fast Processing**: MPS acceleration on M4
3. **Parallel Processing**: Ray Actors for distributed workload
4. **Professional Output**: HD with smooth fade transitions
5. **Complete Automation**: One command from video to highlights

## 💡 Tips

- Start with `for_bigger_blazes.mp4` (fastest)
- Adjust `num_highlights` (1-10) for more/fewer clips
- Change `clip_duration` (1-10s) for longer/shorter clips
- Monitor Ray dashboard for real-time progress
- Check `PROGRESS.md` for detailed development notes

## ⚠️ Known Issues

- **Gradio web UI**: Compatibility issue with Python 3.12 and current Gradio version
  - **Workaround**: Use CLI/Python API (works perfectly!)
  - Web UI will be fixed in future update

## 📝 Example: Process Your Own Video

```python
from pathlib import Path
from src.pipeline import VideoHighlightPipeline

# Your video
video_path = "path/to/your/video.mp4"

# Create pipeline
pipeline = VideoHighlightPipeline(
    num_actors=2,          # Parallel workers
    target_fps=1.0,        # Sample 1 frame per second
    resolution=(224, 224), # Resize for speed
    num_highlights=5,      # Top 5 moments
    clip_duration=3.0      # 3 second clips
)

# Process!
results = pipeline.run(video_path)

if results['success']:
    print(f"✅ Highlight reel created!")
    print(f"📹 Output: {results['output_video']}")
    print(f"⏱️  Processing time: {results['total_time']:.1f}s")

    # View highlights
    for i, h in enumerate(results['highlights']['highlights'], 1):
        mins = int(h['timestamp'] // 60)
        secs = int(h['timestamp'] % 60)
        print(f"   {i}. {mins:02d}:{secs:02d} - Score: {h['importance_score']:.3f}")
else:
    print(f"❌ Error: {results['error']}")
```

## 🎉 Success!

The project is **complete and working perfectly** on M4 MacBook Pro!

- All tests passing ✅
- End-to-end pipeline working ✅
- Fast performance (191 FPS!) ✅
- Professional output quality ✅
- Ray integration working ✅

**Next Steps:** See README.md for scaling to RTX 5090 or multi-GPU clusters!
