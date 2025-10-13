# 🎬 Terminal Video Player

## Overview

Play videos **directly in your terminal** using ASCII art! No external video player needed - watch videos right in your console.

## ✨ Features

### 1. ASCII Art Conversion
- Converts video frames to ASCII characters in real-time
- Uses brightness mapping: ` .:-=+*#%@` (dark to light)
- Adjustable resolution to fit your terminal

### 2. Playback Modes

**Single Video:**
- Play original video
- Play highlight reel
- Maintains original frame rate

**Side-by-Side Comparison:**
- Watch original and highlight reel simultaneously
- See both videos in one terminal window
- Perfect for comparing full video vs highlights

### 3. Terminal Integration
- Automatically adjusts to terminal size
- Clear screen + redraw for smooth animation
- Keyboard control (Ctrl+C to stop)

## 🚀 How to Use

### Option 1: Through Enhanced Demo

```bash
python demo_enhanced.py
```

After processing completes:
```
🎬 Watch videos? (y/n): y

🎬 Video Playback Options

1. Play in terminal (ASCII art)
2. Open in video player (native apps)

Choose playback mode (1/2) [1]: 1

🎬 Terminal Video Player
Choose which video to play:

1. Original video
2. Highlight reel
3. Side-by-side comparison

Select (1/2/3) [3]: 3
```

### Option 2: Standalone Test

```bash
python test_terminal_video.py
```

### Option 3: Python API

```python
from src.utils.terminal_video_player import play_video_in_terminal, play_videos_comparison

# Play single video
play_video_in_terminal(
    'data/raw/demo/for_bigger_blazes.mp4',
    title="Original Video",
    max_duration=30
)

# Play side-by-side
play_videos_comparison(
    'data/raw/demo/for_bigger_blazes.mp4',
    'data/pipeline/for_bigger_blazes/for_bigger_blazes_highlight_reel.mp4',
    max_duration=30
)
```

## 📺 Example Output

### Single Video Mode:
```
┌──────────────────────────── Original Video | Frame 45/360 ─────────────────────────────┐
│                                                                                         │
│ .............................................=         +....                            │
│ .............................................=.        *....                            │
│ .............................................-=       +=-:-.                            │
│ ..............................................::=   -+......                            │
│ .............................................. .  .   ......                            │
│ ...................................................  .......                            │
│ ............................. :.       ....................                            │
│ ...................       +++=++++++     ...................                            │
│ ...................  =++++:-******+*+     .. ...............                            │
│ ...................  +****..*=**+=+++    ........ ..........                            │
│ ...................  =****=+++=+=+=++    ........ ..........                            │
│ ...................  =***++::--::-=++    ...................                            │
│ ...................  -**+.:-:----:-++    ...................                            │
│ ...................   +++::-::::::+++    ...................                            │
│ ...................    -+++======++=     ...................                            │
│ ....................     -+*****+=      ....................                            │
│ .....................      .::::       .....................                            │
│ .........................................................                               │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Side-by-Side Mode:
```
┌──────────── Original │ Highlight Reel | Frame 120 ────────────┐
│                                                                │
│ .........=+++*   │  ...........=+*                            │
│ .........+***=   │  ...........***                            │
│ .........:***+   │  ...........-**                            │
│ ..........+**+   │  ............**                            │
│ ..........+**+   │  ............**                            │
│ ..........-**=   │  ...........:*+                            │
│ ...........+*+   │  ............++                            │
│ ...........+*=   │  ............+=                            │
│ ...........++.   │  ............+.                            │
│ ...........:+    │  ............+                             │
│ ............+    │  .............                             │
│ ............-    │  .............                             │
│ .............    │  .............                             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## 🎨 How It Works

### 1. Frame Extraction
```python
cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()  # Get BGR frame
```

### 2. Grayscale Conversion
```python
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
```

### 3. Resize to Terminal
```python
resized = cv2.resize(gray, (terminal_width, terminal_height))
```

### 4. ASCII Mapping
```python
ascii_chars = " .:-=+*#%@"  # 10 brightness levels

for pixel in frame:
    # Map 0-255 → 0-9 index
    char_index = int(pixel / 255 * 9)
    ascii_char = ascii_chars[char_index]
```

### 5. Real-Time Display
```python
console.clear()
console.print(ascii_frame)
time.sleep(1/fps)  # Maintain frame rate
```

## ⚙️ Configuration

### Adjust Resolution

```python
from src.utils.terminal_video_player import TerminalVideoPlayer

# Custom size
player = TerminalVideoPlayer(width=120, height=40)
player.play('video.mp4', title="My Video")
```

### Change ASCII Characters

```python
# More detailed (16 chars)
player.ascii_chars = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

# Minimal (5 chars)
player.ascii_chars = " .oO@"
```

### Limit Duration

```python
# Play only 10 seconds
play_video_in_terminal('video.mp4', max_duration=10)
```

## 💡 Tips

### Best Results

1. **Large Terminal Window**
   - 120+ columns width
   - 40+ rows height
   - More resolution = better quality

2. **Monospace Font**
   - Use fixed-width fonts
   - Examples: Monaco, Menlo, Courier

3. **High Contrast Videos**
   - Videos with clear shapes work best
   - High motion is visible
   - Text is somewhat readable

### Performance

- **Fast videos** (< 1 min): Smooth playback
- **Long videos** (> 5 min): May lag on older systems
- **High FPS** (60fps): Might skip frames to maintain speed

## 🎯 Use Cases

### 1. Quick Preview
```bash
# Quickly see what's in a video without opening player
python -c "from src.utils import play_video_in_terminal; play_video_in_terminal('video.mp4', max_duration=5)"
```

### 2. Remote Server
```bash
# Watch videos over SSH (no X forwarding needed!)
ssh user@server "cd project && python test_terminal_video.py"
```

### 3. Demos & Presentations
```bash
# Cool way to show videos in terminal-based presentations
# ASCII art impresses everyone! 😎
```

### 4. Debugging
```bash
# See what frames look like during processing
# Useful for checking if video loaded correctly
```

## 🔧 Technical Details

### Dependencies
- **OpenCV** (`opencv-python`): Video frame extraction
- **Pillow**: Image processing
- **Rich**: Terminal rendering and UI

### Frame Rate
- Automatically detected from video
- Maintained during playback using `time.sleep()`
- Formula: `sleep_time = (frame_count / fps) - elapsed_time`

### Memory Usage
- Processes one frame at a time
- No buffering of entire video
- Low memory footprint (~50MB for 1080p frame)

### Limitations
- **Color**: Only grayscale (ASCII has no color by nature)
- **Resolution**: Limited by terminal size (typically 80x24 to 200x50)
- **Details**: Fine details lost in ASCII conversion
- **Text**: Video text may be hard to read

## 📊 Comparison

| Feature | Terminal Player | Native Player |
|---------|----------------|---------------|
| **Quality** | ASCII art (low-res) | Full HD/4K |
| **Colors** | Grayscale only | Full color |
| **Speed** | May lag on slow systems | Smooth |
| **Convenience** | Built-in, no external app | Requires player |
| **Remote** | Works over SSH | Requires X forwarding |
| **Cool Factor** | 🔥🔥🔥 Very cool! | 😐 Normal |

## 🎓 Learning Resources

### ASCII Art Video Players
- [ASCIIVideo](https://github.com/noemiko/asciivideo) - Python ASCII video player
- [aalib](http://aa-project.sourceforge.net/aalib/) - Classic ASCII art library
- [bb demo](http://aa-project.sourceforge.net/bb/) - Famous ASCII art demo

### How ASCII Art Works
- Brightness mapping: pixels → characters
- Character density: `@` is "darker" than `.`
- Aspect ratio: Characters are taller than wide

## 🚀 Future Enhancements

Potential improvements:
1. **Color support**: Use terminal 256-color mode
2. **Audio**: Play audio alongside ASCII video
3. **Unicode blocks**: Use `█▓▒░` for better quality
4. **Caching**: Pre-convert frames for smoother playback
5. **Interactive controls**: Pause, rewind, fast-forward

## 📝 Summary

**Terminal Video Player:**
- ✅ Play videos in terminal (no external player)
- ✅ ASCII art conversion in real-time
- ✅ Side-by-side comparison mode
- ✅ Works over SSH
- ✅ Adjustable resolution
- ✅ Cross-platform

**Perfect for:**
- Quick video previews
- Remote server work
- Cool demos
- Terminal enthusiasts

**Try it now:**
```bash
python test_terminal_video.py
```

Watch videos like it's 1985! 🎮📟
