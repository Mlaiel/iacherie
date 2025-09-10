"""
Monitoring Module for Ainflue Distribution Platform

This module provides comprehensive monitoring, observability, and performance
tracking for the distribution platform with real-time metrics and alerting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .distribution_metrics_collector import (
    DistributionMetricsCollector,
    MetricType,
    MetricData,
    MetricAggregation
)

from .platform_health_monitor import (
    PlatformHealthMonitor,
    HealthCheck,
    HealthStatus,
    ServiceHealth
)

from .performance_tracker import (
    PerformanceTracker,
    PerformanceMetric,
    PerformanceThreshold,
    SystemMetrics,
    ApplicationMetrics,
    MetricType,
    AlertLevel,
    PerformanceTimer,
    track_performance
)

from .alerting_system import (
    AlertingSystem,
    Alert,
    AlertLevel,
    AlertChannel
)

from .dashboard_generator import (
    DashboardGenerator,
    Dashboard,
    Widget,
    Visualization
)

__all__ = [
    # Metrics Collection
    'DistributionMetricsCollector',
    'MetricType',
    'MetricData', 
    'MetricAggregation',
    
    # Health Monitoring
    'PlatformHealthMonitor',
    'HealthCheck',
    'HealthStatus',
    'ServiceHealth',
    
    # Performance Tracking
    'PerformanceTracker',
    'PerformanceMetric',
    'PerformanceThreshold',
    'SystemMetrics',
    'ApplicationMetrics',
    'MetricType',
    'AlertLevel',
    'PerformanceTimer',
    'track_performance',
    
    # Alerting
    'AlertingSystem',
    'Alert',
    'AlertLevel',
    'AlertChannel',
    
    # Dashboards
    'DashboardGenerator',
    'Dashboard',
    'Widget',
    'Visualization'
]

__version__ = "1.0.0"