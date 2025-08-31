#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cache Monitoring - Real-time Cache Performance Monitoring
=========================================================

Advanced monitoring system for cache performance tracking,
alerting, and real-time analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""import asyncio
import logging
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
import collections
import weakref

from ...core.config import get_settings
from ...core.utils import generate_uuid, get_timestamp

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class MetricType(Enum):
    """Monitoring metric types."""    HIT_RATE = "hit_rate"
    MISS_RATE = "miss_rate"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    ERROR_RATE = "error_rate"
    CACHE_SIZE = "cache_size"
    EVICTION_RATE = "eviction_rate"
    NETWORK_IO = "network_io"

class MonitoringStatus(Enum):
    """Monitoring system status."""    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class MetricData:
    """Metric data point."""    metric_type: MetricType
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Monitoring alert."""    alert_id: str
    severity: AlertSeverity
    metric_type: MetricType
    message: str
    value: float
    threshold: float
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Threshold:
    """Monitoring threshold."""    metric_type: MetricType
    operator: str  # >, <, >=, <=, ==, !=
    value: float
    severity: AlertSeverity
    duration_seconds: int = 0  # Alert only after duration
    enabled: bool = True

class CacheMonitor:
    """    Advanced cache monitoring system.
    
    Features:
    - Real-time metrics collection
    - Threshold-based alerting
    - Performance analytics
    - Health monitoring
    - Custom dashboards
    """    
    def __init__(self, collection_interval: int = 10,
                 retention_hours: int = 24,
                 alert_handlers: Optional[List[Callable]] = None):
        """        Initialize cache monitor.
        
        Args:
            collection_interval: Metrics collection interval in seconds
            retention_hours: Metrics retention period
            alert_handlers: Custom alert handlers
        """        self.collection_interval = collection_interval
        self.retention_hours = retention_hours
        self.alert_handlers = alert_handlers or []
        self.logger = logging.getLogger(f"{__name__}.CacheMonitor")
        
        # Metrics storage
        self.metrics: Dict[MetricType, List[MetricData]] = {
            metric_type: [] for metric_type in MetricType
        }
        self.metrics_lock = threading.Lock()
        
        # Alert management
        self.alerts: List[Alert] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.thresholds: List[Threshold] = []
        self.alert_lock = threading.Lock()
        
        # Monitoring state
        self.status = MonitoringStatus.STOPPED
        self.collection_task: Optional[asyncio.Task] = None
        self.alert_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            'total_metrics_collected': 0,
            'total_alerts_generated': 0,
            'monitoring_uptime': 0.0,
            'last_collection': None
        }
        
        # Collectors
        self.metric_collectors: Dict[MetricType, Callable] = {}
        self.custom_collectors: List[Callable] = []
        
        # Health tracking
        self.health_status = "unknown"
        self.health_components: Dict[str, str] = {}
        
        self.logger.info("Cache monitor initialized")
    
    async def register_metric_collector(self, metric_type: MetricType, 
                                      collector: Callable) -> None:
        """Register custom metric collector."""        self.metric_collectors[metric_type] = collector
        self.logger.debug(f"Registered collector for {metric_type.value}")
    
    async def add_custom_collector(self, collector: Callable) -> None:
        """Add custom metric collector."""        self.custom_collectors.append(collector)
        self.logger.debug("Added custom metric collector")
    
    async def add_threshold(self, metric_type: MetricType, operator: str,
                          value: float, severity: AlertSeverity,
                          duration_seconds: int = 0) -> None:
        """Add monitoring threshold."""        threshold = Threshold(
            metric_type=metric_type,
            operator=operator,
            value=value,
            severity=severity,
            duration_seconds=duration_seconds
        )
        
        self.thresholds.append(threshold)
        self.logger.info(f"Added threshold: {metric_type.value} {operator} {value}")
    
    async def remove_threshold(self, metric_type: MetricType) -> bool:
        """Remove monitoring threshold."""        original_count = len(self.thresholds)
        self.thresholds = [t for t in self.thresholds if t.metric_type != metric_type]
        removed = len(self.thresholds) < original_count
        
        if removed:
            self.logger.info(f"Removed threshold for {metric_type.value}")
        
        return removed
    
    async def record_metric(self, metric_type: MetricType, value: float,
                          labels: Optional[Dict[str, str]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record metric data point."""        try:
            metric = MetricData(
                metric_type=metric_type,
                value=value,
                timestamp=datetime.now(),
                labels=labels or {},
                metadata=metadata or {}
            )
            
            with self.metrics_lock:
                self.metrics[metric_type].append(metric)
                self.stats['total_metrics_collected'] += 1
                
                # Clean old metrics
                cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
                self.metrics[metric_type] = [
                    m for m in self.metrics[metric_type]
                    if m.timestamp >= cutoff_time
                ]
            
            # Check thresholds
            await self._check_thresholds(metric)
            
        except Exception as e:
            self.logger.error(f"Error recording metric: {e}")
    
    async def _check_thresholds(self, metric: MetricData) -> None:
        """Check metric against thresholds."""        try:
            for threshold in self.thresholds:
                if not threshold.enabled or threshold.metric_type != metric.metric_type:
                    continue
                
                violation = False
                
                if threshold.operator == ">":
                    violation = metric.value > threshold.value
                elif threshold.operator == "<":
                    violation = metric.value < threshold.value
                elif threshold.operator == ">=":
                    violation = metric.value >= threshold.value
                elif threshold.operator == "<=":
                    violation = metric.value <= threshold.value
                elif threshold.operator == "==":
                    violation = metric.value == threshold.value
                elif threshold.operator == "!=":
                    violation = metric.value != threshold.value
                
                if violation:
                    # Check duration if specified
                    if threshold.duration_seconds > 0:
                        if not await self._check_duration_violation(threshold):
                            continue
                    
                    await self._create_alert(threshold, metric)
            
        except Exception as e:
            self.logger.error(f"Error checking thresholds: {e}")
    
    async def _check_duration_violation(self, threshold: Threshold) -> bool:
        """Check if threshold violation persists for required duration."""        try:
            cutoff_time = datetime.now() - timedelta(seconds=threshold.duration_seconds)
            
            with self.metrics_lock:
                recent_metrics = [
                    m for m in self.metrics[threshold.metric_type]
                    if m.timestamp >= cutoff_time
                ]
            
            # Check if all recent values violate threshold
            for metric in recent_metrics:
                violation = False
                
                if threshold.operator == ">":
                    violation = metric.value > threshold.value
                elif threshold.operator == "<":
                    violation = metric.value < threshold.value
                elif threshold.operator == ">=":
                    violation = metric.value >= threshold.value
                elif threshold.operator == "<=":
                    violation = metric.value <= threshold.value
                elif threshold.operator == "==":
                    violation = metric.value == threshold.value
                elif threshold.operator == "!=":
                    violation = metric.value != threshold.value
                
                if not violation:
                    return False
            
            return len(recent_metrics) > 0
            
        except Exception as e:
            self.logger.error(f"Error checking duration violation: {e}")
            return False
    
    async def _create_alert(self, threshold: Threshold, metric: MetricData) -> None:
        """Create alert for threshold violation."""        try:
            alert_key = f"{threshold.metric_type.value}_{threshold.operator}_{threshold.value}"
            
            # Avoid duplicate alerts
            with self.alert_lock:
                if alert_key in self.active_alerts:
                    return
            
            alert = Alert(
                alert_id=generate_uuid(),
                severity=threshold.severity,
                metric_type=threshold.metric_type,
                message=f"{threshold.metric_type.value} {threshold.operator} {threshold.value} (current: {metric.value})",
                value=metric.value,
                threshold=threshold.value,
                labels=metric.labels,
                metadata=metric.metadata
            )
            
            with self.alert_lock:
                self.alerts.append(alert)
                self.active_alerts[alert_key] = alert
                self.stats['total_alerts_generated'] += 1
            
            # Notify alert handlers
            for handler in self.alert_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(alert)
                    else:
                        handler(alert)
                except Exception as e:
                    self.logger.error(f"Alert handler error: {e}")
            
            self.logger.warning(f"Alert created: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert."""        try:
            with self.alert_lock:
                for alert in self.alerts:
                    if alert.alert_id == alert_id and not alert.acknowledged_at:
                        alert.acknowledged_at = datetime.now()
                        self.logger.info(f"Alert {alert_id} acknowledged")
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert."""        try:
            with self.alert_lock:
                for alert in self.alerts:
                    if alert.alert_id == alert_id and not alert.resolved_at:
                        alert.resolved_at = datetime.now()
                        
                        # Remove from active alerts
                        alert_key = f"{alert.metric_type.value}_{alert.threshold}"
                        if alert_key in self.active_alerts:
                            del self.active_alerts[alert_key]
                        
                        self.logger.info(f"Alert {alert_id} resolved")
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}")
            return False
    
    async def start_monitoring(self) -> None:
        """Start monitoring process."""        if self.status == MonitoringStatus.ACTIVE:
            return
        
        self.status = MonitoringStatus.ACTIVE
        
        # Start collection task
        self.collection_task = asyncio.create_task(self._collection_loop())
        
        # Start alert management task
        self.alert_task = asyncio.create_task(self._alert_management_loop())
        
        self.logger.info("Cache monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring process."""        self.status = MonitoringStatus.STOPPED
        
        # Cancel tasks
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
            self.collection_task = None
        
        if self.alert_task:
            self.alert_task.cancel()
            try:
                await self.alert_task
            except asyncio.CancelledError:
                pass
            self.alert_task = None
        
        self.logger.info("Cache monitoring stopped")
    
    async def pause_monitoring(self) -> None:
        """Pause monitoring process."""        self.status = MonitoringStatus.PAUSED
        self.logger.info("Cache monitoring paused")
    
    async def resume_monitoring(self) -> None:
        """Resume monitoring process."""        if self.status == MonitoringStatus.PAUSED:
            self.status = MonitoringStatus.ACTIVE
            self.logger.info("Cache monitoring resumed")
    
    async def _collection_loop(self) -> None:
        """Main metrics collection loop."""        start_time = time.time()
        
        while True:
            try:
                if self.status != MonitoringStatus.ACTIVE:
                    await asyncio.sleep(1)
                    continue
                
                # Collect metrics
                await self._collect_metrics()
                
                self.stats['monitoring_uptime'] = time.time() - start_time
                self.stats['last_collection'] = datetime.now()
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Collection loop error: {e}")
                self.status = MonitoringStatus.ERROR
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_metrics(self) -> None:
        """Collect all metrics."""        try:
            # Collect standard metrics
            for metric_type, collector in self.metric_collectors.items():
                try:
                    if asyncio.iscoroutinefunction(collector):
                        value = await collector()
                    else:
                        value = collector()
                    
                    await self.record_metric(metric_type, value)
                    
                except Exception as e:
                    self.logger.error(f"Error collecting {metric_type.value}: {e}")
            
            # Collect custom metrics
            for collector in self.custom_collectors:
                try:
                    if asyncio.iscoroutinefunction(collector):
                        await collector(self)
                    else:
                        collector(self)
                except Exception as e:
                    self.logger.error(f"Custom collector error: {e}")
            
            # Update health status
            await self._update_health_status()
            
        except Exception as e:
            self.logger.error(f"Error in metrics collection: {e}")
    
    async def _update_health_status(self) -> None:
        """Update overall health status."""        try:
            # Simple health check based on active alerts
            critical_alerts = [
                alert for alert in self.active_alerts.values()
                if alert.severity == AlertSeverity.CRITICAL and not alert.resolved_at
            ]
            
            high_alerts = [
                alert for alert in self.active_alerts.values()
                if alert.severity == AlertSeverity.HIGH and not alert.resolved_at
            ]
            
            if critical_alerts:
                self.health_status = "critical"
            elif high_alerts:
                self.health_status = "degraded"
            elif self.active_alerts:
                self.health_status = "warning"
            else:
                self.health_status = "healthy"
            
            # Update component health
            self.health_components = {
                'monitoring': 'healthy' if self.status == MonitoringStatus.ACTIVE else 'unhealthy',
                'alerting': 'healthy' if len(critical_alerts) == 0 else 'critical',
                'metrics_collection': 'healthy' if self.stats['last_collection'] else 'unknown'
            }
            
        except Exception as e:
            self.logger.error(f"Error updating health status: {e}")
            self.health_status = "unknown"
    
    async def _alert_management_loop(self) -> None:
        """Alert management background task."""        while True:
            try:
                if self.status != MonitoringStatus.ACTIVE:
                    await asyncio.sleep(10)
                    continue
                
                # Auto-resolve alerts that are no longer active
                await self._auto_resolve_alerts()
                
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(60)  # Run every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Alert management error: {e}")
    
    async def _auto_resolve_alerts(self) -> None:
        """Auto-resolve alerts that are no longer active."""        try:
            current_time = datetime.now()
            
            with self.alert_lock:
                for alert_key, alert in list(self.active_alerts.items()):
                    if alert.resolved_at:
                        continue
                    
                    # Check if condition is still violated
                    threshold = None
                    for t in self.thresholds:
                        if (t.metric_type == alert.metric_type and 
                            t.value == alert.threshold):
                            threshold = t
                            break
                    
                    if not threshold:
                        continue
                    
                    # Get recent metrics
                    with self.metrics_lock:
                        recent_metrics = [
                            m for m in self.metrics[alert.metric_type]
                            if m.timestamp >= current_time - timedelta(minutes=5)
                        ]
                    
                    if not recent_metrics:
                        continue
                    
                    # Check if violation persists
                    violation_persists = False
                    for metric in recent_metrics[-3:]:  # Check last 3 values
                        if threshold.operator == ">":
                            violation_persists = metric.value > threshold.value
                        elif threshold.operator == "<":
                            violation_persists = metric.value < threshold.value
                        # Add other operators as needed
                        
                        if violation_persists:
                            break
                    
                    if not violation_persists:
                        alert.resolved_at = current_time
                        del self.active_alerts[alert_key]
                        self.logger.info(f"Auto-resolved alert {alert.alert_id}")
            
        except Exception as e:
            self.logger.error(f"Error in auto-resolve alerts: {e}")
    
    async def _cleanup_old_alerts(self) -> None:
        """Clean up old resolved alerts."""        try:
            cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
            
            with self.alert_lock:
                original_count = len(self.alerts)
                self.alerts = [
                    alert for alert in self.alerts
                    if (alert.resolved_at is None or alert.resolved_at >= cutoff_time)
                ]
                
                cleaned_count = original_count - len(self.alerts)
                if cleaned_count > 0:
                    self.logger.debug(f"Cleaned up {cleaned_count} old alerts")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up alerts: {e}")
    
    async def get_metrics_summary(self, metric_type: Optional[MetricType] = None,
                                time_range_hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary."""        try:
            cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
            summary = {}
            
            metric_types = [metric_type] if metric_type else list(MetricType)
            
            with self.metrics_lock:
                for mtype in metric_types:
                    metrics = [
                        m for m in self.metrics[mtype]
                        if m.timestamp >= cutoff_time
                    ]
                    
                    if metrics:
                        values = [m.value for m in metrics]
                        summary[mtype.value] = {
                            'count': len(values),
                            'min': min(values),
                            'max': max(values),
                            'mean': statistics.mean(values),
                            'median': statistics.median(values),
                            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                            'latest': values[-1],
                            'timestamp_range': {
                                'start': metrics[0].timestamp.isoformat(),
                                'end': metrics[-1].timestamp.isoformat()
                            }
                        }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting metrics summary: {e}")
            return {}
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts."""        try:
            with self.alert_lock:
                return [
                    {
                        'alert_id': alert.alert_id,
                        'severity': alert.severity.value,
                        'metric_type': alert.metric_type.value,
                        'message': alert.message,
                        'value': alert.value,
                        'threshold': alert.threshold,
                        'created_at': alert.created_at.isoformat(),
                        'acknowledged': alert.acknowledged_at is not None,
                        'labels': alert.labels
                    }
                    for alert in self.active_alerts.values()
                ]
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring system status."""        try:
            with self.metrics_lock:
                total_metrics = sum(len(metrics) for metrics in self.metrics.values())
            
            with self.alert_lock:
                active_alert_count = len(self.active_alerts)
                total_alert_count = len(self.alerts)
            
            return {
                'status': self.status.value,
                'health_status': self.health_status,
                'health_components': self.health_components,
                'collection_interval': self.collection_interval,
                'retention_hours': self.retention_hours,
                'total_metrics': total_metrics,
                'active_alerts': active_alert_count,
                'total_alerts': total_alert_count,
                'threshold_count': len(self.thresholds),
                'stats': self.stats,
                'uptime_seconds': self.stats['monitoring_uptime']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring status: {e}")
            return {}

class AlertManager:
    """Manage alert notifications and escalations."""    
    def __init__(self):
        """Initialize alert manager."""        self.notification_channels: List[Callable] = []
        self.escalation_rules: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"{__name__}.AlertManager")
    
    async def add_notification_channel(self, handler: Callable) -> None:
        """Add notification channel."""        self.notification_channels.append(handler)
    
    async def handle_alert(self, alert: Alert) -> None:
        """Handle alert notification."""        try:
            for channel in self.notification_channels:
                try:
                    if asyncio.iscoroutinefunction(channel):
                        await channel(alert)
                    else:
                        channel(alert)
                except Exception as e:
                    self.logger.error(f"Notification channel error: {e}")
        
        except Exception as e:
            self.logger.error(f"Error handling alert: {e}")

class MetricsExporter:
    """Export metrics to external systems."""    
    def __init__(self, monitor: CacheMonitor):
        """Initialize metrics exporter."""        self.monitor = monitor
        self.exporters: List[Callable] = []
        self.logger = logging.getLogger(f"{__name__}.MetricsExporter")
    
    async def add_exporter(self, exporter: Callable) -> None:
        """Add metrics exporter."""        self.exporters.append(exporter)
    
    async def export_metrics(self, time_range_hours: int = 1) -> None:
        """Export metrics to external systems."""        try:
            summary = await self.monitor.get_metrics_summary(time_range_hours=time_range_hours)
            
            for exporter in self.exporters:
                try:
                    if asyncio.iscoroutinefunction(exporter):
                        await exporter(summary)
                    else:
                        exporter(summary)
                except Exception as e:
                    self.logger.error(f"Metrics exporter error: {e}")
        
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
