"""
Gamification Index Manager - Centralized Data Discovery and Management

This module provides centralized indexing and data management capabilities for all
gamification-related database operations across the Ainflue platform.

Features:
- Centralized gamification data registry and discovery
- Real-time data indexing and query optimization
- Cross-reference data integrity management
- Performance analytics and database monitoring
- Advanced caching and data distribution
- Multi-tenant data organization
- Data migration and synchronization tools
- Integration with analytics and reporting systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, distribution, or theft of this code or concept
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in immediate legal action.

Contact: mlaiel@live.de for authorized usage inquiries.
"""

from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


class GamificationDataType(Enum):
    """Gamification data type classification"""
    ACHIEVEMENT = "achievement"
    CHALLENGE = "challenge"
    LEADERBOARD = "leaderboard"
    REWARD = "reward"
    USER_PROGRESS = "user_progress"
    TRANSACTION = "transaction"
    ANALYTICS = "analytics"


class IndexStatus(Enum):
    """Index entry status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    PENDING = "pending"
    ERROR = "error"


@dataclass
class GamificationIndexEntry:
    """Gamification index entry with comprehensive metadata"""
    entry_id: str
    data_type: GamificationDataType
    status: IndexStatus
    created_at: datetime
    updated_at: datetime
    
    # Data references
    primary_key: str
    secondary_keys: List[str] = field(default_factory=list)
    related_entries: List[str] = field(default_factory=list)
    
    # Performance metrics
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    cache_hit_rate: float = 0.0
    
    # Business metrics
    business_value: float = 0.0
    user_engagement_score: float = 0.0
    
    # Technical metadata
    data_size_bytes: int = 0
    checksum: str = ""
    version: int = 1
    
    # Categorization
    tags: Set[str] = field(default_factory=set)
    categories: Set[str] = field(default_factory=set)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GamificationQueryFilter:
    """Advanced filtering for gamification data queries"""
    data_types: Optional[List[GamificationDataType]] = None
    statuses: Optional[List[IndexStatus]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    min_access_count: Optional[int] = None
    min_business_value: Optional[float] = None
    min_engagement_score: Optional[float] = None
    tags: Optional[Set[str]] = None
    categories: Optional[Set[str]] = None
    text_search: Optional[str] = None


@dataclass
class GamificationIndexStatistics:
    """Comprehensive index statistics"""
    total_entries: int = 0
    entries_by_type: Dict[GamificationDataType, int] = field(default_factory=dict)
    entries_by_status: Dict[IndexStatus, int] = field(default_factory=dict)
    
    # Performance metrics
    total_access_count: int = 0
    average_cache_hit_rate: float = 0.0
    total_data_size_mb: float = 0.0
    
    # Business metrics
    total_business_value: float = 0.0
    average_engagement_score: float = 0.0
    
    # Time metrics
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None
    last_update: Optional[datetime] = None


class GamificationIndexManager:
    """
    Enterprise-grade gamification data index and discovery management system
    
    Provides centralized registry, discovery, and analytics for all gamification
    data with advanced filtering, performance tracking, and business intelligence.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize gamification index manager"""
        self.config = config or {}
        
        # Core registries
        self._index_entries: Dict[str, GamificationIndexEntry] = {}
        self._type_index: Dict[GamificationDataType, Set[str]] = {
            data_type: set() for data_type in GamificationDataType
        }
        self._tag_index: Dict[str, Set[str]] = {}
        self._category_index: Dict[str, Set[str]] = {}
        
        # Performance tracking
        self._access_statistics: Dict[str, Dict[str, Any]] = {}
        self._cache_performance: Dict[str, float] = {}
        
        # Business analytics
        self._business_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.max_entries = self.config.get('max_entries', 100000)
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.analytics_enabled = self.config.get('analytics_enabled', True)
        self.auto_cleanup_enabled = self.config.get('auto_cleanup_enabled', True)
        
        logger.info("Gamification Index Manager initialized successfully")
    
    async def register_entry(
        self,
        entry_id: str,
        data_type: GamificationDataType,
        primary_key: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register a new gamification data entry"""
        try:
            if entry_id in self._index_entries:
                logger.warning(f"Entry {entry_id} already registered")
                return False
            
            # Create index entry
            entry = GamificationIndexEntry(
                entry_id=entry_id,
                data_type=data_type,
                status=IndexStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                primary_key=primary_key,
                metadata=metadata or {}
            )
            
            # Extract tags and categories from metadata
            if metadata:
                entry.tags = set(metadata.get('tags', []))
                entry.categories = set(metadata.get('categories', []))
                entry.business_value = metadata.get('business_value', 0.0)
                entry.data_size_bytes = metadata.get('data_size_bytes', 0)
            
            # Register in indices
            self._index_entries[entry_id] = entry
            self._type_index[data_type].add(entry_id)
            
            # Tag index
            for tag in entry.tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(entry_id)
            
            # Category index
            for category in entry.categories:
                if category not in self._category_index:
                    self._category_index[category] = set()
                self._category_index[category].add(entry_id)
            
            logger.info(f"Entry {entry_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering entry {entry_id}: {e}")
            return False
    
    async def discover_entries(
        self,
        filters: Optional[GamificationQueryFilter] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[GamificationIndexEntry]:
        """Discover gamification entries based on filters"""
        try:
            # Start with all entries
            candidate_ids = set(self._index_entries.keys())
            
            if filters:
                # Apply data type filter
                if filters.data_types:
                    type_matches = set()
                    for data_type in filters.data_types:
                        type_matches.update(self._type_index[data_type])
                    candidate_ids &= type_matches
                
                # Apply status filter
                if filters.statuses:
                    status_matches = {
                        entry_id for entry_id, entry in self._index_entries.items()
                        if entry.status in filters.statuses
                    }
                    candidate_ids &= status_matches
                
                # Apply date filters
                if filters.created_after:
                    date_matches = {
                        entry_id for entry_id, entry in self._index_entries.items()
                        if entry.created_at >= filters.created_after
                    }
                    candidate_ids &= date_matches
                
                if filters.created_before:
                    date_matches = {
                        entry_id for entry_id, entry in self._index_entries.items()
                        if entry.created_at <= filters.created_before
                    }
                    candidate_ids &= date_matches
                
                # Apply access count filter
                if filters.min_access_count is not None:
                    access_matches = {
                        entry_id for entry_id, entry in self._index_entries.items()
                        if entry.access_count >= filters.min_access_count
                    }
                    candidate_ids &= access_matches
                
                # Apply business value filter
                if filters.min_business_value is not None:
                    value_matches = {
                        entry_id for entry_id, entry in self._index_entries.items()
                        if entry.business_value >= filters.min_business_value
                    }
                    candidate_ids &= value_matches
                
                # Apply engagement score filter
                if filters.min_engagement_score is not None:
                    engagement_matches = {
                        entry_id for entry_id, entry in self._index_entries.items()
                        if entry.user_engagement_score >= filters.min_engagement_score
                    }
                    candidate_ids &= engagement_matches
                
                # Apply tag filter
                if filters.tags:
                    tag_matches = set()
                    for tag in filters.tags:
                        if tag in self._tag_index:
                            tag_matches.update(self._tag_index[tag])
                    candidate_ids &= tag_matches
                
                # Apply category filter
                if filters.categories:
                    category_matches = set()
                    for category in filters.categories:
                        if category in self._category_index:
                            category_matches.update(self._category_index[category])
                    candidate_ids &= category_matches
                
                # Apply text search filter
                if filters.text_search:
                    text_matches = await self._search_text(filters.text_search, candidate_ids)
                    candidate_ids &= text_matches
            
            # Convert to entries and sort
            results = [self._index_entries[entry_id] for entry_id in candidate_ids]
            
            # Sort results
            if sort_by == "created_at":
                results.sort(key=lambda x: x.created_at, reverse=sort_desc)
            elif sort_by == "updated_at":
                results.sort(key=lambda x: x.updated_at, reverse=sort_desc)
            elif sort_by == "access_count":
                results.sort(key=lambda x: x.access_count, reverse=sort_desc)
            elif sort_by == "business_value":
                results.sort(key=lambda x: x.business_value, reverse=sort_desc)
            elif sort_by == "engagement_score":
                results.sort(key=lambda x: x.user_engagement_score, reverse=sort_desc)
            
            # Apply pagination
            return results[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error discovering entries: {e}")
            return []
    
    async def update_entry_metrics(
        self,
        entry_id: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """Update entry performance and business metrics"""
        try:
            if entry_id not in self._index_entries:
                logger.warning(f"Entry {entry_id} not found")
                return False
            
            entry = self._index_entries[entry_id]
            
            # Update metrics
            if 'access_count' in metrics:
                entry.access_count = metrics['access_count']
                entry.last_accessed = datetime.now(timezone.utc)
            
            if 'cache_hit_rate' in metrics:
                entry.cache_hit_rate = metrics['cache_hit_rate']
            
            if 'business_value' in metrics:
                entry.business_value = metrics['business_value']
            
            if 'user_engagement_score' in metrics:
                entry.user_engagement_score = metrics['user_engagement_score']
            
            if 'data_size_bytes' in metrics:
                entry.data_size_bytes = metrics['data_size_bytes']
            
            # Update timestamp
            entry.updated_at = datetime.now(timezone.utc)
            entry.version += 1
            
            # Update analytics if enabled
            if self.analytics_enabled:
                await self._update_analytics(entry_id, metrics)
            
            logger.debug(f"Metrics updated for entry {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating entry metrics: {e}")
            return False
    
    async def record_access(self, entry_id: str) -> bool:
        """Record access to an entry for analytics"""
        try:
            if entry_id not in self._index_entries:
                return False
            
            entry = self._index_entries[entry_id]
            entry.access_count += 1
            entry.last_accessed = datetime.now(timezone.utc)
            
            # Update access statistics
            if entry_id not in self._access_statistics:
                self._access_statistics[entry_id] = {
                    'hourly_access': [],
                    'daily_access': [],
                    'total_access': 0
                }
            
            stats = self._access_statistics[entry_id]
            stats['total_access'] += 1
            
            # Track hourly and daily patterns
            now = datetime.now(timezone.utc)
            hour_key = f"{now.year}-{now.month}-{now.day}-{now.hour}"
            day_key = f"{now.year}-{now.month}-{now.day}"
            
            # Update hourly access
            hourly_access = stats['hourly_access']
            if not hourly_access or hourly_access[-1]['hour'] != hour_key:
                hourly_access.append({'hour': hour_key, 'count': 1})
            else:
                hourly_access[-1]['count'] += 1
            
            # Keep only last 24 hours
            if len(hourly_access) > 24:
                stats['hourly_access'] = hourly_access[-24:]
            
            # Update daily access
            daily_access = stats['daily_access']
            if not daily_access or daily_access[-1]['day'] != day_key:
                daily_access.append({'day': day_key, 'count': 1})
            else:
                daily_access[-1]['count'] += 1
            
            # Keep only last 30 days
            if len(daily_access) > 30:
                stats['daily_access'] = daily_access[-30:]
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording access for entry {entry_id}: {e}")
            return False
    
    async def get_entry_analytics(
        self,
        entry_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for an entry"""
        try:
            if entry_id not in self._index_entries:
                return {}
            
            entry = self._index_entries[entry_id]
            access_stats = self._access_statistics.get(entry_id, {})
            
            analytics = {
                'basic_info': {
                    'entry_id': entry_id,
                    'data_type': entry.data_type.value,
                    'status': entry.status.value,
                    'created_at': entry.created_at.isoformat(),
                    'updated_at': entry.updated_at.isoformat(),
                    'version': entry.version
                },
                'performance_metrics': {
                    'access_count': entry.access_count,
                    'cache_hit_rate': entry.cache_hit_rate,
                    'data_size_mb': entry.data_size_bytes / (1024 * 1024),
                    'last_accessed': entry.last_accessed.isoformat() if entry.last_accessed else None
                },
                'business_metrics': {
                    'business_value': entry.business_value,
                    'user_engagement_score': entry.user_engagement_score
                },
                'access_patterns': access_stats,
                'related_data': {
                    'secondary_keys': entry.secondary_keys,
                    'related_entries': entry.related_entries,
                    'tags': list(entry.tags),
                    'categories': list(entry.categories)
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics for entry {entry_id}: {e}")
            return {}
    
    async def get_index_statistics(self) -> GamificationIndexStatistics:
        """Get comprehensive index statistics"""
        try:
            stats = GamificationIndexStatistics()
            
            # Basic counts
            stats.total_entries = len(self._index_entries)
            
            # Count by type
            for data_type in GamificationDataType:
                stats.entries_by_type[data_type] = len(self._type_index[data_type])
            
            # Count by status
            for entry in self._index_entries.values():
                status = entry.status
                stats.entries_by_status[status] = stats.entries_by_status.get(status, 0) + 1
            
            # Performance metrics
            if self._index_entries:
                stats.total_access_count = sum(entry.access_count for entry in self._index_entries.values())
                
                cache_rates = [entry.cache_hit_rate for entry in self._index_entries.values() if entry.cache_hit_rate > 0]
                if cache_rates:
                    stats.average_cache_hit_rate = sum(cache_rates) / len(cache_rates)
                
                stats.total_data_size_mb = sum(
                    entry.data_size_bytes for entry in self._index_entries.values()
                ) / (1024 * 1024)
                
                # Business metrics
                stats.total_business_value = sum(entry.business_value for entry in self._index_entries.values())
                
                engagement_scores = [
                    entry.user_engagement_score for entry in self._index_entries.values()
                    if entry.user_engagement_score > 0
                ]
                if engagement_scores:
                    stats.average_engagement_score = sum(engagement_scores) / len(engagement_scores)
                
                # Time metrics
                creation_times = [entry.created_at for entry in self._index_entries.values()]
                if creation_times:
                    stats.oldest_entry = min(creation_times)
                    stats.newest_entry = max(creation_times)
                
                update_times = [entry.updated_at for entry in self._index_entries.values()]
                if update_times:
                    stats.last_update = max(update_times)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting index statistics: {e}")
            return GamificationIndexStatistics()
    
    async def get_trending_entries(
        self,
        data_type: Optional[GamificationDataType] = None,
        limit: int = 10,
        time_window_hours: int = 24
    ) -> List[GamificationIndexEntry]:
        """Get trending entries based on recent activity"""
        try:
            # Filter by data type if specified
            if data_type:
                candidate_ids = self._type_index[data_type]
            else:
                candidate_ids = set(self._index_entries.keys())
            
            # Calculate trending scores
            trending_entries = []
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
            
            for entry_id in candidate_ids:
                entry = self._index_entries[entry_id]
                
                # Calculate trend score based on recent activity
                trend_score = 0.0
                
                # Recent access boost
                if entry.last_accessed and entry.last_accessed >= cutoff_time:
                    hours_since_access = (datetime.now(timezone.utc) - entry.last_accessed).total_seconds() / 3600
                    recent_access_boost = max(0, (time_window_hours - hours_since_access) / time_window_hours)
                    trend_score += recent_access_boost * 50
                
                # Business value component
                trend_score += entry.business_value * 0.1
                
                # Engagement score component
                trend_score += entry.user_engagement_score * 0.3
                
                # Access frequency component
                if entry.access_count > 0:
                    days_since_creation = (datetime.now(timezone.utc) - entry.created_at).days or 1
                    access_frequency = entry.access_count / days_since_creation
                    trend_score += min(access_frequency * 10, 100)
                
                trending_entries.append((entry, trend_score))
            
            # Sort by trend score
            trending_entries.sort(key=lambda x: x[1], reverse=True)
            
            # Return top entries
            return [entry for entry, _ in trending_entries[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting trending entries: {e}")
            return []
    
    async def cleanup_stale_entries(
        self,
        max_age_days: int = 365,
        min_access_count: int = 1
    ) -> int:
        """Clean up stale entries based on age and usage"""
        try:
            if not self.auto_cleanup_enabled:
                return 0
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
            entries_to_remove = []
            
            for entry_id, entry in self._index_entries.items():
                # Mark for removal if old and unused
                if (entry.created_at < cutoff_date and 
                    entry.access_count < min_access_count and
                    entry.status != IndexStatus.ACTIVE):
                    entries_to_remove.append(entry_id)
            
            # Remove stale entries
            removed_count = 0
            for entry_id in entries_to_remove:
                if await self._remove_entry(entry_id):
                    removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} stale entries")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up stale entries: {e}")
            return 0
    
    # Helper methods
    
    async def _search_text(
        self,
        search_term: str,
        candidate_ids: Set[str]
    ) -> Set[str]:
        """Perform text search across entry metadata"""
        try:
            search_term = search_term.lower()
            matches = set()
            
            for entry_id in candidate_ids:
                entry = self._index_entries[entry_id]
                
                # Search in primary key
                if search_term in entry.primary_key.lower():
                    matches.add(entry_id)
                    continue
                
                # Search in secondary keys
                for key in entry.secondary_keys:
                    if search_term in key.lower():
                        matches.add(entry_id)
                        break
                
                # Search in tags
                for tag in entry.tags:
                    if search_term in tag.lower():
                        matches.add(entry_id)
                        break
                
                # Search in categories
                for category in entry.categories:
                    if search_term in category.lower():
                        matches.add(entry_id)
                        break
                
                # Search in metadata
                metadata_str = json.dumps(entry.metadata, default=str).lower()
                if search_term in metadata_str:
                    matches.add(entry_id)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return set()
    
    async def _update_analytics(
        self,
        entry_id: str,
        metrics: Dict[str, Any]
    ) -> None:
        """Update business analytics for entry"""
        try:
            if entry_id not in self._business_metrics:
                self._business_metrics[entry_id] = {
                    'metric_history': [],
                    'trend_analysis': {},
                    'performance_indicators': {}
                }
            
            analytics = self._business_metrics[entry_id]
            
            # Add to metric history
            metric_snapshot = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'metrics': metrics.copy()
            }
            analytics['metric_history'].append(metric_snapshot)
            
            # Keep only last 100 snapshots
            if len(analytics['metric_history']) > 100:
                analytics['metric_history'] = analytics['metric_history'][-100:]
            
            # Calculate trends
            if len(analytics['metric_history']) >= 2:
                await self._calculate_trends(entry_id, analytics)
            
        except Exception as e:
            logger.error(f"Error updating analytics for entry {entry_id}: {e}")
    
    async def _calculate_trends(
        self,
        entry_id: str,
        analytics: Dict[str, Any]
    ) -> None:
        """Calculate trend analysis for entry"""
        try:
            history = analytics['metric_history']
            if len(history) < 2:
                return
            
            trends = {}
            latest = history[-1]['metrics']
            previous = history[-2]['metrics']
            
            for metric_name in latest:
                if metric_name in previous and isinstance(latest[metric_name], (int, float)):
                    current_value = latest[metric_name]
                    previous_value = previous[metric_name]
                    
                    if previous_value != 0:
                        change_percent = ((current_value - previous_value) / previous_value) * 100
                    else:
                        change_percent = 100.0 if current_value > 0 else 0.0
                    
                    trends[metric_name] = {
                        'current_value': current_value,
                        'previous_value': previous_value,
                        'change_percent': change_percent,
                        'trend': 'up' if change_percent > 0 else 'down' if change_percent < 0 else 'stable'
                    }
            
            analytics['trend_analysis'] = trends
            
        except Exception as e:
            logger.error(f"Error calculating trends for entry {entry_id}: {e}")
    
    async def _remove_entry(self, entry_id: str) -> bool:
        """Remove entry from all indices"""
        try:
            if entry_id not in self._index_entries:
                return False
            
            entry = self._index_entries[entry_id]
            
            # Remove from type index
            self._type_index[entry.data_type].discard(entry_id)
            
            # Remove from tag indices
            for tag in entry.tags:
                if tag in self._tag_index:
                    self._tag_index[tag].discard(entry_id)
                    if not self._tag_index[tag]:
                        del self._tag_index[tag]
            
            # Remove from category indices
            for category in entry.categories:
                if category in self._category_index:
                    self._category_index[category].discard(entry_id)
                    if not self._category_index[category]:
                        del self._category_index[category]
            
            # Remove from main index
            del self._index_entries[entry_id]
            
            # Clean up analytics
            if entry_id in self._access_statistics:
                del self._access_statistics[entry_id]
            if entry_id in self._business_metrics:
                del self._business_metrics[entry_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing entry {entry_id}: {e}")
            return False