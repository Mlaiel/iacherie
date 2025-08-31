"""Content Distribution Database Model

Enterprise-grade SQLAlchemy model for managing multi-platform content distribution,
scheduling, syndication, and cross-platform analytics.

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
"""from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class Platform(Enum):
    """Social media and distribution platforms"""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    TUMBLR = "tumblr"
    VIMEO = "vimeo"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    SUBSTACK = "substack"
    MEDIUM = "medium"
    BLOG = "blog"
    WEBSITE = "website"
    EMAIL = "email"
    RSS = "rss"
    PODCAST = "podcast"


class DistributionStatus(Enum):
    """Distribution status enumeration"""    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    REJECTED = "rejected"
    RETRY = "retry"
    PARTIAL_SUCCESS = "partial_success"


class DistributionStrategy(Enum):
    """Distribution strategy types"""    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    OPTIMAL_TIMING = "optimal_timing"
    SEQUENTIAL = "sequential"
    SIMULTANEOUS = "simultaneous"
    STAGGERED = "staggered"
    CONDITIONAL = "conditional"
    AB_TEST = "ab_test"
    PHASED_ROLLOUT = "phased_rollout"
    GEOGRAPHIC_ROLLOUT = "geographic_rollout"
    AUDIENCE_BASED = "audience_based"


class ContentFormat(Enum):
    """Content format adaptations"""    ORIGINAL = "original"
    SQUARE = "square"
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    LONG_FORM = "long_form"
    CAROUSEL = "carousel"
    AUDIO_ONLY = "audio_only"
    VIDEO_ONLY = "video_only"
    THUMBNAIL = "thumbnail"
    PREVIEW = "preview"
    TEASER = "teaser"


class OptimizationType(Enum):
    """Content optimization types"""    NONE = "none"
    RESIZE = "resize"
    COMPRESS = "compress"
    TRANSCODE = "transcode"
    ENHANCE = "enhance"
    FILTER = "filter"
    CROP = "crop"
    WATERMARK = "watermark"
    SUBTITLE = "subtitle"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    METADATA_OPTIMIZATION = "metadata_optimization"
    SEO_OPTIMIZATION = "seo_optimization"
    ACCESSIBILITY = "accessibility"


class SyncStatus(Enum):
    """Synchronization status"""    SYNCED = "synced"
    OUT_OF_SYNC = "out_of_sync"
    SYNC_PENDING = "sync_pending"
    SYNC_FAILED = "sync_failed"
    NEVER_SYNCED = "never_synced"
    PARTIAL_SYNC = "partial_sync"
    CONFLICT = "conflict"


class ContentDistribution(Base):
    """    Enterprise Content Distribution Model
    
    Comprehensive multi-platform content distribution with intelligent scheduling,
    format optimization, analytics tracking, and cross-platform synchronization.
    """    __tablename__ = 'content_distributions'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    distribution_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Content and user references
    content_id = Column(UUID(as_uuid=True), ForeignKey('user_contents.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    campaign_id = Column(String(100), nullable=True, index=True)
    
    # Distribution configuration
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    status = Column(SQLEnum(DistributionStatus), nullable=False, default=DistributionStatus.DRAFT, index=True)
    strategy = Column(SQLEnum(DistributionStrategy), nullable=False, default=DistributionStrategy.IMMEDIATE, index=True)
    
    # Distribution metadata
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    platform_specific_title = Column(String(500), nullable=True)
    platform_specific_description = Column(Text, nullable=True)
    
    # Timing configuration
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Platform configuration
    platform_post_id = Column(String(200), nullable=True, index=True)
    platform_url = Column(Text, nullable=True)
    platform_account_id = Column(String(200), nullable=True, index=True)
    platform_account_name = Column(String(200), nullable=True)
    
    # Content optimization
    content_format = Column(SQLEnum(ContentFormat), nullable=False, default=ContentFormat.ORIGINAL, index=True)
    optimization_type = Column(SQLEnum(OptimizationType), nullable=False, default=OptimizationType.NONE)
    optimized_content_url = Column(Text, nullable=True)
    original_content_url = Column(Text, nullable=True)
    
    # Content adaptations
    adapted_dimensions = Column(String(50), nullable=True)  # "1080x1080"
    adapted_duration = Column(Integer, nullable=True)  # seconds
    adapted_file_size = Column(Integer, nullable=True)  # bytes
    adapted_format = Column(String(20), nullable=True)  # "mp4", "jpg", etc.
    compression_ratio = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)  # 0-100
    
    # Platform-specific metadata
    hashtags = Column(ARRAY(String), nullable=True)
    mentions = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    categories = Column(ARRAY(String), nullable=True)
    custom_fields = Column(JSONB, nullable=True)
    
    # SEO and discoverability
    seo_title = Column(String(200), nullable=True)
    seo_description = Column(Text, nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    preview_url = Column(Text, nullable=True)
    
    # Audience targeting
    target_audience = Column(JSONB, nullable=True)
    geographic_targeting = Column(JSONB, nullable=True)
    demographic_targeting = Column(JSONB, nullable=True)
    interest_targeting = Column(JSONB, nullable=True)
    custom_audiences = Column(ARRAY(String), nullable=True)
    
    # Engagement settings
    comments_enabled = Column(Boolean, nullable=False, default=True)
    likes_enabled = Column(Boolean, nullable=False, default=True)
    shares_enabled = Column(Boolean, nullable=False, default=True)
    downloads_enabled = Column(Boolean, nullable=False, default=False)
    embedding_enabled = Column(Boolean, nullable=False, default=True)
    
    # Privacy and permissions
    visibility = Column(String(50), nullable=False, default="public")  # public, private, unlisted, followers_only
    age_restriction = Column(String(20), nullable=True)
    content_warning = Column(Boolean, nullable=False, default=False)
    copyright_settings = Column(JSONB, nullable=True)
    
    # Analytics and performance
    views_count = Column(Integer, nullable=False, default=0)
    likes_count = Column(Integer, nullable=False, default=0)
    shares_count = Column(Integer, nullable=False, default=0)
    comments_count = Column(Integer, nullable=False, default=0)
    downloads_count = Column(Integer, nullable=False, default=0)
    reach = Column(Integer, nullable=False, default=0)
    impressions = Column(Integer, nullable=False, default=0)
    
    # Engagement metrics
    engagement_rate = Column(Float, nullable=False, default=0.0)
    click_through_rate = Column(Float, nullable=False, default=0.0)
    conversion_rate = Column(Float, nullable=False, default=0.0)
    bounce_rate = Column(Float, nullable=False, default=0.0)
    watch_time_avg = Column(Integer, nullable=True)  # seconds
    completion_rate = Column(Float, nullable=False, default=0.0)
    
    # Platform-specific metrics
    platform_metrics = Column(JSONB, nullable=True)
    algorithm_score = Column(Float, nullable=True)  # Platform algorithm scoring
    trending_score = Column(Float, nullable=True)
    viral_coefficient = Column(Float, nullable=True)
    
    # Revenue tracking
    revenue_generated = Column(Numeric(10, 2), nullable=False, default=0.00)
    ad_revenue = Column(Numeric(10, 2), nullable=False, default=0.00)
    sponsored_revenue = Column(Numeric(10, 2), nullable=False, default=0.00)
    merchandise_revenue = Column(Numeric(10, 2), nullable=False, default=0.00)
    donation_revenue = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Cross-platform synchronization
    sync_status = Column(SQLEnum(SyncStatus), nullable=False, default=SyncStatus.NEVER_SYNCED, index=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_conflicts = Column(JSONB, nullable=True)
    master_platform = Column(SQLEnum(Platform), nullable=True)
    
    # Distribution chain tracking
    parent_distribution_id = Column(UUID(as_uuid=True), ForeignKey('content_distributions.id'), nullable=True)
    child_distributions = Column(ARRAY(String), nullable=True)
    distribution_order = Column(Integer, nullable=True)
    dependency_rules = Column(JSONB, nullable=True)
    
    # A/B testing
    ab_test_variant = Column(String(50), nullable=True, index=True)
    ab_test_group = Column(String(50), nullable=True, index=True)
    control_group = Column(Boolean, nullable=False, default=False)
    conversion_goals = Column(JSONB, nullable=True)
    
    # Automated actions
    auto_repost_enabled = Column(Boolean, nullable=False, default=False)
    auto_repost_interval = Column(Integer, nullable=True)  # hours
    auto_optimize_enabled = Column(Boolean, nullable=False, default=False)
    auto_hashtag_enabled = Column(Boolean, nullable=False, default=False)
    
    # Error handling and retries
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    error_details = Column(JSONB, nullable=True)
    
    # Platform API integration
    api_response = Column(JSONB, nullable=True)
    api_rate_limit_remaining = Column(Integer, nullable=True)
    api_rate_limit_reset = Column(DateTime(timezone=True), nullable=True)
    webhook_url = Column(Text, nullable=True)
    callback_data = Column(JSONB, nullable=True)
    
    # Quality assurance
    content_review_status = Column(String(50), nullable=True)
    automated_checks_passed = Column(Boolean, nullable=False, default=False)
    manual_approval_required = Column(Boolean, nullable=False, default=False)
    compliance_checks = Column(JSONB, nullable=True)
    
    # Performance optimization
    bandwidth_usage = Column(Integer, nullable=True)  # bytes
    cdn_cache_status = Column(String(50), nullable=True)
    load_time_ms = Column(Integer, nullable=True)
    optimization_savings = Column(JSONB, nullable=True)
    
    # Administrative fields
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_featured = Column(Boolean, nullable=False, default=False, index=True)
    is_archived = Column(Boolean, nullable=False, default=False, index=True)
    is_template = Column(Boolean, nullable=False, default=False)
    
    # Audit trail
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    distribution_source = Column(String(100), nullable=False, default="manual")
    version = Column(String(20), nullable=False, default="1.0.0")
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_content_dist_content_platform', 'content_id', 'platform'),
        Index('idx_content_dist_user_status', 'user_id', 'status'),
        Index('idx_content_dist_scheduled_platform', 'scheduled_at', 'platform'),
        Index('idx_content_dist_published_performance', 'published_at', 'engagement_rate'),
        Index('idx_content_dist_campaign_status', 'campaign_id', 'status'),
        Index('idx_content_dist_platform_account', 'platform', 'platform_account_id'),
        Index('idx_content_dist_sync_status', 'sync_status', 'last_sync_at'),
        Index('idx_content_dist_ab_test', 'ab_test_group', 'ab_test_variant'),
        Index('idx_content_dist_active_featured', 'is_active', 'is_featured'),
        Index('idx_content_dist_revenue', 'revenue_generated'),
    )
    
    # Relationships
    content = relationship("UserContent", back_populates="distributions")
    parent_distribution = relationship("ContentDistribution", remote_side=[id])
    
    def __repr__(self):
        return f"<ContentDistribution(id={self.id}, platform={self.platform.value}, status={self.status.value})>"
    
    @classmethod
    def create_scheduled_distribution(
        cls, 
        content_id: str, 
        user_id: str, 
        platform: Platform, 
        scheduled_at: datetime,
        config: Dict[str, Any]
    ) -> 'ContentDistribution':
        """Create scheduled distribution"""        return cls(
            content_id=content_id,
            user_id=user_id,
            platform=platform,
            status=DistributionStatus.SCHEDULED,
            strategy=DistributionStrategy.SCHEDULED,
            scheduled_at=scheduled_at,
            title=config.get('title', ''),
            description=config.get('description', ''),
            hashtags=config.get('hashtags', []),
            created_by=config.get('created_by', 'system')
        )
    
    @classmethod
    def create_immediate_distribution(
        cls, 
        content_id: str, 
        user_id: str, 
        platform: Platform,
        config: Dict[str, Any]
    ) -> 'ContentDistribution':
        """Create immediate distribution"""        return cls(
            content_id=content_id,
            user_id=user_id,
            platform=platform,
            status=DistributionStatus.PENDING,
            strategy=DistributionStrategy.IMMEDIATE,
            title=config.get('title', ''),
            description=config.get('description', ''),
            hashtags=config.get('hashtags', []),
            created_by=config.get('created_by', 'system')
        )
    
    def update_engagement_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update engagement metrics"""        self.views_count = metrics.get('views', self.views_count)
        self.likes_count = metrics.get('likes', self.likes_count)
        self.shares_count = metrics.get('shares', self.shares_count)
        self.comments_count = metrics.get('comments', self.comments_count)
        self.reach = metrics.get('reach', self.reach)
        self.impressions = metrics.get('impressions', self.impressions)
        
        # Calculate engagement rate
        if self.impressions > 0:
            total_engagement = self.likes_count + self.shares_count + self.comments_count
            self.engagement_rate = (total_engagement / self.impressions) * 100
        
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_as_published(self, platform_post_id: str, platform_url: str) -> None:
        """Mark distribution as published"""        self.status = DistributionStatus.PUBLISHED
        self.published_at = datetime.now(timezone.utc)
        self.platform_post_id = platform_post_id
        self.platform_url = platform_url
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_as_failed(self, error_message: str, error_details: Dict[str, Any] = None) -> None:
        """Mark distribution as failed"""        self.status = DistributionStatus.FAILED
        self.error_message = error_message
        self.error_details = error_details or {}
        self.last_error_at = datetime.now(timezone.utc)
        self.retry_count += 1
        self.updated_at = datetime.now(timezone.utc)
    
    def can_retry(self) -> bool:
        """Check if distribution can be retried"""        return (
            self.status == DistributionStatus.FAILED and
            self.retry_count < self.max_retries
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""        return {
            'engagement_metrics': {
                'views': self.views_count,
                'likes': self.likes_count,
                'shares': self.shares_count,
                'comments': self.comments_count,
                'engagement_rate': self.engagement_rate,
                'reach': self.reach,
                'impressions': self.impressions
            },
            'revenue_metrics': {
                'total_revenue': float(self.revenue_generated),
                'ad_revenue': float(self.ad_revenue),
                'sponsored_revenue': float(self.sponsored_revenue),
                'merchandise_revenue': float(self.merchandise_revenue)
            },
            'platform_info': {
                'platform': self.platform.value,
                'platform_post_id': self.platform_post_id,
                'platform_url': self.platform_url,
                'published_at': self.published_at.isoformat() if self.published_at else None
            }
        }
    
    def calculate_roi(self) -> float:
        """Calculate return on investment"""        # This would include cost calculation in a real implementation
        if self.revenue_generated > 0:
            # Simplified ROI calculation
            return float(self.revenue_generated) * 100
        return 0.0
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on performance"""        recommendations = []
        
        if self.engagement_rate < 2.0:
            recommendations.append("Consider improving content quality or posting time")
        
        if self.completion_rate < 0.5:
            recommendations.append("Content may be too long for this platform")
        
        if self.click_through_rate < 1.0:
            recommendations.append("Improve title and thumbnail to increase clicks")
        
        if len(self.hashtags or []) < 3:
            recommendations.append("Add more relevant hashtags to improve discoverability")
        
        return recommendations
