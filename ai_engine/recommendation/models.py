"""
Ultra-Advanced Data Models for Enterprise Recommendation System
Comprehensive data structures for multi-format content recommendations, creator collaboration,
revenue optimization, and market intelligence

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
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import json
from pydantic import BaseModel, validator, Field
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class PlatformType(Enum):
    """Comprehensive platform enumeration for multi-platform ecosystem"""
    # Music & Audio Platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    AUDIOMACK = "audiomack"
    TIDAL = "tidal"
    DEEZER = "deezer"
    PANDORA = "pandora"
    
    # Video Platforms
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    
    # Social Media Platforms
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    DISCORD = "discord"
    REDDIT = "reddit"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    CLUBHOUSE = "clubhouse"
    
    # Content Creation Platforms
    MEDIUM = "medium"
    SUBSTACK = "substack"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    CAMEO = "cameo"
    
    # Gaming & Streaming
    TWITCH_MUSIC = "twitch_music"
    DISCORD_STAGE = "discord_stage"
    STREAMLABS = "streamlabs"
    
    # Emerging Platforms
    THREADS = "threads"
    MASTODON = "mastodon"
    BLUESKY = "bluesky"


class ContentFormat(Enum):
    """Advanced content format classification"""
    # Audio Formats
    MUSIC_TRACK = "music_track"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    VOICE_MEMO = "voice_memo"
    AUDIO_STORY = "audio_story"
    
    # Video Formats
    LONG_FORM_VIDEO = "long_form_video"
    SHORT_FORM_VIDEO = "short_form_video"
    LIVE_STREAM = "live_stream"
    MUSIC_VIDEO = "music_video"
    TUTORIAL = "tutorial"
    VLOG = "vlog"
    
    # Image Formats
    PHOTO = "photo"
    ARTWORK = "artwork"
    INFOGRAPHIC = "infographic"
    MEME = "meme"
    CAROUSEL = "carousel"
    
    # Text Formats
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    STORY = "story"
    ARTICLE = "article"
    NEWSLETTER = "newsletter"
    
    # Interactive Formats
    POLL = "poll"
    QUIZ = "quiz"
    LIVE_QA = "live_qa"
    COLLABORATION = "collaboration"


class RecommendationType(Enum):
    """Comprehensive recommendation type classification"""
    CONTENT_DISCOVERY = "content_discovery"
    CREATOR_COLLABORATION = "creator_collaboration"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    TREND_ANALYSIS = "trend_analysis"
    BRAND_PARTNERSHIP = "brand_partnership"
    AUDIENCE_EXPANSION = "audience_expansion"
    CROSS_PLATFORM = "cross_platform"
    VIRAL_PREDICTION = "viral_prediction"
    MONETIZATION_STRATEGY = "monetization_strategy"
    CONTENT_OPTIMIZATION = "content_optimization"
    MARKET_INTELLIGENCE = "market_intelligence"
    COMPETITIVE_ANALYSIS = "competitive_analysis"


class EngagementMetricType(Enum):
    """Advanced engagement metrics classification"""
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    CLICK_THROUGH_RATE = "click_through_rate"
    WATCH_TIME = "watch_time"
    COMPLETION_RATE = "completion_rate"
    ENGAGEMENT_RATE = "engagement_rate"
    IMPRESSION_RATE = "impression_rate"
    CONVERSION_RATE = "conversion_rate"
    REVENUE_PER_VIEW = "revenue_per_view"
    SUBSCRIBER_GROWTH = "subscriber_growth"
    BRAND_MENTION_SENTIMENT = "brand_mention_sentiment"


class CollaborationType(Enum):
    """Advanced collaboration type classification"""
    MUSIC_PRODUCTION = "music_production"
    VIDEO_PRODUCTION = "video_production"
    CONTENT_CREATION = "content_creation"
    BRAND_CAMPAIGN = "brand_campaign"
    CROSS_PROMOTION = "cross_promotion"
    SKILL_EXCHANGE = "skill_exchange"
    JOINT_LIVESTREAM = "joint_livestream"
    REMIX_COLLABORATION = "remix_collaboration"
    PODCAST_GUEST = "podcast_guest"
    DUET_PERFORMANCE = "duet_performance"
    EDUCATIONAL_SERIES = "educational_series"
    CHARITY_INITIATIVE = "charity_initiative"


class RevenueModel(Enum):
    """Comprehensive revenue model types"""
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    MERCHANDISE = "merchandise"
    DONATIONS = "donations"
    SPONSORSHIP = "sponsorship"
    AFFILIATE_MARKETING = "affiliate_marketing"
    DIRECT_SALES = "direct_sales"
    LICENSING = "licensing"
    STREAMING_ROYALTIES = "streaming_royalties"
    LIVE_PERFORMANCE = "live_performance"
    EDUCATIONAL_CONTENT = "educational_content"
@dataclass
class UserProfile:
    """Ultra-comprehensive user profile for advanced personalization"""
    user_id: str
    username: str
    email: Optional[str] = None
    
    # Demographic Information
    age_range: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[Dict[str, str]] = None
    timezone: Optional[str] = None
    language_preferences: List[str] = field(default_factory=list)
    
    # Content Preferences
    preferred_content_formats: List[ContentFormat] = field(default_factory=list)
    preferred_genres: List[str] = field(default_factory=list)
    preferred_topics: List[str] = field(default_factory=list)
    content_consumption_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Platform Activity
    active_platforms: List[PlatformType] = field(default_factory=list)
    platform_metrics: Dict[PlatformType, Dict[str, float]] = field(default_factory=dict)
    cross_platform_behavior: Dict[str, Any] = field(default_factory=dict)
    
    # Engagement Behavior
    engagement_patterns: Dict[str, float] = field(default_factory=dict)
    peak_activity_hours: List[int] = field(default_factory=list)
    average_session_duration: float = 0.0
    content_completion_rates: Dict[ContentFormat, float] = field(default_factory=dict)
    
    # Social & Collaboration
    collaboration_history: List[str] = field(default_factory=list)
    network_connections: List[str] = field(default_factory=list)
    influence_score: float = 0.0
    follower_demographics: Dict[str, Any] = field(default_factory=dict)
    
    # Revenue & Monetization
    revenue_history: List[Dict[str, Any]] = field(default_factory=list)
    monetization_preferences: List[RevenueModel] = field(default_factory=list)
    brand_partnership_interests: List[str] = field(default_factory=list)
    
    # Advanced Analytics
    personality_insights: Dict[str, float] = field(default_factory=dict)
    content_quality_score: float = 0.0
    viral_content_history: List[Dict[str, Any]] = field(default_factory=list)
    trend_adoption_score: float = 0.0
    
    # Privacy & Consent
    privacy_settings: Dict[str, bool] = field(default_factory=dict)
    data_usage_consent: List[str] = field(default_factory=list)
    personalization_level: float = 1.0
    
    # System Metadata
    profile_created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    profile_version: str = "v2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for serialization"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'demographic_info': {
                'age_range': self.age_range,
                'gender': self.gender,
                'location': self.location,
                'timezone': self.timezone,
                'language_preferences': self.language_preferences
            },
            'content_preferences': {
                'formats': [fmt.value for fmt in self.preferred_content_formats],
                'genres': self.preferred_genres,
                'topics': self.preferred_topics,
                'consumption_patterns': self.content_consumption_patterns
            },
            'platform_activity': {
                'active_platforms': [plat.value for plat in self.active_platforms],
                'metrics': {plat.value: metrics for plat, metrics in self.platform_metrics.items()},
                'cross_platform_behavior': self.cross_platform_behavior
            },
            'engagement_behavior': self.engagement_patterns,
            'social_collaboration': {
                'history': self.collaboration_history,
                'connections': self.network_connections,
                'influence_score': self.influence_score,
                'follower_demographics': self.follower_demographics
            },
            'monetization': {
                'revenue_history': self.revenue_history,
                'preferences': [model.value for model in self.monetization_preferences],
                'brand_interests': self.brand_partnership_interests
            },
            'analytics': {
                'personality_insights': self.personality_insights,
                'quality_score': self.content_quality_score,
                'viral_history': self.viral_content_history,
                'trend_adoption': self.trend_adoption_score
            },
            'metadata': {
                'created_at': self.profile_created_at.isoformat(),
                'last_updated': self.last_updated.isoformat(),
                'version': self.profile_version
            }
        }


@dataclass
class RecommendationRequest:
    """Comprehensive recommendation request structure"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    
    # Content Specification
    content_types: List[ContentFormat] = field(default_factory=list)
    platforms: List[PlatformType] = field(default_factory=list)
    recommendation_types: List[RecommendationType] = field(default_factory=list)
    
    # Request Parameters
    max_results: int = 50
    min_confidence_score: float = 0.7
    include_trending: bool = True
    include_personalized: bool = True
    include_collaborative_suggestions: bool = False
    
    # Filtering & Targeting
    filters: Dict[str, Any] = field(default_factory=dict)
    exclude_content_ids: List[str] = field(default_factory=list)
    geographic_targeting: Optional[str] = None
    demographic_targeting: Dict[str, Any] = field(default_factory=dict)
    
    # Advanced Options
    diversification_factor: float = 0.3
    novelty_factor: float = 0.2
    viral_potential_threshold: float = 0.8
    revenue_optimization: bool = True
    cross_platform_optimization: bool = True
    
    # Context & Goals
    context: Optional[str] = None
    business_goals: List[str] = field(default_factory=list)
    campaign_objectives: List[str] = field(default_factory=list)
    
    # Time Constraints
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None
    urgency_level: str = "normal"  # low, normal, high, urgent
    
    # Collaboration Specific
    collaboration_goals: List[str] = field(default_factory=list)
    skill_requirements: List[str] = field(default_factory=list)
    budget_range: Optional[Tuple[float, float]] = None
    
    # Quality & Safety
    content_safety_level: str = "standard"  # minimal, standard, strict, maximum
    brand_safety_required: bool = True
    plagiarism_check: bool = True
    
    # System Metadata
    request_timestamp: datetime = field(default_factory=datetime.now)
    client_info: Dict[str, Any] = field(default_factory=dict)
    api_version: str = "v2.0"
    
    def validate(self) -> bool:
        """Validate request parameters"""
        if not self.user_id:
            raise ValueError("user_id is required")
        
        if self.max_results <= 0:
            raise ValueError("max_results must be positive")
            
        if not 0 <= self.min_confidence_score <= 1:
            raise ValueError("min_confidence_score must be between 0 and 1")
            
        if not 0 <= self.diversification_factor <= 1:
            raise ValueError("diversification_factor must be between 0 and 1")
            
        return True


@dataclass 
class ContentRecommendation:
    """Ultra-detailed content recommendation with comprehensive metadata"""
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    content_title: str = ""
    content_description: Optional[str] = None
    
    # Content Details
    content_format: ContentFormat = ContentFormat.MUSIC_TRACK
    content_type: str = ""
    creator_id: str = ""
    creator_name: str = ""
    platform: PlatformType = PlatformType.SPOTIFY
    
    # Recommendation Scoring
    confidence_score: float = 0.0
    relevance_score: float = 0.0
    quality_score: float = 0.0
    novelty_score: float = 0.0
    diversity_score: float = 0.0
    viral_potential_score: float = 0.0
    
    # Business Intelligence
    revenue_potential: float = 0.0
    engagement_prediction: Dict[EngagementMetricType, float] = field(default_factory=dict)
    audience_match_score: float = 0.0
    brand_safety_score: float = 0.0
    
    # Content Analysis
    content_features: Dict[str, Any] = field(default_factory=dict)
    genre_tags: List[str] = field(default_factory=list)
    mood_analysis: Dict[str, float] = field(default_factory=dict)
    sentiment_score: float = 0.0
    
    # Performance Predictions
    predicted_views: int = 0
    predicted_engagement_rate: float = 0.0
    predicted_completion_rate: float = 0.0
    predicted_revenue: float = 0.0
    
    # Collaboration Opportunities
    collaboration_potential: float = 0.0
    suggested_collaborators: List[str] = field(default_factory=list)
    cross_promotion_opportunities: List[str] = field(default_factory=list)
    
    # Distribution Strategy
    optimal_posting_time: Optional[datetime] = None
    recommended_platforms: List[PlatformType] = field(default_factory=list)
    hashtag_suggestions: List[str] = field(default_factory=list)
    seo_keywords: List[str] = field(default_factory=list)
    
    # Rights & Protection
    content_rights_status: str = "verified"
    copyright_info: Dict[str, Any] = field(default_factory=dict)
    usage_permissions: List[str] = field(default_factory=list)
    licensing_requirements: List[str] = field(default_factory=list)
    
    # Advanced Analytics
    trend_alignment_score: float = 0.0
    seasonal_relevance: float = 0.0
    geographic_appeal: Dict[str, float] = field(default_factory=dict)
    demographic_appeal: Dict[str, float] = field(default_factory=dict)
    
    # Explanation & Reasoning
    recommendation_reasons: List[str] = field(default_factory=list)
    algorithm_explanations: Dict[str, str] = field(default_factory=dict)
    personalization_factors: List[str] = field(default_factory=list)
    
    # System Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    recommendation_version: str = "v2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary for API response"""
        return {
            'recommendation_id': self.recommendation_id,
            'content_info': {
                'content_id': self.content_id,
                'title': self.content_title,
                'description': self.content_description,
                'format': self.content_format.value,
                'creator': {
                    'id': self.creator_id,
                    'name': self.creator_name
                },
                'platform': self.platform.value
            },
            'scoring': {
                'confidence': self.confidence_score,
                'relevance': self.relevance_score,
                'quality': self.quality_score,
                'novelty': self.novelty_score,
                'diversity': self.diversity_score,
                'viral_potential': self.viral_potential_score
            },
            'business_intelligence': {
                'revenue_potential': self.revenue_potential,
                'engagement_predictions': {metric.value: value for metric, value in self.engagement_prediction.items()},
                'audience_match': self.audience_match_score,
                'brand_safety': self.brand_safety_score
            },
            'content_analysis': {
                'features': self.content_features,
                'genres': self.genre_tags,
                'mood': self.mood_analysis,
                'sentiment': self.sentiment_score
            },
            'predictions': {
                'views': self.predicted_views,
                'engagement_rate': self.predicted_engagement_rate,
                'completion_rate': self.predicted_completion_rate,
                'revenue': self.predicted_revenue
            },
            'distribution_strategy': {
                'optimal_posting_time': self.optimal_posting_time.isoformat() if self.optimal_posting_time else None,
                'recommended_platforms': [plat.value for plat in self.recommended_platforms],
                'hashtags': self.hashtag_suggestions,
                'seo_keywords': self.seo_keywords
            },
            'rights_protection': {
                'status': self.content_rights_status,
                'copyright': self.copyright_info,
                'permissions': self.usage_permissions,
                'licensing': self.licensing_requirements
            },
            'analytics': {
                'trend_alignment': self.trend_alignment_score,
                'seasonal_relevance': self.seasonal_relevance,
                'geographic_appeal': self.geographic_appeal,
                'demographic_appeal': self.demographic_appeal
            },
            'explanation': {
                'reasons': self.recommendation_reasons,
                'algorithms': self.algorithm_explanations,
                'personalization': self.personalization_factors
            },
            'metadata': {
                'generated_at': self.generated_at.isoformat(),
                'expires_at': self.expires_at.isoformat() if self.expires_at else None,
                'version': self.recommendation_version
            }
        }
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTIMODAL = "multimodal"
    PODCAST = "podcast"
    MUSIC = "music"
    STORY = "story"
    LIVE_STREAM = "live_stream"
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    REVIEW = "review"
    TUTORIAL = "tutorial"
    VLOG = "vlog"
    CHALLENGE = "challenge"
    REACTION = "reaction"
    COLLABORATION = "collaboration"
    PROMOTIONAL = "promotional"
    BEHIND_SCENES = "behind_scenes"
    Q_AND_A = "q_and_a"
    ANNOUNCEMENT = "announcement"
    COMPILATION = "compilation"
    REMIX = "remix"
    COVER = "cover"
    ORIGINAL = "original"
    DOCUMENTARY = "documentary"
    INTERVIEW = "interview"
    PERFORMANCE = "performance"
    COMEDY = "comedy"
    DRAMA = "drama"
    HORROR = "horror"
    SCI_FI = "sci_fi"
    FANTASY = "fantasy"
    ROMANCE = "romance"
    THRILLER = "thriller"
    MYSTERY = "mystery"
    DOCUMENTARY_SERIES = "documentary_series"
    WEB_SERIES = "web_series"
    MINI_SERIES = "mini_series"


class TrendType(Enum):
    """Trend type enumeration"""
    VIRAL = "viral"
    EMERGING = "emerging"
    SEASONAL = "seasonal"
    PLATFORM_SPECIFIC = "platform_specific"
    DEMOGRAPHIC_SPECIFIC = "demographic_specific"
    GEOGRAPHIC = "geographic"
    INDUSTRY = "industry"


class RevenueStream(Enum):
    """Revenue stream enumeration"""
    ADVERTISING = "advertising"
    SPONSORSHIP = "sponsorship"
    AFFILIATE_MARKETING = "affiliate_marketing"
    MERCHANDISE = "merchandise"
    SUBSCRIPTIONS = "subscriptions"
    DONATIONS = "donations"
    LICENSING = "licensing"
    LIVE_EVENTS = "live_events"
    COURSES = "courses"
    CONSULTING = "consulting"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    PLATFORM_MONETIZATION = "platform_monetization"
    DIRECT_SALES = "direct_sales"
    CROWDFUNDING = "crowdfunding"
    PREMIUM_CONTENT = "premium_content"
    VIRTUAL_GIFTS = "virtual_gifts"
    NFTS = "nfts"
    CRYPTO_EARNINGS = "crypto_earnings"


class CollaborationType(Enum):
    """Collaboration type enumeration"""
    DUET = "duet"
    JOINT_CONTENT = "joint_content"
    GUEST_APPEARANCE = "guest_appearance"
    CROSS_PROMOTION = "cross_promotion"
    BRAND_PARTNERSHIP = "brand_partnership"
    SPONSORED_CONTENT = "sponsored_content"
    CHALLENGE_PARTICIPATION = "challenge_participation"
    REACTION_VIDEO = "reaction_video"
    INTERVIEW = "interview"
    PODCAST_GUEST = "podcast_guest"
    LIVE_STREAM = "live_stream"
    REMIX_COLLABORATION = "remix_collaboration"
    SPLIT_CONTENT = "split_content"
    TAKEOVER = "takeover"
    MENTORSHIP = "mentorship"
    COMPETITION = "competition"
    CHARITY_EVENT = "charity_event"
    EDUCATIONAL_SERIES = "educational_series"


class MatchType(Enum):
    """Collaboration match type enumeration"""
    COMPLEMENTARY_SKILLS = "complementary_skills"
    SIMILAR_AUDIENCE = "similar_audience"
    CROSS_PROMOTION = "cross_promotion"
    SKILL_EXCHANGE = "skill_exchange"
    CONTENT_COLLABORATION = "content_collaboration"
    BRAND_PARTNERSHIP = "brand_partnership"
    MENTORSHIP = "mentorship"
    JOINT_PROJECT = "joint_project"
    GUEST_APPEARANCE = "guest_appearance"
    SERIES_COLLABORATION = "series_collaboration"


@dataclass
class Engagement:
    """Engagement metrics structure"""
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    views: int = 0
    click_through_rate: float = 0.0
    engagement_rate: float = 0.0
    average_watch_time: float = 0.0
    completion_rate: float = 0.0
    replay_rate: float = 0.0
    comment_sentiment: float = 0.0


@dataclass
class ContentMetadata:
    """Content metadata structure"""
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    duration: float = 0.0
    file_size: int = 0
    format: str = ""
    resolution: str = ""
    fps: int = 0
    bitrate: int = 0
    audio_channels: int = 0
    audio_sample_rate: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    copyright_info: str = ""
    language: str = ""
    location: str = ""
    equipment_used: str = ""
    editing_software: str = ""
    color_profile: str = ""
    thumbnail_url: str = ""
    preview_url: str = ""


@dataclass
class AudienceInsight:
    """Audience insights structure"""
    total_audience: int = 0
    demographics: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    behaviors: Dict[str, Any] = field(default_factory=dict)
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    device_usage: Dict[str, float] = field(default_factory=dict)
    platform_preferences: Dict[Platform, float] = field(default_factory=dict)
    content_consumption_patterns: Dict[str, Any] = field(default_factory=dict)
    engagement_patterns: Dict[str, float] = field(default_factory=dict)
    growth_trends: Dict[str, float] = field(default_factory=dict)
    retention_metrics: Dict[str, float] = field(default_factory=dict)
    conversion_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class CreatorProfile:
    """Creator profile data structure"""
    creator_id: str
    username: str
    display_name: str
    bio: str = ""
    follower_count: int = 0
    following_count: int = 0
    total_content_count: int = 0
    platforms: List[Platform] = field(default_factory=list)
    primary_content_types: List[ContentType] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    target_demographics: Dict[str, Any] = field(default_factory=dict)
    engagement_metrics: Engagement = field(default_factory=Engagement)
    average_views: int = 0
    growth_rate: float = 0.0
    collaboration_openness: float = 0.0
    brand_safety_score: float = 0.0
    authenticity_score: float = 0.0
    influence_score: float = 0.0
    niche_authority: float = 0.0
    content_quality_score: float = 0.0
    consistency_score: float = 0.0
    trending_topics: List[str] = field(default_factory=list)
    recent_viral_content: List[str] = field(default_factory=list)
    monetization_streams: List[RevenueStream] = field(default_factory=list)
    estimated_earnings: float = 0.0
    collaboration_history: List[str] = field(default_factory=list)
    brand_partnerships: List[str] = field(default_factory=list)
    content_calendar: Dict[str, Any] = field(default_factory=dict)
    audience_insights: Dict[str, Any] = field(default_factory=dict)
    performance_trends: Dict[str, float] = field(default_factory=dict)
    content_preferences: Dict[str, Any] = field(default_factory=dict)
    optimal_posting_times: Dict[Platform, List[str]] = field(default_factory=dict)
    hashtag_performance: Dict[str, float] = field(default_factory=dict)
    cross_platform_metrics: Dict[Platform, Engagement] = field(default_factory=dict)
    content_series: List[str] = field(default_factory=list)
    equipment_setup: Dict[str, str] = field(default_factory=dict)
    editing_software: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    verification_status: bool = False
    contact_information: Dict[str, str] = field(default_factory=dict)
    manager_information: Dict[str, str] = field(default_factory=dict)
    legal_disclaimers: List[str] = field(default_factory=list)


@dataclass
class ContentRecommendation:
    """Content recommendation data structure"""
    creator_id: str
    title: str
    description: str
    content_type: ContentType
    platform: Platform
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    confidence_score: float = 0.0
    relevance_score: float = 0.0
    trending_potential: float = 0.0
    viral_probability: float = 0.0
    expected_engagement: Engagement = field(default_factory=Engagement)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    hashtags: List[str] = field(default_factory=list)
    optimal_posting_time: datetime = field(default_factory=datetime.now)
    content_pillars: List[str] = field(default_factory=list)
    collaboration_suggestions: List[str] = field(default_factory=list)
    monetization_potential: List[RevenueStream] = field(default_factory=list)
    estimated_reach: int = 0
    estimated_views: int = 0
    estimated_revenue: float = 0.0
    production_difficulty: str = "medium"
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    content_format_suggestions: List[str] = field(default_factory=list)
    music_suggestions: List[str] = field(default_factory=list)
    visual_style_suggestions: List[str] = field(default_factory=list)
    duration_recommendation: int = 60
    call_to_action_suggestions: List[str] = field(default_factory=list)
    trending_elements: List[str] = field(default_factory=list)
    seasonal_relevance: float = 0.0
    competitive_analysis: Dict[str, Any] = field(default_factory=dict)
    success_metrics: Dict[str, float] = field(default_factory=dict)
    content_safety_score: float = 1.0
    brand_alignment_score: float = 0.0
    audience_match_score: float = 0.0
    trend_alignment_score: float = 0.0
    performance_prediction: Dict[str, float] = field(default_factory=dict)
    optimization_suggestions: List[str] = field(default_factory=list)
    ab_testing_variants: List[Dict[str, Any]] = field(default_factory=list)
    cross_platform_adaptation: Dict[Platform, Dict[str, Any]] = field(default_factory=dict)
    content_series_potential: bool = False
    follow_up_content_ideas: List[str] = field(default_factory=list)
    repurposing_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    content_lifecycle: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    viewed: bool = False
    implemented: bool = False
    feedback_rating: Optional[float] = None
    performance_actual: Optional[Engagement] = None


@dataclass
class CreatorCompatibility:
    """Creator compatibility analysis"""
    creator_a_id: str
    creator_b_id: str
    compatibility_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    overall_score: float = 0.0
    content_style_similarity: float = 0.0
    audience_overlap: float = 0.0
    engagement_pattern_match: float = 0.0
    brand_alignment: float = 0.0
    collaboration_history_score: float = 0.0
    mutual_benefit_potential: float = 0.0
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    recommended_collaboration_types: List[str] = field(default_factory=list)


@dataclass
class CollaborationMatch:
    """Collaboration match data structure"""
    primary_creator_id: str
    suggested_creator_id: str
    collaboration_type: str
    match_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    match_score: float = 0.0
    compatibility: CreatorCompatibility = field(default_factory=lambda: CreatorCompatibility("", "", ""))
    collaboration_benefits: List[str] = field(default_factory=list)
    suggested_content_ideas: List[str] = field(default_factory=list)
    mutual_audience_growth_potential: float = 0.0
    cross_promotion_opportunities: List[str] = field(default_factory=list)
    revenue_sharing_suggestions: Dict[str, float] = field(default_factory=dict)
    timeline_suggestions: Dict[str, str] = field(default_factory=dict)
    resource_sharing_opportunities: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    success_probability: float = 0.0
    estimated_reach_boost: int = 0
    estimated_engagement_boost: float = 0.0
    estimated_revenue_potential: float = 0.0
    legal_considerations: List[str] = field(default_factory=list)
    contract_template_suggestions: List[str] = field(default_factory=list)
    performance_metrics_to_track: List[str] = field(default_factory=list)
    communication_channel_suggestions: List[str] = field(default_factory=list)
    content_calendar_integration: Dict[str, Any] = field(default_factory=dict)
    brand_partnership_opportunities: List[str] = field(default_factory=list)
    cross_platform_strategy: Dict[Platform, List[str]] = field(default_factory=dict)
    audience_crossover_analysis: Dict[str, Any] = field(default_factory=dict)
    trend_capitalization_opportunities: List[str] = field(default_factory=list)
    seasonal_collaboration_suggestions: List[str] = field(default_factory=list)
    long_term_partnership_potential: float = 0.0
    exclusivity_recommendations: Dict[str, bool] = field(default_factory=dict)
    content_approval_workflow: List[str] = field(default_factory=list)
    dispute_resolution_suggestions: List[str] = field(default_factory=list)
    performance_bonus_structure: Dict[str, float] = field(default_factory=dict)
    intellectual_property_guidelines: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: str = "pending"
    viewed_by_primary: bool = False
    viewed_by_suggested: bool = False
    response_from_suggested: Optional[str] = None
    negotiation_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BrandMatch:
    """Brand collaboration match"""
    creator_id: str
    brand_name: str
    brand_category: str
    match_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    match_score: float = 0.0
    alignment_factors: Dict[str, float] = field(default_factory=dict)
    collaboration_opportunities: List[str] = field(default_factory=list)
    estimated_compensation: float = 0.0
    campaign_suggestions: List[str] = field(default_factory=list)
    deliverable_recommendations: List[str] = field(default_factory=list)
    timeline_suggestions: Dict[str, str] = field(default_factory=dict)
    performance_expectations: Dict[str, float] = field(default_factory=dict)


@dataclass
class TrendInsight:
    """Trend insight data structure"""
    title: str
    description: str
    trend_type: TrendType
    trend_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platforms: List[Platform] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    growth_rate: float = 0.0
    peak_prediction: datetime = field(default_factory=datetime.now)
    decline_prediction: Optional[datetime] = None
    geographic_relevance: List[str] = field(default_factory=list)
    demographic_relevance: Dict[str, Any] = field(default_factory=dict)
    content_types_performing: List[ContentType] = field(default_factory=list)
    top_creators: List[str] = field(default_factory=list)
    engagement_patterns: Dict[str, float] = field(default_factory=dict)
    monetization_opportunities: List[RevenueStream] = field(default_factory=list)
    participation_difficulty: str = "medium"
    saturation_level: float = 0.0
    opportunity_score: float = 0.0
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    content_format_suggestions: List[str] = field(default_factory=list)
    music_associations: List[str] = field(default_factory=list)
    visual_elements: List[str] = field(default_factory=list)
    key_phrases: List[str] = field(default_factory=list)
    influencer_adoption_rate: float = 0.0
    brand_adoption_rate: float = 0.0
    media_coverage: Dict[str, Any] = field(default_factory=dict)
    social_listening_data: Dict[str, Any] = field(default_factory=dict)
    sentiment_analysis: Dict[str, float] = field(default_factory=dict)
    virality_factors: List[str] = field(default_factory=list)
    replication_ease: float = 0.0
    innovation_level: float = 0.0
    cultural_impact: float = 0.0
    commercial_impact: float = 0.0
    longevity_prediction: float = 0.0
    evolution_predictions: List[str] = field(default_factory=list)
    related_trends: List[str] = field(default_factory=list)
    counter_trends: List[str] = field(default_factory=list)
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)
    regional_variations: Dict[str, Any] = field(default_factory=dict)
    age_group_adoption: Dict[str, float] = field(default_factory=dict)
    gender_adoption_patterns: Dict[str, float] = field(default_factory=dict)
    platform_specific_variations: Dict[Platform, Dict[str, Any]] = field(default_factory=dict)
    competitive_landscape: List[str] = field(default_factory=list)
    barrier_to_entry: float = 0.0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    success_case_studies: List[Dict[str, Any]] = field(default_factory=list)
    failure_case_studies: List[Dict[str, Any]] = field(default_factory=list)
    expert_opinions: List[Dict[str, Any]] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    confidence_interval: Tuple[float, float] = (0.0, 1.0)
    last_updated: datetime = field(default_factory=datetime.now)
    next_update_scheduled: datetime = field(default_factory=datetime.now)
    trend_status: str = "active"
    verification_status: str = "pending"
    data_quality_score: float = 0.0
    prediction_accuracy_history: List[float] = field(default_factory=list)


@dataclass
class RevenueStrategy:
    """Revenue strategy recommendation"""
    creator_id: str
    strategy_name: str
    description: str
    strategy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    revenue_streams: List[RevenueStream] = field(default_factory=list)
    implementation_timeline: Dict[str, str] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    estimated_monthly_revenue: float = 0.0
    estimated_setup_cost: float = 0.0
    roi_timeline_months: int = 6
    difficulty_level: str = "medium"
    success_probability: float = 0.0
    market_saturation: float = 0.0
    competitive_advantage: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    required_audience_size: int = 1000
    required_engagement_rate: float = 0.02
    platform_requirements: List[Platform] = field(default_factory=list)
    content_type_requirements: List[ContentType] = field(default_factory=list)
    legal_requirements: List[str] = field(default_factory=list)
    tax_implications: List[str] = field(default_factory=list)
    scaling_potential: float = 0.0
    diversification_benefit: float = 0.0
    seasonal_variations: Dict[str, float] = field(default_factory=dict)
    performance_metrics: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    automation_opportunities: List[str] = field(default_factory=list)
    partnership_opportunities: List[str] = field(default_factory=list)
    technology_stack: List[str] = field(default_factory=list)
    customer_acquisition_strategy: List[str] = field(default_factory=list)
    retention_strategy: List[str] = field(default_factory=list)
    pricing_strategy: Dict[str, Any] = field(default_factory=dict)
    value_proposition: List[str] = field(default_factory=list)
    unique_selling_points: List[str] = field(default_factory=list)
    target_market_analysis: Dict[str, Any] = field(default_factory=dict)
    competitor_analysis: Dict[str, Any] = field(default_factory=dict)
    market_trends: List[str] = field(default_factory=list)
    growth_projections: Dict[str, float] = field(default_factory=dict)
    milestone_targets: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    contingency_plans: List[str] = field(default_factory=list)
    exit_strategy: List[str] = field(default_factory=list)
    success_stories: List[Dict[str, Any]] = field(default_factory=list)
    case_studies: List[Dict[str, Any]] = field(default_factory=list)
    expert_recommendations: List[str] = field(default_factory=list)
    tool_recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    status: str = "draft"
    implementation_status: str = "not_started"
    performance_tracking: Dict[str, float] = field(default_factory=dict)
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RecommendationRequest:
    """Request structure for recommendations"""
    creator_id: str
    request_type: RecommendationType
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    target_platforms: List[Platform] = field(default_factory=list)
    content_types: List[ContentType] = field(default_factory=list)
    timeline: Optional[datetime] = None
    budget_range: Optional[Tuple[float, float]] = None
    audience_targeting: Dict[str, Any] = field(default_factory=dict)
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)
    monetization_goals: List[RevenueStream] = field(default_factory=list)
    performance_goals: Dict[str, float] = field(default_factory=dict)
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    content_restrictions: List[str] = field(default_factory=list)
    geographic_targeting: List[str] = field(default_factory=list)
    language_preferences: List[str] = field(default_factory=list)
    trend_sensitivity: float = 0.5
    risk_tolerance: float = 0.5
    innovation_preference: float = 0.5
    competition_awareness: bool = True
    cross_platform_coordination: bool = False
    long_term_strategy_alignment: bool = True
    seasonal_considerations: bool = True
    brand_safety_requirements: Dict[str, Any] = field(default_factory=dict)
    compliance_requirements: List[str] = field(default_factory=list)
    privacy_settings: Dict[str, bool] = field(default_factory=dict)
    data_usage_permissions: Dict[str, bool] = field(default_factory=dict)
    notification_preferences: Dict[str, bool] = field(default_factory=dict)
    personalization_level: float = 0.8
    explanation_detail_level: str = "medium"
    recommendation_count_limit: int = 10
    diversity_requirement: float = 0.3
    novelty_requirement: float = 0.2
    relevance_threshold: float = 0.1
    confidence_threshold: float = 0.0
    performance_history_weight: float = 0.7
    trend_weight: float = 0.3
    collaboration_weight: float = 0.5
    monetization_weight: float = 0.4
    engagement_weight: float = 0.8
    growth_weight: float = 0.6
    created_at: datetime = field(default_factory=datetime.now)
    processing_priority: str = "normal"
    callback_url: Optional[str] = None
    webhook_events: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentOpportunity:
    """Content creation opportunity structure"""
    title: str
    description: str
    content_type: ContentType
    opportunity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
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


@dataclass
class RecommendationResponse:
    """Response structure for recommendations"""
    request_id: str
    creator_id: str
    response_type: RecommendationType
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
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
    """Performance metrics for recommendation system"""
    total_requests: int = 0
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


# Type aliases for convenience
RecommendationList = List[ContentRecommendation]
CollaborationList = List[CollaborationMatch]
TrendList = List[TrendInsight]
StrategyList = List[RevenueStrategy]


@dataclass
class AnalysisResult:
    """Comprehensive analysis result for content."""
    content_id: str
    content_type: ContentType
    platform: Platform
    analysis_timestamp: str
    success: bool
    confidence_score: float
    
    # Analysis features
    features: Optional['ContentFeatures'] = None
    sentiment_score: float = 0.0
    engagement_potential: float = 0.0
    quality_score: float = 0.0
    
    # Extracted metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    # Analysis details
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    
    # Performance metrics
    technical_quality: float = 0.0
    content_quality: float = 0.0
    audience_alignment: float = 0.0
    trend_relevance: float = 0.0


@dataclass
class ContentFeatures:
    """Base class for content features extracted from analysis."""
    extraction_timestamp: str
    confidence_score: float
    feature_type: str = "base"
    complexity_score: float = 0.0
    uniqueness_score: float = 0.0
    quality_score: float = 0.0
    
    # Engagement features
    engagement_indicators: Dict[str, float] = field(default_factory=dict)
    viral_potential: float = 0.0
    shareability_score: float = 0.0
    
    # Technical features
    technical_metrics: Dict[str, Any] = field(default_factory=dict)
    format_compliance: bool = True
    
    # Semantic features
    topics: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    sentiment: str = "neutral"
    emotional_tone: Dict[str, float] = field(default_factory=dict)
    
    # Contextual features
    temporal_relevance: float = 0.0
    cultural_relevance: float = 0.0
    seasonal_alignment: float = 0.0
    
    # Additional metadata
    extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    feature_vector: Dict[str, float] = field(default_factory=dict)
    raw_features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoFeatures(ContentFeatures):
    """Video-specific features extracted from content analysis."""
    
    # Video metadata
    duration: float = 0.0
    resolution: Tuple[int, int] = (1920, 1080)
    frame_rate: float = 30.0
    bitrate: int = 5000000
    codec: str = "h264"
    file_size: int = 0
    feature_type: str = field(default="video", init=False)
    
    # Visual features
    color_palette: List[str] = field(default_factory=list)
    brightness: float = 0.5
    contrast: float = 0.5
    saturation: float = 0.5
    color_temperature: str = "neutral"
    
    # Motion analysis
    motion_intensity: float = 0.0
    camera_movement: str = "static"
    scene_changes: List[float] = field(default_factory=list)
    action_level: str = "low"
    
    # Content analysis
    faces_detected: int = 0
    objects_detected: List[str] = field(default_factory=list)
    text_regions: int = 0
    scene_types: List[str] = field(default_factory=list)
    
    # Quality metrics
    sharpness: float = 0.0
    noise_level: float = 0.0
    exposure_quality: float = 0.0
    composition_score: float = 0.0
    
    # Audio presence
    has_audio: bool = False
    audio_quality: float = 0.0
    music_detected: bool = False
    speech_detected: bool = False
    
    # Engagement indicators
    thumbnail_appeal: float = 0.0
    visual_interest: float = 0.0
    production_value: float = 0.0
    
    # Technical compliance
    platform_optimized: bool = True
    mobile_friendly: bool = True
    accessibility_features: List[str] = field(default_factory=list)


@dataclass
class AudioFeatures(ContentFeatures):
    """Audio-specific features extracted from content analysis."""
    
    # Audio metadata
    duration: float = 0.0
    sample_rate: int = 44100
    bit_depth: int = 16
    channels: int = 2
    bitrate: int = 320000
    codec: str = "mp3"
    file_size: int = 0
    feature_type: str = field(default="audio", init=False)
    
    # Spectral features
    frequency_range: Tuple[float, float] = (20.0, 20000.0)
    dominant_frequencies: List[float] = field(default_factory=list)
    spectral_centroid: float = 0.0
    spectral_bandwidth: float = 0.0
    spectral_rolloff: float = 0.0
    zero_crossing_rate: float = 0.0
    
    # Rhythm and tempo
    tempo_bpm: float = 120.0
    time_signature: str = "4/4"
    rhythm_complexity: float = 0.0
    beat_strength: float = 0.0
    
    # Voice analysis
    voice_detected: bool = False
    speaker_count: int = 0
    speech_clarity: float = 0.0
    speaking_rate: float = 0.0  # words per minute
    voice_quality: float = 0.0
    
    # Music analysis
    music_detected: bool = False
    musical_key: str = "C major"
    genre_prediction: str = "unknown"
    energy_level: float = 0.0
    danceability: float = 0.0
    valence: float = 0.0  # musical positivity
    
    # Quality metrics
    signal_to_noise_ratio: float = 0.0
    dynamic_range: float = 0.0
    distortion_level: float = 0.0
    clipping_detected: bool = False
    
    # Emotional analysis
    emotion_primary: str = "neutral"
    emotion_confidence: float = 0.0
    emotional_intensity: float = 0.0
    mood_classification: str = "neutral"
    
    # Content classification
    content_type: str = "unknown"  # speech, music, ambient, etc.
    language_detected: str = "unknown"
    accent_detected: str = "unknown"
    
    # Engagement indicators
    catchiness: float = 0.0
    memorability: float = 0.0
    listening_appeal: float = 0.0
    
    # Technical compliance
    loudness_normalized: bool = True
    frequency_balanced: bool = True
    platform_optimized: bool = True


@dataclass
class TextFeatures(ContentFeatures):
    """Text-specific features extracted from content analysis."""
    
    # Basic statistics
    character_count: int = 0
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    feature_type: str = field(default="text", init=False)
    
    # Language features
    language: str = "en"
    language_confidence: float = 0.0
    writing_style: str = "neutral"
    formality_level: str = "neutral"
    
    # Readability metrics
    flesch_kincaid_grade: float = 0.0
    flesch_reading_ease: float = 0.0
    readability_level: str = "medium"
    complexity_score: float = 0.0
    
    # Sentiment and emotion
    sentiment_polarity: float = 0.0  # -1 to 1
    sentiment_subjectivity: float = 0.0  # 0 to 1
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    tone_analysis: Dict[str, float] = field(default_factory=dict)
    
    # Content analysis
    named_entities: List[Dict[str, Any]] = field(default_factory=list)
    key_phrases: List[str] = field(default_factory=list)
    topics_extracted: List[str] = field(default_factory=list)
    intent_classification: str = "informational"
    
    # SEO and keywords
    keywords: List[Dict[str, Any]] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    
    # Style analysis
    passive_voice_ratio: float = 0.0
    question_ratio: float = 0.0
    exclamation_ratio: float = 0.0
    sentence_variety: float = 0.0
    
    # Engagement indicators
    hook_strength: float = 0.0
    call_to_action_present: bool = False
    urgency_level: float = 0.0
    persuasiveness: float = 0.0
    
    # Quality metrics
    grammar_score: float = 0.0
    spelling_accuracy: float = 0.0
    coherence_score: float = 0.0
    clarity_score: float = 0.0
    
    # Platform optimization
    character_limit_compliance: bool = True
    platform_specific_features: Dict[str, Any] = field(default_factory=dict)
    trending_keywords_used: List[str] = field(default_factory=list)
    
    # Content structure
    has_introduction: bool = False
    has_conclusion: bool = False
    structure_score: float = 0.0
    flow_quality: float = 0.0


@dataclass
class CompatibilityScore:
    """Compatibility scoring result between creators."""
    creator1_id: str
    creator2_id: str
    overall_score: float
    confidence: float = 0.0
    
    # Individual component scores
    audience_overlap: float = 0.0
    content_synergy: float = 0.0
    brand_alignment: float = 0.0
    engagement_compatibility: float = 0.0
    platform_match: float = 0.0
    schedule_compatibility: float = 0.0
    experience_level: float = 0.0
    
    # Qualitative assessment
    compatibility_level: str = "unknown"  # poor, low, moderate, good, excellent
    is_compatible: bool = False
    
    # Recommendations and insights
    recommendations: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    
    # Metadata
    calculation_timestamp: str = ""
    scoring_method: str = "weighted_average"
    weights_used: Dict[str, float] = field(default_factory=dict)
    
    # Additional metrics
    potential_reach_increase: float = 0.0
    estimated_engagement_boost: float = 0.0
    collaboration_success_probability: float = 0.0


@dataclass
class ViralPrediction:
    """Viral content prediction result."""
    content_id: str
    prediction_timestamp: str
    viral_score: float
    viral_probability: float = 0.0
    is_viral_likely: bool = False
    confidence: float = 0.0
    
    # Timeline prediction
    peak_expected_hour: int = 24
    total_predicted_reach: int = 0
    viral_timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # Feature analysis
    viral_features: Dict[str, float] = field(default_factory=dict)
    key_drivers: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    
    # Insights and recommendations
    insights: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    
    # Metadata
    prediction_model: str = "advanced_viral_predictor"
    prediction_window_hours: int = 72
    features_analyzed: int = 0
