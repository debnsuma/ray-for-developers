# Setup Guide - M4 MacBook Pro

Step-by-step setup instructions tested on M4 MacBook Pro.

## ✅ Prerequisites

- macOS with M4 chip
- Python 3.12
- Homebrew
- uv package manager

## 🚀 Quick Setup

### Step 1: Clone Repository

```bash
cd /Users/suman/Work/code/ray-for-developers/03-multimodal-data-processing/video-highlight-generator
```

### Step 2: Create Virtual Environment

```bash
# Create venv with Python 3.12
uv venv --python 3.12

# Activate the environment
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
uv pip install -r requirements.txt
```

This installs:
- Ray 2.39.0 (distributed computing)
- PyTorch 2.5.1 (ML framework with MPS support)
- OpenCV 4.10.0 (video processing)
- Transformers, librosa, and other ML libraries

**Installation time**: ~2-3 minutes

### Step 4: Install FFmpeg

```bash
# Install via Homebrew
brew install ffmpeg

# Verify installation
ffmpeg -version
```

### Step 5: Test Environment

```bash
# Run environment test
python test_01_environment.py
```

**Expected output**:
```
======================================================================
TEST 1: Environment Setup
======================================================================

1. Python Version:
   ✅ Python 3.12+ detected

2. Core Package Imports:
   ✅ numpy 1.26.4
   ✅ opencv-python 4.10.0
   ✅ torch 2.5.1
   ✅ ray 2.39.0

3. MPS (Metal Performance Shaders) Status:
   MPS Available: True
   MPS Built: True
   ✅ MPS device: mps

4. PyTorch Computation Test:
   ✅ PyTorch computation successful on mps

5. Ray Framework Test:
   ✅ Ray framework working correctly

6. Ray + PyTorch Integration:
   ✅ Ray + PyTorch integration working

7. FFmpeg Availability:
   ✅ FFmpeg available

======================================================================
SUMMARY
======================================================================
✅ All critical tests passed!
======================================================================
```

## 📊 System Requirements

### Tested Configuration

- **Hardware**: MacBook Pro M4
- **OS**: macOS Sequoia 15.x
- **Python**: 3.12.7
- **RAM**: 16GB+ recommended
- **Storage**: 10GB free space (for dependencies + datasets)

### Performance Expectations

On M4 MacBook Pro:
- **MPS acceleration**: ✅ Available
- **Ray workers**: 4 (recommended)
- **Video processing**: ~20 FPS for frame extraction
- **Model inference**: ~100+ FPS (MobileNetV3)

## 🔧 Troubleshooting

### Issue: MPS not available

**Solution**:
```bash
# Upgrade PyTorch
uv pip install --upgrade torch torchvision
```

### Issue: Ray won't initialize

**Solution**:
```bash
# Stop any existing Ray instances
ray stop

# Clear Ray temp files
rm -rf /tmp/ray

# Restart Ray
python test_01_environment.py
```

### Issue: FFmpeg not found

**Solution**:
```bash
# Install FFmpeg
brew install ffmpeg

# Add to PATH if needed
export PATH="/opt/homebrew/bin:$PATH"
```

### Issue: Out of Memory

**Solution**:
```python
# Reduce Ray workers in your scripts
ray.init(num_cpus=2)  # Instead of 4
```

## 📝 Verification Checklist

Run through this checklist to verify your setup:

- [ ] Python 3.12+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed via uv
- [ ] FFmpeg installed and accessible
- [ ] test_01_environment.py passes all tests
- [ ] Ray dashboard accessible at http://127.0.0.1:8265
- [ ] MPS (Metal) acceleration available

## 🎯 Next Steps

Once setup is complete:

1. **Download sample videos**: `python scripts/download_sample_videos.py`
2. **Test video loading**: `python test_02_video_loading.py`
3. **Test preprocessing**: `python test_03_preprocessing.py`
4. **Run end-to-end demo**: `python demo/simple_demo.py`

## 🐛 Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Review test output for specific error messages
3. Open an issue on GitHub with:
   - Your system configuration
   - Complete error message
   - Output of `python test_01_environment.py`

---

**Last Updated**: 2025-10-12
**Tested On**: M4 MacBook Pro, macOS Sequoia, Python 3.12.7
