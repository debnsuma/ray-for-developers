# 🎬 Real Terminal Video Playback

## Overview

The demo now supports **real video playback** directly in the terminal using **iTerm2/Kitty graphics protocols** via the `timg` tool. This is **NOT ASCII art** - it's actual video frames rendered inline in your terminal.

## ✨ Key Features

- **Real video quality**: Full-color video frames (not ASCII/Unicode blocks)
- **Inline playback**: Videos play in the same terminal window
- **iTerm2/Kitty support**: Uses native graphics protocols for high quality
- **Fallback support**: If `timg` isn't installed, falls back to native video player

## 🚀 Installation

### Install timg (Required)

```bash
brew install timg
```

timg supports multiple terminal graphics protocols:
- **iTerm2 inline images** (best quality on macOS)
- **Kitty graphics protocol**
- **Sixel graphics**
- Fallback to Unicode blocks if needed

## 📺 How to Use

### Option 1: Through Demo

```bash
python demo_enhanced.py
```

After processing completes:
```
🎬 Watch videos? (y/n): y

🎬 Video Playback Options
1. Play in terminal (real video with iTerm2/Kitty graphics)
2. Open in native video player

Choose playback mode (1/2) [2]: 1

🎬 Terminal Video Player
1. Original video (INPUT)
2. Highlight reel (OUTPUT)
3. Both videos (in sequence)

Select (1/2/3) [3]: 3
```

**Result**: Real video plays inline in your terminal using iTerm2 graphics protocol!

### Option 2: Test Script

```bash
python test_timg_real.py
```

This plays the first 10 seconds of the sample video to verify everything works.

## 🎨 How It Works

### Technology Stack

**timg** is a terminal image/video viewer that supports:
1. **iTerm2 inline images protocol** (for iTerm2 on macOS)
2. **Kitty graphics protocol** (for Kitty terminal)
3. **Sixel graphics** (for terminals with sixel support)
4. **Unicode blocks** (fallback for basic terminals)

### Implementation

```python
from src.utils.timg_video_player import play_video_timg, play_comparison_timg

# Play single video
play_video_timg(
    'data/raw/demo/for_bigger_blazes.mp4',
    label="INPUT (Original)",
    max_duration=60
)

# Play comparison (sequential)
play_comparison_timg(
    original_path='data/raw/demo/for_bigger_blazes.mp4',
    processed_path='data/pipeline/for_bigger_blazes/for_bigger_blazes_highlight_reel.mp4',
    original_label="INPUT (Original)",
    processed_label="OUTPUT (Highlight Reel)",
    max_duration=60
)
```

### Under the Hood

When you play a video, `timg` uses:
```bash
timg -V -pi -g120x30 -t60 --title="INPUT (Original): %b" video.mp4
```

Parameters:
- `-V`: Video mode
- `-pi`: Use iTerm2 protocol (auto-detects best available)
- `-g120x30`: Terminal geometry (120 cols × 30 rows)
- `-t60`: Time limit (60 seconds)
- `--title`: Display title with video filename

## 📊 Comparison: ASCII vs Real Video

| Feature | ASCII/Unicode Player | timg Real Video |
|---------|---------------------|-----------------|
| **Quality** | Low-res blocks (░▒▓█) | Full-color real video |
| **Colors** | Grayscale only | Full RGB color |
| **Rendering** | Unicode characters | iTerm2/Kitty graphics |
| **Frame Rate** | May lag | Smooth native FPS |
| **Terminal Support** | All terminals | iTerm2, Kitty, Sixel |
| **Use Case** | SSH, basic terminals | Modern terminals |

**Winner**: timg for real video quality! 🏆

## 🎯 Terminal Compatibility

### ✅ Supported Terminals

- **iTerm2** (macOS) - Best quality, uses inline images protocol
- **Kitty** - Uses Kitty graphics protocol
- **Terminals with Sixel** - Uses Sixel graphics

### ⚠️ Fallback Terminals

- **Standard terminals** - Falls back to Unicode blocks (similar to old player)
- **SSH sessions** - May need Unicode fallback

## 💡 Technical Details

### iTerm2 Inline Images Protocol

When you see this in the output:
```
]1337;File=size=354338;width=928px;height=522px;inline=1:iVBORw0KG...
```

That's the **iTerm2 inline images escape sequence** sending actual PNG image data to your terminal. Each video frame is:
1. Decoded by `timg`
2. Converted to PNG format
3. Sent using iTerm2's proprietary escape sequence
4. Rendered inline in the terminal

### Why It's Better Than ASCII

ASCII/Unicode players like the old `inline_video_player.py`:
- Convert frames to grayscale
- Map pixel values to characters (░▒▓█)
- Limited to ~5 brightness levels
- No color information

timg with iTerm2 protocol:
- Sends actual image data
- Full RGB color (16.7 million colors)
- Original resolution (scaled to fit)
- Native video quality

## 🔧 Configuration

### Custom Geometry

```python
play_video_timg(
    video_path="video.mp4",
    label="My Video",
    max_duration=120,
    geometry="160x40"  # Wider display
)
```

### Time Limits

```python
# Play first 30 seconds
play_video_timg(video_path, max_duration=30)

# Play entire video (no limit)
play_video_timg(video_path, max_duration=0)
```

## 📝 Files Created

### New Files

- `src/utils/timg_video_player.py` - Python wrapper for timg
- `test_timg_real.py` - Test script for real video playback
- `REAL_TERMINAL_VIDEO.md` - This documentation

### Modified Files

- `src/utils/__init__.py` - Now exports timg functions
- `demo_enhanced.py` - Updated to use timg instead of ASCII player

### Deprecated Files

- `src/utils/inline_video_player.py` - Old ASCII/Unicode player (kept for reference)
- `test_inline_quick.py` - Old ASCII player test

## 🎉 Benefits

### Clear Visual Quality
- ✅ Real video frames, not ASCII approximation
- ✅ Full color reproduction
- ✅ Smooth playback at native FPS

### Professional Appearance
- ✅ No pixelation or ASCII artifacts
- ✅ Proper video rendering
- ✅ Maintains aspect ratio

### Better User Experience
- ✅ Instant recognition of video content
- ✅ No learning curve (looks like normal video)
- ✅ Works in same terminal window

## 🚨 Important Notes

1. **Requires `timg` installation**: `brew install timg`
2. **Best on iTerm2**: Other terminals may have varying support
3. **Sequential playback**: Side-by-side shows videos one after another (timg limitation)
4. **Falls back gracefully**: If timg isn't available, uses native video player

## 🎬 Try It Now!

```bash
# Quick test (10 seconds)
python test_timg_real.py

# Full demo
python demo_enhanced.py
# → Process video
# → Choose option 1 (Play in terminal)
# → Choose option 3 (Both videos)
# → Watch real video playback!
```

## 📖 Summary

**Real Terminal Video Player:**
- ✅ Actual video frames (not ASCII)
- ✅ Full RGB color
- ✅ iTerm2/Kitty/Sixel graphics support
- ✅ Inline playback in same terminal
- ✅ Professional quality
- ✅ Native FPS rendering

**Perfect for:**
- Verifying video processing results
- Comparing INPUT vs OUTPUT
- Quick preview without leaving terminal
- Professional demos

**Experience real video in your terminal! 🎬✨**
