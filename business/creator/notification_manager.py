"""Notification Manager - Intelligent Multi-Channel Notification System

Advanced notification management system providing intelligent, personalized notifications
across multiple channels with preference management and delivery optimization.

Project: IA Influencer Agent + Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING:
This code, concept, and intellectual property are exclusively owned by Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from ...core.cache import CacheManager
from ...core.logging import get_logger
from .profile_manager import CreatorProfileManager

logger = get_logger(__name__)


class NotificationType(Enum):
    """
Notification types"""

    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    COLLABORATION = "collaboration"
    SYSTEM = "system"
    SECURITY = "security"
    PROMOTION = "promotion"
    REMINDER = "reminder"


class NotificationChannel(Enum):
    """Notification delivery channels"""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """Notification priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """Notification data"""
    notification_id: str
    creator_id: str
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    channels: List[NotificationChannel] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    delivery_status: Dict[str, str] = field(default_factory=dict)


class NotificationPreferences:
    """
Notification preferences management"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.logger = get_logger(self.__class__.__name__)
    
    async def get_user_preferences(self, creator_id: str) -> Dict[str, Any]:
        """
Get notification preferences for creator"""
        cache_key = f"notification_preferences:{creator_id}"
        preferences = await self.cache.get(cache_key)
        
        if not preferences:
            # Default preferences
            preferences = {
                'creator_id': creator_id,
                'channels': {
                    NotificationChannel.IN_APP.value: True,
                    NotificationChannel.EMAIL.value: True,
                    NotificationChannel.SMS.value: False,
                    NotificationChannel.PUSH.value: True,
                    NotificationChannel.WEBHOOK.value: False
                },
                'types': {
                    NotificationType.ENGAGEMENT.value: {
                        'enabled': True,
                        'channels': ['in_app', 'push'],
                        'frequency': 'immediate'
                    },
                    NotificationType.REVENUE.value: {
                        'enabled': True,
                        'channels': ['in_app', 'email', 'push'],
                        'frequency': 'immediate'
                    },
                    NotificationType.COLLABORATION.value: {
                        'enabled': True,
                        'channels': ['in_app', 'email'],
                        'frequency': 'immediate'
                    },
                    NotificationType.SYSTEM.value: {
                        'enabled': True,
                        'channels': ['in_app'],
                        'frequency': 'immediate'
                    },
                    NotificationType.SECURITY.value: {
                        'enabled': True,
                        'channels': ['in_app', 'email', 'sms'],
                        'frequency': 'immediate'
                    },
                    NotificationType.PROMOTION.value: {
                        'enabled': False,
                        'channels': ['email'],
                        'frequency': 'weekly'
                    },
                    NotificationType.REMINDER.value: {
                        'enabled': True,
                        'channels': ['in_app', 'push'],
                        'frequency': 'immediate'
                    }
                },
                'quiet_hours': {
                    'enabled': True,
                    'start_time': '22:00',
                    'end_time': '08:00',
                    'timezone': 'UTC'
                },
                'digest_preferences': {
                    'daily_digest': True,
                    'weekly_digest': True,
                    'delivery_time': '09:00'
                }
            }
            
            await self.cache.set(cache_key, preferences)
        
        return preferences
    
    async def update_preferences(self, creator_id: str, preferences_update: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification preferences"""
        current_preferences = await self.get_user_preferences(creator_id)
        
        # Merge updates
        for key, value in preferences_update.items():
            if key in current_preferences:
                if isinstance(value, dict) and isinstance(current_preferences[key], dict):
                    current_preferences[key].update(value)
                else:
                    current_preferences[key] = value
        
        # Save updated preferences
        cache_key = f"notification_preferences:{creator_id}"
        await self.cache.set(cache_key, current_preferences)
        
        self.logger.info(f"Updated notification preferences for creator {creator_id}")
        return current_preferences


class NotificationRenderer:
    """Notification content rendering for different channels"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.logger = get_logger(self.__class__.__name__)
    
    async def render_notification(self, notification: Notification, channel: NotificationChannel, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Render notification for specific channel"""
        if channel == NotificationChannel.EMAIL:
            return await self._render_email(notification, creator_data)
        elif channel == NotificationChannel.SMS:
            return await self._render_sms(notification, creator_data)
        elif channel == NotificationChannel.PUSH:
            return await self._render_push(notification, creator_data)
        elif channel == NotificationChannel.IN_APP:
            return await self._render_in_app(notification, creator_data)
        elif channel == NotificationChannel.WEBHOOK:
            return await self._render_webhook(notification, creator_data)
        
        return {'error': 'Unsupported channel'}
    
    async def _render_email(self, notification: Notification, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Render email notification"""
        return {
            'channel': 'email',
            'to': creator_data.get('email'),
            'subject': f"[IA Influencer] {notification.title}",
            'html_content': f"""
                <h2>{notification.title}</h2>
                <p>{notification.message}</p>
                <p>Best regards,<br>IA Influencer Agent Team</p>
            """,
            'text_content': f"{notification.title}\n\n{notification.message}\n\nBest regards,\nIA Influencer Agent Team"
        }
    
    async def _render_sms(self, notification: Notification, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render SMS notification"""
        # Truncate message for SMS
        sms_message = f"{notification.title}: {notification.message}"
        if len(sms_message) > 160:
            sms_message = sms_message[:157] + "..."
        
        return {
            'channel': 'sms',
            'to': creator_data.get('phone'),
            'message': sms_message
        }
    
    async def _render_push(self, notification: Notification, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render push notification"""
        return {
            'channel': 'push',
            'device_tokens': creator_data.get('device_tokens', []),
            'title': notification.title,
            'body': notification.message,
            'data': notification.metadata
        }
    
    async def _render_in_app(self, notification: Notification, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Render in-app notification"""
        return {
            'channel': 'in_app',
            'notification_id': notification.notification_id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type.value,
            'priority': notification.priority.value,
            'created_at': notification.created_at.isoformat(),
            'metadata': notification.metadata
        }
    
    async def _render_webhook(self, notification: Notification, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Render webhook notification"""
        return {
            'channel': 'webhook',
            'url': creator_data.get('webhook_url'),
            'payload': {
                'notification_id': notification.notification_id,
                'creator_id': notification.creator_id,
                'type': notification.notification_type.value,
                'title': notification.title,
                'message': notification.message,
                'priority': notification.priority.value,
                'timestamp': notification.created_at.isoformat(),
                'metadata': notification.metadata
            }
        }


class NotificationDelivery:
    """
Notification delivery engine"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.logger = get_logger(self.__class__.__name__)
    
    async def deliver_notification(self, notification: Notification, channel: NotificationChannel, rendered_content: Dict[str, Any]) -> Dict[str, Any]:
        """
Deliver notification via specific channel"""
        try:
            if channel == NotificationChannel.EMAIL:
                result = await self._deliver_email(rendered_content)
            elif channel == NotificationChannel.SMS:
                result = await self._deliver_sms(rendered_content)
            elif channel == NotificationChannel.PUSH:
                result = await self._deliver_push(rendered_content)
            elif channel == NotificationChannel.IN_APP:
                result = await self._deliver_in_app(rendered_content)
            elif channel == NotificationChannel.WEBHOOK:
                result = await self._deliver_webhook(rendered_content)
            else:
                result = {'status': 'error', 'message': 'Unsupported channel'}
            
            # Update notification delivery status
            if notification.delivery_status is None:
                notification.delivery_status = {}
            notification.delivery_status[channel.value] = result['status']
            
            if result['status'] == 'delivered' and not notification.delivered_at:
                notification.delivered_at = datetime.utcnow()
            
            # Cache updated notification
            await self.cache.set(f"notification:{notification.notification_id}", notification)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Notification delivery failed for {channel.value}: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _deliver_email(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Mock email delivery"""
        self.logger.info(f"Email sent to {content.get('to')}: {content.get('subject')}")
        return {'status': 'delivered', 'delivery_id': f"email_{datetime.utcnow().timestamp()}"}
    
    async def _deliver_sms(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Mock SMS delivery"""
        self.logger.info(f"SMS sent to {content.get('to')}: {content.get('message')}")
        return {'status': 'delivered', 'delivery_id': f"sms_{datetime.utcnow().timestamp()}"}
    
    async def _deliver_push(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Mock push notification delivery"""
        self.logger.info(f"Push notification sent: {content.get('title')}")
        return {'status': 'delivered', 'delivery_id': f"push_{datetime.utcnow().timestamp()}"}
    
    async def _deliver_in_app(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Store in-app notification"""
        notification_id = content['notification_id']
        await self.cache.set(f"in_app_notification:{notification_id}", content)
        return {'status': 'delivered', 'delivery_id': notification_id}
    
    async def _deliver_webhook(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Mock webhook delivery"""
        webhook_url = content.get('url')
        self.logger.info(f"Webhook notification sent to {webhook_url}")
        return {'status': 'delivered', 'delivery_id': f"webhook_{datetime.utcnow().timestamp()}"}


class NotificationManager:
    """
    Main notification management system
    
    Orchestrates intelligent notification creation, personalization, delivery,
    and tracking across multiple channels with preference-based optimization.
    """
    
    def __init__(self, profile_manager: CreatorProfileManager, cache_manager: CacheManager):
        self.profile_manager = profile_manager
        self.cache = cache_manager
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize components
        self.preferences = NotificationPreferences(cache_manager)
        self.renderer = NotificationRenderer(cache_manager)
        self.delivery = NotificationDelivery(cache_manager)
    
    async def send_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send notification to creator
        
        Args:
            notification_data: Notification data including creator_id, title, message, type
            
        Returns:
            Notification sending results
        """
        try:
            creator_id = notification_data['creator_id']
            
            # Get creator profile
            profile = await self.profile_manager.get_creator_profile(creator_id)
            if not profile:
                raise ValueError("Creator not found")
            
            # Create notification object
            notification = Notification(
                notification_id=f"notif_{creator_id}_{datetime.utcnow().timestamp()}",
                creator_id=creator_id,
                title=notification_data['title'],
                message=notification_data['message'],
                notification_type=NotificationType(notification_data.get('type', 'system')),
                priority=NotificationPriority(notification_data.get('priority', 'medium')),
                metadata=notification_data.get('metadata', {})
            )
            
            # Get user preferences
            user_preferences = await self.preferences.get_user_preferences(creator_id)
            
            # Determine delivery channels based on preferences
            notification_type_prefs = user_preferences['types'].get(notification.notification_type.value, {})
            if not notification_type_prefs.get('enabled', True):
                return {'status': 'skipped', 'reason': 'Notification type disabled by user'}
            
            enabled_channels = notification_type_prefs.get('channels', ['in_app'])
            
            # Check quiet hours
            if await self._is_quiet_hours(user_preferences):
                if notification.priority != NotificationPriority.URGENT:
                    # Schedule for later delivery
                    notification.scheduled_at = await self._calculate_next_delivery_time(user_preferences)
                    await self.cache.set(f"scheduled_notification:{notification.notification_id}", notification)
                    return {'status': 'scheduled', 'scheduled_at': notification.scheduled_at.isoformat()}
            
            # Prepare creator data for rendering
            creator_data = {
                'email': profile.contact_info.get('email'),
                'phone': profile.contact_info.get('phone'),
                'device_tokens': [],  # Would come from device registrations
                'webhook_url': profile.integrations.get('webhook_url')
            }
            
            # Deliver to each channel
            delivery_results = {}
            for channel_name in enabled_channels:
                try:
                    channel = NotificationChannel(channel_name)
                    
                    # Render notification for channel
                    rendered_content = await self.renderer.render_notification(
                        notification, channel, creator_data
                    )
                    
                    # Deliver notification
                    delivery_result = await self.delivery.deliver_notification(
                        notification, channel, rendered_content
                    )
                    
                    delivery_results[channel_name] = delivery_result
                    
                except Exception as e:
                    self.logger.error(f"Channel delivery failed for {channel_name}: {e}")
                    delivery_results[channel_name] = {'status': 'failed', 'error': str(e)}
            
            # Cache notification
            await self.cache.set(f"notification:{notification.notification_id}", notification)
            
            self.logger.info(f"Notification {notification.notification_id} processed for creator {creator_id}")
            
            return {
                'notification_id': notification.notification_id,
                'status': 'processed',
                'delivery_results': delivery_results,
                'created_at': notification.created_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Notification sending failed: {e}")
            raise
    
    async def _is_quiet_hours(self, preferences: Dict[str, Any]) -> bool:
        """Check if current time is within quiet hours"""
        quiet_hours = preferences.get('quiet_hours', {})
        if not quiet_hours.get('enabled', False):
            return False
        
        # Simple time check (would need proper timezone handling in production)
        current_hour = datetime.utcnow().hour
        start_hour = int(quiet_hours.get('start_time', '22:00').split(':')[0])
        end_hour = int(quiet_hours.get('end_time', '08:00').split(':')[0])
        
        if start_hour > end_hour:  # Quiet hours span midnight
            return current_hour >= start_hour or current_hour < end_hour
        else:
            return start_hour <= current_hour < end_hour
    
    async def _calculate_next_delivery_time(self, preferences: Dict[str, Any]) -> datetime:
        """
Calculate next appropriate delivery time"""
        quiet_hours = preferences.get('quiet_hours', {})
        end_time = quiet_hours.get('end_time', '08:00')
        end_hour = int(end_time.split(':')[0])
        
        now = datetime.utcnow()
        next_delivery = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        if next_delivery <= now:
            next_delivery += timedelta(days=1)
        
        return next_delivery
    
    async def get_notification_history(self, creator_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
Get notification history for creator"""
        # Mock notification history
        return [
            {
                'notification_id': 'notif_001',
                'title': 'New Collaboration Opportunity',
                'message': 'A creator wants to collaborate with you!',
                'type': 'collaboration',
                'created_at': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'read_at': None,
                'channels_delivered': ['in_app', 'email']
            },
            {
                'notification_id': 'notif_002',
                'title': 'Revenue Milestone Reached',
                'message': 'Congratulations! You\'ve earned €1,000 this month',
                'type': 'revenue',
                'created_at': (datetime.utcnow() - timedelta(days=1)).isoformat(),
                'read_at': (datetime.utcnow() - timedelta(hours=20)).isoformat(),
                'channels_delivered': ['in_app', 'email', 'push']
            }
        ]


# Export classes
__all__ = [
    'NotificationManager',
    'NotificationPreferences',
    'NotificationRenderer',
    'NotificationDelivery'
]
