"""Scaling Infrastructure Management"""
try:
    from .horizontal_scaler import HorizontalScaler
except ImportError:
    HorizontalScaler = None

try:
    from .vertical_scaler import VerticalScaler
except ImportError:
    VerticalScaler = None

try:
    from .cluster_autoscaler import ClusterAutoscaler
except ImportError:
    ClusterAutoscaler = None

try:
    from .predictive_scaler import PredictiveScaler
except ImportError:
    PredictiveScaler = None

try:
    from .load_balancer import LoadBalancer
except ImportError:
    LoadBalancer = None

try:
    from .traffic_manager import TrafficManager
except ImportError:
    TrafficManager = None

try:
    from .capacity_planner import CapacityPlanner
except ImportError:
    CapacityPlanner = None

try:
    from .resource_optimizer import ResourceOptimizer
except ImportError:
    ResourceOptimizer = None

try:
    from .cost_aware_scaler import CostAwareScaler
except ImportError:
    CostAwareScaler = None

__all__ = ['HorizontalScaler', 'VerticalScaler', 'ClusterAutoscaler', 'PredictiveScaler',
           'LoadBalancer', 'TrafficManager', 'CapacityPlanner', 'ResourceOptimizer', 'CostAwareScaler']