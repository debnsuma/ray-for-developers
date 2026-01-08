# Distributed Python for AI: A Complete Guide to Ray

[![Ray](https://img.shields.io/badge/Ray-2.x-blue?logo=ray)](https://ray.io)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6-ee4c2c?logo=pytorch)](https://pytorch.org)
[![DeepSpeed](https://img.shields.io/badge/DeepSpeed-Enabled-green)](https://www.deepspeed.ai/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

> A comprehensive hands-on course to master distributed computing, scalable data pipelines, and AI training at scale.

---

Modern AI workloads demand more than a single machine can offer. In this comprehensive hands-on course, you'll learn Ray-the open-source framework powering AI infrastructure at companies like OpenAI, Uber, and Spotify.

Starting from core distributed computing concepts, you'll progress through building scalable data pipelines that handle multimodal data-images, text, and structured datasets-with ease. You'll master distributed training using **PyTorch's Distributed Data Parallel (DDP)** and **Fully Sharded Data Parallel (FSDP)**, learning to train models across multiple GPUs with automatic fault tolerance and checkpointing.

The course culminates in fine-tuning large language models using **DeepSpeed** and **LoRA**, showing you how production teams efficiently customize billion-parameter models. Whether you're processing terabytes of unstructured data, training computer vision models, or fine-tuning LLMs for your use case-Ray provides a unified, Pythonic approach to scaling it all.

By the end, you'll have the skills to transform any Python application into a distributed, production-ready system.

---

## What You'll Learn

| Skill | Real-World Application |
|-------|------------------------|
| Ray Core (Tasks & Actors) | Build resilient, scalable microservices |
| Ray Data Pipelines | Process TB-scale multimodal datasets |
| Distributed Training (DDP/FSDP) | Train models 10x faster across GPUs |
| DeepSpeed + LoRA | Fine-tune LLMs memory-efficiently |
| Fault Tolerance | Build production-grade AI systems |

---

## Course Curriculum

### Module 1: Ray Core Fundamentals
| Notebook | Topics | Duration |
|----------|--------|----------|
| [01 - Introduction to Ray](01_Ray_Core_intro.ipynb) | What is Ray, Tasks, Actors, First distributed app | ~15 min |

### Module 2: Ray Core Deep Dive
| Notebook | Topics | Duration |
|----------|--------|----------|
| [02 - Ray Core Details Part 1](02_Ray_Core_details_part1.ipynb) | Remote functions, Object Store, Memory model, Task chaining, Retries, Resource allocation | ~45 min |
| [03 - Ray Core Details Part 2](03_Ray_Core_details_part2.ipynb) | Advanced Actors, Fault tolerance, Async actors, Concurrency groups, ActorPool | ~50 min |

### Module 3: Ray Data for Scalable Pipelines
| Notebook | Topics | Duration |
|----------|--------|----------|
| [04 - Introduction to Ray Data](04_Ray_Data_intro.ipynb) | Data loading, Lazy evaluation, Transformations, Stateful transforms | ~40 min |
| [05 - More on Ray Data](05_Ray_Data_part1.ipynb) | Streaming execution, Image pipelines, Data joins, LLM integration | ~90 min |

### Module 4: Distributed Training with Ray Train
| Notebook | Topics | Duration |
|----------|--------|----------|
| [06 - Ray Train Introduction](06_Ray_Train_Intro_part1.ipynb) | Single GPU to distributed, PyTorch DDP, Checkpointing, Fault tolerance | ~60 min |
| [07 - FSDP with Ray Train](07_Ray_Train_Intro_part2.ipynb) | Fully Sharded Data Parallel, Memory efficiency, Large model training | ~40 min |

### Module 5: Fine-Tuning LLMs
| Notebook | Topics | Duration |
|----------|--------|----------|
| [08 - Fine-tune LLMs with Ray Train](08_Finetune_LLMs_with_Ray_Train.ipynb) | Dataset preparation, DeepSpeed, LoRA, GSM8K math fine-tuning | ~50 min |

**Total Duration: ~6+ hours of hands-on content**

---

## Prerequisites

- **Python**: Intermediate level (comfortable with classes, decorators, async)
- **Machine Learning**: Basic understanding of training loops and neural networks
- **PyTorch**: Familiarity helpful but not required (we cover the basics)
- **Hardware**: GPU recommended for training modules, CPU sufficient for Ray Core/Data

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ray-for-developers.git
cd ray-for-developers
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -U pip
pip install ray[all]
pip install -r requirements.txt
```

### 4. Launch Jupyter

```bash
jupyter notebook
```

Start with `01_Ray_Core_intro.ipynb` and follow the module sequence.

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| [Ray](https://ray.io) | Distributed computing framework |
| [PyTorch](https://pytorch.org) | Deep learning framework |
| [DeepSpeed](https://www.deepspeed.ai/) | Memory-efficient training |
| [Transformers](https://huggingface.co/transformers) | LLM models and tokenizers |
| [Accelerate](https://huggingface.co/docs/accelerate) | Training utilities |
| [Diffusers](https://huggingface.co/docs/diffusers) | Image generation models |

---

## Project Structure

```
.
├── 01_Ray_Core_intro.ipynb          # Module 1: Ray fundamentals
├── 02_Ray_Core_details_part1.ipynb  # Module 2: Tasks deep dive
├── 03_Ray_Core_details_part2.ipynb  # Module 2: Actors deep dive
├── 04_Ray_Data_intro.ipynb          # Module 3: Ray Data basics
├── 05_Ray_Data_part1.ipynb          # Module 3: Advanced pipelines
├── 06_Ray_Train_Intro_part1.ipynb   # Module 4: Distributed training
├── 07_Ray_Train_Intro_part2.ipynb   # Module 4: FSDP
├── 08_Finetune_LLMs_with_Ray_Train.ipynb  # Module 5: LLM fine-tuning
├── code/
│   └── *.py                         # Supporting code examples
├── requirements.txt
└── README.md
```

---

## Who Is This For?

- **Python Developers** wanting to scale their applications beyond a single machine
- **Data Engineers** building production-grade data pipelines
- **ML Engineers** training large models across distributed infrastructure
- **AI Practitioners** looking to fine-tune LLMs efficiently
- **Anyone** curious about distributed systems without the complexity

---

## Resources

- [Ray Documentation](https://docs.ray.io)
- [Ray GitHub](https://github.com/ray-project/ray)
- [PyTorch Distributed](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html)
- [DeepSpeed Documentation](https://www.deepspeed.ai/docs/)
- [Anyscale Blog](https://www.anyscale.com/blog)


<p align="center">
  <b>Ready to scale your Python?</b><br>
  Start with <a href="01_Ray_Core_intro.ipynb">Module 1</a> and begin your distributed computing journey.
</p>
