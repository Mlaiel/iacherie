"""Enterprise-grade metrics and monitoring system for IA Influencer Agent.
Professional observability with comprehensive business and system metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 IA Influencer Agent. Unauthorized use strictly prohibited.
"""
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import time
import threading
import asyncio
from collections import defaultdict, deque
from contextlib import contextmanager, asynccontextmanager
import statistics


class MetricType(Enum):
    """Types of metrics for categorization."""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SET = "set"


class MetricUnit(Enum):
    """Standard metric units."""    NONE = ""
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    COUNT = "count"
    PERCENT = "percent"
    RATE = "rate"
    REQUESTS_PER_SECOND = "requests_per_second"


@dataclass
class MetricDefinition:
    """Metric definition with metadata."""    name: str
    metric_type: MetricType
    description: str
    unit: MetricUnit = MetricUnit.NONE
    tags: Dict[str, str] = field(default_factory=dict)
    help_text: Optional[str] = None


@dataclass
class MetricValue:
    """Individual metric measurement."""    value: Union[int, float]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class TimingResult:
    """Result from timing measurement."""    duration_ms: float
    start_time: datetime
    end_time: datetime
    tags: Dict[str, str] = field(default_factory=dict)


class IMetricsCollector(ABC):
    """Interface for metrics collection."""    
    @abstractmethod
    def increment_counter(
        self,
        name: str,
        value: Union[int, float] = 1,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment counter metric."""        pass
    
    @abstractmethod
    def set_gauge(
        self,
        name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Set gauge metric value."""        pass
    
    @abstractmethod
    def record_timing(
        self,
        name: str,
        duration_ms: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record timing metric."""        pass
    
    @abstractmethod
    def record_histogram(
        self,
        name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record histogram value."""        pass


class InMemoryMetricsCollector(IMetricsCollector):
    """In-memory metrics collector for development and testing."""    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self._counters: Dict[str, List[MetricValue]] = defaultdict(list)
        self._gauges: Dict[str, MetricValue] = {}
        self._timings: Dict[str, List[MetricValue]] = defaultdict(list)
        self._histograms: Dict[str, List[MetricValue]] = defaultdict(list)
        self._lock = threading.RLock()
        
        # Start cleanup task
        self._cleanup_task = None
        asyncio.create_task(self._start_cleanup_task())
    
    def increment_counter(
        self,
        name: str,
        value: Union[int, float] = 1,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment counter with value."""        with self._lock:
            metric_value = MetricValue(value=value, tags=tags or {})
            self._counters[name].append(metric_value)
    
    def set_gauge(
        self,
        name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Set gauge to specific value."""        with self._lock:
            self._gauges[name] = MetricValue(value=value, tags=tags or {})
    
    def record_timing(
        self,
        name: str,
        duration_ms: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record timing measurement."""        with self._lock:
            metric_value = MetricValue(value=duration_ms, tags=tags or {})
            self._timings[name].append(metric_value)
    
    def record_histogram(
        self,
        name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record histogram value."""        with self._lock:
            metric_value = MetricValue(value=value, tags=tags or {})
            self._histograms[name].append(metric_value)
    
    def get_counter_sum(self, name: str) -> float:
        """Get total counter value."""        with self._lock:
            return sum(m.value for m in self._counters.get(name, []))
    
    def get_gauge_value(self, name: str) -> Optional[float]:
        """Get current gauge value."""        with self._lock:
            gauge = self._gauges.get(name)
            return gauge.value if gauge else None
    
    def get_timing_stats(self, name: str) -> Dict[str, float]:
        """Get timing statistics."""        with self._lock:
            values = [m.value for m in self._timings.get(name, [])]
            if not values:
                return {}
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "p95": statistics.quantiles(values, n=20)[18] if len(values) > 1 else values[0],
                "p99": statistics.quantiles(values, n=100)[98] if len(values) > 1 else values[0]
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""        with self._lock:
            return {
                "counters": {name: self.get_counter_sum(name) for name in self._counters},
                "gauges": {name: self.get_gauge_value(name) for name in self._gauges},
                "timings": {name: self.get_timing_stats(name) for name in self._timings},
                "histograms": {name: len(values) for name, values in self._histograms.items()}
            }
    
    async def _start_cleanup_task(self):
        """Start background cleanup task."""        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                self._cleanup_old_metrics()
            except asyncio.CancelledError:
                break
            except Exception:
                pass
    
    def _cleanup_old_metrics(self):
        """Remove old metrics beyond retention period."""        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)
        
        with self._lock:
            # Clean counters
            for name in list(self._counters.keys()):
                self._counters[name] = [
                    m for m in self._counters[name]
                    if m.timestamp > cutoff_time
                ]
                if not self._counters[name]:
                    del self._counters[name]
            
            # Clean timings
            for name in list(self._timings.keys()):
                self._timings[name] = [
                    m for m in self._timings[name]
                    if m.timestamp > cutoff_time
                ]
                if not self._timings[name]:
                    del self._timings[name]
            
            # Clean histograms
            for name in list(self._histograms.keys()):
                self._histograms[name] = [
                    m for m in self._histograms[name]
                    if m.timestamp > cutoff_time
                ]
                if not self._histograms[name]:
                    del self._histograms[name]


class MetricsRegistry:
    """Registry for metric definitions and collection."""    
    def __init__(self, collector: IMetricsCollector):
        self.collector = collector
        self._definitions: Dict[str, MetricDefinition] = {}
        self._lock = threading.RLock()
    
    def register_metric(self, definition: MetricDefinition) -> None:
        """Register metric definition."""        with self._lock:
            self._definitions[definition.name] = definition
    
    def register_counter(
        self,
        name: str,
        description: str,
        unit: MetricUnit = MetricUnit.COUNT,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Register counter metric."""        definition = MetricDefinition(
            name=name,
            metric_type=MetricType.COUNTER,
            description=description,
            unit=unit,
            tags=tags or {}
        )
        self.register_metric(definition)
    
    def register_gauge(
        self,
        name: str,
        description: str,
        unit: MetricUnit = MetricUnit.NONE,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Register gauge metric."""        definition = MetricDefinition(
            name=name,
            metric_type=MetricType.GAUGE,
            description=description,
            unit=unit,
            tags=tags or {}
        )
        self.register_metric(definition)
    
    def register_timer(
        self,
        name: str,
        description: str,
        unit: MetricUnit = MetricUnit.MILLISECONDS,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Register timer metric."""        definition = MetricDefinition(
            name=name,
            metric_type=MetricType.TIMER,
            description=description,
            unit=unit,
            tags=tags or {}
        )
        self.register_metric(definition)
    
    def increment(
        self,
        name: str,
        value: Union[int, float] = 1,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment counter metric."""        self.collector.increment_counter(name, value, tags)
    
    def set_gauge(
        self,
        name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Set gauge metric."""        self.collector.set_gauge(name, value, tags)
    
    def record_timing(
        self,
        name: str,
        duration_ms: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record timing metric."""        self.collector.record_timing(name, duration_ms, tags)
    
    @contextmanager
    def timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.record_timing(name, duration_ms, tags)
    
    @asynccontextmanager
    async def async_timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Async context manager for timing operations."""        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.record_timing(name, duration_ms, tags)
    
    def get_definitions(self) -> Dict[str, MetricDefinition]:
        """Get all registered metric definitions."""        with self._lock:
            return self._definitions.copy()


class BusinessMetrics:
    """Business-specific metrics for IA Influencer Agent."""    
    def __init__(self, registry: MetricsRegistry):
        self.registry = registry
        self._register_business_metrics()
    
    def _register_business_metrics(self):
        """Register all business metrics."""        # Content metrics
        self.registry.register_counter(
            "content.uploaded.total",
            "Total content uploads",
            MetricUnit.COUNT
        )
        
        self.registry.register_counter(
            "content.protected.total",
            "Total content protected",
            MetricUnit.COUNT
        )
        
        self.registry.register_gauge(
            "content.processing.active",
            "Currently processing content items",
            MetricUnit.COUNT
        )
        
        # Fingerprinting metrics
        self.registry.register_counter(
            "fingerprint.generated.total",
            "Total fingerprints generated",
            MetricUnit.COUNT
        )
        
        self.registry.register_timer(
            "fingerprint.generation.duration",
            "Fingerprint generation duration",
            MetricUnit.MILLISECONDS
        )
        
        self.registry.register_gauge(
            "fingerprint.accuracy.score",
            "Fingerprint accuracy score",
            MetricUnit.PERCENT
        )
        
        # Infringement detection
        self.registry.register_counter(
            "infringement.detected.total",
            "Total infringements detected",
            MetricUnit.COUNT
        )
        
        self.registry.register_counter(
            "infringement.resolved.total",
            "Total infringements resolved",
            MetricUnit.COUNT
        )
        
        # Revenue metrics
        self.registry.register_gauge(
            "revenue.total.amount",
            "Total revenue amount",
            MetricUnit.NONE
        )
        
        self.registry.register_counter(
            "revenue.transactions.total",
            "Total revenue transactions",
            MetricUnit.COUNT
        )
        
        # API metrics
        self.registry.register_counter(
            "api.requests.total",
            "Total API requests",
            MetricUnit.COUNT
        )
        
        self.registry.register_timer(
            "api.request.duration",
            "API request duration",
            MetricUnit.MILLISECONDS
        )
        
        self.registry.register_counter(
            "api.errors.total",
            "Total API errors",
            MetricUnit.COUNT
        )
        
        # User metrics
        self.registry.register_gauge(
            "users.active.total",
            "Total active users",
            MetricUnit.COUNT
        )
        
        self.registry.register_counter(
            "users.registered.total",
            "Total registered users",
            MetricUnit.COUNT
        )
    
    def record_content_upload(
        self,
        content_type: str,
        file_size_mb: float,
        user_id: str
    ):
        """Record content upload metrics."""        tags = {
            "content_type": content_type,
            "user_id": user_id
        }
        
        self.registry.increment("content.uploaded.total", tags=tags)
        self.registry.record_timing("content.upload.duration", file_size_mb * 10, tags=tags)
    
    def record_fingerprint_generation(
        self,
        content_type: str,
        duration_ms: float,
        accuracy_score: float
    ):
        """Record fingerprint generation metrics."""        tags = {"content_type": content_type}
        
        self.registry.increment("fingerprint.generated.total", tags=tags)
        self.registry.record_timing("fingerprint.generation.duration", duration_ms, tags=tags)
        self.registry.set_gauge("fingerprint.accuracy.score", accuracy_score * 100, tags=tags)
    
    def record_infringement_detection(
        self,
        platform: str,
        similarity_score: float,
        content_type: str
    ):
        """Record infringement detection metrics."""        tags = {
            "platform": platform,
            "content_type": content_type
        }
        
        self.registry.increment("infringement.detected.total", tags=tags)
        self.registry.set_gauge("infringement.similarity.score", similarity_score * 100, tags=tags)
    
    def record_revenue_transaction(
        self,
        amount: float,
        currency: str,
        platform: str,
        revenue_type: str
    ):
        """Record revenue transaction metrics."""        tags = {
            "currency": currency,
            "platform": platform,
            "revenue_type": revenue_type
        }
        
        self.registry.increment("revenue.transactions.total", tags=tags)
        # Note: In production, you'd want to aggregate revenue securely
    
    def record_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float
    ):
        """Record API request metrics."""        tags = {
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code)
        }
        
        self.registry.increment("api.requests.total", tags=tags)
        self.registry.record_timing("api.request.duration", duration_ms, tags=tags)
        
        if status_code >= 400:
            self.registry.increment("api.errors.total", tags=tags)


def timing_decorator(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator for automatic timing measurement."""    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            async with get_metrics_registry().async_timer(metric_name, tags):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            with get_metrics_registry().timer(metric_name, tags):
                return func(*args, **kwargs)
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def counter_decorator(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator for automatic counter increment."""    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                get_metrics_registry().increment(metric_name, tags=tags)
                return result
            except Exception:
                error_tags = {**(tags or {}), "status": "error"}
                get_metrics_registry().increment(metric_name, tags=error_tags)
                raise
        
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                get_metrics_registry().increment(metric_name, tags=tags)
                return result
            except Exception:
                error_tags = {**(tags or {}), "status": "error"}
                get_metrics_registry().increment(metric_name, tags=error_tags)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global metrics instances
_collector = InMemoryMetricsCollector()
_registry = MetricsRegistry(_collector)
_business_metrics = BusinessMetrics(_registry)


def get_metrics_collector() -> IMetricsCollector:
    """Get global metrics collector."""    return _collector


def get_metrics_registry() -> MetricsRegistry:
    """Get global metrics registry."""    return _registry


def get_business_metrics() -> BusinessMetrics:
    """Get business metrics instance."""    return _business_metrics
