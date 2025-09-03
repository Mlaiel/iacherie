"""Leaderboard System - Dynamic Ranking and Competition Management
================================================================

Advanced leaderboard and ranking system providing real-time leaderboards,
competitive rankings, seasonal competitions, and comprehensive analytics
for content creator engagement and motivation.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/gamification/achievements/leaderboards.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA

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
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4
from enum import Enum
from dataclasses import dataclass, field
import json
from collections import defaultdict
import heapq

logger = logging.getLogger(__name__)


class LeaderboardType(str, Enum):
    """Types of leaderboards."""
    GLOBAL = "global"
    REGIONAL = "regional"
    CATEGORY = "category"
    SEASONAL = "seasonal"
    CHALLENGE = "challenge"
    COLLABORATION = "collaboration"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    QUALITY = "quality"


class LeaderboardPeriod(str, Enum):
    """Leaderboard time periods."""
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"


class ScoreType(str, Enum):
    """Types of scoring systems."""
    TOTAL_POINTS = "total_points"
    AVERAGE_QUALITY = "average_quality"
    ENGAGEMENT_RATE = "engagement_rate"
    REVENUE_GENERATED = "revenue_generated"
    COLLABORATIONS = "collaborations"
    CONTENT_COUNT = "content_count"
    FOLLOWER_GROWTH = "follower_growth"
    INNOVATION_SCORE = "innovation_score"
    COMPOSITE = "composite"


@dataclass
class LeaderboardEntry:
    """Individual leaderboard entry."""
    user_id: str
    username: str
    score: float
    rank: int
    previous_rank: Optional[int] = None
    rank_change: int = 0
    badge_count: int = 0
    achievement_count: int = 0
    tier: str = "Newcomer"
    country: Optional[str] = None
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Leaderboard:
    """Leaderboard configuration and data."""
    id: str
    name: str
    description: str
    leaderboard_type: LeaderboardType
    score_type: ScoreType
    period: LeaderboardPeriod
    max_entries: int = 1000
    update_frequency: timedelta = field(default=timedelta(hours=1))
    entries: List[LeaderboardEntry] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class LeaderboardSystem:
    """
    Advanced leaderboard and ranking management system.
    
    Provides real-time leaderboards, competitive rankings, seasonal competitions,
    and comprehensive analytics for user engagement and motivation.
    """
    
    def __init__(self):
        """Initialize the leaderboard system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.initialized = False
        
        # Leaderboard definitions
        self.leaderboards: Dict[str, Leaderboard] = {}
        
        # User score tracking
        self.user_scores: Dict[str, Dict[str, float]] = {}
        
        # Historical data for period calculations
        self.score_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Real-time update queue
        self._update_queue: List[Dict[str, Any]] = []
        self._processing_lock = asyncio.Lock()
        
        # Cached rankings for performance
        self._ranking_cache: Dict[str, List[LeaderboardEntry]] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        
        self.logger.info("LeaderboardSystem initialized")
    
    async def initialize(self) -> bool:
        """Initialize the leaderboard system with default leaderboards."""
        try:
            # Create default leaderboards
            await self._create_default_leaderboards()
            
            # Start background update task
            asyncio.create_task(self._background_update_task())
            
            self.initialized = True
            self.logger.info(f"✅ LeaderboardSystem initialized with {len(self.leaderboards)} leaderboards")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize LeaderboardSystem: {e}")
            return False
    
    async def _create_default_leaderboards(self):
        """Create default leaderboard configurations."""
        default_leaderboards = [
            # Global Leaderboards
            Leaderboard(
                id="global_overall",
                name="Global Leaderboard",
                description="Top creators worldwide based on overall performance",
                leaderboard_type=LeaderboardType.GLOBAL,
                score_type=ScoreType.COMPOSITE,
                period=LeaderboardPeriod.ALL_TIME,
                max_entries=100,
                weights={
                    "total_points": 0.3,
                    "engagement_rate": 0.2,
                    "content_quality": 0.2,
                    "collaboration_score": 0.15,
                    "innovation_score": 0.15
                }
            ),
            Leaderboard(
                id="weekly_rising_stars",
                name="Weekly Rising Stars",
                description="Top performing creators this week",
                leaderboard_type=LeaderboardType.GLOBAL,
                score_type=ScoreType.TOTAL_POINTS,
                period=LeaderboardPeriod.WEEKLY,
                max_entries=50,
                update_frequency=timedelta(hours=6)
            ),
            Leaderboard(
                id="monthly_champions",
                name="Monthly Champions",
                description="Top creators of the month",
                leaderboard_type=LeaderboardType.GLOBAL,
                score_type=ScoreType.COMPOSITE,
                period=LeaderboardPeriod.MONTHLY,
                max_entries=25,
                weights={
                    "total_points": 0.4,
                    "engagement_rate": 0.3,
                    "revenue_generated": 0.3
                }
            ),
            
            # Category-specific Leaderboards
            Leaderboard(
                id="content_creators",
                name="Content Creation Masters",
                description="Top content creators by volume and quality",
                leaderboard_type=LeaderboardType.CATEGORY,
                score_type=ScoreType.COMPOSITE,
                period=LeaderboardPeriod.ALL_TIME,
                max_entries=50,
                filters={"category": "content_creation"},
                weights={
                    "content_count": 0.4,
                    "average_quality": 0.4,
                    "engagement_rate": 0.2
                }
            ),
            Leaderboard(
                id="collaboration_leaders",
                name="Collaboration Leaders",
                description="Top collaborators and team players",
                leaderboard_type=LeaderboardType.CATEGORY,
                score_type=ScoreType.COLLABORATIONS,
                period=LeaderboardPeriod.ALL_TIME,
                max_entries=30,
                filters={"category": "collaboration"}
            ),
            Leaderboard(
                id="revenue_generators",
                name="Revenue Generators",
                description="Top revenue-generating creators",
                leaderboard_type=LeaderboardType.CATEGORY,
                score_type=ScoreType.REVENUE_GENERATED,
                period=LeaderboardPeriod.ALL_TIME,
                max_entries=25,
                filters={"category": "monetization"}
            ),
            
            # Engagement Leaderboards
            Leaderboard(
                id="engagement_masters",
                name="Engagement Masters",
                description="Creators with highest engagement rates",
                leaderboard_type=LeaderboardType.ENGAGEMENT,
                score_type=ScoreType.ENGAGEMENT_RATE,
                period=LeaderboardPeriod.MONTHLY,
                max_entries=20,
                update_frequency=timedelta(hours=12)
            ),
            
            # Innovation Leaderboard
            Leaderboard(
                id="innovation_pioneers",
                name="Innovation Pioneers",
                description="Most innovative and forward-thinking creators",
                leaderboard_type=LeaderboardType.CATEGORY,
                score_type=ScoreType.INNOVATION_SCORE,
                period=LeaderboardPeriod.QUARTERLY,
                max_entries=15,
                filters={"category": "innovation"}
            )
        ]
        
        for leaderboard in default_leaderboards:
            self.leaderboards[leaderboard.id] = leaderboard
        
        self.logger.info(f"Created {len(default_leaderboards)} default leaderboards")
    
    async def update_rankings(
        self,
        user_id: str,
        points_earned: float,
        action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user rankings based on new activity."""
        try:
            # Update user scores
            await self._update_user_scores(user_id, points_earned, action_data)
            
            # Queue leaderboard updates
            affected_leaderboards = await self._queue_leaderboard_updates(user_id, action_data)
            
            # Get current user rankings
            current_rankings = await self._get_user_current_rankings(user_id)
            
            return {
                "updates": affected_leaderboards,
                "current_rankings": current_rankings,
                "total_points": self.user_scores.get(user_id, {}).get("total_points", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error updating rankings for user {user_id}: {e}")
            return {"updates": [], "error": str(e)}
    
    async def _update_user_scores(
        self,
        user_id: str,
        points_earned: float,
        action_data: Dict[str, Any]
    ):
        """Update user's various score metrics."""
        if user_id not in self.user_scores:
            self.user_scores[user_id] = {
                "total_points": 0,
                "engagement_rate": 0,
                "content_quality": 0,
                "collaboration_score": 0,
                "innovation_score": 0,
                "revenue_generated": 0,
                "content_count": 0,
                "follower_growth": 0
            }
        
        scores = self.user_scores[user_id]
        
        # Update total points
        scores["total_points"] += points_earned
        
        # Update specific metrics based on action data
        if "engagement_rate" in action_data:
            # Rolling average engagement rate
            current_rate = scores["engagement_rate"]
            new_rate = action_data["engagement_rate"]
            scores["engagement_rate"] = (current_rate * 0.9) + (new_rate * 0.1)
        
        if "quality_score" in action_data:
            current_quality = scores["content_quality"]
            new_quality = action_data["quality_score"]
            scores["content_quality"] = (current_quality * 0.9) + (new_quality * 0.1)
        
        if "collaboration_bonus" in action_data:
            scores["collaboration_score"] += action_data["collaboration_bonus"]
        
        if "innovation_points" in action_data:
            scores["innovation_score"] += action_data["innovation_points"]
        
        if "revenue_amount" in action_data:
            scores["revenue_generated"] += action_data["revenue_amount"]
        
        if "content_uploaded" in action_data:
            scores["content_count"] += 1
        
        # Record score history
        await self._record_score_history(user_id, scores, action_data)
    
    async def _record_score_history(
        self,
        user_id: str,
        scores: Dict[str, float],
        action_data: Dict[str, Any]
    ):
        """Record historical score data for period calculations."""
        if user_id not in self.score_history:
            self.score_history[user_id] = []
        
        history_entry = {
            "timestamp": datetime.utcnow(),
            "scores": scores.copy(),
            "action_type": action_data.get("action_type", "unknown"),
            "points_earned": action_data.get("points_earned", 0)
        }
        
        self.score_history[user_id].append(history_entry)
        
        # Limit history size (keep last 1000 entries)
        if len(self.score_history[user_id]) > 1000:
            self.score_history[user_id] = self.score_history[user_id][-1000:]
    
    async def _queue_leaderboard_updates(
        self,
        user_id: str,
        action_data: Dict[str, Any]
    ) -> List[str]:
        """Queue leaderboard updates based on user activity."""
        affected_leaderboards = []
        
        for leaderboard_id, leaderboard in self.leaderboards.items():
            if not leaderboard.is_active:
                continue
            
            # Check if this action affects this leaderboard
            if self._should_update_leaderboard(leaderboard, action_data):
                self._update_queue.append({
                    "leaderboard_id": leaderboard_id,
                    "user_id": user_id,
                    "timestamp": datetime.utcnow(),
                    "action_data": action_data
                })
                affected_leaderboards.append(leaderboard_id)
        
        return affected_leaderboards
    
    def _should_update_leaderboard(
        self,
        leaderboard: Leaderboard,
        action_data: Dict[str, Any]
    ) -> bool:
        """Check if leaderboard should be updated based on action."""
        # Check filters
        if leaderboard.filters:
            for filter_key, filter_value in leaderboard.filters.items():
                if filter_key in action_data and action_data[filter_key] != filter_value:
                    return False
        
        # Check score type relevance
        relevant_actions = {
            ScoreType.TOTAL_POINTS: ["content_upload", "achievement_unlock", "collaboration_success"],
            ScoreType.ENGAGEMENT_RATE: ["engagement_update", "viral_content"],
            ScoreType.REVENUE_GENERATED: ["revenue_milestone", "monetization_success"],
            ScoreType.COLLABORATIONS: ["collaboration_success", "partnership_formed"],
            ScoreType.CONTENT_COUNT: ["content_upload"],
            ScoreType.INNOVATION_SCORE: ["innovation_usage", "feature_adoption"]
        }
        
        action_type = action_data.get("action_type", "")
        relevant = relevant_actions.get(leaderboard.score_type, [])
        
        return action_type in relevant or leaderboard.score_type == ScoreType.COMPOSITE
    
    async def _get_user_current_rankings(self, user_id: str) -> Dict[str, Any]:
        """Get user's current rankings across all leaderboards."""
        rankings = {}
        
        for leaderboard_id, leaderboard in self.leaderboards.items():
            if not leaderboard.is_active:
                continue
            
            # Get current leaderboard entries
            entries = await self._get_leaderboard_entries(leaderboard_id)
            
            # Find user's position
            for entry in entries:
                if entry.user_id == user_id:
                    rankings[leaderboard_id] = {
                        "rank": entry.rank,
                        "score": entry.score,
                        "rank_change": entry.rank_change,
                        "leaderboard_name": leaderboard.name,
                        "total_entries": len(entries)
                    }
                    break
        
        return rankings
    
    async def _get_leaderboard_entries(self, leaderboard_id: str) -> List[LeaderboardEntry]:
        """Get leaderboard entries with caching."""
        # Check cache first
        if (leaderboard_id in self._ranking_cache and 
            leaderboard_id in self._cache_expiry and
            datetime.utcnow() < self._cache_expiry[leaderboard_id]):
            return self._ranking_cache[leaderboard_id]
        
        # Rebuild leaderboard
        entries = await self._rebuild_leaderboard(leaderboard_id)
        
        # Cache results
        self._ranking_cache[leaderboard_id] = entries
        self._cache_expiry[leaderboard_id] = datetime.utcnow() + timedelta(minutes=30)
        
        return entries
    
    async def _rebuild_leaderboard(self, leaderboard_id: str) -> List[LeaderboardEntry]:
        """Rebuild leaderboard from scratch."""
        try:
            leaderboard = self.leaderboards[leaderboard_id]
            entries = []
            
            # Calculate scores for all users
            for user_id, scores in self.user_scores.items():
                score = await self._calculate_leaderboard_score(user_id, leaderboard)
                
                if score > 0:  # Only include users with positive scores
                    entry = LeaderboardEntry(
                        user_id=user_id,
                        username=f"User_{user_id[:8]}",  # Placeholder - would get from user service
                        score=score,
                        rank=0,  # Will be set after sorting
                        tier=self._get_user_tier(user_id),
                        badge_count=len(self._get_user_badges(user_id)),
                        achievement_count=len(self._get_user_achievements(user_id))
                    )
                    entries.append(entry)
            
            # Sort by score (descending)
            entries.sort(key=lambda x: x.score, reverse=True)
            
            # Assign ranks
            for i, entry in enumerate(entries):
                entry.rank = i + 1
            
            # Limit to max entries
            if len(entries) > leaderboard.max_entries:
                entries = entries[:leaderboard.max_entries]
            
            # Update leaderboard
            leaderboard.entries = entries
            leaderboard.last_updated = datetime.utcnow()
            
            return entries
            
        except Exception as e:
            self.logger.error(f"Error rebuilding leaderboard {leaderboard_id}: {e}")
            return []
    
    async def _calculate_leaderboard_score(
        self,
        user_id: str,
        leaderboard: Leaderboard
    ) -> float:
        """Calculate user's score for a specific leaderboard."""
        try:
            user_scores = self.user_scores.get(user_id, {})
            
            if leaderboard.score_type == ScoreType.COMPOSITE:
                # Weighted composite score
                score = 0.0
                for metric, weight in leaderboard.weights.items():
                    metric_value = user_scores.get(metric, 0)
                    score += metric_value * weight
                return score
            
            elif leaderboard.score_type == ScoreType.TOTAL_POINTS:
                return user_scores.get("total_points", 0)
            
            elif leaderboard.score_type == ScoreType.ENGAGEMENT_RATE:
                return user_scores.get("engagement_rate", 0) * 1000  # Scale for ranking
            
            elif leaderboard.score_type == ScoreType.REVENUE_GENERATED:
                return user_scores.get("revenue_generated", 0)
            
            elif leaderboard.score_type == ScoreType.COLLABORATIONS:
                return user_scores.get("collaboration_score", 0)
            
            elif leaderboard.score_type == ScoreType.CONTENT_COUNT:
                return user_scores.get("content_count", 0)
            
            elif leaderboard.score_type == ScoreType.INNOVATION_SCORE:
                return user_scores.get("innovation_score", 0)
            
            else:
                return 0.0
                
        except Exception as e:
            self.logger.error(f"Error calculating leaderboard score: {e}")
            return 0.0
    
    def _get_user_tier(self, user_id: str) -> str:
        """Get user's tier based on total points."""
        total_points = self.user_scores.get(user_id, {}).get("total_points", 0)
        
        if total_points >= 50000:
            return "Legendary"
        elif total_points >= 25000:
            return "Master"
        elif total_points >= 10000:
            return "Expert"
        elif total_points >= 5000:
            return "Advanced"
        elif total_points >= 1000:
            return "Intermediate"
        elif total_points >= 100:
            return "Beginner"
        else:
            return "Newcomer"
    
    def _get_user_badges(self, user_id: str) -> List[str]:
        """Get user's badges (placeholder - would integrate with badge system)."""
        # This would integrate with the badge system
        return []
    
    def _get_user_achievements(self, user_id: str) -> List[str]:
        """Get user's achievements (placeholder - would integrate with achievement system)."""
        # This would integrate with the achievement system
        return []
    
    async def get_user_rankings(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive ranking information for a user."""
        try:
            user_rankings = {}
            overall_stats = {
                "total_points": self.user_scores.get(user_id, {}).get("total_points", 0),
                "tier": self._get_user_tier(user_id),
                "global_percentile": 0.0
            }
            
            # Get rankings from all active leaderboards
            for leaderboard_id, leaderboard in self.leaderboards.items():
                if not leaderboard.is_active:
                    continue
                
                entries = await self._get_leaderboard_entries(leaderboard_id)
                
                # Find user's position
                user_entry = None
                for entry in entries:
                    if entry.user_id == user_id:
                        user_entry = entry
                        break
                
                if user_entry:
                    user_rankings[leaderboard_id] = {
                        "leaderboard_name": leaderboard.name,
                        "rank": user_entry.rank,
                        "score": user_entry.score,
                        "total_entries": len(entries),
                        "percentile": (1 - (user_entry.rank - 1) / len(entries)) * 100,
                        "rank_change": user_entry.rank_change,
                        "leaderboard_type": leaderboard.leaderboard_type.value
                    }
            
            # Calculate global percentile
            if "global_overall" in user_rankings:
                overall_stats["global_percentile"] = user_rankings["global_overall"]["percentile"]
            
            return {
                "user_id": user_id,
                "overall_stats": overall_stats,
                "leaderboard_rankings": user_rankings,
                "best_ranking": min([r["rank"] for r in user_rankings.values()]) if user_rankings else None,
                "top_categories": self._get_top_categories(user_rankings)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user rankings: {e}")
            return {}
    
    def _get_top_categories(self, user_rankings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get user's top performing categories."""
        try:
            category_rankings = []
            
            for ranking_data in user_rankings.values():
                if ranking_data["rank"] <= 10:  # Top 10 in any leaderboard
                    category_rankings.append({
                        "leaderboard": ranking_data["leaderboard_name"],
                        "rank": ranking_data["rank"],
                        "percentile": ranking_data["percentile"]
                    })
            
            # Sort by rank (best first)
            category_rankings.sort(key=lambda x: x["rank"])
            
            return category_rankings[:5]  # Top 5 categories
            
        except Exception:
            return []
    
    async def get_leaderboard(
        self,
        leaderboard_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get leaderboard data with pagination."""
        try:
            if leaderboard_id not in self.leaderboards:
                return {"error": "Leaderboard not found"}
            
            leaderboard = self.leaderboards[leaderboard_id]
            entries = await self._get_leaderboard_entries(leaderboard_id)
            
            # Apply pagination
            paginated_entries = entries[offset:offset + limit]
            
            # Format entries for response
            formatted_entries = []
            for entry in paginated_entries:
                formatted_entries.append({
                    "rank": entry.rank,
                    "user_id": entry.user_id,
                    "username": entry.username,
                    "score": entry.score,
                    "rank_change": entry.rank_change,
                    "tier": entry.tier,
                    "badge_count": entry.badge_count,
                    "achievement_count": entry.achievement_count,
                    "last_activity": entry.last_activity
                })
            
            return {
                "leaderboard_id": leaderboard_id,
                "name": leaderboard.name,
                "description": leaderboard.description,
                "type": leaderboard.leaderboard_type.value,
                "period": leaderboard.period.value,
                "entries": formatted_entries,
                "total_entries": len(entries),
                "last_updated": leaderboard.last_updated,
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "has_more": offset + limit < len(entries)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboard {leaderboard_id}: {e}")
            return {"error": str(e)}
    
    async def _background_update_task(self):
        """Background task to process leaderboard updates."""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                async with self._processing_lock:
                    if self._update_queue:
                        # Process updates in batches
                        batch_size = 100
                        updates_to_process = self._update_queue[:batch_size]
                        self._update_queue = self._update_queue[batch_size:]
                        
                        # Group updates by leaderboard
                        leaderboard_updates = defaultdict(list)
                        for update in updates_to_process:
                            leaderboard_updates[update["leaderboard_id"]].append(update)
                        
                        # Process each leaderboard
                        for leaderboard_id, updates in leaderboard_updates.items():
                            await self._process_leaderboard_updates(leaderboard_id, updates)
                
            except Exception as e:
                self.logger.error(f"Error in background update task: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _process_leaderboard_updates(
        self,
        leaderboard_id: str,
        updates: List[Dict[str, Any]]
    ):
        """Process pending updates for a specific leaderboard."""
        try:
            leaderboard = self.leaderboards.get(leaderboard_id)
            if not leaderboard or not leaderboard.is_active:
                return
            
            # Check if enough time has passed since last update
            time_since_update = datetime.utcnow() - leaderboard.last_updated
            if time_since_update < leaderboard.update_frequency:
                return
            
            # Invalidate cache to force rebuild
            if leaderboard_id in self._ranking_cache:
                del self._ranking_cache[leaderboard_id]
            
            # Rebuild leaderboard
            await self._rebuild_leaderboard(leaderboard_id)
            
            self.logger.debug(f"Processed {len(updates)} updates for leaderboard {leaderboard_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing leaderboard updates: {e}")
    
    async def get_leaderboard_statistics(self) -> Dict[str, Any]:
        """Get system-wide leaderboard statistics."""
        try:
            total_leaderboards = len(self.leaderboards)
            active_leaderboards = len([lb for lb in self.leaderboards.values() if lb.is_active])
            total_participants = len(self.user_scores)
            
            # Calculate average scores
            if total_participants > 0:
                avg_points = sum(scores.get("total_points", 0) for scores in self.user_scores.values()) / total_participants
                avg_engagement = sum(scores.get("engagement_rate", 0) for scores in self.user_scores.values()) / total_participants
            else:
                avg_points = avg_engagement = 0
            
            # Tier distribution
            tier_distribution = {}
            for user_id in self.user_scores:
                tier = self._get_user_tier(user_id)
                tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            
            return {
                "total_leaderboards": total_leaderboards,
                "active_leaderboards": active_leaderboards,
                "total_participants": total_participants,
                "average_points": avg_points,
                "average_engagement_rate": avg_engagement,
                "tier_distribution": tier_distribution,
                "pending_updates": len(self._update_queue)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboard statistics: {e}")
            return {}