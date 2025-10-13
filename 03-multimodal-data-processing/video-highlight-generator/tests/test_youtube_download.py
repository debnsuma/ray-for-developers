#!/usr/bin/env python3
"""
Test YouTube video download and processing
"""
import sys
from pathlib import Path
import subprocess

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console

console = Console()


def check_yt_dlp():
    """Check if yt-dlp is installed"""
    result = subprocess.run(['which', 'yt-dlp'], capture_output=True)
    if result.returncode != 0:
        console.print("[bright_red]❌ yt-dlp not found. Please install it:[/bright_red]")
        console.print("[grey70]   pip install yt-dlp[/grey70]")
        console.print("[grey70]   or: brew install yt-dlp[/grey70]")
        return False

    console.print("[bright_green]✅ yt-dlp is installed[/bright_green]")
    return True


def test_download_youtube_video(url: str):
    """
    Test downloading a YouTube video

    Args:
        url: YouTube video URL
    """
    try:
        console.print(f"\n[bold bright_cyan]📥 Testing YouTube download...[/bold bright_cyan]")
        console.print(f"[grey70]URL: {url}[/grey70]\n")

        # Create download directory
        download_dir = Path("data/raw/youtube_test")
        download_dir.mkdir(parents=True, exist_ok=True)

        # Get video info first to check duration
        console.print("[bright_cyan]Step 1: Getting video info...[/bright_cyan]")
        info_cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-playlist',
            url
        ]

        result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            console.print(f"[bright_red]❌ Failed to get video info:[/bright_red]")
            console.print(f"[grey70]{result.stderr}[/grey70]")
            return None, None

        import json
        video_info = json.loads(result.stdout)
        duration = video_info.get('duration', 0)
        title = video_info.get('title', 'YouTube Video')
        video_id = video_info.get('id')

        console.print(f"[bright_green]   ✓ Title: {title}[/bright_green]")
        console.print(f"[bright_green]   ✓ Duration: {duration // 60}m {duration % 60}s[/bright_green]")
        console.print(f"[bright_green]   ✓ Video ID: {video_id}[/bright_green]")

        # Check duration limit (30 minutes = 1800 seconds)
        if duration > 1800:
            mins = duration // 60
            console.print(f"\n[bright_red]❌ Video too long: {mins} minutes[/bright_red]")
            console.print("[grey70]Please use a video shorter than 30 minutes[/grey70]")
            return None, None

        console.print(f"[bright_green]   ✓ Duration is within limit (< 30 min)[/bright_green]")

        # Download video
        console.print("\n[bright_cyan]Step 2: Downloading video...[/bright_cyan]")
        output_template = str(download_dir / '%(id)s.%(ext)s')
        download_cmd = [
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '--merge-output-format', 'mp4',
            '-o', output_template,
            '--no-playlist',
            '--progress',
            url
        ]

        result = subprocess.run(download_cmd, timeout=300)
        if result.returncode != 0:
            console.print(f"[bright_red]❌ Download failed[/bright_red]")
            return None, None

        # Find the downloaded file
        video_path = download_dir / f"{video_id}.mp4"

        if not video_path.exists():
            console.print("[bright_red]❌ Downloaded file not found[/bright_red]")
            return None, None

        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        console.print(f"[bright_green]   ✓ Downloaded: {video_path.name} ({file_size_mb:.1f} MB)[/bright_green]")

        return str(video_path), title

    except subprocess.TimeoutExpired:
        console.print("[bright_red]❌ Download timed out[/bright_red]")
        return None, None
    except Exception as e:
        console.print(f"[bright_red]❌ Error: {e}[/bright_red]")
        import traceback
        console.print(f"[grey70]{traceback.format_exc()}[/grey70]")
        return None, None


def test_process_video(video_path: str, video_name: str):
    """
    Test processing the downloaded video

    Args:
        video_path: Path to the video file
        video_name: Name of the video
    """
    try:
        console.print(f"\n[bold bright_cyan]🎬 Testing video processing...[/bold bright_cyan]")
        console.print(f"[grey70]Video: {video_name}[/grey70]")
        console.print(f"[grey70]Path: {video_path}[/grey70]\n")

        from src.pipeline import VideoHighlightPipeline

        # Initialize pipeline with auto-detection
        console.print("[bright_cyan]Step 3: Initializing pipeline...[/bright_cyan]")
        pipeline = VideoHighlightPipeline(
            num_actors=2,
            target_fps=1.0,
            resolution=(224, 224),
            auto_detect=True
        )
        console.print("[bright_green]   ✓ Pipeline initialized[/bright_green]")

        # Run pipeline
        console.print("\n[bright_cyan]Step 4: Running pipeline...[/bright_cyan]")
        console.print("[grey70]This will take some time depending on video length[/grey70]\n")

        results = pipeline.run(video_path=video_path)

        if results.get('success'):
            console.print("\n[bold bright_green]✅ Processing complete![/bold bright_green]")
            console.print(f"[bright_green]   ✓ Output: {results['output_video']}[/bright_green]")
            console.print(f"[bright_green]   ✓ Highlights found: {results['highlights']['num_highlights']}[/bright_green]")
            console.print(f"[bright_green]   ✓ Total time: {results['total_time']:.1f}s[/bright_green]")

            # Show highlight timestamps
            console.print("\n[bold bright_cyan]🎯 Detected Highlights:[/bold bright_cyan]")
            for i, h in enumerate(results['highlights']['highlights'], 1):
                mins = int(h['timestamp'] // 60)
                secs = int(h['timestamp'] % 60)
                score = h['importance_score']
                console.print(f"   {i}. {mins:02d}:{secs:02d} - score: {score:.3f}")

            return True
        else:
            console.print(f"\n[bright_red]❌ Processing failed: {results.get('error')}[/bright_red]")
            return False

    except Exception as e:
        console.print(f"\n[bright_red]❌ Processing error: {e}[/bright_red]")
        import traceback
        console.print(f"[grey70]{traceback.format_exc()}[/grey70]")
        return False


def main():
    """Main test function"""
    import argparse

    parser = argparse.ArgumentParser(description='Test YouTube download and processing')
    parser.add_argument('--url', type=str, help='YouTube URL to test')
    parser.add_argument('--no-process', action='store_true', help='Skip processing test')
    args = parser.parse_args()

    console.print("\n[bold bright_magenta]═══════════════════════════════════════════════════════════[/bold bright_magenta]")
    console.print("[bold bright_magenta]        YouTube Download & Processing Test[/bold bright_magenta]")
    console.print("[bold bright_magenta]═══════════════════════════════════════════════════════════[/bold bright_magenta]\n")

    # Check prerequisites
    console.print("[bold bright_cyan]Checking prerequisites...[/bold bright_cyan]")
    if not check_yt_dlp():
        sys.exit(1)

    # Use provided URL or default test video
    if args.url:
        url = args.url
        console.print(f"\n[bold bright_cyan]Using provided URL:[/bold bright_cyan]")
        console.print(f"[grey70]{url}[/grey70]")
    else:
        # Default: Big Buck Bunny trailer (33 seconds)
        url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
        console.print(f"\n[bold bright_cyan]Using default test video:[/bold bright_cyan]")
        console.print(f"[grey70]Big Buck Bunny Trailer (~33 seconds)[/grey70]")
        console.print(f"[grey70]{url}[/grey70]")

    # Test download
    video_path, video_name = test_download_youtube_video(url)

    if not video_path:
        console.print("\n[bright_red]❌ Download test failed[/bright_red]")
        sys.exit(1)

    console.print("\n[bold bright_green]✅ Download test passed![/bold bright_green]")

    # Test processing unless skipped
    if not args.no_process:
        console.print()
        success = test_process_video(video_path, video_name)

        if success:
            console.print("\n[bold bright_green]✅ All tests passed![/bold bright_green]")
        else:
            console.print("\n[bright_red]❌ Processing test failed[/bright_red]")
            sys.exit(1)
    else:
        console.print("\n[bright_yellow]⏭  Skipped processing test[/bright_yellow]")

    console.print("\n[bold bright_magenta]═══════════════════════════════════════════════════════════[/bold bright_magenta]")
    console.print("[bold bright_green]Test completed successfully![/bold bright_green]")
    console.print("[bold bright_magenta]═══════════════════════════════════════════════════════════[/bold bright_magenta]\n")


if __name__ == "__main__":
    main()
