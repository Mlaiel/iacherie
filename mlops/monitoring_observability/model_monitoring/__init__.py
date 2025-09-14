"""
MLOps Model Monitoring Module
Comprehensive monitoring for model performance and data drift
"""

try:
    from .performance_monitor import (
        ComprehensiveModelMonitor, MonitoringMetric, AlertSeverity, DriftType,
        DriftDetector, PerformanceAlert, DriftReport
    )
    __all__ = [
        "ComprehensiveModelMonitor", "MonitoringMetric", "AlertSeverity", "DriftType",
        "DriftDetector", "PerformanceAlert", "DriftReport"
    ]
except ImportError:
    # Graceful degradation when dependencies are missing
    __all__ = []

__version__ = "1.0.0"
