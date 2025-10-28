"""Utility modules"""

# Lazy imports to avoid loading OpenCV GUI dependencies on worker nodes
__all__ = [
    'check_timg_available',
    'play_video_timg',
    'play_comparison_timg',
    'SideBySidePlayer',
    'play_videos_side_by_side',
    'safe_ray_init',
    'get_storage_path',
    'is_cluster_mode',
    'get_device_type',
    'get_ray_resources'
]

def __getattr__(name):
    """Lazy import to avoid loading display dependencies on worker nodes"""
    if name in ['check_timg_available', 'play_video_timg', 'play_comparison_timg']:
        from .timg_video_player import check_timg_available, play_video_timg, play_comparison_timg
        return locals()[name]
    elif name in ['SideBySidePlayer', 'play_videos_side_by_side']:
        from .side_by_side_player import SideBySidePlayer, play_videos_side_by_side
        return locals()[name]
    elif name in ['safe_ray_init', 'get_storage_path', 'is_cluster_mode', 'get_device_type', 'get_ray_resources']:
        from .ray_utils import safe_ray_init, get_storage_path, is_cluster_mode, get_device_type, get_ray_resources
        return locals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
