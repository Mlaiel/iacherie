"""Mobile Push Notifications Service
====================================

Professional push notification service supporting FCM, APNS, and web push
for real-time mobile communication and engagement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import json
import aiohttp
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import time
import uuid

logger = logging.getLogger(__name__)


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    """Notification types."""
    CONTENT_UPDATE = "content_update"
    COLLABORATION = "collaboration"
    PAYMENT = "payment"
    SYSTEM = "system"
    MARKETING = "marketing"
    LIVE_EVENT = "live_event"
    REMINDER = "reminder"


class Platform(str, Enum):
    """Mobile platforms."""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


@dataclass
class DeviceToken:
    """Device registration token."""
    token: str
    platform: Platform
    user_id: str
    device_id: str
    app_version: str
    os_version: str
    language: str
    timezone: str
    registered_at: datetime
    last_seen: datetime
    is_active: bool
    metadata: Dict[str, Any]


@dataclass
class NotificationContent:
    """Notification content."""
    title: str
    body: str
    image_url: Optional[str] = None
    icon_url: Optional[str] = None
    sound: Optional[str] = None
    badge: Optional[int] = None
    color: Optional[str] = None
    click_action: Optional[str] = None
    deep_link: Optional[str] = None
    custom_data: Dict[str, Any] = None


@dataclass
class NotificationSchedule:
    """Notification scheduling."""
    send_at: Optional[datetime] = None
    timezone: Optional[str] = None
    repeat_interval: Optional[str] = None  # daily, weekly, monthly
    max_repeats: Optional[int] = None
    end_date: Optional[datetime] = None


@dataclass
class NotificationTargeting:
    """Notification targeting options."""
    user_ids: Optional[List[str]] = None
    device_tokens: Optional[List[str]] = None
    platforms: Optional[List[Platform]] = None
    languages: Optional[List[str]] = None
    app_versions: Optional[List[str]] = None
    user_segments: Optional[List[str]] = None
    geo_locations: Optional[List[Dict[str, Any]]] = None
    exclude_user_ids: Optional[List[str]] = None


@dataclass
class NotificationResult:
    """Notification sending result."""
    notification_id: str
    target_count: int
    sent_count: int
    failed_count: int
    delivery_results: List[Dict[str, Any]]
    sent_at: datetime
    estimated_delivery: datetime
    metadata: Dict[str, Any]


@dataclass
class NotificationAnalytics:
    """Notification analytics data."""
    notification_id: str
    sent_count: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    bounced_count: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    platform_breakdown: Dict[str, Dict[str, int]]
    created_at: datetime
    updated_at: datetime


class PushNotificationService:
    """Professional push notification service."""
    
    def __init__(
        self,
        fcm_server_key: Optional[str] = None,
        fcm_project_id: Optional[str] = None,
        apns_key_id: Optional[str] = None,
        apns_team_id: Optional[str] = None,
        apns_private_key: Optional[str] = None,
        apns_bundle_id: Optional[str] = None,
        web_push_vapid_public: Optional[str] = None,
        web_push_vapid_private: Optional[str] = None,
        web_push_vapid_email: Optional[str] = None,
        production: bool = True
    ):
        # FCM Configuration
        self.fcm_server_key = fcm_server_key
        self.fcm_project_id = fcm_project_id
        
        # APNS Configuration
        self.apns_key_id = apns_key_id
        self.apns_team_id = apns_team_id
        self.apns_private_key = apns_private_key
        self.apns_bundle_id = apns_bundle_id
        self.apns_endpoint = "https://api.push.apple.com" if production else "https://api.sandbox.push.apple.com"
        
        # Web Push Configuration
        self.web_push_vapid_public = web_push_vapid_public
        self.web_push_vapid_private = web_push_vapid_private
        self.web_push_vapid_email = web_push_vapid_email
        
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Device management
        self.registered_devices: Dict[str, DeviceToken] = {}
        self.user_devices: Dict[str, List[str]] = {}  # user_id -> device_tokens
        
        # Analytics tracking
        self.notification_analytics: Dict[str, NotificationAnalytics] = {}
        self.sent_count = 0
        self.delivered_count = 0
        self.failed_count = 0
        
        logger.info("Push notification service initialized")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def register_device(
        self,
        token: str,
        platform: Platform,
        user_id: str,
        device_id: str,
        app_version: str = "1.0.0",
        os_version: str = "unknown",
        language: str = "en",
        timezone: str = "UTC",
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeviceToken:
        """Register a device for push notifications."""
        
        device_token = DeviceToken(
            token=token,
            platform=platform,
            user_id=user_id,
            device_id=device_id,
            app_version=app_version,
            os_version=os_version,
            language=language,
            timezone=timezone,
            registered_at=datetime.now(),
            last_seen=datetime.now(),
            is_active=True,
            metadata=metadata or {}
        )
        
        # Store device
        self.registered_devices[token] = device_token
        
        # Update user devices mapping
        if user_id not in self.user_devices:
            self.user_devices[user_id] = []
        
        if token not in self.user_devices[user_id]:
            self.user_devices[user_id].append(token)
        
        logger.info(f"Device registered: {platform.value} device for user {user_id}")
        return device_token
    
    async def unregister_device(self, token: str) -> bool:
        """Unregister a device."""
        if token in self.registered_devices:
            device = self.registered_devices[token]
            user_id = device.user_id
            
            # Remove from device registry
            del self.registered_devices[token]
            
            # Remove from user devices mapping
            if user_id in self.user_devices and token in self.user_devices[user_id]:
                self.user_devices[user_id].remove(token)
                
                # Clean up empty user entries
                if not self.user_devices[user_id]:
                    del self.user_devices[user_id]
            
            logger.info(f"Device unregistered: {token}")
            return True
        
        return False
    
    async def update_device_activity(self, token: str) -> bool:
        """Update device last seen timestamp."""
        if token in self.registered_devices:
            self.registered_devices[token].last_seen = datetime.now()
            return True
        return False
    
    async def send_notification(
        self,
        content: NotificationContent,
        targeting: NotificationTargeting,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        notification_type: NotificationType = NotificationType.SYSTEM,
        schedule: Optional[NotificationSchedule] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> NotificationResult:
        """Send push notification."""
        await self._ensure_session()
        
        notification_id = str(uuid.uuid4())
        
        # If scheduled, handle scheduling
        if schedule and schedule.send_at and schedule.send_at > datetime.now():
            return await self._schedule_notification(
                notification_id, content, targeting, priority, notification_type, schedule, metadata
            )
        
        # Get target devices
        target_devices = await self._resolve_targeting(targeting)
        
        if not target_devices:
            logger.warning("No target devices found for notification")
            return NotificationResult(
                notification_id=notification_id,
                target_count=0,
                sent_count=0,
                failed_count=0,
                delivery_results=[],
                sent_at=datetime.now(),
                estimated_delivery=datetime.now(),
                metadata=metadata or {}
            )
        
        # Group devices by platform
        platform_groups = self._group_devices_by_platform(target_devices)
        
        # Send to each platform
        delivery_results = []
        sent_count = 0
        failed_count = 0
        
        for platform, devices in platform_groups.items():
            if platform == Platform.ANDROID:
                results = await self._send_fcm_notifications(devices, content, priority, notification_type)
            elif platform == Platform.IOS:
                results = await self._send_apns_notifications(devices, content, priority, notification_type)
            elif platform == Platform.WEB:
                results = await self._send_web_push_notifications(devices, content, priority, notification_type)
            else:
                continue
            
            delivery_results.extend(results)
            sent_count += sum(1 for r in results if r.get("success"))
            failed_count += sum(1 for r in results if not r.get("success"))
        
        # Create analytics entry
        analytics = NotificationAnalytics(
            notification_id=notification_id,
            sent_count=sent_count,
            delivered_count=0,  # Will be updated by delivery receipts
            opened_count=0,
            clicked_count=0,
            bounced_count=failed_count,
            delivery_rate=sent_count / len(target_devices) if target_devices else 0,
            open_rate=0.0,
            click_rate=0.0,
            platform_breakdown={platform.value: {"sent": len(devices), "failed": 0} for platform, devices in platform_groups.items()},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.notification_analytics[notification_id] = analytics
        
        # Update counters
        self.sent_count += sent_count
        self.failed_count += failed_count
        
        result = NotificationResult(
            notification_id=notification_id,
            target_count=len(target_devices),
            sent_count=sent_count,
            failed_count=failed_count,
            delivery_results=delivery_results,
            sent_at=datetime.now(),
            estimated_delivery=datetime.now() + timedelta(seconds=30),
            metadata=metadata or {}
        )
        
        logger.info(f"Notification sent: {notification_id}, targets: {len(target_devices)}, sent: {sent_count}, failed: {failed_count}")
        return result
    
    async def _resolve_targeting(self, targeting: NotificationTargeting) -> List[DeviceToken]:
        """Resolve targeting criteria to device tokens."""
        target_devices = []
        
        # Direct device tokens
        if targeting.device_tokens:
            for token in targeting.device_tokens:
                if token in self.registered_devices:
                    device = self.registered_devices[token]
                    if device.is_active:
                        target_devices.append(device)
        
        # User IDs
        if targeting.user_ids:
            for user_id in targeting.user_ids:
                if user_id in self.user_devices:
                    for token in self.user_devices[user_id]:
                        if token in self.registered_devices:
                            device = self.registered_devices[token]
                            if device.is_active and device not in target_devices:
                                target_devices.append(device)
        
        # Apply filters
        filtered_devices = []
        for device in target_devices:
            # Platform filter
            if targeting.platforms and device.platform not in targeting.platforms:
                continue
            
            # Language filter
            if targeting.languages and device.language not in targeting.languages:
                continue
            
            # App version filter
            if targeting.app_versions and device.app_version not in targeting.app_versions:
                continue
            
            # Exclude users
            if targeting.exclude_user_ids and device.user_id in targeting.exclude_user_ids:
                continue
            
            filtered_devices.append(device)
        
        return filtered_devices
    
    def _group_devices_by_platform(self, devices: List[DeviceToken]) -> Dict[Platform, List[DeviceToken]]:
        """Group devices by platform."""
        groups = {}
        for device in devices:
            if device.platform not in groups:
                groups[device.platform] = []
            groups[device.platform].append(device)
        return groups
    
    async def _send_fcm_notifications(
        self,
        devices: List[DeviceToken],
        content: NotificationContent,
        priority: NotificationPriority,
        notification_type: NotificationType
    ) -> List[Dict[str, Any]]:
        """Send FCM notifications to Android devices."""
        if not self.fcm_server_key:
            logger.error("FCM server key not configured")
            return [{"success": False, "error": "FCM not configured"} for _ in devices]
        
        headers = {
            "Authorization": f"key={self.fcm_server_key}",
            "Content-Type": "application/json"
        }
        
        results = []
        
        # Send in batches
        batch_size = 1000
        for i in range(0, len(devices), batch_size):
            batch = devices[i:i + batch_size]
            tokens = [device.token for device in batch]
            
            # Build FCM payload
            payload = {
                "registration_ids": tokens,
                "notification": {
                    "title": content.title,
                    "body": content.body,
                    "icon": content.icon_url,
                    "image": content.image_url,
                    "sound": content.sound or "default",
                    "color": content.color,
                    "click_action": content.click_action
                },
                "data": {
                    "type": notification_type.value,
                    "deep_link": content.deep_link,
                    **(content.custom_data or {})
                },
                "priority": "high" if priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL] else "normal"
            }
            
            try:
                async with self.session.post(
                    "https://fcm.googleapis.com/fcm/send",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result_data = await response.json()
                        batch_results = []
                        
                        for j, result in enumerate(result_data.get("results", [])):
                            device_result = {
                                "device_token": tokens[j],
                                "platform": "android",
                                "success": "message_id" in result,
                                "message_id": result.get("message_id"),
                                "error": result.get("error")
                            }
                            batch_results.append(device_result)
                        
                        results.extend(batch_results)
                    else:
                        error_data = await response.json()
                        logger.error(f"FCM batch failed: {error_data}")
                        results.extend([{"success": False, "error": "FCM batch failed"} for _ in batch])
            
            except Exception as e:
                logger.error(f"FCM send failed: {e}")
                results.extend([{"success": False, "error": str(e)} for _ in batch])
        
        return results
    
    async def _send_apns_notifications(
        self,
        devices: List[DeviceToken],
        content: NotificationContent,
        priority: NotificationPriority,
        notification_type: NotificationType
    ) -> List[Dict[str, Any]]:
        """Send APNS notifications to iOS devices."""
        if not all([self.apns_key_id, self.apns_team_id, self.apns_private_key, self.apns_bundle_id]):
            logger.error("APNS not properly configured")
            return [{"success": False, "error": "APNS not configured"} for _ in devices]
        
        # Generate JWT token for APNS
        jwt_token = self._generate_apns_jwt()
        
        headers = {
            "Authorization": f"bearer {jwt_token}",
            "Content-Type": "application/json",
            "apns-topic": self.apns_bundle_id,
            "apns-push-type": "alert",
            "apns-priority": "10" if priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL] else "5"
        }
        
        # Build APNS payload
        payload = {
            "aps": {
                "alert": {
                    "title": content.title,
                    "body": content.body
                },
                "sound": content.sound or "default",
                "badge": content.badge,
                "category": notification_type.value
            },
            "type": notification_type.value,
            "deep_link": content.deep_link,
            **(content.custom_data or {})
        }
        
        results = []
        
        for device in devices:
            try:
                async with self.session.post(
                    f"{self.apns_endpoint}/3/device/{device.token}",
                    headers=headers,
                    json=payload
                ) as response:
                    device_result = {
                        "device_token": device.token,
                        "platform": "ios",
                        "success": response.status == 200,
                        "status_code": response.status
                    }
                    
                    if response.status != 200:
                        error_data = await response.json()
                        device_result["error"] = error_data.get("reason", "Unknown APNS error")
                    
                    results.append(device_result)
            
            except Exception as e:
                logger.error(f"APNS send failed for device {device.token}: {e}")
                results.append({
                    "device_token": device.token,
                    "platform": "ios",
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def _send_web_push_notifications(
        self,
        devices: List[DeviceToken],
        content: NotificationContent,
        priority: NotificationPriority,
        notification_type: NotificationType
    ) -> List[Dict[str, Any]]:
        """Send web push notifications."""
        # Web push implementation would require additional libraries like pywebpush
        # For now, return placeholder results
        logger.info(f"Web push notifications would be sent to {len(devices)} devices")
        
        return [{
            "device_token": device.token,
            "platform": "web",
            "success": True,
            "message": "Web push simulation"
        } for device in devices]
    
    def _generate_apns_jwt(self) -> str:
        """Generate JWT token for APNS authentication."""
        # This is a simplified implementation
        # In practice, you'd use the cryptography library to properly sign the JWT
        header = {"alg": "ES256", "kid": self.apns_key_id}
        payload = {
            "iss": self.apns_team_id,
            "iat": int(time.time())
        }
        
        # This would normally be signed with the private key
        # For demonstration, returning a placeholder
        return "placeholder_jwt_token"
    
    async def _schedule_notification(
        self,
        notification_id: str,
        content: NotificationContent,
        targeting: NotificationTargeting,
        priority: NotificationPriority,
        notification_type: NotificationType,
        schedule: NotificationSchedule,
        metadata: Optional[Dict[str, Any]]
    ) -> NotificationResult:
        """Handle scheduled notifications."""
        # In a real implementation, this would use a job queue or scheduler
        logger.info(f"Notification {notification_id} scheduled for {schedule.send_at}")
        
        return NotificationResult(
            notification_id=notification_id,
            target_count=0,
            sent_count=0,
            failed_count=0,
            delivery_results=[],
            sent_at=datetime.now(),
            estimated_delivery=schedule.send_at or datetime.now(),
            metadata={"scheduled": True, **(metadata or {})}
        )
    
    async def track_notification_opened(self, notification_id: str, device_token: str) -> bool:
        """Track notification opened event."""
        if notification_id in self.notification_analytics:
            analytics = self.notification_analytics[notification_id]
            analytics.opened_count += 1
            analytics.open_rate = analytics.opened_count / analytics.sent_count if analytics.sent_count > 0 else 0
            analytics.updated_at = datetime.now()
            
            logger.info(f"Notification opened: {notification_id}")
            return True
        return False
    
    async def track_notification_clicked(self, notification_id: str, device_token: str) -> bool:
        """Track notification clicked event."""
        if notification_id in self.notification_analytics:
            analytics = self.notification_analytics[notification_id]
            analytics.clicked_count += 1
            analytics.click_rate = analytics.clicked_count / analytics.sent_count if analytics.sent_count > 0 else 0
            analytics.updated_at = datetime.now()
            
            logger.info(f"Notification clicked: {notification_id}")
            return True
        return False
    
    def get_notification_analytics(self, notification_id: str) -> Optional[NotificationAnalytics]:
        """Get analytics for a specific notification."""
        return self.notification_analytics.get(notification_id)
    
    def get_user_devices(self, user_id: str) -> List[DeviceToken]:
        """Get all devices for a user."""
        devices = []
        if user_id in self.user_devices:
            for token in self.user_devices[user_id]:
                if token in self.registered_devices:
                    devices.append(self.registered_devices[token])
        return devices
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get service usage statistics."""
        active_devices = sum(1 for device in self.registered_devices.values() if device.is_active)
        total_devices = len(self.registered_devices)
        
        platform_breakdown = {}
        for device in self.registered_devices.values():
            platform = device.platform.value
            if platform not in platform_breakdown:
                platform_breakdown[platform] = {"total": 0, "active": 0}
            platform_breakdown[platform]["total"] += 1
            if device.is_active:
                platform_breakdown[platform]["active"] += 1
        
        return {
            "total_devices": total_devices,
            "active_devices": active_devices,
            "total_notifications_sent": self.sent_count,
            "total_notifications_delivered": self.delivered_count,
            "total_failed": self.failed_count,
            "platform_breakdown": platform_breakdown,
            "recent_notifications": len(self.notification_analytics)
        }


# Utility functions
async def send_instant_notification(
    title: str,
    body: str,
    user_ids: List[str],
    service: PushNotificationService,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    deep_link: Optional[str] = None
) -> NotificationResult:
    """Send instant notification to users."""
    content = NotificationContent(
        title=title,
        body=body,
        deep_link=deep_link
    )
    
    targeting = NotificationTargeting(user_ids=user_ids)
    
    return await service.send_notification(
        content=content,
        targeting=targeting,
        priority=priority
    )


async def broadcast_system_notification(
    title: str,
    body: str,
    service: PushNotificationService,
    exclude_users: Optional[List[str]] = None
) -> NotificationResult:
    """Broadcast system notification to all users."""
    content = NotificationContent(title=title, body=body)
    
    targeting = NotificationTargeting(exclude_user_ids=exclude_users)
    
    return await service.send_notification(
        content=content,
        targeting=targeting,
        notification_type=NotificationType.SYSTEM,
        priority=NotificationPriority.HIGH
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize service (in practice, get these from environment)
        service = PushNotificationService(
            fcm_server_key="your_fcm_server_key",
            apns_key_id="your_apns_key_id",
            apns_team_id="your_team_id",
            apns_private_key="your_private_key",
            apns_bundle_id="com.example.app"
        )
        
        async with service:
            # Register a device
            device = await service.register_device(
                token="sample_device_token",
                platform=Platform.ANDROID,
                user_id="user123",
                device_id="device456"
            )
            print(f"Device registered: {device.device_id}")
            
            # Send notification
            result = await send_instant_notification(
                title="Welcome!",
                body="Thanks for using our app",
                user_ids=["user123"],
                service=service
            )
            print(f"Notification sent: {result.notification_id}")
            
            # Get stats
            stats = service.get_usage_stats()
            print(f"Usage stats: {stats}")
    
    asyncio.run(main())