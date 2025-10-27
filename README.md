<div align="center">

# Ray for Developers

*A comprehensive hands-on guide to building production-grade distributed applications with Ray - from distributed training and multimodal data processing to inference and reinforcement learning.*

[![Ray Version](https://img.shields.io/badge/Ray-2.39.0-blue.svg)](https://docs.ray.io/)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.5.1-orange.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Topics:** `distributed-computing` `machine-learning` `deep-learning` `pytorch` `ray` `distributed-training` `ddp` `fsdp` `multimodal` `reinforcement-learning` `mlops` `data-processing` `model-serving`

</div>

---

## Table of Contents

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

This repository provides a **comprehensive hands-on guide** to building scalable distributed applications with Ray, a unified framework for scaling AI and Python applications. Whether you're training large language models, processing terabytes of data, or deploying ML models at scale, Ray simplifies distributed computing by abstracting away the complexity of cluster management and parallelization.

Through practical examples and production-ready code, you'll master distributed training techniques (from Data Parallel to Fully Sharded Data Parallel), learn to process multimodal datasets efficiently, deploy models for inference at scale, and implement reinforcement learning algorithms. Each module is designed to take you from fundamentals to advanced topics with real-world projects that you can adapt for your own use cases.

![](./imgs/ray_header_logo.png)

## Who Is This For?

- **Software engineers** exploring distributed computing and looking to scale Python applications
- **ML engineers** building scalable training pipelines and deploying models in production
- **Data scientists** working with large-scale datasets that don't fit on a single machine
- **AI researchers** implementing reinforcement learning algorithms and experimenting with distributed training
- **Anyone** looking to leverage Ray for production workloads at scale


## Learning Paths

### 01. Ray Fundamentals

**[→ Explore Ray Fundamentals](./01-ray-fundamentals/)**

Start here if you're new to Ray. This module introduces the core concepts, architecture, and building blocks of the Ray framework. You'll understand how Ray's distributed runtime works, learn to write distributed applications using tasks and actors, and explore the object store for efficient data sharing across processes.

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

**Complete Learning Path:**

This module takes you through a progressive journey from manual distributed training to automated, production-ready implementations:

- **Vanilla PyTorch DDP** - Experience firsthand the complexity and boilerplate required for manual distributed data parallel training with PyTorch's native implementation
- **Ray Train DDP** - Learn how Ray Train eliminates approximately 90% of boilerplate code while maintaining the same performance, requiring only 3 simple changes to your training code
- **Ray Train FSDP** - Discover memory-efficient training with Fully Sharded Data Parallel, which allows you to train models that don't fit on a single GPU by sharding model parameters, gradients, and optimizer states across multiple GPUs. Includes advanced configurations for CPU offloading, mixed precision training, and memory profiling

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

Learn to process large-scale multimodal datasets efficiently with Ray Data, which provides a scalable data processing layer for ML workloads. Ray Data handles petabyte-scale datasets by distributing I/O, transformation, and preprocessing operations across cluster nodes, making it ideal for training data preparation and inference preprocessing.

**Featured Project: [Video Highlight Generator](./03-multimodal-data-processing/video-highlight-generator/)**

An AI-powered system that automatically creates 30-second highlight reels from full-length videos using distributed video processing, feature extraction with deep learning models, and intelligent highlight detection algorithms.

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

Deploy and serve machine learning models at scale with Ray Serve, a scalable model serving library built on Ray. Learn to deploy models as microservices, handle high-throughput inference workloads, and implement production-grade serving patterns with features like dynamic batching, model composition, and autoscaling based on load.

**Topics covered:**
- Model deployment and serving patterns for production systems
- Batch inference optimization for processing large datasets efficiently
- Online serving with dynamic autoscaling based on request load
- Multi-model serving architectures for deploying multiple models simultaneously
- A/B testing and canary deployments for safe model rollouts
- Performance monitoring and observability for production inference systems

### [05. Reinforcement Learning](./05-reinforcement-learning/)

**[→ Coming Soon](./05-reinforcement-learning/)**

Build and train reinforcement learning agents with RLlib, Ray's scalable reinforcement learning library. RLlib provides production-grade implementations of popular RL algorithms and scales from single machines to large clusters, making it suitable for both research and production applications. Learn to train agents in custom environments, implement multi-agent systems, and apply RL techniques like RLHF to fine-tune large language models.

**Topics covered:**
- RLlib fundamentals and core concepts for distributed RL training
- Policy optimization algorithms including PPO (Proximal Policy Optimization), A3C (Asynchronous Advantage Actor-Critic), and SAC (Soft Actor-Critic)
- Custom environments and reward shaping techniques for specific problem domains
- Multi-agent reinforcement learning for scenarios with multiple interacting agents
- Distributed RL training across multiple machines to accelerate learning
- Reinforcement Learning from Human Feedback (RLHF) for fine-tuning language models

## Repository Structure

```
ray-for-developers/
├── 01-ray-fundamentals/          # Core Ray concepts
├── 02-distributed-training/       # Training at scale
├── 03-multimodal-data-processing/ # Data pipelines
├── 04-inference/                  # Model serving
├── 05-reinforcement-learning/     # RL with Ray
└── imgs/                        # Images and resources
```

## Getting Started

### Prerequisites

- **Python 3.12** - Required for compatibility with Ray 2.39.0 and PyTorch 2.5.1
- **uv Package Manager** - [uv](https://github.com/astral-sh/uv) is a fast Python package installer that significantly speeds up dependency installation
- **Python Programming** - Basic understanding of Python programming and familiarity with machine learning concepts
- **PyTorch Knowledge** - Familiarity with PyTorch framework is recommended for the distributed training modules
- **GPU Hardware** - NVIDIA GPU with CUDA support is optional but recommended for accelerated training and realistic performance benchmarks

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

The [examples](./examples/) directory contains complete end-to-end projects demonstrating real-world applications:

- **Image Classification with Distributed Training** - Train computer vision models across multiple GPUs using Ray Train with automatic data parallelism
- **LLM Fine-tuning Pipeline** - End-to-end pipeline for fine-tuning large language models with distributed training and checkpointing
- **Real-time Video Processing** - Process video streams in real-time using Ray's distributed computing capabilities
- **Multi-model Serving System** - Deploy and serve multiple ML models simultaneously with load balancing and autoscaling
- **RL-based Recommendation System** - Build a recommendation system using reinforcement learning with Ray RLlib

## Contributing

Contributions are welcome and greatly appreciated! Here's how you can help improve this project:

- **Report Bugs and Issues** - If you encounter any problems or unexpected behavior, please open an issue with detailed reproduction steps
- **Suggest Features** - Have ideas for new features or improvements? Share them through GitHub issues
- **Improve Documentation** - Help make the documentation clearer, fix typos, or add examples that helped you understand concepts
- **Submit Pull Requests** - Contribute code improvements, bug fixes, or new examples

Please feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## Resources

**Official Ray Resources:**
- [Ray Documentation](https://docs.ray.io/) - Comprehensive official documentation for all Ray components
- [Ray Blog](https://www.anyscale.com/blog) - Technical articles, case studies, and updates from the Ray team
- [Ray Community Forum](https://discuss.ray.io/) - Ask questions and engage with the Ray community
- [Ray GitHub Repository](https://github.com/ray-project/ray) - Source code, issue tracking, and contributions

**Additional Tools:**
- [uv Documentation](https://docs.astral.sh/uv/) - Fast Python package installer used in this repository

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
