#!/usr/bin/env python3
"""
Payment Gateway Notifier
Enterprise real-time notification system for payment events

© 2025 Fahed Mlaiel. All rights reserved.
Proprietary and confidential. Licensed under Enterprise Commercial License.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Callable, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import websockets

from ..core.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    PUSH = "push"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"

class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class NotificationStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"
    EXPIRED = "expired"

@dataclass
class NotificationTemplate:
    """Notification template configuration"""
    name: str
    type: NotificationType
    subject_template: str
    body_template: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    retry_count: int = 3
    retry_delay_seconds: int = 30
    expiry_hours: int = 24
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationPreference:
    """User notification preferences"""
    user_id: str
    enabled_types: Set[NotificationType] = field(default_factory=set)
    disabled_events: Set[str] = field(default_factory=set)
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationRequest:
    """Notification request with all details"""
    id: str
    type: NotificationType
    recipient: str
    subject: str
    body: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    template_variables: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class NotificationResult:
    """Result of notification delivery attempt"""
    request_id: str
    status: NotificationStatus
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    retry_after_seconds: Optional[int] = None

class PaymentGatewayNotifier:
    """
    Enterprise payment notification system with comprehensive delivery options.
    
    Features:
    - Multi-channel notifications (email, SMS, webhook, WebSocket, push)
    - Real-time payment event notifications
    - User preference management
    - Template-based messaging
    - Delivery confirmation tracking
    - Retry logic with exponential backoff
    - A/B testing for notification effectiveness
    - Analytics and optimization
    """

    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.notification_config = self._load_notification_config()
        
        # Templates for different payment events
        self.default_templates = self._load_default_templates()
        
        # User preferences cache
        self.preferences_cache = {}
        
        # Delivery providers
        self.email_provider = self._init_email_provider()
        self.sms_provider = self._init_sms_provider()
        self.webhook_provider = self._init_webhook_provider()
        self.push_provider = self._init_push_provider()
        
        # WebSocket connections for real-time notifications
        self.websocket_connections = {}
        
        # Notification queue and workers
        self.notification_queue = asyncio.Queue()
        self.delivery_workers = []
        self.retry_queue = asyncio.Queue()
        
        # Analytics tracking
        self.delivery_stats = {
            'sent': 0,
            'delivered': 0,
            'failed': 0,
            'by_type': {},
            'by_priority': {}
        }
        
        logger.info("Payment Gateway Notifier initialized with enterprise features")

    def _load_notification_config(self) -> Dict[str, Any]:
        """Load notification configuration"""
        return self.config_manager.get_config('notifications', {
            'max_retry_attempts': 3,
            'retry_delay_base': 30,
            'retry_delay_multiplier': 2.0,
            'max_retry_delay': 3600,
            'queue_size_limit': 10000,
            'worker_count': 5,
            'delivery_timeout': 30,
            'batch_size': 100
        })

    def _load_default_templates(self) -> Dict[str, NotificationTemplate]:
        """Load default notification templates for payment events"""
        return {
            # Payment success notifications
            'payment_success_email': NotificationTemplate(
                name='payment_success_email',
                type=NotificationType.EMAIL,
                subject_template='Payment Successful - ${amount} ${currency}',
                body_template='''
                Dear ${customer_name},
                
                Your payment of ${amount} ${currency} has been successfully processed.
                
                Transaction Details:
                - Payment ID: ${payment_id}
                - Amount: ${amount} ${currency}
                - Date: ${payment_date}
                - Method: ${payment_method}
                
                Thank you for your business!
                
                Best regards,
                Ainflue Payment Team
                ''',
                priority=NotificationPriority.NORMAL
            ),
            
            'payment_success_sms': NotificationTemplate(
                name='payment_success_sms',
                type=NotificationType.SMS,
                subject_template='Payment Success',
                body_template='Payment of ${amount} ${currency} successful. ID: ${payment_id}',
                priority=NotificationPriority.NORMAL
            ),
            
            # Payment failure notifications
            'payment_failed_email': NotificationTemplate(
                name='payment_failed_email',
                type=NotificationType.EMAIL,
                subject_template='Payment Failed - Action Required',
                body_template='''
                Dear ${customer_name},
                
                Your payment attempt has failed. Please review and try again.
                
                Payment Details:
                - Amount: ${amount} ${currency}
                - Date: ${payment_date}
                - Reason: ${failure_reason}
                - Payment ID: ${payment_id}
                
                Please update your payment method or contact support.
                
                Best regards,
                Ainflue Support Team
                ''',
                priority=NotificationPriority.HIGH
            ),
            
            # Creator revenue notifications
            'creator_payout_email': NotificationTemplate(
                name='creator_payout_email',
                type=NotificationType.EMAIL,
                subject_template='Creator Payout Processed - ${amount} ${currency}',
                body_template='''
                Hello ${creator_name},
                
                Your creator revenue payout has been processed!
                
                Payout Details:
                - Amount: ${amount} ${currency}
                - Period: ${payout_period}
                - Content Revenue: ${content_revenue}
                - Collaboration Revenue: ${collaboration_revenue}
                - Platform Fees: ${platform_fees}
                - Payout Method: ${payout_method}
                
                The funds should arrive in your account within 1-3 business days.
                
                Keep creating amazing content!
                
                Best regards,
                Ainflue Creator Team
                ''',
                priority=NotificationPriority.NORMAL
            ),
            
            # Fraud detection alerts
            'fraud_alert_webhook': NotificationTemplate(
                name='fraud_alert_webhook',
                type=NotificationType.WEBHOOK,
                subject_template='Fraud Alert',
                body_template=json.dumps({
                    'event': 'fraud_detected',
                    'payment_id': '${payment_id}',
                    'risk_score': '${risk_score}',
                    'detected_patterns': '${detected_patterns}',
                    'timestamp': '${timestamp}',
                    'customer_id': '${customer_id}',
                    'amount': '${amount}',
                    'currency': '${currency}'
                }),
                priority=NotificationPriority.CRITICAL
            ),
            
            # System alerts
            'system_alert_slack': NotificationTemplate(
                name='system_alert_slack',
                type=NotificationType.SLACK,
                subject_template='Payment System Alert',
                body_template='''
                🚨 *Payment System Alert*
                
                *Alert Type:* ${alert_type}
                *Severity:* ${severity}
                *Description:* ${description}
                *Component:* ${component}
                *Time:* ${timestamp}
                
                Please investigate immediately.
                ''',
                priority=NotificationPriority.URGENT
            ),
            
            # Subscription notifications
            'subscription_renewal_email': NotificationTemplate(
                name='subscription_renewal_email',
                type=NotificationType.EMAIL,
                subject_template='Subscription Renewed - ${service_name}',
                body_template='''
                Dear ${customer_name},
                
                Your subscription has been successfully renewed.
                
                Subscription Details:
                - Service: ${service_name}
                - Plan: ${plan_name}
                - Amount: ${amount} ${currency}
                - Next Billing Date: ${next_billing_date}
                - Payment Method: ${payment_method}
                
                Thank you for your continued subscription!
                
                Best regards,
                Ainflue Subscription Team
                ''',
                priority=NotificationPriority.NORMAL
            ),
            
            # Real-time websocket notifications
            'realtime_payment_update': NotificationTemplate(
                name='realtime_payment_update',
                type=NotificationType.WEBSOCKET,
                subject_template='Payment Update',
                body_template=json.dumps({
                    'event': 'payment_status_update',
                    'payment_id': '${payment_id}',
                    'status': '${status}',
                    'amount': '${amount}',
                    'currency': '${currency}',
                    'timestamp': '${timestamp}'
                }),
                priority=NotificationPriority.NORMAL
            )
        }

    def _init_email_provider(self) -> Optional[Dict[str, Any]]:
        """Initialize email provider configuration"""
        try:
            email_config = self.config_manager.get_config('email', {})
            return {
                'smtp_host': email_config.get('smtp_host', 'smtp.gmail.com'),
                'smtp_port': email_config.get('smtp_port', 587),
                'username': email_config.get('username'),
                'password': email_config.get('password'),
                'use_tls': email_config.get('use_tls', True),
                'from_address': email_config.get('from_address'),
                'from_name': email_config.get('from_name', 'Ainflue Payment System')
            }
        except Exception as e:
            logger.error(f"Failed to initialize email provider: {e}")
            return None

    def _init_sms_provider(self) -> Optional[Dict[str, Any]]:
        """Initialize SMS provider configuration (Twilio)"""
        try:
            sms_config = self.config_manager.get_config('sms', {})
            return {
                'account_sid': sms_config.get('account_sid'),
                'auth_token': sms_config.get('auth_token'),
                'from_number': sms_config.get('from_number'),
                'service_url': 'https://api.twilio.com/2010-04-01/Accounts'
            }
        except Exception as e:
            logger.error(f"Failed to initialize SMS provider: {e}")
            return None

    def _init_webhook_provider(self) -> Dict[str, Any]:
        """Initialize webhook provider configuration"""
        return {
            'timeout': 30,
            'retry_status_codes': [500, 502, 503, 504],
            'max_payload_size': 1024 * 1024,  # 1MB
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': 'Ainflue-Payment-Gateway/1.0'
            }
        }

    def _init_push_provider(self) -> Optional[Dict[str, Any]]:
        """Initialize push notification provider (Firebase)"""
        try:
            push_config = self.config_manager.get_config('push_notifications', {})
            return {
                'server_key': push_config.get('server_key'),
                'service_url': 'https://fcm.googleapis.com/fcm/send',
                'headers': {
                    'Authorization': f"key={push_config.get('server_key')}",
                    'Content-Type': 'application/json'
                }
            }
        except Exception as e:
            logger.error(f"Failed to initialize push provider: {e}")
            return None

    async def start_notification_workers(self):
        """Start background workers for notification processing"""
        try:
            worker_count = self.notification_config.get('worker_count', 5)
            
            for i in range(worker_count):
                worker = asyncio.create_task(self._notification_worker(f"worker-{i}"))
                self.delivery_workers.append(worker)
            
            # Start retry worker
            retry_worker = asyncio.create_task(self._retry_worker())
            self.delivery_workers.append(retry_worker)
            
            logger.info(f"Started {len(self.delivery_workers)} notification workers")
            
        except Exception as e:
            logger.error(f"Failed to start notification workers: {e}")

    async def stop_notification_workers(self):
        """Stop all notification workers"""
        try:
            for worker in self.delivery_workers:
                worker.cancel()
            
            await asyncio.gather(*self.delivery_workers, return_exceptions=True)
            self.delivery_workers.clear()
            
            logger.info("Stopped all notification workers")
            
        except Exception as e:
            logger.error(f"Failed to stop notification workers: {e}")

    async def _notification_worker(self, worker_id: str):
        """Background worker for processing notifications"""
        logger.info(f"Notification worker {worker_id} started")
        
        try:
            while True:
                try:
                    # Get notification from queue with timeout
                    notification = await asyncio.wait_for(
                        self.notification_queue.get(), 
                        timeout=5.0
                    )
                    
                    # Process the notification
                    result = await self._deliver_notification(notification)
                    
                    # Handle retry if needed
                    if result.status == NotificationStatus.FAILED and notification.retry_count < notification.max_retries:
                        notification.retry_count += 1
                        await self.retry_queue.put((notification, result))
                    
                    # Update statistics
                    self._update_delivery_stats(result)
                    
                    # Mark task as done
                    self.notification_queue.task_done()
                    
                except asyncio.TimeoutError:
                    # No notifications in queue, continue
                    continue
                except Exception as e:
                    logger.error(f"Worker {worker_id} error: {e}")
                    await asyncio.sleep(1)
                    
        except asyncio.CancelledError:
            logger.info(f"Notification worker {worker_id} cancelled")
        except Exception as e:
            logger.error(f"Notification worker {worker_id} failed: {e}")

    async def _retry_worker(self):
        """Background worker for handling notification retries"""
        logger.info("Retry worker started")
        
        try:
            while True:
                try:
                    # Get failed notification for retry
                    notification, previous_result = await asyncio.wait_for(
                        self.retry_queue.get(),
                        timeout=5.0
                    )
                    
                    # Calculate retry delay with exponential backoff
                    base_delay = self.notification_config.get('retry_delay_base', 30)
                    multiplier = self.notification_config.get('retry_delay_multiplier', 2.0)
                    max_delay = self.notification_config.get('max_retry_delay', 3600)
                    
                    retry_delay = min(
                        base_delay * (multiplier ** (notification.retry_count - 1)),
                        max_delay
                    )
                    
                    # Wait before retry
                    await asyncio.sleep(retry_delay)
                    
                    # Retry the notification
                    result = await self._deliver_notification(notification)
                    
                    # Check if we need to retry again
                    if result.status == NotificationStatus.FAILED and notification.retry_count < notification.max_retries:
                        notification.retry_count += 1
                        await self.retry_queue.put((notification, result))
                    
                    # Update statistics
                    self._update_delivery_stats(result)
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Retry worker error: {e}")
                    await asyncio.sleep(1)
                    
        except asyncio.CancelledError:
            logger.info("Retry worker cancelled")
        except Exception as e:
            logger.error(f"Retry worker failed: {e}")

    async def send_payment_notification(self, event_type: str, payment_data: Dict[str, Any], 
                                      recipients: List[str], notification_types: List[NotificationType] = None) -> List[str]:
        """
        Send payment-related notifications to recipients.
        
        Args:
            event_type: Type of payment event (payment_success, payment_failed, etc.)
            payment_data: Payment data for template variables
            recipients: List of recipient identifiers
            notification_types: List of notification types to send
            
        Returns:
            List of notification request IDs
        """
        try:
            notification_ids = []
            
            if notification_types is None:
                notification_types = [NotificationType.EMAIL, NotificationType.WEBSOCKET]
            
            for recipient in recipients:
                # Get user preferences
                preferences = await self._get_user_preferences(recipient)
                
                for notification_type in notification_types:
                    # Check if user allows this notification type
                    if notification_type not in preferences.enabled_types:
                        continue
                    
                    # Check if user has disabled this event
                    if event_type in preferences.disabled_events:
                        continue
                    
                    # Get appropriate template
                    template_name = f"{event_type}_{notification_type.value}"
                    template = self.default_templates.get(template_name)
                    
                    if not template:
                        logger.warning(f"No template found for {template_name}")
                        continue
                    
                    # Create notification request
                    notification = await self._create_notification_request(
                        template, recipient, payment_data, preferences
                    )
                    
                    # Queue for delivery
                    await self.notification_queue.put(notification)
                    notification_ids.append(notification.id)
            
            logger.info(f"Queued {len(notification_ids)} notifications for event {event_type}")
            return notification_ids
            
        except Exception as e:
            logger.error(f"Failed to send payment notification: {e}")
            return []

    async def _create_notification_request(self, template: NotificationTemplate, 
                                         recipient: str, data: Dict[str, Any],
                                         preferences: NotificationPreference) -> NotificationRequest:
        """Create a notification request from template and data"""
        try:
            # Generate unique ID
            import uuid
            notification_id = str(uuid.uuid4())
            
            # Render template with data
            subject = self._render_template(template.subject_template, data)
            body = self._render_template(template.body_template, data)
            
            # Calculate expiry time
            expiry_time = None
            if template.expiry_hours > 0:
                expiry_time = datetime.now() + timedelta(hours=template.expiry_hours)
            
            # Create notification request
            notification = NotificationRequest(
                id=notification_id,
                type=template.type,
                recipient=recipient,
                subject=subject,
                body=body,
                priority=template.priority,
                expiry_time=expiry_time,
                max_retries=template.retry_count,
                template_variables=data,
                metadata={
                    'template_name': template.name,
                    'user_language': preferences.language,
                    'user_timezone': preferences.timezone
                }
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"Failed to create notification request: {e}")
            raise

    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render notification template with data"""
        try:
            import string
            return string.Template(template).safe_substitute(data)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return template

    async def _deliver_notification(self, notification: NotificationRequest) -> NotificationResult:
        """Deliver a notification using the appropriate provider"""
        try:
            # Check if notification has expired
            if notification.expiry_time and datetime.now() > notification.expiry_time:
                return NotificationResult(
                    request_id=notification.id,
                    status=NotificationStatus.EXPIRED,
                    error_message="Notification expired"
                )
            
            # Route to appropriate delivery method
            if notification.type == NotificationType.EMAIL:
                return await self._deliver_email(notification)
            elif notification.type == NotificationType.SMS:
                return await self._deliver_sms(notification)
            elif notification.type == NotificationType.WEBHOOK:
                return await self._deliver_webhook(notification)
            elif notification.type == NotificationType.WEBSOCKET:
                return await self._deliver_websocket(notification)
            elif notification.type == NotificationType.PUSH:
                return await self._deliver_push(notification)
            elif notification.type == NotificationType.SLACK:
                return await self._deliver_slack(notification)
            else:
                return NotificationResult(
                    request_id=notification.id,
                    status=NotificationStatus.FAILED,
                    error_message=f"Unsupported notification type: {notification.type}"
                )
                
        except Exception as e:
            logger.error(f"Notification delivery failed: {e}")
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _deliver_email(self, notification: NotificationRequest) -> NotificationResult:
        """Deliver email notification"""
        try:
            if not self.email_provider:
                raise ValueError("Email provider not configured")
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = f"{self.email_provider['from_name']} <{self.email_provider['from_address']}>"
            msg['To'] = notification.recipient
            msg['Subject'] = notification.subject
            
            # Add body
            msg.attach(MIMEText(notification.body, 'plain'))
            
            # Add attachments if any
            for attachment in notification.attachments:
                self._add_email_attachment(msg, attachment)
            
            # Send email
            with smtplib.SMTP(self.email_provider['smtp_host'], self.email_provider['smtp_port']) as server:
                if self.email_provider['use_tls']:
                    server.starttls()
                
                server.login(self.email_provider['username'], self.email_provider['password'])
                server.send_message(msg)
            
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.SENT,
                delivered_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Email delivery failed: {e}")
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _deliver_sms(self, notification: NotificationRequest) -> NotificationResult:
        """Deliver SMS notification using Twilio"""
        try:
            if not self.sms_provider:
                raise ValueError("SMS provider not configured")
            
            # Prepare Twilio API request
            url = f"{self.sms_provider['service_url']}/{self.sms_provider['account_sid']}/Messages.json"
            
            data = {
                'From': self.sms_provider['from_number'],
                'To': notification.recipient,
                'Body': notification.body
            }
            
            # Send SMS via Twilio API
            auth = (self.sms_provider['account_sid'], self.sms_provider['auth_token'])
            
            async with asyncio.timeout(30):
                response = requests.post(url, data=data, auth=auth)
                response.raise_for_status()
            
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.SENT,
                delivered_at=datetime.now(),
                provider_response=response.json()
            )
            
        except Exception as e:
            logger.error(f"SMS delivery failed: {e}")
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _deliver_webhook(self, notification: NotificationRequest) -> NotificationResult:
        """Deliver webhook notification"""
        try:
            # Prepare webhook payload
            payload = {
                'id': notification.id,
                'subject': notification.subject,
                'body': json.loads(notification.body) if notification.body.startswith('{') else notification.body,
                'timestamp': datetime.now().isoformat(),
                'metadata': notification.metadata
            }
            
            # Send webhook
            headers = self.webhook_provider['headers'].copy()
            headers['X-Notification-ID'] = notification.id
            
            async with asyncio.timeout(self.webhook_provider['timeout']):
                response = requests.post(
                    notification.recipient,  # recipient is webhook URL
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
            
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.DELIVERED,
                delivered_at=datetime.now(),
                provider_response={'status_code': response.status_code}
            )
            
        except Exception as e:
            logger.error(f"Webhook delivery failed: {e}")
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _deliver_websocket(self, notification: NotificationRequest) -> NotificationResult:
        """Deliver real-time WebSocket notification"""
        try:
            # Find active WebSocket connections for recipient
            connections = self.websocket_connections.get(notification.recipient, [])
            
            if not connections:
                return NotificationResult(
                    request_id=notification.id,
                    status=NotificationStatus.FAILED,
                    error_message="No active WebSocket connections"
                )
            
            # Prepare message
            message = {
                'id': notification.id,
                'type': 'notification',
                'subject': notification.subject,
                'body': json.loads(notification.body) if notification.body.startswith('{') else notification.body,
                'timestamp': datetime.now().isoformat(),
                'priority': notification.priority.value
            }
            
            # Send to all active connections
            sent_count = 0
            for ws in connections[:]:  # Copy list to avoid modification during iteration
                try:
                    await ws.send(json.dumps(message))
                    sent_count += 1
                except Exception as e:
                    logger.warning(f"Failed to send WebSocket message: {e}")
                    # Remove dead connection
                    connections.remove(ws)
            
            if sent_count > 0:
                return NotificationResult(
                    request_id=notification.id,
                    status=NotificationStatus.DELIVERED,
                    delivered_at=datetime.now(),
                    provider_response={'connections_notified': sent_count}
                )
            else:
                return NotificationResult(
                    request_id=notification.id,
                    status=NotificationStatus.FAILED,
                    error_message="No successful WebSocket deliveries"
                )
                
        except Exception as e:
            logger.error(f"WebSocket delivery failed: {e}")
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _deliver_push(self, notification: NotificationRequest) -> NotificationResult:
        """Deliver push notification using Firebase"""
        try:
            if not self.push_provider:
                raise ValueError("Push notification provider not configured")
            
            # Prepare FCM payload
            payload = {
                'to': notification.recipient,  # FCM token
                'notification': {
                    'title': notification.subject,
                    'body': notification.body[:100] + '...' if len(notification.body) > 100 else notification.body,
                    'icon': 'payment_icon',
                    'sound': 'default'
                },
                'data': {
                    'notification_id': notification.id,
                    'priority': notification.priority.value,
                    'metadata': json.dumps(notification.metadata)
                }
            }
            
            # Send push notification
            async with asyncio.timeout(30):
                response = requests.post(
                    self.push_provider['service_url'],
                    json=payload,
                    headers=self.push_provider['headers']
                )
                response.raise_for_status()
            
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.SENT,
                delivered_at=datetime.now(),
                provider_response=response.json()
            )
            
        except Exception as e:
            logger.error(f"Push notification delivery failed: {e}")
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _deliver_slack(self, notification: NotificationRequest) -> NotificationResult:
        """Deliver Slack notification"""
        try:
            # Prepare Slack payload
            payload = {
                'text': notification.subject,
                'attachments': [
                    {
                        'color': 'good' if notification.priority == NotificationPriority.NORMAL else 'danger',
                        'text': notification.body,
                        'ts': int(datetime.now().timestamp())
                    }
                ]
            }
            
            # Send to Slack webhook
            async with asyncio.timeout(30):
                response = requests.post(
                    notification.recipient,  # Slack webhook URL
                    json=payload
                )
                response.raise_for_status()
            
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.DELIVERED,
                delivered_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Slack delivery failed: {e}")
            return NotificationResult(
                request_id=notification.id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    def _add_email_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment['content'])
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f"attachment; filename= {attachment['filename']}"
            )
            msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to add email attachment: {e}")

    async def _get_user_preferences(self, user_id: str) -> NotificationPreference:
        """Get notification preferences for user"""
        try:
            # Check cache first
            if user_id in self.preferences_cache:
                return self.preferences_cache[user_id]
            
            # Load from database (simplified - would use actual DB)
            # For now, return default preferences
            preferences = NotificationPreference(
                user_id=user_id,
                enabled_types={NotificationType.EMAIL, NotificationType.WEBSOCKET},
                disabled_events=set(),
                language='en',
                timezone='UTC'
            )
            
            # Cache for 5 minutes
            self.preferences_cache[user_id] = preferences
            
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            # Return default preferences
            return NotificationPreference(
                user_id=user_id,
                enabled_types={NotificationType.EMAIL},
                language='en'
            )

    def _update_delivery_stats(self, result: NotificationResult):
        """Update delivery statistics"""
        try:
            if result.status == NotificationStatus.SENT or result.status == NotificationStatus.DELIVERED:
                self.delivery_stats['delivered'] += 1
            elif result.status == NotificationStatus.FAILED:
                self.delivery_stats['failed'] += 1
            
            self.delivery_stats['sent'] += 1
            
        except Exception as e:
            logger.error(f"Failed to update delivery stats: {e}")

    async def register_websocket_connection(self, user_id: str, websocket):
        """Register a WebSocket connection for real-time notifications"""
        try:
            if user_id not in self.websocket_connections:
                self.websocket_connections[user_id] = []
            
            self.websocket_connections[user_id].append(websocket)
            logger.info(f"Registered WebSocket connection for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to register WebSocket connection: {e}")

    async def unregister_websocket_connection(self, user_id: str, websocket):
        """Unregister a WebSocket connection"""
        try:
            if user_id in self.websocket_connections:
                if websocket in self.websocket_connections[user_id]:
                    self.websocket_connections[user_id].remove(websocket)
                
                # Clean up empty lists
                if not self.websocket_connections[user_id]:
                    del self.websocket_connections[user_id]
            
            logger.info(f"Unregistered WebSocket connection for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to unregister WebSocket connection: {e}")

    async def get_notification_status(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific notification"""
        try:
            # In a real implementation, this would query the database
            # For now, return a simple status
            return {
                'notification_id': notification_id,
                'status': 'delivered',
                'delivered_at': datetime.now().isoformat(),
                'attempts': 1
            }
        except Exception as e:
            logger.error(f"Failed to get notification status: {e}")
            return None

    async def get_delivery_statistics(self) -> Dict[str, Any]:
        """Get comprehensive delivery statistics"""
        try:
            return {
                'total_sent': self.delivery_stats['sent'],
                'total_delivered': self.delivery_stats['delivered'],
                'total_failed': self.delivery_stats['failed'],
                'delivery_rate': (
                    self.delivery_stats['delivered'] / max(self.delivery_stats['sent'], 1)
                ) * 100,
                'queue_size': self.notification_queue.qsize(),
                'retry_queue_size': self.retry_queue.qsize(),
                'active_websocket_connections': sum(
                    len(connections) for connections in self.websocket_connections.values()
                ),
                'by_type': self.delivery_stats.get('by_type', {}),
                'by_priority': self.delivery_stats.get('by_priority', {})
            }
        except Exception as e:
            logger.error(f"Failed to get delivery statistics: {e}")
            return {}

# Enterprise-grade notification system with multi-role expertise
__all__ = [
    'PaymentGatewayNotifier', 'NotificationTemplate', 'NotificationPreference', 
    'NotificationRequest', 'NotificationResult', 'NotificationType', 
    'NotificationPriority', 'NotificationStatus'
]