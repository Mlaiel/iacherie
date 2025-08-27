"""
Platform Base Classes and Manager

This module provides the base classes and manager for platform integrations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Enumeration of all supported platform types"""
    
    # Original 16 platforms - Core social media and content platforms
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    BANDCAMP = "bandcamp"
    REDDIT = "reddit"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    
    # Extended platforms for complete ecosystem coverage (12 additional)
    WHATSAPP = "whatsapp"              # Business messaging
    VIMEO = "vimeo"                    # Professional video hosting
    CLUBHOUSE = "clubhouse"            # Audio-based social networking
    MEDIUM = "medium"                  # Article publishing platform
    MASTODON = "mastodon"              # Decentralized social network
    BEREAL = "bereal"                  # Authentic social sharing
    ONLYFANS = "onlyfans"              # Content creator platform
    PATREON = "patreon"                # Creator membership platform
    SUBSTACK = "substack"              # Newsletter publishing
    THREADS = "threads"                # Meta's text-based platform
    KICK = "kick"                      # Streaming platform
    RUMBLE = "rumble"                  # Video platform


class ContentType(Enum):
    """Content type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PLAYLIST = "playlist"
    ALBUM = "album"
    TRACK = "track"


class PlatformStatus(Enum):
    """Platform status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    SUSPENDED = "suspended"


@dataclass
class PlatformCredentials:
    """Platform credentials configuration"""
    api_key: str
    api_secret: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    user_id: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class PlatformConfig:
    """Platform configuration"""
    platform_id: str
    platform_name: str
    platform_type: PlatformType
    api_base_url: str
    rate_limit: int
    max_retries: int
    timeout: int
    credentials: PlatformCredentials
    features: List[str]
    content_types: List[ContentType]


@dataclass
class ContentMetadata:
    """Content metadata structure"""
    title: str
    description: str
    tags: List[str]
    category: str
    language: str
    duration: Optional[int] = None
    file_size: Optional[int] = None
    format: Optional[str] = None
    quality: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None


@dataclass
class UploadResult:
    """Upload result structure"""
    success: bool
    platform_id: str
    content_id: Optional[str] = None
    url: Optional[str] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AnalyticsData:
    """Analytics data structure"""
    platform_id: str
    content_id: str
    views: int
    likes: int
    shares: int
    comments: int
    revenue: Optional[float] = None
    engagement_rate: Optional[float] = None
    reach: Optional[int] = None
    impressions: Optional[int] = None
    click_through_rate: Optional[float] = None
    audience_demographics: Optional[Dict[str, Any]] = None
    collected_at: datetime = datetime.utcnow()


class PlatformBase(ABC):
    """Base class for all platform integrations"""
    
    def __init__(self, config: PlatformConfig):
        """Initialize platform with configuration"""
        self.config = config
        self.status = PlatformStatus.INACTIVE
        self.last_sync = None
        self.error_count = 0
        self.max_errors = 5
        
    @property
    def platform_id(self) -> str:
        """Get platform identifier"""
        return self.config.platform_id
    
    @property
    def platform_name(self) -> str:
        """Get platform name"""
        return self.config.platform_name
    
    @property
    def platform_type(self) -> PlatformType:
        """Get platform type"""
        return self.config.platform_type
    
    @property
    def is_authenticated(self) -> bool:
        """Check if platform is authenticated"""
        return self.config.credentials.access_token is not None
    
    @property
    def is_active(self) -> bool:
        """Check if platform is active"""
        return self.status == PlatformStatus.ACTIVE
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    async def refresh_token(self) -> bool:
        """Refresh authentication token"""
        pass
    
    @abstractmethod
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload content to platform"""
        pass
    
    @abstractmethod
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get content analytics"""
        pass
    
    @abstractmethod
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on platform"""
        pass
    
    @abstractmethod
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's content from platform"""
        pass
    
    @abstractmethod
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from platform"""
        pass
    
    @abstractmethod
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update content metadata"""
        pass
    
    async def test_connection(self) -> bool:
        """Test platform connection"""
        try:
            if not self.is_authenticated:
                return await self.authenticate()
            
            # Basic API call to test connection
            result = await self.get_user_content()
            return result is not None
            
        except Exception as e:
            logger.error(f"Connection test failed for {self.platform_name}: {e}")
            return False
    
    async def handle_rate_limit(self, retry_after: int = None):
        """Handle rate limiting"""
        wait_time = retry_after or self.config.rate_limit
        logger.warning(f"Rate limited on {self.platform_name}, waiting {wait_time}s")
        await asyncio.sleep(wait_time)
    
    def increment_error_count(self):
        """Increment error count and update status"""
        self.error_count += 1
        if self.error_count >= self.max_errors:
            self.status = PlatformStatus.ERROR
            logger.error(f"Platform {self.platform_name} exceeded max errors")
    
    def reset_error_count(self):
        """Reset error count"""
        self.error_count = 0
        if self.status == PlatformStatus.ERROR:
            self.status = PlatformStatus.ACTIVE


class PlatformManager:
    """Manager for multiple platform integrations"""
    
    def __init__(self):
        """Initialize platform manager"""
        self.platforms: Dict[str, PlatformBase] = {}
        self.active_platforms: List[str] = []
        
    def register_platform(self, platform: PlatformBase):
        """Register a platform"""
        self.platforms[platform.platform_id] = platform
        logger.info(f"Registered platform: {platform.platform_name}")
    
    def unregister_platform(self, platform_id: str):
        """Unregister a platform"""
        if platform_id in self.platforms:
            del self.platforms[platform_id]
            if platform_id in self.active_platforms:
                self.active_platforms.remove(platform_id)
            logger.info(f"Unregistered platform: {platform_id}")
    
    def get_platform(self, platform_id: str) -> Optional[PlatformBase]:
        """Get platform by ID"""
        return self.platforms.get(platform_id)
    
    def get_platforms_by_type(self, platform_type: PlatformType) -> List[PlatformBase]:
        """Get platforms by type"""
        return [
            platform for platform in self.platforms.values()
            if platform.platform_type == platform_type
        ]
    
    def get_active_platforms(self) -> List[PlatformBase]:
        """Get active platforms"""
        return [
            platform for platform in self.platforms.values()
            if platform.is_active
        ]
    
    async def authenticate_all(self) -> Dict[str, bool]:
        """Authenticate all platforms"""
        results = {}
        for platform_id, platform in self.platforms.items():
            try:
                results[platform_id] = await platform.authenticate()
                if results[platform_id]:
                    platform.status = PlatformStatus.ACTIVE
                    if platform_id not in self.active_platforms:
                        self.active_platforms.append(platform_id)
            except Exception as e:
                logger.error(f"Authentication failed for {platform_id}: {e}")
                results[platform_id] = False
                platform.status = PlatformStatus.ERROR
        
        return results
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """Test all platform connections"""
        results = {}
        for platform_id, platform in self.platforms.items():
            results[platform_id] = await platform.test_connection()
        
        return results
    
    async def upload_to_platforms(
        self, 
        platform_ids: List[str], 
        content_path: str, 
        metadata: ContentMetadata
    ) -> Dict[str, UploadResult]:
        """Upload content to multiple platforms"""
        results = {}
        
        for platform_id in platform_ids:
            platform = self.get_platform(platform_id)
            if not platform:
                results[platform_id] = UploadResult(
                    success=False,
                    platform_id=platform_id,
                    error=f"Platform {platform_id} not found"
                )
                continue
            
            if not platform.is_active:
                results[platform_id] = UploadResult(
                    success=False,
                    platform_id=platform_id,
                    error=f"Platform {platform_id} is not active"
                )
                continue
            
            try:
                results[platform_id] = await platform.upload_content(content_path, metadata)
            except Exception as e:
                logger.error(f"Upload failed for {platform_id}: {e}")
                results[platform_id] = UploadResult(
                    success=False,
                    platform_id=platform_id,
                    error=str(e)
                )
                platform.increment_error_count()
        
        return results
    
    async def get_aggregated_analytics(
        self, 
        content_ids: Dict[str, str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, AnalyticsData]:
        """Get aggregated analytics from multiple platforms"""
        results = {}
        
        for platform_id, content_id in content_ids.items():
            platform = self.get_platform(platform_id)
            if not platform or not platform.is_active:
                continue
            
            try:
                results[platform_id] = await platform.get_analytics(
                    content_id, start_date, end_date
                )
            except Exception as e:
                logger.error(f"Analytics retrieval failed for {platform_id}: {e}")
                platform.increment_error_count()
        
        return results
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get platform manager statistics"""
        total_platforms = len(self.platforms)
        active_platforms = len(self.get_active_platforms())
        error_platforms = len([
            p for p in self.platforms.values() 
            if p.status == PlatformStatus.ERROR
        ])
        
        platform_types = {}
        for platform in self.platforms.values():
            ptype = platform.platform_type.value
            platform_types[ptype] = platform_types.get(ptype, 0) + 1
        
        return {
            'total_platforms': total_platforms,
            'active_platforms': active_platforms,
            'error_platforms': error_platforms,
            'platform_types': platform_types,
            'last_sync': max(
                [p.last_sync for p in self.platforms.values() if p.last_sync], 
                default=None
            )
        }
