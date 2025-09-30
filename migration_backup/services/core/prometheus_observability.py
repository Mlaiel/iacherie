"""
Enhanced Prometheus Observability - Enterprise DevOps Implementation
==================================================================

**Author**: Expert DevOps Engineer (Fahed Mlaiel)
**Role**: DevOps Expert - Monitoring & Observabilité Enterprise
**Module**: Phase 3 - Observabilité Prometheus/Grafana complète
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-15

Complete Prometheus/Grafana observability implementation with enterprise-grade
metrics collection, alerting, and dashboard generation for microservices.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml

# Enterprise dependencies
try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Summary, Info,
        CollectorRegistry, generate_latest, start_http_server,
        multiprocess, values
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    import grafana_api
    GRAFANA_AVAILABLE = True
except ImportError:
    GRAFANA_AVAILABLE = False

# Configure enterprise logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Enterprise metric types for observability"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    INFO = "info"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricDefinition:
    """Enterprise metric definition"""
    name: str
    help: str
    metric_type: MetricType
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None
    namespace: str = "ainflue"
    subsystem: str = ""


@dataclass
class AlertRule:
    """Prometheus alert rule definition"""
    name: str
    expression: str
    duration: str
    severity: AlertSeverity
    summary: str
    description: str
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class DashboardConfig:
    """Grafana dashboard configuration"""
    title: str
    tags: List[str]
    panels: List[Dict[str, Any]]
    time_range: Dict[str, str] = field(default_factory=lambda: {"from": "now-1h", "to": "now"})
    refresh: str = "30s"


class PrometheusObservability:
    """
    Enterprise Prometheus Observability Manager
    
    Comprehensive observability solution with:
    - Multi-dimensional metrics collection
    - Real-time alerting rules
    - Grafana dashboard automation
    - Service-level indicators (SLIs)
    - Service-level objectives (SLOs)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.registry = CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        self.alert_rules: List[AlertRule] = []
        self.dashboards: List[DashboardConfig] = []
        self.logger = logging.getLogger(f"{__name__}.PrometheusObservability")
        
        # Enterprise service metrics
        self.service_metrics = self._initialize_service_metrics()
        
        # Business metrics for Ainflue platform
        self.business_metrics = self._initialize_business_metrics()
        
        # Performance SLIs
        self.sli_metrics = self._initialize_sli_metrics()
        
        self.logger.info("Enterprise Prometheus Observability initialized")

    def _initialize_service_metrics(self) -> Dict[str, Any]:
        """Initialize core service metrics"""
        metrics = {}
        
        # HTTP request metrics
        metrics['http_requests_total'] = Counter(
            'ainflue_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code', 'service'],
            registry=self.registry
        )
        
        metrics['http_request_duration'] = Histogram(
            'ainflue_http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint', 'service'],
            buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0],
            registry=self.registry
        )
        
        # Service health metrics
        metrics['service_health'] = Gauge(
            'ainflue_service_health',
            'Service health status (1=healthy, 0=unhealthy)',
            ['service', 'instance'],
            registry=self.registry
        )
        
        # Circuit breaker metrics
        metrics['circuit_breaker_state'] = Gauge(
            'ainflue_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half-open)',
            ['service', 'dependency'],
            registry=self.registry
        )
        
        # Database metrics
        metrics['db_connections_active'] = Gauge(
            'ainflue_db_connections_active',
            'Active database connections',
            ['database', 'service'],
            registry=self.registry
        )
        
        metrics['db_query_duration'] = Histogram(
            'ainflue_db_query_duration_seconds',
            'Database query duration',
            ['database', 'operation', 'service'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )
        
        return metrics

    def _initialize_business_metrics(self) -> Dict[str, Any]:
        """Initialize Ainflue business metrics"""
        metrics = {}
        
        # Creator platform metrics
        metrics['creators_active'] = Gauge(
            'ainflue_creators_active_total',
            'Number of active creators',
            ['tier', 'region'],
            registry=self.registry
        )
        
        metrics['content_processed'] = Counter(
            'ainflue_content_processed_total',
            'Total content processed',
            ['type', 'format', 'status'],
            registry=self.registry
        )
        
        # AI processing metrics
        metrics['ai_inference_duration'] = Histogram(
            'ainflue_ai_inference_duration_seconds',
            'AI inference duration',
            ['model', 'provider', 'service'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        metrics['ai_requests_total'] = Counter(
            'ainflue_ai_requests_total',
            'Total AI requests',
            ['model', 'provider', 'status'],
            registry=self.registry
        )
        
        # Revenue metrics
        metrics['revenue_generated'] = Counter(
            'ainflue_revenue_generated_euros',
            'Revenue generated in euros',
            ['creator_tier', 'content_type', 'region'],
            registry=self.registry
        )
        
        # Media processing metrics
        metrics['media_processing_duration'] = Histogram(
            'ainflue_media_processing_duration_seconds',
            'Media processing duration',
            ['format', 'quality', 'service'],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
            registry=self.registry
        )
        
        return metrics

    def _initialize_sli_metrics(self) -> Dict[str, Any]:
        """Initialize Service Level Indicators"""
        metrics = {}
        
        # Availability SLI
        metrics['sli_availability'] = Gauge(
            'ainflue_sli_availability_ratio',
            'Service availability ratio',
            ['service'],
            registry=self.registry
        )
        
        # Latency SLI (P95, P99)
        metrics['sli_latency_p95'] = Gauge(
            'ainflue_sli_latency_p95_seconds',
            'Service latency P95',
            ['service'],
            registry=self.registry
        )
        
        metrics['sli_latency_p99'] = Gauge(
            'ainflue_sli_latency_p99_seconds',
            'Service latency P99',
            ['service'],
            registry=self.registry
        )
        
        # Error rate SLI
        metrics['sli_error_rate'] = Gauge(
            'ainflue_sli_error_rate_ratio',
            'Service error rate ratio',
            ['service'],
            registry=self.registry
        )
        
        # Throughput SLI
        metrics['sli_throughput'] = Gauge(
            'ainflue_sli_throughput_rps',
            'Service throughput in requests per second',
            ['service'],
            registry=self.registry
        )
        
        return metrics

    async def record_http_request(
        self, 
        method: str, 
        endpoint: str, 
        status_code: int, 
        duration: float,
        service: str
    ):
        """Record HTTP request metrics"""
        try:
            # Record request count
            self.service_metrics['http_requests_total'].labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code),
                service=service
            ).inc()
            
            # Record request duration
            self.service_metrics['http_request_duration'].labels(
                method=method,
                endpoint=endpoint,
                service=service
            ).observe(duration)
            
            self.logger.debug(f"Recorded HTTP request: {method} {endpoint} {status_code} ({duration}s)")
            
        except Exception as e:
            self.logger.error(f"Error recording HTTP request metrics: {e}")

    async def record_ai_inference(
        self,
        model: str,
        provider: str,
        duration: float,
        status: str,
        service: str
    ):
        """Record AI inference metrics"""
        try:
            # Record inference duration
            self.business_metrics['ai_inference_duration'].labels(
                model=model,
                provider=provider,
                service=service
            ).observe(duration)
            
            # Record request count
            self.business_metrics['ai_requests_total'].labels(
                model=model,
                provider=provider,
                status=status
            ).inc()
            
            self.logger.debug(f"Recorded AI inference: {model} ({provider}) - {duration}s")
            
        except Exception as e:
            self.logger.error(f"Error recording AI inference metrics: {e}")

    async def record_content_processing(
        self,
        content_type: str,
        format_type: str,
        status: str,
        duration: float = None
    ):
        """Record content processing metrics"""
        try:
            # Record content processed
            self.business_metrics['content_processed'].labels(
                type=content_type,
                format=format_type,
                status=status
            ).inc()
            
            # Record processing duration if provided
            if duration is not None:
                self.business_metrics['media_processing_duration'].labels(
                    format=format_type,
                    quality="standard",
                    service="content_processor"
                ).observe(duration)
            
            self.logger.debug(f"Recorded content processing: {content_type}/{format_type} - {status}")
            
        except Exception as e:
            self.logger.error(f"Error recording content processing metrics: {e}")

    async def update_service_health(self, service: str, instance: str, healthy: bool):
        """Update service health status"""
        try:
            self.service_metrics['service_health'].labels(
                service=service,
                instance=instance
            ).set(1 if healthy else 0)
            
            self.logger.debug(f"Updated service health: {service}@{instance} = {'healthy' if healthy else 'unhealthy'}")
            
        except Exception as e:
            self.logger.error(f"Error updating service health: {e}")

    async def update_sli_metrics(self, service: str, metrics_data: Dict[str, float]):
        """Update Service Level Indicators"""
        try:
            for metric_name, value in metrics_data.items():
                if metric_name in self.sli_metrics:
                    self.sli_metrics[metric_name].labels(service=service).set(value)
            
            self.logger.debug(f"Updated SLI metrics for {service}: {metrics_data}")
            
        except Exception as e:
            self.logger.error(f"Error updating SLI metrics: {e}")

    def create_alert_rules(self) -> List[AlertRule]:
        """Create enterprise alert rules"""
        rules = [
            # High error rate alert
            AlertRule(
                name="HighErrorRate",
                expression='rate(ainflue_http_requests_total{status_code=~"5.."}[5m]) > 0.05',
                duration="5m",
                severity=AlertSeverity.WARNING,
                summary="High error rate detected",
                description="Service {{ $labels.service }} has error rate above 5%",
                labels={"team": "platform"}
            ),
            
            # Service down alert
            AlertRule(
                name="ServiceDown",
                expression='ainflue_service_health == 0',
                duration="1m",
                severity=AlertSeverity.CRITICAL,
                summary="Service is down",
                description="Service {{ $labels.service }} instance {{ $labels.instance }} is unhealthy",
                labels={"team": "platform", "severity": "critical"}
            ),
            
            # High latency alert
            AlertRule(
                name="HighLatency",
                expression='histogram_quantile(0.95, rate(ainflue_http_request_duration_seconds_bucket[5m])) > 1.0',
                duration="5m",
                severity=AlertSeverity.WARNING,
                summary="High latency detected",
                description="Service {{ $labels.service }} has P95 latency above 1s",
                labels={"team": "platform"}
            ),
            
            # AI inference timeout alert
            AlertRule(
                name="AIInferenceTimeout",
                expression='rate(ainflue_ai_requests_total{status="timeout"}[5m]) > 0.01',
                duration="3m",
                severity=AlertSeverity.ERROR,
                summary="AI inference timeouts",
                description="AI model {{ $labels.model }} has timeout rate above 1%",
                labels={"team": "ai"}
            ),
            
            # Circuit breaker open alert
            AlertRule(
                name="CircuitBreakerOpen",
                expression='ainflue_circuit_breaker_state == 1',
                duration="1m",
                severity=AlertSeverity.WARNING,
                summary="Circuit breaker is open",
                description="Circuit breaker for {{ $labels.service }} -> {{ $labels.dependency }} is open",
                labels={"team": "platform"}
            )
        ]
        
        self.alert_rules = rules
        return rules

    def generate_prometheus_config(self) -> Dict[str, Any]:
        """Generate Prometheus configuration"""
        config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
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
            },
            "scrape_configs": [
                {
                    "job_name": "ainflue-core-services",
                    "static_configs": [
                        {
                            "targets": [
                                "core-service:8080",
                                "processing-service:8081",
                                "orchestration-service:8082"
                            ]
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s"
                },
                {
                    "job_name": "ainflue-business-metrics",
                    "static_configs": [
                        {
                            "targets": [
                                "api-gateway:8080",
                                "creator-service:8083",
                                "content-service:8084"
                            ]
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s"
                }
            ]
        }
        
        return config

    def generate_alert_rules_config(self) -> Dict[str, Any]:
        """Generate alert rules configuration"""
        rules = []
        
        for alert in self.alert_rules:
            rule = {
                "alert": alert.name,
                "expr": alert.expression,
                "for": alert.duration,
                "labels": {
                    "severity": alert.severity.value,
                    **alert.labels
                },
                "annotations": {
                    "summary": alert.summary,
                    "description": alert.description
                }
            }
            rules.append(rule)
        
        config = {
            "groups": [
                {
                    "name": "ainflue.rules",
                    "rules": rules
                }
            ]
        }
        
        return config

    def create_grafana_dashboards(self) -> List[DashboardConfig]:
        """Create Grafana dashboards"""
        dashboards = []
        
        # Service Overview Dashboard
        service_dashboard = DashboardConfig(
            title="Ainflue - Service Overview",
            tags=["ainflue", "services", "overview"],
            panels=[
                {
                    "title": "Request Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(ainflue_http_requests_total[5m])',
                            "legendFormat": "{{service}} - {{method}}"
                        }
                    ]
                },
                {
                    "title": "Response Times",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'histogram_quantile(0.95, rate(ainflue_http_request_duration_seconds_bucket[5m]))',
                            "legendFormat": "P95 - {{service}}"
                        },
                        {
                            "expr": 'histogram_quantile(0.99, rate(ainflue_http_request_duration_seconds_bucket[5m]))',
                            "legendFormat": "P99 - {{service}}"
                        }
                    ]
                },
                {
                    "title": "Error Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(ainflue_http_requests_total{status_code=~"5.."}[5m])',
                            "legendFormat": "5xx - {{service}}"
                        }
                    ]
                },
                {
                    "title": "Service Health",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": 'ainflue_service_health',
                            "legendFormat": "{{service}}@{{instance}}"
                        }
                    ]
                }
            ]
        )
        dashboards.append(service_dashboard)
        
        # AI/ML Dashboard
        ai_dashboard = DashboardConfig(
            title="Ainflue - AI/ML Performance",
            tags=["ainflue", "ai", "ml", "performance"],
            panels=[
                {
                    "title": "AI Inference Duration",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'histogram_quantile(0.95, rate(ainflue_ai_inference_duration_seconds_bucket[5m]))',
                            "legendFormat": "P95 - {{model}} ({{provider}})"
                        }
                    ]
                },
                {
                    "title": "AI Request Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(ainflue_ai_requests_total[5m])',
                            "legendFormat": "{{model}} - {{status}}"
                        }
                    ]
                },
                {
                    "title": "Content Processing",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(ainflue_content_processed_total[5m])',
                            "legendFormat": "{{type}} - {{status}}"
                        }
                    ]
                }
            ]
        )
        dashboards.append(ai_dashboard)
        
        # Business Metrics Dashboard
        business_dashboard = DashboardConfig(
            title="Ainflue - Business Metrics",
            tags=["ainflue", "business", "revenue", "creators"],
            panels=[
                {
                    "title": "Active Creators",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": 'ainflue_creators_active_total',
                            "legendFormat": "{{tier}} - {{region}}"
                        }
                    ]
                },
                {
                    "title": "Revenue Generated",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(ainflue_revenue_generated_euros[1h])',
                            "legendFormat": "{{creator_tier}} - {{content_type}}"
                        }
                    ]
                },
                {
                    "title": "Content Processing Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(ainflue_content_processed_total[5m])',
                            "legendFormat": "{{type}} - {{format}}"
                        }
                    ]
                }
            ]
        )
        dashboards.append(business_dashboard)
        
        self.dashboards = dashboards
        return dashboards

    async def export_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        try:
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return ""

    async def start_metrics_server(self, port: int = 8000):
        """Start Prometheus metrics HTTP server"""
        try:
            start_http_server(port, registry=self.registry)
            self.logger.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            self.logger.error(f"Error starting metrics server: {e}")

    async def save_configurations(self, output_dir: str = "/tmp/prometheus-config"):
        """Save all configurations to files"""
        import os
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Save Prometheus config
            prometheus_config = self.generate_prometheus_config()
            with open(f"{output_dir}/prometheus.yml", 'w') as f:
                yaml.dump(prometheus_config, f, default_flow_style=False)
            
            # Save alert rules
            alert_rules = self.generate_alert_rules_config()
            with open(f"{output_dir}/alert-rules.yml", 'w') as f:
                yaml.dump(alert_rules, f, default_flow_style=False)
            
            # Save dashboard configs
            for i, dashboard in enumerate(self.dashboards):
                dashboard_json = {
                    "dashboard": {
                        "title": dashboard.title,
                        "tags": dashboard.tags,
                        "panels": dashboard.panels,
                        "time": dashboard.time_range,
                        "refresh": dashboard.refresh
                    }
                }
                with open(f"{output_dir}/dashboard-{i+1}.json", 'w') as f:
                    json.dump(dashboard_json, f, indent=2)
            
            self.logger.info(f"Configurations saved to {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Error saving configurations: {e}")


# Enterprise singleton instance
_observability_instance: Optional[PrometheusObservability] = None

def get_observability() -> PrometheusObservability:
    """Get singleton observability instance"""
    global _observability_instance
    if _observability_instance is None:
        config = {
            "enabled": True,
            "metrics_port": 8000,
            "alert_manager_url": "http://alertmanager:9093",
            "grafana_url": "http://grafana:3000"
        }
        _observability_instance = PrometheusObservability(config)
    return _observability_instance


# Export enterprise classes
__all__ = [
    'PrometheusObservability',
    'MetricDefinition',
    'AlertRule', 
    'DashboardConfig',
    'MetricType',
    'AlertSeverity',
    'get_observability'
]


if __name__ == "__main__":
    # Demo enterprise observability
    async def demo_observability():
        obs = get_observability()
        
        # Create alert rules
        obs.create_alert_rules()
        
        # Create dashboards
        obs.create_grafana_dashboards()
        
        # Record sample metrics
        await obs.record_http_request("GET", "/api/creators", 200, 0.045, "creator-service")
        await obs.record_ai_inference("gpt-4", "openai", 0.850, "success", "ai-service")
        await obs.record_content_processing("video", "mp4", "processed", 15.2)
        
        # Update health status
        await obs.update_service_health("creator-service", "instance-1", True)
        
        # Export configurations
        await obs.save_configurations()
        
        print("✅ Enterprise Prometheus Observability Demo Complete")
        print("📊 Metrics, Alerts, and Dashboards configured")
        print("🔧 Configuration files saved to /tmp/prometheus-config")
    
    asyncio.run(demo_observability())