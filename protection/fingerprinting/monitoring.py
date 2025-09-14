"""📊 Advanced Monitoring & Analytics System for Content Fingerprinting
===================================================================

Enterprise-grade monitoring, metrics collection, and analytics system
for real-time performance tracking and business intelligence.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import statistics
import json
import threading
from pathlib import Path

import psutil
import numpy as np
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import matplotlib.pyplot as plt
import seaborn as sns

from .models import ContentType, ProcessingStatus, ProcessingMetrics, QualityMetrics

logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    """
Types of metrics collected."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertLevel(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """
System alert definition."""
    alert_id: str
    level: AlertLevel
    message: str
    metric_name: str
    threshold: float
    current_value: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class PerformanceReport:
    """
Comprehensive performance report."""
    report_id: str
    period_start: datetime
    period_end: datetime
    total_files_processed: int
    processing_rate_avg: float
    success_rate: float
    error_rate: float
    content_type_breakdown: Dict[str, int]
    performance_trends: Dict[str, List[float]]
    quality_metrics: Dict[str, float]
    resource_utilization: Dict[str, float]
    recommendations: List[str]

class MetricsCollector:
    """
Advanced metrics collection and aggregation system."""
    
    def __init__(self, collection_interval -> None: float = 1.0, max_history -> None: int = 10000) -> None:
        self.collection_interval = collection_interval
        self.max_history = max_history
        
        # Data storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        
        # Prometheus integration
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
        # Collection state
        self.collecting = False
        self.collection_thread = None
        
        # Custom metric handlers
        self.custom_collectors: List[Callable] = []
        
    def _setup_prometheus_metrics(self) -> None:
        """
Setup Prometheus metrics."""
        self.prom_counters = {
            'files_processed_total': Counter(
                'fingerprinting_files_processed_total',
                'Total number of files processed',
                ['content_type', 'status'],
                registry=self.registry
            ),
            'processing_errors_total': Counter(
                'fingerprinting_errors_total',
                'Total number of processing errors',
                ['error_type', 'content_type'],
                registry=self.registry
            )
        }
        
        self.prom_gauges = {
            'active_jobs': Gauge(
                'fingerprinting_active_jobs',
                'Number of active processing jobs',
                registry=self.registry
            ),
            'queue_size': Gauge(
                'fingerprinting_queue_size',
                'Number of items in processing queue',
                ['priority'],
                registry=self.registry
            ),
            'cpu_usage': Gauge(
                'system_cpu_usage_percent',
                'CPU usage percentage',
                registry=self.registry
            ),
            'memory_usage': Gauge(
                'system_memory_usage_percent',
                'Memory usage percentage',
                registry=self.registry
            )
        }
        
        self.prom_histograms = {
            'processing_duration': Histogram(
                'fingerprinting_processing_duration_seconds',
                'Time spent processing files',
                ['content_type'],
                registry=self.registry
            ),
            'similarity_score': Histogram(
                'fingerprinting_similarity_score',
                'Similarity scores for matches',
                ['content_type'],
                buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0],
                registry=self.registry
            )
        }
    
    def start_collection(self) -> None:
        """
Start metrics collection."""
        if self.collecting:
            return
        
        self.collecting = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        logger.info("Metrics collection started")
    
    def stop_collection(self) -> None:
        """Stop metrics collection."""
        self.collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5.0)
        logger.info("Metrics collection stopped")
    
    def _collection_loop(self) -> None:
        """Main collection loop."""
        while self.collecting:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Run custom collectors
                for collector in self.custom_collectors:
                    try:
                        collector()
                    except Exception as e:
                        logger.warning(f"Custom collector failed: {e}")
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
    
    def _collect_system_metrics(self) -> None:
        """Collect system resource metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent()
            self.record_gauge('system.cpu.usage', cpu_percent)
            self.prom_gauges['cpu_usage'].set(cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.record_gauge('system.memory.usage', memory.percent)
            self.record_gauge('system.memory.available_gb', memory.available / (1024**3))
            self.prom_gauges['memory_usage'].set(memory.percent)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.record_gauge('system.disk.read_mb_per_sec', disk_io.read_bytes / (1024**2))
                self.record_gauge('system.disk.write_mb_per_sec', disk_io.write_bytes / (1024**2))
            
            # Network I/O
            net_io = psutil.net_io_counters()
            if net_io:
                self.record_gauge('system.network.sent_mb_per_sec', net_io.bytes_sent / (1024**2))
                self.record_gauge('system.network.recv_mb_per_sec', net_io.bytes_recv / (1024**2))
                
        except Exception as e:
            logger.warning(f"System metrics collection failed: {e}")
    
    def record_counter(self, name -> None: str, value -> None: float = 1.0, labels -> None: Dict[str, str] = None) -> None:
        """Record counter metric."""
        self.counters[name] += value
        self._record_metric(name, value, MetricType.COUNTER, labels)
    
    def record_gauge(self, name -> None: str, value -> None: float, labels -> None: Dict[str, str] = None) -> None:
        """
Record gauge metric."""
        self.gauges[name] = value
        self._record_metric(name, value, MetricType.GAUGE, labels)
    
    def record_histogram(self, name -> None: str, value -> None: float, labels -> None: Dict[str, str] = None) -> None:
        """
Record histogram metric."""
        self.histograms[name].append(value)
        if len(self.histograms[name]) > self.max_history:
            self.histograms[name] = self.histograms[name][-self.max_history:]
        self._record_metric(name, value, MetricType.HISTOGRAM, labels)
    
    def record_timer(self, name -> None: str, duration -> None: float, labels -> None: Dict[str, str] = None) -> None:
        """
Record timing metric."""
        self.record_histogram(f"{name}.duration", duration, labels)
    
    def _record_metric(self, name -> None: str, value -> None: float, metric_type -> None: MetricType, 
                      labels -> None: Dict[str, str] = None) -> None:
        """Record metric point."""
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels or {},
            metadata={'type': metric_type.value}
        )
        self.metrics[name].append(point)
    
    def get_metric_stats(self, name: str, window_minutes: int = 60) -> Dict[str, float]:
        """
Get statistical summary of metric over time window."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        recent_points = [
            point for point in self.metrics[name]
            if point.timestamp > cutoff_time
        ]
        
        if not recent_points:
            return {}
        
        values = [point.value for point in recent_points]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0.0,
            'p95': np.percentile(values, 95),
            'p99': np.percentile(values, 99)
        }
    
    def add_custom_collector(self, collector -> None: Callable) -> None:
        """
Add custom metrics collector function."""
        self.custom_collectors.append(collector)
    
    def get_prometheus_metrics(self) -> str:
        """
Get metrics in Prometheus format."""
        return generate_latest(self.registry).decode('utf-8')

class AlertingSystem:
    """
Intelligent alerting system with configurable thresholds."""
    
    def __init__(self, metrics_collector -> None: MetricsCollector) -> None:
        self.metrics_collector = metrics_collector
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_handlers: List[Callable] = []
        
        # Default alert rules
        self._setup_default_rules()
        
    def _setup_default_rules(self) -> None:
        """
Setup default alerting rules."""
        self.alert_rules = {
            'high_cpu_usage': {
                'metric': 'system.cpu.usage',
                'threshold': 90.0,
                'operator': '>',
                'level': AlertLevel.WARNING,
                'message': 'High CPU usage detected: {value}%'
            },
            'high_memory_usage': {
                'metric': 'system.memory.usage',
                'threshold': 90.0,
                'operator': '>',
                'level': AlertLevel.WARNING,
                'message': 'High memory usage detected: {value}%'
            },
            'low_success_rate': {
                'metric': 'processing.success_rate',
                'threshold': 85.0,
                'operator': '<',
                'level': AlertLevel.ERROR,
                'message': 'Low processing success rate: {value}%'
            },
            'high_error_rate': {
                'metric': 'processing.error_rate',
                'threshold': 10.0,
                'operator': '>',
                'level': AlertLevel.ERROR,
                'message': 'High error rate detected: {value}%'
            }
        }
    
    def add_rule(self, rule_name -> None: str, metric -> None: str, threshold -> None: float, 
                operator -> None: str, level -> None: AlertLevel, message -> None: str) -> None:
        """
Add custom alert rule."""
        self.alert_rules[rule_name] = {
            'metric': metric,
            'threshold': threshold,
            'operator': operator,
            'level': level,
            'message': message
        }
    
    def check_alerts(self) -> None:
        """
Check all alert rules and trigger alerts if needed."""
        for rule_name, rule in self.alert_rules.items():
            try:
                # Get recent metric stats
                stats = self.metrics_collector.get_metric_stats(rule['metric'], window_minutes=5)
                if not stats:
                    continue
                
                current_value = stats['mean']  # Use mean over window
                threshold = rule['threshold']
                operator = rule['operator']
                
                # Check condition
                alert_triggered = False
                if operator == '>' and current_value > threshold:
                    alert_triggered = True
                elif operator == '<' and current_value < threshold:
                    alert_triggered = True
                elif operator == '==' and abs(current_value - threshold) < 0.01:
                    alert_triggered = True
                
                if alert_triggered and rule_name not in self.active_alerts:
                    # Create new alert
                    alert = Alert(
                        alert_id=f"{rule_name}_{int(time.time())}",
                        level=rule['level'],
                        message=rule['message'].format(value=current_value),
                        metric_name=rule['metric'],
                        threshold=threshold,
                        current_value=current_value,
                        timestamp=datetime.utcnow()
                    )
                    
                    self.active_alerts[rule_name] = alert
                    self.alert_history.append(alert)
                    self._send_alert(alert)
                    
                elif not alert_triggered and rule_name in self.active_alerts:
                    # Resolve existing alert
                    alert = self.active_alerts[rule_name]
                    alert.resolved = True
                    del self.active_alerts[rule_name]
                    
            except Exception as e:
                logger.error(f"Alert check failed for rule {rule_name}: {e}")
    
    def _send_alert(self, alert -> None: Alert) -> None:
        """Send alert through configured notification handlers."""
        logger.warning(f"ALERT [{alert.level.value.upper()}]: {alert.message}")
        
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert notification failed: {e}")
    
    def add_notification_handler(self, handler -> None: Callable[[Alert], None]) -> None:
        """Add alert notification handler."""
        self.notification_handlers.append(handler)
    
    def acknowledge_alert(self, alert_id -> None: str) -> None:
        """
Acknowledge an active alert."""
        for alert in self.active_alerts.values():
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                break

class AnalyticsEngine:
    """
Advanced analytics and reporting engine."""
    
    def __init__(self, metrics_collector -> None: MetricsCollector) -> None:
        self.metrics_collector = metrics_collector
        self.reports_cache: Dict[str, PerformanceReport] = {}
        
    def generate_performance_report(self, 
                                  start_time: datetime, 
                                  end_time: datetime) -> PerformanceReport:
        """
Generate comprehensive performance report."""
        
        # Collect metrics for period
        period_metrics = self._collect_period_metrics(start_time, end_time)
        
        # Calculate key statistics
        total_files = period_metrics.get('files_processed', 0)
        success_count = period_metrics.get('successful_processing', 0)
        error_count = period_metrics.get('processing_errors', 0)
        
        success_rate = (success_count / total_files * 100) if total_files > 0 else 0
        error_rate = (error_count / total_files * 100) if total_files > 0 else 0
        
        # Content type breakdown
        content_breakdown = period_metrics.get('content_type_counts', {})
        
        # Performance trends
        trends = self._calculate_trends(start_time, end_time)
        
        # Quality metrics
        quality = self._analyze_quality_metrics(start_time, end_time)
        
        # Resource utilization
        resources = self._analyze_resource_usage(start_time, end_time)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            success_rate, error_rate, resources, trends
        )
        
        report = PerformanceReport(
            report_id=f"report_{int(time.time())}",
            period_start=start_time,
            period_end=end_time,
            total_files_processed=total_files,
            processing_rate_avg=period_metrics.get('avg_processing_rate', 0),
            success_rate=success_rate,
            error_rate=error_rate,
            content_type_breakdown=content_breakdown,
            performance_trends=trends,
            quality_metrics=quality,
            resource_utilization=resources,
            recommendations=recommendations
        )
        
        # Cache report
        self.reports_cache[report.report_id] = report
        
        return report
    
    def _collect_period_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Collect metrics for specific time period."""
        metrics = {}
        
        # Aggregate data from metrics collector
        for metric_name, points in self.metrics_collector.metrics.items():
            period_points = [
                point for point in points
                if start_time <= point.timestamp <= end_time
            ]
            
            if period_points:
                values = [point.value for point in period_points]
                metrics[metric_name] = {
                    'count': len(values),
                    'sum': sum(values),
                    'avg': statistics.mean(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        return metrics
    
    def _calculate_trends(self, start_time: datetime, end_time: datetime) -> Dict[str, List[float]]:
        """
Calculate performance trends over time."""
        trends = {}
        
        # Split period into segments for trend analysis
        period_duration = end_time - start_time
        segment_duration = period_duration / 10  # 10 segments
        
        for i in range(10):
            segment_start = start_time + (segment_duration * i)
            segment_end = start_time + (segment_duration * (i + 1))
            
            # Collect metrics for this segment
            segment_metrics = self._collect_period_metrics(segment_start, segment_end)
            
            # Extract trend values
            for metric_name, stats in segment_metrics.items():
                if metric_name not in trends:
                    trends[metric_name] = []
                trends[metric_name].append(stats.get('avg', 0))
        
        return trends
    
    def _analyze_quality_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, float]:
        """
Analyze quality metrics for the period."""
        quality_stats = self.metrics_collector.get_metric_stats('processing.quality_score', 
                                                               window_minutes=int((end_time - start_time).total_seconds() / 60))
        
        return {
            'avg_quality_score': quality_stats.get('mean', 0),
            'min_quality_score': quality_stats.get('min', 0),
            'max_quality_score': quality_stats.get('max', 0),
            'quality_variance': quality_stats.get('std', 0)
        }
    
    def _analyze_resource_usage(self, start_time: datetime, end_time: datetime) -> Dict[str, float]:
        """
Analyze resource utilization for the period."""
        window_minutes = int((end_time - start_time).total_seconds() / 60)
        
        cpu_stats = self.metrics_collector.get_metric_stats('system.cpu.usage', window_minutes)
        memory_stats = self.metrics_collector.get_metric_stats('system.memory.usage', window_minutes)
        
        return {
            'avg_cpu_usage': cpu_stats.get('mean', 0),
            'max_cpu_usage': cpu_stats.get('max', 0),
            'avg_memory_usage': memory_stats.get('mean', 0),
            'max_memory_usage': memory_stats.get('max', 0)
        }
    
    def _generate_recommendations(self, success_rate: float, error_rate: float,
                                resources: Dict[str, float], trends: Dict[str, List[float]]) -> List[str]:
        """
Generate optimization recommendations."""
        recommendations = []
        
        # Performance recommendations
        if success_rate < 90:
            recommendations.append("Consider optimizing processing algorithms to improve success rate")
        
        if error_rate > 5:
            recommendations.append("High error rate detected - review error logs and add fault tolerance")
        
        # Resource recommendations
        if resources.get('avg_cpu_usage', 0) > 80:
            recommendations.append("High CPU usage - consider horizontal scaling or optimization")
        
        if resources.get('avg_memory_usage', 0) > 80:
            recommendations.append("High memory usage - optimize memory allocation or add more RAM")
        
        # Trend recommendations
        processing_trend = trends.get('processing.rate', [])
        if processing_trend and len(processing_trend) > 5:
            if processing_trend[-1] < processing_trend[0] * 0.8:
                recommendations.append("Processing rate declining - investigate performance degradation")
        
        return recommendations
    
    def create_dashboard_data(self, report: PerformanceReport) -> Dict[str, Any]:
        """Create data structure for dashboard visualization."""
        return {
            'overview': {
                'total_files': report.total_files_processed,
                'success_rate': round(report.success_rate, 2),
                'error_rate': round(report.error_rate, 2),
                'avg_processing_rate': round(report.processing_rate_avg, 2)
            },
            'content_breakdown': report.content_type_breakdown,
            'quality_metrics': report.quality_metrics,
            'resource_usage': report.resource_utilization,
            'trends': report.performance_trends,
            'recommendations': report.recommendations,
            'period': {
                'start': report.period_start.isoformat(),
                'end': report.period_end.isoformat()
            }
        }

class MonitoringDashboard:
    """
Real-time monitoring dashboard generator."""
    
    def __init__(self, metrics_collector -> None: MetricsCollector, analytics_engine -> None: AnalyticsEngine) -> None:
        self.metrics_collector = metrics_collector
        self.analytics_engine = analytics_engine
        
    def generate_realtime_chart(self, metric_name: str, window_minutes: int = 60) -> str:
        """
Generate real-time chart for a metric."""
        # Get metric data
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        points = [
            point for point in self.metrics_collector.metrics[metric_name]
            if point.timestamp > cutoff_time
        ]
        
        if not points:
            return "No data available"
        
        # Create plot
        timestamps = [point.timestamp for point in points]
        values = [point.value for point in points]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, values, linewidth=2)
        plt.title(f'{metric_name} - Last {window_minutes} minutes')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to base64 string for web display
        import io
        import base64
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150)
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_base64}"

# Main monitoring system class
class FingerprintingMonitor:
    """
    Unified monitoring system for content fingerprinting operations.
    
    Features:
    - Real-time metrics collection and visualization
    - Intelligent alerting with configurable rules
    - Performance analytics and trending
    - Resource utilization monitoring
    - Quality assurance tracking
    - Business intelligence reporting
    """
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        
        # Initialize components
        self.metrics_collector = MetricsCollector(
            collection_interval=self.config.get('collection_interval', 1.0),
            max_history=self.config.get('max_history', 10000)
        )
        
        self.alerting_system = AlertingSystem(self.metrics_collector)
        self.analytics_engine = AnalyticsEngine(self.metrics_collector)
        self.dashboard = MonitoringDashboard(self.metrics_collector, self.analytics_engine)
        
        # Monitoring state
        self.running = False
        
    async def start(self) -> None:
        """
Start the monitoring system."""
        if self.running:
            return
        
        self.metrics_collector.start_collection()
        self.running = True
        
        # Start alert checking loop
        asyncio.create_task(self._alert_check_loop())
        
        logger.info("Fingerprinting monitoring system started")
    
    async def stop(self) -> None:
        """Stop the monitoring system."""
        self.running = False
        self.metrics_collector.stop_collection()
        logger.info("Fingerprinting monitoring system stopped")
    
    async def _alert_check_loop(self) -> None:
        """Background loop for checking alerts."""
        while self.running:
            try:
                self.alerting_system.check_alerts()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Alert checking failed: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def record_processing_event(self, content_type -> None: ContentType, status -> None: ProcessingStatus,
                               duration -> None: float, quality_score -> None: float = None) -> None:
        """Record a processing event for monitoring."""
        # Record basic metrics
        self.metrics_collector.record_counter(
            'files_processed_total',
            labels={'content_type': content_type.value, 'status': status.value}
        )
        
        self.metrics_collector.record_timer(
            f'processing_duration.{content_type.value}',
            duration
        )
        
        if quality_score is not None:
            self.metrics_collector.record_histogram(
                'processing.quality_score',
                quality_score,
                labels={'content_type': content_type.value}
            )
        
        # Update Prometheus metrics
        self.metrics_collector.prom_counters['files_processed_total'].labels(
            content_type=content_type.value,
            status=status.value
        ).inc()
        
        self.metrics_collector.prom_histograms['processing_duration'].labels(
            content_type=content_type.value
        ).observe(duration)
    
    def get_system_health(self) -> Dict[str, Any]:
        """
Get overall system health status."""
        return {
            'status': 'healthy' if self.running else 'stopped',
            'active_alerts': len(self.alerting_system.active_alerts),
            'metrics_collected': len(self.metrics_collector.metrics),
            'collection_rate': self.metrics_collector.collection_interval,
            'uptime_seconds': time.time() - getattr(self, 'start_time', time.time())
        }

# Export main classes
__all__ = [
    'FingerprintingMonitor', 'MetricsCollector', 'AlertingSystem', 'AnalyticsEngine',
    'MonitoringDashboard', 'MetricType', 'AlertLevel', 'Alert', 'PerformanceReport'
]
