"""Advanced Analytics and Metrics Configurations
=============================================

Comprehensive analytics configuration system for crawler performance monitoring,
business intelligence, and data-driven decision making.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps + DBA + Security + Microservices Expert
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project: IA Influencer Agent - Advanced Content Protection Platform
Contact: mlaiel@live.de | www.fahed-mlaiel.de

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, modification, or distribution is strictly prohibited.
Legal action will be taken against violators.
"""import os
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from pathlib import Path

class MetricType(Enum):
    """Types of metrics to collect."""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    RATE = "rate"
    PERCENTAGE = "percentage"
    DISTRIBUTION = "distribution"

class AggregationType(Enum):
    """Aggregation methods for metrics."""    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    STDDEV = "stddev"

class TimeGranularity(Enum):
    """Time granularity for analytics."""    REAL_TIME = "real_time"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class DashboardType(Enum):
    """Types of analytics dashboards."""    OPERATIONAL = "operational"
    BUSINESS = "business"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    SECURITY = "security"
    QUALITY = "quality"

class AlertCondition(Enum):
    """Alert condition types."""    THRESHOLD_EXCEEDED = "threshold_exceeded"
    THRESHOLD_BELOW = "threshold_below"
    RATE_CHANGE = "rate_change"
    ANOMALY_DETECTED = "anomaly_detected"
    PATTERN_BROKEN = "pattern_broken"
    CORRELATION_LOST = "correlation_lost"

@dataclass
class MetricDefinition:
    """Definition of a metric to collect."""    name: str
    metric_type: MetricType
    description: str
    unit: str = ""
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    
    # Collection settings
    collection_interval_seconds: int = 60
    retention_days: int = 90
    aggregation_type: AggregationType = AggregationType.AVERAGE
    
    # Storage settings
    storage_backend: str = "prometheus"  # prometheus, influxdb, elasticsearch
    storage_config: Dict[str, Any] = field(default_factory=dict)
    
    # Alert settings
    alert_enabled: bool = False
    alert_threshold: Optional[float] = None
    alert_condition: AlertCondition = AlertCondition.THRESHOLD_EXCEEDED
    alert_severity: str = "warning"  # info, warning, error, critical

@dataclass
class AnalyticsConfig:
    """Configuration for analytics collection and processing."""    enabled: bool = True
    
    # Collection settings
    real_time_analytics: bool = True
    batch_analytics: bool = True
    streaming_analytics: bool = True
    
    # Data sources
    crawler_metrics: bool = True
    platform_metrics: bool = True
    content_metrics: bool = True
    user_metrics: bool = True
    system_metrics: bool = True
    
    # Processing settings
    data_preprocessing: bool = True
    anomaly_detection: bool = True
    trend_analysis: bool = True
    predictive_analytics: bool = True
    
    # Storage settings
    time_series_db: str = "prometheus"
    analytics_db: str = "elasticsearch"
    data_warehouse: str = "postgresql"
    
    # Export settings
    export_enabled: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json", "parquet"])
    export_schedule: str = "daily"

@dataclass
class DashboardConfig:
    """Configuration for analytics dashboards."""    dashboard_id: str
    dashboard_type: DashboardType
    title: str
    description: str = ""
    enabled: bool = True
    
    # Access control
    public_access: bool = False
    authorized_roles: List[str] = field(default_factory=lambda: ["admin", "analyst"])
    
    # Layout settings
    auto_refresh_seconds: int = 30
    time_range_default: str = "24h"
    timezone: str = "UTC"
    
    # Widgets
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    
    # Export settings
    export_enabled: bool = True
    scheduled_reports: bool = False
    report_recipients: List[str] = field(default_factory=list)

@dataclass
class ReportingConfig:
    """Configuration for automated reporting."""    enabled: bool = True
    
    # Report types
    operational_reports: bool = True
    business_reports: bool = True
    compliance_reports: bool = True
    performance_reports: bool = True
    
    # Scheduling
    daily_reports: bool = True
    weekly_reports: bool = True
    monthly_reports: bool = True
    quarterly_reports: bool = True
    
    # Delivery
    email_delivery: bool = True
    slack_delivery: bool = True
    webhook_delivery: bool = True
    api_delivery: bool = True
    
    # Recipients
    default_recipients: List[str] = field(default_factory=list)
    escalation_recipients: List[str] = field(default_factory=list)
    
    # Content
    include_charts: bool = True
    include_tables: bool = True
    include_summaries: bool = True
    include_recommendations: bool = True

@dataclass
class BusinessIntelligenceConfig:
    """Configuration for business intelligence features."""    enabled: bool = True
    
    # Data mining
    pattern_discovery: bool = True
    correlation_analysis: bool = True
    cohort_analysis: bool = True
    funnel_analysis: bool = True
    
    # Predictive analytics
    forecasting: bool = True
    trend_prediction: bool = True
    anomaly_prediction: bool = True
    capacity_planning: bool = True
    
    # Machine learning
    automated_insights: bool = True
    recommendation_engine: bool = True
    classification_models: bool = True
    clustering_analysis: bool = True
    
    # Visualization
    advanced_charts: bool = True
    interactive_dashboards: bool = True
    custom_visualizations: bool = True
    data_exploration_tools: bool = True

class AnalyticsConfigManager:
    """Manager for analytics configurations."""    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize analytics configuration manager."""        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self.metrics: Dict[str, MetricDefinition] = {}
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.analytics = AnalyticsConfig()
        self.reporting = ReportingConfig()
        self.business_intelligence = BusinessIntelligenceConfig()
        self._load_configurations()
        self._setup_default_metrics()
        self._setup_default_dashboards()
    
    def _load_configurations(self) -> None:
        """Load analytics configurations from files."""        try:
            config_file = self.config_dir / "analytics_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load metrics
                    for metric_name, metric_data in data.get('metrics', {}).items():
                        self.metrics[metric_name] = MetricDefinition(**metric_data)
                    # Load dashboards
                    for dashboard_id, dashboard_data in data.get('dashboards', {}).items():
                        self.dashboards[dashboard_id] = DashboardConfig(**dashboard_data)
        except Exception as e:
            print(f"Error loading analytics configurations: {e}")
    
    def _setup_default_metrics(self) -> None:
        """Setup default metrics for crawlers."""        default_metrics = [
            MetricDefinition(
                name="crawler_requests_total",
                metric_type=MetricType.COUNTER,
                description="Total number of crawler requests",
                unit="requests",
                tags=["crawler", "requests"],
                alert_enabled=True,
                alert_threshold=1000,
                alert_condition=AlertCondition.THRESHOLD_EXCEEDED
            ),
            MetricDefinition(
                name="crawler_success_rate",
                metric_type=MetricType.PERCENTAGE,
                description="Success rate of crawler requests",
                unit="percent",
                tags=["crawler", "success"],
                alert_enabled=True,
                alert_threshold=95.0,
                alert_condition=AlertCondition.THRESHOLD_BELOW
            ),
            MetricDefinition(
                name="crawler_response_time",
                metric_type=MetricType.HISTOGRAM,
                description="Response time of crawler requests",
                unit="milliseconds",
                tags=["crawler", "performance"],
                alert_enabled=True,
                alert_threshold=5000,
                alert_condition=AlertCondition.THRESHOLD_EXCEEDED
            ),
            MetricDefinition(
                name="content_processed_total",
                metric_type=MetricType.COUNTER,
                description="Total amount of content processed",
                unit="items",
                tags=["content", "processing"]
            ),
            MetricDefinition(
                name="violations_detected_total",
                metric_type=MetricType.COUNTER,
                description="Total violations detected",
                unit="violations",
                tags=["security", "violations"],
                alert_enabled=True,
                alert_threshold=10,
                alert_condition=AlertCondition.THRESHOLD_EXCEEDED,
                alert_severity="critical"
            ),
            MetricDefinition(
                name="data_quality_score",
                metric_type=MetricType.GAUGE,
                description="Overall data quality score",
                unit="score",
                tags=["quality", "data"],
                alert_enabled=True,
                alert_threshold=0.8,
                alert_condition=AlertCondition.THRESHOLD_BELOW
            )
        ]
        
        for metric in default_metrics:
            if metric.name not in self.metrics:
                self.metrics[metric.name] = metric
    
    def _setup_default_dashboards(self) -> None:
        """Setup default analytics dashboards."""        default_dashboards = [
            DashboardConfig(
                dashboard_id="operational_overview",
                dashboard_type=DashboardType.OPERATIONAL,
                title="Operational Overview",
                description="Real-time operational metrics and status",
                widgets=[
                    {
                        "type": "metric_card",
                        "metric": "crawler_requests_total",
                        "title": "Total Requests",
                        "time_range": "24h"
                    },
                    {
                        "type": "line_chart",
                        "metric": "crawler_success_rate",
                        "title": "Success Rate",
                        "time_range": "24h"
                    },
                    {
                        "type": "histogram",
                        "metric": "crawler_response_time",
                        "title": "Response Time Distribution",
                        "time_range": "1h"
                    }
                ]
            ),
            DashboardConfig(
                dashboard_id="content_analytics",
                dashboard_type=DashboardType.BUSINESS,
                title="Content Analytics",
                description="Content processing and quality metrics",
                widgets=[
                    {
                        "type": "metric_card",
                        "metric": "content_processed_total",
                        "title": "Content Processed",
                        "time_range": "24h"
                    },
                    {
                        "type": "gauge",
                        "metric": "data_quality_score",
                        "title": "Data Quality Score",
                        "time_range": "1h"
                    },
                    {
                        "type": "alert_table",
                        "metric": "violations_detected_total",
                        "title": "Recent Violations",
                        "time_range": "24h"
                    }
                ]
            ),
            DashboardConfig(
                dashboard_id="executive_summary",
                dashboard_type=DashboardType.EXECUTIVE,
                title="Executive Summary",
                description="High-level business metrics and KPIs",
                authorized_roles=["admin", "executive"],
                widgets=[
                    {
                        "type": "kpi_grid",
                        "metrics": [
                            "crawler_success_rate",
                            "data_quality_score",
                            "content_processed_total"
                        ],
                        "title": "Key Performance Indicators",
                        "time_range": "7d"
                    }
                ]
            )
        ]
        
        for dashboard in default_dashboards:
            if dashboard.dashboard_id not in self.dashboards:
                self.dashboards[dashboard.dashboard_id] = dashboard
    
    def register_metric(self, metric: MetricDefinition) -> None:
        """Register a new metric."""        self.metrics[metric.name] = metric
        self._save_configurations()
    
    def register_dashboard(self, dashboard: DashboardConfig) -> None:
        """Register a new dashboard."""        self.dashboards[dashboard.dashboard_id] = dashboard
        self._save_configurations()
    
    def get_metrics(self, enabled_only: bool = True, tags: Optional[List[str]] = None) -> List[MetricDefinition]:
        """Get metrics, optionally filtered by enabled status and tags."""        metrics = list(self.metrics.values())
        
        if enabled_only:
            metrics = [m for m in metrics if m.enabled]
        
        if tags:
            metrics = [m for m in metrics if any(tag in m.tags for tag in tags)]
        
        return metrics
    
    def get_dashboard(self, dashboard_id: str) -> Optional[DashboardConfig]:
        """Get dashboard configuration by ID."""        return self.dashboards.get(dashboard_id)
    
    def get_dashboards_by_type(self, dashboard_type: DashboardType) -> List[DashboardConfig]:
        """Get dashboards by type."""        return [d for d in self.dashboards.values() if d.dashboard_type == dashboard_type]
    
    def generate_analytics_report(self, 
                                start_time: datetime, 
                                end_time: datetime,
                                metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate analytics report for specified time period."""        report = {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_hours": (end_time - start_time).total_seconds() / 3600
            },
            "summary": {},
            "metrics": {},
            "insights": [],
            "recommendations": []
        }
        
        # Get metrics to include in report
        if metrics is None:
            metrics = [m.name for m in self.get_metrics()]
        
        # This would be implemented with actual data collection
        # For now, return template structure
        for metric_name in metrics:
            metric_def = self.metrics.get(metric_name)
            if metric_def:
                report["metrics"][metric_name] = {
                    "description": metric_def.description,
                    "unit": metric_def.unit,
                    "type": metric_def.metric_type.value,
                    "data": [],  # Would contain actual time series data
                    "summary": {
                        "total": 0,
                        "average": 0,
                        "min": 0,
                        "max": 0
                    }
                }
        
        return report
    
    def get_metric_alerts(self) -> List[Dict[str, Any]]:
        """Get active metric alerts."""        alerts = []
        
        for metric in self.get_metrics():
            if metric.alert_enabled:
                # This would check actual metric values against thresholds
                # For now, return template structure
                alerts.append({
                    "metric_name": metric.name,
                    "alert_condition": metric.alert_condition.value,
                    "threshold": metric.alert_threshold,
                    "severity": metric.alert_severity,
                    "status": "ok",  # Would be actual status
                    "last_triggered": None
                })
        
        return alerts
    
    def optimize_metric_collection(self) -> Dict[str, Any]:
        """Optimize metric collection based on usage patterns."""        optimization_report = {
            "recommendations": [],
            "potential_savings": {},
            "performance_improvements": []
        }
        
        # Analyze metric usage and performance
        for metric in self.get_metrics():
            # Check if metric is being queried
            # Check collection overhead
            # Suggest optimizations
            pass
        
        return optimization_report
    
    def _save_configurations(self) -> None:
        """Save configurations to file."""        try:
            config_file = self.config_dir / "analytics_config.json"
            config_data = {
                "metrics": {
                    name: {
                        "name": metric.name,
                        "metric_type": metric.metric_type.value,
                        "description": metric.description,
                        "unit": metric.unit,
                        "tags": metric.tags,
                        "enabled": metric.enabled,
                        "collection_interval_seconds": metric.collection_interval_seconds,
                        "alert_enabled": metric.alert_enabled,
                        "alert_threshold": metric.alert_threshold
                    }
                    for name, metric in self.metrics.items()
                },
                "dashboards": {
                    dashboard_id: {
                        "dashboard_id": dashboard.dashboard_id,
                        "dashboard_type": dashboard.dashboard_type.value,
                        "title": dashboard.title,
                        "description": dashboard.description,
                        "enabled": dashboard.enabled,
                        "widgets": dashboard.widgets
                    }
                    for dashboard_id, dashboard in self.dashboards.items()
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving analytics configurations: {e}")

# Global analytics configuration manager
analytics_config_manager = AnalyticsConfigManager()

# Predefined metric collections
METRIC_COLLECTIONS = {
    "crawler_performance": [
        "crawler_requests_total",
        "crawler_success_rate", 
        "crawler_response_time",
        "crawler_errors_total"
    ],
    "content_quality": [
        "content_processed_total",
        "data_quality_score",
        "violations_detected_total",
        "duplicate_content_rate"
    ],
    "system_health": [
        "cpu_usage_percent",
        "memory_usage_percent",
        "disk_usage_percent",
        "network_throughput"
    ]
}
