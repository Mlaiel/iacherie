"""
Advanced Metrics Collection Module

Enterprise-grade metrics collection, analysis and monitoring for industrial AI content platform.
Supports multi-format content creators (musicians, bloggers, photographers, influencers, comedians).

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""

import time
import threading
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable, TypeVar, Generic
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from contextlib import contextmanager
import statistics
import json
import logging
from functools import wraps
import gc

# Mock psutil if not available
try:
    import psutil
except ImportError:
    psutil = None

def utc_now():
    """Get current UTC datetime in a timezone-aware manner"""
    return datetime.now(timezone.utc)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class MetricType(Enum):
    """Advanced metric types for comprehensive monitoring"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"
    PERCENTILE = "percentile"
    DISTRIBUTION = "distribution"
    HEALTH_CHECK = "health_check"
    BUSINESS_METRIC = "business_metric"


class MetricPriority(Enum):
    """Metric priority levels for alerting and monitoring"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AggregationType(Enum):
    """Types of metric aggregation"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    P95 = "p95"
    P99 = "p99"
    STD_DEV = "std_dev"


@dataclass
class MetricEntry:
    """Advanced metric entry with comprehensive metadata"""
    name: str
    value: Union[int, float, bool, str]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: MetricPriority = MetricPriority.MEDIUM
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric entry to dictionary for serialization"""
        return {
            "name": self.name,
            "value": self.value,
            "metric_type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "session_id": self.session_id
        }


@dataclass
class PerformanceSnapshot:
    """System performance snapshot"""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def capture(cls) -> 'PerformanceSnapshot':
        """Capture current system performance"""
        if psutil is None:
            # Return mock values when psutil is not available
            return cls(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io={"bytes_sent": 0, "bytes_recv": 0}
            )
        
        return cls(
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage_percent=psutil.disk_usage('/').percent,
            network_io=dict(psutil.net_io_counters()._asdict())
        )


class TimerContext:
    """Context manager for timing operations with advanced features"""
    
    def __init__(
        self,
        collector: 'MetricsCollector',
        metric_name: str,
        tags: Optional[Dict[str, str]] = None,
        threshold_warning: Optional[float] = None,
        threshold_critical: Optional[float] = None,
        auto_gc: bool = False
    ):
        self.collector = collector
        self.metric_name = metric_name
        self.tags = tags or {}
        self.threshold_warning = threshold_warning
        self.threshold_critical = threshold_critical
        self.auto_gc = auto_gc
        self.start_time = None
        self.end_time = None
        
    def __enter__(self):
        if self.auto_gc:
            gc.collect()
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        duration = self.end_time - self.start_time
        
        # Determine priority based on thresholds
        priority = MetricPriority.LOW
        if self.threshold_critical and duration > self.threshold_critical:
            priority = MetricPriority.CRITICAL
        elif self.threshold_warning and duration > self.threshold_warning:
            priority = MetricPriority.HIGH
            
        # Add exception info to tags if error occurred
        if exc_type:
            self.tags["error"] = str(exc_type.__name__)
            self.tags["error_message"] = str(exc_val)
            priority = MetricPriority.HIGH
            
        self.collector.record_timer(
            self.metric_name,
            duration,
            tags=self.tags,
            priority=priority
        )
        
        # Log warnings for slow operations
        if self.threshold_warning and duration > self.threshold_warning:
            logger.warning(
                f"Slow operation detected: {self.metric_name} took {duration:.3f}s"
            )


class MetricsAggregator:
    """Advanced metrics aggregation engine"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        
    def add_value(self, metric_name: str, value: float):
        """Add value to aggregation window"""
        self.data[metric_name].append(value)
        
    def get_aggregation(
        self,
        metric_name: str,
        aggregation_type: AggregationType
    ) -> Optional[float]:
        """Get aggregated value for metric"""
        values = list(self.data.get(metric_name, []))
        if not values:
            return None
            
        if aggregation_type == AggregationType.SUM:
            return sum(values)
        elif aggregation_type == AggregationType.AVERAGE:
            return statistics.mean(values)
        elif aggregation_type == AggregationType.MIN:
            return min(values)
        elif aggregation_type == AggregationType.MAX:
            return max(values)
        elif aggregation_type == AggregationType.COUNT:
            return len(values)
        elif aggregation_type == AggregationType.MEDIAN:
            return statistics.median(values)
        elif aggregation_type == AggregationType.P95:
            return self._percentile(values, 95)
        elif aggregation_type == AggregationType.P99:
            return self._percentile(values, 99)
        elif aggregation_type == AggregationType.STD_DEV:
            return statistics.stdev(values) if len(values) > 1 else 0
            
        return None
        
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]


class BusinessMetricsTracker:
    """Specialized tracker for business-critical metrics"""
    
    def __init__(self):
        self.user_engagement = MetricsAggregator()
        self.content_metrics = MetricsAggregator()
        self.revenue_metrics = MetricsAggregator()
        self.protection_metrics = MetricsAggregator()
        
    def track_user_action(
        self,
        action: str,
        user_id: str,
        content_type: Optional[str] = None,
        value: float = 1.0
    ):
        """Track user engagement actions"""
        metric_name = f"user_action_{action}"
        self.user_engagement.add_value(metric_name, value)
        
    def track_content_quality(
        self,
        content_id: str,
        quality_score: float,
        content_type: str
    ):
        """Track content quality metrics"""
        metric_name = f"content_quality_{content_type}"
        self.content_metrics.add_value(metric_name, quality_score)
        
    def track_revenue_event(
        self,
        event_type: str,
        amount: float,
        currency: str = "USD"
    ):
        """Track revenue-related events"""
        metric_name = f"revenue_{event_type}_{currency}"
        self.revenue_metrics.add_value(metric_name, amount)
        
    def track_protection_event(
        self,
        event_type: str,
        content_id: str,
        confidence_score: float
    ):
        """Track content protection events"""
        metric_name = f"protection_{event_type}"
        self.protection_metrics.add_value(metric_name, confidence_score)


class MetricsCollector:
    """
    Enterprise-grade metrics collection and monitoring system
    
    Features:
    - Real-time metric collection
    - Advanced aggregation
    - Performance monitoring
    - Business metrics tracking
    - Alert threshold management
    - Multi-threaded collection
    """
    
    def __init__(
        self,
        max_entries: int = 10000,
        auto_flush_interval: int = 300,  # 5 minutes
        enable_system_metrics: bool = True
    ):
        self.max_entries = max_entries
        self.auto_flush_interval = auto_flush_interval
        self.enable_system_metrics = enable_system_metrics
        
        # Core storage
        self.metrics: deque = deque(maxlen=max_entries)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Advanced components
        self.aggregator = MetricsAggregator()
        self.business_tracker = BusinessMetricsTracker()
        
        # Threading and concurrency
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._background_thread = None
        
        # Performance tracking
        self.start_time = time.time()
        self.last_flush = utc_now()
        self.performance_snapshots: deque = deque(maxlen=100)
        
        # Alert thresholds
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        self.alert_callbacks: List[Callable] = []
        
        if enable_system_metrics:
            self._start_system_monitoring()
            
    def _start_system_monitoring(self):
        """Start background system monitoring"""
        if self._background_thread is None:
            self._background_thread = threading.Thread(
                target=self._background_monitor,
                daemon=True
            )
            self._background_thread.start()
            
    def _background_monitor(self):
        """Background thread for system monitoring"""
        while not self._stop_event.wait(30):  # Check every 30 seconds
            try:
                # Capture system performance
                snapshot = PerformanceSnapshot.capture()
                self.performance_snapshots.append(snapshot)
                
                # Record system metrics
                self.record_gauge("system.cpu_percent", snapshot.cpu_percent)
                self.record_gauge("system.memory_percent", snapshot.memory_percent)
                self.record_gauge("system.disk_usage_percent", snapshot.disk_usage_percent)
                
                # Auto-flush if needed
                if (utc_now() - self.last_flush).seconds > self.auto_flush_interval:
                    self.flush_metrics()
                    
            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
                
    def increment_counter(
        self,
        name: str,
        value: int = 1,
        tags: Optional[Dict[str, str]] = None,
        priority: MetricPriority = MetricPriority.MEDIUM
    ) -> None:
        """Increment a counter metric with advanced features"""
        with self._lock:
            self.counters[name] += value
            
            entry = MetricEntry(
                name=name,
                value=self.counters[name],
                metric_type=MetricType.COUNTER,
                tags=tags or {},
                priority=priority
            )
            self.metrics.append(entry)
            
            # Check alert thresholds
            self._check_alert_threshold(name, self.counters[name])
            
    def record_gauge(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        priority: MetricPriority = MetricPriority.MEDIUM
    ) -> None:
        """Record a gauge metric"""
        with self._lock:
            self.gauges[name] = value
            
            entry = MetricEntry(
                name=name,
                value=value,
                metric_type=MetricType.GAUGE,
                tags=tags or {},
                priority=priority
            )
            self.metrics.append(entry)
            
            # Add to aggregator
            self.aggregator.add_value(name, value)
            
            # Check alert thresholds
            self._check_alert_threshold(name, value)
            
    def record_histogram(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        bucket_size: int = 1000
    ) -> None:
        """Record a histogram value"""
        with self._lock:
            if len(self.histograms[name]) >= bucket_size:
                self.histograms[name] = self.histograms[name][-bucket_size//2:]
                
            self.histograms[name].append(value)
            
            entry = MetricEntry(
                name=name,
                value=value,
                metric_type=MetricType.HISTOGRAM,
                tags=tags or {}
            )
            self.metrics.append(entry)
            
    def record_timer(
        self,
        name: str,
        duration: float,
        tags: Optional[Dict[str, str]] = None,
        priority: MetricPriority = MetricPriority.MEDIUM
    ) -> None:
        """Record a timer duration"""
        with self._lock:
            self.timers[name].append(duration)
            
            entry = MetricEntry(
                name=name,
                value=duration,
                metric_type=MetricType.TIMER,
                tags=tags or {},
                priority=priority
            )
            self.metrics.append(entry)
            
            # Add to aggregator
            self.aggregator.add_value(name, duration)
            
    def record_rate(
        self,
        name: str,
        events: int = 1,
        window_seconds: int = 60
    ) -> None:
        """Record rate metrics (events per time window)"""
        with self._lock:
            current_time = time.time()
            self.rates[name].append((current_time, events))
            
            # Calculate current rate
            cutoff_time = current_time - window_seconds
            recent_events = [
                events for timestamp, events in self.rates[name]
                if timestamp > cutoff_time
            ]
            current_rate = sum(recent_events) / window_seconds if recent_events else 0
            
            entry = MetricEntry(
                name=f"{name}_rate",
                value=current_rate,
                metric_type=MetricType.RATE,
                metadata={"window_seconds": window_seconds}
            )
            self.metrics.append(entry)
            
    def timer(
        self,
        name: str,
        tags: Optional[Dict[str, str]] = None,
        threshold_warning: Optional[float] = None,
        threshold_critical: Optional[float] = None,
        auto_gc: bool = False
    ) -> TimerContext:
        """Create a timer context manager"""
        return TimerContext(
            self,
            name,
            tags,
            threshold_warning,
            threshold_critical,
            auto_gc
        )
        
    def set_alert_threshold(
        self,
        metric_name: str,
        warning_threshold: Optional[float] = None,
        critical_threshold: Optional[float] = None
    ):
        """Set alert thresholds for a metric"""
        self.alert_thresholds[metric_name] = {
            "warning": warning_threshold,
            "critical": critical_threshold
        }
        
    def add_alert_callback(self, callback: Callable):
        """Add callback for alert notifications"""
        self.alert_callbacks.append(callback)
        
    def _check_alert_threshold(self, metric_name: str, value: float):
        """Check if metric value exceeds alert thresholds"""
        thresholds = self.alert_thresholds.get(metric_name)
        if not thresholds:
            return
            
        alert_level = None
        if thresholds.get("critical") and value >= thresholds["critical"]:
            alert_level = "critical"
        elif thresholds.get("warning") and value >= thresholds["warning"]:
            alert_level = "warning"
            
        if alert_level:
            alert_data = {
                "metric_name": metric_name,
                "value": value,
                "level": alert_level,
                "threshold": thresholds[alert_level],
                "timestamp": utc_now().isoformat()
            }
            
            for callback in self.alert_callbacks:
                try:
                    callback(alert_data)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
                    
    def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get comprehensive summary for a metric"""
        summary = {"name": metric_name, "data": {}}
        
        # Counter data
        if metric_name in self.counters:
            summary["data"]["counter"] = self.counters[metric_name]
            
        # Gauge data
        if metric_name in self.gauges:
            summary["data"]["gauge"] = self.gauges[metric_name]
            
        # Histogram statistics
        if metric_name in self.histograms and self.histograms[metric_name]:
            values = self.histograms[metric_name]
            summary["data"]["histogram"] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "p95": self.aggregator._percentile(values, 95),
                "p99": self.aggregator._percentile(values, 99)
            }
            
        # Timer statistics
        if metric_name in self.timers and self.timers[metric_name]:
            values = self.timers[metric_name]
            summary["data"]["timer"] = {
                "count": len(values),
                "total_time": sum(values),
                "avg_time": statistics.mean(values),
                "min_time": min(values),
                "max_time": max(values),
                "p95_time": self.aggregator._percentile(values, 95),
                "p99_time": self.aggregator._percentile(values, 99)
            }
            
        return summary
        
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        with self._lock:
            uptime = time.time() - self.start_time
            
            health = {
                "uptime_seconds": uptime,
                "metrics_collected": len(self.metrics),
                "counters_active": len(self.counters),
                "gauges_active": len(self.gauges),
                "histograms_active": len(self.histograms),
                "timers_active": len(self.timers),
                "last_flush": self.last_flush.isoformat(),
                "memory_usage": {
                    "metrics_mb": len(self.metrics) * 0.001,  # Rough estimate
                    "total_objects": (
                        len(self.counters) + 
                        len(self.gauges) + 
                        sum(len(h) for h in self.histograms.values()) +
                        sum(len(t) for t in self.timers.values())
                    )
                }
            }
            
            # Add latest system performance if available
            if self.performance_snapshots:
                latest_snapshot = self.performance_snapshots[-1]
                health["system_performance"] = {
                    "cpu_percent": latest_snapshot.cpu_percent,
                    "memory_percent": latest_snapshot.memory_percent,
                    "disk_usage_percent": latest_snapshot.disk_usage_percent,
                    "timestamp": latest_snapshot.timestamp.isoformat()
                }
                
            return health
            
    def flush_metrics(self, export_format: str = "json") -> Optional[str]:
        """Flush collected metrics and optionally export"""
        with self._lock:
            if export_format == "json":
                export_data = {
                    "timestamp": utc_now().isoformat(),
                    "metrics": [metric.to_dict() for metric in self.metrics],
                    "counters": dict(self.counters),
                    "gauges": dict(self.gauges),
                    "system_health": self.get_system_health()
                }
                
                # Clear metrics after export
                self.metrics.clear()
                self.last_flush = utc_now()
                
                return json.dumps(export_data, indent=2)
                
        return None
        
    def stop(self):
        """Stop background monitoring"""
        self._stop_event.set()
        if self._background_thread:
            self._background_thread.join(timeout=5)


# Global metrics collector instance
metrics_collector = MetricsCollector()


def track_execution_time(
    metric_name: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    threshold_warning: Optional[float] = None,
    threshold_critical: Optional[float] = None
):
    """
    Decorator to automatically track function execution time
    
    Args:
        metric_name: Name for the metric (defaults to function name)
        tags: Additional tags for the metric
        threshold_warning: Warning threshold in seconds
        threshold_critical: Critical threshold in seconds
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            name = metric_name or f"function.{func.__name__}.execution_time"
            
            with metrics_collector.timer(
                name,
                tags=tags,
                threshold_warning=threshold_warning,
                threshold_critical=threshold_critical
            ):
                return func(*args, **kwargs)
                
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            name = metric_name or f"function.{func.__name__}.execution_time"
            
            with metrics_collector.timer(
                name,
                tags=tags,
                threshold_warning=threshold_warning,
                threshold_critical=threshold_critical
            ):
                return await func(*args, **kwargs)
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator


def track_business_metric(
    metric_type: str,
    value: Union[int, float] = 1,
    tags: Optional[Dict[str, str]] = None
):
    """
    Decorator to track business metrics
    
    Args:
        metric_type: Type of business metric
        value: Metric value
        tags: Additional tags
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            result = func(*args, **kwargs)
            
            metric_name = f"business.{metric_type}"
            metrics_collector.record_gauge(
                metric_name,
                value,
                tags=tags,
                priority=MetricPriority.HIGH
            )
            
            return result
            
        return wrapper
    return decorator


@contextmanager
def capture_errors(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Context manager to capture and track errors"""
    try:
        yield
    except Exception as e:
        error_tags = tags or {}
        error_tags.update({
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        
        metrics_collector.increment_counter(
            f"{metric_name}.errors",
            tags=error_tags,
            priority=MetricPriority.HIGH
        )
        raise
        
        entry = MetricEntry(
            name=name,
            value=self.counters[name],
            metric_type=MetricType.COUNTER,
            tags=tags or {}
        )
        self.metrics.append(entry)
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric"""
        self.gauges[name] = value
        
        entry = MetricEntry(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            tags=tags or {}
        )
        self.metrics.append(entry)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram value"""
        if name not in self.histograms:
            self.histograms[name] = []
        
        self.histograms[name].append(value)
        
        entry = MetricEntry(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            tags=tags or {}
        )
        self.metrics.append(entry)
    
    def record_timer(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timer value"""
        if name not in self.timers:
            self.timers[name] = []
        
        self.timers[name].append(duration)
        
        entry = MetricEntry(
            name=name,
            value=duration,
            metric_type=MetricType.TIMER,
            tags=tags or {}
        )
        self.metrics.append(entry)
    
    def get_counter(self, name: str) -> int:
        """Get current counter value"""
        return self.counters.get(name, 0)
    
    def get_gauge(self, name: str) -> Optional[float]:
        """Get current gauge value"""
        return self.gauges.get(name)
    
    def get_histogram_stats(self, name: str) -> Optional[Dict[str, float]]:
        """Get histogram statistics"""
        if name not in self.histograms or not self.histograms[name]:
            return None
        
        values = self.histograms[name]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "p95": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
            "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
        }
    
    def get_timer_stats(self, name: str) -> Optional[Dict[str, float]]:
        """Get timer statistics"""
        return self.get_histogram_stats(name)  # Same statistics as histogram
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {name: self.get_histogram_stats(name) for name in self.histograms},
            "timers": {name: self.get_timer_stats(name) for name in self.timers},
            "uptime": time.time() - self.start_time,
            "total_metrics": len(self.metrics)
        }
    
    def get_metrics_by_timeframe(self, minutes: int = 5) -> List[MetricEntry]:
        """Get metrics from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics if m.timestamp >= cutoff_time]
    
    def get_metrics_by_type(self, metric_type: MetricType) -> List[MetricEntry]:
        """Get metrics by type"""
        return [m for m in self.metrics if m.metric_type == metric_type]
    
    def clear_metrics(self) -> None:
        """Clear all metrics"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.timers.clear()
        self.start_time = time.time()
    
    def export_metrics(self, format_type: str = "dict") -> Union[Dict[str, Any], str]:
        """Export metrics in specified format"""
        if format_type == "dict":
            return self.get_all_metrics()
        elif format_type == "prometheus":
            return self._export_prometheus()
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # Counters
        for name, value in self.counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")
        
        # Gauges
        for name, value in self.gauges.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        
        # Histograms (simplified)
        for name, values in self.histograms.items():
            if values:
                lines.append(f"# TYPE {name} histogram")
                lines.append(f"{name}_count {len(values)}")
                lines.append(f"{name}_sum {sum(values)}")
        
        return "\n".join(lines)


class TimerContext:
    """Context manager for timing operations"""
    
    def __init__(self, metrics_collector: MetricsCollector, name: str, tags: Optional[Dict[str, str]] = None):
        self.metrics_collector = metrics_collector
        self.name = name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics_collector.record_timer(self.name, duration, self.tags)


# Global metrics collector instance
metrics_collector = MetricsCollector()
