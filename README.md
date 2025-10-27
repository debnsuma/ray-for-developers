# Ray for Developers

> A comprehensive hands-on guide to building production-grade distributed applications with Ray - from distributed training and multimodal data processing to inference and reinforcement learning.

[![Ray Version](https://img.shields.io/badge/Ray-2.39.0-blue.svg)](https://docs.ray.io/)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.5.1-orange.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Topics:** `distributed-computing` `machine-learning` `deep-learning` `pytorch` `ray` `distributed-training` `ddp` `fsdp` `multimodal` `reinforcement-learning` `mlops` `data-processing` `model-serving`

---

![](./imgs/ray_header_logo.png)

## 📚 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Learning Paths](#learning-paths)
  - [01. Ray Fundamentals](#01-ray-fundamentals)
  - [02. Distributed Training](#02-distributed-training)
  - [03. Multimodal Data Processing](#03-multimodal-data-processing)
  - [04. Inference](#04-inference)
  - [05. Reinforcement Learning](#05-reinforcement-learning)
- [Quick Start](#quick-start)
- [Examples](#examples)
- [Contributing](#contributing)
- [Resources](#resources)

---

## Overview

This repository is your **comprehensive hands-on guide** to building scalable distributed applications with Ray. Master everything from distributed training and multimodal data processing to model serving at scale and reinforcement learning - all with code examples.

## Who Is This For?

- **Software engineers** exploring distributed computing
- **ML engineers** building scalable training pipelines
- **Data scientists** working with large-scale datasets
- **AI researchers** implementing RL algorithms
- **Anyone** looking to leverage Ray for production workloads at scale

---

## Learning Paths

### 01. Ray Fundamentals

**[→ Explore Ray Fundamentals](./01-ray-fundamentals/)**

Start here if you're new to Ray. Learn the core concepts, architecture, and building blocks.

**Topics covered:**
- Ray architecture and cluster management
- Tasks and remote functions
- Actors and stateful computation
- Object store and distributed memory
- Ray Core API patterns
- Debugging and monitoring

### [02. Distributed Training](./02-distributed-training/)

**[→ Explore Distributed Training](./02-distributed-training/)**

Master distributed training for deep learning models at scale - from PyTorch DDP to FSDP.

**🚀 Complete Learning Path:**
- **Vanilla PyTorch DDP** - See the pain points of manual distributed training
- **Ray Train DDP** - Eliminate 90% of boilerplate with 3 simple changes
- **Ray Train FSDP**
    - Scale to large models with 1 parameter change
    - Advanced configuration with CPU offload, mixed precision, and memory profiling

**[View Slides: Distributed Training with Ray](https://www.canva.com/design/DAG2W25BKAw/yXl48lXeg0g60Rf_1RUXrw/view)**
*Deck covering distributed training concepts, architecture, and best practices*

![Ray Train Ecosystem](./02-distributed-training/imgs/Ray_Train.png)
*Ray Train integrates seamlessly with popular frameworks and runs on any infrastructure*

**Topics covered:**
- Data Parallel (DDP) vs Fully Sharded Data Parallel (FSDP)
- Ray Train integration with PyTorch 
- Automatic resource management and fault tolerance
- Multi-node GPU training with shared storage
- When to use DDP vs FSDP for your models
- Advanced FSDP configuration (CPU offload, mixed precision, memory profiling)
- GPU utilization visualization with Ray Dashboard

### [03. Multimodal Data Processing](./03-multimodal-data-processing/)

**[→ Explore Multimodal Data Processing](./03-multimodal-data-processing/)**

Process large-scale multimodal datasets efficiently with Ray Data.

**🎬 Project: [Video Highlight Generator](./03-multimodal-data-processing/video-highlight-generator/)**

[![Video Highlight Generator Demo](https://img.youtube.com/vi/H2YptjwTEXc/maxresdefault.jpg)](https://www.youtube.com/watch?v=H2YptjwTEXc)

*Watch: AI-powered video highlight generation with Ray distributed processing (2 min demo) showcased at PyTorch Conf 2025*

**Topics covered:**
- Ray Data fundamentals
- Processing text, images, video, and audio
- ETL pipelines for ML training
- Data preprocessing and augmentation
- Integration with training workflows
- Streaming and batch processing
- Data quality and validation

### [04. Inference](./04-inference/)

**[→ Coming Soon](./04-inference/)**

Deploy and serve models at scale with Ray Serve.

**Topics covered:**
- Model deployment and serving patterns
- Batch inference optimization
- Online serving with autoscaling
- Multi-model serving
- A/B testing and canary deployments
- Performance monitoring

### [05. Reinforcement Learning](./05-reinforcement-learning/)

**[→ Coming Soon](./05-reinforcement-learning/)**

Build and train reinforcement learning agents with RLlib.

**Topics covered:**
- RLlib fundamentals
- Policy optimization algorithms (PPO, A3C, SAC)
- Custom environments and reward shaping
- Multi-agent reinforcement learning
- Distributed RL training
- RLHF for language models

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

- 🐍 Python 3.12
- ⚡ [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- 📚 Basic understanding of Python and machine learning concepts
- 🔥 Familiarity with PyTorch (for training sections)
- 🎮 GPU with CUDA support (optional, for accelerated training)

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

- 📸 Image classification with distributed training
- 🤖 LLM fine-tuning pipeline
- 🎥 Real-time video processing
- 🚀 Multi-model serving system
- 🎯 RL-based recommendation system

## Contributing

Contributions are welcome! Here's how you can help:

- 🐛 Report bugs and issues
- 💡 Suggest new features or improvements
- 📝 Improve documentation
- 🔧 Submit pull requests

Please feel free to submit issues, fork the repository, and create pull requests.

## Resources

- 📖 [Ray Documentation](https://docs.ray.io/)
- 📝 [Ray Blog](https://www.anyscale.com/blog)
- 💬 [Ray Community](https://discuss.ray.io/)
- 🐙 [Ray GitHub](https://github.com/ray-project/ray)
- ⚡ [uv Documentation](https://docs.astral.sh/uv/)

---

## Support

If you find this repository helpful, please consider giving it a ⭐ on GitHub! It helps others discover this resource.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Ray](https://ray.io/) - the open-source framework for scaling AI and Python applications
- Inspired by the Ray community and the need for practical, hands-on learning resources
- Special thanks to all contributors and the open-source community

---

<div align="center">

**[⬆ Back to Top](#ray-for-developers)**

Made with ❤️ by [Suman Debnath](https://github.com/debnsuma)

</div>
