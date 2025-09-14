"""
Real-Time MLOps Monitoring Dashboard
ML Engineer + DevOps implementation with comprehensive model monitoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import uuid
import time
from collections import deque, defaultdict
import warnings

# Optional dependencies for monitoring
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    warnings.warn("prometheus_client not available. Metrics collection will be limited.")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    warnings.warn("websockets not available. Real-time updates will be limited.")

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of monitoring metrics"""
    MODEL_PERFORMANCE = "model_performance"
    SYSTEM_PERFORMANCE = "system_performance"
    BUSINESS_METRICS = "business_metrics"
    DATA_QUALITY = "data_quality"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    USER_EXPERIENCE = "user_experience"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class MonitoringFrequency(Enum):
    """Monitoring frequencies"""
    REAL_TIME = "real_time"  # < 1 second
    HIGH = "high"  # 1-10 seconds
    MEDIUM = "medium"  # 10-60 seconds
    LOW = "low"  # 1-5 minutes
    BATCH = "batch"  # > 5 minutes


@dataclass
class MonitoringMetric:
    """Individual monitoring metric"""
    metric_id: str
    name: str
    type: MetricType
    value: Union[float, int, str, Dict]
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    model_id: Optional[str] = None
    model_version: Optional[str] = None
    environment: str = "production"
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    metric_name: str
    condition: str  # >, <, ==, !=, contains, etc.
    threshold: Union[float, int, str]
    severity: AlertSeverity
    frequency: MonitoringFrequency
    description: str
    enabled: bool = True
    cooldown_minutes: int = 5
    escalation_rules: List[Dict] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class Alert:
    """Generated alert"""
    alert_id: str
    rule_id: str
    metric: MonitoringMetric
    severity: AlertSeverity
    status: AlertStatus
    message: str
    first_triggered: datetime
    last_triggered: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    escalation_level: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    title: str
    widget_type: str  # line_chart, bar_chart, gauge, table, heatmap, etc.
    metrics: List[str]
    refresh_interval: int = 30  # seconds
    position: Dict[str, int] = field(default_factory=dict)  # x, y, width, height
    configuration: Dict[str, Any] = field(default_factory=dict)


class RealTimeMonitoringDashboard:
    """
    Enterprise real-time monitoring dashboard for MLOps
    ML Engineer + DevOps combined implementation
    """
    
    def __init__(
        self,
        dashboard_name: str,
        model_ids: List[str],
        prometheus_gateway: Optional[str] = None,
        websocket_port: int = 8765,
        retention_days: int = 30
    ):
        """Initialize real-time monitoring dashboard
        
        Args:
            dashboard_name: Name of the monitoring dashboard
            model_ids: List of model IDs to monitor
            prometheus_gateway: Prometheus pushgateway URL
            websocket_port: WebSocket server port for real-time updates
            retention_days: Data retention period in days
        """
        self.dashboard_name = dashboard_name
        self.model_ids = model_ids
        self.prometheus_gateway = prometheus_gateway
        self.websocket_port = websocket_port
        self.retention_days = retention_days
        
        # Monitoring state
        self.metrics_storage: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.widgets: Dict[str, DashboardWidget] = {}
        
        # Real-time connections
        self.websocket_connections: set = set()
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Performance tracking
        self.performance_baselines: Dict[str, Dict] = {}
        self.anomaly_detectors: Dict[str, Any] = {}
        
        # Prometheus metrics if available
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
        
        # Creator-specific monitoring
        self.creator_metrics: Dict[str, Dict] = {}
        
        logger.info(f"Initialized Real-Time Monitoring Dashboard: {dashboard_name}")

    def _setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics collectors"""
        try:
            self.prometheus_metrics = {
                'model_predictions_total': Counter(
                    'model_predictions_total',
                    'Total number of model predictions',
                    ['model_id', 'model_version', 'environment']
                ),
                'model_prediction_latency': Histogram(
                    'model_prediction_latency_seconds',
                    'Model prediction latency in seconds',
                    ['model_id', 'model_version', 'environment'],
                    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
                ),
                'model_accuracy': Gauge(
                    'model_accuracy',
                    'Current model accuracy',
                    ['model_id', 'model_version', 'environment']
                ),
                'model_drift_score': Gauge(
                    'model_drift_score',
                    'Data drift detection score',
                    ['model_id', 'feature_name', 'environment']
                ),
                'system_cpu_usage': Gauge(
                    'system_cpu_usage_percent',
                    'System CPU usage percentage',
                    ['instance', 'environment']
                ),
                'system_memory_usage': Gauge(
                    'system_memory_usage_percent',
                    'System memory usage percentage',
                    ['instance', 'environment']
                ),
                'model_errors_total': Counter(
                    'model_errors_total',
                    'Total number of model errors',
                    ['model_id', 'error_type', 'environment']
                ),
                'business_revenue': Gauge(
                    'business_revenue',
                    'Revenue impact from model',
                    ['model_id', 'creator_type', 'time_period']
                ),
                'creator_engagement': Gauge(
                    'creator_engagement_rate',
                    'Creator engagement rate',
                    ['creator_type', 'platform', 'model_id']
                )
            }
            
            logger.info("Prometheus metrics setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup Prometheus metrics: {e}")

    async def start_monitoring(self) -> None:
        """Start the monitoring system"""
        try:
            # Start WebSocket server for real-time updates
            if WEBSOCKETS_AVAILABLE:
                await self._start_websocket_server()
            
            # Start monitoring tasks for each model
            for model_id in self.model_ids:
                task = asyncio.create_task(self._monitor_model(model_id))
                self.monitoring_tasks[model_id] = task
            
            # Start system monitoring
            system_task = asyncio.create_task(self._monitor_system())
            self.monitoring_tasks['system'] = system_task
            
            # Start alert processing
            alert_task = asyncio.create_task(self._process_alerts())
            self.monitoring_tasks['alerts'] = alert_task
            
            # Start data cleanup
            cleanup_task = asyncio.create_task(self._cleanup_old_data())
            self.monitoring_tasks['cleanup'] = cleanup_task
            
            logger.info("Monitoring system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring system: {e}")
            raise

    async def stop_monitoring(self) -> None:
        """Stop the monitoring system"""
        try:
            # Cancel all monitoring tasks
            for task_name, task in self.monitoring_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        logger.info(f"Cancelled monitoring task: {task_name}")
            
            # Close WebSocket connections
            for connection in self.websocket_connections:
                await connection.close()
            
            logger.info("Monitoring system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring system: {e}")

    async def _start_websocket_server(self) -> None:
        """Start WebSocket server for real-time updates"""
        try:
            async def handle_client(websocket, path):
                self.websocket_connections.add(websocket)
                try:
                    await websocket.wait_closed()
                finally:
                    self.websocket_connections.discard(websocket)
            
            server = await websockets.serve(
                handle_client, 
                "localhost", 
                self.websocket_port
            )
            
            logger.info(f"WebSocket server started on port {self.websocket_port}")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")

    async def _monitor_model(self, model_id: str) -> None:
        """Monitor individual model performance"""
        try:
            while True:
                # Collect model metrics
                await self._collect_model_metrics(model_id)
                
                # Wait based on monitoring frequency
                await asyncio.sleep(1)  # Real-time monitoring
                
        except asyncio.CancelledError:
            logger.info(f"Model monitoring cancelled for {model_id}")
        except Exception as e:
            logger.error(f"Error monitoring model {model_id}: {e}")

    async def _collect_model_metrics(self, model_id: str) -> None:
        """Collect comprehensive model metrics"""
        try:
            timestamp = datetime.now()
            
            # Model performance metrics
            accuracy = await self._get_model_accuracy(model_id)
            if accuracy is not None:
                metric = MonitoringMetric(
                    metric_id=f"accuracy_{model_id}_{int(timestamp.timestamp())}",
                    name="model_accuracy",
                    type=MetricType.MODEL_PERFORMANCE,
                    value=accuracy,
                    unit="percentage",
                    model_id=model_id,
                    timestamp=timestamp
                )
                await self._store_metric(metric)
            
            # Prediction latency
            latency = await self._get_prediction_latency(model_id)
            if latency is not None:
                metric = MonitoringMetric(
                    metric_id=f"latency_{model_id}_{int(timestamp.timestamp())}",
                    name="prediction_latency",
                    type=MetricType.MODEL_PERFORMANCE,
                    value=latency,
                    unit="milliseconds",
                    model_id=model_id,
                    timestamp=timestamp
                )
                await self._store_metric(metric)
            
            # Throughput
            throughput = await self._get_model_throughput(model_id)
            if throughput is not None:
                metric = MonitoringMetric(
                    metric_id=f"throughput_{model_id}_{int(timestamp.timestamp())}",
                    name="prediction_throughput",
                    type=MetricType.MODEL_PERFORMANCE,
                    value=throughput,
                    unit="predictions_per_second",
                    model_id=model_id,
                    timestamp=timestamp
                )
                await self._store_metric(metric)
            
            # Error rate
            error_rate = await self._get_error_rate(model_id)
            if error_rate is not None:
                metric = MonitoringMetric(
                    metric_id=f"error_rate_{model_id}_{int(timestamp.timestamp())}",
                    name="error_rate",
                    type=MetricType.MODEL_PERFORMANCE,
                    value=error_rate,
                    unit="percentage",
                    model_id=model_id,
                    timestamp=timestamp
                )
                await self._store_metric(metric)
            
            # Data drift scores
            drift_scores = await self._get_drift_scores(model_id)
            for feature_name, drift_score in drift_scores.items():
                metric = MonitoringMetric(
                    metric_id=f"drift_{model_id}_{feature_name}_{int(timestamp.timestamp())}",
                    name="data_drift_score",
                    type=MetricType.DATA_QUALITY,
                    value=drift_score,
                    unit="score",
                    model_id=model_id,
                    timestamp=timestamp,
                    tags={"feature": feature_name}
                )
                await self._store_metric(metric)
            
            # Business metrics
            business_metrics = await self._get_business_metrics(model_id)
            for metric_name, value in business_metrics.items():
                metric = MonitoringMetric(
                    metric_id=f"business_{metric_name}_{model_id}_{int(timestamp.timestamp())}",
                    name=f"business_{metric_name}",
                    type=MetricType.BUSINESS_METRICS,
                    value=value,
                    unit="count" if "count" in metric_name else "percentage",
                    model_id=model_id,
                    timestamp=timestamp
                )
                await self._store_metric(metric)
            
            # Creator-specific metrics
            creator_metrics = await self._get_creator_specific_metrics(model_id)
            for metric_name, value in creator_metrics.items():
                metric = MonitoringMetric(
                    metric_id=f"creator_{metric_name}_{model_id}_{int(timestamp.timestamp())}",
                    name=f"creator_{metric_name}",
                    type=MetricType.BUSINESS_METRICS,
                    value=value,
                    unit="score",
                    model_id=model_id,
                    timestamp=timestamp
                )
                await self._store_metric(metric)
            
            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE and hasattr(self, 'prometheus_metrics'):
                self._update_prometheus_metrics(model_id, {
                    'accuracy': accuracy,
                    'latency': latency / 1000 if latency else None,  # Convert to seconds
                    'throughput': throughput,
                    'error_rate': error_rate
                })
            
        except Exception as e:
            logger.error(f"Error collecting metrics for model {model_id}: {e}")

    async def _monitor_system(self) -> None:
        """Monitor system-level metrics"""
        try:
            while True:
                timestamp = datetime.now()
                
                # CPU usage
                cpu_usage = await self._get_cpu_usage()
                if cpu_usage is not None:
                    metric = MonitoringMetric(
                        metric_id=f"cpu_usage_{int(timestamp.timestamp())}",
                        name="cpu_usage",
                        type=MetricType.INFRASTRUCTURE,
                        value=cpu_usage,
                        unit="percentage",
                        timestamp=timestamp
                    )
                    await self._store_metric(metric)
                
                # Memory usage
                memory_usage = await self._get_memory_usage()
                if memory_usage is not None:
                    metric = MonitoringMetric(
                        metric_id=f"memory_usage_{int(timestamp.timestamp())}",
                        name="memory_usage",
                        type=MetricType.INFRASTRUCTURE,
                        value=memory_usage,
                        unit="percentage",
                        timestamp=timestamp
                    )
                    await self._store_metric(metric)
                
                # Disk usage
                disk_usage = await self._get_disk_usage()
                if disk_usage is not None:
                    metric = MonitoringMetric(
                        metric_id=f"disk_usage_{int(timestamp.timestamp())}",
                        name="disk_usage",
                        type=MetricType.INFRASTRUCTURE,
                        value=disk_usage,
                        unit="percentage",
                        timestamp=timestamp
                    )
                    await self._store_metric(metric)
                
                # Network I/O
                network_io = await self._get_network_io()
                for direction, value in network_io.items():
                    metric = MonitoringMetric(
                        metric_id=f"network_{direction}_{int(timestamp.timestamp())}",
                        name=f"network_{direction}",
                        type=MetricType.INFRASTRUCTURE,
                        value=value,
                        unit="bytes_per_second",
                        timestamp=timestamp
                    )
                    await self._store_metric(metric)
                
                await asyncio.sleep(5)  # System monitoring every 5 seconds
                
        except asyncio.CancelledError:
            logger.info("System monitoring cancelled")
        except Exception as e:
            logger.error(f"Error in system monitoring: {e}")

    async def _store_metric(self, metric: MonitoringMetric) -> None:
        """Store metric and broadcast to connected clients"""
        try:
            # Store in memory
            self.metrics_storage[metric.name].append(metric)
            
            # Broadcast to WebSocket clients
            if self.websocket_connections:
                message = {
                    'type': 'metric_update',
                    'metric': {
                        'id': metric.metric_id,
                        'name': metric.name,
                        'type': metric.type.value,
                        'value': metric.value,
                        'unit': metric.unit,
                        'timestamp': metric.timestamp.isoformat(),
                        'model_id': metric.model_id,
                        'tags': metric.tags
                    }
                }
                
                await self._broadcast_to_clients(json.dumps(message))
            
            # Check alert rules
            await self._check_alert_rules(metric)
            
        except Exception as e:
            logger.error(f"Error storing metric {metric.metric_id}: {e}")

    async def _broadcast_to_clients(self, message: str) -> None:
        """Broadcast message to all connected WebSocket clients"""
        if not self.websocket_connections:
            return
        
        disconnected = set()
        
        for connection in self.websocket_connections:
            try:
                await connection.send(message)
            except Exception:
                disconnected.add(connection)
        
        # Remove disconnected clients
        self.websocket_connections -= disconnected

    async def _process_alerts(self) -> None:
        """Process and manage alerts"""
        try:
            while True:
                # Check for alert escalations
                await self._check_alert_escalations()
                
                # Auto-resolve alerts
                await self._auto_resolve_alerts()
                
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(10)  # Check alerts every 10 seconds
                
        except asyncio.CancelledError:
            logger.info("Alert processing cancelled")
        except Exception as e:
            logger.error(f"Error in alert processing: {e}")

    async def _check_alert_rules(self, metric: MonitoringMetric) -> None:
        """Check if metric triggers any alert rules"""
        try:
            for rule_id, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                
                if rule.metric_name != metric.name:
                    continue
                
                # Check if rule conditions are met
                triggered = self._evaluate_alert_condition(metric, rule)
                
                if triggered:
                    # Check cooldown period
                    if rule_id in self.active_alerts:
                        last_triggered = self.active_alerts[rule_id].last_triggered
                        if (datetime.now() - last_triggered).total_seconds() < rule.cooldown_minutes * 60:
                            continue
                    
                    # Create or update alert
                    await self._create_or_update_alert(metric, rule)
            
        except Exception as e:
            logger.error(f"Error checking alert rules for metric {metric.metric_id}: {e}")

    def _evaluate_alert_condition(self, metric: MonitoringMetric, rule: AlertRule) -> bool:
        """Evaluate if metric value meets alert condition"""
        try:
            value = metric.value
            threshold = rule.threshold
            condition = rule.condition.lower()
            
            if condition == '>':
                return float(value) > float(threshold)
            elif condition == '<':
                return float(value) < float(threshold)
            elif condition == '>=':
                return float(value) >= float(threshold)
            elif condition == '<=':
                return float(value) <= float(threshold)
            elif condition == '==':
                return value == threshold
            elif condition == '!=':
                return value != threshold
            elif condition == 'contains':
                return str(threshold).lower() in str(value).lower()
            else:
                logger.warning(f"Unknown alert condition: {condition}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating alert condition: {e}")
            return False

    async def _create_or_update_alert(self, metric: MonitoringMetric, rule: AlertRule) -> None:
        """Create new alert or update existing one"""
        try:
            alert_id = f"alert_{rule.rule_id}_{metric.model_id or 'system'}"
            
            if alert_id in self.active_alerts:
                # Update existing alert
                alert = self.active_alerts[alert_id]
                alert.last_triggered = datetime.now()
                alert.status = AlertStatus.ACTIVE
            else:
                # Create new alert
                alert = Alert(
                    alert_id=alert_id,
                    rule_id=rule.rule_id,
                    metric=metric,
                    severity=rule.severity,
                    status=AlertStatus.ACTIVE,
                    message=f"{rule.name}: {metric.name} {rule.condition} {rule.threshold} (current: {metric.value})",
                    first_triggered=datetime.now(),
                    last_triggered=datetime.now()
                )
                
                self.active_alerts[alert_id] = alert
                self.alert_history.append(alert)
            
            # Send notifications
            await self._send_alert_notifications(alert, rule)
            
            # Broadcast to clients
            if self.websocket_connections:
                message = {
                    'type': 'alert',
                    'alert': {
                        'id': alert.alert_id,
                        'rule_id': alert.rule_id,
                        'severity': alert.severity.value,
                        'status': alert.status.value,
                        'message': alert.message,
                        'first_triggered': alert.first_triggered.isoformat(),
                        'last_triggered': alert.last_triggered.isoformat(),
                        'metric': {
                            'name': metric.name,
                            'value': metric.value,
                            'model_id': metric.model_id
                        }
                    }
                }
                
                await self._broadcast_to_clients(json.dumps(message))
            
            logger.warning(f"Alert triggered: {alert.message}")
            
        except Exception as e:
            logger.error(f"Error creating/updating alert: {e}")

    async def _send_alert_notifications(self, alert: Alert, rule: AlertRule) -> None:
        """Send alert notifications to configured channels"""
        try:
            # Implementation would integrate with notification systems
            # Slack, email, PagerDuty, etc.
            
            notification_message = {
                'alert_id': alert.alert_id,
                'severity': alert.severity.value,
                'message': alert.message,
                'timestamp': alert.last_triggered.isoformat(),
                'dashboard_url': f"http://localhost:{self.websocket_port}/dashboard"
            }
            
            for channel in rule.notification_channels:
                logger.info(f"Sending alert notification to {channel}: {notification_message}")
                # Integration with specific notification channel would go here
            
        except Exception as e:
            logger.error(f"Error sending alert notifications: {e}")

    async def _check_alert_escalations(self) -> None:
        """Check and handle alert escalations"""
        try:
            for alert_id, alert in self.active_alerts.items():
                if alert.status != AlertStatus.ACTIVE:
                    continue
                
                rule = self.alert_rules.get(alert.rule_id)
                if not rule or not rule.escalation_rules:
                    continue
                
                # Check if escalation is needed
                time_since_first = (datetime.now() - alert.first_triggered).total_seconds() / 60
                
                for escalation in rule.escalation_rules:
                    if (time_since_first >= escalation.get('after_minutes', 0) and 
                        alert.escalation_level < escalation.get('level', 0)):
                        
                        alert.escalation_level = escalation['level']
                        
                        # Send escalation notification
                        escalation_message = f"ESCALATED: {alert.message} (Level {alert.escalation_level})"
                        logger.critical(escalation_message)
            
        except Exception as e:
            logger.error(f"Error checking alert escalations: {e}")

    async def _auto_resolve_alerts(self) -> None:
        """Auto-resolve alerts when conditions are no longer met"""
        try:
            resolved_alerts = []
            
            for alert_id, alert in self.active_alerts.items():
                if alert.status != AlertStatus.ACTIVE:
                    continue
                
                rule = self.alert_rules.get(alert.rule_id)
                if not rule:
                    continue
                
                # Get latest metric value
                latest_metric = await self._get_latest_metric(rule.metric_name, alert.metric.model_id)
                
                if latest_metric and not self._evaluate_alert_condition(latest_metric, rule):
                    # Alert condition no longer met
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_at = datetime.now()
                    resolved_alerts.append(alert_id)
                    
                    logger.info(f"Auto-resolved alert: {alert.message}")
            
            # Remove resolved alerts from active alerts
            for alert_id in resolved_alerts:
                del self.active_alerts[alert_id]
            
        except Exception as e:
            logger.error(f"Error auto-resolving alerts: {e}")

    async def _cleanup_old_data(self) -> None:
        """Clean up old monitoring data"""
        try:
            while True:
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                
                # Clean up metrics
                for metric_name, metrics in self.metrics_storage.items():
                    while metrics and metrics[0].timestamp < cutoff_date:
                        metrics.popleft()
                
                # Clean up alert history
                self.alert_history = [
                    alert for alert in self.alert_history
                    if alert.first_triggered > cutoff_date
                ]
                
                logger.info(f"Cleaned up data older than {self.retention_days} days")
                
                # Sleep for 24 hours before next cleanup
                await asyncio.sleep(24 * 3600)
                
        except asyncio.CancelledError:
            logger.info("Data cleanup cancelled")
        except Exception as e:
            logger.error(f"Error in data cleanup: {e}")

    async def _cleanup_old_alerts(self) -> None:
        """Clean up old resolved alerts"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)  # Keep resolved alerts for 1 hour
            
            expired_alerts = [
                alert_id for alert_id, alert in self.active_alerts.items()
                if (alert.status == AlertStatus.RESOLVED and 
                    alert.resolved_at and 
                    alert.resolved_at < cutoff_time)
            ]
            
            for alert_id in expired_alerts:
                del self.active_alerts[alert_id]
            
        except Exception as e:
            logger.error(f"Error cleaning up old alerts: {e}")

    # Metric collection methods (would integrate with actual data sources)
    async def _get_model_accuracy(self, model_id: str) -> Optional[float]:
        """Get current model accuracy"""
        # Implementation would query actual model performance
        return np.random.uniform(0.85, 0.95)  # Simulated

    async def _get_prediction_latency(self, model_id: str) -> Optional[float]:
        """Get average prediction latency in milliseconds"""
        # Implementation would measure actual latency
        return np.random.uniform(10, 50)  # Simulated

    async def _get_model_throughput(self, model_id: str) -> Optional[float]:
        """Get model throughput in predictions per second"""
        # Implementation would measure actual throughput
        return np.random.uniform(50, 200)  # Simulated

    async def _get_error_rate(self, model_id: str) -> Optional[float]:
        """Get model error rate percentage"""
        # Implementation would calculate actual error rate
        return np.random.uniform(0, 2)  # Simulated

    async def _get_drift_scores(self, model_id: str) -> Dict[str, float]:
        """Get data drift scores for model features"""
        # Implementation would use actual drift detection
        features = ['feature_1', 'feature_2', 'feature_3', 'feature_4']
        return {feature: np.random.uniform(0, 0.3) for feature in features}

    async def _get_business_metrics(self, model_id: str) -> Dict[str, float]:
        """Get business impact metrics"""
        # Implementation would query business metrics
        return {
            'revenue_impact': np.random.uniform(1000, 5000),
            'user_satisfaction': np.random.uniform(4.0, 5.0),
            'conversion_rate': np.random.uniform(2, 8),
            'engagement_rate': np.random.uniform(10, 30)
        }

    async def _get_creator_specific_metrics(self, model_id: str) -> Dict[str, float]:
        """Get creator-specific metrics for Ainflue platform"""
        # Implementation would query creator-specific data
        return {
            'content_optimization_score': np.random.uniform(70, 95),
            'collaboration_match_accuracy': np.random.uniform(80, 98),
            'revenue_optimization_lift': np.random.uniform(15, 45),
            'audience_growth_rate': np.random.uniform(5, 25),
            'cross_platform_performance': np.random.uniform(60, 90)
        }

    async def _get_cpu_usage(self) -> Optional[float]:
        """Get system CPU usage percentage"""
        # Implementation would query actual system metrics
        return np.random.uniform(20, 80)  # Simulated

    async def _get_memory_usage(self) -> Optional[float]:
        """Get system memory usage percentage"""
        # Implementation would query actual system metrics
        return np.random.uniform(40, 85)  # Simulated

    async def _get_disk_usage(self) -> Optional[float]:
        """Get system disk usage percentage"""
        # Implementation would query actual system metrics
        return np.random.uniform(30, 70)  # Simulated

    async def _get_network_io(self) -> Dict[str, float]:
        """Get network I/O metrics"""
        # Implementation would query actual network metrics
        return {
            'bytes_in': np.random.uniform(1000000, 10000000),   # 1-10 MB/s
            'bytes_out': np.random.uniform(500000, 5000000)     # 0.5-5 MB/s
        }

    async def _get_latest_metric(self, metric_name: str, model_id: Optional[str]) -> Optional[MonitoringMetric]:
        """Get latest metric value"""
        if metric_name not in self.metrics_storage:
            return None
        
        metrics = self.metrics_storage[metric_name]
        if not metrics:
            return None
        
        # Find latest metric for this model
        for metric in reversed(metrics):
            if model_id is None or metric.model_id == model_id:
                return metric
        
        return None

    def _update_prometheus_metrics(self, model_id: str, metrics: Dict[str, Any]) -> None:
        """Update Prometheus metrics"""
        try:
            if not hasattr(self, 'prometheus_metrics'):
                return
            
            # Update model-specific metrics
            if metrics.get('accuracy') is not None:
                self.prometheus_metrics['model_accuracy'].labels(
                    model_id=model_id, 
                    model_version='latest', 
                    environment='production'
                ).set(metrics['accuracy'])
            
            if metrics.get('latency') is not None:
                self.prometheus_metrics['model_prediction_latency'].labels(
                    model_id=model_id, 
                    model_version='latest', 
                    environment='production'
                ).observe(metrics['latency'])
            
            # Push to gateway if configured
            if self.prometheus_gateway:
                # Implementation would push to Prometheus gateway
                pass
                
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")

    # API methods for dashboard management
    def add_alert_rule(self, alert_rule: AlertRule) -> str:
        """Add new alert rule"""
        self.alert_rules[alert_rule.rule_id] = alert_rule
        logger.info(f"Added alert rule: {alert_rule.name}")
        return alert_rule.rule_id

    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
            return True
        return False

    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = user
            alert.acknowledged_at = datetime.now()
            logger.info(f"Alert {alert_id} acknowledged by {user}")
            return True
        return False

    def resolve_alert(self, alert_id: str, user: str) -> bool:
        """Manually resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            del self.active_alerts[alert_id]
            logger.info(f"Alert {alert_id} resolved by {user}")
            return True
        return False

    def add_dashboard_widget(self, widget: DashboardWidget) -> str:
        """Add dashboard widget"""
        self.widgets[widget.widget_id] = widget
        logger.info(f"Added dashboard widget: {widget.title}")
        return widget.widget_id

    def remove_dashboard_widget(self, widget_id: str) -> bool:
        """Remove dashboard widget"""
        if widget_id in self.widgets:
            del self.widgets[widget_id]
            logger.info(f"Removed dashboard widget: {widget_id}")
            return True
        return False

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        try:
            # Aggregate recent metrics
            recent_metrics = {}
            for metric_name, metrics in self.metrics_storage.items():
                if metrics:
                    recent_metrics[metric_name] = [
                        {
                            'timestamp': metric.timestamp.isoformat(),
                            'value': metric.value,
                            'model_id': metric.model_id,
                            'tags': metric.tags
                        }
                        for metric in list(metrics)[-100:]  # Last 100 data points
                    ]
            
            # Active alerts summary
            alerts_summary = {
                'total_active': len(self.active_alerts),
                'by_severity': {
                    severity.value: sum(
                        1 for alert in self.active_alerts.values() 
                        if alert.severity == severity
                    )
                    for severity in AlertSeverity
                },
                'recent_alerts': [
                    {
                        'id': alert.alert_id,
                        'message': alert.message,
                        'severity': alert.severity.value,
                        'status': alert.status.value,
                        'first_triggered': alert.first_triggered.isoformat(),
                        'model_id': alert.metric.model_id
                    }
                    for alert in sorted(
                        self.active_alerts.values(),
                        key=lambda a: a.first_triggered,
                        reverse=True
                    )[:20]  # Last 20 alerts
                ]
            }
            
            # System health summary
            system_health = {
                'overall_status': 'healthy',  # Would be calculated based on metrics
                'models_monitored': len(self.model_ids),
                'monitoring_uptime': '99.9%',  # Would be calculated
                'data_points_collected': sum(len(metrics) for metrics in self.metrics_storage.values())
            }
            
            return {
                'dashboard_name': self.dashboard_name,
                'timestamp': datetime.now().isoformat(),
                'metrics': recent_metrics,
                'alerts': alerts_summary,
                'system_health': system_health,
                'widgets': {
                    widget_id: {
                        'title': widget.title,
                        'type': widget.widget_type,
                        'metrics': widget.metrics,
                        'position': widget.position,
                        'configuration': widget.configuration
                    }
                    for widget_id, widget in self.widgets.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

    def get_metric_history(
        self, 
        metric_name: str, 
        model_id: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict]:
        """Get metric history for specified time period"""
        try:
            if metric_name not in self.metrics_storage:
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            filtered_metrics = [
                {
                    'timestamp': metric.timestamp.isoformat(),
                    'value': metric.value,
                    'model_id': metric.model_id,
                    'tags': metric.tags,
                    'unit': metric.unit
                }
                for metric in self.metrics_storage[metric_name]
                if (metric.timestamp > cutoff_time and 
                    (model_id is None or metric.model_id == model_id))
            ]
            
            return sorted(filtered_metrics, key=lambda m: m['timestamp'])
            
        except Exception as e:
            logger.error(f"Error getting metric history: {e}")
            return []

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get comprehensive alert summary"""
        try:
            return {
                'active_alerts': len(self.active_alerts),
                'total_rules': len(self.alert_rules),
                'alert_history_count': len(self.alert_history),
                'alerts_by_severity': {
                    severity.value: sum(
                        1 for alert in self.active_alerts.values()
                        if alert.severity == severity
                    )
                    for severity in AlertSeverity
                },
                'alerts_by_model': {
                    model_id: sum(
                        1 for alert in self.active_alerts.values()
                        if alert.metric.model_id == model_id
                    )
                    for model_id in self.model_ids
                },
                'recent_activity': [
                    {
                        'alert_id': alert.alert_id,
                        'message': alert.message,
                        'severity': alert.severity.value,
                        'status': alert.status.value,
                        'timestamp': alert.last_triggered.isoformat()
                    }
                    for alert in sorted(
                        self.alert_history[-50:],  # Last 50 alerts
                        key=lambda a: a.last_triggered,
                        reverse=True
                    )
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting alert summary: {e}")
            return {}


# Creator-specific monitoring extensions
class CreatorMonitoringDashboard(RealTimeMonitoringDashboard):
    """
    Specialized monitoring dashboard for creator-specific metrics
    Enhanced for Ainflue platform with musician, blogger, photographer, influencer, comedian metrics
    """
    
    def __init__(self, creator_type: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.creator_type = creator_type.lower()
        
        # Creator-specific monitoring configurations
        self._setup_creator_specific_monitoring()

    def _setup_creator_specific_monitoring(self) -> None:
        """Setup creator-specific monitoring rules and widgets"""
        
        creator_configs = {
            'musician': {
                'metrics': [
                    'audio_processing_quality', 'streaming_performance', 'collaboration_matches',
                    'revenue_from_streaming', 'audience_engagement', 'music_discovery_rate'
                ],
                'alert_rules': [
                    AlertRule(
                        rule_id='musician_audio_quality',
                        name='Audio Processing Quality Drop',
                        metric_name='audio_processing_quality',
                        condition='<',
                        threshold=0.9,
                        severity=AlertSeverity.WARNING,
                        frequency=MonitoringFrequency.HIGH,
                        description='Audio processing quality below acceptable threshold'
                    ),
                    AlertRule(
                        rule_id='musician_streaming_performance',
                        name='Streaming Performance Issue',
                        metric_name='streaming_performance',
                        condition='<',
                        threshold=0.85,
                        severity=AlertSeverity.CRITICAL,
                        frequency=MonitoringFrequency.REAL_TIME,
                        description='Streaming performance degradation detected'
                    )
                ]
            },
            'blogger': {
                'metrics': [
                    'content_seo_score', 'reading_engagement', 'content_virality',
                    'ad_revenue', 'subscriber_growth', 'content_quality_score'
                ],
                'alert_rules': [
                    AlertRule(
                        rule_id='blogger_seo_drop',
                        name='SEO Score Drop',
                        metric_name='content_seo_score',
                        condition='<',
                        threshold=0.8,
                        severity=AlertSeverity.WARNING,
                        frequency=MonitoringFrequency.MEDIUM,
                        description='Content SEO score below recommended threshold'
                    )
                ]
            },
            'photographer': {
                'metrics': [
                    'image_quality_score', 'portfolio_performance', 'client_satisfaction',
                    'booking_rate', 'portfolio_views', 'style_consistency'
                ],
                'alert_rules': [
                    AlertRule(
                        rule_id='photographer_quality_drop',
                        name='Image Quality Drop',
                        metric_name='image_quality_score',
                        condition='<',
                        threshold=0.9,
                        severity=AlertSeverity.WARNING,
                        frequency=MonitoringFrequency.HIGH,
                        description='Image quality analysis score below threshold'
                    )
                ]
            },
            'influencer': {
                'metrics': [
                    'cross_platform_engagement', 'brand_collaboration_success', 'audience_growth',
                    'content_reach', 'influencer_score', 'monetization_rate'
                ],
                'alert_rules': [
                    AlertRule(
                        rule_id='influencer_engagement_drop',
                        name='Engagement Rate Drop',
                        metric_name='cross_platform_engagement',
                        condition='<',
                        threshold=0.05,  # 5% engagement rate
                        severity=AlertSeverity.WARNING,
                        frequency=MonitoringFrequency.MEDIUM,
                        description='Cross-platform engagement rate below benchmark'
                    )
                ]
            },
            'comedian': {
                'metrics': [
                    'audience_reaction_score', 'timing_accuracy', 'content_humor_rating',
                    'show_bookings', 'audience_retention', 'performance_consistency'
                ],
                'alert_rules': [
                    AlertRule(
                        rule_id='comedian_reaction_drop',
                        name='Audience Reaction Drop',
                        metric_name='audience_reaction_score',
                        condition='<',
                        threshold=0.7,
                        severity=AlertSeverity.WARNING,
                        frequency=MonitoringFrequency.HIGH,
                        description='Audience reaction score below expected level'
                    )
                ]
            }
        }
        
        config = creator_configs.get(self.creator_type, {})
        
        # Add creator-specific alert rules
        for rule in config.get('alert_rules', []):
            self.add_alert_rule(rule)
        
        # Add creator-specific dashboard widgets
        metrics = config.get('metrics', [])
        if metrics:
            widget = DashboardWidget(
                widget_id=f"{self.creator_type}_performance_overview",
                title=f"{self.creator_type.title()} Performance Overview",
                widget_type="multi_metric_chart",
                metrics=metrics,
                refresh_interval=15,
                position={"x": 0, "y": 0, "width": 12, "height": 6},
                configuration={
                    "chart_type": "line",
                    "time_range": "1h",
                    "aggregation": "avg"
                }
            )
            self.add_dashboard_widget(widget)
        
        logger.info(f"Setup creator-specific monitoring for {self.creator_type}")

    async def _get_creator_specific_metrics(self, model_id: str) -> Dict[str, float]:
        """Enhanced creator-specific metrics collection"""
        base_metrics = await super()._get_creator_specific_metrics(model_id)
        
        # Add creator-type specific metrics
        creator_metrics = {}
        
        if self.creator_type == 'musician':
            creator_metrics.update({
                'audio_processing_quality': np.random.uniform(0.85, 0.98),
                'streaming_performance': np.random.uniform(0.80, 0.95),
                'collaboration_matches': np.random.uniform(5, 25),
                'revenue_from_streaming': np.random.uniform(100, 2000),
                'music_discovery_rate': np.random.uniform(10, 40)
            })
        
        elif self.creator_type == 'blogger':
            creator_metrics.update({
                'content_seo_score': np.random.uniform(0.75, 0.95),
                'reading_engagement': np.random.uniform(60, 90),
                'content_virality': np.random.uniform(1, 15),
                'ad_revenue': np.random.uniform(50, 500),
                'content_quality_score': np.random.uniform(0.80, 0.98)
            })
        
        elif self.creator_type == 'photographer':
            creator_metrics.update({
                'image_quality_score': np.random.uniform(0.85, 0.98),
                'portfolio_performance': np.random.uniform(70, 95),
                'client_satisfaction': np.random.uniform(4.0, 5.0),
                'booking_rate': np.random.uniform(20, 80),
                'style_consistency': np.random.uniform(0.75, 0.95)
            })
        
        elif self.creator_type == 'influencer':
            creator_metrics.update({
                'cross_platform_engagement': np.random.uniform(0.03, 0.12),
                'brand_collaboration_success': np.random.uniform(65, 95),
                'content_reach': np.random.uniform(10000, 100000),
                'influencer_score': np.random.uniform(70, 95),
                'monetization_rate': np.random.uniform(15, 45)
            })
        
        elif self.creator_type == 'comedian':
            creator_metrics.update({
                'audience_reaction_score': np.random.uniform(0.60, 0.90),
                'timing_accuracy': np.random.uniform(0.75, 0.95),
                'content_humor_rating': np.random.uniform(3.5, 5.0),
                'show_bookings': np.random.uniform(2, 15),
                'performance_consistency': np.random.uniform(0.70, 0.90)
            })
        
        # Merge with base metrics
        base_metrics.update(creator_metrics)
        return base_metrics