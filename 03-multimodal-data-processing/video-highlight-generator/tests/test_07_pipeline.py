"""
Test 7: End-to-End Pipeline
Test the complete pipeline with progress monitoring
"""
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import VideoHighlightPipeline

print("=" * 70)
print("TEST 7: End-to-End Pipeline")
print("=" * 70)

# Test 7.1: Initialize Pipeline
print("\n1. Initialize Pipeline:")
try:
    pipeline = VideoHighlightPipeline(
        num_actors=2,
        target_fps=1.0,
        resolution=(224, 224),
        num_highlights=3,
        clip_duration=3.0
    )
    print("   ✅ Pipeline initialized")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}")
    sys.exit(1)

# Test 7.2: Test on demo video
print("\n2. Run Complete Pipeline on Demo Video:")
try:
    # Use smallest video for testing
    video_path = Path("data/raw/demo/for_bigger_blazes.mp4")

    if not video_path.exists():
        print(f"   ❌ Video not found: {video_path}")
        sys.exit(1)

    print(f"   Test video: {video_path.name}")

    # Run pipeline
    results = pipeline.run(
        video_path=str(video_path)
    )

    if results['success']:
        print(f"\n   ✅ Pipeline completed successfully!")
        print(f"      Total time: {results['total_time']:.1f}s")
        print(f"      Output video: {results['output_video']}")

        # Print phase times
        print(f"\n   Phase Breakdown:")
        if 'preprocessing' in results:
            print(f"      Phase 1 - Preprocessing: {results['preprocessing'].get('elapsed', 0):.1f}s")
        if 'features' in results:
            print(f"      Phase 2 - Features: {results['features'].get('elapsed', 0):.1f}s")
        if 'highlights' in results:
            print(f"      Phase 3 - Highlights: {results['highlights'].get('elapsed', 0):.1f}s")
        if 'generation' in results:
            print(f"      Phase 4 - Generation: {results['generation'].get('elapsed', 0):.1f}s")

    else:
        print(f"   ❌ Pipeline failed: {results.get('error')}")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ Pipeline test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7.3: Verify output
print("\n3. Verify Pipeline Output:")
try:
    output_video = Path(results['output_video'])

    if not output_video.exists():
        print(f"   ❌ Output video not found: {output_video}")
        sys.exit(1)

    size_mb = output_video.stat().st_size / (1024 * 1024)
    print(f"   Output video: {output_video.name}")
    print(f"   Size: {size_mb:.1f} MB")

    # Check for other output files
    output_dir = output_video.parent

    features_file = output_dir / f"{output_video.stem.replace('_highlight_reel', '')}_features.npy"
    highlights_file = output_dir / f"{output_video.stem.replace('_highlight_reel', '')}_highlights.json"
    results_file = output_dir / "pipeline_results.json"

    files_found = 0
    if features_file.exists():
        print(f"   ✅ Features file: {features_file.name}")
        files_found += 1
    if highlights_file.exists():
        print(f"   ✅ Highlights file: {highlights_file.name}")
        files_found += 1
    if results_file.exists():
        print(f"   ✅ Results file: {results_file.name}")
        files_found += 1

    print(f"   ✅ Verified {files_found + 1} output files")

except Exception as e:
    print(f"   ❌ Verification failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ All pipeline tests passed!")
print(f"\nProcessed: {results['video_name']}")
print(f"Total time: {results['total_time']:.1f}s")
print(f"Output: {results['output_video']}")
print(f"\nPipeline ready for web interface!")
print("Run: python app.py")
print("=" * 70 + "\n")
