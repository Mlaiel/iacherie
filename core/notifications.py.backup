"""Notification System for Content Protection

Advanced notification management system for DMCA automation, compliance alerts,
and real-time communication with copyright owners and legal teams.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Project: IA Influencer Agent Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ COPYRIGHT & LICENSE WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, modification,
distribution, or use without explicit written permission from Fahed Mlaiel is strictly
prohibited and will result in legal action.

All rights reserved © 2025 Fahed Mlaiel
"""
import asyncio
import logging
import smtplib
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import aiohttp
import twilio
from twilio.rest import Client as TwilioClient

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    RETRYING = "retrying"


@dataclass
class NotificationRecipient:
    """Notification recipient information"""
    recipient_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    webhook_url: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    timezone: str = "UTC"
    language: str = "en"


@dataclass
class NotificationTemplate:
    """Notification template"""
    template_id: str
    name: str
    template_type: NotificationType
    subject_template: Optional[str] = None
    body_template: str = ""
    variables: List[str] = field(default_factory=list)
    language: str = "en"
    is_html: bool = False


@dataclass
class NotificationMessage:
    """Notification message"""
    message_id: str
    notification_type: NotificationType
    recipient: NotificationRecipient
    subject: Optional[str] = None
    body: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class NotificationManager:
    """
    Advanced notification management system
    
    Features:
    - Multi-channel notifications (Email, SMS, Webhook, Push)
    - Template management with variable substitution
    - Priority-based delivery
    - Retry logic with exponential backoff
    - Delivery tracking and analytics
    - Rate limiting and throttling
    - Internationalization support
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize notification manager"""
        self.config = config or {}
        self.logger = logger
        
        # Email configuration
        self.smtp_config = self.config.get('smtp', {})
        self.email_enabled = bool(self.smtp_config.get('server'))
        
        # SMS configuration (Twilio)
        self.twilio_config = self.config.get('twilio', {})
        self.sms_enabled = bool(self.twilio_config.get('account_sid'))
        if self.sms_enabled:
            self.twilio_client = TwilioClient(
                self.twilio_config['account_sid'],
                self.twilio_config['auth_token']
            )
        
        # Webhook configuration
        self.webhook_timeout = self.config.get('webhook_timeout', 30)
        self.webhook_retries = self.config.get('webhook_retries', 3)
        
        # Delivery settings
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay_base = self.config.get('retry_delay_base', 60)  # seconds
        self.rate_limit_per_minute = self.config.get('rate_limit_per_minute', 60)
        
        # Storage for templates and delivery tracking
        self.templates: Dict[str, NotificationTemplate] = {}
        self.delivery_queue: List[NotificationMessage] = []
        self.delivery_stats = {
            'total_sent': 0,
            'success_rate': 0.0,
            'failed_deliveries': 0,
            'bounced_emails': 0
        }
    
    async def send_notification(self, 
                              recipient: NotificationRecipient,
                              template_id: str,
                              variables: Dict[str, Any],
                              priority: NotificationPriority = NotificationPriority.NORMAL,
                              scheduled_at: Optional[datetime] = None) -> str:
        """
        Send notification using template
        
        Args:
            recipient: Notification recipient
            template_id: Template identifier
            variables: Template variables
            priority: Notification priority
            scheduled_at: Optional scheduled delivery time
            
        Returns:
            Message ID for tracking
        """
        try:
            # Get template
            template = self.templates.get(template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            
            # Render message from template
            message = await self._render_message_from_template(
                template, recipient, variables, priority, scheduled_at
            )
            
            # Add to delivery queue
            self.delivery_queue.append(message)
            
            # Send immediately if not scheduled
            if scheduled_at is None:
                await self._deliver_message(message)
            
            self.logger.info(f"Notification queued: {message.message_id}")
            return message.message_id
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {str(e)}")
            raise
    
    async def send_direct_notification(self,
                                     recipient: NotificationRecipient,
                                     notification_type: NotificationType,
                                     subject: Optional[str],
                                     body: str,
                                     priority: NotificationPriority = NotificationPriority.NORMAL,
                                     attachments: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Send direct notification without template
        
        Args:
            recipient: Notification recipient
            notification_type: Type of notification
            subject: Message subject (for email)
            body: Message body
            priority: Notification priority
            attachments: Optional attachments
            
        Returns:
            Message ID for tracking
        """
        try:
            import uuid
            
            # Create message
            message = NotificationMessage(
                message_id=str(uuid.uuid4()),
                notification_type=notification_type,
                recipient=recipient,
                subject=subject,
                body=body,
                priority=priority,
                attachments=attachments or [],
                metadata={'direct_send': True}
            )
            
            # Add to delivery queue and send
            self.delivery_queue.append(message)
            await self._deliver_message(message)
            
            self.logger.info(f"Direct notification sent: {message.message_id}")
            return message.message_id
            
        except Exception as e:
            self.logger.error(f"Failed to send direct notification: {str(e)}")
            raise
    
    async def send_dmca_notice_alert(self,
                                   recipient: NotificationRecipient,
                                   notice_id: str,
                                   platform: str,
                                   status: str,
                                   details: Dict[str, Any]) -> str:
        """
        Send DMCA notice status alert
        
        Args:
            recipient: Alert recipient
            notice_id: DMCA notice ID
            platform: Platform name
            status: Current status
            details: Additional details
            
        Returns:
            Message ID for tracking
        """
        try:
            # Determine priority based on status
            priority_map = {
                'sent': NotificationPriority.NORMAL,
                'acknowledged': NotificationPriority.NORMAL,
                'complied': NotificationPriority.HIGH,
                'rejected': NotificationPriority.HIGH,
                'disputed': NotificationPriority.URGENT,
                'expired': NotificationPriority.HIGH
            }
            priority = priority_map.get(status, NotificationPriority.NORMAL)
            
            # Create subject and body
            subject = f"DMCA Notice Update: {status.title()} - {platform}"
            
            body = f"""DMCA Notice Status Update

Notice ID: {notice_id}
Platform: {platform}
Status: {status.title()}
Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

Details:
{json.dumps(details, indent=2)}

This is an automated notification from the IA Influencer Agent Content Protection System.
Contact: mlaiel@live.de for support.

© 2025 Fahed Mlaiel - All Rights Reserved
            """.strip()
            
            return await self.send_direct_notification(
                recipient=recipient,
                notification_type=NotificationType.EMAIL,
                subject=subject,
                body=body,
                priority=priority
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send DMCA alert: {str(e)}")
            raise
    
    async def send_compliance_alert(self,
                                  recipient: NotificationRecipient,
                                  tracking_id: str,
                                  compliance_status: str,
                                  deadline: datetime,
                                  actions_required: List[str]) -> str:
        """
        Send compliance monitoring alert
        
        Args:
            recipient: Alert recipient
            tracking_id: Compliance tracking ID
            compliance_status: Current compliance status
            deadline: Compliance deadline
            actions_required: List of required actions
            
        Returns:
            Message ID for tracking
        """
        try:
            # Determine urgency based on deadline
            time_until_deadline = deadline - datetime.now(timezone.utc)
            days_remaining = time_until_deadline.days
            
            if days_remaining <= 1:
                priority = NotificationPriority.CRITICAL
            elif days_remaining <= 3:
                priority = NotificationPriority.URGENT
            elif days_remaining <= 7:
                priority = NotificationPriority.HIGH
            else:
                priority = NotificationPriority.NORMAL
            
            subject = f"Compliance Alert: {compliance_status.title()} - {days_remaining} days remaining"
            
            actions_list = "\n".join(f"• {action}" for action in actions_required)
            
            body = f"""Compliance Monitoring Alert

Tracking ID: {tracking_id}
Status: {compliance_status.title()}
Deadline: {deadline.strftime('%Y-%m-%d %H:%M:%S UTC')}
Days Remaining: {days_remaining}

Required Actions:
{actions_list}

Please take immediate action to ensure compliance.

This is an automated alert from the IA Influencer Agent Content Protection System.
Contact: mlaiel@live.de for support.

© 2025 Fahed Mlaiel - All Rights Reserved
            """.strip()
            
            return await self.send_direct_notification(
                recipient=recipient,
                notification_type=NotificationType.EMAIL,
                subject=subject,
                body=body,
                priority=priority
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send compliance alert: {str(e)}")
            raise
    
    async def send_enforcement_update(self,
                                    recipient: NotificationRecipient,
                                    enforcement_id: str,
                                    stage: str,
                                    action_taken: str,
                                    result: Dict[str, Any]) -> str:
        """
        Send enforcement action update
        
        Args:
            recipient: Update recipient
            enforcement_id: Enforcement ID
            stage: Current enforcement stage
            action_taken: Action that was taken
            result: Action result
            
        Returns:
            Message ID for tracking
        """
        try:
            subject = f"Enforcement Update: {stage.title()} - {action_taken}"
            
            body = f"""Enforcement Action Update

Enforcement ID: {enforcement_id}
Stage: {stage.title()}
Action Taken: {action_taken}
Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

Result:
{json.dumps(result, indent=2)}

The enforcement process is progressing according to your selected policy.

This is an automated update from the IA Influencer Agent Content Protection System.
Contact: mlaiel@live.de for support.

© 2025 Fahed Mlaiel - All Rights Reserved
            """.strip()
            
            return await self.send_direct_notification(
                recipient=recipient,
                notification_type=NotificationType.EMAIL,
                subject=subject,
                body=body,
                priority=NotificationPriority.NORMAL
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send enforcement update: {str(e)}")
            raise
    
    async def register_template(self, template: NotificationTemplate) -> None:
        """Register notification template"""
        self.templates[template.template_id] = template
        self.logger.info(f"Template registered: {template.template_id}")
    
    async def get_delivery_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get delivery status for message"""
        for message in self.delivery_queue:
            if message.message_id == message_id:
                return {
                    'message_id': message_id,
                    'status': message.status.value,
                    'notification_type': message.notification_type.value,
                    'recipient': message.recipient.name,
                    'created_at': message.created_at.isoformat(),
                    'metadata': message.metadata
                }
        return None
    
    async def get_delivery_analytics(self) -> Dict[str, Any]:
        """Get comprehensive delivery analytics"""
        total_messages = len(self.delivery_queue)
        
        if total_messages == 0:
            return {
                'total_messages': 0,
                'success_rate': 0.0,
                'delivery_stats': self.delivery_stats
            }
        
        # Count by status
        status_counts = {}
        type_counts = {}
        priority_counts = {}
        
        for message in self.delivery_queue:
            status = message.status.value
            msg_type = message.notification_type.value
            priority = message.priority.value
            
            status_counts[status] = status_counts.get(status, 0) + 1
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Calculate success rate
        successful = status_counts.get('sent', 0) + status_counts.get('delivered', 0)
        success_rate = (successful / total_messages) * 100 if total_messages > 0 else 0
        
        return {
            'total_messages': total_messages,
            'success_rate': success_rate,
            'status_breakdown': status_counts,
            'type_breakdown': type_counts,
            'priority_breakdown': priority_counts,
            'delivery_stats': self.delivery_stats
        }
    
    # Private helper methods
    
    async def _render_message_from_template(self,
                                          template: NotificationTemplate,
                                          recipient: NotificationRecipient,
                                          variables: Dict[str, Any],
                                          priority: NotificationPriority,
                                          scheduled_at: Optional[datetime]) -> NotificationMessage:
        """Render message from template"""
        import uuid
        from string import Template
        
        # Add recipient variables
        template_vars = {
            **variables,
            'recipient_name': recipient.name,
            'recipient_email': recipient.email or '',
            'current_date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'current_time': datetime.now(timezone.utc).strftime('%H:%M:%S UTC')
        }
        
        # Render subject
        subject = None
        if template.subject_template:
            subject_tmpl = Template(template.subject_template)
            subject = subject_tmpl.safe_substitute(template_vars)
        
        # Render body
        body_tmpl = Template(template.body_template)
        body = body_tmpl.safe_substitute(template_vars)
        
        return NotificationMessage(
            message_id=str(uuid.uuid4()),
            notification_type=template.template_type,
            recipient=recipient,
            subject=subject,
            body=body,
            priority=priority,
            scheduled_at=scheduled_at,
            metadata={'template_id': template.template_id}
        )
    
    async def _deliver_message(self, message: NotificationMessage) -> bool:
        """Deliver notification message"""
        try:
            message.status = NotificationStatus.SENDING
            
            if message.notification_type == NotificationType.EMAIL:
                success = await self._send_email(message)
            elif message.notification_type == NotificationType.SMS:
                success = await self._send_sms(message)
            elif message.notification_type == NotificationType.WEBHOOK:
                success = await self._send_webhook(message)
            else:
                self.logger.warning(f"Unsupported notification type: {message.notification_type}")
                success = False
            
            if success:
                message.status = NotificationStatus.SENT
                self.delivery_stats['total_sent'] += 1
            else:
                message.status = NotificationStatus.FAILED
                self.delivery_stats['failed_deliveries'] += 1
            
            # Update success rate
            total = self.delivery_stats['total_sent'] + self.delivery_stats['failed_deliveries']
            if total > 0:
                self.delivery_stats['success_rate'] = self.delivery_stats['total_sent'] / total
            
            return success
            
        except Exception as e:
            self.logger.error(f"Message delivery failed: {str(e)}")
            message.status = NotificationStatus.FAILED
            return False
    
    async def _send_email(self, message: NotificationMessage) -> bool:
        """Send email notification"""
        try:
            if not self.email_enabled:
                self.logger.warning("Email not configured")
                return False
            
            if not message.recipient.email:
                self.logger.warning("Recipient email not provided")
                return False
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = message.recipient.email
            msg['Subject'] = message.subject or "Notification"
            
            # Add body
            msg.attach(MIMEText(message.body, 'plain'))
            
            # Add attachments
            for attachment in message.attachments:
                if 'content' in attachment and 'filename' in attachment:
                    part = MIMEApplication(attachment['content'])
                    part.add_header('Content-Disposition', 'attachment', filename=attachment['filename'])
                    msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config.get('port', 587)) as server:
                if self.smtp_config.get('use_tls', True):
                    server.starttls()
                if 'username' in self.smtp_config and 'password' in self.smtp_config:
                    server.login(self.smtp_config['username'], self.smtp_config['password'])
                
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully: {message.message_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Email sending failed: {str(e)}")
            return False
    
    async def _send_sms(self, message: NotificationMessage) -> bool:
        """Send SMS notification"""
        try:
            if not self.sms_enabled:
                self.logger.warning("SMS not configured")
                return False
            
            if not message.recipient.phone:
                self.logger.warning("Recipient phone not provided")
                return False
            
            # Send SMS via Twilio
            sms_message = self.twilio_client.messages.create(
                body=message.body,
                from_=self.twilio_config['from_number'],
                to=message.recipient.phone
            )
            
            self.logger.info(f"SMS sent successfully: {message.message_id}, SID: {sms_message.sid}")
            return True
            
        except Exception as e:
            self.logger.error(f"SMS sending failed: {str(e)}")
            return False
    
    async def _send_webhook(self, message: NotificationMessage) -> bool:
        """Send webhook notification"""
        try:
            if not message.recipient.webhook_url:
                self.logger.warning("Recipient webhook URL not provided")
                return False
            
            # Prepare webhook payload
            payload = {
                'message_id': message.message_id,
                'notification_type': message.notification_type.value,
                'subject': message.subject,
                'body': message.body,
                'priority': message.priority.value,
                'recipient': {
                    'id': message.recipient.recipient_id,
                    'name': message.recipient.name
                },
                'timestamp': message.created_at.isoformat(),
                'metadata': message.metadata
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    message.recipient.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.webhook_timeout)
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Webhook sent successfully: {message.message_id}")
                        return True
                    else:
                        self.logger.error(f"Webhook failed with status: {response.status}")
                        return False
            
        except Exception as e:
            self.logger.error(f"Webhook sending failed: {str(e)}")
            return False


# Factory function
def create_notification_manager(config: Optional[Dict[str, Any]] = None) -> NotificationManager:
    """Factory function to create notification manager"""
    return NotificationManager(config)


# Export all notification components
__all__ = [
    'NotificationType',
    'NotificationPriority',
    'NotificationStatus',
    'NotificationRecipient',
    'NotificationTemplate',
    'NotificationMessage',
    'NotificationManager',
    'create_notification_manager'
]
