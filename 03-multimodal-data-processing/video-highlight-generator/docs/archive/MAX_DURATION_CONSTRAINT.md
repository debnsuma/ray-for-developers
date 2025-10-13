# 🎬 Maximum Reel Duration Constraint (30 Seconds)

## Overview

The video highlight generator now **automatically ensures** that all highlight reels are **30 seconds or less** in duration, regardless of video length or number of detected highlights.

## Key Feature

**Maximum Reel Duration:** 30 seconds (configurable)

This constraint is applied intelligently to produce the best possible highlight reel within the time limit.

## How It Works

### Intelligent Adjustment Strategy

When the total duration of detected highlights exceeds 30 seconds, the system uses a two-stage adjustment strategy:

#### Stage 1: Proportional Duration Reduction
- **Calculates** total duration of all highlight clips
- **Reduces** each clip's duration proportionally to fit within 30s
- **Maintains** minimum clip duration of 2 seconds
- **Preserves** all highlights if possible

**Example:**
```
Original: 5 clips × 8s each = 40s total
Adjusted: 5 clips × 6s each = 30s total (75% of original)
```

#### Stage 2: Selective Highlight Reduction
If proportional reduction results in clips that are too short (< 2s), the system:
- **Selects** top-scoring highlights that fit within 30s
- **Prioritizes** quality over quantity
- **Maximizes** use of available time

**Example:**
```
Original: 12 clips × 3s each = 36s total
Strategy 2: Select top 10 clips × 3s = 30s total
```

## Implementation Details

### 1. Video Generator (`src/features/video_generator.py`)

Added `max_duration` parameter to `generate_highlight_reel()`:

```python
def generate_highlight_reel(
    self,
    video_path: str,
    highlights_path: str,
    output_path: str,
    add_transitions: bool = True,
    max_highlights: Optional[int] = None,
    max_duration: float = 30.0  # NEW: Maximum reel duration
) -> Dict:
```

Added `_adjust_for_max_duration()` method:

```python
def _adjust_for_max_duration(
    self,
    highlights: List[Dict],
    max_duration: float
) -> List[Dict]:
    """
    Adjust highlights to fit within max_duration constraint

    Strategy:
    1. Calculate total duration of all clips
    2. If over max_duration, reduce clip durations proportionally
    3. If still over, select fewer highlights (top scoring ones)
    """
```

### 2. Pipeline (`src/pipeline.py`)

Added `max_reel_duration` parameter:

```python
def __init__(
    self,
    num_actors: int = 2,
    target_fps: float = 1.0,
    resolution: tuple = (224, 224),
    num_highlights: Optional[int] = None,
    clip_duration: Optional[float] = None,
    auto_detect: bool = True,
    max_reel_duration: float = 30.0,  # NEW: Max reel duration
    progress_callback: Optional[Callable] = None
):
```

Updated `generate_highlight_reel()` to pass the constraint:

```python
result = self.generator.generate_highlight_reel(
    video_path=video_path,
    highlights_path=highlights_path,
    output_path=output_path,
    add_transitions=True,
    max_highlights=self.num_highlights,
    max_duration=self.max_reel_duration  # NEW: Pass max duration
)
```

## Usage

### Default Behavior (30 seconds)

```python
from src.pipeline import VideoHighlightPipeline

# Default: max_reel_duration = 30.0
pipeline = VideoHighlightPipeline(
    num_actors=2,
    auto_detect=True
)

results = pipeline.run(video_path="my_video.mp4")
# Highlight reel will be ≤ 30 seconds
```

### Custom Duration

```python
# Custom maximum duration (e.g., 60 seconds)
pipeline = VideoHighlightPipeline(
    num_actors=2,
    auto_detect=True,
    max_reel_duration=60.0  # 60 seconds instead of 30
)

results = pipeline.run(video_path="my_video.mp4")
# Highlight reel will be ≤ 60 seconds
```

## Output Information

The generation results now include detailed duration information:

```python
{
    'success': True,
    'output_path': 'path/to/highlight_reel.mp4',
    'num_clips': 8,
    'output_size_mb': 2.3,
    'actual_duration': 29.5,           # NEW: Actual reel duration
    'estimated_duration': 29.5,        # Same as actual_duration
    'original_highlights': 12,         # NEW: Total highlights detected
    'included_highlights': 8,          # NEW: Highlights actually included
    'video_name': 'my_video'
}
```

## Examples

### Example 1: Short Video (15 seconds)

**Input:** 15-second video
**Detected:** 1 highlight × 3s = 3s total
**Adjustment:** None needed (3s < 30s)
**Output:** 1 highlight, 3s duration ✅

### Example 2: Medium Video (10 minutes)

**Input:** 10-minute video
**Detected:** 8 highlights × 5s each = 40s total
**Adjustment:** Proportional reduction to 3.75s per clip
**Output:** 8 highlights, 30s duration ✅

### Example 3: Long Video (60 minutes)

**Input:** 60-minute video
**Detected:** 15 highlights × 4s each = 60s total
**Adjustment:** Select top 8 highlights (best scores)
**Output:** 8 highlights, ~30s duration ✅

### Example 4: Very Long Video (2 hours)

**Input:** 2-hour video
**Detected:** 20 highlights × 6s each = 120s total
**Adjustment:** Select top 5 highlights
**Output:** 5 highlights, 30s duration ✅

## Benefits

### For Users
- ✅ **Consistent experience** - All reels are short and digestible
- ✅ **No overwhelming length** - Perfect for quick previews
- ✅ **Social media ready** - Fits platform requirements
- ✅ **Fast processing** - Shorter output = faster generation

### For Developers
- ✅ **Predictable output** - Known maximum duration
- ✅ **Quality control** - Prevents excessively long reels
- ✅ **Resource management** - Bounded processing time
- ✅ **Configurable** - Easy to adjust for different use cases

## Technical Details

### Minimum Clip Duration

**Minimum:** 2.0 seconds per clip

This ensures clips are long enough to be meaningful, even after proportional reduction.

### Adjustment Algorithm

```python
if total_duration <= max_duration:
    # No adjustment needed
    return highlights

# Stage 1: Proportional reduction
reduction_factor = max_duration / total_duration
for highlight in highlights:
    new_duration = max(2.0, original_duration * reduction_factor)

if new_total <= max_duration:
    return adjusted_highlights

# Stage 2: Selective inclusion
selected = []
current_duration = 0.0
for highlight in sorted_by_score:
    if current_duration + clip_duration <= max_duration:
        selected.append(highlight)
        current_duration += clip_duration
    else:
        # Try to fit a shorter version
        if remaining >= 2.0:
            adjusted_highlight = clip with remaining time
            selected.append(adjusted_highlight)
        break

return selected
```

### Priority Order

1. **Duration constraint** (30s) - Highest priority
2. **Quality preservation** - Keep best highlights
3. **Clip count** - Maximize number of clips if possible
4. **Minimum clip length** - Maintain 2s minimum

## Console Output

During processing, you'll see:

```
🎬 Generating highlight reel
   Video: my_video.mp4
   Highlights: my_video_highlights.json
   Max duration: 30.0s
   Initial total duration: 48.0s (limit: 30.0s)
   Selected 7/10 highlights: 29.5s
   Extracting 7 clips...
      Clip 1/7: 12.5s (score: 0.892, duration: 4.0s)
      Clip 2/7: 34.2s (score: 0.876, duration: 4.5s)
      ...
   ✅ Extracted 7 clips
   Concatenating 7 clips...
   ✅ Highlight reel created!
      Output: path/to/highlight_reel.mp4
      Size: 2.1 MB
      Clips: 7
      Duration: 29.5s
```

## Configuration

### In Pipeline

```python
pipeline = VideoHighlightPipeline(
    num_actors=2,
    target_fps=1.0,
    resolution=(224, 224),
    auto_detect=True,
    max_reel_duration=30.0  # ← Configure here
)
```

### In Direct Generator Usage

```python
from src.features.video_generator import VideoHighlightGenerator

generator = VideoHighlightGenerator(clip_duration=3.0)

result = generator.generate_highlight_reel(
    video_path="video.mp4",
    highlights_path="highlights.json",
    output_path="output.mp4",
    max_duration=30.0  # ← Configure here
)
```

## Backward Compatibility

✅ **Fully backward compatible**

Existing code without the `max_reel_duration` parameter will default to 30 seconds:

```python
# Old code - still works, defaults to 30s
pipeline = VideoHighlightPipeline(
    num_actors=2,
    auto_detect=True
)
```

## Testing

To verify the constraint:

```bash
# Run pipeline and check output duration
python demo_enhanced.py

# Or test directly
python -c "
from src.pipeline import VideoHighlightPipeline
pipeline = VideoHighlightPipeline(max_reel_duration=30.0)
results = pipeline.run('data/raw/demo/big_buck_bunny.mp4')
print(f'Duration: {results[\"generation\"][\"actual_duration\"]}s')
"
```

## Summary

🎯 **Goal:** Ensure all highlight reels are ≤ 30 seconds
✅ **Implementation:** Two-stage intelligent adjustment
🔧 **Configuration:** Easily customizable via `max_reel_duration` parameter
📊 **Output:** Includes detailed duration metrics
🚀 **Status:** Fully implemented and tested

**All highlight reels are now guaranteed to be 30 seconds or less!** 🎬✨
