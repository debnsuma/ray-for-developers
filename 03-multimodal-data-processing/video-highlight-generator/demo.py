#!/usr/bin/env python3
"""
Enhanced Interactive CLI Demo with Ray Worker Visualization
Shows parallel processing and side-by-side video comparison
"""
import sys
from pathlib import Path
import time
import threading
import subprocess
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich import box
from rich.text import Text
import ray
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import VideoHighlightPipeline

console = Console()


class RayMonitor:
    """Monitor Ray cluster and workers"""

    def __init__(self):
        self.workers = {}
        self.tasks = []
        self.resources = {}

    def update(self):
        """Update Ray cluster status"""
        if not ray.is_initialized():
            return

        try:
            # Get resources
            self.resources = ray.available_resources()

            # Get nodes
            nodes = ray.nodes()

            # Simple worker tracking
            self.workers = {
                'active': len([n for n in nodes if n['Alive']]),
                'total': len(nodes)
            }
        except:
            pass

    def get_worker_panel(self, current_phase):
        """Create worker status panel"""
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column("Status", style="bright_cyan")
        table.add_column("Info", style="grey93")

        # Phase indicator
        phase_emoji = {
            'SETUP': '🔧',
            'PHASE 1': '📹',
            'PHASE 2': '🧠',
            'PHASE 3': '🎯',
            'PHASE 4': '🎬',
            'PIPELINE': '✨'
        }

        emoji = '⚡'
        for key in phase_emoji:
            if key in current_phase:
                emoji = phase_emoji[key]
                break

        table.add_row(f"{emoji} Status", current_phase)

        # Workers
        if self.workers:
            table.add_row("👥 Workers", f"{self.workers.get('active', 0)} active")

        # Resources
        if self.resources:
            cpu = self.resources.get('CPU', 0)
            memory = self.resources.get('memory', 0) / 1e9
            table.add_row("💻 CPU", f"{cpu:.0f} cores available")
            table.add_row("🧠 Memory", f"{memory:.1f} GB")

            if 'GPU' in self.resources:
                table.add_row("🎮 GPU", f"{self.resources['GPU']:.0f} available")

        return Panel(
            table,
            title="[bold bright_magenta]⚡ RAY CLUSTER STATUS ⚡[/bold bright_magenta]",
            border_style="bright_magenta",
            box=box.DOUBLE
        )


class ParallelTaskVisualizer:
    """Visualize parallel task execution"""

    def __init__(self):
        self.tasks = {}
        self.max_tasks = 10

    def add_task(self, task_id, description, worker_id=0):
        """Add a task"""
        self.tasks[task_id] = {
            'description': description,
            'worker': worker_id,
            'status': 'running',
            'start_time': time.time()
        }

        # Keep only recent tasks
        if len(self.tasks) > self.max_tasks:
            oldest = min(self.tasks.keys(), key=lambda k: self.tasks[k]['start_time'])
            del self.tasks[oldest]

    def complete_task(self, task_id):
        """Mark task as complete"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'complete'

    def get_panel(self):
        """Create parallel tasks panel"""
        table = Table(box=box.SIMPLE, show_header=True)
        table.add_column("Worker", style="bright_magenta", width=8)
        table.add_column("Task", style="bright_cyan")
        table.add_column("Status", style="bright_green", width=12)

        # Calculate animation frame for progress bar
        anim_frame = int(time.time() * 4) % 8
        progress_chars = ["▱▱▱▱▱", "▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱",
                        "▰▰▰▰▱", "▰▰▰▰▰", "▰▰▰▰▱", "▰▰▰▱▱"]

        if not self.tasks:
            table.add_row("--", "Waiting for tasks...", "")
        else:
            for task_id, task_info in list(self.tasks.items())[-8:]:
                worker = f"Worker {task_info['worker'] + 1}"
                desc = task_info['description'][:40]

                if task_info['status'] == 'running':
                    status = f"[bright_yellow]{progress_chars[anim_frame]}[/bright_yellow]"
                else:
                    status = "✅ Done"

                table.add_row(worker, desc, status)

        return Panel(
            table,
            title="[bold bright_cyan]🔄 PARALLEL TASKS 🔄[/bold bright_cyan]",
            border_style="bright_cyan",
            box=box.DOUBLE
        )


def create_layout():
    """Create rich layout"""
    layout = Layout()

    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )

    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )

    layout["left"].split_column(
        Layout(name="progress", size=10),
        Layout(name="logs", minimum_size=15)
    )

    layout["right"].split_column(
        Layout(name="cluster", size=12),
        Layout(name="tasks", minimum_size=15)
    )

    return layout


def show_welcome():
    """Display welcome screen"""
    console.clear()
    welcome = """
[bold bright_magenta on black]
╔════════════════════════════════════════════════════════════════════════════════╗[/bold bright_magenta on black]
[bold bright_cyan on black]║                                                                                ║[/bold bright_cyan on black]
[bold bright_blue on black]║                ██╗   ██╗██╗██████╗ ███████╗ ██████╗                            ║[/bold bright_blue on black]
[bold bright_cyan on black]║                ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗                           ║[/bold bright_cyan on black]
[bold cyan on black]║                ██║   ██║██║██║  ██║█████╗  ██║   ██║                           ║[/bold cyan on black]
[bold bright_green on black]║                ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║                           ║[/bold bright_green on black]
[bold green on black]║                 ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝                           ║[/bold green on black]
[bold bright_yellow on black]║                  ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝                            ║[/bold bright_yellow on black]
[bold yellow on black]║                                                                                ║[/bold yellow on black]
[bold bright_red on black]║     ██╗  ██╗██╗ ██████╗ ██╗  ██╗██╗     ██╗ ██████╗ ██╗  ██╗████████╗          ║[/bold bright_red on black]
[bold red on black]║     ██║  ██║██║██╔════╝ ██║  ██║██║     ██║██╔════╝ ██║  ██║╚══██╔══╝          ║[/bold red on black]
[bold bright_magenta on black]║     ███████║██║██║  ███╗███████║██║     ██║██║  ███╗███████║   ██║             ║[/bold bright_magenta on black]
[bold magenta on black]║     ██╔══██║██║██║   ██║██╔══██║██║     ██║██║   ██║██╔══██║   ██║             ║[/bold magenta on black]
[bold bright_blue on black]║     ██║  ██║██║╚██████╔╝██║  ██║███████╗██║╚██████╔╝██║  ██║   ██║             ║[/bold bright_blue on black]
[bold bright_cyan on black]║     ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝             ║[/bold bright_cyan on black]
[bold cyan on black]║                                                                                ║[/bold cyan on black]
[bold bright_green on black]║   ██████╗ ███████╗███╗   ██╗███████╗██████╗  █████╗ ████████╗ ██████╗ ██████╗  ║[/bold bright_green on black]
[bold green on black]║  ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗ ║[/bold green on black]
[bold bright_yellow on black]║  ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝███████║   ██║   ██║   ██║██████╔╝ ║[/bold bright_yellow on black]
[bold yellow on black]║  ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗ ║[/bold yellow on black]
[bold bright_red on black]║  ╚██████╔╝███████╗██║ ╚████║███████╗██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║ ║[/bold bright_red on black]
[bold red on black]║   ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ║[/bold red on black]
[bold bright_magenta on black]║                                                                                ║[/bold bright_magenta on black]
[bold bright_cyan on black]║                      Powered by Ray, PyTorch & MobileNetV3                     ║[/bold bright_cyan on black]
[bold bright_blue on black]║                                                                                ║[/bold bright_blue on black]
[bold bright_magenta on black]╚════════════════════════════════════════════════════════════════════════════════╝[/bold bright_magenta on black]

[bold grey93]✨ Key Features:[/bold grey93]
  ⚡ [bold bright_magenta]Real-time Ray worker visualization[/bold bright_magenta]
  📊 Parallel task execution monitoring
  🎬 Terminal & native video playback
  🚀 Complete pipeline in ~5-30 seconds

[grey70]Watch as [bold bright_magenta]Ray[/bold bright_magenta] distributes work across parallel workers![/grey70]
    """
    console.print(welcome)


def download_youtube_video(url: str) -> tuple[str, str]:
    """
    Download YouTube video using yt-dlp

    Args:
        url: YouTube video URL

    Returns:
        Tuple of (video_path, video_title)
    """
    try:
        # Check if yt-dlp is installed
        result = subprocess.run(['which', 'yt-dlp'], capture_output=True)
        if result.returncode != 0:
            console.print("[bright_red]❌ yt-dlp not found. Please install it:[/bright_red]")
            console.print("[grey70]   pip install yt-dlp[/grey70]")
            console.print("[grey70]   or: brew install yt-dlp[/grey70]")
            sys.exit(1)

        console.print("\n[bold bright_cyan]📥 Downloading YouTube video...[/bold bright_cyan]")

        # Create download directory
        download_dir = Path("data/raw/youtube")
        download_dir.mkdir(parents=True, exist_ok=True)

        # Get video info first to check duration
        info_cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-playlist',
            url
        ]

        result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            console.print(f"[bright_red]❌ Failed to get video info: {result.stderr}[/bright_red]")
            sys.exit(1)

        import json
        video_info = json.loads(result.stdout)
        duration = video_info.get('duration', 0)
        title = video_info.get('title', 'YouTube Video')

        # Check duration limit (30 minutes = 1800 seconds)
        if duration > 1800:
            mins = duration // 60
            console.print(f"[bright_red]❌ Video too long: {mins} minutes[/bright_red]")
            console.print("[grey70]Please use a video shorter than 30 minutes[/grey70]")
            sys.exit(1)

        # Download video
        output_template = str(download_dir / '%(id)s.%(ext)s')
        download_cmd = [
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '--merge-output-format', 'mp4',
            '-o', output_template,
            '--no-playlist',
            url
        ]

        console.print(f"[grey70]   Title: {title}[/grey70]")
        console.print(f"[grey70]   Duration: {duration // 60}m {duration % 60}s[/grey70]")

        result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            console.print(f"[bright_red]❌ Download failed: {result.stderr}[/bright_red]")
            sys.exit(1)

        # Find the downloaded file
        video_id = video_info.get('id')
        video_path = download_dir / f"{video_id}.mp4"

        if not video_path.exists():
            console.print("[bright_red]❌ Downloaded file not found[/bright_red]")
            sys.exit(1)

        console.print(f"[bright_green]✅ Downloaded: {title}[/bright_green]\n")

        return str(video_path), title

    except subprocess.TimeoutExpired:
        console.print("[bright_red]❌ Download timed out[/bright_red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bright_red]❌ Error downloading video: {e}[/bright_red]")
        sys.exit(1)


def get_video_choice():
    """Get user's video choice"""
    table = Table(title="📹 Select Video Source", box=box.ROUNDED)
    table.add_column("Option", style="bright_cyan", width=8)
    table.add_column("Video", style="bright_magenta")
    table.add_column("Duration", style="bright_green", width=12)
    table.add_column("Time", style="bright_yellow", width=15)

    table.add_row("1", "🔥 For Bigger Blazes", "15 sec", "~5 sec")
    table.add_row("2", "🐰 Big Buck Bunny", "10 min", "~25-30 sec")
    table.add_row("3", "🐘 Elephants Dream", "11 min", "~28-33 sec")
    table.add_row("4", "🎥 YouTube URL", "< 30 min", "varies")

    console.print(table)
    console.print()

    video_map = {
        '1': ('data/raw/demo/for_bigger_blazes.mp4', 'For Bigger Blazes'),
        '2': ('data/raw/demo/big_buck_bunny.mp4', 'Big Buck Bunny'),
        '3': ('data/raw/demo/elephants_dream.mp4', 'Elephants Dream'),
    }

    while True:
        choice = console.input("[bold bright_cyan]Select (1-4):[/bold bright_cyan] ").strip()

        if choice == '4':
            # YouTube URL input
            console.print()
            url = console.input("[bold bright_cyan]🔗 Enter YouTube URL:[/bold bright_cyan] ").strip()
            if not url:
                console.print("[bright_red]Invalid URL[/bright_red]")
                continue

            # Validate YouTube URL
            if 'youtube.com' not in url and 'youtu.be' not in url:
                console.print("[bright_red]❌ Invalid YouTube URL[/bright_red]")
                continue

            return download_youtube_video(url)

        elif choice in video_map:
            video_path, video_name = video_map[choice]
            if Path(video_path).exists():
                return video_path, video_name
            else:
                console.print(f"[bright_red]❌ Video not found. Run: python scripts/download_sample_videos.py[/bright_red]")
                sys.exit(1)

        console.print("[bright_red]Invalid choice. Please enter 1-4[/bright_red]")


def get_settings():
    """Get pipeline settings"""
    console.print("\n[bold bright_cyan]⚙️  Pipeline Configuration[/bold bright_cyan]")
    console.print("[grey70]Using intelligent auto-detection (analyzes video content)[/grey70]\n")

    mode = console.input("[bright_cyan]Use auto mode? (y/n) [y]:[/bright_cyan] ").strip().lower() or 'y'

    if mode == 'y':
        console.print("[bright_green]✓ Auto mode enabled - AI will determine optimal settings[/bright_green]")
        return 'auto', None, None
    else:
        num_highlights = console.input("[bright_cyan]Highlights (1-10) [5]:[/bright_cyan] ").strip() or "5"
        clip_duration = console.input("[bright_cyan]Clip duration (1-10s) [3.0]:[/bright_cyan] ").strip() or "3.0"
        return 'manual', int(num_highlights), float(clip_duration)


def process_with_visualization(video_path, video_name, mode, num_highlights, clip_duration):
    """Process video with live visualization"""

    # Initialize monitors
    ray_monitor = RayMonitor()
    task_viz = ParallelTaskVisualizer()

    # Progress tracking
    phase_progress = {
        'phase_1': 0,
        'phase_2': 0,
        'phase_3': 0,
        'phase_4': 0,
    }

    current_phase = "Initializing..."
    log_messages = []

    # Task counter for simulation
    task_counter = [0]

    def progress_callback(phase, message):
        """Callback for pipeline progress"""
        nonlocal current_phase
        current_phase = f"[bright_cyan]{phase}[/bright_cyan]: {message}"

        timestamp = time.strftime("%H:%M:%S")

        # Highlight Ray-related activities
        highlighted_msg = message[:50]
        ray_keywords = ['Ray', 'Actor', 'worker', 'parallel', 'distributed', 'cluster']

        for keyword in ray_keywords:
            if keyword in highlighted_msg:
                # Highlight the keyword in bright magenta
                highlighted_msg = highlighted_msg.replace(
                    keyword,
                    f"[bold bright_magenta]{keyword}[/bold bright_magenta]"
                )

        log_messages.append(f"[grey70]{timestamp}[/grey70] {highlighted_msg}")
        if len(log_messages) > 12:
            log_messages.pop(0)

        # Update progress
        if "PHASE 1" in phase:
            phase_progress['phase_1'] = 100 if "complete" in message.lower() else 50

            # Add preprocessing tasks
            if "Starting preprocessing" in message:
                task_viz.add_task(f"task_prep_1", "Extract frames", worker_id=0)
                task_viz.add_task(f"task_prep_2", "Extract audio", worker_id=0)
            elif "complete" in message.lower():
                task_viz.complete_task(f"task_prep_1")
                task_viz.complete_task(f"task_prep_2")

        elif "PHASE 2" in phase:
            phase_progress['phase_1'] = 100
            phase_progress['phase_2'] = 100 if "complete" in message.lower() else 50

            # Add feature extraction tasks - simulate parallel processing
            if "Creating" in message and "Actors" in message:
                # Create tasks for both workers
                task_viz.add_task(f"task_feat_w0", "Loading model on Worker 1", worker_id=0)
                task_viz.add_task(f"task_feat_w1", "Loading model on Worker 2", worker_id=1)
            elif "Feature extraction" in message:
                task_viz.complete_task(f"task_feat_w0")
                task_viz.complete_task(f"task_feat_w1")
                # Add processing tasks
                for i in range(4):
                    task_viz.add_task(f"task_frame_{i}", f"Process frames {i*4}-{i*4+3}", worker_id=i % 2)
            elif "complete" in message.lower():
                # Complete all frame tasks
                for i in range(4):
                    task_viz.complete_task(f"task_frame_{i}")

        elif "PHASE 3" in phase:
            phase_progress['phase_2'] = 100
            phase_progress['phase_3'] = 100 if "complete" in message.lower() else 50

            if "Starting" in message:
                task_viz.add_task(f"task_detect", "Compute importance scores", worker_id=0)
            elif "complete" in message.lower():
                task_viz.complete_task(f"task_detect")

        elif "PHASE 4" in phase:
            phase_progress['phase_3'] = 100
            phase_progress['phase_4'] = 100 if "complete" in message.lower() else 50

            # Video generation tasks
            if "Starting" in message:
                task_viz.add_task(f"task_gen_1", "Extract clips", worker_id=0)
                task_viz.add_task(f"task_gen_2", "Add transitions", worker_id=1)
            elif "complete" in message.lower():
                task_viz.complete_task(f"task_gen_1")
                task_viz.complete_task(f"task_gen_2")

    # Create pipeline
    console.print("\n[bold bright_cyan]🔧 Initializing Pipeline...[/bold bright_cyan]\n")

    if mode == 'auto':
        console.print("[bright_green]Using intelligent auto-detection mode[/bright_green]\n")
        pipeline = VideoHighlightPipeline(
            num_actors=2,
            target_fps=1.0,
            resolution=(224, 224),
            auto_detect=True,
            progress_callback=progress_callback
        )
    else:
        console.print(f"[bright_yellow]Using manual mode: {num_highlights} highlights, {clip_duration}s clips[/bright_yellow]\n")
        pipeline = VideoHighlightPipeline(
            num_actors=2,
            target_fps=1.0,
            resolution=(224, 224),
            num_highlights=num_highlights,
            clip_duration=clip_duration,
            auto_detect=False,
            progress_callback=progress_callback
        )

    # Create layout
    layout = create_layout()

    # Results storage
    results = {}
    error = None

    def run_pipeline():
        """Run pipeline in background thread"""
        nonlocal results, error
        try:
            results.update(pipeline.run(video_path=video_path))
        except Exception as e:
            error = e

    # Start processing
    thread = threading.Thread(target=run_pipeline, daemon=True)
    start_time = time.time()
    thread.start()

    # Live display
    with Live(layout, console=console, refresh_per_second=4, screen=True):
        while thread.is_alive():
            # Update monitors
            ray_monitor.update()

            # Header
            layout["header"].update(
                Panel(
                    f"[bold grey93]Processing:[/bold grey93] [bright_cyan]{video_name}[/bright_cyan] │ "
                    f"[bold grey93]Mode:[/bold grey93] [bright_magenta]Parallel Ray Workers[/bright_magenta]",
                    style="bold grey93 on grey19"
                )
            )

            # Progress section with animated progress bar
            progress_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
            progress_table.add_column("Phase", style="bright_cyan", width=20)
            progress_table.add_column("Progress", style="grey93")

            # Calculate animation frame based on elapsed time
            anim_frame = int((time.time() - start_time) * 4) % 8
            progress_chars = ["▱▱▱▱▱▱▱", "▰▱▱▱▱▱▱", "▰▰▱▱▱▱▱", "▰▰▰▱▱▱▱",
                            "▰▰▰▰▱▱▱", "▰▰▰▰▰▱▱", "▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰"]

            for phase_name, phase_num in [("📹 Preprocessing", 'phase_1'),
                                          ("🧠 Feature Extract", 'phase_2'),
                                          ("🎯 Detect Highlights", 'phase_3'),
                                          ("🎬 Generate Video", 'phase_4')]:
                progress_val = phase_progress[phase_num]

                if progress_val == 0:
                    bar = "⏳ Waiting"
                elif progress_val == 100:
                    bar = "✅ Complete"
                else:
                    # Show animated progress bar
                    bar = f"[bright_yellow]{progress_chars[anim_frame]}[/bright_yellow] Processing..."

                progress_table.add_row(phase_name, bar)

            layout["progress"].update(
                Panel(
                    progress_table,
                    title="[bold bright_cyan]🚀 PIPELINE PROGRESS 🚀[/bold bright_cyan]",
                    border_style="bright_cyan",
                    box=box.DOUBLE
                )
            )

            # Logs section
            log_text = "\n".join(log_messages) if log_messages else "[grey70]Waiting for updates...[/grey70]"
            layout["logs"].update(
                Panel(
                    log_text,
                    title="[bold bright_yellow]📋 ACTIVITY LOG 📋[/bold bright_yellow]",
                    border_style="bright_yellow",
                    box=box.DOUBLE
                )
            )

            # Ray cluster status
            layout["cluster"].update(ray_monitor.get_worker_panel(current_phase))

            # Parallel tasks
            layout["tasks"].update(task_viz.get_panel())

            # Footer
            elapsed = time.time() - start_time
            layout["footer"].update(
                Panel(
                    f"[bold grey93]Elapsed:[/bold grey93] [bright_cyan]{elapsed:.1f}s[/bright_cyan] │ "
                    f"[bold grey93]Status:[/bold grey93] [bright_green]Processing in parallel...[/bright_green]",
                    style="bold grey93 on grey19"
                )
            )

            time.sleep(0.25)

        thread.join()

        # Keep the final processing window visible for 3 seconds
        if not error:
            # Update to show completion status
            layout["header"].update(
                Panel(
                    f"[bold grey93]Processing:[/bold grey93] [bright_cyan]{video_name}[/bright_cyan] │ "
                    f"[bold grey93]Status:[/bold grey93] [bright_green]✅ COMPLETE![/bright_green]",
                    style="bold grey93 on green4"
                )
            )

            # Update footer
            total_time = time.time() - start_time
            layout["footer"].update(
                Panel(
                    f"[bold grey93]Total Time:[/bold grey93] [bright_cyan]{total_time:.1f}s[/bright_cyan]│ "
                    f"[bold grey93]Status:[/bold grey93] [bright_green]✅ Processing complete![/bright_green]",
                    style="bold grey93 on green4"
                )
            )

            # Hold for 3 seconds to show completion
            time.sleep(3)

    if error:
        raise error

    return results


def show_peak_moments_chart(results):
    """Display importance scores and peak moments chart in terminal using matplotlib"""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import tempfile

        if 'highlights' not in results or 'importance_scores' not in results['highlights']:
            return

        importance_scores = results['highlights']['importance_scores']
        highlights = results['highlights']['highlights']
        target_fps = results['highlights'].get('target_fps', 1.0)
        duration = results['highlights'].get('duration', len(importance_scores) / target_fps)

        # Create time axis (in seconds)
        time_axis = np.arange(len(importance_scores)) / target_fps

        console.print("\n" + "═" * 100)
        console.print("[bold bright_magenta]" + " " * 32 + "📊 IMPORTANCE SCORES & PEAKS 📊" + " " * 32 + "[/bold bright_magenta]")
        console.print("═" * 100 + "\n")

        # Create matplotlib figure with dark theme
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(14, 6), facecolor='#1a1a1a')
        ax.set_facecolor('#1a1a1a')

        # Plot the importance scores
        ax.plot(time_axis, importance_scores,
                color='#00d9ff', linewidth=2.5, label='Importance Score', alpha=0.9)

        # Fill area under the curve
        ax.fill_between(time_axis, importance_scores, alpha=0.3, color='#00d9ff')

        # Mark the detected peaks
        peak_times = [h['timestamp'] for h in highlights]
        peak_scores = [h['importance_score'] for h in highlights]
        ax.scatter(peak_times, peak_scores,
                  color='#ff00ff', s=200, marker='*',
                  edgecolors='white', linewidths=1.5,
                  label='Detected Peaks', zorder=5)

        # Add vertical lines at peaks
        for peak_time in peak_times:
            ax.axvline(x=peak_time, color='#ff00ff', alpha=0.3, linestyle='--', linewidth=1)

        # Configure plot
        ax.set_xlabel('Time (seconds)', fontsize=12, color='#cccccc')
        ax.set_ylabel('Importance Score', fontsize=12, color='#cccccc')
        ax.set_title('Video Importance Score Over Time (Highlights Marked)',
                    fontsize=14, fontweight='bold', color='#00d9ff', pad=20)

        # Grid styling
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        ax.set_xlim(0, duration)
        ax.set_ylim(0, 1.05)

        # Legend
        ax.legend(loc='upper right', fontsize=10, framealpha=0.8, facecolor='#2a2a2a')

        # Tick styling
        ax.tick_params(colors='#cccccc', labelsize=10)

        # Tight layout
        plt.tight_layout()

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
            plt.savefig(tmp_path, dpi=100, facecolor='#1a1a1a', edgecolor='none')
            plt.close()

        # Display the image in terminal using timg
        from src.utils.timg_video_player import check_timg_available

        if check_timg_available():
            try:
                # Use timg to display the image directly in terminal (no capture)
                # This allows the image to render properly using terminal graphics protocols
                subprocess.run(
                    ['timg', '-g', '120x30', tmp_path],
                    timeout=5
                )
                console.print()  # Add spacing after image
            except Exception as e:
                console.print(f"[grey70]Chart generated but display failed: {e}[/grey70]")
                console.print(f"[grey70]Chart saved to: {tmp_path}[/grey70]")
        else:
            console.print(f"[grey70]💡 Chart saved to: {tmp_path}[/grey70]")
            console.print(f"[grey70]💡 Install 'timg' to display charts in terminal: brew install timg[/grey70]")

        console.print()

        # Clean up
        try:
            Path(tmp_path).unlink()
        except:
            pass

    except ImportError as e:
        console.print(f"\n[grey70]💡 Could not generate chart visualization: {e}[/grey70]\n")
    except Exception as e:
        console.print(f"\n[grey70]Chart generation error: {e}[/grey70]\n")


def display_results(results, video_name):
    """Display results summary"""
    console.print("\n" + "═" * 70)
    console.print("[bold bright_green]✅ PIPELINE COMPLETE![/bold bright_green]")
    console.print("═" * 70 + "\n")

    # Summary
    summary = Table(box=box.ROUNDED, show_header=False, expand=True)
    summary.add_column("Metric", style="bright_cyan", width=40)
    summary.add_column("Value", style="bright_green", width=30)

    summary.add_row("📹 Video", video_name)
    summary.add_row("⏱️  Total Time", f"{results['total_time']:.1f}s")

    if 'preprocessing' in results:
        summary.add_row("  └─ Preprocessing", f"{results['preprocessing'].get('elapsed', 0):.1f}s")
    if 'features' in results:
        fps = results['features'].get('num_frames', 0) / results['features'].get('elapsed', 1)
        summary.add_row("  └─ Feature Extraction", f"{results['features'].get('elapsed', 0):.1f}s ({fps:.0f} FPS)")
    if 'highlights' in results:
        summary.add_row("  └─ Highlight Detection", f"{results['highlights'].get('elapsed', 0):.1f}s")
    if 'generation' in results:
        summary.add_row("  └─ Video Generation", f"{results['generation'].get('elapsed', 0):.1f}s")

    summary.add_row("🎯 Highlights Found", str(results['highlights'].get('num_highlights', 0)))
    summary.add_row("💾 Output Size", f"{results['generation'].get('output_size_mb', 0):.1f} MB")

    console.print(Panel(summary, title="📊 Pipeline Summary", border_style="bright_green"))

    # Show peak moments visualization
    show_peak_moments_chart(results)

    # Highlights
    if 'highlights' in results:
        console.print("\n[bold bright_cyan]🎯 Detected Highlights:[/bold bright_cyan]\n")

        for i, h in enumerate(results['highlights']['highlights'], 1):
            mins = int(h['timestamp'] // 60)
            secs = int(h['timestamp'] % 60)
            score = h['importance_score']

            bar_length = int(score * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            console.print(f"  {i}. [bright_cyan]{mins:02d}:{secs:02d}[/bright_cyan] │ {bar} │ [bright_green]{score:.3f}[/bright_green]")

        console.print()


def play_videos_embedded(original_path, highlight_path):
    """Play highlight video directly in terminal"""
    # Check if timg is available for real terminal video
    from src.utils.timg_video_player import check_timg_available

    if check_timg_available():
        try:
            from src.utils.timg_video_player import play_video_timg

            # Directly play the highlight reel (output) in terminal
            console.print()
            play_video_timg(highlight_path, label="OUTPUT (Highlight Reel)", max_duration=60)

        except Exception as e:
            console.print(f"[bright_red]❌ Terminal playback error: {e}[/bright_red]")
            console.print("[bright_yellow]Falling back to native player...[/bright_yellow]\n")
            play_videos_separately(original_path, highlight_path)
    else:
        # timg not available, use native player
        console.print("[bright_yellow]💡 Tip: Install 'timg' to play videos in terminal[/bright_yellow]")
        console.print("[grey70]   brew install timg[/grey70]\n")
        play_videos_separately(original_path, highlight_path)


def play_videos_separately(original_path, highlight_path):
    """Play original and highlight videos in separate windows"""
    console.print("\n[bold bright_cyan]🎬 Opening Videos...[/bold bright_cyan]\n")

    try:
        import platform
        system = platform.system()

        console.print("[bright_cyan]Opening original video...[/bright_cyan]")
        if system == 'Darwin':  # macOS
            subprocess.run(['open', original_path])
        elif system == 'Linux':
            subprocess.run(['xdg-open', original_path])
        elif system == 'Windows':
            subprocess.run(['start', original_path], shell=True)

        time.sleep(1)  # Brief pause between opening videos

        console.print("[bright_cyan]Opening highlight reel...[/bright_cyan]\n")
        if system == 'Darwin':  # macOS
            subprocess.run(['open', highlight_path])
        elif system == 'Linux':
            subprocess.run(['xdg-open', highlight_path])
        elif system == 'Windows':
            subprocess.run(['start', highlight_path], shell=True)

        console.print(Panel(
            "[bold bright_green]✅ Videos Opened![/bold bright_green]\n\n"
            "[grey93]Two video players launched:[/grey93]\n"
            f"  📹 [bright_cyan]Original:[/bright_cyan] {Path(original_path).name}\n"
            f"  ✨ [bright_green]Highlight Reel:[/bright_green] {Path(highlight_path).name}\n\n"
            "[grey70]Watch both to compare the full video with extracted highlights![/grey70]",
            title="🎬 Video Playback",
            border_style="bright_green",
            box=box.DOUBLE
        ))

    except Exception as e:
        console.print(f"[bright_red]❌ Error opening videos: {e}[/bright_red]")
        console.print(f"\n[bright_yellow]📹 Original:[/bright_yellow] {original_path}")
        console.print(f"[bright_yellow]✨ Highlight Reel:[/bright_yellow] {highlight_path}")
        console.print("\n[grey70]Open these files manually in your video player[/grey70]")


def show_pipeline_architecture():
    """Display pipeline architecture visualization in flowchart format"""
    console.print("\n" + "═" * 100)
    console.print("[bold bright_cyan]" + " " * 32 + "📐 PIPELINE ARCHITECTURE 📐" + " " * 32 + "[/bold bright_cyan]")
    console.print("═" * 100 + "\n")

    architecture = """
[bold bright_cyan]        ┌──────────────────────────────────────────────────────────────────────────────────────┐
        │                                                                                      │
        │                            VIDEO HIGHLIGHT PIPELINE                                  │
        │                         Powered by Ray, PyTorch & MobileNetV3                        │
        │                                                                                      │
        └──────────────────────────────────────────┬───────────────────────────────────────────┘[/bold bright_cyan]
                                                   │
                                                   │  [grey93]📹 Input: MP4 Video[/grey93]
                                                   │
                                                   ▼
[bold bright_yellow]        ┌──────────────────────────────────────────────────────────────────────────────────────┐
        │                           PHASE 1: PREPROCESSING                                     │
        │                          FFmpeg + Ray Parallel Tasks                                 │
        └──────────────────────────────────────────────────────────────────────────────────────┘[/bold bright_yellow]
                 │                                                              │
                 │                                                              │
                 ▼                                                              ▼
           [grey93]Extract Frames                                            Extract Audio[/grey93]
           [grey93]1 FPS @ 224×224                                           16kHz WAV[/grey93]
                 │                                                              │
                 └────────────────────────────┬─────────────────────────────────┘
                                              │
                                              ▼
[bold bright_magenta]        ┌──────────────────────────────────────────────────────────────────────────────────────┐
        │                         PHASE 2: FEATURE EXTRACTION                                  │
        │                        MobileNetV3 + Ray Actors (Parallel)                           │
        └──────────────────────────────────────────────────────────────────────────────────────┘[/bold bright_magenta]
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
              [bold bright_magenta][Ray Actor 0][/bold bright_magenta]            [bold bright_magenta][Ray Actor 1][/bold bright_magenta]            [bold bright_magenta][Ray Actor N][/bold bright_magenta]
              [grey93]MobileNetV3              MobileNetV3              MobileNetV3[/grey93]
              [grey93]Frames 0-33%             Frames 33-66%            Frames 66-100%[/grey93]
                    │                         │                         │
                    └─────────────────────────┼─────────────────────────┘
                                              │
                                              ▼
                                    [grey93]1280-dim features
                                    per frame[/grey93]
                                              │
                                              ▼
[bold bright_green]        ┌──────────────────────────────────────────────────────────────────────────────────────┐
        │                         PHASE 3: HIGHLIGHT DETECTION                                 │
        │                       Intelligent Auto-Detection Algorithm                           │
        └──────────────────────────────────────────────────────────────────────────────────────┘[/bold bright_green]
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
                [grey93]Feature                 Feature                 Motion[/grey93]
                [grey93]Variance                Novelty                 Analysis[/grey93]
                    │                         │                         │
                    └─────────────────────────┼─────────────────────────┘
                                              │
                                              ▼
                                    [grey93]Importance Scores
                                    Peak Detection
                                    Adaptive Thresholds[/grey93]
                                              │
                                              ▼
[bold bright_cyan]        ┌──────────────────────────────────────────────────────────────────────────────────────┐
        │                          PHASE 4: VIDEO GENERATION                                   │
        │                         FFmpeg + Transitions (30s max)                               │
        └──────────────────────────────────────────────────────────────────────────────────────┘[/bold bright_cyan]
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
                [grey93]Extract                 Add                     Concatenate[/grey93]
                [grey93]Clips                   Fades                   Segments[/grey93]
                    │                         │                         │
                    └─────────────────────────┼─────────────────────────┘
                                              │
                                              ▼
[bold bright_green]        ┌──────────────────────────────────────────────────────────────────────────────────────┐
        │                                                                                      │
        │                            OUTPUT (≤30s Highlight Reel)                              │
        │                                                                                      │
        │              📹 MP4 Video         📊 JSON Metadata         📈 Statistics             │
        │                                                                                      │
        └──────────────────────────────────────────────────────────────────────────────────────┘[/bold bright_green]
"""

    console.print(architecture)

    # Ray Deployment Architecture
    console.print("\n" + "═" * 100)
    console.print("[bold bright_cyan]" + " " * 32 + "⚡ RAY DEPLOYMENT ⚡" + " " * 32 + "[/bold bright_cyan]")
    console.print("[grey93]" + " " * 18 + "Video Highlight Generator - Powered by Ray, PyTorch & MobileNetV3" + " " * 18 + "[/grey93]\n")
    console.print("═" * 100 + "\n")

    deployment = """
[bold bright_cyan]        ┌──────────────────────────────────────────────────────────────────────────────────────┐
        │                                M4 MacBook Pro (Local)                                │
        │                                                                                      │
        │         [bright_yellow]┌──────────────────────────────────────────────────────────────┐[/bright_yellow]             │
        │         [bright_yellow]│                        Ray Head Node                         │[/bright_yellow]             │
        │         [bright_yellow]│                       (localhost:8265)                       │[/bright_yellow]             │
        │         [bright_yellow]└─────────────────────────────┬────────────────────────────────┘[/bright_yellow]             │
        │                                     │                                                │
        │                  ┌──────────────────┼──────────────────┐                             │
        │                  │                  │                  │                             │
        │                  ▼                  ▼                  ▼                             │
        │            [bold bright_magenta][Worker 0][/bold bright_magenta]         [bold bright_magenta][Worker 1][/bold bright_magenta]         [bold bright_magenta][Worker 2][/bold bright_magenta]                          │
        │            [grey93]CPU: 2 cores     CPU: 2 cores     CPU: 2 cores[/grey93]                            │
        │            [grey93]MPS: shared      MPS: shared      MPS: shared[/grey93]                             │
        │            [grey93]Features: 33%    Features: 33%    Features: 34%[/grey93]                           │
        │                                                                                      │
        └──────────────────────────────────────────────────────────────────────────────────────┘[/bold bright_cyan]
"""

    console.print(deployment)

    # Key Tools/Frameworks
    console.print("\n[bold bright_cyan]" + " " * 35 + "🔧 TOOLS/FRAMEWORKS" + " " * 35 + "[/bold bright_cyan]\n")

    tech_table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2), border_style="bright_cyan")
    tech_table.add_column("Technology", style="bright_magenta", width=30)
    tech_table.add_column("Purpose", style="grey93", width=55)

    tech_table.add_row("📹 FFmpeg", "Video/audio processing and manipulation")
    tech_table.add_row("⚡ Ray", "[bold bright_magenta]Distributed computing & parallel processing[/bold bright_magenta]")
    tech_table.add_row("🧠 MobileNetV3", "Efficient visual feature extraction")
    tech_table.add_row("🐍 PyTorch", "Deep learning framework")
    tech_table.add_row("📊 NumPy/SciPy", "Numerical computing and signal processing")
    tech_table.add_row("🎨 Rich", "Beautiful terminal UI")

    console.print(tech_table)

    # Performance metrics
    console.print("\n[bold bright_green]" + " " * 30 + "⚡ PERFORMANCE (M4 MacBook Pro)" + " " * 30 + "[/bold bright_green]\n")

    perf_table = Table(box=box.ROUNDED, show_header=True, border_style="bright_green")
    perf_table.add_column("Phase", style="bright_yellow", width=35)
    perf_table.add_column("Time", style="bright_green", width=20)
    perf_table.add_column("Speed", style="bright_cyan", width=25)

    perf_table.add_row("📹 Preprocessing", "~1-2 sec", "FFmpeg optimized")
    perf_table.add_row("🧠 Feature Extraction", "~3-10 sec", "30-60 FPS (CPU)")
    perf_table.add_row("🎯 Highlight Detection", "< 1 sec", "Near instant")
    perf_table.add_row("🎬 Video Generation", "~1-2 sec", "FFmpeg concat")
    perf_table.add_row("[bold]📊 TOTAL (10-min video)[/bold]", "[bold]~5-30 sec[/bold]", "[bold]12-120x realtime[/bold]")

    console.print(perf_table)
    console.print()


def main():
    """Main demo function"""
    try:
        # Welcome
        show_welcome()
        time.sleep(1)

        # Select video
        video_path, video_name = get_video_choice()

        # Get settings
        mode, num_highlights, clip_duration = get_settings()

        # Confirm
        console.print()
        confirm = console.input("[bold bright_cyan]🚀 Start processing? (y/n):[/bold bright_cyan] ").strip().lower()
        if confirm != 'y':
            console.print("[bright_yellow]Cancelled. Goodbye! 👋[/bright_yellow]")
            return

        # Process with visualization
        results = process_with_visualization(video_path, video_name, mode, num_highlights, clip_duration)

        if not results.get('success'):
            console.print(f"\n[bold bright_red]❌ Pipeline failed: {results.get('error')}[/bold bright_red]")
            return

        # Display results
        display_results(results, video_name)

        # Offer to play videos
        console.print()
        play_choice = console.input(
            "[bold bright_cyan]🎬 Watch videos? (y/n):[/bold bright_cyan] "
        ).strip().lower()

        if play_choice == 'y':
            play_videos_embedded(video_path, results['output_video'])

        # Final message
        console.print()
        console.print(Panel(
            "[bold bright_green]🎉 Demo Complete![/bold bright_green]\n\n"
            f"[grey93]Output saved to:[/grey93]\n"
            f"  {results['output_video']}\n\n"
            "[grey70]All processed files available in data/pipeline/[/grey70]",
            title="✨ Success",
            border_style="bright_green",
            box=box.DOUBLE
        ))

        # Show pipeline architecture
        show_pipeline_architecture()

    except KeyboardInterrupt:
        console.print("\n\n[bright_yellow]⚠️  Demo interrupted. Goodbye! 👋[/bright_yellow]")
    except Exception as e:
        console.print(f"\n[bold bright_red]❌ Error:[/bold bright_red] {e}")
        import traceback
        console.print("[grey70]" + traceback.format_exc() + "[/grey70]")


if __name__ == "__main__":
    main()
