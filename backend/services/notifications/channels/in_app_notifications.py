"""In-App Notifications Service

Service layer for in-app notification delivery.
Integrates with the core notification infrastructure to provide 
a clean service interface for in-app notifications.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import from core notification system
try:
    from notifications.in_app import InAppNotifier, InAppNotification, InAppNotificationType
except ImportError:
    # Fallback for relative imports
    from ....notifications.in_app import InAppNotifier, InAppNotification, InAppNotificationType

logger = logging.getLogger(__name__)


class InAppNotificationService:
    """
    Service layer for in-app notification management.
    
    Provides a clean interface for sending in-app notifications
    with business logic integration and service-level orchestration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize in-app notification service.
        
        Args:
            config: Optional configuration for in-app service
        """
        self.config = config or {}
        self._in_app_notifier = InAppNotifier(
            config=self.config
        )
        logger.info("InAppNotificationService initialized")
    
    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send in-app notification through the service layer.
        
        Args:
            user_id: Target user identifier
            notification_type: Type of notification
            title: Notification title
            message: Notification message content
            data: Optional additional data payload
            priority: Message priority level
            action_url: Optional URL for notification action
            
        Returns:
            Dict with delivery status and metadata
        """
        try:
            # Create in-app notification
            notification = InAppNotification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                data=data or {},
                priority=priority,
                action_url=action_url,
                timestamp=datetime.utcnow(),
                is_read=False
            )
            
            # Send through core notifier
            result = await self._in_app_notifier.send_notification(notification)
            
            logger.info(f"In-app notification sent successfully to user {user_id}")
            return {
                "success": True,
                "user_id": user_id,
                "notification_id": result.get("notification_id"),
                "notification_type": notification_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send in-app notification to user {user_id}: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "error": str(e),
                "notification_type": notification_type,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def send_bulk_notifications(
        self,
        user_ids: List[str],
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send bulk in-app notifications.
        
        Args:
            user_ids: List of target user identifiers
            notification_type: Type of notification
            title: Notification title
            message: Notification message content
            data: Optional additional data payload
            
        Returns:
            Dict with bulk delivery results
        """
        results = []
        for user_id in user_ids:
            result = await self.send_notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                data=data
            )
            results.append(result)
        
        successful = len([r for r in results if r["success"]])
        failed = len(results) - successful
        
        return {
            "total": len(user_ids),
            "successful": successful,
            "failed": failed,
            "notification_type": notification_type,
            "results": results
        }
    
    async def send_content_notification(
        self,
        user_id: str,
        content_id: str,
        content_title: str,
        notification_type: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send content-related in-app notification.
        
        Args:
            user_id: Target user identifier
            content_id: Content identifier
            content_title: Title of the content
            notification_type: Type of content notification
            message: Notification message
            
        Returns:
            Dict with delivery status and metadata
        """
        data = {
            "content_id": content_id,
            "content_title": content_title
        }
        
        return await self.send_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=f"Content Update: {content_title}",
            message=message,
            data=data,
            action_url=f"/content/{content_id}"
        )
    
    async def send_collaboration_notification(
        self,
        user_id: str,
        requester_name: str,
        project_type: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send collaboration-related in-app notification.
        
        Args:
            user_id: Target user identifier
            requester_name: Name of collaboration requester
            project_type: Type of collaboration project
            message: Notification message
            
        Returns:
            Dict with delivery status and metadata
        """
        data = {
            "requester_name": requester_name,
            "project_type": project_type
        }
        
        return await self.send_notification(
            user_id=user_id,
            notification_type="collaboration_request",
            title=f"Collaboration Request from {requester_name}",
            message=message,
            data=data,
            priority="high",
            action_url="/collaborations/requests"
        )
    
    async def send_revenue_notification(
        self,
        user_id: str,
        amount: float,
        period: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send revenue-related in-app notification.
        
        Args:
            user_id: Target user identifier
            amount: Revenue amount
            period: Revenue period
            message: Notification message
            
        Returns:
            Dict with delivery status and metadata
        """
        data = {
            "amount": amount,
            "period": period,
            "currency": "USD"
        }
        
        return await self.send_notification(
            user_id=user_id,
            notification_type="revenue_milestone",
            title=f"Revenue Milestone Reached",
            message=message,
            data=data,
            priority="high",
            action_url="/dashboard/revenue"
        )
    
    async def mark_as_read(
        self,
        user_id: str,
        notification_id: str
    ) -> Dict[str, Any]:
        """
        Mark notification as read.
        
        Args:
            user_id: User identifier
            notification_id: Notification identifier
            
        Returns:
            Dict with operation result
        """
        try:
            result = await self._in_app_notifier.mark_as_read(
                user_id=user_id,
                notification_id=notification_id
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "notification_id": notification_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "notification_id": notification_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """
        Get user notifications.
        
        Args:
            user_id: User identifier
            limit: Maximum number of notifications to return
            offset: Offset for pagination
            unread_only: Return only unread notifications
            
        Returns:
            Dict with notifications list and metadata
        """
        try:
            notifications = await self._in_app_notifier.get_user_notifications(
                user_id=user_id,
                limit=limit,
                offset=offset,
                unread_only=unread_only
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "notifications": notifications,
                "count": len(notifications),
                "has_more": len(notifications) == limit,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get in-app notification service status."""
        return {
            "service": "InAppNotificationService",
            "status": "active",
            "supported_types": [t.value for t in InAppNotificationType],
            "timestamp": datetime.utcnow().isoformat()
        }