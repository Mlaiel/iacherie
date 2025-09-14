"""Badge System Workflow

AI-powered badge system and achievement recognition workflow.

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

logger = logging.getLogger(__name__)


class BadgeCategory(Enum):
    """Badge categories"""
    CREATOR = "creator"
    SOCIAL = "social"
    MILESTONE = "milestone"
    SKILL = "skill"
    SPECIAL = "special"
    SEASONAL = "seasonal"


class BadgeRarity(Enum):
    """Badge rarity levels"""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Badge:
    """Badge definition"""
    badge_id: str
    name: str
    description: str
    category: BadgeCategory
    rarity: BadgeRarity
    icon_url: str
    unlock_criteria: Dict[str, Any]
    points_value: int = 100
    is_active: bool = True


@dataclass
class UserBadge:
    """User's earned badge"""
    user_id: str
    badge: Badge
    earned_at: datetime = field(default_factory=datetime.utcnow)
    progress_data: Dict[str, Any] = field(default_factory=dict)


class BadgeSystemWorkflow:
    """AI-powered badge system workflow"""
    
    def __init__(self) -> None:
        self.metrics_collector = MetricsCollector()
        self.available_badges: Dict[str, Badge] = {}
        self.user_badges: Dict[str, List[UserBadge]] = {}
        self._initialize_default_badges()
        
    def _initialize_default_badges(self) -> None:
        """Initialize default badge collection"""
        default_badges = [
            Badge("first_post", "First Steps", "Created your first post", BadgeCategory.CREATOR, BadgeRarity.COMMON, "/badges/first_post.png", {"posts_created": 1}),
            Badge("prolific_creator", "Prolific Creator", "Created 100 posts", BadgeCategory.CREATOR, BadgeRarity.RARE, "/badges/prolific.png", {"posts_created": 100}),
            Badge("social_butterfly", "Social Butterfly", "Liked 1000 posts", BadgeCategory.SOCIAL, BadgeRarity.COMMON, "/badges/social.png", {"likes_given": 1000}),
            Badge("influencer", "Rising Influencer", "Gained 10,000 followers", BadgeCategory.MILESTONE, BadgeRarity.EPIC, "/badges/influencer.png", {"followers": 10000}),
            Badge("collaborator", "Team Player", "Completed 10 collaborations", BadgeCategory.SKILL, BadgeRarity.RARE, "/badges/collaborator.png", {"collaborations": 10}),
        ]
        
        for badge in default_badges:
            self.available_badges[badge.badge_id] = badge
    
    async def check_badge_eligibility(self, user_id: str, user_stats: Dict[str, Any]) -> List[Badge]:
        """
        Check which badges user is eligible for
        
        Args:
            user_id: User identifier
            user_stats: User's current statistics
            
        Returns:
            List of eligible badges
        """
        try:
            eligible_badges = []
            user_badge_ids = [ub.badge.badge_id for ub in self.user_badges.get(user_id, [])]
            
            for badge in self.available_badges.values():
                if badge.badge_id not in user_badge_ids and badge.is_active:
                    if await self._check_unlock_criteria(badge.unlock_criteria, user_stats):
                        eligible_badges.append(badge)
            
            return eligible_badges
            
        except Exception as e:
            logger.error(f"Badge eligibility check failed: {e}")
            return []
    
    async def award_badge(self, user_id: str, badge_id: str, progress_data: Dict[str, Any] = None) -> UserBadge:
        """
        Award badge to user
        
        Args:
            user_id: User identifier
            badge_id: Badge identifier
            progress_data: Additional progress data
            
        Returns:
            UserBadge object
        """
        try:
            if badge_id not in self.available_badges:
                raise WorkflowError(f"Badge {badge_id} not found")
            
            badge = self.available_badges[badge_id]
            
            # Check if user already has this badge
            if user_id in self.user_badges:
                for user_badge in self.user_badges[user_id]:
                    if user_badge.badge.badge_id == badge_id:
                        return user_badge  # Already earned
            
            # Create user badge
            user_badge = UserBadge(
                user_id=user_id,
                badge=badge,
                progress_data=progress_data or {}
            )
            
            # Store badge
            if user_id not in self.user_badges:
                self.user_badges[user_id] = []
            self.user_badges[user_id].append(user_badge)
            
            # Record metrics
            await self.metrics_collector.record_metric("badges_awarded", 1)
            await self.metrics_collector.record_metric(f"badge_{badge.category.value}", 1)
            await self.metrics_collector.record_metric(f"badge_rarity_{badge.rarity.value}", 1)
            
            logger.info(f"Badge '{badge.name}' awarded to user {user_id}")
            return user_badge
            
        except Exception as e:
            logger.error(f"Badge award failed: {e}")
            raise WorkflowError(f"Badge award failed: {e}")
    
    async def get_user_badges(self, user_id: str, category: Optional[BadgeCategory] = None) -> List[UserBadge]:
        """Get user's badges with optional category filter"""
        
        user_badges = self.user_badges.get(user_id, [])
        
        if category:
            user_badges = [ub for ub in user_badges if ub.badge.category == category]
        
        # Sort by earned date (newest first)
        user_badges.sort(key=lambda x: x.earned_at, reverse=True)
        
        return user_badges
    
    async def get_badge_progress(self, user_id: str, badge_id: str, user_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Get user's progress toward a specific badge"""
        
        if badge_id not in self.available_badges:
            return {"error": "Badge not found"}
        
        badge = self.available_badges[badge_id]
        
        # Check if already earned
        if user_id in self.user_badges:
            for user_badge in self.user_badges[user_id]:
                if user_badge.badge.badge_id == badge_id:
                    return {"status": "earned", "earned_at": user_badge.earned_at}
        
        # Calculate progress
        progress = {}
        for criteria_key, required_value in badge.unlock_criteria.items():
            current_value = user_stats.get(criteria_key, 0)
            progress[criteria_key] = {
                "current": current_value,
                "required": required_value,
                "percentage": min((current_value / required_value) * 100, 100) if required_value > 0 else 100
            }
        
        # Calculate overall progress
        overall_progress = sum(p["percentage"] for p in progress.values()) / len(progress) if progress else 0
        
        return {
            "status": "in_progress",
            "overall_progress": overall_progress,
            "criteria_progress": progress,
            "badge": badge
        }
    
    async def create_custom_badge(
        self,
        badge_id: str,
        name: str,
        description: str,
        category: BadgeCategory,
        rarity: BadgeRarity,
        unlock_criteria: Dict[str, Any],
        icon_url: str = "",
        points_value: int = 100
    ) -> Badge:
        """Create custom badge"""
        
        badge = Badge(
            badge_id=badge_id,
            name=name,
            description=description,
            category=category,
            rarity=rarity,
            icon_url=icon_url or f"/badges/{badge_id}.png",
            unlock_criteria=unlock_criteria,
            points_value=points_value
        )
        
        self.available_badges[badge_id] = badge
        logger.info(f"Custom badge created: {name}")
        
        return badge
    
    async def get_badge_showcase(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get badge showcase with rarity and popularity"""
        
        badge_stats = {}
        
        # Calculate badge statistics
        for user_badges in self.user_badges.values():
            for user_badge in user_badges:
                badge_id = user_badge.badge.badge_id
                if badge_id not in badge_stats:
                    badge_stats[badge_id] = {"count": 0, "recent_count": 0}
                
                badge_stats[badge_id]["count"] += 1
                
                # Count recent awards (last 30 days)
                if user_badge.earned_at >= datetime.utcnow() - timedelta(days=30):
                    badge_stats[badge_id]["recent_count"] += 1
        
        # Create showcase
        showcase = []
        for badge in self.available_badges.values():
            if badge.is_active:
                stats = badge_stats.get(badge.badge_id, {"count": 0, "recent_count": 0})
                showcase_item = {
                    "badge": badge,
                    "total_earned": stats["count"],
                    "recent_earned": stats["recent_count"],
                    "rarity_score": await self._calculate_rarity_score(badge, stats["count"])
                }
                showcase.append(showcase_item)
        
        # Sort by rarity score and recent activity
        showcase.sort(key=lambda x: (x["rarity_score"], x["recent_earned"]), reverse=True)
        
        return showcase[:limit]
    
    async def _check_unlock_criteria(self, criteria: Dict[str, Any], user_stats: Dict[str, Any]) -> bool:
        """Check if user meets unlock criteria"""
        
        for criteria_key, required_value in criteria.items():
            current_value = user_stats.get(criteria_key, 0)
            if current_value < required_value:
                return False
        
        return True
    
    async def _calculate_rarity_score(self, badge: Badge, earned_count: int) -> float:
        """Calculate badge rarity score"""
        
        # Base rarity from badge definition
        rarity_multipliers = {
            BadgeRarity.COMMON: 1.0,
            BadgeRarity.RARE: 2.0,
            BadgeRarity.EPIC: 4.0,
            BadgeRarity.LEGENDARY: 8.0
        }
        
        base_rarity = rarity_multipliers[badge.rarity]
        
        # Adjust by actual earning frequency (fewer earned = more rare)
        frequency_factor = max(1.0, 100 / max(earned_count, 1))
        
        return base_rarity * frequency_factor