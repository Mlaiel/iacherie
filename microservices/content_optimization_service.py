"""
Content Optimization Service - Enterprise Microservice
====================================================

Advanced content optimization system for multi-platform distribution with AI-powered
enhancement, format adaptation, and performance optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import json
import uuid
from collections import defaultdict
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlatformType(str, Enum):
    """Supported platforms for optimization."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    MEDIUM = "medium"
    WORDPRESS = "wordpress"
    AINFLUE = "ainflue"


class ContentType(str, Enum):
    """Content types for optimization."""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    THUMBNAIL = "thumbnail"
    COVER_ART = "cover_art"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"


class OptimizationType(str, Enum):
    """Types of optimization."""
    FORMAT_CONVERSION = "format_conversion"
    RESOLUTION_SCALING = "resolution_scaling"
    COMPRESSION = "compression"
    SEO_ENHANCEMENT = "seo_enhancement"
    METADATA_OPTIMIZATION = "metadata_optimization"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    SUBTITLE_GENERATION = "subtitle_generation"
    AUDIO_ENHANCEMENT = "audio_enhancement"
    COLOR_CORRECTION = "color_correction"
    QUALITY_IMPROVEMENT = "quality_improvement"
    ACCESSIBILITY_ENHANCEMENT = "accessibility_enhancement"
    LOCALIZATION = "localization"


class OptimizationStatus(str, Enum):
    """Optimization process status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class PlatformRequirements:
    """Platform-specific requirements and constraints."""
    platform: PlatformType
    max_file_size: int  # in bytes
    supported_formats: List[str]
    max_duration: Optional[int] = None  # in seconds
    min_resolution: Optional[Tuple[int, int]] = None
    max_resolution: Optional[Tuple[int, int]] = None
    aspect_ratios: List[str] = field(default_factory=list)
    required_metadata: List[str] = field(default_factory=list)
    character_limits: Dict[str, int] = field(default_factory=dict)
    special_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationSettings:
    """Optimization settings and preferences."""
    target_quality: str = "high"  # low, medium, high, ultra
    preserve_aspect_ratio: bool = True
    enable_upscaling: bool = False
    compression_level: str = "balanced"  # lossless, high, balanced, aggressive
    generate_thumbnails: bool = True
    generate_previews: bool = True
    add_watermark: bool = False
    enhance_audio: bool = True
    auto_subtitles: bool = False
    color_enhancement: bool = True
    noise_reduction: bool = True


class OptimizationRequest(BaseModel):
    """Content optimization request."""
    content_id: str = Field(..., description="Content identifier")
    source_url: str = Field(..., description="Source content URL")
    content_type: ContentType = Field(..., description="Content type")
    target_platforms: List[PlatformType] = Field(..., description="Target platforms")
    optimization_types: List[OptimizationType] = Field(default_factory=list)
    settings: OptimizationSettings = Field(default_factory=OptimizationSettings)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    priority: int = Field(default=5, description="Processing priority (1-10)")
    deadline: Optional[datetime] = Field(None, description="Optimization deadline")


class OptimizedVariant(BaseModel):
    """Single optimized content variant."""
    variant_id: str = Field(..., description="Variant identifier")
    platform: PlatformType = Field(..., description="Target platform")
    content_type: ContentType = Field(..., description="Content type")
    optimized_url: str = Field(..., description="URL to optimized content")
    file_size: int = Field(..., description="File size in bytes")
    format: str = Field(..., description="File format")
    resolution: Optional[Tuple[int, int]] = Field(None, description="Resolution (width, height)")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    bitrate: Optional[int] = Field(None, description="Bitrate")
    quality_score: float = Field(..., description="Quality score (0-1)")
    compression_ratio: float = Field(..., description="Compression ratio")
    optimizations_applied: List[OptimizationType] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class OptimizationResult(BaseModel):
    """Complete optimization result."""
    content_id: str = Field(..., description="Original content ID")
    request_id: str = Field(..., description="Optimization request ID")
    status: OptimizationStatus = Field(..., description="Overall status")
    variants: List[OptimizedVariant] = Field(default_factory=list)
    processing_time: float = Field(default=0.0, description="Total processing time")
    total_size_reduction: float = Field(default=0.0, description="Total size reduction percentage")
    average_quality_score: float = Field(default=0.0, description="Average quality across variants")
    optimizations_completed: List[OptimizationType] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None)


class ContentOptimizationService:
    """
    Enterprise Content Optimization Service
    
    Provides comprehensive content optimization for multi-platform distribution
    with AI-powered enhancement, format adaptation, and performance optimization.
    """
    
    def __init__(self) -> None:
        self.optimization_requests: Dict[str, OptimizationRequest] = {}
        self.optimization_results: Dict[str, OptimizationResult] = {}
        self.platform_requirements: Dict[PlatformType, PlatformRequirements] = {}
        self.processing_queue: List[str] = []  # request IDs
        self.optimization_processors: Dict[OptimizationType, Any] = {}
        self.format_converters: Dict[str, Any] = {}
        self.quality_enhancers: Dict[ContentType, Any] = {}
        
        # Initialize system
        self._initialize_platform_requirements()
        self._initialize_optimization_processors()
        self._initialize_format_converters()
        self._initialize_quality_enhancers()
        
        logger.info("ContentOptimizationService initialized successfully")
    
    def _initialize_platform_requirements(self) -> None:
        """Initialize platform-specific requirements."""
        self.platform_requirements = {
            PlatformType.YOUTUBE: PlatformRequirements(
                platform=PlatformType.YOUTUBE,
                max_file_size=256 * 1024 * 1024 * 1024,  # 256 GB
                supported_formats=["mp4", "mov", "avi", "wmv", "mpg", "flv", "webm"],
                max_duration=12 * 3600,  # 12 hours
                min_resolution=(426, 240),
                max_resolution=(7680, 4320),  # 8K
                aspect_ratios=["16:9", "4:3", "1:1", "9:16"],
                required_metadata=["title", "description"],
                character_limits={"title": 100, "description": 5000},
                special_requirements={
                    "thumbnails": {"formats": ["jpg", "png"], "resolution": (1280, 720)},
                    "captions": True,
                    "end_screens": True
                }
            ),
            PlatformType.INSTAGRAM: PlatformRequirements(
                platform=PlatformType.INSTAGRAM,
                max_file_size=100 * 1024 * 1024,  # 100 MB
                supported_formats=["mp4", "mov"],
                max_duration=60,  # 60 seconds for reels
                min_resolution=(600, 315),
                max_resolution=(1920, 1080),
                aspect_ratios=["1:1", "4:5", "9:16"],
                character_limits={"caption": 2200},
                special_requirements={
                    "story_duration": 15,
                    "reel_duration": 90,
                    "igtv_duration": 3600
                }
            ),
            PlatformType.TIKTOK: PlatformRequirements(
                platform=PlatformType.TIKTOK,
                max_file_size=287 * 1024 * 1024,  # 287 MB
                supported_formats=["mp4", "mov"],
                max_duration=300,  # 5 minutes
                min_resolution=(540, 960),
                max_resolution=(1080, 1920),
                aspect_ratios=["9:16"],
                character_limits={"caption": 4000},
                special_requirements={
                    "optimal_resolution": (1080, 1920),
                    "frame_rate": [23.976, 24, 25, 29.97, 30],
                    "bitrate": {"min": 516, "max": 10000}
                }
            ),
            PlatformType.TWITTER: PlatformRequirements(
                platform=PlatformType.TWITTER,
                max_file_size=512 * 1024 * 1024,  # 512 MB
                supported_formats=["mp4", "mov"],
                max_duration=140,  # 2 minutes 20 seconds
                min_resolution=(32, 32),
                max_resolution=(1920, 1200),
                aspect_ratios=["16:9", "1:1", "2:1"],
                character_limits={"tweet": 280},
                special_requirements={
                    "gif_duration": 6,
                    "optimal_resolution": (1280, 720)
                }
            ),
            PlatformType.LINKEDIN: PlatformRequirements(
                platform=PlatformType.LINKEDIN,
                max_file_size=200 * 1024 * 1024,  # 200 MB
                supported_formats=["mp4", "mov", "wmv", "avi"],
                max_duration=600,  # 10 minutes
                min_resolution=(256, 144),
                max_resolution=(4096, 2304),
                aspect_ratios=["16:9", "1:1", "4:5"],
                character_limits={"post": 3000},
                special_requirements={
                    "professional_focus": True,
                    "captions_recommended": True
                }
            ),
            PlatformType.SPOTIFY: PlatformRequirements(
                platform=PlatformType.SPOTIFY,
                max_file_size=200 * 1024 * 1024,  # 200 MB
                supported_formats=["mp3", "flac", "wav", "ogg"],
                max_duration=None,  # No limit
                required_metadata=["title", "artist", "album"],
                special_requirements={
                    "bit_depth": [16, 24],
                    "sample_rate": [44100, 48000, 96000],
                    "cover_art": {"formats": ["jpg", "png"], "resolution": (640, 640)}
                }
            ),
            PlatformType.PINTEREST: PlatformRequirements(
                platform=PlatformType.PINTEREST,
                max_file_size=20 * 1024 * 1024,  # 20 MB
                supported_formats=["jpg", "png", "gif", "mp4"],
                max_duration=15,  # 15 seconds for video
                min_resolution=(600, 600),
                max_resolution=(2000, 2000),
                aspect_ratios=["2:3", "1:2.1", "1:1"],
                character_limits={"description": 500},
                special_requirements={
                    "vertical_preferred": True,
                    "high_quality_images": True
                }
            )
        }
    
    def _initialize_optimization_processors(self) -> None:
        """Initialize optimization processors."""
        self.optimization_processors = {
            OptimizationType.FORMAT_CONVERSION: self._process_format_conversion,
            OptimizationType.RESOLUTION_SCALING: self._process_resolution_scaling,
            OptimizationType.COMPRESSION: self._process_compression,
            OptimizationType.SEO_ENHANCEMENT: self._process_seo_enhancement,
            OptimizationType.METADATA_OPTIMIZATION: self._process_metadata_optimization,
            OptimizationType.THUMBNAIL_GENERATION: self._process_thumbnail_generation,
            OptimizationType.SUBTITLE_GENERATION: self._process_subtitle_generation,
            OptimizationType.AUDIO_ENHANCEMENT: self._process_audio_enhancement,
            OptimizationType.COLOR_CORRECTION: self._process_color_correction,
            OptimizationType.QUALITY_IMPROVEMENT: self._process_quality_improvement,
            OptimizationType.ACCESSIBILITY_ENHANCEMENT: self._process_accessibility_enhancement,
            OptimizationType.LOCALIZATION: self._process_localization
        }
    
    def _initialize_format_converters(self) -> None:
        """Initialize format conversion capabilities."""
        self.format_converters = {
            "video": {
                "input_formats": ["mp4", "avi", "mov", "wmv", "flv", "mkv", "webm"],
                "output_formats": ["mp4", "webm", "mov"],
                "codecs": {
                    "mp4": ["h264", "h265"],
                    "webm": ["vp9", "av1"],
                    "mov": ["h264", "prores"]
                }
            },
            "audio": {
                "input_formats": ["mp3", "wav", "flac", "aac", "ogg", "m4a"],
                "output_formats": ["mp3", "aac", "ogg", "wav"],
                "codecs": {
                    "mp3": ["mp3"],
                    "aac": ["aac"],
                    "ogg": ["vorbis", "opus"],
                    "wav": ["pcm"]
                }
            },
            "image": {
                "input_formats": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
                "output_formats": ["jpg", "png", "webp", "avif"],
                "quality_levels": [60, 70, 80, 90, 95]
            }
        }
    
    def _initialize_quality_enhancers(self) -> None:
        """Initialize AI-powered quality enhancement modules."""
        self.quality_enhancers = {
            ContentType.VIDEO: {
                "upscaling": {"model": "ESRGAN", "max_scale": 4},
                "denoising": {"model": "DnCNN", "strength_levels": [1, 2, 3]},
                "stabilization": {"model": "DeepStab", "strength": 0.7},
                "color_grading": {"model": "ColorNet", "presets": ["natural", "vibrant", "cinematic"]}
            },
            ContentType.AUDIO: {
                "noise_reduction": {"model": "RNNoise", "strength_levels": [1, 2, 3]},
                "enhancement": {"model": "AudioSR", "sample_rates": [44100, 48000]},
                "mastering": {"model": "LANDR", "styles": ["balanced", "warm", "bright"]},
                "vocal_isolation": {"model": "Spleeter", "stems": [2, 4, 5]}
            },
            ContentType.IMAGE: {
                "upscaling": {"model": "Real-ESRGAN", "max_scale": 8},
                "denoising": {"model": "DnCNN", "noise_types": ["gaussian", "poisson"]},
                "enhancement": {"model": "EDSR", "features": ["sharpness", "contrast", "saturation"]},
                "restoration": {"model": "GFPGAN", "face_enhancement": True}
            }
        }
    
    async def optimize_content(self, request: OptimizationRequest) -> str:
        """Start content optimization process."""
        try:
            request_id = f"opt_{uuid.uuid4().hex[:8]}"
            
            # Store request
            self.optimization_requests[request_id] = request
            
            # Initialize result
            result = OptimizationResult(
                content_id=request.content_id,
                request_id=request_id,
                status=OptimizationStatus.PENDING
            )
            self.optimization_results[request_id] = result
            
            # Add to processing queue
            self.processing_queue.append(request_id)
            
            # Start processing asynchronously
            asyncio.create_task(self._process_optimization_request(request_id))
            
            logger.info(f"Started optimization request {request_id} for content {request.content_id}")
            return request_id
            
        except Exception as e:
            logger.error(f"Error starting optimization: {e}")
            raise
    
    async def _process_optimization_request(self, request_id -> None: str) -> None:
        """Process optimization request."""
        try:
            request = self.optimization_requests[request_id]
            result = self.optimization_results[request_id]
            
            # Update status
            result.status = OptimizationStatus.PROCESSING
            start_time = datetime.now()
            
            # Process each target platform
            for platform in request.target_platforms:
                try:
                    variants = await self._optimize_for_platform(request, platform)
                    result.variants.extend(variants)
                except Exception as e:
                    error_msg = f"Error optimizing for {platform}: {str(e)}"
                    result.errors.append(error_msg)
                    logger.error(error_msg)
            
            # Calculate overall metrics
            if result.variants:
                result.status = OptimizationStatus.COMPLETED
                result.average_quality_score = sum(v.quality_score for v in result.variants) / len(result.variants)
                
                # Calculate size reduction
                original_size = 100 * 1024 * 1024  # Placeholder: 100MB
                total_optimized_size = sum(v.file_size for v in result.variants)
                if len(result.variants) > 0:
                    avg_optimized_size = total_optimized_size / len(result.variants)
                    result.total_size_reduction = ((original_size - avg_optimized_size) / original_size) * 100
                
                # Collect applied optimizations
                all_optimizations = set()
                for variant in result.variants:
                    all_optimizations.update(variant.optimizations_applied)
                result.optimizations_completed = list(all_optimizations)
            else:
                result.status = OptimizationStatus.FAILED
                result.errors.append("No variants were successfully created")
            
            # Calculate processing time
            result.processing_time = (datetime.now() - start_time).total_seconds()
            result.completed_at = datetime.now()
            
            # Remove from processing queue
            if request_id in self.processing_queue:
                self.processing_queue.remove(request_id)
            
            logger.info(f"Completed optimization request {request_id}")
            
        except Exception as e:
            logger.error(f"Error processing optimization request {request_id}: {e}")
            result.status = OptimizationStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.now()
            
            if request_id in self.processing_queue:
                self.processing_queue.remove(request_id)
    
    async def _optimize_for_platform(
        self, 
        request: OptimizationRequest, 
        platform: PlatformType
    ) -> List[OptimizedVariant]:
        """Optimize content for specific platform."""
        try:
            platform_req = self.platform_requirements.get(platform)
            if not platform_req:
                raise ValueError(f"Platform {platform} not supported")
            
            variants = []
            
            # Determine optimizations needed
            optimizations_needed = await self._determine_optimizations(request, platform_req)
            
            # Create base variant
            base_variant = await self._create_base_variant(request, platform)
            
            # Apply optimizations
            optimized_variant = base_variant
            for optimization in optimizations_needed:
                try:
                    optimized_variant = await self._apply_optimization(
                        optimized_variant, optimization, platform_req, request.settings
                    )
                except Exception as e:
                    logger.error(f"Error applying {optimization}: {e}")
                    continue
            
            # Validate against platform requirements
            if await self._validate_platform_requirements(optimized_variant, platform_req):
                variants.append(optimized_variant)
            else:
                logger.warning(f"Variant for {platform} doesn't meet requirements")
            
            return variants
            
        except Exception as e:
            logger.error(f"Error optimizing for platform {platform}: {e}")
            return []
    
    async def _determine_optimizations(
        self, 
        request: OptimizationRequest, 
        platform_req: PlatformRequirements
    ) -> List[OptimizationType]:
        """Determine which optimizations are needed for platform."""
        optimizations = []
        
        # Always include format conversion check
        optimizations.append(OptimizationType.FORMAT_CONVERSION)
        
        # Add resolution scaling if needed
        if platform_req.max_resolution or platform_req.min_resolution:
            optimizations.append(OptimizationType.RESOLUTION_SCALING)
        
        # Add compression for size requirements
        if platform_req.max_file_size:
            optimizations.append(OptimizationType.COMPRESSION)
        
        # Add SEO enhancement for text-heavy platforms
        if platform_req.character_limits:
            optimizations.append(OptimizationType.SEO_ENHANCEMENT)
        
        # Add metadata optimization
        if platform_req.required_metadata:
            optimizations.append(OptimizationType.METADATA_OPTIMIZATION)
        
        # Add thumbnail generation for video platforms
        if (request.content_type == ContentType.VIDEO and 
            "thumbnails" in platform_req.special_requirements):
            optimizations.append(OptimizationType.THUMBNAIL_GENERATION)
        
        # Add quality improvements if enabled
        if request.settings.color_enhancement:
            optimizations.append(OptimizationType.COLOR_CORRECTION)
        
        if request.settings.enhance_audio and request.content_type in [ContentType.VIDEO, ContentType.AUDIO]:
            optimizations.append(OptimizationType.AUDIO_ENHANCEMENT)
        
        # Add accessibility enhancements
        if request.settings.auto_subtitles:
            optimizations.append(OptimizationType.SUBTITLE_GENERATION)
        
        # Include user-specified optimizations
        optimizations.extend(request.optimization_types)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_optimizations = []
        for opt in optimizations:
            if opt not in seen:
                seen.add(opt)
                unique_optimizations.append(opt)
        
        return unique_optimizations
    
    async def _create_base_variant(
        self, 
        request: OptimizationRequest, 
        platform: PlatformType
    ) -> OptimizedVariant:
        """Create base variant before optimizations."""
        variant_id = f"var_{uuid.uuid4().hex[:8]}"
        
        # Placeholder for actual content analysis
        # In real implementation, would analyze source content
        
        return OptimizedVariant(
            variant_id=variant_id,
            platform=platform,
            content_type=request.content_type,
            optimized_url=request.source_url,  # Initially same as source
            file_size=50 * 1024 * 1024,  # Placeholder: 50MB
            format="mp4",  # Placeholder
            resolution=(1920, 1080),  # Placeholder
            duration=120.0,  # Placeholder: 2 minutes
            bitrate=5000,  # Placeholder: 5Mbps
            quality_score=0.7,  # Initial quality
            compression_ratio=1.0,  # No compression yet
            metadata=request.metadata.copy()
        )
    
    async def _apply_optimization(
        self, 
        variant: OptimizedVariant, 
        optimization: OptimizationType,
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Apply specific optimization to variant."""
        try:
            processor = self.optimization_processors.get(optimization)
            if not processor:
                logger.warning(f"No processor for optimization {optimization}")
                return variant
            
            # Apply optimization
            optimized_variant = await processor(variant, platform_req, settings)
            
            # Track applied optimization
            if optimization not in optimized_variant.optimizations_applied:
                optimized_variant.optimizations_applied.append(optimization)
            
            return optimized_variant
            
        except Exception as e:
            logger.error(f"Error applying optimization {optimization}: {e}")
            return variant
    
    # Optimization processors
    async def _process_format_conversion(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Convert content format for platform compatibility."""
        # Check if current format is supported
        if variant.format in platform_req.supported_formats:
            return variant  # No conversion needed
        
        # Select best target format
        if variant.content_type == ContentType.VIDEO:
            if "mp4" in platform_req.supported_formats:
                target_format = "mp4"
            else:
                target_format = platform_req.supported_formats[0]
        elif variant.content_type == ContentType.AUDIO:
            if "mp3" in platform_req.supported_formats:
                target_format = "mp3"
            else:
                target_format = platform_req.supported_formats[0]
        else:
            target_format = platform_req.supported_formats[0]
        
        # Simulate format conversion
        converted_variant = variant.copy()
        converted_variant.format = target_format
        converted_variant.optimized_url = f"{variant.optimized_url}.{target_format}"
        
        # Adjust file size based on format (placeholder logic)
        format_efficiency = {
            "mp4": 1.0,
            "webm": 0.8,
            "mov": 1.2,
            "mp3": 0.1,
            "aac": 0.08,
            "ogg": 0.09
        }
        
        efficiency = format_efficiency.get(target_format, 1.0)
        converted_variant.file_size = int(variant.file_size * efficiency)
        converted_variant.compression_ratio = variant.compression_ratio * efficiency
        
        return converted_variant
    
    async def _process_resolution_scaling(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Scale resolution to meet platform requirements."""
        if not variant.resolution:
            return variant
        
        current_width, current_height = variant.resolution
        
        # Check if scaling is needed
        needs_scaling = False
        target_width, target_height = current_width, current_height
        
        # Check maximum resolution
        if platform_req.max_resolution:
            max_width, max_height = platform_req.max_resolution
            if current_width > max_width or current_height > max_height:
                # Scale down to fit
                scale_factor = min(max_width / current_width, max_height / current_height)
                target_width = int(current_width * scale_factor)
                target_height = int(current_height * scale_factor)
                needs_scaling = True
        
        # Check minimum resolution
        if platform_req.min_resolution:
            min_width, min_height = platform_req.min_resolution
            if target_width < min_width or target_height < min_height:
                if settings.enable_upscaling:
                    # Scale up to meet minimum
                    scale_factor = max(min_width / target_width, min_height / target_height)
                    target_width = int(target_width * scale_factor)
                    target_height = int(target_height * scale_factor)
                    needs_scaling = True
                else:
                    logger.warning("Resolution below minimum and upscaling disabled")
        
        if not needs_scaling:
            return variant
        
        # Apply scaling
        scaled_variant = variant.copy()
        scaled_variant.resolution = (target_width, target_height)
        
        # Adjust file size and quality based on resolution change
        pixel_ratio = (target_width * target_height) / (current_width * current_height)
        scaled_variant.file_size = int(variant.file_size * pixel_ratio)
        
        # Quality impact of scaling
        if pixel_ratio > 1 and not settings.enable_upscaling:
            # Upscaling without enhancement reduces quality
            scaled_variant.quality_score = variant.quality_score * 0.9
        elif pixel_ratio < 1:
            # Downscaling typically maintains quality
            scaled_variant.quality_score = variant.quality_score * 0.95
        
        return scaled_variant
    
    async def _process_compression(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Apply compression to meet size requirements."""
        if variant.file_size <= platform_req.max_file_size:
            return variant  # No compression needed
        
        # Calculate required compression ratio
        required_ratio = platform_req.max_file_size / variant.file_size
        
        # Apply compression based on settings
        compression_settings = {
            "lossless": {"ratio": 0.8, "quality_impact": 1.0},
            "high": {"ratio": 0.6, "quality_impact": 0.95},
            "balanced": {"ratio": 0.4, "quality_impact": 0.85},
            "aggressive": {"ratio": 0.2, "quality_impact": 0.7}
        }
        
        compression_level = settings.compression_level
        compression_config = compression_settings.get(compression_level, compression_settings["balanced"])
        
        # Apply multiple passes if needed
        final_ratio = max(required_ratio, compression_config["ratio"])
        
        compressed_variant = variant.copy()
        compressed_variant.file_size = int(variant.file_size * final_ratio)
        compressed_variant.compression_ratio = variant.compression_ratio * final_ratio
        compressed_variant.quality_score = variant.quality_score * compression_config["quality_impact"]
        
        # Adjust bitrate for video/audio
        if variant.bitrate:
            compressed_variant.bitrate = int(variant.bitrate * final_ratio)
        
        return compressed_variant
    
    async def _process_seo_enhancement(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Enhance metadata for SEO."""
        enhanced_variant = variant.copy()
        
        # Optimize title if character limit exists
        if "title" in platform_req.character_limits:
            title_limit = platform_req.character_limits["title"]
            current_title = enhanced_variant.metadata.get("title", "")
            
            if len(current_title) > title_limit:
                # Truncate while preserving important keywords
                enhanced_variant.metadata["title"] = current_title[:title_limit-3] + "..."
            elif len(current_title) < title_limit * 0.8:
                # Add keywords if title is too short
                enhanced_variant.metadata["title"] = self._enhance_title_with_keywords(
                    current_title, title_limit
                )
        
        # Optimize description
        if "description" in platform_req.character_limits:
            desc_limit = platform_req.character_limits["description"]
            current_desc = enhanced_variant.metadata.get("description", "")
            
            if len(current_desc) > desc_limit:
                enhanced_variant.metadata["description"] = current_desc[:desc_limit-3] + "..."
            else:
                # Enhance description with SEO keywords
                enhanced_variant.metadata["description"] = self._enhance_description_with_seo(
                    current_desc, desc_limit
                )
        
        # Add platform-specific hashtags
        enhanced_variant.metadata["hashtags"] = self._generate_platform_hashtags(
            variant.platform, enhanced_variant.metadata
        )
        
        return enhanced_variant
    
    async def _process_metadata_optimization(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Optimize metadata for platform requirements."""
        optimized_variant = variant.copy()
        
        # Ensure required metadata is present
        for required_field in platform_req.required_metadata:
            if required_field not in optimized_variant.metadata:
                # Generate default values
                if required_field == "title":
                    optimized_variant.metadata["title"] = f"Content {variant.variant_id}"
                elif required_field == "description":
                    optimized_variant.metadata["description"] = "High-quality content optimized for your platform"
                elif required_field == "artist":
                    optimized_variant.metadata["artist"] = "Unknown Artist"
                elif required_field == "album":
                    optimized_variant.metadata["album"] = "Single"
        
        # Add platform-specific metadata
        if variant.platform == PlatformType.YOUTUBE:
            optimized_variant.metadata.update({
                "category": "Entertainment",
                "language": "en",
                "privacy": "public"
            })
        elif variant.platform == PlatformType.SPOTIFY:
            optimized_variant.metadata.update({
                "genre": "Electronic",
                "release_date": datetime.now().strftime("%Y-%m-%d"),
                "copyright": "All rights reserved"
            })
        
        return optimized_variant
    
    async def _process_thumbnail_generation(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Generate thumbnails for video content."""
        if variant.content_type != ContentType.VIDEO:
            return variant
        
        thumbnail_variant = variant.copy()
        
        # Generate thumbnail at optimal time (placeholder logic)
        if variant.duration:
            optimal_time = variant.duration * 0.3  # 30% into video
        else:
            optimal_time = 5.0  # 5 seconds default
        
        # Get platform thumbnail requirements
        thumb_req = platform_req.special_requirements.get("thumbnails", {})
        thumb_resolution = thumb_req.get("resolution", (1280, 720))
        thumb_formats = thumb_req.get("formats", ["jpg"])
        
        # Generate thumbnail metadata
        thumbnail_variant.metadata["thumbnail"] = {
            "url": f"{variant.optimized_url}_thumb.{thumb_formats[0]}",
            "resolution": thumb_resolution,
            "timestamp": optimal_time,
            "format": thumb_formats[0]
        }
        
        return thumbnail_variant
    
    async def _process_subtitle_generation(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Generate subtitles for video content."""
        if variant.content_type != ContentType.VIDEO:
            return variant
        
        subtitle_variant = variant.copy()
        
        # Placeholder subtitle generation
        # In real implementation, would use speech-to-text AI
        subtitle_variant.metadata["subtitles"] = {
            "languages": ["en"],
            "format": "srt",
            "url": f"{variant.optimized_url}_subtitles.srt",
            "auto_generated": True
        }
        
        return subtitle_variant
    
    async def _process_audio_enhancement(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Enhance audio quality."""
        if variant.content_type not in [ContentType.VIDEO, ContentType.AUDIO]:
            return variant
        
        enhanced_variant = variant.copy()
        
        # Apply audio enhancements
        enhancements_applied = []
        
        if settings.noise_reduction:
            enhanced_variant.quality_score = min(1.0, enhanced_variant.quality_score * 1.05)
            enhancements_applied.append("noise_reduction")
        
        # Normalize audio levels
        enhanced_variant.metadata["audio_processing"] = {
            "normalization": True,
            "enhancements": enhancements_applied,
            "peak_level": -1.0,  # dB
            "rms_level": -20.0   # dB
        }
        
        return enhanced_variant
    
    async def _process_color_correction(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Apply color correction and enhancement."""
        if variant.content_type not in [ContentType.VIDEO, ContentType.IMAGE]:
            return variant
        
        color_corrected_variant = variant.copy()
        
        # Apply color corrections
        corrections = {
            "brightness": 1.05,
            "contrast": 1.1,
            "saturation": 1.02,
            "gamma": 1.0
        }
        
        color_corrected_variant.metadata["color_processing"] = corrections
        color_corrected_variant.quality_score = min(1.0, color_corrected_variant.quality_score * 1.03)
        
        return color_corrected_variant
    
    async def _process_quality_improvement(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Apply AI-powered quality improvements."""
        quality_improved_variant = variant.copy()
        
        # Apply quality improvements based on content type
        if variant.content_type == ContentType.VIDEO:
            improvements = ["stabilization", "sharpening", "denoising"]
        elif variant.content_type == ContentType.AUDIO:
            improvements = ["mastering", "enhancement"]
        elif variant.content_type == ContentType.IMAGE:
            improvements = ["sharpening", "denoising", "enhancement"]
        else:
            improvements = []
        
        if improvements:
            quality_improved_variant.metadata["ai_improvements"] = improvements
            quality_improved_variant.quality_score = min(1.0, quality_improved_variant.quality_score * 1.1)
        
        return quality_improved_variant
    
    async def _process_accessibility_enhancement(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Add accessibility enhancements."""
        accessible_variant = variant.copy()
        
        accessibility_features = []
        
        if variant.content_type == ContentType.VIDEO:
            accessibility_features.extend(["closed_captions", "audio_descriptions"])
        elif variant.content_type == ContentType.IMAGE:
            accessibility_features.extend(["alt_text", "high_contrast_version"])
        elif variant.content_type == ContentType.AUDIO:
            accessibility_features.extend(["transcript", "visual_waveform"])
        
        accessible_variant.metadata["accessibility"] = {
            "features": accessibility_features,
            "compliance": "WCAG 2.1 AA"
        }
        
        return accessible_variant
    
    async def _process_localization(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements,
        settings: OptimizationSettings
    ) -> OptimizedVariant:
        """Add localization for different markets."""
        localized_variant = variant.copy()
        
        # Add localized metadata
        localized_variant.metadata["localization"] = {
            "primary_language": "en",
            "available_languages": ["en", "es", "fr", "de"],
            "region_optimized": True
        }
        
        return localized_variant
    
    # Helper methods
    def _enhance_title_with_keywords(self, title: str, limit: int) -> str:
        """Enhance title with relevant keywords."""
        keywords = ["AI", "Tutorial", "Guide", "Tips", "2025"]
        
        available_space = limit - len(title)
        for keyword in keywords:
            if available_space > len(keyword) + 3:  # +3 for spacing
                title += f" | {keyword}"
                available_space -= len(keyword) + 3
            else:
                break
        
        return title[:limit]
    
    def _enhance_description_with_seo(self, description: str, limit: int) -> str:
        """Enhance description with SEO keywords."""
        seo_additions = [
            "\n\n🔔 Subscribe for more content!",
            "\n💬 Leave a comment below",
            "\n👍 Like if this helped you",
            "\n📱 Follow us on social media"
        ]
        
        available_space = limit - len(description)
        for addition in seo_additions:
            if available_space > len(addition):
                description += addition
                available_space -= len(addition)
            else:
                break
        
        return description[:limit]
    
    def _generate_platform_hashtags(self, platform: PlatformType, metadata: Dict[str, Any]) -> List[str]:
        """Generate platform-specific hashtags."""
        base_tags = ["content", "creative", "digital"]
        
        platform_specific = {
            PlatformType.INSTAGRAM: ["instagram", "insta", "photo", "video"],
            PlatformType.TIKTOK: ["tiktok", "viral", "trending", "fyp"],
            PlatformType.TWITTER: ["twitter", "tweet", "social"],
            PlatformType.LINKEDIN: ["linkedin", "professional", "business"],
            PlatformType.YOUTUBE: ["youtube", "video", "subscribe"]
        }
        
        tags = base_tags + platform_specific.get(platform, [])
        
        # Add content-specific tags
        if "genre" in metadata:
            tags.append(metadata["genre"].lower())
        
        return tags[:10]  # Limit to 10 hashtags
    
    async def _validate_platform_requirements(
        self, 
        variant: OptimizedVariant, 
        platform_req: PlatformRequirements
    ) -> bool:
        """Validate variant against platform requirements."""
        try:
            # Check file size
            if variant.file_size > platform_req.max_file_size:
                return False
            
            # Check format
            if variant.format not in platform_req.supported_formats:
                return False
            
            # Check resolution
            if variant.resolution and platform_req.max_resolution:
                width, height = variant.resolution
                max_width, max_height = platform_req.max_resolution
                if width > max_width or height > max_height:
                    return False
            
            if variant.resolution and platform_req.min_resolution:
                width, height = variant.resolution
                min_width, min_height = platform_req.min_resolution
                if width < min_width or height < min_height:
                    return False
            
            # Check duration
            if (variant.duration and platform_req.max_duration and 
                variant.duration > platform_req.max_duration):
                return False
            
            # Check required metadata
            for required_field in platform_req.required_metadata:
                if required_field not in variant.metadata:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating platform requirements: {e}")
            return False
    
    # Public API methods
    async def get_optimization_result(self, request_id: str) -> Optional[OptimizationResult]:
        """Get optimization result by request ID."""
        return self.optimization_results.get(request_id)
    
    async def get_optimization_status(self, request_id: str) -> OptimizationStatus:
        """Get optimization status."""
        result = self.optimization_results.get(request_id)
        return result.status if result else OptimizationStatus.FAILED
    
    async def cancel_optimization(self, request_id: str) -> bool:
        """Cancel ongoing optimization."""
        try:
            if request_id in self.processing_queue:
                self.processing_queue.remove(request_id)
            
            if request_id in self.optimization_results:
                result = self.optimization_results[request_id]
                result.status = OptimizationStatus.CANCELLED
                result.completed_at = datetime.now()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling optimization: {e}")
            return False
    
    async def get_platform_requirements(self, platform: PlatformType) -> Optional[PlatformRequirements]:
        """Get requirements for specific platform."""
        return self.platform_requirements.get(platform)
    
    async def estimate_optimization_time(self, request: OptimizationRequest) -> float:
        """Estimate optimization processing time."""
        # Base time per platform
        base_time_per_platform = 30.0  # seconds
        
        # Additional time per optimization type
        optimization_times = {
            OptimizationType.FORMAT_CONVERSION: 10.0,
            OptimizationType.RESOLUTION_SCALING: 15.0,
            OptimizationType.COMPRESSION: 5.0,
            OptimizationType.QUALITY_IMPROVEMENT: 20.0,
            OptimizationType.AUDIO_ENHANCEMENT: 10.0,
            OptimizationType.THUMBNAIL_GENERATION: 5.0,
            OptimizationType.SUBTITLE_GENERATION: 30.0
        }
        
        total_time = len(request.target_platforms) * base_time_per_platform
        
        for optimization in request.optimization_types:
            total_time += optimization_times.get(optimization, 5.0)
        
        return total_time
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics."""
        total_requests = len(self.optimization_requests)
        total_results = len(self.optimization_results)
        
        if total_results == 0:
            return {
                "total_optimization_requests": total_requests,
                "total_completed": 0,
                "success_rate": 0.0,
                "average_processing_time": 0.0,
                "platforms_supported": len(self.platform_requirements),
                "optimization_types_available": len(self.optimization_processors)
            }
        
        # Calculate success rate
        successful = len([r for r in self.optimization_results.values() 
                         if r.status == OptimizationStatus.COMPLETED])
        success_rate = (successful / total_results) * 100
        
        # Calculate average processing time
        processing_times = [r.processing_time for r in self.optimization_results.values() 
                           if r.processing_time > 0]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        # Platform distribution
        platform_dist = defaultdict(int)
        for result in self.optimization_results.values():
            for variant in result.variants:
                platform_dist[variant.platform.value] += 1
        
        return {
            "total_optimization_requests": total_requests,
            "total_completed": total_results,
            "success_rate": success_rate,
            "average_processing_time": avg_processing_time,
            "platforms_supported": len(self.platform_requirements),
            "optimization_types_available": len(self.optimization_processors),
            "queue_size": len(self.processing_queue),
            "platform_distribution": dict(platform_dist),
            "format_converters": len(self.format_converters),
            "quality_enhancers": len(self.quality_enhancers)
        }


# Global service instance
_optimization_service_instance = None

def get_content_optimization_service() -> ContentOptimizationService:
    """Get singleton instance of ContentOptimizationService."""
    global _optimization_service_instance
    if _optimization_service_instance is None:
        _optimization_service_instance = ContentOptimizationService()
    return _optimization_service_instance


# Example usage and testing
async def example_usage() -> None:
    """Example usage of Content Optimization Service."""
    service = get_content_optimization_service()
    
    # Create optimization request
    request = OptimizationRequest(
        content_id="content_video_123",
        source_url="https://example.com/source_video.mp4",
        content_type=ContentType.VIDEO,
        target_platforms=[
            PlatformType.YOUTUBE,
            PlatformType.INSTAGRAM,
            PlatformType.TIKTOK
        ],
        optimization_types=[
            OptimizationType.FORMAT_CONVERSION,
            OptimizationType.RESOLUTION_SCALING,
            OptimizationType.COMPRESSION,
            OptimizationType.THUMBNAIL_GENERATION
        ],
        settings=OptimizationSettings(
            target_quality="high",
            compression_level="balanced",
            generate_thumbnails=True,
            enhance_audio=True,
            color_enhancement=True
        ),
        metadata={
            "title": "Amazing Tutorial on AI Development",
            "description": "Learn how to build AI applications from scratch"
        }
    )
    
    # Start optimization
    request_id = await service.optimize_content(request)
    print(f"Started optimization: {request_id}")
    
    # Estimate processing time
    estimated_time = await service.estimate_optimization_time(request)
    print(f"Estimated processing time: {estimated_time:.1f} seconds")
    
    # Wait for completion (in real scenario, would poll status)
    await asyncio.sleep(2)
    
    # Get result
    result = await service.get_optimization_result(request_id)
    if result:
        print(f"Optimization Status: {result.status}")
        print(f"Processing Time: {result.processing_time:.2f}s")
        print(f"Variants Created: {len(result.variants)}")
        print(f"Average Quality Score: {result.average_quality_score:.2f}")
        print(f"Size Reduction: {result.total_size_reduction:.1f}%")
        
        for variant in result.variants:
            print(f"  {variant.platform}: {variant.format} "
                  f"({variant.resolution[0]}x{variant.resolution[1]}) "
                  f"- {variant.file_size // (1024*1024)}MB")
    
    # Get platform requirements
    youtube_req = await service.get_platform_requirements(PlatformType.YOUTUBE)
    if youtube_req:
        print(f"YouTube max file size: {youtube_req.max_file_size // (1024*1024*1024)}GB")
        print(f"YouTube supported formats: {youtube_req.supported_formats}")
    
    # Get service metrics
    metrics = service.get_service_metrics()
    print(f"Service metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())