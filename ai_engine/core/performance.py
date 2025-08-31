"""Advanced Performance Monitoring Module

Enterprise-grade performance monitoring and optimization for industrial AI content platform.
Supports comprehensive monitoring of multi-format content processing workflows.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""
import time
import psutil
import threading
import asyncio
import gc
import resource
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque, defaultdict
from contextlib import contextmanager
from functools import wraps
import statistics
import logging
import json
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Performance level classifications"""    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


class ResourceType(Enum):
    """Types of system resources"""    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    DATABASE = "database"
    CACHE = "cache"


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics data structure"""    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # System metrics
    cpu_usage: float = 0.0
    cpu_count: int = 0
    memory_usage: float = 0.0
    memory_available: float = 0.0
    memory_total: float = 0.0
    disk_usage: float = 0.0
    disk_read_speed: float = 0.0
    disk_write_speed: float = 0.0
    
    # Network metrics
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    network_packets_sent: int = 0
    network_packets_recv: int = 0
    
    # Application metrics
    response_time: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0
    concurrent_requests: int = 0
    queue_size: int = 0
    active_connections: int = 0
    
    # AI-specific metrics
    model_load_time: float = 0.0
    inference_time: float = 0.0
    gpu_memory_usage: float = 0.0
    batch_processing_rate: float = 0.0
    
    # Business metrics
    content_processing_rate: float = 0.0
    protection_checks_per_second: float = 0.0
    collaboration_matches_per_minute: float = 0.0
    revenue_per_hour: float = 0.0
    
    # Quality metrics
    uptime_percentage: float = 100.0
    availability_percentage: float = 100.0
    performance_score: float = 100.0
    sla_compliance: float = 100.0
    
    # Custom metrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""        return {
            "timestamp": self.timestamp.isoformat(),
            "system": {
                "cpu_usage": self.cpu_usage,
                "cpu_count": self.cpu_count,
                "memory_usage": self.memory_usage,
                "memory_available": self.memory_available,
                "memory_total": self.memory_total,
                "disk_usage": self.disk_usage,
                "disk_read_speed": self.disk_read_speed,
                "disk_write_speed": self.disk_write_speed
            },
            "network": {
                "bytes_sent": self.network_bytes_sent,
                "bytes_recv": self.network_bytes_recv,
                "packets_sent": self.network_packets_sent,
                "packets_recv": self.network_packets_recv
            },
            "application": {
                "response_time": self.response_time,
                "throughput": self.throughput,
                "error_rate": self.error_rate,
                "concurrent_requests": self.concurrent_requests,
                "queue_size": self.queue_size,
                "active_connections": self.active_connections
            },
            "ai": {
                "model_load_time": self.model_load_time,
                "inference_time": self.inference_time,
                "gpu_memory_usage": self.gpu_memory_usage,
                "batch_processing_rate": self.batch_processing_rate
            },
            "business": {
                "content_processing_rate": self.content_processing_rate,
                "protection_checks_per_second": self.protection_checks_per_second,
                "collaboration_matches_per_minute": self.collaboration_matches_per_minute,
                "revenue_per_hour": self.revenue_per_hour
            },
            "quality": {
                "uptime_percentage": self.uptime_percentage,
                "availability_percentage": self.availability_percentage,
                "performance_score": self.performance_score,
                "sla_compliance": self.sla_compliance
            },
            "custom": self.custom_metrics
        }
        
    def get_performance_level(self) -> PerformanceLevel:
        """Determine overall performance level"""        score = self.performance_score
        
        if score >= 95:
            return PerformanceLevel.EXCELLENT
        elif score >= 85:
            return PerformanceLevel.GOOD
        elif score >= 70:
            return PerformanceLevel.ACCEPTABLE
        elif score >= 50:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL


@dataclass
class ResourceAlert:
    """Resource usage alert"""    resource_type: ResourceType
    current_usage: float
    threshold: float
    severity: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""        return {
            "resource_type": self.resource_type.value,
            "current_usage": self.current_usage,
            "threshold": self.threshold,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message
        }


class PerformanceProfiler:
    """Advanced performance profiler for detailed analysis"""    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.start_time = None
        self.end_time = None
        self.checkpoints: List[Tuple[str, float]] = []
        self.memory_snapshots: List[Tuple[str, float]] = []
        self.resource_usage: Dict[str, List[float]] = defaultdict(list)
        
    def start(self):
        """Start profiling"""        self.start_time = time.perf_counter()
        self.add_checkpoint("start")
        self.add_memory_snapshot("start")
        
    def add_checkpoint(self, name: str):
        """Add a timing checkpoint"""        if self.start_time is None:
            self.start()
        current_time = time.perf_counter()
        elapsed = current_time - self.start_time
        self.checkpoints.append((name, elapsed))
        
    def add_memory_snapshot(self, name: str):
        """Add memory usage snapshot"""        memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        self.memory_snapshots.append((name, memory_mb))
        
    def track_resource(self, resource_name: str, value: float):
        """Track custom resource usage"""        self.resource_usage[resource_name].append(value)
        
    def end(self) -> Dict[str, Any]:
        """End profiling and return results"""        self.end_time = time.perf_counter()
        self.add_checkpoint("end")
        self.add_memory_snapshot("end")
        
        total_time = self.end_time - self.start_time if self.start_time else 0
        
        return {
            "profile_name": self.profile_name,
            "total_time": total_time,
            "checkpoints": self.checkpoints,
            "memory_snapshots": self.memory_snapshots,
            "resource_usage": dict(self.resource_usage),
            "performance_summary": {
                "avg_memory_mb": statistics.mean([snap[1] for snap in self.memory_snapshots]),
                "peak_memory_mb": max([snap[1] for snap in self.memory_snapshots]),
                "memory_delta_mb": self.memory_snapshots[-1][1] - self.memory_snapshots[0][1] if len(self.memory_snapshots) >= 2 else 0
            }
        }


class PerformanceOptimizer:
    """Automatic performance optimization engine"""    
    def __init__(self):
        self.optimization_rules: List[Callable] = []
        self.optimization_history: List[Dict[str, Any]] = []
        
    def add_optimization_rule(self, rule: Callable[[PerformanceMetrics], Optional[Dict[str, Any]]]):
        """Add optimization rule"""        self.optimization_rules.append(rule)
        
    def analyze_and_optimize(self, metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """Analyze metrics and apply optimizations"""        optimizations = []
        
        for rule in self.optimization_rules:
            try:
                result = rule(metrics)
                if result:
                    optimizations.append(result)
                    self.optimization_history.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "optimization": result,
                        "metrics_snapshot": metrics.to_dict()
                    })
            except Exception as e:
                logger.error(f"Error in optimization rule: {e}")
                
        return optimizations
        
    def get_optimization_suggestions(self, metrics: PerformanceMetrics) -> List[str]:
        """Get optimization suggestions based on current metrics"""        suggestions = []
        
        # CPU optimization suggestions
        if metrics.cpu_usage > 80:
            suggestions.append("Consider scaling horizontally or optimizing CPU-intensive operations")
            
        # Memory optimization suggestions
        if metrics.memory_usage > 85:
            suggestions.append("Memory usage is high. Consider implementing memory pooling or garbage collection optimization")
            
        # Response time optimization
        if metrics.response_time > 5.0:
            suggestions.append("Response time is slow. Consider implementing caching or optimizing database queries")
            
        # Error rate optimization
        if metrics.error_rate > 5:
            suggestions.append("Error rate is high. Review error logs and implement better error handling")
            
        # AI-specific optimizations
        if metrics.inference_time > 2.0:
            suggestions.append("AI inference time is slow. Consider model optimization or GPU utilization")
            
        if metrics.batch_processing_rate < 10:
            suggestions.append("Batch processing rate is low. Consider increasing batch sizes or parallel processing")
            
        return suggestions


class PerformanceMonitor:
    """    Enterprise-grade performance monitoring system
    
    Features:
    - Real-time system monitoring
    - AI workload optimization
    - Automatic performance tuning
    - Advanced alerting system
    - Performance profiling
    - Resource usage prediction
    """    
    def __init__(
        self,
        monitoring_interval: int = 30,
        history_size: int = 1000,
        enable_auto_optimization: bool = True,
        enable_predictions: bool = True
    ):
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        self.enable_auto_optimization = enable_auto_optimization
        self.enable_predictions = enable_predictions
        
        # Core data structures
        self.metrics_history: deque = deque(maxlen=history_size)
        self.active_requests: Dict[str, float] = {}
        self.request_stats: Dict[str, List[float]] = defaultdict(list)
        self.active_profilers: Dict[str, PerformanceProfiler] = {}
        
        # Counters and statistics
        self.total_requests = 0
        self.failed_requests = 0
        self.start_time = time.time()
        self.last_disk_io = None
        self.last_network_io = None
        
        # Threading and concurrency
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._monitor_thread = None
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Advanced components
        self.optimizer = PerformanceOptimizer()
        self.alerts: deque = deque(maxlen=100)
        self.alert_thresholds = self._get_default_thresholds()
        self.alert_callbacks: List[Callable] = []
        
        # Monitoring state
        self.monitoring_enabled = True
        
        # Initialize default optimization rules
        self._setup_optimization_rules()
        
        # Start background monitoring
        if self.monitoring_enabled:
            self._start_monitoring()
            
    def _get_default_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get default alert thresholds"""        return {
            "cpu_usage": {"warning": 70, "critical": 85},
            "memory_usage": {"warning": 80, "critical": 90},
            "disk_usage": {"warning": 85, "critical": 95},
            "response_time": {"warning": 2.0, "critical": 5.0},
            "error_rate": {"warning": 5, "critical": 10},
            "gpu_memory_usage": {"warning": 80, "critical": 90}
        }
        
    def _setup_optimization_rules(self):
        """Setup default optimization rules"""        
        def memory_optimization_rule(metrics: PerformanceMetrics) -> Optional[Dict[str, Any]]:
            if metrics.memory_usage > 85:
                gc.collect()  # Force garbage collection
                return {
                    "type": "memory_optimization",
                    "action": "garbage_collection",
                    "reason": f"Memory usage at {metrics.memory_usage:.1f}%"
                }
            return None
            
        def cpu_optimization_rule(metrics: PerformanceMetrics) -> Optional[Dict[str, Any]]:
            if metrics.cpu_usage > 80 and metrics.concurrent_requests > 50:
                return {
                    "type": "load_balancing",
                    "action": "scale_horizontally",
                    "reason": f"CPU usage at {metrics.cpu_usage:.1f}% with {metrics.concurrent_requests} concurrent requests"
                }
            return None
            
        self.optimizer.add_optimization_rule(memory_optimization_rule)
        self.optimizer.add_optimization_rule(cpu_optimization_rule)
        
    def _start_monitoring(self):
        """Start background monitoring thread"""        if self._monitor_thread is None:
            self._monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self._monitor_thread.start()
            
    def _monitoring_loop(self):
        """Main monitoring loop"""        while not self._stop_event.wait(self.monitoring_interval):
            try:
                metrics = self.collect_metrics()
                
                # Store metrics
                with self._lock:
                    self.metrics_history.append(metrics)
                    
                # Check for alerts
                self._check_alerts(metrics)
                
                # Apply optimizations if enabled
                if self.enable_auto_optimization:
                    optimizations = self.optimizer.analyze_and_optimize(metrics)
                    if optimizations:
                        logger.info(f"Applied {len(optimizations)} performance optimizations")
                        
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                
    def start_request(self, request_id: str, request_type: str = "default") -> None:
        """Start tracking a request with detailed context"""        if not self.monitoring_enabled:
            return
            
        with self._lock:
            self.active_requests[request_id] = time.perf_counter()
            self.total_requests += 1
            
    def end_request(
        self,
        request_id: str,
        success: bool = True,
        request_type: str = "default"
    ) -> float:
        """End tracking a request and return detailed timing"""        if not self.monitoring_enabled:
            return 0.0
            
        with self._lock:
            if request_id in self.active_requests:
                start_time = self.active_requests.pop(request_id)
                response_time = time.perf_counter() - start_time
                
                # Track by request type
                self.request_stats[request_type].append(response_time)
                
                if not success:
                    self.failed_requests += 1
                    
                return response_time
                
        return 0.0
        
    def start_profiler(self, profile_name: str) -> PerformanceProfiler:
        """Start a new performance profiler"""        profiler = PerformanceProfiler(profile_name)
        profiler.start()
        self.active_profilers[profile_name] = profiler
        return profiler
        
    def end_profiler(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """End profiler and get results"""        profiler = self.active_profilers.pop(profile_name, None)
        if profiler:
            return profiler.end()
        return None
        
    @contextmanager
    def profile_operation(self, operation_name: str):
        """Context manager for profiling operations"""        profiler = self.start_profiler(operation_name)
        try:
            yield profiler
        finally:
            result = self.end_profiler(operation_name)
            if result:
                logger.debug(f"Profile completed for {operation_name}: {result['total_time']:.3f}s")
                
    def collect_metrics(self) -> PerformanceMetrics:
        """Collect comprehensive performance metrics"""        if not self.monitoring_enabled:
            return PerformanceMetrics()
            
        try:
            # System metrics
            cpu_count = psutil.cpu_count()
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network_io = psutil.net_io_counters()
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read_speed = 0.0
            disk_write_speed = 0.0
            
            if self.last_disk_io:
                time_delta = time.time() - self.last_disk_io[0]
                if time_delta > 0:
                    disk_read_speed = (disk_io.read_bytes - self.last_disk_io[1]) / time_delta / 1024 / 1024  # MB/s
                    disk_write_speed = (disk_io.write_bytes - self.last_disk_io[2]) / time_delta / 1024 / 1024  # MB/s
                    
            self.last_disk_io = (time.time(), disk_io.read_bytes, disk_io.write_bytes)
            
            # Application metrics
            with self._lock:
                concurrent_requests = len(self.active_requests)
                error_rate = (self.failed_requests / max(self.total_requests, 1)) * 100
                uptime = time.time() - self.start_time
                throughput = self.total_requests / max(uptime, 1)
                
                # Calculate average response time
                all_response_times = []
                for request_type_times in self.request_stats.values():
                    all_response_times.extend(request_type_times[-100:])  # Last 100 requests
                    
                avg_response_time = statistics.mean(all_response_times) if all_response_times else 0.0
                
            # GPU metrics (if available)
            gpu_memory_usage = 0.0
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_memory_usage = gpus[0].memoryUtil * 100
            except ImportError:
                pass  # GPU monitoring not available
                
            # Calculate performance score
            performance_score = self._calculate_performance_score(
                cpu_usage, memory.percent, disk.percent, avg_response_time, error_rate
            )
            
            # Build metrics object
            metrics = PerformanceMetrics(
                cpu_usage=cpu_usage,
                cpu_count=cpu_count,
                memory_usage=memory.percent,
                memory_available=memory.available / 1024 / 1024 / 1024,  # GB
                memory_total=memory.total / 1024 / 1024 / 1024,  # GB
                disk_usage=disk.percent,
                disk_read_speed=disk_read_speed,
                disk_write_speed=disk_write_speed,
                network_bytes_sent=network_io.bytes_sent,
                network_bytes_recv=network_io.bytes_recv,
                network_packets_sent=network_io.packets_sent,
                network_packets_recv=network_io.packets_recv,
                response_time=avg_response_time,
                throughput=throughput,
                error_rate=error_rate,
                concurrent_requests=concurrent_requests,
                gpu_memory_usage=gpu_memory_usage,
                uptime_percentage=(uptime / max(uptime, 1)) * 100,
                performance_score=performance_score
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return PerformanceMetrics()
            
    def _calculate_performance_score(
        self,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        response_time: float,
        error_rate: float
    ) -> float:
        """Calculate overall performance score (0-100)"""        # Weights for different metrics
        weights = {
            "cpu": 0.25,
            "memory": 0.25,
            "disk": 0.15,
            "response_time": 0.20,
            "error_rate": 0.15
        }
        
        # Score each metric (100 = best, 0 = worst)
        cpu_score = max(0, 100 - cpu_usage)
        memory_score = max(0, 100 - memory_usage)
        disk_score = max(0, 100 - disk_usage)
        response_score = max(0, 100 - min(response_time * 20, 100))  # 5s = 0 score
        error_score = max(0, 100 - min(error_rate * 10, 100))  # 10% = 0 score
        
        # Calculate weighted average
        performance_score = (
            cpu_score * weights["cpu"] +
            memory_score * weights["memory"] +
            disk_score * weights["disk"] +
            response_score * weights["response_time"] +
            error_score * weights["error_rate"]
        )
        
        return round(performance_score, 2)
        
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check metrics against alert thresholds"""        for metric_name, thresholds in self.alert_thresholds.items():
            value = getattr(metrics, metric_name, 0)
            
            if value >= thresholds.get("critical", float('inf')):
                self._trigger_alert(metric_name, value, "critical", thresholds["critical"])
            elif value >= thresholds.get("warning", float('inf')):
                self._trigger_alert(metric_name, value, "warning", thresholds["warning"])
                
    def _trigger_alert(self, metric_name: str, value: float, severity: str, threshold: float):
        """Trigger performance alert"""        alert = ResourceAlert(
            resource_type=ResourceType(metric_name.split('_')[0]) if '_' in metric_name else ResourceType.CPU,
            current_usage=value,
            threshold=threshold,
            severity=severity,
            message=f"{metric_name} is {value:.1f}% (threshold: {threshold}%)"
        )
        
        self.alerts.append(alert)
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert.to_dict())
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
                
        # Log alert
        logger.warning(f"Performance alert: {alert.message}")
        
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for performance alerts"""        self.alert_callbacks.append(callback)
        
    def set_alert_threshold(
        self,
        metric_name: str,
        warning_threshold: Optional[float] = None,
        critical_threshold: Optional[float] = None
    ):
        """Set custom alert thresholds"""        if metric_name not in self.alert_thresholds:
            self.alert_thresholds[metric_name] = {}
            
        if warning_threshold is not None:
            self.alert_thresholds[metric_name]["warning"] = warning_threshold
        if critical_threshold is not None:
            self.alert_thresholds[metric_name]["critical"] = critical_threshold
            
    def get_metrics_summary(self, time_range_minutes: int = 60) -> Dict[str, Any]:
        """Get metrics summary for specified time range"""        cutoff_time = datetime.utcnow() - timedelta(minutes=time_range_minutes)
        
        with self._lock:
            recent_metrics = [
                m for m in self.metrics_history
                if m.timestamp >= cutoff_time
            ]
            
        if not recent_metrics:
            return {"error": "No metrics available for specified time range"}
            
        # Calculate aggregations
        cpu_values = [m.cpu_usage for m in recent_metrics]
        memory_values = [m.memory_usage for m in recent_metrics]
        response_times = [m.response_time for m in recent_metrics if m.response_time > 0]
        
        summary = {
            "time_range_minutes": time_range_minutes,
            "metrics_count": len(recent_metrics),
            "cpu_usage": {
                "min": min(cpu_values),
                "max": max(cpu_values),
                "avg": statistics.mean(cpu_values),
                "current": recent_metrics[-1].cpu_usage
            },
            "memory_usage": {
                "min": min(memory_values),
                "max": max(memory_values),
                "avg": statistics.mean(memory_values),
                "current": recent_metrics[-1].memory_usage
            },
            "performance": {
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "throughput": recent_metrics[-1].throughput,
                "error_rate": recent_metrics[-1].error_rate,
                "performance_score": recent_metrics[-1].performance_score
            },
            "alerts_count": len([a for a in self.alerts if a.timestamp >= cutoff_time])
        }
        
        return summary
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""        current_metrics = self.collect_metrics()
        summary = self.get_metrics_summary()
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "current_metrics": current_metrics.to_dict(),
            "summary": summary,
            "optimization_suggestions": self.optimizer.get_optimization_suggestions(current_metrics),
            "recent_alerts": [alert.to_dict() for alert in list(self.alerts)[-10:]],
            "system_health": {
                "performance_level": current_metrics.get_performance_level().value,
                "uptime_hours": (time.time() - self.start_time) / 3600,
                "total_requests": self.total_requests,
                "success_rate": ((self.total_requests - self.failed_requests) / max(self.total_requests, 1)) * 100
            }
        }
        
        return report
        
    def stop(self):
        """Stop performance monitoring"""        self.monitoring_enabled = False
        self._stop_event.set()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            
        self._executor.shutdown(wait=True)


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(
    operation_name: Optional[str] = None,
    alert_on_slow: bool = True,
    slow_threshold: float = 5.0
):
    """    Decorator to monitor function performance
    
    Args:
        operation_name: Name for the operation (defaults to function name)
        alert_on_slow: Whether to alert on slow operations
        slow_threshold: Threshold in seconds for slow operation alert
    """    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            request_id = f"{operation}_{int(time.time() * 1000000)}"
            
            performance_monitor.start_request(request_id, operation)
            
            try:
                result = func(*args, **kwargs)
                response_time = performance_monitor.end_request(request_id, True, operation)
                
                if alert_on_slow and response_time > slow_threshold:
                    logger.warning(
                        f"Slow operation detected: {operation} took {response_time:.3f}s"
                    )
                    
                return result
                
            except Exception as e:
                performance_monitor.end_request(request_id, False, operation)
                raise
                
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            request_id = f"{operation}_{int(time.time() * 1000000)}"
            
            performance_monitor.start_request(request_id, operation)
            
            try:
                result = await func(*args, **kwargs)
                response_time = performance_monitor.end_request(request_id, True, operation)
                
                if alert_on_slow and response_time > slow_threshold:
                    logger.warning(
                        f"Slow async operation detected: {operation} took {response_time:.3f}s"
                    )
                    
                return result
                
            except Exception as e:
                performance_monitor.end_request(request_id, False, operation)
                raise
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator


class SystemMonitor:
    """System-level performance monitoring"""    
    def __init__(self):
        self.monitoring_enabled = True
        self.metrics_history = []
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current system performance metrics"""        try:
            # Collect system metrics
            metrics = PerformanceMetrics()
            
            # Cleanup old metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            return metrics
            
        except Exception as e:
            # Fallback metrics if system monitoring fails
            return PerformanceMetrics(
                custom_metrics={"monitoring_error": str(e)}
            )
    
    def get_average_metrics(self, duration_minutes: int = 5) -> Optional[PerformanceMetrics]:
        """Get average metrics over specified duration"""        if not self.monitoring_enabled or not self.metrics_history:
            return None
            
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return None
        
        # Calculate averages
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_usage for m in recent_metrics) / len(recent_metrics)
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        avg_throughput = sum(m.throughput for m in recent_metrics) / len(recent_metrics)
        avg_error_rate = sum(m.error_rate for m in recent_metrics) / len(recent_metrics)
        
        return PerformanceMetrics(
            cpu_usage=avg_cpu,
            memory_usage=avg_memory,
            disk_usage=avg_disk,
            response_time=avg_response_time,
            throughput=avg_throughput,
            error_rate=avg_error_rate
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""        current_metrics = self.collect_metrics()
        avg_metrics = self.get_average_metrics(5)
        
        uptime = time.time() - self.start_time
        
        summary = {
            "uptime_seconds": uptime,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "success_rate": ((self.total_requests - self.failed_requests) / max(self.total_requests, 1)) * 100,
            "current_metrics": {
                "cpu_usage": current_metrics.cpu_usage,
                "memory_usage": current_metrics.memory_usage,
                "concurrent_requests": current_metrics.concurrent_requests,
                "throughput": current_metrics.throughput
            }
        }
        
        if avg_metrics:
            summary["average_metrics_5min"] = {
                "cpu_usage": avg_metrics.cpu_usage,
                "memory_usage": avg_metrics.memory_usage,
                "response_time": avg_metrics.response_time,
                "error_rate": avg_metrics.error_rate
            }
        
        return summary
    
    def reset_metrics(self) -> None:
        """Reset all metrics"""        with self._lock:
            self.metrics_history.clear()
            self.active_requests.clear()
            self.total_requests = 0
            self.failed_requests = 0
            self.start_time = time.time()
    
    def enable_monitoring(self) -> None:
        """Enable performance monitoring"""        self.monitoring_enabled = True
    
    def disable_monitoring(self) -> None:
        """Disable performance monitoring"""        self.monitoring_enabled = False
    
    def add_custom_metric(self, name: str, value: Any) -> None:
        """Add a custom metric to the latest metrics entry"""        if self.monitoring_enabled and self.metrics_history:
            self.metrics_history[-1].custom_metrics[name] = value


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
