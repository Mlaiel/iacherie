"""Reward Distributor - Distribution récompenses
============================================

Reward distribution system for calculating, managing, and distributing
various types of rewards to content creators based on their activities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid


class RewardType(str, Enum):
    """Types of rewards in the system."""
    POINTS = "points"
    CURRENCY = "currency"
    BADGE = "badge"
    NFT = "nft"
    BOOST = "boost"
    ACCESS = "access"
    SUBSCRIPTION = "subscription"
    REVENUE_SHARE = "revenue_share"
    PHYSICAL_ITEM = "physical_item"


class RewardStatus(str, Enum):
    """Status of reward distribution."""
    PENDING = "pending"
    CALCULATING = "calculating"
    APPROVED = "approved"
    DISTRIBUTED = "distributed"
    CLAIMED = "claimed"
    EXPIRED = "expired"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RewardTrigger(str, Enum):
    """Events that trigger reward distribution."""
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    MILESTONE_REACHED = "milestone_reached"
    CHALLENGE_COMPLETE = "challenge_complete"
    TIER_PROMOTION = "tier_promotion"
    COLLABORATION_COMPLETE = "collaboration_complete"
    CONTENT_VIRAL = "content_viral"
    DAILY_LOGIN = "daily_login"
    REFERRAL_SUCCESS = "referral_success"
    SPECIAL_EVENT = "special_event"
    MANUAL_AWARD = "manual_award"


@dataclass
class Reward:
    """Individual reward definition."""
    id: str
    user_id: str
    reward_type: RewardType
    name: str
    description: str
    value: Union[int, float, str, Dict[str, Any]]
    currency_type: Optional[str] = None
    trigger: Optional[RewardTrigger] = None
    trigger_source_id: Optional[str] = None
    status: RewardStatus = RewardStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    distributed_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None


@dataclass
class RewardBundle:
    """Collection of rewards distributed together."""
    id: str
    user_id: str
    name: str
    description: str
    rewards: List[Reward]
    trigger: RewardTrigger
    trigger_source_id: Optional[str] = None
    total_value: Decimal = field(default_factory=lambda: Decimal("0"))
    status: RewardStatus = RewardStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    distributed_at: Optional[datetime] = None


@dataclass
class RewardRule:
    """Rule for automatic reward distribution."""
    id: str
    name: str
    trigger: RewardTrigger
    conditions: Dict[str, Any]
    reward_template: Dict[str, Any]
    is_active: bool = True
    max_per_user: Optional[int] = None
    cooldown_period: Optional[timedelta] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RewardDistributor:
    """
    Advanced reward distribution system providing intelligent reward
    calculation, distribution scheduling, and comprehensive reward analytics.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the reward distributor."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.pending_rewards: List[Reward] = []
        self.reward_bundles: List[RewardBundle] = []
        self.reward_rules: Dict[str, RewardRule] = {}
        self.user_reward_history: Dict[str, List[Reward]] = {}
        
        # Initialize default reward rules
        self._initialize_default_rules()
        
        self.logger.info("RewardDistributor initialized")
    
    def _initialize_default_rules(self):
        """Initialize default reward distribution rules."""
        try:
            # Achievement unlock rewards
            self.reward_rules["achievement_unlock_basic"] = RewardRule(
                id="achievement_unlock_basic",
                name="Basic Achievement Unlock Reward",
                trigger=RewardTrigger.ACHIEVEMENT_UNLOCK,
                conditions={"tier": "bronze"},
                reward_template={
                    "type": RewardType.POINTS,
                    "value": 100,
                    "currency_type": "xp"
                }
            )
            
            self.reward_rules["achievement_unlock_premium"] = RewardRule(
                id="achievement_unlock_premium",
                name="Premium Achievement Unlock Reward",
                trigger=RewardTrigger.ACHIEVEMENT_UNLOCK,
                conditions={"tier": ["gold", "platinum", "diamond"]},
                reward_template={
                    "type": RewardType.CURRENCY,
                    "value": 500,
                    "currency_type": "credits"
                }
            )
            
            # Milestone rewards
            self.reward_rules["milestone_upload"] = RewardRule(
                id="milestone_upload",
                name="Upload Milestone Reward",
                trigger=RewardTrigger.MILESTONE_REACHED,
                conditions={"metric": "uploads", "milestone": [10, 50, 100, 500, 1000]},
                reward_template={
                    "type": RewardType.CURRENCY,
                    "value": "dynamic",  # Calculated based on milestone
                    "currency_type": "credits"
                }
            )
            
            # Challenge completion rewards
            self.reward_rules["challenge_complete"] = RewardRule(
                id="challenge_complete",
                name="Challenge Completion Reward",
                trigger=RewardTrigger.CHALLENGE_COMPLETE,
                conditions={},
                reward_template={
                    "type": RewardType.POINTS,
                    "value": "dynamic",  # Based on challenge difficulty
                    "currency_type": "xp"
                }
            )
            
            # Daily login rewards
            self.reward_rules["daily_login"] = RewardRule(
                id="daily_login",
                name="Daily Login Reward",
                trigger=RewardTrigger.DAILY_LOGIN,
                conditions={},
                reward_template={
                    "type": RewardType.POINTS,
                    "value": 25,
                    "currency_type": "credits"
                },
                max_per_user=1,
                cooldown_period=timedelta(hours=20)
            )
            
            # Viral content rewards
            self.reward_rules["viral_content"] = RewardRule(
                id="viral_content",
                name="Viral Content Reward",
                trigger=RewardTrigger.CONTENT_VIRAL,
                conditions={"views": 1000000},
                reward_template={
                    "type": RewardType.CURRENCY,
                    "value": 2500,
                    "currency_type": "credits"
                }
            )
            
            # Collaboration rewards
            self.reward_rules["collaboration_complete"] = RewardRule(
                id="collaboration_complete",
                name="Collaboration Completion Reward",
                trigger=RewardTrigger.COLLABORATION_COMPLETE,
                conditions={},
                reward_template={
                    "type": RewardType.POINTS,
                    "value": 200,
                    "currency_type": "collaboration_coins"
                }
            )
            
            self.logger.info(f"Initialized {len(self.reward_rules)} default reward rules")
            
        except Exception as e:
            self.logger.error(f"Error initializing default reward rules: {e}")
    
    async def distribute_reward(
        self,
        user_id: str,
        reward_type: RewardType,
        name: str,
        description: str,
        value: Union[int, float, str, Dict[str, Any]],
        trigger: Optional[RewardTrigger] = None,
        trigger_source_id: Optional[str] = None,
        currency_type: Optional[str] = None,
        expires_in: Optional[timedelta] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Distribute a reward to a user."""
        try:
            reward_id = str(uuid.uuid4())
            expires_at = None
            if expires_in:
                expires_at = datetime.now(timezone.utc) + expires_in
            
            reward = Reward(
                id=reward_id,
                user_id=user_id,
                reward_type=reward_type,
                name=name,
                description=description,
                value=value,
                currency_type=currency_type,
                trigger=trigger,
                trigger_source_id=trigger_source_id,
                status=RewardStatus.APPROVED,
                metadata=metadata or {},
                expires_at=expires_at
            )
            
            # Process the reward distribution
            success = await self._process_reward_distribution(reward)
            
            if success:
                # Add to user history
                if user_id not in self.user_reward_history:
                    self.user_reward_history[user_id] = []
                self.user_reward_history[user_id].append(reward)
                
                reward.status = RewardStatus.DISTRIBUTED
                reward.distributed_at = datetime.now(timezone.utc)
                
                self.logger.info(f"🎁 Distributed reward '{name}' to user {user_id}")
                return reward_id
            else:
                reward.status = RewardStatus.FAILED
                self.pending_rewards.append(reward)
                return None
            
        except Exception as e:
            self.logger.error(f"Error distributing reward: {e}")
            return None
    
    async def _process_reward_distribution(self, reward: Reward) -> bool:
        """Process the actual distribution of a reward."""
        try:
            reward_type = reward.reward_type
            
            if reward_type == RewardType.POINTS:
                # Award points through point system
                from .point_system import get_point_system
                point_system = get_point_system()
                
                success = await point_system.award_points(
                    reward.user_id,
                    reward.currency_type,
                    reward.value,
                    reward.trigger.value if reward.trigger else "manual",
                    reward.description,
                    reward.metadata
                )
                return success
            
            elif reward_type == RewardType.CURRENCY:
                # Award currency (simplified - would integrate with payment system)
                self.logger.info(f"💰 Awarded {reward.value} {reward.currency_type} to {reward.user_id}")
                return True
            
            elif reward_type == RewardType.BADGE:
                # Award badge through badge system
                from ..achievements.badge_system import get_badge_system
                badge_system = get_badge_system()
                
                success = await badge_system.award_badge(
                    reward.user_id,
                    str(reward.value),
                    reward.description,
                    reward.metadata
                )
                return success
            
            elif reward_type == RewardType.BOOST:
                # Apply boost (simplified)
                self.logger.info(f"⚡ Applied boost {reward.value} to {reward.user_id}")
                return True
            
            elif reward_type == RewardType.ACCESS:
                # Grant access (simplified)
                self.logger.info(f"🔓 Granted access {reward.value} to {reward.user_id}")
                return True
            
            else:
                # Other reward types (simplified)
                self.logger.info(f"🎁 Distributed {reward_type} reward to {reward.user_id}")
                return True
            
        except Exception as e:
            self.logger.error(f"Error processing reward distribution: {e}")
            return False
    
    async def process_trigger(
        self,
        trigger: RewardTrigger,
        user_id: str,
        trigger_data: Dict[str, Any]
    ) -> List[str]:
        """Process a trigger event and distribute applicable rewards."""
        distributed_rewards = []
        
        try:
            # Find applicable rules
            applicable_rules = [
                rule for rule in self.reward_rules.values()
                if rule.trigger == trigger and rule.is_active
            ]
            
            for rule in applicable_rules:
                # Check conditions
                if await self._check_rule_conditions(rule, user_id, trigger_data):
                    # Check cooldown and limits
                    if await self._check_rule_limits(rule, user_id):
                        # Calculate reward value
                        reward_value = await self._calculate_reward_value(rule, trigger_data)
                        
                        # Distribute reward
                        reward_id = await self.distribute_reward(
                            user_id=user_id,
                            reward_type=RewardType(rule.reward_template["type"]),
                            name=rule.name,
                            description=f"Automatic reward for {trigger.value}",
                            value=reward_value,
                            trigger=trigger,
                            trigger_source_id=trigger_data.get("source_id"),
                            currency_type=rule.reward_template.get("currency_type"),
                            metadata=trigger_data
                        )
                        
                        if reward_id:
                            distributed_rewards.append(reward_id)
            
            self.logger.info(f"Processed trigger {trigger} for {user_id}: {len(distributed_rewards)} rewards distributed")
            return distributed_rewards
            
        except Exception as e:
            self.logger.error(f"Error processing trigger: {e}")
            return []
    
    async def _check_rule_conditions(
        self,
        rule: RewardRule,
        user_id: str,
        trigger_data: Dict[str, Any]
    ) -> bool:
        """Check if rule conditions are met."""
        try:
            conditions = rule.conditions
            
            for condition_key, condition_value in conditions.items():
                data_value = trigger_data.get(condition_key)
                
                if isinstance(condition_value, list):
                    if data_value not in condition_value:
                        return False
                elif isinstance(condition_value, dict):
                    # Complex condition checking
                    if "min" in condition_value and data_value < condition_value["min"]:
                        return False
                    if "max" in condition_value and data_value > condition_value["max"]:
                        return False
                else:
                    if data_value != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rule conditions: {e}")
            return False
    
    async def _check_rule_limits(self, rule: RewardRule, user_id: str) -> bool:
        """Check if rule limits allow distribution."""
        try:
            # Check max per user
            if rule.max_per_user:
                user_rewards = self.user_reward_history.get(user_id, [])
                rule_rewards = [r for r in user_rewards if r.trigger == rule.trigger]
                if len(rule_rewards) >= rule.max_per_user:
                    return False
            
            # Check cooldown
            if rule.cooldown_period:
                user_rewards = self.user_reward_history.get(user_id, [])
                recent_rewards = [
                    r for r in user_rewards
                    if r.trigger == rule.trigger and 
                       r.distributed_at and
                       datetime.now(timezone.utc) - r.distributed_at < rule.cooldown_period
                ]
                if recent_rewards:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rule limits: {e}")
            return False
    
    async def _calculate_reward_value(
        self,
        rule: RewardRule,
        trigger_data: Dict[str, Any]
    ) -> Union[int, float, str]:
        """Calculate dynamic reward value based on rule and trigger data."""
        try:
            template_value = rule.reward_template["value"]
            
            if template_value == "dynamic":
                # Calculate based on trigger and conditions
                if rule.trigger == RewardTrigger.MILESTONE_REACHED:
                    milestone = trigger_data.get("milestone", 1)
                    base_value = 100
                    return base_value * (milestone // 10 + 1)
                
                elif rule.trigger == RewardTrigger.CHALLENGE_COMPLETE:
                    difficulty = trigger_data.get("difficulty", "easy")
                    difficulty_multipliers = {"easy": 50, "medium": 100, "hard": 200, "expert": 400}
                    return difficulty_multipliers.get(difficulty, 50)
                
                elif rule.trigger == RewardTrigger.CONTENT_VIRAL:
                    views = trigger_data.get("views", 0)
                    # Scale reward with view count
                    return min(views // 100000 * 100, 5000)  # Max 5000 credits
                
                return 100  # Default dynamic value
            
            return template_value
            
        except Exception as e:
            self.logger.error(f"Error calculating reward value: {e}")
            return rule.reward_template.get("value", 0)
    
    async def process_action(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process a user action and distribute applicable rewards."""
        results = []
        
        try:
            # Map action types to triggers
            trigger_mapping = {
                "achievement_unlock": RewardTrigger.ACHIEVEMENT_UNLOCK,
                "milestone_reached": RewardTrigger.MILESTONE_REACHED,
                "challenge_complete": RewardTrigger.CHALLENGE_COMPLETE,
                "collaboration_complete": RewardTrigger.COLLABORATION_COMPLETE,
                "content_viral": RewardTrigger.CONTENT_VIRAL,
                "daily_login": RewardTrigger.DAILY_LOGIN,
                "tier_promotion": RewardTrigger.TIER_PROMOTION
            }
            
            trigger = trigger_mapping.get(action_type)
            if trigger:
                reward_ids = await self.process_trigger(trigger, user_id, action_data)
                
                for reward_id in reward_ids:
                    # Find the distributed reward
                    user_rewards = self.user_reward_history.get(user_id, [])
                    reward = next((r for r in user_rewards if r.id == reward_id), None)
                    
                    if reward:
                        results.append({
                            "type": "reward_distributed",
                            "reward_id": reward.id,
                            "reward_type": reward.reward_type,
                            "name": reward.name,
                            "description": reward.description,
                            "value": reward.value,
                            "currency_type": reward.currency_type
                        })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing action for rewards: {e}")
            return []
    
    async def get_user_rewards(
        self,
        user_id: str,
        limit: int = 50,
        status: Optional[RewardStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get user's reward history."""
        try:
            user_rewards = self.user_reward_history.get(user_id, [])
            
            if status:
                user_rewards = [r for r in user_rewards if r.status == status]
            
            # Sort by creation date (newest first)
            user_rewards.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply limit
            limited_rewards = user_rewards[:limit]
            
            return [
                {
                    "id": r.id,
                    "reward_type": r.reward_type,
                    "name": r.name,
                    "description": r.description,
                    "value": r.value,
                    "currency_type": r.currency_type,
                    "status": r.status,
                    "trigger": r.trigger,
                    "created_at": r.created_at.isoformat(),
                    "distributed_at": r.distributed_at.isoformat() if r.distributed_at else None,
                    "claimed_at": r.claimed_at.isoformat() if r.claimed_at else None,
                    "expires_at": r.expires_at.isoformat() if r.expires_at else None
                }
                for r in limited_rewards
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting user rewards: {e}")
            return []
    
    async def claim_reward(self, user_id: str, reward_id: str) -> bool:
        """Mark a reward as claimed by the user."""
        try:
            user_rewards = self.user_reward_history.get(user_id, [])
            reward = next((r for r in user_rewards if r.id == reward_id), None)
            
            if not reward:
                self.logger.warning(f"Reward {reward_id} not found for user {user_id}")
                return False
            
            if reward.status != RewardStatus.DISTRIBUTED:
                self.logger.warning(f"Reward {reward_id} not in distributed status")
                return False
            
            if reward.expires_at and datetime.now(timezone.utc) > reward.expires_at:
                reward.status = RewardStatus.EXPIRED
                self.logger.warning(f"Reward {reward_id} has expired")
                return False
            
            reward.status = RewardStatus.CLAIMED
            reward.claimed_at = datetime.now(timezone.utc)
            
            self.logger.info(f"✅ User {user_id} claimed reward {reward.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error claiming reward: {e}")
            return False


# Global instance
_reward_distributor = None

def get_reward_distributor(database_connection=None, cache_client=None) -> RewardDistributor:
    """Get the global reward distributor instance."""
    global _reward_distributor
    if _reward_distributor is None:
        _reward_distributor = RewardDistributor(database_connection, cache_client)
    return _reward_distributor