"""
End-to-End Video Highlight Generation Pipeline
Orchestrates all phases with Ray monitoring
"""
import ray
import time
from pathlib import Path
from typing import Dict, Optional, Callable
import json
import shutil

from src.models.feature_extractors import create_feature_extractor_pool
from src.features.highlight_detector import HighlightDetector
from src.features.video_generator import VideoHighlightGenerator


class VideoHighlightPipeline:
    """
    End-to-end pipeline for video highlight generation

    Phases:
    1. Preprocessing: Extract frames and audio
    2. Feature Extraction: Extract visual features with Ray Actors
    3. Highlight Detection: Identify important moments
    4. Video Generation: Create highlight reel
    """

    def __init__(
        self,
        num_actors: int = 2,
        target_fps: float = 1.0,
        resolution: tuple = (224, 224),
        num_highlights: Optional[int] = None,
        clip_duration: Optional[float] = None,
        auto_detect: bool = True,
        max_reel_duration: float = 30.0,
        progress_callback: Optional[Callable] = None
    ):
        """
        Initialize the pipeline

        Args:
            num_actors: Number of Ray actors for feature extraction
            target_fps: Target FPS for frame extraction
            resolution: Target resolution for frames
            num_highlights: Number of highlights (None = auto)
            clip_duration: Duration of each highlight clip (None = adaptive)
            auto_detect: Use intelligent auto-detection (recommended)
            max_reel_duration: Maximum total duration of highlight reel in seconds (default: 30s)
            progress_callback: Optional callback for progress updates
        """
        self.num_actors = num_actors
        self.target_fps = target_fps
        self.resolution = resolution
        self.num_highlights = num_highlights
        self.clip_duration = clip_duration
        self.auto_detect = auto_detect
        self.max_reel_duration = max_reel_duration
        self.progress_callback = progress_callback

        # Initialize components
        self.detector = HighlightDetector()

        # Only initialize generator with fixed duration if not auto-detecting
        if not auto_detect and clip_duration is not None:
            self.generator = VideoHighlightGenerator(clip_duration=clip_duration)
        else:
            self.generator = VideoHighlightGenerator(clip_duration=3.0)  # Default

        self.ray_initialized = False

    def _log(self, message: str, phase: str = "INFO"):
        """Log message and call progress callback"""
        print(f"[{phase}] {message}")
        if self.progress_callback:
            self.progress_callback(phase, message)

    def initialize_ray(self):
        """Initialize Ray cluster"""
        if not self.ray_initialized:
            self._log("Initializing Ray...", "SETUP")
            ray.init(num_cpus=4, ignore_reinit_error=True)
            self.ray_initialized = True
            self._log(f"Ray initialized with {ray.available_resources().get('CPU', 0):.0f} CPUs", "SETUP")

    def shutdown_ray(self):
        """Shutdown Ray cluster"""
        if self.ray_initialized:
            ray.shutdown()
            self.ray_initialized = False
            self._log("Ray shutdown complete", "SETUP")

    def preprocess_video(
        self,
        video_path: str,
        output_dir: str
    ) -> Dict:
        """
        Phase 1: Preprocess video (extract frames and audio)
        """
        self._log(f"Starting preprocessing: {Path(video_path).name}", "PHASE 1")

        from scripts.preprocess_videos import preprocess_video

        start_time = time.time()

        # Create fake row structure for preprocess_video function
        video_path_obj = Path(video_path)
        with open(video_path, 'rb') as f:
            video_bytes = f.read()

        row = {
            'path': str(video_path_obj.absolute()),
            'bytes': video_bytes
        }

        # Set output directory temporarily
        original_output = Path("data/processed/demo")
        custom_output = Path(output_dir)

        # Preprocess
        result = preprocess_video(row, target_fps=self.target_fps, resolution=self.resolution)

        # Move to custom output if different
        if custom_output != original_output:
            video_name = video_path_obj.stem
            source = original_output / video_name
            dest = custom_output / video_name

            if source.exists() and source != dest:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(source), str(dest))
                result['output_dir'] = str(dest)

        elapsed = time.time() - start_time

        if result['success']:
            self._log(
                f"Preprocessing complete: {result['extracted_frames']} frames in {elapsed:.1f}s",
                "PHASE 1"
            )
        else:
            self._log(f"Preprocessing failed: {result.get('error')}", "PHASE 1")

        result['elapsed'] = elapsed
        return result

    def extract_features(
        self,
        processed_dir: str,
        output_path: str
    ) -> Dict:
        """
        Phase 2: Extract visual features with Ray Actors
        """
        self._log(f"Starting feature extraction", "PHASE 2")

        start_time = time.time()

        # Create feature extractor actor pool
        self._log(f"Creating {self.num_actors} Ray Actors for feature extraction", "PHASE 2")
        actors = create_feature_extractor_pool(num_actors=self.num_actors)

        # Use first actor to extract features
        actor = actors[0]

        result = ray.get(actor.extract_video_features.remote(
            video_dir=processed_dir,
            output_path=output_path
        ))

        elapsed = time.time() - start_time

        if result['success']:
            fps = result['num_frames'] / elapsed
            self._log(
                f"Feature extraction complete: {result['num_frames']} frames at {fps:.1f} FPS",
                "PHASE 2"
            )
        else:
            self._log(f"Feature extraction failed: {result.get('error')}", "PHASE 2")

        result['elapsed'] = elapsed
        return result

    def detect_highlights(
        self,
        features_path: str,
        output_path: str
    ) -> Dict:
        """
        Phase 3: Detect highlights from features
        """
        self._log(f"Starting highlight detection", "PHASE 3")

        start_time = time.time()

        # Use auto-detection or manual mode
        if self.auto_detect:
            self._log("Using intelligent auto-detection", "PHASE 3")
            result = self.detector.detect_highlights_auto(
                features_path=features_path,
                output_path=output_path
            )
        else:
            self._log(f"Using manual mode: {self.num_highlights} highlights", "PHASE 3")
            result = self.detector.detect_highlights(
                features_path=features_path,
                num_highlights=self.num_highlights,
                output_path=output_path
            )

        elapsed = time.time() - start_time

        self._log(
            f"Highlight detection complete: {result['num_highlights']} highlights in {elapsed:.1f}s",
            "PHASE 3"
        )

        result['elapsed'] = elapsed
        return result

    def generate_highlight_reel(
        self,
        video_path: str,
        highlights_path: str,
        output_path: str
    ) -> Dict:
        """
        Phase 4: Generate highlight video reel
        """
        self._log(f"Starting highlight reel generation (max {self.max_reel_duration}s)", "PHASE 4")

        start_time = time.time()

        result = self.generator.generate_highlight_reel(
            video_path=video_path,
            highlights_path=highlights_path,
            output_path=output_path,
            add_transitions=True,
            max_highlights=self.num_highlights,
            max_duration=self.max_reel_duration
        )

        elapsed = time.time() - start_time

        if result['success']:
            actual_duration = result.get('actual_duration', result.get('estimated_duration', 0))
            self._log(
                f"Highlight reel complete: {result['num_clips']} clips, {actual_duration:.1f}s duration, {result['output_size_mb']:.1f}MB in {elapsed:.1f}s",
                "PHASE 4"
            )
        else:
            self._log(f"Highlight reel failed: {result.get('error')}", "PHASE 4")

        result['elapsed'] = elapsed
        return result

    def run(
        self,
        video_path: str,
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Run the complete end-to-end pipeline

        Args:
            video_path: Path to input video
            output_dir: Optional output directory (default: data/pipeline/{video_name})

        Returns:
            Dictionary with all results and timing information
        """
        video_name = Path(video_path).stem

        if output_dir is None:
            output_dir = f"data/pipeline/{video_name}"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self._log(f"=" * 70, "PIPELINE")
        self._log(f"Starting pipeline for: {video_name}", "PIPELINE")
        self._log(f"Output directory: {output_path}", "PIPELINE")
        self._log(f"=" * 70, "PIPELINE")

        pipeline_start = time.time()

        results = {
            'video_name': video_name,
            'video_path': video_path,
            'output_dir': str(output_path)
        }

        try:
            # Initialize Ray
            self.initialize_ray()

            # Phase 1: Preprocessing
            processed_dir = output_path / "processed"
            preprocess_result = self.preprocess_video(
                video_path=video_path,
                output_dir=str(processed_dir)
            )
            results['preprocessing'] = preprocess_result

            if not preprocess_result['success']:
                raise Exception(f"Preprocessing failed: {preprocess_result.get('error')}")

            # Phase 2: Feature Extraction
            features_path = output_path / f"{video_name}_features.npy"
            features_result = self.extract_features(
                processed_dir=preprocess_result['output_dir'],
                output_path=str(features_path)
            )
            results['features'] = features_result

            if not features_result['success']:
                raise Exception(f"Feature extraction failed: {features_result.get('error')}")

            # Phase 3: Highlight Detection
            highlights_path = output_path / f"{video_name}_highlights.json"
            highlights_result = self.detect_highlights(
                features_path=str(features_path),
                output_path=str(highlights_path)
            )
            results['highlights'] = highlights_result

            # Phase 4: Video Generation
            output_video = output_path / f"{video_name}_highlight_reel.mp4"
            generation_result = self.generate_highlight_reel(
                video_path=video_path,
                highlights_path=str(highlights_path),
                output_path=str(output_video)
            )
            results['generation'] = generation_result

            if not generation_result['success']:
                raise Exception(f"Video generation failed: {generation_result.get('error')}")

            # Success!
            pipeline_elapsed = time.time() - pipeline_start

            results['success'] = True
            results['total_time'] = pipeline_elapsed
            results['output_video'] = str(output_video)

            self._log(f"=" * 70, "PIPELINE")
            self._log(f"Pipeline complete!", "PIPELINE")
            self._log(f"Total time: {pipeline_elapsed:.1f}s", "PIPELINE")
            self._log(f"Output: {output_video}", "PIPELINE")
            self._log(f"=" * 70, "PIPELINE")

            # Save pipeline results
            results_path = output_path / "pipeline_results.json"
            with open(results_path, 'w') as f:
                # Convert non-serializable fields
                results_copy = results.copy()
                if 'features' in results_copy and 'features' in results_copy['features']:
                    del results_copy['features']['features']  # Remove numpy array
                json.dump(results_copy, f, indent=2)

            return results

        except Exception as e:
            pipeline_elapsed = time.time() - pipeline_start

            self._log(f"Pipeline failed: {str(e)}", "ERROR")

            results['success'] = False
            results['error'] = str(e)
            results['total_time'] = pipeline_elapsed

            return results

        finally:
            # Shutdown Ray
            self.shutdown_ray()
