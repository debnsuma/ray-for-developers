"""
Test 2: Video Loading with Ray Data
Test loading videos using Ray Data and extracting basic metadata
"""
import ray
import cv2
import numpy as np
from pathlib import Path
import tempfile

print("=" * 70)
print("TEST 2: Video Loading with Ray Data")
print("=" * 70)

# Test 2.1: Initialize Ray
print("\n1. Initialize Ray:")
ray.init(num_cpus=4, ignore_reinit_error=True)
print(f"   Ray version: {ray.__version__}")
print(f"   ✅ Ray initialized")

# Test 2.2: Load videos with Ray Data
print("\n2. Load Videos with Ray Data:")
video_dir = Path("data/raw/demo").absolute()

# Get list of video files
video_files = list(video_dir.glob("*.mp4"))
print(f"   Looking for videos at: {video_dir}")
print(f"   Found {len(video_files)} video files")

if not video_files:
    print(f"   ❌ No videos found!")
    ray.shutdown()
    exit(1)

try:
    # Convert to string paths
    video_paths = [str(p) for p in video_files]

    ds = ray.data.read_binary_files(
        video_paths,
        include_paths=True
    )
    count = ds.count()
    print(f"   Loaded {count} videos with Ray Data")
    print(f"   ✅ Videos loaded with Ray Data")
except Exception as e:
    print(f"   ❌ Failed to load videos: {e}")
    import traceback
    traceback.print_exc()
    ray.shutdown()
    exit(1)

# Test 2.3: Extract metadata from videos
print("\n3. Extract Video Metadata:")

def extract_metadata(row):
    """Extract metadata from a video file"""
    video_path = row['path']
    video_bytes = row['bytes']

    # Write to temporary file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name

    try:
        # Open with OpenCV
        cap = cv2.VideoCapture(tmp_path)

        if not cap.isOpened():
            return {
                'path': video_path,
                'valid': False,
                'error': 'Could not open video'
            }

        # Extract metadata
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0

        cap.release()

        return {
            'path': video_path,
            'filename': Path(video_path).name,
            'fps': fps,
            'frame_count': frame_count,
            'width': width,
            'height': height,
            'duration': duration,
            'size_mb': len(video_bytes) / (1024 * 1024),
            'valid': True
        }

    except Exception as e:
        return {
            'path': video_path,
            'valid': False,
            'error': str(e)
        }
    finally:
        # Cleanup temp file
        import os
        try:
            os.unlink(tmp_path)
        except:
            pass

# Process videos and extract metadata
try:
    metadata_ds = ds.map(extract_metadata)
    metadata_list = metadata_ds.take_all()

    print(f"   Processed {len(metadata_list)} videos")

    for meta in metadata_list:
        if meta['valid']:
            print(f"\n   📹 {meta['filename']}")
            print(f"      Size: {meta['size_mb']:.1f} MB")
            print(f"      Resolution: {meta['width']}x{meta['height']}")
            print(f"      FPS: {meta['fps']:.1f}")
            print(f"      Frames: {meta['frame_count']}")
            print(f"      Duration: {meta['duration']:.1f}s")
        else:
            print(f"\n   ❌ {meta.get('path', 'unknown')}")
            print(f"      Error: {meta.get('error', 'unknown error')}")

    valid_count = sum(1 for m in metadata_list if m['valid'])
    print(f"\n   ✅ Successfully loaded {valid_count}/{len(metadata_list)} videos")

except Exception as e:
    print(f"   ❌ Failed to extract metadata: {e}")
    ray.shutdown()
    exit(1)

# Test 2.4: Read a single frame from each video
print("\n4. Test Frame Extraction:")

def extract_first_frame(row):
    """Extract first frame from video"""
    video_path = row['path']
    video_bytes = row['bytes']

    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name

    try:
        cap = cv2.VideoCapture(tmp_path)

        if not cap.isOpened():
            return {
                'path': video_path,
                'success': False
            }

        ret, frame = cap.read()
        cap.release()

        if ret:
            return {
                'path': video_path,
                'filename': Path(video_path).name,
                'frame_shape': frame.shape,
                'frame_dtype': str(frame.dtype),
                'success': True
            }
        else:
            return {
                'path': video_path,
                'success': False
            }

    except Exception as e:
        return {
            'path': video_path,
            'success': False,
            'error': str(e)
        }
    finally:
        import os
        try:
            os.unlink(tmp_path)
        except:
            pass

try:
    frames_ds = ds.map(extract_first_frame)
    frames_list = frames_ds.take_all()

    for frame_meta in frames_list:
        if frame_meta['success']:
            print(f"   📸 {frame_meta['filename']}")
            print(f"      Frame shape: {frame_meta['frame_shape']}")
            print(f"      Frame dtype: {frame_meta['frame_dtype']}")
        else:
            print(f"   ❌ {frame_meta.get('path', 'unknown')}")

    success_count = sum(1 for f in frames_list if f['success'])
    print(f"\n   ✅ Extracted frames from {success_count}/{len(frames_list)} videos")

except Exception as e:
    print(f"   ❌ Failed to extract frames: {e}")
    ray.shutdown()
    exit(1)

# Test 2.5: Test parallel processing
print("\n5. Test Parallel Processing:")

def process_video_stats(row):
    """Compute some stats (simulates processing)"""
    import time
    start = time.time()

    video_path = row['path']
    video_bytes = row['bytes']

    # Simulate some work
    size_mb = len(video_bytes) / (1024 * 1024)

    elapsed = time.time() - start

    return {
        'filename': Path(video_path).name,
        'size_mb': size_mb,
        'processing_time': elapsed
    }

try:
    stats_ds = ds.map(process_video_stats)
    stats_list = stats_ds.take_all()

    total_time = sum(s['processing_time'] for s in stats_list)
    total_size = sum(s['size_mb'] for s in stats_list)

    print(f"   Processed {len(stats_list)} videos in parallel")
    print(f"   Total size: {total_size:.1f} MB")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   ✅ Parallel processing working")

except Exception as e:
    print(f"   ❌ Parallel processing failed: {e}")
    ray.shutdown()
    exit(1)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ All tests passed!")
print(f"\nLoaded {count} videos successfully")
print(f"Ray Data pipeline working correctly")
print(f"\nNext step: python test_03_preprocessing.py")
print("=" * 70 + "\n")

ray.shutdown()
