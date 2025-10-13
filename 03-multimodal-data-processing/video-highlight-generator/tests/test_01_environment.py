"""
Test 1: Environment Setup
Verify Ray, PyTorch, and MPS are working correctly on M4 MacBook Pro
"""
import sys

print("=" * 70)
print("TEST 1: Environment Setup")
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

# Test 1.3: MPS availability
print("\n3. MPS (Metal Performance Shaders) Status:")
print(f"   MPS Available: {torch.backends.mps.is_available()}")
print(f"   MPS Built: {torch.backends.mps.is_built()}")

if torch.backends.mps.is_available():
    device = torch.device("mps")
    print(f"   ✅ MPS device: {device}")
else:
    device = torch.device("cpu")
    print(f"   ⚠️  MPS not available, using CPU")

# Test 1.4: Simple PyTorch operation
print("\n4. PyTorch Computation Test:")
try:
    x = torch.randn(100, 100).to(device)
    y = torch.randn(100, 100).to(device)
    z = x @ y  # Matrix multiplication

    if device.type == "mps":
        torch.mps.synchronize()  # Wait for MPS to finish

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
    ray.init(num_cpus=4, ignore_reinit_error=True)
    print(f"   Ray initialized: {ray.is_initialized()}")
    print(f"   Available resources: {ray.available_resources()}")

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
    sys.exit(1)

# Test 1.6: Ray + PyTorch integration
print("\n6. Ray + PyTorch Integration:")
try:
    @ray.remote
    def pytorch_task(size):
        import torch
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        x = torch.randn(size, size).to(device)
        y = torch.randn(size, size).to(device)
        z = (x @ y).sum().item()
        return z

    result = ray.get(pytorch_task.remote(50))
    print(f"   Task result: {result:.4f}")
    print(f"   ✅ Ray + PyTorch integration working")

except Exception as e:
    print(f"   ❌ Ray + PyTorch integration failed: {e}")
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
print("\nYour M4 MacBook Pro is ready for development.")
print("\nNext step: Run test_02_video_loading.py")
print("=" * 70 + "\n")

ray.shutdown()
