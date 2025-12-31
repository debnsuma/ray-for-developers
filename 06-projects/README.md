# 06. Projects

Complete end-to-end projects demonstrating Ray's capabilities across different domains. These projects combine multiple Ray libraries and concepts to build production-ready applications.

## Directory Structure

```
06-projects/
├── end-to-end-llms/                    # LLM fine-tuning and deployment
│   ├── 01_Finetuning_LLMs.ipynb        # Fine-tuning LLMs with Ray
│   ├── 02_Preparing_Data.ipynb         # Data preparation for LLMs
│   ├── 03_Evaluating_LLMs.ipynb        # Evaluating LLM performance
│   ├── 04_Deploying_LLMs.ipynb         # Deploying LLMs with Ray Serve
│   └── bonus/
│       └── MLOps_and_LLMs.ipynb        # MLOps practices for LLMs
├── rag/                                # Retrieval-Augmented Generation
│   ├── 01_Intro_to_RAG.ipynb           # Introduction to RAG
│   ├── 02_Index_Data.ipynb             # Indexing data for retrieval
│   ├── 03_Build_RAG.ipynb              # Building RAG pipelines
│   ├── 04_Deploy_RAG.ipynb             # Deploying RAG applications
│   └── bonus/
│       └── Deploy_LLM.ipynb            # Deploying LLMs
├── ray-tune/                           # Hyperparameter tuning
│   ├── Intro_Tune.ipynb                # Introduction to Ray Tune
│   └── Tune_Train.ipynb                # Integrating Tune with Train
├── video-highlight-generator/          # AI-powered video processing
│   └── README.md                       # Full project documentation
└── README.md
```

## Projects Overview

### 1. End-to-End LLMs
**Folder:** `end-to-end-llms/`

A complete workflow for working with Large Language Models using Ray:

| Notebook | Description |
|----------|-------------|
| `01_Finetuning_LLMs.ipynb` | Fine-tune LLMs using Ray Train for distributed training |
| `02_Preparing_Data.ipynb` | Prepare and preprocess data with Ray Data |
| `03_Evaluating_LLMs.ipynb` | Evaluate LLM performance at scale |
| `04_Deploying_LLMs.ipynb` | Deploy LLMs with Ray Serve |
| `bonus/MLOps_and_LLMs.ipynb` | MLOps best practices for LLM workflows |

**Topics covered:**
- Distributed fine-tuning with Ray Train
- Data preprocessing with Ray Data
- Model evaluation and benchmarking
- Production deployment with Ray Serve
- MLOps practices and monitoring

### 2. RAG (Retrieval-Augmented Generation)
**Folder:** `rag/`

Build and deploy RAG applications that combine retrieval systems with LLMs:

| Notebook | Description |
|----------|-------------|
| `01_Intro_to_RAG.ipynb` | Introduction to RAG architecture |
| `02_Index_Data.ipynb` | Build vector indices with Ray Data |
| `03_Build_RAG.ipynb` | Create RAG pipelines |
| `04_Deploy_RAG.ipynb` | Deploy RAG with Ray Serve |
| `bonus/Deploy_LLM.ipynb` | Deploy the underlying LLM |

**Topics covered:**
- RAG architecture and components
- Document chunking and embedding
- Vector database integration
- Query processing and retrieval
- End-to-end RAG deployment

### 3. Ray Tune - Hyperparameter Tuning
**Folder:** `ray-tune/`

Learn to optimize model hyperparameters with Ray Tune:

| Notebook | Description |
|----------|-------------|
| `Intro_Tune.ipynb` | Introduction to Ray Tune |
| `Tune_Train.ipynb` | Integrating Tune with Ray Train |

**Topics covered:**
- Hyperparameter search algorithms
- Search space definitions
- Early stopping strategies
- Integration with Ray Train
- Experiment tracking

### 4. Video Highlight Generator
**Folder:** `video-highlight-generator/`

An AI-powered system that automatically creates highlight reels from videos:

**Key Features:**
- Ray Actors for distributed ML inference
- MobileNetV3 for feature extraction
- Multi-signal highlight detection
- YouTube video support
- Cluster compatibility

**[→ Full Documentation](./video-highlight-generator/README.md)**

## Prerequisites

- Python 3.12+ installed
- Ray (latest version) installed via uv (see main README)
- Understanding of Ray Core, Train, Data, and Serve concepts
- Project-specific dependencies (see individual READMEs)

## Getting Started

Each project can be run independently:

```bash
# End-to-End LLMs
cd 06-projects/end-to-end-llms
jupyter notebook

# RAG Project
cd 06-projects/rag
jupyter notebook

# Ray Tune
cd 06-projects/ray-tune
jupyter notebook

# Video Highlight Generator
cd 06-projects/video-highlight-generator
pip install -r requirements.txt
python demo.py
```

## Resources

- [Ray Documentation](https://docs.ray.io/)
- [Ray Train Guide](https://docs.ray.io/en/latest/train/train.html)
- [Ray Tune Guide](https://docs.ray.io/en/latest/tune/index.html)
- [Ray Serve Guide](https://docs.ray.io/en/latest/serve/index.html)
- [Ray Data Guide](https://docs.ray.io/en/latest/data/data.html)
