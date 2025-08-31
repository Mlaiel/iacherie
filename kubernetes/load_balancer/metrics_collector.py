"""Metrics Collector for Load Balancer

Advanced metrics collection and monitoring system for the IA Influencer
Agent platform's load balancer services, providing real-time analytics,
performance monitoring, and alerting capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""import time
import asyncio
import logging
import threading
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
import json
import psutil
import socket

# Prometheus client imports (optional)
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus client not available, metrics will only be stored locally")

# InfluxDB client imports (optional)
try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric types"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricScope(Enum):
    """Metric scope"""    GLOBAL = "global"
    PER_SERVICE = "per_service"
    PER_ENDPOINT = "per_endpoint"
    PER_SERVER = "per_server"
    PER_IP = "per_ip"


@dataclass
class MetricDefinition:
    """Metric definition"""    name: str
    type: MetricType
    scope: MetricScope
    description: str
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None
    unit: str = ""
    enabled: bool = True


@dataclass
class MetricData:
    """Metric data point"""    name: str
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    unit: str = ""


@dataclass
class LoadBalancerMetrics:
    """Load balancer performance metrics"""    requests_per_second: float = 0.0
    response_time_avg: float = 0.0
    response_time_p50: float = 0.0
    response_time_p95: float = 0.0
    response_time_p99: float = 0.0
    error_rate: float = 0.0
    active_connections: int = 0
    throughput_bytes_per_second: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_io: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


class MetricsBuffer:
    """Buffered metrics storage for batch processing"""    
    def __init__(self, max_size: int = 10000, flush_interval: int = 30):
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.buffer: deque = deque(maxlen=max_size)
        self.last_flush = time.time()
        self.lock = threading.Lock()
        self.flush_callbacks: List[Callable] = []
    
    def add_callback(self, callback: Callable[[List[MetricData]], None]) -> None:
        """Add flush callback"""        self.flush_callbacks.append(callback)
    
    def add_metric(self, metric: MetricData) -> None:
        """Add metric to buffer"""        with self.lock:
            self.buffer.append(metric)
            
            # Check if we need to flush
            if (len(self.buffer) >= self.max_size or 
                time.time() - self.last_flush >= self.flush_interval):
                self._flush()
    
    def _flush(self) -> None:
        """Flush buffer to callbacks"""        if not self.buffer:
            return
        
        metrics_to_flush = list(self.buffer)
        self.buffer.clear()
        self.last_flush = time.time()
        
        # Call all flush callbacks
        for callback in self.flush_callbacks:
            try:
                callback(metrics_to_flush)
            except Exception as e:
                logger.error(f"Metrics flush callback failed: {e}")
    
    def force_flush(self) -> None:
        """Force flush buffer"""        with self.lock:
            self._flush()


class PrometheusExporter:
    """Prometheus metrics exporter"""    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        if not PROMETHEUS_AVAILABLE:
            raise ImportError("Prometheus client not available")
        
        self.registry = registry or CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        self.lock = threading.Lock()
    
    def register_metric(self, definition: MetricDefinition) -> None:
        """Register metric with Prometheus"""        with self.lock:
            if definition.name in self.metrics:
                return
            
            try:
                if definition.type == MetricType.COUNTER:
                    metric = Counter(
                        definition.name,
                        definition.description,
                        definition.labels,
                        registry=self.registry
                    )
                elif definition.type == MetricType.GAUGE:
                    metric = Gauge(
                        definition.name,
                        definition.description,
                        definition.labels,
                        registry=self.registry
                    )
                elif definition.type == MetricType.HISTOGRAM:
                    metric = Histogram(
                        definition.name,
                        definition.description,
                        definition.labels,
                        buckets=definition.buckets,
                        registry=self.registry
                    )
                elif definition.type == MetricType.SUMMARY:
                    metric = Summary(
                        definition.name,
                        definition.description,
                        definition.labels,
                        registry=self.registry
                    )
                else:
                    raise ValueError(f"Unsupported metric type: {definition.type}")
                
                self.metrics[definition.name] = metric
                logger.debug(f"Registered Prometheus metric: {definition.name}")
                
            except Exception as e:
                logger.error(f"Failed to register Prometheus metric {definition.name}: {e}")
    
    def update_metric(self, metric_data: MetricData) -> None:
        """Update Prometheus metric"""        with self.lock:
            if metric_data.name not in self.metrics:
                logger.warning(f"Prometheus metric {metric_data.name} not registered")
                return
            
            try:
                metric = self.metrics[metric_data.name]
                
                if isinstance(metric, Counter):
                    if metric_data.labels:
                        metric.labels(**metric_data.labels).inc(metric_data.value)
                    else:
                        metric.inc(metric_data.value)
                elif isinstance(metric, Gauge):
                    if metric_data.labels:
                        metric.labels(**metric_data.labels).set(metric_data.value)
                    else:
                        metric.set(metric_data.value)
                elif isinstance(metric, (Histogram, Summary)):
                    if metric_data.labels:
                        metric.labels(**metric_data.labels).observe(metric_data.value)
                    else:
                        metric.observe(metric_data.value)
                
            except Exception as e:
                logger.error(f"Failed to update Prometheus metric {metric_data.name}: {e}")
    
    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus text format"""        try:
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate Prometheus metrics: {e}")
            return ""


class InfluxDBExporter:
    """InfluxDB metrics exporter"""    
    def __init__(self, url: str, token: str, org: str, bucket: str):
        if not INFLUXDB_AVAILABLE:
            raise ImportError("InfluxDB client not available")
        
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.bucket = bucket
        self.org = org
    
    def write_metrics(self, metrics: List[MetricData]) -> None:
        """Write metrics to InfluxDB"""        try:
            points = []
            for metric in metrics:
                point = Point(metric.name) \
                    .field("value", metric.value) \
                    .time(metric.timestamp, WritePrecision.S)
                
                # Add labels as tags
                for key, value in metric.labels.items():
                    point = point.tag(key, value)
                
                if metric.unit:
                    point = point.tag("unit", metric.unit)
                
                points.append(point)
            
            self.write_api.write(bucket=self.bucket, org=self.org, record=points)
            logger.debug(f"Wrote {len(points)} metrics to InfluxDB")
            
        except Exception as e:
            logger.error(f"Failed to write metrics to InfluxDB: {e}")
    
    def close(self) -> None:
        """Close InfluxDB client"""        if self.client:
            self.client.close()


class SystemMetricsCollector:
    """System metrics collector using psutil"""    
    def __init__(self):
        self.last_network_io = None
        self.last_disk_io = None
        self.last_cpu_times = None
        self.last_measurement_time = None
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system metrics"""        try:
            current_time = time.time()
            metrics = {}
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            metrics.update({
                'system_cpu_usage_percent': cpu_percent,
                'system_cpu_count': cpu_count,
                'system_load_avg_1m': load_avg[0],
                'system_load_avg_5m': load_avg[1],
                'system_load_avg_15m': load_avg[2]
            })
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            metrics.update({
                'system_memory_total_bytes': memory.total,
                'system_memory_used_bytes': memory.used,
                'system_memory_available_bytes': memory.available,
                'system_memory_usage_percent': memory.percent,
                'system_swap_total_bytes': swap.total,
                'system_swap_used_bytes': swap.used,
                'system_swap_usage_percent': swap.percent
            })
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            metrics.update({
                'system_disk_total_bytes': disk_usage.total,
                'system_disk_used_bytes': disk_usage.used,
                'system_disk_free_bytes': disk_usage.free,
                'system_disk_usage_percent': (disk_usage.used / disk_usage.total) * 100
            })
            
            if disk_io:
                metrics.update({
                    'system_disk_read_bytes_total': disk_io.read_bytes,
                    'system_disk_write_bytes_total': disk_io.write_bytes,
                    'system_disk_read_count_total': disk_io.read_count,
                    'system_disk_write_count_total': disk_io.write_count
                })
                
                # Calculate rates if we have previous measurements
                if self.last_disk_io and self.last_measurement_time:
                    time_delta = current_time - self.last_measurement_time
                    if time_delta > 0:
                        read_rate = (disk_io.read_bytes - self.last_disk_io.read_bytes) / time_delta
                        write_rate = (disk_io.write_bytes - self.last_disk_io.write_bytes) / time_delta
                        
                        metrics.update({
                            'system_disk_read_bytes_per_second': read_rate,
                            'system_disk_write_bytes_per_second': write_rate
                        })
                
                self.last_disk_io = disk_io
            
            # Network metrics
            network_io = psutil.net_io_counters()
            if network_io:
                metrics.update({
                    'system_network_bytes_sent_total': network_io.bytes_sent,
                    'system_network_bytes_recv_total': network_io.bytes_recv,
                    'system_network_packets_sent_total': network_io.packets_sent,
                    'system_network_packets_recv_total': network_io.packets_recv,
                    'system_network_errors_in_total': network_io.errin,
                    'system_network_errors_out_total': network_io.errout,
                    'system_network_drops_in_total': network_io.dropin,
                    'system_network_drops_out_total': network_io.dropout
                })
                
                # Calculate rates if we have previous measurements
                if self.last_network_io and self.last_measurement_time:
                    time_delta = current_time - self.last_measurement_time
                    if time_delta > 0:
                        sent_rate = (network_io.bytes_sent - self.last_network_io.bytes_sent) / time_delta
                        recv_rate = (network_io.bytes_recv - self.last_network_io.bytes_recv) / time_delta
                        
                        metrics.update({
                            'system_network_bytes_sent_per_second': sent_rate,
                            'system_network_bytes_recv_per_second': recv_rate
                        })
                
                self.last_network_io = network_io
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            metrics.update({
                'process_cpu_usage_percent': process.cpu_percent(),
                'process_memory_rss_bytes': process_memory.rss,
                'process_memory_vms_bytes': process_memory.vms,
                'process_threads_count': process.num_threads(),
                'process_fds_count': process.num_fds() if hasattr(process, 'num_fds') else 0
            })
            
            self.last_measurement_time = current_time
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}


class ResponseTimeTracker:
    """Track response times with percentile calculations"""    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.response_times = deque(maxlen=window_size)
        self.lock = threading.Lock()
    
    def add_response_time(self, response_time: float) -> None:
        """Add response time measurement"""        with self.lock:
            self.response_times.append(response_time)
    
    def get_statistics(self) -> Dict[str, float]:
        """Get response time statistics"""        with self.lock:
            if not self.response_times:
                return {
                    'avg': 0.0,
                    'min': 0.0,
                    'max': 0.0,
                    'p50': 0.0,
                    'p90': 0.0,
                    'p95': 0.0,
                    'p99': 0.0,
                    'count': 0
                }
            
            sorted_times = sorted(self.response_times)
            count = len(sorted_times)
            
            return {
                'avg': statistics.mean(sorted_times),
                'min': min(sorted_times),
                'max': max(sorted_times),
                'p50': statistics.median(sorted_times),
                'p90': sorted_times[int(0.90 * count)] if count > 0 else 0.0,
                'p95': sorted_times[int(0.95 * count)] if count > 0 else 0.0,
                'p99': sorted_times[int(0.99 * count)] if count > 0 else 0.0,
                'count': count
            }


class MetricsCollector:
    """Enterprise Metrics Collector for Load Balancer"""    
    def __init__(self, 
                 prometheus_enabled: bool = True,
                 influxdb_config: Optional[Dict[str, str]] = None,
                 collection_interval: int = 30):
        
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.metrics_buffer = MetricsBuffer()
        self.system_collector = SystemMetricsCollector()
        self.response_trackers: Dict[str, ResponseTimeTracker] = {}
        self.collection_interval = collection_interval
        self.running = False
        self.collection_task = None
        self.lock = threading.RLock()
        
        # Request tracking
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.active_connections = defaultdict(int)
        self.bytes_transferred = defaultdict(int)
        
        # Initialize exporters
        self.prometheus_exporter = None
        self.influxdb_exporter = None
        
        if prometheus_enabled and PROMETHEUS_AVAILABLE:
            try:
                self.prometheus_exporter = PrometheusExporter()
                self.metrics_buffer.add_callback(self._update_prometheus_metrics)
                logger.info("Prometheus exporter initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Prometheus exporter: {e}")
        
        if influxdb_config and INFLUXDB_AVAILABLE:
            try:
                self.influxdb_exporter = InfluxDBExporter(**influxdb_config)
                self.metrics_buffer.add_callback(self.influxdb_exporter.write_metrics)
                logger.info("InfluxDB exporter initialized")
            except Exception as e:
                logger.error(f"Failed to initialize InfluxDB exporter: {e}")
    
    def register_metric(self, definition: MetricDefinition) -> bool:
        """Register metric definition"""        try:
            with self.lock:
                self.metric_definitions[definition.name] = definition
                
                # Register with Prometheus if available
                if self.prometheus_exporter:
                    self.prometheus_exporter.register_metric(definition)
            
            logger.debug(f"Metric {definition.name} registered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register metric {definition.name}: {e}")
            return False
    
    def record_metric(self, name: str, value: Union[int, float], labels: Dict[str, str] = None) -> None:
        """Record metric value"""        try:
            labels = labels or {}
            metric_data = MetricData(
                name=name,
                value=value,
                labels=labels,
                timestamp=datetime.now()
            )
            
            self.metrics_buffer.add_metric(metric_data)
            
        except Exception as e:
            logger.error(f"Failed to record metric {name}: {e}")
    
    def record_request(self, 
                      service: str,
                      endpoint: str,
                      method: str,
                      status_code: int,
                      response_time: float,
                      bytes_sent: int = 0,
                      bytes_received: int = 0,
                      client_ip: str = "",
                      user_id: str = "") -> None:
        """Record HTTP request metrics"""        try:
            # Basic labels
            labels = {
                'service': service,
                'endpoint': endpoint,
                'method': method,
                'status_code': str(status_code)
            }
            
            # Record request count
            self.record_metric('http_requests_total', 1, labels)
            
            # Record response time
            self.record_metric('http_request_duration_seconds', response_time, labels)
            
            # Track response times for percentile calculations
            tracker_key = f"{service}:{endpoint}"
            if tracker_key not in self.response_trackers:
                self.response_trackers[tracker_key] = ResponseTimeTracker()
            self.response_trackers[tracker_key].add_response_time(response_time)
            
            # Record bytes transferred
            if bytes_sent > 0:
                self.record_metric('http_request_size_bytes', bytes_sent, labels)
            if bytes_received > 0:
                self.record_metric('http_response_size_bytes', bytes_received, labels)
            
            # Track errors
            if status_code >= 400:
                error_labels = labels.copy()
                error_labels['error_type'] = 'client_error' if status_code < 500 else 'server_error'
                self.record_metric('http_requests_errors_total', 1, error_labels)
            
            # Update internal counters for rate calculations
            with self.lock:
                key = f"{service}:{endpoint}"
                self.request_counts[key] += 1
                if status_code >= 400:
                    self.error_counts[key] += 1
                self.bytes_transferred[key] += bytes_sent + bytes_received
            
        except Exception as e:
            logger.error(f"Failed to record request metrics: {e}")
    
    def record_connection_event(self, service: str, event_type: str, client_ip: str = "") -> None:
        """Record connection events (open/close)"""        try:
            labels = {
                'service': service,
                'event_type': event_type
            }
            
            if client_ip:
                labels['client_ip'] = client_ip
            
            self.record_metric('connections_total', 1, labels)
            
            # Update active connections count
            with self.lock:
                if event_type == 'open':
                    self.active_connections[service] += 1
                elif event_type == 'close':
                    self.active_connections[service] = max(0, self.active_connections[service] - 1)
                
                self.record_metric('connections_active', self.active_connections[service], {'service': service})
            
        except Exception as e:
            logger.error(f"Failed to record connection event: {e}")
    
    def record_load_balancer_metrics(self, 
                                   server_id: str,
                                   requests_count: int,
                                   response_time: float,
                                   error_count: int,
                                   active_connections: int) -> None:
        """Record load balancer specific metrics"""        try:
            labels = {'server_id': server_id}
            
            self.record_metric('lb_server_requests_total', requests_count, labels)
            self.record_metric('lb_server_response_time_avg', response_time, labels)
            self.record_metric('lb_server_errors_total', error_count, labels)
            self.record_metric('lb_server_connections_active', active_connections, labels)
            
            # Calculate error rate
            if requests_count > 0:
                error_rate = error_count / requests_count
                self.record_metric('lb_server_error_rate', error_rate, labels)
            
        except Exception as e:
            logger.error(f"Failed to record load balancer metrics: {e}")
    
    def _update_prometheus_metrics(self, metrics: List[MetricData]) -> None:
        """Update Prometheus metrics from buffer"""        if not self.prometheus_exporter:
            return
        
        for metric in metrics:
            self.prometheus_exporter.update_metric(metric)
    
    async def _collect_system_metrics(self) -> None:
        """Collect system metrics periodically"""        while self.running:
            try:
                # Collect system metrics
                system_metrics = self.system_collector.collect_system_metrics()
                for name, value in system_metrics.items():
                    self.record_metric(name, value)
                
                # Collect response time percentiles
                for key, tracker in self.response_trackers.items():
                    stats = tracker.get_statistics()
                    service, endpoint = key.split(':', 1)
                    labels = {'service': service, 'endpoint': endpoint}
                    
                    for stat_name, stat_value in stats.items():
                        if stat_name != 'count':
                            metric_name = f'http_request_duration_{stat_name}_seconds'
                            self.record_metric(metric_name, stat_value, labels)
                
                # Calculate rates
                with self.lock:
                    current_time = time.time()
                    
                    # Request rates (simplified - would need proper time windowing in production)
                    for key, count in self.request_counts.items():
                        service, endpoint = key.split(':', 1)
                        labels = {'service': service, 'endpoint': endpoint}
                        # This is a simplified rate calculation
                        rate = count / self.collection_interval if self.collection_interval > 0 else 0
                        self.record_metric('http_requests_per_second', rate, labels)
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in system metrics collection: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def start_collection(self) -> None:
        """Start metrics collection"""        if self.running:
            logger.warning("Metrics collection already running")
            return
        
        self.running = True
        self.collection_task = asyncio.create_task(self._collect_system_metrics())
        logger.info("Metrics collection started")
    
    async def stop_collection(self) -> None:
        """Stop metrics collection"""        if not self.running:
            logger.warning("Metrics collection not running")
            return
        
        self.running = False
        
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining metrics
        self.metrics_buffer.force_flush()
        
        logger.info("Metrics collection stopped")
    
    def configure_platform_metrics(self) -> bool:
        """Configure metrics for platform services"""        try:
            metric_definitions = [
                # HTTP request metrics
                MetricDefinition(
                    name="http_requests_total",
                    type=MetricType.COUNTER,
                    scope=MetricScope.PER_ENDPOINT,
                    description="Total number of HTTP requests",
                    labels=["service", "endpoint", "method", "status_code"]
                ),
                MetricDefinition(
                    name="http_request_duration_seconds",
                    type=MetricType.HISTOGRAM,
                    scope=MetricScope.PER_ENDPOINT,
                    description="HTTP request duration in seconds",
                    labels=["service", "endpoint", "method", "status_code"],
                    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
                ),
                MetricDefinition(
                    name="http_requests_errors_total",
                    type=MetricType.COUNTER,
                    scope=MetricScope.PER_ENDPOINT,
                    description="Total number of HTTP request errors",
                    labels=["service", "endpoint", "method", "status_code", "error_type"]
                ),
                MetricDefinition(
                    name="http_request_size_bytes",
                    type=MetricType.HISTOGRAM,
                    scope=MetricScope.PER_ENDPOINT,
                    description="HTTP request size in bytes",
                    labels=["service", "endpoint", "method"],
                    buckets=[32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]
                ),
                MetricDefinition(
                    name="http_response_size_bytes",
                    type=MetricType.HISTOGRAM,
                    scope=MetricScope.PER_ENDPOINT,
                    description="HTTP response size in bytes",
                    labels=["service", "endpoint", "method"],
                    buckets=[32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]
                ),
                
                # Connection metrics
                MetricDefinition(
                    name="connections_total",
                    type=MetricType.COUNTER,
                    scope=MetricScope.PER_SERVICE,
                    description="Total number of connections",
                    labels=["service", "event_type"]
                ),
                MetricDefinition(
                    name="connections_active",
                    type=MetricType.GAUGE,
                    scope=MetricScope.PER_SERVICE,
                    description="Number of active connections",
                    labels=["service"]
                ),
                
                # Load balancer metrics
                MetricDefinition(
                    name="lb_server_requests_total",
                    type=MetricType.COUNTER,
                    scope=MetricScope.PER_SERVER,
                    description="Total requests per load balancer server",
                    labels=["server_id"]
                ),
                MetricDefinition(
                    name="lb_server_response_time_avg",
                    type=MetricType.GAUGE,
                    scope=MetricScope.PER_SERVER,
                    description="Average response time per server",
                    labels=["server_id"]
                ),
                MetricDefinition(
                    name="lb_server_errors_total",
                    type=MetricType.COUNTER,
                    scope=MetricScope.PER_SERVER,
                    description="Total errors per server",
                    labels=["server_id"]
                ),
                MetricDefinition(
                    name="lb_server_error_rate",
                    type=MetricType.GAUGE,
                    scope=MetricScope.PER_SERVER,
                    description="Error rate per server",
                    labels=["server_id"]
                ),
                MetricDefinition(
                    name="lb_server_connections_active",
                    type=MetricType.GAUGE,
                    scope=MetricScope.PER_SERVER,
                    description="Active connections per server",
                    labels=["server_id"]
                ),
                
                # System metrics
                MetricDefinition(
                    name="system_cpu_usage_percent",
                    type=MetricType.GAUGE,
                    scope=MetricScope.GLOBAL,
                    description="System CPU usage percentage",
                    unit="percent"
                ),
                MetricDefinition(
                    name="system_memory_usage_percent",
                    type=MetricType.GAUGE,
                    scope=MetricScope.GLOBAL,
                    description="System memory usage percentage",
                    unit="percent"
                ),
                MetricDefinition(
                    name="system_memory_used_bytes",
                    type=MetricType.GAUGE,
                    scope=MetricScope.GLOBAL,
                    description="System memory used in bytes",
                    unit="bytes"
                ),
                MetricDefinition(
                    name="system_network_bytes_sent_per_second",
                    type=MetricType.GAUGE,
                    scope=MetricScope.GLOBAL,
                    description="Network bytes sent per second",
                    unit="bytes/s"
                ),
                MetricDefinition(
                    name="system_network_bytes_recv_per_second",
                    type=MetricType.GAUGE,
                    scope=MetricScope.GLOBAL,
                    description="Network bytes received per second",
                    unit="bytes/s"
                ),
                MetricDefinition(
                    name="system_disk_usage_percent",
                    type=MetricType.GAUGE,
                    scope=MetricScope.GLOBAL,
                    description="Disk usage percentage",
                    unit="percent"
                ),
                
                # Application-specific metrics
                MetricDefinition(
                    name="fingerprinting_requests_total",
                    type=MetricType.COUNTER,
                    scope=MetricScope.PER_SERVICE,
                    description="Total fingerprinting requests",
                    labels=["content_type"]
                ),
                MetricDefinition(
                    name="fingerprinting_duration_seconds",
                    type=MetricType.HISTOGRAM,
                    scope=MetricScope.PER_SERVICE,
                    description="Fingerprinting process duration",
                    labels=["content_type"],
                    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
                ),
                MetricDefinition(
                    name="protection_alerts_total",
                    type=MetricType.COUNTER,
                    scope=MetricScope.PER_SERVICE,
                    description="Total protection alerts generated",
                    labels=["alert_type", "severity"]
                ),
                MetricDefinition(
                    name="monetization_transactions_total",
                    type=MetricType.COUNTER,
                    scope=MetricScope.PER_SERVICE,
                    description="Total monetization transactions",
                    labels=["transaction_type", "status"]
                ),
                MetricDefinition(
                    name="ai_generation_requests_total",
                    type=MetricType.COUNTER,
                    scope=MetricScope.PER_SERVICE,
                    description="Total AI generation requests",
                    labels=["generation_type"]
                ),
                MetricDefinition(
                    name="crawler_requests_total",
                    type=MetricType.COUNTER,
                    scope=MetricScope.PER_SERVICE,
                    description="Total crawler requests",
                    labels=["platform", "status"]
                )
            ]
            
            # Register all metrics
            for definition in metric_definitions:
                self.register_metric(definition)
            
            logger.info(f"Platform metrics configured: {len(metric_definitions)} metrics")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure platform metrics: {e}")
            return False
    
    def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format"""        if self.prometheus_exporter:
            return self.prometheus_exporter.get_metrics_text()
        return "# Prometheus metrics not available\n"
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""        with self.lock:
            summary = {
                "registered_metrics": len(self.metric_definitions),
                "active_response_trackers": len(self.response_trackers),
                "prometheus_enabled": self.prometheus_exporter is not None,
                "influxdb_enabled": self.influxdb_exporter is not None,
                "collection_running": self.running,
                "collection_interval": self.collection_interval,
                "buffer_size": len(self.metrics_buffer.buffer),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add response time statistics
            response_stats = {}
            for key, tracker in self.response_trackers.items():
                response_stats[key] = tracker.get_statistics()
            
            summary["response_time_stats"] = response_stats
            
            return summary
    
    def cleanup(self) -> None:
        """Cleanup resources"""        try:
            if self.influxdb_exporter:
                self.influxdb_exporter.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
