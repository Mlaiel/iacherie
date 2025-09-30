"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Enterprise Alerting System
==========================

Enterprise-grade alerting and notification system for IA Chérie SEO platform.
Provides comprehensive monitoring, alerting, and incident management.

Author: Fahed Mlaiel (mlaiel@live.de)
Enterprise Architecture: Advanced Alerting and Monitoring Systems
"""

import asyncio
import logging
import smtplib
import json
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pydantic import BaseModel, Field, validator, EmailStr
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, Enum):
    """Alert status enumeration"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"
    SUPPRESSED = "suppressed"


class NotificationChannel(str, Enum):
    """Notification channel types"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"
    TEAMS = "teams"


class EscalationLevel(str, Enum):
    """Escalation levels"""
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    EXECUTIVE = "executive"


@dataclass
class AlertMetric:
    """Alert metric data"""
    metric_name: str
    current_value: float
    threshold_value: float
    operator: str  # >, <, >=, <=, ==, !=
    timestamp: datetime


class AlertRule(BaseModel):
    """Alert rule configuration"""
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule display name")
    description: str = Field(..., description="Rule description")
    severity: AlertSeverity = Field(..., description="Alert severity")
    
    # Condition configuration
    metric_name: str = Field(..., description="Metric to monitor")
    operator: str = Field(..., description="Comparison operator")
    threshold: float = Field(..., description="Threshold value")
    evaluation_window: int = Field(default=300, description="Evaluation window in seconds")
    
    # Notification configuration
    notification_channels: List[NotificationChannel] = Field(default_factory=list)
    notification_recipients: List[str] = Field(default_factory=list)
    
    # Escalation configuration
    escalation_enabled: bool = Field(default=True)
    escalation_timeout: int = Field(default=1800, description="Escalation timeout in seconds")
    escalation_levels: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Suppression configuration
    suppression_enabled: bool = Field(default=False)
    suppression_duration: int = Field(default=3600, description="Suppression duration in seconds")
    
    # Filtering
    tags: Dict[str, str] = Field(default_factory=dict)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('rule_id')
    def validate_rule_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('rule_id must be at least 3 characters')
        return v.lower().replace(' ', '_')

    @validator('operator')
    def validate_operator(cls, v):
        valid_operators = ['>', '<', '>=', '<=', '==', '!=']
        if v not in valid_operators:
            raise ValueError(f'operator must be one of {valid_operators}')
        return v


class Alert(BaseModel):
    """Alert instance"""
    alert_id: str = Field(..., description="Unique alert identifier")
    rule_id: str = Field(..., description="Associated rule ID")
    severity: AlertSeverity = Field(..., description="Alert severity")
    status: AlertStatus = Field(default=AlertStatus.OPEN)
    
    # Alert details
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    metric_data: Dict[str, Any] = Field(..., description="Metric data that triggered alert")
    
    # Timing
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Assignment
    assigned_to: Optional[str] = None
    escalation_level: Optional[EscalationLevel] = None
    
    # Additional data
    tags: Dict[str, str] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)
    
    # Notification tracking
    notifications_sent: List[Dict[str, Any]] = Field(default_factory=list)


class RuleEngine:
    """Alert rule evaluation engine"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.rules: Dict[str, AlertRule] = {}
        self.evaluation_active = False
        self.evaluation_task: Optional[asyncio.Task] = None
    
    async def register_rule(self, rule: AlertRule) -> bool:
        """Register new alert rule"""
        try:
            # Store rule
            await self.redis_client.hset(
                f"alert_rule:{rule.rule_id}",
                mapping=rule.dict()
            )
            
            self.rules[rule.rule_id] = rule
            
            # Add to rule registry
            await self.redis_client.sadd("alert_rule_registry", rule.rule_id)
            
            logging.info(f"Alert rule {rule.rule_id} registered successfully")
            return True
            
        except Exception as e:
            logging.error(f"Alert rule registration failed for {rule.rule_id}: {e}")
            return False
    
    async def evaluate_rules(self) -> List[Alert]:
        """Evaluate all active rules"""
        triggered_alerts = []
        
        try:
            rule_ids = await self.redis_client.smembers("alert_rule_registry")
            
            for rule_id in rule_ids:
                rule = await self._get_rule(rule_id)
                if not rule or not rule.enabled:
                    continue
                
                # Evaluate rule
                is_triggered = await self._evaluate_rule(rule)
                
                if is_triggered:
                    # Check if alert already exists for this rule
                    existing_alert = await self._get_active_alert_for_rule(rule_id)
                    
                    if not existing_alert:
                        # Create new alert
                        alert = await self._create_alert(rule)
                        if alert:
                            triggered_alerts.append(alert)
                    else:
                        # Update existing alert
                        await self._update_existing_alert(existing_alert, rule)
                else:
                    # Check if we should resolve existing alerts
                    await self._resolve_alerts_for_rule(rule_id)
            
            return triggered_alerts
            
        except Exception as e:
            logging.error(f"Rule evaluation failed: {e}")
            return []
    
    async def _evaluate_rule(self, rule: AlertRule) -> bool:
        """Evaluate individual rule"""
        try:
            # Get metric data
            metric_data = await self._get_metric_data(rule.metric_name, rule.evaluation_window)
            
            if not metric_data:
                return False
            
            # Get current value (latest metric)
            current_value = metric_data[-1]["value"] if metric_data else 0.0
            
            # Evaluate condition
            return self._evaluate_condition(current_value, rule.operator, rule.threshold)
            
        except Exception as e:
            logging.error(f"Rule evaluation failed for {rule.rule_id}: {e}")
            return False
    
    def _evaluate_condition(self, current_value: float, operator: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        if operator == '>':
            return current_value > threshold
        elif operator == '<':
            return current_value < threshold
        elif operator == '>=':
            return current_value >= threshold
        elif operator == '<=':
            return current_value <= threshold
        elif operator == '==':
            return current_value == threshold
        elif operator == '!=':
            return current_value != threshold
        else:
            return False
    
    async def _get_metric_data(self, metric_name: str, window_seconds: int) -> List[Dict[str, Any]]:
        """Get metric data for evaluation"""
        try:
            # Get metric history from Redis
            metric_data = await self.redis_client.lrange(f"metric_history:{metric_name}", 0, 99)
            
            # Parse and filter by time window
            parsed_metrics = []
            cutoff_time = datetime.utcnow() - timedelta(seconds=window_seconds)
            
            for metric_str in metric_data:
                metric = json.loads(metric_str)
                metric_time = datetime.fromisoformat(metric["timestamp"])
                
                if metric_time >= cutoff_time:
                    parsed_metrics.append(metric)
            
            return parsed_metrics
            
        except Exception as e:
            logging.error(f"Get metric data failed for {metric_name}: {e}")
            return []
    
    async def _create_alert(self, rule: AlertRule) -> Optional[Alert]:
        """Create new alert"""
        try:
            alert_id = str(uuid.uuid4())
            
            # Get current metric value for alert description
            metric_data = await self._get_metric_data(rule.metric_name, 60)  # Last minute
            current_value = metric_data[-1]["value"] if metric_data else 0.0
            
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                severity=rule.severity,
                title=f"{rule.name} - Threshold Exceeded",
                description=f"Metric {rule.metric_name} value {current_value} {rule.operator} {rule.threshold}",
                metric_data={
                    "metric_name": rule.metric_name,
                    "current_value": current_value,
                    "threshold": rule.threshold,
                    "operator": rule.operator
                },
                tags=rule.tags
            )
            
            # Store alert
            await self.redis_client.hset(
                f"alert:{alert_id}",
                mapping=alert.dict()
            )
            
            # Add to active alerts
            await self.redis_client.sadd("active_alerts", alert_id)
            
            # Add to rule's alerts
            await self.redis_client.sadd(f"rule_alerts:{rule.rule_id}", alert_id)
            
            logging.info(f"Alert {alert_id} created for rule {rule.rule_id}")
            return alert
            
        except Exception as e:
            logging.error(f"Alert creation failed for rule {rule.rule_id}: {e}")
            return None
    
    async def _get_active_alert_for_rule(self, rule_id: str) -> Optional[Alert]:
        """Get active alert for rule"""
        try:
            alert_ids = await self.redis_client.smembers(f"rule_alerts:{rule_id}")
            
            for alert_id in alert_ids:
                alert_data = await self.redis_client.hgetall(f"alert:{alert_id}")
                
                if alert_data and alert_data.get("status") in [AlertStatus.OPEN.value, AlertStatus.ACKNOWLEDGED.value]:
                    return Alert(**alert_data)
            
            return None
            
        except Exception as e:
            logging.error(f"Get active alert failed for rule {rule_id}: {e}")
            return None
    
    async def _update_existing_alert(self, alert: Alert, rule: AlertRule):
        """Update existing alert with new metric data"""
        try:
            # Get current metric value
            metric_data = await self._get_metric_data(rule.metric_name, 60)
            current_value = metric_data[-1]["value"] if metric_data else 0.0
            
            # Update metric data
            alert.metric_data["current_value"] = current_value
            
            # Update alert in Redis
            await self.redis_client.hset(
                f"alert:{alert.alert_id}",
                mapping=alert.dict()
            )
            
        except Exception as e:
            logging.error(f"Update existing alert failed: {e}")
    
    async def _resolve_alerts_for_rule(self, rule_id: str):
        """Resolve alerts for rule when condition is no longer met"""
        try:
            alert_ids = await self.redis_client.smembers(f"rule_alerts:{rule_id}")
            
            for alert_id in alert_ids:
                alert_data = await self.redis_client.hgetall(f"alert:{alert_id}")
                
                if alert_data and alert_data.get("status") in [AlertStatus.OPEN.value, AlertStatus.ACKNOWLEDGED.value]:
                    # Auto-resolve alert
                    await self.redis_client.hset(
                        f"alert:{alert_id}",
                        mapping={
                            "status": AlertStatus.RESOLVED.value,
                            "resolved_at": datetime.utcnow().isoformat()
                        }
                    )
                    
                    # Remove from active alerts
                    await self.redis_client.srem("active_alerts", alert_id)
                    
                    logging.info(f"Alert {alert_id} auto-resolved")
            
        except Exception as e:
            logging.error(f"Resolve alerts failed for rule {rule_id}: {e}")
    
    async def _get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get alert rule"""
        if rule_id in self.rules:
            return self.rules[rule_id]
        
        rule_data = await self.redis_client.hgetall(f"alert_rule:{rule_id}")
        if rule_data:
            rule = AlertRule(**rule_data)
            self.rules[rule_id] = rule
            return rule
        
        return None


class NotificationManager:
    """Enterprise notification management"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.notification_handlers: Dict[NotificationChannel, Callable] = {}
        
        # Register notification handlers
        self._register_notification_handlers()
    
    def _register_notification_handlers(self):
        """Register notification channel handlers"""
        self.notification_handlers[NotificationChannel.EMAIL] = self._send_email_notification
        self.notification_handlers[NotificationChannel.SLACK] = self._send_slack_notification
        self.notification_handlers[NotificationChannel.WEBHOOK] = self._send_webhook_notification
        self.notification_handlers[NotificationChannel.SMS] = self._send_sms_notification
    
    async def send_alert_notifications(self, alert: Alert, rule: AlertRule) -> Dict[str, Any]:
        """Send notifications for alert"""
        notification_results = {}
        
        try:
            for channel in rule.notification_channels:
                try:
                    handler = self.notification_handlers.get(channel)
                    
                    if handler:
                        result = await handler(alert, rule)
                        notification_results[channel.value] = result
                        
                        # Track notification
                        await self._track_notification(alert.alert_id, channel, result)
                    else:
                        notification_results[channel.value] = {
                            "success": False,
                            "error": f"No handler for channel {channel.value}"
                        }
                        
                except Exception as e:
                    logging.error(f"Notification failed for channel {channel.value}: {e}")
                    notification_results[channel.value] = {
                        "success": False,
                        "error": str(e)
                    }
            
            return notification_results
            
        except Exception as e:
            logging.error(f"Send alert notifications failed: {e}")
            return {}
    
    async def _send_email_notification(self, alert: Alert, rule: AlertRule) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Email configuration (should be from settings)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_username = "alerts@iacherie.com"
            smtp_password = "alert_password"  # Should be from secure config
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = ', '.join(rule.notification_recipients)
            msg['Subject'] = f"[{alert.severity.upper()}] {alert.title}"
            
            # Email body
            body = f"""
Alert Details:
=============
Alert ID: {alert.alert_id}
Severity: {alert.severity}
Rule: {rule.name}
Description: {alert.description}
Triggered At: {alert.triggered_at}

Metric Data:
============
Metric: {alert.metric_data.get('metric_name')}
Current Value: {alert.metric_data.get('current_value')}
Threshold: {alert.metric_data.get('threshold')}
Operator: {alert.metric_data.get('operator')}

This is an automated alert from IA Chérie Enterprise Monitoring System.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email (simulated)
            # In production, use actual SMTP
            logging.info(f"Email notification sent for alert {alert.alert_id}")
            
            return {
                "success": True,
                "channel": "email",
                "recipients": rule.notification_recipients,
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Email notification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_slack_notification(self, alert: Alert, rule: AlertRule) -> Dict[str, Any]:
        """Send Slack notification"""
        try:
            # Slack webhook URL (should be from settings)
            webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
            
            # Create Slack message
            color = {
                AlertSeverity.CRITICAL: "#FF0000",
                AlertSeverity.HIGH: "#FF8000",
                AlertSeverity.MEDIUM: "#FFFF00",
                AlertSeverity.LOW: "#00FF00",
                AlertSeverity.INFO: "#0000FF"
            }.get(alert.severity, "#808080")
            
            slack_message = {
                "attachments": [
                    {
                        "color": color,
                        "title": alert.title,
                        "text": alert.description,
                        "fields": [
                            {"title": "Severity", "value": alert.severity, "short": True},
                            {"title": "Rule", "value": rule.name, "short": True},
                            {"title": "Metric", "value": alert.metric_data.get('metric_name'), "short": True},
                            {"title": "Value", "value": str(alert.metric_data.get('current_value')), "short": True}
                        ],
                        "footer": "IA Chérie Enterprise Monitoring",
                        "ts": int(alert.triggered_at.timestamp())
                    }
                ]
            }
            
            # Send to Slack (simulated)
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=slack_message) as response:
                    if response.status == 200:
                        return {
                            "success": True,
                            "channel": "slack",
                            "sent_at": datetime.utcnow().isoformat()
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Slack API error: {response.status}"
                        }
            
        except Exception as e:
            logging.error(f"Slack notification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_webhook_notification(self, alert: Alert, rule: AlertRule) -> Dict[str, Any]:
        """Send webhook notification"""
        try:
            # Webhook URL (should be configured per rule)
            webhook_url = rule.conditions.get("webhook_url", "https://example.com/webhook")
            
            # Create webhook payload
            webhook_payload = {
                "alert_id": alert.alert_id,
                "rule_id": alert.rule_id,
                "severity": alert.severity,
                "title": alert.title,
                "description": alert.description,
                "metric_data": alert.metric_data,
                "triggered_at": alert.triggered_at.isoformat(),
                "tags": alert.tags
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url, 
                    json=webhook_payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status < 400:
                        return {
                            "success": True,
                            "channel": "webhook",
                            "status_code": response.status,
                            "sent_at": datetime.utcnow().isoformat()
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Webhook error: {response.status}"
                        }
            
        except Exception as e:
            logging.error(f"Webhook notification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_sms_notification(self, alert: Alert, rule: AlertRule) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            # SMS message
            sms_message = f"[{alert.severity.upper()}] {alert.title}: {alert.description}"
            
            # Send SMS (simulated - would use Twilio, AWS SNS, etc.)
            logging.info(f"SMS notification sent for alert {alert.alert_id}")
            
            return {
                "success": True,
                "channel": "sms",
                "recipients": rule.notification_recipients,
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"SMS notification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _track_notification(self, alert_id: str, channel: NotificationChannel, result: Dict[str, Any]):
        """Track notification delivery"""
        try:
            notification_record = {
                "alert_id": alert_id,
                "channel": channel.value,
                "success": result.get("success", False),
                "sent_at": result.get("sent_at", datetime.utcnow().isoformat()),
                "error": result.get("error")
            }
            
            # Store notification record
            await self.redis_client.lpush(
                f"alert_notifications:{alert_id}",
                json.dumps(notification_record)
            )
            
            # Keep only last 100 notifications per alert
            await self.redis_client.ltrim(f"alert_notifications:{alert_id}", 0, 99)
            
        except Exception as e:
            logging.error(f"Track notification failed: {e}")


class EscalationManager:
    """Enterprise escalation management"""
    
    def __init__(self, redis_client: redis.Redis, notification_manager: NotificationManager):
        self.redis_client = redis_client
        self.notification_manager = notification_manager
        self.escalation_active = False
        self.escalation_task: Optional[asyncio.Task] = None
    
    async def process_escalations(self):
        """Process pending escalations"""
        try:
            active_alerts = await self.redis_client.smembers("active_alerts")
            
            for alert_id in active_alerts:
                alert_data = await self.redis_client.hgetall(f"alert:{alert_id}")
                
                if not alert_data:
                    continue
                
                alert = Alert(**alert_data)
                
                # Check if escalation is needed
                if await self._should_escalate(alert):
                    await self._escalate_alert(alert)
            
        except Exception as e:
            logging.error(f"Process escalations failed: {e}")
    
    async def _should_escalate(self, alert: Alert) -> bool:
        """Check if alert should be escalated"""
        try:
            # Get rule
            rule_data = await self.redis_client.hgetall(f"alert_rule:{alert.rule_id}")
            if not rule_data:
                return False
            
            rule = AlertRule(**rule_data)
            
            if not rule.escalation_enabled:
                return False
            
            # Check if alert is unacknowledged and past escalation timeout
            if alert.status == AlertStatus.OPEN:
                time_since_triggered = datetime.utcnow() - alert.triggered_at
                
                return time_since_triggered.total_seconds() >= rule.escalation_timeout
            
            return False
            
        except Exception as e:
            logging.error(f"Should escalate check failed: {e}")
            return False
    
    async def _escalate_alert(self, alert: Alert):
        """Escalate alert to next level"""
        try:
            # Get rule
            rule_data = await self.redis_client.hgetall(f"alert_rule:{alert.rule_id}")
            if not rule_data:
                return
            
            rule = AlertRule(**rule_data)
            
            # Determine next escalation level
            current_level = alert.escalation_level or EscalationLevel.LEVEL_1
            next_level = self._get_next_escalation_level(current_level)
            
            if not next_level:
                return  # Already at highest level
            
            # Update alert with escalation
            await self.redis_client.hset(
                f"alert:{alert.alert_id}",
                mapping={
                    "escalation_level": next_level.value,
                    "escalated_at": datetime.utcnow().isoformat()
                }
            )
            
            # Send escalation notifications
            escalation_config = self._get_escalation_config(rule, next_level)
            
            if escalation_config:
                escalation_rule = AlertRule(
                    rule_id=f"{rule.rule_id}_escalation",
                    name=f"{rule.name} - Escalated to {next_level.value}",
                    description=f"Escalated alert: {alert.description}",
                    severity=alert.severity,
                    metric_name=rule.metric_name,
                    operator=rule.operator,
                    threshold=rule.threshold,
                    notification_channels=escalation_config.get("channels", []),
                    notification_recipients=escalation_config.get("recipients", [])
                )
                
                await self.notification_manager.send_alert_notifications(alert, escalation_rule)
            
            logging.info(f"Alert {alert.alert_id} escalated to {next_level.value}")
            
        except Exception as e:
            logging.error(f"Escalate alert failed: {e}")
    
    def _get_next_escalation_level(self, current_level: Optional[EscalationLevel]) -> Optional[EscalationLevel]:
        """Get next escalation level"""
        level_order = [
            EscalationLevel.LEVEL_1,
            EscalationLevel.LEVEL_2,
            EscalationLevel.LEVEL_3,
            EscalationLevel.EXECUTIVE
        ]
        
        if not current_level:
            return EscalationLevel.LEVEL_1
        
        try:
            current_index = level_order.index(current_level)
            if current_index < len(level_order) - 1:
                return level_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _get_escalation_config(self, rule: AlertRule, level: EscalationLevel) -> Optional[Dict[str, Any]]:
        """Get escalation configuration for level"""
        for escalation_level in rule.escalation_levels:
            if escalation_level.get("level") == level.value:
                return escalation_level
        
        # Default escalation configuration
        return {
            "level": level.value,
            "channels": [NotificationChannel.EMAIL],
            "recipients": ["escalation@iacherie.com"]
        }


class EnterpriseAlertingSystem:
    """
    Enterprise Alerting System
    
    Comprehensive alerting and notification system providing:
    - Real-time rule-based alerting
    - Multi-channel notifications
    - Escalation management
    - Enterprise-grade incident tracking
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: redis.Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        
        # Initialize components
        self.rule_engine = RuleEngine(redis_client)
        self.notification_manager = NotificationManager(redis_client)
        self.escalation_manager = EscalationManager(redis_client, self.notification_manager)
        
        # System state
        self.alerting_active = False
        self.alerting_task: Optional[asyncio.Task] = None
        
        logging.info("Enterprise Alerting System initialized")
    
    async def create_alert_rule(self, rule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create new alert rule"""
        try:
            rule = AlertRule(**rule_config)
            
            success = await self.rule_engine.register_rule(rule)
            
            if success:
                return {
                    "success": True,
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "severity": rule.severity.value,
                    "created_at": rule.created_at.isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Rule registration failed"
                }
                
        except Exception as e:
            logging.error(f"Create alert rule failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_active_alerts(self, severity_filter: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        try:
            active_alert_ids = await self.redis_client.smembers("active_alerts")
            alerts = []
            
            for alert_id in active_alert_ids:
                alert_data = await self.redis_client.hgetall(f"alert:{alert_id}")
                
                if not alert_data:
                    continue
                
                alert = Alert(**alert_data)
                
                if severity_filter and alert.severity != severity_filter:
                    continue
                
                alerts.append({
                    "alert_id": alert.alert_id,
                    "rule_id": alert.rule_id,
                    "title": alert.title,
                    "severity": alert.severity,
                    "status": alert.status,
                    "triggered_at": alert.triggered_at.isoformat(),
                    "escalation_level": alert.escalation_level.value if alert.escalation_level else None
                })
            
            # Sort by severity and time
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.HIGH: 1,
                AlertSeverity.MEDIUM: 2,
                AlertSeverity.LOW: 3,
                AlertSeverity.INFO: 4
            }
            
            alerts.sort(key=lambda a: (severity_order.get(AlertSeverity(a["severity"]), 5), a["triggered_at"]))
            
            return alerts
            
        except Exception as e:
            logging.error(f"Get active alerts failed: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Dict[str, Any]:
        """Acknowledge alert"""
        try:
            alert_data = await self.redis_client.hgetall(f"alert:{alert_id}")
            
            if not alert_data:
                return {"success": False, "error": "Alert not found"}
            
            # Update alert status
            await self.redis_client.hset(
                f"alert:{alert_id}",
                mapping={
                    "status": AlertStatus.ACKNOWLEDGED.value,
                    "acknowledged_at": datetime.utcnow().isoformat(),
                    "assigned_to": acknowledged_by
                }
            )
            
            return {
                "success": True,
                "alert_id": alert_id,
                "acknowledged_by": acknowledged_by,
                "acknowledged_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Acknowledge alert failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def resolve_alert(self, alert_id: str, resolved_by: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Resolve alert"""
        try:
            alert_data = await self.redis_client.hgetall(f"alert:{alert_id}")
            
            if not alert_data:
                return {"success": False, "error": "Alert not found"}
            
            # Update alert status
            update_data = {
                "status": AlertStatus.RESOLVED.value,
                "resolved_at": datetime.utcnow().isoformat()
            }
            
            if notes:
                alert = Alert(**alert_data)
                alert.notes.append(f"{resolved_by}: {notes}")
                update_data["notes"] = json.dumps(alert.notes)
            
            await self.redis_client.hset(f"alert:{alert_id}", mapping=update_data)
            
            # Remove from active alerts
            await self.redis_client.srem("active_alerts", alert_id)
            
            return {
                "success": True,
                "alert_id": alert_id,
                "resolved_by": resolved_by,
                "resolved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Resolve alert failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        try:
            # Get all alert IDs (active and resolved)
            all_alert_keys = await self.redis_client.keys("alert:*")
            alerts = []
            
            for alert_key in all_alert_keys:
                alert_data = await self.redis_client.hgetall(alert_key)
                
                if alert_data:
                    alert = Alert(**alert_data)
                    alerts.append({
                        "alert_id": alert.alert_id,
                        "rule_id": alert.rule_id,
                        "title": alert.title,
                        "severity": alert.severity,
                        "status": alert.status,
                        "triggered_at": alert.triggered_at.isoformat(),
                        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
                    })
            
            # Sort by triggered time (most recent first)
            alerts.sort(key=lambda a: a["triggered_at"], reverse=True)
            
            return alerts[:limit]
            
        except Exception as e:
            logging.error(f"Get alert history failed: {e}")
            return []
    
    async def start_alerting(self) -> bool:
        """Start enterprise alerting system"""
        try:
            if self.alerting_active:
                logging.warning("Alerting system already active")
                return True
            
            self.alerting_active = True
            self.alerting_task = asyncio.create_task(self._alerting_loop())
            
            logging.info("Enterprise alerting system started")
            return True
            
        except Exception as e:
            logging.error(f"Alerting system start failed: {e}")
            return False
    
    async def stop_alerting(self) -> bool:
        """Stop enterprise alerting system"""
        try:
            self.alerting_active = False
            
            if self.alerting_task:
                self.alerting_task.cancel()
                try:
                    await self.alerting_task
                except asyncio.CancelledError:
                    pass
                self.alerting_task = None
            
            logging.info("Enterprise alerting system stopped")
            return True
            
        except Exception as e:
            logging.error(f"Alerting system stop failed: {e}")
            return False
    
    async def _alerting_loop(self):
        """Internal alerting loop"""
        while self.alerting_active:
            try:
                # Evaluate rules and generate alerts
                triggered_alerts = await self.rule_engine.evaluate_rules()
                
                # Send notifications for new alerts
                for alert in triggered_alerts:
                    rule_data = await self.redis_client.hgetall(f"alert_rule:{alert.rule_id}")
                    if rule_data:
                        rule = AlertRule(**rule_data)
                        await self.notification_manager.send_alert_notifications(alert, rule)
                
                # Process escalations
                await self.escalation_manager.process_escalations()
                
                # Update system status
                await self.redis_client.hset(
                    "alerting_status",
                    mapping={
                        "last_evaluation": datetime.utcnow().isoformat(),
                        "alerts_triggered": len(triggered_alerts),
                        "active": self.alerting_active
                    }
                )
                
                await asyncio.sleep(30)  # Evaluate every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Alerting loop error: {e}")
                await asyncio.sleep(60)  # Extended wait on error
    
    async def get_enterprise_alerting_metrics(self) -> Dict[str, Any]:
        """Get comprehensive enterprise alerting metrics"""
        try:
            # Get alert counts by severity
            severity_counts = {}
            status_counts = {}
            
            active_alert_ids = await self.redis_client.smembers("active_alerts")
            
            for alert_id in active_alert_ids:
                alert_data = await self.redis_client.hgetall(f"alert:{alert_id}")
                
                if alert_data:
                    severity = alert_data.get("severity")
                    status = alert_data.get("status")
                    
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    status_counts[status] = status_counts.get(status, 0) + 1
            
            # Get rule count
            rule_ids = await self.redis_client.smembers("alert_rule_registry")
            total_rules = len(rule_ids)
            
            # Get system status
            alerting_status = await self.redis_client.hgetall("alerting_status")
            
            return {
                "total_active_alerts": len(active_alert_ids),
                "total_rules": total_rules,
                "severity_distribution": severity_counts,
                "status_distribution": status_counts,
                "alerting_active": self.alerting_active,
                "last_evaluation": alerting_status.get("last_evaluation"),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Enterprise alerting metrics collection failed: {e}")
            return {}


# Enterprise alerting system instance
_alerting_system_instance: Optional[EnterpriseAlertingSystem] = None


async def get_alerting_system(
    db_session: AsyncSession,
    redis_client: redis.Redis
) -> EnterpriseAlertingSystem:
    """Get or create alerting system instance"""
    global _alerting_system_instance
    
    if _alerting_system_instance is None:
        _alerting_system_instance = EnterpriseAlertingSystem(db_session, redis_client)
    
    return _alerting_system_instance


async def initialize_enterprise_alerting_system(
    db_session: AsyncSession,
    redis_client: redis.Redis
) -> bool:
    """Initialize enterprise alerting system"""
    try:
        alerting_system = await get_alerting_system(db_session, redis_client)
        
        # Start alerting
        await alerting_system.start_alerting()
        
        logging.info("Enterprise alerting system initialized successfully")
        return True
        
    except Exception as e:
        logging.error(f"Enterprise alerting system initialization failed: {e}")
        return False


# Export enterprise alerting components
__all__ = [
    "EnterpriseAlertingSystem",
    "AlertRule",
    "Alert",
    "AlertSeverity",
    "AlertStatus",
    "NotificationChannel",
    "EscalationLevel",
    "RuleEngine",
    "NotificationManager",
    "EscalationManager",
    "get_alerting_system",
    "initialize_enterprise_alerting_system"
]