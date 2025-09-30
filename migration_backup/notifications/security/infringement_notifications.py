"""
🚨 INFRINGEMENT NOTIFICATIONS
Ainflue Platform - Copyright Infringement Notification System

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module handles copyright infringement notifications for the Ainflue Platform,
providing automated detection and notification when content infringement is detected.
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime, timezone
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class InfringementNotification:
    """Infringement notification data structure"""
    notification_id: str
    user_id: str
    content_id: str
    infringement_type: str
    severity: str
    detected_at: datetime
    infringing_url: str
    evidence: Dict[str, Any]
    status: str = "pending"

class InfringementNotifications:
    """
    Enterprise copyright infringement notification system
    Detects and notifies users about content infringement
    """
    
    def __init__(self):
        """Initialize infringement notifications"""
        self.notifications: List[InfringementNotification] = []
        logger.info("Infringement notifications system initialized")
    
    async def notify_infringement_detected(self, infringement_data: Dict[str, Any]) -> bool:
        """
        Notify about detected copyright infringement
        
        Args:
            infringement_data: Detected infringement details
            
        Returns:
            bool: Success status
        """
        try:
            notification = InfringementNotification(
                notification_id=f"inf_{int(datetime.now().timestamp())}",
                user_id=infringement_data.get("owner_id"),
                content_id=infringement_data.get("content_id"),
                infringement_type=infringement_data.get("type", "unauthorized_use"),
                severity=infringement_data.get("severity", "medium"),
                detected_at=datetime.now(timezone.utc),
                infringing_url=infringement_data.get("infringing_url", ""),
                evidence=infringement_data.get("evidence", {}),
                status="detected"
            )
            
            # Send notification based on severity
            await self._send_infringement_alert(notification)
            
            # Store notification
            self.notifications.append(notification)
            
            logger.warning(f"Infringement notification sent: {notification.notification_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending infringement notification: {str(e)}")
            return False
    
    async def _send_infringement_alert(self, notification: InfringementNotification):
        """Send infringement alert based on severity"""
        channels = ["in_app", "email"]
        if notification.severity in ["high", "critical"]:
            channels.append("sms")
        
        alert_data = {
            "title": "🚨 Copyright Infringement Detected",
            "message": f"Your content '{notification.content_id}' has been detected on unauthorized platform",
            "user_id": notification.user_id,
            "type": "copyright_infringement",
            "priority": notification.severity,
            "channels": channels,
            "metadata": {
                "infringement_id": notification.notification_id,
                "infringing_url": notification.infringing_url,
                "evidence": notification.evidence
            }
        }
        
        logger.info(f"Infringement alert prepared: {notification.notification_id}")
    
    async def get_user_infringements(self, user_id: str) -> List[InfringementNotification]:
        """Get all infringement notifications for user"""
        return [n for n in self.notifications if n.user_id == user_id]
    
    async def update_infringement_status(self, notification_id: str, status: str) -> bool:
        """Update infringement notification status"""
        for notification in self.notifications:
            if notification.notification_id == notification_id:
                notification.status = status
                logger.info(f"Infringement {notification_id} status updated to {status}")
                return True
        return False

__all__ = ["InfringementNotifications", "InfringementNotification"]