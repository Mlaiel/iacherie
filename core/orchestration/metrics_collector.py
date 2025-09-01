"""Metrics Collector - Advanced Metrics Collection & Analytics System

Comprehensive metrics collection framework for orchestration systems with
real-time monitoring, advanced analytics, and intelligent alerting capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import statistics
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import uuid
import json

from backend.core.utils.event_dispatcher import EventDispatcher


class MetricType(Enum):
    """
Metric type classification."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"
    PERCENTAGE = "percentage"


class AggregationType(Enum):
    """Metric aggregation types."""

    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "std_dev"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricDefinition:
    """Metric definition and configuration."""
    metric_id: str
    name: str
    metric_type: MetricType
    unit: str
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    retention_period: int = 86400  # seconds
    aggregation_interval: int = 60  # seconds
    alert_rules: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricValue:
    """Individual metric measurement."""
    metric_id: str
    value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedMetric:
    """
Aggregated metric result."""
    metric_id: str
    aggregation_type: AggregationType
    value: Union[int, float]
    count: int
    start_time: datetime
    end_time: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertRule:
    """
Alert rule configuration."""
    rule_id: str
    metric_id: str
    condition: str  # e.g., "> 100", "< 0.95"
    severity: AlertSeverity
    message: str
    threshold_value: Union[int, float]
    time_window: int = 300  # seconds
    cooldown_period: int = 600  # seconds
    enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert instance."""
    alert_id: str
    rule_id: str
    metric_id: str
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    metric_value: Union[int, float]
    threshold_value: Union[int, float]
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dashboard:
    """
Metrics dashboard configuration."""
    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    refresh_interval: int = 30  # seconds
    auto_refresh: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """
    Advanced metrics collection and analytics system for orchestration monitoring.
    
    Provides comprehensive metrics capabilities including:
    - Real-time metric collection and storage
    - Multi-type aggregation with flexible time windows
    - Intelligent alerting with threshold-based rules
    - Performance analytics and trend analysis
    - Custom dashboard creation and visualization
    - Distributed metrics collection support
    """
    
    def __init__(self, retention_days: int = 7, aggregation_intervals: Optional[List[int]] = None):
        self.logger = logging.getLogger(__name__)
        self.event_dispatcher = EventDispatcher()
        
        # Core configuration
        self.retention_days = retention_days
        self.aggregation_intervals = aggregation_intervals or [60, 300, 3600]  # 1min, 5min, 1hour
        
        # Metrics storage
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.raw_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregated_metrics: Dict[str, Dict[int, List[AggregatedMetric]]] = defaultdict(lambda: defaultdict(list))
        
        # Alerting
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_cooldowns: Dict[str, datetime] = {}
        
        # Dashboards
        self.dashboards: Dict[str, Dashboard] = {}
        
        # Performance tracking
        self.collector_stats = {
            'total_metrics_collected': 0,
            'total_alerts_triggered': 0,
            'active_alert_count': 0,
            'metrics_per_second': 0.0,
            'aggregation_performance': {},
            'storage_size_mb': 0.0
        }
        
        # Background tasks
        self._start_background_tasks()
        
        self.logger.info("MetricsCollector initialized")
    
    def _start_background_tasks(self) -> None:
        """Start background metrics processing tasks."""
        asyncio.create_task(self._aggregation_task())
        asyncio.create_task(self._alert_evaluation_task())
        asyncio.create_task(self._cleanup_task())
        asyncio.create_task(self._performance_monitoring_task())
    
    async def register_metric(self, definition: MetricDefinition) -> bool:
        """
        Register metric definition.
        
        Args:
            definition: Metric definition to register
            
        Returns:
            bool: Success status
        """
        try:
            if not await self._validate_metric_definition(definition):
                return False
            
            self.metric_definitions[definition.metric_id] = definition
            
            # Register alert rules
            for rule_config in definition.alert_rules:
                await self._register_alert_rule_from_config(definition.metric_id, rule_config)
            
            await self.event_dispatcher.emit('metric_registered', {
                'metric_id': definition.metric_id,
                'metric_type': definition.metric_type.value,
                'unit': definition.unit
            })
            
            self.logger.info(f"Metric registered: {definition.metric_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register metric: {e}")
            return False
    
    async def record(self, metric_id: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None) -> bool:
        """
        Record metric value.
        
        Args:
            metric_id: Metric identifier
            value: Metric value
            tags: Optional tags for the metric
            
        Returns:
            bool: Success status
        """
        try:
            if metric_id not in self.metric_definitions:
                # Auto-register with default configuration
                await self._auto_register_metric(metric_id, value)
            
            metric_value = MetricValue(
                metric_id=metric_id,
                value=value,
                tags=tags or {}
            )
            
            # Store raw metric
            self.raw_metrics[metric_id].append(metric_value)
            self.collector_stats['total_metrics_collected'] += 1
            
            # Emit event for real-time processing
            await self.event_dispatcher.emit('metric_recorded', {
                'metric_id': metric_id,
                'value': value,
                'timestamp': metric_value.timestamp.isoformat(),
                'tags': tags or {}
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record metric: {e}")
            return False
    
    async def increment(self, metric_id: str, value: Union[int, float] = 1, tags: Optional[Dict[str, str]] = None) -> bool:
        """
        Increment counter metric.
        
        Args:
            metric_id: Metric identifier
            value: Increment value (default: 1)
            tags: Optional tags for the metric
            
        Returns:
            bool: Success status
        """
        return await self.record(metric_id, value, tags)
    
    async def gauge(self, metric_id: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None) -> bool:
        """
        Set gauge metric value.
        
        Args:
            metric_id: Metric identifier
            value: Gauge value
            tags: Optional tags for the metric
            
        Returns:
            bool: Success status
        """
        return await self.record(metric_id, value, tags)
    
    async def timer(self, metric_id: str, duration: float, tags: Optional[Dict[str, str]] = None) -> bool:
        """
        Record timer metric.
        
        Args:
            metric_id: Metric identifier
            duration: Duration in seconds
            tags: Optional tags for the metric
            
        Returns:
            bool: Success status
        """
        return await self.record(metric_id, duration, tags)
    
    async def histogram(self, metric_id: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None) -> bool:
        """
        Record histogram metric.
        
        Args:
            metric_id: Metric identifier
            value: Value to add to histogram
            tags: Optional tags for the metric
            
        Returns:
            bool: Success status
        """
        return await self.record(metric_id, value, tags)
    
    async def get_metric_values(
        self,
        metric_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[MetricValue]:
        """
        Get raw metric values within time range.
        
        Args:
            metric_id: Metric identifier
            start_time: Start time for range (default: 1 hour ago)
            end_time: End time for range (default: now)
            tags: Filter by tags
            
        Returns:
            List of metric values
        """
        try:
            if metric_id not in self.raw_metrics:
                return []
            
            end_time = end_time or datetime.now()
            start_time = start_time or (end_time - timedelta(hours=1))
            
            values = []
            for metric_value in self.raw_metrics[metric_id]:
                if start_time <= metric_value.timestamp <= end_time:
                    if not tags or self._tags_match(metric_value.tags, tags):
                        values.append(metric_value)
            
            return sorted(values, key=lambda x: x.timestamp)
            
        except Exception as e:
            self.logger.error(f"Failed to get metric values: {e}")
            return []
    
    async def get_aggregated_metrics(
        self,
        metric_id: str,
        aggregation_type: AggregationType,
        interval: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AggregatedMetric]:
        """
        Get aggregated metrics for time range.
        
        Args:
            metric_id: Metric identifier
            aggregation_type: Type of aggregation
            interval: Aggregation interval in seconds
            start_time: Start time for range
            end_time: End time for range
            
        Returns:
            List of aggregated metrics
        """
        try:
            if metric_id not in self.aggregated_metrics:
                return []
            
            if interval not in self.aggregated_metrics[metric_id]:
                return []
            
            end_time = end_time or datetime.now()
            start_time = start_time or (end_time - timedelta(hours=1))
            
            aggregated = []
            for metric in self.aggregated_metrics[metric_id][interval]:
                if (metric.aggregation_type == aggregation_type and
                    start_time <= metric.start_time <= end_time):
                    aggregated.append(metric)
            
            return sorted(aggregated, key=lambda x: x.start_time)
            
        except Exception as e:
            self.logger.error(f"Failed to get aggregated metrics: {e}")
            return []
    
    async def create_alert_rule(self, rule: AlertRule) -> bool:
        """
        Create alert rule.
        
        Args:
            rule: Alert rule configuration
            
        Returns:
            bool: Success status
        """
        try:
            if not await self._validate_alert_rule(rule):
                return False
            
            self.alert_rules[rule.rule_id] = rule
            
            await self.event_dispatcher.emit('alert_rule_created', {
                'rule_id': rule.rule_id,
                'metric_id': rule.metric_id,
                'severity': rule.severity.value,
                'threshold': rule.threshold_value
            })
            
            self.logger.info(f"Alert rule created: {rule.rule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create alert rule: {e}")
            return False
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """
        Acknowledge active alert.
        
        Args:
            alert_id: Alert identifier
            acknowledged_by: User who acknowledged the alert
            
        Returns:
            bool: Success status
        """
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            
            await self.event_dispatcher.emit('alert_acknowledged', {
                'alert_id': alert_id,
                'acknowledged_by': acknowledged_by,
                'acknowledged_at': alert.acknowledged_at.isoformat()
            })
            
            self.logger.info(f"Alert acknowledged: {alert_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve active alert.
        
        Args:
            alert_id: Alert identifier
            
        Returns:
            bool: Success status
        """
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.resolved_at = datetime.now()
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            self.collector_stats['active_alert_count'] -= 1
            
            await self.event_dispatcher.emit('alert_resolved', {
                'alert_id': alert_id,
                'resolved_at': alert.resolved_at.isoformat(),
                'duration': (alert.resolved_at - alert.triggered_at).total_seconds()
            })
            
            self.logger.info(f"Alert resolved: {alert_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resolve alert: {e}")
            return False
    
    async def create_dashboard(self, dashboard: Dashboard) -> bool:
        """
        Create metrics dashboard.
        
        Args:
            dashboard: Dashboard configuration
            
        Returns:
            bool: Success status
        """
        try:
            if not await self._validate_dashboard(dashboard):
                return False
            
            self.dashboards[dashboard.dashboard_id] = dashboard
            
            await self.event_dispatcher.emit('dashboard_created', {
                'dashboard_id': dashboard.dashboard_id,
                'name': dashboard.name,
                'widget_count': len(dashboard.widgets)
            })
            
            self.logger.info(f"Dashboard created: {dashboard.dashboard_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create dashboard: {e}")
            return False
    
    async def get_dashboard_data(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Get dashboard data with current metric values.
        
        Args:
            dashboard_id: Dashboard identifier
            
        Returns:
            Dashboard data with current values
        """
        try:
            if dashboard_id not in self.dashboards:
                return None
            
            dashboard = self.dashboards[dashboard_id]
            dashboard_data = {
                'dashboard_id': dashboard_id,
                'name': dashboard.name,
                'description': dashboard.description,
                'refresh_interval': dashboard.refresh_interval,
                'widgets': []
            }
            
            for widget_config in dashboard.widgets:
                widget_data = await self._get_widget_data(widget_config)
                dashboard_data['widgets'].append(widget_data)
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {e}")
            return None
    
    async def analyze_metrics(self, metric_id: str, time_window: int = 3600) -> Dict[str, Any]:
        """
        Perform advanced metric analysis.
        
        Args:
            metric_id: Metric identifier
            time_window: Analysis time window in seconds
            
        Returns:
            Analysis results
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(seconds=time_window)
            
            # Get raw values
            values = await self.get_metric_values(metric_id, start_time, end_time)
            
            if not values:
                return {'error': 'No data available'}
            
            numeric_values = [v.value for v in values]
            
            analysis = {
                'metric_id': metric_id,
                'time_window': time_window,
                'sample_count': len(numeric_values),
                'statistics': {
                    'min': min(numeric_values),
                    'max': max(numeric_values),
                    'mean': statistics.mean(numeric_values),
                    'median': statistics.median(numeric_values),
                    'std_dev': statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
                },
                'trends': await self._analyze_trends(numeric_values),
                'anomalies': await self._detect_anomalies(numeric_values),
                'percentiles': await self._calculate_percentiles(numeric_values)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze metrics: {e}")
            return {'error': str(e)}
    
    async def _auto_register_metric(self, metric_id: str, value: Union[int, float]) -> None:
        """Auto-register metric with default configuration."""
        metric_type = MetricType.GAUGE if isinstance(value, float) else MetricType.COUNTER
        
        definition = MetricDefinition(
            metric_id=metric_id,
            name=f"Auto-registered: {metric_id}",
            metric_type=metric_type,
            unit="count" if metric_type == MetricType.COUNTER else "value",
            description=f"Auto-generated metric for {metric_id}"
        )
        
        await self.register_metric(definition)
    
    async def _register_alert_rule_from_config(self, metric_id: str, config: Dict[str, Any]) -> None:
        """Register alert rule from configuration."""
        rule = AlertRule(
            rule_id=str(uuid.uuid4()),
            metric_id=metric_id,
            condition=config.get('condition', '> 100'),
            severity=AlertSeverity(config.get('severity', 'warning')),
            message=config.get('message', f'Alert for {metric_id}'),
            threshold_value=config.get('threshold', 100),
            time_window=config.get('time_window', 300),
            cooldown_period=config.get('cooldown', 600),
            notification_channels=config.get('notifications', [])
        )
        
        await self.create_alert_rule(rule)
    
    def _tags_match(self, metric_tags: Dict[str, str], filter_tags: Dict[str, str]) -> bool:
        """
Check if metric tags match filter tags."""
        for key, value in filter_tags.items():
            if key not in metric_tags or metric_tags[key] != value:
                return False
        return True
    
    async def _aggregation_task(self) -> None:
        """
Background task for metric aggregation."""
        while True:
            try:
                current_time = datetime.now()
                
                for interval in self.aggregation_intervals:
                    # Align to interval boundary
                    aligned_time = current_time.replace(
                        second=(current_time.second // interval) * interval,
                        microsecond=0
                    )
                    
                    for metric_id in self.metric_definitions:
                        await self._aggregate_metric(metric_id, interval, aligned_time)
                
                await asyncio.sleep(min(self.aggregation_intervals))
                
            except Exception as e:
                self.logger.error(f"Aggregation task failed: {e}")
                await asyncio.sleep(60)
    
    async def _aggregate_metric(self, metric_id: str, interval: int, end_time: datetime) -> None:
        """Aggregate metric for specific interval."""
        try:
            start_time = end_time - timedelta(seconds=interval)
            
            # Get values within interval
            values = []
            for metric_value in self.raw_metrics[metric_id]:
                if start_time <= metric_value.timestamp <= end_time:
                    values.append(metric_value.value)
            
            if not values:
                return
            
            # Create aggregations
            aggregations = [
                AggregatedMetric(
                    metric_id=metric_id,
                    aggregation_type=AggregationType.SUM,
                    value=sum(values),
                    count=len(values),
                    start_time=start_time,
                    end_time=end_time
                ),
                AggregatedMetric(
                    metric_id=metric_id,
                    aggregation_type=AggregationType.AVERAGE,
                    value=statistics.mean(values),
                    count=len(values),
                    start_time=start_time,
                    end_time=end_time
                ),
                AggregatedMetric(
                    metric_id=metric_id,
                    aggregation_type=AggregationType.MIN,
                    value=min(values),
                    count=len(values),
                    start_time=start_time,
                    end_time=end_time
                ),
                AggregatedMetric(
                    metric_id=metric_id,
                    aggregation_type=AggregationType.MAX,
                    value=max(values),
                    count=len(values),
                    start_time=start_time,
                    end_time=end_time
                )
            ]
            
            # Store aggregations
            for aggregation in aggregations:
                self.aggregated_metrics[metric_id][interval].append(aggregation)
            
            # Limit aggregated storage
            max_aggregations = (self.retention_days * 24 * 3600) // interval
            if len(self.aggregated_metrics[metric_id][interval]) > max_aggregations:
                self.aggregated_metrics[metric_id][interval] = (
                    self.aggregated_metrics[metric_id][interval][-max_aggregations:]
                )
            
        except Exception as e:
            self.logger.error(f"Metric aggregation failed: {metric_id} - {e}")
    
    async def _alert_evaluation_task(self) -> None:
        """Background task for alert evaluation."""
        while True:
            try:
                current_time = datetime.now()
                
                for rule in self.alert_rules.values():
                    if not rule.enabled:
                        continue
                    
                    # Check cooldown
                    if rule.rule_id in self.alert_cooldowns:
                        if current_time < self.alert_cooldowns[rule.rule_id]:
                            continue
                    
                    await self._evaluate_alert_rule(rule, current_time)
                
                await asyncio.sleep(30)  # Evaluate every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Alert evaluation failed: {e}")
                await asyncio.sleep(60)
    
    async def _evaluate_alert_rule(self, rule: AlertRule, current_time: datetime) -> None:
        """Evaluate individual alert rule."""
        try:
            # Get recent values
            start_time = current_time - timedelta(seconds=rule.time_window)
            values = await self.get_metric_values(rule.metric_id, start_time, current_time)
            
            if not values:
                return
            
            # Get latest value
            latest_value = values[-1].value
            
            # Evaluate condition
            triggered = self._evaluate_condition(latest_value, rule.condition, rule.threshold_value)
            
            if triggered:
                # Check if already have active alert for this rule
                existing_alert = next(
                    (alert for alert in self.active_alerts.values() if alert.rule_id == rule.rule_id),
                    None
                )
                
                if not existing_alert:
                    await self._trigger_alert(rule, latest_value, current_time)
            else:
                # Check if should resolve existing alert
                existing_alert = next(
                    (alert for alert in self.active_alerts.values() if alert.rule_id == rule.rule_id),
                    None
                )
                
                if existing_alert:
                    await self.resolve_alert(existing_alert.alert_id)
            
        except Exception as e:
            self.logger.error(f"Alert rule evaluation failed: {rule.rule_id} - {e}")
    
    def _evaluate_condition(self, value: Union[int, float], condition: str, threshold: Union[int, float]) -> bool:
        """Evaluate alert condition."""
        try:
            if condition.startswith('>'):
                return value > threshold
            elif condition.startswith('<'):
                return value < threshold
            elif condition.startswith('>='):
                return value >= threshold
            elif condition.startswith('<='):
                return value <= threshold
            elif condition.startswith('=='):
                return value == threshold
            elif condition.startswith('!='):
                return value != threshold
            else:
                return False
        except Exception:
            return False
    
    async def _trigger_alert(self, rule: AlertRule, metric_value: Union[int, float], timestamp: datetime) -> None:
        """
Trigger new alert."""
        alert_id = str(uuid.uuid4())
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            metric_id=rule.metric_id,
            severity=rule.severity,
            message=rule.message,
            triggered_at=timestamp,
            metric_value=metric_value,
            threshold_value=rule.threshold_value
        )
        
        self.active_alerts[alert_id] = alert
        self.collector_stats['active_alert_count'] += 1
        self.collector_stats['total_alerts_triggered'] += 1
        
        # Set cooldown
        self.alert_cooldowns[rule.rule_id] = timestamp + timedelta(seconds=rule.cooldown_period)
        
        await self.event_dispatcher.emit('alert_triggered', {
            'alert_id': alert_id,
            'rule_id': rule.rule_id,
            'metric_id': rule.metric_id,
            'severity': rule.severity.value,
            'message': rule.message,
            'metric_value': metric_value,
            'threshold_value': rule.threshold_value
        })
        
        self.logger.warning(f"Alert triggered: {alert_id} - {rule.message}")
    
    async def _cleanup_task(self) -> None:
        """Background task for data cleanup."""
        while True:
            try:
                cutoff_time = datetime.now() - timedelta(days=self.retention_days)
                
                # Clean raw metrics
                for metric_id in list(self.raw_metrics.keys()):
                    cleaned_metrics = deque()
                    for metric_value in self.raw_metrics[metric_id]:
                        if metric_value.timestamp >= cutoff_time:
                            cleaned_metrics.append(metric_value)
                    self.raw_metrics[metric_id] = cleaned_metrics
                
                # Clean aggregated metrics
                for metric_id in self.aggregated_metrics:
                    for interval in self.aggregated_metrics[metric_id]:
                        cleaned_aggregations = []
                        for aggregation in self.aggregated_metrics[metric_id][interval]:
                            if aggregation.end_time >= cutoff_time:
                                cleaned_aggregations.append(aggregation)
                        self.aggregated_metrics[metric_id][interval] = cleaned_aggregations
                
                # Clean alert history
                self.alert_history = [
                    alert for alert in self.alert_history
                    if alert.triggered_at >= cutoff_time
                ]
                
                # Clean cooldowns
                current_time = datetime.now()
                expired_cooldowns = [
                    rule_id for rule_id, expiry in self.alert_cooldowns.items()
                    if current_time >= expiry
                ]
                for rule_id in expired_cooldowns:
                    del self.alert_cooldowns[rule_id]
                
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                self.logger.error(f"Cleanup task failed: {e}")
                await asyncio.sleep(300)
    
    async def _performance_monitoring_task(self) -> None:
        """Background task for performance monitoring."""
        last_metric_count = 0
        
        while True:
            try:
                # Calculate metrics per second
                current_metric_count = self.collector_stats['total_metrics_collected']
                metrics_delta = current_metric_count - last_metric_count
                self.collector_stats['metrics_per_second'] = metrics_delta / 60.0  # 60-second window
                last_metric_count = current_metric_count
                
                # Calculate storage size (approximation)
                total_raw_metrics = sum(len(metrics) for metrics in self.raw_metrics.values())
                total_aggregated = sum(
                    sum(len(aggs) for aggs in metric_aggs.values())
                    for metric_aggs in self.aggregated_metrics.values()
                )
                
                # Rough estimation: 100 bytes per metric
                self.collector_stats['storage_size_mb'] = (total_raw_metrics + total_aggregated) * 100 / (1024 * 1024)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Performance monitoring failed: {e}")
                await asyncio.sleep(300)
    
    async def _get_widget_data(self, widget_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for dashboard widget."""
        widget_type = widget_config.get('type', 'line_chart')
        metric_id = widget_config.get('metric_id')
        
        if not metric_id:
            return {'error': 'No metric specified'}
        
        try:
            if widget_type == 'line_chart':
                values = await self.get_metric_values(metric_id)
                return {
                    'type': widget_type,
                    'metric_id': metric_id,
                    'data': [
                        {'timestamp': v.timestamp.isoformat(), 'value': v.value}
                        for v in values[-100:]  # Last 100 points
                    ]
                }
            
            elif widget_type == 'gauge':
                values = await self.get_metric_values(metric_id)
                current_value = values[-1].value if values else 0
                return {
                    'type': widget_type,
                    'metric_id': metric_id,
                    'current_value': current_value,
                    'min_value': widget_config.get('min_value', 0),
                    'max_value': widget_config.get('max_value', 100)
                }
            
            elif widget_type == 'counter':
                values = await self.get_metric_values(metric_id)
                total_value = sum(v.value for v in values)
                return {
                    'type': widget_type,
                    'metric_id': metric_id,
                    'total_value': total_value,
                    'current_value': values[-1].value if values else 0
                }
            
            else:
                return {'error': f'Unknown widget type: {widget_type}'}
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _analyze_trends(self, values: List[Union[int, float]]) -> Dict[str, Any]:
        """
Analyze trends in metric values."""
        if len(values) < 3:
            return {'trend': 'insufficient_data'}
        
        # Simple trend analysis
        recent_values = values[-10:]  # Last 10 values
        older_values = values[-20:-10] if len(values) >= 20 else values[:-10]
        
        if not older_values:
            return {'trend': 'insufficient_data'}
        
        recent_avg = statistics.mean(recent_values)
        older_avg = statistics.mean(older_values)
        
        if recent_avg > older_avg * 1.1:
            trend = 'increasing'
        elif recent_avg < older_avg * 0.9:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'recent_average': recent_avg,
            'older_average': older_avg,
            'change_percentage': ((recent_avg - older_avg) / older_avg * 100) if older_avg != 0 else 0
        }
    
    async def _detect_anomalies(self, values: List[Union[int, float]]) -> List[Dict[str, Any]]:
        """
Detect anomalies in metric values."""
        if len(values) < 10:
            return []
        
        anomalies = []
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # Simple outlier detection (values > 2 standard deviations)
        threshold = 2 * std_dev
        
        for i, value in enumerate(values):
            if abs(value - mean_val) > threshold:
                anomalies.append({
                    'index': i,
                    'value': value,
                    'deviation': abs(value - mean_val),
                    'type': 'outlier'
                })
        
        return anomalies
    
    async def _calculate_percentiles(self, values: List[Union[int, float]]) -> Dict[str, float]:
        """
Calculate percentiles for metric values."""
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        def percentile(p):
            k = (n - 1) * p / 100
            f = int(k)
            c = k - f
            if f == n - 1:
                return sorted_values[f]
            return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c
        
        return {
            'p50': percentile(50),
            'p75': percentile(75),
            'p90': percentile(90),
            'p95': percentile(95),
            'p99': percentile(99)
        }
    
    async def _validate_metric_definition(self, definition: MetricDefinition) -> bool:
        """
Validate metric definition."""
        return bool(definition.metric_id and definition.name and definition.unit)
    
    async def _validate_alert_rule(self, rule: AlertRule) -> bool:
        """
Validate alert rule."""
        return bool(rule.rule_id and rule.metric_id and rule.condition and rule.message)
    
    async def _validate_dashboard(self, dashboard: Dashboard) -> bool:
        """
Validate dashboard configuration."""
        return bool(dashboard.dashboard_id and dashboard.name)
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
Get all active alerts."""
        return [
            {
                'alert_id': alert.alert_id,
                'rule_id': alert.rule_id,
                'metric_id': alert.metric_id,
                'severity': alert.severity.value,
                'message': alert.message,
                'triggered_at': alert.triggered_at.isoformat(),
                'metric_value': alert.metric_value,
                'threshold_value': alert.threshold_value,
                'acknowledged': alert.acknowledged_at is not None
            }
            for alert in self.active_alerts.values()
        ]
    
    async def get_metric_summary(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """
Get metric summary information."""
        if metric_id not in self.metric_definitions:
            return None
        
        definition = self.metric_definitions[metric_id]
        recent_values = await self.get_metric_values(metric_id)
        
        summary = {
            'metric_id': metric_id,
            'name': definition.name,
            'type': definition.metric_type.value,
            'unit': definition.unit,
            'description': definition.description,
            'total_values': len(self.raw_metrics.get(metric_id, [])),
            'recent_values': len(recent_values),
            'tags': definition.tags
        }
        
        if recent_values:
            values = [v.value for v in recent_values]
            summary.update({
                'latest_value': values[-1],
                'min_value': min(values),
                'max_value': max(values),
                'average_value': statistics.mean(values)
            })
        
        return summary
    
    async def get_collector_stats(self) -> Dict[str, Any]:
        """
Get metrics collector statistics."""
        return {
            **self.collector_stats,
            'registered_metrics': len(self.metric_definitions),
            'active_alert_rules': len([rule for rule in self.alert_rules.values() if rule.enabled]),
            'total_alert_rules': len(self.alert_rules),
            'dashboards_count': len(self.dashboards),
            'retention_days': self.retention_days
        }
