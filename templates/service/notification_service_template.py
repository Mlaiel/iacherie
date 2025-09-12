"""{{service_name}} Notification Service for Ainflue Platform
{{service_description}}

Enterprise-grade notification service with multi-channel delivery,
real-time push notifications, email campaigns, SMS, and in-app messaging.

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Role: Backend Senior + Communication Systems Expert
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders

import aiohttp
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from pydantic import BaseModel, Field, validator, EmailStr
from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape
import websockets
from twilio.rest import Client as TwilioClient

from core.base_service import BaseService
from core.config import get_settings
from core.database import get_async_session
from core.exceptions import ServiceException, ValidationError
from models.notification import (
    Notification, NotificationTemplate, NotificationLog,
    NotificationPreference, NotificationChannel, Campaign
)
from models.creator import Creator
from models.user import User
from services.analytics_service import AnalyticsService
from utils.validation import validate_notification_data
from utils.template_engine import TemplateEngine
from monitoring.notification_metrics import NotificationMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    MARKETING = "marketing"
    SYSTEM = "system"
    SECURITY = "security"
    REVENUE = "revenue"
    CONTENT = "content"
    COLLABORATION = "collaboration"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class DeliveryStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    BLOCKED = "blocked"
    UNSUBSCRIBED = "unsubscribed"


class TemplateType(Enum):
    """Notification template types"""
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    PAYMENT_CONFIRMATION = "payment_confirmation"
    CONTENT_APPROVED = "content_approved"
    COLLABORATION_INVITE = "collaboration_invite"
    SECURITY_ALERT = "security_alert"
    REVENUE_REPORT = "revenue_report"
    SYSTEM_MAINTENANCE = "system_maintenance"


# Pydantic Models for Request/Response
class SendNotificationRequest(BaseModel):
    """Request model for sending notifications"""
    recipient_id: str = Field(..., description="Recipient user/creator ID")
    channels: List[NotificationChannel] = Field(..., description="Delivery channels")
    notification_type: NotificationType = Field(..., description="Notification type")
    priority: NotificationPriority = Field(NotificationPriority.NORMAL, description="Priority level")
    template_id: Optional[str] = Field(None, description="Template ID")
    subject: Optional[str] = Field(None, description="Notification subject")
    content: Optional[str] = Field(None, description="Notification content")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Template data")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule delivery time")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('channels')
    def validate_channels(cls, v):
        if not v:
            raise ValueError('At least one channel must be specified')
        return v


class CreateTemplateRequest(BaseModel):
    """Request model for creating notification templates"""
    name: str = Field(..., description="Template name")
    template_type: TemplateType = Field(..., description="Template type")
    channels: List[NotificationChannel] = Field(..., description="Supported channels")
    subject_template: str = Field(..., description="Subject template")
    content_template: str = Field(..., description="Content template")
    variables: List[str] = Field(default_factory=list, description="Template variables")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Template name must be at least 3 characters')
        return v.strip()


class CampaignRequest(BaseModel):
    """Request model for creating notification campaigns"""
    name: str = Field(..., description="Campaign name")
    template_id: str = Field(..., description="Template ID")
    target_audience: Dict[str, Any] = Field(..., description="Audience targeting criteria")
    channels: List[NotificationChannel] = Field(..., description="Delivery channels")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule time")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    """Response model for notification operations"""
    notification_id: str = Field(..., description="Notification ID")
    status: str = Field(..., description="Delivery status")
    channels_status: Dict[str, str] = Field(..., description="Status per channel")
    created_at: datetime = Field(..., description="Creation time")
    delivered_at: Optional[datetime] = Field(None, description="Delivery time")


class {{service_class_name}}(BaseService):
    """
    Enterprise Notification Service for Ainflue Platform
    
    Handles comprehensive notification management including:
    - Multi-channel notification delivery
    - Real-time push notifications
    - Email campaigns and automation
    - SMS messaging
    - In-app notifications
    - WebSocket real-time messaging
    - Notification templates and personalization
    - Delivery analytics and reporting
    - User preference management
    - Rate limiting and throttling
    """

    def __init__(self):
        super().__init__()
        self.name = "{{service_name}}"
        self.version = "{{service_version}}"
        self.redis_client = None
        self.metrics_collector = NotificationMetricsCollector()
        
        # Template engine
        self.template_engine = Environment(
            loader=FileSystemLoader('templates/notifications'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # External service clients
        self.smtp_client = None
        self.twilio_client = None
        self.websocket_connections = {}
        
        # Rate limiting configuration
        self.rate_limits = {
            NotificationChannel.EMAIL: 100,     # per hour
            NotificationChannel.SMS: 50,        # per hour  
            NotificationChannel.PUSH: 1000,     # per hour
            NotificationChannel.IN_APP: 10000   # per hour
        }

    async def initialize(self):
        """Initialize service with dependencies"""
        try:
            await super().initialize()
            
            # Initialize Redis for caching and queuing
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                retry_on_timeout=True
            )
            
            # Initialize external services
            await self._initialize_external_services()
            
            # Initialize metrics collection
            await self.metrics_collector.initialize()
            
            # Start background workers
            asyncio.create_task(self._notification_worker())
            asyncio.create_task(self._cleanup_worker())
            
            logger.info(f"{self.name} service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} service: {e}")
            raise ServiceException(f"Service initialization failed: {e}")

    async def _initialize_external_services(self):
        """Initialize external service clients"""
        try:
            # Initialize SMTP for email
            if settings.SMTP_SERVER and settings.SMTP_USERNAME:
                self.smtp_client = {
                    'server': settings.SMTP_SERVER,
                    'port': settings.SMTP_PORT,
                    'username': settings.SMTP_USERNAME,
                    'password': settings.SMTP_PASSWORD,
                    'use_tls': settings.SMTP_USE_TLS
                }
                logger.info("SMTP client initialized")
            
            # Initialize Twilio for SMS
            if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
                self.twilio_client = TwilioClient(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                logger.info("Twilio client initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize external services: {e}")
            raise ServiceException(f"External service initialization failed: {e}")

    async def send_notification(
        self,
        request: SendNotificationRequest,
        session: Optional[AsyncSession] = None
    ) -> NotificationResponse:
        """
        Send notification through specified channels
        
        Args:
            request: Notification sending request
            session: Database session
            
        Returns:
            Notification delivery status
        """
        async with self.get_session(session) as db_session:
            try:
                # Validate recipient
                recipient = await self._get_recipient(request.recipient_id, db_session)
                if not recipient:
                    raise ValidationError(f"Recipient {request.recipient_id} not found")
                
                # Check user preferences
                allowed_channels = await self._get_allowed_channels(
                    request.recipient_id, request.channels, db_session
                )
                
                if not allowed_channels:
                    raise ValidationError("No allowed channels for recipient")
                
                # Prepare notification content
                content_data = await self._prepare_notification_content(
                    request, recipient, db_session
                )
                
                # Create notification record
                notification = Notification(
                    id=str(uuid.uuid4()),
                    recipient_id=request.recipient_id,
                    notification_type=request.notification_type.value,
                    priority=request.priority.value,
                    subject=content_data['subject'],
                    content=content_data['content'],
                    channels=json.dumps([c.value for c in allowed_channels]),
                    template_id=request.template_id,
                    data=request.data,
                    scheduled_at=request.scheduled_at or datetime.utcnow(),
                    expires_at=request.expires_at,
                    status=DeliveryStatus.PENDING.value,
                    metadata=request.metadata,
                    created_at=datetime.utcnow()
                )
                
                db_session.add(notification)
                await db_session.commit()
                
                # Queue for delivery
                await self._queue_notification(notification, allowed_channels)
                
                # Record metrics
                await self.metrics_collector.record_notification(
                    notification_id=notification.id,
                    notification_type=request.notification_type.value,
                    channels=[c.value for c in allowed_channels],
                    priority=request.priority.value
                )
                
                logger.info(f"Notification queued: {notification.id}")
                
                return NotificationResponse(
                    notification_id=notification.id,
                    status=notification.status,
                    channels_status={c.value: "queued" for c in allowed_channels},
                    created_at=notification.created_at,
                    delivered_at=None
                )
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to send notification: {e}")
                await self.metrics_collector.record_error("notification_send", str(e))
                raise ServiceException(f"Notification sending failed: {e}")

    async def _prepare_notification_content(
        self,
        request: SendNotificationRequest,
        recipient: Union[User, Creator],
        session: AsyncSession
    ) -> Dict[str, str]:
        """Prepare notification content from template or direct content"""
        try:
            if request.template_id:
                # Load and render template
                template = await self._get_template(request.template_id, session)
                if not template:
                    raise ValidationError(f"Template {request.template_id} not found")
                
                # Prepare template data
                template_data = {
                    'recipient': {
                        'id': recipient.id,
                        'username': getattr(recipient, 'username', ''),
                        'email': getattr(recipient, 'email', ''),
                        'first_name': getattr(recipient, 'first_name', ''),
                        'last_name': getattr(recipient, 'last_name', '')
                    },
                    'platform': {
                        'name': 'Ainflue',
                        'url': settings.BASE_URL,
                        'support_email': settings.SUPPORT_EMAIL
                    },
                    **request.data
                }
                
                # Render templates
                subject_template = self.template_engine.from_string(template.subject_template)
                content_template = self.template_engine.from_string(template.content_template)
                
                subject = subject_template.render(**template_data)
                content = content_template.render(**template_data)
                
            else:
                # Use direct content
                subject = request.subject or "Notification"
                content = request.content or "You have a new notification."
            
            return {
                'subject': subject,
                'content': content
            }
            
        except Exception as e:
            logger.error(f"Failed to prepare notification content: {e}")
            raise ServiceException(f"Content preparation failed: {e}")

    async def _queue_notification(
        self,
        notification: Notification,
        channels: List[NotificationChannel]
    ):
        """Queue notification for delivery"""
        try:
            # Determine delivery order based on priority
            priority_order = {
                NotificationPriority.CRITICAL: 0,
                NotificationPriority.URGENT: 1,
                NotificationPriority.HIGH: 2,
                NotificationPriority.NORMAL: 3,
                NotificationPriority.LOW: 4
            }
            
            priority_score = priority_order.get(
                NotificationPriority(notification.priority), 3
            )
            
            # Queue for each channel
            for channel in channels:
                queue_data = {
                    'notification_id': notification.id,
                    'channel': channel.value,
                    'priority': priority_score,
                    'scheduled_at': notification.scheduled_at.isoformat(),
                    'retry_count': 0
                }
                
                # Add to Redis queue with priority
                await self.redis_client.zadd(
                    f"notification_queue:{channel.value}",
                    {json.dumps(queue_data): priority_score}
                )
            
            # Update notification status
            await self._update_notification_status(
                notification.id, DeliveryStatus.QUEUED
            )
            
            logger.debug(f"Notification {notification.id} queued for channels: {[c.value for c in channels]}")
            
        except Exception as e:
            logger.error(f"Failed to queue notification {notification.id}: {e}")
            await self._update_notification_status(
                notification.id, DeliveryStatus.FAILED
            )

    async def _notification_worker(self):
        """Background worker for processing notification queue"""
        while True:
            try:
                # Process each channel queue
                for channel in NotificationChannel:
                    await self._process_channel_queue(channel)
                
                # Wait before next iteration
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Notification worker error: {e}")
                await asyncio.sleep(5)

    async def _process_channel_queue(self, channel: NotificationChannel):
        """Process notifications for a specific channel"""
        try:
            queue_name = f"notification_queue:{channel.value}"
            
            # Get highest priority notification
            result = await self.redis_client.zrange(
                queue_name, 0, 0, withscores=True
            )
            
            if not result:
                return
            
            queue_data_str, priority = result[0]
            queue_data = json.loads(queue_data_str)
            
            # Check rate limiting
            if not await self._check_rate_limit(channel):
                logger.debug(f"Rate limit exceeded for {channel.value}")
                return
            
            # Remove from queue
            await self.redis_client.zrem(queue_name, queue_data_str)
            
            # Process notification
            success = await self._deliver_notification(
                queue_data['notification_id'],
                channel,
                queue_data
            )
            
            if not success:
                # Retry if not exceeded max retries
                if queue_data['retry_count'] < 3:
                    queue_data['retry_count'] += 1
                    await asyncio.sleep(2 ** queue_data['retry_count'])  # Exponential backoff
                    
                    await self.redis_client.zadd(
                        queue_name,
                        {json.dumps(queue_data): priority + 1}  # Lower priority for retries
                    )
            
        except Exception as e:
            logger.error(f"Failed to process {channel.value} queue: {e}")

    async def _deliver_notification(
        self,
        notification_id: str,
        channel: NotificationChannel,
        queue_data: Dict[str, Any]
    ) -> bool:
        """Deliver notification through specific channel"""
        try:
            # Get notification details
            notification = await self._get_notification(notification_id)
            if not notification:
                logger.error(f"Notification {notification_id} not found")
                return False
            
            # Check expiration
            if notification.expires_at and datetime.utcnow() > notification.expires_at:
                await self._log_delivery(
                    notification_id, channel, DeliveryStatus.FAILED, "Expired"
                )
                return False
            
            # Deliver based on channel
            if channel == NotificationChannel.EMAIL:
                success = await self._deliver_email(notification)
            elif channel == NotificationChannel.SMS:
                success = await self._deliver_sms(notification)
            elif channel == NotificationChannel.PUSH:
                success = await self._deliver_push(notification)
            elif channel == NotificationChannel.IN_APP:
                success = await self._deliver_in_app(notification)
            elif channel == NotificationChannel.WEBSOCKET:
                success = await self._deliver_websocket(notification)
            elif channel == NotificationChannel.WEBHOOK:
                success = await self._deliver_webhook(notification)
            else:
                logger.warning(f"Unsupported channel: {channel.value}")
                success = False
            
            # Log delivery result
            status = DeliveryStatus.DELIVERED if success else DeliveryStatus.FAILED
            await self._log_delivery(notification_id, channel, status)
            
            # Update metrics
            await self.metrics_collector.record_delivery(
                notification_id, channel.value, status.value
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to deliver notification {notification_id} via {channel.value}: {e}")
            await self._log_delivery(
                notification_id, channel, DeliveryStatus.FAILED, str(e)
            )
            return False

    async def _deliver_email(self, notification: Notification) -> bool:
        """Deliver notification via email"""
        try:
            if not self.smtp_client:
                logger.error("SMTP client not configured")
                return False
            
            # Get recipient email
            recipient = await self._get_recipient(notification.recipient_id)
            if not recipient or not getattr(recipient, 'email', None):
                logger.error(f"No email for recipient {notification.recipient_id}")
                return False
            
            # Create email message
            msg = MimeMultipart('alternative')
            msg['Subject'] = notification.subject
            msg['From'] = f"Ainflue <{self.smtp_client['username']}>"
            msg['To'] = recipient.email
            
            # Add content (support both text and HTML)
            if '<html>' in notification.content.lower() or '<div>' in notification.content.lower():
                html_part = MimeText(notification.content, 'html')
                msg.attach(html_part)
            else:
                text_part = MimeText(notification.content, 'plain')
                msg.attach(text_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_client['server'], self.smtp_client['port']) as server:
                if self.smtp_client['use_tls']:
                    server.starttls()
                server.login(self.smtp_client['username'], self.smtp_client['password'])
                server.send_message(msg)
            
            logger.info(f"Email sent to {recipient.email} for notification {notification.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email for notification {notification.id}: {e}")
            return False

    async def _deliver_sms(self, notification: Notification) -> bool:
        """Deliver notification via SMS"""
        try:
            if not self.twilio_client:
                logger.error("Twilio client not configured")
                return False
            
            # Get recipient phone
            recipient = await self._get_recipient(notification.recipient_id)
            if not recipient or not getattr(recipient, 'phone', None):
                logger.error(f"No phone for recipient {notification.recipient_id}")
                return False
            
            # Send SMS
            message = self.twilio_client.messages.create(
                body=f"{notification.subject}\n\n{notification.content}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=recipient.phone
            )
            
            logger.info(f"SMS sent to {recipient.phone} for notification {notification.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS for notification {notification.id}: {e}")
            return False

    async def _deliver_push(self, notification: Notification) -> bool:
        """Deliver push notification"""
        try:
            # Get recipient push tokens
            push_tokens = await self._get_push_tokens(notification.recipient_id)
            if not push_tokens:
                logger.warning(f"No push tokens for recipient {notification.recipient_id}")
                return False
            
            # Send push notification to each token
            success_count = 0
            for token in push_tokens:
                try:
                    # Use Firebase Cloud Messaging or similar service
                    # This is a placeholder implementation
                    payload = {
                        'notification': {
                            'title': notification.subject,
                            'body': notification.content[:100],  # Truncate for push
                            'icon': 'default'
                        },
                        'data': {
                            'notification_id': notification.id,
                            'type': notification.notification_type
                        }
                    }
                    
                    # Send push notification (implementation depends on service)
                    # await self._send_fcm_notification(token, payload)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send push to token {token}: {e}")
            
            logger.info(f"Push notifications sent: {success_count}/{len(push_tokens)} for notification {notification.id}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to send push notification {notification.id}: {e}")
            return False

    async def _deliver_in_app(self, notification: Notification) -> bool:
        """Deliver in-app notification"""
        try:
            # Store in Redis for real-time retrieval
            in_app_data = {
                'id': notification.id,
                'type': notification.notification_type,
                'priority': notification.priority,
                'subject': notification.subject,
                'content': notification.content,
                'created_at': notification.created_at.isoformat(),
                'metadata': notification.metadata
            }
            
            # Add to user's in-app notification queue
            await self.redis_client.lpush(
                f"in_app_notifications:{notification.recipient_id}",
                json.dumps(in_app_data)
            )
            
            # Keep only last 100 notifications
            await self.redis_client.ltrim(
                f"in_app_notifications:{notification.recipient_id}",
                0, 99
            )
            
            # Set expiration for cleanup
            await self.redis_client.expire(
                f"in_app_notifications:{notification.recipient_id}",
                86400 * 30  # 30 days
            )
            
            logger.info(f"In-app notification stored for recipient {notification.recipient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deliver in-app notification {notification.id}: {e}")
            return False

    async def _deliver_websocket(self, notification: Notification) -> bool:
        """Deliver notification via WebSocket"""
        try:
            # Get active WebSocket connections for recipient
            connections = self.websocket_connections.get(notification.recipient_id, [])
            if not connections:
                logger.debug(f"No active WebSocket connections for recipient {notification.recipient_id}")
                return False
            
            # Prepare WebSocket message
            ws_message = {
                'type': 'notification',
                'id': notification.id,
                'notification_type': notification.notification_type,
                'priority': notification.priority,
                'subject': notification.subject,
                'content': notification.content,
                'created_at': notification.created_at.isoformat(),
                'metadata': notification.metadata
            }
            
            # Send to all active connections
            sent_count = 0
            for connection in connections[:]:  # Copy list to avoid modification during iteration
                try:
                    await connection.send(json.dumps(ws_message))
                    sent_count += 1
                except Exception as e:
                    logger.warning(f"Failed to send WebSocket message: {e}")
                    # Remove dead connection
                    connections.remove(connection)
            
            logger.info(f"WebSocket notification sent to {sent_count} connections for recipient {notification.recipient_id}")
            return sent_count > 0
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket notification {notification.id}: {e}")
            return False

    async def _deliver_webhook(self, notification: Notification) -> bool:
        """Deliver notification via webhook"""
        try:
            # Get recipient webhook URLs
            webhook_urls = await self._get_webhook_urls(notification.recipient_id)
            if not webhook_urls:
                logger.debug(f"No webhook URLs for recipient {notification.recipient_id}")
                return False
            
            # Prepare webhook payload
            webhook_payload = {
                'notification_id': notification.id,
                'type': notification.notification_type,
                'priority': notification.priority,
                'subject': notification.subject,
                'content': notification.content,
                'recipient_id': notification.recipient_id,
                'created_at': notification.created_at.isoformat(),
                'metadata': notification.metadata
            }
            
            # Send to all webhook URLs
            success_count = 0
            for webhook_url in webhook_urls:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            webhook_url,
                            json=webhook_payload,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                success_count += 1
                            else:
                                logger.warning(f"Webhook returned status {response.status}")
                                
                except Exception as e:
                    logger.error(f"Failed to send webhook to {webhook_url}: {e}")
            
            logger.info(f"Webhook notifications sent: {success_count}/{len(webhook_urls)} for notification {notification.id}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification {notification.id}: {e}")
            return False

    async def create_template(
        self,
        request: CreateTemplateRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Create a new notification template
        
        Args:
            request: Template creation request
            session: Database session
            
        Returns:
            Template details
        """
        async with self.get_session(session) as db_session:
            try:
                # Validate template syntax
                await self._validate_template_syntax(
                    request.subject_template,
                    request.content_template
                )
                
                # Create template
                template = NotificationTemplate(
                    id=str(uuid.uuid4()),
                    name=request.name,
                    template_type=request.template_type.value,
                    channels=json.dumps([c.value for c in request.channels]),
                    subject_template=request.subject_template,
                    content_template=request.content_template,
                    variables=json.dumps(request.variables),
                    metadata=request.metadata,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db_session.add(template)
                await db_session.commit()
                
                logger.info(f"Notification template created: {template.id}")
                
                return {
                    "template_id": template.id,
                    "name": template.name,
                    "template_type": template.template_type,
                    "channels": json.loads(template.channels),
                    "variables": json.loads(template.variables),
                    "created_at": template.created_at.isoformat()
                }
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to create template: {e}")
                raise ServiceException(f"Template creation failed: {e}")

    async def get_notifications(
        self,
        recipient_id: str,
        channel: Optional[NotificationChannel] = None,
        notification_type: Optional[NotificationType] = None,
        limit: int = 50,
        offset: int = 0,
        session: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a recipient
        
        Args:
            recipient_id: Recipient ID
            channel: Optional channel filter
            notification_type: Optional type filter
            limit: Maximum number of results
            offset: Results offset
            session: Database session
            
        Returns:
            List of notifications
        """
        async with self.get_session(session) as db_session:
            try:
                # Build query
                query = select(Notification).where(
                    Notification.recipient_id == recipient_id
                )
                
                if notification_type:
                    query = query.where(
                        Notification.notification_type == notification_type.value
                    )
                
                # Add ordering and pagination
                query = query.order_by(Notification.created_at.desc())
                query = query.offset(offset).limit(limit)
                
                # Execute query
                result = await db_session.execute(query)
                notifications = result.scalars().all()
                
                # Format response
                notification_list = []
                for notification in notifications:
                    channels = json.loads(notification.channels) if notification.channels else []
                    
                    # Filter by channel if specified
                    if channel and channel.value not in channels:
                        continue
                    
                    notification_data = {
                        "id": notification.id,
                        "type": notification.notification_type,
                        "priority": notification.priority,
                        "subject": notification.subject,
                        "content": notification.content,
                        "channels": channels,
                        "status": notification.status,
                        "created_at": notification.created_at.isoformat(),
                        "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                        "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
                        "metadata": notification.metadata or {}
                    }
                    
                    notification_list.append(notification_data)
                
                return notification_list
                
            except Exception as e:
                logger.error(f"Failed to get notifications for {recipient_id}: {e}")
                raise ServiceException(f"Failed to retrieve notifications: {e}")

    async def mark_as_read(
        self,
        notification_id: str,
        recipient_id: str,
        session: Optional[AsyncSession] = None
    ) -> bool:
        """
        Mark notification as read
        
        Args:
            notification_id: Notification ID
            recipient_id: Recipient ID
            session: Database session
            
        Returns:
            Success status
        """
        async with self.get_session(session) as db_session:
            try:
                # Update notification
                result = await db_session.execute(
                    update(Notification)
                    .where(
                        and_(
                            Notification.id == notification_id,
                            Notification.recipient_id == recipient_id
                        )
                    )
                    .values(
                        read_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                )
                
                await db_session.commit()
                
                success = result.rowcount > 0
                if success:
                    logger.info(f"Notification {notification_id} marked as read")
                
                return success
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to mark notification as read: {e}")
                raise ServiceException(f"Failed to mark notification as read: {e}")

    # Helper methods
    async def _get_recipient(self, recipient_id: str, session: Optional[AsyncSession] = None):
        """Get recipient (User or Creator)"""
        if session:
            try:
                # Try User first
                result = await session.execute(
                    select(User).where(User.id == recipient_id)
                )
                user = result.scalar_one_or_none()
                if user:
                    return user
                
                # Try Creator
                result = await session.execute(
                    select(Creator).where(Creator.id == recipient_id)
                )
                return result.scalar_one_or_none()
                
            except Exception as e:
                logger.error(f"Failed to get recipient {recipient_id}: {e}")
                return None
        return None

    async def _get_allowed_channels(
        self,
        recipient_id: str,
        requested_channels: List[NotificationChannel],
        session: AsyncSession
    ) -> List[NotificationChannel]:
        """Get allowed channels based on user preferences"""
        try:
            # Get user preferences
            result = await session.execute(
                select(NotificationPreference).where(
                    NotificationPreference.user_id == recipient_id
                )
            )
            preferences = result.scalars().all()
            
            # If no preferences, allow all channels
            if not preferences:
                return requested_channels
            
            # Filter channels based on preferences
            allowed_channels = []
            for channel in requested_channels:
                pref = next(
                    (p for p in preferences if p.channel == channel.value),
                    None
                )
                if not pref or pref.enabled:
                    allowed_channels.append(channel)
            
            return allowed_channels
            
        except Exception as e:
            logger.error(f"Failed to get allowed channels for {recipient_id}: {e}")
            return requested_channels

    async def _get_template(self, template_id: str, session: AsyncSession):
        """Get notification template"""
        try:
            result = await session.execute(
                select(NotificationTemplate).where(
                    NotificationTemplate.id == template_id
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
            return None

    async def _get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        async with self.get_session() as session:
            try:
                result = await session.execute(
                    select(Notification).where(Notification.id == notification_id)
                )
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Failed to get notification {notification_id}: {e}")
                return None

    async def _update_notification_status(
        self,
        notification_id: str,
        status: DeliveryStatus
    ):
        """Update notification status"""
        async with self.get_session() as session:
            try:
                await session.execute(
                    update(Notification)
                    .where(Notification.id == notification_id)
                    .values(
                        status=status.value,
                        delivered_at=datetime.utcnow() if status == DeliveryStatus.DELIVERED else None,
                        updated_at=datetime.utcnow()
                    )
                )
                await session.commit()
            except Exception as e:
                logger.error(f"Failed to update notification status: {e}")

    async def _log_delivery(
        self,
        notification_id: str,
        channel: NotificationChannel,
        status: DeliveryStatus,
        error_message: Optional[str] = None
    ):
        """Log delivery attempt"""
        async with self.get_session() as session:
            try:
                log_entry = NotificationLog(
                    id=str(uuid.uuid4()),
                    notification_id=notification_id,
                    channel=channel.value,
                    status=status.value,
                    error_message=error_message,
                    delivered_at=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                
                session.add(log_entry)
                await session.commit()
            except Exception as e:
                logger.error(f"Failed to log delivery: {e}")

    async def _check_rate_limit(self, channel: NotificationChannel) -> bool:
        """Check if channel is within rate limits"""
        try:
            limit = self.rate_limits.get(channel, 1000)
            current_hour = datetime.utcnow().strftime("%Y%m%d%H")
            rate_key = f"rate_limit:{channel.value}:{current_hour}"
            
            current_count = await self.redis_client.get(rate_key)
            current_count = int(current_count) if current_count else 0
            
            if current_count >= limit:
                return False
            
            # Increment counter
            await self.redis_client.incr(rate_key)
            await self.redis_client.expire(rate_key, 3600)  # 1 hour
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True  # Allow if check fails

    async def _get_push_tokens(self, recipient_id: str) -> List[str]:
        """Get push notification tokens for recipient"""
        try:
            # This would query the user's registered devices/tokens
            # Implementation depends on your device management system
            tokens = await self.redis_client.smembers(f"push_tokens:{recipient_id}")
            return list(tokens) if tokens else []
        except Exception as e:
            logger.error(f"Failed to get push tokens for {recipient_id}: {e}")
            return []

    async def _get_webhook_urls(self, recipient_id: str) -> List[str]:
        """Get webhook URLs for recipient"""
        try:
            # This would query the user's configured webhook URLs
            # Implementation depends on your webhook management system
            urls = await self.redis_client.smembers(f"webhook_urls:{recipient_id}")
            return list(urls) if urls else []
        except Exception as e:
            logger.error(f"Failed to get webhook URLs for {recipient_id}: {e}")
            return []

    async def _validate_template_syntax(
        self,
        subject_template: str,
        content_template: str
    ):
        """Validate Jinja2 template syntax"""
        try:
            self.template_engine.from_string(subject_template)
            self.template_engine.from_string(content_template)
        except Exception as e:
            raise ValidationError(f"Invalid template syntax: {e}")

    async def _cleanup_worker(self):
        """Background worker for cleanup tasks"""
        while True:
            try:
                # Clean up expired notifications
                await self._cleanup_expired_notifications()
                
                # Clean up old logs
                await self._cleanup_old_logs()
                
                # Wait 1 hour before next cleanup
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _cleanup_expired_notifications(self):
        """Clean up expired notifications"""
        async with self.get_session() as session:
            try:
                # Delete expired notifications
                await session.execute(
                    delete(Notification).where(
                        and_(
                            Notification.expires_at <= datetime.utcnow(),
                            Notification.expires_at.isnot(None)
                        )
                    )
                )
                await session.commit()
            except Exception as e:
                logger.error(f"Failed to cleanup expired notifications: {e}")

    async def _cleanup_old_logs(self):
        """Clean up old notification logs"""
        async with self.get_session() as session:
            try:
                # Delete logs older than 90 days
                cutoff_date = datetime.utcnow() - timedelta(days=90)
                await session.execute(
                    delete(NotificationLog).where(
                        NotificationLog.created_at < cutoff_date
                    )
                )
                await session.commit()
            except Exception as e:
                logger.error(f"Failed to cleanup old logs: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = await super().health_check()
            
            # Check Redis connectivity
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis"] = "healthy"
            
            # Check external services
            health_status["external_services"] = {
                "smtp": "available" if self.smtp_client else "unavailable",
                "twilio": "available" if self.twilio_client else "unavailable"
            }
            
            # Check queue sizes
            queue_sizes = {}
            for channel in NotificationChannel:
                size = await self.redis_client.zcard(f"notification_queue:{channel.value}")
                queue_sizes[channel.value] = size
            
            health_status["queue_sizes"] = queue_sizes
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def cleanup(self):
        """Cleanup service resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.metrics_collector:
                await self.metrics_collector.cleanup()
                
            await super().cleanup()
            logger.info(f"{self.name} service cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Failed to cleanup {self.name} service: {e}")


# Example usage and testing
if __name__ == "__main__":
    async def main():
        service = {{service_class_name}}()
        await service.initialize()
        
        # Example notification sending
        notification_request = SendNotificationRequest(
            recipient_id="user_123",
            channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.NORMAL,
            subject="Welcome to Ainflue!",
            content="Thank you for joining our platform. Get started by uploading your first content.",
            data={"welcome_bonus": "$10"}
        )
        
        try:
            result = await service.send_notification(notification_request)
            print(f"Notification sent: {result}")
            
            # Example template creation
            template_request = CreateTemplateRequest(
                name="Welcome Email",
                template_type=TemplateType.WELCOME,
                channels=[NotificationChannel.EMAIL],
                subject_template="Welcome to {{platform.name}}, {{recipient.first_name}}!",
                content_template="Hello {{recipient.first_name}}, welcome to {{platform.name}}!",
                variables=["recipient.first_name", "platform.name"]
            )
            
            template_result = await service.create_template(template_request)
            print(f"Template created: {template_result}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await service.cleanup()

    asyncio.run(main())