"""
AI Recommendation Models - Data Models for Recommendation System
===============================================================

Data models and structures for the Ainflue AI recommendation system.
Provides comprehensive models for creators, content, and recommendations.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime


class Platform(Enum):
    """Social media platforms supported."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    SPOTIFY = "spotify"


class ContentType(Enum):
    """Types of content supported."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    STORY = "story"
    REEL = "reel"
    POST = "post"
    STREAM = "stream"


class RevenueStream(Enum):
    """Revenue stream types."""
    SPONSORED_CONTENT = "sponsored_content"
    AFFILIATE_MARKETING = "affiliate_marketing"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    PRODUCT_PLACEMENT = "product_placement"
    SUBSCRIPTION = "subscription"
    DONATIONS = "donations"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"


@dataclass
class Engagement:
    """Engagement metrics."""
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    saves: int = 0
    click_through_rate: float = 0.0
    engagement_rate: float = 0.0
    
    def calculate_total_engagement(self) -> int:
        """Calculate total engagement."""



        return self.likes + self.comments + self.shares + self.saves


@dataclass
class PerformanceMetrics:
    """Performance metrics for content or creators."""
    reach: int = 0
    impressions: int = 0
    engagement: Engagement = field(default_factory=Engagement)
    conversion_rate: float = 0.0
    revenue_generated: float = 0.0
    audience_growth: float = 0.0
    brand_sentiment: float = 0.0


@dataclass
class ContentMetadata:
    """Metadata for content pieces."""
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    category: str = ""
    language: str = "en"
    duration: Optional[float] = None
    file_size: Optional[int] = None
    resolution: Optional[str] = None
    format: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CreatorProfile:
    """Comprehensive creator profile."""
    creator_id: str
    username: str
    display_name: str
    bio: str = ""
    platforms: List[Platform] = field(default_factory=list)
    content_types: List[ContentType] = field(default_factory=list)
    follower_count: Dict[Platform, int] = field(default_factory=dict)
    engagement_rates: Dict[Platform, float] = field(default_factory=dict)
    niche: List[str] = field(default_factory=list)
    location: str = ""
    languages: List[str] = field(default_factory=lambda: ["en"])
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    revenue_streams: List[RevenueStream] = field(default_factory=list)
    collaboration_history: List[str] = field(default_factory=list)
    brand_safety_score: float = 0.85
    authenticity_score: float = 0.90
    
    def get_total_followers(self) -> int:
        """Get total followers across all platforms."""



        return sum(self.follower_count.values())
    
    def get_average_engagement_rate(self) -> float:
        """Get average engagement rate across platforms."""
        if not self.engagement_rates:
            return 0.0
        return sum(self.engagement_rates.values()) / len(self.engagement_rates)


@dataclass
class ContentRecommendation:
    """Content recommendation for creators."""
    content_id: str
    title: str
    content_type: ContentType
    platform: Platform
    description: str = ""
    target_audience: Dict[str, Any] = field(default_factory=dict)
    predicted_performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    optimal_posting_time: Optional[datetime] = None
    recommended_hashtags: List[str] = field(default_factory=list)
    content_ideas: List[str] = field(default_factory=list)
    collaboration_opportunities: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    reasoning: str = ""


@dataclass
class CreatorCompatibility:
    """Compatibility metrics between creators."""
    creator1_id: str
    creator2_id: str
    compatibility_score: float = 0.0
    shared_audience_overlap: float = 0.0
    content_synergy_score: float = 0.0
    brand_alignment_score: float = 0.0
    collaboration_potential: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)


@dataclass
class CollaborationMatch:
    """Match between creators for collaboration."""
    match_id: str
    creators: List[str] = field(default_factory=list)
    compatibility: CreatorCompatibility = field(default_factory=lambda: CreatorCompatibility("", ""))
    collaboration_type: str = ""
    project_ideas: List[str] = field(default_factory=list)
    expected_outcomes: Dict[str, Any] = field(default_factory=dict)
    timeline: Optional[str] = None
    budget_range: Optional[tuple] = None
    success_probability: float = 0.0


@dataclass
class BrandMatch:
    """Match between creator and brand."""
    match_id: str
    creator_id: str
    brand_name: str
    brand_category: str = ""
    alignment_score: float = 0.0
    audience_overlap: float = 0.0
    engagement_potential: float = 0.0
    brand_safety_rating: float = 0.0
    campaign_types: List[str] = field(default_factory=list)
    estimated_reach: int = 0
    estimated_cost: float = 0.0


@dataclass
class TrendInsight:
    """Trending content or topic insights."""
    trend_id: str
    title: str
    description: str = ""
    category: str = ""
    platforms: List[Platform] = field(default_factory=list)
    growth_rate: float = 0.0
    engagement_rate: float = 0.0
    predicted_duration: Optional[int] = None  # in days
    target_demographics: Dict[str, Any] = field(default_factory=dict)
    related_hashtags: List[str] = field(default_factory=list)
    content_opportunities: List[str] = field(default_factory=list)
    risk_level: str = "low"


@dataclass
class AudienceInsight:
    """Audience analytics and insights."""
    audience_id: str
    demographics: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    behavior_patterns: Dict[str, Any] = field(default_factory=dict)
    platform_preferences: List[Platform] = field(default_factory=list)
    content_preferences: List[ContentType] = field(default_factory=list)
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    purchasing_behavior: Dict[str, Any] = field(default_factory=dict)
    growth_potential: float = 0.0


@dataclass
class RevenueStrategy:
    """Revenue optimization strategy."""
    strategy_id: str
    creator_id: str
    revenue_streams: List[RevenueStream] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    projected_revenue: float = 0.0
    timeline: str = ""
    risk_assessment: str = "medium"
    implementation_difficulty: str = "medium"
    required_resources: List[str] = field(default_factory=list)
    success_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentOpportunity:
    """Content creation opportunity."""
    opportunity_id: str
    title: str
    description: str = ""
    content_type: ContentType = ContentType.POST
    platform: Platform = Platform.INSTAGRAM
    target_audience: Dict[str, Any] = field(default_factory=dict)
    trending_factors: List[str] = field(default_factory=list)
    competition_level: str = "medium"
    effort_required: str = "medium"
    potential_reach: int = 0
    expected_engagement: float = 0.0
    revenue_potential: float = 0.0
    deadline: Optional[datetime] = None


@dataclass
class RecommendationRequest:
    """Request for recommendations from the system."""
    user_id: str
    request_type: str = "content"
    parameters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 10
    platform_filter: Optional[List[Platform]] = None
    content_type_filter: Optional[List[ContentType]] = None
    
    def __post_init__(self):
        if self.platform_filter is None:
            self.platform_filter = []
        if self.content_type_filter is None:
            self.content_type_filter = []


@dataclass
class RecommendationResponse:
    """Response containing recommendations from the system."""
    request_id: str
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: List[float] = field(default_factory=list)
    processing_time: float = 0.0
    total_candidates: int = 0
    
    def get_top_recommendations(self, n: int) -> List[Dict[str, Any]]:
        """Get top N recommendations."""



        return self.recommendations[:n]


# Export all models
__all__ = [
    'Platform',
    'ContentType', 
    'RevenueStream',
    'Engagement',
    'PerformanceMetrics',
    'ContentMetadata',
    'CreatorProfile',
    'ContentRecommendation',
    'CreatorCompatibility',
    'CollaborationMatch',
    'BrandMatch',
    'TrendInsight',
    'AudienceInsight',
    'RevenueStrategy',
    'ContentOpportunity',
    'RecommendationRequest',
    'RecommendationResponse'
]