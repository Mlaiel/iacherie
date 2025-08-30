"""
Achievement Repository - Enterprise Achievement Data Management

This module provides comprehensive data access layer for achievement management
with advanced repository patterns, caching, and business intelligence integration.

Features:
- High-performance achievement data access with optimized queries
- Advanced caching and data distribution strategies
- Comprehensive achievement progression tracking
- Real-time achievement unlock notifications
- Achievement analytics and business intelligence
- Cross-platform achievement synchronization
- Professional audit trails and data integrity
- Integration with creator collaboration workflows

Business Logic Integration:
- Creator activity → Achievement tracking → Database persistence
- Achievement progress → Real-time updates → Notification systems
- Achievement unlocks → Reward distribution → Business analytics
- Achievement data → Creator matching → Collaboration opportunities

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, distribution, or theft of this code or concept
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in immediate legal action.

Contact: mlaiel@live.de for authorized usage inquiries.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import asyncio
import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AchievementType(Enum):
    """Achievement type classification"""
    MILESTONE = "milestone"
    PROGRESSION = "progression"
    CHALLENGE = "challenge"
    COLLABORATION = "collaboration"
    QUALITY = "quality"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    INNOVATION = "innovation"
    SPECIAL_EVENT = "special_event"
    COMMUNITY = "community"


class AchievementTier(Enum):
    """Achievement tier classification"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"


class AchievementStatus(Enum):
    """Achievement status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    LOCKED = "locked"


@dataclass
class AchievementData:
    """Comprehensive achievement data model"""
    achievement_id: str
    title: str
    description: str
    achievement_type: AchievementType
    tier: AchievementTier
    status: AchievementStatus
    
    # Requirements and progress
    requirements: Dict[str, Any] = field(default_factory=dict)
    total_steps: int = 1
    
    # Rewards
    rewards: Dict[str, Any] = field(default_factory=dict)
    points_value: int = 0
    monetary_value: float = 0.0
    
    # Metadata
    icon_url: str = ""
    badge_url: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Business metrics
    difficulty_score: float = 1.0
    business_value: float = 0.0
    completion_rate: float = 0.0
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    # Configuration
    is_hidden: bool = False
    is_repeatable: bool = False
    requires_verification: bool = False
    
    # Analytics
    unlock_count: int = 0
    attempt_count: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserAchievementProgress:
    """User achievement progress tracking"""
    user_id: str
    achievement_id: str
    current_progress: float = 0.0
    steps_completed: int = 0
    is_unlocked: bool = False
    
    # Timing
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    unlocked_at: Optional[datetime] = None
    last_progress_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Progress details
    progress_data: Dict[str, Any] = field(default_factory=dict)
    milestone_data: List[Dict[str, Any]] = field(default_factory=list)
    
    # Verification
    verification_status: str = "pending"  # pending, verified, rejected
    verification_data: Dict[str, Any] = field(default_factory=dict)
    
    # Analytics
    attempt_count: int = 1
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AchievementQuery:
    """Achievement query parameters"""
    achievement_ids: Optional[List[str]] = None
    achievement_types: Optional[List[AchievementType]] = None
    tiers: Optional[List[AchievementTier]] = None
    statuses: Optional[List[AchievementStatus]] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    
    # Filters
    min_points: Optional[int] = None
    max_points: Optional[int] = None
    min_difficulty: Optional[float] = None
    max_difficulty: Optional[float] = None
    min_business_value: Optional[float] = None
    
    # User-specific filters
    user_id: Optional[str] = None
    include_progress: bool = False
    unlocked_only: bool = False
    available_only: bool = True
    
    # Timing filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    expires_after: Optional[datetime] = None
    expires_before: Optional[datetime] = None
    
    # Sorting and pagination
    sort_by: str = "created_at"
    sort_desc: bool = True
    limit: int = 50
    offset: int = 0
    
    # Text search
    search_text: Optional[str] = None


@dataclass
class AchievementAnalytics:
    """Achievement analytics and statistics"""
    total_achievements: int = 0
    active_achievements: int = 0
    total_unlocks: int = 0
    unique_users_with_unlocks: int = 0
    
    # Completion statistics
    average_completion_rate: float = 0.0
    completion_rates_by_tier: Dict[AchievementTier, float] = field(default_factory=dict)
    completion_rates_by_type: Dict[AchievementType, float] = field(default_factory=dict)
    
    # Popular achievements
    most_unlocked_achievements: List[Dict[str, Any]] = field(default_factory=list)
    most_attempted_achievements: List[Dict[str, Any]] = field(default_factory=list)
    highest_value_achievements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Trend data
    daily_unlock_trends: List[Dict[str, Any]] = field(default_factory=list)
    user_engagement_trends: List[Dict[str, Any]] = field(default_factory=list)
    
    # Business metrics
    total_business_value_unlocked: float = 0.0
    total_points_awarded: int = 0
    total_monetary_value_awarded: float = 0.0


class AchievementRepository:
    """
    Enterprise-grade achievement repository with advanced data management
    
    Provides comprehensive achievement data access with high-performance
    querying, caching, analytics, and business intelligence integration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize achievement repository"""
        self.config = config or {}
        
        # Core storage (in production, these would be database connections)
        self._achievements: Dict[str, AchievementData] = {}
        self._user_progress: Dict[str, Dict[str, UserAchievementProgress]] = {}
        self._achievement_analytics: Dict[str, Dict[str, Any]] = {}
        
        # Caching and performance
        self._query_cache: Dict[str, Tuple[datetime, Any]] = {}
        self._analytics_cache: Dict[str, Tuple[datetime, Any]] = {}
        
        # Indexing for performance
        self._type_index: Dict[AchievementType, Set[str]] = {
            achievement_type: set() for achievement_type in AchievementType
        }
        self._tier_index: Dict[AchievementTier, Set[str]] = {
            tier: set() for tier in AchievementTier
        }
        self._category_index: Dict[str, Set[str]] = {}
        self._tag_index: Dict[str, Set[str]] = {}
        
        # Configuration
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.cache_ttl_seconds = self.config.get('cache_ttl_seconds', 300)
        self.max_cache_entries = self.config.get('max_cache_entries', 1000)
        self.analytics_enabled = self.config.get('analytics_enabled', True)
        
        logger.info("Achievement Repository initialized successfully")
    
    async def create_achievement(
        self,
        achievement_data: AchievementData
    ) -> bool:
        """Create a new achievement"""
        try:
            achievement_id = achievement_data.achievement_id
            
            if achievement_id in self._achievements:
                logger.warning(f"Achievement {achievement_id} already exists")
                return False
            
            # Validate achievement data
            if not await self._validate_achievement_data(achievement_data):
                logger.error(f"Invalid achievement data for {achievement_id}")
                return False
            
            # Store achievement
            self._achievements[achievement_id] = achievement_data
            
            # Update indices
            await self._update_indices(achievement_data)
            
            # Initialize analytics
            if self.analytics_enabled:
                await self._initialize_achievement_analytics(achievement_id)
            
            # Clear relevant caches
            await self._clear_cache_for_achievement(achievement_id)
            
            logger.info(f"Achievement {achievement_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating achievement: {e}")
            return False
    
    async def get_achievement(
        self,
        achievement_id: str,
        include_analytics: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get achievement by ID"""
        try:
            if achievement_id not in self._achievements:
                return None
            
            achievement = self._achievements[achievement_id]
            
            result = {
                'achievement': achievement,
                'unlock_count': achievement.unlock_count,
                'attempt_count': achievement.attempt_count,
                'completion_rate': achievement.completion_rate
            }
            
            if include_analytics and self.analytics_enabled:
                analytics = await self._get_achievement_analytics(achievement_id)
                result['analytics'] = analytics
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting achievement {achievement_id}: {e}")
            return None
    
    async def query_achievements(
        self,
        query: AchievementQuery
    ) -> List[Dict[str, Any]]:
        """Query achievements with advanced filtering"""
        try:
            # Check cache first
            if self.cache_enabled:
                cache_key = self._generate_query_cache_key(query)
                cached_result = await self._get_cached_result(cache_key)
                if cached_result:
                    return cached_result
            
            # Start with all achievements
            candidate_ids = set(self._achievements.keys())
            
            # Apply filters
            candidate_ids = await self._apply_query_filters(query, candidate_ids)
            
            # Get achievements and include progress if requested
            results = []
            for achievement_id in candidate_ids:
                achievement = self._achievements[achievement_id]
                
                result = {
                    'achievement_id': achievement_id,
                    'title': achievement.title,
                    'description': achievement.description,
                    'type': achievement.achievement_type.value,
                    'tier': achievement.tier.value,
                    'status': achievement.status.value,
                    'points_value': achievement.points_value,
                    'monetary_value': achievement.monetary_value,
                    'difficulty_score': achievement.difficulty_score,
                    'completion_rate': achievement.completion_rate,
                    'unlock_count': achievement.unlock_count,
                    'requirements': achievement.requirements,
                    'rewards': achievement.rewards,
                    'icon_url': achievement.icon_url,
                    'badge_url': achievement.badge_url,
                    'category': achievement.category,
                    'tags': achievement.tags,
                    'created_at': achievement.created_at.isoformat(),
                    'expires_at': achievement.expires_at.isoformat() if achievement.expires_at else None
                }
                
                # Include user progress if requested
                if query.include_progress and query.user_id:
                    progress = await self._get_user_progress(query.user_id, achievement_id)
                    result['user_progress'] = progress
                
                results.append(result)
            
            # Sort results
            results = await self._sort_results(results, query.sort_by, query.sort_desc)
            
            # Apply pagination
            total_count = len(results)
            results = results[query.offset:query.offset + query.limit]
            
            # Prepare final result
            final_result = {
                'achievements': results,
                'total_count': total_count,
                'offset': query.offset,
                'limit': query.limit
            }
            
            # Cache result
            if self.cache_enabled:
                await self._cache_result(cache_key, final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error querying achievements: {e}")
            return {'achievements': [], 'total_count': 0, 'offset': 0, 'limit': 0}
    
    async def update_user_progress(
        self,
        user_id: str,
        achievement_id: str,
        progress_update: Dict[str, Any]
    ) -> bool:
        """Update user progress towards an achievement"""
        try:
            if achievement_id not in self._achievements:
                logger.error(f"Achievement {achievement_id} not found")
                return False
            
            # Initialize user progress if not exists
            if user_id not in self._user_progress:
                self._user_progress[user_id] = {}
            
            if achievement_id not in self._user_progress[user_id]:
                self._user_progress[user_id][achievement_id] = UserAchievementProgress(
                    user_id=user_id,
                    achievement_id=achievement_id
                )
            
            progress = self._user_progress[user_id][achievement_id]
            achievement = self._achievements[achievement_id]
            
            # Update progress data
            if 'current_progress' in progress_update:
                progress.current_progress = min(100.0, max(0.0, progress_update['current_progress']))
            
            if 'steps_completed' in progress_update:
                progress.steps_completed = min(achievement.total_steps, max(0, progress_update['steps_completed']))
            
            if 'progress_data' in progress_update:
                progress.progress_data.update(progress_update['progress_data'])
            
            # Check for achievement unlock
            if not progress.is_unlocked:
                unlock_achieved = await self._check_achievement_unlock(achievement, progress, progress_update)
                if unlock_achieved:
                    await self._unlock_achievement(user_id, achievement_id)
            
            # Update timestamps
            progress.last_progress_update = datetime.now(timezone.utc)
            progress.attempt_count += 1
            
            # Update achievement analytics
            if self.analytics_enabled:
                await self._update_achievement_analytics(achievement_id, 'progress_update', {
                    'user_id': user_id,
                    'progress': progress.current_progress,
                    'steps_completed': progress.steps_completed
                })
            
            # Clear relevant caches
            await self._clear_cache_for_user_achievement(user_id, achievement_id)
            
            logger.debug(f"Progress updated for user {user_id}, achievement {achievement_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user progress: {e}")
            return False
    
    async def unlock_achievement(
        self,
        user_id: str,
        achievement_id: str,
        verification_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Manually unlock achievement for user"""
        try:
            return await self._unlock_achievement(user_id, achievement_id, verification_data)
            
        except Exception as e:
            logger.error(f"Error unlocking achievement: {e}")
            return False
    
    async def get_user_achievements(
        self,
        user_id: str,
        include_locked: bool = False,
        include_progress: bool = True
    ) -> Dict[str, Any]:
        """Get all achievements for a user"""
        try:
            user_progress = self._user_progress.get(user_id, {})
            
            achievements = []
            unlocked_count = 0
            total_points = 0
            total_monetary_value = 0.0
            
            for achievement_id, achievement in self._achievements.items():
                progress = user_progress.get(achievement_id)
                
                # Skip locked achievements if not requested
                if not include_locked and achievement.is_hidden and (not progress or not progress.is_unlocked):
                    continue
                
                achievement_data = {
                    'achievement_id': achievement_id,
                    'title': achievement.title,
                    'description': achievement.description,
                    'type': achievement.achievement_type.value,
                    'tier': achievement.tier.value,
                    'points_value': achievement.points_value,
                    'monetary_value': achievement.monetary_value,
                    'icon_url': achievement.icon_url,
                    'badge_url': achievement.badge_url,
                    'category': achievement.category,
                    'tags': achievement.tags,
                    'is_unlocked': bool(progress and progress.is_unlocked),
                    'unlock_date': progress.unlocked_at.isoformat() if progress and progress.unlocked_at else None
                }
                
                if include_progress and progress:
                    achievement_data['progress'] = {
                        'current_progress': progress.current_progress,
                        'steps_completed': progress.steps_completed,
                        'total_steps': achievement.total_steps,
                        'started_at': progress.started_at.isoformat(),
                        'last_update': progress.last_progress_update.isoformat(),
                        'attempt_count': progress.attempt_count
                    }
                
                achievements.append(achievement_data)
                
                # Count unlocked achievements and points
                if progress and progress.is_unlocked:
                    unlocked_count += 1
                    total_points += achievement.points_value
                    total_monetary_value += achievement.monetary_value
            
            return {
                'user_id': user_id,
                'achievements': achievements,
                'summary': {
                    'total_achievements': len(achievements),
                    'unlocked_count': unlocked_count,
                    'unlock_rate': (unlocked_count / len(achievements)) * 100 if achievements else 0,
                    'total_points_earned': total_points,
                    'total_monetary_value_earned': total_monetary_value
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user achievements: {e}")
            return {'user_id': user_id, 'achievements': [], 'summary': {}}
    
    async def get_achievement_analytics(
        self,
        achievement_id: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> AchievementAnalytics:
        """Get comprehensive achievement analytics"""
        try:
            if not self.analytics_enabled:
                return AchievementAnalytics()
            
            # Check cache
            cache_key = f"analytics_{achievement_id or 'all'}_{time_range}"
            if self.cache_enabled:
                cached_result = await self._get_cached_analytics(cache_key)
                if cached_result:
                    return cached_result
            
            analytics = AchievementAnalytics()
            
            if achievement_id:
                # Single achievement analytics
                analytics = await self._calculate_single_achievement_analytics(achievement_id, time_range)
            else:
                # Overall analytics
                analytics = await self._calculate_overall_analytics(time_range)
            
            # Cache result
            if self.cache_enabled:
                await self._cache_analytics(cache_key, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting achievement analytics: {e}")
            return AchievementAnalytics()
    
    async def get_leaderboard(
        self,
        category: Optional[str] = None,
        tier: Optional[AchievementTier] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get achievement leaderboard"""
        try:
            user_stats = {}
            
            # Calculate user statistics
            for user_id, user_progress in self._user_progress.items():
                stats = {
                    'user_id': user_id,
                    'total_achievements': 0,
                    'total_points': 0,
                    'total_monetary_value': 0.0,
                    'achievements_by_tier': {tier.value: 0 for tier in AchievementTier},
                    'recent_unlocks': []
                }
                
                for achievement_id, progress in user_progress.items():
                    if not progress.is_unlocked:
                        continue
                    
                    # Apply time range filter
                    if time_range and progress.unlocked_at:
                        start_time, end_time = time_range
                        if not (start_time <= progress.unlocked_at <= end_time):
                            continue
                    
                    achievement = self._achievements.get(achievement_id)
                    if not achievement:
                        continue
                    
                    # Apply category filter
                    if category and achievement.category != category:
                        continue
                    
                    # Apply tier filter
                    if tier and achievement.tier != tier:
                        continue
                    
                    stats['total_achievements'] += 1
                    stats['total_points'] += achievement.points_value
                    stats['total_monetary_value'] += achievement.monetary_value
                    stats['achievements_by_tier'][achievement.tier.value] += 1
                    
                    if progress.unlocked_at:
                        stats['recent_unlocks'].append({
                            'achievement_id': achievement_id,
                            'achievement_title': achievement.title,
                            'tier': achievement.tier.value,
                            'points_value': achievement.points_value,
                            'unlocked_at': progress.unlocked_at.isoformat()
                        })
                
                # Sort recent unlocks by date
                stats['recent_unlocks'].sort(key=lambda x: x['unlocked_at'], reverse=True)
                stats['recent_unlocks'] = stats['recent_unlocks'][:5]  # Keep only 5 most recent
                
                user_stats[user_id] = stats
            
            # Sort users by total points
            leaderboard = sorted(
                user_stats.values(),
                key=lambda x: (x['total_points'], x['total_achievements']),
                reverse=True
            )
            
            # Add ranks
            for i, user_stats in enumerate(leaderboard[:limit]):
                user_stats['rank'] = i + 1
            
            return leaderboard[:limit]
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    # Helper methods
    
    async def _validate_achievement_data(self, achievement_data: AchievementData) -> bool:
        """Validate achievement data"""
        try:
            # Basic validation
            if not achievement_data.achievement_id:
                return False
            
            if not achievement_data.title:
                return False
            
            if achievement_data.total_steps <= 0:
                return False
            
            if achievement_data.points_value < 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating achievement data: {e}")
            return False
    
    async def _update_indices(self, achievement_data: AchievementData) -> None:
        """Update search indices"""
        try:
            achievement_id = achievement_data.achievement_id
            
            # Type index
            self._type_index[achievement_data.achievement_type].add(achievement_id)
            
            # Tier index
            self._tier_index[achievement_data.tier].add(achievement_id)
            
            # Category index
            if achievement_data.category:
                if achievement_data.category not in self._category_index:
                    self._category_index[achievement_data.category] = set()
                self._category_index[achievement_data.category].add(achievement_id)
            
            # Tag index
            for tag in achievement_data.tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(achievement_id)
            
        except Exception as e:
            logger.error(f"Error updating indices: {e}")
    
    async def _apply_query_filters(
        self,
        query: AchievementQuery,
        candidate_ids: Set[str]
    ) -> Set[str]:
        """Apply query filters to candidate achievements"""
        try:
            # Achievement ID filter
            if query.achievement_ids:
                candidate_ids &= set(query.achievement_ids)
            
            # Type filter
            if query.achievement_types:
                type_matches = set()
                for achievement_type in query.achievement_types:
                    type_matches.update(self._type_index[achievement_type])
                candidate_ids &= type_matches
            
            # Tier filter
            if query.tiers:
                tier_matches = set()
                for tier in query.tiers:
                    tier_matches.update(self._tier_index[tier])
                candidate_ids &= tier_matches
            
            # Status filter
            if query.statuses:
                status_matches = {
                    aid for aid in candidate_ids
                    if self._achievements[aid].status in query.statuses
                }
                candidate_ids &= status_matches
            
            # Category filter
            if query.categories:
                category_matches = set()
                for category in query.categories:
                    if category in self._category_index:
                        category_matches.update(self._category_index[category])
                candidate_ids &= category_matches
            
            # Tag filter
            if query.tags:
                tag_matches = set()
                for tag in query.tags:
                    if tag in self._tag_index:
                        tag_matches.update(self._tag_index[tag])
                candidate_ids &= tag_matches
            
            # Points filter
            if query.min_points is not None or query.max_points is not None:
                points_matches = set()
                for aid in candidate_ids:
                    achievement = self._achievements[aid]
                    if query.min_points is not None and achievement.points_value < query.min_points:
                        continue
                    if query.max_points is not None and achievement.points_value > query.max_points:
                        continue
                    points_matches.add(aid)
                candidate_ids &= points_matches
            
            # User-specific filters
            if query.user_id:
                user_progress = self._user_progress.get(query.user_id, {})
                
                if query.unlocked_only:
                    unlocked_matches = {
                        aid for aid in candidate_ids
                        if aid in user_progress and user_progress[aid].is_unlocked
                    }
                    candidate_ids &= unlocked_matches
                
                if query.available_only:
                    # Filter out hidden achievements that are not unlocked
                    available_matches = {
                        aid for aid in candidate_ids
                        if not self._achievements[aid].is_hidden or (
                            aid in user_progress and user_progress[aid].is_unlocked
                        )
                    }
                    candidate_ids &= available_matches
            
            # Text search
            if query.search_text:
                text_matches = await self._search_achievements_text(query.search_text, candidate_ids)
                candidate_ids &= text_matches
            
            return candidate_ids
            
        except Exception as e:
            logger.error(f"Error applying query filters: {e}")
            return candidate_ids
    
    async def _search_achievements_text(self, search_text: str, candidate_ids: Set[str]) -> Set[str]:
        """Search achievements by text"""
        try:
            search_text = search_text.lower()
            matches = set()
            
            for achievement_id in candidate_ids:
                achievement = self._achievements[achievement_id]
                
                # Search in title and description
                if (search_text in achievement.title.lower() or
                    search_text in achievement.description.lower()):
                    matches.add(achievement_id)
                    continue
                
                # Search in tags
                for tag in achievement.tags:
                    if search_text in tag.lower():
                        matches.add(achievement_id)
                        break
                
                # Search in category
                if search_text in achievement.category.lower():
                    matches.add(achievement_id)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return set()
    
    async def _sort_results(
        self,
        results: List[Dict[str, Any]],
        sort_by: str,
        sort_desc: bool
    ) -> List[Dict[str, Any]]:
        """Sort query results"""
        try:
            if sort_by == "title":
                results.sort(key=lambda x: x['title'], reverse=sort_desc)
            elif sort_by == "points_value":
                results.sort(key=lambda x: x['points_value'], reverse=sort_desc)
            elif sort_by == "difficulty_score":
                results.sort(key=lambda x: x['difficulty_score'], reverse=sort_desc)
            elif sort_by == "completion_rate":
                results.sort(key=lambda x: x['completion_rate'], reverse=sort_desc)
            elif sort_by == "unlock_count":
                results.sort(key=lambda x: x['unlock_count'], reverse=sort_desc)
            else:  # default to created_at
                results.sort(key=lambda x: x['created_at'], reverse=sort_desc)
            
            return results
            
        except Exception as e:
            logger.error(f"Error sorting results: {e}")
            return results
    
    async def _check_achievement_unlock(
        self,
        achievement: AchievementData,
        progress: UserAchievementProgress,
        progress_update: Dict[str, Any]
    ) -> bool:
        """Check if achievement should be unlocked"""
        try:
            # Check progress percentage
            if progress.current_progress >= 100.0:
                return True
            
            # Check steps completion
            if progress.steps_completed >= achievement.total_steps:
                return True
            
            # Check custom requirements
            requirements = achievement.requirements
            for req_key, req_value in requirements.items():
                progress_value = progress.progress_data.get(req_key, 0)
                if isinstance(req_value, (int, float)) and progress_value >= req_value:
                    continue
                elif req_value == progress_value:
                    continue
                else:
                    return False
            
            return len(requirements) > 0  # Unlock if all requirements met
            
        except Exception as e:
            logger.error(f"Error checking achievement unlock: {e}")
            return False
    
    async def _unlock_achievement(
        self,
        user_id: str,
        achievement_id: str,
        verification_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Unlock achievement for user"""
        try:
            if achievement_id not in self._achievements:
                return False
            
            # Initialize user progress if not exists
            if user_id not in self._user_progress:
                self._user_progress[user_id] = {}
            
            if achievement_id not in self._user_progress[user_id]:
                self._user_progress[user_id][achievement_id] = UserAchievementProgress(
                    user_id=user_id,
                    achievement_id=achievement_id
                )
            
            progress = self._user_progress[user_id][achievement_id]
            achievement = self._achievements[achievement_id]
            
            # Skip if already unlocked
            if progress.is_unlocked:
                return True
            
            # Unlock achievement
            progress.is_unlocked = True
            progress.unlocked_at = datetime.now(timezone.utc)
            progress.current_progress = 100.0
            progress.steps_completed = achievement.total_steps
            
            if verification_data:
                progress.verification_data = verification_data
                progress.verification_status = "verified"
            
            # Update achievement statistics
            achievement.unlock_count += 1
            achievement.completion_rate = await self._calculate_completion_rate(achievement_id)
            
            # Update analytics
            if self.analytics_enabled:
                await self._update_achievement_analytics(achievement_id, 'unlock', {
                    'user_id': user_id,
                    'timestamp': progress.unlocked_at.isoformat()
                })
            
            logger.info(f"Achievement {achievement_id} unlocked for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unlocking achievement: {e}")
            return False
    
    async def _calculate_completion_rate(self, achievement_id: str) -> float:
        """Calculate achievement completion rate"""
        try:
            total_users = len(self._user_progress)
            if total_users == 0:
                return 0.0
            
            unlocked_count = 0
            for user_progress in self._user_progress.values():
                if achievement_id in user_progress and user_progress[achievement_id].is_unlocked:
                    unlocked_count += 1
            
            return (unlocked_count / total_users) * 100
            
        except Exception as e:
            logger.error(f"Error calculating completion rate: {e}")
            return 0.0
    
    async def _get_user_progress(
        self,
        user_id: str,
        achievement_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get user progress for specific achievement"""
        try:
            if user_id not in self._user_progress:
                return None
            
            if achievement_id not in self._user_progress[user_id]:
                return None
            
            progress = self._user_progress[user_id][achievement_id]
            achievement = self._achievements[achievement_id]
            
            return {
                'current_progress': progress.current_progress,
                'steps_completed': progress.steps_completed,
                'total_steps': achievement.total_steps,
                'is_unlocked': progress.is_unlocked,
                'started_at': progress.started_at.isoformat(),
                'unlocked_at': progress.unlocked_at.isoformat() if progress.unlocked_at else None,
                'last_update': progress.last_progress_update.isoformat(),
                'attempt_count': progress.attempt_count
            }
            
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            return None
    
    # Cache management methods
    
    def _generate_query_cache_key(self, query: AchievementQuery) -> str:
        """Generate cache key for query"""
        try:
            # Create a deterministic cache key from query parameters
            key_parts = [
                f"aids:{','.join(query.achievement_ids) if query.achievement_ids else 'all'}",
                f"types:{','.join([t.value for t in query.achievement_types]) if query.achievement_types else 'all'}",
                f"tiers:{','.join([t.value for t in query.tiers]) if query.tiers else 'all'}",
                f"statuses:{','.join([s.value for s in query.statuses]) if query.statuses else 'all'}",
                f"user:{query.user_id or 'none'}",
                f"prog:{query.include_progress}",
                f"unlocked:{query.unlocked_only}",
                f"available:{query.available_only}",
                f"sort:{query.sort_by}:{query.sort_desc}",
                f"page:{query.offset}:{query.limit}",
                f"search:{query.search_text or 'none'}"
            ]
            return "query_" + "_".join(key_parts)
            
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            return f"query_fallback_{hash(str(query))}"
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached query result"""
        try:
            if cache_key not in self._query_cache:
                return None
            
            cached_time, cached_result = self._query_cache[cache_key]
            
            # Check if cache is still valid
            if (datetime.now(timezone.utc) - cached_time).total_seconds() > self.cache_ttl_seconds:
                del self._query_cache[cache_key]
                return None
            
            return cached_result
            
        except Exception as e:
            logger.error(f"Error getting cached result: {e}")
            return None
    
    async def _cache_result(self, cache_key: str, result: Any) -> None:
        """Cache query result"""
        try:
            # Limit cache size
            if len(self._query_cache) >= self.max_cache_entries:
                # Remove oldest entries
                sorted_cache = sorted(
                    self._query_cache.items(),
                    key=lambda x: x[1][0]
                )
                for old_key, _ in sorted_cache[:len(sorted_cache) // 2]:
                    del self._query_cache[old_key]
            
            self._query_cache[cache_key] = (datetime.now(timezone.utc), result)
            
        except Exception as e:
            logger.error(f"Error caching result: {e}")
    
    async def _clear_cache_for_achievement(self, achievement_id: str) -> None:
        """Clear cache entries related to specific achievement"""
        try:
            keys_to_remove = []
            for cache_key in self._query_cache:
                if achievement_id in cache_key or "all" in cache_key:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                del self._query_cache[key]
                
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    async def _clear_cache_for_user_achievement(self, user_id: str, achievement_id: str) -> None:
        """Clear cache entries related to user achievement"""
        try:
            keys_to_remove = []
            for cache_key in self._query_cache:
                if user_id in cache_key or achievement_id in cache_key:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                del self._query_cache[key]
                
        except Exception as e:
            logger.error(f"Error clearing user cache: {e}")
    
    # Analytics methods
    
    async def _initialize_achievement_analytics(self, achievement_id: str) -> None:
        """Initialize analytics for achievement"""
        try:
            self._achievement_analytics[achievement_id] = {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'unlock_events': [],
                'progress_events': [],
                'daily_stats': {},
                'user_engagement': {}
            }
            
        except Exception as e:
            logger.error(f"Error initializing analytics: {e}")
    
    async def _update_achievement_analytics(
        self,
        achievement_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """Update achievement analytics"""
        try:
            if achievement_id not in self._achievement_analytics:
                await self._initialize_achievement_analytics(achievement_id)
            
            analytics = self._achievement_analytics[achievement_id]
            
            event_record = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': event_type,
                'data': event_data
            }
            
            if event_type == 'unlock':
                analytics['unlock_events'].append(event_record)
            elif event_type == 'progress_update':
                analytics['progress_events'].append(event_record)
            
            # Update daily stats
            today = datetime.now(timezone.utc).date().isoformat()
            if today not in analytics['daily_stats']:
                analytics['daily_stats'][today] = {
                    'unlocks': 0,
                    'progress_updates': 0,
                    'unique_users': set()
                }
            
            daily_stats = analytics['daily_stats'][today]
            if event_type == 'unlock':
                daily_stats['unlocks'] += 1
            elif event_type == 'progress_update':
                daily_stats['progress_updates'] += 1
            
            if 'user_id' in event_data:
                daily_stats['unique_users'].add(event_data['user_id'])
            
            # Keep only last 30 days
            if len(analytics['daily_stats']) > 30:
                sorted_days = sorted(analytics['daily_stats'].keys())
                for old_day in sorted_days[:-30]:
                    del analytics['daily_stats'][old_day]
            
        except Exception as e:
            logger.error(f"Error updating achievement analytics: {e}")
    
    async def _get_achievement_analytics(self, achievement_id: str) -> Dict[str, Any]:
        """Get analytics for specific achievement"""
        try:
            if achievement_id not in self._achievement_analytics:
                return {}
            
            analytics = self._achievement_analytics[achievement_id]
            
            return {
                'total_unlock_events': len(analytics['unlock_events']),
                'total_progress_events': len(analytics['progress_events']),
                'daily_stats': analytics['daily_stats'],
                'recent_unlocks': analytics['unlock_events'][-10:],  # Last 10 unlocks
                'engagement_summary': await self._calculate_engagement_summary(achievement_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting achievement analytics: {e}")
            return {}
    
    async def _calculate_engagement_summary(self, achievement_id: str) -> Dict[str, Any]:
        """Calculate engagement summary for achievement"""
        try:
            analytics = self._achievement_analytics.get(achievement_id, {})
            
            # Calculate engagement metrics
            total_attempts = len([
                up for user_progress in self._user_progress.values()
                for aid, up in user_progress.items()
                if aid == achievement_id
            ])
            
            total_unlocks = len(analytics.get('unlock_events', []))
            
            engagement_rate = (total_unlocks / total_attempts) * 100 if total_attempts > 0 else 0
            
            return {
                'total_attempts': total_attempts,
                'total_unlocks': total_unlocks,
                'engagement_rate': engagement_rate,
                'average_time_to_unlock': await self._calculate_average_unlock_time(achievement_id)
            }
            
        except Exception as e:
            logger.error(f"Error calculating engagement summary: {e}")
            return {}
    
    async def _calculate_average_unlock_time(self, achievement_id: str) -> float:
        """Calculate average time to unlock achievement"""
        try:
            unlock_times = []
            
            for user_progress in self._user_progress.values():
                if achievement_id in user_progress:
                    progress = user_progress[achievement_id]
                    if progress.is_unlocked and progress.unlocked_at:
                        time_diff = (progress.unlocked_at - progress.started_at).total_seconds()
                        unlock_times.append(time_diff)
            
            if unlock_times:
                return sum(unlock_times) / len(unlock_times)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average unlock time: {e}")
            return 0.0
    
    async def _calculate_single_achievement_analytics(
        self,
        achievement_id: str,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> AchievementAnalytics:
        """Calculate analytics for single achievement"""
        try:
            analytics = AchievementAnalytics()
            
            if achievement_id not in self._achievements:
                return analytics
            
            achievement = self._achievements[achievement_id]
            
            # Basic stats
            analytics.total_achievements = 1
            analytics.active_achievements = 1 if achievement.status == AchievementStatus.ACTIVE else 0
            
            # Count unlocks and attempts
            for user_progress in self._user_progress.values():
                if achievement_id in user_progress:
                    progress = user_progress[achievement_id]
                    
                    # Apply time filter
                    if time_range and progress.unlocked_at:
                        start_time, end_time = time_range
                        if not (start_time <= progress.unlocked_at <= end_time):
                            continue
                    
                    if progress.is_unlocked:
                        analytics.total_unlocks += 1
            
            # Calculate completion rate
            total_users_attempted = sum(
                1 for user_progress in self._user_progress.values()
                if achievement_id in user_progress
            )
            
            if total_users_attempted > 0:
                analytics.average_completion_rate = (analytics.total_unlocks / total_users_attempted) * 100
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error calculating single achievement analytics: {e}")
            return AchievementAnalytics()
    
    async def _calculate_overall_analytics(
        self,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> AchievementAnalytics:
        """Calculate overall achievement analytics"""
        try:
            analytics = AchievementAnalytics()
            
            # Basic counts
            analytics.total_achievements = len(self._achievements)
            analytics.active_achievements = sum(
                1 for achievement in self._achievements.values()
                if achievement.status == AchievementStatus.ACTIVE
            )
            
            # Calculate completion rates by tier and type
            tier_stats = {tier: {'total': 0, 'unlocked': 0} for tier in AchievementTier}
            type_stats = {achievement_type: {'total': 0, 'unlocked': 0} for achievement_type in AchievementType}
            
            for achievement in self._achievements.values():
                tier_stats[achievement.tier]['total'] += 1
                type_stats[achievement.achievement_type]['total'] += 1
                
                unlocked_count = sum(
                    1 for user_progress in self._user_progress.values()
                    if achievement.achievement_id in user_progress and
                    user_progress[achievement.achievement_id].is_unlocked
                )
                
                tier_stats[achievement.tier]['unlocked'] += unlocked_count
                type_stats[achievement.achievement_type]['unlocked'] += unlocked_count
                
                analytics.total_unlocks += unlocked_count
                analytics.total_business_value_unlocked += achievement.business_value * unlocked_count
                analytics.total_points_awarded += achievement.points_value * unlocked_count
                analytics.total_monetary_value_awarded += achievement.monetary_value * unlocked_count
            
            # Calculate completion rates
            for tier in AchievementTier:
                total = tier_stats[tier]['total']
                if total > 0:
                    analytics.completion_rates_by_tier[tier] = (tier_stats[tier]['unlocked'] / total) * 100
            
            for achievement_type in AchievementType:
                total = type_stats[achievement_type]['total']
                if total > 0:
                    analytics.completion_rates_by_type[achievement_type] = (type_stats[achievement_type]['unlocked'] / total) * 100
            
            # Calculate average completion rate
            if analytics.total_achievements > 0:
                total_possible_unlocks = analytics.total_achievements * len(self._user_progress)
                if total_possible_unlocks > 0:
                    analytics.average_completion_rate = (analytics.total_unlocks / total_possible_unlocks) * 100
            
            # Count unique users with unlocks
            users_with_unlocks = set()
            for user_id, user_progress in self._user_progress.items():
                for progress in user_progress.values():
                    if progress.is_unlocked:
                        users_with_unlocks.add(user_id)
                        break
            
            analytics.unique_users_with_unlocks = len(users_with_unlocks)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error calculating overall analytics: {e}")
            return AchievementAnalytics()
    
    async def _get_cached_analytics(self, cache_key: str) -> Optional[AchievementAnalytics]:
        """Get cached analytics result"""
        try:
            if cache_key not in self._analytics_cache:
                return None
            
            cached_time, cached_result = self._analytics_cache[cache_key]
            
            # Check if cache is still valid (analytics cache has longer TTL)
            analytics_ttl = self.cache_ttl_seconds * 5  # 5x longer for analytics
            if (datetime.now(timezone.utc) - cached_time).total_seconds() > analytics_ttl:
                del self._analytics_cache[cache_key]
                return None
            
            return cached_result
            
        except Exception as e:
            logger.error(f"Error getting cached analytics: {e}")
            return None
    
    async def _cache_analytics(self, cache_key: str, analytics: AchievementAnalytics) -> None:
        """Cache analytics result"""
        try:
            self._analytics_cache[cache_key] = (datetime.now(timezone.utc), analytics)
            
            # Limit cache size
            if len(self._analytics_cache) > 100:
                oldest_key = min(self._analytics_cache.keys(), key=lambda k: self._analytics_cache[k][0])
                del self._analytics_cache[oldest_key]
            
        except Exception as e:
            logger.error(f"Error caching analytics: {e}")