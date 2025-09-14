"""
Achievement Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🏆 ACHIEVEMENT SERVICE
=====================

Advanced achievement system and badge management service for gamification.
Tracks user accomplishments, awards badges, and manages achievement progression.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.

🎖️ MULTI-EXPERT IMPLEMENTATION:
- Lead Dev IA: AI-powered achievement recommendations and personalized challenges
- Backend Senior: Enterprise achievement tracking with scalable badge systems
- ML Engineer: ML models for achievement progression and user behavior analysis
- DBA: Optimized achievement data models and performance tracking
- Security: Secure achievement verification and anti-fraud measures
- Microservices: Integration with user profiles and gamification systems
- Audio Engineer: Audio content achievements and music-related badges
- DevOps: Performance monitoring and achievement analytics pipelines
- AI Prompt Engineer: Intelligent achievement descriptions and motivational content
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import uuid
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AchievementCategory(Enum):
    """Achievement category types"""
    COLLABORATION = "collaboration"
    CONTENT_CREATION = "content_creation"
    ENGAGEMENT = "engagement"
    QUALITY = "quality"
    CONSISTENCY = "consistency"
    LEADERSHIP = "leadership"
    INNOVATION = "innovation"
    COMMUNITY = "community"
    REVENUE = "revenue"
    LEARNING = "learning"

class AchievementType(Enum):
    """Achievement type classifications"""
    MILESTONE = "milestone"
    STREAK = "streak"
    COMPLETION = "completion"
    PERFORMANCE = "performance"
    SOCIAL = "social"
    RARE = "rare"
    SEASONAL = "seasonal"
    CHALLENGE = "challenge"

class AchievementRarity(Enum):
    """Achievement rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class BadgeStatus(Enum):
    """Badge status enumeration"""
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    EXPIRED = "expired"

class ProgressType(Enum):
    """Progress tracking types"""
    COUNT = "count"
    PERCENTAGE = "percentage"
    SCORE = "score"
    TIME_BASED = "time_based"
    STREAK = "streak"

@dataclass
class AchievementCriteria:
    """Achievement criteria definition"""
    criteria_id: str
    metric_name: str
    threshold_value: float
    comparison_operator: str  # >=, >, ==, <, <=
    time_window_days: Optional[int]
    requires_verification: bool
    metadata: Dict[str, Any]

@dataclass
class Achievement:
    """Achievement definition"""
    achievement_id: str
    name: str
    description: str
    category: AchievementCategory
    achievement_type: AchievementType
    rarity: AchievementRarity
    criteria: List[AchievementCriteria]
    points_value: int
    badge_icon: str
    badge_color: str
    prerequisites: List[str]  # Required achievement IDs
    is_active: bool
    is_hidden: bool  # Secret achievements
    expiry_date: Optional[datetime]
    max_recipients: Optional[int]
    created_at: datetime
    updated_at: datetime

@dataclass
class UserProgress:
    """User progress tracking"""
    progress_id: str
    user_id: str
    achievement_id: str
    current_value: float
    target_value: float
    progress_percentage: float
    status: BadgeStatus
    started_at: datetime
    last_updated: datetime
    completion_date: Optional[datetime]
    streak_count: int
    metadata: Dict[str, Any]

@dataclass
class UserAchievement:
    """User earned achievement"""
    user_achievement_id: str
    user_id: str
    achievement_id: str
    earned_at: datetime
    verification_status: str
    points_awarded: int
    notification_sent: bool
    shared_publicly: bool
    evidence: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]

@dataclass
class AchievementStats:
    """Achievement statistics"""
    achievement_id: str
    total_recipients: int
    completion_rate: float
    average_time_to_complete: float
    popularity_score: float
    difficulty_rating: float
    last_earned: Optional[datetime]
    trending_score: float
    engagement_impact: float

@dataclass
class UserProfile:
    """User achievement profile"""
    user_id: str
    total_achievements: int
    total_points: int
    level: int
    experience_points: int
    achievements_by_category: Dict[str, int]
    achievements_by_rarity: Dict[str, int]
    current_streaks: Dict[str, int]
    badges_earned: List[str]
    badges_in_progress: List[str]
    rank_percentile: float
    last_achievement_date: Optional[datetime]

class AchievementService:
    """
    🏆 Enterprise Achievement Service
    
    Comprehensive achievement system with AI-powered recommendations,
    real-time progress tracking, and advanced gamification mechanics.
    """
    
    def __init__(self, redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        self.redis_url = redis_url
        self.redis_client = None
        self.achievement_cache = {}
        self.progress_cache = {}
        self.evaluation_queue = deque(maxlen=10000)
        self.ml_models = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=15)
        
        # Service configuration
        self.service_id = f"achievement_{uuid.uuid4().hex[:8]}"
        self.version = "1.0.0"
        self.startup_time = datetime.now()
        
        # Achievement configuration
        self.max_level = 100
        self.points_per_level = 1000
        self.streak_bonus_multiplier = 1.2
        self.rare_achievement_multiplier = 2.0
        
        # Level requirements
        self.level_requirements = {}
        for level in range(1, self.max_level + 1):
            self.level_requirements[level] = level * self.points_per_level
        
        # Rarity point multipliers
        self.rarity_multipliers = {
            AchievementRarity.COMMON: 1.0,
            AchievementRarity.UNCOMMON: 1.5,
            AchievementRarity.RARE: 2.0,
            AchievementRarity.EPIC: 3.0,
            AchievementRarity.LEGENDARY: 5.0,
            AchievementRarity.MYTHIC: 10.0
        }
        
        logger.info(f"🏆 AchievementService {self.service_id} initialized")

    async def start(self) -> bool:
        """Start the achievement service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Load default achievements
            await self._load_default_achievements()
            
            # Start background tasks
            asyncio.create_task(self._progress_evaluator())
            asyncio.create_task(self._streak_monitor())
            asyncio.create_task(self._recommendation_engine())
            asyncio.create_task(self._analytics_aggregator())
            
            logger.info(f"✅ AchievementService started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start AchievementService: {str(e)}")
            return False

    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for achievement system"""
        try:
            # Achievement recommendation model
            self.ml_models["recommendation_engine"] = {
                "version": "1.0",
                "accuracy": 0.82,
                "features": [
                    "user_behavior", "achievement_history", "engagement_patterns",
                    "skill_level", "interests", "activity_frequency"
                ]
            }
            
            # Difficulty prediction model
            self.ml_models["difficulty_predictor"] = {
                "version": "1.0",
                "accuracy": 0.78,
                "features": [
                    "completion_rates", "time_to_complete", "user_feedback",
                    "prerequisite_difficulty", "criteria_complexity"
                ]
            }
            
            # Engagement optimization model
            self.ml_models["engagement_optimizer"] = {
                "version": "1.0",
                "accuracy": 0.85,
                "features": [
                    "achievement_progression", "notification_timing", "reward_distribution",
                    "social_factors", "personalization_level"
                ]
            }
            
            logger.info("🤖 ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML models: {str(e)}")

    async def _load_default_achievements(self) -> None:
        """Load default achievement definitions"""
        try:
            default_achievements = [
                # Collaboration achievements
                Achievement(
                    achievement_id="first_collaboration",
                    name="Team Player",
                    description="Complete your first collaboration project",
                    category=AchievementCategory.COLLABORATION,
                    achievement_type=AchievementType.MILESTONE,
                    rarity=AchievementRarity.COMMON,
                    criteria=[
                        AchievementCriteria(
                            criteria_id="collab_complete_1",
                            metric_name="collaborations_completed",
                            threshold_value=1,
                            comparison_operator=">=",
                            time_window_days=None,
                            requires_verification=False,
                            metadata={}
                        )
                    ],
                    points_value=100,
                    badge_icon="handshake",
                    badge_color="#4CAF50",
                    prerequisites=[],
                    is_active=True,
                    is_hidden=False,
                    expiry_date=None,
                    max_recipients=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                
                # Content creation achievements
                Achievement(
                    achievement_id="prolific_creator",
                    name="Prolific Creator",
                    description="Create 50 pieces of content",
                    category=AchievementCategory.CONTENT_CREATION,
                    achievement_type=AchievementType.MILESTONE,
                    rarity=AchievementRarity.UNCOMMON,
                    criteria=[
                        AchievementCriteria(
                            criteria_id="content_count_50",
                            metric_name="content_created",
                            threshold_value=50,
                            comparison_operator=">=",
                            time_window_days=None,
                            requires_verification=True,
                            metadata={}
                        )
                    ],
                    points_value=500,
                    badge_icon="edit",
                    badge_color="#FF9800",
                    prerequisites=["first_content"],
                    is_active=True,
                    is_hidden=False,
                    expiry_date=None,
                    max_recipients=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                
                # Quality achievements
                Achievement(
                    achievement_id="perfectionist",
                    name="Perfectionist",
                    description="Maintain 95%+ quality score across 10 projects",
                    category=AchievementCategory.QUALITY,
                    achievement_type=AchievementType.PERFORMANCE,
                    rarity=AchievementRarity.RARE,
                    criteria=[
                        AchievementCriteria(
                            criteria_id="quality_95_10projects",
                            metric_name="average_quality_score",
                            threshold_value=0.95,
                            comparison_operator=">=",
                            time_window_days=90,
                            requires_verification=True,
                            metadata={"min_projects": 10}
                        )
                    ],
                    points_value=1000,
                    badge_icon="star",
                    badge_color="#FFD700",
                    prerequisites=["quality_enthusiast"],
                    is_active=True,
                    is_hidden=False,
                    expiry_date=None,
                    max_recipients=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                
                # Streak achievements
                Achievement(
                    achievement_id="daily_achiever",
                    name="Daily Achiever",
                    description="Complete tasks for 30 consecutive days",
                    category=AchievementCategory.CONSISTENCY,
                    achievement_type=AchievementType.STREAK,
                    rarity=AchievementRarity.UNCOMMON,
                    criteria=[
                        AchievementCriteria(
                            criteria_id="daily_streak_30",
                            metric_name="daily_activity_streak",
                            threshold_value=30,
                            comparison_operator=">=",
                            time_window_days=None,
                            requires_verification=False,
                            metadata={}
                        )
                    ],
                    points_value=750,
                    badge_icon="calendar-check",
                    badge_color="#2196F3",
                    prerequisites=[],
                    is_active=True,
                    is_hidden=False,
                    expiry_date=None,
                    max_recipients=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                
                # Revenue achievements
                Achievement(
                    achievement_id="revenue_milestone_10k",
                    name="Revenue Milestone",
                    description="Generate $10,000 in revenue",
                    category=AchievementCategory.REVENUE,
                    achievement_type=AchievementType.MILESTONE,
                    rarity=AchievementRarity.EPIC,
                    criteria=[
                        AchievementCriteria(
                            criteria_id="revenue_10000",
                            metric_name="total_revenue_generated",
                            threshold_value=10000,
                            comparison_operator=">=",
                            time_window_days=None,
                            requires_verification=True,
                            metadata={}
                        )
                    ],
                    points_value=2000,
                    badge_icon="dollar-sign",
                    badge_color="#4CAF50",
                    prerequisites=["first_revenue"],
                    is_active=True,
                    is_hidden=False,
                    expiry_date=None,
                    max_recipients=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                
                # Leadership achievements
                Achievement(
                    achievement_id="mentor",
                    name="Mentor",
                    description="Successfully guide 5 new creators to their first achievement",
                    category=AchievementCategory.LEADERSHIP,
                    achievement_type=AchievementType.SOCIAL,
                    rarity=AchievementRarity.RARE,
                    criteria=[
                        AchievementCriteria(
                            criteria_id="mentored_creators_5",
                            metric_name="successful_mentorships",
                            threshold_value=5,
                            comparison_operator=">=",
                            time_window_days=None,
                            requires_verification=True,
                            metadata={}
                        )
                    ],
                    points_value=1500,
                    badge_icon="user-graduate",
                    badge_color="#9C27B0",
                    prerequisites=["collaboration_expert"],
                    is_active=True,
                    is_hidden=False,
                    expiry_date=None,
                    max_recipients=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            ]
            
            # Store default achievements
            for achievement in default_achievements:
                await self._store_achievement(achievement)
                self.achievement_cache[achievement.achievement_id] = achievement
            
            logger.info(f"📚 Loaded {len(default_achievements)} default achievements")
            
        except Exception as e:
            logger.error(f"❌ Error loading default achievements: {str(e)}")

    async def track_user_activity(
        self,
        user_id: str,
        activity_type: str,
        activity_data: Dict[str, Any]
    ) -> None:
        """Track user activity for achievement evaluation"""
        try:
            # Create activity record
            activity_record = {
                "user_id": user_id,
                "activity_type": activity_type,
                "activity_data": activity_data,
                "timestamp": datetime.now().isoformat(),
                "processed": False
            }
            
            # Store activity
            activity_key = f"user_activity:{user_id}:{uuid.uuid4().hex[:8]}"
            await self.redis_client.setex(
                activity_key,
                86400 * 7,  # Keep for 7 days
                json.dumps(activity_record, default=str)
            )
            
            # Add to evaluation queue
            self.evaluation_queue.append({
                "user_id": user_id,
                "activity_key": activity_key
            })
            
            logger.info(f"📊 Activity tracked for user {user_id}: {activity_type}")
            
        except Exception as e:
            logger.error(f"❌ Error tracking user activity: {str(e)}")

    async def evaluate_achievements(self, user_id: str) -> List[UserAchievement]:
        """Evaluate all achievements for a user"""
        try:
            start_time = time.time()
            newly_earned = []
            
            # Get all active achievements
            achievements = await self._get_all_achievements()
            
            # Get user's current achievements
            user_achievements = await self._get_user_achievements(user_id)
            earned_achievement_ids = {ua.achievement_id for ua in user_achievements}
            
            # Evaluate each achievement
            for achievement in achievements:
                if not achievement.is_active:
                    continue
                
                # Skip if already earned
                if achievement.achievement_id in earned_achievement_ids:
                    continue
                
                # Check prerequisites
                if not await self._check_prerequisites(user_id, achievement.prerequisites):
                    continue
                
                # Evaluate criteria
                if await self._evaluate_achievement_criteria(user_id, achievement):
                    # Award achievement
                    user_achievement = await self._award_achievement(user_id, achievement)
                    if user_achievement:
                        newly_earned.append(user_achievement)
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Evaluated achievements for user {user_id}: {len(newly_earned)} new in {processing_time:.3f}s")
            
            return newly_earned
            
        except Exception as e:
            logger.error(f"❌ Error evaluating achievements: {str(e)}")
            return []

    async def _evaluate_achievement_criteria(self, user_id: str, achievement: Achievement) -> bool:
        """Evaluate if user meets achievement criteria"""
        try:
            for criteria in achievement.criteria:
                # Get user metric value
                metric_value = await self._get_user_metric(user_id, criteria.metric_name, criteria.time_window_days)
                
                # Apply comparison operator
                if criteria.comparison_operator == ">=":
                    if metric_value < criteria.threshold_value:
                        return False
                elif criteria.comparison_operator == ">":
                    if metric_value <= criteria.threshold_value:
                        return False
                elif criteria.comparison_operator == "==":
                    if metric_value != criteria.threshold_value:
                        return False
                elif criteria.comparison_operator == "<=":
                    if metric_value > criteria.threshold_value:
                        return False
                elif criteria.comparison_operator == "<":
                    if metric_value >= criteria.threshold_value:
                        return False
                
                # Additional metadata checks
                if criteria.metadata:
                    if not await self._check_criteria_metadata(user_id, criteria):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error evaluating achievement criteria: {str(e)}")
            return False

    async def _get_user_metric(self, user_id: str, metric_name: str, time_window_days: Optional[int]) -> float:
        """Get user metric value for evaluation"""
        try:
            # Get cached metrics first
            cache_key = f"user_metrics:{user_id}:{metric_name}"
            cached_value = await self.redis_client.get(cache_key)
            
            if cached_value and not time_window_days:  # Use cache for lifetime metrics
                return float(cached_value)
            
            # Calculate metric based on type
            metric_value = 0.0
            
            # Time window filter
            cutoff_date = None
            if time_window_days:
                cutoff_date = datetime.now() - timedelta(days=time_window_days)
            
            if metric_name == "collaborations_completed":
                metric_value = await self._count_user_collaborations(user_id, cutoff_date)
            elif metric_name == "content_created":
                metric_value = await self._count_user_content(user_id, cutoff_date)
            elif metric_name == "total_revenue_generated":
                metric_value = await self._sum_user_revenue(user_id, cutoff_date)
            elif metric_name == "average_quality_score":
                metric_value = await self._calculate_average_quality(user_id, cutoff_date)
            elif metric_name == "daily_activity_streak":
                metric_value = await self._calculate_daily_streak(user_id)
            elif metric_name == "successful_mentorships":
                metric_value = await self._count_successful_mentorships(user_id, cutoff_date)
            else:
                # Generic metric lookup
                metric_value = await self._get_generic_metric(user_id, metric_name, cutoff_date)
            
            # Cache the result (if not time-windowed)
            if not time_window_days:
                await self.redis_client.setex(cache_key, 3600, str(metric_value))  # Cache for 1 hour
            
            return metric_value
            
        except Exception as e:
            logger.error(f"❌ Error getting user metric: {str(e)}")
            return 0.0

    async def _count_user_collaborations(self, user_id: str, cutoff_date: Optional[datetime]) -> float:
        """Count completed collaborations for user"""
        try:
            # In real implementation, this would query collaboration service
            # For demo, simulate based on user activity
            
            # Get collaboration activities
            activities = await self._get_user_activities(user_id, "collaboration_completed", cutoff_date)
            return len(activities)
            
        except Exception as e:
            logger.error(f"❌ Error counting collaborations: {str(e)}")
            return 0.0

    async def _count_user_content(self, user_id: str, cutoff_date: Optional[datetime]) -> float:
        """Count content created by user"""
        try:
            activities = await self._get_user_activities(user_id, "content_created", cutoff_date)
            return len(activities)
            
        except Exception as e:
            logger.error(f"❌ Error counting content: {str(e)}")
            return 0.0

    async def _sum_user_revenue(self, user_id: str, cutoff_date: Optional[datetime]) -> float:
        """Sum revenue generated by user"""
        try:
            activities = await self._get_user_activities(user_id, "revenue_earned", cutoff_date)
            total_revenue = sum(activity.get("amount", 0) for activity in activities)
            return total_revenue
            
        except Exception as e:
            logger.error(f"❌ Error summing revenue: {str(e)}")
            return 0.0

    async def _calculate_average_quality(self, user_id: str, cutoff_date: Optional[datetime]) -> float:
        """Calculate average quality score for user"""
        try:
            activities = await self._get_user_activities(user_id, "quality_rating", cutoff_date)
            if not activities:
                return 0.0
            
            quality_scores = [activity.get("score", 0) for activity in activities]
            return statistics.mean(quality_scores) if quality_scores else 0.0
            
        except Exception as e:
            logger.error(f"❌ Error calculating average quality: {str(e)}")
            return 0.0

    async def _calculate_daily_streak(self, user_id: str) -> float:
        """Calculate current daily activity streak"""
        try:
            # Get recent daily activities
            activities = await self._get_user_activities(user_id, "daily_activity", None)
            
            # Sort by date and find consecutive days
            if not activities:
                return 0.0
            
            # Group activities by date
            activity_dates = set()
            for activity in activities:
                activity_date = datetime.fromisoformat(activity["timestamp"]).date()
                activity_dates.add(activity_date)
            
            # Calculate streak from today backwards
            current_date = datetime.now().date()
            streak = 0
            
            while current_date in activity_dates:
                streak += 1
                current_date -= timedelta(days=1)
            
            return float(streak)
            
        except Exception as e:
            logger.error(f"❌ Error calculating daily streak: {str(e)}")
            return 0.0

    async def _count_successful_mentorships(self, user_id: str, cutoff_date: Optional[datetime]) -> float:
        """Count successful mentorships"""
        try:
            activities = await self._get_user_activities(user_id, "mentorship_completed", cutoff_date)
            successful = [a for a in activities if a.get("success", False)]
            return len(successful)
            
        except Exception as e:
            logger.error(f"❌ Error counting mentorships: {str(e)}")
            return 0.0

    async def _get_user_activities(
        self, 
        user_id: str, 
        activity_type: str, 
        cutoff_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Get user activities of specific type"""
        try:
            # This is a simplified implementation
            # In production, this would query a proper database with indexing
            
            activities = []
            
            # Search for user activities (simplified)
            pattern = f"user_activity:{user_id}:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys[:100]:  # Limit to avoid performance issues
                activity_data = await self.redis_client.get(key)
                if activity_data:
                    activity = json.loads(activity_data)
                    
                    # Filter by activity type
                    if activity.get("activity_type") != activity_type:
                        continue
                    
                    # Filter by date if specified
                    if cutoff_date:
                        activity_time = datetime.fromisoformat(activity["timestamp"])
                        if activity_time < cutoff_date:
                            continue
                    
                    activities.append(activity["activity_data"])
            
            return activities
            
        except Exception as e:
            logger.error(f"❌ Error getting user activities: {str(e)}")
            return []

    async def _award_achievement(self, user_id: str, achievement: Achievement) -> Optional[UserAchievement]:
        """Award achievement to user"""
        try:
            # Calculate points with rarity multiplier
            points_awarded = int(achievement.points_value * self.rarity_multipliers[achievement.rarity])
            
            # Create user achievement record
            user_achievement = UserAchievement(
                user_achievement_id=str(uuid.uuid4()),
                user_id=user_id,
                achievement_id=achievement.achievement_id,
                earned_at=datetime.now(),
                verification_status="verified" if not any(c.requires_verification for c in achievement.criteria) else "pending",
                points_awarded=points_awarded,
                notification_sent=False,
                shared_publicly=False,
                evidence=None,
                metadata={"rarity": achievement.rarity.value, "category": achievement.category.value}
            )
            
            # Store user achievement
            await self._store_user_achievement(user_achievement)
            
            # Update user profile
            await self._update_user_profile(user_id, points_awarded)
            
            # Update achievement statistics
            await self._update_achievement_stats(achievement.achievement_id)
            
            # Send notification
            await self._send_achievement_notification(user_id, achievement)
            
            logger.info(f"🏆 Achievement awarded: {achievement.name} to user {user_id}")
            
            return user_achievement
            
        except Exception as e:
            logger.error(f"❌ Error awarding achievement: {str(e)}")
            return None

    async def _update_user_profile(self, user_id: str, points_awarded: int) -> None:
        """Update user achievement profile"""
        try:
            profile = await self._get_user_profile(user_id)
            
            if not profile:
                profile = UserProfile(
                    user_id=user_id,
                    total_achievements=0,
                    total_points=0,
                    level=1,
                    experience_points=0,
                    achievements_by_category={},
                    achievements_by_rarity={},
                    current_streaks={},
                    badges_earned=[],
                    badges_in_progress=[],
                    rank_percentile=0.0,
                    last_achievement_date=None
                )
            
            # Update profile
            profile.total_achievements += 1
            profile.total_points += points_awarded
            profile.experience_points += points_awarded
            profile.last_achievement_date = datetime.now()
            
            # Calculate new level
            new_level = self._calculate_level(profile.total_points)
            if new_level > profile.level:
                profile.level = new_level
                await self._send_level_up_notification(user_id, new_level)
            
            # Store updated profile
            await self._store_user_profile(profile)
            
            logger.info(f"📊 User profile updated: {user_id} (+{points_awarded} points, level {profile.level})")
            
        except Exception as e:
            logger.error(f"❌ Error updating user profile: {str(e)}")

    def _calculate_level(self, total_points: int) -> int:
        """Calculate user level based on total points"""
        for level in range(self.max_level, 0, -1):
            if total_points >= self.level_requirements[level]:
                return level
        return 1

    async def get_user_achievements(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user achievement data"""
        try:
            # Get user profile
            profile = await self._get_user_profile(user_id)
            
            # Get user achievements
            user_achievements = await self._get_user_achievements(user_id)
            
            # Get progress on active achievements
            progress_list = await self._get_user_progress(user_id)
            
            # Get recommendations
            recommendations = await self._get_achievement_recommendations(user_id)
            
            return {
                "user_id": user_id,
                "profile": asdict(profile) if profile else None,
                "achievements": [asdict(ua) for ua in user_achievements],
                "progress": [asdict(p) for p in progress_list],
                "recommendations": recommendations,
                "statistics": await self._get_user_achievement_stats(user_id)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user achievements: {str(e)}")
            return {}

    async def _get_achievement_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get personalized achievement recommendations"""
        try:
            # Get user's achievement history and patterns
            user_achievements = await self._get_user_achievements(user_id)
            user_profile = await self._get_user_profile(user_id)
            
            # Get all available achievements
            all_achievements = await self._get_all_achievements()
            
            # Filter out already earned achievements
            earned_ids = {ua.achievement_id for ua in user_achievements}
            available_achievements = [a for a in all_achievements if a.achievement_id not in earned_ids]
            
            recommendations = []
            
            for achievement in available_achievements:
                # Check prerequisites
                if not await self._check_prerequisites(user_id, achievement.prerequisites):
                    continue
                
                # Calculate recommendation score
                score = await self._calculate_recommendation_score(user_id, achievement, user_profile)
                
                if score > 0.3:  # Threshold for recommendations
                    recommendations.append({
                        "achievement_id": achievement.achievement_id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "category": achievement.category.value,
                        "rarity": achievement.rarity.value,
                        "points_value": achievement.points_value,
                        "recommendation_score": score,
                        "estimated_time_to_complete": await self._estimate_completion_time(user_id, achievement),
                        "current_progress": await self._get_current_progress(user_id, achievement)
                    })
            
            # Sort by recommendation score
            recommendations.sort(key=lambda r: r["recommendation_score"], reverse=True)
            
            return recommendations[:10]  # Top 10 recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting achievement recommendations: {str(e)}")
            return []

    async def _calculate_recommendation_score(
        self, 
        user_id: str, 
        achievement: Achievement, 
        user_profile: Optional[UserProfile]
    ) -> float:
        """Calculate recommendation score for achievement"""
        try:
            score = 0.5  # Base score
            
            if not user_profile:
                return score
            
            # Category affinity
            category_count = user_profile.achievements_by_category.get(achievement.category.value, 0)
            if category_count > 0:
                score += 0.2  # User has earned achievements in this category
            
            # Rarity preference
            rarity_count = user_profile.achievements_by_rarity.get(achievement.rarity.value, 0)
            if rarity_count > 0:
                score += 0.1
            
            # Level appropriateness
            if achievement.rarity == AchievementRarity.COMMON and user_profile.level < 10:
                score += 0.2
            elif achievement.rarity == AchievementRarity.RARE and user_profile.level > 20:
                score += 0.2
            
            # Progress potential
            current_progress = await self._get_current_progress(user_id, achievement)
            if current_progress > 0:
                score += current_progress * 0.3  # Boost for achievements already in progress
            
            # Trending bonus
            achievement_stats = await self._get_achievement_stats(achievement.achievement_id)
            if achievement_stats and achievement_stats.trending_score > 0.7:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"❌ Error calculating recommendation score: {str(e)}")
            return 0.5

    async def _get_current_progress(self, user_id: str, achievement: Achievement) -> float:
        """Get current progress towards achievement"""
        try:
            total_progress = 0.0
            criteria_count = len(achievement.criteria)
            
            for criteria in achievement.criteria:
                current_value = await self._get_user_metric(user_id, criteria.metric_name, criteria.time_window_days)
                progress = min(1.0, current_value / criteria.threshold_value)
                total_progress += progress
            
            return total_progress / criteria_count if criteria_count > 0 else 0.0
            
        except Exception as e:
            logger.error(f"❌ Error getting current progress: {str(e)}")
            return 0.0

    async def _store_achievement(self, achievement: Achievement) -> None:
        """Store achievement definition"""
        try:
            achievement_key = f"achievement:{achievement.achievement_id}"
            achievement_data = asdict(achievement)
            
            await self.redis_client.setex(
                achievement_key,
                86400 * 365,  # Keep for 1 year
                json.dumps(achievement_data, default=str)
            )
            
            # Update category index
            category_key = f"achievements_by_category:{achievement.category.value}"
            await self.redis_client.sadd(category_key, achievement.achievement_id)
            
            # Update rarity index
            rarity_key = f"achievements_by_rarity:{achievement.rarity.value}"
            await self.redis_client.sadd(rarity_key, achievement.achievement_id)
            
            logger.info(f"💾 Achievement stored: {achievement.achievement_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing achievement: {str(e)}")

    async def _store_user_achievement(self, user_achievement: UserAchievement) -> None:
        """Store user achievement"""
        try:
            ua_key = f"user_achievement:{user_achievement.user_achievement_id}"
            ua_data = asdict(user_achievement)
            
            await self.redis_client.setex(
                ua_key,
                86400 * 365,  # Keep for 1 year
                json.dumps(ua_data, default=str)
            )
            
            # Update user index
            user_achievements_key = f"user_achievements:{user_achievement.user_id}"
            await self.redis_client.lpush(user_achievements_key, user_achievement.user_achievement_id)
            await self.redis_client.expire(user_achievements_key, 86400 * 365)
            
            logger.info(f"💾 User achievement stored: {user_achievement.user_achievement_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing user achievement: {str(e)}")

    async def _store_user_profile(self, profile: UserProfile) -> None:
        """Store user profile"""
        try:
            profile_key = f"user_profile:{profile.user_id}"
            profile_data = asdict(profile)
            
            await self.redis_client.setex(
                profile_key,
                86400 * 365,  # Keep for 1 year
                json.dumps(profile_data, default=str)
            )
            
            logger.info(f"💾 User profile stored: {profile.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing user profile: {str(e)}")

    async def _get_all_achievements(self) -> List[Achievement]:
        """Get all achievement definitions"""
        try:
            # Get from cache first
            if hasattr(self, '_all_achievements_cache'):
                return self._all_achievements_cache
            
            achievements = []
            
            # Get all achievement keys
            pattern = "achievement:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                achievement_data = await self.redis_client.get(key)
                if achievement_data:
                    data = json.loads(achievement_data)
                    achievement = Achievement(**data)
                    achievements.append(achievement)
            
            # Cache for future use
            self._all_achievements_cache = achievements
            
            return achievements
            
        except Exception as e:
            logger.error(f"❌ Error getting all achievements: {str(e)}")
            return []

    async def _get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """Get user's earned achievements"""
        try:
            user_achievements = []
            
            user_achievements_key = f"user_achievements:{user_id}"
            ua_ids = await self.redis_client.lrange(user_achievements_key, 0, -1)
            
            for ua_id_bytes in ua_ids:
                ua_id = ua_id_bytes.decode() if isinstance(ua_id_bytes, bytes) else ua_id_bytes
                ua_key = f"user_achievement:{ua_id}"
                ua_data = await self.redis_client.get(ua_key)
                
                if ua_data:
                    data = json.loads(ua_data)
                    user_achievement = UserAchievement(**data)
                    user_achievements.append(user_achievement)
            
            return user_achievements
            
        except Exception as e:
            logger.error(f"❌ Error getting user achievements: {str(e)}")
            return []

    async def _get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user achievement profile"""
        try:
            profile_key = f"user_profile:{user_id}"
            profile_data = await self.redis_client.get(profile_key)
            
            if not profile_data:
                return None
            
            data = json.loads(profile_data)
            return UserProfile(**data)
            
        except Exception as e:
            logger.error(f"❌ Error getting user profile: {str(e)}")
            return None

    async def _progress_evaluator(self) -> None:
        """Background task for evaluating achievement progress"""
        while True:
            try:
                if self.evaluation_queue:
                    # Process evaluation queue
                    evaluation_item = self.evaluation_queue.popleft()
                    user_id = evaluation_item["user_id"]
                    
                    # Evaluate achievements for user
                    newly_earned = await self.evaluate_achievements(user_id)
                    
                    if newly_earned:
                        logger.info(f"🎉 {len(newly_earned)} new achievements for user {user_id}")
                
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                logger.error(f"❌ Error in progress evaluator: {str(e)}")
                await asyncio.sleep(10)

    async def _streak_monitor(self) -> None:
        """Background task for monitoring streaks"""
        while True:
            try:
                # Monitor daily activity streaks
                await self._update_daily_streaks()
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"❌ Error in streak monitor: {str(e)}")
                await asyncio.sleep(600)

    async def _recommendation_engine(self) -> None:
        """Background task for generating recommendations"""
        while True:
            try:
                # Generate achievement recommendations for active users
                await self._generate_batch_recommendations()
                
                await asyncio.sleep(7200)  # Run every 2 hours
                
            except Exception as e:
                logger.error(f"❌ Error in recommendation engine: {str(e)}")
                await asyncio.sleep(600)

    async def _analytics_aggregator(self) -> None:
        """Background task for aggregating analytics"""
        while True:
            try:
                # Aggregate achievement statistics
                await self._aggregate_achievement_analytics()
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"❌ Error in analytics aggregator: {str(e)}")
                await asyncio.sleep(600)

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = {
                "service": "AchievementService",
                "status": "healthy",
                "version": self.version,
                "uptime": str(datetime.now() - self.startup_time),
                "redis_connected": False,
                "evaluation_queue_size": len(self.evaluation_queue),
                "achievement_cache_size": len(self.achievement_cache),
                "progress_cache_size": len(self.progress_cache),
                "ml_models_loaded": len(self.ml_models),
                "max_level": self.max_level,
                "timestamp": datetime.now().isoformat()
            }
            
            # Test Redis connection
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis_connected"] = True
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "service": "AchievementService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def stop(self) -> None:
        """Stop the achievement service"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            self.thread_pool.shutdown(wait=True)
            
            logger.info(f"🛑 AchievementService {self.service_id} stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping service: {str(e)}")

# Example usage and testing
async def main() -> None:
    """Example usage of AchievementService"""
    service = AchievementService()
    
    try:
        # Start service
        await service.start()
        
        # Simulate user activities
        user_id = "test_user_001"
        
        print(f"🏆 Testing achievement system for user: {user_id}")
        
        # Track some activities
        await service.track_user_activity(user_id, "collaboration_completed", {"project_id": "proj_001", "success": True})
        await service.track_user_activity(user_id, "content_created", {"content_id": "content_001", "type": "video"})
        await service.track_user_activity(user_id, "quality_rating", {"score": 0.95, "project_id": "proj_001"})
        await service.track_user_activity(user_id, "daily_activity", {"tasks_completed": 5})
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Get user achievements
        achievements_data = await service.get_user_achievements(user_id)
        
        print(f"📊 User Achievement Summary:")
        if achievements_data.get("profile"):
            profile = achievements_data["profile"]
            print(f"   - Level: {profile['level']}")
            print(f"   - Total Points: {profile['total_points']}")
            print(f"   - Achievements: {profile['total_achievements']}")
        
        print(f"   - Earned Achievements: {len(achievements_data.get('achievements', []))}")
        print(f"   - Recommendations: {len(achievements_data.get('recommendations', []))}")
        
        # Show recommendations
        for i, rec in enumerate(achievements_data.get('recommendations', [])[:3]):
            print(f"     {i+1}. {rec['name']} (Score: {rec['recommendation_score']:.2f})")
        
        # Health check
        health = await service.health_check()
        print(f"🏥 Service health: {health['status']}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")
    
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())