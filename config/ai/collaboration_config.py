"""Collaboration AI Configuration for IA-Influencer Agent Platform
===============================================================

Professional collaboration matching and management AI configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass
import os


class CollaborationType(str, Enum):
    """
Types of collaborations supported."""

    
    MUSIC_COLLABORATION = "music_collaboration"
    VIDEO_COLLABORATION = "video_collaboration"
    PODCAST_COLLABORATION = "podcast_collaboration"
    BRAND_PARTNERSHIP = "brand_partnership"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_CONTENT = "joint_content"
    REMIX_COLLABORATION = "remix_collaboration"
    LIVE_PERFORMANCE = "live_performance"
    EDUCATIONAL_CONTENT = "educational_content"
    CHARITY_COLLABORATION = "charity_collaboration"


class CollaborationStatus(str, Enum):
    """Collaboration request statuses."""

    
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class MatchingCriteria(str, Enum):
    """Criteria for collaboration matching."""

    
    GENRE_SIMILARITY = "genre_similarity"
    AUDIENCE_OVERLAP = "audience_overlap"
    ENGAGEMENT_COMPATIBILITY = "engagement_compatibility"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    CAREER_STAGE = "career_stage"
    BRAND_ALIGNMENT = "brand_alignment"
    CONTENT_QUALITY = "content_quality"
    COLLABORATION_HISTORY = "collaboration_history"


class CreatorTier(str, Enum):
    """Creator tier classifications."""

    
    EMERGING = "emerging"  # < 10K followers
    RISING = "rising"      # 10K - 100K followers
    ESTABLISHED = "established"  # 100K - 1M followers
    INFLUENTIAL = "influential"  # 1M - 10M followers
    CELEBRITY = "celebrity"      # > 10M followers


@dataclass
class CollaborationMatch:
    """Collaboration match configuration."""
    
    match_id: str
    creator_1_id: str
    creator_2_id: str
    collaboration_type: CollaborationType
    match_score: float
    compatibility_scores: Dict[str, float]
    estimated_reach: int
    estimated_engagement: float
    revenue_potential: float
    suggested_terms: Dict[str, Any]
    risk_assessment: Dict[str, float]
    timeline_estimate_days: int
    confidence_level: float


class CollaborationConfig(BaseSettings):
    """
    Professional Collaboration AI Configuration.
    
    Manages AI-powered collaboration matching, recommendation,
    and project management for content creators and influencers.
    """
    
    # Core Collaboration Configuration
    COLLABORATION_STORAGE_PATH: str = "/data/collaborations"
    MATCHING_ALGORITHM: str = "advanced_neural_matching"
    MIN_MATCH_SCORE: float = 0.75
    MAX_COLLABORATION_SUGGESTIONS: int = 20
    COLLABORATION_REFRESH_INTERVAL: int = 24  # hours
    
    # Matching Criteria Weights
    GENRE_SIMILARITY_WEIGHT: float = 0.25
    AUDIENCE_OVERLAP_WEIGHT: float = 0.20
    ENGAGEMENT_COMPATIBILITY_WEIGHT: float = 0.20
    GEOGRAPHIC_PROXIMITY_WEIGHT: float = 0.10
    CAREER_STAGE_WEIGHT: float = 0.15
    BRAND_ALIGNMENT_WEIGHT: float = 0.10
    
    # Creator Tier Configuration
    EMERGING_FOLLOWER_THRESHOLD: int = 10000
    RISING_FOLLOWER_THRESHOLD: int = 100000
    ESTABLISHED_FOLLOWER_THRESHOLD: int = 1000000
    INFLUENTIAL_FOLLOWER_THRESHOLD: int = 10000000
    
    # Collaboration Types Configuration
    MUSIC_COLLABORATION_ENABLED: bool = True
    VIDEO_COLLABORATION_ENABLED: bool = True
    PODCAST_COLLABORATION_ENABLED: bool = True
    BRAND_PARTNERSHIP_ENABLED: bool = True
    CROSS_PROMOTION_ENABLED: bool = True
    JOINT_CONTENT_ENABLED: bool = True
    REMIX_COLLABORATION_ENABLED: bool = True
    LIVE_PERFORMANCE_ENABLED: bool = True
    EDUCATIONAL_CONTENT_ENABLED: bool = True
    CHARITY_COLLABORATION_ENABLED: bool = True
    
    # AI Models Configuration
    CREATOR_MATCHING_MODEL: str = "custom/creator-matcher-v3"
    COMPATIBILITY_SCORING_MODEL: str = "custom/compatibility-scorer-v2"
    SUCCESS_PREDICTION_MODEL: str = "custom/success-predictor-v1"
    CONTENT_SIMILARITY_MODEL: str = "transformers/content-similarity-bert"
    AUDIENCE_ANALYSIS_MODEL: str = "custom/audience-analyzer-v2"
    
    # Matching Parameters
    MAX_GEOGRAPHIC_DISTANCE_KM: int = 1000  # for location-based matching
    MIN_AUDIENCE_OVERLAP_PERCENTAGE: float = 0.05  # 5% minimum overlap
    MAX_FOLLOWER_RATIO_DIFFERENCE: float = 10.0  # max 10:1 ratio
    MIN_ENGAGEMENT_RATE: float = 0.01  # 1% minimum engagement
    
    # Content Analysis
    ANALYZE_CONTENT_SIMILARITY: bool = True
    ANALYZE_POSTING_PATTERNS: bool = True
    ANALYZE_AUDIENCE_DEMOGRAPHICS: bool = True
    ANALYZE_BRAND_SAFETY: bool = True
    ANALYZE_COLLABORATION_HISTORY: bool = True
    
    # Recommendation Engine
    PERSONALIZED_RECOMMENDATIONS: bool = True
    TRENDING_COLLABORATION_TRACKING: bool = True
    SEASONAL_COLLABORATION_SUGGESTIONS: bool = True
    CROSS_GENRE_RECOMMENDATIONS: bool = True
    EMERGING_TALENT_DISCOVERY: bool = True
    
    # Performance Metrics
    TRACK_COLLABORATION_SUCCESS: bool = True
    MEASURE_REACH_AMPLIFICATION: bool = True
    MEASURE_ENGAGEMENT_BOOST: bool = True
    MEASURE_FOLLOWER_GROWTH: bool = True
    MEASURE_REVENUE_IMPACT: bool = True
    
    # Communication and Workflow
    AUTOMATED_INTRODUCTIONS: bool = True
    COLLABORATION_TEMPLATES: bool = True
    CONTRACT_GENERATION: bool = True
    MILESTONE_TRACKING: bool = True
    PAYMENT_SPLITTING: bool = True
    
    # Platform Integration
    SPOTIFY_COLLABORATION_SYNC: bool = True
    YOUTUBE_COLLABORATION_SYNC: bool = True
    TIKTOK_COLLABORATION_SYNC: bool = True
    INSTAGRAM_COLLABORATION_SYNC: bool = True
    TWITTER_COLLABORATION_SYNC: bool = True
    
    # Quality Control
    CREATOR_VERIFICATION_REQUIRED: bool = True
    CONTENT_QUALITY_THRESHOLD: float = 0.7
    BRAND_SAFETY_THRESHOLD: float = 0.8
    SPAM_DETECTION_ENABLED: bool = True
    FAKE_ACCOUNT_DETECTION: bool = True
    
    # Revenue Sharing
    DEFAULT_REVENUE_SPLIT: float = 0.5  # 50/50 split
    ALLOW_CUSTOM_REVENUE_SPLITS: bool = True
    PLATFORM_COMMISSION_RATE: float = 0.1  # 10% platform fee
    HANDLE_TAX_IMPLICATIONS: bool = True
    
    # Legal and Compliance
    CONTRACT_TEMPLATES_ENABLED: bool = True
    INTELLECTUAL_PROPERTY_PROTECTION: bool = True
    DISPUTE_RESOLUTION_SYSTEM: bool = True
    TERMS_AGREEMENT_REQUIRED: bool = True
    
    # Analytics and Reporting
    COLLABORATION_ANALYTICS_ENABLED: bool = True
    SUCCESS_RATE_TRACKING: bool = True
    ROI_CALCULATION_ENABLED: bool = True
    PERFORMANCE_BENCHMARKING: bool = True
    TREND_ANALYSIS_ENABLED: bool = True
    
    # Notification System
    MATCH_NOTIFICATIONS: bool = True
    REQUEST_NOTIFICATIONS: bool = True
    MILESTONE_NOTIFICATIONS: bool = True
    COMPLETION_NOTIFICATIONS: bool = True
    PAYMENT_NOTIFICATIONS: bool = True
    
    # Security and Privacy
    CREATOR_DATA_ENCRYPTION: bool = True
    PRIVATE_COLLABORATION_MODE: bool = True
    NDA_SUPPORT: bool = True
    DATA_SHARING_CONTROLS: bool = True
    
    # Advanced Features
    AI_NEGOTIATION_ASSISTANT: bool = True
    PREDICTIVE_SUCCESS_SCORING: bool = True
    DYNAMIC_PRICING_SUGGESTIONS: bool = True
    COLLABORATION_OPTIMIZATION: bool = True
    MULTI_PARTY_COLLABORATIONS: bool = True
    
    @validator("MIN_MATCH_SCORE")
    def validate_min_match_score(cls, v):
        if v < 0.5 or v > 1.0:
            raise ValueError("Minimum match score must be between 0.5 and 1.0")
        return v
    
    @validator("MAX_COLLABORATION_SUGGESTIONS")
    def validate_max_suggestions(cls, v):
        if v <= 0 or v > 100:
            raise ValueError("Max collaboration suggestions must be between 1 and 100")
        return v
    
    @validator("DEFAULT_REVENUE_SPLIT")
    def validate_revenue_split(cls, v):
        if v < 0.1 or v > 0.9:
            raise ValueError("Default revenue split must be between 10% and 90%")
        return v
    
    def get_collaboration_match(
        self,
        creator_1_data: Dict[str, Any],
        creator_2_data: Dict[str, Any],
        collaboration_type: CollaborationType
    ) -> CollaborationMatch:
        """Generate collaboration match recommendation."""
        
        # Calculate compatibility scores
        compatibility_scores = {
            "genre_similarity": self._calculate_genre_similarity(creator_1_data, creator_2_data),
            "audience_overlap": self._calculate_audience_overlap(creator_1_data, creator_2_data),
            "engagement_compatibility": self._calculate_engagement_compatibility(creator_1_data, creator_2_data),
            "geographic_proximity": self._calculate_geographic_proximity(creator_1_data, creator_2_data),
            "career_stage": self._calculate_career_stage_compatibility(creator_1_data, creator_2_data),
            "brand_alignment": self._calculate_brand_alignment(creator_1_data, creator_2_data)
        }
        
        # Calculate overall match score
        match_score = (
            compatibility_scores["genre_similarity"] * self.GENRE_SIMILARITY_WEIGHT +
            compatibility_scores["audience_overlap"] * self.AUDIENCE_OVERLAP_WEIGHT +
            compatibility_scores["engagement_compatibility"] * self.ENGAGEMENT_COMPATIBILITY_WEIGHT +
            compatibility_scores["geographic_proximity"] * self.GEOGRAPHIC_PROXIMITY_WEIGHT +
            compatibility_scores["career_stage"] * self.CAREER_STAGE_WEIGHT +
            compatibility_scores["brand_alignment"] * self.BRAND_ALIGNMENT_WEIGHT
        )
        
        # Estimate metrics
        estimated_reach = creator_1_data.get("followers", 0) + creator_2_data.get("followers", 0)
        estimated_engagement = (
            creator_1_data.get("engagement_rate", 0) + 
            creator_2_data.get("engagement_rate", 0)
        ) / 2
        
        # Revenue potential calculation
        revenue_potential = self._calculate_revenue_potential(
            estimated_reach, estimated_engagement, collaboration_type
        )
        
        return CollaborationMatch(
            match_id=f"match_{creator_1_data['id']}_{creator_2_data['id']}",
            creator_1_id=creator_1_data["id"],
            creator_2_id=creator_2_data["id"],
            collaboration_type=collaboration_type,
            match_score=match_score,
            compatibility_scores=compatibility_scores,
            estimated_reach=estimated_reach,
            estimated_engagement=estimated_engagement,
            revenue_potential=revenue_potential,
            suggested_terms=self._generate_suggested_terms(
                creator_1_data, creator_2_data, collaboration_type
            ),
            risk_assessment=self._assess_collaboration_risks(creator_1_data, creator_2_data),
            timeline_estimate_days=self._estimate_timeline(collaboration_type),
            confidence_level=match_score * 0.9  # Slightly conservative
        )
    
    def _calculate_genre_similarity(self, creator_1: Dict, creator_2: Dict) -> float:
        """Calculate genre/content similarity score."""
        # Simplified implementation - would use ML model in production
        genres_1 = set(creator_1.get("genres", []))
        genres_2 = set(creator_2.get("genres", []))
        
        if not genres_1 or not genres_2:
            return 0.5  # neutral score
        
        intersection = len(genres_1.intersection(genres_2))
        union = len(genres_1.union(genres_2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_audience_overlap(self, creator_1: Dict, creator_2: Dict) -> float:
        """Calculate audience overlap score."""
        # Simplified implementation - would analyze actual audience data
        demographics_1 = creator_1.get("audience_demographics", {})
        demographics_2 = creator_2.get("audience_demographics", {})
        
        # Mock calculation based on age groups, interests, etc.
        overlap_score = 0.7  # Would be calculated from real data
        return min(overlap_score, 1.0)
    
    def _calculate_engagement_compatibility(self, creator_1: Dict, creator_2: Dict) -> float:
        """Calculate engagement rate compatibility."""
        engagement_1 = creator_1.get("engagement_rate", 0)
        engagement_2 = creator_2.get("engagement_rate", 0)
        
        if engagement_1 == 0 or engagement_2 == 0:
            return 0.0
        
        # Calculate similarity (closer engagement rates = higher compatibility)
        ratio = min(engagement_1, engagement_2) / max(engagement_1, engagement_2)
        return ratio
    
    def _calculate_geographic_proximity(self, creator_1: Dict, creator_2: Dict) -> float:
        """Calculate geographic proximity score."""
        # Simplified implementation - would use actual coordinates
        location_1 = creator_1.get("location", {})
        location_2 = creator_2.get("location", {})
        
        if not location_1 or not location_2:
            return 0.5  # neutral score for unknown locations
        
        # Mock distance calculation
        distance_km = 500  # Would calculate actual distance
        max_distance = self.MAX_GEOGRAPHIC_DISTANCE_KM
        
        return max(0, 1 - (distance_km / max_distance))
    
    def _calculate_career_stage_compatibility(self, creator_1: Dict, creator_2: Dict) -> float:
        """Calculate career stage compatibility."""
        followers_1 = creator_1.get("followers", 0)
        followers_2 = creator_2.get("followers", 0)
        
        tier_1 = self._get_creator_tier(followers_1)
        tier_2 = self._get_creator_tier(followers_2)
        
        # Same tier = 1.0, adjacent tiers = 0.7, distant tiers = lower score
        tier_values = {
            CreatorTier.EMERGING: 1,
            CreatorTier.RISING: 2,
            CreatorTier.ESTABLISHED: 3,
            CreatorTier.INFLUENTIAL: 4,
            CreatorTier.CELEBRITY: 5
        }
        
        tier_diff = abs(tier_values[tier_1] - tier_values[tier_2])
        
        if tier_diff == 0:
            return 1.0
        elif tier_diff == 1:
            return 0.8
        elif tier_diff == 2:
            return 0.6
        else:
            return 0.3
    
    def _calculate_brand_alignment(self, creator_1: Dict, creator_2: Dict) -> float:
        """Calculate brand alignment score."""
        # Simplified implementation - would analyze brand values, content style, etc.
        brand_score = 0.75  # Mock score
        return brand_score
    
    def _calculate_revenue_potential(
        self, 
        estimated_reach: int, 
        estimated_engagement: float, 
        collaboration_type: CollaborationType
    ) -> float:
        """
Calculate estimated revenue potential."""
        
        # Base calculation: reach * engagement * type multiplier
        type_multipliers = {
            CollaborationType.MUSIC_COLLABORATION: 1.2,
            CollaborationType.VIDEO_COLLABORATION: 1.0,
            CollaborationType.BRAND_PARTNERSHIP: 2.0,
            CollaborationType.LIVE_PERFORMANCE: 1.5,
            CollaborationType.CROSS_PROMOTION: 0.8
        }
        
        multiplier = type_multipliers.get(collaboration_type, 1.0)
        
        # Simplified revenue calculation
        base_revenue = (estimated_reach * estimated_engagement * 0.01) * multiplier
        
        return min(base_revenue, 100000.0)  # Cap at reasonable amount
    
    def _generate_suggested_terms(
        self, 
        creator_1: Dict, 
        creator_2: Dict, 
        collaboration_type: CollaborationType
    ) -> Dict[str, Any]:
        """
Generate suggested collaboration terms."""
        
        return {
            "revenue_split": self.DEFAULT_REVENUE_SPLIT,
            "content_ownership": "shared",
            "exclusivity_period_days": 30,
            "promotion_requirements": {
                "minimum_posts": 3,
                "cross_platform_promotion": True,
                "hashtag_requirements": ["#collaboration", "#partnership"]
            },
            "deliverables": self._get_collaboration_deliverables(collaboration_type),
            "timeline_days": self._estimate_timeline(collaboration_type),
            "payment_terms": "upon_completion"
        }
    
    def _assess_collaboration_risks(self, creator_1: Dict, creator_2: Dict) -> Dict[str, float]:
        """Assess potential collaboration risks."""
        
        return {
            "brand_safety_risk": 0.1,  # Low risk
            "content_quality_risk": 0.15,
            "timeline_risk": 0.2,
            "engagement_risk": 0.1,
            "revenue_risk": 0.25,
            "reputation_risk": 0.05
        }
    
    def _estimate_timeline(self, collaboration_type: CollaborationType) -> int:
        """Estimate collaboration timeline in days."""
        
        timelines = {
            CollaborationType.MUSIC_COLLABORATION: 30,
            CollaborationType.VIDEO_COLLABORATION: 21,
            CollaborationType.PODCAST_COLLABORATION: 14,
            CollaborationType.BRAND_PARTNERSHIP: 60,
            CollaborationType.CROSS_PROMOTION: 7,
            CollaborationType.LIVE_PERFORMANCE: 45
        }
        
        return timelines.get(collaboration_type, 21)
    
    def _get_collaboration_deliverables(self, collaboration_type: CollaborationType) -> List[str]:
        """
Get expected deliverables for collaboration type."""
        
        deliverables = {
            CollaborationType.MUSIC_COLLABORATION: [
                "Co-written song/track",
                "Joint performance/recording",
                "Social media promotion",
                "Cross-platform content"
            ],
            CollaborationType.VIDEO_COLLABORATION: [
                "Collaborative video content",
                "Individual promotion videos",
                "Social media teasers",
                "Behind-the-scenes content"
            ],
            CollaborationType.BRAND_PARTNERSHIP: [
                "Sponsored content",
                "Product reviews/demos",
                "Brand integration",
                "Performance metrics report"
            ]
        }
        
        return deliverables.get(collaboration_type, ["Joint content creation"])
    
    def _get_creator_tier(self, followers: int) -> CreatorTier:
        """Determine creator tier based on follower count."""
        
        if followers >= self.INFLUENTIAL_FOLLOWER_THRESHOLD:
            return CreatorTier.CELEBRITY
        elif followers >= self.ESTABLISHED_FOLLOWER_THRESHOLD:
            return CreatorTier.INFLUENTIAL
        elif followers >= self.RISING_FOLLOWER_THRESHOLD:
            return CreatorTier.ESTABLISHED
        elif followers >= self.EMERGING_FOLLOWER_THRESHOLD:
            return CreatorTier.RISING
        else:
            return CreatorTier.EMERGING
    
    class Config:
        env_prefix = "COLLABORATION_"
        case_sensitive = True


# Global instance for easy import
collaboration_config = CollaborationConfig()
