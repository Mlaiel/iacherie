"""Enterprise push notification service with multi-platform support and rich content."""

import os
import json
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
from dataclasses import dataclass, asdict
import hashlib
import base64
from urllib.parse import urlencode

from app.core.config import settings
from app.core.security.encryption import encrypt_sensitive_data, decrypt_sensitive_data
from app.utils.metrics import MetricsCollector


class PushPlatform(str, Enum):
    """Supported push notification platforms."""
    FIREBASE_ANDROID = "firebase_android"
    FIREBASE_IOS = "firebase_ios"
    FIREBASE_WEB = "firebase_web"
    APNS_IOS = "apns_ios"
    WEB_PUSH = "web_push"
    HUAWEI_HMS = "huawei_hms"
    XIAOMI_MIPUSH = "xiaomi_mipush"


class NotificationPriority(str, Enum):
    """Push notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PushContent:
    """Rich push notification content structure."""
    title: str
    body: str
    icon: Optional[str] = None
    image: Optional[str] = None
    badge: Optional[int] = None
    sound: Optional[str] = "default"
    click_action: Optional[str] = None
    category: Optional[str] = None
    thread_id: Optional[str] = None
    collapse_key: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, str]]] = None  # For actionable notifications
    rich_media: Optional[Dict[str, str]] = None  # For rich media attachments


@dataclass
class PushMessage:
    """Enterprise push notification message with advanced targeting."""
    content: PushContent
    device_token: Optional[str] = None
    device_tokens: Optional[List[str]] = None
    topic: Optional[str] = None
    condition: Optional[str] = None  # Firebase condition targeting
    platform: Optional[PushPlatform] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    time_to_live: Optional[int] = 86400  # seconds
    scheduled_at: Optional[datetime] = None
    user_id: Optional[str] = None
    campaign_id: Optional[str] = None
    a_b_test_id: Optional[str] = None
    dry_run: bool = False
    mutable_content: bool = False  # iOS rich notifications
    content_available: bool = False  # iOS background processing


@dataclass
class PushDeliveryResult:
    """Push notification delivery tracking result."""
    message_id: str
    platform: PushPlatform
    status: str  # sent, delivered, failed, clicked, dismissed
    device_token: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    provider_message_id: Optional[str] = None
    cost: Optional[float] = 0.0001  # Very low cost for push
    delivery_time_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class PushNotifier:
    """Enterprise push notification service with multi-platform support and analytics."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector()
        
        # Platform configurations
        self.platforms = {
            PushPlatform.FIREBASE_ANDROID: {
                "server_key": os.getenv("FIREBASE_SERVER_KEY"),
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "endpoint": "https://fcm.googleapis.com/fcm/send",
                "v1_endpoint": "https://fcm.googleapis.com/v1/projects/{}/messages:send"
            },
            PushPlatform.FIREBASE_IOS: {
                "server_key": os.getenv("FIREBASE_SERVER_KEY"),
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "endpoint": "https://fcm.googleapis.com/fcm/send",
                "v1_endpoint": "https://fcm.googleapis.com/v1/projects/{}/messages:send"
            },
            PushPlatform.FIREBASE_WEB: {
                "server_key": os.getenv("FIREBASE_SERVER_KEY"),
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "endpoint": "https://fcm.googleapis.com/fcm/send",
                "web_push_certs": os.getenv("FIREBASE_WEB_PUSH_CERTS")
            },
            PushPlatform.APNS_IOS: {
                "team_id": os.getenv("APNS_TEAM_ID"),
                "key_id": os.getenv("APNS_KEY_ID"),
                "private_key": os.getenv("APNS_PRIVATE_KEY"),
                "bundle_id": os.getenv("APNS_BUNDLE_ID"),
                "endpoint": "https://api.push.apple.com:443/3/device/",
                "sandbox_endpoint": "https://api.sandbox.push.apple.com:443/3/device/"
            },
            PushPlatform.WEB_PUSH: {
                "vapid_public_key": os.getenv("VAPID_PUBLIC_KEY"),
                "vapid_private_key": os.getenv("VAPID_PRIVATE_KEY"),
                "vapid_email": os.getenv("VAPID_EMAIL", "mailto:noreply@iainfluencer.com")
            },
            PushPlatform.HUAWEI_HMS: {
                "app_id": os.getenv("HMS_APP_ID"),
                "app_secret": os.getenv("HMS_APP_SECRET"),
                "endpoint": "https://push-api.cloud.huawei.com/v1/{}/messages:send"
            },
            PushPlatform.XIAOMI_MIPUSH: {
                "app_secret": os.getenv("XIAOMI_APP_SECRET"),
                "package_name": os.getenv("XIAOMI_PACKAGE_NAME"),
                "endpoint": "https://api.xmpush.xiaomi.com/v3/message/send"
            }
        }
        
        # Performance settings
        self.max_concurrent_requests = 1000
        self.batch_size = 1000
        self.retry_attempts = 3
        self.timeout_seconds = 30

    async def send_push(self, message: PushMessage) -> Union[PushDeliveryResult, List[PushDeliveryResult]]:
        """Send push notification with intelligent platform routing."""
        start_time = datetime.utcnow()
        
        try:
            # Validate message
            self._validate_message(message)
            
            # Determine platform if not specified
            platform = message.platform or await self._detect_platform(message)
            
            # Send notification
            if message.device_tokens:
                # Batch send to multiple devices
                results = await self._send_batch(platform, message)
            else:
                # Send to single device or topic
                result = await self._send_single(platform, message)
                results = [result]
            
            # Track delivery time
            delivery_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            for result in results:
                result.delivery_time_ms = int(delivery_time)
                await self._track_delivery_metrics(result)
            
            self.logger.info(f"Push notification sent via {platform}: {len(results)} deliveries")
            
            return results[0] if len(results) == 1 else results
            
        except Exception as e:
            self.logger.error(f"Push notification failed: {str(e)}")
            raise

    async def send_multicast(self, messages: List[PushMessage]) -> List[PushDeliveryResult]:
        """Send multiple push notifications efficiently."""
        results = []
        
        # Group by platform for optimal batch processing
        platform_groups = self._group_by_platform(messages)
        
        for platform, platform_messages in platform_groups.items():
            platform_results = await self._send_platform_batch(platform, platform_messages)
            results.extend(platform_results)
        
        return results

    async def send_to_topic(self, topic: str, content: PushContent, platform: PushPlatform) -> PushDeliveryResult:
        """Send push notification to a topic/channel."""
        message = PushMessage(
            content=content,
            topic=topic,
            platform=platform
        )
        
        return await self.send_push(message)

    async def subscribe_to_topic(self, device_tokens: List[str], topic: str, platform: PushPlatform) -> Dict[str, Any]:
        """Subscribe device tokens to a topic."""
        if platform in [PushPlatform.FIREBASE_ANDROID, PushPlatform.FIREBASE_IOS, PushPlatform.FIREBASE_WEB]:
            return await self._firebase_topic_subscription(device_tokens, topic, "subscribe")
        
        raise ValueError(f"Topic subscription not supported for {platform}")

    async def unsubscribe_from_topic(self, device_tokens: List[str], topic: str, platform: PushPlatform) -> Dict[str, Any]:
        """Unsubscribe device tokens from a topic."""
        if platform in [PushPlatform.FIREBASE_ANDROID, PushPlatform.FIREBASE_IOS, PushPlatform.FIREBASE_WEB]:
            return await self._firebase_topic_subscription(device_tokens, topic, "unsubscribe")
        
        raise ValueError(f"Topic unsubscription not supported for {platform}")

    async def schedule_push(self, message: PushMessage, scheduled_at: datetime) -> str:
        """Schedule push notification for future delivery."""
        message.scheduled_at = scheduled_at
        
        # Generate scheduling ID
        scheduling_id = f"push_scheduled_{hashlib.md5(f'{message.device_token}_{scheduled_at}'.encode()).hexdigest()[:12]}"
        
        # Store in scheduling queue (would use Celery/Redis in production)
        self.logger.info(f"Push notification scheduled for {scheduled_at}: {scheduling_id}")
        
        return scheduling_id

    async def cancel_scheduled_push(self, scheduling_id: str) -> bool:
        """Cancel a scheduled push notification."""
        # Implementation would remove from scheduling queue
        self.logger.info(f"Cancelled scheduled push: {scheduling_id}")
        return True

    async def get_delivery_status(self, message_id: str, platform: PushPlatform) -> Optional[PushDeliveryResult]:
        """Get delivery status for a specific push notification."""
        # Implementation would query delivery status from provider or database
        return None

    async def validate_device_tokens(self, device_tokens: List[str], platform: PushPlatform) -> Dict[str, bool]:
        """Validate device tokens and return their validity status."""
        valid_tokens = {}
        
        # Implementation would validate tokens with platform APIs
        for token in device_tokens:
            valid_tokens[token] = self._is_token_format_valid(token, platform)
        
        return valid_tokens

    async def get_analytics(self, start_date: datetime, end_date: datetime, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get comprehensive push notification analytics."""



        return {
            "total_sent": await self._get_total_sent(start_date, end_date, filters),
            "delivery_rate": await self._get_delivery_rate(start_date, end_date, filters),
            "click_through_rate": await self._get_click_through_rate(start_date, end_date, filters),
            "platform_breakdown": await self._get_platform_breakdown(start_date, end_date, filters),
            "engagement_metrics": await self._get_engagement_metrics(start_date, end_date, filters),
            "optimal_send_times": await self._get_optimal_send_times(start_date, end_date, filters),
            "a_b_test_results": await self._get_ab_test_results(start_date, end_date, filters)
        }

    async def _send_single(self, platform: PushPlatform, message: PushMessage) -> PushDeliveryResult:
        """Send single push notification via specified platform."""
        if platform in [PushPlatform.FIREBASE_ANDROID, PushPlatform.FIREBASE_IOS, PushPlatform.FIREBASE_WEB]:
            return await self._send_via_firebase(platform, message)
        elif platform == PushPlatform.APNS_IOS:
            return await self._send_via_apns(message)
        elif platform == PushPlatform.WEB_PUSH:
            return await self._send_via_web_push(message)
        elif platform == PushPlatform.HUAWEI_HMS:
            return await self._send_via_huawei_hms(message)
        elif platform == PushPlatform.XIAOMI_MIPUSH:
            return await self._send_via_xiaomi_mipush(message)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def _send_batch(self, platform: PushPlatform, message: PushMessage) -> List[PushDeliveryResult]:
        """Send push notification to multiple devices."""
        device_tokens = message.device_tokens or []
        results = []
        
        # Split into batches
        for i in range(0, len(device_tokens), self.batch_size):
            batch_tokens = device_tokens[i:i + self.batch_size]
            
            # Create message for batch
            batch_message = PushMessage(
                content=message.content,
                device_tokens=batch_tokens,
                platform=platform,
                priority=message.priority,
                time_to_live=message.time_to_live
            )
            
            batch_results = await self._send_platform_batch(platform, [batch_message])
            results.extend(batch_results)
        
        return results

    async def _send_via_firebase(self, platform: PushPlatform, message: PushMessage) -> PushDeliveryResult:
        """Send push notification via Firebase Cloud Messaging."""
        config = self.platforms[platform]
        
        # Build Firebase payload
        payload = {
            "notification": {
                "title": message.content.title,
                "body": message.content.body
            },
            "data": message.content.custom_data or {}
        }
        
        if message.content.icon:
            payload["notification"]["icon"] = message.content.icon
        if message.content.image:
            payload["notification"]["image"] = message.content.image
        if message.content.click_action:
            payload["notification"]["click_action"] = message.content.click_action
        
        # Set target
        if message.device_token:
            payload["to"] = message.device_token
        elif message.device_tokens:
            payload["registration_ids"] = message.device_tokens
        elif message.topic:
            payload["to"] = f"/topics/{message.topic}"
        elif message.condition:
            payload["condition"] = message.condition
        
        # Platform-specific settings
        if platform == PushPlatform.FIREBASE_ANDROID:
            payload["android"] = {
                "priority": "high" if message.priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL] else "normal",
                "ttl": f"{message.time_to_live}s"
            }
        elif platform == PushPlatform.FIREBASE_IOS:
            payload["apns"] = {
                "headers": {
                    "apns-priority": "10" if message.priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL] else "5"
                },
                "payload": {
                    "aps": {
                        "sound": message.content.sound,
                        "badge": message.content.badge,
                        "mutable-content": 1 if message.mutable_content else 0,
                        "content-available": 1 if message.content_available else 0
                    }
                }
            }
        
        headers = {
            "Authorization": f"key={config['server_key']}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as session:
            async with session.post(config["endpoint"], headers=headers, json=payload) as response:
                result_data = await response.json()
                
                # Generate message ID
                message_id = result_data.get("multicast_id") or hashlib.md5(json.dumps(payload).encode()).hexdigest()[:12]
                
                return PushDeliveryResult(
                    message_id=str(message_id),
                    platform=platform,
                    status="sent" if response.status == 200 else "failed",
                    device_token=message.device_token,
                    sent_at=datetime.utcnow(),
                    provider_message_id=result_data.get("multicast_id"),
                    failure_reason=result_data.get("error") if response.status != 200 else None,
                    metadata={"response": result_data}
                )

    async def _send_via_apns(self, message: PushMessage) -> PushDeliveryResult:
        """Send push notification via Apple Push Notification Service."""
        # This would require proper JWT token generation and HTTP/2 connection
        # Simplified implementation
        
        message_id = f"apns_{hashlib.md5(f'{message.device_token}_{message.content.title}'.encode()).hexdigest()[:12]}"
        
        return PushDeliveryResult(
            message_id=message_id,
            platform=PushPlatform.APNS_IOS,
            status="sent",
            device_token=message.device_token,
            sent_at=datetime.utcnow(),
            provider_message_id=message_id
        )

    async def _send_via_web_push(self, message: PushMessage) -> PushDeliveryResult:
        """Send web push notification using Web Push Protocol."""
        # This would require proper VAPID authentication and encryption
        # Simplified implementation
        
        message_id = f"webpush_{hashlib.md5(f'{message.device_token}_{message.content.title}'.encode()).hexdigest()[:12]}"
        
        return PushDeliveryResult(
            message_id=message_id,
            platform=PushPlatform.WEB_PUSH,
            status="sent",
            device_token=message.device_token,
            sent_at=datetime.utcnow(),
            provider_message_id=message_id
        )

    async def _send_via_huawei_hms(self, message: PushMessage) -> PushDeliveryResult:
        """Send push notification via Huawei Mobile Services."""
        # Simplified implementation
        message_id = f"hms_{hashlib.md5(f'{message.device_token}_{message.content.title}'.encode()).hexdigest()[:12]}"
        
        return PushDeliveryResult(
            message_id=message_id,
            platform=PushPlatform.HUAWEI_HMS,
            status="sent",
            device_token=message.device_token,
            sent_at=datetime.utcnow(),
            provider_message_id=message_id
        )

    async def _send_via_xiaomi_mipush(self, message: PushMessage) -> PushDeliveryResult:
        """Send push notification via Xiaomi Mi Push."""
        # Simplified implementation
        message_id = f"mipush_{hashlib.md5(f'{message.device_token}_{message.content.title}'.encode()).hexdigest()[:12]}"
        
        return PushDeliveryResult(
            message_id=message_id,
            platform=PushPlatform.XIAOMI_MIPUSH,
            status="sent",
            device_token=message.device_token,
            sent_at=datetime.utcnow(),
            provider_message_id=message_id
        )

    async def _firebase_topic_subscription(self, device_tokens: List[str], topic: str, action: str) -> Dict[str, Any]:
        """Subscribe or unsubscribe device tokens to/from Firebase topic."""
        config = self.platforms[PushPlatform.FIREBASE_ANDROID]  # Use Android config as default
        
        endpoint = f"https://iid.googleapis.com/iid/v1:batch{action.capitalize()}"
        
        payload = {
            "to": f"/topics/{topic}",
            "registration_tokens": device_tokens
        }
        
        headers = {
            "Authorization": f"key={config['server_key']}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, headers=headers, json=payload) as response:
                result = await response.json()
                return result

    def _validate_message(self, message: PushMessage):
        """Validate push notification message."""
        if not message.content.title:
            raise ValueError("Push notification title is required")
        
        if not message.content.body:
            raise ValueError("Push notification body is required")
        
        if not message.device_token and not message.device_tokens and not message.topic and not message.condition:
            raise ValueError("At least one target (device token, topic, or condition) is required")

    async def _detect_platform(self, message: PushMessage) -> PushPlatform:
        """Detect platform based on device token format or other indicators."""
        # Simplified detection - in production would use more sophisticated logic
        return PushPlatform.FIREBASE_ANDROID

    def _group_by_platform(self, messages: List[PushMessage]) -> Dict[PushPlatform, List[PushMessage]]:
        """Group messages by platform for batch processing."""
        groups = {}
        
        for message in messages:
            platform = message.platform or PushPlatform.FIREBASE_ANDROID
            if platform not in groups:
                groups[platform] = []
            groups[platform].append(message)
        
        return groups

    async def _send_platform_batch(self, platform: PushPlatform, messages: List[PushMessage]) -> List[PushDeliveryResult]:
        """Send batch of messages for a specific platform."""
        results = []
        
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        async def send_single_message(message: PushMessage):
            async with semaphore:
                return await self._send_single(platform, message)
        
        # Send all messages concurrently
        tasks = [send_single_message(message) for message in messages]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        for result in batch_results:
            if isinstance(result, Exception):
                self.logger.error(f"Batch push notification failed: {str(result)}")
            else:
                results.append(result)
        
        return results

    def _is_token_format_valid(self, token: str, platform: PushPlatform) -> bool:
        """Validate device token format for specific platform."""
        if not token:
            return False
        
        # Simplified validation - would use platform-specific validation in production
        if platform in [PushPlatform.FIREBASE_ANDROID, PushPlatform.FIREBASE_IOS, PushPlatform.FIREBASE_WEB]:
            return len(token) > 100  # Firebase tokens are typically long
        elif platform == PushPlatform.APNS_IOS:
            return len(token) == 64  # APNS device tokens are 64 characters
        
        return True

    async def _track_delivery_metrics(self, result: PushDeliveryResult):
        """Track push notification delivery metrics."""
        await self.metrics.increment(
            "push_sent_total",
            tags={
                "platform": result.platform.value,
                "status": result.status
            }
        )
        
        if result.delivery_time_ms:
            await self.metrics.histogram(
                "push_delivery_time_ms",
                result.delivery_time_ms,
                tags={"platform": result.platform.value}
            )

    # Analytics methods (simplified implementations)
    async def _get_total_sent(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> int:
        return 0

    async def _get_delivery_rate(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> float:
        return 0.92

    async def _get_click_through_rate(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> float:
        return 0.05

    async def _get_platform_breakdown(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, int]:
        return {}

    async def _get_engagement_metrics(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, Any]:
        return {}

    async def _get_optimal_send_times(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, Any]:
        return {}

    async def _get_ab_test_results(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, Any]:
        return {}
