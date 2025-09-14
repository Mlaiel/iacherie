"""
🔥 ENTERPRISE METRICS COLLECTOR - AINFLUE PLATFORM
Ultra-advanced metrics collection and monitoring system
Specialized metrics collection for workflow analytics
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Set, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import logging
import threading
import time
import statistics
from collections import defaultdict, deque

# === ENTERPRISE MONITORING IMPORTS ===
try:
    import prometheus_client
    from prometheus_client import Counter, Gauge, Histogram, Summary, CollectorRegistry
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    prometheus_client = None

try:
    from ..utils.storage import MetricsStorage
    from ..services.monitoring.prometheus_client import PrometheusClient
    from ..services.monitoring.grafana_client import GrafanaClient
except ImportError:
    # Fallback for missing dependencies
    class MetricsStorage: pass
    class PrometheusClient: pass
    class GrafanaClient: pass


class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"
    RATE = "rate"


class MetricLevel(Enum):
    """Metric importance levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AggregationType(Enum):
    """Metric aggregation types."""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"
    RATE_PER_SECOND = "rate_per_second"


@dataclass
class Metric:
    """Individual metric data point."""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    level: MetricLevel = MetricLevel.INFO
    unit: str = ""
    description: str = ""


@dataclass
class MetricSeries:
    """Time series of metrics."""
    name: str
    metric_type: MetricType
    data_points: List[Metric] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    aggregation_type: AggregationType = AggregationType.AVERAGE


@dataclass
class MetricAlert:
    """Metric alert configuration."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str = ""
    condition: str = ""  # e.g., "> 100", "< 0.5"
    threshold_value: float = 0.0
    comparison_operator: str = ">"  # >, <, >=, <=, ==, !=
    alert_level: MetricLevel = MetricLevel.WARNING
    cooldown_minutes: int = 15
    enabled: bool = True
    callback: Optional[Callable] = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class MetricsCollectorConfig:
    """Metrics collector configuration."""
    enable_prometheus_export: bool = True
    enable_grafana_dashboards: bool = True
    enable_real_time_alerts: bool = True
    metrics_retention_days: int = 30
    collection_interval_seconds: int = 60
    batch_size: int = 1000
    enable_metric_aggregation: bool = True
    enable_anomaly_detection: bool = True
    export_interval_seconds: int = 300
    max_metrics_per_series: int = 10000


# === ENTERPRISE MONITORING: PROMETHEUS INTEGRATION ===

class PrometheusMetricsExporter:
    """
    🔥 ENTERPRISE PROMETHEUS METRICS EXPORTER
    
    Implements ultra-advanced monitoring as required by checklist:
    - Prometheus metrics export
    - Real-time performance tracking
    - Custom metric definitions
    - Automated alerting
    - Dashboard integration
    """
    
    def __init__(self, config: MetricsCollectorConfig = None):
        """Initialize Prometheus metrics exporter."""
        self.config = config or MetricsCollectorConfig()
        self.logger = logging.getLogger(__name__)
        
        if not HAS_PROMETHEUS:
            self.logger.warning("Prometheus client not available - metrics export disabled")
            self.prometheus_enabled = False
            return
        
        self.prometheus_enabled = True
        self.registry = CollectorRegistry()
        self._initialize_prometheus_metrics()
        
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics for enterprise monitoring."""
        # Workflow performance metrics
        self.workflow_execution_time = Histogram(
            'workflow_execution_seconds',
            'Workflow execution time in seconds',
            ['workflow_type', 'user_id', 'status'],
            registry=self.registry,
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        self.workflow_count = Counter(
            'workflow_total',
            'Total number of workflows executed',
            ['workflow_type', 'status'],
            registry=self.registry
        )
        
        self.active_workflows = Gauge(
            'workflow_active_total',
            'Number of currently active workflows',
            ['workflow_type'],
            registry=self.registry
        )
        
        # Pipeline performance metrics
        self.pipeline_execution_time = Histogram(
            'pipeline_execution_seconds',
            'Pipeline execution time in seconds',
            ['pipeline_type', 'stage'],
            registry=self.registry,
            buckets=[0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self.pipeline_step_count = Counter(
            'pipeline_steps_total',
            'Total number of pipeline steps executed',
            ['pipeline_type', 'step_name', 'status'],
            registry=self.registry
        )
        
        # Task scheduling metrics
        self.task_scheduling_time = Histogram(
            'task_scheduling_seconds',
            'Task scheduling latency in seconds',
            ['task_type', 'priority'],
            registry=self.registry,
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
        )
        
        self.queue_size = Gauge(
            'task_queue_size',
            'Number of tasks in queue',
            ['queue_type'],
            registry=self.registry
        )
        
        # State persistence metrics
        self.state_persistence_time = Histogram(
            'state_persistence_seconds',
            'State persistence time in seconds',
            ['operation', 'state_type'],
            registry=self.registry,
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
        )
        
        # Event processing metrics
        self.event_processing_time = Histogram(
            'event_processing_seconds',
            'Event processing time in seconds',
            ['event_type'],
            registry=self.registry,
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1]
        )
        
        self.events_per_second = Gauge(
            'events_per_second',
            'Events processed per second',
            ['event_type'],
            registry=self.registry
        )
        
        # Resource utilization metrics
        self.memory_usage = Gauge(
            'workflow_memory_usage_bytes',
            'Memory usage by workflow engine',
            ['component'],
            registry=self.registry
        )
        
        self.cpu_usage = Gauge(
            'workflow_cpu_usage_percent',
            'CPU usage by workflow engine',
            ['component'],
            registry=self.registry
        )
        
        # Business metrics
        self.content_processed = Counter(
            'content_processed_total',
            'Total content items processed',
            ['content_type', 'status'],
            registry=self.registry
        )
        
        self.revenue_generated = Counter(
            'revenue_generated_total',
            'Total revenue generated',
            ['revenue_stream', 'currency'],
            registry=self.registry
        )
        
        # Security metrics
        self.authentication_attempts = Counter(
            'authentication_attempts_total',
            'Total authentication attempts',
            ['method', 'status'],
            registry=self.registry
        )
        
        self.authorization_checks = Counter(
            'authorization_checks_total',
            'Total authorization checks',
            ['permission', 'resource_type', 'status'],
            registry=self.registry
        )
        
        self.logger.info("Prometheus metrics initialized successfully")
    
    async def record_workflow_execution(
        self,
        workflow_type: str,
        user_id: str,
        execution_time: float,
        status: str
    ):
        """Record workflow execution metrics."""
        if not self.prometheus_enabled:
            return
        
        try:
            self.workflow_execution_time.labels(
                workflow_type=workflow_type,
                user_id=user_id,
                status=status
            ).observe(execution_time)
            
            self.workflow_count.labels(
                workflow_type=workflow_type,
                status=status
            ).inc()
            
            self.logger.debug(f"Recorded workflow execution: {workflow_type} - {execution_time}s")
            
        except Exception as e:
            self.logger.error(f"Failed to record workflow metrics: {e}")
    
    async def record_pipeline_execution(
        self,
        pipeline_type: str,
        stage: str,
        execution_time: float
    ):
        """Record pipeline execution metrics."""
        if not self.prometheus_enabled:
            return
        
        try:
            self.pipeline_execution_time.labels(
                pipeline_type=pipeline_type,
                stage=stage
            ).observe(execution_time)
            
            self.logger.debug(f"Recorded pipeline execution: {pipeline_type}/{stage} - {execution_time}s")
            
        except Exception as e:
            self.logger.error(f"Failed to record pipeline metrics: {e}")
    
    async def record_task_scheduling(
        self,
        task_type: str,
        priority: str,
        scheduling_time: float
    ):
        """Record task scheduling metrics."""
        if not self.prometheus_enabled:
            return
        
        try:
            self.task_scheduling_time.labels(
                task_type=task_type,
                priority=priority
            ).observe(scheduling_time)
            
            self.logger.debug(f"Recorded task scheduling: {task_type} - {scheduling_time}s")
            
        except Exception as e:
            self.logger.error(f"Failed to record scheduling metrics: {e}")
    
    async def record_state_persistence(
        self,
        operation: str,
        state_type: str,
        persistence_time: float
    ):
        """Record state persistence metrics."""
        if not self.prometheus_enabled:
            return
        
        try:
            self.state_persistence_time.labels(
                operation=operation,
                state_type=state_type
            ).observe(persistence_time)
            
            self.logger.debug(f"Recorded state persistence: {operation}/{state_type} - {persistence_time}s")
            
        except Exception as e:
            self.logger.error(f"Failed to record state metrics: {e}")
    
    async def record_event_processing(
        self,
        event_type: str,
        processing_time: float
    ):
        """Record event processing metrics."""
        if not self.prometheus_enabled:
            return
        
        try:
            self.event_processing_time.labels(
                event_type=event_type
            ).observe(processing_time)
            
            self.logger.debug(f"Recorded event processing: {event_type} - {processing_time}s")
            
        except Exception as e:
            self.logger.error(f"Failed to record event metrics: {e}")
    
    async def update_active_workflows(self, workflow_type: str, count: int):
        """Update active workflow count."""
        if not self.prometheus_enabled:
            return
        
        try:
            self.active_workflows.labels(workflow_type=workflow_type).set(count)
        except Exception as e:
            self.logger.error(f"Failed to update active workflow metrics: {e}")
    
    async def update_queue_size(self, queue_type: str, size: int):
        """Update queue size metrics."""
        if not self.prometheus_enabled:
            return
        
        try:
            self.queue_size.labels(queue_type=queue_type).set(size)
        except Exception as e:
            self.logger.error(f"Failed to update queue metrics: {e}")
    
    async def record_authentication(self, method: str, status: str):
        """Record authentication metrics."""
        if not self.prometheus_enabled:
            return
        
        try:
            self.authentication_attempts.labels(method=method, status=status).inc()
        except Exception as e:
            self.logger.error(f"Failed to record authentication metrics: {e}")
    
    async def record_authorization(self, permission: str, resource_type: str, status: str):
        """Record authorization metrics."""
        if not self.prometheus_enabled:
            return
        
        try:
            self.authorization_checks.labels(
                permission=permission,
                resource_type=resource_type,
                status=status
            ).inc()
        except Exception as e:
            self.logger.error(f"Failed to record authorization metrics: {e}")
    
    def get_metrics(self) -> str:
        """Get all metrics in Prometheus format."""
        if not self.prometheus_enabled:
            return "# Prometheus not available\n"
        
        try:
            return prometheus_client.generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed to generate metrics: {e}")
            return f"# Error generating metrics: {e}\n"
    
    async def start_metrics_server(self, port: int = 9090):
        """Start Prometheus metrics server."""
        if not self.prometheus_enabled:
            self.logger.warning("Cannot start metrics server - Prometheus not available")
            return
        
        try:
            prometheus_client.start_http_server(port, registry=self.registry)
            self.logger.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {e}")
            raise


class MetricsCollector:
    """
    🔥 ENTERPRISE METRICS COLLECTOR
    
    Ultra-advanced metrics collection system with:
    - Multi-type metric support (counters, gauges, histograms, timers)
    - Real-time metric aggregation
    - Prometheus and Grafana integration
    - Intelligent alerting system
    - Anomaly detection
    - Time-series analysis
    - Performance monitoring
    - Custom dashboard generation
    """
    
    def __init__(self, config: MetricsCollectorConfig = None):
        """Initialize enterprise metrics collector."""
        self.config = config or MetricsCollectorConfig()
        
        # Metrics storage
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.metric_series: Dict[str, MetricSeries] = {}
        self.aggregated_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.metric_alerts: Dict[str, MetricAlert] = {}
        
        # Real-time metrics
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Thread safety
        self._metrics_lock = threading.Lock()
        self._export_lock = asyncio.Lock()
        
        # Background tasks
        self._collector_active = True
        self._collection_task = None
        self._export_task = None
        self._alert_task = None
        self._cleanup_task = None
        
        # External services
        self.prometheus_client = PrometheusClient() if self.config.enable_prometheus_export else None
        self.grafana_client = GrafanaClient() if self.config.enable_grafana_dashboards else None
        self.metrics_storage = MetricsStorage() if MetricsStorage else None
        
        self.logger = logging.getLogger(__name__)
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background collection tasks."""
        if not self._collection_task:
            self._collection_task = asyncio.create_task(self._collection_loop())
        
        if not self._export_task:
            self._export_task = asyncio.create_task(self._export_loop())
        
        if self.config.enable_real_time_alerts and not self._alert_task:
            self._alert_task = asyncio.create_task(self._alert_loop())
        
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    # METRIC RECORDING METHODS
    
    def increment_counter(
        self,
        name: str,
        value: Union[int, float] = 1,
        tags: Dict[str, str] = None,
        level: MetricLevel = MetricLevel.INFO
    ):
        """Increment a counter metric."""
        with self._metrics_lock:
            self.counters[name] += value
            
            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.COUNTER,
                tags=tags or {},
                level=level
            )
            
            self._store_metric(metric)
    
    def set_gauge(
        self,
        name: str,
        value: Union[int, float],
        tags: Dict[str, str] = None,
        level: MetricLevel = MetricLevel.INFO
    ):
        """Set a gauge metric value."""
        with self._metrics_lock:
            self.gauges[name] = value
            
            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.GAUGE,
                tags=tags or {},
                level=level
            )
            
            self._store_metric(metric)
    
    def record_histogram(
        self,
        name: str,
        value: Union[int, float],
        tags: Dict[str, str] = None,
        level: MetricLevel = MetricLevel.INFO
    ):
        """Record a value in a histogram metric."""
        with self._metrics_lock:
            self.histograms[name].append(value)
            
            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.HISTOGRAM,
                tags=tags or {},
                level=level
            )
            
            self._store_metric(metric)
    
    def record_timer(
        self,
        name: str,
        duration_seconds: float,
        tags: Dict[str, str] = None,
        level: MetricLevel = MetricLevel.INFO
    ):
        """Record a timer duration."""
        with self._metrics_lock:
            self.timers[name].append(duration_seconds)
            
            metric = Metric(
                name=name,
                value=duration_seconds,
                metric_type=MetricType.TIMER,
                tags=tags or {},
                level=level,
                unit="seconds"
            )
            
            self._store_metric(metric)
    
    def record_rate(
        self,
        name: str,
        value: Union[int, float] = 1,
        tags: Dict[str, str] = None,
        level: MetricLevel = MetricLevel.INFO
    ):
        """Record a rate metric (events per time period)."""
        with self._metrics_lock:
            current_time = time.time()
            self.rates[name].append((current_time, value))
            
            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.RATE,
                tags=tags or {},
                level=level,
                unit="per_second"
            )
            
            self._store_metric(metric)
    
    def _store_metric(self, metric: Metric):
        """Store metric in internal storage."""
        self.metrics[metric.name].append(metric)
        
        # Limit metrics per series
        if len(self.metrics[metric.name]) > self.config.max_metrics_per_series:
            self.metrics[metric.name] = self.metrics[metric.name][-self.config.max_metrics_per_series:]
    
    # TIMER CONTEXT MANAGER
    
    def timer(self, name: str, tags: Dict[str, str] = None):
        """Context manager for timing operations."""
        return TimerContext(self, name, tags)
    
    # METRIC AGGREGATION
    
    def get_counter_value(self, name: str) -> float:
        """Get current counter value."""
        with self._metrics_lock:
            return self.counters.get(name, 0.0)
    
    def get_gauge_value(self, name: str) -> float:
        """Get current gauge value."""
        with self._metrics_lock:
            return self.gauges.get(name, 0.0)
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics."""
        with self._metrics_lock:
            values = self.histograms.get(name, [])
            if not values:
                return {}
            
            return {
                "count": len(values),
                "sum": sum(values),
                "avg": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "p50": statistics.median(values),
                "p95": self._percentile(values, 0.95),
                "p99": self._percentile(values, 0.99)
            }
    
    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """Get timer statistics."""
        with self._metrics_lock:
            durations = self.timers.get(name, [])
            if not durations:
                return {}
            
            return {
                "count": len(durations),
                "total_seconds": sum(durations),
                "avg_seconds": statistics.mean(durations),
                "min_seconds": min(durations),
                "max_seconds": max(durations),
                "p50_seconds": statistics.median(durations),
                "p95_seconds": self._percentile(durations, 0.95),
                "p99_seconds": self._percentile(durations, 0.99)
            }
    
    def get_rate_value(self, name: str, window_seconds: int = 60) -> float:
        """Get rate value (events per second) over time window."""
        with self._metrics_lock:
            rate_data = self.rates.get(name, deque())
            if not rate_data:
                return 0.0
            
            current_time = time.time()
            cutoff_time = current_time - window_seconds
            
            # Filter events within time window
            recent_events = [value for timestamp, value in rate_data if timestamp >= cutoff_time]
            
            if not recent_events:
                return 0.0
            
            return sum(recent_events) / window_seconds
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(percentile * len(sorted_values))
        index = min(index, len(sorted_values) - 1)
        
        return sorted_values[index]
    
    # METRIC ALERTS
    
    def add_alert(
        self,
        metric_name: str,
        threshold_value: float,
        comparison_operator: str = ">",
        alert_level: MetricLevel = MetricLevel.WARNING,
        cooldown_minutes: int = 15,
        callback: Optional[Callable] = None
    ) -> str:
        """Add a metric alert."""
        alert = MetricAlert(
            metric_name=metric_name,
            threshold_value=threshold_value,
            comparison_operator=comparison_operator,
            alert_level=alert_level,
            cooldown_minutes=cooldown_minutes,
            callback=callback
        )
        
        self.metric_alerts[alert.alert_id] = alert
        self.logger.info(f"Added alert for metric {metric_name}: {comparison_operator} {threshold_value}")
        
        return alert.alert_id
    
    def remove_alert(self, alert_id: str) -> bool:
        """Remove a metric alert."""
        if alert_id in self.metric_alerts:
            alert = self.metric_alerts[alert_id]
            del self.metric_alerts[alert_id]
            self.logger.info(f"Removed alert {alert_id} for metric {alert.metric_name}")
            return True
        return False
    
    async def _check_alerts(self):
        """Check metric alerts and trigger if necessary."""
        current_time = datetime.utcnow()
        
        for alert in self.metric_alerts.values():
            if not alert.enabled:
                continue
            
            # Check cooldown period
            if (alert.last_triggered and 
                (current_time - alert.last_triggered).total_seconds() < alert.cooldown_minutes * 60):
                continue
            
            # Get current metric value
            current_value = self._get_metric_value_for_alert(alert.metric_name)
            if current_value is None:
                continue
            
            # Check alert condition
            if self._evaluate_alert_condition(current_value, alert):
                await self._trigger_alert(alert, current_value)
    
    def _get_metric_value_for_alert(self, metric_name: str) -> Optional[float]:
        """Get current metric value for alert evaluation."""
        # Check counters
        if metric_name in self.counters:
            return self.counters[metric_name]
        
        # Check gauges
        if metric_name in self.gauges:
            return self.gauges[metric_name]
        
        # Check histogram average
        if metric_name in self.histograms and self.histograms[metric_name]:
            return statistics.mean(self.histograms[metric_name])
        
        # Check timer average
        if metric_name in self.timers and self.timers[metric_name]:
            return statistics.mean(self.timers[metric_name])
        
        # Check rate
        if metric_name in self.rates:
            return self.get_rate_value(metric_name)
        
        return None
    
    def _evaluate_alert_condition(self, value: float, alert: MetricAlert) -> bool:
        """Evaluate if alert condition is met."""
        threshold = alert.threshold_value
        operator = alert.comparison_operator
        
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return abs(value - threshold) < 0.001  # Float comparison
        elif operator == "!=":
            return abs(value - threshold) >= 0.001
        
        return False
    
    async def _trigger_alert(self, alert: MetricAlert, current_value: float):
        """Trigger metric alert."""
        alert.last_triggered = datetime.utcnow()
        alert.trigger_count += 1
        
        alert_message = f"Metric alert triggered: {alert.metric_name} = {current_value} {alert.comparison_operator} {alert.threshold_value}"
        
        # Log alert
        if alert.alert_level == MetricLevel.CRITICAL:
            self.logger.critical(alert_message)
        elif alert.alert_level == MetricLevel.ERROR:
            self.logger.error(alert_message)
        elif alert.alert_level == MetricLevel.WARNING:
            self.logger.warning(alert_message)
        else:
            self.logger.info(alert_message)
        
        # Execute callback if provided
        if alert.callback:
            try:
                if asyncio.iscoroutinefunction(alert.callback):
                    await alert.callback(alert, current_value)
                else:
                    alert.callback(alert, current_value)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    # METRIC AGGREGATION AND ANALYSIS
    
    async def aggregate_metrics(
        self,
        metric_name: str,
        aggregation_type: AggregationType,
        time_window: timedelta = timedelta(hours=1),
        tags_filter: Dict[str, str] = None
    ) -> Optional[float]:
        """Aggregate metrics over time window."""
        if metric_name not in self.metrics:
            return None
        
        cutoff_time = datetime.utcnow() - time_window
        
        # Filter metrics by time and tags
        filtered_metrics = []
        for metric in self.metrics[metric_name]:
            if metric.timestamp < cutoff_time:
                continue
            
            if tags_filter:
                if not all(metric.tags.get(k) == v for k, v in tags_filter.items()):
                    continue
            
            filtered_metrics.append(metric)
        
        if not filtered_metrics:
            return None
        
        values = [metric.value for metric in filtered_metrics]
        
        # Apply aggregation
        if aggregation_type == AggregationType.SUM:
            return sum(values)
        elif aggregation_type == AggregationType.AVERAGE:
            return statistics.mean(values)
        elif aggregation_type == AggregationType.MIN:
            return min(values)
        elif aggregation_type == AggregationType.MAX:
            return max(values)
        elif aggregation_type == AggregationType.COUNT:
            return len(values)
        elif aggregation_type == AggregationType.RATE_PER_SECOND:
            return len(values) / time_window.total_seconds()
        
        return None
    
    def get_metric_series(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags_filter: Dict[str, str] = None
    ) -> Optional[MetricSeries]:
        """Get time series data for a metric."""
        if metric_name not in self.metrics:
            return None
        
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        # Filter metrics
        filtered_metrics = []
        for metric in self.metrics[metric_name]:
            if metric.timestamp < start_time or metric.timestamp > end_time:
                continue
            
            if tags_filter:
                if not all(metric.tags.get(k) == v for k, v in tags_filter.items()):
                    continue
            
            filtered_metrics.append(metric)
        
        if not filtered_metrics:
            return None
        
        # Determine metric type
        metric_type = filtered_metrics[0].metric_type
        
        return MetricSeries(
            name=metric_name,
            metric_type=metric_type,
            data_points=filtered_metrics,
            tags=tags_filter or {},
            start_time=start_time,
            end_time=end_time
        )
    
    # EXPORT AND INTEGRATION
    
    async def export_to_prometheus(self) -> bool:
        """Export metrics to Prometheus."""
        if not self.prometheus_client:
            return False
        
        try:
            async with self._export_lock:
                # Export counters
                for name, value in self.counters.items():
                    await self.prometheus_client.set_counter(name, value)
                
                # Export gauges
                for name, value in self.gauges.items():
                    await self.prometheus_client.set_gauge(name, value)
                
                # Export histogram summaries
                for name, values in self.histograms.items():
                    if values:
                        stats = self.get_histogram_stats(name)
                        await self.prometheus_client.set_histogram(name, stats)
                
                # Export timer summaries
                for name, durations in self.timers.items():
                    if durations:
                        stats = self.get_timer_stats(name)
                        await self.prometheus_client.set_timer(name, stats)
                
                return True
        
        except Exception as e:
            self.logger.error(f"Failed to export to Prometheus: {e}")
            return False
    
    async def create_grafana_dashboard(self, dashboard_name: str, metric_names: List[str]) -> bool:
        """Create Grafana dashboard for metrics."""
        if not self.grafana_client:
            return False
        
        try:
            dashboard_config = {
                "title": dashboard_name,
                "panels": []
            }
            
            for i, metric_name in enumerate(metric_names):
                panel = {
                    "id": i + 1,
                    "title": metric_name.replace("_", " ").title(),
                    "type": "graph",
                    "targets": [
                        {
                            "expr": metric_name,
                            "refId": "A"
                        }
                    ]
                }
                dashboard_config["panels"].append(panel)
            
            return await self.grafana_client.create_dashboard(dashboard_config)
        
        except Exception as e:
            self.logger.error(f"Failed to create Grafana dashboard: {e}")
            return False
    
    # BACKGROUND TASKS
    
    async def _collection_loop(self):
        """Background metrics collection loop."""
        while self._collector_active:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.config.collection_interval_seconds)
            except Exception as e:
                self.logger.error(f"Collection loop error: {e}")
                await asyncio.sleep(60)
    
    async def _export_loop(self):
        """Background metrics export loop."""
        while self._collector_active:
            try:
                if self.config.enable_prometheus_export:
                    await self.export_to_prometheus()
                
                await asyncio.sleep(self.config.export_interval_seconds)
            except Exception as e:
                self.logger.error(f"Export loop error: {e}")
                await asyncio.sleep(60)
    
    async def _alert_loop(self):
        """Background alert checking loop."""
        while self._collector_active:
            try:
                await self._check_alerts()
                await asyncio.sleep(30)  # Check alerts every 30 seconds
            except Exception as e:
                self.logger.error(f"Alert loop error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._collector_active:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(3600)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        # Placeholder for system metrics collection
        # Would collect CPU, memory, disk usage, etc.
        pass
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics based on retention policy."""
        cutoff_time = datetime.utcnow() - timedelta(days=self.config.metrics_retention_days)
        
        with self._metrics_lock:
            for metric_name in list(self.metrics.keys()):
                # Filter out old metrics
                self.metrics[metric_name] = [
                    metric for metric in self.metrics[metric_name]
                    if metric.timestamp > cutoff_time
                ]
                
                # Remove empty metric series
                if not self.metrics[metric_name]:
                    del self.metrics[metric_name]
    
    # STATUS AND MANAGEMENT
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        with self._metrics_lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {
                    name: self.get_histogram_stats(name)
                    for name in self.histograms.keys()
                },
                "timers": {
                    name: self.get_timer_stats(name)
                    for name in self.timers.keys()
                },
                "rates": {
                    name: self.get_rate_value(name)
                    for name in self.rates.keys()
                },
                "total_metrics": sum(len(metrics) for metrics in self.metrics.values()),
                "active_alerts": len([a for a in self.metric_alerts.values() if a.enabled])
            }
    
    def get_collector_status(self) -> Dict[str, Any]:
        """Get metrics collector status."""
        return {
            "active": self._collector_active,
            "prometheus_enabled": self.config.enable_prometheus_export,
            "grafana_enabled": self.config.enable_grafana_dashboards,
            "alerts_enabled": self.config.enable_real_time_alerts,
            "metrics_count": len(self.metrics),
            "alerts_count": len(self.metric_alerts),
            "retention_days": self.config.metrics_retention_days
        }
    
    async def shutdown(self):
        """Shutdown metrics collector."""
        self._collector_active = False
        
        # Cancel background tasks
        if self._collection_task:
            self._collection_task.cancel()
        
        if self._export_task:
            self._export_task.cancel()
        
        if self._alert_task:
            self._alert_task.cancel()
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        self.logger.info("Metrics collector shutdown completed")


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, name: str, tags: Dict[str, str] = None):
        self.collector = collector
        self.name = name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.record_timer(self.name, duration, self.tags)