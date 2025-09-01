#!/usr/bin/env python3
"""Metrics Collection Module - Database Replication System
IA Influencer Agent + Content Protection Platform

This module provides comprehensive metrics collection and analysis
for the database replication system serving content creators globally.

Key Features:
- Real-time performance metrics
- Historical trend analysis
- Alerting based on thresholds
- Export to monitoring systems
- Custom metrics for content creator workflows

WARNING: This module handles sensitive performance data.
         Ensure proper access controls and data protection.

Copyright (c) 2024 IA Influencer Agent Team. All rights reserved.

Unauthorized copying, modification, distribution, or use of this software
is strictly prohibited and may be subject to legal action.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
import statistics
import psutil
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """
Types of metrics collected"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


class MetricSeverity(Enum):
    """Severity levels for metric alerts"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: Union[int, float]
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """
Time series of metric data points"""
    name: str
    metric_type: MetricType
    points: List[MetricPoint] = field(default_factory=list)
    unit: str = ""
    description: str = ""
    
    def add_point(self, value: Union[int, float], tags: Optional[Dict[str, str]] = None):
        """Add a new data point"""
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            tags=tags or {}
        )
        self.points.append(point)
        
        # Keep only last 1000 points to prevent memory bloat
        if len(self.points) > 1000:
            self.points = self.points[-1000:]
    
    def get_latest_value(self) -> Optional[Union[int, float]]:
        """
Get the most recent value"""
        return self.points[-1].value if self.points else None
    
    def get_average(self, duration_minutes: int = 60) -> Optional[float]:
        """
Get average value over specified duration"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        recent_points = [
            p.value for p in self.points 
            if p.timestamp >= cutoff_time
        ]
        return statistics.mean(recent_points) if recent_points else None
    
    def get_percentile(self, percentile: float, duration_minutes: int = 60) -> Optional[float]:
        """
Get percentile value over specified duration"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        recent_points = [
            p.value for p in self.points 
            if p.timestamp >= cutoff_time
        ]
        if not recent_points:
            return None
        
        sorted_points = sorted(recent_points)
        index = int(len(sorted_points) * percentile / 100)
        return sorted_points[min(index, len(sorted_points) - 1)]


@dataclass
class MetricAlert:
    """
Metric-based alert configuration"""
    name: str
    metric_name: str
    condition: Callable[[float], bool]
    severity: MetricSeverity
    message: str
    cooldown_minutes: int = 15
    last_triggered: Optional[datetime] = None
    
    def should_trigger(self, value: float) -> bool:
        """
Check if alert should be triggered"""
        if not self.condition(value):
            return False
        
        if self.last_triggered is None:
            return True
        
        cooldown_expires = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
        return datetime.utcnow() > cooldown_expires
    
    def trigger(self):
        """
Mark alert as triggered"""
        self.last_triggered = datetime.utcnow()


class ReplicationMetricsCollector:
    """
    Comprehensive metrics collection for database replication
    
    Collects and analyzes metrics from all replication components
    with focus on content creator platform requirements
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics: Dict[str, MetricSeries] = {}
        self.alerts: List[MetricAlert] = []
        self.handlers: Dict[str, Any] = {}
        self.collection_interval = config.get('collection_interval', 10)
        self.export_interval = config.get('export_interval', 60)
        self.retention_days = config.get('retention_days', 30)
        self.running = False
        self.export_callbacks: List[Callable] = []
        
        # Initialize standard metrics
        self._initialize_standard_metrics()
        self._initialize_alerts()
    
    def _initialize_standard_metrics(self):
        """
Initialize standard replication metrics"""
        standard_metrics = [
            # Replication lag metrics
            ("replication_lag_ms", MetricType.GAUGE, "milliseconds", "Replication lag in milliseconds"),
            ("replication_lag_bytes", MetricType.GAUGE, "bytes", "Replication lag in bytes"),
            
            # Throughput metrics
            ("replication_throughput_ops", MetricType.COUNTER, "operations/sec", "Replication operations per second"),
            ("replication_throughput_bytes", MetricType.COUNTER, "bytes/sec", "Replication bytes per second"),
            
            # Error metrics
            ("replication_errors_total", MetricType.COUNTER, "count", "Total replication errors"),
            ("replication_retries_total", MetricType.COUNTER, "count", "Total replication retries"),
            
            # Health metrics
            ("replication_uptime_seconds", MetricType.GAUGE, "seconds", "Replication uptime in seconds"),
            ("replication_health_score", MetricType.GAUGE, "score", "Overall replication health score (0-100)"),
            
            # Performance metrics
            ("query_latency_ms", MetricType.HISTOGRAM, "milliseconds", "Database query latency"),
            ("connection_pool_utilization", MetricType.GAUGE, "percentage", "Connection pool utilization"),
            
            # Content creator specific metrics
            ("content_uploads_total", MetricType.COUNTER, "count", "Total content uploads"),
            ("protection_alerts_total", MetricType.COUNTER, "count", "Total content protection alerts"),
            ("user_registrations_total", MetricType.COUNTER, "count", "Total user registrations"),
            ("revenue_tracking_updates", MetricType.COUNTER, "count", "Revenue tracking updates"),
            
            # System resource metrics
            ("cpu_usage_percentage", MetricType.GAUGE, "percentage", "CPU usage percentage"),
            ("memory_usage_bytes", MetricType.GAUGE, "bytes", "Memory usage in bytes"),
            ("disk_usage_percentage", MetricType.GAUGE, "percentage", "Disk usage percentage"),
            ("network_io_bytes", MetricType.COUNTER, "bytes/sec", "Network I/O bytes per second"),
        ]
        
        for name, metric_type, unit, description in standard_metrics:
            self.metrics[name] = MetricSeries(
                name=name,
                metric_type=metric_type,
                unit=unit,
                description=description
            )
    
    def _initialize_alerts(self):
        """Initialize metric-based alerts"""
        self.alerts = [
            # High replication lag alerts
            MetricAlert(
                name="high_replication_lag",
                metric_name="replication_lag_ms",
                condition=lambda x: x > 5000,  # 5 seconds
                severity=MetricSeverity.WARNING,
                message="Replication lag is high: {value}ms"
            ),
            MetricAlert(
                name="critical_replication_lag",
                metric_name="replication_lag_ms",
                condition=lambda x: x > 30000,  # 30 seconds
                severity=MetricSeverity.CRITICAL,
                message="Replication lag is critical: {value}ms"
            ),
            
            # Error rate alerts
            MetricAlert(
                name="high_error_rate",
                metric_name="replication_errors_total",
                condition=lambda x: x > 10,  # More than 10 errors per minute
                severity=MetricSeverity.ERROR,
                message="High replication error rate: {value} errors"
            ),
            
            # Health score alerts
            MetricAlert(
                name="low_health_score",
                metric_name="replication_health_score",
                condition=lambda x: x < 80,
                severity=MetricSeverity.WARNING,
                message="Low replication health score: {value}"
            ),
            MetricAlert(
                name="critical_health_score",
                metric_name="replication_health_score",
                condition=lambda x: x < 50,
                severity=MetricSeverity.CRITICAL,
                message="Critical replication health score: {value}"
            ),
            
            # Resource utilization alerts
            MetricAlert(
                name="high_cpu_usage",
                metric_name="cpu_usage_percentage",
                condition=lambda x: x > 80,
                severity=MetricSeverity.WARNING,
                message="High CPU usage: {value}%"
            ),
            MetricAlert(
                name="high_memory_usage",
                metric_name="memory_usage_bytes",
                condition=lambda x: x > 0.85 * psutil.virtual_memory().total,
                severity=MetricSeverity.WARNING,
                message="High memory usage: {value} bytes"
            ),
            MetricAlert(
                name="high_disk_usage",
                metric_name="disk_usage_percentage",
                condition=lambda x: x > 90,
                severity=MetricSeverity.CRITICAL,
                message="High disk usage: {value}%"
            ),
        ]
    
    def register_handler(self, name: str, handler: Any):
        """Register a replication handler for monitoring"""
        self.handlers[name] = handler
        logger.info(f"Registered handler for metrics collection: {name}")
    
    def add_export_callback(self, callback: Callable):
        """Add callback for metric export"""
        self.export_callbacks.append(callback)
    
    def record_metric(self, name: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None):
        """
Record a metric value"""
        if name not in self.metrics:
            logger.warning(f"Unknown metric: {name}")
            return
        
        self.metrics[name].add_point(value, tags)
        
        # Check alerts for this metric
        self._check_alerts(name, value)
    
    def _check_alerts(self, metric_name: str, value: float):
        """Check if any alerts should be triggered"""
        for alert in self.alerts:
            if alert.metric_name == metric_name and alert.should_trigger(value):
                alert.trigger()
                self._handle_alert(alert, value)
    
    def _handle_alert(self, alert: MetricAlert, value: float):
        """
Handle triggered alert"""
        message = alert.message.format(value=value)
        logger.log(
            level=getattr(logging, alert.severity.value.upper()),
            msg=f"ALERT [{alert.severity.value.upper()}] {alert.name}: {message}"
        )
        
        # Additional alert handling could be added here
        # (e.g., send to external monitoring systems)
    
    async def start_collection(self):
        """Start metrics collection"""
        self.running = True
        logger.info("Starting metrics collection")
        
        # Start collection tasks
        tasks = [
            self._collect_replication_metrics(),
            self._collect_system_metrics(),
            self._collect_content_creator_metrics(),
            self._export_metrics_periodically(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_collection(self):
        """Stop metrics collection"""
        self.running = False
        logger.info("Stopping metrics collection")
    
    async def _collect_replication_metrics(self):
        """Collect replication-specific metrics"""
        while self.running:
            try:
                for handler_name, handler in self.handlers.items():
                    # Collect lag metrics
                    if hasattr(handler, 'get_replication_lag'):
                        lag = await handler.get_replication_lag()
                        if lag is not None:
                            self.record_metric(
                                "replication_lag_ms", 
                                lag, 
                                {"handler": handler_name}
                            )
                    
                    # Collect throughput metrics
                    if hasattr(handler, 'get_throughput_stats'):
                        stats = await handler.get_throughput_stats()
                        if stats:
                            self.record_metric(
                                "replication_throughput_ops",
                                stats.get('operations_per_second', 0),
                                {"handler": handler_name}
                            )
                            self.record_metric(
                                "replication_throughput_bytes",
                                stats.get('bytes_per_second', 0),
                                {"handler": handler_name}
                            )
                    
                    # Collect error metrics
                    if hasattr(handler, 'get_error_count'):
                        error_count = await handler.get_error_count()
                        if error_count is not None:
                            self.record_metric(
                                "replication_errors_total",
                                error_count,
                                {"handler": handler_name}
                            )
                    
                    # Collect health metrics
                    if hasattr(handler, 'get_health_score'):
                        health_score = await handler.get_health_score()
                        if health_score is not None:
                            self.record_metric(
                                "replication_health_score",
                                health_score,
                                {"handler": handler_name}
                            )
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error collecting replication metrics: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_system_metrics(self):
        """Collect system resource metrics"""
        while self.running:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.record_metric("cpu_usage_percentage", cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.record_metric("memory_usage_bytes", memory.used)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.record_metric("disk_usage_percentage", disk_percent)
                
                # Network I/O
                network = psutil.net_io_counters()
                self.record_metric("network_io_bytes", network.bytes_sent + network.bytes_recv)
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_content_creator_metrics(self):
        """Collect content creator platform specific metrics"""
        while self.running:
            try:
                # These would typically be collected from application handlers
                # For now, we'll simulate some basic metrics
                
                # Content upload metrics (would come from file storage handler)
                # self.record_metric("content_uploads_total", upload_count)
                
                # Protection alert metrics (would come from protection system)
                # self.record_metric("protection_alerts_total", alert_count)
                
                # User registration metrics (would come from user service)
                # self.record_metric("user_registrations_total", registration_count)
                
                await asyncio.sleep(self.collection_interval * 2)  # Slower collection for these
                
            except Exception as e:
                logger.error(f"Error collecting content creator metrics: {e}")
                await asyncio.sleep(self.collection_interval * 2)
    
    async def _export_metrics_periodically(self):
        """Export metrics to external systems periodically"""
        while self.running:
            try:
                await asyncio.sleep(self.export_interval)
                await self.export_metrics()
                
            except Exception as e:
                logger.error(f"Error in periodic metric export: {e}")
                await asyncio.sleep(self.export_interval)
    
    async def export_metrics(self):
        """Export metrics to configured systems"""
        try:
            # Export to files
            await self._export_to_json()
            
            # Export via callbacks
            for callback in self.export_callbacks:
                try:
                    await callback(self.metrics)
                except Exception as e:
                    logger.error(f"Error in export callback: {e}")
            
            logger.info("Metrics exported successfully")
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
    
    async def _export_to_json(self):
        """Export metrics to JSON files"""
        try:
            export_dir = Path(self.config.get('export_directory', '/tmp/replication_metrics'))
            export_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.utcnow().isoformat()
            export_file = export_dir / f"metrics_{timestamp}.json"
            
            export_data = {
                'timestamp': timestamp,
                'metrics': {}
            }
            
            for name, series in self.metrics.items():
                if series.points:
                    export_data['metrics'][name] = {
                        'type': series.metric_type.value,
                        'unit': series.unit,
                        'description': series.description,
                        'latest_value': series.get_latest_value(),
                        'average_1h': series.get_average(60),
                        'p95_1h': series.get_percentile(95, 60),
                        'p99_1h': series.get_percentile(99, 60),
                    }
            
            async with aiofiles.open(export_file, 'w') as f:
                await f.write(json.dumps(export_data, indent=2))
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            'collection_started': self.running,
            'total_metrics': len(self.metrics),
            'active_alerts': len([a for a in self.alerts if a.last_triggered]),
            'metrics': {}
        }
        
        for name, series in self.metrics.items():
            if series.points:
                summary['metrics'][name] = {
                    'latest_value': series.get_latest_value(),
                    'average_1h': series.get_average(60),
                    'data_points': len(series.points)
                }
        
        return summary
    
    def get_health_dashboard(self) -> Dict[str, Any]:
        """
Get health dashboard data"""
        dashboard = {
            'overall_health': 'unknown',
            'replication_status': {},
            'system_resources': {},
            'recent_alerts': [],
            'key_metrics': {}
        }
        
        # Calculate overall health
        health_scores = []
        for name, series in self.metrics.items():
            if 'health_score' in name:
                latest = series.get_latest_value()
                if latest is not None:
                    health_scores.append(latest)
        
        if health_scores:
            avg_health = statistics.mean(health_scores)
            if avg_health >= 90:
                dashboard['overall_health'] = 'excellent'
            elif avg_health >= 80:
                dashboard['overall_health'] = 'good'
            elif avg_health >= 60:
                dashboard['overall_health'] = 'fair'
            else:
                dashboard['overall_health'] = 'poor'
        
        # Get key metrics
        key_metric_names = [
            'replication_lag_ms',
            'replication_errors_total',
            'cpu_usage_percentage',
            'memory_usage_bytes',
            'content_uploads_total'
        ]
        
        for metric_name in key_metric_names:
            if metric_name in self.metrics:
                series = self.metrics[metric_name]
                dashboard['key_metrics'][metric_name] = {
                    'current': series.get_latest_value(),
                    'average_1h': series.get_average(60)
                }
        
        # Get recent alerts
        dashboard['recent_alerts'] = [
            {
                'name': alert.name,
                'severity': alert.severity.value,
                'last_triggered': alert.last_triggered.isoformat() if alert.last_triggered else None
            }
            for alert in self.alerts
            if alert.last_triggered and alert.last_triggered > datetime.utcnow() - timedelta(hours=1)
        ]
        
        return dashboard
