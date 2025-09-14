"""
Enterprise Push Notification Service - Clean Implementation
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import json

from .config import settings, MetricsCollector, metrics

class PushPlatform(Enum):
    """Push notification platforms"""
    FIREBASE_ANDROID = "firebase_android"
    FIREBASE_IOS = "firebase_ios"
    FIREBASE_WEB = "firebase_web"
    APNS_IOS = "apns_ios"
    WNS_WINDOWS = "wns_windows"
    ADM_AMAZON = "adm_amazon"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PushContent:
    """Push notification content"""
    title: str
    body: str
    icon: Optional[str] = None
    image: Optional[str] = None
    badge: Optional[int] = None
    sound: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

@dataclass
class PushMessage:
    """Push notification message"""
    user_id: str
    device_token: str
    platform: PushPlatform
    content: PushContent
    priority: NotificationPriority = NotificationPriority.NORMAL
    ttl_seconds: Optional[int] = None
    collapse_key: Optional[str] = None
    notification_id: Optional[str] = None

@dataclass
class PushDeliveryResult:
    """Push notification delivery result"""
    message_id: str
    user_id: str
    platform: PushPlatform
    status: str
    delivered_at: Optional[datetime] = None
    delivery_time: Optional[float] = None
    error_message: Optional[str] = None

class PushNotifier:
    """Enterprise Push Notification Service"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the push notifier"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.metrics = metrics
        
        # Configuration
        self.max_concurrent_requests = self.config.get('max_concurrent_requests', 100)
        self.rate_limits = {
            PushPlatform.FIREBASE_ANDROID: 1000,
            PushPlatform.FIREBASE_IOS: 1000,
            PushPlatform.FIREBASE_WEB: 1000,
            PushPlatform.APNS_IOS: 500,
        }
        
        self.logger.info("PushNotifier initialized successfully")

    async def send_notification(self, message: PushMessage) -> PushDeliveryResult:
        """Send a single push notification"""
        try:
            start_time = datetime.now()
            
            # Validate message
            if not self._validate_message(message):
                raise ValueError(f"Invalid push message for user {message.user_id}")
            
            # Send notification via platform
            result = await self._send_via_platform(message.platform, message)
            
            # Calculate delivery time
            delivery_time = (datetime.now() - start_time).total_seconds()
            result.delivery_time = delivery_time
            
            # Track metrics
            await self._track_delivery_metrics(result)
            
            self.logger.info(f"Push notification sent successfully: {result.message_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send push notification: {e}")
            error_result = PushDeliveryResult(
                message_id=f"error_{message.user_id}_{datetime.now().timestamp()}",
                user_id=message.user_id,
                platform=message.platform,
                status="failed",
                error_message=str(e)
            )
            await self._track_delivery_metrics(error_result)
            return error_result

    async def send_batch(self, messages: List[PushMessage]) -> List[PushDeliveryResult]:
        """Send multiple push notifications with rate limiting"""
        if not messages:
            return []
        
        # Group messages by platform for optimal sending
        platform_groups = {}
        for message in messages:
            if message.platform not in platform_groups:
                platform_groups[message.platform] = []
            platform_groups[message.platform].append(message)
        
        # Send each platform group with appropriate rate limiting
        all_results = []
        for platform, platform_messages in platform_groups.items():
            platform_results = await self._send_batch_with_rate_limit(platform, platform_messages)
            all_results.extend(platform_results)
        
        return all_results

    async def _send_batch_with_rate_limit(self, platform: PushPlatform, messages: List[PushMessage]) -> List[PushDeliveryResult]:
        """Send batch of messages with rate limiting"""
        rate_limit = self.rate_limits.get(platform, 100)
        semaphore = asyncio.Semaphore(min(rate_limit, self.max_concurrent_requests))
        
        async def send_single(message -> None: PushMessage) -> None:
            async with semaphore:
                return await self.send_notification(message)
        
        # Send all messages concurrently with rate limiting
        tasks = [send_single(message) for message in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        filtered_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Batch push failed: {str(result)}")
            else:
                filtered_results.append(result)
        
        return filtered_results

    def _validate_message(self, message: PushMessage) -> bool:
        """Validate push message"""
        if not message.user_id or not message.device_token:
            return False
        
        if not message.content.title and not message.content.body:
            return False
        
        # Validate device token format for platform
        return self._validate_device_token(message.device_token, message.platform)

    def _validate_device_token(self, token: str, platform: PushPlatform) -> bool:
        """Validate device token format"""
        if not token:
            return False
        
        # Simplified validation - in production, use platform-specific validation
        if platform in [PushPlatform.FIREBASE_ANDROID, PushPlatform.FIREBASE_IOS, PushPlatform.FIREBASE_WEB]:
            return len(token) > 100  # Firebase tokens are typically long
        elif platform == PushPlatform.APNS_IOS:
            return len(token) == 64  # APNS device tokens are 64 characters
        
        return True

    async def _send_via_platform(self, platform: PushPlatform, message: PushMessage) -> PushDeliveryResult:
        """Send notification via specific platform"""
        
        # Platform-specific sending logic would go here
        # For now, we'll simulate successful delivery
        
        self.logger.info(f"Sending push via {platform.value} to user {message.user_id}")
        
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Create successful result
        result = PushDeliveryResult(
            message_id=f"{platform.value}_{message.user_id}_{datetime.now().timestamp()}",
            user_id=message.user_id,
            platform=platform,
            status="delivered",
            delivered_at=datetime.now()
        )
        
        return result

    async def _track_delivery_metrics(self, result -> None: PushDeliveryResult) -> None:
        """Track push notification delivery metrics"""
        await self.metrics.increment(
            "push_sent_total",
            tags={
                "platform": result.platform.value,
                "status": result.status
            }
        )
        
        if result.delivery_time:
            await self.metrics.histogram(
                "push_delivery_time",
                result.delivery_time,
                tags={"platform": result.platform.value}
            )

# Export the classes
__all__ = [
    'PushNotifier',
    'PushMessage', 
    'PushContent',
    'PushDeliveryResult',
    'PushPlatform',
    'NotificationPriority'
]