"""
Creator Notification Service - Enterprise Microservice
====================================================

Advanced notification management system for creators with multi-channel delivery,
intelligent scheduling, and personalized content targeting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationStatus(str, Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    """Types of notifications."""
    WELCOME = "welcome"
    CONTENT_APPROVED = "content_approved"
    CONTENT_REJECTED = "content_rejected"
    REVENUE_UPDATE = "revenue_update"
    COLLABORATION_REQUEST = "collaboration_request"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    PERFORMANCE_REPORT = "performance_report"
    SECURITY_ALERT = "security_alert"
    SYSTEM_MAINTENANCE = "system_maintenance"
    MILESTONE_REACHED = "milestone_reached"
    DEADLINE_REMINDER = "deadline_reminder"
    PAYMENT_PROCESSED = "payment_processed"


@dataclass
class NotificationTemplate:
    """Notification template configuration."""
    id: str
    name: str
    type: NotificationType
    subject_template: str
    body_template: str
    channels: List[NotificationChannel]
    priority: NotificationPriority
    variables: Dict[str, str]
    localization: Dict[str, Dict[str, str]]  # language -> {subject, body}


class NotificationRequest(BaseModel):
    """Notification delivery request."""
    creator_id: str = Field(..., description="Target creator ID")
    notification_type: NotificationType = Field(..., description="Type of notification")
    channels: List[NotificationChannel] = Field(..., description="Delivery channels")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL)
    subject: str = Field(..., description="Notification subject")
    content: str = Field(..., description="Notification content")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Template variables")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled delivery time")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class NotificationResponse(BaseModel):
    """Notification delivery response."""
    notification_id: str
    status: NotificationStatus
    channels_attempted: List[NotificationChannel]
    channels_successful: List[NotificationChannel]
    channels_failed: List[NotificationChannel]
    delivery_time: Optional[datetime]
    error_message: Optional[str]
    retry_count: int = 0


class CreatorPreferences(BaseModel):
    """Creator notification preferences."""
    creator_id: str
    enabled_channels: List[NotificationChannel] = Field(default_factory=list)
    disabled_types: List[NotificationType] = Field(default_factory=list)
    quiet_hours: Dict[str, str] = Field(default_factory=dict)  # start_time, end_time
    frequency_limits: Dict[str, int] = Field(default_factory=dict)  # type -> max_per_day
    language: str = Field(default="en")
    timezone: str = Field(default="UTC")


class CreatorNotificationService:
    """
    Enterprise Creator Notification Service
    
    Provides intelligent, multi-channel notification delivery with personalization,
    scheduling, and comprehensive analytics for creator engagement.
    """
    
    def __init__(self) -> None:
        self.templates: Dict[str, NotificationTemplate] = {}
        self.preferences: Dict[str, CreatorPreferences] = {}
        self.delivery_queue: List[NotificationRequest] = []
        self.notification_history: List[NotificationResponse] = []
        self.rate_limits: Dict[str, Dict[str, int]] = {}  # creator_id -> channel -> count
        self.active_webhooks: Dict[str, str] = {}  # creator_id -> webhook_url
        
        # Initialize default templates
        self._initialize_templates()
        
        logger.info("CreatorNotificationService initialized successfully")
    
    def _initialize_templates(self) -> None:
        """Initialize default notification templates."""
        templates = [
            NotificationTemplate(
                id="welcome_template",
                name="Welcome New Creator",
                type=NotificationType.WELCOME,
                subject_template="Welcome to Ainflue, {creator_name}!",
                body_template="Welcome to our creator platform! We're excited to have you join our community.",
                channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                priority=NotificationPriority.HIGH,
                variables={"creator_name": "string"},
                localization={
                    "fr": {
                        "subject": "Bienvenue sur Ainflue, {creator_name}!",
                        "body": "Bienvenue sur notre plateforme créateur! Nous sommes ravis de vous avoir dans notre communauté."
                    },
                    "de": {
                        "subject": "Willkommen bei Ainflue, {creator_name}!",
                        "body": "Willkommen auf unserer Creator-Plattform! Wir freuen uns, Sie in unserer Community zu haben."
                    }
                }
            ),
            NotificationTemplate(
                id="revenue_update_template",
                name="Revenue Update",
                type=NotificationType.REVENUE_UPDATE,
                subject_template="💰 Your earnings update: ${amount}",
                body_template="Great news! You've earned ${amount} in the last {period}. Keep up the excellent work!",
                channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.IN_APP],
                priority=NotificationPriority.HIGH,
                variables={"amount": "decimal", "period": "string"},
                localization={}
            ),
            NotificationTemplate(
                id="collaboration_request_template",
                name="Collaboration Request",
                type=NotificationType.COLLABORATION_REQUEST,
                subject_template="🤝 New collaboration opportunity",
                body_template="You have a new collaboration request from {requester_name}. Check your dashboard to respond!",
                channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.IN_APP],
                priority=NotificationPriority.NORMAL,
                variables={"requester_name": "string"},
                localization={}
            )
        ]
        
        for template in templates:
            self.templates[template.id] = template
    
    async def send_notification(self, request: NotificationRequest) -> NotificationResponse:
        """
        Send notification through specified channels.
        
        Args:
            request: Notification delivery request
            
        Returns:
            NotificationResponse with delivery status
        """
        try:
            notification_id = f"notif_{int(datetime.now().timestamp())}_{request.creator_id}"
            
            # Check creator preferences
            preferences = self.preferences.get(request.creator_id)
            if preferences:
                # Filter channels based on preferences
                enabled_channels = [ch for ch in request.channels if ch in preferences.enabled_channels]
                
                # Check if notification type is disabled
                if request.notification_type in preferences.disabled_types:
                    return NotificationResponse(
                        notification_id=notification_id,
                        status=NotificationStatus.CANCELLED,
                        channels_attempted=[],
                        channels_successful=[],
                        channels_failed=[],
                        error_message="Notification type disabled by creator preferences"
                    )
                
                request.channels = enabled_channels
            
            # Check rate limits
            if not self._check_rate_limits(request.creator_id, request.channels):
                return NotificationResponse(
                    notification_id=notification_id,
                    status=NotificationStatus.FAILED,
                    channels_attempted=request.channels,
                    channels_successful=[],
                    channels_failed=request.channels,
                    error_message="Rate limit exceeded"
                )
            
            # Handle scheduled notifications
            if request.scheduled_at and request.scheduled_at > datetime.now():
                self.delivery_queue.append(request)
                return NotificationResponse(
                    notification_id=notification_id,
                    status=NotificationStatus.PENDING,
                    channels_attempted=request.channels,
                    channels_successful=[],
                    channels_failed=[],
                    delivery_time=request.scheduled_at
                )
            
            # Deliver through each channel
            successful_channels = []
            failed_channels = []
            
            for channel in request.channels:
                try:
                    success = await self._deliver_to_channel(
                        channel, request.creator_id, request.subject, 
                        request.content, request.variables
                    )
                    if success:
                        successful_channels.append(channel)
                        self._update_rate_limit(request.creator_id, channel)
                    else:
                        failed_channels.append(channel)
                except Exception as e:
                    logger.error(f"Failed to deliver notification via {channel}: {e}")
                    failed_channels.append(channel)
            
            # Determine overall status
            if successful_channels:
                status = NotificationStatus.DELIVERED if not failed_channels else NotificationStatus.SENT
            else:
                status = NotificationStatus.FAILED
            
            response = NotificationResponse(
                notification_id=notification_id,
                status=status,
                channels_attempted=request.channels,
                channels_successful=successful_channels,
                channels_failed=failed_channels,
                delivery_time=datetime.now()
            )
            
            # Store in history
            self.notification_history.append(response)
            
            logger.info(f"Notification {notification_id} delivered: {status}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return NotificationResponse(
                notification_id=f"error_{int(datetime.now().timestamp())}",
                status=NotificationStatus.FAILED,
                channels_attempted=request.channels,
                channels_successful=[],
                channels_failed=request.channels,
                error_message=str(e)
            )
    
    async def _deliver_to_channel(
        self, 
        channel: NotificationChannel, 
        creator_id: str, 
        subject: str, 
        content: str, 
        variables: Dict[str, Any]
    ) -> bool:
        """Deliver notification to specific channel."""
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(creator_id, subject, content, variables)
            elif channel == NotificationChannel.SMS:
                return await self._send_sms(creator_id, content, variables)
            elif channel == NotificationChannel.PUSH:
                return await self._send_push(creator_id, subject, content, variables)
            elif channel == NotificationChannel.IN_APP:
                return await self._send_in_app(creator_id, subject, content, variables)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack(creator_id, content, variables)
            elif channel == NotificationChannel.DISCORD:
                return await self._send_discord(creator_id, content, variables)
            elif channel == NotificationChannel.TELEGRAM:
                return await self._send_telegram(creator_id, content, variables)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(creator_id, subject, content, variables)
            else:
                logger.warning(f"Unsupported notification channel: {channel}")
                return False
        except Exception as e:
            logger.error(f"Error delivering to {channel}: {e}")
            return False
    
    async def _send_email(self, creator_id: str, subject: str, content: str, variables: Dict[str, Any]) -> bool:
        """Send email notification."""
        # Placeholder implementation - would integrate with actual email service
        logger.info(f"📧 Email sent to creator {creator_id}: {subject}")
        await asyncio.sleep(0.1)  # Simulate API call
        return True
    
    async def _send_sms(self, creator_id: str, content: str, variables: Dict[str, Any]) -> bool:
        """Send SMS notification."""
        # Placeholder implementation - would integrate with SMS service
        logger.info(f"📱 SMS sent to creator {creator_id}: {content[:50]}...")
        await asyncio.sleep(0.1)  # Simulate API call
        return True
    
    async def _send_push(self, creator_id: str, subject: str, content: str, variables: Dict[str, Any]) -> bool:
        """Send push notification."""
        # Placeholder implementation - would integrate with push service
        logger.info(f"🔔 Push notification sent to creator {creator_id}: {subject}")
        await asyncio.sleep(0.1)  # Simulate API call
        return True
    
    async def _send_in_app(self, creator_id: str, subject: str, content: str, variables: Dict[str, Any]) -> bool:
        """Send in-app notification."""
        # Store in application notification system
        logger.info(f"📲 In-app notification sent to creator {creator_id}: {subject}")
        return True
    
    async def _send_slack(self, creator_id: str, content: str, variables: Dict[str, Any]) -> bool:
        """Send Slack notification."""
        # Placeholder implementation - would integrate with Slack API
        logger.info(f"💬 Slack notification sent to creator {creator_id}")
        await asyncio.sleep(0.1)  # Simulate API call
        return True
    
    async def _send_discord(self, creator_id: str, content: str, variables: Dict[str, Any]) -> bool:
        """Send Discord notification."""
        # Placeholder implementation - would integrate with Discord API
        logger.info(f"🎮 Discord notification sent to creator {creator_id}")
        await asyncio.sleep(0.1)  # Simulate API call
        return True
    
    async def _send_telegram(self, creator_id: str, content: str, variables: Dict[str, Any]) -> bool:
        """Send Telegram notification."""
        # Placeholder implementation - would integrate with Telegram API
        logger.info(f"✈️ Telegram notification sent to creator {creator_id}")
        await asyncio.sleep(0.1)  # Simulate API call
        return True
    
    async def _send_webhook(self, creator_id: str, subject: str, content: str, variables: Dict[str, Any]) -> bool:
        """Send webhook notification."""
        webhook_url = self.active_webhooks.get(creator_id)
        if not webhook_url:
            return False
        
        # Placeholder implementation - would make HTTP POST to webhook
        logger.info(f"🔗 Webhook notification sent to creator {creator_id}")
        await asyncio.sleep(0.1)  # Simulate API call
        return True
    
    def _check_rate_limits(self, creator_id: str, channels: List[NotificationChannel]) -> bool:
        """Check if notification can be sent without exceeding rate limits."""
        if creator_id not in self.rate_limits:
            return True
        
        current_limits = self.rate_limits[creator_id]
        for channel in channels:
            if current_limits.get(channel.value, 0) >= 100:  # Max 100 per day per channel
                return False
        
        return True
    
    def _update_rate_limit(self, creator_id -> None: str, channel -> None: NotificationChannel) -> None:
        """Update rate limit counter for creator and channel."""
        if creator_id not in self.rate_limits:
            self.rate_limits[creator_id] = {}
        
        current_count = self.rate_limits[creator_id].get(channel.value, 0)
        self.rate_limits[creator_id][channel.value] = current_count + 1
    
    async def update_creator_preferences(self, preferences: CreatorPreferences) -> bool:
        """Update creator notification preferences."""
        try:
            self.preferences[preferences.creator_id] = preferences
            logger.info(f"Updated preferences for creator {preferences.creator_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return False
    
    async def get_creator_preferences(self, creator_id: str) -> Optional[CreatorPreferences]:
        """Get creator notification preferences."""
        return self.preferences.get(creator_id)
    
    async def send_bulk_notification(
        self, 
        creator_ids: List[str], 
        notification_type: NotificationType,
        subject: str,
        content: str,
        channels: List[NotificationChannel],
        variables: Optional[Dict[str, Any]] = None
    ) -> List[NotificationResponse]:
        """Send notification to multiple creators."""
        if variables is None:
            variables = {}
        
        results = []
        for creator_id in creator_ids:
            request = NotificationRequest(
                creator_id=creator_id,
                notification_type=notification_type,
                channels=channels,
                subject=subject,
                content=content,
                variables=variables
            )
            
            response = await self.send_notification(request)
            results.append(response)
            
            # Add small delay to prevent overwhelming external services
            await asyncio.sleep(0.1)
        
        logger.info(f"Bulk notification sent to {len(creator_ids)} creators")
        return results
    
    async def process_scheduled_notifications(self) -> None:
        """Process notifications scheduled for delivery."""
        current_time = datetime.now()
        ready_notifications = []
        remaining_notifications = []
        
        for notification in self.delivery_queue:
            if notification.scheduled_at and notification.scheduled_at <= current_time:
                ready_notifications.append(notification)
            else:
                remaining_notifications.append(notification)
        
        self.delivery_queue = remaining_notifications
        
        # Process ready notifications
        for notification in ready_notifications:
            await self.send_notification(notification)
        
        return len(ready_notifications)
    
    async def get_notification_analytics(self, creator_id: str, days: int = 30) -> Dict[str, Any]:
        """Get notification analytics for creator."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        creator_notifications = [
            notif for notif in self.notification_history 
            if notif.notification_id.endswith(creator_id) and 
            notif.delivery_time and notif.delivery_time >= cutoff_date
        ]
        
        total_sent = len(creator_notifications)
        successful = len([n for n in creator_notifications if n.status == NotificationStatus.DELIVERED])
        failed = len([n for n in creator_notifications if n.status == NotificationStatus.FAILED])
        
        channel_stats = {}
        for notif in creator_notifications:
            for channel in notif.channels_successful:
                channel_stats[channel.value] = channel_stats.get(channel.value, 0) + 1
        
        return {
            "total_notifications": total_sent,
            "successful_deliveries": successful,
            "failed_deliveries": failed,
            "success_rate": (successful / total_sent * 100) if total_sent > 0 else 0,
            "channel_performance": channel_stats,
            "period_days": days
        }
    
    def register_webhook(self, creator_id: str, webhook_url: str) -> bool:
        """Register webhook URL for creator."""
        try:
            self.active_webhooks[creator_id] = webhook_url
            logger.info(f"Webhook registered for creator {creator_id}")
            return True
        except Exception as e:
            logger.error(f"Error registering webhook: {e}")
            return False
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics."""
        total_notifications = len(self.notification_history)
        
        if total_notifications == 0:
            return {
                "total_notifications": 0,
                "success_rate": 0,
                "active_creators": 0,
                "templates_count": len(self.templates),
                "queue_size": len(self.delivery_queue)
            }
        
        successful = len([n for n in self.notification_history if n.status == NotificationStatus.DELIVERED])
        
        return {
            "total_notifications": total_notifications,
            "successful_notifications": successful,
            "success_rate": (successful / total_notifications * 100),
            "active_creators": len(self.preferences),
            "templates_count": len(self.templates),
            "queue_size": len(self.delivery_queue),
            "registered_webhooks": len(self.active_webhooks)
        }


# Global service instance
_notification_service_instance = None

def get_creator_notification_service() -> CreatorNotificationService:
    """Get singleton instance of CreatorNotificationService."""
    global _notification_service_instance
    if _notification_service_instance is None:
        _notification_service_instance = CreatorNotificationService()
    return _notification_service_instance


# Example usage and testing
async def example_usage() -> None:
    """Example usage of Creator Notification Service."""
    service = get_creator_notification_service()
    
    # Set creator preferences
    preferences = CreatorPreferences(
        creator_id="creator_123",
        enabled_channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.IN_APP],
        disabled_types=[],
        quiet_hours={"start_time": "22:00", "end_time": "08:00"},
        language="en",
        timezone="UTC"
    )
    await service.update_creator_preferences(preferences)
    
    # Send welcome notification
    welcome_request = NotificationRequest(
        creator_id="creator_123",
        notification_type=NotificationType.WELCOME,
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        subject="Welcome to Ainflue!",
        content="Welcome to our creator platform! We're excited to have you join our community.",
        variables={"creator_name": "John Doe"}
    )
    
    response = await service.send_notification(welcome_request)
    print(f"Welcome notification status: {response.status}")
    
    # Send revenue update
    revenue_request = NotificationRequest(
        creator_id="creator_123",
        notification_type=NotificationType.REVENUE_UPDATE,
        channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH],
        subject="💰 Your earnings update: $156.78",
        content="Great news! You've earned $156.78 in the last week. Keep up the excellent work!",
        variables={"amount": "156.78", "period": "week"}
    )
    
    response = await service.send_notification(revenue_request)
    print(f"Revenue notification status: {response.status}")
    
    # Get analytics
    analytics = await service.get_notification_analytics("creator_123")
    print(f"Notification analytics: {analytics}")
    
    # Get service metrics
    metrics = service.get_service_metrics()
    print(f"Service metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())