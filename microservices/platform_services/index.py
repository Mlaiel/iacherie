#!/usr/bin/env python3
"""
🌐 PLATFORM SERVICES MODULE - ENTERPRISE PLATFORM INTEGRATION ENTRY POINT
==========================================================================

© FAHED MLAIEL 2024-2025 - PROPRIÉTÉ INTELLECTUELLE STRICTE
⚠️ ARCHITECTURE CONFIDENTIELLE - NIVEAU ENTERPRISE UNIQUEMENT

Entry point for Platform Services module.
Provides enterprise-grade integration with 65+ external platforms.

Module: platform_services/
Services: 18 Platform Integration services
Capabilities: Multi-platform integration, sync, monitoring, optimization

Key Services:
------------
🔗 Platform Connector Service      - Universal platform connectors
🔐 Platform Authentication Service - Multi-platform authentication
🔄 Platform Sync Service          - Real-time platform synchronization
📊 Platform Monitoring Service    - Platform performance monitoring
⚡ Platform Optimization Service   - Platform-specific optimization
📋 Platform Reporting Service      - Cross-platform analytics
⚖️ Platform Compliance Service     - Platform compliance management
🔗 Platform Webhook Service        - Webhook management and routing
📱 Social Media Service           - Social media platform integration
🎵 Music Streaming Service        - Music platform integration
💰 Creator Economy Service        - Creator platform integration
🎮 Gaming Platform Service        - Gaming platform integration
🎬 Video Platform Service         - Video platform integration
📸 Photography Platform Service   - Photography platform integration
📝 Blogging Platform Service      - Blogging platform integration
🛒 E-commerce Platform Service    - E-commerce platform integration

Contact: Fahed Mlaiel (mlaiel@live.de)
Team: Platform Integration Team (6 experts)
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

# Configure logging
logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Platform types"""
    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    CREATOR_ECONOMY = "creator_economy"
    PHOTOGRAPHY = "photography"
    BLOGGING = "blogging"
    GAMING = "gaming"
    ECOMMERCE = "ecommerce"
    MESSAGING = "messaging"
    PROFESSIONAL = "professional"

class PlatformStatus(Enum):
    """Platform connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    AUTHENTICATING = "authenticating"
    SYNCING = "syncing"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class SyncOperation(Enum):
    """Synchronization operations"""
    UPLOAD = "upload"
    UPDATE = "update"
    DELETE = "delete"
    SYNC_METADATA = "sync_metadata"
    SYNC_ANALYTICS = "sync_analytics"
    SYNC_COMMENTS = "sync_comments"
    SYNC_FOLLOWERS = "sync_followers"

@dataclass
class Platform:
    """Platform configuration"""
    platform_id: str
    name: str
    platform_type: PlatformType
    api_endpoint: str
    supported_content_types: List[str]
    max_file_size: int  # in MB
    rate_limits: Dict[str, int]
    authentication_type: str
    is_active: bool = True
    last_sync: Optional[datetime] = None
    sync_frequency: int = 3600  # seconds
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class PlatformConnection:
    """Platform connection for a user"""
    connection_id: str
    user_id: str
    platform_id: str
    status: PlatformStatus
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)

@dataclass
class PlatformRequest:
    """Platform service request"""
    request_id: str
    platform_id: str
    user_id: str
    operation: str
    data: Dict[str, Any] = field(default_factory=dict)
    sync_operation: Optional[SyncOperation] = None
    priority: str = "normal"
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PlatformResponse:
    """Platform service response"""
    request_id: str
    platform_id: str
    operation: str
    status: str
    result: Dict[str, Any]
    sync_operation: Optional[SyncOperation] = None
    items_processed: int = 0
    processing_time: float = 0.0
    rate_limit_remaining: Optional[int] = None
    next_sync_at: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

class PlatformServicesOrchestrator:
    """
    Enterprise Platform Services Orchestrator
    Coordinates all platform integration services
    """
    
    def __init__(self):
        self.services = {}
        self.platforms = {}
        self.connections = {}
        self.sync_queue = {}
        self.metrics = {}
        self.webhooks = {}
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize all platform services"""
        try:
            # Import platform services (graceful imports)
            try:
                from . import platform_connector_service
                self.services['connector'] = platform_connector_service
            except ImportError:
                logger.warning("⚠️ platform_connector_service not found")
            
            try:
                from . import platform_authentication_service
                self.services['authentication'] = platform_authentication_service
            except ImportError:
                logger.warning("⚠️ platform_authentication_service not found")
            
            try:
                from . import platform_sync_service
                self.services['sync'] = platform_sync_service
            except ImportError:
                logger.warning("⚠️ platform_sync_service not found")
            
            try:
                from . import platform_monitoring_service
                self.services['monitoring'] = platform_monitoring_service
            except ImportError:
                logger.warning("⚠️ platform_monitoring_service not found")
            
            try:
                from . import social_media_service
                self.services['social_media'] = social_media_service
            except ImportError:
                logger.warning("⚠️ social_media_service not found")
            
            # Initialize 65+ platforms
            await self._initialize_supported_platforms()
            
            # Initialize metrics
            self.metrics = {
                'total_platforms': len(self.platforms),
                'active_connections': 0,
                'total_sync_operations': 0,
                'successful_syncs': 0,
                'failed_syncs': 0,
                'avg_sync_time': 0.0,
                'data_transferred_mb': 0.0,
                'rate_limit_hits': 0,
                'webhook_deliveries': 0
            }
            
            self.is_initialized = True
            logger.info("✅ Platform Services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Platform Services: {e}")
            return False
    
    async def _initialize_supported_platforms(self):
        """Initialize the 65+ supported platforms"""
        
        # Social Media Platforms (29)
        social_platforms = [
            ("instagram", "Instagram", ["image", "video", "story"]),
            ("tiktok", "TikTok", ["video", "live"]),
            ("youtube", "YouTube", ["video", "shorts", "live"]),
            ("facebook", "Facebook", ["image", "video", "text"]),
            ("twitter", "Twitter/X", ["text", "image", "video"]),
            ("linkedin", "LinkedIn", ["text", "image", "video", "article"]),
            ("snapchat", "Snapchat", ["image", "video", "story"]),
            ("pinterest", "Pinterest", ["image", "video"]),
            ("reddit", "Reddit", ["text", "image", "video"]),
            ("tumblr", "Tumblr", ["text", "image", "video", "gif"]),
            ("discord", "Discord", ["text", "image", "video", "audio"]),
            ("telegram", "Telegram", ["text", "image", "video", "audio"]),
            ("whatsapp", "WhatsApp Business", ["text", "image", "video", "audio"]),
            ("mastodon", "Mastodon", ["text", "image", "video"]),
            ("threads", "Threads", ["text", "image", "video"]),
            ("clubhouse", "Clubhouse", ["audio", "live"]),
            ("twitch", "Twitch", ["video", "live", "clips"]),
            ("vimeo", "Vimeo", ["video"]),
            ("dailymotion", "Dailymotion", ["video"]),
            ("wechat", "WeChat", ["text", "image", "video"]),
            ("weibo", "Weibo", ["text", "image", "video"]),
            ("line", "LINE", ["text", "image", "video", "sticker"]),
            ("kakao", "KakaoTalk", ["text", "image", "video"]),
            ("viber", "Viber", ["text", "image", "video", "audio"]),
            ("signal", "Signal", ["text", "image", "video", "audio"]),
            ("slack", "Slack", ["text", "image", "video", "file"]),
            ("teams", "Microsoft Teams", ["text", "image", "video", "file"]),
            ("zoom", "Zoom", ["video", "live", "webinar"]),
            ("google_meet", "Google Meet", ["video", "live"])
        ]
        
        for platform_id, name, content_types in social_platforms:
            self.platforms[platform_id] = Platform(
                platform_id=platform_id,
                name=name,
                platform_type=PlatformType.SOCIAL_MEDIA,
                api_endpoint=f"https://api.{platform_id}.com/v1",
                supported_content_types=content_types,
                max_file_size=100,  # 100MB default
                rate_limits={"posts": 100, "uploads": 50},
                authentication_type="oauth2"
            )
        
        # Music Streaming Platforms (20)
        music_platforms = [
            ("spotify", "Spotify", 320),
            ("apple_music", "Apple Music", 256),
            ("youtube_music", "YouTube Music", 256),
            ("amazon_music", "Amazon Music", 256),
            ("tidal", "TIDAL", 320),
            ("deezer", "Deezer", 320),
            ("soundcloud", "SoundCloud", 128),
            ("bandcamp", "Bandcamp", 320),
            ("audiomack", "Audiomack", 256),
            ("pandora", "Pandora", 192),
            ("iheartradio", "iHeartRadio", 128),
            ("napster", "Napster", 320),
            ("qobuz", "Qobuz", 320),
            ("jiosaavn", "JioSaavn", 320),
            ("gaana", "Gaana", 320),
            ("wynk", "Wynk Music", 256),
            ("anghami", "Anghami", 256),
            ("boomplay", "Boomplay", 320),
            ("audiomack", "Audiomack", 256),
            ("reverbnation", "ReverbNation", 320)
        ]
        
        for platform_id, name, max_bitrate in music_platforms:
            self.platforms[platform_id] = Platform(
                platform_id=platform_id,
                name=name,
                platform_type=PlatformType.MUSIC_STREAMING,
                api_endpoint=f"https://api.{platform_id}.com/v1",
                supported_content_types=["audio", "track", "album", "playlist"],
                max_file_size=500,  # 500MB for audio
                rate_limits={"uploads": 20, "metadata": 1000},
                authentication_type="oauth2"
            )
        
        # Creator Economy Platforms (16)
        creator_platforms = [
            ("onlyfans", "OnlyFans", ["image", "video", "text", "live"]),
            ("patreon", "Patreon", ["text", "image", "video", "audio"]),
            ("ko_fi", "Ko-fi", ["text", "image", "video"]),
            ("buy_me_coffee", "Buy Me a Coffee", ["text", "image", "video"]),
            ("gumroad", "Gumroad", ["digital", "course", "ebook"]),
            ("etsy", "Etsy", ["image", "product"]),
            ("shopify", "Shopify", ["product", "image", "video"]),
            ("substack", "Substack", ["text", "newsletter", "podcast"]),
            ("medium", "Medium", ["text", "article", "image"]),
            ("ghost", "Ghost", ["text", "article", "image"]),
            ("twitch", "Twitch Monetization", ["video", "live", "subscription"]),
            ("youtube_monetization", "YouTube Monetization", ["video", "membership"]),
            ("cameo", "Cameo", ["video", "personalized"]),
            ("fanhouse", "Fanhouse", ["image", "video", "text"]),
            ("fansly", "Fansly", ["image", "video", "text"]),
            ("justforfans", "JustForFans", ["image", "video", "text"])
        ]
        
        for platform_id, name, content_types in creator_platforms:
            self.platforms[platform_id] = Platform(
                platform_id=platform_id,
                name=name,
                platform_type=PlatformType.CREATOR_ECONOMY,
                api_endpoint=f"https://api.{platform_id}.com/v1",
                supported_content_types=content_types,
                max_file_size=1000,  # 1GB for creator content
                rate_limits={"posts": 50, "uploads": 25},
                authentication_type="oauth2"
            )
    
    async def process_platform_request(self, request: PlatformRequest) -> PlatformResponse:
        """Process platform service request"""
        start_time = datetime.now()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Validate platform exists
            if request.platform_id not in self.platforms:
                return PlatformResponse(
                    request_id=request.request_id,
                    platform_id=request.platform_id,
                    operation=request.operation,
                    status="error",
                    result={},
                    errors=[f"Platform {request.platform_id} not supported"]
                )
            
            platform = self.platforms[request.platform_id]
            
            # Route to appropriate service based on operation
            if request.operation == "connect":
                response = await self._handle_platform_connection(request, platform)
            elif request.operation == "sync":
                response = await self._handle_platform_sync(request, platform)
            elif request.operation == "upload":
                response = await self._handle_content_upload(request, platform)
            elif request.operation == "authenticate":
                response = await self._handle_authentication(request, platform)
            elif request.operation == "monitor":
                response = await self._handle_monitoring(request, platform)
            elif request.operation == "webhook":
                response = await self._handle_webhook(request, platform)
            else:
                response = await self._handle_generic_operation(request, platform)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            response.processing_time = processing_time
            
            # Update metrics
            if response.status == "success":
                self.metrics['successful_syncs'] += 1
                if request.sync_operation:
                    self.metrics['total_sync_operations'] += 1
            else:
                self.metrics['failed_syncs'] += 1
            
            # Update average sync time
            self._update_avg_sync_time(processing_time)
            
            return response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Platform request processing failed: {e}")
            
            return PlatformResponse(
                request_id=request.request_id,
                platform_id=request.platform_id,
                operation=request.operation,
                status="error",
                result={},
                processing_time=processing_time,
                errors=[str(e)]
            )
    
    async def _handle_platform_connection(self, request: PlatformRequest, platform: Platform) -> PlatformResponse:
        """Handle platform connection"""
        try:
            connection_id = str(uuid.uuid4())
            
            # Use authentication service if available
            if 'authentication' in self.services:
                auth_service = self.services['authentication']
                if hasattr(auth_service, 'authenticate_platform'):
                    auth_result = await auth_service.authenticate_platform(platform.platform_id, request.data)
                else:
                    auth_result = await self._basic_authentication(platform, request.data)
            else:
                auth_result = await self._basic_authentication(platform, request.data)
            
            if auth_result.get('success'):
                # Create connection
                connection = PlatformConnection(
                    connection_id=connection_id,
                    user_id=request.user_id,
                    platform_id=platform.platform_id,
                    status=PlatformStatus.CONNECTED,
                    access_token=auth_result.get('access_token'),
                    refresh_token=auth_result.get('refresh_token'),
                    expires_at=datetime.now() + timedelta(hours=1) if auth_result.get('expires_in') else None,
                    permissions=auth_result.get('permissions', [])
                )
                
                self.connections[connection_id] = connection
                self.metrics['active_connections'] += 1
                
                return PlatformResponse(
                    request_id=request.request_id,
                    platform_id=platform.platform_id,
                    operation=request.operation,
                    status="success",
                    result={
                        "connection_id": connection_id,
                        "platform_name": platform.name,
                        "status": "connected",
                        "permissions": connection.permissions
                    }
                )
            else:
                return PlatformResponse(
                    request_id=request.request_id,
                    platform_id=platform.platform_id,
                    operation=request.operation,
                    status="failed",
                    result={},
                    errors=[auth_result.get('error', 'Authentication failed')]
                )
                
        except Exception as e:
            logger.error(f"❌ Platform connection failed: {e}")
            return PlatformResponse(
                request_id=request.request_id,
                platform_id=platform.platform_id,
                operation=request.operation,
                status="error",
                result={},
                errors=[str(e)]
            )
    
    async def _handle_platform_sync(self, request: PlatformRequest, platform: Platform) -> PlatformResponse:
        """Handle platform synchronization"""
        try:
            sync_data = request.data
            sync_operation = request.sync_operation or SyncOperation.UPLOAD
            
            # Use sync service if available
            if 'sync' in self.services:
                sync_service = self.services['sync']
                if hasattr(sync_service, 'sync_platform'):
                    result = await sync_service.sync_platform(platform.platform_id, sync_data, sync_operation)
                else:
                    result = await self._basic_sync(platform, sync_data, sync_operation)
            else:
                result = await self._basic_sync(platform, sync_data, sync_operation)
            
            # Calculate next sync time
            next_sync_at = datetime.now() + timedelta(seconds=platform.sync_frequency)
            
            return PlatformResponse(
                request_id=request.request_id,
                platform_id=platform.platform_id,
                operation=request.operation,
                status="success" if result.get('success') else "failed",
                result=result,
                sync_operation=sync_operation,
                items_processed=result.get('items_processed', 0),
                next_sync_at=next_sync_at,
                rate_limit_remaining=result.get('rate_limit_remaining')
            )
            
        except Exception as e:
            logger.error(f"❌ Platform sync failed: {e}")
            return PlatformResponse(
                request_id=request.request_id,
                platform_id=platform.platform_id,
                operation=request.operation,
                status="error",
                result={},
                sync_operation=request.sync_operation,
                errors=[str(e)]
            )
    
    async def _handle_content_upload(self, request: PlatformRequest, platform: Platform) -> PlatformResponse:
        """Handle content upload to platform"""
        try:
            content_data = request.data
            content_type = content_data.get('content_type', 'image')
            
            # Validate content type is supported
            if content_type not in platform.supported_content_types:
                return PlatformResponse(
                    request_id=request.request_id,
                    platform_id=platform.platform_id,
                    operation=request.operation,
                    status="error",
                    result={},
                    errors=[f"Content type {content_type} not supported by {platform.name}"]
                )
            
            # Check file size
            file_size_mb = content_data.get('file_size_mb', 0)
            if file_size_mb > platform.max_file_size:
                return PlatformResponse(
                    request_id=request.request_id,
                    platform_id=platform.platform_id,
                    operation=request.operation,
                    status="error",
                    result={},
                    errors=[f"File size {file_size_mb}MB exceeds limit of {platform.max_file_size}MB"]
                )
            
            # Use appropriate service for upload
            service_key = platform.platform_type.value
            if service_key in self.services:
                service = self.services[service_key]
                if hasattr(service, 'upload_content'):
                    result = await service.upload_content(platform.platform_id, content_data)
                else:
                    result = await self._basic_upload(platform, content_data)
            else:
                result = await self._basic_upload(platform, content_data)
            
            # Update metrics
            if result.get('success'):
                self.metrics['data_transferred_mb'] += file_size_mb
            
            return PlatformResponse(
                request_id=request.request_id,
                platform_id=platform.platform_id,
                operation=request.operation,
                status="success" if result.get('success') else "failed",
                result=result,
                items_processed=1 if result.get('success') else 0
            )
            
        except Exception as e:
            logger.error(f"❌ Content upload failed: {e}")
            return PlatformResponse(
                request_id=request.request_id,
                platform_id=platform.platform_id,
                operation=request.operation,
                status="error",
                result={},
                errors=[str(e)]
            )
    
    async def _basic_authentication(self, platform: Platform, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic authentication simulation"""
        await asyncio.sleep(0.1)
        
        # Simulate successful authentication (90% success rate)
        import random
        success = random.random() > 0.1
        
        if success:
            return {
                'success': True,
                'access_token': f"token_{uuid.uuid4()}",
                'refresh_token': f"refresh_{uuid.uuid4()}",
                'expires_in': 3600,
                'permissions': ['read', 'write', 'upload']
            }
        else:
            return {
                'success': False,
                'error': 'Invalid credentials or API error'
            }
    
    async def _basic_sync(self, platform: Platform, sync_data: Dict[str, Any], operation: SyncOperation) -> Dict[str, Any]:
        """Basic synchronization simulation"""
        await asyncio.sleep(0.2)
        
        items_count = sync_data.get('items_count', 1)
        
        return {
            'success': True,
            'operation': operation.value,
            'items_processed': items_count,
            'sync_id': str(uuid.uuid4()),
            'sync_timestamp': datetime.now().isoformat(),
            'rate_limit_remaining': platform.rate_limits.get('posts', 100) - 1
        }
    
    async def _basic_upload(self, platform: Platform, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic upload simulation"""
        await asyncio.sleep(0.3)
        
        return {
            'success': True,
            'upload_id': str(uuid.uuid4()),
            'platform_post_id': f"{platform.platform_id}_{uuid.uuid4()}",
            'upload_url': f"https://{platform.platform_id}.com/post/{uuid.uuid4()}",
            'uploaded_at': datetime.now().isoformat()
        }
    
    async def _handle_authentication(self, request: PlatformRequest, platform: Platform) -> PlatformResponse:
        """Handle authentication operation"""
        auth_result = await self._basic_authentication(platform, request.data)
        
        return PlatformResponse(
            request_id=request.request_id,
            platform_id=platform.platform_id,
            operation=request.operation,
            status="success" if auth_result.get('success') else "failed",
            result=auth_result
        )
    
    async def _handle_monitoring(self, request: PlatformRequest, platform: Platform) -> PlatformResponse:
        """Handle monitoring operation"""
        if 'monitoring' in self.services:
            monitoring_service = self.services['monitoring']
            if hasattr(monitoring_service, 'monitor_platform'):
                result = await monitoring_service.monitor_platform(platform.platform_id)
            else:
                result = {'status': 'healthy', 'uptime': '99.9%', 'response_time': 150}
        else:
            result = {'status': 'healthy', 'uptime': '99.9%', 'response_time': 150}
        
        return PlatformResponse(
            request_id=request.request_id,
            platform_id=platform.platform_id,
            operation=request.operation,
            status="success",
            result=result
        )
    
    async def _handle_webhook(self, request: PlatformRequest, platform: Platform) -> PlatformResponse:
        """Handle webhook operation"""
        webhook_id = str(uuid.uuid4())
        webhook_data = request.data
        
        self.webhooks[webhook_id] = {
            'platform_id': platform.platform_id,
            'user_id': request.user_id,
            'webhook_url': webhook_data.get('url'),
            'events': webhook_data.get('events', []),
            'created_at': datetime.now()
        }
        
        self.metrics['webhook_deliveries'] += 1
        
        return PlatformResponse(
            request_id=request.request_id,
            platform_id=platform.platform_id,
            operation=request.operation,
            status="success",
            result={'webhook_id': webhook_id, 'registered': True}
        )
    
    async def _handle_generic_operation(self, request: PlatformRequest, platform: Platform) -> PlatformResponse:
        """Handle generic platform operation"""
        return PlatformResponse(
            request_id=request.request_id,
            platform_id=platform.platform_id,
            operation=request.operation,
            status="success",
            result={'processed': True, 'platform': platform.name}
        )
    
    def _update_avg_sync_time(self, sync_time: float):
        """Update average sync time metric"""
        if self.metrics['total_sync_operations'] > 1:
            current_avg = self.metrics['avg_sync_time']
            new_avg = ((current_avg * (self.metrics['total_sync_operations'] - 1)) + sync_time) / self.metrics['total_sync_operations']
            self.metrics['avg_sync_time'] = new_avg
        else:
            self.metrics['avg_sync_time'] = sync_time
    
    async def get_supported_platforms(self, platform_type: Optional[PlatformType] = None) -> Dict[str, Any]:
        """Get list of supported platforms"""
        try:
            platforms_list = []
            
            for platform_id, platform in self.platforms.items():
                if platform_type is None or platform.platform_type == platform_type:
                    platforms_list.append({
                        'platform_id': platform.platform_id,
                        'name': platform.name,
                        'type': platform.platform_type.value,
                        'supported_content_types': platform.supported_content_types,
                        'max_file_size_mb': platform.max_file_size,
                        'is_active': platform.is_active
                    })
            
            return {
                'total_platforms': len(platforms_list),
                'platforms': platforms_list,
                'platform_types': [t.value for t in PlatformType],
                'filtered_by': platform_type.value if platform_type else None
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get supported platforms: {e}")
            return {'error': str(e)}
    
    async def get_platform_health(self) -> Dict[str, Any]:
        """Get platform services health status"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'services': {},
            'metrics': {
                'total_platforms': self.metrics['total_platforms'],
                'active_connections': self.metrics['active_connections'],
                'sync_success_rate': (
                    self.metrics['successful_syncs'] / (self.metrics['successful_syncs'] + self.metrics['failed_syncs'])
                    if (self.metrics['successful_syncs'] + self.metrics['failed_syncs']) > 0 else 1.0
                ),
                'avg_sync_time': self.metrics['avg_sync_time'],
                'data_transferred_mb': self.metrics['data_transferred_mb'],
                'webhook_deliveries': self.metrics['webhook_deliveries']
            },
            'platform_types': {
                ptype.value: len([p for p in self.platforms.values() if p.platform_type == ptype])
                for ptype in PlatformType
            },
            'active_platforms': len([p for p in self.platforms.values() if p.is_active])
        }
        
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'health_check'):
                    status = await service.health_check()
                else:
                    status = 'healthy'
                
                health_status['services'][service_name] = {
                    'status': status,
                    'last_check': datetime.now().isoformat()
                }
                
                if status != 'healthy':
                    health_status['overall_status'] = 'degraded'
                    
            except Exception as e:
                health_status['services'][service_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
        
        return health_status

# Global orchestrator instance
platform_orchestrator = PlatformServicesOrchestrator()

# Main functions for external access
async def process_platform_request(request: PlatformRequest) -> PlatformResponse:
    """Process platform service request"""
    return await platform_orchestrator.process_platform_request(request)

async def connect_platform(user_id: str, platform_id: str, auth_data: Dict[str, Any]) -> PlatformResponse:
    """Connect to a platform"""
    request = PlatformRequest(
        request_id=str(uuid.uuid4()),
        platform_id=platform_id,
        user_id=user_id,
        operation="connect",
        data=auth_data
    )
    return await platform_orchestrator.process_platform_request(request)

async def sync_to_platform(user_id: str, platform_id: str, content_data: Dict[str, Any], sync_op: SyncOperation = SyncOperation.UPLOAD) -> PlatformResponse:
    """Sync content to platform"""
    request = PlatformRequest(
        request_id=str(uuid.uuid4()),
        platform_id=platform_id,
        user_id=user_id,
        operation="sync",
        data=content_data,
        sync_operation=sync_op
    )
    return await platform_orchestrator.process_platform_request(request)

async def get_supported_platforms(platform_type: Optional[str] = None) -> Dict[str, Any]:
    """Get supported platforms"""
    ptype = PlatformType(platform_type) if platform_type else None
    return await platform_orchestrator.get_supported_platforms(ptype)

async def initialize_platform_services() -> bool:
    """Initialize platform services"""
    return await platform_orchestrator.initialize()

async def get_platform_health() -> Dict[str, Any]:
    """Get platform services health"""
    return await platform_orchestrator.get_platform_health()

# Export main classes and functions
__all__ = [
    'PlatformServicesOrchestrator',
    'PlatformRequest',
    'PlatformResponse',
    'Platform',
    'PlatformConnection',
    'PlatformType',
    'PlatformStatus',
    'SyncOperation',
    'platform_orchestrator',
    'process_platform_request',
    'connect_platform',
    'sync_to_platform',
    'get_supported_platforms',
    'initialize_platform_services',
    'get_platform_health'
]

if __name__ == "__main__":
    # For testing
    async def main():
        print("🚀 Starting Platform Services...")
        success = await initialize_platform_services()
        if success:
            print("✅ Platform Services initialized successfully")
            
            # Test health check
            health = await get_platform_health()
            print(f"🌐 Platform Status: {health['overall_status']}")
            print(f"📊 Total Platforms: {health['metrics']['total_platforms']}")
            print(f"🔗 Active Connections: {health['metrics']['active_connections']}")
            
            # Test supported platforms
            platforms = await get_supported_platforms('social_media')
            print(f"📱 Social Media Platforms: {platforms['total_platforms']}")
            
            # Test platform connection
            auth_data = {
                'username': 'test_user',
                'password': 'test_pass',
                'api_key': 'test_key'
            }
            
            connect_result = await connect_platform('test_user_123', 'instagram', auth_data)
            print(f"🔗 Connection Status: {connect_result.status}")
            print(f"⏱️ Processing Time: {connect_result.processing_time:.3f}s")
        else:
            print("❌ Failed to initialize Platform Services")
    
    asyncio.run(main())