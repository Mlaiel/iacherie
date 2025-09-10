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
    DashboardConfig,
    ChartConfig,
    MetricConfig,
    ChartType,
    DashboardTheme,
    RefreshRate
)

from .anomaly_detector import (
    AnomalyDetector,
    AnomalyType,
    AnomalyDetectionConfig,
    AnomalyAlert,
    DetectionMethod
)

# New monitoring modules
from .report_engine import (
    DistributionReportEngine,
    create_report_engine,
    ReportType,
    ReportFormat,
    ReportConfig,
    GeneratedReport
)

from .capacity_planner import (
    DistributionCapacityPlanner,
    create_capacity_planner,
    ResourceType,
    PlanningHorizon,
    CapacityPrediction,
    CapacityAlert
)

from .sla_monitor import (
    DistributionSLAMonitor,
    create_sla_monitor,
    SLAMetricType,
    SLATarget,
    SLAMeasurement,
    SLABreach,
    SLAReport
)

from .cost_tracker import (
    DistributionCostTracker,
    create_cost_tracker,
    CostCategory,
    CostItem,
    CostBudget,
    CostAlert
)

from .roi_calculator import (
    DistributionROICalculator,
    create_roi_calculator,
    RevenueStream,
    InvestmentType,
    ROIAnalysis,
    CustomerMetrics
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
    'DashboardConfig',
    'ChartConfig',
    'MetricConfig',
    'ChartType',
    'DashboardTheme',
    'RefreshRate',
    
    # Anomaly Detection
    'AnomalyDetector',
    'AnomalyType',
    'AnomalyDetectionConfig',
    'AnomalyAlert',
    'DetectionMethod',
    
    # Reporting
    'DistributionReportEngine',
    'create_report_engine',
    'ReportType',
    'ReportFormat',
    'ReportConfig',
    'GeneratedReport',
    
    # Capacity Planning
    'DistributionCapacityPlanner',
    'create_capacity_planner',
    'ResourceType',
    'PlanningHorizon',
    'CapacityPrediction',
    'CapacityAlert',
    
    # SLA Monitoring
    'DistributionSLAMonitor',
    'create_sla_monitor',
    'SLAMetricType',
    'SLATarget',
    'SLAMeasurement',
    'SLABreach',
    'SLAReport',
    
    # Cost Tracking
    'DistributionCostTracker',
    'create_cost_tracker',
    'CostCategory',
    'CostItem',
    'CostBudget',
    'CostAlert',
    
    # ROI Calculation
    'DistributionROICalculator',
    'create_roi_calculator',
    'RevenueStream',
    'InvestmentType',
    'ROIAnalysis',
    'CustomerMetrics'
]

__version__ = "1.0.0"