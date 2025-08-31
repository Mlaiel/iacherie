"""Content Data Model
=================

Professional content data model for multi-format content management.
Supports audio, video, image, and text content with comprehensive metadata.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
from datetime import datetime
from typing import Optional, Dict, List, Any
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

Base = declarative_base()


class ContentType(Enum):
    """Content type enumeration"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"


class ContentStatus(Enum):
    """Content status enumeration"""    DRAFT = "draft"
    PROCESSING = "processing"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    PROTECTED = "protected"


class ContentVisibility(Enum):
    """Content visibility settings"""    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"
    RESTRICTED = "restricted"


class ContentModel(Base):
    """    Professional content data model for IA Influencer Agent platform.
    
    Handles comprehensive content metadata, versioning, and multi-format support
    with protection, monetization, and analytics integration.
    """    
    __tablename__ = "content"
    
    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic content information
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content_type = Column(String(20), nullable=False)  # ContentType enum
    file_format = Column(String(50))  # mp3, mp4, jpg, txt, etc.
    mime_type = Column(String(100))
    
    # File and storage information
    original_filename = Column(String(255))
    file_path = Column(String(1000))
    file_size = Column(Integer)  # bytes
    file_hash = Column(String(64))  # SHA-256 hash
    storage_provider = Column(String(50))  # s3, gcs, azure, local
    storage_bucket = Column(String(100))
    storage_key = Column(String(500))
    
    # Content dimensions and properties
    duration = Column(Float)  # seconds for audio/video
    width = Column(Integer)   # pixels for image/video
    height = Column(Integer)  # pixels for image/video
    resolution = Column(String(20))  # 1920x1080, etc.
    frame_rate = Column(Float)  # fps for video
    sample_rate = Column(Integer)  # Hz for audio
    bit_rate = Column(Integer)  # bits per second
    channels = Column(Integer)  # audio channels
    
    # Content metadata
    metadata = Column(JSON)  # Flexible metadata storage
    tags = Column(ARRAY(String))  # Content tags
    categories = Column(ARRAY(String))  # Content categories
    language = Column(String(10))  # ISO language code
    encoding = Column(String(50))  # Character encoding for text
    
    # Visibility and access control
    visibility = Column(String(20), default=ContentVisibility.PUBLIC.value)
    is_protected = Column(Boolean, default=False)
    is_monetized = Column(Boolean, default=False)
    is_copyrighted = Column(Boolean, default=True)
    license_type = Column(String(50))  # CC, proprietary, etc.
    
    # Performance and analytics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    revenue_total = Column(DECIMAL(12, 4), default=0)
    
    # Geographic and demographic
    upload_location = Column(String(100))  # City, Country
    target_audience = Column(JSON)  # Age groups, demographics
    geographic_restrictions = Column(ARRAY(String))  # Country codes
    
    # SEO and discovery
    seo_title = Column(String(150))
    seo_description = Column(String(300))
    seo_keywords = Column(ARRAY(String))
    search_ranking_score = Column(Float, default=0.0)
    discoverability_score = Column(Float, default=0.0)
    
    # Platform distribution
    platforms = Column(JSON)  # Platform-specific data
    platform_urls = Column(JSON)  # URLs on different platforms
    cross_platform_ids = Column(JSON)  # IDs on different platforms
    
    # Content relationships
    parent_content_id = Column(String(36), ForeignKey("content.id"))  # For derivatives
    collection_id = Column(String(36))  # Content collections/albums
    series_id = Column(String(36))  # Content series
    collaboration_ids = Column(ARRAY(String))  # Collaborative content
    
    # Version control
    version = Column(String(20), default="1.0.0")
    is_latest_version = Column(Boolean, default=True)
    version_history = Column(JSON)  # Version change log
    
    # Processing status
    status = Column(String(20), default=ContentStatus.DRAFT.value)
    processing_status = Column(String(50))  # detailed processing state
    processing_progress = Column(Float, default=0.0)  # 0-100%
    processing_logs = Column(JSON)  # Processing error logs
    
    # Quality metrics
    quality_score = Column(Float, default=0.0)  # 0-100
    content_rating = Column(String(10))  # G, PG, R, etc.
    appropriateness_score = Column(Float, default=100.0)  # AI content moderation
    
    # Engagement and interaction
    average_rating = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    retention_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    # AI and ML features
    ai_generated = Column(Boolean, default=False)
    ai_model_used = Column(String(100))  # Model that generated content
    ai_confidence_score = Column(Float)  # AI generation confidence
    content_fingerprint = Column(String(128))  # AI fingerprint hash
    similarity_vectors = Column(JSON)  # Vector embeddings
    
    # Protection and security
    protection_enabled = Column(Boolean, default=False)
    watermark_applied = Column(Boolean, default=False)
    encryption_enabled = Column(Boolean, default=False)
    access_token = Column(String(128))  # Secure access token
    download_restrictions = Column(JSON)  # Download limitations
    
    # Monetization
    monetization_enabled = Column(Boolean, default=False)
    price = Column(DECIMAL(10, 4))  # Content price
    currency = Column(String(3), default="EUR")
    revenue_share_config = Column(JSON)  # Revenue sharing settings
    licensing_terms = Column(JSON)  # Licensing agreements
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    last_accessed_at = Column(DateTime)
    expires_at = Column(DateTime)  # Content expiration
    
    # Soft delete
    deleted_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="content")
    fingerprints = relationship("FingerprintModel", back_populates="content")
    analytics = relationship("AnalyticsModel", back_populates="content")
    revenue_records = relationship("RevenueModel", back_populates="content")
    protection_records = relationship("ProtectionModel", back_populates="content")
    licenses = relationship("LicensingModel", back_populates="content")
    
    def __repr__(self):
        return f"<ContentModel(id='{self.id}', title='{self.title}', type='{self.content_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation"""        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'content_type': self.content_type,
            'file_format': self.file_format,
            'mime_type': self.mime_type,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'resolution': self.resolution,
            'metadata': self.metadata,
            'tags': self.tags,
            'categories': self.categories,
            'language': self.language,
            'visibility': self.visibility,
            'is_protected': self.is_protected,
            'is_monetized': self.is_monetized,
            'view_count': self.view_count,
            'download_count': self.download_count,
            'like_count': self.like_count,
            'share_count': self.share_count,
            'revenue_total': float(self.revenue_total) if self.revenue_total else 0.0,
            'seo_title': self.seo_title,
            'seo_description': self.seo_description,
            'seo_keywords': self.seo_keywords,
            'platforms': self.platforms,
            'version': self.version,
            'status': self.status,
            'quality_score': self.quality_score,
            'average_rating': self.average_rating,
            'engagement_rate': self.engagement_rate,
            'ai_generated': self.ai_generated,
            'protection_enabled': self.protection_enabled,
            'monetization_enabled': self.monetization_enabled,
            'price': float(self.price) if self.price else None,
            'currency': self.currency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'is_deleted': self.is_deleted
        }
    
    @property
    def is_audio(self) -> bool:
        """Check if content is audio type"""        return self.content_type == ContentType.AUDIO.value
    
    @property
    def is_video(self) -> bool:
        """Check if content is video type"""        return self.content_type == ContentType.VIDEO.value
    
    @property
    def is_image(self) -> bool:
        """Check if content is image type"""        return self.content_type == ContentType.IMAGE.value
    
    @property
    def is_text(self) -> bool:
        """Check if content is text type"""        return self.content_type == ContentType.TEXT.value
    
    @property
    def is_published(self) -> bool:
        """Check if content is published"""        return self.status == ContentStatus.ACTIVE.value and self.published_at is not None
    
    @property
    def is_protected(self) -> bool:
        """Check if content has protection enabled"""        return self.protection_enabled and not self.is_deleted
    
    @property
    def is_monetizable(self) -> bool:
        """Check if content can be monetized"""        return (self.monetization_enabled and 
                self.status == ContentStatus.ACTIVE.value and 
                not self.is_deleted)
    
    @property
    def file_extension(self) -> str:
        """Get file extension from filename"""        if self.original_filename and '.' in self.original_filename:
            return self.original_filename.split('.')[-1].lower()
        return ""
    
    @property
    def aspect_ratio(self) -> Optional[float]:
        """Calculate aspect ratio for visual content"""        if self.width and self.height and self.height > 0:
            return self.width / self.height
        return None
    
    @property
    def size_formatted(self) -> str:
        """Get human-readable file size"""        if not self.file_size:
            return "Unknown"
        
        size = self.file_size
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    @property
    def duration_formatted(self) -> str:
        """Get human-readable duration"""        if not self.duration:
            return "00:00"
        
        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def update_engagement_metrics(self, views: int = 0, likes: int = 0, 
                                shares: int = 0, comments: int = 0):
        """Update engagement metrics"""        if views > 0:
            self.view_count = max(self.view_count or 0, views)
        if likes > 0:
            self.like_count = max(self.like_count or 0, likes)
        if shares > 0:
            self.share_count = max(self.share_count or 0, shares)
        if comments > 0:
            self.comment_count = max(self.comment_count or 0, comments)
        
        # Calculate engagement rate
        total_interactions = (self.like_count or 0) + (self.share_count or 0) + (self.comment_count or 0)
        if self.view_count and self.view_count > 0:
            self.engagement_rate = total_interactions / self.view_count
        
        self.updated_at = datetime.utcnow()
    
    def add_revenue(self, amount: Decimal, currency: str = "EUR"):
        """Add revenue to content"""        if not self.revenue_total:
            self.revenue_total = Decimal('0')
        
        # Convert currency if needed (simplified)
        if currency == self.currency:
            self.revenue_total += amount
        else:
            # In real implementation, would convert currencies
            self.revenue_total += amount
        
        self.updated_at = datetime.utcnow()
    
    def set_quality_score(self, score: float):
        """Set content quality score"""        self.quality_score = max(0.0, min(100.0, score))
        self.updated_at = datetime.utcnow()
    
    def mark_as_protected(self, fingerprint_hash: str = None):
        """Mark content as protected"""        self.protection_enabled = True
        self.is_protected = True
        if fingerprint_hash:
            self.content_fingerprint = fingerprint_hash
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self):
        """Soft delete content"""        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.status = ContentStatus.DELETED.value
        self.updated_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft-deleted content"""        self.is_deleted = False
        self.deleted_at = None
        self.status = ContentStatus.ACTIVE.value
        self.updated_at = datetime.utcnow()
