"""
Highlight Detection for Video Processing
Analyzes visual features to identify interesting moments
Optimized for M4 MacBook Pro
"""
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from scipy import signal
from scipy.spatial.distance import cosine


class HighlightDetector:
    """
    Detect highlights in videos based on visual features

    Uses multiple signals to identify interesting moments:
    1. Feature variance - scenes with high visual change
    2. Feature novelty - unique/rare scenes
    3. Motion intensity - rapid visual changes
    """

    def __init__(
        self,
        variance_weight: float = 0.4,
        novelty_weight: float = 0.3,
        motion_weight: float = 0.3
    ):
        """
        Initialize the highlight detector

        Args:
            variance_weight: Weight for feature variance signal
            novelty_weight: Weight for feature novelty signal
            motion_weight: Weight for motion intensity signal
        """
        self.variance_weight = variance_weight
        self.novelty_weight = novelty_weight
        self.motion_weight = motion_weight

        # Normalize weights
        total = variance_weight + novelty_weight + motion_weight
        self.variance_weight /= total
        self.novelty_weight /= total
        self.motion_weight /= total

        print(f"🔍 HighlightDetector initialized")
        print(f"   Variance weight: {self.variance_weight:.2f}")
        print(f"   Novelty weight: {self.novelty_weight:.2f}")
        print(f"   Motion weight: {self.motion_weight:.2f}")

    def compute_variance_score(self, features: np.ndarray, window_size: int = 10) -> np.ndarray:
        """
        Compute feature variance score
        High variance indicates visually diverse scenes

        Args:
            features: Feature array (num_frames, feature_dim)
            window_size: Window size for rolling variance

        Returns:
            Variance score for each frame
        """
        num_frames = features.shape[0]
        variance_scores = np.zeros(num_frames)

        for i in range(num_frames):
            # Get window around current frame
            start = max(0, i - window_size // 2)
            end = min(num_frames, i + window_size // 2 + 1)
            window = features[start:end]

            # Compute variance across features in window
            variance_scores[i] = np.var(window, axis=0).mean()

        return variance_scores

    def compute_novelty_score(self, features: np.ndarray, k: int = 20) -> np.ndarray:
        """
        Compute feature novelty score
        High novelty indicates unique/rare scenes

        Args:
            features: Feature array (num_frames, feature_dim)
            k: Number of nearest neighbors to consider

        Returns:
            Novelty score for each frame
        """
        num_frames = features.shape[0]
        novelty_scores = np.zeros(num_frames)

        # Normalize features
        features_norm = features / (np.linalg.norm(features, axis=1, keepdims=True) + 1e-8)

        for i in range(num_frames):
            # Compute distances to all other frames
            distances = np.linalg.norm(features_norm - features_norm[i], axis=1)

            # Get k nearest neighbors (excluding self)
            k_nearest = np.partition(distances, min(k, num_frames - 1))[:min(k + 1, num_frames)]
            k_nearest = k_nearest[k_nearest > 0]  # Exclude self (distance = 0)

            # Novelty is average distance to k nearest neighbors
            novelty_scores[i] = k_nearest.mean() if len(k_nearest) > 0 else 0

        return novelty_scores

    def compute_motion_score(self, features: np.ndarray) -> np.ndarray:
        """
        Compute motion intensity score
        High motion indicates rapid visual changes

        Args:
            features: Feature array (num_frames, feature_dim)

        Returns:
            Motion score for each frame
        """
        num_frames = features.shape[0]

        if num_frames < 2:
            return np.zeros(num_frames)

        # Compute frame-to-frame differences
        diffs = np.diff(features, axis=0)
        motion_scores = np.linalg.norm(diffs, axis=1)

        # Pad to match original length (first frame has no motion)
        motion_scores = np.concatenate([[0], motion_scores])

        return motion_scores

    def compute_importance_score(
        self,
        features: np.ndarray,
        variance_window: int = 10,
        novelty_k: int = 20,
        smoothing_window: int = 5
    ) -> np.ndarray:
        """
        Compute overall importance score for each frame

        Args:
            features: Feature array (num_frames, feature_dim)
            variance_window: Window size for variance computation
            novelty_k: Number of neighbors for novelty computation
            smoothing_window: Window size for smoothing final scores

        Returns:
            Importance score for each frame (normalized to [0, 1])
        """
        print(f"   Computing importance scores...")
        print(f"      Frames: {features.shape[0]}")

        # Compute individual signals
        variance_scores = self.compute_variance_score(features, variance_window)
        novelty_scores = self.compute_novelty_score(features, novelty_k)
        motion_scores = self.compute_motion_score(features)

        # Normalize each signal to [0, 1]
        variance_scores = self._normalize(variance_scores)
        novelty_scores = self._normalize(novelty_scores)
        motion_scores = self._normalize(motion_scores)

        # Combine signals
        importance_scores = (
            self.variance_weight * variance_scores +
            self.novelty_weight * novelty_scores +
            self.motion_weight * motion_scores
        )

        # Smooth the scores
        if smoothing_window > 1:
            kernel = np.ones(smoothing_window) / smoothing_window
            importance_scores = np.convolve(importance_scores, kernel, mode='same')

        # Normalize final scores
        importance_scores = self._normalize(importance_scores)

        print(f"      Min score: {importance_scores.min():.4f}")
        print(f"      Max score: {importance_scores.max():.4f}")
        print(f"      Mean score: {importance_scores.mean():.4f}")

        return importance_scores

    def _normalize(self, scores: np.ndarray) -> np.ndarray:
        """Normalize scores to [0, 1]"""
        min_score = scores.min()
        max_score = scores.max()

        if max_score - min_score < 1e-8:
            return np.zeros_like(scores)

        return (scores - min_score) / (max_score - min_score)

    def detect_peaks_auto(
        self,
        importance_scores: np.ndarray,
        video_duration: float,
        min_distance: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Intelligently detect peaks based on score distribution

        Auto-determines:
        - Threshold based on score percentile
        - Number of highlights based on video length

        Args:
            importance_scores: Importance scores for each frame
            video_duration: Duration of video in seconds
            min_distance: Minimum distance between peaks

        Returns:
            Tuple of (peak_indices, peak_scores)
        """
        # Auto-determine threshold using percentile
        # For short videos (< 1min): 75th percentile
        # For medium videos (1-5min): 70th percentile
        # For long videos (> 5min): 65th percentile
        if video_duration < 60:
            threshold_percentile = 75
        elif video_duration < 300:
            threshold_percentile = 70
        else:
            threshold_percentile = 65

        threshold = np.percentile(importance_scores, threshold_percentile)

        print(f"   Auto-threshold: {threshold:.3f} ({threshold_percentile}th percentile)")

        # Find peaks
        peaks, properties = signal.find_peaks(
            importance_scores,
            height=threshold,
            distance=min_distance
        )

        peak_scores = importance_scores[peaks]

        # Auto-determine max highlights based on video duration
        # Rule: ~1 highlight per 30 seconds, min 1, max 15
        max_highlights = max(1, min(15, int(video_duration / 30)))

        print(f"   Max highlights for {video_duration:.0f}s video: {max_highlights}")

        # Sort by score (descending)
        sorted_indices = np.argsort(peak_scores)[::-1]
        peaks = peaks[sorted_indices]
        peak_scores = peak_scores[sorted_indices]

        # Limit to max highlights
        if len(peaks) > max_highlights:
            peaks = peaks[:max_highlights]
            peak_scores = peak_scores[:max_highlights]

        return peaks, peak_scores

    def detect_peaks(
        self,
        importance_scores: np.ndarray,
        num_peaks: Optional[int] = None,
        min_distance: int = 10,
        threshold: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect peaks in importance scores (manual mode)

        Args:
            importance_scores: Importance scores for each frame
            num_peaks: Number of peaks to return (None = auto)
            min_distance: Minimum distance between peaks
            threshold: Minimum threshold for peak detection

        Returns:
            Tuple of (peak_indices, peak_scores)
        """
        # Find peaks using scipy
        peaks, properties = signal.find_peaks(
            importance_scores,
            height=threshold,
            distance=min_distance
        )

        peak_scores = importance_scores[peaks]

        # Sort by score (descending)
        sorted_indices = np.argsort(peak_scores)[::-1]
        peaks = peaks[sorted_indices]
        peak_scores = peak_scores[sorted_indices]

        # Limit number of peaks if specified
        if num_peaks is not None and len(peaks) > num_peaks:
            peaks = peaks[:num_peaks]
            peak_scores = peak_scores[:num_peaks]

        return peaks, peak_scores

    def detect_highlights_auto(
        self,
        features_path: str,
        min_distance: int = 10,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Intelligently detect highlights with auto-configuration

        Args:
            features_path: Path to .npy file with features
            min_distance: Minimum frames between highlights
            output_path: Optional path to save results

        Returns:
            Dictionary with highlight information
        """
        # Load features
        features_path = Path(features_path)
        features = np.load(features_path)

        print(f"\n🎬 Auto-detecting highlights: {features_path.stem}")
        print(f"   Features shape: {features.shape}")

        # Load metadata if available
        metadata_path = features_path.parent / f"{features_path.stem}_metadata.json"
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

        # Get video info
        num_frames = features.shape[0]
        original_fps = metadata.get('original_metadata', {}).get('original_fps', 24.0)
        target_fps = metadata.get('original_metadata', {}).get('target_fps', 1.0)
        duration = num_frames / target_fps

        print(f"   Video duration: {duration:.0f}s")

        # Compute importance scores
        importance_scores = self.compute_importance_score(features)

        # Auto-detect peaks
        print(f"   Using intelligent auto-detection...")
        peak_indices, peak_scores = self.detect_peaks_auto(
            importance_scores,
            video_duration=duration,
            min_distance=min_distance
        )

        print(f"   Found {len(peak_indices)} highlights")

        # Convert frame indices to timestamps and determine clip durations
        highlights = []
        for idx, score in zip(peak_indices, peak_scores):
            timestamp = idx / target_fps

            # Determine clip duration based on surrounding importance
            clip_duration = self._compute_adaptive_duration(
                importance_scores,
                idx,
                target_fps,
                min_duration=2.0,
                max_duration=10.0
            )

            highlights.append({
                'frame_index': int(idx),
                'timestamp': float(timestamp),
                'importance_score': float(score),
                'clip_duration': float(clip_duration)
            })

        # Sort by timestamp
        highlights.sort(key=lambda x: x['timestamp'])

        result = {
            'video_name': metadata.get('video_name', features_path.stem),
            'num_frames': num_frames,
            'original_fps': original_fps,
            'target_fps': target_fps,
            'duration': duration,
            'num_highlights': len(highlights),
            'highlights': highlights,
            'importance_scores': importance_scores.tolist(),
            'features_path': str(features_path),
            'detection_mode': 'auto'
        }

        # Print highlights
        print(f"\n   Highlights:")
        for i, h in enumerate(highlights, 1):
            mins = int(h['timestamp'] // 60)
            secs = int(h['timestamp'] % 60)
            print(f"      {i}. {mins:02d}:{secs:02d} (frame {h['frame_index']}) - score: {h['importance_score']:.3f}, duration: {h['clip_duration']:.1f}s")

        # Save results if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)

            print(f"\n   💾 Saved highlights to {output_path}")

        return result

    def _compute_adaptive_duration(
        self,
        importance_scores: np.ndarray,
        peak_idx: int,
        target_fps: float,
        min_duration: float = 2.0,
        max_duration: float = 10.0,
        threshold_ratio: float = 0.6
    ) -> float:
        """
        Compute adaptive clip duration based on surrounding importance

        Args:
            importance_scores: All importance scores
            peak_idx: Index of the peak
            target_fps: Target FPS
            min_duration: Minimum clip duration
            max_duration: Maximum clip duration
            threshold_ratio: Ratio of peak score to consider as "interesting"

        Returns:
            Clip duration in seconds
        """
        peak_score = importance_scores[peak_idx]
        threshold = peak_score * threshold_ratio

        # Find region where score stays above threshold
        start_idx = peak_idx
        end_idx = peak_idx

        # Search backward
        for i in range(peak_idx - 1, -1, -1):
            if importance_scores[i] >= threshold:
                start_idx = i
            else:
                break

        # Search forward
        for i in range(peak_idx + 1, len(importance_scores)):
            if importance_scores[i] >= threshold:
                end_idx = i
            else:
                break

        # Convert to duration
        duration = (end_idx - start_idx + 1) / target_fps

        # Clamp to min/max
        duration = max(min_duration, min(max_duration, duration))

        return duration

    def detect_highlights(
        self,
        features_path: str,
        num_highlights: int = 5,
        min_distance: int = 10,
        threshold: float = 0.5,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Detect highlights from extracted features (manual mode)

        Args:
            features_path: Path to .npy file with features
            num_highlights: Number of highlights to extract
            min_distance: Minimum frames between highlights
            threshold: Minimum importance threshold
            output_path: Optional path to save results

        Returns:
            Dictionary with highlight information
        """
        # Load features
        features_path = Path(features_path)
        features = np.load(features_path)

        print(f"\n🎬 Detecting highlights: {features_path.stem}")
        print(f"   Features shape: {features.shape}")

        # Load metadata if available
        metadata_path = features_path.parent / f"{features_path.stem}_metadata.json"
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

        # Get video info
        num_frames = features.shape[0]
        original_fps = metadata.get('original_metadata', {}).get('original_fps', 24.0)
        target_fps = metadata.get('original_metadata', {}).get('target_fps', 1.0)

        # Compute importance scores
        importance_scores = self.compute_importance_score(features)

        # Detect peaks
        print(f"   Detecting top {num_highlights} highlights...")
        peak_indices, peak_scores = self.detect_peaks(
            importance_scores,
            num_peaks=num_highlights,
            min_distance=min_distance,
            threshold=threshold
        )

        print(f"   Found {len(peak_indices)} highlights")

        # Convert frame indices to timestamps
        highlights = []
        for idx, score in zip(peak_indices, peak_scores):
            timestamp = idx / target_fps  # Time in seconds at target FPS

            highlights.append({
                'frame_index': int(idx),
                'timestamp': float(timestamp),
                'importance_score': float(score)
            })

        # Sort by timestamp
        highlights.sort(key=lambda x: x['timestamp'])

        result = {
            'video_name': metadata.get('video_name', features_path.stem),
            'num_frames': num_frames,
            'original_fps': original_fps,
            'target_fps': target_fps,
            'duration': num_frames / target_fps,
            'num_highlights': len(highlights),
            'highlights': highlights,
            'importance_scores': importance_scores.tolist(),
            'features_path': str(features_path)
        }

        # Print highlights
        print(f"\n   Highlights:")
        for i, h in enumerate(highlights, 1):
            mins = int(h['timestamp'] // 60)
            secs = int(h['timestamp'] % 60)
            print(f"      {i}. {mins:02d}:{secs:02d} (frame {h['frame_index']}) - score: {h['importance_score']:.3f}")

        # Save results if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)

            print(f"\n   💾 Saved highlights to {output_path}")

        return result
