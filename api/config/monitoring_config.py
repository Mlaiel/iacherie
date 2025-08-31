"""
Monitoring Configuration - IA Influencer Agent Platform
Comprehensive monitoring and observability configuration

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class MetricType(Enum):
    """Types of metrics to collect"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class PrometheusConfig:
    """Prometheus monitoring configuration"""
    
    enabled: bool = field(default_factory=lambda: 
        os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true")
    host: str = field(default_factory=lambda: os.getenv("PROMETHEUS_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("PROMETHEUS_PORT", "9090")))
    metrics_path: str = field(default_factory=lambda: os.getenv("PROMETHEUS_METRICS_PATH", "/metrics"))
    scrape_interval: str = field(default_factory=lambda: os.getenv("PROMETHEUS_SCRAPE_INTERVAL", "15s"))
    evaluation_interval: str = field(default_factory=lambda: os.getenv("PROMETHEUS_EVALUATION_INTERVAL", "15s"))
    retention_time: str = field(default_factory=lambda: os.getenv("PROMETHEUS_RETENTION", "15d"))
    storage_path: str = field(default_factory=lambda: os.getenv("PROMETHEUS_STORAGE_PATH", "/data/prometheus"))
    
    # Authentication
    basic_auth_username: Optional[str] = field(default_factory=lambda: os.getenv("PROMETHEUS_USERNAME"))
    basic_auth_password: Optional[str] = field(default_factory=lambda: os.getenv("PROMETHEUS_PASSWORD"))
    
    # Remote storage configuration
    remote_write_enabled: bool = field(default_factory=lambda: 
        os.getenv("PROMETHEUS_REMOTE_WRITE_ENABLED", "false").lower() == "true")
    remote_write_url: Optional[str] = field(default_factory=lambda: os.getenv("PROMETHEUS_REMOTE_WRITE_URL"))
    
    # Alertmanager integration
    alertmanager_enabled: bool = field(default_factory=lambda: 
        os.getenv("ALERTMANAGER_ENABLED", "true").lower() == "true")
    alertmanager_url: str = field(default_factory=lambda: 
        os.getenv("ALERTMANAGER_URL", "http://localhost:9093"))
    
    @property
    def url(self) -> str:
        """Get Prometheus URL"""



        return f"http://{self.host}:{self.port}"


@dataclass
class GrafanaConfig:
    """Grafana dashboard configuration"""
    
    enabled: bool = field(default_factory=lambda: 
        os.getenv("GRAFANA_ENABLED", "true").lower() == "true")
    host: str = field(default_factory=lambda: os.getenv("GRAFANA_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("GRAFANA_PORT", "3000")))
    admin_username: str = field(default_factory=lambda: os.getenv("GRAFANA_ADMIN_USERNAME", "admin"))
    admin_password: str = field(default_factory=lambda: os.getenv("GRAFANA_ADMIN_PASSWORD", "admin"))
    
    # Database configuration
    database_type: str = field(default_factory=lambda: os.getenv("GRAFANA_DB_TYPE", "sqlite3"))
    database_path: str = field(default_factory=lambda: os.getenv("GRAFANA_DB_PATH", "/data/grafana/grafana.db"))
    
    # Security settings
    secret_key: str = field(default_factory=lambda: os.getenv("GRAFANA_SECRET_KEY", "SW2YcwTIb9zpOOhoPsMm"))
    cookie_secure: bool = field(default_factory=lambda: 
        os.getenv("GRAFANA_COOKIE_SECURE", "false").lower() == "true")
    
    # SMTP configuration for alerts
    smtp_enabled: bool = field(default_factory=lambda: 
        os.getenv("GRAFANA_SMTP_ENABLED", "false").lower() == "true")
    smtp_host: Optional[str] = field(default_factory=lambda: os.getenv("GRAFANA_SMTP_HOST"))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("GRAFANA_SMTP_PORT", "587")))
    smtp_username: Optional[str] = field(default_factory=lambda: os.getenv("GRAFANA_SMTP_USERNAME"))
    smtp_password: Optional[str] = field(default_factory=lambda: os.getenv("GRAFANA_SMTP_PASSWORD"))
    smtp_from_address: Optional[str] = field(default_factory=lambda: os.getenv("GRAFANA_SMTP_FROM_ADDRESS"))
    
    @property
    def url(self) -> str:
        """Get Grafana URL"""



        return f"http://{self.host}:{self.port}"


@dataclass
class JaegerConfig:
    """Jaeger tracing configuration"""
    
    enabled: bool = field(default_factory=lambda: 
        os.getenv("JAEGER_ENABLED", "true").lower() == "true")
    agent_host: str = field(default_factory=lambda: os.getenv("JAEGER_AGENT_HOST", "localhost"))
    agent_port: int = field(default_factory=lambda: int(os.getenv("JAEGER_AGENT_PORT", "6831")))
    collector_endpoint: str = field(default_factory=lambda: 
        os.getenv("JAEGER_COLLECTOR_ENDPOINT", "http://localhost:14268/api/traces"))
    
    # Sampling configuration
    sampler_type: str = field(default_factory=lambda: os.getenv("JAEGER_SAMPLER_TYPE", "const"))
    sampler_param: float = field(default_factory=lambda: float(os.getenv("JAEGER_SAMPLER_PARAM", "1")))
    
    # Service configuration
    service_name: str = field(default_factory=lambda: 
        os.getenv("JAEGER_SERVICE_NAME", "ia-influencer-agent"))
    service_version: str = field(default_factory=lambda: os.getenv("JAEGER_SERVICE_VERSION", "1.0.0"))
    
    # Performance settings
    max_tag_value_length: int = field(default_factory=lambda: 
        int(os.getenv("JAEGER_MAX_TAG_VALUE_LENGTH", "256")))
    flush_interval: int = field(default_factory=lambda: int(os.getenv("JAEGER_FLUSH_INTERVAL", "1")))
    
    @property
    def agent_endpoint(self) -> str:
        """Get Jaeger agent endpoint"""



        return f"{self.agent_host}:{self.agent_port}"


@dataclass
class ElasticSearchConfig:
    """Elasticsearch configuration for log storage"""
    
    enabled: bool = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_LOGGING_ENABLED", "false").lower() == "true")
    hosts: List[str] = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_HOSTS", "localhost:9200").split(","))
    username: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_USERNAME"))
    password: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_PASSWORD"))
    
    # Index configuration
    index_prefix: str = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_INDEX_PREFIX", "ia-influencer"))
    index_date_format: str = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_INDEX_DATE_FORMAT", "%Y.%m.%d"))
    
    # Performance settings
    bulk_size: int = field(default_factory=lambda: int(os.getenv("ELASTICSEARCH_BULK_SIZE", "100")))
    flush_interval: int = field(default_factory=lambda: int(os.getenv("ELASTICSEARCH_FLUSH_INTERVAL", "1")))
    timeout: int = field(default_factory=lambda: int(os.getenv("ELASTICSEARCH_TIMEOUT", "30")))


@dataclass
class AlertConfig:
    """Alert configuration"""
    
    enabled: bool = field(default_factory=lambda: 
        os.getenv("ALERTS_ENABLED", "true").lower() == "true")
    
    # Webhook configuration
    webhook_enabled: bool = field(default_factory=lambda: 
        os.getenv("ALERT_WEBHOOK_ENABLED", "false").lower() == "true")
    webhook_url: Optional[str] = field(default_factory=lambda: os.getenv("ALERT_WEBHOOK_URL"))
    webhook_timeout: int = field(default_factory=lambda: int(os.getenv("ALERT_WEBHOOK_TIMEOUT", "10")))
    
    # Email configuration
    email_enabled: bool = field(default_factory=lambda: 
        os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true")
    smtp_host: Optional[str] = field(default_factory=lambda: os.getenv("ALERT_SMTP_HOST"))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("ALERT_SMTP_PORT", "587")))
    smtp_username: Optional[str] = field(default_factory=lambda: os.getenv("ALERT_SMTP_USERNAME"))
    smtp_password: Optional[str] = field(default_factory=lambda: os.getenv("ALERT_SMTP_PASSWORD"))
    from_email: Optional[str] = field(default_factory=lambda: os.getenv("ALERT_FROM_EMAIL"))
    to_emails: List[str] = field(default_factory=lambda: 
        os.getenv("ALERT_TO_EMAILS", "").split(",") if os.getenv("ALERT_TO_EMAILS") else [])
    
    # Slack configuration
    slack_enabled: bool = field(default_factory=lambda: 
        os.getenv("ALERT_SLACK_ENABLED", "false").lower() == "true")
    slack_webhook_url: Optional[str] = field(default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL"))
    slack_channel: str = field(default_factory=lambda: os.getenv("SLACK_CHANNEL", "#alerts"))
    
    # Discord configuration
    discord_enabled: bool = field(default_factory=lambda: 
        os.getenv("ALERT_DISCORD_ENABLED", "false").lower() == "true")
    discord_webhook_url: Optional[str] = field(default_factory=lambda: os.getenv("DISCORD_WEBHOOK_URL"))
    
    # Alert thresholds
    cpu_threshold: float = field(default_factory=lambda: float(os.getenv("ALERT_CPU_THRESHOLD", "80.0")))
    memory_threshold: float = field(default_factory=lambda: float(os.getenv("ALERT_MEMORY_THRESHOLD", "85.0")))
    disk_threshold: float = field(default_factory=lambda: float(os.getenv("ALERT_DISK_THRESHOLD", "90.0")))
    error_rate_threshold: float = field(default_factory=lambda: 
        float(os.getenv("ALERT_ERROR_RATE_THRESHOLD", "5.0")))
    response_time_threshold: float = field(default_factory=lambda: 
        float(os.getenv("ALERT_RESPONSE_TIME_THRESHOLD", "2000.0")))  # milliseconds
    
    # Alert intervals
    check_interval: int = field(default_factory=lambda: int(os.getenv("ALERT_CHECK_INTERVAL", "60")))  # seconds
    cooldown_period: int = field(default_factory=lambda: int(os.getenv("ALERT_COOLDOWN_PERIOD", "300")))  # seconds


@dataclass
class MonitoringConfig:
    """Comprehensive monitoring configuration"""
    
    # Enable/disable monitoring
    enabled: bool = field(default_factory=lambda: 
        os.getenv("MONITORING_ENABLED", "true").lower() == "true")
    
    # Service discovery
    service_discovery_enabled: bool = field(default_factory=lambda: 
        os.getenv("SERVICE_DISCOVERY_ENABLED", "true").lower() == "true")
    
    # Component configurations
    prometheus: PrometheusConfig = field(default_factory=PrometheusConfig)
    grafana: GrafanaConfig = field(default_factory=GrafanaConfig)
    jaeger: JaegerConfig = field(default_factory=JaegerConfig)
    elasticsearch: ElasticSearchConfig = field(default_factory=ElasticSearchConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    
    # Application metrics
    collect_system_metrics: bool = field(default_factory=lambda: 
        os.getenv("COLLECT_SYSTEM_METRICS", "true").lower() == "true")
    collect_application_metrics: bool = field(default_factory=lambda: 
        os.getenv("COLLECT_APPLICATION_METRICS", "true").lower() == "true")
    collect_business_metrics: bool = field(default_factory=lambda: 
        os.getenv("COLLECT_BUSINESS_METRICS", "true").lower() == "true")
    collect_security_metrics: bool = field(default_factory=lambda: 
        os.getenv("COLLECT_SECURITY_METRICS", "true").lower() == "true")
    
    # Metric collection intervals
    system_metrics_interval: int = field(default_factory=lambda: 
        int(os.getenv("SYSTEM_METRICS_INTERVAL", "15")))  # seconds
    application_metrics_interval: int = field(default_factory=lambda: 
        int(os.getenv("APPLICATION_METRICS_INTERVAL", "30")))  # seconds
    business_metrics_interval: int = field(default_factory=lambda: 
        int(os.getenv("BUSINESS_METRICS_INTERVAL", "60")))  # seconds
    
    # Health check configuration
    health_check_enabled: bool = field(default_factory=lambda: 
        os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true")
    health_check_interval: int = field(default_factory=lambda: 
        int(os.getenv("HEALTH_CHECK_INTERVAL", "30")))  # seconds
    health_check_timeout: int = field(default_factory=lambda: 
        int(os.getenv("HEALTH_CHECK_TIMEOUT", "10")))  # seconds
    
    # Performance monitoring
    performance_monitoring_enabled: bool = field(default_factory=lambda: 
        os.getenv("PERFORMANCE_MONITORING_ENABLED", "true").lower() == "true")
    slow_query_threshold: float = field(default_factory=lambda: 
        float(os.getenv("SLOW_QUERY_THRESHOLD", "1.0")))  # seconds
    api_response_time_threshold: float = field(default_factory=lambda: 
        float(os.getenv("API_RESPONSE_TIME_THRESHOLD", "2.0")))  # seconds
    
    # Security monitoring
    security_monitoring_enabled: bool = field(default_factory=lambda: 
        os.getenv("SECURITY_MONITORING_ENABLED", "true").lower() == "true")
    failed_login_threshold: int = field(default_factory=lambda: 
        int(os.getenv("FAILED_LOGIN_THRESHOLD", "5")))
    suspicious_activity_detection: bool = field(default_factory=lambda: 
        os.getenv("SUSPICIOUS_ACTIVITY_DETECTION", "true").lower() == "true")
    
    # Business monitoring
    business_monitoring_enabled: bool = field(default_factory=lambda: 
        os.getenv("BUSINESS_MONITORING_ENABLED", "true").lower() == "true")
    track_user_engagement: bool = field(default_factory=lambda: 
        os.getenv("TRACK_USER_ENGAGEMENT", "true").lower() == "true")
    track_content_protection: bool = field(default_factory=lambda: 
        os.getenv("TRACK_CONTENT_PROTECTION", "true").lower() == "true")
    track_revenue_metrics: bool = field(default_factory=lambda: 
        os.getenv("TRACK_REVENUE_METRICS", "true").lower() == "true")
    
    # Data retention
    metrics_retention_days: int = field(default_factory=lambda: 
        int(os.getenv("METRICS_RETENTION_DAYS", "30")))
    logs_retention_days: int = field(default_factory=lambda: 
        int(os.getenv("LOGS_RETENTION_DAYS", "7")))
    traces_retention_days: int = field(default_factory=lambda: 
        int(os.getenv("TRACES_RETENTION_DAYS", "7")))
    
    # Dashboard configuration
    default_dashboards: List[str] = field(default_factory=lambda: [
        "system-overview",
        "application-metrics",
        "business-metrics",
        "security-dashboard",
        "performance-dashboard"
    ])
    
    # Custom metrics configuration
    custom_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize monitoring configuration"""
        self._initialize_custom_metrics()
        self._validate_configuration()
    
    def _initialize_custom_metrics(self):
        """Initialize custom business metrics"""
        self.custom_metrics = {
            "content_uploads_total": {
                "type": MetricType.COUNTER,
                "description": "Total number of content uploads",
                "labels": ["content_type", "user_id"]
            },
            "fingerprint_matches_total": {
                "type": MetricType.COUNTER,
                "description": "Total number of fingerprint matches found",
                "labels": ["content_type", "similarity_score_range"]
            },
            "protection_alerts_total": {
                "type": MetricType.COUNTER,
                "description": "Total number of protection alerts sent",
                "labels": ["platform", "severity"]
            },
            "revenue_generated": {
                "type": MetricType.GAUGE,
                "description": "Total revenue generated from platform",
                "labels": ["currency", "user_type"]
            },
            "api_request_duration": {
                "type": MetricType.HISTOGRAM,
                "description": "API request duration in seconds",
                "labels": ["endpoint", "method", "status_code"],
                "buckets": [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            },
            "active_users": {
                "type": MetricType.GAUGE,
                "description": "Number of active users",
                "labels": ["time_period"]
            },
            "database_connections": {
                "type": MetricType.GAUGE,
                "description": "Number of active database connections",
                "labels": ["database_type"]
            },
            "cache_hit_rate": {
                "type": MetricType.GAUGE,
                "description": "Cache hit rate percentage",
                "labels": ["cache_type"]
            },
            "queue_size": {
                "type": MetricType.GAUGE,
                "description": "Size of processing queues",
                "labels": ["queue_name", "priority"]
            },
            "ml_model_accuracy": {
                "type": MetricType.GAUGE,
                "description": "ML model accuracy scores",
                "labels": ["model_name", "model_version"]
            }
        }
    
    def _validate_configuration(self):
        """Validate monitoring configuration"""
        if self.enabled and not (self.prometheus.enabled or self.grafana.enabled):
            raise ValueError("At least one monitoring component must be enabled")
        
        if self.alerts.enabled and not any([
            self.alerts.email_enabled,
            self.alerts.slack_enabled,
            self.alerts.discord_enabled,
            self.alerts.webhook_enabled
        ]):
            raise ValueError("At least one alert channel must be enabled when alerts are enabled")
        
        if self.system_metrics_interval < 5:
            raise ValueError("System metrics interval must be at least 5 seconds")
    
    def get_prometheus_config(self) -> Dict[str, Any]:
        """Get Prometheus configuration dictionary"""



        return {
            "global": {
                "scrape_interval": self.prometheus.scrape_interval,
                "evaluation_interval": self.prometheus.evaluation_interval
            },
            "scrape_configs": [
                {
                    "job_name": "ia-influencer-agent",
                    "static_configs": [
                        {"targets": [f"{self.prometheus.host}:{self.prometheus.port}"]}
                    ]
                }
            ],
            "alerting": {
                "alertmanagers": [
                    {"static_configs": [{"targets": [self.prometheus.alertmanager_url]}]}
                ] if self.prometheus.alertmanager_enabled else []
            }
        }
    
    def get_grafana_datasources(self) -> List[Dict[str, Any]]:
        """Get Grafana datasource configurations"""
        datasources = []
        
        if self.prometheus.enabled:
            datasources.append({
                "name": "Prometheus",
                "type": "prometheus",
                "url": self.prometheus.url,
                "access": "proxy",
                "isDefault": True
            })
        
        if self.elasticsearch.enabled:
            datasources.append({
                "name": "Elasticsearch",
                "type": "elasticsearch",
                "url": f"http://{self.elasticsearch.hosts[0]}",
                "access": "proxy",
                "database": f"{self.elasticsearch.index_prefix}-*",
                "interval": "Daily"
            })
        
        return datasources
    
    def get_jaeger_config(self) -> Dict[str, Any]:
        """Get Jaeger tracer configuration"""



        return {
            "service_name": self.jaeger.service_name,
            "config": {
                "sampler": {
                    "type": self.jaeger.sampler_type,
                    "param": self.jaeger.sampler_param
                },
                "local_agent": {
                    "reporting_host": self.jaeger.agent_host,
                    "reporting_port": self.jaeger.agent_port
                },
                "logging": True
            }
        }
    
    def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get Prometheus alert rules"""



        return [
            {
                "alert": "HighCPUUsage",
                "expr": f"cpu_usage_percent > {self.alerts.cpu_threshold}",
                "for": "5m",
                "labels": {"severity": "warning"},
                "annotations": {
                    "summary": "High CPU usage detected",
                    "description": "CPU usage is above {{ $value }}%"
                }
            },
            {
                "alert": "HighMemoryUsage",
                "expr": f"memory_usage_percent > {self.alerts.memory_threshold}",
                "for": "5m",
                "labels": {"severity": "warning"},
                "annotations": {
                    "summary": "High memory usage detected",
                    "description": "Memory usage is above {{ $value }}%"
                }
            },
            {
                "alert": "HighDiskUsage",
                "expr": f"disk_usage_percent > {self.alerts.disk_threshold}",
                "for": "10m",
                "labels": {"severity": "critical"},
                "annotations": {
                    "summary": "High disk usage detected",
                    "description": "Disk usage is above {{ $value }}%"
                }
            },
            {
                "alert": "HighErrorRate",
                "expr": f"error_rate_percent > {self.alerts.error_rate_threshold}",
                "for": "5m",
                "labels": {"severity": "critical"},
                "annotations": {
                    "summary": "High error rate detected",
                    "description": "Error rate is above {{ $value }}%"
                }
            },
            {
                "alert": "SlowResponseTime",
                "expr": f"avg_response_time_ms > {self.alerts.response_time_threshold}",
                "for": "5m",
                "labels": {"severity": "warning"},
                "annotations": {
                    "summary": "Slow API response time detected",
                    "description": "Average response time is {{ $value }}ms"
                }
            }
        ]
    
    def is_metric_enabled(self, metric_name: str) -> bool:
        """Check if a specific metric is enabled"""



        return metric_name in self.custom_metrics and self.enabled
