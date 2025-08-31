"""Performance Metrics Agent - Real-Time KPI Monitoring

This agent provides real-time performance metrics and KPI tracking for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .core.performance_metrics_agent import PerformanceMetricsAgent
from .models.performance_models import (
    PerformanceMetricsRequest,
    PerformanceMetricsResult,
    KPIMetric,
    AlertConfiguration
)

__all__ = [
    'PerformanceMetricsAgent',
    'PerformanceMetricsRequest', 
    'PerformanceMetricsResult',
    'KPIMetric',
    'AlertConfiguration'
]

__version__ = "1.0.0"