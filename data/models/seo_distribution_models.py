"""SEO Distribution Models
======================

Advanced SEO optimization and distribution models for IA Influencer Agent platform.
AI-powered SEO optimization with multi-platform distribution automation,
search ranking monitoring, and content discoverability enhancement.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

🚀 ENTERPRISE FEATURES:
• AI-powered SEO optimization
• Multi-platform distribution automation (35+ platforms)
• Search ranking monitoring & improvement
• Platform-specific optimization strategies
• Content discoverability enhancement
• Social signal tracking & optimization
• Performance analytics & reporting
• Automated metadata generation
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

# Import base from enterprise content models
from .enterprise_content_models import Base

# ============================================================================
# ENUMS - SEO System
# ============================================================================

class SEOMetric(Enum):
    """SEO performance metrics"""
    RANKING = "ranking"
    VISIBILITY = "visibility"
    CLICK_THROUGH_RATE = "click_through_rate"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    ENGAGEMENT = "engagement"
    BOUNCE_RATE = "bounce_rate"
    TIME_ON_PAGE = "time_on_page"
    CONVERSION_RATE = "conversion_rate"
    BACKLINKS = "backlinks"
    DOMAIN_AUTHORITY = "domain_authority"
    PAGE_SPEED = "page_speed"
    MOBILE_FRIENDLINESS = "mobile_friendliness"
    SOCIAL_SIGNALS = "social_signals"
    FEATURED_SNIPPETS = "featured_snippets"


class SEOStrategy(Enum):
    """SEO optimization strategies"""
    KEYWORDS = "keywords"
    METADATA = "metadata"
    CONTENT_OPTIMIZATION = "content_optimization"
    TECHNICAL_SEO = "technical_seo"
    LINK_BUILDING = "link_building"
    SOCIAL_SIGNALS = "social_signals"
    LOCAL_SEO = "local_seo"
    MOBILE_OPTIMIZATION = "mobile_optimization"
    VOICE_SEARCH = "voice_search"
    FEATURED_SNIPPETS = "featured_snippets"
    IMAGE_SEO = "image_seo"
    VIDEO_SEO = "video_seo"
    SCHEMA_MARKUP = "schema_markup"
    CORE_WEB_VITALS = "core_web_vitals"


class RankingFactor(Enum):
    """Search ranking factors"""
    RELEVANCE = "relevance"
    AUTHORITY = "authority"
    FRESHNESS = "freshness"
    ENGAGEMENT = "engagement"
    TECHNICAL_QUALITY = "technical_quality"
    USER_EXPERIENCE = "user_experience"
    MOBILE_OPTIMIZATION = "mobile_optimization"
    PAGE_SPEED = "page_speed"
    SECURITY = "security"
    CONTENT_QUALITY = "content_quality"
    SOCIAL_SIGNALS = "social_signals"
    BACKLINK_QUALITY = "backlink_quality"
    CLICK_THROUGH_RATE = "click_through_rate"
    DWELL_TIME = "dwell_time"


class OptimizationLevel(Enum):
    """Levels of SEO optimization"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    AI_POWERED = "ai_powered"
    CUSTOM = "custom"


# ============================================================================
# ENUMS - Distribution System
# ============================================================================

class DistributionPlatform(Enum):
    """Supported distribution platforms (35+ platforms)"""
    # Video Platforms
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    TWITCH = "twitch"
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"
    FACEBOOK_VIDEO = "facebook_video"
    
    # Music Platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    TIDAL = "tidal"
    YOUTUBE_MUSIC = "youtube_music"
    
    # Social Media
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    DISCORD = "discord"
    
    # Podcast Platforms
    APPLE_PODCASTS = "apple_podcasts"
    SPOTIFY_PODCASTS = "spotify_podcasts"
    GOOGLE_PODCASTS = "google_podcasts"
    ANCHOR = "anchor"
    STITCHER = "stitcher"
    
    # Professional/Business
    MEDIUM = "medium"
    SUBSTACK = "substack"
    WORDPRESS = "wordpress"
    WATTPAD = "wattpad"
    
    # Emerging Platforms
    CLUBHOUSE = "clubhouse"
    SPACES = "spaces"
    MASTODON = "mastodon"


class DistributionStatus(Enum):
    """Status of content distribution"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    OPTIMIZED = "optimized"
    FAILED = "failed"
    REJECTED = "rejected"
    REMOVED = "removed"
    UPDATING = "updating"
    ARCHIVED = "archived"


class DistributionMethod(Enum):
    """Methods of content distribution"""
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    API_INTEGRATION = "api_integration"
    CROSS_POSTING = "cross_posting"
    SYNDICATION = "syndication"
    RSS_FEED = "rss_feed"
    WEBHOOK = "webhook"


# ============================================================================
# SEO MODELS
# ============================================================================

class SEOOptimizationModel(Base):
    """
    Enterprise SEO optimization model for comprehensive SEO management.
    AI-powered SEO optimization with performance tracking and analytics.
    """
    __tablename__ = 'seo_optimization'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # SEO Configuration
    optimization_level = Column(SQLEnum(OptimizationLevel), nullable=False, default=OptimizationLevel.STANDARD, index=True)
    strategy = Column(SQLEnum(SEOStrategy), nullable=False, index=True)
    target_keywords = Column(JSONB, default=list)  # Primary keywords
    secondary_keywords = Column(JSONB, default=list)  # Secondary keywords
    long_tail_keywords = Column(JSONB, default=list)  # Long-tail keywords
    
    # Metadata Optimization
    optimized_title = Column(String(500))
    optimized_description = Column(Text)
    meta_keywords = Column(JSONB, default=list)
    alt_text = Column(JSONB, default=dict)  # For images
    canonical_url = Column(String(1000))
    open_graph_data = Column(JSONB, default=dict)
    twitter_card_data = Column(JSONB, default=dict)
    
    # Content Optimization
    content_score = Column(Float, default=0.0)  # 0-100 SEO content score
    keyword_density = Column(JSONB, default=dict)  # {"keyword": density}
    readability_score = Column(Float, default=0.0)  # Flesch reading ease
    content_length = Column(Integer)  # Character count
    heading_structure = Column(JSONB, default=dict)  # H1, H2, H3 analysis
    
    # Technical SEO
    page_speed_score = Column(Float, default=0.0)  # 0-100 PageSpeed score
    mobile_friendliness = Column(Float, default=0.0)  # 0-100 mobile score
    core_web_vitals = Column(JSONB, default=dict)  # LCP, FID, CLS scores
    schema_markup = Column(JSONB, default=dict)  # Structured data
    sitemap_included = Column(Boolean, default=False)
    robots_meta = Column(String(200))
    
    # Performance Metrics
    current_ranking = Column(JSONB, default=dict)  # {"keyword": ranking}
    ranking_history = Column(JSONB, default=list)  # Historical rankings
    visibility_score = Column(Float, default=0.0)  # 0-100 visibility
    click_through_rate = Column(Float, default=0.0)  # CTR percentage
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    
    # Search Console Data
    search_console_connected = Column(Boolean, default=False)
    average_position = Column(Float)
    total_impressions = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    search_console_ctr = Column(Float, default=0.0)
    
    # Analytics & Insights
    organic_traffic = Column(Integer, default=0)
    bounce_rate = Column(Float, default=0.0)
    average_session_duration = Column(Float, default=0.0)
    pages_per_session = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    # Competitive Analysis
    competitor_analysis = Column(JSONB, default=dict)
    market_share = Column(Float, default=0.0)
    competitive_keywords = Column(JSONB, default=list)
    ranking_gaps = Column(JSONB, default=list)
    opportunity_keywords = Column(JSONB, default=list)
    
    # Link Building
    internal_links = Column(Integer, default=0)
    external_links = Column(Integer, default=0)
    backlinks_count = Column(Integer, default=0)
    referring_domains = Column(Integer, default=0)
    domain_authority = Column(Float, default=0.0)
    link_quality_score = Column(Float, default=0.0)
    
    # AI Optimization
    ai_suggestions = Column(JSONB, default=list)
    ai_optimization_applied = Column(Boolean, default=False)
    ai_confidence_score = Column(Float, default=0.0)
    ai_performance_prediction = Column(JSONB, default=dict)
    auto_optimization_enabled = Column(Boolean, default=True)
    
    # Local SEO (if applicable)
    local_optimization = Column(Boolean, default=False)
    business_listings = Column(JSONB, default=list)
    local_citations = Column(Integer, default=0)
    google_my_business_score = Column(Float, default=0.0)
    local_pack_ranking = Column(JSONB, default=dict)
    
    # Social Signals
    social_shares = Column(Integer, default=0)
    social_mentions = Column(Integer, default=0)
    social_engagement_score = Column(Float, default=0.0)
    viral_coefficient = Column(Float, default=0.0)
    
    # Monitoring & Alerts
    monitoring_enabled = Column(Boolean, default=True)
    alert_thresholds = Column(JSONB, default=dict)
    last_check_date = Column(DateTime(timezone=True))
    next_check_date = Column(DateTime(timezone=True))
    anomaly_detected = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_optimized_at = Column(DateTime(timezone=True))
    last_ranking_update = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True, index=True)
    is_auto_optimized = Column(Boolean, default=False)
    is_manual_override = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    content = relationship("ContentModel", backref="seo_optimization")
    user = relationship("UserModel", backref="seo_optimizations")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_seo_content_strategy', 'content_id', 'strategy'),
        Index('idx_seo_user_level', 'user_id', 'optimization_level'),
        Index('idx_seo_ranking_visibility', 'visibility_score', 'content_score'),
        Index('idx_seo_active_updated', 'is_active', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<SEOOptimizationModel(id={self.id}, strategy={self.strategy.value}, score={self.content_score})>"


# ============================================================================
# DISTRIBUTION MODELS
# ============================================================================

class DistributionModel(Base):
    """
    Enterprise distribution model for multi-platform content distribution.
    Automated distribution with platform-specific optimization and tracking.
    """
    __tablename__ = 'distribution'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Distribution Configuration
    platform = Column(SQLEnum(DistributionPlatform), nullable=False, index=True)
    status = Column(SQLEnum(DistributionStatus), nullable=False, default=DistributionStatus.PENDING, index=True)
    method = Column(SQLEnum(DistributionMethod), nullable=False, default=DistributionMethod.AUTOMATIC)
    
    # Platform-specific details
    platform_content_id = Column(String(200))  # ID on the target platform
    platform_url = Column(String(1000))  # URL on the target platform
    platform_username = Column(String(200))  # Username/channel on platform
    platform_account_id = Column(String(200))  # Account ID on platform
    
    # Content adaptation
    adapted_title = Column(String(500))
    adapted_description = Column(Text)
    adapted_tags = Column(JSONB, default=list)
    adapted_thumbnail = Column(String(1000))
    adapted_format = Column(String(100))
    content_modifications = Column(JSONB, default=dict)
    
    # Scheduling & Timing
    scheduled_publish_time = Column(DateTime(timezone=True))
    optimal_publish_time = Column(DateTime(timezone=True))
    time_zone = Column(String(50))
    frequency = Column(String(50))  # "once", "daily", "weekly", etc.
    recurring_schedule = Column(JSONB, default=dict)
    
    # Platform-specific settings
    platform_settings = Column(JSONB, default=dict)  # Platform-specific configuration
    visibility_settings = Column(JSONB, default=dict)  # Privacy/visibility settings
    monetization_settings = Column(JSONB, default=dict)  # Monetization configuration
    audience_targeting = Column(JSONB, default=dict)  # Audience targeting settings
    
    # Performance Tracking
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    
    # Analytics Integration
    analytics_connected = Column(Boolean, default=False)
    analytics_id = Column(String(200))
    analytics_data = Column(JSONB, default=dict)
    utm_parameters = Column(JSONB, default=dict)
    conversion_tracking = Column(Boolean, default=False)
    roi_tracking = Column(Boolean, default=False)
    
    # Platform API Integration
    api_connected = Column(Boolean, default=False)
    api_key_id = Column(String(200))  # Reference to stored API key
    oauth_token_id = Column(String(200))  # Reference to stored OAuth token
    api_rate_limit = Column(Integer)
    api_calls_used = Column(Integer, default=0)
    api_last_sync = Column(DateTime(timezone=True))
    
    # Content Compliance
    platform_guidelines_check = Column(Boolean, default=False)
    content_warnings = Column(JSONB, default=list)
    age_restrictions = Column(String(50))
    geographic_restrictions = Column(JSONB, default=list)
    copyright_status = Column(String(100))
    
    # Optimization Features
    hashtag_optimization = Column(Boolean, default=True)
    optimal_hashtags = Column(JSONB, default=list)
    thumbnail_optimization = Column(Boolean, default=True)
    title_optimization = Column(Boolean, default=True)
    description_optimization = Column(Boolean, default=True)
    
    # Cross-platform Features
    cross_promotion = Column(Boolean, default=False)
    cross_platform_links = Column(JSONB, default=dict)
    unified_analytics = Column(Boolean, default=True)
    brand_consistency_check = Column(Boolean, default=True)
    
    # Error Handling & Retry
    error_count = Column(Integer, default=0)
    last_error_message = Column(Text)
    last_error_code = Column(String(50))
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime(timezone=True))
    
    # Publishing Results
    published_at = Column(DateTime(timezone=True))
    publishing_duration = Column(Float)  # seconds
    file_upload_size = Column(Integer)  # bytes
    upload_speed = Column(Float)  # MB/s
    processing_time = Column(Float)  # platform processing time
    
    # Revenue & Monetization
    revenue_enabled = Column(Boolean, default=False)
    revenue_generated = Column(Float, default=0.0)
    ad_revenue = Column(Float, default=0.0)
    subscription_revenue = Column(Float, default=0.0)
    donation_revenue = Column(Float, default=0.0)
    
    # Audience Analytics
    audience_demographics = Column(JSONB, default=dict)
    audience_geography = Column(JSONB, default=dict)
    audience_interests = Column(JSONB, default=dict)
    audience_behavior = Column(JSONB, default=dict)
    audience_growth = Column(JSONB, default=dict)
    
    # Performance Comparison
    platform_benchmark = Column(Float, default=0.0)
    industry_benchmark = Column(Float, default=0.0)
    performance_rank = Column(Integer)
    relative_performance = Column(Float, default=1.0)  # vs average
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_sync_at = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True, index=True)
    is_priority = Column(Boolean, default=False)
    is_test_distribution = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    content = relationship("ContentModel", backref="distributions")
    user = relationship("UserModel", backref="distributions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_distribution_platform_status', 'platform', 'status'),
        Index('idx_distribution_content_user', 'content_id', 'user_id'),
        Index('idx_distribution_scheduled_time', 'scheduled_publish_time'),
        Index('idx_distribution_performance', 'engagement_rate', 'views'),
    )
    
    def __repr__(self):
        return f"<DistributionModel(id={self.id}, platform={self.platform.value}, status={self.status.value})>"


class SearchRankingModel(Base):
    """
    Search ranking tracking model for monitoring search performance.
    Comprehensive ranking tracking across search engines and platforms.
    """
    __tablename__ = 'search_rankings'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=False, index=True)
    seo_optimization_id = Column(UUID(as_uuid=True), ForeignKey('seo_optimization.id'), nullable=False, index=True)
    
    # Search details
    search_engine = Column(String(50), nullable=False, index=True)  # "google", "bing", "youtube", etc.
    keyword = Column(String(300), nullable=False, index=True)
    search_query = Column(String(500))  # Full search query if different
    search_location = Column(String(100))  # Geographic location
    search_device = Column(String(50))  # "desktop", "mobile", "tablet"
    
    # Ranking information
    current_position = Column(Integer, index=True)
    previous_position = Column(Integer)
    best_position = Column(Integer)
    worst_position = Column(Integer)
    position_change = Column(Integer, default=0)
    
    # Search results context
    total_results = Column(Integer)
    search_page = Column(Integer, default=1)  # Which page of results
    featured_snippet = Column(Boolean, default=False)
    knowledge_graph = Column(Boolean, default=False)
    local_pack = Column(Boolean, default=False)
    image_pack = Column(Boolean, default=False)
    video_pack = Column(Boolean, default=False)
    
    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    click_through_rate = Column(Float, default=0.0)
    average_position = Column(Float)
    visibility_percentage = Column(Float, default=0.0)
    
    # Ranking factors analysis
    ranking_factors = Column(JSONB, default=dict)  # Analysis of ranking factors
    content_relevance_score = Column(Float, default=0.0)
    authority_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    user_experience_score = Column(Float, default=0.0)
    
    # Competitive analysis
    competitors_above = Column(JSONB, default=list)  # URLs ranking above
    competitors_below = Column(JSONB, default=list)  # URLs ranking below
    market_share = Column(Float, default=0.0)
    competitive_gap = Column(Float, default=0.0)
    
    # Historical tracking
    ranking_history = Column(JSONB, default=list)  # Historical positions
    trend_direction = Column(String(20))  # "rising", "falling", "stable"
    volatility_score = Column(Float, default=0.0)  # How much rankings fluctuate
    stability_score = Column(Float, default=0.0)  # Ranking stability
    
    # Measurement details
    measurement_date = Column(DateTime(timezone=True), nullable=False, index=True)
    measurement_tool = Column(String(100))  # Tool used for measurement
    data_accuracy = Column(Float, default=0.95)  # Confidence in data
    sample_size = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # System flags
    is_tracked = Column(Boolean, default=True)
    is_target_keyword = Column(Boolean, default=False)  # Priority keyword
    is_anomaly = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    content = relationship("ContentModel", backref="search_rankings")
    seo_optimization = relationship("SEOOptimizationModel", backref="search_rankings")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_ranking_keyword_engine', 'keyword', 'search_engine'),
        Index('idx_ranking_content_position', 'content_id', 'current_position'),
        Index('idx_ranking_date_tracked', 'measurement_date', 'is_tracked'),
    )
    
    def __repr__(self):
        return f"<SearchRankingModel(id={self.id}, keyword='{self.keyword}', position={self.current_position})>"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_seo_optimization_example(content_id: str, user_id: str) -> SEOOptimizationModel:
    """Create example SEO optimization for testing and development"""
    return SEOOptimizationModel(
        content_id=content_id,
        user_id=user_id,
        strategy=SEOStrategy.KEYWORDS,
        target_keywords=["sample", "test", "content"],
        optimized_title="Sample Optimized Title",
        optimized_description="This is a sample optimized description for testing purposes",
        content_score=75.0,
        optimization_level=OptimizationLevel.STANDARD
    )


def create_distribution_example(content_id: str, user_id: str, 
                              platform: DistributionPlatform = DistributionPlatform.YOUTUBE) -> DistributionModel:
    """Create example distribution for testing and development"""
    return DistributionModel(
        content_id=content_id,
        user_id=user_id,
        platform=platform,
        adapted_title=f"Sample Content for {platform.value.title()}",
        adapted_description="This is sample content adapted for the platform",
        adapted_tags=["sample", "test", platform.value],
        method=DistributionMethod.AUTOMATIC
    )


def calculate_seo_score(metrics: Dict[str, float]) -> float:
    """Calculate overall SEO score from various metrics"""
    weights = {
        'content_score': 0.25,
        'technical_score': 0.20,
        'ranking_score': 0.20,
        'engagement_score': 0.15,
        'authority_score': 0.10,
        'social_signals': 0.10
    }
    
    weighted_score = 0.0
    total_weight = 0.0
    
    for metric, weight in weights.items():
        if metric in metrics:
            weighted_score += metrics[metric] * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    return round(weighted_score / total_weight, 2)


def recommend_optimal_publish_time(platform: DistributionPlatform, 
                                 audience_timezone: str = "UTC",
                                 audience_demographics: Dict[str, Any] = None) -> datetime:
    """Recommend optimal publish time based on platform and audience"""
    # Platform-specific optimal times (simplified example)
    optimal_times = {
        DistributionPlatform.YOUTUBE: {"hour": 14, "minute": 0},  # 2 PM
        DistributionPlatform.INSTAGRAM: {"hour": 17, "minute": 0},  # 5 PM
        DistributionPlatform.TIKTOK: {"hour": 18, "minute": 0},  # 6 PM
        DistributionPlatform.TWITTER: {"hour": 12, "minute": 0},  # 12 PM
        DistributionPlatform.LINKEDIN: {"hour": 10, "minute": 0},  # 10 AM
    }
    
    default_time = {"hour": 15, "minute": 0}  # 3 PM default
    optimal = optimal_times.get(platform, default_time)
    
    # In production, this would consider:
    # - Audience demographics
    # - Time zone
    # - Historical performance data
    # - Platform-specific algorithms
    
    now = datetime.utcnow()
    optimal_datetime = now.replace(
        hour=optimal["hour"], 
        minute=optimal["minute"], 
        second=0, 
        microsecond=0
    )
    
    # If optimal time has passed today, schedule for next day
    if optimal_datetime <= now:
        optimal_datetime = optimal_datetime.replace(day=optimal_datetime.day + 1)
    
    return optimal_datetime


def generate_platform_hashtags(content_title: str, content_tags: List[str],
                             platform: DistributionPlatform) -> List[str]:
    """Generate platform-optimized hashtags"""
    base_hashtags = [tag.replace(" ", "").replace("-", "").lower() for tag in content_tags]
    
    # Platform-specific hashtag strategies
    if platform == DistributionPlatform.INSTAGRAM:
        # Instagram allows up to 30 hashtags
        additional_tags = ["insta", "instagram", "content", "creator"]
        return (base_hashtags + additional_tags)[:30]
    
    elif platform == DistributionPlatform.TIKTOK:
        # TikTok trending hashtags
        additional_tags = ["tiktok", "viral", "fyp", "foryou"]
        return (base_hashtags + additional_tags)[:10]
    
    elif platform == DistributionPlatform.TWITTER:
        # Twitter hashtag limit
        return base_hashtags[:3]
    
    else:
        return base_hashtags[:10]


# ============================================================================
# EXPORT SECTION
# ============================================================================

__all__ = [
    # Models
    'SEOOptimizationModel', 'DistributionModel', 'SearchRankingModel',
    
    # SEO Enums
    'SEOMetric', 'SEOStrategy', 'RankingFactor', 'OptimizationLevel',
    
    # Distribution Enums
    'DistributionPlatform', 'DistributionStatus', 'DistributionMethod',
    
    # Utility Functions
    'create_seo_optimization_example', 'create_distribution_example',
    'calculate_seo_score', 'recommend_optimal_publish_time', 'generate_platform_hashtags'
]