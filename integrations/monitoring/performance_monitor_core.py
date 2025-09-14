"""Performance Monitor Core - Core Performance Monitoring System
================================================================

Core performance monitoring infrastructure for Ainflue integrations.
Provides the main PerformanceMonitor class and result management.

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

@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    timestamp: datetime
    metric_name: str
    metric_type: MetricType
    value: float
    integration_name: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    integration_name: Optional[str] = None
    comparison: str = "greater"  # greater, less, equal

@dataclass
class PerformanceAlert:
    """Performance alert notification."""
    alert_id: str
    metric_name: str
    integration_name: Optional[str]
    alert_level: AlertLevel
    threshold_value: float
    actual_value: float
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class IntegrationProfile:
    """Performance profile for an integration."""
    integration_name: str
    last_updated: datetime
    avg_latency: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    uptime: float = 0.0
    total_requests: int = 0
    total_errors: int = 0
    peak_latency: float = 0.0
    peak_memory: float = 0.0
    health_score: float = 100.0
    
    # Historical data (last 24 hours)
    latency_history: List[float] = field(default_factory=list)
    throughput_history: List[float] = field(default_factory=list)
    error_history: List[float] = field(default_factory=list)

class PerformanceMonitor:
    """Comprehensive performance monitoring system."""
    
    def __init__(
        self,
        enable_prometheus -> None: bool = True,
        prometheus_port -> None: int = 8080,
        storage_backend -> None: str = "memory",  # memory, redis, file
        storage_config -> None: Optional[Dict[str, Any]] = None,
        alert_thresholds -> None: Optional[List[PerformanceThreshold]] = None,
        collection_interval -> None: int = 60,  # seconds
        retention_period -> None: int = 86400,  # 24 hours in seconds
        enable_system_monitoring -> None: bool = True
    ) -> None:
        self.enable_prometheus = enable_prometheus
        self.prometheus_port = prometheus_port
        self.storage_backend = storage_backend
        self.storage_config = storage_config or {}
        self.collection_interval = collection_interval
        self.retention_period = retention_period
        self.enable_system_monitoring = enable_system_monitoring
        
        # Internal state
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.integration_profiles: Dict[str, IntegrationProfile] = {}
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_callbacks: List[Callable] = []
        
        # Async components
        self.redis_client: Optional[aioredis.Redis] = None
        self.monitor_task: Optional[asyncio.Task] = None
        self.system_monitor_task: Optional[asyncio.Task] = None
        self.alert_task: Optional[asyncio.Task] = None
        self.monitoring_enabled: bool = True
        
        # Prometheus metrics
        if self.enable_prometheus:
            self.prometheus_registry = CollectorRegistry()
            self._setup_prometheus_metrics()
            
        # Load default thresholds
        if alert_thresholds:
            for threshold in alert_thresholds:
                self.thresholds[f"{threshold.integration_name}:{threshold.metric_name}"] = threshold
                
        logger.info("Performance monitor initialized with backend: %s", storage_backend)

    def _setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics collectors."""
        self.prometheus_metrics = {
            'latency': Histogram(
                'integration_latency_seconds',
                'Integration request latency',
                ['integration', 'operation'],
                registry=self.prometheus_registry
            ),
            'throughput': Counter(
                'integration_requests_total',
                'Total integration requests',
                ['integration', 'status'],
                registry=self.prometheus_registry
            ),
            'error_rate': Gauge(
                'integration_error_rate',
                'Integration error rate',
                ['integration'],
                registry=self.prometheus_registry
            ),
            'memory_usage': Gauge(
                'integration_memory_usage_bytes',
                'Integration memory usage',
                ['integration'],
                registry=self.prometheus_registry
            ),
            'health_score': Gauge(
                'integration_health_score',
                'Integration health score',
                ['integration'],
                registry=self.prometheus_registry
            )
        }

    async def initialize(self, redis_url: Optional[str] = None) -> None:
        """Initialize the performance monitor."""
        try:
            # Setup Redis connection if using redis backend
            if self.storage_backend == "redis":
                if redis_url:
                    self.redis_client = aioredis.from_url(redis_url)
                else:
                    self.redis_client = aioredis.from_url(
                        self.storage_config.get('redis_url', 'redis://localhost:6379')
                    )
                await self.redis_client.ping()
                logger.info("Connected to Redis for performance monitoring")
                
            # Setup default thresholds
            await self._setup_default_thresholds()
            
            # Start background monitoring tasks
            if self.monitoring_enabled:
                self.monitor_task = asyncio.create_task(self._monitor_loop())
                self.alert_task = asyncio.create_task(self._alert_loop())
                
                if self.enable_system_monitoring:
                    self.system_monitor_task = asyncio.create_task(self._system_monitor_loop())
                    
            logger.info("Performance monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance monitor: {e}")
            raise

    async def _setup_default_thresholds(self) -> None:
        """Setup default performance thresholds."""
        default_thresholds = [
            PerformanceThreshold("latency", 1.0, 3.0),  # 1s warning, 3s critical
            PerformanceThreshold("error_rate", 0.05, 0.15),  # 5% warning, 15% critical
            PerformanceThreshold("memory_usage", 80.0, 95.0),  # 80% warning, 95% critical
            PerformanceThreshold("cpu_usage", 70.0, 90.0),  # 70% warning, 90% critical
        ]
        
        for threshold in default_thresholds:
            key = f"default:{threshold.metric_name}"
            if key not in self.thresholds:
                self.thresholds[key] = threshold

    @asynccontextmanager
    async def trace_performance(
        self,
        operation_name -> None: str,
        integration_name -> None: Optional[str] = None,
        tags -> None: Optional[Dict[str, str]] = None
    ) -> None:
        """Context manager for tracing operation performance."""
        start_time = time.time()
        tags = tags or {}
        
        try:
            yield
            
            # Record successful operation
            end_time = time.time()
            latency = end_time - start_time
            
            await self.record_latency(operation_name, latency, integration_name, tags)
            await self.record_throughput(operation_name, 1, integration_name, tags)
            
        except Exception as e:
            # Record failed operation
            end_time = time.time()
            latency = end_time - start_time
            
            await self.record_latency(operation_name, latency, integration_name, tags)
            await self.record_error(operation_name, str(e), integration_name, tags)
            
            # Re-raise the exception
            raise

    async def record_latency(
        self,
        operation_name: str,
        latency_seconds: float,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record operation latency."""
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_name=f"{operation_name}_latency",
            metric_type=MetricType.LATENCY,
            value=latency_seconds,
            integration_name=integration_name,
            tags=tags or {}
        )
        await self._store_metric(metric)

    async def record_throughput(
        self,
        operation_name: str,
        count: int,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record operation throughput."""
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_name=f"{operation_name}_throughput",
            metric_type=MetricType.THROUGHPUT,
            value=float(count),
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
        """Record operation error rate."""
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_name=f"{operation_name}_error_rate",
            metric_type=MetricType.ERROR_RATE,
            value=error_rate,
            integration_name=integration_name,
            tags=tags or {}
        )
        await self._store_metric(metric)

    async def record_memory_usage(
        self,
        operation_name: str,
        memory_mb: float,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record memory usage."""
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_name=f"{operation_name}_memory",
            metric_type=MetricType.MEMORY_USAGE,
            value=memory_mb,
            integration_name=integration_name,
            tags=tags or {}
        )
        await self._store_metric(metric)

    async def record_error(
        self,
        operation_name: str,
        error_message: str,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        error_count: float = 1.0
    ) -> None:
        """Record an error occurrence."""
        error_tags = (tags or {}).copy()
        error_tags['error_type'] = error_message[:100]  # Truncate long error messages
        
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_name=f"{operation_name}_errors",
            metric_type=MetricType.ERROR_RATE,
            value=error_count,
            integration_name=integration_name,
            tags=error_tags
        )
        await self._store_metric(metric)

    async def _store_metric(self, metric: PerformanceMetric) -> None:
        """Store performance metric using configured backend."""
        try:
            if self.storage_backend == "redis" and self.redis_client:
                await self._store_metric_redis(metric)
            elif self.storage_backend == "file":
                await self._store_metric_file(metric)
            else:
                # Default to in-memory storage
                key = f"{metric.integration_name}:{metric.metric_name}"
                self.metrics[key].append(metric)
                
            # Update integration profile
            if metric.integration_name:
                await self._update_integration_profile(metric)
                
            # Update Prometheus metrics
            if self.enable_prometheus:
                await self._update_prometheus_metrics(metric)
                
        except Exception as e:
            logger.error(f"Error storing metric {metric.metric_name}: {e}")

    async def _store_metric_redis(self, metric: PerformanceMetric) -> None:
        """Store metric in Redis."""
        if not self.redis_client:
            return
            
        try:
            key = f"performance:{metric.integration_name}:{metric.metric_name}"
            data = {
                'timestamp': metric.timestamp.isoformat(),
                'metric_type': metric.metric_type.value,
                'value': metric.value,
                'tags': json.dumps(metric.tags)
            }
            
            # Store as a time series (sorted set)
            score = metric.timestamp.timestamp()
            await self.redis_client.zadd(key, {json.dumps(data): score})
            
            # Set expiration
            await self.redis_client.expire(key, self.retention_period)
            
        except Exception as e:
            logger.error(f"Error storing metric in Redis: {e}")

    async def _store_metric_file(self, metric: PerformanceMetric) -> None:
        """Store metric in file."""
        try:
            # Create filename based on date and integration
            date_str = metric.timestamp.strftime('%Y-%m-%d')
            filename = f"performance_{metric.integration_name}_{date_str}.jsonl"
            filepath = self.storage_config.get('file_path', './performance_logs') + '/' + filename
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Append metric to file
            data = asdict(metric)
            data['timestamp'] = metric.timestamp.isoformat()
            data['metric_type'] = metric.metric_type.value
            
            async with aiofiles.open(filepath, 'a') as f:
                await f.write(json.dumps(data) + '\n')
                
        except Exception as e:
            logger.error(f"Error storing metric to file: {e}")

    async def _update_integration_profile(self, metric: PerformanceMetric) -> None:
        """Update integration performance profile."""
        if not metric.integration_name:
            return
            
        profile = self.integration_profiles.get(metric.integration_name)
        if not profile:
            profile = IntegrationProfile(
                integration_name=metric.integration_name,
                last_updated=datetime.utcnow()
            )
            self.integration_profiles[metric.integration_name] = profile
            
        # Update profile based on metric type
        if metric.metric_type == MetricType.LATENCY:
            profile.avg_latency = (profile.avg_latency + metric.value) / 2
            profile.peak_latency = max(profile.peak_latency, metric.value)
            profile.latency_history.append(metric.value)
            if len(profile.latency_history) > 1440:  # Keep 24 hours (1 per minute)
                profile.latency_history.pop(0)
                
        elif metric.metric_type == MetricType.THROUGHPUT:
            profile.throughput = (profile.throughput + metric.value) / 2
            profile.total_requests += int(metric.value)
            profile.throughput_history.append(metric.value)
            if len(profile.throughput_history) > 1440:
                profile.throughput_history.pop(0)
                
        elif metric.metric_type == MetricType.ERROR_RATE:
            profile.error_rate = (profile.error_rate + metric.value) / 2
            profile.total_errors += int(metric.value)
            profile.error_history.append(metric.value)
            if len(profile.error_history) > 1440:
                profile.error_history.pop(0)
                
        elif metric.metric_type == MetricType.MEMORY_USAGE:
            profile.memory_usage = metric.value
            profile.peak_memory = max(profile.peak_memory, metric.value)
            
        # Calculate health score
        health_factors = []
        if profile.avg_latency > 0:
            latency_score = max(0, 100 - (profile.avg_latency * 20))  # Penalize high latency
            health_factors.append(latency_score)
            
        if profile.error_rate >= 0:
            error_score = max(0, 100 - (profile.error_rate * 100))  # Penalize high error rate
            health_factors.append(error_score)
            
        if health_factors:
            profile.health_score = sum(health_factors) / len(health_factors)
            
        profile.last_updated = datetime.utcnow()

    async def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self.monitoring_enabled:
            try:
                await asyncio.sleep(self.collection_interval)
                
                # Collect metrics from all integrations
                await self._collect_integration_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _system_monitor_loop(self) -> None:
        """Background system monitoring loop."""
        while self.monitoring_enabled:
            try:
                await asyncio.sleep(30)  # System metrics every 30 seconds
                
                # Collect system metrics
                await self._collect_system_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system monitoring loop: {e}")
                await asyncio.sleep(5)

    async def _collect_system_metrics(self) -> None:
        """Collect system-level performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_metric("system_cpu", cpu_percent, MetricType.CPU_USAGE)
            
            # Memory usage
            memory = psutil.virtual_memory()
            await self.record_metric("system_memory", memory.percent, MetricType.MEMORY_USAGE)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                await self.record_metric("system_disk_read", disk_io.read_bytes, MetricType.DISK_IO)
                await self.record_metric("system_disk_write", disk_io.write_bytes, MetricType.DISK_IO)
                
            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io:
                await self.record_metric("system_network_sent", network_io.bytes_sent, MetricType.NETWORK_IO)
                await self.record_metric("system_network_recv", network_io.bytes_recv, MetricType.NETWORK_IO)
                
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    async def record_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: MetricType,
        integration_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Generic method to record any metric."""
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_name=metric_name,
            metric_type=metric_type,
            value=value,
            integration_name=integration_name,
            tags=tags or {}
        )
        await self._store_metric(metric)

    async def _collect_integration_metrics(self) -> None:
        """Collect metrics from all registered integrations."""
        for integration_name, profile in self.integration_profiles.items():
            try:
                # This would interface with actual integration instances
                # For now, simulate some metrics
                
                # Example: Record current health score
                await self.record_metric(
                    "health_score",
                    profile.health_score,
                    MetricType.THROUGHPUT,
                    integration_name
                )
                
            except Exception as e:
                logger.error(f"Error collecting metrics for {integration_name}: {e}")

    def get_integration_profile(self, integration_name: str) -> Optional[IntegrationProfile]:
        """Get performance profile for an integration."""
        return self.integration_profiles.get(integration_name)

    def get_all_profiles(self) -> Dict[str, IntegrationProfile]:
        """Get all integration performance profiles."""
        return self.integration_profiles.copy()

    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get all active performance alerts."""
        return [alert for alert in self.active_alerts.values() if not alert.resolved]

    async def get_metrics_summary(self, integration_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics summary."""
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_integrations': len(self.integration_profiles),
            'active_alerts': len(self.get_active_alerts()),
            'overall_health': 0.0,
            'integrations': {}
        }
        
        if integration_name:
            profiles = {integration_name: self.integration_profiles.get(integration_name)}
        else:
            profiles = self.integration_profiles
            
        health_scores = []
        for name, profile in profiles.items():
            if profile:
                summary['integrations'][name] = {
                    'health_score': profile.health_score,
                    'avg_latency': profile.avg_latency,
                    'throughput': profile.throughput,
                    'error_rate': profile.error_rate,
                    'memory_usage': profile.memory_usage,
                    'total_requests': profile.total_requests,
                    'total_errors': profile.total_errors,
                    'last_updated': profile.last_updated.isoformat()
                }
                health_scores.append(profile.health_score)
                
        if health_scores:
            summary['overall_health'] = sum(health_scores) / len(health_scores)
            
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
            "integrations_monitored": len(self.integration_profiles),
            "active_alerts": len(self.get_active_alerts()),
            "monitoring_enabled": self.monitoring_enabled,
            "storage_backend": self.storage_backend,
            "issues": []
        }
        
        # Check Redis connection if using redis backend
        if self.storage_backend == "redis" and self.redis_client:
            try:
                await self.redis_client.ping()
            except Exception as e:
                health["issues"].append(f"Redis connection failed: {e}")
                health["status"] = "degraded"
                
        # Check for critical alerts
        critical_alerts = [a for a in self.get_active_alerts() 
                          if a.alert_level == AlertLevel.CRITICAL]
        if critical_alerts:
            health["issues"].append(f"{len(critical_alerts)} critical alerts active")
            health["status"] = "critical"
            
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