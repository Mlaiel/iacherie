"""
Performance Tracker Module
==========================

Enterprise-grade performance monitoring and tracking for distribution system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2024 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import statistics
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import psutil
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of performance metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

class AlertLevel(Enum):
    """Performance alert levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "unit": self.unit
        }

@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    metric_name: str
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    comparison: str = "greater"  # greater, less, equal
    enabled: bool = True

@dataclass
class SystemMetrics:
    """System-level performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    open_file_descriptors: int
    process_count: int
    load_average: List[float]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ApplicationMetrics:
    """Application-level performance metrics"""
    active_connections: int
    requests_per_second: float
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    error_rate: float
    cache_hit_rate: float
    database_connections: int
    queue_size: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class PerformanceTracker:
    """Enterprise performance tracking system"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.redis_client = None
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        self.alert_callbacks: List[Callable] = []
        self.is_running = False
        self._monitor_task = None
        
        # Time series data for different intervals
        self.minute_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=60))
        self.hour_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=24))
        self.day_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=30))
        
        # Performance counters
        self.counters: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        
        # Request tracking
        self.request_times: deque = deque(maxlen=1000)
        self.error_count: int = 0
        self.total_requests: int = 0
    
    async def start(self):
        """Start performance monitoring"""
        if self.is_running:
            return
        
        # Connect to Redis if URL provided
        if self.redis_url:
            try:
                # Try to import aioredis if available
                try:
                    import aioredis
                    self.redis_client = aioredis.from_url(self.redis_url)
                    await self.redis_client.ping()
                    logger.info("Connected to Redis for metrics storage")
                except ImportError:
                    logger.warning("aioredis not available, Redis storage disabled")
                    self.redis_client = None
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self.redis_client = None
        
        self.is_running = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Performance tracking started")
    
    async def stop(self):
        """Stop performance monitoring"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Performance tracking stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect application metrics
                await self._collect_application_metrics()
                
                # Check thresholds
                await self._check_thresholds()
                
                # Aggregate metrics
                await self._aggregate_metrics()
                
                # Wait for next collection
                await asyncio.sleep(10)  # Collect every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self):
        """Collect system-level performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            await self.record_metric("system.cpu.percent", cpu_percent, MetricType.GAUGE, unit="%")
            
            # Memory metrics
            memory = psutil.virtual_memory()
            await self.record_metric("system.memory.percent", memory.percent, MetricType.GAUGE, unit="%")
            await self.record_metric("system.memory.available", memory.available, MetricType.GAUGE, unit="bytes")
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            await self.record_metric("system.disk.percent", disk_percent, MetricType.GAUGE, unit="%")
            
            # Network metrics
            network = psutil.net_io_counters()
            await self.record_metric("system.network.bytes_sent", network.bytes_sent, MetricType.COUNTER, unit="bytes")
            await self.record_metric("system.network.bytes_recv", network.bytes_recv, MetricType.COUNTER, unit="bytes")
            
            # Process metrics
            process = psutil.Process()
            await self.record_metric("system.process.memory_rss", process.memory_info().rss, MetricType.GAUGE, unit="bytes")
            await self.record_metric("system.process.cpu_percent", process.cpu_percent(), MetricType.GAUGE, unit="%")
            
            # File descriptors
            try:
                fd_count = process.num_fds()
                await self.record_metric("system.process.file_descriptors", fd_count, MetricType.GAUGE)
            except AttributeError:
                # Windows doesn't have num_fds
                pass
            
            # Load average (Unix only)
            try:
                load_avg = psutil.getloadavg()
                await self.record_metric("system.load.1min", load_avg[0], MetricType.GAUGE)
                await self.record_metric("system.load.5min", load_avg[1], MetricType.GAUGE)
                await self.record_metric("system.load.15min", load_avg[2], MetricType.GAUGE)
            except AttributeError:
                # Windows doesn't have load average
                pass
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    async def _collect_application_metrics(self):
        """Collect application-level performance metrics"""
        try:
            # Request rate (requests per second)
            current_time = time.time()
            recent_requests = len([t for t in self.request_times if current_time - t < 60])
            rps = recent_requests / 60.0
            await self.record_metric("app.requests_per_second", rps, MetricType.GAUGE, unit="req/s")
            
            # Response time metrics
            if self.request_times:
                recent_times = [t for t in self.timers.get('response_time', []) if current_time - t < 300]
                if recent_times:
                    avg_response = statistics.mean(recent_times)
                    p95_response = statistics.quantiles(recent_times, n=20)[18] if len(recent_times) > 5 else avg_response
                    p99_response = statistics.quantiles(recent_times, n=100)[98] if len(recent_times) > 10 else avg_response
                    
                    await self.record_metric("app.response_time.avg", avg_response, MetricType.GAUGE, unit="ms")
                    await self.record_metric("app.response_time.p95", p95_response, MetricType.GAUGE, unit="ms")
                    await self.record_metric("app.response_time.p99", p99_response, MetricType.GAUGE, unit="ms")
            
            # Error rate
            if self.total_requests > 0:
                error_rate = (self.error_count / self.total_requests) * 100
                await self.record_metric("app.error_rate", error_rate, MetricType.GAUGE, unit="%")
            
            # Queue sizes (if available)
            for queue_name, size in self.counters.items():
                if queue_name.startswith('queue.'):
                    await self.record_metric(f"app.{queue_name}.size", size, MetricType.GAUGE)
            
        except Exception as e:
            logger.error(f"Failed to collect application metrics: {e}")
    
    async def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        tags: Optional[Dict[str, str]] = None,
        unit: str = ""
    ):
        """Record a performance metric"""
        try:
            metric = PerformanceMetric(
                name=name,
                value=value,
                metric_type=metric_type,
                tags=tags or {},
                unit=unit
            )
            
            # Add to buffer
            self.metrics_buffer[name].append(metric)
            
            # Store in Redis if available
            if self.redis_client:
                await self._store_metric_in_redis(metric)
            
            # Update time series data
            self._update_time_series(name, value)
            
        except Exception as e:
            logger.error(f"Failed to record metric {name}: {e}")
    
    async def _store_metric_in_redis(self, metric: PerformanceMetric):
        """Store metric in Redis"""
        try:
            key = f"metrics:{metric.name}:{int(metric.timestamp.timestamp())}"
            await self.redis_client.setex(key, 86400, metric.value)  # 24 hour TTL
        except Exception as e:
            logger.error(f"Failed to store metric in Redis: {e}")
    
    def _update_time_series(self, name: str, value: float):
        """Update time series data"""
        current_minute = int(time.time() // 60)
        
        # Update minute-level data
        if not self.minute_metrics[name] or self.minute_metrics[name][-1][0] != current_minute:
            self.minute_metrics[name].append((current_minute, value))
        else:
            # Update current minute with latest value
            self.minute_metrics[name][-1] = (current_minute, value)
    
    async def _aggregate_metrics(self):
        """Aggregate metrics for different time intervals"""
        try:
            current_time = int(time.time())
            current_hour = current_time // 3600
            current_day = current_time // 86400
            
            # Aggregate hourly metrics
            for metric_name, minute_data in self.minute_metrics.items():
                if len(minute_data) >= 60:  # At least 1 hour of data
                    last_hour_data = [v for t, v in minute_data if t >= (current_time // 60) - 60]
                    if last_hour_data:
                        hour_avg = statistics.mean(last_hour_data)
                        if not self.hour_metrics[metric_name] or self.hour_metrics[metric_name][-1][0] != current_hour:
                            self.hour_metrics[metric_name].append((current_hour, hour_avg))
            
            # Aggregate daily metrics
            for metric_name, hour_data in self.hour_metrics.items():
                if len(hour_data) >= 24:  # At least 1 day of data
                    last_day_data = [v for t, v in hour_data if t >= current_hour - 24]
                    if last_day_data:
                        day_avg = statistics.mean(last_day_data)
                        if not self.day_metrics[metric_name] or self.day_metrics[metric_name][-1][0] != current_day:
                            self.day_metrics[metric_name].append((current_day, day_avg))
        
        except Exception as e:
            logger.error(f"Failed to aggregate metrics: {e}")
    
    async def _check_thresholds(self):
        """Check performance thresholds and trigger alerts"""
        try:
            for metric_name, threshold in self.thresholds.items():
                if not threshold.enabled:
                    continue
                
                if metric_name in self.metrics_buffer and self.metrics_buffer[metric_name]:
                    latest_metric = self.metrics_buffer[metric_name][-1]
                    value = latest_metric.value
                    
                    alert_level = None
                    
                    # Check critical threshold
                    if threshold.critical_threshold is not None:
                        if self._check_threshold_condition(value, threshold.critical_threshold, threshold.comparison):
                            alert_level = AlertLevel.CRITICAL
                    
                    # Check warning threshold (if not already critical)
                    if alert_level != AlertLevel.CRITICAL and threshold.warning_threshold is not None:
                        if self._check_threshold_condition(value, threshold.warning_threshold, threshold.comparison):
                            alert_level = AlertLevel.WARNING
                    
                    # Trigger alert if threshold exceeded
                    if alert_level:
                        await self._trigger_alert(metric_name, value, alert_level, threshold)
        
        except Exception as e:
            logger.error(f"Failed to check thresholds: {e}")
    
    def _check_threshold_condition(self, value: float, threshold: float, comparison: str) -> bool:
        """Check if value meets threshold condition"""
        if comparison == "greater":
            return value > threshold
        elif comparison == "less":
            return value < threshold
        elif comparison == "equal":
            return abs(value - threshold) < 0.01
        return False
    
    async def _trigger_alert(self, metric_name: str, value: float, level: AlertLevel, threshold: PerformanceThreshold):
        """Trigger performance alert"""
        try:
            alert_data = {
                "metric_name": metric_name,
                "current_value": value,
                "threshold_value": threshold.critical_threshold if level == AlertLevel.CRITICAL else threshold.warning_threshold,
                "level": level.value,
                "comparison": threshold.comparison,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.warning(f"Performance alert: {metric_name} = {value} ({level.value})")
            
            # Call registered alert callbacks
            for callback in self.alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert_data)
                    else:
                        callback(alert_data)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
        
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    def add_threshold(self, threshold: PerformanceThreshold):
        """Add performance threshold"""
        self.thresholds[threshold.metric_name] = threshold
    
    def add_alert_callback(self, callback: Callable):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    async def track_request(self, duration_ms: float, success: bool = True):
        """Track HTTP request performance"""
        current_time = time.time()
        self.request_times.append(current_time)
        self.timers['response_time'].append(duration_ms)
        self.total_requests += 1
        
        if not success:
            self.error_count += 1
        
        # Clean old timer data
        cutoff_time = current_time - 300  # Keep last 5 minutes
        self.timers['response_time'] = [t for t in self.timers['response_time'] if t > cutoff_time]
    
    def increment_counter(self, name: str, value: float = 1.0):
        """Increment a counter metric"""
        self.counters[name] += value
    
    def set_gauge(self, name: str, value: float):
        """Set a gauge metric value"""
        self.counters[name] = value
    
    async def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for specified time period"""
        try:
            summary = {
                "system_metrics": {},
                "application_metrics": {},
                "custom_metrics": {},
                "time_period_hours": hours
            }
            
            # Get recent metrics from buffer
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            for metric_name, metrics in self.metrics_buffer.items():
                recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
                
                if recent_metrics:
                    values = [m.value for m in recent_metrics]
                    metric_summary = {
                        "count": len(values),
                        "avg": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "latest": values[-1],
                        "unit": recent_metrics[-1].unit
                    }
                    
                    if len(values) > 1:
                        metric_summary["std_dev"] = statistics.stdev(values)
                    
                    # Categorize metrics
                    if metric_name.startswith("system."):
                        summary["system_metrics"][metric_name] = metric_summary
                    elif metric_name.startswith("app."):
                        summary["application_metrics"][metric_name] = metric_summary
                    else:
                        summary["custom_metrics"][metric_name] = metric_summary
            
            return summary
        
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            report = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "monitoring_duration_minutes": len(self.minute_metrics.get("system.cpu.percent", [])),
                "summary": await self.get_metrics_summary(hours=24),
                "thresholds": {name: {
                    "warning": t.warning_threshold,
                    "critical": t.critical_threshold,
                    "comparison": t.comparison,
                    "enabled": t.enabled
                } for name, t in self.thresholds.items()},
                "recent_performance": {
                    "requests_per_second": self.counters.get("app.requests_per_second", 0),
                    "error_rate": (self.error_count / max(self.total_requests, 1)) * 100,
                    "total_requests": self.total_requests,
                    "total_errors": self.error_count
                }
            }
            
            return report
        
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {}

# Context manager for timing operations
class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, tracker: PerformanceTracker, metric_name: str):
        self.tracker = tracker
        self.metric_name = metric_name
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (time.time() - self.start_time) * 1000  # Convert to milliseconds
            await self.tracker.record_metric(
                self.metric_name,
                duration,
                MetricType.TIMER,
                unit="ms"
            )
            
            # Track as request if it's an HTTP operation
            if "request" in self.metric_name.lower() or "api" in self.metric_name.lower():
                await self.tracker.track_request(duration, exc_type is None)

# Decorator for tracking function performance
def track_performance(tracker: PerformanceTracker, metric_name: Optional[str] = None):
    """Decorator to track function performance"""
    def decorator(func):
        name = metric_name or f"function.{func.__name__}.duration"
        
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                async with PerformanceTimer(tracker, name):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    asyncio.create_task(tracker.record_metric(name, duration, MetricType.TIMER, unit="ms"))
                    return result
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    asyncio.create_task(tracker.record_metric(f"{name}.error", duration, MetricType.TIMER, unit="ms"))
                    raise
            return sync_wrapper
    return decorator

# Export classes and functions
__all__ = [
    "MetricType",
    "AlertLevel",
    "PerformanceMetric",
    "PerformanceThreshold",
    "SystemMetrics",
    "ApplicationMetrics",
    "PerformanceTracker",
    "PerformanceTimer",
    "track_performance"
]