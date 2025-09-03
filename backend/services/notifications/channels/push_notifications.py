"""Push Notifications Service

Service layer for push notification delivery.
Integrates with the core notification infrastructure to provide 
a clean service interface for push notifications.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import from core notification system
try:
    from notifications.push import PushNotifier, PushMessage, PushContent
except ImportError:
    # Fallback for relative imports
    from ....notifications.push import PushNotifier, PushMessage, PushContent

logger = logging.getLogger(__name__)


class PushNotificationService:
    """
    Service layer for push notification management.
    
    Provides a clean interface for sending push notifications
    with business logic integration and service-level orchestration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize push notification service.
        
        Args:
            config: Optional configuration for push service
        """
        self.config = config or {}
        self._push_notifier = PushNotifier(
            config=self.config
        )
        logger.info("PushNotificationService initialized")
    
    async def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        platform: str = "fcm",
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Send push notification through the service layer.
        
        Args:
            device_token: Device token for push delivery
            title: Notification title
            body: Notification body text
            data: Optional additional data payload
            platform: Push platform (fcm, apns, etc.)
            priority: Message priority level
            
        Returns:
            Dict with delivery status and metadata
        """
        try:
            # Create push content
            push_content = PushContent(
                title=title,
                body=body,
                data=data or {},
                platform=platform
            )
            
            # Create push message
            push_message = PushMessage(
                device_token=device_token,
                content=push_content,
                priority=priority,
                timestamp=datetime.utcnow()
            )
            
            # Send through core notifier
            result = await self._push_notifier.send_push_notification(push_message)
            
            logger.info(f"Push notification sent successfully to {device_token}")
            return {
                "success": True,
                "device_token": device_token,
                "delivery_id": result.get("delivery_id"),
                "platform": platform,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send push notification to {device_token}: {str(e)}")
            return {
                "success": False,
                "device_token": device_token,
                "error": str(e),
                "platform": platform,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def send_bulk_notifications(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        platform: str = "fcm"
    ) -> Dict[str, Any]:
        """
        Send bulk push notifications.
        
        Args:
            device_tokens: List of device tokens
            title: Notification title
            body: Notification body text
            data: Optional additional data payload
            platform: Push platform
            
        Returns:
            Dict with bulk delivery results
        """
        results = []
        for device_token in device_tokens:
            result = await self.send_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data,
                platform=platform
            )
            results.append(result)
        
        successful = len([r for r in results if r["success"]])
        failed = len(results) - successful
        
        return {
            "total": len(device_tokens),
            "successful": successful,
            "failed": failed,
            "platform": platform,
            "results": results
        }
    
    async def send_topic_notification(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        platform: str = "fcm"
    ) -> Dict[str, Any]:
        """
        Send notification to a topic/channel.
        
        Args:
            topic: Topic identifier
            title: Notification title
            body: Notification body text
            data: Optional additional data payload
            platform: Push platform
            
        Returns:
            Dict with delivery status and metadata
        """
        try:
            # Create push content for topic
            push_content = PushContent(
                title=title,
                body=body,
                data=data or {},
                platform=platform
            )
            
            # Send to topic through core notifier
            result = await self._push_notifier.send_topic_notification(
                topic=topic,
                content=push_content
            )
            
            logger.info(f"Topic push notification sent successfully to {topic}")
            return {
                "success": True,
                "topic": topic,
                "delivery_id": result.get("delivery_id"),
                "platform": platform,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send topic push notification to {topic}: {str(e)}")
            return {
                "success": False,
                "topic": topic,
                "error": str(e),
                "platform": platform,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get push notification service status."""
        return {
            "service": "PushNotificationService",
            "status": "active",
            "platforms": ["fcm", "apns"],
            "timestamp": datetime.utcnow().isoformat()
        }