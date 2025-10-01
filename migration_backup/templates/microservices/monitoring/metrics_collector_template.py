"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Metrics Collector Template for IA Chéries Platform
==============================================

Production-ready metrics collection with:
- Prometheus metrics integration
- Custom business metrics
- System performance metrics
- Application health metrics
- Multi-dimensional labels
- Metrics aggregation and processing

Author: Fahed Mlaiel (mlaiel@live.de)
Metrics & Monitoring Expert
"""

import asyncio
import json
import logging
import time
import psutil
import gc
from typing import Dict, Any, Optional, List, Set, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading

from prometheus_client import Counter, Histogram, Gauge, Summary, Info, Enum as PrometheusEnum
from prometheus_client import CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import REGISTRY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"  
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    INFO = "info"
    ENUM = "enum"

@dataclass
class MetricDefinition:
    """Metric definition"""
    name: str
    description: str
    metric_type: MetricType
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None
    quantiles: Optional[List[float]] = None
    enum_states: Optional[List[str]] = None

@dataclass
class MetricEvent:
    """Metric event for recording"""
    metric_name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class MetricsCollector:
    """
    Production-ready metrics collection system for IA Chéries Platform
    
    Features:
    - Prometheus metrics integration
    - Custom business and system metrics
    - Automatic metric registration
    - Multi-dimensional labeling
    - Performance monitoring
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None, 
                 service_name: str = "ainflue-service", service_version: str = "1.0.0"):
        self.registry = registry or REGISTRY
        self.service_name = service_name
        self.service_version = service_version
        
        # Metric instances
        self.metrics: Dict[str, Any] = {}
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        
        # System metrics collection
        self.system_metrics_enabled = True
        self.system_metrics_interval = 10  # seconds
        self.system_metrics_task = None
        
        # Business metrics buffer
        self.metric_events: List[MetricEvent] = []
        self.events_lock = threading.Lock()
        
        # Initialize default metrics
        self._initialize_default_metrics()
        
        # Start system metrics collection
        if self.system_metrics_enabled:
            asyncio.create_task(self._start_system_metrics_collection())
    
    def _initialize_default_metrics(self):
        """Initialize default service metrics"""
        
        # Service info
        self.service_info = Info(
            'service_info',
            'Service information',
            registry=self.registry
        )
        self.service_info.info({
            'service_name': self.service_name,
            'version': self.service_version,
            'started_at': datetime.utcnow().isoformat()
        })
        
        # Request metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            buckets=[0.1, 0.25, 0.5, 1, 2.5, 5, 10],
            registry=self.registry
        )
        
        # System metrics
        self.cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'system_memory_usage_bytes',
            'Memory usage in bytes',
            ['type'],
            registry=self.registry
        )
        
        self.disk_usage = Gauge(
            'system_disk_usage_bytes',
            'Disk usage in bytes',
            ['device', 'type'],
            registry=self.registry
        )
        
        # Application metrics
        self.active_connections = Gauge(
            'app_active_connections',
            'Active connections',
            registry=self.registry
        )
        
        self.business_operations = Counter(
            'business_operations_total',
            'Total business operations',
            ['operation_type', 'status'],
            registry=self.registry
        )
        
        self.business_operation_duration = Histogram(
            'business_operation_duration_seconds',
            'Business operation duration',
            ['operation_type'],
            registry=self.registry
        )
        
        # Error metrics
        self.error_count = Counter(
            'app_errors_total',
            'Total application errors',
            ['error_type', 'component'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_operations = Counter(
            'cache_operations_total',
            'Cache operations',
            ['operation', 'result'],
            registry=self.registry
        )
        
        # Queue metrics
        self.queue_size = Gauge(
            'queue_size',
            'Queue size',
            ['queue_name'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_connections = Gauge(
            'db_connections_active',
            'Active database connections',
            ['database'],
            registry=self.registry
        )
        
        self.db_operations = Counter(
            'db_operations_total',
            'Database operations',
            ['operation', 'table', 'status'],
            registry=self.registry
        )
        
        self.db_operation_duration = Histogram(
            'db_operation_duration_seconds',
            'Database operation duration',
            ['operation', 'table'],
            registry=self.registry
        )
    
    def register_metric(self, definition: MetricDefinition) -> Any:
        """Register a new metric"""
        if definition.name in self.metrics:
            logger.warning(f"Metric {definition.name} already registered")
            return self.metrics[definition.name]
        
        # Create metric based on type
        if definition.metric_type == MetricType.COUNTER:
            metric = Counter(
                definition.name,
                definition.description,
                definition.labels,
                registry=self.registry
            )
        elif definition.metric_type == MetricType.GAUGE:
            metric = Gauge(
                definition.name,
                definition.description,
                definition.labels,
                registry=self.registry
            )
        elif definition.metric_type == MetricType.HISTOGRAM:
            metric = Histogram(
                definition.name,
                definition.description,
                definition.labels,
                buckets=definition.buckets,
                registry=self.registry
            )
        elif definition.metric_type == MetricType.SUMMARY:
            metric = Summary(
                definition.name,
                definition.description,
                definition.labels,
                registry=self.registry
            )
        elif definition.metric_type == MetricType.INFO:
            metric = Info(
                definition.name,
                definition.description,
                registry=self.registry
            )
        elif definition.metric_type == MetricType.ENUM:
            metric = PrometheusEnum(
                definition.name,
                definition.description,
                definition.labels,
                states=definition.enum_states or [],
                registry=self.registry
            )
        else:
            raise ValueError(f"Unsupported metric type: {definition.metric_type}")
        
        self.metrics[definition.name] = metric
        self.metric_definitions[definition.name] = definition
        
        logger.info(f"Registered metric: {definition.name} ({definition.metric_type})")
        return metric
    
    def record_event(self, event: MetricEvent):
        """Record a metric event"""
        with self.events_lock:
            self.metric_events.append(event)
        
        # Process immediately for real-time metrics
        self._process_event(event)
    
    def _process_event(self, event: MetricEvent):
        """Process a single metric event"""
        if event.metric_name not in self.metrics:
            logger.warning(f"Unknown metric: {event.metric_name}")
            return
        
        metric = self.metrics[event.metric_name]
        definition = self.metric_definitions[event.metric_name]
        
        try:
            if definition.metric_type == MetricType.COUNTER:
                if event.labels:
                    metric.labels(**event.labels).inc(event.value)
                else:
                    metric.inc(event.value)
            
            elif definition.metric_type == MetricType.GAUGE:
                if event.labels:
                    metric.labels(**event.labels).set(event.value)
                else:
                    metric.set(event.value)
            
            elif definition.metric_type == MetricType.HISTOGRAM:
                if event.labels:
                    metric.labels(**event.labels).observe(event.value)
                else:
                    metric.observe(event.value)
            
            elif definition.metric_type == MetricType.SUMMARY:
                if event.labels:
                    metric.labels(**event.labels).observe(event.value)
                else:
                    metric.observe(event.value)
                    
        except Exception as e:
            logger.error(f"Failed to process metric event {event.metric_name}: {e}")
    
    def increment_counter(self, name: str, value: float = 1, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        event = MetricEvent(
            metric_name=name,
            value=value,
            labels=labels or {}
        )
        self.record_event(event)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        event = MetricEvent(
            metric_name=name,
            value=value,
            labels=labels or {}
        )
        self.record_event(event)
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observe a histogram metric"""
        event = MetricEvent(
            metric_name=name,
            value=value,
            labels=labels or {}
        )
        self.record_event(event)
    
    def time_operation(self, name: str, labels: Dict[str, str] = None):
        """Context manager for timing operations"""
        return self._TimingContext(self, name, labels or {})
    
    class _TimingContext:
        def __init__(self, collector, metric_name: str, labels: Dict[str, str]):
            self.collector = collector
            self.metric_name = metric_name
            self.labels = labels
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time:
                duration = time.time() - self.start_time
                self.collector.observe_histogram(self.metric_name, duration, self.labels)
    
    async def _start_system_metrics_collection(self):
        """Start background system metrics collection"""
        self.system_metrics_task = asyncio.create_task(self._collect_system_metrics_loop())
    
    async def _collect_system_metrics_loop(self):
        """System metrics collection loop"""
        while True:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.system_metrics_interval)
            except Exception as e:
                logger.error(f"System metrics collection error: {e}")
                await asyncio.sleep(self.system_metrics_interval)
    
    async def _collect_system_metrics(self):
        """Collect system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage.labels(type="used").set(memory.used)
            self.memory_usage.labels(type="available").set(memory.available)
            self.memory_usage.labels(type="total").set(memory.total)
            
            # Disk usage
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    device = partition.device
                    self.disk_usage.labels(device=device, type="used").set(usage.used)
                    self.disk_usage.labels(device=device, type="free").set(usage.free)
                    self.disk_usage.labels(device=device, type="total").set(usage.total)
                except:
                    continue
            
            # Python-specific metrics
            gc_counts = gc.get_count()
            for i, count in enumerate(gc_counts):
                self.set_gauge(f"python_gc_objects_collected_total", count, {"generation": str(i)})
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        self.request_count.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_business_operation(self, operation_type: str, duration: float, status: str = "success"):
        """Record business operation metrics"""
        self.business_operations.labels(operation_type=operation_type, status=status).inc()
        self.business_operation_duration.labels(operation_type=operation_type).observe(duration)
    
    def record_error(self, error_type: str, component: str):
        """Record application error"""
        self.error_count.labels(error_type=error_type, component=component).inc()
    
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation"""
        self.cache_operations.labels(operation=operation, result=result).inc()
    
    def update_queue_size(self, queue_name: str, size: int):
        """Update queue size metric"""
        self.queue_size.labels(queue_name=queue_name).set(size)
    
    def record_db_operation(self, operation: str, table: str, duration: float, status: str = "success"):
        """Record database operation"""
        self.db_operations.labels(operation=operation, table=table, status=status).inc()
        self.db_operation_duration.labels(operation=operation, table=table).observe(duration)
    
    def update_db_connections(self, database: str, count: int):
        """Update database connections metric"""
        self.db_connections.labels(database=database).set(count)
    
    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus text format"""
        return generate_latest(self.registry).decode('utf-8')
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        summary = {
            "service_name": self.service_name,
            "service_version": self.service_version,
            "metrics_count": len(self.metrics),
            "events_processed": len(self.metric_events),
            "collection_time": datetime.utcnow().isoformat()
        }
        
        # Add metric definitions
        summary["metric_definitions"] = {
            name: {
                "type": definition.metric_type.value,
                "description": definition.description,
                "labels": definition.labels
            }
            for name, definition in self.metric_definitions.items()
        }
        
        return summary
    
    def cleanup(self):
        """Cleanup resources"""
        if self.system_metrics_task:
            self.system_metrics_task.cancel()
        
        with self.events_lock:
            self.metric_events.clear()

class MetricsCollectorTemplate:
    """
    Metrics Collector Template for IA Chéries Platform
    
    A comprehensive metrics collection system that provides:
    - Prometheus metrics integration
    - System and application metrics
    - Custom business metrics
    - Real-time metric processing
    """
    
    def __init__(self):
        self.service_name = "metrics-collector"
        self.service_version = "1.0.0"
        self.description = "Production-ready metrics collection with Prometheus integration"
    
    def create_collector(self, config: Dict[str, Any]) -> MetricsCollector:
        """Create a metrics collector instance"""
        return MetricsCollector(
            registry=config.get("registry"),
            service_name=config.get("service_name", "ainflue-service"),
            service_version=config.get("service_version", "1.0.0")
        )
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get metrics collector template information"""
        return {
            "name": self.service_name,
            "version": self.service_version,
            "description": self.description,
            "features": [
                "Prometheus metrics integration",
                "Custom metric registration",
                "System performance monitoring",
                "Application health metrics",
                "Business operation tracking",
                "Error and exception monitoring",
                "Cache and database metrics",
                "Real-time metric processing"
            ],
            "metric_types": [
                "Counter - Monotonically increasing values",
                "Gauge - Point-in-time values",
                "Histogram - Distribution of values",
                "Summary - Quantile calculations",
                "Info - Key-value information",
                "Enum - State-based metrics"
            ],
            "dependencies": ["prometheus_client", "psutil"],
            "endpoints": [
                "/metrics",
                "/metrics/summary",
                "/metrics/register",
                "/health/metrics"
            ]
        }