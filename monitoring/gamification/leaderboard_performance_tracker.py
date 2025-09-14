"""
🎮 MONITORING GAMIFICATION - Leaderboard Performance Tracker
Advanced leaderboard system monitoring and optimization for Ainflue platform
Gaming + Analytics Engineer + Behavioral Psychology Implementation

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from collections import defaultdict, deque
import heapq
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeaderboardType(Enum):
    """Types of leaderboards"""
    GLOBAL_CREATORS = "global_creators"
    CATEGORY_LEADERS = "category_leaders"
    WEEKLY_CHAMPIONS = "weekly_champions"
    MONTHLY_STARS = "monthly_stars"
    RISING_TALENTS = "rising_talents"
    ENGAGEMENT_MASTERS = "engagement_masters"
    COLLABORATION_HEROES = "collaboration_heroes"
    REVENUE_LEADERS = "revenue_leaders"
    COMMUNITY_BUILDERS = "community_builders"
    INNOVATION_PIONEERS = "innovation_pioneers"

class MetricType(Enum):
    """Metrics used for leaderboard ranking"""
    FOLLOWERS_COUNT = "followers_count"
    TOTAL_ENGAGEMENT = "total_engagement"
    CONTENT_QUALITY_SCORE = "content_quality_score"
    COLLABORATION_COUNT = "collaboration_count"
    REVENUE_GENERATED = "revenue_generated"
    COMMUNITY_IMPACT = "community_impact"
    INNOVATION_SCORE = "innovation_score"
    CONSISTENCY_RATING = "consistency_rating"
    GROWTH_RATE = "growth_rate"
    VIRAL_COEFFICIENT = "viral_coefficient"

class RankingAlgorithm(Enum):
    """Ranking algorithms for leaderboards"""
    SIMPLE_SCORE = "simple_score"
    WEIGHTED_COMPOSITE = "weighted_composite"
    ELO_RATING = "elo_rating"
    DECAY_ADJUSTED = "decay_adjusted"
    PERCENTILE_BASED = "percentile_based"
    MACHINE_LEARNING = "machine_learning"

class UpdateFrequency(Enum):
    """Leaderboard update frequencies"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class EngagementPattern(Enum):
    """User engagement patterns with leaderboards"""
    HIGHLY_ENGAGED = "highly_engaged"
    MODERATELY_ENGAGED = "moderately_engaged"
    PASSIVE_VIEWER = "passive_viewer"
    COMPETITIVE_CLIMBER = "competitive_climber"
    CASUAL_OBSERVER = "casual_observer"
    DISENGAGED = "disengaged"

@dataclass
class LeaderboardEntry:
    """Individual leaderboard entry"""
    user_id: str
    username: str
    score: float
    rank: int
    previous_rank: Optional[int]
    metrics: Dict[MetricType, float]
    last_updated: datetime
    rank_change: int = 0
    percentile: float = 0.0
    tier: str = "bronze"

@dataclass
class LeaderboardConfig:
    """Leaderboard configuration"""
    leaderboard_id: str
    name: str
    description: str
    leaderboard_type: LeaderboardType
    primary_metric: MetricType
    secondary_metrics: List[MetricType]
    ranking_algorithm: RankingAlgorithm
    update_frequency: UpdateFrequency
    max_entries: int
    time_window_days: int
    weights: Dict[MetricType, float] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class LeaderboardAnalytics:
    """Leaderboard performance analytics"""
    leaderboard_id: str
    time_period: str
    total_participants: int
    active_participants: int
    average_score: float
    score_distribution: Dict[str, int]
    engagement_metrics: Dict[str, float]
    churn_rate: float
    growth_rate: float
    top_movers: List[str]
    engagement_patterns: Dict[EngagementPattern, int]

@dataclass
class CompetitionEvent:
    """Competition or special event on leaderboard"""
    event_id: str
    name: str
    leaderboard_id: str
    start_date: datetime
    end_date: datetime
    prizes: Dict[str, Any]
    participation_boost: float
    special_rules: Dict[str, Any] = field(default_factory=dict)
    participants: Set[str] = field(default_factory=set)

class LeaderboardPerformanceTracker:
    """
    🎮 Advanced Leaderboard Performance Tracker for Ainflue Platform
    
    Gaming psychology-driven leaderboard optimization with:
    - Multi-algorithm ranking systems with real-time updates
    - Advanced engagement pattern analysis and optimization
    - Psychological motivation tracking and enhancement
    - Cross-leaderboard performance correlation analysis
    - Automated tier and reward system management
    - Competition event orchestration and impact measurement
    - Predictive modeling for user engagement and churn
    - A/B testing framework for leaderboard mechanics
    """
    
    def __init__(self, db_url -> None: str = None, redis_url -> None: str = None) -> None:
        """Initialize leaderboard performance tracker"""
        self.db_url = db_url
        self.redis_url = redis_url
        
        # Data storage
        self.leaderboards: Dict[str, LeaderboardConfig] = {}
        self.leaderboard_data: Dict[str, List[LeaderboardEntry]] = {}
        self.user_engagement_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.analytics_cache: Dict[str, LeaderboardAnalytics] = {}
        
        # Competition and events
        self.active_competitions: Dict[str, CompetitionEvent] = {}
        self.event_impact_metrics: Dict[str, Dict[str, float]] = {}
        
        # Performance tracking
        self.engagement_patterns: Dict[str, EngagementPattern] = {}
        self.motivation_scores: Dict[str, float] = {}
        self.ranking_performance: Dict[str, Dict[str, float]] = {}
        
        # Psychological insights
        self.user_personality_profiles: Dict[str, Dict[str, float]] = {}
        self.optimal_challenge_levels: Dict[str, float] = {}
        
        # Initialize default leaderboards
        asyncio.create_task(self._initialize_default_leaderboards())
        
        logger.info("🎮 Leaderboard Performance Tracker initialized")

    async def _initialize_default_leaderboards(self) -> None:
        """Initialize default leaderboard configurations"""
        try:
            # Global creators leaderboard
            await self.create_leaderboard(
                "global_creators",
                "Global Top Creators",
                "Top creators across all categories",
                LeaderboardType.GLOBAL_CREATORS,
                MetricType.TOTAL_ENGAGEMENT,
                [MetricType.FOLLOWERS_COUNT, MetricType.CONTENT_QUALITY_SCORE],
                RankingAlgorithm.WEIGHTED_COMPOSITE,
                UpdateFrequency.HOURLY,
                max_entries=1000,
                time_window_days=30,
                weights={
                    MetricType.TOTAL_ENGAGEMENT: 0.4,
                    MetricType.FOLLOWERS_COUNT: 0.3,
                    MetricType.CONTENT_QUALITY_SCORE: 0.3
                }
            )
            
            # Weekly champions
            await self.create_leaderboard(
                "weekly_champions",
                "Weekly Champions",
                "Top performers this week",
                LeaderboardType.WEEKLY_CHAMPIONS,
                MetricType.GROWTH_RATE,
                [MetricType.TOTAL_ENGAGEMENT, MetricType.VIRAL_COEFFICIENT],
                RankingAlgorithm.DECAY_ADJUSTED,
                UpdateFrequency.HOURLY,
                max_entries=100,
                time_window_days=7,
                weights={
                    MetricType.GROWTH_RATE: 0.5,
                    MetricType.TOTAL_ENGAGEMENT: 0.3,
                    MetricType.VIRAL_COEFFICIENT: 0.2
                }
            )
            
            # Rising talents
            await self.create_leaderboard(
                "rising_talents",
                "Rising Talents",
                "Fast-growing new creators",
                LeaderboardType.RISING_TALENTS,
                MetricType.GROWTH_RATE,
                [MetricType.CONSISTENCY_RATING, MetricType.INNOVATION_SCORE],
                RankingAlgorithm.MACHINE_LEARNING,
                UpdateFrequency.DAILY,
                max_entries=200,
                time_window_days=14,
                filters={"max_follower_count": 10000, "min_content_count": 5}
            )
            
            # Collaboration heroes
            await self.create_leaderboard(
                "collaboration_heroes",
                "Collaboration Heroes",
                "Masters of creator collaboration",
                LeaderboardType.COLLABORATION_HEROES,
                MetricType.COLLABORATION_COUNT,
                [MetricType.COMMUNITY_IMPACT, MetricType.TOTAL_ENGAGEMENT],
                RankingAlgorithm.ELO_RATING,
                UpdateFrequency.DAILY,
                max_entries=500,
                time_window_days=60
            )
            
            logger.info("✅ Default leaderboards initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing default leaderboards: {e}")

    async def create_leaderboard(
        self,
        leaderboard_id: str,
        name: str,
        description: str,
        leaderboard_type: LeaderboardType,
        primary_metric: MetricType,
        secondary_metrics: List[MetricType],
        ranking_algorithm: RankingAlgorithm,
        update_frequency: UpdateFrequency,
        max_entries: int = 1000,
        time_window_days: int = 30,
        weights: Dict[MetricType, float] = None,
        filters: Dict[str, Any] = None
    ) -> bool:
        """
        📋 Create new leaderboard configuration
        
        Set up leaderboard with specific rules and metrics
        """
        try:
            logger.info(f"📋 Creating leaderboard: {leaderboard_id}")
            
            if weights is None:
                weights = {primary_metric: 1.0}
            
            if filters is None:
                filters = {}
            
            config = LeaderboardConfig(
                leaderboard_id=leaderboard_id,
                name=name,
                description=description,
                leaderboard_type=leaderboard_type,
                primary_metric=primary_metric,
                secondary_metrics=secondary_metrics,
                ranking_algorithm=ranking_algorithm,
                update_frequency=update_frequency,
                max_entries=max_entries,
                time_window_days=time_window_days,
                weights=weights,
                filters=filters
            )
            
            self.leaderboards[leaderboard_id] = config
            self.leaderboard_data[leaderboard_id] = []
            
            logger.info(f"✅ Leaderboard created: {leaderboard_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating leaderboard: {e}")
            return False

    async def update_leaderboard_rankings(
        self,
        leaderboard_id: str,
        user_metrics: Dict[str, Dict[MetricType, float]] = None
    ) -> bool:
        """
        🔄 Update leaderboard rankings
        
        Recalculate rankings based on latest metrics
        """
        try:
            if leaderboard_id not in self.leaderboards:
                logger.error(f"Leaderboard {leaderboard_id} not found")
                return False
            
            config = self.leaderboards[leaderboard_id]
            logger.info(f"🔄 Updating rankings for: {leaderboard_id}")
            
            # Get user metrics (simulate if not provided)
            if user_metrics is None:
                user_metrics = await self._collect_user_metrics(config)
            
            # Calculate scores based on ranking algorithm
            scored_users = []
            for user_id, metrics in user_metrics.items():
                # Apply filters
                if not self._passes_filters(metrics, config.filters):
                    continue
                
                score = await self._calculate_user_score(metrics, config)
                if score > 0:
                    scored_users.append((user_id, score, metrics))
            
            # Sort by score (descending)
            scored_users.sort(key=lambda x: x[1], reverse=True)
            
            # Create leaderboard entries
            current_entries = self.leaderboard_data.get(leaderboard_id, [])
            previous_ranks = {entry.user_id: entry.rank for entry in current_entries}
            
            new_entries = []
            for rank, (user_id, score, metrics) in enumerate(scored_users[:config.max_entries], 1):
                previous_rank = previous_ranks.get(user_id)
                rank_change = 0
                if previous_rank:
                    rank_change = previous_rank - rank  # Positive = moved up
                
                # Calculate tier
                tier = self._calculate_tier(rank, len(scored_users))
                
                # Calculate percentile
                percentile = (len(scored_users) - rank + 1) / len(scored_users)
                
                entry = LeaderboardEntry(
                    user_id=user_id,
                    username=f"User_{user_id}",  # Would get from user service
                    score=score,
                    rank=rank,
                    previous_rank=previous_rank,
                    metrics=metrics,
                    last_updated=datetime.now(),
                    rank_change=rank_change,
                    percentile=percentile,
                    tier=tier
                )
                new_entries.append(entry)
            
            # Update leaderboard data
            self.leaderboard_data[leaderboard_id] = new_entries
            
            # Track ranking performance
            await self._track_ranking_performance(leaderboard_id, new_entries)
            
            # Update user engagement patterns
            await self._update_engagement_patterns(leaderboard_id, new_entries)
            
            logger.info(f"✅ Rankings updated: {len(new_entries)} entries in {leaderboard_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating leaderboard rankings: {e}")
            return False

    async def _collect_user_metrics(self, config: LeaderboardConfig) -> Dict[str, Dict[MetricType, float]]:
        """Collect user metrics for leaderboard calculation"""
        # Simulate user metrics collection - would integrate with real data in production
        user_metrics = {}
        
        # Generate sample data for testing
        for i in range(1000):
            user_id = f"user_{i}"
            
            # Base metrics with realistic distributions
            follower_base = max(100, np.random.lognormal(7, 1.5))
            engagement_base = follower_base * np.random.uniform(0.01, 0.15)
            
            metrics = {
                MetricType.FOLLOWERS_COUNT: follower_base,
                MetricType.TOTAL_ENGAGEMENT: engagement_base,
                MetricType.CONTENT_QUALITY_SCORE: np.random.beta(2, 2),  # 0-1 range
                MetricType.COLLABORATION_COUNT: max(0, np.random.poisson(3)),
                MetricType.REVENUE_GENERATED: max(0, np.random.gamma(2, 500)),
                MetricType.COMMUNITY_IMPACT: np.random.beta(1.5, 2),
                MetricType.INNOVATION_SCORE: np.random.beta(1.8, 2),
                MetricType.CONSISTENCY_RATING: np.random.beta(2, 1.5),
                MetricType.GROWTH_RATE: np.random.normal(0.1, 0.05),
                MetricType.VIRAL_COEFFICIENT: max(0, np.random.exponential(0.3))
            }
            
            user_metrics[user_id] = metrics
        
        return user_metrics

    def _passes_filters(self, metrics: Dict[MetricType, float], filters: Dict[str, Any]) -> bool:
        """Check if user metrics pass leaderboard filters"""
        try:
            for filter_key, filter_value in filters.items():
                if filter_key == "max_follower_count":
                    if metrics.get(MetricType.FOLLOWERS_COUNT, 0) > filter_value:
                        return False
                elif filter_key == "min_follower_count":
                    if metrics.get(MetricType.FOLLOWERS_COUNT, 0) < filter_value:
                        return False
                elif filter_key == "min_content_count":
                    # Would check content count from user data
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking filters: {e}")
            return True

    async def _calculate_user_score(
        self,
        metrics: Dict[MetricType, float],
        config: LeaderboardConfig
    ) -> float:
        """Calculate user score based on ranking algorithm"""
        try:
            if config.ranking_algorithm == RankingAlgorithm.SIMPLE_SCORE:
                return metrics.get(config.primary_metric, 0)
            
            elif config.ranking_algorithm == RankingAlgorithm.WEIGHTED_COMPOSITE:
                score = 0.0
                total_weight = 0.0
                
                for metric, weight in config.weights.items():
                    value = metrics.get(metric, 0)
                    # Normalize values to 0-1 range for fair weighting
                    normalized_value = self._normalize_metric_value(metric, value)
                    score += normalized_value * weight
                    total_weight += weight
                
                return score / max(total_weight, 1.0)
            
            elif config.ranking_algorithm == RankingAlgorithm.ELO_RATING:
                # Simplified ELO-like rating
                base_rating = 1000
                performance_factor = metrics.get(config.primary_metric, 0)
                return base_rating + performance_factor * 10
            
            elif config.ranking_algorithm == RankingAlgorithm.DECAY_ADJUSTED:
                # Time-decay adjusted scoring
                primary_score = metrics.get(config.primary_metric, 0)
                decay_factor = 0.95  # Slight decay for older achievements
                return primary_score * decay_factor
            
            elif config.ranking_algorithm == RankingAlgorithm.PERCENTILE_BASED:
                # Rank based on percentiles across metrics
                score = 0.0
                for metric, weight in config.weights.items():
                    value = metrics.get(metric, 0)
                    percentile = self._calculate_metric_percentile(metric, value)
                    score += percentile * weight
                
                return score
            
            elif config.ranking_algorithm == RankingAlgorithm.MACHINE_LEARNING:
                # ML-based scoring (simplified)
                features = [metrics.get(metric, 0) for metric in MetricType]
                # Would use trained ML model in production
                ml_score = np.mean(features) * 0.8 + np.std(features) * 0.2
                return ml_score
            
            else:
                return metrics.get(config.primary_metric, 0)
                
        except Exception as e:
            logger.error(f"Error calculating user score: {e}")
            return 0.0

    def _normalize_metric_value(self, metric: MetricType, value: float) -> float:
        """Normalize metric value to 0-1 range"""
        # Simplified normalization - would use actual data distribution in production
        normalization_ranges = {
            MetricType.FOLLOWERS_COUNT: (0, 1000000),
            MetricType.TOTAL_ENGAGEMENT: (0, 100000),
            MetricType.CONTENT_QUALITY_SCORE: (0, 1),
            MetricType.COLLABORATION_COUNT: (0, 50),
            MetricType.REVENUE_GENERATED: (0, 100000),
            MetricType.COMMUNITY_IMPACT: (0, 1),
            MetricType.INNOVATION_SCORE: (0, 1),
            MetricType.CONSISTENCY_RATING: (0, 1),
            MetricType.GROWTH_RATE: (-0.5, 1.0),
            MetricType.VIRAL_COEFFICIENT: (0, 5.0)
        }
        
        min_val, max_val = normalization_ranges.get(metric, (0, 1))
        return min(1.0, max(0.0, (value - min_val) / (max_val - min_val)))

    def _calculate_metric_percentile(self, metric: MetricType, value: float) -> float:
        """Calculate percentile for metric value"""
        # Simplified percentile calculation
        # In production, would use actual distribution data
        return min(1.0, max(0.0, value / 1000))  # Placeholder

    def _calculate_tier(self, rank: int, total_participants: int) -> str:
        """Calculate tier based on rank and total participants"""
        if total_participants == 0:
            return "bronze"
        
        percentile = rank / total_participants
        
        if percentile <= 0.01:  # Top 1%
            return "diamond"
        elif percentile <= 0.05:  # Top 5%
            return "platinum"
        elif percentile <= 0.15:  # Top 15%
            return "gold"
        elif percentile <= 0.35:  # Top 35%
            return "silver"
        else:
            return "bronze"

    async def _track_ranking_performance(
        self,
        leaderboard_id: str,
        entries: List[LeaderboardEntry]
    ) -> None:
        """Track ranking performance metrics"""
        try:
            if leaderboard_id not in self.ranking_performance:
                self.ranking_performance[leaderboard_id] = {}
            
            perf_data = self.ranking_performance[leaderboard_id]
            
            # Calculate performance metrics
            rank_changes = [entry.rank_change for entry in entries if entry.rank_change != 0]
            scores = [entry.score for entry in entries]
            
            perf_data.update({
                'avg_score': np.mean(scores) if scores else 0,
                'score_variance': np.var(scores) if len(scores) > 1 else 0,
                'avg_rank_change': np.mean([abs(rc) for rc in rank_changes]) if rank_changes else 0,
                'stability_score': 1.0 - (len(rank_changes) / len(entries)) if entries else 0,
                'last_updated': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error tracking ranking performance: {e}")

    async def _update_engagement_patterns(
        self,
        leaderboard_id: str,
        entries: List[LeaderboardEntry]
    ) -> None:
        """Update user engagement patterns based on leaderboard interaction"""
        try:
            for entry in entries:
                user_id = entry.user_id
                
                # Record engagement event
                engagement_event = {
                    'timestamp': datetime.now(),
                    'leaderboard_id': leaderboard_id,
                    'rank': entry.rank,
                    'rank_change': entry.rank_change,
                    'score': entry.score,
                    'tier': entry.tier
                }
                
                self.user_engagement_history[user_id].append(engagement_event)
                
                # Analyze engagement pattern
                pattern = self._analyze_user_engagement_pattern(user_id)
                self.engagement_patterns[user_id] = pattern
                
                # Update motivation score
                motivation = self._calculate_motivation_score(user_id, entry)
                self.motivation_scores[user_id] = motivation
                
        except Exception as e:
            logger.error(f"Error updating engagement patterns: {e}")

    def _analyze_user_engagement_pattern(self, user_id: str) -> EngagementPattern:
        """Analyze user's engagement pattern with leaderboards"""
        try:
            history = self.user_engagement_history[user_id]
            if len(history) < 3:
                return EngagementPattern.CASUAL_OBSERVER
            
            recent_events = list(history)[-10:]  # Last 10 interactions
            
            # Calculate engagement metrics
            rank_improvements = sum(1 for event in recent_events if event.get('rank_change', 0) > 0)
            rank_declines = sum(1 for event in recent_events if event.get('rank_change', 0) < 0)
            average_rank = np.mean([event.get('rank', 1000) for event in recent_events])
            score_trend = np.polyfit(range(len(recent_events)), 
                                   [event.get('score', 0) for event in recent_events], 1)[0]
            
            # Classify engagement pattern
            if rank_improvements >= 7 and score_trend > 0:
                return EngagementPattern.COMPETITIVE_CLIMBER
            elif average_rank <= 100 and abs(score_trend) < 0.1:
                return EngagementPattern.HIGHLY_ENGAGED
            elif rank_improvements >= 3 and rank_declines <= 3:
                return EngagementPattern.MODERATELY_ENGAGED
            elif rank_declines >= 6:
                return EngagementPattern.DISENGAGED
            else:
                return EngagementPattern.PASSIVE_VIEWER
                
        except Exception as e:
            logger.error(f"Error analyzing engagement pattern: {e}")
            return EngagementPattern.CASUAL_OBSERVER

    def _calculate_motivation_score(self, user_id: str, entry: LeaderboardEntry) -> float:
        """Calculate user motivation score based on performance and psychology"""
        try:
            base_motivation = 0.5
            
            # Rank-based motivation
            if entry.rank <= 10:
                rank_motivation = 0.9
            elif entry.rank <= 100:
                rank_motivation = 0.7
            elif entry.rank <= 1000:
                rank_motivation = 0.5
            else:
                rank_motivation = 0.3
            
            # Progress-based motivation
            progress_motivation = 0.5
            if entry.rank_change > 0:
                progress_motivation = min(1.0, 0.5 + entry.rank_change * 0.01)
            elif entry.rank_change < 0:
                progress_motivation = max(0.1, 0.5 + entry.rank_change * 0.01)
            
            # Tier-based motivation
            tier_motivation = {
                "diamond": 0.95,
                "platinum": 0.85,
                "gold": 0.7,
                "silver": 0.55,
                "bronze": 0.4
            }.get(entry.tier, 0.5)
            
            # Combine factors
            motivation = (rank_motivation * 0.4 + progress_motivation * 0.4 + tier_motivation * 0.2)
            
            return min(1.0, max(0.0, motivation))
            
        except Exception as e:
            logger.error(f"Error calculating motivation score: {e}")
            return 0.5

    async def analyze_leaderboard_performance(
        self,
        leaderboard_id: str,
        time_period_hours: int = 168  # 1 week
    ) -> Optional[LeaderboardAnalytics]:
        """
        📊 Analyze leaderboard performance and engagement
        
        Comprehensive analysis of leaderboard effectiveness
        """
        try:
            if leaderboard_id not in self.leaderboards:
                return None
            
            logger.info(f"📊 Analyzing leaderboard performance: {leaderboard_id}")
            
            config = self.leaderboards[leaderboard_id]
            entries = self.leaderboard_data.get(leaderboard_id, [])
            
            if not entries:
                return None
            
            # Analyze engagement patterns
            pattern_counts = defaultdict(int)
            active_participants = 0
            
            for entry in entries:
                user_pattern = self.engagement_patterns.get(entry.user_id, EngagementPattern.CASUAL_OBSERVER)
                pattern_counts[user_pattern] += 1
                
                if user_pattern in [EngagementPattern.HIGHLY_ENGAGED, EngagementPattern.COMPETITIVE_CLIMBER]:
                    active_participants += 1
            
            # Calculate engagement metrics
            total_participants = len(entries)
            active_ratio = active_participants / max(1, total_participants)
            
            scores = [entry.score for entry in entries]
            avg_score = np.mean(scores)
            
            # Score distribution
            score_distribution = {
                "top_10_percent": len([s for s in scores if s >= np.percentile(scores, 90)]),
                "top_25_percent": len([s for s in scores if s >= np.percentile(scores, 75)]),
                "middle_50_percent": len([s for s in scores if np.percentile(scores, 25) <= s < np.percentile(scores, 75)]),
                "bottom_25_percent": len([s for s in scores if s < np.percentile(scores, 25)])
            }
            
            # Engagement metrics
            engagement_metrics = {
                'participation_rate': active_ratio,
                'avg_motivation_score': np.mean([
                    self.motivation_scores.get(entry.user_id, 0.5) for entry in entries
                ]),
                'rank_volatility': np.mean([
                    abs(entry.rank_change) for entry in entries if entry.rank_change
                ]) if any(entry.rank_change for entry in entries) else 0,
                'tier_distribution_entropy': self._calculate_tier_entropy(entries)
            }
            
            # Calculate churn and growth rates
            churn_rate = len([
                user_id for user_id, pattern in self.engagement_patterns.items()
                if pattern == EngagementPattern.DISENGAGED
            ]) / max(1, total_participants)
            
            growth_rate = 0.1  # Simplified - would calculate from historical data
            
            # Top movers
            top_movers = sorted(
                [entry.user_id for entry in entries if entry.rank_change > 0],
                key=lambda uid: next(e.rank_change for e in entries if e.user_id == uid),
                reverse=True
            )[:5]
            
            analytics = LeaderboardAnalytics(
                leaderboard_id=leaderboard_id,
                time_period=f"{time_period_hours}h",
                total_participants=total_participants,
                active_participants=active_participants,
                average_score=avg_score,
                score_distribution=score_distribution,
                engagement_metrics=engagement_metrics,
                churn_rate=churn_rate,
                growth_rate=growth_rate,
                top_movers=top_movers,
                engagement_patterns=dict(pattern_counts)
            )
            
            # Cache analytics
            self.analytics_cache[leaderboard_id] = analytics
            
            logger.info(f"✅ Leaderboard analysis completed: {active_ratio:.1%} active participation")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error analyzing leaderboard performance: {e}")
            return None

    def _calculate_tier_entropy(self, entries: List[LeaderboardEntry]) -> float:
        """Calculate entropy of tier distribution"""
        try:
            tier_counts = defaultdict(int)
            for entry in entries:
                tier_counts[entry.tier] += 1
            
            total = len(entries)
            if total == 0:
                return 0.0
            
            entropy = 0.0
            for count in tier_counts.values():
                if count > 0:
                    probability = count / total
                    entropy -= probability * np.log2(probability)
            
            return entropy
            
        except Exception as e:
            logger.error(f"Error calculating tier entropy: {e}")
            return 0.0

    async def create_competition_event(
        self,
        event_id: str,
        name: str,
        leaderboard_id: str,
        duration_hours: int,
        prizes: Dict[str, Any],
        participation_boost: float = 1.5,
        special_rules: Dict[str, Any] = None
    ) -> bool:
        """
        🏆 Create competition event for leaderboard
        
        Special time-limited competitions with enhanced rewards
        """
        try:
            logger.info(f"🏆 Creating competition event: {event_id}")
            
            if leaderboard_id not in self.leaderboards:
                logger.error(f"Leaderboard {leaderboard_id} not found")
                return False
            
            if special_rules is None:
                special_rules = {}
            
            event = CompetitionEvent(
                event_id=event_id,
                name=name,
                leaderboard_id=leaderboard_id,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(hours=duration_hours),
                prizes=prizes,
                participation_boost=participation_boost,
                special_rules=special_rules
            )
            
            self.active_competitions[event_id] = event
            
            # Track baseline metrics before event
            baseline_analytics = await self.analyze_leaderboard_performance(leaderboard_id)
            if baseline_analytics:
                self.event_impact_metrics[event_id] = {
                    'baseline_participation': baseline_analytics.active_participants,
                    'baseline_engagement': baseline_analytics.engagement_metrics.get('participation_rate', 0),
                    'start_time': datetime.now().isoformat()
                }
            
            logger.info(f"✅ Competition event created: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating competition event: {e}")
            return False

    async def measure_competition_impact(
        self,
        event_id: str
    ) -> Dict[str, Any]:
        """
        📈 Measure impact of competition event
        
        Analyze how competition affects engagement and performance
        """
        try:
            if event_id not in self.active_competitions:
                return {}
            
            event = self.active_competitions[event_id]
            logger.info(f"📈 Measuring competition impact: {event_id}")
            
            # Get current analytics
            current_analytics = await self.analyze_leaderboard_performance(event.leaderboard_id)
            if not current_analytics:
                return {}
            
            # Get baseline metrics
            baseline_metrics = self.event_impact_metrics.get(event_id, {})
            
            impact_analysis = {
                'event_id': event_id,
                'event_name': event.name,
                'leaderboard_id': event.leaderboard_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'impact_metrics': {},
                'participation_changes': {},
                'engagement_changes': {},
                'performance_insights': []
            }
            
            # Calculate impact metrics
            if baseline_metrics:
                baseline_participation = baseline_metrics.get('baseline_participation', 0)
                baseline_engagement = baseline_metrics.get('baseline_engagement', 0)
                
                participation_change = (
                    (current_analytics.active_participants - baseline_participation) /
                    max(1, baseline_participation)
                )
                
                engagement_change = (
                    (current_analytics.engagement_metrics.get('participation_rate', 0) - baseline_engagement) /
                    max(0.01, baseline_engagement)
                )
                
                impact_analysis['impact_metrics'] = {
                    'participation_boost': participation_change,
                    'engagement_boost': engagement_change,
                    'event_effectiveness': (participation_change + engagement_change) / 2,
                    'participants_added': current_analytics.active_participants - baseline_participation
                }
                
                impact_analysis['participation_changes'] = {
                    'baseline': baseline_participation,
                    'current': current_analytics.active_participants,
                    'change_percentage': participation_change * 100
                }
                
                impact_analysis['engagement_changes'] = {
                    'baseline': baseline_engagement,
                    'current': current_analytics.engagement_metrics.get('participation_rate', 0),
                    'change_percentage': engagement_change * 100
                }
            
            # Performance insights
            insights = []
            
            if impact_analysis['impact_metrics'].get('participation_boost', 0) > 0.2:
                insights.append("Competition significantly increased participation (+20%+)")
            
            if impact_analysis['impact_metrics'].get('engagement_boost', 0) > 0.15:
                insights.append("Competition boosted user engagement substantially")
            
            if current_analytics.engagement_metrics.get('rank_volatility', 0) > 5:
                insights.append("High ranking volatility indicates intense competition")
            
            # Analyze top performers during event
            entries = self.leaderboard_data.get(event.leaderboard_id, [])
            top_performers = entries[:10]  # Top 10
            
            if top_performers:
                avg_motivation = np.mean([
                    self.motivation_scores.get(entry.user_id, 0.5) for entry in top_performers
                ])
                if avg_motivation > 0.8:
                    insights.append("Top performers showing high motivation levels")
            
            if not insights:
                insights.append("Competition impact is minimal or neutral")
            
            impact_analysis['performance_insights'] = insights
            
            logger.info(f"✅ Competition impact measured: {impact_analysis['impact_metrics'].get('event_effectiveness', 0):.2f} effectiveness")
            return impact_analysis
            
        except Exception as e:
            logger.error(f"❌ Error measuring competition impact: {e}")
            return {}

    async def optimize_leaderboard_mechanics(
        self,
        leaderboard_id: str,
        optimization_goals: List[str] = None
    ) -> Dict[str, Any]:
        """
        🔧 Optimize leaderboard mechanics for better engagement
        
        AI-driven optimization of leaderboard parameters
        """
        try:
            if leaderboard_id not in self.leaderboards:
                return {}
            
            if optimization_goals is None:
                optimization_goals = ["increase_participation", "reduce_churn", "improve_engagement"]
            
            logger.info(f"🔧 Optimizing leaderboard mechanics: {leaderboard_id}")
            
            config = self.leaderboards[leaderboard_id]
            analytics = await self.analyze_leaderboard_performance(leaderboard_id)
            
            if not analytics:
                return {}
            
            optimization_report = {
                'leaderboard_id': leaderboard_id,
                'current_performance': {
                    'participation_rate': analytics.engagement_metrics.get('participation_rate', 0),
                    'churn_rate': analytics.churn_rate,
                    'avg_motivation': analytics.engagement_metrics.get('avg_motivation_score', 0)
                },
                'recommendations': [],
                'proposed_changes': {},
                'expected_impact': {},
                'implementation_priority': []
            }
            
            # Analyze current issues and generate recommendations
            participation_rate = analytics.engagement_metrics.get('participation_rate', 0)
            churn_rate = analytics.churn_rate
            
            # Participation optimization
            if "increase_participation" in optimization_goals and participation_rate < 0.3:
                optimization_report['recommendations'].extend([
                    "Reduce leaderboard size to create more achievable rankings",
                    "Implement more frequent updates to maintain engagement",
                    "Add tier-based rewards to motivate lower-ranked users"
                ])
                
                optimization_report['proposed_changes']['max_entries'] = min(config.max_entries, 500)
                optimization_report['proposed_changes']['update_frequency'] = UpdateFrequency.HOURLY
                
                optimization_report['expected_impact']['participation_increase'] = 0.15
            
            # Churn reduction
            if "reduce_churn" in optimization_goals and churn_rate > 0.2:
                optimization_report['recommendations'].extend([
                    "Implement decay-adjusted scoring to give struggling users a chance",
                    "Create separate leaderboards for different skill levels",
                    "Add comeback bonuses for users who improve their ranking"
                ])
                
                optimization_report['proposed_changes']['ranking_algorithm'] = RankingAlgorithm.DECAY_ADJUSTED
                optimization_report['expected_impact']['churn_reduction'] = 0.1
            
            # Engagement improvement
            if "improve_engagement" in optimization_goals:
                avg_motivation = analytics.engagement_metrics.get('avg_motivation_score', 0)
                if avg_motivation < 0.6:
                    optimization_report['recommendations'].extend([
                        "Weight growth metrics more heavily to reward improvement",
                        "Implement achievement milestones within rankings",
                        "Add social features like team competitions"
                    ])
                    
                    # Adjust weights to favor growth
                    new_weights = config.weights.copy()
                    if MetricType.GROWTH_RATE in new_weights:
                        new_weights[MetricType.GROWTH_RATE] *= 1.5
                    else:
                        new_weights[MetricType.GROWTH_RATE] = 0.3
                    
                    optimization_report['proposed_changes']['weights'] = new_weights
                    optimization_report['expected_impact']['motivation_increase'] = 0.2
            
            # Algorithm optimization based on current performance
            current_algo = config.ranking_algorithm
            algo_performance = self.ranking_performance.get(leaderboard_id, {})
            
            stability_score = algo_performance.get('stability_score', 0.5)
            if stability_score < 0.3:
                optimization_report['recommendations'].append(
                    "Current ranking algorithm creates too much volatility - consider ELO or percentile-based ranking"
                )
                optimization_report['proposed_changes']['ranking_algorithm'] = RankingAlgorithm.ELO_RATING
            
            # Priority ranking
            priority_items = []
            
            if churn_rate > 0.3:
                priority_items.append(("High", "Address high churn rate immediately"))
            
            if participation_rate < 0.2:
                priority_items.append(("High", "Boost participation through algorithm changes"))
            
            if stability_score < 0.2:
                priority_items.append(("Medium", "Improve ranking stability"))
            
            if not priority_items:
                priority_items.append(("Low", "Fine-tune existing mechanics"))
            
            optimization_report['implementation_priority'] = priority_items
            
            logger.info(f"✅ Leaderboard optimization completed: {len(optimization_report['recommendations'])} recommendations")
            return optimization_report
            
        except Exception as e:
            logger.error(f"❌ Error optimizing leaderboard mechanics: {e}")
            return {}

    async def generate_leaderboard_report(
        self,
        time_period_hours: int = 168  # 1 week
    ) -> Dict[str, Any]:
        """
        📊 Generate comprehensive leaderboard performance report
        
        Executive summary of all leaderboard performance and engagement
        """
        try:
            logger.info(f"📊 Generating leaderboard report ({time_period_hours}h)")
            
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'time_period_hours': time_period_hours,
                'executive_summary': {},
                'leaderboard_performance': {},
                'user_engagement_analysis': {},
                'competition_impact': {},
                'optimization_recommendations': [],
                'action_items': []
            }
            
            # Analyze all leaderboards
            total_participants = 0
            total_active_users = 0
            leaderboard_analytics = {}
            
            for leaderboard_id in self.leaderboards:
                analytics = await self.analyze_leaderboard_performance(leaderboard_id, time_period_hours)
                if analytics:
                    leaderboard_analytics[leaderboard_id] = analytics
                    total_participants += analytics.total_participants
                    total_active_users += analytics.active_participants
            
            # Executive summary
            overall_participation_rate = total_active_users / max(1, total_participants) if total_participants > 0 else 0
            
            report['executive_summary'] = {
                'total_leaderboards': len(self.leaderboards),
                'active_leaderboards': len(leaderboard_analytics),
                'total_participants': total_participants,
                'total_active_users': total_active_users,
                'overall_participation_rate': overall_participation_rate,
                'active_competitions': len(self.active_competitions),
                'overall_health_score': self._calculate_overall_health_score(leaderboard_analytics)
            }
            
            # Individual leaderboard performance
            for leaderboard_id, analytics in leaderboard_analytics.items():
                config = self.leaderboards[leaderboard_id]
                
                report['leaderboard_performance'][leaderboard_id] = {
                    'name': config.name,
                    'type': config.leaderboard_type.value,
                    'total_participants': analytics.total_participants,
                    'active_participants': analytics.active_participants,
                    'participation_rate': analytics.engagement_metrics.get('participation_rate', 0),
                    'churn_rate': analytics.churn_rate,
                    'avg_motivation_score': analytics.engagement_metrics.get('avg_motivation_score', 0),
                    'rank_volatility': analytics.engagement_metrics.get('rank_volatility', 0),
                    'top_movers': analytics.top_movers[:3]
                }
            
            # User engagement analysis
            engagement_distribution = defaultdict(int)
            motivation_scores = []
            
            for user_id, pattern in self.engagement_patterns.items():
                engagement_distribution[pattern.value] += 1
            
            for user_id, score in self.motivation_scores.items():
                motivation_scores.append(score)
            
            report['user_engagement_analysis'] = {
                'engagement_pattern_distribution': dict(engagement_distribution),
                'avg_motivation_score': np.mean(motivation_scores) if motivation_scores else 0,
                'highly_engaged_users': engagement_distribution.get('highly_engaged', 0),
                'disengaged_users': engagement_distribution.get('disengaged', 0),
                'competitive_climbers': engagement_distribution.get('competitive_climber', 0)
            }
            
            # Competition impact analysis
            competition_impacts = {}
            for event_id in self.active_competitions:
                impact = await self.measure_competition_impact(event_id)
                if impact:
                    competition_impacts[event_id] = {
                        'event_name': impact.get('event_name', ''),
                        'participation_boost': impact.get('impact_metrics', {}).get('participation_boost', 0),
                        'engagement_boost': impact.get('impact_metrics', {}).get('engagement_boost', 0),
                        'effectiveness': impact.get('impact_metrics', {}).get('event_effectiveness', 0)
                    }
            
            report['competition_impact'] = competition_impacts
            
            # Generate recommendations
            recommendations = []
            
            if overall_participation_rate < 0.3:
                recommendations.append("Overall participation is low - review leaderboard accessibility and rewards")
            
            if report['user_engagement_analysis']['disengaged_users'] > total_active_users * 0.3:
                recommendations.append("High disengagement detected - implement retention strategies")
            
            # Find best and worst performing leaderboards
            if leaderboard_analytics:
                best_lb = max(leaderboard_analytics.items(), 
                            key=lambda x: x[1].engagement_metrics.get('participation_rate', 0))
                worst_lb = min(leaderboard_analytics.items(), 
                             key=lambda x: x[1].engagement_metrics.get('participation_rate', 0))
                
                recommendations.append(f"Top performing leaderboard: {best_lb[0]} - replicate successful mechanics")
                recommendations.append(f"Optimize underperforming leaderboard: {worst_lb[0]}")
            
            if not recommendations:
                recommendations.append("Leaderboard system is performing well - continue monitoring")
            
            report['optimization_recommendations'] = recommendations
            
            # Action items
            action_items = []
            
            low_engagement_leaderboards = [
                lb_id for lb_id, analytics in leaderboard_analytics.items()
                if analytics.engagement_metrics.get('participation_rate', 0) < 0.2
            ]
            
            if low_engagement_leaderboards:
                action_items.append(f"Urgent: Optimize low-engagement leaderboards: {', '.join(low_engagement_leaderboards)}")
            
            high_churn_leaderboards = [
                lb_id for lb_id, analytics in leaderboard_analytics.items()
                if analytics.churn_rate > 0.4
            ]
            
            if high_churn_leaderboards:
                action_items.append(f"Address high churn in: {', '.join(high_churn_leaderboards)}")
            
            if not action_items:
                action_items.append("Continue regular monitoring and optimization")
            
            report['action_items'] = action_items
            
            logger.info(f"✅ Leaderboard report generated: {overall_participation_rate:.1%} overall participation")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating leaderboard report: {e}")
            return {}

    def _calculate_overall_health_score(self, analytics_data: Dict[str, LeaderboardAnalytics]) -> float:
        """Calculate overall health score for leaderboard system"""
        try:
            if not analytics_data:
                return 0.0
            
            health_factors = []
            
            for analytics in analytics_data.values():
                participation_score = analytics.engagement_metrics.get('participation_rate', 0)
                churn_score = 1.0 - analytics.churn_rate
                motivation_score = analytics.engagement_metrics.get('avg_motivation_score', 0)
                
                leaderboard_health = (participation_score * 0.4 + churn_score * 0.3 + motivation_score * 0.3)
                health_factors.append(leaderboard_health)
            
            return np.mean(health_factors)
            
        except Exception as e:
            logger.error(f"Error calculating overall health score: {e}")
            return 0.5

# Usage example
async def main() -> None:
    """Test the leaderboard performance tracker"""
    try:
        # Initialize tracker
        tracker = LeaderboardPerformanceTracker()
        
        # Wait for initialization
        await asyncio.sleep(2)
        
        # Update rankings
        for leaderboard_id in tracker.leaderboards:
            success = await tracker.update_leaderboard_rankings(leaderboard_id)
            print(f"Updated rankings for {leaderboard_id}: {success}")
        
        # Analyze performance
        analytics = await tracker.analyze_leaderboard_performance("global_creators")
        if analytics:
            print(f"Global creators analytics: {analytics.active_participants} active participants")
        
        # Create competition
        competition_created = await tracker.create_competition_event(
            "weekly_contest_001",
            "Weekly Creator Contest",
            "weekly_champions",
            168,  # 1 week
            {"first_place": "$1000", "second_place": "$500", "third_place": "$250"}
        )
        print(f"Competition created: {competition_created}")
        
        # Measure competition impact
        if competition_created:
            impact = await tracker.measure_competition_impact("weekly_contest_001")
            print(f"Competition impact measured: {len(impact.get('performance_insights', []))} insights")
        
        # Optimize mechanics
        optimization = await tracker.optimize_leaderboard_mechanics("global_creators")
        print(f"Optimization completed: {len(optimization.get('recommendations', []))} recommendations")
        
        # Generate report
        report = await tracker.generate_leaderboard_report()
        health_score = report.get('executive_summary', {}).get('overall_health_score', 0)
        print(f"Report generated: {health_score:.2f} overall health score")
        
    except Exception as e:
        print(f"Error in leaderboard performance tracking: {e}")

if __name__ == "__main__":
    asyncio.run(main())