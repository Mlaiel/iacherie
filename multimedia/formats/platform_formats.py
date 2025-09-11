"""
Platform-Specific Formats Module for Ainflue Platform
Platform-optimized format handling and recommendations

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, List, Optional, Union, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Platform categories"""
    SOCIAL_MEDIA = "social_media"
    STREAMING = "streaming"
    MOBILE = "mobile"
    WEB = "web"
    BROADCAST = "broadcast"
    GAMING = "gaming"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ContentCategory(Enum):
    """Content categories for platform optimization"""
    SHORT_FORM = "short_form"  # TikTok, Instagram Reels
    LONG_FORM = "long_form"    # YouTube, Twitch
    LIVE_STREAM = "live_stream"
    STORY = "story"            # Instagram/Facebook Stories
    FEED_POST = "feed_post"    # Instagram/Facebook feed
    THUMBNAIL = "thumbnail"
    PROFILE = "profile"
    BANNER = "banner"
    PODCAST = "podcast"
    MUSIC = "music"


@dataclass
class ResolutionSpec:
    """Resolution specifications"""
    width: int
    height: int
    aspect_ratio: str
    is_preferred: bool = False
    min_bitrate: Optional[int] = None
    max_bitrate: Optional[int] = None


@dataclass
class AudioSpec:
    """Audio specifications"""
    sample_rate: int
    channels: int
    bitrate_range: Tuple[int, int]
    codec_preference: List[str]


@dataclass
class PlatformLimits:
    """Platform content limits"""
    max_file_size: Optional[int] = None  # bytes
    max_duration: Optional[int] = None   # seconds
    min_duration: Optional[int] = None   # seconds
    max_bitrate: Optional[int] = None    # kbps
    max_framerate: Optional[float] = None


@dataclass
class PlatformFormat:
    """Platform-specific format specification"""
    platform_id: str
    platform_name: str
    platform_type: PlatformType
    content_category: ContentCategory
    
    # Video specifications
    supported_video_codecs: List[str]
    preferred_video_codec: str
    supported_resolutions: List[ResolutionSpec]
    preferred_resolution: ResolutionSpec
    supported_framerates: List[float]
    preferred_framerate: float
    
    # Audio specifications
    supported_audio_codecs: List[str]
    preferred_audio_codec: str
    audio_spec: AudioSpec
    
    # Container and format
    supported_containers: List[str]
    preferred_container: str
    supported_image_formats: List[str] = field(default_factory=list)
    
    # Platform limits
    limits: PlatformLimits = field(default_factory=PlatformLimits)
    
    # Quality and optimization
    quality_presets: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    encoding_tips: List[str] = field(default_factory=list)
    
    # Metadata and features
    supports_hdr: bool = False
    supports_dolby_vision: bool = False
    supports_dolby_atmos: bool = False
    supports_closed_captions: bool = False
    supports_chapters: bool = False
    
    # Upload specifications
    upload_requirements: Dict[str, Any] = field(default_factory=dict)
    processing_notes: List[str] = field(default_factory=list)


class PlatformFormatRegistry:
    """
    Registry for platform-specific format requirements and optimizations
    Manages format specifications for major content platforms
    """
    
    def __init__(self):
        self.platforms: Dict[str, Dict[str, PlatformFormat]] = {}
        self.platform_aliases: Dict[str, str] = {}
        self._initialize_platform_formats()
    
    def _initialize_platform_formats(self):
        """Initialize registry with major platform specifications"""
        
        # YouTube Specifications
        self._register_youtube_formats()
        
        # TikTok Specifications
        self._register_tiktok_formats()
        
        # Instagram Specifications
        self._register_instagram_formats()
        
        # Facebook Specifications
        self._register_facebook_formats()
        
        # Twitter Specifications
        self._register_twitter_formats()
        
        # LinkedIn Specifications
        self._register_linkedin_formats()
        
        # Twitch Specifications
        self._register_twitch_formats()
        
        # Spotify Specifications
        self._register_spotify_formats()
        
        # Netflix/Streaming Specifications
        self._register_streaming_formats()
    
    def _register_youtube_formats(self):
        """Register YouTube format specifications"""
        
        # YouTube Long-form Video
        youtube_longform = PlatformFormat(
            platform_id="youtube_longform",
            platform_name="YouTube",
            platform_type=PlatformType.STREAMING,
            content_category=ContentCategory.LONG_FORM,
            supported_video_codecs=["h264", "h265", "vp9", "av1"],
            preferred_video_codec="h264",
            supported_resolutions=[
                ResolutionSpec(426, 240, "16:9"),
                ResolutionSpec(640, 360, "16:9"),
                ResolutionSpec(854, 480, "16:9"),
                ResolutionSpec(1280, 720, "16:9"),
                ResolutionSpec(1920, 1080, "16:9", is_preferred=True, min_bitrate=8000, max_bitrate=12000),
                ResolutionSpec(2560, 1440, "16:9", min_bitrate=16000, max_bitrate=24000),
                ResolutionSpec(3840, 2160, "16:9", min_bitrate=35000, max_bitrate=68000),
            ],
            preferred_resolution=ResolutionSpec(1920, 1080, "16:9", is_preferred=True),
            supported_framerates=[23.976, 24, 25, 29.97, 30, 50, 59.94, 60],
            preferred_framerate=30,
            supported_audio_codecs=["aac", "opus"],
            preferred_audio_codec="aac",
            audio_spec=AudioSpec(
                sample_rate=48000,
                channels=2,
                bitrate_range=(128, 384),
                codec_preference=["aac", "opus"]
            ),
            supported_containers=["mp4", "mov", "webm", "flv", "avi", "wmv", "mkv"],
            preferred_container="mp4",
            limits=PlatformLimits(
                max_file_size=256 * 1024 * 1024 * 1024,  # 256GB
                max_duration=12 * 3600,  # 12 hours
                min_duration=1,
                max_framerate=60
            ),
            quality_presets={
                "1080p": {
                    "video_bitrate": 8000,
                    "audio_bitrate": 192,
                    "framerate": 30
                },
                "4k": {
                    "video_bitrate": 35000,
                    "audio_bitrate": 384,
                    "framerate": 30
                }
            },
            supports_hdr=True,
            supports_closed_captions=True,
            supports_chapters=True,
            encoding_tips=[
                "Use H.264 with High profile for best compatibility",
                "Progressive scan, closed GOP",
                "Use 2-pass encoding for better quality",
                "Include metadata for better discoverability"
            ],
            upload_requirements={
                "recommended_bitrate": "VBR, 2-pass",
                "color_space": "Rec. 709",
                "chroma_subsampling": "4:2:0"
            }
        )
        self.register_platform_format(youtube_longform)
        
        # YouTube Shorts
        youtube_shorts = PlatformFormat(
            platform_id="youtube_shorts",
            platform_name="YouTube Shorts",
            platform_type=PlatformType.SOCIAL_MEDIA,
            content_category=ContentCategory.SHORT_FORM,
            supported_video_codecs=["h264", "h265"],
            preferred_video_codec="h264",
            supported_resolutions=[
                ResolutionSpec(1080, 1920, "9:16", is_preferred=True, min_bitrate=4000, max_bitrate=8000),
                ResolutionSpec(720, 1280, "9:16", min_bitrate=2500, max_bitrate=5000),
            ],
            preferred_resolution=ResolutionSpec(1080, 1920, "9:16", is_preferred=True),
            supported_framerates=[30, 60],
            preferred_framerate=30,
            supported_audio_codecs=["aac"],
            preferred_audio_codec="aac",
            audio_spec=AudioSpec(
                sample_rate=48000,
                channels=2,
                bitrate_range=(128, 192),
                codec_preference=["aac"]
            ),
            supported_containers=["mp4"],
            preferred_container="mp4",
            limits=PlatformLimits(
                max_file_size=15 * 1024 * 1024 * 1024,  # 15GB
                max_duration=60,
                min_duration=1
            ),
            quality_presets={
                "standard": {
                    "video_bitrate": 6000,
                    "audio_bitrate": 128,
                    "framerate": 30
                }
            },
            encoding_tips=[
                "Vertical orientation mandatory (9:16)",
                "Keep text readable on mobile screens",
                "Strong hook in first 3 seconds",
                "Use trending audio when appropriate"
            ]
        )
        self.register_platform_format(youtube_shorts)
    
    def _register_tiktok_formats(self):
        """Register TikTok format specifications"""
        
        tiktok = PlatformFormat(
            platform_id="tiktok",
            platform_name="TikTok",
            platform_type=PlatformType.SOCIAL_MEDIA,
            content_category=ContentCategory.SHORT_FORM,
            supported_video_codecs=["h264", "h265"],
            preferred_video_codec="h264",
            supported_resolutions=[
                ResolutionSpec(1080, 1920, "9:16", is_preferred=True, min_bitrate=4000, max_bitrate=8000),
                ResolutionSpec(720, 1280, "9:16", min_bitrate=2000, max_bitrate=4000),
            ],
            preferred_resolution=ResolutionSpec(1080, 1920, "9:16", is_preferred=True),
            supported_framerates=[25, 30],
            preferred_framerate=30,
            supported_audio_codecs=["aac"],
            preferred_audio_codec="aac",
            audio_spec=AudioSpec(
                sample_rate=44100,
                channels=2,
                bitrate_range=(128, 192),
                codec_preference=["aac"]
            ),
            supported_containers=["mp4"],
            preferred_container="mp4",
            limits=PlatformLimits(
                max_file_size=287 * 1024 * 1024,  # 287MB
                max_duration=180,  # 3 minutes (extended)
                min_duration=1
            ),
            quality_presets={
                "standard": {
                    "video_bitrate": 6000,
                    "audio_bitrate": 128,
                    "framerate": 30
                },
                "high_quality": {
                    "video_bitrate": 8000,
                    "audio_bitrate": 192,
                    "framerate": 30
                }
            },
            encoding_tips=[
                "Vertical video mandatory",
                "Strong visual hook in first frame",
                "Text should be large and readable",
                "Use TikTok's built-in audio library for better reach",
                "Optimize for mobile viewing"
            ],
            upload_requirements={
                "aspect_ratio": "9:16 (recommended)",
                "color_space": "sRGB",
                "progressive_scan": True
            }
        )
        self.register_platform_format(tiktok)
    
    def _register_instagram_formats(self):
        """Register Instagram format specifications"""
        
        # Instagram Feed Video
        instagram_feed = PlatformFormat(
            platform_id="instagram_feed",
            platform_name="Instagram Feed",
            platform_type=PlatformType.SOCIAL_MEDIA,
            content_category=ContentCategory.FEED_POST,
            supported_video_codecs=["h264"],
            preferred_video_codec="h264",
            supported_resolutions=[
                ResolutionSpec(1080, 1080, "1:1", is_preferred=True, min_bitrate=3500, max_bitrate=5000),
                ResolutionSpec(1080, 1350, "4:5", min_bitrate=3500, max_bitrate=5000),
                ResolutionSpec(1920, 1080, "16:9", min_bitrate=3500, max_bitrate=5000),
            ],
            preferred_resolution=ResolutionSpec(1080, 1080, "1:1", is_preferred=True),
            supported_framerates=[30],
            preferred_framerate=30,
            supported_audio_codecs=["aac"],
            preferred_audio_codec="aac",
            audio_spec=AudioSpec(
                sample_rate=48000,
                channels=2,
                bitrate_range=(128, 192),
                codec_preference=["aac"]
            ),
            supported_containers=["mp4"],
            preferred_container="mp4",
            supported_image_formats=["jpeg", "png", "heif"],
            limits=PlatformLimits(
                max_file_size=100 * 1024 * 1024,  # 100MB
                max_duration=60,
                min_duration=3
            ),
            quality_presets={
                "square": {
                    "resolution": "1080x1080",
                    "video_bitrate": 4000,
                    "audio_bitrate": 128
                },
                "portrait": {
                    "resolution": "1080x1350",
                    "video_bitrate": 4000,
                    "audio_bitrate": 128
                }
            },
            encoding_tips=[
                "Square format (1:1) performs best",
                "High contrast and saturation work well",
                "Include captions for accessibility",
                "First frame should be engaging thumbnail"
            ]
        )
        self.register_platform_format(instagram_feed)
        
        # Instagram Reels
        instagram_reels = PlatformFormat(
            platform_id="instagram_reels",
            platform_name="Instagram Reels",
            platform_type=PlatformType.SOCIAL_MEDIA,
            content_category=ContentCategory.SHORT_FORM,
            supported_video_codecs=["h264"],
            preferred_video_codec="h264",
            supported_resolutions=[
                ResolutionSpec(1080, 1920, "9:16", is_preferred=True, min_bitrate=4000, max_bitrate=6000),
            ],
            preferred_resolution=ResolutionSpec(1080, 1920, "9:16", is_preferred=True),
            supported_framerates=[30],
            preferred_framerate=30,
            supported_audio_codecs=["aac"],
            preferred_audio_codec="aac",
            audio_spec=AudioSpec(
                sample_rate=48000,
                channels=2,
                bitrate_range=(128, 192),
                codec_preference=["aac"]
            ),
            supported_containers=["mp4"],
            preferred_container="mp4",
            limits=PlatformLimits(
                max_file_size=100 * 1024 * 1024,  # 100MB
                max_duration=90,
                min_duration=1
            ),
            quality_presets={
                "standard": {
                    "video_bitrate": 5000,
                    "audio_bitrate": 128,
                    "framerate": 30
                }
            },
            encoding_tips=[
                "Vertical orientation required",
                "Use trending audio from Instagram library",
                "Strong visual hook in first 3 seconds",
                "Keep text large and readable on mobile"
            ]
        )
        self.register_platform_format(instagram_reels)
        
        # Instagram Stories
        instagram_stories = PlatformFormat(
            platform_id="instagram_stories",
            platform_name="Instagram Stories",
            platform_type=PlatformType.SOCIAL_MEDIA,
            content_category=ContentCategory.STORY,
            supported_video_codecs=["h264"],
            preferred_video_codec="h264",
            supported_resolutions=[
                ResolutionSpec(1080, 1920, "9:16", is_preferred=True, min_bitrate=1000, max_bitrate=2000),
            ],
            preferred_resolution=ResolutionSpec(1080, 1920, "9:16", is_preferred=True),
            supported_framerates=[30],
            preferred_framerate=30,
            supported_audio_codecs=["aac"],
            preferred_audio_codec="aac",
            audio_spec=AudioSpec(
                sample_rate=48000,
                channels=2,
                bitrate_range=(96, 128),
                codec_preference=["aac"]
            ),
            supported_containers=["mp4"],
            preferred_container="mp4",
            supported_image_formats=["jpeg", "png"],
            limits=PlatformLimits(
                max_file_size=30 * 1024 * 1024,  # 30MB
                max_duration=15,
                min_duration=1
            ),
            quality_presets={
                "standard": {
                    "video_bitrate": 1500,
                    "audio_bitrate": 96,
                    "framerate": 30
                }
            },
            encoding_tips=[
                "Vertical full-screen format",
                "Consider safe areas for UI elements",
                "Use bright, high-contrast visuals",
                "Keep content ephemeral and engaging"
            ]
        )
        self.register_platform_format(instagram_stories)
    
    def _register_facebook_formats(self):
        """Register Facebook format specifications"""
        
        facebook_feed = PlatformFormat(
            platform_id="facebook_feed",
            platform_name="Facebook Feed",
            platform_type=PlatformType.SOCIAL_MEDIA,
            content_category=ContentCategory.FEED_POST,
            supported_video_codecs=["h264"],
            preferred_video_codec="h264",
            supported_resolutions=[
                ResolutionSpec(1280, 720, "16:9", min_bitrate=2000, max_bitrate=4000),
                ResolutionSpec(1920, 1080, "16:9", is_preferred=True, min_bitrate=4000, max_bitrate=8000),
                ResolutionSpec(1080, 1080, "1:1", min_bitrate=4000, max_bitrate=8000),
            ],
            preferred_resolution=ResolutionSpec(1920, 1080, "16:9", is_preferred=True),
            supported_framerates=[30],
            preferred_framerate=30,
            supported_audio_codecs=["aac"],
            preferred_audio_codec="aac",
            audio_spec=AudioSpec(
                sample_rate=48000,
                channels=2,
                bitrate_range=(128, 320),
                codec_preference=["aac"]
            ),
            supported_containers=["mp4", "mov"],
            preferred_container="mp4",
            supported_image_formats=["jpeg", "png"],
            limits=PlatformLimits(
                max_file_size=10 * 1024 * 1024 * 1024,  # 10GB
                max_duration=240 * 60,  # 240 minutes
                min_duration=1
            ),
            quality_presets={
                "1080p": {
                    "video_bitrate": 6000,
                    "audio_bitrate": 192,
                    "framerate": 30
                },
                "720p": {
                    "video_bitrate": 3000,
                    "audio_bitrate": 128,
                    "framerate": 30
                }
            },
            supports_closed_captions=True,
            encoding_tips=[
                "Include captions - many users watch without sound",
                "Square videos (1:1) get more engagement in feed",
                "First 3 seconds are crucial for retention",
                "Use Facebook's native upload for best quality"
            ]
        )
        self.register_platform_format(facebook_feed)
    
    def _register_twitter_formats(self):
        """Register Twitter format specifications"""
        
        twitter_video = PlatformFormat(
            platform_id="twitter_video",
            platform_name="Twitter Video",
            platform_type=PlatformType.SOCIAL_MEDIA,
            content_category=ContentCategory.FEED_POST,
            supported_video_codecs=["h264"],
            preferred_video_codec="h264",
            supported_resolutions=[
                ResolutionSpec(1280, 720, "16:9", min_bitrate=2000, max_bitrate=5000),
                ResolutionSpec(720, 720, "1:1", min_bitrate=2000, max_bitrate=5000),
                ResolutionSpec(720, 1280, "9:16", min_bitrate=2000, max_bitrate=5000),
            ],
            preferred_resolution=ResolutionSpec(1280, 720, "16:9"),
            supported_framerates=[29.97, 30],
            preferred_framerate=30,
            supported_audio_codecs=["aac"],
            preferred_audio_codec="aac",
            audio_spec=AudioSpec(
                sample_rate=44100,
                channels=2,
                bitrate_range=(128, 192),
                codec_preference=["aac"]
            ),
            supported_containers=["mp4"],
            preferred_container="mp4",
            supported_image_formats=["jpeg", "png", "gif"],
            limits=PlatformLimits(
                max_file_size=512 * 1024 * 1024,  # 512MB
                max_duration=140,  # 2 minutes 20 seconds
                min_duration=0.5
            ),
            quality_presets={
                "standard": {
                    "video_bitrate": 3000,
                    "audio_bitrate": 128,
                    "framerate": 30
                }
            },
            encoding_tips=[
                "Auto-play is silent, include captions",
                "First frame should work as thumbnail",
                "Keep videos concise and engaging",
                "720p resolution is sufficient for most content"
            ]
        )
        self.register_platform_format(twitter_video)
    
    def _register_linkedin_formats(self):
        """Register LinkedIn format specifications"""
        
        linkedin_video = PlatformFormat(
            platform_id="linkedin_video",
            platform_name="LinkedIn Video",
            platform_type=PlatformType.SOCIAL_MEDIA,
            content_category=ContentCategory.FEED_POST,
            supported_video_codecs=["h264"],
            preferred_video_codec="h264",
            supported_resolutions=[
                ResolutionSpec(1920, 1080, "16:9", is_preferred=True, min_bitrate=3000, max_bitrate=6000),
                ResolutionSpec(1080, 1080, "1:1", min_bitrate=3000, max_bitrate=6000),
            ],
            preferred_resolution=ResolutionSpec(1920, 1080, "16:9", is_preferred=True),
            supported_framerates=[30],
            preferred_framerate=30,
            supported_audio_codecs=["aac"],
            preferred_audio_codec="aac",
            audio_spec=AudioSpec(
                sample_rate=48000,
                channels=2,
                bitrate_range=(128, 192),
                codec_preference=["aac"]
            ),
            supported_containers=["mp4"],
            preferred_container="mp4",
            limits=PlatformLimits(
                max_file_size=5 * 1024 * 1024 * 1024,  # 5GB
                max_duration=10 * 60,  # 10 minutes
                min_duration=3
            ),
            quality_presets={
                "professional": {
                    "video_bitrate": 5000,
                    "audio_bitrate": 192,
                    "framerate": 30
                }
            },
            supports_closed_captions=True,
            encoding_tips=[
                "Professional content performs best",
                "Include captions for accessibility",
                "Landscape orientation preferred",
                "Clear audio is essential for business content"
            ]
        )
        self.register_platform_format(linkedin_video)
    
    def _register_twitch_formats(self):
        """Register Twitch format specifications"""
        
        twitch_stream = PlatformFormat(
            platform_id="twitch_stream",
            platform_name="Twitch Streaming",
            platform_type=PlatformType.STREAMING,
            content_category=ContentCategory.LIVE_STREAM,
            supported_video_codecs=["h264"],
            preferred_video_codec="h264",
            supported_resolutions=[
                ResolutionSpec(1920, 1080, "16:9", is_preferred=True, min_bitrate=4500, max_bitrate=6000),
                ResolutionSpec(1280, 720, "16:9", min_bitrate=3000, max_bitrate=4500),
            ],
            preferred_resolution=ResolutionSpec(1920, 1080, "16:9", is_preferred=True),
            supported_framerates=[30, 60],
            preferred_framerate=60,
            supported_audio_codecs=["aac"],
            preferred_audio_codec="aac",
            audio_spec=AudioSpec(
                sample_rate=48000,
                channels=2,
                bitrate_range=(128, 320),
                codec_preference=["aac"]
            ),
            supported_containers=["mp4", "flv"],
            preferred_container="mp4",
            limits=PlatformLimits(
                max_bitrate=8000,  # kbps total
                max_framerate=60
            ),
            quality_presets={
                "1080p60": {
                    "video_bitrate": 6000,
                    "audio_bitrate": 160,
                    "framerate": 60
                },
                "720p60": {
                    "video_bitrate": 4500,
                    "audio_bitrate": 160,
                    "framerate": 60
                }
            },
            encoding_tips=[
                "Use x264 encoder with fast preset",
                "CBR (constant bitrate) recommended for streaming",
                "Test stream quality before going live",
                "Consider keyframe interval of 2 seconds"
            ],
            upload_requirements={
                "keyframe_interval": "2 seconds",
                "rate_control": "CBR",
                "profile": "High"
            }
        )
        self.register_platform_format(twitch_stream)
    
    def _register_spotify_formats(self):
        """Register Spotify format specifications"""
        
        spotify_podcast = PlatformFormat(
            platform_id="spotify_podcast",
            platform_name="Spotify Podcast",
            platform_type=PlatformType.STREAMING,
            content_category=ContentCategory.PODCAST,
            supported_video_codecs=[],
            preferred_video_codec="",
            supported_resolutions=[],
            preferred_resolution=ResolutionSpec(0, 0, ""),
            supported_framerates=[],
            preferred_framerate=0,
            supported_audio_codecs=["mp3", "aac", "ogg"],
            preferred_audio_codec="mp3",
            audio_spec=AudioSpec(
                sample_rate=44100,
                channels=2,
                bitrate_range=(128, 320),
                codec_preference=["mp3", "aac"]
            ),
            supported_containers=["mp3", "m4a", "ogg"],
            preferred_container="mp3",
            limits=PlatformLimits(
                max_file_size=200 * 1024 * 1024,  # 200MB
                max_duration=None  # No duration limit
            ),
            quality_presets={
                "standard": {
                    "audio_bitrate": 128,
                    "sample_rate": 44100,
                    "channels": 2
                },
                "high_quality": {
                    "audio_bitrate": 192,
                    "sample_rate": 44100,
                    "channels": 2
                }
            },
            encoding_tips=[
                "Mono recording acceptable for speech-only content",
                "Use noise reduction and audio enhancement",
                "Consistent audio levels throughout",
                "Include metadata (title, description, artwork)"
            ]
        )
        self.register_platform_format(spotify_podcast)
    
    def _register_streaming_formats(self):
        """Register streaming service format specifications"""
        
        # Generic OTT Streaming
        ott_streaming = PlatformFormat(
            platform_id="ott_streaming",
            platform_name="OTT Streaming (Netflix/Prime/Disney+)",
            platform_type=PlatformType.STREAMING,
            content_category=ContentCategory.LONG_FORM,
            supported_video_codecs=["h264", "h265", "vp9", "av1"],
            preferred_video_codec="h265",
            supported_resolutions=[
                ResolutionSpec(1920, 1080, "16:9", min_bitrate=8000, max_bitrate=12000),
                ResolutionSpec(3840, 2160, "16:9", is_preferred=True, min_bitrate=25000, max_bitrate=50000),
            ],
            preferred_resolution=ResolutionSpec(3840, 2160, "16:9", is_preferred=True),
            supported_framerates=[23.976, 24, 25, 29.97, 30, 50, 59.94, 60],
            preferred_framerate=24,
            supported_audio_codecs=["aac", "ac3", "eac3", "dts"],
            preferred_audio_codec="eac3",
            audio_spec=AudioSpec(
                sample_rate=48000,
                channels=6,  # 5.1 surround
                bitrate_range=(192, 768),
                codec_preference=["eac3", "ac3", "aac"]
            ),
            supported_containers=["mp4", "mkv"],
            preferred_container="mp4",
            limits=PlatformLimits(
                max_file_size=None,  # No practical limit
                max_duration=None,
                max_bitrate=100000  # 100 Mbps
            ),
            quality_presets={
                "4k_hdr": {
                    "video_bitrate": 45000,
                    "audio_bitrate": 768,
                    "framerate": 24,
                    "hdr": True
                },
                "1080p": {
                    "video_bitrate": 10000,
                    "audio_bitrate": 384,
                    "framerate": 24
                }
            },
            supports_hdr=True,
            supports_dolby_vision=True,
            supports_dolby_atmos=True,
            supports_closed_captions=True,
            supports_chapters=True,
            encoding_tips=[
                "Use professional color grading workflow",
                "HDR10 or Dolby Vision for premium content",
                "Multiple audio tracks for different languages",
                "Closed captions and subtitles required",
                "Consider multiple bitrate ladders for ABR"
            ],
            upload_requirements={
                "color_space": "Rec. 2020 (HDR) or Rec. 709 (SDR)",
                "bit_depth": "10-bit preferred",
                "dynamic_range": "HDR10 or Dolby Vision support"
            }
        )
        self.register_platform_format(ott_streaming)
    
    def register_platform_format(self, platform_format: PlatformFormat):
        """Register a platform format specification"""
        platform_id = platform_format.platform_id
        
        # Create platform category if it doesn't exist
        if platform_format.platform_name not in self.platforms:
            self.platforms[platform_format.platform_name] = {}
        
        self.platforms[platform_format.platform_name][platform_id] = platform_format
        
        # Add aliases
        self.platform_aliases[platform_id] = platform_format.platform_name
        
        logger.info(f"Registered platform format: {platform_format.platform_name} - {platform_format.content_category.value}")
    
    def get_platform_format(self, platform_id: str) -> Optional[PlatformFormat]:
        """Get specific platform format by ID"""
        platform_name = self.platform_aliases.get(platform_id)
        if platform_name and platform_name in self.platforms:
            return self.platforms[platform_name].get(platform_id)
        return None
    
    def get_platform_formats(self, platform_name: str) -> List[PlatformFormat]:
        """Get all formats for a platform"""
        return list(self.platforms.get(platform_name, {}).values())
    
    def get_formats_by_type(self, platform_type: PlatformType) -> List[PlatformFormat]:
        """Get all formats by platform type"""
        formats = []
        for platform_formats in self.platforms.values():
            for fmt in platform_formats.values():
                if fmt.platform_type == platform_type:
                    formats.append(fmt)
        return formats
    
    def get_formats_by_category(self, content_category: ContentCategory) -> List[PlatformFormat]:
        """Get all formats by content category"""
        formats = []
        for platform_formats in self.platforms.values():
            for fmt in platform_formats.values():
                if fmt.content_category == content_category:
                    formats.append(fmt)
        return formats
    
    def find_optimal_format(
        self,
        target_platforms: List[str],
        content_type: str = "video",
        priority: str = "quality"  # quality, compatibility, size
    ) -> Optional[Dict[str, Any]]:
        """Find optimal format settings for multiple platforms"""
        
        platform_formats = []
        for platform_id in target_platforms:
            fmt = self.get_platform_format(platform_id)
            if fmt:
                platform_formats.append(fmt)
        
        if not platform_formats:
            return None
        
        # Find common supported codecs
        if content_type == "video":
            common_video_codecs = set(platform_formats[0].supported_video_codecs)
            common_audio_codecs = set(platform_formats[0].supported_audio_codecs)
            common_containers = set(platform_formats[0].supported_containers)
            
            for fmt in platform_formats[1:]:
                common_video_codecs &= set(fmt.supported_video_codecs)
                common_audio_codecs &= set(fmt.supported_audio_codecs)
                common_containers &= set(fmt.supported_containers)
            
            if not common_video_codecs:
                # Fallback to most widely supported
                video_codec = "h264"
            else:
                # Choose based on priority
                if priority == "quality":
                    video_codec = next((c for c in ["av1", "h265", "h264"] if c in common_video_codecs), "h264")
                else:
                    video_codec = "h264" if "h264" in common_video_codecs else list(common_video_codecs)[0]
            
            audio_codec = "aac" if "aac" in common_audio_codecs else list(common_audio_codecs)[0]
            container = "mp4" if "mp4" in common_containers else list(common_containers)[0]
            
            # Find optimal resolution
            min_max_width = min(fmt.preferred_resolution.width for fmt in platform_formats)
            min_max_height = min(fmt.preferred_resolution.height for fmt in platform_formats)
            
            return {
                "video_codec": video_codec,
                "audio_codec": audio_codec,
                "container": container,
                "max_resolution": {
                    "width": min_max_width,
                    "height": min_max_height
                },
                "target_platforms": target_platforms,
                "optimization_notes": [
                    f"Optimized for {len(target_platforms)} platforms",
                    f"Using {video_codec} for best compatibility",
                    f"Resolution capped at {min_max_width}x{min_max_height}"
                ]
            }
        
        return None
    
    def get_platform_comparison(self, platform_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Compare specifications across platforms"""
        comparison = {}
        
        for platform_id in platform_ids:
            fmt = self.get_platform_format(platform_id)
            if not fmt:
                continue
            
            comparison[platform_id] = {
                "platform_name": fmt.platform_name,
                "category": fmt.content_category.value,
                "preferred_resolution": f"{fmt.preferred_resolution.width}x{fmt.preferred_resolution.height}",
                "aspect_ratio": fmt.preferred_resolution.aspect_ratio,
                "preferred_codec": fmt.preferred_video_codec,
                "max_duration": fmt.limits.max_duration,
                "max_file_size": fmt.limits.max_file_size,
                "supports_hdr": fmt.supports_hdr,
                "supports_captions": fmt.supports_closed_captions
            }
        
        return comparison
    
    def export_registry(self, file_path: Path) -> bool:
        """Export platform formats registry to JSON"""
        try:
            registry_data = {
                "platforms": {},
                "aliases": self.platform_aliases,
                "export_timestamp": "2025-09-11T19:18:00Z",
                "total_platforms": len(self.platforms),
                "total_formats": sum(len(formats) for formats in self.platforms.values())
            }
            
            for platform_name, platform_formats in self.platforms.items():
                platform_data = {}
                
                for format_id, fmt in platform_formats.items():
                    format_data = {
                        "platform_id": fmt.platform_id,
                        "platform_name": fmt.platform_name,
                        "platform_type": fmt.platform_type.value,
                        "content_category": fmt.content_category.value,
                        "supported_video_codecs": fmt.supported_video_codecs,
                        "preferred_video_codec": fmt.preferred_video_codec,
                        "supported_audio_codecs": fmt.supported_audio_codecs,
                        "preferred_audio_codec": fmt.preferred_audio_codec,
                        "supported_containers": fmt.supported_containers,
                        "preferred_container": fmt.preferred_container,
                        "preferred_resolution": {
                            "width": fmt.preferred_resolution.width,
                            "height": fmt.preferred_resolution.height,
                            "aspect_ratio": fmt.preferred_resolution.aspect_ratio
                        },
                        "preferred_framerate": fmt.preferred_framerate,
                        "audio_spec": {
                            "sample_rate": fmt.audio_spec.sample_rate,
                            "channels": fmt.audio_spec.channels,
                            "bitrate_range": fmt.audio_spec.bitrate_range
                        },
                        "limits": {
                            "max_file_size": fmt.limits.max_file_size,
                            "max_duration": fmt.limits.max_duration,
                            "min_duration": fmt.limits.min_duration
                        },
                        "quality_presets": fmt.quality_presets,
                        "supports_hdr": fmt.supports_hdr,
                        "supports_closed_captions": fmt.supports_closed_captions,
                        "encoding_tips": fmt.encoding_tips
                    }
                    
                    platform_data[format_id] = format_data
                
                registry_data["platforms"][platform_name] = platform_data
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Platform formats registry exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export platform formats registry: {e}")
            return False


# Global platform formats registry instance
platform_formats_registry = PlatformFormatRegistry()


async def get_platform_formats_registry() -> PlatformFormatRegistry:
    """Get the global platform formats registry instance"""
    return platform_formats_registry


if __name__ == "__main__":
    # Test platform formats registry
    registry = PlatformFormatRegistry()
    
    print("Platform Formats Overview:")
    print(f"Total platforms: {len(registry.platforms)}")
    
    print("\nShort-form video platforms:")
    short_form = registry.get_formats_by_category(ContentCategory.SHORT_FORM)
    for fmt in short_form:
        print(f"- {fmt.platform_name}: {fmt.preferred_resolution.width}x{fmt.preferred_resolution.height}")
    
    print("\nOptimal format for YouTube + TikTok + Instagram:")
    optimal = registry.find_optimal_format(
        target_platforms=["youtube_shorts", "tiktok", "instagram_reels"],
        priority="compatibility"
    )
    if optimal:
        print(f"Video: {optimal['video_codec']}")
        print(f"Audio: {optimal['audio_codec']}")
        print(f"Container: {optimal['container']}")
        print(f"Max Resolution: {optimal['max_resolution']['width']}x{optimal['max_resolution']['height']}")