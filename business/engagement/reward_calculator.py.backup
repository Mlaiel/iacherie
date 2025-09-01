"""Enterprise Reward Calculator - Dynamic rewards calculation system for IA Influencer platform.

This module provides a sophisticated reward calculation engine that dynamically
calculates and distributes rewards based on user actions, achievements, and performance.
Designed for multi-format content creators with intelligent reward optimization.

Architecture: Enterprise Production-Ready (Backend Level 2)
Module: backend/business/engagement/reward_calculator.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Creator Upload → AI Processing → Protection → SEO → Collaboration Matching + Gamification →
Dynamic Reward Calculation → Distribution → Monetization → Analytics
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import uuid4, UUID
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from dataclasses import dataclass, field
import json
import math

logger = logging.getLogger(__name__)


class RewardType(str, Enum):
    """Types of rewards available in the system."""
    EXPERIENCE_POINTS = "experience_points"
    VIRTUAL_CURRENCY = "virtual_currency"
    REAL_CURRENCY = "real_currency"
    BADGE = "badge"
    ACHIEVEMENT = "achievement"
    PREMIUM_FEATURE = "premium_feature"
    CONTENT_BOOST = "content_boost"
    COLLABORATION_CREDIT = "collaboration_credit"
    PLATFORM_ACCESS = "platform_access"
    PROFILE_HIGHLIGHT = "profile_highlight"
    CUSTOM_ANIMATION = "custom_animation"
    REVENUE_MULTIPLIER = "revenue_multiplier"
    AD_CREDIT = "ad_credit"
    EARLY_ACCESS = "early_access"
    EXCLUSIVE_CONTENT = "exclusive_content"


class RewardRarity(str, Enum):
    """Rarity levels for rewards."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class RewardSource(str, Enum):
    """Sources that can trigger rewards."""
    CONTENT_UPLOAD = "content_upload"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    CHALLENGE_COMPLETION = "challenge_completion"
    COLLABORATION_SUCCESS = "collaboration_success"
    MILESTONE_REACHED = "milestone_reached"
    STREAK_BONUS = "streak_bonus"
    QUALITY_BONUS = "quality_bonus"
    ENGAGEMENT_BONUS = "engagement_bonus"
    REVENUE_SHARING = "revenue_sharing"
    REFERRAL_BONUS = "referral_bonus"
    COMMUNITY_CONTRIBUTION = "community_contribution"
    PLATFORM_EXPANSION = "platform_expansion"
    SEASONAL_EVENT = "seasonal_event"
    ADMIN_GRANT = "admin_grant"


class RewardCalculationMethod(str, Enum):
    """Methods for calculating reward values."""
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    TIERED = "tiered"
    EXPONENTIAL = "exponential"
    PERFORMANCE_BASED = "performance_based"
    COMMUNITY_BASED = "community_based"
    AI_OPTIMIZED = "ai_optimized"


@dataclass
class RewardCalculationContext:
    """Context information for reward calculations."""
    user_id: str
    source: RewardSource
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    user_profile: Dict[str, Any] = field(default_factory=dict)
    platform_state: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Performance metrics
    content_quality_score: float = 0.0
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    collaboration_metrics: Dict[str, float] = field(default_factory=dict)
    revenue_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Multipliers and bonuses
    streak_multiplier: float = 1.0
    quality_multiplier: float = 1.0
    loyalty_multiplier: float = 1.0
    seasonal_multiplier: float = 1.0
    special_event_multiplier: float = 1.0


@dataclass
class RewardRule:
    """Defines rules for calculating rewards."""
    rule_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    reward_type: RewardType = RewardType.EXPERIENCE_POINTS
    calculation_method: RewardCalculationMethod = RewardCalculationMethod.FIXED
    
    # Trigger conditions
    trigger_sources: List[RewardSource] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Calculation parameters
    base_value: Union[int, float, Decimal] = 0
    calculation_params: Dict[str, Any] = field(default_factory=dict)
    
    # Constraints
    min_value: Union[int, float, Decimal] = 0
    max_value: Optional[Union[int, float, Decimal]] = None
    daily_limit: Optional[Union[int, float, Decimal]] = None
    monthly_limit: Optional[Union[int, float, Decimal]] = None
    
    # Metadata
    rarity: RewardRarity = RewardRarity.COMMON
    requires_approval: bool = False
    active: bool = True
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    
    # Usage tracking
    total_awarded: Union[int, float, Decimal] = 0
    times_triggered: int = 0
    
    def is_valid(self, timestamp: Optional[datetime] = None) -> bool:
        """Check if the reward rule is currently valid."""
        if not self.active:
            return False
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if self.valid_from and timestamp < self.valid_from:
            return False
        
        if self.valid_until and timestamp > self.valid_until:
            return False
        
        return True


@dataclass
class CalculatedReward:
    """Represents a calculated reward."""
    reward_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    reward_type: RewardType = RewardType.EXPERIENCE_POINTS
    value: Union[int, float, Decimal] = 0
    original_value: Union[int, float, Decimal] = 0
    
    # Source information
    source: RewardSource = RewardSource.CONTENT_UPLOAD
    source_id: Optional[str] = None
    rule_id: Optional[str] = None
    
    # Calculation details
    calculation_method: RewardCalculationMethod = RewardCalculationMethod.FIXED
    multipliers_applied: Dict[str, float] = field(default_factory=dict)
    bonuses_applied: Dict[str, Union[int, float, Decimal]] = field(default_factory=dict)
    
    # Metadata
    rarity: RewardRarity = RewardRarity.COMMON
    description: str = ""
    display_name: str = ""
    
    # State
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    awarded_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Additional data
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if the reward has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def get_display_value(self) -> str:
        """Get formatted display value for the reward."""
        if self.reward_type == RewardType.VIRTUAL_CURRENCY:
            return f"{int(self.value):,} coins"
        elif self.reward_type == RewardType.REAL_CURRENCY:
            return f"${self.value:.2f}"
        elif self.reward_type == RewardType.EXPERIENCE_POINTS:
            return f"{int(self.value):,} XP"
        elif self.reward_type in [RewardType.BADGE, RewardType.ACHIEVEMENT]:
            return self.display_name or str(self.value)
        else:
            return str(self.value)


class RewardCalculator:
    """
    Enterprise-grade dynamic reward calculation system.
    
    Calculates and optimizes rewards based on user behavior, performance,
    and platform dynamics to maximize engagement and retention.
    """
    
    def __init__(self):
        """Initialize the reward calculator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._rules: Dict[str, RewardRule] = {}
        self._user_reward_history: Dict[str, List[CalculatedReward]] = {}
        self._daily_limits: Dict[str, Dict[str, Decimal]] = {}
        self._monthly_limits: Dict[str, Dict[str, Decimal]] = {}
        
        # Initialize default reward rules
        self._initialize_default_rules()
        
        self.logger.info("RewardCalculator initialized successfully")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default reward rules."""
        
        # Content Upload Rewards
        content_upload_rule = RewardRule(
            name="Content Upload Basic",
            description="Basic reward for uploading content",
            reward_type=RewardType.EXPERIENCE_POINTS,
            calculation_method=RewardCalculationMethod.PERFORMANCE_BASED,
            trigger_sources=[RewardSource.CONTENT_UPLOAD],
            base_value=50,
            calculation_params={
                "quality_weight": 0.4,
                "engagement_weight": 0.3,
                "uniqueness_weight": 0.3,
                "min_quality_threshold": 70
            },
            min_value=25,
            max_value=500,
            daily_limit=2000
        )
        self._rules[content_upload_rule.rule_id] = content_upload_rule
        
        # First Upload Bonus
        first_upload_rule = RewardRule(
            name="First Upload Bonus",
            description="Special bonus for first content upload",
            reward_type=RewardType.EXPERIENCE_POINTS,
            calculation_method=RewardCalculationMethod.FIXED,
            trigger_sources=[RewardSource.CONTENT_UPLOAD],
            base_value=200,
            conditions={"first_upload": True},
            rarity=RewardRarity.UNCOMMON
        )
        self._rules[first_upload_rule.rule_id] = first_upload_rule
        
        # Quality Bonus
        quality_bonus_rule = RewardRule(
            name="Quality Excellence Bonus",
            description="Bonus for high-quality content",
            reward_type=RewardType.VIRTUAL_CURRENCY,
            calculation_method=RewardCalculationMethod.TIERED,
            trigger_sources=[RewardSource.QUALITY_BONUS],
            base_value=100,
            calculation_params={
                "tiers": {
                    95: {"multiplier": 3.0, "rarity": RewardRarity.RARE},
                    90: {"multiplier": 2.0, "rarity": RewardRarity.UNCOMMON},
                    85: {"multiplier": 1.5, "rarity": RewardRarity.COMMON}
                }
            },
            conditions={"min_quality_score": 85},
            daily_limit=1000
        )
        self._rules[quality_bonus_rule.rule_id] = quality_bonus_rule
        
        # Collaboration Success
        collaboration_rule = RewardRule(
            name="Collaboration Success",
            description="Reward for successful collaborations",
            reward_type=RewardType.EXPERIENCE_POINTS,
            calculation_method=RewardCalculationMethod.PERFORMANCE_BASED,
            trigger_sources=[RewardSource.COLLABORATION_SUCCESS],
            base_value=150,
            calculation_params={
                "participant_count_weight": 0.3,
                "quality_weight": 0.4,
                "innovation_weight": 0.3,
                "max_participants": 10
            },
            min_value=75,
            max_value=1000
        )
        self._rules[collaboration_rule.rule_id] = collaboration_rule
        
        # Streak Bonus
        streak_rule = RewardRule(
            name="Activity Streak Bonus",
            description="Daily bonus for maintaining activity streaks",
            reward_type=RewardType.VIRTUAL_CURRENCY,
            calculation_method=RewardCalculationMethod.EXPONENTIAL,
            trigger_sources=[RewardSource.STREAK_BONUS],
            base_value=50,
            calculation_params={
                "growth_rate": 1.1,
                "max_streak_bonus": 500,
                "milestone_bonuses": {7: 100, 30: 500, 100: 2000}
            },
            daily_limit=500
        )
        self._rules[streak_rule.rule_id] = streak_rule
        
        # Revenue Sharing
        revenue_rule = RewardRule(
            name="Revenue Sharing Bonus",
            description="Share of platform revenue based on contribution",
            reward_type=RewardType.REAL_CURRENCY,
            calculation_method=RewardCalculationMethod.PERCENTAGE,
            trigger_sources=[RewardSource.REVENUE_SHARING],
            base_value=0.05,  # 5% base rate
            calculation_params={
                "performance_multiplier": True,
                "tier_bonuses": {
                    "premium": 1.5,
                    "enterprise": 2.0
                }
            },
            monthly_limit=10000,
            requires_approval=True
        )
        self._rules[revenue_rule.rule_id] = revenue_rule
        
        # Achievement Unlock
        achievement_rule = RewardRule(
            name="Achievement Unlock Bonus",
            description="Bonus for unlocking achievements",
            reward_type=RewardType.EXPERIENCE_POINTS,
            calculation_method=RewardCalculationMethod.TIERED,
            trigger_sources=[RewardSource.ACHIEVEMENT_UNLOCK],
            base_value=300,
            calculation_params={
                "rarity_multipliers": {
                    RewardRarity.COMMON.value: 1.0,
                    RewardRarity.UNCOMMON.value: 1.5,
                    RewardRarity.RARE.value: 2.0,
                    RewardRarity.EPIC.value: 3.0,
                    RewardRarity.LEGENDARY.value: 5.0
                }
            }
        )
        self._rules[achievement_rule.rule_id] = achievement_rule
        
        # Challenge Completion
        challenge_rule = RewardRule(
            name="Challenge Completion Reward",
            description="Reward for completing challenges",
            reward_type=RewardType.EXPERIENCE_POINTS,
            calculation_method=RewardCalculationMethod.PERFORMANCE_BASED,
            trigger_sources=[RewardSource.CHALLENGE_COMPLETION],
            base_value=250,
            calculation_params={
                "difficulty_multipliers": {
                    "beginner": 1.0,
                    "intermediate": 1.5,
                    "advanced": 2.0,
                    "expert": 3.0,
                    "master": 5.0
                },
                "ranking_bonuses": {
                    1: 2.0,  # First place
                    2: 1.5,  # Second place
                    3: 1.25  # Third place
                }
            },
            min_value=100,
            max_value=5000
        )
        self._rules[challenge_rule.rule_id] = challenge_rule
    
    async def calculate_rewards(
        self,
        context: RewardCalculationContext
    ) -> List[CalculatedReward]:
        """Calculate rewards for a given context."""
        try:
            calculated_rewards = []
            
            # Find applicable rules
            applicable_rules = await self._find_applicable_rules(context)
            
            for rule in applicable_rules:
                # Check if rule limits allow for more rewards
                if not await self._check_rule_limits(rule, context.user_id):
                    self.logger.debug(f"Rule {rule.name} limit reached for user {context.user_id}")
                    continue
                
                # Calculate reward value
                reward_value = await self._calculate_rule_value(rule, context)
                
                if reward_value <= 0:
                    continue
                
                # Create calculated reward
                reward = CalculatedReward(
                    user_id=context.user_id,
                    reward_type=rule.reward_type,
                    value=reward_value,
                    original_value=rule.base_value,
                    source=context.source,
                    source_id=context.trigger_data.get("source_id"),
                    rule_id=rule.rule_id,
                    calculation_method=rule.calculation_method,
                    rarity=rule.rarity,
                    description=rule.description,
                    display_name=rule.name
                )
                
                # Apply multipliers and bonuses
                await self._apply_multipliers_and_bonuses(reward, context)
                
                # Set expiration if applicable
                if rule.reward_type in [RewardType.CONTENT_BOOST, RewardType.REVENUE_MULTIPLIER]:
                    reward.expires_at = datetime.utcnow() + timedelta(days=30)
                
                calculated_rewards.append(reward)
                
                # Update rule usage tracking
                rule.times_triggered += 1
                rule.total_awarded += reward.value
            
            self.logger.info(f"Calculated {len(calculated_rewards)} rewards for user {context.user_id}")
            return calculated_rewards
            
        except Exception as e:
            self.logger.error(f"Failed to calculate rewards: {e}")
            return []
    
    async def _find_applicable_rules(
        self,
        context: RewardCalculationContext
    ) -> List[RewardRule]:
        """Find rules applicable to the given context."""
        applicable_rules = []
        
        for rule in self._rules.values():
            # Check if rule is valid
            if not rule.is_valid(context.timestamp):
                continue
            
            # Check if source matches
            if context.source not in rule.trigger_sources:
                continue
            
            # Check conditions
            if not await self._check_rule_conditions(rule, context):
                continue
            
            applicable_rules.append(rule)
        
        return applicable_rules
    
    async def _check_rule_conditions(
        self,
        rule: RewardRule,
        context: RewardCalculationContext
    ) -> bool:
        """Check if rule conditions are met."""
        try:
            for condition_key, condition_value in rule.conditions.items():
                
                if condition_key == "first_upload":
                    user_uploads = context.user_profile.get("content_count", 0)
                    if condition_value and user_uploads != 1:
                        return False
                
                elif condition_key == "min_quality_score":
                    if context.content_quality_score < condition_value:
                        return False
                
                elif condition_key == "min_streak_days":
                    current_streak = context.user_profile.get("current_streak", 0)
                    if current_streak < condition_value:
                        return False
                
                elif condition_key == "creator_type":
                    user_creator_type = context.user_profile.get("creator_type", "")
                    if user_creator_type != condition_value:
                        return False
                
                elif condition_key == "subscription_tier":
                    user_tier = context.user_profile.get("subscription_tier", "free")
                    if user_tier != condition_value:
                        return False
                
                elif condition_key in context.trigger_data:
                    if context.trigger_data[condition_key] != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rule conditions: {e}")
            return False
    
    async def _check_rule_limits(self, rule: RewardRule, user_id: str) -> bool:
        """Check if rule limits allow for more rewards."""
        try:
            today = datetime.utcnow().date()
            this_month = datetime.utcnow().replace(day=1).date()
            
            # Initialize user limits if not exists
            if user_id not in self._daily_limits:
                self._daily_limits[user_id] = {}
            if user_id not in self._monthly_limits:
                self._monthly_limits[user_id] = {}
            
            # Check daily limit
            if rule.daily_limit is not None:
                daily_key = f"{rule.rule_id}_{today}"
                daily_used = self._daily_limits[user_id].get(daily_key, Decimal('0'))
                if daily_used >= rule.daily_limit:
                    return False
            
            # Check monthly limit
            if rule.monthly_limit is not None:
                monthly_key = f"{rule.rule_id}_{this_month}"
                monthly_used = self._monthly_limits[user_id].get(monthly_key, Decimal('0'))
                if monthly_used >= rule.monthly_limit:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rule limits: {e}")
            return False
    
    async def _calculate_rule_value(
        self,
        rule: RewardRule,
        context: RewardCalculationContext
    ) -> Union[int, float, Decimal]:
        """Calculate the reward value based on the rule's calculation method."""
        try:
            if rule.calculation_method == RewardCalculationMethod.FIXED:
                return rule.base_value
            
            elif rule.calculation_method == RewardCalculationMethod.PERCENTAGE:
                base_amount = context.trigger_data.get("base_amount", 0)
                return Decimal(str(base_amount)) * Decimal(str(rule.base_value))
            
            elif rule.calculation_method == RewardCalculationMethod.TIERED:
                return await self._calculate_tiered_value(rule, context)
            
            elif rule.calculation_method == RewardCalculationMethod.EXPONENTIAL:
                return await self._calculate_exponential_value(rule, context)
            
            elif rule.calculation_method == RewardCalculationMethod.PERFORMANCE_BASED:
                return await self._calculate_performance_based_value(rule, context)
            
            elif rule.calculation_method == RewardCalculationMethod.COMMUNITY_BASED:
                return await self._calculate_community_based_value(rule, context)
            
            elif rule.calculation_method == RewardCalculationMethod.AI_OPTIMIZED:
                return await self._calculate_ai_optimized_value(rule, context)
            
            else:
                return rule.base_value
                
        except Exception as e:
            self.logger.error(f"Error calculating rule value: {e}")
            return 0
    
    async def _calculate_tiered_value(
        self,
        rule: RewardRule,
        context: RewardCalculationContext
    ) -> Union[int, float, Decimal]:
        """Calculate value using tiered approach."""
        params = rule.calculation_params
        
        if "tiers" in params:
            # Quality-based tiers
            quality_score = context.content_quality_score
            for threshold in sorted(params["tiers"].keys(), reverse=True):
                if quality_score >= threshold:
                    tier_data = params["tiers"][threshold]
                    multiplier = tier_data.get("multiplier", 1.0)
                    return Decimal(str(rule.base_value)) * Decimal(str(multiplier))
        
        elif "rarity_multipliers" in params:
            # Rarity-based tiers
            achievement_rarity = context.trigger_data.get("achievement_rarity", "common")
            multiplier = params["rarity_multipliers"].get(achievement_rarity, 1.0)
            return Decimal(str(rule.base_value)) * Decimal(str(multiplier))
        
        elif "difficulty_multipliers" in params:
            # Difficulty-based tiers
            difficulty = context.trigger_data.get("difficulty", "beginner")
            multiplier = params["difficulty_multipliers"].get(difficulty, 1.0)
            
            # Apply ranking bonus if applicable
            ranking = context.trigger_data.get("ranking")
            if ranking and "ranking_bonuses" in params:
                ranking_bonus = params["ranking_bonuses"].get(ranking, 1.0)
                multiplier *= ranking_bonus
            
            return Decimal(str(rule.base_value)) * Decimal(str(multiplier))
        
        return rule.base_value
    
    async def _calculate_exponential_value(
        self,
        rule: RewardRule,
        context: RewardCalculationContext
    ) -> Union[int, float, Decimal]:
        """Calculate value using exponential growth."""
        params = rule.calculation_params
        
        # Streak-based exponential growth
        if context.source == RewardSource.STREAK_BONUS:
            streak_days = context.user_profile.get("current_streak", 0)
            growth_rate = params.get("growth_rate", 1.1)
            max_bonus = params.get("max_streak_bonus", 500)
            
            # Calculate exponential bonus
            exponential_value = rule.base_value * (growth_rate ** min(streak_days, 30))
            exponential_value = min(exponential_value, max_bonus)
            
            # Add milestone bonuses
            milestone_bonuses = params.get("milestone_bonuses", {})
            milestone_bonus = 0
            for milestone, bonus in milestone_bonuses.items():
                if streak_days >= milestone:
                    milestone_bonus = max(milestone_bonus, bonus)
            
            return Decimal(str(exponential_value + milestone_bonus))
        
        return rule.base_value
    
    async def _calculate_performance_based_value(
        self,
        rule: RewardRule,
        context: RewardCalculationContext
    ) -> Union[int, float, Decimal]:
        """Calculate value based on performance metrics."""
        params = rule.calculation_params
        base_value = Decimal(str(rule.base_value))
        
        if context.source == RewardSource.CONTENT_UPLOAD:
            # Content upload performance calculation
            quality_weight = params.get("quality_weight", 0.4)
            engagement_weight = params.get("engagement_weight", 0.3)
            uniqueness_weight = params.get("uniqueness_weight", 0.3)
            min_threshold = params.get("min_quality_threshold", 70)
            
            quality_score = context.content_quality_score
            if quality_score < min_threshold:
                return 0
            
            # Normalize scores (0-1 range)
            quality_factor = min(quality_score / 100.0, 1.0)
            engagement_factor = min(context.engagement_metrics.get("engagement_rate", 0) / 50.0, 1.0)
            uniqueness_factor = min(context.trigger_data.get("uniqueness_score", 80) / 100.0, 1.0)
            
            # Calculate weighted performance score
            performance_score = (
                quality_factor * quality_weight +
                engagement_factor * engagement_weight +
                uniqueness_factor * uniqueness_weight
            )
            
            return base_value * Decimal(str(performance_score))
        
        elif context.source == RewardSource.COLLABORATION_SUCCESS:
            # Collaboration performance calculation
            participant_weight = params.get("participant_count_weight", 0.3)
            quality_weight = params.get("quality_weight", 0.4)
            innovation_weight = params.get("innovation_weight", 0.3)
            max_participants = params.get("max_participants", 10)
            
            participant_count = context.collaboration_metrics.get("participant_count", 1)
            quality_score = context.collaboration_metrics.get("quality_score", 80)
            innovation_score = context.collaboration_metrics.get("innovation_score", 70)
            
            # Calculate factors
            participant_factor = min(participant_count / max_participants, 1.0)
            quality_factor = min(quality_score / 100.0, 1.0)
            innovation_factor = min(innovation_score / 100.0, 1.0)
            
            # Calculate weighted performance score
            performance_score = (
                participant_factor * participant_weight +
                quality_factor * quality_weight +
                innovation_factor * innovation_weight
            )
            
            return base_value * Decimal(str(performance_score))
        
        return base_value
    
    async def _calculate_community_based_value(
        self,
        rule: RewardRule,
        context: RewardCalculationContext
    ) -> Union[int, float, Decimal]:
        """Calculate value based on community metrics."""
        # Community voting, peer ratings, etc.
        community_score = context.trigger_data.get("community_score", 0.75)
        return Decimal(str(rule.base_value)) * Decimal(str(community_score))
    
    async def _calculate_ai_optimized_value(
        self,
        rule: RewardRule,
        context: RewardCalculationContext
    ) -> Union[int, float, Decimal]:
        """Calculate AI-optimized reward value."""
        # This would integrate with ML models for optimization
        # For now, use a sophisticated heuristic approach
        
        base_value = Decimal(str(rule.base_value))
        
        # User engagement optimization
        user_level = context.user_profile.get("level", 1)
        engagement_history = context.user_profile.get("avg_engagement_rate", 15.0)
        retention_score = context.user_profile.get("retention_score", 0.8)
        
        # Calculate optimization multiplier based on user profile
        level_factor = min(1.0 + (user_level - 1) * 0.02, 2.0)  # Up to 2x for high levels
        engagement_factor = min(engagement_history / 20.0, 1.5)  # Up to 1.5x for high engagement
        retention_factor = retention_score * 1.2  # Up to 1.2x for high retention
        
        optimization_multiplier = (level_factor + engagement_factor + retention_factor) / 3
        
        return base_value * Decimal(str(optimization_multiplier))
    
    async def _apply_multipliers_and_bonuses(
        self,
        reward: CalculatedReward,
        context: RewardCalculationContext
    ) -> None:
        """Apply various multipliers and bonuses to the reward."""
        try:
            original_value = reward.value
            
            # Apply streak multiplier
            if context.streak_multiplier != 1.0:
                reward.value = Decimal(str(reward.value)) * Decimal(str(context.streak_multiplier))
                reward.multipliers_applied["streak"] = context.streak_multiplier
            
            # Apply quality multiplier
            if context.quality_multiplier != 1.0:
                reward.value = Decimal(str(reward.value)) * Decimal(str(context.quality_multiplier))
                reward.multipliers_applied["quality"] = context.quality_multiplier
            
            # Apply loyalty multiplier
            if context.loyalty_multiplier != 1.0:
                reward.value = Decimal(str(reward.value)) * Decimal(str(context.loyalty_multiplier))
                reward.multipliers_applied["loyalty"] = context.loyalty_multiplier
            
            # Apply seasonal multiplier
            if context.seasonal_multiplier != 1.0:
                reward.value = Decimal(str(reward.value)) * Decimal(str(context.seasonal_multiplier))
                reward.multipliers_applied["seasonal"] = context.seasonal_multiplier
            
            # Apply special event multiplier
            if context.special_event_multiplier != 1.0:
                reward.value = Decimal(str(reward.value)) * Decimal(str(context.special_event_multiplier))
                reward.multipliers_applied["special_event"] = context.special_event_multiplier
            
            # Apply subscription tier bonus
            subscription_tier = context.user_profile.get("subscription_tier", "free")
            tier_bonuses = {
                "premium": 1.25,
                "enterprise": 1.5,
                "vip": 2.0
            }
            
            if subscription_tier in tier_bonuses:
                tier_bonus = tier_bonuses[subscription_tier]
                reward.value = Decimal(str(reward.value)) * Decimal(str(tier_bonus))
                reward.multipliers_applied["subscription_tier"] = tier_bonus
            
            # Ensure value stays within rule limits
            rule = self._rules.get(reward.rule_id)
            if rule:
                if rule.min_value and reward.value < rule.min_value:
                    reward.value = Decimal(str(rule.min_value))
                if rule.max_value and reward.value > rule.max_value:
                    reward.value = Decimal(str(rule.max_value))
            
            # Round to appropriate precision
            if reward.reward_type == RewardType.REAL_CURRENCY:
                reward.value = reward.value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                reward.value = int(reward.value)
            
            self.logger.debug(f"Applied multipliers to reward: {original_value} -> {reward.value}")
            
        except Exception as e:
            self.logger.error(f"Error applying multipliers and bonuses: {e}")
    
    async def award_rewards(
        self,
        user_id: str,
        rewards: List[CalculatedReward]
    ) -> List[CalculatedReward]:
        """Award calculated rewards to a user."""
        try:
            awarded_rewards = []
            
            for reward in rewards:
                # Check if reward requires approval
                rule = self._rules.get(reward.rule_id)
                if rule and rule.requires_approval:
                    # Add to pending approval queue
                    reward.metadata["pending_approval"] = True
                    self.logger.info(f"Reward {reward.reward_id} requires approval for user {user_id}")
                    continue
                
                # Award the reward
                reward.awarded_at = datetime.utcnow()
                
                # Update user limits
                await self._update_user_limits(user_id, reward)
                
                # Store in user history
                if user_id not in self._user_reward_history:
                    self._user_reward_history[user_id] = []
                self._user_reward_history[user_id].append(reward)
                
                awarded_rewards.append(reward)
            
            self.logger.info(f"Awarded {len(awarded_rewards)} rewards to user {user_id}")
            return awarded_rewards
            
        except Exception as e:
            self.logger.error(f"Failed to award rewards: {e}")
            return []
    
    async def _update_user_limits(self, user_id: str, reward: CalculatedReward) -> None:
        """Update user's daily and monthly limits."""
        try:
            rule = self._rules.get(reward.rule_id)
            if not rule:
                return
            
            today = datetime.utcnow().date()
            this_month = datetime.utcnow().replace(day=1).date()
            
            # Update daily limit
            if rule.daily_limit is not None:
                daily_key = f"{rule.rule_id}_{today}"
                if user_id not in self._daily_limits:
                    self._daily_limits[user_id] = {}
                
                current_daily = self._daily_limits[user_id].get(daily_key, Decimal('0'))
                self._daily_limits[user_id][daily_key] = current_daily + Decimal(str(reward.value))
            
            # Update monthly limit
            if rule.monthly_limit is not None:
                monthly_key = f"{rule.rule_id}_{this_month}"
                if user_id not in self._monthly_limits:
                    self._monthly_limits[user_id] = {}
                
                current_monthly = self._monthly_limits[user_id].get(monthly_key, Decimal('0'))
                self._monthly_limits[user_id][monthly_key] = current_monthly + Decimal(str(reward.value))
            
        except Exception as e:
            self.logger.error(f"Error updating user limits: {e}")
    
    async def get_user_reward_summary(
        self,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get summary of user's rewards over a period."""
        try:
            if user_id not in self._user_reward_history:
                return {
                    "user_id": user_id,
                    "period_days": period_days,
                    "total_rewards": 0,
                    "total_value": 0,
                    "rewards_by_type": {},
                    "rewards_by_source": {},
                    "recent_rewards": []
                }
            
            cutoff_date = datetime.utcnow() - timedelta(days=period_days)
            recent_rewards = [
                r for r in self._user_reward_history[user_id]
                if r.awarded_at and r.awarded_at >= cutoff_date
            ]
            
            # Calculate summaries
            rewards_by_type = {}
            rewards_by_source = {}
            total_value = 0
            
            for reward in recent_rewards:
                # By type
                reward_type = reward.reward_type.value
                if reward_type not in rewards_by_type:
                    rewards_by_type[reward_type] = {"count": 0, "total_value": 0}
                rewards_by_type[reward_type]["count"] += 1
                rewards_by_type[reward_type]["total_value"] += float(reward.value)
                
                # By source
                source = reward.source.value
                if source not in rewards_by_source:
                    rewards_by_source[source] = {"count": 0, "total_value": 0}
                rewards_by_source[source]["count"] += 1
                rewards_by_source[source]["total_value"] += float(reward.value)
                
                total_value += float(reward.value)
            
            return {
                "user_id": user_id,
                "period_days": period_days,
                "total_rewards": len(recent_rewards),
                "total_value": total_value,
                "rewards_by_type": rewards_by_type,
                "rewards_by_source": rewards_by_source,
                "recent_rewards": [
                    {
                        "reward_id": r.reward_id,
                        "type": r.reward_type.value,
                        "value": r.get_display_value(),
                        "source": r.source.value,
                        "awarded_at": r.awarded_at.isoformat() if r.awarded_at else None,
                        "description": r.description
                    }
                    for r in recent_rewards[-10:]  # Last 10 rewards
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user reward summary: {e}")
            return {}
    
    async def optimize_rewards_for_user(
        self,
        user_id: str,
        user_profile: Dict[str, Any],
        optimization_goals: List[str]
    ) -> Dict[str, Any]:
        """Optimize reward calculations for a specific user."""
        try:
            # Analyze user's reward history and engagement patterns
            history = self._user_reward_history.get(user_id, [])
            
            # Calculate optimization parameters
            optimization_params = {
                "engagement_multiplier": 1.0,
                "retention_multiplier": 1.0,
                "progression_multiplier": 1.0
            }
            
            # Engagement optimization
            if "engagement" in optimization_goals:
                avg_engagement = user_profile.get("avg_engagement_rate", 15.0)
                if avg_engagement < 10.0:
                    optimization_params["engagement_multiplier"] = 1.3
                elif avg_engagement > 25.0:
                    optimization_params["engagement_multiplier"] = 0.9
            
            # Retention optimization
            if "retention" in optimization_goals:
                days_since_last_activity = user_profile.get("days_since_last_activity", 0)
                if days_since_last_activity > 7:
                    optimization_params["retention_multiplier"] = 1.5
                elif days_since_last_activity > 3:
                    optimization_params["retention_multiplier"] = 1.2
            
            # Progression optimization
            if "progression" in optimization_goals:
                user_level = user_profile.get("level", 1)
                level_progress = user_profile.get("level_progress_percentage", 0)
                if level_progress < 20 and user_level > 5:
                    optimization_params["progression_multiplier"] = 1.4
            
            return {
                "user_id": user_id,
                "optimization_applied": True,
                "optimization_params": optimization_params,
                "recommendations": await self._generate_reward_recommendations(user_id, user_profile)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing rewards for user: {e}")
            return {"optimization_applied": False, "error": str(e)}
    
    async def _generate_reward_recommendations(
        self,
        user_id: str,
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized reward recommendations."""
        recommendations = []
        
        # Analyze user patterns
        user_level = user_profile.get("level", 1)
        content_count = user_profile.get("content_count", 0)
        collaboration_count = user_profile.get("collaboration_count", 0)
        
        # Content creation recommendations
        if content_count < user_level * 2:
            recommendations.append({
                "type": "content_creation",
                "title": "Content Creation Boost",
                "description": "Upload more content to earn additional XP and unlock quality bonuses",
                "potential_rewards": "Up to 500 XP per upload"
            })
        
        # Collaboration recommendations
        if collaboration_count < 5:
            recommendations.append({
                "type": "collaboration",
                "title": "Collaboration Opportunities",
                "description": "Partner with other creators to earn collaboration bonuses",
                "potential_rewards": "150-1000 XP per collaboration"
            })
        
        # Quality improvement recommendations
        avg_quality = user_profile.get("avg_quality_score", 75)
        if avg_quality < 90:
            recommendations.append({
                "type": "quality_improvement",
                "title": "Quality Excellence Program",
                "description": "Improve content quality to unlock premium rewards",
                "potential_rewards": "Quality bonuses up to 300 coins"
            })
        
        return recommendations


# Global reward calculator instance
_reward_calculator: Optional[RewardCalculator] = None


async def get_reward_calculator() -> RewardCalculator:
    """Get the global reward calculator instance."""
    global _reward_calculator
    
    if _reward_calculator is None:
        _reward_calculator = RewardCalculator()
    
    return _reward_calculator


# Convenience functions for common operations
async def calculate_content_upload_rewards(
    user_id: str,
    content_data: Dict[str, Any],
    user_profile: Dict[str, Any]
) -> List[CalculatedReward]:
    """Calculate rewards for content upload (convenience function)."""
    calculator = await get_reward_calculator()
    
    context = RewardCalculationContext(
        user_id=user_id,
        source=RewardSource.CONTENT_UPLOAD,
        trigger_data=content_data,
        user_profile=user_profile,
        content_quality_score=content_data.get("quality_score", 80.0),
        engagement_metrics=content_data.get("engagement_metrics", {}),
        streak_multiplier=user_profile.get("streak_multiplier", 1.0),
        quality_multiplier=user_profile.get("quality_multiplier", 1.0)
    )
    
    return await calculator.calculate_rewards(context)


async def award_achievement_rewards(
    user_id: str,
    achievement_data: Dict[str, Any],
    user_profile: Dict[str, Any]
) -> List[CalculatedReward]:
    """Award rewards for achievement unlock (convenience function)."""
    calculator = await get_reward_calculator()
    
    context = RewardCalculationContext(
        user_id=user_id,
        source=RewardSource.ACHIEVEMENT_UNLOCK,
        trigger_data=achievement_data,
        user_profile=user_profile
    )
    
    rewards = await calculator.calculate_rewards(context)
    return await calculator.award_rewards(user_id, rewards)