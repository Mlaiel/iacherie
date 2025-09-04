"""Gaming Achievements - Gaming-Specific Achievement System
==========================================================

Specialized gaming achievement system providing immersive game-like achievements,
progress tracking, and competitive achievements for the influencer tycoon
gaming experience with RPG-style progression mechanics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Gaming Actions → Achievement Tracking → Progress Calculation → Unlock Verification →
Gaming Rewards → Badge Assignment → Leaderboard Updates → Player Progression
"""

import logging
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid
import asyncio
import math

logger = logging.getLogger(__name__)


class GamingAchievementCategory(str, Enum):
    """Categories of gaming achievements."""
    TYCOON_MASTERY = "tycoon_mastery"
    WEALTH_BUILDER = "wealth_builder"
    ASSET_COLLECTOR = "asset_collector"
    EFFICIENCY_EXPERT = "efficiency_expert"
    COMPETITIVE_CHAMPION = "competitive_champion"
    MILESTONE_HUNTER = "milestone_hunter"
    SPEED_RUNNER = "speed_runner"
    STRATEGIST = "strategist"
    COLLECTOR = "collector"
    SOCIAL_GAMER = "social_gamer"
    SEASONAL_CHAMPION = "seasonal_champion"
    RARE_ACHIEVER = "rare_achiever"


class GamingAchievementDifficulty(str, Enum):
    """Difficulty levels for gaming achievements."""
    TRIVIAL = "trivial"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXTREME = "extreme"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"
    IMPOSSIBLE = "impossible"


class GamingAchievementType(str, Enum):
    """Types of gaming achievements."""
    MILESTONE = "milestone"
    CUMULATIVE = "cumulative"
    STREAK = "streak"
    SPEED = "speed"
    EFFICIENCY = "efficiency"
    COLLECTION = "collection"
    COMPETITIVE = "competitive"
    HIDDEN = "hidden"
    SEASONAL = "seasonal"
    CHALLENGE = "challenge"


class GamingAchievementStatus(str, Enum):
    """Status of gaming achievements."""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLAIMED = "claimed"
    EXPIRED = "expired"


@dataclass
class GamingAchievementRequirement:
    """Requirement for a gaming achievement."""
    requirement_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_key: str = ""
    required_value: Union[int, float, Decimal] = 0
    comparison_type: str = "greater_equal"  # greater_equal, equal, less_equal, between
    value_range: Optional[tuple] = None
    time_window_hours: Optional[int] = None
    description: str = ""
    weight: float = 1.0


@dataclass
class GamingAchievementReward:
    """Reward for completing a gaming achievement."""
    reward_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    currency_type: str = "gaming_gems"
    amount: Decimal = Decimal('100')
    bonus_multiplier: float = 1.0
    special_items: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    unlocks: List[str] = field(default_factory=list)


@dataclass
class GamingAchievement:
    """Represents a gaming achievement."""
    achievement_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: GamingAchievementCategory = GamingAchievementCategory.TYCOON_MASTERY
    difficulty: GamingAchievementDifficulty = GamingAchievementDifficulty.EASY
    achievement_type: GamingAchievementType = GamingAchievementType.MILESTONE
    requirements: List[GamingAchievementRequirement] = field(default_factory=list)
    rewards: GamingAchievementReward = field(default_factory=GamingAchievementReward)
    prerequisites: List[str] = field(default_factory=list)
    icon_url: Optional[str] = None
    badge_image: Optional[str] = None
    points_value: int = 10
    rarity_score: float = 1.0
    is_hidden: bool = False
    is_seasonal: bool = False
    season_id: Optional[str] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    max_completions: int = 1
    completion_window_hours: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PlayerProgress:
    """Player progress for a specific achievement."""
    progress_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str = ""
    achievement_id: str = ""
    status: GamingAchievementStatus = GamingAchievementStatus.AVAILABLE
    current_progress: Dict[str, Union[int, float, Decimal]] = field(default_factory=dict)
    completion_percentage: float = 0.0
    completions_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    streak_count: int = 0
    best_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlayerAchievementStats:
    """Overall achievement statistics for a player."""
    player_id: str = ""
    total_achievements: int = 0
    completed_achievements: int = 0
    claimed_achievements: int = 0
    total_points: int = 0
    rarity_score: float = 0.0
    categories_completed: Dict[GamingAchievementCategory, int] = field(default_factory=dict)
    difficulty_completed: Dict[GamingAchievementDifficulty, int] = field(default_factory=dict)
    completion_rate: float = 0.0
    average_completion_time: float = 0.0
    fastest_completion: Optional[float] = None
    longest_streak: int = 0
    seasonal_completions: int = 0
    hidden_discoveries: int = 0
    last_achievement_date: Optional[datetime] = None
    achievement_velocity: float = 0.0  # achievements per day
    leaderboard_rank: Optional[int] = None


class GamingAchievementSystem:
    """
    Advanced gaming achievement system providing immersive achievement tracking,
    RPG-style progression, and competitive achievement mechanics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.achievements: Dict[str, GamingAchievement] = {}
        self.player_progress: Dict[str, Dict[str, PlayerProgress]] = {}
        self.player_stats: Dict[str, PlayerAchievementStats] = {}
        self.achievement_templates: Dict[str, Dict[str, Any]] = {}
        self.seasonal_achievements: Dict[str, List[str]] = {}
        self.hidden_achievements: List[str] = []
        
        self._initialize_gaming_achievements()
        logger.info("🏆 Gaming Achievement System initialized")
    
    def _initialize_gaming_achievements(self):
        """Initialize gaming achievements with templates."""
        # Tycoon Mastery Achievements
        tycoon_achievements = [
            {
                "name": "First Steps",
                "description": "Purchase your first asset",
                "category": GamingAchievementCategory.TYCOON_MASTERY,
                "difficulty": GamingAchievementDifficulty.TRIVIAL,
                "requirements": [{"metric_key": "assets_purchased", "required_value": 1}],
                "rewards": {"amount": Decimal('50'), "badges": ["first_asset"]}
            },
            {
                "name": "Asset Collector",
                "description": "Own 10 different assets",
                "category": GamingAchievementCategory.ASSET_COLLECTOR,
                "difficulty": GamingAchievementDifficulty.EASY,
                "requirements": [{"metric_key": "total_assets", "required_value": 10}],
                "rewards": {"amount": Decimal('200'), "badges": ["collector"]}
            },
            {
                "name": "Millionaire",
                "description": "Accumulate 1 million tycoon cash",
                "category": GamingAchievementCategory.WEALTH_BUILDER,
                "difficulty": GamingAchievementDifficulty.MEDIUM,
                "requirements": [{"metric_key": "total_cash_earned", "required_value": 1000000}],
                "rewards": {"amount": Decimal('1000'), "badges": ["millionaire"], "titles": ["Cash King"]}
            },
            {
                "name": "Speed Demon",
                "description": "Reach level 10 in under 1 hour",
                "category": GamingAchievementCategory.SPEED_RUNNER,
                "difficulty": GamingAchievementDifficulty.HARD,
                "achievement_type": GamingAchievementType.SPEED,
                "requirements": [
                    {"metric_key": "player_level", "required_value": 10},
                    {"metric_key": "playtime_hours", "required_value": 1, "comparison_type": "less_equal"}
                ],
                "rewards": {"amount": Decimal('2000'), "badges": ["speed_demon"], "special_items": ["time_accelerator"]}
            },
            {
                "name": "Efficiency Master",
                "description": "Achieve 95% efficiency across all assets",
                "category": GamingAchievementCategory.EFFICIENCY_EXPERT,
                "difficulty": GamingAchievementDifficulty.EXTREME,
                "requirements": [{"metric_key": "average_efficiency", "required_value": 0.95}],
                "rewards": {"amount": Decimal('5000'), "badges": ["efficiency_master"], "unlocks": ["premium_upgrades"]}
            }
        ]
        
        # Competitive Achievements
        competitive_achievements = [
            {
                "name": "First Victory",
                "description": "Win your first competitive match",
                "category": GamingAchievementCategory.COMPETITIVE_CHAMPION,
                "difficulty": GamingAchievementDifficulty.EASY,
                "requirements": [{"metric_key": "competitive_wins", "required_value": 1}],
                "rewards": {"amount": Decimal('300'), "badges": ["first_victory"]}
            },
            {
                "name": "Champion",
                "description": "Win 100 competitive matches",
                "category": GamingAchievementCategory.COMPETITIVE_CHAMPION,
                "difficulty": GamingAchievementDifficulty.EXTREME,
                "achievement_type": GamingAchievementType.CUMULATIVE,
                "requirements": [{"metric_key": "competitive_wins", "required_value": 100}],
                "rewards": {"amount": Decimal('10000'), "badges": ["champion"], "titles": ["Grand Champion"]}
            },
            {
                "name": "Unstoppable",
                "description": "Achieve a 10-game winning streak",
                "category": GamingAchievementCategory.COMPETITIVE_CHAMPION,
                "difficulty": GamingAchievementDifficulty.HARD,
                "achievement_type": GamingAchievementType.STREAK,
                "requirements": [{"metric_key": "win_streak", "required_value": 10}],
                "rewards": {"amount": Decimal('3000'), "badges": ["unstoppable"]}
            }
        ]
        
        # Hidden Achievements
        hidden_achievements = [
            {
                "name": "Secret Collector",
                "description": "Discover this hidden achievement",
                "category": GamingAchievementCategory.RARE_ACHIEVER,
                "difficulty": GamingAchievementDifficulty.LEGENDARY,
                "is_hidden": True,
                "requirements": [{"metric_key": "secret_actions", "required_value": 5}],
                "rewards": {"amount": Decimal('5000'), "badges": ["secret_master"], "special_items": ["mystery_box"]}
            }
        ]
        
        # Create achievement objects
        all_achievement_data = tycoon_achievements + competitive_achievements + hidden_achievements
        
        for data in all_achievement_data:
            achievement = self._create_achievement_from_data(data)
            self.achievements[achievement.achievement_id] = achievement
            
            if achievement.is_hidden:
                self.hidden_achievements.append(achievement.achievement_id)
        
        logger.info(f"Initialized {len(self.achievements)} gaming achievements")
    
    def _create_achievement_from_data(self, data: Dict[str, Any]) -> GamingAchievement:
        """Create an achievement object from template data."""
        achievement = GamingAchievement(
            name=data["name"],
            description=data["description"],
            category=data["category"],
            difficulty=data["difficulty"],
            achievement_type=data.get("achievement_type", GamingAchievementType.MILESTONE),
            is_hidden=data.get("is_hidden", False),
            is_seasonal=data.get("is_seasonal", False)
        )
        
        # Create requirements
        for req_data in data.get("requirements", []):
            requirement = GamingAchievementRequirement(
                metric_key=req_data["metric_key"],
                required_value=req_data["required_value"],
                comparison_type=req_data.get("comparison_type", "greater_equal"),
                description=req_data.get("description", "")
            )
            achievement.requirements.append(requirement)
        
        # Create rewards
        reward_data = data.get("rewards", {})
        achievement.rewards = GamingAchievementReward(
            amount=reward_data.get("amount", Decimal('100')),
            badges=reward_data.get("badges", []),
            titles=reward_data.get("titles", []),
            special_items=reward_data.get("special_items", []),
            unlocks=reward_data.get("unlocks", [])
        )
        
        # Set points based on difficulty
        difficulty_points = {
            GamingAchievementDifficulty.TRIVIAL: 5,
            GamingAchievementDifficulty.EASY: 10,
            GamingAchievementDifficulty.MEDIUM: 25,
            GamingAchievementDifficulty.HARD: 50,
            GamingAchievementDifficulty.EXTREME: 100,
            GamingAchievementDifficulty.LEGENDARY: 250,
            GamingAchievementDifficulty.MYTHICAL: 500,
            GamingAchievementDifficulty.IMPOSSIBLE: 1000
        }
        achievement.points_value = difficulty_points.get(achievement.difficulty, 10)
        
        return achievement
    
    async def track_gaming_progress(
        self,
        player_id: str,
        metric_updates: Dict[str, Union[int, float, Decimal]]
    ) -> List[str]:
        """Track gaming progress and return list of newly completed achievements."""
        try:
            completed_achievements = []
            
            # Initialize player progress if needed
            if player_id not in self.player_progress:
                await self._initialize_player_progress(player_id)
            
            # Update progress for all achievements
            for achievement_id, achievement in self.achievements.items():
                if achievement.is_hidden and achievement_id in self.hidden_achievements:
                    # Skip hidden achievements unless specific trigger
                    continue
                
                progress = self.player_progress[player_id].get(achievement_id)
                if not progress:
                    progress = await self._create_player_progress(player_id, achievement_id)
                    self.player_progress[player_id][achievement_id] = progress
                
                # Skip if already completed
                if progress.status == GamingAchievementStatus.COMPLETED:
                    continue
                
                # Update progress
                old_percentage = progress.completion_percentage
                await self._update_achievement_progress(progress, achievement, metric_updates)
                
                # Check if newly completed
                if (progress.completion_percentage >= 100.0 and 
                    old_percentage < 100.0 and 
                    progress.status != GamingAchievementStatus.COMPLETED):
                    
                    await self._complete_achievement(player_id, achievement_id)
                    completed_achievements.append(achievement_id)
            
            # Update player stats
            await self._update_player_stats(player_id)
            
            if completed_achievements:
                logger.info(f"Player {player_id} completed {len(completed_achievements)} achievements")
            
            return completed_achievements
            
        except Exception as e:
            logger.error(f"Error tracking gaming progress: {e}")
            return []
    
    async def _initialize_player_progress(self, player_id: str):
        """Initialize progress tracking for a new player."""
        self.player_progress[player_id] = {}
        self.player_stats[player_id] = PlayerAchievementStats(
            player_id=player_id,
            total_achievements=len(self.achievements)
        )
    
    async def _create_player_progress(self, player_id: str, achievement_id: str) -> PlayerProgress:
        """Create new progress entry for a player achievement."""
        achievement = self.achievements[achievement_id]
        
        # Check prerequisites
        status = GamingAchievementStatus.AVAILABLE
        if achievement.prerequisites:
            for prereq_id in achievement.prerequisites:
                prereq_progress = self.player_progress[player_id].get(prereq_id)
                if not prereq_progress or prereq_progress.status != GamingAchievementStatus.COMPLETED:
                    status = GamingAchievementStatus.LOCKED
                    break
        
        progress = PlayerProgress(
            player_id=player_id,
            achievement_id=achievement_id,
            status=status
        )
        
        return progress
    
    async def _update_achievement_progress(
        self,
        progress: PlayerProgress,
        achievement: GamingAchievement,
        metric_updates: Dict[str, Union[int, float, Decimal]]
    ):
        """Update progress for a specific achievement."""
        if progress.status == GamingAchievementStatus.LOCKED:
            return
        
        # Update current progress values
        for metric, value in metric_updates.items():
            if metric in progress.current_progress:
                # For cumulative achievements, add to existing value
                if achievement.achievement_type == GamingAchievementType.CUMULATIVE:
                    progress.current_progress[metric] = progress.current_progress[metric] + value
                else:
                    # For other types, update to new value
                    progress.current_progress[metric] = max(progress.current_progress[metric], value)
            else:
                progress.current_progress[metric] = value
        
        # Calculate completion percentage
        progress.completion_percentage = await self._calculate_completion_percentage(achievement, progress)
        
        # Update status
        if progress.completion_percentage >= 100.0:
            progress.status = GamingAchievementStatus.COMPLETED
            progress.completed_at = datetime.now(timezone.utc)
        elif progress.completion_percentage > 0.0:
            progress.status = GamingAchievementStatus.IN_PROGRESS
            if not progress.started_at:
                progress.started_at = datetime.now(timezone.utc)
        
        progress.last_updated = datetime.now(timezone.utc)
    
    async def _calculate_completion_percentage(
        self,
        achievement: GamingAchievement,
        progress: PlayerProgress
    ) -> float:
        """Calculate completion percentage for an achievement."""
        if not achievement.requirements:
            return 100.0
        
        total_requirements = len(achievement.requirements)
        completed_requirements = 0
        requirement_percentages = []
        
        for requirement in achievement.requirements:
            current_value = progress.current_progress.get(requirement.metric_key, 0)
            required_value = requirement.required_value
            
            if requirement.comparison_type == "greater_equal":
                if current_value >= required_value:
                    completed_requirements += 1
                    requirement_percentages.append(100.0)
                else:
                    percentage = min(100.0, (float(current_value) / float(required_value)) * 100.0)
                    requirement_percentages.append(percentage)
            elif requirement.comparison_type == "equal":
                if current_value == required_value:
                    completed_requirements += 1
                    requirement_percentages.append(100.0)
                else:
                    requirement_percentages.append(0.0)
            elif requirement.comparison_type == "less_equal":
                if current_value <= required_value:
                    completed_requirements += 1
                    requirement_percentages.append(100.0)
                else:
                    requirement_percentages.append(0.0)
        
        # Return average percentage across all requirements
        return sum(requirement_percentages) / len(requirement_percentages) if requirement_percentages else 0.0
    
    async def _complete_achievement(self, player_id: str, achievement_id: str):
        """Mark an achievement as completed and process rewards."""
        progress = self.player_progress[player_id][achievement_id]
        achievement = self.achievements[achievement_id]
        
        progress.completions_count += 1
        progress.status = GamingAchievementStatus.COMPLETED
        
        # Calculate completion time for speed achievements
        if achievement.achievement_type == GamingAchievementType.SPEED and progress.started_at:
            completion_time = (datetime.now(timezone.utc) - progress.started_at).total_seconds()
            if not progress.best_time or completion_time < progress.best_time:
                progress.best_time = completion_time
        
        logger.info(f"Achievement completed: {achievement.name} by player {player_id}")
    
    async def unlock_gaming_achievement(self, player_id: str, achievement_id: str) -> Dict[str, Any]:
        """Manually unlock a gaming achievement (for hidden achievements)."""
        try:
            if achievement_id not in self.achievements:
                return {"success": False, "message": "Achievement not found"}
            
            if player_id not in self.player_progress:
                await self._initialize_player_progress(player_id)
            
            progress = self.player_progress[player_id].get(achievement_id)
            if not progress:
                progress = await self._create_player_progress(player_id, achievement_id)
                self.player_progress[player_id][achievement_id] = progress
            
            if progress.status == GamingAchievementStatus.COMPLETED:
                return {"success": False, "message": "Achievement already completed"}
            
            # Complete the achievement
            progress.status = GamingAchievementStatus.COMPLETED
            progress.completion_percentage = 100.0
            progress.completed_at = datetime.now(timezone.utc)
            progress.completions_count += 1
            
            achievement = self.achievements[achievement_id]
            await self._update_player_stats(player_id)
            
            return {
                "success": True,
                "achievement": {
                    "id": achievement_id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "points": achievement.points_value,
                    "rewards": {
                        "amount": float(achievement.rewards.amount),
                        "badges": achievement.rewards.badges,
                        "titles": achievement.rewards.titles,
                        "special_items": achievement.rewards.special_items
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error unlocking gaming achievement: {e}")
            return {"success": False, "message": str(e)}
    
    async def _update_player_stats(self, player_id: str):
        """Update overall achievement statistics for a player."""
        if player_id not in self.player_stats:
            return
        
        stats = self.player_stats[player_id]
        player_progress = self.player_progress.get(player_id, {})
        
        # Count completions
        completed = sum(1 for p in player_progress.values() if p.status == GamingAchievementStatus.COMPLETED)
        claimed = sum(1 for p in player_progress.values() if p.status == GamingAchievementStatus.CLAIMED)
        
        # Calculate points
        total_points = 0
        for progress in player_progress.values():
            if progress.status == GamingAchievementStatus.COMPLETED:
                achievement = self.achievements.get(progress.achievement_id)
                if achievement:
                    total_points += achievement.points_value
        
        # Update stats
        stats.completed_achievements = completed
        stats.claimed_achievements = claimed
        stats.total_points = total_points
        stats.completion_rate = (completed / stats.total_achievements) * 100.0 if stats.total_achievements > 0 else 0.0
        
        # Find latest achievement
        latest_completion = None
        for progress in player_progress.values():
            if progress.completed_at and (not latest_completion or progress.completed_at > latest_completion):
                latest_completion = progress.completed_at
        stats.last_achievement_date = latest_completion
        
        # Calculate achievement velocity (achievements per day)
        if latest_completion and completed > 0:
            # Find first achievement date
            first_completion = min(
                p.completed_at for p in player_progress.values() 
                if p.completed_at and p.status == GamingAchievementStatus.COMPLETED
            )
            if first_completion:
                days_active = (latest_completion - first_completion).days + 1
                stats.achievement_velocity = completed / days_active if days_active > 0 else 0.0
    
    async def get_gaming_achievements(self, player_id: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """Get all gaming achievements for a player with progress."""
        try:
            if player_id not in self.player_progress:
                await self._initialize_player_progress(player_id)
            
            achievements_data = []
            
            for achievement_id, achievement in self.achievements.items():
                # Skip hidden achievements unless specifically requested
                if achievement.is_hidden and not include_hidden:
                    continue
                
                progress = self.player_progress[player_id].get(achievement_id)
                if not progress:
                    progress = await self._create_player_progress(player_id, achievement_id)
                    self.player_progress[player_id][achievement_id] = progress
                
                achievement_data = {
                    "id": achievement_id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "category": achievement.category.value,
                    "difficulty": achievement.difficulty.value,
                    "type": achievement.achievement_type.value,
                    "points": achievement.points_value,
                    "status": progress.status.value,
                    "completion_percentage": progress.completion_percentage,
                    "completions_count": progress.completions_count,
                    "is_hidden": achievement.is_hidden,
                    "is_seasonal": achievement.is_seasonal,
                    "requirements": [
                        {
                            "metric": req.metric_key,
                            "required": float(req.required_value),
                            "current": float(progress.current_progress.get(req.metric_key, 0)),
                            "comparison": req.comparison_type
                        }
                        for req in achievement.requirements
                    ],
                    "rewards": {
                        "amount": float(achievement.rewards.amount),
                        "currency": achievement.rewards.currency_type,
                        "badges": achievement.rewards.badges,
                        "titles": achievement.rewards.titles,
                        "special_items": achievement.rewards.special_items
                    }
                }
                
                if progress.completed_at:
                    achievement_data["completed_at"] = progress.completed_at.isoformat()
                if progress.best_time:
                    achievement_data["best_time"] = progress.best_time
                
                achievements_data.append(achievement_data)
            
            return achievements_data
            
        except Exception as e:
            logger.error(f"Error getting gaming achievements: {e}")
            return []
    
    async def get_player_achievement_stats(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive achievement statistics for a player."""
        try:
            if player_id not in self.player_stats:
                await self._initialize_player_progress(player_id)
            
            stats = self.player_stats[player_id]
            
            return {
                "player_id": player_id,
                "total_achievements": stats.total_achievements,
                "completed_achievements": stats.completed_achievements,
                "claimed_achievements": stats.claimed_achievements,
                "total_points": stats.total_points,
                "completion_rate": stats.completion_rate,
                "achievement_velocity": stats.achievement_velocity,
                "last_achievement_date": stats.last_achievement_date.isoformat() if stats.last_achievement_date else None,
                "leaderboard_rank": stats.leaderboard_rank
            }
            
        except Exception as e:
            logger.error(f"Error getting player achievement stats: {e}")
            return None


# Global instance
_gaming_achievements_instance: Optional[GamingAchievementSystem] = None


def get_gaming_achievements() -> GamingAchievementSystem:
    """Get the global gaming achievement system instance."""
    global _gaming_achievements_instance
    if _gaming_achievements_instance is None:
        _gaming_achievements_instance = GamingAchievementSystem()
    return _gaming_achievements_instance


async def unlock_gaming_achievement(player_id: str, achievement_id: str) -> Dict[str, Any]:
    """Unlock a gaming achievement for a player."""
    system = get_gaming_achievements()
    return await system.unlock_gaming_achievement(player_id, achievement_id)


async def track_gaming_progress(player_id: str, metric_updates: Dict[str, Union[int, float, Decimal]]) -> List[str]:
    """Track gaming progress and return newly completed achievements."""
    system = get_gaming_achievements()
    return await system.track_gaming_progress(player_id, metric_updates)