"""Platform Adapter - Multi-Platform Integration Engine
====================================================

Provides unified interface for integrating with various social media and content platforms,
handling API differences, authentication, and platform-specific requirements.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Protocol
from enum import Enum
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from abc import ABC, abstractmethod
import json
import aiohttp
from pathlib import Path

from ..security.credentials import CredentialManager
from ..validation.rate_limiter import RateLimiter
from ..monitoring.metrics import MetricsCollector


class PlatformType(Enum):
    """
Platform type enumeration."""

    SOCIAL_MEDIA = "social_media"
    VIDEO_PLATFORM = "video_platform"
    AUDIO_PLATFORM = "audio_platform"
    PROFESSIONAL = "professional"
    MESSAGING = "messaging"
    BLOG = "blog"


class AuthenticationType(Enum):
    """Authentication type enumeration."""

    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"


@dataclass
class PlatformCredentials:
    """Platform credentials data structure."""
    platform: str
    auth_type: AuthenticationType
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlatformLimits:
    """
Platform limits and constraints."""
    max_file_size: int = 0  # bytes
    max_duration: int = 0  # seconds
    max_title_length: int = 0
    max_description_length: int = 0
    supported_formats: List[str] = field(default_factory=list)
    required_fields: List[str] = field(default_factory=list)
    rate_limit_per_hour: int = 0
    rate_limit_per_day: int = 0
    concurrent_uploads: int = 1


@dataclass
class PublicationRequest:
    """
Publication request data structure."""
    content_id: UUID
    file_path: str
    metadata: Dict[str, Any]
    targeting: Dict[str, Any] = field(default_factory=dict)
    monetization: Dict[str, Any] = field(default_factory=dict)
    privacy: Dict[str, Any] = field(default_factory=dict)
    thumbnail_path: Optional[str] = None
    captions_path: Optional[str] = None
    compliance_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PublicationResponse:
    """
Publication response data structure."""
    success: bool
    platform_id: Optional[str] = None
    platform_url: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0


class PlatformAdapterProtocol(Protocol):
    """
Protocol defining platform adapter interface."""
    
    async def authenticate(self, credentials: PlatformCredentials) -> bool:
        """
Authenticate with platform.
        
        Args:
            credentials: Platform authentication credentials
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        pass  # Protocol method - implemented by concrete adapters
    
    async def publish_content(self, request: PublicationRequest) -> PublicationResponse:
        """
Publish content to platform.
        
        Args:
            request: Publication request with content and metadata
            
        Returns:
            PublicationResponse: Response containing publication status and details
        """
        pass  # Protocol method - implemented by concrete adapters
    
    async def get_content_status(self, platform_id: str) -> Dict[str, Any]:
        """
Get content status from platform.
        
        Args:
            platform_id: Platform-specific content identifier
            
        Returns:
            Dict containing content status information
        """
        pass  # Protocol method - implemented by concrete adapters
    
    async def delete_content(self, platform_id: str) -> bool:
        """
Delete content from platform.
        
        Args:
            platform_id: Platform-specific content identifier
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass  # Protocol method - implemented by concrete adapters
    
    async def get_analytics(self, platform_id: str) -> Dict[str, Any]:
        """
Get content analytics from platform.
        
        Args:
            platform_id: Platform-specific content identifier
            
        Returns:
            Dict containing analytics data (views, likes, comments, etc.)
        """
        pass  # Protocol method - implemented by concrete adapters


class BasePlatformAdapter(ABC):
    """
Base class for platform adapters."""
    
    def __init__(self, platform_name: str, config: Dict[str, Any]):
        """
Initialize base adapter."""
        self.platform_name = platform_name
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{platform_name}")
        
        # Core components
        self.credential_manager = CredentialManager()
        self.rate_limiter = RateLimiter()
        self.metrics_collector = MetricsCollector()
        
        # Platform state
        self.is_authenticated = False
        self.credentials: Optional[PlatformCredentials] = None
        self.platform_limits: Optional[PlatformLimits] = None
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        self.last_request_time = datetime.utcnow()
        self.request_count = 0
        
    async def initialize(self) -> bool:
        """Initialize the adapter."""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=300),  # 5 minutes
                headers=self._get_default_headers()
            )
            
            # Load platform limits
            self.platform_limits = await self._load_platform_limits()
            
            # Load credentials
            self.credentials = await self.credential_manager.get_credentials(self.platform_name)
            
            if self.credentials:
                # Authenticate
                self.is_authenticated = await self.authenticate(self.credentials)
            
            self.logger.info(f"Platform adapter {self.platform_name} initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.platform_name} adapter: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the adapter."""
        if self.session:
            await self.session.close()
        
        self.logger.info(f"Platform adapter {self.platform_name} shutdown")
    
    @abstractmethod
    async def authenticate(self, credentials: PlatformCredentials) -> bool:
        """Authenticate with platform."""
        pass
    
    @abstractmethod
    async def publish_content(self, request: PublicationRequest) -> PublicationResponse:
        """
Publish content to platform."""
        pass
    
    @abstractmethod
    async def get_content_status(self, platform_id: str) -> Dict[str, Any]:
        """
Get content status from platform."""
        pass
    
    @abstractmethod
    async def delete_content(self, platform_id: str) -> bool:
        """
Delete content from platform."""
        pass
    
    @abstractmethod
    async def get_analytics(self, platform_id: str) -> Dict[str, Any]:
        """
Get content analytics from platform."""
        pass
    
    async def _load_platform_limits(self) -> PlatformLimits:
        """
Load platform limits and constraints."""
        # This would load from configuration or API
        # Default limits for safety
        return PlatformLimits(
            max_file_size=100 * 1024 * 1024,  # 100MB
            max_duration=3600,  # 1 hour
            max_title_length=100,
            max_description_length=1000,
            supported_formats=["mp4", "jpg", "png", "mp3"],
            required_fields=["title"],
            rate_limit_per_hour=100,
            rate_limit_per_day=1000,
            concurrent_uploads=1
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers."""
        return {
            'User-Agent': f'IA-Influencer-Agent/{self.platform_name}/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    async def _apply_rate_limiting(self) -> None:
        """
Apply rate limiting."""
        await self.rate_limiter.acquire(
            key=f"{self.platform_name}_api",
            limit=self.platform_limits.rate_limit_per_hour,
            window=3600  # 1 hour
        )
    
    async def _make_api_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request."""
        if not self.session:
            raise RuntimeError("Adapter not initialized")
        
        # Apply rate limiting
        await self._apply_rate_limiting()
        
        # Prepare headers
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)
        
        # Add authentication headers
        auth_headers = await self._get_auth_headers()
        request_headers.update(auth_headers)
        
        try:
            # Make request
            async with self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                json=data if data and not files else None,
                data=files if files else None
            ) as response:
                
                # Track metrics
                self.metrics_collector.record_api_request(
                    platform=self.platform_name,
                    status_code=response.status,
                    response_time=(datetime.utcnow() - self.last_request_time).total_seconds()
                )
                
                # Handle response
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"API request failed: {response.status} - {error_text}")
                
                # Parse JSON response
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    return {'text': await response.text()}
                    
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            raise
    
    @abstractmethod
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        pass
    
    async def test_connection(self) -> bool:
        """
Test connection to platform."""
        try:
            # This would make a simple API call to test connectivity
            # Implementation varies by platform
            return self.is_authenticated
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False


class YouTubeAdapter(BasePlatformAdapter):
    """YouTube platform adapter."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("youtube", config)
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        self.upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
    
    async def authenticate(self, credentials: PlatformCredentials) -> bool:
        """Authenticate with YouTube API."""
        try:
            # Test authentication with a simple API call
            headers = {
                'Authorization': f'Bearer {credentials.access_token}'
            }
            
            response = await self._make_api_request(
                method='GET',
                url=f'{self.api_base_url}/channels',
                headers=headers,
                data={'part': 'snippet', 'mine': 'true'}
            )
            
            self.is_authenticated = True
            self.logger.info("YouTube authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"YouTube authentication failed: {e}")
            return False
    
    async def publish_content(self, request: PublicationRequest) -> PublicationResponse:
        """Publish video to YouTube."""
        try:
            start_time = datetime.utcnow()
            
            # Prepare metadata
            video_metadata = {
                'snippet': {
                    'title': request.metadata.get('title', 'Untitled'),
                    'description': request.metadata.get('description', ''),
                    'tags': request.metadata.get('tags', []),
                    'categoryId': request.metadata.get('category_id', '22'),  # People & Blogs
                    'defaultLanguage': request.metadata.get('language', 'en')
                },
                'status': {
                    'privacyStatus': request.privacy.get('privacy_status', 'private'),
                    'publishAt': request.metadata.get('publish_at'),
                    'selfDeclaredMadeForKids': request.metadata.get('made_for_kids', False)
                }
            }
            
            # Add monetization settings
            if request.monetization:
                video_metadata['monetizationDetails'] = {
                    'access': {
                        'allowed': request.monetization.get('enabled', True)
                    }
                }
            
            # Upload video
            with open(request.file_path, 'rb') as video_file:
                files = {
                    'video': video_file,
                    'metadata': json.dumps(video_metadata)
                }
                
                response = await self._make_api_request(
                    method='POST',
                    url=self.upload_url,
                    files=files,
                    data={'part': 'snippet,status,monetizationDetails'}
                )
            
            # Upload thumbnail if provided
            video_id = response.get('id')
            if request.thumbnail_path and video_id:
                await self._upload_thumbnail(video_id, request.thumbnail_path)
            
            # Upload captions if provided
            if request.captions_path and video_id:
                await self._upload_captions(video_id, request.captions_path)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return PublicationResponse(
                success=True,
                platform_id=video_id,
                platform_url=f"https://www.youtube.com/watch?v={video_id}",
                metadata={
                    'video_id': video_id,
                    'title': video_metadata['snippet']['title'],
                    'privacy_status': video_metadata['status']['privacyStatus']
                },
                analytics_data={
                    'views': 0,
                    'likes': 0,
                    'comments': 0,
                    'shares': 0
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"YouTube upload failed: {e}")
            return PublicationResponse(
                success=False,
                error_message=str(e)
            )
    
    async def get_content_status(self, platform_id: str) -> Dict[str, Any]:
        """Get YouTube video status."""
        try:
            response = await self._make_api_request(
                method='GET',
                url=f'{self.api_base_url}/videos',
                data={
                    'part': 'snippet,status,statistics',
                    'id': platform_id
                }
            )
            
            if response.get('items'):
                video = response['items'][0]
                return {
                    'status': 'published',
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'published_at': video['snippet']['publishedAt'],
                    'view_count': int(video['statistics'].get('viewCount', 0)),
                    'like_count': int(video['statistics'].get('likeCount', 0)),
                    'comment_count': int(video['statistics'].get('commentCount', 0))
                }
            else:
                return {'status': 'not_found'}
                
        except Exception as e:
            self.logger.error(f"Failed to get YouTube video status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def delete_content(self, platform_id: str) -> bool:
        """Delete YouTube video."""
        try:
            await self._make_api_request(
                method='DELETE',
                url=f'{self.api_base_url}/videos',
                data={'id': platform_id}
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete YouTube video: {e}")
            return False
    
    async def get_analytics(self, platform_id: str) -> Dict[str, Any]:
        """Get YouTube video analytics."""
        try:
            # Get basic statistics
            response = await self._make_api_request(
                method='GET',
                url=f'{self.api_base_url}/videos',
                data={
                    'part': 'statistics,snippet',
                    'id': platform_id
                }
            )
            
            if response.get('items'):
                video = response['items'][0]
                stats = video['statistics']
                
                return {
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'dislikes': int(stats.get('dislikeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'favorites': int(stats.get('favoriteCount', 0)),
                    'duration': video['snippet'].get('duration'),
                    'published_at': video['snippet']['publishedAt']
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Failed to get YouTube analytics: {e}")
            return {}
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get YouTube authentication headers."""
        if not self.credentials or not self.credentials.access_token:
            return {}
        
        return {
            'Authorization': f'Bearer {self.credentials.access_token}'
        }
    
    async def _upload_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """
Upload video thumbnail."""
        try:
            with open(thumbnail_path, 'rb') as thumb_file:
                files = {'thumbnail': thumb_file}
                
                await self._make_api_request(
                    method='POST',
                    url=f'{self.api_base_url}/thumbnails/set',
                    files=files,
                    data={'videoId': video_id}
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upload thumbnail: {e}")
            return False
    
    async def _upload_captions(self, video_id: str, captions_path: str) -> bool:
        """Upload video captions."""
        try:
            caption_metadata = {
                'snippet': {
                    'videoId': video_id,
                    'language': 'en',
                    'name': 'English',
                    'isDraft': False
                }
            }
            
            with open(captions_path, 'rb') as caption_file:
                files = {
                    'captions': caption_file,
                    'metadata': json.dumps(caption_metadata)
                }
                
                await self._make_api_request(
                    method='POST',
                    url=f'{self.api_base_url}/captions',
                    files=files,
                    data={'part': 'snippet'}
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upload captions: {e}")
            return False


class InstagramAdapter(BasePlatformAdapter):
    """Instagram platform adapter."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("instagram", config)
        self.api_base_url = "https://graph.facebook.com/v18.0"
    
    async def authenticate(self, credentials: PlatformCredentials) -> bool:
        """Authenticate with Instagram API."""
        try:
            # Test authentication
            response = await self._make_api_request(
                method='GET',
                url=f'{self.api_base_url}/me',
                data={'fields': 'id,name'}
            )
            
            self.is_authenticated = True
            self.logger.info("Instagram authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Instagram authentication failed: {e}")
            return False
    
    async def publish_content(self, request: PublicationRequest) -> PublicationResponse:
        """Publish content to Instagram."""
        try:
            start_time = datetime.utcnow()
            
            # Determine content type
            file_path = Path(request.file_path)
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png']:
                return await self._publish_image(request)
            elif file_extension in ['.mp4', '.mov']:
                return await self._publish_video(request)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            self.logger.error(f"Instagram upload failed: {e}")
            return PublicationResponse(
                success=False,
                error_message=str(e)
            )
    
    async def _publish_image(self, request: PublicationRequest) -> PublicationResponse:
        """Publish image to Instagram."""
        # Step 1: Create media object
        media_data = {
            'image_url': request.file_path,  # This would be a public URL
            'caption': request.metadata.get('caption', ''),
            'access_token': self.credentials.access_token
        }
        
        response = await self._make_api_request(
            method='POST',
            url=f'{self.api_base_url}/me/media',
            data=media_data
        )
        
        creation_id = response.get('id')
        
        # Step 2: Publish media
        publish_response = await self._make_api_request(
            method='POST',
            url=f'{self.api_base_url}/me/media_publish',
            data={
                'creation_id': creation_id,
                'access_token': self.credentials.access_token
            }
        )
        
        media_id = publish_response.get('id')
        
        return PublicationResponse(
            success=True,
            platform_id=media_id,
            platform_url=f"https://www.instagram.com/p/{media_id}/",
            metadata={
                'media_id': media_id,
                'creation_id': creation_id,
                'caption': media_data['caption']
            }
        )
    
    async def _publish_video(self, request: PublicationRequest) -> PublicationResponse:
        """Publish video to Instagram."""
        # Similar to image but with video-specific parameters
        media_data = {
            'video_url': request.file_path,  # This would be a public URL
            'caption': request.metadata.get('caption', ''),
            'media_type': 'VIDEO',
            'access_token': self.credentials.access_token
        }
        
        # Add thumbnail if provided
        if request.thumbnail_path:
            media_data['thumb_offset'] = request.metadata.get('thumb_offset', 0)
        
        response = await self._make_api_request(
            method='POST',
            url=f'{self.api_base_url}/me/media',
            data=media_data
        )
        
        creation_id = response.get('id')
        
        # Wait for video processing
        await self._wait_for_video_processing(creation_id)
        
        # Publish video
        publish_response = await self._make_api_request(
            method='POST',
            url=f'{self.api_base_url}/me/media_publish',
            data={
                'creation_id': creation_id,
                'access_token': self.credentials.access_token
            }
        )
        
        media_id = publish_response.get('id')
        
        return PublicationResponse(
            success=True,
            platform_id=media_id,
            platform_url=f"https://www.instagram.com/p/{media_id}/",
            metadata={
                'media_id': media_id,
                'creation_id': creation_id,
                'caption': media_data['caption'],
                'media_type': 'video'
            }
        )
    
    async def _wait_for_video_processing(self, creation_id: str, timeout: int = 300) -> None:
        """Wait for Instagram video processing to complete."""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            response = await self._make_api_request(
                method='GET',
                url=f'{self.api_base_url}/{creation_id}',
                data={
                    'fields': 'status_code',
                    'access_token': self.credentials.access_token
                }
            )
            
            status = response.get('status_code')
            
            if status == 'FINISHED':
                return
            elif status == 'ERROR':
                raise Exception("Video processing failed")
            
            await asyncio.sleep(5)  # Wait 5 seconds before checking again
        
        raise Exception("Video processing timeout")
    
    async def get_content_status(self, platform_id: str) -> Dict[str, Any]:
        """Get Instagram content status."""
        try:
            response = await self._make_api_request(
                method='GET',
                url=f'{self.api_base_url}/{platform_id}',
                data={
                    'fields': 'id,media_type,media_url,permalink,timestamp,caption',
                    'access_token': self.credentials.access_token
                }
            )
            
            return {
                'status': 'published',
                'media_type': response.get('media_type'),
                'caption': response.get('caption'),
                'permalink': response.get('permalink'),
                'published_at': response.get('timestamp')
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get Instagram content status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def delete_content(self, platform_id: str) -> bool:
        """Delete Instagram content."""
        try:
            await self._make_api_request(
                method='DELETE',
                url=f'{self.api_base_url}/{platform_id}',
                data={'access_token': self.credentials.access_token}
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete Instagram content: {e}")
            return False
    
    async def get_analytics(self, platform_id: str) -> Dict[str, Any]:
        """Get Instagram content analytics."""
        try:
            response = await self._make_api_request(
                method='GET',
                url=f'{self.api_base_url}/{platform_id}/insights',
                data={
                    'metric': 'engagement,impressions,reach,saved',
                    'access_token': self.credentials.access_token
                }
            )
            
            analytics = {}
            for insight in response.get('data', []):
                metric_name = insight.get('name')
                metric_value = insight.get('values', [{}])[0].get('value', 0)
                analytics[metric_name] = metric_value
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get Instagram analytics: {e}")
            return {}
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get Instagram authentication headers."""
        # Instagram uses access_token in query parameters, not headers
        return {}


class PlatformAdapter:
    """
    Main Platform Adapter Manager
    
    Manages multiple platform adapters and provides unified interface.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
Initialize platform adapter manager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Platform adapters
        self.adapters: Dict[str, BasePlatformAdapter] = {}
        
        # Supported platforms
        self.supported_platforms = {
            'youtube': YouTubeAdapter,
            'instagram': InstagramAdapter,
            # Additional platforms would be added here
        }
        
        # System state
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """
Initialize all platform adapters."""
        try:
            self.logger.info("Initializing Platform Adapter Manager")
            
            # Initialize adapters for configured platforms
            for platform_name, adapter_class in self.supported_platforms.items():
                platform_config = self.config.get('platforms', {}).get(platform_name, {})
                
                if platform_config.get('enabled', False):
                    adapter = adapter_class(platform_config)
                    
                    if await adapter.initialize():
                        self.adapters[platform_name] = adapter
                        self.logger.info(f"Initialized {platform_name} adapter")
                    else:
                        self.logger.warning(f"Failed to initialize {platform_name} adapter")
            
            self.is_initialized = True
            self.logger.info("Platform Adapter Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Platform Adapter Manager: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown all platform adapters."""
        for platform_name, adapter in self.adapters.items():
            try:
                await adapter.shutdown()
                self.logger.info(f"Shutdown {platform_name} adapter")
            except Exception as e:
                self.logger.error(f"Error shutting down {platform_name} adapter: {e}")
        
        self.adapters.clear()
        self.is_initialized = False
    
    def get_adapter(self, platform: str) -> Optional[BasePlatformAdapter]:
        """Get adapter for specific platform."""
        return self.adapters.get(platform)
    
    def is_platform_supported(self, platform: str) -> bool:
        """
Check if platform is supported."""
        return platform in self.adapters
    
    def get_supported_platforms(self) -> List[str]:
        """
Get list of supported platforms."""
        return list(self.adapters.keys())
    
    async def publish_to_platform(
        self,
        platform: str,
        request: PublicationRequest
    ) -> PublicationResponse:
        """
Publish content to specific platform."""
        adapter = self.get_adapter(platform)
        if not adapter:
            return PublicationResponse(
                success=False,
                error_message=f"Platform {platform} not supported or not configured"
            )
        
        return await adapter.publish_content(request)
    
    async def get_platform_status(self, platform: str, platform_id: str) -> Dict[str, Any]:
        """Get content status from specific platform."""
        adapter = self.get_adapter(platform)
        if not adapter:
            return {'status': 'error', 'error': 'Platform not supported'}
        
        return await adapter.get_content_status(platform_id)
    
    async def delete_from_platform(self, platform: str, platform_id: str) -> bool:
        """
Delete content from specific platform."""
        adapter = self.get_adapter(platform)
        if not adapter:
            return False
        
        return await adapter.delete_content(platform_id)
    
    async def get_platform_analytics(self, platform: str, platform_id: str) -> Dict[str, Any]:
        """
Get analytics from specific platform."""
        adapter = self.get_adapter(platform)
        if not adapter:
            return {}
        
        return await adapter.get_analytics(platform_id)
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """
Test connections to all configured platforms."""
        results = {}
        
        for platform_name, adapter in self.adapters.items():
            try:
                results[platform_name] = await adapter.test_connection()
            except Exception as e:
                self.logger.error(f"Connection test failed for {platform_name}: {e}")
                results[platform_name] = False
        
        return results
    
    def get_platform_limits(self, platform: str) -> Optional[PlatformLimits]:
        """Get platform limits and constraints."""
        adapter = self.get_adapter(platform)
        if adapter:
            return adapter.platform_limits
        return None
    
    def get_adapter_status(self) -> Dict[str, Any]:
        """
Get status of all adapters."""
        status = {}
        
        for platform_name, adapter in self.adapters.items():
            status[platform_name] = {
                'initialized': adapter is not None,
                'authenticated': adapter.is_authenticated if adapter else False,
                'platform_limits': adapter.platform_limits.__dict__ if adapter and adapter.platform_limits else None
            }
        
        return status
