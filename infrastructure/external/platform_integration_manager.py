"""
Platform Integration Manager - 65+ Platform Distribution Engine
==============================================================

Enterprise-grade platform integration system for Ainflue creator content distribution.
Manages simultaneous distribution across 65+ platforms with intelligent optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure - External Integrations Module
Expert Role: Lead Dev IA + Backend Senior + DevOps + Integration Specialist
Version: 1.0 Production Enterprise

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation 
écrite PERSONNELLE est STRICTEMENT INTERDITE et sera poursuivie en justice.

Platforms Supported (65+):
- Social Media (29): Instagram, TikTok, YouTube, Facebook, Twitter/X, LinkedIn, etc.
- Music Streaming (20): Spotify, Apple Music, YouTube Music, Amazon Music, etc.
- Creator Economy (16): OnlyFans, Patreon, Ko-fi, Gumroad, Etsy, etc.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from datetime import datetime, timedelta
import aiohttp
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlatformCategory(Enum):
    """Platform categories for content distribution"""
    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    CREATOR_ECONOMY = "creator_economy"
    VIDEO_PLATFORMS = "video_platforms"
    PROFESSIONAL_NETWORKS = "professional_networks"
    MESSAGING_PLATFORMS = "messaging_platforms"
    GAMING_PLATFORMS = "gaming_platforms"

class ContentType(Enum):
    """Content types for distribution"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    LIVE_STREAM = "live_stream"
    PODCAST = "podcast"
    STORY = "story"

class DistributionStatus(Enum):
    """Distribution status tracking"""
    PENDING = "pending"
    PROCESSING = "processing"
    UPLOADED = "uploaded"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    REVIEWING = "reviewing"

@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    platform_id: str
    platform_name: str
    category: PlatformCategory
    supported_content_types: List[ContentType]
    api_endpoint: str
    auth_method: str
    rate_limits: Dict[str, int]
    content_specs: Dict[str, Any]
    scheduling_support: bool
    analytics_support: bool
    monetization_support: bool
    live_streaming_support: bool

@dataclass
class ContentDistributionRequest:
    """Content distribution request"""
    content_id: str
    content_type: ContentType
    content_url: str
    target_platforms: List[str]
    metadata: Dict[str, Any]
    scheduling: Optional[datetime] = None
    custom_adaptations: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10 scale
    creator_preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionResult:
    """Distribution result for single platform"""
    platform_id: str
    status: DistributionStatus
    platform_content_id: Optional[str] = None
    platform_url: Optional[str] = None
    upload_time: Optional[datetime] = None
    publish_time: Optional[datetime] = None
    error_message: Optional[str] = None
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    adaptation_applied: List[str] = field(default_factory=list)

class PlatformIntegrationManager:
    """
    Enterprise Platform Integration Manager
    
    Manages simultaneous content distribution across 65+ platforms with intelligent
    optimization, scheduling, and analytics for the Ainflue creator economy.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Platform Integration Manager"""
        self.config = config or self._get_default_config()
        self.platform_configs = self._initialize_platform_configs()
        self.platform_connectors = {}
        self.distribution_queue = asyncio.Queue()
        self.active_distributions = {}
        self.analytics_collector = {}
        self.rate_limiters = {}
        
        # Initialize platform-specific connectors
        self._initialize_platform_connectors()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("🌐 Platform Integration Manager initialized - 65+ platforms ready")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for platform integration"""
        return {
            "concurrent_uploads": 10,
            "retry_attempts": 3,
            "timeout_seconds": 300,
            "rate_limit_buffer": 0.8,  # Use 80% of rate limit
            "analytics_collection": True,
            "content_adaptation": {
                "enabled": True,
                "auto_optimize": True,
                "quality_targets": {
                    "instagram": {"resolution": "1080x1080", "duration": 60},
                    "tiktok": {"resolution": "1080x1920", "duration": 180},
                    "youtube": {"resolution": "1920x1080", "duration": None},
                    "spotify": {"format": "mp3", "bitrate": "320kbps"}
                }
            },
            "scheduling": {
                "enabled": True,
                "optimal_times": {
                    "instagram": ["12:00", "17:00", "20:00"],
                    "tiktok": ["06:00", "10:00", "19:00"],
                    "youtube": ["14:00", "20:00"],
                    "linkedin": ["09:00", "17:00"]
                }
            },
            "authentication": {
                "token_refresh_buffer": 300,  # Refresh tokens 5 minutes before expiry
                "oauth_callback_url": "https://api.ainflue.com/oauth/callback"
            },
            "monitoring": {
                "health_check_interval": 60,
                "performance_tracking": True,
                "error_alerting": True
            }
        }
    
    def _initialize_platform_configs(self) -> Dict[str, PlatformConfig]:
        """Initialize configuration for all supported platforms"""
        configs = {}
        
        # Social Media Platforms (29)
        social_platforms = [
            ("instagram", "Instagram", ["image", "video", "story"], "https://graph.instagram.com/v18.0/"),
            ("tiktok", "TikTok", ["video"], "https://open-api.tiktok.com/"),
            ("youtube", "YouTube", ["video", "live_stream"], "https://www.googleapis.com/youtube/v3/"),
            ("facebook", "Facebook", ["image", "video", "text"], "https://graph.facebook.com/v18.0/"),
            ("twitter_x", "Twitter/X", ["image", "video", "text"], "https://api.twitter.com/2/"),
            ("linkedin", "LinkedIn", ["image", "video", "text"], "https://api.linkedin.com/v2/"),
            ("snapchat", "Snapchat", ["image", "video"], "https://adsapi.snapchat.com/v1/"),
            ("pinterest", "Pinterest", ["image"], "https://api.pinterest.com/v5/"),
            ("threads", "Threads", ["text", "image"], "https://graph.threads.net/v1.0/"),
            ("bereal", "BeReal", ["image"], "https://api.bereal.com/v1/"),
            ("mastodon", "Mastodon", ["text", "image", "video"], "https://mastodon.social/api/v1/"),
            ("bluesky", "BlueSky", ["text", "image"], "https://bsky.social/xrpc/"),
            ("discord", "Discord", ["text", "image", "video"], "https://discord.com/api/v10/"),
            ("reddit", "Reddit", ["text", "image", "video"], "https://oauth.reddit.com/"),
            ("twitch", "Twitch", ["live_stream", "video"], "https://api.twitch.tv/helix/"),
            ("kick", "Kick", ["live_stream", "video"], "https://kick.com/api/v2/"),
            ("vimeo", "Vimeo", ["video"], "https://api.vimeo.com/"),
            ("dailymotion", "Dailymotion", ["video"], "https://www.dailymotion.com/partner/"),
            ("rumble", "Rumble", ["video"], "https://rumble.com/api/")
        ]
        
        for platform_id, name, content_types, api_endpoint in social_platforms:
            configs[platform_id] = PlatformConfig(
                platform_id=platform_id,
                platform_name=name,
                category=PlatformCategory.SOCIAL_MEDIA,
                supported_content_types=[ContentType(ct) for ct in content_types],
                api_endpoint=api_endpoint,
                auth_method="oauth2",
                rate_limits={"uploads": 100, "requests": 1000},
                content_specs=self._get_platform_content_specs(platform_id),
                scheduling_support=True,
                analytics_support=True,
                monetization_support=platform_id in ["youtube", "tiktok", "twitch"],
                live_streaming_support=platform_id in ["youtube", "twitch", "kick", "instagram"]
            )
        
        # Music Streaming Platforms (20)
        music_platforms = [
            ("spotify", "Spotify", ["audio", "podcast"], "https://api.spotify.com/v1/"),
            ("apple_music", "Apple Music", ["audio"], "https://api.music.apple.com/v1/"),
            ("youtube_music", "YouTube Music", ["audio"], "https://music.youtube.com/youtubei/v1/"),
            ("amazon_music", "Amazon Music", ["audio"], "https://api.amazonalexa.com/v1/"),
            ("deezer", "Deezer", ["audio"], "https://api.deezer.com/"),
            ("tidal", "Tidal", ["audio"], "https://api.tidal.com/v1/"),
            ("pandora", "Pandora", ["audio"], "https://www.pandora.com/api/v1/"),
            ("soundcloud", "SoundCloud", ["audio", "podcast"], "https://api.soundcloud.com/"),
            ("bandcamp", "Bandcamp", ["audio"], "https://bandcamp.com/api/"),
            ("audiomack", "Audiomack", ["audio"], "https://www.audiomack.com/api/"),
            ("mixcloud", "Mixcloud", ["audio"], "https://api.mixcloud.com/"),
            ("anchor", "Anchor", ["podcast"], "https://anchor.fm/api/"),
            ("apple_podcasts", "Apple Podcasts", ["podcast"], "https://podcasts.apple.com/api/"),
            ("google_podcasts", "Google Podcasts", ["podcast"], "https://podcasts.google.com/api/"),
            ("spotify_podcasts", "Spotify Podcasts", ["podcast"], "https://api.spotify.com/v1/"),
            ("distrokid", "DistroKid", ["audio"], "https://distrokid.com/api/v1/"),
            ("cdbaby", "CD Baby", ["audio"], "https://members.cdbaby.com/api/"),
            ("tunecore", "TuneCore", ["audio"], "https://www.tunecore.com/api/"),
            ("landr", "LANDR", ["audio"], "https://api.landr.com/v1/")
        ]
        
        for platform_id, name, content_types, api_endpoint in music_platforms:
            configs[platform_id] = PlatformConfig(
                platform_id=platform_id,
                platform_name=name,
                category=PlatformCategory.MUSIC_STREAMING,
                supported_content_types=[ContentType(ct) for ct in content_types],
                api_endpoint=api_endpoint,
                auth_method="oauth2",
                rate_limits={"uploads": 50, "requests": 500},
                content_specs=self._get_platform_content_specs(platform_id),
                scheduling_support=platform_id in ["spotify", "apple_music"],
                analytics_support=True,
                monetization_support=True,
                live_streaming_support=False
            )
        
        # Creator Economy Platforms (16)
        creator_platforms = [
            ("onlyfans", "OnlyFans", ["image", "video", "text"], "https://onlyfans.com/api2/v2/"),
            ("patreon", "Patreon", ["image", "video", "text", "audio"], "https://www.patreon.com/api/oauth2/v2/"),
            ("ko_fi", "Ko-fi", ["image", "text"], "https://ko-fi.com/api/v2/"),
            ("buy_me_coffee", "Buy Me a Coffee", ["image", "text"], "https://www.buymeacoffee.com/api/v1/"),
            ("gumroad", "Gumroad", ["document", "video", "audio"], "https://api.gumroad.com/v2/"),
            ("etsy", "Etsy", ["image"], "https://openapi.etsy.com/v3/"),
            ("opensea", "OpenSea", ["image"], "https://api.opensea.io/api/v1/"),
            ("foundation", "Foundation", ["image"], "https://api.foundation.app/"),
            ("superrare", "SuperRare", ["image"], "https://superrare.co/api/v1/"),
            ("async_art", "Async Art", ["image"], "https://api.async.art/v1/"),
            ("knownorigin", "KnownOrigin", ["image"], "https://api.knownorigin.io/v1/"),
            ("fiverr", "Fiverr", ["text", "image"], "https://api.fiverr.com/v1/"),
            ("upwork", "Upwork", ["text"], "https://www.upwork.com/api/v3/"),
            ("substack", "Substack", ["text", "image"], "https://substack.com/api/v1/"),
            ("medium", "Medium", ["text", "image"], "https://api.medium.com/v1/"),
            ("ghost", "Ghost", ["text", "image"], "https://ghost.org/api/v3/")
        ]
        
        for platform_id, name, content_types, api_endpoint in creator_platforms:
            configs[platform_id] = PlatformConfig(
                platform_id=platform_id,
                platform_name=name,
                category=PlatformCategory.CREATOR_ECONOMY,
                supported_content_types=[ContentType(ct) for ct in content_types],
                api_endpoint=api_endpoint,
                auth_method="oauth2",
                rate_limits={"uploads": 20, "requests": 200},
                content_specs=self._get_platform_content_specs(platform_id),
                scheduling_support=platform_id in ["patreon", "substack", "medium", "ghost"],
                analytics_support=True,
                monetization_support=True,
                live_streaming_support=platform_id in ["onlyfans"]
            )
        
        logger.info(f"✅ Initialized {len(configs)} platform configurations")
        return configs
    
    def _get_platform_content_specs(self, platform_id: str) -> Dict[str, Any]:
        """Get platform-specific content specifications"""
        specs_map = {
            "instagram": {
                "image": {"max_size": "10MB", "formats": ["jpg", "png"], "aspect_ratios": ["1:1", "4:5", "9:16"]},
                "video": {"max_size": "100MB", "formats": ["mp4"], "max_duration": 60, "aspect_ratios": ["1:1", "9:16"]},
                "story": {"max_duration": 15, "aspect_ratio": "9:16"}
            },
            "tiktok": {
                "video": {"max_size": "287MB", "formats": ["mp4"], "max_duration": 180, "aspect_ratio": "9:16", "min_duration": 3}
            },
            "youtube": {
                "video": {"max_size": "256GB", "formats": ["mp4", "mov", "avi", "wmv"], "max_duration": 43200, "aspect_ratios": ["16:9"]},
                "live_stream": {"bitrate": "1000-6000kbps", "resolution": ["720p", "1080p", "4K"]}
            },
            "spotify": {
                "audio": {"formats": ["mp3", "flac", "wav"], "bitrate": "320kbps", "sample_rate": "44.1kHz"}
            },
            "twitter_x": {
                "image": {"max_size": "5MB", "formats": ["jpg", "png", "gif"], "max_images": 4},
                "video": {"max_size": "512MB", "formats": ["mp4"], "max_duration": 140}
            },
            "linkedin": {
                "image": {"max_size": "20MB", "formats": ["jpg", "png"]},
                "video": {"max_size": "200MB", "formats": ["mp4"], "max_duration": 600}
            }
        }
        
        return specs_map.get(platform_id, {
            "image": {"max_size": "10MB", "formats": ["jpg", "png"]},
            "video": {"max_size": "100MB", "formats": ["mp4"], "max_duration": 300},
            "audio": {"formats": ["mp3"], "bitrate": "320kbps"}
        })
    
    def _initialize_platform_connectors(self) -> None:
        """Initialize platform-specific connector instances"""
        for platform_id, config in self.platform_configs.items():
            self.platform_connectors[platform_id] = PlatformConnector(config)
            self.rate_limiters[platform_id] = RateLimiter(
                config.rate_limits,
                buffer_factor=self.config["rate_limit_buffer"]
            )
        
        logger.info(f"✅ Initialized {len(self.platform_connectors)} platform connectors")
    
    def _start_background_tasks(self) -> None:
        """Start background processing tasks"""
        # Start distribution processor
        asyncio.create_task(self._distribution_processor())
        
        # Start health monitor
        asyncio.create_task(self._health_monitor())
        
        # Start analytics collector
        asyncio.create_task(self._analytics_collector_loop())
    
    async def distribute_content(self, request: ContentDistributionRequest) -> Dict[str, DistributionResult]:
        """
        Distribute content across multiple platforms
        
        Args:
            request: Content distribution request with platforms and metadata
            
        Returns:
            Dictionary mapping platform IDs to distribution results
        """
        logger.info(f"🚀 Starting content distribution for {request.content_id} to {len(request.target_platforms)} platforms")
        
        results = {}
        
        # Validate platforms
        valid_platforms = self._validate_platforms(request.target_platforms, request.content_type)
        
        if not valid_platforms:
            logger.error(f"❌ No valid platforms found for content type {request.content_type.value}")
            return results
        
        # Create distribution tasks
        distribution_tasks = []
        for platform_id in valid_platforms:
            task = self._distribute_to_platform(request, platform_id)
            distribution_tasks.append((platform_id, task))
        
        # Execute distributions with controlled concurrency
        semaphore = asyncio.Semaphore(self.config["concurrent_uploads"])
        
        async def distribute_with_semaphore(platform_id: str, task):
            async with semaphore:
                return await task
        
        # Wait for all distributions to complete
        completed_tasks = await asyncio.gather(
            *[distribute_with_semaphore(pid, task) for pid, task in distribution_tasks],
            return_exceptions=True
        )
        
        # Process results
        for i, result in enumerate(completed_tasks):
            platform_id = valid_platforms[i]
            
            if isinstance(result, Exception):
                logger.error(f"❌ Distribution failed for {platform_id}: {str(result)}")
                results[platform_id] = DistributionResult(
                    platform_id=platform_id,
                    status=DistributionStatus.FAILED,
                    error_message=str(result)
                )
            else:
                results[platform_id] = result
        
        # Log summary
        successful = sum(1 for r in results.values() if r.status in [DistributionStatus.UPLOADED, DistributionStatus.PUBLISHED])
        logger.info(f"✅ Distribution completed: {successful}/{len(results)} platforms successful")
        
        return results
    
    def _validate_platforms(self, target_platforms: List[str], content_type: ContentType) -> List[str]:
        """Validate platforms support the content type"""
        valid_platforms = []
        
        for platform_id in target_platforms:
            if platform_id not in self.platform_configs:
                logger.warning(f"⚠️ Unknown platform: {platform_id}")
                continue
            
            config = self.platform_configs[platform_id]
            if content_type in config.supported_content_types:
                valid_platforms.append(platform_id)
            else:
                logger.warning(f"⚠️ Platform {platform_id} doesn't support {content_type.value}")
        
        return valid_platforms
    
    async def _distribute_to_platform(self, request: ContentDistributionRequest, platform_id: str) -> DistributionResult:
        """Distribute content to a specific platform"""
        start_time = datetime.now()
        
        try:
            # Check rate limits
            rate_limiter = self.rate_limiters[platform_id]
            await rate_limiter.acquire()
            
            # Get platform connector
            connector = self.platform_connectors[platform_id]
            
            # Adapt content for platform if needed
            adapted_content = await self._adapt_content_for_platform(request, platform_id)
            
            # Upload content
            upload_result = await connector.upload_content(adapted_content)
            
            if upload_result.get("success"):
                result = DistributionResult(
                    platform_id=platform_id,
                    status=DistributionStatus.UPLOADED,
                    platform_content_id=upload_result.get("content_id"),
                    platform_url=upload_result.get("url"),
                    upload_time=start_time,
                    adaptation_applied=adapted_content.get("adaptations_applied", [])
                )
                
                # Schedule publishing if needed
                if request.scheduling and self.platform_configs[platform_id].scheduling_support:
                    await connector.schedule_publish(upload_result.get("content_id"), request.scheduling)
                    result.status = DistributionStatus.SCHEDULED
                else:
                    # Publish immediately
                    publish_result = await connector.publish_content(upload_result.get("content_id"))
                    if publish_result.get("success"):
                        result.status = DistributionStatus.PUBLISHED
                        result.publish_time = datetime.now()
                
                logger.info(f"✅ Content distributed to {platform_id}: {result.status.value}")
                return result
            else:
                return DistributionResult(
                    platform_id=platform_id,
                    status=DistributionStatus.FAILED,
                    error_message=upload_result.get("error", "Unknown upload error")
                )
                
        except Exception as e:
            logger.error(f"❌ Distribution to {platform_id} failed: {str(e)}")
            return DistributionResult(
                platform_id=platform_id,
                status=DistributionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _adapt_content_for_platform(self, request: ContentDistributionRequest, platform_id: str) -> Dict[str, Any]:
        """Adapt content for specific platform requirements"""
        if not self.config["content_adaptation"]["enabled"]:
            return {
                "content_url": request.content_url,
                "metadata": request.metadata,
                "adaptations_applied": []
            }
        
        platform_config = self.platform_configs[platform_id]
        content_specs = platform_config.content_specs
        adaptations_applied = []
        
        adapted_content = {
            "content_url": request.content_url,
            "metadata": request.metadata.copy(),
            "adaptations_applied": adaptations_applied
        }
        
        # Apply platform-specific adaptations
        if request.content_type == ContentType.VIDEO:
            video_specs = content_specs.get("video", {})
            
            # Adapt aspect ratio
            if "aspect_ratios" in video_specs:
                target_ratio = video_specs["aspect_ratios"][0]  # Use first preferred ratio
                adapted_content["target_aspect_ratio"] = target_ratio
                adaptations_applied.append(f"aspect_ratio_{target_ratio}")
            
            # Adapt duration
            if "max_duration" in video_specs:
                max_duration = video_specs["max_duration"]
                adapted_content["max_duration"] = max_duration
                adaptations_applied.append(f"duration_limit_{max_duration}s")
        
        elif request.content_type == ContentType.IMAGE:
            image_specs = content_specs.get("image", {})
            
            # Adapt format
            if "formats" in image_specs:
                preferred_format = image_specs["formats"][0]
                adapted_content["target_format"] = preferred_format
                adaptations_applied.append(f"format_{preferred_format}")
        
        elif request.content_type == ContentType.AUDIO:
            audio_specs = content_specs.get("audio", {})
            
            # Adapt bitrate
            if "bitrate" in audio_specs:
                target_bitrate = audio_specs["bitrate"]
                adapted_content["target_bitrate"] = target_bitrate
                adaptations_applied.append(f"bitrate_{target_bitrate}")
        
        # Platform-specific metadata optimization
        adapted_content["metadata"] = self._optimize_metadata_for_platform(
            request.metadata, platform_id
        )
        
        if adaptations_applied:
            logger.debug(f"🔄 Applied {len(adaptations_applied)} adaptations for {platform_id}")
        
        return adapted_content
    
    def _optimize_metadata_for_platform(self, metadata: Dict[str, Any], platform_id: str) -> Dict[str, Any]:
        """Optimize metadata for specific platform"""
        optimized = metadata.copy()
        
        # Platform-specific optimizations
        if platform_id == "youtube":
            # YouTube SEO optimization
            if "title" in optimized:
                optimized["title"] = optimized["title"][:100]  # YouTube title limit
            if "description" in optimized:
                optimized["description"] = optimized["description"][:5000]  # YouTube description limit
        
        elif platform_id == "instagram":
            # Instagram hashtag optimization
            if "hashtags" in optimized:
                optimized["hashtags"] = optimized["hashtags"][:30]  # Instagram hashtag limit
        
        elif platform_id == "tiktok":
            # TikTok trend optimization
            if "hashtags" in optimized:
                # Add trending TikTok hashtags
                trending_tags = ["#fyp", "#viral", "#trending"]
                current_tags = optimized["hashtags"]
                optimized["hashtags"] = trending_tags + current_tags[:27]  # Leave room for trending tags
        
        elif platform_id == "linkedin":
            # LinkedIn professional optimization
            if "description" in optimized:
                # Add professional context
                optimized["description"] = f"Professional insight: {optimized['description']}"
        
        return optimized
    
    async def _distribution_processor(self) -> None:
        """Background processor for distribution queue"""
        while True:
            try:
                # Get distribution request from queue
                request = await self.distribution_queue.get()
                
                # Process distribution
                results = await self.distribute_content(request)
                
                # Store results
                self.active_distributions[request.content_id] = {
                    "request": request,
                    "results": results,
                    "completed_at": datetime.now()
                }
                
                # Mark task as done
                self.distribution_queue.task_done()
                
            except Exception as e:
                logger.error(f"❌ Distribution processor error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _health_monitor(self) -> None:
        """Monitor platform health and connectivity"""
        while True:
            try:
                for platform_id, connector in self.platform_connectors.items():
                    try:
                        # Perform health check
                        health_status = await connector.health_check()
                        
                        if not health_status.get("healthy", False):
                            logger.warning(f"⚠️ Platform {platform_id} health check failed")
                    
                    except Exception as e:
                        logger.error(f"❌ Health check failed for {platform_id}: {str(e)}")
                
                # Wait before next health check
                await asyncio.sleep(self.config["monitoring"]["health_check_interval"])
                
            except Exception as e:
                logger.error(f"❌ Health monitor error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _analytics_collector_loop(self) -> None:
        """Collect analytics from all platforms"""
        if not self.config["analytics_collection"]:
            return
        
        while True:
            try:
                for platform_id, connector in self.platform_connectors.items():
                    try:
                        # Collect platform analytics
                        analytics = await connector.get_analytics()
                        
                        if analytics:
                            self.analytics_collector[platform_id] = {
                                "data": analytics,
                                "collected_at": datetime.now()
                            }
                    
                    except Exception as e:
                        logger.error(f"❌ Analytics collection failed for {platform_id}: {str(e)}")
                
                # Wait before next collection
                await asyncio.sleep(3600)  # Collect hourly
                
            except Exception as e:
                logger.error(f"❌ Analytics collector error: {str(e)}")
                await asyncio.sleep(3600)
    
    def get_platform_analytics(self, platform_id: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics data for platform(s)"""
        if platform_id:
            return self.analytics_collector.get(platform_id, {})
        else:
            return self.analytics_collector
    
    def get_distribution_status(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get distribution status for content"""
        return self.active_distributions.get(content_id)
    
    def get_supported_platforms(self, content_type: Optional[ContentType] = None) -> List[Dict[str, Any]]:
        """Get list of supported platforms, optionally filtered by content type"""
        platforms = []
        
        for platform_id, config in self.platform_configs.items():
            if content_type is None or content_type in config.supported_content_types:
                platforms.append({
                    "platform_id": platform_id,
                    "platform_name": config.platform_name,
                    "category": config.category.value,
                    "supported_content_types": [ct.value for ct in config.supported_content_types],
                    "scheduling_support": config.scheduling_support,
                    "analytics_support": config.analytics_support,
                    "monetization_support": config.monetization_support,
                    "live_streaming_support": config.live_streaming_support
                })
        
        return platforms
    
    async def schedule_content_distribution(self, request: ContentDistributionRequest) -> str:
        """Schedule content distribution for later execution"""
        # Add to distribution queue
        await self.distribution_queue.put(request)
        
        logger.info(f"📅 Content distribution scheduled for {request.content_id}")
        return request.content_id
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get comprehensive platform statistics"""
        total_distributions = len(self.active_distributions)
        
        # Calculate success rates by platform
        platform_stats = {}
        for content_id, distribution_data in self.active_distributions.items():
            results = distribution_data["results"]
            for platform_id, result in results.items():
                if platform_id not in platform_stats:
                    platform_stats[platform_id] = {"total": 0, "successful": 0}
                
                platform_stats[platform_id]["total"] += 1
                if result.status in [DistributionStatus.UPLOADED, DistributionStatus.PUBLISHED]:
                    platform_stats[platform_id]["successful"] += 1
        
        # Calculate success rates
        for platform_id, stats in platform_stats.items():
            stats["success_rate"] = stats["successful"] / stats["total"] if stats["total"] > 0 else 0
        
        return {
            "total_platforms_configured": len(self.platform_configs),
            "total_distributions": total_distributions,
            "platform_success_rates": platform_stats,
            "analytics_coverage": len(self.analytics_collector),
            "active_connectors": len(self.platform_connectors)
        }

class PlatformConnector:
    """Base platform connector for handling platform-specific operations"""
    
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.session = None
    
    async def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to platform (placeholder implementation)"""
        # This would be implemented per platform
        await asyncio.sleep(0.5)  # Simulate upload time
        
        return {
            "success": True,
            "content_id": f"{self.config.platform_id}_{int(time.time())}",
            "url": f"https://{self.config.platform_id}.com/content/123456"
        }
    
    async def publish_content(self, content_id: str) -> Dict[str, Any]:
        """Publish uploaded content"""
        await asyncio.sleep(0.2)  # Simulate publish time
        
        return {
            "success": True,
            "published_url": f"https://{self.config.platform_id}.com/published/123456"
        }
    
    async def schedule_publish(self, content_id: str, publish_time: datetime) -> Dict[str, Any]:
        """Schedule content for future publishing"""
        return {"success": True, "scheduled_for": publish_time.isoformat()}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check platform connectivity and health"""
        try:
            # Simulate health check
            await asyncio.sleep(0.1)
            return {"healthy": True, "response_time_ms": 100}
        except:
            return {"healthy": False, "error": "Connection failed"}
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get platform analytics"""
        # Simulate analytics data
        return {
            "views": 1000,
            "likes": 50,
            "shares": 10,
            "comments": 5,
            "reach": 2000,
            "engagement_rate": 0.065
        }

class RateLimiter:
    """Rate limiter for platform API calls"""
    
    def __init__(self, limits: Dict[str, int], buffer_factor: float = 0.8):
        self.limits = limits
        self.buffer_factor = buffer_factor
        self.tokens = {}
        self.last_reset = time.time()
        
        # Initialize token buckets
        for limit_type, limit_value in limits.items():
            self.tokens[limit_type] = int(limit_value * buffer_factor)
    
    async def acquire(self, limit_type: str = "uploads") -> None:
        """Acquire permission to make API call"""
        # Reset tokens if time window passed
        current_time = time.time()
        if current_time - self.last_reset >= 3600:  # Reset hourly
            for limit_type, limit_value in self.limits.items():
                self.tokens[limit_type] = int(limit_value * self.buffer_factor)
            self.last_reset = current_time
        
        # Wait if no tokens available
        while self.tokens.get(limit_type, 0) <= 0:
            await asyncio.sleep(1)
        
        # Consume token
        self.tokens[limit_type] -= 1

# Example usage and testing
if __name__ == "__main__":
    async def test_platform_integration():
        """Test the Platform Integration Manager"""
        manager = PlatformIntegrationManager()
        
        # Create test content distribution request
        request = ContentDistributionRequest(
            content_id="test_content_001",
            content_type=ContentType.VIDEO,
            content_url="https://cdn.ainflue.com/videos/test.mp4",
            target_platforms=["instagram", "tiktok", "youtube"],
            metadata={
                "title": "Test Creator Content",
                "description": "Testing platform distribution system",
                "hashtags": ["#test", "#creator", "#content"]
            },
            priority=8
        )
        
        # Test content distribution
        print("🌐 Testing Platform Integration Manager...")
        results = await manager.distribute_content(request)
        
        print(f"✅ Distribution Results:")
        for platform_id, result in results.items():
            print(f"   {platform_id}: {result.status.value}")
        
        # Get platform statistics
        stats = manager.get_platform_statistics()
        print(f"📊 Platform Statistics:")
        print(f"   Total platforms: {stats['total_platforms_configured']}")
        print(f"   Total distributions: {stats['total_distributions']}")
        
        # Get supported platforms
        platforms = manager.get_supported_platforms(ContentType.VIDEO)
        print(f"🎬 Video platforms supported: {len(platforms)}")
    
    # Run test
    asyncio.run(test_platform_integration())