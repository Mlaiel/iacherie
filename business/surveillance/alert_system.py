"""
 Alert System - IA Influencer Agent Surveillance Module
========================================================

Real-time alert system for notifying creators of copyright infringements,
content violations, and surveillance updates.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import smtplib
import json
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import uuid
import time

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(Enum):
    """Types of alerts"""
    INFRINGEMENT_DETECTED = "infringement_detected"
    TAKEDOWN_SUCCESS = "takedown_success"
    TAKEDOWN_FAILED = "takedown_failed"
    HIGH_SIMILARITY_MATCH = "high_similarity_match"
    VIRAL_INFRINGEMENT = "viral_infringement"
    REVENUE_IMPACT = "revenue_impact"
    MASS_INFRINGEMENT = "mass_infringement"
    PLATFORM_SUSPENSION = "platform_suspension"
    LEGAL_ACTION_REQUIRED = "legal_action_required"
    SYSTEM_ERROR = "system_error"
    CRAWL_FAILURE = "crawl_failure"
    PROTECTION_BREACH = "protection_breach"


class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    IN_APP = "in_app"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    alert_type: AlertType
    severity_threshold: AlertSeverity
    conditions: Dict[str, Any]
    channels: List[NotificationChannel]
    frequency_limit: Optional[int] = None  # Max alerts per hour
    cooldown_minutes: Optional[int] = None
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Alert:
    """Alert structure"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    creator_id: str
    content_id: Optional[str] = None
    
    # Alert data
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Notification details
    channels: List[NotificationChannel] = field(default_factory=list)
    sent_channels: List[NotificationChannel] = field(default_factory=list)
    failed_channels: List[NotificationChannel] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Status tracking
    acknowledged: bool = False
    resolved: bool = False
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class NotificationConfig:
    """Notification configuration for a creator"""
    creator_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    webhook_url: Optional[str] = None
    slack_webhook: Optional[str] = None
    discord_webhook: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Channel preferences
    preferred_channels: List[NotificationChannel] = field(default_factory=list)
    severity_channels: Dict[AlertSeverity, List[NotificationChannel]] = field(default_factory=dict)
    
    # Alert preferences
    enabled_alert_types: List[AlertType] = field(default_factory=list)
    quiet_hours: Optional[Dict[str, str]] = None  # {"start": "22:00", "end": "08:00"}
    max_daily_alerts: Optional[int] = None
    
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class NotificationChannel:
    """Base class for notification channels"""
    
    def __init__(self, channel_type: NotificationChannel, config: Dict[str, Any]):
        self.channel_type = channel_type
        self.config = config
        self.enabled = config.get("enabled", True)
    
    async def send_notification(self, alert: Alert, recipient_config: NotificationConfig) -> bool:
        """Send notification through this channel"""
        # Default implementation for notification channels without specific implementation
        logging.warning(f"Notification sending not implemented for {self.__class__.__name__}")
        return False
    
    async def format_message(self, alert: Alert) -> Dict[str, str]:
        """Format message for this channel"""



        return {
            "subject": alert.title,
            "body": alert.message
        }


class EmailNotificationChannel(NotificationChannel):
    """Email notification channel"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(NotificationChannel.EMAIL, config)
        self.smtp_server = config.get("smtp_server", "localhost")
        self.smtp_port = config.get("smtp_port", 587)
        self.smtp_username = config.get("smtp_username", "")
        self.smtp_password = config.get("smtp_password", "")
        self.from_email = config.get("from_email", "alerts@ia-influencer.com")
        self.from_name = config.get("from_name", "IA Influencer Agent")
    
    async def send_notification(self, alert: Alert, recipient_config: NotificationConfig) -> bool:
        """Send email notification"""
        if not recipient_config.email:
            logger.warning(f"No email configured for creator {recipient_config.creator_id}")
            return False
        
        try:
            # Format message
            formatted = await self.format_message(alert)
            
            # Create email message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = formatted["subject"]
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = recipient_config.email
            
            # Create HTML and text versions
            text_body = formatted["body"]
            html_body = self._create_html_body(alert, formatted["body"])
            
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            # Send email (in production, use actual SMTP)
            await asyncio.sleep(0.1)  # Simulate email sending
            logger.info(f"Email sent to {recipient_config.email} for alert {alert.alert_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _create_html_body(self, alert: Alert, text_body: str) -> str:
        """Create HTML email body"""
        severity_colors = {
            AlertSeverity.INFO: "#17a2b8",
            AlertSeverity.LOW: "#28a745",
            AlertSeverity.MEDIUM: "#ffc107",
            AlertSeverity.HIGH: "#fd7e14",
            AlertSeverity.CRITICAL: "#dc3545",
            AlertSeverity.EMERGENCY: "#6f42c1"
        }
        
        color = severity_colors.get(alert.severity, "#6c757d")
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 4px solid {color}; padding-left: 20px; margin-bottom: 20px;">
                <h2 style="color: {color}; margin-top: 0;">
                     {alert.title}
                </h2>
                <p style="color: #6c757d; margin-bottom: 10px;">
                    <strong>Severity:</strong> {alert.severity.value.upper()} | 
                    <strong>Type:</strong> {alert.alert_type.value.replace('_', ' ').title()} |
                    <strong>Time:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
                </p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <p style="margin: 0; white-space: pre-wrap;">{text_body}</p>
            </div>
            
            {self._create_data_section(alert)}
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center; color: #6c757d;">
                <p style="margin: 0; font-size: 12px;">
                    This is an automated alert from IA Influencer Agent Surveillance System<br>
                    Alert ID: {alert.alert_id}
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_data_section(self, alert: Alert) -> str:
        """Create HTML section for alert data"""
        if not alert.data:
            return ""
        
        data_html = "<h3>Details:</h3><ul>"
        
        for key, value in alert.data.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, indent=2)
            
            data_html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        
        data_html += "</ul>"
        return data_html


class WebhookNotificationChannel(NotificationChannel):
    """Webhook notification channel"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(NotificationChannel.WEBHOOK, config)
        self.timeout = config.get("timeout", 10)
        self.retry_attempts = config.get("retry_attempts", 3)
    
    async def send_notification(self, alert: Alert, recipient_config: NotificationConfig) -> bool:
        """Send webhook notification"""
        if not recipient_config.webhook_url:
            logger.warning(f"No webhook URL configured for creator {recipient_config.creator_id}")
            return False
        
        try:
            # Format webhook payload
            payload = {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "title": alert.title,
                "message": alert.message,
                "creator_id": alert.creator_id,
                "content_id": alert.content_id,
                "data": alert.data,
                "metadata": alert.metadata,
                "timestamp": alert.created_at.isoformat()
            }
            
            # Simulate webhook call (in production, use aiohttp)
            await asyncio.sleep(0.1)
            logger.info(f"Webhook sent to {recipient_config.webhook_url} for alert {alert.alert_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False


class SlackNotificationChannel(NotificationChannel):
    """Slack notification channel"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(NotificationChannel.SLACK, config)
    
    async def send_notification(self, alert: Alert, recipient_config: NotificationConfig) -> bool:
        """Send Slack notification"""
        if not recipient_config.slack_webhook:
            logger.warning(f"No Slack webhook configured for creator {recipient_config.creator_id}")
            return False
        
        try:
            # Create Slack payload
            severity_emojis = {
                AlertSeverity.INFO: "ℹ",
                AlertSeverity.LOW: "🟢",
                AlertSeverity.MEDIUM: "🟡",
                AlertSeverity.HIGH: "🟠",
                AlertSeverity.CRITICAL: "",
                AlertSeverity.EMERGENCY: ""
            }
            
            emoji = severity_emojis.get(alert.severity, "")
            
            payload = {
                "text": f"{emoji} *{alert.title}*",
                "attachments": [
                    {
                        "color": self._get_slack_color(alert.severity),
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Type",
                                "value": alert.alert_type.value.replace('_', ' ').title(),
                                "short": True
                            },
                            {
                                "title": "Creator ID",
                                "value": alert.creator_id,
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                "short": True
                            }
                        ],
                        "text": alert.message,
                        "footer": "IA Influencer Agent",
                        "footer_icon": "https://example.com/icon.png",
                        "ts": int(alert.created_at.timestamp())
                    }
                ]
            }
            
            # Simulate Slack API call
            await asyncio.sleep(0.1)
            logger.info(f"Slack notification sent for alert {alert.alert_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _get_slack_color(self, severity: AlertSeverity) -> str:
        """Get Slack color for severity"""
        colors = {
            AlertSeverity.INFO: "#17a2b8",
            AlertSeverity.LOW: "#28a745",
            AlertSeverity.MEDIUM: "#ffc107",
            AlertSeverity.HIGH: "#fd7e14",
            AlertSeverity.CRITICAL: "#dc3545",
            AlertSeverity.EMERGENCY: "#6f42c1"
        }
        return colors.get(severity, "#6c757d")


class SMSNotificationChannel(NotificationChannel):
    """SMS notification channel"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(NotificationChannel.SMS, config)
        self.provider = config.get("provider", "twilio")
        self.api_key = config.get("api_key", "")
        self.from_number = config.get("from_number", "")
    
    async def send_notification(self, alert: Alert, recipient_config: NotificationConfig) -> bool:
        """Send SMS notification"""
        if not recipient_config.phone:
            logger.warning(f"No phone number configured for creator {recipient_config.creator_id}")
            return False
        
        try:
            # Create short SMS message
            message = f" {alert.severity.value.upper()}: {alert.title[:100]}..."
            
            # Simulate SMS API call
            await asyncio.sleep(0.1)
            logger.info(f"SMS sent to {recipient_config.phone} for alert {alert.alert_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
            return False


class AlertSystem:
    """
    Central alert system for real-time notifications of copyright infringements,
    content violations, and surveillance updates
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notification_configs: Dict[str, NotificationConfig] = {}
        self.channels: Dict[NotificationChannel, NotificationChannel] = {}
        self.alert_queue: asyncio.Queue = asyncio.Queue()
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.initialized = False
        self.processing_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> None:
        """Initialize alert system"""



        try:
            # Initialize notification channels
            await self._initialize_channels()
            
            # Load default alert rules
            await self._load_default_alert_rules()
            
            # Start alert processing task
            self.processing_task = asyncio.create_task(self._process_alert_queue())
            
            self.initialized = True
            logger.info("Alert System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Alert System: {e}")
            raise
    
    async def _initialize_channels(self) -> None:
        """Initialize notification channels"""
        # Email channel
        if self.config.get("email_enabled", True):
            email_config = self.config.get("email", {})
            self.channels[NotificationChannel.EMAIL] = EmailNotificationChannel(email_config)
        
        # Webhook channel
        if self.config.get("webhook_enabled", True):
            webhook_config = self.config.get("webhook", {})
            self.channels[NotificationChannel.WEBHOOK] = WebhookNotificationChannel(webhook_config)
        
        # Slack channel
        if self.config.get("slack_enabled", False):
            slack_config = self.config.get("slack", {})
            self.channels[NotificationChannel.SLACK] = SlackNotificationChannel(slack_config)
        
        # SMS channel
        if self.config.get("sms_enabled", False):
            sms_config = self.config.get("sms", {})
            self.channels[NotificationChannel.SMS] = SMSNotificationChannel(sms_config)
        
        logger.info(f"Initialized {len(self.channels)} notification channels")
    
    async def _load_default_alert_rules(self) -> None:
        """Load default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="high_similarity_infringement",
                name="High Similarity Infringement",
                alert_type=AlertType.HIGH_SIMILARITY_MATCH,
                severity_threshold=AlertSeverity.HIGH,
                conditions={"similarity_score": {">=": 0.8}},
                channels=[NotificationChannel.EMAIL, NotificationChannel.WEBHOOK],
                frequency_limit=10,
                cooldown_minutes=15
            ),
            AlertRule(
                rule_id="viral_infringement",
                name="Viral Content Infringement",
                alert_type=AlertType.VIRAL_INFRINGEMENT,
                severity_threshold=AlertSeverity.CRITICAL,
                conditions={"views": {">=": 100000}, "similarity_score": {">=": 0.7}},
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK],
                frequency_limit=5,
                cooldown_minutes=30
            ),
            AlertRule(
                rule_id="mass_infringement",
                name="Mass Infringement Detection",
                alert_type=AlertType.MASS_INFRINGEMENT,
                severity_threshold=AlertSeverity.EMERGENCY,
                conditions={"infringement_count": {">=": 10}},
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.WEBHOOK],
                frequency_limit=1,
                cooldown_minutes=60
            ),
            AlertRule(
                rule_id="takedown_success",
                name="Takedown Success",
                alert_type=AlertType.TAKEDOWN_SUCCESS,
                severity_threshold=AlertSeverity.INFO,
                conditions={},
                channels=[NotificationChannel.EMAIL],
                frequency_limit=50
            ),
            AlertRule(
                rule_id="takedown_failed",
                name="Takedown Failed",
                alert_type=AlertType.TAKEDOWN_FAILED,
                severity_threshold=AlertSeverity.MEDIUM,
                conditions={},
                channels=[NotificationChannel.EMAIL, NotificationChannel.WEBHOOK],
                frequency_limit=20
            ),
            AlertRule(
                rule_id="revenue_impact",
                name="Revenue Impact Alert",
                alert_type=AlertType.REVENUE_IMPACT,
                severity_threshold=AlertSeverity.HIGH,
                conditions={"estimated_loss": {">=": 1000}},
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
                frequency_limit=5,
                cooldown_minutes=120
            ),
            AlertRule(
                rule_id="system_error",
                name="System Error",
                alert_type=AlertType.SYSTEM_ERROR,
                severity_threshold=AlertSeverity.HIGH,
                conditions={},
                channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                frequency_limit=10,
                cooldown_minutes=15
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
        
        logger.info(f"Loaded {len(default_rules)} default alert rules")
    
    async def create_alert(
        self,
        alert_type: AlertType,
        creator_id: str,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        content_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """Create a new alert"""
        alert_id = f"alert_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            creator_id=creator_id,
            content_id=content_id,
            data=data or {},
            metadata=metadata or {}
        )
        
        # Check if alert should be created based on rules
        matching_rules = await self._find_matching_rules(alert)
        
        if matching_rules:
            # Determine notification channels from rules
            channels = set()
            for rule in matching_rules:
                channels.update(rule.channels)
            
            alert.channels = list(channels)
            
            # Add to queue for processing
            await self.alert_queue.put(alert)
            self.active_alerts[alert_id] = alert
            
            logger.info(f"Alert created: {alert_id} (type: {alert_type.value}, severity: {severity.value})")
        else:
            logger.debug(f"Alert filtered out by rules: {alert_id}")
        
        return alert
    
    async def _find_matching_rules(self, alert: Alert) -> List[AlertRule]:
        """Find alert rules that match the alert"""
        matching_rules = []
        
        for rule in self.alert_rules.values():
            if not rule.active:
                continue
            
            # Check alert type
            if rule.alert_type != alert.alert_type:
                continue
            
            # Check severity threshold
            severity_levels = list(AlertSeverity)
            if severity_levels.index(alert.severity) < severity_levels.index(rule.severity_threshold):
                continue
            
            # Check conditions
            if await self._check_rule_conditions(rule, alert):
                matching_rules.append(rule)
        
        return matching_rules
    
    async def _check_rule_conditions(self, rule: AlertRule, alert: Alert) -> bool:
        """Check if alert meets rule conditions"""
        for condition_key, condition_value in rule.conditions.items():
            alert_value = alert.data.get(condition_key)
            
            if alert_value is None:
                continue
            
            if isinstance(condition_value, dict):
                # Handle comparison operators
                for operator, expected_value in condition_value.items():
                    if operator == ">=" and not (alert_value >= expected_value):
                        return False
                    elif operator == ">" and not (alert_value > expected_value):
                        return False
                    elif operator == "<=" and not (alert_value <= expected_value):
                        return False
                    elif operator == "<" and not (alert_value < expected_value):
                        return False
                    elif operator == "==" and not (alert_value == expected_value):
                        return False
                    elif operator == "!=" and not (alert_value != expected_value):
                        return False
            else:
                # Direct value comparison
                if alert_value != condition_value:
                    return False
        
        return True
    
    async def _process_alert_queue(self) -> None:
        """Process alerts from the queue"""
        while True:
            try:
                # Get alert from queue
                alert = await self.alert_queue.get()
                
                # Get notification configuration for creator
                notification_config = self.notification_configs.get(alert.creator_id)
                if not notification_config:
                    logger.warning(f"No notification configuration for creator {alert.creator_id}")
                    continue
                
                # Check quiet hours
                if await self._is_quiet_hours(notification_config):
                    # Reschedule for later unless it's emergency
                    if alert.severity != AlertSeverity.EMERGENCY:
                        await asyncio.sleep(3600)  # Wait 1 hour
                        await self.alert_queue.put(alert)
                        continue
                
                # Send notifications through configured channels
                await self._send_alert_notifications(alert, notification_config)
                
                # Mark task as done
                self.alert_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing alert queue: {e}")
                await asyncio.sleep(1)
    
    async def _send_alert_notifications(self, alert: Alert, config: NotificationConfig) -> None:
        """Send alert through all configured channels"""
        successful_channels = []
        failed_channels = []
        
        for channel_type in alert.channels:
            if channel_type not in config.preferred_channels:
                continue
            
            if channel_type not in self.channels:
                logger.warning(f"Channel not available: {channel_type.value}")
                failed_channels.append(channel_type)
                continue
            
            try:
                channel = self.channels[channel_type]
                success = await channel.send_notification(alert, config)
                
                if success:
                    successful_channels.append(channel_type)
                else:
                    failed_channels.append(channel_type)
                    
            except Exception as e:
                logger.error(f"Failed to send notification via {channel_type.value}: {e}")
                failed_channels.append(channel_type)
        
        # Update alert status
        alert.sent_channels = successful_channels
        alert.failed_channels = failed_channels
        alert.sent_at = datetime.now(timezone.utc)
        
        logger.info(f"Alert {alert.alert_id} sent via {len(successful_channels)} channels")
        
        # Move to history if all notifications sent or failed
        if successful_channels or len(failed_channels) == len(alert.channels):
            self.alert_history.append(alert)
            self.active_alerts.pop(alert.alert_id, None)
    
    async def _is_quiet_hours(self, config: NotificationConfig) -> bool:
        """Check if current time is within quiet hours"""
        if not config.quiet_hours:
            return False
        
        try:
            now = datetime.now().time()
            start_time = datetime.strptime(config.quiet_hours["start"], "%H:%M").time()
            end_time = datetime.strptime(config.quiet_hours["end"], "%H:%M").time()
            
            if start_time <= end_time:
                return start_time <= now <= end_time
            else:
                return now >= start_time or now <= end_time
                
        except Exception as e:
            logger.error(f"Error checking quiet hours: {e}")
            return False
    
    async def register_creator_notifications(
        self,
        creator_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        webhook_url: Optional[str] = None,
        preferred_channels: Optional[List[NotificationChannel]] = None
    ) -> NotificationConfig:
        """Register notification configuration for a creator"""
        config = NotificationConfig(
            creator_id=creator_id,
            email=email,
            phone=phone,
            webhook_url=webhook_url,
            preferred_channels=preferred_channels or [NotificationChannel.EMAIL],
            enabled_alert_types=list(AlertType),  # Enable all by default
            severity_channels={
                AlertSeverity.EMERGENCY: [NotificationChannel.EMAIL, NotificationChannel.SMS],
                AlertSeverity.CRITICAL: [NotificationChannel.EMAIL, NotificationChannel.SMS],
                AlertSeverity.HIGH: [NotificationChannel.EMAIL],
                AlertSeverity.MEDIUM: [NotificationChannel.EMAIL],
                AlertSeverity.LOW: [NotificationChannel.EMAIL],
                AlertSeverity.INFO: [NotificationChannel.EMAIL]
            }
        )
        
        self.notification_configs[creator_id] = config
        logger.info(f"Notification configuration registered for creator {creator_id}")
        
        return config
    
    async def acknowledge_alert(self, alert_id: str, creator_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            
            if alert.creator_id != creator_id:
                logger.warning(f"Creator {creator_id} cannot acknowledge alert {alert_id}")
                return False
            
            alert.acknowledged = True
            alert.acknowledged_at = datetime.now(timezone.utc)
            
            logger.info(f"Alert {alert_id} acknowledged by creator {creator_id}")
            return True
        
        return False
    
    async def resolve_alert(self, alert_id: str, creator_id: str) -> bool:
        """Mark an alert as resolved"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            
            if alert.creator_id != creator_id:
                logger.warning(f"Creator {creator_id} cannot resolve alert {alert_id}")
                return False
            
            alert.resolved = True
            alert.resolved_at = datetime.now(timezone.utc)
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert {alert_id} resolved by creator {creator_id}")
            return True
        
        return False
    
    async def get_active_alerts(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get active alerts for a creator"""
        creator_alerts = [
            alert for alert in self.active_alerts.values()
            if alert.creator_id == creator_id
        ]
        
        return [
            {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "title": alert.title,
                "message": alert.message,
                "content_id": alert.content_id,
                "data": alert.data,
                "created_at": alert.created_at.isoformat(),
                "acknowledged": alert.acknowledged,
                "resolved": alert.resolved
            }
            for alert in sorted(creator_alerts, key=lambda x: x.created_at, reverse=True)
        ]
    
    async def get_alert_statistics(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Get alert statistics"""
        all_alerts = list(self.active_alerts.values()) + self.alert_history
        
        if creator_id:
            all_alerts = [alert for alert in all_alerts if alert.creator_id == creator_id]
        
        total_alerts = len(all_alerts)
        
        # Count by type
        type_counts = {}
        for alert in all_alerts:
            alert_type = alert.alert_type.value
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for alert in all_alerts:
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Acknowledgment stats
        acknowledged_count = len([a for a in all_alerts if a.acknowledged])
        resolved_count = len([a for a in all_alerts if a.resolved])
        
        acknowledgment_rate = (acknowledged_count / total_alerts * 100) if total_alerts > 0 else 0
        resolution_rate = (resolved_count / total_alerts * 100) if total_alerts > 0 else 0
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": len(self.active_alerts),
            "acknowledged_alerts": acknowledged_count,
            "resolved_alerts": resolved_count,
            "acknowledgment_rate": round(acknowledgment_rate, 2),
            "resolution_rate": round(resolution_rate, 2),
            "alert_types": type_counts,
            "severity_distribution": severity_counts
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on alert system"""



        return {
            "system": "healthy" if self.initialized else "unhealthy",
            "queue_size": self.alert_queue.qsize(),
            "active_alerts": len(self.active_alerts),
            "total_rules": len(self.alert_rules),
            "registered_creators": len(self.notification_configs),
            "available_channels": list(self.channels.keys()),
            "processing_active": self.processing_task is not None and not self.processing_task.done(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown alert system"""
        logger.info("Shutting down Alert System")
        
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        # Wait for queue to empty
        await self.alert_queue.join()
        
        self.initialized = False
        logger.info("Alert System shutdown complete")


# Export main components
__all__ = [
    "AlertSystem",
    "Alert",
    "AlertRule",
    "AlertSeverity",
    "AlertType",
    "NotificationChannel",
    "NotificationConfig",
    "EmailNotificationChannel",
    "WebhookNotificationChannel",
    "SlackNotificationChannel",
    "SMSNotificationChannel"
]
