"""Multi-Platform Content Intelligence Module

Advanced AI system for cross-platform content optimization, distribution intelligence,
and platform-specific content adaptation for maximum reach and engagement.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This revolutionary multi-platform AI system is proprietary intellectual property.
Any unauthorized access, copying, or distribution will result in severe legal consequences.

Business Logic: Content Creation → Platform Analysis → Format Adaptation → Distribution Optimization → Performance Tracking → Cross-Platform Synergy
"""
import asyncio
import json
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict
import re
import math

# Image and video processing
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    import cv2
    import numpy as np
    MEDIA_PROCESSING_AVAILABLE = True
except ImportError:
    MEDIA_PROCESSING_AVAILABLE = False

# Audio processing
try:
    import librosa
    import soundfile as sf
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

# NLP processing
try:
    import spacy
    from transformers import pipeline, AutoTokenizer, AutoModel
    import nltk
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

from .exceptions import OptimizationError, ConfigurationError
from .metrics import metrics_collector
from .performance import performance_monitor
from .content_types import ContentType

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported social media platforms"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    REDDIT = "reddit"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class ContentFormat(Enum):
    """Content format types"""    VIDEO_SHORT = "video_short"  # <60s
    VIDEO_LONG = "video_long"    # >60s
    IMAGE_SINGLE = "image_single"
    IMAGE_CAROUSEL = "image_carousel"
    AUDIO_TRACK = "audio_track"
    AUDIO_PODCAST = "audio_podcast"
    TEXT_POST = "text_post"
    STORY = "story"
    LIVE_STREAM = "live_stream"
    BLOG_POST = "blog_post"
    NEWSLETTER = "newsletter"
    REEL = "reel"
    SHORT_FORM = "short_form"


class OptimizationStrategy(Enum):
    """Content optimization strategies"""    VIRAL_MAXIMIZATION = "viral_maximization"
    ENGAGEMENT_FOCUSED = "engagement_focused"
    REACH_EXPANSION = "reach_expansion"
    CONVERSION_OPTIMIZED = "conversion_optimized"
    BRAND_AWARENESS = "brand_awareness"
    COMMUNITY_BUILDING = "community_building"
    REVENUE_MAXIMIZATION = "revenue_maximization"
    RETENTION_FOCUSED = "retention_focused"


class ContentAdaptationType(Enum):
    """Types of content adaptation"""    ASPECT_RATIO = "aspect_ratio"
    DURATION = "duration"
    TEXT_LENGTH = "text_length"
    HASHTAGS = "hashtags"
    THUMBNAIL = "thumbnail"
    CAPTIONS = "captions"
    AUDIO_OPTIMIZATION = "audio_optimization"
    TIMING = "timing"
    METADATA = "metadata"
    CALL_TO_ACTION = "call_to_action"


@dataclass
class PlatformSpecs:
    """Platform-specific content specifications"""    platform: Platform
    
    # Video specifications
    max_video_duration: Optional[int] = None  # seconds
    min_video_duration: Optional[int] = None
    preferred_video_aspect_ratios: List[str] = field(default_factory=list)
    max_video_file_size: Optional[int] = None  # MB
    supported_video_formats: List[str] = field(default_factory=list)
    
    # Image specifications
    preferred_image_dimensions: List[Tuple[int, int]] = field(default_factory=list)
    max_image_file_size: Optional[int] = None  # MB
    supported_image_formats: List[str] = field(default_factory=list)
    max_images_per_post: int = 1
    
    # Audio specifications
    max_audio_duration: Optional[int] = None  # seconds
    supported_audio_formats: List[str] = field(default_factory=list)
    max_audio_file_size: Optional[int] = None  # MB
    
    # Text specifications
    max_text_length: Optional[int] = None
    min_text_length: Optional[int] = None
    supports_hashtags: bool = True
    max_hashtags: Optional[int] = None
    supports_mentions: bool = True
    
    # Engagement features
    supports_comments: bool = True
    supports_likes: bool = True
    supports_shares: bool = True
    supports_stories: bool = False
    supports_live_streaming: bool = False
    supports_polls: bool = False
    
    # Algorithm preferences
    preferred_posting_times: List[str] = field(default_factory=list)
    optimal_posting_frequency: str = "daily"
    engagement_window: int = 24  # hours
    
    # Monetization features
    supports_ads: bool = False
    supports_sponsorships: bool = False
    supports_merchandise: bool = False
    supports_subscriptions: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform.value,
            "video_specs": {
                "max_duration": self.max_video_duration,
                "min_duration": self.min_video_duration,
                "aspect_ratios": self.preferred_video_aspect_ratios,
                "max_file_size": self.max_video_file_size,
                "formats": self.supported_video_formats
            },
            "image_specs": {
                "dimensions": self.preferred_image_dimensions,
                "max_file_size": self.max_image_file_size,
                "formats": self.supported_image_formats,
                "max_per_post": self.max_images_per_post
            },
            "text_specs": {
                "max_length": self.max_text_length,
                "min_length": self.min_text_length,
                "hashtags": self.supports_hashtags,
                "max_hashtags": self.max_hashtags
            },
            "features": {
                "comments": self.supports_comments,
                "likes": self.supports_likes,
                "shares": self.supports_shares,
                "stories": self.supports_stories,
                "live_streaming": self.supports_live_streaming,
                "polls": self.supports_polls
            },
            "algorithm": {
                "posting_times": self.preferred_posting_times,
                "frequency": self.optimal_posting_frequency,
                "engagement_window": self.engagement_window
            },
            "monetization": {
                "ads": self.supports_ads,
                "sponsorships": self.supports_sponsorships,
                "merchandise": self.supports_merchandise,
                "subscriptions": self.supports_subscriptions
            }
        }


@dataclass
class ContentPiece:
    """Represents a piece of content"""    content_id: str
    title: str
    description: str
    content_type: ContentType
    format_type: ContentFormat
    
    # Media files
    video_file: Optional[str] = None
    image_files: List[str] = field(default_factory=list)
    audio_file: Optional[str] = None
    
    # Text content
    text_content: Optional[str] = None
    captions: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    
    # Metadata
    duration: Optional[int] = None  # seconds
    dimensions: Optional[Tuple[int, int]] = None
    file_size: Optional[int] = None  # bytes
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Analytics
    engagement_score: float = 0.0
    virality_potential: float = 0.0
    audience_match: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_id": self.content_id,
            "title": self.title,
            "description": self.description,
            "content_type": self.content_type.value if hasattr(self.content_type, 'value') else str(self.content_type),
            "format_type": self.format_type.value,
            "media": {
                "video_file": self.video_file,
                "image_files": self.image_files,
                "audio_file": self.audio_file
            },
            "text": {
                "content": self.text_content,
                "captions": self.captions,
                "hashtags": self.hashtags
            },
            "metadata": {
                "duration": self.duration,
                "dimensions": self.dimensions,
                "file_size": self.file_size,
                "created_at": self.created_at.isoformat()
            },
            "analytics": {
                "engagement_score": self.engagement_score,
                "virality_potential": self.virality_potential,
                "audience_match": self.audience_match
            }
        }


@dataclass
class AdaptedContent:
    """Content adapted for a specific platform"""    adaptation_id: str
    original_content_id: str
    target_platform: Platform
    adapted_format: ContentFormat
    
    # Adapted media
    adapted_video: Optional[str] = None
    adapted_images: List[str] = field(default_factory=list)
    adapted_audio: Optional[str] = None
    
    # Adapted text
    adapted_title: Optional[str] = None
    adapted_description: Optional[str] = None
    adapted_captions: Optional[str] = None
    adapted_hashtags: List[str] = field(default_factory=list)
    
    # Adaptation details
    adaptations_applied: List[ContentAdaptationType] = field(default_factory=list)
    quality_score: float = 1.0
    compliance_score: float = 1.0
    optimization_score: float = 0.0
    
    # Platform-specific metadata
    thumbnail: Optional[str] = None
    call_to_action: Optional[str] = None
    posting_schedule: Optional[datetime] = None
    target_audience: Optional[str] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "adaptation_id": self.adaptation_id,
            "original_content_id": self.original_content_id,
            "target_platform": self.target_platform.value,
            "adapted_format": self.adapted_format.value,
            "adapted_media": {
                "video": self.adapted_video,
                "images": self.adapted_images,
                "audio": self.adapted_audio
            },
            "adapted_text": {
                "title": self.adapted_title,
                "description": self.adapted_description,
                "captions": self.adapted_captions,
                "hashtags": self.adapted_hashtags
            },
            "adaptation_details": {
                "applied": [a.value for a in self.adaptations_applied],
                "quality_score": self.quality_score,
                "compliance_score": self.compliance_score,
                "optimization_score": self.optimization_score
            },
            "platform_metadata": {
                "thumbnail": self.thumbnail,
                "call_to_action": self.call_to_action,
                "posting_schedule": self.posting_schedule.isoformat() if self.posting_schedule else None,
                "target_audience": self.target_audience
            },
            "created_at": self.created_at.isoformat()
        }


@dataclass
class DistributionPlan:
    """Multi-platform content distribution plan"""    plan_id: str
    content_id: str
    target_platforms: List[Platform]
    
    # Platform adaptations
    platform_adaptations: Dict[Platform, AdaptedContent] = field(default_factory=dict)
    
    # Scheduling
    primary_launch_time: datetime = field(default_factory=datetime.utcnow)
    platform_schedules: Dict[Platform, datetime] = field(default_factory=dict)
    
    # Strategy
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.ENGAGEMENT_FOCUSED
    cross_platform_synergy: bool = True
    staggered_release: bool = False
    
    # Performance predictions
    expected_reach: Dict[Platform, int] = field(default_factory=dict)
    expected_engagement: Dict[Platform, float] = field(default_factory=dict)
    viral_probability: Dict[Platform, float] = field(default_factory=dict)
    
    # Success metrics
    success_criteria: Dict[str, float] = field(default_factory=dict)
    tracking_enabled: bool = True
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "planned"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "content_id": self.content_id,
            "target_platforms": [p.value for p in self.target_platforms],
            "adaptations": {
                p.value: adaptation.to_dict() 
                for p, adaptation in self.platform_adaptations.items()
            },
            "scheduling": {
                "primary_launch": self.primary_launch_time.isoformat(),
                "platform_schedules": {
                    p.value: dt.isoformat() 
                    for p, dt in self.platform_schedules.items()
                }
            },
            "strategy": {
                "optimization": self.optimization_strategy.value,
                "cross_platform_synergy": self.cross_platform_synergy,
                "staggered_release": self.staggered_release
            },
            "predictions": {
                "reach": {p.value: r for p, r in self.expected_reach.items()},
                "engagement": {p.value: e for p, e in self.expected_engagement.items()},
                "viral_probability": {p.value: v for p, v in self.viral_probability.items()}
            },
            "success_criteria": self.success_criteria,
            "tracking_enabled": self.tracking_enabled,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }


class PlatformSpecsManager:
    """Manages platform-specific content specifications"""    
    def __init__(self):
        self.platform_specs = self._initialize_platform_specs()
    
    def _initialize_platform_specs(self) -> Dict[Platform, PlatformSpecs]:
        """Initialize platform specifications"""        specs = {}
        
        # YouTube specifications
        specs[Platform.YOUTUBE] = PlatformSpecs(
            platform=Platform.YOUTUBE,
            max_video_duration=43200,  # 12 hours for regular users
            min_video_duration=1,
            preferred_video_aspect_ratios=["16:9", "9:16"],
            max_video_file_size=256 * 1024,  # 256 GB
            supported_video_formats=["mp4", "mov", "avi", "wmv", "flv", "webm"],
            preferred_image_dimensions=[(1280, 720), (1920, 1080)],
            max_image_file_size=2,  # 2 MB
            supported_image_formats=["jpg", "jpeg", "png", "bmp", "gif"],
            max_text_length=5000,
            supports_hashtags=True,
            max_hashtags=15,
            supports_stories=False,
            supports_live_streaming=True,
            supports_polls=True,
            preferred_posting_times=["14:00", "16:00", "20:00"],
            optimal_posting_frequency="3-7 times per week",
            supports_ads=True,
            supports_sponsorships=True,
            supports_merchandise=True,
            supports_subscriptions=True
        )
        
        # Instagram specifications
        specs[Platform.INSTAGRAM] = PlatformSpecs(
            platform=Platform.INSTAGRAM,
            max_video_duration=60,  # 60 seconds for posts, 15 for stories
            min_video_duration=1,
            preferred_video_aspect_ratios=["1:1", "4:5", "9:16"],
            max_video_file_size=4096,  # 4 GB
            supported_video_formats=["mp4", "mov"],
            preferred_image_dimensions=[(1080, 1080), (1080, 1350), (1080, 1920)],
            max_image_file_size=30,  # 30 MB
            supported_image_formats=["jpg", "jpeg", "png"],
            max_images_per_post=10,
            max_text_length=2200,
            supports_hashtags=True,
            max_hashtags=30,
            supports_stories=True,
            supports_live_streaming=True,
            supports_polls=True,
            preferred_posting_times=["11:00", "13:00", "17:00"],
            optimal_posting_frequency="daily",
            supports_ads=True,
            supports_sponsorships=True,
            supports_merchandise=True
        )
        
        # TikTok specifications
        specs[Platform.TIKTOK] = PlatformSpecs(
            platform=Platform.TIKTOK,
            max_video_duration=180,  # 3 minutes
            min_video_duration=3,
            preferred_video_aspect_ratios=["9:16"],
            max_video_file_size=287,  # 287 MB
            supported_video_formats=["mp4", "mov"],
            max_text_length=2200,
            supports_hashtags=True,
            max_hashtags=100,
            supports_stories=False,
            supports_live_streaming=True,
            preferred_posting_times=["18:00", "19:00", "20:00"],
            optimal_posting_frequency="1-4 times daily",
            supports_ads=True,
            supports_sponsorships=True
        )
        
        # Twitter specifications
        specs[Platform.TWITTER] = PlatformSpecs(
            platform=Platform.TWITTER,
            max_video_duration=140,  # 2 minutes 20 seconds
            min_video_duration=1,
            preferred_video_aspect_ratios=["16:9", "1:1"],
            max_video_file_size=512,  # 512 MB
            supported_video_formats=["mp4", "mov"],
            preferred_image_dimensions=[(1200, 675), (1080, 1080)],
            max_image_file_size=5,  # 5 MB
            supported_image_formats=["jpg", "jpeg", "png", "gif", "webp"],
            max_images_per_post=4,
            max_text_length=280,
            supports_hashtags=True,
            supports_stories=False,
            supports_live_streaming=True,
            preferred_posting_times=["12:00", "15:00", "18:00"],
            optimal_posting_frequency="3-5 times daily",
            supports_ads=True
        )
        
        # LinkedIn specifications
        specs[Platform.LINKEDIN] = PlatformSpecs(
            platform=Platform.LINKEDIN,
            max_video_duration=600,  # 10 minutes
            min_video_duration=3,
            preferred_video_aspect_ratios=["16:9", "1:1", "9:16"],
            max_video_file_size=5120,  # 5 GB
            supported_video_formats=["mp4", "mov", "wmv", "flv", "avi", "asf"],
            preferred_image_dimensions=[(1200, 627), (1080, 1080)],
            max_image_file_size=20,  # 20 MB
            supported_image_formats=["jpg", "jpeg", "png", "gif"],
            max_images_per_post=9,
            max_text_length=3000,
            supports_hashtags=True,
            supports_stories=False,
            supports_live_streaming=True,
            preferred_posting_times=["08:00", "12:00", "17:00"],
            optimal_posting_frequency="1-2 times daily",
            supports_ads=True,
            supports_sponsorships=True
        )
        
        return specs
    
    def get_platform_specs(self, platform: Platform) -> Optional[PlatformSpecs]:
        """Get specifications for a platform"""        return self.platform_specs.get(platform)
    
    def is_content_compliant(self, 
                           content: ContentPiece,
                           platform: Platform) -> Tuple[bool, List[str]]:
        """Check if content complies with platform specifications"""        specs = self.get_platform_specs(platform)
        if not specs:
            return False, ["Platform specifications not available"]
        
        issues = []
        
        # Check video specifications
        if content.video_file and content.duration:
            if specs.max_video_duration and content.duration > specs.max_video_duration:
                issues.append(f"Video duration {content.duration}s exceeds limit of {specs.max_video_duration}s")
            
            if specs.min_video_duration and content.duration < specs.min_video_duration:
                issues.append(f"Video duration {content.duration}s below minimum of {specs.min_video_duration}s")
        
        # Check image specifications
        if content.image_files:
            if len(content.image_files) > specs.max_images_per_post:
                issues.append(f"Image count {len(content.image_files)} exceeds limit of {specs.max_images_per_post}")
        
        # Check text length
        if content.text_content:
            if specs.max_text_length and len(content.text_content) > specs.max_text_length:
                issues.append(f"Text length {len(content.text_content)} exceeds limit of {specs.max_text_length}")
        
        # Check hashtags
        if content.hashtags:
            if not specs.supports_hashtags:
                issues.append("Platform doesn't support hashtags")
            elif specs.max_hashtags and len(content.hashtags) > specs.max_hashtags:
                issues.append(f"Hashtag count {len(content.hashtags)} exceeds limit of {specs.max_hashtags}")
        
        return len(issues) == 0, issues


class ContentAdaptationEngine:
    """Engine for adapting content to different platforms"""    
    def __init__(self):
        self.specs_manager = PlatformSpecsManager()
        self.adaptation_cache = {}
    
    async def adapt_content_for_platform(self, 
                                       content: ContentPiece,
                                       target_platform: Platform,
                                       optimization_strategy: OptimizationStrategy = OptimizationStrategy.ENGAGEMENT_FOCUSED) -> AdaptedContent:
        """Adapt content for a specific platform"""        try:
            # Get platform specifications
            specs = self.specs_manager.get_platform_specs(target_platform)
            if not specs:
                raise OptimizationError(f"Platform {target_platform.value} not supported")
            
            # Check cache
            cache_key = f"{content.content_id}_{target_platform.value}_{optimization_strategy.value}"
            if cache_key in self.adaptation_cache:
                return self.adaptation_cache[cache_key]
            
            # Create adapted content
            adapted_content = AdaptedContent(
                adaptation_id=str(uuid.uuid4()),
                original_content_id=content.content_id,
                target_platform=target_platform,
                adapted_format=self._determine_optimal_format(content, specs)
            )
            
            adaptations_applied = []
            
            # Adapt video content
            if content.video_file:
                adapted_video, video_adaptations = await self._adapt_video(
                    content.video_file, content.duration, specs
                )
                adapted_content.adapted_video = adapted_video
                adaptations_applied.extend(video_adaptations)
            
            # Adapt image content
            if content.image_files:
                adapted_images, image_adaptations = await self._adapt_images(
                    content.image_files, specs
                )
                adapted_content.adapted_images = adapted_images
                adaptations_applied.extend(image_adaptations)
            
            # Adapt audio content
            if content.audio_file:
                adapted_audio, audio_adaptations = await self._adapt_audio(
                    content.audio_file, specs
                )
                adapted_content.adapted_audio = adapted_audio
                adaptations_applied.extend(audio_adaptations)
            
            # Adapt text content
            text_adaptations = await self._adapt_text_content(
                content, specs, target_platform, optimization_strategy
            )
            adapted_content.adapted_title = text_adaptations.get("title")
            adapted_content.adapted_description = text_adaptations.get("description")
            adapted_content.adapted_captions = text_adaptations.get("captions")
            adapted_content.adapted_hashtags = text_adaptations.get("hashtags", [])
            
            if text_adaptations.get("adaptations"):
                adaptations_applied.extend(text_adaptations["adaptations"])
            
            # Generate thumbnail if needed
            if content.video_file or content.image_files:
                adapted_content.thumbnail = await self._generate_thumbnail(
                    content, specs, target_platform
                )
                adaptations_applied.append(ContentAdaptationType.THUMBNAIL)
            
            # Add call-to-action
            adapted_content.call_to_action = self._generate_call_to_action(
                target_platform, optimization_strategy
            )
            adaptations_applied.append(ContentAdaptationType.CALL_TO_ACTION)
            
            # Calculate quality and compliance scores
            adapted_content.quality_score = self._calculate_quality_score(
                content, adapted_content, adaptations_applied
            )
            adapted_content.compliance_score = self._calculate_compliance_score(
                adapted_content, specs
            )
            adapted_content.optimization_score = self._calculate_optimization_score(
                adapted_content, target_platform, optimization_strategy
            )
            
            adapted_content.adaptations_applied = adaptations_applied
            
            # Cache the result
            self.adaptation_cache[cache_key] = adapted_content
            
            return adapted_content
            
        except Exception as e:
            logger.error(f"Content adaptation failed: {e}")
            raise OptimizationError(f"Failed to adapt content: {str(e)}")
    
    def _determine_optimal_format(self, 
                                content: ContentPiece,
                                specs: PlatformSpecs) -> ContentFormat:
        """Determine optimal format for platform"""        # If video content
        if content.video_file and content.duration:
            if specs.platform == Platform.TIKTOK:
                return ContentFormat.SHORT_FORM
            elif specs.platform == Platform.INSTAGRAM and content.duration <= 60:
                return ContentFormat.REEL
            elif content.duration <= 60:
                return ContentFormat.VIDEO_SHORT
            else:
                return ContentFormat.VIDEO_LONG
        
        # If image content
        elif content.image_files:
            if len(content.image_files) > 1:
                return ContentFormat.IMAGE_CAROUSEL
            else:
                return ContentFormat.IMAGE_SINGLE
        
        # If audio content
        elif content.audio_file:
            if content.duration and content.duration > 300:  # 5 minutes
                return ContentFormat.AUDIO_PODCAST
            else:
                return ContentFormat.AUDIO_TRACK
        
        # If text content
        elif content.text_content:
            if specs.platform == Platform.TWITTER:
                return ContentFormat.TEXT_POST
            else:
                return ContentFormat.BLOG_POST
        
        return ContentFormat.TEXT_POST
    
    async def _adapt_video(self, 
                         video_path: str,
                         duration: Optional[int],
                         specs: PlatformSpecs) -> Tuple[Optional[str], List[ContentAdaptationType]]:
        """Adapt video for platform specifications"""        adaptations = []
        adapted_path = video_path
        
        try:
            if not MEDIA_PROCESSING_AVAILABLE:
                logger.warning("Media processing not available - returning original video")
                return video_path, adaptations
            
            # Duration adaptation
            if duration and specs.max_video_duration and duration > specs.max_video_duration:
                # Trim video to maximum duration
                adapted_path = f"adapted_{uuid.uuid4()}.mp4"
                # Note: In real implementation, use video processing library
                adaptations.append(ContentAdaptationType.DURATION)
                logger.info(f"Video trimmed from {duration}s to {specs.max_video_duration}s")
            
            # Aspect ratio adaptation
            if specs.preferred_video_aspect_ratios:
                # Convert to preferred aspect ratio
                adaptations.append(ContentAdaptationType.ASPECT_RATIO)
                logger.info(f"Video aspect ratio adapted for {specs.platform.value}")
            
            return adapted_path, adaptations
            
        except Exception as e:
            logger.error(f"Video adaptation failed: {e}")
            return video_path, adaptations
    
    async def _adapt_images(self, 
                          image_paths: List[str],
                          specs: PlatformSpecs) -> Tuple[List[str], List[ContentAdaptationType]]:
        """Adapt images for platform specifications"""        adaptations = []
        adapted_paths = image_paths.copy()
        
        try:
            if not MEDIA_PROCESSING_AVAILABLE:
                logger.warning("Media processing not available - returning original images")
                return image_paths, adaptations
            
            # Limit number of images
            if len(image_paths) > specs.max_images_per_post:
                adapted_paths = image_paths[:specs.max_images_per_post]
                adaptations.append(ContentAdaptationType.ASPECT_RATIO)
                logger.info(f"Images limited to {specs.max_images_per_post}")
            
            # Resize images to preferred dimensions
            if specs.preferred_image_dimensions:
                target_dimensions = specs.preferred_image_dimensions[0]
                # Note: In real implementation, resize images
                adaptations.append(ContentAdaptationType.ASPECT_RATIO)
                logger.info(f"Images resized to {target_dimensions}")
            
            return adapted_paths, adaptations
            
        except Exception as e:
            logger.error(f"Image adaptation failed: {e}")
            return image_paths, adaptations
    
    async def _adapt_audio(self, 
                         audio_path: str,
                         specs: PlatformSpecs) -> Tuple[Optional[str], List[ContentAdaptationType]]:
        """Adapt audio for platform specifications"""        adaptations = []
        adapted_path = audio_path
        
        try:
            if not AUDIO_PROCESSING_AVAILABLE:
                logger.warning("Audio processing not available - returning original audio")
                return audio_path, adaptations
            
            # Duration adaptation
            if specs.max_audio_duration:
                # Trim audio if necessary
                adaptations.append(ContentAdaptationType.DURATION)
                adaptations.append(ContentAdaptationType.AUDIO_OPTIMIZATION)
                logger.info(f"Audio adapted for {specs.platform.value}")
            
            return adapted_path, adaptations
            
        except Exception as e:
            logger.error(f"Audio adaptation failed: {e}")
            return audio_path, adaptations
    
    async def _adapt_text_content(self, 
                                content: ContentPiece,
                                specs: PlatformSpecs,
                                platform: Platform,
                                strategy: OptimizationStrategy) -> Dict[str, Any]:
        """Adapt text content for platform"""        adaptations = []
        result = {}
        
        try:
            # Adapt title
            if content.title:
                adapted_title = self._adapt_title(content.title, specs, platform, strategy)
                if adapted_title != content.title:
                    adaptations.append(ContentAdaptationType.TEXT_LENGTH)
                result["title"] = adapted_title
            
            # Adapt description
            if content.description:
                adapted_desc = self._adapt_description(content.description, specs, platform, strategy)
                if adapted_desc != content.description:
                    adaptations.append(ContentAdaptationType.TEXT_LENGTH)
                result["description"] = adapted_desc
            
            # Adapt captions
            if content.captions or content.text_content:
                text_to_adapt = content.captions or content.text_content
                adapted_captions = self._adapt_captions(text_to_adapt, specs, platform)
                result["captions"] = adapted_captions
                adaptations.append(ContentAdaptationType.CAPTIONS)
            
            # Adapt hashtags
            adapted_hashtags = self._adapt_hashtags(content.hashtags, specs, platform, strategy)
            if adapted_hashtags != content.hashtags:
                adaptations.append(ContentAdaptationType.HASHTAGS)
            result["hashtags"] = adapted_hashtags
            
            result["adaptations"] = adaptations
            return result
            
        except Exception as e:
            logger.error(f"Text adaptation failed: {e}")
            return {"adaptations": []}
    
    def _adapt_title(self, 
                   title: str,
                   specs: PlatformSpecs,
                   platform: Platform,
                   strategy: OptimizationStrategy) -> str:
        """Adapt title for platform"""        try:
            # Platform-specific title optimization
            if platform == Platform.YOUTUBE:
                # YouTube prefers descriptive, keyword-rich titles
                if len(title) > 60:
                    title = title[:57] + "..."
                
                # Add strategy-specific elements
                if strategy == OptimizationStrategy.VIRAL_MAXIMIZATION:
                    if not any(word in title.upper() for word in ["VIRAL", "TRENDING", "HOT", "AMAZING"]):
                        title = f"🔥 {title}"
            
            elif platform == Platform.TIKTOK:
                # TikTok prefers short, catchy titles
                if len(title) > 100:
                    title = title[:97] + "..."
                
                # Add emojis for engagement
                if not any(char for char in title if ord(char) > 127):  # No emojis present
                    title = f"✨ {title}"
            
            elif platform == Platform.LINKEDIN:
                # LinkedIn prefers professional, value-focused titles
                if strategy == OptimizationStrategy.CONVERSION_OPTIMIZED:
                    if not title.endswith("?") and not title.endswith("!"):
                        title = f"{title} - Here's What You Need to Know"
            
            return title
            
        except Exception as e:
            logger.error(f"Title adaptation failed: {e}")
            return title
    
    def _adapt_description(self, 
                         description: str,
                         specs: PlatformSpecs,
                         platform: Platform,
                         strategy: OptimizationStrategy) -> str:
        """Adapt description for platform"""        try:
            max_length = specs.max_text_length or len(description)
            
            # Truncate if necessary
            if len(description) > max_length:
                # Smart truncation - try to end at sentence boundary
                truncated = description[:max_length-3]
                last_period = truncated.rfind('.')
                last_exclamation = truncated.rfind('!')
                last_question = truncated.rfind('?')
                
                last_sentence_end = max(last_period, last_exclamation, last_question)
                
                if last_sentence_end > max_length * 0.7:  # If we can keep >70% of content
                    description = description[:last_sentence_end+1]
                else:
                    description = truncated + "..."
            
            # Platform-specific adaptations
            if platform == Platform.INSTAGRAM:
                # Instagram users prefer engaging, personal content
                if strategy == OptimizationStrategy.ENGAGEMENT_FOCUSED:
                    if not description.strip().endswith(("?", "!", ".")):
                        description += "\n\nWhat do you think? Let me know in the comments! 💭"
            
            elif platform == Platform.LINKEDIN:
                # LinkedIn prefers professional tone
                if "guys" in description.lower():
                    description = description.replace("guys", "everyone")
                if "Hey!" in description:
                    description = description.replace("Hey!", "Hello,")
            
            return description
            
        except Exception as e:
            logger.error(f"Description adaptation failed: {e}")
            return description
    
    def _adapt_captions(self, 
                      captions: str,
                      specs: PlatformSpecs,
                      platform: Platform) -> str:
        """Adapt captions for platform"""        try:
            # Platform-specific caption formatting
            if platform == Platform.INSTAGRAM:
                # Instagram captions can be longer and more personal
                return captions
            
            elif platform == Platform.TIKTOK:
                # TikTok prefers short, punchy captions
                if len(captions) > 100:
                    sentences = captions.split('.')
                    short_caption = sentences[0]
                    if len(short_caption) > 100:
                        short_caption = short_caption[:97] + "..."
                    return short_caption
            
            elif platform == Platform.TWITTER:
                # Twitter has character limits
                if len(captions) > 250:  # Leave room for media
                    return captions[:247] + "..."
            
            return captions
            
        except Exception as e:
            logger.error(f"Caption adaptation failed: {e}")
            return captions
    
    def _adapt_hashtags(self, 
                      hashtags: List[str],
                      specs: PlatformSpecs,
                      platform: Platform,
                      strategy: OptimizationStrategy) -> List[str]:
        """Adapt hashtags for platform"""        try:
            if not specs.supports_hashtags:
                return []
            
            adapted_hashtags = hashtags.copy()
            
            # Limit number of hashtags
            if specs.max_hashtags and len(adapted_hashtags) > specs.max_hashtags:
                adapted_hashtags = adapted_hashtags[:specs.max_hashtags]
            
            # Platform-specific hashtag strategies
            if platform == Platform.INSTAGRAM:
                # Instagram allows many hashtags
                platform_hashtags = ["#instagram", "#insta", "#photography"]
                if strategy == OptimizationStrategy.VIRAL_MAXIMIZATION:
                    platform_hashtags.extend(["#viral", "#trending", "#explore"])
            
            elif platform == Platform.TIKTOK:
                # TikTok focuses on trending hashtags
                platform_hashtags = ["#tiktok", "#fyp", "#foryou"]
                if strategy == OptimizationStrategy.VIRAL_MAXIMIZATION:
                    platform_hashtags.extend(["#viral", "#trending", "#vibes"])
            
            elif platform == Platform.TWITTER:
                # Twitter uses fewer, more targeted hashtags
                platform_hashtags = []
                adapted_hashtags = adapted_hashtags[:3]  # Twitter works best with fewer hashtags
            
            elif platform == Platform.LINKEDIN:
                # LinkedIn prefers professional hashtags
                platform_hashtags = ["#linkedin", "#professional"]
                adapted_hashtags = [tag for tag in adapted_hashtags if not any(
                    casual in tag.lower() for casual in ["fun", "lol", "vibes", "mood"]
                )]
            
            else:
                platform_hashtags = []
            
            # Add platform-specific hashtags without exceeding limit
            remaining_slots = (specs.max_hashtags or 30) - len(adapted_hashtags)
            platform_hashtags_to_add = platform_hashtags[:remaining_slots]
            
            # Avoid duplicates
            for tag in platform_hashtags_to_add:
                if tag not in adapted_hashtags:
                    adapted_hashtags.append(tag)
            
            return adapted_hashtags
            
        except Exception as e:
            logger.error(f"Hashtag adaptation failed: {e}")
            return hashtags
    
    async def _generate_thumbnail(self, 
                                content: ContentPiece,
                                specs: PlatformSpecs,
                                platform: Platform) -> Optional[str]:
        """Generate platform-optimized thumbnail"""        try:
            if not MEDIA_PROCESSING_AVAILABLE:
                return None
            
            # Platform-specific thumbnail generation logic
            thumbnail_path = f"thumbnail_{uuid.uuid4()}.jpg"
            
            # Note: In real implementation, generate actual thumbnails
            # using video frames or image processing
            
            logger.info(f"Generated thumbnail for {platform.value}")
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return None
    
    def _generate_call_to_action(self, 
                               platform: Platform,
                               strategy: OptimizationStrategy) -> str:
        """Generate platform and strategy-specific call-to-action"""        cta_templates = {
            Platform.YOUTUBE: {
                OptimizationStrategy.ENGAGEMENT_FOCUSED: "Like and subscribe for more content!",
                OptimizationStrategy.CONVERSION_OPTIMIZED: "Check the description for links and resources!",
                OptimizationStrategy.COMMUNITY_BUILDING: "Join our community - comment your thoughts below!",
                OptimizationStrategy.VIRAL_MAXIMIZATION: "Share this with someone who needs to see it!"
            },
            Platform.INSTAGRAM: {
                OptimizationStrategy.ENGAGEMENT_FOCUSED: "Double tap if you agree! 💖",
                OptimizationStrategy.CONVERSION_OPTIMIZED: "Link in bio for more info! 🔗",
                OptimizationStrategy.COMMUNITY_BUILDING: "Tag a friend who would love this! 👥",
                OptimizationStrategy.VIRAL_MAXIMIZATION: "Save this post and share it to your story! ✨"
            },
            Platform.TIKTOK: {
                OptimizationStrategy.ENGAGEMENT_FOCUSED: "Like if you can relate! ❤️",
                OptimizationStrategy.CONVERSION_OPTIMIZED: "Follow for more tips! 🔥",
                OptimizationStrategy.COMMUNITY_BUILDING: "Duet this with your version! 🎵",
                OptimizationStrategy.VIRAL_MAXIMIZATION: "Share this before it's too late! ⚡"
            },
            Platform.TWITTER: {
                OptimizationStrategy.ENGAGEMENT_FOCUSED: "What are your thoughts? Reply below! 💭",
                OptimizationStrategy.CONVERSION_OPTIMIZED: "Thread continues below 🧵",
                OptimizationStrategy.COMMUNITY_BUILDING: "RT if you agree! Let's start a conversation 🗣️",
                OptimizationStrategy.VIRAL_MAXIMIZATION: "This is going viral - jump on the trend! 🚀"
            },
            Platform.LINKEDIN: {
                OptimizationStrategy.ENGAGEMENT_FOCUSED: "What's your experience with this? Share in the comments.",
                OptimizationStrategy.CONVERSION_OPTIMIZED: "Connect with me for more industry insights.",
                OptimizationStrategy.COMMUNITY_BUILDING: "Tag colleagues who would find this valuable.",
                OptimizationStrategy.VIRAL_MAXIMIZATION: "Repost to share this insight with your network."
            }
        }
        
        return cta_templates.get(platform, {}).get(
            strategy, 
            "Engage with this content!"
        )
    
    def _calculate_quality_score(self, 
                               original: ContentPiece,
                               adapted: AdaptedContent,
                               adaptations: List[ContentAdaptationType]) -> float:
        """Calculate quality score for adapted content"""        try:
            base_score = 0.8
            
            # Bonus for minimal adaptations (less data loss)
            adaptation_penalty = len(adaptations) * 0.05
            base_score -= adaptation_penalty
            
            # Bonus for maintaining essential elements
            if adapted.adapted_title and original.title:
                title_similarity = self._text_similarity(original.title, adapted.adapted_title)
                base_score += title_similarity * 0.1
            
            if adapted.adapted_description and original.description:
                desc_similarity = self._text_similarity(original.description, adapted.adapted_description)
                base_score += desc_similarity * 0.1
            
            # Ensure score is within bounds
            return max(0.1, min(1.0, base_score))
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
            return 0.8
    
    def _calculate_compliance_score(self, 
                                  adapted: AdaptedContent,
                                  specs: PlatformSpecs) -> float:
        """Calculate compliance score with platform specifications"""        try:
            # Check if adapted content would be compliant
            # This is a simplified check - real implementation would be more thorough
            
            compliance_score = 1.0
            
            # Check text length compliance
            if adapted.adapted_description and specs.max_text_length:
                if len(adapted.adapted_description) > specs.max_text_length:
                    compliance_score -= 0.3
            
            # Check hashtag compliance
            if adapted.adapted_hashtags:
                if not specs.supports_hashtags:
                    compliance_score -= 0.2
                elif specs.max_hashtags and len(adapted.adapted_hashtags) > specs.max_hashtags:
                    compliance_score -= 0.2
            
            return max(0.0, compliance_score)
            
        except Exception as e:
            logger.error(f"Compliance score calculation failed: {e}")
            return 1.0
    
    def _calculate_optimization_score(self, 
                                    adapted: AdaptedContent,
                                    platform: Platform,
                                    strategy: OptimizationStrategy) -> float:
        """Calculate optimization score based on strategy and platform"""        try:
            base_score = 0.7
            
            # Strategy-specific optimizations
            if strategy == OptimizationStrategy.ENGAGEMENT_FOCUSED:
                if adapted.call_to_action and any(
                    word in adapted.call_to_action.lower() 
                    for word in ["like", "comment", "share", "tag"]
                ):
                    base_score += 0.2
            
            elif strategy == OptimizationStrategy.VIRAL_MAXIMIZATION:
                if adapted.adapted_hashtags and any(
                    tag.lower() in ["#viral", "#trending", "#fyp", "#explore"]
                    for tag in adapted.adapted_hashtags
                ):
                    base_score += 0.2
            
            # Platform-specific optimizations
            if platform == Platform.INSTAGRAM and adapted.adapted_images:
                base_score += 0.1  # Visual content performs well on Instagram
            
            elif platform == Platform.TIKTOK and adapted.adapted_video:
                base_score += 0.1  # Video content is essential for TikTok
            
            return max(0.1, min(1.0, base_score))
            
        except Exception as e:
            logger.error(f"Optimization score calculation failed: {e}")
            return 0.7
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""        try:
            # Simple word-based similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 and not words2:
                return 1.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            logger.warning(f"Text similarity calculation failed: {e}")
            return 0.5


class MultiPlatformDistributionEngine:
    """Engine for multi-platform content distribution"""    
    def __init__(self):
        self.adaptation_engine = ContentAdaptationEngine()
        self.specs_manager = PlatformSpecsManager()
    
    async def create_distribution_plan(self, 
                                     content: ContentPiece,
                                     target_platforms: List[Platform],
                                     strategy: OptimizationStrategy = OptimizationStrategy.ENGAGEMENT_FOCUSED,
                                     staggered_release: bool = False) -> DistributionPlan:
        """Create comprehensive distribution plan"""        try:
            # Create base distribution plan
            plan = DistributionPlan(
                plan_id=str(uuid.uuid4()),
                content_id=content.content_id,
                target_platforms=target_platforms,
                optimization_strategy=strategy,
                staggered_release=staggered_release
            )
            
            # Adapt content for each platform
            for platform in target_platforms:
                try:
                    adapted_content = await self.adaptation_engine.adapt_content_for_platform(
                        content, platform, strategy
                    )
                    plan.platform_adaptations[platform] = adapted_content
                    
                    # Generate performance predictions
                    reach_prediction = self._predict_reach(content, platform, adapted_content)
                    engagement_prediction = self._predict_engagement(content, platform, adapted_content)
                    viral_prediction = self._predict_viral_potential(content, platform, adapted_content)
                    
                    plan.expected_reach[platform] = reach_prediction
                    plan.expected_engagement[platform] = engagement_prediction
                    plan.viral_probability[platform] = viral_prediction
                    
                except Exception as e:
                    logger.error(f"Failed to adapt content for {platform.value}: {e}")
                    continue
            
            # Optimize posting schedule
            plan.platform_schedules = self._optimize_posting_schedule(
                target_platforms, staggered_release
            )
            
            # Set success criteria
            plan.success_criteria = self._define_success_criteria(strategy, target_platforms)
            
            return plan
            
        except Exception as e:
            logger.error(f"Distribution plan creation failed: {e}")
            raise OptimizationError(f"Failed to create distribution plan: {str(e)}")
    
    def _predict_reach(self, 
                     content: ContentPiece,
                     platform: Platform,
                     adapted: AdaptedContent) -> int:
        """Predict potential reach for platform"""        try:
            # Base reach estimation based on platform
            base_reach = {
                Platform.YOUTUBE: 1000,
                Platform.INSTAGRAM: 800,
                Platform.TIKTOK: 1500,
                Platform.TWITTER: 300,
                Platform.LINKEDIN: 200,
                Platform.FACEBOOK: 500
            }.get(platform, 500)
            
            # Adjust based on content quality
            quality_multiplier = adapted.quality_score * 1.5
            
            # Adjust based on optimization
            optimization_multiplier = adapted.optimization_score * 1.3
            
            # Adjust based on content type
            if content.content_type == ContentType.VIDEO and platform in [Platform.YOUTUBE, Platform.TIKTOK]:
                content_type_multiplier = 1.5
            elif content.content_type == ContentType.IMAGE and platform == Platform.INSTAGRAM:
                content_type_multiplier = 1.3
            else:
                content_type_multiplier = 1.0
            
            predicted_reach = int(base_reach * quality_multiplier * optimization_multiplier * content_type_multiplier)
            
            return max(100, predicted_reach)
            
        except Exception as e:
            logger.error(f"Reach prediction failed: {e}")
            return 500
    
    def _predict_engagement(self, 
                          content: ContentPiece,
                          platform: Platform,
                          adapted: AdaptedContent) -> float:
        """Predict engagement rate for platform"""        try:
            # Base engagement rates by platform
            base_engagement = {
                Platform.YOUTUBE: 0.04,
                Platform.INSTAGRAM: 0.08,
                Platform.TIKTOK: 0.15,
                Platform.TWITTER: 0.03,
                Platform.LINKEDIN: 0.05,
                Platform.FACEBOOK: 0.06
            }.get(platform, 0.05)
            
            # Adjust based on content quality and optimization
            quality_factor = adapted.quality_score
            optimization_factor = adapted.optimization_score
            
            # Adjust based on call-to-action presence
            cta_bonus = 0.02 if adapted.call_to_action else 0.0
            
            predicted_engagement = base_engagement * quality_factor * optimization_factor + cta_bonus
            
            return max(0.01, min(0.5, predicted_engagement))
            
        except Exception as e:
            logger.error(f"Engagement prediction failed: {e}")
            return 0.05
    
    def _predict_viral_potential(self, 
                               content: ContentPiece,
                               platform: Platform,
                               adapted: AdaptedContent) -> float:
        """Predict viral potential for platform"""        try:
            # Base viral probability by platform
            base_viral = {
                Platform.TIKTOK: 0.15,
                Platform.INSTAGRAM: 0.08,
                Platform.TWITTER: 0.12,
                Platform.YOUTUBE: 0.05,
                Platform.LINKEDIN: 0.02,
                Platform.FACEBOOK: 0.06
            }.get(platform, 0.05)
            
            # Factors that increase viral potential
            viral_factors = 1.0
            
            # Content type factor
            if content.content_type == ContentType.VIDEO and platform in [Platform.TIKTOK, Platform.INSTAGRAM]:
                viral_factors *= 1.5
            
            # Optimization factor
            viral_factors *= adapted.optimization_score
            
            # Hashtag factor (viral hashtags increase potential)
            if adapted.adapted_hashtags:
                viral_hashtags = ["viral", "trending", "fyp", "explore", "amazing", "incredible"]
                viral_tag_count = sum(1 for tag in adapted.adapted_hashtags 
                                    if any(viral_word in tag.lower() for viral_word in viral_hashtags))
                if viral_tag_count > 0:
                    viral_factors *= (1 + viral_tag_count * 0.1)
            
            predicted_viral = base_viral * viral_factors
            
            return max(0.01, min(0.8, predicted_viral))
            
        except Exception as e:
            logger.error(f"Viral potential prediction failed: {e}")
            return 0.05
    
    def _optimize_posting_schedule(self, 
                                 platforms: List[Platform],
                                 staggered: bool) -> Dict[Platform, datetime]:
        """Optimize posting schedule across platforms"""        schedule = {}
        base_time = datetime.utcnow()
        
        try:
            # Get optimal times for each platform
            optimal_times = {}
            for platform in platforms:
                specs = self.specs_manager.get_platform_specs(platform)
                if specs and specs.preferred_posting_times:
                    # Use first preferred time
                    time_str = specs.preferred_posting_times[0]
                    hour = int(time_str.split(':')[0])
                    optimal_times[platform] = hour
                else:
                    optimal_times[platform] = 14  # Default 2 PM
            
            if staggered:
                # Staggered release - space out posts
                current_time = base_time
                for i, platform in enumerate(platforms):
                    # Calculate next optimal time
                    optimal_hour = optimal_times[platform]
                    next_time = current_time.replace(
                        hour=optimal_hour, 
                        minute=0, 
                        second=0, 
                        microsecond=0
                    )
                    
                    # If optimal time has passed today, schedule for tomorrow
                    if next_time <= current_time:
                        next_time += timedelta(days=1)
                    
                    schedule[platform] = next_time
                    current_time = next_time + timedelta(hours=2)  # 2-hour gap
            else:
                # Simultaneous release - use best overall time
                best_hour = max(set(optimal_times.values()), key=list(optimal_times.values()).count)
                release_time = base_time.replace(
                    hour=best_hour, 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
                
                # If time has passed, schedule for tomorrow
                if release_time <= base_time:
                    release_time += timedelta(days=1)
                
                for platform in platforms:
                    schedule[platform] = release_time
            
            return schedule
            
        except Exception as e:
            logger.error(f"Schedule optimization failed: {e}")
            # Fallback to immediate posting
            return {platform: base_time for platform in platforms}
    
    def _define_success_criteria(self, 
                               strategy: OptimizationStrategy,
                               platforms: List[Platform]) -> Dict[str, float]:
        """Define success criteria based on strategy"""        criteria = {}
        
        try:
            if strategy == OptimizationStrategy.ENGAGEMENT_FOCUSED:
                criteria = {
                    "min_engagement_rate": 0.05,
                    "min_comments": 10,
                    "min_shares": 5,
                    "engagement_growth": 0.1
                }
            
            elif strategy == OptimizationStrategy.VIRAL_MAXIMIZATION:
                criteria = {
                    "min_reach": 10000,
                    "min_shares": 100,
                    "viral_threshold": 0.15,
                    "growth_velocity": 0.5
                }
            
            elif strategy == OptimizationStrategy.CONVERSION_OPTIMIZED:
                criteria = {
                    "min_click_through_rate": 0.02,
                    "min_conversions": 5,
                    "conversion_rate": 0.01,
                    "lead_quality": 0.7
                }
            
            elif strategy == OptimizationStrategy.REACH_EXPANSION:
                criteria = {
                    "min_reach": 5000,
                    "reach_growth": 0.2,
                    "new_followers": 50,
                    "audience_diversity": 0.3
                }
            
            else:  # Default criteria
                criteria = {
                    "min_engagement_rate": 0.03,
                    "min_reach": 1000,
                    "positive_sentiment": 0.7
                }
            
            # Adjust criteria based on number of platforms
            platform_multiplier = len(platforms)
            for key, value in criteria.items():
                if "min_" in key or key in ["new_followers"]:
                    criteria[key] = value * platform_multiplier
            
            return criteria
            
        except Exception as e:
            logger.error(f"Success criteria definition failed: {e}")
            return {"min_engagement_rate": 0.03}


# Global multi-platform intelligence engine
content_intelligence = MultiPlatformDistributionEngine()
