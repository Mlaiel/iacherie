"""Mobile Platform Adaptation System

Advanced mobile platform adaptation engine for optimizing content delivery
across different mobile platforms with platform-specific optimizations,
mobile-native features, and cross-platform compatibility.

Business Logic Integration: Mobile Content → IA Processing → Protection → SEO → Platform Adaptation → Distribution

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import base64


logger = logging.getLogger(__name__)


class MobilePlatformType(Enum):
    """Mobile platform types for adaptation"""
    YOUTUBE_MOBILE = "youtube_mobile"
    INSTAGRAM_MOBILE = "instagram_mobile"
    TIKTOK_MOBILE = "tiktok_mobile"
    TWITTER_MOBILE = "twitter_mobile"
    FACEBOOK_MOBILE = "facebook_mobile"
    LINKEDIN_MOBILE = "linkedin_mobile"
    PINTEREST_MOBILE = "pinterest_mobile"
    SNAPCHAT_MOBILE = "snapchat_mobile"
    SPOTIFY_MOBILE = "spotify_mobile"
    APPLE_MUSIC_MOBILE = "apple_music_mobile"
    SOUNDCLOUD_MOBILE = "soundcloud_mobile"
    TWITCH_MOBILE = "twitch_mobile"


class MobileAdaptationType(Enum):
    """Mobile adaptation types"""
    FORMAT_CONVERSION = "format_conversion"
    QUALITY_OPTIMIZATION = "quality_optimization"
    METADATA_ADAPTATION = "metadata_adaptation"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    CAPTION_OPTIMIZATION = "caption_optimization"
    HASHTAG_ADAPTATION = "hashtag_adaptation"
    ASPECT_RATIO_ADJUSTMENT = "aspect_ratio_adjustment"
    DURATION_OPTIMIZATION = "duration_optimization"


class MobileDeviceCategory(Enum):
    """Mobile device categories"""
    SMARTPHONE_IOS = "smartphone_ios"
    SMARTPHONE_ANDROID = "smartphone_android"
    TABLET_IOS = "tablet_ios"
    TABLET_ANDROID = "tablet_android"
    PWA_MOBILE = "pwa_mobile"
    MOBILE_WEB = "mobile_web"


class ContentOptimizationLevel(Enum):
    """Content optimization levels for mobile"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class MobilePlatformConfiguration:
    """Mobile platform-specific configuration"""
    platform: MobilePlatformType
    device_category: MobileDeviceCategory
    optimization_level: ContentOptimizationLevel
    adaptation_types: List[MobileAdaptationType]
    battery_conscious: bool = True
    network_adaptive: bool = True
    offline_preparation: bool = True
    real_time_adaptation: bool = True
    auto_quality_adjustment: bool = True
    progressive_loading: bool = True
    mobile_native_features: bool = True
    cross_platform_compatibility: bool = True
    api_rate_limiting: bool = True
    content_caching: bool = True
    max_processing_time_ms: int = 5000
    quality_fallback_levels: int = 3
    bandwidth_optimization: bool = True
    storage_optimization: bool = True


@dataclass
class MobilePlatformRequest:
    """Mobile platform adaptation request"""
    request_id: str
    content_id: str
    content_type: str  # audio, video, image, text, story
    content_url: str
    content_size_bytes: int
    original_format: str
    creator_id: str
    creator_type: str
    content_metadata: Dict[str, Any]
    platform_configs: List[MobilePlatformConfiguration]
    target_quality: str = "auto"  # auto, low, medium, high, ultra
    priority: str = "normal"  # low, normal, high, urgent
    deadline: Optional[datetime] = None
    geographic_targeting: List[str] = None
    audience_demographics: Dict[str, Any] = None
    monetization_enabled: bool = True
    analytics_tracking: bool = True
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())
        if self.geographic_targeting is None:
            self.geographic_targeting = []
        if self.audience_demographics is None:
            self.audience_demographics = {}


@dataclass
class PlatformAdaptationResult:
    """Platform adaptation result for specific platform"""
    platform: MobilePlatformType
    success: bool
    adapted_content_url: str
    adapted_format: str
    adapted_quality: str
    adapted_size_bytes: int
    aspect_ratio: str
    duration_seconds: Optional[float]
    thumbnails: List[Dict[str, str]]
    optimized_metadata: Dict[str, Any]
    platform_specific_features: Dict[str, Any]
    mobile_optimizations: List[str]
    quality_levels_available: List[str]
    captions_generated: bool = False
    hashtags_optimized: List[str] = None
    posting_recommendations: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.hashtags_optimized is None:
            self.hashtags_optimized = []
        if self.posting_recommendations is None:
            self.posting_recommendations = {}


@dataclass
class MobilePlatformAdaptationResult:
    """Complete mobile platform adaptation result"""
    request_id: str
    success: bool
    processing_time_ms: int
    battery_usage_percent: float
    network_usage_mb: float
    total_adapted_platforms: int
    platform_results: List[PlatformAdaptationResult]
    cross_platform_optimizations: List[str]
    mobile_specific_optimizations: List[str]
    quality_optimization_applied: bool
    offline_content_prepared: bool
    progressive_loading_enabled: bool
    analytics_data: Dict[str, Any]
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class MobilePlatformAdapter:
    """Mobile Platform Adaptation System
    
    Advanced mobile platform adaptation engine for optimizing content delivery
    across different mobile platforms with platform-specific optimizations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Mobile optimization settings
        self.mobile_optimizations = {
            "battery_aware": self.config.get("enable_battery_optimization", True),
            "network_adaptive": self.config.get("enable_network_adaptation", True),
            "offline_capable": self.config.get("enable_offline_preparation", True),
            "real_time": self.config.get("enable_real_time_adaptation", True),
            "cache_enabled": self.config.get("enable_content_caching", True)
        }
        
        # Platform-specific adapters - placeholders for future integration
        self.youtube_adapter = None     # YouTubeMobileAdapter()
        self.instagram_adapter = None   # InstagramMobileAdapter()
        self.tiktok_adapter = None      # TikTokMobileAdapter()
        self.twitter_adapter = None     # TwitterMobileAdapter()
        self.facebook_adapter = None    # FacebookMobileAdapter()
        self.linkedin_adapter = None    # LinkedInMobileAdapter()
        self.pinterest_adapter = None   # PinterestMobileAdapter()
        self.snapchat_adapter = None    # SnapchatMobileAdapter()
        self.spotify_adapter = None     # SpotifyMobileAdapter()
        self.apple_music_adapter = None # AppleMusicMobileAdapter()
        
        # Mobile processing engines
        self.format_converter = None    # MobileFormatConverter()
        self.quality_optimizer = None   # MobileQualityOptimizer()
        self.thumbnail_generator = None # MobileThumbnailGenerator()
        self.caption_generator = None   # MobileCaptionGenerator()
        self.hashtag_optimizer = None   # MobileHashtagOptimizer()
        
        # Performance tracking
        self.adaptation_metrics = {
            "total_requests": 0,
            "successful_adaptations": 0,
            "platform_adaptations": {},
            "cache_hits": 0,
            "battery_optimizations": 0,
            "network_adaptations": 0,
            "average_processing_time": 0.0
        }
        
        # Initialize platform support
        self._initialize_platform_support()
        
        self.logger.info("Mobile Platform Adapter initialized")
    
    def _initialize_platform_support(self):
        """Initialize platform-specific support configurations."""
        self.platform_specs = {
            MobilePlatformType.YOUTUBE_MOBILE: {
                "supported_formats": ["mp4", "mov", "avi", "mkv"],
                "max_duration": 43200,  # 12 hours
                "max_size_mb": 256000,
                "aspect_ratios": ["16:9", "9:16", "1:1"],
                "thumbnail_sizes": ["1280x720", "1920x1080"],
                "audio_formats": ["aac", "mp3"],
                "captions_supported": True,
                "live_streaming": True,
                "shorts_support": True,
                "mobile_features": ["youtube_shorts", "mobile_upload", "live_mobile"]
            },
            MobilePlatformType.INSTAGRAM_MOBILE: {
                "supported_formats": ["mp4", "mov"],
                "max_duration": 3600,  # 1 hour for IGTV
                "max_size_mb": 4000,
                "aspect_ratios": ["1:1", "4:5", "9:16"],
                "thumbnail_sizes": ["1080x1080", "1080x1350"],
                "audio_formats": ["aac", "mp3"],
                "captions_supported": True,
                "stories_support": True,
                "reels_support": True,
                "mobile_features": ["instagram_stories", "instagram_reels", "mobile_filters"]
            },
            MobilePlatformType.TIKTOK_MOBILE: {
                "supported_formats": ["mp4", "mov"],
                "max_duration": 180,  # 3 minutes
                "max_size_mb": 500,
                "aspect_ratios": ["9:16"],
                "thumbnail_sizes": ["1080x1920"],
                "audio_formats": ["aac", "mp3"],
                "captions_supported": True,
                "effects_support": True,
                "music_integration": True,
                "mobile_features": ["tiktok_effects", "music_sync", "mobile_editing"]
            },
            MobilePlatformType.TWITTER_MOBILE: {
                "supported_formats": ["mp4", "mov"],
                "max_duration": 140,  # 2 minutes 20 seconds
                "max_size_mb": 512,
                "aspect_ratios": ["16:9", "1:1", "9:16"],
                "thumbnail_sizes": ["1280x720", "1200x675"],
                "audio_formats": ["aac"],
                "captions_supported": True,
                "live_streaming": True,
                "spaces_support": True,
                "mobile_features": ["twitter_spaces", "mobile_live", "thread_support"]
            }
        }
    
    async def adapt_for_platforms(self, request: MobilePlatformRequest) -> MobilePlatformAdaptationResult:
        """
        Main entry point for mobile platform adaptation.
        
        Args:
            request: Mobile platform adaptation request
            
        Returns:
            MobilePlatformAdaptationResult: Comprehensive adaptation results
        """
        start_time = time.time()
        self.adaptation_metrics["total_requests"] += 1
        
        self.logger.info(f"Starting mobile platform adaptation for content {request.content_id}")
        
        try:
            # Initialize result
            result = MobilePlatformAdaptationResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=0,
                battery_usage_percent=0.0,
                network_usage_mb=0.0,
                total_adapted_platforms=0,
                platform_results=[],
                cross_platform_optimizations=[],
                mobile_specific_optimizations=[],
                quality_optimization_applied=False,
                offline_content_prepared=False,
                progressive_loading_enabled=False,
                analytics_data={}
            )
            
            # Validate request
            validation_errors = await self._validate_adaptation_request(request)
            if validation_errors:
                result.error_message = "; ".join(validation_errors)
                self.logger.error(f"Platform adaptation request validation failed: {result.error_message}")
                return result
            
            # Apply mobile-specific optimizations
            await self._apply_mobile_optimizations(request, result)
            
            # Prepare content for adaptation
            prepared_content = await self._prepare_content_for_adaptation(request, result)
            if not prepared_content:
                result.error_message = "Failed to prepare content for adaptation"
                return result
            
            # Adapt for each platform
            platform_tasks = []
            for platform_config in request.platform_configs:
                task = self._adapt_for_single_platform(request, platform_config, prepared_content)
                platform_tasks.append(task)
            
            platform_results = await asyncio.gather(*platform_tasks, return_exceptions=True)
            
            # Process platform results
            successful_adaptations = 0
            for i, platform_result in enumerate(platform_results):
                if isinstance(platform_result, Exception):
                    self.logger.error(f"Platform adaptation failed: {str(platform_result)}")
                    # Create error result
                    error_result = PlatformAdaptationResult(
                        platform=request.platform_configs[i].platform,
                        success=False,
                        adapted_content_url="",
                        adapted_format="",
                        adapted_quality="",
                        adapted_size_bytes=0,
                        aspect_ratio="",
                        duration_seconds=None,
                        thumbnails=[],
                        optimized_metadata={},
                        platform_specific_features={},
                        mobile_optimizations=[],
                        quality_levels_available=[],
                        error_message=str(platform_result)
                    )
                    result.platform_results.append(error_result)
                else:
                    result.platform_results.append(platform_result)
                    if platform_result.success:
                        successful_adaptations += 1
            
            result.total_adapted_platforms = successful_adaptations
            
            # Apply cross-platform optimizations
            await self._apply_cross_platform_optimizations(request, result)
            
            # Generate analytics data
            await self._generate_analytics_data(request, result)
            
            # Success if at least one platform adaptation succeeded
            result.success = successful_adaptations > 0
            
            if result.success:
                self.adaptation_metrics["successful_adaptations"] += 1
            
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = int(processing_time)
            self.adaptation_metrics["average_processing_time"] = (
                (self.adaptation_metrics["average_processing_time"] * (self.adaptation_metrics["total_requests"] - 1) + 
                 processing_time) / self.adaptation_metrics["total_requests"]
            )
            
            self.logger.info(f"Mobile platform adaptation completed for {request.content_id} in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            self.logger.error(f"Mobile platform adaptation failed: {str(e)}")
            return MobilePlatformAdaptationResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=int((time.time() - start_time) * 1000),
                battery_usage_percent=0.0,
                network_usage_mb=0.0,
                total_adapted_platforms=0,
                platform_results=[],
                cross_platform_optimizations=[],
                mobile_specific_optimizations=[],
                quality_optimization_applied=False,
                offline_content_prepared=False,
                progressive_loading_enabled=False,
                analytics_data={},
                error_message=str(e)
            )
    
    async def _validate_adaptation_request(self, request: MobilePlatformRequest) -> List[str]:
        """Validate mobile platform adaptation request."""
        errors = []
        
        if not request.content_url:
            errors.append("Content URL is required")
        
        if request.content_size_bytes <= 0:
            errors.append("Content size must be positive")
        
        if not request.platform_configs:
            errors.append("At least one platform configuration is required")
        
        if not request.original_format:
            errors.append("Original content format is required")
        
        # Validate platform configurations
        for config in request.platform_configs:
            if not config.adaptation_types:
                errors.append(f"Adaptation types required for platform {config.platform.value}")
        
        return errors
    
    async def _apply_mobile_optimizations(self, request: MobilePlatformRequest, result: MobilePlatformAdaptationResult):
        """Apply mobile-specific optimizations."""
        self.logger.debug(f"Applying mobile optimizations for {request.content_id}")
        
        optimizations = []
        
        # Battery optimization
        if any(config.battery_conscious for config in request.platform_configs):
            optimizations.extend([
                "battery_aware_processing",
                "efficient_encoding_algorithms",
                "power_conscious_quality_selection"
            ])
            result.battery_usage_percent = 0.2  # Optimized for low battery usage
            self.adaptation_metrics["battery_optimizations"] += 1
        
        # Network optimization
        if any(config.network_adaptive for config in request.platform_configs):
            optimizations.extend([
                "network_adaptive_quality",
                "bandwidth_optimization",
                "progressive_download_preparation"
            ])
            result.network_usage_mb = min(request.content_size_bytes / (1024 * 1024), 50.0)  # Optimized usage
            self.adaptation_metrics["network_adaptations"] += 1
        
        # Offline preparation
        if any(config.offline_preparation for config in request.platform_configs):
            optimizations.extend([
                "offline_content_preparation",
                "local_cache_optimization",
                "sync_ready_formatting"
            ])
            result.offline_content_prepared = True
        
        # Progressive loading
        if any(config.progressive_loading for config in request.platform_configs):
            optimizations.extend([
                "progressive_loading_enabled",
                "adaptive_streaming_preparation",
                "quality_level_generation"
            ])
            result.progressive_loading_enabled = True
        
        result.mobile_specific_optimizations = optimizations
        
        self.logger.debug(f"Applied {len(optimizations)} mobile optimizations")
    
    async def _prepare_content_for_adaptation(self, request: MobilePlatformRequest, result: MobilePlatformAdaptationResult) -> Dict[str, Any]:
        """Prepare content for platform adaptation."""
        self.logger.debug(f"Preparing content for adaptation: {request.content_id}")
        
        try:
            # Content analysis and preparation
            prepared_content = {
                "original_url": request.content_url,
                "original_format": request.original_format,
                "original_size": request.content_size_bytes,
                "content_type": request.content_type,
                "metadata": request.content_metadata,
                "quality_levels": await self._generate_quality_levels(request),
                "mobile_formats": await self._determine_mobile_formats(request),
                "thumbnails": await self._prepare_thumbnails(request),
                "captions": await self._prepare_captions(request),
                "mobile_optimized": True
            }
            
            self.logger.debug("Content preparation completed successfully")
            return prepared_content
            
        except Exception as e:
            self.logger.error(f"Content preparation failed: {str(e)}")
            return {}
    
    async def _generate_quality_levels(self, request: MobilePlatformRequest) -> List[Dict[str, Any]]:
        """Generate quality levels for mobile optimization."""
        quality_levels = []
        
        # Standard mobile quality levels
        if request.content_type in ["video", "audio"]:
            qualities = [
                {"level": "low", "bitrate": "500k", "resolution": "480p", "mobile_optimized": True},
                {"level": "medium", "bitrate": "1M", "resolution": "720p", "mobile_optimized": True},
                {"level": "high", "bitrate": "2M", "resolution": "1080p", "mobile_optimized": True},
                {"level": "ultra", "bitrate": "4M", "resolution": "1440p", "mobile_optimized": False}
            ]
            quality_levels.extend(qualities)
        elif request.content_type == "image":
            qualities = [
                {"level": "low", "width": 480, "height": 320, "mobile_optimized": True},
                {"level": "medium", "width": 720, "height": 480, "mobile_optimized": True},
                {"level": "high", "width": 1080, "height": 720, "mobile_optimized": True},
                {"level": "ultra", "width": 1920, "height": 1080, "mobile_optimized": False}
            ]
            quality_levels.extend(qualities)
        
        return quality_levels
    
    async def _determine_mobile_formats(self, request: MobilePlatformRequest) -> List[str]:
        """Determine optimal mobile formats for content."""
        mobile_formats = []
        
        if request.content_type == "video":
            mobile_formats = ["mp4", "webm", "mov"]
        elif request.content_type == "audio":
            mobile_formats = ["aac", "mp3", "ogg"]
        elif request.content_type == "image":
            mobile_formats = ["webp", "jpeg", "png"]
        else:
            mobile_formats = [request.original_format]
        
        return mobile_formats
    
    async def _prepare_thumbnails(self, request: MobilePlatformRequest) -> List[Dict[str, Any]]:
        """Prepare thumbnails for mobile platforms."""
        thumbnails = []
        
        if request.content_type in ["video", "audio"]:
            # Standard mobile thumbnail sizes
            thumbnail_specs = [
                {"width": 480, "height": 270, "type": "mobile_small"},
                {"width": 720, "height": 405, "type": "mobile_medium"},
                {"width": 1080, "height": 607, "type": "mobile_large"},
                {"width": 1080, "height": 1080, "type": "mobile_square"},
                {"width": 1080, "height": 1920, "type": "mobile_story"}
            ]
            
            for spec in thumbnail_specs:
                thumbnail = {
                    "url": f"{request.content_url}/thumbnail_{spec['type']}.jpg",
                    "width": spec["width"],
                    "height": spec["height"],
                    "type": spec["type"],
                    "mobile_optimized": True
                }
                thumbnails.append(thumbnail)
        
        return thumbnails
    
    async def _prepare_captions(self, request: MobilePlatformRequest) -> List[Dict[str, Any]]:
        """Prepare captions for mobile accessibility."""
        captions = []
        
        if request.content_type in ["video", "audio"]:
            # Mobile-optimized caption formats
            caption_formats = [
                {"format": "vtt", "language": "en", "mobile_optimized": True},
                {"format": "srt", "language": "en", "mobile_optimized": True},
                {"format": "json", "language": "en", "mobile_optimized": True}
            ]
            
            for cap_format in caption_formats:
                caption = {
                    "url": f"{request.content_url}/captions_{cap_format['language']}.{cap_format['format']}",
                    "format": cap_format["format"],
                    "language": cap_format["language"],
                    "mobile_optimized": cap_format["mobile_optimized"]
                }
                captions.append(caption)
        
        return captions
    
    async def _adapt_for_single_platform(self, request: MobilePlatformRequest, platform_config: MobilePlatformConfiguration, prepared_content: Dict[str, Any]) -> PlatformAdaptationResult:
        """Adapt content for a single mobile platform."""
        self.logger.debug(f"Adapting content for platform: {platform_config.platform.value}")
        
        try:
            platform_specs = self.platform_specs.get(platform_config.platform, {})
            
            # Create platform adaptation result
            result = PlatformAdaptationResult(
                platform=platform_config.platform,
                success=False,
                adapted_content_url="",
                adapted_format="",
                adapted_quality="",
                adapted_size_bytes=0,
                aspect_ratio="",
                duration_seconds=None,
                thumbnails=[],
                optimized_metadata={},
                platform_specific_features={},
                mobile_optimizations=[],
                quality_levels_available=[]
            )
            
            # Apply platform-specific adaptations
            await self._apply_format_adaptation(request, platform_config, platform_specs, prepared_content, result)
            await self._apply_quality_optimization(request, platform_config, platform_specs, prepared_content, result)
            await self._apply_metadata_optimization(request, platform_config, platform_specs, prepared_content, result)
            await self._apply_mobile_features(request, platform_config, platform_specs, prepared_content, result)
            await self._generate_platform_thumbnails(request, platform_config, platform_specs, prepared_content, result)
            await self._optimize_hashtags_for_platform(request, platform_config, platform_specs, prepared_content, result)
            await self._generate_posting_recommendations(request, platform_config, platform_specs, prepared_content, result)
            
            result.success = True
            
            # Track platform-specific metrics
            platform_name = platform_config.platform.value
            if platform_name not in self.adaptation_metrics["platform_adaptations"]:
                self.adaptation_metrics["platform_adaptations"][platform_name] = 0
            self.adaptation_metrics["platform_adaptations"][platform_name] += 1
            
            self.logger.debug(f"Platform adaptation completed for {platform_config.platform.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Platform adaptation failed for {platform_config.platform.value}: {str(e)}")
            return PlatformAdaptationResult(
                platform=platform_config.platform,
                success=False,
                adapted_content_url="",
                adapted_format="",
                adapted_quality="",
                adapted_size_bytes=0,
                aspect_ratio="",
                duration_seconds=None,
                thumbnails=[],
                optimized_metadata={},
                platform_specific_features={},
                mobile_optimizations=[],
                quality_levels_available=[],
                error_message=str(e)
            )
    
    async def _apply_format_adaptation(self, request: MobilePlatformRequest, platform_config: MobilePlatformConfiguration, platform_specs: Dict[str, Any], prepared_content: Dict[str, Any], result: PlatformAdaptationResult):
        """Apply format adaptation for platform."""
        supported_formats = platform_specs.get("supported_formats", [])
        
        if request.original_format in supported_formats:
            result.adapted_format = request.original_format
        else:
            # Choose best format for platform
            if request.content_type == "video":
                result.adapted_format = "mp4"  # Most compatible
            elif request.content_type == "audio":
                result.adapted_format = "aac"  # Best mobile audio format
            elif request.content_type == "image":
                result.adapted_format = "webp"  # Best mobile image format
            else:
                result.adapted_format = request.original_format
        
        result.adapted_content_url = f"{request.content_url}/adapted/{platform_config.platform.value}.{result.adapted_format}"
        result.mobile_optimizations.append("format_adaptation")
    
    async def _apply_quality_optimization(self, request: MobilePlatformRequest, platform_config: MobilePlatformConfiguration, platform_specs: Dict[str, Any], prepared_content: Dict[str, Any], result: PlatformAdaptationResult):
        """Apply quality optimization for platform."""
        quality_levels = prepared_content.get("quality_levels", [])
        
        # Select optimal quality for platform and mobile device
        if platform_config.device_category in [MobileDeviceCategory.SMARTPHONE_IOS, MobileDeviceCategory.SMARTPHONE_ANDROID]:
            result.adapted_quality = "medium"  # Optimal for smartphones
        elif platform_config.device_category in [MobileDeviceCategory.TABLET_IOS, MobileDeviceCategory.TABLET_ANDROID]:
            result.adapted_quality = "high"   # Tablets can handle higher quality
        else:
            result.adapted_quality = "medium"  # Default for mobile web/PWA
        
        # Adjust based on platform limitations
        max_size_mb = platform_specs.get("max_size_mb", 1000)
        if request.content_size_bytes > max_size_mb * 1024 * 1024:
            result.adapted_quality = "low"  # Downgrade if too large
        
        # Set adapted size (simulation)
        quality_multipliers = {"low": 0.3, "medium": 0.6, "high": 0.8, "ultra": 1.0}
        multiplier = quality_multipliers.get(result.adapted_quality, 0.6)
        result.adapted_size_bytes = int(request.content_size_bytes * multiplier)
        
        result.quality_levels_available = [q["level"] for q in quality_levels]
        result.mobile_optimizations.append("quality_optimization")
    
    async def _apply_metadata_optimization(self, request: MobilePlatformRequest, platform_config: MobilePlatformConfiguration, platform_specs: Dict[str, Any], prepared_content: Dict[str, Any], result: PlatformAdaptationResult):
        """Apply metadata optimization for platform."""
        optimized_metadata = {
            "title": request.content_metadata.get("title", ""),
            "description": request.content_metadata.get("description", ""),
            "tags": request.content_metadata.get("tags", []),
            "creator": request.creator_id,
            "creator_type": request.creator_type,
            "platform": platform_config.platform.value,
            "mobile_optimized": True,
            "upload_date": datetime.utcnow().isoformat()
        }
        
        # Platform-specific metadata optimizations
        if platform_config.platform == MobilePlatformType.YOUTUBE_MOBILE:
            optimized_metadata.update({
                "category": "22",  # People & Blogs
                "tags_limit": 500,
                "description_limit": 5000,
                "mobile_features": ["youtube_shorts", "mobile_live"]
            })
        elif platform_config.platform == MobilePlatformType.INSTAGRAM_MOBILE:
            optimized_metadata.update({
                "caption_limit": 2200,
                "hashtag_limit": 30,
                "mobile_features": ["stories", "reels", "igtv"]
            })
        elif platform_config.platform == MobilePlatformType.TIKTOK_MOBILE:
            optimized_metadata.update({
                "description_limit": 150,
                "hashtag_limit": 100,
                "mobile_features": ["effects", "music_sync", "duets"]
            })
        
        result.optimized_metadata = optimized_metadata
        result.mobile_optimizations.append("metadata_optimization")
    
    async def _apply_mobile_features(self, request: MobilePlatformRequest, platform_config: MobilePlatformConfiguration, platform_specs: Dict[str, Any], prepared_content: Dict[str, Any], result: PlatformAdaptationResult):
        """Apply mobile-native features for platform."""
        mobile_features = platform_specs.get("mobile_features", [])
        
        platform_features = {}
        
        for feature in mobile_features:
            if feature == "youtube_shorts" and platform_config.platform == MobilePlatformType.YOUTUBE_MOBILE:
                platform_features["shorts_compatible"] = True
                platform_features["vertical_video"] = True
                result.aspect_ratio = "9:16"
            elif feature == "instagram_stories" and platform_config.platform == MobilePlatformType.INSTAGRAM_MOBILE:
                platform_features["stories_ready"] = True
                platform_features["24h_expiry"] = True
                result.aspect_ratio = "9:16"
            elif feature == "tiktok_effects" and platform_config.platform == MobilePlatformType.TIKTOK_MOBILE:
                platform_features["effects_compatible"] = True
                platform_features["music_sync_ready"] = True
                result.aspect_ratio = "9:16"
            elif feature == "mobile_live" and platform_config.platform in [MobilePlatformType.YOUTUBE_MOBILE, MobilePlatformType.INSTAGRAM_MOBILE]:
                platform_features["live_streaming_ready"] = True
                platform_features["real_time_interaction"] = True
        
        # Set default aspect ratio if not set
        if not result.aspect_ratio:
            if request.content_type == "video":
                result.aspect_ratio = "16:9"  # Default landscape
            elif request.content_type == "image":
                result.aspect_ratio = "1:1"   # Square for most mobile platforms
        
        result.platform_specific_features = platform_features
        result.mobile_optimizations.append("mobile_native_features")
    
    async def _generate_platform_thumbnails(self, request: MobilePlatformRequest, platform_config: MobilePlatformConfiguration, platform_specs: Dict[str, Any], prepared_content: Dict[str, Any], result: PlatformAdaptationResult):
        """Generate platform-specific thumbnails."""
        thumbnail_sizes = platform_specs.get("thumbnail_sizes", ["1280x720"])
        
        thumbnails = []
        for size in thumbnail_sizes:
            width, height = size.split('x')
            thumbnail = {
                "url": f"{request.content_url}/thumbnail_{platform_config.platform.value}_{size}.jpg",
                "width": int(width),
                "height": int(height),
                "platform": platform_config.platform.value,
                "mobile_optimized": True
            }
            thumbnails.append(thumbnail)
        
        result.thumbnails = thumbnails
        result.mobile_optimizations.append("platform_thumbnails")
    
    async def _optimize_hashtags_for_platform(self, request: MobilePlatformRequest, platform_config: MobilePlatformConfiguration, platform_specs: Dict[str, Any], prepared_content: Dict[str, Any], result: PlatformAdaptationResult):
        """Optimize hashtags for specific platform."""
        original_tags = request.content_metadata.get("tags", [])
        optimized_hashtags = []
        
        # Base hashtags from content
        for tag in original_tags:
            if not tag.startswith('#'):
                optimized_hashtags.append(f"#{tag}")
            else:
                optimized_hashtags.append(tag)
        
        # Add platform-specific hashtags
        if platform_config.platform == MobilePlatformType.INSTAGRAM_MOBILE:
            platform_hashtags = ["#instagram", "#mobile", "#content", "#creator"]
            optimized_hashtags.extend(platform_hashtags)
        elif platform_config.platform == MobilePlatformType.TIKTOK_MOBILE:
            platform_hashtags = ["#tiktok", "#viral", "#trending", "#mobile"]
            optimized_hashtags.extend(platform_hashtags)
        elif platform_config.platform == MobilePlatformType.TWITTER_MOBILE:
            platform_hashtags = ["#twitter", "#mobile", "#content"]
            optimized_hashtags.extend(platform_hashtags)
        
        # Add creator-type specific hashtags
        creator_hashtags = {
            "musician": ["#music", "#artist", "#audio"],
            "blogger": ["#blog", "#writing", "#content"],
            "photographer": ["#photography", "#photo", "#visual"],
            "influencer": ["#influencer", "#social", "#lifestyle"],
            "comedian": ["#comedy", "#funny", "#entertainment"]
        }
        
        if request.creator_type in creator_hashtags:
            optimized_hashtags.extend(creator_hashtags[request.creator_type])
        
        # Remove duplicates and limit based on platform
        unique_hashtags = list(set(optimized_hashtags))
        if platform_config.platform == MobilePlatformType.INSTAGRAM_MOBILE:
            result.hashtags_optimized = unique_hashtags[:30]  # Instagram limit
        elif platform_config.platform == MobilePlatformType.TIKTOK_MOBILE:
            result.hashtags_optimized = unique_hashtags[:100] # TikTok character limit consideration
        else:
            result.hashtags_optimized = unique_hashtags[:20]  # General limit
        
        result.mobile_optimizations.append("hashtag_optimization")
    
    async def _generate_posting_recommendations(self, request: MobilePlatformRequest, platform_config: MobilePlatformConfiguration, platform_specs: Dict[str, Any], prepared_content: Dict[str, Any], result: PlatformAdaptationResult):
        """Generate posting recommendations for platform."""
        recommendations = {
            "optimal_posting_time": "12:00",
            "timezone": "UTC",
            "frequency": "daily",
            "mobile_specific_tips": [],
            "engagement_strategies": [],
            "platform_best_practices": []
        }
        
        # Platform-specific recommendations
        if platform_config.platform == MobilePlatformType.INSTAGRAM_MOBILE:
            recommendations.update({
                "optimal_posting_time": "11:00-13:00, 17:00-19:00",
                "frequency": "1-2 times daily",
                "mobile_specific_tips": [
                    "Use Stories for behind-the-scenes content",
                    "Post Reels for maximum reach",
                    "Use relevant hashtags (20-30)",
                    "Engage with comments within first hour"
                ]
            })
        elif platform_config.platform == MobilePlatformType.TIKTOK_MOBILE:
            recommendations.update({
                "optimal_posting_time": "18:00-24:00",
                "frequency": "1-4 times daily",
                "mobile_specific_tips": [
                    "Trending sounds increase visibility",
                    "First 3 seconds are crucial",
                    "Vertical video performs best",
                    "Engage with trending hashtags"
                ]
            })
        elif platform_config.platform == MobilePlatformType.YOUTUBE_MOBILE:
            recommendations.update({
                "optimal_posting_time": "14:00-16:00, 20:00-22:00",
                "frequency": "2-3 times weekly",
                "mobile_specific_tips": [
                    "Custom thumbnails improve CTR",
                    "First 15 seconds determine retention",
                    "Mobile-friendly titles (under 60 chars)",
                    "End screens for mobile viewers"
                ]
            })
        
        # Add general mobile recommendations
        recommendations["mobile_specific_tips"].extend([
            "Optimize for mobile viewing",
            "Use clear, readable fonts",
            "Consider vertical format",
            "Test on different screen sizes"
        ])
        
        result.posting_recommendations = recommendations
        result.mobile_optimizations.append("posting_recommendations")
    
    async def _apply_cross_platform_optimizations(self, request: MobilePlatformRequest, result: MobilePlatformAdaptationResult):
        """Apply cross-platform optimizations."""
        self.logger.debug(f"Applying cross-platform optimizations for {request.content_id}")
        
        optimizations = [
            "unified_content_management",
            "cross_platform_analytics",
            "consistent_branding",
            "synchronized_posting",
            "mobile_cross_platform_optimization"
        ]
        
        # Check for platform consistency
        successful_platforms = [pr for pr in result.platform_results if pr.success]
        if len(successful_platforms) > 1:
            optimizations.extend([
                "multi_platform_deployment",
                "cross_platform_engagement_tracking",
                "unified_mobile_experience"
            ])
        
        result.cross_platform_optimizations = optimizations
        result.quality_optimization_applied = True
        
        self.logger.debug(f"Applied {len(optimizations)} cross-platform optimizations")
    
    async def _generate_analytics_data(self, request: MobilePlatformRequest, result: MobilePlatformAdaptationResult):
        """Generate analytics data for adaptation."""
        analytics = {
            "adaptation_id": result.request_id,
            "content_id": request.content_id,
            "creator_id": request.creator_id,
            "total_platforms": len(request.platform_configs),
            "successful_adaptations": result.total_adapted_platforms,
            "success_rate": result.total_adapted_platforms / len(request.platform_configs) if request.platform_configs else 0,
            "processing_time_ms": result.processing_time_ms,
            "mobile_optimizations_count": len(result.mobile_specific_optimizations),
            "cross_platform_optimizations_count": len(result.cross_platform_optimizations),
            "battery_efficiency": 100 - result.battery_usage_percent,
            "network_efficiency": 100 - min(result.network_usage_mb / 100 * 100, 100),
            "platform_breakdown": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Platform-specific analytics
        for platform_result in result.platform_results:
            analytics["platform_breakdown"][platform_result.platform.value] = {
                "success": platform_result.success,
                "optimizations_applied": len(platform_result.mobile_optimizations),
                "quality_levels": len(platform_result.quality_levels_available),
                "thumbnails_generated": len(platform_result.thumbnails),
                "hashtags_optimized": len(platform_result.hashtags_optimized),
                "mobile_features_enabled": len(platform_result.platform_specific_features)
            }
        
        result.analytics_data = analytics
    
    async def get_adaptation_metrics(self) -> Dict[str, Any]:
        """Get mobile platform adaptation performance metrics."""
        return {
            "adaptation_metrics": self.adaptation_metrics,
            "mobile_optimizations": self.mobile_optimizations,
            "supported_platforms": list(self.platform_specs.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_platform_specifications(self) -> Dict[str, Any]:
        """Get platform specifications and capabilities."""
        return {
            "platform_specifications": self.platform_specs,
            "mobile_optimizations_available": self.mobile_optimizations,
            "adaptation_types_supported": [adaptation_type.value for adaptation_type in MobileAdaptationType],
            "device_categories_supported": [device_cat.value for device_cat in MobileDeviceCategory],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def adapt_batch_platforms(self, requests: List[MobilePlatformRequest]) -> List[MobilePlatformAdaptationResult]:
        """Adapt multiple platform requests in batch."""
        self.logger.info(f"Starting batch platform adaptation for {len(requests)} requests")
        
        tasks = [self.adapt_for_platforms(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Batch platform adaptation failed for request {i}: {str(result)}")
                processed_results.append(MobilePlatformAdaptationResult(
                    request_id=requests[i].request_id,
                    success=False,
                    processing_time_ms=0,
                    battery_usage_percent=0.0,
                    network_usage_mb=0.0,
                    total_adapted_platforms=0,
                    platform_results=[],
                    cross_platform_optimizations=[],
                    mobile_specific_optimizations=[],
                    quality_optimization_applied=False,
                    offline_content_prepared=False,
                    progressive_loading_enabled=False,
                    analytics_data={},
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        self.logger.info(f"Batch platform adaptation completed for {len(processed_results)} requests")
        return processed_results


# Factory function for creating mobile platform adapter
def create_mobile_platform_adapter(config: Optional[Dict[str, Any]] = None) -> MobilePlatformAdapter:
    """
    Factory function to create a mobile platform adapter with mobile-specific optimizations.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        MobilePlatformAdapter: Configured mobile platform adapter
    """
    return MobilePlatformAdapter(config)


# Export key classes and functions
__all__ = [
    "MobilePlatformAdapter",
    "MobilePlatformRequest", 
    "MobilePlatformAdaptationResult",
    "PlatformAdaptationResult",
    "MobilePlatformConfiguration",
    "MobilePlatformType",
    "MobileAdaptationType",
    "MobileDeviceCategory",
    "ContentOptimizationLevel",
    "create_mobile_platform_adapter"
]