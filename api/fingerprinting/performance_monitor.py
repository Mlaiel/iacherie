"""IA Influencer Agent - Performance Metrics and Monitoring
Author: Fahed Mlaiel <mlaiel@live.de>

AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée 
sans permission écrite expresse est strictement interdite et 
constituera une violation des droits d'auteur.

Advanced performance monitoring and metrics collection for fingerprinting system
"""

import time
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
from dataclasses import dataclass, field
import threading
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """
Individual metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class PerformanceStats:
    """
Performance statistics container"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0

class MetricsCollector:
    """
    Professional metrics collection system
    Collects and aggregates performance metrics for fingerprinting operations
    """
    
    def __init__(self, max_history: int = 10000):
        """
Initialize metrics collector"""
        self.max_history = max_history
        self.metrics = defaultdict(lambda: deque(maxlen=max_history))
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.timers = {}
        self.lock = threading.RLock()
        
        # Performance tracking
        self.performance_stats = PerformanceStats()
        self.response_times = deque(maxlen=1000)
        self.request_timestamps = deque(maxlen=1000)
        
        logger.info("Metrics collector initialized")
    
    def record_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Record counter metric"""
        with self.lock:
            self.counters[name] += value
            
            metric_point = MetricPoint(
                timestamp=datetime.now(timezone.utc),
                value=value,
                labels=labels or {}
            )
            self.metrics[name].append(metric_point)
    
    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
Record gauge metric"""
        with self.lock:
            self.gauges[name] = value
            
            metric_point = MetricPoint(
                timestamp=datetime.now(timezone.utc),
                value=value,
                labels=labels or {}
            )
            self.metrics[name].append(metric_point)
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
Record histogram metric"""
        with self.lock:
            self.histograms[name].append(value)
            
            metric_point = MetricPoint(
                timestamp=datetime.now(timezone.utc),
                value=value,
                labels=labels or {}
            )
            self.metrics[name].append(metric_point)
    
    def start_timer(self, name: str) -> str:
        """
Start a named timer"""
        timer_id = f"{name}_{int(time.time() * 1000000)}"
        self.timers[timer_id] = time.time()
        return timer_id
    
    def stop_timer(self, timer_id: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Stop a named timer and record duration"""
        if timer_id in self.timers:
            duration = time.time() - self.timers.pop(timer_id)
            
            # Extract metric name from timer_id
            metric_name = '_'.join(timer_id.split('_')[:-1]) + '_duration'
            
            self.record_histogram(metric_name, duration, labels)
            return duration
        return 0.0
    
    def record_request(self, duration: float, success: bool = True):
        """
Record request performance metrics"""
        with self.lock:
            current_time = datetime.now(timezone.utc)
            
            # Update performance stats
            self.performance_stats.total_requests += 1
            if success:
                self.performance_stats.successful_requests += 1
            else:
                self.performance_stats.failed_requests += 1
            
            # Track response times
            self.response_times.append(duration)
            self.request_timestamps.append(current_time)
            
            # Update timing statistics
            if duration < self.performance_stats.min_response_time:
                self.performance_stats.min_response_time = duration
            if duration > self.performance_stats.max_response_time:
                self.performance_stats.max_response_time = duration
            
            # Calculate average response time
            if self.response_times:
                self.performance_stats.average_response_time = sum(self.response_times) / len(self.response_times)
            
            # Calculate requests per second (last minute)
            now = current_time
            minute_ago = now.timestamp() - 60
            recent_requests = sum(1 for ts in self.request_timestamps if ts.timestamp() > minute_ago)
            self.performance_stats.requests_per_second = recent_requests / 60.0
            
            # Calculate error rate
            if self.performance_stats.total_requests > 0:
                self.performance_stats.error_rate = (
                    self.performance_stats.failed_requests / self.performance_stats.total_requests
                )
    
    def get_counter(self, name: str) -> int:
        """
Get counter value"""
        with self.lock:
            return self.counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        """
Get gauge value"""
        with self.lock:
            return self.gauges.get(name, 0.0)
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """
Get histogram statistics"""
        with self.lock:
            values = self.histograms.get(name, [])
            if not values:
                return {}
            
            sorted_values = sorted(values)
            count = len(sorted_values)
            
            return {
                'count': count,
                'min': min(sorted_values),
                'max': max(sorted_values),
                'mean': sum(sorted_values) / count,
                'median': sorted_values[count // 2],
                'p95': sorted_values[int(count * 0.95)] if count > 0 else 0,
                'p99': sorted_values[int(count * 0.99)] if count > 0 else 0
            }
    
    def get_performance_stats(self) -> PerformanceStats:
        """
Get current performance statistics"""
        with self.lock:
            return self.performance_stats
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
Get all collected metrics"""
        with self.lock:
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {name: self.get_histogram_stats(name) for name in self.histograms},
                'performance': self.performance_stats,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def reset_metrics(self):
        """
Reset all metrics"""
        with self.lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.timers.clear()
            self.performance_stats = PerformanceStats()
            self.response_times.clear()
            self.request_timestamps.clear()
        
        logger.info("All metrics reset")

class PerformanceMonitor:
    """
    Advanced performance monitoring system
    Monitors system performance, resource usage, and fingerprinting operations
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        """
Initialize performance monitor"""
        self.metrics = metrics_collector or MetricsCollector()
        self.monitoring_active = False
        self.monitoring_task = None
        self.alert_callbacks = []
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time': 10.0,  # seconds
            'max_error_rate': 0.05,     # 5%
            'min_requests_per_second': 0.1,
            'max_memory_usage': 0.8     # 80%
        }
        
        logger.info("Performance monitor initialized")
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Add callback for performance alerts"""
        self.alert_callbacks.append(callback)
    
    async def start_monitoring(self, interval: int = 30):
        """
Start continuous performance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info(f"Performance monitoring started with {interval}s interval")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self, interval: int):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._collect_system_metrics()
                await self._check_performance_thresholds()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(interval)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.record_gauge('system_cpu_percent', cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.record_gauge('system_memory_percent', memory.percent)
            self.metrics.record_gauge('system_memory_available_gb', memory.available / (1024**3))
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics.record_gauge('system_disk_percent', (disk.used / disk.total) * 100)
            
            # Network I/O
            net_io = psutil.net_io_counters()
            self.metrics.record_counter('system_bytes_sent', net_io.bytes_sent)
            self.metrics.record_counter('system_bytes_received', net_io.bytes_recv)
            
        except ImportError:
            logger.warning("psutil not available, skipping system metrics")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
    
    async def _check_performance_thresholds(self):
        """Check performance thresholds and trigger alerts"""
        try:
            stats = self.metrics.get_performance_stats()
            
            alerts = []
            
            # Check response time
            if stats.average_response_time > self.thresholds['max_response_time']:
                alerts.append({
                    'type': 'high_response_time',
                    'value': stats.average_response_time,
                    'threshold': self.thresholds['max_response_time'],
                    'message': f"Average response time ({stats.average_response_time:.2f}s) exceeds threshold"
                })
            
            # Check error rate
            if stats.error_rate > self.thresholds['max_error_rate']:
                alerts.append({
                    'type': 'high_error_rate',
                    'value': stats.error_rate,
                    'threshold': self.thresholds['max_error_rate'],
                    'message': f"Error rate ({stats.error_rate:.2%}) exceeds threshold"
                })
            
            # Check requests per second
            if stats.requests_per_second < self.thresholds['min_requests_per_second']:
                alerts.append({
                    'type': 'low_throughput',
                    'value': stats.requests_per_second,
                    'threshold': self.thresholds['min_requests_per_second'],
                    'message': f"Requests per second ({stats.requests_per_second:.2f}) below threshold"
                })
            
            # Check memory usage
            memory_percent = self.metrics.get_gauge('system_memory_percent')
            if memory_percent > self.thresholds['max_memory_usage'] * 100:
                alerts.append({
                    'type': 'high_memory_usage',
                    'value': memory_percent / 100,
                    'threshold': self.thresholds['max_memory_usage'],
                    'message': f"Memory usage ({memory_percent:.1f}%) exceeds threshold"
                })
            
            # Trigger alert callbacks
            for alert in alerts:
                for callback in self.alert_callbacks:
                    try:
                        callback(alert['type'], alert)
                    except Exception as e:
                        logger.error(f"Error in alert callback: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error checking performance thresholds: {str(e)}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status"""
        try:
            stats = self.metrics.get_performance_stats()
            all_metrics = self.metrics.get_all_metrics()
            
            # Determine overall health
            health_score = 100.0
            issues = []
            
            # Response time check
            if stats.average_response_time > self.thresholds['max_response_time']:
                health_score -= 20
                issues.append('High response time')
            
            # Error rate check
            if stats.error_rate > self.thresholds['max_error_rate']:
                health_score -= 30
                issues.append('High error rate')
            
            # Memory usage check
            memory_percent = self.metrics.get_gauge('system_memory_percent')
            if memory_percent > self.thresholds['max_memory_usage'] * 100:
                health_score -= 25
                issues.append('High memory usage')
            
            # Throughput check
            if stats.requests_per_second < self.thresholds['min_requests_per_second']:
                health_score -= 15
                issues.append('Low throughput')
            
            health_score = max(0, health_score)
            
            status = 'healthy'
            if health_score < 50:
                status = 'critical'
            elif health_score < 80:
                status = 'warning'
            
            return {
                'status': status,
                'health_score': health_score,
                'issues': issues,
                'performance_stats': stats,
                'system_metrics': {
                    'cpu_percent': self.metrics.get_gauge('system_cpu_percent'),
                    'memory_percent': self.metrics.get_gauge('system_memory_percent'),
                    'disk_percent': self.metrics.get_gauge('system_disk_percent')
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def export_metrics(self, file_path: Path):
        """Export metrics to file"""
        try:
            metrics_data = self.metrics.get_all_metrics()
            
            with open(file_path, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)
            
            logger.info(f"Metrics exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {str(e)}")
            raise

# Global metrics collector and monitor instances
_global_metrics = None
_global_monitor = None

def get_global_metrics() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = MetricsCollector()
    return _global_metrics

def get_global_monitor() -> PerformanceMonitor:
    """
Get global performance monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor(get_global_metrics())
    return _global_monitor

def performance_timer(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """
Decorator for timing function execution"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                metrics = get_global_metrics()
                timer_id = metrics.start_timer(metric_name)
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    metrics.record_request(time.time() - start_time, success=True)
                    return result
                except Exception as e:
                    metrics.record_request(time.time() - start_time, success=False)
                    raise
                finally:
                    metrics.stop_timer(timer_id, labels)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                metrics = get_global_metrics()
                timer_id = metrics.start_timer(metric_name)
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    metrics.record_request(time.time() - start_time, success=True)
                    return result
                except Exception as e:
                    metrics.record_request(time.time() - start_time, success=False)
                    raise
                finally:
                    metrics.stop_timer(timer_id, labels)
            return sync_wrapper
    return decorator
