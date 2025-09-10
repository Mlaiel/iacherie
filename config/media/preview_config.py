#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Preview Configuration Module
======================================

Enterprise-grade preview generation configuration for the Ainflue platform.
Comprehensive preview creation with adaptive streaming, multi-format support,
intelligent content analysis, and dynamic preview generation for optimal user experience.

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

class PreviewType(str, Enum):
    """Preview types"""
    VIDEO_PREVIEW = "video_preview"       # Short video previews
    AUDIO_PREVIEW = "audio_preview"       # Audio clip previews
    IMAGE_SLIDESHOW = "image_slideshow"   # Image slideshow previews
    DOCUMENT_PREVIEW = "document_preview" # Document page previews
    INTERACTIVE = "interactive"           # Interactive previews
    ANIMATED = "animated"                 # Animated previews
    STATIC = "static"                     # Static image previews
    LIVE_PREVIEW = "live_preview"         # Live streaming previews

class PreviewQuality(str, Enum):
    """Preview quality levels"""
    LOW = "low"           # 360p, low bitrate
    MEDIUM = "medium"     # 720p, medium bitrate
    HIGH = "high"         # 1080p, high bitrate
    ADAPTIVE = "adaptive" # Adaptive based on device/connection
    AUTO = "auto"         # Automatically determined

class PreviewDuration(str, Enum):
    """Standard preview durations"""
    MICRO = "micro"       # 5-10 seconds
    SHORT = "short"       # 15-30 seconds
    MEDIUM = "medium"     # 30-60 seconds
    LONG = "long"         # 60-120 seconds
    CUSTOM = "custom"     # Custom duration

class PreviewFormat(str, Enum):
    """Preview output formats"""
    MP4 = "mp4"
    WEBM = "webm"
    HLS = "hls"           # HTTP Live Streaming
    DASH = "dash"         # Dynamic Adaptive Streaming
    GIF = "gif"
    WEBP = "webp"
    JPEG = "jpeg"
    PNG = "png"
    PDF = "pdf"

class ContentAnalysisType(str, Enum):
    """Content analysis types for preview generation"""
    HIGHLIGHT_DETECTION = "highlight_detection"   # Detect interesting moments
    SCENE_DETECTION = "scene_detection"           # Detect scene changes
    FACE_DETECTION = "face_detection"             # Detect faces
    OBJECT_DETECTION = "object_detection"         # Detect objects
    ACTION_DETECTION = "action_detection"         # Detect action sequences
    AUDIO_ANALYSIS = "audio_analysis"             # Analyze audio content
    TEXT_EXTRACTION = "text_extraction"           # Extract text content
    EMOTION_ANALYSIS = "emotion_analysis"         # Analyze emotional content

class AdaptiveStrategy(str, Enum):
    """Adaptive preview strategies"""
    DEVICE_BASED = "device_based"         # Adapt based on device capabilities
    BANDWIDTH_BASED = "bandwidth_based"   # Adapt based on network speed
    USER_PREFERENCE = "user_preference"   # Adapt based on user settings
    CONTENT_BASED = "content_based"       # Adapt based on content type
    TIME_BASED = "time_based"             # Adapt based on time of day
    LOCATION_BASED = "location_based"     # Adapt based on geographic location

@dataclass
class PreviewSegment:
    """Preview segment definition"""
    segment_id: str
    start_time: float     # Start time in seconds
    duration: float       # Duration in seconds
    weight: float = 1.0   # Importance weight (0.0-1.0)
    segment_type: str = "auto"  # auto, intro, highlight, outro, transition
    
    # Content analysis
    scene_score: float = 0.0      # Scene interest score
    action_score: float = 0.0     # Action intensity score
    face_score: float = 0.0       # Face prominence score
    audio_score: float = 0.0      # Audio interest score
    
    # Technical metadata
    resolution: str = ""
    bitrate: int = 0
    frame_rate: float = 0.0
    
    def get_end_time(self) -> float:
        """Get segment end time"""
        return self.start_time + self.duration
    
    def get_total_score(self) -> float:
        """Calculate total interest score"""
        return (self.scene_score + self.action_score + 
                self.face_score + self.audio_score) * self.weight
    
    def overlaps_with(self, other: 'PreviewSegment') -> bool:
        """Check if this segment overlaps with another"""
        return (self.start_time < other.get_end_time() and 
                self.get_end_time() > other.start_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "segment_id": self.segment_id,
            "start_time": self.start_time,
            "duration": self.duration,
            "end_time": self.get_end_time(),
            "weight": self.weight,
            "segment_type": self.segment_type,
            "scene_score": self.scene_score,
            "action_score": self.action_score,
            "face_score": self.face_score,
            "audio_score": self.audio_score,
            "total_score": self.get_total_score(),
            "resolution": self.resolution,
            "bitrate": self.bitrate,
            "frame_rate": self.frame_rate
        }

@dataclass
class PreviewTemplate:
    """Preview generation template"""
    template_id: str
    name: str
    description: str
    preview_type: PreviewType
    
    # Duration settings
    target_duration: float = 30.0  # Target duration in seconds
    min_duration: float = 10.0
    max_duration: float = 120.0
    duration_strategy: PreviewDuration = PreviewDuration.SHORT
    
    # Quality settings
    quality: PreviewQuality = PreviewQuality.MEDIUM
    output_format: PreviewFormat = PreviewFormat.MP4
    resolution_width: int = 1280
    resolution_height: int = 720
    bitrate_kbps: int = 2000
    frame_rate: float = 30.0
    
    # Content analysis
    content_analysis: List[ContentAnalysisType] = field(default_factory=list)
    auto_highlight_detection: bool = True
    scene_change_threshold: float = 0.3
    minimum_segment_duration: float = 2.0
    
    # Segment selection
    max_segments: int = 5
    segment_min_gap: float = 1.0  # Minimum gap between segments
    prefer_intro: bool = True
    prefer_outro: bool = False
    include_transitions: bool = True
    
    # Adaptive settings
    adaptive_quality: bool = True
    adaptive_strategy: AdaptiveStrategy = AdaptiveStrategy.DEVICE_BASED
    fallback_quality: PreviewQuality = PreviewQuality.LOW
    
    # Enhancement
    auto_stabilization: bool = False
    color_correction: bool = True
    audio_normalization: bool = True
    noise_reduction: bool = False
    
    # Effects and overlays
    fade_in_duration: float = 0.5
    fade_out_duration: float = 0.5
    crossfade_duration: float = 0.3
    overlay_enabled: bool = False
    overlay_text: str = ""
    overlay_position: str = "bottom-center"
    
    # Branding
    watermark_enabled: bool = False
    watermark_position: str = "bottom-right"
    watermark_opacity: float = 0.5
    logo_overlay: bool = False
    
    # Performance
    gpu_acceleration: bool = True
    parallel_processing: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 86400  # 24 hours
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    priority: int = 5  # 1-10, higher = more important
    
    def get_resolution_tuple(self) -> Tuple[int, int]:
        """Get resolution as tuple"""
        return (self.resolution_width, self.resolution_height)
    
    def calculate_target_bitrate(self, quality_override: PreviewQuality = None) -> int:
        """Calculate target bitrate based on quality and resolution"""
        
        quality = quality_override or self.quality
        
        # Base bitrate per quality level (for 720p)
        base_bitrates = {
            PreviewQuality.LOW: 1000,      # 1 Mbps
            PreviewQuality.MEDIUM: 2500,   # 2.5 Mbps
            PreviewQuality.HIGH: 5000,     # 5 Mbps
            PreviewQuality.ADAPTIVE: 2500, # Default to medium
            PreviewQuality.AUTO: 2500      # Default to medium
        }
        
        base_bitrate = base_bitrates.get(quality, 2500)
        
        # Scale based on resolution (720p = baseline)
        resolution_factor = (self.resolution_width * self.resolution_height) / (1280 * 720)
        
        return int(base_bitrate * resolution_factor)
    
    def estimate_file_size(self, duration_seconds: float = None) -> int:
        """Estimate output file size in bytes"""
        
        duration = duration_seconds or self.target_duration
        bitrate = self.calculate_target_bitrate()
        
        # Convert bitrate to bytes per second and multiply by duration
        bytes_per_second = (bitrate * 1000) / 8  # Convert Kbps to bytes/second
        estimated_size = int(bytes_per_second * duration)
        
        return estimated_size
    
    def supports_adaptive_streaming(self) -> bool:
        """Check if template supports adaptive streaming"""
        return self.output_format in [PreviewFormat.HLS, PreviewFormat.DASH]
    
    def get_content_analysis_pipeline(self) -> List[str]:
        """Get content analysis pipeline steps"""
        
        pipeline = []
        
        if ContentAnalysisType.SCENE_DETECTION in self.content_analysis:
            pipeline.append("scene_detection")
        
        if ContentAnalysisType.HIGHLIGHT_DETECTION in self.content_analysis:
            pipeline.append("highlight_detection")
        
        if ContentAnalysisType.FACE_DETECTION in self.content_analysis:
            pipeline.append("face_detection")
        
        if ContentAnalysisType.OBJECT_DETECTION in self.content_analysis:
            pipeline.append("object_detection")
        
        if ContentAnalysisType.ACTION_DETECTION in self.content_analysis:
            pipeline.append("action_detection")
        
        if ContentAnalysisType.AUDIO_ANALYSIS in self.content_analysis:
            pipeline.append("audio_analysis")
        
        if ContentAnalysisType.EMOTION_ANALYSIS in self.content_analysis:
            pipeline.append("emotion_analysis")
        
        return pipeline
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "preview_type": self.preview_type.value,
            "target_duration": self.target_duration,
            "min_duration": self.min_duration,
            "max_duration": self.max_duration,
            "duration_strategy": self.duration_strategy.value,
            "quality": self.quality.value,
            "output_format": self.output_format.value,
            "resolution_width": self.resolution_width,
            "resolution_height": self.resolution_height,
            "bitrate_kbps": self.bitrate_kbps,
            "frame_rate": self.frame_rate,
            "content_analysis": [ca.value for ca in self.content_analysis],
            "auto_highlight_detection": self.auto_highlight_detection,
            "scene_change_threshold": self.scene_change_threshold,
            "minimum_segment_duration": self.minimum_segment_duration,
            "max_segments": self.max_segments,
            "segment_min_gap": self.segment_min_gap,
            "prefer_intro": self.prefer_intro,
            "prefer_outro": self.prefer_outro,
            "include_transitions": self.include_transitions,
            "adaptive_quality": self.adaptive_quality,
            "adaptive_strategy": self.adaptive_strategy.value,
            "fallback_quality": self.fallback_quality.value,
            "auto_stabilization": self.auto_stabilization,
            "color_correction": self.color_correction,
            "audio_normalization": self.audio_normalization,
            "noise_reduction": self.noise_reduction,
            "fade_in_duration": self.fade_in_duration,
            "fade_out_duration": self.fade_out_duration,
            "crossfade_duration": self.crossfade_duration,
            "overlay_enabled": self.overlay_enabled,
            "overlay_text": self.overlay_text,
            "overlay_position": self.overlay_position,
            "watermark_enabled": self.watermark_enabled,
            "watermark_position": self.watermark_position,
            "watermark_opacity": self.watermark_opacity,
            "logo_overlay": self.logo_overlay,
            "gpu_acceleration": self.gpu_acceleration,
            "parallel_processing": self.parallel_processing,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "estimated_file_size": self.estimate_file_size(),
            "supports_adaptive": self.supports_adaptive_streaming(),
            "content_pipeline": self.get_content_analysis_pipeline(),
            "created_date": self.created_date.isoformat(),
            "enabled": self.enabled,
            "priority": self.priority
        }

@dataclass
class PreviewJob:
    """Preview generation job"""
    job_id: str
    source_file: str
    template_id: str
    
    # Job configuration
    output_path: str = ""
    custom_segments: List[PreviewSegment] = field(default_factory=list)
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    # Processing information
    status: str = "pending"  # pending, analyzing, generating, encoding, completed, failed
    progress: float = 0.0
    current_step: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Analysis results
    analyzed_segments: List[PreviewSegment] = field(default_factory=list)
    selected_segments: List[PreviewSegment] = field(default_factory=list)
    total_source_duration: float = 0.0
    
    # Output results
    output_files: List[str] = field(default_factory=list)
    preview_duration: float = 0.0
    file_sizes: Dict[str, int] = field(default_factory=dict)
    processing_cost: float = 0.0
    
    # Quality metrics
    analysis_confidence: float = 0.0
    segment_quality_scores: List[float] = field(default_factory=list)
    overall_quality_score: float = 0.0
    
    # Error handling
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    
    def start_processing(self):
        """Start preview generation"""
        self.status = "analyzing"
        self.started_at = datetime.now()
        self.progress = 0.0
        self.current_step = "Starting content analysis"
    
    def update_progress(self, progress: float, step: str = ""):
        """Update job progress"""
        self.progress = max(0.0, min(1.0, progress))
        if step:
            self.current_step = step
    
    def set_analysis_results(self, segments: List[PreviewSegment], 
                           source_duration: float, confidence: float):
        """Set content analysis results"""
        self.analyzed_segments = segments
        self.total_source_duration = source_duration
        self.analysis_confidence = confidence
        self.status = "generating"
        self.current_step = "Selecting optimal segments"
    
    def set_selected_segments(self, segments: List[PreviewSegment]):
        """Set selected segments for preview"""
        self.selected_segments = segments
        self.preview_duration = sum(seg.duration for seg in segments)
        self.status = "encoding"
        self.current_step = "Encoding preview video"
    
    def complete_processing(self, output_files: List[str], file_sizes: Dict[str, int],
                           quality_scores: List[float] = None, processing_cost: float = 0.0):
        """Complete preview generation"""
        self.status = "completed"
        self.completed_at = datetime.now()
        self.progress = 1.0
        self.current_step = "Completed"
        self.output_files = output_files
        self.file_sizes = file_sizes
        self.processing_cost = processing_cost
        
        if quality_scores:
            self.segment_quality_scores = quality_scores
            self.overall_quality_score = sum(quality_scores) / len(quality_scores)
    
    def fail_processing(self, error_message: str):
        """Mark job as failed"""
        self.status = "failed"
        self.completed_at = datetime.now()
        self.error_message = error_message
        self.current_step = f"Failed: {error_message}"
    
    def add_warning(self, warning: str):
        """Add warning message"""
        self.warnings.append(warning)
    
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.status == "failed" and self.retry_count < self.max_retries
    
    def retry(self):
        """Retry failed job"""
        if self.can_retry():
            self.retry_count += 1
            self.status = "pending"
            self.progress = 0.0
            self.current_step = ""
            self.error_message = ""
            self.warnings = []
            self.started_at = None
            self.completed_at = None
    
    def get_processing_duration(self) -> Optional[timedelta]:
        """Get processing duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    def get_compression_ratio(self) -> float:
        """Get compression ratio (preview vs source duration)"""
        if self.total_source_duration > 0:
            return self.preview_duration / self.total_source_duration
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "source_file": self.source_file,
            "template_id": self.template_id,
            "output_path": self.output_path,
            "custom_segments": [seg.to_dict() for seg in self.custom_segments],
            "custom_params": self.custom_params,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "analyzed_segments": [seg.to_dict() for seg in self.analyzed_segments],
            "selected_segments": [seg.to_dict() for seg in self.selected_segments],
            "total_source_duration": self.total_source_duration,
            "output_files": self.output_files,
            "preview_duration": self.preview_duration,
            "file_sizes": self.file_sizes,
            "processing_cost": self.processing_cost,
            "analysis_confidence": self.analysis_confidence,
            "segment_quality_scores": self.segment_quality_scores,
            "overall_quality_score": self.overall_quality_score,
            "compression_ratio": self.get_compression_ratio(),
            "error_message": self.error_message,
            "warnings": self.warnings,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "processing_duration": self.get_processing_duration().total_seconds() if self.get_processing_duration() else None,
            "created_date": self.created_date.isoformat()
        }

class PreviewConfiguration:
    """Main preview configuration manager"""
    
    def __init__(self):
        """Initialize preview configuration"""
        # Data storage
        self.templates: Dict[str, PreviewTemplate] = {}
        self.jobs: Dict[str, PreviewJob] = {}
        
        # Global settings
        self.preview_enabled = True
        self.auto_generation = True
        self.ai_analysis = True
        self.adaptive_streaming = True
        
        # Processing settings
        self.processing_settings = {
            "max_concurrent_jobs": 5,
            "max_queue_size": 500,
            "default_timeout": 900,  # 15 minutes
            "gpu_acceleration": True,
            "parallel_segments": True,
            "temp_directory": "/tmp/previews",
            "output_directory": "/var/previews",
            "cleanup_temp_files": True,
            "memory_limit_mb": 4096
        }
        
        # Analysis settings
        self.analysis_settings = {
            "scene_detection_threshold": 0.3,
            "highlight_detection_enabled": True,
            "face_detection_enabled": True,
            "object_detection_enabled": True,
            "audio_analysis_enabled": True,
            "minimum_segment_length": 2.0,
            "maximum_segment_length": 10.0,
            "confidence_threshold": 0.7
        }
        
        # Quality settings
        self.quality_settings = {
            "default_quality": "medium",
            "adaptive_bitrate": True,
            "quality_scaling": True,
            "auto_resolution": True,
            "frame_rate_optimization": True,
            "audio_quality": "medium",
            "encoding_preset": "medium"  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
        }
        
        # Adaptive settings
        self.adaptive_settings = {
            "device_detection": True,
            "bandwidth_detection": True,
            "user_preference_tracking": True,
            "content_based_adaptation": True,
            "time_based_adaptation": False,
            "location_based_adaptation": False,
            "a_b_testing": True
        }
        
        # Cache settings
        self.cache_settings = {
            "preview_cache_enabled": True,
            "analysis_cache_enabled": True,
            "cache_driver": "redis",
            "preview_cache_ttl": 604800,  # 1 week
            "analysis_cache_ttl": 86400,  # 1 day
            "cache_size_limit": "50GB",
            "preemptive_generation": True
        }
        
        # Performance settings
        self.performance_settings = {
            "progressive_download": True,
            "chunked_transfer": True,
            "cdn_integration": True,
            "edge_caching": True,
            "compression_optimization": True,
            "bandwidth_optimization": True,
            "load_balancing": True
        }
        
        # Initialize default templates
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default preview templates"""
        
        # Short video preview template
        short_video = PreviewTemplate(
            template_id="short_video",
            name="Short Video Preview",
            description="30-second video preview with highlights",
            preview_type=PreviewType.VIDEO_PREVIEW,
            target_duration=30.0,
            quality=PreviewQuality.MEDIUM,
            output_format=PreviewFormat.MP4,
            resolution_width=1280,
            resolution_height=720,
            content_analysis=[
                ContentAnalysisType.HIGHLIGHT_DETECTION,
                ContentAnalysisType.SCENE_DETECTION,
                ContentAnalysisType.FACE_DETECTION
            ],
            auto_highlight_detection=True,
            max_segments=3,
            color_correction=True,
            audio_normalization=True
        )
        
        # Micro video preview for social media
        micro_video = PreviewTemplate(
            template_id="micro_video",
            name="Micro Video Preview",
            description="15-second preview optimized for social media",
            preview_type=PreviewType.VIDEO_PREVIEW,
            target_duration=15.0,
            quality=PreviewQuality.MEDIUM,
            output_format=PreviewFormat.MP4,
            resolution_width=720,
            resolution_height=720,  # Square format
            content_analysis=[
                ContentAnalysisType.HIGHLIGHT_DETECTION,
                ContentAnalysisType.ACTION_DETECTION
            ],
            max_segments=2,
            watermark_enabled=True,
            overlay_enabled=True,
            overlay_text="Preview"
        )
        
        # High quality preview
        high_quality = PreviewTemplate(
            template_id="high_quality",
            name="High Quality Preview",
            description="High quality 60-second preview",
            preview_type=PreviewType.VIDEO_PREVIEW,
            target_duration=60.0,
            quality=PreviewQuality.HIGH,
            output_format=PreviewFormat.MP4,
            resolution_width=1920,
            resolution_height=1080,
            content_analysis=[
                ContentAnalysisType.HIGHLIGHT_DETECTION,
                ContentAnalysisType.SCENE_DETECTION,
                ContentAnalysisType.FACE_DETECTION,
                ContentAnalysisType.OBJECT_DETECTION,
                ContentAnalysisType.AUDIO_ANALYSIS
            ],
            max_segments=5,
            auto_stabilization=True,
            color_correction=True,
            noise_reduction=True,
            priority=8
        )
        
        # Adaptive streaming preview
        adaptive_preview = PreviewTemplate(
            template_id="adaptive_hls",
            name="Adaptive HLS Preview",
            description="Adaptive streaming preview with multiple quality levels",
            preview_type=PreviewType.VIDEO_PREVIEW,
            target_duration=45.0,
            quality=PreviewQuality.ADAPTIVE,
            output_format=PreviewFormat.HLS,
            resolution_width=1280,
            resolution_height=720,
            adaptive_quality=True,
            adaptive_strategy=AdaptiveStrategy.BANDWIDTH_BASED,
            content_analysis=[
                ContentAnalysisType.HIGHLIGHT_DETECTION,
                ContentAnalysisType.SCENE_DETECTION
            ],
            max_segments=4
        )
        
        # Audio preview template
        audio_preview = PreviewTemplate(
            template_id="audio_preview",
            name="Audio Preview",
            description="30-second audio preview with waveform visualization",
            preview_type=PreviewType.AUDIO_PREVIEW,
            target_duration=30.0,
            quality=PreviewQuality.MEDIUM,
            output_format=PreviewFormat.MP4,  # Video with audio waveform
            resolution_width=1280,
            resolution_height=720,
            content_analysis=[
                ContentAnalysisType.AUDIO_ANALYSIS,
                ContentAnalysisType.HIGHLIGHT_DETECTION
            ],
            audio_normalization=True,
            overlay_enabled=True,
            overlay_text="Audio Preview"
        )
        
        # Image slideshow preview
        slideshow_preview = PreviewTemplate(
            template_id="image_slideshow",
            name="Image Slideshow Preview",
            description="Image slideshow with transitions",
            preview_type=PreviewType.IMAGE_SLIDESHOW,
            target_duration=20.0,
            quality=PreviewQuality.HIGH,
            output_format=PreviewFormat.MP4,
            resolution_width=1920,
            resolution_height=1080,
            max_segments=10,  # Max images
            crossfade_duration=0.5,
            include_transitions=True
        )
        
        # Interactive preview
        interactive_preview = PreviewTemplate(
            template_id="interactive",
            name="Interactive Preview",
            description="Interactive preview with multiple quality options",
            preview_type=PreviewType.INTERACTIVE,
            target_duration=30.0,
            quality=PreviewQuality.ADAPTIVE,
            output_format=PreviewFormat.DASH,
            resolution_width=1280,
            resolution_height=720,
            adaptive_quality=True,
            content_analysis=[
                ContentAnalysisType.HIGHLIGHT_DETECTION,
                ContentAnalysisType.SCENE_DETECTION,
                ContentAnalysisType.FACE_DETECTION
            ],
            max_segments=3
        )
        
        # GIF preview
        gif_preview = PreviewTemplate(
            template_id="gif_preview",
            name="GIF Preview",
            description="Animated GIF preview for quick sharing",
            preview_type=PreviewType.ANIMATED,
            target_duration=10.0,
            quality=PreviewQuality.LOW,
            output_format=PreviewFormat.GIF,
            resolution_width=480,
            resolution_height=270,
            frame_rate=12.0,
            max_segments=1,  # Single continuous segment
            content_analysis=[ContentAnalysisType.ACTION_DETECTION]
        )
        
        # Document preview
        document_preview = PreviewTemplate(
            template_id="document_preview",
            name="Document Preview",
            description="Document page preview with text extraction",
            preview_type=PreviewType.DOCUMENT_PREVIEW,
            target_duration=0.0,  # Not applicable for documents
            quality=PreviewQuality.HIGH,
            output_format=PreviewFormat.JPEG,
            resolution_width=1200,
            resolution_height=1600,
            content_analysis=[ContentAnalysisType.TEXT_EXTRACTION],
            max_segments=5  # Max pages to preview
        )
        
        # Store templates
        templates = [
            short_video, micro_video, high_quality, adaptive_preview,
            audio_preview, slideshow_preview, interactive_preview,
            gif_preview, document_preview
        ]
        
        for template in templates:
            self.templates[template.template_id] = template
    
    def create_preview_template(self, template_data: Dict[str, Any]) -> PreviewTemplate:
        """Create new preview template"""
        
        template = PreviewTemplate(
            template_id=template_data.get("template_id", f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=template_data["name"],
            description=template_data.get("description", ""),
            preview_type=PreviewType(template_data.get("preview_type", "video_preview")),
            target_duration=template_data.get("target_duration", 30.0),
            quality=PreviewQuality(template_data.get("quality", "medium")),
            output_format=PreviewFormat(template_data.get("output_format", "mp4")),
            resolution_width=template_data.get("resolution_width", 1280),
            resolution_height=template_data.get("resolution_height", 720),
            auto_highlight_detection=template_data.get("auto_highlight_detection", True),
            adaptive_quality=template_data.get("adaptive_quality", False),
            priority=template_data.get("priority", 5)
        )
        
        # Set content analysis types
        if "content_analysis" in template_data:
            template.content_analysis = [
                ContentAnalysisType(ca) for ca in template_data["content_analysis"]
            ]
        
        self.templates[template.template_id] = template
        return template
    
    def create_preview_job(self, job_data: Dict[str, Any]) -> PreviewJob:
        """Create new preview generation job"""
        
        job = PreviewJob(
            job_id=job_data.get("job_id", f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            source_file=job_data["source_file"],
            template_id=job_data["template_id"],
            output_path=job_data.get("output_path", ""),
            custom_params=job_data.get("custom_params", {})
        )
        
        # Add custom segments if provided
        if "custom_segments" in job_data:
            for seg_data in job_data["custom_segments"]:
                segment = PreviewSegment(
                    segment_id=seg_data.get("segment_id", f"seg_{len(job.custom_segments)}"),
                    start_time=seg_data["start_time"],
                    duration=seg_data["duration"],
                    weight=seg_data.get("weight", 1.0),
                    segment_type=seg_data.get("segment_type", "custom")
                )
                job.custom_segments.append(segment)
        
        self.jobs[job.job_id] = job
        return job
    
    async def generate_preview(self, source_file: str, template_id: str,
                              output_path: str = "", custom_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate preview"""
        
        result = {
            "success": False,
            "job_id": None,
            "output_files": [],
            "preview_duration": 0.0,
            "compression_ratio": 0.0,
            "processing_time": 0.0,
            "analysis_confidence": 0.0,
            "quality_score": 0.0,
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
            
            job = self.create_preview_job(job_data)
            result["job_id"] = job.job_id
            
            # Start processing
            job.start_processing()
            
            # Simulate content analysis
            import time
            import random
            
            processing_start = time.time()
            
            # Step 1: Content Analysis
            job.update_progress(0.1, "Analyzing source content")
            time.sleep(random.uniform(1.0, 3.0))
            
            # Simulate content analysis results
            source_duration = random.uniform(300, 3600)  # 5 minutes to 1 hour
            analyzed_segments = self._simulate_content_analysis(source_duration, template)
            confidence = random.uniform(0.7, 0.95)
            
            job.set_analysis_results(analyzed_segments, source_duration, confidence)
            
            # Step 2: Segment Selection
            job.update_progress(0.3, "Selecting optimal segments")
            time.sleep(random.uniform(0.5, 1.5))
            
            selected_segments = self._select_best_segments(analyzed_segments, template)
            job.set_selected_segments(selected_segments)
            
            # Step 3: Video Generation
            job.update_progress(0.5, "Generating preview video")
            time.sleep(random.uniform(2.0, 5.0))
            
            # Step 4: Encoding
            job.update_progress(0.8, "Encoding output file")
            time.sleep(random.uniform(1.0, 3.0))
            
            # Generate output files
            base_name = os.path.splitext(os.path.basename(source_file))[0]
            
            if not output_path:
                output_path = f"/var/previews/{template_id}"
                os.makedirs(output_path, exist_ok=True)
            
            if template.supports_adaptive_streaming():
                # Generate multiple quality files for adaptive streaming
                output_files = [
                    os.path.join(output_path, f"{base_name}_{template_id}.m3u8"),  # HLS playlist
                    os.path.join(output_path, f"{base_name}_{template_id}_720p.ts"),
                    os.path.join(output_path, f"{base_name}_{template_id}_480p.ts"),
                    os.path.join(output_path, f"{base_name}_{template_id}_360p.ts")
                ]
            else:
                output_file = os.path.join(output_path, f"{base_name}_{template_id}.{template.output_format.value}")
                output_files = [output_file]
            
            # Simulate file sizes
            file_sizes = {}
            for file_path in output_files:
                estimated_size = template.estimate_file_size(job.preview_duration)
                file_sizes[file_path] = int(estimated_size * random.uniform(0.8, 1.2))
            
            # Quality scores
            quality_scores = [random.uniform(0.7, 0.95) for _ in selected_segments]
            
            # Processing cost (simplified)
            processing_cost = job.preview_duration * 0.01  # $0.01 per second
            
            processing_end = time.time()
            processing_time = processing_end - processing_start
            
            # Complete job
            job.complete_processing(output_files, file_sizes, quality_scores, processing_cost)
            
            result.update({
                "success": True,
                "output_files": output_files,
                "preview_duration": job.preview_duration,
                "compression_ratio": job.get_compression_ratio(),
                "processing_time": processing_time,
                "analysis_confidence": confidence,
                "quality_score": job.overall_quality_score
            })
            
        except Exception as e:
            result["error"] = str(e)
            if result["job_id"] and result["job_id"] in self.jobs:
                self.jobs[result["job_id"]].fail_processing(str(e))
        
        return result
    
    def _simulate_content_analysis(self, source_duration: float, 
                                  template: PreviewTemplate) -> List[PreviewSegment]:
        """Simulate content analysis and segment detection"""
        
        import random
        
        segments = []
        segment_count = random.randint(5, 20)
        
        for i in range(segment_count):
            start_time = random.uniform(0, source_duration - 10)
            duration = random.uniform(
                template.minimum_segment_duration,
                min(template.minimum_segment_duration * 3, source_duration - start_time)
            )
            
            segment = PreviewSegment(
                segment_id=f"seg_{i}",
                start_time=start_time,
                duration=duration,
                weight=random.uniform(0.3, 1.0),
                segment_type=random.choice(["auto", "highlight", "intro", "outro"]),
                scene_score=random.uniform(0.2, 1.0),
                action_score=random.uniform(0.1, 1.0),
                face_score=random.uniform(0.0, 1.0),
                audio_score=random.uniform(0.1, 1.0)
            )
            
            segments.append(segment)
        
        # Sort by start time
        segments.sort(key=lambda x: x.start_time)
        
        return segments
    
    def _select_best_segments(self, analyzed_segments: List[PreviewSegment],
                             template: PreviewTemplate) -> List[PreviewSegment]:
        """Select best segments for preview generation"""
        
        # Sort segments by total score
        scored_segments = sorted(analyzed_segments, key=lambda x: x.get_total_score(), reverse=True)
        
        selected_segments = []
        total_duration = 0.0
        
        for segment in scored_segments:
            # Check if adding this segment would exceed target duration
            if total_duration + segment.duration > template.target_duration:
                # Try to trim the segment
                remaining_duration = template.target_duration - total_duration
                if remaining_duration >= template.minimum_segment_duration:
                    # Create trimmed segment
                    trimmed_segment = PreviewSegment(
                        segment_id=f"{segment.segment_id}_trimmed",
                        start_time=segment.start_time,
                        duration=remaining_duration,
                        weight=segment.weight,
                        segment_type=segment.segment_type,
                        scene_score=segment.scene_score,
                        action_score=segment.action_score,
                        face_score=segment.face_score,
                        audio_score=segment.audio_score
                    )
                    selected_segments.append(trimmed_segment)
                    total_duration += remaining_duration
                break
            
            # Check minimum gap between segments
            if selected_segments:
                last_segment = selected_segments[-1]
                if segment.start_time < last_segment.get_end_time() + template.segment_min_gap:
                    continue
            
            selected_segments.append(segment)
            total_duration += segment.duration
            
            # Check if we've reached max segments
            if len(selected_segments) >= template.max_segments:
                break
            
            # Check if we've reached target duration
            if total_duration >= template.target_duration:
                break
        
        # Sort selected segments by start time
        selected_segments.sort(key=lambda x: x.start_time)
        
        return selected_segments
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get preview job status"""
        
        if job_id not in self.jobs:
            return {"error": f"Job {job_id} not found"}
        
        job = self.jobs[job_id]
        return job.to_dict()
    
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
        
        processing_durations = []
        quality_scores = []
        compression_ratios = []
        
        for job in template_jobs:
            if job.get_processing_duration():
                processing_durations.append(job.get_processing_duration().total_seconds())
            
            if job.overall_quality_score > 0:
                quality_scores.append(job.overall_quality_score)
            
            if job.get_compression_ratio() > 0:
                compression_ratios.append(job.get_compression_ratio())
        
        avg_processing_time = sum(processing_durations) / len(processing_durations) if processing_durations else 0
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        avg_compression = sum(compression_ratios) / len(compression_ratios) if compression_ratios else 0
        
        return {
            "template_id": template_id,
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            "average_processing_time": avg_processing_time,
            "average_quality_score": avg_quality,
            "average_compression_ratio": avg_compression
        }
    
    def get_preview_statistics(self) -> Dict[str, Any]:
        """Get preview generation statistics"""
        
        stats = {
            "templates": {
                "total": len(self.templates),
                "enabled": len([t for t in self.templates.values() if t.enabled]),
                "by_type": {},
                "by_format": {},
                "by_quality": {}
            },
            "jobs": {
                "total": len(self.jobs),
                "pending": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0
            },
            "performance": {
                "total_preview_duration": 0.0,
                "total_processing_time": 0.0,
                "average_compression_ratio": 0.0,
                "average_quality_score": 0.0
            }
        }
        
        # Template statistics
        for template in self.templates.values():
            preview_type = template.preview_type.value
            output_format = template.output_format.value
            quality = template.quality.value
            
            stats["templates"]["by_type"][preview_type] = stats["templates"]["by_type"].get(preview_type, 0) + 1
            stats["templates"]["by_format"][output_format] = stats["templates"]["by_format"].get(output_format, 0) + 1
            stats["templates"]["by_quality"][quality] = stats["templates"]["by_quality"].get(quality, 0) + 1
        
        # Job statistics
        preview_durations = []
        processing_times = []
        compression_ratios = []
        quality_scores = []
        
        for job in self.jobs.values():
            stats["jobs"][job.status] += 1
            
            if job.preview_duration > 0:
                preview_durations.append(job.preview_duration)
            
            if job.get_processing_duration():
                processing_times.append(job.get_processing_duration().total_seconds())
            
            if job.get_compression_ratio() > 0:
                compression_ratios.append(job.get_compression_ratio())
            
            if job.overall_quality_score > 0:
                quality_scores.append(job.overall_quality_score)
        
        # Performance statistics
        stats["performance"]["total_preview_duration"] = sum(preview_durations)
        stats["performance"]["total_processing_time"] = sum(processing_times)
        stats["performance"]["average_compression_ratio"] = sum(compression_ratios) / len(compression_ratios) if compression_ratios else 0
        stats["performance"]["average_quality_score"] = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return stats
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete preview configuration"""
        return {
            "preview_statistics": self.get_preview_statistics(),
            "templates": {template_id: template.to_dict() for template_id, template in self.templates.items()},
            "global_settings": {
                "preview_enabled": self.preview_enabled,
                "auto_generation": self.auto_generation,
                "ai_analysis": self.ai_analysis,
                "adaptive_streaming": self.adaptive_streaming
            },
            "processing_settings": self.processing_settings,
            "analysis_settings": self.analysis_settings,
            "quality_settings": self.quality_settings,
            "adaptive_settings": self.adaptive_settings,
            "cache_settings": self.cache_settings,
            "performance_settings": self.performance_settings
        }

# Global preview configuration instance
preview_config = PreviewConfiguration()

# Export main classes
__all__ = [
    "PreviewConfiguration",
    "PreviewType",
    "PreviewQuality",
    "PreviewDuration",
    "PreviewFormat",
    "ContentAnalysisType",
    "AdaptiveStrategy",
    "PreviewSegment",
    "PreviewTemplate",
    "PreviewJob",
    "preview_config"
]
