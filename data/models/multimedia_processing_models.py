"""Multimedia Processing Models
============================

Advanced multimedia processing models for IA Influencer Agent platform.
Comprehensive media processing with quality optimization, format conversion,
and scalable cloud-native processing pipeline.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

🚀 ENTERPRISE FEATURES:
• Multi-format multimedia processing (audio, video, image, document)
• Quality optimization & compression algorithms
• Real-time processing job management
• Format conversion & optimization
• Quality metrics & assessment
• Performance monitoring & analytics
• Scalable processing pipeline
• Cloud-native processing architecture
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum, Index, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, date
from enum import Enum
import uuid
from typing import Optional, Dict, Any, List

# Import base from enterprise content models
from .enterprise_content_models import Base

# ============================================================================
# ENUMS - Media Processing System
# ============================================================================

class MediaType(Enum):
    """Types of media for processing"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    LIVE_STREAM = "live_stream"
    PODCAST = "podcast"
    ANIMATION = "animation"
    THREE_D_MODEL = "three_d_model"
    INTERACTIVE_MEDIA = "interactive_media"
    MIXED_MEDIA = "mixed_media"
    ARCHIVE = "archive"
    PRESENTATION = "presentation"


class ProcessingStage(Enum):
    """Stages in multimedia processing pipeline"""
    UPLOAD = "upload"
    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    ANALYSIS = "analysis"
    ENHANCEMENT = "enhancement"
    COMPRESSION = "compression"
    CONVERSION = "conversion"
    OPTIMIZATION = "optimization"
    QUALITY_CHECK = "quality_check"
    FINALIZATION = "finalization"
    DISTRIBUTION = "distribution"
    ARCHIVAL = "archival"


class QualityLevel(Enum):
    """Quality levels for media processing"""
    LOW = "low"                    # 480p, 96kbps
    STANDARD = "standard"          # 720p, 128kbps
    HIGH = "high"                  # 1080p, 192kbps
    ULTRA = "ultra"                # 4K, 320kbps
    LOSSLESS = "lossless"          # Original quality
    CUSTOM = "custom"              # Custom quality settings
    AUTO = "auto"                  # AI-determined optimal quality
    ADAPTIVE = "adaptive"          # Adaptive quality based on content


class CompressionAlgorithm(Enum):
    """Compression algorithms for media processing"""
    # Video codecs
    H264 = "h264"
    H265_HEVC = "h265_hevc"
    VP9 = "vp9"
    AV1 = "av1"
    XVID = "xvid"
    
    # Audio codecs
    OPUS = "opus"
    AAC = "aac"
    MP3 = "mp3"
    FLAC = "flac"
    VORBIS = "vorbis"
    
    # Image codecs
    JPEG = "jpeg"
    WEBP = "webp"
    AVIF = "avif"
    PNG = "png"
    HEIF = "heif"


class ProcessingStatus(Enum):
    """Status of processing jobs"""
    QUEUED = "queued"
    STARTING = "starting"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRY = "retry"
    OPTIMIZING = "optimizing"
    FINALIZING = "finalizing"


class OutputFormat(Enum):
    """Output formats for processed media"""
    # Video formats
    MP4 = "mp4"
    WEBM = "webm"
    MOV = "mov"
    AVI = "avi"
    MKV = "mkv"
    FLV = "flv"
    
    # Audio formats
    MP3_AUDIO = "mp3"
    AAC_AUDIO = "aac"
    OGG = "ogg"
    WAV = "wav"
    FLAC_AUDIO = "flac"
    M4A = "m4a"
    
    # Image formats
    JPEG_IMAGE = "jpeg"
    PNG_IMAGE = "png"
    WEBP_IMAGE = "webp"
    GIF = "gif"
    SVG = "svg"
    TIFF = "tiff"
    
    # Document formats
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    EPUB = "epub"


class ProcessingPriority(Enum):
    """Priority levels for processing jobs"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    REAL_TIME = "real_time"
    BACKGROUND = "background"
    SCHEDULED = "scheduled"


# ============================================================================
# MULTIMEDIA ASSET MODELS
# ============================================================================

class MultimediaAssetModel(Base):
    """
    Enterprise multimedia asset model for comprehensive media management.
    Advanced asset tracking with technical specifications and processing history.
    """
    __tablename__ = 'multimedia_assets'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Media classification
    media_type = Column(SQLEnum(MediaType), nullable=False, index=True)
    asset_name = Column(String(500), nullable=False)
    asset_description = Column(Text)
    file_extension = Column(String(20), nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # File information
    original_filename = Column(String(500))
    file_size_bytes = Column(Integer, nullable=False, index=True)
    file_hash = Column(String(200), unique=True, nullable=False, index=True)  # SHA-256
    checksum = Column(String(200))  # MD5 for integrity checks
    storage_path = Column(String(1000), nullable=False)
    storage_provider = Column(String(100), default="local")  # "local", "s3", "gcs", "azure"
    
    # Technical specifications
    duration_seconds = Column(Float)           # For audio/video
    frame_rate = Column(Float)                 # For video
    bit_rate = Column(Integer)                 # For audio/video
    sample_rate = Column(Integer)              # For audio
    channels = Column(Integer)                 # For audio (1=mono, 2=stereo)
    resolution_width = Column(Integer)         # For image/video
    resolution_height = Column(Integer)        # For image/video
    aspect_ratio = Column(String(20))          # "16:9", "4:3", "1:1"
    color_depth = Column(Integer)              # Bits per pixel
    color_space = Column(String(50))           # "RGB", "YUV", "CMYK"
    
    # Quality metrics
    quality_score = Column(Float, default=0.0)        # 0-100 quality rating
    technical_quality = Column(Float, default=0.0)    # Technical quality assessment
    perceptual_quality = Column(Float, default=0.0)   # Perceptual quality score
    compression_ratio = Column(Float, default=1.0)    # Compression ratio
    noise_level = Column(Float, default=0.0)          # Noise detection score
    artifact_score = Column(Float, default=0.0)       # Compression artifacts
    
    # Metadata
    metadata_extracted = Column(JSONB, default=dict)  # Extracted metadata
    exif_data = Column(JSONB, default=dict)           # EXIF data for images
    id3_tags = Column(JSONB, default=dict)            # ID3 tags for audio
    xmp_data = Column(JSONB, default=dict)            # XMP metadata
    custom_metadata = Column(JSONB, default=dict)     # Custom metadata
    
    # Processing history
    processing_jobs = Column(JSONB, default=list)     # List of processing job IDs
    processing_count = Column(Integer, default=0)
    last_processed_at = Column(DateTime(timezone=True))
    processing_time_total = Column(Float, default=0.0)  # Total processing time
    versions_created = Column(Integer, default=0)
    
    # Versions & Variants
    is_original = Column(Boolean, default=True)
    parent_asset_id = Column(UUID(as_uuid=True), ForeignKey('multimedia_assets.id'))
    version_number = Column(String(20), default="1.0")
    variant_type = Column(String(100))  # "thumbnail", "preview", "optimized"
    generation_method = Column(String(100))  # "original", "processed", "ai_generated"
    
    # Access & Distribution
    access_url = Column(String(1000))
    cdn_url = Column(String(1000))
    streaming_url = Column(String(1000))
    download_url = Column(String(1000))
    thumbnail_url = Column(String(1000))
    preview_url = Column(String(1000))
    
    # Performance metrics
    download_count = Column(Integer, default=0)
    stream_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    bandwidth_used = Column(Integer, default=0)  # Bytes
    cache_hit_ratio = Column(Float, default=0.0)
    average_load_time = Column(Float, default=0.0)  # seconds
    
    # Content analysis
    content_tags = Column(JSONB, default=list)        # AI-generated content tags
    scene_detection = Column(JSONB, default=list)     # Scene/segment detection
    object_detection = Column(JSONB, default=list)    # Detected objects
    face_detection = Column(JSONB, default=list)      # Face detection results
    text_recognition = Column(JSONB, default=list)    # OCR results
    audio_features = Column(JSONB, default=dict)      # Audio analysis features
    
    # AI processing
    ai_enhanced = Column(Boolean, default=False)
    ai_upscaled = Column(Boolean, default=False)
    ai_denoised = Column(Boolean, default=False)
    ai_colorized = Column(Boolean, default=False)
    ai_analysis_complete = Column(Boolean, default=False)
    ai_processing_version = Column(String(50))
    
    # Security & Protection
    watermarked = Column(Boolean, default=False)
    watermark_type = Column(String(50))  # "visible", "invisible", "digital"
    encrypted = Column(Boolean, default=False)
    encryption_algorithm = Column(String(100))
    access_restricted = Column(Boolean, default=False)
    drm_protected = Column(Boolean, default=False)
    
    # Geographic & Legal
    geo_location = Column(JSONB, default=dict)        # GPS coordinates if available
    creation_location = Column(String(300))
    copyright_info = Column(JSONB, default=dict)
    licensing_terms = Column(Text)
    usage_rights = Column(JSONB, default=dict)
    content_rating = Column(String(50))  # "G", "PG", "R", etc.
    
    # Optimization features
    optimized_for_mobile = Column(Boolean, default=False)
    optimized_for_web = Column(Boolean, default=False)
    progressive_download = Column(Boolean, default=False)
    adaptive_streaming = Column(Boolean, default=False)
    preload_enabled = Column(Boolean, default=False)
    
    # Storage optimization
    compressed = Column(Boolean, default=False)
    compression_algorithm = Column(SQLEnum(CompressionAlgorithm))
    compression_level = Column(Integer)  # 1-10 compression level
    deduplication_applied = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    archive_date = Column(DateTime(timezone=True))
    
    # Backup & Recovery
    backup_count = Column(Integer, default=0)
    last_backup_date = Column(DateTime(timezone=True))
    backup_locations = Column(JSONB, default=list)
    recovery_tested = Column(Boolean, default=False)
    integrity_checked = Column(Boolean, default=False)
    
    # Analytics & Insights
    analytics_data = Column(JSONB, default=dict)
    performance_insights = Column(JSONB, default=list)
    optimization_suggestions = Column(JSONB, default=list)
    usage_patterns = Column(JSONB, default=dict)
    cost_analysis = Column(JSONB, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    uploaded_at = Column(DateTime(timezone=True))
    processed_at = Column(DateTime(timezone=True))
    
    # System flags
    is_processing = Column(Boolean, default=False, index=True)
    is_ready = Column(Boolean, default=False, index=True)
    is_failed = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    content = relationship("ContentModel", backref="multimedia_assets")
    user = relationship("UserModel", backref="multimedia_assets")
    parent_asset = relationship("MultimediaAssetModel", remote_side=[id], backref="child_assets")
    processing_jobs_rel = relationship("ProcessingJobModel", back_populates="multimedia_asset", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_asset_type_size', 'media_type', 'file_size_bytes'),
        Index('idx_asset_content_user', 'content_id', 'user_id'),
        Index('idx_asset_ready_processing', 'is_ready', 'is_processing'),
        Index('idx_asset_hash_original', 'file_hash', 'is_original'),
    )
    
    def __repr__(self) -> None:
        return f"<MultimediaAssetModel(id={self.id}, name='{self.asset_name[:50]}', type={self.media_type.value})>"


# ============================================================================
# PROCESSING JOB MODELS
# ============================================================================

class ProcessingJobModel(Base):
    """
    Processing job model for multimedia processing pipeline management.
    Comprehensive job tracking with performance monitoring and error handling.
    """
    __tablename__ = 'processing_jobs'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    multimedia_asset_id = Column(UUID(as_uuid=True), ForeignKey('multimedia_assets.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Job details
    job_name = Column(String(300), nullable=False)
    job_type = Column(String(100), nullable=False)  # "conversion", "compression", "enhancement"
    processing_stage = Column(SQLEnum(ProcessingStage), nullable=False, index=True)
    status = Column(SQLEnum(ProcessingStatus), nullable=False, default=ProcessingStatus.QUEUED, index=True)
    priority = Column(SQLEnum(ProcessingPriority), nullable=False, default=ProcessingPriority.NORMAL, index=True)
    
    # Processing configuration
    input_format = Column(String(50))
    output_format = Column(SQLEnum(OutputFormat), nullable=False)
    quality_level = Column(SQLEnum(QualityLevel), nullable=False, default=QualityLevel.STANDARD)
    compression_algorithm = Column(SQLEnum(CompressionAlgorithm))
    processing_parameters = Column(JSONB, default=dict)  # Custom processing parameters
    
    # Resource allocation
    cpu_cores_allocated = Column(Integer, default=1)
    memory_allocated_mb = Column(Integer, default=1024)
    gpu_allocated = Column(Boolean, default=False)
    gpu_model = Column(String(100))
    processing_node = Column(String(200))  # Processing server/node
    container_id = Column(String(200))     # Docker container ID
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    current_step = Column(String(200))
    total_steps = Column(Integer, default=1)
    completed_steps = Column(Integer, default=0)
    estimated_completion_time = Column(DateTime(timezone=True))
    
    # Performance metrics
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    processing_duration = Column(Float)    # seconds
    queue_wait_time = Column(Float)        # seconds in queue
    cpu_usage_percent = Column(Float, default=0.0)
    memory_usage_mb = Column(Float, default=0.0)
    gpu_usage_percent = Column(Float, default=0.0)
    
    # Input/Output specifications
    input_file_size = Column(Integer)      # bytes
    output_file_size = Column(Integer)     # bytes
    compression_ratio = Column(Float)      # output/input ratio
    processing_efficiency = Column(Float)  # performance score
    quality_improvement = Column(Float)    # quality delta
    
    # Quality control
    quality_metrics = Column(JSONB, default=dict)  # Quality assessment results
    quality_passed = Column(Boolean, default=True)
    quality_threshold = Column(Float, default=0.8)
    visual_artifacts = Column(JSONB, default=list)
    audio_artifacts = Column(JSONB, default=list)
    
    # Error handling
    error_count = Column(Integer, default=0)
    error_messages = Column(JSONB, default=list)
    warnings = Column(JSONB, default=list)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_error_timestamp = Column(DateTime(timezone=True))
    
    # Output management
    output_files = Column(JSONB, default=list)     # Generated output files
    output_urls = Column(JSONB, default=list)      # URLs to output files
    thumbnail_generated = Column(Boolean, default=False)
    preview_generated = Column(Boolean, default=False)
    metadata_updated = Column(Boolean, default=False)
    
    # Processing pipeline
    pipeline_id = Column(String(200))
    pipeline_stage = Column(Integer, default=1)
    dependent_jobs = Column(JSONB, default=list)   # Job dependencies
    parent_job_id = Column(UUID(as_uuid=True), ForeignKey('processing_jobs.id'))
    child_jobs = Column(JSONB, default=list)       # Child job IDs
    
    # Batch processing
    batch_id = Column(String(200))
    batch_size = Column(Integer, default=1)
    batch_position = Column(Integer, default=1)
    batch_completion_rate = Column(Float, default=0.0)
    
    # Cost tracking
    processing_cost = Column(Float, default=0.0)   # Cost in USD
    resource_cost = Column(Float, default=0.0)     # Resource usage cost
    storage_cost = Column(Float, default=0.0)      # Storage cost
    bandwidth_cost = Column(Float, default=0.0)    # Bandwidth cost
    total_cost = Column(Float, default=0.0)        # Total cost
    
    # Optimization features
    auto_optimization = Column(Boolean, default=True)
    optimization_applied = Column(JSONB, default=list)
    optimization_savings = Column(JSONB, default=dict)  # File size, quality, cost savings
    ai_optimization = Column(Boolean, default=False)
    ai_model_used = Column(String(200))
    
    # Monitoring & Alerts
    monitoring_enabled = Column(Boolean, default=True)
    alert_thresholds = Column(JSONB, default=dict)
    alerts_triggered = Column(JSONB, default=list)
    notification_sent = Column(Boolean, default=False)
    escalation_triggered = Column(Boolean, default=False)
    
    # Scheduling
    scheduled_start = Column(DateTime(timezone=True))
    scheduling_priority = Column(Integer, default=5)  # 1-10 priority
    resource_requirements = Column(JSONB, default=dict)
    deadline = Column(DateTime(timezone=True))
    sla_requirement = Column(Integer)  # SLA in seconds
    
    # Analytics & Insights
    processing_analytics = Column(JSONB, default=dict)
    performance_insights = Column(JSONB, default=list)
    optimization_suggestions = Column(JSONB, default=list)
    benchmark_comparison = Column(JSONB, default=dict)
    
    # Compliance & Audit
    audit_trail = Column(JSONB, default=list)
    compliance_checked = Column(Boolean, default=True)
    data_residency = Column(String(100))  # Geographic data residency
    privacy_compliance = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    queued_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # System flags
    is_priority_job = Column(Boolean, default=False)
    is_test_job = Column(Boolean, default=False)
    is_reprocessing = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    multimedia_asset = relationship("MultimediaAssetModel", back_populates="processing_jobs_rel")
    user = relationship("UserModel", backref="processing_jobs")
    parent_job = relationship("ProcessingJobModel", remote_side=[id], backref="child_jobs_rel")
    quality_metrics_rel = relationship("QualityMetricsModel", back_populates="processing_job", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_job_asset_status', 'multimedia_asset_id', 'status'),
        Index('idx_job_user_priority', 'user_id', 'priority'),
        Index('idx_job_stage_created', 'processing_stage', 'created_at'),
        Index('idx_job_batch_position', 'batch_id', 'batch_position'),
    )
    
    def __repr__(self) -> None:
        return f"<ProcessingJobModel(id={self.id}, name='{self.job_name}', status={self.status.value})>"


# ============================================================================
# QUALITY METRICS MODELS
# ============================================================================

class QualityMetricsModel(Base):
    """
    Quality metrics model for multimedia quality assessment and monitoring.
    Comprehensive quality tracking with automated and manual assessment.
    """
    __tablename__ = 'quality_metrics'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    processing_job_id = Column(UUID(as_uuid=True), ForeignKey('processing_jobs.id'), nullable=False, index=True)
    multimedia_asset_id = Column(UUID(as_uuid=True), ForeignKey('multimedia_assets.id'), nullable=False, index=True)
    
    # Quality assessment details
    assessment_type = Column(String(100), nullable=False)  # "automated", "manual", "hybrid"
    assessment_version = Column(String(50), default="1.0")
    assessment_algorithm = Column(String(200))
    assessment_model = Column(String(200))  # AI model used for assessment
    
    # Overall quality scores
    overall_quality_score = Column(Float, nullable=False)  # 0-100 overall quality
    technical_quality_score = Column(Float)                # Technical quality (0-100)
    perceptual_quality_score = Column(Float)               # Perceptual quality (0-100)
    aesthetic_quality_score = Column(Float)                # Aesthetic quality (0-100)
    usability_score = Column(Float)                        # Usability score (0-100)
    
    # Video quality metrics
    video_quality_metrics = Column(JSONB, default=dict)
    psnr_score = Column(Float)              # Peak Signal-to-Noise Ratio
    ssim_score = Column(Float)              # Structural Similarity Index
    vmaf_score = Column(Float)              # Video Multimethod Assessment Fusion
    vqm_score = Column(Float)               # Video Quality Metric
    motion_smoothness = Column(Float)       # Motion smoothness assessment
    color_accuracy = Column(Float)          # Color reproduction accuracy
    sharpness_score = Column(Float)         # Image sharpness
    contrast_ratio = Column(Float)          # Contrast ratio
    
    # Audio quality metrics
    audio_quality_metrics = Column(JSONB, default=dict)
    snr_score = Column(Float)               # Signal-to-Noise Ratio
    thd_score = Column(Float)               # Total Harmonic Distortion
    dynamic_range = Column(Float)           # Dynamic range
    frequency_response = Column(JSONB, default=dict)  # Frequency response analysis
    loudness_lufs = Column(Float)           # Loudness in LUFS
    peak_level = Column(Float)              # Peak level
    stereo_balance = Column(Float)          # Stereo balance
    
    # Image quality metrics
    image_quality_metrics = Column(JSONB, default=dict)
    resolution_score = Column(Float)        # Resolution adequacy
    noise_level = Column(Float)             # Noise level assessment
    compression_artifacts = Column(Float)   # Compression artifacts detection
    edge_preservation = Column(Float)       # Edge preservation quality
    color_saturation = Column(Float)        # Color saturation level
    brightness_level = Column(Float)        # Brightness assessment
    exposure_quality = Column(Float)        # Exposure quality
    
    # Content analysis
    content_complexity = Column(Float)      # Content complexity score
    scene_changes = Column(Integer)         # Number of scene changes
    motion_intensity = Column(Float)        # Motion intensity level
    texture_detail = Column(Float)          # Texture detail level
    spatial_activity = Column(Float)        # Spatial activity measure
    temporal_activity = Column(Float)       # Temporal activity measure
    
    # Artifact detection
    blocking_artifacts = Column(Float)      # Blocking artifacts score
    ringing_artifacts = Column(Float)       # Ringing artifacts score
    blur_detection = Column(Float)          # Blur detection score
    noise_artifacts = Column(Float)         # Noise artifacts score
    color_bleeding = Column(Float)          # Color bleeding detection
    interlacing_artifacts = Column(Float)   # Interlacing artifacts
    
    # Encoding efficiency
    compression_efficiency = Column(Float)  # Compression efficiency score
    bitrate_efficiency = Column(Float)      # Bitrate utilization efficiency
    file_size_score = Column(Float)         # File size optimization score
    encoding_speed = Column(Float)          # Encoding speed score
    
    # Platform compliance
    platform_compliance = Column(JSONB, default=dict)  # Platform-specific compliance
    format_compatibility = Column(Float)    # Format compatibility score
    streaming_readiness = Column(Float)     # Streaming optimization score
    mobile_optimization = Column(Float)     # Mobile optimization score
    web_optimization = Column(Float)        # Web optimization score
    
    # User experience metrics
    loading_time_score = Column(Float)      # Loading time assessment
    buffering_potential = Column(Float)     # Buffering likelihood
    seek_performance = Column(Float)        # Seek operation performance
    startup_time = Column(Float)            # Initial startup time
    
    # Accessibility metrics
    accessibility_score = Column(Float)     # Accessibility compliance
    subtitle_quality = Column(Float)        # Subtitle quality (if present)
    audio_description = Column(Float)       # Audio description quality
    contrast_accessibility = Column(Float)  # Visual contrast for accessibility
    
    # AI enhancement potential
    enhancement_potential = Column(Float)   # Potential for AI enhancement
    upscaling_benefit = Column(Float)       # Benefit from upscaling
    denoising_benefit = Column(Float)       # Benefit from denoising
    color_correction_benefit = Column(Float) # Benefit from color correction
    stabilization_benefit = Column(Float)   # Benefit from stabilization
    
    # Quality trends
    quality_trend = Column(String(20))      # "improving", "stable", "degrading"
    historical_comparison = Column(JSONB, default=dict)  # Comparison with previous versions
    benchmark_comparison = Column(JSONB, default=dict)   # Industry benchmark comparison
    
    # Assessment context
    assessment_timestamp = Column(DateTime(timezone=True), nullable=False)
    assessment_duration = Column(Float)     # Time taken for assessment
    sample_count = Column(Integer)          # Number of samples analyzed
    confidence_level = Column(Float)        # Confidence in assessment (0-1)
    
    # Human validation
    human_validated = Column(Boolean, default=False)
    human_score = Column(Float)             # Human assessor score
    human_feedback = Column(Text)           # Human feedback
    human_assessor_id = Column(String(200)) # ID of human assessor
    validation_timestamp = Column(DateTime(timezone=True))
    
    # Recommendations
    quality_recommendations = Column(JSONB, default=list)  # Quality improvement recommendations
    optimization_suggestions = Column(JSONB, default=list)  # Optimization suggestions
    processing_adjustments = Column(JSONB, default=list)    # Suggested processing adjustments
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # System flags
    is_final_assessment = Column(Boolean, default=True)
    is_automated = Column(Boolean, default=True)
    is_validated = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    processing_job = relationship("ProcessingJobModel", back_populates="quality_metrics_rel")
    multimedia_asset = relationship("MultimediaAssetModel", backref="quality_assessments")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_quality_job_asset', 'processing_job_id', 'multimedia_asset_id'),
        Index('idx_quality_score_timestamp', 'overall_quality_score', 'assessment_timestamp'),
        Index('idx_quality_type_validated', 'assessment_type', 'is_validated'),
    )
    
    def __repr__(self) -> None:
        return f"<QualityMetricsModel(id={self.id}, score={self.overall_quality_score:.1f}, type={self.assessment_type})>"


# ============================================================================
# COMPRESSION MODELS
# ============================================================================

class CompressionModel(Base):
    """
    Compression model for multimedia compression tracking and optimization.
    Advanced compression management with algorithm comparison and optimization.
    """
    __tablename__ = 'compression'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    multimedia_asset_id = Column(UUID(as_uuid=True), ForeignKey('multimedia_assets.id'), nullable=False, index=True)
    processing_job_id = Column(UUID(as_uuid=True), ForeignKey('processing_jobs.id'), nullable=True, index=True)
    
    # Compression details
    compression_algorithm = Column(SQLEnum(CompressionAlgorithm), nullable=False, index=True)
    compression_preset = Column(String(100))  # "ultrafast", "fast", "medium", "slow", "veryslow"
    compression_level = Column(Integer)        # 1-10 compression level
    quality_target = Column(Float)             # Target quality (0-1)
    bitrate_target = Column(Integer)           # Target bitrate
    
    # File size metrics
    original_size_bytes = Column(Integer, nullable=False)
    compressed_size_bytes = Column(Integer, nullable=False)
    compression_ratio = Column(Float, nullable=False)  # compressed/original
    size_reduction_percentage = Column(Float, nullable=False)  # Percentage saved
    
    # Quality impact
    quality_before = Column(Float)             # Quality before compression
    quality_after = Column(Float)              # Quality after compression
    quality_loss = Column(Float)               # Quality degradation
    perceptual_quality_loss = Column(Float)    # Perceptual quality loss
    acceptable_quality = Column(Boolean, default=True)  # Is quality acceptable?
    
    # Performance metrics
    compression_time = Column(Float)           # Time to compress (seconds)
    compression_speed = Column(Float)          # MB/s compression speed
    cpu_usage_during_compression = Column(Float)  # CPU usage percentage
    memory_usage_during_compression = Column(Float)  # Memory usage MB
    
    # Algorithm-specific settings
    encoder_settings = Column(JSONB, default=dict)  # Encoder-specific settings
    codec_parameters = Column(JSONB, default=dict)  # Codec parameters
    optimization_flags = Column(JSONB, default=list)  # Optimization flags used
    
    # Video compression specifics
    video_codec = Column(String(50))           # Video codec used
    video_bitrate = Column(Integer)            # Video bitrate
    keyframe_interval = Column(Integer)        # Keyframe interval
    b_frames = Column(Integer)                 # Number of B-frames
    reference_frames = Column(Integer)         # Reference frames
    encoding_passes = Column(Integer, default=1)  # Single or multi-pass
    
    # Audio compression specifics
    audio_codec = Column(String(50))           # Audio codec used
    audio_bitrate = Column(Integer)            # Audio bitrate
    audio_sample_rate = Column(Integer)        # Sample rate
    audio_channels = Column(Integer)           # Channel count
    audio_quality_mode = Column(String(50))    # VBR, CBR, ABR
    
    # Image compression specifics
    image_quality = Column(Integer)            # JPEG quality (1-100)
    progressive_encoding = Column(Boolean, default=False)  # Progressive JPEG
    chroma_subsampling = Column(String(20))    # "4:4:4", "4:2:2", "4:2:0"
    color_space_compression = Column(String(50))  # Color space used
    
    # Optimization results
    optimization_applied = Column(JSONB, default=list)  # Applied optimizations
    adaptive_compression = Column(Boolean, default=False)  # Adaptive compression used
    content_aware_compression = Column(Boolean, default=False)  # Content-aware compression
    region_of_interest = Column(JSONB, default=list)  # ROI for selective compression
    
    # Multi-format output
    multiple_qualities = Column(Boolean, default=False)  # Multiple quality outputs
    output_variants = Column(JSONB, default=list)  # Different quality variants
    adaptive_streaming_ready = Column(Boolean, default=False)  # HLS/DASH ready
    
    # Efficiency metrics
    bits_per_pixel = Column(Float)             # Bits per pixel (for images/video)
    compression_efficiency = Column(Float)     # Efficiency score (0-1)
    rate_distortion_score = Column(Float)      # Rate-distortion optimization score
    
    # Comparison with alternatives
    alternative_algorithms_tested = Column(JSONB, default=list)  # Other algorithms tested
    best_alternative = Column(String(100))     # Best performing alternative
    improvement_over_default = Column(Float)   # Improvement over default settings
    
    # Platform optimization
    platform_optimized_for = Column(JSONB, default=list)  # Platforms optimized for
    streaming_optimization = Column(Boolean, default=False)  # Streaming optimized
    mobile_optimization = Column(Boolean, default=False)  # Mobile optimized
    web_optimization = Column(Boolean, default=False)  # Web optimized
    
    # Cost analysis
    processing_cost = Column(Float, default=0.0)  # Cost to process
    storage_savings = Column(Float, default=0.0)  # Storage cost savings
    bandwidth_savings = Column(Float, default=0.0)  # Bandwidth cost savings
    total_savings = Column(Float, default=0.0)  # Total cost savings
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    compression_started_at = Column(DateTime(timezone=True))
    compression_completed_at = Column(DateTime(timezone=True))
    
    # System flags
    is_optimal_compression = Column(Boolean, default=False)  # Is this the optimal compression?
    is_lossless = Column(Boolean, default=False)
    is_experimental = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    multimedia_asset = relationship("MultimediaAssetModel", backref="compression_records")
    processing_job = relationship("ProcessingJobModel", backref="compression_records")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_compression_asset_algorithm', 'multimedia_asset_id', 'compression_algorithm'),
        Index('idx_compression_ratio_quality', 'compression_ratio', 'quality_after'),
        Index('idx_compression_optimal_created', 'is_optimal_compression', 'created_at'),
    )
    
    def __repr__(self) -> None:
        return f"<CompressionModel(id={self.id}, algorithm={self.compression_algorithm.value}, ratio={self.compression_ratio:.2f})>"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_multimedia_asset_example(content_id: str, user_id: str, 
                                   media_type: MediaType = MediaType.VIDEO) -> MultimediaAssetModel:
    """Create example multimedia asset for testing and development"""
    return MultimediaAssetModel(
        content_id=content_id,
        user_id=user_id,
        media_type=media_type,
        asset_name=f"Sample {media_type.value.title()} Asset",
        asset_description="This is a sample multimedia asset for testing purposes",
        file_extension="mp4" if media_type == MediaType.VIDEO else "mp3",
        mime_type="video/mp4" if media_type == MediaType.VIDEO else "audio/mpeg",
        file_size_bytes=10485760,  # 10MB
        file_hash="abc123def456",
        storage_path="/storage/sample/file.mp4"
    )


def create_processing_job_example(multimedia_asset_id: str, user_id: str) -> ProcessingJobModel:
    """Create example processing job for testing and development"""
    return ProcessingJobModel(
        multimedia_asset_id=multimedia_asset_id,
        user_id=user_id,
        job_name="Sample Video Compression Job",
        job_type="compression",
        processing_stage=ProcessingStage.COMPRESSION,
        output_format=OutputFormat.MP4,
        quality_level=QualityLevel.HIGH,
        compression_algorithm=CompressionAlgorithm.H264,
        cpu_cores_allocated=2,
        memory_allocated_mb=2048
    )


def estimate_processing_time(file_size_mb: float, media_type: MediaType, 
                           quality_level: QualityLevel = QualityLevel.STANDARD) -> float:
    """Estimate processing time in seconds based on file characteristics"""
    # Base processing speeds (MB/s) by media type
    base_speeds = {
        MediaType.VIDEO: 0.5,      # Video is slower to process
        MediaType.AUDIO: 2.0,      # Audio is faster
        MediaType.IMAGE: 5.0,      # Images are fastest
        MediaType.DOCUMENT: 3.0    # Documents are moderately fast
    }
    
    # Quality level multipliers
    quality_multipliers = {
        QualityLevel.LOW: 0.5,
        QualityLevel.STANDARD: 1.0,
        QualityLevel.HIGH: 2.0,
        QualityLevel.ULTRA: 4.0,
        QualityLevel.LOSSLESS: 6.0
    }
    
    base_speed = base_speeds.get(media_type, 1.0)
    quality_multiplier = quality_multipliers.get(quality_level, 1.0)
    
    processing_time = file_size_mb / (base_speed / quality_multiplier)
    
    # Add overhead for setup and finalization (20% of processing time)
    total_time = processing_time * 1.2
    
    return round(total_time, 2)


def calculate_optimal_compression(file_size_bytes: int, target_quality: float = 0.9, 
                                target_size_reduction: float = 0.5) -> Dict[str, Any]:
    """Calculate optimal compression settings"""
    # Calculate target file size
    target_size = file_size_bytes * (1 - target_size_reduction)
    
    # Estimate compression ratio needed
    compression_ratio = target_size / file_size_bytes
    
    # Suggest compression algorithm based on requirements
    if target_quality >= 0.95:
        algorithm = CompressionAlgorithm.H265_HEVC  # Best quality preservation
        quality_level = QualityLevel.ULTRA
    elif target_quality >= 0.8:
        algorithm = CompressionAlgorithm.H264       # Good balance
        quality_level = QualityLevel.HIGH
    else:
        algorithm = CompressionAlgorithm.VP9        # Higher compression
        quality_level = QualityLevel.STANDARD
    
    return {
        "recommended_algorithm": algorithm,
        "recommended_quality": quality_level,
        "target_compression_ratio": compression_ratio,
        "target_file_size": target_size,
        "estimated_quality_loss": 1 - target_quality,
        "size_reduction_percentage": target_size_reduction * 100
    }


def generate_quality_report(quality_metrics: QualityMetricsModel) -> Dict[str, Any]:
    """Generate comprehensive quality report"""
    report = {
        "overall_score": quality_metrics.overall_quality_score,
        "grade": get_quality_grade(quality_metrics.overall_quality_score),
        "strengths": [],
        "weaknesses": [],
        "recommendations": []
    }
    
    # Analyze strengths and weaknesses
    if quality_metrics.technical_quality_score and quality_metrics.technical_quality_score >= 80:
        report["strengths"].append("Excellent technical quality")
    elif quality_metrics.technical_quality_score and quality_metrics.technical_quality_score < 60:
        report["weaknesses"].append("Poor technical quality")
        report["recommendations"].append("Consider reprocessing with higher quality settings")
    
    if quality_metrics.compression_efficiency and quality_metrics.compression_efficiency >= 0.8:
        report["strengths"].append("Efficient compression")
    elif quality_metrics.compression_efficiency and quality_metrics.compression_efficiency < 0.5:
        report["weaknesses"].append("Inefficient compression")
        report["recommendations"].append("Try alternative compression algorithms")
    
    return report


def get_quality_grade(score: float) -> str:
    """Convert quality score to letter grade"""
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "B+"
    elif score >= 75:
        return "B"
    elif score >= 70:
        return "C+"
    elif score >= 65:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


# ============================================================================
# EXPORT SECTION
# ============================================================================

__all__ = [
    # Models
    'MultimediaAssetModel', 'ProcessingJobModel', 'QualityMetricsModel', 'CompressionModel',
    
    # Media Processing Enums
    'MediaType', 'ProcessingStage', 'QualityLevel', 'CompressionAlgorithm', 
    'ProcessingStatus', 'OutputFormat', 'ProcessingPriority',
    
    # Utility Functions
    'create_multimedia_asset_example', 'create_processing_job_example',
    'estimate_processing_time', 'calculate_optimal_compression', 
    'generate_quality_report', 'get_quality_grade'
]