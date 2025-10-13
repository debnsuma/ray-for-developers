"""
Real Terminal Video Player using timg
Plays actual video in terminal using iTerm2/Kitty/Sixel graphics protocols
"""
import subprocess
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()


def check_timg_available() -> bool:
    """Check if timg is installed"""
    return shutil.which('timg') is not None


def play_video_timg(
    video_path: str,
    label: str = "Video",
    max_duration: int = 60,
    geometry: str = "120x30"
):
    """
    Play video using timg with real graphics (not ASCII)

    Args:
        video_path: Path to video file
        label: Video label
        max_duration: Maximum duration in seconds
        geometry: Terminal geometry (widthxheight in characters)
    """
    video_path = Path(video_path)

    if not video_path.exists():
        console.print(f"[red]❌ Video not found: {video_path}[/red]")
        return

    if not check_timg_available():
        console.print("[red]❌ timg not installed[/red]")
        console.print("[yellow]Install with: brew install timg[/yellow]")
        return

    console.print(f"\n[bold cyan]📹 {label}[/bold cyan]\n")
    console.print(Panel(
        f"[white]Playing:[/white] [cyan]{video_path.name}[/cyan]\n"
        f"[white]Duration:[/white] [yellow]First {max_duration}s[/yellow]\n\n"
        "[dim]Real video playback using iTerm2/Kitty graphics protocol[/dim]\n"
        "[dim]Press Ctrl+C to stop[/dim]",
        title="🎬 Terminal Video Player",
        border_style="cyan",
        box=box.ROUNDED
    ))

    try:
        # Use timg with:
        # -V: Video mode
        # -pi: iTerm2 inline images (auto-detects best protocol)
        # -g: Geometry
        # -t: Time limit
        # --title: Show filename
        cmd = [
            'timg',
            '-V',  # Video mode
            '-pi',  # Use iTerm2 protocol (or auto-detect)
            f'-g{geometry}',  # Terminal size
            f'-t{max_duration}',  # Time limit
            f'--title={label}: %b',  # Title with label
            str(video_path)
        ]

        subprocess.run(cmd, check=True)
        console.print(f"\n[green]✅ Playback complete![/green]")

    except KeyboardInterrupt:
        console.print(f"\n[yellow]⏸️  Playback stopped[/yellow]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ timg error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


def play_comparison_timg(
    original_path: str,
    processed_path: str,
    original_label: str = "INPUT (Original)",
    processed_label: str = "OUTPUT (Processed)",
    max_duration: int = 60
):
    """
    Play two videos sequentially using timg

    Note: timg doesn't support true side-by-side, so we play them in sequence

    Args:
        original_path: Path to original video
        processed_path: Path to processed video
        original_label: Label for original
        processed_label: Label for processed
        max_duration: Max duration for each video
    """
    console.print("\n[bold cyan]🎬 Video Comparison[/bold cyan]\n")
    console.print("[dim]Playing videos in sequence with real graphics[/dim]\n")

    # Play original
    play_video_timg(original_path, label=original_label, max_duration=max_duration)

    console.print("\n" + "─" * 70 + "\n")

    # Play processed
    play_video_timg(processed_path, label=processed_label, max_duration=max_duration)
