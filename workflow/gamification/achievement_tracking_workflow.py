"""Achievement Tracking Workflow - Advanced achievement detection and recognition system.

This module provides comprehensive achievement tracking capabilities including real-time detection,
progress monitoring, multi-tier recognition systems, and social sharing automation
for enhanced user engagement and motivation across the Ainflue Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

import asyncio
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import math


class AchievementType(Enum):
    """Achievement type classifications."""
    MILESTONE = "milestone"
    SKILL_BASED = "skill_based"
    ENGAGEMENT = "engagement"
    CONSISTENCY = "consistency"
    GROWTH = "growth"
    SOCIAL = "social"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    BUSINESS = "business"
    SPECIAL_EVENT = "special_event"


class AchievementTier(Enum):
    """Achievement tier levels."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"


class AchievementStatus(Enum):
    """Achievement completion status."""
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLAIMED = "claimed"
    EXPIRED = "expired"


class AchievementCategory(Enum):
    """Achievement category classifications."""
    CONTENT_CREATION = "content_creation"
    AUDIENCE_BUILDING = "audience_building"
    ENGAGEMENT_MASTERY = "engagement_mastery"
    TECHNICAL_SKILLS = "technical_skills"
    BUSINESS_GROWTH = "business_growth"
    COMMUNITY_LEADERSHIP = "community_leadership"
    INNOVATION = "innovation"
    COLLABORATION = "collaboration"


@dataclass
class AchievementCriteria:
    """Criteria for achievement completion."""
    metric_name: str
    target_value: float
    comparison_operator: str  # ">=", "<=", "==", "!=", ">", "<"
    time_window: Optional[int] = None  # Time window in days
    platform_specific: bool = False
    cumulative: bool = True
    verification_required: bool = False


@dataclass
class AchievementReward:
    """Reward for completing an achievement."""
    experience_points: int
    badge_id: Optional[str] = None
    premium_features: List[str] = field(default_factory=list)
    special_recognition: Optional[str] = None
    monetary_value: float = 0.0
    exclusive_content: List[str] = field(default_factory=list)


@dataclass
class Achievement:
    """Complete achievement definition."""
    id: str
    name: str
    description: str
    type: AchievementType
    tier: AchievementTier
    category: AchievementCategory
    criteria: List[AchievementCriteria]
    reward: AchievementReward
    icon_url: str
    unlock_requirements: List[str] = field(default_factory=list)
    is_secret: bool = False
    is_repeatable: bool = False
    expiration_date: Optional[datetime] = None
    platforms: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class AchievementProgress:
    """User progress toward an achievement."""
    achievement_id: str
    user_id: str
    status: AchievementStatus
    current_progress: Dict[str, float]
    progress_percentage: float
    started_date: datetime
    completed_date: Optional[datetime] = None
    claimed_date: Optional[datetime] = None
    verification_status: str = "pending"
    milestones_reached: List[str] = field(default_factory=list)


@dataclass
class AchievementEvent:
    """Achievement-related event for tracking."""
    user_id: str
    achievement_id: str
    event_type: str  # "unlocked", "progress", "completed", "claimed"
    event_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    platform: str = "ainflue"
    verification_required: bool = False


class AchievementTrackingWorkflow:
    """Advanced achievement tracking workflow with real-time detection and progress monitoring."""
    
    def __init__(self):
        """Initialize the achievement tracking workflow."""
        self.achievement_registry = {}
        self.user_progress = {}
        self.achievement_events = []
        
        # Initialize default achievements
        self._initialize_default_achievements()
        
        # Progress tracking thresholds
        self.milestone_thresholds = {
            "followers": [100, 500, 1000, 5000, 10000, 50000, 100000],
            "content_created": [10, 50, 100, 500, 1000, 5000],
            "engagement_rate": [1.0, 2.5, 5.0, 7.5, 10.0, 15.0],
            "streak_days": [7, 30, 90, 180, 365],
            "collaborations": [1, 5, 10, 25, 50],
            "revenue_generated": [100, 1000, 5000, 10000, 50000]
        }
    
    async def execute(self, user_data: Dict[str, Any], config: Any) -> Dict[str, Any]:
        """Execute achievement tracking workflow.
        
        Args:
            user_data: User activity and profile data
            config: Workflow configuration
            
        Returns:
            Achievement tracking results and progress updates
        """
        try:
            user_id = user_data.get("user_id", "")
            activity_data = user_data.get("activity_data", {})
            
            if not user_id:
                raise ValueError("User ID is required for achievement tracking")
            
            # Step 1: Update user metrics from activity data
            await self._update_user_metrics(user_id, activity_data)
            
            # Step 2: Check for achievement progress updates
            progress_updates = await self._check_achievement_progress(user_id, activity_data)
            
            # Step 3: Detect newly completed achievements
            completed_achievements = await self._detect_completed_achievements(user_id)
            
            # Step 4: Process achievement unlocks and rewards
            unlocked_achievements = await self._process_achievement_unlocks(
                user_id, completed_achievements
            )
            
            # Step 5: Generate achievement recommendations
            recommendations = await self._generate_achievement_recommendations(
                user_id, activity_data
            )
            
            # Step 6: Calculate overall achievement score
            achievement_score = await self._calculate_achievement_score(user_id)
            
            # Step 7: Create social sharing opportunities
            social_events = await self._create_social_sharing_events(
                user_id, unlocked_achievements
            )
            
            return {
                "status": "completed",
                "user_id": user_id,
                "achievement_score": achievement_score,
                "progress_updates": progress_updates,
                "completed_achievements": completed_achievements,
                "unlocked_achievements": unlocked_achievements,
                "achievements_unlocked": [a["id"] for a in unlocked_achievements],
                "recommendations": recommendations,
                "social_events": social_events,
                "user_progression": {
                    "total_achievements": len(self._get_user_achievements(user_id)),
                    "completion_rate": self._calculate_completion_rate(user_id),
                    "tier_distribution": self._get_tier_distribution(user_id),
                    "next_milestones": self._get_next_milestones(user_id)
                },
                "metrics": {
                    "achievements_in_progress": len(progress_updates),
                    "achievements_completed_today": len([a for a in completed_achievements if self._is_today(a.get("completed_date"))]),
                    "total_experience_earned": self._calculate_total_experience(user_id),
                    "achievement_streak": self._calculate_achievement_streak(user_id)
                }
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "user_id": user_data.get("user_id", ""),
                "achievements_unlocked": [],
                "metrics": {}
            }
    
    async def _update_user_metrics(self, user_id: str, activity_data: Dict[str, Any]) -> None:
        """Update user metrics from activity data."""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {"metrics": {}, "achievements": {}}
        
        # Update metrics from activity data
        metrics = self.user_progress[user_id]["metrics"]
        
        # Content creation metrics
        if "content_created" in activity_data:
            metrics["content_created"] = metrics.get("content_created", 0) + activity_data["content_created"]
        
        # Engagement metrics
        if "views" in activity_data:
            metrics["total_views"] = metrics.get("total_views", 0) + activity_data["views"]
        if "likes" in activity_data:
            metrics["total_likes"] = metrics.get("total_likes", 0) + activity_data["likes"]
        if "comments" in activity_data:
            metrics["total_comments"] = metrics.get("total_comments", 0) + activity_data["comments"]
        
        # Follower metrics
        if "followers" in activity_data:
            metrics["followers"] = activity_data["followers"]
        if "new_followers" in activity_data:
            metrics["followers_gained"] = metrics.get("followers_gained", 0) + activity_data["new_followers"]
        
        # Engagement rate calculation
        if "views" in activity_data and "likes" in activity_data and activity_data["views"] > 0:
            recent_engagement_rate = (activity_data["likes"] + activity_data.get("comments", 0)) / activity_data["views"] * 100
            metrics["avg_engagement_rate"] = self._update_average(
                metrics.get("avg_engagement_rate", 0), recent_engagement_rate, metrics.get("content_created", 1)
            )
        
        # Collaboration metrics
        if "collaborations" in activity_data:
            metrics["collaborations"] = metrics.get("collaborations", 0) + activity_data["collaborations"]
        
        # Revenue metrics
        if "revenue" in activity_data:
            metrics["total_revenue"] = metrics.get("total_revenue", 0) + activity_data["revenue"]
        
        # Streak tracking
        if activity_data.get("daily_activity", False):
            self._update_activity_streak(user_id)
    
    async def _check_achievement_progress(
        self, 
        user_id: str, 
        activity_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check and update progress for all relevant achievements."""
        progress_updates = []
        user_metrics = self.user_progress.get(user_id, {}).get("metrics", {})
        
        for achievement_id, achievement in self.achievement_registry.items():
            # Skip if user already completed this achievement (and it's not repeatable)
            if not achievement.is_repeatable and self._is_achievement_completed(user_id, achievement_id):
                continue
            
            # Check if user meets unlock requirements
            if not self._meets_unlock_requirements(user_id, achievement.unlock_requirements):
                continue
            
            # Check criteria progress
            current_progress = {}
            all_criteria_met = True
            
            for criteria in achievement.criteria:
                metric_value = user_metrics.get(criteria.metric_name, 0)
                
                # Apply time window filtering if specified
                if criteria.time_window:
                    metric_value = self._get_metric_in_time_window(
                        user_id, criteria.metric_name, criteria.time_window
                    )
                
                current_progress[criteria.metric_name] = metric_value
                
                # Check if criteria is met
                criteria_met = self._evaluate_criteria(metric_value, criteria)
                if not criteria_met:
                    all_criteria_met = False
            
            # Calculate progress percentage
            progress_percentage = self._calculate_progress_percentage(achievement, current_progress)
            
            # Update or create progress record
            if achievement_id not in self.user_progress[user_id]["achievements"]:
                self.user_progress[user_id]["achievements"][achievement_id] = AchievementProgress(
                    achievement_id=achievement_id,
                    user_id=user_id,
                    status=AchievementStatus.IN_PROGRESS,
                    current_progress=current_progress,
                    progress_percentage=progress_percentage,
                    started_date=datetime.now()
                )
            else:
                # Update existing progress
                progress_record = self.user_progress[user_id]["achievements"][achievement_id]
                progress_record.current_progress = current_progress
                progress_record.progress_percentage = progress_percentage
                
                # Check for milestone progress
                new_milestones = self._check_milestone_progress(achievement, progress_record)
                if new_milestones:
                    progress_record.milestones_reached.extend(new_milestones)
            
            # Add to progress updates if there was meaningful progress
            if progress_percentage > 0:
                progress_updates.append({
                    "achievement_id": achievement_id,
                    "achievement_name": achievement.name,
                    "progress_percentage": progress_percentage,
                    "current_progress": current_progress,
                    "criteria_met": all_criteria_met,
                    "milestones_reached": self.user_progress[user_id]["achievements"][achievement_id].milestones_reached
                })
        
        return progress_updates
    
    async def _detect_completed_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Detect achievements that have been completed."""
        completed_achievements = []
        user_achievements = self.user_progress.get(user_id, {}).get("achievements", {})
        
        for achievement_id, progress in user_achievements.items():
            if progress.status == AchievementStatus.IN_PROGRESS:
                achievement = self.achievement_registry[achievement_id]
                
                # Check if all criteria are now met
                all_criteria_met = True
                for criteria in achievement.criteria:
                    metric_value = progress.current_progress.get(criteria.metric_name, 0)
                    if not self._evaluate_criteria(metric_value, criteria):
                        all_criteria_met = False
                        break
                
                if all_criteria_met:
                    # Mark as completed
                    progress.status = AchievementStatus.COMPLETED
                    progress.completed_date = datetime.now()
                    
                    completed_achievements.append({
                        "achievement_id": achievement_id,
                        "achievement": achievement,
                        "completed_date": progress.completed_date,
                        "progress": progress
                    })
                    
                    # Create achievement event
                    self._create_achievement_event(
                        user_id, achievement_id, "completed", 
                        {"completion_time": progress.completed_date.isoformat()}
                    )
        
        return completed_achievements
    
    async def _process_achievement_unlocks(
        self, 
        user_id: str, 
        completed_achievements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process newly unlocked achievements and distribute rewards."""
        unlocked_achievements = []
        
        for completed in completed_achievements:
            achievement = completed["achievement"]
            progress = completed["progress"]
            
            # Distribute rewards
            reward_details = await self._distribute_achievement_reward(
                user_id, achievement.reward
            )
            
            # Update progress status to claimed
            progress.status = AchievementStatus.CLAIMED
            progress.claimed_date = datetime.now()
            
            unlocked_achievements.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "tier": achievement.tier.value,
                "type": achievement.type.value,
                "category": achievement.category.value,
                "reward": reward_details,
                "completed_date": progress.completed_date,
                "claimed_date": progress.claimed_date,
                "icon_url": achievement.icon_url
            })
            
            # Create unlock event
            self._create_achievement_event(
                user_id, achievement.id, "unlocked",
                {"reward": reward_details, "tier": achievement.tier.value}
            )
        
        return unlocked_achievements
    
    async def _generate_achievement_recommendations(
        self, 
        user_id: str, 
        activity_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized achievement recommendations."""
        recommendations = []
        user_metrics = self.user_progress.get(user_id, {}).get("metrics", {})
        user_achievements = self.user_progress.get(user_id, {}).get("achievements", {})
        
        # Find achievements that are close to completion (70%+ progress)
        for achievement_id, achievement in self.achievement_registry.items():
            if achievement_id in user_achievements:
                progress = user_achievements[achievement_id]
                if progress.status == AchievementStatus.IN_PROGRESS and progress.progress_percentage >= 70:
                    recommendations.append({
                        "type": "close_to_completion",
                        "achievement_id": achievement_id,
                        "achievement_name": achievement.name,
                        "progress_percentage": progress.progress_percentage,
                        "estimated_completion_time": self._estimate_completion_time(achievement, progress),
                        "priority": "high",
                        "action": f"Continue working towards {achievement.name} - you're {progress.progress_percentage:.1f}% there!"
                    })
        
        # Recommend achievements based on user's strong metrics
        strong_metrics = self._identify_strong_metrics(user_metrics)
        for metric in strong_metrics:
            relevant_achievements = self._find_achievements_by_metric(metric)
            for achievement in relevant_achievements[:2]:  # Top 2 per metric
                if achievement.id not in user_achievements:
                    recommendations.append({
                        "type": "strength_based",
                        "achievement_id": achievement.id,
                        "achievement_name": achievement.name,
                        "related_metric": metric,
                        "priority": "medium",
                        "action": f"Try earning {achievement.name} - you're already strong in {metric}!"
                    })
        
        # Recommend achievements for weak areas (growth opportunities)
        weak_metrics = self._identify_weak_metrics(user_metrics)
        for metric in weak_metrics[:2]:  # Focus on top 2 weak areas
            beginner_achievements = self._find_beginner_achievements_by_metric(metric)
            for achievement in beginner_achievements[:1]:  # One per weak metric
                if achievement.id not in user_achievements:
                    recommendations.append({
                        "type": "growth_opportunity",
                        "achievement_id": achievement.id,
                        "achievement_name": achievement.name,
                        "related_metric": metric,
                        "priority": "low",
                        "action": f"Work on {achievement.name} to improve your {metric} skills!"
                    })
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def _calculate_achievement_score(self, user_id: str) -> float:
        """Calculate overall achievement score for the user."""
        user_achievements = self.user_progress.get(user_id, {}).get("achievements", {})
        
        total_score = 0.0
        completed_count = 0
        
        for achievement_id, progress in user_achievements.items():
            if progress.status in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]:
                achievement = self.achievement_registry[achievement_id]
                
                # Base score from tier
                tier_multipliers = {
                    AchievementTier.BRONZE: 1.0,
                    AchievementTier.SILVER: 2.0,
                    AchievementTier.GOLD: 3.0,
                    AchievementTier.PLATINUM: 5.0,
                    AchievementTier.DIAMOND: 8.0,
                    AchievementTier.LEGENDARY: 15.0
                }
                
                tier_score = tier_multipliers.get(achievement.tier, 1.0) * 100
                total_score += tier_score
                completed_count += 1
        
        # Add bonus for diversity (completing achievements across different categories)
        categories_completed = set()
        for achievement_id, progress in user_achievements.items():
            if progress.status in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]:
                achievement = self.achievement_registry[achievement_id]
                categories_completed.add(achievement.category)
        
        diversity_bonus = len(categories_completed) * 50
        
        return total_score + diversity_bonus
    
    async def _create_social_sharing_events(
        self, 
        user_id: str, 
        unlocked_achievements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create social sharing opportunities for unlocked achievements."""
        social_events = []
        
        for achievement in unlocked_achievements:
            # Create different sharing options based on tier and type
            sharing_templates = self._generate_sharing_templates(achievement)
            
            social_events.append({
                "type": "achievement_unlock",
                "achievement_id": achievement["id"],
                "achievement_name": achievement["name"],
                "achievement_tier": achievement["tier"],
                "sharing_templates": sharing_templates,
                "auto_share_recommended": achievement["tier"] in ["gold", "platinum", "diamond", "legendary"],
                "platforms": ["twitter", "linkedin", "instagram", "facebook"]
            })
        
        return social_events
    
    def _initialize_default_achievements(self) -> None:
        """Initialize default achievement definitions."""
        default_achievements = [
            # Content Creation Achievements
            Achievement(
                id="first_content",
                name="First Steps",
                description="Create your first piece of content",
                type=AchievementType.MILESTONE,
                tier=AchievementTier.BRONZE,
                category=AchievementCategory.CONTENT_CREATION,
                criteria=[AchievementCriteria("content_created", 1, ">=")],
                reward=AchievementReward(experience_points=100, badge_id="creator_badge"),
                icon_url="/icons/first_content.svg"
            ),
            
            Achievement(
                id="content_creator_10",
                name="Content Creator",
                description="Create 10 pieces of content",
                type=AchievementType.MILESTONE,
                tier=AchievementTier.SILVER,
                category=AchievementCategory.CONTENT_CREATION,
                criteria=[AchievementCriteria("content_created", 10, ">=")],
                reward=AchievementReward(experience_points=500, badge_id="creator_silver"),
                icon_url="/icons/content_creator_10.svg"
            ),
            
            Achievement(
                id="prolific_creator",
                name="Prolific Creator",
                description="Create 100 pieces of content",
                type=AchievementType.MILESTONE,
                tier=AchievementTier.GOLD,
                category=AchievementCategory.CONTENT_CREATION,
                criteria=[AchievementCriteria("content_created", 100, ">=")],
                reward=AchievementReward(experience_points=2000, badge_id="creator_gold", premium_features=["advanced_analytics"]),
                icon_url="/icons/prolific_creator.svg"
            ),
            
            # Engagement Achievements
            Achievement(
                id="engagement_master",
                name="Engagement Master",
                description="Maintain 5% engagement rate for 30 days",
                type=AchievementType.SKILL_BASED,
                tier=AchievementTier.GOLD,
                category=AchievementCategory.ENGAGEMENT_MASTERY,
                criteria=[
                    AchievementCriteria("avg_engagement_rate", 5.0, ">=", time_window=30),
                    AchievementCriteria("content_created", 10, ">=", time_window=30)
                ],
                reward=AchievementReward(experience_points=1500, special_recognition="Engagement Expert"),
                icon_url="/icons/engagement_master.svg"
            ),
            
            # Growth Achievements
            Achievement(
                id="growing_audience_1k",
                name="Growing Audience",
                description="Reach 1,000 followers",
                type=AchievementType.GROWTH,
                tier=AchievementTier.SILVER,
                category=AchievementCategory.AUDIENCE_BUILDING,
                criteria=[AchievementCriteria("followers", 1000, ">=")],
                reward=AchievementReward(experience_points=1000, badge_id="audience_builder"),
                icon_url="/icons/growing_audience.svg"
            ),
            
            Achievement(
                id="viral_sensation",
                name="Viral Sensation",
                description="Get 100,000 views on a single piece of content",
                type=AchievementType.MILESTONE,
                tier=AchievementTier.PLATINUM,
                category=AchievementCategory.CONTENT_CREATION,
                criteria=[AchievementCriteria("max_single_content_views", 100000, ">=")],
                reward=AchievementReward(experience_points=5000, badge_id="viral_star", monetary_value=100),
                icon_url="/icons/viral_sensation.svg"
            ),
            
            # Consistency Achievements
            Achievement(
                id="consistent_creator_7",
                name="Consistent Creator",
                description="Create content for 7 days in a row",
                type=AchievementType.CONSISTENCY,
                tier=AchievementTier.BRONZE,
                category=AchievementCategory.CONTENT_CREATION,
                criteria=[AchievementCriteria("content_streak_days", 7, ">=")],
                reward=AchievementReward(experience_points=300, badge_id="consistent_bronze"),
                icon_url="/icons/consistent_7.svg"
            ),
            
            Achievement(
                id="dedication_master",
                name="Dedication Master",
                description="Create content for 30 days in a row",
                type=AchievementType.CONSISTENCY,
                tier=AchievementTier.GOLD,
                category=AchievementCategory.CONTENT_CREATION,
                criteria=[AchievementCriteria("content_streak_days", 30, ">=")],
                reward=AchievementReward(experience_points=2000, badge_id="dedicated_creator", premium_features=["priority_support"]),
                icon_url="/icons/dedication_master.svg"
            ),
            
            # Social Achievements
            Achievement(
                id="community_builder",
                name="Community Builder",
                description="Collaborate with 5 different creators",
                type=AchievementType.SOCIAL,
                tier=AchievementTier.SILVER,
                category=AchievementCategory.COLLABORATION,
                criteria=[AchievementCriteria("collaborations", 5, ">=")],
                reward=AchievementReward(experience_points=800, badge_id="collaborator"),
                icon_url="/icons/community_builder.svg"
            ),
            
            # Business Achievements
            Achievement(
                id="first_earnings",
                name="First Earnings",
                description="Earn your first $100 through the platform",
                type=AchievementType.BUSINESS,
                tier=AchievementTier.SILVER,
                category=AchievementCategory.BUSINESS_GROWTH,
                criteria=[AchievementCriteria("total_revenue", 100, ">=")],
                reward=AchievementReward(experience_points=1000, badge_id="entrepreneur", premium_features=["revenue_analytics"]),
                icon_url="/icons/first_earnings.svg"
            )
        ]
        
        # Register achievements
        for achievement in default_achievements:
            self.achievement_registry[achievement.id] = achievement
    
    # Helper methods
    
    def _update_average(self, current_avg: float, new_value: float, count: int) -> float:
        """Update running average with new value."""
        return (current_avg * (count - 1) + new_value) / count
    
    def _update_activity_streak(self, user_id: str) -> None:
        """Update user's activity streak."""
        metrics = self.user_progress[user_id]["metrics"]
        last_activity = metrics.get("last_activity_date")
        today = datetime.now().date()
        
        if last_activity is None or last_activity != today:
            if last_activity == today - timedelta(days=1):
                # Continue streak
                metrics["content_streak_days"] = metrics.get("content_streak_days", 0) + 1
            else:
                # Reset streak
                metrics["content_streak_days"] = 1
            
            metrics["last_activity_date"] = today
    
    def _is_achievement_completed(self, user_id: str, achievement_id: str) -> bool:
        """Check if user has completed an achievement."""
        user_achievements = self.user_progress.get(user_id, {}).get("achievements", {})
        if achievement_id not in user_achievements:
            return False
        
        status = user_achievements[achievement_id].status
        return status in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]
    
    def _meets_unlock_requirements(self, user_id: str, requirements: List[str]) -> bool:
        """Check if user meets achievement unlock requirements."""
        if not requirements:
            return True
        
        for requirement in requirements:
            if not self._is_achievement_completed(user_id, requirement):
                return False
        
        return True
    
    def _get_metric_in_time_window(self, user_id: str, metric_name: str, days: int) -> float:
        """Get metric value within specified time window."""
        # Simplified implementation - in real system would track time-series data
        user_metrics = self.user_progress.get(user_id, {}).get("metrics", {})
        return user_metrics.get(metric_name, 0)
    
    def _evaluate_criteria(self, value: float, criteria: AchievementCriteria) -> bool:
        """Evaluate if a criteria is met."""
        target = criteria.target_value
        op = criteria.comparison_operator
        
        if op == ">=":
            return value >= target
        elif op == "<=":
            return value <= target
        elif op == "==":
            return value == target
        elif op == "!=":
            return value != target
        elif op == ">":
            return value > target
        elif op == "<":
            return value < target
        else:
            return False
    
    def _calculate_progress_percentage(self, achievement: Achievement, current_progress: Dict[str, float]) -> float:
        """Calculate overall progress percentage for an achievement."""
        if not achievement.criteria:
            return 0.0
        
        total_progress = 0.0
        for criteria in achievement.criteria:
            current_value = current_progress.get(criteria.metric_name, 0)
            target_value = criteria.target_value
            
            if target_value > 0:
                criteria_progress = min(100.0, (current_value / target_value) * 100)
            else:
                criteria_progress = 100.0 if current_value == target_value else 0.0
            
            total_progress += criteria_progress
        
        return total_progress / len(achievement.criteria)
    
    def _check_milestone_progress(self, achievement: Achievement, progress: AchievementProgress) -> List[str]:
        """Check for milestone progress within an achievement."""
        milestones = []
        
        # Check if user reached 25%, 50%, 75% progress for the first time
        thresholds = [25, 50, 75]
        
        for threshold in thresholds:
            milestone_key = f"{achievement.id}_{threshold}%"
            if (progress.progress_percentage >= threshold and 
                milestone_key not in progress.milestones_reached):
                milestones.append(milestone_key)
        
        return milestones
    
    async def _distribute_achievement_reward(self, user_id: str, reward: AchievementReward) -> Dict[str, Any]:
        """Distribute rewards for completed achievement."""
        reward_details = {
            "experience_points": reward.experience_points,
            "badge_id": reward.badge_id,
            "premium_features": reward.premium_features,
            "special_recognition": reward.special_recognition,
            "monetary_value": reward.monetary_value,
            "exclusive_content": reward.exclusive_content
        }
        
        # Update user's total experience
        user_metrics = self.user_progress[user_id]["metrics"]
        user_metrics["total_experience"] = user_metrics.get("total_experience", 0) + reward.experience_points
        
        return reward_details
    
    def _estimate_completion_time(self, achievement: Achievement, progress: AchievementProgress) -> str:
        """Estimate time to complete achievement based on current progress."""
        if progress.progress_percentage >= 90:
            return "1-2 days"
        elif progress.progress_percentage >= 70:
            return "3-7 days"
        elif progress.progress_percentage >= 50:
            return "1-2 weeks"
        else:
            return "2-4 weeks"
    
    def _identify_strong_metrics(self, user_metrics: Dict[str, float]) -> List[str]:
        """Identify user's strongest performance metrics."""
        # Simplified scoring based on relative performance
        strong_metrics = []
        
        if user_metrics.get("avg_engagement_rate", 0) > 3.0:
            strong_metrics.append("engagement")
        if user_metrics.get("followers", 0) > 1000:
            strong_metrics.append("audience_building")
        if user_metrics.get("content_created", 0) > 50:
            strong_metrics.append("content_creation")
        if user_metrics.get("collaborations", 0) > 3:
            strong_metrics.append("collaboration")
        
        return strong_metrics
    
    def _identify_weak_metrics(self, user_metrics: Dict[str, float]) -> List[str]:
        """Identify areas where user could improve."""
        weak_metrics = []
        
        if user_metrics.get("avg_engagement_rate", 0) < 1.0:
            weak_metrics.append("engagement")
        if user_metrics.get("followers", 0) < 100:
            weak_metrics.append("audience_building")
        if user_metrics.get("collaborations", 0) == 0:
            weak_metrics.append("collaboration")
        if user_metrics.get("total_revenue", 0) == 0:
            weak_metrics.append("monetization")
        
        return weak_metrics
    
    def _find_achievements_by_metric(self, metric: str) -> List[Achievement]:
        """Find achievements related to a specific metric."""
        related_achievements = []
        
        metric_mappings = {
            "engagement": ["engagement_rate", "likes", "comments"],
            "content_creation": ["content_created"],
            "audience_building": ["followers", "followers_gained"],
            "collaboration": ["collaborations"],
            "monetization": ["revenue", "total_revenue"]
        }
        
        relevant_metrics = metric_mappings.get(metric, [metric])
        
        for achievement in self.achievement_registry.values():
            for criteria in achievement.criteria:
                if any(m in criteria.metric_name for m in relevant_metrics):
                    related_achievements.append(achievement)
                    break
        
        return related_achievements
    
    def _find_beginner_achievements_by_metric(self, metric: str) -> List[Achievement]:
        """Find beginner-level achievements for a metric."""
        achievements = self._find_achievements_by_metric(metric)
        return [a for a in achievements if a.tier in [AchievementTier.BRONZE, AchievementTier.SILVER]]
    
    def _generate_sharing_templates(self, achievement: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate social sharing templates for achievement."""
        templates = []
        
        # Twitter template
        templates.append({
            "platform": "twitter",
            "template": f"🏆 Just unlocked '{achievement['name']}' on @AinfluePlatform! {achievement['description']} #Achievement #{achievement['tier'].title()}Tier #CreatorLife"
        })
        
        # LinkedIn template
        templates.append({
            "platform": "linkedin",
            "template": f"Excited to share that I've achieved '{achievement['name']}' on Ainflue Platform! {achievement['description']} This milestone represents my commitment to growing as a content creator. #ContentCreator #Achievement"
        })
        
        # Instagram template
        templates.append({
            "platform": "instagram",
            "template": f"🎉 Achievement unlocked: {achievement['name']}! {achievement['description']} #Achievement #CreatorJourney #Ainflue #{achievement['tier'].title()}Tier"
        })
        
        return templates
    
    def _create_achievement_event(self, user_id: str, achievement_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """Create an achievement event for tracking."""
        event = AchievementEvent(
            user_id=user_id,
            achievement_id=achievement_id,
            event_type=event_type,
            event_data=event_data
        )
        self.achievement_events.append(event)
    
    def _get_user_achievements(self, user_id: str) -> Dict[str, AchievementProgress]:
        """Get all achievements for a user."""
        return self.user_progress.get(user_id, {}).get("achievements", {})
    
    def _calculate_completion_rate(self, user_id: str) -> float:
        """Calculate user's achievement completion rate."""
        user_achievements = self._get_user_achievements(user_id)
        total_achievements = len(self.achievement_registry)
        completed_achievements = len([
            a for a in user_achievements.values() 
            if a.status in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]
        ])
        
        return (completed_achievements / total_achievements) * 100 if total_achievements > 0 else 0.0
    
    def _get_tier_distribution(self, user_id: str) -> Dict[str, int]:
        """Get distribution of achievements by tier."""
        user_achievements = self._get_user_achievements(user_id)
        tier_distribution = {tier.value: 0 for tier in AchievementTier}
        
        for progress in user_achievements.values():
            if progress.status in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]:
                achievement = self.achievement_registry[progress.achievement_id]
                tier_distribution[achievement.tier.value] += 1
        
        return tier_distribution
    
    def _get_next_milestones(self, user_id: str) -> List[str]:
        """Get next upcoming milestones for user."""
        user_achievements = self._get_user_achievements(user_id)
        next_milestones = []
        
        # Find achievements with 50%+ progress
        for progress in user_achievements.values():
            if (progress.status == AchievementStatus.IN_PROGRESS and 
                progress.progress_percentage >= 50):
                achievement = self.achievement_registry[progress.achievement_id]
                next_milestones.append(f"{achievement.name} ({progress.progress_percentage:.1f}%)")
        
        return next_milestones[:5]
    
    def _is_today(self, date: Optional[datetime]) -> bool:
        """Check if date is today."""
        if date is None:
            return False
        return date.date() == datetime.now().date()
    
    def _calculate_total_experience(self, user_id: str) -> int:
        """Calculate total experience points earned by user."""
        user_metrics = self.user_progress.get(user_id, {}).get("metrics", {})
        return user_metrics.get("total_experience", 0)
    
    def _calculate_achievement_streak(self, user_id: str) -> int:
        """Calculate user's achievement earning streak."""
        # Simplified implementation - would track actual achievement dates
        user_achievements = self._get_user_achievements(user_id)
        recent_achievements = [
            a for a in user_achievements.values()
            if (a.status in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED] and
                a.completed_date and 
                (datetime.now() - a.completed_date).days <= 7)
        ]
        return len(recent_achievements)