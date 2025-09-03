"""Tier Manager - Gestion des tiers
=================================

Tier management system for categorizing content creators into different
tiers based on their performance, achievements, and engagement metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal


class TierLevel(str, Enum):
    """Available tier levels in the system."""
    NEWCOMER = "newcomer"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"


class TierMetric(str, Enum):
    """Metrics used for tier calculation."""
    TOTAL_UPLOADS = "total_uploads"
    TOTAL_VIEWS = "total_views"
    FOLLOWER_COUNT = "follower_count"
    COLLABORATION_COUNT = "collaboration_count"
    ACHIEVEMENT_POINTS = "achievement_points"
    QUALITY_SCORE = "quality_score"
    ENGAGEMENT_RATE = "engagement_rate"
    REVENUE_GENERATED = "revenue_generated"
    CONSISTENCY_SCORE = "consistency_score"


@dataclass
class TierRequirement:
    """Requirement for achieving a tier."""
    metric: TierMetric
    min_value: Union[int, float]
    weight: float = 1.0
    is_required: bool = True


@dataclass
class TierBenefit:
    """Benefit provided by a tier."""
    name: str
    description: str
    benefit_type: str  # "multiplier", "access", "feature", etc.
    value: Union[int, float, str, Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tier:
    """Tier definition."""
    level: TierLevel
    name: str
    description: str
    requirements: List[TierRequirement]
    benefits: List[TierBenefit]
    min_score: float
    icon_url: str
    color_scheme: Dict[str, str] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class UserTierProgress:
    """User's tier progression tracking."""
    user_id: str
    current_tier: TierLevel
    tier_score: float
    next_tier: Optional[TierLevel] = None
    progress_to_next: float = 0.0
    metrics: Dict[TierMetric, Union[int, float]] = field(default_factory=dict)
    tier_history: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tier_locked_until: Optional[datetime] = None


class TierManager:
    """
    Comprehensive tier management system providing intelligent tier
    calculation, progression tracking, and benefit management.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the tier manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.tiers: Dict[TierLevel, Tier] = {}
        self.user_progress: Dict[str, UserTierProgress] = {}
        
        # Initialize tier system
        self._initialize_tier_structure()
        
        self.logger.info("TierManager initialized")
    
    def _initialize_tier_structure(self):
        """Initialize the tier structure with requirements and benefits."""
        try:
            # Newcomer Tier
            self.tiers[TierLevel.NEWCOMER] = Tier(
                level=TierLevel.NEWCOMER,
                name="Newcomer",
                description="Welcome to the platform! Start your creator journey.",
                requirements=[],  # No requirements for newcomer
                benefits=[
                    TierBenefit("Welcome Bonus", "10% XP bonus for first month", "multiplier", 1.1),
                    TierBenefit("Basic Support", "Access to basic creator tools", "access", "basic_tools")
                ],
                min_score=0.0,
                icon_url="/tiers/newcomer.svg",
                color_scheme={"primary": "#9E9E9E", "secondary": "#E0E0E0"}
            )
            
            # Bronze Tier
            self.tiers[TierLevel.BRONZE] = Tier(
                level=TierLevel.BRONZE,
                name="Bronze Creator",
                description="You're getting started! Keep creating great content.",
                requirements=[
                    TierRequirement(TierMetric.TOTAL_UPLOADS, 5, 2.0),
                    TierRequirement(TierMetric.TOTAL_VIEWS, 1000, 1.5),
                    TierRequirement(TierMetric.ACHIEVEMENT_POINTS, 100, 1.0)
                ],
                benefits=[
                    TierBenefit("Creator Badge", "Bronze creator badge", "badge", "bronze_creator"),
                    TierBenefit("Analytics Access", "Basic analytics dashboard", "access", "basic_analytics"),
                    TierBenefit("Reward Boost", "5% reward bonus", "multiplier", 1.05)
                ],
                min_score=100.0,
                icon_url="/tiers/bronze.svg",
                color_scheme={"primary": "#CD7F32", "secondary": "#DAA520"}
            )
            
            # Silver Tier
            self.tiers[TierLevel.SILVER] = Tier(
                level=TierLevel.SILVER,
                name="Silver Creator",
                description="Great progress! You're building a solid presence.",
                requirements=[
                    TierRequirement(TierMetric.TOTAL_UPLOADS, 25, 2.0),
                    TierRequirement(TierMetric.TOTAL_VIEWS, 10000, 1.5),
                    TierRequirement(TierMetric.FOLLOWER_COUNT, 100, 1.5),
                    TierRequirement(TierMetric.ACHIEVEMENT_POINTS, 500, 1.0),
                    TierRequirement(TierMetric.QUALITY_SCORE, 0.7, 1.5)
                ],
                benefits=[
                    TierBenefit("Silver Badge", "Silver creator badge", "badge", "silver_creator"),
                    TierBenefit("Advanced Analytics", "Advanced analytics access", "access", "advanced_analytics"),
                    TierBenefit("Collaboration Tools", "Enhanced collaboration features", "feature", "collaboration_tools"),
                    TierBenefit("Reward Boost", "10% reward bonus", "multiplier", 1.10)
                ],
                min_score=500.0,
                icon_url="/tiers/silver.svg",
                color_scheme={"primary": "#C0C0C0", "secondary": "#E5E5E5"}
            )
            
            # Gold Tier
            self.tiers[TierLevel.GOLD] = Tier(
                level=TierLevel.GOLD,
                name="Gold Creator",
                description="Impressive! You're a recognized creator in the community.",
                requirements=[
                    TierRequirement(TierMetric.TOTAL_UPLOADS, 100, 2.0),
                    TierRequirement(TierMetric.TOTAL_VIEWS, 100000, 2.0),
                    TierRequirement(TierMetric.FOLLOWER_COUNT, 1000, 1.5),
                    TierRequirement(TierMetric.COLLABORATION_COUNT, 5, 1.0),
                    TierRequirement(TierMetric.ACHIEVEMENT_POINTS, 2000, 1.0),
                    TierRequirement(TierMetric.QUALITY_SCORE, 0.8, 2.0),
                    TierRequirement(TierMetric.ENGAGEMENT_RATE, 0.05, 1.5)
                ],
                benefits=[
                    TierBenefit("Gold Badge", "Gold creator badge", "badge", "gold_creator"),
                    TierBenefit("Premium Features", "Access to premium features", "access", "premium_features"),
                    TierBenefit("Priority Support", "Priority customer support", "access", "priority_support"),
                    TierBenefit("Revenue Share", "Better revenue share rates", "multiplier", 1.15),
                    TierBenefit("Reward Boost", "20% reward bonus", "multiplier", 1.20)
                ],
                min_score=1500.0,
                icon_url="/tiers/gold.svg",
                color_scheme={"primary": "#FFD700", "secondary": "#FFF8DC"}
            )
            
            # Platinum Tier
            self.tiers[TierLevel.PLATINUM] = Tier(
                level=TierLevel.PLATINUM,
                name="Platinum Creator",
                description="Outstanding! You're among the top creators on the platform.",
                requirements=[
                    TierRequirement(TierMetric.TOTAL_UPLOADS, 500, 2.0),
                    TierRequirement(TierMetric.TOTAL_VIEWS, 1000000, 2.5),
                    TierRequirement(TierMetric.FOLLOWER_COUNT, 10000, 2.0),
                    TierRequirement(TierMetric.COLLABORATION_COUNT, 20, 1.5),
                    TierRequirement(TierMetric.ACHIEVEMENT_POINTS, 5000, 1.0),
                    TierRequirement(TierMetric.QUALITY_SCORE, 0.85, 2.0),
                    TierRequirement(TierMetric.ENGAGEMENT_RATE, 0.08, 2.0),
                    TierRequirement(TierMetric.CONSISTENCY_SCORE, 0.8, 1.5)
                ],
                benefits=[
                    TierBenefit("Platinum Badge", "Platinum creator badge", "badge", "platinum_creator"),
                    TierBenefit("Exclusive Events", "Access to exclusive creator events", "access", "exclusive_events"),
                    TierBenefit("Advanced Tools", "Professional creator tools", "feature", "pro_tools"),
                    TierBenefit("Revenue Share", "Premium revenue share rates", "multiplier", 1.25),
                    TierBenefit("Reward Boost", "30% reward bonus", "multiplier", 1.30),
                    TierBenefit("Custom Features", "Request custom features", "access", "custom_features")
                ],
                min_score=5000.0,
                icon_url="/tiers/platinum.svg",
                color_scheme={"primary": "#E5E4E2", "secondary": "#F8F8FF"}
            )
            
            # Diamond Tier
            self.tiers[TierLevel.DIAMOND] = Tier(
                level=TierLevel.DIAMOND,
                name="Diamond Creator",
                description="Exceptional! You're setting the standard for creators.",
                requirements=[
                    TierRequirement(TierMetric.TOTAL_UPLOADS, 1000, 2.0),
                    TierRequirement(TierMetric.TOTAL_VIEWS, 10000000, 3.0),
                    TierRequirement(TierMetric.FOLLOWER_COUNT, 100000, 2.5),
                    TierRequirement(TierMetric.COLLABORATION_COUNT, 50, 2.0),
                    TierRequirement(TierMetric.ACHIEVEMENT_POINTS, 15000, 1.0),
                    TierRequirement(TierMetric.QUALITY_SCORE, 0.9, 2.5),
                    TierRequirement(TierMetric.ENGAGEMENT_RATE, 0.12, 2.5),
                    TierRequirement(TierMetric.CONSISTENCY_SCORE, 0.9, 2.0),
                    TierRequirement(TierMetric.REVENUE_GENERATED, 10000, 1.5)
                ],
                benefits=[
                    TierBenefit("Diamond Badge", "Diamond creator badge", "badge", "diamond_creator"),
                    TierBenefit("VIP Treatment", "VIP creator treatment", "access", "vip_treatment"),
                    TierBenefit("Revenue Share", "Top-tier revenue share", "multiplier", 1.40),
                    TierBenefit("Reward Boost", "50% reward bonus", "multiplier", 1.50),
                    TierBenefit("Direct Contact", "Direct contact with platform team", "access", "direct_contact"),
                    TierBenefit("Beta Access", "Early access to new features", "access", "beta_features")
                ],
                min_score=15000.0,
                icon_url="/tiers/diamond.svg",
                color_scheme={"primary": "#B9F2FF", "secondary": "#E0FFFF"}
            )
            
            # Legendary Tier
            self.tiers[TierLevel.LEGENDARY] = Tier(
                level=TierLevel.LEGENDARY,
                name="Legendary Creator",
                description="Legendary status! You're a platform icon and inspiration.",
                requirements=[
                    TierRequirement(TierMetric.TOTAL_UPLOADS, 2000, 2.0),
                    TierRequirement(TierMetric.TOTAL_VIEWS, 50000000, 3.0),
                    TierRequirement(TierMetric.FOLLOWER_COUNT, 500000, 3.0),
                    TierRequirement(TierMetric.COLLABORATION_COUNT, 100, 2.0),
                    TierRequirement(TierMetric.ACHIEVEMENT_POINTS, 50000, 1.5),
                    TierRequirement(TierMetric.QUALITY_SCORE, 0.95, 3.0),
                    TierRequirement(TierMetric.ENGAGEMENT_RATE, 0.15, 3.0),
                    TierRequirement(TierMetric.CONSISTENCY_SCORE, 0.95, 2.5),
                    TierRequirement(TierMetric.REVENUE_GENERATED, 100000, 2.0)
                ],
                benefits=[
                    TierBenefit("Legendary Badge", "Legendary creator badge", "badge", "legendary_creator"),
                    TierBenefit("Platform Partner", "Official platform partnership", "access", "partnership"),
                    TierBenefit("Revenue Share", "Maximum revenue share", "multiplier", 1.60),
                    TierBenefit("Reward Boost", "100% reward bonus", "multiplier", 2.00),
                    TierBenefit("Advisory Role", "Platform advisory opportunities", "access", "advisory_role"),
                    TierBenefit("Custom Benefits", "Personalized tier benefits", "custom", "personalized")
                ],
                min_score=50000.0,
                icon_url="/tiers/legendary.svg",
                color_scheme={"primary": "#FFD700", "secondary": "#FF6B35", "accent": "#9D4EDD"}
            )
            
            self.logger.info(f"Initialized {len(self.tiers)} tier levels")
            
        except Exception as e:
            self.logger.error(f"Error initializing tier structure: {e}")
    
    async def update_user_metrics(
        self,
        user_id: str,
        metrics: Dict[TierMetric, Union[int, float]]
    ) -> Dict[str, Any]:
        """Update user metrics and recalculate tier."""
        try:
            # Get current progress
            progress = self.user_progress.get(user_id)
            if not progress:
                progress = UserTierProgress(
                    user_id=user_id,
                    current_tier=TierLevel.NEWCOMER,
                    tier_score=0.0,
                    metrics={}
                )
                self.user_progress[user_id] = progress
            
            # Update metrics
            for metric, value in metrics.items():
                progress.metrics[metric] = value
            
            # Recalculate tier
            new_tier_data = await self._calculate_user_tier(user_id)
            
            # Check for tier change
            tier_change = None
            if new_tier_data["tier"] != progress.current_tier:
                # Record tier change
                tier_change = {
                    "from_tier": progress.current_tier,
                    "to_tier": new_tier_data["tier"],
                    "timestamp": datetime.now(timezone.utc),
                    "trigger_metrics": metrics
                }
                
                progress.tier_history.append(tier_change)
                progress.current_tier = new_tier_data["tier"]
                
                self.logger.info(f"🎯 User {user_id} tier change: {tier_change['from_tier']} → {tier_change['to_tier']}")
            
            # Update progress
            progress.tier_score = new_tier_data["score"]
            progress.next_tier = new_tier_data["next_tier"]
            progress.progress_to_next = new_tier_data["progress_to_next"]
            progress.last_updated = datetime.now(timezone.utc)
            
            return {
                "user_id": user_id,
                "current_tier": progress.current_tier,
                "tier_score": progress.tier_score,
                "tier_change": tier_change,
                "next_tier": progress.next_tier,
                "progress_to_next": progress.progress_to_next
            }
            
        except Exception as e:
            self.logger.error(f"Error updating user metrics: {e}")
            return {}
    
    async def _calculate_user_tier(self, user_id: str) -> Dict[str, Any]:
        """Calculate user's current tier based on metrics."""
        try:
            progress = self.user_progress.get(user_id)
            if not progress:
                return {"tier": TierLevel.NEWCOMER, "score": 0.0, "next_tier": TierLevel.BRONZE, "progress_to_next": 0.0}
            
            user_metrics = progress.metrics
            max_score = 0.0
            qualified_tier = TierLevel.NEWCOMER
            
            # Check each tier starting from highest
            tier_levels = list(reversed(list(TierLevel)))
            
            for tier_level in tier_levels:
                tier = self.tiers[tier_level]
                score = await self._calculate_tier_score(user_metrics, tier.requirements)
                
                if score >= tier.min_score and await self._check_tier_requirements(user_metrics, tier.requirements):
                    qualified_tier = tier_level
                    max_score = score
                    break
            
            # Calculate next tier and progress
            next_tier = None
            progress_to_next = 0.0
            
            current_tier_index = list(TierLevel).index(qualified_tier)
            if current_tier_index < len(TierLevel) - 1:
                next_tier_level = list(TierLevel)[current_tier_index + 1]
                next_tier = next_tier_level
                next_tier_obj = self.tiers[next_tier_level]
                
                # Calculate progress to next tier
                next_tier_score = await self._calculate_tier_score(user_metrics, next_tier_obj.requirements)
                progress_to_next = min((next_tier_score / next_tier_obj.min_score) * 100, 100.0)
            
            return {
                "tier": qualified_tier,
                "score": max_score,
                "next_tier": next_tier,
                "progress_to_next": progress_to_next
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating user tier: {e}")
            return {"tier": TierLevel.NEWCOMER, "score": 0.0, "next_tier": None, "progress_to_next": 0.0}
    
    async def _calculate_tier_score(
        self,
        user_metrics: Dict[TierMetric, Union[int, float]],
        requirements: List[TierRequirement]
    ) -> float:
        """Calculate tier score based on user metrics and requirements."""
        try:
            total_score = 0.0
            
            for requirement in requirements:
                metric_value = user_metrics.get(requirement.metric, 0)
                
                # Calculate score contribution
                if requirement.min_value > 0:
                    score_ratio = min(metric_value / requirement.min_value, 2.0)  # Cap at 2x
                    contribution = score_ratio * requirement.weight * 100
                    total_score += contribution
            
            return total_score
            
        except Exception as e:
            self.logger.error(f"Error calculating tier score: {e}")
            return 0.0
    
    async def _check_tier_requirements(
        self,
        user_metrics: Dict[TierMetric, Union[int, float]],
        requirements: List[TierRequirement]
    ) -> bool:
        """Check if user meets all required tier requirements."""
        try:
            for requirement in requirements:
                if requirement.is_required:
                    metric_value = user_metrics.get(requirement.metric, 0)
                    if metric_value < requirement.min_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking tier requirements: {e}")
            return False
    
    async def check_tier_progression(
        self,
        user_id: str,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Check for tier progression and return any tier changes."""
        try:
            if not user_profile:
                return []
            
            # Extract metrics from user profile
            metrics = {}
            metrics[TierMetric.TOTAL_UPLOADS] = user_profile.get("total_uploads", 0)
            metrics[TierMetric.TOTAL_VIEWS] = user_profile.get("total_views", 0)
            metrics[TierMetric.FOLLOWER_COUNT] = user_profile.get("follower_count", 0)
            metrics[TierMetric.COLLABORATION_COUNT] = user_profile.get("collaboration_count", 0)
            metrics[TierMetric.ACHIEVEMENT_POINTS] = user_profile.get("achievement_points", 0)
            metrics[TierMetric.QUALITY_SCORE] = user_profile.get("quality_score", 0.0)
            metrics[TierMetric.ENGAGEMENT_RATE] = user_profile.get("engagement_rate", 0.0)
            metrics[TierMetric.REVENUE_GENERATED] = user_profile.get("revenue_generated", 0.0)
            metrics[TierMetric.CONSISTENCY_SCORE] = user_profile.get("consistency_score", 0.0)
            
            # Update metrics and check for changes
            result = await self.update_user_metrics(user_id, metrics)
            
            if result.get("tier_change"):
                return [{
                    "type": "tier_promotion",
                    "from_tier": result["tier_change"]["from_tier"],
                    "to_tier": result["tier_change"]["to_tier"],
                    "benefits": await self.get_tier_benefits(result["tier_change"]["to_tier"])
                }]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error checking tier progression: {e}")
            return []
    
    async def get_tier_benefits(self, tier_level: TierLevel) -> List[Dict[str, Any]]:
        """Get benefits for a specific tier."""
        try:
            tier = self.tiers.get(tier_level)
            if not tier:
                return []
            
            return [
                {
                    "name": benefit.name,
                    "description": benefit.description,
                    "benefit_type": benefit.benefit_type,
                    "value": benefit.value,
                    "metadata": benefit.metadata
                }
                for benefit in tier.benefits
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting tier benefits: {e}")
            return []
    
    async def get_user_tier_info(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive tier information for a user."""
        try:
            progress = self.user_progress.get(user_id)
            if not progress:
                return {
                    "current_tier": TierLevel.NEWCOMER,
                    "tier_score": 0.0,
                    "next_tier": TierLevel.BRONZE,
                    "progress_to_next": 0.0,
                    "benefits": [],
                    "tier_history": []
                }
            
            current_tier_obj = self.tiers[progress.current_tier]
            
            return {
                "current_tier": progress.current_tier,
                "tier_name": current_tier_obj.name,
                "tier_description": current_tier_obj.description,
                "tier_score": progress.tier_score,
                "next_tier": progress.next_tier,
                "progress_to_next": progress.progress_to_next,
                "benefits": await self.get_tier_benefits(progress.current_tier),
                "tier_history": progress.tier_history[-5:],  # Last 5 tier changes
                "icon_url": current_tier_obj.icon_url,
                "color_scheme": current_tier_obj.color_scheme,
                "metrics": progress.metrics,
                "last_updated": progress.last_updated.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user tier info: {e}")
            return {}
    
    async def get_available_tiers(self) -> List[Dict[str, Any]]:
        """Get list of all available tiers."""
        try:
            return [
                {
                    "level": tier.level,
                    "name": tier.name,
                    "description": tier.description,
                    "min_score": tier.min_score,
                    "icon_url": tier.icon_url,
                    "color_scheme": tier.color_scheme,
                    "requirements": [
                        {
                            "metric": req.metric,
                            "min_value": req.min_value,
                            "weight": req.weight,
                            "is_required": req.is_required
                        }
                        for req in tier.requirements
                    ],
                    "benefits": [
                        {
                            "name": benefit.name,
                            "description": benefit.description,
                            "benefit_type": benefit.benefit_type,
                            "value": benefit.value
                        }
                        for benefit in tier.benefits
                    ]
                }
                for tier in self.tiers.values()
                if tier.is_active
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting available tiers: {e}")
            return []


# Global instance
_tier_manager = None

def get_tier_manager(database_connection=None, cache_client=None) -> TierManager:
    """Get the global tier manager instance."""
    global _tier_manager
    if _tier_manager is None:
        _tier_manager = TierManager(database_connection, cache_client)
    return _tier_manager