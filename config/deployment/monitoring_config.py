"""Monitoring and Observability Configuration Module for IA-Influencer Agent Platform
==================================================================================

Professional monitoring, alerting, and observability infrastructure
for enterprise-grade AI-powered content protection platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
import time
import json
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timedelta
import logging
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MetricType(Enum):
    """Metric types"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricDefinition:
    """Metric definition"""    name: str
    type: MetricType
    description: str
    labels: List[str] = field(default_factory=list)
    unit: Optional[str] = None
    buckets: Optional[List[float]] = None


@dataclass
class AlertRule:
    """Alert rule definition"""    name: str
    description: str
    severity: AlertSeverity
    condition: str
    duration: str
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Dashboard definition"""    name: str
    title: str
    description: str
    panels: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class MonitoringConfig:
    """    Professional monitoring and observability configuration for IA-Influencer Agent Platform.
    
    Provides comprehensive monitoring infrastructure:
    - Prometheus metrics collection and storage
    - Grafana dashboards and visualizations
    - AlertManager for intelligent alerting
    - Jaeger distributed tracing
    - ELK Stack for centralized logging
    - Custom application metrics
    - Performance monitoring and profiling
    - Security event monitoring
    - Business metrics and KPIs
    - Multi-cloud monitoring integration
    - Real-time anomaly detection
    - Capacity planning and forecasting
    """    
    def __init__(self, environment: str = "production", cloud_provider: str = "aws"):
        self.environment = environment
        self.cloud_provider = cloud_provider.lower()
        self.project_name = "ia-influencer-agent"
        
        # Monitoring configuration
        self.prometheus_config = self._get_prometheus_config()
        self.grafana_config = self._get_grafana_config()
        self.alertmanager_config = self._get_alertmanager_config()
        self.jaeger_config = self._get_jaeger_config()
        self.elk_config = self._get_elk_config()
        
        # Custom metrics definitions
        self.metrics = self._define_custom_metrics()
        self.alert_rules = self._define_alert_rules()
        self.dashboards = self._define_dashboards()
    
    def _get_prometheus_config(self) -> Dict[str, Any]:
        """Get Prometheus configuration"""        return {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s",
                "external_labels": {
                    "environment": self.environment,
                    "project": self.project_name,
                    "cloud_provider": self.cloud_provider
                }
            },
            "rule_files": [
                "/etc/prometheus/rules/*.yml"
            ],
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
            },
            "scrape_configs": [
                {
                    "job_name": "prometheus",
                    "static_configs": [
                        {
                            "targets": ["localhost:9090"]
                        }
                    ]
                },
                {
                    "job_name": "ia-influencer-api",
                    "kubernetes_sd_configs": [
                        {
                            "role": "endpoints",
                            "namespaces": {
                                "names": [f"{self.project_name}-{self.environment}"]
                            }
                        }
                    ],
                    "relabel_configs": [
                        {
                            "source_labels": ["__meta_kubernetes_service_name"],
                            "action": "keep",
                            "regex": "api-service"
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s"
                },
                {
                    "job_name": "ia-influencer-ai-services",
                    "kubernetes_sd_configs": [
                        {
                            "role": "endpoints",
                            "namespaces": {
                                "names": [f"{self.project_name}-{self.environment}"]
                            }
                        }
                    ],
                    "relabel_configs": [
                        {
                            "source_labels": ["__meta_kubernetes_service_name"],
                            "action": "keep",
                            "regex": "ai-.*-service"
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s"
                },
                {
                    "job_name": "content-protection-engine",
                    "kubernetes_sd_configs": [
                        {
                            "role": "endpoints",
                            "namespaces": {
                                "names": [f"{self.project_name}-{self.environment}"]
                            }
                        }
                    ],
                    "relabel_configs": [
                        {
                            "source_labels": ["__meta_kubernetes_service_name"],
                            "action": "keep",
                            "regex": "content-protection-.*"
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "15s"
                },
                {
                    "job_name": "monetization-engine",
                    "kubernetes_sd_configs": [
                        {
                            "role": "endpoints",
                            "namespaces": {
                                "names": [f"{self.project_name}-{self.environment}"]
                            }
                        }
                    ],
                    "relabel_configs": [
                        {
                            "source_labels": ["__meta_kubernetes_service_name"],
                            "action": "keep",
                            "regex": "monetization-.*"
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "60s"
                },
                {
                    "job_name": "kubernetes-nodes",
                    "kubernetes_sd_configs": [
                        {
                            "role": "node"
                        }
                    ],
                    "relabel_configs": [
                        {
                            "action": "labelmap",
                            "regex": "__meta_kubernetes_node_label_(.+)"
                        }
                    ]
                },
                {
                    "job_name": "kubernetes-pods",
                    "kubernetes_sd_configs": [
                        {
                            "role": "pod"
                        }
                    ],
                    "relabel_configs": [
                        {
                            "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_scrape"],
                            "action": "keep",
                            "regex": "true"
                        },
                        {
                            "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_path"],
                            "action": "replace",
                            "target_label": "__metrics_path__",
                            "regex": "(.+)"
                        },
                        {
                            "source_labels": ["__address__", "__meta_kubernetes_pod_annotation_prometheus_io_port"],
                            "action": "replace",
                            "regex": "([^:]+)(?::[0-9]+)?;([0-9]+)",
                            "replacement": "${1}:${2}",
                            "target_label": "__address__"
                        }
                    ]
                },
                {
                    "job_name": "blackbox-http",
                    "metrics_path": "/probe",
                    "params": {
                        "module": ["http_2xx"]
                    },
                    "static_configs": [
                        {
                            "targets": [
                                f"https://api.{self.project_name}-{self.environment}.com/health",
                                f"https://app.{self.project_name}-{self.environment}.com/health"
                            ]
                        }
                    ],
                    "relabel_configs": [
                        {
                            "source_labels": ["__address__"],
                            "target_label": "__param_target"
                        },
                        {
                            "source_labels": ["__param_target"],
                            "target_label": "instance"
                        },
                        {
                            "target_label": "__address__",
                            "replacement": "blackbox-exporter:9115"
                        }
                    ]
                }
            ]
        }
    
    def _get_grafana_config(self) -> Dict[str, Any]:
        """Get Grafana configuration"""        return {
            "server": {
                "domain": f"monitoring.{self.project_name}-{self.environment}.com",
                "root_url": f"https://monitoring.{self.project_name}-{self.environment}.com",
                "serve_from_sub_path": False
            },
            "database": {
                "type": "postgres",
                "host": "postgres:5432",
                "name": "grafana",
                "user": "grafana",
                "password": "${GRAFANA_DB_PASSWORD}"
            },
            "security": {
                "admin_user": "admin",
                "admin_password": "${GRAFANA_ADMIN_PASSWORD}",
                "secret_key": "${GRAFANA_SECRET_KEY}",
                "disable_gravatar": True,
                "cookie_secure": True,
                "cookie_samesite": "strict",
                "content_security_policy": True
            },
            "auth": {
                "disable_login_form": False,
                "disable_signout_menu": False,
                "oauth_auto_login": False
            },
            "auth.oauth2": {
                "name": "OAuth2",
                "enabled": True,
                "client_id": "${OAUTH2_CLIENT_ID}",
                "client_secret": "${OAUTH2_CLIENT_SECRET}",
                "scopes": "openid profile email",
                "auth_url": "${OAUTH2_AUTH_URL}",
                "token_url": "${OAUTH2_TOKEN_URL}",
                "api_url": "${OAUTH2_API_URL}",
                "allow_sign_up": True,
                "auto_assign_org": True,
                "auto_assign_org_id": 1,
                "auto_assign_org_role": "Viewer"
            },
            "smtp": {
                "enabled": True,
                "host": "${SMTP_HOST}",
                "user": "${SMTP_USER}",
                "password": "${SMTP_PASSWORD}",
                "from_address": f"monitoring@{self.project_name}.com",
                "from_name": "IA-Influencer Agent Monitoring"
            },
            "alerting": {
                "enabled": True,
                "execute_alerts": True,
                "error_or_timeout": "alerting",
                "nodata_or_nullvalues": "no_data",
                "concurrent_render_limit": 5,
                "evaluation_timeout_seconds": 30,
                "notification_timeout_seconds": 30,
                "max_attempts": 3
            },
            "unified_alerting": {
                "enabled": True,
                "disabled_orgs": [],
                "admin_config_poll_interval": "60s",
                "alertmanager_config_poll_interval": "60s",
                "ha_listen_address": "0.0.0.0:9094",
                "ha_advertise_address": "",
                "ha_peers": "",
                "ha_peer_timeout": "15s",
                "ha_gossip_interval": "200ms",
                "ha_push_pull_interval": "60s",
                "max_attempts": 1,
                "min_interval": "10s",
                "execute_alerts": True
            },
            "metrics": {
                "enabled": True,
                "basic_auth_username": "prometheus",
                "basic_auth_password": "${METRICS_BASIC_AUTH_PASSWORD}",
                "disable_total_stats": False
            },
            "tracing": {
                "jaeger": {
                    "address": "jaeger:14268",
                    "always_included_tag": f"environment:{self.environment}",
                    "sampler_type": "const",
                    "sampler_param": 1,
                    "zipkin_propagation": False,
                    "disable_shared_zipkin_spans": False
                }
            }
        }
    
    def _get_alertmanager_config(self) -> Dict[str, Any]:
        """Get AlertManager configuration"""        return {
            "global": {
                "smtp_smarthost": "${SMTP_HOST}:587",
                "smtp_from": f"alerts@{self.project_name}.com",
                "smtp_auth_username": "${SMTP_USER}",
                "smtp_auth_password": "${SMTP_PASSWORD}",
                "slack_api_url": "${SLACK_WEBHOOK_URL}"
            },
            "templates": [
                "/etc/alertmanager/templates/*.tmpl"
            ],
            "route": {
                "group_by": ["alertname", "cluster", "service"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "default",
                "routes": [
                    {
                        "match": {
                            "severity": "critical"
                        },
                        "receiver": "critical-alerts",
                        "group_wait": "10s",
                        "repeat_interval": "5m"
                    },
                    {
                        "match": {
                            "severity": "high"
                        },
                        "receiver": "high-alerts",
                        "group_wait": "30s",
                        "repeat_interval": "15m"
                    },
                    {
                        "match_re": {
                            "service": "content-protection|ai-.*"
                        },
                        "receiver": "ai-team-alerts",
                        "group_wait": "30s",
                        "repeat_interval": "30m"
                    },
                    {
                        "match": {
                            "service": "monetization-engine"
                        },
                        "receiver": "business-alerts",
                        "group_wait": "60s",
                        "repeat_interval": "1h"
                    }
                ]
            },
            "receivers": [
                {
                    "name": "default",
                    "email_configs": [
                        {
                            "to": f"admin@{self.project_name}.com",
                            "subject": "IA-Influencer Agent Alert: {{ .GroupLabels.alertname }}",
                            "body": self._get_email_template()
                        }
                    ]
                },
                {
                    "name": "critical-alerts",
                    "email_configs": [
                        {
                            "to": f"critical@{self.project_name}.com",
                            "subject": "🚨 CRITICAL: IA-Influencer Agent Alert",
                            "body": self._get_email_template()
                        }
                    ],
                    "slack_configs": [
                        {
                            "api_url": "${SLACK_WEBHOOK_URL}",
                            "channel": "#critical-alerts",
                            "title": "🚨 Critical Alert: {{ .GroupLabels.alertname }}",
                            "text": self._get_slack_template(),
                            "color": "danger"
                        }
                    ]
                },
                {
                    "name": "high-alerts",
                    "email_configs": [
                        {
                            "to": f"high-priority@{self.project_name}.com",
                            "subject": "⚠️ HIGH: IA-Influencer Agent Alert",
                            "body": self._get_email_template()
                        }
                    ],
                    "slack_configs": [
                        {
                            "api_url": "${SLACK_WEBHOOK_URL}",
                            "channel": "#high-alerts",
                            "title": "⚠️ High Priority Alert: {{ .GroupLabels.alertname }}",
                            "text": self._get_slack_template(),
                            "color": "warning"
                        }
                    ]
                },
                {
                    "name": "ai-team-alerts",
                    "email_configs": [
                        {
                            "to": f"ai-team@{self.project_name}.com",
                            "subject": "🤖 AI Service Alert: {{ .GroupLabels.alertname }}",
                            "body": self._get_email_template()
                        }
                    ],
                    "slack_configs": [
                        {
                            "api_url": "${SLACK_WEBHOOK_URL}",
                            "channel": "#ai-alerts",
                            "title": "🤖 AI Service Alert: {{ .GroupLabels.alertname }}",
                            "text": self._get_slack_template(),
                            "color": "good"
                        }
                    ]
                },
                {
                    "name": "business-alerts",
                    "email_configs": [
                        {
                            "to": f"business-team@{self.project_name}.com",
                            "subject": "💰 Business Metric Alert: {{ .GroupLabels.alertname }}",
                            "body": self._get_email_template()
                        }
                    ]
                }
            ],
            "inhibit_rules": [
                {
                    "source_match": {
                        "severity": "critical"
                    },
                    "target_match": {
                        "severity": "warning"
                    },
                    "equal": ["alertname", "cluster", "service"]
                }
            ]
        }
    
    def _get_jaeger_config(self) -> Dict[str, Any]:
        """Get Jaeger tracing configuration"""        return {
            "service_name": f"{self.project_name}-{self.environment}",
            "sampler": {
                "type": "probabilistic",
                "param": 1.0 if self.environment == "development" else 0.1
            },
            "logging": True,
            "local_agent": {
                "reporting_host": "jaeger-agent",
                "reporting_port": 6832
            },
            "collector": {
                "endpoint": "http://jaeger-collector:14268/api/traces",
                "username": "${JAEGER_USERNAME}",
                "password": "${JAEGER_PASSWORD}"
            },
            "reporter": {
                "log_spans": True if self.environment == "development" else False,
                "buffer_flush_interval": 1000,
                "queue_size": 100
            },
            "tags": {
                "environment": self.environment,
                "version": "${APP_VERSION}",
                "service": "ia-influencer-agent"
            }
        }
    
    def _get_elk_config(self) -> Dict[str, Any]:
        """Get ELK Stack configuration"""        return {
            "elasticsearch": {
                "cluster.name": f"{self.project_name}-{self.environment}",
                "node.name": "es-master",
                "discovery.type": "single-node" if self.environment == "development" else "zen",
                "cluster.initial_master_nodes": ["es-master"] if self.environment != "development" else None,
                "bootstrap.memory_lock": True,
                "http.cors.enabled": True,
                "http.cors.allow-origin": "*",
                "xpack.security.enabled": True,
                "xpack.security.transport.ssl.enabled": True,
                "xpack.security.http.ssl.enabled": True,
                "xpack.monitoring.enabled": True,
                "action.destructive_requires_name": True,
                "cluster.routing.allocation.disk.threshold_enabled": True,
                "cluster.routing.allocation.disk.watermark.low": "85%",
                "cluster.routing.allocation.disk.watermark.high": "90%",
                "indices.lifecycle.rollover.check_interval": "1m"
            },
            "logstash": {
                "path.data": "/var/lib/logstash",
                "pipeline.workers": 4,
                "pipeline.batch.size": 125,
                "pipeline.batch.delay": 5,
                "http.host": "0.0.0.0",
                "xpack.monitoring.enabled": True,
                "xpack.monitoring.elasticsearch.hosts": ["elasticsearch:9200"],
                "log.level": "info",
                "path.logs": "/var/log/logstash"
            },
            "kibana": {
                "server.host": "0.0.0.0",
                "elasticsearch.hosts": ["http://elasticsearch:9200"],
                "xpack.security.enabled": True,
                "xpack.encryptedSavedObjects.encryptionKey": "${KIBANA_ENCRYPTION_KEY}",
                "xpack.reporting.encryptionKey": "${KIBANA_REPORTING_KEY}",
                "xpack.security.encryptionKey": "${KIBANA_SECURITY_KEY}",
                "server.publicBaseUrl": f"https://logs.{self.project_name}-{self.environment}.com",
                "logging.appenders.file.type": "file",
                "logging.appenders.file.fileName": "/var/log/kibana/kibana.log",
                "logging.appenders.file.layout.type": "json",
                "logging.root.level": "info"
            },
            "filebeat": {
                "filebeat.inputs": [
                    {
                        "type": "kubernetes",
                        "node": "${NODE_NAME}",
                        "hints.enabled": True,
                        "hints.default_config": {
                            "type": "container",
                            "paths": [
                                "/var/log/containers/*${data.kubernetes.container.id}.log"
                            ]
                        }
                    }
                ],
                "processors": [
                    {
                        "add_kubernetes_metadata": {
                            "host": "${NODE_NAME}",
                            "matchers": [
                                {
                                    "logs_path": {
                                        "logs_path": "/var/log/containers/",
                                        "resource_type": "container"
                                    }
                                }
                            ]
                        }
                    }
                ],
                "output.logstash": {
                    "hosts": ["logstash:5044"]
                },
                "setup.kibana": {
                    "host": "kibana:5601"
                }
            }
        }
    
    def _get_email_template(self) -> str:
        """Get email alert template"""        return """Alert: {{ .GroupLabels.alertname }}
Environment: {{ .CommonLabels.environment }}
Severity: {{ .CommonLabels.severity }}

{{ range .Alerts }}
Instance: {{ .Labels.instance }}
Description: {{ .Annotations.description }}
Summary: {{ .Annotations.summary }}
{{ end }}

Dashboard: https://monitoring.{{ .CommonLabels.environment }}.com/d/overview
Runbook: https://docs.{{ .CommonLabels.environment }}.com/runbooks/{{ .GroupLabels.alertname }}

Generated at: {{ .Timestamp }}
"""    
    def _get_slack_template(self) -> str:
        """Get Slack alert template"""        return """{{ range .Alerts }}
*Alert:* {{ .Labels.alertname }}
*Environment:* {{ .Labels.environment }}
*Severity:* {{ .Labels.severity }}
*Instance:* {{ .Labels.instance }}

*Description:* {{ .Annotations.description }}
*Summary:* {{ .Annotations.summary }}

<https://monitoring.{{ .Labels.environment }}.com/d/overview|Dashboard> | <https://docs.{{ .Labels.environment }}.com/runbooks/{{ .Labels.alertname }}|Runbook>
{{ end }}
"""    
    def _define_custom_metrics(self) -> List[MetricDefinition]:
        """Define custom application metrics"""        return [
            # API Metrics
            MetricDefinition(
                name="ia_api_requests_total",
                type=MetricType.COUNTER,
                description="Total number of API requests",
                labels=["method", "endpoint", "status_code"],
                unit="requests"
            ),
            MetricDefinition(
                name="ia_api_request_duration_seconds",
                type=MetricType.HISTOGRAM,
                description="API request duration in seconds",
                labels=["method", "endpoint"],
                unit="seconds",
                buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
            ),
            MetricDefinition(
                name="ia_api_active_connections",
                type=MetricType.GAUGE,
                description="Number of active API connections",
                unit="connections"
            ),
            
            # Content Protection Metrics
            MetricDefinition(
                name="ia_content_fingerprints_generated_total",
                type=MetricType.COUNTER,
                description="Total number of content fingerprints generated",
                labels=["content_type", "format"],
                unit="fingerprints"
            ),
            MetricDefinition(
                name="ia_content_fingerprint_generation_duration_seconds",
                type=MetricType.HISTOGRAM,
                description="Time taken to generate content fingerprints",
                labels=["content_type", "format"],
                unit="seconds",
                buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
            ),
            MetricDefinition(
                name="ia_content_matches_detected_total",
                type=MetricType.COUNTER,
                description="Total number of content matches detected",
                labels=["platform", "content_type", "action"],
                unit="matches"
            ),
            MetricDefinition(
                name="ia_content_protection_rules_active",
                type=MetricType.GAUGE,
                description="Number of active content protection rules",
                labels=["user_id", "content_type"],
                unit="rules"
            ),
            
            # AI/ML Metrics
            MetricDefinition(
                name="ia_ai_model_inference_duration_seconds",
                type=MetricType.HISTOGRAM,
                description="AI model inference time",
                labels=["model_name", "model_version"],
                unit="seconds",
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            ),
            MetricDefinition(
                name="ia_ai_model_accuracy",
                type=MetricType.GAUGE,
                description="AI model accuracy score",
                labels=["model_name", "model_version"],
                unit="score"
            ),
            MetricDefinition(
                name="ia_ai_training_jobs_total",
                type=MetricType.COUNTER,
                description="Total number of AI training jobs",
                labels=["model_type", "status"],
                unit="jobs"
            ),
            
            # Business Metrics
            MetricDefinition(
                name="ia_revenue_generated_total",
                type=MetricType.COUNTER,
                description="Total revenue generated",
                labels=["revenue_type", "currency", "user_id"],
                unit="revenue"
            ),
            MetricDefinition(
                name="ia_active_users",
                type=MetricType.GAUGE,
                description="Number of active users",
                labels=["user_type", "subscription_tier"],
                unit="users"
            ),
            MetricDefinition(
                name="ia_content_uploads_total",
                type=MetricType.COUNTER,
                description="Total content uploads",
                labels=["content_type", "user_tier"],
                unit="uploads"
            ),
            
            # System Metrics
            MetricDefinition(
                name="ia_database_connections_active",
                type=MetricType.GAUGE,
                description="Number of active database connections",
                labels=["database", "pool"],
                unit="connections"
            ),
            MetricDefinition(
                name="ia_cache_hit_rate",
                type=MetricType.GAUGE,
                description="Cache hit rate percentage",
                labels=["cache_name"],
                unit="percentage"
            ),
            MetricDefinition(
                name="ia_queue_size",
                type=MetricType.GAUGE,
                description="Queue size",
                labels=["queue_name"],
                unit="items"
            ),
            MetricDefinition(
                name="ia_storage_usage_bytes",
                type=MetricType.GAUGE,
                description="Storage usage in bytes",
                labels=["storage_type", "bucket"],
                unit="bytes"
            )
        ]
    
    def _define_alert_rules(self) -> List[AlertRule]:
        """Define alert rules"""        return [
            # Critical Alerts
            AlertRule(
                name="HighErrorRate",
                description="High error rate detected",
                severity=AlertSeverity.CRITICAL,
                condition="rate(ia_api_requests_total{status_code=~'5..'}[5m]) > 0.1",
                duration="2m",
                labels={"team": "platform"},
                annotations={
                    "summary": "High error rate on {{ $labels.endpoint }}",
                    "description": "Error rate is {{ $value | humanizePercentage }} on {{ $labels.endpoint }}"
                }
            ),
            AlertRule(
                name="ServiceDown",
                description="Service is down",
                severity=AlertSeverity.CRITICAL,
                condition="up{job=~'ia-influencer-.*'} == 0",
                duration="1m",
                labels={"team": "platform"},
                annotations={
                    "summary": "Service {{ $labels.job }} is down",
                    "description": "Service {{ $labels.job }} on {{ $labels.instance }} has been down for more than 1 minute"
                }
            ),
            AlertRule(
                name="DatabaseConnectionPoolExhausted",
                description="Database connection pool is exhausted",
                severity=AlertSeverity.CRITICAL,
                condition="ia_database_connections_active / ia_database_connections_max > 0.9",
                duration="30s",
                labels={"team": "platform"},
                annotations={
                    "summary": "Database connection pool near exhaustion",
                    "description": "Database {{ $labels.database }} connection pool is {{ $value | humanizePercentage }} full"
                }
            ),
            
            # High Priority Alerts
            AlertRule(
                name="HighResponseTime",
                description="High API response time",
                severity=AlertSeverity.HIGH,
                condition="histogram_quantile(0.95, rate(ia_api_request_duration_seconds_bucket[5m])) > 2",
                duration="5m",
                labels={"team": "platform"},
                annotations={
                    "summary": "High response time on {{ $labels.endpoint }}",
                    "description": "95th percentile response time is {{ $value }}s on {{ $labels.endpoint }}"
                }
            ),
            AlertRule(
                name="ContentProtectionEngineOverloaded",
                description="Content protection engine is overloaded",
                severity=AlertSeverity.HIGH,
                condition="rate(ia_content_fingerprints_generated_total[5m]) > 100",
                duration="10m",
                labels={"team": "ai"},
                annotations={
                    "summary": "Content protection engine overloaded",
                    "description": "Fingerprint generation rate is {{ $value }} per second, exceeding capacity"
                }
            ),
            
            # Medium Priority Alerts
            AlertRule(
                name="LowCacheHitRate",
                description="Low cache hit rate",
                severity=AlertSeverity.MEDIUM,
                condition="ia_cache_hit_rate < 0.7",
                duration="15m",
                labels={"team": "platform"},
                annotations={
                    "summary": "Low cache hit rate for {{ $labels.cache_name }}",
                    "description": "Cache hit rate is {{ $value | humanizePercentage }} for {{ $labels.cache_name }}"
                }
            ),
            AlertRule(
                name="AIModelAccuracyDrop",
                description="AI model accuracy has dropped",
                severity=AlertSeverity.MEDIUM,
                condition="ia_ai_model_accuracy < 0.85",
                duration="30m",
                labels={"team": "ai"},
                annotations={
                    "summary": "AI model accuracy drop for {{ $labels.model_name }}",
                    "description": "Model {{ $labels.model_name }} accuracy is {{ $value | humanizePercentage }}, below threshold"
                }
            ),
            
            # Business Alerts
            AlertRule(
                name="RevenueDropAlert",
                description="Revenue drop detected",
                severity=AlertSeverity.HIGH,
                condition="rate(ia_revenue_generated_total[1h]) < rate(ia_revenue_generated_total[1h] offset 1d) * 0.8",
                duration="1h",
                labels={"team": "business"},
                annotations={
                    "summary": "Revenue drop detected",
                    "description": "Revenue generation rate has dropped by more than 20% compared to yesterday"
                }
            ),
            
            # Infrastructure Alerts
            AlertRule(
                name="KubernetesNodeNotReady",
                description="Kubernetes node is not ready",
                severity=AlertSeverity.CRITICAL,
                condition="kube_node_status_condition{condition='Ready',status='true'} == 0",
                duration="5m",
                labels={"team": "platform"},
                annotations={
                    "summary": "Kubernetes node {{ $labels.node }} is not ready",
                    "description": "Node {{ $labels.node }} has been not ready for more than 5 minutes"
                }
            ),
            AlertRule(
                name="PodCrashLooping",
                description="Pod is crash looping",
                severity=AlertSeverity.HIGH,
                condition="rate(kube_pod_container_status_restarts_total[15m]) * 60 * 15 > 5",
                duration="5m",
                labels={"team": "platform"},
                annotations={
                    "summary": "Pod {{ $labels.pod }} is crash looping",
                    "description": "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is restarting frequently"
                }
            )
        ]
    
    def _define_dashboards(self) -> List[Dashboard]:
        """Define Grafana dashboards"""        return [
            Dashboard(
                name="ia-platform-overview",
                title="IA-Influencer Agent Platform Overview",
                description="High-level overview of platform metrics",
                tags=["overview", "platform"],
                panels=[
                    {
                        "title": "API Request Rate",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "sum(rate(ia_api_requests_total[5m]))",
                                "legendFormat": "Requests/sec"
                            }
                        ]
                    },
                    {
                        "title": "API Response Time",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, sum(rate(ia_api_request_duration_seconds_bucket[5m])) by (le))",
                                "legendFormat": "95th percentile"
                            }
                        ]
                    },
                    {
                        "title": "Error Rate",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "sum(rate(ia_api_requests_total{status_code=~'5..'}[5m])) / sum(rate(ia_api_requests_total[5m]))",
                                "legendFormat": "Error rate"
                            }
                        ]
                    },
                    {
                        "title": "Active Users",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "ia_active_users",
                                "legendFormat": "Users"
                            }
                        ]
                    }
                ]
            ),
            Dashboard(
                name="content-protection",
                title="Content Protection Dashboard",
                description="Content protection and AI monitoring",
                tags=["content-protection", "ai"],
                panels=[
                    {
                        "title": "Fingerprint Generation Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(ia_content_fingerprints_generated_total[5m])",
                                "legendFormat": "{{ content_type }} - {{ format }}"
                            }
                        ]
                    },
                    {
                        "title": "Content Match Detection",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(ia_content_matches_detected_total[5m])",
                                "legendFormat": "{{ platform }} - {{ action }}"
                            }
                        ]
                    },
                    {
                        "title": "AI Model Performance",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "ia_ai_model_accuracy",
                                "legendFormat": "{{ model_name }}"
                            }
                        ]
                    }
                ]
            ),
            Dashboard(
                name="business-metrics",
                title="Business Metrics Dashboard",
                description="Revenue and business KPIs",
                tags=["business", "revenue"],
                panels=[
                    {
                        "title": "Revenue Generation",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(ia_revenue_generated_total[1h])",
                                "legendFormat": "{{ revenue_type }}"
                            }
                        ]
                    },
                    {
                        "title": "User Growth",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "ia_active_users",
                                "legendFormat": "{{ user_type }}"
                            }
                        ]
                    },
                    {
                        "title": "Content Upload Trends",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(ia_content_uploads_total[1h])",
                                "legendFormat": "{{ content_type }}"
                            }
                        ]
                    }
                ]
            ),
            Dashboard(
                name="infrastructure",
                title="Infrastructure Monitoring",
                description="Kubernetes and system monitoring",
                tags=["infrastructure", "kubernetes"],
                panels=[
                    {
                        "title": "Kubernetes Pods Status",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "sum(kube_pod_status_phase{phase='Running'})",
                                "legendFormat": "Running"
                            },
                            {
                                "expr": "sum(kube_pod_status_phase{phase='Failed'})",
                                "legendFormat": "Failed"
                            }
                        ]
                    },
                    {
                        "title": "Database Connections",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "ia_database_connections_active",
                                "legendFormat": "{{ database }} - {{ pool }}"
                            }
                        ]
                    },
                    {
                        "title": "Storage Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "ia_storage_usage_bytes",
                                "legendFormat": "{{ storage_type }} - {{ bucket }}"
                            }
                        ]
                    }
                ]
            )
        ]
    
    def get_docker_compose_monitoring(self) -> str:
        """Get Docker Compose configuration for monitoring stack"""        return f'''version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    restart: unless-stopped
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:10.1.0
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${{GRAFANA_ADMIN_PASSWORD:-admin}}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SMTP_ENABLED=true
      - GF_SMTP_HOST=${{SMTP_HOST}}
      - GF_SMTP_USER=${{SMTP_USER}}
      - GF_SMTP_PASSWORD=${{SMTP_PASSWORD}}
      - GF_SMTP_FROM_ADDRESS=monitoring@{self.project_name}.com
    restart: unless-stopped
    networks:
      - monitoring
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager:v0.25.0
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - ./alertmanager/templates:/etc/alertmanager/templates
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
    restart: unless-stopped
    networks:
      - monitoring

  jaeger:
    image: jaegertracing/all-in-one:1.47
    container_name: jaeger
    ports:
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
    restart: unless-stopped
    networks:
      - monitoring
    depends_on:
      - elasticsearch

  elasticsearch:
    image: elasticsearch:8.8.0
    container_name: elasticsearch
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    restart: unless-stopped
    networks:
      - monitoring

  kibana:
    image: kibana:8.8.0
    container_name: kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - XPACK_SECURITY_ENABLED=false
    restart: unless-stopped
    networks:
      - monitoring
    depends_on:
      - elasticsearch

  logstash:
    image: logstash:8.8.0
    container_name: logstash
    ports:
      - "5044:5044"
      - "9600:9600"
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
      - ./logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml
    environment:
      - "LS_JAVA_OPTS=-Xmx1g -Xms1g"
    restart: unless-stopped
    networks:
      - monitoring
    depends_on:
      - elasticsearch

  blackbox-exporter:
    image: prom/blackbox-exporter:v0.24.0
    container_name: blackbox-exporter
    ports:
      - "9115:9115"
    volumes:
      - ./blackbox/blackbox.yml:/etc/blackbox_exporter/config.yml
    restart: unless-stopped
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:v1.6.0
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.47.0
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    devices:
      - /dev/kmsg
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:
  elasticsearch_data:

networks:
  monitoring:
    driver: bridge
    external: false
'''
    
    def get_kubernetes_monitoring_manifests(self) -> Dict[str, str]:
        """Get Kubernetes manifests for monitoring stack"""        return {
            "namespace.yaml": f'''
apiVersion: v1
kind: Namespace
metadata:
  name: {self.project_name}-monitoring
  labels:
    name: monitoring
    environment: {self.environment}
''',
            "prometheus-deployment.yaml": f'''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: {self.project_name}-monitoring
  labels:
    app: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.45.0
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus/prometheus.yml
          subPath: prometheus.yml
        - name: rules
          mountPath: /etc/prometheus/rules
        - name: storage
          mountPath: /prometheus
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi" 
            cpu: "2"
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: rules
        configMap:
          name: prometheus-rules
      - name: storage
        persistentVolumeClaim:
          claimName: prometheus-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: {self.project_name}-monitoring
  labels:
    app: prometheus
spec:
  ports:
  - port: 9090
    targetPort: 9090
    name: web
  selector:
    app: prometheus
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prometheus-pvc
  namespace: {self.project_name}-monitoring
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
''',
            "grafana-deployment.yaml": f'''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: {self.project_name}-monitoring
  labels:
    app: grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:10.1.0
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-secrets
              key: admin-password
        volumeMounts:
        - name: storage
          mountPath: /var/lib/grafana
        - name: config
          mountPath: /etc/grafana/provisioning
        resources:
          requests:
            memory: "1Gi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1"
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: grafana-pvc
      - name: config
        configMap:
          name: grafana-config
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: {self.project_name}-monitoring
  labels:
    app: grafana
spec:
  ports:
  - port: 3000
    targetPort: 3000
    name: web
  selector:
    app: grafana
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-pvc
  namespace: {self.project_name}-monitoring
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
'''
        }
    
    def generate_monitoring_configuration(self, output_dir: str = "./monitoring") -> None:
        """Generate all monitoring configuration files"""        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        for subdir in ["prometheus", "grafana", "alertmanager", "jaeger", "elk", "kubernetes"]:
            Path(output_dir, subdir).mkdir(exist_ok=True)
        
        # Generate Prometheus configuration
        with open(f"{output_dir}/prometheus/prometheus.yml", 'w') as f:
            yaml.dump(self.prometheus_config, f, default_flow_style=False)
        
        # Generate Grafana configuration
        with open(f"{output_dir}/grafana/grafana.ini", 'w') as f:
            for section, settings in self.grafana_config.items():
                f.write(f"[{section}]\\n")
                for key, value in settings.items():
                    f.write(f"{key} = {value}\\n")
                f.write("\\n")
        
        # Generate AlertManager configuration
        with open(f"{output_dir}/alertmanager/alertmanager.yml", 'w') as f:
            yaml.dump(self.alertmanager_config, f, default_flow_style=False)
        
        # Generate Jaeger configuration
        with open(f"{output_dir}/jaeger/jaeger.yml", 'w') as f:
            yaml.dump(self.jaeger_config, f, default_flow_style=False)
        
        # Generate ELK configurations
        for service, config in self.elk_config.items():
            with open(f"{output_dir}/elk/{service}.yml", 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        
        # Generate Docker Compose
        with open(f"{output_dir}/docker-compose.monitoring.yml", 'w') as f:
            f.write(self.get_docker_compose_monitoring())
        
        # Generate Kubernetes manifests
        k8s_manifests = self.get_kubernetes_monitoring_manifests()
        for filename, content in k8s_manifests.items():
            with open(f"{output_dir}/kubernetes/{filename}", 'w') as f:
                f.write(content)
        
        # Generate alert rules
        alert_rules_yaml = {
            "groups": [
                {
                    "name": f"{self.project_name}-alerts",
                    "rules": [
                        {
                            "alert": rule.name,
                            "expr": rule.condition,
                            "for": rule.duration,
                            "labels": {**rule.labels, "severity": rule.severity.value},
                            "annotations": rule.annotations
                        }
                        for rule in self.alert_rules
                    ]
                }
            ]
        }
        
        with open(f"{output_dir}/prometheus/rules/alerts.yml", 'w') as f:
            yaml.dump(alert_rules_yaml, f, default_flow_style=False)
        
        # Generate dashboards
        for dashboard in self.dashboards:
            dashboard_json = {
                "dashboard": {
                    "id": None,
                    "title": dashboard.title,
                    "description": dashboard.description,
                    "tags": dashboard.tags,
                    "timezone": "UTC",
                    "panels": dashboard.panels,
                    "time": {
                        "from": "now-6h",
                        "to": "now"
                    },
                    "timepicker": {
                        "refresh_intervals": ["5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"]
                    },
                    "refresh": "30s",
                    "version": 1
                }
            }
            
            with open(f"{output_dir}/grafana/dashboards/{dashboard.name}.json", 'w') as f:
                json.dump(dashboard_json, f, indent=2)
        
        # Generate deployment script
        deployment_script = f'''#!/bin/bash
# Monitoring stack deployment script
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

echo "🚀 Deploying monitoring stack for {self.project_name}..."

# Deploy with Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "📦 Starting monitoring services with Docker Compose..."
    docker-compose -f docker-compose.monitoring.yml up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 60
    
    echo "✅ Monitoring stack deployed successfully!"
    echo "📊 Grafana: http://localhost:3000 (admin/admin)"
    echo "🔍 Prometheus: http://localhost:9090"
    echo "🚨 AlertManager: http://localhost:9093"
    echo "🔎 Jaeger: http://localhost:16686"
    echo "📈 Kibana: http://localhost:5601"
fi

# Deploy to Kubernetes
if command -v kubectl &> /dev/null; then
    echo "☸️  Deploying to Kubernetes..."
    kubectl apply -f kubernetes/
    
    echo "⏳ Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=prometheus -n {self.project_name}-monitoring --timeout=300s
    kubectl wait --for=condition=ready pod -l app=grafana -n {self.project_name}-monitoring --timeout=300s
    
    echo "✅ Kubernetes monitoring stack deployed!"
fi

echo "🎯 Monitoring deployment completed successfully!"
'''
        
        script_path = Path(output_dir) / "deploy-monitoring.sh"
        script_path.write_text(deployment_script)
        script_path.chmod(0o755)
        
        # Generate README
        readme_content = f'''# Monitoring Stack for IA-Influencer Agent Platform

## Overview
Comprehensive monitoring and observability solution for the IA-Influencer Agent Platform.

**Author**: Fahed Mlaiel <mlaiel@live.de>
**Environment**: {self.environment}
**Cloud Provider**: {self.cloud_provider.upper()}

## Components
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Dashboards and visualization
- **AlertManager**: Alert routing and notification
- **Jaeger**: Distributed tracing
- **ELK Stack**: Centralized logging
- **Node Exporter**: System metrics
- **Blackbox Exporter**: Endpoint monitoring

## Quick Start

### Docker Compose
```bash
./deploy-monitoring.sh
```

### Kubernetes
```bash
kubectl apply -f kubernetes/
```

## Access URLs
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- AlertManager: http://localhost:9093
- Jaeger: http://localhost:16686
- Kibana: http://localhost:5601

## Custom Metrics
The platform exposes custom metrics for:
- API performance and usage
- Content protection engine
- AI/ML model performance
- Business KPIs
- System health

## Dashboards
Pre-configured dashboards available:
- Platform Overview
- Content Protection Monitoring
- Business Metrics
- Infrastructure Monitoring

## Alerting
Alert rules configured for:
- Critical service failures
- Performance degradation
- Business metric anomalies
- Infrastructure issues

## Configuration
All configuration files are in their respective directories:
- `prometheus/`: Prometheus configuration and rules
- `grafana/`: Dashboards and provisioning
- `alertmanager/`: Alert routing configuration
- `elk/`: Elasticsearch, Logstash, Kibana configs

## Support
For issues or questions, contact: mlaiel@live.de
'''
        
        with open(f"{output_dir}/README.md", 'w') as f:
            f.write(readme_content)
        
        logging.info(f"Monitoring configuration generated in {output_dir}")


# Global monitoring configuration instance
monitoring_config = MonitoringConfig()
