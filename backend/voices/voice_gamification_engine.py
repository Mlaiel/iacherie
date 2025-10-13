"""
🎮 Voice Gamification Engine - Gamify Voice Content Creation
Challenges, achievements, leaderboards, rewards for voice creators

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class AchievementType(Enum):
    """Types of achievements"""
    FIRST_VOICE = "first_voice"
    VOICE_MASTER = "voice_master"
    COLLABORATION_PRO = "collaboration_pro"
    QUALITY_EXPERT = "quality_expert"
    VIRAL_CREATOR = "viral_creator"
    EARLY_ADOPTER = "early_adopter"
    COMMUNITY_HERO = "community_hero"


class ChallengeType(Enum):
    """Types of challenges"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIAL_EVENT = "special_event"
    COMMUNITY = "community"


@dataclass
class Achievement:
    """Achievement data structure"""
    achievement_id: str
    name: str
    description: str
    achievement_type: AchievementType
    points: int
    icon_url: str
    unlocked_at: Optional[datetime] = None


@dataclass
class Challenge:
    """Challenge data structure"""
    challenge_id: str
    name: str
    description: str
    challenge_type: ChallengeType
    reward_points: int
    start_date: datetime
    end_date: datetime
    requirements: Dict[str, Any]
    participants: int = 0


@dataclass
class UserGamificationProfile:
    """User gamification profile"""
    user_id: str
    total_points: int
    level: int
    achievements: List[Achievement] = field(default_factory=list)
    completed_challenges: List[str] = field(default_factory=list)
    streak_days: int = 0
    last_activity: Optional[datetime] = None


class VoiceGamificationEngine:
    """
    Main gamification engine
    """
    
    def __init__(self):
        """Initialize gamification engine"""
        self.user_profiles: Dict[str, UserGamificationProfile] = {}
        self.achievements_catalog: Dict[str, Achievement] = {}
        self.active_challenges: Dict[str, Challenge] = {}
        self.leaderboard: List[Dict[str, Any]] = []
        
        self._initialize_achievements()
        logger.info("🎮 Voice Gamification Engine initialized")
    
    def _initialize_achievements(self):
        """Initialize achievement catalog"""
        achievements = [
            Achievement("first_voice", "First Voice", "Create your first voice", 
                       AchievementType.FIRST_VOICE, 10, "🎤"),
            Achievement("voice_master", "Voice Master", "Create 100 voices", 
                       AchievementType.VOICE_MASTER, 500, "🏆"),
            Achievement("collab_pro", "Collaboration Pro", "Complete 10 collaborations", 
                       AchievementType.COLLABORATION_PRO, 200, "🤝"),
            Achievement("quality_expert", "Quality Expert", "Achieve 95% quality score", 
                       AchievementType.QUALITY_EXPERT, 300, "⭐"),
        ]
        
        for achievement in achievements:
            self.achievements_catalog[achievement.achievement_id] = achievement
    
    def get_or_create_profile(self, user_id: str) -> UserGamificationProfile:
        """Get or create user gamification profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserGamificationProfile(
                user_id=user_id,
                total_points=0,
                level=1,
                last_activity=datetime.utcnow()
            )
        return self.user_profiles[user_id]
    
    def award_points(self, user_id: str, points: int, reason: str = ""):
        """
        Award points to user
        
        Args:
            user_id: User identifier
            points: Points to award
            reason: Reason for points
        """
        profile = self.get_or_create_profile(user_id)
        profile.total_points += points
        profile.last_activity = datetime.utcnow()
        
        # Level up logic
        new_level = (profile.total_points // 100) + 1
        if new_level > profile.level:
            profile.level = new_level
            logger.info(f"🎉 User {user_id} leveled up to {new_level}!")
        
        logger.info(f"➕ Awarded {points} points to {user_id} - {reason}")
        
        self._update_leaderboard()
    
    def unlock_achievement(self, user_id: str, achievement_id: str):
        """
        Unlock achievement for user
        
        Args:
            user_id: User identifier
            achievement_id: Achievement to unlock
        """
        profile = self.get_or_create_profile(user_id)
        achievement = self.achievements_catalog.get(achievement_id)
        
        if not achievement:
            logger.error(f"❌ Achievement not found: {achievement_id}")
            return
        
        # Check if already unlocked
        if any(a.achievement_id == achievement_id for a in profile.achievements):
            logger.warning(f"⚠️ Achievement already unlocked: {achievement_id}")
            return
        
        # Unlock achievement
        unlocked = Achievement(
            achievement_id=achievement.achievement_id,
            name=achievement.name,
            description=achievement.description,
            achievement_type=achievement.achievement_type,
            points=achievement.points,
            icon_url=achievement.icon_url,
            unlocked_at=datetime.utcnow()
        )
        
        profile.achievements.append(unlocked)
        profile.total_points += achievement.points
        
        logger.info(f"🏆 Achievement unlocked: {achievement.name} for {user_id}")
    
    def check_achievements(self, user_id: str, action: str, metadata: Dict[str, Any]):
        """
        Check and unlock achievements based on user action
        
        Args:
            user_id: User identifier
            action: Action performed
            metadata: Additional metadata
        """
        if action == "voice_created":
            voice_count = metadata.get("total_voices", 0)
            if voice_count == 1:
                self.unlock_achievement(user_id, "first_voice")
            elif voice_count >= 100:
                self.unlock_achievement(user_id, "voice_master")
        
        elif action == "collaboration_completed":
            collab_count = metadata.get("total_collaborations", 0)
            if collab_count >= 10:
                self.unlock_achievement(user_id, "collab_pro")
    
    def create_challenge(self, name: str, description: str, challenge_type: ChallengeType,
                        reward_points: int, duration_days: int, 
                        requirements: Dict[str, Any]) -> Challenge:
        """Create new challenge"""
        challenge_id = f"chal_{int(datetime.utcnow().timestamp())}"
        
        challenge = Challenge(
            challenge_id=challenge_id,
            name=name,
            description=description,
            challenge_type=challenge_type,
            reward_points=reward_points,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow(),  # Add duration_days
            requirements=requirements
        )
        
        self.active_challenges[challenge_id] = challenge
        logger.info(f"🎯 Challenge created: {name}")
        
        return challenge
    
    def complete_challenge(self, user_id: str, challenge_id: str):
        """Mark challenge as completed"""
        profile = self.get_or_create_profile(user_id)
        challenge = self.active_challenges.get(challenge_id)
        
        if not challenge:
            logger.error(f"❌ Challenge not found: {challenge_id}")
            return
        
        if challenge_id in profile.completed_challenges:
            logger.warning(f"⚠️ Challenge already completed: {challenge_id}")
            return
        
        profile.completed_challenges.append(challenge_id)
        self.award_points(user_id, challenge.reward_points, f"Completed {challenge.name}")
        
        logger.info(f"✅ Challenge completed: {challenge.name} by {user_id}")
    
    def get_leaderboard(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get leaderboard"""
        return self.leaderboard[:limit]
    
    def _update_leaderboard(self):
        """Update leaderboard rankings"""
        sorted_profiles = sorted(
            self.user_profiles.values(),
            key=lambda p: (p.total_points, p.level),
            reverse=True
        )
        
        self.leaderboard = [
            {
                "rank": idx + 1,
                "user_id": profile.user_id,
                "points": profile.total_points,
                "level": profile.level,
                "achievements": len(profile.achievements)
            }
            for idx, profile in enumerate(sorted_profiles[:100])
        ]


class VoiceChallengeManager:
    """
    Manage voice creation challenges
    """
    
    def __init__(self):
        """Initialize challenge manager"""
        self.daily_challenges: List[Challenge] = []
        self.weekly_challenges: List[Challenge] = []
        
        logger.info("🎯 Voice Challenge Manager initialized")
    
    def get_daily_challenge(self) -> Optional[Challenge]:
        """Get today's daily challenge"""
        if self.daily_challenges:
            return self.daily_challenges[0]
        return None


class GamificationSystem:
    """
    Orchestrate entire gamification system
    """
    
    def __init__(self):
        """Initialize gamification system"""
        self.engine = VoiceGamificationEngine()
        self.challenge_manager = VoiceChallengeManager()
        
        logger.info("🎮 Gamification System initialized")
    
    def process_user_action(self, user_id: str, action: str, metadata: Dict[str, Any]):
        """Process user action for gamification"""
        # Award points based on action
        points_map = {
            "voice_created": 10,
            "voice_shared": 5,
            "collaboration_joined": 15,
            "quality_threshold_met": 20
        }
        
        points = points_map.get(action, 0)
        if points > 0:
            self.engine.award_points(user_id, points, action)
        
        # Check achievements
        self.engine.check_achievements(user_id, action, metadata)


class LeaderboardManager:
    """Manage leaderboards"""
    
    def __init__(self):
        logger.info("🏆 Leaderboard Manager initialized")


class RewardSystem:
    """Reward system for gamification"""
    
    def __init__(self):
        logger.info("🎁 Reward System initialized")


class ProgressTracking:
    """Track user progress"""
    
    def __init__(self):
        logger.info("📈 Progress Tracking initialized")


class MilestoneManager:
    """Manage user milestones"""
    
    def __init__(self):
        logger.info("🎯 Milestone Manager initialized")


class CompetitionEngine:
    """Engine for competitions"""
    
    def __init__(self):
        logger.info("🏁 Competition Engine initialized")


# Global instances
_gamification_engine: Optional[VoiceGamificationEngine] = None
_gamification_system: Optional[GamificationSystem] = None


def get_gamification_engine() -> VoiceGamificationEngine:
    """Get global gamification engine"""
    global _gamification_engine
    if _gamification_engine is None:
        _gamification_engine = VoiceGamificationEngine()
    return _gamification_engine


def get_gamification_system() -> GamificationSystem:
    """Get global gamification system"""
    global _gamification_system
    if _gamification_system is None:
        _gamification_system = GamificationSystem()
    return _gamification_system


# Auto-initialize
_gamification_engine = VoiceGamificationEngine()
_gamification_system = GamificationSystem()

logger.info("🎮 Voice Gamification Engine module initialized")
