"""
Ainflue Platform - Creator Performance Intelligence Dashboard
===========================================================

Enterprise dashboard for creator performance intelligence with AI-powered predictive
analytics, growth trajectory optimization, and comprehensive performance insights.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
            Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
This code, concept and architecture are the exclusive intellectual property of Fahed Mlaiel.
Any use, reproduction, distribution or adaptation without written personal authorization
from Fahed Mlaiel (mlaiel@live.de) constitutes copyright infringement and will be
prosecuted to the full extent of the law.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import statistics
from collections import defaultdict, deque
import numpy as np

from .enterprise_dashboard_system import (
    EnterpriseDashboardSystem,
    Dashboard,
    DashboardWidget,
    VisualizationType
)

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """Performance metrics for analysis."""
    ENGAGEMENT_RATE = "engagement_rate"
    AUDIENCE_GROWTH = "audience_growth"
    CONTENT_QUALITY = "content_quality"
    REVENUE_PERFORMANCE = "revenue_performance"
    COLLABORATION_SUCCESS = "collaboration_success"
    BRAND_STRENGTH = "brand_strength"
    INFLUENCE_SCORE = "influence_score"
    CONSISTENCY_SCORE = "consistency_score"

class TrendDirection(Enum):
    """Trend direction indicators."""
    RAPID_GROWTH = "rapid_growth"
    STEADY_GROWTH = "steady_growth"
    STABLE = "stable"
    SLIGHT_DECLINE = "slight_decline"
    DECLINING = "declining"
    VOLATILE = "volatile"

class PerformanceCategory(Enum):
    """Performance categories for benchmarking."""
    EXCEPTIONAL = "exceptional"
    ABOVE_AVERAGE = "above_average"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    NEEDS_IMPROVEMENT = "needs_improvement"

@dataclass
class PerformanceSnapshot:
    """Performance snapshot at a point in time."""
    snapshot_id: str
    creator_id: str
    timestamp: datetime
    engagement_rate: float = 0.0
    audience_size: int = 0
    content_views: int = 0
    content_shares: int = 0
    content_saves: int = 0
    revenue: float = 0.0
    collaboration_count: int = 0
    quality_score: float = 0.0
    influence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceAnalysis:
    """Comprehensive performance analysis."""
    analysis_id: str
    creator_id: str
    analysis_period: Tuple[datetime, datetime]
    overall_score: float = 0.0
    metric_scores: Dict[PerformanceMetric, float] = field(default_factory=dict)
    trend_analysis: Dict[PerformanceMetric, TrendDirection] = field(default_factory=dict)
    performance_category: PerformanceCategory = PerformanceCategory.AVERAGE
    strengths: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    growth_potential: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    benchmark_comparison: Dict[str, float] = field(default_factory=dict)
    prediction_confidence: float = 0.0

@dataclass
class GrowthPrediction:
    """AI-powered growth prediction."""
    prediction_id: str
    creator_id: str
    prediction_horizon: int  # days
    predicted_metrics: Dict[PerformanceMetric, float] = field(default_factory=dict)
    growth_trajectory: TrendDirection = TrendDirection.STABLE
    success_probability: float = 0.0
    key_growth_drivers: List[str] = field(default_factory=list)
    potential_obstacles: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    confidence_intervals: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CompetitiveIntelligence:
    """Competitive intelligence analysis."""
    creator_id: str
    competitive_position: str  # "leader", "challenger", "follower", "niche"
    market_share_estimate: float = 0.0
    competitive_advantages: List[str] = field(default_factory=list)
    competitive_gaps: List[str] = field(default_factory=list)
    top_competitors: List[Dict[str, Any]] = field(default_factory=list)
    differentiation_opportunities: List[str] = field(default_factory=list)
    threat_level: str = "low"  # "low", "medium", "high"
    market_trends_alignment: float = 0.0

class CreatorPerformanceIntelligenceDashboard:
    """
    Enterprise dashboard for creator performance intelligence.
    
    Provides AI-powered predictive analytics, comprehensive performance insights,
    growth trajectory optimization, and competitive intelligence for creators.
    """
    
    def __init__(self, dashboard_id: str, config: Dict[str, Any]):
        """Initialize creator performance intelligence dashboard."""
        self.dashboard_id = dashboard_id
        self.config = config
        self.enterprise_system = EnterpriseDashboardSystem()
        
        # Performance data management
        self.performance_snapshots: Dict[str, List[PerformanceSnapshot]] = defaultdict(list)
        self.performance_analyses: Dict[str, PerformanceAnalysis] = {}
        self.growth_predictions: Dict[str, GrowthPrediction] = {}
        self.competitive_intelligence: Dict[str, CompetitiveIntelligence] = {}
        
        # AI intelligence engines
        self.predictive_engine = None
        self.trend_analyzer = None
        self.performance_optimizer = None
        self.competitive_analyzer = None
        
        # Analytics caches
        self.intelligence_insights: Dict[str, Any] = {}
        self.benchmark_data: Dict[str, Any] = {}
        self.market_intelligence: Dict[str, Any] = {}
        
        # Processing queues
        self.analysis_queue: deque = deque()
        self.prediction_queue: deque = deque()
        
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup comprehensive logging for performance intelligence."""
        self.logger = logging.getLogger(f"{__name__}.PerformanceIntelligence")
        self.logger.setLevel(logging.INFO)
        
    async def initialize(self) -> bool:
        """
        Initialize performance intelligence dashboard.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info(f"Initializing Creator Performance Intelligence Dashboard {self.dashboard_id}")
            
            # Initialize enterprise dashboard system
            await self.enterprise_system.initialize()
            
            # Initialize AI intelligence engines
            await self._initialize_intelligence_engines()
            
            # Setup performance widgets
            await self._setup_performance_widgets()
            
            # Initialize benchmark data
            await self._initialize_benchmark_data()
            
            # Start background processing tasks
            await self._start_background_tasks()
            
            self.logger.info(f"Creator Performance Intelligence Dashboard {self.dashboard_id} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize performance intelligence dashboard: {e}")
            return False
    
    async def _initialize_intelligence_engines(self):
        """Initialize AI engines for performance intelligence."""
        # Predictive analytics engine
        self.predictive_engine = {
            "models": {
                "growth_predictor": None,  # Would load actual ML model
                "engagement_forecaster": None,  # Would load actual ML model
                "revenue_predictor": None,  # Would load actual ML model
                "risk_assessor": None  # Would load actual ML model
            },
            "features": [
                "historical_performance", "content_quality", "engagement_patterns",
                "seasonal_trends", "competitive_landscape", "market_conditions"
            ],
            "prediction_horizons": [7, 30, 90, 365],  # days
            "enabled": self.config.get("predictive_analytics", True)
        }
        
        # Trend analysis engine
        self.trend_analyzer = {
            "algorithms": {
                "time_series_analysis": None,
                "pattern_recognition": None,
                "anomaly_detection": None,
                "seasonal_decomposition": None
            },
            "trend_detection_sensitivity": self.config.get("trend_sensitivity", "medium"),
            "enabled": True
        }
        
        # Performance optimization engine
        self.performance_optimizer = {
            "optimization_strategies": {
                "content_optimization": None,
                "timing_optimization": None,
                "audience_targeting": None,
                "engagement_maximization": None
            },
            "optimization_goals": ["growth", "engagement", "revenue", "efficiency"],
            "enabled": self.config.get("performance_optimization", True)
        }
        
        # Competitive analysis engine
        self.competitive_analyzer = {
            "analysis_methods": {
                "market_positioning": None,
                "competitive_benchmarking": None,
                "gap_analysis": None,
                "opportunity_identification": None
            },
            "update_frequency": 86400,  # Daily updates
            "enabled": self.config.get("competitive_analysis", True)
        }
    
    async def _setup_performance_widgets(self):
        """Setup dashboard widgets for performance intelligence."""
        widgets = []
        
        # Performance overview widget
        overview_widget = DashboardWidget(
            widget_id="performance_overview",
            widget_type="performance_intelligence_overview",
            title="Performance Intelligence Overview",
            visualization_type=VisualizationType.KPI_CARD,
            config={
                "key_metrics": ["overall_score", "growth_potential", "competitive_position"],
                "trend_indicators": True,
                "benchmark_comparison": True
            }
        )
        widgets.append(overview_widget)
        
        # Growth prediction widget
        prediction_widget = DashboardWidget(
            widget_id="growth_predictions",
            widget_type="ai_growth_predictions",
            title="AI Growth Predictions",
            visualization_type=VisualizationType.LINE_CHART,
            config={
                "prediction_horizons": [30, 90, 365],
                "confidence_intervals": True,
                "scenario_analysis": True,
                "key_drivers": True
            }
        )
        widgets.append(prediction_widget)
        
        # Performance trends widget
        trends_widget = DashboardWidget(
            widget_id="performance_trends",
            widget_type="trend_analysis",
            title="Performance Trends Analysis",
            visualization_type=VisualizationType.LINE_CHART,
            config={
                "metrics": [m.value for m in PerformanceMetric],
                "trend_detection": True,
                "anomaly_highlighting": True,
                "seasonal_patterns": True
            }
        )
        widgets.append(trends_widget)
        
        # Competitive intelligence widget
        competitive_widget = DashboardWidget(
            widget_id="competitive_intelligence",
            widget_type="competitive_analysis",
            title="Competitive Intelligence",
            visualization_type=VisualizationType.SCATTER_PLOT,
            config={
                "positioning_map": True,
                "competitor_tracking": True,
                "market_opportunities": True,
                "threat_assessment": True
            }
        )
        widgets.append(competitive_widget)
        
        # Performance optimization widget
        optimization_widget = DashboardWidget(
            widget_id="performance_optimization",
            widget_type="ai_optimization_recommendations",
            title="AI Performance Optimization",
            visualization_type=VisualizationType.TABLE,
            config={
                "optimization_strategies": True,
                "impact_estimates": True,
                "implementation_roadmap": True,
                "resource_requirements": True
            }
        )
        widgets.append(optimization_widget)
        
        # Benchmark comparison widget
        benchmark_widget = DashboardWidget(
            widget_id="benchmark_comparison",
            widget_type="performance_benchmarks",
            title="Industry Benchmark Comparison",
            visualization_type=VisualizationType.BAR_CHART,
            config={
                "industry_benchmarks": True,
                "peer_comparisons": True,
                "percentile_rankings": True,
                "improvement_targets": True
            }
        )
        widgets.append(benchmark_widget)
        
        self.widgets = widgets
    
    async def _initialize_benchmark_data(self):
        """Initialize industry benchmark data."""
        # Simulated industry benchmarks (would be loaded from actual market research)
        self.benchmark_data = {
            "industry_averages": {
                PerformanceMetric.ENGAGEMENT_RATE: 0.045,
                PerformanceMetric.AUDIENCE_GROWTH: 0.15,  # 15% monthly growth
                PerformanceMetric.CONTENT_QUALITY: 0.7,
                PerformanceMetric.REVENUE_PERFORMANCE: 0.6,
                PerformanceMetric.COLLABORATION_SUCCESS: 0.75,
                PerformanceMetric.BRAND_STRENGTH: 0.65,
                PerformanceMetric.INFLUENCE_SCORE: 0.5,
                PerformanceMetric.CONSISTENCY_SCORE: 0.6
            },
            "top_performer_thresholds": {
                PerformanceMetric.ENGAGEMENT_RATE: 0.08,
                PerformanceMetric.AUDIENCE_GROWTH: 0.25,
                PerformanceMetric.CONTENT_QUALITY: 0.85,
                PerformanceMetric.REVENUE_PERFORMANCE: 0.8,
                PerformanceMetric.COLLABORATION_SUCCESS: 0.9,
                PerformanceMetric.BRAND_STRENGTH: 0.85,
                PerformanceMetric.INFLUENCE_SCORE: 0.8,
                PerformanceMetric.CONSISTENCY_SCORE: 0.85
            },
            "performance_categories": {
                PerformanceCategory.EXCEPTIONAL: {"min_score": 0.9, "percentile": 95},
                PerformanceCategory.ABOVE_AVERAGE: {"min_score": 0.75, "percentile": 80},
                PerformanceCategory.AVERAGE: {"min_score": 0.5, "percentile": 50},
                PerformanceCategory.BELOW_AVERAGE: {"min_score": 0.3, "percentile": 20},
                PerformanceCategory.NEEDS_IMPROVEMENT: {"min_score": 0.0, "percentile": 0}
            }
        }
    
    async def _start_background_tasks(self):
        """Start background processing tasks."""
        self.background_tasks = [
            asyncio.create_task(self._process_performance_analysis()),
            asyncio.create_task(self._generate_growth_predictions()),
            asyncio.create_task(self._update_competitive_intelligence()),
            asyncio.create_task(self._optimize_performance_recommendations()),
            asyncio.create_task(self._update_market_intelligence())
        ]
    
    async def record_performance_snapshot(
        self,
        creator_id: str,
        performance_data: Dict[str, Union[int, float]]
    ) -> Optional[str]:
        """
        Record performance snapshot for creator.
        
        Args:
            creator_id: Creator identifier
            performance_data: Performance metrics data
            
        Returns:
            str: Snapshot ID if recorded successfully
        """
        try:
            snapshot_id = str(uuid.uuid4())
            
            snapshot = PerformanceSnapshot(
                snapshot_id=snapshot_id,
                creator_id=creator_id,
                timestamp=datetime.now(),
                engagement_rate=performance_data.get("engagement_rate", 0.0),
                audience_size=performance_data.get("audience_size", 0),
                content_views=performance_data.get("content_views", 0),
                content_shares=performance_data.get("content_shares", 0),
                content_saves=performance_data.get("content_saves", 0),
                revenue=performance_data.get("revenue", 0.0),
                collaboration_count=performance_data.get("collaboration_count", 0),
                quality_score=performance_data.get("quality_score", 0.0),
                influence_score=performance_data.get("influence_score", 0.0),
                metadata=performance_data.get("metadata", {})
            )
            
            # Store snapshot
            self.performance_snapshots[creator_id].append(snapshot)
            
            # Keep only last 1000 snapshots per creator
            if len(self.performance_snapshots[creator_id]) > 1000:
                self.performance_snapshots[creator_id] = self.performance_snapshots[creator_id][-1000:]
            
            # Queue for analysis
            self.analysis_queue.append((creator_id, snapshot_id))
            
            self.logger.info(f"Recorded performance snapshot {snapshot_id} for creator {creator_id}")
            return snapshot_id
            
        except Exception as e:
            self.logger.error(f"Failed to record performance snapshot: {e}")
            return None
    
    async def analyze_creator_performance(
        self,
        creator_id: str,
        analysis_period_days: int = 30
    ) -> Optional[PerformanceAnalysis]:
        """
        Analyze creator performance over specified period.
        
        Args:
            creator_id: Creator identifier
            analysis_period_days: Analysis period in days
            
        Returns:
            PerformanceAnalysis: Analysis results if successful
        """
        try:
            analysis_id = str(uuid.uuid4())
            
            # Define analysis period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            # Get performance snapshots for period
            creator_snapshots = self.performance_snapshots.get(creator_id, [])
            period_snapshots = [
                snapshot for snapshot in creator_snapshots
                if start_date <= snapshot.timestamp <= end_date
            ]
            
            if not period_snapshots:
                self.logger.warning(f"No performance data found for creator {creator_id} in analysis period")
                return None
            
            # Create performance analysis
            analysis = PerformanceAnalysis(
                analysis_id=analysis_id,
                creator_id=creator_id,
                analysis_period=(start_date, end_date)
            )
            
            # Calculate metric scores
            analysis.metric_scores = await self._calculate_metric_scores(period_snapshots)
            
            # Analyze trends
            analysis.trend_analysis = await self._analyze_performance_trends(period_snapshots)
            
            # Calculate overall score
            analysis.overall_score = await self._calculate_overall_score(analysis.metric_scores)
            
            # Determine performance category
            analysis.performance_category = await self._categorize_performance(analysis.overall_score)
            
            # Identify strengths and improvement areas
            analysis.strengths, analysis.improvement_areas = await self._identify_strengths_and_improvements(
                analysis.metric_scores, analysis.trend_analysis
            )
            
            # Calculate growth potential
            analysis.growth_potential = await self._calculate_growth_potential(analysis)
            
            # Identify risk factors
            analysis.risk_factors = await self._identify_risk_factors(analysis)
            
            # Generate recommendations
            analysis.recommendations = await self._generate_performance_recommendations(analysis)
            
            # Compare with benchmarks
            analysis.benchmark_comparison = await self._compare_with_benchmarks(analysis.metric_scores)
            
            # Calculate prediction confidence
            analysis.prediction_confidence = await self._calculate_prediction_confidence(period_snapshots)
            
            # Store analysis
            self.performance_analyses[analysis_id] = analysis
            
            self.logger.info(f"Completed performance analysis {analysis_id} for creator {creator_id}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze creator performance: {e}")
            return None
    
    async def _calculate_metric_scores(self, snapshots: List[PerformanceSnapshot]) -> Dict[PerformanceMetric, float]:
        """Calculate performance metric scores from snapshots."""
        try:
            metric_scores = {}
            
            if not snapshots:
                return metric_scores
            
            # Engagement rate score
            engagement_rates = [s.engagement_rate for s in snapshots if s.engagement_rate > 0]
            if engagement_rates:
                avg_engagement = statistics.mean(engagement_rates)
                metric_scores[PerformanceMetric.ENGAGEMENT_RATE] = min(1.0, avg_engagement / 0.1)  # Normalize to 10%
            
            # Audience growth score
            if len(snapshots) > 1:
                first_audience = snapshots[0].audience_size
                last_audience = snapshots[-1].audience_size
                if first_audience > 0:
                    growth_rate = (last_audience - first_audience) / first_audience
                    metric_scores[PerformanceMetric.AUDIENCE_GROWTH] = min(1.0, max(0.0, (growth_rate + 0.1) / 0.5))  # Normalize around 40% growth
            
            # Content quality score
            quality_scores = [s.quality_score for s in snapshots if s.quality_score > 0]
            if quality_scores:
                metric_scores[PerformanceMetric.CONTENT_QUALITY] = statistics.mean(quality_scores)
            
            # Revenue performance score
            revenues = [s.revenue for s in snapshots if s.revenue > 0]
            if revenues:
                avg_revenue = statistics.mean(revenues)
                metric_scores[PerformanceMetric.REVENUE_PERFORMANCE] = min(1.0, avg_revenue / 10000.0)  # Normalize to $10k
            
            # Collaboration success score
            collaboration_counts = [s.collaboration_count for s in snapshots]
            if collaboration_counts:
                avg_collaborations = statistics.mean(collaboration_counts)
                metric_scores[PerformanceMetric.COLLABORATION_SUCCESS] = min(1.0, avg_collaborations / 10.0)  # Normalize to 10 collaborations
            
            # Influence score
            influence_scores = [s.influence_score for s in snapshots if s.influence_score > 0]
            if influence_scores:
                metric_scores[PerformanceMetric.INFLUENCE_SCORE] = statistics.mean(influence_scores)
            
            # Consistency score (based on variance)
            engagement_variance = statistics.variance(engagement_rates) if len(engagement_rates) > 1 else 0
            consistency_score = max(0.0, 1.0 - engagement_variance * 10)  # Lower variance = higher consistency
            metric_scores[PerformanceMetric.CONSISTENCY_SCORE] = consistency_score
            
            return metric_scores
            
        except Exception as e:
            self.logger.error(f"Failed to calculate metric scores: {e}")
            return {}
    
    async def _analyze_performance_trends(self, snapshots: List[PerformanceSnapshot]) -> Dict[PerformanceMetric, TrendDirection]:
        """Analyze performance trends from snapshots."""
        try:
            trends = {}
            
            if len(snapshots) < 3:
                return trends
            
            # Analyze engagement rate trend
            engagement_rates = [s.engagement_rate for s in snapshots if s.engagement_rate > 0]
            if len(engagement_rates) >= 3:
                trends[PerformanceMetric.ENGAGEMENT_RATE] = self._calculate_trend_direction(engagement_rates)
            
            # Analyze audience growth trend
            audience_sizes = [s.audience_size for s in snapshots]
            if len(audience_sizes) >= 3:
                trends[PerformanceMetric.AUDIENCE_GROWTH] = self._calculate_trend_direction(audience_sizes)
            
            # Analyze revenue trend
            revenues = [s.revenue for s in snapshots if s.revenue > 0]
            if len(revenues) >= 3:
                trends[PerformanceMetric.REVENUE_PERFORMANCE] = self._calculate_trend_direction(revenues)
            
            # Analyze quality trend
            quality_scores = [s.quality_score for s in snapshots if s.quality_score > 0]
            if len(quality_scores) >= 3:
                trends[PerformanceMetric.CONTENT_QUALITY] = self._calculate_trend_direction(quality_scores)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to analyze performance trends: {e}")
            return {}
    
    def _calculate_trend_direction(self, values: List[float]) -> TrendDirection:
        """Calculate trend direction from a series of values."""
        try:
            if len(values) < 3:
                return TrendDirection.STABLE
            
            # Calculate moving averages
            window_size = min(3, len(values) // 2)
            if window_size < 2:
                return TrendDirection.STABLE
            
            early_avg = statistics.mean(values[:window_size])
            late_avg = statistics.mean(values[-window_size:])
            
            if early_avg == 0:
                return TrendDirection.STABLE
            
            change_rate = (late_avg - early_avg) / early_avg
            
            # Calculate volatility
            variance = statistics.variance(values) if len(values) > 1 else 0
            cv = (variance ** 0.5) / statistics.mean(values) if statistics.mean(values) > 0 else 0
            
            # High volatility indicates volatile trend
            if cv > 0.5:
                return TrendDirection.VOLATILE
            
            # Determine trend based on change rate
            if change_rate > 0.2:
                return TrendDirection.RAPID_GROWTH
            elif change_rate > 0.05:
                return TrendDirection.STEADY_GROWTH
            elif change_rate > -0.05:
                return TrendDirection.STABLE
            elif change_rate > -0.2:
                return TrendDirection.SLIGHT_DECLINE
            else:
                return TrendDirection.DECLINING
                
        except Exception as e:
            self.logger.error(f"Failed to calculate trend direction: {e}")
            return TrendDirection.STABLE
    
    async def _calculate_overall_score(self, metric_scores: Dict[PerformanceMetric, float]) -> float:
        """Calculate overall performance score."""
        try:
            if not metric_scores:
                return 0.0
            
            # Weighted scoring
            weights = {
                PerformanceMetric.ENGAGEMENT_RATE: 0.2,
                PerformanceMetric.AUDIENCE_GROWTH: 0.2,
                PerformanceMetric.CONTENT_QUALITY: 0.15,
                PerformanceMetric.REVENUE_PERFORMANCE: 0.15,
                PerformanceMetric.COLLABORATION_SUCCESS: 0.1,
                PerformanceMetric.BRAND_STRENGTH: 0.1,
                PerformanceMetric.INFLUENCE_SCORE: 0.05,
                PerformanceMetric.CONSISTENCY_SCORE: 0.05
            }
            
            weighted_sum = 0.0
            total_weight = 0.0
            
            for metric, score in metric_scores.items():
                weight = weights.get(metric, 0.1)
                weighted_sum += score * weight
                total_weight += weight
            
            overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
            
            return min(1.0, max(0.0, overall_score))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate overall score: {e}")
            return 0.0
    
    async def _categorize_performance(self, overall_score: float) -> PerformanceCategory:
        """Categorize performance based on overall score."""
        try:
            categories = self.benchmark_data["performance_categories"]
            
            if overall_score >= categories[PerformanceCategory.EXCEPTIONAL]["min_score"]:
                return PerformanceCategory.EXCEPTIONAL
            elif overall_score >= categories[PerformanceCategory.ABOVE_AVERAGE]["min_score"]:
                return PerformanceCategory.ABOVE_AVERAGE
            elif overall_score >= categories[PerformanceCategory.AVERAGE]["min_score"]:
                return PerformanceCategory.AVERAGE
            elif overall_score >= categories[PerformanceCategory.BELOW_AVERAGE]["min_score"]:
                return PerformanceCategory.BELOW_AVERAGE
            else:
                return PerformanceCategory.NEEDS_IMPROVEMENT
                
        except Exception as e:
            self.logger.error(f"Failed to categorize performance: {e}")
            return PerformanceCategory.AVERAGE
    
    async def _identify_strengths_and_improvements(
        self,
        metric_scores: Dict[PerformanceMetric, float],
        trend_analysis: Dict[PerformanceMetric, TrendDirection]
    ) -> Tuple[List[str], List[str]]:
        """Identify strengths and improvement areas."""
        try:
            strengths = []
            improvements = []
            
            industry_averages = self.benchmark_data["industry_averages"]
            
            for metric, score in metric_scores.items():
                industry_avg = industry_averages.get(metric, 0.5)
                trend = trend_analysis.get(metric, TrendDirection.STABLE)
                
                # Identify strengths
                if score > industry_avg * 1.2 or trend in [TrendDirection.RAPID_GROWTH, TrendDirection.STEADY_GROWTH]:
                    strength_msg = f"Strong {metric.value.replace('_', ' ')}"
                    if trend in [TrendDirection.RAPID_GROWTH, TrendDirection.STEADY_GROWTH]:
                        strength_msg += f" with {trend.value.replace('_', ' ')} trend"
                    strengths.append(strength_msg)
                
                # Identify improvement areas
                elif score < industry_avg * 0.8 or trend in [TrendDirection.DECLINING, TrendDirection.SLIGHT_DECLINE]:
                    improvement_msg = f"Improve {metric.value.replace('_', ' ')}"
                    if trend in [TrendDirection.DECLINING, TrendDirection.SLIGHT_DECLINE]:
                        improvement_msg += f" (currently {trend.value.replace('_', ' ')})"
                    improvements.append(improvement_msg)
            
            return strengths, improvements
            
        except Exception as e:
            self.logger.error(f"Failed to identify strengths and improvements: {e}")
            return [], []
    
    async def _calculate_growth_potential(self, analysis: PerformanceAnalysis) -> float:
        """Calculate growth potential score."""
        try:
            potential_factors = []
            
            # Current performance level (room for improvement)
            performance_gap = 1.0 - analysis.overall_score
            potential_factors.append(performance_gap * 0.3)
            
            # Trend momentum
            positive_trends = sum(
                1 for trend in analysis.trend_analysis.values()
                if trend in [TrendDirection.RAPID_GROWTH, TrendDirection.STEADY_GROWTH]
            )
            total_trends = len(analysis.trend_analysis)
            trend_momentum = positive_trends / total_trends if total_trends > 0 else 0
            potential_factors.append(trend_momentum * 0.4)
            
            # Consistency factor
            consistency_score = analysis.metric_scores.get(PerformanceMetric.CONSISTENCY_SCORE, 0.5)
            potential_factors.append(consistency_score * 0.3)
            
            growth_potential = sum(potential_factors)
            
            return min(1.0, max(0.0, growth_potential))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate growth potential: {e}")
            return 0.5
    
    async def _identify_risk_factors(self, analysis: PerformanceAnalysis) -> List[str]:
        """Identify performance risk factors."""
        try:
            risk_factors = []
            
            # Declining trends
            declining_metrics = [
                metric.value for metric, trend in analysis.trend_analysis.items()
                if trend in [TrendDirection.DECLINING, TrendDirection.SLIGHT_DECLINE]
            ]
            if declining_metrics:
                risk_factors.append(f"Declining trends in: {', '.join(declining_metrics)}")
            
            # Volatile performance
            volatile_metrics = [
                metric.value for metric, trend in analysis.trend_analysis.items()
                if trend == TrendDirection.VOLATILE
            ]
            if volatile_metrics:
                risk_factors.append(f"High volatility in: {', '.join(volatile_metrics)}")
            
            # Low consistency
            consistency_score = analysis.metric_scores.get(PerformanceMetric.CONSISTENCY_SCORE, 0.5)
            if consistency_score < 0.4:
                risk_factors.append("Low performance consistency")
            
            # Below average in critical metrics
            critical_metrics = [PerformanceMetric.ENGAGEMENT_RATE, PerformanceMetric.AUDIENCE_GROWTH]
            industry_averages = self.benchmark_data["industry_averages"]
            
            for metric in critical_metrics:
                score = analysis.metric_scores.get(metric, 0)
                avg = industry_averages.get(metric, 0.5)
                if score < avg * 0.7:
                    risk_factors.append(f"Below average {metric.value.replace('_', ' ')}")
            
            return risk_factors
            
        except Exception as e:
            self.logger.error(f"Failed to identify risk factors: {e}")
            return []
    
    async def _generate_performance_recommendations(self, analysis: PerformanceAnalysis) -> List[str]:
        """Generate AI-powered performance recommendations."""
        try:
            recommendations = []
            
            # Recommendations based on improvement areas
            for improvement in analysis.improvement_areas:
                if "engagement" in improvement.lower():
                    recommendations.extend([
                        "Increase content interaction elements (polls, Q&A, calls-to-action)",
                        "Optimize posting times based on audience activity patterns",
                        "Create more engaging content formats (stories, live streams)"
                    ])
                elif "audience growth" in improvement.lower():
                    recommendations.extend([
                        "Implement cross-platform promotion strategies",
                        "Collaborate with other creators for audience expansion",
                        "Optimize content for discoverability (SEO, hashtags)"
                    ])
                elif "content quality" in improvement.lower():
                    recommendations.extend([
                        "Invest in better production equipment and editing",
                        "Develop content planning and scripting processes",
                        "Analyze top-performing content for quality patterns"
                    ])
                elif "revenue" in improvement.lower():
                    recommendations.extend([
                        "Diversify revenue streams (subscriptions, merchandise, courses)",
                        "Optimize pricing strategies based on value delivery",
                        "Implement upselling and cross-selling tactics"
                    ])
            
            # Recommendations based on performance category
            if analysis.performance_category == PerformanceCategory.NEEDS_IMPROVEMENT:
                recommendations.extend([
                    "Focus on fundamental content quality improvements",
                    "Establish consistent posting schedule",
                    "Study successful creators in your niche for best practices"
                ])
            elif analysis.performance_category == PerformanceCategory.EXCEPTIONAL:
                recommendations.extend([
                    "Maintain excellence while exploring new content formats",
                    "Consider mentoring other creators for additional revenue",
                    "Leverage strong performance for premium brand partnerships"
                ])
            
            # Remove duplicates and limit recommendations
            unique_recommendations = list(set(recommendations))
            return unique_recommendations[:10]  # Top 10 recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance recommendations: {e}")
            return ["Analyze performance data and adjust content strategy accordingly"]
    
    async def _compare_with_benchmarks(self, metric_scores: Dict[PerformanceMetric, float]) -> Dict[str, float]:
        """Compare performance with industry benchmarks."""
        try:
            benchmark_comparison = {}
            industry_averages = self.benchmark_data["industry_averages"]
            
            for metric, score in metric_scores.items():
                benchmark_avg = industry_averages.get(metric, 0.5)
                
                if benchmark_avg > 0:
                    ratio = score / benchmark_avg
                    benchmark_comparison[f"{metric.value}_vs_industry"] = ratio
            
            return benchmark_comparison
            
        except Exception as e:
            self.logger.error(f"Failed to compare with benchmarks: {e}")
            return {}
    
    async def _calculate_prediction_confidence(self, snapshots: List[PerformanceSnapshot]) -> float:
        """Calculate prediction confidence based on data quality."""
        try:
            confidence_factors = []
            
            # Data quantity factor
            data_quantity = len(snapshots)
            quantity_score = min(1.0, data_quantity / 30)  # 30 snapshots = max confidence
            confidence_factors.append(quantity_score * 0.4)
            
            # Data consistency factor
            if len(snapshots) > 1:
                engagement_rates = [s.engagement_rate for s in snapshots if s.engagement_rate > 0]
                if len(engagement_rates) > 1:
                    cv = statistics.stdev(engagement_rates) / statistics.mean(engagement_rates) if statistics.mean(engagement_rates) > 0 else 1
                    consistency_score = max(0.0, 1.0 - cv)
                    confidence_factors.append(consistency_score * 0.3)
            
            # Data recency factor
            latest_snapshot = max(snapshots, key=lambda s: s.timestamp)
            days_since_latest = (datetime.now() - latest_snapshot.timestamp).days
            recency_score = max(0.0, 1.0 - days_since_latest / 30)  # Decay over 30 days
            confidence_factors.append(recency_score * 0.3)
            
            confidence = sum(confidence_factors) if confidence_factors else 0.5
            
            return min(1.0, max(0.1, confidence))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate prediction confidence: {e}")
            return 0.5
    
    async def _process_performance_analysis(self):
        """Process performance analysis queue."""
        while True:
            try:
                if self.analysis_queue:
                    creator_id, snapshot_id = self.analysis_queue.popleft()
                    
                    # Trigger analysis if enough data accumulated
                    creator_snapshots = self.performance_snapshots.get(creator_id, [])
                    if len(creator_snapshots) >= 5:  # Minimum data for analysis
                        await self.analyze_creator_performance(creator_id)
                
                await asyncio.sleep(300)  # Process every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing performance analysis: {e}")
                await asyncio.sleep(600)
    
    async def _generate_growth_predictions(self):
        """Generate AI-powered growth predictions."""
        while True:
            try:
                if self.predictive_engine.get("enabled"):
                    # Generate predictions for creators with sufficient data
                    for creator_id in self.performance_snapshots.keys():
                        snapshots = self.performance_snapshots[creator_id]
                        if len(snapshots) >= 10:  # Minimum for predictions
                            prediction = await self._create_growth_prediction(creator_id, snapshots)
                            if prediction:
                                self.growth_predictions[creator_id] = prediction
                
                await asyncio.sleep(3600)  # Generate predictions hourly
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error generating growth predictions: {e}")
                await asyncio.sleep(1800)
    
    async def _create_growth_prediction(
        self,
        creator_id: str,
        snapshots: List[PerformanceSnapshot]
    ) -> Optional[GrowthPrediction]:
        """Create growth prediction for creator."""
        try:
            prediction_id = str(uuid.uuid4())
            
            # Analyze historical trends
            recent_snapshots = snapshots[-30:]  # Last 30 snapshots
            
            prediction = GrowthPrediction(
                prediction_id=prediction_id,
                creator_id=creator_id,
                prediction_horizon=90  # 90 days
            )
            
            # Predict key metrics (simplified simulation)
            current_engagement = recent_snapshots[-1].engagement_rate if recent_snapshots else 0
            current_audience = recent_snapshots[-1].audience_size if recent_snapshots else 0
            
            # Simulate ML-based predictions
            prediction.predicted_metrics = {
                PerformanceMetric.ENGAGEMENT_RATE: current_engagement * statistics.uniform(0.9, 1.3),
                PerformanceMetric.AUDIENCE_GROWTH: statistics.uniform(0.1, 0.4),  # 10-40% growth
                PerformanceMetric.CONTENT_QUALITY: statistics.uniform(0.7, 0.95),
                PerformanceMetric.REVENUE_PERFORMANCE: statistics.uniform(0.6, 0.9)
            }
            
            # Determine growth trajectory
            avg_growth = statistics.mean([
                pred for pred in prediction.predicted_metrics.values()
                if isinstance(pred, (int, float))
            ])
            
            if avg_growth > 0.8:
                prediction.growth_trajectory = TrendDirection.RAPID_GROWTH
            elif avg_growth > 0.6:
                prediction.growth_trajectory = TrendDirection.STEADY_GROWTH
            else:
                prediction.growth_trajectory = TrendDirection.STABLE
            
            # Calculate success probability
            prediction.success_probability = min(0.95, avg_growth)
            
            # Identify growth drivers
            prediction.key_growth_drivers = [
                "Consistent content quality",
                "Strong audience engagement",
                "Effective collaboration strategies",
                "Market trend alignment"
            ]
            
            # Identify potential obstacles
            prediction.potential_obstacles = [
                "Increased market competition",
                "Algorithm changes",
                "Seasonal content variations",
                "Resource constraints"
            ]
            
            # Generate recommended actions
            prediction.recommended_actions = [
                "Maintain consistent posting schedule",
                "Focus on high-engagement content formats",
                "Explore new collaboration opportunities",
                "Monitor and adapt to market trends"
            ]
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Failed to create growth prediction: {e}")
            return None
    
    async def _update_competitive_intelligence(self):
        """Update competitive intelligence analysis."""
        while True:
            try:
                if self.competitive_analyzer.get("enabled"):
                    # Analyze competitive position for each creator
                    for creator_id in self.performance_snapshots.keys():
                        competitive_intel = await self._analyze_competitive_position(creator_id)
                        if competitive_intel:
                            self.competitive_intelligence[creator_id] = competitive_intel
                
                await asyncio.sleep(self.competitive_analyzer.get("update_frequency", 86400))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error updating competitive intelligence: {e}")
                await asyncio.sleep(3600)
    
    async def _analyze_competitive_position(self, creator_id: str) -> Optional[CompetitiveIntelligence]:
        """Analyze competitive position for creator."""
        try:
            # Get latest performance analysis
            latest_analysis = None
            for analysis in self.performance_analyses.values():
                if analysis.creator_id == creator_id:
                    if not latest_analysis or analysis.analysis_period[1] > latest_analysis.analysis_period[1]:
                        latest_analysis = analysis
            
            if not latest_analysis:
                return None
            
            # Create competitive intelligence
            competitive_intel = CompetitiveIntelligence(creator_id=creator_id)
            
            # Determine competitive position based on performance
            if latest_analysis.performance_category == PerformanceCategory.EXCEPTIONAL:
                competitive_intel.competitive_position = "leader"
            elif latest_analysis.performance_category == PerformanceCategory.ABOVE_AVERAGE:
                competitive_intel.competitive_position = "challenger"
            elif latest_analysis.performance_category == PerformanceCategory.AVERAGE:
                competitive_intel.competitive_position = "follower"
            else:
                competitive_intel.competitive_position = "niche"
            
            # Estimate market share (simplified)
            competitive_intel.market_share_estimate = statistics.uniform(0.01, 0.10)
            
            # Identify competitive advantages
            competitive_intel.competitive_advantages = latest_analysis.strengths[:3]
            
            # Identify competitive gaps
            competitive_intel.competitive_gaps = latest_analysis.improvement_areas[:3]
            
            # Simulate competitor data
            competitive_intel.top_competitors = [
                {
                    "competitor_id": f"competitor_{i}",
                    "market_share": statistics.uniform(0.02, 0.15),
                    "competitive_threat": statistics.choice(["low", "medium", "high"])
                }
                for i in range(3)
            ]
            
            # Identify differentiation opportunities
            competitive_intel.differentiation_opportunities = [
                "Unique content format development",
                "Specialized niche expertise",
                "Premium service offerings",
                "Community building focus"
            ]
            
            # Assess threat level
            declining_trends = sum(
                1 for trend in latest_analysis.trend_analysis.values()
                if trend in [TrendDirection.DECLINING, TrendDirection.SLIGHT_DECLINE]
            )
            
            if declining_trends > 2:
                competitive_intel.threat_level = "high"
            elif declining_trends > 0:
                competitive_intel.threat_level = "medium"
            else:
                competitive_intel.threat_level = "low"
            
            # Market trends alignment
            competitive_intel.market_trends_alignment = statistics.uniform(0.6, 0.9)
            
            return competitive_intel
            
        except Exception as e:
            self.logger.error(f"Failed to analyze competitive position: {e}")
            return None
    
    async def _optimize_performance_recommendations(self):
        """Optimize performance recommendations."""
        while True:
            try:
                # Update optimization insights for all creators
                optimization_insights = {}
                
                for creator_id in self.performance_snapshots.keys():
                    insights = await self._generate_creator_optimization_insights(creator_id)
                    if insights:
                        optimization_insights[creator_id] = insights
                
                self.intelligence_insights = optimization_insights
                
                await asyncio.sleep(1800)  # Update every 30 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error optimizing performance recommendations: {e}")
                await asyncio.sleep(3600)
    
    async def _generate_creator_optimization_insights(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Generate optimization insights for creator."""
        try:
            # Get latest analysis and prediction
            latest_analysis = None
            for analysis in self.performance_analyses.values():
                if analysis.creator_id == creator_id:
                    if not latest_analysis or analysis.analysis_period[1] > latest_analysis.analysis_period[1]:
                        latest_analysis = analysis
            
            prediction = self.growth_predictions.get(creator_id)
            competitive_intel = self.competitive_intelligence.get(creator_id)
            
            if not latest_analysis:
                return None
            
            insights = {
                "optimization_strategies": [],
                "priority_actions": [],
                "resource_requirements": {},
                "expected_impact": {},
                "implementation_timeline": {}
            }
            
            # Generate optimization strategies based on analysis
            for improvement in latest_analysis.improvement_areas:
                if "engagement" in improvement.lower():
                    insights["optimization_strategies"].append({
                        "strategy": "Engagement Optimization",
                        "tactics": [
                            "Implement interactive content elements",
                            "Optimize posting schedule",
                            "Enhance community engagement"
                        ],
                        "expected_impact": "15-30% engagement increase",
                        "timeline": "4-8 weeks"
                    })
                elif "audience" in improvement.lower():
                    insights["optimization_strategies"].append({
                        "strategy": "Audience Growth Acceleration",
                        "tactics": [
                            "Cross-platform promotion",
                            "Strategic collaborations",
                            "SEO optimization"
                        ],
                        "expected_impact": "20-40% follower growth",
                        "timeline": "6-12 weeks"
                    })
            
            # Add competitive-based strategies
            if competitive_intel:
                for gap in competitive_intel.competitive_gaps[:2]:
                    insights["optimization_strategies"].append({
                        "strategy": f"Competitive Gap Closure: {gap}",
                        "tactics": ["Market research", "Feature development", "Skill enhancement"],
                        "expected_impact": "Market position improvement",
                        "timeline": "8-16 weeks"
                    })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization insights: {e}")
            return None
    
    async def _update_market_intelligence(self):
        """Update market intelligence data."""
        while True:
            try:
                # Simulate market intelligence gathering
                market_data = {
                    "market_trends": [
                        {"trend": "Short-form video content", "growth_rate": 0.45, "relevance": "high"},
                        {"trend": "Live streaming", "growth_rate": 0.32, "relevance": "medium"},
                        {"trend": "Audio content/podcasts", "growth_rate": 0.28, "relevance": "high"}
                    ],
                    "emerging_opportunities": [
                        {
                            "opportunity": "AI-assisted content creation",
                            "market_size": "$5.2B",
                            "adoption_rate": "growing"
                        },
                        {
                            "opportunity": "Virtual events and experiences",
                            "market_size": "$3.8B",
                            "adoption_rate": "accelerating"
                        }
                    ],
                    "industry_insights": {
                        "average_creator_earnings": "$4,500/month",
                        "top_10_percent_earnings": "$15,000/month",
                        "fastest_growing_niches": ["Tech education", "Sustainability", "Personal finance"]
                    },
                    "last_updated": datetime.now().isoformat()
                }
                
                self.market_intelligence = market_data
                
                await asyncio.sleep(7200)  # Update every 2 hours
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error updating market intelligence: {e}")
                await asyncio.sleep(3600)
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive performance intelligence dashboard data."""
        try:
            return {
                "performance_overview": await self._get_performance_overview(),
                "growth_predictions": await self._get_predictions_data(),
                "performance_trends": await self._get_trends_data(),
                "competitive_intelligence": await self._get_competitive_data(),
                "performance_optimization": await self._get_optimization_data(),
                "benchmark_comparison": await self._get_benchmark_data(),
                "market_intelligence": self.market_intelligence,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting performance intelligence dashboard data: {e}")
            return {}
    
    async def _get_performance_overview(self) -> Dict[str, Any]:
        """Get performance overview data."""
        all_analyses = list(self.performance_analyses.values())
        
        if not all_analyses:
            return {"message": "No performance analyses available"}
        
        avg_overall_score = statistics.mean([a.overall_score for a in all_analyses])
        avg_growth_potential = statistics.mean([a.growth_potential for a in all_analyses])
        
        category_distribution = defaultdict(int)
        for analysis in all_analyses:
            category_distribution[analysis.performance_category.value] += 1
        
        return {
            "total_creators_analyzed": len(set(a.creator_id for a in all_analyses)),
            "average_overall_score": avg_overall_score,
            "average_growth_potential": avg_growth_potential,
            "performance_category_distribution": dict(category_distribution),
            "top_performers": [
                {"creator_id": a.creator_id, "score": a.overall_score}
                for a in sorted(all_analyses, key=lambda x: x.overall_score, reverse=True)[:5]
            ]
        }
    
    async def _get_predictions_data(self) -> Dict[str, Any]:
        """Get growth predictions data."""
        predictions_data = {}
        
        for creator_id, prediction in self.growth_predictions.items():
            predictions_data[creator_id] = {
                "growth_trajectory": prediction.growth_trajectory.value,
                "success_probability": prediction.success_probability,
                "predicted_metrics": {k.value: v for k, v in prediction.predicted_metrics.items()},
                "key_drivers": prediction.key_growth_drivers[:3],
                "recommended_actions": prediction.recommended_actions[:3]
            }
        
        return predictions_data
    
    async def _get_trends_data(self) -> Dict[str, Any]:
        """Get performance trends data."""
        all_analyses = list(self.performance_analyses.values())
        
        if not all_analyses:
            return {}
        
        # Aggregate trend data
        trend_summary = defaultdict(lambda: defaultdict(int))
        
        for analysis in all_analyses:
            for metric, trend in analysis.trend_analysis.items():
                trend_summary[metric.value][trend.value] += 1
        
        return {
            "trend_distribution": {
                metric: dict(trends) for metric, trends in trend_summary.items()
            },
            "trending_up_creators": len([
                a for a in all_analyses
                if any(t in [TrendDirection.RAPID_GROWTH, TrendDirection.STEADY_GROWTH] 
                      for t in a.trend_analysis.values())
            ]),
            "at_risk_creators": len([
                a for a in all_analyses
                if any(t in [TrendDirection.DECLINING, TrendDirection.SLIGHT_DECLINE]
                      for t in a.trend_analysis.values())
            ])
        }
    
    async def _get_competitive_data(self) -> Dict[str, Any]:
        """Get competitive intelligence data."""
        competitive_data = {}
        
        for creator_id, intel in self.competitive_intelligence.items():
            competitive_data[creator_id] = {
                "competitive_position": intel.competitive_position,
                "market_share_estimate": intel.market_share_estimate,
                "threat_level": intel.threat_level,
                "competitive_advantages": intel.competitive_advantages[:3],
                "top_competitors_count": len(intel.top_competitors)
            }
        
        return competitive_data
    
    async def _get_optimization_data(self) -> Dict[str, Any]:
        """Get optimization recommendations data."""
        return {
            "optimization_insights": self.intelligence_insights,
            "total_strategies": sum(
                len(insights.get("optimization_strategies", []))
                for insights in self.intelligence_insights.values()
            ),
            "high_impact_opportunities": len([
                strategy for insights in self.intelligence_insights.values()
                for strategy in insights.get("optimization_strategies", [])
                if "15-30%" in strategy.get("expected_impact", "") or "20-40%" in strategy.get("expected_impact", "")
            ])
        }
    
    async def _get_benchmark_data(self) -> Dict[str, Any]:
        """Get benchmark comparison data."""
        all_analyses = list(self.performance_analyses.values())
        
        if not all_analyses:
            return {}
        
        # Calculate percentile rankings
        overall_scores = [a.overall_score for a in all_analyses]
        percentile_rankings = {}
        
        for analysis in all_analyses:
            percentile = (sum(1 for score in overall_scores if score <= analysis.overall_score) / len(overall_scores)) * 100
            percentile_rankings[analysis.creator_id] = percentile
        
        return {
            "industry_benchmarks": self.benchmark_data["industry_averages"],
            "percentile_rankings": percentile_rankings,
            "top_10_percent_threshold": sorted(overall_scores, reverse=True)[max(0, len(overall_scores) // 10 - 1)] if overall_scores else 0
        }
    
    async def shutdown(self):
        """Shutdown performance intelligence dashboard."""
        try:
            self.logger.info(f"Shutting down Creator Performance Intelligence Dashboard {self.dashboard_id}")
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Clear caches
            self.performance_snapshots.clear()
            self.performance_analyses.clear()
            self.growth_predictions.clear()
            self.competitive_intelligence.clear()
            
            # Shutdown enterprise system
            await self.enterprise_system.shutdown()
            
            self.logger.info(f"Creator Performance Intelligence Dashboard {self.dashboard_id} shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during performance intelligence dashboard shutdown: {e}")

# Factory function for creating performance intelligence dashboard
async def create_performance_intelligence_dashboard(
    dashboard_id: str,
    config: Dict[str, Any]
) -> CreatorPerformanceIntelligenceDashboard:
    """
    Create and initialize performance intelligence dashboard.
    
    Args:
        dashboard_id: Unique dashboard identifier
        config: Dashboard configuration
        
    Returns:
        CreatorPerformanceIntelligenceDashboard: Initialized dashboard instance
    """
    dashboard = CreatorPerformanceIntelligenceDashboard(dashboard_id, config)
    await dashboard.initialize()
    return dashboard

# Export main components
__all__ = [
    "CreatorPerformanceIntelligenceDashboard",
    "PerformanceSnapshot",
    "PerformanceAnalysis", 
    "GrowthPrediction",
    "CompetitiveIntelligence",
    "PerformanceMetric",
    "TrendDirection",
    "PerformanceCategory",
    "create_performance_intelligence_dashboard"
]