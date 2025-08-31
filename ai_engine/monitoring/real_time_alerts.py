"""Advanced Real-Time Alerts System

Enterprise-grade intelligent alerting system for IA Influencer Agent platform.
Provides real-time monitoring, anomaly detection, and automated response capabilities.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""
import asyncio
import time
import json
from typing import Dict, Any, List, Optional, Callable, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
import statistics
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import redis.asyncio as aioredis
from jinja2 import Template

from ..core.metrics import MetricsCollector, MetricEntry, MetricType, MetricPriority
from ..core.exceptions import AlertingError
from .ai_performance import AIModelType, ProcessingStage
from .content_monitoring import ContentType, ContentStatus
from .business_metrics import RevenueSource

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertCategory(Enum):
    """Alert category classifications"""    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    SYSTEM = "system"
    USER_EXPERIENCE = "user_experience"
    REVENUE = "revenue"
    QUALITY = "quality"
    COMPLIANCE = "compliance"


class AlertChannel(Enum):
    """Alert delivery channels"""    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    DASHBOARD = "dashboard"
    MOBILE_PUSH = "mobile_push"
    PAGERDUTY = "pagerduty"


class AlertStatus(Enum):
    """Alert status states"""    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"


@dataclass
class AlertRule:
    """Alert rule configuration"""    rule_id: str
    name: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    condition: str  # Expression to evaluate
    threshold: float
    comparison_operator: str  # "gt", "lt", "eq", "gte", "lte"
    time_window: timedelta
    evaluation_frequency: timedelta
    channels: List[AlertChannel]
    recipients: List[str]
    auto_resolve: bool = True
    suppress_duration: Optional[timedelta] = None
    escalation_rules: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class Alert:
    """Alert instance"""    alert_id: str
    rule_id: str
    name: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    status: AlertStatus
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    current_value: float = 0.0
    threshold_value: float = 0.0
    affected_entities: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    actions_taken: List[str] = field(default_factory=list)
    escalation_level: int = 0
    suppressed_until: Optional[datetime] = None


@dataclass
class AlertMetrics:
    """Alert system metrics"""    total_alerts: int = 0
    active_alerts: int = 0
    resolved_alerts: int = 0
    false_positives: int = 0
    mean_time_to_acknowledge: float = 0.0
    mean_time_to_resolve: float = 0.0
    alert_rate: float = 0.0
    escalation_rate: float = 0.0
    suppression_rate: float = 0.0


class RealTimeAlerts:
    """    Advanced Real-Time Alerts System
    
    Provides intelligent monitoring, anomaly detection, and automated alerting
    for the IA Influencer Agent platform with multi-channel delivery and
    sophisticated alert management capabilities.
    """    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        redis_client: Optional[aioredis.Redis] = None,
        smtp_config: Optional[Dict[str, Any]] = None,
        slack_config: Optional[Dict[str, Any]] = None
    ):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.redis_client = redis_client
        self.smtp_config = smtp_config or {}
        self.slack_config = slack_config or {}
        
        # Alert management
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.suppressed_alerts: Set[str] = set()
        
        # Metrics and analytics
        self.alert_metrics = AlertMetrics()
        self.performance_baselines: Dict[str, float] = {}
        self.anomaly_models: Dict[str, Any] = {}
        
        # Alert channels
        self.channel_handlers: Dict[AlertChannel, Callable] = {
            AlertChannel.EMAIL: self._send_email_alert,
            AlertChannel.SLACK: self._send_slack_alert,
            AlertChannel.WEBHOOK: self._send_webhook_alert,
            AlertChannel.DASHBOARD: self._send_dashboard_alert
        }
        
        # Alert state
        self.is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._evaluation_task: Optional[asyncio.Task] = None
        
        # Load default alert rules
        self._load_default_alert_rules()
        
    async def start_alerting(self) -> None:
        """Start the real-time alerting system"""        if self.is_monitoring:
            logger.warning("Real-time alerting is already running")
            return
            
        self.is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        self._evaluation_task = asyncio.create_task(self._evaluation_loop())
        
        logger.info("Real-time alerting system started successfully")
        
    async def stop_alerting(self) -> None:
        """Stop the real-time alerting system"""        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        
        for task in [self._monitor_task, self._evaluation_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
        logger.info("Real-time alerting system stopped")
        
    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add a new alert rule"""        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name} ({rule.rule_id})")
        
    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove an alert rule"""        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
            return True
        return False
        
    def enable_rule(self, rule_id: str) -> bool:
        """Enable an alert rule"""        if rule_id in self.alert_rules:
            self.alert_rules[rule_id].enabled = True
            return True
        return False
        
    def disable_rule(self, rule_id: str) -> bool:
        """Disable an alert rule"""        if rule_id in self.alert_rules:
            self.alert_rules[rule_id].enabled = False
            return True
        return False
        
    async def trigger_alert(
        self,
        rule_id: str,
        current_value: float,
        context: Optional[Dict[str, Any]] = None,
        affected_entities: Optional[List[str]] = None
    ) -> Optional[Alert]:
        """Manually trigger an alert"""        if rule_id not in self.alert_rules:
            raise AlertingError(f"Alert rule {rule_id} not found")
            
        rule = self.alert_rules[rule_id]
        
        # Check if alert is already active for this rule
        existing_alert = self._find_active_alert(rule_id)
        if existing_alert and not self._should_retrigger(existing_alert, current_value):
            return existing_alert
            
        # Create new alert
        alert = Alert(
            alert_id=self._generate_alert_id(rule_id),
            rule_id=rule_id,
            name=rule.name,
            description=rule.description,
            category=rule.category,
            severity=rule.severity,
            status=AlertStatus.TRIGGERED,
            triggered_at=datetime.utcnow(),
            current_value=current_value,
            threshold_value=rule.threshold,
            affected_entities=affected_entities or [],
            context=context or {},
            tags={"rule_id": rule_id, "category": rule.category.value}
        )
        
        # Store alert
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        
        # Update metrics
        self.alert_metrics.total_alerts += 1
        self.alert_metrics.active_alerts += 1
        
        # Send notifications
        await self._send_alert_notifications(alert, rule)
        
        # Execute automated actions
        await self._execute_automated_actions(alert, rule)
        
        logger.warning(f"Alert triggered: {alert.name} ({alert.alert_id})")
        return alert
        
    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
        notes: Optional[str] = None
    ) -> bool:
        """Acknowledge an active alert"""        if alert_id not in self.active_alerts:
            return False
            
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by
        
        if notes:
            alert.actions_taken.append(f"Acknowledged by {acknowledged_by}: {notes}")
            
        # Update metrics
        ack_time = (alert.acknowledged_at - alert.triggered_at).total_seconds()
        self._update_acknowledgment_metrics(ack_time)
        
        logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
        return True
        
    async def resolve_alert(
        self,
        alert_id: str,
        resolved_by: Optional[str] = None,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Resolve an active alert"""        if alert_id not in self.active_alerts:
            return False
            
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        
        if resolution_notes:
            alert.actions_taken.append(f"Resolved by {resolved_by}: {resolution_notes}")
            
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        # Update metrics
        self.alert_metrics.active_alerts -= 1
        self.alert_metrics.resolved_alerts += 1
        
        resolve_time = (alert.resolved_at - alert.triggered_at).total_seconds()
        self._update_resolution_metrics(resolve_time)
        
        logger.info(f"Alert resolved: {alert_id}")
        return True
        
    async def suppress_alert(
        self,
        alert_id: str,
        duration: timedelta,
        suppressed_by: str,
        reason: Optional[str] = None
    ) -> bool:
        """Suppress an alert for a specified duration"""        if alert_id not in self.active_alerts:
            return False
            
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.SUPPRESSED
        alert.suppressed_until = datetime.utcnow() + duration
        
        self.suppressed_alerts.add(alert_id)
        
        if reason:
            alert.actions_taken.append(f"Suppressed by {suppressed_by} for {duration}: {reason}")
            
        logger.info(f"Alert suppressed: {alert_id} for {duration}")
        return True
        
    async def escalate_alert(
        self,
        alert_id: str,
        escalated_by: str,
        escalation_reason: Optional[str] = None
    ) -> bool:
        """Escalate an alert to higher severity level"""        if alert_id not in self.active_alerts:
            return False
            
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ESCALATED
        alert.escalation_level += 1
        
        # Increase severity if possible
        if alert.severity == AlertSeverity.WARNING:
            alert.severity = AlertSeverity.ERROR
        elif alert.severity == AlertSeverity.ERROR:
            alert.severity = AlertSeverity.CRITICAL
        elif alert.severity == AlertSeverity.CRITICAL:
            alert.severity = AlertSeverity.EMERGENCY
            
        alert.actions_taken.append(f"Escalated by {escalated_by}: {escalation_reason}")
        
        # Send escalation notifications
        rule = self.alert_rules[alert.rule_id]
        await self._send_escalation_notifications(alert, rule)
        
        logger.warning(f"Alert escalated: {alert_id} to level {alert.escalation_level}")
        return True
        
    async def get_alert_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive alert dashboard data"""        current_time = datetime.utcnow()
        
        # Active alerts summary
        active_by_severity = defaultdict(int)
        active_by_category = defaultdict(int)
        
        for alert in self.active_alerts.values():
            active_by_severity[alert.severity.value] += 1
            active_by_category[alert.category.value] += 1
            
        # Recent alerts (last 24 hours)
        recent_cutoff = current_time - timedelta(hours=24)
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.triggered_at >= recent_cutoff
        ]
        
        # Top alerting entities
        entity_alert_counts = defaultdict(int)
        for alert in recent_alerts:
            for entity in alert.affected_entities:
                entity_alert_counts[entity] += 1
                
        top_entities = sorted(
            entity_alert_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "timestamp": current_time.isoformat(),
            "alert_metrics": {
                "total_alerts": self.alert_metrics.total_alerts,
                "active_alerts": self.alert_metrics.active_alerts,
                "resolved_alerts": self.alert_metrics.resolved_alerts,
                "false_positives": self.alert_metrics.false_positives,
                "mean_time_to_acknowledge": self.alert_metrics.mean_time_to_acknowledge,
                "mean_time_to_resolve": self.alert_metrics.mean_time_to_resolve,
                "alert_rate": self.alert_metrics.alert_rate,
                "escalation_rate": self.alert_metrics.escalation_rate
            },
            "active_alerts_summary": {
                "by_severity": dict(active_by_severity),
                "by_category": dict(active_by_category),
                "total": len(self.active_alerts)
            },
            "recent_alerts": {
                "count": len(recent_alerts),
                "trend": "increasing" if len(recent_alerts) > 50 else "stable"
            },
            "top_alerting_entities": [
                {"entity": entity, "alert_count": count}
                for entity, count in top_entities
            ],
            "alert_rules": {
                "total": len(self.alert_rules),
                "enabled": len([r for r in self.alert_rules.values() if r.enabled]),
                "disabled": len([r for r in self.alert_rules.values() if not r.enabled])
            }
        }
        
    async def get_alert_analytics(
        self,
        time_window: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Get detailed alert analytics"""        cutoff_time = datetime.utcnow() - time_window
        
        # Filter alerts within time window
        window_alerts = [
            alert for alert in self.alert_history
            if alert.triggered_at >= cutoff_time
        ]
        
        if not window_alerts:
            return {"message": "No alerts in the specified time window"}
            
        # Alert patterns analysis
        hourly_distribution = defaultdict(int)
        daily_distribution = defaultdict(int)
        
        for alert in window_alerts:
            hour = alert.triggered_at.hour
            day = alert.triggered_at.strftime("%A")
            hourly_distribution[hour] += 1
            daily_distribution[day] += 1
            
        # Resolution analysis
        resolved_alerts = [a for a in window_alerts if a.resolved_at]
        resolution_times = [
            (a.resolved_at - a.triggered_at).total_seconds()
            for a in resolved_alerts
        ]
        
        # False positive analysis
        false_positives = [a for a in window_alerts if "false_positive" in a.actions_taken]
        
        return {
            "time_window": str(time_window),
            "total_alerts": len(window_alerts),
            "patterns": {
                "hourly_distribution": dict(hourly_distribution),
                "daily_distribution": dict(daily_distribution),
                "peak_hour": max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else 0,
                "peak_day": max(daily_distribution.items(), key=lambda x: x[1])[0] if daily_distribution else "Unknown"
            },
            "resolution_analysis": {
                "total_resolved": len(resolved_alerts),
                "resolution_rate": len(resolved_alerts) / len(window_alerts),
                "average_resolution_time": statistics.mean(resolution_times) if resolution_times else 0,
                "median_resolution_time": statistics.median(resolution_times) if resolution_times else 0
            },
            "quality_metrics": {
                "false_positive_rate": len(false_positives) / len(window_alerts),
                "escalation_rate": len([a for a in window_alerts if a.escalation_level > 0]) / len(window_alerts)
            }
        }
        
    def _load_default_alert_rules(self) -> None:
        """Load default alert rules for the platform"""        default_rules = [
            # AI Performance Alerts
            AlertRule(
                rule_id="ai_high_inference_time",
                name="High AI Model Inference Time",
                description="AI model inference time exceeds threshold",
                category=AlertCategory.PERFORMANCE,
                severity=AlertSeverity.WARNING,
                condition="ai_inference_time > threshold",
                threshold=5.0,
                comparison_operator="gt",
                time_window=timedelta(minutes=5),
                evaluation_frequency=timedelta(minutes=1),
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                recipients=["ops@platform.com"]
            ),
            
            # Content Processing Alerts
            AlertRule(
                rule_id="content_processing_failure_rate",
                name="High Content Processing Failure Rate",
                description="Content processing failure rate exceeds acceptable threshold",
                category=AlertCategory.QUALITY,
                severity=AlertSeverity.ERROR,
                condition="processing_failure_rate > threshold",
                threshold=0.1,  # 10%
                comparison_operator="gt",
                time_window=timedelta(minutes=10),
                evaluation_frequency=timedelta(minutes=2),
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.PAGERDUTY],
                recipients=["engineering@platform.com"]
            ),
            
            # Business Alerts
            AlertRule(
                rule_id="revenue_drop",
                name="Significant Revenue Drop",
                description="Revenue has dropped significantly compared to baseline",
                category=AlertCategory.BUSINESS,
                severity=AlertSeverity.CRITICAL,
                condition="revenue_drop_percentage > threshold",
                threshold=0.2,  # 20%
                comparison_operator="gt",
                time_window=timedelta(hours=1),
                evaluation_frequency=timedelta(minutes=5),
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                recipients=["business@platform.com", "ceo@platform.com"]
            ),
            
            # System Alerts
            AlertRule(
                rule_id="high_cpu_usage",
                name="High CPU Usage",
                description="System CPU usage exceeds threshold",
                category=AlertCategory.SYSTEM,
                severity=AlertSeverity.WARNING,
                condition="cpu_usage > threshold",
                threshold=0.8,  # 80%
                comparison_operator="gt",
                time_window=timedelta(minutes=5),
                evaluation_frequency=timedelta(minutes=1),
                channels=[AlertChannel.EMAIL],
                recipients=["devops@platform.com"]
            ),
            
            # Security Alerts
            AlertRule(
                rule_id="suspicious_login_attempts",
                name="Suspicious Login Attempts",
                description="Multiple failed login attempts detected",
                category=AlertCategory.SECURITY,
                severity=AlertSeverity.ERROR,
                condition="failed_login_attempts > threshold",
                threshold=10,
                comparison_operator="gt",
                time_window=timedelta(minutes=5),
                evaluation_frequency=timedelta(minutes=1),
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                recipients=["security@platform.com"]
            ),
            
            # User Experience Alerts
            AlertRule(
                rule_id="high_user_churn",
                name="High User Churn Rate",
                description="User churn rate is above acceptable threshold",
                category=AlertCategory.USER_EXPERIENCE,
                severity=AlertSeverity.WARNING,
                condition="churn_rate > threshold",
                threshold=0.05,  # 5%
                comparison_operator="gt",
                time_window=timedelta(hours=24),
                evaluation_frequency=timedelta(hours=1),
                channels=[AlertChannel.EMAIL],
                recipients=["product@platform.com"]
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
            
        logger.info(f"Loaded {len(default_rules)} default alert rules")
        
    def _generate_alert_id(self, rule_id: str) -> str:
        """Generate unique alert ID"""        timestamp = str(int(time.time() * 1000))
        return f"alert_{rule_id}_{timestamp}"
        
    def _find_active_alert(self, rule_id: str) -> Optional[Alert]:
        """Find active alert for a given rule"""        for alert in self.active_alerts.values():
            if alert.rule_id == rule_id and alert.status != AlertStatus.RESOLVED:
                return alert
        return None
        
    def _should_retrigger(self, existing_alert: Alert, current_value: float) -> bool:
        """Determine if an alert should be retriggered"""        # Retrigger if value has increased significantly
        value_increase = (current_value - existing_alert.current_value) / existing_alert.current_value
        return value_increase > 0.5  # 50% increase
        
    async def _send_alert_notifications(self, alert: Alert, rule: AlertRule) -> None:
        """Send alert notifications through configured channels"""        for channel in rule.channels:
            try:
                handler = self.channel_handlers.get(channel)
                if handler:
                    await handler(alert, rule)
                else:
                    logger.warning(f"No handler found for alert channel: {channel}")
            except Exception as e:
                logger.error(f"Failed to send alert via {channel}: {e}")
                
    async def _send_email_alert(self, alert: Alert, rule: AlertRule) -> None:
        """Send alert via email"""        if not self.smtp_config:
            logger.warning("SMTP configuration not provided, skipping email alert")
            return
            
        try:
            # Create email content
            subject = f"[{alert.severity.value.upper()}] {alert.name}"
            
            email_template = Template("""            <h2>Alert: {{ alert.name }}</h2>
            <p><strong>Severity:</strong> {{ alert.severity.value.title() }}</p>
            <p><strong>Category:</strong> {{ alert.category.value.title() }}</p>
            <p><strong>Description:</strong> {{ alert.description }}</p>
            <p><strong>Triggered:</strong> {{ alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC') }}</p>
            <p><strong>Current Value:</strong> {{ alert.current_value }}</p>
            <p><strong>Threshold:</strong> {{ alert.threshold_value }}</p>
            
            {% if alert.affected_entities %}
            <p><strong>Affected Entities:</strong></p>
            <ul>
            {% for entity in alert.affected_entities %}
                <li>{{ entity }}</li>
            {% endfor %}
            </ul>
            {% endif %}
            
            <p><strong>Alert ID:</strong> {{ alert.alert_id }}</p>
            """)
            
            body = email_template.render(alert=alert)
            
            # Send email
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config.get('from_email', 'alerts@platform.com')
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            for recipient in rule.recipients:
                msg['To'] = recipient
                
                with smtplib.SMTP(
                    self.smtp_config.get('host', 'localhost'),
                    self.smtp_config.get('port', 587)
                ) as server:
                    if self.smtp_config.get('use_tls', True):
                        server.starttls()
                    if self.smtp_config.get('username'):
                        server.login(
                            self.smtp_config['username'],
                            self.smtp_config['password']
                        )
                    server.send_message(msg)
                    
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            
    async def _send_slack_alert(self, alert: Alert, rule: AlertRule) -> None:
        """Send alert via Slack"""        if not self.slack_config.get('webhook_url'):
            logger.warning("Slack webhook URL not configured, skipping Slack alert")
            return
            
        try:
            # Create Slack message
            color_map = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ffeb3b",
                AlertSeverity.ERROR: "#ff9800",
                AlertSeverity.CRITICAL: "#f44336",
                AlertSeverity.EMERGENCY: "#9c27b0"
            }
            
            message = {
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "#36a64f"),
                        "title": f"{alert.severity.value.upper()}: {alert.name}",
                        "text": alert.description,
                        "fields": [
                            {
                                "title": "Alert ID",
                                "value": alert.alert_id,
                                "short": True
                            },
                            {
                                "title": "Current Value",
                                "value": str(alert.current_value),
                                "short": True
                            },
                            {
                                "title": "Threshold",
                                "value": str(alert.threshold_value),
                                "short": True
                            },
                            {
                                "title": "Triggered",
                                "value": alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                "short": True
                            }
                        ],
                        "footer": "IA Influencer Agent Monitoring",
                        "ts": int(alert.triggered_at.timestamp())
                    }
                ]
            }
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.slack_config['webhook_url'],
                    json=message
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to send Slack alert: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            
    async def _send_webhook_alert(self, alert: Alert, rule: AlertRule) -> None:
        """Send alert via webhook"""        webhook_url = rule.metadata.get('webhook_url')
        if not webhook_url:
            return
            
        try:
            payload = {
                "alert_id": alert.alert_id,
                "rule_id": alert.rule_id,
                "name": alert.name,
                "description": alert.description,
                "severity": alert.severity.value,
                "category": alert.category.value,
                "status": alert.status.value,
                "triggered_at": alert.triggered_at.isoformat(),
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "affected_entities": alert.affected_entities,
                "context": alert.context
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status not in [200, 201, 202]:
                        logger.error(f"Webhook alert failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            
    async def _send_dashboard_alert(self, alert: Alert, rule: AlertRule) -> None:
        """Send alert to dashboard (store in Redis for real-time display)"""        if not self.redis_client:
            return
            
        try:
            alert_data = {
                "alert_id": alert.alert_id,
                "name": alert.name,
                "severity": alert.severity.value,
                "category": alert.category.value,
                "triggered_at": alert.triggered_at.isoformat(),
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value
            }
            
            # Store in Redis with TTL
            await self.redis_client.setex(
                f"dashboard_alert:{alert.alert_id}",
                3600,  # 1 hour TTL
                json.dumps(alert_data)
            )
            
            # Add to dashboard alerts list
            await self.redis_client.lpush("dashboard_alerts", alert.alert_id)
            await self.redis_client.ltrim("dashboard_alerts", 0, 99)  # Keep latest 100
            
        except Exception as e:
            logger.error(f"Failed to send dashboard alert: {e}")
            
    async def _send_escalation_notifications(self, alert: Alert, rule: AlertRule) -> None:
        """Send escalation notifications"""        # Send to all channels with escalation priority
        for channel in rule.channels:
            try:
                handler = self.channel_handlers.get(channel)
                if handler:
                    # Modify alert for escalation
                    escalated_alert = Alert(
                        alert_id=alert.alert_id,
                        rule_id=alert.rule_id,
                        name=f"ESCALATED: {alert.name}",
                        description=f"ESCALATED (Level {alert.escalation_level}): {alert.description}",
                        category=alert.category,
                        severity=alert.severity,
                        status=alert.status,
                        triggered_at=alert.triggered_at,
                        current_value=alert.current_value,
                        threshold_value=alert.threshold_value,
                        affected_entities=alert.affected_entities,
                        context=alert.context,
                        escalation_level=alert.escalation_level
                    )
                    
                    await handler(escalated_alert, rule)
            except Exception as e:
                logger.error(f"Failed to send escalation notification via {channel}: {e}")
                
    async def _execute_automated_actions(self, alert: Alert, rule: AlertRule) -> None:
        """Execute automated actions for alerts"""        automated_actions = rule.metadata.get('automated_actions', [])
        
        for action in automated_actions:
            try:
                action_type = action.get('type')
                
                if action_type == 'scale_resources':
                    await self._scale_resources(alert, action.get('params', {}))
                elif action_type == 'restart_service':
                    await self._restart_service(alert, action.get('params', {}))
                elif action_type == 'quarantine_content':
                    await self._quarantine_content(alert, action.get('params', {}))
                elif action_type == 'block_user':
                    await self._block_user(alert, action.get('params', {}))
                    
                alert.actions_taken.append(f"Automated action executed: {action_type}")
                
            except Exception as e:
                logger.error(f"Failed to execute automated action {action.get('type')}: {e}")
                
    async def _scale_resources(self, alert: Alert, params: Dict[str, Any]) -> None:
        """Scale resources automatically"""        # This would integrate with container orchestration
        logger.info(f"Auto-scaling triggered for alert {alert.alert_id}")
        
    async def _restart_service(self, alert: Alert, params: Dict[str, Any]) -> None:
        """Restart service automatically"""        # This would integrate with service management
        logger.info(f"Service restart triggered for alert {alert.alert_id}")
        
    async def _quarantine_content(self, alert: Alert, params: Dict[str, Any]) -> None:
        """Quarantine content automatically"""        # This would integrate with content management
        logger.info(f"Content quarantine triggered for alert {alert.alert_id}")
        
    async def _block_user(self, alert: Alert, params: Dict[str, Any]) -> None:
        """Block user automatically"""        # This would integrate with user management
        logger.info(f"User block triggered for alert {alert.alert_id}")
        
    def _update_acknowledgment_metrics(self, ack_time: float) -> None:
        """Update acknowledgment time metrics"""        current_mean = self.alert_metrics.mean_time_to_acknowledge
        total_acks = self.alert_metrics.total_alerts  # Simplified
        
        self.alert_metrics.mean_time_to_acknowledge = (
            (current_mean * (total_acks - 1) + ack_time) / total_acks
        )
        
    def _update_resolution_metrics(self, resolve_time: float) -> None:
        """Update resolution time metrics"""        current_mean = self.alert_metrics.mean_time_to_resolve
        total_resolved = self.alert_metrics.resolved_alerts
        
        self.alert_metrics.mean_time_to_resolve = (
            (current_mean * (total_resolved - 1) + resolve_time) / total_resolved
        )
        
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""        while self.is_monitoring:
            try:
                # Check for suppressed alerts that should be unsuppressed
                await self._check_suppressed_alerts()
                
                # Update alert metrics
                await self._update_alert_metrics()
                
                # Clean up old data
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in alert monitoring loop: {e}")
                await asyncio.sleep(60)
                
    async def _evaluation_loop(self) -> None:
        """Alert rule evaluation loop"""        while self.is_monitoring:
            try:
                # Evaluate all active alert rules
                for rule in self.alert_rules.values():
                    if rule.enabled:
                        await self._evaluate_rule(rule)
                        
                await asyncio.sleep(10)  # Evaluate every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in alert evaluation loop: {e}")
                await asyncio.sleep(30)
                
    async def _evaluate_rule(self, rule: AlertRule) -> None:
        """Evaluate a specific alert rule"""        try:
            # This would integrate with the metrics system to get current values
            # For now, we'll simulate rule evaluation
            
            # Get current metric value based on rule condition
            current_value = await self._get_metric_value(rule.condition)
            
            # Check if threshold is breached
            threshold_breached = self._check_threshold(
                current_value,
                rule.threshold,
                rule.comparison_operator
            )
            
            if threshold_breached:
                await self.trigger_alert(
                    rule.rule_id,
                    current_value,
                    context={"evaluation_time": datetime.utcnow().isoformat()}
                )
            else:
                # Auto-resolve if configured
                if rule.auto_resolve:
                    await self._auto_resolve_alerts(rule.rule_id)
                    
        except Exception as e:
            logger.error(f"Failed to evaluate rule {rule.rule_id}: {e}")
            
    async def _get_metric_value(self, condition: str) -> float:
        """Get current metric value for evaluation"""        # This would integrate with the metrics collection system
        # For now, return a simulated value
        return 0.5
        
    def _check_threshold(
        self,
        current_value: float,
        threshold: float,
        operator: str
    ) -> bool:
        """Check if threshold is breached"""        if operator == "gt":
            return current_value > threshold
        elif operator == "lt":
            return current_value < threshold
        elif operator == "eq":
            return current_value == threshold
        elif operator == "gte":
            return current_value >= threshold
        elif operator == "lte":
            return current_value <= threshold
        return False
        
    async def _auto_resolve_alerts(self, rule_id: str) -> None:
        """Auto-resolve alerts for a rule when conditions return to normal"""        alerts_to_resolve = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.rule_id == rule_id
        ]
        
        for alert_id in alerts_to_resolve:
            await self.resolve_alert(alert_id, "System", "Auto-resolved: conditions returned to normal")
            
    async def _check_suppressed_alerts(self) -> None:
        """Check if suppressed alerts should be unsuppressed"""        current_time = datetime.utcnow()
        
        alerts_to_unsuppress = []
        for alert_id in self.suppressed_alerts:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                if alert.suppressed_until and current_time >= alert.suppressed_until:
                    alerts_to_unsuppress.append(alert_id)
                    
        for alert_id in alerts_to_unsuppress:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.TRIGGERED
            alert.suppressed_until = None
            self.suppressed_alerts.discard(alert_id)
            logger.info(f"Alert unsuppressed: {alert_id}")
            
    async def _update_alert_metrics(self) -> None:
        """Update alert system metrics"""        # Calculate alert rate (alerts per hour)
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.triggered_at >= recent_cutoff
        ]
        self.alert_metrics.alert_rate = len(recent_alerts)
        
        # Calculate escalation rate
        escalated_alerts = [
            alert for alert in recent_alerts
            if alert.escalation_level > 0
        ]
        self.alert_metrics.escalation_rate = (
            len(escalated_alerts) / max(len(recent_alerts), 1)
        )
        
    async def _cleanup_old_alerts(self) -> None:
        """Clean up old alert data"""        cutoff_time = datetime.utcnow() - timedelta(days=7)
        
        # Clean alert history
        while (self.alert_history and 
               self.alert_history[0].triggered_at < cutoff_time):
            self.alert_history.popleft()


# Global real-time alerts instance
real_time_alerts = RealTimeAlerts()
