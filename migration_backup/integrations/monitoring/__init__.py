"""
Monitoring Module - Ainflue Integrations
=======================================
Enterprise monitoring module providing comprehensive observability,
performance monitoring, metrics collection, and alerting systems.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Monitoring Core Components
from .monitoring_integration import MonitoringIntegration
from .monitoring_dashboard import MonitoringDashboard
from .audit_logger import AuditLogger

# Performance monitoring components (decomposed from performance_monitor.py)
from .performance_monitor_core import PerformanceMonitorCore
from .metrics_collector import MetricsCollector
from .alerting_system import AlertingSystem

# Public exports
__all__ = [
    'MonitoringIntegration',
    'MonitoringDashboard',
    'AuditLogger',
    'PerformanceMonitorCore',
    'MetricsCollector',
    'AlertingSystem',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise monitoring and observability for Ainflue platform"

# Configuration logique métier Ainflue
AINFLUE_MONITORING = {
    'platforms': 65,
    'monitoring_features': ['real_time_metrics', 'performance_monitoring', 'alerting', 'audit_logging'],
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}