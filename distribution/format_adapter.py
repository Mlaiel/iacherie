"""Format Adapter

Intelligent content format adaptation system for cross-platform optimization.
Automatically adjusts content format, dimensions, duration, and specifications
to match platform requirements and maximize engagement.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import tempfile
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import mimetypes
import json

# Media processing imports
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import cv2
import numpy as np
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
import ffmpeg

from .platform_connectors import SocialPlatform, ContentFormat

logger = logging.getLogger(__name__)


class AspectRatio(Enum):
    """Supported aspect ratios"""
    SQUARE = "1:1"
    PORTRAIT = "9:16"
    LANDSCAPE = "16:9"
    STORY = "9:16"
    REEL = "9:16"
    FEED = "4:5"
    BANNER = "16:4"


class QualityLevel(Enum):
    """Content quality levels"""
    ULTRA_HIGH = "ultra_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ADAPTIVE = "adaptive"


@dataclass
class PlatformSpecifications:
    """Platform-specific content specifications"""
    platform: SocialPlatform
    content_format: ContentFormat
    
    # Video specifications
    max_video_duration: Optional[int] = None  # seconds
    min_video_duration: Optional[int] = None
    max_video_size: Optional[int] = None  # bytes
    video_resolutions: List[Tuple[int, int]] = field(default_factory=list)
    video_aspect_ratios: List[AspectRatio] = field(default_factory=list)
    video_codecs: List[str] = field(default_factory=list)
    video_bitrates: Dict[str, int] = field(default_factory=dict)
    
    # Audio specifications
    max_audio_duration: Optional[int] = None
    max_audio_size: Optional[int] = None
    audio_formats: List[str] = field(default_factory=list)
    audio_bitrates: List[int] = field(default_factory=list)
    audio_sample_rates: List[int] = field(default_factory=list)
    
    # Image specifications
    max_image_size: Optional[int] = None
    image_resolutions: List[Tuple[int, int]] = field(default_factory=list)
    image_formats: List[str] = field(default_factory=list)
    image_aspect_ratios: List[AspectRatio] = field(default_factory=list)
    
    # Text specifications
    max_text_length: Optional[int] = None
    max_hashtags: Optional[int] = None
    supports_markdown: bool = False
    supports_mentions: bool = True
    supports_links: bool = True


@dataclass
class AdaptationRule:
    """Content adaptation rule"""
    source_format: ContentFormat
    target_format: ContentFormat
    target_platform: SocialPlatform
    transformations: List[str]
    quality_settings: Dict[str, Any] = field(default_factory=dict)
    fallback_options: List[str] = field(default_factory=list)


@dataclass
class ContentVariant:
    """Adapted content variant"""
    platform: SocialPlatform
    format: ContentFormat
    file_path: str
    file_size: int
    duration: Optional[float] = None
    resolution: Optional[Tuple[int, int]] = None
    aspect_ratio: Optional[AspectRatio] = None
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FormatAdapter:
    """Intelligent content format adaptation system"""
    
    # Platform specifications database
    PLATFORM_SPECS = {
        SocialPlatform.YOUTUBE: {
            ContentFormat.VIDEO: PlatformSpecifications(
                platform=SocialPlatform.YOUTUBE,
                content_format=ContentFormat.VIDEO,
                max_video_duration=43200,  # 12 hours
                min_video_duration=1,
                max_video_size=128 * 1024 * 1024 * 1024,  # 128GB
                video_resolutions=[(3840, 2160), (1920, 1080), (1280, 720), (854, 480)],
                video_aspect_ratios=[AspectRatio.LANDSCAPE, AspectRatio.SQUARE, AspectRatio.PORTRAIT],
                video_codecs=["h264", "h265", "vp9"],
                video_bitrates={"4k": 45000, "1080p": 8000, "720p": 5000, "480p": 2500}
            ),
            ContentFormat.SHORT: PlatformSpecifications(
                platform=SocialPlatform.YOUTUBE,
                content_format=ContentFormat.SHORT,
                max_video_duration=60,
                min_video_duration=1,
                video_resolutions=[(1080, 1920), (720, 1280)],
                video_aspect_ratios=[AspectRatio.PORTRAIT],
                video_codecs=["h264"]
            )
        },
        SocialPlatform.TIKTOK: {
            ContentFormat.VIDEO: PlatformSpecifications(
                platform=SocialPlatform.TIKTOK,
                content_format=ContentFormat.VIDEO,
                max_video_duration=600,  # 10 minutes
                min_video_duration=1,
                max_video_size=4 * 1024 * 1024 * 1024,  # 4GB
                video_resolutions=[(1080, 1920), (720, 1280)],
                video_aspect_ratios=[AspectRatio.PORTRAIT],
                video_codecs=["h264"]
            )
        },
        SocialPlatform.INSTAGRAM: {
            ContentFormat.VIDEO: PlatformSpecifications(
                platform=SocialPlatform.INSTAGRAM,
                content_format=ContentFormat.VIDEO,
                max_video_duration=60,
                min_video_duration=1,
                video_resolutions=[(1080, 1350), (1080, 1080)],
                video_aspect_ratios=[AspectRatio.SQUARE, AspectRatio.FEED],
                video_codecs=["h264"]
            ),
            ContentFormat.REEL: PlatformSpecifications(
                platform=SocialPlatform.INSTAGRAM,
                content_format=ContentFormat.REEL,
                max_video_duration=90,
                min_video_duration=1,
                video_resolutions=[(1080, 1920)],
                video_aspect_ratios=[AspectRatio.PORTRAIT],
                video_codecs=["h264"]
            ),
            ContentFormat.STORY: PlatformSpecifications(
                platform=SocialPlatform.INSTAGRAM,
                content_format=ContentFormat.STORY,
                max_video_duration=15,
                min_video_duration=1,
                video_resolutions=[(1080, 1920)],
                video_aspect_ratios=[AspectRatio.STORY],
                video_codecs=["h264"]
            ),
            ContentFormat.IMAGE: PlatformSpecifications(
                platform=SocialPlatform.INSTAGRAM,
                content_format=ContentFormat.IMAGE,
                image_resolutions=[(1080, 1080), (1080, 1350)],
                image_aspect_ratios=[AspectRatio.SQUARE, AspectRatio.FEED],
                image_formats=["jpeg", "jpg", "png"]
            )
        },
        SocialPlatform.TWITTER: {
            ContentFormat.VIDEO: PlatformSpecifications(
                platform=SocialPlatform.TWITTER,
                content_format=ContentFormat.VIDEO,
                max_video_duration=140,
                min_video_duration=1,
                max_video_size=512 * 1024 * 1024,  # 512MB
                video_resolutions=[(1920, 1080), (1280, 720)],
                video_aspect_ratios=[AspectRatio.LANDSCAPE, AspectRatio.SQUARE],
                video_codecs=["h264"]
            ),
            ContentFormat.IMAGE: PlatformSpecifications(
                platform=SocialPlatform.TWITTER,
                content_format=ContentFormat.IMAGE,
                max_image_size=5 * 1024 * 1024,  # 5MB
                image_resolutions=[(1200, 675), (1200, 1200)],
                image_formats=["jpeg", "jpg", "png", "gif", "webp"]
            ),
            ContentFormat.TEXT: PlatformSpecifications(
                platform=SocialPlatform.TWITTER,
                content_format=ContentFormat.TEXT,
                max_text_length=280,
                max_hashtags=10,
                supports_mentions=True,
                supports_links=True
            )
        },
        SocialPlatform.FACEBOOK: {
            ContentFormat.VIDEO: PlatformSpecifications(
                platform=SocialPlatform.FACEBOOK,
                content_format=ContentFormat.VIDEO,
                max_video_duration=7200,  # 2 hours
                min_video_duration=1,
                max_video_size=10 * 1024 * 1024 * 1024,  # 10GB
                video_resolutions=[(1920, 1080), (1280, 720)],
                video_aspect_ratios=[AspectRatio.LANDSCAPE, AspectRatio.SQUARE, AspectRatio.PORTRAIT],
                video_codecs=["h264"]
            ),
            ContentFormat.IMAGE: PlatformSpecifications(
                platform=SocialPlatform.FACEBOOK,
                content_format=ContentFormat.IMAGE,
                max_image_size=4 * 1024 * 1024,  # 4MB
                image_resolutions=[(1200, 630), (1200, 1200)],
                image_formats=["jpeg", "jpg", "png"]
            )
        },
        SocialPlatform.LINKEDIN: {
            ContentFormat.VIDEO: PlatformSpecifications(
                platform=SocialPlatform.LINKEDIN,
                content_format=ContentFormat.VIDEO,
                max_video_duration=600,  # 10 minutes
                min_video_duration=3,
                max_video_size=5 * 1024 * 1024 * 1024,  # 5GB
                video_resolutions=[(1920, 1080), (1280, 720)],
                video_aspect_ratios=[AspectRatio.LANDSCAPE, AspectRatio.SQUARE],
                video_codecs=["h264"]
            ),
            ContentFormat.IMAGE: PlatformSpecifications(
                platform=SocialPlatform.LINKEDIN,
                content_format=ContentFormat.IMAGE,
                max_image_size=100 * 1024 * 1024,  # 100MB
                image_resolutions=[(1200, 627), (1080, 1080)],
                image_formats=["jpeg", "jpg", "png"]
            )
        },
        SocialPlatform.SPOTIFY: {
            ContentFormat.AUDIO: PlatformSpecifications(
                platform=SocialPlatform.SPOTIFY,
                content_format=ContentFormat.AUDIO,
                max_audio_duration=10800,  # 3 hours
                audio_formats=["wav", "flac", "mp3"],
                audio_bitrates=[320, 256, 192, 128],
                audio_sample_rates=[44100, 48000, 96000]
            )
        },
        SocialPlatform.SOUNDCLOUD: {
            ContentFormat.AUDIO: PlatformSpecifications(
                platform=SocialPlatform.SOUNDCLOUD,
                content_format=ContentFormat.AUDIO,
                max_audio_duration=21600,  # 6 hours
                max_audio_size=4 * 1024 * 1024 * 1024,  # 4GB
                audio_formats=["wav", "flac", "mp3", "aac"],
                audio_bitrates=[320, 256, 192, 128],
                audio_sample_rates=[44100, 48000]
            )
        }
    }
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.adaptation_cache: Dict[str, ContentVariant] = {}
        self.quality_presets = self._initialize_quality_presets()
    
    def _initialize_quality_presets(self) -> Dict[QualityLevel, Dict[str, Any]]:
        """Initialize quality presets for different content types"""
        return {
            QualityLevel.ULTRA_HIGH: {
                "video_bitrate_multiplier": 2.0,
                "audio_bitrate": 320,
                "image_quality": 100,
                "compression_level": 0
            },
            QualityLevel.HIGH: {
                "video_bitrate_multiplier": 1.5,
                "audio_bitrate": 256,
                "image_quality": 95,
                "compression_level": 1
            },
            QualityLevel.MEDIUM: {
                "video_bitrate_multiplier": 1.0,
                "audio_bitrate": 192,
                "image_quality": 85,
                "compression_level": 3
            },
            QualityLevel.LOW: {
                "video_bitrate_multiplier": 0.7,
                "audio_bitrate": 128,
                "image_quality": 75,
                "compression_level": 5
            }
        }
    
    async def adapt_content(
        self,
        source_file: str,
        target_platforms: List[SocialPlatform],
        target_formats: Optional[Dict[SocialPlatform, List[ContentFormat]]] = None,
        quality_level: QualityLevel = QualityLevel.HIGH,
        optimization_settings: Optional[Dict] = None
    ) -> Dict[SocialPlatform, List[ContentVariant]]:
        """Adapt content for multiple platforms and formats"""
        try:
            results = {}
            
            # Analyze source content
            source_analysis = await self._analyze_source_content(source_file)
            source_format = self._detect_content_format(source_file, source_analysis)
            
            logger.info(f"Adapting {source_format.value} content for {len(target_platforms)} platforms")
            
            for platform in target_platforms:
                platform_variants = []
                
                # Determine target formats for platform
                if target_formats and platform in target_formats:
                    formats = target_formats[platform]
                else:
                    formats = self._get_optimal_formats(platform, source_format)
                
                for target_format in formats:
                    try:
                        variant = await self._create_platform_variant(
                            source_file=source_file,
                            source_format=source_format,
                            source_analysis=source_analysis,
                            target_platform=platform,
                            target_format=target_format,
                            quality_level=quality_level,
                            optimization_settings=optimization_settings or {}
                        )
                        
                        if variant:
                            platform_variants.append(variant)
                    
                    except Exception as e:
                        logger.error(f"Failed to create variant for {platform.value}/{target_format.value}: {str(e)}")
                
                results[platform] = platform_variants
            
            return results
        
        except Exception as e:
            logger.error(f"Content adaptation failed: {str(e)}")
            raise
    
    async def _analyze_source_content(self, source_file: str) -> Dict[str, Any]:
        """Analyze source content properties"""
        try:
            file_path = Path(source_file)
            file_size = file_path.stat().st_size
            mime_type, _ = mimetypes.guess_type(source_file)
            
            analysis = {
                "file_size": file_size,
                "mime_type": mime_type,
                "file_extension": file_path.suffix.lower()
            }
            
            if mime_type and mime_type.startswith("video/"):
                analysis.update(await self._analyze_video(source_file))
            elif mime_type and mime_type.startswith("audio/"):
                analysis.update(await self._analyze_audio(source_file))
            elif mime_type and mime_type.startswith("image/"):
                analysis.update(await self._analyze_image(source_file))
            
            return analysis
        
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            return {"file_size": 0, "mime_type": None}
    
    async def _analyze_video(self, video_file: str) -> Dict[str, Any]:
        """Analyze video content properties"""
        try:
            with VideoFileClip(video_file) as clip:
                return {
                    "duration": clip.duration,
                    "fps": clip.fps,
                    "resolution": (clip.w, clip.h),
                    "aspect_ratio": clip.w / clip.h,
                    "has_audio": clip.audio is not None
                }
        except Exception as e:
            logger.error(f"Video analysis failed: {str(e)}")
            return {}
    
    async def _analyze_audio(self, audio_file: str) -> Dict[str, Any]:
        """Analyze audio content properties"""
        try:
            audio_data, sample_rate = librosa.load(audio_file, sr=None)
            duration = len(audio_data) / sample_rate
            
            return {
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": 1 if audio_data.ndim == 1 else audio_data.shape[0],
                "bitrate": self._estimate_audio_bitrate(audio_file, duration)
            }
        except Exception as e:
            logger.error(f"Audio analysis failed: {str(e)}")
            return {}
    
    async def _analyze_image(self, image_file: str) -> Dict[str, Any]:
        """Analyze image content properties"""
        try:
            with Image.open(image_file) as img:
                return {
                    "resolution": img.size,
                    "aspect_ratio": img.size[0] / img.size[1],
                    "mode": img.mode,
                    "format": img.format
                }
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            return {}
    
    def _detect_content_format(self, file_path: str, analysis: Dict[str, Any]) -> ContentFormat:
        """Detect content format from file and analysis"""
        mime_type = analysis.get("mime_type", "")
        
        if mime_type.startswith("video/"):
            duration = analysis.get("duration", 0)
            if duration <= 60:
                return ContentFormat.SHORT
            else:
                return ContentFormat.VIDEO
        elif mime_type.startswith("audio/"):
            return ContentFormat.AUDIO
        elif mime_type.startswith("image/"):
            return ContentFormat.IMAGE
        else:
            return ContentFormat.TEXT
    
    def _get_optimal_formats(
        self,
        platform: SocialPlatform,
        source_format: ContentFormat
    ) -> List[ContentFormat]:
        """Get optimal target formats for platform"""
        platform_specs = self.PLATFORM_SPECS.get(platform, {})
        available_formats = list(platform_specs.keys())
        
        if not available_formats:
            return [source_format]
        
        # Platform-specific optimal format selection
        if platform == SocialPlatform.TIKTOK:
            return [ContentFormat.VIDEO]
        elif platform == SocialPlatform.INSTAGRAM:
            if source_format == ContentFormat.VIDEO:
                return [ContentFormat.REEL, ContentFormat.VIDEO, ContentFormat.STORY]
            elif source_format == ContentFormat.IMAGE:
                return [ContentFormat.IMAGE, ContentFormat.STORY]
        elif platform == SocialPlatform.YOUTUBE:
            if source_format in [ContentFormat.VIDEO, ContentFormat.SHORT]:
                return [ContentFormat.VIDEO, ContentFormat.SHORT]
        elif platform == SocialPlatform.SPOTIFY:
            return [ContentFormat.AUDIO]
        
        # Default: try to match source format
        if source_format in available_formats:
            return [source_format]
        else:
            return available_formats[:1]  # First available format
    
    async def _create_platform_variant(
        self,
        source_file: str,
        source_format: ContentFormat,
        source_analysis: Dict[str, Any],
        target_platform: SocialPlatform,
        target_format: ContentFormat,
        quality_level: QualityLevel,
        optimization_settings: Dict
    ) -> Optional[ContentVariant]:
        """Create platform-specific content variant"""
        try:
            # Get platform specifications
            platform_specs = self.PLATFORM_SPECS.get(target_platform, {})
            format_specs = platform_specs.get(target_format)
            
            if not format_specs:
                logger.warning(f"No specifications for {target_platform.value}/{target_format.value}")
                return None
            
            # Generate cache key
            cache_key = self._generate_cache_key(
                source_file, target_platform, target_format, quality_level
            )
            
            # Check cache
            if cache_key in self.adaptation_cache:
                return self.adaptation_cache[cache_key]
            
            # Create adaptation based on format
            if target_format in [ContentFormat.VIDEO, ContentFormat.SHORT, ContentFormat.REEL]:
                variant = await self._adapt_video_content(
                    source_file, source_analysis, format_specs, quality_level, optimization_settings
                )
            elif target_format == ContentFormat.AUDIO:
                variant = await self._adapt_audio_content(
                    source_file, source_analysis, format_specs, quality_level, optimization_settings
                )
            elif target_format == ContentFormat.IMAGE:
                variant = await self._adapt_image_content(
                    source_file, source_analysis, format_specs, quality_level, optimization_settings
                )
            else:
                logger.warning(f"Unsupported target format: {target_format.value}")
                return None
            
            # Cache the result
            if variant:
                self.adaptation_cache[cache_key] = variant
            
            return variant
        
        except Exception as e:
            logger.error(f"Platform variant creation failed: {str(e)}")
            return None
    
    async def _adapt_video_content(
        self,
        source_file: str,
        source_analysis: Dict[str, Any],
        format_specs: PlatformSpecifications,
        quality_level: QualityLevel,
        optimization_settings: Dict
    ) -> Optional[ContentVariant]:
        """Adapt video content to platform specifications"""
        try:
            # Generate output filename
            output_file = self.temp_dir / f"adapted_video_{hash(source_file)}_{format_specs.platform.value}_{format_specs.content_format.value}.mp4"
            
            # Get quality settings
            quality_preset = self.quality_presets[quality_level]
            
            # Determine target resolution
            target_resolution = self._select_optimal_resolution(
                source_analysis.get("resolution", (1920, 1080)),
                format_specs.video_resolutions
            )
            
            # Determine target aspect ratio
            target_aspect_ratio = self._select_optimal_aspect_ratio(
                source_analysis.get("aspect_ratio", 16/9),
                format_specs.video_aspect_ratios
            )
            
            # Calculate video bitrate
            base_bitrate = format_specs.video_bitrates.get("1080p", 5000)
            target_bitrate = int(base_bitrate * quality_preset["video_bitrate_multiplier"])
            
            # Load video clip
            with VideoFileClip(source_file) as clip:
                # Trim to maximum duration if needed
                if format_specs.max_video_duration and clip.duration > format_specs.max_video_duration:
                    clip = clip.subclip(0, format_specs.max_video_duration)
                
                # Resize video
                if target_resolution != (clip.w, clip.h):
                    clip = clip.resize(target_resolution)
                
                # Adjust aspect ratio if needed
                if target_aspect_ratio:
                    clip = self._adjust_video_aspect_ratio(clip, target_aspect_ratio)
                
                # Apply optimization settings
                if optimization_settings.get("enhance_quality"):
                    clip = self._enhance_video_quality(clip)
                
                if optimization_settings.get("add_watermark"):
                    clip = self._add_watermark(clip, optimization_settings["watermark_text"])
                
                # Write video with specified bitrate
                clip.write_videofile(
                    str(output_file),
                    bitrate=f"{target_bitrate}k",
                    codec="libx264",
                    audio_codec="aac" if clip.audio else None,
                    verbose=False,
                    logger=None
                )
            
            # Verify output file
            if not output_file.exists():
                logger.error("Video adaptation failed - output file not created")
                return None
            
            # Create variant
            variant = ContentVariant(
                platform=format_specs.platform,
                format=format_specs.content_format,
                file_path=str(output_file),
                file_size=output_file.stat().st_size,
                duration=source_analysis.get("duration"),
                resolution=target_resolution,
                aspect_ratio=target_aspect_ratio,
                quality_metrics={"bitrate": target_bitrate, "quality_level": quality_level.value},
                metadata={"codec": "h264", "container": "mp4"}
            )
            
            return variant
        
        except Exception as e:
            logger.error(f"Video adaptation failed: {str(e)}")
            return None
    
    async def _adapt_audio_content(
        self,
        source_file: str,
        source_analysis: Dict[str, Any],
        format_specs: PlatformSpecifications,
        quality_level: QualityLevel,
        optimization_settings: Dict
    ) -> Optional[ContentVariant]:
        """Adapt audio content to platform specifications"""
        try:
            # Generate output filename
            output_file = self.temp_dir / f"adapted_audio_{hash(source_file)}_{format_specs.platform.value}.mp3"
            
            # Get quality settings
            quality_preset = self.quality_presets[quality_level]
            target_bitrate = quality_preset["audio_bitrate"]
            
            # Select optimal sample rate
            target_sample_rate = self._select_optimal_sample_rate(
                source_analysis.get("sample_rate", 44100),
                format_specs.audio_sample_rates
            )
            
            # Load and process audio
            audio_data, current_sr = librosa.load(source_file, sr=None)
            
            # Resample if needed
            if current_sr != target_sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=current_sr, target_sr=target_sample_rate)
            
            # Trim to maximum duration if needed
            if format_specs.max_audio_duration:
                max_samples = int(format_specs.max_audio_duration * target_sample_rate)
                if len(audio_data) > max_samples:
                    audio_data = audio_data[:max_samples]
            
            # Apply audio enhancement if requested
            if optimization_settings.get("enhance_audio"):
                audio_data = self._enhance_audio_quality(audio_data, target_sample_rate)
            
            # Save audio
            sf.write(str(output_file), audio_data, target_sample_rate)
            
            # Verify output file
            if not output_file.exists():
                logger.error("Audio adaptation failed - output file not created")
                return None
            
            # Calculate duration
            duration = len(audio_data) / target_sample_rate
            
            # Create variant
            variant = ContentVariant(
                platform=format_specs.platform,
                format=format_specs.content_format,
                file_path=str(output_file),
                file_size=output_file.stat().st_size,
                duration=duration,
                quality_metrics={"bitrate": target_bitrate, "sample_rate": target_sample_rate},
                metadata={"format": "mp3", "sample_rate": target_sample_rate}
            )
            
            return variant
        
        except Exception as e:
            logger.error(f"Audio adaptation failed: {str(e)}")
            return None
    
    async def _adapt_image_content(
        self,
        source_file: str,
        source_analysis: Dict[str, Any],
        format_specs: PlatformSpecifications,
        quality_level: QualityLevel,
        optimization_settings: Dict
    ) -> Optional[ContentVariant]:
        """Adapt image content to platform specifications"""
        try:
            # Generate output filename
            output_file = self.temp_dir / f"adapted_image_{hash(source_file)}_{format_specs.platform.value}.jpg"
            
            # Get quality settings
            quality_preset = self.quality_presets[quality_level]
            quality = quality_preset["image_quality"]
            
            # Load image
            with Image.open(source_file) as img:
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Select optimal resolution
                target_resolution = self._select_optimal_resolution(
                    img.size,
                    format_specs.image_resolutions
                )
                
                # Resize image if needed
                if target_resolution != img.size:
                    img = img.resize(target_resolution, Image.Resampling.LANCZOS)
                
                # Adjust aspect ratio if needed
                if format_specs.image_aspect_ratios:
                    target_aspect_ratio = format_specs.image_aspect_ratios[0]
                    img = self._adjust_image_aspect_ratio(img, target_aspect_ratio)
                
                # Apply image enhancements if requested
                if optimization_settings.get("enhance_image"):
                    img = self._enhance_image_quality(img)
                
                # Apply watermark if requested
                if optimization_settings.get("add_watermark"):
                    img = self._add_image_watermark(img, optimization_settings["watermark_text"])
                
                # Save image
                img.save(str(output_file), quality=quality, optimize=True)
            
            # Verify output file
            if not output_file.exists():
                logger.error("Image adaptation failed - output file not created")
                return None
            
            # Create variant
            variant = ContentVariant(
                platform=format_specs.platform,
                format=format_specs.content_format,
                file_path=str(output_file),
                file_size=output_file.stat().st_size,
                resolution=target_resolution,
                quality_metrics={"quality": quality, "optimization_level": quality_preset["compression_level"]},
                metadata={"format": "jpeg", "quality": quality}
            )
            
            return variant
        
        except Exception as e:
            logger.error(f"Image adaptation failed: {str(e)}")
            return None
    
    def _select_optimal_resolution(
        self,
        source_resolution: Tuple[int, int],
        target_resolutions: List[Tuple[int, int]]
    ) -> Tuple[int, int]:
        """Select optimal target resolution"""
        if not target_resolutions:
            return source_resolution
        
        source_pixels = source_resolution[0] * source_resolution[1]
        
        # Find closest resolution without exceeding source quality
        best_resolution = target_resolutions[0]
        best_score = float('inf')
        
        for resolution in target_resolutions:
            target_pixels = resolution[0] * resolution[1]
            
            # Prefer resolutions that don't exceed source
            if target_pixels <= source_pixels:
                score = abs(source_pixels - target_pixels)
            else:
                score = abs(source_pixels - target_pixels) * 2  # Penalty for upscaling
            
            if score < best_score:
                best_score = score
                best_resolution = resolution
        
        return best_resolution
    
    def _select_optimal_aspect_ratio(
        self,
        source_aspect_ratio: float,
        target_aspect_ratios: List[AspectRatio]
    ) -> Optional[AspectRatio]:
        """Select optimal target aspect ratio"""
        if not target_aspect_ratios:
            return None
        
        # Convert aspect ratios to numeric values
        aspect_ratio_values = {
            AspectRatio.SQUARE: 1.0,
            AspectRatio.PORTRAIT: 9/16,
            AspectRatio.LANDSCAPE: 16/9,
            AspectRatio.STORY: 9/16,
            AspectRatio.REEL: 9/16,
            AspectRatio.FEED: 4/5,
            AspectRatio.BANNER: 16/4
        }
        
        # Find closest aspect ratio
        best_ratio = target_aspect_ratios[0]
        best_difference = abs(source_aspect_ratio - aspect_ratio_values[best_ratio])
        
        for ratio in target_aspect_ratios:
            difference = abs(source_aspect_ratio - aspect_ratio_values[ratio])
            if difference < best_difference:
                best_difference = difference
                best_ratio = ratio
        
        return best_ratio
    
    def _select_optimal_sample_rate(
        self,
        source_sample_rate: int,
        target_sample_rates: List[int]
    ) -> int:
        """Select optimal target sample rate"""
        if not target_sample_rates:
            return source_sample_rate
        
        # Find closest sample rate
        return min(target_sample_rates, key=lambda x: abs(source_sample_rate - x))
    
    def _adjust_video_aspect_ratio(self, clip, target_aspect_ratio: AspectRatio):
        """Adjust video to target aspect ratio"""
        # Implementation would use moviepy to crop/pad video
        return clip
    
    def _enhance_video_quality(self, clip):
        """Enhance video quality"""
        # Implementation would apply video filters
        return clip
    
    def _add_watermark(self, clip, watermark_text: str):
        """Add watermark to video"""
        # Implementation would add text overlay
        return clip
    
    def _adjust_image_aspect_ratio(self, img: Image.Image, target_aspect_ratio: AspectRatio) -> Image.Image:
        """Adjust image to target aspect ratio"""
        # Implementation would crop/pad image
        return img
    
    def _enhance_image_quality(self, img: Image.Image) -> Image.Image:
        """Enhance image quality"""
        # Apply sharpening and contrast enhancement
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        return img
    
    def _add_image_watermark(self, img: Image.Image, watermark_text: str) -> Image.Image:
        """Add watermark to image"""
        # Implementation would add text watermark
        return img
    
    def _enhance_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Enhance audio quality"""
        # Implementation would apply audio processing
        return audio_data
    
    def _estimate_audio_bitrate(self, audio_file: str, duration: float) -> int:
        """Estimate audio bitrate"""
        try:
            file_size = Path(audio_file).stat().st_size
            # Rough bitrate estimation: (file_size * 8) / duration / 1000
            return int((file_size * 8) / duration / 1000)
        except:
            return 128  # Default bitrate
    
    def _generate_cache_key(
        self,
        source_file: str,
        platform: SocialPlatform,
        format: ContentFormat,
        quality: QualityLevel
    ) -> str:
        """Generate cache key for adaptation"""
        content = f"{source_file}_{platform.value}_{format.value}_{quality.value}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def get_adaptation_statistics(self) -> Dict[str, Any]:
        """Get adaptation performance statistics"""
        try:
            total_adaptations = len(self.adaptation_cache)
            
            # Platform distribution
            platform_stats = {}
            format_stats = {}
            
            for variant in self.adaptation_cache.values():
                platform = variant.platform.value
                format = variant.format.value
                
                platform_stats[platform] = platform_stats.get(platform, 0) + 1
                format_stats[format] = format_stats.get(format, 0) + 1
            
            # File size statistics
            file_sizes = [v.file_size for v in self.adaptation_cache.values()]
            avg_file_size = sum(file_sizes) / len(file_sizes) if file_sizes else 0
            
            return {
                "total_adaptations": total_adaptations,
                "platform_distribution": platform_stats,
                "format_distribution": format_stats,
                "average_file_size": avg_file_size,
                "cache_size_mb": sum(file_sizes) / (1024 * 1024)
            }
        
        except Exception as e:
            logger.error(f"Statistics generation failed: {str(e)}")
            return {}
    
    def clear_cache(self):
        """Clear adaptation cache and temporary files"""
        try:
            # Remove temporary files
            for cache_file in self.temp_dir.glob("*"):
                cache_file.unlink()
            
            # Clear cache
            self.adaptation_cache.clear()
            
            logger.info("Adaptation cache cleared")
        
        except Exception as e:
            logger.error(f"Cache clearing failed: {str(e)}")
    
    def __del__(self):
        """Cleanup temporary files"""
        try:
            self.clear_cache()
        except:
            pass