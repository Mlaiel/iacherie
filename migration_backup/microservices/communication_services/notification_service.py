"""
🔔 Notification Service
Advanced notification management and delivery system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types"""
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"
    MARKETING = "marketing"
    SYSTEM = "system"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationService:
    """Advanced notification management and delivery service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notifications: List[Dict[str, Any]] = []
        self.subscribers: Dict[str, List[str]] = {}
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.delivery_stats: Dict[str, int] = {
            "sent": 0,
            "delivered": 0,
            "failed": 0,
            "opened": 0
        }
        
        self._initialize_templates()
        self.logger.info("✅ NotificationService initialized")
    
    def _initialize_templates(self):
        """Initialize notification templates"""
        self.templates = {
            "welcome": {
                "title": "Bienvenue sur IA Chéries !",
                "body": "Merci de rejoindre notre plateforme. Commencez à créer du contenu incroyable !",
                "type": NotificationType.SUCCESS,
                "channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            },
            "content_approved": {
                "title": "Contenu approuvé",
                "body": "Votre contenu '{content_title}' a été approuvé et publié.",
                "type": NotificationType.SUCCESS,
                "channels": [NotificationChannel.PUSH, NotificationChannel.IN_APP]
            },
            "payment_received": {
                "title": "Paiement reçu",
                "body": "Vous avez reçu un paiement de {amount} {currency}.",
                "type": NotificationType.SUCCESS,
                "channels": [NotificationChannel.EMAIL, NotificationChannel.PUSH]
            },
            "system_maintenance": {
                "title": "Maintenance système",
                "body": "Maintenance programmée le {date} de {start_time} à {end_time}.",
                "type": NotificationType.WARNING,
                "channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            }
        }
    
    async def send_notification(
        self, 
        user_id: str, 
        template_id: str = None,
        title: str = None,
        message: str = None,
        notification_type: NotificationType = NotificationType.INFO,
        channels: List[NotificationChannel] = None,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send notification to user"""
        try:
            notification_id = str(uuid.uuid4())
            
            # Use template if provided
            if template_id and template_id in self.templates:
                template = self.templates[template_id]
                title = template["title"]
                message = template["body"]
                notification_type = template["type"]
                channels = channels or template["channels"]
                
                # Replace placeholders with data
                if data:
                    for key, value in data.items():
                        title = title.replace(f"{{{key}}}", str(value))
                        message = message.replace(f"{{{key}}}", str(value))
            
            # Default values
            channels = channels or [NotificationChannel.IN_APP]
            
            notification = {
                "notification_id": notification_id,
                "user_id": user_id,
                "title": title or "Notification",
                "message": message or "Vous avez une nouvelle notification",
                "type": notification_type.value,
                "channels": [ch.value for ch in channels],
                "data": data or {},
                "created_at": datetime.utcnow().isoformat(),
                "status": "sent",
                "delivery_attempts": 0
            }
            
            self.notifications.append(notification)
            
            # Simulate delivery to different channels
            delivery_results = {}
            for channel in channels:
                result = await self._deliver_to_channel(notification, channel)
                delivery_results[channel.value] = result
            
            # Update stats
            self.delivery_stats["sent"] += 1
            if all(result["success"] for result in delivery_results.values()):
                self.delivery_stats["delivered"] += 1
            else:
                self.delivery_stats["failed"] += 1
            
            return {
                "success": True,
                "notification_id": notification_id,
                "delivery_results": delivery_results,
                "message": "Notification envoyée avec succès"
            }
            
        except Exception as e:
            self.logger.error(f"Notification sending failed: {str(e)}")
            self.delivery_stats["failed"] += 1
            return {
                "success": False,
                "error": "Notification sending failed",
                "message": str(e)
            }
    
    async def _deliver_to_channel(self, notification: Dict[str, Any], channel: NotificationChannel) -> Dict[str, Any]:
        """Deliver notification to specific channel"""
        try:
            # Simulate delivery delay
            await asyncio.sleep(0.1)
            
            delivery_info = {
                "channel": channel.value,
                "success": True,
                "delivered_at": datetime.utcnow().isoformat(),
                "delivery_id": str(uuid.uuid4())
            }
            
            if channel == NotificationChannel.EMAIL:
                delivery_info["email_subject"] = notification["title"]
                delivery_info["recipient"] = f"user_{notification['user_id']}@example.com"
            elif channel == NotificationChannel.SMS:
                delivery_info["phone_number"] = f"+33XXXXXXXXX"
                delivery_info["sms_id"] = str(uuid.uuid4())
            elif channel == NotificationChannel.PUSH:
                delivery_info["device_token"] = f"device_{notification['user_id']}"
                delivery_info["push_id"] = str(uuid.uuid4())
            
            return delivery_info
            
        except Exception as e:
            return {
                "channel": channel.value,
                "success": False,
                "error": str(e),
                "attempted_at": datetime.utcnow().isoformat()
            }
    
    async def subscribe_user(self, user_id: str, notification_types: List[str]) -> Dict[str, Any]:
        """Subscribe user to notification types"""
        try:
            if user_id not in self.subscribers:
                self.subscribers[user_id] = []
            
            for notif_type in notification_types:
                if notif_type not in self.subscribers[user_id]:
                    self.subscribers[user_id].append(notif_type)
            
            return {
                "success": True,
                "user_id": user_id,
                "subscriptions": self.subscribers[user_id],
                "message": "Abonnements mis à jour"
            }
            
        except Exception as e:
            self.logger.error(f"User subscription failed: {str(e)}")
            return {
                "success": False,
                "error": "Subscription failed",
                "message": str(e)
            }
    
    async def get_user_notifications(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get notifications for user"""
        try:
            user_notifications = [
                notif for notif in self.notifications
                if notif["user_id"] == user_id
            ]
            
            # Sort by creation date (newest first)
            user_notifications.sort(
                key=lambda x: x["created_at"], 
                reverse=True
            )
            
            # Apply limit
            user_notifications = user_notifications[:limit]
            
            return {
                "success": True,
                "user_id": user_id,
                "notifications": user_notifications,
                "total": len(user_notifications),
                "unread": len([n for n in user_notifications if n.get("status") != "read"])
            }
            
        except Exception as e:
            self.logger.error(f"Getting user notifications failed: {str(e)}")
            return {
                "success": False,
                "error": "Failed to get notifications",
                "message": str(e)
            }
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> Dict[str, Any]:
        """Mark notification as read"""
        try:
            for notification in self.notifications:
                if (notification["notification_id"] == notification_id and 
                    notification["user_id"] == user_id):
                    notification["status"] = "read"
                    notification["read_at"] = datetime.utcnow().isoformat()
                    self.delivery_stats["opened"] += 1
                    return {
                        "success": True,
                        "message": "Notification marquée comme lue"
                    }
            
            return {
                "success": False,
                "error": "Notification not found"
            }
            
        except Exception as e:
            self.logger.error(f"Mark as read failed: {str(e)}")
            return {
                "success": False,
                "error": "Mark as read failed",
                "message": str(e)
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "NotificationService",
            "status": "healthy",
            "total_notifications": len(self.notifications),
            "subscribers": len(self.subscribers),
            "templates": len(self.templates),
            "delivery_stats": self.delivery_stats,
            "timestamp": datetime.utcnow().isoformat()
        }


__all__ = ['NotificationService', 'NotificationType', 'NotificationChannel']