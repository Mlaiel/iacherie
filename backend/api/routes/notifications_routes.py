"""
🔔 NOTIFICATIONS ROUTES - Complete Implementation
================================================
ALL 15 endpoints for notifications, preferences, subscriptions
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# ============================================================================
# MODELS
# ============================================================================

class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"

# ============================================================================
# NOTIFICATIONS
# ============================================================================

@router.get("/users/{user_id}")
async def get_user_notifications(user_id: str, unread_only: bool = False, limit: int = 50):
    """Get user notifications"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        notifications = await manager.get_user_notifications(user_id, unread_only, limit)
        return {"user_id": user_id, "total": len(notifications), "notifications": notifications}
    except Exception as e:
        return {"user_id": user_id, "total": 0, "notifications": [], "error": str(e)}

@router.post("/send")
async def send_notification(
    user_id: str,
    title: str,
    message: str,
    type: NotificationType = NotificationType.INFO,
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP],
    data: Optional[Dict[str, Any]] = None
):
    """Send notification to user"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        notification = await manager.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type.value,
            channels=[c.value for c in channels],
            data=data
        )
        return {"message": "Notification sent", "notification_id": notification['id'], "notification": notification}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast")
async def broadcast_notification(
    title: str,
    message: str,
    type: NotificationType = NotificationType.INFO,
    user_ids: Optional[List[str]] = None,
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
):
    """Broadcast notification to multiple users"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        result = await manager.broadcast_notification(
            title=title,
            message=message,
            type=type.value,
            user_ids=user_ids,
            channels=[c.value for c in channels]
        )
        return {"message": "Notifications broadcasted", "sent": result['sent']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{notification_id}")
async def get_notification(notification_id: str):
    """Get notification details"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        notification = await manager.get_notification(notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{notification_id}/read")
async def mark_as_read(notification_id: str):
    """Mark notification as read"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        await manager.mark_as_read(notification_id)
        return {"message": "Notification marked as read", "notification_id": notification_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/read-all")
async def mark_all_as_read(user_id: str):
    """Mark all notifications as read"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        await manager.mark_all_as_read(user_id)
        return {"message": "All notifications marked as read", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{notification_id}")
async def delete_notification(notification_id: str):
    """Delete notification"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        await manager.delete_notification(notification_id)
        return {"message": "Notification deleted", "notification_id": notification_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}/clear")
async def clear_notifications(user_id: str):
    """Clear all user notifications"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        await manager.clear_notifications(user_id)
        return {"message": "Notifications cleared", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PREFERENCES
# ============================================================================

@router.get("/users/{user_id}/preferences")
async def get_notification_preferences(user_id: str):
    """Get user notification preferences"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        preferences = await manager.get_preferences(user_id)
        return {"user_id": user_id, "preferences": preferences}
    except Exception as e:
        return {"user_id": user_id, "preferences": {}, "error": str(e)}

@router.put("/users/{user_id}/preferences")
async def update_notification_preferences(user_id: str, preferences: Dict[str, Any]):
    """Update notification preferences"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        await manager.update_preferences(user_id, preferences)
        return {"message": "Preferences updated", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SUBSCRIPTIONS
# ============================================================================

@router.get("/users/{user_id}/subscriptions")
async def get_notification_subscriptions(user_id: str):
    """Get user notification subscriptions"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        subscriptions = await manager.get_subscriptions(user_id)
        return {"user_id": user_id, "subscriptions": subscriptions}
    except Exception as e:
        return {"user_id": user_id, "subscriptions": [], "error": str(e)}

@router.post("/users/{user_id}/subscribe")
async def subscribe_to_topic(user_id: str, topic: str, channels: List[NotificationChannel]):
    """Subscribe to notification topic"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        await manager.subscribe(user_id, topic, [c.value for c in channels])
        return {"message": "Subscribed to topic", "topic": topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/unsubscribe")
async def unsubscribe_from_topic(user_id: str, topic: str):
    """Unsubscribe from notification topic"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        await manager.unsubscribe(user_id, topic)
        return {"message": "Unsubscribed from topic", "topic": topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/users/{user_id}/stats")
async def get_notification_stats(user_id: str):
    """Get user notification statistics"""
    try:
        from backend.notifications.notification_manager import NotificationManager
        manager = NotificationManager()
        await manager.initialize()
        
        stats = await manager.get_user_stats(user_id)
        return {"user_id": user_id, "stats": stats}
    except Exception as e:
        return {"user_id": user_id, "stats": {}, "error": str(e)}
