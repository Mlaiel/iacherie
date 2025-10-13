"""
Real Notification API Endpoints for IA2Good Platform
Fully implemented with database operations and service integrations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from database import get_db
from models.notification import (
    Notification,
    NotificationPreference,
    NotificationType,
    NotificationChannel,
    NotificationPriority
)
from services.notification_service import notification_service
from api.auth import get_current_user


router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[Dict[str, Any]])
async def list_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's notifications with filters and pagination
    
    Features:
    - Filter by read/unread status
    - Filter by notification type
    - Pagination support
    - Returns full notification objects
    """
    
    user_id = current_user["id"]
    
    query = db.query(Notification).filter(
        Notification.user_id == user_id
    )
    
    if unread_only:
        query = query.filter(Notification.read == False)
    
    if type:
        query = query.filter(Notification.type == type)
    
    total_count = query.count()
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    return {
        "notifications": [
            {
                "id": str(n.id),
                "type": n.type.value,
                "priority": n.priority.value,
                "title": n.title,
                "body": n.body,
                "data": n.data,
                "action_url": n.action_url,
                "channels": n.channels,
                "read": n.read,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "push_sent": n.push_sent,
                "email_sent": n.email_sent,
                "sms_sent": n.sms_sent,
                "created_at": n.created_at.isoformat(),
                "entity_type": n.entity_type,
                "entity_id": str(n.entity_id) if n.entity_id else None
            }
            for n in notifications
        ],
        "total_count": total_count,
        "unread_count": db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).count()
    }


@router.get("/{notification_id}", response_model=Dict[str, Any])
async def get_notification(
    notification_id: UUID,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific notification by ID
    
    Returns full notification details including delivery status
    """
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user["id"]
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {
        "id": str(notification.id),
        "type": notification.type.value,
        "priority": notification.priority.value,
        "title": notification.title,
        "body": notification.body,
        "data": notification.data,
        "action_url": notification.action_url,
        "channels": notification.channels,
        "read": notification.read,
        "read_at": notification.read_at.isoformat() if notification.read_at else None,
        "push_sent": notification.push_sent,
        "push_sent_at": notification.push_sent_at.isoformat() if notification.push_sent_at else None,
        "push_delivery_status": notification.push_delivery_status,
        "email_sent": notification.email_sent,
        "email_sent_at": notification.email_sent_at.isoformat() if notification.email_sent_at else None,
        "sms_sent": notification.sms_sent,
        "sms_sent_at": notification.sms_sent_at.isoformat() if notification.sms_sent_at else None,
        "sms_delivery_status": notification.sms_delivery_status,
        "created_at": notification.created_at.isoformat(),
        "entity_type": notification.entity_type,
        "entity_id": str(notification.entity_id) if notification.entity_id else None
    }


@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: UUID,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read
    
    Updates:
    - read status to True
    - read_at timestamp
    """
    
    success = await notification_service.mark_as_read(notification_id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read", "notification_id": str(notification_id)}


@router.put("/read-all")
async def mark_all_as_read(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read for current user
    
    Returns count of notifications updated
    """
    
    user_id = current_user["id"]
    count = await notification_service.mark_all_as_read(user_id, db)
    
    return {
        "message": f"Marked {count} notifications as read",
        "count": count
    }


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a notification
    
    Permanently removes notification from database
    """
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user["id"]
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted", "notification_id": str(notification_id)}


@router.get("/unread-count", response_model=Dict[str, int])
async def get_unread_count(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get count of unread notifications
    
    Used for badge display in UI
    """
    
    user_id = current_user["id"]
    count = await notification_service.get_unread_count(user_id, db)
    
    return {"unread_count": count}


# ============================================================================
# PREFERENCE ENDPOINTS
# ============================================================================

@router.get("/preferences", response_model=Dict[str, Any])
async def get_notification_preferences(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's notification preferences
    
    Returns:
    - Global enable/disable
    - Channel preferences (push, email, SMS)
    - Type-specific preferences
    - Quiet hours configuration
    """
    
    user_id = current_user["id"]
    
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()
    
    # Create default preferences if not exist
    if not prefs:
        prefs = NotificationPreference(
            user_id=user_id,
            enabled=True,
            in_app_enabled=True,
            push_enabled=True,
            email_enabled=True,
            sms_enabled=False
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return {
        "user_id": str(prefs.user_id),
        "enabled": prefs.enabled,
        "in_app_enabled": prefs.in_app_enabled,
        "push_enabled": prefs.push_enabled,
        "email_enabled": prefs.email_enabled,
        "sms_enabled": prefs.sms_enabled,
        "email": prefs.email,
        "phone": prefs.phone,
        "type_preferences": prefs.type_preferences or {},
        "quiet_hours_enabled": prefs.quiet_hours_enabled,
        "quiet_hours_start": prefs.quiet_hours_start,
        "quiet_hours_end": prefs.quiet_hours_end,
        "timezone": prefs.timezone,
        "language": prefs.language,
        "device_tokens": prefs.device_tokens or []
    }


@router.put("/preferences")
async def update_notification_preferences(
    enabled: Optional[bool] = Body(None),
    in_app_enabled: Optional[bool] = Body(None),
    push_enabled: Optional[bool] = Body(None),
    email_enabled: Optional[bool] = Body(None),
    sms_enabled: Optional[bool] = Body(None),
    email: Optional[str] = Body(None),
    phone: Optional[str] = Body(None),
    type_preferences: Optional[Dict[str, Dict[str, bool]]] = Body(None),
    quiet_hours_enabled: Optional[bool] = Body(None),
    quiet_hours_start: Optional[str] = Body(None),
    quiet_hours_end: Optional[str] = Body(None),
    timezone: Optional[str] = Body(None),
    language: Optional[str] = Body(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's notification preferences
    
    All fields are optional - only provided fields will be updated
    
    Examples:
    - Disable all notifications: {"enabled": false}
    - Disable push only: {"push_enabled": false}
    - Set quiet hours: {"quiet_hours_enabled": true, "quiet_hours_start": "22:00", "quiet_hours_end": "08:00"}
    - Configure type preferences: {"type_preferences": {"case_alert": {"push": true, "email": false}}}
    """
    
    user_id = current_user["id"]
    
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()
    
    if not prefs:
        prefs = NotificationPreference(user_id=user_id)
        db.add(prefs)
    
    # Update provided fields
    if enabled is not None:
        prefs.enabled = enabled
    if in_app_enabled is not None:
        prefs.in_app_enabled = in_app_enabled
    if push_enabled is not None:
        prefs.push_enabled = push_enabled
    if email_enabled is not None:
        prefs.email_enabled = email_enabled
    if sms_enabled is not None:
        prefs.sms_enabled = sms_enabled
    if email is not None:
        prefs.email = email
    if phone is not None:
        prefs.phone = phone
    if type_preferences is not None:
        prefs.type_preferences = type_preferences
    if quiet_hours_enabled is not None:
        prefs.quiet_hours_enabled = quiet_hours_enabled
    if quiet_hours_start is not None:
        prefs.quiet_hours_start = quiet_hours_start
    if quiet_hours_end is not None:
        prefs.quiet_hours_end = quiet_hours_end
    if timezone is not None:
        prefs.timezone = timezone
    if language is not None:
        prefs.language = language
    
    db.commit()
    db.refresh(prefs)
    
    return {
        "message": "Notification preferences updated",
        "preferences": {
            "enabled": prefs.enabled,
            "in_app_enabled": prefs.in_app_enabled,
            "push_enabled": prefs.push_enabled,
            "email_enabled": prefs.email_enabled,
            "sms_enabled": prefs.sms_enabled
        }
    }


# ============================================================================
# DEVICE TOKEN ENDPOINTS
# ============================================================================

@router.post("/device-tokens")
async def register_device_token(
    token: str = Body(..., description="FCM device token"),
    platform: str = Body(..., description="Platform: ios, android, or web"),
    device_id: Optional[str] = Body(None, description="Unique device identifier"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register device token for push notifications
    
    Args:
    - token: Firebase Cloud Messaging device token
    - platform: ios, android, or web
    - device_id: Optional unique device identifier
    
    Used when:
    - User logs in on a new device
    - App is reinstalled
    - Token is refreshed
    """
    
    user_id = current_user["id"]
    
    success = await notification_service.register_device_token(
        user_id=user_id,
        token=token,
        platform=platform,
        db=db
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to register device token")
    
    return {
        "message": "Device token registered successfully",
        "platform": platform,
        "token": token[:20] + "..."  # Show only first 20 chars for security
    }


@router.delete("/device-tokens/{token}")
async def unregister_device_token(
    token: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unregister device token
    
    Used when:
    - User logs out
    - User disables push notifications
    - Token is invalid
    """
    
    user_id = current_user["id"]
    
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()
    
    if not prefs:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    # Remove token from device_tokens array
    device_tokens = prefs.device_tokens or []
    device_tokens = [d for d in device_tokens if d.get('token') != token]
    prefs.device_tokens = device_tokens
    
    db.commit()
    
    return {
        "message": "Device token unregistered successfully"
    }


@router.get("/device-tokens")
async def list_device_tokens(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all registered device tokens for current user
    
    Useful for:
    - Managing devices
    - Debugging push notification issues
    """
    
    user_id = current_user["id"]
    
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()
    
    if not prefs:
        return {"device_tokens": []}
    
    device_tokens = prefs.device_tokens or []
    
    # Mask tokens for security
    masked_tokens = [
        {
            "platform": d.get("platform"),
            "token": d.get("token", "")[:20] + "..." if d.get("token") else "N/A",
            "added_at": d.get("added_at")
        }
        for d in device_tokens
    ]
    
    return {
        "device_tokens": masked_tokens,
        "total_count": len(device_tokens)
    }


# ============================================================================
# TEST ENDPOINT
# ============================================================================

@router.post("/test")
async def send_test_notification(
    channel: NotificationChannel = Body(..., description="Channel to test: push, email, or sms"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a test notification
    
    Used to verify:
    - Push notification setup
    - Email delivery
    - SMS delivery
    
    Useful for troubleshooting notification issues
    """
    
    user_id = current_user["id"]
    
    notification = await notification_service.send_notification(
        user_id=user_id,
        notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
        title=f"Test {channel.value.upper()} Notification",
        body=f"This is a test notification sent via {channel.value}. If you received this, your {channel.value} notifications are working correctly!",
        priority=NotificationPriority.NORMAL,
        channels=[channel],
        db=db
    )
    
    if not notification:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test notification. Check if {channel.value} is enabled in your preferences."
        )
    
    return {
        "message": f"Test notification sent via {channel.value}",
        "notification_id": str(notification.id),
        "delivery_status": {
            "push_sent": notification.push_sent if channel == NotificationChannel.PUSH else None,
            "email_sent": notification.email_sent if channel == NotificationChannel.EMAIL else None,
            "sms_sent": notification.sms_sent if channel == NotificationChannel.SMS else None
        }
    }


# ============================================================================
# STATISTICS ENDPOINT
# ============================================================================

@router.get("/statistics")
async def get_notification_statistics(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notification statistics for current user
    
    Returns:
    - Total notifications received
    - Unread count
    - Breakdown by type
    - Breakdown by channel
    - Recent activity
    """
    
    user_id = current_user["id"]
    
    total_count = db.query(Notification).filter(
        Notification.user_id == user_id
    ).count()
    
    unread_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read == False
    ).count()
    
    # Count by type
    type_counts = {}
    for notif_type in NotificationType:
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.type == notif_type
        ).count()
        if count > 0:
            type_counts[notif_type.value] = count
    
    # Recent notifications (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.created_at >= seven_days_ago
    ).count()
    
    return {
        "total_notifications": total_count,
        "unread_notifications": unread_count,
        "read_notifications": total_count - unread_count,
        "notifications_by_type": type_counts,
        "recent_notifications_7d": recent_count
    }
