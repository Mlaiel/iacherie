"""Performance Tracking Workflow - Advanced performance analytics for content creators.

This module provides comprehensive performance tracking capabilities including content performance,
audience engagement, growth metrics, and cross-platform analytics for multi-format content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from collections import defaultdict
import statistics


class PerformanceMetricType(Enum):
    """Types of performance metrics to track."""
    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    CLICK_THROUGH_RATE = "ctr"
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CONVERSION_RATE = "conversion_rate"
    WATCH_TIME = "watch_time"
    COMPLETION_RATE = "completion_rate"


class PlatformType(Enum):
    """Social media and content platforms."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PINTEREST = "pinterest"


class TimeFrame(Enum):
    """Time frames for performance analysis."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class PerformanceData:
    """Individual performance data point."""
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    platform: PlatformType
    content_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics."""
    content_id: str
    platform: PlatformType
    time_frame: TimeFrame
    total_views: int = 0
    total_likes: int = 0
    total_shares: int = 0
    total_comments: int = 0
    total_saves: int = 0
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    watch_time_seconds: int = 0
    completion_rate: float = 0.0
    conversion_rate: float = 0.0
    growth_rate: float = 0.0
    viral_coefficient: float = 0.0
    audience_retention: Dict[str, float] = field(default_factory=dict)
    demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, int] = field(default_factory=dict)
    device_breakdown: Dict[str, int] = field(default_factory=dict)
    traffic_sources: Dict[str, int] = field(default_factory=dict)


@dataclass
class TrackingResult:
    """Result of performance tracking analysis."""
    user_id: str
    content_metrics: List[PerformanceMetrics]
    aggregate_metrics: PerformanceMetrics
    insights: List[str]
    recommendations: List[str]
    trends: Dict[str, Any]
    benchmarks: Dict[str, float]
    performance_score: float
    analysis_timestamp: datetime


class PerformanceTrackingWorkflow:
    """
    Advanced performance tracking workflow for content creators.
    
    Provides comprehensive performance analytics including engagement tracking,
    growth analysis, audience insights, and cross-platform performance comparison.
    """
    
    def __init__(self):
        """Initialize performance tracking workflow."""
        self.tracking_data = defaultdict(list)
        self.platform_weights = {
            PlatformType.YOUTUBE: 1.0,
            PlatformType.INSTAGRAM: 0.9,
            PlatformType.TIKTOK: 0.8,
            PlatformType.TWITTER: 0.7,
            PlatformType.FACEBOOK: 0.8,
            PlatformType.LINKEDIN: 0.6,
            PlatformType.SPOTIFY: 0.9,
            PlatformType.SOUNDCLOUD: 0.6,
            PlatformType.TWITCH: 0.8,
            PlatformType.PINTEREST: 0.5
        }
    
    async def track_performance(
        self,
        user_id: str,
        content_id: str,
        platform: PlatformType,
        time_frame: TimeFrame = TimeFrame.DAILY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> TrackingResult:
        """
        Track performance for specific content across platforms.
        
        Args:
            user_id: Creator's unique identifier
            content_id: Content item identifier
            platform: Target platform
            time_frame: Analysis time frame
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            TrackingResult with comprehensive performance data
        """
        
        # Set default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Collect performance data
        performance_data = await self._collect_performance_data(
            user_id, content_id, platform, start_date, end_date
        )
        
        # Calculate metrics
        metrics = await self._calculate_metrics(
            performance_data, time_frame, platform
        )
        
        # Generate insights
        insights = await self._generate_insights(metrics, platform)
        
        # Create recommendations
        recommendations = await self._create_recommendations(metrics, insights)
        
        # Analyze trends
        trends = await self._analyze_trends(performance_data, time_frame)
        
        # Calculate benchmarks
        benchmarks = await self._calculate_benchmarks(metrics, platform)
        
        # Calculate performance score
        performance_score = await self._calculate_performance_score(metrics, benchmarks)
        
        return TrackingResult(
            user_id=user_id,
            content_metrics=[metrics],
            aggregate_metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            trends=trends,
            benchmarks=benchmarks,
            performance_score=performance_score,
            analysis_timestamp=datetime.utcnow()
        )
    
    async def track_multi_platform_performance(
        self,
        user_id: str,
        content_ids: List[str],
        platforms: List[PlatformType],
        time_frame: TimeFrame = TimeFrame.WEEKLY
    ) -> TrackingResult:
        """Track performance across multiple platforms."""
        
        all_metrics = []
        
        for content_id in content_ids:
            for platform in platforms:
                try:
                    result = await self.track_performance(
                        user_id, content_id, platform, time_frame
                    )
                    all_metrics.extend(result.content_metrics)
                except Exception as e:
                    print(f"Error tracking {content_id} on {platform}: {e}")
        
        # Aggregate all metrics
        aggregate_metrics = await self._aggregate_metrics(all_metrics)
        
        # Cross-platform insights
        insights = await self._generate_cross_platform_insights(all_metrics)
        
        # Platform-specific recommendations
        recommendations = await self._create_multi_platform_recommendations(all_metrics)
        
        return TrackingResult(
            user_id=user_id,
            content_metrics=all_metrics,
            aggregate_metrics=aggregate_metrics,
            insights=insights,
            recommendations=recommendations,
            trends={},
            benchmarks={},
            performance_score=aggregate_metrics.viral_coefficient * 100,
            analysis_timestamp=datetime.utcnow()
        )
    
    async def get_user_analytics(
        self,
        user_id: str,
        time_period: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive user analytics over specified time period."""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=time_period)
        
        # Get all user content performance
        content_performance = await self._get_user_content_performance(
            user_id, start_date, end_date
        )
        
        # Calculate aggregate statistics
        total_views = sum(cp.total_views for cp in content_performance)
        total_engagement = sum(
            cp.total_likes + cp.total_shares + cp.total_comments 
            for cp in content_performance
        )
        
        avg_engagement_rate = statistics.mean([
            cp.engagement_rate for cp in content_performance
        ]) if content_performance else 0
        
        return {
            "user_id": user_id,
            "time_period_days": time_period,
            "total_content_pieces": len(content_performance),
            "total_views": total_views,
            "total_engagement": total_engagement,
            "average_engagement_rate": avg_engagement_rate,
            "top_performing_content": await self._get_top_performing_content(content_performance),
            "platform_breakdown": await self._get_platform_breakdown(content_performance),
            "growth_metrics": await self._calculate_growth_metrics(user_id, time_period),
            "performance_trends": await self._get_performance_trends(user_id, time_period)
        }
    
    async def _collect_performance_data(
        self,
        user_id: str,
        content_id: str,
        platform: PlatformType,
        start_date: datetime,
        end_date: datetime
    ) -> List[PerformanceData]:
        """Collect raw performance data from platform APIs."""
        
        # Simulate data collection from platform APIs
        # In real implementation, this would call actual platform APIs
        performance_data = []
        
        current_date = start_date
        while current_date <= end_date:
            # Simulate metrics for each day
            data_point = PerformanceData(
                metric_type=PerformanceMetricType.VIEWS,
                value=float(hash(f"{content_id}_{current_date}") % 10000),
                timestamp=current_date,
                platform=platform,
                content_id=content_id,
                metadata={"simulated": True}
            )
            performance_data.append(data_point)
            current_date += timedelta(days=1)
        
        return performance_data
    
    async def _calculate_metrics(
        self,
        performance_data: List[PerformanceData],
        time_frame: TimeFrame,
        platform: PlatformType
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics."""
        
        if not performance_data:
            return PerformanceMetrics(
                content_id="unknown",
                platform=platform,
                time_frame=time_frame
            )
        
        content_id = performance_data[0].content_id
        total_views = sum(dp.value for dp in performance_data if dp.metric_type == PerformanceMetricType.VIEWS)
        
        # Calculate engagement rate (simulated)
        engagement_rate = min(0.15, total_views / 100000) if total_views > 0 else 0
        
        return PerformanceMetrics(
            content_id=content_id,
            platform=platform,
            time_frame=time_frame,
            total_views=int(total_views),
            total_likes=int(total_views * 0.05),
            total_shares=int(total_views * 0.01),
            total_comments=int(total_views * 0.02),
            total_saves=int(total_views * 0.008),
            engagement_rate=engagement_rate,
            click_through_rate=0.03,
            reach=int(total_views * 1.2),
            impressions=int(total_views * 2.5),
            watch_time_seconds=int(total_views * 45),
            completion_rate=0.65,
            conversion_rate=0.02,
            growth_rate=0.15,
            viral_coefficient=engagement_rate * 2,
            audience_retention={"0-25%": 0.8, "25-50%": 0.6, "50-75%": 0.4, "75-100%": 0.3},
            demographics={"18-24": 0.3, "25-34": 0.4, "35-44": 0.2, "45+": 0.1},
            geographic_data={"US": 40, "UK": 20, "CA": 15, "DE": 10, "FR": 8, "Other": 7},
            device_breakdown={"mobile": 70, "desktop": 25, "tablet": 5},
            traffic_sources={"organic": 45, "direct": 30, "social": 20, "referral": 5}
        )
    
    async def _generate_insights(
        self,
        metrics: PerformanceMetrics,
        platform: PlatformType
    ) -> List[str]:
        """Generate actionable insights from performance metrics."""
        
        insights = []
        
        # Engagement rate insights
        if metrics.engagement_rate > 0.08:
            insights.append("🎉 Excellent engagement rate! Your content strongly resonates with your audience.")
        elif metrics.engagement_rate > 0.04:
            insights.append("👍 Good engagement rate. Consider strategies to boost interaction further.")
        else:
            insights.append("📈 Low engagement rate. Focus on creating more engaging content.")
        
        # Completion rate insights
        if metrics.completion_rate > 0.7:
            insights.append("⭐ High completion rate indicates compelling content that keeps viewers watching.")
        elif metrics.completion_rate < 0.4:
            insights.append("⚠️ Low completion rate suggests viewers lose interest early. Consider stronger hooks.")
        
        # Platform-specific insights
        if platform == PlatformType.YOUTUBE:
            if metrics.watch_time_seconds / max(metrics.total_views, 1) > 60:
                insights.append("🎬 Strong YouTube watch time indicates good content quality.")
        elif platform == PlatformType.INSTAGRAM:
            if metrics.total_saves > metrics.total_likes * 0.1:
                insights.append("💾 High save rate on Instagram indicates valuable, reference-worthy content.")
        elif platform == PlatformType.TIKTOK:
            if metrics.total_shares > metrics.total_likes * 0.3:
                insights.append("🚀 High share rate on TikTok indicates viral potential.")
        
        # Growth insights
        if metrics.growth_rate > 0.2:
            insights.append("📈 Strong growth momentum. Maintain consistent posting schedule.")
        
        return insights
    
    async def _create_recommendations(
        self,
        metrics: PerformanceMetrics,
        insights: List[str]
    ) -> List[str]:
        """Create actionable recommendations based on performance analysis."""
        
        recommendations = []
        
        # Engagement recommendations
        if metrics.engagement_rate < 0.04:
            recommendations.append("💬 Increase engagement by asking questions and responding to comments promptly.")
            recommendations.append("🎯 Use trending hashtags and participate in popular challenges.")
        
        # Content optimization
        if metrics.completion_rate < 0.5:
            recommendations.append("🎣 Create stronger opening hooks in the first 3 seconds.")
            recommendations.append("✂️ Consider shortening content length to maintain viewer attention.")
        
        # Timing optimization
        recommendations.append("⏰ Analyze audience active hours and post during peak engagement times.")
        
        # Cross-platform strategy
        if metrics.platform == PlatformType.YOUTUBE:
            recommendations.append("📺 Create shorter clips for Instagram/TikTok to drive traffic to YouTube.")
        
        # Growth strategies
        if metrics.growth_rate < 0.1:
            recommendations.append("🤝 Collaborate with other creators in your niche for cross-promotion.")
            recommendations.append("🎪 Participate in trending topics and challenges.")
        
        return recommendations
    
    async def _analyze_trends(
        self,
        performance_data: List[PerformanceData],
        time_frame: TimeFrame
    ) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        
        if len(performance_data) < 2:
            return {"trend": "insufficient_data"}
        
        # Group data by time periods
        values = [dp.value for dp in performance_data]
        
        # Calculate trend direction
        if len(values) >= 2:
            recent_avg = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
            earlier_avg = statistics.mean(values[:3]) if len(values) >= 3 else values[0]
            
            trend_direction = "increasing" if recent_avg > earlier_avg else "decreasing"
            trend_strength = abs(recent_avg - earlier_avg) / max(earlier_avg, 1)
        else:
            trend_direction = "stable"
            trend_strength = 0
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "peak_value": max(values),
            "valley_value": min(values),
            "volatility": statistics.stdev(values) if len(values) > 1 else 0,
            "data_points": len(values)
        }
    
    async def _calculate_benchmarks(
        self,
        metrics: PerformanceMetrics,
        platform: PlatformType
    ) -> Dict[str, float]:
        """Calculate industry benchmarks for comparison."""
        
        # Industry benchmark data (would come from database in real implementation)
        benchmarks = {
            PlatformType.YOUTUBE: {
                "engagement_rate": 0.045,
                "completion_rate": 0.55,
                "click_through_rate": 0.025
            },
            PlatformType.INSTAGRAM: {
                "engagement_rate": 0.067,
                "completion_rate": 0.70,
                "click_through_rate": 0.015
            },
            PlatformType.TIKTOK: {
                "engagement_rate": 0.089,
                "completion_rate": 0.48,
                "click_through_rate": 0.035
            }
        }
        
        return benchmarks.get(platform, {
            "engagement_rate": 0.05,
            "completion_rate": 0.60,
            "click_through_rate": 0.02
        })
    
    async def _calculate_performance_score(
        self,
        metrics: PerformanceMetrics,
        benchmarks: Dict[str, float]
    ) -> float:
        """Calculate overall performance score (0-100)."""
        
        score = 0
        total_weight = 0
        
        # Engagement rate score (weight: 40%)
        if "engagement_rate" in benchmarks:
            engagement_score = min(100, (metrics.engagement_rate / benchmarks["engagement_rate"]) * 100)
            score += engagement_score * 0.4
            total_weight += 0.4
        
        # Completion rate score (weight: 30%)
        if "completion_rate" in benchmarks:
            completion_score = min(100, (metrics.completion_rate / benchmarks["completion_rate"]) * 100)
            score += completion_score * 0.3
            total_weight += 0.3
        
        # Growth rate score (weight: 20%)
        growth_score = min(100, metrics.growth_rate * 500)  # 20% growth = 100 points
        score += growth_score * 0.2
        total_weight += 0.2
        
        # Viral coefficient score (weight: 10%)
        viral_score = min(100, metrics.viral_coefficient * 1000)
        score += viral_score * 0.1
        total_weight += 0.1
        
        return score / max(total_weight, 1)
    
    async def _aggregate_metrics(
        self,
        metrics_list: List[PerformanceMetrics]
    ) -> PerformanceMetrics:
        """Aggregate multiple performance metrics."""
        
        if not metrics_list:
            return PerformanceMetrics(
                content_id="aggregate",
                platform=PlatformType.YOUTUBE,
                time_frame=TimeFrame.DAILY
            )
        
        return PerformanceMetrics(
            content_id="aggregate",
            platform=metrics_list[0].platform,
            time_frame=metrics_list[0].time_frame,
            total_views=sum(m.total_views for m in metrics_list),
            total_likes=sum(m.total_likes for m in metrics_list),
            total_shares=sum(m.total_shares for m in metrics_list),
            total_comments=sum(m.total_comments for m in metrics_list),
            total_saves=sum(m.total_saves for m in metrics_list),
            engagement_rate=statistics.mean([m.engagement_rate for m in metrics_list]),
            click_through_rate=statistics.mean([m.click_through_rate for m in metrics_list]),
            reach=sum(m.reach for m in metrics_list),
            impressions=sum(m.impressions for m in metrics_list),
            watch_time_seconds=sum(m.watch_time_seconds for m in metrics_list),
            completion_rate=statistics.mean([m.completion_rate for m in metrics_list]),
            conversion_rate=statistics.mean([m.conversion_rate for m in metrics_list]),
            growth_rate=statistics.mean([m.growth_rate for m in metrics_list]),
            viral_coefficient=statistics.mean([m.viral_coefficient for m in metrics_list])
        )
    
    async def _generate_cross_platform_insights(
        self,
        metrics_list: List[PerformanceMetrics]
    ) -> List[str]:
        """Generate insights comparing performance across platforms."""
        
        insights = []
        
        if len(metrics_list) <= 1:
            return ["Need data from multiple platforms for cross-platform analysis."]
        
        # Find best performing platform
        platform_performance = defaultdict(list)
        for metrics in metrics_list:
            platform_performance[metrics.platform].append(metrics.engagement_rate)
        
        best_platform = max(
            platform_performance.keys(),
            key=lambda p: statistics.mean(platform_performance[p])
        )
        
        insights.append(f"🏆 Best performing platform: {best_platform.value.title()}")
        
        # Engagement rate comparison
        engagement_rates = [m.engagement_rate for m in metrics_list]
        if max(engagement_rates) / min(engagement_rates) > 2:
            insights.append("📊 Significant engagement rate variation across platforms - focus on top performers.")
        
        return insights
    
    async def _create_multi_platform_recommendations(
        self,
        metrics_list: List[PerformanceMetrics]
    ) -> List[str]:
        """Create recommendations for multi-platform strategy."""
        
        recommendations = []
        
        recommendations.append("🔄 Repurpose top-performing content across all platforms.")
        recommendations.append("⏰ Optimize posting schedule for each platform's peak hours.")
        recommendations.append("🎯 Tailor content format to each platform's preferences.")
        recommendations.append("📈 Allocate more resources to your best-performing platforms.")
        
        return recommendations
    
    async def _get_user_content_performance(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[PerformanceMetrics]:
        """Get all content performance for a user in specified time period."""
        
        # Simulate getting user's content performance
        # In real implementation, this would query the database
        content_performance = []
        
        for i in range(5):  # Simulate 5 pieces of content
            content_id = f"content_{user_id}_{i}"
            platform = list(PlatformType)[i % len(PlatformType)]
            
            metrics = PerformanceMetrics(
                content_id=content_id,
                platform=platform,
                time_frame=TimeFrame.DAILY,
                total_views=hash(content_id) % 50000,
                total_likes=hash(content_id) % 2500,
                engagement_rate=min(0.2, (hash(content_id) % 100) / 1000),
                completion_rate=min(1.0, (hash(content_id) % 80) / 100)
            )
            content_performance.append(metrics)
        
        return content_performance
    
    async def _get_top_performing_content(
        self,
        content_performance: List[PerformanceMetrics]
    ) -> List[Dict[str, Any]]:
        """Get top performing content pieces."""
        
        sorted_content = sorted(
            content_performance,
            key=lambda x: x.engagement_rate,
            reverse=True
        )
        
        return [
            {
                "content_id": metrics.content_id,
                "platform": metrics.platform.value,
                "engagement_rate": metrics.engagement_rate,
                "total_views": metrics.total_views
            }
            for metrics in sorted_content[:3]
        ]
    
    async def _get_platform_breakdown(
        self,
        content_performance: List[PerformanceMetrics]
    ) -> Dict[str, Dict[str, Any]]:
        """Get performance breakdown by platform."""
        
        platform_data = defaultdict(lambda: {"views": 0, "engagement": 0, "content_count": 0})
        
        for metrics in content_performance:
            platform = metrics.platform.value
            platform_data[platform]["views"] += metrics.total_views
            platform_data[platform]["engagement"] += metrics.total_likes + metrics.total_shares + metrics.total_comments
            platform_data[platform]["content_count"] += 1
        
        return dict(platform_data)
    
    async def _calculate_growth_metrics(
        self,
        user_id: str,
        time_period: int
    ) -> Dict[str, float]:
        """Calculate growth metrics for user."""
        
        # Simulate growth calculations
        return {
            "follower_growth_rate": 0.15,
            "engagement_growth_rate": 0.12,
            "view_growth_rate": 0.18,
            "revenue_growth_rate": 0.22
        }
    
    async def _get_performance_trends(
        self,
        user_id: str,
        time_period: int
    ) -> Dict[str, Any]:
        """Get performance trends for user."""
        
        return {
            "overall_trend": "increasing",
            "best_performing_day": "Wednesday",
            "best_performing_time": "8:00 PM",
            "seasonal_patterns": {
                "weekdays": {"Mon": 0.8, "Tue": 0.9, "Wed": 1.2, "Thu": 1.1, "Fri": 1.0},
                "weekends": {"Sat": 1.3, "Sun": 1.1}
            }
        }


# Export main classes
__all__ = [
    'PerformanceTrackingWorkflow',
    'PerformanceMetrics',
    'TrackingResult',
    'PerformanceData',
    'PerformanceMetricType',
    'PlatformType',
    'TimeFrame'
]