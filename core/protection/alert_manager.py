"""Alert Management System for Content Protection

This module provides comprehensive alerting capabilities for the protection system:
- Real-time violation alerts via multiple channels
- Configurable alert thresholds and escalation rules
- Multi-channel notifications (email, webhook, SMS, push)
- Alert aggregation and deduplication
- Priority-based alert routing and escalation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
from pathlib import Path
import hashlib
import aiohttp
import ssl

# Template engine
from jinja2 import Environment, FileSystemLoader

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, ViolationAlert
from ...config.settings import get_settings
from .violation_detector import ViolationEvidence, ViolationType, ViolationSeverity

logger = get_logger(__name__)
settings = get_settings()


class AlertChannel(Enum):
    """Available alert channels"""    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    IN_APP = "in_app"


class AlertPriority(Enum):
    """Alert priority levels"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(Enum):
    """Alert status"""    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class AlertConfiguration:
    """Configuration for alert rules"""    name: str
    enabled: bool = True
    channels: List[AlertChannel] = field(default_factory=list)
    
    # Trigger conditions
    violation_types: List[ViolationType] = field(default_factory=list)
    severity_threshold: ViolationSeverity = ViolationSeverity.MEDIUM
    similarity_threshold: float = 0.75
    
    # Rate limiting
    max_alerts_per_hour: int = 50
    max_alerts_per_day: int = 200
    cooldown_minutes: int = 15
    
    # Escalation
    escalation_delay_minutes: int = 60
    escalation_channels: List[AlertChannel] = field(default_factory=list)
    
    # Content filtering
    content_types: List[str] = field(default_factory=list)
    platform_filters: List[str] = field(default_factory=list)


@dataclass
class Alert:
    """Represents an alert to be sent"""    alert_id: str
    violation_evidence: ViolationEvidence
    alert_type: str
    priority: AlertPriority
    channels: List[AlertChannel]
    
    # Content
    title: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    
    # Metadata
    status: AlertStatus = AlertStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Delivery tracking
    delivery_attempts: int = 0
    delivery_status: Dict[str, str] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)


@dataclass
class NotificationTemplate:
    """Template for notifications"""    name: str
    channel: AlertChannel
    subject_template: str
    body_template: str
    html_template: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)


class EmailNotifier:
    """Email notification handler"""    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        
        # Template environment
        template_dir = Path(__file__).parent / "templates"
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
    
    async def send_email_alert(self, alert: Alert, recipients: List[str]) -> bool:
        """Send email alert"""        try:
            # Load template
            template = self.template_env.get_template("violation_alert_email.html")
            
            # Render content
            template_vars = {
                'alert': alert,
                'violation': alert.violation_evidence,
                'timestamp': alert.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                'priority': alert.priority.value.upper(),
                'severity': alert.violation_evidence.severity.value.upper(),
                'violation_type': alert.violation_evidence.violation_type.value.replace('_', ' ').title(),
                'detected_url': alert.violation_evidence.detected_url,
                'similarity_scores': alert.violation_evidence.similarity_scores
            }
            
            html_content = template.render(**template_vars)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = alert.title
            msg['From'] = self.from_email
            msg['To'] = ', '.join(recipients)
            
            # Add text and HTML parts
            text_part = MIMEText(alert.message, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Add attachments (screenshots, evidence)
            for attachment_path in alert.attachments:
                if Path(attachment_path).exists():
                    with open(attachment_path, 'rb') as f:
                        attachment = MIMEBase('application', 'octet-stream')
                        attachment.set_payload(f.read())
                        encoders.encode_base64(attachment)
                        attachment.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {Path(attachment_path).name}'
                        )
                        msg.attach(attachment)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False


class WebhookNotifier:
    """Webhook notification handler"""    
    async def send_webhook_alert(self, alert: Alert, webhook_urls: List[str]) -> bool:
        """Send webhook alert"""        try:
            # Prepare payload
            payload = {
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'priority': alert.priority.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.created_at.isoformat(),
                'violation': {
                    'violation_id': alert.violation_evidence.violation_id,
                    'detected_url': alert.violation_evidence.detected_url,
                    'violation_type': alert.violation_evidence.violation_type.value,
                    'severity': alert.violation_evidence.severity.value,
                    'similarity_scores': [
                        {
                            'type': score.fingerprint_type.value,
                            'similarity': score.similarity_score,
                            'confidence': score.confidence
                        }
                        for score in alert.violation_evidence.similarity_scores
                    ]
                },
                'details': alert.details
            }
            
            success_count = 0
            
            async with aiohttp.ClientSession() as session:
                for webhook_url in webhook_urls:
                    try:
                        async with session.post(
                            webhook_url,
                            json=payload,
                            headers={'Content-Type': 'application/json'},
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            if response.status < 400:
                                success_count += 1
                                logger.debug(f"Webhook alert sent to {webhook_url}")
                            else:
                                logger.warning(f"Webhook failed: {webhook_url}, status: {response.status}")
                    
                    except Exception as e:
                        logger.error(f"Error sending webhook to {webhook_url}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error in webhook notification: {e}")
            return False


class SlackNotifier:
    """Slack notification handler"""    
    def __init__(self):
        self.webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)
    
    async def send_slack_alert(self, alert: Alert) -> bool:
        """Send Slack alert"""        try:
            if not self.webhook_url:
                logger.warning("Slack webhook URL not configured")
                return False
            
            # Create Slack message blocks
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 {alert.title}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Priority:* {alert.priority.value.upper()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Violation Type:* {alert.violation_evidence.violation_type.value.replace('_', ' ').title()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:* {alert.violation_evidence.severity.value.upper()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Detected URL:* <{alert.violation_evidence.detected_url}|View Content>"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": alert.message
                    }
                }
            ]
            
            # Add similarity scores
            if alert.violation_evidence.similarity_scores:
                max_similarity = max(s.similarity_score for s in alert.violation_evidence.similarity_scores)
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Max Similarity:* {max_similarity:.2%}"
                    }
                })
            
            # Add action buttons
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Details"
                        },
                        "style": "primary",
                        "url": f"{settings.FRONTEND_URL}/violations/{alert.violation_evidence.violation_id}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Acknowledge"
                        },
                        "style": "default",
                        "value": alert.alert_id
                    }
                ]
            })
            
            payload = {
                "blocks": blocks,
                "unfurl_links": False,
                "unfurl_media": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    success = response.status < 400
                    if success:
                        logger.info("Slack alert sent successfully")
                    else:
                        logger.error(f"Slack alert failed: {response.status}")
                    return success
            
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
            return False


class SMSNotifier:
    """SMS notification handler"""    
    def __init__(self):
        self.api_key = getattr(settings, 'SMS_API_KEY', None)
        self.api_url = getattr(settings, 'SMS_API_URL', None)
    
    async def send_sms_alert(self, alert: Alert, phone_numbers: List[str]) -> bool:
        """Send SMS alert"""        try:
            if not self.api_key or not self.api_url:
                logger.warning("SMS API not configured")
                return False
            
            # Create short message for SMS
            message = f"CONTENT VIOLATION ALERT\n"
            message += f"Type: {alert.violation_evidence.violation_type.value.replace('_', ' ').title()}\n"
            message += f"Severity: {alert.violation_evidence.severity.value.upper()}\n"
            message += f"URL: {alert.violation_evidence.detected_url[:50]}...\n"
            message += f"Time: {alert.created_at.strftime('%H:%M %d/%m/%Y')}"
            
            success_count = 0
            
            async with aiohttp.ClientSession() as session:
                for phone_number in phone_numbers:
                    try:
                        payload = {
                            'api_key': self.api_key,
                            'to': phone_number,
                            'message': message
                        }
                        
                        async with session.post(self.api_url, json=payload) as response:
                            if response.status < 400:
                                success_count += 1
                                logger.debug(f"SMS sent to {phone_number}")
                    
                    except Exception as e:
                        logger.error(f"Error sending SMS to {phone_number}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error in SMS notification: {e}")
            return False


class AlertManager:
    """Main alert management system"""    
    def __init__(self):
        # Notification handlers
        self.email_notifier = EmailNotifier()
        self.webhook_notifier = WebhookNotifier()
        self.slack_notifier = SlackNotifier()
        self.sms_notifier = SMSNotifier()
        
        # Alert storage and tracking
        self.alerts: Dict[str, Alert] = {}
        self.alert_configurations: Dict[str, AlertConfiguration] = {}
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default alert configurations"""        # Critical violations config
        self.alert_configurations['critical_violations'] = AlertConfiguration(
            name="Critical Violations",
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.SMS],
            violation_types=list(ViolationType),
            severity_threshold=ViolationSeverity.CRITICAL,
            similarity_threshold=0.90,
            max_alerts_per_hour=10,
            escalation_delay_minutes=30,
            escalation_channels=[AlertChannel.SMS]
        )
        
        # High priority violations config
        self.alert_configurations['high_priority'] = AlertConfiguration(
            name="High Priority Violations",
            channels=[AlertChannel.EMAIL, AlertChannel.WEBHOOK],
            violation_types=[ViolationType.EXACT_DUPLICATE, ViolationType.MODIFIED_CONTENT],
            severity_threshold=ViolationSeverity.HIGH,
            similarity_threshold=0.80,
            max_alerts_per_hour=25,
            cooldown_minutes=10
        )
        
        # Standard violations config
        self.alert_configurations['standard'] = AlertConfiguration(
            name="Standard Violations",
            channels=[AlertChannel.EMAIL, AlertChannel.IN_APP],
            violation_types=list(ViolationType),
            severity_threshold=ViolationSeverity.MEDIUM,
            similarity_threshold=0.70,
            max_alerts_per_hour=50,
            cooldown_minutes=15
        )
    
    async def start_alert_service(self):
        """Start alert service background tasks"""        # Start alert processor
        processor_task = asyncio.create_task(self._process_alert_queue())
        self.background_tasks.add(processor_task)
        
        # Start escalation handler
        escalation_task = asyncio.create_task(self._handle_escalations())
        self.background_tasks.add(escalation_task)
        
        # Start rate limit cleaner
        cleanup_task = asyncio.create_task(self._cleanup_rate_limits())
        self.background_tasks.add(cleanup_task)
        
        logger.info("Alert service started")
    
    async def stop_alert_service(self):
        """Stop alert service"""        for task in self.background_tasks:
            task.cancel()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("Alert service stopped")
    
    async def send_violation_alert(self, violation_evidence: ViolationEvidence, evidence_data: Dict[str, Any] = None):
        """Send alert for violation detection"""        try:
            # Determine alert configuration
            config = self._get_alert_config_for_violation(violation_evidence)
            
            if not config or not config.enabled:
                return
            
            # Check rate limits
            if not self._check_rate_limits(config):
                logger.warning(f"Rate limit exceeded for config {config.name}")
                return
            
            # Create alert
            alert = self._create_violation_alert(violation_evidence, config, evidence_data)
            
            # Store alert
            self.alerts[alert.alert_id] = alert
            
            # Send alert through configured channels
            await self._send_alert(alert)
            
        except Exception as e:
            logger.error(f"Error sending violation alert: {e}")
    
    async def send_realtime_alert(self, content_id: str, detected_url: str, similarity_score: float):
        """Send real-time alert for high-confidence violations"""        try:
            alert_id = f"realtime_{content_id}_{int(datetime.utcnow().timestamp())}"
            
            alert = Alert(
                alert_id=alert_id,
                violation_evidence=None,  # Simplified for real-time
                alert_type="realtime_violation",
                priority=AlertPriority.HIGH,
                channels=[AlertChannel.WEBHOOK, AlertChannel.IN_APP],
                title=f"🚨 Real-time Violation Detected",
                message=f"High-confidence violation detected for content {content_id}",
                details={
                    'content_id': content_id,
                    'detected_url': detected_url,
                    'similarity_score': similarity_score,
                    'detection_time': datetime.utcnow().isoformat()
                }
            )
            
            self.alerts[alert_id] = alert
            await self._send_alert(alert)
            
        except Exception as e:
            logger.error(f"Error sending realtime alert: {e}")
    
    def _get_alert_config_for_violation(self, violation: ViolationEvidence) -> Optional[AlertConfiguration]:
        """Get appropriate alert configuration for violation"""        # Check critical first
        if violation.severity == ViolationSeverity.CRITICAL:
            return self.alert_configurations.get('critical_violations')
        elif violation.severity == ViolationSeverity.HIGH:
            return self.alert_configurations.get('high_priority')
        else:
            return self.alert_configurations.get('standard')
    
    def _check_rate_limits(self, config: AlertConfiguration) -> bool:
        """Check if rate limits allow sending alert"""        now = datetime.utcnow()
        config_key = config.name
        
        # Initialize rate limit tracking
        if config_key not in self.rate_limits:
            self.rate_limits[config_key] = []
        
        alerts_history = self.rate_limits[config_key]
        
        # Check hourly limit
        hour_ago = now - timedelta(hours=1)
        recent_alerts = [t for t in alerts_history if t > hour_ago]
        
        if len(recent_alerts) >= config.max_alerts_per_hour:
            return False
        
        # Check daily limit
        day_ago = now - timedelta(days=1)
        daily_alerts = [t for t in alerts_history if t > day_ago]
        
        if len(daily_alerts) >= config.max_alerts_per_day:
            return False
        
        # Record this alert
        alerts_history.append(now)
        return True
    
    def _create_violation_alert(self, 
                              violation: ViolationEvidence, 
                              config: AlertConfiguration,
                              evidence_data: Dict[str, Any] = None) -> Alert:
        """Create alert object from violation evidence"""        alert_id = f"alert_{violation.violation_id}_{int(datetime.utcnow().timestamp())}"
        
        # Determine priority
        priority_mapping = {
            ViolationSeverity.CRITICAL: AlertPriority.CRITICAL,
            ViolationSeverity.HIGH: AlertPriority.HIGH,
            ViolationSeverity.MEDIUM: AlertPriority.MEDIUM,
            ViolationSeverity.LOW: AlertPriority.LOW,
            ViolationSeverity.SUSPICIOUS: AlertPriority.INFO
        }
        priority = priority_mapping.get(violation.severity, AlertPriority.MEDIUM)
        
        # Create title and message
        title = f"Content Protection Alert - {violation.violation_type.value.replace('_', ' ').title()}"
        
        max_similarity = max(s.similarity_score for s in violation.similarity_scores) if violation.similarity_scores else 0
        
        message = f"""Content violation detected with {max_similarity:.1%} similarity.

Violation Details:
- Type: {violation.violation_type.value.replace('_', ' ').title()}
- Severity: {violation.severity.value.upper()}
- Detected URL: {violation.detected_url}
- Detection Time: {violation.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

Similarity Scores:
""".strip()
        
        for score in violation.similarity_scores[:3]:  # Show top 3 scores
            message += f"\n- {score.fingerprint_type.value}: {score.similarity_score:.1%} (confidence: {score.confidence:.1%})"
        
        alert = Alert(
            alert_id=alert_id,
            violation_evidence=violation,
            alert_type="violation_detection",
            priority=priority,
            channels=config.channels,
            title=title,
            message=message,
            details={
                'config_name': config.name,
                'evidence_data': evidence_data or {}
            },
            attachments=violation.screenshots
        )
        
        return alert
    
    async def _send_alert(self, alert: Alert):
        """Send alert through configured channels"""        try:
            alert.status = AlertStatus.PENDING
            alert.delivery_attempts += 1
            
            for channel in alert.channels:
                try:
                    success = False
                    
                    if channel == AlertChannel.EMAIL:
                        recipients = getattr(settings, 'ALERT_EMAIL_RECIPIENTS', [])
                        success = await self.email_notifier.send_email_alert(alert, recipients)
                    
                    elif channel == AlertChannel.WEBHOOK:
                        webhook_urls = getattr(settings, 'ALERT_WEBHOOK_URLS', [])
                        success = await self.webhook_notifier.send_webhook_alert(alert, webhook_urls)
                    
                    elif channel == AlertChannel.SLACK:
                        success = await self.slack_notifier.send_slack_alert(alert)
                    
                    elif channel == AlertChannel.SMS:
                        phone_numbers = getattr(settings, 'ALERT_SMS_NUMBERS', [])
                        success = await self.sms_notifier.send_sms_alert(alert, phone_numbers)
                    
                    # Record delivery status
                    alert.delivery_status[channel.value] = "sent" if success else "failed"
                    
                    if not success:
                        alert.error_messages.append(f"Failed to send via {channel.value}")
                
                except Exception as e:
                    logger.error(f"Error sending alert via {channel.value}: {e}")
                    alert.delivery_status[channel.value] = "error"
                    alert.error_messages.append(f"{channel.value}: {str(e)}")
            
            # Update alert status
            successful_deliveries = sum(1 for status in alert.delivery_status.values() if status == "sent")
            
            if successful_deliveries > 0:
                alert.status = AlertStatus.SENT
                alert.sent_at = datetime.utcnow()
            else:
                alert.status = AlertStatus.FAILED
            
            logger.info(f"Alert {alert.alert_id} sent via {successful_deliveries}/{len(alert.channels)} channels")
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            alert.status = AlertStatus.FAILED
            alert.error_messages.append(str(e))
    
    async def _process_alert_queue(self):
        """Background task to process alert queue"""        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Find failed alerts that need retry
                failed_alerts = [
                    alert for alert in self.alerts.values()
                    if alert.status == AlertStatus.FAILED and alert.delivery_attempts < 3
                ]
                
                for alert in failed_alerts:
                    # Wait at least 5 minutes between retries
                    if (datetime.utcnow() - alert.created_at).total_seconds() > 300:
                        logger.info(f"Retrying failed alert {alert.alert_id}")
                        await self._send_alert(alert)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert queue processor: {e}")
    
    async def _handle_escalations(self):
        """Handle alert escalations"""        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                now = datetime.utcnow()
                
                for alert in self.alerts.values():
                    if (alert.status == AlertStatus.SENT and 
                        not alert.acknowledged_at and
                        alert.priority in [AlertPriority.CRITICAL, AlertPriority.HIGH]):
                        
                        # Check if escalation time has passed
                        escalation_delay = timedelta(minutes=60)  # Default 1 hour
                        
                        if alert.sent_at and (now - alert.sent_at) > escalation_delay:
                            await self._escalate_alert(alert)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in escalation handler: {e}")
    
    async def _escalate_alert(self, alert: Alert):
        """Escalate unacknowledged alert"""        try:
            # Create escalation alert
            escalation_alert = Alert(
                alert_id=f"escalation_{alert.alert_id}",
                violation_evidence=alert.violation_evidence,
                alert_type="escalation",
                priority=AlertPriority.CRITICAL,
                channels=[AlertChannel.SMS, AlertChannel.EMAIL],
                title=f"ESCALATION: {alert.title}",
                message=f"UNACKNOWLEDGED ALERT ESCALATION\n\nOriginal alert sent at {alert.sent_at} has not been acknowledged.\n\n{alert.message}",
                details=alert.details
            )
            
            self.alerts[escalation_alert.alert_id] = escalation_alert
            await self._send_alert(escalation_alert)
            
            logger.warning(f"Escalated alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error escalating alert: {e}")
    
    async def _cleanup_rate_limits(self):
        """Clean up old rate limit entries"""        while True:
            try:
                await asyncio.sleep(3600)  # Clean every hour
                
                cutoff_time = datetime.utcnow() - timedelta(days=1)
                
                for config_key in self.rate_limits:
                    self.rate_limits[config_key] = [
                        t for t in self.rate_limits[config_key] if t > cutoff_time
                    ]
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error cleaning rate limits: {e}")
    
    # Public API methods
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert"""        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            
            logger.info(f"Alert {alert_id} acknowledged by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, user_id: str, resolution_notes: str = "") -> bool:
        """Resolve an alert"""        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.notes = resolution_notes
            
            logger.info(f"Alert {alert_id} resolved by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics"""        total_alerts = len(self.alerts)
        
        if total_alerts == 0:
            return {'total_alerts': 0}
        
        status_counts = {}
        priority_counts = {}
        channel_stats = {}
        
        for alert in self.alerts.values():
            # Status distribution
            status = alert.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Priority distribution
            priority = alert.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Channel usage
            for channel in alert.channels:
                channel_name = channel.value
                if channel_name not in channel_stats:
                    channel_stats[channel_name] = {'sent': 0, 'failed': 0}
                
                delivery_status = alert.delivery_status.get(channel_name, 'unknown')
                if delivery_status == 'sent':
                    channel_stats[channel_name]['sent'] += 1
                elif delivery_status in ['failed', 'error']:
                    channel_stats[channel_name]['failed'] += 1
        
        # Calculate rates
        sent_alerts = status_counts.get('sent', 0) + status_counts.get('acknowledged', 0) + status_counts.get('resolved', 0)
        delivery_rate = sent_alerts / total_alerts if total_alerts > 0 else 0
        
        acknowledged_alerts = status_counts.get('acknowledged', 0) + status_counts.get('resolved', 0)
        acknowledgment_rate = acknowledged_alerts / sent_alerts if sent_alerts > 0 else 0
        
        return {
            'total_alerts': total_alerts,
            'status_distribution': status_counts,
            'priority_distribution': priority_counts,
            'channel_statistics': channel_stats,
            'delivery_rate': delivery_rate,
            'acknowledgment_rate': acknowledgment_rate,
            'active_configurations': len([c for c in self.alert_configurations.values() if c.enabled])
        }
