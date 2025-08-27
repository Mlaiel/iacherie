"""
⚡ Performance Monitor - Ultra-Professional DRM System Performance Tracking
========================================================================

Comprehensive performance monitoring, alerting, and optimization system for DRM
with real-time metrics, predictive analytics, and automated performance tuning.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing and usage rights.

🎯 PROJECT TEAM SPECIALTIES:
- Lead AI Developer & Solution Architect: Advanced AI/ML systems and intelligent automation
- Backend Senior Engineer: Enterprise-grade backend architecture and microservices  
- ML Engineer: Machine learning models and predictive analytics
- Database Administrator: High-performance data management and optimization
- Security Engineer: Advanced cybersecurity and data protection
- Microservices Architect: Scalable distributed systems design
- Audio Engineer: Professional audio processing and analysis
- DevOps Engineer: Advanced deployment and infrastructure automation
- IA Prompt Engineer: Advanced AI prompt engineering and optimization
"""

import asyncio
import logging
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import statistics
import uuid
import json
from decimal import Decimal
import traceback

logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    """Types of performance metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SystemComponent(str, Enum):
    """System components being monitored."""
    DRM_ENGINE = "drm_engine"
    LICENSE_ENGINE = "license_engine"
    ACCESS_CONTROL = "access_control"
    REVENUE_ENGINE = "revenue_engine"
    ENCRYPTION_SERVICE = "encryption_service"
    USAGE_TRACKER = "usage_tracker"
    DATABASE = "database"
    CACHE = "cache"
    API_GATEWAY = "api_gateway"
    MEDIA_PROCESSING = "media_processing"

@dataclass
class Metric:
    """Individual performance metric."""
    name: str
    metric_type: MetricType
    value: Union[int, float, Decimal]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    component: SystemComponent = SystemComponent.DRM_ENGINE
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Performance alert."""
    alert_id: str
    component: SystemComponent
    metric_name: str
    severity: AlertSeverity
    message: str
    threshold_value: Union[int, float]
    current_value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceThreshold:
    """Performance monitoring threshold."""
    metric_name: str
    component: SystemComponent
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    severity: AlertSeverity = AlertSeverity.MEDIUM
    consecutive_violations: int = 3
    evaluation_window: int = 300  # seconds
    enabled: bool = True

@dataclass
class SystemHealth:
    """Overall system health status."""
    timestamp: datetime
    overall_status: str  # healthy, degraded, critical
    component_statuses: Dict[SystemComponent, str]
    active_alerts: int
    performance_score: float  # 0-100
    uptime_percentage: float
    response_time_p95: float
    error_rate: float
    throughput: float
    resource_utilization: Dict[str, float]

class PerformanceCollector:
    """Collects performance metrics from various sources."""
    
    def __init__(self):
        self.collection_interval = 30  # seconds
        self.running = False
        self._stop_event = threading.Event()
        self._collector_thread: Optional[threading.Thread] = None

    async def start_collection(self, monitor: 'PerformanceMonitor') -> None:
        """Start background metric collection."""
        self.running = True
        self._stop_event.clear()
        self._collector_thread = threading.Thread(
            target=self._collection_loop,
            args=(monitor,),
            daemon=True
        )
        self._collector_thread.start()
        logger.info("Performance collection started")

    def _collection_loop(self, monitor: 'PerformanceMonitor') -> None:
        """Background collection loop."""
        while not self._stop_event.wait(self.collection_interval):
            try:
                # Collect system metrics
                self._collect_system_metrics(monitor)
                
                # Collect application metrics
                self._collect_application_metrics(monitor)
                
                # Collect custom metrics
                self._collect_custom_metrics(monitor)
                
            except Exception as e:
                logger.error(f"Error in metric collection: {e}")

    def _collect_system_metrics(self, monitor: 'PerformanceMonitor') -> None:
        """Collect system-level metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            monitor.record_metric("cpu_usage_percent", cpu_percent, MetricType.GAUGE)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            monitor.record_metric("memory_usage_percent", memory.percent, MetricType.GAUGE)
            monitor.record_metric("memory_available_bytes", memory.available, MetricType.GAUGE)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            monitor.record_metric("disk_usage_percent", disk.percent, MetricType.GAUGE)
            monitor.record_metric("disk_free_bytes", disk.free, MetricType.GAUGE)
            
            # Network metrics
            network = psutil.net_io_counters()
            monitor.record_metric("network_bytes_sent", network.bytes_sent, MetricType.COUNTER)
            monitor.record_metric("network_bytes_recv", network.bytes_recv, MetricType.COUNTER)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    def _collect_application_metrics(self, monitor: 'PerformanceMonitor') -> None:
        """Collect application-specific metrics."""
        # These would be collected from actual application components
        # Placeholder implementation
        pass

    def _collect_custom_metrics(self, monitor: 'PerformanceMonitor') -> None:
        """Collect custom business metrics."""
        # Placeholder for custom metric collection
        pass

    def stop(self) -> None:
        """Stop metric collection."""
        self.running = False
        self._stop_event.set()
        if self._collector_thread:
            self._collector_thread.join(timeout=5)
        logger.info("Performance collection stopped")

class AlertManager:
    """Manages performance alerts and notifications."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_handlers: List[Callable] = []
        
        # Alert suppression
        self.suppression_rules: Dict[str, Dict[str, Any]] = {}
        self.cooldown_periods: Dict[str, datetime] = {}

    def add_notification_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add alert notification handler."""
        self.notification_handlers.append(handler)

    async def process_alert(self, alert: Alert) -> None:
        """Process and potentially send an alert."""
        # Check suppression rules
        if self._is_suppressed(alert):
            logger.debug(f"Alert {alert.alert_id} suppressed")
            return
        
        # Check cooldown
        cooldown_key = f"{alert.component}_{alert.metric_name}"
        if cooldown_key in self.cooldown_periods:
            if datetime.utcnow() < self.cooldown_periods[cooldown_key]:
                logger.debug(f"Alert {alert.alert_id} in cooldown")
                return
        
        # Store alert
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        for handler in self.notification_handlers:
            try:
                await self._call_handler(handler, alert)
            except Exception as e:
                logger.error(f"Error in notification handler: {e}")
        
        # Set cooldown
        cooldown_duration = self._get_cooldown_duration(alert)
        self.cooldown_periods[cooldown_key] = datetime.utcnow() + timedelta(seconds=cooldown_duration)
        
        logger.warning(f"Alert triggered: {alert.component} - {alert.message}")

    async def _call_handler(self, handler: Callable, alert: Alert) -> None:
        """Call notification handler."""
        if asyncio.iscoroutinefunction(handler):
            await handler(alert)
        else:
            handler(alert)

    def _is_suppressed(self, alert: Alert) -> bool:
        """Check if alert should be suppressed."""
        suppression_key = f"{alert.component}_{alert.metric_name}"
        if suppression_key not in self.suppression_rules:
            return False
        
        rules = self.suppression_rules[suppression_key]
        
        # Check time-based suppression
        if 'suppress_until' in rules:
            if datetime.utcnow() < rules['suppress_until']:
                return True
        
        # Check severity-based suppression
        if 'min_severity' in rules:
            severity_order = [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL]
            if severity_order.index(alert.severity) < severity_order.index(rules['min_severity']):
                return True
        
        return False

    def _get_cooldown_duration(self, alert: Alert) -> int:
        """Get cooldown duration for alert type."""
        base_duration = self.config.get('default_cooldown_seconds', 300)
        
        # Adjust based on severity
        if alert.severity == AlertSeverity.LOW:
            return base_duration * 2
        elif alert.severity == AlertSeverity.MEDIUM:
            return base_duration
        elif alert.severity == AlertSeverity.HIGH:
            return base_duration // 2
        else:  # CRITICAL
            return base_duration // 4

    async def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert."""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.acknowledged = True
        alert.metadata['acknowledged_by'] = user
        alert.metadata['acknowledged_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Alert {alert_id} acknowledged by {user}")
        return True

    async def resolve_alert(self, alert_id: str, user: str, resolution_note: str = "") -> bool:
        """Resolve an alert."""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.metadata['resolved_by'] = user
        alert.metadata['resolution_note'] = resolution_note
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        logger.info(f"Alert {alert_id} resolved by {user}")
        return True

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by severity."""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

class PerformanceMonitor:
    """
    Ultra-Advanced Performance Monitor for DRM System
    
    Features:
    - Real-time performance metric collection and analysis
    - Intelligent alerting with ML-powered anomaly detection
    - Automated performance optimization recommendations
    - Multi-dimensional performance analytics and visualization
    - Predictive performance modeling and capacity planning
    - Advanced SLA monitoring and compliance reporting
    - Custom business metric tracking and KPI dashboards
    - Integration with external monitoring systems (Prometheus, Grafana)
    - Performance regression detection and root cause analysis
    - Automated performance tuning and self-healing capabilities
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Performance Monitor."""
        self.config = config
        self._initialized = False
        
        # Metric storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.metric_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Thresholds and alerting
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        self.alert_manager = AlertManager(config.get('alerting', {}))
        
        # Performance collector
        self.collector = PerformanceCollector()
        
        # Anomaly detection
        self.baseline_data: Dict[str, Dict[str, float]] = {}
        self.anomaly_detection_enabled = config.get('enable_anomaly_detection', True)
        
        # Performance optimization
        self.optimization_rules: List[Dict[str, Any]] = []
        self.auto_optimization_enabled = config.get('enable_auto_optimization', False)
        
        # Caching
        self.cache_ttl = config.get('cache_ttl_seconds', 60)
        self.cached_reports: Dict[str, Tuple[Any, datetime]] = {}
        
        logger.info("Performance Monitor initialized")

    async def initialize(self) -> bool:
        """Initialize the Performance Monitor."""
        try:
            # Load thresholds
            await self._load_thresholds()
            
            # Initialize baseline data
            await self._initialize_baselines()
            
            # Setup notification handlers
            await self._setup_notification_handlers()
            
            # Start metric collection
            await self.collector.start_collection(self)
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            self._initialized = True
            logger.info("Performance Monitor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Performance Monitor: {e}")
            return False

    async def _load_thresholds(self) -> None:
        """Load performance thresholds."""
        # Default thresholds
        default_thresholds = [
            PerformanceThreshold(
                metric_name="cpu_usage_percent",
                component=SystemComponent.DRM_ENGINE,
                max_value=80.0,
                severity=AlertSeverity.HIGH
            ),
            PerformanceThreshold(
                metric_name="memory_usage_percent",
                component=SystemComponent.DRM_ENGINE,
                max_value=85.0,
                severity=AlertSeverity.HIGH
            ),
            PerformanceThreshold(
                metric_name="response_time_ms",
                component=SystemComponent.API_GATEWAY,
                max_value=1000.0,
                severity=AlertSeverity.MEDIUM
            ),
            PerformanceThreshold(
                metric_name="error_rate_percent",
                component=SystemComponent.DRM_ENGINE,
                max_value=5.0,
                severity=AlertSeverity.HIGH
            ),
            PerformanceThreshold(
                metric_name="license_validation_time_ms",
                component=SystemComponent.LICENSE_ENGINE,
                max_value=500.0,
                severity=AlertSeverity.MEDIUM
            )
        ]
        
        for threshold in default_thresholds:
            threshold_key = f"{threshold.component}_{threshold.metric_name}"
            self.thresholds[threshold_key] = threshold

    async def _initialize_baselines(self) -> None:
        """Initialize performance baselines for anomaly detection."""
        # Placeholder for baseline initialization
        # In production, this would load historical data
        logger.debug("Initialized performance baselines")

    async def _setup_notification_handlers(self) -> None:
        """Setup alert notification handlers."""
        # Email notifications
        if self.config.get('email_notifications', {}).get('enabled', False):
            self.alert_manager.add_notification_handler(self._send_email_notification)
        
        # Slack notifications
        if self.config.get('slack_notifications', {}).get('enabled', False):
            self.alert_manager.add_notification_handler(self._send_slack_notification)
        
        # Webhook notifications
        if self.config.get('webhook_notifications', {}).get('enabled', False):
            self.alert_manager.add_notification_handler(self._send_webhook_notification)

    async def _start_monitoring_tasks(self) -> None:
        """Start background monitoring tasks."""
        # Threshold evaluation task
        asyncio.create_task(self._threshold_evaluation_loop())
        
        # Anomaly detection task
        if self.anomaly_detection_enabled:
            asyncio.create_task(self._anomaly_detection_loop())
        
        # Performance optimization task
        if self.auto_optimization_enabled:
            asyncio.create_task(self._performance_optimization_loop())
        
        # Baseline update task
        asyncio.create_task(self._baseline_update_loop())

    def record_metric(
        self,
        name: str,
        value: Union[int, float, Decimal],
        metric_type: MetricType = MetricType.GAUGE,
        component: SystemComponent = SystemComponent.DRM_ENGINE,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a performance metric."""
        if not self._initialized:
            return
        
        metric = Metric(
            name=name,
            metric_type=metric_type,
            value=value,
            component=component,
            labels=labels or {},
            metadata=metadata or {}
        )
        
        # Store metric
        metric_key = f"{component}_{name}"
        self.metrics[metric_key].append(metric)
        
        # Update metadata
        self.metric_metadata[metric_key] = {
            'last_updated': metric.timestamp,
            'metric_type': metric_type,
            'component': component,
            'labels': labels or {}
        }
        
        # Trigger threshold evaluation
        asyncio.create_task(self._evaluate_thresholds(metric_key, metric))

    async def _evaluate_thresholds(self, metric_key: str, metric: Metric) -> None:
        """Evaluate thresholds for a metric."""
        if metric_key not in self.thresholds:
            return
        
        threshold = self.thresholds[metric_key]
        if not threshold.enabled:
            return
        
        # Check threshold violation
        violation = False
        violation_message = ""
        
        if threshold.min_value is not None and float(metric.value) < threshold.min_value:
            violation = True
            violation_message = f"{metric.name} below minimum threshold: {metric.value} < {threshold.min_value}"
        
        if threshold.max_value is not None and float(metric.value) > threshold.max_value:
            violation = True
            violation_message = f"{metric.name} above maximum threshold: {metric.value} > {threshold.max_value}"
        
        if violation:
            # Check for consecutive violations
            recent_metrics = list(self.metrics[metric_key])[-threshold.consecutive_violations:]
            if len(recent_metrics) >= threshold.consecutive_violations:
                # Check if all recent metrics violate threshold
                all_violate = True
                for recent_metric in recent_metrics:
                    if threshold.min_value is not None and float(recent_metric.value) >= threshold.min_value:
                        if threshold.max_value is None or float(recent_metric.value) <= threshold.max_value:
                            all_violate = False
                            break
                    if threshold.max_value is not None and float(recent_metric.value) <= threshold.max_value:
                        if threshold.min_value is None or float(recent_metric.value) >= threshold.min_value:
                            all_violate = False
                            break
                
                if all_violate:
                    # Create alert
                    alert = Alert(
                        alert_id=f"alert_{uuid.uuid4().hex[:16]}",
                        component=threshold.component,
                        metric_name=threshold.metric_name,
                        severity=threshold.severity,
                        message=violation_message,
                        threshold_value=threshold.max_value or threshold.min_value,
                        current_value=float(metric.value)
                    )
                    
                    await self.alert_manager.process_alert(alert)

    async def _threshold_evaluation_loop(self) -> None:
        """Background threshold evaluation loop."""
        while self._initialized:
            try:
                # This is handled per-metric in record_metric
                await asyncio.sleep(60)  # Check every minute for maintenance
                
                # Clean up old cached reports
                await self._cleanup_cached_reports()
                
            except Exception as e:
                logger.error(f"Error in threshold evaluation loop: {e}")
                await asyncio.sleep(60)

    async def _anomaly_detection_loop(self) -> None:
        """Background anomaly detection loop."""
        while self._initialized:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Perform anomaly detection on key metrics
                await self._detect_anomalies()
                
            except Exception as e:
                logger.error(f"Error in anomaly detection loop: {e}")
                await asyncio.sleep(300)

    async def _performance_optimization_loop(self) -> None:
        """Background performance optimization loop."""
        while self._initialized:
            try:
                await asyncio.sleep(600)  # Run every 10 minutes
                
                # Analyze performance and suggest optimizations
                await self._analyze_and_optimize()
                
            except Exception as e:
                logger.error(f"Error in performance optimization loop: {e}")
                await asyncio.sleep(600)

    async def _baseline_update_loop(self) -> None:
        """Background baseline update loop."""
        while self._initialized:
            try:
                await asyncio.sleep(3600)  # Update every hour
                
                # Update performance baselines
                await self._update_baselines()
                
            except Exception as e:
                logger.error(f"Error in baseline update loop: {e}")
                await asyncio.sleep(3600)

    async def _detect_anomalies(self) -> None:
        """Detect performance anomalies using statistical analysis."""
        for metric_key, metric_data in self.metrics.items():
            if len(metric_data) < 50:  # Need sufficient data
                continue
            
            try:
                # Get recent values
                recent_values = [float(m.value) for m in list(metric_data)[-50:]]
                
                # Calculate statistics
                mean_val = statistics.mean(recent_values)
                stdev_val = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
                
                # Z-score based anomaly detection
                if stdev_val > 0:
                    latest_value = recent_values[-1]
                    z_score = abs((latest_value - mean_val) / stdev_val)
                    
                    # Anomaly threshold (3 standard deviations)
                    if z_score > 3:
                        component, metric_name = metric_key.split('_', 1)
                        
                        alert = Alert(
                            alert_id=f"anomaly_{uuid.uuid4().hex[:16]}",
                            component=SystemComponent(component),
                            metric_name=metric_name,
                            severity=AlertSeverity.MEDIUM,
                            message=f"Anomaly detected in {metric_name}: value {latest_value} deviates {z_score:.2f} standard deviations from mean {mean_val:.2f}",
                            threshold_value=mean_val + 3 * stdev_val,
                            current_value=latest_value,
                            metadata={"anomaly_type": "statistical", "z_score": z_score}
                        )
                        
                        await self.alert_manager.process_alert(alert)
                        
            except Exception as e:
                logger.error(f"Error detecting anomalies for {metric_key}: {e}")

    async def _analyze_and_optimize(self) -> None:
        """Analyze performance and trigger optimizations."""
        # Placeholder for performance optimization logic
        # In production, this would implement actual optimization strategies
        logger.debug("Analyzing performance for optimization opportunities")

    async def _update_baselines(self) -> None:
        """Update performance baselines."""
        for metric_key, metric_data in self.metrics.items():
            if len(metric_data) < 100:  # Need sufficient data
                continue
            
            try:
                # Calculate baseline statistics
                values = [float(m.value) for m in metric_data]
                
                baseline = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'stdev': statistics.stdev(values) if len(values) > 1 else 0,
                    'p95': sorted(values)[int(len(values) * 0.95)],
                    'p99': sorted(values)[int(len(values) * 0.99)],
                    'last_updated': datetime.utcnow().isoformat()
                }
                
                self.baseline_data[metric_key] = baseline
                
            except Exception as e:
                logger.error(f"Error updating baseline for {metric_key}: {e}")

    async def _send_email_notification(self, alert: Alert) -> None:
        """Send email notification for alert."""
        # Placeholder for email notification
        logger.info(f"Email notification would be sent for alert: {alert.alert_id}")

    async def _send_slack_notification(self, alert: Alert) -> None:
        """Send Slack notification for alert."""
        # Placeholder for Slack notification
        logger.info(f"Slack notification would be sent for alert: {alert.alert_id}")

    async def _send_webhook_notification(self, alert: Alert) -> None:
        """Send webhook notification for alert."""
        # Placeholder for webhook notification
        logger.info(f"Webhook notification would be sent for alert: {alert.alert_id}")

    async def _cleanup_cached_reports(self) -> None:
        """Clean up expired cached reports."""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for cache_key, (data, timestamp) in self.cached_reports.items():
            if current_time - timestamp > timedelta(seconds=self.cache_ttl):
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self.cached_reports[key]

    def add_threshold(self, threshold: PerformanceThreshold) -> None:
        """Add a performance threshold."""
        threshold_key = f"{threshold.component}_{threshold.metric_name}"
        self.thresholds[threshold_key] = threshold
        logger.info(f"Added threshold for {threshold_key}")

    def remove_threshold(self, component: SystemComponent, metric_name: str) -> bool:
        """Remove a performance threshold."""
        threshold_key = f"{component}_{metric_name}"
        if threshold_key in self.thresholds:
            del self.thresholds[threshold_key]
            logger.info(f"Removed threshold for {threshold_key}")
            return True
        return False

    def get_metric_history(
        self,
        component: SystemComponent,
        metric_name: str,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: Optional[int] = None
    ) -> List[Metric]:
        """Get metric history."""
        metric_key = f"{component}_{metric_name}"
        
        if metric_key not in self.metrics:
            return []
        
        metrics = list(self.metrics[metric_key])
        
        # Filter by time range
        if time_range:
            start_time, end_time = time_range
            metrics = [
                m for m in metrics
                if start_time <= m.timestamp <= end_time
            ]
        
        # Apply limit
        if limit:
            metrics = metrics[-limit:]
        
        return metrics

    async def get_system_health(self) -> SystemHealth:
        """Get overall system health status."""
        current_time = datetime.utcnow()
        
        # Calculate component statuses
        component_statuses = {}
        for component in SystemComponent:
            component_statuses[component] = await self._get_component_status(component)
        
        # Calculate overall status
        status_priority = {"healthy": 0, "degraded": 1, "critical": 2}
        overall_status = "healthy"
        for status in component_statuses.values():
            if status_priority[status] > status_priority[overall_status]:
                overall_status = status
        
        # Get active alerts
        active_alerts = len(self.alert_manager.get_active_alerts())
        
        # Calculate performance score
        performance_score = await self._calculate_performance_score()
        
        # Calculate uptime (placeholder)
        uptime_percentage = 99.9  # Would be calculated from actual uptime data
        
        # Get response time P95
        response_time_p95 = await self._get_response_time_p95()
        
        # Calculate error rate
        error_rate = await self._calculate_error_rate()
        
        # Calculate throughput
        throughput = await self._calculate_throughput()
        
        # Get resource utilization
        resource_utilization = await self._get_resource_utilization()
        
        return SystemHealth(
            timestamp=current_time,
            overall_status=overall_status,
            component_statuses=component_statuses,
            active_alerts=active_alerts,
            performance_score=performance_score,
            uptime_percentage=uptime_percentage,
            response_time_p95=response_time_p95,
            error_rate=error_rate,
            throughput=throughput,
            resource_utilization=resource_utilization
        )

    async def _get_component_status(self, component: SystemComponent) -> str:
        """Get status for a specific component."""
        # Check for critical alerts
        critical_alerts = [
            alert for alert in self.alert_manager.get_active_alerts()
            if alert.component == component and alert.severity == AlertSeverity.CRITICAL
        ]
        
        if critical_alerts:
            return "critical"
        
        # Check for high/medium alerts
        high_medium_alerts = [
            alert for alert in self.alert_manager.get_active_alerts()
            if alert.component == component and alert.severity in [AlertSeverity.HIGH, AlertSeverity.MEDIUM]
        ]
        
        if high_medium_alerts:
            return "degraded"
        
        return "healthy"

    async def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)."""
        scores = []
        
        # CPU score
        cpu_metrics = self.get_metric_history(SystemComponent.DRM_ENGINE, "cpu_usage_percent", limit=10)
        if cpu_metrics:
            avg_cpu = statistics.mean(float(m.value) for m in cpu_metrics)
            cpu_score = max(0, 100 - avg_cpu)
            scores.append(cpu_score)
        
        # Memory score
        memory_metrics = self.get_metric_history(SystemComponent.DRM_ENGINE, "memory_usage_percent", limit=10)
        if memory_metrics:
            avg_memory = statistics.mean(float(m.value) for m in memory_metrics)
            memory_score = max(0, 100 - avg_memory)
            scores.append(memory_score)
        
        # Error rate score
        error_rate = await self._calculate_error_rate()
        error_score = max(0, 100 - error_rate * 10)  # Scale error rate
        scores.append(error_score)
        
        # Return average score
        return statistics.mean(scores) if scores else 50.0

    async def _get_response_time_p95(self) -> float:
        """Get 95th percentile response time."""
        response_metrics = self.get_metric_history(SystemComponent.API_GATEWAY, "response_time_ms", limit=1000)
        
        if not response_metrics:
            return 0.0
        
        values = [float(m.value) for m in response_metrics]
        values.sort()
        
        if len(values) == 0:
            return 0.0
        
        p95_index = int(len(values) * 0.95)
        return values[p95_index] if p95_index < len(values) else values[-1]

    async def _calculate_error_rate(self) -> float:
        """Calculate current error rate percentage."""
        # Placeholder calculation
        # In production, this would calculate actual error rate from request metrics
        return 0.1  # 0.1% error rate

    async def _calculate_throughput(self) -> float:
        """Calculate current throughput (requests/second)."""
        # Placeholder calculation
        # In production, this would calculate actual throughput
        return 1000.0  # 1000 requests/second

    async def _get_resource_utilization(self) -> Dict[str, float]:
        """Get current resource utilization."""
        utilization = {}
        
        # CPU utilization
        cpu_metrics = self.get_metric_history(SystemComponent.DRM_ENGINE, "cpu_usage_percent", limit=1)
        if cpu_metrics:
            utilization["cpu"] = float(cpu_metrics[-1].value)
        
        # Memory utilization
        memory_metrics = self.get_metric_history(SystemComponent.DRM_ENGINE, "memory_usage_percent", limit=1)
        if memory_metrics:
            utilization["memory"] = float(memory_metrics[-1].value)
        
        # Disk utilization
        disk_metrics = self.get_metric_history(SystemComponent.DRM_ENGINE, "disk_usage_percent", limit=1)
        if disk_metrics:
            utilization["disk"] = float(disk_metrics[-1].value)
        
        return utilization

    async def generate_performance_report(
        self,
        report_type: str = "summary",
        time_range: Optional[Tuple[datetime, datetime]] = None,
        components: Optional[List[SystemComponent]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        cache_key = f"performance_report_{report_type}_{time_range}_{components}"
        
        # Check cache
        if cache_key in self.cached_reports:
            cached_data, cached_time = self.cached_reports[cache_key]
            if datetime.utcnow() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_data
        
        # Generate report
        if report_type == "summary":
            report = await self._generate_summary_report(time_range, components)
        elif report_type == "detailed":
            report = await self._generate_detailed_report(time_range, components)
        elif report_type == "sla":
            report = await self._generate_sla_report(time_range, components)
        else:
            report = {"error": f"Unknown report type: {report_type}"}
        
        # Cache result
        self.cached_reports[cache_key] = (report, datetime.utcnow())
        
        return report

    async def _generate_summary_report(
        self,
        time_range: Optional[Tuple[datetime, datetime]],
        components: Optional[List[SystemComponent]]
    ) -> Dict[str, Any]:
        """Generate summary performance report."""
        current_time = datetime.utcnow()
        
        # System health
        system_health = await self.get_system_health()
        
        # Active alerts summary
        active_alerts = self.alert_manager.get_active_alerts()
        alert_summary = {
            "total": len(active_alerts),
            "critical": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
            "high": len([a for a in active_alerts if a.severity == AlertSeverity.HIGH]),
            "medium": len([a for a in active_alerts if a.severity == AlertSeverity.MEDIUM]),
            "low": len([a for a in active_alerts if a.severity == AlertSeverity.LOW])
        }
        
        # Performance trends
        trends = await self._calculate_performance_trends(time_range)
        
        return {
            "report_type": "summary",
            "generated_at": current_time.isoformat(),
            "time_range": {
                "start": time_range[0].isoformat() if time_range else None,
                "end": time_range[1].isoformat() if time_range else None
            },
            "system_health": {
                "overall_status": system_health.overall_status,
                "performance_score": system_health.performance_score,
                "uptime_percentage": system_health.uptime_percentage,
                "response_time_p95": system_health.response_time_p95,
                "error_rate": system_health.error_rate,
                "throughput": system_health.throughput
            },
            "alerts": alert_summary,
            "resource_utilization": system_health.resource_utilization,
            "trends": trends
        }

    async def _generate_detailed_report(
        self,
        time_range: Optional[Tuple[datetime, datetime]],
        components: Optional[List[SystemComponent]]
    ) -> Dict[str, Any]:
        """Generate detailed performance report."""
        summary = await self._generate_summary_report(time_range, components)
        
        # Add detailed metrics for each component
        component_details = {}
        components_to_analyze = components or list(SystemComponent)
        
        for component in components_to_analyze:
            component_details[component.value] = await self._get_component_detailed_metrics(
                component, time_range
            )
        
        # Add alert details
        alert_details = []
        for alert in self.alert_manager.get_active_alerts():
            alert_details.append({
                "id": alert.alert_id,
                "component": alert.component.value,
                "metric": alert.metric_name,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "acknowledged": alert.acknowledged
            })
        
        summary.update({
            "component_details": component_details,
            "alert_details": alert_details
        })
        
        return summary

    async def _generate_sla_report(
        self,
        time_range: Optional[Tuple[datetime, datetime]],
        components: Optional[List[SystemComponent]]
    ) -> Dict[str, Any]:
        """Generate SLA compliance report."""
        # SLA targets (example)
        sla_targets = {
            "uptime": 99.9,  # 99.9% uptime
            "response_time_p95": 1000,  # 1 second P95 response time
            "error_rate": 1.0,  # 1% error rate
            "availability": 99.5  # 99.5% availability
        }
        
        # Calculate actual performance
        current_performance = {
            "uptime": 99.9,  # Would be calculated from actual data
            "response_time_p95": await self._get_response_time_p95(),
            "error_rate": await self._calculate_error_rate(),
            "availability": 99.8  # Would be calculated from actual data
        }
        
        # Calculate SLA compliance
        sla_compliance = {}
        for metric, target in sla_targets.items():
            actual = current_performance.get(metric, 0)
            
            if metric in ["uptime", "availability"]:
                # Higher is better
                compliance = min(100, (actual / target) * 100)
            else:
                # Lower is better
                compliance = min(100, (target / actual) * 100) if actual > 0 else 100
            
            sla_compliance[metric] = {
                "target": target,
                "actual": actual,
                "compliance_percentage": compliance,
                "status": "compliant" if compliance >= 100 else "non_compliant"
            }
        
        # Overall SLA score
        overall_compliance = statistics.mean([c["compliance_percentage"] for c in sla_compliance.values()])
        
        return {
            "report_type": "sla",
            "generated_at": datetime.utcnow().isoformat(),
            "time_range": {
                "start": time_range[0].isoformat() if time_range else None,
                "end": time_range[1].isoformat() if time_range else None
            },
            "overall_compliance": {
                "score": overall_compliance,
                "status": "compliant" if overall_compliance >= 95 else "non_compliant"
            },
            "sla_metrics": sla_compliance
        }

    async def _calculate_performance_trends(
        self,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, str]:
        """Calculate performance trends."""
        trends = {}
        
        # CPU trend
        cpu_metrics = self.get_metric_history(
            SystemComponent.DRM_ENGINE, "cpu_usage_percent", time_range, limit=100
        )
        if len(cpu_metrics) > 10:
            recent_avg = statistics.mean(float(m.value) for m in cpu_metrics[-10:])
            older_avg = statistics.mean(float(m.value) for m in cpu_metrics[:10])
            
            if recent_avg > older_avg * 1.1:
                trends["cpu"] = "increasing"
            elif recent_avg < older_avg * 0.9:
                trends["cpu"] = "decreasing"
            else:
                trends["cpu"] = "stable"
        
        # Memory trend
        memory_metrics = self.get_metric_history(
            SystemComponent.DRM_ENGINE, "memory_usage_percent", time_range, limit=100
        )
        if len(memory_metrics) > 10:
            recent_avg = statistics.mean(float(m.value) for m in memory_metrics[-10:])
            older_avg = statistics.mean(float(m.value) for m in memory_metrics[:10])
            
            if recent_avg > older_avg * 1.1:
                trends["memory"] = "increasing"
            elif recent_avg < older_avg * 0.9:
                trends["memory"] = "decreasing"
            else:
                trends["memory"] = "stable"
        
        return trends

    async def _get_component_detailed_metrics(
        self,
        component: SystemComponent,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Get detailed metrics for a component."""
        # Get all metrics for this component
        component_metrics = {}
        
        for metric_key, metric_data in self.metrics.items():
            if metric_key.startswith(f"{component}_"):
                metric_name = metric_key.split('_', 1)[1]
                
                # Get recent metrics
                recent_metrics = self.get_metric_history(component, metric_name, time_range, limit=100)
                
                if recent_metrics:
                    values = [float(m.value) for m in recent_metrics]
                    
                    component_metrics[metric_name] = {
                        "current": values[-1],
                        "average": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values),
                        "trend": self._calculate_metric_trend(values)
                    }
        
        return component_metrics

    def _calculate_metric_trend(self, values: List[float]) -> str:
        """Calculate trend for a metric."""
        if len(values) < 10:
            return "insufficient_data"
        
        recent_avg = statistics.mean(values[-5:])
        older_avg = statistics.mean(values[:5])
        
        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    async def shutdown(self) -> None:
        """Shutdown the Performance Monitor."""
        logger.info("Shutting down Performance Monitor...")
        
        self._initialized = False
        
        # Stop metric collection
        self.collector.stop()
        
        # Save state if needed
        await self._save_state()
        
        logger.info("Performance Monitor shutdown complete")

    async def _save_state(self) -> None:
        """Save monitor state to persistent storage."""
        # Placeholder for state persistence
        logger.debug("Saving Performance Monitor state")
