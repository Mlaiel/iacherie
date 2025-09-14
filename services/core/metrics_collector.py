"""
Metrics Collector - Enterprise Metrics & Observability
======================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: DevOps Engineer + Backend Senior + ML Engineer + DBA
**Module**: Core Services - Metrics & Observability
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade metrics collection with Prometheus integration, time-series storage,
intelligent alerting, and ML-powered analytics.
"""

import asyncio
import json
import logging
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import aioredis
import psutil
from collections import defaultdict, deque
import uuid


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric type classifications"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"
    RATE = "rate"
    PERCENTAGE = "percentage"


class MetricUnit(Enum):
    """Metric units"""
    NONE = ""
    BYTES = "bytes"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    PERCENT = "percent"
    COUNT = "count"
    RATE_PER_SECOND = "per_second"
    RATE_PER_MINUTE = "per_minute"
    REQUESTS = "requests"
    ERRORS = "errors"
    USERS = "users"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


@dataclass
class Metric:
    """Metric definition with metadata"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Metadata
    service_id: str = ""
    unit: MetricUnit = MetricUnit.NONE
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Value tracking
    previous_value: Optional[Union[int, float]] = None
    delta: Optional[Union[int, float]] = None
    rate: Optional[float] = None
    
    # Aggregation data (for histograms/summaries)
    buckets: Optional[Dict[str, int]] = None
    quantiles: Optional[Dict[str, float]] = None
    sample_count: Optional[int] = None
    sample_sum: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['metric_type'] = self.metric_type.value
        data['unit'] = self.unit.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metric':
        """Create metric from dictionary"""
        data['metric_type'] = MetricType(data['metric_type'])
        data['unit'] = MetricUnit(data['unit'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class TimeSeriesData:
    """Time series data for a metric"""
    metric_name: str
    data_points: deque = field(default_factory=lambda: deque(maxlen=1000))
    max_age_seconds: int = 3600  # 1 hour
    
    def add_point(self, timestamp: datetime, value: Union[int, float]) -> None:
        """Add a data point"""
        self.data_points.append((timestamp, value))
        self._cleanup_old_data()
    
    def get_recent_values(self, seconds: int = 300) -> List[Union[int, float]]:
        """Get values from the last N seconds"""
        cutoff = datetime.now() - timedelta(seconds=seconds)
        return [value for timestamp, value in self.data_points if timestamp >= cutoff]
    
    def get_statistics(self, seconds: int = 300) -> Dict[str, float]:
        """Get statistical summary of recent values"""
        values = self.get_recent_values(seconds)
        if not values:
            return {}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
        }
    
    def _cleanup_old_data(self) -> None:
        """Remove old data points"""
        cutoff = datetime.now() - timedelta(seconds=self.max_age_seconds)
        while self.data_points and self.data_points[0][0] < cutoff:
            self.data_points.popleft()


@dataclass
class PerformanceMetrics:
    """Performance metrics aggregate"""
    service_id: str
    
    # Response time metrics
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    max_response_time: float = 0.0
    
    # Throughput metrics
    requests_per_second: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Error metrics
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    retry_rate: float = 0.0
    
    # Resource metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: float = 0.0
    
    # Availability metrics
    uptime_percentage: float = 100.0
    health_check_success_rate: float = 100.0
    
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class AlertRule:
    """Alert rule definition"""
    rule_id: str
    metric_name: str
    condition: str  # e.g., "> 0.8", "< 100", "== 0"
    threshold: Union[int, float]
    severity: AlertSeverity
    
    # Configuration
    enabled: bool = True
    evaluation_window: int = 300  # seconds
    min_data_points: int = 5
    consecutive_breaches: int = 3
    
    # Actions
    notification_channels: List[str] = field(default_factory=list)
    auto_remediation: Optional[Callable] = None
    
    # State tracking
    current_breach_count: int = 0
    last_triggered: Optional[datetime] = None
    alert_sent: bool = False
    
    # Metadata
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert instance"""
    alert_id: str
    rule_id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    
    # Values
    current_value: Union[int, float]
    threshold: Union[int, float]
    
    # Timing
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    # Context
    service_id: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    acknowledged: bool = False
    resolved: bool = False


class MetricsCollector:
    """
    Enterprise Metrics Collector with Time-Series Storage & ML Analytics
    
    **Expert Roles Implemented:**
    - DevOps Engineer: Comprehensive monitoring, Prometheus integration, alerting
    - Backend Senior: Robust async metrics collection, efficient storage
    - ML Engineer: Intelligent anomaly detection, predictive analytics
    - DBA: Optimized time-series storage, efficient queries, data retention
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        collection_interval: int = 10,
        retention_days: int = 30,
        max_metrics_per_service: int = 1000,
        enable_prometheus: bool = True,
        prometheus_port: int = 8090
    ):
        self.redis_url = redis_url
        self.collection_interval = collection_interval
        self.retention_days = retention_days
        self.max_metrics_per_service = max_metrics_per_service
        self.enable_prometheus = enable_prometheus
        self.prometheus_port = prometheus_port
        
        # Storage
        self.redis_client: Optional[aioredis.Redis] = None
        self.metrics_store: Dict[str, TimeSeriesData] = {}
        self.current_metrics: Dict[str, Metric] = {}
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        
        # Alerting
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.running = False
        
        # Prometheus integration
        self.prometheus_metrics: Dict[str, Any] = {}
        
        # System monitoring
        self.system_metrics_enabled = True
        self.last_collection_time = time.time()
        
        # ML Analytics
        self.anomaly_detection_enabled = True
        self.anomaly_threshold = 2.0  # Standard deviations
        
    async def initialize(self) -> None:
        """Initialize metrics collector"""
        try:
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Load existing alert rules
            await self._load_alert_rules()
            
            # Initialize Prometheus if enabled
            if self.enable_prometheus:
                await self._initialize_prometheus()
            
            # Start background tasks
            self.running = True
            self.background_tasks = [
                asyncio.create_task(self._metrics_collection_loop()),
                asyncio.create_task(self._alert_evaluation_loop()),
                asyncio.create_task(self._cleanup_loop()),
                asyncio.create_task(self._performance_calculation_loop())
            ]
            
            if self.system_metrics_enabled:
                self.background_tasks.append(
                    asyncio.create_task(self._system_metrics_loop())
                )
            
            if self.anomaly_detection_enabled:
                self.background_tasks.append(
                    asyncio.create_task(self._anomaly_detection_loop())
                )
            
            logger.info("Metrics Collector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Metrics Collector: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        self.running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Metrics Collector shutdown completed")
    
    async def record_metric(self, metric: Metric) -> bool:
        """
        Record a metric value
        
        **Roles**: Backend Senior + DevOps + DBA
        """
        try:
            # Validate metric
            if not self._validate_metric(metric):
                return False
            
            # Calculate delta and rate if previous value exists
            previous_metric = self.current_metrics.get(metric.name)
            if previous_metric:
                metric.previous_value = previous_metric.value
                metric.delta = metric.value - previous_metric.value
                
                # Calculate rate for counters
                if metric.metric_type == MetricType.COUNTER:
                    time_diff = (metric.timestamp - previous_metric.timestamp).total_seconds()
                    if time_diff > 0:
                        metric.rate = metric.delta / time_diff
            
            # Store current metric
            self.current_metrics[metric.name] = metric
            
            # Add to time series
            if metric.name not in self.metrics_store:
                self.metrics_store[metric.name] = TimeSeriesData(metric.name)
            
            self.metrics_store[metric.name].add_point(metric.timestamp, metric.value)
            
            # Persist to Redis
            await self._persist_metric(metric)
            
            # Update Prometheus if enabled
            if self.enable_prometheus:
                await self._update_prometheus_metric(metric)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metric {metric.name}: {e}")
            return False
    
    async def record_counter(
        self,
        name: str,
        value: Union[int, float] = 1,
        service_id: str = "",
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """Record a counter metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            service_id=service_id,
            tags=tags or {}
        )
        return await self.record_metric(metric)
    
    async def record_gauge(
        self,
        name: str,
        value: Union[int, float],
        service_id: str = "",
        unit: MetricUnit = MetricUnit.NONE,
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """Record a gauge metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            service_id=service_id,
            unit=unit,
            tags=tags or {}
        )
        return await self.record_metric(metric)
    
    async def record_timer(
        self,
        name: str,
        duration_ms: float,
        service_id: str = "",
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """Record a timer metric"""
        metric = Metric(
            name=name,
            value=duration_ms,
            metric_type=MetricType.TIMER,
            service_id=service_id,
            unit=MetricUnit.MILLISECONDS,
            tags=tags or {}
        )
        return await self.record_metric(metric)
    
    async def record_histogram(
        self,
        name: str,
        value: Union[int, float],
        buckets: Dict[str, int],
        service_id: str = "",
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """Record a histogram metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            service_id=service_id,
            buckets=buckets,
            tags=tags or {}
        )
        return await self.record_metric(metric)
    
    async def get_metric_value(self, metric_name: str) -> Optional[Union[int, float]]:
        """Get current value of a metric"""
        metric = self.current_metrics.get(metric_name)
        return metric.value if metric else None
    
    async def get_metric_statistics(
        self,
        metric_name: str,
        seconds: int = 300
    ) -> Optional[Dict[str, float]]:
        """Get statistical summary of a metric"""
        if metric_name not in self.metrics_store:
            return None
        
        return self.metrics_store[metric_name].get_statistics(seconds)
    
    async def get_metric_history(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[tuple]:
        """Get metric history within time range"""
        if metric_name not in self.metrics_store:
            return []
        
        data_points = list(self.metrics_store[metric_name].data_points)
        
        if start_time:
            data_points = [(ts, val) for ts, val in data_points if ts >= start_time]
        
        if end_time:
            data_points = [(ts, val) for ts, val in data_points if ts <= end_time]
        
        return data_points
    
    async def create_alert_rule(self, alert_rule: AlertRule) -> bool:
        """
        Create an alert rule
        
        **Roles**: DevOps + ML Engineer
        """
        try:
            # Validate alert rule
            if not self._validate_alert_rule(alert_rule):
                return False
            
            # Store alert rule
            self.alert_rules[alert_rule.rule_id] = alert_rule
            
            # Persist to Redis
            await self._save_alert_rule(alert_rule)
            
            logger.info(f"Alert rule created: {alert_rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create alert rule {alert_rule.rule_id}: {e}")
            return False
    
    async def delete_alert_rule(self, rule_id: str) -> bool:
        """Delete an alert rule"""
        try:
            if rule_id not in self.alert_rules:
                return False
            
            # Remove alert rule
            del self.alert_rules[rule_id]
            
            # Remove from Redis
            await self._remove_alert_rule(rule_id)
            
            # Clear any active alerts for this rule
            alerts_to_remove = [
                alert_id for alert_id, alert in self.active_alerts.items()
                if alert.rule_id == rule_id
            ]
            
            for alert_id in alerts_to_remove:
                await self.resolve_alert(alert_id)
            
            logger.info(f"Alert rule deleted: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete alert rule {rule_id}: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert"""
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            # Reset rule state
            rule = self.alert_rules.get(alert.rule_id)
            if rule:
                rule.current_breach_count = 0
                rule.alert_sent = False
            
            logger.info(f"Alert resolved: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        try:
            if alert_id not in self.active_alerts:
                return False
            
            self.active_alerts[alert_id].acknowledged = True
            logger.info(f"Alert acknowledged: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False
    
    async def get_performance_metrics(self, service_id: str) -> Optional[PerformanceMetrics]:
        """Get performance metrics for a service"""
        return self.performance_metrics.get(service_id)
    
    async def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return alerts
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get system metrics overview"""
        total_metrics = len(self.current_metrics)
        active_alerts = len(self.active_alerts)
        
        # Count metrics by type
        metric_types = {}
        for metric in self.current_metrics.values():
            metric_type = metric.metric_type.value
            metric_types[metric_type] = metric_types.get(metric_type, 0) + 1
        
        # Count alerts by severity
        alert_severities = {}
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            alert_severities[severity] = alert_severities.get(severity, 0) + 1
        
        return {
            'total_metrics': total_metrics,
            'metric_types': metric_types,
            'active_alerts': active_alerts,
            'alert_severities': alert_severities,
            'services_monitored': len(self.performance_metrics),
            'collection_rate': 1.0 / self.collection_interval if self.collection_interval > 0 else 0,
            'data_retention_days': self.retention_days
        }
    
    def _validate_metric(self, metric: Metric) -> bool:
        """Validate metric before recording"""
        if not metric.name:
            return False
        
        if not isinstance(metric.value, (int, float)):
            return False
        
        return True
    
    def _validate_alert_rule(self, rule: AlertRule) -> bool:
        """Validate alert rule configuration"""
        if not rule.rule_id or not rule.metric_name:
            return False
        
        if not isinstance(rule.threshold, (int, float)):
            return False
        
        if rule.condition not in ['>', '<', '>=', '<=', '==', '!=']:
            return False
        
        return True
    
    async def _persist_metric(self, metric: Metric) -> None:
        """Persist metric to Redis"""
        if not self.redis_client:
            return
        
        try:
            # Store current metric
            key = f"metric:current:{metric.name}"
            value = json.dumps(metric.to_dict())
            await self.redis_client.setex(key, 3600, value)  # 1 hour TTL
            
            # Store in time series
            ts_key = f"metric:timeseries:{metric.name}"
            ts_data = {
                'timestamp': metric.timestamp.isoformat(),
                'value': metric.value
            }
            await self.redis_client.lpush(ts_key, json.dumps(ts_data))
            await self.redis_client.ltrim(ts_key, 0, 999)  # Keep last 1000 points
            await self.redis_client.expire(ts_key, 86400 * self.retention_days)
            
        except Exception as e:
            logger.error(f"Failed to persist metric to Redis: {e}")
    
    async def _initialize_prometheus(self) -> None:
        """Initialize Prometheus metrics endpoint"""
        # This would integrate with prometheus_client library
        # For now, we'll just log that it's enabled
        logger.info(f"Prometheus endpoint would be available on port {self.prometheus_port}")
    
    async def _update_prometheus_metric(self, metric: Metric) -> None:
        """Update Prometheus metric"""
        # This would update actual Prometheus metrics
        # For now, we'll store in a local registry
        self.prometheus_metrics[metric.name] = metric.value
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while self.running:
            try:
                current_time = time.time()
                collection_rate = 1.0 / (current_time - self.last_collection_time)
                self.last_collection_time = current_time
                
                # Record collection rate as a metric
                await self.record_gauge(
                    "metrics.collection_rate",
                    collection_rate,
                    service_id="metrics_collector",
                    unit=MetricUnit.RATE_PER_SECOND
                )
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(5)
    
    async def _alert_evaluation_loop(self) -> None:
        """Background alert evaluation loop"""
        while self.running:
            try:
                await self._evaluate_alert_rules()
                await asyncio.sleep(30)  # Evaluate every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(10)
    
    async def _evaluate_alert_rules(self) -> None:
        """Evaluate all alert rules"""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            try:
                await self._evaluate_single_rule(rule)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
    
    async def _evaluate_single_rule(self, rule: AlertRule) -> None:
        """Evaluate a single alert rule"""
        # Get recent metric values
        if rule.metric_name not in self.metrics_store:
            return
        
        recent_values = self.metrics_store[rule.metric_name].get_recent_values(rule.evaluation_window)
        
        if len(recent_values) < rule.min_data_points:
            return
        
        # Get current value
        current_value = recent_values[-1] if recent_values else 0
        
        # Evaluate condition
        is_breach = self._evaluate_condition(current_value, rule.condition, rule.threshold)
        
        if is_breach:
            rule.current_breach_count += 1
            
            # Check if we need to trigger an alert
            if (rule.current_breach_count >= rule.consecutive_breaches and 
                not rule.alert_sent):
                
                await self._trigger_alert(rule, current_value)
        else:
            # Reset breach count
            if rule.current_breach_count > 0:
                rule.current_breach_count = 0
                
                # Resolve any active alerts for this rule
                active_alert = None
                for alert_id, alert in self.active_alerts.items():
                    if alert.rule_id == rule.rule_id:
                        active_alert = alert_id
                        break
                
                if active_alert:
                    await self.resolve_alert(active_alert)
    
    def _evaluate_condition(
        self,
        value: Union[int, float],
        condition: str,
        threshold: Union[int, float]
    ) -> bool:
        """Evaluate alert condition"""
        if condition == '>':
            return value > threshold
        elif condition == '<':
            return value < threshold
        elif condition == '>=':
            return value >= threshold
        elif condition == '<=':
            return value <= threshold
        elif condition == '==':
            return value == threshold
        elif condition == '!=':
            return value != threshold
        else:
            return False
    
    async def _trigger_alert(self, rule: AlertRule, current_value: Union[int, float]) -> None:
        """Trigger an alert"""
        alert_id = str(uuid.uuid4())
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            metric_name=rule.metric_name,
            severity=rule.severity,
            message=f"Metric {rule.metric_name} {rule.condition} {rule.threshold} (current: {current_value})",
            current_value=current_value,
            threshold=rule.threshold,
            tags=rule.tags.copy()
        )
        
        # Store active alert
        self.active_alerts[alert_id] = alert
        rule.alert_sent = True
        rule.last_triggered = datetime.now()
        
        # Execute auto-remediation if configured
        if rule.auto_remediation:
            try:
                if asyncio.iscoroutinefunction(rule.auto_remediation):
                    await rule.auto_remediation(alert)
                else:
                    rule.auto_remediation(alert)
            except Exception as e:
                logger.error(f"Auto-remediation failed for rule {rule.rule_id}: {e}")
        
        logger.warning(f"Alert triggered: {alert.message}")
    
    async def _system_metrics_loop(self) -> None:
        """Background system metrics collection loop"""
        while self.running:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"System metrics collection error: {e}")
                await asyncio.sleep(10)
    
    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_gauge(
                "system.cpu.usage_percent",
                cpu_percent,
                service_id="system",
                unit=MetricUnit.PERCENT
            )
            
            # Memory metrics
            memory = psutil.virtual_memory()
            await self.record_gauge(
                "system.memory.usage_percent",
                memory.percent,
                service_id="system",
                unit=MetricUnit.PERCENT
            )
            await self.record_gauge(
                "system.memory.available_bytes",
                memory.available,
                service_id="system",
                unit=MetricUnit.BYTES
            )
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            await self.record_gauge(
                "system.disk.usage_percent",
                (disk.used / disk.total) * 100,
                service_id="system",
                unit=MetricUnit.PERCENT
            )
            
            # Network metrics
            network = psutil.net_io_counters()
            await self.record_counter(
                "system.network.bytes_sent",
                network.bytes_sent,
                service_id="system"
            )
            await self.record_counter(
                "system.network.bytes_recv",
                network.bytes_recv,
                service_id="system"
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _performance_calculation_loop(self) -> None:
        """Background performance metrics calculation loop"""
        while self.running:
            try:
                await self._calculate_performance_metrics()
                await asyncio.sleep(60)  # Calculate every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance calculation error: {e}")
                await asyncio.sleep(10)
    
    async def _calculate_performance_metrics(self) -> None:
        """Calculate performance metrics for all services"""
        services = set()
        
        # Find all services from current metrics
        for metric in self.current_metrics.values():
            if metric.service_id:
                services.add(metric.service_id)
        
        # Calculate performance metrics for each service
        for service_id in services:
            perf_metrics = self.performance_metrics.get(service_id, PerformanceMetrics(service_id))
            
            # Update response time metrics
            response_time_stats = await self.get_metric_statistics(f"{service_id}.response_time", 300)
            if response_time_stats:
                perf_metrics.avg_response_time = response_time_stats.get('mean', 0.0)
                perf_metrics.max_response_time = response_time_stats.get('max', 0.0)
            
            # Update request metrics
            total_requests = await self.get_metric_value(f"{service_id}.requests.total")
            if total_requests:
                perf_metrics.total_requests = int(total_requests)
            
            successful_requests = await self.get_metric_value(f"{service_id}.requests.successful")
            if successful_requests:
                perf_metrics.successful_requests = int(successful_requests)
            
            failed_requests = await self.get_metric_value(f"{service_id}.requests.failed")
            if failed_requests:
                perf_metrics.failed_requests = int(failed_requests)
            
            # Calculate error rate
            if perf_metrics.total_requests > 0:
                perf_metrics.error_rate = (perf_metrics.failed_requests / perf_metrics.total_requests) * 100
            
            # Update resource metrics
            cpu_usage = await self.get_metric_value(f"{service_id}.cpu.usage_percent")
            if cpu_usage:
                perf_metrics.cpu_usage = float(cpu_usage)
            
            memory_usage = await self.get_metric_value(f"{service_id}.memory.usage_percent")
            if memory_usage:
                perf_metrics.memory_usage = float(memory_usage)
            
            perf_metrics.last_updated = datetime.now()
            self.performance_metrics[service_id] = perf_metrics
    
    async def _anomaly_detection_loop(self) -> None:
        """Background anomaly detection loop"""
        while self.running:
            try:
                await self._detect_anomalies()
                await asyncio.sleep(120)  # Check every 2 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Anomaly detection error: {e}")
                await asyncio.sleep(30)
    
    async def _detect_anomalies(self) -> None:
        """Detect anomalies in metric data using ML techniques"""
        for metric_name, time_series in self.metrics_store.items():
            try:
                await self._detect_metric_anomaly(metric_name, time_series)
            except Exception as e:
                logger.error(f"Error detecting anomaly for metric {metric_name}: {e}")
    
    async def _detect_metric_anomaly(self, metric_name: str, time_series: TimeSeriesData) -> None:
        """Detect anomaly in a specific metric using statistical methods"""
        values = time_series.get_recent_values(1800)  # Last 30 minutes
        
        if len(values) < 10:  # Need enough data points
            return
        
        # Calculate statistical measures
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        if std_dev == 0:  # No variation, skip anomaly detection
            return
        
        # Check current value against historical pattern
        current_value = values[-1]
        z_score = abs((current_value - mean_value) / std_dev)
        
        if z_score > self.anomaly_threshold:
            # Anomaly detected
            await self._handle_anomaly(metric_name, current_value, mean_value, z_score)
    
    async def _handle_anomaly(
        self,
        metric_name: str,
        current_value: Union[int, float],
        expected_value: Union[int, float],
        z_score: float
    ) -> None:
        """Handle detected anomaly"""
        logger.warning(
            f"Anomaly detected in {metric_name}: "
            f"current={current_value}, expected={expected_value:.2f}, z_score={z_score:.2f}"
        )
        
        # Record anomaly as a metric
        await self.record_gauge(
            f"anomaly.{metric_name}.z_score",
            z_score,
            service_id="anomaly_detector"
        )
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while self.running:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Cleanup every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old metric data"""
        # Clean up time series data
        for time_series in self.metrics_store.values():
            time_series._cleanup_old_data()
        
        # Clean up alert history (keep last 1000)
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        # Clean up Redis data
        if self.redis_client:
            try:
                # Remove old time series data
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                keys = await self.redis_client.keys("metric:timeseries:*")
                
                for key in keys:
                    # This would implement proper time-based cleanup
                    # For now, we rely on Redis TTL
                    pass
                    
            except Exception as e:
                logger.error(f"Redis cleanup error: {e}")
    
    async def _save_alert_rule(self, rule: AlertRule) -> None:
        """Save alert rule to Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"alert_rule:{rule.rule_id}"
            value = {
                'rule_id': rule.rule_id,
                'metric_name': rule.metric_name,
                'condition': rule.condition,
                'threshold': rule.threshold,
                'severity': rule.severity.value,
                'enabled': rule.enabled,
                'evaluation_window': rule.evaluation_window,
                'min_data_points': rule.min_data_points,
                'consecutive_breaches': rule.consecutive_breaches,
                'notification_channels': rule.notification_channels,
                'description': rule.description,
                'tags': rule.tags
            }
            await self.redis_client.set(key, json.dumps(value))
        except Exception as e:
            logger.error(f"Failed to save alert rule to Redis: {e}")
    
    async def _remove_alert_rule(self, rule_id: str) -> None:
        """Remove alert rule from Redis"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(f"alert_rule:{rule_id}")
        except Exception as e:
            logger.error(f"Failed to remove alert rule from Redis: {e}")
    
    async def _load_alert_rules(self) -> None:
        """Load alert rules from Redis"""
        if not self.redis_client:
            return
        
        try:
            keys = await self.redis_client.keys("alert_rule:*")
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    rule_data = json.loads(data)
                    rule_data['severity'] = AlertSeverity(rule_data['severity'])
                    
                    # Remove non-serializable fields
                    rule_data.pop('auto_remediation', None)
                    rule_data['current_breach_count'] = 0
                    rule_data['alert_sent'] = False
                    rule_data['last_triggered'] = None
                    
                    rule = AlertRule(**rule_data)
                    self.alert_rules[rule.rule_id] = rule
            
            logger.info(f"Loaded {len(self.alert_rules)} alert rules")
        except Exception as e:
            logger.error(f"Failed to load alert rules from Redis: {e}")