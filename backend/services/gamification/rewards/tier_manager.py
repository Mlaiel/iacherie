"""Tier Manager - User Tier and Level Management System
===================================================

Advanced tier management system providing user level progression,
tier benefits, tier requirements, and comprehensive tier analytics
for content creator progression and engagement.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/gamification/rewards/tier_manager.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import math

logger = logging.getLogger(__name__)


class TierLevel(str, Enum):
    """User tier levels."""
    NEWCOMER = "newcomer"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"


class BenefitType(str, Enum):
    """Types of tier benefits."""
    POINT_MULTIPLIER = "point_multiplier"
    REVENUE_SHARE = "revenue_share"
    STORAGE_SPACE = "storage_space"
    PRIORITY_SUPPORT = "priority_support"
    FEATURE_ACCESS = "feature_access"
    COLLABORATION_BOOST = "collaboration_boost"
    VISIBILITY_BOOST = "visibility_boost"
    CUSTOM_PROFILE = "custom_profile"
    EARLY_ACCESS = "early_access"
    EXCLUSIVE_CONTENT = "exclusive_content"
    REDUCED_FEES = "reduced_fees"
    PREMIUM_ANALYTICS = "premium_analytics"


@dataclass
class TierBenefit:
    """Individual tier benefit definition."""
    id: str
    name: str
    description: str
    benefit_type: BenefitType
    value: Union[float, int, str, Dict[str, Any]]
    is_permanent: bool = True
    duration_days: Optional[int] = None
    requires_activation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TierDefinition:
    """Tier level definition and requirements."""
    level: TierLevel
    name: str
    description: str
    requirements: Dict[str, Any]
    benefits: List[TierBenefit]
    icon_url: str = ""
    color_scheme: Dict[str, str] = field(default_factory=dict)
    unlock_message: str = ""
    tier_index: int = 0  # 0-based index for progression
    is_active: bool = True


@dataclass
class UserTierProgress:
    """User's tier progression data."""
    user_id: str
    current_tier: TierLevel
    current_level: int = 1
    tier_progress: float = 0.0  # Percentage to next tier
    total_points: float = 0.0
    tier_unlocked_date: datetime = field(default_factory=datetime.utcnow)
    previous_tier: Optional[TierLevel] = None
    tier_upgrade_history: List[Dict[str, Any]] = field(default_factory=list)
    active_benefits: List[str] = field(default_factory=list)
    lifetime_achievements: int = 0
    tier_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TierUpgradeEvent:
    """Tier upgrade event record."""
    id: str
    user_id: str
    from_tier: TierLevel
    to_tier: TierLevel
    trigger_metrics: Dict[str, Any]
    upgrade_timestamp: datetime = field(default_factory=datetime.utcnow)
    benefits_granted: List[str] = field(default_factory=list)
    celebration_shown: bool = False


class TierManager:
    """
    Comprehensive tier and level management system.
    
    Provides user tier progression, tier benefits management,
    tier requirements tracking, and comprehensive tier analytics.
    """
    
    def __init__(self):
        """Initialize the tier manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.initialized = False
        
        # Tier definitions and configuration
        self.tier_definitions: Dict[TierLevel, TierDefinition] = {}
        self.tier_order: List[TierLevel] = []
        
        # User tier tracking
        self.user_progress: Dict[str, UserTierProgress] = {}
        
        # Tier upgrade events
        self.upgrade_events: List[TierUpgradeEvent] = []
        
        # Tier statistics and analytics
        self.tier_statistics: Dict[str, Any] = {}
        
        self.logger.info("TierManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the tier manager with default tier definitions."""
        try:
            # Load default tier definitions
            await self._load_default_tier_definitions()
            
            # Start background tasks
            asyncio.create_task(self._update_tier_statistics())
            asyncio.create_task(self._cleanup_expired_benefits())
            
            self.initialized = True
            self.logger.info(f"✅ TierManager initialized with {len(self.tier_definitions)} tiers")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize TierManager: {e}")
            return False
    
    async def _load_default_tier_definitions(self):
        """Load default tier definitions and progression system."""
        
        # Define tier progression order
        self.tier_order = [
            TierLevel.NEWCOMER,
            TierLevel.BEGINNER,
            TierLevel.INTERMEDIATE,
            TierLevel.ADVANCED,
            TierLevel.EXPERT,
            TierLevel.MASTER,
            TierLevel.LEGENDARY,
            TierLevel.MYTHICAL
        ]
        
        # Define default tiers
        default_tiers = [
            # NEWCOMER TIER
            TierDefinition(
                level=TierLevel.NEWCOMER,
                name="Newcomer",
                description="Welcome to the platform! Start your journey as a content creator.",
                requirements={
                    "total_points": 0,
                    "content_uploads": 0,
                    "days_active": 0
                },
                benefits=[
                    TierBenefit(
                        id="newcomer_welcome",
                        name="Welcome Package",
                        description="Basic platform access and welcome resources",
                        benefit_type=BenefitType.STORAGE_SPACE,
                        value={"amount": 1, "unit": "GB"}
                    ),
                    TierBenefit(
                        id="newcomer_support",
                        name="Community Support",
                        description="Access to community forums and basic support",
                        benefit_type=BenefitType.FEATURE_ACCESS,
                        value={"features": ["community_forum", "basic_support"]}
                    )
                ],
                icon_url="/tiers/newcomer.svg",
                color_scheme={"primary": "#9E9E9E", "secondary": "#757575"},
                unlock_message="Welcome to the platform! Your journey begins now.",
                tier_index=0
            ),
            
            # BEGINNER TIER
            TierDefinition(
                level=TierLevel.BEGINNER,
                name="Beginner",
                description="You're getting started! Keep creating and engaging.",
                requirements={
                    "total_points": 100,
                    "content_uploads": 3,
                    "days_active": 3
                },
                benefits=[
                    TierBenefit(
                        id="beginner_storage",
                        name="Increased Storage",
                        description="Additional storage space for your content",
                        benefit_type=BenefitType.STORAGE_SPACE,
                        value={"amount": 2, "unit": "GB"}
                    ),
                    TierBenefit(
                        id="beginner_multiplier",
                        name="Point Bonus",
                        description="5% bonus on all points earned",
                        benefit_type=BenefitType.POINT_MULTIPLIER,
                        value=1.05
                    ),
                    TierBenefit(
                        id="beginner_analytics",
                        name="Basic Analytics",
                        description="Access to basic content analytics",
                        benefit_type=BenefitType.FEATURE_ACCESS,
                        value={"features": ["basic_analytics"]}
                    )
                ],
                icon_url="/tiers/beginner.svg",
                color_scheme={"primary": "#4CAF50", "secondary": "#2E7D32"},
                unlock_message="Great start! You've unlocked Beginner tier benefits.",
                tier_index=1
            ),
            
            # INTERMEDIATE TIER
            TierDefinition(
                level=TierLevel.INTERMEDIATE,
                name="Intermediate",
                description="Making progress! Your skills are developing nicely.",
                requirements={
                    "total_points": 1000,
                    "content_uploads": 15,
                    "days_active": 14,
                    "collaborations": 2
                },
                benefits=[
                    TierBenefit(
                        id="intermediate_storage",
                        name="Enhanced Storage",
                        description="5GB of content storage space",
                        benefit_type=BenefitType.STORAGE_SPACE,
                        value={"amount": 5, "unit": "GB"}
                    ),
                    TierBenefit(
                        id="intermediate_multiplier",
                        name="Point Boost",
                        description="10% bonus on all points earned",
                        benefit_type=BenefitType.POINT_MULTIPLIER,
                        value=1.10
                    ),
                    TierBenefit(
                        id="intermediate_collaboration",
                        name="Collaboration Boost",
                        description="Increased visibility in collaboration matching",
                        benefit_type=BenefitType.COLLABORATION_BOOST,
                        value={"multiplier": 1.2}
                    ),
                    TierBenefit(
                        id="intermediate_revenue",
                        name="Revenue Share Bonus",
                        description="2% additional revenue share",
                        benefit_type=BenefitType.REVENUE_SHARE,
                        value=0.02
                    )
                ],
                icon_url="/tiers/intermediate.svg",
                color_scheme={"primary": "#2196F3", "secondary": "#1565C0"},
                unlock_message="Excellent progress! Welcome to Intermediate tier.",
                tier_index=2
            ),
            
            # ADVANCED TIER
            TierDefinition(
                level=TierLevel.ADVANCED,
                name="Advanced",
                description="You're becoming skilled! Advanced features unlocked.",
                requirements={
                    "total_points": 5000,
                    "content_uploads": 50,
                    "days_active": 30,
                    "collaborations": 10,
                    "average_quality": 0.7
                },
                benefits=[
                    TierBenefit(
                        id="advanced_storage",
                        name="Premium Storage",
                        description="15GB of content storage space",
                        benefit_type=BenefitType.STORAGE_SPACE,
                        value={"amount": 15, "unit": "GB"}
                    ),
                    TierBenefit(
                        id="advanced_multiplier",
                        name="Significant Point Boost",
                        description="20% bonus on all points earned",
                        benefit_type=BenefitType.POINT_MULTIPLIER,
                        value=1.20
                    ),
                    TierBenefit(
                        id="advanced_analytics",
                        name="Advanced Analytics",
                        description="Detailed analytics and insights",
                        benefit_type=BenefitType.PREMIUM_ANALYTICS,
                        value={"level": "advanced"}
                    ),
                    TierBenefit(
                        id="advanced_priority",
                        name="Priority Support",
                        description="Priority customer support access",
                        benefit_type=BenefitType.PRIORITY_SUPPORT,
                        value={"level": "standard"}
                    ),
                    TierBenefit(
                        id="advanced_profile",
                        name="Profile Customization",
                        description="Custom profile themes and layouts",
                        benefit_type=BenefitType.CUSTOM_PROFILE,
                        value={"themes": 5, "layouts": 3}
                    )
                ],
                icon_url="/tiers/advanced.svg",
                color_scheme={"primary": "#FF9800", "secondary": "#E65100"},
                unlock_message="Outstanding! You've reached Advanced tier status.",
                tier_index=3
            ),
            
            # EXPERT TIER
            TierDefinition(
                level=TierLevel.EXPERT,
                name="Expert",
                description="Expert level achieved! You're among the skilled creators.",
                requirements={
                    "total_points": 10000,
                    "content_uploads": 100,
                    "days_active": 60,
                    "collaborations": 25,
                    "average_quality": 0.8,
                    "achievements_unlocked": 15
                },
                benefits=[
                    TierBenefit(
                        id="expert_storage",
                        name="Expert Storage",
                        description="50GB of content storage space",
                        benefit_type=BenefitType.STORAGE_SPACE,
                        value={"amount": 50, "unit": "GB"}
                    ),
                    TierBenefit(
                        id="expert_multiplier",
                        name="Expert Point Multiplier",
                        description="30% bonus on all points earned",
                        benefit_type=BenefitType.POINT_MULTIPLIER,
                        value=1.30
                    ),
                    TierBenefit(
                        id="expert_revenue",
                        name="Enhanced Revenue Share",
                        description="5% additional revenue share",
                        benefit_type=BenefitType.REVENUE_SHARE,
                        value=0.05
                    ),
                    TierBenefit(
                        id="expert_visibility",
                        name="Visibility Boost",
                        description="Enhanced content visibility and discovery",
                        benefit_type=BenefitType.VISIBILITY_BOOST,
                        value={"multiplier": 1.5}
                    ),
                    TierBenefit(
                        id="expert_early_access",
                        name="Early Access",
                        description="Early access to new platform features",
                        benefit_type=BenefitType.EARLY_ACCESS,
                        value={"priority": "high"}
                    ),
                    TierBenefit(
                        id="expert_fees",
                        name="Reduced Platform Fees",
                        description="10% reduction in platform fees",
                        benefit_type=BenefitType.REDUCED_FEES,
                        value=0.10
                    )
                ],
                icon_url="/tiers/expert.svg",
                color_scheme={"primary": "#9C27B0", "secondary": "#6A1B9A"},
                unlock_message="Incredible! You've achieved Expert tier recognition.",
                tier_index=4
            ),
            
            # MASTER TIER
            TierDefinition(
                level=TierLevel.MASTER,
                name="Master",
                description="Master tier! You're a true professional creator.",
                requirements={
                    "total_points": 25000,
                    "content_uploads": 250,
                    "days_active": 120,
                    "collaborations": 50,
                    "average_quality": 0.85,
                    "achievements_unlocked": 30,
                    "revenue_generated": 1000
                },
                benefits=[
                    TierBenefit(
                        id="master_storage",
                        name="Master Storage",
                        description="100GB of content storage space",
                        benefit_type=BenefitType.STORAGE_SPACE,
                        value={"amount": 100, "unit": "GB"}
                    ),
                    TierBenefit(
                        id="master_multiplier",
                        name="Master Point Multiplier",
                        description="50% bonus on all points earned",
                        benefit_type=BenefitType.POINT_MULTIPLIER,
                        value=1.50
                    ),
                    TierBenefit(
                        id="master_revenue",
                        name="Master Revenue Share",
                        description="10% additional revenue share",
                        benefit_type=BenefitType.REVENUE_SHARE,
                        value=0.10
                    ),
                    TierBenefit(
                        id="master_priority",
                        name="Premium Priority Support",
                        description="Highest priority support access",
                        benefit_type=BenefitType.PRIORITY_SUPPORT,
                        value={"level": "premium"}
                    ),
                    TierBenefit(
                        id="master_exclusive",
                        name="Exclusive Content Access",
                        description="Access to exclusive master-tier content and events",
                        benefit_type=BenefitType.EXCLUSIVE_CONTENT,
                        value={"level": "master"}
                    ),
                    TierBenefit(
                        id="master_fees",
                        name="Significant Fee Reduction",
                        description="20% reduction in platform fees",
                        benefit_type=BenefitType.REDUCED_FEES,
                        value=0.20
                    ),
                    TierBenefit(
                        id="master_profile",
                        name="Ultimate Profile Customization",
                        description="Unlimited profile customization options",
                        benefit_type=BenefitType.CUSTOM_PROFILE,
                        value={"unlimited": True}
                    )
                ],
                icon_url="/tiers/master.svg",
                color_scheme={"primary": "#E91E63", "secondary": "#AD1457"},
                unlock_message="Phenomenal! Welcome to the prestigious Master tier.",
                tier_index=5
            ),
            
            # LEGENDARY TIER
            TierDefinition(
                level=TierLevel.LEGENDARY,
                name="Legendary",
                description="Legendary status! You're among the platform elite.",
                requirements={
                    "total_points": 50000,
                    "content_uploads": 500,
                    "days_active": 250,
                    "collaborations": 100,
                    "average_quality": 0.9,
                    "achievements_unlocked": 50,
                    "revenue_generated": 5000,
                    "viral_content": 5
                },
                benefits=[
                    TierBenefit(
                        id="legendary_storage",
                        name="Legendary Storage",
                        description="Unlimited content storage space",
                        benefit_type=BenefitType.STORAGE_SPACE,
                        value={"unlimited": True}
                    ),
                    TierBenefit(
                        id="legendary_multiplier",
                        name="Legendary Point Multiplier",
                        description="100% bonus on all points earned",
                        benefit_type=BenefitType.POINT_MULTIPLIER,
                        value=2.00
                    ),
                    TierBenefit(
                        id="legendary_revenue",
                        name="Legendary Revenue Share",
                        description="15% additional revenue share",
                        benefit_type=BenefitType.REVENUE_SHARE,
                        value=0.15
                    ),
                    TierBenefit(
                        id="legendary_fees",
                        name="Maximum Fee Reduction",
                        description="50% reduction in platform fees",
                        benefit_type=BenefitType.REDUCED_FEES,
                        value=0.50
                    ),
                    TierBenefit(
                        id="legendary_access",
                        name="Exclusive Legendary Access",
                        description="Access to all platform features and exclusive events",
                        benefit_type=BenefitType.EXCLUSIVE_CONTENT,
                        value={"level": "legendary", "all_access": True}
                    ),
                    TierBenefit(
                        id="legendary_visibility",
                        name="Maximum Visibility Boost",
                        description="Maximum content visibility and featured placement",
                        benefit_type=BenefitType.VISIBILITY_BOOST,
                        value={"multiplier": 3.0, "featured": True}
                    )
                ],
                icon_url="/tiers/legendary.svg",
                color_scheme={"primary": "#FFD700", "secondary": "#FFA000"},
                unlock_message="LEGENDARY! You've achieved the highest tier of excellence!",
                tier_index=6
            ),
            
            # MYTHICAL TIER (Special/Invite Only)
            TierDefinition(
                level=TierLevel.MYTHICAL,
                name="Mythical",
                description="Mythical tier - Reserved for extraordinary contributors.",
                requirements={
                    "total_points": 100000,
                    "content_uploads": 1000,
                    "days_active": 365,
                    "collaborations": 200,
                    "average_quality": 0.95,
                    "achievements_unlocked": 75,
                    "revenue_generated": 25000,
                    "viral_content": 20,
                    "community_contributions": 100,
                    "special_invitation": True
                },
                benefits=[
                    TierBenefit(
                        id="mythical_all",
                        name="Mythical Status",
                        description="All platform benefits plus exclusive mythical perks",
                        benefit_type=BenefitType.EXCLUSIVE_CONTENT,
                        value={"mythical": True, "everything": True}
                    ),
                    TierBenefit(
                        id="mythical_multiplier",
                        name="Mythical Point Multiplier",
                        description="150% bonus on all points earned",
                        benefit_type=BenefitType.POINT_MULTIPLIER,
                        value=2.50
                    ),
                    TierBenefit(
                        id="mythical_revenue",
                        name="Mythical Revenue Share",
                        description="25% additional revenue share",
                        benefit_type=BenefitType.REVENUE_SHARE,
                        value=0.25
                    ),
                    TierBenefit(
                        id="mythical_fees",
                        name="No Platform Fees",
                        description="Complete elimination of platform fees",
                        benefit_type=BenefitType.REDUCED_FEES,
                        value=1.00
                    )
                ],
                icon_url="/tiers/mythical.svg",
                color_scheme={"primary": "#AA00FF", "secondary": "#6200EA"},
                unlock_message="MYTHICAL! You've transcended to legendary status!",
                tier_index=7
            )
        ]
        
        # Store tier definitions
        for tier_def in default_tiers:
            self.tier_definitions[tier_def.level] = tier_def
        
        self.logger.info(f"Loaded {len(default_tiers)} tier definitions")
    
    async def check_tier_progression(
        self,
        user_id: str,
        points_earned: float
    ) -> Dict[str, Any]:
        """Check and process tier progression for a user."""
        try:
            # Get or create user progress
            if user_id not in self.user_progress:
                self.user_progress[user_id] = UserTierProgress(
                    user_id=user_id,
                    current_tier=TierLevel.NEWCOMER
                )
            
            user_progress = self.user_progress[user_id]
            
            # Update user metrics
            await self._update_user_metrics(user_id, points_earned)
            
            # Check for tier upgrades
            tier_changes = await self._check_tier_upgrades(user_id)
            
            # Calculate progress to next tier
            next_tier_progress = self._calculate_next_tier_progress(user_id)
            
            return {
                "changes": tier_changes,
                "current_tier": user_progress.current_tier.value,
                "tier_progress": next_tier_progress,
                "total_points": user_progress.total_points,
                "active_benefits": user_progress.active_benefits
            }
            
        except Exception as e:
            self.logger.error(f"Error checking tier progression for user {user_id}: {e}")
            return {"changes": [], "error": str(e)}
    
    async def _update_user_metrics(self, user_id: str, points_earned: float):
        """Update user metrics for tier calculations."""
        user_progress = self.user_progress[user_id]
        
        # Update total points
        user_progress.total_points += points_earned
        
        # This method would integrate with other systems to get comprehensive metrics
        # For now, we'll use placeholder logic
        
        # Update tier metrics (these would come from other systems)
        if "content_uploads" not in user_progress.tier_metrics:
            user_progress.tier_metrics["content_uploads"] = 0
        if "collaborations" not in user_progress.tier_metrics:
            user_progress.tier_metrics["collaborations"] = 0
        if "days_active" not in user_progress.tier_metrics:
            user_progress.tier_metrics["days_active"] = (
                datetime.utcnow() - user_progress.tier_unlocked_date
            ).days
        
        # Placeholder updates based on points (real implementation would get actual data)
        user_progress.tier_metrics["estimated_uploads"] = int(user_progress.total_points / 50)  # Rough estimate
        user_progress.tier_metrics["estimated_collaborations"] = int(user_progress.total_points / 200)
        user_progress.tier_metrics["average_quality"] = min(0.95, 0.5 + (user_progress.total_points / 50000))
    
    async def _check_tier_upgrades(self, user_id: str) -> List[Dict[str, Any]]:
        """Check if user qualifies for tier upgrades."""
        user_progress = self.user_progress[user_id]
        current_tier_index = self.tier_order.index(user_progress.current_tier)
        tier_changes = []
        
        # Check each higher tier
        for i in range(current_tier_index + 1, len(self.tier_order)):
            next_tier = self.tier_order[i]
            tier_def = self.tier_definitions[next_tier]
            
            if self._meets_tier_requirements(user_id, tier_def):
                # User qualifies for upgrade
                old_tier = user_progress.current_tier
                user_progress.previous_tier = old_tier
                user_progress.current_tier = next_tier
                user_progress.tier_unlocked_date = datetime.utcnow()
                
                # Grant tier benefits
                benefits_granted = await self._grant_tier_benefits(user_id, tier_def)
                
                # Create upgrade event
                upgrade_event = TierUpgradeEvent(
                    id=str(uuid4()),
                    user_id=user_id,
                    from_tier=old_tier,
                    to_tier=next_tier,
                    trigger_metrics=user_progress.tier_metrics.copy(),
                    benefits_granted=benefits_granted
                )
                
                self.upgrade_events.append(upgrade_event)
                
                # Add to upgrade history
                user_progress.tier_upgrade_history.append({
                    "from_tier": old_tier.value,
                    "to_tier": next_tier.value,
                    "upgrade_date": datetime.utcnow(),
                    "trigger_points": user_progress.total_points
                })
                
                tier_changes.append({
                    "from_tier": old_tier.value,
                    "to_tier": next_tier.value,
                    "benefits_granted": benefits_granted,
                    "unlock_message": tier_def.unlock_message
                })
                
                self.logger.info(f"🎉 Tier upgrade: {user_id} from {old_tier.value} to {next_tier.value}")
                
                # Continue checking for further upgrades
                current_tier_index = i
            else:
                # Stop at first tier that isn't met
                break
        
        return tier_changes
    
    def _meets_tier_requirements(self, user_id: str, tier_def: TierDefinition) -> bool:
        """Check if user meets all requirements for a tier."""
        try:
            user_progress = self.user_progress[user_id]
            requirements = tier_def.requirements
            metrics = user_progress.tier_metrics
            
            # Check total points requirement
            if user_progress.total_points < requirements.get("total_points", 0):
                return False
            
            # Check other requirements
            for req_key, req_value in requirements.items():
                if req_key == "total_points":
                    continue  # Already checked
                
                if req_key == "special_invitation":
                    # Special invitation requirement (for Mythical tier)
                    if req_value and not metrics.get("has_special_invitation", False):
                        return False
                    continue
                
                # Get metric value (with fallbacks)
                if req_key == "content_uploads":
                    actual_value = metrics.get("content_uploads", metrics.get("estimated_uploads", 0))
                elif req_key == "collaborations":
                    actual_value = metrics.get("collaborations", metrics.get("estimated_collaborations", 0))
                elif req_key == "days_active":
                    actual_value = metrics.get("days_active", 0)
                elif req_key == "achievements_unlocked":
                    actual_value = metrics.get("achievements_unlocked", user_progress.lifetime_achievements)
                elif req_key == "average_quality":
                    actual_value = metrics.get("average_quality", 0.5)
                elif req_key == "revenue_generated":
                    actual_value = metrics.get("revenue_generated", 0)
                elif req_key == "viral_content":
                    actual_value = metrics.get("viral_content", 0)
                elif req_key == "community_contributions":
                    actual_value = metrics.get("community_contributions", 0)
                else:
                    actual_value = metrics.get(req_key, 0)
                
                if actual_value < req_value:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking tier requirements: {e}")
            return False
    
    async def _grant_tier_benefits(self, user_id: str, tier_def: TierDefinition) -> List[str]:
        """Grant tier benefits to user."""
        try:
            user_progress = self.user_progress[user_id]
            benefits_granted = []
            
            for benefit in tier_def.benefits:
                # Add benefit to user's active benefits
                if benefit.id not in user_progress.active_benefits:
                    user_progress.active_benefits.append(benefit.id)
                    benefits_granted.append(benefit.id)
                    
                    # Apply benefit effects (this would integrate with other systems)
                    await self._apply_benefit_effect(user_id, benefit)
            
            return benefits_granted
            
        except Exception as e:
            self.logger.error(f"Error granting tier benefits: {e}")
            return []
    
    async def _apply_benefit_effect(self, user_id: str, benefit: TierBenefit):
        """Apply the effect of a tier benefit."""
        try:
            # This method would integrate with other systems to apply benefits
            # For now, we'll log the benefit application
            
            self.logger.info(f"Applied benefit '{benefit.name}' to user {user_id}")
            
            # Examples of benefit applications:
            # - Point multipliers would be registered with the point system
            # - Storage space would be updated in the storage system
            # - Revenue share would be updated in the monetization system
            # - Feature access would be updated in the feature access system
            
        except Exception as e:
            self.logger.error(f"Error applying benefit effect: {e}")
    
    def _calculate_next_tier_progress(self, user_id: str) -> float:
        """Calculate progress percentage to next tier."""
        try:
            user_progress = self.user_progress[user_id]
            current_tier_index = self.tier_order.index(user_progress.current_tier)
            
            # If already at highest tier
            if current_tier_index >= len(self.tier_order) - 1:
                return 100.0
            
            next_tier = self.tier_order[current_tier_index + 1]
            next_tier_def = self.tier_definitions[next_tier]
            
            current_points = user_progress.total_points
            required_points = next_tier_def.requirements.get("total_points", 0)
            
            if current_tier_index > 0:
                current_tier_def = self.tier_definitions[self.tier_order[current_tier_index]]
                current_tier_points = current_tier_def.requirements.get("total_points", 0)
            else:
                current_tier_points = 0
            
            points_needed = required_points - current_tier_points
            points_progress = current_points - current_tier_points
            
            if points_needed <= 0:
                return 100.0
            
            progress = (points_progress / points_needed) * 100
            return min(100.0, max(0.0, progress))
            
        except Exception as e:
            self.logger.error(f"Error calculating next tier progress: {e}")
            return 0.0
    
    async def get_user_tier(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive tier information for a user."""
        try:
            if user_id not in self.user_progress:
                # Initialize new user at newcomer tier
                self.user_progress[user_id] = UserTierProgress(
                    user_id=user_id,
                    current_tier=TierLevel.NEWCOMER
                )
            
            user_progress = self.user_progress[user_id]
            current_tier_def = self.tier_definitions[user_progress.current_tier]
            
            # Get next tier information
            current_tier_index = self.tier_order.index(user_progress.current_tier)
            next_tier_info = None
            
            if current_tier_index < len(self.tier_order) - 1:
                next_tier = self.tier_order[current_tier_index + 1]
                next_tier_def = self.tier_definitions[next_tier]
                next_tier_info = {
                    "level": next_tier.value,
                    "name": next_tier_def.name,
                    "requirements": next_tier_def.requirements,
                    "benefits_preview": [
                        {
                            "name": benefit.name,
                            "description": benefit.description,
                            "type": benefit.benefit_type.value
                        } for benefit in next_tier_def.benefits[:3]  # Show first 3 benefits
                    ]
                }
            
            # Get active benefits details
            active_benefits_details = []
            for benefit_id in user_progress.active_benefits:
                for tier_def in self.tier_definitions.values():
                    for benefit in tier_def.benefits:
                        if benefit.id == benefit_id:
                            active_benefits_details.append({
                                "id": benefit.id,
                                "name": benefit.name,
                                "description": benefit.description,
                                "type": benefit.benefit_type.value,
                                "value": benefit.value,
                                "tier_source": tier_def.level.value
                            })
                            break
            
            return {
                "user_id": user_id,
                "current_tier": {
                    "level": user_progress.current_tier.value,
                    "name": current_tier_def.name,
                    "description": current_tier_def.description,
                    "icon_url": current_tier_def.icon_url,
                    "color_scheme": current_tier_def.color_scheme,
                    "tier_index": current_tier_def.tier_index
                },
                "next_tier": next_tier_info,
                "progress": {
                    "total_points": user_progress.total_points,
                    "tier_progress": self._calculate_next_tier_progress(user_id),
                    "days_in_tier": (datetime.utcnow() - user_progress.tier_unlocked_date).days,
                    "tier_unlocked_date": user_progress.tier_unlocked_date
                },
                "benefits": {
                    "active_count": len(user_progress.active_benefits),
                    "active_benefits": active_benefits_details,
                    "point_multiplier": self._get_effective_point_multiplier(user_progress),
                    "revenue_bonus": self._get_effective_revenue_bonus(user_progress),
                    "storage_space": self._get_effective_storage_space(user_progress)
                },
                "history": {
                    "previous_tier": user_progress.previous_tier.value if user_progress.previous_tier else None,
                    "upgrade_count": len(user_progress.tier_upgrade_history),
                    "recent_upgrades": user_progress.tier_upgrade_history[-3:]  # Last 3 upgrades
                },
                "statistics": {
                    "lifetime_achievements": user_progress.lifetime_achievements,
                    "tier_metrics": user_progress.tier_metrics
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user tier: {e}")
            return {}
    
    def _get_effective_point_multiplier(self, user_progress: UserTierProgress) -> float:
        """Calculate effective point multiplier from all active benefits."""
        multiplier = 1.0
        
        for benefit_id in user_progress.active_benefits:
            for tier_def in self.tier_definitions.values():
                for benefit in tier_def.benefits:
                    if (benefit.id == benefit_id and 
                        benefit.benefit_type == BenefitType.POINT_MULTIPLIER):
                        multiplier = max(multiplier, float(benefit.value))
                        break
        
        return multiplier
    
    def _get_effective_revenue_bonus(self, user_progress: UserTierProgress) -> float:
        """Calculate effective revenue bonus from all active benefits."""
        bonus = 0.0
        
        for benefit_id in user_progress.active_benefits:
            for tier_def in self.tier_definitions.values():
                for benefit in tier_def.benefits:
                    if (benefit.id == benefit_id and 
                        benefit.benefit_type == BenefitType.REVENUE_SHARE):
                        bonus += float(benefit.value)
                        break
        
        return bonus
    
    def _get_effective_storage_space(self, user_progress: UserTierProgress) -> Dict[str, Any]:
        """Calculate effective storage space from all active benefits."""
        total_gb = 0
        unlimited = False
        
        for benefit_id in user_progress.active_benefits:
            for tier_def in self.tier_definitions.values():
                for benefit in tier_def.benefits:
                    if (benefit.id == benefit_id and 
                        benefit.benefit_type == BenefitType.STORAGE_SPACE):
                        
                        if isinstance(benefit.value, dict):
                            if benefit.value.get("unlimited"):
                                unlimited = True
                            else:
                                total_gb += benefit.value.get("amount", 0)
                        break
        
        return {
            "total_gb": total_gb,
            "unlimited": unlimited,
            "display": "Unlimited" if unlimited else f"{total_gb} GB"
        }
    
    async def _update_tier_statistics(self):
        """Background task to update tier distribution statistics."""
        while True:
            try:
                await asyncio.sleep(300)  # Update every 5 minutes
                
                # Calculate tier distribution
                tier_distribution = {}
                total_users = len(self.user_progress)
                
                for tier_level in TierLevel:
                    count = sum(
                        1 for progress in self.user_progress.values()
                        if progress.current_tier == tier_level
                    )
                    tier_distribution[tier_level.value] = {
                        "count": count,
                        "percentage": (count / total_users * 100) if total_users > 0 else 0
                    }
                
                # Calculate upgrade statistics
                recent_upgrades = len([
                    event for event in self.upgrade_events
                    if event.upgrade_timestamp > datetime.utcnow() - timedelta(days=7)
                ])
                
                # Update statistics
                self.tier_statistics = {
                    "total_users": total_users,
                    "tier_distribution": tier_distribution,
                    "recent_upgrades_7d": recent_upgrades,
                    "total_upgrades": len(self.upgrade_events),
                    "average_tier_index": sum(
                        self.tier_definitions[progress.current_tier].tier_index
                        for progress in self.user_progress.values()
                    ) / total_users if total_users > 0 else 0,
                    "last_updated": datetime.utcnow()
                }
                
            except Exception as e:
                self.logger.error(f"Error updating tier statistics: {e}")
                await asyncio.sleep(600)  # Retry in 10 minutes
    
    async def _cleanup_expired_benefits(self):
        """Background task to cleanup expired temporary benefits."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                current_time = datetime.utcnow()
                total_cleaned = 0
                
                for user_progress in self.user_progress.values():
                    expired_benefits = []
                    
                    for benefit_id in user_progress.active_benefits:
                        # Find benefit definition
                        for tier_def in self.tier_definitions.values():
                            for benefit in tier_def.benefits:
                                if (benefit.id == benefit_id and 
                                    not benefit.is_permanent and
                                    benefit.duration_days):
                                    
                                    # Check if benefit has expired
                                    # (This would need tracking of when benefit was granted)
                                    # For now, we'll skip cleanup of temporary benefits
                                    pass
                    
                    # Remove expired benefits
                    for benefit_id in expired_benefits:
                        user_progress.active_benefits.remove(benefit_id)
                        total_cleaned += 1
                
                if total_cleaned > 0:
                    self.logger.info(f"Cleaned up {total_cleaned} expired tier benefits")
                
            except Exception as e:
                self.logger.error(f"Error in cleanup expired benefits task: {e}")
                await asyncio.sleep(1800)  # Retry in 30 minutes
    
    async def get_tier_statistics(self) -> Dict[str, Any]:
        """Get comprehensive tier system statistics."""
        try:
            stats = self.tier_statistics.copy()
            
            # Add additional statistics
            stats.update({
                "total_tier_definitions": len(self.tier_definitions),
                "total_benefits": sum(len(tier_def.benefits) for tier_def.benefits in self.tier_definitions.values()),
                "active_tier_definitions": len([td for td in self.tier_definitions.values() if td.is_active]),
                "highest_tier_achieved": max(
                    (self.tier_definitions[progress.current_tier].tier_index 
                     for progress in self.user_progress.values()),
                    default=0
                )
            })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting tier statistics: {e}")
            return {}