"""
Creator Matching Configuration - Enterprise Configuration Management
Enterprise configuration for creator matching and partnership business logic

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        class Config:
            env_prefix = ""
            case_sensitive = False
            extra = "allow"
    
    def Field(**kwargs):
        return kwargs.get('default_factory', kwargs.get('default'))()
    
    def validator(field_name):
        def decorator(func):
            return func
        return decorator


class MatchingAlgorithm(str, Enum):
    """Creator matching algorithms"""
    AI_BASED = "ai_based"
    INTEREST_BASED = "interest_based"
    SKILL_BASED = "skill_based"
    LOCATION_BASED = "location_based"
    GENRE_BASED = "genre_based"
    AUDIENCE_BASED = "audience_based"
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_SIMILARITY = "content_similarity"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    NETWORK_ANALYSIS = "network_analysis"


class CollaborationType(str, Enum):
    """Types of collaboration"""
    MUSIC_COLLABORATION = "music_collaboration"
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_PROJECT = "joint_project"
    GUEST_APPEARANCE = "guest_appearance"
    REMIX_COLLABORATION = "remix_collaboration"
    BRAND_PARTNERSHIP = "brand_partnership"
    EVENT_COLLABORATION = "event_collaboration"
    EDUCATIONAL_CONTENT = "educational_content"
    CHARITY_PROJECT = "charity_project"


class CreatorTier(str, Enum):
    """Creator tier levels"""
    EMERGING = "emerging"
    RISING = "rising"
    ESTABLISHED = "established"
    PROFESSIONAL = "professional"
    CELEBRITY = "celebrity"
    INFLUENCER = "influencer"
    EXPERT = "expert"


class MatchingCriteria(str, Enum):
    """Matching criteria types"""
    GENRE_COMPATIBILITY = "genre_compatibility"
    AUDIENCE_OVERLAP = "audience_overlap"
    ENGAGEMENT_RATE = "engagement_rate"
    CONTENT_QUALITY = "content_quality"
    COLLABORATION_HISTORY = "collaboration_history"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    LANGUAGE_COMPATIBILITY = "language_compatibility"
    SCHEDULE_AVAILABILITY = "schedule_availability"
    BUDGET_COMPATIBILITY = "budget_compatibility"
    GOAL_ALIGNMENT = "goal_alignment"


class CompatibilityLevel(str, Enum):
    """Compatibility levels"""
    PERFECT_MATCH = "perfect_match"  # 95-100%
    EXCELLENT = "excellent"          # 85-94%
    GOOD = "good"                   # 70-84%
    MODERATE = "moderate"           # 55-69%
    LOW = "low"                     # 40-54%
    POOR = "poor"                   # 0-39%


@dataclass
class MatchingWeights:
    """Weights for different matching criteria"""
    genre_compatibility: float
    audience_overlap: float
    engagement_rate: float
    content_quality: float
    collaboration_history: float
    geographic_proximity: float
    language_compatibility: float
    schedule_availability: float
    budget_compatibility: float
    goal_alignment: float


@dataclass
class CreatorProfile:
    """Creator profile for matching"""
    creator_id: str
    creator_type: str
    tier: CreatorTier
    genres: List[str]
    skills: List[str]
    interests: List[str]
    location: Dict[str, Any]
    languages: List[str]
    audience_demographics: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    collaboration_preferences: Dict[str, Any]
    availability: Dict[str, Any]
    budget_range: Dict[str, float]


@dataclass
class MatchingConfiguration:
    """Matching algorithm configuration"""
    algorithm: MatchingAlgorithm
    enabled: bool
    weight: float
    accuracy_threshold: float
    min_compatibility_score: float
    max_results: int
    cache_duration_hours: int
    real_time_updates: bool
    machine_learning_enabled: bool
    feedback_learning: bool


@dataclass
class CollaborationTemplate:
    """Collaboration template configuration"""
    collaboration_type: CollaborationType
    template_name: str
    description: str
    required_skills: List[str]
    recommended_tiers: List[CreatorTier]
    duration_days: int
    budget_estimate: Dict[str, float]
    deliverables: List[str]
    success_metrics: List[str]
    contract_template: str


class CreatorMatchingSettings(BaseSettings):
    """Creator matching configuration settings"""
    
    # Matching Algorithm Configurations
    matching_algorithms: Dict[str, MatchingConfiguration] = Field(
        default_factory=lambda: {
            "ai_based": MatchingConfiguration(
                algorithm=MatchingAlgorithm.AI_BASED,
                enabled=True,
                weight=0.4,
                accuracy_threshold=0.92,
                min_compatibility_score=0.70,
                max_results=50,
                cache_duration_hours=24,
                real_time_updates=True,
                machine_learning_enabled=True,
                feedback_learning=True
            ),
            "interest_based": MatchingConfiguration(
                algorithm=MatchingAlgorithm.INTEREST_BASED,
                enabled=True,
                weight=0.25,
                accuracy_threshold=0.85,
                min_compatibility_score=0.60,
                max_results=100,
                cache_duration_hours=12,
                real_time_updates=True,
                machine_learning_enabled=False,
                feedback_learning=True
            ),
            "skill_based": MatchingConfiguration(
                algorithm=MatchingAlgorithm.SKILL_BASED,
                enabled=True,
                weight=0.2,
                accuracy_threshold=0.88,
                min_compatibility_score=0.65,
                max_results=75,
                cache_duration_hours=6,
                real_time_updates=True,
                machine_learning_enabled=True,
                feedback_learning=True
            ),
            "location_based": MatchingConfiguration(
                algorithm=MatchingAlgorithm.LOCATION_BASED,
                enabled=True,
                weight=0.1,
                accuracy_threshold=0.80,
                min_compatibility_score=0.50,
                max_results=200,
                cache_duration_hours=48,
                real_time_updates=False,
                machine_learning_enabled=False,
                feedback_learning=False
            ),
            "collaborative_filtering": MatchingConfiguration(
                algorithm=MatchingAlgorithm.COLLABORATIVE_FILTERING,
                enabled=True,
                weight=0.05,
                accuracy_threshold=0.90,
                min_compatibility_score=0.75,
                max_results=30,
                cache_duration_hours=168,  # 1 week
                real_time_updates=False,
                machine_learning_enabled=True,
                feedback_learning=True
            )
        }
    )
    
    # Matching Criteria Weights
    default_matching_weights: MatchingWeights = Field(
        default_factory=lambda: MatchingWeights(
            genre_compatibility=0.25,
            audience_overlap=0.20,
            engagement_rate=0.15,
            content_quality=0.15,
            collaboration_history=0.10,
            geographic_proximity=0.05,
            language_compatibility=0.05,
            schedule_availability=0.03,
            budget_compatibility=0.02,
            goal_alignment=0.00  # Calculated separately
        )
    )
    
    # Creator Tier Specific Weights
    tier_specific_weights: Dict[str, MatchingWeights] = Field(
        default_factory=lambda: {
            "emerging": MatchingWeights(
                genre_compatibility=0.30,
                audience_overlap=0.15,
                engagement_rate=0.20,
                content_quality=0.15,
                collaboration_history=0.05,
                geographic_proximity=0.10,
                language_compatibility=0.05,
                schedule_availability=0.00,
                budget_compatibility=0.00,
                goal_alignment=0.00
            ),
            "professional": MatchingWeights(
                genre_compatibility=0.20,
                audience_overlap=0.25,
                engagement_rate=0.15,
                content_quality=0.20,
                collaboration_history=0.15,
                geographic_proximity=0.02,
                language_compatibility=0.03,
                schedule_availability=0.00,
                budget_compatibility=0.00,
                goal_alignment=0.00
            ),
            "celebrity": MatchingWeights(
                genre_compatibility=0.15,
                audience_overlap=0.30,
                engagement_rate=0.10,
                content_quality=0.25,
                collaboration_history=0.20,
                geographic_proximity=0.00,
                language_compatibility=0.00,
                schedule_availability=0.00,
                budget_compatibility=0.00,
                goal_alignment=0.00
            )
        }
    )
    
    # Collaboration Templates
    collaboration_templates: Dict[str, CollaborationTemplate] = Field(
        default_factory=lambda: {
            "music_remix": CollaborationTemplate(
                collaboration_type=CollaborationType.REMIX_COLLABORATION,
                template_name="Music Remix Collaboration",
                description="Collaborate on remixing existing tracks",
                required_skills=["music_production", "audio_editing", "mixing"],
                recommended_tiers=[CreatorTier.RISING, CreatorTier.ESTABLISHED, CreatorTier.PROFESSIONAL],
                duration_days=14,
                budget_estimate={"min": 500.0, "max": 5000.0, "currency": "USD"},
                deliverables=["remix_track", "stems", "artwork", "promotion_plan"],
                success_metrics=["streams", "downloads", "engagement", "revenue"],
                contract_template="music_remix_contract"
            ),
            "content_collab": CollaborationTemplate(
                collaboration_type=CollaborationType.CONTENT_CREATION,
                template_name="Content Creation Collaboration",
                description="Joint content creation project",
                required_skills=["content_creation", "editing", "storytelling"],
                recommended_tiers=[CreatorTier.EMERGING, CreatorTier.RISING, CreatorTier.ESTABLISHED],
                duration_days=30,
                budget_estimate={"min": 200.0, "max": 2000.0, "currency": "USD"},
                deliverables=["video_content", "social_posts", "behind_scenes", "analytics_report"],
                success_metrics=["views", "engagement", "follower_growth", "brand_awareness"],
                contract_template="content_collaboration_contract"
            ),
            "cross_promotion": CollaborationTemplate(
                collaboration_type=CollaborationType.CROSS_PROMOTION,
                template_name="Cross-Promotion Partnership",
                description="Mutual promotion across platforms",
                required_skills=["social_media", "marketing", "community_management"],
                recommended_tiers=[CreatorTier.RISING, CreatorTier.ESTABLISHED, CreatorTier.INFLUENCER],
                duration_days=7,
                budget_estimate={"min": 0.0, "max": 500.0, "currency": "USD"},
                deliverables=["promotional_posts", "stories", "mentions", "analytics"],
                success_metrics=["reach", "impressions", "follower_exchange", "engagement"],
                contract_template="cross_promotion_agreement"
            ),
            "brand_partnership": CollaborationTemplate(
                collaboration_type=CollaborationType.BRAND_PARTNERSHIP,
                template_name="Brand Partnership Campaign",
                description="Collaborative brand campaign",
                required_skills=["brand_collaboration", "marketing", "content_creation"],
                recommended_tiers=[CreatorTier.ESTABLISHED, CreatorTier.PROFESSIONAL, CreatorTier.CELEBRITY],
                duration_days=21,
                budget_estimate={"min": 1000.0, "max": 50000.0, "currency": "USD"},
                deliverables=["campaign_content", "brand_integration", "performance_report"],
                success_metrics=["brand_awareness", "conversion", "roi", "engagement"],
                contract_template="brand_partnership_contract"
            )
        }
    )
    
    # Matching Performance Settings
    matching_performance: Dict[str, Any] = Field(
        default_factory=lambda: {
            "real_time_matching": True,
            "batch_processing": True,
            "parallel_processing": True,
            "caching_enabled": True,
            "cache_expiry_hours": 24,
            "max_concurrent_matches": 100,
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "performance_monitoring": True,
            "accuracy_tracking": True
        }
    )
    
    # AI and Machine Learning Settings
    ai_ml_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "neural_network_enabled": True,
            "deep_learning_models": True,
            "natural_language_processing": True,
            "computer_vision": True,
            "recommendation_engine": True,
            "feedback_learning": True,
            "continuous_training": True,
            "model_versioning": True,
            "a_b_testing": True,
            "personalization": True
        }
    )
    
    # Privacy and Security Settings
    privacy_security: Dict[str, Any] = Field(
        default_factory=lambda: {
            "data_encryption": True,
            "anonymized_matching": True,
            "consent_management": True,
            "gdpr_compliance": True,
            "data_minimization": True,
            "secure_communication": True,
            "audit_logging": True,
            "access_control": True,
            "data_retention_days": 365,
            "right_to_deletion": True
        }
    )
    
    # Collaboration Management
    collaboration_management: Dict[str, Any] = Field(
        default_factory=lambda: {
            "project_workspace": True,
            "communication_tools": True,
            "file_sharing": True,
            "version_control": True,
            "milestone_tracking": True,
            "contract_management": True,
            "payment_integration": True,
            "dispute_resolution": True,
            "success_tracking": True,
            "feedback_system": True
        }
    )
    
    # Analytics and Reporting
    analytics_reporting: Dict[str, Any] = Field(
        default_factory=lambda: {
            "matching_analytics": True,
            "success_metrics": True,
            "collaboration_tracking": True,
            "performance_insights": True,
            "roi_analysis": True,
            "trend_analysis": True,
            "predictive_analytics": True,
            "dashboard_reporting": True,
            "custom_reports": True,
            "data_visualization": True
        }
    )
    
    # Notification Settings
    notification_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "match_notifications": True,
            "collaboration_invites": True,
            "project_updates": True,
            "milestone_alerts": True,
            "payment_notifications": True,
            "deadline_reminders": True,
            "success_celebrations": True,
            "real_time_chat": True,
            "email_summaries": True,
            "mobile_push": True
        }
    )
    
    class Config:
        env_prefix = "CREATOR_MATCHING_"
        case_sensitive = False
        extra = "allow"
    
    def get_matching_algorithm_config(self, algorithm: str) -> Optional[MatchingConfiguration]:
        """Get matching algorithm configuration"""
        return self.matching_algorithms.get(algorithm)
    
    def get_collaboration_template(self, template_name: str) -> Optional[CollaborationTemplate]:
        """Get collaboration template"""
        return self.collaboration_templates.get(template_name)
    
    def get_matching_weights_for_tier(self, tier: str) -> MatchingWeights:
        """Get matching weights for creator tier"""
        return self.tier_specific_weights.get(tier, self.default_matching_weights)
    
    def is_algorithm_enabled(self, algorithm: str) -> bool:
        """Check if matching algorithm is enabled"""
        config = self.get_matching_algorithm_config(algorithm)
        return config.enabled if config else False
    
    def get_enabled_algorithms(self) -> List[str]:
        """Get list of enabled matching algorithms"""
        return [
            name for name, config in self.matching_algorithms.items()
            if config.enabled
        ]
    
    def calculate_compatibility_score(self, weights: MatchingWeights, scores: Dict[str, float]) -> float:
        """Calculate overall compatibility score"""
        total_score = 0.0
        total_weight = 0.0
        
        score_mapping = {
            'genre_compatibility': weights.genre_compatibility,
            'audience_overlap': weights.audience_overlap,
            'engagement_rate': weights.engagement_rate,
            'content_quality': weights.content_quality,
            'collaboration_history': weights.collaboration_history,
            'geographic_proximity': weights.geographic_proximity,
            'language_compatibility': weights.language_compatibility,
            'schedule_availability': weights.schedule_availability,
            'budget_compatibility': weights.budget_compatibility,
            'goal_alignment': weights.goal_alignment
        }
        
        for criteria, weight in score_mapping.items():
            if criteria in scores and weight > 0:
                total_score += scores[criteria] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def get_compatibility_level(self, score: float) -> CompatibilityLevel:
        """Get compatibility level from score"""
        if score >= 0.95:
            return CompatibilityLevel.PERFECT_MATCH
        elif score >= 0.85:
            return CompatibilityLevel.EXCELLENT
        elif score >= 0.70:
            return CompatibilityLevel.GOOD
        elif score >= 0.55:
            return CompatibilityLevel.MODERATE
        elif score >= 0.40:
            return CompatibilityLevel.LOW
        else:
            return CompatibilityLevel.POOR
    
    def get_recommended_templates(self, creator_tier: str, collaboration_type: str = None) -> List[str]:
        """Get recommended collaboration templates"""
        recommended = []
        tier_enum = CreatorTier(creator_tier) if creator_tier in [t.value for t in CreatorTier] else None
        
        for template_name, template in self.collaboration_templates.items():
            if collaboration_type and template.collaboration_type.value != collaboration_type:
                continue
            
            if tier_enum and tier_enum in template.recommended_tiers:
                recommended.append(template_name)
        
        return recommended
    
    def get_algorithm_accuracy_threshold(self, algorithm: str) -> float:
        """Get accuracy threshold for algorithm"""
        config = self.get_matching_algorithm_config(algorithm)
        return config.accuracy_threshold if config else 0.80
    
    def get_max_results(self, algorithm: str) -> int:
        """Get maximum results for algorithm"""
        config = self.get_matching_algorithm_config(algorithm)
        return config.max_results if config else 50
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete creator matching configuration"""
        errors = []
        
        # Validate matching algorithms
        total_weight = sum(config.weight for config in self.matching_algorithms.values() if config.enabled)
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point differences
            errors.append(f"Algorithm weights sum to {total_weight}, should sum to 1.0")
        
        for algorithm_name, config in self.matching_algorithms.items():
            if config.enabled:
                if config.weight < 0 or config.weight > 1:
                    errors.append(f"Algorithm '{algorithm_name}' has invalid weight")
                if config.accuracy_threshold < 0 or config.accuracy_threshold > 1:
                    errors.append(f"Algorithm '{algorithm_name}' has invalid accuracy threshold")
                if config.min_compatibility_score < 0 or config.min_compatibility_score > 1:
                    errors.append(f"Algorithm '{algorithm_name}' has invalid compatibility score")
                if config.max_results <= 0:
                    errors.append(f"Algorithm '{algorithm_name}' has invalid max results")
        
        # Validate matching weights
        def validate_weights(weights: MatchingWeights, context: str):
            total = (weights.genre_compatibility + weights.audience_overlap + 
                    weights.engagement_rate + weights.content_quality + 
                    weights.collaboration_history + weights.geographic_proximity + 
                    weights.language_compatibility + weights.schedule_availability + 
                    weights.budget_compatibility + weights.goal_alignment)
            if abs(total - 1.0) > 0.01:
                errors.append(f"{context} weights sum to {total}, should sum to 1.0")
        
        validate_weights(self.default_matching_weights, "Default matching")
        for tier, weights in self.tier_specific_weights.items():
            validate_weights(weights, f"Tier '{tier}' matching")
        
        # Validate collaboration templates
        for template_name, template in self.collaboration_templates.items():
            if not template.required_skills:
                errors.append(f"Template '{template_name}' has no required skills")
            if not template.recommended_tiers:
                errors.append(f"Template '{template_name}' has no recommended tiers")
            if template.duration_days <= 0:
                errors.append(f"Template '{template_name}' has invalid duration")
            if not template.deliverables:
                errors.append(f"Template '{template_name}' has no deliverables")
        
        return errors


# Global creator matching settings instance
creator_matching_settings = CreatorMatchingSettings()

__all__ = [
    "CreatorMatchingSettings",
    "creator_matching_settings",
    "MatchingAlgorithm",
    "CollaborationType",
    "CreatorTier",
    "MatchingCriteria",
    "CompatibilityLevel",
    "MatchingWeights",
    "CreatorProfile",
    "MatchingConfiguration",
    "CollaborationTemplate"
]