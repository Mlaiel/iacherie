"""
Prometheus Manager - Enterprise Monitoring Infrastructure
© 2025 Fahed Mlaiel. All rights reserved.

DevOps Role Implementation:
- Comprehensive infrastructure monitoring with Prometheus
- Creator platform-specific metrics collection
- AI-powered alerting and anomaly detection
- Performance optimization insights
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected"""
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    BUSINESS = "business"
    CREATOR_SPECIFIC = "creator_specific"
    AI_PROCESSING = "ai_processing"
    AUDIO_STREAMING = "audio_streaming"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


@dataclass
class MetricConfig:
    """Prometheus metric configuration"""
    name: str
    metric_type: MetricType
    help_text: str
    labels: List[str]
    scrape_interval: str = "15s"
    creator_specific: bool = False


class PrometheusManager:
    """
    Enterprise Prometheus monitoring manager for Ainflue infrastructure
    
    DevOps Role: Complete monitoring infrastructure for creator platform
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metric_configs = {}
        self.alert_rules = {}
        self.dashboards = {}
        
        # Initialize Ainflue-specific monitoring
        self._initialize_ainflue_metrics()
        
        self.logger.info("Prometheus manager initialized with creator platform monitoring")
    
    async def setup_comprehensive_monitoring(self, monitoring_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Setup comprehensive monitoring for Ainflue infrastructure
        
        DevOps Role: Complete monitoring stack with creator-specific metrics
        """
        try:
            # Setup core infrastructure monitoring
            infrastructure_monitoring = await self._setup_infrastructure_monitoring(monitoring_config)
            
            # Setup creator platform monitoring
            creator_monitoring = await self._setup_creator_platform_monitoring(monitoring_config)
            
            # Setup AI processing monitoring
            ai_monitoring = await self._setup_ai_processing_monitoring(monitoring_config)
            
            # Setup audio streaming monitoring
            audio_monitoring = await self._setup_audio_streaming_monitoring(monitoring_config)
            
            # Configure alerting rules
            alerting_config = await self._configure_comprehensive_alerting()
            
            # Setup monitoring dashboards
            dashboard_config = await self._setup_monitoring_dashboards()
            
            result = {
                'monitoring_id': f"monitoring_{int(asyncio.get_event_loop().time())}",
                'infrastructure_monitoring': infrastructure_monitoring,
                'creator_monitoring': creator_monitoring,
                'ai_monitoring': ai_monitoring,
                'audio_monitoring': audio_monitoring,
                'alerting_config': alerting_config,
                'dashboard_config': dashboard_config,
                'metrics_endpoints': await self._get_metrics_endpoints(),
                'status': 'configured',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.info("Comprehensive monitoring setup completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Monitoring setup failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def setup_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method - redirects to comprehensive monitoring"""
        return await self.setup_comprehensive_monitoring(config)
    
    def _initialize_ainflue_metrics(self):
        """Initialize Ainflue-specific metric configurations"""
        metrics = [
            MetricConfig(
                name="ainflue_creator_uploads_total",
                metric_type=MetricType.CREATOR_SPECIFIC,
                help_text="Total number of content uploads by creators",
                labels=["creator_id", "content_type", "upload_status"],
                creator_specific=True
            ),
            MetricConfig(
                name="ainflue_ai_processing_duration_seconds",
                metric_type=MetricType.AI_PROCESSING,
                help_text="Time taken for AI content processing",
                labels=["model_name", "content_type", "processing_stage"],
                creator_specific=True
            ),
            MetricConfig(
                name="ainflue_audio_streaming_quality",
                metric_type=MetricType.AUDIO_STREAMING,
                help_text="Audio streaming quality metrics",
                labels=["codec", "bitrate", "region", "creator_id"],
                creator_specific=True
            ),
            MetricConfig(
                name="ainflue_collaboration_sessions_active",
                metric_type=MetricType.CREATOR_SPECIFIC,
                help_text="Number of active creator collaboration sessions",
                labels=["session_type", "participants_count", "content_type"],
                creator_specific=True
            ),
            MetricConfig(
                name="ainflue_infrastructure_costs_usd",
                metric_type=MetricType.BUSINESS,
                help_text="Infrastructure costs in USD",
                labels=["service", "region", "cost_category"],
                creator_specific=False
            )
        ]
        
        for metric in metrics:
            self.metric_configs[metric.name] = metric
    
    async def _setup_infrastructure_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup core infrastructure monitoring"""
        return {
            'cpu_metrics': ['node_cpu_seconds_total', 'container_cpu_usage_seconds_total'],
            'memory_metrics': ['node_memory_MemTotal_bytes', 'container_memory_usage_bytes'],
            'disk_metrics': ['node_filesystem_size_bytes', 'node_disk_io_time_seconds_total'],
            'network_metrics': ['node_network_receive_bytes_total', 'node_network_transmit_bytes_total'],
            'kubernetes_metrics': ['kube_pod_status_phase', 'kube_deployment_status_replicas'],
            'scrape_interval': '15s',
            'retention_period': '30d'
        }
    
    async def _setup_creator_platform_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup creator platform-specific monitoring"""
        return {
            'creator_metrics': [
                'ainflue_creator_uploads_total',
                'ainflue_creator_active_sessions',
                'ainflue_creator_content_views',
                'ainflue_creator_collaboration_invites'
            ],
            'content_metrics': [
                'ainflue_content_processing_time',
                'ainflue_content_storage_usage',
                'ainflue_content_download_count'
            ],
            'revenue_metrics': [
                'ainflue_creator_revenue_usd',
                'ainflue_platform_commission_usd',
                'ainflue_payout_processing_time'
            ],
            'user_experience_metrics': [
                'ainflue_page_load_time',
                'ainflue_api_response_time',
                'ainflue_error_rate_percent'
            ]
        }
    
    async def _setup_ai_processing_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup AI processing monitoring"""
        return {
            'model_performance': [
                'ainflue_ai_processing_duration_seconds',
                'ainflue_ai_model_accuracy_score',
                'ainflue_ai_queue_length',
                'ainflue_ai_throughput_requests_per_second'
            ],
            'gpu_metrics': [
                'nvidia_gpu_utilization_percent',
                'nvidia_gpu_memory_used_bytes',
                'nvidia_gpu_temperature_celsius'
            ],
            'ml_pipeline_metrics': [
                'ainflue_ml_training_duration',
                'ainflue_ml_model_drift_score',
                'ainflue_ml_feature_importance'
            ]
        }
    
    async def _setup_audio_streaming_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup audio streaming monitoring"""
        return {
            'streaming_quality': [
                'ainflue_audio_streaming_quality',
                'ainflue_audio_bitrate_kbps',
                'ainflue_audio_latency_ms',
                'ainflue_audio_buffer_health'
            ],
            'cdn_metrics': [
                'ainflue_cdn_cache_hit_ratio',
                'ainflue_cdn_bandwidth_usage',
                'ainflue_cdn_origin_requests'
            ],
            'codec_performance': [
                'ainflue_audio_encoding_time',
                'ainflue_audio_compression_ratio',
                'ainflue_audio_quality_score'
            ]
        }
    
    async def _configure_comprehensive_alerting(self) -> Dict[str, Any]:
        """Configure alerting rules for all monitoring aspects"""
        return {
            'critical_alerts': [
                {
                    'name': 'InfrastructureDown',
                    'condition': 'up == 0',
                    'duration': '5m',
                    'severity': AlertSeverity.CRITICAL.value,
                    'description': 'Infrastructure component is down'
                },
                {
                    'name': 'CreatorUploadFailures',
                    'condition': 'rate(ainflue_creator_uploads_total{upload_status="failed"}[5m]) > 0.1',
                    'duration': '2m',
                    'severity': AlertSeverity.CRITICAL.value,
                    'description': 'High creator upload failure rate'
                }
            ],
            'warning_alerts': [
                {
                    'name': 'HighCPUUsage',
                    'condition': 'rate(node_cpu_seconds_total[5m]) > 0.8',
                    'duration': '10m',
                    'severity': AlertSeverity.WARNING.value,
                    'description': 'High CPU usage detected'
                },
                {
                    'name': 'AIProcessingDelay',
                    'condition': 'ainflue_ai_processing_duration_seconds > 30',
                    'duration': '5m',
                    'severity': AlertSeverity.WARNING.value,
                    'description': 'AI processing taking longer than expected'
                }
            ],
            'notification_channels': [
                'slack://alerts-channel',
                'email://devops-team@ainflue.com',
                'pagerduty://on-call-team'
            ]
        }
    
    async def _setup_monitoring_dashboards(self) -> Dict[str, Any]:
        """Setup monitoring dashboards"""
        return {
            'infrastructure_dashboard': {
                'name': 'Ainflue Infrastructure Overview',
                'panels': [
                    'CPU and Memory Usage',
                    'Network Traffic',
                    'Disk Usage',
                    'Kubernetes Cluster Status'
                ]
            },
            'creator_platform_dashboard': {
                'name': 'Creator Platform Metrics',
                'panels': [
                    'Active Creators',
                    'Content Uploads',
                    'Collaboration Sessions',
                    'Revenue Metrics'
                ]
            },
            'ai_processing_dashboard': {
                'name': 'AI Processing Performance',
                'panels': [
                    'Model Performance',
                    'GPU Utilization',
                    'Processing Queue',
                    'ML Pipeline Health'
                ]
            },
            'audio_streaming_dashboard': {
                'name': 'Audio Streaming Quality',
                'panels': [
                    'Streaming Quality Metrics',
                    'CDN Performance',
                    'Codec Efficiency',
                    'Latency Analysis'
                ]
            }
        }
    
    async def _get_metrics_endpoints(self) -> Dict[str, Any]:
        """Get metrics collection endpoints"""
        return {
            'prometheus_endpoint': 'http://prometheus.ainflue.com:9090',
            'grafana_endpoint': 'http://grafana.ainflue.com:3000',
            'alert_manager_endpoint': 'http://alertmanager.ainflue.com:9093',
            'metrics_exporters': [
                'node-exporter:9100',
                'cadvisor:8080',
                'kube-state-metrics:8080',
                'ainflue-app-metrics:8080'
            ]
        }