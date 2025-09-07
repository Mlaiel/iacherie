"""Milestone Reward Calculator - Enterprise Milestone-Based Monetization
=====================================================================

Enterprise-grade milestone reward calculator providing automated reward
calculations for creator milestones, performance benchmarks, and achievement
thresholds with progressive scaling and comprehensive tracking.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/milestone_reward_calculator.py
Business Logic: Milestone Tracking → Reward Calculation → Payout Processing → Analytics

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


class MilestoneCategory(str, Enum):
    """Categories of milestones for reward classification."""
    CONTENT_VOLUME = "content_volume"
    AUDIENCE_GROWTH = "audience_growth"
    REVENUE_TARGETS = "revenue_targets"
    ENGAGEMENT_METRICS = "engagement_metrics"
    COLLABORATION_MILESTONES = "collaboration_milestones"
    QUALITY_BENCHMARKS = "quality_benchmarks"
    CONSISTENCY_STREAKS = "consistency_streaks"
    PLATFORM_LOYALTY = "platform_loyalty"
    INNOVATION_MARKERS = "innovation_markers"
    COMMUNITY_IMPACT = "community_impact"


class MilestoneType(str, Enum):
    """Types of milestone measurement."""
    CUMULATIVE = "cumulative"  # Total accumulated value
    PERIODIC = "periodic"  # Value within time period
    STREAK = "streak"  # Consecutive achievements
    THRESHOLD = "threshold"  # One-time threshold crossing
    PROGRESSION = "progression"  # Progressive improvement
    COMPARATIVE = "comparative"  # Relative to peers


class RewardCalculationMethod(str, Enum):
    """Methods for calculating milestone rewards."""
    FIXED_AMOUNT = "fixed_amount"
    PROGRESSIVE_SCALE = "progressive_scale"
    PERCENTAGE_BASED = "percentage_based"
    TIER_MULTIPLIER = "tier_multiplier"
    ACHIEVEMENT_STACK = "achievement_stack"
    TIME_WEIGHTED = "time_weighted"
    DIFFICULTY_SCALED = "difficulty_scaled"


class MilestoneStatus(str, Enum):
    """Status of milestone progress."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    REWARDED = "rewarded"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


@dataclass
class MilestoneDefinition:
    """Definition of a milestone with reward parameters."""
    milestone_id: str
    name: str
    description: str
    category: MilestoneCategory
    milestone_type: MilestoneType
    target_value: Union[int, float, Decimal]
    measurement_key: str
    reward_calculation_method: RewardCalculationMethod
    base_reward_amount: Decimal
    progression_multiplier: float = 1.0
    max_reward_amount: Optional[Decimal] = None
    time_limit: Optional[timedelta] = None
    prerequisite_milestones: List[str] = field(default_factory=list)
    repeatable: bool = False
    difficulty_level: int = 1
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreatorMilestone:
    """Creator's milestone progress and achievement."""
    milestone_instance_id: str
    creator_id: str
    milestone_id: str
    status: MilestoneStatus
    current_value: Union[int, float, Decimal]
    target_value: Union[int, float, Decimal]
    progress_percentage: float
    started_at: datetime
    achieved_at: Optional[datetime] = None
    rewarded_at: Optional[datetime] = None
    calculated_reward: Optional[Decimal] = None
    streak_count: int = 0
    bonus_multiplier: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MilestoneReward:
    """Milestone reward calculation and distribution."""
    reward_id: str
    milestone_instance_id: str
    creator_id: str
    milestone_id: str
    base_amount: Decimal
    bonus_amount: Decimal
    total_amount: Decimal
    calculation_method: str
    calculation_details: Dict[str, Any]
    currency: str = "USD"
    status: str = "pending"
    processed_at: Optional[datetime] = None
    transaction_id: Optional[str] = None


class MilestoneRewardCalculator:
    """
    Enterprise milestone reward calculator providing automated reward
    calculations for creator milestones with comprehensive tracking.
    """
    
    def __init__(self):
        """Initialize the milestone reward calculator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core storage
        self.milestone_definitions: Dict[str, MilestoneDefinition] = {}
        self.creator_milestones: Dict[str, List[CreatorMilestone]] = {}
        self.milestone_rewards: Dict[str, List[MilestoneReward]] = {}
        
        # Configuration
        self.default_currency = "USD"
        self.max_reward_per_milestone = Decimal("10000.00")
        self.streak_bonus_multiplier = 0.1  # 10% bonus per streak
        self.time_bonus_decay_rate = 0.05  # 5% bonus decay per day delay
        
        # Analytics
        self.total_rewards_calculated = Decimal("0")
        self.milestones_achieved_count = 0
        self.average_achievement_time = timedelta(0)
        
        self.initialized = False
        self.logger.info("MilestoneRewardCalculator initialized")
    
    async def initialize(self) -> bool:
        """Initialize the milestone reward calculator."""
        try:
            await self._load_milestone_definitions()
            await self._load_creator_milestones()
            await self._calculate_analytics()
            
            self.initialized = True
            self.logger.info("MilestoneRewardCalculator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MilestoneRewardCalculator: {e}")
            return False
    
    async def _load_milestone_definitions(self):
        """Load milestone definitions from storage."""
        # Initialize default milestone definitions
        default_milestones = [
            # Content Volume Milestones
            MilestoneDefinition(
                milestone_id="first_content_upload",
                name="First Content Upload",
                description="Upload your first piece of content",
                category=MilestoneCategory.CONTENT_VOLUME,
                milestone_type=MilestoneType.THRESHOLD,
                target_value=1,
                measurement_key="content_count",
                reward_calculation_method=RewardCalculationMethod.FIXED_AMOUNT,
                base_reward_amount=Decimal("10.00")
            ),
            MilestoneDefinition(
                milestone_id="content_milestone_10",
                name="10 Content Pieces",
                description="Upload 10 pieces of content",
                category=MilestoneCategory.CONTENT_VOLUME,
                milestone_type=MilestoneType.CUMULATIVE,
                target_value=10,
                measurement_key="content_count",
                reward_calculation_method=RewardCalculationMethod.PROGRESSIVE_SCALE,
                base_reward_amount=Decimal("50.00"),
                progression_multiplier=1.2
            ),
            MilestoneDefinition(
                milestone_id="content_milestone_100",
                name="100 Content Pieces",
                description="Upload 100 pieces of content",
                category=MilestoneCategory.CONTENT_VOLUME,
                milestone_type=MilestoneType.CUMULATIVE,
                target_value=100,
                measurement_key="content_count",
                reward_calculation_method=RewardCalculationMethod.PROGRESSIVE_SCALE,
                base_reward_amount=Decimal("250.00"),
                progression_multiplier=1.5,
                difficulty_level=3
            ),
            
            # Audience Growth Milestones
            MilestoneDefinition(
                milestone_id="follower_milestone_100",
                name="100 Followers",
                description="Reach 100 followers",
                category=MilestoneCategory.AUDIENCE_GROWTH,
                milestone_type=MilestoneType.THRESHOLD,
                target_value=100,
                measurement_key="follower_count",
                reward_calculation_method=RewardCalculationMethod.FIXED_AMOUNT,
                base_reward_amount=Decimal("25.00")
            ),
            MilestoneDefinition(
                milestone_id="follower_milestone_1k",
                name="1K Followers",
                description="Reach 1,000 followers",
                category=MilestoneCategory.AUDIENCE_GROWTH,
                milestone_type=MilestoneType.THRESHOLD,
                target_value=1000,
                measurement_key="follower_count",
                reward_calculation_method=RewardCalculationMethod.PROGRESSIVE_SCALE,
                base_reward_amount=Decimal("100.00"),
                progression_multiplier=1.3,
                difficulty_level=2
            ),
            MilestoneDefinition(
                milestone_id="follower_milestone_10k",
                name="10K Followers",
                description="Reach 10,000 followers",
                category=MilestoneCategory.AUDIENCE_GROWTH,
                milestone_type=MilestoneType.THRESHOLD,
                target_value=10000,
                measurement_key="follower_count",
                reward_calculation_method=RewardCalculationMethod.PROGRESSIVE_SCALE,
                base_reward_amount=Decimal("500.00"),
                progression_multiplier=1.5,
                difficulty_level=4
            ),
            
            # Revenue Milestones
            MilestoneDefinition(
                milestone_id="revenue_milestone_100",
                name="First $100 Revenue",
                description="Generate your first $100 in revenue",
                category=MilestoneCategory.REVENUE_TARGETS,
                milestone_type=MilestoneType.THRESHOLD,
                target_value=100,
                measurement_key="total_revenue",
                reward_calculation_method=RewardCalculationMethod.PERCENTAGE_BASED,
                base_reward_amount=Decimal("5.00")  # 5% bonus
            ),
            MilestoneDefinition(
                milestone_id="revenue_milestone_1k",
                name="$1K Revenue",
                description="Generate $1,000 in total revenue",
                category=MilestoneCategory.REVENUE_TARGETS,
                milestone_type=MilestoneType.CUMULATIVE,
                target_value=1000,
                measurement_key="total_revenue",
                reward_calculation_method=RewardCalculationMethod.PERCENTAGE_BASED,
                base_reward_amount=Decimal("25.00")  # $25 bonus
            ),
            
            # Engagement Milestones
            MilestoneDefinition(
                milestone_id="engagement_milestone_1k",
                name="1K Total Engagements",
                description="Reach 1,000 total engagements",
                category=MilestoneCategory.ENGAGEMENT_METRICS,
                milestone_type=MilestoneType.CUMULATIVE,
                target_value=1000,
                measurement_key="total_engagements",
                reward_calculation_method=RewardCalculationMethod.PROGRESSIVE_SCALE,
                base_reward_amount=Decimal("30.00"),
                progression_multiplier=1.2
            ),
            
            # Consistency Streaks
            MilestoneDefinition(
                milestone_id="daily_streak_7",
                name="7-Day Upload Streak",
                description="Upload content for 7 consecutive days",
                category=MilestoneCategory.CONSISTENCY_STREAKS,
                milestone_type=MilestoneType.STREAK,
                target_value=7,
                measurement_key="upload_streak",
                reward_calculation_method=RewardCalculationMethod.TIER_MULTIPLIER,
                base_reward_amount=Decimal("20.00"),
                repeatable=True
            ),
            MilestoneDefinition(
                milestone_id="daily_streak_30",
                name="30-Day Upload Streak",
                description="Upload content for 30 consecutive days",
                category=MilestoneCategory.CONSISTENCY_STREAKS,
                milestone_type=MilestoneType.STREAK,
                target_value=30,
                measurement_key="upload_streak",
                reward_calculation_method=RewardCalculationMethod.TIER_MULTIPLIER,
                base_reward_amount=Decimal("100.00"),
                progression_multiplier=1.5,
                repeatable=True
            )
        ]
        
        for milestone in default_milestones:
            self.milestone_definitions[milestone.milestone_id] = milestone
        
        self.logger.info(f"Loaded {len(self.milestone_definitions)} milestone definitions")
    
    async def _load_creator_milestones(self):
        """Load creator milestone progress from storage."""
        # In production, this would load from database
        self.logger.info("Loading creator milestone progress...")
    
    async def _calculate_analytics(self):
        """Calculate system analytics."""
        self.logger.info("Calculating milestone analytics...")
    
    async def check_creator_milestones(
        self,
        creator_id: str,
        metric_updates: Dict[str, Union[int, float, Decimal]]
    ) -> List[CreatorMilestone]:
        """
        Check creator's progress against all milestones and detect achievements.
        
        Args:
            creator_id: Creator identifier
            metric_updates: Updated metrics to check against milestones
            
        Returns:
            List of newly achieved milestones
        """
        try:
            newly_achieved = []
            
            # Initialize creator milestones if not exists
            if creator_id not in self.creator_milestones:
                self.creator_milestones[creator_id] = []
                await self._initialize_creator_milestones(creator_id)
            
            creator_milestones = self.creator_milestones[creator_id]
            
            # Check each milestone
            for milestone in creator_milestones:
                if milestone.status in [MilestoneStatus.ACHIEVED, MilestoneStatus.REWARDED]:
                    continue
                
                milestone_def = self.milestone_definitions.get(milestone.milestone_id)
                if not milestone_def or not milestone_def.enabled:
                    continue
                
                # Update milestone progress
                await self._update_milestone_progress(milestone, metric_updates, milestone_def)
                
                # Check if milestone is achieved
                if await self._is_milestone_achieved(milestone, milestone_def):
                    milestone.status = MilestoneStatus.ACHIEVED
                    milestone.achieved_at = datetime.utcnow()
                    
                    # Calculate reward
                    reward_amount = await self._calculate_milestone_reward(milestone, milestone_def)
                    milestone.calculated_reward = reward_amount
                    
                    newly_achieved.append(milestone)
                    self.milestones_achieved_count += 1
            
            self.logger.info(f"Creator {creator_id} achieved {len(newly_achieved)} new milestones")
            return newly_achieved
            
        except Exception as e:
            self.logger.error(f"Error checking creator milestones: {e}")
            return []
    
    async def _initialize_creator_milestones(self, creator_id: str):
        """Initialize milestone tracking for new creator."""
        for milestone_def in self.milestone_definitions.values():
            if not milestone_def.enabled:
                continue
            
            milestone = CreatorMilestone(
                milestone_instance_id=str(uuid4()),
                creator_id=creator_id,
                milestone_id=milestone_def.milestone_id,
                status=MilestoneStatus.NOT_STARTED,
                current_value=0,
                target_value=milestone_def.target_value,
                progress_percentage=0.0,
                started_at=datetime.utcnow()
            )
            
            self.creator_milestones[creator_id].append(milestone)
        
        self.logger.info(f"Initialized {len(self.milestone_definitions)} milestones for creator {creator_id}")
    
    async def _update_milestone_progress(
        self,
        milestone: CreatorMilestone,
        metric_updates: Dict[str, Any],
        milestone_def: MilestoneDefinition
    ):
        """Update milestone progress based on metric updates."""
        
        measurement_key = milestone_def.measurement_key
        
        if measurement_key not in metric_updates:
            return
        
        new_value = metric_updates[measurement_key]
        
        # Update current value based on milestone type
        if milestone_def.milestone_type == MilestoneType.CUMULATIVE:
            milestone.current_value = new_value
        elif milestone_def.milestone_type == MilestoneType.THRESHOLD:
            milestone.current_value = new_value
        elif milestone_def.milestone_type == MilestoneType.STREAK:
            # For streaks, the value represents consecutive count
            milestone.current_value = new_value
            milestone.streak_count = int(new_value)
        elif milestone_def.milestone_type == MilestoneType.PERIODIC:
            # For periodic, we need time-based calculation
            milestone.current_value = new_value
        
        # Calculate progress percentage
        target = float(milestone.target_value)
        current = float(milestone.current_value)
        milestone.progress_percentage = min((current / target) * 100, 100.0)
        
        # Update status
        if milestone.status == MilestoneStatus.NOT_STARTED and current > 0:
            milestone.status = MilestoneStatus.IN_PROGRESS
    
    async def _is_milestone_achieved(
        self, milestone: CreatorMilestone, milestone_def: MilestoneDefinition
    ) -> bool:
        """Check if milestone has been achieved."""
        
        # Check prerequisite milestones
        if milestone_def.prerequisite_milestones:
            if not await self._check_prerequisites(milestone.creator_id, milestone_def.prerequisite_milestones):
                return False
        
        # Check time limit
        if milestone_def.time_limit:
            time_elapsed = datetime.utcnow() - milestone.started_at
            if time_elapsed > milestone_def.time_limit:
                milestone.status = MilestoneStatus.EXPIRED
                return False
        
        # Check if target is reached
        current = float(milestone.current_value)
        target = float(milestone.target_value)
        
        return current >= target
    
    async def _check_prerequisites(self, creator_id: str, prerequisite_ids: List[str]) -> bool:
        """Check if all prerequisite milestones are achieved."""
        creator_milestones = self.creator_milestones.get(creator_id, [])
        
        for prereq_id in prerequisite_ids:
            prereq_achieved = any(
                m.milestone_id == prereq_id and m.status == MilestoneStatus.ACHIEVED
                for m in creator_milestones
            )
            if not prereq_achieved:
                return False
        
        return True
    
    async def _calculate_milestone_reward(
        self, milestone: CreatorMilestone, milestone_def: MilestoneDefinition
    ) -> Decimal:
        """Calculate reward amount for achieved milestone."""
        
        base_amount = milestone_def.base_reward_amount
        
        if milestone_def.reward_calculation_method == RewardCalculationMethod.FIXED_AMOUNT:
            reward = base_amount
        
        elif milestone_def.reward_calculation_method == RewardCalculationMethod.PROGRESSIVE_SCALE:
            # Apply progression multiplier based on difficulty
            multiplier = milestone_def.progression_multiplier ** milestone_def.difficulty_level
            reward = base_amount * Decimal(str(multiplier))
        
        elif milestone_def.reward_calculation_method == RewardCalculationMethod.PERCENTAGE_BASED:
            # Base amount is percentage, apply to relevant metric
            percentage = float(base_amount)
            if milestone_def.measurement_key == "total_revenue":
                base_value = Decimal(str(milestone.current_value))
                reward = base_value * (Decimal(str(percentage)) / Decimal("100"))
            else:
                reward = base_amount
        
        elif milestone_def.reward_calculation_method == RewardCalculationMethod.TIER_MULTIPLIER:
            # Apply tier multiplier based on creator's progression
            tier_multiplier = await self._get_creator_tier_multiplier(milestone.creator_id)
            reward = base_amount * Decimal(str(tier_multiplier))
        
        elif milestone_def.reward_calculation_method == RewardCalculationMethod.TIME_WEIGHTED:
            # Apply time bonus for quick achievement
            time_elapsed = (milestone.achieved_at or datetime.utcnow()) - milestone.started_at
            expected_time = milestone_def.time_limit or timedelta(days=30)
            
            if time_elapsed < expected_time:
                time_bonus = 1.0 + ((expected_time - time_elapsed).total_seconds() / expected_time.total_seconds()) * 0.5
                reward = base_amount * Decimal(str(time_bonus))
            else:
                reward = base_amount
        
        elif milestone_def.reward_calculation_method == RewardCalculationMethod.DIFFICULTY_SCALED:
            # Scale by difficulty level
            difficulty_multiplier = 1.0 + (milestone_def.difficulty_level - 1) * 0.3
            reward = base_amount * Decimal(str(difficulty_multiplier))
        
        else:
            reward = base_amount
        
        # Apply streak bonus if applicable
        if milestone.streak_count > 1:
            streak_bonus = 1.0 + (milestone.streak_count - 1) * self.streak_bonus_multiplier
            reward = reward * Decimal(str(streak_bonus))
        
        # Apply bonus multiplier
        reward = reward * Decimal(str(milestone.bonus_multiplier))
        
        # Apply maximum cap
        max_reward = milestone_def.max_reward_amount or self.max_reward_per_milestone
        reward = min(reward, max_reward)
        
        return reward.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _get_creator_tier_multiplier(self, creator_id: str) -> float:
        """Get creator's tier multiplier for rewards."""
        # This would integrate with the loyalty system
        # For now, return a base multiplier
        creator_milestones = self.creator_milestones.get(creator_id, [])
        achieved_count = len([m for m in creator_milestones if m.status == MilestoneStatus.ACHIEVED])
        
        # Progressive tier multiplier based on achievements
        if achieved_count >= 20:
            return 2.0
        elif achieved_count >= 10:
            return 1.5
        elif achieved_count >= 5:
            return 1.2
        else:
            return 1.0
    
    async def process_milestone_rewards(
        self, creator_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process and distribute milestone rewards."""
        try:
            processed_rewards = []
            total_amount = Decimal("0")
            
            # Get creators to process
            creators_to_process = [creator_id] if creator_id else list(self.creator_milestones.keys())
            
            for creator in creators_to_process:
                creator_milestones = self.creator_milestones.get(creator, [])
                
                # Find achieved but not rewarded milestones
                pending_rewards = [
                    m for m in creator_milestones 
                    if m.status == MilestoneStatus.ACHIEVED and m.calculated_reward is not None
                ]
                
                for milestone in pending_rewards:
                    reward = await self._create_milestone_reward(milestone)
                    
                    # Process the reward
                    if await self._process_reward_payout(reward):
                        milestone.status = MilestoneStatus.REWARDED
                        milestone.rewarded_at = datetime.utcnow()
                        
                        processed_rewards.append(reward)
                        total_amount += reward.total_amount
                        
                        # Store reward
                        if creator not in self.milestone_rewards:
                            self.milestone_rewards[creator] = []
                        self.milestone_rewards[creator].append(reward)
            
            # Update analytics
            self.total_rewards_calculated += total_amount
            
            result = {
                "processed_count": len(processed_rewards),
                "total_amount": float(total_amount),
                "currency": self.default_currency,
                "rewards": [
                    {
                        "reward_id": r.reward_id,
                        "creator_id": r.creator_id,
                        "milestone_id": r.milestone_id,
                        "amount": float(r.total_amount)
                    }
                    for r in processed_rewards
                ]
            }
            
            self.logger.info(f"Processed {len(processed_rewards)} milestone rewards totaling ${total_amount}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing milestone rewards: {e}")
            return {"error": str(e)}
    
    async def _create_milestone_reward(self, milestone: CreatorMilestone) -> MilestoneReward:
        """Create milestone reward object."""
        milestone_def = self.milestone_definitions[milestone.milestone_id]
        
        reward = MilestoneReward(
            reward_id=str(uuid4()),
            milestone_instance_id=milestone.milestone_instance_id,
            creator_id=milestone.creator_id,
            milestone_id=milestone.milestone_id,
            base_amount=milestone_def.base_reward_amount,
            bonus_amount=milestone.calculated_reward - milestone_def.base_reward_amount,
            total_amount=milestone.calculated_reward,
            calculation_method=milestone_def.reward_calculation_method.value,
            calculation_details={
                "difficulty_level": milestone_def.difficulty_level,
                "streak_count": milestone.streak_count,
                "bonus_multiplier": milestone.bonus_multiplier,
                "achievement_time": (milestone.achieved_at - milestone.started_at).total_seconds() if milestone.achieved_at else 0
            }
        )
        
        return reward
    
    async def _process_reward_payout(self, reward: MilestoneReward) -> bool:
        """Process the actual reward payout."""
        # In production, this would integrate with payment systems
        try:
            # Simulate payment processing
            reward.status = "completed"
            reward.processed_at = datetime.utcnow()
            reward.transaction_id = f"txn_{str(uuid4())[:8]}"
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing reward payout: {e}")
            reward.status = "failed"
            return False
    
    async def get_creator_milestone_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive milestone summary for creator."""
        try:
            creator_milestones = self.creator_milestones.get(creator_id, [])
            creator_rewards = self.milestone_rewards.get(creator_id, [])
            
            if not creator_milestones:
                return {"creator_id": creator_id, "message": "No milestones found"}
            
            # Calculate statistics
            total_milestones = len(creator_milestones)
            achieved_milestones = len([m for m in creator_milestones if m.status == MilestoneStatus.ACHIEVED])
            rewarded_milestones = len([m for m in creator_milestones if m.status == MilestoneStatus.REWARDED])
            in_progress = len([m for m in creator_milestones if m.status == MilestoneStatus.IN_PROGRESS])
            
            total_rewards = sum(r.total_amount for r in creator_rewards)
            
            # Category breakdown
            category_stats = {}
            for milestone in creator_milestones:
                milestone_def = self.milestone_definitions.get(milestone.milestone_id)
                if milestone_def:
                    category = milestone_def.category.value
                    if category not in category_stats:
                        category_stats[category] = {"total": 0, "achieved": 0}
                    category_stats[category]["total"] += 1
                    if milestone.status in [MilestoneStatus.ACHIEVED, MilestoneStatus.REWARDED]:
                        category_stats[category]["achieved"] += 1
            
            # Recent achievements
            recent_achievements = sorted(
                [m for m in creator_milestones if m.achieved_at],
                key=lambda x: x.achieved_at,
                reverse=True
            )[:5]
            
            # Next milestones to achieve
            next_milestones = sorted(
                [m for m in creator_milestones if m.status == MilestoneStatus.IN_PROGRESS],
                key=lambda x: x.progress_percentage,
                reverse=True
            )[:5]
            
            return {
                "creator_id": creator_id,
                "overview": {
                    "total_milestones": total_milestones,
                    "achieved_milestones": achieved_milestones,
                    "rewarded_milestones": rewarded_milestones,
                    "in_progress": in_progress,
                    "completion_rate": round((achieved_milestones / total_milestones) * 100, 1),
                    "total_rewards_earned": float(total_rewards),
                    "currency": self.default_currency
                },
                "category_breakdown": {
                    cat: {
                        "total": stats["total"],
                        "achieved": stats["achieved"],
                        "completion_rate": round((stats["achieved"] / stats["total"]) * 100, 1)
                    }
                    for cat, stats in category_stats.items()
                },
                "recent_achievements": [
                    {
                        "milestone_id": m.milestone_id,
                        "name": self.milestone_definitions.get(m.milestone_id, {}).name if m.milestone_id in self.milestone_definitions else m.milestone_id,
                        "achieved_at": m.achieved_at.isoformat() if m.achieved_at else None,
                        "reward_amount": float(m.calculated_reward) if m.calculated_reward else 0,
                        "category": self.milestone_definitions.get(m.milestone_id, {}).category.value if m.milestone_id in self.milestone_definitions else "unknown"
                    }
                    for m in recent_achievements
                ],
                "next_milestones": [
                    {
                        "milestone_id": m.milestone_id,
                        "name": self.milestone_definitions.get(m.milestone_id, {}).name if m.milestone_id in self.milestone_definitions else m.milestone_id,
                        "progress_percentage": round(m.progress_percentage, 1),
                        "current_value": float(m.current_value),
                        "target_value": float(m.target_value),
                        "potential_reward": float(self.milestone_definitions.get(m.milestone_id, {}).base_reward_amount) if m.milestone_id in self.milestone_definitions else 0
                    }
                    for m in next_milestones
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting milestone summary for creator {creator_id}: {e}")
            return {"error": str(e)}
    
    async def get_system_milestone_analytics(self) -> Dict[str, Any]:
        """Get system-wide milestone analytics."""
        try:
            total_creators = len(self.creator_milestones)
            
            if total_creators == 0:
                return {"message": "No milestone data found"}
            
            # Calculate overall statistics
            total_milestones_tracked = sum(len(milestones) for milestones in self.creator_milestones.values())
            total_achieved = sum(
                len([m for m in milestones if m.status == MilestoneStatus.ACHIEVED])
                for milestones in self.creator_milestones.values()
            )
            
            # Most popular milestones
            milestone_counts = {}
            for milestones in self.creator_milestones.values():
                for milestone in milestones:
                    if milestone.status == MilestoneStatus.ACHIEVED:
                        mid = milestone.milestone_id
                        milestone_counts[mid] = milestone_counts.get(mid, 0) + 1
            
            popular_milestones = sorted(
                milestone_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Category performance
            category_performance = {}
            for category in MilestoneCategory:
                category_milestones = [
                    m for milestones in self.creator_milestones.values()
                    for m in milestones
                    if self.milestone_definitions.get(m.milestone_id, {}).category == category
                ]
                
                if category_milestones:
                    achieved_in_category = len([m for m in category_milestones if m.status == MilestoneStatus.ACHIEVED])
                    category_performance[category.value] = {
                        "total": len(category_milestones),
                        "achieved": achieved_in_category,
                        "completion_rate": round((achieved_in_category / len(category_milestones)) * 100, 1)
                    }
            
            return {
                "overview": {
                    "total_creators": total_creators,
                    "total_milestones_tracked": total_milestones_tracked,
                    "total_achieved": total_achieved,
                    "overall_completion_rate": round((total_achieved / total_milestones_tracked) * 100, 1),
                    "total_rewards_distributed": float(self.total_rewards_calculated),
                    "currency": self.default_currency
                },
                "popular_milestones": [
                    {
                        "milestone_id": mid,
                        "name": self.milestone_definitions.get(mid, {}).name if mid in self.milestone_definitions else mid,
                        "achievement_count": count,
                        "category": self.milestone_definitions.get(mid, {}).category.value if mid in self.milestone_definitions else "unknown"
                    }
                    for mid, count in popular_milestones
                ],
                "category_performance": category_performance,
                "system_health": {
                    "average_milestones_per_creator": round(total_milestones_tracked / total_creators, 1),
                    "achievement_velocity": round(total_achieved / max(total_creators, 1), 1),
                    "reward_efficiency": round(float(self.total_rewards_calculated) / max(total_achieved, 1), 2)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system milestone analytics: {e}")
            return {"error": str(e)}


# Global instance
_milestone_reward_calculator: Optional[MilestoneRewardCalculator] = None

async def get_milestone_reward_calculator() -> MilestoneRewardCalculator:
    """Get the global milestone reward calculator instance."""
    global _milestone_reward_calculator
    
    if _milestone_reward_calculator is None:
        _milestone_reward_calculator = MilestoneRewardCalculator()
        await _milestone_reward_calculator.initialize()
    
    return _milestone_reward_calculator