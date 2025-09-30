"""Monitoring Module for Ainflue Platform
Enterprise-grade monitoring infrastructure with comprehensive observability.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .index import (
    MetricType,
    AlertSeverity,
    MonitoringAlert,
    MetricDefinition,
    MonitoringOrchestrator,
    monitoring_orchestrator,
    initialize_monitoring_services,
    shutdown_monitoring_services
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    'MetricType',
    'AlertSeverity',
    'MonitoringAlert',
    'MetricDefinition',
    'MonitoringOrchestrator',
    'monitoring_orchestrator',
    'initialize_monitoring_services',
    'shutdown_monitoring_services'
]