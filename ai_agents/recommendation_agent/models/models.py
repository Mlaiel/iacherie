"""Enterprise Data Models for Recommendation System

Ultra-advanced data models providing type-safe, performance-optimized
data structures for the recommendation system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timezone
from enum import Enum
import json
import numpy as np
import uuid


class ContentType(Enum):
    """Content type enumeration for multi-modal support"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PLAYLIST = "playlist"
    ALBUM = "album"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    STORY = "story"
    POST = "post"


class InteractionType(Enum):
    """User interaction type enumeration"""    PLAY = "play"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    FOLLOW = "follow"
    SAVE = "save"
    SKIP = "skip"
    DOWNLOAD = "download"
    PURCHASE = "purchase"
    SUBSCRIBE = "subscribe"
    VIEW = "view"
    REPORT = "report"
    BLOCK = "block"


class RecommendationType(Enum):
    """Recommendation algorithm type enumeration"""    COLLABORATIVE = "collaborative"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    TRENDING = "trending"
    SIMILAR_USERS = "similar_users"
    CATEGORY_BASED = "category_based"
    TEMPORAL = "temporal"
    GEOGRAPHIC = "geographic"
    SOCIAL = "social"
    REVENUE_OPTIMIZED = "revenue_optimized"


class CreatorTier(Enum):
    """Creator tier classification"""    EMERGING = "emerging"
    ESTABLISHED = "established"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    INFLUENCER = "influencer"
    CELEBRITY = "celebrity"


class MonetizationStrategy(Enum):
    """Revenue generation strategies"""    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    PAY_PER_VIEW = "pay_per_view"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"
    SPONSORSHIP = "sponsorship"
    DONATIONS = "donations"
    PREMIUM_CONTENT = "premium_content"


@dataclass
class UserProfile:
    """Comprehensive user profile for personalization"""    user_id: str
    username: str
    email: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    demographics: Dict[str, Any] = field(default_factory=dict)
    behavior_patterns: Dict[str, float] = field(default_factory=dict)
    interaction_history: List[str] = field(default_factory=list)
    content_preferences: Dict[ContentType, float] = field(default_factory=dict)
    creator_affinities: Dict[str, float] = field(default_factory=dict)
    geographical_data: Optional[Dict[str, Any]] = None
    language_preferences: List[str] = field(default_factory=lambda: ["en"])
    subscription_tier: str = "free"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    privacy_settings: Dict[str, bool] = field(default_factory=dict)
    monetization_preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_vector(self) -> np.ndarray:
        """Convert user profile to numerical vector for ML processing"""        vector_components = []
        
        # Content preferences
        for content_type in ContentType:
            vector_components.append(self.content_preferences.get(content_type, 0.0))
        
        # Behavior patterns
        for pattern in ['engagement_rate', 'session_duration', 'skip_rate', 'completion_rate']:
            vector_components.append(self.behavior_patterns.get(pattern, 0.0))
        
        return np.array(vector_components)


@dataclass
class CreatorProfile:
    """Comprehensive creator profile and analytics"""    creator_id: str
    username: str
    display_name: str
    creator_type: str
    tier: CreatorTier
    specialties: List[str] = field(default_factory=list)
    content_categories: List[str] = field(default_factory=list)
    follower_count: int = 0
    total_content_count: int = 0
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    revenue_metrics: Dict[str, float] = field(default_factory=dict)
    collaboration_score: float = 0.0
    quality_score: float = 0.0
    trending_score: float = 0.0
    geographical_reach: Dict[str, float] = field(default_factory=dict)
    language_support: List[str] = field(default_factory=list)
    monetization_enabled: bool = True
    verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def calculate_influence_score(self) -> float:
        """Calculate overall influence score based on metrics"""        base_score = min(self.follower_count / 1000.0, 100.0)  # Cap at 100
        engagement_boost = self.engagement_metrics.get('avg_engagement_rate', 0.0) * 50
        quality_boost = self.quality_score * 30
        collaboration_boost = self.collaboration_score * 20
        
        return min(base_score + engagement_boost + quality_boost + collaboration_boost, 1000.0)


@dataclass
class ContentItem:
    """Comprehensive content item representation"""    content_id: str
    title: str
    description: str
    creator_id: str
    content_type: ContentType
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    duration: Optional[float] = None  # in seconds
    file_size: Optional[int] = None  # in bytes
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    engagement_metrics: Dict[str, int] = field(default_factory=dict)
    revenue_data: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    protection_level: str = "standard"
    copyright_info: Dict[str, Any] = field(default_factory=dict)
    collaboration_opportunities: List[str] = field(default_factory=list)
    seo_keywords: List[str] = field(default_factory=list)
    trending_score: float = 0.0
    recommendation_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    
    def calculate_relevance_score(self, user_profile: UserProfile) -> float:
        """Calculate content relevance score for specific user"""        score = 0.0
        
        # Content type preference
        content_pref = user_profile.content_preferences.get(self.content_type, 0.0)
        score += content_pref * 0.3
        
        # Category matching
        user_categories = set(user_profile.preferences.get('categories', []))
        content_categories = set(self.categories)
        category_match = len(user_categories.intersection(content_categories)) / max(len(user_categories), 1)
        score += category_match * 0.25
        
        # Creator affinity
        creator_affinity = user_profile.creator_affinities.get(self.creator_id, 0.0)
        score += creator_affinity * 0.25
        
        # Quality and engagement
        quality_score = self.quality_metrics.get('overall_quality', 0.0)
        engagement_score = min(self.engagement_metrics.get('total_engagement', 0) / 1000.0, 1.0)
        score += (quality_score * 0.1) + (engagement_score * 0.1)
        
        return min(score, 1.0)


@dataclass
class InteractionEvent:
    """User interaction event tracking"""    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    content_id: str = ""
    creator_id: str = ""
    interaction_type: InteractionType = InteractionType.VIEW
    duration: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: Dict[str, Any] = field(default_factory=dict)
    device_info: Dict[str, str] = field(default_factory=dict)
    location_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    revenue_impact: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert interaction event to dictionary for storage"""        return {
            'event_id': self.event_id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'creator_id': self.creator_id,
            'interaction_type': self.interaction_type.value,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'device_info': self.device_info,
            'location_data': self.location_data,
            'session_id': self.session_id,
            'revenue_impact': self.revenue_impact
        }


@dataclass
class RecommendationContext:
    """Context information for generating recommendations"""    session_id: str
    device_type: str
    location: Optional[Dict[str, Any]] = None
    time_of_day: str = ""
    day_of_week: str = ""
    previous_interactions: List[InteractionEvent] = field(default_factory=list)
    current_mood: Optional[str] = None
    social_context: Dict[str, Any] = field(default_factory=dict)
    preference_filters: Dict[str, Any] = field(default_factory=dict)
    collaboration_intent: bool = False
    monetization_focus: bool = False
    content_discovery_mode: str = "balanced"  # conservative, balanced, exploratory
    
    def get_contextual_weight(self, content_type: ContentType) -> float:
        """Get contextual weight for content type based on current context"""        weights = {
            'morning': {ContentType.PODCAST: 1.2, ContentType.AUDIO: 1.1},
            'afternoon': {ContentType.VIDEO: 1.1, ContentType.IMAGE: 1.2},
            'evening': {ContentType.AUDIO: 1.3, ContentType.VIDEO: 1.2},
            'night': {ContentType.AUDIO: 1.4, ContentType.PODCAST: 1.3}
        }
        
        time_weights = weights.get(self.time_of_day, {})
        return time_weights.get(content_type, 1.0)


@dataclass
class CollaborationRequest:
    """Collaboration opportunity representation"""    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    initiator_id: str = ""
    target_creator_id: str = ""
    collaboration_type: str = ""
    project_description: str = ""
    budget_range: Optional[Dict[str, float]] = None
    timeline: Optional[Dict[str, datetime]] = None
    requirements: List[str] = field(default_factory=list)
    skills_needed: List[str] = field(default_factory=list)
    revenue_split: Optional[Dict[str, float]] = None
    status: str = "pending"
    match_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    def calculate_compatibility(self, creator: CreatorProfile) -> float:
        """Calculate collaboration compatibility score"""        score = 0.0
        
        # Skills matching
        creator_skills = set(creator.specialties)
        needed_skills = set(self.skills_needed)
        skill_match = len(creator_skills.intersection(needed_skills)) / max(len(needed_skills), 1)
        score += skill_match * 0.4
        
        # Creator tier compatibility
        tier_scores = {
            CreatorTier.EMERGING: 0.6,
            CreatorTier.ESTABLISHED: 0.8,
            CreatorTier.PREMIUM: 0.9,
            CreatorTier.ENTERPRISE: 1.0
        }
        score += tier_scores.get(creator.tier, 0.5) * 0.3
        
        # Collaboration history
        score += creator.collaboration_score * 0.3
        
        return min(score, 1.0)


@dataclass
class TrendData:
    """Trending content and creator analytics"""    trend_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: Optional[str] = None
    creator_id: Optional[str] = None
    trend_type: str = ""  # content, creator, category, hashtag
    trend_score: float = 0.0
    velocity: float = 0.0  # rate of trend growth
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    demographic_breakdown: Dict[str, float] = field(default_factory=dict)
    engagement_patterns: Dict[str, int] = field(default_factory=dict)
    duration_prediction: Optional[float] = None  # predicted trend lifespan
    monetization_potential: float = 0.0
    competition_level: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    def is_trending_now(self) -> bool:
        """Check if trend is currently active"""        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False
        return self.trend_score > 0.7 and self.velocity > 0.0


@dataclass
class RevenueMetrics:
    """Revenue and monetization analytics"""    content_id: str
    creator_id: str
    total_revenue: float = 0.0
    revenue_streams: Dict[str, float] = field(default_factory=dict)
    conversion_rates: Dict[str, float] = field(default_factory=dict)
    audience_value: float = 0.0
    cost_per_engagement: float = 0.0
    return_on_investment: float = 0.0
    projected_revenue: Dict[str, float] = field(default_factory=dict)
    optimization_suggestions: List[str] = field(default_factory=list)
    performance_indicators: Dict[str, float] = field(default_factory=dict)
    period_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def calculate_efficiency_score(self) -> float:
        """Calculate revenue efficiency score"""        if self.audience_value == 0:
            return 0.0
        
        efficiency = self.total_revenue / self.audience_value
        return min(efficiency * 100, 1000.0)  # Cap at 1000%


@dataclass
class SimilarityScore:
    """Similarity calculation result between entities"""    entity_a_id: str
    entity_b_id: str
    similarity_type: str  # user-user, content-content, creator-creator
    score: float
    contributing_factors: Dict[str, float] = field(default_factory=dict)
    confidence: float = 1.0
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_significant(self, threshold: float = 0.7) -> bool:
        """Check if similarity score is significant"""        return self.score >= threshold and self.confidence >= 0.8


@dataclass
class PersonalizationVector:
    """User personalization vector for ML models"""    user_id: str
    vector_data: np.ndarray
    feature_names: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    model_version: str = "1.0"
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    
    def update_vector(self, new_interactions: List[InteractionEvent]) -> None:
        """Update personalization vector with new interaction data"""        # This would contain the actual ML logic for updating vectors
        # Implementation would depend on the specific ML framework used
        self.last_updated = datetime.now(timezone.utc)
    
    def get_similarity(self, other_vector: 'PersonalizationVector') -> float:
        """Calculate cosine similarity with another personalization vector"""        if len(self.vector_data) != len(other_vector.vector_data):
            return 0.0
        
        dot_product = np.dot(self.vector_data, other_vector.vector_data)
        norm_a = np.linalg.norm(self.vector_data)
        norm_b = np.linalg.norm(other_vector.vector_data)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)


@dataclass
class RecommendationResult:
    """Final recommendation result with metadata"""    recommendations: List[ContentItem]
    algorithm_used: str
    confidence_score: float
    diversity_score: float
    novelty_score: float
    explanation: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    a_b_test_variant: Optional[str] = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def get_top_recommendations(self, count: int) -> List[ContentItem]:
        """Get top N recommendations sorted by score"""        sorted_recs = sorted(
            self.recommendations, 
            key=lambda x: x.recommendation_score, 
            reverse=True
        )
        return sorted_recs[:count]
