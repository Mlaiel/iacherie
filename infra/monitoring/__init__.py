"""
  Init   module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Monitoring Infrastructure Module

Enterprise monitoring and observability infrastructure for Ainflue platform.
Provides comprehensive monitoring, alerting, and observability capabilities.
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary"

# Monitoring infrastructure components
from .prometheus_configuration import PrometheusConfiguration
from .grafana_dashboard_manager import GrafanaDashboardManager
from .jaeger_tracing_setup import JaegerTracingSetup
from .alert_manager_configuration import AlertManagerConfiguration
from .metrics_collection_engine import MetricsCollectionEngine
from .logging_infrastructure import LoggingInfrastructure
from .metrics_aggregation import MetricsAggregation
from .distributed_tracing import DistributedTracing
from .performance_monitoring import PerformanceMonitoring
from .health_checker import HealthChecker

__all__ = [
    # Monitoring Stack
    "PrometheusConfiguration",
    "GrafanaDashboardManager",
    "JaegerTracingSetup",
    "AlertManagerConfiguration",
    "MetricsCollectionEngine",
    
    # Observability Components
    "LoggingInfrastructure",
    "MetricsAggregation",
    "DistributedTracing",
    "PerformanceMonitoring",
    "HealthChecker",
]

# Configuration constants
MONITORING_ENDPOINTS = {
    "prometheus": ":9090",
    "grafana": ":3000",
    "jaeger": ":16686",
    "alertmanager": ":9093"
}

METRICS_RETENTION = {
    "short_term": "7d",
    "medium_term": "30d",
    "long_term": "1y"
}

def get_monitoring_info() -> None:
    """Get monitoring module information."""
    return {
        "version": __version__,
        "author": __author__,
        "endpoints": MONITORING_ENDPOINTS,
        "retention_policies": METRICS_RETENTION
    }