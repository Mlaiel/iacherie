"""
Ainflue Platform - Multimedia Formats - Platform-Specific Formats
Platform-specific format optimization and delivery management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"
    SPOTIFY = "spotify"
    APPLE_PODCASTS = "apple_podcasts"
    NETFLIX = "netflix"
    AMAZON_PRIME = "amazon_prime"
    DISNEY_PLUS = "disney_plus"
    WEB = "web"
    MOBILE_IOS = "mobile_ios"
    MOBILE_ANDROID = "mobile_android"
    SMART_TV = "smart_tv"
    GAMING_CONSOLE = "gaming_console"


class ContentType(Enum):
    """Content types for platform optimization"""
    VIDEO_SHORT = "video_short"       # < 60 seconds
    VIDEO_MEDIUM = "video_medium"     # 1-15 minutes
    VIDEO_LONG = "video_long"         # > 15 minutes
    LIVE_STREAM = "live_stream"
    AUDIO_PODCAST = "audio_podcast"
    AUDIO_MUSIC = "audio_music"
    AUDIO_VOICE = "audio_voice"
    IMAGE_PHOTO = "image_photo"
    IMAGE_STORY = "image_story"
    IMAGE_THUMBNAIL = "image_thumbnail"
    ANIMATION_GIF = "animation_gif"
    DOCUMENT = "document"


@dataclass
class FormatSpecification:
    """Platform format specification"""
    container: str = ""
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    
    # Video specifications
    max_resolution: Optional[Tuple[int, int]] = None
    min_resolution: Optional[Tuple[int, int]] = None
    aspect_ratios: List[str] = field(default_factory=list)
    frame_rates: List[float] = field(default_factory=list)
    video_bitrate_range: Optional[Tuple[int, int]] = None
    
    # Audio specifications
    audio_sample_rates: List[int] = field(default_factory=list)
    audio_channels: List[int] = field(default_factory=list)
    audio_bitrate_range: Optional[Tuple[int, int]] = None
    
    # File constraints
    max_file_size: Optional[int] = None
    max_duration: Optional[int] = None
    min_duration: Optional[int] = None
    
    # Quality settings
    quality_presets: List[str] = field(default_factory=list)
    hdr_support: bool = False
    color_space: Optional[str] = None


@dataclass
class PlatformRequirements:
    """Complete platform requirements"""
    platform: Platform
    content_types: Dict[ContentType, FormatSpecification] = field(default_factory=dict)
    upload_limits: Dict[str, Any] = field(default_factory=dict)
    optimization_guidelines: List[str] = field(default_factory=list)
    prohibited_content: List[str] = field(default_factory=list)
    recommended_settings: Dict[str, Any] = field(default_factory=dict)
    api_endpoints: Dict[str, str] = field(default_factory=dict)
    metadata_requirements: Dict[str, Any] = field(default_factory=dict)


class PlatformFormatsManager:
    """Professional platform-specific formats management system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize platform formats manager"""
        self.config = config or {}
        self.platform_requirements: Dict[Platform, PlatformRequirements] = {}
        
        # Initialize platform specifications
        self._initialize_social_platforms()
        self._initialize_streaming_platforms()
        self._initialize_audio_platforms()
        self._initialize_device_platforms()
    
    def _initialize_social_platforms(self) -> None:
        """Initialize social media platform requirements"""
        try:
            # YouTube
            youtube_reqs = PlatformRequirements(
                platform=Platform.YOUTUBE,
                content_types={
                    ContentType.VIDEO_SHORT: FormatSpecification(
                        container="mp4",
                        video_codec="h264",
                        audio_codec="aac",
                        max_resolution=(1920, 1080),
                        aspect_ratios=["9:16", "1:1", "16:9"],
                        frame_rates=[24, 25, 30, 60],
                        video_bitrate_range=(1000, 8000),
                        max_duration=60,
                        max_file_size=15 * 1024 * 1024 * 1024  # 15GB
                    ),
                    ContentType.VIDEO_LONG: FormatSpecification(
                        container="mp4",
                        video_codec="h264",
                        audio_codec="aac",
                        max_resolution=(3840, 2160),  # 4K
                        aspect_ratios=["16:9", "4:3"],
                        frame_rates=[24, 25, 30, 60],
                        video_bitrate_range=(1000, 68000),
                        hdr_support=True,
                        max_file_size=256 * 1024 * 1024 * 1024  # 256GB
                    ),
                    ContentType.LIVE_STREAM: FormatSpecification(
                        container="mp4",
                        video_codec="h264",
                        audio_codec="aac",
                        max_resolution=(3840, 2160),
                        frame_rates=[30, 60],
                        video_bitrate_range=(1000, 51000)
                    )
                },
                upload_limits={
                    "verified_channel_limit": "256GB",
                    "unverified_channel_limit": "15GB",
                    "daily_upload_limit": "unlimited"
                },
                optimization_guidelines=[
                    "Use H.264 codec for maximum compatibility",
                    "Keep bitrate under 8Mbps for HD content",
                    "Use progressive scan (not interlaced)",
                    "Audio should be 48kHz/16-bit or higher"
                ],
                recommended_settings={
                    "video_codec": "h264",
                    "audio_codec": "aac",
                    "container": "mp4",
                    "pixel_format": "yuv420p"
                }
            )
            self.platform_requirements[Platform.YOUTUBE] = youtube_reqs
            
            # TikTok
            tiktok_reqs = PlatformRequirements(
                platform=Platform.TIKTOK,
                content_types={
                    ContentType.VIDEO_SHORT: FormatSpecification(
                        container="mp4",
                        video_codec="h264",
                        audio_codec="aac",
                        max_resolution=(1080, 1920),  # 9:16 vertical
                        min_resolution=(720, 1280),
                        aspect_ratios=["9:16"],
                        frame_rates=[30],
                        video_bitrate_range=(1000, 3000),
                        max_duration=180,  # 3 minutes
                        max_file_size=287 * 1024 * 1024  # 287MB
                    )
                },
                upload_limits={
                    "max_file_size": "287MB",
                    "max_duration": "180 seconds"
                },
                optimization_guidelines=[
                    "Vertical orientation (9:16) strongly recommended",
                    "Keep videos under 100MB for best performance",
                    "Use 30fps for smooth playback",
                    "Audio quality important for engagement"
                ]
            )
            self.platform_requirements[Platform.TIKTOK] = tiktok_reqs
            
            # Instagram
            instagram_reqs = PlatformRequirements(
                platform=Platform.INSTAGRAM,
                content_types={
                    ContentType.VIDEO_SHORT: FormatSpecification(  # Reels
                        container="mp4",
                        video_codec="h264",
                        audio_codec="aac",
                        max_resolution=(1080, 1920),
                        aspect_ratios=["9:16"],
                        frame_rates=[30],
                        max_duration=90,
                        max_file_size=4 * 1024 * 1024 * 1024  # 4GB
                    ),
                    ContentType.VIDEO_MEDIUM: FormatSpecification(  # IGTV
                        container="mp4",
                        video_codec="h264",
                        audio_codec="aac",
                        max_resolution=(1080, 1920),
                        aspect_ratios=["9:16", "16:9", "1:1"],
                        frame_rates=[30],
                        max_duration=3600,  # 60 minutes
                        max_file_size=3.6 * 1024 * 1024 * 1024  # 3.6GB
                    ),
                    ContentType.IMAGE_PHOTO: FormatSpecification(
                        container="jpeg",
                        max_resolution=(1080, 1080),
                        aspect_ratios=["1:1", "4:5", "16:9"],
                        max_file_size=30 * 1024 * 1024  # 30MB
                    ),
                    ContentType.IMAGE_STORY: FormatSpecification(
                        container="jpeg",
                        max_resolution=(1080, 1920),
                        aspect_ratios=["9:16"],
                        max_file_size=30 * 1024 * 1024  # 30MB
                    )
                },
                optimization_guidelines=[
                    "Square (1:1) or vertical (4:5) for feed posts",
                    "Vertical (9:16) for Stories and Reels",
                    "Use high-quality images (1080px minimum)",
                    "Avoid letterboxing or pillarboxing"
                ]
            )
            self.platform_requirements[Platform.INSTAGRAM] = instagram_reqs
            
        except Exception as e:
            logger.error(f"Error initializing social platforms: {e}")
    
    def _initialize_streaming_platforms(self) -> None:
        """Initialize streaming platform requirements"""
        try:
            # Netflix (theoretical requirements for high-quality content)
            netflix_reqs = PlatformRequirements(
                platform=Platform.NETFLIX,
                content_types={
                    ContentType.VIDEO_LONG: FormatSpecification(
                        container="mp4",
                        video_codec="h264",  # Also supports h265
                        audio_codec="aac",
                        max_resolution=(3840, 2160),  # 4K
                        aspect_ratios=["16:9", "2.39:1"],
                        frame_rates=[23.976, 24, 25, 29.97, 30],
                        video_bitrate_range=(5000, 25000),
                        hdr_support=True,
                        color_space="bt2020"
                    )
                },
                optimization_guidelines=[
                    "Professional color grading required",
                    "Dolby Vision/HDR10 support for premium content",
                    "Multiple quality tiers for adaptive streaming",
                    "Closed captioning mandatory"
                ]
            )
            self.platform_requirements[Platform.NETFLIX] = netflix_reqs
            
        except Exception as e:
            logger.error(f"Error initializing streaming platforms: {e}")
    
    def _initialize_audio_platforms(self) -> None:
        """Initialize audio platform requirements"""
        try:
            # Spotify
            spotify_reqs = PlatformRequirements(
                platform=Platform.SPOTIFY,
                content_types={
                    ContentType.AUDIO_MUSIC: FormatSpecification(
                        container="mp3",
                        audio_codec="mp3",
                        audio_sample_rates=[44100],
                        audio_channels=[2],
                        audio_bitrate_range=(320, 320),  # 320kbps preferred
                        max_file_size=200 * 1024 * 1024  # 200MB
                    ),
                    ContentType.AUDIO_PODCAST: FormatSpecification(
                        container="mp3",
                        audio_codec="mp3",
                        audio_sample_rates=[44100],
                        audio_channels=[1, 2],
                        audio_bitrate_range=(96, 320),
                        max_file_size=200 * 1024 * 1024  # 200MB
                    )
                },
                optimization_guidelines=[
                    "320kbps MP3 for music",
                    "128kbps sufficient for spoken content",
                    "Normalize audio levels",
                    "Include proper metadata tags"
                ]
            )
            self.platform_requirements[Platform.SPOTIFY] = spotify_reqs
            
            # Apple Podcasts
            apple_podcasts_reqs = PlatformRequirements(
                platform=Platform.APPLE_PODCASTS,
                content_types={
                    ContentType.AUDIO_PODCAST: FormatSpecification(
                        container="mp3",
                        audio_codec="mp3",
                        audio_sample_rates=[44100],
                        audio_channels=[1, 2],
                        audio_bitrate_range=(64, 320),
                        max_file_size=500 * 1024 * 1024  # 500MB
                    )
                },
                optimization_guidelines=[
                    "Mono for speech, stereo for music",
                    "Consistent volume levels",
                    "High-quality artwork (3000x3000px)",
                    "Proper RSS feed structure"
                ]
            )
            self.platform_requirements[Platform.APPLE_PODCASTS] = apple_podcasts_reqs
            
        except Exception as e:
            logger.error(f"Error initializing audio platforms: {e}")
    
    def _initialize_device_platforms(self) -> None:
        """Initialize device-specific requirements"""
        try:
            # Mobile iOS
            ios_reqs = PlatformRequirements(
                platform=Platform.MOBILE_IOS,
                content_types={
                    ContentType.VIDEO_MEDIUM: FormatSpecification(
                        container="mp4",
                        video_codec="h264",
                        audio_codec="aac",
                        max_resolution=(1920, 1080),
                        aspect_ratios=["16:9", "9:16", "1:1"],
                        frame_rates=[30, 60],
                        video_bitrate_range=(1000, 5000)
                    )
                },
                optimization_guidelines=[
                    "Use baseline H.264 profile for compatibility",
                    "Progressive download support",
                    "Optimize for battery life",
                    "Support various screen sizes"
                ]
            )
            self.platform_requirements[Platform.MOBILE_IOS] = ios_reqs
            
            # Smart TV
            smart_tv_reqs = PlatformRequirements(
                platform=Platform.SMART_TV,
                content_types={
                    ContentType.VIDEO_LONG: FormatSpecification(
                        container="mp4",
                        video_codec="h264",
                        audio_codec="aac",
                        max_resolution=(3840, 2160),
                        aspect_ratios=["16:9"],
                        frame_rates=[24, 30, 60],
                        video_bitrate_range=(5000, 25000),
                        hdr_support=True
                    )
                },
                optimization_guidelines=[
                    "High bitrate for large screens",
                    "HDR support for premium content",
                    "Dolby Audio support",
                    "Adaptive bitrate streaming"
                ]
            )
            self.platform_requirements[Platform.SMART_TV] = smart_tv_reqs
            
        except Exception as e:
            logger.error(f"Error initializing device platforms: {e}")
    
    def get_platform_requirements(
        self,
        platform: Platform,
        content_type: Optional[ContentType] = None
    ) -> Optional[Union[PlatformRequirements, FormatSpecification]]:
        """Get requirements for specific platform and content type"""
        try:
            if platform not in self.platform_requirements:
                return None
            
            platform_reqs = self.platform_requirements[platform]
            
            if content_type:
                return platform_reqs.content_types.get(content_type)
            
            return platform_reqs
            
        except Exception as e:
            logger.error(f"Error getting platform requirements: {e}")
            return None
    
    def validate_content_for_platform(
        self,
        file_path: Union[str, Path],
        platform: Platform,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Validate content against platform requirements"""
        try:
            file_path = Path(file_path)
            
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Get platform requirements
            spec = self.get_platform_requirements(platform, content_type)
            if not spec:
                validation_result["errors"].append(f"No requirements found for {platform.value}/{content_type.value}")
                validation_result["valid"] = False
                return validation_result
            
            # Check file size
            if spec.max_file_size:
                file_size = file_path.stat().st_size
                if file_size > spec.max_file_size:
                    validation_result["errors"].append(
                        f"File size {file_size} bytes exceeds maximum {spec.max_file_size} bytes"
                    )
                    validation_result["valid"] = False
            
            # Simplified validation (in production, would analyze actual media properties)
            file_extension = file_path.suffix.lower()
            
            # Check container format
            if spec.container:
                expected_extensions = {
                    "mp4": [".mp4", ".m4v"],
                    "jpeg": [".jpg", ".jpeg"],
                    "mp3": [".mp3"]
                }
                
                if spec.container in expected_extensions:
                    if file_extension not in expected_extensions[spec.container]:
                        validation_result["errors"].append(
                            f"File extension {file_extension} doesn't match container {spec.container}"
                        )
                        validation_result["valid"] = False
            
            # Add recommendations based on platform
            platform_reqs = self.platform_requirements[platform]
            validation_result["recommendations"].extend(platform_reqs.optimization_guidelines)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating content: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "recommendations": []
            }
    
    def get_optimization_settings(
        self,
        platform: Platform,
        content_type: ContentType,
        quality_priority: str = "balanced"  # "size", "quality", "balanced"
    ) -> Dict[str, Any]:
        """Get optimization settings for platform and content type"""
        try:
            spec = self.get_platform_requirements(platform, content_type)
            if not spec:
                return {}
            
            settings = {
                "container": spec.container,
                "video_codec": spec.video_codec,
                "audio_codec": spec.audio_codec
            }
            
            # Video settings
            if spec.video_codec:
                if spec.max_resolution:
                    settings["resolution"] = f"{spec.max_resolution[0]}x{spec.max_resolution[1]}"
                
                if spec.frame_rates:
                    # Choose frame rate based on content type
                    if content_type == ContentType.VIDEO_SHORT:
                        settings["frame_rate"] = 30  # Good for social media
                    else:
                        settings["frame_rate"] = spec.frame_rates[0]
                
                if spec.video_bitrate_range:
                    if quality_priority == "size":
                        settings["video_bitrate"] = spec.video_bitrate_range[0]
                    elif quality_priority == "quality":
                        settings["video_bitrate"] = spec.video_bitrate_range[1]
                    else:  # balanced
                        settings["video_bitrate"] = (spec.video_bitrate_range[0] + spec.video_bitrate_range[1]) // 2
            
            # Audio settings
            if spec.audio_codec:
                if spec.audio_sample_rates:
                    settings["audio_sample_rate"] = spec.audio_sample_rates[0]
                
                if spec.audio_channels:
                    # Choose mono for voice, stereo for music
                    if content_type in [ContentType.AUDIO_VOICE, ContentType.AUDIO_PODCAST]:
                        settings["audio_channels"] = 1
                    else:
                        settings["audio_channels"] = 2
                
                if spec.audio_bitrate_range:
                    if quality_priority == "size":
                        settings["audio_bitrate"] = spec.audio_bitrate_range[0]
                    elif quality_priority == "quality":
                        settings["audio_bitrate"] = spec.audio_bitrate_range[1]
                    else:  # balanced
                        settings["audio_bitrate"] = (spec.audio_bitrate_range[0] + spec.audio_bitrate_range[1]) // 2
            
            # Platform-specific optimizations
            platform_reqs = self.platform_requirements[platform]
            if platform_reqs.recommended_settings:
                settings.update(platform_reqs.recommended_settings)
            
            return settings
            
        except Exception as e:
            logger.error(f"Error getting optimization settings: {e}")
            return {}
    
    def suggest_platforms_for_content(
        self,
        content_metadata: Dict[str, Any]
    ) -> List[Tuple[Platform, float]]:
        """Suggest best platforms for content based on characteristics"""
        try:
            suggestions = []
            
            content_type = content_metadata.get("type", ContentType.VIDEO_MEDIUM)
            duration = content_metadata.get("duration", 0)
            aspect_ratio = content_metadata.get("aspect_ratio", "16:9")
            resolution = content_metadata.get("resolution", (1920, 1080))
            
            for platform, reqs in self.platform_requirements.items():
                if content_type not in reqs.content_types:
                    continue
                
                spec = reqs.content_types[content_type]
                score = 0
                
                # Duration compatibility
                if spec.max_duration:
                    if duration <= spec.max_duration:
                        score += 30
                    else:
                        continue  # Incompatible
                
                # Aspect ratio compatibility
                if aspect_ratio in spec.aspect_ratios:
                    score += 25
                elif not spec.aspect_ratios:  # No restriction
                    score += 15
                
                # Resolution compatibility
                if spec.max_resolution:
                    if (resolution[0] <= spec.max_resolution[0] and 
                        resolution[1] <= spec.max_resolution[1]):
                        score += 20
                
                # Content type specific scoring
                if content_type == ContentType.VIDEO_SHORT:
                    if platform in [Platform.TIKTOK, Platform.INSTAGRAM, Platform.YOUTUBE]:
                        score += 25  # These platforms prioritize short content
                
                if content_type == ContentType.AUDIO_PODCAST:
                    if platform in [Platform.SPOTIFY, Platform.APPLE_PODCASTS]:
                        score += 30  # Audio-focused platforms
                
                # Calculate final score as percentage
                final_score = min(score / 100.0, 1.0)
                
                if final_score > 0.5:  # Only suggest if reasonably compatible
                    suggestions.append((platform, final_score))
            
            # Sort by score descending
            suggestions.sort(key=lambda x: x[1], reverse=True)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting platforms: {e}")
            return []
    
    def get_multi_platform_settings(
        self,
        platforms: List[Platform],
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Get settings optimized for multiple platforms"""
        try:
            if not platforms:
                return {}
            
            # Get requirements for all platforms
            all_specs = []
            for platform in platforms:
                spec = self.get_platform_requirements(platform, content_type)
                if spec:
                    all_specs.append(spec)
            
            if not all_specs:
                return {}
            
            # Find common denominator settings
            settings = {}
            
            # Container: use most compatible (usually MP4)
            containers = [spec.container for spec in all_specs if spec.container]
            if "mp4" in containers:
                settings["container"] = "mp4"
            elif containers:
                settings["container"] = containers[0]
            
            # Video codec: prefer H.264 for compatibility
            video_codecs = [spec.video_codec for spec in all_specs if spec.video_codec]
            if "h264" in video_codecs:
                settings["video_codec"] = "h264"
            elif video_codecs:
                settings["video_codec"] = video_codecs[0]
            
            # Audio codec: prefer AAC
            audio_codecs = [spec.audio_codec for spec in all_specs if spec.audio_codec]
            if "aac" in audio_codecs:
                settings["audio_codec"] = "aac"
            elif audio_codecs:
                settings["audio_codec"] = audio_codecs[0]
            
            # Resolution: use minimum of maximums
            max_resolutions = [spec.max_resolution for spec in all_specs if spec.max_resolution]
            if max_resolutions:
                min_width = min(res[0] for res in max_resolutions)
                min_height = min(res[1] for res in max_resolutions)
                settings["max_resolution"] = (min_width, min_height)
            
            # Bitrate: use minimum of maximums for video
            video_bitrates = [spec.video_bitrate_range[1] for spec in all_specs 
                             if spec.video_bitrate_range]
            if video_bitrates:
                settings["max_video_bitrate"] = min(video_bitrates)
            
            # File size: use minimum
            file_sizes = [spec.max_file_size for spec in all_specs if spec.max_file_size]
            if file_sizes:
                settings["max_file_size"] = min(file_sizes)
            
            # Duration: use minimum
            durations = [spec.max_duration for spec in all_specs if spec.max_duration]
            if durations:
                settings["max_duration"] = min(durations)
            
            return settings
            
        except Exception as e:
            logger.error(f"Error getting multi-platform settings: {e}")
            return {}
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Get analytics about platform requirements"""
        try:
            analytics = {
                "total_platforms": len(self.platform_requirements),
                "platform_categories": {
                    "social_media": 0,
                    "streaming": 0,
                    "audio": 0,
                    "devices": 0
                },
                "supported_content_types": {},
                "common_codecs": {
                    "video": {},
                    "audio": {}
                },
                "resolution_support": {},
                "format_compatibility": {}
            }
            
            social_platforms = [Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM, Platform.FACEBOOK, Platform.TWITTER]
            streaming_platforms = [Platform.NETFLIX, Platform.AMAZON_PRIME, Platform.DISNEY_PLUS]
            audio_platforms = [Platform.SPOTIFY, Platform.APPLE_PODCASTS]
            device_platforms = [Platform.MOBILE_IOS, Platform.MOBILE_ANDROID, Platform.SMART_TV]
            
            for platform, reqs in self.platform_requirements.items():
                # Categorize platforms
                if platform in social_platforms:
                    analytics["platform_categories"]["social_media"] += 1
                elif platform in streaming_platforms:
                    analytics["platform_categories"]["streaming"] += 1
                elif platform in audio_platforms:
                    analytics["platform_categories"]["audio"] += 1
                elif platform in device_platforms:
                    analytics["platform_categories"]["devices"] += 1
                
                # Count content types
                for content_type in reqs.content_types.keys():
                    content_type_str = content_type.value
                    analytics["supported_content_types"][content_type_str] = analytics["supported_content_types"].get(content_type_str, 0) + 1
                
                # Count codecs
                for spec in reqs.content_types.values():
                    if spec.video_codec:
                        analytics["common_codecs"]["video"][spec.video_codec] = analytics["common_codecs"]["video"].get(spec.video_codec, 0) + 1
                    if spec.audio_codec:
                        analytics["common_codecs"]["audio"][spec.audio_codec] = analytics["common_codecs"]["audio"].get(spec.audio_codec, 0) + 1
                    
                    # Count resolutions
                    if spec.max_resolution:
                        res_str = f"{spec.max_resolution[0]}x{spec.max_resolution[1]}"
                        analytics["resolution_support"][res_str] = analytics["resolution_support"].get(res_str, 0) + 1
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting platform analytics: {e}")
            return {}


# Export main classes
__all__ = [
    'PlatformFormatsManager',
    'PlatformRequirements',
    'FormatSpecification',
    'Platform',
    'ContentType'
]