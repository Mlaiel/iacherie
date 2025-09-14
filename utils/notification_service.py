"""
Notification Service Utility - DevOps Expert Implementation
==========================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise notification service implementation.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Notification:
    """Notification data structure"""
    id: str
    type: NotificationType
    title: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]


class NotificationService:
    """Enterprise notification service"""
    
    def __init__(self) -> None:
        self.notifications: List[Notification] = []
        self.subscribers: Dict[str, List[callable]] = {}
    
    def subscribe(self, event_type -> None: str, callback -> None: callable) -> None:
        """Subscribe to notification events"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def send_notification(self, notification -> None: Notification) -> None:
        """Send notification to subscribers"""
        self.notifications.append(notification)
        
        # Notify subscribers
        event_type = notification.type.value
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    await callback(notification)
                except Exception as e:
                    logger.error(f"Notification callback failed: {e}")
    
    def get_notifications(self, limit: int = 100) -> List[Notification]:
        """Get recent notifications"""
        return self.notifications[-limit:]