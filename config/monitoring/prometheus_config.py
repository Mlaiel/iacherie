"""Prometheus Configuration Module for IA-Influencer Agent Platform
================================================================

Professional Prometheus monitoring configuration with advanced metrics collection
for content creators platform with AI processing and protection systems.

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
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class MetricType(Enum):
    """Prometheus metric types"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class PrometheusMetric:
    """Prometheus metric configuration"""    name: str
    type: MetricType
    help: str
    labels: List[str] = field(default_factory=list)
    buckets: List[float] = field(default_factory=list)
    quantiles: List[float] = field(default_factory=list)


@dataclass
class PrometheusJobConfig:
    """Prometheus scraping job configuration"""    job_name: str
    scrape_interval: str
    scrape_timeout: str
    metrics_path: str
    static_configs: List[Dict[str, Any]]
    relabel_configs: List[Dict[str, Any]] = field(default_factory=list)


class PrometheusConfig:
    """Professional Prometheus configuration for IA-Influencer platform"""    
    def __init__(self):
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "9090"))
        self.metrics_port = int(os.getenv("METRICS_PORT", "8000"))
        self.scrape_interval = os.getenv("PROMETHEUS_SCRAPE_INTERVAL", "15s")
        self.evaluation_interval = os.getenv("PROMETHEUS_EVALUATION_INTERVAL", "15s")
        self.retention_time = os.getenv("PROMETHEUS_RETENTION_TIME", "30d")
        self.storage_path = os.getenv("PROMETHEUS_STORAGE_PATH", "/prometheus/data")
    
    def get_global_config(self) -> Dict[str, Any]:
        """Get global Prometheus configuration"""        return {
            "scrape_interval": self.scrape_interval,
            "evaluation_interval": self.evaluation_interval,
            "external_labels": {
                "cluster": os.getenv("CLUSTER_NAME", "ia-influencer"),
                "environment": os.getenv("ENVIRONMENT", "production")
            }
        }
    
    def get_scrape_configs(self) -> List[Dict[str, Any]]:
        """Get all scraping configurations"""        return [
            self._get_application_scrape_config(),
            self._get_ai_services_scrape_config(),
            self._get_content_protection_scrape_config(),
            self._get_audio_processing_scrape_config(),
            self._get_monetization_scrape_config(),
            self._get_infrastructure_scrape_config(),
            self._get_security_scrape_config()
        ]
    
    def _get_application_scrape_config(self) -> Dict[str, Any]:
        """Application metrics scraping configuration"""        return {
            "job_name": "ia-influencer-app",
            "scrape_interval": "10s",
            "metrics_path": "/metrics",
            "static_configs": [{
                "targets": [
                    f"app-service:8000",
                    f"api-gateway:8001",
                    f"user-service:8002",
                    f"content-service:8003"
                ]
            }],
            "metric_relabel_configs": [
                {
                    "source_labels": ["__name__"],
                    "regex": "http_requests_total",
                    "target_label": "service_type",
                    "replacement": "web_api"
                }
            ]
        }
    
    def _get_ai_services_scrape_config(self) -> Dict[str, Any]:
        """AI services metrics scraping configuration"""        return {
            "job_name": "ai-services",
            "scrape_interval": "30s",
            "metrics_path": "/ai/metrics",
            "static_configs": [{
                "targets": [
                    f"ml-inference:8100",
                    f"audio-ai:8101",
                    f"recommendation-engine:8102",
                    f"content-generator:8103",
                    f"fingerprint-ai:8104"
                ]
            }],
            "metric_relabel_configs": [
                {
                    "source_labels": ["model_name"],
                    "target_label": "ai_model",
                    "replacement": "${1}"
                }
            ]
        }
    
    def _get_content_protection_scrape_config(self) -> Dict[str, Any]:
        """Content protection metrics scraping configuration"""        return {
            "job_name": "content-protection",
            "scrape_interval": "20s",
            "metrics_path": "/protection/metrics",
            "static_configs": [{
                "targets": [
                    f"fingerprint-service:8200",
                    f"crawler-service:8201",
                    f"detection-engine:8202",
                    f"takedown-service:8203"
                ]
            }],
            "metric_relabel_configs": [
                {
                    "source_labels": ["content_type"],
                    "target_label": "protection_type",
                    "replacement": "${1}_protection"
                }
            ]
        }
    
    def _get_audio_processing_scrape_config(self) -> Dict[str, Any]:
        """Audio processing metrics scraping configuration"""        return {
            "job_name": "audio-processing",
            "scrape_interval": "15s",
            "metrics_path": "/audio/metrics",
            "static_configs": [{
                "targets": [
                    f"audio-fingerprint:8300",
                    f"spectral-analysis:8301",
                    f"audio-enhancement:8302",
                    f"format-converter:8303"
                ]
            }]
        }
    
    def _get_monetization_scrape_config(self) -> Dict[str, Any]:
        """Monetization services metrics scraping configuration"""        return {
            "job_name": "monetization",
            "scrape_interval": "60s",
            "metrics_path": "/monetization/metrics",
            "static_configs": [{
                "targets": [
                    f"revenue-tracker:8400",
                    f"payment-processor:8401",
                    f"licensing-engine:8402",
                    f"analytics-engine:8403"
                ]
            }]
        }
    
    def _get_infrastructure_scrape_config(self) -> Dict[str, Any]:
        """Infrastructure metrics scraping configuration"""        return {
            "job_name": "infrastructure",
            "scrape_interval": "30s",
            "static_configs": [{
                "targets": [
                    f"node-exporter:9100",
                    f"cadvisor:8080",
                    f"postgres-exporter:9187",
                    f"redis-exporter:9121",
                    f"nginx-exporter:9113"
                ]
            }]
        }
    
    def _get_security_scrape_config(self) -> Dict[str, Any]:
        """Security monitoring metrics scraping configuration"""        return {
            "job_name": "security",
            "scrape_interval": "10s",
            "metrics_path": "/security/metrics",
            "static_configs": [{
                "targets": [
                    f"security-monitor:8500",
                    f"auth-service:8501",
                    f"intrusion-detection:8502"
                ]
            }]
        }
    
    def get_alerting_rules(self) -> Dict[str, Any]:
        """Get Prometheus alerting rules configuration"""        return {
            "groups": [
                {
                    "name": "ia-influencer-alerts",
                    "rules": [
                        {
                            "alert": "HighErrorRate",
                            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) > 0.1",
                            "for": "5m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "High error rate detected",
                                "description": "Error rate is above 10% for 5 minutes"
                            }
                        },
                        {
                            "alert": "AIModelInferenceLatency",
                            "expr": "histogram_quantile(0.95, rate(ai_inference_duration_seconds_bucket[5m])) > 5",
                            "for": "3m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "AI model inference latency high",
                                "description": "95th percentile latency is above 5 seconds"
                            }
                        },
                        {
                            "alert": "ContentProtectionDown",
                            "expr": "up{job=\"content-protection\"} == 0",
                            "for": "1m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "Content protection service down",
                                "description": "Content protection service is unavailable"
                            }
                        }
                    ]
                }
            ]
        }
    
    def get_business_metrics(self) -> List[PrometheusMetric]:
        """Get business-specific metrics configuration"""        return [
            PrometheusMetric(
                name="content_uploads_total",
                type=MetricType.COUNTER,
                help="Total number of content uploads",
                labels=["user_id", "content_type", "platform"]
            ),
            PrometheusMetric(
                name="protection_matches_total",
                type=MetricType.COUNTER,
                help="Total number of content protection matches",
                labels=["content_type", "match_confidence", "platform"]
            ),
            PrometheusMetric(
                name="revenue_generated_total",
                type=MetricType.COUNTER,
                help="Total revenue generated from protected content",
                labels=["user_id", "platform", "content_type"]
            ),
            PrometheusMetric(
                name="ai_processing_duration_seconds",
                type=MetricType.HISTOGRAM,
                help="Duration of AI processing tasks",
                labels=["model_type", "content_type"],
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
            ),
            PrometheusMetric(
                name="fingerprint_database_size",
                type=MetricType.GAUGE,
                help="Current size of fingerprint database",
                labels=["content_type", "database_shard"]
            )
        ]
    
    def get_prometheus_yml_config(self) -> str:
        """Generate complete prometheus.yml configuration"""        config = {
            "global": self.get_global_config(),
            "alerting": {
                "alertmanagers": [
                    {
                        "static_configs": [
                            {"targets": ["alertmanager:9093"]}
                        ]
                    }
                ]
            },
            "rule_files": [
                "/etc/prometheus/rules/*.yml"
            ],
            "scrape_configs": self.get_scrape_configs()
        }
        
        import yaml
        return yaml.dump(config, default_flow_style=False, indent=2)
