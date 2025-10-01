#!/usr/bin/env python3
"""
IA Chéries Platform - Gamification Monitoring Engine
===============================================

Enterprise-grade gamification monitoring engine for Creator Economy platform.
Tracks achievement system performance, leaderboard accuracy, reward distribution,
creator engagement gamification metrics, and badge system analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Types of achievements in gamification system"""
    CONTENT_MILESTONE = "content_milestone"
    ENGAGEMENT_GOAL = "engagement_goal"
    REVENUE_TARGET = "revenue_target"
    COLLABORATION_SUCCESS = "collaboration_success"
    SKILL_MASTERY = "skill_mastery"
    CONSISTENCY_STREAK = "consistency_streak"
    INNOVATION_AWARD = "innovation_award"
    COMMUNITY_LEADER = "community_leader"

class RewardType(Enum):
    """Types of rewards in gamification system"""
    BADGE = "badge"
    POINTS = "points"
    EXCLUSIVE_ACCESS = "exclusive_access"
    MONETARY = "monetary"
    RECOGNITION = "recognition"
    FEATURE_UNLOCK = "feature_unlock"
    PREMIUM_BENEFITS = "premium_benefits"
    MENTORSHIP = "mentorship"

class LeaderboardCategory(Enum):
    """Leaderboard categories"""
    OVERALL_PERFORMANCE = "overall_performance"
    CONTENT_QUALITY = "content_quality"
    ENGAGEMENT_RATE = "engagement_rate"
    REVENUE_GENERATED = "revenue_generated"
    COLLABORATION_SUCCESS = "collaboration_success"
    COMMUNITY_CONTRIBUTION = "community_contribution"
    INNOVATION_SCORE = "innovation_score"
    CONSISTENCY_RATING = "consistency_rating"

@dataclass
class AchievementMetrics:
    """Achievement system performance metrics"""
    achievement_id: str
    creator_id: str
    achievement_type: AchievementType
    achievement_name: str
    description: str
    completion_rate: float
    time_to_complete: Optional[float] = None
    difficulty_level: int = 1
    reward_claimed: bool = False
    engagement_boost: float = 0.0
    satisfaction_rating: float = 0.0
    completion_date: Optional[datetime] = None
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class LeaderboardMetrics:
    """Leaderboard accuracy and performance metrics"""
    leaderboard_id: str
    category: LeaderboardCategory
    total_participants: int
    update_frequency_minutes: int
    accuracy_score: float
    data_freshness_score: float
    user_engagement_rate: float
    position_changes: Dict[str, int]
    top_performers: List[str]
    calculation_latency_ms: float
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class RewardDistributionMetrics:
    """Reward distribution effectiveness metrics"""
    reward_id: str
    creator_id: str
    reward_type: RewardType
    reward_value: float
    distribution_time: datetime
    claim_time: Optional[datetime] = None
    time_to_claim_hours: Optional[float] = None
    satisfaction_rating: float = 0.0
    engagement_impact: float = 0.0
    retention_impact: float = 0.0
    conversion_impact: float = 0.0
    cost_effectiveness: float = 0.0

@dataclass
class GamificationEngagementMetrics:
    """Creator engagement with gamification features"""
    creator_id: str
    daily_gamification_interactions: int
    achievement_participation_rate: float
    leaderboard_check_frequency: int
    reward_claim_rate: float
    gamification_satisfaction_score: float
    feature_usage_breakdown: Dict[str, int]
    progression_velocity: float
    competitive_engagement_level: float
    social_sharing_rate: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class GamificationMonitoringEngine:
    """
    Enterprise gamification monitoring engine for Creator Economy platform.
    
    Capabilities:
    - Achievement system performance tracking
    - Leaderboard accuracy monitoring
    - Reward distribution effectiveness analysis
    - Creator engagement gamification metrics
    - Badge system performance analytics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.achievement_metrics: Dict[str, AchievementMetrics] = {}
        self.leaderboard_metrics: Dict[str, LeaderboardMetrics] = {}
        self.reward_metrics: Dict[str, RewardDistributionMetrics] = {}
        self.engagement_metrics: Dict[str, List[GamificationEngagementMetrics]] = defaultdict(list)
        self.monitoring_active = False
        
        # Initialize gamification monitoring systems
        self._initialize_achievement_tracking()
        self._initialize_leaderboard_monitoring()
        self._initialize_reward_analytics()
        self._initialize_engagement_tracking()
        
        logger.info("GamificationMonitoringEngine initialized successfully")
    
    def _initialize_achievement_tracking(self):
        """Initialize achievement system tracking."""
        self.achievement_definitions = {
            AchievementType.CONTENT_MILESTONE: [
                {"name": "First Upload", "threshold": 1, "difficulty": 1},
                {"name": "Content Creator", "threshold": 10, "difficulty": 2},
                {"name": "Prolific Producer", "threshold": 50, "difficulty": 3},
                {"name": "Content Master", "threshold": 100, "difficulty": 4},
                {"name": "Legendary Creator", "threshold": 500, "difficulty": 5}
            ],
            AchievementType.ENGAGEMENT_GOAL: [
                {"name": "First Like", "threshold": 1, "difficulty": 1},
                {"name": "Popular Creator", "threshold": 1000, "difficulty": 2},
                {"name": "Viral Star", "threshold": 10000, "difficulty": 3},
                {"name": "Engagement King", "threshold": 100000, "difficulty": 4},
                {"name": "Global Influencer", "threshold": 1000000, "difficulty": 5}
            ],
            AchievementType.REVENUE_TARGET: [
                {"name": "First Earning", "threshold": 1, "difficulty": 1},
                {"name": "Profitable Creator", "threshold": 100, "difficulty": 2},
                {"name": "Revenue Generator", "threshold": 1000, "difficulty": 3},
                {"name": "Business Builder", "threshold": 10000, "difficulty": 4},
                {"name": "Empire Creator", "threshold": 100000, "difficulty": 5}
            ]
        }
        
        self.achievement_rewards = {
            1: {"points": 100, "badge": "bronze"},
            2: {"points": 250, "badge": "silver"},
            3: {"points": 500, "badge": "gold"},
            4: {"points": 1000, "badge": "platinum", "exclusive_access": True},
            5: {"points": 2500, "badge": "diamond", "monetary": 100, "premium_benefits": True}
        }
    
    def _initialize_leaderboard_monitoring(self):
        """Initialize leaderboard monitoring systems."""
        self.leaderboard_configs = {
            LeaderboardCategory.OVERALL_PERFORMANCE: {
                "update_frequency": 60,  # minutes
                "max_participants": 1000,
                "calculation_weights": {
                    "content_quality": 0.3,
                    "engagement": 0.25,
                    "revenue": 0.2,
                    "consistency": 0.15,
                    "collaboration": 0.1
                }
            },
            LeaderboardCategory.CONTENT_QUALITY: {
                "update_frequency": 30,
                "max_participants": 500,
                "calculation_weights": {
                    "seo_score": 0.4,
                    "engagement_rate": 0.3,
                    "originality": 0.2,
                    "technical_quality": 0.1
                }
            },
            LeaderboardCategory.REVENUE_GENERATED: {
                "update_frequency": 120,
                "max_participants": 200,
                "calculation_weights": {
                    "total_revenue": 0.5,
                    "revenue_growth": 0.3,
                    "monetization_efficiency": 0.2
                }
            }
        }
        
        self.leaderboard_cache = {}
        self.position_history = defaultdict(list)
    
    def _initialize_reward_analytics(self):
        """Initialize reward distribution analytics."""
        self.reward_effectiveness_thresholds = {
            "high_engagement_impact": 0.15,
            "medium_engagement_impact": 0.08,
            "high_retention_impact": 0.20,
            "high_satisfaction": 4.5,
            "cost_effectiveness_target": 2.0
        }
        
        self.reward_budgets = {
            RewardType.POINTS: {"daily_budget": 100000, "cost_per_unit": 0.001},
            RewardType.MONETARY: {"daily_budget": 5000, "cost_per_unit": 1.0},
            RewardType.BADGE: {"daily_budget": 1000, "cost_per_unit": 0.1},
            RewardType.EXCLUSIVE_ACCESS: {"daily_budget": 100, "cost_per_unit": 5.0},
            RewardType.PREMIUM_BENEFITS: {"daily_budget": 50, "cost_per_unit": 20.0}
        }
    
    def _initialize_engagement_tracking(self):
        """Initialize gamification engagement tracking."""
        self.engagement_features = [
            "achievement_browser",
            "leaderboard_viewer",
            "reward_center",
            "progress_tracker",
            "social_sharing",
            "challenge_participation",
            "badge_showcase",
            "point_spending"
        ]
        
        self.engagement_benchmarks = {
            "daily_interactions_target": 5,
            "achievement_participation_target": 0.7,
            "leaderboard_engagement_target": 0.4,
            "reward_claim_target": 0.9,
            "satisfaction_target": 4.0
        }
    
    async def start_monitoring(self):
        """Start gamification monitoring engine."""
        if self.monitoring_active:
            logger.warning("Gamification monitoring already active")
            return
        
        self.monitoring_active = True
        logger.info("Starting gamification monitoring engine...")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_achievement_performance()),
            asyncio.create_task(self._monitor_leaderboard_accuracy()),
            asyncio.create_task(self._monitor_reward_distribution()),
            asyncio.create_task(self._track_engagement_metrics()),
            asyncio.create_task(self._analyze_gamification_effectiveness()),
            asyncio.create_task(self._optimize_reward_systems())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in gamification monitoring: {e}")
            self.monitoring_active = False
            raise
    
    async def stop_monitoring(self):
        """Stop gamification monitoring engine."""
        self.monitoring_active = False
        logger.info("Gamification monitoring engine stopped")
    
    async def track_achievement_completion(self, achievement_data: Dict[str, Any]) -> str:
        """Track achievement completion and performance."""
        achievement_id = achievement_data.get('achievement_id', str(uuid.uuid4()))
        
        metrics = AchievementMetrics(
            achievement_id=achievement_id,
            creator_id=achievement_data.get('creator_id', ''),
            achievement_type=AchievementType(achievement_data.get('type', 'content_milestone')),
            achievement_name=achievement_data.get('name', ''),
            description=achievement_data.get('description', ''),
            completion_rate=achievement_data.get('completion_rate', 1.0),
            time_to_complete=achievement_data.get('time_to_complete_hours'),
            difficulty_level=achievement_data.get('difficulty', 1),
            reward_claimed=achievement_data.get('reward_claimed', False),
            engagement_boost=achievement_data.get('engagement_boost', 0.0),
            satisfaction_rating=achievement_data.get('satisfaction_rating', 0.0),
            completion_date=datetime.now(timezone.utc)
        )
        
        self.achievement_metrics[achievement_id] = metrics
        await self._analyze_achievement_impact(achievement_id)
        
        logger.info(f"Tracked achievement completion: {achievement_id}")
        return achievement_id
    
    async def update_leaderboard_metrics(self, leaderboard_data: Dict[str, Any]):
        """Update leaderboard performance metrics."""
        leaderboard_id = leaderboard_data.get('leaderboard_id')
        category = LeaderboardCategory(leaderboard_data.get('category'))
        
        metrics = LeaderboardMetrics(
            leaderboard_id=leaderboard_id,
            category=category,
            total_participants=leaderboard_data.get('total_participants', 0),
            update_frequency_minutes=leaderboard_data.get('update_frequency', 60),
            accuracy_score=leaderboard_data.get('accuracy_score', 0.0),
            data_freshness_score=leaderboard_data.get('freshness_score', 0.0),
            user_engagement_rate=leaderboard_data.get('engagement_rate', 0.0),
            position_changes=leaderboard_data.get('position_changes', {}),
            top_performers=leaderboard_data.get('top_performers', []),
            calculation_latency_ms=leaderboard_data.get('latency_ms', 0.0)
        )
        
        self.leaderboard_metrics[leaderboard_id] = metrics
        await self._track_leaderboard_changes(leaderboard_id, metrics)
        
        logger.info(f"Updated leaderboard metrics: {leaderboard_id}")
    
    async def track_reward_distribution(self, reward_data: Dict[str, Any]) -> str:
        """Track reward distribution effectiveness."""
        reward_id = reward_data.get('reward_id', str(uuid.uuid4()))
        
        metrics = RewardDistributionMetrics(
            reward_id=reward_id,
            creator_id=reward_data.get('creator_id', ''),
            reward_type=RewardType(reward_data.get('type', 'points')),
            reward_value=reward_data.get('value', 0.0),
            distribution_time=datetime.fromisoformat(reward_data.get('distribution_time', datetime.now(timezone.utc).isoformat())),
            claim_time=datetime.fromisoformat(reward_data['claim_time']) if reward_data.get('claim_time') else None,
            satisfaction_rating=reward_data.get('satisfaction_rating', 0.0),
            engagement_impact=reward_data.get('engagement_impact', 0.0),
            retention_impact=reward_data.get('retention_impact', 0.0),
            conversion_impact=reward_data.get('conversion_impact', 0.0),
            cost_effectiveness=reward_data.get('cost_effectiveness', 0.0)
        )
        
        # Calculate time to claim if claim time provided
        if metrics.claim_time:
            metrics.time_to_claim_hours = (metrics.claim_time - metrics.distribution_time).total_seconds() / 3600
        
        self.reward_metrics[reward_id] = metrics
        await self._analyze_reward_effectiveness(reward_id)
        
        logger.info(f"Tracked reward distribution: {reward_id}")
        return reward_id
    
    async def update_creator_engagement(self, engagement_data: Dict[str, Any]):
        """Update creator gamification engagement metrics."""
        creator_id = engagement_data.get('creator_id')
        
        metrics = GamificationEngagementMetrics(
            creator_id=creator_id,
            daily_gamification_interactions=engagement_data.get('daily_interactions', 0),
            achievement_participation_rate=engagement_data.get('achievement_participation', 0.0),
            leaderboard_check_frequency=engagement_data.get('leaderboard_checks', 0),
            reward_claim_rate=engagement_data.get('reward_claim_rate', 0.0),
            gamification_satisfaction_score=engagement_data.get('satisfaction_score', 0.0),
            feature_usage_breakdown=engagement_data.get('feature_usage', {}),
            progression_velocity=engagement_data.get('progression_velocity', 0.0),
            competitive_engagement_level=engagement_data.get('competitive_level', 0.0),
            social_sharing_rate=engagement_data.get('social_sharing_rate', 0.0)
        )
        
        self.engagement_metrics[creator_id].append(metrics)
        
        # Keep only recent engagement data (last 30 days)
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=30)
        self.engagement_metrics[creator_id] = [
            m for m in self.engagement_metrics[creator_id]
            if m.timestamp > cutoff_time
        ]
        
        logger.info(f"Updated engagement metrics for creator: {creator_id}")
    
    async def _monitor_achievement_performance(self):
        """Monitor achievement system performance."""
        while self.monitoring_active:
            try:
                # Analyze achievement completion rates
                achievement_stats = await self._calculate_achievement_statistics()
                
                # Check for underperforming achievements
                for achievement_type, stats in achievement_stats.items():
                    if stats.get('completion_rate', 0) < 0.1:  # Less than 10%
                        await self._trigger_achievement_alert("low_completion", achievement_type, stats)
                    
                    if stats.get('avg_satisfaction', 0) < 3.0:  # Low satisfaction
                        await self._trigger_achievement_alert("low_satisfaction", achievement_type, stats)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error monitoring achievement performance: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_leaderboard_accuracy(self):
        """Monitor leaderboard accuracy and performance."""
        while self.monitoring_active:
            try:
                for leaderboard_id, metrics in self.leaderboard_metrics.items():
                    # Check accuracy thresholds
                    if metrics.accuracy_score < 0.95:
                        await self._trigger_leaderboard_alert("low_accuracy", leaderboard_id, metrics)
                    
                    # Check data freshness
                    if metrics.data_freshness_score < 0.8:
                        await self._trigger_leaderboard_alert("stale_data", leaderboard_id, metrics)
                    
                    # Check calculation latency
                    if metrics.calculation_latency_ms > 5000:  # 5 seconds
                        await self._trigger_leaderboard_alert("high_latency", leaderboard_id, metrics)
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring leaderboard accuracy: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_reward_distribution(self):
        """Monitor reward distribution effectiveness."""
        while self.monitoring_active:
            try:
                # Analyze reward effectiveness
                reward_stats = await self._calculate_reward_statistics()
                
                # Check budget utilization
                budget_utilization = await self._calculate_budget_utilization()
                
                # Check for underperforming rewards
                for reward_type, stats in reward_stats.items():
                    if stats.get('cost_effectiveness', 0) < self.reward_effectiveness_thresholds["cost_effectiveness_target"]:
                        await self._trigger_reward_alert("low_effectiveness", reward_type, stats)
                    
                    if stats.get('claim_rate', 0) < 0.8:  # Less than 80% claim rate
                        await self._trigger_reward_alert("low_claim_rate", reward_type, stats)
                
                await asyncio.sleep(7200)  # Check every 2 hours
                
            except Exception as e:
                logger.error(f"Error monitoring reward distribution: {e}")
                await asyncio.sleep(300)
    
    async def _track_engagement_metrics(self):
        """Track creator engagement with gamification features."""
        while self.monitoring_active:
            try:
                for creator_id, engagement_list in self.engagement_metrics.items():
                    if engagement_list:
                        latest_engagement = engagement_list[-1]
                        
                        # Check engagement thresholds
                        if latest_engagement.daily_gamification_interactions < self.engagement_benchmarks["daily_interactions_target"]:
                            await self._trigger_engagement_alert("low_interactions", creator_id, latest_engagement)
                        
                        if latest_engagement.gamification_satisfaction_score < self.engagement_benchmarks["satisfaction_target"]:
                            await self._trigger_engagement_alert("low_satisfaction", creator_id, latest_engagement)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error tracking engagement metrics: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_gamification_effectiveness(self):
        """Analyze overall gamification system effectiveness."""
        while self.monitoring_active:
            try:
                effectiveness_report = {
                    "achievement_system": await self._evaluate_achievement_system(),
                    "leaderboard_system": await self._evaluate_leaderboard_system(),
                    "reward_system": await self._evaluate_reward_system(),
                    "overall_engagement": await self._evaluate_overall_engagement()
                }
                
                # Generate insights and recommendations
                insights = await self._generate_gamification_insights(effectiveness_report)
                
                logger.info(f"Gamification effectiveness analysis completed: {json.dumps(insights, default=str)}")
                
                await asyncio.sleep(86400)  # Analyze daily
                
            except Exception as e:
                logger.error(f"Error analyzing gamification effectiveness: {e}")
                await asyncio.sleep(300)
    
    async def _optimize_reward_systems(self):
        """Optimize reward distribution based on performance data."""
        while self.monitoring_active:
            try:
                # Analyze reward performance
                optimization_data = await self._analyze_reward_optimization_opportunities()
                
                # Apply optimizations
                await self._apply_reward_optimizations(optimization_data)
                
                await asyncio.sleep(43200)  # Optimize every 12 hours
                
            except Exception as e:
                logger.error(f"Error optimizing reward systems: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_achievement_impact(self, achievement_id: str):
        """Analyze impact of specific achievement completion."""
        metrics = self.achievement_metrics.get(achievement_id)
        if not metrics:
            return
        
        impact_analysis = {
            "achievement_id": achievement_id,
            "creator_id": metrics.creator_id,
            "engagement_boost": metrics.engagement_boost,
            "satisfaction_rating": metrics.satisfaction_rating,
            "difficulty_vs_satisfaction": metrics.satisfaction_rating / metrics.difficulty_level if metrics.difficulty_level > 0 else 0,
            "time_efficiency": metrics.difficulty_level / metrics.time_to_complete if metrics.time_to_complete and metrics.time_to_complete > 0 else 0
        }
        
        logger.info(f"Achievement impact analysis: {impact_analysis}")
    
    async def _track_leaderboard_changes(self, leaderboard_id: str, metrics: LeaderboardMetrics):
        """Track leaderboard position changes."""
        # Store position history
        position_snapshot = {
            "timestamp": datetime.now(timezone.utc),
            "top_performers": metrics.top_performers,
            "position_changes": metrics.position_changes
        }
        
        self.position_history[leaderboard_id].append(position_snapshot)
        
        # Keep only recent history (last 30 days)
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=30)
        self.position_history[leaderboard_id] = [
            snapshot for snapshot in self.position_history[leaderboard_id]
            if snapshot["timestamp"] > cutoff_time
        ]
    
    async def _analyze_reward_effectiveness(self, reward_id: str):
        """Analyze effectiveness of specific reward distribution."""
        metrics = self.reward_metrics.get(reward_id)
        if not metrics:
            return
        
        effectiveness_score = (
            metrics.engagement_impact * 0.3 +
            metrics.retention_impact * 0.3 +
            metrics.satisfaction_rating / 5.0 * 0.2 +
            metrics.cost_effectiveness * 0.2
        )
        
        analysis = {
            "reward_id": reward_id,
            "reward_type": metrics.reward_type.value,
            "effectiveness_score": effectiveness_score,
            "time_to_claim": metrics.time_to_claim_hours,
            "impact_summary": {
                "engagement": metrics.engagement_impact,
                "retention": metrics.retention_impact,
                "satisfaction": metrics.satisfaction_rating,
                "cost_effectiveness": metrics.cost_effectiveness
            }
        }
        
        logger.info(f"Reward effectiveness analysis: {analysis}")
    
    async def _calculate_achievement_statistics(self) -> Dict[str, Any]:
        """Calculate achievement system statistics."""
        stats = {}
        
        for achievement_type in AchievementType:
            type_achievements = [
                m for m in self.achievement_metrics.values()
                if m.achievement_type == achievement_type
            ]
            
            if type_achievements:
                stats[achievement_type.value] = {
                    "total_completions": len(type_achievements),
                    "avg_completion_rate": sum(m.completion_rate for m in type_achievements) / len(type_achievements),
                    "avg_satisfaction": sum(m.satisfaction_rating for m in type_achievements) / len(type_achievements),
                    "avg_time_to_complete": sum(m.time_to_complete or 0 for m in type_achievements) / len(type_achievements),
                    "reward_claim_rate": sum(1 for m in type_achievements if m.reward_claimed) / len(type_achievements)
                }
        
        return stats
    
    async def _calculate_reward_statistics(self) -> Dict[str, Any]:
        """Calculate reward distribution statistics."""
        stats = {}
        
        for reward_type in RewardType:
            type_rewards = [
                m for m in self.reward_metrics.values()
                if m.reward_type == reward_type
            ]
            
            if type_rewards:
                claimed_rewards = [m for m in type_rewards if m.claim_time is not None]
                
                stats[reward_type.value] = {
                    "total_distributed": len(type_rewards),
                    "claim_rate": len(claimed_rewards) / len(type_rewards),
                    "avg_time_to_claim": sum(m.time_to_claim_hours or 0 for m in claimed_rewards) / len(claimed_rewards) if claimed_rewards else 0,
                    "avg_satisfaction": sum(m.satisfaction_rating for m in type_rewards) / len(type_rewards),
                    "avg_engagement_impact": sum(m.engagement_impact for m in type_rewards) / len(type_rewards),
                    "avg_cost_effectiveness": sum(m.cost_effectiveness for m in type_rewards) / len(type_rewards)
                }
        
        return stats
    
    async def _calculate_budget_utilization(self) -> Dict[str, float]:
        """Calculate reward budget utilization."""
        utilization = {}
        
        for reward_type, budget_info in self.reward_budgets.items():
            type_rewards = [
                m for m in self.reward_metrics.values()
                if m.reward_type == reward_type and 
                m.distribution_time.date() == datetime.now(timezone.utc).date()  # Today's rewards
            ]
            
            total_cost = sum(m.reward_value * budget_info["cost_per_unit"] for m in type_rewards)
            utilization[reward_type.value] = total_cost / budget_info["daily_budget"]
        
        return utilization
    
    async def _evaluate_achievement_system(self) -> Dict[str, Any]:
        """Evaluate achievement system performance."""
        total_achievements = len(self.achievement_metrics)
        completed_achievements = len([m for m in self.achievement_metrics.values() if m.completion_rate >= 1.0])
        
        return {
            "total_achievements": total_achievements,
            "completion_rate": completed_achievements / total_achievements if total_achievements > 0 else 0,
            "avg_satisfaction": sum(m.satisfaction_rating for m in self.achievement_metrics.values()) / total_achievements if total_achievements > 0 else 0,
            "engagement_impact": sum(m.engagement_boost for m in self.achievement_metrics.values()) / total_achievements if total_achievements > 0 else 0
        }
    
    async def _evaluate_leaderboard_system(self) -> Dict[str, Any]:
        """Evaluate leaderboard system performance."""
        total_leaderboards = len(self.leaderboard_metrics)
        
        if total_leaderboards == 0:
            return {"status": "no_data"}
        
        return {
            "total_leaderboards": total_leaderboards,
            "avg_accuracy": sum(m.accuracy_score for m in self.leaderboard_metrics.values()) / total_leaderboards,
            "avg_engagement": sum(m.user_engagement_rate for m in self.leaderboard_metrics.values()) / total_leaderboards,
            "avg_latency": sum(m.calculation_latency_ms for m in self.leaderboard_metrics.values()) / total_leaderboards
        }
    
    async def _evaluate_reward_system(self) -> Dict[str, Any]:
        """Evaluate reward system performance."""
        total_rewards = len(self.reward_metrics)
        claimed_rewards = len([m for m in self.reward_metrics.values() if m.claim_time is not None])
        
        return {
            "total_rewards_distributed": total_rewards,
            "claim_rate": claimed_rewards / total_rewards if total_rewards > 0 else 0,
            "avg_satisfaction": sum(m.satisfaction_rating for m in self.reward_metrics.values()) / total_rewards if total_rewards > 0 else 0,
            "avg_cost_effectiveness": sum(m.cost_effectiveness for m in self.reward_metrics.values()) / total_rewards if total_rewards > 0 else 0
        }
    
    async def _evaluate_overall_engagement(self) -> Dict[str, Any]:
        """Evaluate overall gamification engagement."""
        total_creators = len(self.engagement_metrics)
        
        if total_creators == 0:
            return {"status": "no_data"}
        
        recent_engagement = []
        for creator_engagement_list in self.engagement_metrics.values():
            if creator_engagement_list:
                recent_engagement.append(creator_engagement_list[-1])
        
        if not recent_engagement:
            return {"status": "no_recent_data"}
        
        return {
            "active_creators": len(recent_engagement),
            "avg_daily_interactions": sum(e.daily_gamification_interactions for e in recent_engagement) / len(recent_engagement),
            "avg_satisfaction": sum(e.gamification_satisfaction_score for e in recent_engagement) / len(recent_engagement),
            "avg_participation_rate": sum(e.achievement_participation_rate for e in recent_engagement) / len(recent_engagement)
        }
    
    async def _generate_gamification_insights(self, effectiveness_report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights and recommendations for gamification system."""
        insights = {
            "performance_summary": effectiveness_report,
            "recommendations": [],
            "optimization_opportunities": [],
            "risk_areas": []
        }
        
        # Generate recommendations based on performance
        achievement_data = effectiveness_report.get("achievement_system", {})
        if achievement_data.get("completion_rate", 0) < 0.3:
            insights["recommendations"].append("Reduce achievement difficulty or improve reward values")
        
        leaderboard_data = effectiveness_report.get("leaderboard_system", {})
        if leaderboard_data.get("avg_accuracy", 0) < 0.95:
            insights["recommendations"].append("Improve leaderboard calculation accuracy")
        
        reward_data = effectiveness_report.get("reward_system", {})
        if reward_data.get("claim_rate", 0) < 0.8:
            insights["recommendations"].append("Simplify reward claiming process")
        
        return insights
    
    async def _analyze_reward_optimization_opportunities(self) -> Dict[str, Any]:
        """Analyze opportunities for reward system optimization."""
        reward_stats = await self._calculate_reward_statistics()
        budget_utilization = await self._calculate_budget_utilization()
        
        optimization_data = {
            "underperforming_rewards": [],
            "overperforming_rewards": [],
            "budget_adjustments": [],
            "timing_optimizations": []
        }
        
        for reward_type, stats in reward_stats.items():
            if stats.get("avg_cost_effectiveness", 0) < 1.5:
                optimization_data["underperforming_rewards"].append({
                    "type": reward_type,
                    "issue": "low_cost_effectiveness",
                    "current_value": stats.get("avg_cost_effectiveness", 0)
                })
            
            if stats.get("claim_rate", 0) < 0.7:
                optimization_data["underperforming_rewards"].append({
                    "type": reward_type,
                    "issue": "low_claim_rate",
                    "current_value": stats.get("claim_rate", 0)
                })
        
        return optimization_data
    
    async def _apply_reward_optimizations(self, optimization_data: Dict[str, Any]):
        """Apply reward system optimizations."""
        # In production, this would trigger system adjustments
        logger.info(f"Applied reward optimizations: {optimization_data}")
    
    async def _trigger_achievement_alert(self, alert_type: str, achievement_type: str, stats: Dict[str, Any]):
        """Trigger achievement system alert."""
        alert_data = {
            "type": f"achievement_{alert_type}",
            "achievement_type": achievement_type,
            "statistics": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.warning(f"Achievement alert ({alert_type}): {alert_data}")
    
    async def _trigger_leaderboard_alert(self, alert_type: str, leaderboard_id: str, metrics: LeaderboardMetrics):
        """Trigger leaderboard system alert."""
        alert_data = {
            "type": f"leaderboard_{alert_type}",
            "leaderboard_id": leaderboard_id,
            "category": metrics.category.value,
            "metric_value": getattr(metrics, alert_type.replace("_", ""), 0),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.warning(f"Leaderboard alert ({alert_type}): {alert_data}")
    
    async def _trigger_reward_alert(self, alert_type: str, reward_type: str, stats: Dict[str, Any]):
        """Trigger reward system alert."""
        alert_data = {
            "type": f"reward_{alert_type}",
            "reward_type": reward_type,
            "statistics": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.warning(f"Reward alert ({alert_type}): {alert_data}")
    
    async def _trigger_engagement_alert(self, alert_type: str, creator_id: str, engagement: GamificationEngagementMetrics):
        """Trigger engagement alert."""
        alert_data = {
            "type": f"engagement_{alert_type}",
            "creator_id": creator_id,
            "engagement_metrics": asdict(engagement),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.warning(f"Engagement alert ({alert_type}): {alert_data}")
    
    async def get_gamification_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive gamification monitoring dashboard data."""
        return {
            "achievement_system": {
                "total_achievements": len(self.achievement_metrics),
                "completion_rate": len([m for m in self.achievement_metrics.values() if m.completion_rate >= 1.0]) / len(self.achievement_metrics) if self.achievement_metrics else 0,
                "avg_satisfaction": sum(m.satisfaction_rating for m in self.achievement_metrics.values()) / len(self.achievement_metrics) if self.achievement_metrics else 0
            },
            "leaderboard_system": {
                "total_leaderboards": len(self.leaderboard_metrics),
                "avg_accuracy": sum(m.accuracy_score for m in self.leaderboard_metrics.values()) / len(self.leaderboard_metrics) if self.leaderboard_metrics else 0,
                "avg_engagement": sum(m.user_engagement_rate for m in self.leaderboard_metrics.values()) / len(self.leaderboard_metrics) if self.leaderboard_metrics else 0
            },
            "reward_system": {
                "total_rewards": len(self.reward_metrics),
                "claim_rate": len([m for m in self.reward_metrics.values() if m.claim_time]) / len(self.reward_metrics) if self.reward_metrics else 0,
                "avg_satisfaction": sum(m.satisfaction_rating for m in self.reward_metrics.values()) / len(self.reward_metrics) if self.reward_metrics else 0
            },
            "creator_engagement": {
                "active_creators": len(self.engagement_metrics),
                "avg_daily_interactions": sum(
                    e[-1].daily_gamification_interactions for e in self.engagement_metrics.values() if e
                ) / len([e for e in self.engagement_metrics.values() if e]) if any(self.engagement_metrics.values()) else 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on gamification monitoring systems."""
        return {
            "status": "healthy" if self.monitoring_active else "inactive",
            "achievement_metrics_tracked": len(self.achievement_metrics),
            "leaderboard_metrics_tracked": len(self.leaderboard_metrics),
            "reward_metrics_tracked": len(self.reward_metrics),
            "creator_engagement_tracked": len(self.engagement_metrics),
            "last_check": datetime.now(timezone.utc).isoformat()
        }

# Global gamification monitoring instance
gamification_monitoring_engine = GamificationMonitoringEngine()

async def main():
    """Main function for testing gamification monitoring."""
    engine = GamificationMonitoringEngine()
    
    # Test achievement tracking
    achievement_data = {
        'achievement_id': 'achievement_001',
        'creator_id': 'creator_1',
        'type': 'content_milestone',
        'name': 'First Upload',
        'description': 'Complete your first content upload',
        'completion_rate': 1.0,
        'time_to_complete_hours': 2.5,
        'difficulty': 1,
        'reward_claimed': True,
        'engagement_boost': 0.15,
        'satisfaction_rating': 4.5
    }
    
    await engine.track_achievement_completion(achievement_data)
    
    # Test reward tracking
    reward_data = {
        'reward_id': 'reward_001',
        'creator_id': 'creator_1',
        'type': 'points',
        'value': 100,
        'distribution_time': datetime.now(timezone.utc).isoformat(),
        'claim_time': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        'satisfaction_rating': 4.0,
        'engagement_impact': 0.10,
        'cost_effectiveness': 2.5
    }
    
    await engine.track_reward_distribution(reward_data)
    
    # Get dashboard data
    dashboard = await engine.get_gamification_dashboard_data()
    print(f"Dashboard data: {json.dumps(dashboard, indent=2, default=str)}")
    
    # Health check
    health = await engine.health_check()
    print(f"Health check: {json.dumps(health, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())