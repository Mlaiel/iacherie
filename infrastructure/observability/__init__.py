"""Observability Infrastructure Management - Complete Module
===========================================================
Comprehensive monitoring and observability for enterprise infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Project: Ainflue Infrastructure Enterprise
License: Proprietary - All rights reserved
"""

# Core monitoring functionality (from root monitoring.py)
try:
    from .core_monitoring import (
        MonitoringManager, MetricsCollector, AlertManager, DashboardManager,
        monitoring_manager, metrics_collector, alert_manager, dashboard_manager
    )
except ImportError:
    MonitoringManager = MetricsCollector = AlertManager = DashboardManager = None
    monitoring_manager = metrics_collector = alert_manager = dashboard_manager = None

# Prometheus integration
try:
    from .prometheus_manager import PrometheusManager
except ImportError:
    PrometheusManager = None

# Grafana integration
try:
    from .grafana_manager import GrafanaManager
except ImportError:
    GrafanaManager = None

# Jaeger tracing
try:
    from .jaeger_manager import JaegerManager
except ImportError:
    JaegerManager = None

# ELK Stack integration
try:
    from .elk_stack_manager import ELKStackManager
except ImportError:
    ELKStackManager = None

# Alert management
try:
    from .alert_manager import AlertManager as AdvancedAlertManager
except ImportError:
    AdvancedAlertManager = None

# Metrics collection
try:
    from .metrics_collector import MetricsCollector as AdvancedMetricsCollector
except ImportError:
    AdvancedMetricsCollector = None

# Log aggregation
try:
    from .log_aggregator import LogAggregator
except ImportError:
    LogAggregator = None

# Performance monitoring
try:
    from .performance_monitor import PerformanceMonitor
except ImportError:
    PerformanceMonitor = None

# Health checking
try:
    from .health_checker import HealthChecker
except ImportError:
    HealthChecker = None

__all__ = [
    # Core monitoring
    'MonitoringManager', 'MetricsCollector', 'AlertManager', 'DashboardManager',
    'monitoring_manager', 'metrics_collector', 'alert_manager', 'dashboard_manager',
    # Specialized monitoring
    'PrometheusManager', 'GrafanaManager', 'JaegerManager', 'ELKStackManager', 
    'AdvancedAlertManager', 'AdvancedMetricsCollector', 'LogAggregator', 
    'PerformanceMonitor', 'HealthChecker'
]