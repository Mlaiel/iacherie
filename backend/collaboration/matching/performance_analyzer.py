"""Performance Analyzer Module - Historical Performance Analysis for Creator Matching
===============================================================================

Advanced performance analysis system for evaluating creator collaboration success
based on historical data, engagement metrics, and predictive modeling.

This module implements:
- Historical performance tracking and analysis
- Collaboration success metrics calculation  
- Performance trend analysis and prediction
- Creator performance benchmarking
- ROI and impact measurement

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import statistics

logger = logging.getLogger(__name__)


class PerformanceMetricType(Enum):
    """Types of performance metrics"""
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    CLICK_THROUGH_RATE = "ctr"
    CONVERSION_RATE = "conversion_rate"
    REVENUE = "revenue"
    GROWTH_RATE = "growth_rate"
    RETENTION_RATE = "retention_rate"


class CollaborationType(Enum):
    """Types of collaborations for performance analysis"""
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    PRODUCT_LAUNCH = "product_launch"
    EVENT_COLLABORATION = "event_collaboration"
    EDUCATIONAL_SERIES = "educational_series"
    ENTERTAINMENT = "entertainment"
    BRAND_PARTNERSHIP = "brand_partnership"


class PerformanceTrend(Enum):
    """Performance trend indicators"""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"
    SEASONAL = "seasonal"


@dataclass
class PerformanceMetric:
    """Individual performance metric data point"""
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    platform: str
    content_id: Optional[str] = None
    collaboration_id: Optional[str] = None
    normalized_value: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationPerformance:
    """Performance data for a specific collaboration"""
    collaboration_id: str
    creator_ids: List[str]
    collaboration_type: CollaborationType
    start_date: datetime
    end_date: datetime
    metrics: List[PerformanceMetric]
    pre_collaboration_baseline: Dict[PerformanceMetricType, float]
    post_collaboration_impact: Dict[PerformanceMetricType, float]
    success_score: float
    roi: float
    lessons_learned: List[str] = field(default_factory=list)
    key_success_factors: List[str] = field(default_factory=list)


@dataclass
class CreatorPerformanceProfile:
    """Comprehensive performance profile for a creator"""
    creator_id: str
    historical_metrics: List[PerformanceMetric]
    collaboration_history: List[CollaborationPerformance]
    average_performance: Dict[PerformanceMetricType, float]
    peak_performance: Dict[PerformanceMetricType, float]
    performance_trends: Dict[PerformanceMetricType, PerformanceTrend]
    consistency_scores: Dict[PerformanceMetricType, float]
    growth_trajectory: Dict[str, float]
    strengths: List[str]
    improvement_areas: List[str]
    performance_factors: Dict[str, float]
    benchmark_comparisons: Dict[str, float]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PerformanceAnalysisResult:
    """Result of comprehensive performance analysis"""
    creator_id: str
    analysis_period: Tuple[datetime, datetime]
    overall_performance_score: float
    trend_analysis: Dict[PerformanceMetricType, Dict[str, Any]]
    collaboration_impact_analysis: Dict[str, Any]
    performance_predictions: Dict[PerformanceMetricType, List[float]]
    benchmark_position: Dict[str, float]
    optimization_recommendations: List[Dict[str, Any]]
    risk_factors: List[str]
    growth_opportunities: List[str]
    confidence_intervals: Dict[PerformanceMetricType, Tuple[float, float]]
    detailed_insights: Dict[str, Any]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CollaborationImpactAssessment:
    """Assessment of collaboration impact on performance"""
    collaboration_id: str
    participants: List[str]
    impact_scores: Dict[str, float]  # creator_id -> impact_score
    metric_improvements: Dict[PerformanceMetricType, float]
    attribution_analysis: Dict[str, float]  # which creator contributed what
    synergy_effects: List[Dict[str, Any]]
    unexpected_outcomes: List[str]
    success_probability: float
    replication_potential: float
    lessons_for_future: List[str]


class PerformanceAnalyzer:
    """Advanced performance analysis engine for creator collaborations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the performance analyzer"""
        self.config = config or {}
        self.normalization_factors = self._init_normalization_factors()
        self.benchmark_data = {}
        self.performance_models = {}
        self.trend_detectors = {}
        
        logger.info("📊 Performance Analyzer initialized")
    
    def _init_normalization_factors(self) -> Dict[PerformanceMetricType, Dict[str, float]]:
        """Initialize normalization factors for different metrics and platforms"""
        return {
            PerformanceMetricType.ENGAGEMENT_RATE: {
                'instagram': 1.0,
                'tiktok': 1.2,  # Higher typical engagement
                'youtube': 0.8,  # Lower typical engagement
                'twitter': 0.6
            },
            PerformanceMetricType.REACH: {
                'instagram': 1.0,
                'tiktok': 2.0,  # Higher viral potential
                'youtube': 0.5,
                'twitter': 0.7
            },
            # Add more normalization factors for other metrics
        }
    
    async def analyze_creator_performance(
        self,
        creator_id: str,
        analysis_period: Optional[Tuple[datetime, datetime]] = None,
        include_predictions: bool = True
    ) -> PerformanceAnalysisResult:
        """Perform comprehensive performance analysis for a creator"""
        try:
            logger.info(f"📊 Analyzing performance for creator: {creator_id}")
            
            # Set default analysis period if not provided
            if analysis_period is None:
                end_date = datetime.now(timezone.utc)
                start_date = end_date - timedelta(days=365)  # Last year
                analysis_period = (start_date, end_date)
            
            # Get creator performance profile
            profile = await self._build_performance_profile(creator_id, analysis_period)
            
            # Calculate overall performance score
            overall_score = await self._calculate_overall_performance_score(profile)
            
            # Perform trend analysis
            trend_analysis = await self._perform_trend_analysis(profile)
            
            # Analyze collaboration impact
            collaboration_impact = await self._analyze_collaboration_impact(profile)
            
            # Generate predictions if requested
            predictions = {}
            if include_predictions:
                predictions = await self._generate_performance_predictions(profile)
            
            # Calculate benchmark position
            benchmark_position = await self._calculate_benchmark_position(profile)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(profile)
            
            # Identify risk factors
            risk_factors = await self._identify_risk_factors(profile)
            
            # Find growth opportunities
            growth_opportunities = await self._identify_growth_opportunities(profile)
            
            # Calculate confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(profile)
            
            # Generate detailed insights
            detailed_insights = await self._generate_detailed_insights(profile)
            
            result = PerformanceAnalysisResult(
                creator_id=creator_id,
                analysis_period=analysis_period,
                overall_performance_score=overall_score,
                trend_analysis=trend_analysis,
                collaboration_impact_analysis=collaboration_impact,
                performance_predictions=predictions,
                benchmark_position=benchmark_position,
                optimization_recommendations=recommendations,
                risk_factors=risk_factors,
                growth_opportunities=growth_opportunities,
                confidence_intervals=confidence_intervals,
                detailed_insights=detailed_insights
            )
            
            logger.info(f"✅ Performance analysis completed: {overall_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in performance analysis: {e}")
            raise
    
    async def _build_performance_profile(
        self,
        creator_id: str,
        analysis_period: Tuple[datetime, datetime]
    ) -> CreatorPerformanceProfile:
        """Build comprehensive performance profile for creator"""
        try:
            # Get historical metrics (mock data - replace with real data fetching)
            historical_metrics = await self._fetch_historical_metrics(creator_id, analysis_period)
            
            # Get collaboration history
            collaboration_history = await self._fetch_collaboration_history(creator_id, analysis_period)
            
            # Calculate average performance
            average_performance = self._calculate_average_performance(historical_metrics)
            
            # Calculate peak performance
            peak_performance = self._calculate_peak_performance(historical_metrics)
            
            # Detect performance trends
            performance_trends = await self._detect_performance_trends(historical_metrics)
            
            # Calculate consistency scores
            consistency_scores = self._calculate_consistency_scores(historical_metrics)
            
            # Calculate growth trajectory
            growth_trajectory = self._calculate_growth_trajectory(historical_metrics)
            
            # Identify strengths and improvement areas
            strengths, improvement_areas = await self._identify_strengths_and_improvements(
                historical_metrics, collaboration_history
            )
            
            # Calculate performance factors
            performance_factors = await self._calculate_performance_factors(
                historical_metrics, collaboration_history
            )
            
            # Generate benchmark comparisons
            benchmark_comparisons = await self._generate_benchmark_comparisons(
                creator_id, average_performance
            )
            
            profile = CreatorPerformanceProfile(
                creator_id=creator_id,
                historical_metrics=historical_metrics,
                collaboration_history=collaboration_history,
                average_performance=average_performance,
                peak_performance=peak_performance,
                performance_trends=performance_trends,
                consistency_scores=consistency_scores,
                growth_trajectory=growth_trajectory,
                strengths=strengths,
                improvement_areas=improvement_areas,
                performance_factors=performance_factors,
                benchmark_comparisons=benchmark_comparisons
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error building performance profile: {e}")
            raise
    
    async def _fetch_historical_metrics(
        self,
        creator_id: str,
        period: Tuple[datetime, datetime]
    ) -> List[PerformanceMetric]:
        """Fetch historical performance metrics (mock implementation)"""
        # In real implementation, this would fetch from database
        metrics = []
        
        # Generate mock data for demonstration
        start_date, end_date = period
        current_date = start_date
        
        while current_date <= end_date:
            # Generate mock metrics for each day
            for metric_type in PerformanceMetricType:
                base_value = self._get_base_metric_value(metric_type)
                variation = np.random.normal(0, 0.1)  # 10% random variation
                value = max(0, base_value * (1 + variation))
                
                metric = PerformanceMetric(
                    metric_type=metric_type,
                    value=value,
                    timestamp=current_date,
                    platform="instagram",  # Mock platform
                    context={"mock_data": True}
                )
                metrics.append(metric)
            
            current_date += timedelta(days=1)
        
        return metrics
    
    def _get_base_metric_value(self, metric_type: PerformanceMetricType) -> float:
        """Get base value for metric type (for mock data generation)"""
        base_values = {
            PerformanceMetricType.ENGAGEMENT_RATE: 0.05,  # 5%
            PerformanceMetricType.REACH: 10000,
            PerformanceMetricType.IMPRESSIONS: 15000,
            PerformanceMetricType.VIEWS: 8000,
            PerformanceMetricType.LIKES: 500,
            PerformanceMetricType.SHARES: 50,
            PerformanceMetricType.COMMENTS: 30,
            PerformanceMetricType.SAVES: 100,
            PerformanceMetricType.CLICK_THROUGH_RATE: 0.02,  # 2%
            PerformanceMetricType.CONVERSION_RATE: 0.01,  # 1%
            PerformanceMetricType.REVENUE: 1000,
            PerformanceMetricType.GROWTH_RATE: 0.03,  # 3%
            PerformanceMetricType.RETENTION_RATE: 0.8   # 80%
        }
        return base_values.get(metric_type, 100.0)
    
    async def _fetch_collaboration_history(
        self,
        creator_id: str,
        period: Tuple[datetime, datetime]
    ) -> List[CollaborationPerformance]:
        """Fetch collaboration history (mock implementation)"""
        # Mock collaboration data
        collaborations = []
        
        # Generate 3-5 mock collaborations
        for i in range(3):
            start_date = period[0] + timedelta(days=i*90)
            end_date = start_date + timedelta(days=30)
            
            if end_date <= period[1]:
                collaboration = CollaborationPerformance(
                    collaboration_id=f"collab_{creator_id}_{i}",
                    creator_ids=[creator_id, f"partner_{i}"],
                    collaboration_type=CollaborationType.CONTENT_CREATION,
                    start_date=start_date,
                    end_date=end_date,
                    metrics=[],  # Would be populated with real data
                    pre_collaboration_baseline={
                        PerformanceMetricType.ENGAGEMENT_RATE: 0.05,
                        PerformanceMetricType.REACH: 10000
                    },
                    post_collaboration_impact={
                        PerformanceMetricType.ENGAGEMENT_RATE: 0.08,
                        PerformanceMetricType.REACH: 15000
                    },
                    success_score=0.75 + (i * 0.1),  # Improving success over time
                    roi=1.5 + (i * 0.2),
                    key_success_factors=[f"factor_{i}", "strong_content", "good_timing"]
                )
                collaborations.append(collaboration)
        
        return collaborations
    
    def _calculate_average_performance(
        self,
        metrics: List[PerformanceMetric]
    ) -> Dict[PerformanceMetricType, float]:
        """Calculate average performance across all metrics"""
        metric_groups = {}
        
        # Group metrics by type
        for metric in metrics:
            if metric.metric_type not in metric_groups:
                metric_groups[metric.metric_type] = []
            metric_groups[metric.metric_type].append(metric.value)
        
        # Calculate averages
        averages = {}
        for metric_type, values in metric_groups.items():
            averages[metric_type] = statistics.mean(values)
        
        return averages
    
    def _calculate_peak_performance(
        self,
        metrics: List[PerformanceMetric]
    ) -> Dict[PerformanceMetricType, float]:
        """Calculate peak performance for each metric type"""
        metric_groups = {}
        
        # Group metrics by type
        for metric in metrics:
            if metric.metric_type not in metric_groups:
                metric_groups[metric.metric_type] = []
            metric_groups[metric.metric_type].append(metric.value)
        
        # Calculate peaks
        peaks = {}
        for metric_type, values in metric_groups.items():
            peaks[metric_type] = max(values)
        
        return peaks
    
    async def _detect_performance_trends(
        self,
        metrics: List[PerformanceMetric]
    ) -> Dict[PerformanceMetricType, PerformanceTrend]:
        """Detect performance trends for each metric type"""
        trends = {}
        
        # Group metrics by type and sort by timestamp
        metric_groups = {}
        for metric in metrics:
            if metric.metric_type not in metric_groups:
                metric_groups[metric.metric_type] = []
            metric_groups[metric.metric_type].append(metric)
        
        for metric_type, metric_list in metric_groups.items():
            # Sort by timestamp
            metric_list.sort(key=lambda x: x.timestamp)
            
            # Get values for trend analysis
            values = [m.value for m in metric_list]
            
            if len(values) < 5:  # Need sufficient data points
                trends[metric_type] = PerformanceTrend.STABLE
                continue
            
            # Calculate trend using linear regression
            x = np.arange(len(values)).reshape(-1, 1)
            y = np.array(values)
            
            model = LinearRegression()
            model.fit(x, y)
            
            slope = model.coef_[0]
            r2 = model.score(x, y)
            
            # Calculate coefficient of variation for volatility
            cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
            
            # Determine trend
            if cv > 0.3:  # High volatility
                trends[metric_type] = PerformanceTrend.VOLATILE
            elif abs(slope) < 0.01:  # Minimal change
                trends[metric_type] = PerformanceTrend.STABLE
            elif slope > 0.01:  # Positive trend
                trends[metric_type] = PerformanceTrend.RISING
            else:  # Negative trend
                trends[metric_type] = PerformanceTrend.DECLINING
        
        return trends
    
    def _calculate_consistency_scores(
        self,
        metrics: List[PerformanceMetric]
    ) -> Dict[PerformanceMetricType, float]:
        """Calculate consistency scores for each metric type"""
        consistency_scores = {}
        
        # Group metrics by type
        metric_groups = {}
        for metric in metrics:
            if metric.metric_type not in metric_groups:
                metric_groups[metric.metric_type] = []
            metric_groups[metric.metric_type].append(metric.value)
        
        for metric_type, values in metric_groups.items():
            if len(values) < 2:
                consistency_scores[metric_type] = 0.0
                continue
            
            # Calculate coefficient of variation (lower = more consistent)
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values)
            
            if mean_val > 0:
                cv = std_val / mean_val
                # Convert to consistency score (0-1, higher = more consistent)
                consistency_scores[metric_type] = max(0.0, 1.0 - cv)
            else:
                consistency_scores[metric_type] = 0.0
        
        return consistency_scores
    
    def _calculate_growth_trajectory(
        self,
        metrics: List[PerformanceMetric]
    ) -> Dict[str, float]:
        """Calculate growth trajectory metrics"""
        # Get engagement rate metrics sorted by time
        engagement_metrics = [
            m for m in metrics 
            if m.metric_type == PerformanceMetricType.ENGAGEMENT_RATE
        ]
        engagement_metrics.sort(key=lambda x: x.timestamp)
        
        if len(engagement_metrics) < 2:
            return {"monthly_growth": 0.0, "quarterly_growth": 0.0, "yearly_growth": 0.0}
        
        # Calculate growth over different periods
        values = [m.value for m in engagement_metrics]
        
        # Simple growth calculation (first vs last value)
        total_growth = (values[-1] - values[0]) / values[0] if values[0] > 0 else 0
        
        # Annualize the growth
        days = (engagement_metrics[-1].timestamp - engagement_metrics[0].timestamp).days
        if days > 0:
            yearly_growth = total_growth * (365 / days)
        else:
            yearly_growth = 0.0
        
        return {
            "monthly_growth": yearly_growth / 12,
            "quarterly_growth": yearly_growth / 4,
            "yearly_growth": yearly_growth
        }
    
    async def _identify_strengths_and_improvements(
        self,
        metrics: List[PerformanceMetric],
        collaborations: List[CollaborationPerformance]
    ) -> Tuple[List[str], List[str]]:
        """Identify creator strengths and improvement areas"""
        strengths = []
        improvements = []
        
        # Analyze metric performance
        avg_performance = self._calculate_average_performance(metrics)
        consistency_scores = self._calculate_consistency_scores(metrics)
        
        # Industry benchmarks (mock data)
        benchmarks = {
            PerformanceMetricType.ENGAGEMENT_RATE: 0.04,
            PerformanceMetricType.GROWTH_RATE: 0.02,
            PerformanceMetricType.RETENTION_RATE: 0.75
        }
        
        # Check strengths
        for metric_type, avg_value in avg_performance.items():
            benchmark = benchmarks.get(metric_type, 0)
            consistency = consistency_scores.get(metric_type, 0)
            
            if avg_value > benchmark * 1.2:  # 20% above benchmark
                strengths.append(f"Strong {metric_type.value} performance")
            
            if consistency > 0.8:  # High consistency
                strengths.append(f"Consistent {metric_type.value}")
        
        # Check improvements
        for metric_type, avg_value in avg_performance.items():
            benchmark = benchmarks.get(metric_type, 0)
            consistency = consistency_scores.get(metric_type, 0)
            
            if avg_value < benchmark * 0.8:  # 20% below benchmark
                improvements.append(f"Improve {metric_type.value}")
            
            if consistency < 0.5:  # Low consistency
                improvements.append(f"More consistent {metric_type.value}")
        
        # Analyze collaboration performance
        if collaborations:
            avg_success = statistics.mean([c.success_score for c in collaborations])
            if avg_success > 0.8:
                strengths.append("Excellent collaboration track record")
            elif avg_success < 0.6:
                improvements.append("Improve collaboration execution")
        
        return strengths, improvements
    
    async def _calculate_performance_factors(
        self,
        metrics: List[PerformanceMetric],
        collaborations: List[CollaborationPerformance]
    ) -> Dict[str, float]:
        """Calculate factors that influence performance"""
        factors = {}
        
        # Content quality factor (based on engagement)
        engagement_metrics = [m for m in metrics if m.metric_type == PerformanceMetricType.ENGAGEMENT_RATE]
        if engagement_metrics:
            avg_engagement = statistics.mean([m.value for m in engagement_metrics])
            factors["content_quality"] = min(avg_engagement / 0.1, 1.0)  # Normalize to 0-1
        
        # Consistency factor
        consistency_scores = self._calculate_consistency_scores(metrics)
        if consistency_scores:
            factors["consistency"] = statistics.mean(list(consistency_scores.values()))
        
        # Growth factor
        growth_trajectory = self._calculate_growth_trajectory(metrics)
        yearly_growth = growth_trajectory.get("yearly_growth", 0)
        factors["growth_momentum"] = min(max(yearly_growth / 0.5, 0), 1.0)  # Normalize
        
        # Collaboration effectiveness
        if collaborations:
            avg_roi = statistics.mean([c.roi for c in collaborations])
            factors["collaboration_effectiveness"] = min(avg_roi / 2.0, 1.0)  # Normalize
        
        return factors
    
    async def _generate_benchmark_comparisons(
        self,
        creator_id: str,
        average_performance: Dict[PerformanceMetricType, float]
    ) -> Dict[str, float]:
        """Generate benchmark comparisons (mock implementation)"""
        # Mock industry benchmarks
        benchmarks = {
            "industry_engagement": 0.04,
            "top_10_percent_engagement": 0.08,
            "similar_creators_engagement": 0.045,
            "platform_average_reach": 12000
        }
        
        comparisons = {}
        creator_engagement = average_performance.get(PerformanceMetricType.ENGAGEMENT_RATE, 0)
        creator_reach = average_performance.get(PerformanceMetricType.REACH, 0)
        
        # Calculate relative performance
        if creator_engagement > 0:
            comparisons["vs_industry_engagement"] = creator_engagement / benchmarks["industry_engagement"]
            comparisons["vs_top_10_percent"] = creator_engagement / benchmarks["top_10_percent_engagement"]
            comparisons["vs_similar_creators"] = creator_engagement / benchmarks["similar_creators_engagement"]
        
        if creator_reach > 0:
            comparisons["vs_platform_reach"] = creator_reach / benchmarks["platform_average_reach"]
        
        return comparisons
    
    async def _calculate_overall_performance_score(
        self,
        profile: CreatorPerformanceProfile
    ) -> float:
        """Calculate overall performance score"""
        scores = []
        
        # Performance relative to benchmarks
        for comparison_key, ratio in profile.benchmark_comparisons.items():
            scores.append(min(ratio, 2.0) / 2.0)  # Cap at 2x benchmark, normalize to 0-1
        
        # Consistency scores
        if profile.consistency_scores:
            scores.append(statistics.mean(list(profile.consistency_scores.values())))
        
        # Growth momentum
        yearly_growth = profile.growth_trajectory.get("yearly_growth", 0)
        growth_score = min(max(yearly_growth + 0.5, 0), 1.0)  # Normalize around 0 growth
        scores.append(growth_score)
        
        # Collaboration success
        if profile.collaboration_history:
            avg_success = statistics.mean([c.success_score for c in profile.collaboration_history])
            scores.append(avg_success)
        
        return statistics.mean(scores) if scores else 0.0
    
    async def _perform_trend_analysis(
        self,
        profile: CreatorPerformanceProfile
    ) -> Dict[PerformanceMetricType, Dict[str, Any]]:
        """Perform detailed trend analysis"""
        trend_analysis = {}
        
        for metric_type, trend in profile.performance_trends.items():
            # Get metrics for this type
            metrics = [m for m in profile.historical_metrics if m.metric_type == metric_type]
            metrics.sort(key=lambda x: x.timestamp)
            
            if len(metrics) < 5:
                continue
            
            values = [m.value for m in metrics]
            
            # Calculate trend strength
            x = np.arange(len(values)).reshape(-1, 1)
            y = np.array(values)
            model = LinearRegression()
            model.fit(x, y)
            
            trend_strength = abs(model.coef_[0]) / np.mean(values) if np.mean(values) > 0 else 0
            
            # Calculate momentum (recent vs earlier performance)
            recent_avg = statistics.mean(values[-10:]) if len(values) >= 10 else statistics.mean(values)
            earlier_avg = statistics.mean(values[:10]) if len(values) >= 10 else statistics.mean(values)
            momentum = (recent_avg - earlier_avg) / earlier_avg if earlier_avg > 0 else 0
            
            trend_analysis[metric_type] = {
                "trend": trend.value,
                "strength": trend_strength,
                "momentum": momentum,
                "r_squared": model.score(x, y),
                "recent_average": recent_avg,
                "historical_average": earlier_avg,
                "volatility": np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
            }
        
        return trend_analysis
    
    async def _analyze_collaboration_impact(
        self,
        profile: CreatorPerformanceProfile
    ) -> Dict[str, Any]:
        """Analyze the impact of collaborations on performance"""
        if not profile.collaboration_history:
            return {"message": "No collaboration history available"}
        
        # Calculate average performance lift from collaborations
        total_lift = 0.0
        successful_collaborations = 0
        
        for collab in profile.collaboration_history:
            if collab.success_score > 0.6:  # Consider successful
                successful_collaborations += 1
                # Calculate lift for key metrics
                for metric_type in [PerformanceMetricType.ENGAGEMENT_RATE, PerformanceMetricType.REACH]:
                    baseline = collab.pre_collaboration_baseline.get(metric_type, 0)
                    impact = collab.post_collaboration_impact.get(metric_type, 0)
                    if baseline > 0:
                        lift = (impact - baseline) / baseline
                        total_lift += lift
        
        avg_lift = total_lift / (successful_collaborations * 2) if successful_collaborations > 0 else 0
        
        # Analyze collaboration types effectiveness
        type_effectiveness = {}
        for collab in profile.collaboration_history:
            collab_type = collab.collaboration_type.value
            if collab_type not in type_effectiveness:
                type_effectiveness[collab_type] = []
            type_effectiveness[collab_type].append(collab.success_score)
        
        # Calculate average effectiveness per type
        for collab_type, scores in type_effectiveness.items():
            type_effectiveness[collab_type] = statistics.mean(scores)
        
        return {
            "total_collaborations": len(profile.collaboration_history),
            "successful_collaborations": successful_collaborations,
            "success_rate": successful_collaborations / len(profile.collaboration_history),
            "average_performance_lift": avg_lift,
            "collaboration_type_effectiveness": type_effectiveness,
            "average_roi": statistics.mean([c.roi for c in profile.collaboration_history]),
            "best_collaboration": max(profile.collaboration_history, key=lambda x: x.success_score).collaboration_id
        }
    
    async def _generate_performance_predictions(
        self,
        profile: CreatorPerformanceProfile
    ) -> Dict[PerformanceMetricType, List[float]]:
        """Generate performance predictions for next 3 months"""
        predictions = {}
        
        for metric_type in PerformanceMetricType:
            # Get historical data for this metric
            metrics = [m for m in profile.historical_metrics if m.metric_type == metric_type]
            metrics.sort(key=lambda x: x.timestamp)
            
            if len(metrics) < 10:  # Need sufficient data
                continue
            
            values = [m.value for m in metrics]
            
            # Use simple moving average for prediction (can be enhanced with ML models)
            recent_values = values[-30:]  # Last 30 data points
            trend = np.polyfit(range(len(recent_values)), recent_values, 1)[0]  # Linear trend
            
            # Generate predictions for next 90 days
            last_value = values[-1]
            daily_predictions = []
            
            for day in range(90):
                # Add trend and some randomness
                predicted_value = last_value + (trend * day) + np.random.normal(0, np.std(values) * 0.1)
                predicted_value = max(0, predicted_value)  # Ensure non-negative
                daily_predictions.append(predicted_value)
            
            predictions[metric_type] = daily_predictions
        
        return predictions
    
    async def _calculate_benchmark_position(
        self,
        profile: CreatorPerformanceProfile
    ) -> Dict[str, float]:
        """Calculate position relative to various benchmarks"""
        position = {}
        
        # Use benchmark comparisons from profile
        for comparison, ratio in profile.benchmark_comparisons.items():
            if ratio >= 2.0:
                position[comparison] = "top_5_percent"
            elif ratio >= 1.5:
                position[comparison] = "top_20_percent"
            elif ratio >= 1.0:
                position[comparison] = "above_average"
            elif ratio >= 0.8:
                position[comparison] = "average"
            else:
                position[comparison] = "below_average"
        
        # Overall percentile estimate
        avg_ratio = statistics.mean(list(profile.benchmark_comparisons.values()))
        if avg_ratio >= 2.0:
            position["overall_percentile"] = 95
        elif avg_ratio >= 1.5:
            position["overall_percentile"] = 80
        elif avg_ratio >= 1.0:
            position["overall_percentile"] = 60
        elif avg_ratio >= 0.8:
            position["overall_percentile"] = 40
        else:
            position["overall_percentile"] = 25
        
        return position
    
    async def _generate_optimization_recommendations(
        self,
        profile: CreatorPerformanceProfile
    ) -> List[Dict[str, Any]]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Based on improvement areas
        for improvement in profile.improvement_areas:
            if "engagement" in improvement.lower():
                recommendations.append({
                    "type": "content_optimization",
                    "priority": "high",
                    "recommendation": "Focus on creating more engaging content with interactive elements",
                    "expected_impact": "15-25% engagement increase",
                    "implementation_effort": "medium"
                })
            elif "consistency" in improvement.lower():
                recommendations.append({
                    "type": "posting_schedule",
                    "priority": "medium",
                    "recommendation": "Establish consistent posting schedule and content quality standards",
                    "expected_impact": "10-20% consistency improvement",
                    "implementation_effort": "low"
                })
        
        # Based on performance trends
        for metric_type, trend in profile.performance_trends.items():
            if trend == PerformanceTrend.DECLINING:
                recommendations.append({
                    "type": "trend_reversal",
                    "priority": "high",
                    "recommendation": f"Address declining {metric_type.value} through content strategy review",
                    "expected_impact": "Trend stabilization within 30 days",
                    "implementation_effort": "high"
                })
        
        # Collaboration recommendations
        if profile.collaboration_history:
            best_collab_type = max(
                set(c.collaboration_type for c in profile.collaboration_history),
                key=lambda ct: statistics.mean([c.success_score for c in profile.collaboration_history if c.collaboration_type == ct])
            )
            recommendations.append({
                "type": "collaboration_strategy",
                "priority": "medium",
                "recommendation": f"Focus on {best_collab_type.value} collaborations as they show highest success rate",
                "expected_impact": "20-30% collaboration success rate improvement",
                "implementation_effort": "medium"
            })
        
        return recommendations
    
    async def _identify_risk_factors(self, profile: CreatorPerformanceProfile) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        # Performance risks
        for metric_type, trend in profile.performance_trends.items():
            if trend == PerformanceTrend.DECLINING:
                risks.append(f"Declining {metric_type.value}")
            elif trend == PerformanceTrend.VOLATILE:
                risks.append(f"Unstable {metric_type.value}")
        
        # Consistency risks
        low_consistency_metrics = [
            metric for metric, score in profile.consistency_scores.items() 
            if score < 0.5
        ]
        if low_consistency_metrics:
            risks.append("Low performance consistency")
        
        # Growth risks
        yearly_growth = profile.growth_trajectory.get("yearly_growth", 0)
        if yearly_growth < -0.1:  # Negative growth
            risks.append("Negative growth trajectory")
        
        # Collaboration risks
        if profile.collaboration_history:
            recent_collabs = [c for c in profile.collaboration_history 
                            if c.end_date > datetime.now(timezone.utc) - timedelta(days=180)]
            if recent_collabs:
                avg_recent_success = statistics.mean([c.success_score for c in recent_collabs])
                if avg_recent_success < 0.6:
                    risks.append("Recent collaboration underperformance")
        
        return risks
    
    async def _identify_growth_opportunities(self, profile: CreatorPerformanceProfile) -> List[str]:
        """Identify growth opportunities"""
        opportunities = []
        
        # Based on strengths
        for strength in profile.strengths:
            if "collaboration" in strength.lower():
                opportunities.append("Leverage collaboration expertise for strategic partnerships")
            elif "engagement" in strength.lower():
                opportunities.append("Expand content formats to capitalize on high engagement")
        
        # Based on trends
        rising_metrics = [
            metric for metric, trend in profile.performance_trends.items()
            if trend == PerformanceTrend.RISING
        ]
        if rising_metrics:
            opportunities.append("Double down on rising performance areas")
        
        # Based on benchmark position
        strong_benchmarks = [
            comp for comp, ratio in profile.benchmark_comparisons.items()
            if ratio > 1.2
        ]
        if strong_benchmarks:
            opportunities.append("Leverage above-average performance for premium collaborations")
        
        # Market opportunities
        opportunities.extend([
            "Explore emerging content formats",
            "Target underserved audience segments",
            "Develop signature content series",
            "Build strategic creator network"
        ])
        
        return opportunities
    
    async def _calculate_confidence_intervals(
        self,
        profile: CreatorPerformanceProfile
    ) -> Dict[PerformanceMetricType, Tuple[float, float]]:
        """Calculate confidence intervals for performance predictions"""
        intervals = {}
        
        for metric_type in PerformanceMetricType:
            metrics = [m for m in profile.historical_metrics if m.metric_type == metric_type]
            
            if len(metrics) < 5:
                continue
            
            values = [m.value for m in metrics]
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0
            
            # 95% confidence interval
            margin_of_error = 1.96 * (std_val / np.sqrt(len(values)))
            lower_bound = max(0, mean_val - margin_of_error)
            upper_bound = mean_val + margin_of_error
            
            intervals[metric_type] = (lower_bound, upper_bound)
        
        return intervals
    
    async def _generate_detailed_insights(
        self,
        profile: CreatorPerformanceProfile
    ) -> Dict[str, Any]:
        """Generate detailed performance insights"""
        insights = {
            "performance_summary": {
                "total_metrics_analyzed": len(profile.historical_metrics),
                "analysis_period_days": (
                    max([m.timestamp for m in profile.historical_metrics]) -
                    min([m.timestamp for m in profile.historical_metrics])
                ).days if profile.historical_metrics else 0,
                "strongest_metric": max(profile.average_performance.items(), key=lambda x: x[1])[0].value if profile.average_performance else None,
                "most_consistent_metric": max(profile.consistency_scores.items(), key=lambda x: x[1])[0].value if profile.consistency_scores else None
            },
            "collaboration_insights": {
                "total_collaborations": len(profile.collaboration_history),
                "most_successful_type": max(
                    set(c.collaboration_type.value for c in profile.collaboration_history),
                    key=lambda ct: statistics.mean([c.success_score for c in profile.collaboration_history if c.collaboration_type.value == ct])
                ) if profile.collaboration_history else None,
                "average_collaboration_roi": statistics.mean([c.roi for c in profile.collaboration_history]) if profile.collaboration_history else 0
            },
            "growth_insights": profile.growth_trajectory,
            "market_position": {
                "competitive_advantage": profile.strengths[:3],  # Top 3 strengths
                "improvement_priorities": profile.improvement_areas[:3],  # Top 3 areas
                "performance_factors": profile.performance_factors
            }
        }
        
        return insights
    
    async def assess_collaboration_impact(
        self,
        collaboration_id: str,
        pre_period: Tuple[datetime, datetime],
        post_period: Tuple[datetime, datetime]
    ) -> CollaborationImpactAssessment:
        """Assess the impact of a specific collaboration"""
        try:
            logger.info(f"📊 Assessing collaboration impact: {collaboration_id}")
            
            # Get collaboration details (mock implementation)
            collaboration = await self._get_collaboration_details(collaboration_id)
            
            # Calculate impact for each participant
            impact_scores = {}
            metric_improvements = {}
            
            for creator_id in collaboration['participants']:
                # Get pre and post metrics
                pre_metrics = await self._fetch_historical_metrics(creator_id, pre_period)
                post_metrics = await self._fetch_historical_metrics(creator_id, post_period)
                
                # Calculate improvements
                creator_impact = await self._calculate_creator_impact(pre_metrics, post_metrics)
                impact_scores[creator_id] = creator_impact['overall_impact']
                
                # Aggregate metric improvements
                for metric_type, improvement in creator_impact['metric_improvements'].items():
                    if metric_type not in metric_improvements:
                        metric_improvements[metric_type] = []
                    metric_improvements[metric_type].append(improvement)
            
            # Average metric improvements
            for metric_type, improvements in metric_improvements.items():
                metric_improvements[metric_type] = statistics.mean(improvements)
            
            # Analyze attribution (who contributed what)
            attribution_analysis = await self._analyze_attribution(collaboration, impact_scores)
            
            # Identify synergy effects
            synergy_effects = await self._identify_synergy_effects(collaboration, impact_scores)
            
            # Calculate success probability and replication potential
            success_probability = statistics.mean(list(impact_scores.values()))
            replication_potential = await self._calculate_replication_potential(collaboration)
            
            # Generate lessons learned
            lessons = await self._extract_lessons_learned(collaboration, impact_scores)
            
            assessment = CollaborationImpactAssessment(
                collaboration_id=collaboration_id,
                participants=collaboration['participants'],
                impact_scores=impact_scores,
                metric_improvements=metric_improvements,
                attribution_analysis=attribution_analysis,
                synergy_effects=synergy_effects,
                unexpected_outcomes=[],  # Would be populated with real analysis
                success_probability=success_probability,
                replication_potential=replication_potential,
                lessons_for_future=lessons
            )
            
            logger.info(f"✅ Collaboration impact assessment completed")
            return assessment
            
        except Exception as e:
            logger.error(f"❌ Error in collaboration impact assessment: {e}")
            raise
    
    async def _get_collaboration_details(self, collaboration_id: str) -> Dict[str, Any]:
        """Get collaboration details (mock implementation)"""
        return {
            "collaboration_id": collaboration_id,
            "participants": [f"creator_{i}" for i in range(2)],
            "type": "content_creation",
            "duration_days": 30
        }
    
    async def _calculate_creator_impact(
        self,
        pre_metrics: List[PerformanceMetric],
        post_metrics: List[PerformanceMetric]
    ) -> Dict[str, Any]:
        """Calculate impact for a single creator"""
        pre_avg = self._calculate_average_performance(pre_metrics)
        post_avg = self._calculate_average_performance(post_metrics)
        
        metric_improvements = {}
        total_impact = 0.0
        
        for metric_type in PerformanceMetricType:
            pre_val = pre_avg.get(metric_type, 0)
            post_val = post_avg.get(metric_type, 0)
            
            if pre_val > 0:
                improvement = (post_val - pre_val) / pre_val
                metric_improvements[metric_type] = improvement
                total_impact += improvement
        
        overall_impact = total_impact / len(metric_improvements) if metric_improvements else 0
        
        return {
            "overall_impact": overall_impact,
            "metric_improvements": metric_improvements
        }
    
    async def _analyze_attribution(
        self,
        collaboration: Dict[str, Any],
        impact_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Analyze attribution of success to different participants"""
        # Simplified attribution - could be enhanced with more sophisticated analysis
        total_impact = sum(impact_scores.values())
        
        attribution = {}
        for creator_id, impact in impact_scores.items():
            if total_impact > 0:
                attribution[creator_id] = impact / total_impact
            else:
                attribution[creator_id] = 1.0 / len(impact_scores)
        
        return attribution
    
    async def _identify_synergy_effects(
        self,
        collaboration: Dict[str, Any],
        impact_scores: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify synergy effects from collaboration"""
        effects = []
        
        # Check if combined impact exceeds individual impacts
        avg_impact = statistics.mean(list(impact_scores.values()))
        if avg_impact > 0.2:  # Significant positive impact
            effects.append({
                "type": "performance_amplification",
                "description": "Collaboration amplified individual creator performance",
                "magnitude": avg_impact
            })
        
        # Check for cross-audience pollination
        effects.append({
            "type": "audience_crossover",
            "description": "Creators likely gained access to each other's audiences",
            "magnitude": 0.3  # Mock estimate
        })
        
        return effects
    
    async def _calculate_replication_potential(self, collaboration: Dict[str, Any]) -> float:
        """Calculate how replicable this collaboration success is"""
        # Factors affecting replication
        factors = {
            "content_type_scalability": 0.8,
            "creator_availability": 0.7,
            "market_saturation": 0.6,
            "resource_requirements": 0.9
        }
        
        return statistics.mean(list(factors.values()))
    
    async def _extract_lessons_learned(
        self,
        collaboration: Dict[str, Any],
        impact_scores: Dict[str, float]
    ) -> List[str]:
        """Extract lessons learned from collaboration"""
        lessons = []
        
        avg_impact = statistics.mean(list(impact_scores.values()))
        
        if avg_impact > 0.2:
            lessons.append("High-synergy collaborations drive significant performance gains")
        
        if max(impact_scores.values()) > min(impact_scores.values()) * 2:
            lessons.append("Uneven impact suggests importance of creator compatibility")
        
        lessons.extend([
            "Proper planning and coordination are critical for success",
            "Cross-promotion strategies should be aligned early",
            "Content quality should not be compromised for collaboration"
        ])
        
        return lessons


# Export main classes
__all__ = [
    'PerformanceAnalyzer',
    'CreatorPerformanceProfile',
    'PerformanceAnalysisResult',
    'CollaborationImpactAssessment',
    'PerformanceMetric',
    'CollaborationPerformance',
    'PerformanceMetricType',
    'CollaborationType',
    'PerformanceTrend'
]