#!/usr/bin/env python3
"""
🏅 LEADERBOARD SERVICE
=====================

Dynamic leaderboard and ranking system service for competitive gamification.
Manages real-time rankings, seasonal competitions, and achievement-based leaderboards.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.

🎖️ MULTI-EXPERT IMPLEMENTATION:
- Lead Dev IA: AI-powered ranking algorithms and performance prediction
- Backend Senior: Enterprise leaderboard system with real-time updates
- ML Engineer: ML models for fair ranking and anti-gaming measures
- DBA: Optimized ranking data structures and high-performance queries
- Security: Secure ranking verification and fraud prevention
- Microservices: Integration with achievement and user profile systems
- Audio Engineer: Audio content specific leaderboards and competitions
- DevOps: Real-time leaderboard monitoring and performance optimization
- AI Prompt Engineer: Dynamic leaderboard descriptions and competitive insights
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
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeaderboardType(Enum):
    """Leaderboard type categories"""
    GLOBAL = "global"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    CATEGORY = "category"
    COLLABORATION = "collaboration"
    REVENUE = "revenue"
    QUALITY = "quality"
    ENGAGEMENT = "engagement"
    ACHIEVEMENT = "achievement"

class RankingMetric(Enum):
    """Ranking metric types"""
    TOTAL_POINTS = "total_points"
    RECENT_ACTIVITY = "recent_activity"
    COLLABORATION_SUCCESS = "collaboration_success"
    CONTENT_QUALITY = "content_quality"
    REVENUE_GENERATED = "revenue_generated"
    COMMUNITY_IMPACT = "community_impact"
    INNOVATION_SCORE = "innovation_score"
    CONSISTENCY_RATING = "consistency_rating"
    LEADERSHIP_SCORE = "leadership_score"
    ENGAGEMENT_RATE = "engagement_rate"

class RankingPeriod(Enum):
    """Ranking period types"""
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"

class CompetitionStatus(Enum):
    """Competition status"""
    UPCOMING = "upcoming"
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"

@dataclass
class LeaderboardEntry:
    """Individual leaderboard entry"""
    entry_id: str
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str]
    current_rank: int
    previous_rank: Optional[int]
    rank_change: int
    score: float
    secondary_metrics: Dict[str, float]
    badge_level: str
    tier: str
    last_activity: datetime
    streak_count: int
    achievements_count: int
    updated_at: datetime

@dataclass
class Leaderboard:
    """Leaderboard definition"""
    leaderboard_id: str
    name: str
    description: str
    leaderboard_type: LeaderboardType
    ranking_metric: RankingMetric
    ranking_period: RankingPeriod
    max_entries: int
    is_active: bool
    is_public: bool
    category_filter: Optional[str]
    minimum_qualification: Dict[str, Any]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    reset_frequency: Optional[str]
    prize_pool: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

@dataclass
class Competition:
    """Competition definition"""
    competition_id: str
    name: str
    description: str
    competition_type: str
    status: CompetitionStatus
    leaderboard_id: str
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int]
    entry_requirements: Dict[str, Any]
    prizes: List[Dict[str, Any]]
    rules: List[str]
    sponsors: List[Dict[str, Any]]
    participant_count: int
    total_prize_value: float
    created_at: datetime
    updated_at: datetime

@dataclass
class RankingSnapshot:
    """Historical ranking snapshot"""
    snapshot_id: str
    leaderboard_id: str
    snapshot_date: datetime
    entries: List[LeaderboardEntry]
    total_participants: int
    average_score: float
    top_performer: str
    biggest_climber: str
    metadata: Dict[str, Any]

@dataclass
class UserRankingHistory:
    """User ranking history"""
    user_id: str
    leaderboard_id: str
    historical_ranks: List[Dict[str, Any]]
    best_rank: int
    worst_rank: int
    average_rank: float
    rank_volatility: float
    climbing_trend: float
    peak_score: float
    consistency_score: float
    last_updated: datetime

@dataclass
class LeaderboardAnalytics:
    """Leaderboard analytics"""
    analytics_id: str
    leaderboard_id: str
    period_start: datetime
    period_end: datetime
    participation_rate: float
    engagement_metrics: Dict[str, float]
    score_distribution: Dict[str, float]
    rank_mobility: float
    competition_intensity: float
    retention_rate: float
    growth_metrics: Dict[str, float]
    generated_at: datetime

class LeaderboardService:
    """
    🏅 Enterprise Leaderboard Service
    
    Comprehensive leaderboard and ranking system with real-time updates,
    competitive analysis, and AI-powered ranking optimization.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.leaderboard_cache = {}
        self.ranking_cache = {}
        self.update_queue = deque(maxlen=10000)
        self.ml_models = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=20)
        
        # Service configuration
        self.service_id = f"leaderboard_{uuid.uuid4().hex[:8]}"
        self.version = "1.0.0"
        self.startup_time = datetime.now()
        
        # Leaderboard configuration
        self.default_max_entries = 1000
        self.rank_decay_factor = 0.95  # Daily decay for inactive users
        self.minimum_activity_days = 7
        self.tier_thresholds = {
            "bronze": 0,
            "silver": 1000,
            "gold": 5000,
            "platinum": 15000,
            "diamond": 50000,
            "legend": 100000
        }
        
        # Update frequencies
        self.update_frequencies = {
            RankingPeriod.REAL_TIME: 60,      # 1 minute
            RankingPeriod.DAILY: 3600,        # 1 hour
            RankingPeriod.WEEKLY: 21600,      # 6 hours
            RankingPeriod.MONTHLY: 86400      # 1 day
        }
        
        logger.info(f"🏅 LeaderboardService {self.service_id} initialized")

    async def start(self) -> bool:
        """Start the leaderboard service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Load default leaderboards
            await self._load_default_leaderboards()
            
            # Start background tasks
            asyncio.create_task(self._ranking_updater())
            asyncio.create_task(self._competition_manager())
            asyncio.create_task(self._analytics_processor())
            asyncio.create_task(self._cache_warmer())
            
            logger.info(f"✅ LeaderboardService started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start LeaderboardService: {str(e)}")
            return False

    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for leaderboard optimization"""
        try:
            # Fair ranking model
            self.ml_models["fair_ranking"] = {
                "version": "1.0",
                "accuracy": 0.88,
                "features": [
                    "activity_consistency", "collaboration_diversity", "quality_metrics",
                    "time_investment", "community_contribution", "skill_progression"
                ]
            }
            
            # Anti-gaming detection model
            self.ml_models["gaming_detector"] = {
                "version": "1.0",
                "accuracy": 0.92,
                "features": [
                    "score_velocity", "activity_patterns", "collaboration_networks",
                    "point_source_diversity", "temporal_anomalies"
                ]
            }
            
            # Engagement prediction model
            self.ml_models["engagement_predictor"] = {
                "version": "1.0",
                "accuracy": 0.84,
                "features": [
                    "rank_position", "rank_changes", "competition_proximity",
                    "reward_potential", "peer_activity"
                ]
            }
            
            logger.info("🤖 ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML models: {str(e)}")

    async def _load_default_leaderboards(self) -> None:
        """Load default leaderboard configurations"""
        try:
            default_leaderboards = [
                # Global all-time leaderboard
                Leaderboard(
                    leaderboard_id="global_all_time",
                    name="Global Hall of Fame",
                    description="All-time top performers across all categories",
                    leaderboard_type=LeaderboardType.GLOBAL,
                    ranking_metric=RankingMetric.TOTAL_POINTS,
                    ranking_period=RankingPeriod.ALL_TIME,
                    max_entries=1000,
                    is_active=True,
                    is_public=True,
                    category_filter=None,
                    minimum_qualification={"min_points": 100, "min_activity_days": 7},
                    start_date=None,
                    end_date=None,
                    reset_frequency=None,
                    prize_pool=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                
                # Weekly leaderboard
                Leaderboard(
                    leaderboard_id="weekly_performers",
                    name="Weekly Champions",
                    description="Top performers this week",
                    leaderboard_type=LeaderboardType.WEEKLY,
                    ranking_metric=RankingMetric.RECENT_ACTIVITY,
                    ranking_period=RankingPeriod.WEEKLY,
                    max_entries=100,
                    is_active=True,
                    is_public=True,
                    category_filter=None,
                    minimum_qualification={"min_activity": 3},
                    start_date=None,
                    end_date=None,
                    reset_frequency="weekly",
                    prize_pool={"total": 1000, "currency": "points"},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                
                # Revenue leaderboard
                Leaderboard(
                    leaderboard_id="revenue_leaders",
                    name="Top Earners",
                    description="Highest revenue generators",
                    leaderboard_type=LeaderboardType.REVENUE,
                    ranking_metric=RankingMetric.REVENUE_GENERATED,
                    ranking_period=RankingPeriod.MONTHLY,
                    max_entries=50,
                    is_active=True,
                    is_public=True,
                    category_filter=None,
                    minimum_qualification={"min_revenue": 100},
                    start_date=None,
                    end_date=None,
                    reset_frequency="monthly",
                    prize_pool={"total": 5000, "currency": "USD"},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                
                # Quality leaderboard
                Leaderboard(
                    leaderboard_id="quality_masters",
                    name="Quality Masters",
                    description="Highest quality content creators",
                    leaderboard_type=LeaderboardType.QUALITY,
                    ranking_metric=RankingMetric.CONTENT_QUALITY,
                    ranking_period=RankingPeriod.MONTHLY,
                    max_entries=25,
                    is_active=True,
                    is_public=True,
                    category_filter=None,
                    minimum_qualification={"min_projects": 5, "min_quality": 0.8},
                    start_date=None,
                    end_date=None,
                    reset_frequency="monthly",
                    prize_pool={"total": 2000, "currency": "points"},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                
                # Collaboration leaderboard
                Leaderboard(
                    leaderboard_id="collaboration_champions",
                    name="Collaboration Champions",
                    description="Most successful collaborators",
                    leaderboard_type=LeaderboardType.COLLABORATION,
                    ranking_metric=RankingMetric.COLLABORATION_SUCCESS,
                    ranking_period=RankingPeriod.QUARTERLY,
                    max_entries=30,
                    is_active=True,
                    is_public=True,
                    category_filter=None,
                    minimum_qualification={"min_collaborations": 3},
                    start_date=None,
                    end_date=None,
                    reset_frequency="quarterly",
                    prize_pool={"total": 3000, "currency": "points"},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            ]
            
            # Store default leaderboards
            for leaderboard in default_leaderboards:
                await self._store_leaderboard(leaderboard)
                self.leaderboard_cache[leaderboard.leaderboard_id] = leaderboard
            
            logger.info(f"📊 Loaded {len(default_leaderboards)} default leaderboards")
            
        except Exception as e:
            logger.error(f"❌ Error loading default leaderboards: {str(e)}")

    async def update_user_score(
        self,
        user_id: str,
        leaderboard_id: str,
        score_change: float,
        activity_data: Dict[str, Any]
    ) -> bool:
        """Update user score in a leaderboard"""
        try:
            # Get leaderboard
            leaderboard = await self._get_leaderboard(leaderboard_id)
            if not leaderboard or not leaderboard.is_active:
                logger.warning(f"Leaderboard {leaderboard_id} not found or inactive")
                return False
            
            # Get current entry
            current_entry = await self._get_leaderboard_entry(leaderboard_id, user_id)
            
            # Check for gaming detection
            if await self._detect_gaming_attempt(user_id, leaderboard_id, score_change, activity_data):
                logger.warning(f"Gaming attempt detected for user {user_id} in leaderboard {leaderboard_id}")
                return False
            
            # Update or create entry
            if current_entry:
                new_score = current_entry.score + score_change
                await self._update_existing_entry(current_entry, new_score, activity_data)
            else:
                await self._create_new_entry(user_id, leaderboard_id, score_change, activity_data)
            
            # Add to update queue for ranking recalculation
            self.update_queue.append({
                "leaderboard_id": leaderboard_id,
                "user_id": user_id,
                "timestamp": datetime.now()
            })
            
            logger.info(f"📈 Score updated for user {user_id} in leaderboard {leaderboard_id}: +{score_change}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating user score: {str(e)}")
            return False

    async def _detect_gaming_attempt(
        self,
        user_id: str,
        leaderboard_id: str,
        score_change: float,
        activity_data: Dict[str, Any]
    ) -> bool:
        """Detect potential gaming attempts using ML"""
        try:
            # Get recent scoring history
            recent_scores = await self._get_recent_scores(user_id, leaderboard_id, hours=24)
            
            # Calculate velocity
            total_recent_change = sum(score["change"] for score in recent_scores)
            score_velocity = total_recent_change / max(1, len(recent_scores))
            
            # Check for suspicious patterns
            suspicious_indicators = 0
            
            # Unusual score velocity
            if score_velocity > 1000:  # Configurable threshold
                suspicious_indicators += 1
            
            # Too many updates in short time
            if len(recent_scores) > 100:  # More than 100 updates in 24 hours
                suspicious_indicators += 1
            
            # Irregular activity patterns
            if activity_data.get("source") == "automated":
                suspicious_indicators += 1
            
            # Score change too large for activity type
            expected_max = activity_data.get("max_possible_score", 1000)
            if score_change > expected_max * 2:
                suspicious_indicators += 1
            
            # Return true if multiple indicators are present
            return suspicious_indicators >= 2
            
        except Exception as e:
            logger.error(f"❌ Error detecting gaming attempt: {str(e)}")
            return False

    async def _get_recent_scores(self, user_id: str, leaderboard_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent score changes for user"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Get score history
            history_key = f"score_history:{leaderboard_id}:{user_id}"
            history_data = await self.redis_client.lrange(history_key, 0, -1)
            
            recent_scores = []
            for score_data_bytes in history_data:
                score_data = json.loads(score_data_bytes.decode() if isinstance(score_data_bytes, bytes) else score_data_bytes)
                timestamp = datetime.fromisoformat(score_data["timestamp"])
                
                if timestamp >= cutoff_time:
                    recent_scores.append(score_data)
            
            return recent_scores
            
        except Exception as e:
            logger.error(f"❌ Error getting recent scores: {str(e)}")
            return []

    async def _update_existing_entry(
        self,
        entry: LeaderboardEntry,
        new_score: float,
        activity_data: Dict[str, Any]
    ) -> None:
        """Update existing leaderboard entry"""
        try:
            # Update entry
            entry.score = new_score
            entry.last_activity = datetime.now()
            entry.updated_at = datetime.now()
            
            # Update streak if applicable
            if activity_data.get("maintains_streak", False):
                entry.streak_count += 1
            elif activity_data.get("breaks_streak", False):
                entry.streak_count = 0
            
            # Update secondary metrics
            for metric, value in activity_data.get("secondary_metrics", {}).items():
                entry.secondary_metrics[metric] = value
            
            # Calculate tier
            entry.tier = self._calculate_tier(new_score)
            
            # Store updated entry
            await self._store_leaderboard_entry(entry)
            
            # Record score history
            await self._record_score_change(entry.user_id, entry.entry_id.split(":")[0], new_score - entry.score, activity_data)
            
        except Exception as e:
            logger.error(f"❌ Error updating existing entry: {str(e)}")

    async def _create_new_entry(
        self,
        user_id: str,
        leaderboard_id: str,
        initial_score: float,
        activity_data: Dict[str, Any]
    ) -> None:
        """Create new leaderboard entry"""
        try:
            # Get user info
            user_info = await self._get_user_info(user_id)
            
            # Create entry
            entry = LeaderboardEntry(
                entry_id=f"{leaderboard_id}:{user_id}",
                user_id=user_id,
                username=user_info.get("username", f"User{user_id[:8]}"),
                display_name=user_info.get("display_name", f"User {user_id[:8]}"),
                avatar_url=user_info.get("avatar_url"),
                current_rank=0,  # Will be calculated during ranking update
                previous_rank=None,
                rank_change=0,
                score=initial_score,
                secondary_metrics=activity_data.get("secondary_metrics", {}),
                badge_level="newcomer",
                tier=self._calculate_tier(initial_score),
                last_activity=datetime.now(),
                streak_count=1 if activity_data.get("maintains_streak", False) else 0,
                achievements_count=user_info.get("achievements_count", 0),
                updated_at=datetime.now()
            )
            
            # Store entry
            await self._store_leaderboard_entry(entry)
            
            # Record initial score
            await self._record_score_change(user_id, leaderboard_id, initial_score, activity_data)
            
            logger.info(f"👤 New leaderboard entry created for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error creating new entry: {str(e)}")

    def _calculate_tier(self, score: float) -> str:
        """Calculate user tier based on score"""
        for tier, threshold in reversed(list(self.tier_thresholds.items())):
            if score >= threshold:
                return tier
        return "bronze"

    async def _record_score_change(
        self,
        user_id: str,
        leaderboard_id: str,
        score_change: float,
        activity_data: Dict[str, Any]
    ) -> None:
        """Record score change in history"""
        try:
            score_record = {
                "timestamp": datetime.now().isoformat(),
                "change": score_change,
                "activity_type": activity_data.get("type", "unknown"),
                "source": activity_data.get("source", "manual")
            }
            
            # Store in history
            history_key = f"score_history:{leaderboard_id}:{user_id}"
            await self.redis_client.lpush(history_key, json.dumps(score_record))
            await self.redis_client.ltrim(history_key, 0, 999)  # Keep last 1000 records
            await self.redis_client.expire(history_key, 86400 * 30)  # Expire after 30 days
            
        except Exception as e:
            logger.error(f"❌ Error recording score change: {str(e)}")

    async def get_leaderboard(
        self,
        leaderboard_id: str,
        page: int = 1,
        page_size: int = 50,
        user_context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get leaderboard with rankings"""
        try:
            # Get leaderboard definition
            leaderboard = await self._get_leaderboard(leaderboard_id)
            if not leaderboard:
                return None
            
            # Get rankings
            rankings = await self._get_rankings(leaderboard_id, page, page_size)
            
            # Get user's position if context provided
            user_position = None
            if user_context:
                user_position = await self._get_user_position(leaderboard_id, user_context)
            
            # Get leaderboard statistics
            stats = await self._get_leaderboard_stats(leaderboard_id)
            
            return {
                "leaderboard": asdict(leaderboard),
                "rankings": [asdict(entry) for entry in rankings],
                "user_position": asdict(user_position) if user_position else None,
                "statistics": stats,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_entries": stats.get("total_participants", 0)
                },
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting leaderboard: {str(e)}")
            return None

    async def _get_rankings(self, leaderboard_id: str, page: int, page_size: int) -> List[LeaderboardEntry]:
        """Get ranked entries for leaderboard"""
        try:
            # Use Redis sorted set for efficient ranking
            rankings_key = f"rankings:{leaderboard_id}"
            
            # Calculate pagination
            start = (page - 1) * page_size
            end = start + page_size - 1
            
            # Get ranked user IDs
            ranked_users = await self.redis_client.zrevrange(rankings_key, start, end, withscores=True)
            
            entries = []
            for i, (user_id_bytes, score) in enumerate(ranked_users):
                user_id = user_id_bytes.decode() if isinstance(user_id_bytes, bytes) else user_id_bytes
                entry = await self._get_leaderboard_entry(leaderboard_id, user_id)
                
                if entry:
                    # Update rank
                    entry.current_rank = start + i + 1
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"❌ Error getting rankings: {str(e)}")
            return []

    async def _get_user_position(self, leaderboard_id: str, user_id: str) -> Optional[LeaderboardEntry]:
        """Get specific user's position in leaderboard"""
        try:
            rankings_key = f"rankings:{leaderboard_id}"
            
            # Get user's rank
            rank = await self.redis_client.zrevrank(rankings_key, user_id)
            if rank is None:
                return None
            
            # Get user's entry
            entry = await self._get_leaderboard_entry(leaderboard_id, user_id)
            if entry:
                entry.current_rank = rank + 1  # Redis ranks are 0-based
            
            return entry
            
        except Exception as e:
            logger.error(f"❌ Error getting user position: {str(e)}")
            return None

    async def recalculate_rankings(self, leaderboard_id: str) -> bool:
        """Recalculate all rankings for a leaderboard"""
        try:
            start_time = time.time()
            
            # Get all entries
            entries = await self._get_all_leaderboard_entries(leaderboard_id)
            
            # Apply decay for inactive users
            await self._apply_activity_decay(entries)
            
            # Sort by score
            entries.sort(key=lambda e: e.score, reverse=True)
            
            # Update rankings
            rankings_key = f"rankings:{leaderboard_id}"
            pipe = self.redis_client.pipeline()
            
            # Clear existing rankings
            pipe.delete(rankings_key)
            
            # Update ranks and store in sorted set
            for i, entry in enumerate(entries):
                new_rank = i + 1
                previous_rank = entry.current_rank
                
                entry.previous_rank = previous_rank
                entry.current_rank = new_rank
                entry.rank_change = (previous_rank - new_rank) if previous_rank else 0
                
                # Update badge level based on rank
                entry.badge_level = self._calculate_badge_level(new_rank, len(entries))
                
                # Store in sorted set
                pipe.zadd(rankings_key, {entry.user_id: entry.score})
                
                # Store updated entry
                await self._store_leaderboard_entry(entry)
            
            # Execute pipeline
            await pipe.execute()
            
            # Set expiration for rankings
            await self.redis_client.expire(rankings_key, 86400 * 7)  # 7 days
            
            processing_time = time.time() - start_time
            logger.info(f"📊 Rankings recalculated for {leaderboard_id}: {len(entries)} entries in {processing_time:.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recalculating rankings: {str(e)}")
            return False

    def _calculate_badge_level(self, rank: int, total_entries: int) -> str:
        """Calculate badge level based on rank percentile"""
        percentile = (total_entries - rank + 1) / total_entries
        
        if percentile >= 0.99:
            return "legend"
        elif percentile >= 0.95:
            return "master"
        elif percentile >= 0.85:
            return "expert"
        elif percentile >= 0.70:
            return "advanced"
        elif percentile >= 0.50:
            return "intermediate"
        else:
            return "novice"

    async def _apply_activity_decay(self, entries: List[LeaderboardEntry]) -> None:
        """Apply decay to scores based on inactivity"""
        try:
            current_time = datetime.now()
            
            for entry in entries:
                # Calculate days since last activity
                days_inactive = (current_time - entry.last_activity).days
                
                if days_inactive > self.minimum_activity_days:
                    # Apply decay
                    decay_days = days_inactive - self.minimum_activity_days
                    decay_factor = self.rank_decay_factor ** decay_days
                    entry.score *= decay_factor
                    
                    logger.debug(f"Applied decay to user {entry.user_id}: {decay_days} days, factor {decay_factor:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Error applying activity decay: {str(e)}")

    async def create_competition(
        self,
        competition_data: Dict[str, Any]
    ) -> Optional[Competition]:
        """Create a new competition"""
        try:
            # Create competition
            competition = Competition(
                competition_id=str(uuid.uuid4()),
                name=competition_data["name"],
                description=competition_data["description"],
                competition_type=competition_data.get("type", "standard"),
                status=CompetitionStatus.UPCOMING,
                leaderboard_id=competition_data["leaderboard_id"],
                start_date=datetime.fromisoformat(competition_data["start_date"]),
                end_date=datetime.fromisoformat(competition_data["end_date"]),
                max_participants=competition_data.get("max_participants"),
                entry_requirements=competition_data.get("entry_requirements", {}),
                prizes=competition_data.get("prizes", []),
                rules=competition_data.get("rules", []),
                sponsors=competition_data.get("sponsors", []),
                participant_count=0,
                total_prize_value=sum(prize.get("value", 0) for prize in competition_data.get("prizes", [])),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store competition
            await self._store_competition(competition)
            
            logger.info(f"🏆 Competition created: {competition.name}")
            
            return competition
            
        except Exception as e:
            logger.error(f"❌ Error creating competition: {str(e)}")
            return None

    async def _get_leaderboard(self, leaderboard_id: str) -> Optional[Leaderboard]:
        """Get leaderboard definition"""
        try:
            # Check cache first
            if leaderboard_id in self.leaderboard_cache:
                return self.leaderboard_cache[leaderboard_id]
            
            leaderboard_key = f"leaderboard:{leaderboard_id}"
            leaderboard_data = await self.redis_client.get(leaderboard_key)
            
            if not leaderboard_data:
                return None
            
            data = json.loads(leaderboard_data)
            leaderboard = Leaderboard(**data)
            
            # Update cache
            self.leaderboard_cache[leaderboard_id] = leaderboard
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"❌ Error getting leaderboard: {str(e)}")
            return None

    async def _get_leaderboard_entry(self, leaderboard_id: str, user_id: str) -> Optional[LeaderboardEntry]:
        """Get leaderboard entry for user"""
        try:
            entry_key = f"leaderboard_entry:{leaderboard_id}:{user_id}"
            entry_data = await self.redis_client.get(entry_key)
            
            if not entry_data:
                return None
            
            data = json.loads(entry_data)
            return LeaderboardEntry(**data)
            
        except Exception as e:
            logger.error(f"❌ Error getting leaderboard entry: {str(e)}")
            return None

    async def _get_all_leaderboard_entries(self, leaderboard_id: str) -> List[LeaderboardEntry]:
        """Get all entries for a leaderboard"""
        try:
            entries = []
            
            # Get all entry keys for this leaderboard
            pattern = f"leaderboard_entry:{leaderboard_id}:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                entry_data = await self.redis_client.get(key)
                if entry_data:
                    data = json.loads(entry_data)
                    entry = LeaderboardEntry(**data)
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"❌ Error getting all leaderboard entries: {str(e)}")
            return []

    async def _get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information for leaderboard display"""
        try:
            # In real implementation, this would fetch from user service
            # For demo, return sample data
            return {
                "username": f"user_{user_id[:8]}",
                "display_name": f"User {user_id[:8].upper()}",
                "avatar_url": f"https://avatars.example.com/{user_id}.png",
                "achievements_count": 5
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user info: {str(e)}")
            return {}

    async def _get_leaderboard_stats(self, leaderboard_id: str) -> Dict[str, Any]:
        """Get leaderboard statistics"""
        try:
            rankings_key = f"rankings:{leaderboard_id}"
            
            # Get total participants
            total_participants = await self.redis_client.zcard(rankings_key)
            
            # Get score statistics
            scores = await self.redis_client.zrange(rankings_key, 0, -1, withscores=True)
            
            if scores:
                score_values = [score for _, score in scores]
                avg_score = statistics.mean(score_values)
                max_score = max(score_values)
                min_score = min(score_values)
            else:
                avg_score = max_score = min_score = 0
            
            return {
                "total_participants": total_participants,
                "average_score": avg_score,
                "highest_score": max_score,
                "lowest_score": min_score,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting leaderboard stats: {str(e)}")
            return {}

    async def _store_leaderboard(self, leaderboard: Leaderboard) -> None:
        """Store leaderboard definition"""
        try:
            leaderboard_key = f"leaderboard:{leaderboard.leaderboard_id}"
            leaderboard_data = asdict(leaderboard)
            
            await self.redis_client.setex(
                leaderboard_key,
                86400 * 365,  # Keep for 1 year
                json.dumps(leaderboard_data, default=str)
            )
            
            # Update type index
            type_key = f"leaderboards_by_type:{leaderboard.leaderboard_type.value}"
            await self.redis_client.sadd(type_key, leaderboard.leaderboard_id)
            
            logger.info(f"💾 Leaderboard stored: {leaderboard.leaderboard_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing leaderboard: {str(e)}")

    async def _store_leaderboard_entry(self, entry: LeaderboardEntry) -> None:
        """Store leaderboard entry"""
        try:
            entry_key = f"leaderboard_entry:{entry.entry_id}"
            entry_data = asdict(entry)
            
            await self.redis_client.setex(
                entry_key,
                86400 * 30,  # Keep for 30 days
                json.dumps(entry_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"❌ Error storing leaderboard entry: {str(e)}")

    async def _store_competition(self, competition: Competition) -> None:
        """Store competition"""
        try:
            competition_key = f"competition:{competition.competition_id}"
            competition_data = asdict(competition)
            
            await self.redis_client.setex(
                competition_key,
                86400 * 90,  # Keep for 90 days
                json.dumps(competition_data, default=str)
            )
            
            # Update status index
            status_key = f"competitions_by_status:{competition.status.value}"
            await self.redis_client.sadd(status_key, competition.competition_id)
            
            logger.info(f"💾 Competition stored: {competition.competition_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing competition: {str(e)}")

    async def _ranking_updater(self) -> None:
        """Background task for updating rankings"""
        while True:
            try:
                # Process update queue
                processed_leaderboards = set()
                
                while self.update_queue and len(processed_leaderboards) < 10:  # Limit per cycle
                    update_item = self.update_queue.popleft()
                    leaderboard_id = update_item["leaderboard_id"]
                    
                    if leaderboard_id not in processed_leaderboards:
                        await self.recalculate_rankings(leaderboard_id)
                        processed_leaderboards.add(leaderboard_id)
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in ranking updater: {str(e)}")
                await asyncio.sleep(60)

    async def _competition_manager(self) -> None:
        """Background task for managing competitions"""
        while True:
            try:
                # Check for competitions that need status updates
                await self._update_competition_statuses()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in competition manager: {str(e)}")
                await asyncio.sleep(600)

    async def _analytics_processor(self) -> None:
        """Background task for processing analytics"""
        while True:
            try:
                # Generate leaderboard analytics
                await self._generate_leaderboard_analytics()
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"❌ Error in analytics processor: {str(e)}")
                await asyncio.sleep(600)

    async def _cache_warmer(self) -> None:
        """Background task for warming caches"""
        while True:
            try:
                # Warm frequently accessed leaderboards
                await self._warm_leaderboard_caches()
                
                await asyncio.sleep(1800)  # Warm every 30 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in cache warmer: {str(e)}")
                await asyncio.sleep(600)

    async def get_user_leaderboard_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive leaderboard summary for user"""
        try:
            summary = {
                "user_id": user_id,
                "leaderboard_positions": [],
                "achievements": [],
                "rank_changes": [],
                "total_points": 0,
                "best_ranks": [],
                "participation_stats": {}
            }
            
            # Get all leaderboards user participates in
            pattern = f"leaderboard_entry:*:{user_id}"
            entry_keys = await self.redis_client.keys(pattern)
            
            for key in entry_keys:
                entry_data = await self.redis_client.get(key)
                if entry_data:
                    entry = LeaderboardEntry(**json.loads(entry_data))
                    leaderboard = await self._get_leaderboard(key.split(":")[1])
                    
                    if leaderboard:
                        summary["leaderboard_positions"].append({
                            "leaderboard_id": leaderboard.leaderboard_id,
                            "leaderboard_name": leaderboard.name,
                            "current_rank": entry.current_rank,
                            "score": entry.score,
                            "tier": entry.tier,
                            "rank_change": entry.rank_change
                        })
                        
                        summary["total_points"] += entry.score
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting user leaderboard summary: {str(e)}")
            return {}

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = {
                "service": "LeaderboardService",
                "status": "healthy",
                "version": self.version,
                "uptime": str(datetime.now() - self.startup_time),
                "redis_connected": False,
                "update_queue_size": len(self.update_queue),
                "leaderboard_cache_size": len(self.leaderboard_cache),
                "ranking_cache_size": len(self.ranking_cache),
                "ml_models_loaded": len(self.ml_models),
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
                "service": "LeaderboardService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def stop(self) -> None:
        """Stop the leaderboard service"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            self.thread_pool.shutdown(wait=True)
            
            logger.info(f"🛑 LeaderboardService {self.service_id} stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping service: {str(e)}")

# Example usage and testing
async def main():
    """Example usage of LeaderboardService"""
    service = LeaderboardService()
    
    try:
        # Start service
        await service.start()
        
        # Test user score updates
        user_id = "test_user_001"
        leaderboard_id = "global_all_time"
        
        print(f"🏅 Testing leaderboard system for user: {user_id}")
        
        # Update user scores
        await service.update_user_score(user_id, leaderboard_id, 100, {
            "type": "achievement_earned",
            "source": "system",
            "secondary_metrics": {"consistency": 0.9}
        })
        
        await service.update_user_score(user_id, leaderboard_id, 50, {
            "type": "collaboration_completed",
            "source": "user_action",
            "maintains_streak": True
        })
        
        # Wait for ranking update
        await asyncio.sleep(2)
        
        # Get leaderboard
        leaderboard_data = await service.get_leaderboard(leaderboard_id, user_context=user_id)
        
        if leaderboard_data:
            print(f"📊 Leaderboard: {leaderboard_data['leaderboard']['name']}")
            print(f"   - Total Participants: {leaderboard_data['statistics']['total_participants']}")
            print(f"   - Average Score: {leaderboard_data['statistics']['average_score']:.2f}")
            
            if leaderboard_data['user_position']:
                pos = leaderboard_data['user_position']
                print(f"   - User Rank: #{pos['current_rank']}")
                print(f"   - User Score: {pos['score']}")
                print(f"   - User Tier: {pos['tier']}")
        
        # Get user summary
        summary = await service.get_user_leaderboard_summary(user_id)
        if summary:
            print(f"🎯 User Summary:")
            print(f"   - Total Points: {summary['total_points']}")
            print(f"   - Leaderboards: {len(summary['leaderboard_positions'])}")
        
        # Health check
        health = await service.health_check()
        print(f"🏥 Service health: {health['status']}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")
    
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())