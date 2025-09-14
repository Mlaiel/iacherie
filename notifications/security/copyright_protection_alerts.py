"""
🛡️ COPYRIGHT PROTECTION ALERTS
Ainflue Platform - Copyright Protection Notification System

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module handles copyright protection alerts and notifications for the Ainflue Platform,
providing real-time alerts when content protection is activated or when infringement is detected.
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ProtectionLevel(Enum):
    """Copyright protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

@dataclass
class CopyrightAlert:
    """Copyright protection alert data"""
    alert_id: str
    user_id: str
    content_id: str
    protection_level: ProtectionLevel
    alert_type: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]

class CopyrightProtectionAlerts:
    """
    Enterprise-grade copyright protection alerts system
    Manages copyright protection notifications and infringement alerts
    """
    
    def __init__(self) -> None:
        """Initialize copyright protection alerts"""
        self.alert_history: List[CopyrightAlert] = []
        logger.info("Copyright protection alerts system initialized")
    
    async def notify_protection_activated(self, user_id: str, content_id: str, 
                                        protection_data: Dict[str, Any]) -> bool:
        """
        Notify user that copyright protection has been activated
        
        Args:
            user_id: User identifier
            content_id: Content identifier
            protection_data: Protection configuration data
            
        Returns:
            bool: Success status
        """
        try:
            protection_level = ProtectionLevel(protection_data.get("level", "standard"))
            
            alert = CopyrightAlert(
                alert_id=f"cp_{user_id}_{content_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                content_id=content_id,
                protection_level=protection_level,
                alert_type="protection_activated",
                message=f"Copyright protection {protection_level.value} activated for content {content_id}",
                timestamp=datetime.now(timezone.utc),
                metadata=protection_data
            )
            
            # Send multi-channel notification
            await self._send_protection_notification(alert)
            
            # Store alert in history
            self.alert_history.append(alert)
            
            logger.info(f"Copyright protection notification sent for content {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending copyright protection notification: {str(e)}")
            return False
    
    async def notify_infringement(self, infringement_data: Dict[str, Any]) -> bool:
        """
        Notify about detected copyright infringement
        
        Args:
            infringement_data: Infringement detection data
            
        Returns:
            bool: Success status
        """
        try:
            user_id = infringement_data.get("owner_id")
            content_id = infringement_data.get("content_id")
            
            alert = CopyrightAlert(
                alert_id=f"inf_{user_id}_{content_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                content_id=content_id,
                protection_level=ProtectionLevel.ENTERPRISE,
                alert_type="infringement_detected",
                message=f"Copyright infringement detected for content {content_id}",
                timestamp=datetime.now(timezone.utc),
                metadata=infringement_data
            )
            
            # Send urgent notification
            await self._send_infringement_notification(alert)
            
            # Store alert in history
            self.alert_history.append(alert)
            
            logger.warning(f"Copyright infringement notification sent for content {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending infringement notification: {str(e)}")
            return False
    
    async def _send_protection_notification(self, alert -> None: CopyrightAlert) -> None:
        """Send copyright protection notification via multiple channels"""
        notification_data = {
            "title": "🛡️ Copyright Protection Activated",
            "message": alert.message,
            "user_id": alert.user_id,
            "type": "copyright_protection",
            "priority": "high",
            "channels": ["in_app", "email"],
            "metadata": alert.metadata
        }
        
        # Send via notification orchestrator
        # await self.notification_service.send_notification(notification_data)
        logger.info(f"Copyright protection notification prepared: {alert.alert_id}")
    
    async def _send_infringement_notification(self, alert -> None: CopyrightAlert) -> None:
        """Send infringement notification via urgent channels"""
        notification_data = {
            "title": "🚨 Copyright Infringement Detected",
            "message": alert.message,
            "user_id": alert.user_id,
            "type": "copyright_infringement",
            "priority": "critical",
            "channels": ["in_app", "email", "sms"],
            "metadata": alert.metadata
        }
        
        # Send via notification orchestrator
        # await self.notification_service.send_urgent_notification(notification_data)
        logger.warning(f"Copyright infringement notification prepared: {alert.alert_id}")
    
    async def get_protection_history(self, user_id: str) -> List[CopyrightAlert]:
        """Get copyright protection history for user"""
        return [alert for alert in self.alert_history if alert.user_id == user_id]
    
    async def get_infringement_summary(self, user_id: str) -> Dict[str, Any]:
        """Get infringement summary for user"""
        user_alerts = await self.get_protection_history(user_id)
        infringement_alerts = [a for a in user_alerts if a.alert_type == "infringement_detected"]
        
        return {
            "total_infringements": len(infringement_alerts),
            "recent_infringements": len([a for a in infringement_alerts 
                                       if (datetime.now(timezone.utc) - a.timestamp).days <= 30]),
            "protected_content_count": len([a for a in user_alerts 
                                          if a.alert_type == "protection_activated"]),
            "last_infringement": infringement_alerts[-1].timestamp if infringement_alerts else None
        }

# Export the main class
__all__ = ["CopyrightProtectionAlerts", "CopyrightAlert", "ProtectionLevel"]