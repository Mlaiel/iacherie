"""
MLOps Model Performance Module
Handles model performance tracking and optimization
"""

# This module provides model performance functionality
# Currently using the main monitoring module

try:
    from ..model_monitoring.performance_monitor import PerformanceAlert, MonitoringMetric
    __all__ = ["PerformanceAlert", "MonitoringMetric"]
except ImportError:
    __all__ = []

__version__ = "1.0.0"
