"""Performance Tracking Workflow - Advanced Performance Analytics for Ainflue Platform.

This module provides comprehensive performance tracking and monitoring across all content
platforms, enabling real-time insights into content effectiveness and audience engagement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Performance metric types for comprehensive tracking."""
    VIEWS = "views"
    ENGAGEMENT = "engagement"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    SAVES = "saves"
    CONVERSION = "conversion"


class Platform(Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    content_id: str
    platform: Platform
    timestamp: datetime
    views: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    clicks: int = 0
    shares: int = 0
    comments: int = 0
    likes: int = 0
    saves: int = 0
    conversion_rate: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass
class TrackingResult:
    """Performance tracking result."""
    content_id: str
    tracking_period: Dict[str, datetime]
    platforms: List[Platform]
    metrics: List[PerformanceMetrics]
    aggregated_metrics: Dict[str, Union[int, float]]
    performance_score: float
    insights: List[str]
    recommendations: List[str]
    trend_analysis: Dict[str, Any]


class PerformanceTrackingWorkflow:
    """Advanced performance tracking workflow for multi-platform content analysis."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize performance tracking workflow.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.tracking_interval = self.config.get('tracking_interval', 300)  # 5 minutes
        self.platforms = self.config.get('platforms', [p.value for p in Platform])
        self.metrics = self.config.get('metrics', [m.value for m in MetricType])
        self.performance_cache = {}
        
    async def track_performance(
        self,
        content_id: str,
        platforms: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        time_period: Optional[Dict[str, datetime]] = None
    ) -> TrackingResult:
        """Track performance metrics for specific content across platforms.
        
        Args:
            content_id: Unique content identifier
            platforms: List of platforms to track (default: all configured)
            metrics: List of metrics to track (default: all configured)
            time_period: Time period for tracking (default: last 24 hours)
            
        Returns:
            TrackingResult with comprehensive performance data
        """
        try:
            logger.info(f"Starting performance tracking for content: {content_id}")
            
            # Set defaults
            platforms = platforms or self.platforms
            metrics = metrics or self.metrics
            time_period = time_period or {
                'start': datetime.now() - timedelta(hours=24),
                'end': datetime.now()
            }
            
            # Collect metrics from all platforms
            all_metrics = []
            for platform in platforms:
                platform_metrics = await self._collect_platform_metrics(
                    content_id, platform, metrics, time_period
                )
                all_metrics.extend(platform_metrics)
            
            # Aggregate metrics
            aggregated_metrics = self._aggregate_metrics(all_metrics)
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(aggregated_metrics)
            
            # Generate insights and recommendations
            insights = await self._generate_insights(all_metrics, aggregated_metrics)
            recommendations = await self._generate_recommendations(
                all_metrics, aggregated_metrics, performance_score
            )
            
            # Perform trend analysis
            trend_analysis = await self._analyze_trends(content_id, all_metrics)
            
            result = TrackingResult(
                content_id=content_id,
                tracking_period=time_period,
                platforms=[Platform(p) for p in platforms],
                metrics=all_metrics,
                aggregated_metrics=aggregated_metrics,
                performance_score=performance_score,
                insights=insights,
                recommendations=recommendations,
                trend_analysis=trend_analysis
            )
            
            # Cache result
            self.performance_cache[content_id] = result
            
            logger.info(f"Performance tracking completed for content: {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error tracking performance for content {content_id}: {str(e)}")
            raise
    
    async def _collect_platform_metrics(
        self,
        content_id: str,
        platform: str,
        metrics: List[str],
        time_period: Dict[str, datetime]
    ) -> List[PerformanceMetrics]:
        """Collect metrics from specific platform.
        
        Args:
            content_id: Content identifier
            platform: Platform name
            metrics: List of metrics to collect
            time_period: Time period for collection
            
        Returns:
            List of PerformanceMetrics
        """
        try:
            # Simulate API call to platform
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Mock data generation (in real implementation, call actual platform APIs)
            import random
            
            base_metrics = PerformanceMetrics(
                content_id=content_id,
                platform=Platform(platform),
                timestamp=datetime.now(),
                views=random.randint(1000, 100000),
                engagement_rate=random.uniform(1.0, 15.0),
                reach=random.randint(500, 80000),
                impressions=random.randint(2000, 150000),
                clicks=random.randint(50, 5000),
                shares=random.randint(10, 1000),
                comments=random.randint(5, 500),
                likes=random.randint(100, 10000),
                saves=random.randint(20, 2000),
                conversion_rate=random.uniform(0.5, 5.0),
                metadata={
                    'platform_specific_data': f"{platform}_data",
                    'collection_time': datetime.now().isoformat()
                }
            )
            
            return [base_metrics]
            
        except Exception as e:
            logger.error(f"Error collecting metrics from {platform}: {str(e)}")
            return []
    
    def _aggregate_metrics(self, metrics: List[PerformanceMetrics]) -> Dict[str, Union[int, float]]:
        """Aggregate metrics across platforms.
        
        Args:
            metrics: List of performance metrics
            
        Returns:
            Dictionary of aggregated metrics
        """
        if not metrics:
            return {}
        
        total_views = sum(m.views for m in metrics)
        total_reach = sum(m.reach for m in metrics)
        total_impressions = sum(m.impressions for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        total_shares = sum(m.shares for m in metrics)
        total_comments = sum(m.comments for m in metrics)
        total_likes = sum(m.likes for m in metrics)
        total_saves = sum(m.saves for m in metrics)
        
        avg_engagement_rate = sum(m.engagement_rate for m in metrics) / len(metrics)
        avg_conversion_rate = sum(m.conversion_rate for m in metrics) / len(metrics)
        
        return {
            'total_views': total_views,
            'total_reach': total_reach,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_shares': total_shares,
            'total_comments': total_comments,
            'total_likes': total_likes,
            'total_saves': total_saves,
            'average_engagement_rate': avg_engagement_rate,
            'average_conversion_rate': avg_conversion_rate,
            'engagement_interactions': total_likes + total_comments + total_shares,
            'click_through_rate': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        }
    
    def _calculate_performance_score(self, aggregated_metrics: Dict[str, Union[int, float]]) -> float:
        """Calculate overall performance score.
        
        Args:
            aggregated_metrics: Aggregated metrics dictionary
            
        Returns:
            Performance score (0-100)
        """
        if not aggregated_metrics:
            return 0.0
        
        # Weighted performance scoring
        weights = {
            'engagement_rate': 0.3,
            'conversion_rate': 0.25,
            'reach': 0.2,
            'click_through_rate': 0.15,
            'interactions': 0.1
        }
        
        # Normalize metrics to 0-100 scale
        normalized_engagement = min(aggregated_metrics.get('average_engagement_rate', 0) * 10, 100)
        normalized_conversion = min(aggregated_metrics.get('average_conversion_rate', 0) * 20, 100)
        normalized_reach = min(aggregated_metrics.get('total_reach', 0) / 1000, 100)
        normalized_ctr = min(aggregated_metrics.get('click_through_rate', 0) * 5, 100)
        normalized_interactions = min(aggregated_metrics.get('engagement_interactions', 0) / 100, 100)
        
        score = (
            normalized_engagement * weights['engagement_rate'] +
            normalized_conversion * weights['conversion_rate'] +
            normalized_reach * weights['reach'] +
            normalized_ctr * weights['click_through_rate'] +
            normalized_interactions * weights['interactions']
        )
        
        return round(min(score, 100), 2)
    
    async def _generate_insights(
        self,
        metrics: List[PerformanceMetrics],
        aggregated_metrics: Dict[str, Union[int, float]]
    ) -> List[str]:
        """Generate performance insights.
        
        Args:
            metrics: List of performance metrics
            aggregated_metrics: Aggregated metrics
            
        Returns:
            List of insight strings
        """
        insights = []
        
        # Platform performance comparison
        platform_performance = {}
        for metric in metrics:
            platform = metric.platform.value
            if platform not in platform_performance:
                platform_performance[platform] = []
            platform_performance[platform].append(metric.engagement_rate)
        
        if len(platform_performance) > 1:
            best_platform = max(platform_performance.keys(), 
                              key=lambda p: sum(platform_performance[p]) / len(platform_performance[p]))
            insights.append(f"Best performing platform: {best_platform.title()}")
        
        # Engagement analysis
        avg_engagement = aggregated_metrics.get('average_engagement_rate', 0)
        if avg_engagement > 10:
            insights.append("Exceptional engagement rate - content resonates strongly with audience")
        elif avg_engagement > 5:
            insights.append("Good engagement rate - audience is actively interacting")
        elif avg_engagement < 2:
            insights.append("Low engagement rate - consider content optimization")
        
        # Reach vs Engagement analysis
        total_reach = aggregated_metrics.get('total_reach', 0)
        engagement_interactions = aggregated_metrics.get('engagement_interactions', 0)
        if total_reach > 0:
            interaction_rate = (engagement_interactions / total_reach) * 100
            if interaction_rate > 5:
                insights.append("High interaction rate relative to reach - strong content quality")
            elif interaction_rate < 1:
                insights.append("Low interaction rate - content may need improvement")
        
        return insights
    
    async def _generate_recommendations(
        self,
        metrics: List[PerformanceMetrics],
        aggregated_metrics: Dict[str, Union[int, float]],
        performance_score: float
    ) -> List[str]:
        """Generate performance improvement recommendations.
        
        Args:
            metrics: List of performance metrics
            aggregated_metrics: Aggregated metrics
            performance_score: Overall performance score
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Overall performance recommendations
        if performance_score < 30:
            recommendations.append("Consider revising content strategy and posting times")
            recommendations.append("Analyze competitor content for inspiration")
        elif performance_score < 60:
            recommendations.append("Optimize content for better engagement")
            recommendations.append("Experiment with different content formats")
        else:
            recommendations.append("Great performance! Consider scaling successful content types")
        
        # Platform-specific recommendations
        platform_metrics = {}
        for metric in metrics:
            platform = metric.platform.value
            if platform not in platform_metrics:
                platform_metrics[platform] = metric
            elif metric.engagement_rate > platform_metrics[platform].engagement_rate:
                platform_metrics[platform] = metric
        
        for platform, metric in platform_metrics.items():
            if metric.engagement_rate < 3:
                recommendations.append(f"Improve {platform} content engagement with better CTAs")
            if metric.conversion_rate < 1:
                recommendations.append(f"Optimize {platform} conversion funnel")
        
        # CTR recommendations
        ctr = aggregated_metrics.get('click_through_rate', 0)
        if ctr < 1:
            recommendations.append("Improve call-to-action clarity and placement")
        elif ctr > 5:
            recommendations.append("Excellent CTR - replicate successful CTA strategies")
        
        return recommendations
    
    async def _analyze_trends(
        self,
        content_id: str,
        metrics: List[PerformanceMetrics]
    ) -> Dict[str, Any]:
        """Analyze performance trends over time.
        
        Args:
            content_id: Content identifier
            metrics: Current metrics
            
        Returns:
            Dictionary with trend analysis
        """
        # In a real implementation, this would compare with historical data
        trend_analysis = {
            'trending_up': [],
            'trending_down': [],
            'stable': [],
            'growth_rate': 0.0,
            'prediction': 'stable'
        }
        
        # Mock trend analysis based on current performance
        avg_engagement = sum(m.engagement_rate for m in metrics) / len(metrics) if metrics else 0
        
        if avg_engagement > 8:
            trend_analysis['trending_up'].append('engagement_rate')
            trend_analysis['growth_rate'] = 15.5
            trend_analysis['prediction'] = 'continued_growth'
        elif avg_engagement < 3:
            trend_analysis['trending_down'].append('engagement_rate')
            trend_analysis['growth_rate'] = -8.2
            trend_analysis['prediction'] = 'declining_performance'
        else:
            trend_analysis['stable'].append('engagement_rate')
            trend_analysis['prediction'] = 'stable_performance'
        
        return trend_analysis

    async def get_real_time_metrics(self, content_id: str) -> Optional[PerformanceMetrics]:
        """Get real-time performance metrics for content.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Latest PerformanceMetrics or None
        """
        try:
            # Check cache first
            if content_id in self.performance_cache:
                cached_result = self.performance_cache[content_id]
                if cached_result.metrics:
                    return cached_result.metrics[-1]  # Return latest metric
            
            # Fetch real-time data
            platforms = [Platform.INSTAGRAM.value]  # Start with one platform for real-time
            metrics = await self._collect_platform_metrics(
                content_id, platforms[0], self.metrics, 
                {'start': datetime.now() - timedelta(minutes=5), 'end': datetime.now()}
            )
            
            return metrics[0] if metrics else None
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {str(e)}")
            return None

    async def get_performance_history(
        self, 
        content_id: str, 
        days: int = 30
    ) -> List[PerformanceMetrics]:
        """Get historical performance data.
        
        Args:
            content_id: Content identifier
            days: Number of days of history to retrieve
            
        Returns:
            List of historical PerformanceMetrics
        """
        try:
            # In real implementation, this would query historical database
            history = []
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                # Mock historical data
                import random
                for platform in [Platform.INSTAGRAM, Platform.TIKTOK]:
                    metric = PerformanceMetrics(
                        content_id=content_id,
                        platform=platform,
                        timestamp=date,
                        views=random.randint(500, 50000),
                        engagement_rate=random.uniform(0.5, 12.0),
                        reach=random.randint(300, 40000),
                        impressions=random.randint(1000, 80000)
                    )
                    history.append(metric)
            
            return sorted(history, key=lambda x: x.timestamp)
            
        except Exception as e:
            logger.error(f"Error getting performance history: {str(e)}")
            return []