"""Analytics & Insights Schemas for IA Influencer Agent Platform
Comprehensive performance analytics, business intelligence, and reporting schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class AnalyticsReport(UUIDSchema, TimestampSchema, AuditSchema):
    """
Comprehensive analytics report schema."""
    
    report_name: str = Field(description="Analytics report name")
    report_type: str = Field(description="Type of analytics report")
    creator_id: Optional[UUID] = Field(None, description="Creator for scoped reports")
    
    # Report configuration
    date_range_start: datetime
    date_range_end: datetime
    granularity: str = Field(description="Data granularity level")
    metrics_included: List[str] = Field(description="Metrics included in report")
    
    # Performance overview
    total_views: int = Field(default=0, ge=0)
    total_engagements: int = Field(default=0, ge=0)
    total_conversions: int = Field(default=0, ge=0)
    total_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Content performance
    content_performance: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed content performance metrics"
    )
    top_performing_content: List[Dict[str, Any]] = Field(default_factory=list)
    content_category_performance: Dict[str, Any] = Field(default_factory=dict)
    
    # Audience analytics
    audience_demographics: Dict[str, Any] = Field(default_factory=dict)
    audience_behavior: Dict[str, Any] = Field(default_factory=dict)
    audience_growth: Dict[str, int] = Field(default_factory=dict)
    audience_retention: Dict[str, float] = Field(default_factory=dict)
    
    # Platform performance
    platform_metrics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    cross_platform_correlation: Dict[str, float] = Field(default_factory=dict)
    platform_roi: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Engagement analytics
    engagement_trends: List[Dict[str, Any]] = Field(default_factory=list)
    engagement_by_time: Dict[str, float] = Field(default_factory=dict)
    interaction_types: Dict[str, int] = Field(default_factory=dict)
    viral_content_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Revenue analytics
    revenue_streams: Dict[str, Decimal] = Field(default_factory=dict)
    monetization_efficiency: Dict[str, float] = Field(default_factory=dict)
    customer_lifetime_value: Optional[Decimal] = None
    revenue_per_follower: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Predictive insights
    growth_predictions: Dict[str, float] = Field(default_factory=dict)
    trend_analysis: List[str] = Field(default_factory=list)
    opportunity_identification: List[str] = Field(default_factory=list)
    risk_assessment: List[str] = Field(default_factory=list)
    
    # Comparative analysis
    industry_benchmarks: Dict[str, float] = Field(default_factory=dict)
    competitor_comparison: Dict[str, Any] = Field(default_factory=dict)
    performance_ranking: Optional[int] = None
    
    # Recommendations
    optimization_recommendations: List[str] = Field(default_factory=list)
    content_strategy_insights: List[str] = Field(default_factory=list)
    monetization_opportunities: List[str] = Field(default_factory=list)
    
    @validator('report_type')
    def validate_report_type(cls, v) -> None:
        """Validate report type."""
        allowed_types = {
            "performance_overview", "audience_analysis", "content_performance",
            "revenue_analysis", "engagement_report", "growth_analysis",
            "competitive_intelligence", "roi_analysis", "trend_report",
            "custom_dashboard", "executive_summary", "detailed_analytics"
        }
        if v not in allowed_types:
            raise ValueError(f'Report type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('granularity')
    def validate_granularity(cls, v) -> None:
        """Validate data granularity."""
        allowed_granularities = {
            "hourly", "daily", "weekly", "monthly", "quarterly", "yearly"
        }
        if v not in allowed_granularities:
            raise ValueError(f'Granularity must be one of: {", ".join(allowed_granularities)}')
        return v


class ContentAnalytics(UUIDSchema, TimestampSchema):
    """Detailed content performance analytics schema."""
    
    content_id: UUID
    analysis_period_start: datetime
    analysis_period_end: datetime
    
    # Basic metrics
    total_views: int = Field(default=0, ge=0)
    unique_views: int = Field(default=0, ge=0)
    total_engagements: int = Field(default=0, ge=0)
    engagement_rate: float = Field(default=0.0, ge=0.0)
    
    # Time-based performance
    hourly_performance: Dict[str, int] = Field(default_factory=dict)
    daily_performance: Dict[str, int] = Field(default_factory=dict)
    weekly_trends: List[float] = Field(default_factory=list)
    performance_lifecycle: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Platform breakdown
    platform_views: Dict[str, int] = Field(default_factory=dict)
    platform_engagement: Dict[str, float] = Field(default_factory=dict)
    cross_platform_sharing: Dict[str, int] = Field(default_factory=dict)
    
    # Audience engagement
    likes_count: int = Field(default=0, ge=0)
    comments_count: int = Field(default=0, ge=0)
    shares_count: int = Field(default=0, ge=0)
    saves_count: int = Field(default=0, ge=0)
    click_through_rate: float = Field(default=0.0, ge=0.0)
    
    # Content completion metrics
    average_watch_time: float = Field(default=0.0, ge=0.0)
    completion_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    replay_rate: float = Field(default=0.0, ge=0.0)
    drop_off_points: List[float] = Field(default_factory=list)
    
    # Audience demographics
    age_demographics: Dict[str, float] = Field(default_factory=dict)
    gender_demographics: Dict[str, float] = Field(default_factory=dict)
    geographic_distribution: Dict[str, float] = Field(default_factory=dict)
    device_usage: Dict[str, float] = Field(default_factory=dict)
    
    # Traffic sources
    organic_traffic: float = Field(default=0.0, ge=0.0)
    social_referrals: Dict[str, float] = Field(default_factory=dict)
    direct_traffic: float = Field(default=0.0, ge=0.0)
    search_traffic: float = Field(default=0.0, ge=0.0)
    
    # Conversion metrics
    conversion_events: Dict[str, int] = Field(default_factory=dict)
    conversion_rate: float = Field(default=0.0, ge=0.0)
    revenue_attribution: Decimal = Field(default=Decimal('0.00'), ge=0)
    cost_per_conversion: Optional[Decimal] = None
    
    # Content quality indicators
    authenticity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    brand_safety_score: float = Field(default=0.0, ge=0.0, le=1.0)
    sentiment_analysis: Dict[str, float] = Field(default_factory=dict)
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Comparative performance
    vs_previous_content: Dict[str, float] = Field(default_factory=dict)
    vs_category_average: Dict[str, float] = Field(default_factory=dict)
    performance_percentile: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Optimization insights
    peak_performance_factors: List[str] = Field(default_factory=list)
    improvement_opportunities: List[str] = Field(default_factory=list)
    similar_content_recommendations: List[UUID] = Field(default_factory=list)


class AudienceInsights(UUIDSchema, TimestampSchema):
    """
Comprehensive audience analytics and insights schema."""
    
    creator_id: UUID
    insight_period_start: datetime
    insight_period_end: datetime
    
    # Audience size and growth
    total_followers: Dict[str, int] = Field(default_factory=dict)
    follower_growth: Dict[str, List[int]] = Field(default_factory=dict)
    audience_reach: Dict[str, int] = Field(default_factory=dict)
    unique_audience_size: int = Field(default=0, ge=0)
    
    # Demographics
    age_distribution: Dict[str, float] = Field(default_factory=dict)
    gender_distribution: Dict[str, float] = Field(default_factory=dict)
    location_distribution: Dict[str, float] = Field(default_factory=dict)
    language_preferences: Dict[str, float] = Field(default_factory=dict)
    
    # Behavioral insights
    engagement_patterns: Dict[str, Any] = Field(default_factory=dict)
    content_preferences: Dict[str, float] = Field(default_factory=dict)
    platform_usage: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    activity_timing: Dict[str, List[float]] = Field(default_factory=dict)
    
    # Interest analysis
    primary_interests: List[str] = Field(default_factory=list)
    secondary_interests: List[str] = Field(default_factory=list)
    emerging_interests: List[str] = Field(default_factory=list)
    interest_overlap: Dict[str, float] = Field(default_factory=dict)
    
    # Psychographic profiling
    personality_traits: Dict[str, float] = Field(default_factory=dict)
    values_alignment: Dict[str, float] = Field(default_factory=dict)
    lifestyle_indicators: List[str] = Field(default_factory=list)
    purchase_behavior: Dict[str, Any] = Field(default_factory=dict)
    
    # Audience quality metrics
    engagement_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    authenticity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    loyalty_index: float = Field(default=0.0, ge=0.0, le=1.0)
    influence_receptivity: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Segmentation analysis
    audience_segments: List[Dict[str, Any]] = Field(default_factory=list)
    high_value_segments: List[Dict[str, Any]] = Field(default_factory=list)
    growth_segments: List[Dict[str, Any]] = Field(default_factory=list)
    at_risk_segments: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Cross-platform analysis
    platform_overlap: Dict[str, float] = Field(default_factory=dict)
    platform_specific_behavior: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    migration_patterns: Dict[str, List[float]] = Field(default_factory=dict)
    
    # Competitive audience analysis
    shared_audience_competitors: List[Dict[str, Any]] = Field(default_factory=list)
    audience_uniqueness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    competitive_positioning: Dict[str, Any] = Field(default_factory=dict)
    
    # Predictive insights
    growth_trajectory: Dict[str, List[float]] = Field(default_factory=dict)
    churn_risk_analysis: Dict[str, float] = Field(default_factory=dict)
    lifetime_value_prediction: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Actionable recommendations
    content_recommendations: List[str] = Field(default_factory=list)
    posting_optimization: Dict[str, str] = Field(default_factory=list)
    engagement_strategies: List[str] = Field(default_factory=list)
    monetization_opportunities: List[str] = Field(default_factory=list)


class RevenueAnalytics(UUIDSchema, TimestampSchema):
    """
Comprehensive revenue and monetization analytics schema."""
    
    creator_id: UUID
    analysis_period_start: datetime
    analysis_period_end: datetime
    
    # Revenue overview
    total_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    revenue_growth: float = Field(default=0.0)
    revenue_by_period: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Revenue streams
    sponsored_content_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    affiliate_marketing_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    product_sales_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    subscription_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    licensing_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    collaboration_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    other_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Revenue stream analysis
    revenue_stream_performance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    revenue_diversification_index: float = Field(default=0.0, ge=0.0, le=1.0)
    most_profitable_streams: List[str] = Field(default_factory=list)
    growing_revenue_streams: List[str] = Field(default_factory=list)
    
    # Platform monetization
    platform_revenue: Dict[str, Decimal] = Field(default_factory=dict)
    platform_monetization_rate: Dict[str, float] = Field(default_factory=dict)
    cross_platform_revenue_correlation: Dict[str, float] = Field(default_factory=dict)
    
    # Customer economics
    average_order_value: Decimal = Field(default=Decimal('0.00'), ge=0)
    customer_acquisition_cost: Decimal = Field(default=Decimal('0.00'), ge=0)
    customer_lifetime_value: Decimal = Field(default=Decimal('0.00'), ge=0)
    return_customer_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Performance metrics
    revenue_per_follower: Dict[str, Decimal] = Field(default_factory=dict)
    revenue_per_engagement: Decimal = Field(default=Decimal('0.00'), ge=0)
    conversion_rate_by_funnel: Dict[str, float] = Field(default_factory=dict)
    
    # Cost analysis
    content_production_costs: Decimal = Field(default=Decimal('0.00'), ge=0)
    marketing_costs: Decimal = Field(default=Decimal('0.00'), ge=0)
    platform_fees: Decimal = Field(default=Decimal('0.00'), ge=0)
    operational_costs: Decimal = Field(default=Decimal('0.00'), ge=0)
    total_costs: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Profitability analysis
    gross_profit: Decimal = Field(default=Decimal('0.00'))
    net_profit: Decimal = Field(default=Decimal('0.00'))
    profit_margin: float = Field(default=0.0)
    roi_by_activity: Dict[str, float] = Field(default_factory=dict)
    
    # Pricing analysis
    optimal_pricing_insights: Dict[str, Decimal] = Field(default_factory=dict)
    price_elasticity_analysis: Dict[str, float] = Field(default_factory=dict)
    competitive_pricing_position: Dict[str, Any] = Field(default_factory=dict)
    
    # Seasonal and trend analysis
    seasonal_revenue_patterns: Dict[str, List[Decimal]] = Field(default_factory=dict)
    revenue_trends: List[Dict[str, Any]] = Field(default_factory=list)
    market_opportunity_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Forecast and projections
    revenue_forecast: Dict[str, Decimal] = Field(default_factory=dict)
    growth_projections: Dict[str, float] = Field(default_factory=dict)
    scenario_analysis: Dict[str, Dict[str, Decimal]] = Field(default_factory=dict)
    
    # Optimization recommendations
    monetization_opportunities: List[str] = Field(default_factory=list)
    cost_reduction_recommendations: List[str] = Field(default_factory=list)
    pricing_optimization_suggestions: List[str] = Field(default_factory=list)
    revenue_diversification_strategies: List[str] = Field(default_factory=list)


class CompetitiveIntelligence(UUIDSchema, TimestampSchema):
    """
Competitive analysis and market intelligence schema."""
    
    creator_id: UUID
    analysis_date: datetime
    market_segment: str = Field(description="Market segment for analysis")
    
    # Competitor identification
    direct_competitors: List[Dict[str, Any]] = Field(default_factory=list)
    indirect_competitors: List[Dict[str, Any]] = Field(default_factory=list)
    emerging_competitors: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Market positioning
    market_position: str = Field(description="Current market position")
    competitive_advantages: List[str] = Field(default_factory=list)
    competitive_disadvantages: List[str] = Field(default_factory=list)
    differentiation_factors: List[str] = Field(default_factory=list)
    
    # Performance comparison
    follower_count_comparison: Dict[str, int] = Field(default_factory=dict)
    engagement_rate_comparison: Dict[str, float] = Field(default_factory=dict)
    content_volume_comparison: Dict[str, int] = Field(default_factory=dict)
    growth_rate_comparison: Dict[str, float] = Field(default_factory=dict)
    
    # Content analysis
    competitor_content_strategies: Dict[str, List[str]] = Field(default_factory=dict)
    content_gap_opportunities: List[str] = Field(default_factory=list)
    trending_competitor_content: List[Dict[str, Any]] = Field(default_factory=list)
    content_innovation_tracking: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Audience overlap analysis
    audience_overlap_percentages: Dict[str, float] = Field(default_factory=dict)
    unique_audience_segments: List[str] = Field(default_factory=list)
    shared_audience_characteristics: Dict[str, Any] = Field(default_factory=dict)
    
    # Brand partnership analysis
    competitor_brand_partnerships: Dict[str, List[str]] = Field(default_factory=dict)
    partnership_opportunity_gaps: List[str] = Field(default_factory=list)
    brand_exclusivity_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Pricing and monetization
    competitor_pricing_strategies: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    monetization_method_comparison: Dict[str, List[str]] = Field(default_factory=dict)
    revenue_stream_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Platform strategy comparison
    platform_presence_comparison: Dict[str, Dict[str, bool]] = Field(default_factory=dict)
    cross_platform_strategy_analysis: Dict[str, str] = Field(default_factory=dict)
    platform_performance_comparison: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Innovation tracking
    competitor_feature_adoption: Dict[str, List[str]] = Field(default_factory=dict)
    technology_usage_comparison: Dict[str, List[str]] = Field(default_factory=dict)
    innovation_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Market trends
    industry_trend_adoption: Dict[str, float] = Field(default_factory=dict)
    emerging_market_opportunities: List[str] = Field(default_factory=list)
    market_saturation_analysis: Dict[str, float] = Field(default_factory=dict)
    
    # Strategic recommendations
    competitive_response_strategies: List[str] = Field(default_factory=list)
    market_opportunity_prioritization: List[Dict[str, Any]] = Field(default_factory=list)
    defensive_strategies: List[str] = Field(default_factory=list)
    growth_opportunities: List[str] = Field(default_factory=list)


class PlatformPerformance(UUIDSchema, TimestampSchema):
    """Multi-platform performance analytics schema."""
    
    creator_id: UUID
    analysis_period_start: datetime
    analysis_period_end: datetime
    
    # Platform overview
    active_platforms: List[str] = Field(description="Active social media platforms")
    platform_performance_summary: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Platform-specific metrics
    instagram_metrics: Optional[Dict[str, Any]] = None
    youtube_metrics: Optional[Dict[str, Any]] = None
    tiktok_metrics: Optional[Dict[str, Any]] = None
    twitter_metrics: Optional[Dict[str, Any]] = None
    facebook_metrics: Optional[Dict[str, Any]] = None
    linkedin_metrics: Optional[Dict[str, Any]] = None
    snapchat_metrics: Optional[Dict[str, Any]] = None
    pinterest_metrics: Optional[Dict[str, Any]] = None
    twitch_metrics: Optional[Dict[str, Any]] = None
    
    # Cross-platform analysis
    audience_overlap: Dict[str, float] = Field(default_factory=dict)
    content_performance_correlation: Dict[str, float] = Field(default_factory=dict)
    cross_promotion_effectiveness: Dict[str, float] = Field(default_factory=dict)
    platform_synergy_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Platform efficiency metrics
    time_investment_per_platform: Dict[str, float] = Field(default_factory=dict)
    roi_per_platform: Dict[str, Decimal] = Field(default_factory=dict)
    engagement_efficiency: Dict[str, float] = Field(default_factory=dict)
    growth_efficiency: Dict[str, float] = Field(default_factory=dict)
    
    # Content adaptation analysis
    platform_specific_content_performance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    content_format_preferences: Dict[str, List[str]] = Field(default_factory=dict)
    optimal_posting_frequency: Dict[str, str] = Field(default_factory=dict)
    
    # Algorithm performance
    algorithm_favorability: Dict[str, float] = Field(default_factory=dict)
    organic_reach_trends: Dict[str, List[float]] = Field(default_factory=dict)
    algorithmic_changes_impact: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    
    # Monetization by platform
    platform_revenue: Dict[str, Decimal] = Field(default_factory=dict)
    monetization_features_usage: Dict[str, List[str]] = Field(default_factory=dict)
    conversion_rates_by_platform: Dict[str, float] = Field(default_factory=dict)
    
    # Platform strategy recommendations
    platform_prioritization: List[str] = Field(default_factory=list)
    underperforming_platforms: List[str] = Field(default_factory=list)
    expansion_opportunities: List[str] = Field(default_factory=list)
    optimization_recommendations: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Future platform trends
    emerging_platform_analysis: List[Dict[str, Any]] = Field(default_factory=list)
    platform_lifecycle_assessment: Dict[str, str] = Field(default_factory=dict)
    strategic_platform_roadmap: List[Dict[str, str]] = Field(default_factory=list)


class BusinessIntelligenceDashboard(UUIDSchema, TimestampSchema):
    """Executive business intelligence dashboard schema."""
    
    creator_id: UUID
    dashboard_name: str = Field(description="Dashboard name")
    dashboard_type: str = Field(description="Type of BI dashboard")
    refresh_frequency: str = Field(description="Data refresh frequency")
    
    # Key Performance Indicators
    primary_kpis: Dict[str, Any] = Field(default_factory=dict)
    secondary_kpis: Dict[str, Any] = Field(default_factory=dict)
    kpi_targets: Dict[str, float] = Field(default_factory=dict)
    kpi_achievements: Dict[str, float] = Field(default_factory=dict)
    
    # Executive summary metrics
    revenue_summary: Dict[str, Decimal] = Field(default_factory=dict)
    growth_summary: Dict[str, float] = Field(default_factory=dict)
    audience_summary: Dict[str, int] = Field(default_factory=dict)
    performance_summary: Dict[str, float] = Field(default_factory=dict)
    
    # Trend analysis
    performance_trends: List[Dict[str, Any]] = Field(default_factory=list)
    market_trends: List[str] = Field(default_factory=list)
    competitive_trends: List[str] = Field(default_factory=list)
    
    # Risk and opportunity assessment
    current_risks: List[Dict[str, str]] = Field(default_factory=list)
    growth_opportunities: List[Dict[str, str]] = Field(default_factory=list)
    strategic_initiatives: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Financial health indicators
    profitability_metrics: Dict[str, Decimal] = Field(default_factory=dict)
    cash_flow_indicators: Dict[str, Decimal] = Field(default_factory=dict)
    investment_returns: Dict[str, float] = Field(default_factory=dict)
    
    # Operational efficiency
    productivity_metrics: Dict[str, float] = Field(default_factory=dict)
    resource_utilization: Dict[str, float] = Field(default_factory=dict)
    process_efficiency: Dict[str, float] = Field(default_factory=dict)
    
    # Strategic insights
    market_position_analysis: Dict[str, Any] = Field(default_factory=dict)
    competitive_advantage_assessment: List[str] = Field(default_factory=list)
    strategic_recommendations: List[str] = Field(default_factory=list)
    
    # Forecast and projections
    short_term_forecasts: Dict[str, Any] = Field(default_factory=dict)
    long_term_projections: Dict[str, Any] = Field(default_factory=dict)
    scenario_planning: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Alert and notifications
    critical_alerts: List[str] = Field(default_factory=list)
    performance_warnings: List[str] = Field(default_factory=list)
    opportunity_notifications: List[str] = Field(default_factory=list)
    
    @validator('dashboard_type')
    def validate_dashboard_type(cls, v) -> None:
        """Validate dashboard type."""
        allowed_types = {
            "executive_summary", "performance_overview", "financial_dashboard",
            "operational_metrics", "strategic_planning", "risk_management",
            "competitive_intelligence", "growth_tracking", "roi_analysis"
        }
        if v not in allowed_types:
            raise ValueError(f'Dashboard type must be one of: {", ".join(allowed_types)}')
        return v
