"""
Utility functions for Ray initialization
Handles both local (Mac) and cluster environments
"""
import os
import ray


def safe_ray_init(num_cpus=None, num_gpus=None, **kwargs):
    """
    Safely initialize Ray for both local and cluster environments

    Automatically detects cluster mode and avoids resource parameters.
    Cluster mode is detected through:
    - RAY_ADDRESS environment variable
    - ray.init() attempting to connect to existing cluster

    Args:
        num_cpus: Number of CPUs (only used for local mode)
        num_gpus: Number of GPUs (only used for local mode)
        **kwargs: Additional arguments to pass to ray.init()

    Returns:
        ray.init() result
    """
    # Check if already initialized
    if ray.is_initialized():
        print("Ray is already initialized")
        return

    # Check if connecting to existing cluster via environment variable
    ray_address = os.environ.get('RAY_ADDRESS')

    # Prepare init arguments
    init_kwargs = {'ignore_reinit_error': True}
    init_kwargs.update(kwargs)

    if ray_address:
        # Explicit cluster mode via RAY_ADDRESS
        print(f"Connecting to Ray cluster at {ray_address}")
        # Remove resource parameters
        init_kwargs.pop('num_cpus', None)
        init_kwargs.pop('num_gpus', None)
        return ray.init(**init_kwargs)

    # Try to initialize with resources first (local mode)
    if num_cpus is not None:
        init_kwargs['num_cpus'] = num_cpus
    if num_gpus is not None:
        init_kwargs['num_gpus'] = num_gpus

    try:
        print("Starting local Ray instance")
        return ray.init(**init_kwargs)
    except ValueError as e:
        if "When connecting to an existing cluster" in str(e):
            # Detected cluster connection, retry without resource parameters
            print("Detected existing Ray cluster, connecting without resource parameters")
            # Rebuild init_kwargs without resource parameters
            cluster_init_kwargs = {k: v for k, v in kwargs.items()}
            cluster_init_kwargs['ignore_reinit_error'] = True
            # Explicitly ensure no resource parameters
            cluster_init_kwargs.pop('num_cpus', None)
            cluster_init_kwargs.pop('num_gpus', None)
            return ray.init(**cluster_init_kwargs)
        else:
            # Re-raise other ValueError exceptions
            raise


def get_device_type():
    """
    Get the appropriate device type for PyTorch

    Returns:
        str: 'cuda', 'mps', or 'cpu'
    """
    import torch

    if torch.cuda.is_available():
        return 'cuda'
    elif torch.backends.mps.is_available():
        return 'mps'
    else:
        return 'cpu'


def get_ray_resources():
    """
    Get available Ray resources

    Returns:
        dict: Available resources
    """
    if not ray.is_initialized():
        return {}

    return ray.available_resources()


def is_cluster_mode():
    """
    Check if running on Ray cluster

    Returns:
        bool: True if on cluster, False if local
    """
    # Check for RAY_ADDRESS environment variable
    if os.environ.get('RAY_ADDRESS'):
        return True

    # Check if cluster storage mount exists
    from pathlib import Path
    if Path('/mnt/cluster_storage').exists():
        return True

    return False


def get_storage_path(relative_path=''):
    """
    Get storage path for data files (cluster-aware)

    Returns cluster storage path (/mnt/cluster_storage) when on cluster,
    otherwise returns local data path.

    Args:
        relative_path: Optional relative path within storage (e.g., 'raw/demo')

    Returns:
        Path: Full path to storage location
    """
    from pathlib import Path

    if is_cluster_mode():
        base = Path('/mnt/cluster_storage')
    else:
        # Local mode - use data/ directory relative to project root
        base = Path(__file__).parent.parent.parent / 'data'

    if relative_path:
        return base / relative_path
    return base
