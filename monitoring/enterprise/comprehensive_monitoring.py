"""Enterprise Monitoring and Alerting System
==========================================

Comprehensive monitoring system with real-time metrics collection,
intelligent alerting, performance analytics, and operational dashboards.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited

Features:
- Real-time metrics collection and aggregation
- Intelligent alerting with machine learning-based anomaly detection
- Performance analytics and trend analysis
- Multi-channel notifications (email, SMS, Slack, webhooks)
- Customizable dashboards and reporting
- Compliance monitoring and audit trails
- Infrastructure and application monitoring
- Business metrics and KPI tracking
"""import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union, Callable
from dataclasses import dataclass, field
import statistics
import hashlib
import secrets

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertState(Enum):
    """Alert states"""    FIRING = "firing"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


class NotificationChannel(Enum):
    """Notification channels"""    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PAGER_DUTY = "pager_duty"
    TEAMS = "teams"


@dataclass
class MetricDataPoint:
    """Individual metric data point"""    timestamp: datetime
    value: Union[int, float]
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """Metric definition and data"""    name: str
    metric_type: MetricType
    description: str
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    data_points: List[MetricDataPoint] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    retention_days: int = 30


@dataclass
class AlertRule:
    """Alert rule definition"""    rule_id: str
    name: str
    description: str
    metric_name: str
    condition: str  # e.g., "> 0.8", "< 100", "increase 50%"
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    evaluation_interval: int = 60  # seconds
    for_duration: int = 300  # seconds to fire
    tags: Dict[str, str] = field(default_factory=dict)
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Alert:
    """Active alert instance"""    alert_id: str
    rule_id: str
    metric_name: str
    severity: AlertSeverity
    state: AlertState
    message: str
    value: float
    threshold: float
    started_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    notification_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""    widget_id: str
    widget_type: str  # chart, gauge, table, status
    title: str
    metric_queries: List[str]
    time_range: str = "1h"
    refresh_interval: int = 30
    position: Dict[str, int] = field(default_factory=dict)  # x, y, width, height
    configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Dashboard definition"""    dashboard_id: str
    name: str
    description: str
    widgets: List[DashboardWidget]
    tags: List[str] = field(default_factory=list)
    created_by: str = "system"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_public: bool = False


class MetricsCollector:
    """Advanced metrics collection and storage"""    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.metric_buffer: Dict[str, List[MetricDataPoint]] = {}
        self.collectors: List[Callable] = []
        self.collection_interval = 15  # seconds
        self.max_buffer_size = 1000
        
    def register_metric(self, metric: Metric) -> None:
        """Register a new metric"""        self.metrics[metric.name] = metric
        self.metric_buffer[metric.name] = []
        logger.info(f"Registered metric: {metric.name} ({metric.metric_type.value})")
    
    async def collect_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Collect a metric data point"""        if metric_name not in self.metrics:
            # Auto-register basic metric
            self.register_metric(Metric(
                name=metric_name,
                metric_type=MetricType.GAUGE,
                description=f"Auto-registered metric: {metric_name}"
            ))
        
        data_point = MetricDataPoint(
            timestamp=timestamp or datetime.now(timezone.utc),
            value=value,
            tags=tags or {}
        )
        
        # Add to buffer
        self.metric_buffer[metric_name].append(data_point)
        
        # Limit buffer size
        if len(self.metric_buffer[metric_name]) > self.max_buffer_size:
            self.metric_buffer[metric_name] = self.metric_buffer[metric_name][-self.max_buffer_size:]
        
        # Update metric
        self.metrics[metric_name].data_points.append(data_point)
        self.metrics[metric_name].last_updated = data_point.timestamp
        
        # Limit data points for retention
        retention_cutoff = datetime.now(timezone.utc) - timedelta(
            days=self.metrics[metric_name].retention_days
        )
        self.metrics[metric_name].data_points = [
            dp for dp in self.metrics[metric_name].data_points
            if dp.timestamp > retention_cutoff
        ]
    
    def register_collector(self, collector_func: Callable) -> None:
        """Register a metric collector function"""        self.collectors.append(collector_func)
    
    async def start_collection(self) -> None:
        """Start automatic metric collection"""        while True:
            try:
                # Run all registered collectors
                for collector in self.collectors:
                    try:
                        await collector(self)
                    except Exception as e:
                        logger.error(f"Collector error: {e}")
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(self.collection_interval)
    
    def get_metric_value(
        self,
        metric_name: str,
        aggregation: str = "last",
        time_range: Optional[timedelta] = None
    ) -> Optional[float]:
        """Get aggregated metric value"""        if metric_name not in self.metrics:
            return None
        
        data_points = self.metrics[metric_name].data_points
        
        if time_range:
            cutoff = datetime.now(timezone.utc) - time_range
            data_points = [dp for dp in data_points if dp.timestamp > cutoff]
        
        if not data_points:
            return None
        
        values = [dp.value for dp in data_points]
        
        if aggregation == "last":
            return values[-1]
        elif aggregation == "avg":
            return statistics.mean(values)
        elif aggregation == "max":
            return max(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "count":
            return len(values)
        else:
            return values[-1]
    
    def get_metric_trend(
        self,
        metric_name: str,
        time_range: timedelta = timedelta(hours=1)
    ) -> Dict[str, float]:
        """Get metric trend analysis"""        if metric_name not in self.metrics:
            return {}
        
        cutoff = datetime.now(timezone.utc) - time_range
        data_points = [
            dp for dp in self.metrics[metric_name].data_points
            if dp.timestamp > cutoff
        ]
        
        if len(data_points) < 2:
            return {"trend": 0.0, "change_percent": 0.0}
        
        values = [dp.value for dp in data_points]
        first_value = values[0]
        last_value = values[-1]
        
        change = last_value - first_value
        change_percent = (change / first_value * 100) if first_value != 0 else 0
        
        return {
            "trend": change,
            "change_percent": change_percent,
            "first_value": first_value,
            "last_value": last_value,
            "data_points": len(data_points)
        }


class AnomalyDetector:
    """Machine learning-based anomaly detection"""    
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {}
        self.training_window = timedelta(days=7)
        self.detection_sensitivity = 0.95  # confidence threshold
    
    async def train_model(self, metric_name: str, data_points: List[MetricDataPoint]) -> None:
        """Train anomaly detection model for metric"""        if len(data_points) < 100:  # Need sufficient data
            return
        
        values = [dp.value for dp in data_points]
        
        # Calculate statistical baseline
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Calculate percentiles
        sorted_values = sorted(values)
        p25 = sorted_values[len(sorted_values) // 4]
        p75 = sorted_values[3 * len(sorted_values) // 4]
        iqr = p75 - p25
        
        # Simple outlier detection bounds
        lower_bound = p25 - 1.5 * iqr
        upper_bound = p75 + 1.5 * iqr
        
        self.models[metric_name] = {
            "mean": mean_value,
            "std_dev": std_dev,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "p25": p25,
            "p75": p75,
            "last_trained": datetime.now(timezone.utc),
            "training_points": len(data_points)
        }
        
        logger.info(f"Trained anomaly model for {metric_name}: bounds [{lower_bound:.2f}, {upper_bound:.2f}]")
    
    async def detect_anomaly(
        self,
        metric_name: str,
        value: float,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Detect if value is anomalous"""        if metric_name not in self.models:
            return {
                "is_anomaly": False,
                "reason": "no_model",
                "confidence": 0.0
            }
        
        model = self.models[metric_name]
        
        # Check if outside bounds
        is_outlier = value < model["lower_bound"] or value > model["upper_bound"]
        
        # Calculate confidence based on distance from bounds
        if value < model["lower_bound"]:
            distance = model["lower_bound"] - value
            max_distance = model["lower_bound"] - (model["mean"] - 3 * model["std_dev"])
            confidence = min(1.0, distance / max(max_distance, 1))
        elif value > model["upper_bound"]:
            distance = value - model["upper_bound"]
            max_distance = (model["mean"] + 3 * model["std_dev"]) - model["upper_bound"]
            confidence = min(1.0, distance / max(max_distance, 1))
        else:
            confidence = 0.0
        
        return {
            "is_anomaly": is_outlier and confidence >= self.detection_sensitivity,
            "confidence": confidence,
            "bounds": [model["lower_bound"], model["upper_bound"]],
            "reason": "statistical_outlier" if is_outlier else "within_bounds"
        }


class AlertManager:
    """Intelligent alert management system"""    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.anomaly_detector = AnomalyDetector()
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.notification_queue: List[Dict[str, Any]] = []
        self.evaluation_interval = 30  # seconds
        
    def register_alert_rule(self, rule: AlertRule) -> None:
        """Register an alert rule"""        self.rules[rule.rule_id] = rule
        logger.info(f"Registered alert rule: {rule.name}")
    
    async def start_monitoring(self) -> None:
        """Start alert monitoring loop"""        while True:
            try:
                await self._evaluate_all_rules()
                await self._process_notifications()
                await asyncio.sleep(self.evaluation_interval)
                
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(self.evaluation_interval)
    
    async def _evaluate_all_rules(self) -> None:
        """Evaluate all alert rules"""        for rule in self.rules.values():
            if rule.enabled:
                await self._evaluate_rule(rule)
    
    async def _evaluate_rule(self, rule: AlertRule) -> None:
        """Evaluate a single alert rule"""        try:
            # Get current metric value
            current_value = self.metrics_collector.get_metric_value(
                rule.metric_name,
                aggregation="last",
                time_range=timedelta(minutes=5)
            )
            
            if current_value is None:
                return
            
            # Check condition
            condition_met = self._evaluate_condition(rule.condition, current_value, rule.threshold)
            
            # Check for anomalies
            anomaly_result = await self.anomaly_detector.detect_anomaly(
                rule.metric_name, current_value, datetime.now(timezone.utc)
            )
            
            alert_id = f"{rule.rule_id}_{rule.metric_name}"
            
            if condition_met or anomaly_result["is_anomaly"]:
                await self._fire_alert(rule, current_value, anomaly_result)
            else:
                await self._resolve_alert(alert_id)
                
        except Exception as e:
            logger.error(f"Rule evaluation error for {rule.name}: {e}")
    
    def _evaluate_condition(self, condition: str, value: float, threshold: float) -> bool:
        """Evaluate alert condition"""        condition = condition.strip().lower()
        
        if condition.startswith(">"):
            return value > threshold
        elif condition.startswith("<"):
            return value < threshold
        elif condition.startswith(">="):
            return value >= threshold
        elif condition.startswith("<="):
            return value <= threshold
        elif condition.startswith("==") or condition.startswith("="):
            return abs(value - threshold) < 0.001
        elif condition.startswith("!="):
            return abs(value - threshold) >= 0.001
        elif "increase" in condition:
            # Check for percentage increase
            trend = self.metrics_collector.get_metric_trend(
                metric_name, time_range=timedelta(minutes=10)
            )
            return trend.get("change_percent", 0) > threshold
        elif "decrease" in condition:
            # Check for percentage decrease
            trend = self.metrics_collector.get_metric_trend(
                metric_name, time_range=timedelta(minutes=10)
            )
            return trend.get("change_percent", 0) < -threshold
        else:
            return False
    
    async def _fire_alert(self, rule: AlertRule, value: float, anomaly_result: Dict[str, Any]) -> None:
        """Fire an alert"""        alert_id = f"{rule.rule_id}_{rule.metric_name}"
        
        # Check if alert already exists
        if alert_id in self.active_alerts:
            # Update existing alert
            self.active_alerts[alert_id].value = value
            return
        
        # Create new alert
        message = f"{rule.name}: {rule.metric_name} = {value:.2f} (threshold: {rule.threshold})"
        if anomaly_result["is_anomaly"]:
            message += f" [ANOMALY: {anomaly_result['confidence']:.2f} confidence]"
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            metric_name=rule.metric_name,
            severity=rule.severity,
            state=AlertState.FIRING,
            message=message,
            value=value,
            threshold=rule.threshold,
            started_at=datetime.now(timezone.utc),
            tags=rule.tags.copy()
        )
        
        self.active_alerts[alert_id] = alert
        
        # Queue notifications
        for channel in rule.notification_channels:
            self.notification_queue.append({
                "alert": alert,
                "channel": channel,
                "action": "fire"
            })
        
        logger.warning(f"Alert fired: {message}")
    
    async def _resolve_alert(self, alert_id: str) -> None:
        """Resolve an alert"""        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.state = AlertState.RESOLVED
            alert.resolved_at = datetime.now(timezone.utc)
            
            # Queue resolution notifications
            rule = self.rules[alert.rule_id]
            for channel in rule.notification_channels:
                self.notification_queue.append({
                    "alert": alert,
                    "channel": channel,
                    "action": "resolve"
                })
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert resolved: {alert.message}")
    
    async def _process_notifications(self) -> None:
        """Process notification queue"""        while self.notification_queue:
            notification = self.notification_queue.pop(0)
            try:
                await self._send_notification(notification)
            except Exception as e:
                logger.error(f"Notification error: {e}")
    
    async def _send_notification(self, notification: Dict[str, Any]) -> None:
        """Send a notification"""        alert = notification["alert"]
        channel = notification["channel"]
        action = notification["action"]
        
        # Mock notification sending - in production, integrate with actual services
        if channel == NotificationChannel.EMAIL:
            await self._send_email_notification(alert, action)
        elif channel == NotificationChannel.SLACK:
            await self._send_slack_notification(alert, action)
        elif channel == NotificationChannel.WEBHOOK:
            await self._send_webhook_notification(alert, action)
        
        # Record notification
        alert.notification_history.append({
            "channel": channel.value,
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "sent"
        })
    
    async def _send_email_notification(self, alert: Alert, action: str) -> None:
        """Send email notification"""        logger.info(f"EMAIL: {action.upper()} - {alert.message}")
    
    async def _send_slack_notification(self, alert: Alert, action: str) -> None:
        """Send Slack notification"""        logger.info(f"SLACK: {action.upper()} - {alert.message}")
    
    async def _send_webhook_notification(self, alert: Alert, action: str) -> None:
        """Send webhook notification"""        logger.info(f"WEBHOOK: {action.upper()} - {alert.message}")
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.state = AlertState.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now(timezone.utc)
            alert.acknowledged_by = acknowledged_by
            logger.info(f"Alert acknowledged by {acknowledged_by}: {alert.message}")
            return True
        return False
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary"""        total_alerts = len(self.active_alerts)
        by_severity = {}
        
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total_active_alerts": total_alerts,
            "by_severity": by_severity,
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules.values() if r.enabled])
        }


class MonitoringSystem:
    """Main monitoring system orchestrator"""    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(self.metrics_collector)
        self._setup_default_metrics()
        self._setup_default_alerts()
    
    def _setup_default_metrics(self) -> None:
        """Setup default system metrics"""        default_metrics = [
            Metric("system_cpu_percent", MetricType.GAUGE, "CPU usage percentage", "%"),
            Metric("system_memory_percent", MetricType.GAUGE, "Memory usage percentage", "%"),
            Metric("system_disk_percent", MetricType.GAUGE, "Disk usage percentage", "%"),
            Metric("api_response_time", MetricType.HISTOGRAM, "API response time", "ms"),
            Metric("api_requests_total", MetricType.COUNTER, "Total API requests", "count"),
            Metric("api_errors_total", MetricType.COUNTER, "Total API errors", "count"),
            Metric("security_alerts_count", MetricType.GAUGE, "Active security alerts", "count"),
            Metric("content_submissions_count", MetricType.COUNTER, "Content submissions", "count"),
            Metric("piracy_detections_count", MetricType.COUNTER, "Piracy detections", "count")
        ]
        
        for metric in default_metrics:
            self.metrics_collector.register_metric(metric)
    
    def _setup_default_alerts(self) -> None:
        """Setup default alert rules"""        default_rules = [
            AlertRule(
                rule_id="high_cpu_usage",
                name="High CPU Usage",
                description="CPU usage is above 80%",
                metric_name="system_cpu_percent",
                condition="> 80",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK]
            ),
            AlertRule(
                rule_id="high_memory_usage",
                name="High Memory Usage", 
                description="Memory usage is above 85%",
                metric_name="system_memory_percent",
                condition="> 85",
                threshold=85.0,
                severity=AlertSeverity.ERROR,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK]
            ),
            AlertRule(
                rule_id="high_response_time",
                name="High API Response Time",
                description="API response time is above 2000ms",
                metric_name="api_response_time",
                condition="> 2000",
                threshold=2000.0,
                severity=AlertSeverity.WARNING,
                notification_channels=[NotificationChannel.SLACK]
            )
        ]
        
        for rule in default_rules:
            self.alert_manager.register_alert_rule(rule)
    
    async def start(self) -> None:
        """Start the monitoring system"""        logger.info("Starting enterprise monitoring system...")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self.metrics_collector.start_collection()),
            asyncio.create_task(self.alert_manager.start_monitoring())
        ]
        
        logger.info("Monitoring system started successfully")
        
        # Wait for tasks (in production, this would be managed by the application)
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""        alert_summary = self.alert_manager.get_alert_summary()
        
        # Calculate health score
        total_alerts = alert_summary["total_active_alerts"]
        critical_alerts = alert_summary["by_severity"].get("critical", 0)
        error_alerts = alert_summary["by_severity"].get("error", 0)
        
        if critical_alerts > 0:
            health_status = "critical"
            health_score = 20
        elif error_alerts > 0:
            health_status = "degraded"
            health_score = 50
        elif total_alerts > 0:
            health_status = "warning"
            health_score = 75
        else:
            health_status = "healthy"
            health_score = 100
        
        return {
            "status": health_status,
            "health_score": health_score,
            "alerts": alert_summary,
            "metrics_collected": len(self.metrics_collector.metrics),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "uptime_metrics": {
                "cpu_usage": self.metrics_collector.get_metric_value("system_cpu_percent"),
                "memory_usage": self.metrics_collector.get_metric_value("system_memory_percent"),
                "response_time": self.metrics_collector.get_metric_value("api_response_time")
            }
        }


# Export main components
__all__ = [
    "MonitoringSystem",
    "MetricsCollector",
    "AlertManager",
    "AnomalyDetector",
    "Metric",
    "AlertRule",
    "Alert",
    "MetricType",
    "AlertSeverity",
    "NotificationChannel"
]