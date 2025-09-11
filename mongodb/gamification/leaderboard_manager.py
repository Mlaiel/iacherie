"""MongoDB Leaderboard Manager
============================

Dynamic leaderboards and ranking system for gamification in the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

logger = logging.getLogger(__name__)

class LeaderboardType(Enum):
    """Leaderboard types."""
    GLOBAL_POINTS = "global_points"
    CATEGORY_POINTS = "category_points"
    WEEKLY_POINTS = "weekly_points"
    MONTHLY_POINTS = "monthly_points"
    CONTENT_CREATORS = "content_creators"
    COLLABORATORS = "collaborators"
    REVENUE_EARNERS = "revenue_earners"
    ENGAGEMENT_LEADERS = "engagement_leaders"
    ACHIEVEMENT_HUNTERS = "achievement_hunters"

class TimeFrame(Enum):
    """Leaderboard time frames."""
    ALL_TIME = "all_time"
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"

@dataclass
class LeaderboardConfig:
    """Leaderboard configuration."""
    leaderboard_id: str
    name: str
    description: str
    leaderboard_type: LeaderboardType
    time_frame: TimeFrame
    category_filter: Optional[str] = None
    min_activity_threshold: int = 0
    update_frequency_minutes: int = 60
    max_entries: int = 100
    enabled: bool = True

@dataclass
class LeaderboardEntry:
    """Individual leaderboard entry."""
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str]
    score: float
    rank: int
    previous_rank: Optional[int]
    rank_change: int
    additional_stats: Dict[str, Any]
    last_updated: datetime

class LeaderboardManager:
    """Enterprise-grade leaderboard management system."""
    
    def __init__(self, client: MongoClient, database_name: str):
        """Initialize leaderboard manager."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for leaderboard management")
            
        self.client = client
        self.database = client[database_name]
        
        # Collections
        self.leaderboards_collection = self.database['leaderboards']
        self.leaderboard_entries_collection = self.database['leaderboard_entries']
        self.leaderboard_history_collection = self.database['leaderboard_history']
        self.user_points_collection = self.database['user_points']
        self.points_transactions_collection = self.database['points_transactions']
        
        # Cache for performance
        self._leaderboard_cache = {}
        self._cache_ttl_minutes = 15
        
        # Initialize default leaderboards
        self._ensure_default_leaderboards()
    
    def _ensure_default_leaderboards(self):
        """Ensure default leaderboards exist."""
        default_leaderboards = [
            LeaderboardConfig(
                leaderboard_id="global_all_time",
                name="🏆 Global Champions",
                description="Top performers of all time across all categories",
                leaderboard_type=LeaderboardType.GLOBAL_POINTS,
                time_frame=TimeFrame.ALL_TIME,
                update_frequency_minutes=60,
                max_entries=100
            ),
            LeaderboardConfig(
                leaderboard_id="weekly_leaders",
                name="⚡ Weekly Leaders",
                description="Top performers this week",
                leaderboard_type=LeaderboardType.WEEKLY_POINTS,
                time_frame=TimeFrame.WEEKLY,
                update_frequency_minutes=30,
                max_entries=50
            ),
            LeaderboardConfig(
                leaderboard_id="monthly_stars",
                name="🌟 Monthly Stars",
                description="Top performers this month",
                leaderboard_type=LeaderboardType.MONTHLY_POINTS,
                time_frame=TimeFrame.MONTHLY,
                update_frequency_minutes=60,
                max_entries=50
            ),
            LeaderboardConfig(
                leaderboard_id="content_creators",
                name="🎬 Content Masters",
                description="Top content creators by engagement and quality",
                leaderboard_type=LeaderboardType.CONTENT_CREATORS,
                time_frame=TimeFrame.ALL_TIME,
                category_filter="content",
                min_activity_threshold=10,
                update_frequency_minutes=120,
                max_entries=25
            ),
            LeaderboardConfig(
                leaderboard_id="collaboration_experts",
                name="🤝 Collaboration Experts",
                description="Most successful collaborators",
                leaderboard_type=LeaderboardType.COLLABORATORS,
                time_frame=TimeFrame.ALL_TIME,
                category_filter="collaboration",
                min_activity_threshold=5,
                update_frequency_minutes=180,
                max_entries=25
            ),
            LeaderboardConfig(
                leaderboard_id="revenue_champions",
                name="💰 Revenue Champions",
                description="Top earners on the platform",
                leaderboard_type=LeaderboardType.REVENUE_EARNERS,
                time_frame=TimeFrame.ALL_TIME,
                category_filter="revenue",
                min_activity_threshold=1,
                update_frequency_minutes=240,
                max_entries=25
            ),
            LeaderboardConfig(
                leaderboard_id="engagement_leaders",
                name="📱 Engagement Leaders",
                description="Users with highest engagement rates",
                leaderboard_type=LeaderboardType.ENGAGEMENT_LEADERS,
                time_frame=TimeFrame.MONTHLY,
                category_filter="engagement",
                min_activity_threshold=20,
                update_frequency_minutes=120,
                max_entries=25
            ),
            LeaderboardConfig(
                leaderboard_id="achievement_hunters",
                name="🏅 Achievement Hunters",
                description="Users with most achievements unlocked",
                leaderboard_type=LeaderboardType.ACHIEVEMENT_HUNTERS,
                time_frame=TimeFrame.ALL_TIME,
                category_filter="achievement",
                update_frequency_minutes=360,
                max_entries=25
            )
        ]
        
        # Insert leaderboards if they don't exist
        for config in default_leaderboards:
            existing = self.leaderboards_collection.find_one(
                {"leaderboard_id": config.leaderboard_id}
            )
            
            if not existing:
                config_dict = asdict(config)
                config_dict["leaderboard_type"] = config.leaderboard_type.value
                config_dict["time_frame"] = config.time_frame.value
                config_dict["created_at"] = datetime.now()
                config_dict["last_updated"] = None
                
                self.leaderboards_collection.insert_one(config_dict)
                logger.info(f"Created default leaderboard: {config.name}")
    
    def update_leaderboard(self, leaderboard_id: str) -> bool:
        """Update a specific leaderboard."""
        try:
            # Get leaderboard configuration
            config_data = self.leaderboards_collection.find_one(
                {"leaderboard_id": leaderboard_id, "enabled": True}
            )
            
            if not config_data:
                logger.error(f"Leaderboard not found: {leaderboard_id}")
                return False
            
            # Convert to config object
            config = self._dict_to_config(config_data)
            
            # Get current entries for comparison
            current_entries = self._get_current_entries(leaderboard_id)
            current_ranks = {entry["user_id"]: entry["rank"] for entry in current_entries}
            
            # Calculate new leaderboard
            new_entries = self._calculate_leaderboard(config)
            
            # Add rank change information
            for i, entry in enumerate(new_entries):
                entry.rank = i + 1
                entry.previous_rank = current_ranks.get(entry.user_id)
                
                if entry.previous_rank:
                    entry.rank_change = entry.previous_rank - entry.rank
                else:
                    entry.rank_change = 0  # New entry
            
            # Store entries
            self._store_leaderboard_entries(leaderboard_id, new_entries)
            
            # Archive previous leaderboard for history
            if current_entries:
                self._archive_leaderboard(leaderboard_id, current_entries)
            
            # Update last updated timestamp
            self.leaderboards_collection.update_one(
                {"leaderboard_id": leaderboard_id},
                {"$set": {"last_updated": datetime.now()}}
            )
            
            # Clear cache
            cache_key = f"leaderboard_{leaderboard_id}"
            self._leaderboard_cache.pop(cache_key, None)
            
            logger.info(f"Updated leaderboard: {leaderboard_id} with {len(new_entries)} entries")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update leaderboard {leaderboard_id}: {e}")
            return False
    
    def _dict_to_config(self, config_data: Dict[str, Any]) -> LeaderboardConfig:
        """Convert dictionary to LeaderboardConfig object."""
        config_data["leaderboard_type"] = LeaderboardType(config_data["leaderboard_type"])
        config_data["time_frame"] = TimeFrame(config_data["time_frame"])
        config_data.pop("_id", None)
        config_data.pop("created_at", None)
        config_data.pop("last_updated", None)
        
        return LeaderboardConfig(**config_data)
    
    def _calculate_leaderboard(self, config: LeaderboardConfig) -> List[LeaderboardEntry]:
        """Calculate leaderboard entries based on configuration."""
        try:
            if config.leaderboard_type == LeaderboardType.GLOBAL_POINTS:
                return self._calculate_global_points_leaderboard(config)
            elif config.leaderboard_type == LeaderboardType.WEEKLY_POINTS:
                return self._calculate_time_based_leaderboard(config, days=7)
            elif config.leaderboard_type == LeaderboardType.MONTHLY_POINTS:
                return self._calculate_time_based_leaderboard(config, days=30)
            elif config.leaderboard_type == LeaderboardType.CONTENT_CREATORS:
                return self._calculate_content_creators_leaderboard(config)
            elif config.leaderboard_type == LeaderboardType.COLLABORATORS:
                return self._calculate_collaborators_leaderboard(config)
            elif config.leaderboard_type == LeaderboardType.REVENUE_EARNERS:
                return self._calculate_revenue_leaderboard(config)
            elif config.leaderboard_type == LeaderboardType.ENGAGEMENT_LEADERS:
                return self._calculate_engagement_leaderboard(config)
            elif config.leaderboard_type == LeaderboardType.ACHIEVEMENT_HUNTERS:
                return self._calculate_achievement_leaderboard(config)
            else:
                logger.warning(f"Unknown leaderboard type: {config.leaderboard_type}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to calculate leaderboard: {e}")
            return []
    
    def _calculate_global_points_leaderboard(self, config: LeaderboardConfig) -> List[LeaderboardEntry]:
        """Calculate global points leaderboard."""
        pipeline = [
            {"$match": {"total_points": {"$gt": config.min_activity_threshold}}},
            {"$sort": {"total_points": -1}},
            {"$limit": config.max_entries}
        ]
        
        user_points = list(self.user_points_collection.aggregate(pipeline))
        entries = []
        
        for user_data in user_points:
            # Get user info (would integrate with user service)
            user_info = self._get_user_info(user_data["user_id"])
            
            entry = LeaderboardEntry(
                user_id=user_data["user_id"],
                username=user_info.get("username", user_data["user_id"]),
                display_name=user_info.get("display_name", user_info.get("username", user_data["user_id"])),
                avatar_url=user_info.get("avatar_url"),
                score=user_data["total_points"],
                rank=0,  # Will be set later
                previous_rank=None,
                rank_change=0,
                additional_stats={
                    "total_points": user_data["total_points"],
                    "category_breakdown": user_data.get("category_points", {})
                },
                last_updated=datetime.now()
            )
            entries.append(entry)
        
        return entries
    
    def _calculate_time_based_leaderboard(self, config: LeaderboardConfig, days: int) -> List[LeaderboardEntry]:
        """Calculate time-based leaderboard (weekly, monthly)."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {
                "$group": {
                    "_id": "$user_id",
                    "total_points": {"$sum": "$points_change"},
                    "transaction_count": {"$sum": 1}
                }
            },
            {"$match": {"total_points": {"$gt": config.min_activity_threshold}}},
            {"$sort": {"total_points": -1}},
            {"$limit": config.max_entries}
        ]
        
        results = list(self.points_transactions_collection.aggregate(pipeline))
        entries = []
        
        for result in results:
            user_info = self._get_user_info(result["_id"])
            
            entry = LeaderboardEntry(
                user_id=result["_id"],
                username=user_info.get("username", result["_id"]),
                display_name=user_info.get("display_name", user_info.get("username", result["_id"])),
                avatar_url=user_info.get("avatar_url"),
                score=result["total_points"],
                rank=0,
                previous_rank=None,
                rank_change=0,
                additional_stats={
                    "period_points": result["total_points"],
                    "activity_count": result["transaction_count"],
                    "period_days": days
                },
                last_updated=datetime.now()
            )
            entries.append(entry)
        
        return entries
    
    def _calculate_content_creators_leaderboard(self, config: LeaderboardConfig) -> List[LeaderboardEntry]:
        """Calculate content creators leaderboard."""
        pipeline = [
            {"$match": {"category": "content"}},
            {
                "$group": {
                    "_id": "$user_id",
                    "content_points": {"$sum": "$points_change"},
                    "content_count": {"$sum": 1},
                    "avg_points": {"$avg": "$points_change"}
                }
            },
            {"$match": {"content_count": {"$gte": config.min_activity_threshold}}},
            {
                "$addFields": {
                    "composite_score": {
                        "$add": [
                            "$content_points",
                            {"$multiply": ["$avg_points", 10]}  # Bonus for quality
                        ]
                    }
                }
            },
            {"$sort": {"composite_score": -1}},
            {"$limit": config.max_entries}
        ]
        
        results = list(self.points_transactions_collection.aggregate(pipeline))
        entries = []
        
        for result in results:
            user_info = self._get_user_info(result["_id"])
            
            entry = LeaderboardEntry(
                user_id=result["_id"],
                username=user_info.get("username", result["_id"]),
                display_name=user_info.get("display_name", user_info.get("username", result["_id"])),
                avatar_url=user_info.get("avatar_url"),
                score=result["composite_score"],
                rank=0,
                previous_rank=None,
                rank_change=0,
                additional_stats={
                    "content_points": result["content_points"],
                    "content_count": result["content_count"],
                    "avg_points_per_content": result["avg_points"],
                    "composite_score": result["composite_score"]
                },
                last_updated=datetime.now()
            )
            entries.append(entry)
        
        return entries
    
    def _calculate_collaborators_leaderboard(self, config: LeaderboardConfig) -> List[LeaderboardEntry]:
        """Calculate collaborators leaderboard."""
        pipeline = [
            {"$match": {"category": "collaboration"}},
            {
                "$group": {
                    "_id": "$user_id",
                    "collaboration_points": {"$sum": "$points_change"},
                    "collaboration_count": {"$sum": 1},
                    "avg_points": {"$avg": "$points_change"}
                }
            },
            {"$match": {"collaboration_count": {"$gte": config.min_activity_threshold}}},
            {"$sort": {"collaboration_points": -1}},
            {"$limit": config.max_entries}
        ]
        
        results = list(self.points_transactions_collection.aggregate(pipeline))
        entries = []
        
        for result in results:
            user_info = self._get_user_info(result["_id"])
            
            entry = LeaderboardEntry(
                user_id=result["_id"],
                username=user_info.get("username", result["_id"]),
                display_name=user_info.get("display_name", user_info.get("username", result["_id"])),
                avatar_url=user_info.get("avatar_url"),
                score=result["collaboration_points"],
                rank=0,
                previous_rank=None,
                rank_change=0,
                additional_stats={
                    "collaboration_points": result["collaboration_points"],
                    "collaboration_count": result["collaboration_count"],
                    "avg_points_per_collaboration": result["avg_points"]
                },
                last_updated=datetime.now()
            )
            entries.append(entry)
        
        return entries
    
    def _calculate_revenue_leaderboard(self, config: LeaderboardConfig) -> List[LeaderboardEntry]:
        """Calculate revenue earners leaderboard."""
        pipeline = [
            {"$match": {"category": "revenue"}},
            {
                "$group": {
                    "_id": "$user_id",
                    "revenue_points": {"$sum": "$points_change"},
                    "revenue_events": {"$sum": 1}
                }
            },
            {"$match": {"revenue_events": {"$gte": config.min_activity_threshold}}},
            {"$sort": {"revenue_points": -1}},
            {"$limit": config.max_entries}
        ]
        
        results = list(self.points_transactions_collection.aggregate(pipeline))
        entries = []
        
        for result in results:
            user_info = self._get_user_info(result["_id"])
            
            entry = LeaderboardEntry(
                user_id=result["_id"],
                username=user_info.get("username", result["_id"]),
                display_name=user_info.get("display_name", user_info.get("username", result["_id"])),
                avatar_url=user_info.get("avatar_url"),
                score=result["revenue_points"],
                rank=0,
                previous_rank=None,
                rank_change=0,
                additional_stats={
                    "revenue_points": result["revenue_points"],
                    "revenue_events": result["revenue_events"]
                },
                last_updated=datetime.now()
            )
            entries.append(entry)
        
        return entries
    
    def _calculate_engagement_leaderboard(self, config: LeaderboardConfig) -> List[LeaderboardEntry]:
        """Calculate engagement leaders leaderboard."""
        # Get monthly engagement data
        cutoff_date = datetime.now() - timedelta(days=30)
        
        pipeline = [
            {
                "$match": {
                    "category": "engagement",
                    "timestamp": {"$gte": cutoff_date}
                }
            },
            {
                "$group": {
                    "_id": "$user_id",
                    "engagement_points": {"$sum": "$points_change"},
                    "engagement_count": {"$sum": 1}
                }
            },
            {"$match": {"engagement_count": {"$gte": config.min_activity_threshold}}},
            {"$sort": {"engagement_points": -1}},
            {"$limit": config.max_entries}
        ]
        
        results = list(self.points_transactions_collection.aggregate(pipeline))
        entries = []
        
        for result in results:
            user_info = self._get_user_info(result["_id"])
            
            entry = LeaderboardEntry(
                user_id=result["_id"],
                username=user_info.get("username", result["_id"]),
                display_name=user_info.get("display_name", user_info.get("username", result["_id"])),
                avatar_url=user_info.get("avatar_url"),
                score=result["engagement_points"],
                rank=0,
                previous_rank=None,
                rank_change=0,
                additional_stats={
                    "engagement_points": result["engagement_points"],
                    "engagement_count": result["engagement_count"],
                    "period": "last_30_days"
                },
                last_updated=datetime.now()
            )
            entries.append(entry)
        
        return entries
    
    def _calculate_achievement_leaderboard(self, config: LeaderboardConfig) -> List[LeaderboardEntry]:
        """Calculate achievement hunters leaderboard."""
        pipeline = [
            {"$match": {"category": "achievement"}},
            {
                "$group": {
                    "_id": "$user_id",
                    "achievement_points": {"$sum": "$points_change"},
                    "achievement_count": {"$sum": 1}
                }
            },
            {"$sort": {"achievement_count": -1, "achievement_points": -1}},
            {"$limit": config.max_entries}
        ]
        
        results = list(self.points_transactions_collection.aggregate(pipeline))
        entries = []
        
        for result in results:
            user_info = self._get_user_info(result["_id"])
            
            entry = LeaderboardEntry(
                user_id=result["_id"],
                username=user_info.get("username", result["_id"]),
                display_name=user_info.get("display_name", user_info.get("username", result["_id"])),
                avatar_url=user_info.get("avatar_url"),
                score=result["achievement_count"],
                rank=0,
                previous_rank=None,
                rank_change=0,
                additional_stats={
                    "achievement_count": result["achievement_count"],
                    "achievement_points": result["achievement_points"]
                },
                last_updated=datetime.now()
            )
            entries.append(entry)
        
        return entries
    
    def _get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information (placeholder - would integrate with user service)."""
        # This would integrate with the user management system
        return {
            "username": f"user_{user_id[:8]}",
            "display_name": f"User {user_id[:8]}",
            "avatar_url": f"/avatars/{user_id}.jpg"
        }
    
    def _get_current_entries(self, leaderboard_id: str) -> List[Dict[str, Any]]:
        """Get current leaderboard entries."""
        try:
            entries = list(
                self.leaderboard_entries_collection.find(
                    {"leaderboard_id": leaderboard_id}
                ).sort("rank", 1)
            )
            
            for entry in entries:
                entry.pop("_id", None)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get current entries: {e}")
            return []
    
    def _store_leaderboard_entries(self, leaderboard_id: str, entries: List[LeaderboardEntry]):
        """Store new leaderboard entries."""
        try:
            # Remove existing entries
            self.leaderboard_entries_collection.delete_many(
                {"leaderboard_id": leaderboard_id}
            )
            
            # Insert new entries
            if entries:
                entries_data = []
                for entry in entries:
                    entry_dict = asdict(entry)
                    entry_dict["leaderboard_id"] = leaderboard_id
                    entries_data.append(entry_dict)
                
                self.leaderboard_entries_collection.insert_many(entries_data)
            
        except Exception as e:
            logger.error(f"Failed to store leaderboard entries: {e}")
    
    def _archive_leaderboard(self, leaderboard_id: str, entries: List[Dict[str, Any]]):
        """Archive previous leaderboard for history."""
        try:
            if entries:
                archive_data = {
                    "leaderboard_id": leaderboard_id,
                    "archived_at": datetime.now(),
                    "entries": entries
                }
                
                self.leaderboard_history_collection.insert_one(archive_data)
            
        except Exception as e:
            logger.error(f"Failed to archive leaderboard: {e}")
    
    def get_leaderboard(self, leaderboard_id: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get leaderboard entries."""
        try:
            # Check cache first
            cache_key = f"leaderboard_{leaderboard_id}"
            
            if use_cache and cache_key in self._leaderboard_cache:
                cached_data = self._leaderboard_cache[cache_key]
                cache_time = cached_data["timestamp"]
                
                if datetime.now() - cache_time < timedelta(minutes=self._cache_ttl_minutes):
                    return cached_data["entries"]
            
            # Get from database
            entries = self._get_current_entries(leaderboard_id)
            
            # Cache results
            if use_cache:
                self._leaderboard_cache[cache_key] = {
                    "timestamp": datetime.now(),
                    "entries": entries
                }
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            return []
    
    def get_user_rank(self, leaderboard_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's rank in a specific leaderboard."""
        try:
            entry = self.leaderboard_entries_collection.find_one({
                "leaderboard_id": leaderboard_id,
                "user_id": user_id
            })
            
            if entry:
                entry.pop("_id", None)
                return entry
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user rank: {e}")
            return None
    
    def get_leaderboard_configs(self) -> List[Dict[str, Any]]:
        """Get all leaderboard configurations."""
        try:
            configs = list(self.leaderboards_collection.find({"enabled": True}))
            
            for config in configs:
                config.pop("_id", None)
            
            return configs
            
        except Exception as e:
            logger.error(f"Failed to get leaderboard configs: {e}")
            return []
    
    def update_all_leaderboards(self) -> int:
        """Update all enabled leaderboards."""
        updated_count = 0
        
        try:
            configs = self.get_leaderboard_configs()
            
            for config in configs:
                if self.update_leaderboard(config["leaderboard_id"]):
                    updated_count += 1
            
            logger.info(f"Updated {updated_count}/{len(configs)} leaderboards")
            return updated_count
            
        except Exception as e:
            logger.error(f"Failed to update all leaderboards: {e}")
            return updated_count

# Export the main class
__all__ = ['LeaderboardManager', 'LeaderboardConfig', 'LeaderboardEntry', 'LeaderboardType', 'TimeFrame']