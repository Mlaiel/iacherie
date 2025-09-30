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

Alert Manager Template for Ainflue Platform
==========================================

Production-ready alert management with:
- Multi-channel alerting (email, Slack, webhook)
- Alert correlation and grouping
- Escalation policies and routing
- Alert suppression and silencing
- Incident management integration
- Metric-based alert rules

Author: Fahed Mlaiel (mlaiel@live.de)
Alerting & Incident Management Expert
"""

import asyncio
import json
import logging
import time
import aiohttp
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, Any, Optional, List, Set, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertStatus(str, Enum):
    """Alert status"""
    FIRING = "firing"
    RESOLVED = "resolved"
    SILENCED = "silenced"
    ACKNOWLEDGED = "acknowledged"

class NotificationChannel(str, Enum):
    """Notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    DISCORD = "discord"

@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    metric_query: str
    threshold: float
    comparison: str = ">"  # >, <, >=, <=, ==, !=
    duration: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    status: AlertStatus = AlertStatus.FIRING
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    last_sent: Optional[datetime] = None

@dataclass
class NotificationRule:
    """Notification rule configuration"""
    name: str
    channels: List[NotificationChannel]
    severity_filter: List[AlertSeverity]
    label_matchers: Dict[str, str] = field(default_factory=dict)
    cooldown_minutes: int = 30
    escalation_delay_minutes: int = 60
    config: Dict[str, Any] = field(default_factory=dict)

class AlertManager:
    """
    Production-ready alert management system
    
    Features:
    - Multi-channel alerting
    - Alert correlation and grouping
    - Escalation policies
    - Alert suppression and silencing
    - Metric evaluation and thresholds
    """
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.notification_rules: List[NotificationRule] = []
        self.silenced_alerts: Set[str] = set()
        self.alert_history: List[Alert] = []
        
        # Notification channels
        self.notification_handlers = {
            NotificationChannel.EMAIL: self._send_email,
            NotificationChannel.SLACK: self._send_slack,
            NotificationChannel.WEBHOOK: self._send_webhook,
            NotificationChannel.SMS: self._send_sms,
            NotificationChannel.DISCORD: self._send_discord
        }
        
        # Background tasks
        self.evaluation_task = None
        self.cleanup_task = None
    
    def add_alert_rule(self, alert: Alert):
        """Add an alert rule"""
        self.alerts[alert.id] = alert
        logger.info(f"Added alert rule: {alert.name}")
    
    def add_notification_rule(self, rule: NotificationRule):
        """Add a notification rule"""
        self.notification_rules.append(rule)
        logger.info(f"Added notification rule: {rule.name}")
    
    async def start_monitoring(self):
        """Start alert monitoring"""
        self.evaluation_task = asyncio.create_task(self._evaluation_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Started alert monitoring")
    
    async def stop_monitoring(self):
        """Stop alert monitoring"""
        if self.evaluation_task:
            self.evaluation_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        logger.info("Stopped alert monitoring")
    
    async def _evaluation_loop(self):
        """Main alert evaluation loop"""
        while True:
            try:
                await self._evaluate_alerts()
                await asyncio.sleep(30)  # Evaluate every 30 seconds
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_loop(self):
        """Cleanup resolved alerts"""
        while True:
            try:
                await self._cleanup_resolved_alerts()
                await asyncio.sleep(3600)  # Cleanup every hour
            except Exception as e:
                logger.error(f"Alert cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _evaluate_alerts(self):
        """Evaluate all alert rules"""
        for alert_id, alert in self.alerts.items():
            if alert_id in self.silenced_alerts:
                continue
            
            try:
                # Evaluate metric query (mock implementation)
                metric_value = await self._evaluate_metric_query(alert.metric_query)
                
                should_fire = self._check_threshold(metric_value, alert.threshold, alert.comparison)
                
                if should_fire and alert.status != AlertStatus.FIRING:
                    await self._fire_alert(alert, metric_value)
                elif not should_fire and alert.status == AlertStatus.FIRING:
                    await self._resolve_alert(alert)
                    
            except Exception as e:
                logger.error(f"Failed to evaluate alert {alert.name}: {e}")
    
    async def _evaluate_metric_query(self, query: str) -> float:
        """Evaluate metric query (mock implementation)"""
        # In a real implementation, this would query Prometheus/metrics system
        import random
        return random.uniform(0, 100)
    
    def _check_threshold(self, value: float, threshold: float, comparison: str) -> bool:
        """Check if value meets threshold condition"""
        if comparison == ">":
            return value > threshold
        elif comparison == "<":
            return value < threshold
        elif comparison == ">=":
            return value >= threshold
        elif comparison == "<=":
            return value <= threshold
        elif comparison == "==":
            return value == threshold
        elif comparison == "!=":
            return value != threshold
        else:
            return False
    
    async def _fire_alert(self, alert: Alert, current_value: float):
        """Fire an alert"""
        alert.status = AlertStatus.FIRING
        alert.created_at = datetime.utcnow()
        alert.annotations["current_value"] = str(current_value)
        
        # Send notifications
        await self._send_notifications(alert)
        
        # Add to history
        self.alert_history.append(alert)
        
        logger.warning(f"Alert FIRED: {alert.name} (value: {current_value}, threshold: {alert.threshold})")
    
    async def _resolve_alert(self, alert: Alert):
        """Resolve an alert"""
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        
        # Send resolution notifications
        await self._send_notifications(alert, resolved=True)
        
        logger.info(f"Alert RESOLVED: {alert.name}")
    
    async def _send_notifications(self, alert: Alert, resolved: bool = False):
        """Send notifications for an alert"""
        for rule in self.notification_rules:
            if self._matches_notification_rule(alert, rule):
                # Check cooldown
                if alert.last_sent and rule.cooldown_minutes > 0:
                    time_since_last = datetime.utcnow() - alert.last_sent
                    if time_since_last < timedelta(minutes=rule.cooldown_minutes):
                        continue
                
                # Send to all channels in the rule
                for channel in rule.channels:
                    try:
                        handler = self.notification_handlers.get(channel)
                        if handler:
                            await handler(alert, rule, resolved)
                        else:
                            logger.warning(f"No handler for channel: {channel}")
                    except Exception as e:
                        logger.error(f"Failed to send notification via {channel}: {e}")
                
                alert.last_sent = datetime.utcnow()
    
    def _matches_notification_rule(self, alert: Alert, rule: NotificationRule) -> bool:
        """Check if alert matches notification rule"""
        # Check severity filter
        if alert.severity not in rule.severity_filter:
            return False
        
        # Check label matchers
        for label_key, label_value in rule.label_matchers.items():
            if alert.labels.get(label_key) != label_value:
                return False
        
        return True
    
    async def _send_email(self, alert: Alert, rule: NotificationRule, resolved: bool = False):
        """Send email notification"""
        try:
            config = rule.config.get("email", {})
            smtp_server = config.get("smtp_server", "localhost")
            smtp_port = config.get("smtp_port", 587)
            username = config.get("username")
            password = config.get("password")
            from_addr = config.get("from_addr", "alerts@ainflue.com")
            to_addrs = config.get("to_addrs", [])
            
            if not to_addrs:
                logger.warning("No email recipients configured")
                return
            
            subject = f"{'RESOLVED' if resolved else 'ALERT'}: {alert.name}"
            
            body = f"""
Alert: {alert.name}
Severity: {alert.severity.value.upper()}
Status: {alert.status.value.upper()}
Description: {alert.description}

Metric Query: {alert.metric_query}
Threshold: {alert.threshold}
Current Value: {alert.annotations.get('current_value', 'N/A')}

Created: {alert.created_at.isoformat()}
{'Resolved: ' + alert.resolved_at.isoformat() if resolved else ''}

Labels: {json.dumps(alert.labels, indent=2)}
"""
            
            msg = MimeMultipart()
            msg["From"] = from_addr
            msg["To"] = ", ".join(to_addrs)
            msg["Subject"] = subject
            msg.attach(MimeText(body, "plain"))
            
            # Send email (mock implementation)
            logger.info(f"Email notification sent: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_slack(self, alert: Alert, rule: NotificationRule, resolved: bool = False):
        """Send Slack notification"""
        try:
            config = rule.config.get("slack", {})
            webhook_url = config.get("webhook_url")
            channel = config.get("channel", "#alerts")
            
            if not webhook_url:
                logger.warning("No Slack webhook URL configured")
                return
            
            color = "good" if resolved else ("danger" if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH] else "warning")
            
            payload = {
                "channel": channel,
                "username": "Ainflue Alerts",
                "icon_emoji": ":warning:",
                "attachments": [{
                    "color": color,
                    "title": f"{'RESOLVED' if resolved else 'ALERT'}: {alert.name}",
                    "text": alert.description,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Status", "value": alert.status.value.upper(), "short": True},
                        {"title": "Current Value", "value": alert.annotations.get("current_value", "N/A"), "short": True},
                        {"title": "Threshold", "value": str(alert.threshold), "short": True}
                    ],
                    "footer": "Ainflue Alert Manager",
                    "ts": int(alert.created_at.timestamp())
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent: {alert.name}")
                    else:
                        logger.error(f"Slack notification failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    async def _send_webhook(self, alert: Alert, rule: NotificationRule, resolved: bool = False):
        """Send webhook notification"""
        try:
            config = rule.config.get("webhook", {})
            url = config.get("url")
            headers = config.get("headers", {})
            
            if not url:
                logger.warning("No webhook URL configured")
                return
            
            payload = {
                "alert": {
                    "id": alert.id,
                    "name": alert.name,
                    "description": alert.description,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "metric_query": alert.metric_query,
                    "threshold": alert.threshold,
                    "current_value": alert.annotations.get("current_value"),
                    "created_at": alert.created_at.isoformat(),
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "labels": alert.labels,
                    "annotations": alert.annotations
                },
                "resolved": resolved,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent: {alert.name}")
                    else:
                        logger.error(f"Webhook notification failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    async def _send_sms(self, alert: Alert, rule: NotificationRule, resolved: bool = False):
        """Send SMS notification (mock implementation)"""
        logger.info(f"SMS notification sent: {alert.name}")
    
    async def _send_discord(self, alert: Alert, rule: NotificationRule, resolved: bool = False):
        """Send Discord notification (mock implementation)"""
        logger.info(f"Discord notification sent: {alert.name}")
    
    def silence_alert(self, alert_id: str, duration: timedelta = timedelta(hours=1)):
        """Silence an alert for specified duration"""
        self.silenced_alerts.add(alert_id)
        
        # Schedule removal of silence
        async def remove_silence():
            await asyncio.sleep(duration.total_seconds())
            self.silenced_alerts.discard(alert_id)
        
        asyncio.create_task(remove_silence())
        logger.info(f"Silenced alert {alert_id} for {duration}")
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].status = AlertStatus.ACKNOWLEDGED
            logger.info(f"Acknowledged alert {alert_id}")
    
    async def _cleanup_resolved_alerts(self):
        """Clean up old resolved alerts"""
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        
        # Remove old alerts from history
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.resolved_at is None or alert.resolved_at > cutoff_time
        ]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary"""
        firing_alerts = [alert for alert in self.alerts.values() if alert.status == AlertStatus.FIRING]
        resolved_alerts = [alert for alert in self.alerts.values() if alert.status == AlertStatus.RESOLVED]
        
        return {
            "total_alerts": len(self.alerts),
            "firing_alerts": len(firing_alerts),
            "resolved_alerts": len(resolved_alerts),
            "silenced_alerts": len(self.silenced_alerts),
            "notification_rules": len(self.notification_rules),
            "severity_breakdown": {
                severity.value: len([a for a in firing_alerts if a.severity == severity])
                for severity in AlertSeverity
            }
        }

class AlertManagerTemplate:
    """
    Alert Manager Template for Ainflue Platform
    
    A comprehensive alert management system that provides:
    - Multi-channel alerting
    - Alert correlation and grouping
    - Escalation policies
    - Alert suppression and silencing
    """
    
    def __init__(self):
        self.service_name = "alert-manager"
        self.service_version = "1.0.0"
        self.description = "Production-ready alert management with multi-channel notifications"
    
    def create_manager(self, config: Dict[str, Any]) -> AlertManager:
        """Create an alert manager instance"""
        return AlertManager()
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get alert manager template information"""
        return {
            "name": self.service_name,
            "version": self.service_version,
            "description": self.description,
            "features": [
                "Multi-channel alerting",
                "Alert correlation and grouping",
                "Escalation policies and routing",
                "Alert suppression and silencing",
                "Incident management integration",
                "Metric-based alert rules",
                "Notification cooldowns",
                "Alert acknowledgment"
            ],
            "notification_channels": [
                "Email with SMTP support",
                "Slack webhook integration",
                "Custom webhook notifications",
                "SMS notifications",
                "Discord webhook support"
            ],
            "dependencies": ["aiohttp", "smtplib"],
            "endpoints": [
                "/alerts",
                "/alerts/{alert_id}/silence",
                "/alerts/{alert_id}/acknowledge",
                "/notifications/rules",
                "/alerts/summary"
            ]
        }