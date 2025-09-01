"""Notification business service for IA Influencer Agent platform.

This service handles comprehensive notification management including real-time 
alerts, email notifications, push notifications, and in-app messaging.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import logging
import asyncio
import json

from ..core.config import get_settings
from ..core.database import get_db
from ..models.notification import Notification, NotificationCreate, NotificationPreferences
from ..models.user import User
from ..utils.email_sender import EmailSender
from ..utils.push_notification_sender import PushNotificationSender
from ..utils.websocket_manager import WebSocketManager
from ..services.analytics import AnalyticsService

logger = logging.getLogger(__name__)
settings = get_settings()

class NotificationType(str, Enum):
    """
Notification types for the platform."""

    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    COLLABORATION_COMPLETED = "collaboration_completed"
    CONTENT_PROTECTION_ALERT = "content_protection_alert"
    CONTENT_VIOLATION_DETECTED = "content_violation_detected"
    MONETIZATION_UPDATE = "monetization_update"
    REVENUE_PAYMENT = "revenue_payment"
    SYSTEM_ALERT = "system_alert"
    CONTENT_UPLOADED = "content_uploaded"
    CONTENT_PROCESSED = "content_processed"
    AI_RECOMMENDATION = "ai_recommendation"
    MATCH_SUGGESTION = "match_suggestion"
    SECURITY_ALERT = "security_alert"
    SUBSCRIPTION_UPDATE = "subscription_update"
    PLATFORM_UPDATE = "platform_update"

class NotificationPriority(str, Enum):
    """Notification priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(str, Enum):
    """Notification delivery channels."""

    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    WEBSOCKET = "websocket"

class NotificationService:
    """
    Comprehensive notification management service.
    
    Features:
    - Multi-channel notification delivery
    - Real-time WebSocket notifications
    - Email notification campaigns
    - Push notifications for mobile
    - Intelligent notification batching
    - User preference management
    - Analytics and tracking
    - Template management
    """
    
    def __init__(self):
        self.email_sender = EmailSender()
        self.push_sender = PushNotificationSender()
        self.websocket_manager = WebSocketManager()
        self.analytics = AnalyticsService()
    
    async def send_notification(
        self,
        recipient_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        channels: Optional[List[NotificationChannel]] = None,
        scheduled_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Send a notification through specified channels.
        
        Args:
            recipient_id: ID of the user to receive the notification
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional data payload
            priority: Notification priority level
            channels: Delivery channels (if None, use user preferences)
            scheduled_at: When to send the notification (None for immediate)
            expires_at: When the notification expires
            db: Database session
            
        Returns:
            Notification delivery status and details
        """
        try:
            if not db:
                db = next(get_db())
            
            # Get recipient user
            recipient = db.query(User).filter(User.id == recipient_id).first()
            if not recipient:
                raise ValueError(f"Recipient {recipient_id} not found")
            
            # Create notification record
            notification = Notification(
                id=uuid.uuid4(),
                recipient_id=recipient_id,
                notification_type=notification_type.value,
                title=title,
                message=message,
                data=data or {},
                priority=priority.value,
                created_at=datetime.utcnow(),
                scheduled_at=scheduled_at or datetime.utcnow(),
                expires_at=expires_at,
                is_read=False,
                delivery_status={}
            )
            
            # Determine delivery channels
            if channels is None:
                channels = await self._get_user_preferred_channels(
                    recipient_id, notification_type, db
                )
            
            # Save notification to database
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Deliver notification if not scheduled for later
            if not scheduled_at or scheduled_at <= datetime.utcnow():
                delivery_results = await self._deliver_notification(
                    notification, recipient, channels
                )
                
                # Update delivery status
                notification.delivery_status = delivery_results
                notification.sent_at = datetime.utcnow()
                db.commit()
            
            logger.info(f"Notification created: {notification.id} for user {recipient_id}")
            
            return {
                "notification_id": notification.id,
                "status": "sent" if notification.sent_at else "scheduled",
                "channels": [channel.value for channel in channels],
                "delivery_results": notification.delivery_status,
                "created_at": notification.created_at,
                "scheduled_at": notification.scheduled_at
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def send_bulk_notification(
        self,
        recipient_ids: List[uuid.UUID],
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        channels: Optional[List[NotificationChannel]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Send bulk notifications to multiple users efficiently.
        
        Args:
            recipient_ids: List of user IDs to receive the notification
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional data payload
            priority: Notification priority level
            channels: Delivery channels
            db: Database session
            
        Returns:
            Bulk notification results
        """
        try:
            if not db:
                db = next(get_db())
            
            results = {
                "total_recipients": len(recipient_ids),
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            # Process in batches to avoid overwhelming the system
            batch_size = 100
            for i in range(0, len(recipient_ids), batch_size):
                batch = recipient_ids[i:i + batch_size]
                
                # Send notifications in parallel within each batch
                batch_tasks = []
                for recipient_id in batch:
                    task = asyncio.create_task(
                        self.send_notification(
                            recipient_id=recipient_id,
                            notification_type=notification_type,
                            title=title,
                            message=message,
                            data=data,
                            priority=priority,
                            channels=channels,
                            db=db
                        )
                    )
                    batch_tasks.append(task)
                
                # Wait for batch completion
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Process results
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        results["failed"] += 1
                        results["errors"].append({
                            "recipient_id": str(batch[j]),
                            "error": str(result)
                        })
                    else:
                        results["successful"] += 1
            
            logger.info(f"Bulk notification completed: {results['successful']}/{results['total_recipients']} successful")
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending bulk notification: {str(e)}")
            raise
    
    async def mark_notification_read(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
        db: Session = None
    ) -> bool:
        """
        Mark a notification as read by the user.
        
        Args:
            notification_id: ID of the notification to mark as read
            user_id: ID of the user marking it as read
            db: Database session
            
        Returns:
            Success status
        """
        try:
            if not db:
                db = next(get_db())
            
            # Find and update notification
            notification = db.query(Notification).filter(
                and_(
                    Notification.id == notification_id,
                    Notification.recipient_id == user_id
                )
            ).first()
            
            if not notification:
                raise ValueError(f"Notification {notification_id} not found for user {user_id}")
            
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            
            # Track analytics
            await self.analytics.track_notification_interaction(
                notification_id, user_id, "read"
            )
            
            logger.info(f"Notification {notification_id} marked as read by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    async def get_user_notifications(
        self,
        user_id: uuid.UUID,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        notification_types: Optional[List[NotificationType]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get notifications for a user with filtering options.
        
        Args:
            user_id: ID of the user
            unread_only: Whether to return only unread notifications
            limit: Maximum number of notifications to return
            offset: Offset for pagination
            notification_types: Filter by specific notification types
            db: Database session
            
        Returns:
            User notifications with metadata
        """
        try:
            if not db:
                db = next(get_db())
            
            # Build query
            query = db.query(Notification).filter(Notification.recipient_id == user_id)
            
            if unread_only:
                query = query.filter(Notification.is_read == False)
            
            if notification_types:
                type_values = [nt.value for nt in notification_types]
                query = query.filter(Notification.notification_type.in_(type_values))
            
            # Filter out expired notifications
            query = query.filter(
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
            
            # Get total count
            total_count = query.count()
            
            # Get notifications with pagination
            notifications = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
            
            # Format response
            notification_data = []
            for notification in notifications:
                notification_data.append({
                    "id": notification.id,
                    "type": notification.notification_type,
                    "title": notification.title,
                    "message": notification.message,
                    "data": notification.data,
                    "priority": notification.priority,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at,
                    "read_at": notification.read_at,
                    "expires_at": notification.expires_at
                })
            
            # Get unread count
            unread_count = db.query(func.count(Notification.id)).filter(
                and_(
                    Notification.recipient_id == user_id,
                    Notification.is_read == False,
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow()
                    )
                )
            ).scalar()
            
            return {
                "notifications": notification_data,
                "total_count": total_count,
                "unread_count": unread_count,
                "has_more": offset + len(notifications) < total_count
            }
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise
    
    async def update_notification_preferences(
        self,
        user_id: uuid.UUID,
        preferences: Dict[str, Any],
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Update user notification preferences.
        
        Args:
            user_id: ID of the user
            preferences: Notification preferences to update
            db: Database session
            
        Returns:
            Updated preferences
        """
        try:
            if not db:
                db = next(get_db())
            
            # Get or create user preferences
            user_prefs = db.query(NotificationPreferences).filter(
                NotificationPreferences.user_id == user_id
            ).first()
            
            if not user_prefs:
                user_prefs = NotificationPreferences(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    preferences=preferences,
                    created_at=datetime.utcnow()
                )
                db.add(user_prefs)
            else:
                user_prefs.preferences.update(preferences)
                user_prefs.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(user_prefs)
            
            logger.info(f"Notification preferences updated for user {user_id}")
            
            return user_prefs.preferences
            
        except Exception as e:
            logger.error(f"Error updating notification preferences: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def send_collaboration_notification(
        self,
        requester_id: uuid.UUID,
        partner_id: uuid.UUID,
        collaboration_type: str,
        action: str,
        collaboration_data: Dict[str, Any],
        db: Session = None
    ):
        """
        Send collaboration-specific notifications.
        
        Args:
            requester_id: ID of user making the request
            partner_id: ID of user receiving the request
            collaboration_type: Type of collaboration
            action: Action taken ('request', 'accept', 'reject', 'complete')
            collaboration_data: Collaboration details
            db: Database session
        """
        try:
            # Get user information
            if not db:
                db = next(get_db())
                
            requester = db.query(User).filter(User.id == requester_id).first()
            partner = db.query(User).filter(User.id == partner_id).first()
            
            if not requester or not partner:
                raise ValueError("User not found")
            
            # Determine notification type and content based on action
            if action == "request":
                notification_type = NotificationType.COLLABORATION_REQUEST
                title = f"New Collaboration Request"
                message = f"{requester.full_name or requester.username} wants to collaborate with you on a {collaboration_type} project"
                recipient_id = partner_id
                
            elif action == "accept":
                notification_type = NotificationType.COLLABORATION_ACCEPTED
                title = f"Collaboration Request Accepted"
                message = f"{partner.full_name or partner.username} accepted your collaboration request"
                recipient_id = requester_id
                
            elif action == "complete":
                notification_type = NotificationType.COLLABORATION_COMPLETED
                title = f"Collaboration Completed"
                message = f"Your {collaboration_type} collaboration has been completed successfully"
                # Send to both users
                await self.send_notification(
                    recipient_id=requester_id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    data=collaboration_data,
                    priority=NotificationPriority.MEDIUM,
                    db=db
                )
                recipient_id = partner_id
            
            # Send the notification
            await self.send_notification(
                recipient_id=recipient_id,
                notification_type=notification_type,
                title=title,
                message=message,
                data=collaboration_data,
                priority=NotificationPriority.HIGH,
                db=db
            )
            
        except Exception as e:
            logger.error(f"Error sending collaboration notification: {str(e)}")
            raise
    
    async def send_content_protection_alert(
        self,
        user_id: uuid.UUID,
        content_id: uuid.UUID,
        violation_type: str,
        violation_details: Dict[str, Any],
        db: Session = None
    ):
        """
        Send content protection violation alert.
        
        Args:
            user_id: ID of the content owner
            content_id: ID of the protected content
            violation_type: Type of violation detected
            violation_details: Details about the violation
            db: Database session
        """
        try:
            if not db:
                db = next(get_db())
            
            # Get content information
            from ..models.content import Content
            content = db.query(Content).filter(Content.id == content_id).first()
            
            if not content:
                raise ValueError(f"Content {content_id} not found")
            
            title = f"Content Protection Alert: {violation_type.title()}"
            message = f"Unauthorized use of your content '{content.title}' has been detected"
            
            data = {
                "content_id": str(content_id),
                "content_title": content.title,
                "violation_type": violation_type,
                "violation_details": violation_details,
                "detected_at": datetime.utcnow().isoformat()
            }
            
            await self.send_notification(
                recipient_id=user_id,
                notification_type=NotificationType.CONTENT_VIOLATION_DETECTED,
                title=title,
                message=message,
                data=data,
                priority=NotificationPriority.URGENT,
                channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.IN_APP],
                db=db
            )
            
        except Exception as e:
            logger.error(f"Error sending content protection alert: {str(e)}")
            raise
    
    async def send_monetization_update(
        self,
        user_id: uuid.UUID,
        update_type: str,
        amount: float,
        currency: str,
        details: Dict[str, Any],
        db: Session = None
    ):
        """
        Send monetization and revenue updates.
        
        Args:
            user_id: ID of the user
            update_type: Type of monetization update ('revenue', 'payment', 'dispute')
            amount: Amount involved
            currency: Currency code
            details: Additional details
            db: Database session
        """
        try:
            if update_type == "revenue":
                title = f"New Revenue Generated"
                message = f"You've earned {amount:.2f} {currency} from your protected content"
                priority = NotificationPriority.MEDIUM
                
            elif update_type == "payment":
                title = f"Payment Processed"
                message = f"Payment of {amount:.2f} {currency} has been processed to your account"
                priority = NotificationPriority.HIGH
                
            elif update_type == "dispute":
                title = f"Revenue Dispute"
                message = f"A dispute has been raised for {amount:.2f} {currency} revenue"
                priority = NotificationPriority.HIGH
            
            data = {
                "update_type": update_type,
                "amount": amount,
                "currency": currency,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.send_notification(
                recipient_id=user_id,
                notification_type=NotificationType.MONETIZATION_UPDATE,
                title=title,
                message=message,
                data=data,
                priority=priority,
                db=db
            )
            
        except Exception as e:
            logger.error(f"Error sending monetization update: {str(e)}")
            raise
    
    async def send_ai_recommendation(
        self,
        user_id: uuid.UUID,
        recommendation_type: str,
        recommendation_data: Dict[str, Any],
        db: Session = None
    ):
        """
        Send AI-generated recommendations to users.
        
        Args:
            user_id: ID of the user
            recommendation_type: Type of recommendation ('match', 'optimization', 'trend')
            recommendation_data: Recommendation details
            db: Database session
        """
        try:
            if recommendation_type == "match":
                title = "New Collaboration Match Found"
                message = f"We found {recommendation_data.get('match_count', 1)} potential collaboration partners for you"
                
            elif recommendation_type == "optimization":
                title = "Content Optimization Suggestion"
                message = f"AI suggests improvements for better engagement on your content"
                
            elif recommendation_type == "trend":
                title = "Trending Opportunity"
                message = f"Jump on the trending {recommendation_data.get('trend_topic', 'topic')} for better visibility"
            
            data = {
                "recommendation_type": recommendation_type,
                "recommendation_data": recommendation_data,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            await self.send_notification(
                recipient_id=user_id,
                notification_type=NotificationType.AI_RECOMMENDATION,
                title=title,
                message=message,
                data=data,
                priority=NotificationPriority.LOW,
                channels=[NotificationChannel.IN_APP],
                db=db
            )
            
        except Exception as e:
            logger.error(f"Error sending AI recommendation: {str(e)}")
            raise
    
    async def process_scheduled_notifications(self, db: Session = None):
        """
        Process notifications scheduled for delivery.
        
        Args:
            db: Database session
        """
        try:
            if not db:
                db = next(get_db())
            
            # Get notifications scheduled for now or past
            scheduled_notifications = db.query(Notification).filter(
                and_(
                    Notification.sent_at.is_(None),
                    Notification.scheduled_at <= datetime.utcnow(),
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow()
                    )
                )
            ).limit(100).all()
            
            if not scheduled_notifications:
                return
            
            logger.info(f"Processing {len(scheduled_notifications)} scheduled notifications")
            
            for notification in scheduled_notifications:
                try:
                    # Get recipient
                    recipient = db.query(User).filter(
                        User.id == notification.recipient_id
                    ).first()
                    
                    if not recipient:
                        continue
                    
                    # Get user's preferred channels for this notification type
                    channels = await self._get_user_preferred_channels(
                        notification.recipient_id,
                        NotificationType(notification.notification_type),
                        db
                    )
                    
                    # Deliver notification
                    delivery_results = await self._deliver_notification(
                        notification, recipient, channels
                    )
                    
                    # Update notification
                    notification.delivery_status = delivery_results
                    notification.sent_at = datetime.utcnow()
                    db.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing scheduled notification {notification.id}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error processing scheduled notifications: {str(e)}")
            raise
    
    async def cleanup_expired_notifications(self, db: Session = None):
        """
        Clean up expired notifications.
        
        Args:
            db: Database session
        """
        try:
            if not db:
                db = next(get_db())
            
            # Delete expired notifications
            expired_count = db.query(Notification).filter(
                and_(
                    Notification.expires_at.is_not(None),
                    Notification.expires_at < datetime.utcnow()
                )
            ).delete(synchronize_session=False)
            
            db.commit()
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired notifications")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired notifications: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _get_user_preferred_channels(
        self,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        db: Session
    ) -> List[NotificationChannel]:
        """Get user's preferred notification channels for a specific type."""
        try:
            user_prefs = db.query(NotificationPreferences).filter(
                NotificationPreferences.user_id == user_id
            ).first()
            
            if not user_prefs:
                # Default channels based on notification priority
                return self._get_default_channels(notification_type)
            
            # Get preferences for this notification type
            type_prefs = user_prefs.preferences.get(notification_type.value, {})
            
            enabled_channels = []
            for channel in NotificationChannel:
                if type_prefs.get(channel.value, True):  # Default to enabled
                    enabled_channels.append(channel)
            
            # Ensure at least one channel is enabled
            if not enabled_channels:
                enabled_channels = [NotificationChannel.IN_APP]
            
            return enabled_channels
            
        except Exception as e:
            logger.error(f"Error getting user preferred channels: {str(e)}")
            return self._get_default_channels(notification_type)
    
    def _get_default_channels(self, notification_type: NotificationType) -> List[NotificationChannel]:
        """Get default channels based on notification type and priority."""
        urgent_types = {
            NotificationType.CONTENT_VIOLATION_DETECTED,
            NotificationType.SECURITY_ALERT,
            NotificationType.REVENUE_PAYMENT
        }
        
        if notification_type in urgent_types:
            return [
                NotificationChannel.IN_APP,
                NotificationChannel.EMAIL,
                NotificationChannel.PUSH,
                NotificationChannel.WEBSOCKET
            ]
        else:
            return [NotificationChannel.IN_APP, NotificationChannel.WEBSOCKET]
    
    async def _deliver_notification(
        self,
        notification: Notification,
        recipient: User,
        channels: List[NotificationChannel]
    ) -> Dict[str, Any]:
        """
Deliver notification through specified channels."""
        delivery_results = {}
        
        for channel in channels:
            try:
                if channel == NotificationChannel.IN_APP:
                    # In-app notifications are stored in database (already done)
                    delivery_results[channel.value] = {
                        "status": "success",
                        "delivered_at": datetime.utcnow().isoformat()
                    }
                
                elif channel == NotificationChannel.EMAIL:
                    result = await self._send_email_notification(notification, recipient)
                    delivery_results[channel.value] = result
                
                elif channel == NotificationChannel.PUSH:
                    result = await self._send_push_notification(notification, recipient)
                    delivery_results[channel.value] = result
                
                elif channel == NotificationChannel.WEBSOCKET:
                    result = await self._send_websocket_notification(notification, recipient)
                    delivery_results[channel.value] = result
                
            except Exception as e:
                delivery_results[channel.value] = {
                    "status": "failed",
                    "error": str(e),
                    "attempted_at": datetime.utcnow().isoformat()
                }
                logger.error(f"Failed to deliver notification via {channel.value}: {str(e)}")
        
        return delivery_results
    
    async def _send_email_notification(
        self,
        notification: Notification,
        recipient: User
    ) -> Dict[str, Any]:
        """Send notification via email."""
        try:
            email_data = {
                "to": recipient.email,
                "subject": notification.title,
                "template": self._get_email_template(notification.notification_type),
                "data": {
                    "user_name": recipient.full_name or recipient.username,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_data": notification.data,
                    "app_url": settings.FRONTEND_URL
                }
            }
            
            result = await self.email_sender.send_notification_email(email_data)
            
            return {
                "status": "success" if result else "failed",
                "delivered_at": datetime.utcnow().isoformat(),
                "email": recipient.email
            }
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "attempted_at": datetime.utcnow().isoformat()
            }
    
    async def _send_push_notification(
        self,
        notification: Notification,
        recipient: User
    ) -> Dict[str, Any]:
        """Send notification via push notification."""
        try:
            # Get user's push notification tokens
            push_tokens = getattr(recipient, 'push_notification_tokens', [])
            
            if not push_tokens:
                return {
                    "status": "skipped",
                    "reason": "no_push_tokens",
                    "attempted_at": datetime.utcnow().isoformat()
                }
            
            push_data = {
                "tokens": push_tokens,
                "title": notification.title,
                "body": notification.message,
                "data": notification.data
            }
            
            result = await self.push_sender.send_push_notification(push_data)
            
            return {
                "status": "success" if result else "failed",
                "delivered_at": datetime.utcnow().isoformat(),
                "tokens_count": len(push_tokens)
            }
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "attempted_at": datetime.utcnow().isoformat()
            }
    
    async def _send_websocket_notification(
        self,
        notification: Notification,
        recipient: User
    ) -> Dict[str, Any]:
        """Send notification via WebSocket."""
        try:
            websocket_data = {
                "type": "notification",
                "notification": {
                    "id": str(notification.id),
                    "type": notification.notification_type,
                    "title": notification.title,
                    "message": notification.message,
                    "data": notification.data,
                    "priority": notification.priority,
                    "created_at": notification.created_at.isoformat()
                }
            }
            
            result = await self.websocket_manager.send_to_user(
                user_id=str(recipient.id),
                data=websocket_data
            )
            
            return {
                "status": "success" if result else "failed",
                "delivered_at": datetime.utcnow().isoformat(),
                "user_id": str(recipient.id)
            }
            
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "attempted_at": datetime.utcnow().isoformat()
            }
    
    def _get_email_template(self, notification_type: str) -> str:
        """Get email template name for notification type."""
        template_mapping = {
            NotificationType.COLLABORATION_REQUEST.value: "collaboration_request",
            NotificationType.COLLABORATION_ACCEPTED.value: "collaboration_accepted",
            NotificationType.CONTENT_VIOLATION_DETECTED.value: "content_violation_alert",
            NotificationType.MONETIZATION_UPDATE.value: "monetization_update",
            NotificationType.REVENUE_PAYMENT.value: "payment_notification",
            NotificationType.AI_RECOMMENDATION.value: "ai_recommendation"
        }
        
        return template_mapping.get(notification_type, "default_notification")
