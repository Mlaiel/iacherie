"""Platform Serializer Module
==========================

Specialized serialization for platform-specific data and API responses.
Optimized for multi-platform content distribution and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel (mlaiel@live.de). 
Any unauthorized copying, distribution, modification, or commercial use is STRICTLY PROHIBITED 
and will result in immediate legal action under German and International Copyright Law.

ZERO TOLERANCE POLICY: Anyone attempting to steal, copy, or misappropriate this code or concept 
will face severe legal consequences including but not limited to criminal charges, civil litigation, 
and substantial financial damages.

AUTHORIZED USE ONLY: Contact mlaiel@live.de for official licensing agreements.

Expertise combinée:
- Lead Developer IA: Architecture multi-plateforme intelligente
- Backend Senior: Intégrations API robustes et scalables
- ML Engineer: Algorithmes d'adaptation par plateforme
- DBA Expert: Optimisation des données multi-plateformes
- Sécurité: Protection des données sensibles cross-platform
- Microservices: Architecture distribuée multi-plateformes
- Audio/Vidéo: Adaptation formats par plateforme
- DevOps: Déploiement et monitoring multi-cloud
- IA Prompt Engineer: Optimisation de contenu par plateforme
"""
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel, Field, validator, HttpUrl

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported platform types."""
    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    SOCIAL_MEDIA = "social_media"
    IMAGE_SHARING = "image_sharing"
    PODCAST_PLATFORM = "podcast_platform"
    BLOG_PLATFORM = "blog_platform"
    MARKETPLACE = "marketplace"
    FILE_SHARING = "file_sharing"
    GENERIC_WEB = "generic_web"

class PlatformName(Enum):
    """Known platform names."""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    REDDIT = "reddit"
    TUMBLR = "tumblr"
    MEDIUM = "medium"
    WORDPRESS = "wordpress"
    BLOGGER = "blogger"
    DEVIANTART = "deviantart"
    FLICKR = "flickr"
    UNSPLASH = "unsplash"
    SHUTTERSTOCK = "shutterstock"
    GETTY_IMAGES = "getty_images"
    DROPBOX = "dropbox"
    GOOGLE_DRIVE = "google_drive"
    ONEDRIVE = "onedrive"
    WETRANSFER = "wetransfer"
    GENERIC = "generic"

class ApiVersion(Enum):
    """API version standards."""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    BETA = "beta"
    LATEST = "latest"
    DEPRECATED = "deprecated"

class AuthenticationType(Enum):
    """Authentication methods."""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    COOKIE_AUTH = "cookie_auth"
    SESSION_AUTH = "session_auth"
    NO_AUTH = "no_auth"

@dataclass
class PlatformLimits:
    """Platform API and content limits."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    max_file_size_mb: int = 100
    max_duration_seconds: int = 3600
    supported_formats: List[str] = field(default_factory=list)
    content_restrictions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlatformConfig:
    """Platform configuration and settings."""
    api_base_url: str
    api_version: ApiVersion
    authentication: AuthenticationType
    rate_limits: PlatformLimits
    endpoints: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_seconds: int = 1

@dataclass
class PlatformMetrics:
    """Platform performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    average_response_time_ms: float = 0.0
    error_rate: float = 0.0
    uptime_percentage: float = 100.0
    last_successful_request: Optional[datetime] = None
    last_error: Optional[str] = None

class PlatformData(BaseModel):
    """
    Comprehensive platform data model.
    
    Represents platform-specific content, metadata, and API responses
    for multi-platform content distribution and monitoring.
    """
    
    # Basic identification
    platform_id: str = Field(..., description="Unique platform record identifier")
    platform_name: PlatformName = Field(..., description="Platform name")
    platform_type: PlatformType = Field(..., description="Platform type")
    platform_url: HttpUrl = Field(..., description="Platform URL")
    
    # Content identification
    content_id: str = Field(..., description="Associated content identifier")
    platform_content_id: Optional[str] = Field(default=None, description="Platform-specific content ID")
    content_url: Optional[HttpUrl] = Field(default=None, description="Content URL on platform")
    
    # Platform-specific metadata
    platform_metadata: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific metadata")
    api_response_data: Dict[str, Any] = Field(default_factory=dict, description="Raw API response data")
    extracted_data: Dict[str, Any] = Field(default_factory=dict, description="Processed extracted data")
    
    # Content properties on platform
    title: Optional[str] = Field(default=None, description="Content title on platform")
    description: Optional[str] = Field(default=None, description="Content description")
    tags: List[str] = Field(default_factory=list, description="Platform tags")
    category: Optional[str] = Field(default=None, description="Platform category")
    
    # Creator/uploader information
    creator_name: Optional[str] = Field(default=None, description="Creator name on platform")
    creator_id: Optional[str] = Field(default=None, description="Creator ID on platform")
    creator_url: Optional[HttpUrl] = Field(default=None, description="Creator profile URL")
    creator_metadata: Dict[str, Any] = Field(default_factory=dict, description="Creator metadata")
    
    # Engagement metrics
    views: int = Field(default=0, description="View count")
    likes: int = Field(default=0, description="Like count")
    dislikes: int = Field(default=0, description="Dislike count")
    comments: int = Field(default=0, description="Comment count")
    shares: int = Field(default=0, description="Share count")
    downloads: int = Field(default=0, description="Download count")
    
    # Content status
    published: bool = Field(default=False, description="Content published status")
    published_at: Optional[datetime] = Field(default=None, description="Publication timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    visibility: str = Field(default="public", description="Content visibility")
    monetized: bool = Field(default=False, description="Monetization status")
    
    # Platform configuration
    platform_config: Optional[PlatformConfig] = Field(default=None, description="Platform configuration")
    sync_enabled: bool = Field(default=True, description="Sync enabled status")
    monitoring_enabled: bool = Field(default=True, description="Monitoring enabled")
    last_sync: Optional[datetime] = Field(default=None, description="Last sync timestamp")
    
    # Processing information
    extraction_method: str = Field(default="api", description="Data extraction method")
    extraction_status: str = Field(default="pending", description="Extraction status")
    processing_errors: List[str] = Field(default_factory=list, description="Processing errors")
    
    # Timestamps
    discovered_at: datetime = Field(default_factory=datetime.now, description="Discovery timestamp")
    last_checked: datetime = Field(default_factory=datetime.now, description="Last check timestamp")
    next_check: Optional[datetime] = Field(default=None, description="Next check timestamp")
    
    # Quality and verification
    data_quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Data quality score")
    verified: bool = Field(default=False, description="Data verification status")
    verification_method: Optional[str] = Field(default=None, description="Verification method")
    
    # Custom data
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom platform fields")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    
    @validator('platform_name', pre=True)
    def validate_platform_name(cls, v):
        if isinstance(v, str):
            return PlatformName(v.lower())
        return v
    
    @validator('platform_type', pre=True)
    def validate_platform_type(cls, v):
        if isinstance(v, str):
            return PlatformType(v.lower())
        return v
    
    @validator('visibility')
    def validate_visibility(cls, v):
        allowed_values = ['public', 'private', 'unlisted', 'restricted', 'members_only']
        if v.lower() not in allowed_values:
            raise ValueError(f"Invalid visibility value. Must be one of: {allowed_values}")
        return v.lower()

class PlatformSerializer:
    """
    Advanced platform data serialization system.
    
    Handles efficient serialization and deserialization of platform-specific data,
    API responses, and multi-platform content management for the IA-Influencer-Agent platform.
    """
    
    def __init__(self):
        """Initialize platform serializer."""
        self.platform_url_patterns = {
            PlatformName.YOUTUBE: r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)',
            PlatformName.SPOTIFY: r'spotify\.com/(?:track|album|playlist)/([a-zA-Z0-9_-]+)',
            PlatformName.SOUNDCLOUD: r'soundcloud\.com/([^/]+)/([^/?]+)',
            PlatformName.INSTAGRAM: r'instagram\.com/(?:p|reel)/([a-zA-Z0-9_-]+)',
            PlatformName.TIKTOK: r'tiktok\.com/@([^/]+)/video/(\d+)',
            PlatformName.TWITTER: r'twitter\.com/[^/]+/status/(\d+)',
            PlatformName.FACEBOOK: r'facebook\.com/[^/]+/(?:posts|videos)/(\d+)'
        }
        
        logger.info("Platform serializer initialized")
    
    def serialize_platform(
        self,
        platform: PlatformData,
        include_api_response: bool = False,
        include_config: bool = False,
        compact_metadata: bool = False
    ) -> Dict[str, Any]:
        """
        Serialize platform data to dictionary format.
        
        Args:
            platform: Platform data to serialize
            include_api_response: Whether to include raw API response
            include_config: Whether to include platform configuration
            compact_metadata: Whether to compact metadata
            
        Returns:
            Serialized platform dictionary
        """
        try:
            # Convert to dictionary
            data = platform.dict()
            
            # Handle datetime conversions
            data['discovered_at'] = platform.discovered_at.isoformat()
            data['last_checked'] = platform.last_checked.isoformat()
            
            if platform.published_at:
                data['published_at'] = platform.published_at.isoformat()
            
            if platform.updated_at:
                data['updated_at'] = platform.updated_at.isoformat()
            
            if platform.last_sync:
                data['last_sync'] = platform.last_sync.isoformat()
            
            if platform.next_check:
                data['next_check'] = platform.next_check.isoformat()
            
            # Handle URL conversions
            data['platform_url'] = str(platform.platform_url)
            if platform.content_url:
                data['content_url'] = str(platform.content_url)
            if platform.creator_url:
                data['creator_url'] = str(platform.creator_url)
            
            # Handle API response data
            if not include_api_response:
                data.pop('api_response_data', None)
            
            # Handle platform configuration
            if include_config and platform.platform_config:
                data['platform_config'] = self._serialize_platform_config(platform.platform_config)
            elif not include_config:
                data.pop('platform_config', None)
            
            # Compact metadata if requested
            if compact_metadata:
                data['platform_metadata'] = self._compact_metadata(data.get('platform_metadata', {}))
                data['extracted_data'] = self._compact_metadata(data.get('extracted_data', {}))
                data['creator_metadata'] = self._compact_metadata(data.get('creator_metadata', {}))
            
            # Convert enums
            data['platform_name'] = platform.platform_name.value
            data['platform_type'] = platform.platform_type.value
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_api_response': include_api_response,
                'includes_config': include_config,
                'metadata_compacted': compact_metadata,
                'platform_name': platform.platform_name.value
            }
            
            logger.debug(f"Serialized platform data {platform.platform_id}")
            return data
            
        except Exception as e:
            logger.error(f"Platform serialization failed: {e}")
            raise
    
    def deserialize_platform(
        self,
        data: Dict[str, Any]
    ) -> PlatformData:
        """
        Deserialize platform data from dictionary format.
        
        Args:
            data: Serialized platform dictionary
            
        Returns:
            Deserialized PlatformData object
        """
        try:
            # Handle datetime conversions
            datetime_fields = ['discovered_at', 'last_checked', 'published_at', 'updated_at', 'last_sync', 'next_check']
            
            for field in datetime_fields:
                if isinstance(data.get(field), str):
                    data[field] = datetime.fromisoformat(data[field])
            
            # Deserialize platform configuration
            if 'platform_config' in data and data['platform_config']:
                data['platform_config'] = self._deserialize_platform_config(data['platform_config'])
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            
            # Create PlatformData object
            platform = PlatformData(**data)
            
            logger.debug(f"Deserialized platform data {platform.platform_id}")
            return platform
            
        except Exception as e:
            logger.error(f"Platform deserialization failed: {e}")
            raise
    
    def serialize_platform_batch(
        self,
        platforms: List[PlatformData],
        compact_mode: bool = True
    ) -> List[Dict[str, Any]]:
        """Serialize multiple platform records efficiently."""
        try:
            serialized_list = []
            
            for platform in platforms:
                serialized = self.serialize_platform(
                    platform,
                    include_api_response=not compact_mode,
                    include_config=not compact_mode,
                    compact_metadata=compact_mode
                )
                serialized_list.append(serialized)
            
            logger.info(f"Serialized {len(platforms)} platform records")
            return serialized_list
            
        except Exception as e:
            logger.error(f"Platform batch serialization failed: {e}")
            raise
    
    def deserialize_platform_batch(
        self,
        data_list: List[Dict[str, Any]]
    ) -> List[PlatformData]:
        """Deserialize multiple platform records efficiently."""
        try:
            platforms = []
            
            for data in data_list:
                platform = self.deserialize_platform(data)
                platforms.append(platform)
            
            logger.info(f"Deserialized {len(data_list)} platform records")
            return platforms
            
        except Exception as e:
            logger.error(f"Platform batch deserialization failed: {e}")
            raise
    
    def _serialize_platform_config(
        self,
        config: PlatformConfig
    ) -> Dict[str, Any]:
        """Serialize platform configuration."""
        try:
            data = {
                'api_base_url': config.api_base_url,
                'api_version': config.api_version.value,
                'authentication': config.authentication.value,
                'endpoints': config.endpoints,
                'headers': config.headers,
                'parameters': config.parameters,
                'timeout_seconds': config.timeout_seconds,
                'retry_attempts': config.retry_attempts,
                'retry_delay_seconds': config.retry_delay_seconds
            }
            
            # Serialize rate limits
            data['rate_limits'] = {
                'requests_per_minute': config.rate_limits.requests_per_minute,
                'requests_per_hour': config.rate_limits.requests_per_hour,
                'requests_per_day': config.rate_limits.requests_per_day,
                'max_file_size_mb': config.rate_limits.max_file_size_mb,
                'max_duration_seconds': config.rate_limits.max_duration_seconds,
                'supported_formats': config.rate_limits.supported_formats,
                'content_restrictions': config.rate_limits.content_restrictions
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Platform config serialization failed: {e}")
            raise
    
    def _deserialize_platform_config(
        self,
        data: Dict[str, Any]
    ) -> PlatformConfig:
        """Deserialize platform configuration."""
        try:
            # Deserialize rate limits
            rate_limits_data = data.get('rate_limits', {})
            rate_limits = PlatformLimits(**rate_limits_data)
            
            # Handle enum conversions
            api_version = ApiVersion(data.get('api_version', 'v1'))
            authentication = AuthenticationType(data.get('authentication', 'api_key'))
            
            # Create config object
            config = PlatformConfig(
                api_base_url=data['api_base_url'],
                api_version=api_version,
                authentication=authentication,
                rate_limits=rate_limits,
                endpoints=data.get('endpoints', {}),
                headers=data.get('headers', {}),
                parameters=data.get('parameters', {}),
                timeout_seconds=data.get('timeout_seconds', 30),
                retry_attempts=data.get('retry_attempts', 3),
                retry_delay_seconds=data.get('retry_delay_seconds', 1)
            )
            
            return config
            
        except Exception as e:
            logger.error(f"Platform config deserialization failed: {e}")
            raise
    
    def _compact_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Compact metadata by removing large or unnecessary fields."""
        try:
            compacted = {}
            max_value_size = 10000  # 10KB limit for individual values
            
            for key, value in metadata.items():
                if isinstance(value, str) and len(value) > max_value_size:
                    # Truncate large strings
                    compacted[key] = value[:max_value_size] + "...[truncated]"
                elif isinstance(value, (list, dict)) and len(str(value)) > max_value_size:
                    # Skip large objects
                    compacted[key + "_size"] = len(str(value))
                    compacted[key + "_type"] = type(value).__name__
                else:
                    compacted[key] = value
            
            return compacted
            
        except Exception as e:
            logger.error(f"Metadata compaction failed: {e}")
            return metadata
    
    def extract_platform_content_id(
        self,
        url: str,
        platform_name: PlatformName
    ) -> Optional[str]:
        """Extract platform-specific content ID from URL."""
        try:
            pattern = self.platform_url_patterns.get(platform_name)
            if not pattern:
                return None
            
            match = re.search(pattern, url)
            if match:
                return match.group(1) if match.groups() else match.group(0)
            
            return None
            
        except Exception as e:
            logger.error(f"Content ID extraction failed: {e}")
            return None
    
    def normalize_platform_url(
        self,
        url: str,
        platform_name: PlatformName
    ) -> str:
        """Normalize platform URL to standard format."""
        try:
            parsed = urlparse(url)
            
            if platform_name == PlatformName.YOUTUBE:
                # Extract video ID and create standard URL
                video_id = self.extract_platform_content_id(url, platform_name)
                if video_id:
                    return f"https://www.youtube.com/watch?v={video_id}"
            
            elif platform_name == PlatformName.SPOTIFY:
                # Extract track/album/playlist ID
                content_id = self.extract_platform_content_id(url, platform_name)
                if content_id:
                    # Extract type from original URL
                    if '/track/' in url:
                        return f"https://open.spotify.com/track/{content_id}"
                    elif '/album/' in url:
                        return f"https://open.spotify.com/album/{content_id}"
                    elif '/playlist/' in url:
                        return f"https://open.spotify.com/playlist/{content_id}"
            
            elif platform_name == PlatformName.INSTAGRAM:
                # Extract post ID
                post_id = self.extract_platform_content_id(url, platform_name)
                if post_id:
                    return f"https://www.instagram.com/p/{post_id}/"
            
            # Return original URL if normalization not implemented
            return url
            
        except Exception as e:
            logger.error(f"URL normalization failed: {e}")
            return url
    
    def detect_platform_from_url(self, url: str) -> Optional[PlatformName]:
        """Detect platform from URL."""
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '')
            
            platform_domains = {
                'youtube.com': PlatformName.YOUTUBE,
                'youtu.be': PlatformName.YOUTUBE,
                'spotify.com': PlatformName.SPOTIFY,
                'soundcloud.com': PlatformName.SOUNDCLOUD,
                'instagram.com': PlatformName.INSTAGRAM,
                'tiktok.com': PlatformName.TIKTOK,
                'twitter.com': PlatformName.TWITTER,
                'facebook.com': PlatformName.FACEBOOK,
                'linkedin.com': PlatformName.LINKEDIN,
                'pinterest.com': PlatformName.PINTEREST,
                'twitch.tv': PlatformName.TWITCH,
                'vimeo.com': PlatformName.VIMEO,
                'reddit.com': PlatformName.REDDIT,
                'medium.com': PlatformName.MEDIUM,
                'bandcamp.com': PlatformName.BANDCAMP
            }
            
            return platform_domains.get(domain)
            
        except Exception as e:
            logger.error(f"Platform detection failed: {e}")
            return None
    
    def validate_platform_data(
        self,
        platform: PlatformData
    ) -> Dict[str, Any]:
        """Validate platform data integrity."""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Required field validation
            if not platform.platform_id:
                validation_result['errors'].append("Missing platform_id")
            
            if not platform.content_id:
                validation_result['errors'].append("Missing content_id")
            
            # URL validation
            try:
                parsed = urlparse(str(platform.platform_url))
                if not parsed.scheme or not parsed.netloc:
                    validation_result['errors'].append("Invalid platform_url format")
            except:
                validation_result['errors'].append("Invalid platform_url")
            
            # Content URL validation
            if platform.content_url:
                try:
                    parsed = urlparse(str(platform.content_url))
                    if not parsed.scheme or not parsed.netloc:
                        validation_result['errors'].append("Invalid content_url format")
                except:
                    validation_result['errors'].append("Invalid content_url")
            
            # Metric validation
            numeric_fields = ['views', 'likes', 'dislikes', 'comments', 'shares', 'downloads']
            for field in numeric_fields:
                value = getattr(platform, field, 0)
                if value < 0:
                    validation_result['errors'].append(f"Negative value for {field}")
            
            # Quality score validation
            if not 0.0 <= platform.data_quality_score <= 1.0:
                validation_result['errors'].append("Invalid data_quality_score range")
            
            # Platform consistency validation
            detected_platform = self.detect_platform_from_url(str(platform.platform_url))
            if detected_platform and detected_platform != platform.platform_name:
                validation_result['warnings'].append(
                    f"Platform name mismatch: {platform.platform_name.value} vs {detected_platform.value}"
                )
            
            # Set validation result
            validation_result['valid'] = len(validation_result['errors']) == 0
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Platform validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {e}"],
                'warnings': []
            }
    
    def create_platform_summary(
        self,
        platform: PlatformData
    ) -> Dict[str, Any]:
        """Create summary of platform data."""
        try:
            return {
                'platform_id': platform.platform_id,
                'platform_name': platform.platform_name.value,
                'platform_type': platform.platform_type.value,
                'content_id': platform.content_id,
                'title': platform.title,
                'creator_name': platform.creator_name,
                'published': platform.published,
                'published_at': platform.published_at.isoformat() if platform.published_at else None,
                'views': platform.views,
                'likes': platform.likes,
                'comments': platform.comments,
                'shares': platform.shares,
                'visibility': platform.visibility,
                'monetized': platform.monetized,
                'sync_enabled': platform.sync_enabled,
                'monitoring_enabled': platform.monitoring_enabled,
                'data_quality_score': platform.data_quality_score,
                'verified': platform.verified,
                'last_sync': platform.last_sync.isoformat() if platform.last_sync else None,
                'content_url': str(platform.content_url) if platform.content_url else None
            }
            
        except Exception as e:
            logger.error(f"Platform summary creation failed: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'PlatformSerializer',
    'PlatformData',
    'PlatformConfig',
    'PlatformLimits',
    'PlatformMetrics',
    'PlatformType',
    'PlatformName',
    'ApiVersion',
    'AuthenticationType'
]erializer Module
==========================

Specialized serialization for platform-specific data and API responses.
Optimized for multi-platform content aggregation and normalization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from urllib.parse import urlparse
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported platform types."""
    SOCIAL_MEDIA = "social_media"
    VIDEO_STREAMING = "video_streaming"
    AUDIO_STREAMING = "audio_streaming"
    LIVE_STREAMING = "live_streaming"
    PROFESSIONAL = "professional"
    E_COMMERCE = "e_commerce"
    BLOG = "blog"
    FORUM = "forum"
    NEWS = "news"
    OTHER = "other"

class PlatformCategory(Enum):
    """Platform categories."""
    ENTERTAINMENT = "entertainment"
    MUSIC = "music"
    EDUCATION = "education"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    LIFESTYLE = "lifestyle"
    NEWS = "news"
    GAMING = "gaming"
    SPORTS = "sports"
    GENERAL = "general"

class ContentFormat(Enum):
    """Content formats supported by platforms."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LIVE_VIDEO = "live_video"
    LIVE_AUDIO = "live_audio"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    PODCAST = "podcast"

@dataclass
class PlatformLimits:
    """Platform-specific content limits."""
    max_title_length: int = 200
    max_description_length: int = 5000
    max_tags: int = 30
    max_tag_length: int = 50
    max_file_size_mb: int = 100
    max_duration_seconds: int = 3600
    supported_formats: List[str] = field(default_factory=list)
    api_rate_limit: int = 100  # requests per hour

@dataclass
class PlatformMetrics:
    """Platform engagement metrics."""
    views: int = 0
    likes: int = 0
    dislikes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    downloads: int = 0
    followers: int = 0
    subscribers: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0

@dataclass
class PlatformAlgorithm:
    """Platform algorithm preferences."""
    prefers_engagement: bool = True
    prefers_retention: bool = True
    prefers_consistency: bool = True
    optimal_posting_times: List[str] = field(default_factory=list)
    trending_hashtags: List[str] = field(default_factory=list)
    algorithm_factors: Dict[str, float] = field(default_factory=dict)

class PlatformData(BaseModel):
    """
    Comprehensive platform data model.
    
    Represents platform-specific information, configurations,
    content formats, and API responses for the IA-Influencer-Agent platform.
    """
    
    # Platform identification
    platform_id: str = Field(..., description="Unique platform identifier")
    platform_name: str = Field(..., description="Platform name")
    platform_type: PlatformType = Field(..., description="Platform type")
    platform_category: PlatformCategory = Field(default=PlatformCategory.GENERAL)
    platform_url: str = Field(..., description="Platform base URL")
    
    # API configuration
    api_version: str = Field(default="v1", description="API version")
    api_endpoint: str = Field(..., description="API base endpoint")
    api_key_required: bool = Field(default=True)
    api_rate_limit: int = Field(default=100, description="Requests per hour")
    api_authentication_type: str = Field(default="oauth2")
    
    # Content configuration
    supported_formats: List[ContentFormat] = Field(default_factory=list)
    content_limits: PlatformLimits = Field(default_factory=PlatformLimits)
    upload_requirements: Dict[str, Any] = Field(default_factory=dict)
    
    # Platform features
    supports_live_streaming: bool = Field(default=False)
    supports_monetization: bool = Field(default=False)
    supports_analytics: bool = Field(default=False)
    supports_scheduling: bool = Field(default=False)
    supports_collaboration: bool = Field(default=False)
    
    # Algorithm and optimization
    algorithm_info: Optional[PlatformAlgorithm] = Field(default=None)
    seo_factors: List[str] = Field(default_factory=list)
    ranking_factors: Dict[str, float] = Field(default_factory=dict)
    
    # Content metadata structure
    metadata_schema: Dict[str, Any] = Field(default_factory=dict)
    required_fields: List[str] = Field(default_factory=list)
    optional_fields: List[str] = Field(default_factory=list)
    
    # Platform-specific data
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    platform_config: Dict[str, Any] = Field(default_factory=dict)
    crawler_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Status and monitoring
    active: bool = Field(default=True)
    last_crawled: Optional[datetime] = Field(default=None)
    crawl_frequency_minutes: int = Field(default=60)
    health_status: str = Field(default="unknown")
    
    # Statistics
    total_content_crawled: int = Field(default=0)
    violations_detected: int = Field(default=0)
    last_violation_detected: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('platform_type', pre=True)
    def validate_platform_type(cls, v):
        if isinstance(v, str):
            return PlatformType(v.lower())
        return v
    
    @validator('platform_category', pre=True)
    def validate_platform_category(cls, v):
        if isinstance(v, str):
            return PlatformCategory(v.lower())
        return v
    
    @validator('platform_url')
    def validate_platform_url(cls, v):
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid platform URL format")
        return v
    
    @validator('api_rate_limit')
    def validate_api_rate_limit(cls, v):
        if v <= 0:
            raise ValueError("API rate limit must be positive")
        return v

class PlatformSerializer:
    """
    Advanced platform data serialization system.
    
    Handles efficient serialization and deserialization of platform
    configurations, API responses, and metadata with format normalization.
    """
    
    def __init__(self):
        """Initialize platform serializer."""
        self.platform_configs = self._load_platform_configs()
        self.content_normalizers = self._init_content_normalizers()
        
        logger.info("Platform serializer initialized")
    
    def _load_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific configurations."""
        return {
            'youtube': {
                'api_endpoint': 'https://www.googleapis.com/youtube/v3',
                'content_limits': {
                    'max_title_length': 100,
                    'max_description_length': 5000,
                    'max_tags': 30,
                    'max_file_size_mb': 2048,
                    'max_duration_seconds': 43200  # 12 hours
                },
                'supported_formats': ['video', 'live_video', 'short'],
                'algorithm_factors': {
                    'watch_time': 0.4,
                    'click_through_rate': 0.25,
                    'engagement': 0.2,
                    'session_duration': 0.15
                }
            },
            'instagram': {
                'api_endpoint': 'https://graph.instagram.com',
                'content_limits': {
                    'max_title_length': 150,
                    'max_description_length': 2200,
                    'max_tags': 30,
                    'max_file_size_mb': 100,
                    'max_duration_seconds': 600  # 10 minutes for reels
                },
                'supported_formats': ['image', 'video', 'story', 'reel', 'live_video'],
                'algorithm_factors': {
                    'engagement': 0.35,
                    'relationship': 0.3,
                    'timeliness': 0.2,
                    'interest': 0.15
                }
            },
            'tiktok': {
                'api_endpoint': 'https://open-api.tiktok.com',
                'content_limits': {
                    'max_title_length': 150,
                    'max_description_length': 300,
                    'max_tags': 100,
                    'max_file_size_mb': 287,
                    'max_duration_seconds': 180  # 3 minutes
                },
                'supported_formats': ['video', 'live_video'],
                'algorithm_factors': {
                    'completion_rate': 0.4,
                    'engagement': 0.3,
                    'shares': 0.2,
                    'trending_sounds': 0.1
                }
            },
            'spotify': {
                'api_endpoint': 'https://api.spotify.com/v1',
                'content_limits': {
                    'max_title_length': 100,
                    'max_description_length': 1000,
                    'max_file_size_mb': 500,
                    'max_duration_seconds': 10800  # 3 hours
                },
                'supported_formats': ['audio', 'podcast'],
                'algorithm_factors': {
                    'completion_rate': 0.4,
                    'saves': 0.25,
                    'playlist_adds': 0.2,
                    'skip_rate': -0.15
                }
            }
        }
    
    def _init_content_normalizers(self) -> Dict[str, callable]:
        """Initialize content normalization functions."""
        return {
            'title': self._normalize_title,
            'description': self._normalize_description,
            'tags': self._normalize_tags,
            'url': self._normalize_url,
            'timestamp': self._normalize_timestamp,
            'metrics': self._normalize_metrics
        }
    
    def serialize_platform_data(
        self,
        platform_data: PlatformData,
        include_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        Serialize platform data to dictionary format.
        
        Args:
            platform_data: Platform data to serialize
            include_sensitive: Whether to include sensitive API data
            
        Returns:
            Serialized platform dictionary
        """
        try:
            # Convert to dictionary
            data = platform_data.dict()
            
            # Handle datetime conversions
            data['created_at'] = platform_data.created_at.isoformat()
            data['updated_at'] = platform_data.updated_at.isoformat()
            
            if platform_data.last_crawled:
                data['last_crawled'] = platform_data.last_crawled.isoformat()
            
            if platform_data.last_violation_detected:
                data['last_violation_detected'] = platform_data.last_violation_detected.isoformat()
            
            # Serialize complex objects
            if platform_data.content_limits:
                data['content_limits'] = self._serialize_platform_limits(platform_data.content_limits)
            
            if platform_data.algorithm_info:
                data['algorithm_info'] = self._serialize_platform_algorithm(platform_data.algorithm_info)
            
            # Convert enums
            data['platform_type'] = platform_data.platform_type.value
            data['platform_category'] = platform_data.platform_category.value
            data['supported_formats'] = [fmt.value for fmt in platform_data.supported_formats]
            
            # Handle sensitive data
            if not include_sensitive:
                # Remove sensitive fields
                sensitive_fields = ['api_key', 'access_token', 'refresh_token', 'client_secret']
                for field in sensitive_fields:
                    data.get('platform_config', {}).pop(field, None)
                    data.get('crawler_config', {}).pop(field, None)
                    data.get('custom_fields', {}).pop(field, None)
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_sensitive': include_sensitive,
                'platform_type': platform_data.platform_type.value
            }
            
            logger.debug(f"Serialized platform data for {platform_data.platform_name}")
            return data
            
        except Exception as e:
            logger.error(f"Platform data serialization failed: {e}")
            raise
    
    def deserialize_platform_data(
        self,
        data: Dict[str, Any]
    ) -> PlatformData:
        """
        Deserialize platform data from dictionary format.
        
        Args:
            data: Serialized platform dictionary
            
        Returns:
            Deserialized PlatformData object
        """
        try:
            # Handle datetime conversions
            if isinstance(data.get('created_at'), str):
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            
            if isinstance(data.get('updated_at'), str):
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            
            if isinstance(data.get('last_crawled'), str):
                data['last_crawled'] = datetime.fromisoformat(data['last_crawled'])
            
            if isinstance(data.get('last_violation_detected'), str):
                data['last_violation_detected'] = datetime.fromisoformat(data['last_violation_detected'])
            
            # Deserialize complex objects
            if 'content_limits' in data and data['content_limits']:
                data['content_limits'] = self._deserialize_platform_limits(data['content_limits'])
            
            if 'algorithm_info' in data and data['algorithm_info']:
                data['algorithm_info'] = self._deserialize_platform_algorithm(data['algorithm_info'])
            
            # Convert enum values
            if isinstance(data.get('platform_type'), str):
                data['platform_type'] = PlatformType(data['platform_type'])
            
            if isinstance(data.get('platform_category'), str):
                data['platform_category'] = PlatformCategory(data['platform_category'])
            
            if 'supported_formats' in data:
                data['supported_formats'] = [
                    ContentFormat(fmt) if isinstance(fmt, str) else fmt
                    for fmt in data['supported_formats']
                ]
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            
            # Create PlatformData object
            platform_data = PlatformData(**data)
            
            logger.debug(f"Deserialized platform data for {platform_data.platform_name}")
            return platform_data
            
        except Exception as e:
            logger.error(f"Platform data deserialization failed: {e}")
            raise
    
    def normalize_platform_content(
        self,
        content: Dict[str, Any],
        platform_name: str
    ) -> Dict[str, Any]:
        """
        Normalize content from platform-specific format to standard format.
        
        Args:
            content: Raw platform content
            platform_name: Source platform name
            
        Returns:
            Normalized content dictionary
        """
        try:
            normalized = {}
            
            # Apply platform-specific normalization
            if platform_name.lower() == 'youtube':
                normalized = self._normalize_youtube_content(content)
            elif platform_name.lower() == 'instagram':
                normalized = self._normalize_instagram_content(content)
            elif platform_name.lower() == 'tiktok':
                normalized = self._normalize_tiktok_content(content)
            elif platform_name.lower() == 'spotify':
                normalized = self._normalize_spotify_content(content)
            else:
                normalized = self._normalize_generic_content(content)
            
            # Apply common normalizations
            for field, normalizer in self.content_normalizers.items():
                if field in normalized:
                    normalized[field] = normalizer(normalized[field])
            
            # Add normalization metadata
            normalized['_normalization'] = {
                'source_platform': platform_name,
                'normalized_at': datetime.now().isoformat(),
                'version': '2.0.0'
            }
            
            logger.debug(f"Normalized content from {platform_name}")
            return normalized
            
        except Exception as e:
            logger.error(f"Content normalization failed for {platform_name}: {e}")
            return content  # Return original if normalization fails
    
    def _normalize_youtube_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize YouTube content."""
        normalized = {
            'id': content.get('id', {}).get('videoId') or content.get('id'),
            'title': content.get('snippet', {}).get('title', ''),
            'description': content.get('snippet', {}).get('description', ''),
            'thumbnail': content.get('snippet', {}).get('thumbnails', {}).get('high', {}).get('url'),
            'published_at': content.get('snippet', {}).get('publishedAt'),
            'channel_id': content.get('snippet', {}).get('channelId'),
            'channel_title': content.get('snippet', {}).get('channelTitle'),
            'tags': content.get('snippet', {}).get('tags', []),
            'category_id': content.get('snippet', {}).get('categoryId'),
            'duration': content.get('contentDetails', {}).get('duration'),
            'view_count': int(content.get('statistics', {}).get('viewCount', 0)),
            'like_count': int(content.get('statistics', {}).get('likeCount', 0)),
            'comment_count': int(content.get('statistics', {}).get('commentCount', 0)),
            'url': f"https://www.youtube.com/watch?v={content.get('id')}"
        }
        return normalized
    
    def _normalize_instagram_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Instagram content."""
        normalized = {
            'id': content.get('id'),
            'title': content.get('caption', '')[:100],  # First 100 chars as title
            'description': content.get('caption', ''),
            'thumbnail': content.get('media_url'),
            'published_at': content.get('timestamp'),
            'media_type': content.get('media_type'),
            'like_count': content.get('like_count', 0),
            'comments_count': content.get('comments_count', 0),
            'permalink': content.get('permalink'),
            'url': content.get('permalink')
        }
        return normalized
    
    def _normalize_tiktok_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize TikTok content."""
        normalized = {
            'id': content.get('id'),
            'title': content.get('desc', '')[:100],  # First 100 chars as title
            'description': content.get('desc', ''),
            'thumbnail': content.get('video', {}).get('cover'),
            'published_at': content.get('createTime'),
            'author': content.get('author', {}).get('uniqueId'),
            'duration': content.get('video', {}).get('duration'),
            'view_count': content.get('stats', {}).get('playCount', 0),
            'like_count': content.get('stats', {}).get('diggCount', 0),
            'comment_count': content.get('stats', {}).get('commentCount', 0),
            'share_count': content.get('stats', {}).get('shareCount', 0),
            'url': f"https://www.tiktok.com/@{content.get('author', {}).get('uniqueId')}/video/{content.get('id')}"
        }
        return normalized
    
    def _normalize_spotify_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Spotify content."""
        normalized = {
            'id': content.get('id'),
            'title': content.get('name', ''),
            'description': content.get('description', ''),
            'thumbnail': content.get('images', [{}])[0].get('url') if content.get('images') else None,
            'published_at': content.get('release_date'),
            'artists': [artist.get('name') for artist in content.get('artists', [])],
            'album': content.get('album', {}).get('name'),
            'duration': content.get('duration_ms'),
            'popularity': content.get('popularity', 0),
            'preview_url': content.get('preview_url'),
            'url': content.get('external_urls', {}).get('spotify')
        }
        return normalized
    
    def _normalize_generic_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize generic platform content."""
        # Basic normalization for unknown platforms
        normalized = {
            'id': content.get('id') or content.get('_id') or content.get('identifier'),
            'title': content.get('title') or content.get('name') or content.get('headline'),
            'description': content.get('description') or content.get('content') or content.get('text'),
            'url': content.get('url') or content.get('link') or content.get('permalink'),
            'published_at': content.get('published_at') or content.get('created_at') or content.get('timestamp'),
            'author': content.get('author') or content.get('creator') or content.get('user'),
            'raw_data': content  # Preserve original data
        }
        return normalized
    
    def _normalize_title(self, title: Any) -> str:
        """Normalize content title."""
        if not title:
            return ""
        
        title = str(title).strip()
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title)
        # Remove special characters that might cause issues
        title = re.sub(r'[^\w\s\-\.\,\!\?\:\;]', '', title)
        
        return title[:200]  # Truncate to reasonable length
    
    def _normalize_description(self, description: Any) -> str:
        """Normalize content description."""
        if not description:
            return ""
        
        description = str(description).strip()
        # Normalize line breaks
        description = re.sub(r'\r\n|\r|\n', '\n', description)
        # Remove excessive whitespace
        description = re.sub(r' +', ' ', description)
        
        return description[:5000]  # Truncate to reasonable length
    
    def _normalize_tags(self, tags: Any) -> List[str]:
        """Normalize content tags."""
        if not tags:
            return []
        
        if isinstance(tags, str):
            # Split string tags
            tags = re.split(r'[,;#\s]+', tags)
        
        normalized_tags = []
        for tag in tags:
            if tag:
                tag = str(tag).strip().lower()
                tag = re.sub(r'[^\w\-]', '', tag)
                if tag and len(tag) <= 50:
                    normalized_tags.append(tag)
        
        return normalized_tags[:30]  # Limit number of tags
    
    def _normalize_url(self, url: Any) -> str:
        """Normalize content URL."""
        if not url:
            return ""
        
        url = str(url).strip()
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            if url.startswith('//'):
                url = 'https:' + url
            elif not url.startswith('/'):
                url = 'https://' + url
        
        return url
    
    def _normalize_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """Normalize timestamp to datetime object."""
        if not timestamp:
            return None
        
        try:
            if isinstance(timestamp, datetime):
                return timestamp
            elif isinstance(timestamp, str):
                # Try different timestamp formats
                for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                    try:
                        return datetime.strptime(timestamp, fmt)
                    except ValueError:
                        continue
                # Try ISO format
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, (int, float)):
                # Unix timestamp
                return datetime.fromtimestamp(timestamp)
        except Exception:
            pass
        
        return None
    
    def _normalize_metrics(self, metrics: Any) -> Dict[str, int]:
        """Normalize engagement metrics."""
        normalized = {
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0
        }
        
        if not metrics or not isinstance(metrics, dict):
            return normalized
        
        # Map common metric names
        metric_mappings = {
            'view_count': 'views',
            'viewCount': 'views',
            'playCount': 'views',
            'like_count': 'likes',
            'likeCount': 'likes',
            'diggCount': 'likes',
            'comment_count': 'comments',
            'commentCount': 'comments',
            'commentsCount': 'comments',
            'share_count': 'shares',
            'shareCount': 'shares'
        }
        
        for key, value in metrics.items():
            if key in metric_mappings:
                try:
                    normalized[metric_mappings[key]] = int(value or 0)
                except (ValueError, TypeError):
                    pass
        
        return normalized
    
    def _serialize_platform_limits(self, limits: PlatformLimits) -> Dict[str, Any]:
        """Serialize platform limits."""
        return {
            'max_title_length': limits.max_title_length,
            'max_description_length': limits.max_description_length,
            'max_tags': limits.max_tags,
            'max_tag_length': limits.max_tag_length,
            'max_file_size_mb': limits.max_file_size_mb,
            'max_duration_seconds': limits.max_duration_seconds,
            'supported_formats': limits.supported_formats,
            'api_rate_limit': limits.api_rate_limit
        }
    
    def _deserialize_platform_limits(self, data: Dict[str, Any]) -> PlatformLimits:
        """Deserialize platform limits."""
        return PlatformLimits(**data)
    
    def _serialize_platform_algorithm(self, algorithm: PlatformAlgorithm) -> Dict[str, Any]:
        """Serialize platform algorithm info."""
        return {
            'prefers_engagement': algorithm.prefers_engagement,
            'prefers_retention': algorithm.prefers_retention,
            'prefers_consistency': algorithm.prefers_consistency,
            'optimal_posting_times': algorithm.optimal_posting_times,
            'trending_hashtags': algorithm.trending_hashtags,
            'algorithm_factors': algorithm.algorithm_factors
        }
    
    def _deserialize_platform_algorithm(self, data: Dict[str, Any]) -> PlatformAlgorithm:
        """Deserialize platform algorithm info."""
        return PlatformAlgorithm(**data)


# Export main classes
__all__ = [
    'PlatformSerializer',
    'PlatformData',
    'PlatformType',
    'PlatformCategory',
    'ContentFormat',
    'PlatformLimits',
    'PlatformMetrics',
    'PlatformAlgorithm'
]
