"""
Ainflue Platform - Cross-Platform Analytics Aggregator
=====================================================

Advanced analytics aggregation system for collecting, processing, and unifying
analytics data across all platforms in the Ainflue ecosystem. Provides unified
insights, cross-platform performance analysis, and comprehensive reporting.

Features:
- Multi-platform data aggregation
- Real-time analytics processing
- Cross-platform performance analysis
- Unified reporting and insights
- Data synchronization and normalization
- Advanced correlation analysis

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import math
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Platform(Enum):
    """Supported platforms for analytics aggregation."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"

class MetricType(Enum):
    """Types of analytics metrics."""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    FOLLOWERS = "followers"
    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"

class AggregationPeriod(Enum):
    """Aggregation time periods."""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class PlatformMetric:
    """Individual platform metric data point."""
    metric_id: str
    platform: Platform
    metric_type: MetricType
    value: float
    timestamp: datetime
    content_id: Optional[str] = None
    user_id: Optional[str] = None
    campaign_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AggregatedMetric:
    """Aggregated metric across platforms."""
    aggregation_id: str
    metric_type: MetricType
    total_value: float
    platform_breakdown: Dict[Platform, float]
    period: AggregationPeriod
    start_time: datetime
    end_time: datetime
    data_quality_score: float = 1.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    trend_direction: str = "stable"  # increasing, decreasing, stable
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CrossPlatformInsight:
    """Cross-platform analytics insight."""
    insight_id: str
    title: str
    description: str
    insight_type: str
    platforms_involved: List[Platform]
    metrics_analyzed: List[MetricType]
    key_findings: List[str]
    recommendations: List[str]
    confidence_score: float
    impact_score: float
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class PlatformPerformance:
    """Platform-specific performance analysis."""
    platform: Platform
    performance_score: float
    growth_rate: float
    engagement_rate: float
    reach_efficiency: float
    content_performance: Dict[str, float]
    audience_quality: float
    monetization_potential: float
    competitive_position: str
    optimization_opportunities: List[str]
    analyzed_at: datetime = field(default_factory=datetime.now)

class CrossPlatformAnalyticsAggregator:
    """
    Advanced cross-platform analytics aggregation system for the Ainflue platform.
    
    Collects, processes, and unifies analytics data from multiple platforms
    to provide comprehensive insights and cross-platform performance analysis.
    """
    
    def __init__(self) -> None:
        """Initialize the cross-platform analytics aggregator."""
        self.platform_metrics: Dict[Platform, List[PlatformMetric]] = defaultdict(list)
        self.aggregated_metrics: List[AggregatedMetric] = []
        self.cross_platform_insights: List[CrossPlatformInsight] = []
        self.platform_performances: Dict[Platform, PlatformPerformance] = {}
        self.data_connectors: Dict[Platform, Dict[str, Any]] = {}
        self.aggregation_rules: Dict[str, Any] = {}
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}
        
        logger.info("Initializing Cross-Platform Analytics Aggregator")
        self._setup_data_connectors()
        self._initialize_aggregation_rules()
        self._setup_correlation_tracking()
    
    def _setup_data_connectors(self) -> None:
        """Setup data connectors for each platform."""
        for platform in Platform:
            self.data_connectors[platform] = {
                "api_endpoint": f"https://api.{platform.value}.com",
                "authentication": "oauth2",
                "rate_limit": self._get_platform_rate_limit(platform),
                "data_freshness_minutes": self._get_data_freshness_requirement(platform),
                "supported_metrics": self._get_supported_metrics(platform),
                "last_sync": None,
                "status": "active"
            }
    
    def _get_platform_rate_limit(self, platform: Platform) -> int:
        """Get rate limit for platform API."""
        rate_limits = {
            Platform.YOUTUBE: 10000,
            Platform.INSTAGRAM: 4800,
            Platform.TIKTOK: 1000,
            Platform.TWITTER: 2000000,
            Platform.FACEBOOK: 4800,
            Platform.LINKEDIN: 500,
            Platform.TWITCH: 800,
            Platform.SPOTIFY: 1000,
            Platform.SOUNDCLOUD: 15000,
            Platform.PINTEREST: 1000,
            Platform.SNAPCHAT: 1000,
            Platform.DISCORD: 5000
        }
        return rate_limits.get(platform, 1000)
    
    def _get_data_freshness_requirement(self, platform: Platform) -> int:
        """Get data freshness requirement in minutes."""
        freshness_requirements = {
            Platform.YOUTUBE: 60,
            Platform.INSTAGRAM: 30,
            Platform.TIKTOK: 15,
            Platform.TWITTER: 5,
            Platform.FACEBOOK: 60,
            Platform.LINKEDIN: 120,
            Platform.TWITCH: 10,
            Platform.SPOTIFY: 60,
            Platform.SOUNDCLOUD: 60,
            Platform.PINTEREST: 60,
            Platform.SNAPCHAT: 30,
            Platform.DISCORD: 15
        }
        return freshness_requirements.get(platform, 60)
    
    def _get_supported_metrics(self, platform: Platform) -> List[MetricType]:
        """Get supported metrics for each platform."""
        platform_metrics = {
            Platform.YOUTUBE: [MetricType.VIEWS, MetricType.LIKES, MetricType.COMMENTS, MetricType.SHARES, MetricType.REVENUE],
            Platform.INSTAGRAM: [MetricType.LIKES, MetricType.COMMENTS, MetricType.SHARES, MetricType.SAVES, MetricType.REACH, MetricType.IMPRESSIONS],
            Platform.TIKTOK: [MetricType.VIEWS, MetricType.LIKES, MetricType.COMMENTS, MetricType.SHARES, MetricType.REACH],
            Platform.TWITTER: [MetricType.IMPRESSIONS, MetricType.ENGAGEMENT, MetricType.CLICKS, MetricType.LIKES, MetricType.SHARES],
            Platform.FACEBOOK: [MetricType.REACH, MetricType.ENGAGEMENT, MetricType.CLICKS, MetricType.IMPRESSIONS, MetricType.SHARES],
            Platform.LINKEDIN: [MetricType.IMPRESSIONS, MetricType.CLICKS, MetricType.ENGAGEMENT, MetricType.FOLLOWERS],
            Platform.TWITCH: [MetricType.VIEWS, MetricType.FOLLOWERS, MetricType.ENGAGEMENT, MetricType.REVENUE],
            Platform.SPOTIFY: [MetricType.VIEWS, MetricType.FOLLOWERS, MetricType.REVENUE],
            Platform.SOUNDCLOUD: [MetricType.VIEWS, MetricType.LIKES, MetricType.COMMENTS, MetricType.FOLLOWERS],
            Platform.PINTEREST: [MetricType.IMPRESSIONS, MetricType.CLICKS, MetricType.SAVES, MetricType.ENGAGEMENT],
            Platform.SNAPCHAT: [MetricType.VIEWS, MetricType.REACH, MetricType.ENGAGEMENT],
            Platform.DISCORD: [MetricType.ENGAGEMENT, MetricType.FOLLOWERS]
        }
        return platform_metrics.get(platform, [MetricType.ENGAGEMENT, MetricType.REACH])
    
    def _initialize_aggregation_rules(self) -> None:
        """Initialize aggregation rules for different metrics."""
        self.aggregation_rules = {
            "default_weights": {
                Platform.YOUTUBE: 0.25,
                Platform.INSTAGRAM: 0.20,
                Platform.TIKTOK: 0.15,
                Platform.TWITTER: 0.10,
                Platform.FACEBOOK: 0.15,
                Platform.LINKEDIN: 0.05,
                Platform.TWITCH: 0.10
            },
            "metric_normalization": {
                MetricType.ENGAGEMENT: "rate_based",  # Normalize by followers
                MetricType.REACH: "absolute",
                MetricType.REVENUE: "absolute",
                MetricType.VIEWS: "absolute",
                MetricType.LIKES: "rate_based"
            },
            "aggregation_methods": {
                MetricType.REVENUE: "sum",
                MetricType.VIEWS: "sum",
                MetricType.REACH: "sum",
                MetricType.ENGAGEMENT: "weighted_average",
                MetricType.FOLLOWERS: "sum"
            },
            "data_quality_thresholds": {
                "minimum_platforms": 3,
                "maximum_age_hours": 24,
                "minimum_confidence": 0.7
            }
        }
    
    def _setup_correlation_tracking(self) -> None:
        """Setup correlation tracking between platforms and metrics."""
        # Initialize correlation matrix
        platforms = list(Platform)
        for platform1 in platforms:
            self.correlation_matrix[platform1.value] = {}
            for platform2 in platforms:
                # Initialize with neutral correlation
                self.correlation_matrix[platform1.value][platform2.value] = 0.0
    
    def ingest_platform_data(
        self,
        platform: Platform,
        metrics_data: List[Dict[str, Any]],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Ingest analytics data from a specific platform."""
        
        try:
            ingested_metrics = []
            ingestion_timestamp = timestamp or datetime.now()
            
            for metric_data in metrics_data:
                # Validate and create metric
                metric = self._create_platform_metric(platform, metric_data, ingestion_timestamp)
                if metric:
                    ingested_metrics.append(metric)
            
            # Store metrics
            self.platform_metrics[platform].extend(ingested_metrics)
            
            # Update connector status
            self.data_connectors[platform]["last_sync"] = ingestion_timestamp
            self.data_connectors[platform]["status"] = "active"
            
            # Trigger aggregation if enough data
            if len(ingested_metrics) > 0:
                self._trigger_aggregation_if_needed()
            
            logger.info(f"Ingested {len(ingested_metrics)} metrics from {platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest data from {platform.value}: {e}")
            self.data_connectors[platform]["status"] = "error"
            return False
    
    def _create_platform_metric(
        self,
        platform: Platform,
        metric_data: Dict[str, Any],
        timestamp: datetime
    ) -> Optional[PlatformMetric]:
        """Create a platform metric from raw data."""
        
        try:
            metric_type_str = metric_data.get("metric_type", "").lower()
            metric_type = None
            
            # Map metric type
            for mt in MetricType:
                if mt.value.lower() == metric_type_str:
                    metric_type = mt
                    break
            
            if not metric_type:
                logger.warning(f"Unknown metric type: {metric_type_str}")
                return None
            
            # Validate value
            value = float(metric_data.get("value", 0))
            if value < 0:
                logger.warning(f"Negative metric value: {value}")
                return None
            
            return PlatformMetric(
                metric_id=f"metric_{uuid.uuid4().hex[:8]}",
                platform=platform,
                metric_type=metric_type,
                value=value,
                timestamp=timestamp,
                content_id=metric_data.get("content_id"),
                user_id=metric_data.get("user_id"),
                campaign_id=metric_data.get("campaign_id"),
                metadata=metric_data.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to create metric: {e}")
            return None
    
    def _trigger_aggregation_if_needed(self) -> None:
        """Trigger aggregation if conditions are met."""
        
        # Check if we have enough recent data from multiple platforms
        recent_cutoff = datetime.now() - timedelta(hours=1)
        platforms_with_recent_data = 0
        
        for platform, metrics in self.platform_metrics.items():
            recent_metrics = [m for m in metrics if m.timestamp > recent_cutoff]
            if recent_metrics:
                platforms_with_recent_data += 1
        
        # Trigger aggregation if we have data from multiple platforms
        min_platforms = self.aggregation_rules["data_quality_thresholds"]["minimum_platforms"]
        if platforms_with_recent_data >= min_platforms:
            self._perform_periodic_aggregation(AggregationPeriod.HOURLY)
    
    def aggregate_metrics(
        self,
        metric_type: MetricType,
        period: AggregationPeriod,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> AggregatedMetric:
        """Aggregate metrics across platforms for a specific period."""
        
        # Set time range
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = self._calculate_period_start(end_time, period)
        
        # Collect relevant metrics
        relevant_metrics = self._collect_metrics_for_period(metric_type, start_time, end_time)
        
        # Perform aggregation
        aggregated_value, platform_breakdown = self._aggregate_metric_values(relevant_metrics, metric_type)
        
        # Calculate data quality
        data_quality = self._calculate_data_quality(relevant_metrics, start_time, end_time)
        
        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(relevant_metrics, aggregated_value)
        
        # Determine trend direction
        trend_direction = self._determine_trend_direction(metric_type, aggregated_value, period)
        
        # Create aggregated metric
        aggregated_metric = AggregatedMetric(
            aggregation_id=f"agg_{uuid.uuid4().hex[:8]}",
            metric_type=metric_type,
            total_value=aggregated_value,
            platform_breakdown=platform_breakdown,
            period=period,
            start_time=start_time,
            end_time=end_time,
            data_quality_score=data_quality,
            confidence_interval=confidence_interval,
            trend_direction=trend_direction
        )
        
        self.aggregated_metrics.append(aggregated_metric)
        
        logger.info(f"Aggregated {metric_type.value} for {period.value}: {aggregated_value}")
        return aggregated_metric
    
    def _calculate_period_start(self, end_time: datetime, period: AggregationPeriod) -> datetime:
        """Calculate start time for aggregation period."""
        
        if period == AggregationPeriod.HOURLY:
            return end_time - timedelta(hours=1)
        elif period == AggregationPeriod.DAILY:
            return end_time - timedelta(days=1)
        elif period == AggregationPeriod.WEEKLY:
            return end_time - timedelta(weeks=1)
        elif period == AggregationPeriod.MONTHLY:
            return end_time - timedelta(days=30)
        elif period == AggregationPeriod.QUARTERLY:
            return end_time - timedelta(days=90)
        elif period == AggregationPeriod.YEARLY:
            return end_time - timedelta(days=365)
        else:
            return end_time - timedelta(hours=1)
    
    def _collect_metrics_for_period(
        self,
        metric_type: MetricType,
        start_time: datetime,
        end_time: datetime
    ) -> List[PlatformMetric]:
        """Collect metrics for the specified period."""
        
        relevant_metrics = []
        
        for platform, metrics in self.platform_metrics.items():
            platform_metrics = [
                metric for metric in metrics
                if (metric.metric_type == metric_type and
                    start_time <= metric.timestamp <= end_time)
            ]
            relevant_metrics.extend(platform_metrics)
        
        return relevant_metrics
    
    def _aggregate_metric_values(
        self,
        metrics: List[PlatformMetric],
        metric_type: MetricType
    ) -> Tuple[float, Dict[Platform, float]]:
        """Aggregate metric values according to aggregation rules."""
        
        if not metrics:
            return 0.0, {}
        
        # Group by platform
        platform_values = defaultdict(list)
        for metric in metrics:
            platform_values[metric.platform].append(metric.value)
        
        # Calculate platform totals
        platform_breakdown = {}
        for platform, values in platform_values.items():
            if values:
                aggregation_method = self.aggregation_rules["aggregation_methods"].get(metric_type, "sum")
                
                if aggregation_method == "sum":
                    platform_breakdown[platform] = sum(values)
                elif aggregation_method == "average":
                    platform_breakdown[platform] = statistics.mean(values)
                elif aggregation_method == "weighted_average":
                    # Use platform weights
                    weight = self.aggregation_rules["default_weights"].get(platform, 0.1)
                    platform_breakdown[platform] = statistics.mean(values) * weight
                else:
                    platform_breakdown[platform] = sum(values)
        
        # Calculate total
        total_value = sum(platform_breakdown.values())
        
        return total_value, platform_breakdown
    
    def _calculate_data_quality(
        self,
        metrics: List[PlatformMetric],
        start_time: datetime,
        end_time: datetime
    ) -> float:
        """Calculate data quality score for aggregation."""
        
        quality_factors = []
        
        # Completeness - number of platforms with data
        platforms_with_data = len(set(metric.platform for metric in metrics))
        total_platforms = len(Platform)
        completeness = platforms_with_data / total_platforms
        quality_factors.append(("completeness", completeness, 0.4))
        
        # Freshness - how recent is the data
        if metrics:
            avg_age_hours = statistics.mean([
                (datetime.now() - metric.timestamp).total_seconds() / 3600
                for metric in metrics
            ])
            max_age = self.aggregation_rules["data_quality_thresholds"]["maximum_age_hours"]
            freshness = max(0.0, 1.0 - (avg_age_hours / max_age))
        else:
            freshness = 0.0
        quality_factors.append(("freshness", freshness, 0.3))
        
        # Consistency - variance in data points
        if len(metrics) > 1:
            values = [metric.value for metric in metrics]
            if statistics.stdev(values) > 0:
                cv = statistics.stdev(values) / statistics.mean(values)  # Coefficient of variation
                consistency = max(0.0, 1.0 - cv)
            else:
                consistency = 1.0
        else:
            consistency = 0.5
        quality_factors.append(("consistency", consistency, 0.3))
        
        # Calculate weighted quality score
        total_weighted_score = sum(score * weight for _, score, weight in quality_factors)
        return round(total_weighted_score, 3)
    
    def _calculate_confidence_interval(
        self,
        metrics: List[PlatformMetric],
        aggregated_value: float
    ) -> Tuple[float, float]:
        """Calculate confidence interval for aggregated value."""
        
        if len(metrics) < 2:
            return (aggregated_value * 0.9, aggregated_value * 1.1)
        
        values = [metric.value for metric in metrics]
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # 95% confidence interval
        margin_of_error = 1.96 * (std_dev / math.sqrt(len(values)))
        lower_bound = max(0, mean_value - margin_of_error)
        upper_bound = mean_value + margin_of_error
        
        return (round(lower_bound, 2), round(upper_bound, 2))
    
    def _determine_trend_direction(
        self,
        metric_type: MetricType,
        current_value: float,
        period: AggregationPeriod
    ) -> str:
        """Determine trend direction by comparing with previous period."""
        
        # Find previous period's aggregation
        previous_aggregations = [
            agg for agg in self.aggregated_metrics
            if (agg.metric_type == metric_type and
                agg.period == period and
                agg.end_time < datetime.now() - self._get_period_duration(period))
        ]
        
        if not previous_aggregations:
            return "stable"
        
        # Get most recent previous aggregation
        previous_agg = max(previous_aggregations, key=lambda x: x.end_time)
        previous_value = previous_agg.total_value
        
        if previous_value == 0:
            return "stable"
        
        change_rate = (current_value - previous_value) / previous_value
        
        if change_rate > 0.05:  # 5% increase
            return "increasing"
        elif change_rate < -0.05:  # 5% decrease
            return "decreasing"
        else:
            return "stable"
    
    def _get_period_duration(self, period: AggregationPeriod) -> timedelta:
        """Get duration for aggregation period."""
        
        duration_map = {
            AggregationPeriod.HOURLY: timedelta(hours=1),
            AggregationPeriod.DAILY: timedelta(days=1),
            AggregationPeriod.WEEKLY: timedelta(weeks=1),
            AggregationPeriod.MONTHLY: timedelta(days=30),
            AggregationPeriod.QUARTERLY: timedelta(days=90),
            AggregationPeriod.YEARLY: timedelta(days=365)
        }
        
        return duration_map.get(period, timedelta(hours=1))
    
    def _perform_periodic_aggregation(self, period -> None: AggregationPeriod) -> None:
        """Perform periodic aggregation for all metric types."""
        
        # Aggregate each metric type
        for metric_type in MetricType:
            try:
                self.aggregate_metrics(metric_type, period)
            except Exception as e:
                logger.error(f"Failed to aggregate {metric_type.value}: {e}")
        
        # Generate cross-platform insights
        self._generate_cross_platform_insights()
        
        # Update platform performance analysis
        self._update_platform_performances()
        
        # Update correlations
        self._update_correlation_matrix()
    
    def _generate_cross_platform_insights(self) -> None:
        """Generate insights from cross-platform data analysis."""
        
        # Analyze recent aggregations
        recent_aggregations = [
            agg for agg in self.aggregated_metrics
            if (datetime.now() - agg.created_at).hours <= 24
        ]
        
        if len(recent_aggregations) < 3:
            return
        
        # Find interesting patterns
        insights = []
        
        # Top performing platforms
        platform_performance = self._analyze_platform_performance(recent_aggregations)
        if platform_performance:
            insights.append(self._create_performance_insight(platform_performance))
        
        # Cross-platform correlations
        correlation_insights = self._analyze_cross_platform_correlations(recent_aggregations)
        insights.extend(correlation_insights)
        
        # Growth opportunities
        growth_insights = self._identify_growth_opportunities(recent_aggregations)
        insights.extend(growth_insights)
        
        # Store insights
        self.cross_platform_insights.extend(insights)
        
        # Keep only recent insights
        cutoff_date = datetime.now() - timedelta(days=30)
        self.cross_platform_insights = [
            insight for insight in self.cross_platform_insights
            if insight.created_at > cutoff_date
        ]
    
    def _analyze_platform_performance(self, aggregations: List[AggregatedMetric]) -> Optional[Dict[str, Any]]:
        """Analyze platform performance from aggregations."""
        
        platform_scores = defaultdict(list)
        
        for agg in aggregations:
            for platform, value in agg.platform_breakdown.items():
                # Normalize value by platform weight
                weight = self.aggregation_rules["default_weights"].get(platform, 0.1)
                normalized_score = value / weight if weight > 0 else value
                platform_scores[platform].append(normalized_score)
        
        if not platform_scores:
            return None
        
        # Calculate average performance per platform
        platform_averages = {
            platform: statistics.mean(scores)
            for platform, scores in platform_scores.items()
        }
        
        # Find top performer
        top_platform = max(platform_averages.items(), key=lambda x: x[1])
        
        return {
            "top_platform": top_platform[0],
            "top_score": top_platform[1],
            "platform_rankings": sorted(platform_averages.items(), key=lambda x: x[1], reverse=True)
        }
    
    def _create_performance_insight(self, performance_data: Dict[str, Any]) -> CrossPlatformInsight:
        """Create insight from platform performance analysis."""
        
        top_platform = performance_data["top_platform"]
        top_score = performance_data["top_score"]
        
        return CrossPlatformInsight(
            insight_id=f"insight_{uuid.uuid4().hex[:8]}",
            title=f"{top_platform.value.title()} Leading Platform Performance",
            description=f"{top_platform.value.title()} shows strongest performance with score of {top_score:.2f}",
            insight_type="platform_performance",
            platforms_involved=[top_platform],
            metrics_analyzed=[MetricType.ENGAGEMENT, MetricType.REACH],
            key_findings=[
                f"{top_platform.value.title()} outperforming other platforms",
                f"Performance score: {top_score:.2f}",
                "Opportunity to scale successful strategies"
            ],
            recommendations=[
                f"Allocate more resources to {top_platform.value}",
                "Analyze successful content strategies on this platform",
                "Cross-pollinate successful tactics to other platforms"
            ],
            confidence_score=0.85,
            impact_score=0.7
        )
    
    def _analyze_cross_platform_correlations(self, aggregations: List[AggregatedMetric]) -> List[CrossPlatformInsight]:
        """Analyze correlations between platforms."""
        
        insights = []
        
        # Group aggregations by metric type
        metric_aggregations = defaultdict(list)
        for agg in aggregations:
            metric_aggregations[agg.metric_type].append(agg)
        
        # Look for strong correlations
        for metric_type, aggs in metric_aggregations.items():
            if len(aggs) < 3:
                continue
            
            correlations = self._calculate_platform_correlations(aggs)
            strong_correlations = [
                (platform1, platform2, corr) for (platform1, platform2), corr in correlations.items()
                if abs(corr) > 0.7
            ]
            
            for platform1, platform2, correlation in strong_correlations:
                insight = CrossPlatformInsight(
                    insight_id=f"insight_{uuid.uuid4().hex[:8]}",
                    title=f"Strong Correlation: {platform1.value.title()} and {platform2.value.title()}",
                    description=f"Strong {correlation:.2f} correlation detected between platforms for {metric_type.value}",
                    insight_type="platform_correlation",
                    platforms_involved=[platform1, platform2],
                    metrics_analyzed=[metric_type],
                    key_findings=[
                        f"Correlation coefficient: {correlation:.2f}",
                        "Performance patterns move together",
                        "Shared audience or content strategy impact"
                    ],
                    recommendations=[
                        "Coordinate content strategy across correlated platforms",
                        "Time content releases for maximum cross-platform impact",
                        "Leverage success on one platform to boost the other"
                    ],
                    confidence_score=0.8,
                    impact_score=0.65
                )
                insights.append(insight)
        
        return insights[:3]  # Return top 3 correlation insights
    
    def _calculate_platform_correlations(self, aggregations: List[AggregatedMetric]) -> Dict[Tuple[Platform, Platform], float]:
        """Calculate correlations between platform performances."""
        
        platform_values = defaultdict(list)
        
        # Collect values for each platform
        for agg in aggregations:
            for platform, value in agg.platform_breakdown.items():
                platform_values[platform].append(value)
        
        correlations = {}
        platforms = list(platform_values.keys())
        
        # Calculate pairwise correlations
        for i, platform1 in enumerate(platforms):
            for platform2 in platforms[i+1:]:
                values1 = platform_values[platform1]
                values2 = platform_values[platform2]
                
                if len(values1) >= 3 and len(values2) >= 3:
                    correlation = self._calculate_correlation(values1, values2)
                    correlations[(platform1, platform2)] = correlation
        
        return correlations
    
    def _calculate_correlation(self, values1: List[float], values2: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        
        if len(values1) != len(values2) or len(values1) < 2:
            return 0.0
        
        mean1 = statistics.mean(values1)
        mean2 = statistics.mean(values2)
        
        numerator = sum((x - mean1) * (y - mean2) for x, y in zip(values1, values2))
        
        sum_sq1 = sum((x - mean1) ** 2 for x in values1)
        sum_sq2 = sum((y - mean2) ** 2 for y in values2)
        
        denominator = math.sqrt(sum_sq1 * sum_sq2)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _identify_growth_opportunities(self, aggregations: List[AggregatedMetric]) -> List[CrossPlatformInsight]:
        """Identify growth opportunities from aggregated data."""
        
        insights = []
        
        # Look for platforms with declining trends
        declining_platforms = []
        growing_platforms = []
        
        for agg in aggregations:
            if agg.trend_direction == "decreasing":
                declining_platforms.extend(agg.platform_breakdown.keys())
            elif agg.trend_direction == "increasing":
                growing_platforms.extend(agg.platform_breakdown.keys())
        
        # Find consistently declining platforms
        platform_decline_count = defaultdict(int)
        for platform in declining_platforms:
            platform_decline_count[platform] += 1
        
        # Create insights for platforms that need attention
        for platform, decline_count in platform_decline_count.items():
            if decline_count >= 2:  # Declining in multiple metrics
                insight = CrossPlatformInsight(
                    insight_id=f"insight_{uuid.uuid4().hex[:8]}",
                    title=f"Growth Opportunity: {platform.value.title()} Performance Decline",
                    description=f"{platform.value.title()} showing declining trends across multiple metrics",
                    insight_type="growth_opportunity",
                    platforms_involved=[platform],
                    metrics_analyzed=[MetricType.ENGAGEMENT, MetricType.REACH],
                    key_findings=[
                        f"Declining trends detected across {decline_count} metrics",
                        "Potential for performance recovery",
                        "May benefit from strategy adjustment"
                    ],
                    recommendations=[
                        f"Review and refresh {platform.value} content strategy",
                        "Analyze competitor performance on this platform",
                        "Consider increasing engagement initiatives",
                        "Test new content formats and timing"
                    ],
                    confidence_score=0.75,
                    impact_score=0.8
                )
                insights.append(insight)
        
        return insights[:2]  # Return top 2 growth opportunity insights
    
    def _update_platform_performances(self) -> None:
        """Update platform performance analysis."""
        
        for platform in Platform:
            performance = self._analyze_individual_platform_performance(platform)
            if performance:
                self.platform_performances[platform] = performance
    
    def _analyze_individual_platform_performance(self, platform: Platform) -> Optional[PlatformPerformance]:
        """Analyze performance for an individual platform."""
        
        # Get recent metrics for this platform
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_metrics = [
            metric for metric in self.platform_metrics[platform]
            if metric.timestamp > recent_cutoff
        ]
        
        if len(recent_metrics) < 5:  # Need minimum data
            return None
        
        # Calculate performance metrics
        performance_score = self._calculate_platform_performance_score(recent_metrics)
        growth_rate = self._calculate_platform_growth_rate(platform)
        engagement_rate = self._calculate_platform_engagement_rate(recent_metrics)
        reach_efficiency = self._calculate_reach_efficiency(recent_metrics)
        content_performance = self._analyze_content_performance(recent_metrics)
        audience_quality = self._assess_audience_quality(recent_metrics)
        monetization_potential = self._assess_monetization_potential(platform, recent_metrics)
        competitive_position = self._assess_competitive_position(platform)
        optimization_opportunities = self._identify_platform_optimization_opportunities(platform, recent_metrics)
        
        return PlatformPerformance(
            platform=platform,
            performance_score=performance_score,
            growth_rate=growth_rate,
            engagement_rate=engagement_rate,
            reach_efficiency=reach_efficiency,
            content_performance=content_performance,
            audience_quality=audience_quality,
            monetization_potential=monetization_potential,
            competitive_position=competitive_position,
            optimization_opportunities=optimization_opportunities
        )
    
    def _calculate_platform_performance_score(self, metrics: List[PlatformMetric]) -> float:
        """Calculate overall performance score for a platform."""
        
        if not metrics:
            return 0.0
        
        # Weight different metrics
        metric_weights = {
            MetricType.ENGAGEMENT: 0.3,
            MetricType.REACH: 0.25,
            MetricType.REVENUE: 0.2,
            MetricType.VIEWS: 0.15,
            MetricType.FOLLOWERS: 0.1
        }
        
        metric_scores = defaultdict(list)
        for metric in metrics:
            metric_scores[metric.metric_type].append(metric.value)
        
        weighted_scores = []
        for metric_type, weight in metric_weights.items():
            if metric_type in metric_scores:
                avg_value = statistics.mean(metric_scores[metric_type])
                # Normalize score (simplified normalization)
                normalized_score = min(1.0, avg_value / 1000)  # Adjust based on metric type
                weighted_scores.append(normalized_score * weight)
        
        return sum(weighted_scores) if weighted_scores else 0.5
    
    def _calculate_platform_growth_rate(self, platform: Platform) -> float:
        """Calculate growth rate for a platform."""
        
        # Compare recent week to previous week
        now = datetime.now()
        recent_week_start = now - timedelta(days=7)
        previous_week_start = now - timedelta(days=14)
        
        recent_metrics = [
            metric for metric in self.platform_metrics[platform]
            if recent_week_start <= metric.timestamp <= now
        ]
        
        previous_metrics = [
            metric for metric in self.platform_metrics[platform]
            if previous_week_start <= metric.timestamp <= recent_week_start
        ]
        
        if not recent_metrics or not previous_metrics:
            return 0.0
        
        recent_total = sum(metric.value for metric in recent_metrics)
        previous_total = sum(metric.value for metric in previous_metrics)
        
        if previous_total == 0:
            return 0.0
        
        growth_rate = (recent_total - previous_total) / previous_total
        return round(growth_rate, 3)
    
    def _calculate_platform_engagement_rate(self, metrics: List[PlatformMetric]) -> float:
        """Calculate engagement rate for a platform."""
        
        engagement_metrics = [m for m in metrics if m.metric_type == MetricType.ENGAGEMENT]
        if not engagement_metrics:
            return 0.5  # Default engagement rate
        
        return statistics.mean([m.value for m in engagement_metrics]) / 100  # Normalize to 0-1
    
    def _calculate_reach_efficiency(self, metrics: List[PlatformMetric]) -> float:
        """Calculate reach efficiency (engagement per reach)."""
        
        reach_metrics = [m for m in metrics if m.metric_type == MetricType.REACH]
        engagement_metrics = [m for m in metrics if m.metric_type == MetricType.ENGAGEMENT]
        
        if not reach_metrics or not engagement_metrics:
            return 0.5
        
        total_reach = sum(m.value for m in reach_metrics)
        total_engagement = sum(m.value for m in engagement_metrics)
        
        if total_reach == 0:
            return 0.0
        
        efficiency = total_engagement / total_reach
        return min(1.0, efficiency * 10)  # Normalize and cap at 1.0
    
    def _analyze_content_performance(self, metrics: List[PlatformMetric]) -> Dict[str, float]:
        """Analyze content performance patterns."""
        
        # Group metrics by content
        content_performance = defaultdict(list)
        for metric in metrics:
            if metric.content_id:
                content_performance[metric.content_id].append(metric.value)
        
        if not content_performance:
            return {"average_performance": 0.5}
        
        # Calculate performance statistics
        content_averages = {
            content_id: statistics.mean(values)
            for content_id, values in content_performance.items()
        }
        
        return {
            "average_performance": statistics.mean(content_averages.values()),
            "top_content_performance": max(content_averages.values()),
            "content_consistency": 1.0 - (statistics.stdev(content_averages.values()) / statistics.mean(content_averages.values()))
        }
    
    def _assess_audience_quality(self, metrics: List[PlatformMetric]) -> float:
        """Assess audience quality based on engagement patterns."""
        
        # Simplified audience quality assessment
        engagement_metrics = [m for m in metrics if m.metric_type == MetricType.ENGAGEMENT]
        
        if not engagement_metrics:
            return 0.6
        
        # Higher engagement generally indicates better audience quality
        avg_engagement = statistics.mean([m.value for m in engagement_metrics])
        
        # Normalize to 0-1 scale
        quality_score = min(1.0, avg_engagement / 100)
        return quality_score
    
    def _assess_monetization_potential(self, platform: Platform, metrics: List[PlatformMetric]) -> float:
        """Assess monetization potential for a platform."""
        
        # Platform-specific monetization potential
        platform_potential = {
            Platform.YOUTUBE: 0.9,
            Platform.INSTAGRAM: 0.8,
            Platform.TIKTOK: 0.7,
            Platform.TWITCH: 0.85,
            Platform.FACEBOOK: 0.75,
            Platform.SPOTIFY: 0.8,
            Platform.LINKEDIN: 0.6
        }
        
        base_potential = platform_potential.get(platform, 0.5)
        
        # Adjust based on audience size and engagement
        followers_metrics = [m for m in metrics if m.metric_type == MetricType.FOLLOWERS]
        engagement_metrics = [m for m in metrics if m.metric_type == MetricType.ENGAGEMENT]
        
        if followers_metrics and engagement_metrics:
            avg_followers = statistics.mean([m.value for m in followers_metrics])
            avg_engagement = statistics.mean([m.value for m in engagement_metrics])
            
            # Higher follower count and engagement increase monetization potential
            follower_factor = min(1.2, 1.0 + (avg_followers / 100000))  # Boost for large audiences
            engagement_factor = min(1.1, 1.0 + (avg_engagement / 1000))
            
            adjusted_potential = base_potential * follower_factor * engagement_factor
            return min(1.0, adjusted_potential)
        
        return base_potential
    
    def _assess_competitive_position(self, platform: Platform) -> str:
        """Assess competitive position on a platform."""
        
        # Simplified competitive position assessment
        performance = self.platform_performances.get(platform)
        
        if not performance:
            return "unknown"
        
        if hasattr(performance, 'performance_score'):
            score = performance.performance_score
        else:
            score = 0.5
        
        if score > 0.8:
            return "leading"
        elif score > 0.6:
            return "competitive"
        elif score > 0.4:
            return "developing"
        else:
            return "emerging"
    
    def _identify_platform_optimization_opportunities(
        self,
        platform: Platform,
        metrics: List[PlatformMetric]
    ) -> List[str]:
        """Identify optimization opportunities for a platform."""
        
        opportunities = []
        
        # Check engagement rate
        engagement_rate = self._calculate_platform_engagement_rate(metrics)
        if engagement_rate < 0.3:
            opportunities.append("Improve content engagement strategies")
        
        # Check growth rate
        growth_rate = self._calculate_platform_growth_rate(platform)
        if growth_rate < 0.05:
            opportunities.append("Accelerate audience growth initiatives")
        
        # Check reach efficiency
        reach_efficiency = self._calculate_reach_efficiency(metrics)
        if reach_efficiency < 0.4:
            opportunities.append("Optimize reach-to-engagement conversion")
        
        # Platform-specific opportunities
        platform_opportunities = {
            Platform.YOUTUBE: ["Optimize video SEO", "Improve thumbnail design", "Enhance video descriptions"],
            Platform.INSTAGRAM: ["Increase story engagement", "Optimize posting times", "Use relevant hashtags"],
            Platform.TIKTOK: ["Trend participation", "Sound optimization", "Cross-platform promotion"],
            Platform.TWITTER: ["Improve tweet timing", "Increase thread engagement", "Hashtag optimization"],
            Platform.LINKEDIN: ["Professional content focus", "Industry thought leadership", "Network building"]
        }
        
        platform_specific = platform_opportunities.get(platform, ["Content optimization", "Audience engagement"])
        opportunities.extend(platform_specific[:2])
        
        return opportunities[:5]
    
    def _update_correlation_matrix(self) -> None:
        """Update the correlation matrix between platforms."""
        
        # Get recent aggregations
        recent_aggregations = [
            agg for agg in self.aggregated_metrics
            if (datetime.now() - agg.created_at).days <= 7
        ]
        
        if len(recent_aggregations) < 5:
            return
        
        # Group by metric type
        metric_aggregations = defaultdict(list)
        for agg in recent_aggregations:
            metric_aggregations[agg.metric_type].append(agg)
        
        # Calculate correlations for each metric type
        for metric_type, aggs in metric_aggregations.items():
            correlations = self._calculate_platform_correlations(aggs)
            
            # Update correlation matrix
            for (platform1, platform2), correlation in correlations.items():
                self.correlation_matrix[platform1.value][platform2.value] = correlation
                self.correlation_matrix[platform2.value][platform1.value] = correlation
    
    def get_analytics_dashboard(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard."""
        
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        
        # Recent aggregations
        recent_aggregations = [
            agg for agg in self.aggregated_metrics
            if agg.created_at > cutoff_time
        ]
        
        # Platform status
        platform_status = {}
        for platform, connector in self.data_connectors.items():
            last_sync = connector.get("last_sync")
            status = connector.get("status", "inactive")
            
            platform_status[platform.value] = {
                "status": status,
                "last_sync": last_sync.isoformat() if last_sync else None,
                "data_freshness": self._calculate_data_freshness(platform),
                "metric_count": len(self.platform_metrics[platform])
            }
        
        # Performance summary
        performance_summary = {}
        for platform, performance in self.platform_performances.items():
            performance_summary[platform.value] = {
                "performance_score": round(performance.performance_score, 3),
                "growth_rate": round(performance.growth_rate, 3),
                "engagement_rate": round(performance.engagement_rate, 3),
                "competitive_position": performance.competitive_position
            }
        
        # Recent insights
        recent_insights = [
            {
                "title": insight.title,
                "insight_type": insight.insight_type,
                "platforms": [p.value for p in insight.platforms_involved],
                "confidence_score": insight.confidence_score,
                "created_at": insight.created_at.isoformat()
            }
            for insight in self.cross_platform_insights[-10:]
        ]
        
        return {
            "time_range_hours": time_range_hours,
            "overview": {
                "total_platforms": len(Platform),
                "active_platforms": len([p for p, s in platform_status.items() if s["status"] == "active"]),
                "total_aggregations": len(recent_aggregations),
                "total_insights": len(self.cross_platform_insights),
                "data_quality_score": self._calculate_overall_data_quality()
            },
            "platform_status": platform_status,
            "performance_summary": performance_summary,
            "recent_insights": recent_insights,
            "aggregation_summary": self._get_aggregation_summary(recent_aggregations),
            "correlation_highlights": self._get_correlation_highlights(),
            "optimization_opportunities": self._get_top_optimization_opportunities(),
            "dashboard_updated_at": datetime.now().isoformat()
        }
    
    def _calculate_data_freshness(self, platform: Platform) -> str:
        """Calculate data freshness for a platform."""
        
        last_sync = self.data_connectors[platform].get("last_sync")
        if not last_sync:
            return "no_data"
        
        hours_since_sync = (datetime.now() - last_sync).total_seconds() / 3600
        freshness_requirement = self._get_data_freshness_requirement(platform) / 60  # Convert to hours
        
        if hours_since_sync <= freshness_requirement:
            return "fresh"
        elif hours_since_sync <= freshness_requirement * 2:
            return "acceptable"
        else:
            return "stale"
    
    def _calculate_overall_data_quality(self) -> float:
        """Calculate overall data quality score."""
        
        if not self.aggregated_metrics:
            return 0.5
        
        recent_aggregations = [
            agg for agg in self.aggregated_metrics
            if (datetime.now() - agg.created_at).hours <= 24
        ]
        
        if not recent_aggregations:
            return 0.5
        
        quality_scores = [agg.data_quality_score for agg in recent_aggregations]
        return round(statistics.mean(quality_scores), 3)
    
    def _get_aggregation_summary(self, aggregations: List[AggregatedMetric]) -> Dict[str, Any]:
        """Get summary of recent aggregations."""
        
        if not aggregations:
            return {"message": "No recent aggregations"}
        
        # Group by metric type
        metric_totals = defaultdict(float)
        for agg in aggregations:
            metric_totals[agg.metric_type.value] += agg.total_value
        
        # Trend analysis
        trend_counts = defaultdict(int)
        for agg in aggregations:
            trend_counts[agg.trend_direction] += 1
        
        return {
            "total_aggregations": len(aggregations),
            "metric_totals": dict(metric_totals),
            "trend_distribution": dict(trend_counts),
            "average_quality_score": round(statistics.mean([agg.data_quality_score for agg in aggregations]), 3)
        }
    
    def _get_correlation_highlights(self) -> List[Dict[str, Any]]:
        """Get highlights from correlation matrix."""
        
        highlights = []
        
        for platform1, correlations in self.correlation_matrix.items():
            for platform2, correlation in correlations.items():
                if platform1 != platform2 and abs(correlation) > 0.7:
                    highlights.append({
                        "platform1": platform1,
                        "platform2": platform2,
                        "correlation": round(correlation, 3),
                        "strength": "strong" if abs(correlation) > 0.8 else "moderate"
                    })
        
        # Sort by correlation strength
        highlights.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        return highlights[:5]
    
    def _get_top_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Get top optimization opportunities across platforms."""
        
        opportunities = []
        
        for platform, performance in self.platform_performances.items():
            for opportunity in performance.optimization_opportunities:
                opportunities.append({
                    "platform": platform.value,
                    "opportunity": opportunity,
                    "performance_score": performance.performance_score,
                    "priority": "high" if performance.performance_score < 0.5 else "medium"
                })
        
        # Sort by performance score (lowest first)
        opportunities.sort(key=lambda x: x["performance_score"])
        return opportunities[:8]

# Initialize the global cross-platform analytics aggregator
cross_platform_analytics_aggregator = CrossPlatformAnalyticsAggregator()

def create_aggregator_config() -> Dict[str, Any]:
    """Create default configuration for analytics aggregator."""
    return {
        "supported_platforms": [platform.value for platform in Platform],
        "metric_types": [metric.value for metric in MetricType],
        "aggregation_periods": [period.value for period in AggregationPeriod],
        "data_connectors": cross_platform_analytics_aggregator.data_connectors,
        "aggregation_rules": cross_platform_analytics_aggregator.aggregation_rules,
        "real_time_processing": True,
        "correlation_tracking": True
    }

# Export main components
__all__ = [
    'CrossPlatformAnalyticsAggregator',
    'Platform',
    'MetricType',
    'AggregationPeriod',
    'PlatformMetric',
    'AggregatedMetric',
    'CrossPlatformInsight',
    'PlatformPerformance',
    'cross_platform_analytics_aggregator',
    'create_aggregator_config'
]