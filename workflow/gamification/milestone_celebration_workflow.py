"""Milestone Celebration Workflow

AI-powered milestone celebration and achievement recognition workflow.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class MilestoneType(Enum):
    """Types of milestones"""
    FOLLOWER_MILESTONE = "follower_milestone"
    CONTENT_MILESTONE = "content_milestone"
    ENGAGEMENT_MILESTONE = "engagement_milestone"
    ANNIVERSARY_MILESTONE = "anniversary_milestone"
    ACHIEVEMENT_MILESTONE = "achievement_milestone"
    COLLABORATION_MILESTONE = "collaboration_milestone"


@dataclass
class Milestone:
    """Milestone definition"""
    milestone_id: str
    user_id: str
    milestone_type: MilestoneType
    title: str
    description: str
    achievement_data: Dict[str, Any]
    celebration_level: str = "standard"  # minimal, standard, special, epic
    achieved_at: datetime = field(default_factory=datetime.utcnow)
    celebrated: bool = False
    celebration_data: Dict[str, Any] = field(default_factory=dict)


class MilestoneCelebrationWorkflow:
    """AI-powered milestone celebration workflow"""
    
    def __init__(self) -> None:
        self.metrics_collector = MetricsCollector()
        self.user_milestones: Dict[str, List[Milestone]] = {}
        
    async def track_milestone_achievement(
        self,
        user_id: str,
        milestone_type: MilestoneType,
        achievement_data: Dict[str, Any],
        auto_celebrate: bool = True
    ) -> Milestone:
        """
        Track and celebrate milestone achievement
        
        Args:
            user_id: User identifier
            milestone_type: Type of milestone
            achievement_data: Data about the achievement
            auto_celebrate: Whether to auto-trigger celebration
            
        Returns:
            Milestone object
        """
        try:
            milestone_id = f"milestone_{int(datetime.utcnow().timestamp())}_{user_id}"
            
            # Generate milestone details
            title, description = await self._generate_milestone_details(milestone_type, achievement_data)
            
            # Determine celebration level
            celebration_level = await self._determine_celebration_level(milestone_type, achievement_data)
            
            milestone = Milestone(
                milestone_id=milestone_id,
                user_id=user_id,
                milestone_type=milestone_type,
                title=title,
                description=description,
                achievement_data=achievement_data,
                celebration_level=celebration_level,
                celebrated=auto_celebrate
            )
            
            # Store milestone
            if user_id not in self.user_milestones:
                self.user_milestones[user_id] = []
            self.user_milestones[user_id].append(milestone)
            
            # Trigger celebration if requested
            if auto_celebrate:
                await self._celebrate_milestone(milestone)
            
            # Record metrics
            await self.metrics_collector.record_metric("milestones_achieved", 1)
            await self.metrics_collector.record_metric(f"milestone_{milestone_type.value}", 1)
            
            logger.info(f"Milestone achieved: {title} for user {user_id}")
            return milestone
            
        except Exception as e:
            logger.error(f"Milestone tracking failed: {e}")
            raise WorkflowError(f"Milestone tracking failed: {e}")
    
    async def celebrate_milestone(self, milestone_id: str) -> Dict[str, Any]:
        """
        Manually trigger milestone celebration
        
        Args:
            milestone_id: Milestone identifier
            
        Returns:
            Celebration result data
        """
        try:
            milestone = await self._find_milestone(milestone_id)
            if not milestone:
                raise WorkflowError(f"Milestone {milestone_id} not found")
            
            if milestone.celebrated:
                return {"status": "already_celebrated", "milestone": milestone}
            
            celebration_result = await self._celebrate_milestone(milestone)
            milestone.celebrated = True
            milestone.celebration_data = celebration_result
            
            return {"status": "celebrated", "celebration": celebration_result}
            
        except Exception as e:
            logger.error(f"Milestone celebration failed: {e}")
            raise WorkflowError(f"Milestone celebration failed: {e}")
    
    async def get_user_milestones(
        self, 
        user_id: str, 
        milestone_type: Optional[MilestoneType] = None,
        limit: int = 50
    ) -> List[Milestone]:
        """Get user's milestones with optional filtering"""
        
        user_milestones = self.user_milestones.get(user_id, [])
        
        if milestone_type:
            user_milestones = [m for m in user_milestones if m.milestone_type == milestone_type]
        
        # Sort by achievement date (newest first)
        user_milestones.sort(key=lambda x: x.achieved_at, reverse=True)
        
        return user_milestones[:limit]
    
    async def check_potential_milestones(self, user_id: str, user_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for potential milestones based on current stats"""
        
        potential_milestones = []
        
        # Follower milestones
        followers = user_stats.get("followers_count", 0)
        follower_milestones = [100, 500, 1000, 5000, 10000, 50000, 100000]
        
        for threshold in follower_milestones:
            if followers >= threshold:
                if not await self._milestone_already_achieved(user_id, "follower", threshold):
                    potential_milestones.append({
                        "type": MilestoneType.FOLLOWER_MILESTONE,
                        "threshold": threshold,
                        "current": followers,
                        "title": f"{threshold:,} Followers Milestone",
                        "celebration_level": await self._determine_celebration_level(
                            MilestoneType.FOLLOWER_MILESTONE, {"count": threshold}
                        )
                    })
        
        # Content milestones
        posts_count = user_stats.get("posts_count", 0)
        content_milestones = [1, 10, 50, 100, 500, 1000]
        
        for threshold in content_milestones:
            if posts_count >= threshold:
                if not await self._milestone_already_achieved(user_id, "content", threshold):
                    potential_milestones.append({
                        "type": MilestoneType.CONTENT_MILESTONE,
                        "threshold": threshold,
                        "current": posts_count,
                        "title": f"{threshold} Posts Created",
                        "celebration_level": await self._determine_celebration_level(
                            MilestoneType.CONTENT_MILESTONE, {"count": threshold}
                        )
                    })
        
        # Engagement milestones
        total_likes = user_stats.get("total_likes_received", 0)
        engagement_milestones = [100, 1000, 10000, 100000]
        
        for threshold in engagement_milestones:
            if total_likes >= threshold:
                if not await self._milestone_already_achieved(user_id, "engagement", threshold):
                    potential_milestones.append({
                        "type": MilestoneType.ENGAGEMENT_MILESTONE,
                        "threshold": threshold,
                        "current": total_likes,
                        "title": f"{threshold:,} Total Likes Received",
                        "celebration_level": await self._determine_celebration_level(
                            MilestoneType.ENGAGEMENT_MILESTONE, {"count": threshold}
                        )
                    })
        
        return potential_milestones
    
    async def _generate_milestone_details(self, milestone_type: MilestoneType, data: Dict[str, Any]) -> tuple:
        """Generate title and description for milestone"""
        
        if milestone_type == MilestoneType.FOLLOWER_MILESTONE:
            count = data.get("count", 0)
            title = f"🎉 {count:,} Followers Milestone!"
            description = f"You've reached {count:,} followers! Your community is growing!"
            
        elif milestone_type == MilestoneType.CONTENT_MILESTONE:
            count = data.get("count", 0)
            if count == 1:
                title = "🎬 First Post Created!"
                description = "Welcome to your content creation journey!"
            else:
                title = f"📝 {count} Posts Created!"
                description = f"You've created {count} pieces of content. Keep it up!"
        
        elif milestone_type == MilestoneType.ENGAGEMENT_MILESTONE:
            count = data.get("count", 0)
            metric = data.get("metric", "likes")
            title = f"💖 {count:,} {metric.title()} Milestone!"
            description = f"Your content has received {count:,} {metric}!"
        
        elif milestone_type == MilestoneType.ANNIVERSARY_MILESTONE:
            years = data.get("years", 1)
            title = f"🎂 {years} Year Anniversary!"
            description = f"You've been creating amazing content for {years} year(s)!"
        
        elif milestone_type == MilestoneType.ACHIEVEMENT_MILESTONE:
            achievement_name = data.get("achievement_name", "Achievement")
            title = f"🏆 {achievement_name} Unlocked!"
            description = f"You've earned the {achievement_name} achievement!"
        
        elif milestone_type == MilestoneType.COLLABORATION_MILESTONE:
            count = data.get("count", 0)
            title = f"🤝 {count} Collaborations Completed!"
            description = f"You've successfully completed {count} collaborations!"
        
        else:
            title = "🎯 Milestone Achieved!"
            description = "Congratulations on reaching this milestone!"
        
        return title, description
    
    async def _determine_celebration_level(self, milestone_type: MilestoneType, data: Dict[str, Any]) -> str:
        """Determine appropriate celebration level"""
        
        count = data.get("count", 0)
        
        if milestone_type == MilestoneType.FOLLOWER_MILESTONE:
            if count >= 100000:
                return "epic"
            elif count >= 10000:
                return "special"
            elif count >= 1000:
                return "standard"
            else:
                return "minimal"
        
        elif milestone_type == MilestoneType.CONTENT_MILESTONE:
            if count >= 1000:
                return "epic"
            elif count >= 100:
                return "special"
            elif count >= 10:
                return "standard"
            else:
                return "minimal"
        
        elif milestone_type == MilestoneType.ENGAGEMENT_MILESTONE:
            if count >= 100000:
                return "epic"
            elif count >= 10000:
                return "special"
            elif count >= 1000:
                return "standard"
            else:
                return "minimal"
        
        else:
            return "standard"
    
    async def _celebrate_milestone(self, milestone: Milestone) -> Dict[str, Any]:
        """Execute milestone celebration"""
        
        celebration_elements = []
        
        # Determine celebration elements based on level
        if milestone.celebration_level == "epic":
            celebration_elements = [
                "animated_confetti_effect",
                "special_achievement_badge",
                "social_media_announcement",
                "personal_congratulations_video",
                "exclusive_feature_unlock",
                "leaderboard_highlight"
            ]
        
        elif milestone.celebration_level == "special":
            celebration_elements = [
                "confetti_effect",
                "achievement_badge",
                "community_announcement",
                "congratulations_message",
                "bonus_rewards"
            ]
        
        elif milestone.celebration_level == "standard":
            celebration_elements = [
                "celebration_popup",
                "achievement_notification",
                "congratulations_message"
            ]
        
        else:  # minimal
            celebration_elements = [
                "simple_notification",
                "achievement_recorded"
            ]
        
        # Execute celebration elements
        celebration_result = {
            "milestone_id": milestone.milestone_id,
            "celebration_level": milestone.celebration_level,
            "elements_triggered": celebration_elements,
            "celebration_timestamp": datetime.utcnow().isoformat(),
            "social_sharing_enabled": milestone.celebration_level in ["special", "epic"],
            "rewards_granted": await self._grant_milestone_rewards(milestone)
        }
        
        logger.info(f"Milestone celebrated: {milestone.title} with {milestone.celebration_level} level")
        
        return celebration_result
    
    async def _grant_milestone_rewards(self, milestone: Milestone) -> List[str]:
        """Grant rewards for milestone achievement"""
        
        rewards = []
        
        # Base rewards
        if milestone.celebration_level == "epic":
            rewards.extend(["1000_bonus_points", "epic_badge", "exclusive_feature_access"])
        elif milestone.celebration_level == "special":
            rewards.extend(["500_bonus_points", "special_badge", "premium_feature_trial"])
        elif milestone.celebration_level == "standard":
            rewards.extend(["200_bonus_points", "milestone_badge"])
        else:
            rewards.extend(["50_bonus_points"])
        
        # Type-specific rewards
        if milestone.milestone_type == MilestoneType.FOLLOWER_MILESTONE:
            rewards.append("social_boost_credit")
        elif milestone.milestone_type == MilestoneType.CONTENT_MILESTONE:
            rewards.append("content_enhancement_credit")
        elif milestone.milestone_type == MilestoneType.ENGAGEMENT_MILESTONE:
            rewards.append("engagement_analytics_access")
        
        return rewards
    
    async def _find_milestone(self, milestone_id: str) -> Optional[Milestone]:
        """Find milestone by ID"""
        
        for user_milestones in self.user_milestones.values():
            for milestone in user_milestones:
                if milestone.milestone_id == milestone_id:
                    return milestone
        
        return None
    
    async def _milestone_already_achieved(self, user_id: str, milestone_category: str, threshold: int) -> bool:
        """Check if milestone was already achieved"""
        
        user_milestones = self.user_milestones.get(user_id, [])
        
        for milestone in user_milestones:
            achievement_data = milestone.achievement_data
            if (achievement_data.get("category") == milestone_category and 
                achievement_data.get("count", 0) >= threshold):
                return True
        
        return False
    
    async def get_celebration_analytics(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Get analytics for milestone celebrations"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
        
        total_milestones = 0
        celebrated_milestones = 0
        celebration_levels = {}
        milestone_types = {}
        
        for user_milestones in self.user_milestones.values():
            for milestone in user_milestones:
                if milestone.achieved_at >= cutoff_date:
                    total_milestones += 1
                    
                    if milestone.celebrated:
                        celebrated_milestones += 1
                    
                    level = milestone.celebration_level
                    celebration_levels[level] = celebration_levels.get(level, 0) + 1
                    
                    milestone_type = milestone.milestone_type.value
                    milestone_types[milestone_type] = milestone_types.get(milestone_type, 0) + 1
        
        celebration_rate = (celebrated_milestones / total_milestones) * 100 if total_milestones > 0 else 0
        
        analytics = {
            "period_days": time_period_days,
            "total_milestones": total_milestones,
            "celebrated_milestones": celebrated_milestones,
            "celebration_rate_percentage": round(celebration_rate, 2),
            "celebration_levels": celebration_levels,
            "milestone_types": milestone_types,
            "average_milestones_per_day": total_milestones / time_period_days
        }
        
        return analytics