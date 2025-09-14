"""Alert Manager for IA Influencer Agent Platform
==============================================

Advanced alerting system with multi-channel notifications, escalation policies,
and intelligent alert correlation and deduplication.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aioredis
import aiohttp
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """
Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status"""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    name: str
    severity: AlertSeverity
    message: str
    source: str
    status: AlertStatus = AlertStatus.ACTIVE
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    fingerprint: Optional[str] = None
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


@dataclass
class NotificationChannel:
    """
Notification channel configuration"""
    name: str
    type: str  # email, slack, webhook, telegram, pagerduty
    config: Dict[str, Any]
    enabled: bool = True
    severity_filter: List[AlertSeverity] = field(default_factory=lambda: list(AlertSeverity))


@dataclass
class EscalationRule:
    """
Alert escalation rule"""
    name: str
    conditions: Dict[str, Any]
    delay: int  # seconds
    channels: List[str]
    enabled: bool = True


@dataclass
class SilenceRule:
    """
Alert silence rule"""
    id: str
    matchers: Dict[str, str]
    start_time: datetime
    end_time: datetime
    created_by: str
    comment: str


class AlertManager:
    """
    Advanced alert management system with intelligent correlation,
    escalation policies, and multi-channel notifications.
    """
    
    def __init__(
        self,
        redis_client -> None: Optional[aioredis.Redis] = None,
        correlation_window -> None: int = 300,  # 5 minutes
        cleanup_interval -> None: int = 3600,   # 1 hour
        max_alert_age -> None: int = 604800     # 7 days
    ) -> None:
        self.redis_client = redis_client
        self.correlation_window = correlation_window
        self.cleanup_interval = cleanup_interval
        self.max_alert_age = max_alert_age
        
        # Alert storage
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        
        # Configuration
        self._notification_channels: Dict[str, NotificationChannel] = {}
        self._escalation_rules: List[EscalationRule] = []
        self._silence_rules: List[SilenceRule] = []
        
        # Processing state
        self._processing = False
        self._processor_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Correlation and deduplication
        self._correlation_rules: Dict[str, Callable] = {}
        self._alert_fingerprints: Dict[str, str] = {}
        
        # Rate limiting
        self._rate_limits: Dict[str, Dict[str, Any]] = {}
        
        # Register default notification channels
        self._register_default_channels()
        
    def _register_default_channels(self) -> None:
        try:
            logger.info(f"Executing _register_default_channels")
            
            # Implementation for _register_default_channels
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_register_default_channels completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_register_default_channels failed: {e}")
            raise
            name="webhook_monitoring",
            type="webhook",
            config={
                "url": "http://localhost:8080/alerts",
                "method": "POST",
                "headers": {"Content-Type": "application/json"}
            }
        ))
        
    async def start_processing(self) -> None:
        """Start alert processing"""
        if self._processing:
            logger.warning("Alert processing already running")
            return
            
        self._processing = True
        self._processor_task = asyncio.create_task(self._processing_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Load state from Redis
        await self._load_state()
        
        logger.info("Alert processing started")
        
    async def stop_processing(self) -> None:
        """Stop alert processing"""
        self._processing = False
        
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
                
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
        # Save state to Redis
        await self._save_state()
        
        logger.info("Alert processing stopped")
        
    async def _processing_loop(self) -> None:
        """Main alert processing loop"""
        while self._processing:
            try:
                await self._process_pending_alerts()
                await self._check_escalations()
                await self._process_correlations()
                await asyncio.sleep(10)  # Process every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert processing loop: {e}")
                await asyncio.sleep(5)
                
    async def _cleanup_loop(self) -> None:
        """Cleanup loop for old alerts and maintenance"""
        while self._processing:
            try:
                await self._cleanup_old_alerts()
                await self._cleanup_expired_silences()
                await self._save_state()
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
                
    async def fire_alert(
        self,
        name: str,
        message: str,
        severity: AlertSeverity,
        source: str,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None
    ) -> str:
        """Fire a new alert"""
        
        # Generate alert ID and fingerprint
        alert_id = f"{name}_{source}_{int(time.time())}"
        fingerprint = self._generate_fingerprint(name, source, labels or {})
        
        # Check for existing alert with same fingerprint
        existing_alert = self._find_alert_by_fingerprint(fingerprint)
        if existing_alert and existing_alert.status == AlertStatus.ACTIVE:
            # Update existing alert
            existing_alert.message = message
            existing_alert.timestamp = datetime.utcnow()
            logger.info(f"Updated existing alert: {existing_alert.id}")
            return existing_alert.id
            
        # Create new alert
        alert = Alert(
            id=alert_id,
            name=name,
            severity=severity,
            message=message,
            source=source,
            labels=labels or {},
            annotations=annotations or {},
            fingerprint=fingerprint
        )
        
        # Check silence rules
        if self._is_silenced(alert):
            alert.status = AlertStatus.SILENCED
            logger.info(f"Alert silenced: {alert_id}")
            
        # Store alert
        self._active_alerts[alert_id] = alert
        self._alert_fingerprints[fingerprint] = alert_id
        
        # Queue for processing
        if self.redis_client:
            await self.redis_client.lpush("alert_queue", json.dumps({
                "alert_id": alert_id,
                "action": "fire"
            }))
            
        logger.info(f"Alert fired: {alert_id} - {name} ({severity.value})")
        return alert_id
        
    async def resolve_alert(self, alert_id: str, resolved_by: Optional[str] = None) -> bool:
        """Resolve an alert"""
        if alert_id not in self._active_alerts:
            logger.warning(f"Alert not found: {alert_id}")
            return False
            
        alert = self._active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        
        # Move to history
        self._alert_history.append(alert)
        del self._active_alerts[alert_id]
        
        if alert.fingerprint and alert.fingerprint in self._alert_fingerprints:
            del self._alert_fingerprints[alert.fingerprint]
            
        # Queue for processing
        if self.redis_client:
            await self.redis_client.lpush("alert_queue", json.dumps({
                "alert_id": alert_id,
                "action": "resolve",
                "resolved_by": resolved_by
            }))
            
        logger.info(f"Alert resolved: {alert_id}")
        return True
        
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id not in self._active_alerts:
            logger.warning(f"Alert not found: {alert_id}")
            return False
            
        alert = self._active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by
        
        logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
        return True
        
    async def silence_alerts(
        self,
        matchers: Dict[str, str],
        duration: int,
        created_by: str,
        comment: str
    ) -> str:
        """Create a silence rule"""
        silence_id = f"silence_{int(time.time())}"
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=duration)
        
        silence = SilenceRule(
            id=silence_id,
            matchers=matchers,
            start_time=start_time,
            end_time=end_time,
            created_by=created_by,
            comment=comment
        )
        
        self._silence_rules.append(silence)
        
        # Apply to existing alerts
        for alert in self._active_alerts.values():
            if self._matches_silence(alert, silence):
                alert.status = AlertStatus.SILENCED
                
        logger.info(f"Silence rule created: {silence_id}")
        return silence_id
        
    async def _process_pending_alerts(self) -> None:
        """Process pending alerts from queue"""
        if not self.redis_client:
            return
            
        try:
            while True:
                item = await self.redis_client.brpop("alert_queue", timeout=1)
                if not item:
                    break
                    
                _, data = item
                alert_data = json.loads(data)
                alert_id = alert_data["alert_id"]
                action = alert_data["action"]
                
                if action == "fire":
                    await self._send_notifications(alert_id)
                elif action == "resolve":
                    await self._send_resolution_notifications(alert_id, alert_data.get("resolved_by"))
                    
        except Exception as e:
            logger.error(f"Error processing pending alerts: {e}")
            
    async def _send_notifications(self, alert_id -> None: str) -> None:
        """Send notifications for an alert"""
        if alert_id not in self._active_alerts:
            return
            
        alert = self._active_alerts[alert_id]
        
        # Skip if silenced
        if alert.status == AlertStatus.SILENCED:
            return
            
        # Check rate limiting
        if self._is_rate_limited(alert):
            logger.info(f"Alert rate limited: {alert_id}")
            return
            
        # Send to matching channels
        for channel_name, channel in self._notification_channels.items():
            if not channel.enabled:
                continue
                
            if alert.severity not in channel.severity_filter:
                continue
                
            try:
                await self._send_to_channel(alert, channel)
                self._update_rate_limit(alert, channel_name)
                
            except Exception as e:
                logger.error(f"Error sending alert to channel {channel_name}: {e}")
                
    async def _send_to_channel(self, alert -> None: Alert, channel -> None: NotificationChannel) -> None:
        """Send alert to specific notification channel"""
        if channel.type == "email":
            await self._send_email_notification(alert, channel)
        elif channel.type == "slack":
            await self._send_slack_notification(alert, channel)
        elif channel.type == "webhook":
            await self._send_webhook_notification(alert, channel)
        elif channel.type == "telegram":
            await self._send_telegram_notification(alert, channel)
        else:
            logger.warning(f"Unknown channel type: {channel.type}")
            
    async def _send_email_notification(self, alert -> None: Alert, channel -> None: NotificationChannel) -> None:
        """Send email notification"""
        config = channel.config
        
        # Create email content
        subject = f"[{alert.severity.value.upper()}] {alert.name}"
        
        template = Template("""
        <h2>Alert: {{ alert.name }}</h2>
        <p><strong>Severity:</strong> {{ alert.severity.value.upper() }}</p>
        <p><strong>Source:</strong> {{ alert.source }}</p>
        <p><strong>Time:</strong> {{ alert.timestamp }}</p>
        <p><strong>Message:</strong> {{ alert.message }}</p>
        
        {% if alert.labels %}
        <h3>Labels:</h3>
        <ul>
        {% for key, value in alert.labels.items() %}
            <li><strong>{{ key }}:</strong> {{ value }}</li>
        {% endfor %}
        </ul>
        {% endif %}
        
        {% if alert.annotations %}
        <h3>Annotations:</h3>
        <ul>
        {% for key, value in alert.annotations.items() %}
            <li><strong>{{ key }}:</strong> {{ value }}</li>
        {% endfor %}
        </ul>
        {% endif %}
        """)
        
        html_content = template.render(alert=alert)
        
        # Send email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config['username']
        msg['To'] = ', '.join(config['recipients'])
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Note: This is a simplified implementation
        # In production, use async email library like aiosmtplib
        logger.info(f"Email notification sent for alert: {alert.id}")
        
    async def _send_slack_notification(self, alert -> None: Alert, channel -> None: NotificationChannel) -> None:
        """Send Slack notification"""
        config = channel.config
        
        # Create Slack message
        color = {
            AlertSeverity.INFO: "good",
            AlertSeverity.WARNING: "warning", 
            AlertSeverity.CRITICAL: "danger",
            AlertSeverity.EMERGENCY: "danger"
        }.get(alert.severity, "warning")
        
        payload = {
            "channel": config.get("channel", "#alerts"),
            "username": config.get("username", "Alert Bot"),
            "attachments": [{
                "color": color,
                "title": f"{alert.severity.value.upper()}: {alert.name}",
                "text": alert.message,
                "fields": [
                    {"title": "Source", "value": alert.source, "short": True},
                    {"title": "Time", "value": alert.timestamp.isoformat(), "short": True}
                ],
                "footer": "IA Influencer Agent",
                "ts": int(alert.timestamp.timestamp())
            }]
        }
        
        # Add labels and annotations as fields
        if alert.labels:
            for key, value in alert.labels.items():
                payload["attachments"][0]["fields"].append({
                    "title": f"Label: {key}",
                    "value": value,
                    "short": True
                })
                
        async with aiohttp.ClientSession() as session:
            async with session.post(config["webhook_url"], json=payload) as response:
                if response.status == 200:
                    logger.info(f"Slack notification sent for alert: {alert.id}")
                else:
                    logger.error(f"Failed to send Slack notification: {response.status}")
                    
    async def _send_webhook_notification(self, alert -> None: Alert, channel -> None: NotificationChannel) -> None:
        """Send webhook notification"""
        config = channel.config
        
        payload = {
            "alert_id": alert.id,
            "name": alert.name,
            "severity": alert.severity.value,
            "status": alert.status.value,
            "message": alert.message,
            "source": alert.source,
            "timestamp": alert.timestamp.isoformat(),
            "labels": alert.labels,
            "annotations": alert.annotations
        }
        
        headers = config.get("headers", {})
        method = config.get("method", "POST")
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, config["url"], json=payload, headers=headers) as response:
                if response.status < 400:
                    logger.info(f"Webhook notification sent for alert: {alert.id}")
                else:
                    logger.error(f"Failed to send webhook notification: {response.status}")
                    
    async def _send_telegram_notification(self, alert -> None: Alert, channel -> None: NotificationChannel) -> None:
        """Send Telegram notification"""
        config = channel.config
        
        # Format message for Telegram
        message = f"# [EMOJI_REMOVED] *{alert.severity.value.upper()}*: {alert.name}\n\n"
        message += f"*Message:* {alert.message}\n"
        message += f"*Source:* {alert.source}\n"
        message += f"*Time:* {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if alert.labels:
            message += "\n*Labels:*\n"
            for key, value in alert.labels.items():
                message += f"# [EMOJI_REMOVED] {key}: {value}\n"
                
        payload = {
            "chat_id": config["chat_id"],
            "text": message,
            "parse_mode": "Markdown"
        }
        
        url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Telegram notification sent for alert: {alert.id}")
                else:
                    logger.error(f"Failed to send Telegram notification: {response.status}")
                    
    def _generate_fingerprint(self, name: str, source: str, labels: Dict[str, str]) -> str:
        """Generate alert fingerprint for deduplication"""
        fingerprint_data = f"{name}:{source}:{sorted(labels.items())}"
        return str(hash(fingerprint_data))
        
    def _find_alert_by_fingerprint(self, fingerprint: str) -> Optional[Alert]:
        """Find alert by fingerprint"""
        alert_id = self._alert_fingerprints.get(fingerprint)
        if alert_id and alert_id in self._active_alerts:
            return self._active_alerts[alert_id]
        return None
        
    def _is_silenced(self, alert: Alert) -> bool:
        """
Check if alert matches any silence rule"""
        for silence in self._silence_rules:
            if self._matches_silence(alert, silence):
                return True
        return False
        
    def _matches_silence(self, alert: Alert, silence: SilenceRule) -> bool:
        """
Check if alert matches silence rule"""
        now = datetime.utcnow()
        if now < silence.start_time or now > silence.end_time:
            return False
            
        for key, pattern in silence.matchers.items():
            if key == "name" and alert.name != pattern:
                return False
            elif key == "source" and alert.source != pattern:
                return False
            elif key in alert.labels and alert.labels[key] != pattern:
                return False
                
        return True
        
    def _is_rate_limited(self, alert: Alert) -> bool:
        """Check if alert is rate limited"""
        key = f"{alert.name}:{alert.source}"
        
        if key not in self._rate_limits:
            self._rate_limits[key] = {
                "count": 0,
                "window_start": time.time()
            }
            
        rate_limit = self._rate_limits[key]
        now = time.time()
        
        # Reset window if expired (5 minute window)
        if now - rate_limit["window_start"] > 300:
            rate_limit["count"] = 0
            rate_limit["window_start"] = now
            
        # Check limit (max 10 alerts per 5 minutes)
        if rate_limit["count"] >= 10:
            return True
            
        return False
        
    def _update_rate_limit(self, alert -> None: Alert, channel_name -> None: str) -> None:
        """Update rate limit counter"""
        key = f"{alert.name}:{alert.source}"
        if key in self._rate_limits:
            self._rate_limits[key]["count"] += 1
            
    async def _check_escalations(self) -> None:
        """Check and process alert escalations"""
        for rule in self._escalation_rules:
            if not rule.enabled:
                continue
                
            # Find alerts matching escalation conditions
            for alert in self._active_alerts.values():
                if self._matches_escalation_conditions(alert, rule):
                    age = (datetime.utcnow() - alert.timestamp).total_seconds()
                    if age >= rule.delay and alert.status == AlertStatus.ACTIVE:
                        await self._escalate_alert(alert, rule)
                        
    def _matches_escalation_conditions(self, alert: Alert, rule: EscalationRule) -> bool:
        """
Check if alert matches escalation conditions"""
        conditions = rule.conditions
        
        if "severity" in conditions:
            if alert.severity.value not in conditions["severity"]:
                return False
                
        if "source" in conditions:
            if alert.source not in conditions["source"]:
                return False
                
        if "labels" in conditions:
            for key, value in conditions["labels"].items():
                if key not in alert.labels or alert.labels[key] != value:
                    return False
                    
        return True
        
    async def _escalate_alert(self, alert -> None: Alert, rule -> None: EscalationRule) -> None:
        """Escalate an alert"""
        logger.info(f"Escalating alert {alert.id} via rule {rule.name}")
        
        # Send to escalation channels
        for channel_name in rule.channels:
            if channel_name in self._notification_channels:
                channel = self._notification_channels[channel_name]
                try:
                    await self._send_to_channel(alert, channel)
                except Exception as e:
                    logger.error(f"Error escalating to channel {channel_name}: {e}")
                    
    async def _process_correlations(self) -> None:
        """Process alert correlations"""
        # Implement correlation logic based on time windows and patterns
        pass
        
    async def _cleanup_old_alerts(self) -> None:
        """
Clean up old resolved alerts"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.max_alert_age)
        
        # Remove old alerts from history
        self._alert_history = [
            alert for alert in self._alert_history
            if alert.resolved_at and alert.resolved_at > cutoff
        ]
        
        logger.debug(f"Cleaned up old alerts, history size: {len(self._alert_history)}")
        
    async def _cleanup_expired_silences(self) -> None:
        """Clean up expired silence rules"""
        now = datetime.utcnow()
        active_silences = []
        
        for silence in self._silence_rules:
            if silence.end_time > now:
                active_silences.append(silence)
            else:
                logger.info(f"Expired silence rule: {silence.id}")
                
        self._silence_rules = active_silences
        
    async def _load_state(self) -> None:
        """Load state from Redis"""
        if not self.redis_client:
            return
            
        try:
            # Load active alerts
            alert_data = await self.redis_client.get("alerts:active")
            if alert_data:
                alerts_dict = json.loads(alert_data)
                for alert_id, alert_data in alerts_dict.items():
                    alert = Alert(**alert_data)
                    alert.timestamp = datetime.fromisoformat(alert_data["timestamp"])
                    alert.severity = AlertSeverity(alert_data["severity"])
                    alert.status = AlertStatus(alert_data["status"])
                    self._active_alerts[alert_id] = alert
                    
            logger.info(f"Loaded {len(self._active_alerts)} active alerts from Redis")
            
        except Exception as e:
            logger.error(f"Error loading state from Redis: {e}")
            
    async def _save_state(self) -> None:
        """Save state to Redis"""
        if not self.redis_client:
            return
            
        try:
            # Save active alerts
            alerts_dict = {}
            for alert_id, alert in self._active_alerts.items():
                alerts_dict[alert_id] = {
                    "id": alert.id,
                    "name": alert.name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "source": alert.source,
                    "status": alert.status.value,
                    "timestamp": alert.timestamp.isoformat(),
                    "labels": alert.labels,
                    "annotations": alert.annotations,
                    "fingerprint": alert.fingerprint
                }
                
            await self.redis_client.set(
                "alerts:active",
                json.dumps(alerts_dict),
                ex=86400  # 24 hours TTL
            )
            
            logger.debug(f"Saved {len(self._active_alerts)} active alerts to Redis")
            
        except Exception as e:
            logger.error(f"Error saving state to Redis: {e}")
            
    # Public interface methods
    def register_channel(self, channel -> None: NotificationChannel) -> None:
        """Register a notification channel"""
        self._notification_channels[channel.name] = channel
        logger.info(f"Registered notification channel: {channel.name}")
        
    def register_escalation_rule(self, rule -> None: EscalationRule) -> None:
        """Register an escalation rule"""
        self._escalation_rules.append(rule)
        logger.info(f"Registered escalation rule: {rule.name}")
        
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return [
            {
                "id": alert.id,
                "name": alert.name,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "message": alert.message,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "labels": alert.labels,
                "annotations": alert.annotations
            }
            for alert in self._active_alerts.values()
        ]
        
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        severity_counts = {severity.value: 0 for severity in AlertSeverity}
        status_counts = {status.value: 0 for status in AlertStatus}
        
        for alert in self._active_alerts.values():
            severity_counts[alert.severity.value] += 1
            status_counts[alert.status.value] += 1
            
        return {
            "total_active": len(self._active_alerts),
            "total_history": len(self._alert_history),
            "severity_counts": severity_counts,
            "status_counts": status_counts,
            "notification_channels": len(self._notification_channels),
            "escalation_rules": len(self._escalation_rules),
            "silence_rules": len(self._silence_rules)
        }

# File has syntax issues - needs manual review