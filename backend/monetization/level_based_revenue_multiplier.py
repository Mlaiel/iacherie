"""Level-Based Revenue Multiplier - Enterprise Level Progression System
======================================================================

Enterprise-grade level-based revenue multiplier providing automated revenue
scaling based on creator levels, experience points, and progression milestones
with comprehensive tracking and tier-based benefit distribution.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/level_based_revenue_multiplier.py
Business Logic: Experience Tracking → Level Calculation → Multiplier Application → Revenue Enhancement

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import json
import math

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class ExperienceSource(str, Enum):
    """Sources of experience points for level progression."""
    CONTENT_CREATION = "content_creation"
    AUDIENCE_ENGAGEMENT = "audience_engagement"
    REVENUE_GENERATION = "revenue_generation"
    COLLABORATIONS = "collaborations"
    PLATFORM_PARTICIPATION = "platform_participation"
    QUALITY_ACHIEVEMENTS = "quality_achievements"
    COMMUNITY_CONTRIBUTIONS = "community_contributions"
    MILESTONE_COMPLETIONS = "milestone_completions"
    SKILL_DEVELOPMENTS = "skill_developments"
    INNOVATION_ACTIVITIES = "innovation_activities"


class LevelTier(str, Enum):
    """Level tiers with different progression characteristics."""
    NOVICE = "novice"        # Levels 1-10
    INTERMEDIATE = "intermediate"  # Levels 11-25
    ADVANCED = "advanced"    # Levels 26-50
    EXPERT = "expert"        # Levels 51-75
    MASTER = "master"        # Levels 76-100
    GRANDMASTER = "grandmaster"  # Levels 101+


class MultiplierType(str, Enum):
    """Types of revenue multipliers based on level."""
    BASE_REVENUE = "base_revenue"
    ENGAGEMENT_BONUS = "engagement_bonus"
    COLLABORATION_BONUS = "collaboration_bonus"
    QUALITY_PREMIUM = "quality_premium"
    LOYALTY_REWARD = "loyalty_reward"
    ACHIEVEMENT_MULTIPLIER = "achievement_multiplier"
    TIER_BONUS = "tier_bonus"
    PRESTIGE_MULTIPLIER = "prestige_multiplier"


@dataclass
class LevelDefinition:
    """Definition of a level with requirements and benefits."""
    level: int
    tier: LevelTier
    experience_required: int
    cumulative_experience: int
    base_multiplier: float
    tier_bonus: float
    unlock_benefits: List[str]
    prestige_available: bool = False
    special_abilities: List[str] = field(default_factory=list)


@dataclass
class CreatorLevel:
    """Creator's level progression and status."""
    creator_id: str
    current_level: int
    current_tier: LevelTier
    total_experience: int
    experience_to_next_level: int
    prestige_level: int = 0
    prestige_experience: int = 0
    level_achieved_date: datetime = field(default_factory=datetime.utcnow)
    tier_achieved_date: datetime = field(default_factory=datetime.utcnow)
    experience_breakdown: Dict[ExperienceSource, int] = field(default_factory=dict)
    level_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ExperienceTransaction:
    """Experience point transaction record."""
    transaction_id: str
    creator_id: str
    source: ExperienceSource
    amount: int
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
    multiplier_applied: float = 1.0
    final_amount: int = 0


@dataclass
class RevenueMultiplierCalculation:
    """Revenue multiplier calculation with breakdown."""
    calculation_id: str
    creator_id: str
    base_revenue: Decimal
    level: int
    tier: LevelTier
    prestige_level: int
    base_multiplier: float
    tier_bonus: float
    prestige_bonus: float
    special_bonuses: Dict[str, float]
    total_multiplier: float
    enhanced_revenue: Decimal
    revenue_increase: Decimal
    calculation_date: datetime = field(default_factory=datetime.utcnow)


class LevelBasedRevenueMultiplier:
    """
    Enterprise level-based revenue multiplier providing automated revenue
    scaling based on creator progression and experience accumulation.
    """
    
    def __init__(self):
        """Initialize the level-based revenue multiplier."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core storage
        self.level_definitions: Dict[int, LevelDefinition] = {}
        self.creator_levels: Dict[str, CreatorLevel] = {}
        self.experience_transactions: Dict[str, List[ExperienceTransaction]] = {}
        self.multiplier_calculations: Dict[str, List[RevenueMultiplierCalculation]] = {}
        
        # Configuration
        self.max_level = 100
        self.prestige_max_level = 10
        self.experience_decay_rate = 0.0  # No decay by default
        self.tier_progression_bonus = 0.1  # 10% bonus per tier
        self.prestige_multiplier_base = 0.05  # 5% per prestige level
        
        # Experience point values
        self.experience_values = self._initialize_experience_values()
        
        # Analytics
        self.total_experience_awarded = 0
        self.total_revenue_enhanced = Decimal("0")
        self.level_distribution = {}
        
        self.initialized = False
        self.logger.info("LevelBasedRevenueMultiplier initialized")
    
    def _initialize_experience_values(self) -> Dict[ExperienceSource, int]:
        """Initialize base experience point values for different sources."""
        return {
            ExperienceSource.CONTENT_CREATION: 10,      # Per content piece
            ExperienceSource.AUDIENCE_ENGAGEMENT: 1,    # Per engagement
            ExperienceSource.REVENUE_GENERATION: 5,     # Per dollar revenue
            ExperienceSource.COLLABORATIONS: 50,        # Per collaboration
            ExperienceSource.PLATFORM_PARTICIPATION: 25, # Per platform activity
            ExperienceSource.QUALITY_ACHIEVEMENTS: 100,  # Per quality milestone
            ExperienceSource.COMMUNITY_CONTRIBUTIONS: 75, # Per community activity
            ExperienceSource.MILESTONE_COMPLETIONS: 200, # Per milestone
            ExperienceSource.SKILL_DEVELOPMENTS: 150,   # Per skill acquired
            ExperienceSource.INNOVATION_ACTIVITIES: 300  # Per innovation project
        }
    
    async def initialize(self) -> bool:
        """Initialize the level-based revenue multiplier."""
        try:
            await self._create_level_definitions()
            await self._load_creator_levels()
            await self._load_experience_data()
            await self._calculate_level_distribution()
            
            self.initialized = True
            self.logger.info("LevelBasedRevenueMultiplier initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LevelBasedRevenueMultiplier: {e}")
            return False
    
    async def _create_level_definitions(self):
        """Create level definitions with progression requirements."""
        
        for level in range(1, self.max_level + 1):
            # Determine tier
            if level <= 10:
                tier = LevelTier.NOVICE
            elif level <= 25:
                tier = LevelTier.INTERMEDIATE
            elif level <= 50:
                tier = LevelTier.ADVANCED
            elif level <= 75:
                tier = LevelTier.EXPERT
            elif level <= 100:
                tier = LevelTier.MASTER
            else:
                tier = LevelTier.GRANDMASTER
            
            # Calculate experience requirements (exponential growth)
            if level == 1:
                experience_required = 0
                cumulative_experience = 0
            else:
                # Exponential formula: 100 * level^1.5
                experience_required = int(100 * (level ** 1.5))
                cumulative_experience = sum(
                    int(100 * (i ** 1.5)) for i in range(2, level + 1)
                )
            
            # Calculate base multiplier (increases with level)
            base_multiplier = 1.0 + (level - 1) * 0.02  # 2% per level
            
            # Tier bonus
            tier_bonuses = {
                LevelTier.NOVICE: 0.0,
                LevelTier.INTERMEDIATE: 0.1,
                LevelTier.ADVANCED: 0.25,
                LevelTier.EXPERT: 0.5,
                LevelTier.MASTER: 1.0,
                LevelTier.GRANDMASTER: 2.0
            }
            tier_bonus = tier_bonuses[tier]
            
            # Unlock benefits based on level
            unlock_benefits = []
            if level == 5:
                unlock_benefits.append("Enhanced Analytics")
            if level == 10:
                unlock_benefits.append("Collaboration Boost")
            if level == 20:
                unlock_benefits.append("Premium Features")
            if level == 30:
                unlock_benefits.append("Revenue Optimization")
            if level == 50:
                unlock_benefits.append("Expert Status")
            if level == 75:
                unlock_benefits.append("Master Benefits")
            if level == 100:
                unlock_benefits.append("Prestige Unlock")
            
            # Special abilities
            special_abilities = []
            if level >= 25:
                special_abilities.append("Advanced Revenue Tracking")
            if level >= 50:
                special_abilities.append("AI-Powered Insights")
            if level >= 75:
                special_abilities.append("Custom Monetization Strategies")
            
            level_def = LevelDefinition(
                level=level,
                tier=tier,
                experience_required=experience_required,
                cumulative_experience=cumulative_experience,
                base_multiplier=base_multiplier,
                tier_bonus=tier_bonus,
                unlock_benefits=unlock_benefits,
                prestige_available=(level == self.max_level),
                special_abilities=special_abilities
            )
            
            self.level_definitions[level] = level_def
        
        self.logger.info(f"Created {len(self.level_definitions)} level definitions")
    
    async def _load_creator_levels(self):
        """Load creator level data from storage."""
        # In production, this would load from database
        self.logger.info("Loading creator level data...")
    
    async def _load_experience_data(self):
        """Load experience transaction data from storage."""
        # In production, this would load from database
        self.logger.info("Loading experience data...")
    
    async def _calculate_level_distribution(self):
        """Calculate level distribution statistics."""
        if not self.creator_levels:
            return
        
        distribution = {}
        for creator_level in self.creator_levels.values():
            level = creator_level.current_level
            tier = creator_level.current_tier.value
            
            if tier not in distribution:
                distribution[tier] = {"count": 0, "levels": {}}
            
            distribution[tier]["count"] += 1
            if level not in distribution[tier]["levels"]:
                distribution[tier]["levels"][level] = 0
            distribution[tier]["levels"][level] += 1
        
        self.level_distribution = distribution
    
    async def award_experience(
        self,
        creator_id: str,
        source: ExperienceSource,
        amount: Optional[int] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExperienceTransaction:
        """
        Award experience points to a creator.
        
        Args:
            creator_id: Creator identifier
            source: Source of experience points
            amount: Override amount (uses default if None)
            description: Description of the experience award
            metadata: Additional metadata
            
        Returns:
            Experience transaction record
        """
        try:
            # Initialize creator level if not exists
            if creator_id not in self.creator_levels:
                await self._initialize_creator_level(creator_id)
            
            # Determine experience amount
            if amount is None:
                amount = self.experience_values.get(source, 10)
            
            # Apply any multipliers
            multiplier = await self._calculate_experience_multiplier(creator_id, source)
            final_amount = int(amount * multiplier)
            
            # Create transaction
            transaction = ExperienceTransaction(
                transaction_id=str(uuid4()),
                creator_id=creator_id,
                source=source,
                amount=amount,
                description=description,
                metadata=metadata or {},
                multiplier_applied=multiplier,
                final_amount=final_amount
            )
            
            # Store transaction
            if creator_id not in self.experience_transactions:
                self.experience_transactions[creator_id] = []
            self.experience_transactions[creator_id].append(transaction)
            
            # Update creator level
            await self._update_creator_experience(creator_id, source, final_amount)
            
            # Check for level up
            await self._check_level_progression(creator_id)
            
            # Update analytics
            self.total_experience_awarded += final_amount
            
            self.logger.debug(f"Awarded {final_amount} XP to creator {creator_id} from {source.value}")
            return transaction
            
        except Exception as e:
            self.logger.error(f"Error awarding experience: {e}")
            raise
    
    async def _initialize_creator_level(self, creator_id: str):
        """Initialize level tracking for new creator."""
        creator_level = CreatorLevel(
            creator_id=creator_id,
            current_level=1,
            current_tier=LevelTier.NOVICE,
            total_experience=0,
            experience_to_next_level=self.level_definitions[2].experience_required
        )
        
        self.creator_levels[creator_id] = creator_level
        self.logger.info(f"Initialized level tracking for creator {creator_id}")
    
    async def _calculate_experience_multiplier(self, creator_id: str, source: ExperienceSource) -> float:
        """Calculate experience multiplier based on creator status."""
        
        creator_level = self.creator_levels.get(creator_id)
        if not creator_level:
            return 1.0
        
        multiplier = 1.0
        
        # Tier-based experience multiplier
        tier_multipliers = {
            LevelTier.NOVICE: 1.0,
            LevelTier.INTERMEDIATE: 1.1,
            LevelTier.ADVANCED: 1.2,
            LevelTier.EXPERT: 1.3,
            LevelTier.MASTER: 1.5,
            LevelTier.GRANDMASTER: 2.0
        }
        
        multiplier *= tier_multipliers.get(creator_level.current_tier, 1.0)
        
        # Prestige multiplier
        if creator_level.prestige_level > 0:
            prestige_bonus = 1.0 + (creator_level.prestige_level * self.prestige_multiplier_base)
            multiplier *= prestige_bonus
        
        # Source-specific multipliers
        if source == ExperienceSource.QUALITY_ACHIEVEMENTS and creator_level.current_level >= 25:
            multiplier *= 1.5  # Quality focus bonus for advanced creators
        
        return multiplier
    
    async def _update_creator_experience(self, creator_id: str, source: ExperienceSource, amount: int):
        """Update creator's experience points."""
        
        creator_level = self.creator_levels[creator_id]
        
        # Add to total experience
        creator_level.total_experience += amount
        
        # Update source breakdown
        if source not in creator_level.experience_breakdown:
            creator_level.experience_breakdown[source] = 0
        creator_level.experience_breakdown[source] += amount
        
        # Update experience to next level
        next_level = creator_level.current_level + 1
        if next_level <= self.max_level:
            next_level_def = self.level_definitions[next_level]
            required_total = next_level_def.cumulative_experience
            creator_level.experience_to_next_level = max(0, required_total - creator_level.total_experience)
    
    async def _check_level_progression(self, creator_id: str):
        """Check if creator has leveled up."""
        
        creator_level = self.creator_levels[creator_id]
        current_level = creator_level.current_level
        
        # Check for level progression
        while current_level < self.max_level:
            next_level = current_level + 1
            next_level_def = self.level_definitions[next_level]
            
            if creator_level.total_experience >= next_level_def.cumulative_experience:
                # Level up!
                old_level = creator_level.current_level
                old_tier = creator_level.current_tier
                
                creator_level.current_level = next_level
                creator_level.current_tier = next_level_def.tier
                creator_level.level_achieved_date = datetime.utcnow()
                
                # Check for tier progression
                if creator_level.current_tier != old_tier:
                    creator_level.tier_achieved_date = datetime.utcnow()
                
                # Add to level history
                creator_level.level_history.append({
                    "level": next_level,
                    "tier": next_level_def.tier.value,
                    "achieved_at": datetime.utcnow().isoformat(),
                    "total_experience": creator_level.total_experience
                })
                
                # Update experience to next level
                if next_level < self.max_level:
                    next_next_level_def = self.level_definitions[next_level + 1]
                    creator_level.experience_to_next_level = (
                        next_next_level_def.cumulative_experience - creator_level.total_experience
                    )
                else:
                    creator_level.experience_to_next_level = 0
                
                self.logger.info(f"Creator {creator_id} leveled up: {old_level} → {next_level} ({old_tier.value} → {creator_level.current_tier.value})")
                
                current_level = next_level
            else:
                break
    
    async def calculate_revenue_multiplier(
        self,
        creator_id: str,
        base_revenue: Decimal,
        multiplier_types: Optional[List[MultiplierType]] = None
    ) -> RevenueMultiplierCalculation:
        """
        Calculate revenue multiplier based on creator's level.
        
        Args:
            creator_id: Creator identifier
            base_revenue: Base revenue amount
            multiplier_types: Types of multipliers to apply
            
        Returns:
            Revenue multiplier calculation with breakdown
        """
        try:
            if creator_id not in self.creator_levels:
                # No level data = no multiplier
                return self._create_no_multiplier_calculation(creator_id, base_revenue)
            
            creator_level = self.creator_levels[creator_id]
            level_def = self.level_definitions[creator_level.current_level]
            
            if multiplier_types is None:
                multiplier_types = [MultiplierType.BASE_REVENUE, MultiplierType.TIER_BONUS]
            
            # Calculate base multiplier
            base_multiplier = level_def.base_multiplier
            
            # Calculate tier bonus
            tier_bonus = level_def.tier_bonus
            
            # Calculate prestige bonus
            prestige_bonus = 0.0
            if creator_level.prestige_level > 0:
                prestige_bonus = creator_level.prestige_level * self.prestige_multiplier_base
            
            # Calculate special bonuses
            special_bonuses = {}
            
            if MultiplierType.ENGAGEMENT_BONUS in multiplier_types:
                # Bonus based on engagement experience
                engagement_exp = creator_level.experience_breakdown.get(ExperienceSource.AUDIENCE_ENGAGEMENT, 0)
                if engagement_exp > 1000:
                    special_bonuses["engagement_bonus"] = min(0.2, engagement_exp / 10000)  # Up to 20%
            
            if MultiplierType.COLLABORATION_BONUS in multiplier_types:
                # Bonus for collaboration activity
                collab_exp = creator_level.experience_breakdown.get(ExperienceSource.COLLABORATIONS, 0)
                if collab_exp > 500:
                    special_bonuses["collaboration_bonus"] = min(0.15, collab_exp / 5000)  # Up to 15%
            
            if MultiplierType.QUALITY_PREMIUM in multiplier_types:
                # Premium for quality achievements
                quality_exp = creator_level.experience_breakdown.get(ExperienceSource.QUALITY_ACHIEVEMENTS, 0)
                if quality_exp > 1000:
                    special_bonuses["quality_premium"] = min(0.25, quality_exp / 4000)  # Up to 25%
            
            if MultiplierType.ACHIEVEMENT_MULTIPLIER in multiplier_types:
                # Multiplier for milestone completions
                milestone_exp = creator_level.experience_breakdown.get(ExperienceSource.MILESTONE_COMPLETIONS, 0)
                if milestone_exp > 2000:
                    special_bonuses["achievement_multiplier"] = min(0.3, milestone_exp / 10000)  # Up to 30%
            
            # Calculate total multiplier
            total_multiplier = base_multiplier + tier_bonus + prestige_bonus + sum(special_bonuses.values())
            
            # Calculate enhanced revenue
            enhanced_revenue = base_revenue * Decimal(str(total_multiplier))
            revenue_increase = enhanced_revenue - base_revenue
            
            calculation = RevenueMultiplierCalculation(
                calculation_id=str(uuid4()),
                creator_id=creator_id,
                base_revenue=base_revenue,
                level=creator_level.current_level,
                tier=creator_level.current_tier,
                prestige_level=creator_level.prestige_level,
                base_multiplier=base_multiplier,
                tier_bonus=tier_bonus,
                prestige_bonus=prestige_bonus,
                special_bonuses=special_bonuses,
                total_multiplier=total_multiplier,
                enhanced_revenue=enhanced_revenue,
                revenue_increase=revenue_increase
            )
            
            # Store calculation
            if creator_id not in self.multiplier_calculations:
                self.multiplier_calculations[creator_id] = []
            self.multiplier_calculations[creator_id].append(calculation)
            
            # Update analytics
            self.total_revenue_enhanced += revenue_increase
            
            self.logger.debug(f"Calculated revenue multiplier for creator {creator_id}: {total_multiplier:.2f}x")
            return calculation
            
        except Exception as e:
            self.logger.error(f"Error calculating revenue multiplier: {e}")
            return self._create_no_multiplier_calculation(creator_id, base_revenue)
    
    def _create_no_multiplier_calculation(
        self, creator_id: str, base_revenue: Decimal
    ) -> RevenueMultiplierCalculation:
        """Create calculation for creators with no level multiplier."""
        return RevenueMultiplierCalculation(
            calculation_id=str(uuid4()),
            creator_id=creator_id,
            base_revenue=base_revenue,
            level=1,
            tier=LevelTier.NOVICE,
            prestige_level=0,
            base_multiplier=1.0,
            tier_bonus=0.0,
            prestige_bonus=0.0,
            special_bonuses={},
            total_multiplier=1.0,
            enhanced_revenue=base_revenue,
            revenue_increase=Decimal("0")
        )
    
    async def prestige_creator(self, creator_id: str) -> bool:
        """Prestige a max-level creator to unlock additional benefits."""
        try:
            if creator_id not in self.creator_levels:
                raise ValueError("Creator level data not found")
            
            creator_level = self.creator_levels[creator_id]
            
            if creator_level.current_level < self.max_level:
                raise ValueError("Creator must be max level to prestige")
            
            if creator_level.prestige_level >= self.prestige_max_level:
                raise ValueError("Creator has reached maximum prestige level")
            
            # Reset level but keep prestige
            creator_level.prestige_level += 1
            creator_level.current_level = 1
            creator_level.current_tier = LevelTier.NOVICE
            creator_level.prestige_experience += creator_level.total_experience
            creator_level.total_experience = 0
            creator_level.experience_to_next_level = self.level_definitions[2].experience_required
            
            # Add to history
            creator_level.level_history.append({
                "event": "prestige",
                "prestige_level": creator_level.prestige_level,
                "timestamp": datetime.utcnow().isoformat(),
                "total_experience_sacrificed": creator_level.prestige_experience
            })
            
            self.logger.info(f"Creator {creator_id} prestiged to level {creator_level.prestige_level}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error prestiging creator: {e}")
            return False
    
    async def get_creator_level_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive level summary for creator."""
        try:
            if creator_id not in self.creator_levels:
                return {"creator_id": creator_id, "message": "No level data found"}
            
            creator_level = self.creator_levels[creator_id]
            level_def = self.level_definitions[creator_level.current_level]
            creator_transactions = self.experience_transactions.get(creator_id, [])
            creator_calculations = self.multiplier_calculations.get(creator_id, [])
            
            # Calculate progress percentage
            if creator_level.current_level < self.max_level:
                current_total = level_def.cumulative_experience
                next_level_def = self.level_definitions[creator_level.current_level + 1]
                next_total = next_level_def.cumulative_experience
                level_progress = ((creator_level.total_experience - current_total) / 
                                (next_total - current_total)) * 100
            else:
                level_progress = 100.0
            
            # Recent multiplier impact
            recent_calculations = sorted(
                creator_calculations,
                key=lambda x: x.calculation_date,
                reverse=True
            )[:5]
            
            total_revenue_boost = sum(
                calc.revenue_increase for calc in creator_calculations
            )
            
            return {
                "creator_id": creator_id,
                "level_status": {
                    "current_level": creator_level.current_level,
                    "current_tier": creator_level.current_tier.value,
                    "prestige_level": creator_level.prestige_level,
                    "total_experience": creator_level.total_experience,
                    "experience_to_next_level": creator_level.experience_to_next_level,
                    "level_progress_percentage": round(level_progress, 1)
                },
                "multiplier_benefits": {
                    "base_multiplier": level_def.base_multiplier,
                    "tier_bonus": level_def.tier_bonus,
                    "prestige_bonus": creator_level.prestige_level * self.prestige_multiplier_base,
                    "total_revenue_boost": float(total_revenue_boost),
                    "currency": "USD"
                },
                "experience_breakdown": {
                    source.value: amount
                    for source, amount in creator_level.experience_breakdown.items()
                },
                "unlocked_benefits": level_def.unlock_benefits,
                "special_abilities": level_def.special_abilities,
                "recent_multiplier_calculations": [
                    {
                        "date": calc.calculation_date.isoformat(),
                        "multiplier": round(calc.total_multiplier, 2),
                        "revenue_increase": float(calc.revenue_increase)
                    }
                    for calc in recent_calculations
                ],
                "progression_history": creator_level.level_history[-10:]  # Last 10 events
            }
            
        except Exception as e:
            self.logger.error(f"Error getting creator level summary: {e}")
            return {"error": str(e)}
    
    async def get_system_level_analytics(self) -> Dict[str, Any]:
        """Get system-wide level analytics."""
        try:
            total_creators = len(self.creator_levels)
            
            if total_creators == 0:
                return {"message": "No level data found"}
            
            # Calculate level distribution
            await self._calculate_level_distribution()
            
            # Calculate averages
            avg_level = sum(c.current_level for c in self.creator_levels.values()) / total_creators
            total_prestige_levels = sum(c.prestige_level for c in self.creator_levels.values())
            
            # Top creators by level
            top_creators = sorted(
                self.creator_levels.values(),
                key=lambda x: (x.prestige_level, x.current_level, x.total_experience),
                reverse=True
            )[:10]
            
            # Experience source distribution
            source_totals = {}
            for creator_level in self.creator_levels.values():
                for source, amount in creator_level.experience_breakdown.items():
                    source_totals[source.value] = source_totals.get(source.value, 0) + amount
            
            return {
                "overview": {
                    "total_creators": total_creators,
                    "average_level": round(avg_level, 1),
                    "total_prestige_levels": total_prestige_levels,
                    "total_experience_awarded": self.total_experience_awarded,
                    "total_revenue_enhanced": float(self.total_revenue_enhanced),
                    "currency": "USD"
                },
                "level_distribution": self.level_distribution,
                "experience_sources": source_totals,
                "top_creators": [
                    {
                        "creator_id": c.creator_id,
                        "level": c.current_level,
                        "tier": c.current_tier.value,
                        "prestige_level": c.prestige_level,
                        "total_experience": c.total_experience
                    }
                    for c in top_creators
                ],
                "progression_metrics": {
                    "creators_at_max_level": len([c for c in self.creator_levels.values() if c.current_level == self.max_level]),
                    "prestiged_creators": len([c for c in self.creator_levels.values() if c.prestige_level > 0]),
                    "active_levelers": len([c for c in self.creator_levels.values() if c.experience_to_next_level > 0]),
                    "tier_progression_rate": round((total_creators - len([c for c in self.creator_levels.values() if c.current_tier == LevelTier.NOVICE])) / max(total_creators, 1) * 100, 1)
                },
                "system_health": {
                    "engagement_score": min(95.0, 75.0 + (avg_level / self.max_level) * 25),
                    "progression_balance": "Healthy",  # Could be calculated from distribution
                    "revenue_impact": round(float(self.total_revenue_enhanced) / max(total_creators, 1), 2)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system level analytics: {e}")
            return {"error": str(e)}


# Global instance
_level_based_revenue_multiplier: Optional[LevelBasedRevenueMultiplier] = None

async def get_level_based_revenue_multiplier() -> LevelBasedRevenueMultiplier:
    """Get the global level-based revenue multiplier instance."""
    global _level_based_revenue_multiplier
    
    if _level_based_revenue_multiplier is None:
        _level_based_revenue_multiplier = LevelBasedRevenueMultiplier()
        await _level_based_revenue_multiplier.initialize()
    
    return _level_based_revenue_multiplier