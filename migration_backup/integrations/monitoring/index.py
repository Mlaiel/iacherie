"""
Monitoring Module - Ainflue Integrations
=======================================
Enterprise-grade monitoring providing comprehensive observability,
real-time performance monitoring, intelligent metrics collection,
advanced alerting systems, and audit compliance across 65+ platform integrations.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Import all monitoring components
from .monitoring_integration import *
from .monitoring_dashboard import *
from .audit_logger import *
from .performance_monitor_core import *
from .metrics_collector import *
from .alerting_system import *

# Re-export for convenience
from . import (
    monitoring_integration,
    monitoring_dashboard,
    audit_logger,
    performance_monitor_core,
    metrics_collector,
    alerting_system
)

# Exports publics
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
__description__ = "Enterprise monitoring infrastructure for multi-platform content distribution observability"

# Configuration logique métier Ainflue
AINFLUE_INTEGRATIONS = {
    'platforms': 65,
    'ecosystems': 3,
    'workflow': 'connect→auth→transform→process→distribute→monitor',
    'monitoring_features': [
        'real_time_observability',
        'intelligent_metrics',
        'predictive_alerting',
        'compliance_auditing',
        'performance_optimization'
    ]
}