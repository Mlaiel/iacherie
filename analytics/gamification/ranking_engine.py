"""Unified Ranking Engine - Enterprise Ranking & Leaderboard System
=====================================================================

Comprehensive unified ranking system combining platform rankings
and competitive gaming leaderboards with sophisticated scoring algorithms,
tier management, and tournament mechanics.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/gamification/ranking_engine.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

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
Ranking Calculation → Gaming Leaderboards → Distribution → Monetization → Analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import math
from statistics import mean, median
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================================
# UNIFIED RANKING ENUMS AND TYPES
# ============================================================================

class UserTier(str, Enum):
    """Unified user tier levels."""
    NEWCOMER = "newcomer"
    RISING = "rising"
    SKILLED = "skilled"
    EXPERT = "expert"
    MASTER = "master"
    LEGEND = "legend"
    CHAMPION = "champion"


class CompetitiveRank(str, Enum):
    """Gaming competitive ranking tiers."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    LEGEND = "legend"


class RankingCategory(str, Enum):
    """Unified ranking categories."""
    # Platform Categories
    OVERALL = "overall"
    CONTENT_QUALITY = "content_quality"
    ENGAGEMENT = "engagement"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    INNOVATION = "innovation"
    COMMUNITY = "community"
    
    # Gaming Categories
    GLOBAL_WEALTH = "global_wealth"
    GLOBAL_LEVEL = "global_level"
    GLOBAL_ACHIEVEMENTS = "global_achievements"
    SPEED_RUNNERS = "speed_runners"
    EFFICIENCY_MASTERS = "efficiency_masters"
    COMPETITIVE_RANKING = "competitive_ranking"
    WEEKLY_INCOME = "weekly_income"
    MONTHLY_GROWTH = "monthly_growth"
    SEASONAL_CHAMPIONS = "seasonal_champions"
    TOURNAMENT_BRACKET = "tournament_bracket"


class RankingPeriod(str, Enum):
    """Ranking time periods."""
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"
    SEASONAL = "seasonal"


class LeaderboardType(str, Enum):
    """Types of leaderboards."""
    PLATFORM_RANKING = "platform_ranking"
    GAMING_LEADERBOARD = "gaming_leaderboard"
    COMPETITIVE_LADDER = "competitive_ladder"
    TOURNAMENT_BRACKET = "tournament_bracket"
    SEASONAL_RANKING = "seasonal_ranking"
    GUILD_RANKING = "guild_ranking"


class TournamentStatus(str, Enum):
    """Tournament status types."""
    UPCOMING = "upcoming"
    REGISTRATION_OPEN = "registration_open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TournamentFormat(str, Enum):
    """Tournament format types."""
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS_SYSTEM = "swiss_system"
    LADDER = "ladder"
    BATTLE_ROYALE = "battle_royale"


# ============================================================================
# UNIFIED DATA STRUCTURES
# ============================================================================

@dataclass
class ScoreComponent:
    """Individual score component for ranking calculations."""
    name: str
    value: float
    weight: float
    max_value: Optional[float] = None
    normalization_method: str = "linear"  # linear, logarithmic, exponential
    decay_factor: float = 1.0  # For time-based decay
    is_gaming_metric: bool = False


@dataclass
class RankEntry:
    """Unified ranking entry for both platform and gaming."""
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    username: str = ""
    display_name: str = ""
    avatar_url: Optional[str] = None
    
    # Ranking data
    rank: int = 0
    previous_rank: Optional[int] = None
    score: Decimal = Decimal('0')
    secondary_scores: Dict[str, Decimal] = field(default_factory=dict)
    
    # Tier information
    tier: UserTier = UserTier.NEWCOMER
    competitive_rank: Optional[CompetitiveRank] = None
    tier_progress: float = 0.0  # Progress to next tier (0-100%)
    
    # Performance metrics
    percentile: float = 0.0
    score_change: Decimal = Decimal('0')
    rank_change: int = 0
    win_rate: Optional[float] = None
    
    # Gaming-specific
    is_gaming_entry: bool = False
    gaming_level: Optional[int] = None
    gaming_stats: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Leaderboard:
    """Unified leaderboard structure."""
    leaderboard_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    leaderboard_type: LeaderboardType = LeaderboardType.PLATFORM_RANKING
    category: RankingCategory = RankingCategory.OVERALL
    period: RankingPeriod = RankingPeriod.ALL_TIME
    
    # Configuration
    max_entries: int = 1000
    update_frequency: int = 300  # seconds
    scoring_algorithm: str = "weighted_sum"
    is_gaming_leaderboard: bool = False
    
    # Entries
    entries: List[RankEntry] = field(default_factory=list)
    
    # Tournament data (if applicable)
    tournament_id: Optional[str] = None
    tournament_status: Optional[TournamentStatus] = None
    tournament_format: Optional[TournamentFormat] = None
    
    # Timing
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Settings
    is_active: bool = True
    is_public: bool = True
    reward_pool: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tournament:
    """Tournament structure for competitive gaming."""
    tournament_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    tournament_format: TournamentFormat = TournamentFormat.SINGLE_ELIMINATION
    status: TournamentStatus = TournamentStatus.UPCOMING
    
    # Participants
    registered_players: List[str] = field(default_factory=list)
    max_participants: int = 64
    min_participants: int = 8
    
    # Schedule
    registration_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    registration_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7))
    tournament_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7))
    tournament_end: Optional[datetime] = None
    
    # Prizes
    prize_pool: Dict[str, Any] = field(default_factory=dict)
    entry_fee: Optional[Decimal] = None
    
    # Results
    brackets: Dict[str, Any] = field(default_factory=dict)
    winners: List[str] = field(default_factory=list)
    
    # Settings
    category: RankingCategory = RankingCategory.COMPETITIVE_RANKING
    skill_based_matching: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# UNIFIED RANKING ENGINE
# ============================================================================

class UnifiedRankingEngine:
    """
    Unified ranking engine combining platform rankings and competitive
    gaming leaderboards with sophisticated scoring and tier management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.leaderboards: Dict[str, Leaderboard] = {}
        self.tournaments: Dict[str, Tournament] = {}
        self.user_rankings: Dict[str, Dict[str, RankEntry]] = {}
        self.score_components: Dict[str, List[ScoreComponent]] = {}
        self.tier_thresholds: Dict[UserTier, float] = {}
        self.competitive_thresholds: Dict[CompetitiveRank, float] = {}
        
        self._initialize_ranking_system()
        logger.info("🏆 Unified Ranking Engine initialized")
    
    def _initialize_ranking_system(self):
        """Initialize ranking system with default configurations."""
        
        # Initialize tier thresholds
        self.tier_thresholds = {
            UserTier.NEWCOMER: 0.0,
            UserTier.RISING: 1000.0,
            UserTier.SKILLED: 5000.0,
            UserTier.EXPERT: 15000.0,
            UserTier.MASTER: 35000.0,
            UserTier.LEGEND: 75000.0,
            UserTier.CHAMPION: 150000.0,
        }
        
        # Initialize competitive ranking thresholds
        self.competitive_thresholds = {
            CompetitiveRank.BRONZE: 0.0,
            CompetitiveRank.SILVER: 1500.0,
            CompetitiveRank.GOLD: 3000.0,
            CompetitiveRank.PLATINUM: 5000.0,
            CompetitiveRank.DIAMOND: 8000.0,
            CompetitiveRank.MASTER: 12000.0,
            CompetitiveRank.GRANDMASTER: 18000.0,
            CompetitiveRank.LEGEND: 25000.0,
        }
        
        # Initialize default leaderboards
        self._create_default_leaderboards()
        
        # Initialize score components
        self._initialize_score_components()
    
    def _create_default_leaderboards(self):
        """Create default platform and gaming leaderboards."""
        
        # Platform leaderboards
        platform_boards = [
            ("overall_ranking", "Overall Creator Ranking", RankingCategory.OVERALL),
            ("content_quality", "Content Quality Leaders", RankingCategory.CONTENT_QUALITY),
            ("engagement_masters", "Engagement Champions", RankingCategory.ENGAGEMENT),
            ("collaboration_kings", "Collaboration Masters", RankingCategory.COLLABORATION),
        ]
        
        for board_id, name, category in platform_boards:
            leaderboard = Leaderboard(
                leaderboard_id=board_id,
                name=name,
                category=category,
                leaderboard_type=LeaderboardType.PLATFORM_RANKING,
                is_gaming_leaderboard=False
            )
            self.leaderboards[board_id] = leaderboard
        
        # Gaming leaderboards
        gaming_boards = [
            ("wealth_leaders", "Wealth Leaderboard", RankingCategory.GLOBAL_WEALTH),
            ("level_masters", "Level Champions", RankingCategory.GLOBAL_LEVEL),
            ("achievement_hunters", "Achievement Leaders", RankingCategory.GLOBAL_ACHIEVEMENTS),
            ("speed_demons", "Speed Run Champions", RankingCategory.SPEED_RUNNERS),
            ("efficiency_experts", "Efficiency Masters", RankingCategory.EFFICIENCY_MASTERS),
        ]
        
        for board_id, name, category in gaming_boards:
            leaderboard = Leaderboard(
                leaderboard_id=board_id,
                name=name,
                category=category,
                leaderboard_type=LeaderboardType.GAMING_LEADERBOARD,
                is_gaming_leaderboard=True
            )
            self.leaderboards[board_id] = leaderboard
    
    def _initialize_score_components(self):
        """Initialize scoring components for different categories."""
        
        # Platform score components
        self.score_components[RankingCategory.OVERALL.value] = [
            ScoreComponent("content_uploads", 0, 0.2, normalization_method="logarithmic"),
            ScoreComponent("total_views", 0, 0.25, normalization_method="logarithmic"),
            ScoreComponent("engagement_rate", 0, 0.2, max_value=100),
            ScoreComponent("collaboration_score", 0, 0.15),
            ScoreComponent("quality_score", 0, 0.2, max_value=100),
        ]
        
        self.score_components[RankingCategory.CONTENT_QUALITY.value] = [
            ScoreComponent("average_quality_score", 0, 0.4, max_value=100),
            ScoreComponent("consistency_score", 0, 0.3, max_value=100),
            ScoreComponent("innovation_score", 0, 0.3, max_value=100),
        ]
        
        # Gaming score components
        self.score_components[RankingCategory.GLOBAL_WEALTH.value] = [
            ScoreComponent("total_cash", 0, 0.5, normalization_method="logarithmic", is_gaming_metric=True),
            ScoreComponent("net_worth", 0, 0.3, normalization_method="logarithmic", is_gaming_metric=True),
            ScoreComponent("passive_income", 0, 0.2, normalization_method="logarithmic", is_gaming_metric=True),
        ]
        
        self.score_components[RankingCategory.GLOBAL_LEVEL.value] = [
            ScoreComponent("player_level", 0, 0.6, is_gaming_metric=True),
            ScoreComponent("experience_points", 0, 0.25, normalization_method="logarithmic", is_gaming_metric=True),
            ScoreComponent("prestige_points", 0, 0.15, is_gaming_metric=True),
        ]
    
    async def calculate_user_score(self, user_id: str, category: RankingCategory, 
                                 user_metrics: Dict[str, Any]) -> float:
        """Calculate user score for a specific category."""
        try:
            components = self.score_components.get(category.value, [])
            if not components:
                return 0.0
            
            total_score = 0.0
            total_weight = sum(comp.weight for comp in components)
            
            for component in components:
                raw_value = user_metrics.get(component.name, 0)
                normalized_value = self._normalize_value(raw_value, component)
                weighted_score = normalized_value * component.weight
                total_score += weighted_score
            
            # Normalize to 0-100 scale if needed
            if total_weight > 0:
                final_score = (total_score / total_weight) * 100
            else:
                final_score = 0.0
            
            return max(0.0, min(100.0, final_score))
            
        except Exception as e:
            logger.error(f"Error calculating user score: {e}")
            return 0.0
    
    def _normalize_value(self, value: float, component: ScoreComponent) -> float:
        """Normalize a metric value based on the component configuration."""
        try:
            if component.normalization_method == "logarithmic":
                normalized = math.log(max(1, value))
            elif component.normalization_method == "exponential":
                normalized = math.pow(value, 0.5)  # Square root
            else:  # linear
                normalized = float(value)
            
            # Apply max value constraints
            if component.max_value:
                normalized = min(normalized, component.max_value)
            
            # Apply decay factor
            normalized *= component.decay_factor
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing value: {e}")
            return 0.0
    
    async def update_user_ranking(self, user_id: str, user_metrics: Dict[str, Any],
                                 is_gaming_update: bool = False) -> Dict[str, Any]:
        """Update user rankings across all relevant leaderboards."""
        try:
            updated_rankings = {}
            
            # Initialize user rankings if needed
            if user_id not in self.user_rankings:
                self.user_rankings[user_id] = {}
            
            # Update rankings for each leaderboard
            for leaderboard_id, leaderboard in self.leaderboards.items():
                
                # Skip if leaderboard type doesn't match update type
                if leaderboard.is_gaming_leaderboard != is_gaming_update:
                    continue
                
                # Calculate score for this category
                score = await self.calculate_user_score(
                    user_id, leaderboard.category, user_metrics
                )
                
                # Get or create rank entry
                existing_entry = next(
                    (entry for entry in leaderboard.entries if entry.user_id == user_id),
                    None
                )
                
                if existing_entry:
                    # Update existing entry
                    existing_entry.previous_rank = existing_entry.rank
                    existing_entry.score_change = Decimal(str(score)) - existing_entry.score
                    existing_entry.score = Decimal(str(score))
                    existing_entry.last_updated = datetime.now(timezone.utc)
                    
                    # Update gaming-specific data
                    if is_gaming_update:
                        existing_entry.gaming_level = user_metrics.get('level')
                        existing_entry.gaming_stats = {
                            'total_cash': user_metrics.get('total_cash', 0),
                            'assets_owned': user_metrics.get('assets_owned', 0),
                            'prestige_points': user_metrics.get('prestige_points', 0)
                        }
                    
                    rank_entry = existing_entry
                else:
                    # Create new entry
                    rank_entry = RankEntry(
                        user_id=user_id,
                        username=user_metrics.get('username', ''),
                        display_name=user_metrics.get('display_name', ''),
                        score=Decimal(str(score)),
                        is_gaming_entry=is_gaming_update
                    )
                    
                    if is_gaming_update:
                        rank_entry.gaming_level = user_metrics.get('level')
                        rank_entry.gaming_stats = {
                            'total_cash': user_metrics.get('total_cash', 0),
                            'assets_owned': user_metrics.get('assets_owned', 0),
                            'prestige_points': user_metrics.get('prestige_points', 0)
                        }
                    
                    leaderboard.entries.append(rank_entry)
                
                # Update tier
                rank_entry.tier = self._calculate_user_tier(float(rank_entry.score))
                rank_entry.tier_progress = self._calculate_tier_progress(rank_entry.tier, float(rank_entry.score))
                
                # Update competitive rank for gaming entries
                if is_gaming_update:
                    rank_entry.competitive_rank = self._calculate_competitive_rank(float(rank_entry.score))
                
                # Store in user rankings
                self.user_rankings[user_id][leaderboard_id] = rank_entry
                updated_rankings[leaderboard_id] = rank_entry
            
            # Recalculate positions for updated leaderboards
            await self._recalculate_leaderboard_positions(updated_rankings.keys())
            
            return {
                "success": True,
                "updated_rankings": len(updated_rankings),
                "rankings": updated_rankings
            }
            
        except Exception as e:
            logger.error(f"Error updating user ranking: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_user_tier(self, score: float) -> UserTier:
        """Calculate user tier based on score."""
        for tier in reversed(list(UserTier)):
            if score >= self.tier_thresholds[tier]:
                return tier
        return UserTier.NEWCOMER
    
    def _calculate_tier_progress(self, current_tier: UserTier, score: float) -> float:
        """Calculate progress to next tier."""
        try:
            tiers = list(UserTier)
            current_index = tiers.index(current_tier)
            
            if current_index >= len(tiers) - 1:
                return 100.0  # Already at max tier
            
            current_threshold = self.tier_thresholds[current_tier]
            next_tier = tiers[current_index + 1]
            next_threshold = self.tier_thresholds[next_tier]
            
            progress = (score - current_threshold) / (next_threshold - current_threshold)
            return max(0.0, min(100.0, progress * 100))
            
        except Exception as e:
            logger.error(f"Error calculating tier progress: {e}")
            return 0.0
    
    def _calculate_competitive_rank(self, score: float) -> CompetitiveRank:
        """Calculate competitive rank for gaming entries."""
        for rank in reversed(list(CompetitiveRank)):
            if score >= self.competitive_thresholds[rank]:
                return rank
        return CompetitiveRank.BRONZE
    
    async def _recalculate_leaderboard_positions(self, leaderboard_ids: List[str]):
        """Recalculate positions for specified leaderboards."""
        try:
            for leaderboard_id in leaderboard_ids:
                leaderboard = self.leaderboards.get(leaderboard_id)
                if not leaderboard:
                    continue
                
                # Sort entries by score (descending)
                leaderboard.entries.sort(key=lambda x: float(x.score), reverse=True)
                
                # Update positions and percentiles
                total_entries = len(leaderboard.entries)
                for i, entry in enumerate(leaderboard.entries):
                    new_rank = i + 1
                    entry.rank_change = (entry.previous_rank or new_rank) - new_rank
                    entry.rank = new_rank
                    entry.percentile = ((total_entries - i) / total_entries) * 100 if total_entries > 0 else 0
                
                leaderboard.last_updated = datetime.now(timezone.utc)
                
        except Exception as e:
            logger.error(f"Error recalculating leaderboard positions: {e}")
    
    async def get_leaderboard(self, leaderboard_id: str, limit: int = 100, 
                            offset: int = 0) -> Dict[str, Any]:
        """Get leaderboard with pagination."""
        try:
            leaderboard = self.leaderboards.get(leaderboard_id)
            if not leaderboard:
                return {"error": "Leaderboard not found"}
            
            # Get paginated entries
            end_index = offset + limit
            entries = leaderboard.entries[offset:end_index]
            
            return {
                "leaderboard_id": leaderboard_id,
                "name": leaderboard.name,
                "category": leaderboard.category.value,
                "period": leaderboard.period.value,
                "is_gaming": leaderboard.is_gaming_leaderboard,
                "total_entries": len(leaderboard.entries),
                "entries": entries,
                "last_updated": leaderboard.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return {"error": str(e)}
    
    async def get_user_rankings(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user ranking data."""
        try:
            user_rankings = self.user_rankings.get(user_id, {})
            
            # Separate platform and gaming rankings
            platform_rankings = {}
            gaming_rankings = {}
            
            for leaderboard_id, rank_entry in user_rankings.items():
                leaderboard = self.leaderboards.get(leaderboard_id)
                if not leaderboard:
                    continue
                
                ranking_data = {
                    "leaderboard_name": leaderboard.name,
                    "category": leaderboard.category.value,
                    "rank": rank_entry.rank,
                    "score": float(rank_entry.score),
                    "tier": rank_entry.tier.value,
                    "tier_progress": rank_entry.tier_progress,
                    "percentile": rank_entry.percentile,
                    "rank_change": rank_entry.rank_change
                }
                
                if leaderboard.is_gaming_leaderboard:
                    ranking_data["competitive_rank"] = rank_entry.competitive_rank.value if rank_entry.competitive_rank else None
                    ranking_data["gaming_level"] = rank_entry.gaming_level
                    gaming_rankings[leaderboard_id] = ranking_data
                else:
                    platform_rankings[leaderboard_id] = ranking_data
            
            return {
                "user_id": user_id,
                "platform_rankings": platform_rankings,
                "gaming_rankings": gaming_rankings,
                "total_leaderboards": len(user_rankings)
            }
            
        except Exception as e:
            logger.error(f"Error getting user rankings: {e}")
            return {"error": str(e)}
    
    async def create_tournament(self, tournament_data: Dict[str, Any]) -> Tournament:
        """Create a new tournament."""
        try:
            tournament = Tournament(
                name=tournament_data.get('name', ''),
                description=tournament_data.get('description', ''),
                tournament_format=TournamentFormat(tournament_data.get('format', 'single_elimination')),
                max_participants=tournament_data.get('max_participants', 64),
                min_participants=tournament_data.get('min_participants', 8),
                category=RankingCategory(tournament_data.get('category', 'competitive_ranking'))
            )
            
            # Set tournament schedule
            if 'registration_end' in tournament_data:
                tournament.registration_end = datetime.fromisoformat(tournament_data['registration_end'])
            if 'tournament_start' in tournament_data:
                tournament.tournament_start = datetime.fromisoformat(tournament_data['tournament_start'])
            
            # Set prize pool
            tournament.prize_pool = tournament_data.get('prize_pool', {})
            tournament.entry_fee = Decimal(str(tournament_data.get('entry_fee', 0)))
            
            self.tournaments[tournament.tournament_id] = tournament
            
            # Create tournament leaderboard
            tournament_leaderboard = Leaderboard(
                leaderboard_id=f"tournament_{tournament.tournament_id}",
                name=f"{tournament.name} - Tournament Bracket",
                leaderboard_type=LeaderboardType.TOURNAMENT_BRACKET,
                category=tournament.category,
                tournament_id=tournament.tournament_id,
                tournament_status=tournament.status,
                tournament_format=tournament.tournament_format,
                is_gaming_leaderboard=True
            )
            
            self.leaderboards[tournament_leaderboard.leaderboard_id] = tournament_leaderboard
            
            logger.info(f"🏆 Created tournament: {tournament.name} ({tournament.tournament_id})")
            return tournament
            
        except Exception as e:
            logger.error(f"Error creating tournament: {e}")
            raise


# Global instance
_ranking_engine_instance: Optional[UnifiedRankingEngine] = None


def get_ranking_engine() -> UnifiedRankingEngine:
    """Get the global unified ranking engine instance."""
    global _ranking_engine_instance
    if _ranking_engine_instance is None:
        _ranking_engine_instance = UnifiedRankingEngine()
    return _ranking_engine_instance


async def update_user_ranking(user_id: str, user_metrics: Dict[str, Any], 
                            is_gaming_update: bool = False) -> Dict[str, Any]:
    """Update user rankings across all leaderboards."""
    engine = get_ranking_engine()
    return await engine.update_user_ranking(user_id, user_metrics, is_gaming_update)


async def get_leaderboard(leaderboard_id: str, limit: int = 100) -> Dict[str, Any]:
    """Get leaderboard data."""
    engine = get_ranking_engine()
    return await engine.get_leaderboard(leaderboard_id, limit)
