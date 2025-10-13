# 🚀 How to Run and Experience the Pipeline

## ✨ Enhanced CLI Demo (Recommended!)

I've created TWO beautiful CLI demos - choose based on your needs!

### Option A: Enhanced Demo with Ray Worker Visualization (New!)

```bash
# Activate virtual environment
source .venv/bin/activate

# Run enhanced demo - shows parallelism!
python demo_enhanced.py
```

**Features:**
- 🔄 **Real-time Ray worker visualization** in CLI
- 📊 **Parallel task execution monitoring** (see tasks on W0, W1)
- 🎬 **Side-by-side video comparison** (original + highlights)
- ⚡ **6-panel live dashboard** with cluster status
- 🎯 **No browser required** - everything in terminal!

### Option B: Simple Interactive Demo

```bash
# Run simple demo - clean and focused
python run_demo.py
```

**Features:**
- 🎨 Beautiful UI with colors and progress bars
- 📊 Results tables and summaries
- 🌐 Auto-opens Ray Dashboard in browser
- 🎬 Auto-play video option

### What You'll See:

1. **📹 Video Selection Menu**
   - Choose from 3 demo videos
   - See estimated processing times

2. **⚙️ Configuration**
   - Set number of highlights (1-10)
   - Set clip duration (1-10s)

3. **🚀 Real-Time Processing**
   - Live progress bar
   - Phase-by-phase updates
   - Ray Dashboard auto-opens in browser

4. **📊 Results Display**
   - Processing time breakdown
   - Highlight timestamps with scores
   - Output file location

5. **🎬 Auto-Play**
   - Option to open highlight reel automatically
   - View your highlights!

### Example Session:

```
🎬 Video Highlight Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Select video (1-3):
  1. For Bigger Blazes 🔥 (15s) - ~5 seconds
  2. Big Buck Bunny 🐰 (10min) - ~25-30 seconds
  3. Elephants Dream 🐘 (11min) - ~28-33 seconds

> 1

Number of highlights (1-10) [default: 5]: 3
Clip duration (1-10s) [default: 3.0]: 3

🚀 Opening Ray Dashboard...
✅ Ray Dashboard opened: http://localhost:8265

🎬 Processing: For Bigger Blazes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🔄 Processing video... ████████████████████ 100%

✅ PIPELINE COMPLETE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Summary:
  Total Time: 5.1s
  Phase 1: 0.5s
  Phase 2: 1.7s
  Phase 3: 0.0s
  Phase 4: 0.7s

🎯 Highlights:
  1. 00:07 - Score: 1.000 🌟

📹 Output: data/pipeline/for_bigger_blazes/for_bigger_blazes_highlight_reel.mp4
```

---

## 🐍 Python Script (Programmatic)

If you want to use it in your own code:

```python
from src.pipeline import VideoHighlightPipeline

# Create pipeline
pipeline = VideoHighlightPipeline(
    num_actors=2,
    num_highlights=5,
    clip_duration=3.0
)

# Process video
results = pipeline.run('data/raw/demo/for_bigger_blazes.mp4')

# Check results
if results['success']:
    print(f"✅ Output: {results['output_video']}")
    print(f"⏱️  Time: {results['total_time']:.1f}s")

    # View highlights
    for h in results['highlights']['highlights']:
        mins = int(h['timestamp'] // 60)
        secs = int(h['timestamp'] % 60)
        print(f"  {mins:02d}:{secs:02d} - Score: {h['importance_score']:.3f}")
```

Save as `my_test.py` and run:
```bash
python my_test.py
```

---

## 🧪 Test Suite (Step-by-Step)

To see each phase individually:

```bash
python test_01_environment.py      # ✅ Environment setup
python test_02_video_loading.py    # ✅ Ray Data loading
python test_03_preprocessing.py    # ✅ Frame extraction
python test_04_features.py         # ✅ MobileNetV3 features
python test_05_highlights.py       # ✅ Highlight detection
python test_06_generation.py       # ✅ Video generation
python test_07_pipeline.py         # ✅ End-to-end pipeline
```

Each test shows detailed output and verifies that phase works correctly.

---

## 📊 Ray Dashboard

The Ray Dashboard opens automatically when you run the demo, but you can also open it manually:

**URL**: http://localhost:8265

**What to Watch:**
- **Jobs**: See the pipeline running
- **Actors**: Watch 2 VisualFeatureExtractor actors
- **Tasks**: See frame processing tasks
- **Resources**: Monitor CPU and MPS usage
- **Timeline**: Visualize task execution

**Best View**: Open in a separate monitor or window while running the demo!

---

## 🎯 What Each Demo Shows

### demo_enhanced.py (Enhanced CLI - BEST!)
✅ **Real-time Ray worker visualization**
✅ **Parallel task execution display**
✅ **Side-by-side video comparison**
✅ **6-panel live dashboard**
✅ **CPU/Memory/GPU monitoring**
✅ **Activity logs with timestamps**
✅ **Everything in terminal - no browser needed**

### run_demo.py (Simple Interactive CLI)
✅ Beautiful UI with colors and progress
✅ Real-time updates
✅ Auto-opens Ray Dashboard
✅ Interactive configuration
✅ Results visualization
✅ Auto-play video

### Python Script
✅ Programmatic access
✅ Easy to integrate
✅ Full control over parameters
✅ Perfect for automation

### Test Suite
✅ Phase-by-phase verification
✅ Detailed technical output
✅ Performance metrics
✅ Educational - see how it works

---

## 💡 Recommendations

**For First Time / Best Experience**: Run `python demo_enhanced.py`
- **See Ray parallelism in action!**
- Watch tasks distributed across workers (W0, W1)
- Real-time cluster monitoring
- Side-by-side video comparison
- Everything in one terminal!

**For Simple Demo**: Run `python run_demo.py`
- Clean and focused UI
- Opens Ray Dashboard in browser
- Interactive configuration
- Auto-play highlights

**For Development**: Use Python scripts
- Quick iterations
- Easy to customize
- Integrate into workflows

**For Understanding**: Run test suite
- Learn each phase
- See technical details
- Verify everything works

---

## 🎬 Video Recommendations

**First Try**: Option 1 (For Bigger Blazes - 15s)
- Fastest processing (~5 seconds)
- Quick results
- Perfect for testing

**Full Experience**: Option 2 (Big Buck Bunny - 10min)
- Realistic video length
- Multiple highlights
- ~25-30 seconds processing

**Maximum Impact**: Option 3 (Elephants Dream - 11min)
- Longest video
- Most highlights
- Shows scalability

---

## 🆘 Troubleshooting

**If videos not found:**
```bash
python scripts/download_sample_videos.py
```

**If Ray won't start:**
```bash
# Kill any existing Ray processes
ray stop
# Then run demo again
```

**If port 8265 is busy:**
The Ray Dashboard might already be running from a previous session. That's okay - it will still work!

---

## 🎉 Enjoy!

You now have multiple ways to experience the pipeline:
1. ⭐ **Enhanced CLI Demo (demo_enhanced.py)** - See parallelism & Ray workers!
2. 🌟 Simple CLI Demo (run_demo.py) - Clean interface
3. 🐍 Python Scripts (programmatic) - For integration
4. 🧪 Test Suite (educational) - Learn each phase

**All methods show the complete Ray-powered pipeline in action!**

### 🎯 Complete Example Session (demo_enhanced.py)

```
╔═══════════════════════════════════════════════════════════╗
║      🎬 Video Highlight Generator - Enhanced Demo        ║
╚═══════════════════════════════════════════════════════════╝

Select (1-3): 1

┌──────────────────────────────────────────────┐
│ 🎬 For Bigger Blazes                         │
└──────────────────────────────────────────────┘
┌──────────── Pipeline Progress ───────────────┐
│ ✅ Phase 1: Preprocessing Complete           │
│ 🔄 Phase 2: Feature Extraction Running       │
│ ⏳ Phase 3: Highlight Detection Waiting      │
│ ⏳ Phase 4: Video Generation Waiting         │
└──────────────────────────────────────────────┘
┌─────────────── Activity Log ─────────────────┐
│ 11:07:43 [PHASE 1] Preprocessing complete    │
│ 11:07:46 [PHASE 2] Starting feature extract  │
│ 11:07:48 [PHASE 2] 16 frames @ 10.2 FPS     │
└──────────────────────────────────────────────┘
┌──────────── Ray Cluster Status ──────────────┐
│ 💻 CPUs: 4 active                            │
│ 💾 Memory: 45%                               │
│ 👷 Workers: 2 active (W0, W1)                │
│ 🎮 GPU: MPS enabled                          │
└──────────────────────────────────────────────┘
┌────────── Parallel Task Execution ───────────┐
│ Worker  Task                Status           │
│ W0      Extract frame 1     ✅ Done          │
│ W1      Extract frame 2     🔄 Running       │
└──────────────────────────────────────────────┘
┌──────────────────────────────────────────────┐
│ Elapsed: 5.1s | Status: Complete             │
└──────────────────────────────────────────────┘

✅ Pipeline Complete!
🎬 Play side-by-side comparison? (y/n): y
Opening original and highlights side by side...
```

For questions, check:
- USAGE.md - Quick usage guide
- PROGRESS.md - Development notes
- README.md - Full documentation
