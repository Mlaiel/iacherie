"""
from datetime import datetime

Monitoring System Configurations
===============================

System monitoring and observability settings for Ainflue Distribution Platform.
Handles metrics collection, alerting, and performance monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import timedelta
import os
import json

class MetricType(Enum):
    """Types of metrics to monitor"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"
    PERCENTAGE = "percentage"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel(Enum):
    """Alert notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    DISCORD = "discord"

class MonitoringScope(Enum):
    """Monitoring scope levels"""
    SYSTEM = "system"
    APPLICATION = "application"
    BUSINESS = "business"
    USER_EXPERIENCE = "user_experience"
    SECURITY = "security"

@dataclass
class MetricConfig:
    """Configuration for a specific metric"""
    name: str
    metric_type: MetricType
    scope: MonitoringScope
    collection_interval_seconds: int = 60
    retention_days: int = 30
    tags: Dict[str, str] = field(default_factory=dict)
    aggregation_methods: List[str] = field(default_factory=lambda: ["avg", "max", "min"])
    enabled: bool = True
    
@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric_name: str
    condition: str  # e.g., "> 80", "< 0.5", "== 0"
    threshold: float
    severity: AlertSeverity
    evaluation_window_minutes: int = 5
    cooldown_minutes: int = 15
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class AlertChannel:
    """Alert notification channel configuration"""
    name: str
    channel_type: AlertChannel
    endpoint: str  # email, webhook URL, Slack channel, etc.
    enabled: bool = True
    severity_filter: List[AlertSeverity] = field(default_factory=lambda: [AlertSeverity.WARNING, AlertSeverity.ERROR, AlertSeverity.CRITICAL])
    rate_limit_minutes: int = 5
    template: str = "default"
    
@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    name: str
    metrics: List[str]
    refresh_interval_seconds: int = 30
    time_range_hours: int = 24
    chart_types: Dict[str, str] = field(default_factory=dict)
    filters: Dict[str, List[str]] = field(default_factory=dict)
    enabled: bool = True
    
@dataclass
class PerformanceThresholds:
    """Performance thresholds for monitoring"""
    response_time_ms: Dict[str, float] = field(default_factory=lambda: {
        "p50": 100.0,
        "p95": 500.0,
        "p99": 1000.0
    })
    throughput_rps: float = 1000.0
    error_rate_percentage: float = 1.0
    availability_percentage: float = 99.9
    resource_utilization: Dict[str, float] = field(default_factory=lambda: {
        "cpu": 80.0,
        "memory": 85.0,
        "disk": 90.0,
        "network": 80.0
    })

class MonitoringConfigs:
    """
    System monitoring configuration manager
    
    Features:
    - Metric collection configuration
    - Alert rule management
    - Dashboard configuration
    - Performance thresholds
    - Integration settings
    - Data retention policies
    """
    
    def __init__(self) -> None:
        self.metrics: Dict[str, MetricConfig] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alert_channels: Dict[str, AlertChannel] = {}
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.performance_thresholds = PerformanceThresholds()
        self.global_settings = self._get_default_global_settings()
        self._load_default_configurations()
        
    def _get_default_global_settings(self) -> Dict[str, Any]:
        """Get default global monitoring settings"""
        return {
            "enabled": True,
            "default_retention_days": 30,
            "default_collection_interval": 60,
            "enable_alerting": True,
            "enable_dashboards": True,
            "timezone": "UTC",
            "data_compression": True,
            "sampling_rate": 1.0,
            "batch_size": 1000,
            "export_formats": ["prometheus", "json", "csv"],
            "storage_backend": "prometheus",
            "backup_enabled": True,
            "backup_interval_hours": 24
        }
        
    def _load_default_configurations(self) -> None:
        """Load default monitoring configurations"""
        
        # System metrics
        self.metrics.update({
            "system_cpu_usage": MetricConfig(
                name="system_cpu_usage",
                metric_type=MetricType.GAUGE,
                scope=MonitoringScope.SYSTEM,
                collection_interval_seconds=30,
                retention_days=90,
                tags={"component": "system"},
                aggregation_methods=["avg", "max"]
            ),
            "system_memory_usage": MetricConfig(
                name="system_memory_usage",
                metric_type=MetricType.GAUGE,
                scope=MonitoringScope.SYSTEM,
                collection_interval_seconds=30,
                retention_days=90,
                tags={"component": "system"}
            ),
            "system_disk_usage": MetricConfig(
                name="system_disk_usage",
                metric_type=MetricType.GAUGE,
                scope=MonitoringScope.SYSTEM,
                collection_interval_seconds=300,  # 5 minutes
                retention_days=90,
                tags={"component": "system"}
            ),
            "system_network_io": MetricConfig(
                name="system_network_io",
                metric_type=MetricType.RATE,
                scope=MonitoringScope.SYSTEM,
                collection_interval_seconds=60,
                retention_days=30,
                tags={"component": "system"}
            )
        })
        
        # Application metrics
        self.metrics.update({
            "app_request_count": MetricConfig(
                name="app_request_count",
                metric_type=MetricType.COUNTER,
                scope=MonitoringScope.APPLICATION,
                collection_interval_seconds=10,
                retention_days=60,
                tags={"component": "api"},
                aggregation_methods=["sum", "rate"]
            ),
            "app_response_time": MetricConfig(
                name="app_response_time",
                metric_type=MetricType.HISTOGRAM,
                scope=MonitoringScope.APPLICATION,
                collection_interval_seconds=10,
                retention_days=60,
                tags={"component": "api"},
                aggregation_methods=["avg", "p50", "p95", "p99"]
            ),
            "app_error_rate": MetricConfig(
                name="app_error_rate",
                metric_type=MetricType.RATE,
                scope=MonitoringScope.APPLICATION,
                collection_interval_seconds=60,
                retention_days=90,
                tags={"component": "api"}
            ),
            "app_active_users": MetricConfig(
                name="app_active_users",
                metric_type=MetricType.GAUGE,
                scope=MonitoringScope.APPLICATION,
                collection_interval_seconds=300,
                retention_days=30,
                tags={"component": "user"}
            )
        })
        
        # Business metrics
        self.metrics.update({
            "business_publications_total": MetricConfig(
                name="business_publications_total",
                metric_type=MetricType.COUNTER,
                scope=MonitoringScope.BUSINESS,
                collection_interval_seconds=60,
                retention_days=365,
                tags={"component": "distribution"}
            ),
            "business_revenue": MetricConfig(
                name="business_revenue",
                metric_type=MetricType.COUNTER,
                scope=MonitoringScope.BUSINESS,
                collection_interval_seconds=300,
                retention_days=365,
                tags={"component": "monetization"}
            ),
            "business_conversion_rate": MetricConfig(
                name="business_conversion_rate",
                metric_type=MetricType.PERCENTAGE,
                scope=MonitoringScope.BUSINESS,
                collection_interval_seconds=300,
                retention_days=90,
                tags={"component": "funnel"}
            ),
            "business_churn_rate": MetricConfig(
                name="business_churn_rate",
                metric_type=MetricType.PERCENTAGE,
                scope=MonitoringScope.BUSINESS,
                collection_interval_seconds=3600,  # 1 hour
                retention_days=365,
                tags={"component": "retention"}
            )
        })
        
        # User experience metrics
        self.metrics.update({
            "ux_page_load_time": MetricConfig(
                name="ux_page_load_time",
                metric_type=MetricType.HISTOGRAM,
                scope=MonitoringScope.USER_EXPERIENCE,
                collection_interval_seconds=60,
                retention_days=30,
                tags={"component": "frontend"}
            ),
            "ux_error_count": MetricConfig(
                name="ux_error_count",
                metric_type=MetricType.COUNTER,
                scope=MonitoringScope.USER_EXPERIENCE,
                collection_interval_seconds=60,
                retention_days=30,
                tags={"component": "frontend"}
            ),
            "ux_satisfaction_score": MetricConfig(
                name="ux_satisfaction_score",
                metric_type=MetricType.GAUGE,
                scope=MonitoringScope.USER_EXPERIENCE,
                collection_interval_seconds=3600,
                retention_days=90,
                tags={"component": "feedback"}
            )
        })
        
        # Security metrics
        self.metrics.update({
            "security_failed_logins": MetricConfig(
                name="security_failed_logins",
                metric_type=MetricType.COUNTER,
                scope=MonitoringScope.SECURITY,
                collection_interval_seconds=60,
                retention_days=90,
                tags={"component": "auth"}
            ),
            "security_suspicious_activity": MetricConfig(
                name="security_suspicious_activity",
                metric_type=MetricType.COUNTER,
                scope=MonitoringScope.SECURITY,
                collection_interval_seconds=60,
                retention_days=180,
                tags={"component": "security"}
            ),
            "security_api_rate_limit_hits": MetricConfig(
                name="security_api_rate_limit_hits",
                metric_type=MetricType.COUNTER,
                scope=MonitoringScope.SECURITY,
                collection_interval_seconds=60,
                retention_days=30,
                tags={"component": "api"}
            )
        })
        
        # Alert rules
        self.alert_rules.update({
            "high_cpu_usage": AlertRule(
                name="High CPU Usage",
                metric_name="system_cpu_usage",
                condition=">",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                evaluation_window_minutes=5,
                cooldown_minutes=15
            ),
            "critical_cpu_usage": AlertRule(
                name="Critical CPU Usage",
                metric_name="system_cpu_usage",
                condition=">",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                evaluation_window_minutes=2,
                cooldown_minutes=5
            ),
            "high_memory_usage": AlertRule(
                name="High Memory Usage",
                metric_name="system_memory_usage",
                condition=">",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                evaluation_window_minutes=5
            ),
            "high_error_rate": AlertRule(
                name="High Error Rate",
                metric_name="app_error_rate",
                condition=">",
                threshold=5.0,
                severity=AlertSeverity.ERROR,
                evaluation_window_minutes=3,
                cooldown_minutes=10
            ),
            "slow_response_time": AlertRule(
                name="Slow Response Time",
                metric_name="app_response_time",
                condition=">",
                threshold=1000.0,  # 1 second
                severity=AlertSeverity.WARNING,
                evaluation_window_minutes=5
            ),
            "low_conversion_rate": AlertRule(
                name="Low Conversion Rate",
                metric_name="business_conversion_rate",
                condition="<",
                threshold=2.0,  # 2%
                severity=AlertSeverity.WARNING,
                evaluation_window_minutes=30
            ),
            "security_brute_force": AlertRule(
                name="Potential Brute Force Attack",
                metric_name="security_failed_logins",
                condition=">",
                threshold=100.0,
                severity=AlertSeverity.CRITICAL,
                evaluation_window_minutes=5,
                cooldown_minutes=30
            )
        })
        
        # Alert channels
        self.alert_channels.update({
            "ops_email": AlertChannel(
                name="Operations Email",
                channel_type=AlertChannel.EMAIL,
                endpoint="ops@ainflue.com",
                severity_filter=[AlertSeverity.WARNING, AlertSeverity.ERROR, AlertSeverity.CRITICAL],
                rate_limit_minutes=5
            ),
            "ops_slack": AlertChannel(
                name="Operations Slack",
                channel_type=AlertChannel.SLACK,
                endpoint="#ops-alerts",
                severity_filter=[AlertSeverity.ERROR, AlertSeverity.CRITICAL],
                rate_limit_minutes=3
            ),
            "oncall_pagerduty": AlertChannel(
                name="On-Call PagerDuty",
                channel_type=AlertChannel.PAGERDUTY,
                endpoint="critical-alerts",
                severity_filter=[AlertSeverity.CRITICAL],
                rate_limit_minutes=1
            ),
            "business_webhook": AlertChannel(
                name="Business Metrics Webhook",
                channel_type=AlertChannel.WEBHOOK,
                endpoint="https://hooks.slack.com/business-alerts",
                severity_filter=[AlertSeverity.WARNING, AlertSeverity.ERROR],
                rate_limit_minutes=10
            )
        })
        
        # Dashboards
        self.dashboards.update({
            "system_overview": DashboardConfig(
                name="System Overview",
                metrics=["system_cpu_usage", "system_memory_usage", "system_disk_usage", "system_network_io"],
                refresh_interval_seconds=30,
                time_range_hours=24,
                chart_types={
                    "system_cpu_usage": "line",
                    "system_memory_usage": "line",
                    "system_disk_usage": "gauge",
                    "system_network_io": "area"
                }
            ),
            "application_performance": DashboardConfig(
                name="Application Performance",
                metrics=["app_request_count", "app_response_time", "app_error_rate", "app_active_users"],
                refresh_interval_seconds=10,
                time_range_hours=12,
                chart_types={
                    "app_request_count": "bar",
                    "app_response_time": "histogram",
                    "app_error_rate": "line",
                    "app_active_users": "line"
                }
            ),
            "business_metrics": DashboardConfig(
                name="Business Metrics",
                metrics=["business_publications_total", "business_revenue", "business_conversion_rate", "business_churn_rate"],
                refresh_interval_seconds=300,
                time_range_hours=168,  # 7 days
                chart_types={
                    "business_publications_total": "cumulative",
                    "business_revenue": "bar",
                    "business_conversion_rate": "line",
                    "business_churn_rate": "line"
                }
            ),
            "security_dashboard": DashboardConfig(
                name="Security Dashboard",
                metrics=["security_failed_logins", "security_suspicious_activity", "security_api_rate_limit_hits"],
                refresh_interval_seconds=60,
                time_range_hours=24,
                chart_types={
                    "security_failed_logins": "heatmap",
                    "security_suspicious_activity": "scatter",
                    "security_api_rate_limit_hits": "bar"
                }
            )
        })
        
    def get_metric_config(self, metric_name: str) -> Optional[MetricConfig]:
        """Get configuration for a specific metric"""
        return self.metrics.get(metric_name)
        
    def get_alert_rule(self, rule_name: str) -> Optional[AlertRule]:
        """Get alert rule configuration"""
        return self.alert_rules.get(rule_name)
        
    def get_alert_channel(self, channel_name: str) -> Optional[AlertChannel]:
        """Get alert channel configuration"""
        return self.alert_channels.get(channel_name)
        
    def get_dashboard_config(self, dashboard_name: str) -> Optional[DashboardConfig]:
        """Get dashboard configuration"""
        return self.dashboards.get(dashboard_name)
        
    def get_metrics_by_scope(self, scope: MonitoringScope) -> List[MetricConfig]:
        """Get all metrics for a specific scope"""
        return [metric for metric in self.metrics.values() if metric.scope == scope]
        
    def get_enabled_metrics(self) -> List[MetricConfig]:
        """Get all enabled metrics"""
        return [metric for metric in self.metrics.values() if metric.enabled]
        
    def get_critical_alerts(self) -> List[AlertRule]:
        """Get all critical alert rules"""
        return [rule for rule in self.alert_rules.values() 
                if rule.severity == AlertSeverity.CRITICAL and rule.enabled]
        
    def validate_metric_threshold(self, metric_name: str, value: float) -> List[AlertRule]:
        """Check if metric value triggers any alert rules"""
        triggered_rules = []
        
        for rule in self.alert_rules.values():
            if not rule.enabled or rule.metric_name != metric_name:
                continue
                
            if self._evaluate_alert_condition(rule.condition, value, rule.threshold):
                triggered_rules.append(rule)
                
        return triggered_rules
        
    def _evaluate_alert_condition(self, condition: str, value: float, threshold: float) -> bool:
        """Evaluate alert condition"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return abs(value - threshold) < 0.001  # Float comparison
        elif condition == "!=":
            return abs(value - threshold) >= 0.001
        return False
        
    def get_retention_policy(self, metric_name: str) -> int:
        """Get retention policy for a metric in days"""
        metric = self.get_metric_config(metric_name)
        return metric.retention_days if metric else self.global_settings["default_retention_days"]
        
    def get_collection_interval(self, metric_name: str) -> int:
        """Get collection interval for a metric in seconds"""
        metric = self.get_metric_config(metric_name)
        return metric.collection_interval_seconds if metric else self.global_settings["default_collection_interval"]
        
    def add_custom_metric(self, metric_config -> None: MetricConfig) -> None:
        """Add a custom metric configuration"""
        self.metrics[metric_config.name] = metric_config
        
    def add_custom_alert_rule(self, alert_rule -> None: AlertRule) -> None:
        """Add a custom alert rule"""
        self.alert_rules[alert_rule.name] = alert_rule
        
    def add_custom_alert_channel(self, alert_channel -> None: AlertChannel) -> None:
        """Add a custom alert channel"""
        self.alert_channels[alert_channel.name] = alert_channel
        
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get monitoring configuration summary"""
        return {
            "total_metrics": len(self.metrics),
            "enabled_metrics": len(self.get_enabled_metrics()),
            "total_alert_rules": len(self.alert_rules),
            "critical_alert_rules": len(self.get_critical_alerts()),
            "alert_channels": len(self.alert_channels),
            "dashboards": len(self.dashboards),
            "metrics_by_scope": {
                scope.value: len(self.get_metrics_by_scope(scope))
                for scope in MonitoringScope
            },
            "global_settings": self.global_settings
        }
        
    def generate_prometheus_config(self) -> Dict[str, Any]:
        """Generate Prometheus-compatible configuration"""
        prometheus_config = {
            "global": {
                "scrape_interval": f"{self.global_settings['default_collection_interval']}s",
                "evaluation_interval": "15s"
            },
            "scrape_configs": [],
            "rule_files": ["alert_rules.yml"],
            "alerting": {
                "alertmanagers": [
                    {
                        "static_configs": [
                            {
                                "targets": ["alertmanager:9093"]
                            }
                        ]
                    }
                ]
            }
        }
        
        # Group metrics by collection interval
        scrape_configs_by_interval = {}
        for metric in self.get_enabled_metrics():
            interval = metric.collection_interval_seconds
            if interval not in scrape_configs_by_interval:
                scrape_configs_by_interval[interval] = []
            scrape_configs_by_interval[interval].append(metric)
            
        # Create scrape configs
        for interval, metrics in scrape_configs_by_interval.items():
            scrape_config = {
                "job_name": f"ainflue_metrics_{interval}s",
                "scrape_interval": f"{interval}s",
                "static_configs": [
                    {
                        "targets": ["localhost:8080"],
                        "labels": {
                            "service": "ainflue_distribution"
                        }
                    }
                ],
                "metrics_path": "/metrics",
                "honor_labels": True
            }
            prometheus_config["scrape_configs"].append(scrape_config)
            
        return prometheus_config
        
    def export_config(self, output_path -> None: str) -> None:
        """Export configuration to JSON file"""
        config_data = {
            "global_settings": self.global_settings,
            "performance_thresholds": {
                "response_time_ms": self.performance_thresholds.response_time_ms,
                "throughput_rps": self.performance_thresholds.throughput_rps,
                "error_rate_percentage": self.performance_thresholds.error_rate_percentage,
                "availability_percentage": self.performance_thresholds.availability_percentage,
                "resource_utilization": self.performance_thresholds.resource_utilization
            },
            "metrics": {
                name: {
                    "name": config.name,
                    "metric_type": config.metric_type.value,
                    "scope": config.scope.value,
                    "collection_interval_seconds": config.collection_interval_seconds,
                    "retention_days": config.retention_days,
                    "tags": config.tags,
                    "aggregation_methods": config.aggregation_methods,
                    "enabled": config.enabled
                }
                for name, config in self.metrics.items()
            },
            "alert_rules": {
                name: {
                    "name": rule.name,
                    "metric_name": rule.metric_name,
                    "condition": rule.condition,
                    "threshold": rule.threshold,
                    "severity": rule.severity.value,
                    "evaluation_window_minutes": rule.evaluation_window_minutes,
                    "cooldown_minutes": rule.cooldown_minutes,
                    "enabled": rule.enabled,
                    "tags": rule.tags
                }
                for name, rule in self.alert_rules.items()
            },
            "alert_channels": {
                name: {
                    "name": channel.name,
                    "channel_type": channel.channel_type.value,
                    "endpoint": channel.endpoint,
                    "enabled": channel.enabled,
                    "severity_filter": [s.value for s in channel.severity_filter],
                    "rate_limit_minutes": channel.rate_limit_minutes,
                    "template": channel.template
                }
                for name, channel in self.alert_channels.items()
            },
            "dashboards": {
                name: {
                    "name": config.name,
                    "metrics": config.metrics,
                    "refresh_interval_seconds": config.refresh_interval_seconds,
                    "time_range_hours": config.time_range_hours,
                    "chart_types": config.chart_types,
                    "filters": config.filters,
                    "enabled": config.enabled
                }
                for name, config in self.dashboards.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

# Global instance
monitoring_configs = MonitoringConfigs()

# Environment-based configuration loading
config_file = os.getenv('MONITORING_CONFIG_FILE')
if config_file and os.path.exists(config_file):
    # Load custom configuration logic would go here
    pass

# Export configuration for external use
def get_monitoring_configs() -> MonitoringConfigs:
    """Get the global monitoring configurations instance"""
    return monitoring_configs

def get_metric_config(metric_name: str) -> Optional[MetricConfig]:
    """Get metric configuration"""
    return monitoring_configs.get_metric_config(metric_name)

def validate_metric_threshold(metric_name: str, value: float) -> List[AlertRule]:
    """Check if metric value triggers alerts"""
    return monitoring_configs.validate_metric_threshold(metric_name, value)

def get_dashboard_metrics(dashboard_name: str) -> List[str]:
    """Get metrics for a dashboard"""
    dashboard = monitoring_configs.get_dashboard_config(dashboard_name)
    return dashboard.metrics if dashboard else []

def get_prometheus_config() -> Dict[str, Any]:
    """Get Prometheus-compatible configuration"""
    return monitoring_configs.generate_prometheus_config()