"""Mobile Reward System

Advanced mobile reward distribution system for creator incentives with
points, badges, unlocks, special features, and mobile-optimized reward
delivery and notification mechanisms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import uuid
import time


logger = logging.getLogger(__name__)


class RewardCategory(Enum):
    """Reward categories"""
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    DAILY_BONUS = "daily_bonus"
    COLLABORATION = "collaboration"
    QUALITY_BONUS = "quality_bonus"
    MOBILE_BONUS = "mobile_bonus"
    SPECIAL_EVENT = "special_event"


class RewardStatus(Enum):
    """Reward status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    CLAIMED = "claimed"
    EXPIRED = "expired"


@dataclass
class Reward:
    """Individual reward definition"""
    reward_id: str
    title: str
    description: str
    category: RewardCategory
    points_value: int
    badge_icon: Optional[str] = None
    unlock_feature: Optional[str] = None
    expiry_date: Optional[datetime] = None
    mobile_exclusive: bool = False
    
    def __post_init__(self):
        if not self.reward_id:
            self.reward_id = str(uuid.uuid4())


@dataclass
class MobileRewardConfiguration:
    """Mobile reward system configuration"""
    enable_instant_delivery: bool = True
    enable_notifications: bool = True
    enable_animations: bool = True
    auto_claim_rewards: bool = False
    mobile_exclusive_bonuses: bool = True
    social_sharing: bool = True
    reward_stacking: bool = True


@dataclass
class MobileRewardRequest:
    """Mobile reward system request"""
    request_id: str
    user_id: str
    reward_trigger: str
    trigger_data: Dict[str, Any]
    mobile_config: MobileRewardConfiguration
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


@dataclass
class RewardDelivery:
    """Reward delivery information"""
    delivery_id: str
    reward: Reward
    delivered_at: datetime
    claimed_at: Optional[datetime] = None
    status: RewardStatus = RewardStatus.DELIVERED
    mobile_notification_sent: bool = False
    
    def __post_init__(self):
        if not self.delivery_id:
            self.delivery_id = str(uuid.uuid4())


@dataclass
class MobileRewardResult:
    """Mobile reward system result"""
    request_id: str
    success: bool
    processing_time_ms: int
    rewards_delivered: List[RewardDelivery]
    total_points_earned: int
    new_unlocks: List[str]
    mobile_notifications: List[Dict[str, Any]]
    reward_summary: Dict[str, Any]
    mobile_optimizations: List[str]
    analytics_data: Dict[str, Any]
    error_message: Optional[str] = None


class MobileRewardSystem:
    """Mobile Reward System
    
    Advanced mobile reward distribution system for creator incentives
    with mobile-optimized reward delivery and notifications.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Reward system data
        self.user_rewards = {}
        self.reward_catalog = self._initialize_reward_catalog()
        self.delivery_history = {}
        
        # Performance tracking
        self.reward_metrics = {
            "total_rewards_delivered": 0,
            "total_points_distributed": 0,
            "mobile_exclusive_rewards": 0,
            "active_reward_users": 0
        }
        
        self.logger.info("Mobile Reward System initialized")
    
    def _initialize_reward_catalog(self) -> Dict[str, Reward]:
        """Initialize the reward catalog."""
        return {
            "first_upload_reward": Reward(
                reward_id="first_upload_001",
                title="Welcome Creator!",
                description="Welcome bonus for your first upload",
                category=RewardCategory.ACHIEVEMENT,
                points_value=100,
                badge_icon="🎉",
                mobile_exclusive=True
            ),
            "mobile_master_reward": Reward(
                reward_id="mobile_master_001",
                title="Mobile Master",
                description="Reward for mastering mobile features",
                category=RewardCategory.MOBILE_BONUS,
                points_value=500,
                badge_icon="📱",
                unlock_feature="advanced_mobile_tools",
                mobile_exclusive=True
            ),
            "collaboration_reward": Reward(
                reward_id="collaboration_001",
                title="Team Player",
                description="Bonus for successful collaboration",
                category=RewardCategory.COLLABORATION,
                points_value=200,
                badge_icon="🤝"
            ),
            "quality_excellence": Reward(
                reward_id="quality_001",
                title="Quality Excellence",
                description="Reward for high-quality content",
                category=RewardCategory.QUALITY_BONUS,
                points_value=300,
                badge_icon="⭐",
                unlock_feature="quality_analytics"
            ),
            "daily_login_bonus": Reward(
                reward_id="daily_001",
                title="Daily Creator",
                description="Daily login bonus",
                category=RewardCategory.DAILY_BONUS,
                points_value=25,
                badge_icon="📅",
                expiry_date=datetime.utcnow() + timedelta(days=1)
            ),
            "milestone_100_uploads": Reward(
                reward_id="milestone_100",
                title="Century Creator",
                description="100 uploads milestone reward",
                category=RewardCategory.MILESTONE,
                points_value=1000,
                badge_icon="💯",
                unlock_feature="premium_features"
            ),
            "mobile_engagement_boost": Reward(
                reward_id="mobile_engagement_001",
                title="Mobile Engagement Boost",
                description="Extra points for mobile engagement",
                category=RewardCategory.MOBILE_BONUS,
                points_value=150,
                badge_icon="🚀",
                mobile_exclusive=True
            )
        }
    
    async def distribute_rewards(self, request: MobileRewardRequest) -> MobileRewardResult:
        """Distribute rewards based on trigger."""
        start_time = time.time()
        
        self.logger.info(f"Processing rewards for user {request.user_id}")
        
        try:
            result = MobileRewardResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=0,
                rewards_delivered=[],
                total_points_earned=0,
                new_unlocks=[],
                mobile_notifications=[],
                reward_summary={},
                mobile_optimizations=[],
                analytics_data={}
            )
            
            # Core reward distribution pipeline
            await self._determine_eligible_rewards(request, result)
            await self._deliver_rewards(request, result)
            await self._apply_mobile_bonuses(request, result)
            await self._handle_unlocks(request, result)
            await self._generate_notifications(request, result)
            await self._update_reward_summary(request, result)
            await self._apply_mobile_optimizations(request, result)
            await self._generate_reward_analytics(request, result)
            
            result.success = True
            
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = int(processing_time)
            
            self.logger.info(f"Reward distribution completed in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            self.logger.error(f"Reward distribution failed: {str(e)}")
            return MobileRewardResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=int((time.time() - start_time) * 1000),
                rewards_delivered=[],
                total_points_earned=0,
                new_unlocks=[],
                mobile_notifications=[],
                reward_summary={},
                mobile_optimizations=[],
                analytics_data={},
                error_message=str(e)
            )
    
    async def _determine_eligible_rewards(self, request: MobileRewardRequest, result: MobileRewardResult):
        """Determine which rewards are eligible for the trigger."""
        eligible_rewards = []
        trigger = request.reward_trigger
        trigger_data = request.trigger_data
        
        # Map triggers to rewards
        trigger_reward_mapping = {
            "first_upload": ["first_upload_reward"],
            "mobile_action_completed": ["mobile_master_reward", "mobile_engagement_boost"],
            "collaboration_completed": ["collaboration_reward"],
            "high_quality_content": ["quality_excellence"],
            "daily_login": ["daily_login_bonus"],
            "milestone_reached": ["milestone_100_uploads"],
            "achievement_unlocked": ["mobile_master_reward"]
        }
        
        eligible_reward_ids = trigger_reward_mapping.get(trigger, [])
        
        for reward_id in eligible_reward_ids:
            if reward_id in self.reward_catalog:
                reward = self.reward_catalog[reward_id]
                
                # Check additional eligibility criteria
                if await self._check_reward_eligibility(reward, request):
                    eligible_rewards.append(reward)
        
        # Store eligible rewards for delivery
        result.rewards_delivered = [
            RewardDelivery(
                delivery_id=str(uuid.uuid4()),
                reward=reward,
                delivered_at=datetime.utcnow(),
                status=RewardStatus.DELIVERED
            )
            for reward in eligible_rewards
        ]
    
    async def _check_reward_eligibility(self, reward: Reward, request: MobileRewardRequest) -> bool:
        """Check if user is eligible for specific reward."""
        user_id = request.user_id
        
        # Check if reward already claimed recently
        if user_id in self.delivery_history:
            user_history = self.delivery_history[user_id]
            
            # Daily rewards can only be claimed once per day
            if reward.category == RewardCategory.DAILY_BONUS:
                today = datetime.utcnow().date()
                for delivery in user_history:
                    if (delivery.reward.category == RewardCategory.DAILY_BONUS and 
                        delivery.delivered_at.date() == today):
                        return False
            
            # Achievement rewards are one-time only
            if reward.category == RewardCategory.ACHIEVEMENT:
                for delivery in user_history:
                    if delivery.reward.reward_id == reward.reward_id:
                        return False
        
        # Check expiry
        if reward.expiry_date and datetime.utcnow() > reward.expiry_date:
            return False
        
        # Check mobile exclusivity
        if reward.mobile_exclusive and not request.trigger_data.get("mobile_action", False):
            return False
        
        return True
    
    async def _deliver_rewards(self, request: MobileRewardRequest, result: MobileRewardResult):
        """Deliver rewards to user."""
        user_id = request.user_id
        total_points = 0
        
        for delivery in result.rewards_delivered:
            # Update user reward balance
            if user_id not in self.user_rewards:
                self.user_rewards[user_id] = {
                    "total_points": 0,
                    "badges": [],
                    "unlocked_features": [],
                    "reward_history": []
                }
            
            user_data = self.user_rewards[user_id]
            reward = delivery.reward
            
            # Add points
            user_data["total_points"] += reward.points_value
            total_points += reward.points_value
            
            # Add badge if applicable
            if reward.badge_icon and reward.badge_icon not in user_data["badges"]:
                user_data["badges"].append(reward.badge_icon)
            
            # Track delivery history
            if user_id not in self.delivery_history:
                self.delivery_history[user_id] = []
            
            self.delivery_history[user_id].append(delivery)
            user_data["reward_history"].append(delivery.delivery_id)
            
            # Update metrics
            self.reward_metrics["total_rewards_delivered"] += 1
            self.reward_metrics["total_points_distributed"] += reward.points_value
            
            if reward.mobile_exclusive:
                self.reward_metrics["mobile_exclusive_rewards"] += 1
        
        result.total_points_earned = total_points
        
        # Mark user as active
        if user_id not in self.user_rewards or total_points > 0:
            self.reward_metrics["active_reward_users"] = len(self.user_rewards)
    
    async def _apply_mobile_bonuses(self, request: MobileRewardRequest, result: MobileRewardResult):
        """Apply mobile-specific bonuses."""
        if not request.mobile_config.mobile_exclusive_bonuses:
            return
        
        trigger_data = request.trigger_data
        mobile_bonus_applied = False
        
        # Check for mobile action bonus
        if trigger_data.get("mobile_action", False):
            bonus_points = int(result.total_points_earned * 0.2)  # 20% mobile bonus
            
            if bonus_points > 0:
                mobile_bonus_reward = Reward(
                    reward_id=f"mobile_bonus_{request.request_id}",
                    title="Mobile Action Bonus",
                    description="20% bonus for mobile action",
                    category=RewardCategory.MOBILE_BONUS,
                    points_value=bonus_points,
                    badge_icon="📱",
                    mobile_exclusive=True
                )
                
                bonus_delivery = RewardDelivery(
                    delivery_id=str(uuid.uuid4()),
                    reward=mobile_bonus_reward,
                    delivered_at=datetime.utcnow(),
                    status=RewardStatus.DELIVERED
                )
                
                result.rewards_delivered.append(bonus_delivery)
                result.total_points_earned += bonus_points
                mobile_bonus_applied = True
        
        # Apply to user balance
        if mobile_bonus_applied:
            user_data = self.user_rewards[request.user_id]
            user_data["total_points"] += bonus_points
    
    async def _handle_unlocks(self, request: MobileRewardRequest, result: MobileRewardResult):
        """Handle feature unlocks from rewards."""
        new_unlocks = []
        user_data = self.user_rewards[request.user_id]
        
        for delivery in result.rewards_delivered:
            reward = delivery.reward
            
            if reward.unlock_feature and reward.unlock_feature not in user_data["unlocked_features"]:
                user_data["unlocked_features"].append(reward.unlock_feature)
                new_unlocks.append(reward.unlock_feature)
        
        result.new_unlocks = new_unlocks
    
    async def _generate_notifications(self, request: MobileRewardRequest, result: MobileRewardResult):
        """Generate mobile notifications for rewards."""
        if not request.mobile_config.enable_notifications:
            return
        
        notifications = []
        
        for delivery in result.rewards_delivered:
            reward = delivery.reward
            
            notification = {
                "notification_id": str(uuid.uuid4()),
                "type": "reward_received",
                "title": f"🎉 {reward.title}",
                "message": f"You earned {reward.points_value} points! {reward.description}",
                "badge_icon": reward.badge_icon,
                "points_earned": reward.points_value,
                "mobile_optimized": True,
                "priority": "high" if reward.category == RewardCategory.ACHIEVEMENT else "medium",
                "action_buttons": ["Claim", "Share"] if not request.mobile_config.auto_claim_rewards else ["Share"],
                "created_at": datetime.utcnow().isoformat()
            }
            
            notifications.append(notification)
            delivery.mobile_notification_sent = True
        
        # Summary notification for multiple rewards
        if len(result.rewards_delivered) > 1:
            summary_notification = {
                "notification_id": str(uuid.uuid4()),
                "type": "reward_summary",
                "title": f"🏆 {len(result.rewards_delivered)} Rewards Earned!",
                "message": f"Total: {result.total_points_earned} points earned",
                "mobile_optimized": True,
                "priority": "high",
                "action_buttons": ["View All", "Share"],
                "created_at": datetime.utcnow().isoformat()
            }
            
            notifications.append(summary_notification)
        
        result.mobile_notifications = notifications
    
    async def _update_reward_summary(self, request: MobileRewardRequest, result: MobileRewardResult):
        """Update reward summary for user."""
        user_data = self.user_rewards[request.user_id]
        
        summary = {
            "total_lifetime_points": user_data["total_points"],
            "rewards_received_today": len(result.rewards_delivered),
            "points_earned_today": result.total_points_earned,
            "total_badges": len(user_data["badges"]),
            "unlocked_features": len(user_data["unlocked_features"]),
            "new_unlocks_today": len(result.new_unlocks),
            "mobile_exclusive_rewards": sum(1 for d in result.rewards_delivered if d.reward.mobile_exclusive),
            "next_milestone": self._calculate_next_milestone(user_data["total_points"])
        }
        
        result.reward_summary = summary
    
    def _calculate_next_milestone(self, current_points: int) -> Dict[str, Any]:
        """Calculate next point milestone."""
        milestones = [100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
        
        for milestone in milestones:
            if current_points < milestone:
                return {
                    "target_points": milestone,
                    "points_needed": milestone - current_points,
                    "progress_percentage": (current_points / milestone) * 100
                }
        
        return {
            "target_points": current_points + 50000,
            "points_needed": 50000,
            "progress_percentage": 0
        }
    
    async def _apply_mobile_optimizations(self, request: MobileRewardRequest, result: MobileRewardResult):
        """Apply mobile-specific optimizations."""
        mobile_optimizations = [
            "instant_reward_notifications",
            "haptic_feedback_on_reward",
            "animated_point_counters",
            "swipe_to_claim_rewards",
            "mobile_badge_gallery",
            "touch_friendly_reward_ui",
            "mobile_sharing_integration",
            "offline_reward_queue",
            "battery_efficient_animations",
            "adaptive_notification_timing"
        ]
        
        if request.mobile_config.enable_animations:
            mobile_optimizations.extend([
                "reward_celebration_animations",
                "point_earning_effects",
                "badge_unlock_animations"
            ])
        
        result.mobile_optimizations = mobile_optimizations
    
    async def _generate_reward_analytics(self, request: MobileRewardRequest, result: MobileRewardResult):
        """Generate analytics data for reward distribution."""
        analytics = {
            "reward_distribution_id": result.request_id,
            "user_id": request.user_id,
            "trigger": request.reward_trigger,
            "rewards_delivered_count": len(result.rewards_delivered),
            "total_points_earned": result.total_points_earned,
            "new_unlocks_count": len(result.new_unlocks),
            "mobile_notifications_count": len(result.mobile_notifications),
            "mobile_exclusive_rewards": sum(1 for d in result.rewards_delivered if d.reward.mobile_exclusive),
            "reward_categories": list(set(d.reward.category.value for d in result.rewards_delivered)),
            "mobile_optimizations_count": len(result.mobile_optimizations),
            "user_summary": result.reward_summary,
            "processing_time_ms": result.processing_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result.analytics_data = analytics


# Export key classes and functions
__all__ = [
    "MobileRewardSystem",
    "MobileRewardRequest", 
    "MobileRewardResult",
    "Reward",
    "RewardDelivery",
    "MobileRewardConfiguration",
    "RewardCategory",
    "RewardStatus"
]