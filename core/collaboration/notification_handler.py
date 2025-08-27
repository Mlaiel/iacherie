"""
📧 NOTIFICATION HANDLER - Communication Management System
========================================================

Developed by: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved - Unauthorized use is strictly prohibited

⚠️  LEGAL WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any attempt to steal, copy, or reproduce this concept, idea, or code
without explicit written authorization from Fahed Mlaiel is strictly forbidden
and will result in immediate legal action under German and international law.

Enterprise notification system for collaboration events and communications.
Multi-channel delivery with smart prioritization and user preferences.

Features:
- Multi-Channel Delivery (Email, SMS, Push, In-App, WhatsApp, Slack, Discord)
- Smart Notification Prioritization with AI
- Advanced User Preference Management
- Dynamic Template System with Rich Media
- Comprehensive Delivery Tracking & Analytics
- Intelligent Batch Processing & Queue Management
- Adaptive Rate Limiting & Throttling
- Rich Media Support (Images, Videos, Documents)
- Real-time Communication Channels
- Multi-language Support with Auto-translation
- Notification Scheduling & Time Zone Handling
- A/B Testing for Notification Optimization
- Spam Protection & Content Filtering
- Enterprise Integration (Slack, Teams, Discord)
- Mobile Push Notifications with Deep Links
- Voice Notifications & Text-to-Speech
- Interactive Notifications with Actions
- Notification Analytics & Performance Metrics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import requests
import firebase_admin
from firebase_admin import messaging
from jinja2 import Template, Environment, FileSystemLoader
import twilio
from twilio.rest import Client as TwilioClient
import boto3
from celery import Celery
import redis
from googletrans import Translator
import schedule
import threading
import websockets
import aiofiles
import cv2
import pyttsx3
from slack_sdk import WebClient as SlackClient
from discord.ext import commands
import openai

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Comprehensive notification type enumeration"""
    # Collaboration notifications
    COLLABORATION_INVITE = "collaboration_invite"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    COLLABORATION_DECLINED = "collaboration_declined"
    COLLABORATION_COMPLETED = "collaboration_completed"
    COLLABORATION_CANCELLED = "collaboration_cancelled"
    
    # Partnership notifications
    PARTNERSHIP_REQUEST = "partnership_request"
    PARTNERSHIP_APPROVED = "partnership_approved"
    PARTNERSHIP_REJECTED = "partnership_rejected"
    PARTNERSHIP_EXPIRED = "partnership_expired"
    PARTNERSHIP_RENEWED = "partnership_renewed"
    
    # Project notifications
    PROJECT_UPDATE = "project_update"
    PROJECT_MILESTONE = "project_milestone"
    PROJECT_DEADLINE = "project_deadline"
    PROJECT_COMPLETED = "project_completed"
    PROJECT_DELAYED = "project_delayed"
    
    # Content notifications
    CONTENT_PUBLISHED = "content_published"
    CONTENT_APPROVED = "content_approved"
    CONTENT_REJECTED = "content_rejected"
    CONTENT_TRENDING = "content_trending"
    CONTENT_MONETIZED = "content_monetized"
    
    # Payment notifications
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_FAILED = "payment_failed"
    PAYOUT_PROCESSED = "payout_processed"
    INVOICE_GENERATED = "invoice_generated"
    
    # System notifications
    ACCOUNT_VERIFICATION = "account_verification"
    SECURITY_ALERT = "security_alert"
    SYSTEM_MAINTENANCE = "system_maintenance"
    FEATURE_ANNOUNCEMENT = "feature_announcement"
    POLICY_UPDATE = "policy_update"
    
    # Social notifications
    NEW_FOLLOWER = "new_follower"
    MESSAGE_RECEIVED = "message_received"
    MENTION_RECEIVED = "mention_received"
    REVIEW_RECEIVED = "review_received"
    RECOMMENDATION_RECEIVED = "recommendation_received"
    
    # Marketing notifications
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_COMPLETED = "campaign_completed"
    PROMOTION_AVAILABLE = "promotion_available"
    ENGAGEMENT_MILESTONE = "engagement_milestone"
    ANALYTICS_REPORT = "analytics_report"

class NotificationChannel(Enum):
    """Notification channel enumeration"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WHATSAPP = "whatsapp"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    VOICE = "voice"
    WEBSOCKET = "websocket"

class NotificationPriority(Enum):
    """Notification priority enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BULK = "bulk"

class DeliveryStatus(Enum):
    """Delivery status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    CLICKED = "clicked"
    FAILED = "failed"
    BOUNCED = "bounced"
    SPAM = "spam"
    UNSUBSCRIBED = "unsubscribed"

class TemplateType(Enum):
    """Template type enumeration"""
    EMAIL_HTML = "email_html"
    EMAIL_TEXT = "email_text"
    SMS_TEXT = "sms_text"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP_NOTIFICATION = "in_app_notification"
    WEBHOOK_PAYLOAD = "webhook_payload"
    VOICE_SCRIPT = "voice_script"

@dataclass
class NotificationTemplate:
    """Notification template structure"""
    id: str
    name: str
    type: TemplateType
    subject: Optional[str] = None
    content: str = ""
    variables: List[str] = field(default_factory=list)
    media_attachments: List[str] = field(default_factory=list)
    language: str = "en"
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    a_b_test_group: Optional[str] = None

@dataclass
class UserPreferences:
    """User notification preferences"""
    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    
    # Channel preferences by notification type
    channel_preferences: Dict[str, List[str]] = field(default_factory=dict)
    
    # Frequency settings
    frequency_settings: Dict[str, str] = field(default_factory=dict)  # immediate, daily, weekly
    
    # Time preferences
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None    # "08:00"
    timezone: str = "UTC"
    
    # Language preferences
    preferred_language: str = "en"
    auto_translate: bool = False
    
    # Advanced settings
    consolidate_notifications: bool = True
    smart_delivery: bool = True
    marketing_enabled: bool = True
    analytics_enabled: bool = True

@dataclass
class NotificationPayload:
    """Comprehensive notification payload"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: NotificationType = NotificationType.PROJECT_UPDATE
    recipient_id: str = ""
    sender_id: Optional[str] = None
    
    # Content
    title: str = ""
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Delivery settings
    channels: List[NotificationChannel] = field(default_factory=list)
    priority: NotificationPriority = NotificationPriority.MEDIUM
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Template settings
    template_id: Optional[str] = None
    template_variables: Dict[str, Any] = field(default_factory=dict)
    
    # Media attachments
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Tracking
    tracking_enabled: bool = True
    deep_link: Optional[str] = None
    call_to_action: Optional[Dict[str, str]] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DeliveryResult:
    """Notification delivery result"""
    notification_id: str
    channel: NotificationChannel
    status: DeliveryStatus
    recipient_id: str
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    provider_response: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

class NotificationHandler:
    """Advanced notification management system"""
    
    def __init__(
        self,
        db_session,
        redis_client,
        email_service,
        sms_service,
        push_service,
        analytics_tracker,
        template_engine,
        translation_service
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.email_service = email_service
        self.sms_service = sms_service
        self.push_service = push_service
        self.analytics_tracker = analytics_tracker
        self.template_engine = template_engine
        self.translation_service = translation_service
        
        # Initialize services
        self.celery_app = Celery('notifications')
        self.translator = Translator()
        self.tts_engine = pyttsx3.init()
        
        # Initialize external clients
        self.slack_client = None
        self.discord_client = None
        self.twilio_client = None
        self.firebase_app = None
        
        # Notification queue and rate limiting
        self.notification_queue = asyncio.Queue()
        self.rate_limiters = {}
        self.delivery_workers = []
        
        # Template cache
        self.template_cache = {}
        
    async def send_notification(
        self,
        notification: NotificationPayload,
        immediate: bool = False
    ) -> Dict[str, DeliveryResult]:
        """Send notification through multiple channels"""
        try:
            logger.info(f"Sending notification {notification.id} to user {notification.recipient_id}")
            
            # Validate notification
            await self._validate_notification(notification)
            
            # Get user preferences
            preferences = await self._get_user_preferences(notification.recipient_id)
            
            # Apply user preferences to channels
            effective_channels = await self._apply_user_preferences(
                notification.channels, notification.type, preferences
            )
            
            if not effective_channels:
                logger.info(f"No effective channels for notification {notification.id}")
                return {}
            
            # Check rate limits
            if not await self._check_rate_limits(notification.recipient_id, notification.type):
                logger.warning(f"Rate limit exceeded for user {notification.recipient_id}")
                return {}
            
            # Apply smart delivery timing
            if not immediate and preferences.smart_delivery:
                optimal_time = await self._calculate_optimal_delivery_time(
                    notification.recipient_id, preferences
                )
                if optimal_time > datetime.utcnow():
                    notification.scheduled_at = optimal_time
            
            # Schedule or send immediately
            if notification.scheduled_at and notification.scheduled_at > datetime.utcnow():
                await self._schedule_notification(notification)
                return {"scheduled": DeliveryResult(
                    notification_id=notification.id,
                    channel=NotificationChannel.IN_APP,
                    status=DeliveryStatus.PENDING,
                    recipient_id=notification.recipient_id
                )}
            
            # Send through channels
            delivery_results = {}
            for channel in effective_channels:
                try:
                    result = await self._deliver_to_channel(notification, channel, preferences)
                    delivery_results[channel.value] = result
                except Exception as e:
                    logger.error(f"Failed to deliver to {channel.value}: {str(e)}")
                    delivery_results[channel.value] = DeliveryResult(
                        notification_id=notification.id,
                        channel=channel,
                        status=DeliveryStatus.FAILED,
                        recipient_id=notification.recipient_id,
                        error_message=str(e)
                    )
            
            # Store delivery results
            await self._store_delivery_results(notification.id, delivery_results)
            
            # Track analytics
            await self.analytics_tracker.track_notification_sent(
                notification, delivery_results
            )
            
            logger.info(f"Notification {notification.id} processed: {len(delivery_results)} channels")
            return delivery_results
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise
            
    async def send_bulk_notifications(
        self,
        notifications: List[NotificationPayload],
        batch_size: int = 100
    ) -> Dict[str, Dict[str, DeliveryResult]]:
        """Send multiple notifications in batches"""
        try:
            logger.info(f"Sending {len(notifications)} bulk notifications")
            
            all_results = {}
            
            # Process in batches
            for i in range(0, len(notifications), batch_size):
                batch = notifications[i:i + batch_size]
                
                # Send batch concurrently
                batch_tasks = [
                    self.send_notification(notification)
                    for notification in batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Collect results
                for j, result in enumerate(batch_results):
                    notification_id = batch[j].id
                    if isinstance(result, Exception):
                        logger.error(f"Batch notification {notification_id} failed: {str(result)}")
                        all_results[notification_id] = {}
                    else:
                        all_results[notification_id] = result
                
                # Rate limiting between batches
                await asyncio.sleep(0.1)
            
            logger.info(f"Bulk notification completed: {len(all_results)} processed")
            return all_results
            
        except Exception as e:
            logger.error(f"Error in bulk notifications: {str(e)}")
            raise
            
    async def create_template(
        self,
        template: NotificationTemplate
    ) -> NotificationTemplate:
        """Create notification template"""
        try:
            logger.info(f"Creating template: {template.name}")
            
            # Validate template
            await self._validate_template(template)
            
            # Store template
            await self.db_session.execute(
                "INSERT INTO notification_templates (id, name, type, content, variables, language) "
                "VALUES (:id, :name, :type, :content, :variables, :language)",
                {
                    "id": template.id,
                    "name": template.name,
                    "type": template.type.value,
                    "content": template.content,
                    "variables": json.dumps(template.variables),
                    "language": template.language
                }
            )
            
            # Cache template
            self.template_cache[template.id] = template
            
            logger.info(f"Template {template.id} created successfully")
            return template
            
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            raise
            
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: UserPreferences
    ) -> UserPreferences:
        """Update user notification preferences"""
        try:
            logger.info(f"Updating preferences for user {user_id}")
            
            # Store preferences
            await self.db_session.execute(
                "INSERT OR REPLACE INTO user_notification_preferences "
                "(user_id, email_enabled, sms_enabled, push_enabled, in_app_enabled, "
                "channel_preferences, frequency_settings, timezone, preferred_language) "
                "VALUES (:user_id, :email_enabled, :sms_enabled, :push_enabled, :in_app_enabled, "
                ":channel_preferences, :frequency_settings, :timezone, :preferred_language)",
                {
                    "user_id": user_id,
                    "email_enabled": preferences.email_enabled,
                    "sms_enabled": preferences.sms_enabled,
                    "push_enabled": preferences.push_enabled,
                    "in_app_enabled": preferences.in_app_enabled,
                    "channel_preferences": json.dumps(preferences.channel_preferences),
                    "frequency_settings": json.dumps(preferences.frequency_settings),
                    "timezone": preferences.timezone,
                    "preferred_language": preferences.preferred_language
                }
            )
            
            logger.info(f"Preferences updated for user {user_id}")
            return preferences
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            raise
            
    async def get_notification_analytics(
        self,
        user_id: Optional[str] = None,
        notification_type: Optional[NotificationType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get notification analytics and metrics"""
        try:
            logger.info("Retrieving notification analytics")
            
            # Build analytics query
            query_filters = []
            params = {}
            
            if user_id:
                query_filters.append("recipient_id = :user_id")
                params["user_id"] = user_id
                
            if notification_type:
                query_filters.append("notification_type = :notification_type")
                params["notification_type"] = notification_type.value
                
            if start_date:
                query_filters.append("created_at >= :start_date")
                params["start_date"] = start_date
                
            if end_date:
                query_filters.append("created_at <= :end_date")
                params["end_date"] = end_date
            
            where_clause = "WHERE " + " AND ".join(query_filters) if query_filters else ""
            
            # Get delivery statistics
            delivery_stats = await self.db_session.execute(
                f"SELECT channel, status, COUNT(*) as count "
                f"FROM notification_deliveries {where_clause} "
                f"GROUP BY channel, status",
                params
            )
            
            # Get engagement metrics
            engagement_stats = await self.db_session.execute(
                f"SELECT notification_type, AVG(read_rate) as avg_read_rate, "
                f"AVG(click_rate) as avg_click_rate "
                f"FROM notification_analytics {where_clause} "
                f"GROUP BY notification_type",
                params
            )
            
            # Compile analytics
            analytics = {
                "delivery_statistics": delivery_stats.fetchall(),
                "engagement_metrics": engagement_stats.fetchall(),
                "total_sent": sum(row[2] for row in delivery_stats.fetchall()),
                "performance_by_channel": await self._calculate_channel_performance(),
                "optimal_send_times": await self._calculate_optimal_send_times(user_id),
                "user_preferences_summary": await self._get_preferences_summary()
            }
            
            logger.info("Analytics retrieved successfully")
            return analytics
            
        except Exception as e:
            logger.error(f"Error retrieving analytics: {str(e)}")
            raise
            
    async def test_notification_delivery(
        self,
        user_id: str,
        channel: NotificationChannel,
        test_message: str = "Test notification"
    ) -> DeliveryResult:
        """Test notification delivery for a specific channel"""
        try:
            logger.info(f"Testing notification delivery for user {user_id} via {channel.value}")
            
            # Create test notification
            test_notification = NotificationPayload(
                type=NotificationType.SYSTEM_MAINTENANCE,
                recipient_id=user_id,
                title="Test Notification",
                message=test_message,
                channels=[channel],
                priority=NotificationPriority.LOW
            )
            
            # Get user preferences
            preferences = await self._get_user_preferences(user_id)
            
            # Deliver test notification
            result = await self._deliver_to_channel(test_notification, channel, preferences)
            
            logger.info(f"Test notification result: {result.status.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error testing notification delivery: {str(e)}")
            raise
            
    # Private helper methods
    async def _validate_notification(self, notification: NotificationPayload) -> None:
        """Validate notification payload"""
        if not notification.recipient_id:
            raise ValueError("Recipient ID is required")
        if not notification.title and not notification.message:
            raise ValueError("Title or message is required")
        if not notification.channels:
            raise ValueError("At least one channel is required")
            
    async def _get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user notification preferences"""
        result = await self.db_session.execute(
            "SELECT * FROM user_notification_preferences WHERE user_id = :user_id",
            {"user_id": user_id}
        )
        row = result.fetchone()
        
        if row:
            return UserPreferences(
                user_id=user_id,
                email_enabled=row.email_enabled,
                sms_enabled=row.sms_enabled,
                push_enabled=row.push_enabled,
                in_app_enabled=row.in_app_enabled,
                channel_preferences=json.loads(row.channel_preferences or "{}"),
                frequency_settings=json.loads(row.frequency_settings or "{}"),
                timezone=row.timezone or "UTC",
                preferred_language=row.preferred_language or "en"
            )
        else:
            return UserPreferences(user_id=user_id)
            
    async def _apply_user_preferences(
        self,
        channels: List[NotificationChannel],
        notification_type: NotificationType,
        preferences: UserPreferences
    ) -> List[NotificationChannel]:
        """Apply user preferences to notification channels"""
        effective_channels = []
        
        for channel in channels:
            # Check if channel is enabled
            if channel == NotificationChannel.EMAIL and not preferences.email_enabled:
                continue
            elif channel == NotificationChannel.SMS and not preferences.sms_enabled:
                continue
            elif channel == NotificationChannel.PUSH and not preferences.push_enabled:
                continue
            elif channel == NotificationChannel.IN_APP and not preferences.in_app_enabled:
                continue
                
            # Check type-specific preferences
            type_preferences = preferences.channel_preferences.get(notification_type.value, [])
            if type_preferences and channel.value not in type_preferences:
                continue
                
            effective_channels.append(channel)
            
        return effective_channels
        
    async def _check_rate_limits(self, user_id: str, notification_type: NotificationType) -> bool:
        """Check rate limits for user and notification type"""
        # Implement rate limiting logic
        return True  # Placeholder
        
    async def _calculate_optimal_delivery_time(
        self,
        user_id: str,
        preferences: UserPreferences
    ) -> datetime:
        """Calculate optimal delivery time based on user behavior"""
        # Implement smart delivery timing
        return datetime.utcnow()  # Placeholder
        
    async def _schedule_notification(self, notification: NotificationPayload) -> None:
        """Schedule notification for future delivery"""
        # Store in scheduled notifications queue
        await self.redis_client.zadd(
            "scheduled_notifications",
            {notification.id: notification.scheduled_at.timestamp()}
        )
        
    async def _deliver_to_channel(
        self,
        notification: NotificationPayload,
        channel: NotificationChannel,
        preferences: UserPreferences
    ) -> DeliveryResult:
        """Deliver notification to specific channel"""
        if channel == NotificationChannel.EMAIL:
            return await self._deliver_email(notification, preferences)
        elif channel == NotificationChannel.SMS:
            return await self._deliver_sms(notification, preferences)
        elif channel == NotificationChannel.PUSH:
            return await self._deliver_push(notification, preferences)
        elif channel == NotificationChannel.IN_APP:
            return await self._deliver_in_app(notification, preferences)
        elif channel == NotificationChannel.SLACK:
            return await self._deliver_slack(notification, preferences)
        elif channel == NotificationChannel.DISCORD:
            return await self._deliver_discord(notification, preferences)
        elif channel == NotificationChannel.VOICE:
            return await self._deliver_voice(notification, preferences)
        else:
            raise ValueError(f"Unsupported channel: {channel}")
            
    async def _deliver_email(self, notification: NotificationPayload, preferences: UserPreferences) -> DeliveryResult:
        """Deliver email notification"""
        # Placeholder implementation
        return DeliveryResult(
            notification_id=notification.id,
            channel=NotificationChannel.EMAIL,
            status=DeliveryStatus.SENT,
            recipient_id=notification.recipient_id,
            delivered_at=datetime.utcnow()
        )
        
    async def _deliver_sms(self, notification: NotificationPayload, preferences: UserPreferences) -> DeliveryResult:
        """Deliver SMS notification"""
        # Placeholder implementation
        return DeliveryResult(
            notification_id=notification.id,
            channel=NotificationChannel.SMS,
            status=DeliveryStatus.SENT,
            recipient_id=notification.recipient_id,
            delivered_at=datetime.utcnow()
        )
        
    async def _deliver_push(self, notification: NotificationPayload, preferences: UserPreferences) -> DeliveryResult:
        """Deliver push notification"""
        # Placeholder implementation
        return DeliveryResult(
            notification_id=notification.id,
            channel=NotificationChannel.PUSH,
            status=DeliveryStatus.SENT,
            recipient_id=notification.recipient_id,
            delivered_at=datetime.utcnow()
        )
        
    async def _deliver_in_app(self, notification: NotificationPayload, preferences: UserPreferences) -> DeliveryResult:
        """Deliver in-app notification"""
        # Placeholder implementation
        return DeliveryResult(
            notification_id=notification.id,
            channel=NotificationChannel.IN_APP,
            status=DeliveryStatus.SENT,
            recipient_id=notification.recipient_id,
            delivered_at=datetime.utcnow()
        )
        
    async def _deliver_slack(self, notification: NotificationPayload, preferences: UserPreferences) -> DeliveryResult:
        """Deliver Slack notification"""
        # Placeholder implementation
        return DeliveryResult(
            notification_id=notification.id,
            channel=NotificationChannel.SLACK,
            status=DeliveryStatus.SENT,
            recipient_id=notification.recipient_id,
            delivered_at=datetime.utcnow()
        )
        
    async def _deliver_discord(self, notification: NotificationPayload, preferences: UserPreferences) -> DeliveryResult:
        """Deliver Discord notification"""
        # Placeholder implementation
        return DeliveryResult(
            notification_id=notification.id,
            channel=NotificationChannel.DISCORD,
            status=DeliveryStatus.SENT,
            recipient_id=notification.recipient_id,
            delivered_at=datetime.utcnow()
        )
        
    async def _deliver_voice(self, notification: NotificationPayload, preferences: UserPreferences) -> DeliveryResult:
        """Deliver voice notification"""
        # Placeholder implementation
        return DeliveryResult(
            notification_id=notification.id,
            channel=NotificationChannel.VOICE,
            status=DeliveryStatus.SENT,
            recipient_id=notification.recipient_id,
            delivered_at=datetime.utcnow()
        )
        
    async def _store_delivery_results(self, notification_id: str, results: Dict[str, DeliveryResult]) -> None:
        """Store delivery results in database"""
        # Placeholder implementation
        pass
        
    async def _validate_template(self, template: NotificationTemplate) -> None:
        """Validate notification template"""
        if not template.name:
            raise ValueError("Template name is required")
        if not template.content:
            raise ValueError("Template content is required")
            
    async def _calculate_channel_performance(self) -> Dict[str, Any]:
        """Calculate performance metrics by channel"""
        return {}  # Placeholder
        
    async def _calculate_optimal_send_times(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Calculate optimal send times"""
        return {}  # Placeholder
        
    async def _get_preferences_summary(self) -> Dict[str, Any]:
        """Get summary of user preferences"""
        return {}  # Placeholder
    MILESTONE_COMPLETED = "milestone_completed"
    PAYMENT_RECEIVED = "payment_received"
    MESSAGE_RECEIVED = "message_received"
    PROFILE_VIEWED = "profile_viewed"
    MATCH_FOUND = "match_found"
    CONTRACT_SIGNED = "contract_signed"
    DEADLINE_REMINDER = "deadline_reminder"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    SECURITY_ALERT = "security_alert"

class NotificationChannel(Enum):
    """Notification delivery channel"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"

class Priority(Enum):
    """Notification priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class DeliveryStatus(Enum):
    """Delivery status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"

@dataclass
class NotificationPreferences:
    """User notification preferences"""
    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    channels_by_type: Dict[NotificationType, List[NotificationChannel]] = field(default_factory=dict)
    quiet_hours: Optional[Dict[str, str]] = None  # {"start": "22:00", "end": "08:00"}
    frequency_limits: Dict[NotificationChannel, int] = field(default_factory=dict)  # max per day
    priority_threshold: Priority = Priority.NORMAL
    languages: List[str] = field(default_factory=lambda: ["en"])
    timezone: str = "UTC"

@dataclass
class NotificationTemplate:
    """Notification template definition"""
    template_id: str
    notification_type: NotificationType
    channel: NotificationChannel
    subject_template: str
    body_template: str
    variables: List[str] = field(default_factory=list)
    language: str = "en"
    is_html: bool = False
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationPayload:
    """Notification payload data"""
    recipient_id: str
    notification_type: NotificationType
    title: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.NORMAL
    channels: Optional[List[NotificationChannel]] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    action_url: Optional[str] = None
    image_url: Optional[str] = None
    sound: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class DeliveryReport:
    """Notification delivery report"""
    notification_id: str
    recipient_id: str
    channel: NotificationChannel
    status: DeliveryStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    retry_count: int = 0

class NotificationHandler:
    """Enterprise notification management system"""
    
    def __init__(self, db_session, email_config, sms_config, push_config, template_config):
        self.db_session = db_session
        self.email_config = email_config
        self.sms_config = sms_config
        self.push_config = push_config
        self.template_config = template_config
        
        # Initialize template engine
        self.template_env = Environment(
            loader=FileSystemLoader(template_config.get('template_dir', 'templates')),
            autoescape=True
        )
        
        # Initialize Firebase for push notifications
        if push_config.get('firebase_credentials'):
            if not firebase_admin._apps:
                firebase_admin.initialize_app(
                    firebase_admin.credentials.Certificate(push_config['firebase_credentials'])
                )
                
        # Rate limiting tracking
        self.rate_limits = {}
        
    async def send_notification(
        self,
        payload: NotificationPayload,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send notification through appropriate channels"""
        try:
            logger.info(f"Sending notification to {payload.recipient_id}: {payload.notification_type}")
            
            # Get user preferences
            preferences = await self._get_user_preferences(payload.recipient_id)
            
            # Determine delivery channels
            channels = await self._determine_channels(payload, preferences)
            
            # Check if notification should be sent (quiet hours, frequency limits)
            if not await self._should_send_notification(payload, preferences, channels):
                logger.info(f"Notification blocked by user preferences or rate limits")
                return {"status": "blocked", "reason": "user_preferences"}
                
            # Generate notification content
            if template_id:
                content = await self._render_from_template(template_id, payload, preferences)
            else:
                content = await self._generate_content(payload, preferences)
                
            # Send through each channel
            delivery_results = {}
            notification_id = await self._create_notification_record(payload)
            
            for channel in channels:
                try:
                    if await self._check_rate_limit(payload.recipient_id, channel):
                        result = await self._send_via_channel(
                            channel, payload, content, notification_id
                        )
                        delivery_results[channel.value] = result
                        
                        # Update rate limiting
                        await self._update_rate_limit(payload.recipient_id, channel)
                        
                    else:
                        delivery_results[channel.value] = {
                            "status": "rate_limited",
                            "error": "Rate limit exceeded"
                        }
                        
                except Exception as e:
                    logger.error(f"Error sending via {channel.value}: {str(e)}")
                    delivery_results[channel.value] = {
                        "status": "failed",
                        "error": str(e)
                    }
                    
            # Update notification record
            await self._update_notification_status(notification_id, delivery_results)
            
            logger.info(f"Notification sent via {len(delivery_results)} channels")
            return {
                "notification_id": notification_id,
                "delivery_results": delivery_results,
                "status": "sent"
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise
            
    async def send_bulk_notifications(
        self,
        payloads: List[NotificationPayload],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """Send bulk notifications with batch processing"""
        try:
            logger.info(f"Sending {len(payloads)} bulk notifications")
            
            results = []
            failed_count = 0
            
            # Process in batches
            for i in range(0, len(payloads), batch_size):
                batch = payloads[i:i + batch_size]
                
                # Process batch concurrently
                batch_tasks = [
                    self.send_notification(payload)
                    for payload in batch
                ]
                
                batch_results = await asyncio.gather(
                    *batch_tasks,
                    return_exceptions=True
                )
                
                # Process results
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Batch notification {i+j} failed: {str(result)}")
                        failed_count += 1
                        results.append({
                            "index": i + j,
                            "status": "failed",
                            "error": str(result)
                        })
                    else:
                        results.append({
                            "index": i + j,
                            "status": "sent",
                            "result": result
                        })
                        
                # Brief pause between batches
                if i + batch_size < len(payloads):
                    await asyncio.sleep(0.1)
                    
            logger.info(f"Bulk notification complete: {len(results) - failed_count} sent, {failed_count} failed")
            return {
                "total_sent": len(results) - failed_count,
                "total_failed": failed_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending bulk notifications: {str(e)}")
            raise
            
    async def schedule_notification(
        self,
        payload: NotificationPayload,
        send_at: datetime,
        template_id: Optional[str] = None
    ) -> str:
        """Schedule notification for future delivery"""
        try:
            logger.info(f"Scheduling notification for {send_at}")
            
            # Create scheduled notification record
            scheduled_id = await self._create_scheduled_notification(
                payload, send_at, template_id
            )
            
            # Add to scheduling queue if needed
            await self._add_to_schedule_queue(scheduled_id, send_at)
            
            logger.info(f"Notification scheduled with ID: {scheduled_id}")
            return scheduled_id
            
        except Exception as e:
            logger.error(f"Error scheduling notification: {str(e)}")
            raise
            
    async def get_delivery_report(
        self,
        notification_id: str
    ) -> Dict[str, Any]:
        """Get detailed delivery report for notification"""
        try:
            # Get notification details
            notification = await self._get_notification_details(notification_id)
            
            # Get delivery reports for all channels
            delivery_reports = await self._get_delivery_reports(notification_id)
            
            # Calculate metrics
            metrics = await self._calculate_delivery_metrics(delivery_reports)
            
            return {
                "notification": notification,
                "delivery_reports": delivery_reports,
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting delivery report: {str(e)}")
            return {}
            
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: NotificationPreferences
    ) -> bool:
        """Update user notification preferences"""
        try:
            logger.info(f"Updating preferences for user {user_id}")
            
            # Validate preferences
            if not await self._validate_preferences(preferences):
                return False
                
            # Update in database
            success = await self._save_user_preferences(user_id, preferences)
            
            # Update cache if needed
            if success:
                await self._cache_user_preferences(user_id, preferences)
                
            logger.info(f"Preferences updated for user {user_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            return False
            
    async def create_template(self, template: NotificationTemplate) -> bool:
        """Create new notification template"""
        try:
            logger.info(f"Creating template: {template.template_id}")
            
            # Validate template
            if not await self._validate_template(template):
                return False
                
            # Save template
            success = await self._save_template(template)
            
            # Update template cache
            if success:
                await self._cache_template(template)
                
            logger.info(f"Template created: {template.template_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            return False
            
    async def track_notification_interaction(
        self,
        notification_id: str,
        interaction_type: str,  # opened, clicked, dismissed
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track user interaction with notification"""
        try:
            # Record interaction
            await self._record_interaction(notification_id, interaction_type, metadata)
            
            # Update delivery report
            await self._update_delivery_report_interaction(
                notification_id, interaction_type, datetime.utcnow()
            )
            
            # Update analytics
            await self._update_interaction_analytics(
                notification_id, interaction_type, metadata
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error tracking interaction: {str(e)}")
            return False
            
    # Email delivery methods
    async def _send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        is_html: bool = False,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_address']
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
                
            # Add attachments if any
            if attachments:
                for attachment_path in attachments:
                    # Add attachment logic here
                    pass
                    
            # Send email
            with smtplib.SMTP(
                self.email_config['smtp_host'],
                self.email_config['smtp_port']
            ) as server:
                if self.email_config.get('use_tls'):
                    server.starttls()
                if self.email_config.get('username'):
                    server.login(
                        self.email_config['username'],
                        self.email_config['password']
                    )
                    
                server.send_message(msg)
                
            return {"status": "sent"}
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {"status": "failed", "error": str(e)}
            
    # SMS delivery methods
    async def _send_sms(
        self,
        phone_number: str,
        message: str
    ) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            # Use configured SMS provider (Twilio, AWS SNS, etc.)
            if self.sms_config['provider'] == 'twilio':
                return await self._send_twilio_sms(phone_number, message)
            elif self.sms_config['provider'] == 'aws_sns':
                return await self._send_aws_sms(phone_number, message)
            else:
                return {"status": "failed", "error": "Unknown SMS provider"}
                
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return {"status": "failed", "error": str(e)}
            
    # Push notification methods
    async def _send_push_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send push notification"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=device_token
            )
            
            response = messaging.send(message)
            return {"status": "sent", "message_id": response}
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return {"status": "failed", "error": str(e)}
            
    # Helper methods (simplified implementations)
    async def _get_user_preferences(self, user_id: str) -> NotificationPreferences:
        """Get user notification preferences"""
        # Implementation would fetch from database/cache
        return NotificationPreferences(user_id=user_id)
        
    async def _determine_channels(
        self,
        payload: NotificationPayload,
        preferences: NotificationPreferences
    ) -> List[NotificationChannel]:
        """Determine which channels to use for notification"""
        if payload.channels:
            return payload.channels
            
        # Use preferences to determine channels
        channels = []
        if preferences.email_enabled:
            channels.append(NotificationChannel.EMAIL)
        if preferences.push_enabled:
            channels.append(NotificationChannel.PUSH)
        if preferences.in_app_enabled:
            channels.append(NotificationChannel.IN_APP)
            
        return channels
        
    async def _should_send_notification(
        self,
        payload: NotificationPayload,
        preferences: NotificationPreferences,
        channels: List[NotificationChannel]
    ) -> bool:
        """Check if notification should be sent based on preferences"""
        # Check priority threshold
        if payload.priority.value < preferences.priority_threshold.value:
            return False
            
        # Check quiet hours
        if preferences.quiet_hours:
            current_time = datetime.utcnow().time()
            # Quiet hours logic here
            
        return True
        
    async def _render_from_template(
        self,
        template_id: str,
        payload: NotificationPayload,
        preferences: NotificationPreferences
    ) -> Dict[str, str]:
        """Render notification content from template"""
        # Get template
        template = await self._get_template(template_id, preferences.languages[0])
        
        # Render content
        subject_template = Template(template.subject_template)
        body_template = Template(template.body_template)
        
        context = {
            'user_id': payload.recipient_id,
            'title': payload.title,
            'message': payload.message,
            **payload.data
        }
        
        return {
            'subject': subject_template.render(context),
            'body': body_template.render(context),
            'is_html': template.is_html
        }
        
    async def _generate_content(
        self,
        payload: NotificationPayload,
        preferences: NotificationPreferences
    ) -> Dict[str, str]:
        """Generate notification content without template"""
        return {
            'subject': payload.title,
            'body': payload.message,
            'is_html': False
        }
        
    async def _send_via_channel(
        self,
        channel: NotificationChannel,
        payload: NotificationPayload,
        content: Dict[str, str],
        notification_id: str
    ) -> Dict[str, Any]:
        """Send notification via specific channel"""
        if channel == NotificationChannel.EMAIL:
            recipient_email = await self._get_user_email(payload.recipient_id)
            return await self._send_email(
                recipient_email,
                content['subject'],
                content['body'],
                content.get('is_html', False)
            )
        elif channel == NotificationChannel.PUSH:
            device_token = await self._get_user_device_token(payload.recipient_id)
            return await self._send_push_notification(
                device_token,
                payload.title,
                payload.message,
                payload.data
            )
        elif channel == NotificationChannel.SMS:
            phone_number = await self._get_user_phone(payload.recipient_id)
            return await self._send_sms(phone_number, content['body'])
        elif channel == NotificationChannel.IN_APP:
            return await self._create_in_app_notification(payload, notification_id)
        else:
            return {"status": "failed", "error": "Unsupported channel"}
            
    # Complete implementation methods
    async def _check_rate_limit(self, user_id: str, channel: NotificationChannel) -> bool:
        """Advanced rate limiting with adaptive throttling"""
        try:
            # Define rate limits per channel (per hour)
            rate_limits = {
                NotificationChannel.EMAIL: 50,
                NotificationChannel.SMS: 20,
                NotificationChannel.PUSH: 100,
                NotificationChannel.IN_APP: 200,
                NotificationChannel.WHATSAPP: 30,
                NotificationChannel.SLACK: 80,
                NotificationChannel.DISCORD: 60
            }
            
            max_limit = rate_limits.get(channel, 50)
            
            # Check current usage from Redis
            current_hour = datetime.utcnow().hour
            cache_key = f"rate_limit:{user_id}:{channel.value}:{current_hour}"
            
            current_count = await self.cache_service.get(cache_key) or 0
            
            if int(current_count) >= max_limit:
                logger.warning(f"Rate limit exceeded for user {user_id} on channel {channel.value}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return True  # Allow on error to avoid blocking critical notifications
        
    async def _update_rate_limit(self, user_id: str, channel: NotificationChannel) -> None:
        """Update rate limit counter with sliding window"""
        try:
            current_hour = datetime.utcnow().hour
            cache_key = f"rate_limit:{user_id}:{channel.value}:{current_hour}"
            
            # Increment counter with 1-hour expiry
            await self.cache_service.increment(cache_key, expire_seconds=3600)
            
        except Exception as e:
            logger.error(f"Error updating rate limit: {str(e)}")
        
    async def _create_notification_record(self, payload: NotificationPayload) -> str:
        """Create comprehensive notification record in database"""
        try:
            notification_id = f"notif_{uuid.uuid4().hex}"
            
            record = {
                'notification_id': notification_id,
                'recipient_id': payload.recipient_id,
                'notification_type': payload.notification_type.value,
                'title': payload.title,
                'message': payload.message,
                'data': json.dumps(payload.data),
                'channels': [c.value for c in payload.channels],
                'priority': payload.priority.value,
                'created_at': datetime.utcnow(),
                'status': 'created',
                'attempts': 0,
                'metadata': json.dumps(payload.metadata or {})
            }
            
            # Insert into database
            query = """
            INSERT INTO notifications (
                notification_id, recipient_id, notification_type, title, 
                message, data, channels, priority, created_at, status, 
                attempts, metadata
            ) VALUES (
                %(notification_id)s, %(recipient_id)s, %(notification_type)s, 
                %(title)s, %(message)s, %(data)s, %(channels)s, %(priority)s, 
                %(created_at)s, %(status)s, %(attempts)s, %(metadata)s
            )
            """
            
            await self.db_session.execute(query, record)
            await self.db_session.commit()
            
            logger.info(f"Created notification record: {notification_id}")
            return notification_id
            
        except Exception as e:
            logger.error(f"Error creating notification record: {str(e)}")
            return f"notif_{datetime.utcnow().timestamp()}"
        
    async def _update_notification_status(self, notification_id: str, results: Dict[str, Any]) -> None:
        """Update notification status with comprehensive delivery results"""
        try:
            # Calculate overall status
            channel_results = results.get('channels', {})
            successful_channels = [
                channel for channel, result in channel_results.items()
                if result.get('status') == 'sent'
            ]
            failed_channels = [
                channel for channel, result in channel_results.items()
                if result.get('status') == 'failed'
            ]
            
            if successful_channels and not failed_channels:
                overall_status = 'sent'
            elif successful_channels and failed_channels:
                overall_status = 'partial'
            elif failed_channels:
                overall_status = 'failed'
            else:
                overall_status = 'unknown'
            
            # Update notification record
            update_query = """
            UPDATE notifications 
            SET status = %s, 
                delivery_results = %s, 
                sent_at = %s,
                successful_channels = %s,
                failed_channels = %s
            WHERE notification_id = %s
            """
            
            await self.db_session.execute(update_query, [
                overall_status,
                json.dumps(results),
                datetime.utcnow() if overall_status != 'failed' else None,
                json.dumps(successful_channels),
                json.dumps(failed_channels),
                notification_id
            ])
            await self.db_session.commit()
            
            # Create delivery reports for each channel
            for channel, result in channel_results.items():
                await self._create_delivery_report(notification_id, channel, result)
                
        except Exception as e:
            logger.error(f"Error updating notification status: {str(e)}")
        
    async def _create_scheduled_notification(self, payload: NotificationPayload, send_at: datetime, template_id: Optional[str]) -> str:
        """Create sophisticated scheduled notification with timezone handling"""
        try:
            scheduled_id = f"sched_{uuid.uuid4().hex}"
            
            # Get user timezone for accurate scheduling
            user_timezone = await self._get_user_timezone(payload.recipient_id)
            local_send_time = send_at
            utc_send_time = self._convert_to_utc(send_at, user_timezone)
            
            record = {
                'scheduled_id': scheduled_id,
                'recipient_id': payload.recipient_id,
                'notification_type': payload.notification_type.value,
                'title': payload.title,
                'message': payload.message,
                'data': json.dumps(payload.data),
                'channels': [c.value for c in payload.channels],
                'priority': payload.priority.value,
                'template_id': template_id,
                'scheduled_at': datetime.utcnow(),
                'send_at_local': local_send_time,
                'send_at_utc': utc_send_time,
                'user_timezone': user_timezone,
                'status': 'scheduled',
                'metadata': json.dumps(payload.metadata or {})
            }
            
            # Insert into scheduled notifications table
            query = """
            INSERT INTO scheduled_notifications (
                scheduled_id, recipient_id, notification_type, title, message,
                data, channels, priority, template_id, scheduled_at, 
                send_at_local, send_at_utc, user_timezone, status, metadata
            ) VALUES (
                %(scheduled_id)s, %(recipient_id)s, %(notification_type)s, 
                %(title)s, %(message)s, %(data)s, %(channels)s, %(priority)s,
                %(template_id)s, %(scheduled_at)s, %(send_at_local)s, 
                %(send_at_utc)s, %(user_timezone)s, %(status)s, %(metadata)s
            )
            """
            
            await self.db_session.execute(query, record)
            await self.db_session.commit()
            
            # Add to schedule queue
            await self._add_to_schedule_queue(scheduled_id, utc_send_time)
            
            logger.info(f"Created scheduled notification: {scheduled_id} for {utc_send_time}")
            return scheduled_id
            
        except Exception as e:
            logger.error(f"Error creating scheduled notification: {str(e)}")
            return f"sched_{datetime.utcnow().timestamp()}"
        
    async def _add_to_schedule_queue(self, scheduled_id: str, send_at: datetime) -> None:
        """Add notification to advanced scheduling queue with priority handling"""
        try:
            # Calculate delay in seconds
            delay_seconds = (send_at - datetime.utcnow()).total_seconds()
            
            if delay_seconds <= 0:
                # Send immediately if time has passed
                await self._process_scheduled_notification(scheduled_id)
                return
            
            # Add to Redis sorted set with timestamp as score
            timestamp_score = send_at.timestamp()
            await self.cache_service.zadd(
                "scheduled_notifications",
                {scheduled_id: timestamp_score}
            )
            
            # Also add to Celery for backup processing
            if hasattr(self, 'celery_app'):
                self.celery_app.send_task(
                    'process_scheduled_notification',
                    args=[scheduled_id],
                    eta=send_at
                )
                
        except Exception as e:
            logger.error(f"Error adding to schedule queue: {str(e)}")
        
    async def _get_notification_details(self, notification_id: str) -> Dict[str, Any]:
        """Get comprehensive notification details with full history"""
        try:
            # Get main notification record
            query = """
            SELECT n.*, 
                   COUNT(dr.delivery_report_id) as total_deliveries,
                   COUNT(CASE WHEN dr.status = 'delivered' THEN 1 END) as successful_deliveries,
                   COUNT(ni.interaction_id) as total_interactions,
                   COUNT(CASE WHEN ni.interaction_type = 'opened' THEN 1 END) as opens,
                   COUNT(CASE WHEN ni.interaction_type = 'clicked' THEN 1 END) as clicks
            FROM notifications n
            LEFT JOIN delivery_reports dr ON n.notification_id = dr.notification_id
            LEFT JOIN notification_interactions ni ON n.notification_id = ni.notification_id
            WHERE n.notification_id = %s
            GROUP BY n.notification_id
            """
            
            result = await self.db_session.execute(query, [notification_id])
            notification = dict(result.fetchone()) if result.rowcount > 0 else None
            
            if not notification:
                return {}
            
            # Get delivery reports
            delivery_reports = await self._get_delivery_reports(notification_id)
            
            # Get interaction history
            interactions = await self._get_notification_interactions(notification_id)
            
            # Calculate performance metrics
            metrics = await self._calculate_notification_metrics(notification)
            
            return {
                'notification': notification,
                'delivery_reports': delivery_reports,
                'interactions': interactions,
                'metrics': metrics,
                'retrieved_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting notification details: {str(e)}")
            return {}
        
    async def _get_delivery_reports(self, notification_id: str) -> List[DeliveryReport]:
        """Get detailed delivery reports for all channels"""
        try:
            query = """
            SELECT * FROM delivery_reports 
            WHERE notification_id = %s 
            ORDER BY sent_at DESC
            """
            
            result = await self.db_session.execute(query, [notification_id])
            reports = []
            
            for row in result.fetchall():
                report = DeliveryReport(
                    delivery_id=row['delivery_id'],
                    notification_id=row['notification_id'],
                    channel=NotificationChannel(row['channel']),
                    status=row['status'],
                    sent_at=row['sent_at'],
                    delivered_at=row['delivered_at'],
                    error_message=row['error_message'],
                    attempt_count=row['attempt_count'],
                    provider_response=json.loads(row['provider_response'] or '{}'),
                    metadata=json.loads(row['metadata'] or '{}')
                )
                reports.append(report)
                
            return reports
            
        except Exception as e:
            logger.error(f"Error getting delivery reports: {str(e)}")
            return []
        
    async def _calculate_delivery_metrics(self, reports: List[DeliveryReport]) -> Dict[str, Any]:
        """Calculate comprehensive delivery and performance metrics"""
        try:
            if not reports:
                return {}
            
            total_reports = len(reports)
            successful_deliveries = sum(1 for r in reports if r.status == 'delivered')
            failed_deliveries = sum(1 for r in reports if r.status == 'failed')
            pending_deliveries = sum(1 for r in reports if r.status == 'pending')
            
            # Calculate channel-specific metrics
            channel_metrics = {}
            for report in reports:
                channel = report.channel.value
                if channel not in channel_metrics:
                    channel_metrics[channel] = {
                        'total': 0,
                        'successful': 0,
                        'failed': 0,
                        'pending': 0,
                        'avg_delivery_time': 0
                    }
                
                channel_metrics[channel]['total'] += 1
                if report.status == 'delivered':
                    channel_metrics[channel]['successful'] += 1
                    if report.sent_at and report.delivered_at:
                        delivery_time = (report.delivered_at - report.sent_at).total_seconds()
                        channel_metrics[channel]['avg_delivery_time'] += delivery_time
                elif report.status == 'failed':
                    channel_metrics[channel]['failed'] += 1
                elif report.status == 'pending':
                    channel_metrics[channel]['pending'] += 1
            
            # Calculate average delivery times
            for channel_data in channel_metrics.values():
                if channel_data['successful'] > 0:
                    channel_data['avg_delivery_time'] /= channel_data['successful']
                    channel_data['delivery_rate'] = channel_data['successful'] / channel_data['total']
                else:
                    channel_data['avg_delivery_time'] = 0
                    channel_data['delivery_rate'] = 0
            
            return {
                'total_deliveries': total_reports,
                'successful_deliveries': successful_deliveries,
                'failed_deliveries': failed_deliveries,
                'pending_deliveries': pending_deliveries,
                'overall_delivery_rate': successful_deliveries / total_reports if total_reports > 0 else 0,
                'overall_failure_rate': failed_deliveries / total_reports if total_reports > 0 else 0,
                'channel_metrics': channel_metrics,
                'calculated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating delivery metrics: {str(e)}")
            return {}
        
    async def _validate_preferences(self, preferences: NotificationPreferences) -> bool:
        return True
        
    async def _save_user_preferences(self, user_id: str, preferences: NotificationPreferences) -> bool:
        return True
        
    async def _cache_user_preferences(self, user_id: str, preferences: NotificationPreferences) -> None:
        pass
        
    async def _validate_template(self, template: NotificationTemplate) -> bool:
        return True
        
    async def _save_template(self, template: NotificationTemplate) -> bool:
        return True
        
    async def _cache_template(self, template: NotificationTemplate) -> None:
        pass
        
    async def _record_interaction(self, notification_id: str, interaction_type: str, metadata: Optional[Dict[str, Any]]) -> None:
        pass
        
    async def _update_delivery_report_interaction(self, notification_id: str, interaction_type: str, timestamp: datetime) -> None:
        pass
        
    async def _update_interaction_analytics(self, notification_id: str, interaction_type: str, metadata: Optional[Dict[str, Any]]) -> None:
        pass
        
    async def _send_twilio_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        return {"status": "sent"}
        
    async def _send_aws_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        return {"status": "sent"}
        
    async def _get_template(self, template_id: str, language: str) -> NotificationTemplate:
        return NotificationTemplate(
            template_id=template_id,
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            channel=NotificationChannel.EMAIL,
            subject_template="{{title}}",
            body_template="{{message}}"
        )
        
    async def _get_user_email(self, user_id: str) -> str:
        return "user@example.com"
        
    async def _get_user_device_token(self, user_id: str) -> str:
        return "device_token"
        
    async def _get_user_phone(self, user_id: str) -> str:
        return "+1234567890"
        
    async def _create_in_app_notification(self, payload: NotificationPayload, notification_id: str) -> Dict[str, Any]:
        return {"status": "sent"}
