"""Content Performance Analytics
Advanced analytics system for multi-platform content performance tracking.

Features:
- Multi-platform performance tracking
- Content ROI analysis
- SEO impact measurement
- Creator collaboration analytics
- Content lifecycle analysis
- Monetization correlation
- Audience engagement analysis
- Content optimization recommendations

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

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Expertise: Lead Dev IA + Data Scientist + Analytics Expert + Performance Engineer
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.decomposition import PCA
    from sklearn.metrics import mean_squared_error, r2_score, classification_report
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    from scipy import stats
    from scipy.signal import find_peaks
    import warnings
    warnings.filterwarnings('ignore')
except ImportError as e:
    logging.warning(f"Optional performance analytics dependencies not available: {e}")

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of content metrics."""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    COST = "cost"
    ROI = "roi"
    RETENTION = "retention"
    GROWTH = "growth"


class AnalyticsTimeframe(Enum):
    """Analytics timeframes."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    REAL_TIME = "real_time"
    CUSTOM = "custom"


class Platform(Enum):
    """Supported platforms for analytics."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    PODCAST = "podcast"
    BLOG = "blog"
    WEBSITE = "website"


class ContentCategory(Enum):
    """Content categories for analysis."""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    PROMOTIONAL = "promotional"
    BEHIND_SCENES = "behind_scenes"
    USER_GENERATED = "user_generated"
    LIVE = "live"
    STORY = "story"
    POST = "post"
    VIDEO = "video"
    AUDIO = "audio"


@dataclass
class ContentMetrics:
    """Comprehensive content metrics."""
    content_id: str
    platform: Platform
    category: ContentCategory
    publish_date: datetime
    views: Optional[int] = None
    impressions: Optional[int] = None
    reach: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    clicks: Optional[int] = None
    engagement_rate: Optional[float] = None
    click_through_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    watch_time: Optional[float] = None
    completion_rate: Optional[float] = None
    bounce_rate: Optional[float] = None
    revenue: Optional[float] = None
    cost: Optional[float] = None
    roi: Optional[float] = None
    audience_retention: List[float] = field(default_factory=list)
    demographic_data: Dict[str, Any] = field(default_factory=dict)
    device_data: Dict[str, float] = field(default_factory=dict)
    traffic_sources: Dict[str, float] = field(default_factory=dict)
    peak_engagement_times: List[datetime] = field(default_factory=list)


@dataclass
class PerformanceTrend:
    """Performance trend analysis."""
    metric_type: MetricType
    platform: Platform
    timeframe: AnalyticsTimeframe
    trend_direction: str  # "increasing", "decreasing", "stable", "volatile"
    growth_rate: float
    seasonal_pattern: bool
    anomalies: List[datetime] = field(default_factory=list)
    predictions: Dict[str, float] = field(default_factory=dict)
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    correlation_factors: Dict[str, float] = field(default_factory=dict)


@dataclass
class CompetitorAnalysis:
    """Competitor performance analysis."""
    competitor_id: str
    competitor_name: str
    platform: Platform
    content_frequency: float
    avg_engagement_rate: float
    top_performing_content: List[str] = field(default_factory=list)
    content_themes: Dict[str, float] = field(default_factory=dict)
    posting_patterns: Dict[str, Any] = field(default_factory=dict)
    audience_overlap: float = 0.0
    performance_gap: Dict[MetricType, float] = field(default_factory=dict)
    growth_trends: Dict[str, float] = field(default_factory=dict)
    strategic_insights: List[str] = field(default_factory=list)


@dataclass
class ROIAnalysis:
    """Return on Investment analysis."""
    content_id: str
    platform: Platform
    investment: float
    revenue: float
    roi_percentage: float
    cost_per_engagement: float
    cost_per_conversion: float
    lifetime_value: float
    payback_period: Optional[int] = None  # days
    break_even_point: Optional[datetime] = None
    revenue_attribution: Dict[str, float] = field(default_factory=dict)
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    optimization_recommendations: List[str] = field(default_factory=list)


@dataclass
class AudienceInsights:
    """Detailed audience analytics."""
    platform: Platform
    total_audience: int
    demographics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    interests: Dict[str, float] = field(default_factory=dict)
    behaviors: Dict[str, float] = field(default_factory=dict)
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    device_usage: Dict[str, float] = field(default_factory=dict)
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    growth_segments: Dict[str, float] = field(default_factory=dict)
    churn_analysis: Dict[str, Any] = field(default_factory=dict)
    lookalike_opportunities: List[str] = field(default_factory=list)


@dataclass
class ContentPerformanceReport:
    """Comprehensive content performance report."""
    report_date: datetime
    timeframe: AnalyticsTimeframe
    content_metrics: List[ContentMetrics]
    performance_trends: List[PerformanceTrend]
    competitor_analysis: List[CompetitorAnalysis]
    roi_analysis: List[ROIAnalysis]
    audience_insights: Dict[Platform, AudienceInsights]
    top_performers: Dict[Platform, List[str]]
    underperformers: Dict[Platform, List[str]]
    optimization_opportunities: List[str]
    strategic_recommendations: List[str]
    predictive_insights: Dict[str, Any]
    anomaly_alerts: List[Dict[str, Any]]
    benchmark_comparisons: Dict[str, Dict[str, float]]
    content_lifecycle_analysis: Dict[str, Any]
    cross_platform_insights: Dict[str, Any]


class ContentPerformanceAnalytics:
    """Advanced analytics system for comprehensive content performance tracking.
    
    Provides deep insights into content performance across platforms, ROI analysis,
    audience behavior, and predictive analytics for strategic optimization.
    """
    
    def __init__(self, 
                 enable_predictive_analytics: bool = True,
                 enable_real_time_tracking: bool = True,
                 benchmark_data_source: Optional[str] = None):
        """Initialize Content Performance Analytics.
        
        Args:
            enable_predictive_analytics: Enable ML-based predictive analytics
            enable_real_time_tracking: Enable real-time performance tracking
            benchmark_data_source: External benchmark data source
        """
        self.enable_predictive_analytics = enable_predictive_analytics
        self.enable_real_time_tracking = enable_real_time_tracking
        self.benchmark_data_source = benchmark_data_source
        
        # Analytics models
        self.performance_models = {}
        self.trend_models = {}
        self.anomaly_detectors = {}
        
        # Data storage
        self.metrics_cache = {}
        self.trend_cache = {}
        self.benchmark_cache = {}
        
        if enable_predictive_analytics:
            self._initialize_predictive_models()
        
        # Analytics configuration
        self.config = {
            "min_data_points": 10,
            "confidence_threshold": 0.8,
            "anomaly_threshold": 2.0,  # Standard deviations
            "trend_window": 30,  # days
            "forecast_horizon": 7,  # days
            "update_frequency": 3600  # seconds
        }
        
        logger.info("Content Performance Analytics initialized successfully")
    
    async def analyze_content_performance(self,
                                        content_metrics: List[ContentMetrics],
                                        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY,
                                        include_predictions: bool = True,
                                        include_competitors: bool = True) -> ContentPerformanceReport:
        """Perform comprehensive content performance analysis.
        
        Args:
            content_metrics: List of content metrics to analyze
            timeframe: Analysis timeframe
            include_predictions: Include predictive analytics
            include_competitors: Include competitor analysis
            
        Returns:
            ContentPerformanceReport with comprehensive insights
        """
        try:
            logger.info(f"Analyzing performance for {len(content_metrics)} content items")
            
            # Analyze performance trends
            performance_trends = await self._analyze_performance_trends(content_metrics, timeframe)
            
            # Competitor analysis
            competitor_analysis = []
            if include_competitors:
                competitor_analysis = await self._perform_competitor_analysis(content_metrics)
            
            # ROI analysis
            roi_analysis = await self._calculate_roi_analysis(content_metrics)
            
            # Audience insights
            audience_insights = await self._generate_audience_insights(content_metrics)
            
            # Identify top and underperformers
            top_performers, underperformers = await self._identify_performance_segments(content_metrics)
            
            # Generate optimization opportunities
            optimization_opportunities = await self._identify_optimization_opportunities(
                content_metrics, performance_trends
            )
            
            # Strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                content_metrics, performance_trends, roi_analysis
            )
            
            # Predictive insights
            predictive_insights = {}
            if include_predictions and self.enable_predictive_analytics:
                predictive_insights = await self._generate_predictive_insights(
                    content_metrics, performance_trends
                )
            
            # Anomaly detection
            anomaly_alerts = await self._detect_performance_anomalies(content_metrics)
            
            # Benchmark comparisons
            benchmark_comparisons = await self._perform_benchmark_analysis(content_metrics)
            
            # Content lifecycle analysis
            lifecycle_analysis = await self._analyze_content_lifecycle(content_metrics)
            
            # Cross-platform insights
            cross_platform_insights = await self._generate_cross_platform_insights(content_metrics)
            
            return ContentPerformanceReport(
                report_date=datetime.now(),
                timeframe=timeframe,
                content_metrics=content_metrics,
                performance_trends=performance_trends,
                competitor_analysis=competitor_analysis,
                roi_analysis=roi_analysis,
                audience_insights=audience_insights,
                top_performers=top_performers,
                underperformers=underperformers,
                optimization_opportunities=optimization_opportunities,
                strategic_recommendations=strategic_recommendations,
                predictive_insights=predictive_insights,
                anomaly_alerts=anomaly_alerts,
                benchmark_comparisons=benchmark_comparisons,
                content_lifecycle_analysis=lifecycle_analysis,
                cross_platform_insights=cross_platform_insights
            )
            
        except Exception as e:
            logger.error(f"Error in content performance analysis: {e}")
            raise
    
    async def track_real_time_performance(self,
                                        content_id: str,
                                        platform: Platform,
                                        duration_hours: int = 24) -> Dict[str, Any]:
        """Track real-time performance for specific content.
        
        Args:
            content_id: Content identifier
            platform: Platform to track
            duration_hours: Tracking duration in hours
            
        Returns:
            Dictionary with real-time performance data
        """
        try:
            if not self.enable_real_time_tracking:
                logger.warning("Real-time tracking is disabled")
                return {}
            
            real_time_data = {
                "content_id": content_id,
                "platform": platform.value,
                "start_time": datetime.now(),
                "duration_hours": duration_hours,
                "metrics_timeline": [],
                "engagement_peaks": [],
                "growth_rate": 0.0,
                "velocity_score": 0.0,
                "viral_indicators": {},
                "audience_behavior": {},
                "optimization_alerts": []
            }
            
            # Simulate real-time tracking (would integrate with actual APIs)
            start_time = datetime.now()
            for hour in range(duration_hours):
                current_time = start_time + timedelta(hours=hour)
                
                # Generate mock metrics for demonstration
                metrics_snapshot = {
                    "timestamp": current_time,
                    "views": hour * 100 + np.random.randint(50, 200),
                    "likes": hour * 10 + np.random.randint(5, 20),
                    "comments": hour * 2 + np.random.randint(1, 5),
                    "shares": hour * 1 + np.random.randint(0, 3),
                    "engagement_rate": (hour * 0.01 + np.random.uniform(0.02, 0.08))
                }
                
                real_time_data["metrics_timeline"].append(metrics_snapshot)
            
            # Analyze real-time patterns
            real_time_data["engagement_peaks"] = self._identify_engagement_peaks(
                real_time_data["metrics_timeline"]
            )
            
            real_time_data["growth_rate"] = self._calculate_growth_rate(
                real_time_data["metrics_timeline"]
            )
            
            real_time_data["velocity_score"] = self._calculate_velocity_score(
                real_time_data["metrics_timeline"]
            )
            
            return real_time_data
            
        except Exception as e:
            logger.error(f"Error in real-time tracking: {e}")
            return {}
    
    async def generate_performance_forecast(self,
                                          content_metrics: List[ContentMetrics],
                                          forecast_days: int = 7,
                                          confidence_level: float = 0.95) -> Dict[str, Any]:
        """Generate performance forecasts using predictive analytics.
        
        Args:
            content_metrics: Historical content metrics
            forecast_days: Number of days to forecast
            confidence_level: Confidence level for predictions
            
        Returns:
            Dictionary with forecast results
        """
        try:
            if not self.enable_predictive_analytics:
                logger.warning("Predictive analytics is disabled")
                return {}
            
            forecast_results = {
                "forecast_period": forecast_days,
                "confidence_level": confidence_level,
                "predictions_by_platform": {},
                "trend_forecasts": {},
                "performance_scenarios": {},
                "recommendation_impact": {},
                "risk_assessments": {}
            }
            
            # Group metrics by platform
            platform_metrics = {}
            for metric in content_metrics:
                if metric.platform not in platform_metrics:
                    platform_metrics[metric.platform] = []
                platform_metrics[metric.platform].append(metric)
            
            # Generate forecasts for each platform
            for platform, metrics in platform_metrics.items():
                if len(metrics) < self.config["min_data_points"]:
                    continue
                
                platform_forecast = await self._forecast_platform_performance(
                    metrics, forecast_days, confidence_level
                )
                forecast_results["predictions_by_platform"][platform.value] = platform_forecast
            
            # Generate trend forecasts
            forecast_results["trend_forecasts"] = await self._forecast_content_trends(
                content_metrics, forecast_days
            )
            
            # Performance scenarios
            forecast_results["performance_scenarios"] = await self._generate_performance_scenarios(
                content_metrics, forecast_days
            )
            
            return forecast_results
            
        except Exception as e:
            logger.error(f"Error generating performance forecast: {e}")
            return {}
    
    async def analyze_content_roi(self,
                                content_metrics: List[ContentMetrics],
                                cost_data: Dict[str, float],
                                attribution_model: str = "linear") -> List[ROIAnalysis]:
        """Analyze return on investment for content.
        
        Args:
            content_metrics: Content performance metrics
            cost_data: Cost data for content creation/promotion
            attribution_model: Attribution model for revenue calculation
            
        Returns:
            List of ROI analysis results
        """
        try:
            roi_analyses = []
            
            for metric in content_metrics:
                content_cost = cost_data.get(metric.content_id, 0.0)
                content_revenue = metric.revenue or 0.0
                
                if content_cost > 0:
                    roi_percentage = ((content_revenue - content_cost) / content_cost) * 100
                else:
                    roi_percentage = 0.0 if content_revenue == 0 else float('inf')
                
                # Calculate additional ROI metrics
                engagement_cost = content_cost / max(1, (metric.likes or 0) + (metric.comments or 0) + (metric.shares or 0))
                conversion_cost = content_cost / max(1, metric.clicks or 0) if metric.clicks else 0
                
                # Estimate lifetime value
                lifetime_value = await self._estimate_content_lifetime_value(metric)
                
                # Calculate payback period
                payback_period = await self._calculate_payback_period(metric, content_cost)
                
                roi_analysis = ROIAnalysis(
                    content_id=metric.content_id,
                    platform=metric.platform,
                    investment=content_cost,
                    revenue=content_revenue,
                    roi_percentage=roi_percentage,
                    cost_per_engagement=engagement_cost,
                    cost_per_conversion=conversion_cost,
                    lifetime_value=lifetime_value,
                    payback_period=payback_period,
                    revenue_attribution=self._calculate_revenue_attribution(metric, attribution_model),
                    cost_breakdown=self._breakdown_content_costs(content_cost),
                    optimization_recommendations=self._generate_roi_recommendations(metric, roi_percentage)
                )
                
                roi_analyses.append(roi_analysis)
            
            return roi_analyses
            
        except Exception as e:
            logger.error(f"Error analyzing content ROI: {e}")
            return []
    
    # Private helper methods
    
    def _initialize_predictive_models(self) -> None:
        """Initialize machine learning models for predictions."""
        try:
            # Performance prediction models
            self.performance_models = {
                "engagement_predictor": RandomForestRegressor(n_estimators=100, random_state=42),
                "view_predictor": GradientBoostingRegressor(n_estimators=100, random_state=42),
                "roi_predictor": LinearRegression(),
                "viral_classifier": LogisticRegression(random_state=42)
            }
            
            # Trend analysis models
            self.trend_models = {
                "trend_detector": LinearRegression(),
                "seasonality_detector": RandomForestRegressor(n_estimators=50, random_state=42)
            }
            
            # Anomaly detection
            self.anomaly_detectors = {
                "isolation_forest": None,  # Would initialize with actual IsolationForest
                "z_score_detector": None
            }
            
            logger.info("Predictive models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing predictive models: {e}")
    
    async def _analyze_performance_trends(self,
                                        content_metrics: List[ContentMetrics],
                                        timeframe: AnalyticsTimeframe) -> List[PerformanceTrend]:
        """Analyze performance trends across metrics."""
        try:
            trends = []
            
            # Group metrics by platform and metric type
            for platform in Platform:
                platform_metrics = [m for m in content_metrics if m.platform == platform]
                if not platform_metrics:
                    continue
                
                # Analyze different metric types
                for metric_type in MetricType:
                    trend = await self._calculate_metric_trend(
                        platform_metrics, metric_type, timeframe
                    )
                    if trend:
                        trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return []
    
    async def _calculate_metric_trend(self,
                                    metrics: List[ContentMetrics],
                                    metric_type: MetricType,
                                    timeframe: AnalyticsTimeframe) -> Optional[PerformanceTrend]:
        """Calculate trend for specific metric type."""
        try:
            # Extract metric values
            metric_values = []
            dates = []
            
            for metric in metrics:
                value = None
                if metric_type == MetricType.ENGAGEMENT:
                    value = metric.engagement_rate
                elif metric_type == MetricType.VIEWS:
                    value = metric.views
                elif metric_type == MetricType.LIKES:
                    value = metric.likes
                elif metric_type == MetricType.REVENUE:
                    value = metric.revenue
                # Add more metric types as needed
                
                if value is not None:
                    metric_values.append(value)
                    dates.append(metric.publish_date)
            
            if len(metric_values) < 2:
                return None
            
            # Calculate trend direction and growth rate
            values_array = np.array(metric_values)
            trend_direction = "stable"
            growth_rate = 0.0
            
            if len(values_array) > 1:
                # Simple linear regression for trend
                x = np.arange(len(values_array))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, values_array)
                
                if slope > 0.1:
                    trend_direction = "increasing"
                elif slope < -0.1:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
                
                growth_rate = slope
            
            # Detect seasonality (simplified)
            seasonal_pattern = len(set(dates)) > 7 and len(values_array) > 14
            
            trend = PerformanceTrend(
                metric_type=metric_type,
                platform=metrics[0].platform,
                timeframe=timeframe,
                trend_direction=trend_direction,
                growth_rate=growth_rate,
                seasonal_pattern=seasonal_pattern,
                confidence_interval=(growth_rate - std_err, growth_rate + std_err) if 'std_err' in locals() else (0.0, 0.0)
            )
            
            return trend
            
        except Exception as e:
            logger.error(f"Error calculating metric trend: {e}")
            return None
    
    async def _perform_competitor_analysis(self, content_metrics: List[ContentMetrics]) -> List[CompetitorAnalysis]:
        """Perform competitor analysis (simplified mock implementation)."""
        try:
            # This would integrate with actual competitor data sources
            competitor_analyses = []
            
            platforms = set(metric.platform for metric in content_metrics)
            
            for platform in platforms:
                # Mock competitor data
                competitor = CompetitorAnalysis(
                    competitor_id="competitor_1",
                    competitor_name="Top Competitor",
                    platform=platform,
                    content_frequency=1.2,  # posts per day
                    avg_engagement_rate=0.05,
                    top_performing_content=["video_1", "post_2", "story_3"],
                    content_themes={"educational": 0.4, "entertainment": 0.6},
                    posting_patterns={"peak_times": ["12pm", "6pm", "9pm"]},
                    audience_overlap=0.25,
                    performance_gap={MetricType.ENGAGEMENT: -0.02, MetricType.REACH: -1000},
                    strategic_insights=[
                        "Competitor posts more frequently",
                        "Higher engagement on video content",
                        "Strong evening posting performance"
                    ]
                )
                
                competitor_analyses.append(competitor)
            
            return competitor_analyses
            
        except Exception as e:
            logger.error(f"Error in competitor analysis: {e}")
            return []
    
    async def _calculate_roi_analysis(self, content_metrics: List[ContentMetrics]) -> List[ROIAnalysis]:
        """Calculate ROI analysis for content."""
        try:
            roi_analyses = []
            
            for metric in content_metrics:
                # Mock cost and revenue data
                mock_cost = 100.0  # $100 base cost
                mock_revenue = metric.revenue or (metric.views or 0) * 0.01  # $0.01 per view
                
                roi_percentage = ((mock_revenue - mock_cost) / mock_cost) * 100 if mock_cost > 0 else 0
                
                roi_analysis = ROIAnalysis(
                    content_id=metric.content_id,
                    platform=metric.platform,
                    investment=mock_cost,
                    revenue=mock_revenue,
                    roi_percentage=roi_percentage,
                    cost_per_engagement=mock_cost / max(1, (metric.likes or 0) + (metric.comments or 0)),
                    cost_per_conversion=mock_cost / max(1, metric.clicks or 0) if metric.clicks else 0,
                    lifetime_value=mock_revenue * 1.5,  # Estimated LTV
                    optimization_recommendations=self._generate_roi_recommendations(metric, roi_percentage)
                )
                
                roi_analyses.append(roi_analysis)
            
            return roi_analyses
            
        except Exception as e:
            logger.error(f"Error calculating ROI analysis: {e}")
            return []
    
    async def _generate_audience_insights(self, content_metrics: List[ContentMetrics]) -> Dict[Platform, AudienceInsights]:
        """Generate audience insights per platform."""
        try:
            insights = {}
            
            platforms = set(metric.platform for metric in content_metrics)
            
            for platform in platforms:
                platform_metrics = [m for m in content_metrics if m.platform == platform]
                
                # Aggregate audience data
                total_reach = sum(m.reach or 0 for m in platform_metrics)
                
                # Mock demographic data
                audience_insight = AudienceInsights(
                    platform=platform,
                    total_audience=total_reach,
                    demographics={
                        "age": {"18-24": 0.25, "25-34": 0.35, "35-44": 0.25, "45+": 0.15},
                        "gender": {"male": 0.45, "female": 0.55},
                        "location": {"urban": 0.7, "suburban": 0.2, "rural": 0.1}
                    },
                    interests={"technology": 0.3, "entertainment": 0.4, "lifestyle": 0.3},
                    behaviors={"mobile_users": 0.8, "desktop_users": 0.2},
                    engagement_patterns={"peak_hours": ["12pm", "6pm", "9pm"]},
                    device_usage={"mobile": 0.75, "desktop": 0.20, "tablet": 0.05},
                    growth_segments={"new_followers": 0.15, "returning_users": 0.85}
                )
                
                insights[platform] = audience_insight
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating audience insights: {e}")
            return {}
    
    # Additional helper methods (simplified for brevity)
    
    async def _identify_performance_segments(self, content_metrics: List[ContentMetrics]) -> Tuple[Dict[Platform, List[str]], Dict[Platform, List[str]]]:
        """Identify top performers and underperformers."""
        top_performers = {}
        underperformers = {}
        
        platforms = set(metric.platform for metric in content_metrics)
        
        for platform in platforms:
            platform_metrics = [m for m in content_metrics if m.platform == platform]
            
            # Sort by engagement rate
            sorted_metrics = sorted(
                platform_metrics,
                key=lambda x: x.engagement_rate or 0,
                reverse=True
            )
            
            total_count = len(sorted_metrics)
            top_count = max(1, total_count // 5)  # Top 20%
            bottom_count = max(1, total_count // 5)  # Bottom 20%
            
            top_performers[platform] = [m.content_id for m in sorted_metrics[:top_count]]
            underperformers[platform] = [m.content_id for m in sorted_metrics[-bottom_count:]]
        
        return top_performers, underperformers
    
    def _identify_engagement_peaks(self, metrics_timeline: List[Dict]) -> List[datetime]:
        """Identify engagement peaks in timeline."""
        if not metrics_timeline:
            return []
        
        engagement_rates = [m.get("engagement_rate", 0) for m in metrics_timeline]
        peaks, _ = find_peaks(engagement_rates, height=np.mean(engagement_rates))
        
        peak_times = [metrics_timeline[i]["timestamp"] for i in peaks if i < len(metrics_timeline)]
        return peak_times
    
    def _calculate_growth_rate(self, metrics_timeline: List[Dict]) -> float:
        """Calculate growth rate from timeline."""
        if len(metrics_timeline) < 2:
            return 0.0
        
        initial_views = metrics_timeline[0].get("views", 0)
        final_views = metrics_timeline[-1].get("views", 0)
        
        if initial_views == 0:
            return 0.0
        
        return ((final_views - initial_views) / initial_views) * 100
    
    def _calculate_velocity_score(self, metrics_timeline: List[Dict]) -> float:
        """Calculate content velocity score."""
        if not metrics_timeline:
            return 0.0
        
        # Simplified velocity calculation
        total_engagement = sum(
            m.get("likes", 0) + m.get("comments", 0) + m.get("shares", 0)
            for m in metrics_timeline
        )
        
        hours = len(metrics_timeline)
        return total_engagement / max(1, hours)
    
    def _generate_roi_recommendations(self, metric: ContentMetrics, roi_percentage: float) -> List[str]:
        """Generate ROI optimization recommendations."""
        recommendations = []
        
        if roi_percentage < 50:
            recommendations.append("Consider reducing production costs")
            recommendations.append("Improve content targeting for better engagement")
        
        if metric.engagement_rate and metric.engagement_rate < 0.03:
            recommendations.append("Focus on improving content quality and relevance")
        
        if metric.click_through_rate and metric.click_through_rate < 0.02:
            recommendations.append("Optimize call-to-action placement and messaging")
        
        return recommendations
    
    # Additional placeholder methods for completeness
    
    async def _identify_optimization_opportunities(self, content_metrics, trends):
        """Identify content optimization opportunities."""
        return [
            "Increase posting frequency during peak engagement hours",
            "Focus on video content for higher engagement rates",
            "Implement cross-platform promotion strategies"
        ]
    
    async def _generate_strategic_recommendations(self, content_metrics, trends, roi_analysis):
        """Generate strategic recommendations."""
        return [
            "Prioritize high-ROI content formats",
            "Expand presence on top-performing platforms",
            "Develop content series to improve audience retention"
        ]