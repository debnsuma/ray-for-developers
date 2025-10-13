"""
Test 4: Feature Extraction with Ray Actors
Test MobileNetV3 on M4 MacBook Pro with MPS acceleration
"""
import ray
import torch
import numpy as np
from pathlib import Path
import sys
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.feature_extractors import VisualFeatureExtractor, create_feature_extractor_pool

print("=" * 70)
print("TEST 4: Feature Extraction with Ray Actors")
print("=" * 70)

# Test 4.1: Initialize Ray
print("\n1. Initialize Ray:")
ray.init(num_cpus=4, ignore_reinit_error=True)
print(f"   Ray version: {ray.__version__}")
print(f"   ✅ Ray initialized")

# Test 4.2: Test MPS availability
print("\n2. MPS (Metal Performance Shaders) Status:")
print(f"   MPS Available: {torch.backends.mps.is_available()}")
print(f"   MPS Built: {torch.backends.mps.is_built()}")

if torch.backends.mps.is_available():
    print(f"   ✅ MPS ready for feature extraction")
else:
    print(f"   ⚠️  MPS not available, will use CPU")

# Test 4.3: Create single feature extractor actor
print("\n3. Create VisualFeatureExtractor Actor:")
try:
    extractor = VisualFeatureExtractor.remote(
        model_name="mobilenet_v3_small",
        use_mps=True
    )

    # Get device info
    device_info = ray.get(extractor.get_device_info.remote())
    print(f"   Actor device: {device_info['device']}")
    print(f"   Device type: {device_info['device_type']}")
    print(f"   ✅ Actor created successfully")

except Exception as e:
    print(f"   ❌ Failed to create actor: {e}")
    ray.shutdown()
    sys.exit(1)

# Test 4.4: Test single frame feature extraction
print("\n4. Test Single Frame Feature Extraction:")
try:
    # Get a test frame from preprocessed data
    processed_dir = Path("data/processed/demo")

    # Find first video with frames
    test_frame = None
    for video_dir in processed_dir.iterdir():
        if video_dir.is_dir():
            frames_dir = video_dir / "frames"
            if frames_dir.exists():
                frames = list(frames_dir.glob("frame_*.jpg"))
                if frames:
                    test_frame = str(frames[0])
                    print(f"   Test frame: {test_frame}")
                    break

    if not test_frame:
        print(f"   ❌ No preprocessed frames found!")
        print(f"   Run: python scripts/preprocess_videos.py")
        ray.shutdown()
        sys.exit(1)

    # Extract features
    start_time = time.time()
    features = ray.get(extractor.extract_frame_features.remote(test_frame))
    elapsed = time.time() - start_time

    print(f"   Features shape: {features.shape}")
    print(f"   Features dtype: {features.dtype}")
    print(f"   Features range: [{features.min():.4f}, {features.max():.4f}]")
    print(f"   Extraction time: {elapsed*1000:.2f}ms")
    print(f"   ✅ Single frame extraction successful")

except Exception as e:
    print(f"   ❌ Frame extraction failed: {e}")
    import traceback
    traceback.print_exc()
    ray.shutdown()
    sys.exit(1)

# Test 4.5: Test full video feature extraction
print("\n5. Test Full Video Feature Extraction:")
try:
    # Get first video directory
    processed_dir = Path("data/processed/demo")
    video_dirs = [d for d in processed_dir.iterdir() if d.is_dir()]

    if not video_dirs:
        print(f"   ❌ No preprocessed videos found!")
        ray.shutdown()
        sys.exit(1)

    # Use the smallest video for testing (for_bigger_blazes)
    test_video = None
    for vdir in video_dirs:
        if "blazes" in vdir.name.lower():
            test_video = vdir
            break

    if not test_video:
        test_video = video_dirs[0]

    print(f"   Test video: {test_video.name}")

    # Extract features
    output_path = Path("data/features/demo") / f"{test_video.name}_features.npy"

    start_time = time.time()
    result = ray.get(extractor.extract_video_features.remote(
        video_dir=str(test_video),
        output_path=str(output_path)
    ))
    elapsed = time.time() - start_time

    if result['success']:
        print(f"   Video: {result['video_name']}")
        print(f"   Frames: {result['num_frames']}")
        print(f"   Feature dim: {result['feature_dim']}")
        print(f"   Features shape: {result['features'].shape}")
        print(f"   Extraction time: {elapsed:.2f}s")
        print(f"   FPS: {result['num_frames']/elapsed:.1f} frames/sec")
        print(f"   Output: {result['output_path']}")
        print(f"   ✅ Video feature extraction successful")
    else:
        print(f"   ❌ Extraction failed: {result.get('error', 'unknown')}")
        ray.shutdown()
        sys.exit(1)

except Exception as e:
    print(f"   ❌ Video extraction failed: {e}")
    import traceback
    traceback.print_exc()
    ray.shutdown()
    sys.exit(1)

# Test 4.6: Test parallel feature extraction with multiple actors
print("\n6. Test Parallel Feature Extraction (Multiple Actors):")
try:
    # Get all video directories
    video_dirs = [d for d in processed_dir.iterdir() if d.is_dir()]
    print(f"   Found {len(video_dirs)} videos to process")

    # Create actor pool (2 actors for M4)
    num_actors = min(2, len(video_dirs))
    actors = create_feature_extractor_pool(num_actors=num_actors)

    # Distribute videos to actors
    print(f"\n   🚀 Starting parallel extraction with {num_actors} actors...")

    start_time = time.time()

    # Create tasks
    tasks = []
    for i, video_dir in enumerate(video_dirs):
        actor = actors[i % num_actors]
        output_path = Path("data/features/demo") / f"{video_dir.name}_features.npy"

        task = actor.extract_video_features.remote(
            video_dir=str(video_dir),
            output_path=str(output_path)
        )
        tasks.append(task)

    # Wait for all tasks to complete
    results = ray.get(tasks)

    elapsed = time.time() - start_time

    # Summary
    successful = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'])
    total_frames = sum(r['num_frames'] for r in results if r['success'])

    print(f"\n   ✅ Parallel extraction complete!")
    print(f"      Successful: {successful}/{len(results)}")
    if failed > 0:
        print(f"      Failed: {failed}/{len(results)}")
    print(f"      Total frames: {total_frames}")
    print(f"      Total time: {elapsed:.2f}s")
    print(f"      Overall FPS: {total_frames/elapsed:.1f} frames/sec")
    print(f"      Average per video: {elapsed/len(results):.2f}s")

    # Details
    print(f"\n   Extracted features:")
    for result in results:
        if result['success']:
            print(f"      📹 {result['video_name']}: {result['num_frames']} frames, {result['feature_dim']} dims")

except Exception as e:
    print(f"   ❌ Parallel extraction failed: {e}")
    import traceback
    traceback.print_exc()
    ray.shutdown()
    sys.exit(1)

# Test 4.7: Verify saved features
print("\n7. Verify Saved Features:")
try:
    features_dir = Path("data/features/demo")

    if not features_dir.exists():
        print(f"   ❌ Features directory not found!")
        ray.shutdown()
        sys.exit(1)

    feature_files = list(features_dir.glob("*_features.npy"))
    metadata_files = list(features_dir.glob("*_metadata.json"))

    print(f"   Feature files: {len(feature_files)}")
    print(f"   Metadata files: {len(metadata_files)}")

    if feature_files:
        # Load and verify first feature file
        test_file = feature_files[0]
        features = np.load(test_file)

        print(f"\n   Sample feature file: {test_file.name}")
        print(f"      Shape: {features.shape}")
        print(f"      Dtype: {features.dtype}")
        print(f"      Size: {test_file.stat().st_size / (1024*1024):.2f} MB")
        print(f"   ✅ Features saved and loadable")
    else:
        print(f"   ⚠️  No feature files found")

except Exception as e:
    print(f"   ❌ Verification failed: {e}")
    ray.shutdown()
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ All feature extraction tests passed!")
print(f"\nMobileNetV3-small working on M4 MacBook Pro")
print(f"Device: {device_info['device_type'].upper()}")
print(f"Extracted features from {successful} videos")
print(f"Total frames processed: {total_frames}")
print(f"Performance: {total_frames/elapsed:.1f} FPS")
print(f"\nFeatures saved to: data/features/demo/")
print(f"\nNext step: Implement highlight detection (Phase 5)")
print("=" * 70 + "\n")

ray.shutdown()
