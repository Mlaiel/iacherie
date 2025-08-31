"""IA Influencer Agent Platform - Creator Models
Advanced creator management for multi-format content creators

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Engineer + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected by copyright law and intellectual property rights.
Any unauthorized use, reproduction, copying, distribution, or commercial exploitation 
without explicit written permission from Fahed Mlaiel is strictly prohibited and 
will result in legal action.

Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""from datetime import datetime, timezone
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


class Creator(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin):
    """Core creator model for multi-format content creators"""    
    __tablename__ = 'creators'
    
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Creator Identity
    creator_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    
    creator_slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    
    creator_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # musician, blogger, photographer, influencer, comedian, podcaster
    
    # Professional Information
    professional_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    stage_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Contact and Business
    business_email: Mapped[Optional[str]] = mapped_column(
        String(320),
        nullable=True,
        index=True
    )
    
    management_contact: Mapped[Optional[str]] = mapped_column(
        String(320),
        nullable=True
    )
    
    booking_email: Mapped[Optional[str]] = mapped_column(
        String(320),
        nullable=True
    )
    
    # Content Categories
    primary_genre: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    secondary_genres: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)),
        nullable=True
    )
    
    content_categories: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)),
        nullable=True
    )  # music, video, photography, blog, podcast, social
    
    # Verification and Trust
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    verification_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )  # platform, identity, professional, premium
    
    trust_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal('0.00'),
        nullable=False,
        index=True
    )
    
    # Subscription and Payment
    subscription_tier: Mapped[str] = mapped_column(
        String(50),
        default='free',
        nullable=False,
        index=True
    )  # free, basic, professional, enterprise
    
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Platform Integrations
    platform_connections: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True
    )  # Spotify, YouTube, Instagram, TikTok, etc.
    
    # Relationships
    profile: Mapped["CreatorProfile"] = relationship(
        "CreatorProfile",
        back_populates="creator",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    statistics: Mapped["CreatorStatistics"] = relationship(
        "CreatorStatistics",
        back_populates="creator",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    subscription: Mapped[Optional["CreatorSubscription"]] = relationship(
        "CreatorSubscription",
        back_populates="creator",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_creators_type_status', 'creator_type', 'status'),
        Index('idx_creators_verification', 'is_verified', 'verification_type'),
        Index('idx_creators_subscription', 'subscription_tier', 'subscription_expires_at'),
        CheckConstraint('trust_score >= 0 AND trust_score <= 100', name='valid_trust_score'),
    )


class CreatorProfile(BaseModel, UUIDMixin, TimestampMixin, MetadataMixin, PerformanceMetricsMixin):
    """Extended creator profile with rich media and analytics"""    
    __tablename__ = 'creator_profiles'
    
    creator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Visual Branding
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    cover_image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    banner_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    # Brand Colors and Theme
    brand_colors: Mapped[Optional[Dict[str, str]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    theme_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Portfolio and Showcase
    featured_content: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(255)),
        nullable=True
    )  # Content IDs of featured works
    
    portfolio_items: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    achievements: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    awards: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Social Media and External Links
    website_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    social_media_links: Mapped[Optional[Dict[str, str]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True
    )
    
    streaming_platforms: Mapped[Optional[Dict[str, str]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True
    )
    
    # Professional Information
    equipment_list: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    skills: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)),
        nullable=True
    )
    
    languages: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(20)),
        nullable=True
    )
    
    collaboration_preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Content Statistics
    total_content_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    published_content_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    protected_content_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    # Performance Metrics
    average_engagement_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    total_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    
    monthly_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    
    # Relationships
    creator: Mapped["Creator"] = relationship(
        "Creator",
        back_populates="profile"
    )


class CreatorStatistics(BaseModel, UUIDMixin, TimestampMixin):
    """Real-time statistics and analytics for creators"""    
    __tablename__ = 'creator_statistics'
    
    creator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Audience Metrics
    total_followers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True
    )
    
    total_subscribers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    monthly_active_followers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    audience_demographics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Content Performance
    total_views: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True
    )
    
    total_likes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    total_shares: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    total_comments: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    # Time-based Metrics
    daily_stats: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    weekly_stats: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    monthly_stats: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Platform-specific Metrics
    platform_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True
    )  # Spotify, YouTube, Instagram, etc. specific metrics
    
    # Revenue and Monetization
    total_revenue_earned: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    
    revenue_this_month: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    
    average_monthly_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    
    # Growth Metrics
    follower_growth_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    engagement_growth_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    revenue_growth_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Protection and Rights
    content_violations_detected: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    takedown_requests_sent: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    successful_takedowns: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    estimated_recovered_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    
    # Last Update
    last_calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default='now()',
        index=True
    )
    
    # Relationships
    creator: Mapped["Creator"] = relationship(
        "Creator",
        back_populates="statistics"
    )


class CreatorSubscription(BaseModel, UUIDMixin, TimestampMixin, AuditMixin):
    """Creator subscription and billing management"""    
    __tablename__ = 'creator_subscriptions'
    
    creator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Subscription Details
    plan_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    plan_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # free, basic, professional, enterprise
    
    billing_cycle: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # monthly, yearly, lifetime
    
    # Pricing
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        default='USD',
        nullable=False
    )
    
    # Status and Timing
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # active, cancelled, expired, suspended
    
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Features and Limits
    features: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )
    
    usage_limits: Mapped[Dict[str, int]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )
    
    current_usage: Mapped[Dict[str, int]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )
    
    # Payment Information
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    payment_provider: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )  # stripe, paypal, wire, etc.
    
    payment_provider_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    last_payment_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    next_payment_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Trial Information
    is_trial: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Auto-renewal
    auto_renew: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Relationships
    creator: Mapped["Creator"] = relationship(
        "Creator",
        back_populates="subscription"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_subscriptions_status_expires', 'status', 'expires_at'),
        Index('idx_subscriptions_trial', 'is_trial', 'trial_ends_at'),
        Index('idx_subscriptions_next_payment', 'next_payment_at'),
    )
