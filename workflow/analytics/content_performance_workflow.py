"""Content Performance Workflow - Advanced Content Performance Analytics for Ainflue Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content for analysis."""
    VIDEO = "video"
    IMAGE = "image"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    LIVE = "live"
    ARTICLE = "article"
    PODCAST = "podcast"


@dataclass
class ContentMetrics:
    """Content performance metrics."""
    content_id: str
    content_type: ContentType
    platform: str
    publish_date: datetime
    views: int = 0
    engagement_rate: float = 0.0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    reach: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    completion_rate: float = 0.0
    average_watch_time: float = 0.0
    performance_score: float = 0.0


@dataclass
class PerformanceReport:
    """Comprehensive content performance report."""
    analysis_period: Dict[str, datetime]
    total_content_pieces: int
    content_metrics: List[ContentMetrics]
    top_performing_content: List[ContentMetrics]
    content_type_analysis: Dict[str, Any]
    platform_performance: Dict[str, Any]
    optimization_insights: List[str]
    trend_analysis: Dict[str, Any]


class ContentPerformanceWorkflow:
    """Advanced content performance analysis workflow."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content performance workflow."""
        self.config = config or {}
        self.performance_cache = {}

    async def analyze_content_performance(
        self,
        creator_id: str,
        time_period: Optional[Dict[str, datetime]] = None,
        content_types: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None
    ) -> PerformanceReport:
        """Analyze content performance across platforms and types."""
        try:
            logger.info(f"Starting content performance analysis for creator: {creator_id}")
            
            time_period = time_period or {
                'start': datetime.now() - timedelta(days=30),
                'end': datetime.now()
            }
            
            # Collect content performance data
            content_metrics = await self._collect_content_metrics(
                creator_id, time_period, content_types, platforms
            )
            
            # Identify top performing content
            top_performing = self._identify_top_performing_content(content_metrics)
            
            # Analyze by content type
            content_type_analysis = self._analyze_by_content_type(content_metrics)
            
            # Analyze by platform
            platform_performance = self._analyze_by_platform(content_metrics)
            
            # Generate optimization insights
            optimization_insights = await self._generate_optimization_insights(content_metrics)
            
            # Perform trend analysis
            trend_analysis = self._analyze_content_trends(content_metrics)
            
            report = PerformanceReport(
                analysis_period=time_period,
                total_content_pieces=len(content_metrics),
                content_metrics=content_metrics,
                top_performing_content=top_performing,
                content_type_analysis=content_type_analysis,
                platform_performance=platform_performance,
                optimization_insights=optimization_insights,
                trend_analysis=trend_analysis
            )
            
            self.performance_cache[creator_id] = report
            logger.info(f"Content performance analysis completed for creator: {creator_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error analyzing content performance: {str(e)}")
            raise

    async def _collect_content_metrics(
        self,
        creator_id: str,
        time_period: Dict[str, datetime],
        content_types: Optional[List[str]],
        platforms: Optional[List[str]]
    ) -> List[ContentMetrics]:
        """Collect content performance metrics."""
        # Mock implementation - in production, integrate with platform APIs
        import random
        
        metrics = []
        content_types = content_types or [ct.value for ct in ContentType]
        platforms = platforms or ['instagram', 'tiktok', 'youtube']
        
        num_content = random.randint(20, 100)
        
        for i in range(num_content):
            content_type = random.choice([ContentType(ct) for ct in content_types])
            platform = random.choice(platforms)
            
            # Generate realistic metrics based on content type
            base_views = {
                ContentType.VIDEO: (1000, 50000),
                ContentType.IMAGE: (500, 20000),
                ContentType.CAROUSEL: (800, 30000),
                ContentType.STORY: (200, 10000),
                ContentType.REEL: (2000, 100000),
                ContentType.LIVE: (100, 5000)
            }
            
            min_views, max_views = base_views.get(content_type, (500, 25000))
            views = random.randint(min_views, max_views)
            
            metrics.append(ContentMetrics(
                content_id=f"content_{i+1}",
                content_type=content_type,
                platform=platform,
                publish_date=time_period['start'] + timedelta(days=random.randint(0, 29)),
                views=views,
                engagement_rate=random.uniform(1.0, 15.0),
                likes=random.randint(views//100, views//10),
                comments=random.randint(views//500, views//50),
                shares=random.randint(views//1000, views//100),
                saves=random.randint(views//200, views//20),
                reach=random.randint(views//2, views*2),
                impressions=random.randint(views, views*3),
                click_through_rate=random.uniform(0.5, 8.0),
                completion_rate=random.uniform(30, 95),
                average_watch_time=random.uniform(15, 180),
                performance_score=random.uniform(40, 95)
            ))
        
        return metrics

    def _identify_top_performing_content(self, metrics: List[ContentMetrics]) -> List[ContentMetrics]:
        """Identify top performing content pieces."""
        return sorted(metrics, key=lambda x: x.performance_score, reverse=True)[:10]

    def _analyze_by_content_type(self, metrics: List[ContentMetrics]) -> Dict[str, Any]:
        """Analyze performance by content type."""
        type_analysis = {}
        
        for content_type in ContentType:
            type_metrics = [m for m in metrics if m.content_type == content_type]
            if type_metrics:
                type_analysis[content_type.value] = {
                    'count': len(type_metrics),
                    'avg_views': sum(m.views for m in type_metrics) / len(type_metrics),
                    'avg_engagement_rate': sum(m.engagement_rate for m in type_metrics) / len(type_metrics),
                    'avg_performance_score': sum(m.performance_score for m in type_metrics) / len(type_metrics)
                }
        
        return type_analysis

    def _analyze_by_platform(self, metrics: List[ContentMetrics]) -> Dict[str, Any]:
        """Analyze performance by platform."""
        platform_analysis = {}
        platforms = set(m.platform for m in metrics)
        
        for platform in platforms:
            platform_metrics = [m for m in metrics if m.platform == platform]
            if platform_metrics:
                platform_analysis[platform] = {
                    'count': len(platform_metrics),
                    'avg_views': sum(m.views for m in platform_metrics) / len(platform_metrics),
                    'avg_engagement_rate': sum(m.engagement_rate for m in platform_metrics) / len(platform_metrics),
                    'total_reach': sum(m.reach for m in platform_metrics)
                }
        
        return platform_analysis

    async def _generate_optimization_insights(self, metrics: List[ContentMetrics]) -> List[str]:
        """Generate content optimization insights."""
        insights = []
        
        if not metrics:
            return ["No content data available for analysis"]
        
        # Best performing content type
        type_performance = {}
        for metric in metrics:
            content_type = metric.content_type.value
            if content_type not in type_performance:
                type_performance[content_type] = []
            type_performance[content_type].append(metric.performance_score)
        
        best_type = max(type_performance.keys(), 
                       key=lambda t: sum(type_performance[t]) / len(type_performance[t]))
        insights.append(f"Best performing content type: {best_type}")
        
        # Engagement rate insights
        avg_engagement = sum(m.engagement_rate for m in metrics) / len(metrics)
        if avg_engagement < 3.0:
            insights.append("Overall engagement rate is low - consider improving content quality")
        elif avg_engagement > 8.0:
            insights.append("Excellent engagement rate - scale successful content strategies")
        
        return insights

    def _analyze_content_trends(self, metrics: List[ContentMetrics]) -> Dict[str, Any]:
        """Analyze content performance trends."""
        # Group by week for trend analysis
        weekly_performance = {}
        for metric in metrics:
            week = metric.publish_date.isocalendar()[1]  # Week number
            if week not in weekly_performance:
                weekly_performance[week] = []
            weekly_performance[week].append(metric.performance_score)
        
        # Calculate weekly averages
        weekly_avg = {week: sum(scores) / len(scores) 
                     for week, scores in weekly_performance.items()}
        
        return {
            'weekly_performance': weekly_avg,
            'trending_up': len([w for w in weekly_avg.values() if w > 70]) > len(weekly_avg) // 2,
            'performance_volatility': max(weekly_avg.values()) - min(weekly_avg.values()) if weekly_avg else 0
        }