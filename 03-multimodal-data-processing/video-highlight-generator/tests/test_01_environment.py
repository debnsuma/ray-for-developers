"""
Test 1: Environment Setup
Verify Ray, PyTorch, and device acceleration are working correctly
Compatible with both Mac (local) and Ray cluster environments
"""
import sys
import os

print("=" * 70)
print("TEST 1: Environment Setup")
print("=" * 70)
print(f"Environment: {'Ray Cluster' if os.environ.get('RAY_ADDRESS') else 'Local'}")
print("=" * 70)

# Test 1.1: Python version
print("\n1. Python Version:")
print(f"   Version: {sys.version}")
if sys.version_info >= (3, 12):
    print("   ✅ Python 3.12+ detected")
else:
    print("   ❌ Python 3.12+ required, current version is below 3.12")

# Test 1.2: Import core packages
print("\n2. Core Package Imports:")
try:
    import numpy as np
    print(f"   ✅ numpy {np.__version__}")
except ImportError as e:
    print(f"   ❌ numpy import failed: {e}")
    sys.exit(1)

try:
    import cv2
    print(f"   ✅ opencv-python {cv2.__version__}")
except ImportError as e:
    print(f"   ❌ opencv-python import failed: {e}")
    sys.exit(1)

try:
    import torch
    print(f"   ✅ torch {torch.__version__}")
except ImportError as e:
    print(f"   ❌ torch import failed: {e}")
    sys.exit(1)

try:
    import ray
    print(f"   ✅ ray {ray.__version__}")
except ImportError as e:
    print(f"   ❌ ray import failed: {e}")
    sys.exit(1)

# Test 1.3: Device acceleration status
print("\n3. Device Acceleration Status:")
print(f"   CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   CUDA Device Count: {torch.cuda.device_count()}")
    print(f"   CUDA Device Name: {torch.cuda.get_device_name(0)}")
print(f"   MPS Available: {torch.backends.mps.is_available()}")
print(f"   MPS Built: {torch.backends.mps.is_built()}")

# Select best available device
if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"   ✅ Using CUDA device: {device}")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
    print(f"   ✅ Using MPS device: {device}")
else:
    device = torch.device("cpu")
    print(f"   ⚠️  No GPU acceleration available, using CPU")

# Test 1.4: Simple PyTorch operation
print("\n4. PyTorch Computation Test:")
try:
    x = torch.randn(100, 100).to(device)
    y = torch.randn(100, 100).to(device)
    z = x @ y  # Matrix multiplication

    # Synchronize based on device type
    if device.type == "cuda":
        torch.cuda.synchronize()
    elif device.type == "mps":
        torch.mps.synchronize()

    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {z.shape}")
    print(f"   Output device: {z.device}")
    print(f"   ✅ PyTorch computation successful on {device}")
except Exception as e:
    print(f"   ❌ PyTorch computation failed: {e}")
    sys.exit(1)

# Test 1.5: Ray initialization
print("\n5. Ray Framework Test:")
try:
    # Import utility for safe Ray initialization
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.utils.ray_utils import safe_ray_init

    # Initialize Ray (handles both local and cluster modes)
    safe_ray_init(num_cpus=4)
    print(f"   Ray initialized: {ray.is_initialized()}")

    # Show available resources
    resources = ray.available_resources()
    print(f"   Available CPUs: {resources.get('CPU', 0):.0f}")
    if 'GPU' in resources:
        print(f"   Available GPUs: {resources.get('GPU', 0):.0f}")

    # Simple Ray task
    @ray.remote
    def test_task(x):
        return x * 2

    result = ray.get(test_task.remote(21))
    assert result == 42, f"Expected 42, got {result}"
    print(f"   Test task result: {result}")
    print(f"   ✅ Ray framework working correctly")

except Exception as e:
    print(f"   ❌ Ray initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 1.6: Ray + PyTorch integration
print("\n6. Ray + PyTorch Integration:")
try:
    @ray.remote
    def pytorch_task(size):
        import torch
        # Select best available device
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

        x = torch.randn(size, size).to(device)
        y = torch.randn(size, size).to(device)
        z = (x @ y).sum().item()
        return z, device

    result, task_device = ray.get(pytorch_task.remote(50))
    print(f"   Task result: {result:.4f}")
    print(f"   Task device: {task_device}")
    print(f"   ✅ Ray + PyTorch integration working")

except Exception as e:
    print(f"   ❌ Ray + PyTorch integration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 1.7: FFmpeg check
print("\n7. FFmpeg Availability:")
try:
    import subprocess
    result = subprocess.run(
        ['ffmpeg', '-version'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        version_line = result.stdout.split('\n')[0]
        print(f"   {version_line}")
        print(f"   ✅ FFmpeg available")
    else:
        print(f"   ❌ FFmpeg not found")
        print(f"   Install with: brew install ffmpeg")
except FileNotFoundError:
    print(f"   ❌ FFmpeg not found in PATH")
    print(f"   Install with: brew install ffmpeg")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ All critical tests passed!")
print(f"\nEnvironment: {'Ray Cluster' if os.environ.get('RAY_ADDRESS') else 'Local'}")
print(f"Device: {device.type.upper()}")
print("\nYour environment is ready for video processing.")
print("\nNext step: Run test_02_video_loading.py")
print("=" * 70 + "\n")

ray.shutdown()
