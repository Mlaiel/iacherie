"""Monitoring Configuration Module - Consolidated Monitoring Configs
import logging

================================================================

Consolidates all monitoring-related configurations from:
- config/monitoring/ (24 files)
- config/logging/ (16 files)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import os

# ===== LOGGING CONFIGURATION =====

class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogFormat(str, Enum):
    """Log formats"""
    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"
    COMPACT = "compact"

@dataclass
class LoggerConfig:
    """Individual logger configuration"""
    name: str
    level: LogLevel = LogLevel.INFO
    handlers: List[str] = field(default_factory=lambda: ["console"])
    propagate: bool = True
    filters: List[str] = field(default_factory=list)

@dataclass
class LogHandlerConfig:
    """Log handler configuration"""
    name: str
    handler_type: str  # console, file, rotating_file, syslog, http
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.TEXT
    filename: Optional[str] = None
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    encoding: str = "utf-8"

@dataclass
class LoggingConfig:
    """Logging configuration"""
    version: int = 1
    disable_existing_loggers: bool = False
    root_level: LogLevel = LogLevel.INFO
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    handlers: List[LogHandlerConfig] = field(default_factory=list)
    loggers: List[LoggerConfig] = field(default_factory=list)
    log_to_file: bool = True
    log_to_console: bool = True
    log_rotation_enabled: bool = True

# ===== METRICS CONFIGURATION =====

class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"

class MetricAggregation(str, Enum):
    """Metric aggregation methods"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"

@dataclass
class MetricDefinition:
    """Metric definition"""
    name: str
    metric_type: MetricType
    description: str
    unit: str = ""
    labels: List[str] = field(default_factory=list)
    aggregation: MetricAggregation = MetricAggregation.AVERAGE
    collection_interval: int = 60  # seconds

@dataclass
class MetricsConfig:
    """Metrics collection configuration"""
    enabled: bool = True
    collection_interval: int = 60  # seconds
    retention_period_days: int = 30
    export_format: str = "prometheus"  # prometheus, influxdb, statsd
    export_endpoint: Optional[str] = None
    custom_metrics: List[MetricDefinition] = field(default_factory=list)
    system_metrics_enabled: bool = True
    application_metrics_enabled: bool = True

# ===== HEALTH CHECKS CONFIGURATION =====

class HealthCheckType(str, Enum):
    """Health check types"""
    HTTP = "http"
    TCP = "tcp"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_SERVICE = "external_service"
    CUSTOM = "custom"

@dataclass
class HealthCheck:
    """Individual health check configuration"""
    name: str
    check_type: HealthCheckType
    endpoint: Optional[str] = None
    timeout_seconds: int = 5
    interval_seconds: int = 30
    failure_threshold: int = 3
    success_threshold: int = 1
    enabled: bool = True

@dataclass
class HealthChecksConfig:
    """Health checks configuration"""
    enabled: bool = True
    endpoint: str = "/health"
    detailed_endpoint: str = "/health/detailed"
    checks: List[HealthCheck] = field(default_factory=list)
    overall_timeout: int = 30
    include_system_info: bool = True
    include_dependencies: bool = True

# ===== ALERTING CONFIGURATION =====

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel(str, Enum):
    """Alert notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    DISCORD = "discord"

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    description: str
    metric_name: str
    condition: str  # >, <, >=, <=, ==, !=
    threshold: float
    duration_minutes: int = 5
    severity: AlertSeverity = AlertSeverity.WARNING
    channels: List[AlertChannel] = field(default_factory=lambda: [AlertChannel.EMAIL])
    enabled: bool = True
    runbook_url: Optional[str] = None

@dataclass
class AlertingConfig:
    """Alerting configuration"""
    enabled: bool = True
    rules: List[AlertRule] = field(default_factory=list)
    default_channels: List[AlertChannel] = field(default_factory=lambda: [AlertChannel.EMAIL])
    notification_cooldown_minutes: int = 60
    escalation_enabled: bool = True
    escalation_delay_minutes: int = 30

# ===== PROMETHEUS CONFIGURATION =====

@dataclass
class PrometheusConfig:
    """Prometheus monitoring configuration"""
    enabled: bool = True
    endpoint: str = "/metrics"
    port: int = 9090
    scrape_interval: int = 15  # seconds
    retention_days: int = 15
    storage_path: str = "/var/lib/prometheus"
    external_labels: Dict[str, str] = field(default_factory=dict)
    remote_write_enabled: bool = False
    remote_write_url: Optional[str] = None

# ===== GRAFANA CONFIGURATION =====

@dataclass
class GrafanaConfig:
    """Grafana dashboard configuration"""
    enabled: bool = True
    port: int = 3000
    admin_user: str = "admin"
    admin_password: str = "admin"
    datasource_url: str = "http://prometheus:9090"
    dashboard_provisioning: bool = True
    dashboard_path: str = "/var/lib/grafana/dashboards"
    plugins: List[str] = field(default_factory=list)

# ===== DISTRIBUTED TRACING CONFIGURATION =====

class TracingBackend(str, Enum):
    """Tracing backends"""
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    DATADOG = "datadog"
    NEW_RELIC = "newrelic"
    ELASTIC_APM = "elastic_apm"

@dataclass
class TracingConfig:
    """Distributed tracing configuration"""
    enabled: bool = True
    backend: TracingBackend = TracingBackend.JAEGER
    service_name: str = "ia-influencer-agent"
    sampling_rate: float = 0.1  # 10% sampling
    endpoint: Optional[str] = None
    agent_host: str = "localhost"
    agent_port: int = 6831
    trace_id_header: str = "X-Trace-Id"
    span_id_header: str = "X-Span-Id"

# ===== PERFORMANCE MONITORING =====

@dataclass
class PerformanceConfig:
    """Performance monitoring configuration"""
    enabled: bool = True
    response_time_tracking: bool = True
    database_query_tracking: bool = True
    external_api_tracking: bool = True
    memory_usage_tracking: bool = True
    cpu_usage_tracking: bool = True
    slow_query_threshold_ms: int = 1000
    slow_request_threshold_ms: int = 5000
    profiling_enabled: bool = False

# ===== BUSINESS METRICS CONFIGURATION =====

@dataclass
class BusinessMetricsConfig:
    """Business metrics configuration"""
    enabled: bool = True
    user_registration_tracking: bool = True
    content_upload_tracking: bool = True
    revenue_tracking: bool = True
    conversion_tracking: bool = True
    retention_tracking: bool = True
    engagement_tracking: bool = True
    custom_events: List[str] = field(default_factory=list)

# ===== SECURITY MONITORING =====

@dataclass
class SecurityMonitoringConfig:
    """Security monitoring configuration"""
    enabled: bool = True
    failed_login_tracking: bool = True
    suspicious_activity_detection: bool = True
    data_access_logging: bool = True
    privilege_escalation_detection: bool = True
    anomaly_detection: bool = True
    threat_intelligence_integration: bool = False
    security_alerts_enabled: bool = True

# ===== ENVIRONMENT-SPECIFIC CONFIGURATIONS =====

def get_development_monitoring_config() -> Dict[str, Any]:
    """Get development monitoring configuration"""
    return {
        "logging": LoggingConfig(
            root_level=LogLevel.DEBUG,
            log_to_console=True,
            log_to_file=False
        ),
        "metrics": MetricsConfig(
            enabled=True,
            collection_interval=30,
            retention_period_days=7
        ),
        "health_checks": HealthChecksConfig(
            enabled=True,
            include_system_info=True
        ),
        "alerting": AlertingConfig(
            enabled=False  # Disable alerts in dev
        ),
        "prometheus": PrometheusConfig(
            enabled=False
        ),
        "grafana": GrafanaConfig(
            enabled=False
        ),
        "tracing": TracingConfig(
            enabled=False
        ),
        "performance": PerformanceConfig(
            enabled=True,
            profiling_enabled=True
        )
    }

def get_production_monitoring_config() -> Dict[str, Any]:
    """Get production monitoring configuration"""
    return {
        "logging": LoggingConfig(
            root_level=LogLevel.INFO,
            log_to_console=False,
            log_to_file=True,
            log_rotation_enabled=True
        ),
        "metrics": MetricsConfig(
            enabled=True,
            collection_interval=60,
            retention_period_days=90
        ),
        "health_checks": HealthChecksConfig(
            enabled=True,
            include_system_info=False  # Don't expose system info in prod
        ),
        "alerting": AlertingConfig(
            enabled=True,
            escalation_enabled=True
        ),
        "prometheus": PrometheusConfig(
            enabled=True,
            retention_days=30
        ),
        "grafana": GrafanaConfig(
            enabled=True,
            admin_password=os.getenv("GRAFANA_ADMIN_PASSWORD", "change-me")
        ),
        "tracing": TracingConfig(
            enabled=True,
            sampling_rate=0.05  # 5% sampling in production
        ),
        "performance": PerformanceConfig(
            enabled=True,
            profiling_enabled=False
        )
    }

def get_testing_monitoring_config() -> Dict[str, Any]:
    """Get testing monitoring configuration"""
    return {
        "logging": LoggingConfig(
            root_level=LogLevel.WARNING,
            log_to_console=False,
            log_to_file=False
        ),
        "metrics": MetricsConfig(
            enabled=False
        ),
        "health_checks": HealthChecksConfig(
            enabled=False
        ),
        "alerting": AlertingConfig(
            enabled=False
        ),
        "prometheus": PrometheusConfig(
            enabled=False
        ),
        "grafana": GrafanaConfig(
            enabled=False
        ),
        "tracing": TracingConfig(
            enabled=False
        ),
        "performance": PerformanceConfig(
            enabled=False
        )
    }

# ===== MONITORING CONFIGURATION FACTORY =====

class MonitoringConfigurationFactory:
    """Factory for creating monitoring configurations"""
    
    @staticmethod
    def create_config(environment: str = "development") -> Dict[str, Any]:
        """Create monitoring configuration for environment"""
        if environment.lower() == "production":
            return get_production_monitoring_config()
        elif environment.lower() == "testing":
            return get_testing_monitoring_config()
        else:
            return get_development_monitoring_config()

# Export all monitoring configurations
__all__ = [
    # Enums
    "LogLevel",
    "LogFormat",
    "MetricType",
    "MetricAggregation",
    "HealthCheckType",
    "AlertSeverity",
    "AlertChannel",
    "TracingBackend",
    
    # Configuration Classes
    "LoggerConfig",
    "LogHandlerConfig",
    "LoggingConfig",
    "MetricDefinition",
    "MetricsConfig",
    "HealthCheck",
    "HealthChecksConfig",
    "AlertRule",
    "AlertingConfig",
    "PrometheusConfig",
    "GrafanaConfig",
    "TracingConfig",
    "PerformanceConfig",
    "BusinessMetricsConfig",
    "SecurityMonitoringConfig",
    
    # Factory and Functions
    "MonitoringConfigurationFactory",
    "get_development_monitoring_config",
    "get_production_monitoring_config",
    "get_testing_monitoring_config"
]