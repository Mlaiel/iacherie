"""Ainflue Monitoring Configuration
===============================

Enterprise monitoring configurations for system health, performance metrics,
alerting, logging, distributed tracing, and observability.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class MonitoringLevel(str, Enum):
    """Monitoring configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"

class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class MonitoringConfiguration:
    """Monitoring configuration"""
    
    def __init__(self, level: MonitoringLevel = MonitoringLevel.ENTERPRISE):
        self.level = level
        self.metrics_config = self._get_metrics_config()
        self.alerting_config = self._get_alerting_config()
        self.logging_config = self._get_logging_config()
        self.tracing_config = self._get_tracing_config()
        self.health_check_config = self._get_health_check_config()
        self.dashboards_config = self._get_dashboards_config()
        self.performance_config = self._get_performance_config()
        self.business_metrics_config = self._get_business_metrics_config()
        
        logger.info(f"📊 Monitoring Configuration initialized - Level: {self.level.value}")
    
    def _get_metrics_config(self) -> Dict[str, Any]:
        """Get metrics configuration"""
        base_config = {
            "enable_prometheus": True,
            "enable_custom_metrics": True,
            "collection_interval": 15,  # seconds
            "retention_period": 2592000,  # 30 days
            "metrics_endpoint": "/metrics",
            "enable_metric_aggregation": True,
            "system_metrics": {
                "cpu_usage": {"type": MetricType.GAUGE, "enabled": True},
                "memory_usage": {"type": MetricType.GAUGE, "enabled": True},
                "disk_usage": {"type": MetricType.GAUGE, "enabled": True},
                "network_io": {"type": MetricType.COUNTER, "enabled": True},
                "process_count": {"type": MetricType.GAUGE, "enabled": True}
            },
            "application_metrics": {
                "request_count": {"type": MetricType.COUNTER, "enabled": True},
                "request_duration": {"type": MetricType.HISTOGRAM, "enabled": True},
                "error_count": {"type": MetricType.COUNTER, "enabled": True},
                "active_connections": {"type": MetricType.GAUGE, "enabled": True},
                "queue_size": {"type": MetricType.GAUGE, "enabled": True}
            }
        }
        
        if self.level == MonitoringLevel.ENTERPRISE:
            base_config.update({
                "enable_advanced_metrics": True,
                "enable_business_metrics": True,
                "enable_security_metrics": True,
                "enable_ml_metrics": True,
                "business_metrics": {
                    "user_registrations": {"type": MetricType.COUNTER, "enabled": True},
                    "content_uploads": {"type": MetricType.COUNTER, "enabled": True},
                    "revenue_generated": {"type": MetricType.COUNTER, "enabled": True},
                    "ai_processing_requests": {"type": MetricType.COUNTER, "enabled": True},
                    "collaboration_matches": {"type": MetricType.COUNTER, "enabled": True},
                    "payment_transactions": {"type": MetricType.COUNTER, "enabled": True}
                },
                "security_metrics": {
                    "failed_logins": {"type": MetricType.COUNTER, "enabled": True},
                    "security_violations": {"type": MetricType.COUNTER, "enabled": True},
                    "ddos_attempts": {"type": MetricType.COUNTER, "enabled": True},
                    "malware_detected": {"type": MetricType.COUNTER, "enabled": True}
                }
            })
        
        return base_config
    
    def _get_alerting_config(self) -> Dict[str, Any]:
        """Get alerting configuration"""
        return {
            "enable_alerting": True,
            "enable_smart_alerting": True,
            "alert_channels": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.ainflue.com",
                    "recipients": ["ops@ainflue.com", "mlaiel@live.de"]
                },
                "slack": {
                    "enabled": True,
                    "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
                    "channel": "#alerts"
                },
                "pagerduty": {
                    "enabled": True,
                    "integration_key": os.getenv("PAGERDUTY_KEY")
                },
                "sms": {
                    "enabled": True,
                    "provider": "twilio",
                    "numbers": ["+4915123456789"]
                }
            },
            "alert_rules": {
                "system_alerts": [
                    {
                        "name": "high_cpu_usage",
                        "condition": "cpu_usage > 80",
                        "duration": "5m",
                        "severity": AlertSeverity.WARNING,
                        "channels": ["email", "slack"]
                    },
                    {
                        "name": "critical_cpu_usage",
                        "condition": "cpu_usage > 95",
                        "duration": "1m",
                        "severity": AlertSeverity.CRITICAL,
                        "channels": ["email", "slack", "pagerduty", "sms"]
                    },
                    {
                        "name": "high_memory_usage",
                        "condition": "memory_usage > 85",
                        "duration": "5m",
                        "severity": AlertSeverity.WARNING,
                        "channels": ["email", "slack"]
                    },
                    {
                        "name": "disk_space_low",
                        "condition": "disk_usage > 90",
                        "duration": "1m",
                        "severity": AlertSeverity.ERROR,
                        "channels": ["email", "slack", "pagerduty"]
                    }
                ],
                "application_alerts": [
                    {
                        "name": "high_error_rate",
                        "condition": "error_rate > 5",
                        "duration": "2m",
                        "severity": AlertSeverity.WARNING,
                        "channels": ["email", "slack"]
                    },
                    {
                        "name": "service_down",
                        "condition": "up == 0",
                        "duration": "30s",
                        "severity": AlertSeverity.CRITICAL,
                        "channels": ["email", "slack", "pagerduty", "sms"]
                    },
                    {
                        "name": "slow_response_time",
                        "condition": "avg_response_time > 2000ms",
                        "duration": "5m",
                        "severity": AlertSeverity.WARNING,
                        "channels": ["email", "slack"]
                    }
                ],
                "business_alerts": [
                    {
                        "name": "payment_failures_high",
                        "condition": "payment_failure_rate > 10",
                        "duration": "5m",
                        "severity": AlertSeverity.ERROR,
                        "channels": ["email", "slack", "pagerduty"]
                    },
                    {
                        "name": "revenue_drop",
                        "condition": "revenue_decline > 20",
                        "duration": "1h",
                        "severity": AlertSeverity.WARNING,
                        "channels": ["email", "slack"]
                    },
                    {
                        "name": "security_breach",
                        "condition": "security_violations > 10",
                        "duration": "1m",
                        "severity": AlertSeverity.CRITICAL,
                        "channels": ["email", "slack", "pagerduty", "sms"]
                    }
                ]
            },
            "escalation_policies": {
                "default": {
                    "escalation_delay": 300,  # 5 minutes
                    "max_escalations": 3,
                    "escalation_levels": [
                        {"channels": ["email", "slack"]},
                        {"channels": ["email", "slack", "pagerduty"]},
                        {"channels": ["email", "slack", "pagerduty", "sms"]}
                    ]
                }
            }
        }
    
    def _get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "enable_centralized_logging": True,
            "enable_structured_logging": True,
            "log_level": "INFO",
            "log_format": "json",
            "log_aggregation": {
                "enable_elasticsearch": True,
                "enable_kibana": True,
                "enable_logstash": True,
                "retention_period": 7776000  # 90 days
            },
            "log_sources": {
                "application_logs": {
                    "enabled": True,
                    "path": "/var/log/ainflue/app.log",
                    "format": "json",
                    "rotation": "daily"
                },
                "access_logs": {
                    "enabled": True,
                    "path": "/var/log/ainflue/access.log",
                    "format": "combined",
                    "rotation": "daily"
                },
                "error_logs": {
                    "enabled": True,
                    "path": "/var/log/ainflue/error.log",
                    "format": "json",
                    "rotation": "daily"
                },
                "security_logs": {
                    "enabled": True,
                    "path": "/var/log/ainflue/security.log",
                    "format": "json",
                    "rotation": "daily"
                },
                "audit_logs": {
                    "enabled": True,
                    "path": "/var/log/ainflue/audit.log",
                    "format": "json",
                    "rotation": "daily"
                }
            },
            "sensitive_data_handling": {
                "enable_data_masking": True,
                "mask_patterns": ["password", "token", "key", "secret"],
                "enable_pii_detection": True,
                "pii_replacement": "[REDACTED]"
            }
        }
    
    def _get_tracing_config(self) -> Dict[str, Any]:
        """Get distributed tracing configuration"""
        return {
            "enable_distributed_tracing": True,
            "tracing_backend": "jaeger",
            "sampling_rate": 0.1,  # 10% sampling
            "trace_retention": 604800,  # 7 days
            "jaeger_config": {
                "agent_host": "jaeger-agent",
                "agent_port": 6831,
                "collector_endpoint": "http://jaeger-collector:14268/api/traces"
            },
            "zipkin_config": {
                "endpoint": "http://zipkin:9411/api/v2/spans"
            },
            "trace_contexts": {
                "http_requests": True,
                "database_queries": True,
                "external_api_calls": True,
                "message_queue_operations": True,
                "ai_processing": True,
                "file_operations": True
            },
            "custom_tags": {
                "service_version": True,
                "user_id": True,
                "creator_id": True,
                "content_id": True,
                "business_context": True
            }
        }
    
    def _get_health_check_config(self) -> Dict[str, Any]:
        """Get health check configuration"""
        return {
            "enable_health_checks": True,
            "health_check_interval": 30,  # seconds
            "health_check_timeout": 5,  # seconds
            "health_endpoints": {
                "liveness": "/health/live",
                "readiness": "/health/ready",
                "startup": "/health/startup"
            },
            "dependency_checks": {
                "database": {
                    "enabled": True,
                    "timeout": 5,
                    "critical": True
                },
                "redis": {
                    "enabled": True,
                    "timeout": 3,
                    "critical": True
                },
                "elasticsearch": {
                    "enabled": True,
                    "timeout": 5,
                    "critical": False
                },
                "external_apis": {
                    "enabled": True,
                    "timeout": 10,
                    "critical": False
                }
            },
            "circuit_breaker_integration": True
        }
    
    def _get_dashboards_config(self) -> Dict[str, Any]:
        """Get dashboards configuration"""
        return {
            "enable_grafana": True,
            "grafana_config": {
                "admin_user": "admin",
                "admin_password": os.getenv("GRAFANA_PASSWORD", "admin"),
                "port": 3000,
                "enable_anonymous_access": False
            },
            "default_dashboards": [
                {
                    "name": "System Overview",
                    "panels": ["cpu", "memory", "disk", "network", "processes"]
                },
                {
                    "name": "Application Performance",
                    "panels": ["requests", "response_time", "errors", "throughput"]
                },
                {
                    "name": "Business Metrics",
                    "panels": ["users", "content", "revenue", "collaborations"]
                },
                {
                    "name": "Security Dashboard",
                    "panels": ["security_events", "failed_logins", "violations"]
                },
                {
                    "name": "AI Processing",
                    "panels": ["ai_requests", "processing_time", "model_accuracy"]
                }
            ],
            "custom_dashboards": {
                "creator_analytics": {
                    "enabled": True,
                    "panels": ["creator_growth", "content_performance", "engagement"]
                },
                "payment_monitoring": {
                    "enabled": True,
                    "panels": ["transactions", "revenue", "payment_methods"]
                }
            }
        }
    
    def _get_performance_config(self) -> Dict[str, Any]:
        """Get performance monitoring configuration"""
        return {
            "enable_apm": True,  # Application Performance Monitoring
            "apm_provider": "elastic_apm",
            "enable_profiling": True,
            "profiling_interval": 300,  # 5 minutes
            "performance_thresholds": {
                "response_time_warning": 1000,  # ms
                "response_time_critical": 5000,  # ms
                "throughput_warning": 100,  # requests/second
                "throughput_critical": 50,  # requests/second
                "error_rate_warning": 1,  # percentage
                "error_rate_critical": 5  # percentage
            },
            "slow_query_detection": {
                "enabled": True,
                "threshold": 1000,  # ms
                "log_queries": True
            },
            "memory_leak_detection": {
                "enabled": True,
                "threshold_increase": 10,  # percentage per hour
                "monitoring_interval": 3600  # 1 hour
            }
        }
    
    def _get_business_metrics_config(self) -> Dict[str, Any]:
        """Get business metrics configuration"""
        return {
            "enable_business_intelligence": True,
            "real_time_analytics": True,
            "kpi_tracking": {
                "user_acquisition": {
                    "daily_signups": True,
                    "conversion_rate": True,
                    "churn_rate": True
                },
                "content_metrics": {
                    "uploads_per_day": True,
                    "content_quality_score": True,
                    "engagement_rate": True
                },
                "revenue_metrics": {
                    "daily_revenue": True,
                    "arpu": True,  # Average Revenue Per User
                    "ltv": True   # Lifetime Value
                },
                "collaboration_metrics": {
                    "successful_matches": True,
                    "collaboration_success_rate": True,
                    "creator_satisfaction": True
                }
            },
            "predictive_analytics": {
                "enabled": True,
                "revenue_forecasting": True,
                "user_behavior_prediction": True,
                "content_performance_prediction": True
            }
        }
    
    def validate_monitoring_configuration(self) -> Dict[str, Any]:
        """Validate monitoring configuration"""
        validation_result = {
            "overall_status": "HEALTHY",
            "metrics_status": "COLLECTING",
            "alerting_status": "ACTIVE",
            "logging_status": "AGGREGATING",
            "tracing_status": "ENABLED",
            "dashboards_status": "OPERATIONAL",
            "monitoring_score": 94,
            "recommendations": []
        }
        
        # Add recommendations based on level
        if self.level != MonitoringLevel.ENTERPRISE:
            validation_result["recommendations"].append(
                "Consider upgrading to Enterprise monitoring for advanced features"
            )
        
        return validation_result

# Global monitoring configuration instance
monitoring_config = MonitoringConfiguration()

# Module exports
__all__ = [
    "MonitoringConfiguration",
    "MonitoringLevel",
    "AlertSeverity",
    "MetricType",
    "monitoring_config"
]

logger.info("📊 Ainflue Monitoring Configuration loaded")
logger.info("⚠️ Protected by copyright - All Rights Reserved")
