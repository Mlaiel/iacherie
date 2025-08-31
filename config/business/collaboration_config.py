"""Collaboration Configuration Module
==================================

Manages creator collaboration matching, partnership workflows, and revenue sharing.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""
from enum import Enum
from typing import Dict, List, Optional, Set, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid


class CollaborationType(str, Enum):
    """Types of collaborations supported."""
    MUSIC_COLLAB = "music_collaboration"
    VIDEO_COLLAB = "video_collaboration"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_PROJECT = "joint_project"
    REMIX_PERMISSION = "remix_permission"
    COVER_LICENSE = "cover_license"
    SAMPLE_USAGE = "sample_usage"
    FEATURE_REQUEST = "feature_request"
    BRAND_PARTNERSHIP = "brand_partnership"
    TOUR_COLLABORATION = "tour_collaboration"
    MERCHANDISE_COLLAB = "merchandise_collaboration"
    CONTENT_SERIES = "content_series"


class CollaborationStatus(str, Enum):
    """Collaboration request and project status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    DISPUTED = "disputed"
    ARCHIVED = "archived"


class MatchingCriteria(str, Enum):
    """Criteria for collaboration matching."""
    GENRE_SIMILARITY = "genre_similarity"
    AUDIENCE_OVERLAP = "audience_overlap"
    LOCATION_PROXIMITY = "location_proximity"
    EXPERIENCE_LEVEL = "experience_level"
    COLLABORATION_HISTORY = "collaboration_history"
    FOLLOWER_COUNT = "follower_count"
    ENGAGEMENT_RATE = "engagement_rate"
    CONTENT_QUALITY = "content_quality"
    AVAILABILITY = "availability"
    BUDGET_RANGE = "budget_range"
    LANGUAGE_COMPATIBILITY = "language_compatibility"
    TIMEZONE_COMPATIBILITY = "timezone_compatibility"


class RevenueShareModel(str, Enum):
    """Revenue sharing models for collaborations."""
    EQUAL_SPLIT = "equal_split"
    WEIGHTED_CONTRIBUTION = "weighted_contribution"
    FOLLOWER_BASED = "follower_based"
    TIME_BASED = "time_based"
    INVESTMENT_BASED = "investment_based"
    CUSTOM_AGREEMENT = "custom_agreement"
    FLAT_FEE = "flat_fee"
    ROYALTY_PERCENTAGE = "royalty_percentage"


@dataclass
class CollaborationTerms:
    """Terms and conditions for collaboration."""
    duration_days: int
    revenue_share_model: RevenueShareModel
    revenue_split_percentage: Dict[str, float]
    deliverables: List[str]
    deadlines: Dict[str, datetime]
    exclusivity_required: bool
    credit_requirements: Dict[str, str]
    usage_rights: Dict[str, str]
    termination_conditions: List[str]
    dispute_resolution: str


@dataclass
class CreatorProfile:
    """Creator profile for collaboration matching."""
    creator_id: str
    creator_type: str
    genres: List[str]
    skills: List[str]
    languages: List[str]
    location: Dict[str, str]
    timezone: str
    follower_count: Dict[str, int]
    engagement_rate: float
    collaboration_rating: float
    availability_schedule: Dict[str, List[str]]
    budget_range: Dict[str, int]
    preferred_collaboration_types: List[CollaborationType]
    collaboration_history: List[str]
    portfolio_samples: List[str]


class CollaborationConfig:
    """Enterprise collaboration management configuration."""
    # Collaboration type configurations
    COLLABORATION_TYPES = {
        CollaborationType.MUSIC_COLLAB: {
            "description": "Musical collaboration for original content creation",
            "min_participants": 2,
            "max_participants": 10,
            "typical_duration_days": 60,
            "required_skills": ["music_production", "vocals", "instruments"],
            "deliverables": ["audio_track", "music_video", "marketing_materials"],
            "revenue_models": [
                RevenueShareModel.EQUAL_SPLIT,
                RevenueShareModel.WEIGHTED_CONTRIBUTION,
                RevenueShareModel.ROYALTY_PERCENTAGE
            ],
            "matching_weights": {
                MatchingCriteria.GENRE_SIMILARITY: 0.4,
                MatchingCriteria.EXPERIENCE_LEVEL: 0.2,
                MatchingCriteria.COLLABORATION_HISTORY: 0.2,
                MatchingCriteria.TIMEZONE_COMPATIBILITY: 0.2
            }
        },
        CollaborationType.VIDEO_COLLAB: {
            "description": "Video content collaboration and co-creation",
            "min_participants": 2,
            "max_participants": 8,
            "typical_duration_days": 45,
            "required_skills": ["video_editing", "content_creation", "storytelling"],
            "deliverables": ["video_content", "thumbnails", "social_media_clips"],
            "revenue_models": [
                RevenueShareModel.EQUAL_SPLIT,
                RevenueShareModel.FOLLOWER_BASED,
                RevenueShareModel.ENGAGEMENT_RATE_BASED
            ],
            "matching_weights": {
                MatchingCriteria.AUDIENCE_OVERLAP: 0.3,
                MatchingCriteria.CONTENT_QUALITY: 0.25,
                MatchingCriteria.ENGAGEMENT_RATE: 0.25,
                MatchingCriteria.LOCATION_PROXIMITY: 0.2
            }
        },
        CollaborationType.CROSS_PROMOTION: {
            "description": "Cross-promotional marketing partnership",
            "min_participants": 2,
            "max_participants": 5,
            "typical_duration_days": 30,
            "required_skills": ["social_media", "marketing", "content_planning"],
            "deliverables": ["social_posts", "story_features", "mutual_mentions"],
            "revenue_models": [
                RevenueShareModel.FLAT_FEE,
                RevenueShareModel.FOLLOWER_BASED
            ],
            "matching_weights": {
                MatchingCriteria.AUDIENCE_OVERLAP: 0.4,
                MatchingCriteria.FOLLOWER_COUNT: 0.3,
                MatchingCriteria.ENGAGEMENT_RATE: 0.3
            }
        },
        CollaborationType.BRAND_PARTNERSHIP: {
            "description": "Brand sponsorship and partnership collaboration",
            "min_participants": 2,
            "max_participants": 20,
            "typical_duration_days": 90,
            "required_skills": ["brand_alignment", "audience_engagement", "professional_conduct"],
            "deliverables": ["sponsored_content", "product_reviews", "campaign_participation"],
            "revenue_models": [
                RevenueShareModel.FLAT_FEE,
                RevenueShareModel.CUSTOM_AGREEMENT
            ],
            "matching_weights": {
                MatchingCriteria.AUDIENCE_OVERLAP: 0.35,
                MatchingCriteria.FOLLOWER_COUNT: 0.25,
                MatchingCriteria.ENGAGEMENT_RATE: 0.25,
                MatchingCriteria.CONTENT_QUALITY: 0.15
            }
        }
    }

    # Matching algorithm configurations
    MATCHING_ALGORITHM = {
        "similarity_threshold": 0.7,
        "max_matches_per_request": 20,
        "match_expiry_days": 14,
        "boost_factors": {
            "verified_creators": 1.2,
            "premium_members": 1.15,
            "high_rating": 1.1,
            "frequent_collaborators": 1.05
        },
        "penalty_factors": {
            "low_rating": 0.8,
            "inactive_profile": 0.7,
            "pending_disputes": 0.5,
            "unreliable_history": 0.6
        },
        "geographic_preferences": {
            "same_city": 1.3,
            "same_state": 1.2,
            "same_country": 1.1,
            "same_timezone": 1.15,
            "same_continent": 1.05
        }
    }

    # Revenue sharing configurations
    REVENUE_SHARE_MODELS = {
        RevenueShareModel.EQUAL_SPLIT: {
            "description": "Equal revenue split among all participants",
            "calculation_method": "total_revenue / participant_count",
            "minimum_participants": 2,
            "maximum_participants": 10,
            "requires_agreement": False,
            "dispute_resolution": "automatic_mediation"
        },
        RevenueShareModel.WEIGHTED_CONTRIBUTION: {
            "description": "Revenue split based on contribution percentage",
            "calculation_method": "total_revenue * contribution_weight",
            "factors": ["time_invested", "skills_provided", "resources_contributed"],
            "requires_agreement": True,
            "dispute_resolution": "expert_panel_review"
        },
        RevenueShareModel.FOLLOWER_BASED: {
            "description": "Revenue split based on follower count ratio",
            "calculation_method": "total_revenue * (follower_count / total_followers)",
            "platforms": ["instagram", "youtube", "tiktok", "spotify"],
            "weight_per_platform": {"instagram": 0.3, "youtube": 0.4, "tiktok": 0.2, "spotify": 0.1},
            "requires_verification": True
        },
        RevenueShareModel.FLAT_FEE: {
            "description": "Fixed payment regardless of revenue performance",
            "payment_schedule": ["upfront", "milestone_based", "completion"],
            "currency_options": ["USD", "EUR", "GBP"],
            "escrow_required": True
        }
    }

    # Collaboration workflow stages
    COLLABORATION_WORKFLOW = {
        "discovery": {
            "duration_days": 3,
            "actions": ["search_matches", "review_profiles", "send_invitations"],
            "auto_reminders": True,
            "timeout_action": "extend_search"
        },
        "negotiation": {
            "duration_days": 7,
            "actions": ["discuss_terms", "agree_deliverables", "set_timeline"],
            "required_agreements": ["revenue_split", "credit_attribution", "usage_rights"],
            "timeout_action": "auto_decline"
        },
        "contract": {
            "duration_days": 3,
            "actions": ["review_contract", "digital_signature", "escrow_setup"],
            "legal_review_required": True,
            "timeout_action": "cancel_collaboration"
        },
        "execution": {
            "duration_days": "variable",
            "actions": ["create_content", "review_progress", "meet_milestones"],
            "milestone_tracking": True,
            "quality_assurance": True
        },
        "completion": {
            "duration_days": 7,
            "actions": ["final_review", "approve_deliverables", "process_payment"],
            "satisfaction_survey": True,
            "rating_exchange": True
        }
    }

    # Quality and safety measures
    SAFETY_MEASURES = {
        "verification_requirements": {
            "identity_verification": True,
            "portfolio_verification": True,
            "contact_information": True,
            "social_media_verification": True
        },
        "background_checks": {
            "collaboration_history": True,
            "dispute_record": True,
            "rating_threshold": 3.5,
            "completion_rate_minimum": 0.8
        },
        "content_guidelines": {
            "explicit_content_policy": "restricted",
            "copyright_compliance": "mandatory",
            "brand_safety_guidelines": True,
            "community_standards": "enforced"
        },
        "dispute_resolution": {
            "mediation_service": "professional_mediation",
            "arbitration_available": True,
            "refund_policy": "case_by_case",
            "suspension_policy": "temporary_for_investigation"
        }
    }

    # Performance metrics and KPIs
    PERFORMANCE_METRICS = {
        "matching_accuracy": {
            "target_percentage": 85,
            "measurement": "successful_collaborations / total_matches",
            "tracking_period": "monthly"
        },
        "collaboration_completion_rate": {
            "target_percentage": 80,
            "measurement": "completed_projects / started_projects",
            "tracking_period": "quarterly"
        },
        "user_satisfaction_score": {
            "target_score": 4.2,
            "measurement": "average_rating",
            "minimum_responses": 10
        },
        "revenue_processing_accuracy": {
            "target_percentage": 99.9,
            "measurement": "correct_payments / total_payments",
            "error_tolerance": 0.1
        },
        "dispute_resolution_time": {
            "target_days": 7,
            "measurement": "average_resolution_time",
            "escalation_threshold": 14
        }
    }

    # Geographic and cultural considerations
    REGIONAL_PREFERENCES = {
        "north_america": {
            "preferred_communication": ["email", "discord", "slack"],
            "business_hours": "9am-5pm EST/PST",
            "payment_methods": ["paypal", "stripe", "wise"],
            "legal_framework": "US_commercial_law"
        },
        "europe": {
            "preferred_communication": ["email", "whatsapp", "teams"],
            "business_hours": "9am-5pm CET",
            "payment_methods": ["sepa", "paypal", "wise"],
            "legal_framework": "EU_commercial_law",
            "gdpr_compliance": "required"
        },
        "asia_pacific": {
            "preferred_communication": ["wechat", "line", "email"],
            "business_hours": "variable_by_country",
            "payment_methods": ["alipay", "paypal", "local_banks"],
            "legal_framework": "country_specific"
        }
    }

    @classmethod
    def calculate_collaboration_score(cls, creator1: CreatorProfile, creator2: CreatorProfile, 
                                    collab_type: CollaborationType) -> float:
        """Calculate compatibility score between two creators."""
        type_config = cls.COLLABORATION_TYPES.get(collab_type)
        if not type_config:
            return 0.0
        
        matching_weights = type_config["matching_weights"]
        total_score = 0.0
        
        for criteria, weight in matching_weights.items():
            criteria_score = cls._calculate_criteria_score(creator1, creator2, criteria)
            total_score += criteria_score * weight
        
        return min(total_score, 1.0)

    @classmethod
    def _calculate_criteria_score(cls, creator1: CreatorProfile, creator2: CreatorProfile, 
                                criteria: MatchingCriteria) -> float:
        """Calculate score for specific matching criteria."""
        if criteria == MatchingCriteria.GENRE_SIMILARITY:
            common_genres = set(creator1.genres) & set(creator2.genres)
            total_genres = set(creator1.genres) | set(creator2.genres)
            return len(common_genres) / len(total_genres) if total_genres else 0.0
        
        elif criteria == MatchingCriteria.AUDIENCE_OVERLAP:
            # Simplified calculation - would integrate with analytics data
            overlap = min(creator1.follower_count.get("total", 0), creator2.follower_count.get("total", 0))
            total = max(creator1.follower_count.get("total", 1), creator2.follower_count.get("total", 1))
            return overlap / total
        
        elif criteria == MatchingCriteria.EXPERIENCE_LEVEL:
            exp_diff = abs(len(creator1.collaboration_history) - len(creator2.collaboration_history))
            return max(0, 1 - (exp_diff / 10))  # Normalize based on collaboration count
        
        elif criteria == MatchingCriteria.COLLABORATION_HISTORY:
            # Check for common collaborators or successful past projects
            common_collabs = set(creator1.collaboration_history) & set(creator2.collaboration_history)
            return min(len(common_collabs) * 0.2, 1.0)
        
        else:
            return 0.5  # Default neutral score

    @classmethod
    def get_collaboration_terms_template(cls, collab_type: CollaborationType) -> CollaborationTerms:
        """Get default terms template for collaboration type."""
        type_config = cls.COLLABORATION_TYPES.get(collab_type)
        if not type_config:
            return None
        
        return CollaborationTerms(
            duration_days=type_config["typical_duration_days"],
            revenue_share_model=type_config["revenue_models"][0],
            revenue_split_percentage={},  # To be filled during negotiation
            deliverables=type_config["deliverables"],
            deadlines={},  # To be set during negotiation
            exclusivity_required=False,
            credit_requirements={},
            usage_rights={},
            termination_conditions=[
                "mutual_agreement",
                "breach_of_contract",
                "non_performance"
            ],
            dispute_resolution="mediation_first"
        )

    @classmethod
    def validate_collaboration_request(cls, creator_id: str, target_creator_id: str, 
                                     collab_type: CollaborationType) -> Tuple[bool, str]:
        """Validate collaboration request before processing."""
        # Basic validation logic
        if creator_id == target_creator_id:
            return False, "Cannot collaborate with yourself"
        
        type_config = cls.COLLABORATION_TYPES.get(collab_type)
        if not type_config:
            return False, "Invalid collaboration type"
        
        # Would include additional checks:
        # - Creator eligibility
        # - Active dispute checks
        # - Rate limiting
        # - Blacklist verification
        
        return True, "Valid collaboration request"

    @classmethod
    def calculate_revenue_split(cls, total_revenue: float, model: RevenueShareModel, 
                              participants: List[Dict], **kwargs) -> Dict[str, float]:
        """Calculate revenue distribution based on sharing model."""
        if model == RevenueShareModel.EQUAL_SPLIT:
            split_amount = total_revenue / len(participants)
            return {p["creator_id"]: split_amount for p in participants}
        
        elif model == RevenueShareModel.WEIGHTED_CONTRIBUTION:
            total_weight = sum(p.get("contribution_weight", 1) for p in participants)
            return {
                p["creator_id"]: total_revenue * (p.get("contribution_weight", 1) / total_weight)
                for p in participants
            }
        
        elif model == RevenueShareModel.FOLLOWER_BASED:
            total_followers = sum(p.get("follower_count", 0) for p in participants)
            if total_followers == 0:
                return cls.calculate_revenue_split(total_revenue, RevenueShareModel.EQUAL_SPLIT, participants)
            
            return {
                p["creator_id"]: total_revenue * (p.get("follower_count", 0) / total_followers)
                for p in participants
            }
        
        else:
            # Default to equal split for unknown models
            return cls.calculate_revenue_split(total_revenue, RevenueShareModel.EQUAL_SPLIT, participants)

    @classmethod
    def get_matching_preferences(cls, creator_type: str, location: str) -> Dict:
        """Get matching preferences based on creator profile."""
        base_preferences = {
            "max_distance_km": 100,
            "timezone_difference_hours": 3,
            "language_match_required": False,
            "experience_level_range": 2,
            "minimum_rating": 3.0
        }
        
        # Customize based on creator type
        if creator_type == "musician":
            base_preferences.update({
                "genre_match_importance": 0.8,
                "instrument_compatibility": True,
                "studio_access_preferred": True
            })
        elif creator_type == "influencer":
            base_preferences.update({
                "audience_overlap_importance": 0.9,
                "brand_alignment_required": True,
                "content_style_similarity": 0.7
            })
        
        return base_preferences
