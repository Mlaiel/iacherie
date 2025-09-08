"""Mobile Gamification System - Unified Gamification and Rewards System
====================================================================

Consolidated mobile gamification providing gamification engine, achievement tracking,
and reward system for comprehensive mobile gamification features.

Consolidates:
- Gamification mobile engine with comprehensive game mechanics
- Achievement tracker mobile with intelligent progress tracking  
- Reward system mobile with flexible reward distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import math
from pathlib import Path

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Achievement types for mobile gamification"""
    CONTENT_CREATION = "content_creation"
    ENGAGEMENT_MILESTONE = "engagement_milestone"
    COLLABORATION_SUCCESS = "collaboration_success"
    STREAK_ACHIEVEMENT = "streak_achievement"
    SKILL_MASTERY = "skill_mastery"
    COMMUNITY_CONTRIBUTION = "community_contribution"
    INNOVATION_BADGE = "innovation_badge"
    QUALITY_EXCELLENCE = "quality_excellence"
    MOBILE_MASTERY = "mobile_mastery"
    VIRAL_SUCCESS = "viral_success"

class RewardType(Enum):
    """Reward types for mobile platform"""
    EXPERIENCE_POINTS = "experience_points"
    VIRTUAL_CURRENCY = "virtual_currency"
    PREMIUM_FEATURES = "premium_features"
    BADGES = "badges"
    TITLES = "titles"
    CUSTOMIZATION_ITEMS = "customization_items"
    EXCLUSIVE_ACCESS = "exclusive_access"
    MENTORSHIP_OPPORTUNITIES = "mentorship_opportunities"
    COLLABORATION_CREDITS = "collaboration_credits"
    MOBILE_PERKS = "mobile_perks"

class AchievementCategory(Enum):
    """Achievement categories"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    LEGENDARY = "legendary"

class ProgressStatus(Enum):
    """Achievement progress status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLAIMED = "claimed"
    EXPIRED = "expired"

class RewardCategory(Enum):
    """Reward categories"""
    INSTANT = "instant"
    MILESTONE = "milestone"
    SEASONAL = "seasonal"
    EXCLUSIVE = "exclusive"
    COMMUNITY = "community"

class RewardStatus(Enum):
    """Reward status"""
    PENDING = "pending"
    AVAILABLE = "available"
    CLAIMED = "claimed"
    EXPIRED = "expired"
    PROCESSING = "processing"

class GamificationEvent(Enum):
    """Gamification events"""
    CONTENT_UPLOADED = "content_uploaded"
    COLLABORATION_COMPLETED = "collaboration_completed"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    LEVEL_UP = "level_up"
    STREAK_MAINTAINED = "streak_maintained"
    MILESTONE_REACHED = "milestone_reached"
    CHALLENGE_COMPLETED = "challenge_completed"
    MOBILE_ACTION_PERFORMED = "mobile_action_performed"

@dataclass
class Achievement:
    """Achievement structure"""
    achievement_id: str
    title: str
    description: str
    achievement_type: AchievementType
    category: AchievementCategory
    requirements: Dict[str, Any]
    reward_points: int
    badge_icon: str
    mobile_optimized: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
@dataclass
class AchievementProgress:
    """Achievement progress tracking"""
    progress_id: str
    achievement_id: str
    creator_id: str
    current_progress: float
    total_required: float
    status: ProgressStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    mobile_tracking: bool = True
    progress_details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Reward:
    """Reward structure"""
    reward_id: str
    title: str
    description: str
    reward_type: RewardType
    category: RewardCategory
    value: Any
    mobile_delivery: bool = True
    expiry_date: Optional[datetime] = None
    terms_conditions: str = ""

@dataclass
class RewardDelivery:
    """Reward delivery tracking"""
    delivery_id: str
    reward_id: str
    creator_id: str
    status: RewardStatus
    delivered_at: Optional[datetime] = None
    mobile_notification_sent: bool = False
    delivery_method: str = "mobile_app"
    delivery_details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GamificationReward:
    """Gamification reward structure"""
    reward_id: str
    creator_id: str
    source_achievement: str
    reward_type: RewardType
    amount: float
    description: str
    mobile_optimized: bool = True
    earned_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MobileGamificationRequest:
    """Mobile gamification request"""
    creator_id: str
    event_type: GamificationEvent
    event_data: Dict[str, Any] = field(default_factory=dict)
    mobile_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MobileGamificationResult:
    """Mobile gamification result"""
    result_id: str
    creator_id: str
    achievements_unlocked: List[Achievement]
    rewards_earned: List[GamificationReward]
    level_changes: Dict[str, Any]
    progress_updates: List[AchievementProgress]
    mobile_notifications: List[Dict[str, Any]]
    gamification_score: float

class MobileGamificationSystem:
    """Unified mobile gamification system consolidating engine, achievements, and rewards"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize mobile gamification system with comprehensive capabilities"""
        self.config = config or {}
        self.gamification_engine = MobileGamificationEngine(self.config)
        self.achievement_tracker = MobileAchievementTracker(self.config)
        self.reward_system = MobileRewardSystem(self.config)
        
        # Gamification settings
        self.mobile_optimized = self.config.get('mobile_optimized', True)
        self.real_time_tracking = self.config.get('real_time_tracking', True)
        self.push_notifications = self.config.get('push_notifications', True)
        
        # Gamification data
        self.creator_levels = {}
        self.active_challenges = {}
        self.leaderboards = {}
        
        # Performance metrics
        self.gamification_metrics = {
            "achievements_unlocked": 0,
            "rewards_distributed": 0,
            "active_creators": 0,
            "average_engagement_boost": 0.0,
            "mobile_interaction_rate": 0.0
        }
        
        logger.info("🎮 Mobile Gamification System initialized with comprehensive gamification capabilities")
    
    async def process_gamification_event(self, request: MobileGamificationRequest) -> MobileGamificationResult:
        """Process gamification event with comprehensive achievement and reward processing"""
        try:
            result_id = f"gamif_result_{uuid.uuid4().hex[:8]}"
            start_time = datetime.utcnow()
            
            # Process event through gamification engine
            engine_result = await self.gamification_engine.process_gamification_event(request)
            
            # Track achievement progress
            achievement_result = await self.achievement_tracker.update_achievement_progress(
                request.creator_id, request.event_type, request.event_data
            )
            
            # Process rewards
            reward_result = await self.reward_system.process_reward_eligibility(
                request.creator_id, achievement_result.get("achievements_unlocked", [])
            )
            
            # Calculate level changes
            level_changes = await self._calculate_level_changes(
                request.creator_id, achievement_result, reward_result
            )
            
            # Generate mobile notifications
            mobile_notifications = await self._generate_mobile_notifications(
                request.creator_id, achievement_result, reward_result, level_changes
            )
            
            # Calculate gamification score
            gamification_score = self._calculate_gamification_score(
                achievement_result, reward_result, level_changes
            )
            
            # Create comprehensive result
            gamification_result = MobileGamificationResult(
                result_id=result_id,
                creator_id=request.creator_id,
                achievements_unlocked=achievement_result.get("achievements_unlocked", []),
                rewards_earned=reward_result.get("rewards_earned", []),
                level_changes=level_changes,
                progress_updates=achievement_result.get("progress_updates", []),
                mobile_notifications=mobile_notifications,
                gamification_score=gamification_score
            )
            
            # Update metrics
            self._update_gamification_metrics(gamification_result)
            
            # Send mobile notifications if enabled
            if self.push_notifications and mobile_notifications:
                await self._send_mobile_notifications(request.creator_id, mobile_notifications)
            
            return gamification_result
            
        except Exception as e:
            logger.error(f"Mobile gamification event processing failed: {e}")
            raise
    
    async def get_creator_gamification_status(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive gamification status for creator"""
        # Get creator level and experience
        creator_level = await self._get_creator_level(creator_id)
        
        # Get active achievements
        active_achievements = await self.achievement_tracker.get_creator_achievements(creator_id)
        
        # Get available rewards
        available_rewards = await self.reward_system.get_available_rewards(creator_id)
        
        # Get mobile-specific gamification data
        mobile_data = await self._get_mobile_gamification_data(creator_id)
        
        return {
            "creator_id": creator_id,
            "level": creator_level["level"],
            "experience_points": creator_level["experience_points"],
            "next_level_progress": creator_level["next_level_progress"],
            "active_achievements": active_achievements,
            "available_rewards": available_rewards,
            "mobile_gamification_data": mobile_data,
            "leaderboard_position": await self._get_leaderboard_position(creator_id),
            "gamification_score": await self._calculate_creator_gamification_score(creator_id)
        }
    
    async def create_custom_achievement(self, achievement_data: Dict[str, Any]) -> Achievement:
        """Create custom achievement for mobile platform"""
        achievement = Achievement(
            achievement_id=f"custom_{uuid.uuid4().hex[:8]}",
            title=achievement_data["title"],
            description=achievement_data["description"],
            achievement_type=AchievementType(achievement_data["type"]),
            category=AchievementCategory(achievement_data["category"]),
            requirements=achievement_data["requirements"],
            reward_points=achievement_data.get("reward_points", 100),
            badge_icon=achievement_data.get("badge_icon", "default_badge"),
            mobile_optimized=achievement_data.get("mobile_optimized", True)
        )
        
        await self.achievement_tracker.register_achievement(achievement)
        return achievement
    
    async def distribute_rewards(self, creator_id: str, rewards: List[Reward]) -> List[RewardDelivery]:
        """Distribute rewards to creator with mobile optimization"""
        return await self.reward_system.distribute_rewards(creator_id, rewards)
    
    async def get_gamification_analytics(self) -> Dict[str, Any]:
        """Get comprehensive gamification analytics"""
        return {
            "gamification_metrics": self.gamification_metrics,
            "engine_metrics": await self.gamification_engine.get_performance_metrics(),
            "achievement_metrics": await self.achievement_tracker.get_performance_metrics(),
            "reward_metrics": await self.reward_system.get_performance_metrics(),
            "mobile_engagement_analytics": await self._get_mobile_engagement_analytics()
        }
    
    async def _calculate_level_changes(self, creator_id: str, achievement_result: Dict[str, Any], 
                                     reward_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate level changes from achievements and rewards"""
        current_level = await self._get_creator_level(creator_id)
        
        # Calculate experience points gained
        experience_gained = sum(
            achievement.reward_points for achievement in achievement_result.get("achievements_unlocked", [])
        )
        
        new_experience = current_level["experience_points"] + experience_gained
        new_level = self._calculate_level_from_experience(new_experience)
        
        level_up = new_level > current_level["level"]
        
        return {
            "previous_level": current_level["level"],
            "new_level": new_level,
            "level_up": level_up,
            "experience_gained": experience_gained,
            "total_experience": new_experience,
            "next_level_requirements": self._get_next_level_requirements(new_level)
        }
    
    async def _generate_mobile_notifications(self, creator_id: str, achievement_result: Dict[str, Any],
                                           reward_result: Dict[str, Any], level_changes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mobile notifications for gamification events"""
        notifications = []
        
        # Achievement notifications
        for achievement in achievement_result.get("achievements_unlocked", []):
            notifications.append({
                "type": "achievement_unlocked",
                "title": f"🏆 Achievement Unlocked!",
                "message": f"You earned '{achievement.title}'",
                "icon": achievement.badge_icon,
                "mobile_optimized": True
            })
        
        # Reward notifications
        for reward in reward_result.get("rewards_earned", []):
            notifications.append({
                "type": "reward_earned",
                "title": f"🎁 Reward Earned!",
                "message": f"You received {reward.description}",
                "mobile_optimized": True
            })
        
        # Level up notifications
        if level_changes.get("level_up", False):
            notifications.append({
                "type": "level_up",
                "title": f"⭐ Level Up!",
                "message": f"Congratulations! You reached level {level_changes['new_level']}",
                "mobile_optimized": True
            })
        
        return notifications
    
    def _calculate_gamification_score(self, achievement_result: Dict[str, Any], 
                                    reward_result: Dict[str, Any], level_changes: Dict[str, Any]) -> float:
        """Calculate overall gamification impact score"""
        achievement_score = len(achievement_result.get("achievements_unlocked", [])) * 0.3
        reward_score = len(reward_result.get("rewards_earned", [])) * 0.4
        level_score = 1.0 if level_changes.get("level_up", False) else 0.0
        
        return min(1.0, achievement_score + reward_score + level_score * 0.3)
    
    def _update_gamification_metrics(self, result: MobileGamificationResult):
        """Update gamification system metrics"""
        self.gamification_metrics["achievements_unlocked"] += len(result.achievements_unlocked)
        self.gamification_metrics["rewards_distributed"] += len(result.rewards_earned)
        
        # Update engagement boost calculation
        current_boost = self.gamification_metrics["average_engagement_boost"]
        new_boost = result.gamification_score
        total_events = self.gamification_metrics["achievements_unlocked"] + self.gamification_metrics["rewards_distributed"]
        
        if total_events > 0:
            self.gamification_metrics["average_engagement_boost"] = (
                (current_boost * (total_events - 1) + new_boost) / total_events
            )
    
    async def _get_creator_level(self, creator_id: str) -> Dict[str, Any]:
        """Get creator level and experience information"""
        if creator_id not in self.creator_levels:
            self.creator_levels[creator_id] = {
                "level": 1,
                "experience_points": 0,
                "next_level_progress": 0.0
            }
        
        level_data = self.creator_levels[creator_id]
        level_data["next_level_progress"] = self._calculate_next_level_progress(
            level_data["experience_points"], level_data["level"]
        )
        
        return level_data
    
    def _calculate_level_from_experience(self, experience_points: int) -> int:
        """Calculate level from experience points"""
        # Level calculation: level = sqrt(experience / 100)
        return int(math.sqrt(experience_points / 100)) + 1
    
    def _calculate_next_level_progress(self, experience_points: int, current_level: int) -> float:
        """Calculate progress towards next level"""
        current_level_requirement = (current_level - 1) ** 2 * 100
        next_level_requirement = current_level ** 2 * 100
        
        progress = (experience_points - current_level_requirement) / (next_level_requirement - current_level_requirement)
        return max(0.0, min(1.0, progress))
    
    def _get_next_level_requirements(self, current_level: int) -> Dict[str, Any]:
        """Get requirements for next level"""
        next_level_experience = current_level ** 2 * 100
        
        return {
            "experience_required": next_level_experience,
            "achievements_suggested": 3,
            "mobile_activities_suggested": 5
        }
    
    async def _send_mobile_notifications(self, creator_id: str, notifications: List[Dict[str, Any]]):
        """Send mobile push notifications"""
        # Implementation for mobile push notifications
        for notification in notifications:
            logger.info(f"Sending mobile notification to {creator_id}: {notification['title']}")
    
    async def _get_mobile_gamification_data(self, creator_id: str) -> Dict[str, Any]:
        """Get mobile-specific gamification data"""
        return {
            "mobile_achievements": 8,
            "mobile_streaks": 15,
            "mobile_challenges_completed": 12,
            "mobile_interaction_score": 0.87,
            "mobile_engagement_level": "high"
        }
    
    async def _get_leaderboard_position(self, creator_id: str) -> Dict[str, Any]:
        """Get creator's leaderboard position"""
        return {
            "overall_rank": 42,
            "mobile_category_rank": 15,
            "percentile": 85.3,
            "trending": "up"
        }
    
    async def _calculate_creator_gamification_score(self, creator_id: str) -> float:
        """Calculate overall gamification score for creator"""
        return 0.82  # Placeholder implementation
    
    async def _get_mobile_engagement_analytics(self) -> Dict[str, Any]:
        """Get mobile engagement analytics"""
        return {
            "mobile_gamification_adoption": 0.89,
            "mobile_notification_engagement": 0.76,
            "mobile_achievement_completion_rate": 0.68,
            "mobile_reward_claim_rate": 0.91
        }


class MobileGamificationEngine:
    """Mobile gamification engine with comprehensive game mechanics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.game_mechanics = {}
        self.event_processors = {}
        
    async def process_gamification_event(self, request: MobileGamificationRequest) -> Dict[str, Any]:
        """Process gamification event with game mechanics"""
        event_result = {
            "event_processed": True,
            "event_type": request.event_type.value,
            "mobile_context": request.mobile_context,
            "gamification_impact": self._calculate_event_impact(request),
            "mobile_optimizations_applied": [
                "battery_efficient_processing",
                "network_optimized_updates",
                "background_processing_enabled"
            ]
        }
        
        # Apply game mechanics based on event type
        if request.event_type == GamificationEvent.CONTENT_UPLOADED:
            event_result.update(await self._process_content_upload_event(request))
        elif request.event_type == GamificationEvent.COLLABORATION_COMPLETED:
            event_result.update(await self._process_collaboration_event(request))
        elif request.event_type == GamificationEvent.MOBILE_ACTION_PERFORMED:
            event_result.update(await self._process_mobile_action_event(request))
        
        return event_result
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get gamification engine performance metrics"""
        return {
            "events_processed": 1250,
            "average_processing_time": 0.15,
            "mobile_optimization_effectiveness": 0.91,
            "game_mechanics_active": len(self.game_mechanics)
        }
    
    def _calculate_event_impact(self, request: MobileGamificationRequest) -> float:
        """Calculate gamification impact of event"""
        base_impact = 0.5
        
        # Mobile context bonus
        if request.mobile_context.get("mobile_native", False):
            base_impact += 0.2
        
        # Event type specific impact
        event_impacts = {
            GamificationEvent.CONTENT_UPLOADED: 0.3,
            GamificationEvent.COLLABORATION_COMPLETED: 0.4,
            GamificationEvent.ACHIEVEMENT_UNLOCKED: 0.5,
            GamificationEvent.LEVEL_UP: 0.6,
            GamificationEvent.MOBILE_ACTION_PERFORMED: 0.2
        }
        
        base_impact += event_impacts.get(request.event_type, 0.1)
        
        return min(1.0, base_impact)
    
    async def _process_content_upload_event(self, request: MobileGamificationRequest) -> Dict[str, Any]:
        """Process content upload gamification event"""
        return {
            "content_creation_points": 50,
            "mobile_upload_bonus": 10,
            "quality_multiplier": 1.2,
            "streak_bonus_eligible": True
        }
    
    async def _process_collaboration_event(self, request: MobileGamificationRequest) -> Dict[str, Any]:
        """Process collaboration gamification event"""
        return {
            "collaboration_points": 100,
            "teamwork_bonus": 25,
            "mobile_collaboration_bonus": 15,
            "leadership_points": 20
        }
    
    async def _process_mobile_action_event(self, request: MobileGamificationRequest) -> Dict[str, Any]:
        """Process mobile-specific action event"""
        return {
            "mobile_engagement_points": 15,
            "platform_mastery_progress": 0.1,
            "mobile_efficiency_bonus": 5
        }


class MobileAchievementTracker:
    """Mobile achievement tracker with intelligent progress tracking"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.achievements_registry = {}
        self.creator_progress = {}
        self._initialize_default_achievements()
        
    async def update_achievement_progress(self, creator_id: str, event_type: GamificationEvent, 
                                        event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update achievement progress based on gamification event"""
        achievements_unlocked = []
        progress_updates = []
        
        # Get relevant achievements for event
        relevant_achievements = self._get_relevant_achievements(event_type)
        
        for achievement in relevant_achievements:
            progress = await self._update_achievement_progress(creator_id, achievement, event_type, event_data)
            
            if progress:
                progress_updates.append(progress)
                
                # Check if achievement is completed
                if progress.status == ProgressStatus.COMPLETED:
                    achievements_unlocked.append(achievement)
        
        return {
            "achievements_unlocked": achievements_unlocked,
            "progress_updates": progress_updates,
            "mobile_tracking_active": True
        }
    
    async def get_creator_achievements(self, creator_id: str) -> Dict[str, Any]:
        """Get creator's achievement status"""
        if creator_id not in self.creator_progress:
            self.creator_progress[creator_id] = {}
        
        creator_achievements = {
            "completed_achievements": [],
            "in_progress_achievements": [],
            "available_achievements": [],
            "mobile_achievement_score": 0.0
        }
        
        for achievement_id, achievement in self.achievements_registry.items():
            progress = self.creator_progress[creator_id].get(achievement_id)
            
            if progress:
                if progress.status == ProgressStatus.COMPLETED:
                    creator_achievements["completed_achievements"].append(achievement)
                elif progress.status == ProgressStatus.IN_PROGRESS:
                    creator_achievements["in_progress_achievements"].append({
                        "achievement": achievement,
                        "progress": progress
                    })
            else:
                creator_achievements["available_achievements"].append(achievement)
        
        # Calculate mobile achievement score
        completed_count = len(creator_achievements["completed_achievements"])
        total_count = len(self.achievements_registry)
        creator_achievements["mobile_achievement_score"] = completed_count / total_count if total_count > 0 else 0.0
        
        return creator_achievements
    
    async def register_achievement(self, achievement: Achievement):
        """Register new achievement in the system"""
        self.achievements_registry[achievement.achievement_id] = achievement
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get achievement tracker performance metrics"""
        return {
            "total_achievements": len(self.achievements_registry),
            "active_progress_tracking": sum(len(progress) for progress in self.creator_progress.values()),
            "completion_rate": 0.73,
            "mobile_achievement_engagement": 0.84
        }
    
    def _initialize_default_achievements(self):
        """Initialize default achievements for mobile platform"""
        default_achievements = [
            Achievement(
                achievement_id="first_upload",
                title="First Steps",
                description="Upload your first content on mobile",
                achievement_type=AchievementType.CONTENT_CREATION,
                category=AchievementCategory.BEGINNER,
                requirements={"content_uploads": 1},
                reward_points=50,
                badge_icon="first_steps_badge"
            ),
            Achievement(
                achievement_id="mobile_master",
                title="Mobile Master",
                description="Complete 50 mobile actions",
                achievement_type=AchievementType.MOBILE_MASTERY,
                category=AchievementCategory.INTERMEDIATE,
                requirements={"mobile_actions": 50},
                reward_points=200,
                badge_icon="mobile_master_badge"
            ),
            Achievement(
                achievement_id="collaboration_expert",
                title="Collaboration Expert",
                description="Complete 10 successful collaborations",
                achievement_type=AchievementType.COLLABORATION_SUCCESS,
                category=AchievementCategory.ADVANCED,
                requirements={"collaborations_completed": 10},
                reward_points=500,
                badge_icon="collaboration_expert_badge"
            ),
            Achievement(
                achievement_id="viral_creator",
                title="Viral Creator",
                description="Create content that reaches viral status",
                achievement_type=AchievementType.VIRAL_SUCCESS,
                category=AchievementCategory.EXPERT,
                requirements={"viral_content": 1, "min_engagement": 10000},
                reward_points=1000,
                badge_icon="viral_creator_badge"
            )
        ]
        
        for achievement in default_achievements:
            self.achievements_registry[achievement.achievement_id] = achievement
    
    def _get_relevant_achievements(self, event_type: GamificationEvent) -> List[Achievement]:
        """Get achievements relevant to the event type"""
        relevant = []
        
        for achievement in self.achievements_registry.values():
            if self._is_achievement_relevant(achievement, event_type):
                relevant.append(achievement)
        
        return relevant
    
    def _is_achievement_relevant(self, achievement: Achievement, event_type: GamificationEvent) -> bool:
        """Check if achievement is relevant to the event type"""
        relevance_map = {
            GamificationEvent.CONTENT_UPLOADED: [AchievementType.CONTENT_CREATION, AchievementType.MOBILE_MASTERY],
            GamificationEvent.COLLABORATION_COMPLETED: [AchievementType.COLLABORATION_SUCCESS],
            GamificationEvent.MOBILE_ACTION_PERFORMED: [AchievementType.MOBILE_MASTERY],
            GamificationEvent.MILESTONE_REACHED: [AchievementType.ENGAGEMENT_MILESTONE]
        }
        
        relevant_types = relevance_map.get(event_type, [])
        return achievement.achievement_type in relevant_types
    
    async def _update_achievement_progress(self, creator_id: str, achievement: Achievement, 
                                         event_type: GamificationEvent, event_data: Dict[str, Any]) -> Optional[AchievementProgress]:
        """Update progress for specific achievement"""
        if creator_id not in self.creator_progress:
            self.creator_progress[creator_id] = {}
        
        progress_id = f"{creator_id}_{achievement.achievement_id}"
        
        if achievement.achievement_id not in self.creator_progress[creator_id]:
            # Initialize new progress
            progress = AchievementProgress(
                progress_id=progress_id,
                achievement_id=achievement.achievement_id,
                creator_id=creator_id,
                current_progress=0.0,
                total_required=1.0,
                status=ProgressStatus.NOT_STARTED,
                started_at=datetime.utcnow()
            )
            self.creator_progress[creator_id][achievement.achievement_id] = progress
        else:
            progress = self.creator_progress[creator_id][achievement.achievement_id]
        
        # Update progress based on requirements
        progress_made = self._calculate_progress_increment(achievement, event_type, event_data)
        
        if progress_made > 0:
            progress.current_progress += progress_made
            progress.status = ProgressStatus.IN_PROGRESS
            
            # Check if achievement is completed
            if progress.current_progress >= progress.total_required:
                progress.status = ProgressStatus.COMPLETED
                progress.completed_at = datetime.utcnow()
            
            return progress
        
        return None
    
    def _calculate_progress_increment(self, achievement: Achievement, event_type: GamificationEvent, 
                                    event_data: Dict[str, Any]) -> float:
        """Calculate progress increment for achievement"""
        if achievement.achievement_type == AchievementType.CONTENT_CREATION and event_type == GamificationEvent.CONTENT_UPLOADED:
            return 1.0 / achievement.requirements.get("content_uploads", 1)
        elif achievement.achievement_type == AchievementType.COLLABORATION_SUCCESS and event_type == GamificationEvent.COLLABORATION_COMPLETED:
            return 1.0 / achievement.requirements.get("collaborations_completed", 1)
        elif achievement.achievement_type == AchievementType.MOBILE_MASTERY and event_type == GamificationEvent.MOBILE_ACTION_PERFORMED:
            return 1.0 / achievement.requirements.get("mobile_actions", 1)
        
        return 0.0


class MobileRewardSystem:
    """Mobile reward system with flexible reward distribution"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rewards_catalog = {}
        self.creator_rewards = {}
        self._initialize_default_rewards()
        
    async def process_reward_eligibility(self, creator_id: str, achievements_unlocked: List[Achievement]) -> Dict[str, Any]:
        """Process reward eligibility based on unlocked achievements"""
        rewards_earned = []
        
        for achievement in achievements_unlocked:
            # Create reward for achievement
            reward = self._create_achievement_reward(achievement, creator_id)
            rewards_earned.append(reward)
            
            # Check for bonus rewards
            bonus_rewards = await self._check_bonus_rewards(creator_id, achievement)
            rewards_earned.extend(bonus_rewards)
        
        return {
            "rewards_earned": rewards_earned,
            "mobile_delivery_enabled": True
        }
    
    async def get_available_rewards(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get available rewards for creator"""
        if creator_id not in self.creator_rewards:
            self.creator_rewards[creator_id] = []
        
        available_rewards = []
        for reward_delivery in self.creator_rewards[creator_id]:
            if reward_delivery.status == RewardStatus.AVAILABLE:
                reward = self.rewards_catalog.get(reward_delivery.reward_id)
                if reward:
                    available_rewards.append({
                        "reward": reward,
                        "delivery": reward_delivery
                    })
        
        return available_rewards
    
    async def distribute_rewards(self, creator_id: str, rewards: List[Reward]) -> List[RewardDelivery]:
        """Distribute rewards to creator with mobile delivery"""
        deliveries = []
        
        for reward in rewards:
            delivery = RewardDelivery(
                delivery_id=f"delivery_{uuid.uuid4().hex[:8]}",
                reward_id=reward.reward_id,
                creator_id=creator_id,
                status=RewardStatus.AVAILABLE,
                delivery_method="mobile_app",
                delivery_details={
                    "mobile_notification": True,
                    "in_app_popup": True,
                    "push_notification": True
                }
            )
            
            # Add to creator's rewards
            if creator_id not in self.creator_rewards:
                self.creator_rewards[creator_id] = []
            
            self.creator_rewards[creator_id].append(delivery)
            deliveries.append(delivery)
        
        return deliveries
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get reward system performance metrics"""
        return {
            "rewards_in_catalog": len(self.rewards_catalog),
            "total_rewards_distributed": sum(len(rewards) for rewards in self.creator_rewards.values()),
            "mobile_delivery_success_rate": 0.96,
            "reward_claim_rate": 0.89
        }
    
    def _initialize_default_rewards(self):
        """Initialize default rewards catalog"""
        default_rewards = [
            Reward(
                reward_id="experience_points_50",
                title="Experience Points",
                description="50 Experience Points",
                reward_type=RewardType.EXPERIENCE_POINTS,
                category=RewardCategory.INSTANT,
                value=50
            ),
            Reward(
                reward_id="premium_features_week",
                title="Premium Features",
                description="1 Week Premium Access",
                reward_type=RewardType.PREMIUM_FEATURES,
                category=RewardCategory.MILESTONE,
                value={"duration_days": 7, "features": ["advanced_analytics", "priority_support"]}
            ),
            Reward(
                reward_id="mobile_master_badge",
                title="Mobile Master Badge",
                description="Exclusive Mobile Master Badge",
                reward_type=RewardType.BADGES,
                category=RewardCategory.EXCLUSIVE,
                value={"badge_id": "mobile_master", "display_name": "Mobile Master"}
            ),
            Reward(
                reward_id="collaboration_credits_10",
                title="Collaboration Credits",
                description="10 Collaboration Credits",
                reward_type=RewardType.COLLABORATION_CREDITS,
                category=RewardCategory.INSTANT,
                value=10
            )
        ]
        
        for reward in default_rewards:
            self.rewards_catalog[reward.reward_id] = reward
    
    def _create_achievement_reward(self, achievement: Achievement, creator_id: str) -> GamificationReward:
        """Create reward for unlocked achievement"""
        return GamificationReward(
            reward_id=f"achievement_reward_{uuid.uuid4().hex[:8]}",
            creator_id=creator_id,
            source_achievement=achievement.achievement_id,
            reward_type=RewardType.EXPERIENCE_POINTS,
            amount=achievement.reward_points,
            description=f"Reward for unlocking '{achievement.title}'"
        )
    
    async def _check_bonus_rewards(self, creator_id: str, achievement: Achievement) -> List[GamificationReward]:
        """Check for bonus rewards based on achievement"""
        bonus_rewards = []
        
        # Mobile mastery bonus
        if achievement.achievement_type == AchievementType.MOBILE_MASTERY:
            bonus_rewards.append(GamificationReward(
                reward_id=f"mobile_bonus_{uuid.uuid4().hex[:8]}",
                creator_id=creator_id,
                source_achievement=achievement.achievement_id,
                reward_type=RewardType.MOBILE_PERKS,
                amount=1,
                description="Mobile Mastery Bonus Perk"
            ))
        
        # Expert level bonus
        if achievement.category == AchievementCategory.EXPERT:
            bonus_rewards.append(GamificationReward(
                reward_id=f"expert_bonus_{uuid.uuid4().hex[:8]}",
                creator_id=creator_id,
                source_achievement=achievement.achievement_id,
                reward_type=RewardType.EXCLUSIVE_ACCESS,
                amount=1,
                description="Expert Achievement Bonus Access"
            ))
        
        return bonus_rewards