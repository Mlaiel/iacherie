"""
Notification Orchestrator
========================

Enterprise notification orchestration service for coordinating all notification types.
Provides intelligent routing, prioritization, and delivery optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    CHAT = "chat"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class NotificationOrchestrator:
    """
    Enterprise Notification Orchestrator
    
    Coordinates all notification types with intelligent routing,
    delivery optimization, and comprehensive analytics.
    """
    
    def __init__(self):
        self.notification_queue = {}
        self.delivery_rules = {}
        self.user_preferences = {}
        self.analytics = {}
        self.is_active = False
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize notification orchestrator"""
        try:
            logger.info("Initializing Notification Orchestrator...")
            
            # Setup delivery rules
            await self._setup_delivery_rules()
            
            # Start processing queue
            asyncio.create_task(self._process_notification_queue())
            
            self.is_active = True
            
            return {
                "status": "success",
                "service": "notification_orchestrator",
                "channels": [channel.value for channel in NotificationChannel]
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize notification orchestrator: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _setup_delivery_rules(self):
        """Setup default notification delivery rules"""
        self.delivery_rules = {
            "creator_onboarding": {
                "channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                "priority": NotificationPriority.HIGH,
                "delay": 0
            },
            "collaboration_request": {
                "channels": [NotificationChannel.PUSH, NotificationChannel.EMAIL],
                "priority": NotificationPriority.NORMAL,
                "delay": 0
            },
            "payment_received": {
                "channels": [NotificationChannel.PUSH, NotificationChannel.EMAIL],
                "priority": NotificationPriority.HIGH,
                "delay": 0
            },
            "security_alert": {
                "channels": [NotificationChannel.PUSH, NotificationChannel.EMAIL, NotificationChannel.SMS],
                "priority": NotificationPriority.CRITICAL,
                "delay": 0
            },
            "weekly_report": {
                "channels": [NotificationChannel.EMAIL],
                "priority": NotificationPriority.LOW,
                "delay": 0
            }
        }
    
    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        channels: Optional[List[NotificationChannel]] = None,
        priority: Optional[NotificationPriority] = None
    ) -> Dict[str, Any]:
        """Send notification through orchestrator"""
        try:
            notification_id = f"notif_{datetime.utcnow().timestamp()}"
            
            # Get delivery rules for notification type
            rules = self.delivery_rules.get(notification_type, {})
            
            # Use provided channels or fall back to rules
            delivery_channels = channels or rules.get("channels", [NotificationChannel.IN_APP])
            notification_priority = priority or rules.get("priority", NotificationPriority.NORMAL)
            
            # Apply user preferences
            delivery_channels = await self._apply_user_preferences(user_id, delivery_channels)
            
            notification_data = {
                "id": notification_id,
                "user_id": user_id,
                "type": notification_type,
                "title": title,
                "message": message,
                "data": data or {},
                "channels": [ch.value if isinstance(ch, NotificationChannel) else ch for ch in delivery_channels],
                "priority": notification_priority.value if isinstance(notification_priority, NotificationPriority) else notification_priority,
                "created_at": datetime.utcnow().isoformat(),
                "status": "queued",
                "attempts": 0,
                "max_attempts": 3
            }
            
            # Add to queue
            self.notification_queue[notification_id] = notification_data
            
            logger.info(f"Notification queued: {notification_id}")
            
            return {
                "status": "success",
                "notification_id": notification_id,
                "channels": notification_data["channels"],
                "priority": notification_data["priority"]
            }
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _apply_user_preferences(
        self, 
        user_id: str, 
        channels: List[NotificationChannel]
    ) -> List[NotificationChannel]:
        """Apply user notification preferences"""
        user_prefs = self.user_preferences.get(user_id, {})
        
        if not user_prefs:
            return channels  # No preferences, use all channels
        
        # Filter channels based on user preferences
        filtered_channels = []
        for channel in channels:
            channel_value = channel.value if isinstance(channel, NotificationChannel) else channel
            if user_prefs.get(channel_value, True):  # Default to enabled
                filtered_channels.append(channel)
        
        return filtered_channels if filtered_channels else [NotificationChannel.IN_APP]
    
    async def _process_notification_queue(self):
        """Process notification queue continuously"""
        while self.is_active:
            try:
                # Process queued notifications
                for notification_id, notification_data in list(self.notification_queue.items()):
                    if notification_data["status"] == "queued":
                        await self._deliver_notification(notification_id, notification_data)
                
                # Wait before next iteration
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in notification queue processing: {e}")
                await asyncio.sleep(10)
    
    async def _deliver_notification(self, notification_id: str, notification_data: Dict[str, Any]):
        """Deliver notification through specified channels"""
        try:
            notification_data["status"] = "delivering"
            notification_data["attempts"] += 1
            
            delivery_results = []
            
            # Deliver through each channel
            for channel in notification_data["channels"]:
                result = await self._deliver_to_channel(channel, notification_data)
                delivery_results.append(result)
            
            # Update status based on results
            successful_deliveries = [r for r in delivery_results if r["status"] == "success"]
            
            if successful_deliveries:
                notification_data["status"] = "delivered"
                notification_data["delivered_at"] = datetime.utcnow().isoformat()
                notification_data["delivery_results"] = delivery_results
                
                # Remove from queue
                del self.notification_queue[notification_id]
                
                # Log analytics
                await self._log_delivery_analytics(notification_data, True)
                
                logger.info(f"Notification delivered: {notification_id}")
                
            else:
                # All deliveries failed
                if notification_data["attempts"] >= notification_data["max_attempts"]:
                    notification_data["status"] = "failed"
                    del self.notification_queue[notification_id]
                    await self._log_delivery_analytics(notification_data, False)
                    logger.error(f"Notification delivery failed: {notification_id}")
                else:
                    notification_data["status"] = "queued"  # Retry later
            
        except Exception as e:
            logger.error(f"Error delivering notification {notification_id}: {e}")
            notification_data["status"] = "error"
    
    async def _deliver_to_channel(
        self, 
        channel: str, 
        notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deliver notification to specific channel"""
        try:
            # Mock delivery - in real implementation would call actual services
            if channel == NotificationChannel.EMAIL.value:
                # Call email service
                return {"channel": channel, "status": "success", "message_id": "email_123"}
            elif channel == NotificationChannel.PUSH.value:
                # Call push notification service
                return {"channel": channel, "status": "success", "message_id": "push_456"}
            elif channel == NotificationChannel.SMS.value:
                # Call SMS service
                return {"channel": channel, "status": "success", "message_id": "sms_789"}
            elif channel == NotificationChannel.IN_APP.value:
                # Deliver in-app notification
                return {"channel": channel, "status": "success", "message_id": "app_321"}
            else:
                return {"channel": channel, "status": "error", "error": "Unknown channel"}
            
        except Exception as e:
            logger.error(f"Failed to deliver to channel {channel}: {e}")
            return {"channel": channel, "status": "error", "error": str(e)}
    
    async def _log_delivery_analytics(self, notification_data: Dict[str, Any], success: bool):
        """Log notification delivery analytics"""
        notification_type = notification_data["type"]
        
        if notification_type not in self.analytics:
            self.analytics[notification_type] = {
                "total_sent": 0,
                "successful": 0,
                "failed": 0,
                "channels": {channel.value: 0 for channel in NotificationChannel}
            }
        
        self.analytics[notification_type]["total_sent"] += 1
        
        if success:
            self.analytics[notification_type]["successful"] += 1
        else:
            self.analytics[notification_type]["failed"] += 1
        
        # Log channel usage
        for channel in notification_data["channels"]:
            if channel in self.analytics[notification_type]["channels"]:
                self.analytics[notification_type]["channels"][channel] += 1
    
    async def set_user_preferences(
        self, 
        user_id: str, 
        preferences: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Set user notification preferences"""
        try:
            self.user_preferences[user_id] = preferences
            
            logger.info(f"User preferences updated: {user_id}")
            
            return {
                "status": "success",
                "user_id": user_id,
                "preferences": preferences
            }
            
        except Exception as e:
            logger.error(f"Failed to set user preferences: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_delivery_status(self, notification_id: str) -> Dict[str, Any]:
        """Get notification delivery status"""
        try:
            if notification_id in self.notification_queue:
                notification_data = self.notification_queue[notification_id]
                return {
                    "status": "success",
                    "notification_status": notification_data["status"],
                    "attempts": notification_data["attempts"],
                    "channels": notification_data["channels"]
                }
            else:
                return {
                    "status": "error",
                    "error": "Notification not found or already processed"
                }
                
        except Exception as e:
            logger.error(f"Failed to get delivery status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get notification analytics"""
        return {
            "service": "notification_orchestrator",
            "analytics": self.analytics,
            "queue_size": len(self.notification_queue),
            "active_users": len(self.user_preferences),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get orchestrator health status"""
        return {
            "service": "notification_orchestrator",
            "status": "healthy" if self.is_active else "inactive",
            "queue_size": len(self.notification_queue),
            "supported_channels": len(NotificationChannel),
            "last_check": datetime.utcnow().isoformat()
        }