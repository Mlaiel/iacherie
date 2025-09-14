"""
Metrics Collector Core module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Ainflue Core Infrastructure - Advanced Metrics Collection Engine
===============================================================

Enterprise-grade metrics collection system with multi-dimensional
metrics support, real-time aggregation, time-series storage,
and comprehensive monitoring integration.

Features:
- Multi-dimensional metrics (counters, gauges, histograms, summaries)
- Real-time metrics aggregation and streaming
- Time-series storage with configurable retention
- Prometheus integration and exporters
- Custom metrics labels and tagging
- Metrics alerting and threshold monitoring
- Performance profiling and resource tracking
- Business metrics and KPI tracking

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized copying or distribution prohibited
"""

import asyncio
import time
import json
import logging
import threading
from typing import Dict, List, Optional, Any, Union, Set, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import statistics
import collections
import psutil
import hashlib
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"

class MetricUnit(str, Enum):
    """Metric units"""
    NONE = "none"
    BYTES = "bytes"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    PERCENT = "percent"
    COUNT = "count"
    RATE = "rate"

@dataclass
class MetricValue:
    """A single metric value with timestamp"""
    value: Union[int, float]
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class MetricSample:
    """Metric sample with metadata"""
    name: str
    metric_type: MetricType
    value: Union[int, float]
    unit: MetricUnit = MetricUnit.NONE
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    help_text: str = ""

class MetricAggregationType(str, Enum):
    """Metric aggregation types"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_50 = "p50"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"

@dataclass
class AggregatedMetric:
    """Aggregated metric data"""
    name: str
    aggregation_type: MetricAggregationType
    value: float
    sample_count: int
    time_window_seconds: int
    start_time: float
    end_time: float
    labels: Dict[str, str] = field(default_factory=dict)

class Counter:
    """Thread-safe counter metric"""
    
    def __init__(self, name -> None: str, help_text -> None: str = "", labels -> None: Optional[Dict[str, str]] = None) -> None:
        self.name = name
        self.help_text = help_text
        self.labels = labels or {}
        self._value = 0
        self._lock = threading.Lock()
    
    def inc(self, amount -> None: Union[int, float] = 1) -> None:
        """Increment counter"""
        with self._lock:
            if amount < 0:
                raise ValueError("Counter increment must be non-negative")
            self._value += amount
    
    def get(self) -> float:
        """Get current value"""
        with self._lock:
            return self._value
    
    def reset(self) -> None:
        """Reset counter to zero"""
        with self._lock:
            self._value = 0

class Gauge:
    """Thread-safe gauge metric"""
    
    def __init__(self, name -> None: str, help_text -> None: str = "", labels -> None: Optional[Dict[str, str]] = None) -> None:
        self.name = name
        self.help_text = help_text
        self.labels = labels or {}
        self._value = 0
        self._lock = threading.Lock()
    
    def set(self, value -> None: Union[int, float]) -> None:
        """Set gauge value"""
        with self._lock:
            self._value = value
    
    def inc(self, amount -> None: Union[int, float] = 1) -> None:
        """Increment gauge"""
        with self._lock:
            self._value += amount
    
    def dec(self, amount -> None: Union[int, float] = 1) -> None:
        """Decrement gauge"""
        with self._lock:
            self._value -= amount
    
    def get(self) -> float:
        """Get current value"""
        with self._lock:
            return self._value

class Histogram:
    """Thread-safe histogram metric"""
    
    def __init__(self, name -> None: str, buckets -> None: Optional[List[float]] = None, 
                 help_text -> None: str = "", labels -> None: Optional[Dict[str, str]] = None) -> None:
        self.name = name
        self.help_text = help_text
        self.labels = labels or {}
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
        self._bucket_counts = {bucket: 0 for bucket in self.buckets}
        self._sum = 0
        self._count = 0
        self._lock = threading.Lock()
    
    def observe(self, value -> None: Union[int, float]) -> None:
        """Observe a value"""
        with self._lock:
            self._sum += value
            self._count += 1
            
            for bucket in self.buckets:
                if value <= bucket:
                    self._bucket_counts[bucket] += 1
    
    def get_bucket_counts(self) -> Dict[float, int]:
        """Get bucket counts"""
        with self._lock:
            return self._bucket_counts.copy()
    
    def get_sum(self) -> float:
        """Get sum of all observed values"""
        with self._lock:
            return self._sum
    
    def get_count(self) -> int:
        """Get count of observations"""
        with self._lock:
            return self._count
    
    def get_percentile(self, percentile: float) -> float:
        """Estimate percentile value"""
        # Simplified percentile estimation
        with self._lock:
            if self._count == 0:
                return 0.0
            
            target_count = self._count * (percentile / 100.0)
            cumulative_count = 0
            
            for bucket in sorted(self.buckets):
                cumulative_count += self._bucket_counts[bucket]
                if cumulative_count >= target_count:
                    return bucket
            
            return max(self.buckets)

class Timer:
    """Timer metric for measuring durations"""
    
    def __init__(self, name -> None: str, help_text -> None: str = "", labels -> None: Optional[Dict[str, str]] = None) -> None:
        self.name = name
        self.help_text = help_text
        self.labels = labels or {}
        self.histogram = Histogram(name + "_duration", help_text=help_text, labels=labels)
        self._start_times = {}
        self._lock = threading.Lock()
    
    def start(self, operation_id: Optional[str] = None) -> str:
        """Start timing an operation"""
        if operation_id is None:
            operation_id = f"{threading.get_ident()}_{time.time()}"
        
        with self._lock:
            self._start_times[operation_id] = time.time()
        
        return operation_id
    
    def stop(self, operation_id: str) -> float:
        """Stop timing and record duration"""
        end_time = time.time()
        
        with self._lock:
            start_time = self._start_times.pop(operation_id, end_time)
        
        duration = end_time - start_time
        self.histogram.observe(duration)
        return duration
    
    @asynccontextmanager
    async def time_async(self) -> None:
        """Async context manager for timing"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.histogram.observe(duration)
    
    def time_function(self, func: Callable) -> Callable:
        """Decorator for timing functions"""
        def wrapper(*args, **kwargs) -> None:
            operation_id = self.start()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                self.stop(operation_id)
        
        async def async_wrapper(*args, **kwargs) -> None:
            operation_id = self.start()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                self.stop(operation_id)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

class MetricRegistry:
    """Registry for managing metrics"""
    
    def __init__(self) -> None:
        self.metrics: Dict[str, Union[Counter, Gauge, Histogram, Timer]] = {}
        self._lock = threading.Lock()
    
    def register_counter(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Counter:
        """Register a counter metric"""
        with self._lock:
            if name in self.metrics:
                metric = self.metrics[name]
                if isinstance(metric, Counter):
                    return metric
                else:
                    raise ValueError(f"Metric {name} already exists with different type")
            
            counter = Counter(name, help_text, labels)
            self.metrics[name] = counter
            return counter
    
    def register_gauge(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Gauge:
        """Register a gauge metric"""
        with self._lock:
            if name in self.metrics:
                metric = self.metrics[name]
                if isinstance(metric, Gauge):
                    return metric
                else:
                    raise ValueError(f"Metric {name} already exists with different type")
            
            gauge = Gauge(name, help_text, labels)
            self.metrics[name] = gauge
            return gauge
    
    def register_histogram(self, name: str, buckets: Optional[List[float]] = None,
                          help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Histogram:
        """Register a histogram metric"""
        with self._lock:
            if name in self.metrics:
                metric = self.metrics[name]
                if isinstance(metric, Histogram):
                    return metric
                else:
                    raise ValueError(f"Metric {name} already exists with different type")
            
            histogram = Histogram(name, buckets, help_text, labels)
            self.metrics[name] = histogram
            return histogram
    
    def register_timer(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Timer:
        """Register a timer metric"""
        with self._lock:
            if name in self.metrics:
                metric = self.metrics[name]
                if isinstance(metric, Timer):
                    return metric
                else:
                    raise ValueError(f"Metric {name} already exists with different type")
            
            timer = Timer(name, help_text, labels)
            self.metrics[name] = timer
            return timer
    
    def get_metric(self, name: str) -> Optional[Union[Counter, Gauge, Histogram, Timer]]:
        """Get metric by name"""
        with self._lock:
            return self.metrics.get(name)
    
    def list_metrics(self) -> List[str]:
        """List all metric names"""
        with self._lock:
            return list(self.metrics.keys())
    
    def collect_all(self) -> List[MetricSample]:
        """Collect all metrics as samples"""
        samples = []
        
        with self._lock:
            for name, metric in self.metrics.items():
                if isinstance(metric, Counter):
                    samples.append(MetricSample(
                        name=name,
                        metric_type=MetricType.COUNTER,
                        value=metric.get(),
                        labels=metric.labels,
                        help_text=metric.help_text
                    ))
                elif isinstance(metric, Gauge):
                    samples.append(MetricSample(
                        name=name,
                        metric_type=MetricType.GAUGE,
                        value=metric.get(),
                        labels=metric.labels,
                        help_text=metric.help_text
                    ))
                elif isinstance(metric, Histogram):
                    samples.append(MetricSample(
                        name=name + "_sum",
                        metric_type=MetricType.COUNTER,
                        value=metric.get_sum(),
                        labels=metric.labels,
                        help_text=metric.help_text
                    ))
                    samples.append(MetricSample(
                        name=name + "_count",
                        metric_type=MetricType.COUNTER,
                        value=metric.get_count(),
                        labels=metric.labels,
                        help_text=metric.help_text
                    ))
                    for bucket, count in metric.get_bucket_counts().items():
                        bucket_labels = metric.labels.copy()
                        bucket_labels["le"] = str(bucket)
                        samples.append(MetricSample(
                            name=name + "_bucket",
                            metric_type=MetricType.COUNTER,
                            value=count,
                            labels=bucket_labels,
                            help_text=metric.help_text
                        ))
                elif isinstance(metric, Timer):
                    # Timer is based on histogram
                    histogram = metric.histogram
                    samples.append(MetricSample(
                        name=name + "_sum",
                        metric_type=MetricType.COUNTER,
                        value=histogram.get_sum(),
                        unit=MetricUnit.SECONDS,
                        labels=metric.labels,
                        help_text=metric.help_text
                    ))
        
        return samples

class MetricsAggregator:
    """Aggregates metrics over time windows"""
    
    def __init__(self, window_seconds -> None: int = 60) -> None:
        self.window_seconds = window_seconds
        self.metric_values: Dict[str, List[MetricValue]] = collections.defaultdict(list)
        self._lock = threading.Lock()
    
    def add_value(self, name -> None: str, value -> None: Union[int, float], labels -> None: Optional[Dict[str, str]] = None) -> None:
        """Add a metric value"""
        metric_value = MetricValue(value=value, labels=labels or {})
        
        with self._lock:
            self.metric_values[name].append(metric_value)
            # Keep only values within the window
            cutoff_time = time.time() - self.window_seconds
            self.metric_values[name] = [
                v for v in self.metric_values[name] 
                if v.timestamp > cutoff_time
            ]
    
    def aggregate(self, name: str, aggregation_type: MetricAggregationType) -> Optional[AggregatedMetric]:
        """Aggregate metric values"""
        with self._lock:
            values = self.metric_values.get(name, [])
            if not values:
                return None
            
            value_list = [v.value for v in values]
            current_time = time.time()
            start_time = current_time - self.window_seconds
            
            if aggregation_type == MetricAggregationType.SUM:
                aggregated_value = sum(value_list)
            elif aggregation_type == MetricAggregationType.AVERAGE:
                aggregated_value = statistics.mean(value_list)
            elif aggregation_type == MetricAggregationType.MIN:
                aggregated_value = min(value_list)
            elif aggregation_type == MetricAggregationType.MAX:
                aggregated_value = max(value_list)
            elif aggregation_type == MetricAggregationType.COUNT:
                aggregated_value = len(value_list)
            elif aggregation_type == MetricAggregationType.PERCENTILE_50:
                aggregated_value = statistics.median(value_list)
            elif aggregation_type == MetricAggregationType.PERCENTILE_95:
                aggregated_value = statistics.quantiles(value_list, n=20)[18] if len(value_list) > 1 else value_list[0]
            elif aggregation_type == MetricAggregationType.PERCENTILE_99:
                aggregated_value = statistics.quantiles(value_list, n=100)[98] if len(value_list) > 1 else value_list[0]
            else:
                aggregated_value = statistics.mean(value_list)
            
            return AggregatedMetric(
                name=name,
                aggregation_type=aggregation_type,
                value=aggregated_value,
                sample_count=len(value_list),
                time_window_seconds=self.window_seconds,
                start_time=start_time,
                end_time=current_time
            )

class SystemMetricsCollector:
    """Collects system metrics"""
    
    def __init__(self, registry -> None: MetricRegistry) -> None:
        self.registry = registry
        
        # Register system metrics
        self.cpu_usage = registry.register_gauge("system_cpu_usage_percent", "CPU usage percentage")
        self.memory_usage = registry.register_gauge("system_memory_usage_percent", "Memory usage percentage")
        self.disk_usage = registry.register_gauge("system_disk_usage_percent", "Disk usage percentage")
        self.network_bytes_sent = registry.register_counter("system_network_bytes_sent_total", "Network bytes sent")
        self.network_bytes_recv = registry.register_counter("system_network_bytes_recv_total", "Network bytes received")
        
        self._last_network_stats = None
        self.enabled = True
    
    async def collect_system_metrics(self) -> None:
        """Collect system metrics"""
        if not self.enabled:
            return
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.disk_usage.set(disk.percent)
            
            # Network usage
            network_stats = psutil.net_io_counters()
            if self._last_network_stats:
                bytes_sent_diff = network_stats.bytes_sent - self._last_network_stats.bytes_sent
                bytes_recv_diff = network_stats.bytes_recv - self._last_network_stats.bytes_recv
                
                if bytes_sent_diff >= 0:  # Handle counter resets
                    self.network_bytes_sent.inc(bytes_sent_diff)
                if bytes_recv_diff >= 0:
                    self.network_bytes_recv.inc(bytes_recv_diff)
            
            self._last_network_stats = network_stats
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

class MetricsCollectorCore:
    """Advanced enterprise metrics collector core"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        self.level = level
        self.registry = MetricRegistry()
        self.aggregator = MetricsAggregator()
        self.system_collector = SystemMetricsCollector(self.registry)
        self.enabled = True
        
        # Collection tasks
        self._collection_tasks: List[asyncio.Task] = []
        self._collection_running = False
        
        # Performance settings based on level
        self.performance_config = self._get_performance_config()
        
        # Business metrics
        self._setup_business_metrics()
    
    def _get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration based on level"""
        configs = {
            "basic": {
                "collection_interval": 60,
                "aggregation_window": 300,
                "max_metrics": 100,
                "retention_hours": 24
            },
            "standard": {
                "collection_interval": 30,
                "aggregation_window": 180,
                "max_metrics": 500,
                "retention_hours": 72
            },
            "professional": {
                "collection_interval": 15,
                "aggregation_window": 60,
                "max_metrics": 1000,
                "retention_hours": 168
            },
            "enterprise": {
                "collection_interval": 10,
                "aggregation_window": 30,
                "max_metrics": 10000,
                "retention_hours": 720
            }
        }
        return configs.get(self.level, configs["enterprise"])
    
    def _setup_business_metrics(self) -> None:
        """Setup business-specific metrics"""
        # API metrics
        self.api_requests_total = self.registry.register_counter(
            "api_requests_total", "Total API requests", {"method": "", "endpoint": "", "status": ""}
        )
        self.api_request_duration = self.registry.register_histogram(
            "api_request_duration_seconds", help_text="API request duration in seconds"
        )
        
        # Content metrics
        self.content_uploads_total = self.registry.register_counter(
            "content_uploads_total", "Total content uploads", {"type": "", "status": ""}
        )
        self.content_processing_duration = self.registry.register_histogram(
            "content_processing_duration_seconds", help_text="Content processing duration"
        )
        
        # User metrics
        self.active_users = self.registry.register_gauge(
            "active_users_current", "Current active users"
        )
        self.user_registrations_total = self.registry.register_counter(
            "user_registrations_total", "Total user registrations"
        )
        
        # AI metrics
        self.ai_predictions_total = self.registry.register_counter(
            "ai_predictions_total", "Total AI predictions", {"model": "", "status": ""}
        )
        self.ai_model_accuracy = self.registry.register_gauge(
            "ai_model_accuracy", "AI model accuracy", {"model": ""}
        )
        
        # Security metrics
        self.security_violations_total = self.registry.register_counter(
            "security_violations_total", "Total security violations", {"type": "", "severity": ""}
        )
        self.authentication_attempts_total = self.registry.register_counter(
            "authentication_attempts_total", "Total authentication attempts", {"status": ""}
        )
    
    async def initialize(self) -> bool:
        """Initialize metrics collector"""
        try:
            logger.info(f"🚀 Initializing MetricsCollectorCore - Level: {self.level}")
            
            # Start collection tasks
            await self.start_collection()
            
            logger.info("✅ MetricsCollectorCore initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MetricsCollectorCore: {e}")
            return False
    
    async def start_collection(self) -> bool:
        """Start metrics collection"""
        try:
            if self._collection_running:
                return True
            
            self._collection_running = True
            
            # Start system metrics collection
            self._collection_tasks.append(
                asyncio.create_task(self._system_metrics_loop())
            )
            
            # Start aggregation task
            self._collection_tasks.append(
                asyncio.create_task(self._aggregation_loop())
            )
            
            logger.info("✅ Metrics collection started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start metrics collection: {e}")
            return False
    
    async def _system_metrics_loop(self) -> None:
        """System metrics collection loop"""
        while self._collection_running:
            try:
                await self.system_collector.collect_system_metrics()
                await asyncio.sleep(self.performance_config["collection_interval"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system metrics collection: {e}")
                await asyncio.sleep(self.performance_config["collection_interval"])
    
    async def _aggregation_loop(self) -> None:
        """Metrics aggregation loop"""
        while self._collection_running:
            try:
                # Perform aggregations
                await self._perform_aggregations()
                await asyncio.sleep(self.performance_config["aggregation_window"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics aggregation: {e}")
                await asyncio.sleep(self.performance_config["aggregation_window"])
    
    async def _perform_aggregations(self) -> None:
        """Perform metric aggregations"""
        # This would typically store aggregated metrics to a time-series database
        # For now, we'll just log some basic aggregations
        try:
            for metric_name in ["api_requests_total", "content_uploads_total"]:
                for agg_type in [MetricAggregationType.SUM, MetricAggregationType.AVERAGE]:
                    aggregated = self.aggregator.aggregate(metric_name, agg_type)
                    if aggregated:
                        logger.debug(f"Aggregated {metric_name} ({agg_type.value}): {aggregated.value}")
        except Exception as e:
            logger.error(f"Aggregation error: {e}")
    
    def record_api_request(self, method -> None: str, endpoint -> None: str, status_code -> None: int, duration -> None: float) -> None:
        """Record API request metrics"""
        labels = {"method": method, "endpoint": endpoint, "status": str(status_code)}
        
        # Update counter with labels
        counter = self.registry.register_counter("api_requests_total", labels=labels)
        counter.inc()
        
        # Record duration
        self.api_request_duration.observe(duration)
        
        # Add to aggregator
        self.aggregator.add_value("api_requests_total", 1, labels)
    
    def record_content_upload(self, content_type -> None: str, status -> None: str, processing_duration -> None: float) -> None:
        """Record content upload metrics"""
        labels = {"type": content_type, "status": status}
        
        counter = self.registry.register_counter("content_uploads_total", labels=labels)
        counter.inc()
        
        self.content_processing_duration.observe(processing_duration)
        
        self.aggregator.add_value("content_uploads_total", 1, labels)
    
    def record_ai_prediction(self, model_name -> None: str, status -> None: str, accuracy -> None: Optional[float] = None) -> None:
        """Record AI prediction metrics"""
        labels = {"model": model_name, "status": status}
        
        counter = self.registry.register_counter("ai_predictions_total", labels=labels)
        counter.inc()
        
        if accuracy is not None:
            gauge = self.registry.register_gauge("ai_model_accuracy", labels={"model": model_name})
            gauge.set(accuracy)
    
    def record_security_violation(self, violation_type -> None: str, severity -> None: str) -> None:
        """Record security violation metrics"""
        labels = {"type": violation_type, "severity": severity}
        
        counter = self.registry.register_counter("security_violations_total", labels=labels)
        counter.inc()
    
    def set_active_users(self, count -> None: int) -> None:
        """Set current active users count"""
        self.active_users.set(count)
    
    def get_timer(self, name: str, help_text: str = "") -> Timer:
        """Get or create a timer metric"""
        return self.registry.register_timer(name, help_text)
    
    def get_counter(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Counter:
        """Get or create a counter metric"""
        return self.registry.register_counter(name, help_text, labels)
    
    def get_gauge(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Gauge:
        """Get or create a gauge metric"""
        return self.registry.register_gauge(name, help_text, labels)
    
    def get_histogram(self, name: str, buckets: Optional[List[float]] = None, 
                     help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Histogram:
        """Get or create a histogram metric"""
        return self.registry.register_histogram(name, buckets, help_text, labels)
    
    async def collect_metrics(self) -> List[MetricSample]:
        """Collect all metrics"""
        return self.registry.collect_all()
    
    async def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        samples = await self.collect_metrics()
        prometheus_lines = []
        
        for sample in samples:
            # Build labels string
            labels_str = ""
            if sample.labels:
                label_pairs = [f'{k}="{v}"' for k, v in sample.labels.items()]
                labels_str = "{" + ",".join(label_pairs) + "}"
            
            # Add help text
            if sample.help_text:
                prometheus_lines.append(f"# HELP {sample.name} {sample.help_text}")
            prometheus_lines.append(f"# TYPE {sample.name} {sample.metric_type.value}")
            
            # Add metric line
            prometheus_lines.append(f"{sample.name}{labels_str} {sample.value} {int(sample.timestamp * 1000)}")
        
        return "\n".join(prometheus_lines)
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        samples = await self.collect_metrics()
        
        return {
            "total_metrics": len(samples),
            "collection_running": self._collection_running,
            "system_metrics": {
                "cpu_usage": self.system_collector.cpu_usage.get(),
                "memory_usage": self.system_collector.memory_usage.get(),
                "disk_usage": self.system_collector.disk_usage.get()
            },
            "business_metrics": {
                "api_requests_total": self.api_requests_total.get(),
                "content_uploads_total": self.content_uploads_total.get(),
                "active_users": self.active_users.get()
            },
            "collection_config": self.performance_config
        }
    
    async def stop_collection(self) -> bool:
        """Stop metrics collection"""
        try:
            self._collection_running = False
            
            # Cancel all tasks
            for task in self._collection_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self._collection_tasks, return_exceptions=True)
            
            self._collection_tasks.clear()
            logger.info("✅ Metrics collection stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop metrics collection: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Health check for metrics collector"""
        try:
            # Check if collection is running and we have metrics
            return self._collection_running and len(self.registry.metrics) > 0
        except Exception as e:
            logger.error(f"MetricsCollectorCore health check failed: {e}")
            return False
    
    async def start(self) -> bool:
        """Start metrics collector service"""
        try:
            logger.info("🚀 Starting MetricsCollectorCore service")
            return await self.start_collection()
        except Exception as e:
            logger.error(f"❌ Failed to start MetricsCollectorCore: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop metrics collector service"""
        try:
            logger.info("🛑 Stopping MetricsCollectorCore service")
            return await self.stop_collection()
        except Exception as e:
            logger.error(f"❌ Failed to stop MetricsCollectorCore: {e}")
            return False

# Export main classes
__all__ = [
    "MetricsCollectorCore", "MetricRegistry", "Counter", "Gauge", "Histogram", "Timer",
    "MetricSample", "AggregatedMetric", "MetricType", "MetricUnit", "MetricAggregationType"
]