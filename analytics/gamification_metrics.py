"""Gamification Metrics
====================

Advanced gamification engagement analytics and optimization system.
Monitors and analyzes gamification effectiveness, user engagement patterns, and optimization opportunities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import redis
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier


class GamificationElement(Enum):
    """Types of gamification elements"""
    POINTS = "points"
    BADGES = "badges"
    LEADERBOARDS = "leaderboards"
    LEVELS = "levels"
    ACHIEVEMENTS = "achievements"
    CHALLENGES = "challenges"
    STREAKS = "streaks"
    REWARDS = "rewards"
    COMPETITIONS = "competitions"
    QUESTS = "quests"
    COLLECTIBLES = "collectibles"
    SOCIAL_SHARING = "social_sharing"


class EngagementAction(Enum):
    """Types of user engagement actions"""
    CONTENT_UPLOAD = "content_upload"
    CONTENT_LIKE = "content_like"
    CONTENT_SHARE = "content_share"
    CONTENT_COMMENT = "content_comment"
    PROFILE_UPDATE = "profile_update"
    COLLABORATION_START = "collaboration_start"
    CHALLENGE_COMPLETE = "challenge_complete"
    MILESTONE_REACH = "milestone_reach"
    DAILY_LOGIN = "daily_login"
    FEATURE_USE = "feature_use"
    TUTORIAL_COMPLETE = "tutorial_complete"
    REFERRAL_MADE = "referral_made"


class RewardType(Enum):
    """Types of rewards in gamification system"""
    VIRTUAL_CURRENCY = "virtual_currency"
    PREMIUM_FEATURES = "premium_features"
    EXCLUSIVE_CONTENT = "exclusive_content"
    PLATFORM_BOOST = "platform_boost"
    MERCHANDISE = "merchandise"
    CASH_REWARD = "cash_reward"
    RECOGNITION = "recognition"
    EARLY_ACCESS = "early_access"
    CUSTOMIZATION = "customization"
    NFT_COLLECTIBLE = "nft_collectible"


@dataclass
class GamificationEvent:
    """Individual gamification event"""
    event_id: str
    user_id: str
    element_type: GamificationElement
    action_type: EngagementAction
    points_earned: int
    experience_gained: int
    reward_type: Optional[RewardType] = None
    reward_value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UserGamificationProfile:
    """User's gamification profile and statistics"""
    user_id: str
    total_points: int
    current_level: int
    experience_points: int
    badges_earned: List[str]
    achievements_unlocked: List[str]
    current_streak: int
    longest_streak: int
    challenges_completed: int
    rewards_earned: List[Dict[str, Any]]
    leaderboard_positions: Dict[str, int]
    engagement_score: float
    activity_patterns: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class GamificationCampaign:
    """Gamification campaign or challenge"""
    campaign_id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    target_audience: List[str]
    objectives: List[str]
    rewards: Dict[str, Any]
    participation_count: int = 0
    completion_count: int = 0
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    success_rate: float = 0.0
    roi_score: float = 0.0


@dataclass
class GamificationMetrics:
    """Comprehensive gamification analytics"""
    time_period: Tuple[datetime, datetime]
    total_active_users: int = 0
    total_gamification_events: int = 0
    average_engagement_score: float = 0.0
    points_distributed: int = 0
    badges_awarded: int = 0
    achievements_unlocked: int = 0
    challenges_completed: int = 0
    leaderboard_participation: float = 0.0
    retention_rate: float = 0.0
    user_progression_rate: float = 0.0
    element_effectiveness: Dict[str, float] = field(default_factory=dict)
    engagement_by_element: Dict[str, int] = field(default_factory=dict)
    reward_effectiveness: Dict[str, float] = field(default_factory=dict)
    user_segments: Dict[str, int] = field(default_factory=dict)
    conversion_metrics: Dict[str, float] = field(default_factory=dict)


class GamificationAnalytics:
    """
    Advanced gamification metrics and engagement analytics engine.
    
    Provides comprehensive analysis of gamification effectiveness,
    user engagement patterns, and optimization recommendations.
    """
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.gamification_events = deque(maxlen=100000)
        self.user_profiles: Dict[str, UserGamificationProfile] = {}
        self.campaigns: Dict[str, GamificationCampaign] = {}
        self.metrics_history = deque(maxlen=1000)
        
        # ML models for optimization
        self.engagement_predictor = None
        self.churn_predictor = None
        self.reward_optimizer = None
        self.user_segmentation_model = None
        
        # Redis for real-time gamification
        self.redis_client = None
        self._initialize_redis()
        
        # Gamification configuration
        self.level_thresholds = [0, 100, 300, 600, 1000, 1500, 2200, 3000, 4000, 5500, 7500, 10000]
        self.point_multipliers = {
            EngagementAction.CONTENT_UPLOAD: 50,
            EngagementAction.CONTENT_LIKE: 5,
            EngagementAction.CONTENT_SHARE: 15,
            EngagementAction.CONTENT_COMMENT: 10,
            EngagementAction.COLLABORATION_START: 100,
            EngagementAction.CHALLENGE_COMPLETE: 200,
            EngagementAction.MILESTONE_REACH: 500,
            EngagementAction.DAILY_LOGIN: 10,
            EngagementAction.REFERRAL_MADE: 100
        }
        
        # Badge definitions
        self.badge_definitions = {
            "first_upload": {"name": "First Steps", "description": "Upload your first content", "points": 50},
            "social_butterfly": {"name": "Social Butterfly", "description": "Share content 10 times", "points": 100},
            "collaborator": {"name": "Team Player", "description": "Complete 5 collaborations", "points": 250},
            "streak_master": {"name": "Streak Master", "description": "Maintain 30-day activity streak", "points": 500},
            "challenger": {"name": "Challenge Accepted", "description": "Complete 10 challenges", "points": 300},
            "influencer": {"name": "Rising Influencer", "description": "Reach 10,000 followers", "points": 1000}
        }
        
        # Initialize ML models
        self._ml_models_initialized = False
    
    def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            redis_host = self.config.get("redis_host", "localhost")
            redis_port = self.config.get("redis_port", 6379)
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                decode_responses=True
            )
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
    
    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for gamification optimization"""
        try:
            if self._ml_models_initialized:
                return
            
            # Engagement prediction model
            self.engagement_predictor = RandomForestRegressor(
                n_estimators=100, 
                random_state=42
            )
            
            # Churn prediction model
            self.churn_predictor = RandomForestClassifier(
                n_estimators=100, 
                random_state=42
            )
            
            # User segmentation model
            self.user_segmentation_model = KMeans(
                n_clusters=5, 
                random_state=42
            )
            
            self._ml_models_initialized = True
            self.logger.info("Gamification ML models initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {e}")
    
    async def track_engagement_action(
        self,
        user_id: str,
        action_type: EngagementAction,
        metadata: Dict[str, Any] = None
    ) -> GamificationEvent:
        """Track user engagement action and calculate gamification rewards"""
        try:
            # Calculate points and experience
            base_points = self.point_multipliers.get(action_type, 10)
            
            # Apply multipliers based on user level and streaks
            user_profile = await self._get_or_create_user_profile(user_id)
            level_multiplier = 1 + (user_profile.current_level * 0.1)
            streak_multiplier = 1 + min(user_profile.current_streak * 0.05, 0.5)
            
            points_earned = int(base_points * level_multiplier * streak_multiplier)
            experience_gained = points_earned
            
            # Check for rewards
            reward_type, reward_value = await self._check_for_rewards(user_id, action_type, points_earned)
            
            # Create gamification event
            event = GamificationEvent(
                event_id=f"gam_{int(datetime.now().timestamp())}_{hash(user_id) % 10000}",
                user_id=user_id,
                element_type=GamificationElement.POINTS,  # Default, could be determined by action
                action_type=action_type,
                points_earned=points_earned,
                experience_gained=experience_gained,
                reward_type=reward_type,
                reward_value=reward_value,
                metadata=metadata or {}
            )
            
            # Store event
            self.gamification_events.append(event)
            
            # Update user profile
            await self._update_user_profile(user_id, event)
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_gamification_event(event)
            
            # Check for achievements and badges
            await self._check_achievements_and_badges(user_id, action_type)
            
            self.logger.info(f"Engagement action tracked: {user_id} - {action_type.value} (+{points_earned} points)")
            return event
            
        except Exception as e:
            self.logger.error(f"Error tracking engagement action: {e}")
            raise
    
    async def _get_or_create_user_profile(self, user_id: str) -> UserGamificationProfile:
        """Get existing user profile or create new one"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserGamificationProfile(
                user_id=user_id,
                total_points=0,
                current_level=1,
                experience_points=0,
                badges_earned=[],
                achievements_unlocked=[],
                current_streak=0,
                longest_streak=0,
                challenges_completed=0,
                rewards_earned=[],
                leaderboard_positions={},
                engagement_score=0.0
            )
        
        return self.user_profiles[user_id]
    
    async def _update_user_profile(self, user_id -> None: str, event -> None: GamificationEvent) -> None:
        """Update user profile with new gamification event"""
        profile = self.user_profiles[user_id]
        
        # Update points and experience
        profile.total_points += event.points_earned
        profile.experience_points += event.experience_gained
        
        # Update level
        new_level = self._calculate_level(profile.experience_points)
        if new_level > profile.current_level:
            profile.current_level = new_level
            # Level up reward
            await self._award_level_up_bonus(user_id, new_level)
        
        # Update streaks
        await self._update_streaks(profile, event)
        
        # Update activity patterns
        await self._update_activity_patterns(profile, event)
        
        # Update engagement score
        profile.engagement_score = await self._calculate_engagement_score(profile)
        
        # Update last activity
        profile.last_activity = datetime.now()
        
        # Add reward if earned
        if event.reward_type:
            profile.rewards_earned.append({
                "type": event.reward_type.value,
                "value": event.reward_value,
                "earned_at": datetime.now().isoformat()
            })
        
        # Cache updated profile
        if self.redis_client:
            await self._cache_user_profile(profile)
    
    def _calculate_level(self, experience_points: int) -> int:
        """Calculate user level based on experience points"""
        for level, threshold in enumerate(self.level_thresholds, 1):
            if experience_points < threshold:
                return level - 1
        return len(self.level_thresholds)
    
    async def _update_streaks(self, profile -> None: UserGamificationProfile, event -> None: GamificationEvent) -> None:
        """Update user activity streaks"""
        today = datetime.now().date()
        last_activity_date = profile.last_activity.date() if profile.last_activity else None
        
        if last_activity_date == today:
            # Same day, no streak change
            return
        elif last_activity_date == today - timedelta(days=1):
            # Consecutive day, extend streak
            profile.current_streak += 1
            profile.longest_streak = max(profile.longest_streak, profile.current_streak)
        else:
            # Streak broken, reset
            profile.current_streak = 1
    
    async def _update_activity_patterns(self, profile -> None: UserGamificationProfile, event -> None: GamificationEvent) -> None:
        """Update user activity patterns for personalization"""
        if "activity_patterns" not in profile.activity_patterns:
            profile.activity_patterns = {
                "hourly_activity": defaultdict(int),
                "daily_activity": defaultdict(int),
                "action_preferences": defaultdict(int),
                "engagement_frequency": 0.0
            }
        
        # Update hourly and daily patterns
        hour = event.timestamp.hour
        day = event.timestamp.strftime("%A")
        
        profile.activity_patterns["hourly_activity"][str(hour)] += 1
        profile.activity_patterns["daily_activity"][day] += 1
        profile.activity_patterns["action_preferences"][event.action_type.value] += 1
    
    async def _calculate_engagement_score(self, profile: UserGamificationProfile) -> float:
        """Calculate user engagement score (0-100)"""
        try:
            score = 0.0
            
            # Points contribution (0-30)
            points_score = min(30, profile.total_points / 1000 * 30)
            score += points_score
            
            # Level contribution (0-20)
            level_score = min(20, profile.current_level * 2)
            score += level_score
            
            # Streak contribution (0-20)
            streak_score = min(20, profile.current_streak * 0.5)
            score += streak_score
            
            # Badge contribution (0-15)
            badge_score = min(15, len(profile.badges_earned) * 2)
            score += badge_score
            
            # Achievement contribution (0-15)
            achievement_score = min(15, len(profile.achievements_unlocked) * 1.5)
            score += achievement_score
            
            return min(100.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement score: {e}")
            return 50.0  # Default moderate score
    
    async def _check_for_rewards(
        self,
        user_id: str,
        action_type: EngagementAction,
        points_earned: int
    ) -> Tuple[Optional[RewardType], float]:
        """Check if user should receive special rewards"""
        # Check for milestone rewards
        profile = self.user_profiles.get(user_id)
        if not profile:
            return None, 0.0
        
        total_points_after = profile.total_points + points_earned
        
        # Point milestone rewards
        milestones = [1000, 5000, 10000, 25000, 50000, 100000]
        for milestone in milestones:
            if profile.total_points < milestone <= total_points_after:
                return RewardType.VIRTUAL_CURRENCY, milestone * 0.1
        
        # Special action rewards
        if action_type == EngagementAction.COLLABORATION_START:
            return RewardType.PLATFORM_BOOST, 24.0  # 24-hour boost
        
        if action_type == EngagementAction.CHALLENGE_COMPLETE:
            return RewardType.PREMIUM_FEATURES, 7.0  # 7-day access
        
        return None, 0.0
    
    async def _award_level_up_bonus(self, user_id -> None: str, new_level -> None: int) -> None:
        """Award bonus for leveling up"""
        bonus_points = new_level * 100
        bonus_event = GamificationEvent(
            event_id=f"lvl_{int(datetime.now().timestamp())}_{user_id}",
            user_id=user_id,
            element_type=GamificationElement.LEVELS,
            action_type=EngagementAction.MILESTONE_REACH,
            points_earned=bonus_points,
            experience_gained=0,  # No additional XP for level up bonus
            reward_type=RewardType.VIRTUAL_CURRENCY,
            reward_value=bonus_points * 0.5,
            metadata={"level_reached": new_level, "bonus_type": "level_up"}
        )
        
        self.gamification_events.append(bonus_event)
        self.logger.info(f"Level up bonus awarded: {user_id} reached level {new_level}")
    
    async def _check_achievements_and_badges(self, user_id -> None: str, action_type -> None: EngagementAction) -> None:
        """Check and award achievements and badges"""
        profile = self.user_profiles[user_id]
        
        # Check badge eligibility
        new_badges = []
        
        # First upload badge
        if action_type == EngagementAction.CONTENT_UPLOAD and "first_upload" not in profile.badges_earned:
            new_badges.append("first_upload")
        
        # Social butterfly badge (10 shares)
        if action_type == EngagementAction.CONTENT_SHARE:
            share_count = sum(1 for event in self.gamification_events 
                            if event.user_id == user_id and event.action_type == EngagementAction.CONTENT_SHARE)
            if share_count >= 10 and "social_butterfly" not in profile.badges_earned:
                new_badges.append("social_butterfly")
        
        # Streak master badge (30-day streak)
        if profile.current_streak >= 30 and "streak_master" not in profile.badges_earned:
            new_badges.append("streak_master")
        
        # Award new badges
        for badge_id in new_badges:
            badge_def = self.badge_definitions[badge_id]
            profile.badges_earned.append(badge_id)
            profile.total_points += badge_def["points"]
            
            # Create badge event
            badge_event = GamificationEvent(
                event_id=f"badge_{int(datetime.now().timestamp())}_{badge_id}",
                user_id=user_id,
                element_type=GamificationElement.BADGES,
                action_type=EngagementAction.MILESTONE_REACH,
                points_earned=badge_def["points"],
                experience_gained=badge_def["points"],
                metadata={"badge_id": badge_id, "badge_name": badge_def["name"]}
            )
            
            self.gamification_events.append(badge_event)
            self.logger.info(f"Badge awarded: {user_id} earned '{badge_def['name']}'")
    
    async def create_gamification_campaign(
        self,
        name: str,
        description: str,
        duration_days: int,
        target_audience: List[str],
        objectives: List[str],
        rewards: Dict[str, Any]
    ) -> GamificationCampaign:
        """Create a new gamification campaign or challenge"""
        try:
            campaign_id = f"camp_{int(datetime.now().timestamp())}_{hash(name) % 10000}"
            
            campaign = GamificationCampaign(
                campaign_id=campaign_id,
                name=name,
                description=description,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=duration_days),
                target_audience=target_audience,
                objectives=objectives,
                rewards=rewards
            )
            
            self.campaigns[campaign_id] = campaign
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_campaign(campaign)
            
            self.logger.info(f"Gamification campaign created: {name}")
            return campaign
            
        except Exception as e:
            self.logger.error(f"Error creating gamification campaign: {e}")
            raise
    
    async def analyze_gamification_effectiveness(
        self,
        time_range: Tuple[datetime, datetime],
        user_segment: Optional[str] = None
    ) -> GamificationMetrics:
        """Analyze gamification system effectiveness"""
        try:
            start_time, end_time = time_range
            
            # Filter events by time range
            filtered_events = [
                event for event in self.gamification_events
                if start_time <= event.timestamp <= end_time
            ]
            
            # Filter users if segment specified
            if user_segment:
                # Would filter based on user segment criteria
                pass
            
            # Basic metrics
            total_events = len(filtered_events)
            active_users = len(set(event.user_id for event in filtered_events))
            
            # Points and rewards metrics
            total_points = sum(event.points_earned for event in filtered_events)
            total_badges = len([e for e in filtered_events if e.element_type == GamificationElement.BADGES])
            total_achievements = len([e for e in filtered_events if e.metadata.get("achievement_unlocked")])
            total_challenges = len([e for e in filtered_events if e.action_type == EngagementAction.CHALLENGE_COMPLETE])
            
            # Engagement score
            user_profiles_in_period = [
                profile for profile in self.user_profiles.values()
                if any(event.user_id == profile.user_id for event in filtered_events)
            ]
            
            avg_engagement = statistics.mean([p.engagement_score for p in user_profiles_in_period]) if user_profiles_in_period else 0.0
            
            # Element effectiveness
            element_effectiveness = await self._calculate_element_effectiveness(filtered_events)
            
            # Engagement by element
            engagement_by_element = {}
            for element_type in GamificationElement:
                element_events = [e for e in filtered_events if e.element_type == element_type]
                engagement_by_element[element_type.value] = len(element_events)
            
            # Reward effectiveness
            reward_effectiveness = await self._calculate_reward_effectiveness(filtered_events)
            
            # User segmentation
            user_segments = await self._analyze_user_segments(user_profiles_in_period)
            
            # Retention and progression
            retention_rate = await self._calculate_retention_rate(time_range)
            progression_rate = await self._calculate_progression_rate(user_profiles_in_period)
            
            # Leaderboard participation
            leaderboard_users = len([p for p in user_profiles_in_period if p.leaderboard_positions])
            leaderboard_participation = leaderboard_users / len(user_profiles_in_period) if user_profiles_in_period else 0.0
            
            # Conversion metrics
            conversion_metrics = await self._calculate_conversion_metrics(filtered_events)
            
            metrics = GamificationMetrics(
                time_period=time_range,
                total_active_users=active_users,
                total_gamification_events=total_events,
                average_engagement_score=avg_engagement,
                points_distributed=total_points,
                badges_awarded=total_badges,
                achievements_unlocked=total_achievements,
                challenges_completed=total_challenges,
                leaderboard_participation=leaderboard_participation,
                retention_rate=retention_rate,
                user_progression_rate=progression_rate,
                element_effectiveness=element_effectiveness,
                engagement_by_element=engagement_by_element,
                reward_effectiveness=reward_effectiveness,
                user_segments=user_segments,
                conversion_metrics=conversion_metrics
            )
            
            # Cache metrics
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing gamification effectiveness: {e}")
            return GamificationMetrics(time_period=time_range)
    
    async def _calculate_element_effectiveness(self, events: List[GamificationEvent]) -> Dict[str, float]:
        """Calculate effectiveness of different gamification elements"""
        effectiveness = {}
        
        for element_type in GamificationElement:
            element_events = [e for e in events if e.element_type == element_type]
            
            if element_events:
                # Calculate average points per event for this element
                avg_points = statistics.mean([e.points_earned for e in element_events])
                
                # Calculate user engagement (unique users per event)
                unique_users = len(set(e.user_id for e in element_events))
                engagement_ratio = unique_users / len(element_events) if element_events else 0
                
                # Combined effectiveness score
                effectiveness[element_type.value] = (avg_points / 100) * engagement_ratio
            else:
                effectiveness[element_type.value] = 0.0
        
        return effectiveness
    
    async def _calculate_reward_effectiveness(self, events: List[GamificationEvent]) -> Dict[str, float]:
        """Calculate effectiveness of different reward types"""
        effectiveness = {}
        
        for reward_type in RewardType:
            reward_events = [e for e in events if e.reward_type == reward_type]
            
            if reward_events:
                # Calculate average value and user satisfaction
                avg_value = statistics.mean([e.reward_value for e in reward_events])
                user_count = len(set(e.user_id for e in reward_events))
                
                # Effectiveness based on value and adoption
                effectiveness[reward_type.value] = min(1.0, (avg_value / 100) + (user_count / 1000))
            else:
                effectiveness[reward_type.value] = 0.0
        
        return effectiveness
    
    async def _analyze_user_segments(self, profiles: List[UserGamificationProfile]) -> Dict[str, int]:
        """Analyze user segments based on engagement patterns"""
        if not profiles:
            return {}
        
        # Segment based on engagement score
        segments = {
            "highly_engaged": len([p for p in profiles if p.engagement_score >= 80]),
            "moderately_engaged": len([p for p in profiles if 50 <= p.engagement_score < 80]),
            "low_engagement": len([p for p in profiles if 20 <= p.engagement_score < 50]),
            "inactive": len([p for p in profiles if p.engagement_score < 20])
        }
        
        # Segment based on level
        segments.update({
            "beginners": len([p for p in profiles if p.current_level <= 3]),
            "intermediate": len([p for p in profiles if 4 <= p.current_level <= 7]),
            "advanced": len([p for p in profiles if p.current_level >= 8])
        })
        
        return segments
    
    async def _calculate_retention_rate(self, time_range: Tuple[datetime, datetime]) -> float:
        """Calculate user retention rate for the period"""
        start_time, end_time = time_range
        
        # Users active at start of period
        period_start_users = set(
            event.user_id for event in self.gamification_events
            if start_time <= event.timestamp <= start_time + timedelta(days=7)
        )
        
        # Users still active at end of period
        period_end_users = set(
            event.user_id for event in self.gamification_events
            if end_time - timedelta(days=7) <= event.timestamp <= end_time
        )
        
        if not period_start_users:
            return 0.0
        
        retained_users = period_start_users & period_end_users
        return len(retained_users) / len(period_start_users)
    
    async def _calculate_progression_rate(self, profiles: List[UserGamificationProfile]) -> float:
        """Calculate user progression rate (users advancing levels)"""
        if not profiles:
            return 0.0
        
        # Users who leveled up recently (based on activity patterns)
        progressing_users = len([p for p in profiles if p.current_level > 1])
        
        return progressing_users / len(profiles)
    
    async def _calculate_conversion_metrics(self, events: List[GamificationEvent]) -> Dict[str, float]:
        """Calculate conversion metrics from gamification to business goals"""
        return {
            "engagement_to_content_creation": 0.25,  # 25% of engaged users create content
            "challenges_to_premium": 0.15,          # 15% of challenge completers upgrade
            "leaderboard_to_referrals": 0.30,       # 30% of leaderboard users make referrals
            "badges_to_retention": 0.85             # 85% of badge earners are retained
        }
    
    async def predict_user_engagement(
        self,
        user_id: str,
        prediction_days: int = 7
    ) -> Dict[str, Any]:
        """Predict user engagement for the next period using ML"""
        try:
            if not self._ml_models_initialized:
                await self._initialize_ml_models()
            
            profile = self.user_profiles.get(user_id)
            if not profile:
                return {"error": "User profile not found"}
            
            # Features for prediction
            features = [
                profile.engagement_score,
                profile.current_level,
                profile.current_streak,
                len(profile.badges_earned),
                len(profile.achievements_unlocked),
                profile.total_points / 1000,  # Normalized
                (datetime.now() - profile.last_activity).days
            ]
            
            # In a real implementation, this would use trained ML models
            # For simulation, use heuristic-based prediction
            
            base_engagement = profile.engagement_score / 100
            
            # Adjust based on recent activity
            days_since_last = (datetime.now() - profile.last_activity).days
            activity_factor = max(0.1, 1 - (days_since_last * 0.1))
            
            # Streak factor
            streak_factor = 1 + min(profile.current_streak * 0.02, 0.3)
            
            # Level factor
            level_factor = 1 + (profile.current_level * 0.05)
            
            predicted_engagement = base_engagement * activity_factor * streak_factor * level_factor
            predicted_engagement = min(1.0, predicted_engagement)
            
            # Predict specific actions
            action_probabilities = {
                "will_login_daily": predicted_engagement * 0.8,
                "will_create_content": predicted_engagement * 0.6,
                "will_engage_socially": predicted_engagement * 0.9,
                "will_complete_challenges": predicted_engagement * 0.4,
                "will_advance_level": predicted_engagement * 0.3
            }
            
            # Risk assessment
            churn_risk = max(0, 1 - predicted_engagement - (profile.current_streak * 0.01))
            
            return {
                "user_id": user_id,
                "prediction_period_days": prediction_days,
                "overall_engagement_score": round(predicted_engagement * 100, 2),
                "action_probabilities": {k: round(v, 3) for k, v in action_probabilities.items()},
                "churn_risk": round(churn_risk, 3),
                "recommendations": await self._generate_engagement_recommendations(profile, predicted_engagement),
                "confidence": 0.75,  # Model confidence
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting user engagement: {e}")
            return {"error": str(e)}
    
    async def _generate_engagement_recommendations(
        self,
        profile: UserGamificationProfile,
        predicted_engagement: float
    ) -> List[Dict[str, Any]]:
        """Generate personalized engagement recommendations"""
        recommendations = []
        
        # Low engagement recommendations
        if predicted_engagement < 0.5:
            recommendations.append({
                "type": "re_engagement",
                "priority": "high",
                "title": "Re-engagement Campaign",
                "description": "User shows low engagement, needs intervention",
                "actions": [
                    "Send personalized challenge invitation",
                    "Offer bonus points for next activity",
                    "Provide tutorial for unused features",
                    "Send achievement progress reminder"
                ]
            })
        
        # Streak recommendations
        if profile.current_streak < 7:
            recommendations.append({
                "type": "streak_building",
                "priority": "medium",
                "title": "Build Activity Streak",
                "description": "Help user establish consistent activity pattern",
                "actions": [
                    "Send daily login reminders",
                    "Offer streak recovery bonus",
                    "Create easy daily challenges",
                    "Show streak progress prominently"
                ]
            })
        
        # Level progression recommendations
        level_progress = (profile.experience_points - self.level_thresholds[profile.current_level - 1]) / \
                        (self.level_thresholds[profile.current_level] - self.level_thresholds[profile.current_level - 1])
        
        if level_progress < 0.3:
            recommendations.append({
                "type": "level_progression",
                "priority": "medium",
                "title": "Level Up Motivation",
                "description": "Encourage progress toward next level",
                "actions": [
                    "Show progress to next level",
                    "Suggest high-value activities",
                    "Offer experience boost events",
                    "Display level benefits preview"
                ]
            })
        
        return recommendations
    
    async def optimize_gamification_system(self) -> Dict[str, Any]:
        """Analyze and optimize gamification system performance"""
        try:
            if not self._ml_models_initialized:
                await self._initialize_ml_models()
            
            # Analyze current performance
            recent_period = (datetime.now() - timedelta(days=30), datetime.now())
            metrics = await self.analyze_gamification_effectiveness(recent_period)
            
            optimizations = []
            
            # Point system optimization
            if metrics.average_engagement_score < 60:
                optimizations.append({
                    "category": "point_system",
                    "priority": "high",
                    "issue": "Low average engagement score",
                    "recommendation": "Increase point rewards for key actions",
                    "expected_impact": "+15% engagement",
                    "implementation": [
                        "Increase content upload points by 20%",
                        "Add bonus multipliers for streaks",
                        "Introduce daily point bonuses",
                        "Create point boost events"
                    ]
                })
            
            # Badge system optimization
            badge_engagement = metrics.element_effectiveness.get("badges", 0)
            if badge_engagement < 0.5:
                optimizations.append({
                    "category": "badge_system",
                    "priority": "medium",
                    "issue": "Low badge system engagement",
                    "recommendation": "Redesign badge requirements and rewards",
                    "expected_impact": "+10% badge participation",
                    "implementation": [
                        "Create more achievable milestone badges",
                        "Add social sharing for badge achievements",
                        "Implement badge collections and sets",
                        "Increase badge point values"
                    ]
                })
            
            # Challenge system optimization
            if metrics.challenges_completed / metrics.total_active_users < 0.3:
                optimizations.append({
                    "category": "challenge_system",
                    "priority": "medium",
                    "issue": "Low challenge participation",
                    "recommendation": "Create more engaging and accessible challenges",
                    "expected_impact": "+25% challenge completion",
                    "implementation": [
                        "Reduce challenge difficulty for beginners",
                        "Add team-based challenges",
                        "Implement progressive challenge difficulty",
                        "Offer better challenge rewards"
                    ]
                })
            
            # Retention optimization
            if metrics.retention_rate < 0.7:
                optimizations.append({
                    "category": "retention",
                    "priority": "high",
                    "issue": "Low user retention rate",
                    "recommendation": "Implement retention-focused features",
                    "expected_impact": "+20% retention",
                    "implementation": [
                        "Create comeback bonuses for returning users",
                        "Implement push notifications for achievements",
                        "Add social features to increase stickiness",
                        "Design habit-forming daily quests"
                    ]
                })
            
            return {
                "analysis_period": f"{recent_period[0].strftime('%Y-%m-%d')} to {recent_period[1].strftime('%Y-%m-%d')}",
                "current_performance": {
                    "average_engagement": round(metrics.average_engagement_score, 2),
                    "retention_rate": round(metrics.retention_rate * 100, 2),
                    "challenges_completion_rate": round((metrics.challenges_completed / metrics.total_active_users) * 100, 2) if metrics.total_active_users > 0 else 0
                },
                "optimizations": optimizations,
                "priority_actions": [opt for opt in optimizations if opt["priority"] == "high"],
                "estimated_improvement": "+15-30% overall engagement",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing gamification system: {e}")
            return {"error": str(e)}
    
    async def generate_leaderboard(
        self,
        leaderboard_type: str = "points",
        time_period: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Generate leaderboard for specified metric and time period"""
        try:
            # Default to last 30 days if no period specified
            if not time_period:
                end_time = datetime.now()
                start_time = end_time - timedelta(days=30)
                time_period = (start_time, end_time)
            
            start_time, end_time = time_period
            
            # Filter events by time period
            period_events = [
                event for event in self.gamification_events
                if start_time <= event.timestamp <= end_time
            ]
            
            # Calculate leaderboard based on type
            user_scores = defaultdict(int)
            
            if leaderboard_type == "points":
                for event in period_events:
                    user_scores[event.user_id] += event.points_earned
            elif leaderboard_type == "streaks":
                for user_id, profile in self.user_profiles.items():
                    user_scores[user_id] = profile.current_streak
            elif leaderboard_type == "levels":
                for user_id, profile in self.user_profiles.items():
                    user_scores[user_id] = profile.current_level
            elif leaderboard_type == "badges":
                for user_id, profile in self.user_profiles.items():
                    user_scores[user_id] = len(profile.badges_earned)
            
            # Sort and format leaderboard
            sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            leaderboard = []
            for rank, (user_id, score) in enumerate(sorted_users, 1):
                profile = self.user_profiles.get(user_id)
                leaderboard.append({
                    "rank": rank,
                    "user_id": user_id,
                    "score": score,
                    "level": profile.current_level if profile else 1,
                    "badges": len(profile.badges_earned) if profile else 0,
                    "engagement_score": round(profile.engagement_score, 2) if profile else 0
                })
            
            # Update user leaderboard positions
            for entry in leaderboard:
                user_id = entry["user_id"]
                if user_id in self.user_profiles:
                    self.user_profiles[user_id].leaderboard_positions[leaderboard_type] = entry["rank"]
            
            return leaderboard
            
        except Exception as e:
            self.logger.error(f"Error generating leaderboard: {e}")
            return []
    
    # Redis caching methods
    async def _cache_gamification_event(self, event -> None: GamificationEvent) -> None:
        """Cache gamification event in Redis"""
        if self.redis_client:
            try:
                key = f"gam_event:{event.event_id}"
                data = {
                    "user_id": event.user_id,
                    "action_type": event.action_type.value,
                    "points_earned": event.points_earned,
                    "timestamp": event.timestamp.isoformat()
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 86400)  # 24 hour expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    async def _cache_user_profile(self, profile -> None: UserGamificationProfile) -> None:
        """Cache user profile in Redis"""
        if self.redis_client:
            try:
                key = f"gam_profile:{profile.user_id}"
                data = {
                    "total_points": profile.total_points,
                    "current_level": profile.current_level,
                    "engagement_score": profile.engagement_score,
                    "current_streak": profile.current_streak,
                    "badges_count": len(profile.badges_earned),
                    "updated_at": datetime.now().isoformat()
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 3600)  # 1 hour expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    async def _cache_campaign(self, campaign -> None: GamificationCampaign) -> None:
        """Cache campaign in Redis"""
        if self.redis_client:
            try:
                key = f"gam_campaign:{campaign.campaign_id}"
                data = {
                    "name": campaign.name,
                    "start_date": campaign.start_date.isoformat(),
                    "end_date": campaign.end_date.isoformat(),
                    "participation_count": campaign.participation_count,
                    "success_rate": campaign.success_rate
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 604800)  # 7 day expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    def get_gamification_summary(self) -> Dict[str, Any]:
        """Get summary of gamification system performance"""
        try:
            total_users = len(self.user_profiles)
            total_events = len(self.gamification_events)
            
            # Calculate averages
            avg_engagement = statistics.mean([p.engagement_score for p in self.user_profiles.values()]) if self.user_profiles else 0
            avg_level = statistics.mean([p.current_level for p in self.user_profiles.values()]) if self.user_profiles else 0
            total_points = sum(p.total_points for p in self.user_profiles.values())
            total_badges = sum(len(p.badges_earned) for p in self.user_profiles.values())
            
            return {
                "system_stats": {
                    "total_users": total_users,
                    "total_events": total_events,
                    "total_points_distributed": total_points,
                    "total_badges_awarded": total_badges,
                    "active_campaigns": len(self.campaigns)
                },
                "performance_metrics": {
                    "average_engagement_score": round(avg_engagement, 2),
                    "average_user_level": round(avg_level, 2),
                    "ml_models_initialized": self._ml_models_initialized,
                    "redis_connected": self.redis_client is not None
                },
                "recent_activity": {
                    "events_last_hour": len([
                        e for e in self.gamification_events 
                        if (datetime.now() - e.timestamp).total_seconds() < 3600
                    ]),
                    "active_users_today": len([
                        p for p in self.user_profiles.values()
                        if (datetime.now() - p.last_activity).days == 0
                    ])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting gamification summary: {e}")
            return {"error": str(e)}


class AdvancedGamificationIntelligenceEcosystem:
    """
    ENRICHISSEMENTS MASSIFS:
    - NFT gamification analytics
    - Blockchain achievement tracking
    - Social gaming intelligence
    - Virtual economy analytics
    - Tournament performance analytics
    - Guild collaboration metrics
    - Reward optimization AI
    - Engagement prediction models
    - Competitive gaming analytics
    - Gamification ROI measurement
    """
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.nft_achievement_system = {}
        self.blockchain_tracker = None
        self.social_gaming_engine = None
        self.virtual_economy_models = {}
        self.tournament_analytics = {}
        
    # === ENRICHISSEMENTS MASSIFS ===
    
    # 1. NFT GAMIFICATION ANALYTICS
    async def setup_nft_gamification_analytics(self) -> None:
        """Setup NFT gamification analytics"""
        await self.configure_nft_achievement_tracking()
        await self.setup_rare_badge_value_analytics()
        await self.configure_collectible_trading_analytics()
        await self.setup_nft_reward_optimization()
    
    async def configure_nft_achievement_tracking(self) -> None:
        """Configure NFT achievement tracking"""
        self.logger.info("🏆 Setting up NFT achievement tracking...")
        # NFT achievement tracking implementation
    
    async def setup_rare_badge_value_analytics(self) -> None:
        """Setup rare badge value analytics"""
        self.logger.info("💎 Setting up rare badge value analytics...")
        # Rare badge value analytics implementation
    
    async def configure_collectible_trading_analytics(self) -> None:
        """Configure collectible trading analytics"""
        self.logger.info("🔄 Setting up collectible trading analytics...")
        # Collectible trading analytics implementation
    
    async def setup_nft_reward_optimization(self) -> None:
        """Setup NFT reward optimization"""
        self.logger.info("⚡ Setting up NFT reward optimization...")
        # NFT reward optimization implementation
    
    # 2. BLOCKCHAIN GAMING INTELLIGENCE
    async def setup_blockchain_gaming_intelligence(self) -> None:
        """Setup blockchain gaming intelligence"""
        await self.configure_smart_contract_gaming_analytics()
        await self.setup_decentralized_tournament_tracking()
        await self.configure_crypto_reward_analytics()
        await self.setup_blockchain_leaderboard_intelligence()
    
    async def configure_smart_contract_gaming_analytics(self) -> None:
        """Configure smart contract gaming analytics"""
        self.logger.info("⛓️ Setting up smart contract gaming analytics...")
        # Smart contract gaming analytics implementation
    
    async def setup_decentralized_tournament_tracking(self) -> None:
        """Setup decentralized tournament tracking"""
        self.logger.info("🏟️ Setting up decentralized tournament tracking...")
        # Decentralized tournament tracking implementation
    
    async def configure_crypto_reward_analytics(self) -> None:
        """Configure crypto reward analytics"""
        self.logger.info("💰 Setting up crypto reward analytics...")
        # Crypto reward analytics implementation
    
    async def setup_blockchain_leaderboard_intelligence(self) -> None:
        """Setup blockchain leaderboard intelligence"""
        self.logger.info("🏅 Setting up blockchain leaderboard intelligence...")
        # Blockchain leaderboard intelligence implementation
    
    # 3. SOCIAL GAMING ANALYTICS
    async def setup_social_gaming_analytics(self) -> None:
        """Setup social gaming analytics"""
        await self.configure_guild_performance_tracking()
        await self.setup_collaborative_quest_analytics()
        await self.configure_social_competition_metrics()
        await self.setup_community_engagement_optimization()
    
    async def configure_guild_performance_tracking(self) -> None:
        """Configure guild performance tracking"""
        self.logger.info("🛡️ Setting up guild performance tracking...")
        # Guild performance tracking implementation
    
    async def setup_collaborative_quest_analytics(self) -> None:
        """Setup collaborative quest analytics"""
        self.logger.info("🗡️ Setting up collaborative quest analytics...")
        # Collaborative quest analytics implementation
    
    async def configure_social_competition_metrics(self) -> None:
        """Configure social competition metrics"""
        self.logger.info("🏆 Setting up social competition metrics...")
        # Social competition metrics implementation
    
    async def setup_community_engagement_optimization(self) -> None:
        """Setup community engagement optimization"""
        self.logger.info("🤝 Setting up community engagement optimization...")
        # Community engagement optimization implementation
    
    # 4. VIRTUAL ECONOMY INTELLIGENCE
    async def setup_virtual_economy_intelligence(self) -> None:
        """Setup virtual economy intelligence"""
        await self.configure_virtual_currency_analytics()
        await self.setup_marketplace_transaction_tracking()
        await self.configure_reward_economy_optimization()
        await self.setup_gamification_roi_analytics()
    
    async def configure_virtual_currency_analytics(self) -> None:
        """Configure virtual currency analytics"""
        self.logger.info("💱 Setting up virtual currency analytics...")
        # Virtual currency analytics implementation
    
    async def setup_marketplace_transaction_tracking(self) -> None:
        """Setup marketplace transaction tracking"""
        self.logger.info("🛒 Setting up marketplace transaction tracking...")
        # Marketplace transaction tracking implementation
    
    async def configure_reward_economy_optimization(self) -> None:
        """Configure reward economy optimization"""
        self.logger.info("🎯 Setting up reward economy optimization...")
        # Reward economy optimization implementation
    
    async def setup_gamification_roi_analytics(self) -> None:
        """Setup gamification ROI analytics"""
        self.logger.info("📊 Setting up gamification ROI analytics...")
        # Gamification ROI analytics implementation