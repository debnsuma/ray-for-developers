"""
Preprocess videos with Ray Data
- Extract frames at target FPS (default: 1 FPS for M4)
- Extract audio track
- Save metadata
Optimized for M4 MacBook Pro
"""
import ray
import cv2
import numpy as np
from pathlib import Path
import subprocess
import json
import tempfile
import os

def preprocess_video(row, target_fps=1, resolution=(224, 224)):
    """
    Preprocess a single video: extract frames and audio

    Args:
        row: Ray Data row with video bytes and path
        target_fps: Target frames per second to extract (1 for M4)
        resolution: Target resolution for frames (224x224 for faster processing)

    Returns:
        Dictionary with preprocessing results
    """
    video_path = row['path']
    video_bytes = row['bytes']
    video_name = Path(video_path).stem

    print(f"\n📹 Processing: {video_name}")

    # Create output directory
    output_dir = Path("data/processed/demo") / video_name
    output_dir.mkdir(parents=True, exist_ok=True)

    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    # Write video to temp file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp.write(video_bytes)
        tmp_video_path = tmp.name

    try:
        # ============= EXTRACT FRAMES =============
        cap = cv2.VideoCapture(tmp_video_path)

        if not cap.isOpened():
            return {'success': False, 'error': 'Could not open video', 'video_name': video_name}

        # Get video properties
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / original_fps if original_fps > 0 else 0

        # Calculate frame interval
        frame_interval = int(original_fps / target_fps) if original_fps > 0 else 1

        print(f"   Original: {width}x{height} @ {original_fps:.1f} FPS, {total_frames} frames")
        print(f"   Extracting every {frame_interval}th frame → {target_fps} FPS")

        # Extract frames
        frame_idx = 0
        saved_frames = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Sample frame at target FPS
            if frame_idx % frame_interval == 0:
                # Resize frame
                frame_resized = cv2.resize(frame, resolution)

                # Save frame
                frame_path = frames_dir / f"frame_{saved_frames:06d}.jpg"
                cv2.imwrite(str(frame_path), frame_resized)
                saved_frames += 1

            frame_idx += 1

        cap.release()
        print(f"   ✅ Extracted {saved_frames} frames")

        # ============= EXTRACT AUDIO =============
        audio_path = output_dir / "audio.wav"

        try:
            result = subprocess.run([
                'ffmpeg',
                '-i', tmp_video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono
                str(audio_path),
                '-y',  # Overwrite
                '-loglevel', 'error'  # Only show errors
            ], capture_output=True, check=True)

            audio_size_mb = audio_path.stat().st_size / (1024 * 1024)
            print(f"   ✅ Extracted audio ({audio_size_mb:.1f} MB)")
            has_audio = True

        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  No audio track or extraction failed")
            has_audio = False

        # ============= SAVE METADATA =============
        metadata = {
            'video_name': video_name,
            'original_path': video_path,
            'original_fps': original_fps,
            'original_resolution': [width, height],
            'total_frames': total_frames,
            'duration': duration,
            'target_fps': target_fps,
            'target_resolution': list(resolution),
            'extracted_frames': saved_frames,
            'frames_dir': str(frames_dir),
            'audio_path': str(audio_path) if has_audio else None,
            'has_audio': has_audio
        }

        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"   ✅ Saved metadata")

        return {
            'success': True,
            'video_name': video_name,
            'extracted_frames': saved_frames,
            'has_audio': has_audio,
            'output_dir': str(output_dir),
            'metadata': metadata
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'video_name': video_name
        }

    finally:
        # Cleanup temp file
        try:
            os.unlink(tmp_video_path)
        except:
            pass


def main():
    """Preprocess all videos in data/raw/demo"""

    print("=" * 70)
    print("VIDEO PREPROCESSING WITH RAY DATA")
    print("=" * 70)
    print("\nOptimized for M4 MacBook Pro")
    print("- Target FPS: 1 (for faster processing)")
    print("- Resolution: 224x224 (lightweight)")
    print("- Parallel processing with Ray Data\n")

    # Initialize Ray
    ray.init(num_cpus=4, ignore_reinit_error=True)
    print(f"✅ Ray initialized with 4 CPUs\n")

    # Load videos
    video_dir = Path("data/raw/demo").absolute()
    video_files = list(video_dir.glob("*.mp4"))

    if not video_files:
        print("❌ No videos found!")
        ray.shutdown()
        return

    print(f"Found {len(video_files)} videos to process\n")

    # Create Ray Dataset
    video_paths = [str(p) for p in video_files]
    ds = ray.data.read_binary_files(video_paths, include_paths=True)

    # Preprocess videos in parallel
    print("🚀 Starting parallel preprocessing...\n")

    import time
    start_time = time.time()

    results_ds = ds.map(
        lambda row: preprocess_video(row, target_fps=1, resolution=(224, 224))
    )

    # Collect results
    results = results_ds.take_all()

    elapsed = time.time() - start_time

    # Summary
    print("\n" + "=" * 70)
    print("PREPROCESSING SUMMARY")
    print("=" * 70)

    successful = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'])

    print(f"\n✅ Successful: {successful}/{len(results)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(results)}")

    print(f"\n⏱️  Total time: {elapsed:.1f}s")
    print(f"   Average: {elapsed/len(results):.1f}s per video")

    # Details
    print(f"\nProcessed videos:")
    total_frames = 0
    for result in results:
        if result['success']:
            frames = result['extracted_frames']
            audio = "✅" if result['has_audio'] else "❌"
            print(f"   📹 {result['video_name']}")
            print(f"      Frames: {frames}, Audio: {audio}")
            total_frames += frames

    print(f"\nTotal extracted frames: {total_frames}")
    print(f"Output directory: data/processed/demo/")

    print("\n" + "=" * 70)
    print("✅ Preprocessing complete!")
    print("\nNext step: python test_03_preprocessing.py")
    print("=" * 70 + "\n")

    ray.shutdown()


if __name__ == "__main__":
    main()
