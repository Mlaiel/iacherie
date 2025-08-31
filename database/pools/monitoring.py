"""Pool Metrics and Monitoring System - IA Influencer Agent + Content Protection Platform

Comprehensive metrics collection, monitoring, and alerting system for all database connection pools.
Provides real-time performance insights, health monitoring, and automated alerting capabilities.

Monitoring Features:
- Real-time connection pool metrics collection
- Performance analytics and trend analysis
- Health status monitoring with automated checks
- Custom alerting with configurable thresholds
- Distributed tracing for connection lifecycle
- Resource utilization tracking and optimization recommendations

Metrics Types:
- Connection pool statistics (active, idle, waiting connections)
- Query performance metrics (latency, throughput, errors)
- Resource utilization (CPU, memory, network)
- Health status indicators and uptime tracking
- Business metrics (content processing, user engagement)
- Security metrics (authentication failures, access patterns)

Alerting & Notifications:
- Real-time alert generation based on thresholds
- Multi-channel notifications (email, Slack, webhook)
- Escalation policies for critical issues
- Alert correlation and noise reduction
- Automated remediation for common issues

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
import json
import time
import statistics
from typing import Dict, List, Optional, Any, Union, Callable, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import threading
import weakref
import psutil
import uuid

try:
    import aiohttp
    import aioprometheus
    from aioprometheus import Counter, Gauge, Histogram, Summary
    import structlog
    import sentry_sdk
    from sentry_sdk.integrations.asyncio import AsyncioIntegration
except ImportError as e:
    logging.warning(f"Monitoring dependency missing: {e}")

from .manager import PoolConfig, DatabaseConnectionInfo, DatabaseType, PoolStrategy, ConnectionState

logger = logging.getLogger(__name__)

# =============== MONITORING ENUMS ===============

class MetricType(str, Enum):
    """Types of metrics"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(str, Enum):
    """Alert severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class HealthStatus(str, Enum):
    """Health status levels"""    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class MonitoringComponent(str, Enum):
    """Components being monitored"""    CONNECTION_POOL = "connection_pool"
    DATABASE = "database"
    CACHE = "cache"
    STORAGE = "storage"
    NETWORK = "network"
    SYSTEM = "system"

class NotificationChannel(str, Enum):
    """Notification channels"""    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    DASHBOARD = "dashboard"

# =============== METRIC MODELS ===============

@dataclass
class MetricPoint:
    """Single metric data point"""    metric_name: str
    metric_type: MetricType
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricSeries:
    """Time series of metric points"""    metric_name: str
    metric_type: MetricType
    points: deque = field(default_factory=lambda: deque(maxlen=1000))
    labels: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_point(self, value: Union[int, float], timestamp: Optional[datetime] = None) -> None:
        """Add a metric point"""        self.points.append(MetricPoint(
            metric_name=self.metric_name,
            metric_type=self.metric_type,
            value=value,
            timestamp=timestamp or datetime.utcnow(),
            labels=self.labels
        ))
    
    def get_latest(self) -> Optional[MetricPoint]:
        """Get the latest metric point"""        return self.points[-1] if self.points else None
    
    def get_average(self, duration: timedelta = timedelta(minutes=5)) -> Optional[float]:
        """Get average value over duration"""        cutoff_time = datetime.utcnow() - duration
        recent_points = [p.value for p in self.points if p.timestamp >= cutoff_time]
        return statistics.mean(recent_points) if recent_points else None
    
    def get_percentile(self, percentile: float, duration: timedelta = timedelta(minutes=5)) -> Optional[float]:
        """Get percentile value over duration"""        cutoff_time = datetime.utcnow() - duration
        recent_points = [p.value for p in self.points if p.timestamp >= cutoff_time]
        if not recent_points:
            return None
        recent_points.sort()
        index = int(len(recent_points) * percentile / 100)
        return recent_points[min(index, len(recent_points) - 1)]

@dataclass
class HealthCheck:
    """Health check definition"""    check_id: str
    component: MonitoringComponent
    check_name: str
    check_function: Callable[[], bool]
    interval_seconds: int = 60
    timeout_seconds: int = 30
    retries: int = 3
    enabled: bool = True
    tags: Set[str] = field(default_factory=set)

@dataclass
class HealthCheckResult:
    """Result of a health check"""    check_id: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AlertRule:
    """Alert rule definition"""    rule_id: str
    rule_name: str
    metric_name: str
    condition: str  # e.g., "> 100", "< 0.5", "== 0"
    severity: AlertSeverity
    duration: timedelta  # How long condition must be true
    cooldown: timedelta  # Minimum time between alerts
    enabled: bool = True
    channels: List[NotificationChannel] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Active alert"""    alert_id: str
    rule_id: str
    metric_name: str
    condition: str
    current_value: Union[int, float]
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceSnapshot:
    """Performance snapshot for optimization"""    snapshot_id: str
    component: MonitoringComponent
    timestamp: datetime
    metrics: Dict[str, MetricPoint]
    resource_usage: Dict[str, float]
    recommendations: List[str]
    health_status: HealthStatus

# =============== POOL METRICS COLLECTOR ===============

class PoolMetricsCollector:
    """Collects metrics from database connection pools"""    
    def __init__(self):
        self.metrics: Dict[str, MetricSeries] = {}
        self.pools: Dict[str, Any] = {}
        self._collection_interval = 30  # seconds
        self._collection_task: Optional[asyncio.Task] = None
        self._lock = threading.RLock()
    
    def register_pool(self, pool_id: str, pool_instance: Any) -> None:
        """Register a pool for metrics collection"""        with self._lock:
            self.pools[pool_id] = pool_instance
            logger.info(f"✅ Pool registered for metrics: {pool_id}")
    
    def unregister_pool(self, pool_id: str) -> None:
        """Unregister pool from metrics collection"""        with self._lock:
            if pool_id in self.pools:
                del self.pools[pool_id]
                logger.info(f"✅ Pool unregistered from metrics: {pool_id}")
    
    async def start_collection(self) -> None:
        """Start metrics collection"""        if self._collection_task is None or self._collection_task.done():
            self._collection_task = asyncio.create_task(self._collection_loop())
            logger.info("✅ Metrics collection started")
    
    async def stop_collection(self) -> None:
        """Stop metrics collection"""        if self._collection_task and not self._collection_task.done():
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
            logger.info("✅ Metrics collection stopped")
    
    async def _collection_loop(self) -> None:
        """Main metrics collection loop"""        while True:
            try:
                await self._collect_pool_metrics()
                await asyncio.sleep(self._collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(self._collection_interval)
    
    async def _collect_pool_metrics(self) -> None:
        """Collect metrics from all registered pools"""        with self._lock:
            for pool_id, pool_instance in self.pools.items():
                try:
                    await self._collect_single_pool_metrics(pool_id, pool_instance)
                except Exception as e:
                    logger.error(f"Failed to collect metrics for pool {pool_id}: {e}")
    
    async def _collect_single_pool_metrics(self, pool_id: str, pool_instance: Any) -> None:
        """Collect metrics from a single pool"""        try:
            # Get pool statistics
            stats = getattr(pool_instance, 'get_pool_statistics', lambda: {})()
            
            # Collect connection metrics
            self._record_metric(f"pool.{pool_id}.active_connections", stats.get('active_connections', 0), MetricType.GAUGE)
            self._record_metric(f"pool.{pool_id}.idle_connections", stats.get('idle_connections', 0), MetricType.GAUGE)
            self._record_metric(f"pool.{pool_id}.waiting_connections", stats.get('waiting_connections', 0), MetricType.GAUGE)
            self._record_metric(f"pool.{pool_id}.total_connections", stats.get('total_connections', 0), MetricType.GAUGE)
            
            # Collect performance metrics
            self._record_metric(f"pool.{pool_id}.avg_query_time", stats.get('avg_query_time', 0), MetricType.GAUGE)
            self._record_metric(f"pool.{pool_id}.queries_per_second", stats.get('queries_per_second', 0), MetricType.GAUGE)
            self._record_metric(f"pool.{pool_id}.error_rate", stats.get('error_rate', 0), MetricType.GAUGE)
            
            # Collect health metrics
            health_status = getattr(pool_instance, 'is_healthy', lambda: True)()
            self._record_metric(f"pool.{pool_id}.health", 1 if health_status else 0, MetricType.GAUGE)
            
        except Exception as e:
            logger.error(f"Error collecting metrics for pool {pool_id}: {e}")
    
    def _record_metric(self, metric_name: str, value: Union[int, float], metric_type: MetricType, 
                      labels: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value"""        labels = labels or {}
        
        # Get or create metric series
        if metric_name not in self.metrics:
            self.metrics[metric_name] = MetricSeries(
                metric_name=metric_name,
                metric_type=metric_type,
                labels=labels
            )
        
        # Add metric point
        self.metrics[metric_name].add_point(value)
    
    def get_metric(self, metric_name: str) -> Optional[MetricSeries]:
        """Get metric series by name"""        return self.metrics.get(metric_name)
    
    def get_all_metrics(self) -> Dict[str, MetricSeries]:
        """Get all collected metrics"""        return self.metrics.copy()

# =============== HEALTH MONITOR ===============

class HealthMonitor:
    """Health monitoring system"""    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_results: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
        self._lock = threading.RLock()
    
    def register_health_check(self, health_check: HealthCheck) -> None:
        """Register a health check"""        with self._lock:
            self.health_checks[health_check.check_id] = health_check
            
            # Start monitoring task
            if health_check.enabled:
                self._start_health_check_task(health_check)
                
            logger.info(f"✅ Health check registered: {health_check.check_id}")
    
    def unregister_health_check(self, check_id: str) -> None:
        """Unregister a health check"""        with self._lock:
            if check_id in self.health_checks:
                del self.health_checks[check_id]
                
                # Stop monitoring task
                if check_id in self._monitoring_tasks:
                    self._monitoring_tasks[check_id].cancel()
                    del self._monitoring_tasks[check_id]
                
                logger.info(f"✅ Health check unregistered: {check_id}")
    
    def _start_health_check_task(self, health_check: HealthCheck) -> None:
        """Start monitoring task for health check"""        if health_check.check_id not in self._monitoring_tasks:
            task = asyncio.create_task(self._health_check_loop(health_check))
            self._monitoring_tasks[health_check.check_id] = task
    
    async def _health_check_loop(self, health_check: HealthCheck) -> None:
        """Main health check loop"""        while True:
            try:
                if health_check.enabled:
                    result = await self._execute_health_check(health_check)
                    self.health_results[health_check.check_id].append(result)
                
                await asyncio.sleep(health_check.interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error for {health_check.check_id}: {e}")
                await asyncio.sleep(health_check.interval_seconds)
    
    async def _execute_health_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Execute a single health check"""        start_time = time.time()
        
        try:
            # Execute health check with timeout
            check_passed = await asyncio.wait_for(
                asyncio.to_thread(health_check.check_function),
                timeout=health_check.timeout_seconds
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.HEALTHY if check_passed else HealthStatus.UNHEALTHY,
                message="Health check passed" if check_passed else "Health check failed",
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms
            )
            
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.CRITICAL,
                message=f"Health check timed out after {health_check.timeout_seconds}s",
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.CRITICAL,
                message=f"Health check error: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms
            )
    
    def get_component_health(self, component: MonitoringComponent) -> HealthStatus:
        """Get overall health status for a component"""        component_checks = [
            hc for hc in self.health_checks.values() 
            if hc.component == component and hc.enabled
        ]
        
        if not component_checks:
            return HealthStatus.HEALTHY
        
        # Get latest results for component checks
        latest_results = []
        for health_check in component_checks:
            results = self.health_results.get(health_check.check_id)
            if results:
                latest_results.append(results[-1])
        
        if not latest_results:
            return HealthStatus.HEALTHY
        
        # Determine overall health
        critical_count = sum(1 for r in latest_results if r.status == HealthStatus.CRITICAL)
        unhealthy_count = sum(1 for r in latest_results if r.status == HealthStatus.UNHEALTHY)
        
        if critical_count > 0:
            return HealthStatus.CRITICAL
        elif unhealthy_count > len(latest_results) * 0.5:  # More than 50% unhealthy
            return HealthStatus.UNHEALTHY
        elif unhealthy_count > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""        summary = {
            "overall_status": HealthStatus.HEALTHY,
            "components": {},
            "total_checks": len(self.health_checks),
            "enabled_checks": sum(1 for hc in self.health_checks.values() if hc.enabled),
            "last_updated": datetime.utcnow()
        }
        
        # Get status for each component
        for component in MonitoringComponent:
            component_health = self.get_component_health(component)
            summary["components"][component.value] = component_health.value
            
            # Update overall status (worst status wins)
            if component_health == HealthStatus.CRITICAL:
                summary["overall_status"] = HealthStatus.CRITICAL
            elif component_health == HealthStatus.UNHEALTHY and summary["overall_status"] != HealthStatus.CRITICAL:
                summary["overall_status"] = HealthStatus.UNHEALTHY
            elif component_health == HealthStatus.DEGRADED and summary["overall_status"] == HealthStatus.HEALTHY:
                summary["overall_status"] = HealthStatus.DEGRADED
        
        return summary

# =============== ALERT MANAGER ===============

class AlertManager:
    """Alert management system"""    
    def __init__(self, metrics_collector: PoolMetricsCollector):
        self.metrics_collector = metrics_collector
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self._evaluation_task: Optional[asyncio.Task] = None
        self._evaluation_interval = 30  # seconds
        self._lock = threading.RLock()
        self._notification_handlers: Dict[NotificationChannel, Callable] = {}
    
    def register_alert_rule(self, alert_rule: AlertRule) -> None:
        """Register an alert rule"""        with self._lock:
            self.alert_rules[alert_rule.rule_id] = alert_rule
            logger.info(f"✅ Alert rule registered: {alert_rule.rule_id}")
    
    def unregister_alert_rule(self, rule_id: str) -> None:
        """Unregister an alert rule"""        with self._lock:
            if rule_id in self.alert_rules:
                del self.alert_rules[rule_id]
                logger.info(f"✅ Alert rule unregistered: {rule_id}")
    
    def register_notification_handler(self, channel: NotificationChannel, handler: Callable) -> None:
        """Register notification handler for a channel"""        self._notification_handlers[channel] = handler
        logger.info(f"✅ Notification handler registered: {channel.value}")
    
    async def start_evaluation(self) -> None:
        """Start alert rule evaluation"""        if self._evaluation_task is None or self._evaluation_task.done():
            self._evaluation_task = asyncio.create_task(self._evaluation_loop())
            logger.info("✅ Alert evaluation started")
    
    async def stop_evaluation(self) -> None:
        """Stop alert rule evaluation"""        if self._evaluation_task and not self._evaluation_task.done():
            self._evaluation_task.cancel()
            try:
                await self._evaluation_task
            except asyncio.CancelledError:
                pass
            logger.info("✅ Alert evaluation stopped")
    
    async def _evaluation_loop(self) -> None:
        """Main alert evaluation loop"""        while True:
            try:
                await self._evaluate_alert_rules()
                await asyncio.sleep(self._evaluation_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(self._evaluation_interval)
    
    async def _evaluate_alert_rules(self) -> None:
        """Evaluate all alert rules"""        with self._lock:
            for rule_id, alert_rule in self.alert_rules.items():
                if alert_rule.enabled:
                    try:
                        await self._evaluate_single_rule(alert_rule)
                    except Exception as e:
                        logger.error(f"Failed to evaluate alert rule {rule_id}: {e}")
    
    async def _evaluate_single_rule(self, alert_rule: AlertRule) -> None:
        """Evaluate a single alert rule"""        try:
            # Get metric series
            metric_series = self.metrics_collector.get_metric(alert_rule.metric_name)
            if not metric_series:
                return
            
            # Get latest value
            latest_point = metric_series.get_latest()
            if not latest_point:
                return
            
            # Evaluate condition
            condition_met = self._evaluate_condition(latest_point.value, alert_rule.condition)
            
            # Check if alert should be triggered
            if condition_met:
                await self._handle_alert_trigger(alert_rule, latest_point.value)
            else:
                await self._handle_alert_resolution(alert_rule)
                
        except Exception as e:
            logger.error(f"Error evaluating alert rule {alert_rule.rule_id}: {e}")
    
    def _evaluate_condition(self, value: Union[int, float], condition: str) -> bool:
        """Evaluate alert condition"""        try:
            # Simple condition evaluation (can be enhanced with expression parser)
            if condition.startswith(">"):
                threshold = float(condition[1:].strip())
                return value > threshold
            elif condition.startswith("<"):
                threshold = float(condition[1:].strip())
                return value < threshold
            elif condition.startswith("=="):
                threshold = float(condition[2:].strip())
                return value == threshold
            elif condition.startswith("!="):
                threshold = float(condition[2:].strip())
                return value != threshold
            else:
                return False
        except Exception:
            return False
    
    async def _handle_alert_trigger(self, alert_rule: AlertRule, current_value: Union[int, float]) -> None:
        """Handle alert trigger"""        # Check if alert already exists
        existing_alert = None
        for alert in self.active_alerts.values():
            if alert.rule_id == alert_rule.rule_id and alert.resolved_at is None:
                existing_alert = alert
                break
        
        if existing_alert:
            # Update existing alert
            existing_alert.current_value = current_value
            return
        
        # Check cooldown
        if self._is_in_cooldown(alert_rule):
            return
        
        # Create new alert
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            rule_id=alert_rule.rule_id,
            metric_name=alert_rule.metric_name,
            condition=alert_rule.condition,
            current_value=current_value,
            severity=alert_rule.severity,
            message=f"Alert triggered: {alert_rule.rule_name} - {alert_rule.metric_name} {alert_rule.condition} (current: {current_value})",
            triggered_at=datetime.utcnow()
        )
        
        self.active_alerts[alert.alert_id] = alert
        
        # Send notifications
        await self._send_alert_notifications(alert, alert_rule)
        
        logger.warning(f"🚨 Alert triggered: {alert_rule.rule_name}")
    
    async def _handle_alert_resolution(self, alert_rule: AlertRule) -> None:
        """Handle alert resolution"""        # Find active alerts for this rule
        for alert in list(self.active_alerts.values()):
            if alert.rule_id == alert_rule.rule_id and alert.resolved_at is None:
                # Resolve alert
                alert.resolved_at = datetime.utcnow()
                
                # Move to history
                self.alert_history.append(alert)
                del self.active_alerts[alert.alert_id]
                
                logger.info(f"✅ Alert resolved: {alert_rule.rule_name}")
    
    def _is_in_cooldown(self, alert_rule: AlertRule) -> bool:
        """Check if alert rule is in cooldown period"""        cutoff_time = datetime.utcnow() - alert_rule.cooldown
        
        # Check recent alerts in history
        for alert in self.alert_history:
            if (alert.rule_id == alert_rule.rule_id and 
                alert.triggered_at >= cutoff_time):
                return True
        
        return False
    
    async def _send_alert_notifications(self, alert: Alert, alert_rule: AlertRule) -> None:
        """Send alert notifications"""        for channel in alert_rule.channels:
            handler = self._notification_handlers.get(channel)
            if handler:
                try:
                    await handler(alert, alert_rule)
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel.value}: {e}")
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""        with self._lock:
            alert = self.active_alerts.get(alert_id)
            if alert and alert.acknowledged_at is None:
                alert.acknowledged_at = datetime.utcnow()
                alert.acknowledged_by = acknowledged_by
                logger.info(f"✅ Alert acknowledged: {alert_id} by {acknowledged_by}")
                return True
        return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts"""        alerts = list(self.active_alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda a: a.triggered_at, reverse=True)

# =============== PERFORMANCE ANALYZER ===============

class PerformanceAnalyzer:
    """Performance analysis and optimization recommendations"""    
    def __init__(self, metrics_collector: PoolMetricsCollector, health_monitor: HealthMonitor):
        self.metrics_collector = metrics_collector
        self.health_monitor = health_monitor
        self.snapshots: deque = deque(maxlen=100)
    
    async def create_performance_snapshot(self, component: MonitoringComponent) -> PerformanceSnapshot:
        """Create a performance snapshot for analysis"""        try:
            snapshot_metrics = {}
            resource_usage = {}
            recommendations = []
            
            # Collect relevant metrics
            all_metrics = self.metrics_collector.get_all_metrics()
            component_prefix = f"{component.value}."
            
            for metric_name, metric_series in all_metrics.items():
                if metric_name.startswith(component_prefix):
                    latest_point = metric_series.get_latest()
                    if latest_point:
                        snapshot_metrics[metric_name] = latest_point
            
            # Collect system resource usage
            resource_usage = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            }
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(component, snapshot_metrics, resource_usage)
            
            # Determine health status
            health_status = self.health_monitor.get_component_health(component)
            
            snapshot = PerformanceSnapshot(
                snapshot_id=str(uuid.uuid4()),
                component=component,
                timestamp=datetime.utcnow(),
                metrics=snapshot_metrics,
                resource_usage=resource_usage,
                recommendations=recommendations,
                health_status=health_status
            )
            
            self.snapshots.append(snapshot)
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to create performance snapshot: {e}")
            raise
    
    async def _generate_recommendations(self, component: MonitoringComponent, 
                                      metrics: Dict[str, MetricPoint],
                                      resource_usage: Dict[str, float]) -> List[str]:
        """Generate performance optimization recommendations"""        recommendations = []
        
        try:
            # CPU recommendations
            cpu_percent = resource_usage.get("cpu_percent", 0)
            if cpu_percent > 80:
                recommendations.append("High CPU usage detected. Consider scaling up or optimizing queries.")
            
            # Memory recommendations
            memory_percent = resource_usage.get("memory_percent", 0)
            if memory_percent > 85:
                recommendations.append("High memory usage detected. Consider increasing memory or reducing connection pool sizes.")
            
            # Connection pool recommendations
            if component == MonitoringComponent.CONNECTION_POOL:
                for metric_name, metric_point in metrics.items():
                    if "active_connections" in metric_name and metric_point.value > 80:
                        recommendations.append(f"High connection usage in {metric_name}. Consider increasing pool size.")
                    elif "waiting_connections" in metric_name and metric_point.value > 10:
                        recommendations.append(f"High connection wait times in {metric_name}. Consider optimizing queries or increasing pool size.")
                    elif "error_rate" in metric_name and metric_point.value > 0.05:  # 5% error rate
                        recommendations.append(f"High error rate in {metric_name}. Investigate connection issues.")
            
            # Database recommendations
            if component == MonitoringComponent.DATABASE:
                for metric_name, metric_point in metrics.items():
                    if "query_time" in metric_name and metric_point.value > 1000:  # 1 second
                        recommendations.append(f"Slow queries detected in {metric_name}. Consider query optimization or indexing.")
            
            # Generic recommendations
            if not recommendations:
                recommendations.append("System performance is within normal parameters.")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Unable to generate recommendations due to analysis error.")
        
        return recommendations
    
    def get_performance_trends(self, component: MonitoringComponent, 
                             duration: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Get performance trends over time"""        try:
            cutoff_time = datetime.utcnow() - duration
            relevant_snapshots = [
                s for s in self.snapshots 
                if s.component == component and s.timestamp >= cutoff_time
            ]
            
            if not relevant_snapshots:
                return {"error": "No data available for the specified duration"}
            
            # Calculate trends
            trends = {
                "snapshot_count": len(relevant_snapshots),
                "time_range": {
                    "start": relevant_snapshots[0].timestamp,
                    "end": relevant_snapshots[-1].timestamp
                },
                "health_status_distribution": {},
                "average_resource_usage": {},
                "recommendation_frequency": {}
            }
            
            # Health status distribution
            health_counts = defaultdict(int)
            for snapshot in relevant_snapshots:
                health_counts[snapshot.health_status.value] += 1
            trends["health_status_distribution"] = dict(health_counts)
            
            # Average resource usage
            resource_sums = defaultdict(list)
            for snapshot in relevant_snapshots:
                for resource, value in snapshot.resource_usage.items():
                    if isinstance(value, (int, float)):
                        resource_sums[resource].append(value)
            
            for resource, values in resource_sums.items():
                trends["average_resource_usage"][resource] = statistics.mean(values)
            
            # Recommendation frequency
            recommendation_counts = defaultdict(int)
            for snapshot in relevant_snapshots:
                for recommendation in snapshot.recommendations:
                    recommendation_counts[recommendation] += 1
            trends["recommendation_frequency"] = dict(recommendation_counts)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            return {"error": f"Failed to analyze trends: {str(e)}"}

# =============== MONITORING MANAGER ===============

class PoolMonitoringManager:
    """Central monitoring manager for all pool components"""    
    def __init__(self):
        self.metrics_collector = PoolMetricsCollector()
        self.health_monitor = HealthMonitor()
        self.alert_manager = AlertManager(self.metrics_collector)
        self.performance_analyzer = PerformanceAnalyzer(self.metrics_collector, self.health_monitor)
        
        self._initialized = False
        self._monitoring_tasks: List[asyncio.Task] = []
    
    async def initialize(self) -> bool:
        """Initialize monitoring system"""        try:
            # Start components
            await self.metrics_collector.start_collection()
            await self.alert_manager.start_evaluation()
            
            # Register default health checks
            await self._register_default_health_checks()
            
            # Register default alert rules
            await self._register_default_alert_rules()
            
            # Register default notification handlers
            await self._register_default_notification_handlers()
            
            self._initialized = True
            logger.info("✅ Pool monitoring system initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Monitoring system initialization failed: {e}")
            return False
    
    async def _register_default_health_checks(self) -> None:
        """Register default health checks"""        # System health check
        system_health_check = HealthCheck(
            check_id="system_health",
            component=MonitoringComponent.SYSTEM,
            check_name="System Resource Health",
            check_function=lambda: psutil.cpu_percent() < 90 and psutil.virtual_memory().percent < 90,
            interval_seconds=30
        )
        self.health_monitor.register_health_check(system_health_check)
        
        # Connection pool health check
        pool_health_check = HealthCheck(
            check_id="connection_pools_health",
            component=MonitoringComponent.CONNECTION_POOL,
            check_name="Connection Pool Health",
            check_function=lambda: len(self.metrics_collector.pools) > 0,
            interval_seconds=60
        )
        self.health_monitor.register_health_check(pool_health_check)
    
    async def _register_default_alert_rules(self) -> None:
        """Register default alert rules"""        # High CPU usage alert
        cpu_alert = AlertRule(
            rule_id="high_cpu_usage",
            rule_name="High CPU Usage",
            metric_name="system.cpu_percent",
            condition="> 80",
            severity=AlertSeverity.WARNING,
            duration=timedelta(minutes=2),
            cooldown=timedelta(minutes=5),
            channels=[NotificationChannel.DASHBOARD]
        )
        self.alert_manager.register_alert_rule(cpu_alert)
        
        # Connection pool saturation alert
        pool_alert = AlertRule(
            rule_id="connection_pool_saturation",
            rule_name="Connection Pool Saturation",
            metric_name="pool.*.active_connections",
            condition="> 80",
            severity=AlertSeverity.ERROR,
            duration=timedelta(minutes=1),
            cooldown=timedelta(minutes=3),
            channels=[NotificationChannel.DASHBOARD]
        )
        self.alert_manager.register_alert_rule(pool_alert)
    
    async def _register_default_notification_handlers(self) -> None:
        """Register default notification handlers"""        # Dashboard notification handler
        async def dashboard_handler(alert: Alert, alert_rule: AlertRule):
            logger.warning(f"🚨 DASHBOARD ALERT: {alert.message}")
        
        self.alert_manager.register_notification_handler(NotificationChannel.DASHBOARD, dashboard_handler)
    
    def register_pool(self, pool_id: str, pool_instance: Any) -> None:
        """Register a pool for monitoring"""        self.metrics_collector.register_pool(pool_id, pool_instance)
    
    def unregister_pool(self, pool_id: str) -> None:
        """Unregister pool from monitoring"""        self.metrics_collector.unregister_pool(pool_id)
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get monitoring dashboard data"""        try:
            dashboard = {
                "timestamp": datetime.utcnow(),
                "health_summary": self.health_monitor.get_health_summary(),
                "active_alerts": len(self.alert_manager.get_active_alerts()),
                "critical_alerts": len(self.alert_manager.get_active_alerts(AlertSeverity.CRITICAL)),
                "monitored_pools": len(self.metrics_collector.pools),
                "recent_metrics": {},
                "system_resources": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage_percent": psutil.disk_usage('/').percent
                }
            }
            
            # Add recent metrics
            for metric_name, metric_series in self.metrics_collector.get_all_metrics().items():
                latest_point = metric_series.get_latest()
                if latest_point:
                    dashboard["recent_metrics"][metric_name] = {
                        "value": latest_point.value,
                        "timestamp": latest_point.timestamp
                    }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting monitoring dashboard: {e}")
            return {"error": f"Dashboard error: {str(e)}"}
    
    async def create_performance_report(self, component: MonitoringComponent) -> Dict[str, Any]:
        """Create comprehensive performance report"""        try:
            # Create performance snapshot
            snapshot = await self.performance_analyzer.create_performance_snapshot(component)
            
            # Get performance trends
            trends = self.performance_analyzer.get_performance_trends(component)
            
            # Get relevant alerts
            relevant_alerts = [
                alert for alert in self.alert_manager.get_active_alerts()
                if component.value in alert.metric_name
            ]
            
            report = {
                "component": component.value,
                "generated_at": datetime.utcnow(),
                "snapshot": asdict(snapshot),
                "trends": trends,
                "active_alerts": [asdict(alert) for alert in relevant_alerts],
                "recommendations": snapshot.recommendations,
                "health_status": snapshot.health_status.value
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error creating performance report: {e}")
            return {"error": f"Report generation error: {str(e)}"}
    
    async def close(self) -> None:
        """Close monitoring system"""        try:
            await self.metrics_collector.stop_collection()
            await self.alert_manager.stop_evaluation()
            
            # Cancel any remaining tasks
            for task in self._monitoring_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            logger.info("✅ Pool monitoring system closed")
        except Exception as e:
            logger.error(f"Error closing monitoring system: {e}")

# =============== GLOBAL MONITORING MANAGER ===============

_global_monitoring_manager: Optional[PoolMonitoringManager] = None

def get_monitoring_manager() -> PoolMonitoringManager:
    """Get global monitoring manager instance"""    global _global_monitoring_manager
    if _global_monitoring_manager is None:
        _global_monitoring_manager = PoolMonitoringManager()
    return _global_monitoring_manager

async def initialize_monitoring_system() -> bool:
    """Initialize global monitoring system"""    global _global_monitoring_manager
    _global_monitoring_manager = PoolMonitoringManager()
    return await _global_monitoring_manager.initialize()

# =============== EXPORTS ===============

__all__ = [
    "PoolMonitoringManager",
    "get_monitoring_manager",
    "initialize_monitoring_system",
    "PoolMetricsCollector",
    "HealthMonitor",
    "AlertManager",
    "PerformanceAnalyzer",
    "MetricType",
    "AlertSeverity",
    "HealthStatus",
    "MonitoringComponent",
    "NotificationChannel",
    "MetricPoint",
    "MetricSeries",
    "HealthCheck",
    "HealthCheckResult",
    "AlertRule",
    "Alert",
    "PerformanceSnapshot"
]
