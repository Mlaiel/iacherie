"""Advanced Monitoring and Observability System
==========================================

Prometheus, Grafana, and ELK stack integration for production monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import time
import json
import logging
import psutil
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server, CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

try:
    import elasticsearch
    HAS_ELASTICSEARCH = True
except ImportError:
    HAS_ELASTICSEARCH = False

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class MetricConfig:
    """Metric configuration"""
    name: str
    metric_type: MetricType
    description: str
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None  # For histograms


@dataclass
class Alert:
    """Alert definition"""
    alert_id: str
    name: str
    level: AlertLevel
    condition: str
    message: str
    threshold: float
    metric_name: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PrometheusMetricsCollector:
    """Prometheus metrics collector"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.registry = CollectorRegistry()
        self.metrics = {}
        self.logger = logging.getLogger(__name__)
        
        if not HAS_PROMETHEUS:
            self.logger.warning("Prometheus client not available - metrics collection disabled")
            return
        
        self._initialize_default_metrics()
        
    def _initialize_default_metrics(self):
        """Initialize default application metrics"""
        if not HAS_PROMETHEUS:
            return
            
        default_metrics = [
            MetricConfig(
                name="http_requests_total",
                metric_type=MetricType.COUNTER,
                description="Total HTTP requests",
                labels=["method", "endpoint", "status_code"]
            ),
            MetricConfig(
                name="http_request_duration_seconds",
                metric_type=MetricType.HISTOGRAM,
                description="HTTP request duration in seconds",
                labels=["method", "endpoint"],
                buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
            ),
            MetricConfig(
                name="active_connections",
                metric_type=MetricType.GAUGE,
                description="Number of active connections"
            ),
            MetricConfig(
                name="database_connections_active",
                metric_type=MetricType.GAUGE,
                description="Active database connections"
            ),
            MetricConfig(
                name="memory_usage_bytes",
                metric_type=MetricType.GAUGE,
                description="Memory usage in bytes"
            ),
            MetricConfig(
                name="cpu_usage_percent",
                metric_type=MetricType.GAUGE,
                description="CPU usage percentage"
            ),
            MetricConfig(
                name="ai_inference_duration_seconds",
                metric_type=MetricType.HISTOGRAM,
                description="AI inference duration in seconds",
                labels=["model_name", "inference_type"],
                buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
            ),
            MetricConfig(
                name="content_processing_total",
                metric_type=MetricType.COUNTER,
                description="Total content items processed",
                labels=["content_type", "processing_result"]
            )
        ]
        
        for metric_config in default_metrics:
            self.register_metric(metric_config)
    
    def register_metric(self, config: MetricConfig):
        """Register a new metric"""
        if not HAS_PROMETHEUS:
            return
            
        try:
            metric_args = {
                'name': config.name,
                'documentation': config.description,
                'registry': self.registry
            }
            
            if config.labels:
                metric_args['labelnames'] = config.labels
            
            if config.metric_type == MetricType.COUNTER:
                metric = Counter(**metric_args)
            elif config.metric_type == MetricType.GAUGE:
                metric = Gauge(**metric_args)
            elif config.metric_type == MetricType.HISTOGRAM:
                if config.buckets:
                    metric_args['buckets'] = config.buckets
                metric = Histogram(**metric_args)
            elif config.metric_type == MetricType.SUMMARY:
                metric = Summary(**metric_args)
            else:
                raise ValueError(f"Unsupported metric type: {config.metric_type}")
            
            self.metrics[config.name] = metric
            self.logger.info(f"Registered metric: {config.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to register metric {config.name}: {str(e)}")
    
    def increment_counter(self, name: str, labels: Dict[str, str] = None, value: float = 1):
        """Increment a counter metric"""
        if not HAS_PROMETHEUS or name not in self.metrics:
            return
            
        try:
            metric = self.metrics[name]
            if labels:
                metric.labels(**labels).inc(value)
            else:
                metric.inc(value)
        except Exception as e:
            self.logger.error(f"Failed to increment counter {name}: {str(e)}")
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        if not HAS_PROMETHEUS or name not in self.metrics:
            return
            
        try:
            metric = self.metrics[name]
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)
        except Exception as e:
            self.logger.error(f"Failed to set gauge {name}: {str(e)}")
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observe a histogram metric"""
        if not HAS_PROMETHEUS or name not in self.metrics:
            return
            
        try:
            metric = self.metrics[name]
            if labels:
                metric.labels(**labels).observe(value)
            else:
                metric.observe(value)
        except Exception as e:
            self.logger.error(f"Failed to observe histogram {name}: {str(e)}")
    
    def get_metrics_data(self) -> str:
        """Get Prometheus formatted metrics data"""
        if not HAS_PROMETHEUS:
            return ""
            
        return generate_latest(self.registry).decode('utf-8')


class SystemMetricsCollector:
    """System-level metrics collector"""
    
    def __init__(self, prometheus_collector: PrometheusMetricsCollector):
        self.prometheus = prometheus_collector
        self.logger = logging.getLogger(__name__)
        self.collection_interval = 5  # seconds
        self._stop_event = threading.Event()
        self._collector_thread = None
        
    def start_collection(self):
        """Start system metrics collection"""
        if self._collector_thread and self._collector_thread.is_alive():
            return
            
        self._stop_event.clear()
        self._collector_thread = threading.Thread(target=self._collect_metrics_loop)
        self._collector_thread.daemon = True
        self._collector_thread.start()
        self.logger.info("System metrics collection started")
    
    def stop_collection(self):
        """Stop system metrics collection"""
        self._stop_event.set()
        if self._collector_thread:
            self._collector_thread.join(timeout=5)
        self.logger.info("System metrics collection stopped")
    
    def _collect_metrics_loop(self):
        """Main metrics collection loop"""
        while not self._stop_event.wait(self.collection_interval):
            try:
                self._collect_system_metrics()
            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {str(e)}")
    
    def _collect_system_metrics(self):
        """Collect system metrics"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self.prometheus.set_gauge("memory_usage_bytes", memory.used)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            self.prometheus.set_gauge("cpu_usage_percent", cpu_percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.prometheus.set_gauge("disk_usage_bytes", disk.used)
            self.prometheus.set_gauge("disk_free_bytes", disk.free)
            
            # Network I/O
            network = psutil.net_io_counters()
            self.prometheus.set_gauge("network_bytes_sent", network.bytes_sent)
            self.prometheus.set_gauge("network_bytes_recv", network.bytes_recv)
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {str(e)}")


class ELKStackIntegration:
    """Elasticsearch, Logstash, Kibana integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.elasticsearch_client = None
        self.logger = logging.getLogger(__name__)
        
        if HAS_ELASTICSEARCH:
            self._initialize_elasticsearch()
        else:
            self.logger.warning("Elasticsearch client not available - log shipping disabled")
    
    def _initialize_elasticsearch(self):
        """Initialize Elasticsearch client"""
        try:
            es_config = self.config.get('elasticsearch', {})
            hosts = es_config.get('hosts', ['localhost:9200'])
            username = es_config.get('username')
            password = es_config.get('password')
            
            client_config = {'hosts': hosts}
            if username and password:
                client_config['http_auth'] = (username, password)
            
            self.elasticsearch_client = elasticsearch.Elasticsearch(**client_config)
            
            # Test connection
            if self.elasticsearch_client.ping():
                self.logger.info("Elasticsearch connection established")
            else:
                self.logger.warning("Elasticsearch connection failed")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Elasticsearch: {str(e)}")
    
    async def ship_log(self, log_data: Dict[str, Any], index: str = None):
        """Ship log to Elasticsearch"""
        if not self.elasticsearch_client:
            return
            
        try:
            index = index or f"ainflue-logs-{datetime.utcnow().strftime('%Y.%m.%d')}"
            
            log_document = {
                '@timestamp': datetime.utcnow().isoformat(),
                'application': 'ainflue',
                'environment': os.getenv('ENVIRONMENT', 'development'),
                **log_data
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self.elasticsearch_client.index,
                index,
                log_document
            )
            
        except Exception as e:
            self.logger.error(f"Failed to ship log to Elasticsearch: {str(e)}")
    
    async def search_logs(self, query: Dict[str, Any], index: str = None) -> Dict[str, Any]:
        """Search logs in Elasticsearch"""
        if not self.elasticsearch_client:
            return {'hits': {'hits': []}}
            
        try:
            index = index or "ainflue-logs-*"
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.elasticsearch_client.search,
                index,
                query
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to search logs: {str(e)}")
            return {'hits': {'hits': []}}


class AlertManager:
    """Alert management system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        
    def register_alert_handler(self, handler: Callable):
        """Register an alert handler"""
        self.alert_handlers.append(handler)
        
    async def create_alert(self, alert: Alert):
        """Create a new alert"""
        try:
            self.active_alerts[alert.alert_id] = alert
            
            # Notify all handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    self.logger.error(f"Alert handler failed: {str(e)}")
            
            self.logger.warning(f"Alert created: {alert.name} [{alert.level.value}]")
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {str(e)}")
    
    async def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved_at = datetime.utcnow()
            
            # Notify handlers of resolution
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    self.logger.error(f"Alert resolution handler failed: {str(e)}")
            
            del self.active_alerts[alert_id]
            self.logger.info(f"Alert resolved: {alert.name}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())


class MonitoringSystem:
    """Comprehensive monitoring system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.prometheus = PrometheusMetricsCollector(config.get('prometheus', {}))
        self.system_metrics = SystemMetricsCollector(self.prometheus)
        self.elk = ELKStackIntegration(config.get('elk', {}))
        self.alerts = AlertManager(config.get('alerts', {}))
        self.logger = logging.getLogger(__name__)
        
        # Register default alert handlers
        self.alerts.register_alert_handler(self._log_alert_handler)
        self.alerts.register_alert_handler(self._elk_alert_handler)
        
    async def start(self):
        """Start monitoring system"""
        try:
            # Start Prometheus metrics server
            if HAS_PROMETHEUS and self.config.get('prometheus', {}).get('enabled', True):
                port = self.config.get('prometheus', {}).get('port', 9090)
                start_http_server(port, registry=self.prometheus.registry)
                self.logger.info(f"Prometheus metrics server started on port {port}")
            
            # Start system metrics collection
            self.system_metrics.start_collection()
            
            self.logger.info("Monitoring system started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring system: {str(e)}")
            raise
    
    async def stop(self):
        """Stop monitoring system"""
        self.system_metrics.stop_collection()
        self.logger.info("Monitoring system stopped")
    
    async def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        self.prometheus.increment_counter(
            "http_requests_total",
            {"method": method, "endpoint": endpoint, "status_code": str(status_code)}
        )
        
        self.prometheus.observe_histogram(
            "http_request_duration_seconds",
            duration,
            {"method": method, "endpoint": endpoint}
        )
    
    async def record_ai_inference(self, model_name: str, inference_type: str, duration: float):
        """Record AI inference metrics"""
        self.prometheus.observe_histogram(
            "ai_inference_duration_seconds",
            duration,
            {"model_name": model_name, "inference_type": inference_type}
        )
    
    async def record_content_processing(self, content_type: str, result: str):
        """Record content processing metrics"""
        self.prometheus.increment_counter(
            "content_processing_total",
            {"content_type": content_type, "processing_result": result}
        )
    
    async def check_alerts(self):
        """Check for alert conditions"""
        try:
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                await self.alerts.create_alert(Alert(
                    alert_id=f"memory_high_{int(time.time())}",
                    name="High Memory Usage",
                    level=AlertLevel.CRITICAL,
                    condition="memory_usage > 90%",
                    message=f"Memory usage is {memory.percent:.1f}%",
                    threshold=90.0,
                    metric_name="memory_usage_percent",
                    created_at=datetime.utcnow()
                ))
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent()
            if cpu_percent > 85:
                await self.alerts.create_alert(Alert(
                    alert_id=f"cpu_high_{int(time.time())}",
                    name="High CPU Usage",
                    level=AlertLevel.WARNING,
                    condition="cpu_usage > 85%",
                    message=f"CPU usage is {cpu_percent:.1f}%",
                    threshold=85.0,
                    metric_name="cpu_usage_percent",
                    created_at=datetime.utcnow()
                ))
            
        except Exception as e:
            self.logger.error(f"Error checking alerts: {str(e)}")
    
    async def _log_alert_handler(self, alert: Alert):
        """Log alert handler"""
        level_map = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.CRITICAL: logging.CRITICAL,
            AlertLevel.EMERGENCY: logging.CRITICAL
        }
        
        log_level = level_map.get(alert.level, logging.WARNING)
        self.logger.log(log_level, f"ALERT: {alert.name} - {alert.message}")
    
    async def _elk_alert_handler(self, alert: Alert):
        """ELK stack alert handler"""
        alert_log = {
            'alert_id': alert.alert_id,
            'alert_name': alert.name,
            'level': alert.level.value,
            'condition': alert.condition,
            'message': alert.message,
            'threshold': alert.threshold,
            'metric_name': alert.metric_name,
            'created_at': alert.created_at.isoformat(),
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
            'metadata': alert.metadata
        }
        
        await self.elk.ship_log(alert_log, "ainflue-alerts")


# Global monitoring instance
monitoring_system = None


async def initialize_monitoring(config: Dict[str, Any] = None) -> MonitoringSystem:
    """Initialize global monitoring system"""
    global monitoring_system
    
    if monitoring_system is None:
        monitoring_system = MonitoringSystem(config)
        await monitoring_system.start()
    
    return monitoring_system


def get_monitoring_system() -> Optional[MonitoringSystem]:
    """Get global monitoring system instance"""
    return monitoring_system


# Convenience functions
async def record_request_metric(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metric"""
    if monitoring_system:
        await monitoring_system.record_request(method, endpoint, status_code, duration)


async def record_ai_metric(model_name: str, inference_type: str, duration: float):
    """Record AI inference metric"""
    if monitoring_system:
        await monitoring_system.record_ai_inference(model_name, inference_type, duration)


async def ship_log(log_data: Dict[str, Any], index: str = None):
    """Ship log to ELK stack"""
    if monitoring_system:
        await monitoring_system.elk.ship_log(log_data, index)