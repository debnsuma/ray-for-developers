# 🎬 Side-by-Side Video Player with Play/Pause Controls

## Overview

Play two videos **side-by-side** in the **same terminal** with **play/pause controls** using real video (not ASCII art). Videos are displayed using iTerm2/Kitty graphics protocols with labeled headers showing "ORIGINAL" and "PROCESSED".

## ✨ Key Features

- ✅ **Side-by-side layout** - Both videos play simultaneously
- ✅ **Labeled headers** - Blue "ORIGINAL" and green "PROCESSED" banners
- ✅ **Play/Pause controls** - Press SPACE to pause/resume
- ✅ **Real video rendering** - Full-color frames using iTerm2/Kitty graphics
- ✅ **Timestamp display** - Shows current time / total duration
- ✅ **Same terminal** - No popup windows
- ✅ **Synchronized playback** - Both videos play in sync

## 🎨 Visual Layout

```
┌────────────────────────────────┬─┬────────────────────────────────┐
│      INPUT (Original)          │ │    OUTPUT (Processed)          │ ← Headers
├────────────────────────────────┤ ├────────────────────────────────┤
│                                │ │                                │
│    [Original Video Frame]      │ │  [Processed Video Frame]       │
│                                │ │                                │
│                                │ │                                │
│                                │ │                                │
└────────────────────────────────┴─┴────────────────────────────────┘
  00:05 / 00:15  [SPACE] Pause  [Q] Quit                          ← Footer
```

## 🚀 How to Use

### Option 1: Through Demo

```bash
python demo_enhanced.py
```

After processing:
```
🎬 Watch videos? (y/n): y

🎬 Video Playback Options
1. Play in terminal (real video with iTerm2/Kitty graphics)
2. Open in native video player

Choose playback mode (1/2) [2]: 1

🎬 Terminal Video Player
1. Original video (INPUT)
2. Highlight reel (OUTPUT)
3. Side-by-side with play/pause (recommended!)
4. Both videos (in sequence)

Select (1/2/3/4) [3]: 3
```

**Result**: Videos play side-by-side with play/pause controls!

### Option 2: Test Script

```bash
python test_side_by_side.py
```

Plays first 20 seconds for testing.

### Option 3: Python API

```python
from src.utils.side_by_side_player import play_videos_side_by_side

play_videos_side_by_side(
    original_path='data/raw/demo/for_bigger_blazes.mp4',
    processed_path='data/pipeline/for_bigger_blazes/for_bigger_blazes_highlight_reel.mp4',
    original_label="ORIGINAL",
    processed_label="PROCESSED",
    max_duration=60  # 0 = no limit
)
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| **SPACE** | Toggle Play/Pause |
| **Q** | Quit playback |

**Visual Feedback:**
- Playing: `[SPACE] Pause  [Q] Quit` (green)
- Paused: `[SPACE] Play  [Q] Quit` (blue)

## 🔧 How It Works

### Frame-by-Frame Processing

1. **Read frames** from both videos simultaneously
2. **Resize** to same height (maintaining aspect ratio)
3. **Add headers** with labels:
   - Left header: Blue background + "INPUT (Original)" text
   - Right header: Green background + "OUTPUT (Processed)" text
4. **Combine** side-by-side with 4px separator
5. **Add footer** with timestamp and controls
6. **Save** combined frame as temporary PNG
7. **Display** using `timg` with iTerm2 protocol
8. **Wait** for keyboard input (non-blocking)

### Synchronization

Both videos are read frame-by-frame in lockstep:
```python
ret_left, frame_left = cap_left.read()
ret_right, frame_right = cap_right.read()

combined_frame = create_side_by_side_frame(
    frame_left, frame_right,
    "ORIGINAL", "PROCESSED",
    timestamp, duration
)
```

### Play/Pause Implementation

Uses non-blocking keyboard input:
```python
# Setup terminal for non-blocking input
tty.setcbreak(sys.stdin.fileno())

while playing:
    if is_key_pressed():
        key = get_key().lower()
        if key == ' ':
            paused = not paused
        elif key == 'q':
            break

    if not paused:
        # Read and display next frame
        frame_count += 1
```

## 📊 Technical Details

### Header Design

**Left Header (ORIGINAL):**
- Background: RGB(100, 50, 20) - Dark blue
- Text: White, centered
- Height: 60 pixels
- Font: OpenCV HERSHEY_SIMPLEX, scale 1.2

**Right Header (PROCESSED):**
- Background: RGB(20, 80, 20) - Dark green
- Text: White, centered
- Height: 60 pixels
- Font: OpenCV HERSHEY_SIMPLEX, scale 1.2

### Footer Design

- Background: RGB(30, 30, 30) - Dark gray
- Height: 50 pixels
- Left side: Timestamp (00:05 / 00:15)
- Right side: Controls with color-coded status

### Frame Rate Maintenance

Maintains original FPS:
```python
frame_delay = 1.0 / fps

# For each frame:
elapsed = time.time() - start_time - total_pause_time
expected_time = frame_count * frame_delay
sleep_time = expected_time - elapsed

if sleep_time > 0:
    time.sleep(sleep_time)
```

### Pause Time Tracking

Tracks total pause duration to maintain sync:
```python
if paused:
    pause_start = time.time()
else:
    total_pause_time += time.time() - pause_start
```

## 💡 Use Cases

### 1. Quality Comparison
```python
# Compare original vs processed quality side-by-side
play_videos_side_by_side(
    "raw_video.mp4",
    "enhanced_video.mp4",
    "RAW FOOTAGE",
    "AI ENHANCED"
)
```

### 2. Before/After Demo
```python
# Show transformation side-by-side
play_videos_side_by_side(
    "before_editing.mp4",
    "after_editing.mp4",
    "BEFORE",
    "AFTER"
)
```

### 3. Highlight Verification
```python
# Verify highlight extraction
play_videos_side_by_side(
    "full_video.mp4",
    "highlights.mp4",
    "FULL VIDEO (10min)",
    "HIGHLIGHTS (2min)"
)
```

### 4. A/B Testing
```python
# Compare two processing methods
play_videos_side_by_side(
    "method_a.mp4",
    "method_b.mp4",
    "METHOD A",
    "METHOD B"
)
```

## 🎯 Benefits

### Real-Time Comparison
- ✅ See differences instantly
- ✅ Both videos play in perfect sync
- ✅ No need to switch between windows

### Professional Quality
- ✅ Full-color real video (not ASCII)
- ✅ Labeled headers for clarity
- ✅ Professional appearance

### Interactive Control
- ✅ Pause anytime to examine frames
- ✅ Resume seamlessly
- ✅ Quit when done

### Terminal Native
- ✅ No popup windows
- ✅ All in same terminal
- ✅ Works with SSH (if terminal supports graphics)

## 📝 Configuration

### Custom Labels

```python
from src.utils.side_by_side_player import SideBySidePlayer

player = SideBySidePlayer(width=200, height=50)
player.play_side_by_side(
    "video1.mp4",
    "video2.mp4",
    left_label="VERSION 1.0",
    right_label="VERSION 2.0",
    max_duration=120
)
```

### Duration Control

```python
# Play first 30 seconds
play_videos_side_by_side(original, processed, max_duration=30)

# Play entire video
play_videos_side_by_side(original, processed, max_duration=0)
```

### Terminal Size

Auto-detects terminal size:
```python
import shutil
term_size = shutil.get_terminal_size()
width = min(200, term_size.columns)
height = min(50, term_size.lines - 10)
```

## 🚨 Requirements

### Dependencies
- **OpenCV** (`cv2`) - Frame processing
- **timg** - Terminal graphics rendering
- **Rich** - Console formatting
- **termios/tty** - Non-blocking keyboard input

### Installation
```bash
# Install timg
brew install timg

# Python dependencies (already in requirements.txt)
pip install opencv-python rich numpy
```

### Terminal Support
- **iTerm2** (macOS) - Best quality
- **Kitty** - Full support
- **Terminals with Sixel** - Supported
- **Basic terminals** - Won't work (needs graphics protocol)

## 🎬 Example Session

```bash
$ python test_side_by_side.py

🎬 Testing Side-by-Side Video Player

Features:
  • Two videos playing side-by-side
  • Real video (not ASCII)
  • Labeled headers (ORIGINAL / PROCESSED)
  • Play/Pause with SPACE
  • Quit with Q

🎬 Side-by-Side Video Player

╭────────────────────────── 🎬 Controls ──────────────────────────╮
│ ORIGINAL: for_bigger_blazes.mp4                                 │
│ PROCESSED: for_bigger_blazes_highlight_reel.mp4                 │
│                                                                  │
│ Duration: 00:15                                                  │
│ FPS: 24.0                                                        │
│                                                                  │
│ Controls:                                                        │
│   • SPACE - Play/Pause                                           │
│   • Q - Quit                                                     │
│                                                                  │
│ Playing in terminal with iTerm2/Kitty graphics...               │
╰──────────────────────────────────────────────────────────────────╯

[Videos playing side-by-side with headers and controls...]

✅ Playback complete!
```

## 📚 API Reference

### `SideBySidePlayer`

```python
class SideBySidePlayer:
    def __init__(self, width: int = 160, height: int = 30):
        """Initialize side-by-side player"""

    def play_side_by_side(
        self,
        left_path: str,
        right_path: str,
        left_label: str = "ORIGINAL",
        right_label: str = "PROCESSED",
        max_duration: int = 60
    ):
        """Play two videos side-by-side with controls"""
```

### `play_videos_side_by_side()`

```python
def play_videos_side_by_side(
    original_path: str,
    processed_path: str,
    original_label: str = "INPUT (Original)",
    processed_label: str = "OUTPUT (Processed)",
    max_duration: int = 60
):
    """Convenience function to play videos side-by-side"""
```

## 🎉 Summary

**Side-by-Side Video Player:**
- ✅ Two videos playing simultaneously
- ✅ Labeled headers (ORIGINAL / PROCESSED)
- ✅ Play/Pause controls (SPACE/Q)
- ✅ Real video rendering (iTerm2/Kitty)
- ✅ Same terminal window
- ✅ Synchronized playback
- ✅ Timestamp display
- ✅ Professional quality

**Perfect for:**
- Quality comparison
- Before/After demos
- Highlight verification
- A/B testing
- Client presentations

**Experience professional side-by-side video comparison in your terminal! 🎬✨**
