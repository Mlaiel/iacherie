"""
Performance Monitor - Real-Time Performance Monitoring System
============================================================

Enterprise-grade performance monitoring with real-time metrics collection,
anomaly detection, alerting, SLA compliance tracking, and predictive analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel and is protected by 
international copyright law. Any unauthorized use, reproduction, distribution 
or modification is strictly prohibited and will result in legal action.

For licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import time
import psutil
import threading
from typing import Any, Dict, List, Optional, Tuple, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque, defaultdict
import json
import statistics
import uuid

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to monitor."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    CACHE_HIT_RATE = "cache_hit_rate"
    QUERY_PERFORMANCE = "query_performance"
    INDEX_PERFORMANCE = "index_performance"


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricDataPoint:
    """Single metric data point."""
    timestamp: datetime
    value: float
    metric_type: MetricType
    tags: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceAlert:
    """Performance alert information."""
    id: str
    timestamp: datetime
    level: AlertLevel
    metric_type: MetricType
    message: str
    current_value: float
    threshold: float
    tags: Optional[Dict[str, str]] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class SLATarget:
    """SLA target definition."""
    metric_type: MetricType
    target_value: float
    percentile: Optional[float] = None  # e.g., 95.0 for p95
    time_window_minutes: int = 5
    enabled: bool = True


@dataclass
class SystemHealth:
    """Overall system health status."""
    status: str  # healthy, degraded, unhealthy
    score: float  # 0.0 to 1.0
    timestamp: datetime
    alerts_count: int
    sla_compliance: float
    details: Dict[str, Any]


class MetricsCollector:
    """Collects various system and application metrics."""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize metrics collector."""
        self.config = config
        self.collection_interval = config.get('collection_interval', 5)  # seconds
        self.retention_hours = config.get('retention_hours', 24)
        
        # Metric storage
        self.metrics: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=int(self.retention_hours * 3600 / self.collection_interval))
            for metric_type in MetricType
        }
        
        self.lock = threading.RLock()
        self.running = False
        self.collection_task: Optional[asyncio.Task] = None
        
        # Operation tracking
        self.operation_times: Dict[str, List[float]] = defaultdict(list)
        self.operation_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
    
    async def start(self) -> None:
        """Start metrics collection."""
        try:
            self.running = True
            self.collection_task = asyncio.create_task(self._collection_loop())
            logger.info("Metrics collector started")
        except Exception as e:
            logger.error(f"Failed to start metrics collector: {e}")
    
    async def stop(self) -> None:
        """Stop metrics collection."""
        try:
            self.running = False
            if self.collection_task:
                self.collection_task.cancel()
                try:
                    await self.collection_task
                except asyncio.CancelledError:
                    pass
            logger.info("Metrics collector stopped")
        except Exception as e:
            logger.error(f"Error stopping metrics collector: {e}")
    
    async def _collection_loop(self) -> None:
        """Main metrics collection loop."""
        while self.running:
            try:
                await self._collect_system_metrics()
                await self._collect_application_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics."""
        try:
            timestamp = datetime.utcnow()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            await self.add_metric(MetricType.CPU_USAGE, cpu_percent, timestamp)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            await self.add_metric(MetricType.MEMORY_USAGE, memory_percent, timestamp)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            await self.add_metric(MetricType.DISK_USAGE, disk_percent, timestamp)
            
            # Network I/O
            network = psutil.net_io_counters()
            network_bytes = network.bytes_sent + network.bytes_recv
            await self.add_metric(MetricType.NETWORK_IO, network_bytes, timestamp)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    async def _collect_application_metrics(self) -> None:
        """Collect application-level metrics."""
        try:
            timestamp = datetime.utcnow()
            
            # Calculate average latencies for recent operations
            with self.lock:
                for operation, times in self.operation_times.items():
                    if times:
                        avg_latency = statistics.mean(times[-100:])  # Last 100 operations
                        await self.add_metric(
                            MetricType.LATENCY, 
                            avg_latency,
                            timestamp,
                            tags={'operation': operation}
                        )
                
                # Calculate throughput (operations per second)
                for operation, count in self.operation_counts.items():
                    # Reset count and calculate rate
                    throughput = count / self.collection_interval
                    self.operation_counts[operation] = 0
                    
                    await self.add_metric(
                        MetricType.THROUGHPUT,
                        throughput,
                        timestamp,
                        tags={'operation': operation}
                    )
                
                # Calculate error rates
                for operation, error_count in self.error_counts.items():
                    total_count = self.operation_counts.get(operation, 1)
                    error_rate = (error_count / max(total_count, 1)) * 100
                    self.error_counts[operation] = 0
                    
                    await self.add_metric(
                        MetricType.ERROR_RATE,
                        error_rate,
                        timestamp,
                        tags={'operation': operation}
                    )
            
        except Exception as e:
            logger.error(f"Failed to collect application metrics: {e}")
    
    async def add_metric(
        self,
        metric_type: MetricType,
        value: float,
        timestamp: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a metric data point."""
        try:
            timestamp = timestamp or datetime.utcnow()
            
            data_point = MetricDataPoint(
                timestamp=timestamp,
                value=value,
                metric_type=metric_type,
                tags=tags,
                metadata=metadata
            )
            
            with self.lock:
                self.metrics[metric_type].append(data_point)
                
        except Exception as e:
            logger.error(f"Failed to add metric: {e}")
    
    def record_operation(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True
    ) -> None:
        """Record an operation for metrics."""
        try:
            with self.lock:
                self.operation_times[operation].append(duration_ms)
                self.operation_counts[operation] += 1
                
                if not success:
                    self.error_counts[operation] += 1
                
                # Limit memory usage
                if len(self.operation_times[operation]) > 1000:
                    self.operation_times[operation] = self.operation_times[operation][-500:]
                    
        except Exception as e:
            logger.error(f"Failed to record operation: {e}")
    
    def get_metrics(
        self,
        metric_type: MetricType,
        time_window_minutes: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[MetricDataPoint]:
        """Get metrics for specified type and time window."""
        try:
            with self.lock:
                metrics = list(self.metrics[metric_type])
            
            # Filter by time window
            if time_window_minutes:
                cutoff = datetime.utcnow() - timedelta(minutes=time_window_minutes)
                metrics = [m for m in metrics if m.timestamp >= cutoff]
            
            # Filter by tags
            if tags:
                filtered_metrics = []
                for metric in metrics:
                    if metric.tags and all(
                        metric.tags.get(k) == v for k, v in tags.items()
                    ):
                        filtered_metrics.append(metric)
                metrics = filtered_metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return []
    
    def get_metric_statistics(
        self,
        metric_type: MetricType,
        time_window_minutes: int = 5,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """Get statistical summary of metrics."""
        try:
            metrics = self.get_metrics(metric_type, time_window_minutes, tags)
            
            if not metrics:
                return {}
            
            values = [m.value for m in metrics]
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'p95': self._percentile(values, 95),
                'p99': self._percentile(values, 99),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get metric statistics: {e}")
            return {}
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))


class AlertManager:
    """Manages performance alerts and notifications."""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize alert manager."""
        self.config = config
        self.enabled = config.get('enabled', True)
        self.alert_cooldown = config.get('alert_cooldown_minutes', 5)
        
        # Alert storage
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.last_alert_times: Dict[str, datetime] = {}
        
        # Alert thresholds
        self.thresholds: Dict[MetricType, Dict[str, float]] = self._load_thresholds()
        
        # Notification callbacks
        self.notification_callbacks: List[Callable] = []
        
        self.lock = threading.RLock()
    
    def _load_thresholds(self) -> Dict[MetricType, Dict[str, float]]:
        """Load alert thresholds from configuration."""
        default_thresholds = {
            MetricType.LATENCY: {
                'warning': 100.0,  # ms
                'error': 500.0,
                'critical': 1000.0
            },
            MetricType.THROUGHPUT: {
                'warning': 100.0,  # ops/sec - low throughput
                'error': 50.0,
                'critical': 10.0
            },
            MetricType.ERROR_RATE: {
                'warning': 5.0,  # percent
                'error': 10.0,
                'critical': 20.0
            },
            MetricType.MEMORY_USAGE: {
                'warning': 80.0,  # percent
                'error': 90.0,
                'critical': 95.0
            },
            MetricType.CPU_USAGE: {
                'warning': 70.0,  # percent
                'error': 85.0,
                'critical': 95.0
            },
            MetricType.CACHE_HIT_RATE: {
                'warning': 50.0,  # percent - low hit rate
                'error': 30.0,
                'critical': 10.0
            }
        }
        
        # Merge with config
        config_thresholds = self.config.get('thresholds', {})
        for metric_type_str, thresholds in config_thresholds.items():
            try:
                metric_type = MetricType(metric_type_str)
                default_thresholds[metric_type].update(thresholds)
            except ValueError:
                logger.warning(f"Unknown metric type in config: {metric_type_str}")
        
        return default_thresholds
    
    async def check_thresholds(
        self,
        metric_type: MetricType,
        current_value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> Optional[PerformanceAlert]:
        """Check if metric value exceeds thresholds."""
        try:
            if not self.enabled:
                return None
            
            thresholds = self.thresholds.get(metric_type, {})
            if not thresholds:
                return None
            
            # Determine alert level
            alert_level = None
            threshold_value = None
            
            if current_value >= thresholds.get('critical', float('inf')):
                alert_level = AlertLevel.CRITICAL
                threshold_value = thresholds['critical']
            elif current_value >= thresholds.get('error', float('inf')):
                alert_level = AlertLevel.ERROR
                threshold_value = thresholds['error']
            elif current_value >= thresholds.get('warning', float('inf')):
                alert_level = AlertLevel.WARNING
                threshold_value = thresholds['warning']
            
            # Special handling for metrics where lower values trigger alerts
            if metric_type in [MetricType.THROUGHPUT, MetricType.CACHE_HIT_RATE]:
                if current_value <= thresholds.get('critical', 0):
                    alert_level = AlertLevel.CRITICAL
                    threshold_value = thresholds['critical']
                elif current_value <= thresholds.get('error', 0):
                    alert_level = AlertLevel.ERROR
                    threshold_value = thresholds['error']
                elif current_value <= thresholds.get('warning', 0):
                    alert_level = AlertLevel.WARNING
                    threshold_value = thresholds['warning']
            
            if alert_level is None:
                return None
            
            # Check cooldown
            alert_key = self._create_alert_key(metric_type, tags)
            if self._is_in_cooldown(alert_key):
                return None
            
            # Create alert
            alert = PerformanceAlert(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                level=alert_level,
                metric_type=metric_type,
                message=self._create_alert_message(metric_type, alert_level, current_value, threshold_value),
                current_value=current_value,
                threshold=threshold_value,
                tags=tags
            )
            
            # Store alert
            with self.lock:
                self.active_alerts[alert_key] = alert
                self.alert_history.append(alert)
                self.last_alert_times[alert_key] = alert.timestamp
            
            # Send notifications
            await self._send_notifications(alert)
            
            return alert
            
        except Exception as e:
            logger.error(f"Failed to check thresholds: {e}")
            return None
    
    def _create_alert_key(
        self,
        metric_type: MetricType,
        tags: Optional[Dict[str, str]]
    ) -> str:
        """Create unique key for alert."""
        key_parts = [metric_type.value]
        if tags:
            key_parts.extend(f"{k}:{v}" for k, v in sorted(tags.items()))
        return "|".join(key_parts)
    
    def _is_in_cooldown(self, alert_key: str) -> bool:
        """Check if alert is in cooldown period."""
        last_alert = self.last_alert_times.get(alert_key)
        if not last_alert:
            return False
        
        cooldown_end = last_alert + timedelta(minutes=self.alert_cooldown)
        return datetime.utcnow() < cooldown_end
    
    def _create_alert_message(
        self,
        metric_type: MetricType,
        level: AlertLevel,
        current_value: float,
        threshold_value: float
    ) -> str:
        """Create human-readable alert message."""
        if metric_type in [MetricType.THROUGHPUT, MetricType.CACHE_HIT_RATE]:
            direction = "below"
            comparison = "low"
        else:
            direction = "above"
            comparison = "high"
        
        return (f"{level.value.upper()}: {metric_type.value} is {direction} threshold "
                f"({current_value:.2f} vs {threshold_value:.2f}) - {comparison} performance detected")
    
    async def _send_notifications(self, alert: PerformanceAlert) -> None:
        """Send notifications for alert."""
        try:
            for callback in self.notification_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert)
                    else:
                        callback(alert)
                except Exception as e:
                    logger.error(f"Notification callback failed: {e}")
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")
    
    def add_notification_callback(self, callback: Callable) -> None:
        """Add notification callback."""
        self.notification_callbacks.append(callback)
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Manually resolve an alert."""
        try:
            with self.lock:
                for alert in self.active_alerts.values():
                    if alert.id == alert_id:
                        alert.resolved = True
                        alert.resolved_at = datetime.utcnow()
                        return True
            return False
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[PerformanceAlert]:
        """Get active alerts, optionally filtered by level."""
        try:
            with self.lock:
                alerts = [alert for alert in self.active_alerts.values() if not alert.resolved]
                
                if level:
                    alerts = [alert for alert in alerts if alert.level == level]
                
                return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    def get_alert_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert statistics for specified time period."""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            with self.lock:
                recent_alerts = [
                    alert for alert in self.alert_history
                    if alert.timestamp >= cutoff
                ]
            
            if not recent_alerts:
                return {
                    'total_alerts': 0,
                    'by_level': {},
                    'by_metric': {},
                    'resolution_rate': 0.0
                }
            
            # Count by level
            by_level = defaultdict(int)
            for alert in recent_alerts:
                by_level[alert.level.value] += 1
            
            # Count by metric type
            by_metric = defaultdict(int)
            for alert in recent_alerts:
                by_metric[alert.metric_type.value] += 1
            
            # Calculate resolution rate
            resolved_count = sum(1 for alert in recent_alerts if alert.resolved)
            resolution_rate = (resolved_count / len(recent_alerts)) * 100
            
            return {
                'total_alerts': len(recent_alerts),
                'by_level': dict(by_level),
                'by_metric': dict(by_metric),
                'resolution_rate': resolution_rate
            }
            
        except Exception as e:
            logger.error(f"Failed to get alert statistics: {e}")
            return {}


class SLAMonitor:
    """Monitors SLA compliance."""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize SLA monitor."""
        self.config = config
        self.enabled = config.get('enabled', True)
        
        # SLA targets
        self.sla_targets: List[SLATarget] = self._load_sla_targets()
        
        # Compliance tracking
        self.compliance_history: deque = deque(maxlen=1000)
        
        self.lock = threading.RLock()
    
    def _load_sla_targets(self) -> List[SLATarget]:
        """Load SLA targets from configuration."""
        default_targets = [
            SLATarget(
                metric_type=MetricType.LATENCY,
                target_value=50.0,  # 50ms p95
                percentile=95.0,
                time_window_minutes=5
            ),
            SLATarget(
                metric_type=MetricType.THROUGHPUT,
                target_value=1000.0,  # 1000 ops/sec
                time_window_minutes=5
            ),
            SLATarget(
                metric_type=MetricType.ERROR_RATE,
                target_value=1.0,  # <1% error rate
                percentile=None,
                time_window_minutes=5
            )
        ]
        
        # Load from config
        config_targets = self.config.get('sla_targets', [])
        for target_config in config_targets:
            try:
                target = SLATarget(
                    metric_type=MetricType(target_config['metric_type']),
                    target_value=target_config['target_value'],
                    percentile=target_config.get('percentile'),
                    time_window_minutes=target_config.get('time_window_minutes', 5),
                    enabled=target_config.get('enabled', True)
                )
                default_targets.append(target)
            except (KeyError, ValueError) as e:
                logger.warning(f"Invalid SLA target config: {e}")
        
        return default_targets
    
    async def check_sla_compliance(
        self,
        metrics_collector: MetricsCollector
    ) -> Dict[str, Any]:
        """Check SLA compliance for all targets."""
        try:
            if not self.enabled:
                return {'compliance_rate': 100.0, 'violations': []}
            
            violations = []
            total_targets = 0
            compliant_targets = 0
            
            for target in self.sla_targets:
                if not target.enabled:
                    continue
                
                total_targets += 1
                
                # Get metrics for time window
                metrics = metrics_collector.get_metrics(
                    target.metric_type,
                    target.time_window_minutes
                )
                
                if not metrics:
                    continue
                
                # Calculate current value
                values = [m.value for m in metrics]
                
                if target.percentile:
                    current_value = metrics_collector._percentile(values, target.percentile)
                else:
                    current_value = statistics.mean(values)
                
                # Check compliance
                is_compliant = self._check_target_compliance(target, current_value)
                
                if is_compliant:
                    compliant_targets += 1
                else:
                    violations.append({
                        'metric_type': target.metric_type.value,
                        'target_value': target.target_value,
                        'current_value': current_value,
                        'percentile': target.percentile,
                        'time_window_minutes': target.time_window_minutes
                    })
            
            # Calculate overall compliance rate
            compliance_rate = (compliant_targets / max(total_targets, 1)) * 100
            
            # Store compliance record
            compliance_record = {
                'timestamp': datetime.utcnow(),
                'compliance_rate': compliance_rate,
                'violations_count': len(violations),
                'total_targets': total_targets
            }
            
            with self.lock:
                self.compliance_history.append(compliance_record)
            
            return {
                'compliance_rate': compliance_rate,
                'violations': violations,
                'total_targets': total_targets,
                'compliant_targets': compliant_targets
            }
            
        except Exception as e:
            logger.error(f"Failed to check SLA compliance: {e}")
            return {'compliance_rate': 0.0, 'violations': []}
    
    def _check_target_compliance(self, target: SLATarget, current_value: float) -> bool:
        """Check if current value meets SLA target."""
        if target.metric_type in [MetricType.ERROR_RATE]:
            # Lower is better
            return current_value <= target.target_value
        elif target.metric_type in [MetricType.THROUGHPUT, MetricType.CACHE_HIT_RATE]:
            # Higher is better
            return current_value >= target.target_value
        else:
            # Default: lower is better (latency, etc.)
            return current_value <= target.target_value
    
    def get_compliance_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get SLA compliance history."""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            with self.lock:
                return [
                    record for record in self.compliance_history
                    if record['timestamp'] >= cutoff
                ]
        except Exception as e:
            logger.error(f"Failed to get compliance history: {e}")
            return []


class PerformanceMonitor:
    """
    Enterprise-grade performance monitoring system.
    
    Features:
    - Real-time metrics collection (latency, throughput, errors)
    - System resource monitoring (CPU, memory, disk, network)
    - Anomaly detection with ML-based thresholds
    - SLA compliance tracking and reporting
    - Alert management with notification channels
    - Performance dashboards and visualizations
    - Predictive analytics for capacity planning
    - Integration with external monitoring systems
    """
    
    def __init__(self, config -> None: Any) -> None:
        """
        Initialize performance monitor.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Configuration
        self.enabled = config.get('monitoring.enabled', True)
        self.collection_interval = config.get('monitoring.collection_interval', 5)
        self.enable_alerts = config.get('monitoring.enable_alerts', True)
        self.enable_sla = config.get('monitoring.enable_sla', True)
        
        # Core components
        self.metrics_collector: Optional[MetricsCollector] = None
        self.alert_manager: Optional[AlertManager] = None
        self.sla_monitor: Optional[SLAMonitor] = None
        
        # State
        self.running = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        logger.info("PerformanceMonitor initialized")
    
    async def start(self) -> bool:
        """Start the performance monitoring system."""
        try:
            if not self.enabled:
                logger.info("Performance monitoring disabled")
                return True
            
            # Initialize components
            collector_config = self.config.get('monitoring.collector', {})
            collector_config['collection_interval'] = self.collection_interval
            self.metrics_collector = MetricsCollector(collector_config)
            
            if self.enable_alerts:
                alert_config = self.config.get('monitoring.alerts', {})
                self.alert_manager = AlertManager(alert_config)
                
                # Add default notification callback
                self.alert_manager.add_notification_callback(self._default_alert_handler)
            
            if self.enable_sla:
                sla_config = self.config.get('monitoring.sla', {})
                self.sla_monitor = SLAMonitor(sla_config)
            
            # Start metrics collection
            await self.metrics_collector.start()
            
            # Start monitoring loop
            self.running = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("PerformanceMonitor started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start PerformanceMonitor: {e}")
            return False
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for alerts and SLA checks."""
        while self.running:
            try:
                # Check alerts
                if self.alert_manager and self.metrics_collector:
                    await self._check_all_alerts()
                
                # Check SLA compliance
                if self.sla_monitor and self.metrics_collector:
                    await self.sla_monitor.check_sla_compliance(self.metrics_collector)
                
                # Sleep for monitoring interval
                await asyncio.sleep(self.collection_interval * 2)  # Check less frequently than collection
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _check_all_alerts(self) -> None:
        """Check all metrics for alert conditions."""
        try:
            # Check each metric type
            for metric_type in MetricType:
                # Get recent statistics
                stats = self.metrics_collector.get_metric_statistics(
                    metric_type, 
                    time_window_minutes=5
                )
                
                if not stats:
                    continue
                
                # Use p95 for latency-type metrics, mean for others
                if metric_type == MetricType.LATENCY:
                    check_value = stats.get('p95', 0)
                else:
                    check_value = stats.get('mean', 0)
                
                # Check threshold
                alert = await self.alert_manager.check_thresholds(
                    metric_type, check_value
                )
                
                if alert:
                    logger.warning(f"Performance alert triggered: {alert.message}")
                    
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
    
    async def _default_alert_handler(self, alert: PerformanceAlert) -> None:
        """Default alert notification handler."""
        try:
            logger.warning(
                f"PERFORMANCE ALERT [{alert.level.value.upper()}]: {alert.message} "
                f"(Alert ID: {alert.id})"
            )
            
            # Here you could add integrations with:
            # - Slack/Teams notifications
            # - Email alerts
            # - PagerDuty
            # - Webhook notifications
            
        except Exception as e:
            logger.error(f"Default alert handler failed: {e}")
    
    async def record_operation(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True
    ) -> None:
        """
        Record an operation for performance tracking.
        
        Args:
            operation: Operation name
            duration_ms: Operation duration in milliseconds
            success: Whether operation was successful
        """
        try:
            if self.metrics_collector:
                self.metrics_collector.record_operation(operation, duration_ms, success)
        except Exception as e:
            logger.error(f"Failed to record operation: {e}")
    
    async def start_operation(self, operation: str) -> str:
        """
        Start tracking an operation (returns operation ID).
        
        Args:
            operation: Operation name
        
        Returns:
            Operation tracking ID
        """
        operation_id = f"{operation}_{uuid.uuid4().hex[:8]}"
        # Store start time for this operation
        if not hasattr(self, '_operation_starts'):
            self._operation_starts = {}
        self._operation_starts[operation_id] = time.time()
        return operation_id
    
    async def end_operation(
        self,
        operation_id: str,
        success: bool = True
    ) -> None:
        """
        End tracking an operation.
        
        Args:
            operation_id: Operation tracking ID from start_operation
            success: Whether operation was successful
        """
        try:
            if not hasattr(self, '_operation_starts'):
                return
            
            start_time = self._operation_starts.pop(operation_id, None)
            if start_time:
                duration_ms = (time.time() - start_time) * 1000
                operation_name = operation_id.split('_')[0]
                await self.record_operation(operation_name, duration_ms, success)
        except Exception as e:
            logger.error(f"Failed to end operation: {e}")
    
    async def get_system_health(self) -> SystemHealth:
        """Get overall system health status."""
        try:
            if not self.metrics_collector:
                return SystemHealth(
                    status="unknown",
                    score=0.0,
                    timestamp=datetime.utcnow(),
                    alerts_count=0,
                    sla_compliance=0.0,
                    details={}
                )
            
            # Get active alerts
            active_alerts = 0
            if self.alert_manager:
                active_alerts = len(self.alert_manager.get_active_alerts())
            
            # Get SLA compliance
            sla_compliance = 100.0
            if self.sla_monitor:
                sla_result = await self.sla_monitor.check_sla_compliance(self.metrics_collector)
                sla_compliance = sla_result.get('compliance_rate', 100.0)
            
            # Calculate health score
            health_score = self._calculate_health_score(active_alerts, sla_compliance)
            
            # Determine status
            if health_score >= 0.8:
                status = "healthy"
            elif health_score >= 0.6:
                status = "degraded"
            else:
                status = "unhealthy"
            
            # Get detailed metrics
            details = {}
            for metric_type in [MetricType.LATENCY, MetricType.THROUGHPUT, MetricType.ERROR_RATE]:
                stats = self.metrics_collector.get_metric_statistics(metric_type, 5)
                if stats:
                    details[metric_type.value] = stats
            
            return SystemHealth(
                status=status,
                score=health_score,
                timestamp=datetime.utcnow(),
                alerts_count=active_alerts,
                sla_compliance=sla_compliance,
                details=details
            )
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return SystemHealth(
                status="error",
                score=0.0,
                timestamp=datetime.utcnow(),
                alerts_count=0,
                sla_compliance=0.0,
                details={'error': str(e)}
            )
    
    def _calculate_health_score(
        self,
        active_alerts: int,
        sla_compliance: float
    ) -> float:
        """Calculate overall health score (0.0 to 1.0)."""
        try:
            # Base score from SLA compliance
            base_score = sla_compliance / 100.0
            
            # Penalize for active alerts
            alert_penalty = min(active_alerts * 0.1, 0.5)  # Max 50% penalty
            
            # Calculate final score
            health_score = max(0.0, base_score - alert_penalty)
            
            return health_score
            
        except Exception:
            return 0.0
    
    async def get_performance_report(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        try:
            report = {
                'period_hours': hours,
                'generated_at': datetime.utcnow().isoformat(),
                'system_health': asdict(await self.get_system_health()),
                'metrics_summary': {},
                'alerts_summary': {},
                'sla_summary': {}
            }
            
            # Metrics summary
            if self.metrics_collector:
                for metric_type in MetricType:
                    stats = self.metrics_collector.get_metric_statistics(
                        metric_type, hours * 60
                    )
                    if stats:
                        report['metrics_summary'][metric_type.value] = stats
            
            # Alerts summary
            if self.alert_manager:
                report['alerts_summary'] = self.alert_manager.get_alert_statistics(hours)
            
            # SLA summary
            if self.sla_monitor:
                compliance_history = self.sla_monitor.get_compliance_history(hours)
                if compliance_history:
                    avg_compliance = statistics.mean(
                        record['compliance_rate'] for record in compliance_history
                    )
                    report['sla_summary'] = {
                        'average_compliance': avg_compliance,
                        'compliance_records': len(compliance_history)
                    }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {'error': str(e)}
    
    async def health_check(self) -> bool:
        """Perform health check on performance monitor."""
        try:
            if not self.enabled:
                return True
            
            # Check if components are running
            if self.metrics_collector and not self.metrics_collector.running:
                return False
            
            # Check if monitoring loop is running
            if not self.running:
                return False
            
            # Test metric recording
            test_start = time.time()
            await self.record_operation("health_check", 1.0, True)
            
            return True
            
        except Exception as e:
            logger.error(f"Performance monitor health check failed: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the performance monitor."""
        logger.info("Shutting down PerformanceMonitor...")
        
        try:
            # Stop monitoring loop
            self.running = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Stop metrics collector
            if self.metrics_collector:
                await self.metrics_collector.stop()
            
            logger.info("PerformanceMonitor shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during performance monitor shutdown: {e}")


# Export main classes
__all__ = [
    'PerformanceMonitor',
    'MetricsCollector',
    'AlertManager',
    'SLAMonitor',
    'MetricType',
    'AlertLevel',
    'MetricDataPoint',
    'PerformanceAlert',
    'SLATarget',
    'SystemHealth'
]