"""Format Adapter - Adaptation formats
====================================

Content format adaptation system for optimizing content across different platforms
with intelligent format conversion, size optimization, and quality preservation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Content types for adaptation."""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    CAROUSEL = "carousel"
    STORY = "story"


class PlatformFormat(str, Enum):
    """Platform format specifications."""
    YOUTUBE_VIDEO = "youtube_video"
    YOUTUBE_SHORT = "youtube_short"
    INSTAGRAM_FEED = "instagram_feed"
    INSTAGRAM_STORY = "instagram_story"
    INSTAGRAM_REEL = "instagram_reel"
    TIKTOK_VIDEO = "tiktok_video"
    SPOTIFY_TRACK = "spotify_track"
    SOUNDCLOUD_TRACK = "soundcloud_track"


@dataclass
class FormatSpecification:
    """Platform format specification."""
    platform: str
    format_type: PlatformFormat
    video_specs: Optional[Dict[str, Any]] = None
    audio_specs: Optional[Dict[str, Any]] = None
    image_specs: Optional[Dict[str, Any]] = None
    text_limits: Optional[Dict[str, int]] = None
    aspect_ratios: Optional[List[str]] = None
    file_size_limits: Optional[Dict[str, int]] = None


@dataclass
class AdaptationResult:
    """Result of content adaptation."""
    success: bool
    source_format: str
    target_format: PlatformFormat
    adapted_content: Dict[str, Any]
    optimizations_applied: List[str]
    quality_score: float
    size_reduction_percent: float
    processing_time_seconds: float
    warnings: List[str]
    errors: List[str]


class FormatAdapter:
    """Advanced content format adaptation engine."""
    
    def __init__(self):
        """Initialize format adapter."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.format_specs = self._initialize_format_specifications()
    
    def _initialize_format_specifications(self) -> Dict[PlatformFormat, FormatSpecification]:
        """Initialize platform format specifications."""
        return {
            PlatformFormat.YOUTUBE_VIDEO: FormatSpecification(
                platform="youtube",
                format_type=PlatformFormat.YOUTUBE_VIDEO,
                video_specs={
                    "min_resolution": "720p",
                    "max_resolution": "4K",
                    "fps": [24, 30, 60],
                    "codecs": ["H.264", "H.265"],
                    "max_duration_seconds": 43200,  # 12 hours
                    "min_duration_seconds": 1
                },
                audio_specs={
                    "sample_rate": [44100, 48000],
                    "bitrate": "128-320 kbps",
                    "channels": ["mono", "stereo"]
                },
                text_limits={
                    "title": 100,
                    "description": 5000,
                    "tags": 500
                },
                aspect_ratios=["16:9", "4:3"],
                file_size_limits={"video": 256 * 1024 * 1024 * 1024}  # 256GB
            ),
            
            PlatformFormat.YOUTUBE_SHORT: FormatSpecification(
                platform="youtube",
                format_type=PlatformFormat.YOUTUBE_SHORT,
                video_specs={
                    "resolution": "1080x1920",
                    "fps": [24, 30, 60],
                    "codecs": ["H.264"],
                    "max_duration_seconds": 60,
                    "min_duration_seconds": 1
                },
                text_limits={
                    "title": 100,
                    "description": 5000
                },
                aspect_ratios=["9:16"],
                file_size_limits={"video": 15 * 1024 * 1024 * 1024}  # 15GB
            ),
            
            PlatformFormat.INSTAGRAM_FEED: FormatSpecification(
                platform="instagram",
                format_type=PlatformFormat.INSTAGRAM_FEED,
                image_specs={
                    "min_resolution": "600x600",
                    "max_resolution": "1080x1080",
                    "formats": ["JPEG", "PNG"]
                },
                video_specs={
                    "resolution": "1080x1080",
                    "fps": [30],
                    "max_duration_seconds": 60,
                    "min_duration_seconds": 3
                },
                text_limits={
                    "caption": 2200,
                    "hashtags": 30
                },
                aspect_ratios=["1:1", "4:5", "16:9"],
                file_size_limits={
                    "image": 30 * 1024 * 1024,  # 30MB
                    "video": 4 * 1024 * 1024 * 1024  # 4GB
                }
            ),
            
            PlatformFormat.INSTAGRAM_STORY: FormatSpecification(
                platform="instagram",
                format_type=PlatformFormat.INSTAGRAM_STORY,
                image_specs={
                    "resolution": "1080x1920",
                    "formats": ["JPEG", "PNG"]
                },
                video_specs={
                    "resolution": "1080x1920",
                    "fps": [30],
                    "max_duration_seconds": 15,
                    "min_duration_seconds": 1
                },
                aspect_ratios=["9:16"],
                file_size_limits={
                    "image": 30 * 1024 * 1024,  # 30MB
                    "video": 4 * 1024 * 1024 * 1024  # 4GB
                }
            ),
            
            PlatformFormat.INSTAGRAM_REEL: FormatSpecification(
                platform="instagram", 
                format_type=PlatformFormat.INSTAGRAM_REEL,
                video_specs={
                    "resolution": "1080x1920",
                    "fps": [30],
                    "max_duration_seconds": 90,
                    "min_duration_seconds": 3
                },
                aspect_ratios=["9:16"],
                file_size_limits={"video": 4 * 1024 * 1024 * 1024}  # 4GB
            ),
            
            PlatformFormat.TIKTOK_VIDEO: FormatSpecification(
                platform="tiktok",
                format_type=PlatformFormat.TIKTOK_VIDEO,
                video_specs={
                    "resolution": "1080x1920",
                    "fps": [30],
                    "max_duration_seconds": 180,  # 3 minutes
                    "min_duration_seconds": 1
                },
                text_limits={
                    "caption": 2200
                },
                aspect_ratios=["9:16"],
                file_size_limits={"video": 4 * 1024 * 1024 * 1024}  # 4GB
            ),
            
            PlatformFormat.SPOTIFY_TRACK: FormatSpecification(
                platform="spotify",
                format_type=PlatformFormat.SPOTIFY_TRACK,
                audio_specs={
                    "formats": ["FLAC", "WAV", "MP3"],
                    "sample_rate": [44100, 48000, 96000],
                    "bit_depth": [16, 24],
                    "channels": ["mono", "stereo"],
                    "min_duration_seconds": 30,
                    "max_duration_seconds": 3600  # 1 hour
                },
                text_limits={
                    "title": 100,
                    "album": 100,
                    "artist": 100
                },
                file_size_limits={"audio": 1024 * 1024 * 1024}  # 1GB
            ),
            
            PlatformFormat.SOUNDCLOUD_TRACK: FormatSpecification(
                platform="soundcloud",
                format_type=PlatformFormat.SOUNDCLOUD_TRACK,
                audio_specs={
                    "formats": ["MP3", "FLAC", "WAV", "AIFF"],
                    "sample_rate": [44100, 48000],
                    "bitrate": "128-320 kbps",
                    "channels": ["mono", "stereo"],
                    "max_duration_seconds": 36000  # 10 hours
                },
                text_limits={
                    "title": 100,
                    "description": 2000,
                    "tags": 10
                },
                file_size_limits={"audio": 5 * 1024 * 1024 * 1024}  # 5GB
            )
        }
    
    async def adapt_content(
        self,
        content: Dict[str, Any],
        target_format: PlatformFormat,
        optimization_level: str = "balanced"  # "fast", "balanced", "quality"
    ) -> AdaptationResult:
        """Adapt content to target platform format.
        
        Args:
            content: Source content data
            target_format: Target platform format
            optimization_level: Optimization level preference
            
        Returns:
            AdaptationResult with adapted content
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting content adaptation to {target_format.value}")
            
            if target_format not in self.format_specs:
                raise ValueError(f"Unsupported target format: {target_format}")
            
            spec = self.format_specs[target_format]
            source_format = content.get("format", "unknown")
            
            # Initialize result
            adapted_content = content.copy()
            optimizations_applied = []
            warnings = []
            errors = []
            
            # Adapt based on content type
            content_type = ContentType(content.get("type", "text"))
            
            if content_type == ContentType.VIDEO:
                adapted_content, video_optimizations, video_warnings = await self._adapt_video(
                    content, spec, optimization_level
                )
                optimizations_applied.extend(video_optimizations)
                warnings.extend(video_warnings)
            
            elif content_type == ContentType.IMAGE:
                adapted_content, image_optimizations, image_warnings = await self._adapt_image(
                    content, spec, optimization_level
                )
                optimizations_applied.extend(image_optimizations)
                warnings.extend(image_warnings)
            
            elif content_type == ContentType.AUDIO:
                adapted_content, audio_optimizations, audio_warnings = await self._adapt_audio(
                    content, spec, optimization_level
                )
                optimizations_applied.extend(audio_optimizations)
                warnings.extend(audio_warnings)
            
            # Adapt text content
            text_adaptations, text_warnings = await self._adapt_text(content, spec)
            adapted_content.update(text_adaptations)
            optimizations_applied.extend(["text_optimization"])
            warnings.extend(text_warnings)
            
            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            quality_score = self._calculate_quality_score(content, adapted_content, spec)
            size_reduction = self._calculate_size_reduction(content, adapted_content)
            
            result = AdaptationResult(
                success=True,
                source_format=source_format,
                target_format=target_format,
                adapted_content=adapted_content,
                optimizations_applied=optimizations_applied,
                quality_score=quality_score,
                size_reduction_percent=size_reduction,
                processing_time_seconds=processing_time,
                warnings=warnings,
                errors=errors
            )
            
            self.logger.info(f"Content adaptation completed: {target_format.value} - "
                           f"Quality: {quality_score:.2f}, "
                           f"Size reduction: {size_reduction:.1f}%")
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.error(f"Content adaptation failed: {str(e)}")
            
            return AdaptationResult(
                success=False,
                source_format=content.get("format", "unknown"),
                target_format=target_format,
                adapted_content={},
                optimizations_applied=[],
                quality_score=0.0,
                size_reduction_percent=0.0,
                processing_time_seconds=processing_time,
                warnings=[],
                errors=[str(e)]
            )
    
    async def _adapt_video(
        self,
        content: Dict[str, Any],
        spec: FormatSpecification,
        optimization_level: str
    ) -> Tuple[Dict[str, Any], List[str], List[str]]:
        """Adapt video content."""
        adapted = content.copy()
        optimizations = []
        warnings = []
        
        # Simulate video processing
        await asyncio.sleep(0.1)
        
        video_specs = spec.video_specs or {}
        
        # Resolution adaptation
        if "resolution" in video_specs:
            target_resolution = video_specs["resolution"]
            adapted["resolution"] = target_resolution
            optimizations.append(f"resolution_adapted_to_{target_resolution}")
        
        # Duration constraints
        current_duration = content.get("duration_seconds", 0)
        max_duration = video_specs.get("max_duration_seconds", float('inf'))
        min_duration = video_specs.get("min_duration_seconds", 0)
        
        if current_duration > max_duration:
            adapted["duration_seconds"] = max_duration
            optimizations.append("duration_trimmed")
            warnings.append(f"Video trimmed from {current_duration}s to {max_duration}s")
        elif current_duration < min_duration:
            warnings.append(f"Video too short: {current_duration}s < {min_duration}s minimum")
        
        # Codec optimization
        if "codecs" in video_specs:
            preferred_codec = video_specs["codecs"][0]
            adapted["codec"] = preferred_codec
            optimizations.append(f"codec_optimized_to_{preferred_codec}")
        
        # Quality optimization based on level
        if optimization_level == "quality":
            adapted["bitrate"] = "high"
            optimizations.append("high_quality_encoding")
        elif optimization_level == "fast":
            adapted["bitrate"] = "medium"
            optimizations.append("fast_encoding")
        else:  # balanced
            adapted["bitrate"] = "balanced"
            optimizations.append("balanced_encoding")
        
        return adapted, optimizations, warnings
    
    async def _adapt_image(
        self,
        content: Dict[str, Any],
        spec: FormatSpecification,
        optimization_level: str
    ) -> Tuple[Dict[str, Any], List[str], List[str]]:
        """Adapt image content."""
        adapted = content.copy()
        optimizations = []
        warnings = []
        
        # Simulate image processing
        await asyncio.sleep(0.05)
        
        image_specs = spec.image_specs or {}
        
        # Resolution optimization
        if "max_resolution" in image_specs:
            max_res = image_specs["max_resolution"]
            adapted["resolution"] = max_res
            optimizations.append(f"resolution_optimized_to_{max_res}")
        
        # Format optimization
        if "formats" in image_specs:
            preferred_format = image_specs["formats"][0]
            adapted["format"] = preferred_format
            optimizations.append(f"format_converted_to_{preferred_format}")
        
        # Quality optimization
        if optimization_level == "quality":
            adapted["quality"] = 95
            optimizations.append("high_quality_compression")
        elif optimization_level == "fast":
            adapted["quality"] = 75
            optimizations.append("fast_compression")
        else:  # balanced
            adapted["quality"] = 85
            optimizations.append("balanced_compression")
        
        return adapted, optimizations, warnings
    
    async def _adapt_audio(
        self,
        content: Dict[str, Any],
        spec: FormatSpecification,
        optimization_level: str
    ) -> Tuple[Dict[str, Any], List[str], List[str]]:
        """Adapt audio content."""
        adapted = content.copy()
        optimizations = []
        warnings = []
        
        # Simulate audio processing
        await asyncio.sleep(0.08)
        
        audio_specs = spec.audio_specs or {}
        
        # Sample rate optimization
        if "sample_rate" in audio_specs:
            preferred_rate = audio_specs["sample_rate"][0]
            adapted["sample_rate"] = preferred_rate
            optimizations.append(f"sample_rate_optimized_to_{preferred_rate}")
        
        # Format optimization
        if "formats" in audio_specs:
            preferred_format = audio_specs["formats"][0]
            adapted["format"] = preferred_format
            optimizations.append(f"format_converted_to_{preferred_format}")
        
        # Bitrate optimization
        if optimization_level == "quality" and "bit_depth" in audio_specs:
            adapted["bit_depth"] = max(audio_specs["bit_depth"])
            optimizations.append("high_quality_audio")
        elif optimization_level == "fast":
            adapted["bitrate"] = "128kbps"
            optimizations.append("fast_encoding")
        else:  # balanced
            adapted["bitrate"] = "256kbps"
            optimizations.append("balanced_encoding")
        
        # Duration check
        current_duration = content.get("duration_seconds", 0)
        max_duration = audio_specs.get("max_duration_seconds", float('inf'))
        min_duration = audio_specs.get("min_duration_seconds", 0)
        
        if current_duration > max_duration:
            adapted["duration_seconds"] = max_duration
            optimizations.append("duration_trimmed")
            warnings.append(f"Audio trimmed from {current_duration}s to {max_duration}s")
        elif current_duration < min_duration:
            warnings.append(f"Audio too short: {current_duration}s < {min_duration}s minimum")
        
        return adapted, optimizations, warnings
    
    async def _adapt_text(
        self,
        content: Dict[str, Any],
        spec: FormatSpecification
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Adapt text content to platform limits."""
        adaptations = {}
        warnings = []
        
        text_limits = spec.text_limits or {}
        
        for field, limit in text_limits.items():
            if field in content and isinstance(content[field], str):
                original_text = content[field]
                if len(original_text) > limit:
                    adapted_text = original_text[:limit-3] + "..."
                    adaptations[field] = adapted_text
                    warnings.append(f"{field} truncated from {len(original_text)} to {limit} characters")
                else:
                    adaptations[field] = original_text
        
        return adaptations, warnings
    
    def _calculate_quality_score(
        self,
        source: Dict[str, Any],
        adapted: Dict[str, Any],
        spec: FormatSpecification
    ) -> float:
        """Calculate adaptation quality score."""
        score = 1.0
        
        # Check if requirements are met
        if spec.video_specs:
            # Resolution score
            source_res = source.get("resolution", "unknown")
            adapted_res = adapted.get("resolution", "unknown")
            if adapted_res != "unknown":
                score *= 0.9  # Some quality loss in adaptation
        
        if spec.audio_specs:
            # Audio quality score
            if adapted.get("bitrate") == "high":
                score *= 0.95
            elif adapted.get("bitrate") == "medium":
                score *= 0.85
            else:
                score *= 0.75
        
        # Text preservation score
        text_fields = ["title", "description", "caption"]
        for field in text_fields:
            if field in source and field in adapted:
                if len(adapted[field]) < len(source[field]):
                    score *= 0.9  # Penalty for text truncation
        
        return max(0.1, min(1.0, score))
    
    def _calculate_size_reduction(
        self,
        source: Dict[str, Any],
        adapted: Dict[str, Any]
    ) -> float:
        """Calculate size reduction percentage."""
        # Simulate size calculation
        source_size = source.get("file_size_mb", 100)
        
        # Estimate adapted size based on optimizations
        reduction_factor = 0.8  # 20% reduction on average
        if adapted.get("quality") == 75:
            reduction_factor = 0.6  # 40% reduction for fast compression
        elif adapted.get("quality") == 95:
            reduction_factor = 0.9  # 10% reduction for high quality
        
        adapted_size = source_size * reduction_factor
        reduction_percent = ((source_size - adapted_size) / source_size) * 100
        
        return max(0.0, min(100.0, reduction_percent))
    
    async def get_platform_requirements(self, platform: str) -> Dict[str, Any]:
        """Get platform format requirements.
        
        Args:
            platform: Platform name
            
        Returns:
            Platform requirements dictionary
        """
        platform_formats = {
            format_spec.format_type: format_spec
            for format_spec in self.format_specs.values()
            if format_spec.platform.lower() == platform.lower()
        }
        
        if not platform_formats:
            return {"error": f"Platform {platform} not supported"}
        
        requirements = {}
        
        for format_type, spec in platform_formats.items():
            format_reqs = {
                "format_type": format_type.value,
                "platform": spec.platform
            }
            
            if spec.video_specs:
                format_reqs["video"] = spec.video_specs
            
            if spec.audio_specs:
                format_reqs["audio"] = spec.audio_specs
                
            if spec.image_specs:
                format_reqs["image"] = spec.image_specs
            
            if spec.text_limits:
                format_reqs["text_limits"] = spec.text_limits
                
            if spec.aspect_ratios:
                format_reqs["aspect_ratios"] = spec.aspect_ratios
                
            if spec.file_size_limits:
                format_reqs["file_size_limits"] = spec.file_size_limits
            
            requirements[format_type.value] = format_reqs
        
        return requirements
    
    async def validate_content_for_platform(
        self,
        content: Dict[str, Any],
        target_format: PlatformFormat
    ) -> Dict[str, Any]:
        """Validate content against platform requirements.
        
        Args:
            content: Content to validate
            target_format: Target platform format
            
        Returns:
            Validation result dictionary
        """
        if target_format not in self.format_specs:
            return {
                "valid": False,
                "errors": [f"Unsupported format: {target_format}"]
            }
        
        spec = self.format_specs[target_format]
        errors = []
        warnings = []
        
        # Validate file size
        if spec.file_size_limits:
            content_size = content.get("file_size_bytes", 0)
            content_type = content.get("type", "unknown")
            
            if content_type in spec.file_size_limits:
                max_size = spec.file_size_limits[content_type]
                if content_size > max_size:
                    errors.append(f"File size {content_size} exceeds limit {max_size}")
        
        # Validate text limits
        if spec.text_limits:
            for field, limit in spec.text_limits.items():
                if field in content:
                    text_length = len(str(content[field]))
                    if text_length > limit:
                        warnings.append(f"{field} length {text_length} exceeds limit {limit}")
        
        # Validate video specs
        if spec.video_specs and content.get("type") == "video":
            duration = content.get("duration_seconds", 0)
            max_duration = spec.video_specs.get("max_duration_seconds", float('inf'))
            min_duration = spec.video_specs.get("min_duration_seconds", 0)
            
            if duration > max_duration:
                warnings.append(f"Video duration {duration}s exceeds maximum {max_duration}s")
            elif duration < min_duration:
                errors.append(f"Video duration {duration}s below minimum {min_duration}s")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "adaptations_needed": len(warnings) > 0
        }


# Global format adapter instance
_format_adapter: Optional[FormatAdapter] = None


def get_format_adapter() -> FormatAdapter:
    """Get global format adapter instance."""
    global _format_adapter
    
    if _format_adapter is None:
        _format_adapter = FormatAdapter()
    
    return _format_adapter


# Convenience functions
async def adapt_for_platform(
    content: Dict[str, Any],
    platform: str,
    format_type: str = "default"
) -> AdaptationResult:
    """Convenience function to adapt content for platform."""
    adapter = get_format_adapter()
    
    # Map platform and format to PlatformFormat enum
    format_mapping = {
        ("youtube", "video"): PlatformFormat.YOUTUBE_VIDEO,
        ("youtube", "short"): PlatformFormat.YOUTUBE_SHORT,
        ("instagram", "feed"): PlatformFormat.INSTAGRAM_FEED,
        ("instagram", "story"): PlatformFormat.INSTAGRAM_STORY,
        ("instagram", "reel"): PlatformFormat.INSTAGRAM_REEL,
        ("tiktok", "video"): PlatformFormat.TIKTOK_VIDEO,
        ("spotify", "track"): PlatformFormat.SPOTIFY_TRACK,
        ("soundcloud", "track"): PlatformFormat.SOUNDCLOUD_TRACK
    }
    
    # Default formats for platforms
    if format_type == "default":
        default_formats = {
            "youtube": PlatformFormat.YOUTUBE_VIDEO,
            "instagram": PlatformFormat.INSTAGRAM_FEED,
            "tiktok": PlatformFormat.TIKTOK_VIDEO,
            "spotify": PlatformFormat.SPOTIFY_TRACK,
            "soundcloud": PlatformFormat.SOUNDCLOUD_TRACK
        }
        target_format = default_formats.get(platform.lower())
    else:
        target_format = format_mapping.get((platform.lower(), format_type.lower()))
    
    if not target_format:
        raise ValueError(f"Unsupported platform/format combination: {platform}/{format_type}")
    
    return await adapter.adapt_content(content, target_format)