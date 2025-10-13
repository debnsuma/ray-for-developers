"""
Download sample videos for testing on M4 MacBook Pro
Uses small, freely available videos for quick testing
"""
import os
import subprocess
from pathlib import Path
import sys

def download_video(url: str, output_path: str, description: str) -> bool:
    """Download a video using curl"""
    print(f"\n📥 Downloading: {description}")
    print(f"   URL: {url}")
    print(f"   Output: {output_path}")

    try:
        result = subprocess.run(
            ['curl', '-L', '-o', output_path, url, '--progress-bar'],
            capture_output=False,
            check=True
        )

        # Check file size
        size_mb = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"   ✅ Downloaded! ({size_mb:.1f} MB)")
        return True

    except subprocess.CalledProcessError as e:
        print(f"   ❌ Download failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verify_video(video_path: str) -> dict:
    """Verify video and get metadata using FFprobe"""
    try:
        result = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,duration',
            '-show_entries', 'format=duration',
            '-of', 'json',
            video_path
        ], capture_output=True, text=True, check=True)

        import json
        data = json.loads(result.stdout)

        if 'streams' in data and len(data['streams']) > 0:
            stream = data['streams'][0]
            duration = float(data['format']['duration']) if 'format' in data else 0

            # Parse frame rate
            fps_str = stream.get('r_frame_rate', '0/1')
            num, den = map(int, fps_str.split('/'))
            fps = num / den if den > 0 else 0

            return {
                'width': stream.get('width', 0),
                'height': stream.get('height', 0),
                'fps': fps,
                'duration': duration,
                'valid': True
            }
    except Exception as e:
        print(f"   ⚠️  Could not verify video: {e}")
        return {'valid': False}

    return {'valid': False}

def main():
    """Download sample videos for testing"""

    print("=" * 70)
    print("SAMPLE VIDEO DOWNLOADER")
    print("=" * 70)
    print("\nDownloading small test videos (~100MB total)")
    print("These are royalty-free sample videos for development\n")

    output_dir = Path("data/raw/demo")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Sample videos from sample-videos.com and other free sources
    # These are small files perfect for testing
    videos = [
        {
            "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "output": "data/raw/demo/big_buck_bunny.mp4",
            "description": "Big Buck Bunny - Animated short (10 min)"
        },
        {
            "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "output": "data/raw/demo/elephants_dream.mp4",
            "description": "Elephants Dream - Animated short (11 min)"
        },
        {
            "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "output": "data/raw/demo/for_bigger_blazes.mp4",
            "description": "For Bigger Blazes - Short clip (15 sec)"
        }
    ]

    successful = 0
    failed = 0

    for video in videos:
        if Path(video['output']).exists():
            size_mb = Path(video['output']).stat().st_size / (1024 * 1024)
            print(f"\n✓ Already exists: {video['output']} ({size_mb:.1f} MB)")
            print("  Skipping download...")
            successful += 1
            continue

        if download_video(video['url'], video['output'], video['description']):
            successful += 1
        else:
            failed += 1

    # Verify all videos
    print("\n" + "=" * 70)
    print("VERIFYING VIDEOS")
    print("=" * 70)

    video_files = list(output_dir.glob("*.mp4"))

    if not video_files:
        print("\n❌ No videos found!")
        sys.exit(1)

    print(f"\nFound {len(video_files)} video(s):\n")

    total_duration = 0
    total_size = 0

    for video_path in sorted(video_files):
        print(f"📹 {video_path.name}")

        # Get file size
        size_mb = video_path.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"   Size: {size_mb:.1f} MB")

        # Verify video
        metadata = verify_video(str(video_path))

        if metadata['valid']:
            print(f"   Resolution: {metadata['width']}x{metadata['height']}")
            print(f"   FPS: {metadata['fps']:.1f}")
            print(f"   Duration: {metadata['duration']:.1f}s")
            total_duration += metadata['duration']
            print(f"   ✅ Valid video")
        else:
            print(f"   ⚠️  Could not verify (but file exists)")

        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ Downloaded: {successful}")
    if failed > 0:
        print(f"❌ Failed: {failed}")
    print(f"\nTotal videos: {len(video_files)}")
    print(f"Total size: {total_size:.1f} MB")
    print(f"Total duration: {total_duration/60:.1f} minutes")
    print(f"\nVideos saved to: {output_dir.absolute()}")
    print("\n✅ Ready for testing!")
    print("\nNext step: python test_02_video_loading.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
