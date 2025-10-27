# Ray for Developers

Welcome to **Ray for Developers** - your comprehensive guide to building scalable distributed applications, training large models, processing multimodal data, serving inference workloads, and implementing reinforcement learning systems using [Ray](https://www.ray.io/).

## About This Repository

This repository serves as a hands-on learning resource for developers who want to master Ray for production-grade distributed computing. Whether you're building ML pipelines, training foundation models, or scaling data processing workloads, this guide will take you from fundamentals to advanced use cases.

## Who Is This For?

- Software engineers exploring distributed computing
- ML engineers building scalable training pipelines
- Data scientists working with large-scale datasets
- AI researchers implementing RL algorithms
- Anyone looking to leverage Ray for production workloads

## Learning Paths

### [01. Ray Fundamentals](./01-ray-fundamentals/)
Start here if you're new to Ray. Learn the core concepts, architecture, and building blocks.

**Topics covered:**
- Ray architecture and cluster management
- Tasks and remote functions
- Actors and stateful computation
- Object store and distributed memory
- Ray Core API patterns
- Debugging and monitoring

### [02. Distributed Training](./02-distributed-training/)
Master distributed training for deep learning models at scale - from PyTorch DDP to FSDP.

**🚀 Complete Learning Path:**
- **Vanilla PyTorch DDP** - See the pain points of manual distributed training
- **Ray Train DDP** - Eliminate 90% of boilerplate with 3 simple changes
- **Ray Train FSDP** - Scale to large models with 1 parameter change
- **Ray Train FSDP2** - Advanced configuration with CPU offload, mixed precision, and memory profiling
- Side-by-side comparison showing Ray's advantages

**Topics covered:**
- Data Parallel (DDP) vs Fully Sharded Data Parallel (FSDP)
- Ray Train integration with PyTorch (same model: VisionTransformer on CIFAR-10)
- Automatic resource management and fault tolerance
- Multi-node GPU training with shared storage
- When to use DDP vs FSDP for your models
- Advanced FSDP configuration (CPU offload, mixed precision, memory profiling)
- GPU utilization visualization with Ray Dashboard

### [03. Multimodal Data Processing](./03-multimodal-data-processing/)
Process large-scale multimodal datasets efficiently with Ray Data.

**🎬 Project: [Video Highlight Generator](./03-multimodal-data-processing/video-highlight-generator/)**

[![Video Highlight Generator Demo](https://img.youtube.com/vi/H2YptjwTEXc/maxresdefault.jpg)](https://www.youtube.com/watch?v=H2YptjwTEXc)

*Watch: AI-powered video highlight generation with Ray distributed processing (2 min demo)*

**Topics covered:**
- Ray Data fundamentals
- Processing text, images, video, and audio
- ETL pipelines for ML training
- Data preprocessing and augmentation
- Integration with training workflows
- Streaming and batch processing
- Data quality and validation

### [04. Inference](./04-inference/)
Deploy and serve ML models at scale with high throughput and low latency.

**Topics covered:**
- Ray Serve fundamentals
- Model deployment patterns
- Batching and autoscaling
- Multi-model serving
- LLM inference optimization
- A/B testing and model versioning
- Production monitoring

### [05. Reinforcement Learning](./05-reinforcement-learning/)
Build and train RL agents with Ray RLlib.

**Topics covered:**
- RLlib architecture and concepts
- Policy optimization algorithms (PPO, SAC, etc.)
- Multi-agent RL
- Custom environments and models
- Distributed RL training
- RLHF for LLM alignment
- Production deployment

## Repository Structure

```
ray-for-developers/
├── 01-ray-fundamentals/          # Core Ray concepts
├── 02-distributed-training/       # Training at scale
├── 03-multimodal-data-processing/ # Data pipelines
├── 04-inference/                  # Model serving
├── 05-reinforcement-learning/     # RL with Ray
├── examples/                      # End-to-end examples
└── assets/                        # Images and resources
```

## Getting Started

### Prerequisites

- Python 3.12
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Basic understanding of Python and machine learning concepts
- Familiarity with PyTorch (for training sections)
- GPU with CUDA support (optional, for accelerated training)

### Installation

First, install uv if you haven't already:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Create a virtual environment and install dependencies:

```bash
# Clone this repository
git clone https://github.com/debnsuma/ray-for-developers.git
cd ray-for-developers

# Create virtual environment with Python 3.12
uv venv --python 3.12

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install Ray with all components (CPU version)
uv pip install "ray[default,train,tune,serve,rllib,data]"

# Install PyTorch (CPU version)
uv pip install torch torchvision torchaudio

# For GPU support with CUDA 12.1
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Verify Installation

```bash
python -c "import ray; ray.init(); print(f'Ray version: {ray.__version__}')"
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Quick Start

1. Start with [Ray Fundamentals](./01-ray-fundamentals/) to learn the basics

2. Follow along with code examples and exercises in each section

3. Run the examples:
```bash
cd 01-ray-fundamentals
python examples/01_hello_ray.py
```

## Examples

Check out the [examples](./examples/) directory for complete end-to-end projects:

- Image classification with distributed training
- LLM fine-tuning pipeline
- Real-time video processing
- Multi-model serving system
- RL-based recommendation system

## Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and create pull requests.

## Resources

- [Ray Documentation](https://docs.ray.io/)
- [Ray Blog](https://www.anyscale.com/blog)
- [Ray Community](https://discuss.ray.io/)
- [Ray GitHub](https://github.com/ray-project/ray)
- [uv Documentation](https://docs.astral.sh/uv/)
