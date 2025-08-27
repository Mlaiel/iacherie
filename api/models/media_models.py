"""
IA Influencer Agent Platform - Media Models
Advanced media file management with processing and analysis capabilities

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Engineer + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected by copyright law and intellectual property rights.
Any unauthorized use, reproduction, copying, distribution, or commercial exploitation 
without explicit written permission from Fahed Mlaiel is strictly prohibited and 
will result in legal action.

Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, Numeric,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from .base import (
    BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin,
    AuditMixin, MetadataMixin, StatusMixin
)


class MediaFile(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin):
    """Core media file model for all file types"""
    
    __tablename__ = 'media_files'
    
    content_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('contents.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # File Information
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    file_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    # File Properties
    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # audio, video, image, document
    
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    file_extension: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True
    )
    
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )  # Size in bytes
    
    # Checksums and Integrity
    md5_hash: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True
    )
    
    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True
    )
    
    crc32_checksum: Mapped[Optional[str]] = mapped_column(
        String(8),
        nullable=True
    )
    
    # Storage Information
    storage_provider: Mapped[str] = mapped_column(
        String(50),
        default='local',
        nullable=False
    )  # local, aws_s3, gcp_storage, azure_blob
    
    storage_bucket: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    storage_region: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    storage_class: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )  # standard, cold, archive
    
    # Media Properties
    duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # Duration in seconds for audio/video
    
    width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # Width in pixels for images/video
    
    height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # Height in pixels for images/video
    
    bitrate: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # Bitrate for audio/video
    
    # Processing Status
    is_processed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    processing_status: Mapped[str] = mapped_column(
        String(50),
        default='pending',
        nullable=False,
        index=True
    )  # pending, processing, completed, failed
    
    # Quality and Versions
    quality_level: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )  # original, high, medium, low, thumbnail
    
    is_original: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    parent_file_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('media_files.id'),
        nullable=True,
        index=True
    )
    
    # Access Control
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    access_url_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Relationships
    processing_jobs: Mapped[List["MediaProcessing"]] = relationship(
        "MediaProcessing",
        back_populates="media_file",
        cascade="all, delete-orphan"
    )
    
    transforms: Mapped[List["MediaTransform"]] = relationship(
        "MediaTransform",
        back_populates="media_file",
        cascade="all, delete-orphan"
    )
    
    analysis: Mapped[Optional["MediaAnalysis"]] = relationship(
        "MediaAnalysis",
        back_populates="media_file",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    child_files: Mapped[List["MediaFile"]] = relationship(
        "MediaFile",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_media_content_type', 'content_id', 'file_type'),
        Index('idx_media_size_created', 'file_size', 'created_at'),
        Index('idx_media_processing_status', 'processing_status', 'is_processed'),
        Index('idx_media_storage', 'storage_provider', 'storage_bucket'),
        CheckConstraint('file_size >= 0', name='positive_file_size'),
        CheckConstraint('duration >= 0 OR duration IS NULL', name='positive_duration'),
        CheckConstraint('width >= 0 OR width IS NULL', name='positive_width'),
        CheckConstraint('height >= 0 OR height IS NULL', name='positive_height'),
    )


class MediaProcessing(BaseModel, UUIDMixin, TimestampMixin, StatusMixin):
    """Media processing jobs and pipeline management"""
    
    __tablename__ = 'media_processing'
    
    media_file_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('media_files.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Job Information
    job_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # transcode, thumbnail, watermark, analysis, fingerprint
    
    job_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    job_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Processing Configuration
    input_parameters: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    output_parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    processing_options: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True
    )
    
    # Execution Details
    processor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # ffmpeg, opencv, pillow, custom
    
    processor_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Status and Progress
    progress_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Results and Output
    output_files: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    processing_log: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Performance Metrics
    processing_time_seconds: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 3),
        nullable=True
    )
    
    cpu_usage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )
    
    memory_usage: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # Memory usage in MB
    
    # Queue and Priority
    queue_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    priority: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False
    )  # 1-10, higher number = higher priority
    
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False
    )
    
    # Relationships
    media_file: Mapped["MediaFile"] = relationship(
        "MediaFile",
        back_populates="processing_jobs"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_processing_job_type_status', 'job_type', 'status'),
        Index('idx_processing_started_completed', 'started_at', 'completed_at'),
        Index('idx_processing_priority', 'priority', 'created_at'),
        CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='valid_progress'),
        CheckConstraint('priority >= 1 AND priority <= 10', name='valid_priority'),
    )


class MediaTransform(BaseModel, UUIDMixin, TimestampMixin, AuditMixin):
    """Media transformation and conversion records"""
    
    __tablename__ = 'media_transforms'
    
    media_file_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('media_files.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Transform Information
    transform_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # resize, crop, rotate, filter, format_conversion
    
    transform_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    # Input and Output
    source_format: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    target_format: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    source_properties: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    target_properties: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    # Transformation Parameters
    transform_parameters: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    quality_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Results
    output_file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    output_file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    compression_ratio: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    quality_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Status
    is_successful: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    error_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    media_file: Mapped["MediaFile"] = relationship(
        "MediaFile",
        back_populates="transforms"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_transforms_type_success', 'transform_type', 'is_successful'),
        Index('idx_transforms_formats', 'source_format', 'target_format'),
    )


class MediaAnalysis(BaseModel, UUIDMixin, TimestampMixin):
    """AI-powered media analysis and insights"""
    
    __tablename__ = 'media_analysis'
    
    media_file_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('media_files.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Analysis Types
    analysis_types: Mapped[List[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=False
    )  # content_recognition, sentiment, quality, similarity
    
    # Audio Analysis
    audio_features: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # tempo, key, mood, genre predictions
    
    audio_quality_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Image/Video Analysis
    visual_features: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # objects, faces, scenes, colors
    
    visual_quality_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Content Recognition
    detected_objects: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    detected_faces: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    detected_text: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Content Safety and Moderation
    content_safety_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    safety_categories: Mapped[Optional[Dict[str, Decimal]]] = mapped_column(
        JSONB,
        nullable=True
    )  # adult, violence, hate, etc. with confidence scores
    
    moderation_flags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(50)),
        nullable=True
    )
    
    # Sentiment and Emotion
    sentiment_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    emotion_scores: Mapped[Optional[Dict[str, Decimal]]] = mapped_column(
        JSONB,
        nullable=True
    )  # joy, sadness, anger, etc.
    
    # Technical Quality
    technical_quality: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # noise, blur, exposure, etc.
    
    # AI Model Information
    models_used: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False
    )  # Model names, versions, confidence scores
    
    # Analysis Metadata
    analysis_duration: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 3),
        nullable=True
    )  # Analysis time in seconds
    
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Custom Analysis Results
    custom_analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Relationships
    media_file: Mapped["MediaFile"] = relationship(
        "MediaFile",
        back_populates="analysis"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_analysis_quality_scores', 'audio_quality_score', 'visual_quality_score'),
        Index('idx_analysis_safety', 'content_safety_score'),
        Index('idx_analysis_confidence', 'confidence_score'),
    )
