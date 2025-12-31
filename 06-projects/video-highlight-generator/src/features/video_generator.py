"""
Video Highlight Generation
Extracts and concatenates highlight clips using FFmpeg
Optimized for M4 MacBook Pro
"""
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import tempfile
import shutil


class VideoHighlightGenerator:
    """
    Generate highlight reels from detected highlights

    Uses FFmpeg to:
    1. Extract video segments at highlight timestamps
    2. Concatenate segments into a single highlight reel
    3. Optionally add transitions between clips
    """

    def __init__(
        self,
        clip_duration: float = 3.0,
        fade_duration: float = 0.5,
        output_format: str = "mp4",
        video_codec: str = "libx264",
        audio_codec: str = "aac"
    ):
        """
        Initialize the video highlight generator

        Args:
            clip_duration: Duration of each highlight clip in seconds
            fade_duration: Duration of fade in/out transitions
            output_format: Output video format
            video_codec: Video codec for output
            audio_codec: Audio codec for output
        """
        self.clip_duration = clip_duration
        self.fade_duration = fade_duration
        self.output_format = output_format
        self.video_codec = video_codec
        self.audio_codec = audio_codec

        print(f"🎬 VideoHighlightGenerator initialized")
        print(f"   Clip duration: {clip_duration}s")
        print(f"   Fade duration: {fade_duration}s")
        print(f"   Output format: {output_format}")

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

        Args:
            highlights: List of highlight dictionaries
            max_duration: Maximum total duration in seconds

        Returns:
            Adjusted list of highlights
        """
        if not highlights:
            return highlights

        # Calculate total duration
        total_duration = sum(
            h.get('clip_duration', self.clip_duration) for h in highlights
        )

        print(f"   Initial total duration: {total_duration:.1f}s (limit: {max_duration:.1f}s)")

        if total_duration <= max_duration:
            print(f"   Duration within limit - no adjustment needed")
            return highlights

        # Strategy 1: Reduce clip durations proportionally
        reduction_factor = max_duration / total_duration
        adjusted_highlights = []

        for h in highlights:
            h_copy = h.copy()
            original_duration = h.get('clip_duration', self.clip_duration)
            new_duration = max(2.0, original_duration * reduction_factor)  # Min 2s clips
            h_copy['clip_duration'] = new_duration
            adjusted_highlights.append(h_copy)

        # Check if proportional reduction is sufficient
        new_total = sum(h['clip_duration'] for h in adjusted_highlights)

        if new_total <= max_duration:
            print(f"   Adjusted clip durations proportionally: {new_total:.1f}s")
            return adjusted_highlights

        # Strategy 2: Select fewer highlights (keep top scoring ones)
        # Highlights should already be sorted by score (descending)
        selected = []
        current_duration = 0.0

        for h in highlights:
            clip_duration = h.get('clip_duration', self.clip_duration)
            if current_duration + clip_duration <= max_duration:
                selected.append(h)
                current_duration += clip_duration
            else:
                # Try to fit a shorter version
                remaining = max_duration - current_duration
                if remaining >= 2.0:  # Minimum 2s clip
                    h_copy = h.copy()
                    h_copy['clip_duration'] = remaining
                    selected.append(h_copy)
                break

        final_duration = sum(h.get('clip_duration', self.clip_duration) for h in selected)
        print(f"   Selected {len(selected)}/{len(highlights)} highlights: {final_duration:.1f}s")

        return selected

    def extract_clip(
        self,
        video_path: str,
        timestamp: float,
        output_path: str,
        duration: Optional[float] = None
    ) -> bool:
        """
        Extract a single clip from video at timestamp

        Args:
            video_path: Path to source video
            timestamp: Start timestamp in seconds
            output_path: Output path for clip
            duration: Duration of clip (None = use default)

        Returns:
            True if successful, False otherwise
        """
        if duration is None:
            duration = self.clip_duration

        # Calculate start time (centered on timestamp)
        start_time = max(0, timestamp - duration / 2)

        try:
            # Extract clip with FFmpeg
            cmd = [
                'ffmpeg',
                '-ss', str(start_time),  # Start time
                '-i', video_path,  # Input file
                '-t', str(duration),  # Duration
                '-c:v', self.video_codec,  # Video codec
                '-c:a', self.audio_codec,  # Audio codec
                '-y',  # Overwrite output
                '-loglevel', 'error',  # Only show errors
                output_path
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Failed to extract clip at {timestamp}s: {e.stderr.decode()}")
            return False

    def add_fade_transitions(
        self,
        input_path: str,
        output_path: str,
        fade_in: bool = True,
        fade_out: bool = True
    ) -> bool:
        """
        Add fade in/out transitions to a clip

        Args:
            input_path: Input clip path
            output_path: Output path with transitions
            fade_in: Add fade in transition
            fade_out: Add fade out transition

        Returns:
            True if successful, False otherwise
        """
        try:
            # Build filter complex for fades
            filters = []

            if fade_in:
                filters.append(f"fade=t=in:st=0:d={self.fade_duration}")

            if fade_out:
                # Need to know duration for fade out
                # Get duration from input file
                probe_cmd = [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'json',
                    input_path
                ]
                result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
                duration = float(json.loads(result.stdout)['format']['duration'])
                fade_start = max(0, duration - self.fade_duration)
                filters.append(f"fade=t=out:st={fade_start}:d={self.fade_duration}")

            if not filters:
                # No transitions, just copy
                shutil.copy(input_path, output_path)
                return True

            filter_str = ",".join(filters)

            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vf', filter_str,
                '-c:a', 'copy',  # Copy audio without re-encoding
                '-y',
                '-loglevel', 'error',
                output_path
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Failed to add transitions: {e.stderr.decode()}")
            return False

    def concatenate_clips(
        self,
        clip_paths: List[str],
        output_path: str
    ) -> bool:
        """
        Concatenate multiple clips into single video

        Args:
            clip_paths: List of clip paths to concatenate
            output_path: Output path for concatenated video

        Returns:
            True if successful, False otherwise
        """
        if not clip_paths:
            print("   ⚠️  No clips to concatenate")
            return False

        # Create temporary file list for FFmpeg concat
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            concat_file = f.name
            for clip_path in clip_paths:
                # Convert to absolute path and escape
                abs_path = str(Path(clip_path).absolute())
                escaped_path = abs_path.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")

        try:
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',  # Copy streams without re-encoding for speed
                '-y',
                '-loglevel', 'error',
                output_path
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Failed to concatenate clips: {e.stderr.decode()}")
            return False

        finally:
            # Cleanup temp file
            Path(concat_file).unlink(missing_ok=True)

    def generate_highlight_reel(
        self,
        video_path: str,
        highlights_path: str,
        output_path: str,
        add_transitions: bool = True,
        max_highlights: Optional[int] = None,
        max_duration: float = 30.0
    ) -> Dict:
        """
        Generate complete highlight reel from highlights data

        Args:
            video_path: Path to original video
            highlights_path: Path to highlights JSON file
            output_path: Output path for highlight reel
            add_transitions: Add fade transitions between clips
            max_highlights: Maximum number of highlights to include
            max_duration: Maximum total duration of highlight reel in seconds (default: 30s)

        Returns:
            Dictionary with generation results
        """
        print(f"\n🎬 Generating highlight reel")
        print(f"   Video: {Path(video_path).name}")
        print(f"   Highlights: {Path(highlights_path).name}")
        print(f"   Max duration: {max_duration}s")

        # Load highlights
        with open(highlights_path, 'r') as f:
            highlights_data = json.load(f)

        highlights = highlights_data['highlights']

        # Limit by max_duration constraint - prioritize this over max_highlights
        highlights_adjusted = self._adjust_for_max_duration(highlights, max_duration)

        # Then apply max_highlights if specified
        if max_highlights and len(highlights_adjusted) > max_highlights:
            highlights_adjusted = highlights_adjusted[:max_highlights]
            print(f"   Using top {max_highlights} highlights")

        highlights = highlights_adjusted

        print(f"   Extracting {len(highlights)} clips...")

        # Create temporary directory for clips
        temp_dir = Path(tempfile.mkdtemp())

        try:
            clip_paths = []
            successful_clips = 0

            # Extract each highlight clip
            for i, highlight in enumerate(highlights):
                timestamp = highlight['timestamp']
                score = highlight['importance_score']

                # Use adaptive duration if available, otherwise use default
                clip_duration = highlight.get('clip_duration', self.clip_duration)

                print(f"      Clip {i+1}/{len(highlights)}: {timestamp:.1f}s (score: {score:.3f}, duration: {clip_duration:.1f}s)")

                # Extract clip
                clip_path = temp_dir / f"clip_{i:03d}.mp4"
                success = self.extract_clip(
                    video_path=video_path,
                    timestamp=timestamp,
                    output_path=str(clip_path),
                    duration=clip_duration
                )

                if not success:
                    continue

                # Add transitions if requested
                if add_transitions:
                    transition_path = temp_dir / f"clip_{i:03d}_fade.mp4"
                    success = self.add_fade_transitions(
                        input_path=str(clip_path),
                        output_path=str(transition_path),
                        fade_in=True,
                        fade_out=True
                    )

                    if success:
                        clip_paths.append(str(transition_path))
                        successful_clips += 1
                    else:
                        # Use clip without transitions
                        clip_paths.append(str(clip_path))
                        successful_clips += 1
                else:
                    clip_paths.append(str(clip_path))
                    successful_clips += 1

            print(f"   ✅ Extracted {successful_clips} clips")

            if not clip_paths:
                return {
                    'success': False,
                    'error': 'No clips extracted'
                }

            # Concatenate clips
            print(f"   Concatenating {len(clip_paths)} clips...")

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            success = self.concatenate_clips(
                clip_paths=clip_paths,
                output_path=str(output_path)
            )

            if not success:
                return {
                    'success': False,
                    'error': 'Failed to concatenate clips'
                }

            # Get output file size
            output_size_mb = output_path.stat().st_size / (1024 * 1024)

            # Calculate actual total duration
            actual_duration = sum(
                h.get('clip_duration', self.clip_duration) for h in highlights
            )

            print(f"   ✅ Highlight reel created!")
            print(f"      Output: {output_path}")
            print(f"      Size: {output_size_mb:.1f} MB")
            print(f"      Clips: {len(clip_paths)}")
            print(f"      Duration: {actual_duration:.1f}s")

            return {
                'success': True,
                'output_path': str(output_path),
                'num_clips': len(clip_paths),
                'output_size_mb': output_size_mb,
                'estimated_duration': actual_duration,
                'actual_duration': actual_duration,
                'video_name': highlights_data['video_name'],
                'original_highlights': len(highlights_data['highlights']),
                'included_highlights': len(highlights)
            }

        except Exception as e:
            print(f"   ❌ Error generating highlight reel: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }

        finally:
            # Cleanup temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
