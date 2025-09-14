"""Content Performance Workflow - Advanced content performance analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
"""

import asyncio
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics


class ContentType(Enum):
    """ContentType class implementation"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    CAROUSEL = "carousel"
    STORY = "story"
    LIVE = "live"
    REEL = "reel"


@dataclass
class ContentMetrics:
    """ContentMetrics: class implementation"""
    content_id: str
    content_type: ContentType
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    saves: int = 0
    engagement_rate: float = 0.0
    viral_score: float = 0.0
    quality_score: float = 0.0
    performance_rank: int = 0


@dataclass
class PerformanceReport:
    """PerformanceReport: class implementation"""
    user_id: str
    content_metrics: List[ContentMetrics]
    top_performers: List[ContentMetrics]
    insights: List[str]
    recommendations: List[str]
    analysis_timestamp: datetime


class ContentPerformanceWorkflow:
    """Content performance analysis workflow."""
    
    async def analyze_content_performance(
        self,
        user_id: str,
        content_ids: List[str],
        time_period: int = 30
    ) -> PerformanceReport:
        """Analyze performance of content pieces."""
        
        metrics = []
        for content_id in content_ids:
            # Simulate content performance data
            content_type = list(ContentType)[hash(content_id) % len(ContentType)]
            views = hash(f"{content_id}_views") % 10000
            likes = int(views * 0.05)
            shares = int(views * 0.01)
            comments = int(views * 0.02)
            saves = int(views * 0.008)
            
            engagement_rate = (likes + shares + comments + saves) / max(views, 1)
            viral_score = shares / max(views, 1) * 100
            quality_score = min(10, engagement_rate * 20)
            
            metric = ContentMetrics(
                content_id=content_id,
                content_type=content_type,
                views=views,
                likes=likes,
                shares=shares,
                comments=comments,
                saves=saves,
                engagement_rate=engagement_rate,
                viral_score=viral_score,
                quality_score=quality_score
            )
            metrics.append(metric)
        
        # Rank content by performance
        metrics.sort(key=lambda x: x.engagement_rate, reverse=True)
        for i, metric in enumerate(metrics):
            metric.performance_rank = i + 1
        
        top_performers = metrics[:5]
        
        insights = await self._generate_insights(metrics)
        recommendations = await self._generate_recommendations(metrics)
        
        return PerformanceReport(
            user_id=user_id,
            content_metrics=metrics,
            top_performers=top_performers,
            insights=insights,
            recommendations=recommendations,
            analysis_timestamp=datetime.utcnow()
        )
    
    async def get_user_analytics(
        self,
        user_id: str,
        time_period: int = 30
    ) -> Dict[str, Any]:
        """Get user content analytics summary."""
        
        # Simulate user content data
        content_count = hash(f"{user_id}_content") % 50 + 10
        total_views = hash(f"{user_id}_views") % 100000
        avg_engagement = (hash(f"{user_id}_engagement") % 100) / 1000
        
        return {
            "user_id": user_id,
            "time_period_days": time_period,
            "total_content_pieces": content_count,
            "total_views": total_views,
            "average_engagement_rate": avg_engagement,
            "top_content_type": "video",
            "performance_trend": "increasing"
        }
    
    async def _generate_insights(self, metrics: List[ContentMetrics]) -> List[str]:
        """Generate performance insights."""
        
        insights = []
        
        if metrics:
            avg_engagement = statistics.mean([m.engagement_rate for m in metrics])
            if avg_engagement > 0.05:
                insights.append("🎉 Excellent average engagement rate across content!")
            
            # Content type analysis
            type_performance = {}
            for metric in metrics:
                if metric.content_type not in type_performance:
                    type_performance[metric.content_type] = []
                type_performance[metric.content_type].append(metric.engagement_rate)
            
            best_type = max(type_performance.keys(), 
                          key=lambda t: statistics.mean(type_performance[t]))
            insights.append(f"📊 {best_type.value} content performs best for you.")
        
        return insights
    
    async def _generate_recommendations(self, metrics: List[ContentMetrics]) -> List[str]:
        """Generate content recommendations."""
        
        recommendations = []
        
        if metrics:
            top_performer = metrics[0]
            recommendations.append(f"🚀 Replicate success of your top content ({top_performer.content_id})")
            
            # Low performers
            low_performers = [m for m in metrics if m.engagement_rate < 0.02]
            if len(low_performers) > len(metrics) * 0.3:
                recommendations.append("⚠️ 30%+ of content is underperforming. Review content strategy.")
        
        return recommendations


# Export main classes
__all__ = ['ContentPerformanceWorkflow', 'ContentMetrics', 'PerformanceReport', 'ContentType']