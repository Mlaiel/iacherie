"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Monitoring & Observability Templates for IA Chéries Platform
========================================================

Production-ready monitoring and observability templates with:
- Metrics collection and Prometheus integration
- Distributed tracing with OpenTelemetry
- Centralized logging with structured formats
- Alert management and notification
- Performance profiling and optimization
- Error tracking and analysis

Author: Fahed Mlaiel (mlaiel@live.de)
Monitoring & Observability Expert
"""

from .metrics_collector_template import MetricsCollectorTemplate
from .tracing_interceptor_template import TracingInterceptorTemplate
from .logging_handler_template import LoggingHandlerTemplate
from .alert_manager_template import AlertManagerTemplate
from .dashboard_exporter_template import DashboardExporterTemplate
from .performance_profiler_template import PerformanceProfilerTemplate
from .error_tracker_template import ErrorTrackerTemplate
from .audit_logger_template import AuditLoggerTemplate

__all__ = [
    "MetricsCollectorTemplate",
    "TracingInterceptorTemplate",
    "LoggingHandlerTemplate",
    "AlertManagerTemplate",
    "DashboardExporterTemplate",
    "PerformanceProfilerTemplate",
    "ErrorTrackerTemplate",
    "AuditLoggerTemplate"
]