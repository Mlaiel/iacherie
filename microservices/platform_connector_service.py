"""
🌐 Platform Connector Microservice
Multi-platform API integration management for content distribution across 20+ platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json
import aiohttp
import base64
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PlatformType(str, Enum):
    """Platform categories"""
    SOCIAL_MEDIA = "social_media"
    VIDEO_PLATFORM = "video_platform"
    MUSIC_PLATFORM = "music_platform"
    BLOGGING_PLATFORM = "blogging_platform"
    MARKETPLACE = "marketplace"
    STREAMING_PLATFORM = "streaming_platform"
    PODCAST_PLATFORM = "podcast_platform"
    PHOTO_PLATFORM = "photo_platform"


class ContentFormat(str, Enum):
    """Content format types"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    LIVE_STREAM = "live_stream"


class PlatformStatus(str, Enum):
    """Platform connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


@dataclass
class PlatformCredentials:
    """Platform API credentials"""
    platform_id: str
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    webhook_secret: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)


@dataclass
class PlatformConfig:
    """Platform configuration"""
    platform_id: str
    name: str
    platform_type: PlatformType
    base_url: str
    api_version: str
    supported_formats: List[ContentFormat]
    rate_limits: Dict[str, int] = field(default_factory=dict)
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    max_file_size_mb: Optional[int] = None
    webhook_events: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class ContentUpload:
    """Content upload request"""
    upload_id: str
    creator_id: str
    platform_id: str
    content_type: ContentFormat
    title: str
    description: str
    file_url: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    privacy_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UploadResult:
    """Upload operation result"""
    upload_id: str
    platform_id: str
    platform_post_id: Optional[str] = None
    status: str = "pending"
    platform_url: Optional[str] = None
    error_message: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PlatformConnector(ABC):
    """Abstract platform connector interface"""
    
    @abstractmethod
    async def authenticate(self, credentials: PlatformCredentials) -> bool:
        """Authenticate with platform"""
        pass
    
    @abstractmethod
    async def upload_content(self, content: ContentUpload) -> UploadResult:
        """Upload content to platform"""
        pass
    
    @abstractmethod
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get content analytics from platform"""
        pass
    
    @abstractmethod
    async def delete_content(self, post_id: str) -> bool:
        """Delete content from platform"""
        pass


class YouTubeConnector(PlatformConnector):
    """YouTube platform connector"""
    
    def __init__(self, config -> None: PlatformConfig) -> None:
        self.config = config
        self.credentials: Optional[PlatformCredentials] = None
    
    async def authenticate(self, credentials: PlatformCredentials) -> bool:
        """Authenticate with YouTube API"""
        try:
            # Mock YouTube OAuth2 authentication
            if credentials.access_token:
                self.credentials = credentials
                logger.info("YouTube authentication successful")
                return True
            return False
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False
    
    async def upload_content(self, content: ContentUpload) -> UploadResult:
        """Upload video to YouTube"""
        try:
            # Mock YouTube upload
            result = UploadResult(
                upload_id=content.upload_id,
                platform_id=content.platform_id,
                platform_post_id=f"yt_{uuid.uuid4().hex[:8]}",
                status="success",
                platform_url=f"https://youtube.com/watch?v={uuid.uuid4().hex[:8]}",
                uploaded_at=datetime.utcnow()
            )
            
            logger.info(f"Uploaded content to YouTube: {result.platform_post_id}")
            return result
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            return UploadResult(
                upload_id=content.upload_id,
                platform_id=content.platform_id,
                status="failed",
                error_message=str(e)
            )
    
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get YouTube analytics"""
        # Mock analytics data
        return {
            "post_id": post_id,
            "views": 1000,
            "likes": 50,
            "comments": 10,
            "shares": 5,
            "watch_time_minutes": 500,
            "engagement_rate": 6.5
        }
    
    async def delete_content(self, post_id: str) -> bool:
        """Delete YouTube video"""
        try:
            # Mock deletion
            logger.info(f"Deleted YouTube video: {post_id}")
            return True
        except Exception as e:
            logger.error(f"YouTube deletion failed: {e}")
            return False


class InstagramConnector(PlatformConnector):
    """Instagram platform connector"""
    
    def __init__(self, config -> None: PlatformConfig) -> None:
        self.config = config
        self.credentials: Optional[PlatformCredentials] = None
    
    async def authenticate(self, credentials: PlatformCredentials) -> bool:
        """Authenticate with Instagram API"""
        try:
            if credentials.access_token:
                self.credentials = credentials
                logger.info("Instagram authentication successful")
                return True
            return False
        except Exception as e:
            logger.error(f"Instagram authentication failed: {e}")
            return False
    
    async def upload_content(self, content: ContentUpload) -> UploadResult:
        """Upload content to Instagram"""
        try:
            result = UploadResult(
                upload_id=content.upload_id,
                platform_id=content.platform_id,
                platform_post_id=f"ig_{uuid.uuid4().hex[:8]}",
                status="success",
                platform_url=f"https://instagram.com/p/{uuid.uuid4().hex[:8]}",
                uploaded_at=datetime.utcnow()
            )
            
            logger.info(f"Uploaded content to Instagram: {result.platform_post_id}")
            return result
            
        except Exception as e:
            logger.error(f"Instagram upload failed: {e}")
            return UploadResult(
                upload_id=content.upload_id,
                platform_id=content.platform_id,
                status="failed",
                error_message=str(e)
            )
    
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Instagram analytics"""
        return {
            "post_id": post_id,
            "likes": 200,
            "comments": 15,
            "shares": 8,
            "saves": 25,
            "reach": 800,
            "impressions": 1200,
            "engagement_rate": 20.6
        }
    
    async def delete_content(self, post_id: str) -> bool:
        """Delete Instagram post"""
        try:
            logger.info(f"Deleted Instagram post: {post_id}")
            return True
        except Exception as e:
            logger.error(f"Instagram deletion failed: {e}")
            return False


class SpotifyConnector(PlatformConnector):
    """Spotify platform connector"""
    
    def __init__(self, config -> None: PlatformConfig) -> None:
        self.config = config
        self.credentials: Optional[PlatformCredentials] = None
    
    async def authenticate(self, credentials: PlatformCredentials) -> bool:
        """Authenticate with Spotify API"""
        try:
            if credentials.client_id and credentials.client_secret:
                self.credentials = credentials
                logger.info("Spotify authentication successful")
                return True
            return False
        except Exception as e:
            logger.error(f"Spotify authentication failed: {e}")
            return False
    
    async def upload_content(self, content: ContentUpload) -> UploadResult:
        """Upload music to Spotify"""
        try:
            result = UploadResult(
                upload_id=content.upload_id,
                platform_id=content.platform_id,
                platform_post_id=f"spotify_{uuid.uuid4().hex[:8]}",
                status="success",
                platform_url=f"https://open.spotify.com/track/{uuid.uuid4().hex[:8]}",
                uploaded_at=datetime.utcnow()
            )
            
            logger.info(f"Uploaded music to Spotify: {result.platform_post_id}")
            return result
            
        except Exception as e:
            logger.error(f"Spotify upload failed: {e}")
            return UploadResult(
                upload_id=content.upload_id,
                platform_id=content.platform_id,
                status="failed",
                error_message=str(e)
            )
    
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Spotify analytics"""
        return {
            "post_id": post_id,
            "streams": 5000,
            "listeners": 1200,
            "saves": 300,
            "playlist_adds": 150,
            "skip_rate": 15.2,
            "completion_rate": 72.8
        }
    
    async def delete_content(self, post_id: str) -> bool:
        """Delete Spotify track"""
        try:
            logger.info(f"Deleted Spotify track: {post_id}")
            return True
        except Exception as e:
            logger.error(f"Spotify deletion failed: {e}")
            return False


class PlatformConnectorService:
    """Multi-platform API integration management service"""
    
    def __init__(self) -> None:
        self.platforms: Dict[str, PlatformConfig] = {}
        self.connectors: Dict[str, PlatformConnector] = {}
        self.credentials: Dict[str, PlatformCredentials] = {}
        self.upload_history: List[UploadResult] = []
        
        # Initialize default platforms
        self._initialize_platforms()
    
    def _initialize_platforms(self) -> None:
        """Initialize supported platforms"""
        platforms = [
            PlatformConfig(
                platform_id="youtube",
                name="YouTube",
                platform_type=PlatformType.VIDEO_PLATFORM,
                base_url="https://www.googleapis.com/youtube/v3",
                api_version="v3",
                supported_formats=[ContentFormat.VIDEO],
                rate_limits={"uploads_per_day": 6},
                required_fields=["title", "description"],
                max_file_size_mb=2048,
                webhook_events=["video_published", "video_processed"]
            ),
            PlatformConfig(
                platform_id="instagram",
                name="Instagram",
                platform_type=PlatformType.SOCIAL_MEDIA,
                base_url="https://graph.instagram.com",
                api_version="v18.0",
                supported_formats=[ContentFormat.IMAGE, ContentFormat.VIDEO],
                rate_limits={"uploads_per_hour": 25},
                required_fields=["caption"],
                max_file_size_mb=100
            ),
            PlatformConfig(
                platform_id="spotify",
                name="Spotify",
                platform_type=PlatformType.MUSIC_PLATFORM,
                base_url="https://api.spotify.com",
                api_version="v1",
                supported_formats=[ContentFormat.AUDIO],
                rate_limits={"uploads_per_day": 100},
                required_fields=["title", "artist"]
            ),
            PlatformConfig(
                platform_id="tiktok",
                name="TikTok",
                platform_type=PlatformType.SOCIAL_MEDIA,
                base_url="https://open-api.tiktok.com",
                api_version="v1.3",
                supported_formats=[ContentFormat.VIDEO],
                rate_limits={"uploads_per_day": 10},
                max_file_size_mb=500
            ),
            PlatformConfig(
                platform_id="linkedin",
                name="LinkedIn",
                platform_type=PlatformType.SOCIAL_MEDIA,
                base_url="https://api.linkedin.com",
                api_version="v2",
                supported_formats=[ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.TEXT],
                rate_limits={"uploads_per_day": 100}
            )
        ]
        
        for platform in platforms:
            self.platforms[platform.platform_id] = platform
            
            # Initialize connectors
            if platform.platform_id == "youtube":
                self.connectors[platform.platform_id] = YouTubeConnector(platform)
            elif platform.platform_id == "instagram":
                self.connectors[platform.platform_id] = InstagramConnector(platform)
            elif platform.platform_id == "spotify":
                self.connectors[platform.platform_id] = SpotifyConnector(platform)
    
    async def connect_platform(self, platform_id: str, credentials: PlatformCredentials) -> bool:
        """Connect to a platform with credentials"""
        if platform_id not in self.connectors:
            raise ValueError(f"Platform {platform_id} not supported")
        
        connector = self.connectors[platform_id]
        success = await connector.authenticate(credentials)
        
        if success:
            self.credentials[platform_id] = credentials
            logger.info(f"Connected to platform: {platform_id}")
        
        return success
    
    async def upload_to_platform(self, platform_id: str, content: ContentUpload) -> UploadResult:
        """Upload content to specific platform"""
        if platform_id not in self.connectors:
            raise ValueError(f"Platform {platform_id} not supported")
        
        if platform_id not in self.credentials:
            raise ValueError(f"Platform {platform_id} not authenticated")
        
        # Check platform requirements
        platform = self.platforms[platform_id]
        if content.content_type not in platform.supported_formats:
            raise ValueError(f"Content type {content.content_type} not supported by {platform_id}")
        
        # Check rate limits
        if not await self._check_rate_limits(platform_id):
            raise ValueError(f"Rate limit exceeded for {platform_id}")
        
        connector = self.connectors[platform_id]
        result = await connector.upload_content(content)
        
        self.upload_history.append(result)
        return result
    
    async def upload_to_multiple_platforms(
        self, 
        platform_ids: List[str], 
        content: ContentUpload
    ) -> List[UploadResult]:
        """Upload content to multiple platforms simultaneously"""
        
        tasks = []
        for platform_id in platform_ids:
            if platform_id in self.connectors and platform_id in self.credentials:
                # Create separate content object for each platform
                platform_content = ContentUpload(
                    upload_id=f"{content.upload_id}_{platform_id}",
                    creator_id=content.creator_id,
                    platform_id=platform_id,
                    content_type=content.content_type,
                    title=content.title,
                    description=content.description,
                    file_url=content.file_url,
                    metadata=content.metadata.copy(),
                    tags=content.tags.copy(),
                    scheduled_at=content.scheduled_at,
                    privacy_settings=content.privacy_settings.copy()
                )
                
                tasks.append(self.upload_to_platform(platform_id, platform_content))
        
        if not tasks:
            return []
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(UploadResult(
                    upload_id=f"{content.upload_id}_{platform_ids[i]}",
                    platform_id=platform_ids[i],
                    status="failed",
                    error_message=str(result)
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def _check_rate_limits(self, platform_id: str) -> bool:
        """Check if platform rate limits allow upload"""
        platform = self.platforms[platform_id]
        current_time = datetime.utcnow()
        
        # Count recent uploads
        for limit_type, limit_value in platform.rate_limits.items():
            if "per_day" in limit_type:
                start_time = current_time - timedelta(days=1)
            elif "per_hour" in limit_type:
                start_time = current_time - timedelta(hours=1)
            else:
                continue
            
            recent_uploads = [
                r for r in self.upload_history
                if (r.platform_id == platform_id and 
                    r.uploaded_at and 
                    r.uploaded_at >= start_time and
                    r.status == "success")
            ]
            
            if len(recent_uploads) >= limit_value:
                return False
        
        return True
    
    async def get_platform_analytics(self, platform_id: str, post_ids: List[str]) -> List[Dict[str, Any]]:
        """Get analytics for posts on a platform"""
        if platform_id not in self.connectors:
            return []
        
        connector = self.connectors[platform_id]
        analytics = []
        
        for post_id in post_ids:
            try:
                stats = await connector.get_analytics(post_id)
                analytics.append(stats)
            except Exception as e:
                logger.error(f"Failed to get analytics for {post_id}: {e}")
                analytics.append({"post_id": post_id, "error": str(e)})
        
        return analytics
    
    async def get_cross_platform_analytics(self, upload_id: str) -> Dict[str, Any]:
        """Get aggregated analytics across all platforms for an upload"""
        # Find all results for this upload
        related_uploads = [
            r for r in self.upload_history
            if r.upload_id.startswith(upload_id) and r.status == "success"
        ]
        
        if not related_uploads:
            return {}
        
        analytics = {}
        total_engagement = 0
        total_reach = 0
        
        for upload_result in related_uploads:
            if upload_result.platform_post_id:
                platform_analytics = await self.get_platform_analytics(
                    upload_result.platform_id, 
                    [upload_result.platform_post_id]
                )
                
                if platform_analytics:
                    analytics[upload_result.platform_id] = platform_analytics[0]
                    
                    # Aggregate metrics
                    platform_data = platform_analytics[0]
                    total_engagement += platform_data.get("likes", 0) + platform_data.get("comments", 0) + platform_data.get("shares", 0)
                    total_reach += platform_data.get("views", platform_data.get("reach", platform_data.get("streams", 0)))
        
        return {
            "upload_id": upload_id,
            "platform_analytics": analytics,
            "aggregated_metrics": {
                "total_engagement": total_engagement,
                "total_reach": total_reach,
                "platforms_count": len(analytics)
            }
        }
    
    async def schedule_content(
        self, 
        platform_ids: List[str], 
        content: ContentUpload, 
        scheduled_time: datetime
    ) -> str:
        """Schedule content for future publication"""
        # In a real implementation, this would use a job scheduler
        schedule_id = str(uuid.uuid4())
        
        logger.info(f"Scheduled content {content.upload_id} for {scheduled_time} on platforms: {platform_ids}")
        
        # Store scheduling info (in real implementation, use database)
        return schedule_id
    
    async def get_platform_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all connected platforms"""
        status = {}
        
        for platform_id, config in self.platforms.items():
            is_connected = platform_id in self.credentials
            
            status[platform_id] = {
                "name": config.name,
                "type": config.platform_type.value,
                "connected": is_connected,
                "supported_formats": [f.value for f in config.supported_formats],
                "rate_limits": config.rate_limits,
                "status": PlatformStatus.CONNECTED.value if is_connected else PlatformStatus.DISCONNECTED.value
            }
        
        return status


# Global service instance
platform_connector_service = PlatformConnectorService()

async def get_platform_connector_service() -> PlatformConnectorService:
    """Get platform connector service instance"""
    return platform_connector_service