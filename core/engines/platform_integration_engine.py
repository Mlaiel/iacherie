"""Platform Integration Engine - IA-Influencer-Agent
================================================================================

Module: backend/core/engines/platform_integration_engine.py
Architecture: IA-Influencer-Agent Backend (Level 3)
Created: 2025-08-19
Team: Lead Dev IA + Backend Senior + API Integration Expert

MISSION: Multi-platform content distribution and analytics integration
MÉTIER: Content creation → Platform APIs → Distribution → Analytics aggregation

Author: Fahed Mlaiel <mlaiel@live.de>
COPYRIGHT WARNING: This code is proprietary. Unauthorized use, copying, or 
redistribution without explicit written permission from Fahed Mlaiel is 
strictly prohibited and will result in legal action.
================================================================================
"""

import logging
import asyncio
import json
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import base64
from urllib.parse import urlencode
import mimetypes

# Internal imports
from ..database.models import PlatformConnection, ContentDistribution
from ..utils.metrics import MetricsCollector
from ..cache.redis_manager import RedisManager
from ..security.crypto_manager import CryptoManager
from ..storage.file_manager import FileManager

logger = logging.getLogger(__name__)


class Platform(str, Enum):
    """
Supported social media platforms"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    DISCORD = "discord"


class ContentFormat(str, Enum):
    """Content formats for distribution"""

    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"


class DistributionStatus(str, Enum):
    """Content distribution status"""

    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"


@dataclass
class PlatformCredentials:
    """Platform authentication credentials"""
    platform: Platform
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    additional_data: Dict[str, Any] = None


@dataclass
class ContentMetadata:
    """
Content metadata for distribution"""
    title: str
    description: str
    tags: List[str]
    category: Optional[str] = None
    privacy_level: str = "public"
    thumbnail_url: Optional[str] = None
    custom_metadata: Dict[str, Any] = None


@dataclass
class DistributionResult:
    """Content distribution result"""
    platform: Platform
    platform_content_id: str
    content_url: str
    status: DistributionStatus
    upload_time: datetime
    metrics: Dict[str, Any] = None
    error_message: Optional[str] = None


@dataclass
class PlatformAnalytics:
    """
Platform analytics data"""
    platform: Platform
    content_id: str
    views: int
    likes: int
    comments: int
    shares: int
    engagement_rate: float
    reach: int
    impressions: int
    revenue: float = 0.0
    additional_metrics: Dict[str, Any] = None


class PlatformIntegrationEngine:
    """
    Enterprise platform integration engine for multi-platform content distribution
    
    Features:
    - Multi-platform OAuth authentication
    - Automated content distribution
    - Real-time analytics aggregation
    - Content format optimization
    - Scheduling and publishing
    - Cross-platform analytics
    """
    
    def __init__(
        self,
        redis_manager: RedisManager,
        metrics_collector: MetricsCollector,
        crypto_manager: CryptoManager,
        file_manager: FileManager,
        config: Dict[str, Any] = None
    ):
        self.redis_manager = redis_manager
        self.metrics_collector = metrics_collector
        self.crypto_manager = crypto_manager
        self.file_manager = file_manager
        self.config = config or {}
        
        # Platform configurations
        self.platform_configs = self._load_platform_configs()
        
        # HTTP session with retry logic
        self.session_timeout = aiohttp.ClientTimeout(total=300)
        
        # Cache settings
        self.cache_ttl = self.config.get("cache_ttl", 3600)
        
        # Rate limiting
        self.rate_limits = {
            Platform.YOUTUBE: 100,    # requests per minute
            Platform.INSTAGRAM: 200,
            Platform.TIKTOK: 100,
            Platform.SPOTIFY: 100,
            Platform.FACEBOOK: 200,
            Platform.TWITTER: 300
        }
        
        logger.info("PlatformIntegrationEngine initialized successfully")

    def _load_platform_configs(self) -> Dict[Platform, Dict[str, Any]]:
        """Load API configurations for each platform"""
        return {
            Platform.YOUTUBE: {
                "auth_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "api_base": "https://www.googleapis.com/youtube/v3",
                "upload_url": "https://www.googleapis.com/upload/youtube/v3/videos",
                "scopes": [
                    "https://www.googleapis.com/auth/youtube.upload",
                    "https://www.googleapis.com/auth/youtube.readonly"
                ],
                "max_file_size": 128 * 1024 * 1024 * 1024,  # 128GB
                "supported_formats": [".mp4", ".mov", ".avi", ".wmv", ".flv", ".webm"]
            },
            Platform.INSTAGRAM: {
                "auth_url": "https://api.instagram.com/oauth/authorize",
                "token_url": "https://api.instagram.com/oauth/access_token",
                "api_base": "https://graph.instagram.com",
                "scopes": ["user_profile", "user_media"],
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "supported_formats": [".jpg", ".jpeg", ".png", ".mp4"]
            },
            Platform.TIKTOK: {
                "auth_url": "https://www.tiktok.com/auth/authorize/",
                "token_url": "https://open-api.tiktok.com/oauth/access_token/",
                "api_base": "https://open-api.tiktok.com",
                "scopes": ["user.info.basic", "video.upload"],
                "max_file_size": 500 * 1024 * 1024,  # 500MB
                "supported_formats": [".mp4", ".mov"]
            },
            Platform.SPOTIFY: {
                "auth_url": "https://accounts.spotify.com/authorize",
                "token_url": "https://accounts.spotify.com/api/token",
                "api_base": "https://api.spotify.com/v1",
                "scopes": ["user-read-private", "user-read-email"],
                "max_file_size": 50 * 1024 * 1024,  # 50MB
                "supported_formats": [".mp3", ".wav", ".flac"]
            },
            Platform.FACEBOOK: {
                "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
                "api_base": "https://graph.facebook.com/v18.0",
                "scopes": ["pages_manage_posts", "pages_read_engagement"],
                "max_file_size": 4 * 1024 * 1024 * 1024,  # 4GB
                "supported_formats": [".mp4", ".mov", ".jpg", ".png"]
            },
            Platform.TWITTER: {
                "auth_url": "https://twitter.com/i/oauth2/authorize",
                "token_url": "https://api.twitter.com/2/oauth2/token",
                "api_base": "https://api.twitter.com/2",
                "scopes": ["tweet.read", "tweet.write", "users.read"],
                "max_file_size": 512 * 1024 * 1024,  # 512MB
                "supported_formats": [".mp4", ".gif", ".jpg", ".png"]
            }
        }

    async def authenticate_platform(
        self,
        platform: Platform,
        auth_code: str,
        redirect_uri: str,
        user_id: str
    ) -> PlatformCredentials:
        """
        Authenticate user with platform using OAuth flow
        
        Args:
            platform: Platform to authenticate
            auth_code: Authorization code from OAuth callback
            redirect_uri: OAuth redirect URI
            user_id: User identifier
            
        Returns:
            Platform credentials
        """
        try:
            config = self.platform_configs[platform]
            
            # Exchange authorization code for access token
            token_data = await self._exchange_auth_code(
                platform, auth_code, redirect_uri
            )
            
            # Create credentials object
            credentials = PlatformCredentials(
                platform=platform,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_expires_at=self._calculate_token_expiry(token_data),
                client_id=self.config.get(f"{platform.value}_client_id"),
                client_secret=self.config.get(f"{platform.value}_client_secret"),
                additional_data=token_data
            )
            
            # Encrypt and store credentials
            await self._store_platform_credentials(user_id, credentials)
            
            # Test connection
            await self._test_platform_connection(credentials)
            
            # Update metrics
            self.metrics_collector.increment_counter(
                "platform_authentications",
                tags={"platform": platform.value}
            )
            
            logger.info(f"Platform authentication successful: {platform.value} for user {user_id}")
            return credentials
            
        except Exception as e:
            logger.error(f"Platform authentication failed: {e}")
            raise

    async def _exchange_auth_code(
        self,
        platform: Platform,
        auth_code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            config = self.platform_configs[platform]
            
            data = {
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": redirect_uri,
                "client_id": self.config.get(f"{platform.value}_client_id"),
                "client_secret": self.config.get(f"{platform.value}_client_secret")
            }
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.post(config["token_url"], data=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"Token exchange failed: {response.status} - {error_text}")
                        raise Exception(f"Token exchange failed: {response.status}")
            
        except Exception as e:
            logger.error(f"Auth code exchange failed: {e}")
            raise

    def _calculate_token_expiry(self, token_data: Dict[str, Any]) -> Optional[datetime]:
        """Calculate token expiry time"""
        expires_in = token_data.get("expires_in")
        if expires_in:
            return datetime.now() + timedelta(seconds=int(expires_in))
        return None

    async def distribute_content(
        self,
        content_path: str,
        content_format: ContentFormat,
        metadata: ContentMetadata,
        target_platforms: List[Platform],
        user_id: str,
        schedule_time: Optional[datetime] = None
    ) -> List[DistributionResult]:
        """
        Distribute content to multiple platforms
        
        Args:
            content_path: Path to content file
            content_format: Content format type
            metadata: Content metadata
            target_platforms: Platforms to distribute to
            user_id: Content owner
            schedule_time: Optional scheduling time
            
        Returns:
            List of distribution results
        """
        try:
            distribution_results = []
            
            # Validate content file
            if not await self.file_manager.file_exists(content_path):
                raise FileNotFoundError(f"Content file not found: {content_path}")
            
            # Process each platform
            distribution_tasks = []
            for platform in target_platforms:
                task = self._distribute_to_platform(
                    content_path,
                    content_format,
                    metadata,
                    platform,
                    user_id,
                    schedule_time
                )
                distribution_tasks.append(task)
            
            # Execute distributions in parallel
            results = await asyncio.gather(*distribution_tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                platform = target_platforms[i]
                if isinstance(result, Exception):
                    logger.error(f"Distribution to {platform.value} failed: {result}")
                    distribution_results.append(DistributionResult(
                        platform=platform,
                        platform_content_id="",
                        content_url="",
                        status=DistributionStatus.FAILED,
                        upload_time=datetime.now(),
                        error_message=str(result)
                    ))
                else:
                    distribution_results.append(result)
            
            # Store distribution records
            await self._store_distribution_records(distribution_results, user_id)
            
            # Update metrics
            successful_distributions = [r for r in distribution_results if r.status == DistributionStatus.PUBLISHED]
            self.metrics_collector.increment_counter(
                "content_distributions",
                len(successful_distributions),
                tags={"format": content_format.value}
            )
            
            logger.info(f"Content distributed to {len(successful_distributions)}/{len(target_platforms)} platforms")
            return distribution_results
            
        except Exception as e:
            logger.error(f"Content distribution failed: {e}")
            raise

    async def _distribute_to_platform(
        self,
        content_path: str,
        content_format: ContentFormat,
        metadata: ContentMetadata,
        platform: Platform,
        user_id: str,
        schedule_time: Optional[datetime] = None
    ) -> DistributionResult:
        """Distribute content to specific platform"""
        try:
            # Get platform credentials
            credentials = await self._get_platform_credentials(user_id, platform)
            if not credentials:
                raise ValueError(f"No credentials found for platform: {platform.value}")
            
            # Refresh token if needed
            credentials = await self._refresh_token_if_needed(credentials)
            
            # Validate content format for platform
            await self._validate_content_for_platform(content_path, content_format, platform)
            
            # Platform-specific distribution
            if platform == Platform.YOUTUBE:
                return await self._upload_to_youtube(content_path, metadata, credentials)
            elif platform == Platform.INSTAGRAM:
                return await self._upload_to_instagram(content_path, metadata, credentials)
            elif platform == Platform.TIKTOK:
                return await self._upload_to_tiktok(content_path, metadata, credentials)
            elif platform == Platform.FACEBOOK:
                return await self._upload_to_facebook(content_path, metadata, credentials)
            elif platform == Platform.TWITTER:
                return await self._upload_to_twitter(content_path, metadata, credentials)
            else:
                raise ValueError(f"Platform not supported: {platform.value}")
            
        except Exception as e:
            logger.error(f"Platform distribution failed for {platform.value}: {e}")
            raise

    async def _upload_to_youtube(
        self,
        content_path: str,
        metadata: ContentMetadata,
        credentials: PlatformCredentials
    ) -> DistributionResult:
        """Upload video to YouTube"""
        try:
            config = self.platform_configs[Platform.YOUTUBE]
            
            # Prepare video metadata
            video_metadata = {
                "snippet": {
                    "title": metadata.title,
                    "description": metadata.description,
                    "tags": metadata.tags,
                    "categoryId": metadata.category or "22"  # People & Blogs
                },
                "status": {
                    "privacyStatus": metadata.privacy_level
                }
            }
            
            # Upload video using resumable upload
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            # First, initiate upload session
            upload_url = f"{config['upload_url']}?uploadType=resumable&part=snippet,status"
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.post(
                    upload_url,
                    headers=headers,
                    json=video_metadata
                ) as response:
                    if response.status == 200:
                        upload_session_url = response.headers.get("Location")
                    else:
                        error_text = await response.text()
                        raise Exception(f"YouTube upload initiation failed: {error_text}")
                
                # Upload video file
                async with aiofiles.open(content_path, 'rb') as f:
                    video_data = await f.read()
                
                upload_headers = {
                    "Content-Type": "video/*",
                    "Content-Length": str(len(video_data))
                }
                
                async with session.put(
                    upload_session_url,
                    headers=upload_headers,
                    data=video_data
                ) as response:
                    if response.status == 200:
                        upload_result = await response.json()
                        video_id = upload_result["id"]
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        return DistributionResult(
                            platform=Platform.YOUTUBE,
                            platform_content_id=video_id,
                            content_url=video_url,
                            status=DistributionStatus.PUBLISHED,
                            upload_time=datetime.now()
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"YouTube video upload failed: {error_text}")
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            raise

    async def _upload_to_instagram(
        self,
        content_path: str,
        metadata: ContentMetadata,
        credentials: PlatformCredentials
    ) -> DistributionResult:
        """Upload content to Instagram"""
        try:
            config = self.platform_configs[Platform.INSTAGRAM]
            
            # Get user's Instagram account ID
            headers = {
                "Authorization": f"Bearer {credentials.access_token}"
            }
            
            # First, get user info
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.get(
                    f"{config['api_base']}/me",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        account_id = user_data["id"]
                    else:
                        raise Exception("Failed to get Instagram account info")
                
                # Upload media
                upload_url = f"{config['api_base']}/{account_id}/media"
                
                # Read file and convert to base64
                async with aiofiles.open(content_path, 'rb') as f:
                    file_data = await f.read()
                
                file_b64 = base64.b64encode(file_data).decode('utf-8')
                
                upload_data = {
                    "image_url": f"data:image/jpeg;base64,{file_b64}",
                    "caption": f"{metadata.title}\n\n{metadata.description}",
                    "access_token": credentials.access_token
                }
                
                async with session.post(upload_url, data=upload_data) as response:
                    if response.status == 200:
                        upload_result = await response.json()
                        media_id = upload_result["id"]
                        
                        # Publish the media
                        publish_url = f"{config['api_base']}/{account_id}/media_publish"
                        publish_data = {
                            "creation_id": media_id,
                            "access_token": credentials.access_token
                        }
                        
                        async with session.post(publish_url, data=publish_data) as publish_response:
                            if publish_response.status == 200:
                                publish_result = await publish_response.json()
                                post_id = publish_result["id"]
                                
                                return DistributionResult(
                                    platform=Platform.INSTAGRAM,
                                    platform_content_id=post_id,
                                    content_url=f"https://www.instagram.com/p/{post_id}/",
                                    status=DistributionStatus.PUBLISHED,
                                    upload_time=datetime.now()
                                )
                            else:
                                error_text = await publish_response.text()
                                raise Exception(f"Instagram publish failed: {error_text}")
                    else:
                        error_text = await response.text()
                        raise Exception(f"Instagram upload failed: {error_text}")
            
        except Exception as e:
            logger.error(f"Instagram upload failed: {e}")
            raise

    async def _upload_to_tiktok(
        self,
        content_path: str,
        metadata: ContentMetadata,
        credentials: PlatformCredentials
    ) -> DistributionResult:
        """Upload video to TikTok"""
        try:
            config = self.platform_configs[Platform.TIKTOK]
            
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            # Initiate video upload
            upload_init_url = f"{config['api_base']}/video/init/"
            init_data = {
                "post_info": {
                    "title": metadata.title,
                    "description": metadata.description,
                    "privacy_level": metadata.privacy_level.upper(),
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": await self._get_file_size(content_path)
                }
            }
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.post(
                    upload_init_url,
                    headers=headers,
                    json=init_data
                ) as response:
                    if response.status == 200:
                        init_result = await response.json()
                        upload_url = init_result["data"]["upload_url"]
                        publish_id = init_result["data"]["publish_id"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"TikTok upload init failed: {error_text}")
                
                # Upload video file
                async with aiofiles.open(content_path, 'rb') as f:
                    video_data = await f.read()
                
                upload_headers = {
                    "Content-Type": "video/mp4",
                    "Content-Range": f"bytes 0-{len(video_data)-1}/{len(video_data)}"
                }
                
                async with session.put(
                    upload_url,
                    headers=upload_headers,
                    data=video_data
                ) as response:
                    if response.status == 200:
                        return DistributionResult(
                            platform=Platform.TIKTOK,
                            platform_content_id=publish_id,
                            content_url=f"https://www.tiktok.com/@user/video/{publish_id}",
                            status=DistributionStatus.PUBLISHED,
                            upload_time=datetime.now()
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"TikTok video upload failed: {error_text}")
            
        except Exception as e:
            logger.error(f"TikTok upload failed: {e}")
            raise

    async def _upload_to_facebook(
        self,
        content_path: str,
        metadata: ContentMetadata,
        credentials: PlatformCredentials
    ) -> DistributionResult:
        """Upload content to Facebook"""
        try:
            config = self.platform_configs[Platform.FACEBOOK]
            
            # Get page access token (assuming user manages a page)
            headers = {
                "Authorization": f"Bearer {credentials.access_token}"
            }
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                # Get user's pages
                async with session.get(
                    f"{config['api_base']}/me/accounts",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        pages_data = await response.json()
                        if pages_data["data"]:
                            page = pages_data["data"][0]  # Use first page
                            page_id = page["id"]
                            page_token = page["access_token"]
                        else:
                            raise Exception("No Facebook pages found")
                    else:
                        raise Exception("Failed to get Facebook pages")
                
                # Upload video
                upload_url = f"{config['api_base']}/{page_id}/videos"
                
                # Read video file
                async with aiofiles.open(content_path, 'rb') as f:
                    video_data = await f.read()
                
                form_data = aiohttp.FormData()
                form_data.add_field('access_token', page_token)
                form_data.add_field('title', metadata.title)
                form_data.add_field('description', metadata.description)
                form_data.add_field('published', 'true')
                form_data.add_field('source', video_data, filename='video.mp4', content_type='video/mp4')
                
                async with session.post(upload_url, data=form_data) as response:
                    if response.status == 200:
                        upload_result = await response.json()
                        video_id = upload_result["id"]
                        
                        return DistributionResult(
                            platform=Platform.FACEBOOK,
                            platform_content_id=video_id,
                            content_url=f"https://www.facebook.com/{page_id}/videos/{video_id}/",
                            status=DistributionStatus.PUBLISHED,
                            upload_time=datetime.now()
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"Facebook upload failed: {error_text}")
            
        except Exception as e:
            logger.error(f"Facebook upload failed: {e}")
            raise

    async def _upload_to_twitter(
        self,
        content_path: str,
        metadata: ContentMetadata,
        credentials: PlatformCredentials
    ) -> DistributionResult:
        """Upload content to Twitter"""
        try:
            config = self.platform_configs[Platform.TWITTER]
            
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                # For video uploads, use media upload endpoint first
                media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"
                
                async with aiofiles.open(content_path, 'rb') as f:
                    media_data = await f.read()
                
                # Upload media
                form_data = aiohttp.FormData()
                form_data.add_field('media', media_data, filename='video.mp4', content_type='video/mp4')
                
                async with session.post(media_upload_url, data=form_data, headers={"Authorization": headers["Authorization"]}) as response:
                    if response.status == 200:
                        media_result = await response.json()
                        media_id = media_result["media_id_string"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"Twitter media upload failed: {error_text}")
                
                # Create tweet with media
                tweet_url = f"{config['api_base']}/tweets"
                tweet_data = {
                    "text": f"{metadata.title}\n\n{metadata.description}",
                    "media": {
                        "media_ids": [media_id]
                    }
                }
                
                async with session.post(tweet_url, headers=headers, json=tweet_data) as response:
                    if response.status == 201:
                        tweet_result = await response.json()
                        tweet_id = tweet_result["data"]["id"]
                        
                        return DistributionResult(
                            platform=Platform.TWITTER,
                            platform_content_id=tweet_id,
                            content_url=f"https://twitter.com/user/status/{tweet_id}",
                            status=DistributionStatus.PUBLISHED,
                            upload_time=datetime.now()
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"Twitter tweet creation failed: {error_text}")
            
        except Exception as e:
            logger.error(f"Twitter upload failed: {e}")
            raise

    async def aggregate_analytics(
        self,
        user_id: str,
        content_ids: List[str] = None,
        platforms: List[Platform] = None,
        period_start: datetime = None,
        period_end: datetime = None
    ) -> Dict[Platform, List[PlatformAnalytics]]:
        """
        Aggregate analytics data from multiple platforms
        
        Args:
            user_id: User identifier
            content_ids: Specific content to analyze
            platforms: Platforms to include
            period_start: Analytics start date
            period_end: Analytics end date
            
        Returns:
            Platform analytics data
        """
        try:
            if not period_end:
                period_end = datetime.now()
            if not period_start:
                period_start = period_end - timedelta(days=30)
            
            # Get user's connected platforms
            connected_platforms = await self._get_user_platforms(user_id)
            
            if platforms:
                connected_platforms = [p for p in connected_platforms if p in platforms]
            
            analytics_results = {}
            
            # Fetch analytics from each platform
            for platform in connected_platforms:
                try:
                    platform_analytics = await self._fetch_platform_analytics(
                        user_id,
                        platform,
                        content_ids,
                        period_start,
                        period_end
                    )
                    analytics_results[platform] = platform_analytics
                    
                except Exception as e:
                    logger.error(f"Failed to fetch analytics for {platform.value}: {e}")
                    analytics_results[platform] = []
            
            # Cache results
            cache_key = f"analytics:{user_id}:{hash(str(content_ids))}:{period_start.date()}:{period_end.date()}"
            await self._cache_analytics_results(cache_key, analytics_results)
            
            # Update metrics
            self.metrics_collector.increment_counter(
                "analytics_aggregations",
                tags={"platforms": str(len(analytics_results))}
            )
            
            logger.info(f"Analytics aggregated for {len(analytics_results)} platforms")
            return analytics_results
            
        except Exception as e:
            logger.error(f"Analytics aggregation failed: {e}")
            return {}

    # Helper methods for data persistence and validation
    async def _validate_content_for_platform(
        self,
        content_path: str,
        content_format: ContentFormat,
        platform: Platform
    ):
        """Validate content compatibility with platform"""
        config = self.platform_configs[platform]
        
        # Check file size
        file_size = await self._get_file_size(content_path)
        if file_size > config["max_file_size"]:
            raise ValueError(f"File too large for {platform.value}: {file_size} bytes")
        
        # Check file format
        file_extension = content_path.lower().split('.')[-1]
        if f".{file_extension}" not in config["supported_formats"]:
            raise ValueError(f"Unsupported format for {platform.value}: {file_extension}")

    async def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        return await self.file_manager.get_file_size(file_path)

    async def _test_platform_connection(self, credentials: PlatformCredentials):
        """
Test platform connection"""
        # Implementation for testing platform connection
        pass

    async def _store_platform_credentials(self, user_id: str, credentials: PlatformCredentials):
        """
Store encrypted platform credentials"""
        # Implementation depends on your database and encryption strategy
        pass

    async def _get_platform_credentials(self, user_id: str, platform: Platform) -> Optional[PlatformCredentials]:
        """
Get platform credentials for user"""
        # Implementation depends on your database layer
        return None

    async def _refresh_token_if_needed(self, credentials: PlatformCredentials) -> PlatformCredentials:
        """
Refresh access token if expired"""
        if credentials.token_expires_at and datetime.now() >= credentials.token_expires_at:
            # Implement token refresh logic
            pass
        return credentials

    async def _store_distribution_records(self, results: List[DistributionResult], user_id: str):
        """
Store distribution records in database"""
        # Implementation depends on your database layer
        pass

    async def _get_user_platforms(self, user_id: str) -> List[Platform]:
        """
Get user's connected platforms"""
        # Implementation depends on your database layer
        return []

    async def _fetch_platform_analytics(
        self,
        user_id: str,
        platform: Platform,
        content_ids: List[str],
        period_start: datetime,
        period_end: datetime
    ) -> List[PlatformAnalytics]:
        """
Fetch analytics from specific platform"""
        # Implementation for platform-specific analytics fetching
        return []

    async def _cache_analytics_results(self, cache_key: str, results: Dict[Platform, List[PlatformAnalytics]]):
        """
Cache analytics results"""
        try:
            # Convert to JSON-serializable format
            serializable_results = {}
            for platform, analytics_list in results.items():
                serializable_results[platform.value] = [asdict(analytics) for analytics in analytics_list]
            
            await self.redis_manager.setex(cache_key, self.cache_ttl, json.dumps(serializable_results))
        except Exception as e:
            logger.warning(f"Failed to cache analytics results: {e}")
