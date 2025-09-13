"""Scaling Infrastructure Management - Complete Module
=====================================================
Comprehensive auto-scaling and resource management for enterprise infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Project: Ainflue Infrastructure Enterprise
License: Proprietary - All rights reserved
"""

# Core autoscaling functionality (from root autoscaling.py)
try:
    from .core_autoscaling import (
        AutoscalingManager, HPAManager, VPAManager, ClusterAutoscaler,
        autoscaling_manager, hpa_manager, vpa_manager, cluster_autoscaler
    )
except ImportError:
    AutoscalingManager = HPAManager = VPAManager = None
    autoscaling_manager = hpa_manager = vpa_manager = cluster_autoscaler = None

# Horizontal scaling
try:
    from .horizontal_scaler import HorizontalScaler
except ImportError:
    HorizontalScaler = None

# Vertical scaling
try:
    from .vertical_scaler import VerticalScaler
except ImportError:
    VerticalScaler = None

# Cluster autoscaling
try:
    from .cluster_autoscaler import ClusterAutoscaler as AdvancedClusterAutoscaler
except ImportError:
    AdvancedClusterAutoscaler = None

# Predictive scaling
try:
    from .predictive_scaler import PredictiveScaler
except ImportError:
    PredictiveScaler = None

# Load balancing
try:
    from .load_balancer import LoadBalancer
except ImportError:
    LoadBalancer = None

# Traffic management
try:
    from .traffic_manager import TrafficManager
except ImportError:
    TrafficManager = None

# Capacity planning
try:
    from .capacity_planner import CapacityPlanner
except ImportError:
    CapacityPlanner = None

# Resource optimization
try:
    from .resource_optimizer import ResourceOptimizer
except ImportError:
    ResourceOptimizer = None

# Cost-aware scaling
try:
    from .cost_aware_scaler import CostAwareScaler
except ImportError:
    CostAwareScaler = None

__all__ = [
    # Core autoscaling
    'AutoscalingManager', 'HPAManager', 'VPAManager', 'ClusterAutoscaler',
    'autoscaling_manager', 'hpa_manager', 'vpa_manager', 'cluster_autoscaler',
    # Advanced scaling
    'HorizontalScaler', 'VerticalScaler', 'AdvancedClusterAutoscaler', 'PredictiveScaler',
    'LoadBalancer', 'TrafficManager', 'CapacityPlanner', 'ResourceOptimizer', 'CostAwareScaler'
]