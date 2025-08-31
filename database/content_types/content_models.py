"""Content Models Module - Professional Database Models for Content Management

Module définissant les modèles de base de données pour la gestion complète
du contenu multimédia dans la plateforme IA Influencer Agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Database Architect, ORM Specialist, Content Management Expert
Copyright: Fahed Mlaiel - All rights reserved
"""from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid
import json
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, LargeBinary,
    ForeignKey, Table, Index, UniqueConstraint, CheckConstraint,
    JSON, ARRAY, Enum as SQLEnum, BigInteger, SmallInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

Base = declarative_base()

# Content classification enums
class ContentStatus(Enum):
    """Content processing and publication status"""    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"

class ContentType(Enum):
    """Primary content type categories"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTIMEDIA = "multimedia"
    DOCUMENT = "document"
    ARCHIVE = "archive"

class ContentFormat(Enum):
    """Specific content format subcategories"""    # Audio formats
    AUDIO_MP3 = "audio/mp3"
    AUDIO_WAV = "audio/wav"
    AUDIO_FLAC = "audio/flac"
    AUDIO_AAC = "audio/aac"
    AUDIO_OGG = "audio/ogg"
    
    # Video formats
    VIDEO_MP4 = "video/mp4"
    VIDEO_AVI = "video/avi"
    VIDEO_MOV = "video/mov"
    VIDEO_WEBM = "video/webm"
    VIDEO_MKV = "video/mkv"
    
    # Image formats
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_TIFF = "image/tiff"
    IMAGE_WEBP = "image/webp"
    IMAGE_GIF = "image/gif"
    
    # Text formats
    TEXT_PLAIN = "text/plain"
    TEXT_MARKDOWN = "text/markdown"
    TEXT_HTML = "text/html"
    TEXT_PDF = "application/pdf"
    TEXT_DOCX = "application/docx"

class ProtectionLevel(Enum):
    """Content protection and security levels"""    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class QualityLevel(Enum):
    """Content quality assessment levels"""    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROFESSIONAL = "professional"
    BROADCAST = "broadcast"

class ContentOrigin(Enum):
    """Content origin and source classification"""    USER_UPLOAD = "user_upload"
    AI_GENERATED = "ai_generated"
    IMPORTED = "imported"
    COLLABORATION = "collaboration"
    REMIX = "remix"
    DERIVATIVE = "derivative"
    ORIGINAL = "original"

class ProcessingStatus(Enum):
    """Content processing pipeline status"""    PENDING = "pending"
    IN_QUEUE = "in_queue"
    ANALYZING = "analyzing"
    FINGERPRINTING = "fingerprinting"
    PROTECTING = "protecting"
    OPTIMIZING = "optimizing"
    DISTRIBUTING = "distributing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

class MonetizationStatus(Enum):
    """Content monetization status"""    DISABLED = "disabled"
    ENABLED = "enabled"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    EARNING = "earning"

class DistributionStatus(Enum):
    """Content distribution status across platforms"""    NOT_DISTRIBUTED = "not_distributed"
    PENDING_DISTRIBUTION = "pending_distribution"
    DISTRIBUTED = "distributed"
    DISTRIBUTION_FAILED = "distribution_failed"
    PARTIALLY_DISTRIBUTED = "partially_distributed"
    REMOVED = "removed"

# Association tables for many-to-many relationships
content_tags_association = Table(
    'content_tags',
    Base.metadata,
    Column('content_id', UUID(as_uuid=True), ForeignKey('contents.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('content_tags_lookup.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), default=func.now()),
    Index('idx_content_tags_content', 'content_id'),
    Index('idx_content_tags_tag', 'tag_id')
)

content_categories_association = Table(
    'content_categories',
    Base.metadata,
    Column('content_id', UUID(as_uuid=True), ForeignKey('contents.id'), primary_key=True),
    Column('category_id', UUID(as_uuid=True), ForeignKey('content_categories_lookup.id'), primary_key=True),
    Column('relevance_score', Float, default=1.0),
    Column('created_at', DateTime(timezone=True), default=func.now()),
    Index('idx_content_categories_content', 'content_id'),
    Index('idx_content_categories_category', 'category_id')
)

content_relationships_association = Table(
    'content_relationships',
    Base.metadata,
    Column('parent_content_id', UUID(as_uuid=True), ForeignKey('contents.id'), primary_key=True),
    Column('child_content_id', UUID(as_uuid=True), ForeignKey('contents.id'), primary_key=True),
    Column('relationship_type', String(50), nullable=False),
    Column('relationship_strength', Float, default=1.0),
    Column('created_at', DateTime(timezone=True), default=func.now()),
    Index('idx_content_rel_parent', 'parent_content_id'),
    Index('idx_content_rel_child', 'child_content_id'),
    Index('idx_content_rel_type', 'relationship_type')
)

class ContentTagsLookup(Base):
    """Lookup table for content tags"""    __tablename__ = 'content_tags_lookup'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50))
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_tags_name', 'name'),
        Index('idx_tags_category', 'category'),
        Index('idx_tags_usage', 'usage_count'),
    )

class ContentCategoriesLookup(Base):
    """Lookup table for content categories"""    __tablename__ = 'content_categories_lookup'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey('content_categories_lookup.id'))
    hierarchy_level = Column(SmallInteger, default=0)
    content_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Self-referential relationship for hierarchical categories
    subcategories = relationship("ContentCategoriesLookup", backref=backref('parent_category', remote_side=[id]))
    
    # Indexes
    __table_args__ = (
        Index('idx_categories_name', 'name'),
        Index('idx_categories_parent', 'parent_category_id'),
        Index('idx_categories_level', 'hierarchy_level'),
    )

class ContentSource(Base):
    """Content source and origin tracking"""    __tablename__ = 'content_sources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    source_type = Column(String(50), nullable=False)  # upload, crawl, api, import, etc.
    source_url = Column(Text)
    source_platform = Column(String(100))
    api_endpoint = Column(Text)
    authentication_method = Column(String(50))
    rate_limit_info = Column(JSONB)
    last_accessed = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    configuration = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_sources_type', 'source_type'),
        Index('idx_sources_platform', 'source_platform'),
        Index('idx_sources_active', 'is_active'),
    )

class ContentMetadata(Base):
    """Extended metadata for content items"""    __tablename__ = 'content_metadata'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('contents.id'), nullable=False, unique=True)
    
    # Technical metadata
    file_size_bytes = Column(BigInteger)
    duration_seconds = Column(Float)
    frame_rate = Column(Float)
    bit_rate = Column(Integer)
    sample_rate = Column(Integer)
    channels = Column(SmallInteger)
    resolution_width = Column(Integer)
    resolution_height = Column(Integer)
    color_depth = Column(SmallInteger)
    compression_ratio = Column(Float)
    
    # Quality metrics
    quality_score = Column(Float, CheckConstraint('quality_score >= 0 AND quality_score <= 1'))
    sharpness_score = Column(Float)
    noise_level = Column(Float)
    dynamic_range = Column(Float)
    color_accuracy = Column(Float)
    exposure_quality = Column(Float)
    
    # Content analysis
    face_count = Column(SmallInteger, default=0)
    object_count = Column(SmallInteger, default=0)
    scene_count = Column(SmallInteger, default=0)
    text_density = Column(Float)
    motion_intensity = Column(Float)
    audio_energy = Column(Float)
    
    # Descriptive metadata
    title = Column(String(500))
    description = Column(Text)
    keywords = Column(ARRAY(String(100)))
    language_code = Column(String(10))
    country_code = Column(String(10))
    cultural_context = Column(String(100))
    
    # Content creation metadata
    creation_software = Column(String(200))
    creation_software_version = Column(String(50))
    camera_make = Column(String(100))
    camera_model = Column(String(100))
    lens_info = Column(String(200))
    location_latitude = Column(Float)
    location_longitude = Column(Float)
    location_name = Column(String(200))
    
    # Rights and licensing
    copyright_holder = Column(String(200))
    license_type = Column(String(100))
    usage_rights = Column(Text)
    attribution_required = Column(Boolean, default=False)
    commercial_use_allowed = Column(Boolean, default=False)
    modification_allowed = Column(Boolean, default=False)
    
    # Advanced metadata
    ai_generated = Column(Boolean, default=False)
    ai_model_used = Column(String(200))
    deepfake_probability = Column(Float)
    authenticity_score = Column(Float)
    sentiment_score = Column(Float)
    emotion_analysis = Column(JSONB)
    
    # Custom metadata fields
    custom_metadata = Column(JSONB)
    processing_metadata = Column(JSONB)
    analytics_metadata = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationship
    content = relationship("Content", back_populates="metadata")
    
    # Indexes
    __table_args__ = (
        Index('idx_metadata_content', 'content_id'),
        Index('idx_metadata_quality', 'quality_score'),
        Index('idx_metadata_language', 'language_code'),
        Index('idx_metadata_location', 'location_latitude', 'location_longitude'),
        Index('idx_metadata_ai_generated', 'ai_generated'),
        Index('idx_metadata_title_gin', 'title', postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'}),
        Index('idx_metadata_keywords_gin', 'keywords', postgresql_using='gin'),
    )

class ContentFingerprint(Base):
    """Content fingerprinting for duplicate detection and protection"""    __tablename__ = 'content_fingerprints'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('contents.id'), nullable=False, unique=True)
    
    # Primary hashes
    md5_hash = Column(String(32), nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    xxhash = Column(String(16))
    
    # Perceptual hashes
    perceptual_hash = Column(String(64))
    difference_hash = Column(String(64))
    average_hash = Column(String(64))
    wavelet_hash = Column(String(64))
    
    # Audio fingerprints
    chromaprint = Column(Text)
    acoustic_fingerprint = Column(LargeBinary)
    spectral_centroid = Column(ARRAY(Float))
    mfcc_features = Column(LargeBinary)
    
    # Video fingerprints
    temporal_fingerprint = Column(LargeBinary)
    keyframe_hashes = Column(ARRAY(String(64)))
    motion_fingerprint = Column(LargeBinary)
    
    # Text fingerprints
    simhash = Column(String(64))
    minhash = Column(LargeBinary)
    tfidf_signature = Column(LargeBinary)
    semantic_hash = Column(String(64))
    
    # Advanced fingerprints
    feature_vector = Column(LargeBinary)
    neural_embedding = Column(LargeBinary)
    structural_hash = Column(String(64))
    
    # Fingerprint metadata
    fingerprint_version = Column(String(20), default="1.0")
    algorithm_used = Column(String(100))
    confidence_score = Column(Float, CheckConstraint('confidence_score >= 0 AND confidence_score <= 1'))
    quality_indicators = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationship
    content = relationship("Content", back_populates="fingerprint")
    
    # Indexes for fast similarity searches
    __table_args__ = (
        Index('idx_fingerprint_content', 'content_id'),
        Index('idx_fingerprint_md5', 'md5_hash'),
        Index('idx_fingerprint_sha256', 'sha256_hash'),
        Index('idx_fingerprint_perceptual', 'perceptual_hash'),
        Index('idx_fingerprint_confidence', 'confidence_score'),
        Index('idx_fingerprint_version', 'fingerprint_version'),
    )

class ContentProcessingJob(Base):
    """Track content processing jobs and their status"""    __tablename__ = 'content_processing_jobs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('contents.id'), nullable=False)
    job_type = Column(String(50), nullable=False)  # analysis, transcription, thumbnail, etc.
    job_status = Column(String(20), nullable=False, default='pending')  # pending, running, completed, failed
    priority = Column(SmallInteger, default=5)  # 1-10, lower is higher priority
    
    # Processing details
    processor_name = Column(String(100))
    processor_version = Column(String(20))
    processing_parameters = Column(JSONB)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    
    # Progress tracking
    progress_percentage = Column(SmallInteger, default=0, CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100'))
    current_step = Column(String(100))
    total_steps = Column(SmallInteger)
    estimated_completion = Column(DateTime(timezone=True))
    
    # Resource usage
    cpu_usage = Column(Float)
    memory_usage_mb = Column(Integer)
    processing_duration_ms = Column(BigInteger)
    
    # Error handling
    error_message = Column(Text)
    error_code = Column(String(50))
    retry_count = Column(SmallInteger, default=0)
    max_retries = Column(SmallInteger, default=3)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationship
    content = relationship("Content", back_populates="processing_jobs")
    
    # Indexes
    __table_args__ = (
        Index('idx_processing_content', 'content_id'),
        Index('idx_processing_status', 'job_status'),
        Index('idx_processing_type', 'job_type'),
        Index('idx_processing_priority', 'priority'),
        Index('idx_processing_created', 'created_at'),
    )

class ContentVersionHistory(Base):
    """Track content version history and changes"""    __tablename__ = 'content_version_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('contents.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    version_label = Column(String(100))
    
    # Change tracking
    change_type = Column(String(50), nullable=False)  # create, update, delete, restore
    change_description = Column(Text)
    changed_fields = Column(ARRAY(String(100)))
    change_summary = Column(JSONB)
    
    # Previous state
    previous_file_path = Column(Text)
    previous_metadata = Column(JSONB)
    previous_fingerprint = Column(JSONB)
    
    # Change context
    changed_by_user_id = Column(UUID(as_uuid=True))
    changed_by_system = Column(String(100))
    change_reason = Column(String(200))
    change_source = Column(String(100))  # user, system, api, migration
    
    # File information
    file_size_change = Column(BigInteger)
    content_hash_previous = Column(String(64))
    content_hash_current = Column(String(64))
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationship
    content = relationship("Content", back_populates="version_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_version_content', 'content_id'),
        Index('idx_version_number', 'content_id', 'version_number'),
        Index('idx_version_type', 'change_type'),
        Index('idx_version_created', 'created_at'),
        UniqueConstraint('content_id', 'version_number', name='uq_content_version'),
    )

class Content(Base):
    """Main content table with comprehensive content management"""    __tablename__ = 'contents'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_hash = Column(String(64), nullable=False, unique=True)
    
    # Content classification
    content_type = Column(SQLEnum(ContentType), nullable=False)
    content_format = Column(SQLEnum(ContentFormat), nullable=False)
    content_subtype = Column(String(100))
    
    # File information
    original_filename = Column(String(500), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(200))
    file_extension = Column(String(20))
    
    # Content status and lifecycle
    status = Column(SQLEnum(ContentStatus), nullable=False, default=ContentStatus.UPLOADED)
    protection_level = Column(SQLEnum(ProtectionLevel), nullable=False, default=ProtectionLevel.PROTECTED)
    quality_level = Column(SQLEnum(QualityLevel), default=QualityLevel.UNKNOWN)
    
    # Content source and origin
    source_id = Column(UUID(as_uuid=True), ForeignKey('content_sources.id'))
    source_url = Column(Text)
    source_platform = Column(String(100))
    source_reference_id = Column(String(200))
    
    # Processing information
    processing_version = Column(String(20), default="1.0")
    last_processed_at = Column(DateTime(timezone=True))
    processing_duration_ms = Column(BigInteger)
    
    # Content metrics
    view_count = Column(BigInteger, default=0)
    download_count = Column(BigInteger, default=0)
    share_count = Column(BigInteger, default=0)
    rating_average = Column(Float, CheckConstraint('rating_average >= 0 AND rating_average <= 5'))
    rating_count = Column(Integer, default=0)
    
    # Content dates
    content_created_at = Column(DateTime(timezone=True))  # Original creation date
    content_published_at = Column(DateTime(timezone=True))  # Original publication date
    uploaded_at = Column(DateTime(timezone=True), default=func.now())
    first_processed_at = Column(DateTime(timezone=True))
    last_accessed_at = Column(DateTime(timezone=True))
    
    # User and ownership
    uploaded_by_user_id = Column(UUID(as_uuid=True))
    owner_user_id = Column(UUID(as_uuid=True))
    creator_name = Column(String(200))
    copyright_holder = Column(String(200))
    
    # Content validation and security
    is_validated = Column(Boolean, default=False)
    validation_score = Column(Float, CheckConstraint('validation_score >= 0 AND validation_score <= 1'))
    security_scan_passed = Column(Boolean, default=False)
    content_warnings = Column(ARRAY(String(100)))
    age_rating = Column(String(20))
    
    # Search and discovery
    search_vector = Column(TSVECTOR)
    search_keywords = Column(ARRAY(String(100)))
    trending_score = Column(Float, default=0.0)
    recommendation_score = Column(Float, default=0.0)
    
    # System metadata
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))  # Soft delete
    
    # Current version tracking
    current_version = Column(Integer, default=1)
    is_current_version = Column(Boolean, default=True)
    
    # Additional metadata
    custom_fields = Column(JSONB)
    system_metadata = Column(JSONB)
    analytics_data = Column(JSONB)
    
    # Relationships
    source = relationship("ContentSource", backref="contents")
    metadata = relationship("ContentMetadata", back_populates="content", uselist=False, cascade="all, delete-orphan")
    fingerprint = relationship("ContentFingerprint", back_populates="content", uselist=False, cascade="all, delete-orphan")
    processing_jobs = relationship("ContentProcessingJob", back_populates="content", cascade="all, delete-orphan")
    version_history = relationship("ContentVersionHistory", back_populates="content", cascade="all, delete-orphan")
    
    # Many-to-many relationships
    tags = relationship("ContentTagsLookup", secondary=content_tags_association, backref="contents")
    categories = relationship("ContentCategoriesLookup", secondary=content_categories_association, backref="contents")
    
    # Self-referential relationships for content connections
    related_contents = relationship(
        "Content",
        secondary=content_relationships_association,
        primaryjoin=id == content_relationships_association.c.parent_content_id,
        secondaryjoin=id == content_relationships_association.c.child_content_id,
        backref="related_to_contents"
    )
    
    # Hybrid properties for computed fields
    @hybrid_property
    def file_size_mb(self):
        """File size in megabytes"""        return self.file_size_bytes / (1024 * 1024) if self.file_size_bytes else 0
    
    @hybrid_property
    def processing_duration_seconds(self):
        """Processing duration in seconds"""        return self.processing_duration_ms / 1000 if self.processing_duration_ms else 0
    
    @hybrid_property
    def is_multimedia(self):
        """Check if content is multimedia type"""        return self.content_type == ContentType.MULTIMEDIA
    
    @hybrid_property
    def is_deleted(self):
        """Check if content is soft-deleted"""        return self.deleted_at is not None
    
    # Comprehensive indexes for performance
    __table_args__ = (
        # Primary search indexes
        Index('idx_content_hash', 'content_hash'),
        Index('idx_content_type', 'content_type'),
        Index('idx_content_format', 'content_format'),
        Index('idx_content_status', 'status'),
        Index('idx_content_protection', 'protection_level'),
        
        # Performance indexes
        Index('idx_content_created', 'created_at'),
        Index('idx_content_updated', 'updated_at'),
        Index('idx_content_uploaded', 'uploaded_at'),
        Index('idx_content_processed', 'last_processed_at'),
        Index('idx_content_accessed', 'last_accessed_at'),
        
        # User and ownership indexes
        Index('idx_content_uploaded_by', 'uploaded_by_user_id'),
        Index('idx_content_owner', 'owner_user_id'),
        
        # Source and origin indexes
        Index('idx_content_source', 'source_id'),
        Index('idx_content_platform', 'source_platform'),
        Index('idx_content_source_ref', 'source_reference_id'),
        
        # Content quality and metrics
        Index('idx_content_quality', 'quality_level'),
        Index('idx_content_validation', 'is_validated'),
        Index('idx_content_security', 'security_scan_passed'),
        Index('idx_content_trending', 'trending_score'),
        
        # Full-text search index
        Index('idx_content_search', 'search_vector', postgresql_using='gin'),
        Index('idx_content_keywords_gin', 'search_keywords', postgresql_using='gin'),
        
        # Soft delete support
        Index('idx_content_active', 'id', postgresql_where=Column('deleted_at').is_(None)),
        
        # Composite indexes for common queries
        Index('idx_content_type_status', 'content_type', 'status'),
        Index('idx_content_user_type', 'uploaded_by_user_id', 'content_type'),
        Index('idx_content_source_type', 'source_id', 'content_type'),
        Index('idx_content_created_type', 'created_at', 'content_type'),
        
        # Constraints
        CheckConstraint('file_size_bytes > 0', name='ck_content_file_size_positive'),
        CheckConstraint('current_version > 0', name='ck_content_version_positive'),
        CheckConstraint('view_count >= 0', name='ck_content_view_count_non_negative'),
        CheckConstraint('download_count >= 0', name='ck_content_download_count_non_negative'),
    )

    def __repr__(self):
        return f"<Content(id={self.id}, type={self.content_type}, filename='{self.original_filename}')>"

# Database utility functions and models
class ContentDatabaseManager:
    """Utility class for content database operations"""    
    @staticmethod
    def create_tables(engine):
        """Create all content-related tables"""        Base.metadata.create_all(engine)
    
    @staticmethod
    def get_content_stats(session) -> Dict[str, Any]:
        """Get comprehensive content statistics"""        from sqlalchemy import func, distinct
        
        stats = {}
        
        # Basic counts
        stats['total_contents'] = session.query(Content).count()
        stats['active_contents'] = session.query(Content).filter(Content.deleted_at.is_(None)).count()
        
        # Content by type
        type_stats = session.query(
            Content.content_type,
            func.count(Content.id).label('count')
        ).group_by(Content.content_type).all()
        stats['by_type'] = {str(ct): count for ct, count in type_stats}
        
        # Content by status
        status_stats = session.query(
            Content.status,
            func.count(Content.id).label('count')
        ).group_by(Content.status).all()
        stats['by_status'] = {str(status): count for status, count in status_stats}
        
        # Storage statistics
        total_size = session.query(func.sum(Content.file_size_bytes)).scalar() or 0
        stats['total_size_bytes'] = total_size
        stats['total_size_gb'] = total_size / (1024**3)
        
        # Recent activity
        from datetime import datetime, timedelta
        recent_date = datetime.now(timezone.utc) - timedelta(days=7)
        stats['uploads_last_7_days'] = session.query(Content).filter(
            Content.uploaded_at >= recent_date
        ).count()
        
        return stats
    
    @staticmethod
    def cleanup_orphaned_records(session) -> Dict[str, int]:
        """Clean up orphaned records and return cleanup statistics"""        cleanup_stats = {}
        
        # Remove orphaned metadata
        orphaned_metadata = session.query(ContentMetadata).filter(
            ~ContentMetadata.content_id.in_(
                session.query(Content.id)
            )
        ).count()
        
        if orphaned_metadata > 0:
            session.query(ContentMetadata).filter(
                ~ContentMetadata.content_id.in_(
                    session.query(Content.id)
                )
            ).delete(synchronize_session=False)
            
        cleanup_stats['orphaned_metadata_removed'] = orphaned_metadata
        
        # Remove orphaned fingerprints
        orphaned_fingerprints = session.query(ContentFingerprint).filter(
            ~ContentFingerprint.content_id.in_(
                session.query(Content.id)
            )
        ).count()
        
        if orphaned_fingerprints > 0:
            session.query(ContentFingerprint).filter(
                ~ContentFingerprint.content_id.in_(
                    session.query(Content.id)
                )
            ).delete(synchronize_session=False)
            
        cleanup_stats['orphaned_fingerprints_removed'] = orphaned_fingerprints
        
        session.commit()
        return cleanup_stats
