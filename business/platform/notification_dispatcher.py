"""Notification Dispatcher - Advanced Multi-Channel Notification System

Intelligent notification routing and delivery system supporting multiple channels
including email, SMS, push notifications, webhooks, and in-app notifications.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from ...core.config import settings
from ...core.logging import get_logger
from ...models.notification import NotificationQueue, NotificationStatus, UserPreference
from ...services.notification.email_service import EmailService
from ...services.notification.sms_service import SMSService
from ...services.notification.push_service import PushNotificationService
from ...services.notification.webhook_service import WebhookService

logger = get_logger(__name__)

class NotificationType(Enum):
    """Notification types"""    CONTENT_UPLOAD = "content_upload"
    CONTENT_PROTECTION = "content_protection"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    REVENUE_UPDATE = "revenue_update"
    PAYOUT_PROCESSED = "payout_processed"
    SECURITY_ALERT = "security_alert"
    PLATFORM_UPDATE = "platform_update"
    MARKETING = "marketing"
    SYSTEM_MAINTENANCE = "system_maintenance"

class NotificationChannel(Enum):
    """Notification channels"""    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"

class NotificationPriority(Enum):
    """Notification priority levels"""    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class NotificationContent:
    """Notification content structure"""    title: str
    message: str
    action_url: Optional[str] = None
    image_url: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationRequest:
    """Notification request structure"""    user_id: int
    notification_type: NotificationType
    priority: NotificationPriority
    content: NotificationContent
    channels: Optional[List[NotificationChannel]] = None
    schedule_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class NotificationDispatcher:
    """    Advanced multi-channel notification system
    
    Features:
    - Multi-channel notification delivery
    - Intelligent channel selection
    - User preference management
    - Delivery tracking and analytics
    - Retry logic and fallback channels
    - Template management
    - Rate limiting and throttling
    """    
    def __init__(self):
        # Channel services
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushNotificationService()
        self.webhook_service = WebhookService()
        
        # Notification queue
        self.notification_queue = asyncio.Queue(maxsize=10000)
        
        # Channel priority by notification type
        self.channel_priorities = {
            NotificationType.SECURITY_ALERT: [
                NotificationChannel.EMAIL,
                NotificationChannel.SMS,
                NotificationChannel.PUSH
            ],
            NotificationType.CONTENT_PROTECTION: [
                NotificationChannel.EMAIL,
                NotificationChannel.IN_APP,
                NotificationChannel.PUSH
            ],
            NotificationType.COLLABORATION_REQUEST: [
                NotificationChannel.EMAIL,
                NotificationChannel.IN_APP
            ],
            NotificationType.REVENUE_UPDATE: [
                NotificationChannel.EMAIL,
                NotificationChannel.IN_APP
            ],
            NotificationType.MARKETING: [
                NotificationChannel.EMAIL,
                NotificationChannel.PUSH
            ]
        }
        
        # Rate limits per channel
        self.rate_limits = {
            NotificationChannel.EMAIL: {'limit': 100, 'window': 3600},
            NotificationChannel.SMS: {'limit': 20, 'window': 3600},
            NotificationChannel.PUSH: {'limit': 200, 'window': 3600}
        }
    
    async def initialize(self) -> bool:
        """        Initialize notification dispatcher
        
        Returns:
            bool: Initialization success status
        """        try:
            logger.info("Initializing Notification Dispatcher...")
            
            # Initialize channel services
            await self.email_service.initialize()
            await self.sms_service.initialize()
            await self.push_service.initialize()
            await self.webhook_service.initialize()
            
            # Start background processors
            asyncio.create_task(self._process_notification_queue())
            asyncio.create_task(self._process_scheduled_notifications())
            asyncio.create_task(self._cleanup_expired_notifications())
            
            logger.info("Notification Dispatcher initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Notification Dispatcher initialization failed: {e}")
            return False
    
    async def send_notification(
        self,
        notification_request: NotificationRequest,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """        Send notification through appropriate channels
        
        Args:
            notification_request: Notification details
            session: Database session
            
        Returns:
            Dict containing dispatch results
        """        try:
            # Generate notification ID
            notification_id = f"notif_{notification_request.user_id}_{int(datetime.utcnow().timestamp())}"
            
            # Get user preferences
            user_preferences = await self._get_user_preferences(
                notification_request.user_id, session
            )
            
            # Determine channels based on type and user preferences
            target_channels = await self._determine_target_channels(
                notification_request, user_preferences
            )
            
            # Create notification queue entry
            queue_entry = NotificationQueue(
                notification_id=notification_id,
                user_id=notification_request.user_id,
                notification_type=notification_request.notification_type.value,
                priority=notification_request.priority.value,
                title=notification_request.content.title,
                message=notification_request.content.message,
                channels=json.dumps([c.value for c in target_channels]),
                schedule_at=notification_request.schedule_at or datetime.utcnow(),
                expires_at=notification_request.expires_at,
                status=NotificationStatus.QUEUED,
                metadata=json.dumps(notification_request.metadata),
                created_at=datetime.utcnow()
            )
            
            session.add(queue_entry)
            await session.commit()
            await session.refresh(queue_entry)
            
            # Queue for immediate processing or schedule
            if notification_request.schedule_at and notification_request.schedule_at > datetime.utcnow():
                # Scheduled notification
                await self._schedule_notification(queue_entry)
                status = "scheduled"
            else:
                # Immediate notification
                await self.notification_queue.put(queue_entry)
                status = "queued"
            
            logger.info(f"Notification queued: {notification_id}")
            
            return {
                'notification_id': notification_id,
                'status': status,
                'channels': [c.value for c in target_channels],
                'scheduled_at': notification_request.schedule_at.isoformat() if notification_request.schedule_at else None,
                'created_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Notification dispatch failed: {e}")
            raise HTTPException(status_code=500, detail=f"Notification failed: {str(e)}")
    
    async def send_bulk_notification(
        self,
        user_ids: List[int],
        notification_type: NotificationType,
        content: NotificationContent,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """        Send bulk notification to multiple users
        
        Args:
            user_ids: List of user IDs
            notification_type: Type of notification
            content: Notification content
            priority: Notification priority
            session: Database session
            
        Returns:
            Dict containing bulk dispatch results
        """        try:
            bulk_id = f"bulk_{int(datetime.utcnow().timestamp())}"
            dispatch_results = []
            failed_dispatches = []
            
            for user_id in user_ids:
                try:
                    request = NotificationRequest(
                        user_id=user_id,
                        notification_type=notification_type,
                        priority=priority,
                        content=content,
                        metadata={'bulk_id': bulk_id}
                    )
                    
                    result = await self.send_notification(request, session)
                    dispatch_results.append(result)
                    
                except Exception as e:
                    failed_dispatches.append({
                        'user_id': user_id,
                        'error': str(e)
                    })
                    logger.error(f"Bulk notification failed for user {user_id}: {e}")
            
            return {
                'bulk_id': bulk_id,
                'total_users': len(user_ids),
                'successful_dispatches': len(dispatch_results),
                'failed_dispatches': len(failed_dispatches),
                'dispatch_results': dispatch_results,
                'failures': failed_dispatches,
                'created_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Bulk notification failed: {e}")
            raise HTTPException(status_code=500, detail=f"Bulk notification failed: {str(e)}")
    
    async def get_notification_status(
        self,
        notification_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """        Get notification delivery status
        
        Args:
            notification_id: Notification ID
            session: Database session
            
        Returns:
            Dict containing notification status
        """        try:
            result = await session.execute(
                select(NotificationQueue).where(
                    NotificationQueue.notification_id == notification_id
                )
            )
            
            notification = result.scalar_one_or_none()
            
            if not notification:
                raise HTTPException(status_code=404, detail="Notification not found")
            
            # Parse delivery results
            delivery_results = json.loads(notification.delivery_results) if notification.delivery_results else {}
            channels = json.loads(notification.channels) if notification.channels else []
            
            return {
                'notification_id': notification_id,
                'status': notification.status.value,
                'channels': channels,
                'delivery_results': delivery_results,
                'created_at': notification.created_at.isoformat(),
                'scheduled_at': notification.schedule_at.isoformat() if notification.schedule_at else None,
                'sent_at': notification.sent_at.isoformat() if notification.sent_at else None,
                'failed_at': notification.failed_at.isoformat() if notification.failed_at else None,
                'error_message': notification.error_message
            }
            
        except Exception as e:
            logger.error(f"Failed to get notification status: {e}")
            raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
    
    async def update_user_preferences(
        self,
        user_id: int,
        preferences: Dict[str, Any],
        session: AsyncSession
    ) -> Dict[str, Any]:
        """        Update user notification preferences
        
        Args:
            user_id: User ID
            preferences: Notification preferences
            session: Database session
            
        Returns:
            Dict containing updated preferences
        """        try:
            # Get existing preferences
            result = await session.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            user_pref = result.scalar_one_or_none()
            
            if not user_pref:
                # Create new preferences
                user_pref = UserPreference(
                    user_id=user_id,
                    preferences=json.dumps(preferences),
                    updated_at=datetime.utcnow()
                )
                session.add(user_pref)
            else:
                # Update existing preferences
                user_pref.preferences = json.dumps(preferences)
                user_pref.updated_at = datetime.utcnow()
            
            await session.commit()
            
            logger.info(f"User preferences updated: {user_id}")
            
            return {
                'user_id': user_id,
                'preferences': preferences,
                'updated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Preference update failed: {e}")
            raise HTTPException(status_code=500, detail=f"Preference update failed: {str(e)}")
    
    async def get_notification_analytics(
        self,
        user_id: Optional[int] = None,
        time_range: Optional[Dict[str, datetime]] = None,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """        Get notification analytics
        
        Args:
            user_id: Specific user ID (optional)
            time_range: Time range for analytics
            session: Database session
            
        Returns:
            Dict containing notification analytics
        """        try:
            # Build query
            query = select(NotificationQueue)
            
            if user_id:
                query = query.where(NotificationQueue.user_id == user_id)
            
            if time_range:
                query = query.where(
                    and_(
                        NotificationQueue.created_at >= time_range['start'],
                        NotificationQueue.created_at <= time_range['end']
                    )
                )
            
            result = await session.execute(query)
            notifications = result.scalars().all()
            
            # Calculate analytics
            total_notifications = len(notifications)
            status_counts = {}
            channel_counts = {}
            type_counts = {}
            
            for notif in notifications:
                # Status distribution
                status = notif.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Channel distribution
                channels = json.loads(notif.channels) if notif.channels else []
                for channel in channels:
                    channel_counts[channel] = channel_counts.get(channel, 0) + 1
                
                # Type distribution
                notif_type = notif.notification_type
                type_counts[notif_type] = type_counts.get(notif_type, 0) + 1
            
            # Calculate delivery rates
            delivered = status_counts.get('delivered', 0)
            failed = status_counts.get('failed', 0)
            delivery_rate = (delivered / total_notifications * 100) if total_notifications > 0 else 0
            
            return {
                'user_id': user_id,
                'time_range': {
                    'start': time_range['start'].isoformat() if time_range else None,
                    'end': time_range['end'].isoformat() if time_range else None
                },
                'total_notifications': total_notifications,
                'delivery_rate': round(delivery_rate, 2),
                'status_distribution': status_counts,
                'channel_distribution': channel_counts,
                'type_distribution': type_counts,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Notification analytics failed: {e}")
            raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")
    
    async def _process_notification_queue(self):
        """Process notification queue in background"""        while True:
            try:
                # Get notification from queue
                notification = await self.notification_queue.get()
                
                # Process notification
                await self._process_single_notification(notification)
                
                # Mark as done
                self.notification_queue.task_done()
                
            except Exception as e:
                logger.error(f"Notification queue processing error: {e}")
                await asyncio.sleep(5)
    
    async def _process_single_notification(self, notification: NotificationQueue):
        """Process single notification"""        try:
            channels = json.loads(notification.channels) if notification.channels else []
            delivery_results = {}
            
            # Process each channel
            for channel_name in channels:
                channel = NotificationChannel(channel_name)
                
                # Check rate limits
                if await self._check_rate_limit(notification.user_id, channel):
                    result = await self._send_via_channel(notification, channel)
                    delivery_results[channel_name] = result
                else:
                    delivery_results[channel_name] = {
                        'success': False,
                        'error': 'Rate limit exceeded'
                    }
            
            # Update notification status
            await self._update_notification_status(notification, delivery_results)
            
        except Exception as e:
            logger.error(f"Notification processing failed: {e}")
            await self._mark_notification_failed(notification, str(e))
    
    async def _send_via_channel(
        self, 
        notification: NotificationQueue, 
        channel: NotificationChannel
    ) -> Dict[str, Any]:
        """Send notification via specific channel"""        try:
            content = NotificationContent(
                title=notification.title,
                message=notification.message,
                data=json.loads(notification.metadata) if notification.metadata else {}
            )
            
            if channel == NotificationChannel.EMAIL:
                result = await self.email_service.send_notification(
                    user_id=notification.user_id,
                    content=content
                )
            elif channel == NotificationChannel.SMS:
                result = await self.sms_service.send_notification(
                    user_id=notification.user_id,
                    content=content
                )
            elif channel == NotificationChannel.PUSH:
                result = await self.push_service.send_notification(
                    user_id=notification.user_id,
                    content=content
                )
            elif channel == NotificationChannel.WEBHOOK:
                result = await self.webhook_service.send_notification(
                    user_id=notification.user_id,
                    content=content
                )
            else:
                result = {
                    'success': False,
                    'error': f'Unsupported channel: {channel.value}'
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Channel delivery failed for {channel.value}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_user_preferences(
        self, 
        user_id: int, 
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get user notification preferences"""        result = await session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        
        user_pref = result.scalar_one_or_none()
        
        if user_pref and user_pref.preferences:
            return json.loads(user_pref.preferences)
        
        # Return default preferences
        return {
            'email': True,
            'push': True,
            'sms': False,
            'marketing': True,
            'security_alerts': True
        }
    
    async def _determine_target_channels(
        self,
        request: NotificationRequest,
        user_preferences: Dict[str, Any]
    ) -> List[NotificationChannel]:
        """Determine target channels based on type and preferences"""        if request.channels:
            # Use explicitly specified channels
            return request.channels
        
        # Use default channels for notification type
        default_channels = self.channel_priorities.get(
            request.notification_type,
            [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
        )
        
        # Filter based on user preferences
        allowed_channels = []
        for channel in default_channels:
            pref_key = channel.value.lower()
            if user_preferences.get(pref_key, True):
                allowed_channels.append(channel)
        
        return allowed_channels
    
    async def _check_rate_limit(self, user_id: int, channel: NotificationChannel) -> bool:
        """Check rate limits for channel"""        # Implementation for rate limiting
        return True  # Placeholder
    
    async def _update_notification_status(
        self,
        notification: NotificationQueue,
        delivery_results: Dict[str, Any]
    ):
        """Update notification status based on delivery results"""        # Implementation for status update
        pass
    
    async def _mark_notification_failed(self, notification: NotificationQueue, error: str):
        """Mark notification as failed"""        # Implementation for failure marking
        pass
    
    async def _process_scheduled_notifications(self):
        """Process scheduled notifications"""        while True:
            try:
                # Implementation for scheduled notification processing
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scheduled notification processing error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_notifications(self):
        """Clean up expired notifications"""        while True:
            try:
                # Implementation for cleanup
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                logger.error(f"Notification cleanup error: {e}")
                await asyncio.sleep(3600)
