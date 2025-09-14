"""Enterprise in-app notification service with real-time delivery and user experience optimization."""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from enum import Enum
import logging
from dataclasses import dataclass, asdict
import hashlib
import uuid

from .config import settings
from .config import encrypt_sensitive_data, decrypt_sensitive_data
from .config import MetricsCollector, metrics


class InAppNotificationType(str, Enum):
    """
In-app notification types for IA Influencer business logic."""
    # Content Management
    CONTENT_UPLOAD_SUCCESS = "content_upload_success"
    CONTENT_UPLOAD_FAILED = "content_upload_failed"
    CONTENT_PROCESSING_COMPLETE = "content_processing_complete"
    CONTENT_PROTECTION_ACTIVE = "content_protection_active"
    
    # Copyright Protection
    INFRINGEMENT_DETECTED = "infringement_detected"
    DMCA_NOTICE_SENT = "dmca_notice_sent"
    TAKEDOWN_SUCCESSFUL = "takedown_successful"
    PROTECTION_ALERT = "protection_alert"
    
    # Collaboration Opportunities
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_MATCH = "collaboration_match"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    COLLABORATION_DECLINED = "collaboration_declined"
    COLLABORATION_COMPLETED = "collaboration_completed"
    
    # Monetization & Revenue
    REVENUE_MILESTONE = "revenue_milestone"
    PAYMENT_RECEIVED = "payment_received"
    PAYOUT_READY = "payout_ready"
    LICENSING_OPPORTUNITY = "licensing_opportunity"
    SPONSORSHIP_OFFER = "sponsorship_offer"
    
    # Analytics & Performance
    VIRAL_CONTENT_ALERT = "viral_content_alert"
    PERFORMANCE_MILESTONE = "performance_milestone"
    SEO_IMPROVEMENT = "seo_improvement"
    TREND_OPPORTUNITY = "trend_opportunity"
    ANALYTICS_REPORT_READY = "analytics_report_ready"
    
    # Platform Integration
    PLATFORM_CONNECTION_SUCCESS = "platform_connection_success"
    PLATFORM_CONNECTION_FAILED = "platform_connection_failed"
    SOCIAL_MEDIA_PUBLISHED = "social_media_published"
    CROSS_PLATFORM_SYNC = "cross_platform_sync"
    
    # Account & Subscription
    SUBSCRIPTION_UPGRADE = "subscription_upgrade"
    FEATURE_UNLOCK = "feature_unlock"
    PROFILE_VERIFICATION = "profile_verification"
    SECURITY_ALERT = "security_alert"
    
    # System & Maintenance
    SYSTEM_UPDATE = "system_update"
    MAINTENANCE_NOTICE = "maintenance_notice"
    FEATURE_ANNOUNCEMENT = "feature_announcement"
    TUTORIAL_SUGGESTION = "tutorial_suggestion"


class NotificationPriority(str, Enum):
    """In-app notification priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationCategory(str, Enum):
    """Notification categories for filtering and organization."""

    CONTENT = "content"
    PROTECTION = "protection"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    ANALYTICS = "analytics"
    PLATFORM = "platform"
    ACCOUNT = "account"
    SYSTEM = "system"


@dataclass
class InAppNotificationAction:
    """Interactive action for in-app notifications."""
    id: str
    label: str
    action_type: str  # navigate, api_call, dismiss, custom
    action_data: Optional[Dict[str, Any]] = None
    style: str = "primary"  # primary, secondary, success, warning, danger
    icon: Optional[str] = None


@dataclass
class InAppNotification:
    """Rich in-app notification with business context and interactivity."""
    id: str
    user_id: str
    type: InAppNotificationType
    category: NotificationCategory
    priority: NotificationPriority
    title: str
    message: str
    icon: Optional[str] = None
    image: Optional[str] = None
    color: Optional[str] = None
    actions: Optional[List[InAppNotificationAction]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Business context
    content_id: Optional[str] = None
    campaign_id: Optional[str] = None
    collaboration_id: Optional[str] = None
    revenue_amount: Optional[float] = None
    platform: Optional[str] = None
    creator_type: Optional[str] = None
    
    # State management
    read: bool = False
    dismissed: bool = False
    clicked: bool = False
    action_taken: Optional[str] = None
    
    # Timing
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    read_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    
    # Targeting
    show_in_dashboard: bool = True
    show_as_popup: bool = False
    show_as_banner: bool = False
    persistent: bool = False
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.id is None:
            self.id = str(uuid.uuid4())


@dataclass
class NotificationPreferences:
    """
User preferences for in-app notifications."""
    user_id: str
    enabled_types: Set[InAppNotificationType]
    priority_threshold: NotificationPriority = NotificationPriority.NORMAL
    show_popups: bool = True
    show_banners: bool = True
    sound_enabled: bool = True
    desktop_notifications: bool = False
    email_digest: bool = True
    digest_frequency: str = "daily"  # never, daily, weekly
    quiet_hours_start: Optional[int] = None  # 0-23 hours
    quiet_hours_end: Optional[int] = None
    categories_muted: Set[NotificationCategory] = None
    
    def __post_init__(self) -> None:
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
            self.categories_muted = set()


class InAppNotifier:
    """Enterprise in-app notification service with real-time delivery and comprehensive user experience."""
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector()
        
        # In-memory storage for demo (would use Redis/database in production)
        self.notifications = {}  # user_id -> List[InAppNotification]
        self.user_preferences = {}  # user_id -> NotificationPreferences
        self.active_connections = {}  # user_id -> Set[WebSocket connections]
        
        # Configuration
        self.max_notifications_per_user = 1000
        self.default_notification_ttl = timedelta(days=30)
        self.batch_size = 50
        self.real_time_enabled = True
        
        # Templates for different notification types
        self.notification_templates = {
            InAppNotificationType.CONTENT_UPLOAD_SUCCESS: {
                "title": "Content Upload Successful",
                "message": "Your {content_type} has been uploaded and is now being processed for protection.",
                "icon": "upload-cloud",
                "color": "#10B981",
                "category": NotificationCategory.CONTENT,
                "priority": NotificationPriority.NORMAL,
                "show_as_popup": True,
                "actions": [
                    InAppNotificationAction(
                        id="view_content",
                        label="View Content",
                        action_type="navigate",
                        action_data={"route": "/content/{content_id}"}
                    )
                ]
            },
            InAppNotificationType.INFRINGEMENT_DETECTED: {
                "title": "Copyright Infringement Detected",
                "message": "We found unauthorized use of your content '{content_title}' on {platform}.",
                "icon": "shield-alert",
                "color": "#F59E0B",
                "category": NotificationCategory.PROTECTION,
                "priority": NotificationPriority.HIGH,
                "show_as_popup": True,
                "persistent": True,
                "actions": [
                    InAppNotificationAction(
                        id="send_dmca",
                        label="Send DMCA Notice",
                        action_type="api_call",
                        action_data={"endpoint": "/api/v1/dmca/send"},
                        style="primary"
                    ),
                    InAppNotificationAction(
                        id="view_details",
                        label="View Details",
                        action_type="navigate",
                        action_data={"route": "/protection/infringements/{infringement_id}"},
                        style="secondary"
                    )
                ]
            },
            InAppNotificationType.COLLABORATION_REQUEST: {
                "title": "New Collaboration Request",
                "message": "{requester_name} wants to collaborate on a {project_type} project.",
                "icon": "users",
                "color": "#8B5CF6",
                "category": NotificationCategory.COLLABORATION,
                "priority": NotificationPriority.HIGH,
                "show_as_popup": True,
                "actions": [
                    InAppNotificationAction(
                        id="accept_collaboration",
                        label="Accept",
                        action_type="api_call",
                        action_data={"endpoint": "/api/v1/collaborations/{collaboration_id}/accept"},
                        style="success"
                    ),
                    InAppNotificationAction(
                        id="decline_collaboration",
                        label="Decline",
                        action_type="api_call",
                        action_data={"endpoint": "/api/v1/collaborations/{collaboration_id}/decline"},
                        style="secondary"
                    ),
                    InAppNotificationAction(
                        id="view_profile",
                        label="View Profile",
                        action_type="navigate",
                        action_data={"route": "/creators/{requester_id}"},
                        style="secondary"
                    )
                ]
            },
            InAppNotificationType.REVENUE_MILESTONE: {
                "title": "Revenue Milestone Reached!",
                "message": "Congratulations! You've earned ${amount} from your content this month.",
                "icon": "trending-up",
                "color": "#059669",
                "category": NotificationCategory.MONETIZATION,
                "priority": NotificationPriority.HIGH,
                "show_as_popup": True,
                "show_as_banner": True,
                "actions": [
                    InAppNotificationAction(
                        id="view_earnings",
                        label="View Earnings",
                        action_type="navigate",
                        action_data={"route": "/monetization/earnings"}
                    )
                ]
            },
            InAppNotificationType.VIRAL_CONTENT_ALERT: {
                "title": "Your Content is Going Viral!",
                "message": "'{content_title}' has gained {views} views in the last 24 hours!",
                "icon": "zap",
                "color": "#DC2626",
                "category": NotificationCategory.ANALYTICS,
                "priority": NotificationPriority.HIGH,
                "show_as_popup": True,
                "show_as_banner": True,
                "actions": [
                    InAppNotificationAction(
                        id="boost_content",
                        label="Boost Further",
                        action_type="navigate",
                        action_data={"route": "/marketing/boost/{content_id}"}
                    ),
                    InAppNotificationAction(
                        id="view_analytics",
                        label="View Analytics",
                        action_type="navigate",
                        action_data={"route": "/analytics/content/{content_id}"}
                    )
                ]
            }
        }

    async def create_notification(self, notification: InAppNotification) -> str:
        """Create and deliver in-app notification."""
        # Apply user preferences
        if not await self._should_deliver_notification(notification):
            self.logger.debug(f"Notification filtered by user preferences: {notification.id}")
            return notification.id
        
        # Apply template if available
        await self._apply_template(notification)
        
        # Store notification
        await self._store_notification(notification)
        
        # Deliver in real-time if user is connected
        if self.real_time_enabled:
            await self._deliver_real_time(notification)
        
        # Track metrics
        await self._track_notification_metrics(notification)
        
        self.logger.info(f"In-app notification created: {notification.id} for user {notification.user_id}")
        return notification.id

    async def create_bulk_notifications(self, notifications: List[InAppNotification]) -> List[str]:
        """Create multiple notifications efficiently."""
        notification_ids = []
        
        # Process in batches
        for i in range(0, len(notifications), self.batch_size):
            batch = notifications[i:i + self.batch_size]
            
            # Process batch concurrently
            tasks = [self.create_notification(notification) for notification in batch]
            batch_ids = await asyncio.gather(*tasks)
            notification_ids.extend(batch_ids)
        
        return notification_ids

    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False,
        category: Optional[NotificationCategory] = None,
        priority: Optional[NotificationPriority] = None
    ) -> List[InAppNotification]:
        """
Get notifications for a specific user with filtering."""
        user_notifications = self.notifications.get(user_id, [])
        
        # Apply filters
        filtered_notifications = []
        for notification in user_notifications:
            if unread_only and notification.read:
                continue
            if category and notification.category != category:
                continue
            if priority and notification.priority != priority:
                continue
            if notification.expires_at and notification.expires_at < datetime.utcnow():
                continue
                
            filtered_notifications.append(notification)
        
        # Sort by creation date (newest first)
        filtered_notifications.sort(key=lambda n: n.created_at, reverse=True)
        
        # Apply pagination
        return filtered_notifications[offset:offset + limit]

    async def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """
Mark a notification as read."""
        user_notifications = self.notifications.get(user_id, [])
        
        for notification in user_notifications:
            if notification.id == notification_id:
                notification.read = True
                notification.read_at = datetime.utcnow()
                
                # Track engagement metrics
                await self._track_engagement_metrics(notification, "read")
                
                self.logger.debug(f"Notification marked as read: {notification_id}")
                return True
        
        return False

    async def mark_all_notifications_read(self, user_id: str, category: Optional[NotificationCategory] = None) -> int:
        """Mark all notifications as read for a user."""
        user_notifications = self.notifications.get(user_id, [])
        marked_count = 0
        
        for notification in user_notifications:
            if not notification.read:
                if category is None or notification.category == category:
                    notification.read = True
                    notification.read_at = datetime.utcnow()
                    marked_count += 1
        
        self.logger.info(f"Marked {marked_count} notifications as read for user {user_id}")
        return marked_count

    async def dismiss_notification(self, user_id: str, notification_id: str) -> bool:
        """Dismiss a notification."""
        user_notifications = self.notifications.get(user_id, [])
        
        for notification in user_notifications:
            if notification.id == notification_id:
                notification.dismissed = True
                
                # Track engagement metrics
                await self._track_engagement_metrics(notification, "dismissed")
                
                self.logger.debug(f"Notification dismissed: {notification_id}")
                return True
        
        return False

    async def handle_notification_action(self, user_id: str, notification_id: str, action_id: str) -> Dict[str, Any]:
        """Handle notification action execution."""
        user_notifications = self.notifications.get(user_id, [])
        
        for notification in user_notifications:
            if notification.id == notification_id:
                # Find action
                action = None
                if notification.actions:
                    action = next((a for a in notification.actions if a.id == action_id), None)
                
                if not action:
                    return {"success": False, "error": "Action not found"}
                
                # Mark notification as clicked and action taken
                notification.clicked = True
                notification.clicked_at = datetime.utcnow()
                notification.action_taken = action_id
                
                # Track engagement metrics
                await self._track_engagement_metrics(notification, "clicked", action_id)
                
                # Execute action
                result = await self._execute_action(action, notification)
                
                self.logger.info(f"Notification action executed: {notification_id} -> {action_id}")
                return result
        
        return {"success": False, "error": "Notification not found"}

    async def get_notification_counts(self, user_id: str) -> Dict[str, int]:
        """Get notification counts by category and status."""
        user_notifications = self.notifications.get(user_id, [])
        
        counts = {
            "total": 0,
            "unread": 0,
            "by_category": {},
            "by_priority": {},
            "urgent": 0
        }
        
        for notification in user_notifications:
            if notification.expires_at and notification.expires_at < datetime.utcnow():
                continue
                
            counts["total"] += 1
            
            if not notification.read:
                counts["unread"] += 1
            
            # Count by category
            category = notification.category.value
            counts["by_category"][category] = counts["by_category"].get(category, 0) + 1
            
            # Count by priority
            priority = notification.priority.value
            counts["by_priority"][priority] = counts["by_priority"].get(priority, 0) + 1
            
            # Count urgent notifications
            if notification.priority in [NotificationPriority.URGENT, NotificationPriority.CRITICAL]:
                counts["urgent"] += 1
        
        return counts

    async def set_user_preferences(self, user_id: str, preferences: NotificationPreferences) -> bool:
        """Set notification preferences for a user."""
        preferences.user_id = user_id
        self.user_preferences[user_id] = preferences
        
        self.logger.info(f"Notification preferences updated for user {user_id}")
        return True

    async def get_user_preferences(self, user_id: str) -> NotificationPreferences:
        """Get notification preferences for a user."""
        return self.user_preferences.get(user_id, NotificationPreferences(
            user_id=user_id,
            enabled_types=set(InAppNotificationType)
        ))

    async def cleanup_expired_notifications(self) -> int:
        """
Clean up expired notifications."""
        cleaned_count = 0
        current_time = datetime.utcnow()
        
        for user_id, user_notifications in self.notifications.items():
            # Remove expired notifications
            original_count = len(user_notifications)
            user_notifications[:] = [
                n for n in user_notifications
                if not n.expires_at or n.expires_at > current_time
            ]
            
            # Limit notifications per user
            if len(user_notifications) > self.max_notifications_per_user:
                # Keep most recent notifications
                user_notifications.sort(key=lambda n: n.created_at, reverse=True)
                user_notifications[:] = user_notifications[:self.max_notifications_per_user]
            
            cleaned_count += original_count - len(user_notifications)
        
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} expired notifications")
        
        return cleaned_count

    async def get_analytics(self, start_date: datetime, end_date: datetime, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive in-app notification analytics."""
        return {
            "total_sent": await self._get_total_sent(start_date, end_date, user_id),
            "engagement_rate": await self._get_engagement_rate(start_date, end_date, user_id),
            "click_through_rate": await self._get_click_through_rate(start_date, end_date, user_id),
            "type_breakdown": await self._get_type_breakdown(start_date, end_date, user_id),
            "category_performance": await self._get_category_performance(start_date, end_date, user_id),
            "priority_distribution": await self._get_priority_distribution(start_date, end_date, user_id),
            "peak_engagement_times": await self._get_peak_engagement_times(start_date, end_date, user_id),
            "user_preferences_trends": await self._get_user_preferences_trends(start_date, end_date)
        }

    async def _should_deliver_notification(self, notification: InAppNotification) -> bool:
        """Check if notification should be delivered based on user preferences."""
        preferences = await self.get_user_preferences(notification.user_id)
        
        # Check if notification type is enabled
        if notification.type not in preferences.enabled_types:
            return False
        
        # Check priority threshold
        priority_levels = [NotificationPriority.LOW, NotificationPriority.NORMAL, NotificationPriority.HIGH, NotificationPriority.URGENT, NotificationPriority.CRITICAL]
        if priority_levels.index(notification.priority) < priority_levels.index(preferences.priority_threshold):
            return False
        
        # Check if category is muted
        if notification.category in preferences.categories_muted:
            return False
        
        # Check quiet hours
        if preferences.quiet_hours_start is not None and preferences.quiet_hours_end is not None:
            current_hour = datetime.utcnow().hour
            if preferences.quiet_hours_start <= preferences.quiet_hours_end:
                # Same day quiet hours
                if preferences.quiet_hours_start <= current_hour <= preferences.quiet_hours_end:
                    return False
            else:
                # Cross-midnight quiet hours
                if current_hour >= preferences.quiet_hours_start or current_hour <= preferences.quiet_hours_end:
                    return False
        
        return True

    async def _apply_template(self, notification -> None: InAppNotification) -> None:
        """
Apply notification template if available."""
        template = self.notification_templates.get(notification.type)
        if not template:
            return
        
        # Apply template defaults
        if not notification.icon and template.get("icon"):
            notification.icon = template["icon"]
        if not notification.color and template.get("color"):
            notification.color = template["color"]
        if template.get("category") and not hasattr(notification, "category"):
            notification.category = template["category"]
        if template.get("priority") and notification.priority == NotificationPriority.NORMAL:
            notification.priority = template["priority"]
        if template.get("show_as_popup") is not None:
            notification.show_as_popup = template["show_as_popup"]
        if template.get("show_as_banner") is not None:
            notification.show_as_banner = template["show_as_banner"]
        if template.get("persistent") is not None:
            notification.persistent = template["persistent"]
        
        # Apply template actions if not specified
        if not notification.actions and template.get("actions"):
            notification.actions = [
                InAppNotificationAction(**action_data) 
                for action_data in template["actions"]
            ]
        
        # Apply template message formatting
        if template.get("message") and notification.metadata:
            try:
                notification.message = template["message"].format(**notification.metadata)
            except KeyError:
                pass  # Keep original message if formatting fails

    async def _store_notification(self, notification -> None: InAppNotification) -> None:
        """Store notification for user."""
        if notification.user_id not in self.notifications:
            self.notifications[notification.user_id] = []
        
        self.notifications[notification.user_id].append(notification)

    async def _deliver_real_time(self, notification -> None: InAppNotification) -> None:
        """
Deliver notification in real-time via WebSocket."""
        # This would integrate with WebSocket connections in production
        self.logger.debug(f"Real-time delivery simulated for notification: {notification.id}")

    async def _execute_action(self, action: InAppNotificationAction, notification: InAppNotification) -> Dict[str, Any]:
        """Execute notification action."""
        if action.action_type == "navigate":
            return {
                "success": True,
                "action_type": "navigate",
                "route": action.action_data.get("route", "/")
            }
        elif action.action_type == "api_call":
            return {
                "success": True,
                "action_type": "api_call",
                "endpoint": action.action_data.get("endpoint", ""),
                "message": "API call would be executed in production"
            }
        elif action.action_type == "dismiss":
            await self.dismiss_notification(notification.user_id, notification.id)
            return {
                "success": True,
                "action_type": "dismiss",
                "message": "Notification dismissed"
            }
        else:
            return {
                "success": True,
                "action_type": "custom",
                "message": "Custom action would be executed in production"
            }

    async def _track_notification_metrics(self, notification -> None: InAppNotification) -> None:
        """Track notification creation metrics."""
        await self.metrics.increment(
            "inapp_notifications_created_total",
            tags={
                "type": notification.type.value,
                "category": notification.category.value,
                "priority": notification.priority.value
            }
        )

    async def _track_engagement_metrics(self, notification -> None: InAppNotification, action -> None: str, action_id -> None: Optional[str] = None) -> None:
        """Track notification engagement metrics."""
        tags = {
            "type": notification.type.value,
            "category": notification.category.value,
        try:
                    # Request validation
                    if not start_date:
        try:
                    # Request validation
                    if not start_date:
        try:
                    # Request validation
                    if not start_date:
        try:
                    # Request validation
                    if not start_date:
        try:
                    # Request validation
                    if not start_date:
        try:
                    # Request validation
                    if not start_date:
        try:
                    # Request validation
                    if not start_date:
        try:
                    # Request validation
                    if not start_date:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle__get_user_preferences_trends_request(start_date)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_user_preferences_trends failed: {e}")
                    return {"status": "error", "message": str(e)}
                    result = await self._handle__get_peak_engagement_times_request(start_date)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_peak_engagement_times failed: {e}")
                    return {"status": "error", "message": str(e)}
                    result = await self._handle__get_priority_distribution_request(start_date)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_priority_distribution failed: {e}")
                    return {"status": "error", "message": str(e)}
                    result = await self._handle__get_category_performance_request(start_date)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_category_performance failed: {e}")
                    return {"status": "error", "message": str(e)}
                    result = await self._handle__get_type_breakdown_request(start_date)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_type_breakdown failed: {e}")
                    return {"status": "error", "message": str(e)}
                    result = await self._handle__get_click_through_rate_request(start_date)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_click_through_rate failed: {e}")
                    return {"status": "error", "message": str(e)}
                    result = await self._handle__get_engagement_rate_request(start_date)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_engagement_rate failed: {e}")
                    return {"status": "error", "message": str(e)}
                    result = await self._handle__get_total_sent_request(start_date)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_total_sent failed: {e}")
                    return {"status": "error", "message": str(e)}
        }
        
        if action_id:
            tags["action_id"] = action_id
        
        await self.metrics.increment(
            "inapp_notifications_engagement_total",
            tags=tags
        )

    # Analytics methods (simplified implementations)
    async def _get_total_sent(self, start_date: datetime, end_date: datetime, user_id: Optional[str]) -> int:
        return 0

    async def _get_engagement_rate(self, start_date: datetime, end_date: datetime, user_id: Optional[str]) -> float:
        return 0.75

    async def _get_click_through_rate(self, start_date: datetime, end_date: datetime, user_id: Optional[str]) -> float:
        return 0.15

    async def _get_type_breakdown(self, start_date: datetime, end_date: datetime, user_id: Optional[str]) -> Dict[str, int]:
        return {}

    async def _get_category_performance(self, start_date: datetime, end_date: datetime, user_id: Optional[str]) -> Dict[str, Dict]:
        return {}

    async def _get_priority_distribution(self, start_date: datetime, end_date: datetime, user_id: Optional[str]) -> Dict[str, int]:
        return {}

    async def _get_peak_engagement_times(self, start_date: datetime, end_date: datetime, user_id: Optional[str]) -> Dict[str, Any]:
        return {}

    async def _get_user_preferences_trends(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        return {}

# File has syntax issues - needs manual review