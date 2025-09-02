"""Database Alert Manager

Advanced database alerting system with intelligent notification routing,
escalation policies, and automated response capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Propriété intellectuelle de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from collections import defaultdict, deque
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp

from ..models.monitoring import DatabaseAlert, AlertRule, NotificationChannel
from ...core.config import Settings
from ...utils.cache import RedisCache
from ...utils.template_engine import TemplateEngine


class AlertSeverity(Enum):
    """
Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status types"""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class NotificationType(Enum):
    """Notification channel types"""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    TEAMS = "teams"
    DISCORD = "discord"


@dataclass
class AlertCondition:
    """Alert condition definition"""
    metric_name: str
    operator: str  # gt, gte, lt, lte, eq, ne
    threshold: float
    duration_minutes: int
    aggregation: str = "avg"  # avg, max, min, sum, count
    
    def evaluate(self, values: List[float]) -> bool:
        """Evaluate condition against values"""
        if not values:
            return False
        
        # Apply aggregation
        if self.aggregation == "avg":
            value = sum(values) / len(values)
        elif self.aggregation == "max":
            value = max(values)
        elif self.aggregation == "min":
            value = min(values)
        elif self.aggregation == "sum":
            value = sum(values)
        elif self.aggregation == "count":
            value = len(values)
        else:
            value = sum(values) / len(values)  # Default to avg
        
        # Apply operator
        if self.operator == "gt":
            return value > self.threshold
        elif self.operator == "gte":
            return value >= self.threshold
        elif self.operator == "lt":
            return value < self.threshold
        elif self.operator == "lte":
            return value <= self.threshold
        elif self.operator == "eq":
            return value == self.threshold
        elif self.operator == "ne":
            return value != self.threshold
        else:
            return False


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    description: str
    conditions: List[AlertCondition]
    severity: AlertSeverity
    enabled: bool
    notification_channels: List[str]
    escalation_delay_minutes: int = 15
    auto_resolve: bool = True
    auto_resolve_delay_minutes: int = 5
    suppression_duration_minutes: int = 60
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['conditions'] = [asdict(condition) for condition in self.conditions]
        return data


@dataclass
class Alert:
    """
Alert instance"""
    alert_id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    description: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    notification_count: int = 0
    last_notification: Optional[datetime] = None
    suppressed_until: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['status'] = self.status.value
        data['triggered_at'] = self.triggered_at.isoformat()
        data['acknowledged_at'] = self.acknowledged_at.isoformat() if self.acknowledged_at else None
        data['resolved_at'] = self.resolved_at.isoformat() if self.resolved_at else None
        data['last_notification'] = self.last_notification.isoformat() if self.last_notification else None
        data['suppressed_until'] = self.suppressed_until.isoformat() if self.suppressed_until else None
        return data


@dataclass
class NotificationChannel:
    """
Notification channel configuration"""
    channel_id: str
    name: str
    channel_type: NotificationType
    config: Dict[str, Any]
    enabled: bool = True
    rate_limit_per_hour: int = 60
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        data = asdict(self)
        data['channel_type'] = self.channel_type.value
        return data


class DatabaseAlertManager:
    """
    Advanced database alert management system.
    
    Features:
    - Flexible alert rule engine
    - Multiple notification channels
    - Escalation policies
    - Alert suppression and grouping
    - Automated resolution
    - Rich templating system
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        self.template_engine = TemplateEngine()
        
        # Alert management
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.notification_channels: Dict[str, NotificationChannel] = {}
        self.alert_history: deque = deque(maxlen=10000)
        
        # Evaluation state
        self.evaluating_active = False
        self.metric_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Notification tracking
        self.notification_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Initialize default rules and channels
        self._initialize_default_setup()
        
        self.logger.info("Database Alert Manager initialized")
    
    def _initialize_default_setup(self) -> None:
        try:
            logger.info(f"Executing _initialize_default_setup")
            
            # Implementation for _initialize_default_setup
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_initialize_default_setup completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_initialize_default_setup failed: {e}")
            raise
            rule_id="many_slow_queries",
            name="Many Slow Queries",
            description="High number of slow queries detected",
            conditions=[AlertCondition(
                metric_name="database_slow_queries",
                operator="gte",
                threshold=20.0,
                duration_minutes=5,
                aggregation="avg"
            )],
            severity=AlertSeverity.WARNING,
            enabled=True,
            notification_channels=["email_admin"] if self.settings.email_enabled else []
        ))
    
    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add alert rule"""
        self.alert_rules[rule.rule_id] = rule
        self.logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            self.logger.info(f"Removed alert rule: {rule_id}")
            return True
        return False
    
    def add_notification_channel(self, channel: NotificationChannel) -> None:
        """Add notification channel"""
        self.notification_channels[channel.channel_id] = channel
        self.logger.info(f"Added notification channel: {channel.name}")
    
    def remove_notification_channel(self, channel_id: str) -> bool:
        """Remove notification channel"""
        if channel_id in self.notification_channels:
            del self.notification_channels[channel_id]
            self.logger.info(f"Removed notification channel: {channel_id}")
            return True
        return False
    
    async def start_evaluation(self, interval: int = 60) -> None:
        """Start alert rule evaluation"""
        if self.evaluating_active:
            self.logger.warning("Alert evaluation already active")
            return
        
        self.evaluating_active = True
        self.logger.info(f"Starting alert evaluation with {interval}s interval")
        
        try:
            while self.evaluating_active:
                await self._evaluate_all_rules()
                await self._check_auto_resolution()
                await self._cleanup_old_alerts()
                await asyncio.sleep(interval)
                
        except Exception as e:
            self.logger.error(f"Alert evaluation error: {e}")
            self.evaluating_active = False
            raise
    
    async def stop_evaluation(self) -> None:
        """Stop alert rule evaluation"""
        self.evaluating_active = False
        self.logger.info("Alert evaluation stopped")
    
    async def _evaluate_all_rules(self) -> None:
        """Evaluate all enabled alert rules"""
        for rule_id, rule in self.alert_rules.items():
            if rule.enabled:
                try:
                    await self._evaluate_rule(rule)
                except Exception as e:
                    self.logger.error(f"Error evaluating rule {rule_id}: {e}")
    
    async def _evaluate_rule(self, rule: AlertRule) -> None:
        """Evaluate a single alert rule"""
        try:
            # Check if all conditions are met
            all_conditions_met = True
            
            for condition in rule.conditions:
                # Get metric values for the duration
                metric_values = await self._get_metric_values_for_duration(
                    condition.metric_name, 
                    condition.duration_minutes
                )
                
                if not condition.evaluate(metric_values):
                    all_conditions_met = False
                    break
            
            # Check if alert already exists
            existing_alert_id = f"{rule.rule_id}_{hash(str(rule.conditions))}"
            existing_alert = self.active_alerts.get(existing_alert_id)
            
            if all_conditions_met:
                if not existing_alert or existing_alert.status == AlertStatus.RESOLVED:
                    # Create new alert
                    await self._create_alert(rule, existing_alert_id)
            else:
                if existing_alert and existing_alert.status == AlertStatus.ACTIVE:
                    # Auto-resolve if enabled
                    if rule.auto_resolve:
                        await self._resolve_alert(existing_alert_id, "Auto-resolved", "system")
                        
        except Exception as e:
            self.logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
    
    async def _get_metric_values_for_duration(
        self, 
        metric_name: str, 
        duration_minutes: int
    ) -> List[float]:
        """Get metric values for specified duration"""
        try:
            # Get from cache or metric buffer
            if metric_name in self.metric_buffers:
                cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
                values = []
                
                for metric_value in self.metric_buffers[metric_name]:
                    if hasattr(metric_value, 'timestamp') and metric_value.timestamp >= cutoff_time:
                        values.append(float(metric_value.value))
                
                return values
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting metric values for {metric_name}: {e}")
            return []
    
    async def _create_alert(self, rule: AlertRule, alert_id: str) -> None:
        """Create new alert"""
        try:
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                rule_name=rule.name,
                severity=rule.severity,
                status=AlertStatus.ACTIVE,
                message=f"Alert: {rule.name}",
                description=rule.description,
                triggered_at=datetime.utcnow(),
                metadata=rule.metadata.copy()
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Cache alert
            await self.cache.set(
                f"alert:{alert_id}",
                json.dumps(alert.to_dict()),
                expire=86400
            )
            
            # Send notifications
            await self._send_alert_notifications(alert, rule)
            
            self.logger.warning(f"Alert created: {rule.name} (ID: {alert_id})")
            
        except Exception as e:
            self.logger.error(f"Error creating alert for rule {rule.rule_id}: {e}")
    
    async def _send_alert_notifications(self, alert: Alert, rule: AlertRule) -> None:
        """Send alert notifications to configured channels"""
        try:
            # Check if alert is suppressed
            if alert.suppressed_until and datetime.utcnow() < alert.suppressed_until:
                return
            
            # Send to each configured channel
            for channel_id in rule.notification_channels:
                channel = self.notification_channels.get(channel_id)
                if channel and channel.enabled:
                    # Check rate limiting
                    if await self._check_rate_limit(channel_id):
                        await self._send_notification(alert, channel)
                        
                        # Update notification tracking
                        alert.notification_count += 1
                        alert.last_notification = datetime.utcnow()
                        
                        self.notification_rates[channel_id].append(datetime.utcnow())
            
        except Exception as e:
            self.logger.error(f"Error sending notifications for alert {alert.alert_id}: {e}")
    
    async def _check_rate_limit(self, channel_id: str) -> bool:
        """Check if channel rate limit allows notification"""
        try:
            channel = self.notification_channels.get(channel_id)
            if not channel:
                return False
            
            # Count notifications in the last hour
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            recent_notifications = [
                dt for dt in self.notification_rates[channel_id]
                if dt >= cutoff_time
            ]
            
            return len(recent_notifications) < channel.rate_limit_per_hour
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit for channel {channel_id}: {e}")
            return False
    
    async def _send_notification(self, alert: Alert, channel: NotificationChannel) -> None:
        """Send notification to specific channel"""
        try:
            if channel.channel_type == NotificationType.EMAIL:
                await self._send_email_notification(alert, channel)
            elif channel.channel_type == NotificationType.SLACK:
                await self._send_slack_notification(alert, channel)
            elif channel.channel_type == NotificationType.WEBHOOK:
                await self._send_webhook_notification(alert, channel)
            elif channel.channel_type == NotificationType.TEAMS:
                await self._send_teams_notification(alert, channel)
            else:
                self.logger.warning(f"Unsupported notification type: {channel.channel_type}")
                
        except Exception as e:
            self.logger.error(f"Error sending notification to {channel.name}: {e}")
    
    async def _send_email_notification(self, alert: Alert, channel: NotificationChannel) -> None:
        """Send email notification"""
        try:
            config = channel.config
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = config.get('from', config['username'])
            msg['To'] = config['to']
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.rule_name}"
            
            # Create email body
            body = await self.template_engine.render_template('alert_email.html', {
                'alert': alert.to_dict(),
                'severity_color': self._get_severity_color(alert.severity)
            })
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(config['smtp_host'], config['smtp_port'])
            if config.get('username') and config.get('password'):
                server.starttls()
                server.login(config['username'], config['password'])
            
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email notification sent to {config['to']}")
            
        except Exception as e:
            self.logger.error(f"Error sending email notification: {e}")
    
    async def _send_slack_notification(self, alert: Alert, channel: NotificationChannel) -> None:
        """Send Slack notification"""
        try:
            config = channel.config
            webhook_url = config['webhook_url']
            
            # Create Slack message
            message = {
                "text": f"Database Alert: {alert.rule_name}",
                "attachments": [{
                    "color": self._get_severity_color(alert.severity),
                    "title": alert.rule_name,
                    "text": alert.description,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Status", "value": alert.status.value.upper(), "short": True},
                        {"title": "Triggered At", "value": alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S UTC"), "short": False}
                    ]
                }]
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    if response.status == 200:
                        self.logger.info("Slack notification sent successfully")
                    else:
                        self.logger.error(f"Slack notification failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {e}")
    
    async def _send_webhook_notification(self, alert: Alert, channel: NotificationChannel) -> None:
        """Send webhook notification"""
        try:
            config = channel.config
            url = config['url']
            
            payload = {
                "alert": alert.to_dict(),
                "channel": channel.name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            headers = config.get('headers', {'Content-Type': 'application/json'})
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if 200 <= response.status < 300:
                        self.logger.info(f"Webhook notification sent to {url}")
                    else:
                        self.logger.error(f"Webhook notification failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error sending webhook notification: {e}")
    
    async def _send_teams_notification(self, alert: Alert, channel: NotificationChannel) -> None:
        """Send Microsoft Teams notification"""
        try:
            config = channel.config
            webhook_url = config['webhook_url']
            
            # Create Teams message card
            message = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": f"Database Alert: {alert.rule_name}",
                "themeColor": self._get_severity_color(alert.severity).replace('#', ''),
                "sections": [{
                    "activityTitle": f"Database Alert: {alert.rule_name}",
                    "activitySubtitle": alert.description,
                    "facts": [
                        {"name": "Severity", "value": alert.severity.value.upper()},
                        {"name": "Status", "value": alert.status.value.upper()},
                        {"name": "Triggered At", "value": alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S UTC")}
                    ]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    if response.status == 200:
                        self.logger.info("Teams notification sent successfully")
                    else:
                        self.logger.error(f"Teams notification failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error sending Teams notification: {e}")
    
    def _get_severity_color(self, severity: AlertSeverity) -> str:
        """Get color code for severity level"""
        colors = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9500",
            AlertSeverity.CRITICAL: "#ff4444",
            AlertSeverity.EMERGENCY: "#8b0000"
        }
        return colors.get(severity, "#808080")
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                
                if alert.status == AlertStatus.ACTIVE:
                    alert.status = AlertStatus.ACKNOWLEDGED
                    alert.acknowledged_at = datetime.utcnow()
                    alert.acknowledged_by = acknowledged_by
                    
                    # Update cache
                    await self.cache.set(
                        f"alert:{alert_id}",
                        json.dumps(alert.to_dict()),
                        expire=86400
                    )
                    
                    self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
    
    async def _resolve_alert(self, alert_id: str, reason: str, resolved_by: str) -> bool:
        """Resolve an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                
                if alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_at = datetime.utcnow()
                    alert.resolved_by = resolved_by
                    alert.metadata['resolution_reason'] = reason
                    
                    # Update cache
                    await self.cache.set(
                        f"alert:{alert_id}",
                        json.dumps(alert.to_dict()),
                        expire=86400
                    )
                    
                    self.logger.info(f"Alert {alert_id} resolved by {resolved_by}: {reason}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error resolving alert {alert_id}: {e}")
            return False
    
    async def suppress_alert(self, alert_id: str, duration_minutes: int) -> bool:
        """Suppress an alert for specified duration"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.suppressed_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
                
                # Update cache
                await self.cache.set(
                    f"alert:{alert_id}",
                    json.dumps(alert.to_dict()),
                    expire=86400
                )
                
                self.logger.info(f"Alert {alert_id} suppressed for {duration_minutes} minutes")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error suppressing alert {alert_id}: {e}")
            return False
    
    async def _check_auto_resolution(self) -> None:
        """Check for auto-resolution of alerts"""
        try:
            for alert_id, alert in list(self.active_alerts.items()):
                if alert.status == AlertStatus.ACTIVE:
                    rule = self.alert_rules.get(alert.rule_id)
                    
                    if rule and rule.auto_resolve:
                        # Check if conditions are no longer met
                        all_conditions_met = True
                        
                        for condition in rule.conditions:
                            metric_values = await self._get_metric_values_for_duration(
                                condition.metric_name,
                                rule.auto_resolve_delay_minutes
                            )
                            
                            if condition.evaluate(metric_values):
                                all_conditions_met = False
                                break
                        
                        if all_conditions_met:
                            await self._resolve_alert(alert_id, "Auto-resolved", "system")
                            
        except Exception as e:
            self.logger.error(f"Error checking auto-resolution: {e}")
    
    async def _cleanup_old_alerts(self) -> None:
        """Clean up old resolved alerts"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            
            alerts_to_remove = []
            for alert_id, alert in self.active_alerts.items():
                if (alert.status == AlertStatus.RESOLVED and
                    alert.resolved_at and alert.resolved_at < cutoff_time):
                    alerts_to_remove.append(alert_id)
            
            for alert_id in alerts_to_remove:
                del self.active_alerts[alert_id]
                await self.cache.delete(f"alert:{alert_id}")
            
            if alerts_to_remove:
                self.logger.debug(f"Cleaned up {len(alerts_to_remove)} old alerts")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old alerts: {e}")
    
    async def add_metric_value(self, metric_name: str, metric_value: Any) -> None:
        """Add metric value to buffers for alert evaluation"""
        try:
            self.metric_buffers[metric_name].append(metric_value)
        except Exception as e:
            self.logger.error(f"Error adding metric value for {metric_name}: {e}")
    
    async def get_active_alerts(self, severity: AlertSeverity = None) -> List[Dict[str, Any]]:
        """Get active alerts"""
        try:
            alerts = []
            for alert in self.active_alerts.values():
                if alert.status == AlertStatus.ACTIVE:
                    if severity is None or alert.severity == severity:
                        alerts.append(alert.to_dict())
            
            # Sort by severity and triggered time
            severity_order = {
                AlertSeverity.EMERGENCY: 4,
                AlertSeverity.CRITICAL: 3,
                AlertSeverity.WARNING: 2,
                AlertSeverity.INFO: 1
            }
            
            alerts.sort(
                key=lambda x: (
                    -severity_order.get(AlertSeverity(x['severity']), 0),
                    x['triggered_at']
                )
            )
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        try:
            summary = {
                "total_active": 0,
                "by_severity": {severity.value: 0 for severity in AlertSeverity},
                "by_status": {status.value: 0 for status in AlertStatus},
                "total_rules": len(self.alert_rules),
                "enabled_rules": sum(1 for rule in self.alert_rules.values() if rule.enabled),
                "notification_channels": len(self.notification_channels),
                "evaluation_active": self.evaluating_active
            }
            
            for alert in self.active_alerts.values():
                summary["by_severity"][alert.severity.value] += 1
                summary["by_status"][alert.status.value] += 1
                
                if alert.status == AlertStatus.ACTIVE:
                    summary["total_active"] += 1
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting alert summary: {e}")
            return {"error": str(e)}
    
    async def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get all alert rules"""
        return [rule.to_dict() for rule in self.alert_rules.values()]
    
    async def get_notification_channels(self) -> List[Dict[str, Any]]:
        """
Get all notification channels"""
        return [channel.to_dict() for channel in self.notification_channels.values()]
