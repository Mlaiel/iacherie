"""Notification Service for Copyright Enforcement
Professional notification system for alerts, updates, and communications
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import smtplib
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiohttp
from pathlib import Path

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """
Types of notifications"""

    CASE_CREATED = "case_created"
    CASE_UPDATED = "case_updated"
    CASE_RESOLVED = "case_resolved"
    ESCALATION_CREATED = "escalation_created"
    ESCALATION_APPROVED = "escalation_approved"
    ESCALATION_REJECTED = "escalation_rejected"
    DOCUMENT_GENERATED = "document_generated"
    DOCUMENT_SENT = "document_sent"
    PLATFORM_RESPONSE = "platform_response"
    DEADLINE_WARNING = "deadline_warning"
    DEADLINE_MISSED = "deadline_missed"
    EVIDENCE_COLLECTED = "evidence_collected"
    ALERT_CRITICAL = "alert_critical"
    ALERT_WARNING = "alert_warning"
    SYSTEM_STATUS = "system_status"
    REPORT_GENERATED = "report_generated"


class NotificationPriority(Enum):
    """Notification priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Notification delivery channels"""

    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    DASHBOARD = "dashboard"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(Enum):
    """Status of notification delivery"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    READ = "read"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class NotificationRecipient:
    """Notification recipient information"""
    id: str
    name: str
    email: str = ""
    phone: str = ""
    slack_user_id: str = ""
    discord_user_id: str = ""
    webhook_url: str = ""
    
    # Preferences
    preferred_channels: List[NotificationChannel] = field(default_factory=lambda: [NotificationChannel.EMAIL])
    timezone: str = "UTC"
    notification_hours: Tuple[int, int] = (9, 18)  # 9 AM to 6 PM
    enabled: bool = True
    
    # Subscription settings
    subscribed_types: Set[NotificationType] = field(default_factory=set)
    minimum_priority: NotificationPriority = NotificationPriority.NORMAL


@dataclass
class NotificationTemplate:
    """Template for notification content"""
    id: str
    notification_type: NotificationType
    channel: NotificationChannel
    subject_template: str
    body_template: str
    html_template: Optional[str] = None
    
    # Template metadata
    language: str = "en"
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    variables: Set[str] = field(default_factory=set)


@dataclass
class NotificationMessage:
    """Individual notification message"""
    id: str
    notification_type: NotificationType
    recipient: NotificationRecipient
    channel: NotificationChannel
    priority: NotificationPriority
    
    # Content
    subject: str
    body: str
    html_body: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    
    # Context and metadata
    case_id: Optional[str] = None
    related_entity_id: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    # Delivery tracking
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # Retry and error handling
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    
    # Tracking
    tracking_id: Optional[str] = None
    delivery_receipt: Optional[str] = None


class EmailProvider:
    """
Email notification provider"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.smtp_host = config.get('smtp_host', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_username = config.get('smtp_username', '')
        self.smtp_password = config.get('smtp_password', '')
        self.smtp_use_tls = config.get('smtp_use_tls', True)
        self.from_email = config.get('from_email', 'noreply@example.com')
        self.from_name = config.get('from_name', 'IA Influencer Agent')
    
    async def send_email(self, message: NotificationMessage) -> bool:
        """
Send email notification"""
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = message.recipient.email
            msg['Message-ID'] = f"<{message.id}@{self.smtp_host}>"
            
            # Add text body
            text_part = MIMEText(message.body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML body if available
            if message.html_body:
                html_part = MIMEText(message.html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments
            for attachment_path in message.attachments:
                try:
                    with open(attachment_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {Path(attachment_path).name}'
                        )
                        msg.attach(part)
                except Exception as e:
                    logger.warning(f"Failed to attach file {attachment_path}: {e}")
            
            # Send email
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls
            )
            
            logger.info(f"Email sent successfully to {message.recipient.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {message.recipient.email}: {e}")
            message.error_message = str(e)
            return False


class WebhookProvider:
    """Webhook notification provider"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get('timeout', 30)
        self.retry_delays = [1, 5, 15]  # seconds
    
    async def send_webhook(self, message: NotificationMessage) -> bool:
        """
Send webhook notification"""
        try:
            webhook_url = message.recipient.webhook_url
            if not webhook_url:
                logger.error("No webhook URL configured for recipient")
                return False
            
            # Prepare webhook payload
            payload = {
                'id': message.id,
                'type': message.notification_type.value,
                'priority': message.priority.value,
                'subject': message.subject,
                'body': message.body,
                'case_id': message.case_id,
                'timestamp': message.created_at.isoformat(),
                'context': message.context_data
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'IA-Influencer-Agent/2.0 (Notification Service)',
                'X-Notification-ID': message.id,
                'X-Notification-Type': message.notification_type.value
            }
            
            # Send webhook with retries
            for attempt in range(len(self.retry_delays) + 1):
                try:
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                        async with session.post(webhook_url, json=payload, headers=headers) as response:
                            if response.status in [200, 201, 202]:
                                logger.info(f"Webhook sent successfully to {webhook_url}")
                                message.tracking_id = response.headers.get('X-Tracking-ID')
                                return True
                            elif response.status in [400, 401, 403, 404]:
                                # Don't retry client errors
                                logger.error(f"Webhook failed with client error {response.status}")
                                message.error_message = f"HTTP {response.status}"
                                return False
                            else:
                                # Server error, might retry
                                if attempt < len(self.retry_delays):
                                    await asyncio.sleep(self.retry_delays[attempt])
                                    continue
                                else:
                                    message.error_message = f"HTTP {response.status} after retries"
                                    return False
                
                except asyncio.TimeoutError:
                    if attempt < len(self.retry_delays):
                        await asyncio.sleep(self.retry_delays[attempt])
                        continue
                    else:
                        message.error_message = "Timeout after retries"
                        return False
                
                except Exception as e:
                    if attempt < len(self.retry_delays):
                        await asyncio.sleep(self.retry_delays[attempt])
                        continue
                    else:
                        message.error_message = str(e)
                        return False
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
            message.error_message = str(e)
            return False


class SlackProvider:
    """Slack notification provider"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bot_token = config.get('bot_token', '')
        self.webhook_url = config.get('webhook_url', '')
        self.timeout = config.get('timeout', 30)
    
    async def send_slack_message(self, message: NotificationMessage) -> bool:
        """
Send Slack notification"""
        try:
            if not self.webhook_url and not self.bot_token:
                logger.error("No Slack configuration found")
                return False
            
            # Prepare Slack message
            slack_message = {
                'text': message.subject,
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': message.subject
                        }
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': message.body
                        }
                    }
                ]
            }
            
            # Add context information
            if message.case_id:
                slack_message['blocks'].append({
                    'type': 'context',
                    'elements': [
                        {
                            'type': 'mrkdwn',
                            'text': f"*Case ID:* {message.case_id}"
                        },
                        {
                            'type': 'mrkdwn',
                            'text': f"*Priority:* {message.priority.value.upper()}"
                        }
                    ]
                })
            
            # Add color based on priority
            if message.priority == NotificationPriority.CRITICAL:
                slack_message['attachments'] = [{'color': 'danger'}]
            elif message.priority == NotificationPriority.URGENT:
                slack_message['attachments'] = [{'color': 'warning'}]
            elif message.priority == NotificationPriority.HIGH:
                slack_message['attachments'] = [{'color': 'good'}]
            
            # Send via webhook or bot API
            if self.webhook_url:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    async with session.post(self.webhook_url, json=slack_message) as response:
                        if response.status == 200:
                            logger.info("Slack message sent via webhook")
                            return True
                        else:
                            logger.error(f"Slack webhook failed: {response.status}")
                            return False
            
            elif self.bot_token:
                # Use Slack Web API
                headers = {
                    'Authorization': f'Bearer {self.bot_token}',
                    'Content-Type': 'application/json'
                }
                
                # Send to user or channel
                if message.recipient.slack_user_id:
                    slack_message['channel'] = message.recipient.slack_user_id
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    async with session.post(
                        'https://slack.com/api/chat.postMessage',
                        json=slack_message,
                        headers=headers
                    ) as response:
                        result = await response.json()
                        if result.get('ok'):
                            logger.info("Slack message sent via bot API")
                            message.tracking_id = result.get('ts')
                            return True
                        else:
                            logger.error(f"Slack bot API failed: {result.get('error')}")
                            message.error_message = result.get('error')
                            return False
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            message.error_message = str(e)
            return False


class NotificationService:
    """Main notification service"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize providers
        self.email_provider = EmailProvider(self.config.get('email', {})) if self.config.get('email') else None
        self.webhook_provider = WebhookProvider(self.config.get('webhook', {})) if self.config.get('webhook') else None
        self.slack_provider = SlackProvider(self.config.get('slack', {})) if self.config.get('slack') else None
        
        # Storage and caching
        self.recipients: Dict[str, NotificationRecipient] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        self.message_queue: List[NotificationMessage] = []
        self.sent_messages: Dict[str, NotificationMessage] = {}
        
        # Service settings
        self.queue_processing_interval = self.config.get('queue_processing_interval', 10)  # seconds
        self.max_queue_size = self.config.get('max_queue_size', 1000)
        self.message_retention_days = self.config.get('message_retention_days', 30)
        self.enable_rate_limiting = self.config.get('enable_rate_limiting', True)
        
        # Rate limiting
        self.rate_limits = {
            NotificationChannel.EMAIL: 100,  # per hour
            NotificationChannel.SMS: 50,
            NotificationChannel.WEBHOOK: 500,
            NotificationChannel.SLACK: 200
        }
        self.rate_tracking: Dict[str, List[datetime]] = {}
        
        # Processing state
        self.processing = False
        self.processing_task: Optional[asyncio.Task] = None
        
        self._setup_default_templates()
        logger.info("Notification service initialized")
    
    def _setup_default_templates(self):
        """Setup default notification templates"""
        default_templates = [
            NotificationTemplate(
                id="case_created_email",
                notification_type=NotificationType.CASE_CREATED,
                channel=NotificationChannel.EMAIL,
                subject_template="New Copyright Case Created - {{case_id}}",
                body_template="""A new copyright enforcement case has been created.

Case ID: {{case_id}}
Infringement URL: {{infringement_url}}
Platform: {{platform}}
Similarity Score: {{similarity_score}}%
Priority: {{priority}}

The case has been assigned for review and enforcement actions will begin automatically.

This is an automated notification from IA Influencer Agent Content Protection System.
""",
                html_template="""<h2>New Copyright Case Created</h2>
<p>A new copyright enforcement case has been created.</p>
<ul>
<li><strong>Case ID:</strong> {{case_id}}</li>
<li><strong>Infringement URL:</strong> <a href="{{infringement_url}}">{{infringement_url}}</a></li>
<li><strong>Platform:</strong> {{platform}}</li>
<li><strong>Similarity Score:</strong> {{similarity_score}}%</li>
<li><strong>Priority:</strong> {{priority}}</li>
</ul>
<p>The case has been assigned for review and enforcement actions will begin automatically.</p>
<p><em>This is an automated notification from IA Influencer Agent Content Protection System.</em></p>
""",
                variables={"case_id", "infringement_url", "platform", "similarity_score", "priority"}
            ),
            NotificationTemplate(
                id="escalation_created_email",
                notification_type=NotificationType.ESCALATION_CREATED,
                channel=NotificationChannel.EMAIL,
                subject_template="Case Escalated - {{case_id}} ({{escalation_level}})",
                body_template="""A copyright enforcement case has been escalated and requires attention.

Case ID: {{case_id}}
Escalation Level: {{escalation_level}}
Triggered By: {{trigger_reason}}
Deadline: {{deadline}}
Assigned To: {{assigned_to}}

Please review the case and take appropriate action.

View case details: {{case_url}}

This is an automated notification from IA Influencer Agent Content Protection System.
""",
                variables={"case_id", "escalation_level", "trigger_reason", "deadline", "assigned_to", "case_url"}
            ),
            NotificationTemplate(
                id="deadline_warning_email",
                notification_type=NotificationType.DEADLINE_WARNING,
                channel=NotificationChannel.EMAIL,
                subject_template="⚠️ Case Deadline Approaching - {{case_id}}",
                body_template="""WARNING: A case deadline is approaching and requires immediate attention.

Case ID: {{case_id}}
Current Status: {{status}}
Deadline: {{deadline}}
Time Remaining: {{time_remaining}}
Assigned To: {{assigned_to}}

Please take action before the deadline expires to avoid automatic escalation.

View case details: {{case_url}}

This is an automated notification from IA Influencer Agent Content Protection System.
""",
                variables={"case_id", "status", "deadline", "time_remaining", "assigned_to", "case_url"}
            ),
            NotificationTemplate(
                id="document_generated_email",
                notification_type=NotificationType.DOCUMENT_GENERATED,
                channel=NotificationChannel.EMAIL,
                subject_template="Legal Document Generated - {{document_type}} for {{case_id}}",
                body_template="""A legal document has been generated for your review.

Case ID: {{case_id}}
Document Type: {{document_type}}
Document ID: {{document_id}}
Status: {{status}}
Generated: {{generation_time}}

{% if requires_review %}
This document requires review before sending. Please review and approve.
{% endif %}

View document: {{document_url}}

This is an automated notification from IA Influencer Agent Content Protection System.
""",
                variables={"case_id", "document_type", "document_id", "status", "generation_time", "requires_review", "document_url"}
            ),
            NotificationTemplate(
                id="alert_critical_slack",
                notification_type=NotificationType.ALERT_CRITICAL,
                channel=NotificationChannel.SLACK,
                subject_template="🚨 CRITICAL ALERT: {{alert_title}}",
                body_template="""*CRITICAL ALERT*

{{alert_description}}

*Metric:* {{metric_name}}
*Value:* {{metric_value}}
*Threshold:* {{threshold}}
*Severity:* {{severity}}

Immediate attention required!
""",
                variables={"alert_title", "alert_description", "metric_name", "metric_value", "threshold", "severity"}
            )
        ]
        
        for template in default_templates:
            self.templates[template.id] = template
    
    async def add_recipient(self, recipient: NotificationRecipient):
        """Add notification recipient"""
        self.recipients[recipient.id] = recipient
        logger.info(f"Added notification recipient: {recipient.name} ({recipient.id})")
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        recipient_id: str,
        context_data: Dict[str, Any],
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channels: Optional[List[NotificationChannel]] = None,
        case_id: Optional[str] = None
    ) -> List[str]:
        """Send notification to recipient"""
        try:
            recipient = self.recipients.get(recipient_id)
            if not recipient:
                logger.error(f"Recipient not found: {recipient_id}")
                return []
            
            if not recipient.enabled:
                logger.debug(f"Notifications disabled for recipient: {recipient_id}")
                return []
            
            # Check if recipient is subscribed to this notification type
            if recipient.subscribed_types and notification_type not in recipient.subscribed_types:
                logger.debug(f"Recipient {recipient_id} not subscribed to {notification_type.value}")
                return []
            
            # Check priority threshold
            priority_levels = [NotificationPriority.LOW, NotificationPriority.NORMAL, 
                             NotificationPriority.HIGH, NotificationPriority.URGENT, 
                             NotificationPriority.CRITICAL]
            
            if priority_levels.index(priority) < priority_levels.index(recipient.minimum_priority):
                logger.debug(f"Notification priority {priority.value} below threshold for {recipient_id}")
                return []
            
            # Determine channels to use
            if not channels:
                channels = recipient.preferred_channels
            
            message_ids = []
            
            # Create and queue messages for each channel
            for channel in channels:
                message = await self._create_message(
                    notification_type=notification_type,
                    recipient=recipient,
                    channel=channel,
                    priority=priority,
                    context_data=context_data,
                    case_id=case_id
                )
                
                if message:
                    await self._queue_message(message)
                    message_ids.append(message.id)
            
            logger.info(f"Queued {len(message_ids)} notifications for {recipient_id}")
            return message_ids
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return []
    
    async def _create_message(
        self,
        notification_type: NotificationType,
        recipient: NotificationRecipient,
        channel: NotificationChannel,
        priority: NotificationPriority,
        context_data: Dict[str, Any],
        case_id: Optional[str] = None
    ) -> Optional[NotificationMessage]:
        """Create notification message from template"""
        try:
            # Find appropriate template
            template_id = f"{notification_type.value}_{channel.value}"
            template = self.templates.get(template_id)
            
            if not template:
                # Try generic template
                template = self.templates.get(f"{notification_type.value}_email")
            
            if not template:
                logger.warning(f"No template found for {notification_type.value} on {channel.value}")
                return None
            
            # Render template content
            from jinja2 import Template
            
            subject_template = Template(template.subject_template)
            body_template = Template(template.body_template)
            
            subject = subject_template.render(**context_data)
            body = body_template.render(**context_data)
            
            html_body = None
            if template.html_template:
                html_template = Template(template.html_template)
                html_body = html_template.render(**context_data)
            
            # Create message
            message_id = f"MSG-{notification_type.value}-{recipient.id}-{int(datetime.utcnow().timestamp())}"
            
            message = NotificationMessage(
                id=message_id,
                notification_type=notification_type,
                recipient=recipient,
                channel=channel,
                priority=priority,
                subject=subject,
                body=body,
                html_body=html_body,
                case_id=case_id,
                context_data=context_data
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            return None
    
    async def _queue_message(self, message: NotificationMessage):
        """Add message to processing queue"""
        try:
            # Check queue size limit
            if len(self.message_queue) >= self.max_queue_size:
                # Remove oldest message
                oldest_message = min(self.message_queue, key=lambda m: m.created_at)
                self.message_queue.remove(oldest_message)
                logger.warning("Message queue full, removed oldest message")
            
            self.message_queue.append(message)
            
            # Start processing if not already running
            if not self.processing:
                await self.start_processing()
            
        except Exception as e:
            logger.error(f"Error queuing message: {e}")
    
    async def start_processing(self):
        """Start message queue processing"""
        if self.processing:
            return
        
        self.processing = True
        self.processing_task = asyncio.create_task(self._process_queue())
        logger.info("Started notification queue processing")
    
    async def stop_processing(self):
        """Stop message queue processing"""
        self.processing = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped notification queue processing")
    
    async def _process_queue(self):
        """Process notification message queue"""
        while self.processing:
            try:
                if not self.message_queue:
                    await asyncio.sleep(self.queue_processing_interval)
                    continue
                
                # Process messages in priority order
                self.message_queue.sort(key=lambda m: (
                    [NotificationPriority.LOW, NotificationPriority.NORMAL, 
                     NotificationPriority.HIGH, NotificationPriority.URGENT, 
                     NotificationPriority.CRITICAL].index(m.priority),
                    m.created_at
                ), reverse=True)
                
                # Process batch of messages
                batch_size = 10
                batch = self.message_queue[:batch_size]
                self.message_queue = self.message_queue[batch_size:]
                
                # Send messages concurrently
                tasks = [self._send_message(message) for message in batch]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                await asyncio.sleep(1)  # Brief pause between batches
                
            except Exception as e:
                logger.error(f"Error processing notification queue: {e}")
                await asyncio.sleep(5)
    
    async def _send_message(self, message: NotificationMessage):
        """Send individual message"""
        try:
            # Check rate limiting
            if self.enable_rate_limiting and not self._check_rate_limit(message):
                # Re-queue for later
                await asyncio.sleep(60)  # Wait 1 minute
                await self._queue_message(message)
                return
            
            # Update message status
            message.status = NotificationStatus.PENDING
            
            # Send based on channel
            success = False
            
            if message.channel == NotificationChannel.EMAIL and self.email_provider:
                success = await self.email_provider.send_email(message)
            elif message.channel == NotificationChannel.WEBHOOK and self.webhook_provider:
                success = await self.webhook_provider.send_webhook(message)
            elif message.channel == NotificationChannel.SLACK and self.slack_provider:
                success = await self.slack_provider.send_slack_message(message)
            else:
                logger.warning(f"No provider available for channel {message.channel.value}")
                message.error_message = f"No provider for {message.channel.value}"
            
            # Update message status
            if success:
                message.status = NotificationStatus.SENT
                message.sent_at = datetime.utcnow()
                logger.debug(f"Message sent successfully: {message.id}")
            else:
                message.status = NotificationStatus.FAILED
                message.retry_count += 1
                
                # Retry if below max retries
                if message.retry_count < message.max_retries:
                    # Exponential backoff
                    delay = min(300, 30 * (2 ** message.retry_count))  # Max 5 minutes
                    await asyncio.sleep(delay)
                    await self._queue_message(message)
                    logger.info(f"Retrying message {message.id} (attempt {message.retry_count + 1})")
                else:
                    logger.error(f"Message failed after {message.max_retries} retries: {message.id}")
            
            # Store sent message
            self.sent_messages[message.id] = message
            
        except Exception as e:
            logger.error(f"Error sending message {message.id}: {e}")
            message.status = NotificationStatus.FAILED
            message.error_message = str(e)
            self.sent_messages[message.id] = message
    
    def _check_rate_limit(self, message: NotificationMessage) -> bool:
        """Check if message can be sent within rate limits"""
        try:
            channel = message.channel
            recipient_id = message.recipient.id
            rate_key = f"{channel.value}_{recipient_id}"
            
            now = datetime.utcnow()
            hour_ago = now - timedelta(hours=1)
            
            # Get recent sends for this channel/recipient
            if rate_key not in self.rate_tracking:
                self.rate_tracking[rate_key] = []
            
            recent_sends = self.rate_tracking[rate_key]
            
            # Remove old entries
            recent_sends = [send_time for send_time in recent_sends if send_time > hour_ago]
            self.rate_tracking[rate_key] = recent_sends
            
            # Check limit
            limit = self.rate_limits.get(channel, 100)
            if len(recent_sends) >= limit:
                logger.warning(f"Rate limit exceeded for {rate_key}: {len(recent_sends)}/{limit}")
                return False
            
            # Add current send
            recent_sends.append(now)
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow send on error
    
    async def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get status of sent message"""
        try:
            message = self.sent_messages.get(message_id)
            if not message:
                return None
            
            return {
                'id': message.id,
                'type': message.notification_type.value,
                'channel': message.channel.value,
                'recipient': message.recipient.name,
                'status': message.status.value,
                'priority': message.priority.value,
                'created_at': message.created_at.isoformat(),
                'sent_at': message.sent_at.isoformat() if message.sent_at else None,
                'delivered_at': message.delivered_at.isoformat() if message.delivered_at else None,
                'read_at': message.read_at.isoformat() if message.read_at else None,
                'retry_count': message.retry_count,
                'error_message': message.error_message,
                'tracking_id': message.tracking_id
            }
            
        except Exception as e:
            logger.error(f"Error getting message status: {e}")
            return None
    
    async def mark_message_delivered(self, message_id: str):
        """Mark message as delivered"""
        message = self.sent_messages.get(message_id)
        if message:
            message.status = NotificationStatus.DELIVERED
            message.delivered_at = datetime.utcnow()
    
    async def mark_message_read(self, message_id: str):
        """
Mark message as read"""
        message = self.sent_messages.get(message_id)
        if message:
            message.status = NotificationStatus.READ
            message.read_at = datetime.utcnow()
    
    async def get_notification_statistics(self) -> Dict[str, Any]:
        """
Get notification service statistics"""
        try:
            stats = {
                'queue_size': len(self.message_queue),
                'total_sent': len(self.sent_messages),
                'processing': self.processing,
                'recipients': len(self.recipients),
                'templates': len(self.templates),
                'by_status': {},
                'by_channel': {},
                'by_priority': {},
                'by_type': {}
            }
            
            # Analyze sent messages
            for message in self.sent_messages.values():
                status = message.status.value
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                channel = message.channel.value
                stats['by_channel'][channel] = stats['by_channel'].get(channel, 0) + 1
                
                priority = message.priority.value
                stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
                
                msg_type = message.notification_type.value
                stats['by_type'][msg_type] = stats['by_type'].get(msg_type, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting notification statistics: {e}")
            return {}
    
    async def cleanup_old_messages(self):
        """Clean up old messages"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.message_retention_days)
            
            # Clean up sent messages
            old_message_ids = [
                msg_id for msg_id, message in self.sent_messages.items()
                if message.created_at < cutoff_date
            ]
            
            for msg_id in old_message_ids:
                del self.sent_messages[msg_id]
            
            # Clean up rate tracking
            hour_ago = datetime.utcnow() - timedelta(hours=1)
            for rate_key in list(self.rate_tracking.keys()):
                self.rate_tracking[rate_key] = [
                    send_time for send_time in self.rate_tracking[rate_key]
                    if send_time > hour_ago
                ]
                
                if not self.rate_tracking[rate_key]:
                    del self.rate_tracking[rate_key]
            
            logger.info(f"Cleaned up {len(old_message_ids)} old messages")
            
        except Exception as e:
            logger.error(f"Error cleaning up old messages: {e}")
    
    async def shutdown(self):
        """Shutdown notification service"""
        try:
            await self.stop_processing()
            
            # Process remaining messages in queue
            if self.message_queue:
                logger.info(f"Processing {len(self.message_queue)} remaining messages")
                tasks = [self._send_message(message) for message in self.message_queue]
                await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info("Notification service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error shutting down notification service: {e}")


# Global instance
notification_service = NotificationService()


async def get_notification_service() -> NotificationService:
    """Get the global notification service instance"""
    return notification_service


__all__ = [
    'NotificationService',
    'NotificationMessage',
    'NotificationRecipient',
    'NotificationTemplate',
    'NotificationType',
    'NotificationPriority',
    'NotificationChannel',
    'NotificationStatus',
    'EmailProvider',
    'WebhookProvider',
    'SlackProvider',
    'get_notification_service'
]
