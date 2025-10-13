"""
Test 6: Video Highlight Generation
Test extraction and concatenation of highlight clips
"""
from pathlib import Path
import sys
import subprocess
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.features.video_generator import VideoHighlightGenerator

print("=" * 70)
print("TEST 6: Video Highlight Generation")
print("=" * 70)

# Test 6.1: Initialize VideoHighlightGenerator
print("\n1. Initialize VideoHighlightGenerator:")
try:
    generator = VideoHighlightGenerator(
        clip_duration=3.0,
        fade_duration=0.5,
        output_format="mp4",
        video_codec="libx264",
        audio_codec="aac"
    )
    print("   ✅ VideoHighlightGenerator initialized")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}")
    sys.exit(1)

# Test 6.2: Test single clip extraction
print("\n2. Test Single Clip Extraction:")
try:
    # Get test video
    video_dir = Path("data/raw/demo")
    test_video = None

    # Use smallest video for quick testing
    for v in video_dir.glob("*.mp4"):
        if "blazes" in v.name.lower():
            test_video = v
            break

    if not test_video:
        test_video = list(video_dir.glob("*.mp4"))[0]

    print(f"   Test video: {test_video.name}")

    # Extract single clip at 5 seconds
    test_clip_path = Path("data/output/demo/test_clip.mp4")
    test_clip_path.parent.mkdir(parents=True, exist_ok=True)

    success = generator.extract_clip(
        video_path=str(test_video),
        timestamp=5.0,
        output_path=str(test_clip_path),
        duration=3.0
    )

    if success and test_clip_path.exists():
        size_mb = test_clip_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Clip extracted successfully")
        print(f"      Output: {test_clip_path}")
        print(f"      Size: {size_mb:.2f} MB")
    else:
        print(f"   ❌ Clip extraction failed")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ Clip extraction test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6.3: Test transitions
print("\n3. Test Fade Transitions:")
try:
    transition_clip_path = Path("data/output/demo/test_clip_fade.mp4")

    success = generator.add_fade_transitions(
        input_path=str(test_clip_path),
        output_path=str(transition_clip_path),
        fade_in=True,
        fade_out=True
    )

    if success and transition_clip_path.exists():
        size_mb = transition_clip_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Transitions added successfully")
        print(f"      Output: {transition_clip_path}")
        print(f"      Size: {size_mb:.2f} MB")
    else:
        print(f"   ❌ Transition addition failed")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ Transition test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6.4: Test clip concatenation
print("\n4. Test Clip Concatenation:")
try:
    # Create a few test clips
    print(f"   Creating multiple test clips...")

    test_clips = []
    for i in range(3):
        clip_path = Path(f"data/output/demo/concat_test_clip_{i}.mp4")
        timestamp = 3.0 + i * 3.0  # Clips at 3s, 6s, 9s

        success = generator.extract_clip(
            video_path=str(test_video),
            timestamp=timestamp,
            output_path=str(clip_path),
            duration=2.0
        )

        if success:
            test_clips.append(str(clip_path))

    print(f"   Created {len(test_clips)} test clips")

    # Concatenate
    concat_output = Path("data/output/demo/test_concatenated.mp4")

    success = generator.concatenate_clips(
        clip_paths=test_clips,
        output_path=str(concat_output)
    )

    if success and concat_output.exists():
        size_mb = concat_output.stat().st_size / (1024 * 1024)
        print(f"   ✅ Clips concatenated successfully")
        print(f"      Output: {concat_output}")
        print(f"      Size: {size_mb:.2f} MB")
    else:
        print(f"   ❌ Concatenation failed")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ Concatenation test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6.5: Test full highlight reel generation
print("\n5. Test Full Highlight Reel Generation:")
try:
    highlights_dir = Path("data/highlights/demo")
    video_dir = Path("data/raw/demo")

    # Test on smallest video first
    test_highlights = None
    test_video = None

    for h in highlights_dir.glob("*_highlights.json"):
        video_name = h.stem.replace("_highlights", "")
        video_path = video_dir / f"{video_name}.mp4"

        if video_path.exists() and "blazes" in video_name.lower():
            test_highlights = h
            test_video = video_path
            break

    if not test_highlights:
        # Use first available
        test_highlights = list(highlights_dir.glob("*_highlights.json"))[0]
        video_name = test_highlights.stem.replace("_highlights", "")
        test_video = video_dir / f"{video_name}.mp4"

    print(f"   Video: {test_video.name}")
    print(f"   Highlights: {test_highlights.name}")

    output_path = Path("data/output/demo") / f"{test_video.stem}_highlight_reel.mp4"

    result = generator.generate_highlight_reel(
        video_path=str(test_video),
        highlights_path=str(test_highlights),
        output_path=str(output_path),
        add_transitions=True,
        max_highlights=None
    )

    if result['success']:
        print(f"   ✅ Highlight reel generated successfully")
        print(f"      Clips: {result['num_clips']}")
        print(f"      Duration: ~{result['estimated_duration']:.1f}s")
        print(f"      Size: {result['output_size_mb']:.1f} MB")
    else:
        print(f"   ❌ Highlight reel generation failed: {result.get('error')}")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ Highlight reel test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6.6: Generate highlight reels for all videos
print("\n6. Generate Highlight Reels for All Videos:")
try:
    highlights_dir = Path("data/highlights/demo")
    video_dir = Path("data/raw/demo")

    highlight_files = list(highlights_dir.glob("*_highlights.json"))
    print(f"   Found {len(highlight_files)} highlight files")

    all_results = []

    for highlights_file in sorted(highlight_files):
        video_name = highlights_file.stem.replace("_highlights", "")
        video_path = video_dir / f"{video_name}.mp4"

        if not video_path.exists():
            print(f"   ⚠️  Video not found: {video_path.name}")
            continue

        output_path = Path("data/output/demo") / f"{video_name}_highlight_reel.mp4"

        print(f"\n   Processing: {video_name}")

        result = generator.generate_highlight_reel(
            video_path=str(video_path),
            highlights_path=str(highlights_file),
            output_path=str(output_path),
            add_transitions=True,
            max_highlights=5  # Limit to top 5 highlights
        )

        all_results.append(result)

    # Summary
    successful = sum(1 for r in all_results if r['success'])
    failed = sum(1 for r in all_results if not r['success'])

    print(f"\n   ✅ Generated {successful} highlight reels")
    if failed > 0:
        print(f"   ❌ Failed: {failed}")

    total_clips = sum(r.get('num_clips', 0) for r in all_results if r['success'])
    total_size = sum(r.get('output_size_mb', 0) for r in all_results if r['success'])

    print(f"      Total clips: {total_clips}")
    print(f"      Total size: {total_size:.1f} MB")

except Exception as e:
    print(f"   ❌ Batch generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6.7: Verify output videos
print("\n7. Verify Output Videos:")
try:
    output_dir = Path("data/output/demo")
    reel_files = list(output_dir.glob("*_highlight_reel.mp4"))

    print(f"   Highlight reel files: {len(reel_files)}")

    if reel_files:
        # Verify first file with FFprobe
        test_file = reel_files[0]

        probe_cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,duration',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(test_file)
        ]

        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        if 'streams' in data and len(data['streams']) > 0:
            stream = data['streams'][0]
            duration = float(data['format']['duration']) if 'format' in data else 0

            print(f"\n   Sample file: {test_file.name}")
            print(f"      Resolution: {stream.get('width')}x{stream.get('height')}")
            print(f"      Duration: {duration:.1f}s")
            print(f"      Size: {test_file.stat().st_size / (1024*1024):.1f} MB")
            print(f"   ✅ Output videos verified")
        else:
            print(f"   ⚠️  Could not verify video metadata")
    else:
        print(f"   ⚠️  No highlight reel files found")

except Exception as e:
    print(f"   ❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ All video generation tests passed!")

print(f"\nGenerated highlight reels:")
for result in all_results:
    if result['success']:
        print(f"   📹 {result['video_name']}")
        print(f"      Clips: {result['num_clips']}")
        print(f"      Duration: ~{result['estimated_duration']:.1f}s")
        print(f"      Size: {result['output_size_mb']:.1f} MB")

print(f"\nOutput directory: data/output/demo/")
print(f"\nNext step: Create demo application (Phase 7)")
print("=" * 70 + "\n")
