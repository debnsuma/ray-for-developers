"""
Side-by-Side Video Player with Play/Pause Controls
Displays two videos side-by-side in terminal using iTerm2/Kitty graphics
"""
import cv2
import numpy as np
import subprocess
import tempfile
import time
import sys
import select
import termios
import tty
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()


class SideBySidePlayer:
    """Play two videos side-by-side with play/pause controls"""

    def __init__(self, width: int = 160, height: int = 30):
        """
        Initialize side-by-side player

        Args:
            width: Terminal width in characters
            height: Terminal height in characters
        """
        self.width = width
        self.height = height
        self.paused = False
        self.running = True

    def is_key_pressed(self):
        """Check if a key was pressed (non-blocking)"""
        return select.select([sys.stdin], [], [], 0.0)[0]

    def get_key(self):
        """Get the pressed key"""
        return sys.stdin.read(1)

    def format_timestamp(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS or MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def create_side_by_side_frame(
        self,
        left_frame: np.ndarray,
        right_frame: np.ndarray,
        left_label: str,
        right_label: str,
        timestamp: float,
        duration: float
    ) -> np.ndarray:
        """
        Create a single frame with two videos side-by-side with labels

        Args:
            left_frame: Left video frame
            right_frame: Right video frame
            left_label: Label for left video
            right_label: Label for right video
            timestamp: Current timestamp
            duration: Total duration

        Returns:
            Combined frame with labels
        """
        # Resize both frames to same height
        target_height = min(left_frame.shape[0], right_frame.shape[0])

        # Calculate width maintaining aspect ratio
        left_aspect = left_frame.shape[1] / left_frame.shape[0]
        right_aspect = right_frame.shape[1] / right_frame.shape[0]

        left_width = int(target_height * left_aspect)
        right_width = int(target_height * right_aspect)

        # Resize frames
        left_resized = cv2.resize(left_frame, (left_width, target_height))
        right_resized = cv2.resize(right_frame, (right_width, target_height))

        # Add timestamp overlay to each frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        time_str = self.format_timestamp(timestamp)
        font_scale = 0.6
        thickness = 2

        # Add timestamp to left frame (bottom-right)
        (text_width, text_height), baseline = cv2.getTextSize(time_str, font, font_scale, thickness)
        x = left_width - text_width - 10
        y = target_height - 10

        # Semi-transparent background for left
        overlay_left = left_resized.copy()
        cv2.rectangle(overlay_left, (x - 5, y - text_height - 5),
                     (x + text_width + 5, y + baseline + 5), (0, 0, 0), -1)
        left_resized = cv2.addWeighted(overlay_left, 0.6, left_resized, 0.4, 0)
        cv2.putText(left_resized, time_str, (x, y), font, font_scale, (255, 255, 255), thickness)

        # Add timestamp to right frame (bottom-right)
        x = right_width - text_width - 10
        y = target_height - 10

        # Semi-transparent background for right
        overlay_right = right_resized.copy()
        cv2.rectangle(overlay_right, (x - 5, y - text_height - 5),
                     (x + text_width + 5, y + baseline + 5), (0, 0, 0), -1)
        right_resized = cv2.addWeighted(overlay_right, 0.6, right_resized, 0.4, 0)
        cv2.putText(right_resized, time_str, (x, y), font, font_scale, (255, 255, 255), thickness)

        # Create header bars with labels
        header_height = 60
        separator_width = 4

        # Left header (soft teal/cyan)
        left_header = np.zeros((header_height, left_width, 3), dtype=np.uint8)
        left_header[:] = (80, 60, 40)  # Soft teal/cyan background

        # Right header (soft mint green)
        right_header = np.zeros((header_height, right_width, 3), dtype=np.uint8)
        right_header[:] = (40, 70, 50)  # Soft mint green background

        # Add text to headers
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 2

        # Left label
        (text_width, text_height), _ = cv2.getTextSize(left_label, font, font_scale, thickness)
        x = (left_width - text_width) // 2
        y = (header_height + text_height) // 2
        cv2.putText(left_header, left_label, (x, y), font, font_scale, (255, 255, 255), thickness)

        # Right label
        (text_width, text_height), _ = cv2.getTextSize(right_label, font, font_scale, thickness)
        x = (right_width - text_width) // 2
        y = (header_height + text_height) // 2
        cv2.putText(right_header, right_label, (x, y), font, font_scale, (255, 255, 255), thickness)

        # Combine headers with frames
        left_combined = np.vstack([left_header, left_resized])
        right_combined = np.vstack([right_header, right_resized])

        # Create separator
        separator = np.ones((left_combined.shape[0], separator_width, 3), dtype=np.uint8) * 50

        # Combine side by side
        combined = np.hstack([left_combined, separator, right_combined])

        # Add timestamp and controls footer
        footer_height = 50
        footer = np.zeros((footer_height, combined.shape[1], 3), dtype=np.uint8)
        footer[:] = (40, 40, 40)  # Slightly lighter dark gray

        # Timestamp text
        time_str = f"{self.format_timestamp(timestamp)} / {self.format_timestamp(duration)}"
        (text_width, text_height), _ = cv2.getTextSize(time_str, font, 0.7, 2)
        x = 20
        y = (footer_height + text_height) // 2
        cv2.putText(footer, time_str, (x, y), font, 0.7, (255, 255, 255), 2)

        # Controls text
        if self.paused:
            controls_text = "[SPACE] Play  [Q] Quit"
            status_color = (180, 150, 120)  # Soft amber
        else:
            controls_text = "[SPACE] Pause  [Q] Quit"
            status_color = (120, 180, 140)  # Soft mint

        (text_width, text_height), _ = cv2.getTextSize(controls_text, font, 0.7, 2)
        x = combined.shape[1] - text_width - 20
        y = (footer_height + text_height) // 2
        cv2.putText(footer, controls_text, (x, y), font, 0.7, status_color, 2)

        # Combine with footer
        final_frame = np.vstack([combined, footer])

        return final_frame

    def play_side_by_side(
        self,
        left_path: str,
        right_path: str,
        left_label: str = "ORIGINAL",
        right_label: str = "PROCESSED",
        max_duration: int = 60
    ):
        """
        Play two videos side-by-side with play/pause controls

        Args:
            left_path: Path to left video
            right_path: Path to right video
            left_label: Label for left video
            right_label: Label for right video
            max_duration: Maximum duration in seconds
        """
        left_path = Path(left_path)
        right_path = Path(right_path)

        if not left_path.exists():
            console.print(f"[bright_red]❌ Left video not found: {left_path}[/bright_red]")
            return

        if not right_path.exists():
            console.print(f"[bright_red]❌ Right video not found: {right_path}[/bright_red]")
            return

        # Open both videos
        cap_left = cv2.VideoCapture(str(left_path))
        cap_right = cv2.VideoCapture(str(right_path))

        if not cap_left.isOpened() or not cap_right.isOpened():
            console.print("[bright_red]❌ Could not open videos[/bright_red]")
            return

        # Get video properties
        fps = cap_left.get(cv2.CAP_PROP_FPS)
        total_frames_left = int(cap_left.get(cv2.CAP_PROP_FRAME_COUNT))
        total_frames_right = int(cap_right.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_left = total_frames_left / fps
        duration_right = total_frames_right / fps
        duration = max(duration_left, duration_right)
        frame_delay = 1.0 / fps

        # Limit duration
        if max_duration > 0:
            max_frames = min(total_frames_left, total_frames_right, int(max_duration * fps))
        else:
            max_frames = min(total_frames_left, total_frames_right)

        console.print(f"\n[bold bright_cyan]🎬 Side-by-Side Video Player[/bold bright_cyan]\n")
        console.print(Panel(
            f"[bright_cyan]{left_label}:[/bright_cyan] {left_path.name}\n"
            f"[bright_green]{right_label}:[/bright_green] {right_path.name}\n\n"
            f"[grey93]Duration:[/grey93] {self.format_timestamp(duration)}\n"
            f"[grey93]FPS:[/grey93] {fps:.1f}\n\n"
            "[bright_yellow]Controls:[/bright_yellow]\n"
            "  • [bright_cyan]SPACE[/bright_cyan] - Play/Pause\n"
            "  • [bright_cyan]Q[/bright_cyan] - Quit\n\n"
            "[grey70]Playing in terminal with iTerm2/Kitty graphics...[/grey70]",
            title="🎬 Controls",
            border_style="bright_cyan",
            box=box.ROUNDED
        ))

        # Setup non-blocking keyboard input
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())

            frame_count = 0
            start_time = time.time()
            pause_start = 0
            total_pause_time = 0

            # Create temp directory for frames
            temp_dir = tempfile.mkdtemp()
            temp_frame_path = Path(temp_dir) / "frame.png"

            while frame_count < max_frames and self.running:
                # Check for keyboard input
                if self.is_key_pressed():
                    key = self.get_key().lower()
                    if key == ' ':
                        self.paused = not self.paused
                        if self.paused:
                            pause_start = time.time()
                        else:
                            total_pause_time += time.time() - pause_start
                    elif key == 'q':
                        self.running = False
                        break

                if not self.paused:
                    # Read frames
                    ret_left, frame_left = cap_left.read()
                    ret_right, frame_right = cap_right.read()

                    if not ret_left or not ret_right:
                        break

                    # Calculate timestamp
                    timestamp = frame_count / fps

                    # Create combined frame
                    combined_frame = self.create_side_by_side_frame(
                        frame_left,
                        frame_right,
                        left_label,
                        right_label,
                        timestamp,
                        duration
                    )

                    # Save frame temporarily
                    cv2.imwrite(str(temp_frame_path), combined_frame)

                    # Display using timg (iTerm2 protocol)
                    try:
                        # Clear screen and display frame
                        subprocess.run(
                            ['timg', '-pi', '--clear', str(temp_frame_path)],
                            check=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    except subprocess.CalledProcessError:
                        console.print("[bright_red]❌ Error displaying frame[/bright_red]")
                        break

                    # Maintain frame rate
                    elapsed = time.time() - start_time - total_pause_time
                    expected_time = frame_count * frame_delay
                    sleep_time = expected_time - elapsed

                    if sleep_time > 0:
                        time.sleep(sleep_time)

                    frame_count += 1
                else:
                    # Paused - just sleep a bit
                    time.sleep(0.1)

            # Cleanup
            if temp_frame_path.exists():
                temp_frame_path.unlink()
            Path(temp_dir).rmdir()

            console.print(f"\n[bright_green]✅ Playback complete![/bright_green]")

        except KeyboardInterrupt:
            console.print(f"\n[bright_yellow]⏸️  Playback stopped[/bright_yellow]")

        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            cap_left.release()
            cap_right.release()


def play_videos_side_by_side(
    original_path: str,
    processed_path: str,
    original_label: str = "INPUT (Original)",
    processed_label: str = "OUTPUT (Processed)",
    max_duration: int = 60
):
    """
    Convenience function to play videos side-by-side

    Args:
        original_path: Path to original video
        processed_path: Path to processed video
        original_label: Label for original video
        processed_label: Label for processed video
        max_duration: Maximum duration in seconds (0 = no limit)
    """
    # Get terminal size
    try:
        import shutil
        term_size = shutil.get_terminal_size()
        width = min(200, term_size.columns)
        height = min(50, term_size.lines - 10)
    except:
        width = 160
        height = 30

    player = SideBySidePlayer(width=width, height=height)
    player.play_side_by_side(
        original_path,
        processed_path,
        original_label,
        processed_label,
        max_duration
    )
