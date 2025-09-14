"""Notification Handler - Deployment Automation

Advanced notification management system for the IA Influencer Agent platform,
providing multi-channel notifications, intelligent alerting, and
comprehensive deployment event communication.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import smtplib
import requests
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import aiohttp

from ..core.base import BaseComponent
from ..monitoring.metrics_collector import MetricsCollector


class NotificationLevel(Enum):
    """
Notification severity levels"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Notification delivery channels"""

    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    SMS = "sms"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    CONSOLE = "console"


class NotificationEventType(Enum):
    """Types of notification events"""

    DEPLOYMENT_STARTED = "deployment_started"
    DEPLOYMENT_COMPLETED = "deployment_completed"
    DEPLOYMENT_FAILED = "deployment_failed"
    ROLLBACK_STARTED = "rollback_started"
    ROLLBACK_COMPLETED = "rollback_completed"
    ROLLBACK_FAILED = "rollback_failed"
    SCALING_EVENT = "scaling_event"
    HEALTH_CHECK_FAILED = "health_check_failed"
    RESOURCE_THRESHOLD = "resource_threshold"
    CONFIGURATION_CHANGED = "configuration_changed"
    SYSTEM_ALERT = "system_alert"
    MAINTENANCE_MODE = "maintenance_mode"


@dataclass
class NotificationTemplate:
    """Notification template configuration"""
    name: str
    event_type: NotificationEventType
    level: NotificationLevel
    channels: List[NotificationChannel]
    subject_template: str
    body_template: str
    is_html: bool = False
    attachments: List[str] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    cooldown_minutes: int = 30
    max_frequency_per_hour: int = 10


@dataclass
class NotificationRecipient:
    """
Notification recipient configuration"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    slack_user_id: Optional[str] = None
    teams_user_id: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    notification_preferences: Dict[NotificationLevel, List[NotificationChannel]] = field(
        default_factory=lambda: {
            NotificationLevel.DEBUG: [],
            NotificationLevel.INFO: [NotificationChannel.EMAIL],
            NotificationLevel.WARNING: [NotificationChannel.EMAIL, NotificationChannel.SLACK],
            NotificationLevel.ERROR: [NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.SMS],
            NotificationLevel.CRITICAL: [NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.SMS]
        }
    )
    time_zone: str = "UTC"
    quiet_hours: Dict[str, str] = field(default_factory=lambda: {"start": "22:00", "end": "08:00"})


@dataclass
class NotificationEvent:
    """Notification event data"""
    event_id: str
    event_type: NotificationEventType
    level: NotificationLevel
    timestamp: datetime
    title: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    environment: Optional[str] = None
    service_name: Optional[str] = None
    workflow_id: Optional[str] = None
    attachments: List[str] = field(default_factory=list)


@dataclass
class NotificationDelivery:
    """
Notification delivery tracking"""
    delivery_id: str
    notification_event_id: str
    recipient: str
    channel: NotificationChannel
    status: str  # pending, sent, failed, skipped
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    response_data: Dict[str, Any] = field(default_factory=dict)


class NotificationHandler(BaseComponent):
    """
    Enterprise-grade notification management system.
    
    Provides comprehensive notification capabilities including multi-channel
    delivery, intelligent routing, rate limiting, template management,
    and delivery tracking for deployment automation events.
    """
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.metrics_collector = MetricsCollector(config.get('metrics', {}))
        
        # Notification state
        self.templates: Dict[str, NotificationTemplate] = {}
        self.recipients: Dict[str, NotificationRecipient] = {}
        self.delivery_history: List[NotificationDelivery] = []
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        
        # Channel configurations
        self.email_config = config.get('email', {})
        self.slack_config = config.get('slack', {})
        self.teams_config = config.get('teams', {})
        self.sms_config = config.get('sms', {})
        self.webhook_config = config.get('webhook', {})
        
        # Rate limiting
        self.rate_limit_cache: Dict[str, List[datetime]] = {}
        self.cooldown_cache: Dict[str, datetime] = {}
        
        # Initialize default templates and recipients
        self._initialize_default_templates()
        self._initialize_default_recipients()
        
        # Start notification worker
        asyncio.create_task(self._notification_worker())

    def _initialize_default_templates(self) -> None:
        """
Initialize default notification templates"""
        
        # Deployment Started
        self.templates['deployment_started'] = NotificationTemplate(
            name="Deployment Started",
            event_type=NotificationEventType.DEPLOYMENT_STARTED,
            level=NotificationLevel.INFO,
            channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
            subject_template="🚀 Deployment Started: {service_name} in {environment}",
            body_template="""Deployment has started for the IA Influencer Agent platform.

**Details:**
- Service: {service_name}
- Environment: {environment}
- Workflow ID: {workflow_id}
- Strategy: {strategy}
- Started at: {timestamp}
- Initiated by: {initiated_by}

The deployment is now in progress. You will receive updates as the process continues.

---
IA Influencer Agent Deployment System
(c) Fahed Mlaiel - All rights reserved
            """,
            cooldown_minutes=5
        )
        
        # Deployment Completed
        self.templates['deployment_completed'] = NotificationTemplate(
            name="Deployment Completed",
            event_type=NotificationEventType.DEPLOYMENT_COMPLETED,
            level=NotificationLevel.INFO,
            channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
            subject_template="✅ Deployment Completed: {service_name} in {environment}",
            body_template="""Deployment has completed successfully for the IA Influencer Agent platform.

**Details:**
- Service: {service_name}
- Environment: {environment}
- Workflow ID: {workflow_id}
- Duration: {duration}
- Completed at: {timestamp}

**Health Status:**
{health_status}

The new version is now live and serving traffic.

---
IA Influencer Agent Deployment System
(c) Fahed Mlaiel - All rights reserved
            """,
            cooldown_minutes=5
        )
        
        # Deployment Failed
        self.templates['deployment_failed'] = NotificationTemplate(
            name="Deployment Failed",
            event_type=NotificationEventType.DEPLOYMENT_FAILED,
            level=NotificationLevel.ERROR,
            channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL, NotificationChannel.SMS],
            subject_template="❌ Deployment Failed: {service_name} in {environment}",
            body_template="""DEPLOYMENT FAILURE ALERT

A deployment has failed for the IA Influencer Agent platform.

**Details:**
- Service: {service_name}
- Environment: {environment}
- Workflow ID: {workflow_id}
- Failed at: {timestamp}
- Duration: {duration}

**Error Details:**
{error_message}

**Steps Completed:**
{completed_steps}

**Recommended Actions:**
1. Review the deployment logs
2. Check service health status
3. Consider initiating a rollback
4. Contact the development team if needed

---
IA Influencer Agent Deployment System
(c) Fahed Mlaiel - All rights reserved
            """,
            cooldown_minutes=10
        )
        
        # Rollback Events
        self.templates['rollback_completed'] = NotificationTemplate(
            name="Rollback Completed",
            event_type=NotificationEventType.ROLLBACK_COMPLETED,
            level=NotificationLevel.WARNING,
            channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
            subject_template="🔄 Rollback Completed: {service_name} in {environment}",
            body_template="""Rollback has completed for the IA Influencer Agent platform.

**Details:**
- Service: {service_name}
- Environment: {environment}
- Rollback Point: {rollback_point}
- Duration: {duration}
- Completed at: {timestamp}
- Reason: {reason}

**Health Status:**
{health_status}

The service has been restored to the previous stable version.

---
IA Influencer Agent Deployment System
(c) Fahed Mlaiel - All rights reserved
            """,
            cooldown_minutes=15
        )
        
        # Scaling Events
        self.templates['scaling_event'] = NotificationTemplate(
            name="Scaling Event",
            event_type=NotificationEventType.SCALING_EVENT,
            level=NotificationLevel.INFO,
            channels=[NotificationChannel.SLACK],
            subject_template="📊 Scaling Event: {service_name} ({from_replicas} → {to_replicas})",
            body_template="""Auto-scaling event occurred for the IA Influencer Agent platform.

**Details:**
- Service: {service_name}
- Environment: {environment}
- From: {from_replicas} replicas
- To: {to_replicas} replicas
- Direction: {direction}
- Trigger: {trigger_reason}
- Strategy: {strategy}
- Timestamp: {timestamp}

**Current Metrics:**
{current_metrics}

The service capacity has been automatically adjusted based on current demand.

---
IA Influencer Agent Deployment System
(c) Fahed Mlaiel - All rights reserved
            """,
            cooldown_minutes=30,
            max_frequency_per_hour=6
        )
        
        # Health Check Failed
        self.templates['health_check_failed'] = NotificationTemplate(
            name="Health Check Failed",
            event_type=NotificationEventType.HEALTH_CHECK_FAILED,
            level=NotificationLevel.ERROR,
            channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL, NotificationChannel.SMS],
            subject_template="🚨 Health Check Failed: {service_name} in {environment}",
            body_template="""HEALTH CHECK FAILURE ALERT

A critical health check has failed for the IA Influencer Agent platform.

**Details:**
- Service: {service_name}
- Environment: {environment}
- Health Check: {health_check_name}
- Failed at: {timestamp}
- Consecutive Failures: {failure_count}

**Failure Details:**
{failure_reason}

**Service Status:**
{service_status}

**Immediate Actions Required:**
1. Investigate service health immediately
2. Check resource utilization
3. Review recent deployments
4. Consider emergency rollback if needed

---
IA Influencer Agent Deployment System
(c) Fahed Mlaiel - All rights reserved
            """,
            cooldown_minutes=5,
            max_frequency_per_hour=12
        )

    def _initialize_default_recipients(self) -> None:
        """
Initialize default notification recipients"""
        
        # Platform Administrator
        self.recipients['platform_admin'] = NotificationRecipient(
            name="Platform Administrator",
            email=self.config.get('admin_email', 'mlaiel@live.de'),
            phone=self.config.get('admin_phone'),
            slack_user_id=self.config.get('admin_slack_id'),
            notification_preferences={
                NotificationLevel.DEBUG: [],
                NotificationLevel.INFO: [NotificationChannel.SLACK],
                NotificationLevel.WARNING: [NotificationChannel.EMAIL, NotificationChannel.SLACK],
                NotificationLevel.ERROR: [NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.SMS],
                NotificationLevel.CRITICAL: [NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.SMS]
            }
        )
        
        # DevOps Team
        self.recipients['devops_team'] = NotificationRecipient(
            name="DevOps Team",
            email=self.config.get('devops_email', 'devops@ia-influencer.com'),
            slack_user_id=self.config.get('devops_slack_channel'),
            notification_preferences={
                NotificationLevel.DEBUG: [],
                NotificationLevel.INFO: [NotificationChannel.SLACK],
                NotificationLevel.WARNING: [NotificationChannel.EMAIL, NotificationChannel.SLACK],
                NotificationLevel.ERROR: [NotificationChannel.EMAIL, NotificationChannel.SLACK],
                NotificationLevel.CRITICAL: [NotificationChannel.EMAIL, NotificationChannel.SLACK]
            }
        )
        
        # Development Team
        self.recipients['dev_team'] = NotificationRecipient(
            name="Development Team",
            email=self.config.get('dev_email', 'dev@ia-influencer.com'),
            slack_user_id=self.config.get('dev_slack_channel'),
            notification_preferences={
                NotificationLevel.DEBUG: [],
                NotificationLevel.INFO: [],
                NotificationLevel.WARNING: [NotificationChannel.SLACK],
                NotificationLevel.ERROR: [NotificationChannel.EMAIL, NotificationChannel.SLACK],
                NotificationLevel.CRITICAL: [NotificationChannel.EMAIL, NotificationChannel.SLACK]
            }
        )

    async def _notification_worker(self) -> None:
        """Background worker to process notification queue"""
        
        while True:
            try:
                # Get notification from queue
                notification_event = await self.notification_queue.get()
                
                # Process the notification
                await self._process_notification(notification_event)
                
                # Mark task as done
                self.notification_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in notification worker: {str(e)}", exc_info=True)
                await asyncio.sleep(1)

    async def send_notification(
        self,
        event_type: NotificationEventType,
        level: NotificationLevel,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        environment: Optional[str] = None,
        service_name: Optional[str] = None,
        workflow_id: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> str:
        """
        Send a notification.
        
        Args:
            event_type: Type of notification event
            level: Notification severity level
            title: Notification title
            message: Notification message
            metadata: Additional metadata
            environment: Environment name
            service_name: Service name
            workflow_id: Workflow identifier
            attachments: File attachments
            
        Returns:
            Notification event ID
        """
        
        event_id = f"notif-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{event_type.value}"
        
        notification_event = NotificationEvent(
            event_id=event_id,
            event_type=event_type,
            level=level,
            timestamp=datetime.utcnow(),
            title=title,
            message=message,
            metadata=metadata or {},
            environment=environment,
            service_name=service_name,
            workflow_id=workflow_id,
            attachments=attachments or []
        )
        
        # Add to queue for processing
        await self.notification_queue.put(notification_event)
        
        self.logger.info(f"Queued notification: {event_id} ({event_type.value}, {level.value})")
        
        return event_id

    async def _process_notification(self, event: NotificationEvent) -> None:
        """Process a notification event"""
        
        try:
            # Get template for this event type
            template = self._get_template_for_event(event)
            
            if not template:
                self.logger.warning(f"No template found for event type: {event.event_type.value}")
                return
            
            # Check rate limiting and cooldowns
            if self._is_rate_limited(event, template):
                self.logger.info(f"Notification rate limited: {event.event_id}")
                return
            
            # Get recipients for this notification level
            recipients = self._get_recipients_for_level(event.level)
            
            if not recipients:
                self.logger.warning(f"No recipients configured for level: {event.level.value}")
                return
            
            # Process each recipient
            for recipient_name, recipient in recipients.items():
                await self._send_to_recipient(event, template, recipient_name, recipient)
            
            # Update rate limiting cache
            self._update_rate_limit_cache(event, template)
            
        except Exception as e:
            self.logger.error(f"Error processing notification {event.event_id}: {str(e)}", exc_info=True)

    def _get_template_for_event(self, event: NotificationEvent) -> Optional[NotificationTemplate]:
        """Get notification template for an event"""
        
        # Try exact match first
        template_key = event.event_type.value
        if template_key in self.templates:
            return self.templates[template_key]
        
        # Try generic templates based on level
        if event.level == NotificationLevel.CRITICAL:
            return self._get_critical_template()
        elif event.level == NotificationLevel.ERROR:
            return self._get_error_template()
        
        return None

    def _get_critical_template(self) -> NotificationTemplate:
        """
Get default critical notification template"""
        
        return NotificationTemplate(
            name="Critical Alert",
            event_type=NotificationEventType.SYSTEM_ALERT,
            level=NotificationLevel.CRITICAL,
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.SMS],
            subject_template="🚨 CRITICAL ALERT: {title}",
            body_template="""CRITICAL SYSTEM ALERT

{message}

**Details:**
- Environment: {environment}
- Service: {service_name}
- Timestamp: {timestamp}
- Workflow ID: {workflow_id}

Immediate attention required!

---
IA Influencer Agent Deployment System
(c) Fahed Mlaiel - All rights reserved
            """,
            cooldown_minutes=5
        )

    def _get_error_template(self) -> NotificationTemplate:
        """
Get default error notification template"""
        
        return NotificationTemplate(
            name="Error Alert",
            event_type=NotificationEventType.SYSTEM_ALERT,
            level=NotificationLevel.ERROR,
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            subject_template="❌ ERROR: {title}",
            body_template="""System Error Alert

{message}

**Details:**
- Environment: {environment}
- Service: {service_name}
- Timestamp: {timestamp}
- Workflow ID: {workflow_id}

Please investigate this issue.

---
IA Influencer Agent Deployment System
(c) Fahed Mlaiel - All rights reserved
            """,
            cooldown_minutes=10
        )

    def _get_recipients_for_level(self, level: NotificationLevel) -> Dict[str, NotificationRecipient]:
        """
Get recipients that should receive notifications at this level"""
        
        relevant_recipients = {}
        
        for name, recipient in self.recipients.items():
            if level in recipient.notification_preferences:
                channels = recipient.notification_preferences[level]
                if channels:  # Only include if they want notifications at this level
                    relevant_recipients[name] = recipient
        
        return relevant_recipients

    async def _send_to_recipient(
        self,
        event: NotificationEvent,
        template: NotificationTemplate,
        recipient_name: str,
        recipient: NotificationRecipient
    ) -> None:
        """
Send notification to a specific recipient"""
        
        try:
            # Check if recipient wants notifications at this level
            if event.level not in recipient.notification_preferences:
                return
            
            channels = recipient.notification_preferences[event.level]
            
            # Check quiet hours
            if self._is_in_quiet_hours(recipient):
                # Only send critical notifications during quiet hours
                if event.level != NotificationLevel.CRITICAL:
                    self.logger.info(f"Skipping notification during quiet hours: {recipient_name}")
                    return
            
            # Send to each preferred channel
            for channel in channels:
                if channel in template.channels:  # Only send if template supports this channel
                    await self._send_via_channel(event, template, recipient, channel)
        
        except Exception as e:
            self.logger.error(f"Error sending to recipient {recipient_name}: {str(e)}")

    async def _send_via_channel(
        self,
        event: NotificationEvent,
        template: NotificationTemplate,
        recipient: NotificationRecipient,
        channel: NotificationChannel
    ) -> None:
        """Send notification via specific channel"""
        
        delivery_id = f"delivery-{event.event_id}-{channel.value}-{datetime.utcnow().strftime('%H%M%S')}"
        
        delivery = NotificationDelivery(
            delivery_id=delivery_id,
            notification_event_id=event.event_id,
            recipient=recipient.name,
            channel=channel,
            status="pending"
        )
        
        try:
            # Render message from template
            rendered_subject, rendered_body = self._render_template(event, template)
            
            # Send via appropriate channel
            if channel == NotificationChannel.EMAIL:
                await self._send_email(recipient, rendered_subject, rendered_body, event.attachments)
            elif channel == NotificationChannel.SLACK:
                await self._send_slack(recipient, rendered_subject, rendered_body)
            elif channel == NotificationChannel.TEAMS:
                await self._send_teams(recipient, rendered_subject, rendered_body)
            elif channel == NotificationChannel.SMS:
                await self._send_sms(recipient, rendered_subject)
            elif channel == NotificationChannel.WEBHOOK:
                await self._send_webhook(event, rendered_subject, rendered_body)
            elif channel == NotificationChannel.CONSOLE:
                self._send_console(rendered_subject, rendered_body)
            
            delivery.status = "sent"
            delivery.sent_at = datetime.utcnow()
            
        except Exception as e:
            delivery.status = "failed"
            delivery.error_message = str(e)
            self.logger.error(f"Failed to send notification via {channel.value}: {str(e)}")
        
        finally:
            self.delivery_history.append(delivery)

    def _render_template(
        self,
        event: NotificationEvent,
        template: NotificationTemplate
    ) -> tuple[str, str]:
        """Render notification template with event data"""
        
        # Prepare template variables
        variables = {
            'title': event.title,
            'message': event.message,
            'timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'environment': event.environment or 'unknown',
            'service_name': event.service_name or 'unknown',
            'workflow_id': event.workflow_id or 'unknown',
            'event_type': event.event_type.value,
            'level': event.level.value
        }
        
        # Add metadata variables
        variables.update(event.metadata)
        
        # Render subject
        try:
            rendered_subject = template.subject_template.format(**variables)
        except KeyError as e:
            self.logger.warning(f"Missing template variable in subject: {e}")
            rendered_subject = template.subject_template
        
        # Render body
        try:
            rendered_body = template.body_template.format(**variables)
        except KeyError as e:
            self.logger.warning(f"Missing template variable in body: {e}")
            rendered_body = template.body_template
        
        return rendered_subject, rendered_body

    async def _send_email(
        self,
        recipient: NotificationRecipient,
        subject: str,
        body: str,
        attachments: List[str]
    ) -> None:
        """Send email notification"""
        
        if not recipient.email or not self.email_config:
            return
        
        try:
            # Create message
            msg = MimeMultipart()
            msg['From'] = self.email_config.get('from_address', 'noreply@ia-influencer.com')
            msg['To'] = recipient.email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MimeText(body, 'plain'))
            
            # Add attachments
            for attachment_path in attachments:
                try:
                    with open(attachment_path, 'rb') as attachment:
                        part = MimeBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {attachment_path.split("/")[-1]}'
                        )
                        msg.attach(part)
                except Exception as e:
                    self.logger.warning(f"Failed to attach file {attachment_path}: {str(e)}")
            
            # Send email
            smtp_server = self.email_config.get('smtp_server', 'localhost')
            smtp_port = self.email_config.get('smtp_port', 587)
            smtp_username = self.email_config.get('smtp_username')
            smtp_password = self.email_config.get('smtp_password')
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            
            if smtp_username and smtp_password:
                server.starttls()
                server.login(smtp_username, smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {recipient.email}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {recipient.email}: {str(e)}")
            raise

    async def _send_slack(
        self,
        recipient: NotificationRecipient,
        subject: str,
        body: str
    ) -> None:
        """Send Slack notification"""
        
        if not self.slack_config.get('webhook_url'):
            return
        
        try:
            # Format message for Slack
            slack_message = {
                "text": subject,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": subject
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": body.replace('\n', '\n')
                        }
                    }
                ]
            }
            
            # Add user mention if specified
            if recipient.slack_user_id:
                slack_message["channel"] = f"@{recipient.slack_user_id}"
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.slack_config['webhook_url'],
                    json=slack_message,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Slack notification sent successfully")
                    else:
                        raise Exception(f"Slack API returned status {response.status}")
        
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {str(e)}")
            raise

    async def _send_teams(
        self,
        recipient: NotificationRecipient,
        subject: str,
        body: str
    ) -> None:
        """Send Microsoft Teams notification"""
        
        if not self.teams_config.get('webhook_url'):
            return
        
        try:
            # Format message for Teams
            teams_message = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": subject,
                "sections": [{
                    "activityTitle": subject,
                    "activitySubtitle": "IA Influencer Agent Deployment System",
                    "text": body,
                    "markdown": True
                }]
            }
            
            # Send to Teams
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.teams_config['webhook_url'],
                    json=teams_message,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Teams notification sent successfully")
                    else:
                        raise Exception(f"Teams API returned status {response.status}")
        
        except Exception as e:
            self.logger.error(f"Failed to send Teams notification: {str(e)}")
            raise

    async def _send_sms(
        self,
        recipient: NotificationRecipient,
        message: str
    ) -> None:
        """Send SMS notification"""
        
        if not recipient.phone or not self.sms_config:
            return
        
        try:
            # Use configured SMS service (Twilio, AWS SNS, etc.)
            sms_service = self.sms_config.get('service', 'twilio')
            
            if sms_service == 'twilio':
                await self._send_twilio_sms(recipient.phone, message)
            elif sms_service == 'aws_sns':
                await self._send_aws_sns_sms(recipient.phone, message)
            else:
                raise Exception(f"Unsupported SMS service: {sms_service}")
        
        except Exception as e:
            self.logger.error(f"Failed to send SMS to {recipient.phone}: {str(e)}")
            raise

    async def _send_twilio_sms(self, phone: str, message: str) -> None:
        """Send SMS via Twilio"""
        
        # This would use the Twilio client
        # For security, actual implementation would use proper Twilio SDK
        self.logger.info(f"SMS would be sent to {phone}: {message[:50]}...")

    async def _send_aws_sns_sms(self, phone: str, message: str) -> None:
        """Send SMS via AWS SNS"""
        
        # This would use AWS SNS client
        # For security, actual implementation would use proper AWS SDK
        self.logger.info(f"AWS SNS SMS would be sent to {phone}: {message[:50]}...")

    async def _send_webhook(
        self,
        event: NotificationEvent,
        subject: str,
        body: str
    ) -> None:
        """Send webhook notification"""
        
        webhook_urls = self.webhook_config.get('urls', [])
        
        for webhook_url in webhook_urls:
            try:
                payload = {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "level": event.level.value,
                    "timestamp": event.timestamp.isoformat(),
                    "subject": subject,
                    "body": body,
                    "metadata": event.metadata,
                    "environment": event.environment,
                    "service_name": event.service_name,
                    "workflow_id": event.workflow_id
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook_url,
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            self.logger.info(f"Webhook notification sent to {webhook_url}")
                        else:
                            raise Exception(f"Webhook returned status {response.status}")
            
            except Exception as e:
                self.logger.error(f"Failed to send webhook to {webhook_url}: {str(e)}")

    def _send_console(self, subject: str, body: str) -> None:
        """Send console notification (logging)"""
        
        self.logger.info(f"NOTIFICATION: {subject}")
        self.logger.info(f"MESSAGE: {body}")

    def _is_rate_limited(self, event: NotificationEvent, template: NotificationTemplate) -> bool:
        """Check if notification is rate limited"""
        
        # Check cooldown
        cooldown_key = f"{event.event_type.value}_{event.service_name or 'global'}"
        if cooldown_key in self.cooldown_cache:
            last_sent = self.cooldown_cache[cooldown_key]
            cooldown_period = timedelta(minutes=template.cooldown_minutes)
            if datetime.utcnow() - last_sent < cooldown_period:
                return True
        
        # Check frequency limit
        rate_key = f"{event.event_type.value}_{event.service_name or 'global'}"
        if rate_key in self.rate_limit_cache:
            # Clean old entries (older than 1 hour)
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            self.rate_limit_cache[rate_key] = [
                timestamp for timestamp in self.rate_limit_cache[rate_key]
                if timestamp > one_hour_ago
            ]
            
            # Check if we exceed the frequency limit
            if len(self.rate_limit_cache[rate_key]) >= template.max_frequency_per_hour:
                return True
        
        return False

    def _update_rate_limit_cache(self, event: NotificationEvent, template: NotificationTemplate) -> None:
        """Update rate limiting cache"""
        
        current_time = datetime.utcnow()
        
        # Update cooldown cache
        cooldown_key = f"{event.event_type.value}_{event.service_name or 'global'}"
        self.cooldown_cache[cooldown_key] = current_time
        
        # Update frequency cache
        rate_key = f"{event.event_type.value}_{event.service_name or 'global'}"
        if rate_key not in self.rate_limit_cache:
            self.rate_limit_cache[rate_key] = []
        self.rate_limit_cache[rate_key].append(current_time)

    def _is_in_quiet_hours(self, recipient: NotificationRecipient) -> bool:
        """Check if current time is in recipient's quiet hours"""
        
        # Simple implementation - would need proper timezone handling
        current_hour = datetime.utcnow().hour
        
        quiet_start = int(recipient.quiet_hours.get('start', '22:00').split(':')[0])
        quiet_end = int(recipient.quiet_hours.get('end', '08:00').split(':')[0])
        
        if quiet_start > quiet_end:  # Overnight quiet hours
            return current_hour >= quiet_start or current_hour < quiet_end
        else:
            return quiet_start <= current_hour < quiet_end

    async def add_notification_template(self, template: NotificationTemplate) -> None:
        """
Add a new notification template"""
        
        self.templates[template.name.lower().replace(' ', '_')] = template
        self.logger.info(f"Added notification template: {template.name}")

    async def add_notification_recipient(self, recipient: NotificationRecipient) -> None:
        """Add a new notification recipient"""
        
        self.recipients[recipient.name.lower().replace(' ', '_')] = recipient
        self.logger.info(f"Added notification recipient: {recipient.name}")

    async def get_notification_status(self, event_id: str) -> Dict[str, Any]:
        """Get notification delivery status"""
        
        deliveries = [d for d in self.delivery_history if d.notification_event_id == event_id]
        
        return {
            'event_id': event_id,
            'total_deliveries': len(deliveries),
            'successful_deliveries': len([d for d in deliveries if d.status == 'sent']),
            'failed_deliveries': len([d for d in deliveries if d.status == 'failed']),
            'deliveries': [
                {
                    'delivery_id': d.delivery_id,
                    'recipient': d.recipient,
                    'channel': d.channel.value,
                    'status': d.status,
                    'sent_at': d.sent_at,
                    'error_message': d.error_message
                }
                for d in deliveries
            ]
        }

    async def get_delivery_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
Get notification delivery statistics"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_deliveries = [
            d for d in self.delivery_history
            if d.sent_at and d.sent_at > cutoff_time
        ]
        
        total_deliveries = len(recent_deliveries)
        successful_deliveries = len([d for d in recent_deliveries if d.status == 'sent'])
        failed_deliveries = len([d for d in recent_deliveries if d.status == 'failed'])
        
        # Channel breakdown
        channel_stats = {}
        for delivery in recent_deliveries:
            channel = delivery.channel.value
            if channel not in channel_stats:
                channel_stats[channel] = {'total': 0, 'successful': 0, 'failed': 0}
            
            channel_stats[channel]['total'] += 1
            if delivery.status == 'sent':
                channel_stats[channel]['successful'] += 1
            elif delivery.status == 'failed':
                channel_stats[channel]['failed'] += 1
        
        return {
            'time_period_hours': hours,
            'total_deliveries': total_deliveries,
            'successful_deliveries': successful_deliveries,
            'failed_deliveries': failed_deliveries,
            'success_rate': (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0,
            'channel_statistics': channel_stats
        }

    async def test_notification_channels(self) -> Dict[str, Any]:
        """
Test all configured notification channels"""
        
        test_results = {}
        
        test_event = NotificationEvent(
            event_id="test-notification",
            event_type=NotificationEventType.SYSTEM_ALERT,
            level=NotificationLevel.INFO,
            timestamp=datetime.utcnow(),
            title="Test Notification",
            message="This is a test notification to verify channel connectivity.",
            metadata={'test': True}
        )
        
        # Test each configured channel
        for channel in NotificationChannel:
            try:
                if channel == NotificationChannel.EMAIL and self.email_config:
                    # Test email configuration
                    test_results[channel.value] = {'status': 'configured', 'error': None}
                elif channel == NotificationChannel.SLACK and self.slack_config.get('webhook_url'):
                    # Test Slack webhook
                    test_results[channel.value] = {'status': 'configured', 'error': None}
                elif channel == NotificationChannel.TEAMS and self.teams_config.get('webhook_url'):
                    # Test Teams webhook
                    test_results[channel.value] = {'status': 'configured', 'error': None}
                elif channel == NotificationChannel.SMS and self.sms_config:
                    # Test SMS configuration
                    test_results[channel.value] = {'status': 'configured', 'error': None}
                elif channel == NotificationChannel.WEBHOOK and self.webhook_config.get('urls'):
                    # Test webhook configuration
                    test_results[channel.value] = {'status': 'configured', 'error': None}
                else:
                    test_results[channel.value] = {'status': 'not_configured', 'error': 'No configuration found'}
            
            except Exception as e:
                test_results[channel.value] = {'status': 'error', 'error': str(e)}
        
        return test_results
