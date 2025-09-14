"""Distribution & Platform Integration Schemas for IA Influencer Agent Platform
Professional multi-platform distribution, content delivery, and platform integration schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from pydantic import Field, HttpUrl, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class DistributionRequest(BaseSchema):
    """
Content distribution request schema."""
    
    content_id: UUID = Field(description="Content to distribute")
    creator_id: UUID = Field(description="Content creator")
    distribution_name: str = Field(description="Distribution campaign name")
    distribution_type: str = Field(description="Type of distribution")
    
    # Target platforms
    target_platforms: List[str] = Field(description="Platforms for distribution")
    platform_specific_settings: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    priority_platforms: List[str] = Field(default_factory=list)
    
    # Distribution settings
    release_date: datetime = Field(description="Scheduled release date")
    release_type: str = Field(default="standard", description="Release type")
    embargo_settings: Optional[Dict[str, datetime]] = Field(None, description="Platform-specific embargo")
    
    # Content optimization
    auto_optimization: bool = Field(default=True, description="Enable platform optimization")
    format_conversion: Dict[str, List[str]] = Field(default_factory=dict)
    quality_presets: Dict[str, str] = Field(default_factory=dict)
    metadata_customization: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Geographic distribution
    global_distribution: bool = Field(default=True)
    included_territories: List[str] = Field(default_factory=list)
    excluded_territories: List[str] = Field(default_factory=list)
    regional_variations: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Monetization settings
    monetization_enabled: bool = Field(default=True)
    pricing_strategy: Dict[str, Decimal] = Field(default_factory=dict)
    subscription_tier_access: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Marketing and promotion
    promotional_assets: List[Dict[str, str]] = Field(default_factory=list)
    marketing_campaign_integration: bool = Field(default=False)
    social_media_auto_post: bool = Field(default=False)
    press_release_generation: bool = Field(default=False)
    
    @validator('distribution_type')
    def validate_distribution_type(cls, v) -> None:
        """Validate distribution type."""
        allowed_types = {
            "single_release", "album_release", "ep_release", "compilation",
            "live_recording", "remix_package", "deluxe_edition", "remaster",
            "video_content", "podcast_episode", "audiobook", "educational_content"
        }
        if v not in allowed_types:
            raise ValueError(f'Distribution type must be one of: {", ".join(allowed_types)}')
        return v


class DistributionOut(UUIDSchema, TimestampSchema):
    """Distribution status and information schema."""
    
    content_id: UUID
    creator_id: UUID
    distribution_name: str
    distribution_type: str
    
    # Distribution status
    overall_status: str = Field(description="Overall distribution status")
    release_date: datetime
    actual_release_date: Optional[datetime] = None
    distribution_progress: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Platform status
    platform_statuses: Dict[str, str] = Field(default_factory=dict, description="Status per platform")
    successful_platforms: List[str] = Field(default_factory=list)
    failed_platforms: List[str] = Field(default_factory=list)
    pending_platforms: List[str] = Field(default_factory=list)
    
    # Distribution URLs
    platform_urls: Dict[str, HttpUrl] = Field(default_factory=dict)
    universal_link: Optional[HttpUrl] = Field(None, description="Universal distribution link")
    qr_code_url: Optional[HttpUrl] = Field(None, description="QR code for easy sharing")
    
    # Performance metrics
    total_views: int = Field(default=0, ge=0)
    total_downloads: int = Field(default=0, ge=0)
    total_streams: int = Field(default=0, ge=0)
    engagement_rate: float = Field(default=0.0, ge=0.0)
    
    # Geographic performance
    top_territories: List[Dict[str, Any]] = Field(default_factory=list)
    territory_performance: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    
    # Revenue tracking
    total_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    revenue_by_platform: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Quality and compliance
    content_quality_scores: Dict[str, float] = Field(default_factory=dict)
    compliance_status: Dict[str, str] = Field(default_factory=dict)
    copyright_clearance: Dict[str, bool] = Field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Calculate distribution success rate."""
        total_platforms = len(self.platform_statuses)
        if total_platforms == 0:
            return 0.0
        return len(self.successful_platforms) / total_platforms


class PlatformIntegration(UUIDSchema, TimestampSchema, AuditSchema):
    """
Platform integration configuration schema."""
    
    creator_id: UUID = Field(description="Creator setting up integration")
    platform_name: str = Field(description="Platform name")
    integration_type: str = Field(description="Type of integration")
    
    # Authentication and credentials
    authentication_method: str = Field(description="Authentication method used")
    api_credentials: Dict[str, str] = Field(description="API credentials (encrypted)")
    oauth_tokens: Dict[str, str] = Field(default_factory=dict, description="OAuth tokens")
    refresh_token: Optional[str] = Field(None, description="Refresh token for auth renewal")
    
    # Integration settings
    sync_frequency: str = Field(default="daily", description="Data synchronization frequency")
    auto_upload: bool = Field(default=False, description="Automatic content upload")
    auto_metadata_sync: bool = Field(default=True, description="Automatic metadata sync")
    bidirectional_sync: bool = Field(default=False, description="Two-way synchronization")
    
    # Platform-specific configuration
    platform_settings: Dict[str, Any] = Field(default_factory=dict)
    content_mapping: Dict[str, str] = Field(default_factory=dict, description="Content type mapping")
    metadata_mapping: Dict[str, str] = Field(default_factory=dict, description="Metadata field mapping")
    
    # Integration status
    integration_status: str = Field(default="active", description="Current integration status")
    last_sync_date: Optional[datetime] = None
    next_sync_date: Optional[datetime] = None
    sync_error_count: int = Field(default=0, ge=0)
    last_error_message: Optional[str] = None
    
    # Performance metrics
    total_uploads: int = Field(default=0, ge=0)
    successful_uploads: int = Field(default=0, ge=0)
    failed_uploads: int = Field(default=0, ge=0)
    average_upload_time: Optional[float] = None
    
    # Rate limiting and quotas
    api_rate_limits: Dict[str, int] = Field(default_factory=dict)
    quota_usage: Dict[str, int] = Field(default_factory=dict)
    quota_reset_date: Optional[datetime] = None
    
    # Security and compliance
    encryption_enabled: bool = Field(default=True)
    data_retention_policy: str = Field(default="platform_default")
    privacy_settings: Dict[str, bool] = Field(default_factory=dict)
    compliance_requirements: List[str] = Field(default_factory=list)
    
    @validator('platform_name')
    def validate_platform_name(cls, v) -> None:
        """Validate platform name."""
        allowed_platforms = {
            "spotify", "apple_music", "youtube", "youtube_music", "amazon_music",
            "deezer", "tidal", "soundcloud", "bandcamp", "instagram", "tiktok",
            "facebook", "twitter", "linkedin", "twitch", "discord", "patreon"
        }
        if v.lower() not in allowed_platforms:
            raise ValueError(f'Platform must be one of: {", ".join(allowed_platforms)}')
        return v.lower()


class ContentDelivery(UUIDSchema, TimestampSchema):
    """Content delivery network and optimization schema."""
    
    content_id: UUID
    delivery_method: str = Field(description="Content delivery method")
    cdn_provider: str = Field(description="CDN provider")
    
    # Delivery configuration
    edge_locations: List[str] = Field(default_factory=list, description="CDN edge locations")
    caching_strategy: str = Field(default="optimal", description="Content caching strategy")
    compression_enabled: bool = Field(default=True)
    optimization_level: str = Field(default="balanced", description="Delivery optimization level")
    
    # Performance settings
    streaming_quality_options: List[str] = Field(default_factory=list)
    adaptive_bitrate_enabled: bool = Field(default=True)
    preload_strategy: str = Field(default="metadata", description="Content preload strategy")
    
    # Security and access control
    secure_delivery: bool = Field(default=True)
    access_control_enabled: bool = Field(default=False)
    geo_blocking: List[str] = Field(default_factory=list, description="Geo-blocked territories")
    token_authentication: bool = Field(default=False)
    
    # Delivery URLs and endpoints
    primary_delivery_url: HttpUrl = Field(description="Primary content delivery URL")
    backup_delivery_urls: List[HttpUrl] = Field(default_factory=list)
    streaming_endpoints: Dict[str, HttpUrl] = Field(default_factory=dict)
    download_endpoints: Dict[str, HttpUrl] = Field(default_factory=dict)
    
    # Performance metrics
    cache_hit_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    average_response_time: float = Field(default=0.0, ge=0.0, description="Response time in ms")
    bandwidth_usage: float = Field(default=0.0, ge=0.0, description="Bandwidth usage in GB")
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Cost tracking
    delivery_costs: Decimal = Field(default=Decimal('0.00'), ge=0)
    bandwidth_costs: Decimal = Field(default=Decimal('0.00'), ge=0)
    storage_costs: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    @validator('delivery_method')
    def validate_delivery_method(cls, v) -> None:
        """Validate delivery method."""
        allowed_methods = {
            "progressive_download", "adaptive_streaming", "live_streaming",
            "on_demand_streaming", "cached_delivery", "direct_download"
        }
        if v not in allowed_methods:
            raise ValueError(f'Delivery method must be one of: {", ".join(allowed_methods)}')
        return v


class DistributionMetrics(UUIDSchema, TimestampSchema):
    """Distribution performance metrics schema."""
    
    distribution_id: UUID
    metrics_period_start: datetime
    metrics_period_end: datetime
    
    # Reach and engagement metrics
    total_impressions: int = Field(default=0, ge=0)
    total_reach: int = Field(default=0, ge=0)
    unique_listeners: int = Field(default=0, ge=0)
    engagement_rate: float = Field(default=0.0, ge=0.0)
    
    # Performance by platform
    platform_performance: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    top_performing_platforms: List[Dict[str, Any]] = Field(default_factory=list)
    platform_growth_rates: Dict[str, float] = Field(default_factory=dict)
    
    # Geographic performance
    performance_by_territory: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    top_territories: List[Dict[str, Any]] = Field(default_factory=list)
    geographic_spread: float = Field(default=0.0, ge=0.0, description="Geographic diversity score")
    
    # Audience demographics
    age_demographics: Dict[str, float] = Field(default_factory=dict)
    gender_demographics: Dict[str, float] = Field(default_factory=dict)
    device_usage: Dict[str, float] = Field(default_factory=dict)
    listening_patterns: Dict[str, Any] = Field(default_factory=dict)
    
    # Conversion and monetization
    conversion_rates: Dict[str, float] = Field(default_factory=dict)
    revenue_per_platform: Dict[str, Decimal] = Field(default_factory=dict)
    average_revenue_per_user: Decimal = Field(default=Decimal('0.00'), ge=0)
    lifetime_value_estimates: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Quality metrics
    content_completion_rates: Dict[str, float] = Field(default_factory=dict)
    skip_rates: Dict[str, float] = Field(default_factory=dict)
    repeat_listening_rate: float = Field(default=0.0, ge=0.0)
    user_satisfaction_scores: Dict[str, float] = Field(default_factory=dict)
    
    # Trend analysis
    growth_trends: Dict[str, List[float]] = Field(default_factory=dict)
    seasonal_patterns: Dict[str, float] = Field(default_factory=dict)
    viral_coefficient: Optional[float] = Field(None, description="Viral growth coefficient")
    
    # Competitive analysis
    market_share_estimates: Dict[str, float] = Field(default_factory=dict)
    competitive_positioning: Dict[str, Any] = Field(default_factory=dict)
    benchmark_comparisons: Dict[str, float] = Field(default_factory=dict)


class PlatformAnalytics(UUIDSchema, TimestampSchema):
    """Platform-specific analytics schema."""
    
    creator_id: UUID
    platform_name: str
    analytics_period_start: datetime
    analytics_period_end: datetime
    
    # Platform-specific metrics
    platform_followers: int = Field(default=0, ge=0)
    follower_growth: int = Field(default=0, description="Net follower change")
    content_posted: int = Field(default=0, ge=0)
    total_interactions: int = Field(default=0, ge=0)
    
    # Engagement analytics
    average_engagement_rate: float = Field(default=0.0, ge=0.0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    
    # Reach and impressions
    organic_reach: int = Field(default=0, ge=0)
    paid_reach: int = Field(default=0, ge=0)
    total_impressions: int = Field(default=0, ge=0)
    impression_share: Optional[float] = None
    
    # Audience insights
    audience_demographics: Dict[str, Any] = Field(default_factory=dict)
    audience_interests: List[str] = Field(default_factory=list)
    audience_activity_patterns: Dict[str, float] = Field(default_factory=dict)
    audience_retention: Dict[str, float] = Field(default_factory=dict)
    
    # Content performance
    top_performing_content: List[Dict[str, Any]] = Field(default_factory=list)
    content_type_performance: Dict[str, float] = Field(default_factory=dict)
    optimal_posting_times: Dict[str, List[str]] = Field(default_factory=dict)
    hashtag_performance: Dict[str, int] = Field(default_factory=dict)
    
    # Monetization metrics
    revenue_generated: Decimal = Field(default=Decimal('0.00'), ge=0)
    cost_per_engagement: Optional[Decimal] = None
    return_on_ad_spend: Optional[float] = None
    conversion_tracking: Dict[str, int] = Field(default_factory=dict)
    
    # Growth and trends
    growth_rate: float = Field(default=0.0, description="Period over period growth")
    trend_analysis: Dict[str, Any] = Field(default_factory=dict)
    prediction_models: Dict[str, float] = Field(default_factory=dict)


class MultiPlatformSync(UUIDSchema, TimestampSchema):
    """Multi-platform synchronization schema."""
    
    creator_id: UUID
    sync_configuration_name: str = Field(description="Sync configuration name")
    
    # Platform selection
    source_platforms: List[str] = Field(description="Source platforms for content")
    target_platforms: List[str] = Field(description="Target platforms for distribution")
    platform_priorities: Dict[str, int] = Field(default_factory=dict)
    
    # Synchronization rules
    content_sync_rules: Dict[str, Any] = Field(default_factory=dict)
    metadata_sync_rules: Dict[str, Any] = Field(default_factory=dict)
    scheduling_rules: Dict[str, str] = Field(default_factory=dict)
    format_conversion_rules: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    
    # Automation settings
    auto_cross_posting: bool = Field(default=False)
    auto_engagement_sync: bool = Field(default=False)
    auto_analytics_aggregation: bool = Field(default=True)
    conflict_resolution_strategy: str = Field(default="manual_review")
    
    # Sync frequency and timing
    sync_frequency: str = Field(default="hourly")
    sync_time_windows: List[Dict[str, str]] = Field(default_factory=list)
    batch_processing: bool = Field(default=True)
    
    # Performance tracking
    successful_syncs: int = Field(default=0, ge=0)
    failed_syncs: int = Field(default=0, ge=0)
    last_sync_duration: Optional[float] = None
    average_sync_time: Optional[float] = None
    
    # Error handling
    error_handling_strategy: str = Field(default="retry_with_backoff")
    max_retry_attempts: int = Field(default=3, ge=1)
    error_notifications: bool = Field(default=True)
    
    # Data consistency
    consistency_checks: Dict[str, bool] = Field(default_factory=dict)
    data_validation_rules: List[str] = Field(default_factory=list)
    conflict_logs: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('sync_frequency')
    def validate_sync_frequency(cls, v) -> None:
        """Validate sync frequency."""
        allowed_frequencies = {
            "real_time", "every_15_minutes", "hourly", "daily", 
            "weekly", "manual", "event_driven"
        }
        if v not in allowed_frequencies:
            raise ValueError(f'Sync frequency must be one of: {", ".join(allowed_frequencies)}')
        return v


class DistributionCampaign(UUIDSchema, TimestampSchema, AuditSchema):
    """Distribution campaign management schema."""
    
    creator_id: UUID
    campaign_name: str = Field(description="Distribution campaign name")
    campaign_type: str = Field(description="Type of distribution campaign")
    
    # Campaign objectives
    primary_objective: str = Field(description="Primary campaign objective")
    secondary_objectives: List[str] = Field(default_factory=list)
    success_metrics: Dict[str, float] = Field(default_factory=dict)
    target_kpis: Dict[str, float] = Field(default_factory=dict)
    
    # Campaign timeline
    campaign_start_date: datetime
    campaign_end_date: datetime
    milestone_dates: List[Dict[str, datetime]] = Field(default_factory=list)
    
    # Content and assets
    campaign_content: List[UUID] = Field(description="Content included in campaign")
    promotional_assets: List[Dict[str, str]] = Field(default_factory=list)
    creative_variants: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Targeting and distribution
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    geographic_targeting: List[str] = Field(default_factory=list)
    platform_allocation: Dict[str, float] = Field(default_factory=dict)
    budget_allocation: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Performance tracking
    campaign_performance: Dict[str, float] = Field(default_factory=dict)
    roi_metrics: Dict[str, float] = Field(default_factory=dict)
    conversion_tracking: Dict[str, int] = Field(default_factory=dict)
    audience_insights: Dict[str, Any] = Field(default_factory=dict)
    
    # Optimization
    a_b_tests: List[Dict[str, Any]] = Field(default_factory=list)
    optimization_history: List[Dict[str, Any]] = Field(default_factory=list)
    performance_adjustments: List[Dict[str, str]] = Field(default_factory=list)
    
    # Campaign status
    campaign_status: str = Field(default="draft")
    approval_status: str = Field(default="pending")
    budget_status: Dict[str, Decimal] = Field(default_factory=dict)
    
    @validator('campaign_type')
    def validate_campaign_type(cls, v) -> None:
        """Validate campaign type."""
        allowed_types = {
            "album_launch", "single_release", "promotional_campaign", "brand_partnership",
            "seasonal_campaign", "cross_platform_sync", "viral_marketing", "influencer_collaboration"
        }
        if v not in allowed_types:
            raise ValueError(f'Campaign type must be one of: {", ".join(allowed_types)}')
        return v
