"""MongoDB Achievement Manager
===========================

Advanced achievement system management for gamification in the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

logger = logging.getLogger(__name__)

class AchievementCategory(Enum):
    """Achievement categories."""
    CONTENT = "content"
    COLLABORATION = "collaboration"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    PLATFORM = "platform"
    SOCIAL = "social"
    LEARNING = "learning"
    MILESTONE = "milestone"

class AchievementType(Enum):
    """Achievement types."""
    CUMULATIVE = "cumulative"  # Based on total count
    STREAK = "streak"  # Based on consecutive actions
    THRESHOLD = "threshold"  # One-time milestone
    PERCENTAGE = "percentage"  # Based on percentage completion
    RARE = "rare"  # Special/rare achievements

@dataclass
class Achievement:
    """Achievement definition."""
    achievement_id: str
    name: str
    description: str
    category: AchievementCategory
    achievement_type: AchievementType
    points: int
    requirements: Dict[str, Any]
    prerequisites: List[str]
    hidden: bool = False
    limited_time: bool = False
    expires_at: Optional[datetime] = None
    icon_url: Optional[str] = None
    badge_color: str = "#FFD700"
    rarity: str = "common"  # common, uncommon, rare, epic, legendary

@dataclass
class UserAchievement:
    """User achievement record."""
    user_id: str
    achievement_id: str
    earned_at: datetime
    points_earned: int
    progress_data: Dict[str, Any]
    notified: bool = False

class AchievementManager:
    """Enterprise-grade achievement management system."""
    
    def __init__(self, client -> None: MongoClient, database_name -> None: str) -> None:
        """Initialize achievement manager."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for achievement management")
            
        self.client = client
        self.database = client[database_name]
        
        # Collections
        self.achievements_collection = self.database['achievements']
        self.user_achievements_collection = self.database['user_achievements']
        self.achievement_progress_collection = self.database['achievement_progress']
        
        # Cache for performance
        self._achievements_cache = {}
        self._cache_updated = None
        self.cache_ttl_seconds = 300  # 5 minutes
        
        # Initialize default achievements
        self._ensure_default_achievements()
    
    def _ensure_default_achievements(self) -> None:
        """Ensure default achievements exist."""
        default_achievements = [
            Achievement(
                achievement_id="first_content_upload",
                name="🎬 First Creator",
                description="Upload your first piece of content to the platform",
                category=AchievementCategory.CONTENT,
                achievement_type=AchievementType.THRESHOLD,
                points=100,
                requirements={"content_uploads": 1},
                prerequisites=[],
                icon_url="/icons/achievements/first_creator.png",
                badge_color="#4CAF50",
                rarity="common"
            ),
            Achievement(
                achievement_id="content_master_100",
                name="🎭 Content Master",
                description="Upload 100 pieces of content",
                category=AchievementCategory.CONTENT,
                achievement_type=AchievementType.CUMULATIVE,
                points=2000,
                requirements={"content_uploads": 100},
                prerequisites=["first_content_upload"],
                icon_url="/icons/achievements/content_master.png",
                badge_color="#FF9800",
                rarity="rare"
            ),
            Achievement(
                achievement_id="first_collaboration",
                name="🤝 Team Player",
                description="Complete your first collaboration project",
                category=AchievementCategory.COLLABORATION,
                achievement_type=AchievementType.THRESHOLD,
                points=250,
                requirements={"collaborations_completed": 1},
                prerequisites=[],
                icon_url="/icons/achievements/team_player.png",
                badge_color="#2196F3",
                rarity="common"
            ),
            Achievement(
                achievement_id="revenue_first_dollar",
                name="💰 First Earnings",
                description="Earn your first dollar on the platform",
                category=AchievementCategory.REVENUE,
                achievement_type=AchievementType.THRESHOLD,
                points=500,
                requirements={"total_revenue": 1.0},
                prerequisites=[],
                icon_url="/icons/achievements/first_earnings.png",
                badge_color="#4CAF50",
                rarity="uncommon"
            ),
            Achievement(
                achievement_id="engagement_viral",
                name="🔥 Viral Content",
                description="Create content that reaches 100K+ views",
                category=AchievementCategory.ENGAGEMENT,
                achievement_type=AchievementType.THRESHOLD,
                points=1500,
                requirements={"max_content_views": 100000},
                prerequisites=["first_content_upload"],
                icon_url="/icons/achievements/viral_content.png",
                badge_color="#E91E63",
                rarity="epic"
            ),
            Achievement(
                achievement_id="platform_multi_master",
                name="🌍 Multi-Platform Master",
                description="Successfully sync content to 5+ platforms",
                category=AchievementCategory.PLATFORM,
                achievement_type=AchievementType.THRESHOLD,
                points=1000,
                requirements={"platforms_synced": 5},
                prerequisites=["first_content_upload"],
                icon_url="/icons/achievements/multi_platform.png",
                badge_color="#9C27B0",
                rarity="rare"
            ),
            Achievement(
                achievement_id="learning_ai_expert",
                name="🤖 AI Expert",
                description="Use AI features 50+ times",
                category=AchievementCategory.LEARNING,
                achievement_type=AchievementType.CUMULATIVE,
                points=750,
                requirements={"ai_features_used": 50},
                prerequisites=[],
                icon_url="/icons/achievements/ai_expert.png",
                badge_color="#FF5722",
                rarity="uncommon"
            ),
            Achievement(
                achievement_id="social_influencer",
                name="👥 Social Influencer",
                description="Gain 10,000+ followers across all platforms",
                category=AchievementCategory.SOCIAL,
                achievement_type=AchievementType.CUMULATIVE,
                points=2500,
                requirements={"total_followers": 10000},
                prerequisites=["platform_multi_master"],
                icon_url="/icons/achievements/social_influencer.png",
                badge_color="#673AB7",
                rarity="epic"
            ),
            Achievement(
                achievement_id="milestone_year_one",
                name="🎂 One Year Strong",
                description="Active member for one full year",
                category=AchievementCategory.MILESTONE,
                achievement_type=AchievementType.THRESHOLD,
                points=1000,
                requirements={"days_active": 365},
                prerequisites=[],
                icon_url="/icons/achievements/year_one.png",
                badge_color="#795548",
                rarity="rare"
            ),
            Achievement(
                achievement_id="streak_daily_creator",
                name="📅 Daily Creator",
                description="Upload content for 30 consecutive days",
                category=AchievementCategory.CONTENT,
                achievement_type=AchievementType.STREAK,
                points=800,
                requirements={"daily_upload_streak": 30},
                prerequisites=["first_content_upload"],
                icon_url="/icons/achievements/daily_creator.png",
                badge_color="#FFC107",
                rarity="uncommon"
            )
        ]
        
        # Insert achievements if they don't exist
        for achievement in default_achievements:
            existing = self.achievements_collection.find_one(
                {"achievement_id": achievement.achievement_id}
            )
            
            if not existing:
                self.achievements_collection.insert_one(asdict(achievement))
                logger.info(f"Created default achievement: {achievement.name}")
    
    def create_achievement(self, achievement: Achievement) -> bool:
        """Create a new achievement."""
        try:
            # Check if achievement already exists
            existing = self.achievements_collection.find_one(
                {"achievement_id": achievement.achievement_id}
            )
            
            if existing:
                logger.warning(f"Achievement already exists: {achievement.achievement_id}")
                return False
            
            # Insert achievement
            result = self.achievements_collection.insert_one(asdict(achievement))
            
            if result.inserted_id:
                # Clear cache
                self._achievements_cache = {}
                logger.info(f"Created achievement: {achievement.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to create achievement: {e}")
            return False
    
    def get_achievements(self, category: Optional[AchievementCategory] = None) -> List[Achievement]:
        """Get all achievements, optionally filtered by category."""
        try:
            # Use cache if available and fresh
            cache_key = f"all_{category.value if category else 'all'}"
            
            if (self._cache_updated and 
                datetime.now() - self._cache_updated < timedelta(seconds=self.cache_ttl_seconds) and
                cache_key in self._achievements_cache):
                return self._achievements_cache[cache_key]
            
            # Build query
            query = {}
            if category:
                query["category"] = category.value
            
            # Fetch from database
            achievements_data = list(self.achievements_collection.find(query))
            
            # Convert to Achievement objects
            achievements = []
            for data in achievements_data:
                try:
                    # Handle enum conversion
                    data["category"] = AchievementCategory(data["category"])
                    data["achievement_type"] = AchievementType(data["achievement_type"])
                    
                    # Remove MongoDB _id field
                    data.pop("_id", None)
                    
                    achievement = Achievement(**data)
                    achievements.append(achievement)
                    
                except Exception as e:
                    logger.error(f"Failed to parse achievement {data.get('achievement_id', 'unknown')}: {e}")
            
            # Cache results
            self._achievements_cache[cache_key] = achievements
            self._cache_updated = datetime.now()
            
            return achievements
            
        except Exception as e:
            logger.error(f"Failed to get achievements: {e}")
            return []
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get specific achievement by ID."""
        try:
            achievement_data = self.achievements_collection.find_one(
                {"achievement_id": achievement_id}
            )
            
            if not achievement_data:
                return None
            
            # Handle enum conversion
            achievement_data["category"] = AchievementCategory(achievement_data["category"])
            achievement_data["achievement_type"] = AchievementType(achievement_data["achievement_type"])
            
            # Remove MongoDB _id field
            achievement_data.pop("_id", None)
            
            return Achievement(**achievement_data)
            
        except Exception as e:
            logger.error(f"Failed to get achievement {achievement_id}: {e}")
            return None
    
    def check_and_award_achievements(self, user_id: str, user_stats: Dict[str, Any]) -> List[UserAchievement]:
        """Check user stats against achievements and award new ones."""
        try:
            newly_earned = []
            
            # Get all achievements
            all_achievements = self.get_achievements()
            
            # Get user's current achievements
            user_achievements = set(
                ach["achievement_id"] 
                for ach in self.user_achievements_collection.find({"user_id": user_id})
            )
            
            for achievement in all_achievements:
                # Skip if user already has this achievement
                if achievement.achievement_id in user_achievements:
                    continue
                
                # Check prerequisites
                if not self._check_prerequisites(user_id, achievement.prerequisites):
                    continue
                
                # Check if achievement requirements are met
                if self._check_requirements(achievement, user_stats):
                    # Award achievement
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.achievement_id,
                        earned_at=datetime.now(),
                        points_earned=achievement.points,
                        progress_data=user_stats.copy()
                    )
                    
                    # Insert into database
                    self.user_achievements_collection.insert_one(asdict(user_achievement))
                    
                    newly_earned.append(user_achievement)
                    user_achievements.add(achievement.achievement_id)
                    
                    logger.info(f"Awarded achievement '{achievement.name}' to user {user_id}")
            
            return newly_earned
            
        except Exception as e:
            logger.error(f"Failed to check achievements for user {user_id}: {e}")
            return []
    
    def _check_prerequisites(self, user_id: str, prerequisites: List[str]) -> bool:
        """Check if user meets achievement prerequisites."""
        if not prerequisites:
            return True
        
        user_achievements = set(
            ach["achievement_id"] 
            for ach in self.user_achievements_collection.find({"user_id": user_id})
        )
        
        return all(prereq in user_achievements for prereq in prerequisites)
    
    def _check_requirements(self, achievement: Achievement, user_stats: Dict[str, Any]) -> bool:
        """Check if user stats meet achievement requirements."""
        try:
            for requirement_key, required_value in achievement.requirements.items():
                user_value = user_stats.get(requirement_key, 0)
                
                if achievement.achievement_type == AchievementType.THRESHOLD:
                    if user_value < required_value:
                        return False
                elif achievement.achievement_type == AchievementType.CUMULATIVE:
                    if user_value < required_value:
                        return False
                elif achievement.achievement_type == AchievementType.STREAK:
                    # For streaks, check current streak value
                    if user_value < required_value:
                        return False
                elif achievement.achievement_type == AchievementType.PERCENTAGE:
                    # For percentage-based achievements
                    if user_value < required_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking requirements for {achievement.achievement_id}: {e}")
            return False
    
    def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all achievements earned by a user."""
        try:
            user_achievements = list(
                self.user_achievements_collection.find({"user_id": user_id})
            )
            
            # Enrich with achievement details
            enriched_achievements = []
            for user_ach in user_achievements:
                achievement = self.get_achievement(user_ach["achievement_id"])
                if achievement:
                    enriched = {
                        "achievement": asdict(achievement),
                        "earned_at": user_ach["earned_at"],
                        "points_earned": user_ach["points_earned"],
                        "progress_data": user_ach.get("progress_data", {}),
                        "notified": user_ach.get("notified", False)
                    }
                    enriched_achievements.append(enriched)
            
            return enriched_achievements
            
        except Exception as e:
            logger.error(f"Failed to get user achievements for {user_id}: {e}")
            return []
    
    def get_achievement_progress(self, user_id: str, achievement_id: str, current_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Get user's progress towards a specific achievement."""
        try:
            achievement = self.get_achievement(achievement_id)
            if not achievement:
                return {}
            
            # Check if already earned
            existing = self.user_achievements_collection.find_one({
                "user_id": user_id,
                "achievement_id": achievement_id
            })
            
            if existing:
                return {
                    "achievement_id": achievement_id,
                    "completed": True,
                    "earned_at": existing["earned_at"],
                    "progress_percentage": 100.0
                }
            
            # Calculate progress
            progress_data = {}
            total_progress = 0
            requirement_count = len(achievement.requirements)
            
            for requirement_key, required_value in achievement.requirements.items():
                user_value = current_stats.get(requirement_key, 0)
                progress_percentage = min(100, (user_value / required_value) * 100)
                
                progress_data[requirement_key] = {
                    "current": user_value,
                    "required": required_value,
                    "percentage": progress_percentage
                }
                
                total_progress += progress_percentage
            
            overall_progress = total_progress / requirement_count if requirement_count > 0 else 0
            
            return {
                "achievement_id": achievement_id,
                "completed": False,
                "progress_percentage": overall_progress,
                "requirements_progress": progress_data,
                "can_earn": self._check_prerequisites(user_id, achievement.prerequisites)
            }
            
        except Exception as e:
            logger.error(f"Failed to get achievement progress: {e}")
            return {}
    
    def get_user_achievement_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive achievement summary for user."""
        try:
            # Get earned achievements
            earned_achievements = self.get_user_achievements(user_id)
            
            # Calculate statistics
            total_points = sum(ach["points_earned"] for ach in earned_achievements)
            total_achievements = len(earned_achievements)
            
            # Group by category
            category_stats = {}
            for ach in earned_achievements:
                category = ach["achievement"]["category"]
                if category not in category_stats:
                    category_stats[category] = {"count": 0, "points": 0}
                
                category_stats[category]["count"] += 1
                category_stats[category]["points"] += ach["points_earned"]
            
            # Group by rarity
            rarity_stats = {}
            for ach in earned_achievements:
                rarity = ach["achievement"]["rarity"]
                rarity_stats[rarity] = rarity_stats.get(rarity, 0) + 1
            
            return {
                "user_id": user_id,
                "total_achievements": total_achievements,
                "total_points": total_points,
                "category_breakdown": category_stats,
                "rarity_breakdown": rarity_stats,
                "recent_achievements": sorted(
                    earned_achievements,
                    key=lambda x: x["earned_at"],
                    reverse=True
                )[:5]
            }
            
        except Exception as e:
            logger.error(f"Failed to get achievement summary for {user_id}: {e}")
            return {}
    
    def update_achievement(self, achievement_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing achievement."""
        try:
            result = self.achievements_collection.update_one(
                {"achievement_id": achievement_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                # Clear cache
                self._achievements_cache = {}
                logger.info(f"Updated achievement: {achievement_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update achievement {achievement_id}: {e}")
            return False
    
    def delete_achievement(self, achievement_id: str) -> bool:
        """Delete an achievement (use with caution)."""
        try:
            # First remove all user achievements for this achievement
            self.user_achievements_collection.delete_many(
                {"achievement_id": achievement_id}
            )
            
            # Then remove the achievement itself
            result = self.achievements_collection.delete_one(
                {"achievement_id": achievement_id}
            )
            
            if result.deleted_count > 0:
                # Clear cache
                self._achievements_cache = {}
                logger.info(f"Deleted achievement: {achievement_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete achievement {achievement_id}: {e}")
            return False

# Export the main class
__all__ = ['AchievementManager', 'Achievement', 'UserAchievement', 'AchievementCategory', 'AchievementType']