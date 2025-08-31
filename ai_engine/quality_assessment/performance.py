"""
Quality Assessment Performance Monitor

Advanced performance monitoring and metrics collection for quality assessment operations.
Provides real-time monitoring, performance analytics, and resource optimization.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING 
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.
"""

import asyncio
import time
import logging
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import statistics
from functools import wraps

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to collect"""
    PROCESSING_TIME = "processing_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    QUEUE_SIZE = "queue_size"
    CACHE_HIT_RATE = "cache_hit_rate"
    USER_SATISFACTION = "user_satisfaction"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    metric_type: MetricType
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""



        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'metric_type': self.metric_type.value,
            'context': self.context
        }


@dataclass
class PerformanceAlert:
    """Performance alert"""
    message: str
    severity: AlertSeverity
    metric_name: str
    threshold_value: float
    actual_value: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""



        return {
            'message': self.message,
            'severity': self.severity.value,
            'metric_name': self.metric_name,
            'threshold_value': self.threshold_value,
            'actual_value': self.actual_value,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context
        }


@dataclass
class SystemResourceInfo:
    """System resource information"""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_available_mb': self.memory_available_mb,
            'disk_usage_percent': self.disk_usage_percent,
            'disk_free_gb': self.disk_free_gb,
            'network_sent_mb': self.network_sent_mb,
            'network_recv_mb': self.network_recv_mb,
            'timestamp': self.timestamp.isoformat()
        }


class PerformanceTracker:
    """
    Performance tracking and monitoring system
    
    Tracks performance metrics, system resources, and generates alerts
    for quality assessment operations.
    """
    
    def __init__(self, max_history_size: int = 10000):
        """
        Initialize performance tracker
        
        Args:
            max_history_size: Maximum number of metrics to keep in history
        """
        self.max_history_size = max_history_size
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history_size))
        self.alerts: List[PerformanceAlert] = []
        self.thresholds: Dict[str, Dict[str, float]] = {}
        self.start_time = datetime.now()
        self.operation_counters: Dict[str, int] = defaultdict(int)
        self.error_counters: Dict[str, int] = defaultdict(int)
        
        # Resource monitoring
        self.system_resources: deque = deque(maxlen=1000)
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Set default thresholds
        self._set_default_thresholds()
    
    def _set_default_thresholds(self):
        """Set default performance thresholds"""
        self.thresholds = {
            'processing_time': {
                'warning': 30.0,    # 30 seconds
                'critical': 60.0    # 60 seconds
            },
            'memory_usage': {
                'warning': 80.0,    # 80%
                'critical': 95.0    # 95%
            },
            'cpu_usage': {
                'warning': 85.0,    # 85%
                'critical': 95.0    # 95%
            },
            'disk_usage': {
                'warning': 85.0,    # 85%
                'critical': 95.0    # 95%
            },
            'error_rate': {
                'warning': 5.0,     # 5%
                'critical': 15.0    # 15%
            },
            'throughput': {
                'warning': 10.0,    # Operations per minute
                'critical': 5.0     # Operations per minute
            }
        }
    
    def start_monitoring(self, interval: float = 5.0):
        """
        Start system resource monitoring
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring_active:
            logger.warning("Performance monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_system_resources,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop system resource monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Performance monitoring stopped")
    
    def _monitor_system_resources(self, interval: float):
        """Monitor system resources continuously"""
        logger.info(f"System resource monitoring started with {interval}s interval")
        
        while self.monitoring_active:
            try:
                # Collect system metrics
                resource_info = self._collect_system_resources()
                self.system_resources.append(resource_info)
                
                # Check for threshold violations
                self._check_resource_thresholds(resource_info)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                time.sleep(interval)
    
    def _collect_system_resources(self) -> SystemResourceInfo:
        """Collect current system resource information"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_mb = memory.available / (1024 * 1024)
        
        # Disk usage
        disk = psutil.disk_usage('.')
        disk_usage_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024 * 1024 * 1024)
        
        # Network IO
        network = psutil.net_io_counters()
        network_sent_mb = network.bytes_sent / (1024 * 1024)
        network_recv_mb = network.bytes_recv / (1024 * 1024)
        
        return SystemResourceInfo(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_mb=memory_available_mb,
            disk_usage_percent=disk_usage_percent,
            disk_free_gb=disk_free_gb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            timestamp=datetime.now()
        )
    
    def _check_resource_thresholds(self, resource_info: SystemResourceInfo):
        """Check resource metrics against thresholds"""
        checks = [
            ('cpu_usage', resource_info.cpu_percent, '%'),
            ('memory_usage', resource_info.memory_percent, '%'),
            ('disk_usage', resource_info.disk_usage_percent, '%')
        ]
        
        for metric_name, value, unit in checks:
            self._check_threshold(metric_name, value, unit)
    
    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        metric_type: MetricType = MetricType.PROCESSING_TIME,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Record a performance metric
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            metric_type: Type of metric
            context: Additional context information
        """
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            metric_type=metric_type,
            context=context or {}
        )
        
        self.metrics_history[name].append(metric)
        
        # Check threshold
        self._check_threshold(name, value, unit)
        
        logger.debug(f"Recorded metric: {name} = {value} {unit}")
    
    def _check_threshold(self, metric_name: str, value: float, unit: str):
        """Check if metric value exceeds thresholds"""
        if metric_name not in self.thresholds:
            return
        
        thresholds = self.thresholds[metric_name]
        
        if value >= thresholds.get('critical', float('inf')):
            severity = AlertSeverity.CRITICAL
            threshold = thresholds['critical']
        elif value >= thresholds.get('warning', float('inf')):
            severity = AlertSeverity.WARNING
            threshold = thresholds['warning']
        else:
            return  # No threshold exceeded
        
        alert = PerformanceAlert(
            message=f"{metric_name} ({value:.2f} {unit}) exceeded {severity.value} threshold ({threshold:.2f} {unit})",
            severity=severity,
            metric_name=metric_name,
            threshold_value=threshold,
            actual_value=value,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        logger.warning(f"Performance alert: {alert.message}")
    
    def record_operation(self, operation_name: str, success: bool = True):
        """
        Record operation execution
        
        Args:
            operation_name: Name of the operation
            success: Whether operation was successful
        """
        self.operation_counters[operation_name] += 1
        
        if not success:
            self.error_counters[operation_name] += 1
    
    def get_metric_statistics(self, metric_name: str) -> Dict[str, float]:
        """
        Get statistical summary of a metric
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Dictionary with statistical summary
        """
        if metric_name not in self.metrics_history:
            return {}
        
        values = [m.value for m in self.metrics_history[metric_name]]
        
        if not values:
            return {}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
        }
    
    def get_error_rate(self, operation_name: str) -> float:
        """
        Calculate error rate for an operation
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Error rate as percentage
        """
        total = self.operation_counters.get(operation_name, 0)
        errors = self.error_counters.get(operation_name, 0)
        
        if total == 0:
            return 0.0
        
        return (errors / total) * 100
    
    def get_throughput(self, operation_name: str, time_window_minutes: int = 60) -> float:
        """
        Calculate throughput for an operation
        
        Args:
            operation_name: Name of the operation
            time_window_minutes: Time window in minutes
            
        Returns:
            Operations per minute
        """
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        # Count operations in time window
        count = 0
        if operation_name in self.metrics_history:
            for metric in self.metrics_history[operation_name]:
                if metric.timestamp >= cutoff_time:
                    count += 1
        
        return count / time_window_minutes if time_window_minutes > 0 else 0.0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary
        
        Returns:
            Dictionary with performance summary
        """
        uptime = datetime.now() - self.start_time
        
        # Calculate overall statistics
        total_operations = sum(self.operation_counters.values())
        total_errors = sum(self.error_counters.values())
        overall_error_rate = (total_errors / total_operations * 100) if total_operations > 0 else 0.0
        
        # Get recent alerts
        recent_alerts = [
            alert for alert in self.alerts[-10:]
            if alert.timestamp >= datetime.now() - timedelta(hours=24)
        ]
        
        # Get current system resources
        current_resources = None
        if self.system_resources:
            current_resources = self.system_resources[-1].to_dict()
        
        return {
            'uptime_seconds': uptime.total_seconds(),
            'total_operations': total_operations,
            'total_errors': total_errors,
            'overall_error_rate': overall_error_rate,
            'active_alerts': len(recent_alerts),
            'recent_alerts': [alert.to_dict() for alert in recent_alerts],
            'current_system_resources': current_resources,
            'operation_counts': dict(self.operation_counters),
            'error_counts': dict(self.error_counters),
            'metric_summaries': {
                name: self.get_metric_statistics(name)
                for name in self.metrics_history.keys()
            }
        }
    
    def export_metrics(self, format: str = 'json') -> str:
        """
        Export metrics to specified format
        
        Args:
            format: Export format ('json', 'csv')
            
        Returns:
            Exported metrics as string
        """
        if format.lower() == 'json':
            return json.dumps(self.get_performance_summary(), indent=2, default=str)
        elif format.lower() == 'csv':
            # Simple CSV export for metrics
            lines = ['metric_name,timestamp,value,unit,type']
            
            for metric_name, metrics in self.metrics_history.items():
                for metric in metrics:
                    lines.append(f"{metric_name},{metric.timestamp},{metric.value},{metric.unit},{metric.metric_type.value}")
            
            return '\n'.join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def reset_metrics(self):
        """Reset all metrics and counters"""
        self.metrics_history.clear()
        self.alerts.clear()
        self.operation_counters.clear()
        self.error_counters.clear()
        self.system_resources.clear()
        self.start_time = datetime.now()
        logger.info("Performance metrics reset")


# Global performance tracker instance
performance_tracker = PerformanceTracker()


def monitor_performance(
    operation_name: str = None,
    track_memory: bool = True,
    track_cpu: bool = False
):
    """
    Decorator to monitor function performance
    
    Args:
        operation_name: Name of the operation (defaults to function name)
        track_memory: Whether to track memory usage
        track_cpu: Whether to track CPU usage
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024 if track_memory else 0
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
                
            except Exception as e:
                success = False
                raise
                
            finally:
                # Record performance metrics
                end_time = time.time()
                processing_time = end_time - start_time
                
                performance_tracker.record_metric(
                    name=f"{op_name}_processing_time",
                    value=processing_time,
                    unit="seconds",
                    metric_type=MetricType.PROCESSING_TIME
                )
                
                if track_memory:
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_used = end_memory - start_memory
                    
                    performance_tracker.record_metric(
                        name=f"{op_name}_memory_usage",
                        value=memory_used,
                        unit="MB",
                        metric_type=MetricType.MEMORY_USAGE
                    )
                
                performance_tracker.record_operation(op_name, success)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024 if track_memory else 0
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
                
            except Exception as e:
                success = False
                raise
                
            finally:
                # Record performance metrics
                end_time = time.time()
                processing_time = end_time - start_time
                
                performance_tracker.record_metric(
                    name=f"{op_name}_processing_time",
                    value=processing_time,
                    unit="seconds",
                    metric_type=MetricType.PROCESSING_TIME
                )
                
                if track_memory:
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_used = end_memory - start_memory
                    
                    performance_tracker.record_metric(
                        name=f"{op_name}_memory_usage",
                        value=memory_used,
                        unit="MB",
                        metric_type=MetricType.MEMORY_USAGE
                    )
                
                performance_tracker.record_operation(op_name, success)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Utility functions
def get_performance_summary() -> Dict[str, Any]:
    """Get current performance summary"""



    return performance_tracker.get_performance_summary()


def start_performance_monitoring(interval: float = 5.0):
    """Start performance monitoring"""
    performance_tracker.start_monitoring(interval)


def stop_performance_monitoring():
    """Stop performance monitoring"""
    performance_tracker.stop_monitoring()


def record_custom_metric(name: str, value: float, unit: str = ""):
    """Record a custom performance metric"""
    performance_tracker.record_metric(name, value, unit)


# Export performance monitoring components
__all__ = [
    'PerformanceTracker',
    'PerformanceMetric',
    'PerformanceAlert',
    'SystemResourceInfo',
    'MetricType',
    'AlertSeverity',
    'performance_tracker',
    'monitor_performance',
    'get_performance_summary',
    'start_performance_monitoring',
    'stop_performance_monitoring',
    'record_custom_metric'
]
