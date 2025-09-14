"""Leaderboard Management Workflow

AI-powered leaderboard management and ranking system workflow.

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
from ..utils.caching import CacheManager

logger = logging.getLogger(__name__)


class LeaderboardType(Enum):
    """Types of leaderboards"""
    GLOBAL = "global"
    WEEKLY = "weekly" 
    MONTHLY = "monthly"
    CATEGORY = "category"
    REGIONAL = "regional"
    TEAM = "team"


@dataclass
class LeaderboardEntry:
    """Leaderboard entry data"""
    user_id: str
    username: str
    score: float
    rank: int
    previous_rank: int
    rank_change: int
    category: str = ""
    team_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeaderboardData:
    """Complete leaderboard data"""
    leaderboard_id: str
    leaderboard_type: LeaderboardType
    entries: List[LeaderboardEntry]
    total_participants: int
    period_start: datetime
    period_end: datetime
    last_updated: datetime = field(default_factory=datetime.utcnow)


class LeaderboardManagementWorkflow:
    """AI-powered leaderboard management workflow"""
    
    def __init__(self) -> None:
        self.metrics_collector = MetricsCollector()
        self.cache_manager = CacheManager()
        self.leaderboards: Dict[str, LeaderboardData] = {}
        
    async def update_leaderboard(
        self,
        leaderboard_id: str,
        leaderboard_type: LeaderboardType,
        user_scores: Dict[str, float],
        category: str = ""
    ) -> LeaderboardData:
        """
        Update leaderboard with new scores
        
        Args:
            leaderboard_id: Unique leaderboard identifier
            leaderboard_type: Type of leaderboard
            user_scores: Dictionary of user_id to score mappings
            category: Optional category for filtered leaderboards
            
        Returns:
            LeaderboardData with updated rankings
        """
        try:
            start_time = datetime.utcnow()
            
            logger.info(f"Updating leaderboard {leaderboard_id} with {len(user_scores)} entries")
            
            # Get existing leaderboard or create new one
            existing_leaderboard = self.leaderboards.get(leaderboard_id)
            previous_rankings = {}
            
            if existing_leaderboard:
                previous_rankings = {
                    entry.user_id: entry.rank 
                    for entry in existing_leaderboard.entries
                }
            
            # Create leaderboard entries
            entries = []
            sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
            
            for rank, (user_id, score) in enumerate(sorted_users, 1):
                previous_rank = previous_rankings.get(user_id, 0)
                rank_change = previous_rank - rank if previous_rank > 0 else 0
                
                # Get user metadata
                username = await self._get_username(user_id)
                
                entry = LeaderboardEntry(
                    user_id=user_id,
                    username=username,
                    score=score,
                    rank=rank,
                    previous_rank=previous_rank,
                    rank_change=rank_change,
                    category=category,
                    metadata=await self._get_user_metadata(user_id)
                )
                
                entries.append(entry)
            
            # Determine period based on leaderboard type
            period_start, period_end = await self._get_leaderboard_period(leaderboard_type)
            
            # Create updated leaderboard
            leaderboard = LeaderboardData(
                leaderboard_id=leaderboard_id,
                leaderboard_type=leaderboard_type,
                entries=entries,
                total_participants=len(entries),
                period_start=period_start,
                period_end=period_end
            )
            
            # Store leaderboard
            self.leaderboards[leaderboard_id] = leaderboard
            
            # Cache leaderboard
            await self._cache_leaderboard(leaderboard)
            
            # Send notifications for significant rank changes
            await self._notify_rank_changes(entries)
            
            # Record metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_metric("leaderboard_update_duration", duration)
            await self.metrics_collector.record_metric("leaderboard_participants", len(entries))
            
            logger.info(f"Leaderboard {leaderboard_id} updated successfully")
            return leaderboard
            
        except Exception as e:
            logger.error(f"Leaderboard update failed for {leaderboard_id}: {e}")
            raise WorkflowError(f"Leaderboard update failed: {e}")
    
    async def get_leaderboard(
        self,
        leaderboard_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> LeaderboardData:
        """Get leaderboard data with pagination"""
        
        if leaderboard_id not in self.leaderboards:
            # Try to load from cache
            cached_leaderboard = await self.cache_manager.get(f"leaderboard_{leaderboard_id}")
            if cached_leaderboard:
                self.leaderboards[leaderboard_id] = cached_leaderboard
            else:
                raise WorkflowError(f"Leaderboard {leaderboard_id} not found")
        
        leaderboard = self.leaderboards[leaderboard_id]
        
        # Apply pagination
        paginated_entries = leaderboard.entries[offset:offset + limit]
        
        return LeaderboardData(
            leaderboard_id=leaderboard.leaderboard_id,
            leaderboard_type=leaderboard.leaderboard_type,
            entries=paginated_entries,
            total_participants=leaderboard.total_participants,
            period_start=leaderboard.period_start,
            period_end=leaderboard.period_end,
            last_updated=leaderboard.last_updated
        )
    
    async def get_user_rank(self, leaderboard_id: str, user_id: str) -> Optional[LeaderboardEntry]:
        """Get specific user's rank in leaderboard"""
        
        if leaderboard_id not in self.leaderboards:
            return None
        
        leaderboard = self.leaderboards[leaderboard_id]
        
        for entry in leaderboard.entries:
            if entry.user_id == user_id:
                return entry
        
        return None
    
    async def get_surrounding_ranks(
        self,
        leaderboard_id: str,
        user_id: str,
        context_size: int = 5
    ) -> List[LeaderboardEntry]:
        """Get users around specific user's rank"""
        
        user_entry = await self.get_user_rank(leaderboard_id, user_id)
        if not user_entry:
            return []
        
        leaderboard = self.leaderboards[leaderboard_id]
        user_rank = user_entry.rank
        
        start_rank = max(1, user_rank - context_size)
        end_rank = min(len(leaderboard.entries), user_rank + context_size)
        
        surrounding_entries = [
            entry for entry in leaderboard.entries
            if start_rank <= entry.rank <= end_rank
        ]
        
        return surrounding_entries
    
    async def create_category_leaderboard(
        self,
        base_leaderboard_id: str,
        category: str,
        limit: int = 100
    ) -> LeaderboardData:
        """Create filtered leaderboard by category"""
        
        if base_leaderboard_id not in self.leaderboards:
            raise WorkflowError(f"Base leaderboard {base_leaderboard_id} not found")
        
        base_leaderboard = self.leaderboards[base_leaderboard_id]
        
        # Filter entries by category
        category_entries = [
            entry for entry in base_leaderboard.entries
            if entry.category == category or category in entry.metadata.get("categories", [])
        ]
        
        # Re-rank filtered entries
        for rank, entry in enumerate(category_entries[:limit], 1):
            entry.rank = rank
        
        category_leaderboard_id = f"{base_leaderboard_id}_{category}"
        
        category_leaderboard = LeaderboardData(
            leaderboard_id=category_leaderboard_id,
            leaderboard_type=LeaderboardType.CATEGORY,
            entries=category_entries[:limit],
            total_participants=len(category_entries),
            period_start=base_leaderboard.period_start,
            period_end=base_leaderboard.period_end
        )
        
        self.leaderboards[category_leaderboard_id] = category_leaderboard
        await self._cache_leaderboard(category_leaderboard)
        
        return category_leaderboard
    
    async def get_leaderboard_analytics(self, leaderboard_id: str) -> Dict[str, Any]:
        """Get analytics for leaderboard"""
        
        if leaderboard_id not in self.leaderboards:
            return {"error": "Leaderboard not found"}
        
        leaderboard = self.leaderboards[leaderboard_id]
        entries = leaderboard.entries
        
        if not entries:
            return {"error": "No entries in leaderboard"}
        
        # Calculate analytics
        scores = [entry.score for entry in entries]
        rank_changes = [entry.rank_change for entry in entries if entry.rank_change != 0]
        
        analytics = {
            "total_participants": leaderboard.total_participants,
            "score_statistics": {
                "max_score": max(scores),
                "min_score": min(scores),
                "average_score": sum(scores) / len(scores),
                "median_score": sorted(scores)[len(scores) // 2]
            },
            "rank_movement": {
                "users_moved_up": len([rc for rc in rank_changes if rc > 0]),
                "users_moved_down": len([rc for rc in rank_changes if rc < 0]),
                "users_unchanged": len(entries) - len(rank_changes),
                "biggest_climb": max(rank_changes) if rank_changes else 0,
                "biggest_drop": min(rank_changes) if rank_changes else 0
            },
            "participation_trends": await self._analyze_participation_trends(leaderboard_id),
            "competition_intensity": await self._calculate_competition_intensity(scores)
        }
        
        return analytics
    
    async def reset_leaderboard(self, leaderboard_id: str, archive: bool = True) -> bool:
        """Reset leaderboard for new period"""
        
        if leaderboard_id not in self.leaderboards:
            return False
        
        leaderboard = self.leaderboards[leaderboard_id]
        
        # Archive current leaderboard if requested
        if archive:
            archive_id = f"{leaderboard_id}_archive_{int(datetime.utcnow().timestamp())}"
            await self._archive_leaderboard(leaderboard, archive_id)
        
        # Reset leaderboard
        period_start, period_end = await self._get_leaderboard_period(leaderboard.leaderboard_type)
        
        reset_leaderboard = LeaderboardData(
            leaderboard_id=leaderboard_id,
            leaderboard_type=leaderboard.leaderboard_type,
            entries=[],
            total_participants=0,
            period_start=period_start,
            period_end=period_end
        )
        
        self.leaderboards[leaderboard_id] = reset_leaderboard
        await self._cache_leaderboard(reset_leaderboard)
        
        logger.info(f"Leaderboard {leaderboard_id} reset successfully")
        return True
    
    async def _get_username(self, user_id: str) -> str:
        """Get username for user ID"""
        # In real implementation, this would query user database
        return f"User_{user_id[-4:]}"
    
    async def _get_user_metadata(self, user_id: str) -> Dict[str, Any]:
        """Get user metadata for leaderboard display"""
        # In real implementation, this would query user profile
        return {
            "avatar_url": f"https://example.com/avatars/{user_id}.jpg",
            "level": 10,
            "badges": ["Creator", "Contributor"],
            "categories": ["content", "engagement"]
        }
    
    async def _get_leaderboard_period(self, leaderboard_type: LeaderboardType) -> tuple:
        """Get period start and end dates for leaderboard type"""
        now = datetime.utcnow()
        
        if leaderboard_type == LeaderboardType.WEEKLY:
            start = now - timedelta(days=now.weekday())
            end = start + timedelta(days=7)
        elif leaderboard_type == LeaderboardType.MONTHLY:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        else:  # GLOBAL or other types
            start = datetime(2025, 1, 1)  # Platform launch
            end = datetime(2030, 1, 1)   # Far future
        
        return start, end
    
    async def _cache_leaderboard(self, leaderboard -> None: LeaderboardData) -> None:
        """Cache leaderboard data"""
        cache_key = f"leaderboard_{leaderboard.leaderboard_id}"
        await self.cache_manager.set(cache_key, leaderboard, ttl=3600)
    
    async def _notify_rank_changes(self, entries -> None: List[LeaderboardEntry]) -> None:
        """Send notifications for significant rank changes"""
        significant_changes = [
            entry for entry in entries
            if abs(entry.rank_change) >= 5  # Notify for changes of 5+ positions
        ]
        
        for entry in significant_changes:
            if entry.rank_change > 0:
                message = f"Congratulations! You've climbed {entry.rank_change} positions to rank #{entry.rank}!"
            else:
                message = f"You've dropped {abs(entry.rank_change)} positions to rank #{entry.rank}. Keep pushing!"
            
            # In real implementation, send notification
            logger.info(f"Rank change notification for {entry.user_id}: {message}")
    
    async def _analyze_participation_trends(self, leaderboard_id: str) -> Dict[str, Any]:
        """Analyze participation trends"""
        # Simulate participation analysis
        return {
            "participation_growth": "5% increase from last period",
            "retention_rate": 0.85,
            "new_participants": 150,
            "returning_participants": 850
        }
    
    async def _calculate_competition_intensity(self, scores: List[float]) -> float:
        """Calculate how competitive the leaderboard is"""
        if len(scores) < 2:
            return 0.0
        
        # Calculate coefficient of variation as intensity measure
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        
        if mean_score == 0:
            return 0.0
        
        coefficient_of_variation = std_dev / mean_score
        
        # Normalize to 0-1 scale
        intensity = min(coefficient_of_variation, 1.0)
        return round(intensity, 3)
    
    async def _archive_leaderboard(self, leaderboard -> None: LeaderboardData, archive_id -> None: str) -> None:
        """Archive leaderboard data"""
        archive_key = f"leaderboard_archive_{archive_id}"
        await self.cache_manager.set(archive_key, leaderboard, ttl=86400 * 365)  # 1 year
        logger.info(f"Leaderboard archived as {archive_id}")