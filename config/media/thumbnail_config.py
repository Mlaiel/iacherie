#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Thumbnail Configuration Module
========================================

Enterprise-grade thumbnail generation configuration for the Ainflue platform.
Comprehensive thumbnail creation with AI-powered smart cropping, adaptive sizing,
multi-format support, and intelligent content analysis for optimal preview generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib

class ThumbnailType(str, Enum):
    """Thumbnail types"""
    STATIC = "static"                 # Static image thumbnail
    ANIMATED = "animated"             # Animated GIF/WebP
    VIDEO_POSTER = "video_poster"     # Video poster frame
    SPRITE_SHEET = "sprite_sheet"     # Sprite sheet for scrubbing
    PROGRESSIVE = "progressive"       # Progressive loading thumbnails
    SMART_CROP = "smart_crop"         # AI-powered smart cropping
    COLLAGE = "collage"               # Multi-frame collage
    PREVIEW_GRID = "preview_grid"     # Grid of preview frames

class ThumbnailSize(str, Enum):
    """Standard thumbnail sizes"""
    MICRO = "micro"           # 32x32 - Icons
    TINY = "tiny"             # 64x64 - Small icons
    SMALL = "small"           # 128x128 - List items
    MEDIUM = "medium"         # 256x256 - Cards
    LARGE = "large"           # 512x512 - Featured content
    XLARGE = "xlarge"         # 1024x1024 - Hero images
    CUSTOM = "custom"         # Custom dimensions

class CropStrategy(str, Enum):
    """Cropping strategies"""
    CENTER = "center"                 # Center crop
    SMART = "smart"                   # AI-powered smart crop
    FACE_DETECTION = "face_detection" # Focus on detected faces
    OBJECT_DETECTION = "object_detection"  # Focus on detected objects
    ENTROPY = "entropy"               # High entropy (detail) areas
    ATTENTION = "attention"           # Visual attention modeling
    MANUAL = "manual"                 # Manual crop coordinates
    ASPECT_AWARE = "aspect_aware"     # Aspect ratio aware cropping

class OutputFormat(str, Enum):
    """Output formats for thumbnails"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    AVIF = "avif"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    SVG = "svg"

class Quality(str, Enum):
    """Quality presets"""
    LOW = "low"           # 50% quality, small file size
    MEDIUM = "medium"     # 75% quality, balanced
    HIGH = "high"         # 90% quality, large file size
    LOSSLESS = "lossless" # 100% quality, largest file size
    ADAPTIVE = "adaptive" # Quality based on content analysis

class ProcessingPriority(str, Enum):
    """Processing priority levels"""
    LOW = "low"           # Background processing
    NORMAL = "normal"     # Standard processing
    HIGH = "high"         # Priority processing
    URGENT = "urgent"     # Immediate processing
    REALTIME = "realtime" # Real-time processing

@dataclass
class ThumbnailDimension:
    """Thumbnail dimension specification"""
    width: int
    height: int
    aspect_ratio: Optional[str] = None  # "16:9", "4:3", "1:1", etc.
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    
    def __post_init__(self):
        """Calculate aspect ratio if not provided"""
        if not self.aspect_ratio and self.width > 0 and self.height > 0:
            from math import gcd
            ratio_gcd = gcd(self.width, self.height)
            self.aspect_ratio = f"{self.width // ratio_gcd}:{self.height // ratio_gcd}"
    
    def get_scaled_dimensions(self, original_width: int, original_height: int, 
                             fit_strategy: str = "cover") -> Tuple[int, int]:
        """Get scaled dimensions based on fit strategy"""
        
        if fit_strategy == "cover":
            # Scale to cover the entire thumbnail area (may crop)
            scale_w = self.width / original_width
            scale_h = self.height / original_height
            scale = max(scale_w, scale_h)
            
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
        elif fit_strategy == "contain":
            # Scale to fit within thumbnail area (no cropping)
            scale_w = self.width / original_width
            scale_h = self.height / original_height
            scale = min(scale_w, scale_h)
            
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
        elif fit_strategy == "stretch":
            # Stretch to exact dimensions (may distort)
            new_width = self.width
            new_height = self.height
            
        else:  # exact
            new_width = self.width
            new_height = self.height
        
        return new_width, new_height
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "width": self.width,
            "height": self.height,
            "aspect_ratio": self.aspect_ratio,
            "max_width": self.max_width,
            "max_height": self.max_height,
            "min_width": self.min_width,
            "min_height": self.min_height
        }

@dataclass
class ThumbnailTemplate:
    """Thumbnail generation template"""
    template_id: str
    name: str
    description: str
    thumbnail_type: ThumbnailType
    
    # Output specifications
    dimensions: ThumbnailDimension
    output_format: OutputFormat = OutputFormat.WEBP
    quality: Quality = Quality.MEDIUM
    
    # Processing settings
    crop_strategy: CropStrategy = CropStrategy.SMART
    fit_strategy: str = "cover"  # cover, contain, stretch, exact
    upscale_allowed: bool = False
    downscale_quality: str = "high"  # high, medium, low
    
    # AI enhancement
    ai_enhancement: bool = False
    face_detection: bool = False
    object_detection: bool = False
    scene_analysis: bool = False
    content_aware_crop: bool = True
    
    # Animation settings (for animated thumbnails)
    animation_duration: float = 3.0  # seconds
    frame_rate: int = 10  # fps
    loop_count: int = 0  # 0 = infinite
    
    # Sprite sheet settings
    sprite_columns: int = 10
    sprite_rows: int = 10
    sprite_interval: float = 1.0  # seconds between frames
    
    # Filters and effects
    sharpen: bool = False
    sharpen_amount: float = 0.5
    contrast_enhance: bool = False
    contrast_amount: float = 0.2
    saturation_enhance: bool = False
    saturation_amount: float = 0.1
    
    # Overlay and branding
    overlay_enabled: bool = False
    overlay_image: str = ""
    overlay_position: str = "bottom-right"  # top-left, top-right, bottom-left, bottom-right, center
    overlay_opacity: float = 0.8
    
    # Watermark
    watermark_enabled: bool = False
    watermark_text: str = ""
    watermark_position: str = "bottom-right"
    watermark_opacity: float = 0.5
    watermark_size: int = 12
    
    # Performance
    processing_priority: ProcessingPriority = ProcessingPriority.NORMAL
    cache_enabled: bool = True
    cache_ttl: int = 86400  # 24 hours
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    
    def get_quality_value(self) -> int:
        """Get numeric quality value"""
        quality_map = {
            Quality.LOW: 50,
            Quality.MEDIUM: 75,
            Quality.HIGH: 90,
            Quality.LOSSLESS: 100,
            Quality.ADAPTIVE: 85  # Default for adaptive
        }
        return quality_map.get(self.quality, 75)
    
    def supports_animation(self) -> bool:
        """Check if template supports animation"""
        return (self.thumbnail_type == ThumbnailType.ANIMATED or 
                self.output_format in [OutputFormat.GIF, OutputFormat.WEBP])
    
    def calculate_processing_cost(self, source_width: int, source_height: int) -> float:
        """Calculate estimated processing cost"""
        
        # Base cost factors
        source_pixels = source_width * source_height
        target_pixels = self.dimensions.width * self.dimensions.height
        
        # Base cost per megapixel
        base_cost = (source_pixels / 1000000) * 0.001  # $0.001 per megapixel
        
        # Processing complexity multipliers
        complexity_multiplier = 1.0
        
        if self.ai_enhancement:
            complexity_multiplier += 0.5
        
        if self.face_detection or self.object_detection:
            complexity_multiplier += 0.3
        
        if self.scene_analysis:
            complexity_multiplier += 0.2
        
        if self.thumbnail_type == ThumbnailType.ANIMATED:
            complexity_multiplier += 0.4
        
        if self.thumbnail_type == ThumbnailType.SPRITE_SHEET:
            complexity_multiplier += 0.6
        
        # Quality multiplier
        quality_multiplier = {
            Quality.LOW: 0.8,
            Quality.MEDIUM: 1.0,
            Quality.HIGH: 1.2,
            Quality.LOSSLESS: 1.5,
            Quality.ADAPTIVE: 1.1
        }.get(self.quality, 1.0)
        
        total_cost = base_cost * complexity_multiplier * quality_multiplier
        
        return round(total_cost, 6)
    
    def get_cache_key(self, source_file: str) -> str:
        """Generate cache key for thumbnail"""
        
        # Create unique identifier based on template and source
        template_hash = hashlib.md5(
            f"{self.template_id}:{self.dimensions.width}x{self.dimensions.height}:"
            f"{self.output_format.value}:{self.quality.value}:{self.crop_strategy.value}"
            .encode()
        ).hexdigest()[:16]
        
        source_hash = hashlib.md5(source_file.encode()).hexdigest()[:16]
        
        return f"thumb_{template_hash}_{source_hash}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "thumbnail_type": self.thumbnail_type.value,
            "dimensions": self.dimensions.to_dict(),
            "output_format": self.output_format.value,
            "quality": self.quality.value,
            "crop_strategy": self.crop_strategy.value,
            "fit_strategy": self.fit_strategy,
            "upscale_allowed": self.upscale_allowed,
            "downscale_quality": self.downscale_quality,
            "ai_enhancement": self.ai_enhancement,
            "face_detection": self.face_detection,
            "object_detection": self.object_detection,
            "scene_analysis": self.scene_analysis,
            "content_aware_crop": self.content_aware_crop,
            "animation_duration": self.animation_duration,
            "frame_rate": self.frame_rate,
            "loop_count": self.loop_count,
            "sprite_columns": self.sprite_columns,
            "sprite_rows": self.sprite_rows,
            "sprite_interval": self.sprite_interval,
            "sharpen": self.sharpen,
            "sharpen_amount": self.sharpen_amount,
            "contrast_enhance": self.contrast_enhance,
            "contrast_amount": self.contrast_amount,
            "saturation_enhance": self.saturation_enhance,
            "saturation_amount": self.saturation_amount,
            "overlay_enabled": self.overlay_enabled,
            "overlay_image": self.overlay_image,
            "overlay_position": self.overlay_position,
            "overlay_opacity": self.overlay_opacity,
            "watermark_enabled": self.watermark_enabled,
            "watermark_text": self.watermark_text,
            "watermark_position": self.watermark_position,
            "watermark_opacity": self.watermark_opacity,
            "watermark_size": self.watermark_size,
            "processing_priority": self.processing_priority.value,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "created_date": self.created_date.isoformat(),
            "enabled": self.enabled
        }

@dataclass
class ThumbnailJob:
    """Thumbnail generation job"""
    job_id: str
    source_file: str
    template_id: str
    
    # Job configuration
    output_path: str = ""
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    # Processing information
    status: str = "pending"  # pending, processing, completed, failed
    progress: float = 0.0  # 0.0 to 1.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: float = 0.0  # seconds
    
    # Results
    output_files: List[str] = field(default_factory=list)
    file_sizes: Dict[str, int] = field(default_factory=dict)
    processing_cost: float = 0.0
    
    # Error handling
    error_message: str = ""
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    
    def start_processing(self):
        """Mark job as started"""
        self.status = "processing"
        self.started_at = datetime.now()
        self.progress = 0.0
    
    def update_progress(self, progress: float):
        """Update job progress"""
        self.progress = max(0.0, min(1.0, progress))
    
    def complete_processing(self, output_files: List[str], file_sizes: Dict[str, int], 
                           processing_cost: float = 0.0):
        """Mark job as completed"""
        self.status = "completed"
        self.completed_at = datetime.now()
        self.progress = 1.0
        self.output_files = output_files
        self.file_sizes = file_sizes
        self.processing_cost = processing_cost
        
        if self.started_at:
            self.processing_time = (self.completed_at - self.started_at).total_seconds()
    
    def fail_processing(self, error_message: str):
        """Mark job as failed"""
        self.status = "failed"
        self.completed_at = datetime.now()
        self.error_message = error_message
        
        if self.started_at:
            self.processing_time = (self.completed_at - self.started_at).total_seconds()
    
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.status == "failed" and self.retry_count < self.max_retries
    
    def retry(self):
        """Retry failed job"""
        if self.can_retry():
            self.retry_count += 1
            self.status = "pending"
            self.progress = 0.0
            self.error_message = ""
            self.started_at = None
            self.completed_at = None
    
    def get_processing_duration(self) -> Optional[timedelta]:
        """Get processing duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "source_file": self.source_file,
            "template_id": self.template_id,
            "output_path": self.output_path,
            "custom_params": self.custom_params,
            "status": self.status,
            "progress": self.progress,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time": self.processing_time,
            "output_files": self.output_files,
            "file_sizes": self.file_sizes,
            "processing_cost": self.processing_cost,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_date": self.created_date.isoformat(),
            "priority": self.priority.value
        }

class ThumbnailConfiguration:
    """Main thumbnail configuration manager"""
    
    def __init__(self):
        """Initialize thumbnail configuration"""
        # Data storage
        self.templates: Dict[str, ThumbnailTemplate] = {}
        self.jobs: Dict[str, ThumbnailJob] = {}
        
        # Global settings
        self.thumbnail_enabled = True
        self.auto_generation = True
        self.ai_enhancement = True
        self.batch_processing = True
        
        # Processing settings
        self.processing_settings = {
            "max_concurrent_jobs": 10,
            "max_queue_size": 1000,
            "default_timeout": 300,  # 5 minutes
            "chunk_size": 1024 * 1024,  # 1MB
            "temp_directory": "/tmp/thumbnails",
            "output_directory": "/var/thumbnails",
            "enable_gpu_acceleration": True,
            "memory_limit_mb": 2048
        }
        
        # Quality settings
        self.quality_settings = {
            "default_quality": "medium",
            "progressive_jpeg": True,
            "optimize_png": True,
            "webp_quality": 85,
            "avif_quality": 80,
            "gif_optimization": True,
            "strip_metadata": True,
            "color_profile": "srgb"
        }
        
        # AI settings
        self.ai_settings = {
            "face_detection_enabled": True,
            "object_detection_enabled": True,
            "scene_analysis_enabled": True,
            "content_aware_cropping": True,
            "smart_crop_model": "latest",
            "confidence_threshold": 0.7,
            "max_faces_detect": 10,
            "max_objects_detect": 20
        }
        
        # Cache settings
        self.cache_settings = {
            "cache_enabled": True,
            "cache_driver": "redis",  # redis, memcache, file
            "cache_ttl": 86400,  # 24 hours
            "cache_size_limit": "10GB",
            "cache_cleanup_interval": 3600,  # 1 hour
            "preemptive_regeneration": True
        }
        
        # Performance settings
        self.performance_settings = {
            "lazy_loading": True,
            "progressive_enhancement": True,
            "adaptive_quality": True,
            "client_hints": True,
            "responsive_images": True,
            "webp_fallback": True,
            "avif_fallback": True
        }
        
        # Initialize default templates
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default thumbnail templates"""
        
        # Micro thumbnails for icons
        micro_template = ThumbnailTemplate(
            template_id="micro",
            name="Micro Thumbnail",
            description="32x32 thumbnails for icons and small UI elements",
            thumbnail_type=ThumbnailType.STATIC,
            dimensions=ThumbnailDimension(32, 32),
            output_format=OutputFormat.WEBP,
            quality=Quality.MEDIUM,
            crop_strategy=CropStrategy.SMART,
            ai_enhancement=True,
            face_detection=True
        )
        
        # Small thumbnails for lists
        small_template = ThumbnailTemplate(
            template_id="small",
            name="Small Thumbnail",
            description="128x128 thumbnails for list items and cards",
            thumbnail_type=ThumbnailType.STATIC,
            dimensions=ThumbnailDimension(128, 128),
            output_format=OutputFormat.WEBP,
            quality=Quality.MEDIUM,
            crop_strategy=CropStrategy.SMART,
            ai_enhancement=True,
            face_detection=True,
            object_detection=True
        )
        
        # Medium thumbnails for cards
        medium_template = ThumbnailTemplate(
            template_id="medium",
            name="Medium Thumbnail",
            description="256x256 thumbnails for content cards",
            thumbnail_type=ThumbnailType.STATIC,
            dimensions=ThumbnailDimension(256, 256),
            output_format=OutputFormat.WEBP,
            quality=Quality.HIGH,
            crop_strategy=CropStrategy.SMART,
            ai_enhancement=True,
            face_detection=True,
            object_detection=True,
            scene_analysis=True,
            sharpen=True,
            contrast_enhance=True
        )
        
        # Large thumbnails for featured content
        large_template = ThumbnailTemplate(
            template_id="large",
            name="Large Thumbnail",
            description="512x512 thumbnails for featured content",
            thumbnail_type=ThumbnailType.STATIC,
            dimensions=ThumbnailDimension(512, 512),
            output_format=OutputFormat.WEBP,
            quality=Quality.HIGH,
            crop_strategy=CropStrategy.SMART,
            ai_enhancement=True,
            face_detection=True,
            object_detection=True,
            scene_analysis=True,
            content_aware_crop=True,
            sharpen=True,
            contrast_enhance=True,
            saturation_enhance=True
        )
        
        # Video poster thumbnails
        video_poster_template = ThumbnailTemplate(
            template_id="video_poster",
            name="Video Poster",
            description="Video poster frames with 16:9 aspect ratio",
            thumbnail_type=ThumbnailType.VIDEO_POSTER,
            dimensions=ThumbnailDimension(1280, 720, "16:9"),
            output_format=OutputFormat.WEBP,
            quality=Quality.HIGH,
            crop_strategy=CropStrategy.SMART,
            fit_strategy="cover",
            ai_enhancement=True,
            scene_analysis=True,
            content_aware_crop=True,
            sharpen=True,
            overlay_enabled=True,
            overlay_position="bottom-right"
        )
        
        # Animated thumbnails
        animated_template = ThumbnailTemplate(
            template_id="animated",
            name="Animated Thumbnail",
            description="Animated thumbnails for video previews",
            thumbnail_type=ThumbnailType.ANIMATED,
            dimensions=ThumbnailDimension(320, 240),
            output_format=OutputFormat.WEBP,
            quality=Quality.MEDIUM,
            crop_strategy=CropStrategy.CENTER,
            animation_duration=3.0,
            frame_rate=10,
            loop_count=0,
            processing_priority=ProcessingPriority.HIGH
        )
        
        # Sprite sheet for video scrubbing
        sprite_template = ThumbnailTemplate(
            template_id="sprite_sheet",
            name="Video Sprite Sheet",
            description="Sprite sheet for video timeline scrubbing",
            thumbnail_type=ThumbnailType.SPRITE_SHEET,
            dimensions=ThumbnailDimension(1600, 900),  # 10x10 grid of 160x90 frames
            output_format=OutputFormat.JPEG,
            quality=Quality.MEDIUM,
            crop_strategy=CropStrategy.CENTER,
            sprite_columns=10,
            sprite_rows=10,
            sprite_interval=1.0,  # One frame per second
            processing_priority=ProcessingPriority.LOW
        )
        
        # Smart crop portrait
        portrait_template = ThumbnailTemplate(
            template_id="portrait",
            name="Portrait Thumbnail",
            description="Portrait-oriented thumbnails with face detection",
            thumbnail_type=ThumbnailType.SMART_CROP,
            dimensions=ThumbnailDimension(320, 480, "2:3"),
            output_format=OutputFormat.WEBP,
            quality=Quality.HIGH,
            crop_strategy=CropStrategy.FACE_DETECTION,
            ai_enhancement=True,
            face_detection=True,
            content_aware_crop=True,
            sharpen=True
        )
        
        # Social media optimized
        social_template = ThumbnailTemplate(
            template_id="social",
            name="Social Media Thumbnail",
            description="Square thumbnails optimized for social media",
            thumbnail_type=ThumbnailType.STATIC,
            dimensions=ThumbnailDimension(400, 400, "1:1"),
            output_format=OutputFormat.WEBP,
            quality=Quality.HIGH,
            crop_strategy=CropStrategy.SMART,
            ai_enhancement=True,
            face_detection=True,
            object_detection=True,
            sharpen=True,
            contrast_enhance=True,
            saturation_enhance=True,
            watermark_enabled=True,
            watermark_position="bottom-right",
            watermark_opacity=0.3
        )
        
        # Store templates
        templates = [
            micro_template, small_template, medium_template, large_template,
            video_poster_template, animated_template, sprite_template,
            portrait_template, social_template
        ]
        
        for template in templates:
            self.templates[template.template_id] = template
    
    def create_thumbnail_template(self, template_data: Dict[str, Any]) -> ThumbnailTemplate:
        """Create new thumbnail template"""
        
        # Create dimensions
        dim_data = template_data.get("dimensions", {})
        dimensions = ThumbnailDimension(
            width=dim_data.get("width", 256),
            height=dim_data.get("height", 256),
            aspect_ratio=dim_data.get("aspect_ratio")
        )
        
        template = ThumbnailTemplate(
            template_id=template_data.get("template_id", f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=template_data["name"],
            description=template_data.get("description", ""),
            thumbnail_type=ThumbnailType(template_data.get("thumbnail_type", "static")),
            dimensions=dimensions,
            output_format=OutputFormat(template_data.get("output_format", "webp")),
            quality=Quality(template_data.get("quality", "medium")),
            crop_strategy=CropStrategy(template_data.get("crop_strategy", "smart")),
            ai_enhancement=template_data.get("ai_enhancement", False),
            face_detection=template_data.get("face_detection", False),
            object_detection=template_data.get("object_detection", False),
            processing_priority=ProcessingPriority(template_data.get("processing_priority", "normal"))
        )
        
        self.templates[template.template_id] = template
        return template
    
    def create_thumbnail_job(self, job_data: Dict[str, Any]) -> ThumbnailJob:
        """Create new thumbnail generation job"""
        
        job = ThumbnailJob(
            job_id=job_data.get("job_id", f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            source_file=job_data["source_file"],
            template_id=job_data["template_id"],
            output_path=job_data.get("output_path", ""),
            custom_params=job_data.get("custom_params", {}),
            priority=ProcessingPriority(job_data.get("priority", "normal"))
        )
        
        self.jobs[job.job_id] = job
        return job
    
    async def generate_thumbnail(self, source_file: str, template_id: str,
                                output_path: str = "", custom_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate thumbnail"""
        
        result = {
            "success": False,
            "job_id": None,
            "output_files": [],
            "processing_time": 0.0,
            "processing_cost": 0.0,
            "error": None
        }
        
        try:
            if template_id not in self.templates:
                result["error"] = f"Template {template_id} not found"
                return result
            
            template = self.templates[template_id]
            
            # Create job
            job_data = {
                "source_file": source_file,
                "template_id": template_id,
                "output_path": output_path,
                "custom_params": custom_params or {}
            }
            
            job = self.create_thumbnail_job(job_data)
            result["job_id"] = job.job_id
            
            # Start processing
            job.start_processing()
            
            # Simulate thumbnail generation
            import time
            import random
            
            processing_start = time.time()
            
            # Simulate processing steps
            steps = [
                ("Loading source file", 0.1),
                ("Analyzing content", 0.2),
                ("Applying AI enhancement", 0.4),
                ("Cropping and resizing", 0.6),
                ("Applying filters", 0.8),
                ("Encoding output", 1.0)
            ]
            
            for step_name, progress in steps:
                job.update_progress(progress)
                time.sleep(random.uniform(0.1, 0.3))  # Simulate processing time
            
            # Generate output files
            base_name = os.path.splitext(os.path.basename(source_file))[0]
            output_extension = template.output_format.value
            
            if not output_path:
                output_path = f"/var/thumbnails/{template_id}"
                os.makedirs(output_path, exist_ok=True)
            
            output_file = os.path.join(output_path, f"{base_name}_{template_id}.{output_extension}")
            
            # Simulate file creation and get size
            output_files = [output_file]
            file_sizes = {output_file: random.randint(5000, 50000)}  # Random file size
            
            # Calculate processing cost
            processing_cost = template.calculate_processing_cost(1920, 1080)  # Assume HD source
            
            processing_end = time.time()
            processing_time = processing_end - processing_start
            
            # Complete job
            job.complete_processing(output_files, file_sizes, processing_cost)
            
            result.update({
                "success": True,
                "output_files": output_files,
                "processing_time": processing_time,
                "processing_cost": processing_cost
            })
            
        except Exception as e:
            result["error"] = str(e)
            if result["job_id"] and result["job_id"] in self.jobs:
                self.jobs[result["job_id"]].fail_processing(str(e))
        
        return result
    
    def generate_multiple_thumbnails(self, source_file: str, template_ids: List[str],
                                   output_path: str = "") -> Dict[str, Any]:
        """Generate multiple thumbnails from different templates"""
        
        result = {
            "success": False,
            "job_ids": [],
            "completed_jobs": 0,
            "failed_jobs": 0,
            "total_processing_time": 0.0,
            "total_processing_cost": 0.0,
            "results": {},
            "error": None
        }
        
        try:
            for template_id in template_ids:
                if template_id in self.templates:
                    job_result = await self.generate_thumbnail(source_file, template_id, output_path)
                    
                    result["job_ids"].append(job_result.get("job_id"))
                    result["results"][template_id] = job_result
                    
                    if job_result["success"]:
                        result["completed_jobs"] += 1
                        result["total_processing_time"] += job_result["processing_time"]
                        result["total_processing_cost"] += job_result["processing_cost"]
                    else:
                        result["failed_jobs"] += 1
                
                else:
                    result["results"][template_id] = {
                        "success": False,
                        "error": f"Template {template_id} not found"
                    }
                    result["failed_jobs"] += 1
            
            result["success"] = result["completed_jobs"] > 0
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get thumbnail job status"""
        
        if job_id not in self.jobs:
            return {"error": f"Job {job_id} not found"}
        
        job = self.jobs[job_id]
        return job.to_dict()
    
    def get_processing_queue(self) -> Dict[str, Any]:
        """Get processing queue status"""
        
        queue_stats = {
            "total_jobs": len(self.jobs),
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "queue_length": 0,
            "average_processing_time": 0.0,
            "total_processing_cost": 0.0
        }
        
        processing_times = []
        total_cost = 0.0
        
        for job in self.jobs.values():
            queue_stats[job.status] += 1
            
            if job.status == "pending":
                queue_stats["queue_length"] += 1
            
            if job.processing_time > 0:
                processing_times.append(job.processing_time)
            
            total_cost += job.processing_cost
        
        if processing_times:
            queue_stats["average_processing_time"] = sum(processing_times) / len(processing_times)
        
        queue_stats["total_processing_cost"] = total_cost
        
        return queue_stats
    
    def cleanup_completed_jobs(self, older_than_hours: int = 24) -> int:
        """Clean up completed jobs older than specified hours"""
        
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        jobs_to_remove = []
        
        for job_id, job in self.jobs.items():
            if (job.status in ["completed", "failed"] and 
                job.completed_at and 
                job.completed_at < cutoff_time):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
        
        return len(jobs_to_remove)
    
    def get_template_performance(self, template_id: str) -> Dict[str, Any]:
        """Get performance metrics for a template"""
        
        if template_id not in self.templates:
            return {"error": f"Template {template_id} not found"}
        
        template_jobs = [job for job in self.jobs.values() if job.template_id == template_id]
        
        if not template_jobs:
            return {"error": "No jobs found for this template"}
        
        # Calculate metrics
        total_jobs = len(template_jobs)
        completed_jobs = len([j for j in template_jobs if j.status == "completed"])
        failed_jobs = len([j for j in template_jobs if j.status == "failed"])
        
        processing_times = [j.processing_time for j in template_jobs if j.processing_time > 0]
        costs = [j.processing_cost for j in template_jobs if j.processing_cost > 0]
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        total_cost = sum(costs)
        
        return {
            "template_id": template_id,
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            "average_processing_time": avg_processing_time,
            "total_processing_cost": total_cost,
            "average_cost_per_job": total_cost / total_jobs if total_jobs > 0 else 0
        }
    
    def get_thumbnail_statistics(self) -> Dict[str, Any]:
        """Get thumbnail generation statistics"""
        
        stats = {
            "templates": {
                "total": len(self.templates),
                "enabled": len([t for t in self.templates.values() if t.enabled]),
                "by_type": {},
                "by_format": {}
            },
            "jobs": self.get_processing_queue(),
            "performance": {
                "total_processing_time": 0.0,
                "total_processing_cost": 0.0,
                "average_job_time": 0.0,
                "fastest_template": None,
                "slowest_template": None
            }
        }
        
        # Template statistics
        for template in self.templates.values():
            thumb_type = template.thumbnail_type.value
            output_format = template.output_format.value
            
            stats["templates"]["by_type"][thumb_type] = stats["templates"]["by_type"].get(thumb_type, 0) + 1
            stats["templates"]["by_format"][output_format] = stats["templates"]["by_format"].get(output_format, 0) + 1
        
        # Performance statistics
        all_processing_times = []
        all_costs = []
        template_avg_times = {}
        
        for job in self.jobs.values():
            if job.processing_time > 0:
                all_processing_times.append(job.processing_time)
                all_costs.append(job.processing_cost)
                
                template_id = job.template_id
                if template_id not in template_avg_times:
                    template_avg_times[template_id] = []
                template_avg_times[template_id].append(job.processing_time)
        
        if all_processing_times:
            stats["performance"]["total_processing_time"] = sum(all_processing_times)
            stats["performance"]["total_processing_cost"] = sum(all_costs)
            stats["performance"]["average_job_time"] = sum(all_processing_times) / len(all_processing_times)
            
            # Find fastest and slowest templates
            template_speeds = {}
            for template_id, times in template_avg_times.items():
                template_speeds[template_id] = sum(times) / len(times)
            
            if template_speeds:
                fastest = min(template_speeds.items(), key=lambda x: x[1])
                slowest = max(template_speeds.items(), key=lambda x: x[1])
                
                stats["performance"]["fastest_template"] = {"id": fastest[0], "avg_time": fastest[1]}
                stats["performance"]["slowest_template"] = {"id": slowest[0], "avg_time": slowest[1]}
        
        return stats
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete thumbnail configuration"""
        return {
            "thumbnail_statistics": self.get_thumbnail_statistics(),
            "templates": {template_id: template.to_dict() for template_id, template in self.templates.items()},
            "global_settings": {
                "thumbnail_enabled": self.thumbnail_enabled,
                "auto_generation": self.auto_generation,
                "ai_enhancement": self.ai_enhancement,
                "batch_processing": self.batch_processing
            },
            "processing_settings": self.processing_settings,
            "quality_settings": self.quality_settings,
            "ai_settings": self.ai_settings,
            "cache_settings": self.cache_settings,
            "performance_settings": self.performance_settings
        }

# Global thumbnail configuration instance
thumbnail_config = ThumbnailConfiguration()

# Export main classes
__all__ = [
    "ThumbnailConfiguration",
    "ThumbnailType",
    "ThumbnailSize",
    "CropStrategy",
    "OutputFormat",
    "Quality",
    "ProcessingPriority",
    "ThumbnailDimension",
    "ThumbnailTemplate",
    "ThumbnailJob",
    "thumbnail_config"
]
