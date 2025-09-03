"""Analytics Aggregator

Unified multi-platform analytics system that aggregates data from all connected
platforms and provides comprehensive cross-platform insights and reporting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import numpy as np
from collections import defaultdict

from .platform_connectors import SocialPlatform

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    VIEWS = "views"
    REVENUE = "revenue"
    CONVERSION = "conversion"


class TimeGranularity(Enum):
    """Time granularity for analytics"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class PlatformAnalytics:
    """Analytics data for a specific platform"""
    platform: SocialPlatform
    content_id: str
    timestamp: datetime
    
    # Core metrics
    views: int = 0
    impressions: int = 0
    reach: int = 0
    engagement_rate: float = 0.0
    
    # Interaction metrics
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    
    # Performance metrics
    completion_rate: float = 0.0
    bounce_rate: float = 0.0
    average_watch_time: float = 0.0
    
    # Revenue metrics
    revenue: float = 0.0
    cpm: float = 0.0  # Cost per mille
    cpc: float = 0.0  # Cost per click
    
    # Audience metrics
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, Any] = field(default_factory=dict)
    device_breakdown: Dict[str, int] = field(default_factory=dict)
    
    # Additional platform-specific metrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedMetrics:
    """Unified metrics across all platforms"""
    period_start: datetime
    period_end: datetime
    total_platforms: int
    
    # Aggregated core metrics
    total_views: int = 0
    total_impressions: int = 0
    total_reach: int = 0
    average_engagement_rate: float = 0.0
    
    # Aggregated interaction metrics
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_saves: int = 0
    total_clicks: int = 0
    
    # Performance aggregates
    average_completion_rate: float = 0.0
    average_watch_time: float = 0.0
    
    # Revenue aggregates
    total_revenue: float = 0.0
    average_cpm: float = 0.0
    average_cpc: float = 0.0
    
    # Cross-platform insights
    best_performing_platform: Optional[SocialPlatform] = None
    platform_performance_ranking: List[SocialPlatform] = field(default_factory=list)
    optimization_recommendations: List[str] = field(default_factory=list)


@dataclass
class CrossPlatformInsights:
    """Advanced cross-platform analytics insights"""
    content_id: str
    analysis_period: Dict[str, datetime]
    
    # Platform comparison
    platform_metrics: Dict[SocialPlatform, PlatformAnalytics] = field(default_factory=dict)
    platform_rankings: Dict[MetricType, List[SocialPlatform]] = field(default_factory=dict)
    
    # Trend analysis
    growth_trends: Dict[MetricType, Dict[SocialPlatform, float]] = field(default_factory=dict)
    seasonality_patterns: Dict[SocialPlatform, Dict[str, Any]] = field(default_factory=dict)
    
    # Audience analysis
    cross_platform_audience_overlap: Dict[str, float] = field(default_factory=dict)
    unique_audience_size: int = 0
    audience_migration_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Content performance
    optimal_posting_times: Dict[SocialPlatform, List[int]] = field(default_factory=dict)
    content_format_performance: Dict[str, Dict[SocialPlatform, float]] = field(default_factory=dict)
    hashtag_performance: Dict[str, Dict[SocialPlatform, float]] = field(default_factory=dict)
    
    # ROI analysis
    platform_roi: Dict[SocialPlatform, float] = field(default_factory=dict)
    cost_per_engagement: Dict[SocialPlatform, float] = field(default_factory=dict)
    revenue_attribution: Dict[SocialPlatform, float] = field(default_factory=dict)


class AnalyticsAggregator:
    """Unified multi-platform analytics aggregation system"""
    
    def __init__(self):
        self.platform_data: Dict[str, List[PlatformAnalytics]] = defaultdict(list)
        self.unified_cache: Dict[str, UnifiedMetrics] = {}
        self.insights_cache: Dict[str, CrossPlatformInsights] = {}
        self.benchmark_data: Dict[SocialPlatform, Dict[str, float]] = {}
        
        # Initialize benchmark data
        self._initialize_benchmarks()
    
    def _initialize_benchmarks(self):
        """Initialize industry benchmark data"""
        self.benchmark_data = {
            SocialPlatform.YOUTUBE: {
                "engagement_rate": 0.04,  # 4%
                "completion_rate": 0.41,  # 41%
                "cpm": 2.50,
                "cpc": 0.84
            },
            SocialPlatform.TIKTOK: {
                "engagement_rate": 0.055,  # 5.5%
                "completion_rate": 0.82,   # 82%
                "cpm": 1.20,
                "cpc": 0.45
            },
            SocialPlatform.INSTAGRAM: {
                "engagement_rate": 0.022,  # 2.2%
                "completion_rate": 0.65,   # 65%
                "cpm": 3.20,
                "cpc": 1.15
            },
            SocialPlatform.TWITTER: {
                "engagement_rate": 0.014,  # 1.4%
                "completion_rate": 0.35,   # 35%
                "cpm": 2.80,
                "cpc": 0.95
            },
            SocialPlatform.FACEBOOK: {
                "engagement_rate": 0.013,  # 1.3%
                "completion_rate": 0.55,   # 55%
                "cpm": 3.50,
                "cpc": 1.25
            },
            SocialPlatform.LINKEDIN: {
                "engagement_rate": 0.019,  # 1.9%
                "completion_rate": 0.48,   # 48%
                "cpm": 5.20,
                "cpc": 2.35
            }
        }
    
    async def add_platform_analytics(
        self,
        analytics: PlatformAnalytics
    ):
        """Add analytics data from a platform"""
        try:
            content_key = f"{analytics.platform.value}_{analytics.content_id}"
            self.platform_data[content_key].append(analytics)
            
            # Clear related caches
            self._invalidate_caches(analytics.content_id)
            
            logger.debug(f"Added analytics for {analytics.platform.value} content {analytics.content_id}")
        
        except Exception as e:
            logger.error(f"Failed to add platform analytics: {str(e)}")
    
    async def get_unified_metrics(
        self,
        content_id: str,
        platforms: List[SocialPlatform],
        period_start: datetime,
        period_end: datetime,
        use_cache: bool = True
    ) -> UnifiedMetrics:
        """Get unified metrics across specified platforms"""
        try:
            cache_key = f"{content_id}_{hash(tuple(platforms))}_{period_start}_{period_end}"
            
            if use_cache and cache_key in self.unified_cache:
                return self.unified_cache[cache_key]
            
            # Collect platform analytics for the period
            platform_analytics = {}
            
            for platform in platforms:
                content_key = f"{platform.value}_{content_id}"
                platform_data = self.platform_data.get(content_key, [])
                
                # Filter by time period
                filtered_data = [
                    data for data in platform_data
                    if period_start <= data.timestamp <= period_end
                ]
                
                if filtered_data:
                    # Aggregate data for this platform
                    platform_analytics[platform] = self._aggregate_platform_data(filtered_data)
            
            # Create unified metrics
            unified = await self._create_unified_metrics(
                platform_analytics, period_start, period_end
            )
            
            # Cache the result
            if use_cache:
                self.unified_cache[cache_key] = unified
            
            return unified
        
        except Exception as e:
            logger.error(f"Failed to get unified metrics: {str(e)}")
            return UnifiedMetrics(
                period_start=period_start,
                period_end=period_end,
                total_platforms=0
            )
    
    def _aggregate_platform_data(self, data_points: List[PlatformAnalytics]) -> PlatformAnalytics:
        """Aggregate multiple data points for a platform"""
        if not data_points:
            return PlatformAnalytics(
                platform=SocialPlatform.YOUTUBE,  # Default
                content_id="",
                timestamp=datetime.now()
            )
        
        # Use the latest data point as base
        aggregated = data_points[-1]
        
        # Sum cumulative metrics
        aggregated.views = sum(dp.views for dp in data_points)
        aggregated.impressions = sum(dp.impressions for dp in data_points)
        aggregated.reach = max(dp.reach for dp in data_points)  # Reach is not cumulative
        aggregated.likes = sum(dp.likes for dp in data_points)
        aggregated.comments = sum(dp.comments for dp in data_points)
        aggregated.shares = sum(dp.shares for dp in data_points)
        aggregated.saves = sum(dp.saves for dp in data_points)
        aggregated.clicks = sum(dp.clicks for dp in data_points)
        aggregated.revenue = sum(dp.revenue for dp in data_points)
        
        # Average rate-based metrics
        rate_metrics = ['engagement_rate', 'completion_rate', 'bounce_rate', 'average_watch_time', 'cpm', 'cpc']
        for metric in rate_metrics:
            values = [getattr(dp, metric) for dp in data_points if getattr(dp, metric) > 0]
            setattr(aggregated, metric, np.mean(values) if values else 0.0)
        
        return aggregated
    
    async def _create_unified_metrics(
        self,
        platform_analytics: Dict[SocialPlatform, PlatformAnalytics],
        period_start: datetime,
        period_end: datetime
    ) -> UnifiedMetrics:
        """Create unified metrics from platform analytics"""
        if not platform_analytics:
            return UnifiedMetrics(
                period_start=period_start,
                period_end=period_end,
                total_platforms=0
            )
        
        # Aggregate core metrics
        total_views = sum(analytics.views for analytics in platform_analytics.values())
        total_impressions = sum(analytics.impressions for analytics in platform_analytics.values())
        total_reach = sum(analytics.reach for analytics in platform_analytics.values())
        
        # Calculate weighted averages for rates
        engagement_rates = []
        completion_rates = []
        watch_times = []
        cpms = []
        cpcs = []
        
        for analytics in platform_analytics.values():
            if analytics.views > 0:  # Weight by views
                engagement_rates.extend([analytics.engagement_rate] * analytics.views)
                completion_rates.extend([analytics.completion_rate] * analytics.views)
                watch_times.extend([analytics.average_watch_time] * analytics.views)
            
            if analytics.impressions > 0:  # Weight by impressions for cost metrics
                cpms.extend([analytics.cpm] * analytics.impressions)
                cpcs.extend([analytics.cpc] * analytics.clicks)
        
        # Aggregate interaction metrics
        total_likes = sum(analytics.likes for analytics in platform_analytics.values())
        total_comments = sum(analytics.comments for analytics in platform_analytics.values())
        total_shares = sum(analytics.shares for analytics in platform_analytics.values())
        total_saves = sum(analytics.saves for analytics in platform_analytics.values())
        total_clicks = sum(analytics.clicks for analytics in platform_analytics.values())
        
        # Aggregate revenue
        total_revenue = sum(analytics.revenue for analytics in platform_analytics.values())
        
        # Determine best performing platform
        best_platform = self._determine_best_platform(platform_analytics)
        platform_ranking = self._rank_platforms_by_performance(platform_analytics)
        
        # Generate optimization recommendations
        recommendations = await self._generate_optimization_recommendations(platform_analytics)
        
        return UnifiedMetrics(
            period_start=period_start,
            period_end=period_end,
            total_platforms=len(platform_analytics),
            total_views=total_views,
            total_impressions=total_impressions,
            total_reach=total_reach,
            average_engagement_rate=np.mean(engagement_rates) if engagement_rates else 0.0,
            total_likes=total_likes,
            total_comments=total_comments,
            total_shares=total_shares,
            total_saves=total_saves,
            total_clicks=total_clicks,
            average_completion_rate=np.mean(completion_rates) if completion_rates else 0.0,
            average_watch_time=np.mean(watch_times) if watch_times else 0.0,
            total_revenue=total_revenue,
            average_cpm=np.mean(cpms) if cpms else 0.0,
            average_cpc=np.mean(cpcs) if cpcs else 0.0,
            best_performing_platform=best_platform,
            platform_performance_ranking=platform_ranking,
            optimization_recommendations=recommendations
        )
    
    def _determine_best_platform(
        self,
        platform_analytics: Dict[SocialPlatform, PlatformAnalytics]
    ) -> Optional[SocialPlatform]:
        """Determine the best performing platform"""
        if not platform_analytics:
            return None
        
        # Score platforms based on multiple factors
        platform_scores = {}
        
        for platform, analytics in platform_analytics.items():
            score = 0.0
            
            # Engagement score (40%)
            benchmark = self.benchmark_data.get(platform, {})
            benchmark_engagement = benchmark.get("engagement_rate", 0.02)
            
            if benchmark_engagement > 0:
                engagement_score = (analytics.engagement_rate / benchmark_engagement) * 40
                score += min(engagement_score, 40)  # Cap at 40 points
            
            # Reach score (30%)
            if analytics.impressions > 0:
                reach_efficiency = analytics.reach / analytics.impressions
                score += reach_efficiency * 30
            
            # Revenue score (20%)
            if analytics.revenue > 0:
                score += min(analytics.revenue / 100, 20)  # $1 = 0.01 points, cap at 20
            
            # Completion rate score (10%)
            benchmark_completion = benchmark.get("completion_rate", 0.5)
            if benchmark_completion > 0:
                completion_score = (analytics.completion_rate / benchmark_completion) * 10
                score += min(completion_score, 10)
            
            platform_scores[platform] = score
        
        # Return platform with highest score
        return max(platform_scores.items(), key=lambda x: x[1])[0]
    
    def _rank_platforms_by_performance(
        self,
        platform_analytics: Dict[SocialPlatform, PlatformAnalytics]
    ) -> List[SocialPlatform]:
        """Rank platforms by overall performance"""
        platform_scores = {}
        
        for platform, analytics in platform_analytics.items():
            # Combined performance score
            score = (
                analytics.engagement_rate * 100 +
                analytics.completion_rate * 50 +
                (analytics.revenue / max(analytics.impressions, 1)) * 1000 +
                (analytics.reach / max(analytics.impressions, 1)) * 25
            )
            platform_scores[platform] = score
        
        # Sort by score descending
        return sorted(platform_scores.keys(), key=lambda x: platform_scores[x], reverse=True)
    
    async def _generate_optimization_recommendations(
        self,
        platform_analytics: Dict[SocialPlatform, PlatformAnalytics]
    ) -> List[str]:
        """Generate optimization recommendations based on performance"""
        recommendations = []
        
        for platform, analytics in platform_analytics.items():
            benchmark = self.benchmark_data.get(platform, {})
            
            # Engagement rate recommendation
            benchmark_engagement = benchmark.get("engagement_rate", 0.02)
            if analytics.engagement_rate < benchmark_engagement * 0.8:
                recommendations.append(
                    f"Improve {platform.value} engagement rate "
                    f"(current: {analytics.engagement_rate:.2%}, benchmark: {benchmark_engagement:.2%})"
                )
            
            # Completion rate recommendation
            benchmark_completion = benchmark.get("completion_rate", 0.5)
            if analytics.completion_rate < benchmark_completion * 0.8:
                recommendations.append(
                    f"Optimize {platform.value} content for higher completion rates "
                    f"(current: {analytics.completion_rate:.2%}, benchmark: {benchmark_completion:.2%})"
                )
            
            # Cost efficiency recommendation
            benchmark_cpm = benchmark.get("cpm", 3.0)
            if analytics.cpm > benchmark_cpm * 1.2:
                recommendations.append(
                    f"Reduce {platform.value} cost per thousand impressions "
                    f"(current: ${analytics.cpm:.2f}, benchmark: ${benchmark_cpm:.2f})"
                )
        
        # Cross-platform recommendations
        if len(platform_analytics) > 1:
            best_platform = self._determine_best_platform(platform_analytics)
            if best_platform:
                recommendations.append(
                    f"Consider allocating more budget to {best_platform.value} "
                    "based on superior performance metrics"
                )
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def get_cross_platform_insights(
        self,
        content_id: str,
        platforms: List[SocialPlatform],
        period_start: datetime,
        period_end: datetime,
        use_cache: bool = True
    ) -> CrossPlatformInsights:
        """Get advanced cross-platform insights"""
        try:
            cache_key = f"insights_{content_id}_{hash(tuple(platforms))}_{period_start}_{period_end}"
            
            if use_cache and cache_key in self.insights_cache:
                return self.insights_cache[cache_key]
            
            # Collect platform metrics
            platform_metrics = {}
            
            for platform in platforms:
                content_key = f"{platform.value}_{content_id}"
                platform_data = self.platform_data.get(content_key, [])
                
                filtered_data = [
                    data for data in platform_data
                    if period_start <= data.timestamp <= period_end
                ]
                
                if filtered_data:
                    platform_metrics[platform] = self._aggregate_platform_data(filtered_data)
            
            # Generate platform rankings for each metric type
            platform_rankings = {}
            for metric_type in MetricType:
                rankings = self._rank_platforms_by_metric(platform_metrics, metric_type)
                platform_rankings[metric_type] = rankings
            
            # Calculate growth trends
            growth_trends = await self._calculate_growth_trends(
                content_id, platforms, period_start, period_end
            )
            
            # Analyze seasonality patterns
            seasonality_patterns = await self._analyze_seasonality_patterns(
                content_id, platforms, period_start, period_end
            )
            
            # Calculate audience overlap and migration
            audience_overlap = await self._calculate_audience_overlap(platform_metrics)
            unique_audience_size = await self._estimate_unique_audience_size(platform_metrics)
            migration_patterns = await self._analyze_audience_migration(content_id, platforms)
            
            # Analyze content performance patterns
            optimal_times = await self._analyze_optimal_posting_times(content_id, platforms)
            format_performance = await self._analyze_content_format_performance(content_id, platforms)
            hashtag_performance = await self._analyze_hashtag_performance(content_id, platforms)
            
            # Calculate ROI metrics
            platform_roi = self._calculate_platform_roi(platform_metrics)
            cost_per_engagement = self._calculate_cost_per_engagement(platform_metrics)
            revenue_attribution = self._calculate_revenue_attribution(platform_metrics)
            
            insights = CrossPlatformInsights(
                content_id=content_id,
                analysis_period={"start": period_start, "end": period_end},
                platform_metrics=platform_metrics,
                platform_rankings=platform_rankings,
                growth_trends=growth_trends,
                seasonality_patterns=seasonality_patterns,
                cross_platform_audience_overlap=audience_overlap,
                unique_audience_size=unique_audience_size,
                audience_migration_patterns=migration_patterns,
                optimal_posting_times=optimal_times,
                content_format_performance=format_performance,
                hashtag_performance=hashtag_performance,
                platform_roi=platform_roi,
                cost_per_engagement=cost_per_engagement,
                revenue_attribution=revenue_attribution
            )
            
            # Cache the result
            if use_cache:
                self.insights_cache[cache_key] = insights
            
            return insights
        
        except Exception as e:
            logger.error(f"Failed to get cross-platform insights: {str(e)}")
            return CrossPlatformInsights(
                content_id=content_id,
                analysis_period={"start": period_start, "end": period_end}
            )
    
    def _rank_platforms_by_metric(
        self,
        platform_metrics: Dict[SocialPlatform, PlatformAnalytics],
        metric_type: MetricType
    ) -> List[SocialPlatform]:
        """Rank platforms by specific metric"""
        metric_map = {
            MetricType.ENGAGEMENT: "engagement_rate",
            MetricType.REACH: "reach",
            MetricType.IMPRESSIONS: "impressions",
            MetricType.VIEWS: "views",
            MetricType.LIKES: "likes",
            MetricType.COMMENTS: "comments",
            MetricType.SHARES: "shares",
            MetricType.REVENUE: "revenue"
        }
        
        metric_attr = metric_map.get(metric_type, "views")
        
        platforms_with_values = [
            (platform, getattr(analytics, metric_attr, 0))
            for platform, analytics in platform_metrics.items()
        ]
        
        # Sort by metric value descending
        platforms_with_values.sort(key=lambda x: x[1], reverse=True)
        
        return [platform for platform, _ in platforms_with_values]
    
    async def _calculate_growth_trends(
        self,
        content_id: str,
        platforms: List[SocialPlatform],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[MetricType, Dict[SocialPlatform, float]]:
        """Calculate growth trends for each metric and platform"""
        # Simplified implementation - would calculate week-over-week or month-over-month growth
        growth_trends = {}
        
        for metric_type in MetricType:
            growth_trends[metric_type] = {}
            
            for platform in platforms:
                # Placeholder: calculate actual growth rate
                growth_trends[metric_type][platform] = 0.05  # 5% growth
        
        return growth_trends
    
    async def _analyze_seasonality_patterns(
        self,
        content_id: str,
        platforms: List[SocialPlatform],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[SocialPlatform, Dict[str, Any]]:
        """Analyze seasonality patterns in platform performance"""
        # Simplified implementation - would analyze day-of-week, hour-of-day patterns
        patterns = {}
        
        for platform in platforms:
            patterns[platform] = {
                "best_days": ["Monday", "Wednesday", "Friday"],
                "best_hours": [9, 12, 17, 19],
                "seasonal_factor": 1.1
            }
        
        return patterns
    
    async def _calculate_audience_overlap(
        self,
        platform_metrics: Dict[SocialPlatform, PlatformAnalytics]
    ) -> Dict[str, float]:
        """Calculate audience overlap between platforms"""
        # Simplified implementation - would use actual audience data
        overlap = {}
        platforms = list(platform_metrics.keys())
        
        for i, platform1 in enumerate(platforms):
            for platform2 in platforms[i+1:]:
                key = f"{platform1.value}_{platform2.value}"
                # Placeholder: estimate overlap based on reach and demographics
                overlap[key] = 0.25  # 25% overlap
        
        return overlap
    
    async def _estimate_unique_audience_size(
        self,
        platform_metrics: Dict[SocialPlatform, PlatformAnalytics]
    ) -> int:
        """Estimate unique audience size across all platforms"""
        total_reach = sum(analytics.reach for analytics in platform_metrics.values())
        # Apply overlap reduction factor
        estimated_overlap = 0.3  # 30% average overlap
        return int(total_reach * (1 - estimated_overlap))
    
    async def _analyze_audience_migration(
        self,
        content_id: str,
        platforms: List[SocialPlatform]
    ) -> Dict[str, Any]:
        """Analyze audience migration patterns between platforms"""
        # Simplified implementation
        return {
            "primary_migration_path": "Instagram -> TikTok",
            "migration_rate": 0.15,
            "retention_by_platform": {platform.value: 0.7 for platform in platforms}
        }
    
    async def _analyze_optimal_posting_times(
        self,
        content_id: str,
        platforms: List[SocialPlatform]
    ) -> Dict[SocialPlatform, List[int]]:
        """Analyze optimal posting times for each platform"""
        # Simplified implementation - would analyze historical performance by time
        optimal_times = {}
        
        platform_defaults = {
            SocialPlatform.YOUTUBE: [14, 15, 16, 17],
            SocialPlatform.TIKTOK: [18, 19, 20, 21],
            SocialPlatform.INSTAGRAM: [11, 12, 17, 18, 19],
            SocialPlatform.TWITTER: [8, 9, 12, 13, 17],
            SocialPlatform.FACEBOOK: [13, 14, 15],
            SocialPlatform.LINKEDIN: [8, 9, 10, 17, 18]
        }
        
        for platform in platforms:
            optimal_times[platform] = platform_defaults.get(platform, [12, 13, 14, 15])
        
        return optimal_times
    
    async def _analyze_content_format_performance(
        self,
        content_id: str,
        platforms: List[SocialPlatform]
    ) -> Dict[str, Dict[SocialPlatform, float]]:
        """Analyze content format performance across platforms"""
        # Simplified implementation
        formats = ["video", "image", "carousel", "story"]
        format_performance = {}
        
        for format_type in formats:
            format_performance[format_type] = {}
            for platform in platforms:
                # Placeholder performance score
                format_performance[format_type][platform] = np.random.uniform(0.7, 1.3)
        
        return format_performance
    
    async def _analyze_hashtag_performance(
        self,
        content_id: str,
        platforms: List[SocialPlatform]
    ) -> Dict[str, Dict[SocialPlatform, float]]:
        """Analyze hashtag performance across platforms"""
        # Simplified implementation - would analyze actual hashtag data
        hashtags = ["#content", "#viral", "#trending", "#creator"]
        hashtag_performance = {}
        
        for hashtag in hashtags:
            hashtag_performance[hashtag] = {}
            for platform in platforms:
                # Placeholder performance score
                hashtag_performance[hashtag][platform] = np.random.uniform(0.8, 1.5)
        
        return hashtag_performance
    
    def _calculate_platform_roi(
        self,
        platform_metrics: Dict[SocialPlatform, PlatformAnalytics]
    ) -> Dict[SocialPlatform, float]:
        """Calculate ROI for each platform"""
        platform_roi = {}
        
        for platform, analytics in platform_metrics.items():
            # Simplified ROI calculation: revenue / estimated cost
            estimated_cost = analytics.impressions * analytics.cpm / 1000 if analytics.cpm > 0 else 100
            roi = (analytics.revenue / estimated_cost - 1) if estimated_cost > 0 else 0
            platform_roi[platform] = roi
        
        return platform_roi
    
    def _calculate_cost_per_engagement(
        self,
        platform_metrics: Dict[SocialPlatform, PlatformAnalytics]
    ) -> Dict[SocialPlatform, float]:
        """Calculate cost per engagement for each platform"""
        cost_per_engagement = {}
        
        for platform, analytics in platform_metrics.items():
            total_engagements = analytics.likes + analytics.comments + analytics.shares
            estimated_cost = analytics.impressions * analytics.cpm / 1000 if analytics.cpm > 0 else 0
            
            if total_engagements > 0 and estimated_cost > 0:
                cost_per_engagement[platform] = estimated_cost / total_engagements
            else:
                cost_per_engagement[platform] = 0.0
        
        return cost_per_engagement
    
    def _calculate_revenue_attribution(
        self,
        platform_metrics: Dict[SocialPlatform, PlatformAnalytics]
    ) -> Dict[SocialPlatform, float]:
        """Calculate revenue attribution for each platform"""
        total_revenue = sum(analytics.revenue for analytics in platform_metrics.values())
        
        if total_revenue == 0:
            return {platform: 0.0 for platform in platform_metrics.keys()}
        
        return {
            platform: analytics.revenue / total_revenue
            for platform, analytics in platform_metrics.items()
        }
    
    def _invalidate_caches(self, content_id: str):
        """Invalidate caches related to content"""
        # Remove cache entries containing the content_id
        keys_to_remove = [
            key for key in self.unified_cache.keys()
            if content_id in key
        ]
        for key in keys_to_remove:
            del self.unified_cache[key]
        
        keys_to_remove = [
            key for key in self.insights_cache.keys()
            if content_id in key
        ]
        for key in keys_to_remove:
            del self.insights_cache[key]
    
    async def export_analytics_report(
        self,
        content_id: str,
        platforms: List[SocialPlatform],
        period_start: datetime,
        period_end: datetime,
        format: str = "json"
    ) -> str:
        """Export comprehensive analytics report"""
        try:
            # Get unified metrics and insights
            unified_metrics = await self.get_unified_metrics(
                content_id, platforms, period_start, period_end
            )
            
            insights = await self.get_cross_platform_insights(
                content_id, platforms, period_start, period_end
            )
            
            # Create comprehensive report
            report = {
                "content_id": content_id,
                "report_generated": datetime.now().isoformat(),
                "analysis_period": {
                    "start": period_start.isoformat(),
                    "end": period_end.isoformat()
                },
                "unified_metrics": asdict(unified_metrics),
                "cross_platform_insights": asdict(insights),
                "executive_summary": self._generate_executive_summary(unified_metrics, insights)
            }
            
            if format.lower() == "json":
                return json.dumps(report, indent=2, default=str)
            else:
                # Could implement CSV, PDF formats
                return json.dumps(report, indent=2, default=str)
        
        except Exception as e:
            logger.error(f"Analytics report export failed: {str(e)}")
            return "{}"
    
    def _generate_executive_summary(
        self,
        unified_metrics: UnifiedMetrics,
        insights: CrossPlatformInsights
    ) -> Dict[str, Any]:
        """Generate executive summary of analytics"""
        return {
            "key_achievements": [
                f"Total reach of {unified_metrics.total_reach:,} across {unified_metrics.total_platforms} platforms",
                f"Generated ${unified_metrics.total_revenue:.2f} in revenue",
                f"Achieved {unified_metrics.average_engagement_rate:.2%} average engagement rate"
            ],
            "top_performing_platform": unified_metrics.best_performing_platform.value if unified_metrics.best_performing_platform else "None",
            "primary_recommendations": unified_metrics.optimization_recommendations[:3],
            "growth_opportunity": "Focus on video content for higher engagement",
            "cost_efficiency": f"Average CPM of ${unified_metrics.average_cpm:.2f} across platforms"
        }
    
    async def get_aggregator_statistics(self) -> Dict[str, Any]:
        """Get aggregator performance statistics"""
        try:
            total_content_tracked = len(set(
                key.split('_')[1] for key in self.platform_data.keys()
            ))
            
            total_data_points = sum(len(data) for data in self.platform_data.values())
            
            platform_distribution = defaultdict(int)
            for key in self.platform_data.keys():
                platform = key.split('_')[0]
                platform_distribution[platform] += len(self.platform_data[key])
            
            return {
                "total_content_tracked": total_content_tracked,
                "total_data_points": total_data_points,
                "platform_distribution": dict(platform_distribution),
                "cache_sizes": {
                    "unified_metrics": len(self.unified_cache),
                    "insights": len(self.insights_cache)
                },
                "benchmarks_loaded": len(self.benchmark_data)
            }
        
        except Exception as e:
            logger.error(f"Statistics generation failed: {str(e)}")
            return {}
    
    def clear_cache(self):
        """Clear all analytics caches"""
        self.unified_cache.clear()
        self.insights_cache.clear()
        logger.info("Analytics caches cleared")