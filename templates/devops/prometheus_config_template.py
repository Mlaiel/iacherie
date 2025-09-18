"""Prometheus Configuration Template for Ainflue Platform
Enterprise-grade monitoring and observability configuration for creator economy platform.

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE
© 2025 Fahed Mlaiel <mlaiel@live.de>
Tous droits réservés - Utilisation commerciale interdite sans autorisation écrite explicite

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2024-09-18
"""

import logging
import yaml
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to collect"""
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    BUSINESS = "business"
    CREATOR_ECONOMY = "creator_economy"
    AI_MODELS = "ai_models"
    SECURITY = "security"


class ServiceType(Enum):
    """Ainflue platform services"""
    API_GATEWAY = "api-gateway"
    AUTH_SERVICE = "auth-service"
    CONTENT_PROCESSOR = "content-processor"
    AI_SERVICES = "ai-services"
    MEDIA_PROCESSOR = "media-processor"
    ANALYTICS_SERVICE = "analytics-service"
    PAYMENT_SERVICE = "payment-service"


@dataclass
class PrometheusConfig:
    """Prometheus monitoring configuration"""
    project_name: str
    environment: str
    namespace: str = "monitoring"
    
    # Retention settings
    retention_time: str = "30d"
    retention_size: str = "50GB"
    
    # Scrape settings
    scrape_interval: str = "15s"
    evaluation_interval: str = "15s"
    
    # Enable specific metric types
    enable_infrastructure_metrics: bool = True
    enable_application_metrics: bool = True
    enable_business_metrics: bool = True
    enable_creator_economy_metrics: bool = True
    enable_ai_model_metrics: bool = True
    enable_security_metrics: bool = True
    
    # Service monitoring
    services_to_monitor: List[ServiceType] = None
    
    # External integrations
    enable_alertmanager: bool = True
    enable_grafana: bool = True
    enable_pushgateway: bool = True
    
    def __post_init__(self):
        if self.services_to_monitor is None:
            self.services_to_monitor = [
                ServiceType.API_GATEWAY,
                ServiceType.AUTH_SERVICE,
                ServiceType.CONTENT_PROCESSOR,
                ServiceType.AI_SERVICES,
                ServiceType.MEDIA_PROCESSOR,
                ServiceType.ANALYTICS_SERVICE
            ]


class PrometheusConfigTemplate:
    """Enterprise Prometheus Configuration Template for Ainflue Platform"""
    
    def __init__(self, config: PrometheusConfig):
        self.config = config
        
    def generate_prometheus_config(self) -> Dict[str, Any]:
        """Generate main Prometheus configuration"""
        config = {
            "global": {
                "scrape_interval": self.config.scrape_interval,
                "evaluation_interval": self.config.evaluation_interval,
                "external_labels": {
                    "cluster": f"{self.config.project_name}-{self.config.environment}",
                    "environment": self.config.environment,
                    "project": self.config.project_name
                }
            },
            "rule_files": [
                "/etc/prometheus/rules/*.yml"
            ],
            "alerting": {
                "alertmanagers": [
                    {
                        "static_configs": [
                            {"targets": ["alertmanager:9093"]}
                        ]
                    }
                ]
            } if self.config.enable_alertmanager else {},
            "scrape_configs": self._generate_scrape_configs()
        }
        
        return config
    
    def _generate_scrape_configs(self) -> List[Dict[str, Any]]:
        """Generate scrape configurations for all targets"""
        scrape_configs = []
        
        # Prometheus self-monitoring
        scrape_configs.append({
            "job_name": "prometheus",
            "static_configs": [
                {"targets": ["localhost:9090"]}
            ],
            "scrape_interval": "30s"
        })
        
        # Kubernetes infrastructure monitoring
        if self.config.enable_infrastructure_metrics:
            scrape_configs.extend(self._generate_kubernetes_scrape_configs())
        
        # Application service monitoring
        if self.config.enable_application_metrics:
            scrape_configs.extend(self._generate_application_scrape_configs())
        
        # Creator economy specific metrics
        if self.config.enable_creator_economy_metrics:
            scrape_configs.extend(self._generate_creator_economy_scrape_configs())
        
        # AI model monitoring
        if self.config.enable_ai_model_metrics:
            scrape_configs.extend(self._generate_ai_model_scrape_configs())
        
        # Security monitoring
        if self.config.enable_security_metrics:
            scrape_configs.extend(self._generate_security_scrape_configs())
        
        return scrape_configs
    
    def _generate_kubernetes_scrape_configs(self) -> List[Dict[str, Any]]:
        """Generate Kubernetes infrastructure scrape configs"""
        return [
            {
                "job_name": "kubernetes-apiservers",
                "kubernetes_sd_configs": [
                    {"role": "endpoints"}
                ],
                "scheme": "https",
                "tls_config": {
                    "ca_file": "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
                },
                "bearer_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token",
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_namespace", "__meta_kubernetes_service_name", "__meta_kubernetes_endpoint_port_name"],
                        "action": "keep",
                        "regex": "default;kubernetes;https"
                    }
                ]
            },
            {
                "job_name": "kubernetes-nodes",
                "kubernetes_sd_configs": [
                    {"role": "node"}
                ],
                "scheme": "https",
                "tls_config": {
                    "ca_file": "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
                },
                "bearer_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token",
                "relabel_configs": [
                    {
                        "action": "labelmap",
                        "regex": "__meta_kubernetes_node_label_(.+)"
                    }
                ]
            },
            {
                "job_name": "kubernetes-cadvisor",
                "kubernetes_sd_configs": [
                    {"role": "node"}
                ],
                "scheme": "https",
                "metrics_path": "/metrics/cadvisor",
                "tls_config": {
                    "ca_file": "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
                },
                "bearer_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token",
                "relabel_configs": [
                    {
                        "action": "labelmap",
                        "regex": "__meta_kubernetes_node_label_(.+)"
                    }
                ]
            },
            {
                "job_name": "kubernetes-service-endpoints",
                "kubernetes_sd_configs": [
                    {"role": "endpoints"}
                ],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_service_annotation_prometheus_io_scrape"],
                        "action": "keep",
                        "regex": True
                    },
                    {
                        "source_labels": ["__meta_kubernetes_service_annotation_prometheus_io_path"],
                        "action": "replace",
                        "target_label": "__metrics_path__",
                        "regex": "(.+)"
                    },
                    {
                        "source_labels": ["__address__", "__meta_kubernetes_service_annotation_prometheus_io_port"],
                        "action": "replace",
                        "target_label": "__address__",
                        "regex": "([^:]+)(?::\\d+)?;(\\d+)",
                        "replacement": "$1:$2"
                    }
                ]
            }
        ]
    
    def _generate_application_scrape_configs(self) -> List[Dict[str, Any]]:
        """Generate application service scrape configs"""
        scrape_configs = []
        
        for service in self.config.services_to_monitor:
            service_name = service.value
            scrape_configs.append({
                "job_name": f"ainflue-{service_name}",
                "kubernetes_sd_configs": [
                    {
                        "role": "endpoints",
                        "namespaces": {
                            "names": [f"{self.config.project_name}-{self.config.environment}"]
                        }
                    }
                ],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_service_name"],
                        "action": "keep",
                        "regex": f"{self.config.project_name}-{service_name}"
                    },
                    {
                        "source_labels": ["__meta_kubernetes_endpoint_port_name"],
                        "action": "keep",
                        "regex": "metrics"
                    }
                ],
                "scrape_interval": "30s",
                "metrics_path": "/metrics"
            })
        
        return scrape_configs
    
    def _generate_creator_economy_scrape_configs(self) -> List[Dict[str, Any]]:
        """Generate creator economy specific scrape configs"""
        return [
            {
                "job_name": "creator-metrics",
                "kubernetes_sd_configs": [
                    {
                        "role": "endpoints",
                        "namespaces": {
                            "names": [f"{self.config.project_name}-{self.config.environment}"]
                        }
                    }
                ],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_service_annotation_metrics_creator_economy"],
                        "action": "keep",
                        "regex": "true"
                    }
                ],
                "scrape_interval": "60s",
                "metrics_path": "/metrics/creator"
            },
            {
                "job_name": "content-processing-metrics",
                "kubernetes_sd_configs": [
                    {
                        "role": "endpoints",
                        "namespaces": {
                            "names": [f"{self.config.project_name}-{self.config.environment}"]
                        }
                    }
                ],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_service_annotation_metrics_content_processing"],
                        "action": "keep",
                        "regex": "true"
                    }
                ],
                "scrape_interval": "30s",
                "metrics_path": "/metrics/content"
            },
            {
                "job_name": "revenue-metrics",
                "kubernetes_sd_configs": [
                    {
                        "role": "endpoints",
                        "namespaces": {
                            "names": [f"{self.config.project_name}-{self.config.environment}"]
                        }
                    }
                ],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_service_annotation_metrics_revenue"],
                        "action": "keep",
                        "regex": "true"
                    }
                ],
                "scrape_interval": "300s",  # 5 minutes for business metrics
                "metrics_path": "/metrics/revenue"
            }
        ]
    
    def _generate_ai_model_scrape_configs(self) -> List[Dict[str, Any]]:
        """Generate AI model monitoring scrape configs"""
        return [
            {
                "job_name": "ai-model-inference",
                "kubernetes_sd_configs": [
                    {
                        "role": "endpoints",
                        "namespaces": {
                            "names": [f"{self.config.project_name}-{self.config.environment}"]
                        }
                    }
                ],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_service_annotation_metrics_ai_models"],
                        "action": "keep",
                        "regex": "true"
                    }
                ],
                "scrape_interval": "15s",
                "metrics_path": "/metrics/ai"
            },
            {
                "job_name": "gpu-metrics",
                "static_configs": [
                    {"targets": ["dcgm-exporter:9400"]}
                ],
                "scrape_interval": "30s"
            }
        ]
    
    def _generate_security_scrape_configs(self) -> List[Dict[str, Any]]:
        """Generate security monitoring scrape configs"""
        return [
            {
                "job_name": "security-events",
                "kubernetes_sd_configs": [
                    {
                        "role": "endpoints",
                        "namespaces": {
                            "names": [f"{self.config.project_name}-{self.config.environment}"]
                        }
                    }
                ],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_service_annotation_metrics_security"],
                        "action": "keep",
                        "regex": "true"
                    }
                ],
                "scrape_interval": "60s",
                "metrics_path": "/metrics/security"
            },
            {
                "job_name": "vault-metrics",
                "static_configs": [
                    {"targets": ["vault:8200"]}
                ],
                "scheme": "https",
                "tls_config": {
                    "insecure_skip_verify": True
                },
                "metrics_path": "/v1/sys/metrics",
                "params": {
                    "format": ["prometheus"]
                },
                "scrape_interval": "60s"
            }
        ]
    
    def generate_alerting_rules(self) -> Dict[str, Any]:
        """Generate Prometheus alerting rules"""
        rules = {
            "groups": []
        }
        
        # Infrastructure alerts
        if self.config.enable_infrastructure_metrics:
            rules["groups"].append(self._generate_infrastructure_alerts())
        
        # Application alerts
        if self.config.enable_application_metrics:
            rules["groups"].append(self._generate_application_alerts())
        
        # Creator economy alerts
        if self.config.enable_creator_economy_metrics:
            rules["groups"].append(self._generate_creator_economy_alerts())
        
        # AI model alerts
        if self.config.enable_ai_model_metrics:
            rules["groups"].append(self._generate_ai_model_alerts())
        
        # Security alerts
        if self.config.enable_security_metrics:
            rules["groups"].append(self._generate_security_alerts())
        
        return rules
    
    def _generate_infrastructure_alerts(self) -> Dict[str, Any]:
        """Generate infrastructure alerting rules"""
        return {
            "name": "infrastructure",
            "rules": [
                {
                    "alert": "HighCPUUsage",
                    "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100) > 80",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "category": "infrastructure"
                    },
                    "annotations": {
                        "summary": "High CPU usage detected",
                        "description": "CPU usage is above 80% for {{ $labels.instance }}"
                    }
                },
                {
                    "alert": "HighMemoryUsage",
                    "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "category": "infrastructure"
                    },
                    "annotations": {
                        "summary": "High memory usage detected",
                        "description": "Memory usage is above 85% for {{ $labels.instance }}"
                    }
                },
                {
                    "alert": "DiskSpaceLow",
                    "expr": "(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90",
                    "for": "10m",
                    "labels": {
                        "severity": "critical",
                        "category": "infrastructure"
                    },
                    "annotations": {
                        "summary": "Disk space is running low",
                        "description": "Disk usage is above 90% for {{ $labels.instance }} on {{ $labels.mountpoint }}"
                    }
                },
                {
                    "alert": "PodCrashLooping",
                    "expr": "rate(kube_pod_container_status_restarts_total[15m]) > 0",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "category": "kubernetes"
                    },
                    "annotations": {
                        "summary": "Pod is crash looping",
                        "description": "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is crash looping"
                    }
                }
            ]
        }
    
    def _generate_application_alerts(self) -> Dict[str, Any]:
        """Generate application alerting rules"""
        return {
            "name": "application",
            "rules": [
                {
                    "alert": "HighErrorRate",
                    "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) > 0.05",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "category": "application"
                    },
                    "annotations": {
                        "summary": "High error rate detected",
                        "description": "Error rate is above 5% for {{ $labels.service }}"
                    }
                },
                {
                    "alert": "HighResponseTime",
                    "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2",
                    "for": "10m",
                    "labels": {
                        "severity": "warning",
                        "category": "application"
                    },
                    "annotations": {
                        "summary": "High response time detected",
                        "description": "95th percentile response time is above 2 seconds for {{ $labels.service }}"
                    }
                },
                {
                    "alert": "ServiceDown",
                    "expr": "up{job=~\"ainflue-.*\"} == 0",
                    "for": "1m",
                    "labels": {
                        "severity": "critical",
                        "category": "application"
                    },
                    "annotations": {
                        "summary": "Service is down",
                        "description": "Service {{ $labels.job }} is down"
                    }
                }
            ]
        }
    
    def _generate_creator_economy_alerts(self) -> Dict[str, Any]:
        """Generate creator economy specific alerts"""
        return {
            "name": "creator_economy",
            "rules": [
                {
                    "alert": "ContentProcessingBacklog",
                    "expr": "content_processing_queue_size > 1000",
                    "for": "15m",
                    "labels": {
                        "severity": "warning",
                        "category": "creator_economy"
                    },
                    "annotations": {
                        "summary": "Content processing backlog is high",
                        "description": "Content processing queue has {{ $value }} items"
                    }
                },
                {
                    "alert": "CreatorUploadFailures",
                    "expr": "rate(creator_upload_failures_total[10m]) > 0.1",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "category": "creator_economy"
                    },
                    "annotations": {
                        "summary": "High creator upload failure rate",
                        "description": "Creator upload failure rate is {{ $value }} per second"
                    }
                },
                {
                    "alert": "RevenueSystemDown",
                    "expr": "revenue_system_health == 0",
                    "for": "1m",
                    "labels": {
                        "severity": "critical",
                        "category": "creator_economy"
                    },
                    "annotations": {
                        "summary": "Revenue system is down",
                        "description": "Revenue processing system is not healthy"
                    }
                },
                {
                    "alert": "LowCreatorEngagement",
                    "expr": "creator_daily_active_users < 100",
                    "for": "1h",
                    "labels": {
                        "severity": "info",
                        "category": "creator_economy"
                    },
                    "annotations": {
                        "summary": "Low creator engagement",
                        "description": "Daily active creators is below threshold: {{ $value }}"
                    }
                }
            ]
        }
    
    def _generate_ai_model_alerts(self) -> Dict[str, Any]:
        """Generate AI model specific alerts"""
        return {
            "name": "ai_models",
            "rules": [
                {
                    "alert": "AIInferenceLatencyHigh",
                    "expr": "histogram_quantile(0.95, rate(ai_inference_duration_seconds_bucket[5m])) > 10",
                    "for": "10m",
                    "labels": {
                        "severity": "warning",
                        "category": "ai_models"
                    },
                    "annotations": {
                        "summary": "AI inference latency is high",
                        "description": "95th percentile AI inference latency is {{ $value }} seconds for model {{ $labels.model }}"
                    }
                },
                {
                    "alert": "GPUUtilizationHigh",
                    "expr": "DCGM_FI_DEV_GPU_UTIL > 95",
                    "for": "15m",
                    "labels": {
                        "severity": "warning",
                        "category": "ai_models"
                    },
                    "annotations": {
                        "summary": "GPU utilization is very high",
                        "description": "GPU {{ $labels.gpu }} utilization is {{ $value }}%"
                    }
                },
                {
                    "alert": "AIModelErrors",
                    "expr": "rate(ai_model_errors_total[5m]) > 0.01",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "category": "ai_models"
                    },
                    "annotations": {
                        "summary": "AI model errors detected",
                        "description": "AI model {{ $labels.model }} is producing errors at {{ $value }} per second"
                    }
                }
            ]
        }
    
    def _generate_security_alerts(self) -> Dict[str, Any]:
        """Generate security alerting rules"""
        return {
            "name": "security",
            "rules": [
                {
                    "alert": "SuspiciousLoginActivity",
                    "expr": "rate(auth_failed_attempts_total[5m]) > 10",
                    "for": "2m",
                    "labels": {
                        "severity": "warning",
                        "category": "security"
                    },
                    "annotations": {
                        "summary": "Suspicious login activity detected",
                        "description": "Failed login attempts rate is {{ $value }} per second from {{ $labels.source_ip }}"
                    }
                },
                {
                    "alert": "VaultSealedUnexpectedly",
                    "expr": "vault_core_sealed == 1",
                    "for": "1m",
                    "labels": {
                        "severity": "critical",
                        "category": "security"
                    },
                    "annotations": {
                        "summary": "Vault is sealed unexpectedly",
                        "description": "HashiCorp Vault instance is sealed"
                    }
                },
                {
                    "alert": "SecurityVulnerabilityDetected",
                    "expr": "security_vulnerabilities_high > 0",
                    "for": "1m",
                    "labels": {
                        "severity": "critical",
                        "category": "security"
                    },
                    "annotations": {
                        "summary": "High severity security vulnerability detected",
                        "description": "{{ $value }} high severity vulnerabilities detected in {{ $labels.component }}"
                    }
                }
            ]
        }
    
    def generate_recording_rules(self) -> Dict[str, Any]:
        """Generate Prometheus recording rules for performance optimization"""
        return {
            "groups": [
                {
                    "name": "creator_economy_recordings",
                    "interval": "30s",
                    "rules": [
                        {
                            "record": "ainflue:creator_active_users_5m",
                            "expr": "sum(rate(creator_activity_total[5m]))"
                        },
                        {
                            "record": "ainflue:content_processing_rate_5m",
                            "expr": "sum(rate(content_processed_total[5m]))"
                        },
                        {
                            "record": "ainflue:revenue_per_second_5m",
                            "expr": "sum(rate(revenue_generated_total[5m]))"
                        },
                        {
                            "record": "ainflue:ai_inference_rate_5m",
                            "expr": "sum(rate(ai_inference_requests_total[5m]))"
                        }
                    ]
                }
            ]
        }
    
    def save_prometheus_configs(self, output_dir: str) -> None:
        """Save all Prometheus configurations"""
        output_path = Path(output_dir)
        prometheus_dir = output_path / "prometheus"
        prometheus_dir.mkdir(parents=True, exist_ok=True)
        
        # Main configuration
        with open(prometheus_dir / "prometheus.yml", 'w') as f:
            yaml.dump(self.generate_prometheus_config(), f, default_flow_style=False, indent=2)
        
        # Alerting rules
        rules_dir = prometheus_dir / "rules"
        rules_dir.mkdir(exist_ok=True)
        
        with open(rules_dir / "alerts.yml", 'w') as f:
            yaml.dump(self.generate_alerting_rules(), f, default_flow_style=False, indent=2)
        
        # Recording rules
        with open(rules_dir / "recording.yml", 'w') as f:
            yaml.dump(self.generate_recording_rules(), f, default_flow_style=False, indent=2)
        
        logger.info(f"Prometheus configurations saved to {output_dir}")


# Example usage
def create_production_prometheus_config() -> PrometheusConfig:
    """Create production Prometheus configuration"""
    return PrometheusConfig(
        project_name="ainflue-platform",
        environment="production",
        retention_time="30d",
        retention_size="50GB",
        enable_infrastructure_metrics=True,
        enable_application_metrics=True,
        enable_business_metrics=True,
        enable_creator_economy_metrics=True,
        enable_ai_model_metrics=True,
        enable_security_metrics=True,
        enable_alertmanager=True,
        enable_grafana=True
    )


if __name__ == "__main__":
    config = create_production_prometheus_config()
    template = PrometheusConfigTemplate(config)
    
    print("Prometheus Configuration Template for Ainflue Platform")
    print("Configuration:")
    print(f"- Environment: {config.environment}")
    print(f"- Retention: {config.retention_time}")
    print(f"- Services Monitored: {[s.value for s in config.services_to_monitor]}")
    print(f"- Creator Economy Metrics: {config.enable_creator_economy_metrics}")
    print(f"- AI Model Metrics: {config.enable_ai_model_metrics}")
    print(f"- Security Metrics: {config.enable_security_metrics}")
