"""Gamification System
Creator challenges, achievements, and engagement gamification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ChallengeType(Enum):
    """Challenge types"""    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    COMMUNITY = "community"


class AchievementTier(Enum):
    """Achievement tiers"""    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class Challenge:
    """Challenge definition"""    id: str
    title: str
    description: str
    challenge_type: ChallengeType
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    participants: List[str]
    is_active: bool = True


@dataclass
class Achievement:
    """Achievement definition"""    id: str
    title: str
    description: str
    tier: AchievementTier
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    unlock_conditions: List[str]
    rarity: float  # 0.0 to 1.0


@dataclass
class UserProgress:
    """User progress tracking"""    user_id: str
    level: int
    experience_points: int
    achievements_unlocked: List[str]
    challenges_completed: List[str]
    current_streak: int
    total_rewards_earned: float
    rank: Optional[int] = None


class GamificationSystem:
    """Creator gamification and engagement system"""    
    def __init__(self):
        self.challenges = {}
        self.achievements = {}
        self.user_progress = {}
        self.leaderboards = {}
        
        # Initialize default achievements and challenges
        self._initialize_default_content()
        
    async def create_challenge(
        self,
        title: str,
        description: str,
        challenge_type: ChallengeType,
        requirements: Dict[str, Any],
        rewards: Dict[str, Any],
        duration_days: int = 7
    ) -> str:
        """Create a new challenge"""        try:
            challenge_id = f"challenge_{int(datetime.now().timestamp())}"
            
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_days)
            
            challenge = Challenge(
                id=challenge_id,
                title=title,
                description=description,
                challenge_type=challenge_type,
                requirements=requirements,
                rewards=rewards,
                start_date=start_date,
                end_date=end_date,
                participants=[]
            )
            
            self.challenges[challenge_id] = challenge
            
            logger.info(f"Challenge created: {title} ({challenge_id})")
            return challenge_id
            
        except Exception as e:
            logger.error(f"Error creating challenge: {str(e)}")
            raise
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Join a challenge"""        try:
            challenge = self.challenges.get(challenge_id)
            if not challenge or not challenge.is_active:
                return False
                
            if datetime.now() > challenge.end_date:
                return False
                
            if user_id not in challenge.participants:
                challenge.participants.append(user_id)
                
                # Initialize user progress if needed
                if user_id not in self.user_progress:
                    self.user_progress[user_id] = UserProgress(
                        user_id=user_id,
                        level=1,
                        experience_points=0,
                        achievements_unlocked=[],
                        challenges_completed=[],
                        current_streak=0,
                        total_rewards_earned=0.0
                    )
                
                logger.info(f"User {user_id} joined challenge {challenge_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error joining challenge: {str(e)}")
            return False
    
    async def check_challenge_progress(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> List[str]:
        """Check and update challenge progress for user"""        try:
            completed_challenges = []
            user_progress = self.user_progress.get(user_id)
            
            if not user_progress:
                return completed_challenges
            
            for challenge_id, challenge in self.challenges.items():
                if (user_id in challenge.participants and 
                    challenge.is_active and
                    challenge_id not in user_progress.challenges_completed):
                    
                    if self._check_challenge_completion(challenge, activity_data):
                        # Challenge completed
                        user_progress.challenges_completed.append(challenge_id)
                        completed_challenges.append(challenge_id)
                        
                        # Award rewards
                        await self._award_challenge_rewards(user_id, challenge.rewards)
                        
                        logger.info(f"Challenge completed: {user_id} - {challenge_id}")
            
            return completed_challenges
            
        except Exception as e:
            logger.error(f"Error checking challenge progress: {str(e)}")
            return []
    
    async def unlock_achievement(
        self,
        user_id: str,
        user_stats: Dict[str, Any]
    ) -> List[str]:
        """Check and unlock achievements for user"""        try:
            unlocked_achievements = []
            user_progress = self.user_progress.get(user_id)
            
            if not user_progress:
                return unlocked_achievements
            
            for achievement_id, achievement in self.achievements.items():
                if achievement_id not in user_progress.achievements_unlocked:
                    if self._check_achievement_requirements(achievement, user_stats, user_progress):
                        # Achievement unlocked
                        user_progress.achievements_unlocked.append(achievement_id)
                        unlocked_achievements.append(achievement_id)
                        
                        # Award rewards
                        await self._award_achievement_rewards(user_id, achievement.rewards)
                        
                        logger.info(f"Achievement unlocked: {user_id} - {achievement_id}")
            
            return unlocked_achievements
            
        except Exception as e:
            logger.error(f"Error unlocking achievements: {str(e)}")
            return []
    
    async def update_leaderboards(self):
        """Update global and category leaderboards"""        try:
            # Global leaderboard by experience points
            global_ranking = sorted(
                self.user_progress.values(),
                key=lambda x: x.experience_points,
                reverse=True
            )
            
            self.leaderboards["global"] = [
                {
                    "rank": i + 1,
                    "user_id": user.user_id,
                    "experience_points": user.experience_points,
                    "level": user.level,
                    "achievements": len(user.achievements_unlocked)
                }
                for i, user in enumerate(global_ranking[:100])  # Top 100
            ]
            
            # Update user ranks
            for i, user in enumerate(global_ranking):
                user.rank = i + 1
            
            # Weekly challenge leaderboard
            weekly_participants = {}
            for challenge in self.challenges.values():
                if challenge.challenge_type == ChallengeType.WEEKLY:
                    for participant in challenge.participants:
                        if participant not in weekly_participants:
                            weekly_participants[participant] = 0
                        if challenge.id in self.user_progress.get(participant, UserProgress("", 0, 0, [], [], 0, 0.0)).challenges_completed:
                            weekly_participants[participant] += 1
            
            weekly_ranking = sorted(
                weekly_participants.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            self.leaderboards["weekly_challenges"] = [
                {"rank": i + 1, "user_id": user_id, "challenges_completed": count}
                for i, (user_id, count) in enumerate(weekly_ranking[:50])
            ]
            
            logger.info("Leaderboards updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating leaderboards: {str(e)}")
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get gamification dashboard for user"""        try:
            user_progress = self.user_progress.get(user_id)
            if not user_progress:
                return {"error": "User not found"}
            
            # Get active challenges
            active_challenges = [
                {
                    "id": challenge.id,
                    "title": challenge.title,
                    "description": challenge.description,
                    "end_date": challenge.end_date.isoformat(),
                    "is_participating": user_id in challenge.participants,
                    "is_completed": challenge.id in user_progress.challenges_completed
                }
                for challenge in self.challenges.values()
                if challenge.is_active and datetime.now() <= challenge.end_date
            ]
            
            # Get recent achievements
            recent_achievements = [
                {
                    "id": achievement_id,
                    "title": self.achievements[achievement_id].title,
                    "tier": self.achievements[achievement_id].tier.value,
                    "unlocked_recently": True
                }
                for achievement_id in user_progress.achievements_unlocked[-5:]  # Last 5
                if achievement_id in self.achievements
            ]
            
            # Calculate progress to next level
            current_level = user_progress.level
            next_level_xp = current_level * 1000  # Simple XP formula
            progress_to_next = (user_progress.experience_points % 1000) / 1000
            
            dashboard = {
                "user_id": user_id,
                "level": user_progress.level,
                "experience_points": user_progress.experience_points,
                "progress_to_next_level": progress_to_next,
                "global_rank": user_progress.rank,
                "current_streak": user_progress.current_streak,
                "total_achievements": len(user_progress.achievements_unlocked),
                "total_challenges_completed": len(user_progress.challenges_completed),
                "total_rewards_earned": user_progress.total_rewards_earned,
                "active_challenges": active_challenges,
                "recent_achievements": recent_achievements,
                "available_challenges": len([c for c in self.challenges.values() if c.is_active and user_id not in c.participants])
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting user dashboard: {str(e)}")
            return {"error": str(e)}
    
    def _initialize_default_content(self):
        """Initialize default achievements and challenges"""        try:
            # Default achievements
            default_achievements = [
                {
                    "id": "first_upload",
                    "title": "First Steps",
                    "description": "Upload your first content",
                    "tier": AchievementTier.BRONZE,
                    "requirements": {"uploads": 1},
                    "rewards": {"xp": 100, "badge": "newcomer"}
                },
                {
                    "id": "viral_content",
                    "title": "Viral Creator",
                    "description": "Create content with 10K+ views",
                    "tier": AchievementTier.GOLD,
                    "requirements": {"max_views": 10000},
                    "rewards": {"xp": 1000, "bonus_revenue": 50}
                },
                {
                    "id": "collaboration_master",
                    "title": "Collaboration Master",
                    "description": "Complete 10 successful collaborations",
                    "tier": AchievementTier.PLATINUM,
                    "requirements": {"collaborations_completed": 10},
                    "rewards": {"xp": 2000, "special_badge": "collaborator"}
                }
            ]
            
            for ach_data in default_achievements:
                achievement = Achievement(
                    id=ach_data["id"],
                    title=ach_data["title"],
                    description=ach_data["description"],
                    tier=ach_data["tier"],
                    requirements=ach_data["requirements"],
                    rewards=ach_data["rewards"],
                    unlock_conditions=[],
                    rarity=0.5
                )
                self.achievements[ach_data["id"]] = achievement
            
            # Default challenges
            weekly_challenge = Challenge(
                id="weekly_upload",
                title="Weekly Creator",
                description="Upload 3 pieces of content this week",
                challenge_type=ChallengeType.WEEKLY,
                requirements={"uploads": 3, "timeframe": "week"},
                rewards={"xp": 500, "streak_bonus": True},
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=7),
                participants=[]
            )
            self.challenges["weekly_upload"] = weekly_challenge
            
        except Exception as e:
            logger.error(f"Error initializing default content: {str(e)}")
    
    def _check_challenge_completion(
        self,
        challenge: Challenge,
        activity_data: Dict[str, Any]
    ) -> bool:
        """Check if challenge requirements are met"""        try:
            requirements = challenge.requirements
            
            for req_key, req_value in requirements.items():
                if req_key == "uploads":
                    if activity_data.get("uploads_count", 0) < req_value:
                        return False
                elif req_key == "views":
                    if activity_data.get("total_views", 0) < req_value:
                        return False
                elif req_key == "collaborations":
                    if activity_data.get("collaborations_count", 0) < req_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking challenge completion: {str(e)}")
            return False
    
    def _check_achievement_requirements(
        self,
        achievement: Achievement,
        user_stats: Dict[str, Any],
        user_progress: UserProgress
    ) -> bool:
        """Check if achievement requirements are met"""        try:
            requirements = achievement.requirements
            
            for req_key, req_value in requirements.items():
                if req_key == "uploads":
                    if user_stats.get("total_uploads", 0) < req_value:
                        return False
                elif req_key == "max_views":
                    if user_stats.get("max_content_views", 0) < req_value:
                        return False
                elif req_key == "collaborations_completed":
                    if len(user_progress.challenges_completed) < req_value:
                        return False
                elif req_key == "level":
                    if user_progress.level < req_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking achievement requirements: {str(e)}")
            return False
    
    async def _award_challenge_rewards(
        self,
        user_id: str,
        rewards: Dict[str, Any]
    ):
        """Award challenge completion rewards"""        try:
            user_progress = self.user_progress[user_id]
            
            if "xp" in rewards:
                user_progress.experience_points += rewards["xp"]
                
                # Check for level up
                new_level = (user_progress.experience_points // 1000) + 1
                if new_level > user_progress.level:
                    user_progress.level = new_level
                    logger.info(f"User {user_id} leveled up to {new_level}")
            
            if "streak_bonus" in rewards and rewards["streak_bonus"]:
                user_progress.current_streak += 1
            
            if "bonus_revenue" in rewards:
                user_progress.total_rewards_earned += rewards["bonus_revenue"]
            
        except Exception as e:
            logger.error(f"Error awarding challenge rewards: {str(e)}")
    
    async def _award_achievement_rewards(
        self,
        user_id: str,
        rewards: Dict[str, Any]
    ):
        """Award achievement unlock rewards"""        try:
            user_progress = self.user_progress[user_id]
            
            if "xp" in rewards:
                user_progress.experience_points += rewards["xp"]
                
                # Check for level up
                new_level = (user_progress.experience_points // 1000) + 1
                if new_level > user_progress.level:
                    user_progress.level = new_level
                    logger.info(f"User {user_id} leveled up to {new_level}")
            
            if "bonus_revenue" in rewards:
                user_progress.total_rewards_earned += rewards["bonus_revenue"]
            
        except Exception as e:
            logger.error(f"Error awarding achievement rewards: {str(e)}")