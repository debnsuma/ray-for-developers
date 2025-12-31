# 01. Ray Core - Distributed Computing Fundamentals

Welcome to Ray Core! This section covers the core concepts and building blocks of Ray for distributed computing. If you're new to Ray, start here to build a solid foundation.

## What is Ray Core?

Ray Core is the foundation of the Ray framework, providing simple primitives for building and running distributed applications:
- **Tasks** - Stateless functions executed remotely
- **Actors** - Stateful classes running in the cluster
- **Objects** - Immutable values stored in Ray's distributed object store

## Directory Structure

```
01-ray-core-distributed-computing/
├── notebooks/                    # Main learning notebooks
│   ├── Ray_Core_1_Remote_Functions.ipynb    # Remote tasks and parallel execution
│   ├── Ray_Core_2_Remote_Objects.ipynb      # Distributed object store
│   ├── Ray_Core_3_Remote_Classes_part_1.ipynb   # Actors introduction
│   ├── Ray_Core_4_Remote_Classes_part_2.ipynb   # Advanced actor patterns
│   ├── Ray_Core_5_Best_Practices.ipynb      # Best practices and patterns
│   └── Ray_Core_6_Compiled_Graphs_experimental.ipynb  # Experimental features
├── bonus/                        # Additional examples
│   ├── 1_core_examples.ipynb     # Extra Ray Core examples
│   └── 2_task_lifecycle_deep_dive.ipynb  # Deep dive into task lifecycle
├── solutions/                    # Exercise solutions
│   ├── ex_01_solution.ipynb
│   ├── ex_02_solution.ipynb
│   ├── ex_03_solution.ipynb
│   └── ex_04_solution.ipynb
├── utils/                        # Helper utilities
│   ├── model_helper_utils.py
│   └── tasks_helper_utils.py
└── README.md
```

## Learning Path

### 1. Remote Functions (Tasks)
**Notebook:** `Ray_Core_1_Remote_Functions.ipynb`

Learn the fundamentals of Ray tasks:
- Converting Python functions to distributed tasks with `@ray.remote`
- Parallel execution patterns (Monte Carlo, Fibonacci)
- Task dependencies and DAG patterns
- Resource management and scheduling

### 2. Remote Objects
**Notebook:** `Ray_Core_2_Remote_Objects.ipynb`

Understand Ray's distributed object store:
- `ray.put()` for storing objects
- `ray.get()` for retrieving objects
- Object references and futures
- Efficient data sharing across tasks

### 3. Remote Classes (Actors) - Part 1
**Notebook:** `Ray_Core_3_Remote_Classes_part_1.ipynb`

Introduction to stateful computation with actors:
- Creating actors with `@ray.remote`
- Actor methods and state management
- Actor handles and references

### 4. Remote Classes (Actors) - Part 2
**Notebook:** `Ray_Core_4_Remote_Classes_part_2.ipynb`

Advanced actor patterns:
- Actor pools and load balancing
- Async actors
- Actor lifecycle management
- Fault tolerance with actors

### 5. Best Practices
**Notebook:** `Ray_Core_5_Best_Practices.ipynb`

Production-ready patterns:
- Anti-patterns to avoid
- Memory management
- Performance optimization
- Debugging techniques

### 6. Compiled Graphs (Experimental)
**Notebook:** `Ray_Core_6_Compiled_Graphs_experimental.ipynb`

Explore experimental features for optimized execution graphs.

## Prerequisites

- Python 3.12+ installed
- Ray (latest version) installed via uv (see main README)
- Basic Python knowledge (functions, classes, decorators)

## Getting Started

```bash
# Navigate to this directory
cd 01-ray-core-distributed-computing

# Start Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

Start with `notebooks/Ray_Core_1_Remote_Functions.ipynb` and progress through the numbered notebooks.

## Resources

- [Ray Core Documentation](https://docs.ray.io/en/latest/ray-core/walkthrough.html)
- [Ray Core Examples](https://docs.ray.io/en/latest/ray-core/examples/overview.html)
- [Ray Patterns](https://docs.ray.io/en/latest/ray-core/patterns/index.html)
- [Ray API Reference](https://docs.ray.io/en/latest/ray-core/api/index.html)
