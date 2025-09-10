"""
Creator Collaboration Configurations
===================================

Creator collaboration and partnership settings for Ainflue Distribution Platform.
Manages collaboration workflows, revenue sharing, and creator matching.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import os
import json

class CollaborationType(Enum):
    """Types of creator collaborations"""
    CROSS_PROMOTION = "cross_promotion"
    CONTENT_CREATION = "content_creation"
    REVENUE_SHARE = "revenue_share"
    GUEST_APPEARANCE = "guest_appearance"
    JOINT_CAMPAIGN = "joint_campaign"
    SKILL_EXCHANGE = "skill_exchange"
    MENTORSHIP = "mentorship"
    CO_BRANDING = "co_branding"

class RevenueShareModel(Enum):
    """Revenue sharing models for collaborations"""
    EQUAL_SPLIT = "equal_split"  # 50/50 split
    PROPORTIONAL = "proportional"  # Based on contribution/following
    CUSTOM_SPLIT = "custom_split"  # Custom percentage split
    LEAD_CREATOR = "lead_creator"  # 70/30 in favor of lead
    PERFORMANCE_BASED = "performance_based"  # Based on performance metrics
    FLAT_FEE = "flat_fee"  # Fixed payment regardless of performance

class CreatorTier(Enum):
    """Creator tier levels for matching and collaboration"""
    NANO = "nano"  # 1K-10K followers
    MICRO = "micro"  # 10K-100K followers
    MACRO = "macro"  # 100K-1M followers
    MEGA = "mega"  # 1M+ followers
    CELEBRITY = "celebrity"  # 10M+ followers

class MatchingCriteria(Enum):
    """Criteria for creator matching algorithm"""
    AUDIENCE_OVERLAP = "audience_overlap"
    CONTENT_STYLE = "content_style"
    ENGAGEMENT_RATE = "engagement_rate"
    BRAND_ALIGNMENT = "brand_alignment"
    NICHE_COMPATIBILITY = "niche_compatibility"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    COLLABORATION_HISTORY = "collaboration_history"
    PLATFORM_PRESENCE = "platform_presence"

@dataclass
class CollaborationConfig:
    """Base configuration for collaborations"""
    collaboration_type: CollaborationType
    min_creator_tier: CreatorTier
    max_creator_tier: CreatorTier
    revenue_share_model: RevenueShareModel
    default_duration_days: int = 30
    approval_required: bool = True
    auto_matching_enabled: bool = True
    cross_platform_allowed: bool = True
    exclusive_partnership: bool = False
    contract_template: str = "standard"
    
@dataclass
class RevenueShareConfig:
    """Revenue sharing configuration details"""
    model: RevenueShareModel
    primary_creator_percentage: float = 50.0
    secondary_creator_percentage: float = 50.0
    platform_fee_percentage: float = 10.0
    minimum_payout_threshold: float = 25.0
    payment_schedule: str = "monthly"  # weekly, bi-weekly, monthly
    currency: str = "USD"
    tax_handling: str = "creator_responsible"  # platform_handles, creator_responsible
    payment_methods: List[str] = field(default_factory=lambda: ["paypal", "stripe", "bank_transfer"])

@dataclass
class CreatorMatchingConfig:
    """Configuration for creator matching algorithm"""
    enabled_criteria: List[MatchingCriteria] = field(default_factory=list)
    weight_factors: Dict[MatchingCriteria, float] = field(default_factory=dict)
    minimum_match_score: float = 0.7
    max_suggestions_per_creator: int = 10
    refresh_interval_hours: int = 24
    exclude_recent_collaborators: bool = True
    exclude_competitors: bool = True
    geographic_radius_km: Optional[int] = None
    
@dataclass
class CollaborationWorkflowConfig:
    """Workflow configuration for collaboration process"""
    proposal_auto_approval: bool = False
    proposal_expiry_days: int = 7
    contract_generation_auto: bool = True
    content_approval_required: bool = True
    performance_tracking_enabled: bool = True
    dispute_resolution_process: str = "mediation"  # mediation, arbitration, platform_decision
    feedback_collection_enabled: bool = True
    rating_system_enabled: bool = True
    
@dataclass
class ContentCollaborationConfig:
    """Content-specific collaboration settings"""
    supported_content_types: List[str] = field(default_factory=lambda: ["video", "image", "audio", "text"])
    quality_standards: Dict[str, Any] = field(default_factory=dict)
    brand_safety_checks: bool = True
    content_moderation_level: str = "standard"  # basic, standard, strict
    attribution_requirements: List[str] = field(default_factory=lambda: ["creator_tag", "platform_tag"])
    cross_posting_allowed: bool = True
    exclusive_content_premium: float = 1.5  # 50% premium for exclusive content
    
@dataclass
class CommunicationConfig:
    """Communication settings for collaborations"""
    in_platform_messaging: bool = True
    external_communication_allowed: bool = True
    auto_introduction_enabled: bool = True
    collaboration_channels: List[str] = field(default_factory=lambda: ["chat", "video_call", "email"])
    language_matching_preferred: bool = True
    timezone_consideration: bool = True
    response_time_sla_hours: int = 24

class CollaborationConfigs:
    """
    Creator collaboration configuration manager
    
    Features:
    - Collaboration type management
    - Revenue sharing models
    - Creator matching algorithms
    - Workflow automation
    - Content collaboration rules
    - Communication preferences
    """
    
    def __init__(self):
        self.collaboration_configs: Dict[CollaborationType, CollaborationConfig] = {}
        self.revenue_share_configs: Dict[RevenueShareModel, RevenueShareConfig] = {}
        self.matching_config = CreatorMatchingConfig()
        self.workflow_config = CollaborationWorkflowConfig()
        self.content_config = ContentCollaborationConfig()
        self.communication_config = CommunicationConfig()
        self._load_default_configurations()
        
    def _load_default_configurations(self):
        """Load default collaboration configurations"""
        
        # Cross-promotion collaborations
        self.collaboration_configs[CollaborationType.CROSS_PROMOTION] = CollaborationConfig(
            collaboration_type=CollaborationType.CROSS_PROMOTION,
            min_creator_tier=CreatorTier.NANO,
            max_creator_tier=CreatorTier.CELEBRITY,
            revenue_share_model=RevenueShareModel.EQUAL_SPLIT,
            default_duration_days=14,
            approval_required=False,
            auto_matching_enabled=True,
            cross_platform_allowed=True,
            exclusive_partnership=False,
            contract_template="cross_promotion"
        )
        
        # Content creation collaborations
        self.collaboration_configs[CollaborationType.CONTENT_CREATION] = CollaborationConfig(
            collaboration_type=CollaborationType.CONTENT_CREATION,
            min_creator_tier=CreatorTier.MICRO,
            max_creator_tier=CreatorTier.MEGA,
            revenue_share_model=RevenueShareModel.PROPORTIONAL,
            default_duration_days=30,
            approval_required=True,
            auto_matching_enabled=True,
            cross_platform_allowed=True,
            exclusive_partnership=False,
            contract_template="content_creation"
        )
        
        # Revenue share collaborations
        self.collaboration_configs[CollaborationType.REVENUE_SHARE] = CollaborationConfig(
            collaboration_type=CollaborationType.REVENUE_SHARE,
            min_creator_tier=CreatorTier.MICRO,
            max_creator_tier=CreatorTier.CELEBRITY,
            revenue_share_model=RevenueShareModel.PERFORMANCE_BASED,
            default_duration_days=60,
            approval_required=True,
            auto_matching_enabled=False,
            cross_platform_allowed=True,
            exclusive_partnership=True,
            contract_template="revenue_share"
        )
        
        # Joint campaign collaborations
        self.collaboration_configs[CollaborationType.JOINT_CAMPAIGN] = CollaborationConfig(
            collaboration_type=CollaborationType.JOINT_CAMPAIGN,
            min_creator_tier=CreatorTier.MACRO,
            max_creator_tier=CreatorTier.CELEBRITY,
            revenue_share_model=RevenueShareModel.CUSTOM_SPLIT,
            default_duration_days=45,
            approval_required=True,
            auto_matching_enabled=False,
            cross_platform_allowed=True,
            exclusive_partnership=True,
            contract_template="joint_campaign"
        )
        
        # Revenue share models
        self.revenue_share_configs[RevenueShareModel.EQUAL_SPLIT] = RevenueShareConfig(
            model=RevenueShareModel.EQUAL_SPLIT,
            primary_creator_percentage=50.0,
            secondary_creator_percentage=50.0,
            platform_fee_percentage=5.0,
            minimum_payout_threshold=25.0,
            payment_schedule="monthly"
        )
        
        self.revenue_share_configs[RevenueShareModel.PROPORTIONAL] = RevenueShareConfig(
            model=RevenueShareModel.PROPORTIONAL,
            primary_creator_percentage=60.0,
            secondary_creator_percentage=40.0,
            platform_fee_percentage=8.0,
            minimum_payout_threshold=50.0,
            payment_schedule="monthly"
        )
        
        self.revenue_share_configs[RevenueShareModel.LEAD_CREATOR] = RevenueShareConfig(
            model=RevenueShareModel.LEAD_CREATOR,
            primary_creator_percentage=70.0,
            secondary_creator_percentage=30.0,
            platform_fee_percentage=7.0,
            minimum_payout_threshold=30.0,
            payment_schedule="bi-weekly"
        )
        
        self.revenue_share_configs[RevenueShareModel.PERFORMANCE_BASED] = RevenueShareConfig(
            model=RevenueShareModel.PERFORMANCE_BASED,
            primary_creator_percentage=50.0,  # Base percentage, adjusted by performance
            secondary_creator_percentage=50.0,
            platform_fee_percentage=10.0,
            minimum_payout_threshold=100.0,
            payment_schedule="monthly"
        )
        
        # Creator matching configuration
        self.matching_config = CreatorMatchingConfig(
            enabled_criteria=[
                MatchingCriteria.AUDIENCE_OVERLAP,
                MatchingCriteria.CONTENT_STYLE,
                MatchingCriteria.ENGAGEMENT_RATE,
                MatchingCriteria.NICHE_COMPATIBILITY,
                MatchingCriteria.PLATFORM_PRESENCE
            ],
            weight_factors={
                MatchingCriteria.AUDIENCE_OVERLAP: 0.25,
                MatchingCriteria.CONTENT_STYLE: 0.20,
                MatchingCriteria.ENGAGEMENT_RATE: 0.20,
                MatchingCriteria.NICHE_COMPATIBILITY: 0.15,
                MatchingCriteria.PLATFORM_PRESENCE: 0.10,
                MatchingCriteria.BRAND_ALIGNMENT: 0.10
            },
            minimum_match_score=0.65,
            max_suggestions_per_creator=8,
            refresh_interval_hours=12,
            exclude_recent_collaborators=True,
            exclude_competitors=True
        )
        
        # Workflow configuration
        self.workflow_config = CollaborationWorkflowConfig(
            proposal_auto_approval=False,
            proposal_expiry_days=5,
            contract_generation_auto=True,
            content_approval_required=True,
            performance_tracking_enabled=True,
            dispute_resolution_process="mediation",
            feedback_collection_enabled=True,
            rating_system_enabled=True
        )
        
        # Content collaboration configuration
        self.content_config = ContentCollaborationConfig(
            supported_content_types=["video", "image", "audio", "text", "live", "story"],
            quality_standards={
                "video": {"min_resolution": "1080p", "min_duration_seconds": 30},
                "image": {"min_resolution": "1920x1080", "formats": ["jpg", "png"]},
                "audio": {"min_bitrate": "128kbps", "formats": ["mp3", "wav"]}
            },
            brand_safety_checks=True,
            content_moderation_level="standard",
            attribution_requirements=["creator_tag", "collaboration_tag"],
            cross_posting_allowed=True,
            exclusive_content_premium=1.3
        )
        
        # Communication configuration
        self.communication_config = CommunicationConfig(
            in_platform_messaging=True,
            external_communication_allowed=True,
            auto_introduction_enabled=True,
            collaboration_channels=["chat", "video_call", "email", "phone"],
            language_matching_preferred=True,
            timezone_consideration=True,
            response_time_sla_hours=12
        )
        
    def get_collaboration_config(self, collaboration_type: CollaborationType) -> Optional[CollaborationConfig]:
        """Get configuration for a collaboration type"""
        return self.collaboration_configs.get(collaboration_type)
        
    def get_revenue_share_config(self, model: RevenueShareModel) -> Optional[RevenueShareConfig]:
        """Get revenue sharing configuration for a model"""
        return self.revenue_share_configs.get(model)
        
    def calculate_revenue_split(
        self, 
        total_revenue: float, 
        model: RevenueShareModel,
        performance_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """Calculate revenue split based on model and performance"""
        config = self.get_revenue_share_config(model)
        if not config:
            # Default equal split
            platform_fee = total_revenue * 0.1
            remaining = total_revenue - platform_fee
            return {
                "primary_creator": remaining * 0.5,
                "secondary_creator": remaining * 0.5,
                "platform_fee": platform_fee,
                "total": total_revenue
            }
            
        platform_fee = total_revenue * (config.platform_fee_percentage / 100)
        remaining = total_revenue - platform_fee
        
        if model == RevenueShareModel.PERFORMANCE_BASED and performance_metrics:
            # Adjust split based on performance
            primary_performance = performance_metrics.get("primary_engagement", 0.5)
            secondary_performance = performance_metrics.get("secondary_engagement", 0.5)
            total_performance = primary_performance + secondary_performance
            
            if total_performance > 0:
                primary_percentage = primary_performance / total_performance
                secondary_percentage = secondary_performance / total_performance
            else:
                primary_percentage = 0.5
                secondary_percentage = 0.5
        else:
            primary_percentage = config.primary_creator_percentage / 100
            secondary_percentage = config.secondary_creator_percentage / 100
            
        return {
            "primary_creator": remaining * primary_percentage,
            "secondary_creator": remaining * secondary_percentage,
            "platform_fee": platform_fee,
            "total": total_revenue,
            "primary_percentage": primary_percentage * 100,
            "secondary_percentage": secondary_percentage * 100
        }
        
    def calculate_match_score(
        self, 
        creator1_profile: Dict[str, Any], 
        creator2_profile: Dict[str, Any]
    ) -> float:
        """Calculate compatibility score between two creators"""
        total_score = 0.0
        total_weight = 0.0
        
        for criteria in self.matching_config.enabled_criteria:
            weight = self.matching_config.weight_factors.get(criteria, 0.1)
            score = self._calculate_criteria_score(criteria, creator1_profile, creator2_profile)
            total_score += score * weight
            total_weight += weight
            
        return total_score / total_weight if total_weight > 0 else 0.0
        
    def _calculate_criteria_score(
        self, 
        criteria: MatchingCriteria, 
        profile1: Dict[str, Any], 
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate score for a specific matching criteria"""
        
        if criteria == MatchingCriteria.AUDIENCE_OVERLAP:
            # Simple audience overlap calculation
            audience1 = set(profile1.get("audience_interests", []))
            audience2 = set(profile2.get("audience_interests", []))
            if not audience1 or not audience2:
                return 0.5
            intersection = len(audience1.intersection(audience2))
            union = len(audience1.union(audience2))
            return intersection / union if union > 0 else 0.0
            
        elif criteria == MatchingCriteria.CONTENT_STYLE:
            # Content style similarity
            style1 = profile1.get("content_style", [])
            style2 = profile2.get("content_style", [])
            if not style1 or not style2:
                return 0.5
            common_styles = len(set(style1).intersection(set(style2)))
            total_styles = len(set(style1).union(set(style2)))
            return common_styles / total_styles if total_styles > 0 else 0.0
            
        elif criteria == MatchingCriteria.ENGAGEMENT_RATE:
            # Similar engagement rates are better for collaboration
            rate1 = profile1.get("engagement_rate", 0.05)
            rate2 = profile2.get("engagement_rate", 0.05)
            diff = abs(rate1 - rate2)
            return max(0.0, 1.0 - (diff * 10))  # Penalize large differences
            
        elif criteria == MatchingCriteria.NICHE_COMPATIBILITY:
            # Niche compatibility
            niche1 = profile1.get("primary_niche", "")
            niche2 = profile2.get("primary_niche", "")
            if niche1 == niche2:
                return 1.0
            elif niche1 in profile2.get("secondary_niches", []) or niche2 in profile1.get("secondary_niches", []):
                return 0.7
            else:
                return 0.3
                
        elif criteria == MatchingCriteria.PLATFORM_PRESENCE:
            # Shared platform presence
            platforms1 = set(profile1.get("platforms", []))
            platforms2 = set(profile2.get("platforms", []))
            if not platforms1 or not platforms2:
                return 0.0
            shared = len(platforms1.intersection(platforms2))
            total = len(platforms1.union(platforms2))
            return shared / total if total > 0 else 0.0
            
        return 0.5  # Default score for unknown criteria
        
    def is_collaboration_allowed(
        self, 
        creator1_tier: CreatorTier, 
        creator2_tier: CreatorTier,
        collaboration_type: CollaborationType
    ) -> bool:
        """Check if collaboration is allowed between creator tiers"""
        config = self.get_collaboration_config(collaboration_type)
        if not config:
            return True
            
        tier_values = {
            CreatorTier.NANO: 1,
            CreatorTier.MICRO: 2,
            CreatorTier.MACRO: 3,
            CreatorTier.MEGA: 4,
            CreatorTier.CELEBRITY: 5
        }
        
        min_tier_value = tier_values[config.min_creator_tier]
        max_tier_value = tier_values[config.max_creator_tier]
        
        tier1_value = tier_values[creator1_tier]
        tier2_value = tier_values[creator2_tier]
        
        return (min_tier_value <= tier1_value <= max_tier_value and 
                min_tier_value <= tier2_value <= max_tier_value)
        
    def get_contract_template(self, collaboration_type: CollaborationType) -> str:
        """Get contract template for collaboration type"""
        config = self.get_collaboration_config(collaboration_type)
        return config.contract_template if config else "standard"
        
    def get_content_quality_standards(self, content_type: str) -> Dict[str, Any]:
        """Get quality standards for content type"""
        return self.content_config.quality_standards.get(content_type, {})
        
    def validate_collaboration_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a collaboration proposal"""
        collaboration_type = CollaborationType(proposal.get("type"))
        config = self.get_collaboration_config(collaboration_type)
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not config:
            validation_result["errors"].append("Invalid collaboration type")
            validation_result["valid"] = False
            return validation_result
            
        # Check creator tier compatibility
        creator1_tier = CreatorTier(proposal.get("creator1_tier"))
        creator2_tier = CreatorTier(proposal.get("creator2_tier"))
        
        if not self.is_collaboration_allowed(creator1_tier, creator2_tier, collaboration_type):
            validation_result["errors"].append("Creator tiers not compatible for this collaboration type")
            validation_result["valid"] = False
            
        # Check exclusive partnership conflicts
        if config.exclusive_partnership and proposal.get("has_competing_partnerships"):
            validation_result["errors"].append("Exclusive partnership required, but creator has competing partnerships")
            validation_result["valid"] = False
            
        # Check duration
        proposed_duration = proposal.get("duration_days", config.default_duration_days)
        if proposed_duration > config.default_duration_days * 2:
            validation_result["warnings"].append("Proposed duration is significantly longer than typical")
            
        # Check content type support
        content_types = proposal.get("content_types", [])
        for content_type in content_types:
            if content_type not in self.content_config.supported_content_types:
                validation_result["errors"].append(f"Content type '{content_type}' not supported")
                validation_result["valid"] = False
                
        return validation_result
        
    def get_collaboration_recommendations(self, creator_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get collaboration recommendations for a creator"""
        recommendations = []
        
        creator_tier = CreatorTier(creator_profile.get("tier", "nano"))
        primary_niche = creator_profile.get("primary_niche", "")
        platforms = creator_profile.get("platforms", [])
        
        # Recommend based on creator tier and niche
        if creator_tier in [CreatorTier.NANO, CreatorTier.MICRO]:
            recommendations.extend([
                {
                    "type": CollaborationType.CROSS_PROMOTION.value,
                    "reason": "Great for growing your audience",
                    "expected_benefit": "20-50% audience growth"
                },
                {
                    "type": CollaborationType.SKILL_EXCHANGE.value,
                    "reason": "Learn new skills from other creators",
                    "expected_benefit": "Skill development and networking"
                }
            ])
            
        if creator_tier in [CreatorTier.MACRO, CreatorTier.MEGA]:
            recommendations.extend([
                {
                    "type": CollaborationType.REVENUE_SHARE.value,
                    "reason": "Monetize your influence effectively",
                    "expected_benefit": "Significant revenue potential"
                },
                {
                    "type": CollaborationType.JOINT_CAMPAIGN.value,
                    "reason": "Perfect for brand campaigns",
                    "expected_benefit": "High-value partnerships"
                }
            ])
            
        # Platform-specific recommendations
        if "youtube" in platforms and "tiktok" in platforms:
            recommendations.append({
                "type": CollaborationType.CONTENT_CREATION.value,
                "reason": "Cross-platform content creation",
                "expected_benefit": "Maximize content reach"
            })
            
        return recommendations[:5]  # Return top 5 recommendations
        
    def export_config(self, output_path: str):
        """Export configuration to JSON file"""
        config_data = {
            "collaboration_configs": {
                collab_type.value: {
                    "collaboration_type": config.collaboration_type.value,
                    "min_creator_tier": config.min_creator_tier.value,
                    "max_creator_tier": config.max_creator_tier.value,
                    "revenue_share_model": config.revenue_share_model.value,
                    "default_duration_days": config.default_duration_days,
                    "approval_required": config.approval_required,
                    "auto_matching_enabled": config.auto_matching_enabled,
                    "cross_platform_allowed": config.cross_platform_allowed,
                    "exclusive_partnership": config.exclusive_partnership,
                    "contract_template": config.contract_template
                }
                for collab_type, config in self.collaboration_configs.items()
            },
            "revenue_share_configs": {
                model.value: {
                    "model": config.model.value,
                    "primary_creator_percentage": config.primary_creator_percentage,
                    "secondary_creator_percentage": config.secondary_creator_percentage,
                    "platform_fee_percentage": config.platform_fee_percentage,
                    "minimum_payout_threshold": config.minimum_payout_threshold,
                    "payment_schedule": config.payment_schedule,
                    "currency": config.currency,
                    "tax_handling": config.tax_handling,
                    "payment_methods": config.payment_methods
                }
                for model, config in self.revenue_share_configs.items()
            },
            "matching_config": {
                "enabled_criteria": [criteria.value for criteria in self.matching_config.enabled_criteria],
                "weight_factors": {criteria.value: weight for criteria, weight in self.matching_config.weight_factors.items()},
                "minimum_match_score": self.matching_config.minimum_match_score,
                "max_suggestions_per_creator": self.matching_config.max_suggestions_per_creator,
                "refresh_interval_hours": self.matching_config.refresh_interval_hours,
                "exclude_recent_collaborators": self.matching_config.exclude_recent_collaborators,
                "exclude_competitors": self.matching_config.exclude_competitors,
                "geographic_radius_km": self.matching_config.geographic_radius_km
            },
            "workflow_config": {
                "proposal_auto_approval": self.workflow_config.proposal_auto_approval,
                "proposal_expiry_days": self.workflow_config.proposal_expiry_days,
                "contract_generation_auto": self.workflow_config.contract_generation_auto,
                "content_approval_required": self.workflow_config.content_approval_required,
                "performance_tracking_enabled": self.workflow_config.performance_tracking_enabled,
                "dispute_resolution_process": self.workflow_config.dispute_resolution_process,
                "feedback_collection_enabled": self.workflow_config.feedback_collection_enabled,
                "rating_system_enabled": self.workflow_config.rating_system_enabled
            },
            "content_config": {
                "supported_content_types": self.content_config.supported_content_types,
                "quality_standards": self.content_config.quality_standards,
                "brand_safety_checks": self.content_config.brand_safety_checks,
                "content_moderation_level": self.content_config.content_moderation_level,
                "attribution_requirements": self.content_config.attribution_requirements,
                "cross_posting_allowed": self.content_config.cross_posting_allowed,
                "exclusive_content_premium": self.content_config.exclusive_content_premium
            },
            "communication_config": {
                "in_platform_messaging": self.communication_config.in_platform_messaging,
                "external_communication_allowed": self.communication_config.external_communication_allowed,
                "auto_introduction_enabled": self.communication_config.auto_introduction_enabled,
                "collaboration_channels": self.communication_config.collaboration_channels,
                "language_matching_preferred": self.communication_config.language_matching_preferred,
                "timezone_consideration": self.communication_config.timezone_consideration,
                "response_time_sla_hours": self.communication_config.response_time_sla_hours
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

# Global instance
collaboration_configs = CollaborationConfigs()

# Environment-based configuration loading
config_file = os.getenv('COLLABORATION_CONFIG_FILE')
if config_file and os.path.exists(config_file):
    # Load custom configuration logic would go here
    pass

# Export configuration for external use
def get_collaboration_configs() -> CollaborationConfigs:
    """Get the global collaboration configurations instance"""
    return collaboration_configs

def calculate_revenue_split(total_revenue: float, model: RevenueShareModel, performance_metrics: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """Calculate revenue split for collaboration"""
    return collaboration_configs.calculate_revenue_split(total_revenue, model, performance_metrics)

def get_creator_match_score(creator1_profile: Dict[str, Any], creator2_profile: Dict[str, Any]) -> float:
    """Calculate compatibility score between creators"""
    return collaboration_configs.calculate_match_score(creator1_profile, creator2_profile)

def validate_collaboration(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """Validate collaboration proposal"""
    return collaboration_configs.validate_collaboration_proposal(proposal)

def get_collaboration_recommendations(creator_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get collaboration recommendations for creator"""
    return collaboration_configs.get_collaboration_recommendations(creator_profile)