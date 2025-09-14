"""IA Influencer Agent - Metrics Configuration
import json

Enterprise-grade metrics configuration and settings

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Centralized metrics configuration
- Environment-specific settings
- Multi-tenant metrics isolation
- Performance tuning parameters
- Alert configuration templates
- Dashboard configuration presets
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from backend.core.config import get_settings

settings = get_settings()


class MetricsEnvironment(Enum):
    """
Metrics environment types"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class PrometheusConfig:
    """Prometheus configuration"""
    enabled: bool = True
    port: int = 8000
    pushgateway_url: Optional[str] = None
    scrape_interval: str = "15s"
    evaluation_interval: str = "15s"
    retention_time: str = "30d"
    max_samples: int = 50000000


@dataclass
class GrafanaConfig:
    """Grafana configuration"""
    enabled: bool = True
    url: str = "http://localhost:3000"
    api_key: Optional[str] = None
    organization_id: int = 1
    default_datasource: str = "prometheus"
    dashboard_refresh_interval: str = "30s"


@dataclass
class AlertConfig:
    """Alert configuration"""
    enabled: bool = True
    evaluation_interval: int = 30  # seconds
    notification_channels: List[str] = field(default_factory=list)
    escalation_enabled: bool = True
    silence_duration: int = 3600  # 1 hour
    auto_resolve: bool = True


@dataclass
class MetricsRetentionConfig:
    """
Metrics retention configuration"""
    realtime_retention: int = 300    # 5 minutes
    fast_retention: int = 3600       # 1 hour
    normal_retention: int = 86400    # 24 hours
    slow_retention: int = 604800     # 7 days
    aggregated_retention: int = 2592000  # 30 days


class MetricsConfiguration:
    """
    Centralized metrics configuration manager
    """
    
    def __init__(self, environment -> None: MetricsEnvironment = MetricsEnvironment.PRODUCTION) -> None:
        self.environment = environment
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """
Load configuration based on environment"""
        
        # Prometheus Configuration
        self.prometheus = PrometheusConfig(
            enabled=os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true",
            port=int(os.getenv("PROMETHEUS_PORT", "8000")),
            pushgateway_url=os.getenv("PROMETHEUS_PUSHGATEWAY_URL"),
            scrape_interval=os.getenv("PROMETHEUS_SCRAPE_INTERVAL", "15s"),
            evaluation_interval=os.getenv("PROMETHEUS_EVALUATION_INTERVAL", "15s"),
            retention_time=os.getenv("PROMETHEUS_RETENTION_TIME", "30d"),
            max_samples=int(os.getenv("PROMETHEUS_MAX_SAMPLES", "50000000"))
        )
        
        # Grafana Configuration
        self.grafana = GrafanaConfig(
            enabled=os.getenv("GRAFANA_ENABLED", "true").lower() == "true",
            url=os.getenv("GRAFANA_URL", "http://localhost:3000"),
            api_key=os.getenv("GRAFANA_API_KEY"),
            organization_id=int(os.getenv("GRAFANA_ORG_ID", "1")),
            default_datasource=os.getenv("GRAFANA_DEFAULT_DATASOURCE", "prometheus"),
            dashboard_refresh_interval=os.getenv("GRAFANA_REFRESH_INTERVAL", "30s")
        )
        
        # Alert Configuration
        self.alerts = AlertConfig(
            enabled=os.getenv("ALERTS_ENABLED", "true").lower() == "true",
            evaluation_interval=int(os.getenv("ALERT_EVALUATION_INTERVAL", "30")),
            notification_channels=os.getenv("ALERT_NOTIFICATION_CHANNELS", "").split(",") if os.getenv("ALERT_NOTIFICATION_CHANNELS") else [],
            escalation_enabled=os.getenv("ALERT_ESCALATION_ENABLED", "true").lower() == "true",
            silence_duration=int(os.getenv("ALERT_SILENCE_DURATION", "3600")),
            auto_resolve=os.getenv("ALERT_AUTO_RESOLVE", "true").lower() == "true"
        )
        
        # Retention Configuration
        self.retention = MetricsRetentionConfig(
            realtime_retention=int(os.getenv("METRICS_REALTIME_RETENTION", "300")),
            fast_retention=int(os.getenv("METRICS_FAST_RETENTION", "3600")),
            normal_retention=int(os.getenv("METRICS_NORMAL_RETENTION", "86400")),
            slow_retention=int(os.getenv("METRICS_SLOW_RETENTION", "604800")),
            aggregated_retention=int(os.getenv("METRICS_AGGREGATED_RETENTION", "2592000"))
        )
        
        # Environment-specific adjustments
        if self.environment == MetricsEnvironment.DEVELOPMENT:
            self._apply_development_settings()
        elif self.environment == MetricsEnvironment.STAGING:
            self._apply_staging_settings()
        elif self.environment == MetricsEnvironment.PRODUCTION:
            self._apply_production_settings()
    
    def _apply_development_settings(self) -> None:
        """Apply development environment settings"""
        # Reduced retention for development
        self.retention.realtime_retention = 60      # 1 minute
        self.retention.fast_retention = 300         # 5 minutes
        self.retention.normal_retention = 3600      # 1 hour
        self.retention.slow_retention = 86400       # 1 day
        self.retention.aggregated_retention = 604800  # 7 days
        
        # More frequent evaluation for testing
        self.alerts.evaluation_interval = 10  # 10 seconds
        
        # Lower resource usage
        self.prometheus.max_samples = 1000000  # 1M samples
    
    def _apply_staging_settings(self) -> None:
        """
Apply staging environment settings"""
        # Medium retention for staging
        self.retention.realtime_retention = 180     # 3 minutes
        self.retention.fast_retention = 1800        # 30 minutes
        self.retention.normal_retention = 43200     # 12 hours
        self.retention.slow_retention = 259200      # 3 days
        self.retention.aggregated_retention = 1209600  # 14 days
        
        # Standard evaluation interval
        self.alerts.evaluation_interval = 20  # 20 seconds
        
        # Medium resource usage
        self.prometheus.max_samples = 10000000  # 10M samples
    
    def _apply_production_settings(self) -> None:
        """
Apply production environment settings"""
        # Full retention for production
        # (using default values)
        
        # Ensure critical settings are enabled
        self.alerts.enabled = True
        self.alerts.escalation_enabled = True
        self.prometheus.enabled = True
        self.grafana.enabled = True
    
    def get_metric_retention(self, metric_name: str) -> int:
        """
Get retention period for specific metric"""
        # Business metrics get longer retention
        if any(keyword in metric_name.lower() for keyword in ["revenue", "user", "business"]):
            return self.retention.aggregated_retention
        
        # Performance metrics get standard retention
        elif any(keyword in metric_name.lower() for keyword in ["http", "api", "latency"]):
            return self.retention.normal_retention
        
        # System metrics get shorter retention
        elif any(keyword in metric_name.lower() for keyword in ["cpu", "memory", "disk"]):
            return self.retention.fast_retention
        
        # Default retention
        else:
            return self.retention.normal_retention
    
    def get_alert_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get alert thresholds by environment"""
        base_thresholds = {
            "http_error_rate": {
                "warning": 0.05,   # 5%
                "critical": 0.10   # 10%
            },
            "http_latency_p95": {
                "warning": 1.0,    # 1 second
                "critical": 2.0    # 2 seconds
            },
            "cpu_usage": {
                "warning": 80.0,   # 80%
                "critical": 90.0   # 90%
            },
            "memory_usage": {
                "warning": 80.0,   # 80%
                "critical": 90.0   # 90%
            },
            "disk_usage": {
                "warning": 80.0,   # 80%
                "critical": 90.0   # 90%
            },
            "ai_model_accuracy": {
                "warning": 0.80,   # 80%
                "critical": 0.70   # 70%
            }
        }
        
        # Adjust thresholds by environment
        if self.environment == MetricsEnvironment.DEVELOPMENT:
            # More lenient thresholds for development
            for metric, thresholds in base_thresholds.items():
                if "usage" in metric or "error_rate" in metric:
                    thresholds["warning"] *= 1.2
                    thresholds["critical"] *= 1.2
                elif "accuracy" in metric:
                    thresholds["warning"] *= 0.9
                    thresholds["critical"] *= 0.9
        
        return base_thresholds
    
    def get_dashboard_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get default dashboard configurations"""
        return {
            "application_overview": {
                "title": "Application Overview",
                "description": "High-level application performance metrics",
                "refresh_interval": self.grafana.dashboard_refresh_interval,
                "panels": [
                    {
                        "title": "HTTP Requests Rate",
                        "type": "graph",
                        "metric": "ia_influencer_http_requests_total",
                        "time_range": "1h"
                    },
                    {
                        "title": "Response Time P95",
                        "type": "graph", 
                        "metric": "ia_influencer_http_request_duration_seconds",
                        "time_range": "1h",
                        "aggregation": "percentile_95"
                    },
                    {
                        "title": "Error Rate",
                        "type": "singlestat",
                        "metric": "ia_influencer_http_requests_total",
                        "filter": "status_code=~'5..'",
                        "time_range": "5m"
                    },
                    {
                        "title": "Active Users",
                        "type": "singlestat",
                        "metric": "ia_influencer_active_users",
                        "time_range": "1h"
                    }
                ]
            },
            "infrastructure": {
                "title": "Infrastructure Monitoring",
                "description": "System resources and infrastructure health",
                "refresh_interval": self.grafana.dashboard_refresh_interval,
                "panels": [
                    {
                        "title": "CPU Usage",
                        "type": "graph",
                        "metric": "ia_influencer_system_cpu_usage_percent",
                        "time_range": "1h"
                    },
                    {
                        "title": "Memory Usage", 
                        "type": "graph",
                        "metric": "ia_influencer_system_memory_usage_bytes",
                        "time_range": "1h"
                    },
                    {
                        "title": "Database Connections",
                        "type": "singlestat",
                        "metric": "ia_influencer_database_connections",
                        "time_range": "5m"
                    },
                    {
                        "title": "Cache Hit Rate",
                        "type": "singlestat", 
                        "metric": "ia_influencer_cache_hit_rate",
                        "time_range": "5m"
                    }
                ]
            },
            "ai_models": {
                "title": "AI Model Performance",
                "description": "AI model inference and accuracy metrics",
                "refresh_interval": self.grafana.dashboard_refresh_interval,
                "panels": [
                    {
                        "title": "Model Predictions Rate",
                        "type": "graph",
                        "metric": "ia_influencer_ai_predictions_total",
                        "time_range": "1h"
                    },
                    {
                        "title": "Inference Duration P95",
                        "type": "graph",
                        "metric": "ia_influencer_ai_inference_duration_seconds",
                        "time_range": "1h",
                        "aggregation": "percentile_95"
                    },
                    {
                        "title": "Model Accuracy",
                        "type": "singlestat",
                        "metric": "ia_influencer_ai_model_accuracy",
                        "time_range": "1h"
                    }
                ]
            },
            "content_protection": {
                "title": "Content Protection",
                "description": "Content fingerprinting and protection metrics",
                "refresh_interval": self.grafana.dashboard_refresh_interval,
                "panels": [
                    {
                        "title": "Fingerprints Created",
                        "type": "graph",
                        "metric": "ia_influencer_fingerprints_created_total",
                        "time_range": "1h"
                    },
                    {
                        "title": "Content Matches Detected",
                        "type": "graph",
                        "metric": "ia_influencer_content_matches_total",
                        "time_range": "1h"
                    },
                    {
                        "title": "Processing Duration P95",
                        "type": "graph",
                        "metric": "ia_influencer_fingerprint_processing_seconds",
                        "time_range": "1h",
                        "aggregation": "percentile_95"
                    }
                ]
            },
            "business_metrics": {
                "title": "Business Metrics",
                "description": "Revenue and business performance indicators",
                "refresh_interval": "5m",  # Less frequent updates for business metrics
                "panels": [
                    {
                        "title": "Revenue by Platform",
                        "type": "graph",
                        "metric": "ia_influencer_revenue_tracked_total",
                        "time_range": "24h"
                    },
                    {
                        "title": "Licensing Transactions",
                        "type": "graph", 
                        "metric": "ia_influencer_licensing_transactions_total",
                        "time_range": "24h"
                    },
                    {
                        "title": "Monthly Active Users",
                        "type": "singlestat",
                        "metric": "ia_influencer_active_users",
                        "filter": "time_window='monthly'",
                        "time_range": "30d"
                    }
                ]
            }
        }
    
    def get_notification_channels(self) -> Dict[str, Dict[str, Any]]:
        """Get notification channel configurations"""
        return {
            "email": {
                "type": "email",
                "enabled": os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "true").lower() == "true",
                "smtp_server": os.getenv("SMTP_SERVER", "localhost"),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "username": os.getenv("SMTP_USERNAME"),
                "password": os.getenv("SMTP_PASSWORD"),
                "from_email": os.getenv("ALERT_FROM_EMAIL", "alerts@ia-influencer.com"),
                "to_emails": os.getenv("ALERT_TO_EMAILS", "").split(",") if os.getenv("ALERT_TO_EMAILS") else ["admin@ia-influencer.com"]
            },
            "slack": {
                "type": "slack",
                "enabled": os.getenv("SLACK_NOTIFICATIONS_ENABLED", "false").lower() == "true",
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
                "channel": os.getenv("SLACK_ALERT_CHANNEL", "#alerts"),
                "username": os.getenv("SLACK_BOT_USERNAME", "IA-Influencer-Alerts")
            },
            "webhook": {
                "type": "webhook",
                "enabled": os.getenv("WEBHOOK_NOTIFICATIONS_ENABLED", "false").lower() == "true",
                "url": os.getenv("WEBHOOK_ALERT_URL"),
                "method": os.getenv("WEBHOOK_METHOD", "POST"),
                "headers": json.loads(os.getenv("WEBHOOK_HEADERS", "{}")) if os.getenv("WEBHOOK_HEADERS") else {},
                "timeout": int(os.getenv("WEBHOOK_TIMEOUT", "10"))
            }
        }
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate Prometheus configuration
        if self.prometheus.enabled:
            if not (1000 <= self.prometheus.port <= 65535):
                issues.append(f"Invalid Prometheus port: {self.prometheus.port}")
            
            if self.prometheus.max_samples < 1000000:
                issues.append("Prometheus max_samples too low for production")
        
        # Validate Grafana configuration
        if self.grafana.enabled:
            if not self.grafana.url:
                issues.append("Grafana URL not configured")
            
            if not self.grafana.api_key and self.environment == MetricsEnvironment.PRODUCTION:
                issues.append("Grafana API key not configured for production")
        
        # Validate alerts configuration
        if self.alerts.enabled:
            if not self.alerts.notification_channels:
                issues.append("No notification channels configured for alerts")
            
            if self.alerts.evaluation_interval < 5:
                issues.append("Alert evaluation interval too frequent (< 5 seconds)")
        
        # Validate retention configuration
        if self.retention.realtime_retention > self.retention.fast_retention:
            issues.append("Realtime retention cannot be longer than fast retention")
        
        if self.retention.fast_retention > self.retention.normal_retention:
            issues.append("Fast retention cannot be longer than normal retention")
        
        return issues


# Global configuration instance
def get_metrics_config(environment: MetricsEnvironment = None) -> MetricsConfiguration:
    """Get metrics configuration instance"""
    if environment is None:
        env_name = os.getenv("METRICS_ENVIRONMENT", "production").lower()
        environment = MetricsEnvironment(env_name)
    
    return MetricsConfiguration(environment)
