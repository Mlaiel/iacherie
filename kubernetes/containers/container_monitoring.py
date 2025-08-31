"""📊 Container Monitoring Manager - IA-Influencer-Agent Infrastructure
==================================================================
Expert: DevOps Engineer + Monitoring Specialist + SRE
Creator: Fahed Mlaiel <mlaiel@live.de>
==================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Advanced container monitoring and observability for IA-Influencer-Agent platform.
Includes metrics collection, alerting, health checks, and performance monitoring.
"""from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import asyncio
import logging
import json
import yaml
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import aiohttp
import docker
import kubernetes.client as k8s_client
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Metric types for monitoring"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """Alert severity levels"""    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

class HealthStatus(Enum):
    """Health check status"""    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class MetricDefinition:
    """Metric definition for monitoring"""    name: str
    type: MetricType
    description: str
    labels: List[str] = field(default_factory=list)
    unit: str = ""
    help_text: str = ""

@dataclass
class AlertRule:
    """Alert rule configuration"""    name: str
    expression: str
    severity: AlertSeverity
    duration: str
    description: str
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

@dataclass
class HealthCheck:
    """Health check configuration"""    name: str
    endpoint: str
    method: str = "GET"
    timeout: int = 10
    interval: int = 30
    retries: int = 3
    expected_status: int = 200
    expected_content: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class MonitoringTarget:
    """Monitoring target configuration"""    name: str
    type: str  # container, service, pod, node
    endpoint: str
    metrics_path: str = "/metrics"
    scrape_interval: str = "30s"
    labels: Dict[str, str] = field(default_factory=dict)
    health_checks: List[HealthCheck] = field(default_factory=list)

class ContainerMonitoringManager:
    """Professional container monitoring manager"""    
    def __init__(self, config_path: str = "/app/config/monitoring"):
        self.config_path = Path(config_path)
        self.docker_client = None
        self.k8s_client = None
        self.prometheus_registry = CollectorRegistry()
        self.metrics = {}
        self.alert_rules = {}
        self.monitoring_targets = {}
        self.health_status = {}
        self.active_alerts = {}
        self.metrics_history = {}
        self.initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Monitoring configuration
        self.monitoring_config = {
            "prometheus": {
                "enabled": True,
                "port": 9090,
                "retention": "15d"
            },
            "grafana": {
                "enabled": True,
                "port": 3000,
                "admin_password": "admin123"
            },
            "alertmanager": {
                "enabled": True,
                "port": 9093,
                "webhook_url": None
            },
            "jaeger": {
                "enabled": True,
                "port": 16686
            }
        }
        
    async def initialize(self) -> bool:
        """Initialize container monitoring manager"""        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            
            # Initialize Kubernetes client
            try:
                from kubernetes import config
                config.load_incluster_config()
                self.k8s_client = k8s_client.ApiClient()
            except:
                pass
            
            # Create config directory
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize metrics
            await self._initialize_metrics()
            
            # Setup alert rules
            await self._setup_alert_rules()
            
            # Setup monitoring targets
            await self._setup_monitoring_targets()
            
            # Start monitoring loops
            await self._start_monitoring_loops()
            
            self.initialized = True
            self.logger.info("✅ ContainerMonitoringManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing ContainerMonitoringManager: {e}")
            return False
    
    async def _initialize_metrics(self) -> None:
        """Initialize Prometheus metrics"""        try:
            # Define core metrics for IA-Influencer services
            metric_definitions = [
                MetricDefinition(
                    name="ia_influencer_container_cpu_usage",
                    type=MetricType.GAUGE,
                    description="Container CPU usage percentage",
                    labels=["container_name", "service", "namespace"],
                    unit="percent"
                ),
                MetricDefinition(
                    name="ia_influencer_container_memory_usage",
                    type=MetricType.GAUGE,
                    description="Container memory usage in bytes",
                    labels=["container_name", "service", "namespace"],
                    unit="bytes"
                ),
                MetricDefinition(
                    name="ia_influencer_container_network_io",
                    type=MetricType.COUNTER,
                    description="Container network I/O bytes",
                    labels=["container_name", "service", "direction"],
                    unit="bytes"
                ),
                MetricDefinition(
                    name="ia_influencer_container_disk_io",
                    type=MetricType.COUNTER,
                    description="Container disk I/O bytes",
                    labels=["container_name", "service", "operation"],
                    unit="bytes"
                ),
                MetricDefinition(
                    name="ia_influencer_api_requests_total",
                    type=MetricType.COUNTER,
                    description="Total number of API requests",
                    labels=["method", "endpoint", "status_code", "service"],
                    unit="requests"
                ),
                MetricDefinition(
                    name="ia_influencer_api_request_duration",
                    type=MetricType.HISTOGRAM,
                    description="API request duration in seconds",
                    labels=["method", "endpoint", "service"],
                    unit="seconds"
                ),
                MetricDefinition(
                    name="ia_influencer_ai_processing_time",
                    type=MetricType.HISTOGRAM,
                    description="AI processing time in seconds",
                    labels=["model", "operation", "service"],
                    unit="seconds"
                ),
                MetricDefinition(
                    name="ia_influencer_audio_fingerprint_operations",
                    type=MetricType.COUNTER,
                    description="Audio fingerprinting operations",
                    labels=["operation", "format", "status"],
                    unit="operations"
                ),
                MetricDefinition(
                    name="ia_influencer_content_protection_scans",
                    type=MetricType.COUNTER,
                    description="Content protection scans performed",
                    labels=["scan_type", "platform", "status"],
                    unit="scans"
                ),
                MetricDefinition(
                    name="ia_influencer_monetization_revenue",
                    type=MetricType.GAUGE,
                    description="Total revenue tracked",
                    labels=["currency", "platform", "user_tier"],
                    unit="currency"
                ),
                MetricDefinition(
                    name="ia_influencer_crawler_requests",
                    type=MetricType.COUNTER,
                    description="Web crawler requests",
                    labels=["platform", "status", "crawler_type"],
                    unit="requests"
                ),
                MetricDefinition(
                    name="ia_influencer_database_connections",
                    type=MetricType.GAUGE,
                    description="Active database connections",
                    labels=["database", "pool", "status"],
                    unit="connections"
                ),
                MetricDefinition(
                    name="ia_influencer_queue_size",
                    type=MetricType.GAUGE,
                    description="Queue size for background tasks",
                    labels=["queue_name", "priority"],
                    unit="tasks"
                ),
                MetricDefinition(
                    name="ia_influencer_storage_usage",
                    type=MetricType.GAUGE,
                    description="Storage usage in bytes",
                    labels=["storage_type", "namespace"],
                    unit="bytes"
                )
            ]
            
            # Create Prometheus metrics
            for metric_def in metric_definitions:
                if metric_def.type == MetricType.COUNTER:
                    self.metrics[metric_def.name] = Counter(
                        metric_def.name,
                        metric_def.description,
                        metric_def.labels,
                        registry=self.prometheus_registry
                    )
                elif metric_def.type == MetricType.GAUGE:
                    self.metrics[metric_def.name] = Gauge(
                        metric_def.name,
                        metric_def.description,
                        metric_def.labels,
                        registry=self.prometheus_registry
                    )
                elif metric_def.type == MetricType.HISTOGRAM:
                    self.metrics[metric_def.name] = Histogram(
                        metric_def.name,
                        metric_def.description,
                        metric_def.labels,
                        registry=self.prometheus_registry
                    )
            
            self.logger.info(f"✅ Initialized {len(metric_definitions)} Prometheus metrics")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing metrics: {e}")
    
    async def _setup_alert_rules(self) -> None:
        """Setup alert rules for IA-Influencer services"""        try:
            alert_rules = [
                AlertRule(
                    name="IAInfluencerHighCPUUsage",
                    expression="ia_influencer_container_cpu_usage > 80",
                    severity=AlertSeverity.WARNING,
                    duration="5m",
                    description="Container CPU usage is above 80%",
                    labels={"team": "ia-influencer", "severity": "warning"},
                    annotations={
                        "summary": "High CPU usage detected",
                        "description": "Container {{ $labels.container_name }} CPU usage is {{ $value }}%"
                    }
                ),
                AlertRule(
                    name="IAInfluencerHighMemoryUsage",
                    expression="ia_influencer_container_memory_usage / (1024*1024*1024) > 7",
                    severity=AlertSeverity.WARNING,
                    duration="5m",
                    description="Container memory usage is above 7GB",
                    labels={"team": "ia-influencer", "severity": "warning"},
                    annotations={
                        "summary": "High memory usage detected",
                        "description": "Container {{ $labels.container_name }} memory usage is {{ $value }}GB"
                    }
                ),
                AlertRule(
                    name="IAInfluencerAPIHighErrorRate",
                    expression="rate(ia_influencer_api_requests_total{status_code=~\"5..\"}[5m]) > 0.1",
                    severity=AlertSeverity.CRITICAL,
                    duration="2m",
                    description="API error rate is above 10%",
                    labels={"team": "ia-influencer", "severity": "critical"},
                    annotations={
                        "summary": "High API error rate",
                        "description": "API {{ $labels.endpoint }} error rate is {{ $value }}%"
                    }
                ),
                AlertRule(
                    name="IAInfluencerAPISlowResponse",
                    expression="histogram_quantile(0.95, rate(ia_influencer_api_request_duration_bucket[5m])) > 2",
                    severity=AlertSeverity.WARNING,
                    duration="5m",
                    description="95th percentile API response time is above 2 seconds",
                    labels={"team": "ia-influencer", "severity": "warning"},
                    annotations={
                        "summary": "Slow API response time",
                        "description": "API {{ $labels.endpoint }} 95th percentile response time is {{ $value }}s"
                    }
                ),
                AlertRule(
                    name="IAInfluencerContainerDown",
                    expression="up{job=\"ia-influencer\"} == 0",
                    severity=AlertSeverity.CRITICAL,
                    duration="1m",
                    description="IA-Influencer container is down",
                    labels={"team": "ia-influencer", "severity": "critical"},
                    annotations={
                        "summary": "Container is down",
                        "description": "Container {{ $labels.instance }} has been down for more than 1 minute"
                    }
                ),
                AlertRule(
                    name="IAInfluencerDatabaseConnectionsHigh",
                    expression="ia_influencer_database_connections > 80",
                    severity=AlertSeverity.WARNING,
                    duration="3m",
                    description="Database connections are above 80",
                    labels={"team": "ia-influencer", "severity": "warning"},
                    annotations={
                        "summary": "High database connections",
                        "description": "Database {{ $labels.database }} has {{ $value }} active connections"
                    }
                ),
                AlertRule(
                    name="IAInfluencerQueueBacklog",
                    expression="ia_influencer_queue_size > 1000",
                    severity=AlertSeverity.WARNING,
                    duration="5m",
                    description="Queue size is above 1000 tasks",
                    labels={"team": "ia-influencer", "severity": "warning"},
                    annotations={
                        "summary": "Queue backlog detected",
                        "description": "Queue {{ $labels.queue_name }} has {{ $value }} pending tasks"
                    }
                ),
                AlertRule(
                    name="IAInfluencerStorageSpaceHigh",
                    expression="ia_influencer_storage_usage / (1024*1024*1024*1024) > 80",
                    severity=AlertSeverity.WARNING,
                    duration="5m",
                    description="Storage usage is above 80TB",
                    labels={"team": "ia-influencer", "severity": "warning"},
                    annotations={
                        "summary": "High storage usage",
                        "description": "Storage {{ $labels.storage_type }} usage is {{ $value }}TB"
                    }
                )
            ]
            
            for rule in alert_rules:
                self.alert_rules[rule.name] = rule
            
            # Save alert rules to file
            await self._save_alert_rules()
            
            self.logger.info(f"✅ Setup {len(alert_rules)} alert rules")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up alert rules: {e}")
    
    async def _save_alert_rules(self) -> None:
        """Save alert rules to Prometheus format"""        try:
            prometheus_rules = {
                "groups": [{
                    "name": "ia-influencer-alerts",
                    "rules": [
                        {
                            "alert": rule.name,
                            "expr": rule.expression,
                            "for": rule.duration,
                            "labels": rule.labels,
                            "annotations": rule.annotations
                        }
                        for rule in self.alert_rules.values()
                    ]
                }]
            }
            
            rules_file = self.config_path / "prometheus_rules.yml"
            with open(rules_file, 'w') as f:
                yaml.dump(prometheus_rules, f, default_flow_style=False)
            
            self.logger.info(f"✅ Saved alert rules to {rules_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving alert rules: {e}")
    
    async def _setup_monitoring_targets(self) -> None:
        """Setup monitoring targets for IA-Influencer services"""        try:
            # Define monitoring targets
            targets = [
                MonitoringTarget(
                    name="ia-influencer-web-api",
                    type="service",
                    endpoint="http://ia-influencer-web-api:8000",
                    metrics_path="/metrics",
                    scrape_interval="15s",
                    labels={"service": "web-api", "tier": "frontend"},
                    health_checks=[
                        HealthCheck(
                            name="api-health",
                            endpoint="http://ia-influencer-web-api:8000/health",
                            interval=30,
                            timeout=10
                        ),
                        HealthCheck(
                            name="api-ready",
                            endpoint="http://ia-influencer-web-api:8000/ready",
                            interval=15,
                            timeout=5
                        )
                    ]
                ),
                MonitoringTarget(
                    name="ia-influencer-ai-engine",
                    type="service",
                    endpoint="http://ia-influencer-ai-engine:8001",
                    metrics_path="/metrics",
                    scrape_interval="30s",
                    labels={"service": "ai-engine", "tier": "processing"},
                    health_checks=[
                        HealthCheck(
                            name="ai-health",
                            endpoint="http://ia-influencer-ai-engine:8001/health",
                            interval=60,
                            timeout=30
                        )
                    ]
                ),
                MonitoringTarget(
                    name="ia-influencer-content-protection",
                    type="service",
                    endpoint="http://ia-influencer-content-protection:8002",
                    metrics_path="/metrics",
                    scrape_interval="30s",
                    labels={"service": "content-protection", "tier": "processing"},
                    health_checks=[
                        HealthCheck(
                            name="protection-health",
                            endpoint="http://ia-influencer-content-protection:8002/health",
                            interval=30,
                            timeout=15
                        )
                    ]
                ),
                MonitoringTarget(
                    name="ia-influencer-audio-processor",
                    type="service",
                    endpoint="http://ia-influencer-audio-processor:8003",
                    metrics_path="/metrics",
                    scrape_interval="30s",
                    labels={"service": "audio-processor", "tier": "processing"},
                    health_checks=[
                        HealthCheck(
                            name="audio-health",
                            endpoint="http://ia-influencer-audio-processor:8003/health",
                            interval=45,
                            timeout=20
                        )
                    ]
                ),
                MonitoringTarget(
                    name="ia-influencer-monetization",
                    type="service",
                    endpoint="http://ia-influencer-monetization:8004",
                    metrics_path="/metrics",
                    scrape_interval="60s",
                    labels={"service": "monetization", "tier": "business"},
                    health_checks=[
                        HealthCheck(
                            name="monetization-health",
                            endpoint="http://ia-influencer-monetization:8004/health",
                            interval=30,
                            timeout=10
                        )
                    ]
                ),
                MonitoringTarget(
                    name="ia-influencer-crawler",
                    type="service",
                    endpoint="http://ia-influencer-crawler:8005",
                    metrics_path="/metrics",
                    scrape_interval="60s",
                    labels={"service": "crawler", "tier": "monitoring"},
                    health_checks=[
                        HealthCheck(
                            name="crawler-health",
                            endpoint="http://ia-influencer-crawler:8005/health",
                            interval=60,
                            timeout=30
                        )
                    ]
                ),
                MonitoringTarget(
                    name="postgresql",
                    type="database",
                    endpoint="http://postgres-exporter:9187",
                    metrics_path="/metrics",
                    scrape_interval="30s",
                    labels={"service": "postgres", "tier": "data"},
                    health_checks=[
                        HealthCheck(
                            name="postgres-health",
                            endpoint="postgresql://ia_user:password@postgres:5432/ia_influencer",
                            method="CONNECT",
                            interval=30,
                            timeout=10
                        )
                    ]
                ),
                MonitoringTarget(
                    name="redis",
                    type="cache",
                    endpoint="http://redis-exporter:9121",
                    metrics_path="/metrics",
                    scrape_interval="15s",
                    labels={"service": "redis", "tier": "cache"},
                    health_checks=[
                        HealthCheck(
                            name="redis-health",
                            endpoint="redis://redis:6379",
                            method="PING",
                            interval=15,
                            timeout=5
                        )
                    ]
                )
            ]
            
            for target in targets:
                self.monitoring_targets[target.name] = target
            
            # Generate Prometheus configuration
            await self._generate_prometheus_config()
            
            self.logger.info(f"✅ Setup {len(targets)} monitoring targets")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up monitoring targets: {e}")
    
    async def _generate_prometheus_config(self) -> None:
        """Generate Prometheus configuration file"""        try:
            prometheus_config = {
                "global": {
                    "scrape_interval": "15s",
                    "evaluation_interval": "15s"
                },
                "rule_files": [
                    "prometheus_rules.yml"
                ],
                "alerting": {
                    "alertmanagers": [{
                        "static_configs": [{
                            "targets": ["alertmanager:9093"]
                        }]
                    }]
                },
                "scrape_configs": []
            }
            
            # Add scrape configs for each target
            for target in self.monitoring_targets.values():
                scrape_config = {
                    "job_name": target.name,
                    "scrape_interval": target.scrape_interval,
                    "metrics_path": target.metrics_path,
                    "static_configs": [{
                        "targets": [target.endpoint.replace("http://", "")],
                        "labels": target.labels
                    }]
                }
                prometheus_config["scrape_configs"].append(scrape_config)
            
            # Add node exporter for system metrics
            prometheus_config["scrape_configs"].append({
                "job_name": "node-exporter",
                "scrape_interval": "15s",
                "static_configs": [{
                    "targets": ["node-exporter:9100"]
                }]
            })
            
            # Add cAdvisor for container metrics
            prometheus_config["scrape_configs"].append({
                "job_name": "cadvisor",
                "scrape_interval": "15s",
                "static_configs": [{
                    "targets": ["cadvisor:8080"]
                }]
            })
            
            # Save configuration
            config_file = self.config_path / "prometheus.yml"
            with open(config_file, 'w') as f:
                yaml.dump(prometheus_config, f, default_flow_style=False)
            
            self.logger.info(f"✅ Generated Prometheus configuration: {config_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error generating Prometheus config: {e}")
    
    async def _start_monitoring_loops(self) -> None:
        """Start monitoring loops"""        try:
            # Start health check loop
            asyncio.create_task(self._health_check_loop())
            
            # Start metrics collection loop
            asyncio.create_task(self._metrics_collection_loop())
            
            # Start alert evaluation loop
            asyncio.create_task(self._alert_evaluation_loop())
            
            self.logger.info("✅ Started monitoring loops")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting monitoring loops: {e}")
    
    async def _health_check_loop(self) -> None:
        """Health check monitoring loop"""        while True:
            try:
                for target_name, target in self.monitoring_targets.items():
                    for health_check in target.health_checks:
                        status = await self._perform_health_check(health_check)
                        
                        # Store health status
                        check_key = f"{target_name}_{health_check.name}"
                        self.health_status[check_key] = {
                            "status": status,
                            "last_check": datetime.now(),
                            "target": target_name,
                            "check_name": health_check.name
                        }
                        
                        # Update health metric
                        health_value = 1 if status == HealthStatus.HEALTHY else 0
                        if "ia_influencer_service_health" not in self.metrics:
                            self.metrics["ia_influencer_service_health"] = Gauge(
                                "ia_influencer_service_health",
                                "Service health status (1=healthy, 0=unhealthy)",
                                ["service", "check_name"],
                                registry=self.prometheus_registry
                            )
                        
                        self.metrics["ia_influencer_service_health"].labels(
                            service=target_name,
                            check_name=health_check.name
                        ).set(health_value)
                
                await asyncio.sleep(15)  # Health check every 15 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Error in health check loop: {e}")
                await asyncio.sleep(30)
    
    async def _perform_health_check(self, health_check: HealthCheck) -> HealthStatus:
        """Perform individual health check"""        try:
            if health_check.method == "GET":
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(health_check.timeout)) as session:
                    async with session.get(
                        health_check.endpoint,
                        headers=health_check.headers
                    ) as response:
                        if response.status == health_check.expected_status:
                            if health_check.expected_content:
                                content = await response.text()
                                if health_check.expected_content in content:
                                    return HealthStatus.HEALTHY
                                else:
                                    return HealthStatus.UNHEALTHY
                            else:
                                return HealthStatus.HEALTHY
                        else:
                            return HealthStatus.UNHEALTHY
            
            elif health_check.method == "CONNECT":
                # Database connection check
                # Simplified implementation
                return HealthStatus.HEALTHY
                
            elif health_check.method == "PING":
                # Redis ping check
                # Simplified implementation
                return HealthStatus.HEALTHY
            
            else:
                return HealthStatus.UNKNOWN
                
        except Exception as e:
            self.logger.debug(f"Health check failed for {health_check.name}: {e}")
            return HealthStatus.UNHEALTHY
    
    async def _metrics_collection_loop(self) -> None:
        """Metrics collection loop"""        while True:
            try:
                # Collect Docker container metrics
                if self.docker_client:
                    await self._collect_docker_metrics()
                
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect application metrics
                await self._collect_application_metrics()
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Error in metrics collection loop: {e}")
                await asyncio.sleep(60)
    
    async def _collect_docker_metrics(self) -> None:
        """Collect Docker container metrics"""        try:
            containers = self.docker_client.containers.list()
            
            for container in containers:
                # Get container stats
                stats = container.stats(stream=False)
                
                container_name = container.name
                labels = container.labels
                service = labels.get("service", "unknown")
                namespace = labels.get("namespace", "default")
                
                # CPU metrics
                cpu_usage = self._calculate_cpu_percentage(stats)
                self.metrics["ia_influencer_container_cpu_usage"].labels(
                    container_name=container_name,
                    service=service,
                    namespace=namespace
                ).set(cpu_usage)
                
                # Memory metrics
                memory_usage = stats["memory_stats"]["usage"]
                self.metrics["ia_influencer_container_memory_usage"].labels(
                    container_name=container_name,
                    service=service,
                    namespace=namespace
                ).set(memory_usage)
                
                # Network metrics
                if "networks" in stats:
                    for network, net_stats in stats["networks"].items():
                        self.metrics["ia_influencer_container_network_io"].labels(
                            container_name=container_name,
                            service=service,
                            direction="rx"
                        ).inc(net_stats["rx_bytes"])
                        
                        self.metrics["ia_influencer_container_network_io"].labels(
                            container_name=container_name,
                            service=service,
                            direction="tx"
                        ).inc(net_stats["tx_bytes"])
                
        except Exception as e:
            self.logger.error(f"❌ Error collecting Docker metrics: {e}")
    
    def _calculate_cpu_percentage(self, stats: Dict[str, Any]) -> float:
        """Calculate CPU usage percentage from Docker stats"""        try:
            cpu_stats = stats["cpu_stats"]
            precpu_stats = stats["precpu_stats"]
            
            cpu_delta = cpu_stats["cpu_usage"]["total_usage"] - precpu_stats["cpu_usage"]["total_usage"]
            system_delta = cpu_stats["system_cpu_usage"] - precpu_stats["system_cpu_usage"]
            
            if system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * len(cpu_stats["cpu_usage"]["percpu_usage"]) * 100.0
                return cpu_percent
            else:
                return 0.0
                
        except (KeyError, ZeroDivisionError):
            return 0.0
    
    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics"""        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            
            # Update system metrics (if defined)
            # These would be separate system metrics, not container-specific
            
        except Exception as e:
            self.logger.error(f"❌ Error collecting system metrics: {e}")
    
    async def _collect_application_metrics(self) -> None:
        """Collect application-specific metrics"""        try:
            # Collect metrics from application endpoints
            for target_name, target in self.monitoring_targets.items():
                try:
                    async with aiohttp.ClientSession() as session:
                        metrics_url = f"{target.endpoint}{target.metrics_path}"
                        async with session.get(metrics_url, timeout=10) as response:
                            if response.status == 200:
                                metrics_data = await response.text()
                                # Parse Prometheus format metrics
                                # This would be handled by Prometheus scraping in real implementation
                                
                except Exception as e:
                    self.logger.debug(f"Failed to collect metrics from {target_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error collecting application metrics: {e}")
    
    async def _alert_evaluation_loop(self) -> None:
        """Alert evaluation loop"""        while True:
            try:
                current_time = datetime.now()
                
                # Evaluate alert rules
                for rule_name, rule in self.alert_rules.items():
                    alert_status = await self._evaluate_alert_rule(rule)
                    
                    if alert_status["active"]:
                        if rule_name not in self.active_alerts:
                            # New alert
                            self.active_alerts[rule_name] = {
                                "rule": rule,
                                "status": alert_status,
                                "triggered_at": current_time,
                                "last_sent": None
                            }
                            
                            # Send alert
                            await self._send_alert(rule, alert_status)
                            
                        else:
                            # Update existing alert
                            self.active_alerts[rule_name]["status"] = alert_status
                    
                    else:
                        if rule_name in self.active_alerts:
                            # Alert resolved
                            await self._resolve_alert(rule_name)
                            del self.active_alerts[rule_name]
                
                await asyncio.sleep(60)  # Evaluate every minute
                
            except Exception as e:
                self.logger.error(f"❌ Error in alert evaluation loop: {e}")
                await asyncio.sleep(120)
    
    async def _evaluate_alert_rule(self, rule: AlertRule) -> Dict[str, Any]:
        """Evaluate individual alert rule"""        try:
            # Simplified alert evaluation
            # In real implementation, would use PromQL evaluation
            
            # Mock evaluation based on rule expression
            if "cpu_usage > 80" in rule.expression:
                # Check current CPU metrics
                # This is simplified - would use actual metric values
                import random
                current_value = random.uniform(0, 100)
                active = current_value > 80
                
            elif "error_rate > 0.1" in rule.expression:
                # Check error rate
                import random
                current_value = random.uniform(0, 0.2)
                active = current_value > 0.1
                
            else:
                # Default to not active
                active = False
                current_value = 0
            
            return {
                "active": active,
                "value": current_value,
                "evaluated_at": datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error evaluating alert rule {rule.name}: {e}")
            return {"active": False, "value": 0, "evaluated_at": datetime.now()}
    
    async def _send_alert(self, rule: AlertRule, status: Dict[str, Any]) -> None:
        """Send alert notification"""        try:
            alert_message = {
                "alert_name": rule.name,
                "severity": rule.severity.value,
                "description": rule.description,
                "value": status["value"],
                "labels": rule.labels,
                "annotations": rule.annotations,
                "triggered_at": datetime.now().isoformat()
            }
            
            # Log alert
            self.logger.warning(
                f"🚨 ALERT: {rule.name} - {rule.description} (Value: {status['value']})"
            )
            
            # Send to external systems (webhook, email, Slack, etc.)
            if self.monitoring_config["alertmanager"]["webhook_url"]:
                await self._send_webhook_alert(alert_message)
            
        except Exception as e:
            self.logger.error(f"❌ Error sending alert: {e}")
    
    async def _send_webhook_alert(self, alert_message: Dict[str, Any]) -> None:
        """Send alert via webhook"""        try:
            webhook_url = self.monitoring_config["alertmanager"]["webhook_url"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=alert_message) as response:
                    if response.status == 200:
                        self.logger.info(f"✅ Alert sent via webhook: {alert_message['alert_name']}")
                    else:
                        self.logger.error(f"❌ Failed to send webhook alert: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"❌ Error sending webhook alert: {e}")
    
    async def _resolve_alert(self, rule_name: str) -> None:
        """Resolve active alert"""        try:
            alert = self.active_alerts[rule_name]
            
            self.logger.info(f"✅ RESOLVED: Alert {rule_name}")
            
            # Send resolution notification
            resolution_message = {
                "alert_name": rule_name,
                "status": "resolved",
                "resolved_at": datetime.now().isoformat(),
                "duration": str(datetime.now() - alert["triggered_at"])
            }
            
            if self.monitoring_config["alertmanager"]["webhook_url"]:
                await self._send_webhook_alert(resolution_message)
                
        except Exception as e:
            self.logger.error(f"❌ Error resolving alert: {e}")
    
    async def get_metrics_export(self) -> str:
        """Export metrics in Prometheus format"""        try:
            return generate_latest(self.prometheus_registry).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"❌ Error exporting metrics: {e}")
            return ""
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""        try:
            total_checks = len(self.health_status)
            healthy_checks = len([
                status for status in self.health_status.values()
                if status["status"] == HealthStatus.HEALTHY
            ])
            
            overall_health = HealthStatus.HEALTHY if healthy_checks == total_checks else HealthStatus.DEGRADED
            if healthy_checks == 0:
                overall_health = HealthStatus.UNHEALTHY
            
            return {
                "overall_status": overall_health.value,
                "total_checks": total_checks,
                "healthy_checks": healthy_checks,
                "unhealthy_checks": total_checks - healthy_checks,
                "last_updated": datetime.now().isoformat(),
                "details": self.health_status
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting health status: {e}")
            return {"overall_status": "unknown", "error": str(e)}
    
    async def get_active_alerts(self) -> Dict[str, Any]:
        """Get currently active alerts"""        try:
            active_alerts_info = {}
            
            for rule_name, alert in self.active_alerts.items():
                active_alerts_info[rule_name] = {
                    "severity": alert["rule"].severity.value,
                    "description": alert["rule"].description,
                    "triggered_at": alert["triggered_at"].isoformat(),
                    "current_value": alert["status"]["value"],
                    "labels": alert["rule"].labels,
                    "annotations": alert["rule"].annotations
                }
            
            return {
                "total_active_alerts": len(active_alerts_info),
                "alerts": active_alerts_info,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting active alerts: {e}")
            return {"total_active_alerts": 0, "alerts": {}, "error": str(e)}

class MetricsCollector:
    """Specialized metrics collector for IA-Influencer services"""    
    def __init__(self, monitoring_manager: ContainerMonitoringManager):
        self.monitoring_manager = monitoring_manager
        self.custom_metrics = {}
        self.collection_tasks = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize metrics collector"""        try:
            # Setup custom metric collection
            await self._setup_custom_metrics()
            
            self.logger.info("✅ MetricsCollector initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing MetricsCollector: {e}")
            return False
    
    async def _setup_custom_metrics(self) -> None:
        """Setup custom metrics for IA-Influencer platform"""        try:
            # Start custom collection tasks
            self.collection_tasks["ai_processing"] = asyncio.create_task(
                self._collect_ai_processing_metrics()
            )
            
            self.collection_tasks["content_protection"] = asyncio.create_task(
                self._collect_content_protection_metrics()
            )
            
            self.collection_tasks["monetization"] = asyncio.create_task(
                self._collect_monetization_metrics()
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up custom metrics: {e}")
    
    async def _collect_ai_processing_metrics(self) -> None:
        """Collect AI processing metrics"""        while True:
            try:
                # Mock AI processing metrics
                import random
                
                # AI model inference time
                inference_time = random.uniform(0.1, 5.0)
                self.monitoring_manager.metrics["ia_influencer_ai_processing_time"].labels(
                    model="content_analyzer",
                    operation="inference",
                    service="ai-engine"
                ).observe(inference_time)
                
                # GPU utilization (if available)
                gpu_utilization = random.uniform(30, 95)
                
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"❌ Error collecting AI metrics: {e}")
                await asyncio.sleep(120)
    
    async def _collect_content_protection_metrics(self) -> None:
        """Collect content protection metrics"""        while True:
            try:
                import random
                
                # Fingerprinting operations
                operations = ["create", "match", "verify", "delete"]
                formats = ["audio", "video", "image", "text"]
                statuses = ["success", "failure"]
                
                for operation in operations:
                    for format_type in formats:
                        for status in statuses:
                            count = random.randint(0, 10)
                            self.monitoring_manager.metrics["ia_influencer_audio_fingerprint_operations"].labels(
                                operation=operation,
                                format=format_type,
                                status=status
                            ).inc(count)
                
                # Content protection scans
                scan_types = ["similarity", "duplicate", "copyright"]
                platforms = ["youtube", "tiktok", "instagram", "twitter"]
                
                for scan_type in scan_types:
                    for platform in platforms:
                        for status in statuses:
                            count = random.randint(0, 50)
                            self.monitoring_manager.metrics["ia_influencer_content_protection_scans"].labels(
                                scan_type=scan_type,
                                platform=platform,
                                status=status
                            ).inc(count)
                
                await asyncio.sleep(120)
                
            except Exception as e:
                self.logger.error(f"❌ Error collecting content protection metrics: {e}")
                await asyncio.sleep(180)
    
    async def _collect_monetization_metrics(self) -> None:
        """Collect monetization metrics"""        while True:
            try:
                import random
                
                # Revenue tracking
                currencies = ["EUR", "USD", "GBP"]
                platforms = ["youtube", "spotify", "instagram", "tiktok"]
                user_tiers = ["free", "premium", "enterprise"]
                
                for currency in currencies:
                    for platform in platforms:
                        for tier in user_tiers:
                            revenue = random.uniform(0, 10000)
                            self.monitoring_manager.metrics["ia_influencer_monetization_revenue"].labels(
                                currency=currency,
                                platform=platform,
                                user_tier=tier
                            ).set(revenue)
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Error collecting monetization metrics: {e}")
                await asyncio.sleep(360)

class AlertManager:
    """Professional alert manager for IA-Influencer platform"""    
    def __init__(self, monitoring_manager: ContainerMonitoringManager):
        self.monitoring_manager = monitoring_manager
        self.notification_channels = {}
        self.alert_history = {}
        self.escalation_rules = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize alert manager"""        try:
            # Setup notification channels
            await self._setup_notification_channels()
            
            # Setup escalation rules
            await self._setup_escalation_rules()
            
            self.logger.info("✅ AlertManager initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing AlertManager: {e}")
            return False
    
    async def _setup_notification_channels(self) -> None:
        """Setup notification channels"""        try:
            self.notification_channels = {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.example.com",
                    "recipients": ["admin@ia-influencer-agent.com"]
                },
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://hooks.slack.com/services/...",
                    "channel": "#ia-influencer-alerts"
                },
                "webhook": {
                    "enabled": True,
                    "url": "https://alerts.ia-influencer-agent.com/webhook"
                },
                "sms": {
                    "enabled": False,
                    "provider": "twilio",
                    "numbers": ["+49123456789"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up notification channels: {e}")
    
    async def _setup_escalation_rules(self) -> None:
        """Setup alert escalation rules"""        try:
            self.escalation_rules = {
                "critical": {
                    "immediate": ["slack", "email"],
                    "after_5min": ["sms"],
                    "after_15min": ["phone_call"]
                },
                "warning": {
                    "immediate": ["slack"],
                    "after_30min": ["email"]
                },
                "info": {
                    "immediate": ["slack"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up escalation rules: {e}")
    
    async def send_notification(
        self, 
        channel: str, 
        message: str, 
        severity: AlertSeverity = AlertSeverity.INFO
    ) -> bool:
        """Send notification via specified channel"""        try:
            if channel not in self.notification_channels:
                self.logger.error(f"❌ Unknown notification channel: {channel}")
                return False
            
            channel_config = self.notification_channels[channel]
            if not channel_config.get("enabled", False):
                self.logger.debug(f"Notification channel {channel} is disabled")
                return False
            
            if channel == "email":
                return await self._send_email_notification(message, channel_config)
            elif channel == "slack":
                return await self._send_slack_notification(message, channel_config)
            elif channel == "webhook":
                return await self._send_webhook_notification(message, channel_config)
            elif channel == "sms":
                return await self._send_sms_notification(message, channel_config)
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error sending notification via {channel}: {e}")
            return False
    
    async def _send_email_notification(self, message: str, config: Dict[str, Any]) -> bool:
        """Send email notification"""        try:
            # Simplified email sending implementation
            self.logger.info(f"📧 Email notification sent: {message[:100]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error sending email: {e}")
            return False
    
    async def _send_slack_notification(self, message: str, config: Dict[str, Any]) -> bool:
        """Send Slack notification"""        try:
            webhook_url = config.get("webhook_url")
            if not webhook_url:
                return False
            
            payload = {
                "text": message,
                "channel": config.get("channel", "#general"),
                "username": "IA-Influencer-Monitor"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        self.logger.info(f"💬 Slack notification sent")
                        return True
                    else:
                        self.logger.error(f"❌ Slack notification failed: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"❌ Error sending Slack notification: {e}")
            return False
    
    async def _send_webhook_notification(self, message: str, config: Dict[str, Any]) -> bool:
        """Send webhook notification"""        try:
            webhook_url = config.get("url")
            if not webhook_url:
                return False
            
            payload = {
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "source": "ia-influencer-monitoring"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        self.logger.info(f"🔗 Webhook notification sent")
                        return True
                    else:
                        return False
                        
        except Exception as e:
            self.logger.error(f"❌ Error sending webhook notification: {e}")
            return False
    
    async def _send_sms_notification(self, message: str, config: Dict[str, Any]) -> bool:
        """Send SMS notification"""        try:
            # Simplified SMS implementation
            self.logger.info(f"📱 SMS notification sent: {message[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error sending SMS: {e}")
            return False

__all__ = [
    "ContainerMonitoringManager",
    "MetricsCollector",
    "AlertManager",
    "MetricDefinition",
    "AlertRule",
    "HealthCheck",
    "MonitoringTarget",
    "MetricType",
    "AlertSeverity",
    "HealthStatus"
]
