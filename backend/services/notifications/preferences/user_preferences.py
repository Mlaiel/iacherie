"""User Preferences Service

Service layer for user notification preferences management.
Integrates with the core notification infrastructure to provide 
a clean service interface for user preference operations.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, time

# Import from core notification system
try:
    from notifications.orchestrator import NotificationPreference
except ImportError:
    try:
        # Try alternative import paths
        from ....notifications.orchestrator import NotificationPreference
    except ImportError:
        try:
            # Fallback to database import
            from backend.database.communication.notification_engine import NotificationPreference
        except ImportError:
            # Mock for testing when dependencies are not available
            class NotificationPreference:
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)

logger = logging.getLogger(__name__)


class UserPreferencesService:
    """
    Service layer for user notification preferences management.
    
    Provides a clean interface for managing user notification preferences
    with business logic integration and service-level orchestration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize user preferences service.
        
        Args:
            config: Optional configuration for preferences service
        """
        self.config = config or {}
        self._preferences_store = {}  # In-memory store for demo
        logger.info("UserPreferencesService initialized")
    
    async def get_user_preferences(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get user notification preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with user preferences
        """
        try:
            # Get preferences from store
            preferences = self._preferences_store.get(user_id, {})
            
            # Default preferences if none exist
            if not preferences:
                preferences = self._get_default_preferences()
                self._preferences_store[user_id] = preferences
            
            return {
                "success": True,
                "user_id": user_id,
                "preferences": preferences,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user preferences for {user_id}: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user notification preferences.
        
        Args:
            user_id: User identifier
            preferences: Preferences to update
            
        Returns:
            Dict with update result
        """
        try:
            # Get current preferences
            current_preferences = self._preferences_store.get(user_id, self._get_default_preferences())
            
            # Update with new preferences
            current_preferences.update(preferences)
            self._preferences_store[user_id] = current_preferences
            
            logger.info(f"Updated preferences for user {user_id}")
            return {
                "success": True,
                "user_id": user_id,
                "updated_preferences": preferences,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update user preferences for {user_id}: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def set_channel_preference(
        self,
        user_id: str,
        channel: str,
        enabled: bool,
        notification_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Set channel-specific preferences.
        
        Args:
            user_id: User identifier
            channel: Notification channel (email, sms, push, in_app)
            enabled: Whether channel is enabled
            notification_types: Optional specific notification types for this channel
            
        Returns:
            Dict with operation result
        """
        try:
            current_preferences = self._preferences_store.get(user_id, self._get_default_preferences())
            
            if "channels" not in current_preferences:
                current_preferences["channels"] = {}
            
            current_preferences["channels"][channel] = {
                "enabled": enabled,
                "notification_types": notification_types or "all"
            }
            
            self._preferences_store[user_id] = current_preferences
            
            logger.info(f"Updated {channel} preference for user {user_id}")
            return {
                "success": True,
                "user_id": user_id,
                "channel": channel,
                "enabled": enabled,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to set channel preference for {user_id}: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "channel": channel,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def set_quiet_hours(
        self,
        user_id: str,
        start_time: str,
        end_time: str,
        timezone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set quiet hours for the user.
        
        Args:
            user_id: User identifier
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
            timezone: Optional timezone
            
        Returns:
            Dict with operation result
        """
        try:
            current_preferences = self._preferences_store.get(user_id, self._get_default_preferences())
            
            current_preferences["quiet_hours"] = {
                "enabled": True,
                "start_time": start_time,
                "end_time": end_time,
                "timezone": timezone or "UTC"
            }
            
            self._preferences_store[user_id] = current_preferences
            
            logger.info(f"Updated quiet hours for user {user_id}")
            return {
                "success": True,
                "user_id": user_id,
                "quiet_hours": current_preferences["quiet_hours"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to set quiet hours for {user_id}: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def set_frequency_preference(
        self,
        user_id: str,
        notification_type: str,
        frequency: str
    ) -> Dict[str, Any]:
        """
        Set frequency preference for a notification type.
        
        Args:
            user_id: User identifier
            notification_type: Type of notification
            frequency: Frequency setting (immediate, hourly, daily, weekly)
            
        Returns:
            Dict with operation result
        """
        try:
            current_preferences = self._preferences_store.get(user_id, self._get_default_preferences())
            
            if "frequencies" not in current_preferences:
                current_preferences["frequencies"] = {}
            
            current_preferences["frequencies"][notification_type] = frequency
            self._preferences_store[user_id] = current_preferences
            
            logger.info(f"Updated frequency preference for user {user_id}")
            return {
                "success": True,
                "user_id": user_id,
                "notification_type": notification_type,
                "frequency": frequency,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to set frequency preference for {user_id}: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "notification_type": notification_type,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def set_priority_threshold(
        self,
        user_id: str,
        channel: str,
        minimum_priority: str
    ) -> Dict[str, Any]:
        """
        Set minimum priority threshold for a channel.
        
        Args:
            user_id: User identifier
            channel: Notification channel
            minimum_priority: Minimum priority (low, normal, high, urgent)
            
        Returns:
            Dict with operation result
        """
        try:
            current_preferences = self._preferences_store.get(user_id, self._get_default_preferences())
            
            if "priority_thresholds" not in current_preferences:
                current_preferences["priority_thresholds"] = {}
            
            current_preferences["priority_thresholds"][channel] = minimum_priority
            self._preferences_store[user_id] = current_preferences
            
            logger.info(f"Updated priority threshold for user {user_id}")
            return {
                "success": True,
                "user_id": user_id,
                "channel": channel,
                "minimum_priority": minimum_priority,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to set priority threshold for {user_id}: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "channel": channel,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_notification_allowed(
        self,
        user_id: str,
        notification_type: str,
        channel: str,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Check if a notification is allowed based on user preferences.
        
        Args:
            user_id: User identifier
            notification_type: Type of notification
            channel: Notification channel
            priority: Notification priority
            
        Returns:
            Dict with allowance result and reasons
        """
        try:
            preferences = self._preferences_store.get(user_id, self._get_default_preferences())
            
            # Check if channel is enabled
            channel_prefs = preferences.get("channels", {}).get(channel, {"enabled": True})
            if not channel_prefs.get("enabled", True):
                return {
                    "allowed": False,
                    "reason": f"Channel {channel} is disabled",
                    "user_id": user_id
                }
            
            # Check priority threshold
            priority_thresholds = preferences.get("priority_thresholds", {})
            min_priority = priority_thresholds.get(channel, "low")
            
            priority_levels = {"low": 1, "normal": 2, "high": 3, "urgent": 4}
            if priority_levels.get(priority, 2) < priority_levels.get(min_priority, 1):
                return {
                    "allowed": False,
                    "reason": f"Priority {priority} below threshold {min_priority}",
                    "user_id": user_id
                }
            
            # Check quiet hours
            quiet_hours = preferences.get("quiet_hours", {})
            if quiet_hours.get("enabled", False):
                current_time = datetime.utcnow().time()
                start_time = time.fromisoformat(quiet_hours.get("start_time", "22:00"))
                end_time = time.fromisoformat(quiet_hours.get("end_time", "08:00"))
                
                # Simple quiet hours check (doesn't handle timezone properly for demo)
                if start_time <= current_time or current_time <= end_time:
                    if priority != "urgent":
                        return {
                            "allowed": False,
                            "reason": "Within quiet hours",
                            "user_id": user_id
                        }
            
            return {
                "allowed": True,
                "user_id": user_id,
                "channel": channel,
                "notification_type": notification_type
            }
            
        except Exception as e:
            logger.error(f"Failed to check notification allowance for {user_id}: {str(e)}")
            return {
                "allowed": False,
                "reason": f"Error checking preferences: {str(e)}",
                "user_id": user_id
            }
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences."""
        return {
            "channels": {
                "email": {"enabled": True, "notification_types": "all"},
                "sms": {"enabled": True, "notification_types": ["urgent", "security"]},
                "push": {"enabled": True, "notification_types": "all"},
                "in_app": {"enabled": True, "notification_types": "all"}
            },
            "frequencies": {
                "content_updates": "immediate",
                "collaboration_requests": "immediate",
                "revenue_reports": "daily",
                "marketing": "weekly"
            },
            "priority_thresholds": {
                "email": "normal",
                "sms": "high",
                "push": "normal",
                "in_app": "low"
            },
            "quiet_hours": {
                "enabled": False,
                "start_time": "22:00",
                "end_time": "08:00",
                "timezone": "UTC"
            },
            "language": "en",
            "timezone": "UTC"
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get user preferences service status."""
        return {
            "service": "UserPreferencesService",
            "status": "active",
            "supported_channels": ["email", "sms", "push", "in_app"],
            "supported_frequencies": ["immediate", "hourly", "daily", "weekly"],
            "supported_priorities": ["low", "normal", "high", "urgent"],
            "active_users": len(self._preferences_store),
            "timestamp": datetime.utcnow().isoformat()
        }