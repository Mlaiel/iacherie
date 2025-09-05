"""Creator Voice Performance Analytics Engine

Advanced analytics system for tracking, analyzing, and optimizing creator voice
performance metrics across multiple dimensions and platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
import json
from collections import defaultdict
import statistics

try:
    from .creator_voice_intelligence import CreatorType, VoiceContentType, CreatorVoiceProfile
except ImportError:
    from creator_voice_intelligence import CreatorType, VoiceContentType, CreatorVoiceProfile

logger = logging.getLogger(__name__)


class AnalyticsMetric(Enum):
    """Core analytics metrics for voice content"""
    ENGAGEMENT_RATE = "engagement_rate"
    LISTEN_THROUGH_RATE = "listen_through_rate"
    AUDIENCE_RETENTION = "audience_retention"
    QUALITY_SCORE = "quality_score"
    COMMERCIAL_PERFORMANCE = "commercial_performance"
    VIRAL_COEFFICIENT = "viral_coefficient"
    AUDIENCE_GROWTH = "audience_growth"
    REVENUE_GENERATION = "revenue_generation"
    COLLABORATION_SUCCESS = "collaboration_success"
    SEO_PERFORMANCE = "seo_performance"


class TimeFrame(Enum):
    """Time frame options for analytics"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    REAL_TIME = "real_time"
    CUSTOM = "custom"


class PerformanceTrend(Enum):
    """Performance trend indicators"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    BREAKTHROUGH = "breakthrough"
    DECLINING = "declining"


@dataclass
class PerformanceMetric:
    """Individual performance metric data point"""
    metric_name: str
    value: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsSnapshot:
    """Analytics snapshot for a specific time period"""
    creator_id: str
    time_frame: TimeFrame
    start_date: datetime
    end_date: datetime
    metrics: Dict[str, PerformanceMetric]
    aggregated_data: Dict[str, Any]
    trends: Dict[str, PerformanceTrend]
    insights: List[str]
    recommendations: List[str]
    comparative_analysis: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ContentPerformanceAnalysis:
    """Performance analysis for individual content pieces"""
    content_id: str
    creator_id: str
    content_type: VoiceContentType
    performance_score: float
    engagement_metrics: Dict[str, float]
    audience_metrics: Dict[str, Any]
    revenue_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    platform_performance: Dict[str, Dict[str, float]]
    lifecycle_stage: str
    optimization_opportunities: List[str]
    benchmark_comparison: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AudienceSegment:
    """Audience segment analysis"""
    segment_id: str
    segment_name: str
    demographics: Dict[str, Any]
    preferences: Dict[str, Any]
    engagement_patterns: Dict[str, float]
    value_metrics: Dict[str, float]
    growth_rate: float
    retention_rate: float
    segment_size: int
    revenue_contribution: float


@dataclass
class CompetitiveAnalysis:
    """Competitive landscape analysis"""
    creator_id: str
    market_position: str
    competitive_rank: int
    market_share: float
    key_competitors: List[Dict[str, Any]]
    competitive_advantages: List[str]
    opportunity_gaps: List[str]
    threat_analysis: List[str]
    differentiation_score: float
    market_trend_alignment: float


class CreatorVoiceAnalytics:
    """Advanced Creator Voice Performance Analytics Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Analytics storage
        self.performance_history: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.analytics_snapshots: Dict[str, List[AnalyticsSnapshot]] = defaultdict(list)
        self.content_analytics: Dict[str, ContentPerformanceAnalysis] = {}
        self.audience_segments: Dict[str, Dict[str, AudienceSegment]] = defaultdict(dict)
        
        # Analytics models and processors
        self.trend_analyzer = None
        self.prediction_model = None
        self.benchmark_data = {}
        
        # Performance benchmarks by creator type
        self.performance_benchmarks = self._initialize_performance_benchmarks()
        
        # Analytics configuration
        self.metric_weights = self._initialize_metric_weights()
        self.alert_thresholds = self._initialize_alert_thresholds()
        
    def _initialize_performance_benchmarks(self) -> Dict[CreatorType, Dict[str, float]]:
        """Initialize performance benchmarks by creator type"""
        return {
            CreatorType.MUSICIAN: {
                "engagement_rate": 0.08,
                "listen_through_rate": 0.65,
                "audience_retention": 0.72,
                "quality_score": 0.75,
                "commercial_performance": 0.15,
                "viral_coefficient": 0.12,
                "audience_growth": 0.05,
                "revenue_generation": 1000.0,
                "collaboration_success": 0.25,
                "seo_performance": 0.45
            },
            CreatorType.PODCASTER: {
                "engagement_rate": 0.12,
                "listen_through_rate": 0.55,
                "audience_retention": 0.68,
                "quality_score": 0.70,
                "commercial_performance": 0.20,
                "viral_coefficient": 0.08,
                "audience_growth": 0.08,
                "revenue_generation": 800.0,
                "collaboration_success": 0.30,
                "seo_performance": 0.55
            },
            CreatorType.NARRATOR: {
                "engagement_rate": 0.15,
                "listen_through_rate": 0.80,
                "audience_retention": 0.85,
                "quality_score": 0.80,
                "commercial_performance": 0.25,
                "viral_coefficient": 0.05,
                "audience_growth": 0.04,
                "revenue_generation": 1200.0,
                "collaboration_success": 0.20,
                "seo_performance": 0.40
            },
            CreatorType.VOICE_ACTOR: {
                "engagement_rate": 0.10,
                "listen_through_rate": 0.70,
                "audience_retention": 0.75,
                "quality_score": 0.85,
                "commercial_performance": 0.30,
                "viral_coefficient": 0.06,
                "audience_growth": 0.03,
                "revenue_generation": 1500.0,
                "collaboration_success": 0.35,
                "seo_performance": 0.35
            },
            CreatorType.SINGER: {
                "engagement_rate": 0.10,
                "listen_through_rate": 0.60,
                "audience_retention": 0.70,
                "quality_score": 0.78,
                "commercial_performance": 0.18,
                "viral_coefficient": 0.15,
                "audience_growth": 0.06,
                "revenue_generation": 1100.0,
                "collaboration_success": 0.28,
                "seo_performance": 0.50
            }
        }
    
    def _initialize_metric_weights(self) -> Dict[str, float]:
        """Initialize metric weights for overall performance calculation"""
        return {
            "engagement_rate": 0.20,
            "listen_through_rate": 0.15,
            "audience_retention": 0.15,
            "quality_score": 0.15,
            "commercial_performance": 0.10,
            "viral_coefficient": 0.05,
            "audience_growth": 0.10,
            "revenue_generation": 0.10
        }
    
    def _initialize_alert_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize alert thresholds for performance monitoring"""
        return {
            "critical": {
                "engagement_rate": 0.02,
                "listen_through_rate": 0.30,
                "audience_retention": 0.40,
                "quality_score": 0.50,
                "audience_growth": -0.10
            },
            "warning": {
                "engagement_rate": 0.05,
                "listen_through_rate": 0.50,
                "audience_retention": 0.60,
                "quality_score": 0.65,
                "audience_growth": -0.05
            },
            "good": {
                "engagement_rate": 0.10,
                "listen_through_rate": 0.70,
                "audience_retention": 0.75,
                "quality_score": 0.80,
                "audience_growth": 0.05
            }
        }
    
    async def track_performance_metric(
        self,
        creator_id: str,
        metric_name: str,
        value: float,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track a performance metric for a creator"""
        
        try:
            metric = PerformanceMetric(
                metric_name=metric_name,
                value=value,
                timestamp=datetime.now(),
                context=context or {},
                metadata=metadata or {}
            )
            
            self.performance_history[creator_id].append(metric)
            
            # Check for alerts
            await self._check_performance_alerts(creator_id, metric)
            
            self.logger.info(f"Tracked metric {metric_name} for creator {creator_id}: {value}")
            
        except Exception as e:
            self.logger.error(f"Error tracking performance metric: {str(e)}")
            raise
    
    async def analyze_creator_performance(
        self,
        creator_id: str,
        creator_type: CreatorType,
        time_frame: TimeFrame = TimeFrame.MONTHLY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AnalyticsSnapshot:
        """Analyze comprehensive creator performance"""
        
        try:
            self.logger.info(f"Analyzing performance for creator {creator_id}")
            
            # Determine time range
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = self._get_start_date_for_timeframe(end_date, time_frame)
            
            # Get performance data for time period
            metrics_data = await self._get_metrics_for_period(creator_id, start_date, end_date)
            
            # Calculate aggregated metrics
            aggregated_data = await self._calculate_aggregated_metrics(metrics_data, creator_type)
            
            # Analyze trends
            trends = await self._analyze_performance_trends(creator_id, metrics_data, time_frame)
            
            # Generate insights
            insights = await self._generate_performance_insights(aggregated_data, trends, creator_type)
            
            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(
                aggregated_data, trends, creator_type, insights
            )
            
            # Comparative analysis
            comparative_analysis = await self._perform_comparative_analysis(
                creator_id, aggregated_data, creator_type
            )
            
            # Create performance metrics
            performance_metrics = {}
            for metric_name, data in aggregated_data.items():
                performance_metrics[metric_name] = PerformanceMetric(
                    metric_name=metric_name,
                    value=data.get("average", 0.0),
                    timestamp=datetime.now(),
                    context={"aggregation_type": "average", "time_frame": time_frame.value},
                    metadata=data
                )
            
            # Create analytics snapshot
            snapshot = AnalyticsSnapshot(
                creator_id=creator_id,
                time_frame=time_frame,
                start_date=start_date,
                end_date=end_date,
                metrics=performance_metrics,
                aggregated_data=aggregated_data,
                trends=trends,
                insights=insights,
                recommendations=recommendations,
                comparative_analysis=comparative_analysis
            )
            
            # Store snapshot
            self.analytics_snapshots[creator_id].append(snapshot)
            
            self.logger.info(f"Performance analysis completed for creator {creator_id}")
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Error analyzing creator performance: {str(e)}")
            raise
    
    async def analyze_content_performance(
        self,
        content_id: str,
        creator_id: str,
        content_type: VoiceContentType,
        performance_data: Dict[str, Any],
        platform_data: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> ContentPerformanceAnalysis:
        """Analyze performance of individual content pieces"""
        
        try:
            self.logger.info(f"Analyzing content performance for {content_id}")
            
            # Extract metrics from performance data
            engagement_metrics = performance_data.get("engagement", {})
            audience_metrics = performance_data.get("audience", {})
            revenue_metrics = performance_data.get("revenue", {})
            quality_metrics = performance_data.get("quality", {})
            
            # Calculate overall performance score
            performance_score = await self._calculate_content_performance_score(
                engagement_metrics, audience_metrics, revenue_metrics, quality_metrics, content_type
            )
            
            # Analyze platform performance
            platform_performance = {}
            if platform_data:
                for platform, data in platform_data.items():
                    platform_performance[platform] = await self._analyze_platform_performance(
                        data, content_type
                    )
            
            # Determine lifecycle stage
            lifecycle_stage = await self._determine_content_lifecycle_stage(
                content_id, engagement_metrics, audience_metrics
            )
            
            # Identify optimization opportunities
            optimization_opportunities = await self._identify_content_optimization_opportunities(
                engagement_metrics, audience_metrics, revenue_metrics, quality_metrics, content_type
            )
            
            # Benchmark comparison
            benchmark_comparison = await self._compare_to_benchmarks(
                performance_score, engagement_metrics, content_type
            )
            
            # Create analysis
            analysis = ContentPerformanceAnalysis(
                content_id=content_id,
                creator_id=creator_id,
                content_type=content_type,
                performance_score=performance_score,
                engagement_metrics=engagement_metrics,
                audience_metrics=audience_metrics,
                revenue_metrics=revenue_metrics,
                quality_metrics=quality_metrics,
                platform_performance=platform_performance,
                lifecycle_stage=lifecycle_stage,
                optimization_opportunities=optimization_opportunities,
                benchmark_comparison=benchmark_comparison
            )
            
            # Store analysis
            self.content_analytics[content_id] = analysis
            
            self.logger.info(f"Content performance analysis completed for {content_id}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing content performance: {str(e)}")
            raise
    
    async def analyze_audience_segments(
        self,
        creator_id: str,
        audience_data: Dict[str, Any],
        engagement_data: Dict[str, Any]
    ) -> Dict[str, AudienceSegment]:
        """Analyze and segment audience for targeted insights"""
        
        try:
            self.logger.info(f"Analyzing audience segments for creator {creator_id}")
            
            segments = {}
            
            # Demographic segmentation
            demographic_segments = await self._create_demographic_segments(audience_data)
            
            # Behavioral segmentation
            behavioral_segments = await self._create_behavioral_segments(engagement_data)
            
            # Value-based segmentation
            value_segments = await self._create_value_based_segments(audience_data, engagement_data)
            
            # Combine and analyze segments
            all_segments = {**demographic_segments, **behavioral_segments, **value_segments}
            
            for segment_id, segment_data in all_segments.items():
                segment = AudienceSegment(
                    segment_id=segment_id,
                    segment_name=segment_data["name"],
                    demographics=segment_data.get("demographics", {}),
                    preferences=segment_data.get("preferences", {}),
                    engagement_patterns=segment_data.get("engagement_patterns", {}),
                    value_metrics=segment_data.get("value_metrics", {}),
                    growth_rate=segment_data.get("growth_rate", 0.0),
                    retention_rate=segment_data.get("retention_rate", 0.0),
                    segment_size=segment_data.get("size", 0),
                    revenue_contribution=segment_data.get("revenue_contribution", 0.0)
                )
                segments[segment_id] = segment
            
            # Store segments
            self.audience_segments[creator_id] = segments
            
            self.logger.info(f"Audience segmentation completed for creator {creator_id}")
            return segments
            
        except Exception as e:
            self.logger.error(f"Error analyzing audience segments: {str(e)}")
            raise
    
    async def generate_performance_forecast(
        self,
        creator_id: str,
        creator_type: CreatorType,
        forecast_horizon: int = 30,  # days
        scenario_factors: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Generate performance forecast based on historical data and trends"""
        
        try:
            self.logger.info(f"Generating performance forecast for creator {creator_id}")
            
            # Get historical performance data
            historical_data = await self._get_historical_performance_data(creator_id, days=90)
            
            # Analyze trends and patterns
            trend_analysis = await self._analyze_forecast_trends(historical_data)
            
            # Apply scenario factors
            scenario_adjustments = scenario_factors or {}
            
            # Generate forecasts for key metrics
            forecasted_metrics = {}
            for metric in AnalyticsMetric:
                metric_history = [data for data in historical_data if data.metric_name == metric.value]
                if metric_history:
                    forecast = await self._forecast_metric(
                        metric_history, forecast_horizon, trend_analysis, scenario_adjustments
                    )
                    forecasted_metrics[metric.value] = forecast
            
            # Calculate confidence intervals
            confidence_intervals = await self._calculate_forecast_confidence(
                forecasted_metrics, historical_data
            )
            
            # Generate growth projections
            growth_projections = await self._calculate_growth_projections(
                forecasted_metrics, creator_type
            )
            
            # Identify potential opportunities and risks
            opportunities = await self._identify_forecast_opportunities(forecasted_metrics, trend_analysis)
            risks = await self._identify_forecast_risks(forecasted_metrics, trend_analysis)
            
            forecast = {
                "creator_id": creator_id,
                "forecast_horizon_days": forecast_horizon,
                "forecasted_metrics": forecasted_metrics,
                "trend_analysis": trend_analysis,
                "confidence_intervals": confidence_intervals,
                "growth_projections": growth_projections,
                "opportunities": opportunities,
                "risks": risks,
                "scenario_factors": scenario_adjustments,
                "generated_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Performance forecast generated for creator {creator_id}")
            return forecast
            
        except Exception as e:
            self.logger.error(f"Error generating performance forecast: {str(e)}")
            raise
    
    async def compare_creator_performance(
        self,
        creator_ids: List[str],
        creator_types: List[CreatorType],
        comparison_metrics: List[str],
        time_frame: TimeFrame = TimeFrame.MONTHLY
    ) -> Dict[str, Any]:
        """Compare performance across multiple creators"""
        
        try:
            self.logger.info(f"Comparing performance for creators: {creator_ids}")
            
            comparison_data = {}
            
            # Get performance data for each creator
            for i, creator_id in enumerate(creator_ids):
                creator_type = creator_types[i] if i < len(creator_types) else CreatorType.MUSICIAN
                
                snapshot = await self.analyze_creator_performance(
                    creator_id, creator_type, time_frame
                )
                
                comparison_data[creator_id] = {
                    "creator_type": creator_type.value,
                    "metrics": {metric: snapshot.aggregated_data.get(metric, {}).get("average", 0.0) 
                              for metric in comparison_metrics},
                    "overall_score": await self._calculate_overall_performance_score(snapshot.aggregated_data),
                    "strengths": await self._identify_performance_strengths(snapshot.aggregated_data, creator_type),
                    "weaknesses": await self._identify_performance_weaknesses(snapshot.aggregated_data, creator_type)
                }
            
            # Calculate rankings
            rankings = await self._calculate_creator_rankings(comparison_data, comparison_metrics)
            
            # Identify top performers
            top_performers = await self._identify_top_performers(comparison_data, rankings)
            
            # Generate insights
            comparison_insights = await self._generate_comparison_insights(comparison_data, rankings)
            
            comparison_result = {
                "creators_compared": creator_ids,
                "comparison_metrics": comparison_metrics,
                "time_frame": time_frame.value,
                "performance_data": comparison_data,
                "rankings": rankings,
                "top_performers": top_performers,
                "insights": comparison_insights,
                "generated_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Creator performance comparison completed")
            return comparison_result
            
        except Exception as e:
            self.logger.error(f"Error comparing creator performance: {str(e)}")
            raise
    
    # Helper methods for analytics processing
    def _get_start_date_for_timeframe(self, end_date: datetime, time_frame: TimeFrame) -> datetime:
        """Get start date for given timeframe"""
        if time_frame == TimeFrame.DAILY:
            return end_date - timedelta(days=1)
        elif time_frame == TimeFrame.WEEKLY:
            return end_date - timedelta(weeks=1)
        elif time_frame == TimeFrame.MONTHLY:
            return end_date - timedelta(days=30)
        elif time_frame == TimeFrame.QUARTERLY:
            return end_date - timedelta(days=90)
        elif time_frame == TimeFrame.YEARLY:
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=30)  # Default to monthly
    
    async def _get_metrics_for_period(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[PerformanceMetric]:
        """Get performance metrics for specified time period"""
        
        creator_metrics = self.performance_history.get(creator_id, [])
        period_metrics = [
            metric for metric in creator_metrics
            if start_date <= metric.timestamp <= end_date
        ]
        
        return period_metrics
    
    async def _calculate_aggregated_metrics(
        self,
        metrics_data: List[PerformanceMetric],
        creator_type: CreatorType
    ) -> Dict[str, Any]:
        """Calculate aggregated metrics from raw data"""
        
        aggregated = {}
        
        # Group metrics by name
        metrics_by_name = defaultdict(list)
        for metric in metrics_data:
            metrics_by_name[metric.metric_name].append(metric.value)
        
        # Calculate aggregations for each metric
        for metric_name, values in metrics_by_name.items():
            if values:
                aggregated[metric_name] = {
                    "average": statistics.mean(values),
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
                    "count": len(values),
                    "trend": self._calculate_simple_trend(values)
                }
        
        return aggregated
    
    def _calculate_simple_trend(self, values: List[float]) -> str:
        """Calculate simple trend from values"""
        if len(values) < 2:
            return "stable"
        
        recent_avg = statistics.mean(values[-len(values)//3:]) if len(values) >= 6 else values[-1]
        early_avg = statistics.mean(values[:len(values)//3]) if len(values) >= 6 else values[0]
        
        change_percent = (recent_avg - early_avg) / early_avg if early_avg != 0 else 0
        
        if change_percent > 0.1:
            return "increasing"
        elif change_percent < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    async def _analyze_performance_trends(
        self,
        creator_id: str,
        metrics_data: List[PerformanceMetric],
        time_frame: TimeFrame
    ) -> Dict[str, PerformanceTrend]:
        """Analyze performance trends for metrics"""
        
        trends = {}
        
        # Group metrics by name and analyze trends
        metrics_by_name = defaultdict(list)
        for metric in metrics_data:
            metrics_by_name[metric.metric_name].append((metric.timestamp, metric.value))
        
        for metric_name, time_value_pairs in metrics_by_name.items():
            if len(time_value_pairs) >= 3:
                # Sort by timestamp
                time_value_pairs.sort(key=lambda x: x[0])
                values = [pair[1] for pair in time_value_pairs]
                
                # Analyze trend
                if len(values) >= 5:
                    trend = self._analyze_detailed_trend(values)
                else:
                    trend = PerformanceTrend(self._calculate_simple_trend(values))
                
                trends[metric_name] = trend
        
        return trends
    
    def _analyze_detailed_trend(self, values: List[float]) -> PerformanceTrend:
        """Analyze detailed trend patterns"""
        if len(values) < 5:
            return PerformanceTrend.STABLE
        
        # Calculate moving averages
        short_ma = statistics.mean(values[-3:])
        long_ma = statistics.mean(values[-5:])
        
        # Calculate volatility
        volatility = statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) != 0 else 0
        
        # Determine trend
        change_percent = (short_ma - long_ma) / long_ma if long_ma != 0 else 0
        
        if volatility > 0.3:
            return PerformanceTrend.VOLATILE
        elif change_percent > 0.2:
            return PerformanceTrend.BREAKTHROUGH
        elif change_percent > 0.05:
            return PerformanceTrend.INCREASING
        elif change_percent < -0.2:
            return PerformanceTrend.DECLINING
        elif change_percent < -0.05:
            return PerformanceTrend.DECREASING
        else:
            return PerformanceTrend.STABLE
    
    async def _generate_performance_insights(
        self,
        aggregated_data: Dict[str, Any],
        trends: Dict[str, PerformanceTrend],
        creator_type: CreatorType
    ) -> List[str]:
        """Generate actionable performance insights"""
        
        insights = []
        benchmarks = self.performance_benchmarks.get(creator_type, {})
        
        # Analyze each metric against benchmarks and trends
        for metric_name, data in aggregated_data.items():
            average_value = data.get("average", 0.0)
            benchmark_value = benchmarks.get(metric_name, 0.0)
            trend = trends.get(metric_name, PerformanceTrend.STABLE)
            
            if average_value > benchmark_value * 1.2:
                insights.append(f"Excellent {metric_name} performance - {(average_value/benchmark_value-1)*100:.1f}% above industry benchmark")
            elif average_value < benchmark_value * 0.8:
                insights.append(f"{metric_name} below benchmark - opportunity for {(1-average_value/benchmark_value)*100:.1f}% improvement")
            
            if trend == PerformanceTrend.BREAKTHROUGH:
                insights.append(f"{metric_name} showing breakthrough performance - capitalize on momentum")
            elif trend == PerformanceTrend.DECLINING:
                insights.append(f"{metric_name} declining trend detected - immediate attention needed")
        
        return insights
    
    async def _generate_performance_recommendations(
        self,
        aggregated_data: Dict[str, Any],
        trends: Dict[str, PerformanceTrend],
        creator_type: CreatorType,
        insights: List[str]
    ) -> List[str]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        benchmarks = self.performance_benchmarks.get(creator_type, {})
        
        # Priority-based recommendations
        priority_metrics = ["engagement_rate", "quality_score", "audience_retention"]
        
        for metric_name in priority_metrics:
            if metric_name in aggregated_data:
                data = aggregated_data[metric_name]
                average_value = data.get("average", 0.0)
                benchmark_value = benchmarks.get(metric_name, 0.0)
                
                if average_value < benchmark_value:
                    if metric_name == "engagement_rate":
                        recommendations.append("Focus on creating more interactive and engaging content to boost audience engagement")
                    elif metric_name == "quality_score":
                        recommendations.append("Invest in audio quality improvements and content production refinement")
                    elif metric_name == "audience_retention":
                        recommendations.append("Optimize content structure and pacing to improve listener retention")
        
        # Trend-based recommendations
        for metric_name, trend in trends.items():
            if trend == PerformanceTrend.DECLINING:
                recommendations.append(f"Address declining {metric_name} through targeted improvement strategies")
            elif trend == PerformanceTrend.BREAKTHROUGH:
                recommendations.append(f"Scale and amplify {metric_name} strategies across all content")
        
        return recommendations
    
    async def _perform_comparative_analysis(
        self,
        creator_id: str,
        aggregated_data: Dict[str, Any],
        creator_type: CreatorType
    ) -> Dict[str, Any]:
        """Perform comparative analysis against benchmarks and peers"""
        
        benchmarks = self.performance_benchmarks.get(creator_type, {})
        
        # Compare against industry benchmarks
        benchmark_comparison = {}
        for metric_name, data in aggregated_data.items():
            average_value = data.get("average", 0.0)
            benchmark_value = benchmarks.get(metric_name, 0.0)
            
            if benchmark_value > 0:
                performance_ratio = average_value / benchmark_value
                benchmark_comparison[metric_name] = {
                    "performance_ratio": performance_ratio,
                    "percentile_rank": min(100, max(0, (performance_ratio - 0.5) * 100)),
                    "benchmark_gap": average_value - benchmark_value
                }
        
        # Calculate overall performance score
        overall_score = await self._calculate_overall_performance_score(aggregated_data)
        
        return {
            "benchmark_comparison": benchmark_comparison,
            "overall_performance_score": overall_score,
            "performance_tier": self._determine_performance_tier(overall_score),
            "top_strengths": await self._identify_top_strengths(benchmark_comparison),
            "improvement_areas": await self._identify_improvement_areas(benchmark_comparison)
        }
    
    async def _check_performance_alerts(self, creator_id: str, metric: PerformanceMetric):
        """Check if metric triggers any performance alerts"""
        
        thresholds = self.alert_thresholds
        metric_value = metric.value
        metric_name = metric.metric_name
        
        if metric_name in thresholds["critical"] and metric_value <= thresholds["critical"][metric_name]:
            self.logger.warning(f"CRITICAL ALERT: {metric_name} for creator {creator_id} is critically low: {metric_value}")
        elif metric_name in thresholds["warning"] and metric_value <= thresholds["warning"][metric_name]:
            self.logger.warning(f"WARNING: {metric_name} for creator {creator_id} is below warning threshold: {metric_value}")
    
    # Additional helper methods continue with similar patterns...
    async def _calculate_content_performance_score(self, engagement_metrics, audience_metrics, revenue_metrics, quality_metrics, content_type):
        """Calculate overall content performance score"""
        # Weighted calculation based on content type
        weights = {"engagement": 0.3, "audience": 0.25, "revenue": 0.25, "quality": 0.2}
        
        engagement_score = engagement_metrics.get("overall_engagement", 0.5)
        audience_score = audience_metrics.get("retention_rate", 0.5)
        revenue_score = min(1.0, revenue_metrics.get("revenue_per_view", 0) / 0.1)  # Normalize
        quality_score = quality_metrics.get("overall_quality", 0.5)
        
        return (engagement_score * weights["engagement"] + 
                audience_score * weights["audience"] + 
                revenue_score * weights["revenue"] + 
                quality_score * weights["quality"])
    
    async def _calculate_overall_performance_score(self, aggregated_data: Dict[str, Any]) -> float:
        """Calculate overall performance score from aggregated data"""
        weighted_score = 0.0
        total_weight = 0.0
        
        for metric_name, weight in self.metric_weights.items():
            if metric_name in aggregated_data:
                metric_value = aggregated_data[metric_name].get("average", 0.0)
                # Normalize metrics to 0-1 scale (this would be more sophisticated in production)
                normalized_value = min(1.0, metric_value / 1.0)  # Placeholder normalization
                weighted_score += normalized_value * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_performance_tier(self, overall_score: float) -> str:
        """Determine performance tier based on overall score"""
        if overall_score >= 0.9:
            return "exceptional"
        elif overall_score >= 0.8:
            return "excellent"
        elif overall_score >= 0.7:
            return "good"
        elif overall_score >= 0.6:
            return "average"
        elif overall_score >= 0.5:
            return "below_average"
        else:
            return "needs_improvement"
    
    async def _identify_top_strengths(self, benchmark_comparison: Dict[str, Any]) -> List[str]:
        """Identify top performance strengths"""
        strengths = []
        for metric_name, data in benchmark_comparison.items():
            if data.get("performance_ratio", 0) > 1.2:
                strengths.append(metric_name)
        return strengths[:3]  # Top 3 strengths
    
    async def _identify_improvement_areas(self, benchmark_comparison: Dict[str, Any]) -> List[str]:
        """Identify areas needing improvement"""
        improvements = []
        for metric_name, data in benchmark_comparison.items():
            if data.get("performance_ratio", 1) < 0.8:
                improvements.append(metric_name)
        return improvements[:3]  # Top 3 improvement areas