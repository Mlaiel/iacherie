"""Enterprise Content Models
=========================

Core content, user, and analytics models for IA Influencer Agent platform.
Comprehensive enterprise-level data models supporting multi-format content,
advanced user management, and real-time analytics tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

🚀 ENTERPRISE FEATURES:
• Multi-format content support (audio, video, image, text, podcast, live streams)
• Creator type differentiation (musicians, bloggers, photographers, influencers, comedians)
• Comprehensive user profiles with subscription tiers
• Real-time analytics tracking for all content types
• Content lifecycle management (draft → published → monetized)
• Privacy & visibility controls
• Performance metrics & KPIs tracking
• User verification & trust scoring
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, date
from enum import Enum
import uuid
from typing import Optional, Dict, Any, List

# SQLAlchemy declarative base
Base = declarative_base()


# ============================================================================
# ENUMS - Content Management
# ============================================================================

class ContentType(Enum):
    """Content type enumeration supporting all creator formats"""
    MUSIC = "music"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    AUDIO = "audio"
    DOCUMENT = "document"
    SOCIAL_POST = "social_post"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"


class ContentStatus(Enum):
    """Content lifecycle status management"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    MONETIZED = "monetized"
    ARCHIVED = "archived"
    DELETED = "deleted"
    SUSPENDED = "suspended"
    FLAGGED = "flagged"
    PROCESSING = "processing"


class ContentVisibility(Enum):
    """Content privacy and access control"""
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PREMIUM = "premium"
    SUBSCRIBERS_ONLY = "subscribers_only"
    MEMBERS_ONLY = "members_only"
    PAID_ACCESS = "paid_access"
    LIMITED_ACCESS = "limited_access"


# ============================================================================
# ENUMS - User Management
# ============================================================================

class UserType(Enum):
    """Creator type classification for platform specialization"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    ARTIST = "artist"
    EDUCATOR = "educator"
    BUSINESS = "business"
    BRAND = "brand"
    AGENCY = "agency"
    CONTENT_CREATOR = "content_creator"


class UserStatus(Enum):
    """User account status and verification levels"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    PARTNER = "partner"
    ADMIN = "admin"


class SubscriptionTier(Enum):
    """Subscription tiers with increasing capabilities"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    PARTNER = "partner"
    CUSTOM = "custom"


# ============================================================================
# ENUMS - Analytics & Metrics
# ============================================================================

class AnalyticsType(Enum):
    """Analytics tracking categories"""
    VIEWS = "views"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    PROTECTION = "protection"
    PERFORMANCE = "performance"
    AUDIENCE = "audience"
    CONVERSION = "conversion"
    RETENTION = "retention"
    TRAFFIC = "traffic"
    SOCIAL = "social"


class MetricType(Enum):
    """Specific metric types for detailed tracking"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    REAL_TIME = "real_time"
    CUMULATIVE = "cumulative"
    AVERAGE = "average"
    PEAK = "peak"
    TREND = "trend"


class TimeGranularity(Enum):
    """Time granularity for analytics aggregation"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    REAL_TIME = "real_time"


# ============================================================================
# CORE MODELS
# ============================================================================

class ContentModel(Base):
    """
    Enterprise content model supporting all creator content types.
    Comprehensive content management with lifecycle tracking, analytics integration,
    and multi-platform distribution capabilities.
    """
    __tablename__ = 'content'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Content classification
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    status = Column(SQLEnum(ContentStatus), nullable=False, default=ContentStatus.DRAFT, index=True)
    visibility = Column(SQLEnum(ContentVisibility), nullable=False, default=ContentVisibility.PRIVATE, index=True)
    
    # Core content information
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    content_url = Column(String(1000))
    thumbnail_url = Column(String(1000))
    original_filename = Column(String(500))
    
    # File & technical metadata
    file_size = Column(Integer)  # bytes
    file_format = Column(String(50))
    duration = Column(Float)  # seconds for audio/video
    resolution = Column(String(50))  # for images/videos
    bitrate = Column(Integer)  # for audio/video
    codec = Column(String(50))
    
    # Content metadata
    tags = Column(JSONB, default=list)  # ["music", "rock", "instrumental"]
    categories = Column(JSONB, default=list)  # ["entertainment", "music"]
    language = Column(String(10), default="en")
    genre = Column(String(100))
    mood = Column(String(100))
    
    # SEO & Discovery
    seo_title = Column(String(100))
    seo_description = Column(String(300))
    seo_keywords = Column(JSONB, default=list)
    custom_url_slug = Column(String(200), unique=True, index=True)
    
    # Analytics & Performance
    view_count = Column(Integer, default=0, index=True)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    
    # Revenue tracking
    revenue_total = Column(Float, default=0.0, index=True)
    revenue_this_month = Column(Float, default=0.0)
    license_revenue = Column(Float, default=0.0)
    ad_revenue = Column(Float, default=0.0)
    
    # Platform distribution
    platforms_published = Column(JSONB, default=list)  # ["youtube", "spotify", "instagram"]
    platform_urls = Column(JSONB, default=dict)  # {"youtube": "https://youtube.com/watch?v=123"}
    cross_platform_sync = Column(Boolean, default=True)
    
    # Protection & Rights
    copyright_status = Column(String(50), default="protected")
    license_type = Column(String(100))
    rights_management = Column(Boolean, default=True)
    content_id_claimed = Column(Boolean, default=False)
    fingerprint_generated = Column(Boolean, default=False)
    
    # Engagement metrics
    engagement_rate = Column(Float, default=0.0)  # percentage
    retention_rate = Column(Float, default=0.0)  # percentage
    conversion_rate = Column(Float, default=0.0)  # percentage
    audience_reach = Column(Integer, default=0)
    
    # AI processing status
    ai_analysis_complete = Column(Boolean, default=False)
    ai_optimization_applied = Column(Boolean, default=False)
    ai_enhancement_status = Column(String(50), default="pending")
    ai_tags_generated = Column(JSONB, default=list)
    
    # Geographic & Demographic
    target_regions = Column(JSONB, default=list)  # ["US", "DE", "FR"]
    age_rating = Column(String(20), default="all_ages")
    content_warnings = Column(JSONB, default=list)
    
    # Timestamps & lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), index=True)
    archived_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    
    # System flags
    is_featured = Column(Boolean, default=False, index=True)
    is_trending = Column(Boolean, default=False, index=True)
    is_monetized = Column(Boolean, default=False, index=True)
    is_premium = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Performance optimization
    cache_invalidation_key = Column(String(100))
    last_performance_update = Column(DateTime(timezone=True))
    
    # Relationships
    owner = relationship("UserModel", back_populates="content_items")
    analytics_records = relationship("AnalyticsModel", back_populates="content", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_content_user_status', 'user_id', 'status'),
        Index('idx_content_type_visibility', 'content_type', 'visibility'),
        Index('idx_content_created_featured', 'created_at', 'is_featured'),
        Index('idx_content_revenue_monetized', 'revenue_total', 'is_monetized'),
        Index('idx_content_views_trending', 'view_count', 'is_trending'),
    )
    
    def __repr__(self):
        return f"<ContentModel(id={self.id}, title='{self.title[:50]}', type={self.content_type.value})>"


class UserModel(Base):
    """
    Enterprise user model supporting all creator types with comprehensive
    profile management, subscription tiers, and analytics integration.
    """
    __tablename__ = 'users'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    
    # User classification
    user_type = Column(SQLEnum(UserType), nullable=False, index=True)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE, index=True)
    subscription_tier = Column(SQLEnum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE, index=True)
    
    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    display_name = Column(String(150), index=True)
    bio = Column(Text)
    avatar_url = Column(String(1000))
    cover_image_url = Column(String(1000))
    
    # Contact & Location
    phone = Column(String(20))
    website = Column(String(500))
    location = Column(String(200))
    timezone = Column(String(50), default="UTC")
    language_preference = Column(String(10), default="en")
    
    # Creator-specific information
    creator_category = Column(String(100))  # "Music Producer", "Fashion Blogger", etc.
    specializations = Column(JSONB, default=list)  # ["Electronic Music", "Portrait Photography"]
    years_experience = Column(Integer)
    professional_level = Column(String(50))  # "beginner", "intermediate", "professional", "expert"
    
    # Social media links
    social_links = Column(JSONB, default=dict)  # {"instagram": "@username", "youtube": "channel_id"}
    verification_links = Column(JSONB, default=dict)  # Platform verification URLs
    
    # Statistics & Performance
    total_content_count = Column(Integer, default=0, index=True)
    total_followers = Column(Integer, default=0, index=True)
    total_views = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0, index=True)
    total_downloads = Column(Integer, default=0)
    
    # Monthly metrics
    monthly_views = Column(Integer, default=0)
    monthly_revenue = Column(Float, default=0.0)
    monthly_engagement = Column(Float, default=0.0)
    monthly_growth_rate = Column(Float, default=0.0)
    
    # Engagement metrics
    average_engagement_rate = Column(Float, default=0.0)
    audience_retention_rate = Column(Float, default=0.0)
    fan_base_growth_rate = Column(Float, default=0.0)
    content_quality_score = Column(Float, default=0.0)
    
    # Trust & Verification
    verification_status = Column(String(50), default="unverified")
    trust_score = Column(Float, default=0.0)  # 0-100 trust rating
    identity_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    
    # Subscription & Billing
    subscription_start_date = Column(DateTime(timezone=True))
    subscription_end_date = Column(DateTime(timezone=True))
    billing_cycle = Column(String(20), default="monthly")  # "monthly", "annual"
    payment_method_id = Column(String(100))
    
    # Platform settings
    notification_preferences = Column(JSONB, default=dict)
    privacy_settings = Column(JSONB, default=dict)
    content_preferences = Column(JSONB, default=dict)
    ai_assistance_enabled = Column(Boolean, default=True)
    
    # Geographic & Demographic
    country = Column(String(5))  # ISO country code
    region = Column(String(100))
    age_range = Column(String(20))  # "18-24", "25-34", etc.
    target_audience = Column(JSONB, default=list)
    
    # Revenue & Monetization
    monetization_enabled = Column(Boolean, default=False)
    payout_method = Column(String(50))  # "stripe", "paypal", "bank_transfer"
    payout_schedule = Column(String(20), default="monthly")
    minimum_payout_threshold = Column(Float, default=50.0)
    
    # Platform permissions
    platform_permissions = Column(JSONB, default=dict)  # {"youtube": {"upload": true, "monetize": true}}
    api_access_tokens = Column(JSONB, default=dict)  # Encrypted platform tokens
    integration_status = Column(JSONB, default=dict)  # Platform connection status
    
    # AI & Analytics
    ai_profile_complete = Column(Boolean, default=False)
    ai_recommendations_enabled = Column(Boolean, default=True)
    analytics_access_level = Column(String(20), default="basic")  # "basic", "advanced", "enterprise"
    
    # Timestamps & lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), index=True)
    last_active_at = Column(DateTime(timezone=True), index=True)
    deleted_at = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True, index=True)
    is_premium = Column(Boolean, default=False, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    is_featured_creator = Column(Boolean, default=False)
    is_beta_tester = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    content_items = relationship("ContentModel", back_populates="owner", cascade="all, delete-orphan")
    analytics_records = relationship("AnalyticsModel", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_type_status', 'user_type', 'status'),
        Index('idx_user_subscription_premium', 'subscription_tier', 'is_premium'),
        Index('idx_user_revenue_tier', 'total_revenue', 'subscription_tier'),
        Index('idx_user_verification_trust', 'is_verified', 'trust_score'),
        Index('idx_user_active_login', 'is_active', 'last_login_at'),
    )
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, username='{self.username}', type={self.user_type.value})>"


class AnalyticsModel(Base):
    """
    Enterprise analytics model for comprehensive tracking of content performance,
    user behavior, revenue metrics, and platform-wide intelligence.
    """
    __tablename__ = 'analytics'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=True, index=True)
    
    # Analytics classification
    analytics_type = Column(SQLEnum(AnalyticsType), nullable=False, index=True)
    metric_type = Column(SQLEnum(MetricType), nullable=False, index=True)
    time_granularity = Column(SQLEnum(TimeGranularity), nullable=False, index=True)
    
    # Measurement data
    measurement_date = Column(DateTime(timezone=True), nullable=False, index=True)
    value = Column(Float, nullable=False)
    previous_value = Column(Float)
    percentage_change = Column(Float)
    
    # Metric details
    metric_name = Column(String(100), nullable=False, index=True)
    metric_category = Column(String(50))
    metric_subcategory = Column(String(50))
    unit_of_measurement = Column(String(20))  # "views", "dollars", "percentage", "count"
    
    # Contextual information
    platform = Column(String(50))  # "youtube", "spotify", "instagram", "platform_wide"
    region = Column(String(10))  # ISO country code
    device_type = Column(String(20))  # "mobile", "desktop", "tablet", "smart_tv"
    traffic_source = Column(String(50))  # "organic", "paid", "social", "direct"
    
    # Segmentation
    audience_segment = Column(String(100))  # "18-24_male_US", "premium_subscribers"
    content_category = Column(String(50))
    user_tier = Column(String(20))
    
    # Advanced metrics
    confidence_score = Column(Float, default=1.0)  # Data quality/confidence 0-1
    sample_size = Column(Integer)
    margin_of_error = Column(Float)
    statistical_significance = Column(Boolean, default=True)
    
    # Metadata
    data_source = Column(String(100))  # "google_analytics", "platform_api", "internal_tracking"
    collection_method = Column(String(50))  # "api", "webhook", "batch_import", "real_time"
    processing_status = Column(String(20), default="processed")
    
    # Dimensions (for OLAP-style analytics)
    dimensions = Column(JSONB, default=dict)  # {"age_group": "25-34", "genre": "electronic"}
    measures = Column(JSONB, default=dict)  # {"revenue": 150.0, "conversion_rate": 0.03}
    
    # Comparative analytics
    vs_previous_period = Column(Float)
    vs_same_period_last_year = Column(Float)
    industry_benchmark = Column(Float)
    percentile_rank = Column(Float)  # Performance vs other creators
    
    # Predictive analytics
    predicted_next_value = Column(Float)
    trend_direction = Column(String(20))  # "increasing", "decreasing", "stable", "volatile"
    seasonality_factor = Column(Float)
    growth_rate = Column(Float)
    
    # Real-time metrics
    real_time_value = Column(Float)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    update_frequency = Column(String(20), default="hourly")  # "real_time", "hourly", "daily"
    
    # Quality & Validation
    data_quality_score = Column(Float, default=1.0)
    anomaly_detected = Column(Boolean, default=False)
    outlier_flag = Column(Boolean, default=False)
    validation_status = Column(String(20), default="validated")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # System flags
    is_deleted = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="analytics_records")
    content = relationship("ContentModel", back_populates="analytics_records")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_analytics_user_date', 'user_id', 'measurement_date'),
        Index('idx_analytics_content_type', 'content_id', 'analytics_type'),
        Index('idx_analytics_platform_metric', 'platform', 'metric_name'),
        Index('idx_analytics_date_granularity', 'measurement_date', 'time_granularity'),
        Index('idx_analytics_type_category', 'analytics_type', 'metric_category'),
    )
    
    def __repr__(self):
        return f"<AnalyticsModel(id={self.id}, metric='{self.metric_name}', value={self.value})>"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_content_example(user_id: str, content_type: ContentType = ContentType.MUSIC) -> ContentModel:
    """Create example content for testing and development"""
    return ContentModel(
        user_id=user_id,
        content_type=content_type,
        title=f"Sample {content_type.value.title()} Content",
        description="This is a sample content item for testing purposes",
        tags=["sample", "test", content_type.value],
        categories=["entertainment"],
        language="en"
    )


def create_user_example(user_type: UserType = UserType.MUSICIAN) -> UserModel:
    """Create example user for testing and development"""
    return UserModel(
        email=f"test_{user_type.value}@example.com",
        username=f"test_{user_type.value}_{uuid.uuid4().hex[:8]}",
        user_type=user_type,
        display_name=f"Test {user_type.value.title()}",
        bio=f"Sample {user_type.value} profile for testing",
        specializations=[f"{user_type.value}_specialty"]
    )


def create_analytics_example(user_id: str, content_id: str = None, 
                           analytics_type: AnalyticsType = AnalyticsType.VIEWS) -> AnalyticsModel:
    """Create example analytics record for testing and development"""
    return AnalyticsModel(
        user_id=user_id,
        content_id=content_id,
        analytics_type=analytics_type,
        metric_type=MetricType.DAILY,
        time_granularity=TimeGranularity.DAY,
        measurement_date=datetime.utcnow(),
        value=100.0,
        metric_name=f"{analytics_type.value}_count",
        platform="platform_wide"
    )


# ============================================================================
# EXPORT SECTION
# ============================================================================

__all__ = [
    # Base
    'Base',
    
    # Models
    'ContentModel', 'UserModel', 'AnalyticsModel',
    
    # Content Enums
    'ContentType', 'ContentStatus', 'ContentVisibility',
    
    # User Enums
    'UserType', 'UserStatus', 'SubscriptionTier',
    
    # Analytics Enums
    'AnalyticsType', 'MetricType', 'TimeGranularity',
    
    # Utility Functions
    'create_content_example', 'create_user_example', 'create_analytics_example'
]