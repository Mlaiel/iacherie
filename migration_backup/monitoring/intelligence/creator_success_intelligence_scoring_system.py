"""Creator Success Intelligence Scoring System
==========================================

Enterprise-grade Creator Success Intelligence system providing comprehensive
success scoring, intelligent performance evaluation, and advanced success
analytics for the IA Chéries Creator Economy. Implements sophisticated scoring
algorithms, success prediction, and intelligent optimization recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team technical training included
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import math

# Optional imports for enhanced functionality
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Mock numpy for basic operations
    np = type('MockNumpy', (), {
        'array': lambda x: list(x) if hasattr(x, '__iter__') else [x],
        'mean': lambda x: sum(x) / len(x) if x else 0,
        'std': lambda x: (sum((i - sum(x)/len(x))**2 for i in x) / len(x))**0.5 if x else 0,
        'random': type('Random', (), {'rand': lambda: __import__('random').random()})(),
        'percentile': lambda x, p: sorted(x)[int(len(x) * p / 100)] if x else 0,
        'corrcoef': lambda x, y: 0.5  # Mock correlation
    })()

logger = logging.getLogger(__name__)

class SuccessMetricType(Enum):
    """Types of success metrics"""
    ENGAGEMENT_SUCCESS = "engagement_success"
    GROWTH_SUCCESS = "growth_success"
    REVENUE_SUCCESS = "revenue_success"
    CONTENT_SUCCESS = "content_success"
    COLLABORATION_SUCCESS = "collaboration_success"
    INNOVATION_SUCCESS = "innovation_success"
    CONSISTENCY_SUCCESS = "consistency_success"
    COMMUNITY_SUCCESS = "community_success"
    BRAND_SUCCESS = "brand_success"
    INFLUENCE_SUCCESS = "influence_success"

class SuccessLevel(Enum):
    """Success level categories"""
    EMERGING = "emerging"
    DEVELOPING = "developing"
    ESTABLISHED = "established"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    LEGEND = "legend"

class ScoreCategory(Enum):
    """Score categories for detailed analysis"""
    AUDIENCE_ENGAGEMENT = "audience_engagement"
    CONTENT_QUALITY = "content_quality"
    GROWTH_VELOCITY = "growth_velocity"
    MONETIZATION_EFFICIENCY = "monetization_efficiency"
    PLATFORM_MASTERY = "platform_mastery"
    COLLABORATION_IMPACT = "collaboration_impact"
    INNOVATION_INDEX = "innovation_index"
    CONSISTENCY_SCORE = "consistency_score"
    INFLUENCE_REACH = "influence_reach"
    BRAND_STRENGTH = "brand_strength"

class BenchmarkType(Enum):
    """Types of benchmarks for comparison"""
    PEER_COMPARISON = "peer_comparison"
    INDUSTRY_AVERAGE = "industry_average"
    TOP_PERFORMERS = "top_performers"
    HISTORICAL_SELF = "historical_self"
    PLATFORM_LEADERS = "platform_leaders"

@dataclass
class SuccessMetric:
    """Individual success metric data"""
    metric_id: str
    creator_id: str
    metric_type: SuccessMetricType
    value: float
    timestamp: datetime
    weight: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)
    source: str = "system"
    verified: bool = False

@dataclass
class ScoreComponent:
    """Component of the overall success score"""
    category: ScoreCategory
    raw_score: float
    weighted_score: float
    weight: float
    percentile_rank: float
    benchmark_comparison: Dict[str, float] = field(default_factory=dict)
    contributing_factors: List[str] = field(default_factory=list)
    improvement_potential: float = 0.0

@dataclass
class SuccessScore:
    """Comprehensive success score for a creator"""
    score_id: str
    creator_id: str
    overall_score: float
    success_level: SuccessLevel
    score_components: List[ScoreComponent]
    percentile_rank: float
    trend_direction: str  # "improving", "declining", "stable"
    confidence_level: float
    last_period_change: float
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    benchmark_comparisons: Dict[BenchmarkType, float] = field(default_factory=dict)
    calculation_date: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SuccessBenchmark:
    """Benchmark data for success comparison"""
    benchmark_id: str
    benchmark_type: BenchmarkType
    category: Optional[ScoreCategory] = None
    creator_category: Optional[str] = None
    platform: Optional[str] = None
    percentile_scores: Dict[int, float] = field(default_factory=dict)  # percentile -> score
    sample_size: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class SuccessTrajectory:
    """Success trajectory analysis"""
    creator_id: str
    trajectory_type: str  # "exponential", "linear", "plateau", "declining"
    growth_rate: float
    acceleration: float
    predicted_peak: Optional[datetime] = None
    sustainability_score: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    opportunity_factors: List[str] = field(default_factory=list)

@dataclass
class SuccessInsight:
    """Success insight and recommendation"""
    insight_id: str
    creator_id: str
    insight_type: str
    title: str
    description: str
    priority: str  # "critical", "high", "medium", "low"
    impact_potential: float
    effort_required: str  # "low", "medium", "high"
    time_to_impact: int  # days
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    action_items: List[str] = field(default_factory=list)

@dataclass
class SuccessAnalytics:
    """Success analytics aggregated data"""
    timeframe: str
    total_creators_analyzed: int
    average_success_score: float
    score_distribution: Dict[SuccessLevel, int]
    top_performing_categories: List[ScoreCategory]
    trending_success_factors: List[str]
    benchmark_updates: int
    insights_generated: int
    success_trajectory_patterns: Dict[str, int]

class CreatorSuccessIntelligenceScoring:
    """Enterprise Creator Success Intelligence Scoring System
    
    Provides comprehensive success scoring with intelligent analytics,
    benchmarking, and optimization recommendations for Creator Economy success.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Creator Success Intelligence Scoring System
        
        Args:
            config: Configuration dictionary for scoring settings
        """
        self.config = config or {}
        self.creator_metrics = defaultdict(list)
        self.success_scores = {}
        self.score_history = defaultdict(list)
        self.benchmarks = {}
        self.success_trajectories = {}
        self.success_insights = defaultdict(list)
        self.analytics_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=6)
        
        # Scoring configuration
        self.scoring_config = {
            "score_weights": {
                ScoreCategory.AUDIENCE_ENGAGEMENT: 0.20,
                ScoreCategory.CONTENT_QUALITY: 0.15,
                ScoreCategory.GROWTH_VELOCITY: 0.15,
                ScoreCategory.MONETIZATION_EFFICIENCY: 0.12,
                ScoreCategory.PLATFORM_MASTERY: 0.10,
                ScoreCategory.COLLABORATION_IMPACT: 0.08,
                ScoreCategory.INNOVATION_INDEX: 0.08,
                ScoreCategory.CONSISTENCY_SCORE: 0.06,
                ScoreCategory.INFLUENCE_REACH: 0.03,
                ScoreCategory.BRAND_STRENGTH: 0.03
            },
            "success_level_thresholds": {
                SuccessLevel.EMERGING: 0.0,
                SuccessLevel.DEVELOPING: 0.20,
                SuccessLevel.ESTABLISHED: 0.40,
                SuccessLevel.ADVANCED: 0.60,
                SuccessLevel.EXPERT: 0.75,
                SuccessLevel.MASTER: 0.85,
                SuccessLevel.LEGEND: 0.95
            },
            "calculation_window_days": 30,
            "trend_analysis_periods": 5,
            "benchmark_update_interval": 86400,  # 24 hours
            "confidence_threshold": 0.7,
            "min_metrics_for_score": 5
        }
        
        # Initialize benchmarks
        self._initialize_default_benchmarks()
        
        # Start background tasks
        asyncio.create_task(self._score_calculator())
        asyncio.create_task(self._benchmark_updater())
        asyncio.create_task(self._insight_generator())
        
        logger.info("Creator Success Intelligence Scoring System initialized successfully")
    
    def _initialize_default_benchmarks(self):
        """Initialize default benchmark data"""
        # Industry average benchmarks
        industry_benchmark = SuccessBenchmark(
            benchmark_id="industry_average",
            benchmark_type=BenchmarkType.INDUSTRY_AVERAGE,
            percentile_scores={
                10: 0.15, 25: 0.25, 50: 0.45, 75: 0.65, 90: 0.80, 95: 0.90, 99: 0.95
            },
            sample_size=10000
        )
        
        # Top performers benchmark
        top_performers_benchmark = SuccessBenchmark(
            benchmark_id="top_performers",
            benchmark_type=BenchmarkType.TOP_PERFORMERS,
            percentile_scores={
                10: 0.70, 25: 0.75, 50: 0.82, 75: 0.88, 90: 0.93, 95: 0.96, 99: 0.99
            },
            sample_size=1000
        )
        
        # Platform leaders benchmark
        platform_leaders_benchmark = SuccessBenchmark(
            benchmark_id="platform_leaders",
            benchmark_type=BenchmarkType.PLATFORM_LEADERS,
            percentile_scores={
                10: 0.60, 25: 0.68, 50: 0.75, 75: 0.83, 90: 0.89, 95: 0.94, 99: 0.98
            },
            sample_size=500
        )
        
        self.benchmarks = {
            "industry_average": industry_benchmark,
            "top_performers": top_performers_benchmark,
            "platform_leaders": platform_leaders_benchmark
        }
        
        logger.info("Default benchmarks initialized")
    
    async def record_success_metric(self, metric: SuccessMetric) -> bool:
        """Record a success metric for analysis
        
        Args:
            metric: Success metric to record
            
        Returns:
            Success status of recording
        """
        try:
            # Validate metric
            if not metric.creator_id or not metric.metric_id:
                raise ValueError("Creator ID and metric ID are required")
            
            # Store metric
            self.creator_metrics[metric.creator_id].append(metric)
            
            # Maintain data retention
            cutoff_date = datetime.now() - timedelta(days=90)
            self.creator_metrics[metric.creator_id] = [
                m for m in self.creator_metrics[metric.creator_id]
                if m.timestamp >= cutoff_date
            ]
            
            # Trigger score recalculation if enough metrics
            if len(self.creator_metrics[metric.creator_id]) >= self.scoring_config["min_metrics_for_score"]:
                await self._schedule_score_calculation(metric.creator_id)
            
            logger.debug(f"Success metric recorded: {metric.metric_type.value} for {metric.creator_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording success metric: {str(e)}")
            return False
    
    async def calculate_success_score(self, creator_id: str) -> Optional[SuccessScore]:
        """Calculate comprehensive success score for a creator
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            Success score result
        """
        try:
            metrics = self.creator_metrics.get(creator_id, [])
            
            if len(metrics) < self.scoring_config["min_metrics_for_score"]:
                logger.warning(f"Insufficient metrics for creator {creator_id}")
                return None
            
            # Calculate scores for each category
            score_components = []
            
            for category in ScoreCategory:
                component_score = await self._calculate_category_score(creator_id, category, metrics)
                if component_score:
                    score_components.append(component_score)
            
            if not score_components:
                return None
            
            # Calculate overall score
            overall_score = sum(
                component.weighted_score 
                for component in score_components
            )
            
            # Determine success level
            success_level = self._determine_success_level(overall_score)
            
            # Calculate percentile rank
            percentile_rank = await self._calculate_percentile_rank(creator_id, overall_score)
            
            # Analyze trend
            trend_direction, confidence_level, last_period_change = await self._analyze_score_trend(creator_id)
            
            # Identify strengths and weaknesses
            strengths, weaknesses = self._identify_strengths_weaknesses(score_components)
            
            # Generate recommendations
            recommendations = await self._generate_success_recommendations(creator_id, score_components)
            
            # Calculate benchmark comparisons
            benchmark_comparisons = await self._calculate_benchmark_comparisons(overall_score)
            
            # Create success score
            success_score = SuccessScore(
                score_id=str(uuid.uuid4()),
                creator_id=creator_id,
                overall_score=overall_score,
                success_level=success_level,
                score_components=score_components,
                percentile_rank=percentile_rank,
                trend_direction=trend_direction,
                confidence_level=confidence_level,
                last_period_change=last_period_change,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                benchmark_comparisons=benchmark_comparisons
            )
            
            # Store score
            self.success_scores[creator_id] = success_score
            self.score_history[creator_id].append(success_score)
            
            # Generate trajectory analysis
            await self._analyze_success_trajectory(creator_id)
            
            # Generate insights
            await self._generate_success_insights(creator_id, success_score)
            
            logger.info(f"Success score calculated for {creator_id}: {overall_score:.3f} ({success_level.value})")
            return success_score
            
        except Exception as e:
            logger.error(f"Error calculating success score: {str(e)}")
            return None
    
    async def _calculate_category_score(
        self, 
        creator_id: str, 
        category: ScoreCategory, 
        metrics: List[SuccessMetric]
    ) -> Optional[ScoreComponent]:
        """Calculate score for a specific category"""
        try:
            # Filter metrics relevant to this category
            relevant_metrics = await self._get_category_metrics(category, metrics)
            
            if not relevant_metrics:
                return None
            
            # Calculate raw score based on category-specific logic
            if category == ScoreCategory.AUDIENCE_ENGAGEMENT:
                raw_score = await self._calculate_engagement_score(relevant_metrics)
            elif category == ScoreCategory.CONTENT_QUALITY:
                raw_score = await self._calculate_content_quality_score(relevant_metrics)
            elif category == ScoreCategory.GROWTH_VELOCITY:
                raw_score = await self._calculate_growth_score(relevant_metrics)
            elif category == ScoreCategory.MONETIZATION_EFFICIENCY:
                raw_score = await self._calculate_monetization_score(relevant_metrics)
            elif category == ScoreCategory.PLATFORM_MASTERY:
                raw_score = await self._calculate_platform_mastery_score(relevant_metrics)
            elif category == ScoreCategory.COLLABORATION_IMPACT:
                raw_score = await self._calculate_collaboration_score(relevant_metrics)
            elif category == ScoreCategory.INNOVATION_INDEX:
                raw_score = await self._calculate_innovation_score(relevant_metrics)
            elif category == ScoreCategory.CONSISTENCY_SCORE:
                raw_score = await self._calculate_consistency_score(relevant_metrics)
            elif category == ScoreCategory.INFLUENCE_REACH:
                raw_score = await self._calculate_influence_score(relevant_metrics)
            elif category == ScoreCategory.BRAND_STRENGTH:
                raw_score = await self._calculate_brand_score(relevant_metrics)
            else:
                raw_score = 0.5  # Default score
            
            # Get weight for this category
            weight = self.scoring_config["score_weights"].get(category, 0.1)
            
            # Calculate weighted score
            weighted_score = raw_score * weight
            
            # Calculate percentile rank for this category
            percentile_rank = await self._calculate_category_percentile(creator_id, category, raw_score)
            
            # Get benchmark comparisons
            benchmark_comparison = await self._get_category_benchmarks(category, raw_score)
            
            # Identify contributing factors
            contributing_factors = await self._identify_contributing_factors(category, relevant_metrics)
            
            # Calculate improvement potential
            improvement_potential = max(0, 1.0 - raw_score)
            
            return ScoreComponent(
                category=category,
                raw_score=raw_score,
                weighted_score=weighted_score,
                weight=weight,
                percentile_rank=percentile_rank,
                benchmark_comparison=benchmark_comparison,
                contributing_factors=contributing_factors,
                improvement_potential=improvement_potential
            )
            
        except Exception as e:
            logger.error(f"Error calculating category score for {category.value}: {str(e)}")
            return None
    
    async def _get_category_metrics(self, category: ScoreCategory, metrics: List[SuccessMetric]) -> List[SuccessMetric]:
        """Get metrics relevant to a specific category"""
        try:
            category_mapping = {
                ScoreCategory.AUDIENCE_ENGAGEMENT: [SuccessMetricType.ENGAGEMENT_SUCCESS],
                ScoreCategory.CONTENT_QUALITY: [SuccessMetricType.CONTENT_SUCCESS],
                ScoreCategory.GROWTH_VELOCITY: [SuccessMetricType.GROWTH_SUCCESS],
                ScoreCategory.MONETIZATION_EFFICIENCY: [SuccessMetricType.REVENUE_SUCCESS],
                ScoreCategory.PLATFORM_MASTERY: [SuccessMetricType.CONTENT_SUCCESS, SuccessMetricType.ENGAGEMENT_SUCCESS],
                ScoreCategory.COLLABORATION_IMPACT: [SuccessMetricType.COLLABORATION_SUCCESS],
                ScoreCategory.INNOVATION_INDEX: [SuccessMetricType.INNOVATION_SUCCESS],
                ScoreCategory.CONSISTENCY_SCORE: [SuccessMetricType.CONSISTENCY_SUCCESS],
                ScoreCategory.INFLUENCE_REACH: [SuccessMetricType.INFLUENCE_SUCCESS],
                ScoreCategory.BRAND_STRENGTH: [SuccessMetricType.BRAND_SUCCESS]
            }
            
            relevant_types = category_mapping.get(category, [])
            
            return [
                metric for metric in metrics
                if metric.metric_type in relevant_types
            ]
            
        except Exception as e:
            logger.error(f"Error getting category metrics: {str(e)}")
            return []
    
    async def _calculate_engagement_score(self, metrics: List[SuccessMetric]) -> float:
        """Calculate engagement success score"""
        try:
            if not metrics:
                return 0.0
            
            # Weight recent metrics more heavily
            total_weighted_value = 0.0
            total_weight = 0.0
            
            now = datetime.now()
            
            for metric in metrics:
                # Calculate time decay weight (more recent = higher weight)
                days_old = (now - metric.timestamp).days
                time_weight = math.exp(-days_old / 30.0)  # Exponential decay over 30 days
                
                # Apply metric weight
                final_weight = time_weight * metric.weight
                
                total_weighted_value += metric.value * final_weight
                total_weight += final_weight
            
            if total_weight == 0:
                return 0.0
            
            # Normalize to 0-1 scale
            raw_score = total_weighted_value / total_weight
            
            # Apply engagement-specific scaling
            # High engagement rates are exponentially more valuable
            engagement_score = min(1.0, raw_score ** 0.8)  # Slightly favor higher engagement
            
            return engagement_score
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return 0.0
    
    async def _calculate_content_quality_score(self, metrics: List[SuccessMetric]) -> float:
        """Calculate content quality success score"""
        try:
            if not metrics:
                return 0.0
            
            # Focus on consistency and improvement in quality
            values = [metric.value for metric in sorted(metrics, key=lambda x: x.timestamp)]
            
            if len(values) == 1:
                return values[0]
            
            # Calculate average quality
            avg_quality = sum(values) / len(values)
            
            # Calculate improvement trend
            if len(values) >= 3:
                recent_avg = sum(values[-3:]) / 3
                early_avg = sum(values[:3]) / 3
                improvement_factor = min(1.2, recent_avg / early_avg) if early_avg > 0 else 1.0
            else:
                improvement_factor = 1.0
            
            # Calculate consistency (lower variance is better)
            if len(values) > 1:
                variance = sum((v - avg_quality) ** 2 for v in values) / len(values)
                consistency_factor = max(0.5, 1.0 - variance)
            else:
                consistency_factor = 1.0
            
            # Combine factors
            quality_score = avg_quality * improvement_factor * consistency_factor
            
            return min(1.0, quality_score)
            
        except Exception as e:
            logger.error(f"Error calculating content quality score: {str(e)}")
            return 0.0
    
    async def _calculate_growth_score(self, metrics: List[SuccessMetric]) -> float:
        """Calculate growth velocity success score"""
        try:
            if not metrics:
                return 0.0
            
            # Sort metrics by timestamp
            sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
            
            if len(sorted_metrics) < 2:
                return sorted_metrics[0].value if sorted_metrics else 0.0
            
            # Calculate growth rate
            values = [metric.value for metric in sorted_metrics]
            
            # Use compound growth rate
            periods = len(values) - 1
            if values[0] > 0:
                growth_rate = (values[-1] / values[0]) ** (1.0 / periods) - 1
            else:
                # Handle zero starting value
                growth_rate = sum(values[1:]) / len(values[1:]) if len(values) > 1 else 0
            
            # Convert growth rate to score (0-1 scale)
            # 100% growth over period = score of 1.0
            growth_score = min(1.0, growth_rate)
            
            # Bonus for acceleration
            if len(values) >= 4:
                first_half_growth = values[len(values)//2] / values[0] if values[0] > 0 else 0
                second_half_growth = values[-1] / values[len(values)//2] if values[len(values)//2] > 0 else 0
                
                if second_half_growth > first_half_growth:
                    acceleration_bonus = 0.1
                    growth_score = min(1.0, growth_score + acceleration_bonus)
            
            return max(0.0, growth_score)
            
        except Exception as e:
            logger.error(f"Error calculating growth score: {str(e)}")
            return 0.0
    
    async def _calculate_monetization_score(self, metrics: List[SuccessMetric]) -> float:
        """Calculate monetization efficiency success score"""
        try:
            if not metrics:
                return 0.0
            
            # Consider revenue consistency and growth
            values = [metric.value for metric in sorted(metrics, key=lambda x: x.timestamp)]
            
            if not values:
                return 0.0
            
            # Calculate revenue efficiency (revenue per engagement/follower)
            avg_revenue = sum(values) / len(values)
            
            # Normalize revenue to 0-1 scale (this would be platform/category specific)
            # For now, use log scale to handle wide revenue ranges
            if avg_revenue > 0:
                # Assume $1000/month is "good" monetization
                normalized_revenue = min(1.0, math.log10(avg_revenue + 1) / math.log10(1001))
            else:
                normalized_revenue = 0.0
            
            # Bonus for consistency
            if len(values) > 1:
                revenue_variance = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
                consistency_bonus = max(0.0, 0.2 * (1.0 - revenue_variance))
                normalized_revenue = min(1.0, normalized_revenue + consistency_bonus)
            
            return normalized_revenue
            
        except Exception as e:
            logger.error(f"Error calculating monetization score: {str(e)}")
            return 0.0
    
    async def _calculate_platform_mastery_score(self, metrics: List[SuccessMetric]) -> float:
        """Calculate platform mastery success score"""
        try:
            if not metrics:
                return 0.0
            
            # Consider number of platforms and performance across them
            platform_performance = defaultdict(list)
            
            for metric in metrics:
                platform = metric.context.get("platform", "unknown")
                platform_performance[platform].append(metric.value)
            
            if not platform_performance:
                return 0.0
            
            # Calculate average performance per platform
            platform_scores = {}
            for platform, values in platform_performance.items():
                platform_scores[platform] = sum(values) / len(values)
            
            # Platform diversity bonus
            num_platforms = len(platform_scores)
            diversity_bonus = min(0.3, num_platforms * 0.1)  # Max 30% bonus for 3+ platforms
            
            # Average performance across platforms
            avg_performance = sum(platform_scores.values()) / len(platform_scores)
            
            # Combine performance and diversity
            mastery_score = min(1.0, avg_performance + diversity_bonus)
            
            return mastery_score
            
        except Exception as e:
            logger.error(f"Error calculating platform mastery score: {str(e)}")
            return 0.0
    
    async def _calculate_collaboration_score(self, metrics: List[SuccessMetric]) -> float:
        """Calculate collaboration impact success score"""
        try:
            if not metrics:
                return 0.0
            
            # Consider collaboration frequency and success
            collaboration_values = [metric.value for metric in metrics]
            
            if not collaboration_values:
                return 0.0
            
            # Average collaboration success
            avg_success = sum(collaboration_values) / len(collaboration_values)
            
            # Frequency bonus (more collaborations = higher score)
            frequency_factor = min(1.2, len(collaboration_values) / 10.0)  # Normalize to 10 collaborations
            
            collaboration_score = min(1.0, avg_success * frequency_factor)
            
            return collaboration_score
            
        except Exception as e:
            logger.error(f"Error calculating collaboration score: {str(e)}")
            return 0.0
    
    async def _calculate_innovation_score(self, metrics: List[SuccessMetric]) -> float:
        """Calculate innovation index success score"""
        try:
            if not metrics:
                return 0.0
            
            # Innovation is about trying new things and pioneering trends
            innovation_values = [metric.value for metric in metrics]
            
            # Calculate average innovation score
            avg_innovation = sum(innovation_values) / len(innovation_values)
            
            # Bonus for recent innovation activity
            recent_metrics = [
                metric for metric in metrics
                if (datetime.now() - metric.timestamp).days <= 30
            ]
            
            if recent_metrics:
                recent_innovation = sum(m.value for m in recent_metrics) / len(recent_metrics)
                recency_bonus = min(0.2, (recent_innovation - avg_innovation) * 0.5)
                avg_innovation = min(1.0, avg_innovation + recency_bonus)
            
            return avg_innovation
            
        except Exception as e:
            logger.error(f"Error calculating innovation score: {str(e)}")
            return 0.0
    
    async def _calculate_consistency_score(self, metrics: List[SuccessMetric]) -> float:
        """Calculate consistency success score"""
        try:
            if not metrics:
                return 0.0
            
            # Consistency is about regular activity and predictable quality
            sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
            
            if len(sorted_metrics) < 2:
                return sorted_metrics[0].value if sorted_metrics else 0.0
            
            # Calculate time gaps between activities
            time_gaps = []
            for i in range(1, len(sorted_metrics)):
                gap = (sorted_metrics[i].timestamp - sorted_metrics[i-1].timestamp).days
                time_gaps.append(gap)
            
            # Consistency in timing (lower variance in gaps = more consistent)
            if time_gaps:
                avg_gap = sum(time_gaps) / len(time_gaps)
                gap_variance = sum((gap - avg_gap) ** 2 for gap in time_gaps) / len(time_gaps)
                timing_consistency = max(0.0, 1.0 - (gap_variance ** 0.5) / max(avg_gap, 1))
            else:
                timing_consistency = 1.0
            
            # Consistency in quality
            values = [metric.value for metric in sorted_metrics]
            avg_value = sum(values) / len(values)
            value_variance = sum((v - avg_value) ** 2 for v in values) / len(values)
            quality_consistency = max(0.0, 1.0 - (value_variance ** 0.5))
            
            # Combine timing and quality consistency
            consistency_score = (timing_consistency + quality_consistency) / 2
            
            return consistency_score
            
        except Exception as e:
            logger.error(f"Error calculating consistency score: {str(e)}")
            return 0.0
    
    async def _calculate_influence_score(self, metrics: List[SuccessMetric]) -> float:
        """Calculate influence reach success score"""
        try:
            if not metrics:
                return 0.0
            
            # Influence combines reach and impact
            influence_values = [metric.value for metric in metrics]
            
            # Use logarithmic scale for influence (network effects)
            avg_influence = sum(influence_values) / len(influence_values)
            
            # Apply logarithmic scaling for influence
            if avg_influence > 0:
                influence_score = min(1.0, math.log10(avg_influence + 1) / math.log10(1000001))  # Scale to 1M influence
            else:
                influence_score = 0.0
            
            return influence_score
            
        except Exception as e:
            logger.error(f"Error calculating influence score: {str(e)}")
            return 0.0
    
    async def _calculate_brand_score(self, metrics: List[SuccessMetric]) -> float:
        """Calculate brand strength success score"""
        try:
            if not metrics:
                return 0.0
            
            # Brand strength is about recognition and differentiation
            brand_values = [metric.value for metric in metrics]
            
            avg_brand_strength = sum(brand_values) / len(brand_values)
            
            # Bonus for brand consistency across platforms
            platform_brand_scores = defaultdict(list)
            for metric in metrics:
                platform = metric.context.get("platform", "unknown")
                platform_brand_scores[platform].append(metric.value)
            
            if len(platform_brand_scores) > 1:
                # Calculate consistency across platforms
                platform_averages = [
                    sum(scores) / len(scores) 
                    for scores in platform_brand_scores.values()
                ]
                consistency_bonus = max(0.0, 1.0 - np.std(platform_averages)) * 0.2
                avg_brand_strength = min(1.0, avg_brand_strength + consistency_bonus)
            
            return avg_brand_strength
            
        except Exception as e:
            logger.error(f"Error calculating brand score: {str(e)}")
            return 0.0
    
    def _determine_success_level(self, overall_score: float) -> SuccessLevel:
        """Determine success level based on overall score"""
        try:
            thresholds = self.scoring_config["success_level_thresholds"]
            
            for level in reversed(list(SuccessLevel)):
                if overall_score >= thresholds[level]:
                    return level
            
            return SuccessLevel.EMERGING
            
        except Exception as e:
            logger.error(f"Error determining success level: {str(e)}")
            return SuccessLevel.EMERGING
    
    async def _calculate_percentile_rank(self, creator_id: str, overall_score: float) -> float:
        """Calculate percentile rank compared to all creators"""
        try:
            all_scores = [
                score.overall_score 
                for score in self.success_scores.values()
                if score.creator_id != creator_id
            ]
            
            if not all_scores:
                return 50.0  # No comparison data
            
            # Count scores below current score
            scores_below = sum(1 for score in all_scores if score < overall_score)
            
            # Calculate percentile
            percentile = (scores_below / len(all_scores)) * 100
            
            return percentile
            
        except Exception as e:
            logger.error(f"Error calculating percentile rank: {str(e)}")
            return 50.0
    
    async def _analyze_score_trend(self, creator_id: str) -> Tuple[str, float, float]:
        """Analyze success score trend for creator"""
        try:
            history = self.score_history.get(creator_id, [])
            
            if len(history) < 2:
                return "stable", 0.5, 0.0
            
            # Get recent scores
            recent_scores = [score.overall_score for score in history[-5:]]
            
            if len(recent_scores) < 2:
                return "stable", 0.5, 0.0
            
            # Calculate trend
            first_half = recent_scores[:len(recent_scores)//2]
            second_half = recent_scores[len(recent_scores)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            change = second_avg - first_avg
            
            # Determine trend direction
            if change > 0.05:
                trend_direction = "improving"
            elif change < -0.05:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
            
            # Calculate confidence based on consistency
            score_variance = np.std(recent_scores) if len(recent_scores) > 1 else 0
            confidence_level = max(0.1, 1.0 - score_variance)
            
            return trend_direction, confidence_level, change
            
        except Exception as e:
            logger.error(f"Error analyzing score trend: {str(e)}")
            return "stable", 0.5, 0.0
    
    def _identify_strengths_weaknesses(self, score_components: List[ScoreComponent]) -> Tuple[List[str], List[str]]:
        """Identify strengths and weaknesses from score components"""
        try:
            # Sort components by percentile rank
            sorted_components = sorted(score_components, key=lambda x: x.percentile_rank, reverse=True)
            
            strengths = []
            weaknesses = []
            
            for component in sorted_components[:3]:  # Top 3 as strengths
                if component.percentile_rank >= 70:
                    strengths.append(f"Strong {component.category.value.replace('_', ' ')}")
            
            for component in sorted_components[-3:]:  # Bottom 3 as weaknesses
                if component.percentile_rank <= 30:
                    weaknesses.append(f"Improve {component.category.value.replace('_', ' ')}")
            
            return strengths, weaknesses
            
        except Exception as e:
            logger.error(f"Error identifying strengths/weaknesses: {str(e)}")
            return [], []
    
    async def _generate_success_recommendations(
        self, 
        creator_id: str, 
        score_components: List[ScoreComponent]
    ) -> List[str]:
        """Generate success optimization recommendations"""
        try:
            recommendations = []
            
            # Find lowest scoring categories for improvement
            improvement_components = sorted(
                score_components, 
                key=lambda x: x.raw_score * x.improvement_potential,
                reverse=True
            )
            
            for component in improvement_components[:3]:  # Top 3 improvement areas
                category = component.category
                
                if category == ScoreCategory.AUDIENCE_ENGAGEMENT:
                    recommendations.append("Increase engagement through interactive content and community building")
                elif category == ScoreCategory.CONTENT_QUALITY:
                    recommendations.append("Focus on improving content production quality and storytelling")
                elif category == ScoreCategory.GROWTH_VELOCITY:
                    recommendations.append("Implement growth strategies like cross-promotion and trending topics")
                elif category == ScoreCategory.MONETIZATION_EFFICIENCY:
                    recommendations.append("Diversify revenue streams and optimize pricing strategies")
                elif category == ScoreCategory.PLATFORM_MASTERY:
                    recommendations.append("Expand to additional platforms and optimize platform-specific content")
                elif category == ScoreCategory.COLLABORATION_IMPACT:
                    recommendations.append("Seek strategic collaborations with complementary creators")
                elif category == ScoreCategory.INNOVATION_INDEX:
                    recommendations.append("Experiment with new content formats and emerging trends")
                elif category == ScoreCategory.CONSISTENCY_SCORE:
                    recommendations.append("Establish regular content schedule and maintain quality standards")
                elif category == ScoreCategory.INFLUENCE_REACH:
                    recommendations.append("Build thought leadership through expert content and opinions")
                elif category == ScoreCategory.BRAND_STRENGTH:
                    recommendations.append("Develop consistent brand identity and unique value proposition")
            
            # Add general recommendations
            recommendations.append("Monitor success metrics regularly and adjust strategy based on performance")
            
            return recommendations[:5]  # Limit to top 5
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Focus on consistent high-quality content creation"]
    
    async def _calculate_category_percentile(self, creator_id: str, category: ScoreCategory, score: float) -> float:
        """Calculate percentile rank for specific category"""
        try:
            # Get all scores for this category
            category_scores = []
            
            for other_creator_id, success_score in self.success_scores.items():
                if other_creator_id != creator_id:
                    for component in success_score.score_components:
                        if component.category == category:
                            category_scores.append(component.raw_score)
            
            if not category_scores:
                return 50.0
            
            # Calculate percentile
            scores_below = sum(1 for s in category_scores if s < score)
            percentile = (scores_below / len(category_scores)) * 100
            
            return percentile
            
        except Exception as e:
            logger.error(f"Error calculating category percentile: {str(e)}")
            return 50.0
    
    async def _get_category_benchmarks(self, category: ScoreCategory, score: float) -> Dict[str, float]:
        """Get benchmark comparisons for category"""
        try:
            benchmarks = {}
            
            for benchmark_type, benchmark in self.benchmarks.items():
                # Find closest percentile
                best_percentile = 50
                best_diff = float('inf')
                
                for percentile, benchmark_score in benchmark.percentile_scores.items():
                    diff = abs(score - benchmark_score)
                    if diff < best_diff:
                        best_diff = diff
                        best_percentile = percentile
                
                benchmarks[benchmark_type] = best_percentile
            
            return benchmarks
            
        except Exception as e:
            logger.error(f"Error getting category benchmarks: {str(e)}")
            return {}
    
    async def _identify_contributing_factors(self, category: ScoreCategory, metrics: List[SuccessMetric]) -> List[str]:
        """Identify factors contributing to category score"""
        try:
            factors = []
            
            if not metrics:
                return factors
            
            # Analyze metric patterns
            values = [metric.value for metric in metrics]
            avg_value = sum(values) / len(values)
            
            # Check for trends
            if len(values) >= 3:
                recent_avg = sum(values[-3:]) / 3
                if recent_avg > avg_value * 1.1:
                    factors.append("improving_trend")
                elif recent_avg < avg_value * 0.9:
                    factors.append("declining_trend")
                else:
                    factors.append("stable_performance")
            
            # Check for consistency
            if len(values) > 1:
                variance = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
                if variance < 0.2:
                    factors.append("high_consistency")
                elif variance > 0.5:
                    factors.append("high_variability")
            
            # Check for recent activity
            recent_metrics = [
                m for m in metrics
                if (datetime.now() - m.timestamp).days <= 7
            ]
            
            if len(recent_metrics) >= 3:
                factors.append("high_recent_activity")
            elif not recent_metrics:
                factors.append("low_recent_activity")
            
            return factors[:3]  # Limit to top 3 factors
            
        except Exception as e:
            logger.error(f"Error identifying contributing factors: {str(e)}")
            return []
    
    async def _calculate_benchmark_comparisons(self, overall_score: float) -> Dict[BenchmarkType, float]:
        """Calculate benchmark comparisons for overall score"""
        try:
            comparisons = {}
            
            for benchmark_id, benchmark in self.benchmarks.items():
                # Find percentile in benchmark
                best_percentile = 50
                best_diff = float('inf')
                
                for percentile, benchmark_score in benchmark.percentile_scores.items():
                    diff = abs(overall_score - benchmark_score)
                    if diff < best_diff:
                        best_diff = diff
                        best_percentile = percentile
                
                comparisons[benchmark.benchmark_type] = best_percentile
            
            return comparisons
            
        except Exception as e:
            logger.error(f"Error calculating benchmark comparisons: {str(e)}")
            return {}
    
    async def _analyze_success_trajectory(self, creator_id: str):
        """Analyze success trajectory for creator"""
        try:
            history = self.score_history.get(creator_id, [])
            
            if len(history) < 3:
                return
            
            # Get score progression
            scores = [score.overall_score for score in history]
            
            # Calculate growth rate
            if len(scores) >= 2:
                periods = len(scores) - 1
                if scores[0] > 0:
                    growth_rate = (scores[-1] / scores[0]) ** (1.0 / periods) - 1
                else:
                    growth_rate = 0.0
            else:
                growth_rate = 0.0
            
            # Calculate acceleration
            if len(scores) >= 3:
                recent_growth = scores[-1] - scores[-2]
                previous_growth = scores[-2] - scores[-3]
                acceleration = recent_growth - previous_growth
            else:
                acceleration = 0.0
            
            # Determine trajectory type
            if growth_rate > 0.1:
                if acceleration > 0:
                    trajectory_type = "exponential"
                else:
                    trajectory_type = "linear"
            elif growth_rate > -0.05:
                trajectory_type = "plateau"
            else:
                trajectory_type = "declining"
            
            # Calculate sustainability score
            score_variance = np.std(scores) if len(scores) > 1 else 0
            sustainability_score = max(0.0, 1.0 - score_variance)
            
            # Identify risk and opportunity factors
            risk_factors = []
            opportunity_factors = []
            
            if trajectory_type == "declining":
                risk_factors.append("performance_decline")
            if score_variance > 0.2:
                risk_factors.append("high_volatility")
            
            if growth_rate > 0.05:
                opportunity_factors.append("positive_growth_trend")
            if acceleration > 0:
                opportunity_factors.append("accelerating_improvement")
            
            # Store trajectory analysis
            trajectory = SuccessTrajectory(
                creator_id=creator_id,
                trajectory_type=trajectory_type,
                growth_rate=growth_rate,
                acceleration=acceleration,
                sustainability_score=sustainability_score,
                risk_factors=risk_factors,
                opportunity_factors=opportunity_factors
            )
            
            self.success_trajectories[creator_id] = trajectory
            
        except Exception as e:
            logger.error(f"Error analyzing success trajectory: {str(e)}")
    
    async def _generate_success_insights(self, creator_id: str, success_score: SuccessScore):
        """Generate success insights for creator"""
        try:
            insights = []
            
            # Performance insights
            if success_score.trend_direction == "declining":
                insight = SuccessInsight(
                    insight_id=str(uuid.uuid4()),
                    creator_id=creator_id,
                    insight_type="performance_alert",
                    title="Performance Decline Detected",
                    description="Your success score has been declining. Focus on strengthening weak areas.",
                    priority="high",
                    impact_potential=0.8,
                    effort_required="medium",
                    time_to_impact=14,
                    action_items=[
                        "Review recent content performance",
                        "Analyze engagement patterns",
                        "Implement improvement strategies"
                    ]
                )
                insights.append(insight)
            
            # Opportunity insights
            trajectory = self.success_trajectories.get(creator_id)
            if trajectory and "accelerating_improvement" in trajectory.opportunity_factors:
                insight = SuccessInsight(
                    insight_id=str(uuid.uuid4()),
                    creator_id=creator_id,
                    insight_type="growth_opportunity",
                    title="Accelerating Growth Detected",
                    description="You're on an upward trajectory. Now is the time to scale your efforts.",
                    priority="medium",
                    impact_potential=0.9,
                    effort_required="high",
                    time_to_impact=30,
                    action_items=[
                        "Increase content production",
                        "Expand to new platforms",
                        "Seek collaboration opportunities"
                    ]
                )
                insights.append(insight)
            
            # Benchmark insights
            industry_percentile = success_score.benchmark_comparisons.get(BenchmarkType.INDUSTRY_AVERAGE, 50)
            if industry_percentile >= 90:
                insight = SuccessInsight(
                    insight_id=str(uuid.uuid4()),
                    creator_id=creator_id,
                    insight_type="achievement",
                    title="Top Performer Recognition",
                    description="You're performing in the top 10% of creators. Consider mentoring others.",
                    priority="low",
                    impact_potential=0.6,
                    effort_required="low",
                    time_to_impact=7,
                    action_items=[
                        "Share success strategies",
                        "Mentor emerging creators",
                        "Build thought leadership"
                    ]
                )
                insights.append(insight)
            
            # Store insights
            self.success_insights[creator_id].extend(insights)
            
        except Exception as e:
            logger.error(f"Error generating success insights: {str(e)}")
    
    async def _schedule_score_calculation(self, creator_id: str):
        """Schedule score calculation for creator"""
        try:
            # This would typically use a task queue in production
            # For now, calculate immediately
            await self.calculate_success_score(creator_id)
            
        except Exception as e:
            logger.error(f"Error scheduling score calculation: {str(e)}")
    
    async def _score_calculator(self):
        """Background task to calculate scores periodically"""
        while True:
            try:
                # Recalculate scores for active creators
                for creator_id in list(self.creator_metrics.keys()):
                    if len(self.creator_metrics[creator_id]) >= self.scoring_config["min_metrics_for_score"]:
                        await self.calculate_success_score(creator_id)
                        await asyncio.sleep(1)  # Rate limiting
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in score calculator: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _benchmark_updater(self):
        """Background task to update benchmarks"""
        while True:
            try:
                await self._update_benchmarks()
                await asyncio.sleep(self.scoring_config["benchmark_update_interval"])
                
            except Exception as e:
                logger.error(f"Error in benchmark updater: {str(e)}")
                await asyncio.sleep(86400)
    
    async def _update_benchmarks(self):
        """Update benchmark data based on current creator scores"""
        try:
            # Collect all current scores
            all_scores = [score.overall_score for score in self.success_scores.values()]
            
            if len(all_scores) < 10:
                return  # Need minimum data for meaningful benchmarks
            
            # Calculate percentiles
            percentiles = [10, 25, 50, 75, 90, 95, 99]
            percentile_scores = {}
            
            for p in percentiles:
                percentile_scores[p] = np.percentile(all_scores, p) if NUMPY_AVAILABLE else sorted(all_scores)[int(len(all_scores) * p / 100)]
            
            # Update industry benchmark
            if "industry_average" in self.benchmarks:
                self.benchmarks["industry_average"].percentile_scores = percentile_scores
                self.benchmarks["industry_average"].sample_size = len(all_scores)
                self.benchmarks["industry_average"].last_updated = datetime.now()
            
            logger.info(f"Updated benchmarks with {len(all_scores)} creator scores")
            
        except Exception as e:
            logger.error(f"Error updating benchmarks: {str(e)}")
    
    async def _insight_generator(self):
        """Background task to generate insights"""
        while True:
            try:
                # Generate insights for creators with recent activity
                for creator_id, success_score in self.success_scores.items():
                    if (datetime.now() - success_score.calculation_date).days <= 1:
                        await self._generate_success_insights(creator_id, success_score)
                
                await asyncio.sleep(43200)  # Run every 12 hours
                
            except Exception as e:
                logger.error(f"Error in insight generator: {str(e)}")
                await asyncio.sleep(43200)
    
    async def get_creator_success_profile(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive success profile for creator
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            Success profile data
        """
        try:
            success_score = self.success_scores.get(creator_id)
            if not success_score:
                return None
            
            # Get trajectory
            trajectory = self.success_trajectories.get(creator_id)
            
            # Get recent insights
            recent_insights = self.success_insights.get(creator_id, [])[-5:]
            
            # Get score history
            history = self.score_history.get(creator_id, [])[-10:]
            
            return {
                "creator_id": creator_id,
                "overall_score": success_score.overall_score,
                "success_level": success_score.success_level.value,
                "percentile_rank": success_score.percentile_rank,
                "trend_direction": success_score.trend_direction,
                "confidence_level": success_score.confidence_level,
                "last_period_change": success_score.last_period_change,
                "score_components": [
                    {
                        "category": comp.category.value,
                        "raw_score": comp.raw_score,
                        "weighted_score": comp.weighted_score,
                        "percentile_rank": comp.percentile_rank,
                        "improvement_potential": comp.improvement_potential
                    }
                    for comp in success_score.score_components
                ],
                "strengths": success_score.strengths,
                "weaknesses": success_score.weaknesses,
                "recommendations": success_score.recommendations,
                "benchmark_comparisons": {
                    k.value: v for k, v in success_score.benchmark_comparisons.items()
                },
                "trajectory": {
                    "type": trajectory.trajectory_type if trajectory else "unknown",
                    "growth_rate": trajectory.growth_rate if trajectory else 0.0,
                    "sustainability_score": trajectory.sustainability_score if trajectory else 0.0,
                    "risk_factors": trajectory.risk_factors if trajectory else [],
                    "opportunity_factors": trajectory.opportunity_factors if trajectory else []
                } if trajectory else None,
                "recent_insights": [
                    {
                        "title": insight.title,
                        "description": insight.description,
                        "priority": insight.priority,
                        "impact_potential": insight.impact_potential,
                        "action_items": insight.action_items
                    }
                    for insight in recent_insights
                ],
                "score_history": [
                    {
                        "score": score.overall_score,
                        "date": score.calculation_date.isoformat(),
                        "level": score.success_level.value
                    }
                    for score in history
                ],
                "calculation_date": success_score.calculation_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting creator success profile: {str(e)}")
            return None
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and performance metrics
        
        Returns:
            System health information
        """
        try:
            total_creators = len(self.creator_metrics)
            scored_creators = len(self.success_scores)
            total_metrics = sum(len(metrics) for metrics in self.creator_metrics.values())
            total_insights = sum(len(insights) for insights in self.success_insights.values())
            
            return {
                "total_creators_tracked": total_creators,
                "creators_with_scores": scored_creators,
                "total_success_metrics": total_metrics,
                "total_insights_generated": total_insights,
                "benchmarks_available": len(self.benchmarks),
                "trajectory_analyses": len(self.success_trajectories),
                "score_calculation_coverage": (scored_creators / total_creators * 100) if total_creators > 0 else 0,
                "average_success_score": sum(score.overall_score for score in self.success_scores.values()) / len(self.success_scores) if self.success_scores else 0,
                "system_status": "operational",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {"status": "error", "message": str(e)}

# Export main class and types
__all__ = [
    'CreatorSuccessIntelligenceScoring',
    'SuccessMetricType',
    'SuccessLevel',
    'ScoreCategory',
    'BenchmarkType',
    'SuccessMetric',
    'ScoreComponent',
    'SuccessScore',
    'SuccessBenchmark',
    'SuccessTrajectory',
    'SuccessInsight',
    'SuccessAnalytics'
]