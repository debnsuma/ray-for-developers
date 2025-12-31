"""
Visual Feature Extraction with Ray Actors
Supports GPU acceleration (CUDA/MPS) and CPU fallback
Uses MobileNetV3-small for lightweight, fast inference
"""
import ray
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import json


@ray.remote
class VisualFeatureExtractor:
    """
    Ray Actor for extracting visual features from video frames
    Automatically selects best available device (CUDA > MPS > CPU)
    """

    def __init__(self, model_name: str = "mobilenet_v3_small", use_gpu: bool = True):
        """
        Initialize the feature extractor

        Args:
            model_name: Model to use (mobilenet_v3_small for lightweight inference)
            use_gpu: Use GPU acceleration (CUDA/MPS) if available
        """
        print(f"🔧 Initializing VisualFeatureExtractor (Ray Actor)...")

        # Select best available device
        if use_gpu:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                print(f"   Using CUDA acceleration (GPU: {torch.cuda.get_device_name(0)})")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
                print(f"   Using MPS acceleration (Apple Silicon)")
            else:
                self.device = torch.device("cpu")
                print(f"   GPU not available, using CPU")
        else:
            self.device = torch.device("cpu")
            print(f"   Using CPU")

        # Load MobileNetV3-small (lightweight, fast on M4)
        print(f"   Loading {model_name}...")
        if model_name == "mobilenet_v3_small":
            self.model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
        elif model_name == "mobilenet_v3_large":
            self.model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.IMAGENET1K_V1)
        else:
            raise ValueError(f"Unsupported model: {model_name}")

        # Remove classifier to get features
        # MobileNetV3: features -> avgpool -> classifier
        # We want output after avgpool (before classifier)
        self.model.classifier = torch.nn.Identity()

        self.model.to(self.device)
        self.model.eval()

        # Image preprocessing pipeline
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        print(f"   ✅ Model loaded and ready on {self.device}")

    def extract_frame_features(self, frame_path: str) -> np.ndarray:
        """
        Extract features from a single frame

        Args:
            frame_path: Path to frame image

        Returns:
            Feature vector as numpy array
        """
        # Load image
        img = Image.open(frame_path).convert('RGB')

        # Preprocess
        img_tensor = self.transform(img).unsqueeze(0).to(self.device)

        # Extract features
        with torch.no_grad():
            features = self.model(img_tensor)

            # Synchronize based on device type
            if self.device.type == "cuda":
                torch.cuda.synchronize()
            elif self.device.type == "mps":
                torch.mps.synchronize()

        # Convert to numpy
        features_np = features.cpu().numpy().squeeze()

        return features_np

    def extract_video_features(
        self,
        video_dir: str,
        output_path: Optional[str] = None,
        progress_callback: Optional[object] = None
    ) -> Dict:
        """
        Extract features from all frames in a video directory

        Args:
            video_dir: Path to processed video directory (contains frames/)
            output_path: Optional path to save features
            progress_callback: Optional callback for progress updates (frame_idx, total_frames)

        Returns:
            Dictionary with features and metadata
        """
        video_path = Path(video_dir)
        frames_dir = video_path / "frames"

        if not frames_dir.exists():
            return {
                'success': False,
                'error': f'Frames directory not found: {frames_dir}'
            }

        # Get all frames
        frame_files = sorted(frames_dir.glob("frame_*.jpg"))

        if not frame_files:
            return {
                'success': False,
                'error': f'No frames found in {frames_dir}'
            }

        print(f"\n📹 Extracting features: {video_path.name}")
        print(f"   Frames: {len(frame_files)}")

        # Extract features for each frame
        features_list = []

        for i, frame_path in enumerate(frame_files):
            features = self.extract_frame_features(str(frame_path))
            features_list.append(features)

            # Progress callback
            if progress_callback:
                # Return progress info
                progress_callback.remote('progress', i + 1, len(frame_files))

            if (i + 1) % 100 == 0:
                print(f"   Processed {i + 1}/{len(frame_files)} frames...")

        # Stack into array
        features_array = np.stack(features_list)

        print(f"   ✅ Features shape: {features_array.shape}")

        # Load metadata
        metadata_path = video_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}

        result = {
            'success': True,
            'video_name': video_path.name,
            'features': features_array,
            'num_frames': len(frame_files),
            'feature_dim': features_array.shape[1],
            'metadata': metadata
        }

        # Save features if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            np.save(output_path, features_array)

            # Save metadata
            meta_output = output_path.parent / f"{output_path.stem}_metadata.json"
            with open(meta_output, 'w') as f:
                json.dump({
                    'video_name': result['video_name'],
                    'num_frames': result['num_frames'],
                    'feature_dim': result['feature_dim'],
                    'features_path': str(output_path),
                    'original_metadata': metadata
                }, f, indent=2)

            print(f"   💾 Saved features to {output_path}")
            result['output_path'] = str(output_path)

        return result

    def get_device_info(self) -> Dict[str, str]:
        """Get information about the device being used"""
        return {
            'device': str(self.device),
            'device_type': self.device.type,
            'cuda_available': torch.cuda.is_available(),
            'mps_available': torch.backends.mps.is_available()
        }


def create_feature_extractor_pool(num_actors: int = 2) -> List:
    """
    Create a pool of VisualFeatureExtractor actors

    Args:
        num_actors: Number of actors to create

    Returns:
        List of actor handles
    """
    print(f"\n🚀 Creating pool of {num_actors} VisualFeatureExtractor actors...")

    actors = [
        VisualFeatureExtractor.remote(model_name="mobilenet_v3_small", use_gpu=True)
        for _ in range(num_actors)
    ]

    print(f"✅ Created {num_actors} actors")

    return actors
