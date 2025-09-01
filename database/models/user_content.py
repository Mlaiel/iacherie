"""User Content Database Model

Enterprise-grade SQLAlchemy model for managing user-generated content across
multiple platforms with comprehensive metadata and lifecycle management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class ContentType(Enum):
    """
Content type enumeration"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    STORY = "story"
    REEL = "reel"
    POST = "post"
    ALBUM = "album"
    PLAYLIST = "playlist"
    COVER_ART = "cover_art"
    LYRICS = "lyrics"
    MUSIC_VIDEO = "music_video"
    REMIX = "remix"
    MASHUP = "mashup"
    SAMPLE = "sample"
    MULTIMODAL = "multimodal"


class ContentStatus(Enum):
    """Content lifecycle status"""

    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"
    SUSPENDED = "suspended"
    UNDER_REVIEW = "under_review"
    REJECTED = "rejected"
    PENDING_APPROVAL = "pending_approval"


class ContentGenre(Enum):
    """Music and content genres"""

    POP = "pop"
    ROCK = "rock"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    COUNTRY = "country"
    REGGAE = "reggae"
    BLUES = "blues"
    FOLK = "folk"
    LATIN = "latin"
    WORLD = "world"
    EXPERIMENTAL = "experimental"
    AMBIENT = "ambient"
    HOUSE = "house"
    TECHNO = "techno"
    TRANCE = "trance"
    DUBSTEP = "dubstep"
    DRUM_AND_BASS = "drum_and_bass"
    TRAP = "trap"
    LO_FI = "lo_fi"
    INDIE = "indie"
    ALTERNATIVE = "alternative"
    PUNK = "punk"
    METAL = "metal"
    FUNK = "funk"
    SOUL = "soul"
    RNB = "rnb"
    GOSPEL = "gospel"
    COMEDY = "comedy"
    PODCAST_TALK = "podcast_talk"
    PODCAST_NEWS = "podcast_news"
    PODCAST_EDUCATION = "podcast_education"
    OTHER = "other"


class LicenseType(Enum):
    """Content licensing types"""

    ALL_RIGHTS_RESERVED = "all_rights_reserved"
    CREATIVE_COMMONS_BY = "creative_commons_by"
    CREATIVE_COMMONS_BY_SA = "creative_commons_by_sa"
    CREATIVE_COMMONS_BY_NC = "creative_commons_by_nc"
    CREATIVE_COMMONS_BY_NC_SA = "creative_commons_by_nc_sa"
    CREATIVE_COMMONS_BY_ND = "creative_commons_by_nd"
    CREATIVE_COMMONS_BY_NC_ND = "creative_commons_by_nc_nd"
    PUBLIC_DOMAIN = "public_domain"
    ROYALTY_FREE = "royalty_free"
    EXCLUSIVE_LICENSE = "exclusive_license"
    NON_EXCLUSIVE_LICENSE = "non_exclusive_license"
    SYNC_LICENSE = "sync_license"
    MECHANICAL_LICENSE = "mechanical_license"
    PERFORMANCE_LICENSE = "performance_license"


class VisibilityLevel(Enum):
    """Content visibility levels"""

    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"
    FOLLOWERS_ONLY = "followers_only"
    PREMIUM_ONLY = "premium_only"
    COLLABORATORS_ONLY = "collaborators_only"
    RESTRICTED = "restricted"


class ProcessingStatus(Enum):
    """Content processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"


class QualityLevel(Enum):
    """Content quality levels"""

    ULTRA = "ultra"  # 4K, 320kbps+, lossless
    HIGH = "high"    # 1080p, 256kbps, high quality
    MEDIUM = "medium"  # 720p, 192kbps, standard quality
    LOW = "low"      # 480p, 128kbps, basic quality
    PREVIEW = "preview"  # Watermarked or limited preview


class UserContent(Base):
    """
    Enterprise User Content Model
    
    Comprehensive content management system for creators supporting multi-format content,
    advanced metadata, collaboration features, and monetization capabilities.
    """
    __tablename__ = "user_content"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    content_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=True, index=True)
    
    # Content classification
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    content_status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT, index=True)
    processing_status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    
    # Basic content information
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    artist_name = Column(String(255), nullable=True, index=True)
    featured_artists = Column(ARRAY(String), nullable=True)
    
    # Content categorization
    genre = Column(SQLEnum(ContentGenre), nullable=True, index=True)
    subgenres = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True, index=True)
    keywords = Column(ARRAY(String), nullable=True)
    mood = Column(String(100), nullable=True)
    energy_level = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # File and storage information
    original_filename = Column(String(500), nullable=True)
    file_path = Column(String(1000), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_hash = Column(String(255), nullable=True, index=True)
    
    # Quality and technical metadata
    quality_level = Column(SQLEnum(QualityLevel), default=QualityLevel.HIGH)
    duration = Column(Float, nullable=True)  # Duration in seconds
    bitrate = Column(Integer, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    bit_depth = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    codec = Column(String(50), nullable=True)
    
    # Video-specific metadata
    resolution_width = Column(Integer, nullable=True)
    resolution_height = Column(Integer, nullable=True)
    framerate = Column(Float, nullable=True)
    aspect_ratio = Column(String(20), nullable=True)
    video_codec = Column(String(50), nullable=True)
    
    # Image-specific metadata
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    color_space = Column(String(50), nullable=True)
    dpi = Column(Integer, nullable=True)
    
    # Audio analysis data
    tempo = Column(Float, nullable=True)  # BPM
    key_signature = Column(String(10), nullable=True)
    time_signature = Column(String(10), nullable=True)
    loudness = Column(Float, nullable=True)  # LUFS
    dynamics = Column(Float, nullable=True)
    spectral_features = Column(JSON, nullable=True)
    
    # Content accessibility
    visibility_level = Column(SQLEnum(VisibilityLevel), default=VisibilityLevel.PUBLIC)
    is_explicit = Column(Boolean, default=False)
    age_restriction = Column(Integer, nullable=True)
    content_warnings = Column(ARRAY(String), nullable=True)
    accessibility_features = Column(JSON, nullable=True)
    
    # Rights and licensing
    license_type = Column(SQLEnum(LicenseType), default=LicenseType.ALL_RIGHTS_RESERVED)
    copyright_owner = Column(String(255), nullable=True)
    copyright_year = Column(Integer, nullable=True)
    publishing_rights = Column(JSON, nullable=True)
    mechanical_rights = Column(JSON, nullable=True)
    sync_rights = Column(JSON, nullable=True)
    
    # Collaboration and credits
    collaborators = Column(JSON, nullable=True)
    credits = Column(JSON, nullable=True)
    producers = Column(ARRAY(String), nullable=True)
    writers = Column(ARRAY(String), nullable=True)
    composers = Column(ARRAY(String), nullable=True)
    performers = Column(ARRAY(String), nullable=True)
    engineers = Column(ARRAY(String), nullable=True)
    
    # Distribution and platforms
    distributed_platforms = Column(JSON, nullable=True)
    platform_specific_metadata = Column(JSON, nullable=True)
    external_ids = Column(JSON, nullable=True)  # Platform-specific content IDs
    sync_status = Column(JSON, nullable=True)
    
    # Monetization settings
    monetization_enabled = Column(Boolean, default=False)
    price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="EUR")
    revenue_sharing = Column(JSON, nullable=True)
    royalty_splits = Column(JSON, nullable=True)
    licensing_fees = Column(JSON, nullable=True)
    
    # Analytics and performance
    play_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    # Engagement metrics
    average_completion_rate = Column(Float, default=0.0)
    peak_concurrent_listeners = Column(Integer, default=0)
    total_listening_time = Column(Integer, default=0)  # Total seconds listened
    unique_listeners = Column(Integer, default=0)
    returning_listeners = Column(Integer, default=0)
    
    # Geographic and demographic data
    audience_countries = Column(JSON, nullable=True)
    audience_cities = Column(JSON, nullable=True)
    audience_age_groups = Column(JSON, nullable=True)
    audience_gender_split = Column(JSON, nullable=True)
    
    # AI and machine learning insights
    ai_generated_tags = Column(ARRAY(String), nullable=True)
    ai_content_analysis = Column(JSON, nullable=True)
    sentiment_analysis = Column(JSON, nullable=True)
    content_similarity_scores = Column(JSON, nullable=True)
    recommendation_scores = Column(JSON, nullable=True)
    trend_predictions = Column(JSON, nullable=True)
    
    # Content relationships
    parent_content_id = Column(UUID(as_uuid=True), ForeignKey('user_content.id'), nullable=True)
    remix_source_id = Column(UUID(as_uuid=True), ForeignKey('user_content.id'), nullable=True)
    album_id = Column(UUID(as_uuid=True), ForeignKey('user_content.id'), nullable=True)
    playlist_ids = Column(ARRAY(UUID), nullable=True)
    
    # Version control
    version_number = Column(String(20), default="1.0.0")
    is_latest_version = Column(Boolean, default=True)
    previous_version_id = Column(UUID(as_uuid=True), ForeignKey('user_content.id'), nullable=True)
    version_notes = Column(Text, nullable=True)
    
    # Processing and optimization
    processing_log = Column(JSON, nullable=True)
    optimization_status = Column(String(50), nullable=True)
    compression_ratio = Column(Float, nullable=True)
    quality_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    published_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    release_date = Column(DateTime(timezone=True), nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_trending = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    requires_review = Column(Boolean, default=False)
    
    # Content protection
    is_protected = Column(Boolean, default=True)
    watermark_enabled = Column(Boolean, default=False)
    drm_enabled = Column(Boolean, default=False)
    download_protection = Column(Boolean, default=False)
    
    # Relationships
    content_fingerprint = relationship("ContentFingerprint", back_populates="user_content")
    parent_content = relationship("UserContent", remote_side=[id], foreign_keys=[parent_content_id])
    remix_source = relationship("UserContent", remote_side=[id], foreign_keys=[remix_source_id])
    album = relationship("UserContent", remote_side=[id], foreign_keys=[album_id])
    previous_version = relationship("UserContent", remote_side=[id], foreign_keys=[previous_version_id])
    metadata_records = relationship("ContentMetadata", back_populates="user_content", cascade="all, delete-orphan")
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_content_user_type', 'user_id', 'content_type'),
        Index('idx_content_status_visibility', 'content_status', 'visibility_level'),
        Index('idx_content_genre_mood', 'genre', 'mood'),
        Index('idx_content_monetization', 'monetization_enabled', 'price'),
        Index('idx_content_analytics', 'play_count', 'like_count'),
        Index('idx_content_created_featured', 'created_at', 'is_featured'),
        Index('idx_content_artist_genre', 'artist_name', 'genre'),
        Index('idx_content_duration_quality', 'duration', 'quality_level'),
        Index('idx_content_trending_verified', 'is_trending', 'is_verified'),
        Index('idx_content_protection_status', 'is_protected', 'watermark_enabled'),
        Index('idx_content_release_date', 'release_date', 'content_status'),
        Index('idx_content_collaboration', 'collaborators'),
        Index('idx_content_tags', 'tags'),
    )
    
    def __repr__(self):
        return f"<UserContent(id={self.id}, title='{self.title}', type={self.content_type.value}, status={self.content_status.value})>"
    
    def to_dict(self, include_analytics: bool = True, include_technical: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        base_dict = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "content_fingerprint_id": str(self.content_fingerprint_id) if self.content_fingerprint_id else None,
            "content_type": self.content_type.value if self.content_type else None,
            "content_status": self.content_status.value if self.content_status else None,
            "processing_status": self.processing_status.value if self.processing_status else None,
            "title": self.title,
            "description": self.description,
            "short_description": self.short_description,
            "artist_name": self.artist_name,
            "featured_artists": self.featured_artists,
            "genre": self.genre.value if self.genre else None,
            "subgenres": self.subgenres,
            "tags": self.tags,
            "keywords": self.keywords,
            "mood": self.mood,
            "energy_level": self.energy_level,
            "quality_level": self.quality_level.value if self.quality_level else None,
            "duration": self.duration,
            "visibility_level": self.visibility_level.value if self.visibility_level else None,
            "is_explicit": self.is_explicit,
            "age_restriction": self.age_restriction,
            "content_warnings": self.content_warnings,
            "license_type": self.license_type.value if self.license_type else None,
            "copyright_owner": self.copyright_owner,
            "copyright_year": self.copyright_year,
            "collaborators": self.collaborators,
            "credits": self.credits,
            "producers": self.producers,
            "writers": self.writers,
            "composers": self.composers,
            "performers": self.performers,
            "monetization_enabled": self.monetization_enabled,
            "price": float(self.price) if self.price else None,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "is_trending": self.is_trending,
            "is_verified": self.is_verified,
            "is_protected": self.is_protected,
            "version_number": self.version_number,
            "is_latest_version": self.is_latest_version
        }
        
        if include_analytics:
            base_dict.update({
                "play_count": self.play_count,
                "download_count": self.download_count,
                "like_count": self.like_count,
                "share_count": self.share_count,
                "comment_count": self.comment_count,
                "view_count": self.view_count,
                "average_completion_rate": self.average_completion_rate,
                "total_listening_time": self.total_listening_time,
                "unique_listeners": self.unique_listeners,
                "audience_countries": self.audience_countries,
                "audience_age_groups": self.audience_age_groups,
                "ai_content_analysis": self.ai_content_analysis,
                "sentiment_analysis": self.sentiment_analysis
            })
        
        if include_technical:
            base_dict.update({
                "file_size": self.file_size,
                "mime_type": self.mime_type,
                "bitrate": self.bitrate,
                "sample_rate": self.sample_rate,
                "bit_depth": self.bit_depth,
                "channels": self.channels,
                "codec": self.codec,
                "resolution_width": self.resolution_width,
                "resolution_height": self.resolution_height,
                "framerate": self.framerate,
                "tempo": self.tempo,
                "key_signature": self.key_signature,
                "time_signature": self.time_signature,
                "loudness": self.loudness,
                "spectral_features": self.spectral_features,
                "processing_log": self.processing_log,
                "quality_score": self.quality_score
            })
        
        return base_dict
    
    def get_engagement_rate(self) -> float:
        """Calculate engagement rate based on interactions"""
        if self.view_count == 0:
            return 0.0
        
        total_interactions = (self.like_count + self.share_count + self.comment_count)
        return (total_interactions / self.view_count) * 100
    
    def get_completion_rate(self) -> float:
        """
Get content completion rate"""
        return self.average_completion_rate or 0.0
    
    def is_monetizable(self) -> bool:
        """
Check if content can be monetized"""
        return (
            self.monetization_enabled and
            self.content_status == ContentStatus.PUBLISHED and
            not self.is_explicit and
            self.is_verified and
            self.quality_level in [QualityLevel.HIGH, QualityLevel.ULTRA]
        )
    
    def get_revenue_potential(self) -> float:
        """
Estimate revenue potential based on metrics"""
        base_score = 0.0
        
        # Engagement factor
        engagement_rate = self.get_engagement_rate()
        base_score += min(engagement_rate / 10.0, 5.0)
        
        # Quality factor
        quality_weights = {
            QualityLevel.ULTRA: 5.0,
            QualityLevel.HIGH: 4.0,
            QualityLevel.MEDIUM: 2.5,
            QualityLevel.LOW: 1.0,
            QualityLevel.PREVIEW: 0.5
        }
        base_score += quality_weights.get(self.quality_level, 1.0)
        
        # Popularity factor
        if self.play_count > 0:
            base_score += min(self.play_count / 1000.0, 10.0)
        
        # Trending bonus
        if self.is_trending:
            base_score *= 1.5
        
        # Featured bonus
        if self.is_featured:
            base_score *= 1.3
        
        return min(base_score, 100.0)  # Cap at 100
    
    @classmethod
    def create_from_upload(cls, upload_data: Dict[str, Any], user_id: str) -> 'UserContent':
        """
Create UserContent from upload data"""
        return cls(
            user_id=user_id,
            content_type=ContentType(upload_data.get('content_type', 'audio')),
            title=upload_data.get('title', 'Untitled'),
            description=upload_data.get('description'),
            artist_name=upload_data.get('artist_name'),
            genre=ContentGenre(upload_data.get('genre', 'other')),
            tags=upload_data.get('tags', []),
            original_filename=upload_data.get('filename'),
            file_size=upload_data.get('file_size'),
            mime_type=upload_data.get('mime_type'),
            duration=upload_data.get('duration'),
            quality_level=QualityLevel(upload_data.get('quality_level', 'high')),
            visibility_level=VisibilityLevel(upload_data.get('visibility', 'public')),
            license_type=LicenseType(upload_data.get('license', 'all_rights_reserved')),
            monetization_enabled=upload_data.get('monetization_enabled', False),
            is_explicit=upload_data.get('is_explicit', False)
        )
