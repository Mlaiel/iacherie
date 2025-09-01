"""Notification Engine Database Management

Enterprise notification system for real-time alerts, creator communications,
and multi-channel delivery across all content creation workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

import uuid
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import asyncio

Base = declarative_base()
logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """
Notification types for creators"""

    CONTENT_PROTECTION_ALERT = "content_protection_alert"
    COLLABORATION_REQUEST = "collaboration_request"
    REVENUE_UPDATE = "revenue_update"
    PLATFORM_SYNC = "platform_sync"
    AI_RECOMMENDATION = "ai_recommendation"
    WORKFLOW_STATUS = "workflow_status"
    SYSTEM_ALERT = "system_alert"
    MARKETING_CAMPAIGN = "marketing_campaign"
    COMMUNITY_UPDATE = "community_update"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"


class NotificationPriority(Enum):
    """Notification priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class ChannelType(Enum):
    """Notification delivery channels"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"


class NotificationStatus(Enum):
    """Notification delivery status"""

    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ContentCreatorType(Enum):
    """Creator types for targeted notifications"""

    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    COMEDIAN = "comedian"
    INFLUENCER = "influencer"
    BRAND_AMBASSADOR = "brand_ambassador"
    CONTENT_CREATOR = "content_creator"
    MULTI_FORMAT = "multi_format"


@dataclass
class NotificationTemplate:
    """Notification template structure"""
    template_id: str
    name: str
    content_type: str
    subject_template: str
    body_template: str
    variables: List[str]
    channels: List[ChannelType]
    creator_types: List[ContentCreatorType]
    localization: Dict[str, Dict[str, str]]


@dataclass
class NotificationRecipient:
    """
Notification recipient information"""
    user_id: str
    creator_type: ContentCreatorType
    channels: List[ChannelType]
    preferences: Dict[str, Any]
    timezone: str
    language: str
    contact_info: Dict[str, str]


class NotificationChannel(Base):
    """
Notification channel configuration"""
    __tablename__ = "notification_channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    channel_type = Column(String(50), nullable=False)
    channel_config = Column(JSON)
    is_enabled = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    verification_expires = Column(DateTime(timezone=True))
    rate_limit_per_hour = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime(timezone=True))
    failure_count = Column(Integer, default=0)
    metadata = Column(JSON)

    __table_args__ = (
        Index('idx_channel_user_type', 'user_id', 'channel_type'),
    )


class NotificationTemplate(Base):
    """Notification template model"""
    __tablename__ = "notification_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_key = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    notification_type = Column(String(100), nullable=False)
    priority = Column(String(50), default=NotificationPriority.NORMAL.value)
    
    # Template content
    subject_template = Column(Text)
    body_template = Column(Text)
    html_template = Column(Text)
    variables = Column(ARRAY(String))
    
    # Targeting
    creator_types = Column(ARRAY(String))
    supported_channels = Column(ARRAY(String))
    
    # Localization
    localizations = Column(JSON)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)
    rate_limit_per_user_hour = Column(Integer, default=10)
    expires_after_hours = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_by = Column(String(255))

    __table_args__ = (
        Index('idx_template_type_active', 'notification_type', 'is_active'),
    )


class Notification(Base):
    """Notification instance model"""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(String(255), nullable=False, unique=True, index=True)
    template_id = Column(UUID(as_uuid=True), index=True)
    user_id = Column(String(255), nullable=False, index=True)
    creator_type = Column(String(50))
    
    # Content
    notification_type = Column(String(100), nullable=False)
    priority = Column(String(50), default=NotificationPriority.NORMAL.value)
    subject = Column(String(500))
    content = Column(Text)
    html_content = Column(Text)
    
    # Delivery
    channels = Column(ARRAY(String))
    status = Column(String(50), default=NotificationStatus.PENDING.value)
    scheduled_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Metadata
    variables = Column(JSON)
    context = Column(JSON)
    tracking_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    
    # Processing
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text)
    worker_id = Column(String(255))

    __table_args__ = (
        Index('idx_notification_user_type', 'user_id', 'notification_type'),
        Index('idx_notification_status_scheduled', 'status', 'scheduled_at'),
        Index('idx_notification_priority_created', 'priority', 'created_at'),
    )


class NotificationDelivery(Base):
    """Notification delivery tracking per channel"""
    __tablename__ = "notification_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(String(255), nullable=False, index=True)
    channel_type = Column(String(50), nullable=False)
    channel_address = Column(String(500))
    
    # Delivery status
    status = Column(String(50), default=NotificationStatus.PENDING.value)
    attempt_count = Column(Integer, default=0)
    
    # Timestamps
    queued_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    
    # Response data
    provider_message_id = Column(String(255))
    provider_response = Column(JSON)
    error_message = Column(Text)
    
    # Engagement tracking
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    unsubscribed_at = Column(DateTime(timezone=True))
    
    # Metrics
    delivery_time_ms = Column(Integer)
    provider_cost = Column(Float)

    __table_args__ = (
        Index('idx_delivery_notification_channel', 'notification_id', 'channel_type'),
        Index('idx_delivery_status_queued', 'status', 'queued_at'),
    )


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    notification_type = Column(String(100), nullable=False)
    channel_type = Column(String(50), nullable=False)
    
    # Preferences
    is_enabled = Column(Boolean, default=True)
    frequency = Column(String(50), default="immediate")  # immediate, hourly, daily, weekly
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))    # HH:MM format
    minimum_priority = Column(String(50), default=NotificationPriority.NORMAL.value)
    
    # Scheduling
    preferred_time = Column(String(5))     # HH:MM format
    timezone = Column(String(50))
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_preference_user_type_channel', 'user_id', 'notification_type', 'channel_type'),
    )


class NotificationMetrics(Base):
    """Notification system metrics"""
    __tablename__ = "notification_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_type = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    labels = Column(JSON)
    aggregation_period = Column(String(50))  # minute, hour, day, week

    __table_args__ = (
        Index('idx_metrics_type_time', 'metric_type', 'timestamp'),
    )


class NotificationEngine:
    """Enterprise notification engine with multi-channel delivery"""
    
    def __init__(self, redis_client: redis.Redis, db_session: Session):
        self.redis = redis_client
        self.db = db_session
        self.templates: Dict[str, NotificationTemplate] = {}
        self.channels: Dict[str, Any] = {}
        self.running = False
        self.worker_tasks: List[asyncio.Task] = []
        
        # Channel providers
        self.email_config = {}
        self.sms_config = {}
        self.push_config = {}
        self.webhook_config = {}
    
    async def initialize(self):
        """
Initialize notification engine"""
        try:
            # Load templates and channels
            await self._load_templates()
            await self._load_channel_configurations()
            
            # Start background workers
            await self._start_workers()
            
            self.running = True
            logger.info("Notification engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize notification engine: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        # Stop workers
        for task in self.worker_tasks:
            task.cancel()
        
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        logger.info("Notification engine shutdown completed")
    
    async def create_template(
        self,
        template_key: str,
        name: str,
        notification_type: NotificationType,
        subject_template: str,
        body_template: str,
        variables: List[str],
        creator_types: List[ContentCreatorType],
        supported_channels: List[ChannelType],
        localizations: Optional[Dict[str, Dict[str, str]]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> NotificationTemplate:
        """Create notification template"""
        try:
            template = NotificationTemplate(
                template_key=template_key,
                name=name,
                notification_type=notification_type.value,
                subject_template=subject_template,
                body_template=body_template,
                variables=variables,
                creator_types=[ct.value for ct in creator_types],
                supported_channels=[ch.value for ch in supported_channels],
                localizations=localizations or {},
                priority=priority.value
            )
            
            self.db.add(template)
            self.db.commit()
            
            # Cache template
            self.templates[template_key] = template
            
            logger.info(f"Created notification template: {template_key}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to create template {template_key}: {e}")
            self.db.rollback()
            raise
    
    async def send_notification(
        self,
        user_id: str,
        template_key: str,
        variables: Dict[str, Any],
        channels: Optional[List[ChannelType]] = None,
        priority: Optional[NotificationPriority] = None,
        scheduled_at: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Send notification to user"""
        try:
            # Get template
            template = self.templates.get(template_key)
            if not template:
                template = self.db.query(NotificationTemplate).filter(
                    NotificationTemplate.template_key == template_key,
                    NotificationTemplate.is_active == True
                ).first()
                
                if not template:
                    raise ValueError(f"Template {template_key} not found")
            
            # Get user preferences
            user_channels = await self._get_user_channels(user_id, channels)
            if not user_channels:
                logger.warning(f"No delivery channels for user {user_id}")
                return ""
            
            # Create notification
            notification_id = f"notif_{uuid.uuid4().hex[:12]}"
            
            # Render content
            subject = await self._render_template(template.subject_template, variables)
            content = await self._render_template(template.body_template, variables)
            
            notification = Notification(
                notification_id=notification_id,
                template_id=template.id,
                user_id=user_id,
                notification_type=template.notification_type,
                priority=priority.value if priority else template.priority,
                subject=subject,
                content=content,
                channels=[ch.value for ch in user_channels],
                variables=variables,
                context=context or {},
                scheduled_at=scheduled_at or datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(hours=template.expires_after_hours or 24)
            )
            
            self.db.add(notification)
            self.db.commit()
            
            # Queue for delivery
            await self._queue_notification(notification_id, user_channels)
            
            logger.info(f"Queued notification {notification_id} for user {user_id}")
            return notification_id
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            self.db.rollback()
            raise
    
    async def send_bulk_notification(
        self,
        user_ids: List[str],
        template_key: str,
        variables: Dict[str, Any],
        channels: Optional[List[ChannelType]] = None,
        priority: Optional[NotificationPriority] = None,
        creator_type_filter: Optional[ContentCreatorType] = None
    ) -> List[str]:
        """Send bulk notifications to multiple users"""
        notification_ids = []
        
        for user_id in user_ids:
            try:
                # Apply creator type filter if specified
                if creator_type_filter:
                    user_creator_type = await self._get_user_creator_type(user_id)
                    if user_creator_type != creator_type_filter:
                        continue
                
                # Personalize variables if needed
                user_variables = await self._personalize_variables(user_id, variables)
                
                notification_id = await self.send_notification(
                    user_id=user_id,
                    template_key=template_key,
                    variables=user_variables,
                    channels=channels,
                    priority=priority
                )
                
                if notification_id:
                    notification_ids.append(notification_id)
                    
            except Exception as e:
                logger.error(f"Failed to send bulk notification to {user_id}: {e}")
                continue
        
        logger.info(f"Sent bulk notifications to {len(notification_ids)} users")
        return notification_ids
    
    async def register_channel(
        self,
        user_id: str,
        channel_type: ChannelType,
        config: Dict[str, Any],
        verify: bool = True
    ) -> NotificationChannel:
        """Register notification channel for user"""
        try:
            # Check if channel already exists
            existing = self.db.query(NotificationChannel).filter(
                NotificationChannel.user_id == user_id,
                NotificationChannel.channel_type == channel_type.value
            ).first()
            
            if existing:
                # Update existing
                existing.channel_config = config
                existing.updated_at = datetime.now(timezone.utc)
                if verify:
                    await self._send_verification(existing)
            else:
                # Create new
                channel = NotificationChannel(
                    user_id=user_id,
                    channel_type=channel_type.value,
                    channel_config=config,
                    verification_token=uuid.uuid4().hex if verify else None,
                    verification_expires=datetime.now(timezone.utc) + timedelta(hours=24) if verify else None
                )
                
                self.db.add(channel)
                existing = channel
                
                if verify:
                    await self._send_verification(channel)
            
            self.db.commit()
            
            logger.info(f"Registered {channel_type.value} channel for user {user_id}")
            return existing
            
        except Exception as e:
            logger.error(f"Failed to register channel: {e}")
            self.db.rollback()
            raise
    
    async def verify_channel(self, user_id: str, channel_type: ChannelType, token: str) -> bool:
        """Verify notification channel"""
        try:
            channel = self.db.query(NotificationChannel).filter(
                NotificationChannel.user_id == user_id,
                NotificationChannel.channel_type == channel_type.value,
                NotificationChannel.verification_token == token,
                NotificationChannel.verification_expires > datetime.now(timezone.utc)
            ).first()
            
            if not channel:
                return False
            
            channel.is_verified = True
            channel.verification_token = None
            channel.verification_expires = None
            channel.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            logger.info(f"Verified {channel_type.value} channel for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify channel: {e}")
            self.db.rollback()
            return False
    
    async def update_preferences(
        self,
        user_id: str,
        notification_type: NotificationType,
        channel_type: ChannelType,
        preferences: Dict[str, Any]
    ):
        """Update user notification preferences"""
        try:
            existing = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id,
                NotificationPreference.notification_type == notification_type.value,
                NotificationPreference.channel_type == channel_type.value
            ).first()
            
            if existing:
                # Update existing
                for key, value in preferences.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.now(timezone.utc)
            else:
                # Create new
                pref = NotificationPreference(
                    user_id=user_id,
                    notification_type=notification_type.value,
                    channel_type=channel_type.value,
                    **preferences
                )
                self.db.add(pref)
            
            self.db.commit()
            logger.info(f"Updated preferences for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to update preferences: {e}")
            self.db.rollback()
            raise
    
    async def get_notification_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        notification_type: Optional[NotificationType] = None
    ) -> List[Dict[str, Any]]:
        """Get user's notification history"""
        try:
            query = self.db.query(Notification).filter(
                Notification.user_id == user_id
            )
            
            if notification_type:
                query = query.filter(Notification.notification_type == notification_type.value)
            
            notifications = query.order_by(
                Notification.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": n.notification_id,
                    "type": n.notification_type,
                    "subject": n.subject,
                    "content": n.content,
                    "status": n.status,
                    "created_at": n.created_at.isoformat(),
                    "sent_at": n.sent_at.isoformat() if n.sent_at else None,
                    "opened_at": n.opened_at.isoformat() if n.opened_at else None
                }
                for n in notifications
            ]
            
        except Exception as e:
            logger.error(f"Failed to get notification history: {e}")
            return []
    
    async def get_delivery_stats(
        self,
        notification_id: str
    ) -> Dict[str, Any]:
        """Get notification delivery statistics"""
        try:
            deliveries = self.db.query(NotificationDelivery).filter(
                NotificationDelivery.notification_id == notification_id
            ).all()
            
            stats = {
                "total_channels": len(deliveries),
                "delivered": len([d for d in deliveries if d.status == NotificationStatus.DELIVERED.value]),
                "failed": len([d for d in deliveries if d.status == NotificationStatus.FAILED.value]),
                "pending": len([d for d in deliveries if d.status == NotificationStatus.PENDING.value]),
                "channels": {}
            }
            
            for delivery in deliveries:
                stats["channels"][delivery.channel_type] = {
                    "status": delivery.status,
                    "sent_at": delivery.sent_at.isoformat() if delivery.sent_at else None,
                    "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None,
                    "opened_at": delivery.opened_at.isoformat() if delivery.opened_at else None,
                    "error": delivery.error_message
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get delivery stats: {e}")
            return {}
    
    # Private methods
    
    async def _load_templates(self):
        """Load notification templates from database"""
        templates = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.is_active == True
        ).all()
        
        for template in templates:
            self.templates[template.template_key] = template
    
    async def _load_channel_configurations(self):
        """
Load channel configurations"""
        try:
            # Email configuration
            self.channel_configs[ChannelType.EMAIL] = {
                'smtp_host': 'smtp.gmail.com',
                'smtp_port': 587,
                'use_tls': True,
                'default_from': 'notifications@ia-influencer.com',
                'rate_limit': 100,  # per minute
                'retry_attempts': 3,
                'retry_delay': 30
            }
            
            # SMS configuration
            self.channel_configs[ChannelType.SMS] = {
                'provider': 'twilio',
                'rate_limit': 10,  # per minute
                'retry_attempts': 2,
                'retry_delay': 60
            }
            
            # Push notification configuration
            self.channel_configs[ChannelType.PUSH] = {
                'firebase_key': 'firebase_server_key',
                'rate_limit': 1000,  # per minute
                'retry_attempts': 3,
                'retry_delay': 15
            }
            
            # In-app notification configuration
            self.channel_configs[ChannelType.IN_APP] = {
                'real_time': True,
                'persistence': True,
                'rate_limit': 500,  # per minute
                'retention_days': 30
            }
            
            # Webhook configuration
            self.channel_configs[ChannelType.WEBHOOK] = {
                'timeout': 30,
                'rate_limit': 200,  # per minute
                'retry_attempts': 5,
                'retry_delay': 120
            }
            
            logger.info("Channel configurations loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load channel configurations: {e}")
            raise
    
    async def _start_workers(self):
        """Start background worker tasks"""
        self.worker_tasks.extend([
            asyncio.create_task(self._notification_processor_worker()),
            asyncio.create_task(self._delivery_scheduler_worker()),
            asyncio.create_task(self._metrics_collector_worker())
        ])
    
    async def _get_user_channels(
        self, 
        user_id: str, 
        requested_channels: Optional[List[ChannelType]]
    ) -> List[ChannelType]:
        """
Get user's available notification channels"""
        # Get user's verified channels
        channels = self.db.query(NotificationChannel).filter(
            NotificationChannel.user_id == user_id,
            NotificationChannel.is_enabled == True,
            NotificationChannel.is_verified == True
        ).all()
        
        available_channels = [ChannelType(ch.channel_type) for ch in channels]
        
        if requested_channels:
            return [ch for ch in requested_channels if ch in available_channels]
        
        return available_channels
    
    async def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
Render template with variables"""
        try:
            # Simple string replacement - could use Jinja2 for more complex templates
            rendered = template
            for key, value in variables.items():
                rendered = rendered.replace(f"{{{key}}}", str(value))
            return rendered
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return template
    
    async def _queue_notification(self, notification_id: str, channels: List[ChannelType]):
        """Queue notification for delivery"""
        await self.redis.lpush(
            "notification_queue",
            json.dumps({
                "notification_id": notification_id,
                "channels": [ch.value for ch in channels],
                "queued_at": datetime.now(timezone.utc).isoformat()
            })
        )
    
    async def _send_verification(self, channel: NotificationChannel):
        """Send channel verification message"""
        try:
            channel_type = ChannelType(channel.channel_type)
            verification_code = str(uuid.uuid4())[:8].upper()
            
            # Store verification code
            await self.redis_client.setex(
                f"verification:{channel.id}",
                900,  # 15 minutes
                verification_code
            )
            
            if channel_type == ChannelType.EMAIL:
                await self._send_email_verification(channel, verification_code)
            elif channel_type == ChannelType.SMS:
                await self._send_sms_verification(channel, verification_code)
            elif channel_type == ChannelType.PUSH:
                await self._send_push_verification(channel, verification_code)
            else:
                logger.warning(f"Verification not supported for channel type: {channel_type}")
                return False
            
            # Update channel status
            channel.verification_sent_at = datetime.utcnow()
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification for channel {channel.id}: {e}")
            return False
    
    async def _send_email_verification(self, channel: NotificationChannel, code: str):
        """Send email verification"""
        subject = "Verify Your Email - IA Influencer Platform"
        body = f"""
        Dear Creator,
        
        Please verify your email address by entering this code: {code}
        
        This code expires in 15 minutes.
        
        Best regards,
        IA Influencer Team
        """
        
        # Use your email service implementation
        await self._send_email(channel.endpoint, subject, body)
    
    async def _send_sms_verification(self, channel: NotificationChannel, code: str):
        """
Send SMS verification"""
        message = f"IA Influencer: Your verification code is {code}. Expires in 15 minutes."
        
        # Use your SMS service implementation
        await self._send_sms(channel.endpoint, message)
    
    async def _send_push_verification(self, channel: NotificationChannel, code: str):
        """Send push notification verification"""
        title = "Verify Device"
        body = f"Your verification code: {code}"
        
        # Use your push notification service implementation
        await self._send_push_notification(channel.endpoint, title, body)
    
    async def _get_user_creator_type(self, user_id: str) -> Optional[ContentCreatorType]:
        """Get user's creator type"""
        # Would query user profile for creator type
        return ContentCreatorType.MULTI_FORMAT  # Default
    
    async def _personalize_variables(self, user_id: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
Personalize variables for specific user"""
        # Add user-specific data to variables
        personalized = variables.copy()
        personalized["user_id"] = user_id
        return personalized
    
    async def _notification_processor_worker(self):
        """Background worker for processing notifications"""
        while self.running:
            try:
                await asyncio.sleep(1)
                # Process notification queue
                
            except Exception as e:
                logger.error(f"Notification processor error: {e}")
                await asyncio.sleep(5)
    
    async def _delivery_scheduler_worker(self):
        """Background worker for delivery scheduling"""
        while self.running:
            try:
                await asyncio.sleep(10)
                # Process scheduled deliveries
                
            except Exception as e:
                logger.error(f"Delivery scheduler error: {e}")
                await asyncio.sleep(5)
    
    async def _metrics_collector_worker(self):
        """Background worker for metrics collection"""
        while self.running:
            try:
                await asyncio.sleep(30)
                # Collect metrics
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(10)
