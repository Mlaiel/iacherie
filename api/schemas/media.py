"""Media Processing Schemas for IA Influencer Agent Platform
Professional media file handling, processing, and transformation schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field, validator, HttpUrl

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class MediaFileUpload(BaseSchema):
    """Professional media file upload schema."""    
    content_id: UUID = Field(description="Associated content ID")
    file_type: str = Field(description="Media file type (audio, video, image, document)")
    mime_type: str = Field(description="MIME type of the file")
    filename: str = Field(description="Original filename")
    file_size: int = Field(gt=0, description="File size in bytes")
    file_checksum: str = Field(description="File integrity checksum")
    
    # Upload metadata
    upload_session_id: str = Field(description="Upload session identifier")
    chunk_size: Optional[int] = Field(None, description="Chunk size for chunked upload")
    total_chunks: Optional[int] = Field(None, description="Total number of chunks")
    current_chunk: Optional[int] = Field(None, description="Current chunk number")
    
    # File properties
    duration_seconds: Optional[float] = Field(None, description="Media duration")
    width: Optional[int] = Field(None, description="Image/video width")
    height: Optional[int] = Field(None, description="Image/video height")
    bit_rate: Optional[int] = Field(None, description="Audio/video bitrate")
    sample_rate: Optional[int] = Field(None, description="Audio sample rate")
    channels: Optional[int] = Field(None, description="Audio channels")
    codec: Optional[str] = Field(None, description="Media codec")
    
    @validator('file_type')
    def validate_file_type(cls, v):
        """Validate file type."""        allowed_types = {'audio', 'video', 'image', 'document', 'archive', 'other'}
        if v not in allowed_types:
            raise ValueError(f'File type must be one of: {", ".join(allowed_types)}')
        return v


class MediaFileOut(UUIDSchema, TimestampSchema):
    """Media file information schema."""    
    content_id: UUID
    file_type: str
    mime_type: str
    filename: str
    file_size: int
    file_checksum: str
    
    # Storage information
    storage_path: str = Field(description="File storage path")
    storage_provider: str = Field(description="Storage provider (local, s3, gcs)")
    cdn_url: Optional[HttpUrl] = Field(None, description="CDN URL for file access")
    
    # File properties
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec: Optional[str] = None
    
    # Processing status
    processing_status: str = Field(default="pending")
    processing_progress: float = Field(default=0.0, ge=0.0, le=1.0)
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    
    # Generated variants
    variants: List[Dict[str, Any]] = Field(default_factory=list, description="Generated file variants")
    thumbnails: List[Dict[str, Any]] = Field(default_factory=list, description="Generated thumbnails")
    previews: List[Dict[str, Any]] = Field(default_factory=list, description="Generated previews")
    
    # Access URLs
    download_url: Optional[HttpUrl] = None
    streaming_url: Optional[HttpUrl] = None
    thumbnail_url: Optional[HttpUrl] = None
    preview_url: Optional[HttpUrl] = None
    
    # Analytics
    download_count: int = Field(default=0, ge=0)
    view_count: int = Field(default=0, ge=0)
    bandwidth_used_bytes: int = Field(default=0, ge=0)


class MediaProcessing(UUIDSchema, TimestampSchema):
    """Media processing job configuration schema."""    
    media_file_id: UUID
    processing_type: str = Field(description="Type of processing to perform")
    processing_priority: int = Field(default=5, ge=1, le=10, description="Processing priority")
    
    # Processing parameters
    processing_parameters: Dict[str, Any] = Field(default_factory=dict)
    output_formats: List[str] = Field(default_factory=list)
    quality_settings: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing status
    status: str = Field(default="queued", description="Processing status")
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    estimated_completion: Optional[datetime] = None
    
    # Results
    processing_results: Dict[str, Any] = Field(default_factory=dict)
    output_files: List[Dict[str, Any]] = Field(default_factory=list)
    processing_logs: List[str] = Field(default_factory=list)
    error_details: Optional[str] = None
    
    # Performance metrics
    processing_time_seconds: Optional[float] = None
    cpu_usage_average: Optional[float] = None
    memory_usage_peak_mb: Optional[float] = None
    
    @validator('processing_type')
    def validate_processing_type(cls, v):
        """Validate processing type."""        allowed_types = {
            'transcode', 'compress', 'thumbnail', 'preview', 'analysis',
            'watermark', 'normalize', 'enhance', 'extract_metadata'
        }
        if v not in allowed_types:
            raise ValueError(f'Processing type must be one of: {", ".join(allowed_types)}')
        return v


class MediaTransform(BaseSchema):
    """Media transformation configuration schema."""    
    media_file_id: UUID
    transformation_name: str = Field(description="Transformation preset name")
    
    # Video transformations
    video_codec: Optional[str] = Field(None, description="Target video codec")
    video_bitrate: Optional[int] = Field(None, description="Target video bitrate")
    video_resolution: Optional[str] = Field(None, description="Target resolution (e.g., '1920x1080')")
    video_fps: Optional[float] = Field(None, description="Target frames per second")
    video_quality: Optional[str] = Field(None, description="Quality preset")
    
    # Audio transformations
    audio_codec: Optional[str] = Field(None, description="Target audio codec")
    audio_bitrate: Optional[int] = Field(None, description="Target audio bitrate")
    audio_sample_rate: Optional[int] = Field(None, description="Target sample rate")
    audio_channels: Optional[int] = Field(None, description="Target channel count")
    audio_volume: Optional[float] = Field(None, description="Volume adjustment")
    
    # Image transformations
    image_format: Optional[str] = Field(None, description="Target image format")
    image_quality: Optional[int] = Field(None, ge=1, le=100, description="JPEG quality")
    image_width: Optional[int] = Field(None, description="Target width")
    image_height: Optional[int] = Field(None, description="Target height")
    image_crop: Optional[str] = Field(None, description="Crop mode")
    image_filters: List[str] = Field(default_factory=list, description="Image filters")
    
    # General options
    preserve_metadata: bool = Field(default=True, description="Preserve original metadata")
    add_watermark: bool = Field(default=False, description="Add watermark")
    output_container: Optional[str] = Field(None, description="Output container format")


class MediaAnalysis(UUIDSchema, TimestampSchema):
    """Media analysis results schema."""    
    media_file_id: UUID
    analysis_type: str = Field(description="Type of analysis performed")
    analysis_version: str = Field(description="Analysis algorithm version")
    
    # Audio analysis
    audio_features: Dict[str, Any] = Field(default_factory=dict, description="Audio feature extraction")
    audio_quality_metrics: Dict[str, float] = Field(default_factory=dict)
    audio_technical_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Video analysis
    video_features: Dict[str, Any] = Field(default_factory=dict, description="Video feature extraction")
    scene_detection: List[Dict[str, Any]] = Field(default_factory=list)
    motion_analysis: Dict[str, Any] = Field(default_factory=dict)
    visual_quality_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Image analysis
    image_features: Dict[str, Any] = Field(default_factory=dict, description="Image feature extraction")
    color_analysis: Dict[str, Any] = Field(default_factory=dict)
    composition_analysis: Dict[str, Any] = Field(default_factory=dict)
    object_detection: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Content analysis
    content_classification: Dict[str, float] = Field(default_factory=dict)
    sentiment_analysis: Optional[Dict[str, float]] = None
    explicit_content_detection: Dict[str, float] = Field(default_factory=dict)
    brand_safety_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Technical analysis
    file_integrity_check: bool = Field(default=True)
    corruption_detected: bool = Field(default=False)
    technical_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Performance metrics
    analysis_duration_seconds: float = Field(ge=0.0)
    confidence_score: float = Field(ge=0.0, le=1.0)


class AudioProcessing(BaseSchema):
    """Specialized audio processing schema."""    
    media_file_id: UUID
    processing_preset: str = Field(description="Audio processing preset")
    
    # Audio enhancement
    noise_reduction: bool = Field(default=False)
    normalize_volume: bool = Field(default=True)
    enhance_quality: bool = Field(default=False)
    stereo_enhancement: bool = Field(default=False)
    
    # Audio effects
    reverb: Optional[Dict[str, float]] = None
    equalizer: Optional[Dict[str, float]] = None
    compressor: Optional[Dict[str, float]] = None
    limiter: Optional[Dict[str, float]] = None
    
    # Format conversion
    target_format: str = Field(description="Target audio format")
    target_bitrate: int = Field(description="Target bitrate in kbps")
    target_sample_rate: int = Field(description="Target sample rate in Hz")
    target_channels: int = Field(description="Target channel count")
    
    # Advanced options
    fade_in_duration: Optional[float] = Field(None, description="Fade in duration in seconds")
    fade_out_duration: Optional[float] = Field(None, description="Fade out duration in seconds")
    trim_start: Optional[float] = Field(None, description="Trim from start in seconds")
    trim_end: Optional[float] = Field(None, description="Trim from end in seconds")


class VideoProcessing(BaseSchema):
    """Specialized video processing schema."""    
    media_file_id: UUID
    processing_preset: str = Field(description="Video processing preset")
    
    # Video encoding
    target_codec: str = Field(description="Target video codec")
    target_bitrate: int = Field(description="Target bitrate in kbps")
    target_resolution: str = Field(description="Target resolution")
    target_fps: float = Field(description="Target frames per second")
    
    # Video enhancement
    upscale: bool = Field(default=False)
    stabilization: bool = Field(default=False)
    noise_reduction: bool = Field(default=False)
    color_correction: bool = Field(default=False)
    
    # Video effects
    filters: List[str] = Field(default_factory=list)
    transitions: List[Dict[str, Any]] = Field(default_factory=list)
    overlays: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Audio processing (for video files)
    audio_processing: Optional[AudioProcessing] = None
    
    # Output options
    generate_thumbnails: bool = Field(default=True)
    thumbnail_count: int = Field(default=10, ge=1, le=100)
    generate_preview: bool = Field(default=True)
    preview_duration: int = Field(default=30, ge=5, le=300)


class ImageProcessing(BaseSchema):
    """Specialized image processing schema."""    
    media_file_id: UUID
    processing_preset: str = Field(description="Image processing preset")
    
    # Image optimization
    optimize_size: bool = Field(default=True)
    target_quality: int = Field(default=85, ge=1, le=100)
    progressive_jpeg: bool = Field(default=True)
    strip_metadata: bool = Field(default=False)
    
    # Image transformations
    resize: Optional[Dict[str, int]] = Field(None, description="Resize parameters")
    crop: Optional[Dict[str, Any]] = Field(None, description="Crop parameters")
    rotate: Optional[float] = Field(None, description="Rotation angle")
    flip: Optional[str] = Field(None, description="Flip direction")
    
    # Image enhancement
    auto_enhance: bool = Field(default=False)
    brightness_adjustment: Optional[float] = Field(None, ge=-100, le=100)
    contrast_adjustment: Optional[float] = Field(None, ge=-100, le=100)
    saturation_adjustment: Optional[float] = Field(None, ge=-100, le=100)
    
    # Filters and effects
    filters: List[str] = Field(default_factory=list)
    blur_radius: Optional[float] = Field(None, ge=0)
    sharpen_amount: Optional[float] = Field(None, ge=0)
    
    # Format conversion
    target_format: str = Field(description="Target image format")
    background_color: Optional[str] = Field(None, description="Background color for transparency")
    
    # Variants generation
    generate_variants: bool = Field(default=True)
    variant_sizes: List[Dict[str, int]] = Field(
        default_factory=lambda: [
            {"width": 150, "height": 150, "name": "thumbnail"},
            {"width": 300, "height": 300, "name": "small"},
            {"width": 800, "height": 800, "name": "medium"},
            {"width": 1200, "height": 1200, "name": "large"}
        ]
    )


class MediaStreamingConfig(BaseSchema):
    """Media streaming configuration schema."""    
    media_file_id: UUID
    streaming_protocol: str = Field(description="Streaming protocol (HLS, DASH, etc.)")
    
    # Quality variants
    quality_variants: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Different quality variants for adaptive streaming"
    )
    
    # Streaming settings
    segment_duration: int = Field(default=6, ge=2, le=10, description="Segment duration in seconds")
    playlist_type: str = Field(default="vod", description="Playlist type (vod, live)")
    encryption_enabled: bool = Field(default=True, description="Enable stream encryption")
    
    # Access control
    access_control: Dict[str, Any] = Field(default_factory=dict)
    drm_enabled: bool = Field(default=False, description="Enable DRM protection")
    geo_restrictions: List[str] = Field(default_factory=list)
    
    # Analytics
    analytics_enabled: bool = Field(default=True)
    detailed_analytics: bool = Field(default=False)


class MediaBackup(UUIDSchema, TimestampSchema):
    """Media backup and archival schema."""    
    media_file_id: UUID
    backup_type: str = Field(description="Backup type (full, incremental, snapshot)")
    backup_location: str = Field(description="Backup storage location")
    backup_provider: str = Field(description="Backup service provider")
    
    # Backup configuration
    retention_days: int = Field(default=365, ge=1, description="Backup retention period")
    compression_enabled: bool = Field(default=True)
    encryption_enabled: bool = Field(default=True)
    
    # Backup status
    backup_status: str = Field(default="pending")
    backup_size: Optional[int] = Field(None, description="Backup size in bytes")
    backup_checksum: Optional[str] = Field(None, description="Backup integrity checksum")
    
    # Recovery information
    recovery_point_objective: int = Field(default=24, description="RPO in hours")
    recovery_time_objective: int = Field(default=4, description="RTO in hours")
    last_verified: Optional[datetime] = Field(None, description="Last backup verification")
    
    @validator('backup_type')
    def validate_backup_type(cls, v):
        """Validate backup type."""        allowed_types = {'full', 'incremental', 'differential', 'snapshot', 'continuous'}
        if v not in allowed_types:
            raise ValueError(f'Backup type must be one of: {", ".join(allowed_types)}')
        return v
