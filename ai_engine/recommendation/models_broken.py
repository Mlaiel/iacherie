"""Data Models for Recommendation System
Comprehensive data structures for recommendations, matches, and insights

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev + AI Architect Developer
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Developer
- DevOps Engineer
- AI Prompt Engineer
Email: mlaiel@live.de
"""from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid


class Platform(Enum):
    """Platform enumeration"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    DISCORD = "discord"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"


class RecommendationType(Enum):
    """Recommendation type enumeration"""    CONTENT_DISCOVERY = "content_discovery"
    CREATOR_COLLABORATION = "creator_collaboration"
    TREND_BASED = "trend_based"
    MONETIZATION = "monetization"
    CROSS_PLATFORM = "cross_platform"
    VIRAL_POTENTIAL = "viral_potential"
    SEASONAL = "seasonal"
    GEOGRAPHIC = "geographic"


class ContentType(Enum):
    """Content type enumeration"""    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    PODCAST = "podcast"
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"
    INTERACTIVE = "interactive"
    STORY = "story"
    REEL = "reel"
    MUSIC_VIDEO = "music_video"
    COVER_SONG = "cover_song"
    ORIGINAL_SONG = "original_song"
    REMIX = "remix"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    UNBOXING = "unboxing"
    VLOG = "vlog"
    CHALLENGE = "challenge"
    COLLABORATION = "collaboration"
    DANCE = "dance"
    COMEDY = "comedy"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"
    EDUCATIONAL = "educational"
    NEWS = "news"
    DOCUMENTARY = "documentary"
    BEHIND_SCENES = "behind_scenes"
    Q_AND_A = "q_and_a"
    CONTEST = "contest"
    GIVEAWAY = "giveaway"
    PRODUCT_PLACEMENT = "product_placement"
    SPONSORED_CONTENT = "sponsored_content"
    BRAND_PARTNERSHIP = "brand_partnership"
    CONTENT_SERIES = "content_series"
    EVENT_COLLABORATION = "event_collaboration"


class TrendType(Enum):
    """Trend type enumeration"""    RISING = "rising"
    VIRAL = "viral"
    SEASONAL = "seasonal"
    DECLINING = "declining"
    STABLE = "stable"
    EMERGING = "emerging"
    NICHE = "niche"


class RevenueStream(Enum):
    """Revenue stream enumeration"""    ADVERTISING = "advertising"
    SUBSCRIPTIONS = "subscriptions"
    MERCHANDISE = "merchandise"
    SPONSORSHIPS = "sponsorships"
    DONATIONS = "donations"
    LICENSING = "licensing"
    AFFILIATE = "affiliate"
    COURSES = "courses"
    LIVE_EVENTS = "live_events"
    NFT = "nft"
Development Team Specialties:
- Lead Dev + AI Architect Developer
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Developer
- DevOps Engineer
- AI Prompt Engineer
Email: mlaiel@live.de
"""from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid


class ContentType(Enum):
    """Content type enumeration"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTIMODAL = "multimodal"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"


class Platform(Enum):
    """Platform enumeration"""    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    DISCORD = "discord"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"


class RecommendationType(Enum):
    """Recommendation type enumeration"""    CONTENT_DISCOVERY = "content_discovery"
    CREATOR_COLLABORATION = "creator_collaboration"
    TREND_BASED = "trend_based"
    MONETIZATION = "monetization"
    CROSS_PLATFORM = "cross_platform"
    VIRAL_POTENTIAL = "viral_potential"
    SEASONAL = "seasonal"
    GEOGRAPHIC = "geographic"


class MatchType(Enum):
    """Collaboration match type enumeration"""    COMPLEMENTARY_SKILLS = "complementary_skills"
    SIMILAR_AUDIENCE = "similar_audience"
    CROSS_GENRE = "cross_genre"
    SKILL_EXCHANGE = "skill_exchange"
    BRAND_PARTNERSHIP = "brand_partnership"
    CONTENT_SERIES = "content_series"
    EVENT_COLLABORATION = "event_collaboration"


class TrendType(Enum):
    """Trend type enumeration"""    RISING = "rising"
    VIRAL = "viral"
    SEASONAL = "seasonal"
    DECLINING = "declining"
    STABLE = "stable"
    EMERGING = "emerging"
    NICHE = "niche"


class RevenueStream(Enum):
    """Revenue stream enumeration"""    ADVERTISING = "advertising"
    SUBSCRIPTIONS = "subscriptions"
    MERCHANDISE = "merchandise"
    SPONSORSHIPS = "sponsorships"
    DONATIONS = "donations"
    LICENSING = "licensing"
    AFFILIATE = "affiliate"
    COURSES = "courses"
    LIVE_EVENTS = "live_events"
    NFT = "nft"


@dataclass
class Engagement:
    """Engagement metrics structure"""    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0
    saves: int = 0
    clicks: int = 0
    reactions: Dict[str, int] = field(default_factory=dict)
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ContentMetadata:
    """Content metadata structure"""    title: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    language: str = "en"
    duration: Optional[float] = None
    file_size: Optional[int] = None
    resolution: Optional[str] = None
    quality_score: Optional[float] = None
    creation_date: Optional[datetime] = None
    upload_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    copyright_info: Optional[Dict[str, Any]] = None
    licensing_info: Optional[Dict[str, Any]] = None


@dataclass
class CreatorProfile:
    """Creator profile data structure"""    creator_id: str
    name: str
    handle: str
    bio: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    platforms: List[Platform] = field(default_factory=list)
    followers_count: Dict[Platform, int] = field(default_factory=dict)
    engagement_rate: Dict[Platform, float] = field(default_factory=dict)
    content_types: List[ContentType] = field(default_factory=list)
    collaboration_history: List[str] = field(default_factory=list)
    revenue_streams: List[RevenueStream] = field(default_factory=list)
    average_revenue: Optional[float] = None
    location: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    brand_partnerships: List[str] = field(default_factory=list)
    verification_status: bool = False
    quality_score: float = 0.0
    reputation_score: float = 0.0
    created_date: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)


@dataclass
class AudienceInsight:
    """Audience analysis insight"""    age_distribution: Dict[str, float] = field(default_factory=dict)
    gender_distribution: Dict[str, float] = field(default_factory=dict)
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    interest_categories: Dict[str, float] = field(default_factory=dict)
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    platform_preferences: Dict[Platform, float] = field(default_factory=dict)
    peak_activity_hours: List[int] = field(default_factory=list)
    content_preferences: Dict[ContentType, float] = field(default_factory=dict)
    purchasing_behavior: Dict[str, Any] = field(default_factory=dict)
    social_influence_score: float = 0.0


@dataclass
class RecommendationRequest:
    """Request structure for recommendations"""    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    creator_id: Optional[str] = None
    recommendation_type: RecommendationType = RecommendationType.CONTENT_DISCOVERY
    content_type: Optional[ContentType] = None
    platforms: List[Platform] = field(default_factory=list)
    max_results: int = 20
    min_confidence_score: float = 0.7
    time_window: Optional[timedelta] = None
    geographic_filter: Optional[str] = None
    language_filter: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    exclude_content: List[str] = field(default_factory=list)
    personalization_level: float = 0.8
    diversity_factor: float = 0.3
    novelty_factor: float = 0.2
    include_explanations: bool = True
    real_time: bool = True
    filters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ContentRecommendation:
    """Content recommendation structure"""    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    title: str = ""
    content_type: ContentType = ContentType.TEXT
    creator_id: str = ""
    creator_name: str = ""
    platform: Platform = Platform.YOUTUBE
    confidence_score: float = 0.0
    relevance_score: float = 0.0
    quality_score: float = 0.0
    engagement_prediction: float = 0.0
    viral_potential: float = 0.0
    monetization_potential: float = 0.0
    trend_alignment: float = 0.0
    audience_match: float = 0.0
    content_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    duration: Optional[float] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    share_count: Optional[int] = None
    publication_date: Optional[datetime] = None
    explanations: List[str] = field(default_factory=list)
    similar_content: List[str] = field(default_factory=list)
    cross_platform_opportunities: List[Platform] = field(default_factory=list)
    estimated_revenue: Optional[float] = None
    protection_status: Dict[str, Any] = field(default_factory=dict)
    metadata: ContentMetadata = field(default_factory=lambda: ContentMetadata(title=""))
    recommendation_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CreatorCompatibility:
    """Creator compatibility analysis structure"""    creator1_id: str
    creator2_id: str
    compatibility_score: float
    shared_attributes: Dict[str, Any] = field(default_factory=dict)
    complementary_skills: List[str] = field(default_factory=list)
    audience_overlap: float = 0.0
    collaboration_potential: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    success_probability: float = 0.0
    recommended_collaboration_types: List[str] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CollaborationMatch:
    """Collaboration match structure"""    match_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requesting_creator_id: str = ""
    matched_creator_id: str = ""
    match_type: MatchType = MatchType.COMPLEMENTARY_SKILLS
    compatibility_score: float = 0.0
    audience_overlap: float = 0.0
    skill_complementarity: float = 0.0
    genre_synergy: float = 0.0
    geographic_compatibility: float = 0.0
    platform_alignment: float = 0.0
    revenue_potential: float = 0.0
    viral_potential: float = 0.0
    risk_assessment: float = 0.0
    estimated_reach_increase: Optional[int] = None
    estimated_engagement_boost: Optional[float] = None
    estimated_revenue_impact: Optional[float] = None
    collaboration_type_suggestions: List[str] = field(default_factory=list)
    content_format_suggestions: List[ContentType] = field(default_factory=list)
    platform_recommendations: List[Platform] = field(default_factory=list)
    timeline_suggestion: Optional[timedelta] = None
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    success_factors: List[str] = field(default_factory=list)
    potential_challenges: List[str] = field(default_factory=list)
    collaboration_history: List[str] = field(default_factory=list)
    mutual_connections: List[str] = field(default_factory=list)
    explanations: List[str] = field(default_factory=list)
    creator_profiles: Dict[str, CreatorProfile] = field(default_factory=dict)
    match_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BrandMatch:
    """Brand partnership match structure"""    brand_id: str
    creator_id: str
    match_score: float
    brand_name: str
    creator_name: str
    compatibility_reasons: List[str] = field(default_factory=list)
    audience_alignment: float = 0.0
    brand_safety_score: float = 0.0
    estimated_partnership_value: Optional[float] = None
    partnership_type: str = "sponsored_content"
    content_guidelines: Dict[str, Any] = field(default_factory=dict)
    campaign_suggestions: List[str] = field(default_factory=list)
    target_demographics: Dict[str, Any] = field(default_factory=dict)
    performance_expectations: Dict[str, float] = field(default_factory=dict)
    contract_suggestions: Dict[str, Any] = field(default_factory=dict)
    match_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TrendInsight:
    """Trend analysis insight structure"""    trend_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trend_name: str = ""
    trend_type: TrendType = TrendType.RISING
    content_type: ContentType = ContentType.TEXT
    platforms: List[Platform] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    growth_rate: float = 0.0
    momentum_score: float = 0.0
    viral_coefficient: float = 0.0
    engagement_velocity: float = 0.0
    saturation_level: float = 0.0
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    demographic_appeal: Dict[str, float] = field(default_factory=dict)
    peak_prediction: Optional[datetime] = None
    duration_prediction: Optional[timedelta] = None
    monetization_opportunities: List[RevenueStream] = field(default_factory=list)
    creator_opportunities: List[str] = field(default_factory=list)
    content_suggestions: List[str] = field(default_factory=list)
    platform_optimization: Dict[Platform, Dict[str, Any]] = field(default_factory=dict)
    related_trends: List[str] = field(default_factory=list)
    influencing_factors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    confidence_interval: Tuple[float, float] = (0.0, 1.0)
    data_sources: List[str] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class RevenueStrategy:
    """Revenue optimization strategy structure"""    strategy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    target_revenue: Optional[float] = None
    optimization_period: timedelta = field(default_factory=lambda: timedelta(days=30))
    primary_revenue_streams: List[RevenueStream] = field(default_factory=list)
    platform_strategy: Dict[Platform, Dict[str, Any]] = field(default_factory=dict)
    content_strategy: Dict[ContentType, Dict[str, Any]] = field(default_factory=dict)
    audience_targeting: AudienceInsight = field(default_factory=AudienceInsight)
    pricing_recommendations: Dict[str, float] = field(default_factory=dict)
    collaboration_opportunities: List[str] = field(default_factory=list)
    brand_partnership_targets: List[str] = field(default_factory=list)
    growth_projections: Dict[str, float] = field(default_factory=dict)
    milestone_timeline: Dict[datetime, str] = field(default_factory=dict)
    resource_allocation: Dict[str, float] = field(default_factory=dict)
    performance_kpis: List[str] = field(default_factory=list)
    risk_mitigation: List[str] = field(default_factory=list)
    success_metrics: Dict[str, float] = field(default_factory=dict)
    optimization_score: float = 0.0
    confidence_level: float = 0.0
    implementation_complexity: str = "medium"
    expected_roi: Optional[float] = None
    strategy_explanations: List[str] = field(default_factory=list)
    alternative_strategies: List[Dict[str, Any]] = field(default_factory=list)
    created_timestamp: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class RecommendationResponse:
    """Response structure for recommendation requests"""    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    status: str = "success"
    content_recommendations: List[ContentRecommendation] = field(default_factory=list)
    collaboration_matches: List[CollaborationMatch] = field(default_factory=list)
    trend_insights: List[TrendInsight] = field(default_factory=list)
    revenue_strategies: List[RevenueStrategy] = field(default_factory=list)
    total_results: int = 0
    processing_time_ms: float = 0.0
    confidence_level: float = 0.0
    quality_score: float = 0.0
    personalization_applied: bool = False
    trend_boost_applied: bool = False
    protection_filtered: bool = False
    explanations: List[str] = field(default_factory=list)
    recommendations_metadata: Dict[str, Any] = field(default_factory=dict)
    cache_hit: bool = False
    model_version: str = "1.0.0"
    api_version: str = "1.0.0"
    response_timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for recommendation system"""    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    recommendation_accuracy: float = 0.0
    user_satisfaction_score: float = 0.0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue_impact: float = 0.0
    model_performance: Dict[str, float] = field(default_factory=dict)
    platform_performance: Dict[Platform, Dict[str, float]] = field(default_factory=dict)
    content_type_performance: Dict[ContentType, Dict[str, float]] = field(default_factory=dict)
    geographic_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    trend_prediction_accuracy: float = 0.0
    collaboration_success_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ContentOpportunity:
    """Content creation opportunity structure"""    opportunity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    content_type: ContentType
    platform_suggestions: List[Platform] = field(default_factory=list)
    trending_topics: List[str] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    optimal_timing: Dict[str, Any] = field(default_factory=dict)
    engagement_potential: float = 0.0
    virality_score: float = 0.0
    competition_level: str = "medium"
    difficulty_score: float = 0.5
    estimated_reach: int = 0
    estimated_engagement: int = 0
    content_suggestions: List[str] = field(default_factory=list)
    hashtag_suggestions: List[str] = field(default_factory=list)
    collaboration_potential: List[str] = field(default_factory=list)
    monetization_opportunities: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    success_metrics: Dict[str, float] = field(default_factory=dict)
    opportunity_timestamp: datetime = field(default_factory=datetime.now)


# Type aliases for convenience
RecommendationList = List[ContentRecommendation]
CollaborationList = List[CollaborationMatch]
TrendList = List[TrendInsight]
StrategyList = List[RevenueStrategy]
