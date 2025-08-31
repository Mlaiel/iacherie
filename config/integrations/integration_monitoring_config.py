"""Integration Monitoring Configuration Module for IA-Influencer Agent Platform
============================================================================

Professional monitoring configuration for external integrations and services.
Handles health checks, performance metrics, alerting, and service monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission
is strictly prohibited and will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, Any, Optional, List, Union, Callable
from pydantic import BaseSettings, Field, validator
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta


class MonitoringLevel(str, Enum):
    """Monitoring intensity levels."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CRITICAL = "critical"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(str, Enum):
    """Types of metrics to collect."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class HealthStatus(str, Enum):
    """Service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


@dataclass
class HealthCheckConfig:
    """Health check configuration for a service."""
    service_name: str
    endpoint: str
    method: str = "GET"
    timeout: float = 10.0
    interval: int = 60  # seconds
    retries: int = 3
    expected_status: int = 200
    expected_response: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class MetricConfig:
    """Metric collection configuration."""
    name: str
    metric_type: MetricType
    description: str
    unit: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    collection_interval: int = 60  # seconds
    retention_period: int = 86400  # 24 hours
    enabled: bool = True


@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    description: str
    metric_name: str
    condition: str  # e.g., "value > 100", "value < 0.5"
    severity: AlertSeverity
    duration: int = 300  # seconds - how long condition must be true
    cooldown: int = 900  # seconds - minimum time between alerts
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)


class IntegrationMonitoringConfig(BaseSettings):
    """Integration monitoring configuration for external services."""
    
    # === GENERAL MONITORING SETTINGS ===
    
    # Global monitoring settings
    monitoring_enabled: bool = Field(default=True, env="MONITORING_ENABLED")
    monitoring_level: MonitoringLevel = Field(default=MonitoringLevel.STANDARD, env="MONITORING_LEVEL")
    metrics_retention_days: int = Field(default=30, env="METRICS_RETENTION_DAYS")
    
    # Collection intervals (in seconds)
    default_collection_interval: int = Field(default=60, env="DEFAULT_COLLECTION_INTERVAL")
    high_frequency_interval: int = Field(default=15, env="HIGH_FREQUENCY_INTERVAL")
    low_frequency_interval: int = Field(default=300, env="LOW_FREQUENCY_INTERVAL")
    
    # === HEALTH CHECK SETTINGS ===
    
    # Global health check settings
    health_checks_enabled: bool = Field(default=True, env="HEALTH_CHECKS_ENABLED")
    health_check_timeout: float = Field(default=10.0, env="HEALTH_CHECK_TIMEOUT")
    health_check_retries: int = Field(default=3, env="HEALTH_CHECK_RETRIES")
    health_check_interval: int = Field(default=60, env="HEALTH_CHECK_INTERVAL")
    
    # Platform health checks
    spotify_health_check_enabled: bool = Field(default=True, env="SPOTIFY_HEALTH_CHECK_ENABLED")
    spotify_health_endpoint: str = Field(default="https://api.spotify.com/v1/me", env="SPOTIFY_HEALTH_ENDPOINT")
    
    youtube_health_check_enabled: bool = Field(default=True, env="YOUTUBE_HEALTH_CHECK_ENABLED")
    youtube_health_endpoint: str = Field(
        default="https://www.googleapis.com/youtube/v3/channels",
        env="YOUTUBE_HEALTH_ENDPOINT"
    )
    
    instagram_health_check_enabled: bool = Field(default=True, env="INSTAGRAM_HEALTH_CHECK_ENABLED")
    instagram_health_endpoint: str = Field(default="https://graph.instagram.com/me", env="INSTAGRAM_HEALTH_ENDPOINT")
    
    # Infrastructure health checks
    database_health_check_enabled: bool = Field(default=True, env="DATABASE_HEALTH_CHECK_ENABLED")
    redis_health_check_enabled: bool = Field(default=True, env="REDIS_HEALTH_CHECK_ENABLED")
    elasticsearch_health_check_enabled: bool = Field(default=True, env="ELASTICSEARCH_HEALTH_CHECK_ENABLED")
    
    # === METRICS COLLECTION ===
    
    # API metrics
    collect_api_metrics: bool = Field(default=True, env="COLLECT_API_METRICS")
    api_response_time_threshold: float = Field(default=5.0, env="API_RESPONSE_TIME_THRESHOLD")
    api_error_rate_threshold: float = Field(default=0.05, env="API_ERROR_RATE_THRESHOLD")  # 5%
    
    # Performance metrics
    collect_performance_metrics: bool = Field(default=True, env="COLLECT_PERFORMANCE_METRICS")
    cpu_usage_threshold: float = Field(default=80.0, env="CPU_USAGE_THRESHOLD")
    memory_usage_threshold: float = Field(default=85.0, env="MEMORY_USAGE_THRESHOLD")
    disk_usage_threshold: float = Field(default=90.0, env="DISK_USAGE_THRESHOLD")
    
    # Business metrics
    collect_business_metrics: bool = Field(default=True, env="COLLECT_BUSINESS_METRICS")
    track_user_engagement: bool = Field(default=True, env="TRACK_USER_ENGAGEMENT")
    track_content_metrics: bool = Field(default=True, env="TRACK_CONTENT_METRICS")
    track_revenue_metrics: bool = Field(default=True, env="TRACK_REVENUE_METRICS")
    
    # Content protection metrics
    collect_protection_metrics: bool = Field(default=True, env="COLLECT_PROTECTION_METRICS")
    fingerprint_match_threshold: float = Field(default=0.9, env="FINGERPRINT_MATCH_THRESHOLD")
    copyright_violation_threshold: int = Field(default=10, env="COPYRIGHT_VIOLATION_THRESHOLD")
    
    # === ALERTING SETTINGS ===
    
    # Alert configuration
    alerting_enabled: bool = Field(default=True, env="ALERTING_ENABLED")
    alert_cooldown_period: int = Field(default=900, env="ALERT_COOLDOWN_PERIOD")  # 15 minutes
    max_alerts_per_hour: int = Field(default=100, env="MAX_ALERTS_PER_HOUR")
    
    # Alert channels
    email_alerts_enabled: bool = Field(default=True, env="EMAIL_ALERTS_ENABLED")
    slack_alerts_enabled: bool = Field(default=False, env="SLACK_ALERTS_ENABLED")
    webhook_alerts_enabled: bool = Field(default=False, env="WEBHOOK_ALERTS_ENABLED")
    sms_alerts_enabled: bool = Field(default=False, env="SMS_ALERTS_ENABLED")
    
    # Alert recipients
    alert_email_recipients: List[str] = Field(
        default_factory=lambda: ["admin@ia-influencer.com"],
        env="ALERT_EMAIL_RECIPIENTS"
    )
    alert_slack_channel: str = Field(default="#alerts", env="ALERT_SLACK_CHANNEL")
    alert_webhook_url: Optional[str] = Field(default=None, env="ALERT_WEBHOOK_URL")
    
    # === SERVICE-SPECIFIC MONITORING ===
    
    # Spotify monitoring
    monitor_spotify_api: bool = Field(default=True, env="MONITOR_SPOTIFY_API")
    spotify_rate_limit_threshold: float = Field(default=0.8, env="SPOTIFY_RATE_LIMIT_THRESHOLD")  # 80% of limit
    spotify_quota_threshold: float = Field(default=0.9, env="SPOTIFY_QUOTA_THRESHOLD")  # 90% of quota
    
    # YouTube monitoring
    monitor_youtube_api: bool = Field(default=True, env="MONITOR_YOUTUBE_API")
    youtube_quota_threshold: float = Field(default=0.8, env="YOUTUBE_QUOTA_THRESHOLD")
    youtube_upload_error_threshold: float = Field(default=0.1, env="YOUTUBE_UPLOAD_ERROR_THRESHOLD")
    
    # Payment monitoring
    monitor_payment_systems: bool = Field(default=True, env="MONITOR_PAYMENT_SYSTEMS")
    payment_failure_threshold: float = Field(default=0.05, env="PAYMENT_FAILURE_THRESHOLD")  # 5%
    payment_processing_time_threshold: float = Field(default=30.0, env="PAYMENT_PROCESSING_TIME_THRESHOLD")
    
    # Content protection monitoring
    monitor_content_protection: bool = Field(default=True, env="MONITOR_CONTENT_PROTECTION")
    fingerprint_processing_time_threshold: float = Field(default=60.0, env="FINGERPRINT_PROCESSING_TIME_THRESHOLD")
    content_scan_failure_threshold: float = Field(default=0.1, env="CONTENT_SCAN_FAILURE_THRESHOLD")
    
    # === LOGGING AND STORAGE ===
    
    # Metric storage
    metrics_storage_backend: str = Field(default="prometheus", env="METRICS_STORAGE_BACKEND")
    metrics_export_enabled: bool = Field(default=True, env="METRICS_EXPORT_ENABLED")
    metrics_export_interval: int = Field(default=60, env="METRICS_EXPORT_INTERVAL")
    
    # Log aggregation
    log_aggregation_enabled: bool = Field(default=True, env="LOG_AGGREGATION_ENABLED")
    log_level: str = Field(default="INFO", env="MONITORING_LOG_LEVEL")
    structured_logging: bool = Field(default=True, env="STRUCTURED_LOGGING")
    
    # Dashboard settings
    dashboard_enabled: bool = Field(default=True, env="DASHBOARD_ENABLED")
    dashboard_refresh_interval: int = Field(default=30, env="DASHBOARD_REFRESH_INTERVAL")
    dashboard_retention_days: int = Field(default=90, env="DASHBOARD_RETENTION_DAYS")
    
    # === ADVANCED MONITORING ===
    
    # Anomaly detection
    anomaly_detection_enabled: bool = Field(default=False, env="ANOMALY_DETECTION_ENABLED")
    anomaly_detection_sensitivity: float = Field(default=0.8, env="ANOMALY_DETECTION_SENSITIVITY")
    anomaly_detection_window: int = Field(default=3600, env="ANOMALY_DETECTION_WINDOW")  # 1 hour
    
    # Predictive monitoring
    predictive_monitoring_enabled: bool = Field(default=False, env="PREDICTIVE_MONITORING_ENABLED")
    prediction_horizon: int = Field(default=1800, env="PREDICTION_HORIZON")  # 30 minutes
    
    # Distributed tracing
    distributed_tracing_enabled: bool = Field(default=True, env="DISTRIBUTED_TRACING_ENABLED")
    trace_sampling_rate: float = Field(default=0.1, env="TRACE_SAMPLING_RATE")  # 10%
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class MonitoringManager:
    """Integration monitoring manager with comprehensive service monitoring."""
    
    def __init__(self, config: IntegrationMonitoringConfig):
        self.config = config
        self.health_checks: Dict[str, HealthCheckConfig] = {}
        self.metrics: Dict[str, MetricConfig] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.service_status: Dict[str, HealthStatus] = {}
        self._initialize_default_monitoring()
    
    def _initialize_default_monitoring(self):
        """Initialize default monitoring configurations."""
        # Default health checks
        if self.config.spotify_health_check_enabled:
            self.register_health_check(HealthCheckConfig(
                service_name="spotify_api",
                endpoint=self.config.spotify_health_endpoint,
                timeout=self.config.health_check_timeout,
                interval=self.config.health_check_interval
            ))
        
        if self.config.youtube_health_check_enabled:
            self.register_health_check(HealthCheckConfig(
                service_name="youtube_api",
                endpoint=self.config.youtube_health_endpoint,
                timeout=self.config.health_check_timeout,
                interval=self.config.health_check_interval
            ))
        
        # Default metrics
        if self.config.collect_api_metrics:
            self.register_metric(MetricConfig(
                name="api_response_time",
                metric_type=MetricType.HISTOGRAM,
                description="API response time in seconds",
                unit="seconds",
                collection_interval=self.config.default_collection_interval
            ))
            
            self.register_metric(MetricConfig(
                name="api_error_rate",
                metric_type=MetricType.RATE,
                description="API error rate",
                unit="percentage",
                collection_interval=self.config.default_collection_interval
            ))
        
        # Default alert rules
        if self.config.alerting_enabled:
            self.register_alert_rule(AlertRule(
                name="high_api_response_time",
                description="API response time exceeds threshold",
                metric_name="api_response_time",
                condition=f"value > {self.config.api_response_time_threshold}",
                severity=AlertSeverity.WARNING,
                duration=300
            ))
            
            self.register_alert_rule(AlertRule(
                name="high_api_error_rate",
                description="API error rate exceeds threshold",
                metric_name="api_error_rate",
                condition=f"value > {self.config.api_error_rate_threshold}",
                severity=AlertSeverity.ERROR,
                duration=180
            ))
    
    def register_health_check(self, health_check: HealthCheckConfig):
        """Register a health check configuration."""
        self.health_checks[health_check.service_name] = health_check
    
    def register_metric(self, metric: MetricConfig):
        """Register a metric configuration."""
        self.metrics[metric.name] = metric
    
    def register_alert_rule(self, alert_rule: AlertRule):
        """Register an alert rule."""
        self.alert_rules[alert_rule.name] = alert_rule
    
    def get_health_status(self, service_name: str) -> HealthStatus:
        """Get health status for a service."""
        return self.service_status.get(service_name, HealthStatus.UNKNOWN)
    
    def update_health_status(self, service_name: str, status: HealthStatus):
        """Update health status for a service."""
        self.service_status[service_name] = status
    
    def get_all_health_status(self) -> Dict[str, HealthStatus]:
        """Get health status for all monitored services."""
        return self.service_status.copy()
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get monitoring configuration for a service."""
        health_check = self.health_checks.get(service_name)
        related_metrics = [
            metric for metric in self.metrics.values()
            if service_name in metric.tags.get("service", "")
        ]
        related_alerts = [
            alert for alert in self.alert_rules.values()
            if service_name in alert.tags.get("service", "")
        ]
        
        return {
            "service_name": service_name,
            "health_check": health_check,
            "metrics": related_metrics,
            "alert_rules": related_alerts,
            "current_status": self.get_health_status(service_name)
        }
    
    def get_platform_monitoring_config(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific monitoring configuration."""
        monitor_enabled = getattr(self.config, f"monitor_{platform}_api", False)
        health_enabled = getattr(self.config, f"{platform}_health_check_enabled", False)
        
        config = {
            "platform": platform,
            "monitoring_enabled": monitor_enabled,
            "health_check_enabled": health_enabled,
            "monitoring_level": self.config.monitoring_level
        }
        
        # Add platform-specific thresholds
        if platform == "spotify":
            config.update({
                "rate_limit_threshold": self.config.spotify_rate_limit_threshold,
                "quota_threshold": self.config.spotify_quota_threshold
            })
        elif platform == "youtube":
            config.update({
                "quota_threshold": self.config.youtube_quota_threshold,
                "upload_error_threshold": self.config.youtube_upload_error_threshold
            })
        
        return config
    
    def get_alert_configuration(self) -> Dict[str, Any]:
        """Get alerting configuration."""
        return {
            "enabled": self.config.alerting_enabled,
            "cooldown_period": self.config.alert_cooldown_period,
            "max_alerts_per_hour": self.config.max_alerts_per_hour,
            "channels": {
                "email": {
                    "enabled": self.config.email_alerts_enabled,
                    "recipients": self.config.alert_email_recipients
                },
                "slack": {
                    "enabled": self.config.slack_alerts_enabled,
                    "channel": self.config.alert_slack_channel
                },
                "webhook": {
                    "enabled": self.config.webhook_alerts_enabled,
                    "url": self.config.alert_webhook_url
                },
                "sms": {
                    "enabled": self.config.sms_alerts_enabled
                }
            }
        }
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get monitoring system statistics."""
        total_services = len(self.health_checks)
        healthy_services = sum(
            1 for status in self.service_status.values() 
            if status == HealthStatus.HEALTHY
        )
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "degraded_services": sum(
                1 for status in self.service_status.values() 
                if status == HealthStatus.DEGRADED
            ),
            "unhealthy_services": sum(
                1 for status in self.service_status.values() 
                if status == HealthStatus.UNHEALTHY
            ),
            "total_metrics": len(self.metrics),
            "enabled_metrics": sum(1 for metric in self.metrics.values() if metric.enabled),
            "total_alert_rules": len(self.alert_rules),
            "enabled_alert_rules": sum(1 for rule in self.alert_rules.values() if rule.enabled),
            "monitoring_level": self.config.monitoring_level,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0
        }
    
    def is_service_critical(self, service_name: str) -> bool:
        """Check if a service is marked as critical."""
        health_check = self.health_checks.get(service_name)
        if not health_check:
            return False
        
        # Services with payment, authentication, or core functionality are critical
        critical_services = [
            "stripe", "paypal", "authentication", "database", "redis",
            "content_protection", "fingerprint_engine"
        ]
        
        return any(critical in service_name.lower() for critical in critical_services)


# Global integration monitoring configuration instance
integration_monitoring_config = IntegrationMonitoringConfig()
monitoring_manager = MonitoringManager(integration_monitoring_config)
