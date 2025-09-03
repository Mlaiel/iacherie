"""Reward Distributor - Comprehensive Reward Distribution System
============================================================

Advanced reward distribution system providing intelligent reward calculation,
distribution strategies, reward bundling, and comprehensive reward analytics
for content creator engagement and retention.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/gamification/rewards/reward_distributor.py
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
import random

logger = logging.getLogger(__name__)


class RewardType(str, Enum):
    """Types of rewards that can be distributed."""
    POINTS = "points"
    CURRENCY = "currency"
    PREMIUM_TIME = "premium_time"
    FEATURE_ACCESS = "feature_access"
    BADGE = "badge"
    NFT = "nft"
    REVENUE_SHARE = "revenue_share"
    PRIORITY_SUPPORT = "priority_support"
    CUSTOM_PROFILE = "custom_profile"
    COLLABORATION_BOOST = "collaboration_boost"
    VISIBILITY_BOOST = "visibility_boost"
    STORAGE_SPACE = "storage_space"
    DISCOUNT_COUPON = "discount_coupon"
    SPECIAL_EVENT_ACCESS = "special_event_access"


class RewardRarity(str, Enum):
    """Reward rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"


class RewardSource(str, Enum):
    """Sources that trigger reward distribution."""
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    MILESTONE_REACHED = "milestone_reached"
    DAILY_LOGIN = "daily_login"
    CONTENT_UPLOAD = "content_upload"
    COLLABORATION_SUCCESS = "collaboration_success"
    QUALITY_BONUS = "quality_bonus"
    ENGAGEMENT_BONUS = "engagement_bonus"
    REVENUE_MILESTONE = "revenue_milestone"
    STREAK_BONUS = "streak_bonus"
    CHALLENGE_COMPLETION = "challenge_completion"
    COMMUNITY_CONTRIBUTION = "community_contribution"
    REFERRAL_BONUS = "referral_bonus"
    SEASONAL_EVENT = "seasonal_event"
    SPECIAL_PROMOTION = "special_promotion"


@dataclass
class Reward:
    """Individual reward definition."""
    id: str
    name: str
    description: str
    reward_type: RewardType
    rarity: RewardRarity
    value: Union[float, int, str, Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    expiry_date: Optional[datetime] = None
    transferable: bool = False
    stackable: bool = True
    max_quantity: Optional[int] = None
    prerequisites: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RewardBundle:
    """Collection of rewards distributed together."""
    id: str
    name: str
    description: str
    rewards: List[Reward]
    bonus_multiplier: float = 1.0
    total_value: float = 0.0
    source: RewardSource = RewardSource.ACHIEVEMENT_UNLOCK
    recipient_id: str = ""
    distributed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RewardDistributionRule:
    """Rule for automatic reward distribution."""
    id: str
    name: str
    trigger_conditions: Dict[str, Any]
    reward_templates: List[Dict[str, Any]]
    probability: float = 1.0
    cooldown_period: Optional[timedelta] = None
    max_distributions_per_user: Optional[int] = None
    is_active: bool = True
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserRewardHistory:
    """User's reward history and statistics."""
    user_id: str
    total_rewards_received: int = 0
    total_value_received: float = 0.0
    rewards_by_type: Dict[str, int] = field(default_factory=dict)
    rewards_by_rarity: Dict[str, int] = field(default_factory=dict)
    last_reward_date: Optional[datetime] = None
    active_rewards: List[str] = field(default_factory=list)
    expired_rewards: List[str] = field(default_factory=list)
    favorite_reward_types: List[str] = field(default_factory=list)


class RewardDistributor:
    """
    Comprehensive reward distribution system.
    
    Provides intelligent reward calculation, distribution strategies,
    reward bundling, and comprehensive analytics for user engagement.
    """
    
    def __init__(self):
        """Initialize the reward distributor."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.initialized = False
        
        # Reward definitions and templates
        self.reward_templates: Dict[str, Reward] = {}
        self.distribution_rules: Dict[str, RewardDistributionRule] = {}
        
        # User reward tracking
        self.user_histories: Dict[str, UserRewardHistory] = {}
        self.user_active_rewards: Dict[str, List[Reward]] = {}
        
        # Distribution tracking
        self.distribution_log: List[RewardBundle] = []
        self.cooldown_tracking: Dict[str, Dict[str, datetime]] = {}
        
        # Analytics and statistics
        self.distribution_stats: Dict[str, Any] = {}
        
        self.logger.info("RewardDistributor initialized")
    
    async def initialize(self) -> bool:
        """Initialize the reward distributor with default templates and rules."""
        try:
            # Load default reward templates
            await self._load_default_reward_templates()
            
            # Load default distribution rules
            await self._load_default_distribution_rules()
            
            # Start background tasks
            asyncio.create_task(self._cleanup_expired_rewards())
            asyncio.create_task(self._update_statistics())
            
            self.initialized = True
            self.logger.info(f"✅ RewardDistributor initialized with {len(self.reward_templates)} templates and {len(self.distribution_rules)} rules")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize RewardDistributor: {e}")
            return False
    
    async def _load_default_reward_templates(self):
        """Load default reward templates."""
        default_templates = [
            # Point Rewards
            Reward(
                id="points_small",
                name="Point Boost",
                description="A small boost of points to help you progress",
                reward_type=RewardType.POINTS,
                rarity=RewardRarity.COMMON,
                value=100,
                stackable=True
            ),
            Reward(
                id="points_medium",
                name="Point Bundle",
                description="A nice bundle of points for your achievements",
                reward_type=RewardType.POINTS,
                rarity=RewardRarity.UNCOMMON,
                value=500,
                stackable=True
            ),
            Reward(
                id="points_large",
                name="Point Jackpot",
                description="A massive point reward for exceptional performance",
                reward_type=RewardType.POINTS,
                rarity=RewardRarity.RARE,
                value=2000,
                stackable=True
            ),
            
            # Currency Rewards
            Reward(
                id="currency_starter",
                name="Starter Coins",
                description="Some coins to get you started on your journey",
                reward_type=RewardType.CURRENCY,
                rarity=RewardRarity.COMMON,
                value={"type": "platform_coins", "amount": 50},
                stackable=True
            ),
            Reward(
                id="currency_bonus",
                name="Bonus Coins",
                description="Extra coins for your hard work",
                reward_type=RewardType.CURRENCY,
                rarity=RewardRarity.UNCOMMON,
                value={"type": "platform_coins", "amount": 200},
                stackable=True
            ),
            Reward(
                id="currency_premium",
                name="Premium Currency",
                description="Exclusive premium currency for special purchases",
                reward_type=RewardType.CURRENCY,
                rarity=RewardRarity.EPIC,
                value={"type": "premium_currency", "amount": 100},
                stackable=True
            ),
            
            # Premium Time Rewards
            Reward(
                id="premium_day",
                name="Premium Day Pass",
                description="24 hours of premium features access",
                reward_type=RewardType.PREMIUM_TIME,
                rarity=RewardRarity.UNCOMMON,
                value={"duration": 1, "unit": "days"},
                expiry_date=datetime.utcnow() + timedelta(days=30),
                stackable=True
            ),
            Reward(
                id="premium_week",
                name="Premium Week Pass",
                description="7 days of premium features access",
                reward_type=RewardType.PREMIUM_TIME,
                rarity=RewardRarity.RARE,
                value={"duration": 7, "unit": "days"},
                expiry_date=datetime.utcnow() + timedelta(days=30),
                stackable=True
            ),
            Reward(
                id="premium_month",
                name="Premium Month Pass",
                description="30 days of premium features access",
                reward_type=RewardType.PREMIUM_TIME,
                rarity=RewardRarity.EPIC,
                value={"duration": 30, "unit": "days"},
                expiry_date=datetime.utcnow() + timedelta(days=60),
                stackable=True
            ),
            
            # Feature Access Rewards
            Reward(
                id="advanced_analytics",
                name="Advanced Analytics Access",
                description="Access to advanced analytics dashboard for 30 days",
                reward_type=RewardType.FEATURE_ACCESS,
                rarity=RewardRarity.RARE,
                value={"feature": "advanced_analytics", "duration": 30},
                expiry_date=datetime.utcnow() + timedelta(days=30),
                stackable=False
            ),
            Reward(
                id="priority_processing",
                name="Priority Processing",
                description="Priority content processing for faster results",
                reward_type=RewardType.FEATURE_ACCESS,
                rarity=RewardRarity.EPIC,
                value={"feature": "priority_processing", "uses": 10},
                stackable=True
            ),
            
            # Boost Rewards
            Reward(
                id="collaboration_boost",
                name="Collaboration Boost",
                description="Increased visibility in collaboration matching",
                reward_type=RewardType.COLLABORATION_BOOST,
                rarity=RewardRarity.UNCOMMON,
                value={"multiplier": 1.5, "duration": 7},
                expiry_date=datetime.utcnow() + timedelta(days=14),
                stackable=False
            ),
            Reward(
                id="visibility_boost",
                name="Visibility Boost",
                description="Enhanced content visibility for 24 hours",
                reward_type=RewardType.VISIBILITY_BOOST,
                rarity=RewardRarity.RARE,
                value={"multiplier": 2.0, "duration": 1},
                expiry_date=datetime.utcnow() + timedelta(days=7),
                stackable=False
            ),
            
            # Revenue Share Rewards
            Reward(
                id="revenue_boost_small",
                name="Revenue Boost 5%",
                description="5% increased revenue share for 7 days",
                reward_type=RewardType.REVENUE_SHARE,
                rarity=RewardRarity.RARE,
                value={"percentage": 0.05, "duration": 7},
                expiry_date=datetime.utcnow() + timedelta(days=14),
                stackable=False
            ),
            Reward(
                id="revenue_boost_large",
                name="Revenue Boost 10%",
                description="10% increased revenue share for 14 days",
                reward_type=RewardType.REVENUE_SHARE,
                rarity=RewardRarity.LEGENDARY,
                value={"percentage": 0.10, "duration": 14},
                expiry_date=datetime.utcnow() + timedelta(days=30),
                stackable=False
            ),
            
            # Storage Rewards
            Reward(
                id="storage_small",
                name="Extra Storage",
                description="Additional 1GB of content storage",
                reward_type=RewardType.STORAGE_SPACE,
                rarity=RewardRarity.UNCOMMON,
                value={"amount": 1, "unit": "GB", "permanent": True},
                stackable=True
            ),
            Reward(
                id="storage_large",
                name="Storage Upgrade",
                description="Additional 10GB of content storage",
                reward_type=RewardType.STORAGE_SPACE,
                rarity=RewardRarity.EPIC,
                value={"amount": 10, "unit": "GB", "permanent": True},
                stackable=True
            ),
            
            # Special Event Access
            Reward(
                id="beta_access",
                name="Beta Feature Access",
                description="Early access to beta features and testing",
                reward_type=RewardType.SPECIAL_EVENT_ACCESS,
                rarity=RewardRarity.LEGENDARY,
                value={"event": "beta_program", "permanent": True},
                stackable=False,
                max_quantity=1
            ),
            Reward(
                id="exclusive_webinar",
                name="Exclusive Webinar Invitation",
                description="Invitation to exclusive creator masterclass",
                reward_type=RewardType.SPECIAL_EVENT_ACCESS,
                rarity=RewardRarity.EPIC,
                value={"event": "creator_masterclass", "date": "2025-03-15"},
                expiry_date=datetime(2025, 3, 15),
                stackable=False
            )
        ]
        
        for template in default_templates:
            self.reward_templates[template.id] = template
        
        self.logger.info(f"Loaded {len(default_templates)} default reward templates")
    
    async def _load_default_distribution_rules(self):
        """Load default reward distribution rules."""
        default_rules = [
            # Achievement-based rewards
            RewardDistributionRule(
                id="first_achievement",
                name="First Achievement Reward",
                trigger_conditions={
                    "source": "achievement_unlock",
                    "achievement_tier": "bronze",
                    "is_first": True
                },
                reward_templates=[
                    {"template_id": "points_medium", "probability": 1.0},
                    {"template_id": "currency_starter", "probability": 0.8},
                    {"template_id": "premium_day", "probability": 0.3}
                ],
                probability=1.0,
                priority=10
            ),
            RewardDistributionRule(
                id="gold_achievement",
                name="Gold Achievement Reward",
                trigger_conditions={
                    "source": "achievement_unlock",
                    "achievement_tier": "gold"
                },
                reward_templates=[
                    {"template_id": "points_large", "probability": 1.0},
                    {"template_id": "currency_bonus", "probability": 0.9},
                    {"template_id": "premium_week", "probability": 0.5},
                    {"template_id": "collaboration_boost", "probability": 0.3}
                ],
                probability=1.0,
                priority=8
            ),
            RewardDistributionRule(
                id="legendary_achievement",
                name="Legendary Achievement Reward",
                trigger_conditions={
                    "source": "achievement_unlock",
                    "achievement_tier": "legendary"
                },
                reward_templates=[
                    {"template_id": "points_large", "probability": 1.0, "multiplier": 2.0},
                    {"template_id": "currency_premium", "probability": 1.0},
                    {"template_id": "premium_month", "probability": 0.8},
                    {"template_id": "revenue_boost_large", "probability": 0.6},
                    {"template_id": "beta_access", "probability": 0.2}
                ],
                probability=1.0,
                priority=5
            ),
            
            # Milestone rewards
            RewardDistributionRule(
                id="content_milestone",
                name="Content Creation Milestone",
                trigger_conditions={
                    "source": "milestone_reached",
                    "milestone_type": "content_count",
                    "value": {"multiple_of": 10}
                },
                reward_templates=[
                    {"template_id": "points_medium", "probability": 1.0},
                    {"template_id": "storage_small", "probability": 0.7},
                    {"template_id": "visibility_boost", "probability": 0.2}
                ],
                probability=1.0,
                cooldown_period=timedelta(hours=24),
                priority=7
            ),
            RewardDistributionRule(
                id="collaboration_milestone",
                name="Collaboration Milestone",
                trigger_conditions={
                    "source": "milestone_reached",
                    "milestone_type": "collaborations",
                    "value": {"multiple_of": 5}
                },
                reward_templates=[
                    {"template_id": "points_medium", "probability": 1.0},
                    {"template_id": "collaboration_boost", "probability": 0.8},
                    {"template_id": "premium_day", "probability": 0.4}
                ],
                probability=1.0,
                cooldown_period=timedelta(hours=48),
                priority=6
            ),
            
            # Daily activity rewards
            RewardDistributionRule(
                id="daily_login_streak",
                name="Daily Login Streak Reward",
                trigger_conditions={
                    "source": "streak_bonus",
                    "streak_type": "daily_login",
                    "streak_count": {"min": 7}
                },
                reward_templates=[
                    {"template_id": "points_small", "probability": 1.0, "streak_multiplier": True},
                    {"template_id": "currency_starter", "probability": 0.5},
                    {"template_id": "premium_day", "probability": 0.1}
                ],
                probability=1.0,
                cooldown_period=timedelta(days=1),
                priority=9
            ),
            
            # Quality-based rewards
            RewardDistributionRule(
                id="high_quality_content",
                name="High Quality Content Reward",
                trigger_conditions={
                    "source": "quality_bonus",
                    "quality_score": {"min": 0.9}
                },
                reward_templates=[
                    {"template_id": "points_medium", "probability": 1.0},
                    {"template_id": "advanced_analytics", "probability": 0.3},
                    {"template_id": "priority_processing", "probability": 0.2}
                ],
                probability=0.8,
                cooldown_period=timedelta(hours=12),
                priority=6
            ),
            
            # Revenue-based rewards
            RewardDistributionRule(
                id="revenue_milestone",
                name="Revenue Milestone Reward",
                trigger_conditions={
                    "source": "revenue_milestone",
                    "amount": {"min": 100}
                },
                reward_templates=[
                    {"template_id": "points_large", "probability": 1.0},
                    {"template_id": "currency_premium", "probability": 0.7},
                    {"template_id": "revenue_boost_small", "probability": 0.4}
                ],
                probability=1.0,
                priority=4
            ),
            
            # Community contribution rewards
            RewardDistributionRule(
                id="community_helper",
                name="Community Helper Reward",
                trigger_conditions={
                    "source": "community_contribution",
                    "contribution_type": "help_provided"
                },
                reward_templates=[
                    {"template_id": "points_small", "probability": 1.0},
                    {"template_id": "currency_starter", "probability": 0.6}
                ],
                probability=0.9,
                cooldown_period=timedelta(hours=6),
                priority=8
            ),
            
            # Seasonal/Special event rewards
            RewardDistributionRule(
                id="seasonal_bonus",
                name="Seasonal Event Bonus",
                trigger_conditions={
                    "source": "seasonal_event",
                    "event_type": "any"
                },
                reward_templates=[
                    {"template_id": "points_medium", "probability": 1.0, "multiplier": 1.5},
                    {"template_id": "currency_bonus", "probability": 0.8},
                    {"template_id": "exclusive_webinar", "probability": 0.3}
                ],
                probability=1.0,
                priority=3
            )
        ]
        
        for rule in default_rules:
            self.distribution_rules[rule.id] = rule
        
        self.logger.info(f"Loaded {len(default_rules)} default distribution rules")
    
    async def distribute_rewards(
        self,
        user_id: str,
        source: str,
        context_data: Dict[str, Any],
        points_earned: float = 0
    ) -> Dict[str, Any]:
        """Distribute rewards based on context and rules."""
        try:
            # Find applicable distribution rules
            applicable_rules = self._find_applicable_rules(source, context_data)
            
            if not applicable_rules:
                return {"rewards": [], "message": "No applicable reward rules found"}
            
            # Get or create user history
            if user_id not in self.user_histories:
                self.user_histories[user_id] = UserRewardHistory(user_id=user_id)
            
            user_history = self.user_histories[user_id]
            reward_bundles = []
            
            # Process each applicable rule
            for rule in applicable_rules:
                # Check cooldown
                if not self._check_cooldown(user_id, rule.id):
                    continue
                
                # Check distribution limits
                if not self._check_distribution_limits(user_id, rule):
                    continue
                
                # Generate rewards from rule
                bundle = await self._generate_reward_bundle(user_id, rule, context_data, points_earned)
                
                if bundle and bundle.rewards:
                    reward_bundles.append(bundle)
                    
                    # Update cooldown tracking
                    self._update_cooldown(user_id, rule.id)
                    
                    # Distribute rewards to user
                    await self._apply_rewards_to_user(user_id, bundle)
            
            # Update user history
            self._update_user_history(user_history, reward_bundles)
            
            return {
                "rewards": [bundle.id for bundle in reward_bundles],
                "total_bundles": len(reward_bundles),
                "total_value": sum(bundle.total_value for bundle in reward_bundles),
                "user_total_rewards": user_history.total_rewards_received
            }
            
        except Exception as e:
            self.logger.error(f"Error distributing rewards for user {user_id}: {e}")
            return {"rewards": [], "error": str(e)}
    
    def _find_applicable_rules(
        self,
        source: str,
        context_data: Dict[str, Any]
    ) -> List[RewardDistributionRule]:
        """Find distribution rules applicable to the given context."""
        applicable_rules = []
        
        for rule in self.distribution_rules.values():
            if not rule.is_active:
                continue
            
            # Check probability
            if random.random() > rule.probability:
                continue
            
            # Check trigger conditions
            if self._check_rule_conditions(rule, source, context_data):
                applicable_rules.append(rule)
        
        # Sort by priority (lower number = higher priority)
        applicable_rules.sort(key=lambda r: r.priority)
        
        return applicable_rules
    
    def _check_rule_conditions(
        self,
        rule: RewardDistributionRule,
        source: str,
        context_data: Dict[str, Any]
    ) -> bool:
        """Check if rule conditions are met."""
        try:
            conditions = rule.trigger_conditions
            
            # Check source
            if "source" in conditions and conditions["source"] != source:
                return False
            
            # Check other conditions
            for condition_key, condition_value in conditions.items():
                if condition_key == "source":
                    continue
                
                if condition_key not in context_data:
                    return False
                
                actual_value = context_data[condition_key]
                
                if isinstance(condition_value, dict):
                    # Complex condition checking
                    if "min" in condition_value and actual_value < condition_value["min"]:
                        return False
                    if "max" in condition_value and actual_value > condition_value["max"]:
                        return False
                    if "multiple_of" in condition_value and actual_value % condition_value["multiple_of"] != 0:
                        return False
                elif isinstance(condition_value, (list, tuple)):
                    if actual_value not in condition_value:
                        return False
                else:
                    if actual_value != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rule conditions: {e}")
            return False
    
    def _check_cooldown(self, user_id: str, rule_id: str) -> bool:
        """Check if rule is not in cooldown for user."""
        if user_id not in self.cooldown_tracking:
            return True
        
        if rule_id not in self.cooldown_tracking[user_id]:
            return True
        
        rule = self.distribution_rules.get(rule_id)
        if not rule or not rule.cooldown_period:
            return True
        
        last_distribution = self.cooldown_tracking[user_id][rule_id]
        cooldown_end = last_distribution + rule.cooldown_period
        
        return datetime.utcnow() > cooldown_end
    
    def _check_distribution_limits(self, user_id: str, rule: RewardDistributionRule) -> bool:
        """Check if user hasn't exceeded distribution limits."""
        if not rule.max_distributions_per_user:
            return True
        
        # Count distributions for this rule and user
        user_distributions = sum(
            1 for bundle in self.distribution_log
            if bundle.recipient_id == user_id and 
            any(reward.metadata.get("rule_id") == rule.id for reward in bundle.rewards)
        )
        
        return user_distributions < rule.max_distributions_per_user
    
    async def _generate_reward_bundle(
        self,
        user_id: str,
        rule: RewardDistributionRule,
        context_data: Dict[str, Any],
        points_earned: float
    ) -> Optional[RewardBundle]:
        """Generate a reward bundle from a distribution rule."""
        try:
            rewards = []
            total_value = 0.0
            
            for template_config in rule.reward_templates:
                template_id = template_config["template_id"]
                probability = template_config.get("probability", 1.0)
                
                # Check probability
                if random.random() > probability:
                    continue
                
                # Get reward template
                template = self.reward_templates.get(template_id)
                if not template:
                    continue
                
                # Create reward instance
                reward = await self._create_reward_instance(
                    template, template_config, context_data, points_earned
                )
                
                if reward:
                    reward.metadata["rule_id"] = rule.id
                    reward.metadata["source"] = context_data.get("source", "unknown")
                    rewards.append(reward)
                    total_value += self._calculate_reward_value(reward)
            
            if not rewards:
                return None
            
            # Create bundle
            bundle = RewardBundle(
                id=str(uuid4()),
                name=f"{rule.name} Bundle",
                description=f"Rewards from {rule.name}",
                rewards=rewards,
                total_value=total_value,
                source=RewardSource(context_data.get("source", "achievement_unlock")),
                recipient_id=user_id
            )
            
            # Add to distribution log
            self.distribution_log.append(bundle)
            
            return bundle
            
        except Exception as e:
            self.logger.error(f"Error generating reward bundle: {e}")
            return None
    
    async def _create_reward_instance(
        self,
        template: Reward,
        template_config: Dict[str, Any],
        context_data: Dict[str, Any],
        points_earned: float
    ) -> Optional[Reward]:
        """Create a specific reward instance from template."""
        try:
            # Create base reward from template
            reward = Reward(
                id=str(uuid4()),
                name=template.name,
                description=template.description,
                reward_type=template.reward_type,
                rarity=template.rarity,
                value=template.value,
                metadata=template.metadata.copy(),
                expiry_date=template.expiry_date,
                transferable=template.transferable,
                stackable=template.stackable,
                max_quantity=template.max_quantity,
                prerequisites=template.prerequisites.copy()
            )
            
            # Apply multipliers and modifications
            multiplier = template_config.get("multiplier", 1.0)
            
            # Streak multiplier
            if template_config.get("streak_multiplier") and "streak_count" in context_data:
                streak_count = context_data["streak_count"]
                streak_multiplier = min(3.0, 1 + (streak_count - 1) * 0.1)  # Cap at 3x
                multiplier *= streak_multiplier
            
            # Points-based scaling
            if template_config.get("points_scale") and points_earned > 0:
                points_multiplier = 1 + (points_earned / 1000) * 0.1  # 10% per 1000 points
                multiplier = min(2.0, multiplier * points_multiplier)  # Cap at 2x
            
            # Apply multiplier to value
            if isinstance(reward.value, (int, float)):
                reward.value = reward.value * multiplier
            elif isinstance(reward.value, dict) and "amount" in reward.value:
                reward.value["amount"] = int(reward.value["amount"] * multiplier)
            
            # Add context metadata
            reward.metadata.update({
                "context": context_data,
                "generation_multiplier": multiplier,
                "base_template": template.id
            })
            
            return reward
            
        except Exception as e:
            self.logger.error(f"Error creating reward instance: {e}")
            return None
    
    def _calculate_reward_value(self, reward: Reward) -> float:
        """Calculate monetary/point value of a reward."""
        try:
            if reward.reward_type == RewardType.POINTS:
                return float(reward.value) * 0.01  # 1 point = $0.01 equivalent
            
            elif reward.reward_type == RewardType.CURRENCY:
                if isinstance(reward.value, dict):
                    amount = reward.value.get("amount", 0)
                    currency_type = reward.value.get("type", "platform_coins")
                    
                    # Currency conversion rates
                    rates = {
                        "platform_coins": 0.005,  # $0.005 per coin
                        "premium_currency": 0.02   # $0.02 per premium coin
                    }
                    return amount * rates.get(currency_type, 0.01)
                return 0.0
            
            elif reward.reward_type == RewardType.PREMIUM_TIME:
                if isinstance(reward.value, dict):
                    duration = reward.value.get("duration", 0)
                    unit = reward.value.get("unit", "days")
                    
                    # Premium value per day
                    daily_value = 2.99  # $2.99 per day
                    
                    if unit == "days":
                        return duration * daily_value
                    elif unit == "hours":
                        return (duration / 24) * daily_value
                return 0.0
            
            elif reward.reward_type in [RewardType.REVENUE_SHARE, RewardType.COLLABORATION_BOOST]:
                # Estimated value based on boost percentage and duration
                if isinstance(reward.value, dict):
                    percentage = reward.value.get("percentage", 0.05)
                    duration = reward.value.get("duration", 7)
                    # Rough estimate: $10 base value per day
                    return percentage * duration * 10
                return 0.0
            
            elif reward.reward_type == RewardType.STORAGE_SPACE:
                if isinstance(reward.value, dict):
                    amount = reward.value.get("amount", 0)
                    # $0.10 per GB
                    return amount * 0.10
                return 0.0
            
            else:
                # Default value for other reward types
                rarity_values = {
                    RewardRarity.COMMON: 1.0,
                    RewardRarity.UNCOMMON: 2.5,
                    RewardRarity.RARE: 5.0,
                    RewardRarity.EPIC: 10.0,
                    RewardRarity.LEGENDARY: 25.0,
                    RewardRarity.MYTHICAL: 50.0
                }
                return rarity_values.get(reward.rarity, 1.0)
                
        except Exception as e:
            self.logger.error(f"Error calculating reward value: {e}")
            return 0.0
    
    def _update_cooldown(self, user_id: str, rule_id: str):
        """Update cooldown tracking for a rule."""
        if user_id not in self.cooldown_tracking:
            self.cooldown_tracking[user_id] = {}
        
        self.cooldown_tracking[user_id][rule_id] = datetime.utcnow()
    
    async def _apply_rewards_to_user(self, user_id: str, bundle: RewardBundle):
        """Apply rewards to user's account."""
        try:
            if user_id not in self.user_active_rewards:
                self.user_active_rewards[user_id] = []
            
            # Add rewards to user's active rewards
            for reward in bundle.rewards:
                self.user_active_rewards[user_id].append(reward)
            
            self.logger.info(f"💰 Distributed {len(bundle.rewards)} rewards to user {user_id} (value: ${bundle.total_value:.2f})")
            
        except Exception as e:
            self.logger.error(f"Error applying rewards to user: {e}")
    
    def _update_user_history(self, user_history: UserRewardHistory, bundles: List[RewardBundle]):
        """Update user's reward history."""
        try:
            for bundle in bundles:
                user_history.total_rewards_received += len(bundle.rewards)
                user_history.total_value_received += bundle.total_value
                user_history.last_reward_date = datetime.utcnow()
                
                # Update type and rarity distributions
                for reward in bundle.rewards:
                    reward_type = reward.reward_type.value
                    reward_rarity = reward.rarity.value
                    
                    user_history.rewards_by_type[reward_type] = user_history.rewards_by_type.get(reward_type, 0) + 1
                    user_history.rewards_by_rarity[reward_rarity] = user_history.rewards_by_rarity.get(reward_rarity, 0) + 1
                    
                    # Update active rewards
                    user_history.active_rewards.append(reward.id)
            
            # Update favorite reward types
            self._update_favorite_types(user_history)
            
        except Exception as e:
            self.logger.error(f"Error updating user history: {e}")
    
    def _update_favorite_types(self, user_history: UserRewardHistory):
        """Update user's favorite reward types based on history."""
        try:
            # Sort reward types by frequency
            sorted_types = sorted(
                user_history.rewards_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Update favorite types (top 3)
            user_history.favorite_reward_types = [reward_type for reward_type, _ in sorted_types[:3]]
            
        except Exception as e:
            self.logger.error(f"Error updating favorite types: {e}")
    
    async def get_user_rewards(self, user_id: str) -> Dict[str, Any]:
        """Get user's reward information."""
        try:
            user_history = self.user_histories.get(user_id, UserRewardHistory(user_id=user_id))
            active_rewards = self.user_active_rewards.get(user_id, [])
            
            # Categorize active rewards
            active_by_type = {}
            for reward in active_rewards:
                reward_type = reward.reward_type.value
                if reward_type not in active_by_type:
                    active_by_type[reward_type] = []
                active_by_type[reward_type].append({
                    "id": reward.id,
                    "name": reward.name,
                    "description": reward.description,
                    "value": reward.value,
                    "rarity": reward.rarity.value,
                    "expiry_date": reward.expiry_date,
                    "metadata": reward.metadata
                })
            
            return {
                "user_id": user_id,
                "total_rewards_received": user_history.total_rewards_received,
                "total_value_received": user_history.total_value_received,
                "rewards_by_type": user_history.rewards_by_type,
                "rewards_by_rarity": user_history.rewards_by_rarity,
                "last_reward_date": user_history.last_reward_date,
                "active_rewards": active_by_type,
                "active_rewards_count": len(active_rewards),
                "favorite_reward_types": user_history.favorite_reward_types,
                "estimated_portfolio_value": sum(self._calculate_reward_value(r) for r in active_rewards)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user rewards: {e}")
            return {}
    
    async def _cleanup_expired_rewards(self):
        """Background task to cleanup expired rewards."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                current_time = datetime.utcnow()
                total_cleaned = 0
                
                # Clean expired rewards from user accounts
                for user_id, rewards in self.user_active_rewards.items():
                    expired_rewards = []
                    
                    for reward in rewards:
                        if reward.expiry_date and current_time > reward.expiry_date:
                            expired_rewards.append(reward)
                    
                    # Remove expired rewards
                    for expired_reward in expired_rewards:
                        rewards.remove(expired_reward)
                        total_cleaned += 1
                        
                        # Move to expired list in user history
                        if user_id in self.user_histories:
                            self.user_histories[user_id].expired_rewards.append(expired_reward.id)
                
                if total_cleaned > 0:
                    self.logger.info(f"Cleaned up {total_cleaned} expired rewards")
                
            except Exception as e:
                self.logger.error(f"Error in cleanup expired rewards task: {e}")
                await asyncio.sleep(1800)  # Retry in 30 minutes
    
    async def _update_statistics(self):
        """Background task to update distribution statistics."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Calculate distribution statistics
                total_distributions = len(self.distribution_log)
                total_value_distributed = sum(bundle.total_value for bundle in self.distribution_log)
                
                # Distribution by source
                source_distribution = {}
                for bundle in self.distribution_log:
                    source = bundle.source.value
                    source_distribution[source] = source_distribution.get(source, 0) + 1
                
                # Distribution by reward type
                type_distribution = {}
                for bundle in self.distribution_log:
                    for reward in bundle.rewards:
                        reward_type = reward.reward_type.value
                        type_distribution[reward_type] = type_distribution.get(reward_type, 0) + 1
                
                self.distribution_stats = {
                    "total_distributions": total_distributions,
                    "total_value_distributed": total_value_distributed,
                    "source_distribution": source_distribution,
                    "type_distribution": type_distribution,
                    "active_users_with_rewards": len(self.user_active_rewards),
                    "last_updated": datetime.utcnow()
                }
                
            except Exception as e:
                self.logger.error(f"Error updating statistics: {e}")
                await asyncio.sleep(600)  # Retry in 10 minutes
    
    async def get_reward_statistics(self) -> Dict[str, Any]:
        """Get comprehensive reward distribution statistics."""
        try:
            # Get current statistics
            stats = self.distribution_stats.copy()
            
            # Add additional metrics
            stats.update({
                "total_reward_templates": len(self.reward_templates),
                "active_distribution_rules": len([r for r in self.distribution_rules.values() if r.is_active]),
                "users_with_history": len(self.user_histories),
                "average_rewards_per_user": (
                    sum(h.total_rewards_received for h in self.user_histories.values()) / 
                    len(self.user_histories)
                ) if self.user_histories else 0,
                "average_value_per_user": (
                    sum(h.total_value_received for h in self.user_histories.values()) / 
                    len(self.user_histories)
                ) if self.user_histories else 0
            })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting reward statistics: {e}")
            return {}