"""
Leaderboard Repository - Enterprise Leaderboard Data Management

This module provides comprehensive data access layer for leaderboard management
with real-time ranking, advanced caching, and performance optimization.

Features:
- High-performance leaderboard data access and ranking
- Real-time leaderboard updates and notifications
- Advanced leaderboard analytics and trending
- Multi-dimensional ranking systems
- Cross-platform leaderboard synchronization
- Professional audit trails and data integrity
- Integration with gamification and achievement systems
- Leaderboard performance monitoring and optimization

Business Logic Integration:
- User achievements → Leaderboard updates → Real-time ranking
- Challenge completion → Leaderboard position → Competition analytics
- Performance metrics → Ranking algorithms → Business intelligence
- Leaderboard data → Creator matching → Collaboration opportunities

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

logger = logging.getLogger(__name__)


class LeaderboardType(Enum):
    """Leaderboard type classification"""
    GLOBAL = "global"
    CHALLENGE = "challenge"
    ACHIEVEMENT = "achievement"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    COLLABORATION = "collaboration"
    QUALITY = "quality"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"


class RankingMetric(Enum):
    """Ranking metric types"""
    TOTAL_POINTS = "total_points"
    ACHIEVEMENT_COUNT = "achievement_count"
    CHALLENGE_WINS = "challenge_wins"
    REVENUE_GENERATED = "revenue_generated"
    ENGAGEMENT_SCORE = "engagement_score"
    QUALITY_SCORE = "quality_score"
    COLLABORATION_COUNT = "collaboration_count"
    CONTENT_UPLOADS = "content_uploads"


@dataclass
class LeaderboardData:
    """Comprehensive leaderboard data model"""
    leaderboard_id: str
    name: str
    description: str
    leaderboard_type: LeaderboardType
    ranking_metric: RankingMetric
    
    # Configuration
    max_entries: int = 1000
    update_frequency_minutes: int = 5
    is_active: bool = True
    is_public: bool = True
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reset_schedule: Optional[str] = None  # cron expression
    last_reset: Optional[datetime] = None
    
    # Filtering
    category_filter: Optional[str] = None
    tag_filters: List[str] = field(default_factory=list)
    user_group_filter: Optional[str] = None
    
    # Rewards
    rewards_config: Dict[str, Any] = field(default_factory=dict)
    
    # Performance
    entry_count: int = 0
    last_calculation_time: Optional[datetime] = None
    calculation_duration_ms: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeaderboardEntry:
    """Leaderboard entry data"""
    user_id: str
    username: str
    rank: int
    score: float
    
    # Detailed metrics
    metric_values: Dict[str, float] = field(default_factory=dict)
    
    # Change tracking
    previous_rank: Optional[int] = None
    rank_change: int = 0  # positive = moved up, negative = moved down
    score_change: float = 0.0
    
    # Performance data
    trend_direction: str = "stable"  # up, down, stable
    performance_streak: int = 0
    
    # Timing
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    first_appearance: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Additional data
    profile_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeaderboardQuery:
    """Leaderboard query parameters"""
    leaderboard_ids: Optional[List[str]] = None
    leaderboard_types: Optional[List[LeaderboardType]] = None
    ranking_metrics: Optional[List[RankingMetric]] = None
    
    # User-specific filters
    user_id: Optional[str] = None
    include_user_rank: bool = False
    
    # Entry filters
    top_n: Optional[int] = None
    min_score: Optional[float] = None
    category_filter: Optional[str] = None
    
    # Timing filters
    active_only: bool = True
    public_only: bool = True
    updated_after: Optional[datetime] = None
    
    # Sorting and pagination
    sort_by: str = "rank"
    sort_desc: bool = False
    limit: int = 100
    offset: int = 0
    
    # Includes
    include_entries: bool = True
    include_analytics: bool = False
    include_trends: bool = False


class LeaderboardRepository:
    """
    Enterprise-grade leaderboard repository with advanced ranking management
    
    Provides comprehensive leaderboard data access with high-performance
    ranking, real-time updates, analytics, and business intelligence.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize leaderboard repository"""
        self.config = config or {}
        
        # Core storage
        self._leaderboards: Dict[str, LeaderboardData] = {}
        self._leaderboard_entries: Dict[str, List[LeaderboardEntry]] = {}
        
        # Performance indices
        self._type_index: Dict[LeaderboardType, Set[str]] = {
            lb_type: set() for lb_type in LeaderboardType
        }
        self._metric_index: Dict[RankingMetric, Set[str]] = {
            metric: set() for metric in RankingMetric
        }
        self._user_rankings: Dict[str, Dict[str, int]] = {}  # user_id -> leaderboard_id -> rank
        
        # Caching and performance
        self._ranking_cache: Dict[str, Tuple[datetime, List[LeaderboardEntry]]] = {}
        self._user_rank_cache: Dict[str, Tuple[datetime, Dict[str, int]]] = {}
        
        # Analytics
        self._leaderboard_analytics: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.cache_ttl_seconds = self.config.get('cache_ttl_seconds', 300)
        self.real_time_updates = self.config.get('real_time_updates', True)
        
        logger.info("Leaderboard Repository initialized successfully")
    
    async def create_leaderboard(self, leaderboard_data: LeaderboardData) -> bool:
        """Create a new leaderboard"""
        try:
            leaderboard_id = leaderboard_data.leaderboard_id
            
            if leaderboard_id in self._leaderboards:
                logger.warning(f"Leaderboard {leaderboard_id} already exists")
                return False
            
            # Store leaderboard
            self._leaderboards[leaderboard_id] = leaderboard_data
            self._leaderboard_entries[leaderboard_id] = []
            
            # Update indices
            self._type_index[leaderboard_data.leaderboard_type].add(leaderboard_id)
            self._metric_index[leaderboard_data.ranking_metric].add(leaderboard_id)
            
            # Initialize analytics
            await self._initialize_analytics(leaderboard_id)
            
            logger.info(f"Leaderboard {leaderboard_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating leaderboard: {e}")
            return False
    
    async def get_leaderboard(
        self,
        leaderboard_id: str,
        include_entries: bool = True,
        limit: int = 100
    ) -> Optional[Dict[str, Any]]:
        """Get leaderboard by ID"""
        try:
            if leaderboard_id not in self._leaderboards:
                return None
            
            leaderboard = self._leaderboards[leaderboard_id]
            
            result = {
                'leaderboard_id': leaderboard_id,
                'name': leaderboard.name,
                'description': leaderboard.description,
                'leaderboard_type': leaderboard.leaderboard_type.value,
                'ranking_metric': leaderboard.ranking_metric.value,
                'max_entries': leaderboard.max_entries,
                'update_frequency_minutes': leaderboard.update_frequency_minutes,
                'is_active': leaderboard.is_active,
                'is_public': leaderboard.is_public,
                'created_at': leaderboard.created_at.isoformat(),
                'updated_at': leaderboard.updated_at.isoformat(),
                'last_reset': leaderboard.last_reset.isoformat() if leaderboard.last_reset else None,
                'entry_count': leaderboard.entry_count,
                'last_calculation_time': leaderboard.last_calculation_time.isoformat() if leaderboard.last_calculation_time else None,
                'calculation_duration_ms': leaderboard.calculation_duration_ms,
                'metadata': leaderboard.metadata
            }
            
            if include_entries:
                entries = await self._get_leaderboard_entries(leaderboard_id, limit)
                result['entries'] = entries
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting leaderboard {leaderboard_id}: {e}")
            return None
    
    async def update_user_score(
        self,
        leaderboard_id: str,
        user_id: str,
        username: str,
        score: float,
        metric_values: Optional[Dict[str, float]] = None
    ) -> bool:
        """Update user score in leaderboard"""
        try:
            if leaderboard_id not in self._leaderboards:
                return False
            
            leaderboard = self._leaderboards[leaderboard_id]
            entries = self._leaderboard_entries[leaderboard_id]
            
            # Find existing entry
            existing_entry = None
            for entry in entries:
                if entry.user_id == user_id:
                    existing_entry = entry
                    break
            
            if existing_entry:
                # Update existing entry
                previous_score = existing_entry.score
                existing_entry.score = score
                existing_entry.score_change = score - previous_score
                existing_entry.metric_values = metric_values or {}
                existing_entry.last_updated = datetime.now(timezone.utc)
                
                # Update trend
                if existing_entry.score_change > 0:
                    existing_entry.trend_direction = "up"
                    existing_entry.performance_streak += 1
                elif existing_entry.score_change < 0:
                    existing_entry.trend_direction = "down"
                    existing_entry.performance_streak = 0
                else:
                    existing_entry.trend_direction = "stable"
            else:
                # Create new entry
                new_entry = LeaderboardEntry(
                    user_id=user_id,
                    username=username,
                    rank=0,  # Will be calculated during ranking
                    score=score,
                    metric_values=metric_values or {}
                )
                entries.append(new_entry)
                leaderboard.entry_count += 1
            
            # Recalculate rankings
            await self._recalculate_rankings(leaderboard_id)
            
            # Update analytics
            await self._update_analytics(leaderboard_id, 'score_update', {
                'user_id': user_id,
                'score': score,
                'previous_score': existing_entry.score - existing_entry.score_change if existing_entry else 0
            })
            
            # Clear cache
            await self._clear_leaderboard_cache(leaderboard_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user score: {e}")
            return False
    
    async def get_user_rank(
        self,
        user_id: str,
        leaderboard_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user rank in leaderboards"""
        try:
            # Check cache
            if self.cache_enabled and user_id in self._user_rank_cache:
                cached_time, cached_ranks = self._user_rank_cache[user_id]
                if (datetime.now(timezone.utc) - cached_time).total_seconds() < self.cache_ttl_seconds:
                    if leaderboard_id:
                        return {'leaderboard_id': leaderboard_id, 'rank': cached_ranks.get(leaderboard_id)}
                    else:
                        return {'user_id': user_id, 'rankings': cached_ranks}
            
            user_rankings = {}
            
            # Get rankings from specific leaderboard or all
            target_leaderboards = [leaderboard_id] if leaderboard_id else list(self._leaderboards.keys())
            
            for lb_id in target_leaderboards:
                if lb_id not in self._leaderboard_entries:
                    continue
                
                # Find user in leaderboard
                for entry in self._leaderboard_entries[lb_id]:
                    if entry.user_id == user_id:
                        user_rankings[lb_id] = {
                            'rank': entry.rank,
                            'score': entry.score,
                            'rank_change': entry.rank_change,
                            'trend_direction': entry.trend_direction,
                            'last_updated': entry.last_updated.isoformat()
                        }
                        break
            
            # Cache result
            if self.cache_enabled:
                rank_data = {lb_id: data['rank'] for lb_id, data in user_rankings.items()}
                self._user_rank_cache[user_id] = (datetime.now(timezone.utc), rank_data)
            
            if leaderboard_id:
                return user_rankings.get(leaderboard_id, {'rank': None})
            else:
                return {'user_id': user_id, 'rankings': user_rankings}
            
        except Exception as e:
            logger.error(f"Error getting user rank: {e}")
            return {}
    
    async def get_top_performers(
        self,
        leaderboard_id: str,
        limit: int = 10,
        metric_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get top performers from leaderboard"""
        try:
            entries = await self._get_leaderboard_entries(leaderboard_id, limit)
            
            top_performers = []
            for entry in entries:
                performer_data = {
                    'rank': entry.rank,
                    'user_id': entry.user_id,
                    'username': entry.username,
                    'score': entry.score,
                    'rank_change': entry.rank_change,
                    'trend_direction': entry.trend_direction,
                    'performance_streak': entry.performance_streak,
                    'metric_values': entry.metric_values,
                    'last_updated': entry.last_updated.isoformat()
                }
                
                if metric_filter and metric_filter in entry.metric_values:
                    performer_data['filtered_metric'] = entry.metric_values[metric_filter]
                
                top_performers.append(performer_data)
            
            return top_performers
            
        except Exception as e:
            logger.error(f"Error getting top performers: {e}")
            return []
    
    async def reset_leaderboard(self, leaderboard_id: str) -> bool:
        """Reset leaderboard entries"""
        try:
            if leaderboard_id not in self._leaderboards:
                return False
            
            # Archive current entries for analytics
            await self._archive_leaderboard_entries(leaderboard_id)
            
            # Clear entries
            self._leaderboard_entries[leaderboard_id] = []
            
            # Update leaderboard data
            leaderboard = self._leaderboards[leaderboard_id]
            leaderboard.entry_count = 0
            leaderboard.last_reset = datetime.now(timezone.utc)
            leaderboard.updated_at = datetime.now(timezone.utc)
            
            # Clear cache
            await self._clear_leaderboard_cache(leaderboard_id)
            
            # Update analytics
            await self._update_analytics(leaderboard_id, 'reset', {})
            
            logger.info(f"Leaderboard {leaderboard_id} reset successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting leaderboard: {e}")
            return False
    
    # Helper methods
    
    async def _get_leaderboard_entries(
        self,
        leaderboard_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get leaderboard entries"""
        try:
            # Check cache
            cache_key = f"entries_{leaderboard_id}_{limit}"
            if self.cache_enabled and cache_key in self._ranking_cache:
                cached_time, cached_entries = self._ranking_cache[cache_key]
                if (datetime.now(timezone.utc) - cached_time).total_seconds() < 60:  # 1 minute cache
                    return [self._entry_to_dict(entry) for entry in cached_entries]
            
            if leaderboard_id not in self._leaderboard_entries:
                return []
            
            entries = self._leaderboard_entries[leaderboard_id][:limit]
            
            # Cache entries
            if self.cache_enabled:
                self._ranking_cache[cache_key] = (datetime.now(timezone.utc), entries.copy())
            
            return [self._entry_to_dict(entry) for entry in entries]
            
        except Exception as e:
            logger.error(f"Error getting leaderboard entries: {e}")
            return []
    
    def _entry_to_dict(self, entry: LeaderboardEntry) -> Dict[str, Any]:
        """Convert entry to dictionary"""
        return {
            'rank': entry.rank,
            'user_id': entry.user_id,
            'username': entry.username,
            'score': entry.score,
            'metric_values': entry.metric_values,
            'previous_rank': entry.previous_rank,
            'rank_change': entry.rank_change,
            'score_change': entry.score_change,
            'trend_direction': entry.trend_direction,
            'performance_streak': entry.performance_streak,
            'last_updated': entry.last_updated.isoformat(),
            'first_appearance': entry.first_appearance.isoformat(),
            'profile_data': entry.profile_data
        }
    
    async def _recalculate_rankings(self, leaderboard_id: str) -> None:
        """Recalculate leaderboard rankings"""
        try:
            start_time = datetime.now(timezone.utc)
            
            if leaderboard_id not in self._leaderboard_entries:
                return
            
            entries = self._leaderboard_entries[leaderboard_id]
            
            # Store previous ranks
            for entry in entries:
                entry.previous_rank = entry.rank
            
            # Sort by score (descending)
            entries.sort(key=lambda x: x.score, reverse=True)
            
            # Update ranks and calculate changes
            for i, entry in enumerate(entries):
                new_rank = i + 1
                entry.rank_change = (entry.previous_rank - new_rank) if entry.previous_rank else 0
                entry.rank = new_rank
            
            # Limit entries to max_entries
            leaderboard = self._leaderboards[leaderboard_id]
            if len(entries) > leaderboard.max_entries:
                self._leaderboard_entries[leaderboard_id] = entries[:leaderboard.max_entries]
                leaderboard.entry_count = leaderboard.max_entries
            
            # Update leaderboard metadata
            calculation_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            leaderboard.last_calculation_time = start_time
            leaderboard.calculation_duration_ms = calculation_time
            leaderboard.updated_at = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Error recalculating rankings: {e}")
    
    # Analytics methods
    
    async def _initialize_analytics(self, leaderboard_id: str) -> None:
        """Initialize analytics for leaderboard"""
        try:
            self._leaderboard_analytics[leaderboard_id] = {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'score_updates': [],
                'rank_changes': [],
                'reset_events': [],
                'daily_stats': {}
            }
            
        except Exception as e:
            logger.error(f"Error initializing analytics: {e}")
    
    async def _update_analytics(
        self,
        leaderboard_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """Update leaderboard analytics"""
        try:
            if leaderboard_id not in self._leaderboard_analytics:
                await self._initialize_analytics(leaderboard_id)
            
            analytics = self._leaderboard_analytics[leaderboard_id]
            
            event = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': event_type,
                'data': event_data
            }
            
            if event_type == 'score_update':
                analytics['score_updates'].append(event)
            elif event_type == 'rank_change':
                analytics['rank_changes'].append(event)
            elif event_type == 'reset':
                analytics['reset_events'].append(event)
            
            # Update daily stats
            today = datetime.now(timezone.utc).date().isoformat()
            if today not in analytics['daily_stats']:
                analytics['daily_stats'][today] = {
                    'score_updates': 0,
                    'rank_changes': 0,
                    'unique_users': set()
                }
            
            daily_stats = analytics['daily_stats'][today]
            if event_type == 'score_update':
                daily_stats['score_updates'] += 1
            elif event_type == 'rank_change':
                daily_stats['rank_changes'] += 1
            
            if 'user_id' in event_data:
                daily_stats['unique_users'].add(event_data['user_id'])
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    async def _archive_leaderboard_entries(self, leaderboard_id: str) -> None:
        """Archive leaderboard entries before reset"""
        try:
            if leaderboard_id not in self._leaderboard_entries:
                return
            
            entries = self._leaderboard_entries[leaderboard_id]
            archive_data = {
                'leaderboard_id': leaderboard_id,
                'archived_at': datetime.now(timezone.utc).isoformat(),
                'entry_count': len(entries),
                'entries': [self._entry_to_dict(entry) for entry in entries]
            }
            
            # Store in analytics for historical data
            if leaderboard_id not in self._leaderboard_analytics:
                await self._initialize_analytics(leaderboard_id)
            
            analytics = self._leaderboard_analytics[leaderboard_id]
            if 'archived_periods' not in analytics:
                analytics['archived_periods'] = []
            
            analytics['archived_periods'].append(archive_data)
            
            # Keep only last 10 archived periods
            if len(analytics['archived_periods']) > 10:
                analytics['archived_periods'] = analytics['archived_periods'][-10:]
            
        except Exception as e:
            logger.error(f"Error archiving leaderboard entries: {e}")
    
    # Cache management
    
    async def _clear_leaderboard_cache(self, leaderboard_id: str) -> None:
        """Clear cache for specific leaderboard"""
        try:
            # Clear ranking cache
            keys_to_remove = [k for k in self._ranking_cache if k.startswith(f"entries_{leaderboard_id}")]
            for key in keys_to_remove:
                del self._ranking_cache[key]
            
            # Clear user rank cache for affected users
            if leaderboard_id in self._leaderboard_entries:
                for entry in self._leaderboard_entries[leaderboard_id]:
                    if entry.user_id in self._user_rank_cache:
                        del self._user_rank_cache[entry.user_id]
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")