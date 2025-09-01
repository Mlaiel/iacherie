"""Resource Monitor Module

Advanced database resource monitoring system for tracking CPU, memory, disk I/O,
and database-specific metrics with intelligent alerting and trend analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import time
import psutil
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass, field
from collections import deque, defaultdict
import statistics
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from ...core.logging import get_logger
from ...core.config import settings
from ...core.metrics import MetricsCollector

logger = get_logger(__name__)


class ResourceType(Enum):
    """
Types of system resources"""

    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    DATABASE_CONNECTIONS = "database_connections"
    DATABASE_LOCKS = "database_locks"
    DATABASE_CACHE = "database_cache"
    DATABASE_STORAGE = "database_storage"


class AlertLevel(Enum):
    """Resource alert levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class TrendDirection(Enum):
    """Resource usage trend directions"""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class ResourceThreshold:
    """Resource monitoring threshold configuration"""
    resource_type: ResourceType
    warning_threshold: float
    critical_threshold: float
    emergency_threshold: float
    check_interval_seconds: int = 60
    trend_window_minutes: int = 15
    enable_predictions: bool = True


@dataclass
class ResourceMetrics:
    """
Resource usage metrics at a point in time"""
    timestamp: datetime
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_available_gb: float = 0.0
    disk_read_mb_per_sec: float = 0.0
    disk_write_mb_per_sec: float = 0.0
    disk_usage_percent: float = 0.0
    network_recv_mb_per_sec: float = 0.0
    network_sent_mb_per_sec: float = 0.0
    
    # Database-specific metrics
    active_connections: int = 0
    total_connections: int = 0
    blocked_queries: int = 0
    deadlocks: int = 0
    cache_hit_ratio: float = 0.0
    buffer_cache_mb: float = 0.0
    database_size_gb: float = 0.0
    temp_files_count: int = 0
    temp_files_size_mb: float = 0.0
    
    @property
    def connection_utilization(self) -> float:
        """
Calculate connection pool utilization percentage"""
        if self.total_connections == 0:
            return 0.0
        return (self.active_connections / self.total_connections) * 100


@dataclass
class ResourceAlert:
    """
Resource usage alert"""
    alert_id: str
    resource_type: ResourceType
    level: AlertLevel
    message: str
    current_value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    duration: Optional[timedelta] = None
    
    def resolve(self) -> None:
        """
Mark alert as resolved"""
        if not self.resolved:
            self.resolved = True
            self.resolved_at = datetime.now()
            self.duration = self.resolved_at - self.timestamp


@dataclass
class ResourceTrend:
    """
Resource usage trend analysis"""
    resource_type: ResourceType
    direction: TrendDirection
    rate_of_change: float  # Units per minute
    confidence: float  # 0-1 scale
    predicted_value_1h: Optional[float] = None
    predicted_value_24h: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.now)


class ResourcePredictor:
    """
Predictive analytics for resource usage"""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self._data_points: Dict[ResourceType, deque] = defaultdict(lambda: deque(maxlen=window_size))
    
    def add_data_point(self, resource_type: ResourceType, value: float, timestamp: datetime) -> None:
        """
Add a data point for trend analysis"""
        self._data_points[resource_type].append((timestamp, value))
    
    def analyze_trend(self, resource_type: ResourceType) -> Optional[ResourceTrend]:
        """
Analyze trend for a specific resource"""
        data = self._data_points[resource_type]
        if len(data) < 10:  # Need minimum data points
            return None
        
        try:
            # Extract values and timestamps
            timestamps = [point[0] for point in data]
            values = [point[1] for point in data]
            
            # Calculate time differences in minutes
            time_diffs = [(timestamps[i] - timestamps[0]).total_seconds() / 60 for i in range(len(timestamps))]
            
            # Linear regression for trend
            n = len(values)
            sum_x = sum(time_diffs)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(time_diffs, values))
            sum_x2 = sum(x * x for x in time_diffs)
            
            # Calculate slope (rate of change per minute)
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator == 0:
                rate_of_change = 0.0
            else:
                rate_of_change = (n * sum_xy - sum_x * sum_y) / denominator
            
            # Calculate R-squared for confidence
            mean_y = sum_y / n
            ss_tot = sum((y - mean_y) ** 2 for y in values)
            
            if ss_tot == 0:
                confidence = 1.0
            else:
                # Predicted values using linear regression
                intercept = (sum_y - rate_of_change * sum_x) / n
                predicted_values = [intercept + rate_of_change * x for x in time_diffs]
                ss_res = sum((values[i] - predicted_values[i]) ** 2 for i in range(len(values)))
                confidence = max(0.0, 1 - (ss_res / ss_tot))
            
            # Determine trend direction
            if abs(rate_of_change) < 0.1:  # Very small change
                direction = TrendDirection.STABLE
            elif rate_of_change > 0:
                direction = TrendDirection.INCREASING
            else:
                direction = TrendDirection.DECREASING
            
            # Check for volatility
            if len(values) > 5:
                std_dev = statistics.stdev(values[-10:])  # Last 10 points
                mean_val = statistics.mean(values[-10:])
                if mean_val > 0 and (std_dev / mean_val) > 0.3:  # High coefficient of variation
                    direction = TrendDirection.VOLATILE
            
            # Predict future values
            current_time = timestamps[-1]
            current_value = values[-1]
            
            # 1 hour prediction
            minutes_ahead_1h = 60
            predicted_1h = current_value + (rate_of_change * minutes_ahead_1h)
            
            # 24 hour prediction (but with lower confidence for long-term)
            minutes_ahead_24h = 24 * 60
            predicted_24h = current_value + (rate_of_change * minutes_ahead_24h)
            
            return ResourceTrend(
                resource_type=resource_type,
                direction=direction,
                rate_of_change=rate_of_change,
                confidence=confidence,
                predicted_value_1h=max(0, predicted_1h) if predicted_1h is not None else None,
                predicted_value_24h=max(0, predicted_24h) if predicted_24h is not None else None
            )
            
        except Exception as e:
            logger.warning(f"Trend analysis failed for {resource_type}: {e}")
            return None
    
    def get_all_trends(self) -> Dict[ResourceType, ResourceTrend]:
        """Get trends for all monitored resources"""
        trends = {}
        for resource_type in self._data_points:
            trend = self.analyze_trend(resource_type)
            if trend:
                trends[resource_type] = trend
        return trends


class ResourceMonitor:
    """
Advanced system and database resource monitor"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics_collector = MetricsCollector()
        self.predictor = ResourcePredictor()
        
        # Monitoring configuration
        self.check_interval = self.config.get('check_interval_seconds', 60)
        self.retention_hours = self.config.get('retention_hours', 24)
        self.enable_predictions = self.config.get('enable_predictions', True)
        
        # Resource thresholds
        self.thresholds = self._load_thresholds()
        
        # Data storage
        self._metrics_history: deque = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self._active_alerts: Dict[str, ResourceAlert] = {}
        self._alert_history: List[ResourceAlert] = []
        
        # Monitoring state
        self._monitoring_task: Optional[asyncio.Task] = None
        self._database_engine: Optional[AsyncEngine] = None
        self._last_disk_io = None
        self._last_network_io = None
        
        # Alert callbacks
        self._alert_callbacks: List[Callable[[ResourceAlert], Awaitable[None]]] = []
    
    def _load_thresholds(self) -> Dict[ResourceType, ResourceThreshold]:
        """
Load resource monitoring thresholds"""
        default_thresholds = {
            ResourceType.CPU: ResourceThreshold(
                resource_type=ResourceType.CPU,
                warning_threshold=70.0,
                critical_threshold=85.0,
                emergency_threshold=95.0
            ),
            ResourceType.MEMORY: ResourceThreshold(
                resource_type=ResourceType.MEMORY,
                warning_threshold=75.0,
                critical_threshold=90.0,
                emergency_threshold=95.0
            ),
            ResourceType.DISK_IO: ResourceThreshold(
                resource_type=ResourceType.DISK_IO,
                warning_threshold=100.0,  # MB/s
                critical_threshold=200.0,
                emergency_threshold=500.0
            ),
            ResourceType.DATABASE_CONNECTIONS: ResourceThreshold(
                resource_type=ResourceType.DATABASE_CONNECTIONS,
                warning_threshold=75.0,  # Percentage
                critical_threshold=90.0,
                emergency_threshold=95.0
            ),
        }
        
        # Override with config values if provided
        config_thresholds = self.config.get('thresholds', {})
        for resource_type, threshold in config_thresholds.items():
            if isinstance(resource_type, str):
                resource_type = ResourceType(resource_type)
            default_thresholds[resource_type] = threshold
        
        return default_thresholds
    
    async def start_monitoring(self, database_engine: Optional[AsyncEngine] = None) -> None:
        """
Start resource monitoring"""
        try:
            self._database_engine = database_engine
            
            logger.info("Starting resource monitoring")
            
            # Start monitoring task
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("Resource monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start resource monitoring: {e}")
            raise
    
    async def stop_monitoring(self) -> None:
        """Stop resource monitoring"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Resource monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while True:
            try:
                # Collect metrics
                metrics = await self._collect_metrics()
                
                # Store metrics
                self._metrics_history.append(metrics)
                
                # Update predictor
                if self.enable_predictions:
                    self._update_predictor(metrics)
                
                # Check thresholds and generate alerts
                await self._check_thresholds(metrics)
                
                # Send metrics to collector
                await self._send_metrics(metrics)
                
                # Clean up old data
                self._cleanup_old_data()
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _collect_metrics(self) -> ResourceMetrics:
        """Collect system and database metrics"""
        timestamp = datetime.now()
        metrics = ResourceMetrics(timestamp=timestamp)
        
        # System metrics
        try:
            # CPU
            metrics.cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory
            memory = psutil.virtual_memory()
            metrics.memory_percent = memory.percent
            metrics.memory_available_gb = memory.available / (1024**3)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io and self._last_disk_io:
                time_diff = self.check_interval
                read_diff = disk_io.read_bytes - self._last_disk_io.read_bytes
                write_diff = disk_io.write_bytes - self._last_disk_io.write_bytes
                
                metrics.disk_read_mb_per_sec = (read_diff / time_diff) / (1024**2)
                metrics.disk_write_mb_per_sec = (write_diff / time_diff) / (1024**2)
            
            self._last_disk_io = disk_io
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            metrics.disk_usage_percent = disk_usage.percent
            
            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io and self._last_network_io:
                time_diff = self.check_interval
                recv_diff = network_io.bytes_recv - self._last_network_io.bytes_recv
                sent_diff = network_io.bytes_sent - self._last_network_io.bytes_sent
                
                metrics.network_recv_mb_per_sec = (recv_diff / time_diff) / (1024**2)
                metrics.network_sent_mb_per_sec = (sent_diff / time_diff) / (1024**2)
            
            self._last_network_io = network_io
            
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")
        
        # Database metrics
        if self._database_engine:
            try:
                await self._collect_database_metrics(metrics)
            except Exception as e:
                logger.warning(f"Failed to collect database metrics: {e}")
        
        return metrics
    
    async def _collect_database_metrics(self, metrics: ResourceMetrics) -> None:
        """Collect database-specific metrics"""
        try:
            async with self._database_engine.begin() as conn:
                # Connection stats
                result = await conn.execute(text("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                """))
                row = result.fetchone()
                if row:
                    metrics.total_connections = row.total_connections
                    metrics.active_connections = row.active_connections
                
                # Lock stats
                result = await conn.execute(text("""
                    SELECT count(*) as blocked_queries
                    FROM pg_stat_activity 
                    WHERE waiting = true
                """))
                row = result.fetchone()
                if row:
                    metrics.blocked_queries = row.blocked_queries
                
                # Cache hit ratio
                result = await conn.execute(text("""
                    SELECT 
                        round(
                            100 * sum(heap_blks_hit) / 
                            NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0), 
                            2
                        ) as cache_hit_ratio
                    FROM pg_statio_user_tables
                """))
                row = result.fetchone()
                if row and row.cache_hit_ratio:
                    metrics.cache_hit_ratio = float(row.cache_hit_ratio)
                
                # Database size
                result = await conn.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                           pg_database_size(current_database()) / (1024^3)::float as size_gb
                """))
                row = result.fetchone()
                if row:
                    metrics.database_size_gb = float(row.size_gb)
                
                # Temporary files
                result = await conn.execute(text("""
                    SELECT 
                        sum(temp_files) as temp_files_count,
                        sum(temp_bytes) / (1024^2)::float as temp_files_size_mb
                    FROM pg_stat_database 
                    WHERE datname = current_database()
                """))
                row = result.fetchone()
                if row:
                    metrics.temp_files_count = int(row.temp_files_count or 0)
                    metrics.temp_files_size_mb = float(row.temp_files_size_mb or 0)
                
        except Exception as e:
            logger.warning(f"Database metrics collection error: {e}")
    
    def _update_predictor(self, metrics: ResourceMetrics) -> None:
        """Update predictor with new metrics"""
        timestamp = metrics.timestamp
        
        # Add data points to predictor
        self.predictor.add_data_point(ResourceType.CPU, metrics.cpu_percent, timestamp)
        self.predictor.add_data_point(ResourceType.MEMORY, metrics.memory_percent, timestamp)
        self.predictor.add_data_point(ResourceType.DISK_IO, 
                                     metrics.disk_read_mb_per_sec + metrics.disk_write_mb_per_sec, 
                                     timestamp)
        self.predictor.add_data_point(ResourceType.DATABASE_CONNECTIONS, 
                                     metrics.connection_utilization, timestamp)
    
    async def _check_thresholds(self, metrics: ResourceMetrics) -> None:
        """
Check metrics against thresholds and generate alerts"""
        checks = [
            (ResourceType.CPU, metrics.cpu_percent),
            (ResourceType.MEMORY, metrics.memory_percent),
            (ResourceType.DISK_IO, metrics.disk_read_mb_per_sec + metrics.disk_write_mb_per_sec),
            (ResourceType.DATABASE_CONNECTIONS, metrics.connection_utilization),
        ]
        
        for resource_type, current_value in checks:
            if resource_type not in self.thresholds:
                continue
            
            threshold = self.thresholds[resource_type]
            await self._check_single_threshold(resource_type, current_value, threshold)
    
    async def _check_single_threshold(self, resource_type: ResourceType, current_value: float, threshold: ResourceThreshold) -> None:
        """
Check a single resource against its threshold"""
        alert_level = None
        threshold_value = None
        
        if current_value >= threshold.emergency_threshold:
            alert_level = AlertLevel.EMERGENCY
            threshold_value = threshold.emergency_threshold
        elif current_value >= threshold.critical_threshold:
            alert_level = AlertLevel.CRITICAL
            threshold_value = threshold.critical_threshold
        elif current_value >= threshold.warning_threshold:
            alert_level = AlertLevel.WARNING
            threshold_value = threshold.warning_threshold
        
        alert_key = f"{resource_type.value}_{alert_level.value if alert_level else 'ok'}"
        
        if alert_level:
            # Create or update alert
            if alert_key not in self._active_alerts:
                alert = ResourceAlert(
                    alert_id=alert_key,
                    resource_type=resource_type,
                    level=alert_level,
                    message=f"{resource_type.value.upper()} usage {alert_level.value}: {current_value:.1f}%",
                    current_value=current_value,
                    threshold=threshold_value,
                    timestamp=datetime.now()
                )
                
                self._active_alerts[alert_key] = alert
                self._alert_history.append(alert)
                
                # Trigger alert callbacks
                await self._trigger_alert_callbacks(alert)
                
                logger.warning(f"Resource alert: {alert.message}")
            else:
                # Update existing alert
                self._active_alerts[alert_key].current_value = current_value
        else:
            # Resolve any existing alerts for this resource
            alerts_to_resolve = [
                key for key in self._active_alerts
                if key.startswith(resource_type.value) and not self._active_alerts[key].resolved
            ]
            
            for alert_key in alerts_to_resolve:
                alert = self._active_alerts[alert_key]
                alert.resolve()
                logger.info(f"Resource alert resolved: {alert.message}")
                del self._active_alerts[alert_key]
    
    async def _trigger_alert_callbacks(self, alert: ResourceAlert) -> None:
        """Trigger registered alert callbacks"""
        for callback in self._alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def add_alert_callback(self, callback: Callable[[ResourceAlert], Awaitable[None]]) -> None:
        """Add an alert callback function"""
        self._alert_callbacks.append(callback)
    
    async def _send_metrics(self, metrics: ResourceMetrics) -> None:
        """
Send metrics to monitoring system"""
        try:
            # System metrics
            self.metrics_collector.gauge("system_cpu_percent", metrics.cpu_percent)
            self.metrics_collector.gauge("system_memory_percent", metrics.memory_percent)
            self.metrics_collector.gauge("system_memory_available_gb", metrics.memory_available_gb)
            self.metrics_collector.gauge("system_disk_read_mb_per_sec", metrics.disk_read_mb_per_sec)
            self.metrics_collector.gauge("system_disk_write_mb_per_sec", metrics.disk_write_mb_per_sec)
            self.metrics_collector.gauge("system_disk_usage_percent", metrics.disk_usage_percent)
            self.metrics_collector.gauge("system_network_recv_mb_per_sec", metrics.network_recv_mb_per_sec)
            self.metrics_collector.gauge("system_network_sent_mb_per_sec", metrics.network_sent_mb_per_sec)
            
            # Database metrics
            self.metrics_collector.gauge("database_connections_total", metrics.total_connections)
            self.metrics_collector.gauge("database_connections_active", metrics.active_connections)
            self.metrics_collector.gauge("database_connections_utilization", metrics.connection_utilization)
            self.metrics_collector.gauge("database_blocked_queries", metrics.blocked_queries)
            self.metrics_collector.gauge("database_cache_hit_ratio", metrics.cache_hit_ratio)
            self.metrics_collector.gauge("database_size_gb", metrics.database_size_gb)
            self.metrics_collector.gauge("database_temp_files_count", metrics.temp_files_count)
            self.metrics_collector.gauge("database_temp_files_size_mb", metrics.temp_files_size_mb)
            
        except Exception as e:
            logger.warning(f"Failed to send metrics: {e}")
    
    def _cleanup_old_data(self) -> None:
        """Clean up old metrics and alerts"""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        # Clean up old alert history
        self._alert_history = [
            alert for alert in self._alert_history
            if alert.timestamp > cutoff_time
        ]
    
    def get_current_metrics(self) -> Optional[ResourceMetrics]:
        """
Get the most recent metrics"""
        return self._metrics_history[-1] if self._metrics_history else None
    
    def get_metrics_history(self, hours: int = 1) -> List[ResourceMetrics]:
        """
Get metrics history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metrics for metrics in self._metrics_history
            if metrics.timestamp > cutoff_time
        ]
    
    def get_active_alerts(self) -> List[ResourceAlert]:
        """
Get all active alerts"""
        return list(self._active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[ResourceAlert]:
        """
Get alert history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self._alert_history
            if alert.timestamp > cutoff_time
        ]
    
    def get_resource_trends(self) -> Dict[ResourceType, ResourceTrend]:
        """
Get current resource trends"""
        return self.predictor.get_all_trends()
    
    async def get_resource_summary(self) -> Dict[str, Any]:
        """
Get comprehensive resource summary"""
        current_metrics = self.get_current_metrics()
        active_alerts = self.get_active_alerts()
        trends = self.get_resource_trends()
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "system_health": {
                "cpu_percent": current_metrics.cpu_percent if current_metrics else 0,
                "memory_percent": current_metrics.memory_percent if current_metrics else 0,
                "disk_usage_percent": current_metrics.disk_usage_percent if current_metrics else 0,
                "connection_utilization": current_metrics.connection_utilization if current_metrics else 0,
            },
            "alerts": {
                "active_count": len(active_alerts),
                "critical_count": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
                "emergency_count": len([a for a in active_alerts if a.level == AlertLevel.EMERGENCY]),
            },
            "trends": {
                resource_type.value: {
                    "direction": trend.direction.value,
                    "rate_of_change": trend.rate_of_change,
                    "confidence": trend.confidence,
                    "predicted_1h": trend.predicted_value_1h,
                } for resource_type, trend in trends.items()
            },
            "performance_indicators": {
                "cache_hit_ratio": current_metrics.cache_hit_ratio if current_metrics else 0,
                "blocked_queries": current_metrics.blocked_queries if current_metrics else 0,
                "temp_files_size_mb": current_metrics.temp_files_size_mb if current_metrics else 0,
            }
        }
        
        return summary


# Global resource monitor instance
_resource_monitor: Optional[ResourceMonitor] = None


def get_resource_monitor(config: Optional[Dict[str, Any]] = None) -> ResourceMonitor:
    """Get global resource monitor instance"""
    global _resource_monitor
    
    if _resource_monitor is None:
        _resource_monitor = ResourceMonitor(config)
    
    return _resource_monitor


async def start_resource_monitoring(database_engine: Optional[AsyncEngine] = None, config: Optional[Dict[str, Any]] = None) -> None:
    """
Start global resource monitoring"""
    monitor = get_resource_monitor(config)
    await monitor.start_monitoring(database_engine)


async def stop_resource_monitoring() -> None:
    """
Stop global resource monitoring"""
    global _resource_monitor
    
    if _resource_monitor:
        await _resource_monitor.stop_monitoring()
        _resource_monitor = None


class ContentProtectionResourceMonitor:
    """
Specialized resource monitor for content protection operations"""
    
    def __init__(self, base_monitor: ResourceMonitor):
        self.base_monitor = base_monitor
        self.fingerprint_metrics = {
            'processing_time': deque(maxlen=1000),
            'memory_usage': deque(maxlen=1000),
            'vector_operations': deque(maxlen=1000),
            'similarity_searches': deque(maxlen=1000)
        }
        self.protection_thresholds = {
            'max_fingerprint_time': 30.0,  # seconds
            'max_memory_per_fingerprint': 512,  # MB
            'max_concurrent_operations': 50,
            'max_vector_dimension': 2048
        }
    
    async def monitor_fingerprint_operation(
        self, 
        operation_type: str, 
        content_size: int,
        vector_dimension: int = None
    ) -> Dict[str, Any]:
        """
Monitor fingerprint generation operation"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Monitor during operation
            yield {"status": "monitoring", "start_time": start_time}
            
        finally:
            # Calculate metrics
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            processing_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            # Store metrics
            self.fingerprint_metrics['processing_time'].append(processing_time)
            self.fingerprint_metrics['memory_usage'].append(memory_used)
            
            if vector_dimension:
                self.fingerprint_metrics['vector_operations'].append(vector_dimension)
            
            # Check thresholds
            alerts = []
            if processing_time > self.protection_thresholds['max_fingerprint_time']:
                alerts.append(f"Fingerprint processing time exceeded: {processing_time:.2f}s")
            
            if memory_used > self.protection_thresholds['max_memory_per_fingerprint']:
                alerts.append(f"Memory usage exceeded: {memory_used:.2f}MB")
            
            return {
                'operation_type': operation_type,
                'processing_time': processing_time,
                'memory_used': memory_used,
                'content_size': content_size,
                'vector_dimension': vector_dimension,
                'alerts': alerts,
                'timestamp': datetime.now()
            }
    
    async def monitor_similarity_search(
        self, 
        query_vector_size: int, 
        database_size: int
    ) -> Dict[str, Any]:
        """Monitor vector similarity search performance"""
        start_time = time.time()
        
        try:
            yield {"status": "searching", "start_time": start_time}
            
        finally:
            search_time = time.time() - start_time
            self.fingerprint_metrics['similarity_searches'].append(search_time)
            
            return {
                'search_time': search_time,
                'query_vector_size': query_vector_size,
                'database_size': database_size,
                'performance_score': self._calculate_search_performance(search_time, database_size),
                'timestamp': datetime.now()
            }
    
    def _calculate_search_performance(self, search_time: float, database_size: int) -> float:
        """Calculate search performance score (0-100)"""
        # Baseline: 1 second for 1M vectors is score 100
        baseline_time = database_size / 1000000
        if search_time <= baseline_time:
            return 100.0
        else:
            return max(0, 100 - ((search_time - baseline_time) / baseline_time * 100))
    
    def get_protection_metrics(self) -> Dict[str, Any]:
        """
Get content protection specific metrics"""
        if not self.fingerprint_metrics['processing_time']:
            return {}
        
        return {
            'avg_fingerprint_time': statistics.mean(self.fingerprint_metrics['processing_time']),
            'max_fingerprint_time': max(self.fingerprint_metrics['processing_time']),
            'avg_memory_usage': statistics.mean(self.fingerprint_metrics['memory_usage']),
            'max_memory_usage': max(self.fingerprint_metrics['memory_usage']),
            'avg_search_time': statistics.mean(self.fingerprint_metrics['similarity_searches']) if self.fingerprint_metrics['similarity_searches'] else 0,
            'total_operations': len(self.fingerprint_metrics['processing_time']),
            'total_searches': len(self.fingerprint_metrics['similarity_searches'])
        }


class MonetizationResourceMonitor:
    """
Specialized resource monitor for monetization operations"""
    
    def __init__(self, base_monitor: ResourceMonitor):
        self.base_monitor = base_monitor
        self.revenue_metrics = {
            'calculation_time': deque(maxlen=1000),
            'aggregation_time': deque(maxlen=1000),
            'report_generation_time': deque(maxlen=1000),
            'api_response_time': deque(maxlen=1000)
        }
        self.monetization_thresholds = {
            'max_calculation_time': 5.0,  # seconds
            'max_aggregation_time': 15.0,  # seconds
            'max_report_time': 30.0,  # seconds
            'max_api_response_time': 2.0  # seconds
        }
    
    async def monitor_revenue_calculation(
        self, 
        user_count: int, 
        period_days: int
    ) -> Dict[str, Any]:
        """
Monitor revenue calculation performance"""
        start_time = time.time()
        
        try:
            yield {"status": "calculating", "start_time": start_time}
            
        finally:
            calculation_time = time.time() - start_time
            self.revenue_metrics['calculation_time'].append(calculation_time)
            
            alerts = []
            if calculation_time > self.monetization_thresholds['max_calculation_time']:
                alerts.append(f"Revenue calculation time exceeded: {calculation_time:.2f}s")
            
            return {
                'calculation_time': calculation_time,
                'user_count': user_count,
                'period_days': period_days,
                'performance_score': self._calculate_revenue_performance(calculation_time, user_count),
                'alerts': alerts,
                'timestamp': datetime.now()
            }
    
    async def monitor_report_generation(
        self, 
        report_type: str, 
        data_points: int
    ) -> Dict[str, Any]:
        """Monitor report generation performance"""
        start_time = time.time()
        
        try:
            yield {"status": "generating", "start_time": start_time}
            
        finally:
            generation_time = time.time() - start_time
            self.revenue_metrics['report_generation_time'].append(generation_time)
            
            return {
                'generation_time': generation_time,
                'report_type': report_type,
                'data_points': data_points,
                'performance_score': self._calculate_report_performance(generation_time, data_points),
                'timestamp': datetime.now()
            }
    
    def _calculate_revenue_performance(self, calculation_time: float, user_count: int) -> float:
        """Calculate revenue calculation performance score"""
        # Baseline: 1 second per 1000 users is score 100
        baseline_time = user_count / 1000
        if calculation_time <= baseline_time:
            return 100.0
        else:
            return max(0, 100 - ((calculation_time - baseline_time) / baseline_time * 100))
    
    def _calculate_report_performance(self, generation_time: float, data_points: int) -> float:
        """
Calculate report generation performance score"""
        # Baseline: 0.01 second per data point is score 100
        baseline_time = data_points * 0.01
        if generation_time <= baseline_time:
            return 100.0
        else:
            return max(0, 100 - ((generation_time - baseline_time) / baseline_time * 100))
    
    def get_monetization_metrics(self) -> Dict[str, Any]:
        """
Get monetization specific metrics"""
        if not self.revenue_metrics['calculation_time']:
            return {}
        
        return {
            'avg_calculation_time': statistics.mean(self.revenue_metrics['calculation_time']),
            'max_calculation_time': max(self.revenue_metrics['calculation_time']),
            'avg_report_time': statistics.mean(self.revenue_metrics['report_generation_time']) if self.revenue_metrics['report_generation_time'] else 0,
            'max_report_time': max(self.revenue_metrics['report_generation_time']) if self.revenue_metrics['report_generation_time'] else 0,
            'total_calculations': len(self.revenue_metrics['calculation_time']),
            'total_reports': len(self.revenue_metrics['report_generation_time'])
        }


class MultimediaResourceMonitor:
    """
Specialized resource monitor for multimedia processing operations"""
    
    def __init__(self, base_monitor: ResourceMonitor):
        self.base_monitor = base_monitor
        self.multimedia_metrics = {
            'audio_processing_time': deque(maxlen=1000),
            'video_processing_time': deque(maxlen=1000),
            'image_processing_time': deque(maxlen=1000),
            'upload_time': deque(maxlen=1000),
            'transcoding_time': deque(maxlen=1000)
        }
        self.multimedia_thresholds = {
            'max_audio_processing_time': 60.0,  # seconds
            'max_video_processing_time': 300.0,  # seconds
            'max_image_processing_time': 10.0,  # seconds
            'max_upload_time': 120.0,  # seconds
            'max_file_size': 1024  # MB
        }
    
    async def monitor_content_upload(
        self, 
        content_type: str, 
        file_size: int, 
        format: str
    ) -> Dict[str, Any]:
        """
Monitor content upload performance"""
        start_time = time.time()
        
        try:
            yield {"status": "uploading", "start_time": start_time}
            
        finally:
            upload_time = time.time() - start_time
            self.multimedia_metrics['upload_time'].append(upload_time)
            
            alerts = []
            if upload_time > self.multimedia_thresholds['max_upload_time']:
                alerts.append(f"Upload time exceeded: {upload_time:.2f}s")
            
            if file_size > self.multimedia_thresholds['max_file_size'] * 1024 * 1024:
                alerts.append(f"File size exceeded: {file_size / 1024 / 1024:.2f}MB")
            
            return {
                'upload_time': upload_time,
                'content_type': content_type,
                'file_size': file_size,
                'format': format,
                'upload_speed_mbps': (file_size / 1024 / 1024) / upload_time if upload_time > 0 else 0,
                'alerts': alerts,
                'timestamp': datetime.now()
            }
    
    async def monitor_content_processing(
        self, 
        content_type: str, 
        duration: float, 
        quality: str
    ) -> Dict[str, Any]:
        """Monitor content processing performance"""
        start_time = time.time()
        
        try:
            yield {"status": "processing", "start_time": start_time}
            
        finally:
            processing_time = time.time() - start_time
            
            # Store in appropriate metric
            metric_key = f"{content_type}_processing_time"
            if metric_key in self.multimedia_metrics:
                self.multimedia_metrics[metric_key].append(processing_time)
            
            # Check thresholds
            alerts = []
            threshold_key = f"max_{content_type}_processing_time"
            if threshold_key in self.multimedia_thresholds:
                if processing_time > self.multimedia_thresholds[threshold_key]:
                    alerts.append(f"{content_type.title()} processing time exceeded: {processing_time:.2f}s")
            
            return {
                'processing_time': processing_time,
                'content_type': content_type,
                'duration': duration,
                'quality': quality,
                'processing_ratio': processing_time / duration if duration > 0 else 0,
                'alerts': alerts,
                'timestamp': datetime.now()
            }
    
    def get_multimedia_metrics(self) -> Dict[str, Any]:
        """Get multimedia processing specific metrics"""
        metrics = {}
        
        for metric_type, values in self.multimedia_metrics.items():
            if values:
                metrics[f"avg_{metric_type}"] = statistics.mean(values)
                metrics[f"max_{metric_type}"] = max(values)
                metrics[f"total_{metric_type.replace('_time', '_operations')}"] = len(values)
        
        return metrics


class AIProcessingResourceMonitor:
    """Specialized resource monitor for AI processing operations"""
    
    def __init__(self, base_monitor: ResourceMonitor):
        self.base_monitor = base_monitor
        self.ai_metrics = {
            'model_inference_time': deque(maxlen=1000),
            'training_time': deque(maxlen=1000),
            'gpu_utilization': deque(maxlen=1000),
            'memory_usage': deque(maxlen=1000)
        }
        self.ai_thresholds = {
            'max_inference_time': 5.0,  # seconds
            'max_training_time': 3600.0,  # seconds
            'max_gpu_utilization': 95.0,  # percentage
            'max_memory_usage': 8192  # MB
        }
    
    async def monitor_ml_inference(
        self, 
        model_name: str, 
        input_size: int,
        batch_size: int = 1
    ) -> Dict[str, Any]:
        """
Monitor ML model inference performance"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            yield {"status": "inferencing", "start_time": start_time}
            
        finally:
            inference_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_used = end_memory - start_memory
            
            self.ai_metrics['model_inference_time'].append(inference_time)
            self.ai_metrics['memory_usage'].append(memory_used)
            
            alerts = []
            if inference_time > self.ai_thresholds['max_inference_time']:
                alerts.append(f"Inference time exceeded: {inference_time:.2f}s")
            
            if memory_used > self.ai_thresholds['max_memory_usage']:
                alerts.append(f"Memory usage exceeded: {memory_used:.2f}MB")
            
            return {
                'inference_time': inference_time,
                'model_name': model_name,
                'input_size': input_size,
                'batch_size': batch_size,
                'memory_used': memory_used,
                'throughput': batch_size / inference_time if inference_time > 0 else 0,
                'alerts': alerts,
                'timestamp': datetime.now()
            }
    
    def get_ai_metrics(self) -> Dict[str, Any]:
        """Get AI processing specific metrics"""
        if not self.ai_metrics['model_inference_time']:
            return {}
        
        return {
            'avg_inference_time': statistics.mean(self.ai_metrics['model_inference_time']),
            'max_inference_time': max(self.ai_metrics['model_inference_time']),
            'avg_memory_usage': statistics.mean(self.ai_metrics['memory_usage']),
            'max_memory_usage': max(self.ai_metrics['memory_usage']),
            'total_inferences': len(self.ai_metrics['model_inference_time'])
        }
