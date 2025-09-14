"""💳 Payment Gateway Notifier
=============================

Enterprise notification system for real-time payment events with multi-channel
communication, delivery confirmation tracking, and notification preferences.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import jinja2
import uuid

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    SLACK = "slack"
    DISCORD = "discord"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    RETRYING = "retrying"


class PaymentEventType(Enum):
    """Payment event types for notifications"""
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_REFUNDED = "payment_refunded"
    PAYMENT_DISPUTED = "payment_disputed"
    FRAUD_DETECTED = "fraud_detected"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SYSTEM_ERROR = "system_error"
    MAINTENANCE_MODE = "maintenance_mode"
    PAYOUT_PROCESSED = "payout_processed"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"


@dataclass
class NotificationPreferences:
    """User notification preferences"""
    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    webhook_enabled: bool = False
    channels: Dict[PaymentEventType, List[NotificationChannel]] = field(default_factory=dict)
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None
    timezone: str = "UTC"


@dataclass
class NotificationTemplate:
    """Notification message template"""
    template_id: str
    event_type: PaymentEventType
    channel: NotificationChannel
    subject_template: str
    body_template: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationRequest:
    """Notification delivery request"""
    request_id: str
    user_id: str
    event_type: PaymentEventType
    channel: NotificationChannel
    recipient: str
    subject: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = None


@dataclass
class NotificationResult:
    """Notification delivery result"""
    request_id: str
    status: NotificationStatus
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    delivery_attempts: int = 0


class PaymentGatewayNotifier:
    """Enterprise payment gateway notification system"""

    def __init__(self) -> None:
        self.templates: Dict[str, NotificationTemplate] = {}
        self.preferences: Dict[str, NotificationPreferences] = {}
        
        # Email configuration
        self.smtp_config = {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': None,
            'password': None,
            'use_tls': True
        }
        
        # Webhook configuration
        self.webhook_timeout = 30
        self.webhook_retry_delay = [1, 5, 15, 60]  # seconds
        
        # Template engine
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader({}),
            autoescape=True
        )
        
        # Notification queue
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        self.delivery_workers: List[asyncio.Task] = []
        self.worker_count = 5
        
        # Delivery tracking
        self.delivery_results: Dict[str, NotificationResult] = {}
        
        # Default templates
        self._setup_default_templates()

    async def initialize(self) -> None:
        """Initialize notification system"""
        # Start delivery workers
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._delivery_worker(f"worker-{i}"))
            self.delivery_workers.append(worker)
        
        logger.info(f"Payment gateway notifier initialized with {self.worker_count} workers")

    async def send_payment_notification(self,
                                      user_id: str,
                                      event_type: PaymentEventType,
                                      context: Dict[str, Any],
                                      priority: NotificationPriority = NotificationPriority.NORMAL,
                                      channels: Optional[List[NotificationChannel]] = None) -> List[str]:
        """Send payment event notification"""
        
        # Get user preferences
        prefs = self.preferences.get(user_id, NotificationPreferences(user_id=user_id))
        
        # Determine channels to use
        if channels is None:
            channels = prefs.channels.get(event_type, [NotificationChannel.EMAIL])
        
        # Filter channels based on preferences
        enabled_channels = []
        for channel in channels:
            if self._is_channel_enabled(prefs, channel):
                enabled_channels.append(channel)
        
        if not enabled_channels:
            logger.warning(f"No enabled channels for user {user_id} and event {event_type}")
            return []
        
        # Generate notifications for each channel
        request_ids = []
        for channel in enabled_channels:
            request_id = await self._create_notification_request(
                user_id, event_type, channel, context, priority
            )
            if request_id:
                request_ids.append(request_id)
        
        return request_ids

    async def _create_notification_request(self,
                                         user_id: str,
                                         event_type: PaymentEventType,
                                         channel: NotificationChannel,
                                         context: Dict[str, Any],
                                         priority: NotificationPriority) -> Optional[str]:
        """Create notification request"""
        
        # Get template for event and channel
        template = self._get_template(event_type, channel)
        if not template:
            logger.warning(f"No template found for {event_type} on {channel}")
            return None
        
        # Get recipient information
        recipient = await self._get_recipient_info(user_id, channel)
        if not recipient:
            logger.warning(f"No recipient info for user {user_id} on channel {channel}")
            return None
        
        # Render message from template
        subject, message = await self._render_template(template, context)
        
        # Create notification request
        request = NotificationRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            event_type=event_type,
            channel=channel,
            recipient=recipient,
            subject=subject,
            message=message,
            priority=priority,
            metadata=context
        )
        
        # Check quiet hours
        if self._is_quiet_hours(user_id):
            request.scheduled_for = self._get_next_active_time(user_id)
        
        # Queue for delivery
        await self.notification_queue.put(request)
        
        return request.request_id

    async def _delivery_worker(self, worker_id -> None: str) -> None:
        """Notification delivery worker"""
        logger.info(f"Notification worker {worker_id} started")
        
        while True:
            try:
                # Get notification request
                request = await self.notification_queue.get()
                
                # Check if scheduled for later
                if request.scheduled_for and datetime.now() < request.scheduled_for:
                    # Re-queue for later
                    await asyncio.sleep(1)
                    await self.notification_queue.put(request)
                    continue
                
                # Deliver notification
                result = await self._deliver_notification(request)
                
                # Track result
                self.delivery_results[request.request_id] = result
                
                # Handle failed delivery
                if result.status == NotificationStatus.FAILED and request.retry_count < request.max_retries:
                    request.retry_count += 1
                    delay = min(300, 2 ** request.retry_count)  # Exponential backoff, max 5 minutes
                    await asyncio.sleep(delay)
                    await self.notification_queue.put(request)
                
                self.notification_queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

    async def _deliver_notification(self, request: NotificationRequest) -> NotificationResult:
        """Deliver single notification"""
        
        result = NotificationResult(
            request_id=request.request_id,
            status=NotificationStatus.PENDING,
            delivery_attempts=request.retry_count + 1
        )
        
        try:
            if request.channel == NotificationChannel.EMAIL:
                success = await self._send_email(request)
            elif request.channel == NotificationChannel.SMS:
                success = await self._send_sms(request)
            elif request.channel == NotificationChannel.WEBHOOK:
                success = await self._send_webhook(request)
            elif request.channel == NotificationChannel.PUSH:
                success = await self._send_push(request)
            elif request.channel == NotificationChannel.SLACK:
                success = await self._send_slack(request)
            elif request.channel == NotificationChannel.DISCORD:
                success = await self._send_discord(request)
            elif request.channel == NotificationChannel.IN_APP:
                success = await self._send_in_app(request)
            else:
                logger.warning(f"Unsupported channel: {request.channel}")
                success = False
            
            if success:
                result.status = NotificationStatus.SENT
                result.delivered_at = datetime.now()
            else:
                result.status = NotificationStatus.FAILED
                result.error_message = "Delivery failed"
            
        except Exception as e:
            logger.error(f"Notification delivery error: {e}")
            result.status = NotificationStatus.FAILED
            result.error_message = str(e)
        
        return result

    async def _send_email(self, request: NotificationRequest) -> bool:
        """Send email notification"""
        try:
            if not self.smtp_config['username'] or not self.smtp_config['password']:
                logger.warning("SMTP credentials not configured")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = request.recipient
            msg['Subject'] = request.subject
            
            msg.attach(MIMEText(request.message, 'html'))
            
            server = smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port'])
            if self.smtp_config['use_tls']:
                server.starttls()
            
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False

    async def _send_sms(self, request: NotificationRequest) -> bool:
        """Send SMS notification (placeholder implementation)"""
        # In real implementation, integrate with SMS provider like Twilio
        logger.info(f"SMS notification sent to {request.recipient}: {request.message}")
        return True

    async def _send_webhook(self, request: NotificationRequest) -> bool:
        """Send webhook notification"""
        try:
            payload = {
                'event_type': request.event_type.value,
                'user_id': request.user_id,
                'message': request.message,
                'metadata': request.metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.webhook_timeout)) as session:
                async with session.post(request.recipient, json=payload) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Webhook sending failed: {e}")
            return False

    async def _send_push(self, request: NotificationRequest) -> bool:
        """Send push notification (placeholder implementation)"""
        # In real implementation, integrate with push notification service
        logger.info(f"Push notification sent to {request.recipient}: {request.subject}")
        return True

    async def _send_slack(self, request: NotificationRequest) -> bool:
        """Send Slack notification"""
        try:
            payload = {
                'text': request.subject,
                'attachments': [{
                    'color': 'good' if 'completed' in request.event_type.value else 'warning',
                    'text': request.message,
                    'ts': datetime.now().timestamp()
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(request.recipient, json=payload) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False

    async def _send_discord(self, request: NotificationRequest) -> bool:
        """Send Discord notification"""
        try:
            payload = {
                'content': f"**{request.subject}**\n{request.message}",
                'embeds': [{
                    'title': request.subject,
                    'description': request.message,
                    'color': 0x00ff00 if 'completed' in request.event_type.value else 0xff9900,
                    'timestamp': datetime.now().isoformat()
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(request.recipient, json=payload) as response:
                    return response.status == 204
                    
        except Exception as e:
            logger.error(f"Discord notification failed: {e}")
            return False

    async def _send_in_app(self, request: NotificationRequest) -> bool:
        """Send in-app notification (placeholder implementation)"""
        # In real implementation, store in database for user's notification center
        logger.info(f"In-app notification created for user {request.user_id}: {request.subject}")
        return True

    def _get_template(self, event_type: PaymentEventType, channel: NotificationChannel) -> Optional[NotificationTemplate]:
        """Get notification template"""
        template_key = f"{event_type.value}_{channel.value}"
        return self.templates.get(template_key)

    async def _get_recipient_info(self, user_id: str, channel: NotificationChannel) -> Optional[str]:
        """Get recipient information for user and channel"""
        # In real implementation, this would query user database
        # For now, return placeholder data
        if channel == NotificationChannel.EMAIL:
            return f"user{user_id}@example.com"
        elif channel == NotificationChannel.SMS:
            return "+1234567890"
        elif channel == NotificationChannel.WEBHOOK:
            return f"https://api.example.com/webhooks/{user_id}"
        elif channel == NotificationChannel.SLACK:
            return "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
        elif channel == NotificationChannel.DISCORD:
            return "https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK"
        return None

    async def _render_template(self, template: NotificationTemplate, context: Dict[str, Any]) -> Tuple[str, str]:
        """Render notification template"""
        try:
            subject_template = self.jinja_env.from_string(template.subject_template)
            body_template = self.jinja_env.from_string(template.body_template)
            
            # Merge template variables with context
            render_context = {**template.variables, **context}
            
            subject = subject_template.render(render_context)
            message = body_template.render(render_context)
            
            return subject, message
            
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return template.subject_template, template.body_template

    def _is_channel_enabled(self, prefs: NotificationPreferences, channel: NotificationChannel) -> bool:
        """Check if notification channel is enabled for user"""
        if channel == NotificationChannel.EMAIL:
            return prefs.email_enabled
        elif channel == NotificationChannel.SMS:
            return prefs.sms_enabled
        elif channel == NotificationChannel.PUSH:
            return prefs.push_enabled
        elif channel == NotificationChannel.WEBHOOK:
            return prefs.webhook_enabled
        return True

    def _is_quiet_hours(self, user_id: str) -> bool:
        """Check if current time is in user's quiet hours"""
        prefs = self.preferences.get(user_id)
        if not prefs or not prefs.quiet_hours_start or not prefs.quiet_hours_end:
            return False
        
        # Simplified quiet hours check (ignores timezone for now)
        current_hour = datetime.now().hour
        return prefs.quiet_hours_start <= current_hour <= prefs.quiet_hours_end

    def _get_next_active_time(self, user_id: str) -> datetime:
        """Get next active time after quiet hours"""
        prefs = self.preferences.get(user_id)
        if not prefs or not prefs.quiet_hours_end:
            return datetime.now()
        
        # Schedule for end of quiet hours
        now = datetime.now()
        next_time = now.replace(hour=prefs.quiet_hours_end, minute=0, second=0, microsecond=0)
        
        if next_time <= now:
            next_time += timedelta(days=1)
        
        return next_time

    def _setup_default_templates(self) -> None:
        """Setup default notification templates"""
        
        # Payment completed template
        self.templates["payment_completed_email"] = NotificationTemplate(
            template_id="payment_completed_email",
            event_type=PaymentEventType.PAYMENT_COMPLETED,
            channel=NotificationChannel.EMAIL,
            subject_template="Payment Completed - Transaction {{ transaction_id }}",
            body_template="""
            <h2>Payment Successful</h2>
            <p>Your payment of {{ amount }} {{ currency }} has been successfully processed.</p>
            <p><strong>Transaction ID:</strong> {{ transaction_id }}</p>
            <p><strong>Date:</strong> {{ date }}</p>
            <p>Thank you for using our service!</p>
            """,
            priority=NotificationPriority.NORMAL
        )
        
        # Payment failed template
        self.templates["payment_failed_email"] = NotificationTemplate(
            template_id="payment_failed_email",
            event_type=PaymentEventType.PAYMENT_FAILED,
            channel=NotificationChannel.EMAIL,
            subject_template="Payment Failed - Transaction {{ transaction_id }}",
            body_template="""
            <h2>Payment Failed</h2>
            <p>Your payment of {{ amount }} {{ currency }} could not be processed.</p>
            <p><strong>Reason:</strong> {{ error_message }}</p>
            <p><strong>Transaction ID:</strong> {{ transaction_id }}</p>
            <p>Please try again or contact support if the issue persists.</p>
            """,
            priority=NotificationPriority.HIGH
        )
        
        # Fraud detected template
        self.templates["fraud_detected_email"] = NotificationTemplate(
            template_id="fraud_detected_email",
            event_type=PaymentEventType.FRAUD_DETECTED,
            channel=NotificationChannel.EMAIL,
            subject_template="Security Alert - Suspicious Activity Detected",
            body_template="""
            <h2>Security Alert</h2>
            <p>We detected suspicious activity on your account.</p>
            <p><strong>Transaction ID:</strong> {{ transaction_id }}</p>
            <p><strong>Amount:</strong> {{ amount }} {{ currency }}</p>
            <p>If this was not you, please contact our security team immediately.</p>
            """,
            priority=NotificationPriority.CRITICAL
        )

    async def set_user_preferences(self, user_id -> None: str, preferences -> None: NotificationPreferences) -> None:
        """Set notification preferences for user"""
        self.preferences[user_id] = preferences

    async def get_delivery_status(self, request_id: str) -> Optional[NotificationResult]:
        """Get delivery status for notification request"""
        return self.delivery_results.get(request_id)

    async def get_delivery_stats(self) -> Dict[str, Any]:
        """Get notification delivery statistics"""
        total = len(self.delivery_results)
        if total == 0:
            return {'total': 0, 'success_rate': 0}
        
        successful = sum(1 for result in self.delivery_results.values() 
                        if result.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED])
        
        failed = sum(1 for result in self.delivery_results.values() 
                    if result.status == NotificationStatus.FAILED)
        
        pending = sum(1 for result in self.delivery_results.values() 
                     if result.status == NotificationStatus.PENDING)
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'pending': pending,
            'success_rate': successful / total,
            'queue_size': self.notification_queue.qsize(),
            'active_workers': len(self.delivery_workers)
        }

    async def cleanup(self) -> None:
        """Cleanup notification system"""
        # Cancel all workers
        for worker in self.delivery_workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.delivery_workers, return_exceptions=True)
        
        logger.info("Payment gateway notifier cleanup completed")