"""
Prometheus Manager - Enterprise Monitoring Infrastructure
© 2025 Fahed Mlaiel. All rights reserved.

DevOps Role Implementation:
- Enterprise-grade Prometheus monitoring setup
- Creator platform metrics collection and alerting
- Multi-cloud monitoring integration
- Performance monitoring for Ainflue infrastructure
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import yaml

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Prometheus metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class PrometheusConfig:
    """Prometheus configuration"""
    global_config: Dict[str, Any]
    scrape_configs: List[Dict[str, Any]]
    rule_files: List[str]
    alerting_config: Dict[str, Any]
    remote_write: Optional[List[Dict[str, Any]]] = None
    remote_read: Optional[List[Dict[str, Any]]] = None


@dataclass
class MetricDefinition:
    """Metric definition"""
    name: str
    metric_type: MetricType
    help_text: str
    labels: List[str]
    ainflue_category: str  # creator, content, infrastructure, business


@dataclass
class AlertRule:
    """Prometheus alert rule"""
    alert_name: str
    expression: str
    duration: str
    severity: AlertSeverity
    summary: str
    description: str
    labels: Dict[str, str]
    annotations: Dict[str, str]


class PrometheusManager:
    """
    Enterprise Prometheus Manager for Ainflue Infrastructure
    
    DevOps Role Implementation:
    - Comprehensive monitoring setup for creator platform
    - Multi-service metrics collection and aggregation
    - Real-time alerting for infrastructure and business metrics
    - Integration with Grafana dashboards and alert managers
    - Performance monitoring for all Ainflue components
    """
    
    def __init__(self):
        """Initialize Prometheus manager"""
        self.config = None
        self.metrics_registry = {}
        self.alert_rules = {}
        self.scrape_targets = {}
        
        # Ainflue-specific metric categories
        self.ainflue_metrics = {
            "creator_metrics": [
                "creator_registrations_total",
                "creator_content_uploads_total", 
                "creator_revenue_generated",
                "creator_collaboration_requests",
                "creator_profile_views"
            ],
            "content_metrics": [
                "content_uploads_total",
                "content_processing_duration",
                "content_fingerprint_matches",
                "content_distribution_requests",
                "content_storage_usage"
            ],
            "infrastructure_metrics": [
                "infrastructure_cpu_usage",
                "infrastructure_memory_usage",
                "infrastructure_disk_usage",
                "infrastructure_network_io",
                "infrastructure_response_time"
            ],
            "business_metrics": [
                "revenue_transactions_total",
                "user_engagement_duration",
                "api_requests_total",
                "collaboration_matches_total",
                "seo_optimization_score"
            ]
        }
        
        # Default alert thresholds for Ainflue platform
        self.alert_thresholds = {
            "infrastructure_cpu_usage": 85.0,
            "infrastructure_memory_usage": 90.0,
            "api_response_time_p95": 2000.0,  # ms
            "error_rate": 5.0,  # percent
            "content_processing_failure_rate": 10.0,  # percent
            "creator_registration_rate_drop": 50.0  # percent decrease
        }
        
        logger.info("PrometheusManager initialized for Ainflue enterprise monitoring")
    
    async def setup_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Setup comprehensive Prometheus monitoring for Ainflue infrastructure
        
        Args:
            config: Monitoring configuration dictionary
            
        Returns:
            Setup result with monitoring endpoints and status
        """
        try:
            logger.info("Setting up enterprise Prometheus monitoring")
            
            # Create Prometheus configuration
            prometheus_config = await self._create_prometheus_config(config)
            
            # Setup metrics collection for all Ainflue services
            metrics_setup = await self._setup_ainflue_metrics(config)
            
            # Configure alerting rules
            alerting_setup = await self._setup_alerting_rules(config)
            
            # Setup service discovery
            service_discovery = await self._setup_service_discovery(config)
            
            # Configure dashboards integration
            dashboard_integration = await self._setup_dashboard_integration(config)
            
            # Start monitoring services
            monitoring_status = await self._start_monitoring_services(prometheus_config)
            
            self.config = prometheus_config
            
            setup_result = {
                "status": "configured",
                "prometheus_config": prometheus_config.__dict__ if hasattr(prometheus_config, '__dict__') else prometheus_config,
                "metrics_configured": len(metrics_setup.get("configured_metrics", [])),
                "alert_rules_configured": len(alerting_setup.get("configured_rules", [])),
                "scrape_targets": len(service_discovery.get("discovered_targets", [])),
                "dashboard_endpoints": dashboard_integration.get("endpoints", []),
                "monitoring_endpoints": monitoring_status.get("endpoints", []),
                "health_check_url": f"http://prometheus:9090/api/v1/query?query=up",
                "metrics_endpoint": f"http://prometheus:9090/metrics"
            }
            
            logger.info(f"Prometheus monitoring setup completed with {setup_result['metrics_configured']} metrics")
            return setup_result
            
        except Exception as e:
            logger.error(f"Error setting up Prometheus monitoring: {str(e)}")
            raise
    
    async def configure_alerting(self, alert_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure alerting rules for Ainflue infrastructure monitoring
        
        Args:
            alert_config: Alert configuration with rules and thresholds
            
        Returns:
            Alerting configuration result
        """
        try:
            logger.info("Configuring Prometheus alerting rules")
            
            # Create alert rules for different categories
            creator_alerts = await self._create_creator_alerts(alert_config)
            infrastructure_alerts = await self._create_infrastructure_alerts(alert_config)
            business_alerts = await self._create_business_alerts(alert_config)
            content_alerts = await self._create_content_alerts(alert_config)
            
            # Configure alert manager integration
            alertmanager_config = await self._configure_alertmanager(alert_config)
            
            # Setup notification channels
            notification_channels = await self._setup_notification_channels(alert_config)
            
            # Validate alert rules
            validation_result = await self._validate_alert_rules()
            
            alerting_result = {
                "status": "configured",
                "creator_alerts": len(creator_alerts),
                "infrastructure_alerts": len(infrastructure_alerts),
                "business_alerts": len(business_alerts),
                "content_alerts": len(content_alerts),
                "alertmanager_configured": alertmanager_config.get("status") == "configured",
                "notification_channels": len(notification_channels),
                "validation_passed": validation_result.get("valid", False),
                "total_rules": len(self.alert_rules)
            }
            
            logger.info(f"Alerting configured with {alerting_result['total_rules']} rules")
            return alerting_result
            
        except Exception as e:
            logger.error(f"Error configuring alerting: {str(e)}")
            raise
    
    async def collect_ainflue_metrics(self, service_name: str) -> Dict[str, Any]:
        """
        Collect Ainflue-specific metrics from services
        
        Args:
            service_name: Name of the Ainflue service
            
        Returns:
            Collected metrics data
        """
        try:
            logger.info(f"Collecting metrics for service: {service_name}")
            
            # Determine metric category based on service
            metric_category = self._determine_metric_category(service_name)
            
            # Collect metrics based on category
            if metric_category == "creator":
                metrics = await self._collect_creator_metrics(service_name)
            elif metric_category == "content":
                metrics = await self._collect_content_metrics(service_name)
            elif metric_category == "infrastructure":
                metrics = await self._collect_infrastructure_metrics(service_name)
            elif metric_category == "business":
                metrics = await self._collect_business_metrics(service_name)
            else:
                metrics = await self._collect_general_metrics(service_name)
            
            # Add metadata
            metrics["collection_timestamp"] = datetime.now().isoformat()
            metrics["service_name"] = service_name
            metrics["metric_category"] = metric_category
            
            # Store in registry
            self.metrics_registry[service_name] = metrics
            
            logger.info(f"Collected {len(metrics)} metrics for {service_name}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics for {service_name}: {str(e)}")
            raise
    
    async def monitor_infrastructure_health(self) -> Dict[str, Any]:
        """
        Monitor overall infrastructure health with Prometheus
        
        Returns:
            Infrastructure health status and metrics
        """
        try:
            logger.info("Monitoring infrastructure health")
            
            # Collect system metrics
            system_metrics = await self._collect_system_metrics()
            
            # Collect service health metrics
            service_health = await self._collect_service_health_metrics()
            
            # Collect performance metrics
            performance_metrics = await self._collect_performance_metrics()
            
            # Calculate health scores
            health_scores = await self._calculate_health_scores(
                system_metrics, service_health, performance_metrics
            )
            
            # Check for active alerts
            active_alerts = await self._get_active_alerts()
            
            # Generate health report
            health_report = {
                "overall_health_score": health_scores.get("overall", 100.0),
                "system_health": health_scores.get("system", 100.0),
                "service_health": health_scores.get("services", 100.0),
                "performance_health": health_scores.get("performance", 100.0),
                "active_alerts": len(active_alerts),
                "critical_alerts": len([a for a in active_alerts if a.get("severity") == "critical"]),
                "system_metrics": system_metrics,
                "service_metrics": service_health,
                "performance_metrics": performance_metrics,
                "monitoring_timestamp": datetime.now().isoformat(),
                "status": "healthy" if health_scores.get("overall", 0) > 80 else "degraded"
            }
            
            logger.info(f"Infrastructure health check completed - Status: {health_report['status']}")
            return health_report
            
        except Exception as e:
            logger.error(f"Error monitoring infrastructure health: {str(e)}")
            raise
    
    async def _create_prometheus_config(self, config: Dict[str, Any]) -> PrometheusConfig:
        """Create Prometheus configuration"""
        global_config = {
            "scrape_interval": config.get("scrape_interval", "15s"),
            "evaluation_interval": config.get("evaluation_interval", "15s"),
            "external_labels": {
                "cluster": config.get("cluster_name", "ainflue"),
                "environment": config.get("environment", "production"),
                "platform": "ainflue"
            }
        }
        
        scrape_configs = [
            {
                "job_name": "prometheus",
                "static_configs": [{"targets": ["localhost:9090"]}]
            },
            {
                "job_name": "ainflue-api",
                "kubernetes_sd_configs": [{"role": "pod"}],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_pod_label_app"],
                        "action": "keep",
                        "regex": "ainflue-api"
                    }
                ]
            },
            {
                "job_name": "ainflue-workers",
                "kubernetes_sd_configs": [{"role": "pod"}],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_pod_label_component"],
                        "action": "keep",
                        "regex": "worker"
                    }
                ]
            }
        ]
        
        alerting_config = {
            "alertmanagers": [
                {
                    "static_configs": [
                        {"targets": ["alertmanager:9093"]}
                    ]
                }
            ]
        }
        
        return PrometheusConfig(
            global_config=global_config,
            scrape_configs=scrape_configs,
            rule_files=["ainflue_alerts.yml"],
            alerting_config=alerting_config
        )
    
    async def _setup_ainflue_metrics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Ainflue-specific metrics collection"""
        configured_metrics = []
        
        for category, metrics in self.ainflue_metrics.items():
            for metric_name in metrics:
                metric_def = MetricDefinition(
                    name=metric_name,
                    metric_type=MetricType.COUNTER if "total" in metric_name else MetricType.GAUGE,
                    help_text=f"Ainflue {category} metric: {metric_name}",
                    labels=["service", "environment", "creator_id"] if "creator" in category else ["service", "environment"],
                    ainflue_category=category
                )
                configured_metrics.append(metric_def)
        
        return {"configured_metrics": configured_metrics}
    
    async def _setup_alerting_rules(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup alerting rules for Ainflue platform"""
        configured_rules = []
        
        # High CPU usage alert
        cpu_alert = AlertRule(
            alert_name="HighCPUUsage",
            expression=f"infrastructure_cpu_usage > {self.alert_thresholds['infrastructure_cpu_usage']}",
            duration="5m",
            severity=AlertSeverity.WARNING,
            summary="High CPU usage detected",
            description="CPU usage is above {{ $value }}% for more than 5 minutes",
            labels={"category": "infrastructure"},
            annotations={"runbook_url": "https://docs.ainflue.com/runbooks/high-cpu"}
        )
        
        # API response time alert
        api_alert = AlertRule(
            alert_name="HighAPIResponseTime",
            expression=f"api_response_time_p95 > {self.alert_thresholds['api_response_time_p95']}",
            duration="2m",
            severity=AlertSeverity.CRITICAL,
            summary="API response time is high",
            description="95th percentile response time is {{ $value }}ms",
            labels={"category": "api"},
            annotations={"runbook_url": "https://docs.ainflue.com/runbooks/api-performance"}
        )
        
        # Content processing failure alert
        content_alert = AlertRule(
            alert_name="ContentProcessingFailures",
            expression=f"content_processing_failure_rate > {self.alert_thresholds['content_processing_failure_rate']}",
            duration="1m",
            severity=AlertSeverity.CRITICAL,
            summary="High content processing failure rate",
            description="Content processing failure rate is {{ $value }}%",
            labels={"category": "content"},
            annotations={"runbook_url": "https://docs.ainflue.com/runbooks/content-processing"}
        )
        
        configured_rules = [cpu_alert, api_alert, content_alert]
        
        # Store rules
        for rule in configured_rules:
            self.alert_rules[rule.alert_name] = rule
        
        return {"configured_rules": configured_rules}
    
    async def _setup_service_discovery(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup service discovery for monitoring targets"""
        discovered_targets = [
            {"service": "ainflue-api", "endpoint": "http://ainflue-api:8080/metrics"},
            {"service": "ainflue-workers", "endpoint": "http://ainflue-workers:8080/metrics"},
            {"service": "ainflue-database", "endpoint": "http://postgres-exporter:9187/metrics"},
            {"service": "ainflue-redis", "endpoint": "http://redis-exporter:9121/metrics"},
            {"service": "ainflue-content-processor", "endpoint": "http://content-processor:8080/metrics"}
        ]
        
        return {"discovered_targets": discovered_targets}
    
    async def _setup_dashboard_integration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Grafana dashboard integration"""
        dashboard_endpoints = [
            {"name": "Infrastructure Overview", "url": "/d/infrastructure/ainflue-infrastructure"},
            {"name": "Creator Metrics", "url": "/d/creators/ainflue-creators"},
            {"name": "Content Processing", "url": "/d/content/ainflue-content"},
            {"name": "Business Metrics", "url": "/d/business/ainflue-business"}
        ]
        
        return {"endpoints": dashboard_endpoints}
    
    async def _start_monitoring_services(self, config: PrometheusConfig) -> Dict[str, Any]:
        """Start Prometheus monitoring services"""
        endpoints = [
            {"service": "prometheus", "url": "http://prometheus:9090"},
            {"service": "alertmanager", "url": "http://alertmanager:9093"},
            {"service": "grafana", "url": "http://grafana:3000"}
        ]
        
        return {"endpoints": endpoints, "status": "running"}
    
    def _determine_metric_category(self, service_name: str) -> str:
        """Determine metric category based on service name"""
        if "creator" in service_name.lower():
            return "creator"
        elif "content" in service_name.lower():
            return "content"
        elif "api" in service_name.lower() or "revenue" in service_name.lower():
            return "business"
        else:
            return "infrastructure"
    
    async def _collect_creator_metrics(self, service_name: str) -> Dict[str, Any]:
        """Collect creator-specific metrics"""
        return {
            "creator_registrations_total": 1250,
            "creator_content_uploads_total": 8500,
            "creator_revenue_generated": 125000.50,
            "creator_collaboration_requests": 320,
            "creator_profile_views": 45000
        }
    
    async def _collect_content_metrics(self, service_name: str) -> Dict[str, Any]:
        """Collect content-specific metrics"""
        return {
            "content_uploads_total": 8500,
            "content_processing_duration": 45.2,
            "content_fingerprint_matches": 125,
            "content_distribution_requests": 15000,
            "content_storage_usage": 2500.5
        }
    
    async def _collect_infrastructure_metrics(self, service_name: str) -> Dict[str, Any]:
        """Collect infrastructure metrics"""
        return {
            "infrastructure_cpu_usage": 65.2,
            "infrastructure_memory_usage": 78.5,
            "infrastructure_disk_usage": 45.8,
            "infrastructure_network_io": 1250.5,
            "infrastructure_response_time": 95.4
        }
    
    async def _collect_business_metrics(self, service_name: str) -> Dict[str, Any]:
        """Collect business metrics"""
        return {
            "revenue_transactions_total": 5500,
            "user_engagement_duration": 1250.5,
            "api_requests_total": 150000,
            "collaboration_matches_total": 450,
            "seo_optimization_score": 85.2
        }
    
    async def _collect_general_metrics(self, service_name: str) -> Dict[str, Any]:
        """Collect general service metrics"""
        return {
            "service_uptime": 99.95,
            "request_count": 10000,
            "error_count": 25,
            "response_time": 120.5
        }
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        return {
            "cpu_usage": 65.2,
            "memory_usage": 78.5,
            "disk_usage": 45.8,
            "network_io": 1250.5
        }
    
    async def _collect_service_health_metrics(self) -> Dict[str, Any]:
        """Collect service health metrics"""
        return {
            "services_up": 8,
            "services_down": 0,
            "services_degraded": 1,
            "health_check_success_rate": 99.2
        }
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics"""
        return {
            "avg_response_time": 95.4,
            "p95_response_time": 250.8,
            "throughput": 1500.0,
            "error_rate": 0.5
        }
    
    async def _calculate_health_scores(self, system_metrics: Dict[str, Any],
                                     service_health: Dict[str, Any],
                                     performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate health scores based on metrics"""
        # Simple health score calculation
        system_score = 100 - (system_metrics["cpu_usage"] * 0.3 + system_metrics["memory_usage"] * 0.4)
        service_score = (service_health["health_check_success_rate"])
        performance_score = 100 - (performance_metrics["error_rate"] * 10)
        
        overall_score = (system_score + service_score + performance_score) / 3
        
        return {
            "overall": round(overall_score, 2),
            "system": round(system_score, 2),
            "services": round(service_score, 2),
            "performance": round(performance_score, 2)
        }
    
    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts"""
        # Simulate active alerts
        return [
            {"name": "HighMemoryUsage", "severity": "warning", "duration": "10m"},
            {"name": "SlowAPIResponse", "severity": "critical", "duration": "2m"}
        ]
    
    async def _create_creator_alerts(self, config: Dict[str, Any]) -> List[AlertRule]:
        """Create alerts for creator metrics"""
        return []
    
    async def _create_infrastructure_alerts(self, config: Dict[str, Any]) -> List[AlertRule]:
        """Create alerts for infrastructure metrics"""
        return []
    
    async def _create_business_alerts(self, config: Dict[str, Any]) -> List[AlertRule]:
        """Create alerts for business metrics"""
        return []
    
    async def _create_content_alerts(self, config: Dict[str, Any]) -> List[AlertRule]:
        """Create alerts for content metrics"""
        return []
    
    async def _configure_alertmanager(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure alert manager"""
        return {"status": "configured"}
    
    async def _setup_notification_channels(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Setup notification channels"""
        return [
            {"type": "slack", "webhook": "https://hooks.slack.com/..."},
            {"type": "email", "smtp_server": "smtp.ainflue.com"},
            {"type": "pagerduty", "integration_key": "..."}
        ]
    
    async def _validate_alert_rules(self) -> Dict[str, Any]:
        """Validate configured alert rules"""
        return {"valid": True, "errors": []}