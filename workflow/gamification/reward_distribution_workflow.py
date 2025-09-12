"""Reward Distribution Workflow

AI-powered reward distribution and management workflow for gamification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class RewardType(Enum):
    """Types of rewards"""
    POINTS = "points"
    BADGE = "badge"
    ITEM = "item"
    FEATURE_ACCESS = "feature_access"
    DISCOUNT = "discount"
    RECOGNITION = "recognition"


@dataclass
class Reward:
    """Reward definition"""
    reward_id: str
    name: str
    description: str
    reward_type: RewardType
    value: Any
    rarity: str = "common"  # common, rare, epic, legendary
    expires_at: Optional[datetime] = None


@dataclass
class RewardDistribution:
    """Reward distribution event"""
    distribution_id: str
    user_id: str
    reward: Reward
    source: str  # achievement, challenge, milestone, etc.
    distributed_at: datetime = field(default_factory=datetime.utcnow)
    claimed: bool = False
    claimed_at: Optional[datetime] = None


class RewardDistributionWorkflow:
    """AI-powered reward distribution workflow"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.reward_catalog: Dict[str, Reward] = {}
        self.user_rewards: Dict[str, List[RewardDistribution]] = {}
        self._initialize_reward_catalog()
        
    def _initialize_reward_catalog(self):
        """Initialize default reward catalog"""
        default_rewards = [
            Reward("points_100", "100 Points", "100 experience points", RewardType.POINTS, 100),
            Reward("badge_first_post", "First Post", "Created your first post", RewardType.BADGE, "first_post"),
            Reward("feature_analytics", "Analytics Access", "Access to advanced analytics", RewardType.FEATURE_ACCESS, "analytics"),
            Reward("discount_premium", "Premium Discount", "50% off premium features", RewardType.DISCOUNT, 0.5),
        ]
        
        for reward in default_rewards:
            self.reward_catalog[reward.reward_id] = reward
    
    async def distribute_reward(
        self,
        user_id: str,
        reward_id: str,
        source: str,
        auto_claim: bool = False
    ) -> RewardDistribution:
        """
        Distribute a reward to a user
        
        Args:
            user_id: User identifier
            reward_id: Reward identifier from catalog
            source: Source of reward (achievement, challenge, etc.)
            auto_claim: Whether to auto-claim the reward
            
        Returns:
            RewardDistribution object
        """
        try:
            if reward_id not in self.reward_catalog:
                raise WorkflowError(f"Reward {reward_id} not found in catalog")
            
            reward = self.reward_catalog[reward_id]
            distribution_id = f"dist_{int(datetime.utcnow().timestamp())}_{user_id}"
            
            distribution = RewardDistribution(
                distribution_id=distribution_id,
                user_id=user_id,
                reward=reward,
                source=source,
                claimed=auto_claim,
                claimed_at=datetime.utcnow() if auto_claim else None
            )
            
            # Store distribution
            if user_id not in self.user_rewards:
                self.user_rewards[user_id] = []
            self.user_rewards[user_id].append(distribution)
            
            # Apply reward if auto-claimed
            if auto_claim:
                await self._apply_reward(user_id, reward)
            
            # Record metrics
            await self.metrics_collector.record_metric("rewards_distributed", 1)
            await self.metrics_collector.record_metric(f"reward_type_{reward.reward_type.value}", 1)
            
            logger.info(f"Reward {reward_id} distributed to user {user_id} from {source}")
            return distribution
            
        except Exception as e:
            logger.error(f"Reward distribution failed: {e}")
            raise WorkflowError(f"Reward distribution failed: {e}")
    
    async def claim_reward(self, user_id: str, distribution_id: str) -> bool:
        """
        Claim a pending reward
        
        Args:
            user_id: User identifier
            distribution_id: Distribution identifier
            
        Returns:
            True if successfully claimed
        """
        try:
            user_distributions = self.user_rewards.get(user_id, [])
            
            for distribution in user_distributions:
                if distribution.distribution_id == distribution_id:
                    if distribution.claimed:
                        return False  # Already claimed
                    
                    # Check if reward has expired
                    if distribution.reward.expires_at and datetime.utcnow() > distribution.reward.expires_at:
                        return False  # Expired
                    
                    distribution.claimed = True
                    distribution.claimed_at = datetime.utcnow()
                    
                    # Apply reward effect
                    await self._apply_reward(user_id, distribution.reward)
                    
                    logger.info(f"User {user_id} claimed reward {distribution.reward.reward_id}")
                    return True
            
            return False  # Distribution not found
            
        except Exception as e:
            logger.error(f"Reward claim failed: {e}")
            return False
    
    async def get_user_rewards(self, user_id: str, include_claimed: bool = True) -> List[RewardDistribution]:
        """Get all rewards for a user"""
        
        user_distributions = self.user_rewards.get(user_id, [])
        
        if not include_claimed:
            user_distributions = [d for d in user_distributions if not d.claimed]
        
        return user_distributions
    
    async def get_pending_rewards(self, user_id: str) -> List[RewardDistribution]:
        """Get unclaimed rewards for a user"""
        
        user_distributions = self.user_rewards.get(user_id, [])
        pending = []
        
        for distribution in user_distributions:
            if not distribution.claimed:
                # Check if not expired
                if not distribution.reward.expires_at or datetime.utcnow() <= distribution.reward.expires_at:
                    pending.append(distribution)
        
        return pending
    
    async def create_custom_reward(
        self,
        reward_id: str,
        name: str,
        description: str,
        reward_type: RewardType,
        value: Any,
        rarity: str = "common",
        expires_in_days: Optional[int] = None
    ) -> Reward:
        """Create a custom reward in the catalog"""
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        reward = Reward(
            reward_id=reward_id,
            name=name,
            description=description,
            reward_type=reward_type,
            value=value,
            rarity=rarity,
            expires_at=expires_at
        )
        
        self.reward_catalog[reward_id] = reward
        logger.info(f"Created custom reward: {reward_id}")
        
        return reward
    
    async def distribute_milestone_rewards(self, user_id: str, milestone: str, user_stats: Dict[str, Any]):
        """Distribute rewards based on milestone achievement"""
        
        milestone_rewards = {
            "first_post": ["points_100", "badge_first_post"],
            "10_posts": ["points_500", "badge_prolific"],
            "100_likes": ["points_300", "badge_popular"],
            "1000_followers": ["feature_analytics", "badge_influencer"],
            "premium_upgrade": ["discount_premium", "badge_premium"]
        }
        
        rewards_to_distribute = milestone_rewards.get(milestone, [])
        
        for reward_id in rewards_to_distribute:
            if reward_id in self.reward_catalog:
                await self.distribute_reward(user_id, reward_id, f"milestone_{milestone}")
        
        logger.info(f"Distributed {len(rewards_to_distribute)} milestone rewards for {milestone}")
    
    async def calculate_reward_value(self, user_id: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate appropriate reward value for an action using AI"""
        
        base_values = {
            "post_created": 50,
            "like_received": 5,
            "comment_received": 10,
            "share_received": 15,
            "follower_gained": 20,
            "challenge_completed": 100,
            "streak_maintained": 25
        }
        
        base_value = base_values.get(action, 10)
        
        # Apply multipliers based on context
        multiplier = 1.0
        
        # Quality multiplier
        if context.get("quality_score", 0) > 0.8:
            multiplier *= 1.5
        
        # Streak multiplier
        if context.get("streak_days", 0) > 7:
            multiplier *= 1.2
        
        # Engagement multiplier
        if context.get("engagement_rate", 0) > 0.1:
            multiplier *= 1.3
        
        final_value = int(base_value * multiplier)
        
        return {
            "points": final_value,
            "multiplier": multiplier,
            "base_value": base_value,
            "bonus_reasons": self._get_bonus_reasons(context)
        }
    
    async def _apply_reward(self, user_id: str, reward: Reward):
        """Apply the effect of a reward to the user"""
        
        if reward.reward_type == RewardType.POINTS:
            # Add points to user account
            logger.info(f"Added {reward.value} points to user {user_id}")
            
        elif reward.reward_type == RewardType.BADGE:
            # Add badge to user profile
            logger.info(f"Awarded badge '{reward.value}' to user {user_id}")
            
        elif reward.reward_type == RewardType.FEATURE_ACCESS:
            # Grant feature access
            logger.info(f"Granted access to '{reward.value}' for user {user_id}")
            
        elif reward.reward_type == RewardType.DISCOUNT:
            # Create discount coupon
            logger.info(f"Applied {reward.value * 100}% discount for user {user_id}")
            
        elif reward.reward_type == RewardType.RECOGNITION:
            # Add to recognition board
            logger.info(f"Added recognition '{reward.value}' for user {user_id}")
        
        # Record application metrics
        await self.metrics_collector.record_metric("rewards_applied", 1)
        await self.metrics_collector.record_metric(f"reward_applied_{reward.reward_type.value}", 1)
    
    def _get_bonus_reasons(self, context: Dict[str, Any]) -> List[str]:
        """Get list of bonus reasons for transparency"""
        
        reasons = []
        
        if context.get("quality_score", 0) > 0.8:
            reasons.append("High quality content (+50%)")
        
        if context.get("streak_days", 0) > 7:
            reasons.append("Streak bonus (+20%)")
        
        if context.get("engagement_rate", 0) > 0.1:
            reasons.append("High engagement (+30%)")
        
        return reasons
    
    async def get_reward_analytics(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Get analytics for reward distribution"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
        
        total_distributed = 0
        total_claimed = 0
        reward_type_counts = {}
        rarity_distribution = {}
        
        for user_distributions in self.user_rewards.values():
            for distribution in user_distributions:
                if distribution.distributed_at >= cutoff_date:
                    total_distributed += 1
                    
                    if distribution.claimed:
                        total_claimed += 1
                    
                    reward_type = distribution.reward.reward_type.value
                    reward_type_counts[reward_type] = reward_type_counts.get(reward_type, 0) + 1
                    
                    rarity = distribution.reward.rarity
                    rarity_distribution[rarity] = rarity_distribution.get(rarity, 0) + 1
        
        claim_rate = (total_claimed / total_distributed) * 100 if total_distributed > 0 else 0
        
        analytics = {
            "period_days": time_period_days,
            "total_distributed": total_distributed,
            "total_claimed": total_claimed,
            "claim_rate_percentage": round(claim_rate, 2),
            "reward_types": reward_type_counts,
            "rarity_distribution": rarity_distribution,
            "most_popular_reward": max(reward_type_counts.items(), key=lambda x: x[1])[0] if reward_type_counts else None
        }
        
        return analytics