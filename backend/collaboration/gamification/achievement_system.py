"""Achievement System - Multi-Dimensional Achievement Engine
==========================================================

Advanced achievement system providing:
- Multi-category achievement tracking
- Progressive achievement tiers
- Dynamic achievement unlocking
- Achievement progress monitoring
- Rule-based achievement generation
- Social achievement sharing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class AchievementType(Enum):
    """Types of achievements"""
    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    ENGAGEMENT = "engagement"
    SKILL_DEVELOPMENT = "skill_development"
    COMMUNITY = "community"
    MILESTONE = "milestone"
    SPECIAL_EVENT = "special_event"
    CONSISTENCY = "consistency"
    INNOVATION = "innovation"
    LEADERSHIP = "leadership"


class AchievementTier(Enum):
    """Achievement tier levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"


class AchievementStatus(Enum):
    """Achievement status"""
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLAIMED = "claimed"
    EXPIRED = "expired"


@dataclass
class AchievementRule:
    """Achievement rule definition"""
    rule_id: str
    rule_type: str  # count, threshold, sequence, time_based
    conditions: Dict[str, Any]
    target_value: Union[int, float]
    time_window: Optional[timedelta] = None
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.rule_id:
            self.rule_id = str(uuid.uuid4())


@dataclass
class Achievement:
    """Achievement definition"""
    achievement_id: str
    name: str
    description: str
    achievement_type: AchievementType
    tier: AchievementTier
    icon: str = ""
    points_value: int = 100
    rules: List[AchievementRule] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_secret: bool = False
    is_repeatable: bool = False
    expiry_date: Optional[datetime] = None
    unlock_level: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.achievement_id:
            self.achievement_id = str(uuid.uuid4())


@dataclass
class AchievementProgress:
    """User's progress on an achievement"""
    progress_id: str
    user_id: str
    achievement_id: str
    current_value: Union[int, float] = 0
    target_value: Union[int, float] = 0
    progress_percentage: float = 0.0
    status: AchievementStatus = AchievementStatus.LOCKED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    progress_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.progress_id:
            self.progress_id = str(uuid.uuid4())


@dataclass
class UserAchievements:
    """User's achievement collection"""
    user_id: str
    total_achievements: int = 0
    total_points: int = 0
    achievements_by_tier: Dict[str, int] = field(default_factory=dict)
    achievements_by_type: Dict[str, int] = field(default_factory=dict)
    completed_achievements: List[str] = field(default_factory=list)
    in_progress_achievements: List[str] = field(default_factory=list)
    recent_achievements: List[str] = field(default_factory=list)
    achievement_level: int = 1
    
    def __post_init__(self):
        if not self.achievements_by_tier:
            self.achievements_by_tier = {tier.value: 0 for tier in AchievementTier}
        if not self.achievements_by_type:
            self.achievements_by_type = {atype.value: 0 for atype in AchievementType}


class AchievementSystem:
    """
    Multi-Dimensional Achievement Engine
    
    Provides comprehensive achievement tracking, progress monitoring,
    and dynamic achievement generation for enhanced user engagement.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the achievement system"""
        self.config = config or {}
        
        # System settings
        self.auto_claim_enabled = self.config.get('auto_claim_enabled', True)
        self.achievement_notifications = self.config.get('notifications_enabled', True)
        self.max_achievements_per_user = self.config.get('max_achievements', 1000)
        
        # Point values by tier
        self.tier_point_multipliers = self.config.get('tier_multipliers', {
            AchievementTier.BRONZE.value: 1.0,
            AchievementTier.SILVER.value: 2.0,
            AchievementTier.GOLD.value: 3.5,
            AchievementTier.PLATINUM.value: 5.0,
            AchievementTier.DIAMOND.value: 8.0,
            AchievementTier.LEGENDARY.value: 15.0
        })
        
        # Data storage
        self.achievements = {}
        self.user_progress = defaultdict(dict)  # user_id -> achievement_id -> progress
        self.user_achievements = {}
        self.achievement_categories = defaultdict(list)
        
        # Achievement rules and triggers
        self.achievement_triggers = defaultdict(list)
        self.dynamic_achievements = {}
        
        # Analytics
        self.achievement_stats = defaultdict(dict)
        self.completion_rates = defaultdict(float)
        
        logger.info("AchievementSystem initialized with multi-dimensional tracking")
    
    async def create_achievement(
        self,
        name: str,
        description: str,
        achievement_type: AchievementType,
        tier: AchievementTier,
        rules: List[AchievementRule],
        points_value: Optional[int] = None,
        rewards: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Achievement:
        """
        Create a new achievement
        
        Args:
            name: Achievement name
            description: Achievement description
            achievement_type: Type of achievement
            tier: Achievement tier
            rules: List of achievement rules
            points_value: Points awarded (auto-calculated if not provided)
            rewards: Additional rewards
            metadata: Achievement metadata
            
        Returns:
            Created achievement
        """
        try:
            # Calculate points if not provided
            if points_value is None:
                base_points = 100
                multiplier = self.tier_point_multipliers.get(tier.value, 1.0)
                points_value = int(base_points * multiplier)
            
            achievement = Achievement(
                achievement_id=str(uuid.uuid4()),
                name=name,
                description=description,
                achievement_type=achievement_type,
                tier=tier,
                points_value=points_value,
                rules=rules,
                rewards=rewards or {},
                metadata=metadata or {}
            )
            
            self.achievements[achievement.achievement_id] = achievement
            self.achievement_categories[achievement_type.value].append(achievement.achievement_id)
            
            # Set up achievement triggers
            await self._setup_achievement_triggers(achievement)
            
            logger.info(f"Achievement '{name}' created with {points_value} points")
            return achievement
            
        except Exception as e:
            logger.error(f"Failed to create achievement: {str(e)}")
            raise
    
    async def track_user_activity(
        self,
        user_id: str,
        activity_type: str,
        activity_data: Dict[str, Any]
    ):
        """
        Track user activity and update achievement progress
        
        Args:
            user_id: User identifier
            activity_type: Type of activity
            activity_data: Activity data and context
        """
        try:
            # Initialize user achievements if needed
            if user_id not in self.user_achievements:
                self.user_achievements[user_id] = UserAchievements(user_id=user_id)
            
            # Find relevant achievements for this activity
            relevant_achievements = await self._find_relevant_achievements(
                activity_type, activity_data
            )
            
            # Update progress for each relevant achievement
            for achievement_id in relevant_achievements:
                await self._update_achievement_progress(
                    user_id, achievement_id, activity_type, activity_data
                )
            
            # Check for newly unlocked achievements
            await self._check_unlocked_achievements(user_id)
            
            logger.debug(f"Activity tracked for user {user_id}: {activity_type}")
            
        except Exception as e:
            logger.error(f"Failed to track user activity: {str(e)}")
    
    async def get_user_achievements(
        self,
        user_id: str,
        include_locked: bool = False,
        category: Optional[AchievementType] = None
    ) -> Dict[str, Any]:
        """
        Get user's achievement status and progress
        
        Args:
            user_id: User identifier
            include_locked: Whether to include locked achievements
            category: Filter by achievement category
            
        Returns:
            User achievement data
        """
        try:
            if user_id not in self.user_achievements:
                self.user_achievements[user_id] = UserAchievements(user_id=user_id)
            
            user_data = self.user_achievements[user_id]
            user_progress = self.user_progress[user_id]
            
            # Get achievements with progress
            achievements_data = []
            
            for achievement_id, achievement in self.achievements.items():
                # Filter by category if specified
                if category and achievement.achievement_type != category:
                    continue
                
                progress = user_progress.get(achievement_id)
                
                # Skip locked achievements if not requested
                if (not include_locked and 
                    (not progress or progress.status == AchievementStatus.LOCKED)):
                    continue
                
                achievement_data = {
                    'achievement_id': achievement_id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'type': achievement.achievement_type.value,
                    'tier': achievement.tier.value,
                    'points_value': achievement.points_value,
                    'icon': achievement.icon,
                    'is_secret': achievement.is_secret,
                    'progress': {
                        'status': progress.status.value if progress else 'locked',
                        'current_value': progress.current_value if progress else 0,
                        'target_value': progress.target_value if progress else 0,
                        'percentage': progress.progress_percentage if progress else 0.0,
                        'completed_at': progress.completed_at.isoformat() if progress and progress.completed_at else None
                    }
                }
                
                achievements_data.append(achievement_data)
            
            return {
                'user_id': user_id,
                'summary': {
                    'total_achievements': user_data.total_achievements,
                    'total_points': user_data.total_points,
                    'achievement_level': user_data.achievement_level,
                    'by_tier': user_data.achievements_by_tier,
                    'by_type': user_data.achievements_by_type
                },
                'achievements': achievements_data,
                'recent_achievements': await self._get_recent_achievements(user_id),
                'recommended_achievements': await self._get_recommended_achievements(user_id)
            }
            
        except Exception as e:
            logger.error(f"Failed to get user achievements: {str(e)}")
            return {}
    
    async def claim_achievement(
        self,
        user_id: str,
        achievement_id: str
    ) -> Dict[str, Any]:
        """
        Claim a completed achievement
        
        Args:
            user_id: User identifier
            achievement_id: Achievement to claim
            
        Returns:
            Claim result with rewards
        """
        try:
            if achievement_id not in self.achievements:
                raise ValueError(f"Achievement {achievement_id} not found")
            
            if user_id not in self.user_progress:
                raise ValueError(f"No progress found for user {user_id}")
            
            progress = self.user_progress[user_id].get(achievement_id)
            
            if not progress:
                raise ValueError(f"No progress found for achievement {achievement_id}")
            
            if progress.status != AchievementStatus.COMPLETED:
                raise ValueError(f"Achievement {achievement_id} not completed")
            
            if progress.status == AchievementStatus.CLAIMED:
                raise ValueError(f"Achievement {achievement_id} already claimed")
            
            achievement = self.achievements[achievement_id]
            
            # Mark as claimed
            progress.status = AchievementStatus.CLAIMED
            progress.claimed_at = datetime.now()
            
            # Update user achievements
            user_data = self.user_achievements[user_id]
            user_data.total_points += achievement.points_value
            
            # Distribute rewards
            rewards_granted = await self._distribute_achievement_rewards(
                user_id, achievement
            )
            
            # Send notification
            if self.achievement_notifications:
                await self._send_achievement_notification(user_id, achievement)
            
            logger.info(f"Achievement '{achievement.name}' claimed by user {user_id}")
            
            return {
                'achievement_id': achievement_id,
                'points_awarded': achievement.points_value,
                'rewards': rewards_granted,
                'claimed_at': progress.claimed_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to claim achievement: {str(e)}")
            raise
    
    async def create_dynamic_achievement(
        self,
        user_id: str,
        template_type: str,
        parameters: Dict[str, Any]
    ) -> Achievement:
        """
        Create personalized achievement for user
        
        Args:
            user_id: Target user
            template_type: Achievement template type
            parameters: Personalization parameters
            
        Returns:
            Created dynamic achievement
        """
        try:
            # Generate personalized achievement based on user's activity patterns
            achievement_data = await self._generate_personalized_achievement(
                user_id, template_type, parameters
            )
            
            # Create the achievement
            achievement = await self.create_achievement(
                name=achievement_data['name'],
                description=achievement_data['description'],
                achievement_type=AchievementType(achievement_data['type']),
                tier=AchievementTier(achievement_data['tier']),
                rules=achievement_data['rules'],
                points_value=achievement_data['points'],
                metadata={
                    'dynamic': True,
                    'user_specific': user_id,
                    'template_type': template_type,
                    'generated_at': datetime.now().isoformat()
                }
            )
            
            # Store as dynamic achievement
            self.dynamic_achievements[achievement.achievement_id] = {
                'user_id': user_id,
                'template_type': template_type,
                'parameters': parameters
            }
            
            # Initialize progress for the user
            await self._initialize_achievement_progress(user_id, achievement.achievement_id)
            
            logger.info(f"Dynamic achievement created for user {user_id}: {achievement.name}")
            return achievement
            
        except Exception as e:
            logger.error(f"Failed to create dynamic achievement: {str(e)}")
            raise
    
    async def _find_relevant_achievements(
        self,
        activity_type: str,
        activity_data: Dict[str, Any]
    ) -> List[str]:
        """Find achievements relevant to the activity"""
        relevant_achievements = []
        
        for achievement_id, achievement in self.achievements.items():
            # Check if achievement rules match the activity
            for rule in achievement.rules:
                if await self._rule_matches_activity(rule, activity_type, activity_data):
                    relevant_achievements.append(achievement_id)
                    break
        
        return relevant_achievements
    
    async def _rule_matches_activity(
        self,
        rule: AchievementRule,
        activity_type: str,
        activity_data: Dict[str, Any]
    ) -> bool:
        """Check if achievement rule matches the activity"""
        conditions = rule.conditions
        
        # Check activity type match
        if 'activity_types' in conditions:
            if activity_type not in conditions['activity_types']:
                return False
        
        # Check specific conditions
        if 'content_type' in conditions and 'content_type' in activity_data:
            if activity_data['content_type'] not in conditions['content_type']:
                return False
        
        if 'collaboration_type' in conditions and 'collaboration_type' in activity_data:
            if activity_data['collaboration_type'] not in conditions['collaboration_type']:
                return False
        
        return True
    
    async def _update_achievement_progress(
        self,
        user_id: str,
        achievement_id: str,
        activity_type: str,
        activity_data: Dict[str, Any]
    ):
        """Update user's progress on an achievement"""
        achievement = self.achievements[achievement_id]
        
        # Get or create progress record
        if achievement_id not in self.user_progress[user_id]:
            await self._initialize_achievement_progress(user_id, achievement_id)
        
        progress = self.user_progress[user_id][achievement_id]
        
        # Skip if already completed and not repeatable
        if (progress.status == AchievementStatus.COMPLETED and 
            not achievement.is_repeatable):
            return
        
        # Calculate progress update based on rules
        progress_increment = await self._calculate_progress_increment(
            achievement, activity_type, activity_data
        )
        
        if progress_increment > 0:
            # Update progress
            old_value = progress.current_value
            progress.current_value += progress_increment
            
            # Ensure we don't exceed target
            if progress.current_value > progress.target_value:
                progress.current_value = progress.target_value
            
            # Update percentage
            progress.progress_percentage = (
                progress.current_value / progress.target_value * 100
                if progress.target_value > 0 else 0
            )
            
            # Check if completed
            if progress.current_value >= progress.target_value:
                progress.status = AchievementStatus.COMPLETED
                progress.completed_at = datetime.now()
                
                # Auto-claim if enabled
                if self.auto_claim_enabled:
                    await self.claim_achievement(user_id, achievement_id)
                
                # Update user achievement counts
                await self._update_user_achievement_counts(user_id, achievement)
            elif progress.status == AchievementStatus.LOCKED:
                progress.status = AchievementStatus.IN_PROGRESS
                progress.started_at = datetime.now()
            
            # Record progress history
            progress.progress_history.append({
                'timestamp': datetime.now().isoformat(),
                'activity_type': activity_type,
                'old_value': old_value,
                'new_value': progress.current_value,
                'increment': progress_increment
            })
    
    async def _initialize_achievement_progress(self, user_id: str, achievement_id: str):
        """Initialize progress record for user and achievement"""
        achievement = self.achievements[achievement_id]
        
        # Calculate target value from rules
        target_value = 0
        for rule in achievement.rules:
            if rule.rule_type in ['count', 'threshold']:
                target_value = max(target_value, rule.target_value)
        
        progress = AchievementProgress(
            progress_id=str(uuid.uuid4()),
            user_id=user_id,
            achievement_id=achievement_id,
            target_value=target_value,
            status=AchievementStatus.LOCKED
        )
        
        self.user_progress[user_id][achievement_id] = progress
    
    async def _calculate_progress_increment(
        self,
        achievement: Achievement,
        activity_type: str,
        activity_data: Dict[str, Any]
    ) -> float:
        """Calculate how much progress this activity contributes"""
        total_increment = 0
        
        for rule in achievement.rules:
            if rule.rule_type == 'count':
                # Simple count increment
                total_increment += 1
            elif rule.rule_type == 'threshold':
                # Value-based increment
                value_field = rule.conditions.get('value_field', 'value')
                increment = activity_data.get(value_field, 0)
                total_increment += increment
            elif rule.rule_type == 'sequence':
                # Sequential achievement
                total_increment += 1  # Simplified
        
        return total_increment
    
    async def _update_user_achievement_counts(self, user_id: str, achievement: Achievement):
        """Update user's achievement statistics"""
        user_data = self.user_achievements[user_id]
        
        # Update totals
        user_data.total_achievements += 1
        
        # Update by tier
        tier_key = achievement.tier.value
        user_data.achievements_by_tier[tier_key] += 1
        
        # Update by type
        type_key = achievement.achievement_type.value
        user_data.achievements_by_type[type_key] += 1
        
        # Add to completed list
        if achievement.achievement_id not in user_data.completed_achievements:
            user_data.completed_achievements.append(achievement.achievement_id)
        
        # Add to recent achievements (keep last 10)
        user_data.recent_achievements.append(achievement.achievement_id)
        user_data.recent_achievements = user_data.recent_achievements[-10:]
        
        # Update achievement level based on total points
        await self._update_achievement_level(user_id)
    
    async def _update_achievement_level(self, user_id: str):
        """Update user's achievement level based on total points"""
        user_data = self.user_achievements[user_id]
        
        # Simple level calculation (in production, would use more sophisticated curves)
        level_thresholds = [0, 100, 300, 600, 1000, 1500, 2500, 4000, 6000, 10000]
        
        for level, threshold in enumerate(level_thresholds):
            if user_data.total_points >= threshold:
                user_data.achievement_level = level + 1
            else:
                break
    
    async def _distribute_achievement_rewards(
        self,
        user_id: str,
        achievement: Achievement
    ) -> Dict[str, Any]:
        """Distribute rewards for claimed achievement"""
        rewards_granted = {}
        
        if achievement.rewards:
            for reward_type, reward_value in achievement.rewards.items():
                if reward_type == 'bonus_points':
                    # Award bonus points
                    user_data = self.user_achievements[user_id]
                    user_data.total_points += reward_value
                    rewards_granted['bonus_points'] = reward_value
                
                elif reward_type == 'badge':
                    # Award special badge
                    rewards_granted['badge'] = reward_value
                
                elif reward_type == 'unlock_feature':
                    # Unlock special feature
                    rewards_granted['feature_unlock'] = reward_value
        
        return rewards_granted
    
    async def _send_achievement_notification(self, user_id: str, achievement: Achievement):
        """Send achievement notification to user"""
        # Placeholder for notification system integration
        logger.info(f"Achievement notification sent to {user_id}: {achievement.name}")
    
    async def _get_recent_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's recent achievements"""
        if user_id not in self.user_achievements:
            return []
        
        user_data = self.user_achievements[user_id]
        recent_data = []
        
        for achievement_id in user_data.recent_achievements[-5:]:  # Last 5
            if achievement_id in self.achievements:
                achievement = self.achievements[achievement_id]
                progress = self.user_progress[user_id].get(achievement_id)
                
                recent_data.append({
                    'achievement_id': achievement_id,
                    'name': achievement.name,
                    'tier': achievement.tier.value,
                    'points': achievement.points_value,
                    'completed_at': progress.completed_at.isoformat() if progress and progress.completed_at else None
                })
        
        return recent_data
    
    async def _get_recommended_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recommended achievements for user"""
        recommendations = []
        
        # Get user's activity patterns and suggest relevant achievements
        user_progress = self.user_progress[user_id]
        
        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in user_progress:
                # New achievement - recommend based on type affinity
                recommendations.append({
                    'achievement_id': achievement_id,
                    'name': achievement.name,
                    'type': achievement.achievement_type.value,
                    'tier': achievement.tier.value,
                    'points': achievement.points_value,
                    'reason': 'new_opportunity'
                })
                
                if len(recommendations) >= 5:
                    break
        
        return recommendations
    
    async def _generate_personalized_achievement(
        self,
        user_id: str,
        template_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized achievement based on user patterns"""
        # Analyze user's activity to create personalized achievement
        user_activity = parameters.get('user_activity', {})
        
        if template_type == 'content_streak':
            # Create streak-based achievement
            target_days = parameters.get('target_days', 7)
            content_type = parameters.get('content_type', 'any')
            
            return {
                'name': f'{target_days}-Day {content_type.title()} Creation Streak',
                'description': f'Create {content_type} content for {target_days} consecutive days',
                'type': 'consistency',
                'tier': 'silver' if target_days <= 7 else 'gold',
                'points': target_days * 50,
                'rules': [
                    AchievementRule(
                        rule_id=str(uuid.uuid4()),
                        rule_type='sequence',
                        conditions={'activity_types': ['content_created'], 'content_type': [content_type]},
                        target_value=target_days
                    )
                ]
            }
        
        elif template_type == 'collaboration_goal':
            # Create collaboration-based achievement
            target_collabs = parameters.get('target_collaborations', 5)
            
            return {
                'name': f'Collaboration Champion - {target_collabs} Projects',
                'description': f'Successfully complete {target_collabs} collaboration projects',
                'type': 'collaboration',
                'tier': 'gold',
                'points': target_collabs * 200,
                'rules': [
                    AchievementRule(
                        rule_id=str(uuid.uuid4()),
                        rule_type='count',
                        conditions={'activity_types': ['collaboration_completed']},
                        target_value=target_collabs
                    )
                ]
            }
        
        # Default achievement
        return {
            'name': 'Custom Achievement',
            'description': 'Personalized achievement',
            'type': 'milestone',
            'tier': 'bronze',
            'points': 100,
            'rules': []
        }
    
    async def _setup_achievement_triggers(self, achievement: Achievement):
        """Set up triggers for achievement monitoring"""
        for rule in achievement.rules:
            if 'activity_types' in rule.conditions:
                for activity_type in rule.conditions['activity_types']:
                    self.achievement_triggers[activity_type].append(achievement.achievement_id)
    
    async def _check_unlocked_achievements(self, user_id: str):
        """Check for newly unlocked achievements based on user level/progress"""
        user_data = self.user_achievements[user_id]
        
        for achievement_id, achievement in self.achievements.items():
            # Check if user meets unlock requirements
            if (user_data.achievement_level >= achievement.unlock_level and
                achievement_id not in self.user_progress[user_id]):
                
                # Initialize progress for newly unlocked achievement
                await self._initialize_achievement_progress(user_id, achievement_id)
                
                # Add to in-progress list
                user_data.in_progress_achievements.append(achievement_id)
    
    async def get_achievement_analytics(self) -> Dict[str, Any]:
        """Get comprehensive achievement analytics"""
        total_achievements = len(self.achievements)
        total_users = len(self.user_achievements)
        
        # Calculate completion rates
        completion_stats = {}
        for achievement_id, achievement in self.achievements.items():
            completed_users = 0
            for user_id, user_progress in self.user_progress.items():
                progress = user_progress.get(achievement_id)
                if progress and progress.status == AchievementStatus.COMPLETED:
                    completed_users += 1
            
            completion_rate = completed_users / max(total_users, 1)
            completion_stats[achievement_id] = {
                'name': achievement.name,
                'completion_rate': completion_rate,
                'completed_users': completed_users
            }
        
        # Most/least popular achievements
        sorted_completions = sorted(
            completion_stats.items(),
            key=lambda x: x[1]['completion_rate'],
            reverse=True
        )
        
        return {
            'total_achievements': total_achievements,
            'total_users': total_users,
            'average_achievements_per_user': sum(
                ua.total_achievements for ua in self.user_achievements.values()
            ) / max(total_users, 1),
            'completion_rates': completion_stats,
            'most_popular': sorted_completions[:5],
            'least_popular': sorted_completions[-5:],
            'achievements_by_tier': {
                tier.value: sum(1 for a in self.achievements.values() if a.tier == tier)
                for tier in AchievementTier
            },
            'achievements_by_type': {
                atype.value: sum(1 for a in self.achievements.values() if a.achievement_type == atype)
                for atype in AchievementType
            }
        }


# Export main classes
__all__ = [
    'AchievementSystem',
    'Achievement',
    'AchievementProgress',
    'AchievementRule',
    'UserAchievements',
    'AchievementType',
    'AchievementTier',
    'AchievementStatus'
]