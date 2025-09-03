"""Achievement Engine - Moteur achievements
==========================================

Core achievement processing engine that handles achievement tracking,
validation, and unlocking for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum

# Import existing achievement types from the main gamification module
try:
    from ...gamification.achievement_system import (
        Achievement,
        AchievementTier,
        AchievementCategory,
        AchievementStatus,
        UserAchievementProgress,
        AchievementRequirement,
        AchievementReward
    )
except ImportError:
    # Fallback definitions if main module is not available
    from enum import Enum
    
    class AchievementTier(str, Enum):
        BRONZE = "bronze"
        SILVER = "silver"
        GOLD = "gold"
        PLATINUM = "platinum"
        DIAMOND = "diamond"


class AchievementEngine:
    """
    Core achievement processing engine providing sophisticated achievement
    tracking, validation, and unlocking mechanisms.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the achievement engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.achievements: Dict[str, Achievement] = {}
        self.user_progress: Dict[str, Dict[str, UserAchievementProgress]] = {}
        
        # Initialize achievement templates
        self._initialize_achievement_templates()
        
        self.logger.info("AchievementEngine initialized")
    
    def _initialize_achievement_templates(self):
        """Initialize default achievement templates."""
        try:
            # Content creation achievements
            self.achievements["first_upload"] = self._create_achievement(
                "first_upload",
                "First Steps",
                "Upload your first piece of content",
                AchievementTier.BRONZE,
                {"uploads": 1},
                {"xp": 100, "badge": "newcomer"}
            )
            
            self.achievements["prolific_creator"] = self._create_achievement(
                "prolific_creator",
                "Prolific Creator",
                "Upload 100 pieces of content",
                AchievementTier.SILVER,
                {"uploads": 100},
                {"xp": 1000, "badge": "prolific", "credits": 500}
            )
            
            self.achievements["viral_master"] = self._create_achievement(
                "viral_master",
                "Viral Master",
                "Reach 1M+ views on content",
                AchievementTier.GOLD,
                {"max_views": 1000000},
                {"xp": 2500, "badge": "viral", "credits": 1000}
            )
            
            # Collaboration achievements
            self.achievements["collaborator"] = self._create_achievement(
                "collaborator",
                "Team Player",
                "Complete 5 successful collaborations",
                AchievementTier.SILVER,
                {"collaborations": 5},
                {"xp": 750, "badge": "collaborator"}
            )
            
            # Engagement achievements
            self.achievements["influencer"] = self._create_achievement(
                "influencer",
                "Rising Influencer",
                "Gain 10,000 followers",
                AchievementTier.GOLD,
                {"followers": 10000},
                {"xp": 2000, "badge": "influencer", "revenue_boost": 0.1}
            )
            
            self.logger.info(f"Initialized {len(self.achievements)} achievement templates")
            
        except Exception as e:
            self.logger.error(f"Error initializing achievement templates: {e}")
    
    def _create_achievement(
        self,
        achievement_id: str,
        title: str,
        description: str,
        tier: AchievementTier,
        requirements: Dict[str, Any],
        rewards: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Helper method to create achievement objects."""
        # This is a simplified version - in reality would use the full Achievement class
        return {
            "id": achievement_id,
            "title": title,
            "description": description,
            "tier": tier,
            "requirements": requirements,
            "rewards": rewards,
            "created_at": datetime.now(timezone.utc)
        }
    
    async def track_user_metric(
        self,
        user_id: str,
        metric_key: str,
        value: Union[int, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Track a metric for a user and check for achievement unlocks."""
        unlocked_achievements = []
        
        try:
            # Update user metrics (simplified - would use proper storage)
            if user_id not in self.user_progress:
                self.user_progress[user_id] = {}
            
            # Check each achievement for potential unlock
            for achievement_id, achievement in self.achievements.items():
                if achievement_id not in self.user_progress[user_id]:
                    # Check if user meets requirements for this achievement
                    if await self._check_achievement_requirements(user_id, achievement, metric_key, value):
                        # Unlock achievement
                        await self._unlock_achievement(user_id, achievement_id)
                        unlocked_achievements.append(achievement_id)
            
            self.logger.info(f"Tracked metric {metric_key}={value} for user {user_id}, unlocked: {unlocked_achievements}")
            return unlocked_achievements
            
        except Exception as e:
            self.logger.error(f"Error tracking user metric: {e}")
            return []
    
    async def _check_achievement_requirements(
        self,
        user_id: str,
        achievement: Dict[str, Any],
        metric_key: str,
        value: Union[int, float]
    ) -> bool:
        """Check if achievement requirements are met."""
        try:
            requirements = achievement.get("requirements", {})
            
            # Simple requirement checking (simplified)
            if metric_key in requirements:
                required_value = requirements[metric_key]
                if value >= required_value:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking achievement requirements: {e}")
            return False
    
    async def _unlock_achievement(self, user_id: str, achievement_id: str):
        """Unlock an achievement for a user."""
        try:
            achievement = self.achievements.get(achievement_id)
            if not achievement:
                return
            
            # Create progress record
            progress = {
                "user_id": user_id,
                "achievement_id": achievement_id,
                "unlocked_at": datetime.now(timezone.utc),
                "status": "unlocked"
            }
            
            self.user_progress[user_id][achievement_id] = progress
            
            # Award rewards (simplified)
            rewards = achievement.get("rewards", {})
            await self._award_achievement_rewards(user_id, rewards)
            
            self.logger.info(f"🏆 Achievement unlocked: {achievement['title']} for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error unlocking achievement: {e}")
    
    async def _award_achievement_rewards(self, user_id: str, rewards: Dict[str, Any]):
        """Award rewards for achievement unlock."""
        try:
            for reward_type, reward_value in rewards.items():
                if reward_type == "xp":
                    self.logger.info(f"💎 Awarded {reward_value} XP to {user_id}")
                elif reward_type == "credits":
                    self.logger.info(f"💰 Awarded {reward_value} credits to {user_id}")
                elif reward_type == "badge":
                    self.logger.info(f"🎖️ Awarded {reward_value} badge to {user_id}")
                elif reward_type == "revenue_boost":
                    self.logger.info(f"📈 Applied {reward_value*100}% revenue boost to {user_id}")
                
        except Exception as e:
            self.logger.error(f"Error awarding achievement rewards: {e}")
    
    async def process_action(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process a user action and check for achievement unlocks."""
        results = []
        
        try:
            # Map action types to metrics
            metric_mapping = {
                "content_upload": "uploads",
                "content_view": "views",
                "collaboration_complete": "collaborations",
                "follower_gain": "followers"
            }
            
            metric_key = metric_mapping.get(action_type)
            if metric_key:
                # Extract value from action data
                value = action_data.get("count", 1)
                if action_type == "content_view":
                    value = action_data.get("view_count", 0)
                elif action_type == "follower_gain":
                    value = action_data.get("total_followers", 0)
                
                # Track the metric
                unlocked = await self.track_user_metric(user_id, metric_key, value)
                
                # Format results
                for achievement_id in unlocked:
                    achievement = self.achievements.get(achievement_id)
                    if achievement:
                        results.append({
                            "type": "achievement_unlocked",
                            "achievement_id": achievement_id,
                            "title": achievement["title"],
                            "description": achievement["description"],
                            "tier": achievement["tier"],
                            "rewards": achievement["rewards"]
                        })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing action for achievements: {e}")
            return []
    
    async def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user's achievement summary."""
        try:
            user_achievements = self.user_progress.get(user_id, {})
            
            summary = {
                "total_achievements": len(user_achievements),
                "unlocked_achievements": len([a for a in user_achievements.values() if a.get("status") == "unlocked"]),
                "achievements_by_tier": {},
                "recent_unlocks": [],
                "progress": {}
            }
            
            # Count by tier
            for achievement_id, progress in user_achievements.items():
                achievement = self.achievements.get(achievement_id)
                if achievement:
                    tier = achievement["tier"]
                    if tier not in summary["achievements_by_tier"]:
                        summary["achievements_by_tier"][tier] = 0
                    summary["achievements_by_tier"][tier] += 1
            
            # Recent unlocks (last 10)
            recent = sorted(
                [a for a in user_achievements.values() if a.get("unlocked_at")],
                key=lambda x: x["unlocked_at"],
                reverse=True
            )[:10]
            
            summary["recent_unlocks"] = [
                {
                    "achievement_id": a["achievement_id"],
                    "unlocked_at": a["unlocked_at"].isoformat(),
                    "title": self.achievements.get(a["achievement_id"], {}).get("title", "")
                }
                for a in recent
            ]
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting user achievement summary: {e}")
            return {}
    
    async def get_available_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of available achievements for a user."""
        try:
            user_achievements = self.user_progress.get(user_id, {})
            available = []
            
            for achievement_id, achievement in self.achievements.items():
                if achievement_id not in user_achievements:
                    available.append({
                        "id": achievement_id,
                        "title": achievement["title"],
                        "description": achievement["description"],
                        "tier": achievement["tier"],
                        "requirements": achievement["requirements"],
                        "rewards": achievement["rewards"]
                    })
            
            return available
            
        except Exception as e:
            self.logger.error(f"Error getting available achievements: {e}")
            return []


# Global instance
_achievement_engine = None

def get_achievement_engine(database_connection=None, cache_client=None) -> AchievementEngine:
    """Get the global achievement engine instance."""
    global _achievement_engine
    if _achievement_engine is None:
        _achievement_engine = AchievementEngine(database_connection, cache_client)
    return _achievement_engine