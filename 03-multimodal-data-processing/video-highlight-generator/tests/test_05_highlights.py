"""
Test 5: Highlight Detection
Test detection of interesting moments from visual features
"""
import numpy as np
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.features.highlight_detector import HighlightDetector

print("=" * 70)
print("TEST 5: Highlight Detection")
print("=" * 70)

# Test 5.1: Initialize HighlightDetector
print("\n1. Initialize HighlightDetector:")
try:
    detector = HighlightDetector(
        variance_weight=0.4,
        novelty_weight=0.3,
        motion_weight=0.3
    )
    print("   ✅ HighlightDetector initialized")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}")
    sys.exit(1)

# Test 5.2: Test on single video
print("\n2. Test Highlight Detection on Single Video:")
try:
    features_dir = Path("data/features/demo")

    # Test on smallest video first
    test_features = None
    for f in features_dir.glob("*_features.npy"):
        if "blazes" in f.stem.lower():
            test_features = f
            break

    if not test_features:
        test_features = list(features_dir.glob("*_features.npy"))[0]

    print(f"   Test features: {test_features.name}")

    # Detect highlights
    result = detector.detect_highlights(
        features_path=str(test_features),
        num_highlights=3,
        min_distance=5,
        threshold=0.3,
        output_path=f"data/highlights/demo/{test_features.stem.replace('_features', '')}_highlights.json"
    )

    print(f"\n   ✅ Highlight detection successful")
    print(f"      Video: {result['video_name']}")
    print(f"      Duration: {result['duration']:.1f}s")
    print(f"      Highlights found: {result['num_highlights']}")

except Exception as e:
    print(f"   ❌ Highlight detection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5.3: Test on all videos
print("\n3. Test Highlight Detection on All Videos:")
try:
    features_dir = Path("data/features/demo")
    feature_files = list(features_dir.glob("*_features.npy"))

    print(f"   Found {len(feature_files)} feature files")

    all_results = []

    for feature_file in sorted(feature_files):
        output_path = Path("data/highlights/demo") / f"{feature_file.stem.replace('_features', '')}_highlights.json"

        result = detector.detect_highlights(
            features_path=str(feature_file),
            num_highlights=5,
            min_distance=10,
            threshold=0.4,
            output_path=str(output_path)
        )

        all_results.append(result)

    print(f"\n   ✅ Processed {len(all_results)} videos")

    # Summary
    total_highlights = sum(r['num_highlights'] for r in all_results)
    print(f"      Total highlights detected: {total_highlights}")

except Exception as e:
    print(f"   ❌ Batch processing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5.4: Visualize importance scores
print("\n4. Visualize Importance Scores:")
try:
    # Create visualizations for each video
    for result in all_results:
        video_name = result['video_name']
        importance_scores = np.array(result['importance_scores'])
        highlights = result['highlights']

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 4))

        # Plot importance scores
        frames = np.arange(len(importance_scores))
        ax.plot(frames, importance_scores, 'b-', linewidth=1, label='Importance Score')

        # Mark highlights
        for h in highlights:
            frame_idx = h['frame_index']
            score = h['importance_score']
            ax.axvline(frame_idx, color='r', linestyle='--', alpha=0.5)
            ax.plot(frame_idx, score, 'r*', markersize=15)

        ax.set_xlabel('Frame Index')
        ax.set_ylabel('Importance Score')
        ax.set_title(f'Highlight Detection - {video_name}')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Save plot
        plot_path = Path("data/highlights/demo") / f"{video_name}_importance_plot.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"   📊 Saved plot: {plot_path.name}")

    print(f"   ✅ Created {len(all_results)} visualization plots")

except Exception as e:
    print(f"   ❌ Visualization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5.5: Verify saved highlights
print("\n5. Verify Saved Highlight Data:")
try:
    highlights_dir = Path("data/highlights/demo")

    json_files = list(highlights_dir.glob("*_highlights.json"))
    plot_files = list(highlights_dir.glob("*_importance_plot.png"))

    print(f"   Highlight JSON files: {len(json_files)}")
    print(f"   Visualization plots: {len(plot_files)}")

    if json_files:
        # Load and verify first file
        import json
        test_file = json_files[0]

        with open(test_file, 'r') as f:
            data = json.load(f)

        print(f"\n   Sample highlight file: {test_file.name}")
        print(f"      Video: {data['video_name']}")
        print(f"      Frames: {data['num_frames']}")
        print(f"      Highlights: {data['num_highlights']}")
        print(f"      Keys: {list(data.keys())}")
        print(f"   ✅ Highlight data saved and loadable")
    else:
        print(f"   ⚠️  No highlight files found")

except Exception as e:
    print(f"   ❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5.6: Test different parameters
print("\n6. Test Different Detection Parameters:")
try:
    # Test with more aggressive detection
    test_features = feature_files[0]

    print(f"   Testing aggressive detection (lower threshold)...")
    result_aggressive = detector.detect_highlights(
        features_path=str(test_features),
        num_highlights=10,
        min_distance=5,
        threshold=0.2
    )

    print(f"      Aggressive: {result_aggressive['num_highlights']} highlights")

    # Test with conservative detection
    print(f"   Testing conservative detection (higher threshold)...")
    result_conservative = detector.detect_highlights(
        features_path=str(test_features),
        num_highlights=10,
        min_distance=15,
        threshold=0.6
    )

    print(f"      Conservative: {result_conservative['num_highlights']} highlights")

    print(f"   ✅ Parameter testing successful")

except Exception as e:
    print(f"   ❌ Parameter testing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ All highlight detection tests passed!")
print(f"\nProcessed {len(all_results)} videos:")

for result in all_results:
    print(f"   📹 {result['video_name']}")
    print(f"      Duration: {result['duration']:.1f}s")
    print(f"      Highlights: {result['num_highlights']}")
    if result['highlights']:
        top_highlight = result['highlights'][0]
        mins = int(top_highlight['timestamp'] // 60)
        secs = int(top_highlight['timestamp'] % 60)
        print(f"      Top highlight: {mins:02d}:{secs:02d} (score: {top_highlight['importance_score']:.3f})")

print(f"\nHighlights saved to: data/highlights/demo/")
print(f"Visualizations saved to: data/highlights/demo/")
print(f"\nNext step: Generate highlight video clips (Phase 6)")
print("=" * 70 + "\n")
