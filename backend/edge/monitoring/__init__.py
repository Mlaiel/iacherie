"""Edge Monitoring Module
======================

Monitoring and observability infrastructure for edge computing nodes,
providing real-time metrics collection, performance monitoring, and alerting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Edge metrics collection
from .edge_metrics import (
    EdgeMetricsCollector,
    MetricType,
    MetricLevel,
    EdgeMetric,
    MetricAggregation,
    create_edge_metrics_collector
)

# Performance monitoring
from .performance_monitor import (
    EdgePerformanceMonitor,
    PerformanceAlert,
    AlertLevel,
    PerformanceThreshold,
    PerformanceTrend,
    create_performance_monitor
)

# Health checking
from .health_checker import (
    EdgeHealthChecker,
    HealthStatus,
    HealthCheck,
    HealthCheckResult,
    create_health_checker
)

# Alerting system
from .alerting_system import (
    EdgeAlertingSystem,
    AlertType,
    AlertRule,
    Alert,
    AlertChannel,
    create_alerting_system
)

# Telemetry collection
from .telemetry_collector import (
    EdgeTelemetryCollector,
    TelemetryData,
    TelemetrySource,
    create_telemetry_collector
)

# Dashboard API
from .dashboard_api import (
    EdgeDashboardAPI,
    DashboardWidget,
    DashboardConfig,
    create_dashboard_api
)

__all__ = [
    # Edge metrics
    "EdgeMetricsCollector",
    "MetricType", 
    "MetricLevel",
    "EdgeMetric",
    "MetricAggregation",
    "create_edge_metrics_collector",
    
    # Performance monitoring
    "EdgePerformanceMonitor",
    "PerformanceAlert",
    "AlertLevel",
    "PerformanceThreshold",
    "PerformanceTrend",
    "create_performance_monitor",
    
    # Health checking
    "EdgeHealthChecker",
    "HealthStatus",
    "HealthCheck",
    "HealthCheckResult",
    "create_health_checker",
    
    # Alerting
    "EdgeAlertingSystem",
    "AlertType",
    "AlertRule",
    "Alert",
    "AlertChannel",
    "create_alerting_system",
    
    # Telemetry
    "EdgeTelemetryCollector",
    "TelemetryData",
    "TelemetrySource",
    "create_telemetry_collector",
    
    # Dashboard
    "EdgeDashboardAPI",
    "DashboardWidget",
    "DashboardConfig",
    "create_dashboard_api"
]