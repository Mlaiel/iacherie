"""Content Models - Pydantic data models for content generation

Professional data models that define the structure and validation
for all content generation operations and API responses.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""
from typing import Dict, Any, List, Optional, Union, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum


# Enums for type safety
class ContentType(str, Enum):
    """Content type enumeration"""    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    INSTAGRAM_POST = "instagram_post"
    TWITTER_POST = "twitter_post"
    LINKEDIN_POST = "linkedin_post"
    TIKTOK_CAPTION = "tiktok_caption"
    YOUTUBE_DESCRIPTION = "youtube_description"
    EMAIL_MARKETING = "email_marketing"
    NEWSLETTER = "newsletter"
    PRODUCT_DESCRIPTION = "product_description"
    SALES_PAGE = "sales_page"
    LANDING_PAGE = "landing_page"
    AD_COPY = "ad_copy"
    PRESS_RELEASE = "press_release"
    ARTICLE = "article"
    POST = "post"  # Social media post


class Platform(str, Enum):
    """Social media platform enumeration"""    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    THREADS = "threads"


class ContentFormat(str, Enum):
    """Content format enumeration"""    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"


class QualityLevel(str, Enum):
    """Quality level enumeration"""    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class BrandVoice(str, Enum):
    """Brand voice enumeration"""    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    PLAYFUL = "playful"
    INSPIRATIONAL = "inspirational"


# Base Models
class BaseContentModel(BaseModel):
    """Base model for all content-related models"""    
    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        validate_assignment = True


# Request Models
class ContentGenerationRequest(BaseContentModel):
    """Request model for content generation"""    
    content_type: ContentType = Field(..., description="Type of content to generate")
    topic: str = Field(..., min_length=3, max_length=200, description="Content topic or theme")
    target_audience: Optional[str] = Field(None, description="Target audience description")
    platform: Optional[Platform] = Field(None, description="Target platform")
    
    # Content specifications
    tone: Optional[BrandVoice] = Field(BrandVoice.PROFESSIONAL, description="Content tone/voice")
    word_count: Optional[int] = Field(None, ge=10, le=10000, description="Target word count")
    quality_level: QualityLevel = Field(QualityLevel.STANDARD, description="Quality level")
    
    # SEO and optimization
    keywords: Optional[List[str]] = Field(None, description="Target keywords for SEO")
    hashtags: Optional[List[str]] = Field(None, description="Hashtags to include")
    
    # Template and style
    template_type: Optional[str] = Field(None, description="Template type to use")
    style_preferences: Optional[Dict[str, Any]] = Field(None, description="Style preferences")
    
    # Business context
    brand_name: Optional[str] = Field(None, description="Brand name")
    product_name: Optional[str] = Field(None, description="Product name")
    call_to_action: Optional[str] = Field(None, description="Desired call to action")
    
    # Technical requirements
    format: ContentFormat = Field(ContentFormat.TEXT, description="Output format")
    language: str = Field("en", description="Content language")
    
    # Additional context
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    references: Optional[List[str]] = Field(None, description="Reference materials")
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if v and len(v) > 10:
            raise ValueError("Maximum 10 keywords allowed")
        return v
    
    @validator('hashtags')
    def validate_hashtags(cls, v):
        if v and len(v) > 30:
            raise ValueError("Maximum 30 hashtags allowed")
        return v


class ContentOptimizationRequest(BaseContentModel):
    """Request model for content optimization"""    
    content: str = Field(..., min_length=10, description="Content to optimize")
    optimization_type: Literal["quality", "seo", "format", "engagement"] = Field(
        "quality", description="Type of optimization"
    )
    target_platform: Optional[Platform] = Field(None, description="Target platform")
    
    # Optimization parameters
    keywords: Optional[List[str]] = Field(None, description="SEO keywords")
    target_audience: Optional[str] = Field(None, description="Target audience")
    brand_voice: Optional[BrandVoice] = Field(None, description="Brand voice")
    
    # Advanced settings
    preserve_tone: bool = Field(True, description="Preserve original tone")
    max_changes: Optional[int] = Field(None, description="Maximum changes to make")
    optimization_level: QualityLevel = Field(QualityLevel.STANDARD, description="Optimization level")
    
    # Additional fields for backward compatibility
    optimization_goals: Optional[List[str]] = Field(None, description="Optimization goals")
    current_performance: Optional[Dict[str, Any]] = Field(None, description="Current performance metrics")
    target_metrics: Optional[Dict[str, Any]] = Field(None, description="Target metrics")
    constraints: Optional[List[str]] = Field(None, description="Optimization constraints")


class TemplateRequest(BaseContentModel):
    """Request model for template-based content creation"""    
    template_type: Literal["social", "blog", "marketing"] = Field(..., description="Template type")
    template_category: str = Field(..., description="Specific template category")
    platform: Optional[Platform] = Field(None, description="Target platform")
    
    # Template data
    template_data: Dict[str, Any] = Field(..., description="Data to fill template")
    
    # Customization
    custom_elements: Optional[Dict[str, Any]] = Field(None, description="Custom template elements")
    auto_optimize: bool = Field(True, description="Apply automatic optimizations")


class PerformanceAnalysisRequest(BaseContentModel):
    """Request model for performance analysis"""    
    content_id: str = Field(..., description="Content identifier")
    platform: Platform = Field(..., description="Platform where content was published")
    
    # Metrics data
    views: Optional[int] = Field(None, ge=0, description="Number of views")
    likes: Optional[int] = Field(None, ge=0, description="Number of likes")
    shares: Optional[int] = Field(None, ge=0, description="Number of shares")
    comments: Optional[int] = Field(None, ge=0, description="Number of comments")
    clicks: Optional[int] = Field(None, ge=0, description="Number of clicks")
    conversions: Optional[int] = Field(None, ge=0, description="Number of conversions")
    reach: Optional[int] = Field(None, ge=0, description="Content reach")
    impressions: Optional[int] = Field(None, ge=0, description="Number of impressions")
    
    # Time-based metrics
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    # Additional data
    audience_demographics: Optional[Dict[str, Any]] = Field(None, description="Audience data")
    engagement_timeline: Optional[List[Dict[str, Any]]] = Field(None, description="Engagement over time")


# Response Models
class QualityScoreResponse(BaseContentModel):
    """Response model for quality scores"""    
    overall_score: float = Field(..., ge=0, le=1, description="Overall quality score")
    readability_score: float = Field(..., ge=0, le=1, description="Readability score")
    engagement_score: float = Field(..., ge=0, le=1, description="Engagement potential score")
    seo_score: float = Field(..., ge=0, le=1, description="SEO quality score")
    originality_score: float = Field(..., ge=0, le=1, description="Originality score")
    technical_score: float = Field(..., ge=0, le=1, description="Technical quality score")
    brand_alignment_score: float = Field(..., ge=0, le=1, description="Brand alignment score")
    
    quality_grade: str = Field(..., description="Letter grade (A+ to F)")
    dimension_scores: Dict[str, float] = Field(..., description="Individual dimension scores")
    improvement_suggestions: List[str] = Field(..., description="Improvement suggestions")


class ContentGenerationResponse(BaseContentModel):
    """Response model for content generation"""    
    content_id: str = Field(..., description="Unique content identifier")
    content_type: ContentType = Field(..., description="Type of content generated")
    status: Literal["completed", "failed", "in_progress", "needs_review"] = Field(
        ..., description="Generation status"
    )
    
    # Generated content
    final_content: Optional[str] = Field(None, description="Final generated content")
    original_content: Optional[str] = Field(None, description="Original generated content")
    
    # Process information
    workflow: Optional[str] = Field(None, description="Workflow used")
    steps_completed: List[str] = Field(default_factory=list, description="Completed workflow steps")
    
    # Quality and optimization
    quality_scores: Optional[QualityScoreResponse] = Field(None, description="Quality assessment")
    enhancements_applied: List[str] = Field(default_factory=list, description="Applied enhancements")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    word_count: Optional[int] = Field(None, description="Final word count")
    character_count: Optional[int] = Field(None, description="Final character count")
    
    # Validation and compliance
    validation: Optional[Dict[str, Any]] = Field(None, description="Business rule validation")
    compliance_score: Optional[float] = Field(None, description="Compliance score")
    
    # Error handling
    error: Optional[str] = Field(None, description="Error message if generation failed")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")


class ContentOptimizationResponse(BaseContentModel):
    """Response model for content optimization"""    
    content_id: str = Field(..., description="Content identifier")
    optimization_type: str = Field(..., description="Type of optimization applied")
    status: Literal["completed", "failed", "partial"] = Field(..., description="Optimization status")
    
    # Content
    original_content: str = Field(..., description="Original content")
    optimized_content: str = Field(..., description="Optimized content")
    
    # Optimization results
    optimizations_applied: List[str] = Field(..., description="Applied optimizations")
    performance_improvement: Dict[str, Any] = Field(..., description="Performance improvement metrics")
    
    # Scores and metrics
    optimization_score: Optional[float] = Field(None, description="Optimization effectiveness score")
    before_metrics: Optional[Dict[str, float]] = Field(None, description="Metrics before optimization")
    after_metrics: Optional[Dict[str, float]] = Field(None, description="Metrics after optimization")
    
    # Processing info
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    optimized_at: datetime = Field(default_factory=datetime.now, description="Optimization timestamp")
    
    # Error handling
    error: Optional[str] = Field(None, description="Error message if optimization failed")


class PerformanceMetrics(BaseContentModel):
    """Performance metrics model"""    
    content_id: str = Field(..., description="Content identifier")
    platform: Platform = Field(..., description="Platform")
    content_type: ContentType = Field(..., description="Content type")
    
    # Engagement metrics
    views: int = Field(0, ge=0, description="Number of views")
    likes: int = Field(0, ge=0, description="Number of likes")
    shares: int = Field(0, ge=0, description="Number of shares")
    comments: int = Field(0, ge=0, description="Number of comments")
    clicks: int = Field(0, ge=0, description="Number of clicks")
    conversions: int = Field(0, ge=0, description="Number of conversions")
    
    # Reach metrics
    reach: int = Field(0, ge=0, description="Content reach")
    impressions: int = Field(0, ge=0, description="Number of impressions")
    
    # Calculated metrics
    engagement_rate: float = Field(0, ge=0, le=1, description="Engagement rate")
    click_through_rate: float = Field(0, ge=0, le=1, description="Click-through rate")
    conversion_rate: float = Field(0, ge=0, le=1, description="Conversion rate")
    
    # Quality metrics
    quality_score: Optional[float] = Field(None, description="Content quality score")
    sentiment_score: Optional[float] = Field(None, description="Audience sentiment score")
    
    # Timestamps
    created_at: datetime = Field(..., description="Content creation time")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last metrics update")


class PerformanceInsight(BaseContentModel):
    """Performance insight model"""    
    insight_type: str = Field(..., description="Type of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    impact_level: Literal["high", "medium", "low"] = Field(..., description="Impact level")
    recommendation: str = Field(..., description="Recommended action")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in insight")
    data_points: Dict[str, Any] = Field(..., description="Supporting data points")


class PerformanceAnalysisResponse(BaseContentModel):
    """Response model for performance analysis"""    
    content_id: str = Field(..., description="Content identifier")
    analysis_type: str = Field(..., description="Type of analysis performed")
    
    # Performance data
    performance_metrics: PerformanceMetrics = Field(..., description="Performance metrics")
    insights: List[PerformanceInsight] = Field(..., description="Generated insights")
    
    # Comparative analysis
    benchmark_comparison: Optional[Dict[str, Any]] = Field(None, description="Benchmark comparison")
    historical_comparison: Optional[Dict[str, Any]] = Field(None, description="Historical comparison")
    
    # Recommendations
    optimization_recommendations: List[str] = Field(..., description="Optimization recommendations")
    next_actions: List[str] = Field(..., description="Recommended next actions")
    
    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    analysis_version: str = Field("1.0", description="Analysis algorithm version")


class ContentRecommendationsResponse(BaseContentModel):
    """Response model for content recommendations"""    
    content_type: ContentType = Field(..., description="Content type")
    target_audience: Optional[str] = Field(None, description="Target audience")
    platform: Optional[Platform] = Field(None, description="Target platform")
    
    # Recommendations
    recommendations: List[str] = Field(..., description="General recommendations")
    best_practices: List[str] = Field(..., description="Best practices")
    template_suggestions: List[str] = Field(..., description="Template suggestions")
    optimization_tips: List[str] = Field(..., description="Optimization tips")
    
    # Content ideas
    topic_suggestions: List[str] = Field(default_factory=list, description="Topic suggestions")
    trending_themes: List[str] = Field(default_factory=list, description="Trending themes")
    
    # Timing and frequency
    optimal_posting_times: Optional[List[str]] = Field(None, description="Optimal posting times")
    recommended_frequency: Optional[str] = Field(None, description="Recommended posting frequency")
    
    # Performance predictions
    engagement_forecast: Optional[Dict[str, float]] = Field(None, description="Engagement forecast")
    success_probability: Optional[float] = Field(None, description="Success probability")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    recommendation_version: str = Field("1.0", description="Recommendation algorithm version")


# Utility Models
class ContentMetadata(BaseContentModel):
    """Content metadata model"""    
    title: Optional[str] = Field(None, description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    author: Optional[str] = Field(None, description="Content author")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    category: Optional[str] = Field(None, description="Content category")
    
    # SEO metadata
    meta_title: Optional[str] = Field(None, description="SEO meta title")
    meta_description: Optional[str] = Field(None, description="SEO meta description")
    canonical_url: Optional[str] = Field(None, description="Canonical URL")
    
    # Social media metadata
    og_title: Optional[str] = Field(None, description="Open Graph title")
    og_description: Optional[str] = Field(None, description="Open Graph description")
    og_image: Optional[str] = Field(None, description="Open Graph image URL")
    
    # Publishing metadata
    publish_date: Optional[datetime] = Field(None, description="Publish date")
    last_modified: Optional[datetime] = Field(None, description="Last modified date")
    status: Optional[str] = Field(None, description="Publishing status")


class ABTestConfiguration(BaseContentModel):
    """A/B test configuration model"""    
    test_id: str = Field(..., description="Unique test identifier")
    test_name: str = Field(..., description="Test name")
    hypothesis: str = Field(..., description="Test hypothesis")
    
    # Test variants
    variant_a: Dict[str, Any] = Field(..., description="Variant A configuration")
    variant_b: Dict[str, Any] = Field(..., description="Variant B configuration")
    
    # Test parameters
    traffic_split: float = Field(0.5, ge=0, le=1, description="Traffic split (0.5 = 50/50)")
    duration_days: int = Field(7, ge=1, le=90, description="Test duration in days")
    success_metric: str = Field(..., description="Primary success metric")
    
    # Statistical settings
    confidence_level: float = Field(0.95, ge=0.8, le=0.99, description="Statistical confidence level")
    minimum_sample_size: int = Field(100, ge=10, description="Minimum sample size per variant")
    
    # Test status
    status: Literal["draft", "running", "completed", "cancelled"] = Field("draft", description="Test status")
    started_at: Optional[datetime] = Field(None, description="Test start time")
    ended_at: Optional[datetime] = Field(None, description="Test end time")


# Error Models
class ContentError(BaseContentModel):
    """Content error model"""    
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    error_type: Literal["validation", "generation", "optimization", "system"] = Field(
        ..., description="Error type"
    )
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")


# Batch Processing Models
class BatchContentRequest(BaseContentModel):
    """Batch content generation request"""    
    batch_id: str = Field(..., description="Batch identifier")
    requests: List[ContentGenerationRequest] = Field(..., description="List of content requests")
    
    # Batch settings
    parallel_processing: bool = Field(True, description="Enable parallel processing")
    max_concurrent: int = Field(5, ge=1, le=10, description="Maximum concurrent processes")
    
    # Quality settings
    quality_threshold: float = Field(0.7, ge=0, le=1, description="Minimum quality threshold")
    auto_retry: bool = Field(True, description="Auto-retry failed generations")
    
    # Notification settings
    notify_on_completion: bool = Field(False, description="Send notification on completion")
    notification_email: Optional[EmailStr] = Field(None, description="Notification email")


class BatchContentResponse(BaseContentModel):
    """Batch content generation response"""    
    batch_id: str = Field(..., description="Batch identifier")
    status: Literal["processing", "completed", "failed", "partial"] = Field(
        ..., description="Batch status"
    )
    
    # Progress tracking
    total_requests: int = Field(..., description="Total number of requests")
    completed_requests: int = Field(..., description="Number of completed requests")
    failed_requests: int = Field(..., description="Number of failed requests")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage")
    
    # Results
    results: List[ContentGenerationResponse] = Field(..., description="Individual results")
    
    # Summary statistics
    average_quality_score: Optional[float] = Field(None, description="Average quality score")
    total_processing_time: Optional[float] = Field(None, description="Total processing time")
    
    # Timestamps
    started_at: datetime = Field(..., description="Batch start time")
    completed_at: Optional[datetime] = Field(None, description="Batch completion time")
    
    # Error summary
    errors: List[ContentError] = Field(default_factory=list, description="Batch errors")
