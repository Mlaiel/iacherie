"""🚀 Push Notification Service - Enterprise FCM/APNS System
============================================================
Module: platform_core/notifications/push_notification_service.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 PUSH NOTIFICATION SERVICE - FCM/APNS ENTERPRISE
- Firebase Cloud Messaging (Android/Web)
- Apple Push Notification Service (iOS)
- Rich media notifications avec deep linking
- Segmentation intelligente et targeting avancé
- Analytics engagement push temps réel
"""

import asyncio
import logging
import json
import jwt
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import ssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import firebase_admin
from firebase_admin import credentials, messaging
import uuid

logger = logging.getLogger(__name__)


class PushProvider(Enum):
    """Push notification providers."""
    FCM = "fcm"  # Firebase Cloud Messaging
    APNS = "apns"  # Apple Push Notification Service
    WEB_PUSH = "web_push"  # Web Push Protocol
    ONESIGNAL = "onesignal"  # OneSignal
    PUSHER = "pusher"  # Pusher Beams


class DevicePlatform(Enum):
    """Device platforms."""
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    WINDOWS = "windows"
    MACOS = "macos"


class PushPriority(Enum):
    """Push notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class PushStatus(Enum):
    """Push notification status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    CLICKED = "clicked"
    DISMISSED = "dismissed"
    FAILED = "failed"


@dataclass
class PushAction:
    """Push notification action button."""
    id: str
    title: str
    icon: Optional[str] = None
    action_url: Optional[str] = None


@dataclass
class PushPayload:
    """Custom payload data."""
    data: Dict[str, Any] = field(default_factory=dict)
    deep_link: Optional[str] = None
    tracking_id: Optional[str] = None


@dataclass
class PushDevice:
    """Push notification device information."""
    token: str
    platform: DevicePlatform
    app_version: Optional[str] = None
    os_version: Optional[str] = None
    device_model: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    last_active: Optional[datetime] = None
    enabled: bool = True
    
    def __post_init__(self):
        """Validate device token."""
        if not self.token:
            raise ValueError("Device token is required")
        
        # Basic token validation based on platform
        if self.platform == DevicePlatform.IOS and len(self.token) != 64:
            logger.warning(f"Invalid iOS token length: {len(self.token)}")
        elif self.platform == DevicePlatform.ANDROID and len(self.token) < 140:
            logger.warning(f"Potentially invalid Android token length: {len(self.token)}")


@dataclass
class PushRecipient:
    """Push notification recipient."""
    user_id: str
    devices: List[PushDevice]
    personalization_data: Dict[str, Any] = field(default_factory=dict)
    segments: List[str] = field(default_factory=list)
    preferences: Dict[str, bool] = field(default_factory=dict)


@dataclass
class PushTemplate:
    """Push notification template."""
    id: str
    name: str
    title_template: str
    body_template: str
    image_url: Optional[str] = None
    icon_url: Optional[str] = None
    badge_count: Optional[int] = None
    sound: Optional[str] = None
    actions: List[PushAction] = field(default_factory=list)
    category: Optional[str] = None
    thread_id: Optional[str] = None
    collapse_key: Optional[str] = None
    ttl: int = 86400  # Time to live in seconds
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PushRequest:
    """Push notification request."""
    recipients: List[PushRecipient]
    title: str
    body: str
    template_id: Optional[str] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    image_url: Optional[str] = None
    icon_url: Optional[str] = None
    badge_count: Optional[int] = None
    sound: Optional[str] = None
    actions: List[PushAction] = field(default_factory=list)
    payload: Optional[PushPayload] = None
    priority: PushPriority = PushPriority.NORMAL
    send_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    thread_id: Optional[str] = None
    collapse_key: Optional[str] = None
    ttl: int = 86400
    mutable_content: bool = False
    content_available: bool = False


@dataclass
class PushResult:
    """Push notification result."""
    message_id: str
    status: PushStatus
    provider: PushProvider
    sent_at: datetime
    devices_targeted: int
    devices_successful: int
    devices_failed: int
    error_messages: List[str] = field(default_factory=list)
    provider_response: Optional[Dict[str, Any]] = None
    tracking_id: Optional[str] = None


class PushProviderInterface:
    """Interface for push notification providers."""
    
    async def send_push(self, request: PushRequest) -> PushResult:
        """Send push notification."""
        raise NotImplementedError
    
    async def get_delivery_status(self, message_id: str) -> PushStatus:
        """Get delivery status."""
        raise NotImplementedError
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> None:
        """Handle provider webhook."""
        raise NotImplementedError
    
    async def validate_token(self, token: str, platform: DevicePlatform) -> bool:
        """Validate device token."""
        raise NotImplementedError


class FCMProvider(PushProviderInterface):
    """Firebase Cloud Messaging provider."""
    
    def __init__(self, config: Dict[str, Any]):
        self.project_id = config.get('project_id')
        self.service_account_path = config.get('service_account_path')
        self.service_account_info = config.get('service_account_info')
        
        # Initialize Firebase Admin SDK
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        try:
            if self.service_account_path:
                cred = credentials.Certificate(self.service_account_path)
            elif self.service_account_info:
                cred = credentials.Certificate(self.service_account_info)
            else:
                raise ValueError("Firebase credentials not provided")
            
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            
            logger.info("Firebase Admin SDK initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    async def send_push(self, request: PushRequest) -> PushResult:
        """Send push notification via FCM."""
        try:
            successful_sends = 0
            failed_sends = 0
            error_messages = []
            
            # Collect all Android and Web tokens
            tokens = []
            for recipient in request.recipients:
                for device in recipient.devices:
                    if device.platform in [DevicePlatform.ANDROID, DevicePlatform.WEB] and device.enabled:
                        tokens.append(device.token)
            
            if not tokens:
                return PushResult(
                    message_id="",
                    status=PushStatus.FAILED,
                    provider=PushProvider.FCM,
                    sent_at=datetime.utcnow(),
                    devices_targeted=0,
                    devices_successful=0,
                    devices_failed=0,
                    error_messages=["No valid FCM tokens found"]
                )
            
            # Create FCM message
            notification = messaging.Notification(
                title=request.title,
                body=request.body,
                image=request.image_url
            )
            
            # Create Android config
            android_config = messaging.AndroidConfig(
                priority='high' if request.priority == PushPriority.HIGH else 'normal',
                notification=messaging.AndroidNotification(
                    icon=request.icon_url,
                    sound=request.sound or 'default',
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                    channel_id='default'
                ),
                data=request.payload.data if request.payload else {}
            )
            
            # Create web config
            web_config = messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title=request.title,
                    body=request.body,
                    icon=request.icon_url,
                    image=request.image_url,
                    badge=request.badge_count,
                    actions=[
                        messaging.WebpushNotificationAction(
                            action=action.id,
                            title=action.title,
                            icon=action.icon
                        ) for action in request.actions
                    ] if request.actions else None
                ),
                data=request.payload.data if request.payload else {}
            )
            
            # Create multicast message
            message = messaging.MulticastMessage(
                tokens=tokens,
                notification=notification,
                android=android_config,
                webpush=web_config,
                data=request.payload.data if request.payload else {}
            )
            
            # Send message
            response = messaging.send_multicast(message)
            
            successful_sends = response.success_count
            failed_sends = response.failure_count
            
            # Process individual responses
            for i, resp in enumerate(response.responses):
                if not resp.success:
                    error_messages.append(f"Token {i}: {resp.exception}")
            
            return PushResult(
                message_id=str(uuid.uuid4()),
                status=PushStatus.SENT if successful_sends > 0 else PushStatus.FAILED,
                provider=PushProvider.FCM,
                sent_at=datetime.utcnow(),
                devices_targeted=len(tokens),
                devices_successful=successful_sends,
                devices_failed=failed_sends,
                error_messages=error_messages,
                provider_response={
                    'success_count': successful_sends,
                    'failure_count': failed_sends,
                    'responses': [{'success': r.success, 'message_id': r.message_id if r.success else None} for r in response.responses]
                }
            )
            
        except Exception as e:
            logger.error(f"FCM push notification failed: {e}")
            return PushResult(
                message_id="",
                status=PushStatus.FAILED,
                provider=PushProvider.FCM,
                sent_at=datetime.utcnow(),
                devices_targeted=len(tokens) if 'tokens' in locals() else 0,
                devices_successful=0,
                devices_failed=len(tokens) if 'tokens' in locals() else 0,
                error_messages=[str(e)]
            )
    
    async def get_delivery_status(self, message_id: str) -> PushStatus:
        """Get FCM delivery status."""
        try:
            # FCM doesn't provide direct delivery status API
            # Would need to implement using Firebase Analytics or custom tracking
            return PushStatus.SENT
        except Exception as e:
            logger.error(f"Failed to get FCM delivery status: {e}")
            return PushStatus.FAILED
    
    async def validate_token(self, token: str, platform: DevicePlatform) -> bool:
        """Validate FCM token."""
        try:
            # Try to send a test message to validate token
            test_message = messaging.Message(
                token=token,
                data={'test': 'validation'},
                dry_run=True  # Don't actually send
            )
            
            messaging.send(test_message)
            return True
            
        except Exception as e:
            logger.warning(f"FCM token validation failed: {e}")
            return False
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> None:
        """Handle FCM webhook events."""
        try:
            # FCM doesn't have traditional webhooks
            # Analytics events would come through Firebase Analytics
            logger.info(f"FCM webhook received: {payload}")
        except Exception as e:
            logger.error(f"FCM webhook error: {e}")


class APNSProvider(PushProviderInterface):
    """Apple Push Notification Service provider."""
    
    def __init__(self, config: Dict[str, Any]):
        self.team_id = config.get('team_id')
        self.key_id = config.get('key_id')
        self.private_key_path = config.get('private_key_path')
        self.private_key_content = config.get('private_key_content')
        self.bundle_id = config.get('bundle_id')
        self.sandbox = config.get('sandbox', False)
        
        # APNS URLs
        self.apns_url = "https://api.sandbox.push.apple.com" if self.sandbox else "https://api.push.apple.com"
        
        # Load private key
        self._load_private_key()
    
    def _load_private_key(self):
        """Load APNS private key."""
        try:
            if self.private_key_path:
                with open(self.private_key_path, 'rb') as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
            elif self.private_key_content:
                self.private_key = serialization.load_pem_private_key(
                    self.private_key_content.encode(),
                    password=None
                )
            else:
                raise ValueError("APNS private key not provided")
                
            logger.info("APNS private key loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load APNS private key: {e}")
            raise
    
    def _generate_jwt_token(self) -> str:
        """Generate JWT token for APNS authentication."""
        try:
            headers = {
                'alg': 'ES256',
                'kid': self.key_id
            }
            
            payload = {
                'iss': self.team_id,
                'iat': int(time.time())
            }
            
            token = jwt.encode(payload, self.private_key, algorithm='ES256', headers=headers)
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate APNS JWT token: {e}")
            raise
    
    async def send_push(self, request: PushRequest) -> PushResult:
        """Send push notification via APNS."""
        try:
            successful_sends = 0
            failed_sends = 0
            error_messages = []
            
            # Collect all iOS tokens
            ios_tokens = []
            for recipient in request.recipients:
                for device in recipient.devices:
                    if device.platform == DevicePlatform.IOS and device.enabled:
                        ios_tokens.append(device.token)
            
            if not ios_tokens:
                return PushResult(
                    message_id="",
                    status=PushStatus.FAILED,
                    provider=PushProvider.APNS,
                    sent_at=datetime.utcnow(),
                    devices_targeted=0,
                    devices_successful=0,
                    devices_failed=0,
                    error_messages=["No valid iOS tokens found"]
                )
            
            # Generate JWT token
            jwt_token = self._generate_jwt_token()
            
            # Create APNS payload
            aps_payload = {
                'alert': {
                    'title': request.title,
                    'body': request.body
                },
                'sound': request.sound or 'default',
                'badge': request.badge_count
            }
            
            if request.mutable_content:
                aps_payload['mutable-content'] = 1
            
            if request.content_available:
                aps_payload['content-available'] = 1
            
            if request.thread_id:
                aps_payload['thread-id'] = request.thread_id
            
            if request.category:
                aps_payload['category'] = request.category
            
            # Complete payload
            payload = {
                'aps': aps_payload
            }
            
            # Add custom data
            if request.payload and request.payload.data:
                payload.update(request.payload.data)
            
            # Headers for APNS request
            headers = {
                'authorization': f'bearer {jwt_token}',
                'apns-topic': self.bundle_id,
                'apns-push-type': 'alert',
                'apns-priority': '10' if request.priority == PushPriority.HIGH else '5',
                'apns-expiration': str(int(time.time()) + request.ttl)
            }
            
            if request.collapse_key:
                headers['apns-collapse-id'] = request.collapse_key
            
            # Send to each token
            async with aiohttp.ClientSession() as session:
                for token in ios_tokens:
                    try:
                        async with session.post(
                            f"{self.apns_url}/3/device/{token}",
                            json=payload,
                            headers=headers
                        ) as response:
                            if response.status == 200:
                                successful_sends += 1
                            else:
                                failed_sends += 1
                                error_text = await response.text()
                                error_messages.append(f"Token {token}: {error_text}")
                                
                    except Exception as e:
                        failed_sends += 1
                        error_messages.append(f"Token {token}: {str(e)}")
            
            return PushResult(
                message_id=str(uuid.uuid4()),
                status=PushStatus.SENT if successful_sends > 0 else PushStatus.FAILED,
                provider=PushProvider.APNS,
                sent_at=datetime.utcnow(),
                devices_targeted=len(ios_tokens),
                devices_successful=successful_sends,
                devices_failed=failed_sends,
                error_messages=error_messages
            )
            
        except Exception as e:
            logger.error(f"APNS push notification failed: {e}")
            return PushResult(
                message_id="",
                status=PushStatus.FAILED,
                provider=PushProvider.APNS,
                sent_at=datetime.utcnow(),
                devices_targeted=len(ios_tokens) if 'ios_tokens' in locals() else 0,
                devices_successful=0,
                devices_failed=len(ios_tokens) if 'ios_tokens' in locals() else 0,
                error_messages=[str(e)]
            )
    
    async def get_delivery_status(self, message_id: str) -> PushStatus:
        """Get APNS delivery status."""
        try:
            # APNS doesn't provide delivery status feedback
            # Would need to implement custom tracking
            return PushStatus.SENT
        except Exception as e:
            logger.error(f"Failed to get APNS delivery status: {e}")
            return PushStatus.FAILED
    
    async def validate_token(self, token: str, platform: DevicePlatform) -> bool:
        """Validate APNS token."""
        try:
            # Basic token format validation
            if platform == DevicePlatform.IOS:
                # iOS tokens should be 64 hex characters
                if len(token) == 64 and all(c in '0123456789abcdefABCDEF' for c in token):
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"APNS token validation failed: {e}")
            return False
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> None:
        """Handle APNS webhook events."""
        try:
            # APNS doesn't have webhooks
            # Feedback would come through feedback service (deprecated)
            logger.info(f"APNS webhook received: {payload}")
        except Exception as e:
            logger.error(f"APNS webhook error: {e}")


class OneSignalProvider(PushProviderInterface):
    """OneSignal push notification provider."""
    
    def __init__(self, config: Dict[str, Any]):
        self.app_id = config.get('app_id')
        self.api_key = config.get('api_key')
        self.base_url = "https://onesignal.com/api/v1"
    
    async def send_push(self, request: PushRequest) -> PushResult:
        """Send push notification via OneSignal."""
        try:
            # Collect device tokens by platform
            include_player_ids = []
            for recipient in request.recipients:
                for device in recipient.devices:
                    if device.enabled:
                        include_player_ids.append(device.token)
            
            if not include_player_ids:
                return PushResult(
                    message_id="",
                    status=PushStatus.FAILED,
                    provider=PushProvider.ONESIGNAL,
                    sent_at=datetime.utcnow(),
                    devices_targeted=0,
                    devices_successful=0,
                    devices_failed=0,
                    error_messages=["No valid OneSignal player IDs found"]
                )
            
            # Create OneSignal notification
            notification_data = {
                'app_id': self.app_id,
                'include_player_ids': include_player_ids,
                'headings': {'en': request.title},
                'contents': {'en': request.body},
                'data': request.payload.data if request.payload else {},
                'priority': 10 if request.priority == PushPriority.HIGH else 5
            }
            
            if request.image_url:
                notification_data['big_picture'] = request.image_url
                notification_data['large_icon'] = request.icon_url or request.image_url
            
            if request.actions:
                notification_data['buttons'] = [
                    {
                        'id': action.id,
                        'text': action.title,
                        'icon': action.icon,
                        'url': action.action_url
                    } for action in request.actions
                ]
            
            if request.send_at:
                notification_data['send_after'] = request.send_at.isoformat()
            
            # Send notification
            headers = {
                'Authorization': f'Basic {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/notifications",
                    json=notification_data,
                    headers=headers
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        return PushResult(
                            message_id=result.get('id', ''),
                            status=PushStatus.SENT,
                            provider=PushProvider.ONESIGNAL,
                            sent_at=datetime.utcnow(),
                            devices_targeted=len(include_player_ids),
                            devices_successful=result.get('recipients', 0),
                            devices_failed=len(include_player_ids) - result.get('recipients', 0),
                            provider_response=result
                        )
                    else:
                        raise Exception(f"OneSignal API error: {result}")
                        
        except Exception as e:
            logger.error(f"OneSignal push notification failed: {e}")
            return PushResult(
                message_id="",
                status=PushStatus.FAILED,
                provider=PushProvider.ONESIGNAL,
                sent_at=datetime.utcnow(),
                devices_targeted=len(include_player_ids) if 'include_player_ids' in locals() else 0,
                devices_successful=0,
                devices_failed=len(include_player_ids) if 'include_player_ids' in locals() else 0,
                error_messages=[str(e)]
            )
    
    async def get_delivery_status(self, message_id: str) -> PushStatus:
        """Get OneSignal delivery status."""
        try:
            headers = {'Authorization': f'Basic {self.api_key}'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/notifications/{message_id}",
                    headers=headers
                ) as response:
                    result = await response.json()
                    
                    if result.get('successful') and result.get('successful') > 0:
                        return PushStatus.DELIVERED
                    elif result.get('failed') and result.get('failed') > 0:
                        return PushStatus.FAILED
                    else:
                        return PushStatus.SENT
                        
        except Exception as e:
            logger.error(f"Failed to get OneSignal delivery status: {e}")
            return PushStatus.FAILED
    
    async def validate_token(self, token: str, platform: DevicePlatform) -> bool:
        """Validate OneSignal player ID."""
        try:
            # OneSignal player IDs are UUIDs
            if len(token) == 36 and token.count('-') == 4:
                return True
            return False
        except Exception as e:
            logger.warning(f"OneSignal token validation failed: {e}")
            return False
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> None:
        """Handle OneSignal webhook events."""
        try:
            event_type = payload.get('type')
            notification_id = payload.get('notification_id')
            
            if event_type == 'click':
                logger.info(f"OneSignal notification {notification_id} clicked")
            elif event_type == 'delivered':
                logger.info(f"OneSignal notification {notification_id} delivered")
                
        except Exception as e:
            logger.error(f"OneSignal webhook error: {e}")


class PushNotificationService:
    """Enterprise push notification service with multi-provider support."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[PushProvider, PushProviderInterface] = {}
        self.analytics_data: Dict[str, Any] = {}
        self.device_registry: Dict[str, List[PushDevice]] = {}
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize push notification providers."""
        try:
            # Initialize FCM
            if 'fcm' in self.config:
                self.providers[PushProvider.FCM] = FCMProvider(self.config['fcm'])
            
            # Initialize APNS
            if 'apns' in self.config:
                self.providers[PushProvider.APNS] = APNSProvider(self.config['apns'])
            
            # Initialize OneSignal
            if 'onesignal' in self.config:
                self.providers[PushProvider.ONESIGNAL] = OneSignalProvider(self.config['onesignal'])
                
            logger.info(f"Initialized {len(self.providers)} push notification providers")
            
        except Exception as e:
            logger.error(f"Failed to initialize push providers: {e}")
    
    async def send_push_notification(self, request: PushRequest) -> Dict[PushProvider, PushResult]:
        """Send push notification across all relevant providers."""
        results = {}
        
        try:
            # Group recipients by platform
            platform_recipients = {platform: [] for platform in DevicePlatform}
            
            for recipient in request.recipients:
                for device in recipient.devices:
                    if device.enabled:
                        platform_recipients[device.platform].append(
                            PushRecipient(
                                user_id=recipient.user_id,
                                devices=[device],
                                personalization_data=recipient.personalization_data,
                                segments=recipient.segments,
                                preferences=recipient.preferences
                            )
                        )
            
            # Send via FCM for Android and Web
            if (platform_recipients[DevicePlatform.ANDROID] or platform_recipients[DevicePlatform.WEB]) and PushProvider.FCM in self.providers:
                fcm_recipients = platform_recipients[DevicePlatform.ANDROID] + platform_recipients[DevicePlatform.WEB]
                if fcm_recipients:
                    fcm_request = PushRequest(
                        recipients=fcm_recipients,
                        **{k: v for k, v in request.__dict__.items() if k != 'recipients'}
                    )
                    results[PushProvider.FCM] = await self.providers[PushProvider.FCM].send_push(fcm_request)
            
            # Send via APNS for iOS
            if platform_recipients[DevicePlatform.IOS] and PushProvider.APNS in self.providers:
                apns_request = PushRequest(
                    recipients=platform_recipients[DevicePlatform.IOS],
                    **{k: v for k, v in request.__dict__.items() if k != 'recipients'}
                )
                results[PushProvider.APNS] = await self.providers[PushProvider.APNS].send_push(apns_request)
            
            # Send via OneSignal for all platforms if configured
            if PushProvider.ONESIGNAL in self.providers:
                all_recipients = [r for recipients in platform_recipients.values() for r in recipients]
                if all_recipients:
                    onesignal_request = PushRequest(
                        recipients=all_recipients,
                        **{k: v for k, v in request.__dict__.items() if k != 'recipients'}
                    )
                    results[PushProvider.ONESIGNAL] = await self.providers[PushProvider.ONESIGNAL].send_push(onesignal_request)
            
            # Track analytics
            await self._track_push_sent(request, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Push notification sending failed: {e}")
            return {}
    
    async def send_template_push(self, template_id: str, recipients: List[PushRecipient], 
                               template_data: Dict[str, Any]) -> Dict[PushProvider, PushResult]:
        """Send push notification using template."""
        try:
            # Load template
            template = await self._load_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Render template
            title = template.title_template
            body = template.body_template
            
            # Simple template rendering
            for key, value in template_data.items():
                title = title.replace(f"{{{{{key}}}}}", str(value))
                body = body.replace(f"{{{{{key}}}}}", str(value))
            
            # Create push request
            request = PushRequest(
                recipients=recipients,
                title=title,
                body=body,
                template_id=template_id,
                template_data=template_data,
                image_url=template.image_url,
                icon_url=template.icon_url,
                badge_count=template.badge_count,
                sound=template.sound,
                actions=template.actions,
                category=template.category,
                thread_id=template.thread_id,
                collapse_key=template.collapse_key,
                ttl=template.ttl
            )
            
            return await self.send_push_notification(request)
            
        except Exception as e:
            logger.error(f"Template push notification failed: {e}")
            return {}
    
    async def register_device(self, user_id: str, device: PushDevice) -> bool:
        """Register device for push notifications."""
        try:
            # Validate device token
            for provider in self.providers.values():
                if await provider.validate_token(device.token, device.platform):
                    break
            else:
                logger.warning(f"Invalid device token: {device.token}")
                return False
            
            # Add device to registry
            if user_id not in self.device_registry:
                self.device_registry[user_id] = []
            
            # Remove existing device with same token
            self.device_registry[user_id] = [
                d for d in self.device_registry[user_id] 
                if d.token != device.token
            ]
            
            # Add new device
            self.device_registry[user_id].append(device)
            
            logger.info(f"Device registered for user {user_id}: {device.platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register device: {e}")
            return False
    
    async def unregister_device(self, user_id: str, token: str) -> bool:
        """Unregister device from push notifications."""
        try:
            if user_id in self.device_registry:
                original_count = len(self.device_registry[user_id])
                self.device_registry[user_id] = [
                    d for d in self.device_registry[user_id] 
                    if d.token != token
                ]
                
                if len(self.device_registry[user_id]) < original_count:
                    logger.info(f"Device unregistered for user {user_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister device: {e}")
            return False
    
    async def get_user_devices(self, user_id: str) -> List[PushDevice]:
        """Get all devices for a user."""
        return self.device_registry.get(user_id, [])
    
    async def _load_template(self, template_id: str) -> Optional[PushTemplate]:
        """Load push notification template."""
        try:
            # Implementation would load from database
            # For now, return a sample template
            return PushTemplate(
                id=template_id,
                name=f"Template {template_id}",
                title_template="Welcome {{user_name}}!",
                body_template="Thank you for joining {{platform_name}}. Start creating amazing content!",
                image_url="https://example.com/welcome.jpg",
                icon_url="https://example.com/icon.png",
                sound="default",
                actions=[
                    PushAction(
                        id="get_started",
                        title="Get Started",
                        action_url="iacherie://onboarding"
                    )
                ],
                category="welcome"
            )
            
        except Exception as e:
            logger.error(f"Failed to load template {template_id}: {e}")
            return None
    
    async def _track_push_sent(self, request: PushRequest, results: Dict[PushProvider, PushResult]) -> None:
        """Track push notification analytics."""
        try:
            analytics_key = f"push_analytics_{datetime.utcnow().strftime('%Y-%m-%d')}"
            
            if analytics_key not in self.analytics_data:
                self.analytics_data[analytics_key] = {
                    'total_sent': 0,
                    'total_delivered': 0,
                    'by_provider': {},
                    'by_platform': {},
                    'by_category': {}
                }
            
            analytics = self.analytics_data[analytics_key]
            
            for provider, result in results.items():
                analytics['total_sent'] += result.devices_successful
                
                # Track by provider
                provider_key = provider.value
                if provider_key not in analytics['by_provider']:
                    analytics['by_provider'][provider_key] = {'sent': 0, 'failed': 0}
                
                analytics['by_provider'][provider_key]['sent'] += result.devices_successful
                analytics['by_provider'][provider_key]['failed'] += result.devices_failed
            
            # Track by category
            if request.category:
                analytics['by_category'][request.category] = analytics['by_category'].get(request.category, 0) + 1
            
            logger.info(f"Push analytics updated: {analytics}")
            
        except Exception as e:
            logger.error(f"Failed to track push analytics: {e}")
    
    async def get_analytics(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get push notification analytics."""
        try:
            if not date:
                date = datetime.utcnow()
            
            analytics_key = f"push_analytics_{date.strftime('%Y-%m-%d')}"
            return self.analytics_data.get(analytics_key, {})
            
        except Exception as e:
            logger.error(f"Failed to get push analytics: {e}")
            return {}
    
    async def segment_users(self, criteria: Dict[str, Any]) -> List[str]:
        """Segment users based on criteria."""
        try:
            # Implementation would query user database
            # For now, return sample user IDs
            return ["user_1", "user_2", "user_3"]
            
        except Exception as e:
            logger.error(f"User segmentation failed: {e}")
            return []
    
    async def optimize_send_time(self, user_id: str) -> datetime:
        """Optimize push notification send time for user."""
        try:
            # Implementation would use ML to predict optimal send time
            # Based on user's historical engagement patterns
            
            # For now, return intelligent defaults
            current_time = datetime.utcnow()
            
            # Send during active hours (10 AM - 8 PM)
            optimal_hour = 18  # 6 PM
            optimal_time = current_time.replace(
                hour=optimal_hour,
                minute=0,
                second=0,
                microsecond=0
            )
            
            # If it's past optimal time today, schedule for tomorrow
            if current_time.hour >= optimal_hour:
                optimal_time += timedelta(days=1)
            
            return optimal_time
            
        except Exception as e:
            logger.error(f"Failed to optimize send time: {e}")
            return datetime.utcnow()


# Factory function for creating service instance
def create_push_service(config: Dict[str, Any]) -> PushNotificationService:
    """Create and configure push notification service."""
    return PushNotificationService(config)


# Export main classes and functions
__all__ = [
    'PushNotificationService',
    'PushProvider',
    'DevicePlatform',
    'PushPriority',
    'PushStatus',
    'PushAction',
    'PushPayload',
    'PushDevice',
    'PushRecipient',
    'PushTemplate',
    'PushRequest',
    'PushResult',
    'create_push_service'
]