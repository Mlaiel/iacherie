"""
Auto Scaling Agent - Enterprise Dynamic Resource Management & Load Balancing System

© 2025 Fahed Mlaiel - All Rights Reserved.
This module provides advanced auto-scaling capabilities for the IA Influencer Agent platform.
"""

from .auto_scaling_manager import AutoScalingManager
from .load_balancer import IntelligentLoadBalancer
from .resource_monitor import ResourceMonitor
from .scaling_engine import ScalingEngine
from .metrics_collector import MetricsCollector
from .threshold_manager import ThresholdManager

__all__ = [
    'AutoScalingManager',
    'IntelligentLoadBalancer',
    'ResourceMonitor',
    'ScalingEngine',
    'MetricsCollector',
    'ThresholdManager'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
