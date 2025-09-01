"""Monitoring and Notification Services
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowMetrics:
    """Workflow metrics collection"""
    
    def __init__(self):
        self.metrics = {}
    
    async def setup_content_tracking(self, config: Dict[str, Any]):
        """Setup content tracking configuration"""
        workflow_id = config.get("workflow_id")
        content_id = config.get("content_id")
        
        tracking_config = {
            "workflow_id": workflow_id,
            "content_id": content_id,
            "tracking_events": config.get("tracking_events", []),
            "setup_time": datetime.utcnow().isoformat()
        }
        
        self.metrics[workflow_id] = tracking_config
        logger.info(f"Tracking setup for workflow {workflow_id}")


class NotificationService:
    """Notification service for workflow updates"""
    
    def __init__(self):
        self.notifications = []
    
    async def send_notification(self, notification_data: Dict[str, Any]):
        """Send notification to user"""
        workflow_id = notification_data.get("workflow_id")
        creator_id = notification_data.get("creator_id")
        title = notification_data.get("title")
        message = notification_data.get("message")
        
        notification = {
            "id": f"notif_{len(self.notifications)}",
            "workflow_id": workflow_id,
            "creator_id": creator_id,
            "title": title,
            "message": message,
            "timestamp": notification_data.get("timestamp"),
            "sent": True
        }
        
        self.notifications.append(notification)
        logger.info(f"Notification sent to {creator_id}: {title}")
        
        return notification