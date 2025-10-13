# 🎬 Embedded Video Player

## Overview

Play videos in an **embedded window** with **labeled banners** showing INPUT/OUTPUT. Real video playback using OpenCV - not ASCII art!

## ✨ Features

### 1. Labeled Video Playback
- **Banner at top** showing video type:
  - `INPUT (Original)` - Blue banner
  - `OUTPUT (Highlight Reel)` - Green banner
- **Real video quality** - full resolution playback
- **Smooth frame rate** - maintains original FPS

### 2. Side-by-Side Comparison
```
┌──────────────────────────────────────────────────┐
│        INPUT (Original)                          │
│  [Original video playing]                        │
│                                                  │
│                                                  │
└──────────────────────────────────────────────────┘
│
┌──────────────────────────────────────────────────┐
│        OUTPUT (Highlight Reel)                   │
│  [Highlight reel playing]                        │
│                                                  │
│                                                  │
└──────────────────────────────────────────────────┘
```

Both videos play **simultaneously** in one window!

### 3. Interactive Controls
- **SPACE**: Pause/Resume
- **Q**: Quit playback
- **Frame counter**: Shows current frame number

## 🚀 How to Use

### Option 1: Through Enhanced Demo

```bash
python demo_enhanced.py
```

After processing:
```
🎬 Watch videos? (y/n): y

🎬 Video Playback Options
1. Play in embedded window (with labels)  ← Real video
2. Open in native video player

Choose playback mode (1/2) [1]: 1

🎬 Embedded Video Player
1. Original video (INPUT)
2. Highlight reel (OUTPUT)
3. Side-by-side comparison (recommended)

Select (1/2/3) [3]: 3
```

**Result:** Opens window showing both videos side-by-side with INPUT/OUTPUT labels!

### Option 2: Standalone Test

```bash
python test_embedded_video.py
```

### Option 3: Python API

```python
from src.utils.embedded_video_player import play_video_embedded, play_comparison_embedded

# Play single video with label
play_video_embedded(
    'data/raw/demo/for_bigger_blazes.mp4',
    label="INPUT (Original)"
)

# Play side-by-side comparison
play_comparison_embedded(
    original_path='data/raw/demo/for_bigger_blazes.mp4',
    processed_path='data/pipeline/for_bigger_blazes/for_bigger_blazes_highlight_reel.mp4',
    original_label="INPUT (Original)",
    processed_label="OUTPUT (Highlight Reel)"
)
```

## 🎨 Visual Layout

### Single Video Mode

```
┌────────────────────────────────────────────────────┐
│               INPUT (Original)                     │ ← Banner
├────────────────────────────────────────────────────┤
│                                                    │
│                                                    │
│           [Video Frame]                            │
│                                                    │
│                                                    │
│                                                    │
└────────────────────────────────────────────────────┘
  Frame: 45                                          ← Info
```

### Side-by-Side Comparison Mode

```
┌─────────────────────────────┬───┬─────────────────────────────┐
│    INPUT (Original)         │   │   OUTPUT (Highlight Reel)   │ ← Banners
├─────────────────────────────┤   ├─────────────────────────────┤
│                             │   │                             │
│                             │   │                             │
│   [Original Video]          │ │ │   [Highlight Reel]          │
│                             │   │                             │
│                             │   │                             │
│                             │   │                             │
└─────────────────────────────┴───┴─────────────────────────────┘
  Frame: 120                                                     ← Info
```

## 🔧 Technical Details

### Banner Customization

The banner shows:
- **Text**: Video label (e.g., "INPUT (Original)")
- **Background**: Dark gray (40, 40, 40)
- **Text Color**:
  - Blue (100, 200, 255) for INPUT
  - Green (100, 255, 100) for OUTPUT
- **Height**: 50 pixels
- **Font**: OpenCV default (HERSHEY_SIMPLEX)

### Video Processing

```python
# 1. Load video
cap = cv2.VideoCapture(video_path)

# 2. Read frame
ret, frame = cap.read()

# 3. Add banner
banner = create_banner(text, color)
frame_with_banner = vstack([banner, frame])

# 4. Display
cv2.imshow(window_name, frame_with_banner)
cv2.waitKey(frame_delay)
```

### Side-by-Side Algorithm

```python
# 1. Load both videos
cap1 = cv2.VideoCapture(original_path)
cap2 = cv2.VideoCapture(processed_path)

# 2. Read frames
ret1, frame1 = cap1.read()
ret2, frame2 = cap2.read()

# 3. Resize to same height
height = min(frame1.shape[0], frame2.shape[0])
frame1_resized = cv2.resize(frame1, ...)
frame2_resized = cv2.resize(frame2, ...)

# 4. Add banners
frame1_with_banner = add_banner(frame1_resized, "INPUT")
frame2_with_banner = add_banner(frame2_resized, "OUTPUT")

# 5. Combine horizontally
combined = hstack([frame1_with_banner, separator, frame2_with_banner])

# 6. Display
cv2.imshow(window_name, combined)
```

## 📊 Comparison: ASCII vs Embedded

| Feature | ASCII Player | Embedded Player |
|---------|-------------|-----------------|
| **Quality** | Low-res ASCII art | Full video quality |
| **Colors** | Grayscale only | Full color |
| **Labels** | Text above | Banners in video |
| **Frame Rate** | May lag | Smooth (maintains FPS) |
| **Resolution** | Terminal size (~120x40) | Video resolution (720p, 1080p) |
| **Side-by-Side** | ASCII blocks | Real videos |
| **Controls** | Ctrl+C only | SPACE, Q |
| **Use Case** | Fun demo, SSH | Real comparison |

**Winner:** Embedded Player for real work! 🏆

## 💡 Use Cases

### 1. Video Quality Comparison
```python
# Compare original vs processed quality
play_comparison_embedded(
    original_path="input.mp4",
    processed_path="output.mp4",
    original_label="INPUT (Raw Footage)",
    processed_label="OUTPUT (Enhanced)"
)
```

### 2. Before/After Showcase
```python
# Show transformation
play_comparison_embedded(
    original_path="before.mp4",
    processed_path="after.mp4",
    original_label="BEFORE (Unedited)",
    processed_label="AFTER (Edited)"
)
```

### 3. Highlight Verification
```python
# Verify highlights match original moments
play_comparison_embedded(
    original_path="full_video.mp4",
    processed_path="highlights.mp4",
    original_label="INPUT (Full Video - 10min)",
    processed_label="OUTPUT (Highlights - 2min)"
)
```

### 4. Client Presentations
```python
# Professional demo for clients
# Labels clearly show INPUT vs OUTPUT
# Side-by-side proves quality
```

## ⚙️ Configuration

### Custom Labels

```python
from src.utils.embedded_video_player import EmbeddedVideoPlayer

player = EmbeddedVideoPlayer()

# Custom colors (BGR format)
player.play_side_by_side(
    "original.mp4",
    "processed.mp4",
    original_label="RAW FOOTAGE",
    processed_label="AI ENHANCED"
)
```

### Adjust Banner

```python
player = EmbeddedVideoPlayer()
player.banner_height = 60  # Taller banner
player.font_scale = 0.9    # Larger font
player.font_thickness = 3  # Bolder text
```

## 🎯 Benefits

### Clear Labeling
- ✅ Instantly see which video is which
- ✅ Professional appearance
- ✅ No confusion during playback

### Real Quality
- ✅ Full resolution (720p, 1080p, 4K)
- ✅ Smooth frame rate (24fps, 30fps, 60fps)
- ✅ All colors preserved

### Interactive
- ✅ Pause when needed
- ✅ Resume playback
- ✅ Frame counter for reference

### Side-by-Side
- ✅ See both videos simultaneously
- ✅ Compare timing and content
- ✅ Perfect for quality verification

## 🚀 Try It Now!

### Quick Test
```bash
python test_embedded_video.py
```

**You'll see:**
1. Menu to choose viewing mode
2. Window opens with labeled video(s)
3. Real video playback with banners
4. Side-by-side comparison (if selected)

### In Demo
```bash
python demo_enhanced.py
```

**After processing:**
1. Choose to watch videos (y)
2. Select embedded mode (1)
3. Choose side-by-side (3)
4. See INPUT and OUTPUT playing together!

## 📝 Summary

**Embedded Video Player:**
- ✅ Real video playback (not ASCII)
- ✅ Labeled banners (INPUT/OUTPUT)
- ✅ Side-by-side comparison
- ✅ Interactive controls (pause, quit)
- ✅ Full quality and color
- ✅ Professional appearance

**Perfect for:**
- Video quality comparison
- Before/after showcases
- Highlight verification
- Client presentations

**Replace ASCII player with real video playback! 🎬✨**
