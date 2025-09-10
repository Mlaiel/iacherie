"""
Collaboration Business Configuration - Enterprise Configuration Management
Enterprise configuration for collaboration business logic and partnership systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


class CollaborationType(str, Enum):
    """Types of collaboration"""
    CONTENT_COLLABORATION = "content_collaboration"
    CROSS_PROMOTION = "cross_promotion"
    REVENUE_SHARING = "revenue_sharing"
    JOINT_VENTURE = "joint_venture"
    MENTORSHIP = "mentorship"
    SKILL_EXCHANGE = "skill_exchange"
    PROJECT_PARTNERSHIP = "project_partnership"
    BRAND_COLLABORATION = "brand_collaboration"


class CollaborationStatus(str, Enum):
    """Collaboration status"""
    PROPOSED = "proposed"
    PENDING = "pending"
    ACCEPTED = "accepted"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    PAUSED = "paused"


class RevenueModel(str, Enum):
    """Revenue sharing models"""
    EQUAL_SPLIT = "equal_split"
    WEIGHTED_SPLIT = "weighted_split"
    CONTRIBUTION_BASED = "contribution_based"
    ROLE_BASED = "role_based"
    PERFORMANCE_BASED = "performance_based"
    FIXED_FEE = "fixed_fee"
    MILESTONE_BASED = "milestone_based"
    SKILL_EXCHANGE = "skill_exchange"


class MatchingCriteria(str, Enum):
    """Creator matching criteria"""
    SKILL_BASED = "skill_based"
    GENRE_BASED = "genre_based"
    AUDIENCE_OVERLAP = "audience_overlap"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    EXPERIENCE_LEVEL = "experience_level"
    AVAILABILITY = "availability"
    REPUTATION_SCORE = "reputation_score"
    COLLABORATION_HISTORY = "collaboration_history"


@dataclass
class CollaborationTemplate:
    """Collaboration template configuration"""
    template_name: str
    collaboration_type: CollaborationType
    required_roles: List[str]
    optional_roles: List[str]
    default_revenue_model: RevenueModel
    duration_days: int
    required_skills: List[str]
    workflow_steps: List[str]
    deliverables: List[str]


@dataclass
class RevenueDistribution:
    """Revenue distribution configuration"""
    model: RevenueModel
    percentages: Dict[str, float]
    conditions: Dict[str, Any]
    minimum_payout: float
    payment_schedule: str
    dispute_resolution: str


@dataclass
class CollaborationWorkflow:
    """Collaboration workflow configuration"""
    workflow_name: str
    stages: List[str]
    approval_points: List[str]
    automation_enabled: bool
    notification_triggers: List[str]
    deadline_tracking: bool


class CollaborationBusinessSettings:
    """Collaboration business configuration settings"""
    
    def __init__(self):
        # Collaboration Templates
        self.collaboration_templates = {
            "music_collaboration": CollaborationTemplate(
                template_name="music_collaboration",
                collaboration_type=CollaborationType.CONTENT_COLLABORATION,
                required_roles=["primary_artist", "collaborating_artist"],
                optional_roles=["producer", "songwriter", "vocalist"],
                default_revenue_model=RevenueModel.CONTRIBUTION_BASED,
                duration_days=90,
                required_skills=["music_production", "performance"],
                workflow_steps=[
                    "project_proposal",
                    "role_assignment",
                    "collaboration_agreement",
                    "content_creation",
                    "review_approval",
                    "final_production",
                    "distribution",
                    "revenue_sharing"
                ],
                deliverables=["final_track", "stems", "artwork", "metadata"]
            ),
            
            "content_partnership": CollaborationTemplate(
                template_name="content_partnership",
                collaboration_type=CollaborationType.CROSS_PROMOTION,
                required_roles=["content_creator_1", "content_creator_2"],
                optional_roles=["editor", "marketer"],
                default_revenue_model=RevenueModel.EQUAL_SPLIT,
                duration_days=30,
                required_skills=["content_creation", "social_media"],
                workflow_steps=[
                    "partnership_proposal",
                    "content_planning",
                    "cross_promotion_agreement",
                    "content_creation",
                    "mutual_promotion",
                    "performance_tracking"
                ],
                deliverables=["promoted_content", "metrics_report"]
            ),
            
            "brand_collaboration": CollaborationTemplate(
                template_name="brand_collaboration",
                collaboration_type=CollaborationType.BRAND_COLLABORATION,
                required_roles=["brand", "influencer"],
                optional_roles=["content_creator", "photographer"],
                default_revenue_model=RevenueModel.FIXED_FEE,
                duration_days=60,
                required_skills=["brand_alignment", "content_creation"],
                workflow_steps=[
                    "brand_brief",
                    "proposal_submission",
                    "contract_negotiation",
                    "content_creation",
                    "brand_approval",
                    "content_publishing",
                    "performance_reporting"
                ],
                deliverables=["sponsored_content", "performance_metrics", "usage_rights"]
            ),
            
            "mentorship_program": CollaborationTemplate(
                template_name="mentorship_program",
                collaboration_type=CollaborationType.MENTORSHIP,
                required_roles=["mentor", "mentee"],
                optional_roles=["program_coordinator"],
                default_revenue_model=RevenueModel.SKILL_EXCHANGE,
                duration_days=180,
                required_skills=["expertise_in_field", "teaching_ability"],
                workflow_steps=[
                    "mentor_matching",
                    "goal_setting",
                    "regular_sessions",
                    "progress_tracking",
                    "milestone_reviews",
                    "program_completion"
                ],
                deliverables=["learning_plan", "progress_reports", "certification"]
            )
        }
        
        # Revenue Distribution Models
        self.revenue_models = {
            RevenueModel.EQUAL_SPLIT: RevenueDistribution(
                model=RevenueModel.EQUAL_SPLIT,
                percentages={"default": 50.0},
                conditions={"minimum_participants": 2},
                minimum_payout=10.0,
                payment_schedule="monthly",
                dispute_resolution="automated_mediation"
            ),
            
            RevenueModel.CONTRIBUTION_BASED: RevenueDistribution(
                model=RevenueModel.CONTRIBUTION_BASED,
                percentages={
                    "content_creation": 40.0,
                    "production": 30.0,
                    "promotion": 20.0,
                    "distribution": 10.0
                },
                conditions={"contribution_tracking": True},
                minimum_payout=5.0,
                payment_schedule="per_milestone",
                dispute_resolution="expert_panel"
            ),
            
            RevenueModel.PERFORMANCE_BASED: RevenueDistribution(
                model=RevenueModel.PERFORMANCE_BASED,
                percentages={
                    "base_payment": 30.0,
                    "performance_bonus": 70.0
                },
                conditions={
                    "performance_metrics": ["views", "engagement", "conversions"],
                    "threshold_multipliers": [1.0, 1.5, 2.0, 3.0]
                },
                minimum_payout=25.0,
                payment_schedule="quarterly",
                dispute_resolution="performance_audit"
            )
        }
        
        # Collaboration Workflows
        self.workflows = {
            "standard_collaboration": CollaborationWorkflow(
                workflow_name="standard_collaboration",
                stages=[
                    "proposal",
                    "negotiation",
                    "agreement",
                    "execution",
                    "review",
                    "completion",
                    "settlement"
                ],
                approval_points=["agreement", "completion"],
                automation_enabled=True,
                notification_triggers=[
                    "stage_transition",
                    "deadline_approaching",
                    "approval_required",
                    "dispute_raised"
                ],
                deadline_tracking=True
            ),
            
            "fast_track_collaboration": CollaborationWorkflow(
                workflow_name="fast_track_collaboration",
                stages=[
                    "instant_match",
                    "quick_agreement",
                    "immediate_execution",
                    "rapid_completion"
                ],
                approval_points=["quick_agreement"],
                automation_enabled=True,
                notification_triggers=["stage_transition", "completion"],
                deadline_tracking=True
            )
        }
        
        # Matching Algorithm Configuration
        self.matching_algorithm = {
            "enabled": True,
            "matching_criteria": [
                MatchingCriteria.SKILL_BASED,
                MatchingCriteria.GENRE_BASED,
                MatchingCriteria.AUDIENCE_OVERLAP,
                MatchingCriteria.REPUTATION_SCORE
            ],
            "weights": {
                MatchingCriteria.SKILL_BASED: 0.30,
                MatchingCriteria.GENRE_BASED: 0.25,
                MatchingCriteria.AUDIENCE_OVERLAP: 0.20,
                MatchingCriteria.REPUTATION_SCORE: 0.15,
                MatchingCriteria.AVAILABILITY: 0.10
            },
            "minimum_match_score": 0.7,
            "maximum_suggestions": 10,
            "refresh_interval_hours": 24
        }
        
        # Collaboration Tools Configuration
        self.collaboration_tools = {
            "project_management": {
                "enabled": True,
                "features": [
                    "task_assignment",
                    "deadline_tracking",
                    "progress_monitoring",
                    "file_sharing",
                    "version_control"
                ]
            },
            "communication": {
                "enabled": True,
                "channels": [
                    "real_time_chat",
                    "video_calls",
                    "voice_calls",
                    "screen_sharing",
                    "collaborative_editing"
                ]
            },
            "financial_management": {
                "enabled": True,
                "features": [
                    "expense_tracking",
                    "revenue_calculation",
                    "payment_processing",
                    "tax_reporting",
                    "invoice_generation"
                ]
            }
        }
        
        # Quality Assurance
        self.quality_assurance = {
            "collaboration_rating": True,
            "performance_tracking": True,
            "dispute_prevention": True,
            "quality_metrics": [
                "completion_rate",
                "on_time_delivery",
                "collaboration_satisfaction",
                "revenue_achievement"
            ],
            "minimum_quality_score": 4.0,
            "review_required_threshold": 3.5
        }
        
        # Legal and Compliance
        self.legal_compliance = {
            "contract_templates": True,
            "intellectual_property_protection": True,
            "dispute_resolution_process": True,
            "legal_review_required": False,
            "jurisdiction": "international",
            "governing_law": "platform_terms"
        }
        
        # Business Intelligence
        self.business_intelligence = {
            "analytics_enabled": True,
            "success_metrics": [
                "collaboration_completion_rate",
                "average_revenue_per_collaboration",
                "creator_satisfaction_score",
                "repeat_collaboration_rate"
            ],
            "reporting_frequency": "monthly",
            "predictive_analytics": True,
            "trend_analysis": True
        }
        
        # Platform Integration
        self.platform_integration = {
            "cross_platform_promotion": True,
            "unified_content_distribution": True,
            "shared_analytics": True,
            "collaborative_monetization": True,
            "joint_audience_building": True
        }
        
        # Security and Privacy
        self.security_privacy = {
            "data_encryption": True,
            "privacy_protection": True,
            "confidentiality_agreements": True,
            "secure_file_sharing": True,
            "access_control": True,
            "audit_logging": True
        }
    
    def get_collaboration_template(self, template_name: str) -> Optional[CollaborationTemplate]:
        """Get collaboration template by name"""
        return self.collaboration_templates.get(template_name)
    
    def get_revenue_model(self, model_type: RevenueModel) -> Optional[RevenueDistribution]:
        """Get revenue distribution model"""
        return self.revenue_models.get(model_type)
    
    def get_workflow(self, workflow_name: str) -> Optional[CollaborationWorkflow]:
        """Get collaboration workflow"""
        return self.workflows.get(workflow_name)
    
    def calculate_match_score(self, creator1_profile: Dict[str, Any], 
                            creator2_profile: Dict[str, Any]) -> float:
        """Calculate collaboration match score"""
        score = 0.0
        total_weight = 0.0
        
        for criteria, weight in self.matching_algorithm["weights"].items():
            # Simplified scoring logic - would be replaced with actual algorithm
            criteria_score = 0.8  # Placeholder
            score += criteria_score * weight
            total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def get_collaboration_types_for_creator(self, creator_type: str) -> List[CollaborationType]:
        """Get suitable collaboration types for creator type"""
        type_mapping = {
            "musicians": [
                CollaborationType.CONTENT_COLLABORATION,
                CollaborationType.CROSS_PROMOTION,
                CollaborationType.REVENUE_SHARING
            ],
            "influencers": [
                CollaborationType.BRAND_COLLABORATION,
                CollaborationType.CROSS_PROMOTION,
                CollaborationType.JOINT_VENTURE
            ],
            "photographers": [
                CollaborationType.PROJECT_PARTNERSHIP,
                CollaborationType.SKILL_EXCHANGE,
                CollaborationType.BRAND_COLLABORATION
            ]
        }
        return type_mapping.get(creator_type, [])
    
    def validate_collaboration_proposal(self, proposal: Dict[str, Any]) -> List[str]:
        """Validate collaboration proposal"""
        errors = []
        
        required_fields = ["collaboration_type", "participants", "duration", "deliverables"]
        for field in required_fields:
            if field not in proposal:
                errors.append(f"Missing required field: {field}")
        
        # Validate collaboration type
        if proposal.get("collaboration_type") not in [ct.value for ct in CollaborationType]:
            errors.append("Invalid collaboration type")
        
        # Validate participants
        participants = proposal.get("participants", [])
        if len(participants) < 2:
            errors.append("At least 2 participants required")
        
        return errors
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete collaboration configuration"""
        errors = []
        
        # Validate templates
        for template_name, template in self.collaboration_templates.items():
            if not template.required_roles:
                errors.append(f"Template '{template_name}' has no required roles")
            if template.duration_days <= 0:
                errors.append(f"Invalid duration for template '{template_name}'")
        
        # Validate revenue models
        for model_type, distribution in self.revenue_models.items():
            total_percentage = sum(distribution.percentages.values())
            if abs(total_percentage - 100.0) > 0.01:
                errors.append(f"Revenue percentages don't sum to 100% for model '{model_type}'")
        
        # Validate matching algorithm weights
        total_weight = sum(self.matching_algorithm["weights"].values())
        if abs(total_weight - 1.0) > 0.01:
            errors.append("Matching algorithm weights don't sum to 1.0")
        
        return errors


# Global collaboration business settings instance
collaboration_business_settings = CollaborationBusinessSettings()

__all__ = [
    "CollaborationBusinessSettings",
    "collaboration_business_settings",
    "CollaborationType",
    "CollaborationStatus",
    "RevenueModel",
    "MatchingCriteria",
    "CollaborationTemplate",
    "RevenueDistribution",
    "CollaborationWorkflow"
]