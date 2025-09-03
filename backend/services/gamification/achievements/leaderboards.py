"""Leaderboards - Classements
==========================

Leaderboard system for ranking content creators across various metrics
and categories with real-time updates and competition features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum


class LeaderboardType(str, Enum):
    """Types of leaderboards."""
    GLOBAL = "global"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CATEGORY = "category"
    TIER = "tier"


class LeaderboardMetric(str, Enum):
    """Metrics used for leaderboard ranking."""
    TOTAL_VIEWS = "total_views"
    TOTAL_UPLOADS = "total_uploads"
    COLLABORATION_COUNT = "collaboration_count"
    FOLLOWER_COUNT = "follower_count"
    ENGAGEMENT_RATE = "engagement_rate"
    REVENUE_GENERATED = "revenue_generated"
    ACHIEVEMENT_POINTS = "achievement_points"
    QUALITY_SCORE = "quality_score"


@dataclass
class LeaderboardEntry:
    """Entry in a leaderboard."""
    user_id: str
    username: str
    display_name: str
    score: Union[int, float]
    rank: int
    previous_rank: Optional[int] = None
    rank_change: int = 0
    avatar_url: Optional[str] = None
    tier: Optional[str] = None
    badges: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Leaderboard:
    """Leaderboard configuration."""
    id: str
    name: str
    description: str
    leaderboard_type: LeaderboardType
    metric: LeaderboardMetric
    max_entries: int = 100
    update_frequency: timedelta = field(default_factory=lambda: timedelta(hours=1))
    is_active: bool = True
    category_filter: Optional[str] = None
    tier_filter: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: Optional[datetime] = None


class Leaderboards:
    """
    Comprehensive leaderboard system providing real-time ranking and
    competition features for content creators.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the leaderboards system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.leaderboards: Dict[str, Leaderboard] = {}
        self.leaderboard_data: Dict[str, List[LeaderboardEntry]] = {}
        
        # Initialize default leaderboards
        self._initialize_default_leaderboards()
        
        self.logger.info("Leaderboards system initialized")
    
    def _initialize_default_leaderboards(self):
        """Initialize default leaderboard configurations."""
        try:
            # Global leaderboards
            self.leaderboards["global_views"] = Leaderboard(
                id="global_views",
                name="Top Creators by Views",
                description="Global ranking by total content views",
                leaderboard_type=LeaderboardType.GLOBAL,
                metric=LeaderboardMetric.TOTAL_VIEWS,
                max_entries=100
            )
            
            self.leaderboards["global_creators"] = Leaderboard(
                id="global_creators",
                name="Most Prolific Creators",
                description="Global ranking by content uploads",
                leaderboard_type=LeaderboardType.GLOBAL,
                metric=LeaderboardMetric.TOTAL_UPLOADS,
                max_entries=100
            )
            
            self.leaderboards["global_collaborators"] = Leaderboard(
                id="global_collaborators",
                name="Top Collaborators",
                description="Global ranking by collaboration count",
                leaderboard_type=LeaderboardType.GLOBAL,
                metric=LeaderboardMetric.COLLABORATION_COUNT,
                max_entries=50
            )
            
            # Weekly leaderboards
            self.leaderboards["weekly_rising"] = Leaderboard(
                id="weekly_rising",
                name="Rising Stars This Week",
                description="Weekly ranking by engagement growth",
                leaderboard_type=LeaderboardType.WEEKLY,
                metric=LeaderboardMetric.ENGAGEMENT_RATE,
                max_entries=50,
                update_frequency=timedelta(hours=6)
            )
            
            self.leaderboards["weekly_uploads"] = Leaderboard(
                id="weekly_uploads",
                name="Most Active This Week",
                description="Weekly ranking by content uploads",
                leaderboard_type=LeaderboardType.WEEKLY,
                metric=LeaderboardMetric.TOTAL_UPLOADS,
                max_entries=30,
                update_frequency=timedelta(hours=1)
            )
            
            # Monthly leaderboards
            self.leaderboards["monthly_revenue"] = Leaderboard(
                id="monthly_revenue",
                name="Top Earners This Month",
                description="Monthly ranking by revenue generated",
                leaderboard_type=LeaderboardType.MONTHLY,
                metric=LeaderboardMetric.REVENUE_GENERATED,
                max_entries=25,
                update_frequency=timedelta(hours=12)
            )
            
            # Achievement-based leaderboard
            self.leaderboards["achievement_leaders"] = Leaderboard(
                id="achievement_leaders",
                name="Achievement Champions",
                description="Ranking by achievement points earned",
                leaderboard_type=LeaderboardType.GLOBAL,
                metric=LeaderboardMetric.ACHIEVEMENT_POINTS,
                max_entries=50
            )
            
            # Initialize empty data for each leaderboard
            for lb_id in self.leaderboards.keys():
                self.leaderboard_data[lb_id] = []
            
            self.logger.info(f"Initialized {len(self.leaderboards)} default leaderboards")
            
        except Exception as e:
            self.logger.error(f"Error initializing default leaderboards: {e}")
    
    async def update_user_score(
        self,
        user_id: str,
        metric: LeaderboardMetric,
        score: Union[int, float],
        username: str = "",
        display_name: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update a user's score for relevant leaderboards."""
        try:
            # Find leaderboards that use this metric
            relevant_leaderboards = [
                lb_id for lb_id, lb in self.leaderboards.items()
                if lb.metric == metric and lb.is_active
            ]
            
            for lb_id in relevant_leaderboards:
                await self._update_leaderboard_entry(
                    lb_id, user_id, score, username, display_name, metadata
                )
            
            self.logger.debug(f"Updated scores for user {user_id} in {len(relevant_leaderboards)} leaderboards")
            
        except Exception as e:
            self.logger.error(f"Error updating user score: {e}")
    
    async def _update_leaderboard_entry(
        self,
        leaderboard_id: str,
        user_id: str,
        score: Union[int, float],
        username: str = "",
        display_name: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update or create an entry in a specific leaderboard."""
        try:
            if leaderboard_id not in self.leaderboard_data:
                self.leaderboard_data[leaderboard_id] = []
            
            entries = self.leaderboard_data[leaderboard_id]
            
            # Find existing entry
            existing_entry = None
            for entry in entries:
                if entry.user_id == user_id:
                    existing_entry = entry
                    break
            
            if existing_entry:
                # Update existing entry
                existing_entry.previous_rank = existing_entry.rank
                existing_entry.score = score
                existing_entry.last_updated = datetime.now(timezone.utc)
                if metadata:
                    existing_entry.metadata.update(metadata)
            else:
                # Create new entry
                new_entry = LeaderboardEntry(
                    user_id=user_id,
                    username=username or f"user_{user_id}",
                    display_name=display_name or username or f"User {user_id}",
                    score=score,
                    rank=len(entries) + 1,  # Temporary rank
                    metadata=metadata or {}
                )
                entries.append(new_entry)
            
            # Recalculate rankings
            await self._recalculate_rankings(leaderboard_id)
            
        except Exception as e:
            self.logger.error(f"Error updating leaderboard entry: {e}")
    
    async def _recalculate_rankings(self, leaderboard_id: str):
        """Recalculate rankings for a leaderboard."""
        try:
            if leaderboard_id not in self.leaderboard_data:
                return
            
            entries = self.leaderboard_data[leaderboard_id]
            leaderboard = self.leaderboards[leaderboard_id]
            
            # Sort by score (descending)
            entries.sort(key=lambda x: x.score, reverse=True)
            
            # Update rankings
            for i, entry in enumerate(entries):
                new_rank = i + 1
                if entry.previous_rank is None:
                    entry.previous_rank = new_rank
                
                entry.rank_change = (entry.previous_rank or new_rank) - new_rank
                entry.rank = new_rank
            
            # Limit entries to max_entries
            if len(entries) > leaderboard.max_entries:
                self.leaderboard_data[leaderboard_id] = entries[:leaderboard.max_entries]
            
            # Update leaderboard last_updated
            leaderboard.last_updated = datetime.now(timezone.utc)
            
        except Exception as e:
            self.logger.error(f"Error recalculating rankings: {e}")
    
    async def get_leaderboard(
        self,
        leaderboard_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get leaderboard data."""
        try:
            if leaderboard_id not in self.leaderboards:
                return {"error": "Leaderboard not found"}
            
            leaderboard = self.leaderboards[leaderboard_id]
            entries = self.leaderboard_data.get(leaderboard_id, [])
            
            # Apply pagination
            paginated_entries = entries[offset:offset + limit]
            
            return {
                "leaderboard": {
                    "id": leaderboard.id,
                    "name": leaderboard.name,
                    "description": leaderboard.description,
                    "type": leaderboard.leaderboard_type,
                    "metric": leaderboard.metric,
                    "last_updated": leaderboard.last_updated.isoformat() if leaderboard.last_updated else None,
                    "total_entries": len(entries)
                },
                "entries": [
                    {
                        "rank": entry.rank,
                        "previous_rank": entry.previous_rank,
                        "rank_change": entry.rank_change,
                        "user_id": entry.user_id,
                        "username": entry.username,
                        "display_name": entry.display_name,
                        "score": entry.score,
                        "avatar_url": entry.avatar_url,
                        "tier": entry.tier,
                        "badges": entry.badges,
                        "metadata": entry.metadata
                    }
                    for entry in paginated_entries
                ],
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": len(entries),
                    "has_more": offset + limit < len(entries)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return {"error": "Failed to retrieve leaderboard"}
    
    async def get_user_rank(self, user_id: str, leaderboard_id: str) -> Optional[Dict[str, Any]]:
        """Get a user's rank in a specific leaderboard."""
        try:
            entries = self.leaderboard_data.get(leaderboard_id, [])
            
            for entry in entries:
                if entry.user_id == user_id:
                    return {
                        "rank": entry.rank,
                        "previous_rank": entry.previous_rank,
                        "rank_change": entry.rank_change,
                        "score": entry.score,
                        "total_entries": len(entries),
                        "percentile": round((1 - (entry.rank - 1) / len(entries)) * 100, 1)
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user rank: {e}")
            return None
    
    async def get_user_rankings_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a summary of user's rankings across all leaderboards."""
        try:
            summary = {
                "user_id": user_id,
                "rankings": {},
                "best_ranks": [],
                "total_leaderboards": len(self.leaderboards)
            }
            
            best_ranks = []
            
            for lb_id, leaderboard in self.leaderboards.items():
                rank_data = await self.get_user_rank(user_id, lb_id)
                if rank_data:
                    summary["rankings"][lb_id] = {
                        "leaderboard_name": leaderboard.name,
                        "rank": rank_data["rank"],
                        "score": rank_data["score"],
                        "rank_change": rank_data["rank_change"],
                        "percentile": rank_data["percentile"]
                    }
                    
                    best_ranks.append({
                        "leaderboard_id": lb_id,
                        "leaderboard_name": leaderboard.name,
                        "rank": rank_data["rank"],
                        "percentile": rank_data["percentile"]
                    })
            
            # Sort by best percentile
            best_ranks.sort(key=lambda x: x["percentile"], reverse=True)
            summary["best_ranks"] = best_ranks[:5]
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting user rankings summary: {e}")
            return {}
    
    async def get_available_leaderboards(self) -> List[Dict[str, Any]]:
        """Get list of all available leaderboards."""
        try:
            return [
                {
                    "id": lb.id,
                    "name": lb.name,
                    "description": lb.description,
                    "type": lb.leaderboard_type,
                    "metric": lb.metric,
                    "max_entries": lb.max_entries,
                    "total_entries": len(self.leaderboard_data.get(lb.id, [])),
                    "last_updated": lb.last_updated.isoformat() if lb.last_updated else None
                }
                for lb in self.leaderboards.values()
                if lb.is_active
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting available leaderboards: {e}")
            return []
    
    async def create_custom_leaderboard(
        self,
        leaderboard_id: str,
        name: str,
        description: str,
        leaderboard_type: LeaderboardType,
        metric: LeaderboardMetric,
        max_entries: int = 50,
        category_filter: Optional[str] = None,
        tier_filter: Optional[str] = None
    ) -> bool:
        """Create a custom leaderboard."""
        try:
            if leaderboard_id in self.leaderboards:
                self.logger.warning(f"Leaderboard {leaderboard_id} already exists")
                return False
            
            leaderboard = Leaderboard(
                id=leaderboard_id,
                name=name,
                description=description,
                leaderboard_type=leaderboard_type,
                metric=metric,
                max_entries=max_entries,
                category_filter=category_filter,
                tier_filter=tier_filter
            )
            
            self.leaderboards[leaderboard_id] = leaderboard
            self.leaderboard_data[leaderboard_id] = []
            
            self.logger.info(f"Created custom leaderboard: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating custom leaderboard: {e}")
            return False


# Global instance
_leaderboards = None

def get_leaderboards(database_connection=None, cache_client=None) -> Leaderboards:
    """Get the global leaderboards instance."""
    global _leaderboards
    if _leaderboards is None:
        _leaderboards = Leaderboards(database_connection, cache_client)
    return _leaderboards