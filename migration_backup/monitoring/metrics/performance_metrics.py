"""📊 Performance Metrics - Advanced Performance Monitoring System
===============================================================

Enterprise-grade performance monitoring for the Ainflue platform with
real-time metrics, APM integration, and comprehensive performance analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from functools import wraps
from collections import defaultdict, deque
from enum import Enum
import statistics
import json

# Try to import psutil, fallback to mock implementation if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Mock psutil for testing environments
    class MockProcess:
        pid = 12345
        
        def memory_info(self):
            class MemInfo:
                rss = 1024 * 1024 * 50  # 50MB
                vms = 1024 * 1024 * 100  # 100MB
            return MemInfo()
        
        def cpu_percent(self):
            return 15.5  # Mock CPU usage
        
        def memory_percent(self):
            return 45.2  # Mock memory usage
        
        def connections(self):
            return []  # Mock connections list
        
        def open_files(self):
            return []  # Mock open files list
        
        def num_threads(self):
            return 10  # Mock thread count
    
    def cpu_count():
        return 4  # Mock CPU count
    
    def virtual_memory():
        class VirtMem:
            total = 8 * 1024 * 1024 * 1024  # 8GB
            available = 4 * 1024 * 1024 * 1024  # 4GB
            percent = 50.0
            used = 4 * 1024 * 1024 * 1024  # 4GB
        return VirtMem()
    
    def disk_usage(path):
        class DiskUsage:
            total = 100 * 1024 * 1024 * 1024  # 100GB
            used = 50 * 1024 * 1024 * 1024   # 50GB
            free = 50 * 1024 * 1024 * 1024   # 50GB
        return DiskUsage()
    
    def boot_time():
        return time.time() - 86400  # Boot time 24 hours ago
        
    def Process(pid=None):
        return MockProcess()
    
    # Create mock psutil module
    class MockPsutil:
        Process = Process
        cpu_count = staticmethod(cpu_count)
        virtual_memory = staticmethod(virtual_memory)
        disk_usage = staticmethod(disk_usage)
        boot_time = staticmethod(boot_time)
        
        @staticmethod
        def cpu_percent(interval=1):
            return 25.5  # Mock system CPU usage
    
    psutil = MockPsutil()

logger = logging.getLogger(__name__)


class PerformanceMetricType(Enum):
    """Performance metric types for comprehensive monitoring."""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    DATABASE_PERFORMANCE = "database_performance"
    API_RESPONSE_TIME = "api_response_time"
    AUDIO_PROCESSING_LATENCY = "audio_processing_latency"
    CONTENT_PROTECTION_SPEED = "content_protection_speed"
    MONETIZATION_TRANSACTION_TIME = "monetization_transaction_time"
    COLLABORATION_MATCHING_TIME = "collaboration_matching_time"


class AlertLevel(Enum):
    """Performance alert levels."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    name: str
    metric_type: PerformanceMetricType
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, Any] = field(default_factory=dict)
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None


@dataclass
class SystemResources:
    """System resource utilization snapshot."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_connections: int
    open_files: int
    timestamp: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """Advanced performance monitoring system for Ainflue platform."""
    
    def __init__(self, collection_interval: int = 30):
        """Initialize performance monitor.
        
        Args:
            collection_interval: Metrics collection interval in seconds
        """
        self.collection_interval = collection_interval
        self.metrics_storage = defaultdict(deque)
        self.alert_handlers: List[Callable] = []
        self.running = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Performance thresholds
        self.thresholds = {
            PerformanceMetricType.CPU_USAGE: {"warning": 70, "critical": 90},
            PerformanceMetricType.MEMORY_USAGE: {"warning": 80, "critical": 95},
            PerformanceMetricType.DISK_USAGE: {"warning": 85, "critical": 95},
            PerformanceMetricType.API_RESPONSE_TIME: {"warning": 1000, "critical": 5000},  # ms
            PerformanceMetricType.AUDIO_PROCESSING_LATENCY: {"warning": 500, "critical": 2000},  # ms
        }
        
        logger.info("Performance monitor initialized")
    
    async def start_monitoring(self):
        """Start continuous performance monitoring."""
        if self.running:
            logger.warning("Performance monitoring already running")
            return
        
        self.running = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring."""
        self.running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        try:
            while self.running:
                await self.collect_system_metrics()
                await self.collect_application_metrics()
                await asyncio.sleep(self.collection_interval)
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            raise
    
    async def collect_system_metrics(self):
        """Collect system-level performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_metric(PerformanceMetric(
                name="system_cpu_usage",
                metric_type=PerformanceMetricType.CPU_USAGE,
                value=cpu_percent,
                unit="percent",
                threshold_warning=self.thresholds[PerformanceMetricType.CPU_USAGE]["warning"],
                threshold_critical=self.thresholds[PerformanceMetricType.CPU_USAGE]["critical"]
            ))
            
            # Memory metrics
            memory = psutil.virtual_memory()
            await self.record_metric(PerformanceMetric(
                name="system_memory_usage",
                metric_type=PerformanceMetricType.MEMORY_USAGE,
                value=memory.percent,
                unit="percent",
                labels={"total_gb": round(memory.total / (1024**3), 2)},
                threshold_warning=self.thresholds[PerformanceMetricType.MEMORY_USAGE]["warning"],
                threshold_critical=self.thresholds[PerformanceMetricType.MEMORY_USAGE]["critical"]
            ))
            
            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            await self.record_metric(PerformanceMetric(
                name="system_disk_usage",
                metric_type=PerformanceMetricType.DISK_USAGE,
                value=disk_percent,
                unit="percent",
                labels={"total_gb": round(disk.total / (1024**3), 2)},
                threshold_warning=self.thresholds[PerformanceMetricType.DISK_USAGE]["warning"],
                threshold_critical=self.thresholds[PerformanceMetricType.DISK_USAGE]["critical"]
            ))
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def collect_application_metrics(self):
        """Collect application-specific performance metrics."""
        try:
            # Process-specific metrics
            process = psutil.Process()
            
            # Application CPU usage
            app_cpu = process.cpu_percent()
            await self.record_metric(PerformanceMetric(
                name="application_cpu_usage",
                metric_type=PerformanceMetricType.CPU_USAGE,
                value=app_cpu,
                unit="percent",
                labels={"process_id": process.pid}
            ))
            
            # Application memory usage
            memory_info = process.memory_info()
            app_memory_mb = memory_info.rss / (1024 * 1024)
            await self.record_metric(PerformanceMetric(
                name="application_memory_usage",
                metric_type=PerformanceMetricType.MEMORY_USAGE,
                value=app_memory_mb,
                unit="mb",
                labels={"process_id": process.pid}
            ))
            
            # Thread count
            thread_count = process.num_threads()
            await self.record_metric(PerformanceMetric(
                name="application_thread_count",
                metric_type=PerformanceMetricType.CPU_USAGE,
                value=thread_count,
                unit="count",
                labels={"process_id": process.pid}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    async def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric and check thresholds."""
        # Store metric
        self.metrics_storage[metric.name].append(metric)
        
        # Keep only last 1000 metrics per type to manage memory
        if len(self.metrics_storage[metric.name]) > 1000:
            self.metrics_storage[metric.name].popleft()
        
        # Check thresholds and trigger alerts
        await self._check_thresholds(metric)
        
        logger.debug(f"Recorded metric: {metric.name} = {metric.value} {metric.unit}")
    
    async def _check_thresholds(self, metric: PerformanceMetric):
        """Check metric thresholds and trigger alerts."""
        alert_level = None
        
        if metric.threshold_critical and metric.value >= metric.threshold_critical:
            alert_level = AlertLevel.CRITICAL
        elif metric.threshold_warning and metric.value >= metric.threshold_warning:
            alert_level = AlertLevel.WARNING
        
        if alert_level:
            await self._trigger_alert(metric, alert_level)
    
    async def _trigger_alert(self, metric: PerformanceMetric, level: AlertLevel):
        """Trigger performance alert."""
        alert_data = {
            "metric_name": metric.name,
            "value": metric.value,
            "unit": metric.unit,
            "level": level.value,
            "timestamp": metric.timestamp.isoformat(),
            "labels": metric.labels
        }
        
        logger.warning(f"Performance alert triggered: {metric.name} = {metric.value} {metric.unit} (Level: {level.value})")
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert_data)
                else:
                    handler(alert_data)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler for performance notifications."""
        self.alert_handlers.append(handler)
        logger.info(f"Added performance alert handler: {handler.__name__}")
    
    def get_metrics_summary(self, metric_name: str, duration_minutes: int = 60) -> Dict[str, Any]:
        """Get summary statistics for a metric over specified duration."""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        if metric_name not in self.metrics_storage:
            return {"error": f"Metric {metric_name} not found"}
        
        recent_metrics = [
            m for m in self.metrics_storage[metric_name]
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": f"No recent data for {metric_name}"}
        
        values = [m.value for m in recent_metrics]
        
        return {
            "metric_name": metric_name,
            "duration_minutes": duration_minutes,
            "sample_count": len(values),
            "current_value": values[-1] if values else None,
            "average": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "unit": recent_metrics[-1].unit if recent_metrics else None
        }
    
    def get_system_health_score(self) -> Dict[str, Any]:
        """Calculate overall system health score based on key metrics."""
        health_score = 100.0
        health_details = {}
        
        key_metrics = [
            "system_cpu_usage",
            "system_memory_usage", 
            "system_disk_usage"
        ]
        
        for metric_name in key_metrics:
            if metric_name in self.metrics_storage:
                recent_metrics = list(self.metrics_storage[metric_name])[-10:]  # Last 10 samples
                if recent_metrics:
                    avg_value = statistics.mean([m.value for m in recent_metrics])
                    
                    # Calculate health impact
                    if metric_name.endswith("_usage"):
                        if avg_value > 90:
                            health_score -= 30
                            health_details[metric_name] = "critical"
                        elif avg_value > 70:
                            health_score -= 15
                            health_details[metric_name] = "warning"
                        else:
                            health_details[metric_name] = "healthy"
        
        health_score = max(0, health_score)  # Ensure non-negative
        
        if health_score >= 80:
            overall_status = "healthy"
        elif health_score >= 60:
            overall_status = "warning"
        else:
            overall_status = "critical"
        
        return {
            "health_score": health_score,
            "overall_status": overall_status,
            "details": health_details,
            "timestamp": datetime.now().isoformat()
        }


# Performance monitoring decorators
def monitor_execution_time(metric_name: str, monitor: PerformanceMonitor):
    """Decorator to monitor function execution time."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                
                await monitor.record_metric(PerformanceMetric(
                    name=f"{metric_name}_execution_time",
                    metric_type=PerformanceMetricType.API_RESPONSE_TIME,
                    value=execution_time,
                    unit="ms",
                    labels={"function": func.__name__}
                ))
                
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                await monitor.record_metric(PerformanceMetric(
                    name=f"{metric_name}_execution_time_error",
                    metric_type=PerformanceMetricType.API_RESPONSE_TIME,
                    value=execution_time,
                    unit="ms",
                    labels={"function": func.__name__, "error": str(e)}
                ))
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # For sync functions, we'll log the metric for now
                logger.info(f"Performance metric: {metric_name}_execution_time = {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.warning(f"Performance metric (error): {metric_name}_execution_time = {execution_time:.2f}ms, error: {str(e)}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


# Convenience functions
async def start_performance_monitoring():
    """Start global performance monitoring."""
    await performance_monitor.start_monitoring()


async def stop_performance_monitoring():
    """Stop global performance monitoring."""
    await performance_monitor.stop_monitoring()


def get_performance_summary(metric_name: str, duration_minutes: int = 60) -> Dict[str, Any]:
    """Get performance summary for a specific metric."""
    return performance_monitor.get_metrics_summary(metric_name, duration_minutes)


def get_system_health() -> Dict[str, Any]:
    """Get current system health status."""
    return performance_monitor.get_system_health_score()