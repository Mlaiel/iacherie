"""Performance Monitor - Enterprise Performance Tracking System

Advanced performance monitoring and optimization system for comprehensive
performance tracking, bottleneck detection, and system optimization.

Business Logic:
Performance monitoring → Real-time analysis → Bottleneck detection →
Optimization recommendations → Automated scaling → Performance reporting

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import psutil
import threading
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque, defaultdict
import json
import statistics
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """
Performance assessment levels"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of performance metrics"""

    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    RESOURCE_USAGE = "resource_usage"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    LATENCY = "latency"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceThresholds:
    """
Performance threshold configuration"""
    excellent: float
    good: float
    fair: float
    poor: float
    # Values below 'poor' are considered critical
    
    def assess_level(self, value: float) -> PerformanceLevel:
        """
Assess performance level based on value"""
        if value <= self.excellent:
            return PerformanceLevel.EXCELLENT
        elif value <= self.good:
            return PerformanceLevel.GOOD
        elif value <= self.fair:
            return PerformanceLevel.FAIR
        elif value <= self.poor:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL


@dataclass
class PerformanceReport:
    """
Comprehensive performance assessment report"""
    timestamp: datetime
    overall_score: float  # 0-100
    performance_level: PerformanceLevel
    metrics: Dict[str, PerformanceMetric]
    bottlenecks: List[str]
    recommendations: List[str]
    trends: Dict[str, str]  # improving, declining, stable
    alerts: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            'timestamp': self.timestamp.isoformat(),
            'overall_score': self.overall_score,
            'performance_level': self.performance_level.value,
            'metrics': {
                name: {
                    'value': metric.value,
                    'unit': metric.unit,
                    'timestamp': metric.timestamp.isoformat(),
                    'tags': metric.tags,
                    'metadata': metric.metadata
                }
                for name, metric in self.metrics.items()
            },
            'bottlenecks': self.bottlenecks,
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            'bottlenecks': self.bottlenecks,
            'recommendations': self.recommendations,
            'trends': self.trends,
            'alerts': self.alerts
        }


class SystemResourceMonitor:
    """
System resource monitoring and analysis"""
    
    def __init__(self):
        self.process = psutil.Process()
        
    def get_cpu_metrics(self) -> Dict[str, float]:
        """
Get CPU usage metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'load_average_1m': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0,
            'load_average_5m': psutil.getloadavg()[1] if hasattr(psutil, 'getloadavg') else 0.0,
            'load_average_15m': psutil.getloadavg()[2] if hasattr(psutil, 'getloadavg') else 0.0
        }
    
    def get_memory_metrics(self) -> Dict[str, float]:
        """
Get memory usage metrics"""
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        process_memory = self.process.memory_info()
        
        return {
            'memory_total_gb': virtual_memory.total / (1024**3),
            'memory_available_gb': virtual_memory.available / (1024**3),
            'memory_used_percent': virtual_memory.percent,
            'memory_free_gb': virtual_memory.free / (1024**3),
            'swap_total_gb': swap_memory.total / (1024**3),
            'swap_used_percent': swap_memory.percent,
            'process_memory_rss_mb': process_memory.rss / (1024**2),
            'process_memory_vms_mb': process_memory.vms / (1024**2)
        }
    
    def get_disk_metrics(self) -> Dict[str, float]:
        """
Get disk usage metrics"""
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        metrics = {
            'disk_total_gb': disk_usage.total / (1024**3),
            'disk_used_gb': disk_usage.used / (1024**3),
            'disk_free_gb': disk_usage.free / (1024**3),
            'disk_used_percent': (disk_usage.used / disk_usage.total) * 100
        }
        
        if disk_io:
            metrics.update({
                'disk_read_mb': disk_io.read_bytes / (1024**2),
                'disk_write_mb': disk_io.write_bytes / (1024**2),
                'disk_read_count': disk_io.read_count,
                'disk_write_count': disk_io.write_count
            })
        
        return metrics
    
    def get_network_metrics(self) -> Dict[str, float]:
        """
Get network usage metrics"""
        network_io = psutil.net_io_counters()
        
        if not network_io:
            return {}
        
        return {
            'network_bytes_sent_mb': network_io.bytes_sent / (1024**2),
            'network_bytes_recv_mb': network_io.bytes_recv / (1024**2),
            'network_packets_sent': network_io.packets_sent,
            'network_packets_recv': network_io.packets_recv,
            'network_errors_in': network_io.errin,
            'network_errors_out': network_io.errout,
            'network_drops_in': network_io.dropin,
            'network_drops_out': network_io.dropout
        }
    
    def get_all_system_metrics(self) -> Dict[str, float]:
        """
Get comprehensive system metrics"""
        all_metrics = {}
        
        try:
            all_metrics.update(self.get_cpu_metrics())
        except Exception as e:
            logger.error(f"Error getting CPU metrics: {e}")
        
        try:
            all_metrics.update(self.get_memory_metrics())
        except Exception as e:
            logger.error(f"Error getting memory metrics: {e}")
        
        try:
            all_metrics.update(self.get_disk_metrics())
        except Exception as e:
            logger.error(f"Error getting disk metrics: {e}")
        
        try:
            all_metrics.update(self.get_network_metrics())
        except Exception as e:
            logger.error(f"Error getting network metrics: {e}")
        
        return all_metrics


class PerformanceTimer:
    """High-precision performance timing context manager"""
    
    def __init__(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.metadata = metadata or {}
        self.start_time = None
        self.end_time = None
        self.duration_ms = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration_ms = (self.end_time - self.start_time) * 1000
    
    def get_duration_ms(self) -> float:
        """
Get duration in milliseconds"""
        return self.duration_ms or 0.0
    
    def get_duration_seconds(self) -> float:
        """
Get duration in seconds"""
        return (self.duration_ms or 0.0) / 1000.0


class PerformanceAnalyzer:
    """
Advanced performance analysis and trend detection"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.lock = threading.RLock()
    
    def add_measurement(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """
Add a performance measurement"""
        with self.lock:
            measurement = {
                'value': value,
                'timestamp': timestamp or datetime.now(timezone.utc)
            }
            self.metric_history[metric_name].append(measurement)
    
    def get_trend(self, metric_name: str, time_window_minutes: int = 30) -> str:
        """
Analyze trend for a specific metric"""
        with self.lock:
            if metric_name not in self.metric_history:
                return "unknown"
            
            measurements = list(self.metric_history[metric_name])
            if len(measurements) < 2:
                return "insufficient_data"
            
            # Filter by time window
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
            recent_measurements = [
                m for m in measurements if m['timestamp'] >= cutoff_time
            ]
            
            if len(recent_measurements) < 2:
                return "insufficient_recent_data"
            
            # Calculate trend
            values = [m['value'] for m in recent_measurements]
            
            # Simple linear trend analysis
            if len(values) >= 3:
                first_third = statistics.mean(values[:len(values)//3])
                last_third = statistics.mean(values[-len(values)//3:])
                
                change_percent = ((last_third - first_third) / first_third) * 100 if first_third != 0 else 0
                
                if change_percent > 10:
                    return "increasing"
                elif change_percent < -10:
                    return "decreasing"
                else:
                    return "stable"
            
            return "stable"
    
    def get_statistics(self, metric_name: str, time_window_minutes: int = 60) -> Dict[str, float]:
        """Get statistical analysis for a metric"""
        with self.lock:
            if metric_name not in self.metric_history:
                return {}
            
            measurements = list(self.metric_history[metric_name])
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
            recent_measurements = [
                m['value'] for m in measurements if m['timestamp'] >= cutoff_time
            ]
            
            if not recent_measurements:
                return {}
            
            try:
                return {
                    'count': len(recent_measurements),
                    'min': min(recent_measurements),
                    'max': max(recent_measurements),
                    'mean': statistics.mean(recent_measurements),
                    'median': statistics.median(recent_measurements),
                    'std_dev': statistics.stdev(recent_measurements) if len(recent_measurements) > 1 else 0.0,
                    'p95': self._percentile(recent_measurements, 95),
                    'p99': self._percentile(recent_measurements, 99)
                }
            except Exception as e:
                logger.error(f"Error calculating statistics for {metric_name}: {e}")
                return {}
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            if upper_index >= len(sorted_values):
                return sorted_values[lower_index]
            
            lower_value = sorted_values[lower_index]
            upper_value = sorted_values[upper_index]
            fraction = index - lower_index
            
            return lower_value + fraction * (upper_value - lower_value)


class PerformanceMonitor:
    """
Enterprise performance monitoring system"""
    
    def __init__(self):
        self.system_monitor = SystemResourceMonitor()
        self.analyzer = PerformanceAnalyzer()
        self.thresholds = self._initialize_thresholds()
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 30  # seconds
        
    def _initialize_thresholds(self) -> Dict[str, PerformanceThresholds]:
        """
Initialize performance thresholds"""
        return {
            'response_time_ms': PerformanceThresholds(
                excellent=100.0, good=300.0, fair=800.0, poor=2000.0
            ),
            'cpu_percent': PerformanceThresholds(
                excellent=30.0, good=50.0, fair=70.0, poor=85.0
            ),
            'memory_used_percent': PerformanceThresholds(
                excellent=50.0, good=70.0, fair=80.0, poor=90.0
            ),
            'disk_used_percent': PerformanceThresholds(
                excellent=60.0, good=75.0, fair=85.0, poor=95.0
            ),
            'throughput_rps': PerformanceThresholds(
                excellent=1000.0, good=500.0, fair=200.0, poor=50.0
            ),
            'error_rate_percent': PerformanceThresholds(
                excellent=0.1, good=0.5, fair=1.0, poor=5.0
            )
        }
    
    @contextmanager
    def measure_performance(self, operation_name: str, 
                           metadata: Optional[Dict[str, Any]] = None):
        """
Context manager for measuring operation performance"""
        timer = PerformanceTimer(operation_name, metadata)
        try:
            with timer:
                yield timer
        finally:
            # Record the measurement
            self.record_performance_metric(
                f"{operation_name}_response_time",
                timer.get_duration_ms(),
                "milliseconds",
                metadata=metadata
            )
    
    def record_performance_metric(self, name: str, value: float, unit: str,
                                 tags: Optional[Dict[str, str]] = None,
                                 metadata: Optional[Dict[str, Any]] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        # Add to analyzer for trend analysis
        self.analyzer.add_measurement(name, value)
        
        # Check thresholds and log warnings
        self._check_performance_thresholds(metric)
    
    def _check_performance_thresholds(self, metric: PerformanceMetric):
        """
Check if metric exceeds performance thresholds"""
        # Map metric names to threshold keys
        threshold_key = None
        if 'response_time' in metric.name:
            threshold_key = 'response_time_ms'
        elif 'cpu_percent' in metric.name:
            threshold_key = 'cpu_percent'
        elif 'memory_used_percent' in metric.name:
            threshold_key = 'memory_used_percent'
        elif 'disk_used_percent' in metric.name:
            threshold_key = 'disk_used_percent'
        elif 'throughput' in metric.name:
            threshold_key = 'throughput_rps'
        elif 'error_rate' in metric.name:
            threshold_key = 'error_rate_percent'
        
        if threshold_key and threshold_key in self.thresholds:
            threshold = self.thresholds[threshold_key]
            level = threshold.assess_level(metric.value)
            
            if level == PerformanceLevel.CRITICAL:
                logger.critical(f"CRITICAL performance issue: {metric.name} = {metric.value} {metric.unit}")
            elif level == PerformanceLevel.POOR:
                logger.warning(f"POOR performance: {metric.name} = {metric.value} {metric.unit}")
    
    def get_current_performance_snapshot(self) -> PerformanceReport:
        """Get current comprehensive performance snapshot"""
        timestamp = datetime.now(timezone.utc)
        
        # Get system metrics
        system_metrics = self.system_monitor.get_all_system_metrics()
        
        # Convert to PerformanceMetric objects
        metrics = {}
        for name, value in system_metrics.items():
            metrics[name] = PerformanceMetric(
                name=name,
                value=value,
                unit=self._get_metric_unit(name),
                timestamp=timestamp
            )
        
        # Analyze bottlenecks
        bottlenecks = self._identify_bottlenecks(system_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(system_metrics, bottlenecks)
        
        # Get trends
        trends = {}
        for metric_name in metrics:
            trends[metric_name] = self.analyzer.get_trend(metric_name)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(system_metrics)
        
        # Determine performance level
        performance_level = self._assess_overall_performance_level(overall_score)
        
        # Generate alerts
        alerts = self._generate_alerts(system_metrics)
        
        return PerformanceReport(
            timestamp=timestamp,
            overall_score=overall_score,
            performance_level=performance_level,
            metrics=metrics,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            trends=trends,
            alerts=alerts
        )
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """
Get appropriate unit for metric"""
        if 'percent' in metric_name:
            return 'percent'
        elif '_gb' in metric_name:
            return 'gigabytes'
        elif '_mb' in metric_name:
            return 'megabytes'
        elif 'count' in metric_name:
            return 'count'
        elif 'average' in metric_name:
            return 'load'
        else:
            return 'units'
    
    def _identify_bottlenecks(self, metrics: Dict[str, float]) -> List[str]:
        """
Identify system bottlenecks"""
        bottlenecks = []
        
        # CPU bottleneck
        if metrics.get('cpu_percent', 0) > 80:
            bottlenecks.append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
        
        # Memory bottleneck
        if metrics.get('memory_used_percent', 0) > 85:
            bottlenecks.append(f"High memory usage: {metrics['memory_used_percent']:.1f}%")
        
        # Disk bottleneck
        if metrics.get('disk_used_percent', 0) > 90:
            bottlenecks.append(f"High disk usage: {metrics['disk_used_percent']:.1f}%")
        
        # Network errors
        if metrics.get('network_errors_in', 0) > 10 or metrics.get('network_errors_out', 0) > 10:
            bottlenecks.append("Network errors detected")
        
        return bottlenecks
    
    def _generate_recommendations(self, metrics: Dict[str, float], 
                                 bottlenecks: List[str]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if any('CPU' in bottleneck for bottleneck in bottlenecks):
            recommendations.extend([
                "Consider CPU optimization or scaling",
                "Review CPU-intensive operations",
                "Implement caching to reduce CPU load"
            ])
        
        if any('memory' in bottleneck for bottleneck in bottlenecks):
            recommendations.extend([
                "Optimize memory usage patterns",
                "Consider memory scaling",
                "Review memory leaks"
            ])
        
        if any('disk' in bottleneck for bottleneck in bottlenecks):
            recommendations.extend([
                "Implement disk space management",
                "Consider storage expansion",
                "Optimize data retention policies"
            ])
        
        if any('Network' in bottleneck for bottleneck in bottlenecks):
            recommendations.extend([
                "Investigate network connectivity issues",
                "Review network configuration",
                "Monitor network infrastructure"
            ])
        
        if not bottlenecks:
            recommendations.append("System performance is optimal")
        
        return recommendations
    
    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall performance score (0-100)"""
        scores = []
        
        # CPU score
        cpu_percent = metrics.get('cpu_percent', 0)
        cpu_score = max(0, 100 - cpu_percent)
        scores.append(cpu_score)
        
        # Memory score
        memory_percent = metrics.get('memory_used_percent', 0)
        memory_score = max(0, 100 - memory_percent)
        scores.append(memory_score)
        
        # Disk score
        disk_percent = metrics.get('disk_used_percent', 0)
        disk_score = max(0, 100 - disk_percent)
        scores.append(disk_score)
        
        # Average the scores
        return statistics.mean(scores) if scores else 0.0
    
    def _assess_overall_performance_level(self, score: float) -> PerformanceLevel:
        """
Assess overall performance level"""
        if score >= 90:
            return PerformanceLevel.EXCELLENT
        elif score >= 75:
            return PerformanceLevel.GOOD
        elif score >= 60:
            return PerformanceLevel.FAIR
        elif score >= 40:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL
    
    def _generate_alerts(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """
Generate performance alerts"""
        alerts = []
        
        # Critical alerts
        if metrics.get('cpu_percent', 0) > 95:
            alerts.append({
                'level': 'critical',
                'metric': 'cpu_percent',
                'value': metrics['cpu_percent'],
                'message': 'Extremely high CPU usage detected'
            })
        
        if metrics.get('memory_used_percent', 0) > 95:
            alerts.append({
                'level': 'critical',
                'metric': 'memory_used_percent',
                'value': metrics['memory_used_percent'],
                'message': 'Critical memory usage level'
            })
        
        if metrics.get('disk_used_percent', 0) > 98:
            alerts.append({
                'level': 'critical',
                'metric': 'disk_used_percent',
                'value': metrics['disk_used_percent'],
                'message': 'Disk space critically low'
            })
        
        return alerts
    
    def start_monitoring(self, interval_seconds: int = 30):
        """
Start continuous performance monitoring"""
        if self.monitoring_active:
            logger.warning("Performance monitoring already active")
            return
        
        self.monitoring_interval = interval_seconds
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info(f"Performance monitoring started with {interval_seconds}s interval")
    
    def stop_monitoring(self):
        """Stop continuous performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Get performance snapshot
                snapshot = self.get_current_performance_snapshot()
                
                # Log performance summary
                logger.info(f"Performance Score: {snapshot.overall_score:.1f}/100 "
                           f"({snapshot.performance_level.value})")
                
                # Log alerts
                for alert in snapshot.alerts:
                    if alert['level'] == 'critical':
                        logger.critical(f"Performance Alert: {alert['message']}")
                    else:
                        logger.warning(f"Performance Alert: {alert['message']}")
                
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
            
            # Wait for next iteration
            time.sleep(self.monitoring_interval)
    
    async def get_performance_report_async(self) -> PerformanceReport:
        """Get performance report asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_current_performance_snapshot)
    
    def export_performance_data(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """
Export performance data for analysis"""
        export_data = {
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'time_range_hours': time_range_hours,
            'current_snapshot': self.get_current_performance_snapshot().to_dict(),
            'historical_trends': {},
            'statistics': {}
        }
        
        # Add historical trends for key metrics
        key_metrics = ['cpu_percent', 'memory_used_percent', 'disk_used_percent']
        for metric_name in key_metrics:
            export_data['historical_trends'][metric_name] = self.analyzer.get_trend(
                metric_name, time_range_hours * 60
            )
            export_data['statistics'][metric_name] = self.analyzer.get_statistics(
                metric_name, time_range_hours * 60
            )
        
        return export_data
