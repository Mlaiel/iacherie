"""
🎯 Metrics Collection Microservice
Performance metrics collection, aggregation, and analytics service with real-time monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"
    RATE = "rate"


class MetricUnit(str, Enum):
    """Metric units"""
    NONE = "none"
    BYTES = "bytes"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    REQUESTS = "requests"
    ERRORS = "errors"
    PERCENT = "percent"
    COUNT = "count"


class AggregationType(str, Enum):
    """Aggregation types"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    RATE = "rate"
    P50 = "p50"
    P90 = "p90"
    P95 = "p95"
    P99 = "p99"


@dataclass
class MetricValue:
    """Single metric value"""
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }


@dataclass
class MetricDefinition:
    """Metric definition"""
    name: str
    type: MetricType
    unit: MetricUnit = MetricUnit.NONE
    description: str = ""
    labels: List[str] = field(default_factory=list)
    help_text: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MetricSeries:
    """Time series of metric values"""
    definition: MetricDefinition
    values: deque = field(default_factory=lambda: deque(maxlen=10000))
    current_value: Optional[Union[int, float]] = None
    last_updated: Optional[datetime] = None
    
    def add_value(self, value: Union[int, float], timestamp: datetime = None, tags: Dict[str, str] = None):
        """Add value to series"""
        timestamp = timestamp or datetime.utcnow()
        tags = tags or {}
        
        metric_value = MetricValue(value=value, timestamp=timestamp, tags=tags)
        self.values.append(metric_value)
        self.current_value = value
        self.last_updated = timestamp
        
    def get_aggregated_value(self, aggregation: AggregationType, 
                           start_time: datetime = None, end_time: datetime = None) -> Optional[float]:
        """Get aggregated value for time range"""
        if not self.values:
            return None
            
        # Filter by time range
        filtered_values = []
        for metric_value in self.values:
            if start_time and metric_value.timestamp < start_time:
                continue
            if end_time and metric_value.timestamp > end_time:
                continue
            filtered_values.append(metric_value.value)
            
        if not filtered_values:
            return None
            
        # Apply aggregation
        if aggregation == AggregationType.SUM:
            return sum(filtered_values)
        elif aggregation == AggregationType.AVG:
            return statistics.mean(filtered_values)
        elif aggregation == AggregationType.MIN:
            return min(filtered_values)
        elif aggregation == AggregationType.MAX:
            return max(filtered_values)
        elif aggregation == AggregationType.COUNT:
            return len(filtered_values)
        elif aggregation == AggregationType.P50:
            return statistics.median(filtered_values)
        elif aggregation == AggregationType.P90:
            return self._percentile(filtered_values, 0.90)
        elif aggregation == AggregationType.P95:
            return self._percentile(filtered_values, 0.95)
        elif aggregation == AggregationType.P99:
            return self._percentile(filtered_values, 0.99)
        elif aggregation == AggregationType.RATE:
            if len(filtered_values) < 2:
                return 0.0
            # Calculate rate per second
            time_span = (self.values[-1].timestamp - self.values[0].timestamp).total_seconds()
            if time_span <= 0:
                return 0.0
            return len(filtered_values) / time_span
            
        return None
        
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(percentile * (len(sorted_values) - 1))
        return sorted_values[index]


class Counter:
    """Counter metric implementation"""
    
    def __init__(self, name: str, description: str = "", labels: List[str] = None):
        self.definition = MetricDefinition(
            name=name,
            type=MetricType.COUNTER,
            description=description,
            labels=labels or []
        )
        self.series = MetricSeries(self.definition)
        self._value = 0
        self._lock = threading.Lock()
        
    def increment(self, amount: Union[int, float] = 1, tags: Dict[str, str] = None):
        """Increment counter"""
        with self._lock:
            self._value += amount
            self.series.add_value(self._value, tags=tags)
            
    def get_value(self) -> Union[int, float]:
        """Get current value"""
        return self._value
        
    def reset(self):
        """Reset counter"""
        with self._lock:
            self._value = 0
            self.series.add_value(self._value)


class Gauge:
    """Gauge metric implementation"""
    
    def __init__(self, name: str, description: str = "", labels: List[str] = None):
        self.definition = MetricDefinition(
            name=name,
            type=MetricType.GAUGE,
            description=description,
            labels=labels or []
        )
        self.series = MetricSeries(self.definition)
        self._value = 0
        self._lock = threading.Lock()
        
    def set(self, value: Union[int, float], tags: Dict[str, str] = None):
        """Set gauge value"""
        with self._lock:
            self._value = value
            self.series.add_value(self._value, tags=tags)
            
    def increment(self, amount: Union[int, float] = 1, tags: Dict[str, str] = None):
        """Increment gauge"""
        with self._lock:
            self._value += amount
            self.series.add_value(self._value, tags=tags)
            
    def decrement(self, amount: Union[int, float] = 1, tags: Dict[str, str] = None):
        """Decrement gauge"""
        with self._lock:
            self._value -= amount
            self.series.add_value(self._value, tags=tags)
            
    def get_value(self) -> Union[int, float]:
        """Get current value"""
        return self._value


class Histogram:
    """Histogram metric implementation"""
    
    def __init__(self, name: str, description: str = "", 
                 buckets: List[float] = None, labels: List[str] = None):
        self.definition = MetricDefinition(
            name=name,
            type=MetricType.HISTOGRAM,
            description=description,
            labels=labels or []
        )
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
        self.bucket_counts = {bucket: 0 for bucket in self.buckets}
        self.bucket_counts[float('inf')] = 0
        self.sum = 0
        self.count = 0
        self.series = MetricSeries(self.definition)
        self._lock = threading.Lock()
        
    def observe(self, value: Union[int, float], tags: Dict[str, str] = None):
        """Observe a value"""
        with self._lock:
            self.sum += value
            self.count += 1
            
            # Update buckets
            for bucket in self.buckets:
                if value <= bucket:
                    self.bucket_counts[bucket] += 1
                    
            # Always update infinity bucket
            self.bucket_counts[float('inf')] += 1
            
            # Add to series
            self.series.add_value(value, tags=tags)
            
    def get_bucket_counts(self) -> Dict[float, int]:
        """Get bucket counts"""
        return self.bucket_counts.copy()
        
    def get_percentile(self, percentile: float) -> float:
        """Calculate percentile from histogram"""
        if self.count == 0:
            return 0.0
            
        target_count = percentile * self.count
        cumulative_count = 0
        
        for bucket in sorted(self.buckets):
            cumulative_count += self.bucket_counts[bucket]
            if cumulative_count >= target_count:
                return bucket
                
        return float('inf')


class Timer:
    """Timer metric implementation with context manager"""
    
    def __init__(self, name: str, description: str = "", labels: List[str] = None):
        self.definition = MetricDefinition(
            name=name,
            type=MetricType.TIMER,
            unit=MetricUnit.SECONDS,
            description=description,
            labels=labels or []
        )
        self.histogram = Histogram(f"{name}_duration", description, labels=labels)
        self.series = MetricSeries(self.definition)
        self._start_time = None
        
    def start(self):
        """Start timer"""
        self._start_time = time.time()
        
    def stop(self, tags: Dict[str, str] = None) -> float:
        """Stop timer and return duration"""
        if self._start_time is None:
            return 0.0
            
        duration = time.time() - self._start_time
        self.histogram.observe(duration, tags)
        self.series.add_value(duration, tags=tags)
        self._start_time = None
        return duration
        
    def __enter__(self):
        """Enter context manager"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        self.stop()


class MetricCollector:
    """Collector for organizing related metrics"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.metrics: Dict[str, Union[Counter, Gauge, Histogram, Timer]] = {}
        
    def counter(self, name: str, description: str = "", labels: List[str] = None) -> Counter:
        """Create or get counter metric"""
        if name not in self.metrics:
            self.metrics[name] = Counter(f"{self.name}_{name}", description, labels)
        return self.metrics[name]
        
    def gauge(self, name: str, description: str = "", labels: List[str] = None) -> Gauge:
        """Create or get gauge metric"""
        if name not in self.metrics:
            self.metrics[name] = Gauge(f"{self.name}_{name}", description, labels)
        return self.metrics[name]
        
    def histogram(self, name: str, description: str = "", 
                  buckets: List[float] = None, labels: List[str] = None) -> Histogram:
        """Create or get histogram metric"""
        if name not in self.metrics:
            self.metrics[name] = Histogram(f"{self.name}_{name}", description, buckets, labels)
        return self.metrics[name]
        
    def timer(self, name: str, description: str = "", labels: List[str] = None) -> Timer:
        """Create or get timer metric"""
        if name not in self.metrics:
            self.metrics[name] = Timer(f"{self.name}_{name}", description, labels)
        return self.metrics[name]
        
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics data"""
        result = {}
        for name, metric in self.metrics.items():
            if isinstance(metric, (Counter, Gauge)):
                result[name] = metric.get_value()
            elif isinstance(metric, Histogram):
                result[name] = {
                    'count': metric.count,
                    'sum': metric.sum,
                    'buckets': metric.get_bucket_counts()
                }
            elif isinstance(metric, Timer):
                result[name] = {
                    'count': metric.histogram.count,
                    'sum': metric.histogram.sum,
                    'avg': metric.histogram.sum / metric.histogram.count if metric.histogram.count > 0 else 0
                }
        return result


class MetricsExporter(ABC):
    """Abstract metrics exporter"""
    
    @abstractmethod
    async def export_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Export metrics"""
        pass


class PrometheusExporter(MetricsExporter):
    """Prometheus metrics exporter"""
    
    def __init__(self, port: int = 8000, endpoint: str = "/metrics"):
        self.port = port
        self.endpoint = endpoint
        self.app = None
        
    async def export_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Export metrics in Prometheus format"""
        try:
            prometheus_output = self._format_prometheus(metrics)
            # In a real implementation, this would serve the metrics via HTTP
            logger.debug(f"Prometheus metrics exported: {len(prometheus_output)} lines")
            return True
        except Exception as e:
            logger.error(f"Error exporting to Prometheus: {str(e)}")
            return False
            
    def _format_prometheus(self, metrics: Dict[str, Any]) -> List[str]:
        """Format metrics for Prometheus"""
        lines = []
        
        for metric_name, metric_data in metrics.items():
            if isinstance(metric_data, (int, float)):
                lines.append(f"{metric_name} {metric_data}")
            elif isinstance(metric_data, dict):
                for key, value in metric_data.items():
                    if isinstance(value, (int, float)):
                        lines.append(f"{metric_name}_{key} {value}")
                        
        return lines


class JSONExporter(MetricsExporter):
    """JSON metrics exporter"""
    
    def __init__(self, output_file: str = None):
        self.output_file = output_file
        
    async def export_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Export metrics as JSON"""
        try:
            metrics_with_timestamp = {
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics
            }
            
            if self.output_file:
                with open(self.output_file, 'w') as f:
                    json.dump(metrics_with_timestamp, f, indent=2)
            else:
                logger.info(f"Metrics JSON: {json.dumps(metrics_with_timestamp)}")
                
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            return False


class MetricsService:
    """Performance Metrics Collection and Analytics Service"""
    
    def __init__(self, name: str = "metrics_service"):
        self.name = name
        self.collectors: Dict[str, MetricCollector] = {}
        self.global_metrics: Dict[str, Union[Counter, Gauge, Histogram, Timer]] = {}
        self.exporters: List[MetricsExporter] = []
        self.running = False
        self.export_interval = 60  # seconds
        self.export_task = None
        self._lock = threading.Lock()
        
        # Built-in system metrics
        self._setup_system_metrics()
        
    def _setup_system_metrics(self):
        """Setup system-level metrics"""
        system_collector = self.create_collector("system", "System-level metrics")
        
        # Create basic system metrics
        system_collector.gauge("memory_usage", "Memory usage in bytes")
        system_collector.gauge("cpu_usage", "CPU usage percentage")
        system_collector.counter("requests_total", "Total number of requests")
        system_collector.counter("errors_total", "Total number of errors")
        system_collector.histogram("request_duration", "Request duration in seconds")
        
        # Service-specific metrics
        service_collector = self.create_collector("service", "Service-level metrics")
        service_collector.gauge("uptime", "Service uptime in seconds")
        service_collector.gauge("active_connections", "Number of active connections")
        service_collector.counter("operations_total", "Total number of operations")
        
    async def start(self):
        """Start metrics service"""
        self.running = True
        
        # Start periodic export
        self.export_task = asyncio.create_task(self._export_periodically())
        
        # Update uptime metric
        uptime_gauge = self.get_collector("service").gauge("uptime")
        uptime_gauge.set(0)
        
        logger.info(f"Started metrics service: {self.name}")
        
    async def stop(self):
        """Stop metrics service"""
        self.running = False
        
        if self.export_task:
            self.export_task.cancel()
            try:
                await self.export_task
            except asyncio.CancelledError:
                pass
                
        # Final export
        await self._export_metrics()
        
        logger.info(f"Stopped metrics service: {self.name}")
        
    def create_collector(self, name: str, description: str = "") -> MetricCollector:
        """Create metric collector"""
        if name not in self.collectors:
            self.collectors[name] = MetricCollector(name, description)
            logger.info(f"Created metric collector: {name}")
        return self.collectors[name]
        
    def get_collector(self, name: str) -> Optional[MetricCollector]:
        """Get metric collector"""
        return self.collectors.get(name)
        
    def remove_collector(self, name: str):
        """Remove metric collector"""
        if name in self.collectors:
            del self.collectors[name]
            logger.info(f"Removed metric collector: {name}")
            
    def counter(self, name: str, description: str = "", labels: List[str] = None) -> Counter:
        """Create global counter metric"""
        if name not in self.global_metrics:
            self.global_metrics[name] = Counter(name, description, labels)
        return self.global_metrics[name]
        
    def gauge(self, name: str, description: str = "", labels: List[str] = None) -> Gauge:
        """Create global gauge metric"""
        if name not in self.global_metrics:
            self.global_metrics[name] = Gauge(name, description, labels)
        return self.global_metrics[name]
        
    def histogram(self, name: str, description: str = "", 
                  buckets: List[float] = None, labels: List[str] = None) -> Histogram:
        """Create global histogram metric"""
        if name not in self.global_metrics:
            self.global_metrics[name] = Histogram(name, description, buckets, labels)
        return self.global_metrics[name]
        
    def timer(self, name: str, description: str = "", labels: List[str] = None) -> Timer:
        """Create global timer metric"""
        if name not in self.global_metrics:
            self.global_metrics[name] = Timer(name, description, labels)
        return self.global_metrics[name]
        
    def add_exporter(self, exporter: MetricsExporter):
        """Add metrics exporter"""
        self.exporters.append(exporter)
        logger.info(f"Added metrics exporter: {type(exporter).__name__}")
        
    def remove_exporter(self, exporter: MetricsExporter):
        """Remove metrics exporter"""
        if exporter in self.exporters:
            self.exporters.remove(exporter)
            logger.info(f"Removed metrics exporter: {type(exporter).__name__}")
            
    def set_export_interval(self, interval: int):
        """Set export interval in seconds"""
        self.export_interval = interval
        
    async def record_request(self, duration: float, status_code: int = 200, tags: Dict[str, str] = None):
        """Record HTTP request metrics"""
        tags = tags or {}
        
        # Update request metrics
        requests_counter = self.get_collector("system").counter("requests_total")
        requests_counter.increment(tags=tags)
        
        # Update duration histogram
        duration_histogram = self.get_collector("system").histogram("request_duration")
        duration_histogram.observe(duration, tags=tags)
        
        # Update error counter if needed
        if status_code >= 400:
            errors_counter = self.get_collector("system").counter("errors_total")
            errors_counter.increment(tags={**tags, 'status_code': str(status_code)})
            
    async def record_operation(self, operation_name: str, duration: float, 
                             success: bool = True, tags: Dict[str, str] = None):
        """Record operation metrics"""
        tags = tags or {}
        tags['operation'] = operation_name
        tags['success'] = str(success)
        
        # Update operation counter
        operations_counter = self.get_collector("service").counter("operations_total")
        operations_counter.increment(tags=tags)
        
        # Create operation-specific timer if it doesn't exist
        timer_name = f"operation_{operation_name}_duration"
        if timer_name not in self.global_metrics:
            self.timer(timer_name, f"Duration of {operation_name} operations")
            
        # Record duration
        operation_timer = self.global_metrics[timer_name]
        operation_timer.histogram.observe(duration, tags=tags)
        
    def update_system_metrics(self):
        """Update system metrics"""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_gauge = self.get_collector("system").gauge("memory_usage")
            memory_gauge.set(memory.used)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            cpu_gauge = self.get_collector("system").gauge("cpu_usage")
            cpu_gauge.set(cpu_percent)
            
        except ImportError:
            logger.warning("psutil not available, skipping system metrics")
        except Exception as e:
            logger.error(f"Error updating system metrics: {str(e)}")
            
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics data"""
        all_metrics = {}
        
        # Global metrics
        for name, metric in self.global_metrics.items():
            if isinstance(metric, (Counter, Gauge)):
                all_metrics[name] = metric.get_value()
            elif isinstance(metric, Histogram):
                all_metrics[name] = {
                    'count': metric.count,
                    'sum': metric.sum,
                    'buckets': metric.get_bucket_counts(),
                    'avg': metric.sum / metric.count if metric.count > 0 else 0
                }
            elif isinstance(metric, Timer):
                all_metrics[name] = {
                    'count': metric.histogram.count,
                    'sum': metric.histogram.sum,
                    'avg': metric.histogram.sum / metric.histogram.count if metric.histogram.count > 0 else 0
                }
                
        # Collector metrics
        for collector_name, collector in self.collectors.items():
            collector_metrics = collector.get_all_metrics()
            for metric_name, metric_value in collector_metrics.items():
                full_name = f"{collector_name}_{metric_name}"
                all_metrics[full_name] = metric_value
                
        return all_metrics
        
    async def _export_metrics(self):
        """Export metrics to all exporters"""
        try:
            # Update system metrics before export
            self.update_system_metrics()
            
            # Get all metrics
            metrics = self.get_all_metrics()
            
            # Export to all exporters
            for exporter in self.exporters:
                try:
                    await exporter.export_metrics(metrics)
                except Exception as e:
                    logger.error(f"Error in exporter {type(exporter).__name__}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error exporting metrics: {str(e)}")
            
    async def _export_periodically(self):
        """Periodically export metrics"""
        while self.running:
            try:
                await asyncio.sleep(self.export_interval)
                await self._export_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic export: {str(e)}")
                
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "name": self.name,
            "status": "running" if self.running else "stopped",
            "collectors_count": len(self.collectors),
            "global_metrics_count": len(self.global_metrics),
            "exporters_count": len(self.exporters),
            "export_interval": self.export_interval,
            "collectors": list(self.collectors.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }


def create_metrics_service(config: Dict[str, Any] = None) -> MetricsService:
    """Factory function to create Metrics service"""
    config = config or {}
    service_name = config.get('name', 'metrics_service')
    
    service = MetricsService(service_name)
    
    # Configure export interval
    if 'export_interval' in config:
        service.set_export_interval(config['export_interval'])
        
    # Add exporters
    if 'exporters' in config:
        for exporter_config in config['exporters']:
            exporter_type = exporter_config.get('type')
            
            if exporter_type == 'prometheus':
                exporter = PrometheusExporter(
                    port=exporter_config.get('port', 8000),
                    endpoint=exporter_config.get('endpoint', '/metrics')
                )
                service.add_exporter(exporter)
                
            elif exporter_type == 'json':
                exporter = JSONExporter(
                    output_file=exporter_config.get('output_file')
                )
                service.add_exporter(exporter)
                
    return service


__all__ = [
    'MetricsService', 'MetricCollector', 'Counter', 'Gauge', 'Histogram', 'Timer',
    'MetricType', 'MetricUnit', 'AggregationType', 'MetricDefinition',
    'PrometheusExporter', 'JSONExporter', 'create_metrics_service'
]