"""Audio Gamification & SEO Events - Industrial Grade Engagement & Optimization
==============================================================================

This module handles all events related to gamification, user engagement, SEO optimization,
and viral content analytics for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use, modification, or distribution of this code is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from enum import Enum

from ..core.base_event import BaseEvent


class AchievementType(Enum):
    """Achievement types for gamification"""
    UPLOAD_MILESTONE = "upload_milestone"
    STREAMING_MILESTONE = "streaming_milestone"
    COLLABORATION = "collaboration"
    QUALITY_EXCELLENCE = "quality_excellence"
    SOCIAL_ENGAGEMENT = "social_engagement"
    REVENUE_MILESTONE = "revenue_milestone"


class BadgeCategory(Enum):
    """Badge categories for user achievements"""
    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    INFLUENCER = "influencer"
    TECHNICAL = "technical"
    SOCIAL = "social"
    BUSINESS = "business"


@dataclass
class AudioSEOOptimizationEvent(BaseEvent):
    """
    Event triggered when SEO optimization is performed on audio content.
    
    Handles search engine optimization for better content discoverability.
    """
    user_id: UUID
    file_id: UUID
    optimization_id: UUID
    filename: str
    optimization_type: str  # metadata, tags, description, title
    before_metrics: Dict[str, Any]
    after_metrics: Dict[str, Any]
    seo_score: float
    target_keywords: List[str]
    optimized_fields: List[str]
    optimization_suggestions: List[str]
    search_visibility: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.seo.optimization",
            data={
                "file_id": str(self.file_id),
                "optimization_id": str(self.optimization_id),
                "optimization_type": self.optimization_type,
                "seo_score": self.seo_score,
                "keywords_count": len(self.target_keywords),
                "optimized_fields_count": len(self.optimized_fields)
            }
        )


@dataclass
class AudioMetadataEnrichmentEvent(BaseEvent):
    """
    Event triggered when audio metadata is automatically enriched.
    
    Enhances content metadata for better searchability and categorization.
    """
    user_id: UUID
    file_id: UUID
    enrichment_id: UUID
    filename: str
    enrichment_source: str  # ai_analysis, user_input, third_party_api
    original_metadata: Dict[str, Any]
    enriched_metadata: Dict[str, Any]
    enrichment_confidence: float
    fields_added: List[str]
    fields_improved: List[str]
    quality_score: float
    enrichment_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.seo.metadata_enrichment",
            data={
                "file_id": str(self.file_id),
                "enrichment_id": str(self.enrichment_id),
                "enrichment_source": self.enrichment_source,
                "enrichment_confidence": self.enrichment_confidence,
                "quality_score": self.quality_score,
                "fields_added_count": len(self.fields_added)
            }
        )


@dataclass
class AudioTagGenerationEvent(BaseEvent):
    """
    Event triggered when tags are automatically generated for audio content.
    
    Creates relevant tags for improved content discovery and organization.
    """
    user_id: UUID
    file_id: UUID
    generation_id: UUID
    filename: str
    generation_method: str  # ai_analysis, similarity_matching, crowd_sourcing
    generated_tags: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    tag_categories: Dict[str, List[str]]
    existing_tags: List[str]
    suggested_tags: List[str]
    rejected_tags: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.seo.tag_generation",
            data={
                "file_id": str(self.file_id),
                "generation_id": str(self.generation_id),
                "generation_method": self.generation_method,
                "generated_tags_count": len(self.generated_tags),
                "tag_categories_count": len(self.tag_categories),
                "suggested_tags_count": len(self.suggested_tags)
            }
        )


@dataclass
class AudioGamificationPointsEvent(BaseEvent):
    """
    Event triggered when gamification points are awarded or deducted.
    
    Manages user engagement through point-based reward systems.
    """
    user_id: UUID
    points_transaction_id: UUID
    activity_type: str
    points_change: int  # positive for award, negative for deduction
    total_points: int
    point_category: str  # upload, collaboration, quality, engagement
    achievement_triggered: bool
    milestone_reached: Optional[str] = None
    bonus_multiplier: float = 1.0
    transaction_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.gamification.points_awarded",
            data={
                "points_transaction_id": str(self.points_transaction_id),
                "activity_type": self.activity_type,
                "points_change": self.points_change,
                "total_points": self.total_points,
                "point_category": self.point_category,
                "achievement_triggered": self.achievement_triggered,
                "bonus_multiplier": self.bonus_multiplier
            }
        )


@dataclass
class AudioAchievementUnlockedEvent(BaseEvent):
    """
    Event triggered when a user unlocks a new achievement.
    
    Manages achievement system for user engagement and motivation.
    """
    user_id: UUID
    achievement_id: UUID
    achievement_name: str
    achievement_type: str
    achievement_description: str
    unlock_timestamp: datetime
    achievement_tier: str  # bronze, silver, gold, platinum
    points_awarded: int
    badge_earned: Optional[str] = None
    rarity_level: str = "common"  # common, rare, epic, legendary
    unlock_conditions: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.gamification.achievement_unlocked",
            data={
                "achievement_id": str(self.achievement_id),
                "achievement_name": self.achievement_name,
                "achievement_type": self.achievement_type,
                "achievement_tier": self.achievement_tier,
                "points_awarded": self.points_awarded,
                "rarity_level": self.rarity_level
            }
        )


@dataclass
class AudioLeaderboardUpdateEvent(BaseEvent):
    """
    Event triggered when leaderboard standings are updated.
    
    Manages competitive rankings and social comparison features.
    """
    user_id: UUID
    leaderboard_type: str  # global, genre, monthly, weekly
    previous_rank: Optional[int]
    current_rank: int
    rank_change: int
    score: float
    category: str
    timeframe: str
    total_participants: int
    percentile: float
    leaderboard_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.gamification.leaderboard_update",
            data={
                "leaderboard_type": self.leaderboard_type,
                "current_rank": self.current_rank,
                "rank_change": self.rank_change,
                "score": self.score,
                "category": self.category,
                "percentile": self.percentile,
                "total_participants": self.total_participants
            }
        )


@dataclass
class AudioBadgeEarnedEvent(BaseEvent):
    """
    Event triggered when a user earns a new badge.
    
    Manages badge system for recognizing user accomplishments.
    """
    user_id: UUID
    badge_id: UUID
    badge_name: str
    badge_category: str
    badge_description: str
    earned_timestamp: datetime
    badge_icon: str
    badge_color: str
    prerequisite_badges: List[str] = field(default_factory=list)
    badge_benefits: List[str] = field(default_factory=list)
    display_order: int = 0
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.gamification.badge_earned",
            data={
                "badge_id": str(self.badge_id),
                "badge_name": self.badge_name,
                "badge_category": self.badge_category,
                "prerequisite_count": len(self.prerequisite_badges),
                "benefits_count": len(self.badge_benefits)
            }
        )


@dataclass
class AudioChallengeCompletedEvent(BaseEvent):
    """
    Event triggered when a user completes a challenge.
    
    Manages time-limited challenges and special events.
    """
    user_id: UUID
    challenge_id: UUID
    challenge_name: str
    challenge_type: str  # daily, weekly, monthly, special_event
    completion_timestamp: datetime
    completion_time: float  # seconds taken to complete
    score_achieved: float
    perfect_completion: bool
    rewards_earned: List[Dict[str, Any]]
    leaderboard_position: Optional[int] = None
    challenge_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.gamification.challenge_completed",
            data={
                "challenge_id": str(self.challenge_id),
                "challenge_name": self.challenge_name,
                "challenge_type": self.challenge_type,
                "score_achieved": self.score_achieved,
                "perfect_completion": self.perfect_completion,
                "rewards_count": len(self.rewards_earned)
            }
        )


@dataclass
class AudioSocialShareEvent(BaseEvent):
    """
    Event triggered when audio content is shared on social platforms.
    
    Tracks social engagement and viral distribution patterns.
    """
    user_id: UUID
    file_id: UUID
    share_id: UUID
    filename: str
    platform: str  # twitter, facebook, instagram, tiktok, youtube
    share_type: str  # direct_link, embedded, preview, story
    share_timestamp: datetime
    engagement_metrics: Dict[str, Any]
    reach_estimate: int
    hashtags_used: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    viral_potential_score: float = 0.0
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.seo.social_share",
            data={
                "file_id": str(self.file_id),
                "share_id": str(self.share_id),
                "platform": self.platform,
                "share_type": self.share_type,
                "reach_estimate": self.reach_estimate,
                "hashtags_count": len(self.hashtags_used),
                "viral_potential_score": self.viral_potential_score
            }
        )


@dataclass
class AudioViralityAnalysisEvent(BaseEvent):
    """
    Event triggered when virality analysis is performed on audio content.
    
    Analyzes content potential for viral distribution and engagement.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    virality_score: float
    trend_prediction: Dict[str, Any]
    engagement_patterns: Dict[str, Any]
    social_signals: Dict[str, Any]
    content_factors: Dict[str, Any]
    timing_analysis: Dict[str, Any]
    audience_fit: Dict[str, Any]
    recommendation_actions: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.seo.virality_analysis",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "virality_score": self.virality_score,
                "recommendation_count": len(self.recommendation_actions),
                "trend_indicators": list(self.trend_prediction.keys())
            }
        )