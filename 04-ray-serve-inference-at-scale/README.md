# 04. Inference at Scale with Ray Serve

Deploy and serve ML models at scale with high throughput, low latency, and production-grade reliability.

## Overview

This module covers deploying and serving machine learning models in production using Ray Serve. Ray Serve is a scalable model serving library built on Ray that supports complex inference pipelines, dynamic batching, model composition, and autoscaling.

## Directory Structure

```
04-ray-serve-inference-at-scale/
├── notebooks/                              # Core learning notebooks
│   ├── 01_Intro_Serve.ipynb                # Introduction to Ray Serve
│   ├── 02_Architecture.ipynb               # Ray Serve architecture
│   ├── 03_Designing_Serve_Applications.ipynb  # Designing applications
│   ├── 04_Observability.ipynb              # Monitoring and observability
│   ├── 05_Autoscaling.ipynb                # Autoscaling patterns
│   ├── 06_Performance_Optimization.ipynb   # Performance optimization
│   └── Intro_Serve.ipynb                   # Ray Serve introduction
├── examples/                               # Production examples
│   ├── intro/                              # Basic introduction
│   │   └── main.py
│   ├── app_builder/                        # Application builder pattern
│   │   └── main.py
│   ├── autoscaling/                        # Autoscaling examples
│   │   ├── locustfile.py                   # Load testing
│   │   ├── resnet50_model.py               # Model serving
│   │   └── scripts/
│   │       └── visualize_metrics.py
│   ├── debugging/                          # Debugging examples
│   │   └── debug.py
│   ├── distributed_tracing/                # Distributed tracing
│   ├── online_stream_processing/           # Stream processing
│   │   ├── sqs.py                          # SQS integration
│   │   └── guide.ipynb
│   └── tests/                              # Test suite
│       ├── conftest.py
│       ├── example_app.py
│       ├── example_composition.py
│       ├── test_basic_unit.py
│       ├── test_composition.py
│       ├── test_integration_handle.py
│       └── test_integration_http.py
└── README.md
```

## Learning Path

### 1. Introduction to Ray Serve
**Notebook:** `notebooks/01_Intro_Serve.ipynb`

Get started with Ray Serve:
- Ray Serve basics and concepts
- Creating deployments with `@serve.deployment`
- HTTP endpoints and request handling
- Deploying your first model

### 2. Ray Serve Architecture
**Notebook:** `notebooks/02_Architecture.ipynb`

Understand the architecture:
- Serve Controller and Replica architecture
- Request routing and load balancing
- Deployment lifecycle
- Resource management

### 3. Designing Serve Applications
**Notebook:** `notebooks/03_Designing_Serve_Applications.ipynb`

Build production applications:
- Model composition patterns
- Request/response handling
- Streaming responses
- Multi-model pipelines

### 4. Observability
**Notebook:** `notebooks/04_Observability.ipynb`

Monitor your deployments:
- Metrics and logging
- Ray Dashboard integration
- Prometheus/Grafana setup
- Debugging techniques

### 5. Autoscaling
**Notebook:** `notebooks/05_Autoscaling.ipynb`

Scale automatically:
- Autoscaling configuration
- Min/max replicas
- Target metrics
- Load testing with Locust

### 6. Performance Optimization
**Notebook:** `notebooks/06_Performance_Optimization.ipynb`

Optimize for production:
- Batching strategies
- Concurrent requests
- GPU utilization
- Latency optimization

## Key Concepts

### Basic Deployment
```python
from ray import serve

@serve.deployment
class MyModel:
    def __init__(self):
        self.model = load_model()

    def __call__(self, request):
        data = request.json()
        return self.model.predict(data)

app = MyModel.bind()
serve.run(app)
```

### Model Composition
```python
@serve.deployment
class Preprocessor:
    def __call__(self, data):
        return preprocess(data)

@serve.deployment
class Model:
    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.model = load_model()

    async def __call__(self, request):
        data = await self.preprocessor.remote(request.json())
        return self.model.predict(data)

preprocessor = Preprocessor.bind()
model = Model.bind(preprocessor)
serve.run(model)
```

### Autoscaling Configuration
```python
@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 10,
        "target_num_ongoing_requests_per_replica": 5,
    }
)
class ScalableModel:
    ...
```

### Dynamic Batching
```python
@serve.deployment
class BatchingModel:
    @serve.batch(max_batch_size=32, batch_wait_timeout_s=0.1)
    async def predict(self, requests):
        inputs = [r.json() for r in requests]
        return self.model.predict_batch(inputs)
```

## Production Examples

The `examples/` directory contains production-ready patterns:

| Example | Description |
|---------|-------------|
| `intro/` | Basic Ray Serve introduction |
| `app_builder/` | Application builder pattern |
| `autoscaling/` | Autoscaling with load testing |
| `debugging/` | Debugging techniques |
| `distributed_tracing/` | Distributed tracing setup |
| `online_stream_processing/` | SQS stream processing |
| `tests/` | Comprehensive test suite |

## Prerequisites

- Python 3.12+ installed
- Ray (latest version) installed via uv (see main README)
- Understanding of Ray fundamentals
- Familiarity with ML model deployment concepts

## Getting Started

```bash
# Navigate to this directory
cd 04-ray-serve-inference-at-scale

# Start Jupyter for notebooks
jupyter notebook

# Or run examples directly
cd examples/intro
python main.py
```

Start with `notebooks/01_Intro_Serve.ipynb` and progress through the notebooks.

## Resources

- [Ray Serve Documentation](https://docs.ray.io/en/latest/serve/index.html)
- [Ray Serve Tutorials](https://docs.ray.io/en/latest/serve/tutorials/index.html)
- [Ray Serve API Reference](https://docs.ray.io/en/latest/serve/api/index.html)
- [Production Guide](https://docs.ray.io/en/latest/serve/production-guide/index.html)
