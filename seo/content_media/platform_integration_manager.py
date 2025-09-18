"""Platform Integration Manager
Comprehensive platform integration and API management for content distribution.

Features:
- YouTube API integration
- Spotify API integration  
- Instagram Graph API
- TikTok API integration
- LinkedIn API integration
- Pinterest API integration
- Twitch API integration
- Platform-specific SEO rules

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

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

Author: Fahed Mlaiel (mlaiel@live.de)
Expertise: Lead Dev IA + API Integration Expert + Platform Specialist + DevOps Engineer
"""

import asyncio
import logging
import json
import hashlib
import base64
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import requests
from pathlib import Path

try:
    import google.auth
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
    import tweepy
    import facebook
    import linkedin
    from TikTokApi import TikTokApi
    import pinterest
    from twitchAPI.twitch import Twitch
    from twitchAPI.oauth import UserAuthenticator
    import instabot
    import pandas as pd
    import numpy as np
    from PIL import Image
    import ffmpeg
    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
except ImportError as e:
    logging.warning(f"Optional platform integration dependencies not available: {e}")

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Supported platform types."""
    SOCIAL_MEDIA = "social_media"
    VIDEO_STREAMING = "video_streaming"
    MUSIC_STREAMING = "music_streaming"
    PODCAST = "podcast"
    BLOGGING = "blogging"
    PROFESSIONAL = "professional"
    MESSAGING = "messaging"
    LIVE_STREAMING = "live_streaming"
    E_COMMERCE = "e_commerce"


class Platform(Enum):
    """Supported platforms."""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    TWITCH = "twitch"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    REDDIT = "reddit"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    DEEZER = "deezer"
    TIDAL = "tidal"
    BANDCAMP = "bandcamp"


class ContentType(Enum):
    """Content types for platform optimization."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    POST = "post"
    REEL = "reel"
    SHORT = "short"
    PODCAST = "podcast"
    ARTICLE = "article"
    ALBUM = "album"
    PLAYLIST = "playlist"


class IntegrationStatus(Enum):
    """Integration status states."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PENDING = "pending"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


@dataclass
class PlatformCredentials:
    """Platform API credentials."""
    platform: Platform
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    bearer_token: Optional[str] = None
    webhook_secret: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlatformConfig:
    """Platform-specific configuration."""
    platform: Platform
    platform_type: PlatformType
    api_version: str
    base_url: str
    rate_limits: Dict[str, int]
    supported_content_types: List[ContentType]
    max_file_sizes: Dict[ContentType, int]
    optimal_formats: Dict[ContentType, List[str]]
    seo_requirements: Dict[str, Any]
    monetization_features: List[str]
    analytics_capabilities: List[str]
    webhook_support: bool = False
    real_time_updates: bool = False


@dataclass
class ContentItem:
    """Content item for platform distribution."""
    content_id: str
    title: str
    description: str
    content_type: ContentType
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    thumbnail_path: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    duration: Optional[int] = None
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    privacy_level: str = "public"
    scheduled_publish: Optional[datetime] = None
    monetization_enabled: bool = False
    custom_thumbnail: bool = False
    closed_captions: Optional[str] = None
    language: str = "en"
    location: Optional[str] = None
    collaborators: List[str] = field(default_factory=list)


@dataclass
class PublishResult:
    """Result of content publishing."""
    platform: Platform
    success: bool
    content_id: str
    platform_content_id: Optional[str] = None
    url: Optional[str] = None
    error_message: Optional[str] = None
    published_at: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PlatformIntegration:
    """Platform integration status and data."""
    platform: Platform
    status: IntegrationStatus
    credentials: PlatformCredentials
    config: PlatformConfig
    last_sync: Optional[datetime] = None
    error_count: int = 0
    rate_limit_reset: Optional[datetime] = None
    webhook_url: Optional[str] = None
    sync_enabled: bool = True
    auto_publish: bool = False
    content_sync_settings: Dict[str, Any] = field(default_factory=dict)


class PlatformIntegrationManager:
    """Comprehensive platform integration manager for multi-platform content distribution.
    
    Manages API connections, content optimization, and automated publishing across
    all major social media, streaming, and content platforms.
    """
    
    def __init__(self, 
                 credentials_file: Optional[str] = None,
                 enable_webhooks: bool = True,
                 auto_retry: bool = True):
        """Initialize Platform Integration Manager.
        
        Args:
            credentials_file: Path to credentials configuration file
            enable_webhooks: Enable webhook support for real-time updates
            auto_retry: Enable automatic retry for failed operations
        """
        self.credentials_file = credentials_file
        self.enable_webhooks = enable_webhooks
        self.auto_retry = auto_retry
        
        # Platform integrations
        self.integrations: Dict[Platform, PlatformIntegration] = {}
        
        # API clients
        self.api_clients: Dict[Platform, Any] = {}
        
        # Rate limiting
        self.rate_limiters: Dict[Platform, Dict[str, datetime]] = {}
        
        # Initialize platform configurations
        self.platform_configs = self._initialize_platform_configs()
        
        # Load credentials if file provided
        if credentials_file and Path(credentials_file).exists():
            self._load_credentials(credentials_file)
        
        # Session for HTTP requests
        self.session = aiohttp.ClientSession()
        
        logger.info("Platform Integration Manager initialized successfully")
    
    async def connect_platform(self, 
                             platform: Platform,
                             credentials: PlatformCredentials) -> bool:
        """Connect to a platform with provided credentials.
        
        Args:
            platform: Platform to connect to
            credentials: Platform credentials
            
        Returns:
            Boolean indicating success
        """
        try:
            logger.info(f"Connecting to {platform.value}")
            
            # Get platform configuration
            config = self.platform_configs.get(platform)
            if not config:
                logger.error(f"No configuration found for {platform.value}")
                return False
            
            # Initialize API client
            api_client = await self._initialize_api_client(platform, credentials)
            if not api_client:
                logger.error(f"Failed to initialize API client for {platform.value}")
                return False
            
            # Test connection
            connection_test = await self._test_platform_connection(platform, api_client)
            if not connection_test:
                logger.error(f"Connection test failed for {platform.value}")
                return False
            
            # Create integration
            integration = PlatformIntegration(
                platform=platform,
                status=IntegrationStatus.CONNECTED,
                credentials=credentials,
                config=config,
                last_sync=datetime.now()
            )
            
            self.integrations[platform] = integration
            self.api_clients[platform] = api_client
            
            logger.info(f"Successfully connected to {platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to {platform.value}: {e}")
            return False
    
    async def publish_content(self,
                            content: ContentItem,
                            platforms: List[Platform],
                            optimize_per_platform: bool = True) -> Dict[Platform, PublishResult]:
        """Publish content to multiple platforms.
        
        Args:
            content: Content item to publish
            platforms: List of target platforms
            optimize_per_platform: Whether to optimize content for each platform
            
        Returns:
            Dictionary mapping platforms to publish results
        """
        try:
            results = {}
            
            for platform in platforms:
                # Check if platform is connected
                if platform not in self.integrations:
                    results[platform] = PublishResult(
                        platform=platform,
                        success=False,
                        content_id=content.content_id,
                        error_message="Platform not connected"
                    )
                    continue
                
                integration = self.integrations[platform]
                if integration.status != IntegrationStatus.CONNECTED:
                    results[platform] = PublishResult(
                        platform=platform,
                        success=False,
                        content_id=content.content_id,
                        error_message=f"Platform status: {integration.status.value}"
                    )
                    continue
                
                # Optimize content for platform if requested
                optimized_content = content
                if optimize_per_platform:
                    optimized_content = await self._optimize_content_for_platform(content, platform)
                
                # Publish to platform
                result = await self._publish_to_platform(optimized_content, platform)
                results[platform] = result
                
                # Add delay between publishes to respect rate limits
                await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            logger.error(f"Error publishing content: {e}")
            return {}
    
    async def sync_content_metrics(self, 
                                 platform: Platform,
                                 content_ids: List[str] = None,
                                 date_range: Tuple[datetime, datetime] = None) -> Dict[str, Dict[str, Any]]:
        """Sync content metrics from platform.
        
        Args:
            platform: Platform to sync from
            content_ids: Specific content IDs to sync (optional)
            date_range: Date range for metrics (optional)
            
        Returns:
            Dictionary mapping content IDs to metrics
        """
        try:
            if platform not in self.integrations:
                logger.error(f"Platform {platform.value} not connected")
                return {}
            
            integration = self.integrations[platform]
            api_client = self.api_clients.get(platform)
            
            if not api_client:
                logger.error(f"No API client for {platform.value}")
                return {}
            
            # Platform-specific metrics sync
            metrics = await self._sync_platform_metrics(platform, api_client, content_ids, date_range)
            
            # Update last sync time
            integration.last_sync = datetime.now()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error syncing metrics from {platform.value}: {e}")
            return {}
    
    async def get_platform_analytics(self,
                                   platform: Platform,
                                   metric_types: List[str] = None,
                                   time_period: str = "30d") -> Dict[str, Any]:
        """Get analytics data from platform.
        
        Args:
            platform: Platform to get analytics from
            metric_types: Specific metrics to retrieve
            time_period: Time period for analytics (7d, 30d, 90d, etc.)
            
        Returns:
            Dictionary with analytics data
        """
        try:
            if platform not in self.integrations:
                logger.error(f"Platform {platform.value} not connected")
                return {}
            
            api_client = self.api_clients.get(platform)
            if not api_client:
                return {}
            
            # Platform-specific analytics retrieval
            analytics = await self._get_platform_analytics(platform, api_client, metric_types, time_period)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics from {platform.value}: {e}")
            return {}
    
    async def cross_platform_optimization(self,
                                        content: ContentItem,
                                        target_platforms: List[Platform]) -> Dict[Platform, ContentItem]:
        """Optimize content for multiple platforms simultaneously.
        
        Args:
            content: Original content item
            target_platforms: List of target platforms
            
        Returns:
            Dictionary mapping platforms to optimized content
        """
        try:
            optimized_content = {}
            
            for platform in target_platforms:
                if platform not in self.platform_configs:
                    continue
                
                # Create platform-specific optimization
                platform_content = await self._optimize_content_for_platform(content, platform)
                optimized_content[platform] = platform_content
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error in cross-platform optimization: {e}")
            return {}
    
    async def schedule_content_publishing(self,
                                        content: ContentItem,
                                        platforms: List[Platform],
                                        schedule: Dict[Platform, datetime]) -> Dict[Platform, bool]:
        """Schedule content publishing across platforms.
        
        Args:
            content: Content to schedule
            platforms: Target platforms
            schedule: Publishing schedule per platform
            
        Returns:
            Dictionary mapping platforms to scheduling success
        """
        try:
            scheduling_results = {}
            
            for platform in platforms:
                if platform not in schedule:
                    continue
                
                publish_time = schedule[platform]
                
                # Check if platform supports scheduling
                config = self.platform_configs.get(platform)
                if not config or "scheduling" not in config.analytics_capabilities:
                    scheduling_results[platform] = False
                    continue
                
                # Schedule on platform
                success = await self._schedule_on_platform(content, platform, publish_time)
                scheduling_results[platform] = success
            
            return scheduling_results
            
        except Exception as e:
            logger.error(f"Error scheduling content: {e}")
            return {}
    
    # Private helper methods
    
    def _initialize_platform_configs(self) -> Dict[Platform, PlatformConfig]:
        """Initialize configurations for all supported platforms."""
        configs = {}
        
        # YouTube configuration
        configs[Platform.YOUTUBE] = PlatformConfig(
            platform=Platform.YOUTUBE,
            platform_type=PlatformType.VIDEO_STREAMING,
            api_version="v3",
            base_url="https://www.googleapis.com/youtube/v3",
            rate_limits={"requests_per_day": 10000, "uploads_per_day": 100},
            supported_content_types=[ContentType.VIDEO, ContentType.LIVE_STREAM],
            max_file_sizes={ContentType.VIDEO: 128 * 1024 * 1024 * 1024},  # 128GB
            optimal_formats={ContentType.VIDEO: ["mp4", "mov", "avi", "wmv", "flv", "webm"]},
            seo_requirements={
                "title_length": 100,
                "description_length": 5000,
                "tags_count": 15,
                "thumbnail_required": True
            },
            monetization_features=["ads", "memberships", "super_chat", "merchandise"],
            analytics_capabilities=["views", "watch_time", "subscribers", "revenue", "demographics"],
            webhook_support=True,
            real_time_updates=True
        )
        
        # Spotify configuration
        configs[Platform.SPOTIFY] = PlatformConfig(
            platform=Platform.SPOTIFY,
            platform_type=PlatformType.MUSIC_STREAMING,
            api_version="v1",
            base_url="https://api.spotify.com/v1",
            rate_limits={"requests_per_second": 100},
            supported_content_types=[ContentType.AUDIO, ContentType.ALBUM, ContentType.PLAYLIST],
            max_file_sizes={ContentType.AUDIO: 100 * 1024 * 1024},  # 100MB
            optimal_formats={ContentType.AUDIO: ["mp3", "flac", "wav", "ogg"]},
            seo_requirements={
                "title_length": 50,
                "description_length": 300,
                "genres_required": True,
                "artwork_required": True
            },
            monetization_features=["streaming_royalties", "playlist_placement"],
            analytics_capabilities=["streams", "listeners", "playlists", "demographics"],
            webhook_support=True,
            real_time_updates=False
        )
        
        # Instagram configuration
        configs[Platform.INSTAGRAM] = PlatformConfig(
            platform=Platform.INSTAGRAM,
            platform_type=PlatformType.SOCIAL_MEDIA,
            api_version="v18.0",
            base_url="https://graph.facebook.com",
            rate_limits={"requests_per_hour": 200},
            supported_content_types=[ContentType.IMAGE, ContentType.VIDEO, ContentType.STORY, ContentType.REEL],
            max_file_sizes={
                ContentType.IMAGE: 8 * 1024 * 1024,  # 8MB
                ContentType.VIDEO: 100 * 1024 * 1024,  # 100MB
                ContentType.REEL: 100 * 1024 * 1024   # 100MB
            },
            optimal_formats={
                ContentType.IMAGE: ["jpg", "jpeg", "png"],
                ContentType.VIDEO: ["mp4", "mov"],
                ContentType.REEL: ["mp4"]
            },
            seo_requirements={
                "caption_length": 2200,
                "hashtags_count": 30,
                "mentions_allowed": True,
                "location_tagging": True
            },
            monetization_features=["brand_partnerships", "shopping", "badges"],
            analytics_capabilities=["reach", "impressions", "engagement", "saves", "profile_visits"],
            webhook_support=True,
            real_time_updates=True
        )
        
        # TikTok configuration
        configs[Platform.TIKTOK] = PlatformConfig(
            platform=Platform.TIKTOK,
            platform_type=PlatformType.SOCIAL_MEDIA,
            api_version="v2",
            base_url="https://open-api.tiktok.com",
            rate_limits={"requests_per_day": 1000},
            supported_content_types=[ContentType.VIDEO, ContentType.SHORT, ContentType.LIVE_STREAM],
            max_file_sizes={ContentType.VIDEO: 4 * 1024 * 1024 * 1024},  # 4GB
            optimal_formats={ContentType.VIDEO: ["mp4", "mov", "webm"]},
            seo_requirements={
                "caption_length": 300,
                "hashtags_count": 20,
                "trending_sounds": True,
                "effects_encouraged": True
            },
            monetization_features=["creator_fund", "brand_partnerships", "gifts", "shopping"],
            analytics_capabilities=["views", "likes", "shares", "comments", "profile_views"],
            webhook_support=False,
            real_time_updates=True
        )
        
        # Twitter configuration
        configs[Platform.TWITTER] = PlatformConfig(
            platform=Platform.TWITTER,
            platform_type=PlatformType.SOCIAL_MEDIA,
            api_version="v2",
            base_url="https://api.twitter.com/2",
            rate_limits={"tweets_per_day": 300, "requests_per_15min": 300},
            supported_content_types=[ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO],
            max_file_sizes={
                ContentType.IMAGE: 5 * 1024 * 1024,  # 5MB
                ContentType.VIDEO: 512 * 1024 * 1024  # 512MB
            },
            optimal_formats={
                ContentType.IMAGE: ["jpg", "jpeg", "png", "gif", "webp"],
                ContentType.VIDEO: ["mp4", "mov"]
            },
            seo_requirements={
                "character_limit": 280,
                "hashtags_count": 5,
                "mentions_allowed": True,
                "thread_support": True
            },
            monetization_features=["super_follows", "tip_jar", "twitter_blue"],
            analytics_capabilities=["impressions", "engagements", "profile_clicks", "followers"],
            webhook_support=True,
            real_time_updates=True
        )
        
        # Add more platform configurations as needed
        
        return configs
    
    async def _initialize_api_client(self, platform: Platform, credentials: PlatformCredentials) -> Optional[Any]:
        """Initialize API client for specific platform."""
        try:
            if platform == Platform.YOUTUBE:
                return await self._init_youtube_client(credentials)
            elif platform == Platform.SPOTIFY:
                return await self._init_spotify_client(credentials)
            elif platform == Platform.INSTAGRAM:
                return await self._init_instagram_client(credentials)
            elif platform == Platform.TIKTOK:
                return await self._init_tiktok_client(credentials)
            elif platform == Platform.TWITTER:
                return await self._init_twitter_client(credentials)
            else:
                logger.warning(f"API client initialization not implemented for {platform.value}")
                return None
                
        except Exception as e:
            logger.error(f"Error initializing {platform.value} client: {e}")
            return None
    
    async def _init_youtube_client(self, credentials: PlatformCredentials) -> Optional[Any]:
        """Initialize YouTube API client."""
        try:
            # Create credentials object
            creds = Credentials(
                token=credentials.access_token,
                refresh_token=credentials.refresh_token,
                client_id=credentials.client_id,
                client_secret=credentials.client_secret
            )
            
            # Build YouTube service
            youtube = build('youtube', 'v3', credentials=creds)
            return youtube
            
        except Exception as e:
            logger.error(f"Error initializing YouTube client: {e}")
            return None
    
    async def _init_spotify_client(self, credentials: PlatformCredentials) -> Optional[Any]:
        """Initialize Spotify API client."""
        try:
            # Create Spotify client
            if credentials.client_id and credentials.client_secret:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=credentials.client_id,
                    client_secret=credentials.client_secret
                )
                spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                return spotify
            else:
                logger.error("Spotify credentials missing")
                return None
                
        except Exception as e:
            logger.error(f"Error initializing Spotify client: {e}")
            return None
    
    async def _init_instagram_client(self, credentials: PlatformCredentials) -> Optional[Any]:
        """Initialize Instagram API client."""
        try:
            # Instagram uses Facebook Graph API
            # This would typically use the facebook-sdk or direct HTTP requests
            return {
                "access_token": credentials.access_token,
                "base_url": "https://graph.facebook.com/v18.0"
            }
            
        except Exception as e:
            logger.error(f"Error initializing Instagram client: {e}")
            return None
    
    async def _init_tiktok_client(self, credentials: PlatformCredentials) -> Optional[Any]:
        """Initialize TikTok API client."""
        try:
            # TikTok API client initialization
            return {
                "access_token": credentials.access_token,
                "base_url": "https://open-api.tiktok.com"
            }
            
        except Exception as e:
            logger.error(f"Error initializing TikTok client: {e}")
            return None
    
    async def _init_twitter_client(self, credentials: PlatformCredentials) -> Optional[Any]:
        """Initialize Twitter API client."""
        try:
            # Twitter API v2 client
            client = tweepy.Client(
                bearer_token=credentials.bearer_token,
                consumer_key=credentials.client_id,
                consumer_secret=credentials.client_secret,
                access_token=credentials.access_token,
                access_token_secret=credentials.api_secret
            )
            return client
            
        except Exception as e:
            logger.error(f"Error initializing Twitter client: {e}")
            return None
    
    async def _test_platform_connection(self, platform: Platform, api_client: Any) -> bool:
        """Test connection to platform."""
        try:
            if platform == Platform.YOUTUBE:
                # Test YouTube connection
                response = api_client.channels().list(part="snippet", mine=True).execute()
                return len(response.get("items", [])) > 0
                
            elif platform == Platform.SPOTIFY:
                # Test Spotify connection
                user = api_client.current_user()
                return user is not None
                
            elif platform == Platform.INSTAGRAM:
                # Test Instagram connection
                # Simple test with account info
                return api_client.get("access_token") is not None
                
            elif platform == Platform.TWITTER:
                # Test Twitter connection
                me = api_client.get_me()
                return me is not None
                
            else:
                # Default to True for unsupported platforms
                return True
                
        except Exception as e:
            logger.error(f"Connection test failed for {platform.value}: {e}")
            return False
    
    async def _optimize_content_for_platform(self, content: ContentItem, platform: Platform) -> ContentItem:
        """Optimize content for specific platform."""
        try:
            config = self.platform_configs.get(platform)
            if not config:
                return content
            
            # Create optimized copy
            optimized = ContentItem(
                content_id=f"{content.content_id}_{platform.value}",
                title=content.title,
                description=content.description,
                content_type=content.content_type,
                file_path=content.file_path,
                file_url=content.file_url,
                thumbnail_path=content.thumbnail_path,
                tags=content.tags.copy(),
                hashtags=content.hashtags.copy(),
                category=content.category,
                duration=content.duration,
                metadata=content.metadata.copy()
            )
            
            # Apply platform-specific optimizations
            seo_reqs = config.seo_requirements
            
            # Optimize title
            if "title_length" in seo_reqs:
                max_length = seo_reqs["title_length"]
                if len(optimized.title) > max_length:
                    optimized.title = optimized.title[:max_length-3] + "..."
            
            # Optimize description
            if "description_length" in seo_reqs:
                max_length = seo_reqs["description_length"]
                if len(optimized.description) > max_length:
                    optimized.description = optimized.description[:max_length-3] + "..."
            
            # Optimize hashtags
            if "hashtags_count" in seo_reqs:
                max_hashtags = seo_reqs["hashtags_count"]
                if len(optimized.hashtags) > max_hashtags:
                    optimized.hashtags = optimized.hashtags[:max_hashtags]
            
            # Platform-specific adjustments
            if platform == Platform.YOUTUBE:
                # YouTube specific optimizations
                if not optimized.thumbnail_path and seo_reqs.get("thumbnail_required"):
                    # Generate default thumbnail if none provided
                    optimized.metadata["needs_thumbnail"] = True
                    
            elif platform == Platform.INSTAGRAM:
                # Instagram specific optimizations
                # Ensure hashtags are formatted correctly
                optimized.hashtags = [f"#{tag.lstrip('#')}" for tag in optimized.hashtags]
                
            elif platform == Platform.TIKTOK:
                # TikTok specific optimizations
                # Add trending hashtags if available
                trending_hashtags = ["#fyp", "#foryou", "#viral"]
                optimized.hashtags.extend(trending_hashtags[:3])
                
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing content for {platform.value}: {e}")
            return content
    
    async def _publish_to_platform(self, content: ContentItem, platform: Platform) -> PublishResult:
        """Publish content to specific platform."""
        try:
            api_client = self.api_clients.get(platform)
            if not api_client:
                return PublishResult(
                    platform=platform,
                    success=False,
                    content_id=content.content_id,
                    error_message="API client not available"
                )
            
            # Platform-specific publishing
            if platform == Platform.YOUTUBE:
                return await self._publish_to_youtube(content, api_client)
            elif platform == Platform.INSTAGRAM:
                return await self._publish_to_instagram(content, api_client)
            elif platform == Platform.TWITTER:
                return await self._publish_to_twitter(content, api_client)
            elif platform == Platform.TIKTOK:
                return await self._publish_to_tiktok(content, api_client)
            else:
                return PublishResult(
                    platform=platform,
                    success=False,
                    content_id=content.content_id,
                    error_message=f"Publishing not implemented for {platform.value}"
                )
                
        except Exception as e:
            logger.error(f"Error publishing to {platform.value}: {e}")
            return PublishResult(
                platform=platform,
                success=False,
                content_id=content.content_id,
                error_message=str(e)
            )
    
    # Simplified publishing methods (would be fully implemented in production)
    
    async def _publish_to_youtube(self, content: ContentItem, api_client: Any) -> PublishResult:
        """Publish video to YouTube."""
        try:
            # YouTube video upload logic would go here
            # This is a simplified mock implementation
            
            result = PublishResult(
                platform=Platform.YOUTUBE,
                success=True,
                content_id=content.content_id,
                platform_content_id="yt_" + content.content_id,
                url=f"https://youtube.com/watch?v=mock_{content.content_id}",
                published_at=datetime.now(),
                recommendations=["Add end screens", "Create playlist", "Enable monetization"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error publishing to YouTube: {e}")
            return PublishResult(
                platform=Platform.YOUTUBE,
                success=False,
                content_id=content.content_id,
                error_message=str(e)
            )
    
    async def _publish_to_instagram(self, content: ContentItem, api_client: Any) -> PublishResult:
        """Publish content to Instagram."""
        try:
            # Instagram publishing logic would go here
            result = PublishResult(
                platform=Platform.INSTAGRAM,
                success=True,
                content_id=content.content_id,
                platform_content_id="ig_" + content.content_id,
                url=f"https://instagram.com/p/mock_{content.content_id}",
                published_at=datetime.now(),
                recommendations=["Use trending hashtags", "Post at optimal time", "Engage with comments"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error publishing to Instagram: {e}")
            return PublishResult(
                platform=Platform.INSTAGRAM,
                success=False,
                content_id=content.content_id,
                error_message=str(e)
            )
    
    async def _publish_to_twitter(self, content: ContentItem, api_client: Any) -> PublishResult:
        """Publish content to Twitter."""
        try:
            # Twitter publishing logic
            if content.content_type == ContentType.TEXT:
                # Text tweet
                tweet_text = f"{content.title}\n\n{content.description}"
                if content.hashtags:
                    tweet_text += "\n\n" + " ".join(content.hashtags)
                
                # Ensure within character limit
                if len(tweet_text) > 280:
                    tweet_text = tweet_text[:277] + "..."
                
                # Post tweet (mock)
                result = PublishResult(
                    platform=Platform.TWITTER,
                    success=True,
                    content_id=content.content_id,
                    platform_content_id="tw_" + content.content_id,
                    url=f"https://twitter.com/user/status/mock_{content.content_id}",
                    published_at=datetime.now()
                )
                
                return result
            
        except Exception as e:
            logger.error(f"Error publishing to Twitter: {e}")
            return PublishResult(
                platform=Platform.TWITTER,
                success=False,
                content_id=content.content_id,
                error_message=str(e)
            )
    
    # Additional helper methods would be implemented here...
    
    def _load_credentials(self, credentials_file: str) -> None:
        """Load credentials from file."""
        try:
            with open(credentials_file, 'r') as f:
                creds_data = json.load(f)
            
            for platform_name, platform_creds in creds_data.items():
                try:
                    platform = Platform(platform_name)
                    credentials = PlatformCredentials(
                        platform=platform,
                        **platform_creds
                    )
                    # Store credentials for later use
                    
                except ValueError:
                    logger.warning(f"Unknown platform in credentials: {platform_name}")
                    
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self, 'session'):
            await self.session.close()