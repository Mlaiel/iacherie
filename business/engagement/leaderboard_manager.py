"""
Enterprise Leaderboard Manager - Dynamic leaderboard system for IA Influencer platform.

This module provides a comprehensive leaderboard management system that creates
dynamic rankings, competitive environments, and recognition systems for
multi-format content creators.

Architecture: Enterprise Production-Ready (Backend Level 2)
Module: backend/business/engagement/leaderboard_manager.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Creator Upload → AI Processing → Protection → SEO → Collaboration Matching + Gamification →
Leaderboard Ranking → Distribution → Monetization → Analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from uuid import uuid4, UUID
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from dataclasses import dataclass, field
import json
import math

logger = logging.getLogger(__name__)


class LeaderboardType(str, Enum):
    """Types of leaderboards."""
    GLOBAL = "global"
    REGIONAL = "regional"
    CATEGORY = "category"
    CREATOR_TYPE = "creator_type"
    PLATFORM = "platform"
    SKILL_LEVEL = "skill_level"
    CHALLENGE = "challenge"
    COLLABORATION = "collaboration"
    SEASONAL = "seasonal"
    CUSTOM = "custom"


class LeaderboardMetric(str, Enum):
    """Metrics used for leaderboard rankings."""
    EXPERIENCE_POINTS = "experience_points"
    CONTENT_COUNT = "content_count"
    COLLABORATION_COUNT = "collaboration_count"
    TOTAL_REVENUE = "total_revenue"
    ENGAGEMENT_RATE = "engagement_rate"
    QUALITY_SCORE = "quality_score"
    STREAK_DAYS = "streak_days"
    ACHIEVEMENT_COUNT = "achievement_count"
    COMMUNITY_IMPACT = "community_impact"
    INNOVATION_SCORE = "innovation_score"
    GLOBAL_REACH = "global_reach"
    VIRAL_CONTENT_COUNT = "viral_content_count"
    MENTORSHIP_IMPACT = "mentorship_impact"
    PLATFORM_MASTERY = "platform_mastery"
    COMPOSITE_SCORE = "composite_score"


class LeaderboardScope(str, Enum):
    """Scope/duration of leaderboards."""
    ALL_TIME = "all_time"
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"
    REAL_TIME = "real_time"


class LeaderboardStatus(str, Enum):
    """Status of leaderboards."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class LeaderboardEntry:
    """Represents a single entry in a leaderboard."""
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    leaderboard_id: str = ""
    
    # Ranking information
    current_rank: int = 0
    previous_rank: Optional[int] = None
    rank_change: int = 0
    
    # Score information
    score: Decimal = field(default_factory=lambda: Decimal('0'))
    previous_score: Optional[Decimal] = None
    score_change: Decimal = field(default_factory=lambda: Decimal('0'))
    
    # Component scores (for composite rankings)
    component_scores: Dict[str, Decimal] = field(default_factory=dict)
    
    # User information (cached for performance)
    user_display_name: str = ""
    user_avatar_url: str = ""
    user_creator_type: str = ""
    user_level: int = 1
    user_badges: List[str] = field(default_factory=list)
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.utcnow)
    streak_count: int = 0
    total_achievements: int = 0
    
    # Performance indicators
    trending_up: bool = False
    momentum_score: float = 0.0
    consistency_score: float = 0.0
    
    def get_rank_change_indicator(self) -> str:
        """Get visual indicator for rank change."""
        if self.rank_change > 0:
            return f"↑{self.rank_change}"
        elif self.rank_change < 0:
            return f"↓{abs(self.rank_change)}"
        else:
            return "→"
    
    def get_score_change_percentage(self) -> float:
        """Get percentage change in score."""
        if not self.previous_score or self.previous_score == 0:
            return 0.0
        
        change = float(self.score - self.previous_score)
        return (change / float(self.previous_score)) * 100


@dataclass
class LeaderboardDefinition:
    """Defines a leaderboard configuration."""
    leaderboard_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    
    # Configuration
    leaderboard_type: LeaderboardType = LeaderboardType.GLOBAL
    primary_metric: LeaderboardMetric = LeaderboardMetric.EXPERIENCE_POINTS
    secondary_metrics: List[LeaderboardMetric] = field(default_factory=list)
    scope: LeaderboardScope = LeaderboardScope.ALL_TIME
    
    # Filtering and segmentation
    creator_type_filter: Optional[str] = None
    region_filter: Optional[str] = None
    platform_filter: Optional[str] = None
    skill_level_filter: Optional[str] = None
    custom_filters: Dict[str, Any] = field(default_factory=dict)
    
    # Ranking configuration
    max_entries: int = 1000
    min_score_threshold: Optional[Decimal] = None
    composite_weights: Dict[str, float] = field(default_factory=dict)
    
    # Update configuration
    update_frequency: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    real_time_updates: bool = False
    
    # Rewards and recognition
    top_tier_rewards: Dict[str, Any] = field(default_factory=dict)
    participation_rewards: Dict[str, Any] = field(default_factory=dict)
    milestone_rewards: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    
    # Visibility and access
    public: bool = True
    featured: bool = False
    requires_opt_in: bool = False
    
    # Administrative
    status: LeaderboardStatus = LeaderboardStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    
    # Statistics
    total_participants: int = 0
    active_participants: int = 0
    last_calculation: Optional[datetime] = None
    
    def is_user_eligible(self, user_profile: Dict[str, Any]) -> bool:
        """Check if a user is eligible for this leaderboard."""
        # Check creator type filter
        if self.creator_type_filter:
            user_creator_type = user_profile.get("creator_type", "")
            if user_creator_type != self.creator_type_filter:
                return False
        
        # Check region filter
        if self.region_filter:
            user_region = user_profile.get("region", "")
            if user_region != self.region_filter:
                return False
        
        # Check platform filter
        if self.platform_filter:
            user_platforms = user_profile.get("connected_platforms", [])
            if self.platform_filter not in user_platforms:
                return False
        
        # Check skill level filter
        if self.skill_level_filter:
            user_level = user_profile.get("level", 1)
            level_ranges = {
                "beginner": (1, 10),
                "intermediate": (11, 30),
                "advanced": (31, 60),
                "expert": (61, 100)
            }
            
            if self.skill_level_filter in level_ranges:
                min_level, max_level = level_ranges[self.skill_level_filter]
                if not (min_level <= user_level <= max_level):
                    return False
        
        # Check custom filters
        for filter_key, filter_value in self.custom_filters.items():
            user_value = user_profile.get(filter_key)
            if user_value != filter_value:
                return False
        
        return True
    
    def get_scope_start_date(self) -> Optional[datetime]:
        """Get the start date for the current scope period."""
        now = datetime.utcnow()
        
        if self.scope == LeaderboardScope.ALL_TIME:
            return None
        elif self.scope == LeaderboardScope.YEARLY:
            return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif self.scope == LeaderboardScope.MONTHLY:
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif self.scope == LeaderboardScope.WEEKLY:
            days_since_monday = now.weekday()
            return (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.scope == LeaderboardScope.DAILY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.scope == LeaderboardScope.REAL_TIME:
            return now - timedelta(hours=24)  # Last 24 hours for real-time
        
        return None


class LeaderboardManager:
    """
    Enterprise-grade leaderboard management system.
    
    Manages dynamic rankings, competitive environments, and recognition
    systems across multiple dimensions and time periods.
    """
    
    def __init__(self):
        """Initialize the leaderboard manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._leaderboards: Dict[str, LeaderboardDefinition] = {}
        self._leaderboard_data: Dict[str, List[LeaderboardEntry]] = {}
        self._user_data_cache: Dict[str, Dict[str, Any]] = {}
        self._calculation_lock = asyncio.Lock()
        
        # Initialize default leaderboards
        self._initialize_default_leaderboards()
        
        self.logger.info("LeaderboardManager initialized successfully")
    
    def _initialize_default_leaderboards(self) -> None:
        """Initialize default platform leaderboards."""
        
        # Global Experience Points Leaderboard
        global_xp = LeaderboardDefinition(
            name="Global Experience Leaders",
            description="Top creators by total experience points earned",
            leaderboard_type=LeaderboardType.GLOBAL,
            primary_metric=LeaderboardMetric.EXPERIENCE_POINTS,
            secondary_metrics=[LeaderboardMetric.ACHIEVEMENT_COUNT, LeaderboardMetric.STREAK_DAYS],
            scope=LeaderboardScope.ALL_TIME,
            max_entries=100,
            featured=True,
            top_tier_rewards={
                1: {"virtual_currency": 5000, "badge": "global_champion", "special_benefits": ["champion_status"]},
                2: {"virtual_currency": 3000, "badge": "runner_up", "special_benefits": ["elite_status"]},
                3: {"virtual_currency": 2000, "badge": "top_performer", "special_benefits": ["premium_features"]}
            }
        )
        self._leaderboards[global_xp.leaderboard_id] = global_xp
        
        # Monthly Rising Stars
        monthly_rising = LeaderboardDefinition(
            name="Monthly Rising Stars",
            description="Fastest growing creators this month",
            leaderboard_type=LeaderboardType.GLOBAL,
            primary_metric=LeaderboardMetric.EXPERIENCE_POINTS,
            scope=LeaderboardScope.MONTHLY,
            max_entries=50,
            featured=True,
            top_tier_rewards={
                1: {"virtual_currency": 2000, "badge": "rising_star", "special_benefits": ["boost_package"]},
                2: {"virtual_currency": 1500, "badge": "momentum_builder"},
                3: {"virtual_currency": 1000, "badge": "growth_achiever"}
            }
        )
        self._leaderboards[monthly_rising.leaderboard_id] = monthly_rising
        
        # Quality Masters
        quality_leaders = LeaderboardDefinition(
            name="Quality Masters",
            description="Creators with highest average content quality",
            leaderboard_type=LeaderboardType.CATEGORY,
            primary_metric=LeaderboardMetric.QUALITY_SCORE,
            secondary_metrics=[LeaderboardMetric.CONTENT_COUNT],
            scope=LeaderboardScope.ALL_TIME,
            max_entries=75,
            min_score_threshold=Decimal('85'),
            top_tier_rewards={
                1: {"virtual_currency": 3000, "badge": "quality_master", "special_benefits": ["quality_tools"]},
                2: {"virtual_currency": 2000, "badge": "excellence_achiever"},
                3: {"virtual_currency": 1500, "badge": "quality_champion"}
            }
        )
        self._leaderboards[quality_leaders.leaderboard_id] = quality_leaders
        
        # Collaboration Champions
        collab_champions = LeaderboardDefinition(
            name="Collaboration Champions",
            description="Most successful collaborative creators",
            leaderboard_type=LeaderboardType.COLLABORATION,
            primary_metric=LeaderboardMetric.COLLABORATION_COUNT,
            secondary_metrics=[LeaderboardMetric.COMMUNITY_IMPACT, LeaderboardMetric.GLOBAL_REACH],
            scope=LeaderboardScope.ALL_TIME,
            max_entries=50,
            top_tier_rewards={
                1: {"virtual_currency": 2500, "badge": "collaboration_master", "special_benefits": ["networking_tools"]},
                2: {"virtual_currency": 1800, "badge": "team_leader"},
                3: {"virtual_currency": 1200, "badge": "partnership_pro"}
            }
        )
        self._leaderboards[collab_champions.leaderboard_id] = collab_champions
        
        # Revenue Leaders
        revenue_leaders = LeaderboardDefinition(
            name="Revenue Leaders",
            description="Top earning creators on the platform",
            leaderboard_type=LeaderboardType.GLOBAL,
            primary_metric=LeaderboardMetric.TOTAL_REVENUE,
            secondary_metrics=[LeaderboardMetric.CONTENT_COUNT, LeaderboardMetric.PLATFORM_MASTERY],
            scope=LeaderboardScope.ALL_TIME,
            max_entries=100,
            min_score_threshold=Decimal('100'),
            top_tier_rewards={
                1: {"real_currency": 500, "badge": "revenue_king", "special_benefits": ["premium_analytics"]},
                2: {"real_currency": 300, "badge": "monetization_master"},
                3: {"real_currency": 200, "badge": "earnings_champion"}
            }
        )
        self._leaderboards[revenue_leaders.leaderboard_id] = revenue_leaders
        
        # Weekly Engagement Kings
        weekly_engagement = LeaderboardDefinition(
            name="Weekly Engagement Kings",
            description="Highest engagement rates this week",
            leaderboard_type=LeaderboardType.GLOBAL,
            primary_metric=LeaderboardMetric.ENGAGEMENT_RATE,
            secondary_metrics=[LeaderboardMetric.CONTENT_COUNT],
            scope=LeaderboardScope.WEEKLY,
            max_entries=25,
            min_score_threshold=Decimal('15'),
            real_time_updates=True,
            update_frequency=timedelta(hours=6),
            top_tier_rewards={
                1: {"virtual_currency": 1000, "badge": "engagement_king", "special_benefits": ["engagement_boost"]},
                2: {"virtual_currency": 750, "badge": "audience_master"},
                3: {"virtual_currency": 500, "badge": "connection_pro"}
            }
        )
        self._leaderboards[weekly_engagement.leaderboard_id] = weekly_engagement
        
        # Innovation Pioneers
        innovation_leaders = LeaderboardDefinition(
            name="Innovation Pioneers",
            description="Early adopters and feature innovators",
            leaderboard_type=LeaderboardType.CATEGORY,
            primary_metric=LeaderboardMetric.INNOVATION_SCORE,
            secondary_metrics=[LeaderboardMetric.EXPERIENCE_POINTS],
            scope=LeaderboardScope.ALL_TIME,
            max_entries=30,
            top_tier_rewards={
                1: {"virtual_currency": 2000, "badge": "innovation_pioneer", "special_benefits": ["early_access"]},
                2: {"virtual_currency": 1500, "badge": "feature_explorer"},
                3: {"virtual_currency": 1000, "badge": "tech_adopter"}
            }
        )
        self._leaderboards[innovation_leaders.leaderboard_id] = innovation_leaders
        
        # Creator Type Specific Leaderboards
        creator_types = ["musician", "blogger", "photographer", "influencer", "comedian"]
        for creator_type in creator_types:
            type_leaderboard = LeaderboardDefinition(
                name=f"Top {creator_type.title()}s",
                description=f"Leading {creator_type}s by experience points",
                leaderboard_type=LeaderboardType.CREATOR_TYPE,
                primary_metric=LeaderboardMetric.EXPERIENCE_POINTS,
                secondary_metrics=[LeaderboardMetric.QUALITY_SCORE, LeaderboardMetric.ENGAGEMENT_RATE],
                scope=LeaderboardScope.ALL_TIME,
                creator_type_filter=creator_type,
                max_entries=50,
                top_tier_rewards={
                    1: {"virtual_currency": 1500, "badge": f"{creator_type}_champion"},
                    2: {"virtual_currency": 1000, "badge": f"{creator_type}_master"},
                    3: {"virtual_currency": 750, "badge": f"{creator_type}_expert"}
                }
            )
            self._leaderboards[type_leaderboard.leaderboard_id] = type_leaderboard
        
        # Regional Leaderboards
        regions = ["north_america", "europe", "asia", "south_america", "africa", "oceania"]
        for region in regions:
            regional_leaderboard = LeaderboardDefinition(
                name=f"{region.replace('_', ' ').title()} Leaders",
                description=f"Top creators from {region.replace('_', ' ').title()}",
                leaderboard_type=LeaderboardType.REGIONAL,
                primary_metric=LeaderboardMetric.EXPERIENCE_POINTS,
                secondary_metrics=[LeaderboardMetric.COMMUNITY_IMPACT],
                scope=LeaderboardScope.ALL_TIME,
                region_filter=region,
                max_entries=25,
                top_tier_rewards={
                    1: {"virtual_currency": 1000, "badge": f"{region}_champion"},
                    2: {"virtual_currency": 750, "badge": f"{region}_leader"},
                    3: {"virtual_currency": 500, "badge": f"{region}_star"}
                }
            )
            self._leaderboards[regional_leaderboard.leaderboard_id] = regional_leaderboard
    
    async def update_user_score(
        self,
        user_id: str,
        metric: LeaderboardMetric,
        value: Union[int, float, Decimal],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Update user score for a specific metric and affected leaderboards."""
        try:
            # Cache user profile for performance
            if user_profile:
                self._user_data_cache[user_id] = user_profile
            
            affected_leaderboards = []
            
            # Find leaderboards that use this metric
            for leaderboard_id, leaderboard in self._leaderboards.items():
                if (leaderboard.primary_metric == metric or 
                    metric in leaderboard.secondary_metrics):
                    
                    # Check if user is eligible
                    if user_profile and not leaderboard.is_user_eligible(user_profile):
                        continue
                    
                    # Update leaderboard entry
                    await self._update_leaderboard_entry(leaderboard_id, user_id, metric, value)
                    affected_leaderboards.append(leaderboard_id)
            
            # Trigger recalculation for real-time leaderboards
            for leaderboard_id in affected_leaderboards:
                leaderboard = self._leaderboards[leaderboard_id]
                if leaderboard.real_time_updates:
                    await self._recalculate_leaderboard_rankings(leaderboard_id)
            
            return affected_leaderboards
            
        except Exception as e:
            self.logger.error(f"Error updating user score: {e}")
            return []
    
    async def _update_leaderboard_entry(
        self,
        leaderboard_id: str,
        user_id: str,
        metric: LeaderboardMetric,
        value: Union[int, float, Decimal]
    ) -> None:
        """Update a specific entry in a leaderboard."""
        try:
            if leaderboard_id not in self._leaderboard_data:
                self._leaderboard_data[leaderboard_id] = []
            
            # Find existing entry or create new one
            entry = None
            for existing_entry in self._leaderboard_data[leaderboard_id]:
                if existing_entry.user_id == user_id:
                    entry = existing_entry
                    break
            
            if not entry:
                # Create new entry
                user_profile = self._user_data_cache.get(user_id, {})
                entry = LeaderboardEntry(
                    user_id=user_id,
                    leaderboard_id=leaderboard_id,
                    user_display_name=user_profile.get("display_name", f"User {user_id[:8]}"),
                    user_avatar_url=user_profile.get("avatar_url", ""),
                    user_creator_type=user_profile.get("creator_type", ""),
                    user_level=user_profile.get("level", 1),
                    user_badges=user_profile.get("badges", [])
                )
                self._leaderboard_data[leaderboard_id].append(entry)
            
            # Update scores
            leaderboard = self._leaderboards[leaderboard_id]
            
            if metric == leaderboard.primary_metric:
                entry.previous_score = entry.score
                entry.score = Decimal(str(value))
                entry.score_change = entry.score - (entry.previous_score or Decimal('0'))
            else:
                # Update component score
                entry.component_scores[metric.value] = Decimal(str(value))
            
            # Update metadata
            entry.last_updated = datetime.utcnow()
            
            # Calculate momentum and trends
            await self._calculate_entry_momentum(entry)
            
        except Exception as e:
            self.logger.error(f"Error updating leaderboard entry: {e}")
    
    async def _calculate_entry_momentum(self, entry: LeaderboardEntry) -> None:
        """Calculate momentum and trending indicators for an entry."""
        try:
            # Calculate momentum based on recent score changes
            if entry.previous_score and entry.score > entry.previous_score:
                score_increase = float(entry.score - entry.previous_score)
                time_factor = 1.0  # Could be based on time since last update
                entry.momentum_score = score_increase * time_factor
                entry.trending_up = True
            else:
                entry.momentum_score = max(0, entry.momentum_score * 0.9)  # Decay momentum
                entry.trending_up = False
            
            # Calculate consistency score (simplified)
            # This would ideally use historical data
            entry.consistency_score = min(100.0, entry.momentum_score * 0.1)
            
        except Exception as e:
            self.logger.error(f"Error calculating entry momentum: {e}")
    
    async def _recalculate_leaderboard_rankings(self, leaderboard_id: str) -> None:
        """Recalculate rankings for a specific leaderboard."""
        async with self._calculation_lock:
            try:
                if leaderboard_id not in self._leaderboard_data:
                    return
                
                leaderboard = self._leaderboards[leaderboard_id]
                entries = self._leaderboard_data[leaderboard_id]
                
                # Calculate composite scores if needed
                for entry in entries:
                    if leaderboard.composite_weights:
                        composite_score = await self._calculate_composite_score(entry, leaderboard)
                        entry.score = composite_score
                
                # Sort entries by score (descending)
                entries.sort(key=lambda e: e.score, reverse=True)
                
                # Update rankings
                for i, entry in enumerate(entries):
                    new_rank = i + 1
                    entry.previous_rank = entry.current_rank
                    entry.current_rank = new_rank
                    entry.rank_change = (entry.previous_rank or new_rank) - new_rank
                
                # Apply max entries limit
                if len(entries) > leaderboard.max_entries:
                    self._leaderboard_data[leaderboard_id] = entries[:leaderboard.max_entries]
                
                # Update leaderboard metadata
                leaderboard.last_calculation = datetime.utcnow()
                leaderboard.active_participants = len([e for e in entries if e.score > 0])
                
                self.logger.debug(f"Recalculated rankings for leaderboard {leaderboard.name}")
                
            except Exception as e:
                self.logger.error(f"Error recalculating leaderboard rankings: {e}")
    
    async def _calculate_composite_score(
        self,
        entry: LeaderboardEntry,
        leaderboard: LeaderboardDefinition
    ) -> Decimal:
        """Calculate composite score based on weighted metrics."""
        try:
            composite_score = Decimal('0')
            
            # Primary metric weight (default to 1.0 if not specified)
            primary_weight = leaderboard.composite_weights.get(
                leaderboard.primary_metric.value, 1.0
            )
            composite_score += entry.score * Decimal(str(primary_weight))
            
            # Secondary metrics
            for metric in leaderboard.secondary_metrics:
                weight = leaderboard.composite_weights.get(metric.value, 0.1)
                component_score = entry.component_scores.get(metric.value, Decimal('0'))
                composite_score += component_score * Decimal(str(weight))
            
            return composite_score
            
        except Exception as e:
            self.logger.error(f"Error calculating composite score: {e}")
            return entry.score
    
    async def get_leaderboard(
        self,
        leaderboard_id: str,
        limit: int = 50,
        offset: int = 0,
        include_user_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get leaderboard data with optional user context."""
        try:
            if leaderboard_id not in self._leaderboards:
                raise ValueError(f"Leaderboard {leaderboard_id} not found")
            
            leaderboard = self._leaderboards[leaderboard_id]
            
            # Ensure rankings are up to date
            if not leaderboard.real_time_updates:
                last_calc = leaderboard.last_calculation
                if (not last_calc or 
                    datetime.utcnow() - last_calc > leaderboard.update_frequency):
                    await self._recalculate_leaderboard_rankings(leaderboard_id)
            
            entries = self._leaderboard_data.get(leaderboard_id, [])
            
            # Apply pagination
            total_entries = len(entries)
            paginated_entries = entries[offset:offset + limit]
            
            # Convert to serializable format
            leaderboard_data = {
                "leaderboard_id": leaderboard_id,
                "name": leaderboard.name,
                "description": leaderboard.description,
                "type": leaderboard.leaderboard_type.value,
                "primary_metric": leaderboard.primary_metric.value,
                "scope": leaderboard.scope.value,
                "last_updated": leaderboard.last_calculation.isoformat() if leaderboard.last_calculation else None,
                "total_participants": total_entries,
                "entries": []
            }
            
            for entry in paginated_entries:
                entry_data = {
                    "rank": entry.current_rank,
                    "user_id": entry.user_id,
                    "display_name": entry.user_display_name,
                    "avatar_url": entry.user_avatar_url,
                    "creator_type": entry.user_creator_type,
                    "level": entry.user_level,
                    "badges": entry.user_badges,
                    "score": float(entry.score),
                    "score_display": self._format_score(entry.score, leaderboard.primary_metric),
                    "rank_change": entry.rank_change,
                    "rank_change_indicator": entry.get_rank_change_indicator(),
                    "trending": entry.trending_up,
                    "momentum_score": entry.momentum_score,
                    "last_updated": entry.last_updated.isoformat()
                }
                
                # Add component scores for composite leaderboards
                if leaderboard.composite_weights and entry.component_scores:
                    entry_data["component_scores"] = {
                        k: float(v) for k, v in entry.component_scores.items()
                    }
                
                leaderboard_data["entries"].append(entry_data)
            
            # Add user context if requested
            if include_user_context:
                user_entry = await self._get_user_position(leaderboard_id, include_user_context)
                if user_entry:
                    leaderboard_data["user_context"] = {
                        "user_rank": user_entry.current_rank,
                        "user_score": float(user_entry.score),
                        "rank_change": user_entry.rank_change,
                        "percentile": self._calculate_percentile(user_entry.current_rank, total_entries)
                    }
            
            # Add metadata
            leaderboard_data["pagination"] = {
                "limit": limit,
                "offset": offset,
                "total": total_entries,
                "has_more": offset + limit < total_entries
            }
            
            return leaderboard_data
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return {}
    
    def _format_score(self, score: Decimal, metric: LeaderboardMetric) -> str:
        """Format score for display based on metric type."""
        if metric == LeaderboardMetric.TOTAL_REVENUE:
            return f"${float(score):,.2f}"
        elif metric == LeaderboardMetric.ENGAGEMENT_RATE:
            return f"{float(score):.1f}%"
        elif metric == LeaderboardMetric.QUALITY_SCORE:
            return f"{float(score):.1f}/100"
        elif metric in [LeaderboardMetric.EXPERIENCE_POINTS, LeaderboardMetric.CONTENT_COUNT]:
            return f"{int(score):,}"
        else:
            return f"{float(score):,.1f}"
    
    def _calculate_percentile(self, rank: int, total: int) -> float:
        """Calculate percentile for a given rank."""
        if total == 0:
            return 0.0
        return ((total - rank + 1) / total) * 100
    
    async def _get_user_position(
        self,
        leaderboard_id: str,
        user_id: str
    ) -> Optional[LeaderboardEntry]:
        """Get a user's position in a specific leaderboard."""
        entries = self._leaderboard_data.get(leaderboard_id, [])
        
        for entry in entries:
            if entry.user_id == user_id:
                return entry
        
        return None
    
    async def get_user_leaderboard_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's performance across all leaderboards."""
        try:
            summary = {
                "user_id": user_id,
                "total_leaderboards": 0,
                "top_10_positions": 0,
                "top_100_positions": 0,
                "featured_positions": [],
                "best_ranks": {},
                "recent_improvements": [],
                "total_rewards_available": {
                    "virtual_currency": 0,
                    "real_currency": 0.0,
                    "badges": [],
                    "special_benefits": []
                }
            }
            
            for leaderboard_id, leaderboard in self._leaderboards.items():
                user_entry = await self._get_user_position(leaderboard_id, user_id)
                
                if user_entry:
                    summary["total_leaderboards"] += 1
                    
                    # Count top positions
                    if user_entry.current_rank <= 10:
                        summary["top_10_positions"] += 1
                    if user_entry.current_rank <= 100:
                        summary["top_100_positions"] += 1
                    
                    # Track best ranks by category
                    category = leaderboard.leaderboard_type.value
                    if (category not in summary["best_ranks"] or
                        user_entry.current_rank < summary["best_ranks"][category]["rank"]):
                        summary["best_ranks"][category] = {
                            "leaderboard_name": leaderboard.name,
                            "rank": user_entry.current_rank,
                            "score": float(user_entry.score)
                        }
                    
                    # Featured leaderboard positions
                    if leaderboard.featured and user_entry.current_rank <= 25:
                        summary["featured_positions"].append({
                            "leaderboard_name": leaderboard.name,
                            "rank": user_entry.current_rank,
                            "score": float(user_entry.score),
                            "rank_change": user_entry.rank_change
                        })
                    
                    # Recent improvements
                    if user_entry.rank_change > 0:
                        summary["recent_improvements"].append({
                            "leaderboard_name": leaderboard.name,
                            "rank_improvement": user_entry.rank_change,
                            "current_rank": user_entry.current_rank
                        })
                    
                    # Calculate available rewards
                    for rank, rewards in leaderboard.top_tier_rewards.items():
                        if user_entry.current_rank <= rank:
                            if "virtual_currency" in rewards:
                                summary["total_rewards_available"]["virtual_currency"] += rewards["virtual_currency"]
                            if "real_currency" in rewards:
                                summary["total_rewards_available"]["real_currency"] += rewards["real_currency"]
                            if "badge" in rewards and rewards["badge"] not in summary["total_rewards_available"]["badges"]:
                                summary["total_rewards_available"]["badges"].append(rewards["badge"])
                            if "special_benefits" in rewards:
                                for benefit in rewards["special_benefits"]:
                                    if benefit not in summary["total_rewards_available"]["special_benefits"]:
                                        summary["total_rewards_available"]["special_benefits"].append(benefit)
            
            # Sort featured positions by rank
            summary["featured_positions"].sort(key=lambda x: x["rank"])
            
            # Sort recent improvements by improvement amount
            summary["recent_improvements"].sort(key=lambda x: x["rank_improvement"], reverse=True)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting user leaderboard summary: {e}")
            return {}
    
    async def get_available_leaderboards(
        self,
        user_profile: Optional[Dict[str, Any]] = None,
        featured_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get list of available leaderboards, optionally filtered by user eligibility."""
        try:
            leaderboards = []
            
            for leaderboard_id, leaderboard in self._leaderboards.items():
                # Check if leaderboard is active
                if leaderboard.status != LeaderboardStatus.ACTIVE:
                    continue
                
                # Check featured filter
                if featured_only and not leaderboard.featured:
                    continue
                
                # Check user eligibility
                if user_profile and not leaderboard.is_user_eligible(user_profile):
                    continue
                
                leaderboard_info = {
                    "leaderboard_id": leaderboard_id,
                    "name": leaderboard.name,
                    "description": leaderboard.description,
                    "type": leaderboard.leaderboard_type.value,
                    "primary_metric": leaderboard.primary_metric.value,
                    "scope": leaderboard.scope.value,
                    "max_entries": leaderboard.max_entries,
                    "featured": leaderboard.featured,
                    "public": leaderboard.public,
                    "total_participants": leaderboard.total_participants,
                    "last_updated": leaderboard.last_calculation.isoformat() if leaderboard.last_calculation else None,
                    "top_rewards": leaderboard.top_tier_rewards
                }
                
                # Add user-specific information if profile provided
                if user_profile:
                    user_entry = await self._get_user_position(leaderboard_id, user_profile.get("user_id"))
                    if user_entry:
                        leaderboard_info["user_rank"] = user_entry.current_rank
                        leaderboard_info["user_score"] = float(user_entry.score)
                        leaderboard_info["user_eligible_for_rewards"] = any(
                            user_entry.current_rank <= rank 
                            for rank in leaderboard.top_tier_rewards.keys()
                        )
                
                leaderboards.append(leaderboard_info)
            
            # Sort by featured status, then by participant count
            leaderboards.sort(key=lambda x: (not x["featured"], -x["total_participants"]))
            
            return leaderboards
            
        except Exception as e:
            self.logger.error(f"Error getting available leaderboards: {e}")
            return []
    
    async def create_custom_leaderboard(
        self,
        leaderboard_config: Dict[str, Any],
        creator_id: str
    ) -> str:
        """Create a custom leaderboard."""
        try:
            # Validate required fields
            required_fields = ["name", "primary_metric"]
            for field in required_fields:
                if field not in leaderboard_config:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create leaderboard definition
            leaderboard = LeaderboardDefinition(
                name=leaderboard_config["name"],
                description=leaderboard_config.get("description", ""),
                leaderboard_type=LeaderboardType(leaderboard_config.get("type", "custom")),
                primary_metric=LeaderboardMetric(leaderboard_config["primary_metric"]),
                secondary_metrics=[
                    LeaderboardMetric(m) for m in leaderboard_config.get("secondary_metrics", [])
                ],
                scope=LeaderboardScope(leaderboard_config.get("scope", "all_time")),
                creator_type_filter=leaderboard_config.get("creator_type_filter"),
                region_filter=leaderboard_config.get("region_filter"),
                platform_filter=leaderboard_config.get("platform_filter"),
                skill_level_filter=leaderboard_config.get("skill_level_filter"),
                custom_filters=leaderboard_config.get("custom_filters", {}),
                max_entries=leaderboard_config.get("max_entries", 100),
                min_score_threshold=Decimal(str(leaderboard_config["min_score_threshold"])) if "min_score_threshold" in leaderboard_config else None,
                composite_weights=leaderboard_config.get("composite_weights", {}),
                update_frequency=timedelta(minutes=leaderboard_config.get("update_frequency_minutes", 30)),
                real_time_updates=leaderboard_config.get("real_time_updates", False),
                top_tier_rewards=leaderboard_config.get("top_tier_rewards", {}),
                participation_rewards=leaderboard_config.get("participation_rewards", {}),
                milestone_rewards=leaderboard_config.get("milestone_rewards", {}),
                public=leaderboard_config.get("public", True),
                featured=leaderboard_config.get("featured", False),
                requires_opt_in=leaderboard_config.get("requires_opt_in", False),
                created_by=creator_id
            )
            
            # Store leaderboard
            self._leaderboards[leaderboard.leaderboard_id] = leaderboard
            self._leaderboard_data[leaderboard.leaderboard_id] = []
            
            self.logger.info(f"Created custom leaderboard: {leaderboard.name} by {creator_id}")
            
            return leaderboard.leaderboard_id
            
        except Exception as e:
            self.logger.error(f"Error creating custom leaderboard: {e}")
            raise
    
    async def schedule_leaderboard_updates(self) -> None:
        """Schedule regular leaderboard updates."""
        try:
            for leaderboard_id, leaderboard in self._leaderboards.items():
                if leaderboard.status == LeaderboardStatus.ACTIVE and not leaderboard.real_time_updates:
                    last_calc = leaderboard.last_calculation
                    
                    if (not last_calc or 
                        datetime.utcnow() - last_calc >= leaderboard.update_frequency):
                        await self._recalculate_leaderboard_rankings(leaderboard_id)
            
            self.logger.debug("Completed scheduled leaderboard updates")
            
        except Exception as e:
            self.logger.error(f"Error in scheduled leaderboard updates: {e}")
    
    async def get_leaderboard_analytics(self, leaderboard_id: str) -> Dict[str, Any]:
        """Get analytics data for a specific leaderboard."""
        try:
            if leaderboard_id not in self._leaderboards:
                raise ValueError(f"Leaderboard {leaderboard_id} not found")
            
            leaderboard = self._leaderboards[leaderboard_id]
            entries = self._leaderboard_data.get(leaderboard_id, [])
            
            if not entries:
                return {"message": "No data available for analytics"}
            
            # Calculate statistics
            scores = [float(entry.score) for entry in entries]
            
            analytics = {
                "leaderboard_id": leaderboard_id,
                "name": leaderboard.name,
                "total_participants": len(entries),
                "score_statistics": {
                    "min_score": min(scores) if scores else 0,
                    "max_score": max(scores) if scores else 0,
                    "average_score": sum(scores) / len(scores) if scores else 0,
                    "median_score": sorted(scores)[len(scores) // 2] if scores else 0
                },
                "participation_trends": {
                    "total_participants": leaderboard.total_participants,
                    "active_participants": leaderboard.active_participants,
                    "participation_rate": (leaderboard.active_participants / leaderboard.total_participants * 100) if leaderboard.total_participants > 0 else 0
                },
                "top_performers": [
                    {
                        "rank": entry.current_rank,
                        "user_id": entry.user_id,
                        "display_name": entry.user_display_name,
                        "score": float(entry.score),
                        "trending": entry.trending_up
                    }
                    for entry in entries[:10]
                ],
                "recent_activity": {
                    "entries_with_recent_updates": len([
                        e for e in entries 
                        if (datetime.utcnow() - e.last_updated).days <= 7
                    ]),
                    "trending_users": len([e for e in entries if e.trending_up])
                }
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboard analytics: {e}")
            return {}


# Global leaderboard manager instance
_leaderboard_manager: Optional[LeaderboardManager] = None


async def get_leaderboard_manager() -> LeaderboardManager:
    """Get the global leaderboard manager instance."""
    global _leaderboard_manager
    
    if _leaderboard_manager is None:
        _leaderboard_manager = LeaderboardManager()
    
    return _leaderboard_manager


# Convenience functions for common operations
async def update_user_metric_score(
    user_id: str,
    metric: LeaderboardMetric,
    value: Union[int, float, Decimal],
    user_profile: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Update user metric score (convenience function)."""
    manager = await get_leaderboard_manager()
    return await manager.update_user_score(user_id, metric, value, user_profile)


async def get_global_leaderboard(limit: int = 50, user_context: Optional[str] = None) -> Dict[str, Any]:
    """Get the main global leaderboard (convenience function)."""
    manager = await get_leaderboard_manager()
    
    # Find the global experience points leaderboard
    for leaderboard_id, leaderboard in manager._leaderboards.items():
        if (leaderboard.leaderboard_type == LeaderboardType.GLOBAL and 
            leaderboard.primary_metric == LeaderboardMetric.EXPERIENCE_POINTS and
            leaderboard.scope == LeaderboardScope.ALL_TIME):
            return await manager.get_leaderboard(leaderboard_id, limit, 0, user_context)
    
    return {}


async def get_user_rankings(user_id: str) -> Dict[str, Any]:
    """Get user's rankings across all leaderboards (convenience function)."""
    manager = await get_leaderboard_manager()
    return await manager.get_user_leaderboard_summary(user_id)