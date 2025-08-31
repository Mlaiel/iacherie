"""IA Influencer Agent Platform - Content Models
Comprehensive content management for multi-format media

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
    AuditMixin, MetadataMixin, StatusMixin, PerformanceMetricsMixin
)


class Content(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin, PerformanceMetricsMixin):
    """
Core content model for multi-format media management"""
    
    __tablename__ = 'contents'
    
    creator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Basic Information
    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True
    )
    
    slug: Mapped[Optional[str]] = mapped_column(
        String(350),
        unique=True,
        nullable=True,
        index=True
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    content_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # music, video, image, blog, podcast, social_post
    
    # Content Classification
    genre: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    subcategory: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Content Properties
    language: Mapped[str] = mapped_column(
        String(10),
        default='en',
        nullable=False,
        index=True
    )
    
    duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # Duration in seconds for audio/video
    
    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # File size in bytes
    
    # Rights and Licensing
    copyright_status: Mapped[str] = mapped_column(
        String(50),
        default='owned',
        nullable=False,
        index=True
    )  # owned, licensed, fair_use, public_domain
    
    license_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    is_original: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Monetization
    is_monetizable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    monetization_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )  # advertising, subscription, pay_per_view, free
    
    price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        default='USD',
        nullable=False
    )
    
    # Visibility and Publishing
    visibility: Mapped[str] = mapped_column(
        String(20),
        default='private',
        nullable=False,
        index=True
    )  # public, private, unlisted, scheduled
    
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    scheduled_publish_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # SEO and Discovery
    seo_title: Mapped[Optional[str]] = mapped_column(
        String(300),
        nullable=True
    )
    
    seo_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    keywords: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)),
        nullable=True
    )
    
    # Content Safety and Moderation
    content_rating: Mapped[str] = mapped_column(
        String(20),
        default='general',
        nullable=False
    )  # general, mature, explicit
    
    is_ai_generated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    content_warnings: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)),
        nullable=True
    )
    
    # Relationships
    metadata: Mapped["ContentMetadata"] = relationship(
        "ContentMetadata",
        back_populates="content",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    versions: Mapped[List["ContentVersion"]] = relationship(
        "ContentVersion",
        back_populates="content",
        cascade="all, delete-orphan"
    )
    
    tags: Mapped[List["ContentTag"]] = relationship(
        "ContentTag",
        back_populates="content",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_contents_creator_type', 'creator_id', 'content_type'),
        Index('idx_contents_status_published', 'status', 'is_published'),
        Index('idx_contents_visibility_published', 'visibility', 'published_at'),
        Index('idx_contents_genre_category', 'genre', 'category'),
        CheckConstraint('duration >= 0', name='positive_duration'),
        CheckConstraint('file_size >= 0', name='positive_file_size'),
    )


class ContentMetadata(BaseModel, UUIDMixin, TimestampMixin):
    """Extended metadata for content with technical and business information"""
    
    __tablename__ = 'content_metadata'
    
    content_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('contents.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Technical Metadata
    file_format: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    codec: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    bitrate: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    sample_rate: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    resolution: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )  # 1920x1080, etc.
    
    frame_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )
    
    color_space: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Audio-specific Metadata
    bpm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # Beats per minute
    
    key_signature: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )  # C major, A minor, etc.
    
    time_signature: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )  # 4/4, 3/4, etc.
    
    instruments: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)),
        nullable=True
    )
    
    # Image/Video Metadata
    camera_make: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    camera_model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    lens: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    focal_length: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        nullable=True
    )
    
    aperture: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True
    )
    
    iso: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    exposure_time: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Location Metadata
    location: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    latitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 8),
        nullable=True
    )
    
    longitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(11, 8),
        nullable=True
    )
    
    altitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        nullable=True
    )
    
    # Production Metadata
    production_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    recording_studio: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    producer: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    engineer: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    # Collaborators and Credits
    featuring: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(200)),
        nullable=True
    )
    
    writers: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(200)),
        nullable=True
    )
    
    composers: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(200)),
        nullable=True
    )
    
    performers: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(200)),
        nullable=True
    )
    
    # Custom Metadata
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True
    )
    
    # Relationships
    content: Mapped["Content"] = relationship(
        "Content",
        back_populates="metadata"
    )


class ContentVersion(BaseModel, UUIDMixin, TimestampMixin, AuditMixin):
    """Version control for content changes and updates"""
    
    __tablename__ = 'content_versions'
    
    content_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('contents.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Version Information
    version_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )  # 1.0.0, 1.1.0, etc.
    
    version_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # major, minor, patch
    
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Change Information
    change_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    change_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    change_reason: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )  # update, fix, enhancement, revision
    
    # File Information
    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    file_hash: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True
    )  # SHA-256 hash
    
    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default='draft',
        nullable=False,
        index=True
    )  # draft, published, archived
    
    # Relationships
    content: Mapped["Content"] = relationship(
        "Content",
        back_populates="versions"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_versions_content_number', 'content_id', 'version_number'),
        Index('idx_versions_current', 'is_current'),
        UniqueConstraint('content_id', 'version_number', name='unique_content_version'),
    )


class ContentTag(BaseModel, UUIDMixin, TimestampMixin):
    """Flexible tagging system for content organization"""
    
    __tablename__ = 'content_tags'
    
    content_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('contents.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Tag Information
    tag_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    tag_category: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )  # genre, mood, instrument, style, etc.
    
    tag_type: Mapped[str] = mapped_column(
        String(20),
        default='user',
        nullable=False,
        index=True
    )  # user, auto, ai_generated, system
    
    # Metadata
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )  # For AI-generated tags
    
    source: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )  # manual, ai_analysis, import, etc.
    
    # Usage Statistics
    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    
    # Relationships
    content: Mapped["Content"] = relationship(
        "Content",
        back_populates="tags"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_tags_name_category', 'tag_name', 'tag_category'),
        Index('idx_tags_type_confidence', 'tag_type', 'confidence_score'),
        UniqueConstraint('content_id', 'tag_name', 'tag_category', name='unique_content_tag'),
    )
