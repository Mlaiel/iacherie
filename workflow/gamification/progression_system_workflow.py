"""Progression System Workflow

AI-powered user progression and leveling system workflow for content creators.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector
from ..utils.caching import CacheManager

logger = logging.getLogger(__name__)


class ProgressionType(Enum):
    """Types of progression systems"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    SKILL_TREE = "skill_tree"
    MILESTONE_BASED = "milestone_based"


@dataclass
class UserLevel:
    """User level information"""
    user_id: str
    current_level: int
    current_xp: int
    xp_to_next_level: int
    total_xp: int
    level_title: str
    unlock_features: List[str] = field(default_factory=list)
    level_rewards: List[str] = field(default_factory=list)


@dataclass
class ProgressionResult:
    """Progression workflow result"""
    user_id: str
    previous_level: int
    current_level: int
    xp_gained: int
    level_up: bool
    new_unlocks: List[str]
    rewards_earned: List[str]
    progression_analysis: Dict[str, Any]
    updated_at: datetime = field(default_factory=datetime.utcnow)


class ProgressionSystemWorkflow:
    """AI-powered progression system workflow"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.cache_manager = CacheManager()
        self.user_progressions: Dict[str, UserLevel] = {}
        
    async def update_user_progression(
        self,
        user_id: str,
        action_type: str,
        xp_earned: int,
        progression_type: ProgressionType = ProgressionType.LINEAR
    ) -> ProgressionResult:
        """
        Update user progression based on actions
        
        Args:
            user_id: User identifier
            action_type: Type of action performed
            xp_earned: Experience points earned
            progression_type: Type of progression system
            
        Returns:
            ProgressionResult with progression updates
        """
        try:
            start_time = datetime.utcnow()
            
            logger.info(f"Updating progression for user {user_id}: +{xp_earned} XP")
            
            # Get current user level
            current_level = await self._get_user_level(user_id)
            previous_level_num = current_level.current_level
            
            # Calculate new XP and level
            new_total_xp = current_level.total_xp + xp_earned
            new_level_data = await self._calculate_level_from_xp(new_total_xp, progression_type)
            
            # Check for level up
            level_up = new_level_data["level"] > current_level.current_level
            
            # Get new unlocks and rewards
            new_unlocks = []
            rewards_earned = []
            
            if level_up:
                new_unlocks = await self._get_level_unlocks(new_level_data["level"])
                rewards_earned = await self._get_level_rewards(new_level_data["level"])
            
            # Update user progression
            updated_level = UserLevel(
                user_id=user_id,
                current_level=new_level_data["level"],
                current_xp=new_level_data["current_xp"],
                xp_to_next_level=new_level_data["xp_to_next"],
                total_xp=new_total_xp,
                level_title=new_level_data["title"],
                unlock_features=current_level.unlock_features + new_unlocks,
                level_rewards=current_level.level_rewards + rewards_earned
            )
            
            # Store updated progression
            self.user_progressions[user_id] = updated_level
            
            # Generate progression analysis
            progression_analysis = await self._analyze_progression(
                user_id, action_type, xp_earned, level_up
            )
            
            # Create result
            result = ProgressionResult(
                user_id=user_id,
                previous_level=previous_level_num,
                current_level=updated_level.current_level,
                xp_gained=xp_earned,
                level_up=level_up,
                new_unlocks=new_unlocks,
                rewards_earned=rewards_earned,
                progression_analysis=progression_analysis
            )
            
            # Cache progression data
            await self._cache_progression(updated_level)
            
            # Record metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_metric("progression_update_duration", duration)
            await self.metrics_collector.record_metric("user_level", updated_level.current_level)
            
            if level_up:
                await self.metrics_collector.record_metric("level_ups", 1)
                logger.info(f"User {user_id} leveled up to level {updated_level.current_level}!")
            
            return result
            
        except Exception as e:
            logger.error(f"Progression update failed for user {user_id}: {e}")
            raise WorkflowError(f"Progression update failed: {e}")
    
    async def _get_user_level(self, user_id: str) -> UserLevel:
        """Get current user level data"""
        if user_id in self.user_progressions:
            return self.user_progressions[user_id]
        
        # Check cache
        cached_level = await self.cache_manager.get(f"user_level_{user_id}")
        if cached_level:
            self.user_progressions[user_id] = cached_level
            return cached_level
        
        # Create new user progression
        new_level = UserLevel(
            user_id=user_id,
            current_level=1,
            current_xp=0,
            xp_to_next_level=100,
            total_xp=0,
            level_title="Newcomer"
        )
        
        self.user_progressions[user_id] = new_level
        return new_level
    
    async def _calculate_level_from_xp(self, total_xp: int, progression_type: ProgressionType) -> Dict[str, Any]:
        """Calculate level and XP breakdown from total XP"""
        if progression_type == ProgressionType.LINEAR:
            # Linear progression: 100 XP per level
            level = (total_xp // 100) + 1
            current_xp = total_xp % 100
            xp_to_next = 100 - current_xp
            
        elif progression_type == ProgressionType.EXPONENTIAL:
            # Exponential progression: XP requirement increases each level
            level = 1
            xp_required = 100
            remaining_xp = total_xp
            
            while remaining_xp >= xp_required:
                remaining_xp -= xp_required
                level += 1
                xp_required = int(xp_required * 1.2)  # 20% increase each level
            
            current_xp = remaining_xp
            xp_to_next = xp_required - current_xp
            
        else:
            # Default to linear
            level = (total_xp // 100) + 1
            current_xp = total_xp % 100
            xp_to_next = 100 - current_xp
        
        # Get level title
        title = await self._get_level_title(level)
        
        return {
            "level": level,
            "current_xp": current_xp,
            "xp_to_next": xp_to_next,
            "title": title
        }
    
    async def _get_level_title(self, level: int) -> str:
        """Get title for level"""
        level_titles = {
            1: "Newcomer",
            5: "Rising Creator",
            10: "Content Enthusiast", 
            15: "Skilled Creator",
            20: "Expert Creator",
            25: "Master Creator",
            30: "Elite Creator",
            40: "Legendary Creator",
            50: "Creator Master",
            75: "Creator Legend",
            100: "Creator God"
        }
        
        # Find the highest title that applies
        applicable_title = "Newcomer"
        for title_level, title in level_titles.items():
            if level >= title_level:
                applicable_title = title
        
        return applicable_title
    
    async def _get_level_unlocks(self, level: int) -> List[str]:
        """Get features unlocked at level"""
        level_unlocks = {
            5: ["Advanced Analytics"],
            10: ["Custom Branding", "Priority Support"],
            15: ["Collaboration Tools", "Advanced Scheduling"],
            20: ["White Label Options", "API Access"],
            25: ["Custom Workflows", "Advanced Integrations"],
            30: ["Enterprise Features", "Dedicated Manager"],
            40: ["Beta Feature Access", "Custom Development"],
            50: ["VIP Status", "Special Events Access"]
        }
        
        return level_unlocks.get(level, [])
    
    async def _get_level_rewards(self, level: int) -> List[str]:
        """Get rewards earned at level"""
        level_rewards = {
            5: ["100 Bonus Credits", "Achievement Badge"],
            10: ["Premium Template Pack", "Special Badge"],
            15: ["Advanced Feature Credits", "Milestone Badge"],
            20: ["Enterprise Trial", "Expert Badge"],
            25: ["Custom Consultation", "Master Badge"],
            30: ["VIP Benefits", "Elite Badge"],
            40: ["Special Recognition", "Legendary Badge"],
            50: ["Lifetime Benefits", "Ultimate Badge"]
        }
        
        return level_rewards.get(level, [])
    
    async def _analyze_progression(
        self, user_id: str, action_type: str, xp_earned: int, level_up: bool
    ) -> Dict[str, Any]:
        """Analyze progression patterns and provide insights"""
        
        analysis = {
            "xp_source": action_type,
            "xp_amount": xp_earned,
            "level_up_achieved": level_up,
            "progression_velocity": "normal",  # Calculate based on time between levels
            "engagement_pattern": "consistent",  # Analyze engagement patterns
            "projected_next_level": await self._project_next_level_time(user_id),
            "recommendations": await self._get_progression_recommendations(user_id)
        }
        
        return analysis
    
    async def _project_next_level_time(self, user_id: str) -> Dict[str, Any]:
        """Project when user will reach next level"""
        user_level = self.user_progressions.get(user_id)
        if not user_level:
            return {"error": "User progression not found"}
        
        # Simple projection based on average XP per day
        avg_xp_per_day = 50  # This would be calculated from historical data
        days_to_next_level = user_level.xp_to_next_level / avg_xp_per_day
        
        return {
            "days_estimated": round(days_to_next_level, 1),
            "xp_needed": user_level.xp_to_next_level,
            "daily_xp_average": avg_xp_per_day
        }
    
    async def _get_progression_recommendations(self, user_id: str) -> List[str]:
        """Get personalized progression recommendations"""
        recommendations = [
            "Complete daily challenges for bonus XP",
            "Engage with community content for social XP",
            "Create high-quality content for performance bonuses",
            "Participate in platform events for special rewards",
            "Collaborate with other creators for collaboration XP"
        ]
        
        return recommendations[:3]  # Return top 3 recommendations
    
    async def _cache_progression(self, user_level: UserLevel):
        """Cache user progression data"""
        cache_key = f"user_level_{user_level.user_id}"
        await self.cache_manager.set(cache_key, user_level, ttl=3600)
    
    async def get_leaderboard(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get progression leaderboard"""
        # Sort users by total XP
        sorted_users = sorted(
            self.user_progressions.values(),
            key=lambda x: x.total_xp,
            reverse=True
        )
        
        leaderboard = []
        for i, user in enumerate(sorted_users[:limit]):
            leaderboard.append({
                "rank": i + 1,
                "user_id": user.user_id,
                "level": user.current_level,
                "total_xp": user.total_xp,
                "title": user.level_title
            })
        
        return leaderboard
    
    async def get_progression_stats(self, user_id: str) -> Dict[str, Any]:
        """Get detailed progression statistics for user"""
        user_level = await self._get_user_level(user_id)
        
        stats = {
            "current_level": user_level.current_level,
            "total_xp": user_level.total_xp,
            "current_level_xp": user_level.current_xp,
            "xp_to_next_level": user_level.xp_to_next_level,
            "level_title": user_level.level_title,
            "unlocked_features": user_level.unlock_features,
            "earned_rewards": user_level.level_rewards,
            "progression_percentage": (user_level.current_xp / (user_level.current_xp + user_level.xp_to_next_level)) * 100,
            "next_unlocks": await self._get_level_unlocks(user_level.current_level + 1),
            "next_rewards": await self._get_level_rewards(user_level.current_level + 1)
        }
        
        return stats