"""Performance Monitor - Integration Performance Tracking System
============================================================

Advanced performance monitoring system for tracking integration performance,
identifying bottlenecks, and optimizing system efficiency.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import psutil
import gc
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import json
import statistics
from contextlib import asynccontextmanager
import threading
import weakref

import aioredis
import aiofiles
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Performance metric types."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    QUEUE_SIZE = "queue_size"
    CONNECTION_POOL = "connection_pool"
    CACHE_HIT_RATE = "cache_hit_rate"

class AlertLevel(Enum):
    """Performance alert levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    integration_name: Optional[str] = None
    service_name: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    emergency_threshold: Optional[float] = None
    window_minutes: int = 5
    min_samples: int = 10
    enabled: bool = True

@dataclass
class PerformanceAlert:
    """Performance alert."""
    alert_id: str
    metric_name: str
    level: AlertLevel
    current_value: float
    threshold_value: float
    integration_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration: Optional[timedelta] = None
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrationProfile:
    """Performance profile for an integration."""
    integration_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_rps: float = 0.0
    error_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    # Resource usage
    avg_memory_mb: float = 0.0
    avg_cpu_percent: float = 0.0
    peak_memory_mb: float = 0.0
    peak_cpu_percent: float = 0.0

class PerformanceCollector:
    """Collects and aggregates performance metrics."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.last_cleanup = datetime.utcnow()
        self.lock = threading.RLock()

    def add_metric(self, metric: PerformanceMetric) -> None:
        """Add a metric to the collector."""
        with self.lock:
            key = f"{metric.integration_name or 'system'}:{metric.name}"
            self.metrics[key].append(metric)
            
            # Periodic cleanup
            now = datetime.utcnow()
            if (now - self.last_cleanup).total_seconds() > 300:  # 5 minutes
                self._cleanup_old_metrics()
                self.last_cleanup = now

    def get_metrics(self, metric_name: str, integration_name: Optional[str] = None) -> List[PerformanceMetric]:
        """Get metrics for a specific metric name."""
        with self.lock:
            key = f"{integration_name or 'system'}:{metric_name}"
            return list(self.metrics.get(key, []))

    def get_latest_value(self, metric_name: str, integration_name: Optional[str] = None) -> Optional[float]:
        """Get the latest value for a metric."""
        metrics = self.get_metrics(metric_name, integration_name)
        return metrics[-1].value if metrics else None

    def calculate_statistics(
        self, 
        metric_name: str, 
        integration_name: Optional[str] = None,
        window_minutes: int = 5
    ) -> Dict[str, float]:
        """Calculate statistics for a metric."""
        metrics = self.get_metrics(metric_name, integration_name)
        
        # Filter by time window
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {}
            
        values = [m.value for m in recent_metrics]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stddev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'p95': self._percentile(values, 95),
            'p99': self._percentile(values, 99)
        }

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]

    def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics beyond retention period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)  # 24 hour retention
        
        for key, metric_queue in self.metrics.items():
            # Remove old metrics
            while metric_queue and metric_queue[0].timestamp < cutoff_time:
                metric_queue.popleft()

class PerformanceMonitor:
    """Comprehensive performance monitoring system."""
    
    def __init__(
        self,
        enable_prometheus: bool = True,
        enable_system_metrics: bool = True,
        collection_interval: int = 30,
        storage_backend: str = "memory"  # memory, redis, file
    ):
        self.enable_prometheus = enable_prometheus
        self.enable_system_metrics = enable_system_metrics
        self.collection_interval = collection_interval
        self.storage_backend = storage_backend
        
        # Metric collection
        self.collector = PerformanceCollector()
        self.integration_profiles: Dict[str, IntegrationProfile] = {}
        
        # Thresholds and alerting
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_callbacks: List[Callable] = []
        
        # Background tasks
        self.monitor_task = None
        self.system_monitor_task = None
        self.alert_task = None
        
        # Prometheus metrics (if enabled)
        if self.enable_prometheus:
            self.prometheus_registry = CollectorRegistry()
            self._setup_prometheus_metrics()
            
        # Redis client for distributed storage
        self.redis_client = None
        
        # Performance tracking
        self.active_traces: Dict[str, Dict[str, Any]] = {}
        self.trace_lock = threading.RLock()
        
        logger.info("Performance Monitor initialized")

    def _setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics."""
        self.prom_request_duration = Histogram(
            'integration_request_duration_seconds',
            'Request duration in seconds',
            ['integration', 'method', 'status'],
            registry=self.prometheus_registry
        )
        
        self.prom_request_total = Counter(
            'integration_requests_total',
            'Total number of requests',
            ['integration', 'method', 'status'],
            registry=self.prometheus_registry
        )
        
        self.prom_error_rate = Gauge(
            'integration_error_rate',
            'Current error rate',
            ['integration'],
            registry=self.prometheus_registry
        )
        
        self.prom_memory_usage = Gauge(
            'integration_memory_usage_bytes',
            'Memory usage in bytes',
            ['integration'],
            registry=self.prometheus_registry
        )
        
        self.prom_cpu_usage = Gauge(
            'integration_cpu_usage_percent',
            'CPU usage percentage',
            ['integration'],
            registry=self.prometheus_registry
        )

    async def initialize(self, redis_url: Optional[str] = None) -> None:
        """Initialize performance monitoring."""
        try:
            # Initialize Redis if using Redis backend
            if self.storage_backend == "redis" and redis_url:
                self.redis_client = await aioredis.from_url(redis_url)
                await self.redis_client.ping()
                logger.info("Redis storage backend initialized")
                
            # Setup default thresholds
            await self._setup_default_thresholds()
            
            # Start background monitoring tasks
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            
            if self.enable_system_metrics:
                self.system_monitor_task = asyncio.create_task(self._system_monitor_loop())
                
            self.alert_task = asyncio.create_task(self._alert_loop())
            
            logger.info("Performance Monitor initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance monitor: {e}")
            raise

    async def _setup_default_thresholds(self) -> None:
        """Setup default performance thresholds."""
        default_thresholds = [
            PerformanceThreshold("latency_ms", 1000, 5000, 10000),
            PerformanceThreshold("error_rate", 0.05, 0.10, 0.25),
            PerformanceThreshold("memory_usage_mb", 500, 1000, 2000),
            PerformanceThreshold("cpu_usage_percent", 70, 85, 95),
            PerformanceThreshold("throughput_rps", 10, 5, 1)  # Low throughput alert
        ]
        
        for threshold in default_thresholds:
            self.thresholds[threshold.metric_name] = threshold

    @asynccontextmanager
    async def trace_performance(
        self,
        operation_name: str,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """Context manager for tracing operation performance."""
        trace_id = f"{operation_name}_{int(time.time() * 1000)}"
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Initialize trace
        with self.trace_lock:
            self.active_traces[trace_id] = {
                'operation_name': operation_name,
                'integration_name': integration_name,
                'start_time': start_time,
                'start_memory': start_memory,
                'tags': tags or {}
            }
        
        try:
            yield trace_id
        except Exception as e:
            # Record error
            await self.record_error(operation_name, str(e), integration_name)
            raise
        finally:
            # Calculate metrics
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            duration_ms = (end_time - start_time) * 1000
            memory_delta = end_memory - start_memory
            
            # Record performance metrics
            await self.record_latency(operation_name, duration_ms, integration_name, tags)
            
            if memory_delta > 0:
                await self.record_memory_usage(operation_name, memory_delta, integration_name, tags)
                
            # Update Prometheus metrics
            if self.enable_prometheus:
                labels = {
                    'integration': integration_name or 'unknown',
                    'method': operation_name,
                    'status': 'success'
                }
                self.prom_request_duration.labels(**labels).observe(duration_ms / 1000)
                self.prom_request_total.labels(**labels).inc()
                
            # Clean up trace
            with self.trace_lock:
                self.active_traces.pop(trace_id, None)

    async def record_latency(
        self,
        operation_name: str,
        latency_ms: float,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record latency metric."""
        metric = PerformanceMetric(
            name=f"{operation_name}_latency_ms",
            metric_type=MetricType.LATENCY,
            value=latency_ms,
            integration_name=integration_name,
            tags=tags or {}
        )
        
        await self._store_metric(metric)

    async def record_throughput(
        self,
        operation_name: str,
        requests_per_second: float,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record throughput metric."""
        metric = PerformanceMetric(
            name=f"{operation_name}_throughput_rps",
            metric_type=MetricType.THROUGHPUT,
            value=requests_per_second,
            integration_name=integration_name,
            tags=tags or {}
        )
        
        await self._store_metric(metric)

    async def record_error_rate(
        self,
        operation_name: str,
        error_rate: float,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record error rate metric."""
        metric = PerformanceMetric(
            name=f"{operation_name}_error_rate",
            metric_type=MetricType.ERROR_RATE,
            value=error_rate,
            integration_name=integration_name,
            tags=tags or {}
        )
        
        await self._store_metric(metric)
        
        # Update Prometheus
        if self.enable_prometheus and integration_name:
            self.prom_error_rate.labels(integration=integration_name).set(error_rate)

    async def record_memory_usage(
        self,
        operation_name: str,
        memory_mb: float,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record memory usage metric."""
        metric = PerformanceMetric(
            name=f"{operation_name}_memory_mb",
            metric_type=MetricType.MEMORY_USAGE,
            value=memory_mb,
            integration_name=integration_name,
            tags=tags or {}
        )
        
        await self._store_metric(metric)
        
        # Update Prometheus
        if self.enable_prometheus and integration_name:
            self.prom_memory_usage.labels(integration=integration_name).set(memory_mb * 1024 * 1024)

    async def record_error(
        self,
        operation_name: str,
        error_message: str,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record an error occurrence."""
        # Update Prometheus error counter
        if self.enable_prometheus:
            labels = {
                'integration': integration_name or 'unknown',
                'method': operation_name,
                'status': 'error'
            }
            self.prom_request_total.labels(**labels).inc()
            
        # Store error metric
        error_tags = (tags or {}).copy()
        error_tags['error_message'] = error_message
        
        metric = PerformanceMetric(
            name=f"{operation_name}_error",
            metric_type=MetricType.ERROR_RATE,
            value=1.0,
            integration_name=integration_name,
            tags=error_tags
        )
        
        await self._store_metric(metric)

    async def _store_metric(self, metric: PerformanceMetric) -> None:
        """Store metric using configured backend."""
        # Always store in memory collector
        self.collector.add_metric(metric)
        
        # Store in external backend if configured
        if self.storage_backend == "redis" and self.redis_client:
            await self._store_metric_redis(metric)
        elif self.storage_backend == "file":
            await self._store_metric_file(metric)
            
        # Update integration profile
        await self._update_integration_profile(metric)

    async def _store_metric_redis(self, metric: PerformanceMetric) -> None:
        """Store metric in Redis."""
        try:
            key = f"performance:{metric.integration_name or 'system'}:{metric.name}"
            data = {
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'metric_type': metric.metric_type.value,
                'tags': metric.tags,
                'metadata': metric.metadata
            }
            
            # Store as JSON with TTL
            await self.redis_client.setex(
                f"{key}:{int(metric.timestamp.timestamp())}",
                24 * 3600,  # 24 hours TTL
                json.dumps(data)
            )
            
            # Add to time series
            await self.redis_client.zadd(
                f"{key}:timeseries",
                {json.dumps(data): metric.timestamp.timestamp()}
            )
            
            # Trim old entries (keep last 1000)
            await self.redis_client.zremrangebyrank(f"{key}:timeseries", 0, -1001)
            
        except Exception as e:
            logger.error(f"Failed to store metric in Redis: {e}")

    async def _store_metric_file(self, metric: PerformanceMetric) -> None:
        """Store metric in file."""
        try:
            date_str = metric.timestamp.strftime('%Y-%m-%d')
            file_path = f"/home/runner/work/Ainflue/Ainflue/logs/performance/metrics_{date_str}.jsonl"
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            metric_data = {
                'name': metric.name,
                'metric_type': metric.metric_type.value,
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'integration_name': metric.integration_name,
                'tags': metric.tags,
                'metadata': metric.metadata
            }
            
            async with aiofiles.open(file_path, mode='a') as f:
                await f.write(json.dumps(metric_data) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to store metric to file: {e}")

    async def _update_integration_profile(self, metric: PerformanceMetric) -> None:
        """Update integration performance profile."""
        if not metric.integration_name:
            return
            
        profile = self.integration_profiles.get(
            metric.integration_name,
            IntegrationProfile(integration_name=metric.integration_name)
        )
        
        # Update based on metric type
        if metric.metric_type == MetricType.LATENCY:
            # Recalculate latency statistics
            recent_metrics = self.collector.get_metrics(metric.name, metric.integration_name)
            if recent_metrics:
                values = [m.value for m in recent_metrics[-100:]]  # Last 100 samples
                profile.avg_latency_ms = statistics.mean(values)
                profile.p95_latency_ms = self.collector._percentile(values, 95)
                profile.p99_latency_ms = self.collector._percentile(values, 99)
                
        elif metric.metric_type == MetricType.MEMORY_USAGE:
            profile.avg_memory_mb = metric.value
            profile.peak_memory_mb = max(profile.peak_memory_mb, metric.value)
            
        elif metric.metric_type == MetricType.CPU_USAGE:
            profile.avg_cpu_percent = metric.value
            profile.peak_cpu_percent = max(profile.peak_cpu_percent, metric.value)
            
        elif metric.metric_type == MetricType.ERROR_RATE:
            profile.error_rate = metric.value
            
        profile.last_updated = datetime.utcnow()
        self.integration_profiles[metric.integration_name] = profile

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while True:
            try:
                await asyncio.sleep(self.collection_interval)
                
                # Collect integration-specific metrics
                await self._collect_integration_metrics()
                
                # Run garbage collection periodically
                if self.collection_interval % 300 == 0:  # Every 5 minutes
                    gc.collect()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

    async def _system_monitor_loop(self) -> None:
        """System metrics monitoring loop."""
        while True:
            try:
                await asyncio.sleep(30)  # Every 30 seconds
                
                # Collect system metrics
                await self._collect_system_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system monitoring loop: {e}")

    async def _collect_system_metrics(self) -> None:
        """Collect system-level performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_metric("system_cpu_percent", cpu_percent, MetricType.CPU_USAGE)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.used / 1024 / 1024
            await self.record_metric("system_memory_mb", memory_mb, MetricType.MEMORY_USAGE)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                await self.record_metric("system_disk_read_mb", disk_io.read_bytes / 1024 / 1024, MetricType.DISK_IO)
                await self.record_metric("system_disk_write_mb", disk_io.write_bytes / 1024 / 1024, MetricType.DISK_IO)
                
            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io:
                await self.record_metric("system_network_sent_mb", network_io.bytes_sent / 1024 / 1024, MetricType.NETWORK_IO)
                await self.record_metric("system_network_recv_mb", network_io.bytes_recv / 1024 / 1024, MetricType.NETWORK_IO)
                
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    async def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a custom metric."""
        metric = PerformanceMetric(
            name=name,
            metric_type=metric_type,
            value=value,
            integration_name=integration_name,
            tags=tags or {}
        )
        
        await self._store_metric(metric)

    async def _collect_integration_metrics(self) -> None:
        """Collect metrics for all active integrations."""
        for integration_name, profile in self.integration_profiles.items():
            try:
                # Calculate derived metrics
                
                # Throughput (requests per second)
                recent_requests = len(self.collector.get_metrics(
                    f"*_latency_ms", integration_name
                ))
                
                if recent_requests > 0:
                    time_window = 60  # 1 minute
                    throughput = recent_requests / time_window
                    await self.record_throughput("requests", throughput, integration_name)
                    
                # Error rate calculation
                error_metrics = self.collector.get_metrics(f"*_error", integration_name)
                total_metrics = len(self.collector.get_metrics(f"*", integration_name))
                
                if total_metrics > 0:
                    error_rate = len(error_metrics) / total_metrics
                    await self.record_error_rate("requests", error_rate, integration_name)
                    
            except Exception as e:
                logger.error(f"Error collecting metrics for {integration_name}: {e}")

    async def _alert_loop(self) -> None:
        """Alert monitoring loop."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._check_thresholds()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert loop: {e}")

    async def _check_thresholds(self) -> None:
        """Check performance thresholds and generate alerts."""
        for threshold_name, threshold in self.thresholds.items():
            if not threshold.enabled:
                continue
                
            try:
                # Check threshold for each integration
                for integration_name in self.integration_profiles.keys():
                    await self._check_integration_threshold(threshold, integration_name)
                    
                # Check system-level thresholds
                await self._check_integration_threshold(threshold, None)
                
            except Exception as e:
                logger.error(f"Error checking threshold {threshold_name}: {e}")

    async def _check_integration_threshold(
        self,
        threshold: PerformanceThreshold,
        integration_name: Optional[str]
    ) -> None:
        """Check threshold for specific integration."""
        stats = self.collector.calculate_statistics(
            threshold.metric_name,
            integration_name,
            threshold.window_minutes
        )
        
        if not stats or stats['count'] < threshold.min_samples:
            return
            
        current_value = stats['mean']
        alert_key = f"{integration_name or 'system'}:{threshold.metric_name}"
        
        # Determine alert level
        alert_level = None
        threshold_value = None
        
        if (threshold.emergency_threshold and 
            current_value >= threshold.emergency_threshold):
            alert_level = AlertLevel.EMERGENCY
            threshold_value = threshold.emergency_threshold
        elif current_value >= threshold.critical_threshold:
            alert_level = AlertLevel.CRITICAL
            threshold_value = threshold.critical_threshold
        elif current_value >= threshold.warning_threshold:
            alert_level = AlertLevel.WARNING
            threshold_value = threshold.warning_threshold
            
        # Handle alert state
        if alert_level:
            await self._handle_alert(
                alert_key, threshold.metric_name, alert_level,
                current_value, threshold_value, integration_name
            )
        else:
            # Clear existing alert if value is now within threshold
            await self._clear_alert(alert_key)

    async def _handle_alert(
        self,
        alert_key: str,
        metric_name: str,
        level: AlertLevel,
        current_value: float,
        threshold_value: float,
        integration_name: Optional[str]
    ) -> None:
        """Handle performance alert."""
        existing_alert = self.active_alerts.get(alert_key)
        
        if existing_alert:
            # Update existing alert
            existing_alert.current_value = current_value
            existing_alert.level = level
            existing_alert.duration = datetime.utcnow() - existing_alert.timestamp
        else:
            # Create new alert
            alert = PerformanceAlert(
                alert_id=alert_key,
                metric_name=metric_name,
                level=level,
                current_value=current_value,
                threshold_value=threshold_value,
                integration_name=integration_name,
                message=f"{metric_name} is {current_value:.2f}, exceeding {level.value} threshold of {threshold_value:.2f}"
            )
            
            self.active_alerts[alert_key] = alert
            
            # Notify alert callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
                    
            logger.warning(f"Performance alert: {alert.message}")

    async def _clear_alert(self, alert_key: str) -> None:
        """Clear performance alert."""
        if alert_key in self.active_alerts:
            alert = self.active_alerts.pop(alert_key)
            logger.info(f"Performance alert cleared: {alert.metric_name}")

    def add_alert_callback(self, callback: Callable) -> None:
        """Add alert notification callback."""
        self.alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: Callable) -> None:
        """Remove alert notification callback."""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)

    def set_threshold(self, threshold: PerformanceThreshold) -> None:
        """Set performance threshold."""
        self.thresholds[threshold.metric_name] = threshold

    def get_integration_profile(self, integration_name: str) -> Optional[IntegrationProfile]:
        """Get performance profile for integration."""
        return self.integration_profiles.get(integration_name)

    def get_all_profiles(self) -> Dict[str, IntegrationProfile]:
        """Get all integration profiles."""
        return self.integration_profiles.copy()

    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())

    async def get_metrics_summary(self, integration_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'integration_name': integration_name,
            'profiles': {},
            'current_metrics': {},
            'active_alerts': len(self.active_alerts),
            'system_health': 'healthy'
        }
        
        if integration_name:
            profile = self.integration_profiles.get(integration_name)
            if profile:
                summary['profiles'][integration_name] = asdict(profile)
        else:
            summary['profiles'] = {k: asdict(v) for k, v in self.integration_profiles.items()}
            
        # Get current metric values
        for metric_name in ['latency_ms', 'throughput_rps', 'error_rate', 'memory_mb', 'cpu_percent']:
            current_value = self.collector.get_latest_value(metric_name, integration_name)
            if current_value is not None:
                summary['current_metrics'][metric_name] = current_value
                
        # Determine system health
        critical_alerts = [a for a in self.active_alerts.values() 
                          if a.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]]
        if critical_alerts:
            summary['system_health'] = 'critical'
        elif self.active_alerts:
            summary['system_health'] = 'degraded'
            
        return summary

    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        if not self.enable_prometheus:
            return ""
            
        return generate_latest(self.prometheus_registry).decode('utf-8')

    async def health_check(self) -> Dict[str, Any]:
        """Perform performance monitor health check."""
        health = {
            "status": "healthy",
            "active_integrations": len(self.integration_profiles),
            "metrics_collected": sum(len(deque_obj) for deque_obj in self.collector.metrics.values()),
            "active_alerts": len(self.active_alerts),
            "storage_backend": self.storage_backend,
            "prometheus_enabled": self.enable_prometheus,
            "issues": []
        }
        
        # Check storage connectivity
        if self.storage_backend == "redis" and self.redis_client:
            try:
                await self.redis_client.ping()
            except Exception as e:
                health["issues"].append(f"Redis connectivity issue: {e}")
                health["status"] = "degraded"
                
        # Check for critical alerts
        critical_alerts = [a for a in self.active_alerts.values() 
                          if a.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]]
        if critical_alerts:
            health["issues"].append(f"{len(critical_alerts)} critical performance alerts")
            health["status"] = "critical" if any(a.level == AlertLevel.EMERGENCY for a in critical_alerts) else "degraded"
            
        return health

    async def shutdown(self) -> None:
        """Shutdown performance monitor gracefully."""
        logger.info("Shutting down performance monitor...")
        
        # Cancel background tasks
        for task in [self.monitor_task, self.system_monitor_task, self.alert_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
            
        logger.info("Performance monitor shutdown completed")

    def __repr__(self) -> str:
        return f"PerformanceMonitor(integrations={len(self.integration_profiles)}, alerts={len(self.active_alerts)})"


# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Export main classes and functions
__all__ = [
    "PerformanceMonitor",
    "PerformanceMetric",
    "PerformanceThreshold",
    "PerformanceAlert",
    "IntegrationProfile",
    "MetricType",
    "AlertLevel",
    "performance_monitor"
]