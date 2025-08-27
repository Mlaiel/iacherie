"""
📈 Performance Monitor - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/data_management/storage/performance_monitor.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

Advanced performance monitoring for storage operations
with real-time analytics and predictive insights.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Sécurité: Fahed Mlaiel
- Microservices: Fahed Mlaiel
- Audio Engineer: Fahed Mlaiel
- DevOps: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import asyncio
import time
import psutil
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import statistics
import json

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of performance metrics"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    QUEUE_SIZE = "queue_size"
    SUCCESS_RATE = "success_rate"
    BANDWIDTH = "bandwidth"
    IOPS = "iops"

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    level: AlertLevel
    message: str
    metric_type: MetricType
    current_value: float
    threshold_value: float
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    metric_type: MetricType
    warning_threshold: float
    error_threshold: float
    critical_threshold: float
    comparison: str = "greater_than"  # greater_than, less_than, equals
    window_size: int = 10  # Number of data points to consider
    enabled: bool = True

class ResourceMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: float = 1.0):
        """Start resource monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_resources,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("Resource monitoring stopped")
    
    def _monitor_resources(self, interval: float):
        """Monitor system resources in background thread"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                
                # Network I/O
                network = psutil.net_io_counters()
                
                # Store metrics (would integrate with main monitor)
                metrics = {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'disk_percent': disk_percent,
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv
                }
                
                # Log high resource usage
                if cpu_percent > 90:
                    logger.warning(f"High CPU usage: {cpu_percent}%")
                if memory_percent > 90:
                    logger.warning(f"High memory usage: {memory_percent}%")
                if disk_percent > 90:
                    logger.warning(f"High disk usage: {disk_percent}%")
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {str(e)}")
                time.sleep(interval)
    
    def get_current_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': (lambda d: (d.used / d.total) * 100)(psutil.disk_usage('/')),
                'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
            }
        except Exception as e:
            logger.error(f"Failed to get resource usage: {str(e)}")
            return {}

class MetricsAggregator:
    """Aggregates and analyzes performance metrics"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics: Dict[MetricType, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.lock = threading.Lock()
    
    def add_metric(self, metric: PerformanceMetric):
        """Add a performance metric"""
        with self.lock:
            self.metrics[metric.metric_type].append(metric)
    
    def get_aggregated_stats(self, metric_type: MetricType, duration_minutes: int = 60) -> Dict[str, float]:
        """Get aggregated statistics for a metric type"""
        with self.lock:
            cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
            recent_metrics = [
                m for m in self.metrics[metric_type]
                if m.timestamp > cutoff_time
            ]
            
            if not recent_metrics:
                return {}
            
            values = [m.value for m in recent_metrics]
            
            return {
                'count': len(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'min': min(values),
                'max': max(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
                'p95': self._percentile(values, 95),
                'p99': self._percentile(values, 99)
            }
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * (percentile / 100.0)
        f = int(k)
        c = k - f
        
        if f == len(sorted_values) - 1:
            return sorted_values[f]
        else:
            return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c
    
    def get_trend_analysis(self, metric_type: MetricType, duration_minutes: int = 60) -> Dict[str, Any]:
        """Analyze trends in metrics"""
        with self.lock:
            cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
            recent_metrics = [
                m for m in self.metrics[metric_type]
                if m.timestamp > cutoff_time
            ]
            
            if len(recent_metrics) < 2:
                return {'trend': 'insufficient_data'}
            
            # Simple linear trend analysis
            values = [m.value for m in recent_metrics]
            times = [(m.timestamp - recent_metrics[0].timestamp).total_seconds() for m in recent_metrics]
            
            # Calculate slope
            if len(values) > 1:
                mean_time = statistics.mean(times)
                mean_value = statistics.mean(values)
                
                numerator = sum((t - mean_time) * (v - mean_value) for t, v in zip(times, values))
                denominator = sum((t - mean_time) ** 2 for t in times)
                
                slope = numerator / denominator if denominator != 0 else 0
                
                if slope > 0.1:
                    trend = 'increasing'
                elif slope < -0.1:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
                
                return {
                    'trend': trend,
                    'slope': slope,
                    'correlation': abs(slope),
                    'data_points': len(values),
                    'time_span_minutes': (times[-1] - times[0]) / 60
                }
            
            return {'trend': 'stable'}

class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.
    
    Features:
    - Real-time metric collection
    - Automatic threshold alerting
    - Trend analysis and prediction
    - Resource usage monitoring
    - Performance bottleneck detection
    - Custom metric support
    - Historical data analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize performance monitor"""
        self.config = config or {}
        
        # Core components
        self.aggregator = MetricsAggregator(window_size=self.config.get('window_size', 10000))
        self.resource_monitor = ResourceMonitor()
        
        # Alerting
        self.thresholds: Dict[MetricType, PerformanceThreshold] = {}
        self.alerts: List[PerformanceAlert] = []
        self.alert_callbacks: List[callable] = []
        
        # Operation tracking
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.operation_history: deque = deque(maxlen=1000)
        
        # Background tasks
        self.monitoring_active = False
        self.background_tasks: List[asyncio.Task] = []
        
        # Performance analytics
        self.analytics_cache: Dict[str, Tuple[Any, datetime]] = {}
        self.cache_ttl = timedelta(minutes=5)
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
        
        logger.info("PerformanceMonitor initialized")
    
    def _initialize_default_thresholds(self):
        """Initialize default performance thresholds"""
        default_thresholds = {
            MetricType.LATENCY: PerformanceThreshold(
                metric_type=MetricType.LATENCY,
                warning_threshold=1.0,  # 1 second
                error_threshold=5.0,    # 5 seconds
                critical_threshold=10.0, # 10 seconds
                comparison="greater_than"
            ),
            MetricType.ERROR_RATE: PerformanceThreshold(
                metric_type=MetricType.ERROR_RATE,
                warning_threshold=0.05,  # 5%
                error_threshold=0.10,    # 10%
                critical_threshold=0.25, # 25%
                comparison="greater_than"
            ),
            MetricType.SUCCESS_RATE: PerformanceThreshold(
                metric_type=MetricType.SUCCESS_RATE,
                warning_threshold=0.95,  # 95%
                error_threshold=0.90,    # 90%
                critical_threshold=0.80, # 80%
                comparison="less_than"
            ),
            MetricType.THROUGHPUT: PerformanceThreshold(
                metric_type=MetricType.THROUGHPUT,
                warning_threshold=10.0,   # 10 ops/sec
                error_threshold=5.0,      # 5 ops/sec
                critical_threshold=1.0,   # 1 op/sec
                comparison="less_than"
            )
        }
        
        self.thresholds.update(default_thresholds)
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Start resource monitoring
        self.resource_monitor.start_monitoring(interval=1.0)
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._threshold_monitor()),
            asyncio.create_task(self._analytics_updater()),
            asyncio.create_task(self._cleanup_old_data())
        ]
        
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        
        # Stop resource monitoring
        self.resource_monitor.stop_monitoring()
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()
        
        logger.info("Performance monitoring stopped")
    
    def record_operation(
        self,
        operation: str,
        success: bool,
        processing_time: float,
        file_size: int = 0,
        tags: Optional[Dict[str, str]] = None
    ):
        """Record a storage operation"""
        timestamp = datetime.now()
        operation_id = f"{operation}_{int(time.time())}"
        
        # Record individual metrics
        self.record_metric(MetricType.LATENCY, processing_time, tags={'operation': operation})
        
        if file_size > 0:
            throughput = file_size / processing_time if processing_time > 0 else 0
            self.record_metric(MetricType.THROUGHPUT, throughput, tags={'operation': operation})
        
        # Update operation tracking
        operation_data = {
            'operation_id': operation_id,
            'operation': operation,
            'success': success,
            'processing_time': processing_time,
            'file_size': file_size,
            'timestamp': timestamp,
            'tags': tags or {}
        }
        
        self.operation_history.append(operation_data)
        
        # Calculate success rate
        recent_ops = [op for op in self.operation_history if op['timestamp'] > timestamp - timedelta(minutes=5)]
        if recent_ops:
            success_rate = sum(1 for op in recent_ops if op['success']) / len(recent_ops)
            self.record_metric(MetricType.SUCCESS_RATE, success_rate, tags={'operation': operation})
            
            error_rate = 1.0 - success_rate
            self.record_metric(MetricType.ERROR_RATE, error_rate, tags={'operation': operation})
    
    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a performance metric"""
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.aggregator.add_metric(metric)
    
    def start_operation(self, operation_id: str, operation_type: str, metadata: Optional[Dict[str, Any]] = None):
        """Start tracking an operation"""
        self.active_operations[operation_id] = {
            'operation_type': operation_type,
            'start_time': time.time(),
            'metadata': metadata or {}
        }
    
    def end_operation(self, operation_id: str, success: bool, file_size: int = 0):
        """End tracking an operation"""
        if operation_id not in self.active_operations:
            logger.warning(f"Operation {operation_id} not found in active operations")
            return
        
        operation_data = self.active_operations.pop(operation_id)
        processing_time = time.time() - operation_data['start_time']
        
        self.record_operation(
            operation=operation_data['operation_type'],
            success=success,
            processing_time=processing_time,
            file_size=file_size,
            tags=operation_data['metadata']
        )
    
    def add_threshold(self, threshold: PerformanceThreshold):
        """Add a performance threshold"""
        self.thresholds[threshold.metric_type] = threshold
        logger.info(f"Added threshold for {threshold.metric_type.value}")
    
    def add_alert_callback(self, callback: callable):
        """Add an alert callback function"""
        self.alert_callbacks.append(callback)
    
    async def get_metrics(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        
        cache_key = f"metrics_{duration_minutes}"
        if cache_key in self.analytics_cache:
            cached_data, cached_time = self.analytics_cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_data
        
        metrics = {}
        
        # Get aggregated stats for each metric type
        for metric_type in MetricType:
            stats = self.aggregator.get_aggregated_stats(metric_type, duration_minutes)
            if stats:
                metrics[metric_type.value] = stats
                
                # Add trend analysis
                trend = self.aggregator.get_trend_analysis(metric_type, duration_minutes)
                metrics[f"{metric_type.value}_trend"] = trend
        
        # Add resource usage
        metrics['resource_usage'] = self.resource_monitor.get_current_usage()
        
        # Add operation statistics
        metrics['operation_stats'] = self._get_operation_statistics(duration_minutes)
        
        # Add alert summary
        metrics['alert_summary'] = self._get_alert_summary()
        
        # Cache results
        self.analytics_cache[cache_key] = (metrics, datetime.now())
        
        return metrics
    
    async def get_performance_report(self, duration_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        report = {
            'report_period_hours': duration_hours,
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'detailed_metrics': {},
            'recommendations': [],
            'alerts': []
        }
        
        # Get metrics for the period
        metrics = await self.get_metrics(duration_hours * 60)
        report['detailed_metrics'] = metrics
        
        # Generate summary
        summary = {}
        
        # Operation performance
        if 'operation_stats' in metrics:
            op_stats = metrics['operation_stats']
            summary['total_operations'] = op_stats.get('total_operations', 0)
            summary['success_rate'] = op_stats.get('success_rate', 0.0)
            summary['avg_processing_time'] = op_stats.get('avg_processing_time', 0.0)
        
        # Resource utilization
        if 'resource_usage' in metrics:
            resource_usage = metrics['resource_usage']
            summary['avg_cpu_usage'] = resource_usage.get('cpu_percent', 0.0)
            summary['avg_memory_usage'] = resource_usage.get('memory_percent', 0.0)
            summary['avg_disk_usage'] = resource_usage.get('disk_percent', 0.0)
        
        # Alert summary
        alert_summary = metrics.get('alert_summary', {})
        summary['total_alerts'] = alert_summary.get('total_alerts', 0)
        summary['critical_alerts'] = alert_summary.get('critical_count', 0)
        
        report['summary'] = summary
        
        # Generate recommendations
        recommendations = self._generate_performance_recommendations(metrics)
        report['recommendations'] = recommendations
        
        # Include recent alerts
        recent_alerts = [
            alert for alert in self.alerts
            if alert.timestamp > datetime.now() - timedelta(hours=duration_hours)
        ]
        report['alerts'] = [
            {
                'alert_id': alert.alert_id,
                'level': alert.level.value,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'resolved': alert.resolved
            }
            for alert in recent_alerts
        ]
        
        return report
    
    def _get_operation_statistics(self, duration_minutes: int) -> Dict[str, Any]:
        """Get operation statistics"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        recent_ops = [op for op in self.operation_history if op['timestamp'] > cutoff_time]
        
        if not recent_ops:
            return {}
        
        total_ops = len(recent_ops)
        successful_ops = sum(1 for op in recent_ops if op['success'])
        
        processing_times = [op['processing_time'] for op in recent_ops]
        file_sizes = [op['file_size'] for op in recent_ops if op['file_size'] > 0]
        
        stats = {
            'total_operations': total_ops,
            'successful_operations': successful_ops,
            'failed_operations': total_ops - successful_ops,
            'success_rate': successful_ops / total_ops if total_ops > 0 else 0.0,
            'avg_processing_time': statistics.mean(processing_times) if processing_times else 0.0,
            'p95_processing_time': self.aggregator._percentile(processing_times, 95) if processing_times else 0.0
        }
        
        if file_sizes:
            stats['avg_file_size_mb'] = statistics.mean(file_sizes) / (1024 * 1024)
            stats['total_data_processed_mb'] = sum(file_sizes) / (1024 * 1024)
        
        # Operation type breakdown
        operation_types = defaultdict(int)
        for op in recent_ops:
            operation_types[op['operation']] += 1
        
        stats['operation_breakdown'] = dict(operation_types)
        
        return stats
    
    def _get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary"""
        active_alerts = [alert for alert in self.alerts if not alert.resolved]
        
        summary = {
            'total_alerts': len(self.alerts),
            'active_alerts': len(active_alerts),
            'resolved_alerts': len(self.alerts) - len(active_alerts)
        }
        
        # Count by level
        level_counts = defaultdict(int)
        for alert in active_alerts:
            level_counts[alert.level.value] += 1
        
        summary.update({
            'info_count': level_counts.get('info', 0),
            'warning_count': level_counts.get('warning', 0),
            'error_count': level_counts.get('error', 0),
            'critical_count': level_counts.get('critical', 0)
        })
        
        return summary
    
    def _generate_performance_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Check latency
        if 'latency' in metrics:
            latency_stats = metrics['latency']
            if latency_stats.get('p95', 0) > 5.0:
                recommendations.append("High latency detected (P95 > 5s). Consider optimizing storage operations.")
        
        # Check error rate
        if 'error_rate' in metrics:
            error_stats = metrics['error_rate']
            if error_stats.get('mean', 0) > 0.1:
                recommendations.append("High error rate detected (>10%). Review error logs and system health.")
        
        # Check resource usage
        resource_usage = metrics.get('resource_usage', {})
        
        if resource_usage.get('cpu_percent', 0) > 80:
            recommendations.append("High CPU usage detected. Consider scaling or optimizing CPU-intensive operations.")
        
        if resource_usage.get('memory_percent', 0) > 80:
            recommendations.append("High memory usage detected. Monitor for memory leaks or consider increasing memory.")
        
        if resource_usage.get('disk_percent', 0) > 80:
            recommendations.append("High disk usage detected. Consider cleaning up old files or expanding storage.")
        
        # Check throughput
        if 'throughput' in metrics:
            throughput_stats = metrics['throughput']
            if throughput_stats.get('mean', 0) < 1.0:
                recommendations.append("Low throughput detected (<1 op/s). Investigate performance bottlenecks.")
        
        # Check trends
        for metric_name in ['latency_trend', 'error_rate_trend']:
            if metric_name in metrics:
                trend = metrics[metric_name]
                if trend.get('trend') == 'increasing':
                    recommendations.append(f"{metric_name.replace('_trend', '').title()} is trending upward. Monitor closely.")
        
        if not recommendations:
            recommendations.append("System performance is within acceptable parameters.")
        
        return recommendations
    
    async def _threshold_monitor(self):
        """Background task to monitor thresholds and generate alerts"""
        while self.monitoring_active:
            try:
                for metric_type, threshold in self.thresholds.items():
                    if not threshold.enabled:
                        continue
                    
                    # Get recent metrics
                    recent_metrics = list(self.aggregator.metrics[metric_type])[-threshold.window_size:]
                    
                    if len(recent_metrics) < threshold.window_size:
                        continue
                    
                    # Calculate current value (average of recent metrics)
                    current_value = statistics.mean([m.value for m in recent_metrics])
                    
                    # Check thresholds
                    alert_level = None
                    threshold_value = None
                    
                    if threshold.comparison == "greater_than":
                        if current_value >= threshold.critical_threshold:
                            alert_level = AlertLevel.CRITICAL
                            threshold_value = threshold.critical_threshold
                        elif current_value >= threshold.error_threshold:
                            alert_level = AlertLevel.ERROR
                            threshold_value = threshold.error_threshold
                        elif current_value >= threshold.warning_threshold:
                            alert_level = AlertLevel.WARNING
                            threshold_value = threshold.warning_threshold
                    
                    elif threshold.comparison == "less_than":
                        if current_value <= threshold.critical_threshold:
                            alert_level = AlertLevel.CRITICAL
                            threshold_value = threshold.critical_threshold
                        elif current_value <= threshold.error_threshold:
                            alert_level = AlertLevel.ERROR
                            threshold_value = threshold.error_threshold
                        elif current_value <= threshold.warning_threshold:
                            alert_level = AlertLevel.WARNING
                            threshold_value = threshold.warning_threshold
                    
                    # Generate alert if threshold exceeded
                    if alert_level and threshold_value is not None:
                        await self._generate_alert(
                            metric_type, alert_level, current_value, threshold_value
                        )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Threshold monitoring error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _generate_alert(
        self,
        metric_type: MetricType,
        level: AlertLevel,
        current_value: float,
        threshold_value: float
    ):
        """Generate a performance alert"""
        
        # Check if similar alert already exists
        existing_alert = None
        for alert in self.alerts:
            if (alert.metric_type == metric_type and 
                alert.level == level and 
                not alert.resolved and
                (datetime.now() - alert.timestamp).total_seconds() < 3600):  # Within last hour
                existing_alert = alert
                break
        
        if existing_alert:
            return  # Don't duplicate recent alerts
        
        alert_id = f"{metric_type.value}_{level.value}_{int(time.time())}"
        
        message = (
            f"{metric_type.value.title()} {level.value}: "
            f"Current value {current_value:.2f} exceeds threshold {threshold_value:.2f}"
        )
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            level=level,
            message=message,
            metric_type=metric_type,
            current_value=current_value,
            threshold_value=threshold_value,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        
        logger.warning(f"Performance alert: {message}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {str(e)}")
    
    async def _analytics_updater(self):
        """Background task to update analytics cache"""
        while self.monitoring_active:
            try:
                # Clear expired cache entries
                current_time = datetime.now()
                expired_keys = [
                    key for key, (_, cached_time) in self.analytics_cache.items()
                    if current_time - cached_time > self.cache_ttl
                ]
                
                for key in expired_keys:
                    del self.analytics_cache[key]
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analytics updater error: {str(e)}")
                await asyncio.sleep(300)
    
    async def _cleanup_old_data(self):
        """Background task to cleanup old data"""
        while self.monitoring_active:
            try:
                # Clean up old alerts (keep last 30 days)
                cutoff_time = datetime.now() - timedelta(days=30)
                self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]
                
                await asyncio.sleep(86400)  # Run daily
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup task error: {str(e)}")
                await asyncio.sleep(86400)

# Export main classes
__all__ = [
    'PerformanceMonitor',
    'PerformanceMetric',
    'PerformanceAlert',
    'PerformanceThreshold',
    'MetricType',
    'AlertLevel',
    'ResourceMonitor',
    'MetricsAggregator'
]
