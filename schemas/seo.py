"""SEO & Marketing Optimization Schemas for IA Influencer Agent Platform
Professional SEO analysis, content optimization, and marketing strategy schemas

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


class SEOAnalysis(UUIDSchema, TimestampSchema):
    """
SEO analysis results schema."""
    
    content_id: UUID = Field(description="Analyzed content")
    analysis_type: str = Field(description="Type of SEO analysis")
    analysis_version: str = Field(description="Analysis algorithm version")
    
    # Content analysis
    content_quality_score: float = Field(ge=0.0, le=1.0, description="Content quality score")
    readability_score: float = Field(ge=0.0, le=1.0, description="Content readability")
    uniqueness_score: float = Field(ge=0.0, le=1.0, description="Content uniqueness")
    relevance_score: float = Field(ge=0.0, le=1.0, description="Topic relevance")
    
    # Keyword analysis
    primary_keywords: List[str] = Field(default_factory=list)
    secondary_keywords: List[str] = Field(default_factory=list)
    long_tail_keywords: List[str] = Field(default_factory=list)
    keyword_density: Dict[str, float] = Field(default_factory=dict)
    keyword_difficulty: Dict[str, float] = Field(default_factory=dict)
    search_volume: Dict[str, int] = Field(default_factory=dict)
    
    # Technical SEO
    title_optimization: Dict[str, Any] = Field(default_factory=dict)
    meta_description_optimization: Dict[str, Any] = Field(default_factory=dict)
    header_structure: Dict[str, List[str]] = Field(default_factory=dict)
    internal_linking_opportunities: List[str] = Field(default_factory=list)
    
    # Content structure
    content_length: int = Field(ge=0, description="Content length in words")
    paragraph_structure: Dict[str, int] = Field(default_factory=dict)
    list_usage: int = Field(ge=0, description="Number of lists")
    media_integration: Dict[str, int] = Field(default_factory=dict)
    
    # Semantic analysis
    topic_clusters: List[str] = Field(default_factory=list)
    semantic_keywords: List[str] = Field(default_factory=list)
    content_gaps: List[str] = Field(default_factory=list)
    related_topics: List[str] = Field(default_factory=list)
    
    # Competitive analysis
    competitor_comparison: Dict[str, Any] = Field(default_factory=dict)
    content_gaps_vs_competitors: List[str] = Field(default_factory=list)
    competitive_keywords: List[str] = Field(default_factory=list)
    
    # Optimization recommendations
    immediate_improvements: List[str] = Field(default_factory=list)
    long_term_strategies: List[str] = Field(default_factory=list)
    content_enhancement_suggestions: List[str] = Field(default_factory=list)
    technical_improvements: List[str] = Field(default_factory=list)
    
    # Performance predictions
    ranking_potential: Dict[str, float] = Field(default_factory=dict)
    traffic_estimate: Dict[str, int] = Field(default_factory=dict)
    conversion_probability: Optional[float] = None
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        """Validate analysis type."""
        allowed_types = {
            "content_analysis", "keyword_research", "competitive_analysis",
            "technical_seo", "semantic_analysis", "performance_audit"
        }
        if v not in allowed_types:
            raise ValueError(f'Analysis type must be one of: {", ".join(allowed_types)}')
        return v


class SEOOptimization(BaseSchema):
    """SEO optimization request schema."""
    
    content_id: UUID = Field(description="Content to optimize")
    optimization_level: str = Field(description="Level of optimization")
    target_keywords: List[str] = Field(description="Primary keywords to target")
    secondary_keywords: List[str] = Field(default_factory=list)
    
    # Optimization scope
    optimize_title: bool = Field(default=True)
    optimize_description: bool = Field(default=True)
    optimize_content: bool = Field(default=True)
    optimize_tags: bool = Field(default=True)
    
    # Target audience
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    geographic_targeting: List[str] = Field(default_factory=list)
    language_targeting: List[str] = Field(default_factory=list)
    demographic_targeting: Dict[str, Any] = Field(default_factory=dict)
    
    # Content preferences
    tone_of_voice: str = Field(default="professional")
    content_style: str = Field(default="informative")
    brand_guidelines: Dict[str, str] = Field(default_factory=dict)
    compliance_requirements: List[str] = Field(default_factory=list)
    
    # Technical requirements
    character_limits: Dict[str, int] = Field(default_factory=dict)
    format_requirements: List[str] = Field(default_factory=list)
    platform_specifications: Dict[str, Any] = Field(default_factory=dict)
    
    # Advanced options
    semantic_optimization: bool = Field(default=True)
    entity_recognition: bool = Field(default=True)
    sentiment_optimization: bool = Field(default=False)
    multilingual_optimization: bool = Field(default=False)
    
    @validator('optimization_level')
    def validate_optimization_level(cls, v):
        """Validate optimization level."""
        allowed_levels = {"basic", "standard", "advanced", "comprehensive", "custom"}
        if v not in allowed_levels:
            raise ValueError(f'Optimization level must be one of: {", ".join(allowed_levels)}')
        return v


class KeywordResearch(UUIDSchema, TimestampSchema):
    """Keyword research results schema."""
    
    research_query: str = Field(description="Initial research query")
    research_scope: str = Field(description="Scope of keyword research")
    target_market: str = Field(description="Target market/region")
    
    # Primary keyword data
    primary_keywords: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Primary keyword opportunities"
    )
    
    # Keyword categories
    short_tail_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    long_tail_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    question_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    commercial_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Competitive analysis
    competitor_keywords: Dict[str, List[str]] = Field(default_factory=dict)
    keyword_gaps: List[str] = Field(default_factory=list)
    opportunity_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Search intent analysis
    informational_keywords: List[str] = Field(default_factory=list)
    navigational_keywords: List[str] = Field(default_factory=list)
    transactional_keywords: List[str] = Field(default_factory=list)
    commercial_investigation_keywords: List[str] = Field(default_factory=list)
    
    # Seasonal and trend data
    seasonal_trends: Dict[str, List[float]] = Field(default_factory=dict)
    trending_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    emerging_topics: List[str] = Field(default_factory=list)
    
    # Difficulty and opportunity metrics
    keyword_difficulty_distribution: Dict[str, int] = Field(default_factory=dict)
    search_volume_distribution: Dict[str, int] = Field(default_factory=dict)
    competition_level: Dict[str, int] = Field(default_factory=dict)
    
    # Related topics and entities
    related_topics: List[str] = Field(default_factory=list)
    semantic_entities: List[str] = Field(default_factory=list)
    topic_clusters: List[Dict[str, List[str]]] = Field(default_factory=list)
    
    # Recommendations
    prioritized_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    content_strategy_recommendations: List[str] = Field(default_factory=list)
    quick_win_opportunities: List[str] = Field(default_factory=list)
    
    @validator('research_scope')
    def validate_research_scope(cls, v):
        """Validate research scope."""
        allowed_scopes = {
            "comprehensive", "competitive", "niche_specific", "trend_analysis",
            "seasonal_analysis", "local_seo", "voice_search", "mobile_optimization"
        }
        if v not in allowed_scopes:
            raise ValueError(f'Research scope must be one of: {", ".join(allowed_scopes)}')
        return v


class ContentOptimization(UUIDSchema, TimestampSchema):
    """Content optimization results schema."""
    
    content_id: UUID
    optimization_request_id: UUID = Field(description="Associated optimization request")
    optimization_type: str = Field(description="Type of optimization performed")
    
    # Original vs optimized content
    original_content_metrics: Dict[str, Any] = Field(default_factory=dict)
    optimized_content_preview: str = Field(description="Preview of optimized content")
    optimization_changes: List[Dict[str, str]] = Field(default_factory=list)
    
    # SEO improvements
    title_optimizations: List[str] = Field(default_factory=list)
    description_optimizations: List[str] = Field(default_factory=list)
    content_structure_improvements: List[str] = Field(default_factory=list)
    keyword_integration: Dict[str, int] = Field(default_factory=dict)
    
    # Readability improvements
    readability_score_improvement: float = Field(default=0.0)
    sentence_structure_improvements: int = Field(default=0, ge=0)
    vocabulary_enhancements: int = Field(default=0, ge=0)
    
    # Performance predictions
    expected_ranking_improvement: Dict[str, float] = Field(default_factory=dict)
    estimated_traffic_increase: Optional[float] = None
    conversion_rate_impact: Optional[float] = None
    
    # Quality metrics
    content_quality_score: float = Field(ge=0.0, le=1.0)
    uniqueness_verification: bool = Field(default=True)
    plagiarism_check_passed: bool = Field(default=True)
    brand_consistency_score: float = Field(ge=0.0, le=1.0)
    
    # Implementation status
    optimization_status: str = Field(default="pending")
    applied_optimizations: List[str] = Field(default_factory=list)
    pending_optimizations: List[str] = Field(default_factory=list)
    
    # A/B testing setup
    ab_test_variants: List[Dict[str, str]] = Field(default_factory=list)
    test_metrics: List[str] = Field(default_factory=list)
    test_duration: Optional[int] = Field(None, description="Test duration in days")


class SocialMediaStrategy(UUIDSchema, TimestampSchema):
    """Social media marketing strategy schema."""
    
    creator_id: UUID
    strategy_name: str = Field(description="Social media strategy name")
    target_platforms: List[str] = Field(description="Target social media platforms")
    
    # Strategy objectives
    primary_goals: List[str] = Field(description="Primary marketing goals")
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    brand_positioning: str = Field(description="Brand positioning statement")
    unique_value_proposition: str = Field(description="Unique value proposition")
    
    # Content strategy
    content_pillars: List[str] = Field(default_factory=list, description="Content pillars/themes")
    content_mix: Dict[str, float] = Field(default_factory=dict, description="Content type distribution")
    posting_frequency: Dict[str, str] = Field(default_factory=dict, description="Posting frequency per platform")
    optimal_posting_times: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Engagement strategy
    hashtag_strategy: Dict[str, List[str]] = Field(default_factory=dict)
    influencer_collaboration_plan: List[Dict[str, Any]] = Field(default_factory=list)
    community_building_tactics: List[str] = Field(default_factory=list)
    user_generated_content_strategy: Dict[str, Any] = Field(default_factory=dict)
    
    # Campaign planning
    promotional_campaigns: List[Dict[str, Any]] = Field(default_factory=list)
    seasonal_content_calendar: Dict[str, List[str]] = Field(default_factory=dict)
    product_launch_strategies: List[str] = Field(default_factory=list)
    
    # Performance tracking
    kpi_targets: Dict[str, float] = Field(default_factory=dict)
    conversion_goals: Dict[str, int] = Field(default_factory=dict)
    roi_targets: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Budget allocation
    platform_budget_allocation: Dict[str, Decimal] = Field(default_factory=dict)
    campaign_budgets: Dict[str, Decimal] = Field(default_factory=dict)
    paid_promotion_strategy: Dict[str, Any] = Field(default_factory=dict)
    
    # Risk management
    crisis_management_plan: List[str] = Field(default_factory=list)
    brand_safety_guidelines: List[str] = Field(default_factory=list)
    reputation_monitoring_strategy: Dict[str, Any] = Field(default_factory=dict)


class MarketingCampaign(UUIDSchema, TimestampSchema, AuditSchema):
    """Marketing campaign management schema."""
    
    creator_id: UUID
    campaign_name: str = Field(description="Marketing campaign name")
    campaign_type: str = Field(description="Type of marketing campaign")
    campaign_objective: str = Field(description="Primary campaign objective")
    
    # Campaign timeline
    campaign_start_date: datetime
    campaign_end_date: datetime
    preparation_timeline: List[Dict[str, datetime]] = Field(default_factory=list)
    execution_milestones: List[Dict[str, datetime]] = Field(default_factory=list)
    
    # Target audience
    target_demographics: Dict[str, Any] = Field(default_factory=dict)
    audience_segments: List[Dict[str, Any]] = Field(default_factory=list)
    persona_targeting: List[Dict[str, str]] = Field(default_factory=list)
    
    # Campaign assets
    creative_assets: List[Dict[str, str]] = Field(default_factory=list)
    content_calendar: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    promotional_materials: List[HttpUrl] = Field(default_factory=list)
    
    # Channel strategy
    marketing_channels: List[str] = Field(description="Marketing channels to use")
    channel_allocation: Dict[str, float] = Field(default_factory=dict, description="Budget allocation per channel")
    cross_channel_integration: Dict[str, Any] = Field(default_factory=dict)
    
    # Budget and resources
    total_budget: Decimal = Field(ge=0, description="Total campaign budget")
    budget_breakdown: Dict[str, Decimal] = Field(default_factory=dict)
    resource_requirements: List[str] = Field(default_factory=list)
    
    # Performance targets
    reach_targets: Dict[str, int] = Field(default_factory=dict)
    engagement_targets: Dict[str, float] = Field(default_factory=dict)
    conversion_targets: Dict[str, int] = Field(default_factory=dict)
    roi_targets: Decimal = Field(default=Decimal('0.00'))
    
    # Tracking and measurement
    tracking_parameters: Dict[str, str] = Field(default_factory=dict)
    attribution_model: str = Field(default="last_click")
    measurement_methodology: List[str] = Field(default_factory=list)
    
    # Campaign performance
    actual_performance: Dict[str, float] = Field(default_factory=dict)
    performance_vs_targets: Dict[str, float] = Field(default_factory=dict)
    optimization_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # A/B testing
    test_variations: List[Dict[str, Any]] = Field(default_factory=list)
    test_results: Dict[str, float] = Field(default_factory=dict)
    winning_variations: List[str] = Field(default_factory=list)
    
    @validator('campaign_type')
    def validate_campaign_type(cls, v):
        """Validate campaign type."""
        allowed_types = {
            "brand_awareness", "lead_generation", "product_launch", "engagement",
            "conversion", "retention", "viral_marketing", "influencer_collaboration",
            "content_marketing", "paid_advertising", "email_marketing", "seo_campaign"
        }
        if v not in allowed_types:
            raise ValueError(f'Campaign type must be one of: {", ".join(allowed_types)}')
        return v


class InfluencerMetrics(UUIDSchema, TimestampSchema):
    """Influencer performance metrics schema."""
    
    creator_id: UUID
    metrics_period_start: datetime
    metrics_period_end: datetime
    
    # Audience metrics
    total_followers: Dict[str, int] = Field(default_factory=dict, description="Followers per platform")
    follower_growth: Dict[str, int] = Field(default_factory=dict)
    audience_demographics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    audience_quality_score: float = Field(ge=0.0, le=1.0)
    
    # Engagement metrics
    average_engagement_rate: float = Field(ge=0.0)
    engagement_by_platform: Dict[str, float] = Field(default_factory=dict)
    engagement_by_content_type: Dict[str, float] = Field(default_factory=dict)
    viral_content_count: int = Field(default=0, ge=0)
    
    # Content performance
    total_content_published: int = Field(default=0, ge=0)
    top_performing_content: List[Dict[str, Any]] = Field(default_factory=list)
    content_completion_rates: Dict[str, float] = Field(default_factory=dict)
    content_sharing_rates: Dict[str, float] = Field(default_factory=dict)
    
    # Influence metrics
    influence_score: float = Field(ge=0.0, le=1.0, description="Overall influence score")
    topic_authority: Dict[str, float] = Field(default_factory=dict)
    brand_affinity: Dict[str, float] = Field(default_factory=dict)
    recommendation_impact: float = Field(ge=0.0, description="Recommendation effectiveness")
    
    # Commercial metrics
    brand_collaboration_count: int = Field(default=0, ge=0)
    sponsored_content_performance: Dict[str, float] = Field(default_factory=dict)
    conversion_rates: Dict[str, float] = Field(default_factory=dict)
    estimated_media_value: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Growth and trend analysis
    growth_trajectory: Dict[str, List[float]] = Field(default_factory=dict)
    trending_topics: List[str] = Field(default_factory=list)
    content_innovation_score: float = Field(ge=0.0, le=1.0)
    market_positioning: Dict[str, Any] = Field(default_factory=dict)
    
    # Authenticity and trust metrics
    authenticity_score: float = Field(ge=0.0, le=1.0)
    fake_follower_percentage: float = Field(ge=0.0, le=100.0)
    engagement_authenticity: float = Field(ge=0.0, le=1.0)
    brand_safety_score: float = Field(ge=0.0, le=1.0)
    
    # Competitive analysis
    competitor_comparison: Dict[str, float] = Field(default_factory=dict)
    market_share: Optional[float] = Field(None, ge=0.0, le=100.0)
    unique_positioning_factors: List[str] = Field(default_factory=list)


class ContentPerformancePrediction(UUIDSchema, TimestampSchema):
    """AI-powered content performance prediction schema."""
    
    content_id: UUID
    prediction_model_version: str = Field(description="Prediction model version")
    confidence_level: float = Field(ge=0.0, le=1.0, description="Prediction confidence")
    
    # Performance predictions
    predicted_reach: Dict[str, int] = Field(default_factory=dict)
    predicted_engagement: Dict[str, float] = Field(default_factory=dict)
    predicted_conversions: Dict[str, int] = Field(default_factory=dict)
    virality_probability: float = Field(ge=0.0, le=1.0)
    
    # Temporal predictions
    peak_performance_timing: Dict[str, datetime] = Field(default_factory=dict)
    performance_lifecycle: Dict[str, List[float]] = Field(default_factory=dict)
    optimal_posting_windows: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Audience response predictions
    demographic_response: Dict[str, float] = Field(default_factory=dict)
    geographic_performance: Dict[str, float] = Field(default_factory=dict)
    device_performance: Dict[str, float] = Field(default_factory=dict)
    
    # Content optimization suggestions
    title_alternatives: List[Dict[str, float]] = Field(default_factory=list)
    thumbnail_recommendations: List[str] = Field(default_factory=list)
    hashtag_recommendations: List[str] = Field(default_factory=list)
    posting_time_recommendations: List[datetime] = Field(default_factory=list)
    
    # Risk assessment
    performance_risks: List[str] = Field(default_factory=list)
    controversy_risk_score: float = Field(ge=0.0, le=1.0)
    brand_safety_score: float = Field(ge=0.0, le=1.0)
    
    # Success factors
    success_probability_factors: Dict[str, float] = Field(default_factory=dict)
    optimization_opportunities: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    
    # Model performance
    historical_accuracy: float = Field(ge=0.0, le=1.0, description="Historical prediction accuracy")
    similar_content_benchmarks: List[Dict[str, Any]] = Field(default_factory=list)
    prediction_uncertainty: Dict[str, float] = Field(default_factory=dict)
