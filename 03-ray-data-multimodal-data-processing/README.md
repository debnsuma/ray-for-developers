# 03. Multimodal Data Processing with Ray Data

Build scalable pipelines for processing video, images, text, and multimodal datasets using Ray Data's distributed computing framework.

## Overview

This module teaches you how to use Ray Data for scalable data processing pipelines. Ray Data provides a unified API for loading, transforming, and processing large-scale datasets that can scale from a single machine to multi-node Ray clusters.

## Directory Structure

```
03-ray-data-multimodal-data-processing/
├── notebooks/                          # Core learning notebooks
│   ├── 01_Welcome.ipynb                # Welcome and setup guide
│   ├── 02_AI_Libs_Intro.ipynb          # AI Libraries overview
│   ├── 03_Intro_Data.ipynb             # Introduction to Ray Data
│   ├── 03a_Sol_Data.ipynb              # Ray Data exercises solution
│   ├── 05_Ray_Data_AI.ipynb            # Ray Data for AI workloads
│   ├── 05a_Sol_Ray_Data_AI.ipynb       # Ray Data AI exercises solution
│   ├── Intro_Data.ipynb                # Ray Data introduction
│   ├── VHOL.ipynb                      # Virtual Hands-On Lab
│   └── VHOL_without_output.ipynb       # VHOL without output
├── batch-inference-optimization/       # Batch inference patterns
│   ├── 01-inference-fundamentals.ipynb # Inference fundamentals
│   ├── 02-ray-data-architecture.ipynb  # Ray Data architecture
│   ├── 03-advanced-optimization.ipynb  # Advanced optimization
│   └── README.ipynb                    # Overview
├── multimodal-search/                  # Multimodal search pipeline
│   ├── 1_setup_tools.ipynb             # Setup tools
│   ├── 2_intro_data.ipynb              # Introduction to data
│   ├── 2a_sol_data.ipynb               # Data exercises solution
│   ├── 3_process_data.ipynb            # Data processing
│   ├── A_simple_query.ipynb            # Simple query example
│   └── B_process_1000_data.ipynb       # Processing large datasets
├── etl-optimization/                   # ETL optimization patterns
├── unstructured-data-ingestion/        # Unstructured data ingestion
├── utils/                              # Helper utilities
│   ├── sequential_process.py           # Sequential processing
│   ├── parallel_process.py             # Parallel processing
│   ├── ray_actor.py                    # Ray Actor example
│   └── counter.py                      # Counter actor
└── README.md
```

## Learning Path

### 1. Introduction to Ray Data
**Notebooks:** `notebooks/01_Welcome.ipynb`, `notebooks/03_Intro_Data.ipynb`

Learn the fundamentals of Ray Data:
- Ray Data basics and API
- Creating and manipulating datasets
- Data transformations with `map`, `filter`, `flat_map`
- Reading from various sources (Parquet, CSV, JSON, images)

### 2. Ray Data for AI Workloads
**Notebooks:** `notebooks/05_Ray_Data_AI.ipynb`, `notebooks/VHOL.ipynb`

Apply Ray Data to ML workloads:
- Preprocessing for training pipelines
- Feature engineering at scale
- Integration with Ray Train
- Batch inference patterns

### 3. Batch Inference Optimization
**Folder:** `batch-inference-optimization/`

Deep dive into batch inference:
- Inference fundamentals and patterns
- Ray Data architecture for inference
- Advanced optimization techniques
- GPU utilization and throughput

### 4. Multimodal Search Pipeline
**Folder:** `multimodal-search/`

Build a complete multimodal search system:
- Setup and tools configuration
- Processing text, images, and embeddings
- Building search indices
- Querying multimodal data

## Key Concepts

### Ray Data Features
- **Lazy Execution** - Operations are lazily evaluated for optimization
- **Streaming** - Process data larger than memory with streaming
- **Parallelism** - Automatic parallelization across cluster
- **Integration** - Works seamlessly with Ray Train and Ray Serve

### Common Operations
```python
import ray

# Read data
ds = ray.data.read_parquet("s3://bucket/data/")

# Transform data
ds = ds.map(lambda x: {"processed": transform(x["raw"])})

# Filter data
ds = ds.filter(lambda x: x["score"] > 0.5)

# Batch operations
ds = ds.map_batches(model.predict, batch_size=32)

# Write data
ds.write_parquet("s3://bucket/output/")
```

### Batch Inference Pattern
```python
class Predictor:
    def __init__(self):
        self.model = load_model()

    def __call__(self, batch):
        return {"predictions": self.model(batch["inputs"])}

ds = ray.data.read_images("images/")
ds = ds.map_batches(Predictor, concurrency=4, batch_size=32)
```

## Related Projects

For a complete video processing project using Ray, see:
- **[Video Highlight Generator](../06-projects/video-highlight-generator/)** - AI-powered video highlight generation using Ray for distributed processing

## Prerequisites

- Python 3.12+ installed
- Ray (latest version) installed via uv (see main README)
- Basic Python knowledge
- Understanding of Ray Core concepts helps

## Getting Started

```bash
# Navigate to this directory
cd 03-ray-data-multimodal-data-processing

# Start Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

Start with `notebooks/01_Welcome.ipynb` and progress through the notebooks.

## Resources

- [Ray Data Documentation](https://docs.ray.io/en/latest/data/data.html)
- [Ray Data API Reference](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.html)
- [Ray Data Examples](https://docs.ray.io/en/latest/data/examples.html)
- [Batch Inference Guide](https://docs.ray.io/en/latest/data/batch_inference.html)
