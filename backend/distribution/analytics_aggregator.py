"""Advanced Analytics Aggregator - Cross-Platform Analytics Intelligence System
===========================================================================

Sophisticated analytics aggregation system providing unified analytics collection,
real-time data processing, advanced insights generation, and comprehensive
performance tracking across multiple content distribution platforms.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/distribution/analytics_aggregator.py
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
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
from statistics import mean, median

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of analytics metrics."""
    VIEWS = "views"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    WATCH_TIME = "watch_time"
    REVENUE = "revenue"
    CONVERSION_RATE = "conversion_rate"
    CTR = "ctr"  # Click-through rate


class AggregationPeriod(str, Enum):
    """Aggregation time periods."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class AnalyticsDataPoint:
    """Individual analytics data point."""
    platform: str
    content_id: str
    metric_type: MetricType
    value: Union[int, float, Decimal]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for a time period."""
    period: AggregationPeriod
    start_time: datetime
    end_time: datetime
    platforms: List[str]
    metrics: Dict[MetricType, Union[int, float, Decimal]]
    growth_rates: Dict[MetricType, float] = field(default_factory=dict)
    comparisons: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceInsight:
    """Performance insight generated from analytics."""
    id: str
    title: str
    description: str
    insight_type: str
    confidence_score: float
    actionable_recommendations: List[str]
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)


class AnalyticsAggregator:
    """
    Advanced analytics aggregation system providing comprehensive
    cross-platform analytics intelligence and insights generation.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the analytics aggregator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.raw_data: List[AnalyticsDataPoint] = []
        self.aggregated_metrics: Dict[str, AggregatedMetrics] = {}
        self.insights: List[PerformanceInsight] = []
        
        self.logger.info("AnalyticsAggregator initialized")
    
    async def collect_platform_analytics(
        self,
        platform: str,
        content_id: str,
        metrics_data: Dict[str, Union[int, float]]
    ) -> bool:
        """Collect analytics data from a platform."""
        try:
            timestamp = datetime.utcnow()
            
            for metric_name, value in metrics_data.items():
                try:
                    metric_type = MetricType(metric_name.lower())
                    
                    data_point = AnalyticsDataPoint(
                        platform=platform,
                        content_id=content_id,
                        metric_type=metric_type,
                        value=value,
                        timestamp=timestamp
                    )
                    
                    self.raw_data.append(data_point)
                    
                except ValueError:
                    # Skip unknown metric types
                    self.logger.warning(f"Unknown metric type: {metric_name}")
                    continue
            
            self.logger.debug(f"📊 Collected analytics for {platform}:{content_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error collecting platform analytics: {e}")
            return False
    
    async def aggregate_metrics(
        self,
        period: AggregationPeriod,
        start_time: datetime,
        end_time: datetime,
        platforms: Optional[List[str]] = None,
        content_ids: Optional[List[str]] = None
    ) -> AggregatedMetrics:
        """Aggregate metrics for specified period and filters."""
        try:
            # Filter data points
            filtered_data = []
            for data_point in self.raw_data:
                # Time filter
                if not (start_time <= data_point.timestamp <= end_time):
                    continue
                
                # Platform filter
                if platforms and data_point.platform not in platforms:
                    continue
                
                # Content filter
                if content_ids and data_point.content_id not in content_ids:
                    continue
                
                filtered_data.append(data_point)
            
            # Group data by metric type
            metrics_by_type = {}
            platforms_used = set()
            
            for data_point in filtered_data:
                metric_type = data_point.metric_type
                platforms_used.add(data_point.platform)
                
                if metric_type not in metrics_by_type:
                    metrics_by_type[metric_type] = []
                
                metrics_by_type[metric_type].append(data_point.value)
            
            # Calculate aggregated values
            aggregated_values = {}
            for metric_type, values in metrics_by_type.items():
                if metric_type in [MetricType.ENGAGEMENT_RATE, MetricType.CONVERSION_RATE, MetricType.CTR]:
                    # Use average for rate metrics
                    aggregated_values[metric_type] = mean(values) if values else 0
                else:
                    # Use sum for count metrics
                    aggregated_values[metric_type] = sum(values)
            
            # Calculate growth rates
            growth_rates = await self._calculate_growth_rates(
                aggregated_values, period, start_time, platforms, content_ids
            )
            
            aggregated_metrics = AggregatedMetrics(
                period=period,
                start_time=start_time,
                end_time=end_time,
                platforms=list(platforms_used),
                metrics=aggregated_values,
                growth_rates=growth_rates
            )
            
            # Store aggregated metrics
            key = f"{period.value}_{start_time.isoformat()}_{end_time.isoformat()}"
            self.aggregated_metrics[key] = aggregated_metrics
            
            self.logger.info(f"📈 Metrics aggregated for {period.value} period")
            
            return aggregated_metrics
            
        except Exception as e:
            self.logger.error(f"Error aggregating metrics: {e}")
            return AggregatedMetrics(
                period=period,
                start_time=start_time,
                end_time=end_time,
                platforms=[],
                metrics={}
            )
    
    async def _calculate_growth_rates(
        self,
        current_metrics: Dict[MetricType, Union[int, float]],
        period: AggregationPeriod,
        current_start: datetime,
        platforms: Optional[List[str]],
        content_ids: Optional[List[str]]
    ) -> Dict[MetricType, float]:
        """Calculate growth rates compared to previous period."""
        try:
            growth_rates = {}
            
            # Calculate previous period
            period_delta = {
                AggregationPeriod.HOUR: timedelta(hours=1),
                AggregationPeriod.DAY: timedelta(days=1),
                AggregationPeriod.WEEK: timedelta(weeks=1),
                AggregationPeriod.MONTH: timedelta(days=30),
                AggregationPeriod.QUARTER: timedelta(days=90),
                AggregationPeriod.YEAR: timedelta(days=365)
            }
            
            delta = period_delta.get(period, timedelta(days=1))
            prev_start = current_start - delta
            prev_end = current_start
            
            # Get previous period metrics
            prev_metrics = await self.aggregate_metrics(
                period, prev_start, prev_end, platforms, content_ids
            )
            
            # Calculate growth rates
            for metric_type, current_value in current_metrics.items():
                prev_value = prev_metrics.metrics.get(metric_type, 0)
                
                if prev_value > 0:
                    growth_rate = ((current_value - prev_value) / prev_value) * 100
                    growth_rates[metric_type] = growth_rate
                elif current_value > 0:
                    growth_rates[metric_type] = 100.0  # New metric
                else:
                    growth_rates[metric_type] = 0.0
            
            return growth_rates
            
        except Exception as e:
            self.logger.error(f"Error calculating growth rates: {e}")
            return {}
    
    async def generate_insights(
        self,
        aggregated_metrics: AggregatedMetrics,
        comparison_periods: Optional[List[AggregatedMetrics]] = None
    ) -> List[PerformanceInsight]:
        """Generate performance insights from aggregated metrics."""
        try:
            insights = []
            
            # Performance trend insights
            insights.extend(await self._analyze_performance_trends(aggregated_metrics))
            
            # Platform comparison insights
            insights.extend(await self._analyze_platform_performance(aggregated_metrics))
            
            # Engagement insights
            insights.extend(await self._analyze_engagement_patterns(aggregated_metrics))
            
            # Growth insights
            insights.extend(await self._analyze_growth_patterns(aggregated_metrics))
            
            # Optimization recommendations
            insights.extend(await self._generate_optimization_recommendations(aggregated_metrics))
            
            # Store insights
            self.insights.extend(insights)
            
            self.logger.info(f"🧠 Generated {len(insights)} performance insights")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return []
    
    async def _analyze_performance_trends(
        self,
        metrics: AggregatedMetrics
    ) -> List[PerformanceInsight]:
        """Analyze performance trends."""
        insights = []
        
        try:
            # High engagement rate insight
            engagement_rate = metrics.metrics.get(MetricType.ENGAGEMENT_RATE, 0)
            if engagement_rate > 0.05:  # 5% threshold
                insights.append(PerformanceInsight(
                    id=str(uuid4()),
                    title="High Engagement Performance",
                    description=f"Excellent engagement rate of {engagement_rate:.2%} achieved",
                    insight_type="positive_trend",
                    confidence_score=0.9,
                    actionable_recommendations=[
                        "Continue with similar content strategy",
                        "Analyze successful content elements for replication",
                        "Consider increasing posting frequency"
                    ],
                    supporting_data={"engagement_rate": engagement_rate}
                ))
            
            # Growth trend insight
            views_growth = metrics.growth_rates.get(MetricType.VIEWS, 0)
            if views_growth > 20:  # 20% growth
                insights.append(PerformanceInsight(
                    id=str(uuid4()),
                    title="Strong Growth Trend",
                    description=f"Views increased by {views_growth:.1f}% compared to previous period",
                    insight_type="growth",
                    confidence_score=0.8,
                    actionable_recommendations=[
                        "Maintain current content quality and schedule",
                        "Expand to similar content themes",
                        "Consider cross-platform promotion"
                    ],
                    supporting_data={"views_growth": views_growth}
                ))
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance trends: {e}")
        
        return insights
    
    async def _analyze_platform_performance(
        self,
        metrics: AggregatedMetrics
    ) -> List[PerformanceInsight]:
        """Analyze platform-specific performance."""
        insights = []
        
        try:
            # Platform comparison would require platform-specific data
            # This is a simplified version
            if len(metrics.platforms) > 1:
                insights.append(PerformanceInsight(
                    id=str(uuid4()),
                    title="Multi-Platform Distribution",
                    description=f"Content distributed across {len(metrics.platforms)} platforms",
                    insight_type="platform_analysis",
                    confidence_score=0.7,
                    actionable_recommendations=[
                        "Analyze performance differences between platforms",
                        "Optimize content for each platform's audience",
                        "Consider platform-specific posting schedules"
                    ],
                    supporting_data={"platform_count": len(metrics.platforms)}
                ))
            
        except Exception as e:
            self.logger.error(f"Error analyzing platform performance: {e}")
        
        return insights
    
    async def _analyze_engagement_patterns(
        self,
        metrics: AggregatedMetrics
    ) -> List[PerformanceInsight]:
        """Analyze engagement patterns."""
        insights = []
        
        try:
            views = metrics.metrics.get(MetricType.VIEWS, 0)
            likes = metrics.metrics.get(MetricType.LIKES, 0)
            comments = metrics.metrics.get(MetricType.COMMENTS, 0)
            
            # Comment to like ratio
            if likes > 0 and comments > 0:
                comment_like_ratio = comments / likes
                if comment_like_ratio > 0.1:  # High comment engagement
                    insights.append(PerformanceInsight(
                        id=str(uuid4()),
                        title="High Comment Engagement",
                        description=f"Strong comment engagement with {comment_like_ratio:.2%} comment-to-like ratio",
                        insight_type="engagement_pattern",
                        confidence_score=0.8,
                        actionable_recommendations=[
                            "Respond to comments to maintain engagement",
                            "Create content that encourages discussion",
                            "Use call-to-action prompts for comments"
                        ],
                        supporting_data={"comment_like_ratio": comment_like_ratio}
                    ))
            
        except Exception as e:
            self.logger.error(f"Error analyzing engagement patterns: {e}")
        
        return insights
    
    async def _analyze_growth_patterns(
        self,
        metrics: AggregatedMetrics
    ) -> List[PerformanceInsight]:
        """Analyze growth patterns."""
        insights = []
        
        try:
            # Identify declining metrics
            declining_metrics = []
            for metric_type, growth_rate in metrics.growth_rates.items():
                if growth_rate < -10:  # Declining by more than 10%
                    declining_metrics.append((metric_type, growth_rate))
            
            if declining_metrics:
                insights.append(PerformanceInsight(
                    id=str(uuid4()),
                    title="Performance Decline Alert",
                    description=f"Declining trends detected in {len(declining_metrics)} metrics",
                    insight_type="decline_alert",
                    confidence_score=0.9,
                    actionable_recommendations=[
                        "Review recent content changes",
                        "Analyze competitor performance",
                        "Consider refreshing content strategy",
                        "Check posting schedule consistency"
                    ],
                    supporting_data={"declining_metrics": declining_metrics}
                ))
            
        except Exception as e:
            self.logger.error(f"Error analyzing growth patterns: {e}")
        
        return insights
    
    async def _generate_optimization_recommendations(
        self,
        metrics: AggregatedMetrics
    ) -> List[PerformanceInsight]:
        """Generate optimization recommendations."""
        insights = []
        
        try:
            views = metrics.metrics.get(MetricType.VIEWS, 0)
            engagement_rate = metrics.metrics.get(MetricType.ENGAGEMENT_RATE, 0)
            
            # Low engagement with high views
            if views > 1000 and engagement_rate < 0.02:
                insights.append(PerformanceInsight(
                    id=str(uuid4()),
                    title="Engagement Optimization Opportunity",
                    description="High views but low engagement rate indicates optimization potential",
                    insight_type="optimization",
                    confidence_score=0.8,
                    actionable_recommendations=[
                        "Improve call-to-action elements",
                        "Create more interactive content",
                        "Optimize content for target audience",
                        "A/B test different content formats"
                    ],
                    supporting_data={
                        "views": views,
                        "engagement_rate": engagement_rate
                    }
                ))
            
        except Exception as e:
            self.logger.error(f"Error generating optimization recommendations: {e}")
        
        return insights
    
    async def get_real_time_metrics(
        self,
        platforms: Optional[List[str]] = None,
        content_ids: Optional[List[str]] = None,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Get real-time metrics for the specified time window."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            # Get recent data
            recent_metrics = await self.aggregate_metrics(
                AggregationPeriod.HOUR,
                start_time,
                end_time,
                platforms,
                content_ids
            )
            
            # Calculate real-time stats
            real_time_data = {
                "timestamp": end_time.isoformat(),
                "time_window_hours": time_window_hours,
                "platforms": recent_metrics.platforms,
                "total_views": recent_metrics.metrics.get(MetricType.VIEWS, 0),
                "total_engagement": (
                    recent_metrics.metrics.get(MetricType.LIKES, 0) +
                    recent_metrics.metrics.get(MetricType.COMMENTS, 0) +
                    recent_metrics.metrics.get(MetricType.SHARES, 0)
                ),
                "engagement_rate": recent_metrics.metrics.get(MetricType.ENGAGEMENT_RATE, 0),
                "growth_rates": recent_metrics.growth_rates,
                "top_performing_metrics": self._get_top_performing_metrics(recent_metrics)
            }
            
            return real_time_data
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            return {}
    
    def _get_top_performing_metrics(self, metrics: AggregatedMetrics) -> List[Dict[str, Any]]:
        """Get top performing metrics."""
        try:
            metric_performance = []
            
            for metric_type, value in metrics.metrics.items():
                growth_rate = metrics.growth_rates.get(metric_type, 0)
                
                metric_performance.append({
                    "metric": metric_type.value,
                    "value": value,
                    "growth_rate": growth_rate,
                    "performance_score": value * (1 + growth_rate / 100)
                })
            
            # Sort by performance score
            metric_performance.sort(key=lambda x: x["performance_score"], reverse=True)
            
            return metric_performance[:5]  # Top 5
            
        except Exception as e:
            self.logger.error(f"Error getting top performing metrics: {e}")
            return []
    
    async def export_analytics_report(
        self,
        start_time: datetime,
        end_time: datetime,
        platforms: Optional[List[str]] = None,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """Export comprehensive analytics report."""
        try:
            # Aggregate metrics for the period
            weekly_metrics = await self.aggregate_metrics(
                AggregationPeriod.WEEK,
                start_time,
                end_time,
                platforms
            )
            
            # Generate insights
            insights = await self.generate_insights(weekly_metrics)
            
            # Compile report
            report = {
                "report_id": str(uuid4()),
                "generated_at": datetime.utcnow().isoformat(),
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "platforms": platforms or weekly_metrics.platforms,
                "summary": {
                    "total_views": weekly_metrics.metrics.get(MetricType.VIEWS, 0),
                    "total_engagement": (
                        weekly_metrics.metrics.get(MetricType.LIKES, 0) +
                        weekly_metrics.metrics.get(MetricType.COMMENTS, 0) +
                        weekly_metrics.metrics.get(MetricType.SHARES, 0)
                    ),
                    "average_engagement_rate": weekly_metrics.metrics.get(MetricType.ENGAGEMENT_RATE, 0),
                    "total_reach": weekly_metrics.metrics.get(MetricType.REACH, 0)
                },
                "detailed_metrics": weekly_metrics.metrics,
                "growth_rates": weekly_metrics.growth_rates,
                "insights": [
                    {
                        "title": insight.title,
                        "description": insight.description,
                        "type": insight.insight_type,
                        "confidence": insight.confidence_score,
                        "recommendations": insight.actionable_recommendations
                    }
                    for insight in insights
                ],
                "recommendations": self._compile_recommendations(insights)
            }
            
            self.logger.info(f"📊 Analytics report exported for {start_time} to {end_time}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error exporting analytics report: {e}")
            return {}
    
    def _compile_recommendations(self, insights: List[PerformanceInsight]) -> List[str]:
        """Compile top recommendations from insights."""
        try:
            all_recommendations = []
            for insight in insights:
                all_recommendations.extend(insight.actionable_recommendations)
            
            # Remove duplicates while preserving order
            unique_recommendations = []
            seen = set()
            for rec in all_recommendations:
                if rec not in seen:
                    unique_recommendations.append(rec)
                    seen.add(rec)
            
            return unique_recommendations[:10]  # Top 10 recommendations
            
        except Exception as e:
            self.logger.error(f"Error compiling recommendations: {e}")
            return []


# Global analytics aggregator instance
_analytics_aggregator: Optional[AnalyticsAggregator] = None


async def get_analytics_aggregator() -> AnalyticsAggregator:
    """Get global analytics aggregator instance."""
    global _analytics_aggregator
    
    if _analytics_aggregator is None:
        _analytics_aggregator = AnalyticsAggregator()
    
    return _analytics_aggregator