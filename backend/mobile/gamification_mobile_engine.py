"""Mobile Gamification Engine

Advanced mobile gamification system for creator engagement with achievements,
rewards, challenges, leaderboards, and mobile-optimized gaming mechanics
to enhance user experience and platform engagement.

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


class AchievementType(Enum):
    """Types of achievements"""
    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    ENGAGEMENT = "engagement"
    SKILL_DEVELOPMENT = "skill_development"
    COMMUNITY = "community"
    MILESTONE = "milestone"


class RewardType(Enum):
    """Types of rewards"""
    POINTS = "points"
    BADGE = "badge"
    UNLOCK = "unlock"
    FEATURE_ACCESS = "feature_access"
    RECOGNITION = "recognition"


@dataclass
class Achievement:
    """Achievement definition"""
    achievement_id: str
    title: str
    description: str
    achievement_type: AchievementType
    points_value: int
    badge_icon: str
    unlock_criteria: Dict[str, Any]
    mobile_friendly: bool = True


@dataclass
class MobileGamificationConfiguration:
    """Mobile gamification configuration"""
    enable_achievements: bool = True
    enable_points_system: bool = True
    enable_leaderboards: bool = True
    enable_challenges: bool = True
    mobile_notifications: bool = True
    social_sharing: bool = True
    real_time_updates: bool = True


@dataclass
class MobileGamificationRequest:
    """Mobile gamification request"""
    request_id: str
    user_id: str
    action_type: str
    action_data: Dict[str, Any]
    mobile_config: MobileGamificationConfiguration
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


@dataclass
class GamificationReward:
    """Gamification reward"""
    reward_id: str
    reward_type: RewardType
    title: str
    description: str
    points_earned: int
    badge_unlocked: Optional[str] = None
    special_unlock: Optional[str] = None


@dataclass
class MobileGamificationResult:
    """Mobile gamification result"""
    request_id: str
    success: bool
    processing_time_ms: int
    rewards_earned: List[GamificationReward]
    achievements_unlocked: List[Achievement]
    current_level: int
    total_points: int
    leaderboard_position: int
    mobile_optimizations: List[str]
    analytics_data: Dict[str, Any]
    error_message: Optional[str] = None


class MobileGamificationEngine:
    """Mobile Gamification Engine
    
    Advanced mobile gamification system for creator engagement with achievements,
    rewards, and mobile-optimized gaming mechanics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Gamification data
        self.user_progress = {}
        self.achievements_catalog = self._initialize_achievements()
        self.leaderboard = {}
        
        # Performance tracking
        self.gamification_metrics = {
            "total_actions": 0,
            "rewards_distributed": 0,
            "achievements_unlocked": 0,
            "active_users": 0
        }
        
        self.logger.info("Mobile Gamification Engine initialized")
    
    def _initialize_achievements(self) -> List[Achievement]:
        """Initialize the achievements catalog."""
        return [
            Achievement(
                achievement_id="first_upload",
                title="First Steps",
                description="Upload your first content",
                achievement_type=AchievementType.CONTENT_CREATION,
                points_value=100,
                badge_icon="🚀",
                unlock_criteria={"uploads": 1}
            ),
            Achievement(
                achievement_id="mobile_master",
                title="Mobile Master",
                description="Complete 10 mobile-optimized uploads",
                achievement_type=AchievementType.SKILL_DEVELOPMENT,
                points_value=500,
                badge_icon="📱",
                unlock_criteria={"mobile_uploads": 10}
            ),
            Achievement(
                achievement_id="collaborator",
                title="Team Player",
                description="Complete your first collaboration",
                achievement_type=AchievementType.COLLABORATION,
                points_value=200,
                badge_icon="🤝",
                unlock_criteria={"collaborations": 1}
            ),
            Achievement(
                achievement_id="engagement_king",
                title="Engagement King",
                description="Reach 1000 total engagement points",
                achievement_type=AchievementType.ENGAGEMENT,
                points_value=300,
                badge_icon="👑",
                unlock_criteria={"engagement_points": 1000}
            )
        ]
    
    async def process_gamification(self, request: MobileGamificationRequest) -> MobileGamificationResult:
        """Process gamification for user action."""
        start_time = time.time()
        self.gamification_metrics["total_actions"] += 1
        
        self.logger.info(f"Processing gamification for user {request.user_id}")
        
        try:
            result = MobileGamificationResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=0,
                rewards_earned=[],
                achievements_unlocked=[],
                current_level=1,
                total_points=0,
                leaderboard_position=0,
                mobile_optimizations=[],
                analytics_data={}
            )
            
            # Core gamification pipeline
            await self._update_user_progress(request, result)
            await self._check_achievements(request, result)
            await self._calculate_rewards(request, result)
            await self._update_leaderboard(request, result)
            await self._apply_mobile_optimizations(request, result)
            await self._generate_gamification_analytics(request, result)
            
            result.success = True
            
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = int(processing_time)
            
            self.logger.info(f"Gamification processed successfully in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            self.logger.error(f"Gamification processing failed: {str(e)}")
            return MobileGamificationResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=int((time.time() - start_time) * 1000),
                rewards_earned=[],
                achievements_unlocked=[],
                current_level=1,
                total_points=0,
                leaderboard_position=0,
                mobile_optimizations=[],
                analytics_data={},
                error_message=str(e)
            )
    
    async def _update_user_progress(self, request: MobileGamificationRequest, result: MobileGamificationResult):
        """Update user progress based on action."""
        user_id = request.user_id
        
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                "total_points": 0,
                "level": 1,
                "uploads": 0,
                "mobile_uploads": 0,
                "collaborations": 0,
                "engagement_points": 0,
                "achievements": []
            }
        
        user_data = self.user_progress[user_id]
        
        # Update based on action type
        if request.action_type == "upload":
            user_data["uploads"] += 1
            if request.action_data.get("mobile_optimized", False):
                user_data["mobile_uploads"] += 1
        elif request.action_type == "collaboration":
            user_data["collaborations"] += 1
        elif request.action_type == "engagement":
            user_data["engagement_points"] += request.action_data.get("points", 10)
        
        result.total_points = user_data["total_points"]
        result.current_level = user_data["level"]
    
    async def _check_achievements(self, request: MobileGamificationRequest, result: MobileGamificationResult):
        """Check for newly unlocked achievements."""
        user_data = self.user_progress[request.user_id]
        new_achievements = []
        
        for achievement in self.achievements_catalog:
            if achievement.achievement_id in user_data["achievements"]:
                continue  # Already unlocked
            
            # Check unlock criteria
            criteria_met = True
            for criterion, required_value in achievement.unlock_criteria.items():
                user_value = user_data.get(criterion, 0)
                if user_value < required_value:
                    criteria_met = False
                    break
            
            if criteria_met:
                new_achievements.append(achievement)
                user_data["achievements"].append(achievement.achievement_id)
                user_data["total_points"] += achievement.points_value
                self.gamification_metrics["achievements_unlocked"] += 1
        
        result.achievements_unlocked = new_achievements
        result.total_points = user_data["total_points"]
    
    async def _calculate_rewards(self, request: MobileGamificationRequest, result: MobileGamificationResult):
        """Calculate rewards for the action."""
        rewards = []
        
        # Base action rewards
        base_points = {
            "upload": 50,
            "collaboration": 100,
            "engagement": 25,
            "mobile_action": 75
        }
        
        action_points = base_points.get(request.action_type, 10)
        
        # Mobile bonus
        if request.action_data.get("mobile_optimized", False):
            action_points = int(action_points * 1.2)  # 20% mobile bonus
        
        reward = GamificationReward(
            reward_id=str(uuid.uuid4()),
            reward_type=RewardType.POINTS,
            title=f"{request.action_type.title()} Reward",
            description=f"Points for {request.action_type}",
            points_earned=action_points
        )
        
        rewards.append(reward)
        
        # Achievement rewards
        for achievement in result.achievements_unlocked:
            achievement_reward = GamificationReward(
                reward_id=str(uuid.uuid4()),
                reward_type=RewardType.BADGE,
                title=achievement.title,
                description=achievement.description,
                points_earned=achievement.points_value,
                badge_unlocked=achievement.badge_icon
            )
            rewards.append(achievement_reward)
        
        result.rewards_earned = rewards
        self.gamification_metrics["rewards_distributed"] += len(rewards)
    
    async def _update_leaderboard(self, request: MobileGamificationRequest, result: MobileGamificationResult):
        """Update leaderboard position."""
        user_id = request.user_id
        user_points = self.user_progress[user_id]["total_points"]
        
        # Update leaderboard
        self.leaderboard[user_id] = user_points
        
        # Calculate position
        sorted_users = sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)
        position = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id), len(sorted_users))
        
        result.leaderboard_position = position
    
    async def _apply_mobile_optimizations(self, request: MobileGamificationRequest, result: MobileGamificationResult):
        """Apply mobile-specific optimizations."""
        mobile_optimizations = [
            "mobile_animations",
            "touch_feedback",
            "haptic_responses",
            "progressive_rewards",
            "mobile_notifications",
            "social_sharing_integration",
            "achievement_popups",
            "leaderboard_mobile_view",
            "quick_actions",
            "gesture_controls"
        ]
        
        result.mobile_optimizations = mobile_optimizations
    
    async def _generate_gamification_analytics(self, request: MobileGamificationRequest, result: MobileGamificationResult):
        """Generate analytics data."""
        analytics = {
            "gamification_id": result.request_id,
            "user_id": request.user_id,
            "action_type": request.action_type,
            "rewards_count": len(result.rewards_earned),
            "achievements_unlocked_count": len(result.achievements_unlocked),
            "total_points": result.total_points,
            "current_level": result.current_level,
            "leaderboard_position": result.leaderboard_position,
            "mobile_optimizations_count": len(result.mobile_optimizations),
            "processing_time_ms": result.processing_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result.analytics_data = analytics


# Export key classes and functions
__all__ = [
    "MobileGamificationEngine",
    "MobileGamificationRequest", 
    "MobileGamificationResult",
    "Achievement",
    "GamificationReward",
    "MobileGamificationConfiguration",
    "AchievementType",
    "RewardType"
]