"""
Working Notification System for Ainflue Platform
Simplified implementation to ensure functionality
"""

import asyncio
import time
import hashlib
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"

class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

class EmailNotificationService:
    """Email notification service"""
    
    def __init__(self):
        self.logger = logger
        
    async def send_email(self, to: str, subject: str, content: str, 
                        from_email: str = "noreply@ainflue.com") -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Mock email sending
            email_id = f"email_{int(time.time())}_{hashlib.md5(to.encode()).hexdigest()[:8]}"
            
            # Simulate email sending delay
            await asyncio.sleep(0.1)
            
            return {
                "status": "success",
                "email_id": email_id,
                "to": to,
                "subject": subject,
                "sent_at": datetime.utcnow().isoformat(),
                "message": "Email sent successfully"
            }
        except Exception as e:
            self.logger.error(f"Email sending failed: {e}")
            return {"status": "error", "message": str(e)}

class SMSNotificationService:
    """SMS notification service"""
    
    def __init__(self):
        self.logger = logger
        
    async def send_sms(self, to: str, message: str, from_number: str = "+1234567890") -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            # Mock SMS sending
            sms_id = f"sms_{int(time.time())}_{hashlib.md5(to.encode()).hexdigest()[:8]}"
            
            # Simulate SMS sending delay
            await asyncio.sleep(0.1)
            
            return {
                "status": "success",
                "sms_id": sms_id,
                "to": to,
                "message": message,
                "sent_at": datetime.utcnow().isoformat(),
                "message_status": "SMS sent successfully"
            }
        except Exception as e:
            self.logger.error(f"SMS sending failed: {e}")
            return {"status": "error", "message": str(e)}

class PushNotificationService:
    """Push notification service"""
    
    def __init__(self):
        self.logger = logger
        
    async def send_push(self, device_token: str, title: str, body: str, 
                       data: Dict = None) -> Dict[str, Any]:
        """Send push notification"""
        try:
            # Mock push notification sending
            push_id = f"push_{int(time.time())}_{hashlib.md5(device_token.encode()).hexdigest()[:8]}"
            
            # Simulate push sending delay
            await asyncio.sleep(0.1)
            
            return {
                "status": "success",
                "push_id": push_id,
                "device_token": device_token,
                "title": title,
                "body": body,
                "data": data or {},
                "sent_at": datetime.utcnow().isoformat(),
                "message": "Push notification sent successfully"
            }
        except Exception as e:
            self.logger.error(f"Push notification sending failed: {e}")
            return {"status": "error", "message": str(e)}

class InAppNotificationService:
    """In-app notification service"""
    
    def __init__(self):
        self.logger = logger
        self.notifications = {}  # In-memory storage for demo
        
    async def create_notification(self, user_id: str, title: str, content: str,
                                action_url: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Create in-app notification"""
        try:
            notification_id = f"notif_{int(time.time())}_{hashlib.md5(user_id.encode()).hexdigest()[:8]}"
            
            notification = {
                "id": notification_id,
                "user_id": user_id,
                "title": title,
                "content": content,
                "action_url": action_url,
                "metadata": metadata or {},
                "status": NotificationStatus.PENDING.value,
                "created_at": datetime.utcnow().isoformat(),
                "read_at": None
            }
            
            # Store notification
            if user_id not in self.notifications:
                self.notifications[user_id] = []
            self.notifications[user_id].append(notification)
            
            return {
                "status": "success",
                "notification": notification,
                "message": "In-app notification created successfully"
            }
        except Exception as e:
            self.logger.error(f"In-app notification creation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_user_notifications(self, user_id: str, unread_only: bool = False) -> Dict[str, Any]:
        """Get user notifications"""
        try:
            user_notifications = self.notifications.get(user_id, [])
            
            if unread_only:
                user_notifications = [n for n in user_notifications if not n["read_at"]]
            
            # Sort by creation date (newest first)
            user_notifications = sorted(user_notifications, key=lambda x: x["created_at"], reverse=True)
            
            return {
                "status": "success",
                "notifications": user_notifications,
                "count": len(user_notifications)
            }
        except Exception as e:
            self.logger.error(f"Getting user notifications failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def mark_as_read(self, user_id: str, notification_id: str) -> Dict[str, Any]:
        """Mark notification as read"""
        try:
            user_notifications = self.notifications.get(user_id, [])
            
            for notification in user_notifications:
                if notification["id"] == notification_id:
                    notification["read_at"] = datetime.utcnow().isoformat()
                    notification["status"] = NotificationStatus.READ.value
                    
                    return {
                        "status": "success",
                        "notification": notification,
                        "message": "Notification marked as read"
                    }
            
            return {"status": "error", "message": "Notification not found"}
        except Exception as e:
            self.logger.error(f"Marking notification as read failed: {e}")
            return {"status": "error", "message": str(e)}

class NotificationOrchestrator:
    """Main notification orchestrator"""
    
    def __init__(self):
        self.logger = logger
        self.email_service = EmailNotificationService()
        self.sms_service = SMSNotificationService()
        self.push_service = PushNotificationService()
        self.in_app_service = InAppNotificationService()
        self.notification_log = []  # For tracking all notifications
        
    async def send_notification(self, notification_type: NotificationType, 
                              recipient: str, title: str, content: str,
                              priority: NotificationPriority = NotificationPriority.MEDIUM,
                              metadata: Dict = None) -> Dict[str, Any]:
        """Send notification through specified channel"""
        try:
            result = None
            
            if notification_type == NotificationType.EMAIL:
                result = await self.email_service.send_email(recipient, title, content)
            elif notification_type == NotificationType.SMS:
                result = await self.sms_service.send_sms(recipient, content)
            elif notification_type == NotificationType.PUSH:
                # Assuming recipient is device token for push
                result = await self.push_service.send_push(recipient, title, content)
            elif notification_type == NotificationType.IN_APP:
                # Assuming recipient is user_id for in-app
                result = await self.in_app_service.create_notification(recipient, title, content)
            
            # Log notification
            log_entry = {
                "type": notification_type.value,
                "recipient": recipient,
                "title": title,
                "priority": priority.value,
                "status": result.get("status", "unknown") if result else "failed",
                "sent_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            self.notification_log.append(log_entry)
            
            return result or {"status": "error", "message": "Unknown notification type"}
            
        except Exception as e:
            self.logger.error(f"Notification sending failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def send_multi_channel(self, channels: List[Dict[str, Any]], 
                               title: str, content: str,
                               priority: NotificationPriority = NotificationPriority.MEDIUM) -> Dict[str, Any]:
        """Send notification through multiple channels"""
        try:
            results = []
            
            for channel in channels:
                notification_type = NotificationType(channel["type"])
                recipient = channel["recipient"]
                
                result = await self.send_notification(
                    notification_type, recipient, title, content, priority
                )
                results.append({
                    "channel": channel,
                    "result": result
                })
            
            success_count = sum(1 for r in results if r["result"]["status"] == "success")
            
            return {
                "status": "success" if success_count > 0 else "error",
                "results": results,
                "success_count": success_count,
                "total_count": len(results),
                "message": f"Sent to {success_count}/{len(results)} channels"
            }
            
        except Exception as e:
            self.logger.error(f"Multi-channel notification failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_notification_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get notification history"""
        try:
            # Sort by sent date (newest first)
            history = sorted(self.notification_log, key=lambda x: x["sent_at"], reverse=True)
            history = history[:limit]
            
            return {
                "status": "success",
                "notifications": history,
                "count": len(history)
            }
        except Exception as e:
            self.logger.error(f"Getting notification history failed: {e}")
            return {"status": "error", "message": str(e)}

# Service instance
notification_orchestrator = NotificationOrchestrator()

# API functions
async def send_email(to: str, subject: str, content: str) -> Dict[str, Any]:
    """Send email notification"""
    return await notification_orchestrator.send_notification(
        NotificationType.EMAIL, to, subject, content
    )

async def send_sms(to: str, message: str) -> Dict[str, Any]:
    """Send SMS notification"""
    return await notification_orchestrator.send_notification(
        NotificationType.SMS, to, "SMS", message
    )

async def send_push_notification(device_token: str, title: str, body: str) -> Dict[str, Any]:
    """Send push notification"""
    return await notification_orchestrator.send_notification(
        NotificationType.PUSH, device_token, title, body
    )

async def create_in_app_notification(user_id: str, title: str, content: str) -> Dict[str, Any]:
    """Create in-app notification"""
    return await notification_orchestrator.send_notification(
        NotificationType.IN_APP, user_id, title, content
    )

async def get_user_notifications(user_id: str, unread_only: bool = False) -> Dict[str, Any]:
    """Get user notifications"""
    return await notification_orchestrator.in_app_service.get_user_notifications(user_id, unread_only)

async def mark_notification_read(user_id: str, notification_id: str) -> Dict[str, Any]:
    """Mark notification as read"""
    return await notification_orchestrator.in_app_service.mark_as_read(user_id, notification_id)

# Export main functions
__all__ = ['send_email', 'send_sms', 'send_push_notification', 'create_in_app_notification',
           'get_user_notifications', 'mark_notification_read', 'NotificationOrchestrator',
           'NotificationType', 'NotificationPriority', 'NotificationStatus']