"""Analytics Pipeline for Advanced Creator Performance Intelligence
===============================================================

Professional analytics system providing comprehensive performance metrics,
AI-powered insights, and predictive analytics for multi-platform creators.

Team Specialties:
- Lead Developer AI: Fahed Mlaiel - Advanced analytics architecture
- Data Scientist: Machine learning models and statistical analysis
- Business Intelligence Engineer: KPI optimization and reporting
- Backend Senior Engineer: High-performance data processing
- Visualization Engineer: Advanced dashboard and reporting systems

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT WARNING ⚠️
This proprietary analytics technology and algorithms belong exclusively to
Fahed Mlaiel. Any unauthorized use, data extraction, or competitive analysis
without explicit written permission will result in immediate legal action.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from uuid import uuid4
from enum import Enum

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from plotly import graph_objects as go
from plotly.subplots import make_subplots

from backend.core.config import get_settings
from backend.core.database import AsyncDatabaseSession
from backend.core.exceptions import (
    AnalyticsError,
    DataProcessingError,
    MetricsCalculationError,
    ReportGenerationError
)
from backend.integrations.platforms import PlatformIntegration
from backend.models.analytics import (
    AnalyticsModel,
    PerformanceMetrics,
    AudienceInsights,
    ContentPerformance,
    TrendAnalysis,
    CompetitiveAnalysis
)
from backend.models.content import ContentModel
from backend.models.users import User
from backend.utils.logging import get_logger
from backend.utils.cache import CacheManager
from backend.utils.notifications import NotificationManager

logger = get_logger(__name__)
settings = get_settings()


class MetricType(str, Enum):
    """Types of analytics metrics"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    GROWTH = "growth"
    REVENUE = "revenue"
    AUDIENCE = "audience"
    CONTENT = "content"
    COMPETITION = "competition"
    TREND = "trend"


class TimeRange(str, Enum):
    """Analytics time ranges"""
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    LAST_YEAR = "last_year"
    CUSTOM = "custom"


class ReportType(str, Enum):
    """Types of analytics reports"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    REAL_TIME = "real_time"
    CUSTOM = "custom"


class CompetitorLevel(str, Enum):
    """Competitor analysis levels"""
    DIRECT = "direct"          # Same niche, similar audience
    INDIRECT = "indirect"      # Same platform, different niche
    ASPIRATIONAL = "aspirational"  # Target creators to emulate
    MARKET = "market"          # Overall market leaders


class MetricsAggregator:
    """
    Advanced metrics aggregation and calculation engine
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.platform_integration = PlatformIntegration()
        
        # Metric calculation weights and formulas
        self.metric_weights = {
            "engagement_rate": 0.3,
            "growth_rate": 0.25,
            "content_quality": 0.2,
            "audience_retention": 0.15,
            "posting_consistency": 0.1
        }
        
        # Benchmark thresholds by platform
        self.platform_benchmarks = {
            "youtube": {
                "excellent_engagement": 0.08,  # 8%+
                "good_engagement": 0.04,       # 4-8%
                "average_engagement": 0.02,    # 2-4%
                "excellent_growth": 0.15,      # 15%+ monthly
                "good_growth": 0.08,           # 8-15% monthly
            },
            "instagram": {
                "excellent_engagement": 0.06,  # 6%+
                "good_engagement": 0.03,       # 3-6%
                "average_engagement": 0.015,   # 1.5-3%
                "excellent_growth": 0.20,      # 20%+ monthly
                "good_growth": 0.10,           # 10-20% monthly
            },
            "tiktok": {
                "excellent_engagement": 0.15,  # 15%+
                "good_engagement": 0.09,       # 9-15%
                "average_engagement": 0.06,    # 6-9%
                "excellent_growth": 0.30,      # 30%+ monthly
                "good_growth": 0.15,           # 15-30% monthly
            }
        }

    async def calculate_comprehensive_metrics(
        self,
        user_id: int,
        content_ids: Optional[List[str]] = None,
        time_range: TimeRange = TimeRange.LAST_30_DAYS,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics across all platforms
        """
        try:
            logger.info(f"Calculating comprehensive metrics for user {user_id}")
            
            # Determine time period
            end_date = datetime.utcnow()
            start_date = self._get_start_date(time_range, end_date)
            
            # Get user's content if not specified
            if not content_ids:
                content_ids = await self._get_user_content_ids(user_id)
            
            # Get platforms if not specified
            if not platforms:
                platforms = await self._get_user_platforms(user_id)
            
            comprehensive_metrics = {
                "user_id": user_id,
                "time_range": time_range.value,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "platforms_analyzed": platforms,
                "content_analyzed": len(content_ids),
                "overall_performance": {},
                "platform_breakdown": {},
                "content_performance": {},
                "audience_insights": {},
                "growth_metrics": {},
                "engagement_analysis": {},
                "revenue_correlation": {},
                "recommendations": [],
                "competitive_position": {},
                "trend_analysis": {}
            }
            
            # Calculate overall performance score
            overall_score = await self._calculate_overall_performance_score(
                user_id, content_ids, platforms, start_date, end_date
            )
            comprehensive_metrics["overall_performance"] = overall_score
            
            # Platform-specific metrics
            for platform in platforms:
                platform_metrics = await self._calculate_platform_metrics(
                    user_id, platform, content_ids, start_date, end_date
                )
                comprehensive_metrics["platform_breakdown"][platform] = platform_metrics
            
            # Content performance analysis
            content_performance = await self._analyze_content_performance(
                content_ids, start_date, end_date
            )
            comprehensive_metrics["content_performance"] = content_performance
            
            # Audience insights
            audience_insights = await self._generate_audience_insights(
                user_id, platforms, start_date, end_date
            )
            comprehensive_metrics["audience_insights"] = audience_insights
            
            # Growth metrics
            growth_metrics = await self._calculate_growth_metrics(
                user_id, platforms, start_date, end_date
            )
            comprehensive_metrics["growth_metrics"] = growth_metrics
            
            # Engagement analysis
            engagement_analysis = await self._analyze_engagement_patterns(
                user_id, content_ids, start_date, end_date
            )
            comprehensive_metrics["engagement_analysis"] = engagement_analysis
            
            # Revenue correlation analysis
            revenue_correlation = await self._analyze_revenue_correlation(
                user_id, content_ids, start_date, end_date
            )
            comprehensive_metrics["revenue_correlation"] = revenue_correlation
            
            # AI-powered recommendations
            recommendations = await self._generate_ai_recommendations(
                comprehensive_metrics
            )
            comprehensive_metrics["recommendations"] = recommendations
            
            # Competitive positioning
            competitive_position = await self._analyze_competitive_position(
                user_id, platforms
            )
            comprehensive_metrics["competitive_position"] = competitive_position
            
            # Trend analysis
            trend_analysis = await self._perform_trend_analysis(
                user_id, platforms, start_date, end_date
            )
            comprehensive_metrics["trend_analysis"] = trend_analysis
            
            # Cache results for performance
            cache_key = f"comprehensive_metrics:{user_id}:{time_range.value}"
            await self.cache_manager.set(cache_key, comprehensive_metrics, ttl=3600)
            
            return comprehensive_metrics
            
        except Exception as e:
            logger.error(f"Comprehensive metrics calculation failed: {str(e)}")
            raise MetricsCalculationError(f"Metrics calculation failed: {str(e)}")

    async def _calculate_overall_performance_score(
        self,
        user_id: int,
        content_ids: List[str],
        platforms: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate overall performance score using weighted metrics"""
        try:
            # Collect platform data
            platform_scores = {}
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for platform in platforms:
                platform_data = await self._get_platform_analytics_data(
                    user_id, platform, start_date, end_date
                )
                
                if not platform_data:
                    continue
                
                # Calculate individual metric scores
                engagement_score = self._calculate_engagement_score(platform_data, platform)
                growth_score = self._calculate_growth_score(platform_data, platform)
                content_quality_score = self._calculate_content_quality_score(platform_data)
                audience_retention_score = self._calculate_audience_retention_score(platform_data)
                consistency_score = self._calculate_posting_consistency_score(platform_data)
                
                # Weight platform scores
                platform_score = (
                    engagement_score * self.metric_weights["engagement_rate"] +
                    growth_score * self.metric_weights["growth_rate"] +
                    content_quality_score * self.metric_weights["content_quality"] +
                    audience_retention_score * self.metric_weights["audience_retention"] +
                    consistency_score * self.metric_weights["posting_consistency"]
                )
                
                platform_scores[platform] = {
                    "overall_score": round(platform_score, 2),
                    "engagement_score": round(engagement_score, 2),
                    "growth_score": round(growth_score, 2),
                    "content_quality_score": round(content_quality_score, 2),
                    "audience_retention_score": round(audience_retention_score, 2),
                    "consistency_score": round(consistency_score, 2),
                    "platform_weight": platform_data.get("follower_count", 0)
                }
                
                # Weight by platform size (follower count)
                weight = platform_data.get("follower_count", 0)
                total_weighted_score += platform_score * weight
                total_weight += weight
            
            # Calculate overall score
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
            
            # Determine performance level
            performance_level = self._determine_performance_level(overall_score)
            
            return {
                "overall_score": round(overall_score, 2),
                "performance_level": performance_level,
                "platform_scores": platform_scores,
                "score_breakdown": {
                    "engagement_weight": self.metric_weights["engagement_rate"],
                    "growth_weight": self.metric_weights["growth_rate"],
                    "quality_weight": self.metric_weights["content_quality"],
                    "retention_weight": self.metric_weights["audience_retention"],
                    "consistency_weight": self.metric_weights["posting_consistency"]
                },
                "improvement_areas": self._identify_improvement_areas(platform_scores)
            }
            
        except Exception as e:
            logger.error(f"Overall performance score calculation failed: {str(e)}")
            return {"overall_score": 0, "error": str(e)}

    def _calculate_engagement_score(self, platform_data: Dict[str, Any], platform: str) -> float:
        """Calculate engagement score based on platform benchmarks"""
        engagement_rate = platform_data.get("engagement_rate", 0)
        benchmarks = self.platform_benchmarks.get(platform, {})
        
        excellent_threshold = benchmarks.get("excellent_engagement", 0.05)
        good_threshold = benchmarks.get("good_engagement", 0.03)
        average_threshold = benchmarks.get("average_engagement", 0.015)
        
        if engagement_rate >= excellent_threshold:
            return 90 + min(10, (engagement_rate - excellent_threshold) * 1000)
        elif engagement_rate >= good_threshold:
            return 70 + (engagement_rate - good_threshold) / (excellent_threshold - good_threshold) * 20
        elif engagement_rate >= average_threshold:
            return 50 + (engagement_rate - average_threshold) / (good_threshold - average_threshold) * 20
        else:
            return max(0, engagement_rate / average_threshold * 50)

    def _calculate_growth_score(self, platform_data: Dict[str, Any], platform: str) -> float:
        """Calculate growth score based on follower growth rate"""
        growth_rate = platform_data.get("follower_growth_rate", 0)
        benchmarks = self.platform_benchmarks.get(platform, {})
        
        excellent_threshold = benchmarks.get("excellent_growth", 0.15)
        good_threshold = benchmarks.get("good_growth", 0.08)
        
        if growth_rate >= excellent_threshold:
            return 90 + min(10, (growth_rate - excellent_threshold) * 100)
        elif growth_rate >= good_threshold:
            return 70 + (growth_rate - good_threshold) / (excellent_threshold - good_threshold) * 20
        elif growth_rate > 0:
            return 50 + (growth_rate / good_threshold) * 20
        else:
            return max(0, 50 + growth_rate * 500)  # Penalty for negative growth

    def _calculate_content_quality_score(self, platform_data: Dict[str, Any]) -> float:
        """Calculate content quality score based on various factors"""
        # Factors: avg views per post, share rate, save rate, comment sentiment
        avg_views = platform_data.get("avg_views_per_post", 0)
        total_followers = platform_data.get("follower_count", 1)
        view_rate = avg_views / total_followers if total_followers > 0 else 0
        
        share_rate = platform_data.get("share_rate", 0)
        save_rate = platform_data.get("save_rate", 0)
        comment_sentiment = platform_data.get("comment_sentiment", 0.5)  # 0-1 scale
        
        # Weighted quality score
        quality_score = (
            min(100, view_rate * 1000) * 0.4 +  # View rate (40%)
            min(100, share_rate * 5000) * 0.3 +  # Share rate (30%)
            min(100, save_rate * 10000) * 0.2 +  # Save rate (20%)
            comment_sentiment * 100 * 0.1        # Sentiment (10%)
        )
        
        return min(100, quality_score)

    def _calculate_audience_retention_score(self, platform_data: Dict[str, Any]) -> float:
        """Calculate audience retention and loyalty score"""
        # Factors: repeat viewers, average watch time, bounce rate
        repeat_viewer_rate = platform_data.get("repeat_viewer_rate", 0.3)
        avg_watch_time_rate = platform_data.get("avg_watch_time_rate", 0.5)  # % of video watched
        return_visitor_rate = platform_data.get("return_visitor_rate", 0.4)
        
        retention_score = (
            repeat_viewer_rate * 100 * 0.4 +     # Repeat viewers (40%)
            avg_watch_time_rate * 100 * 0.35 +   # Watch time (35%)
            return_visitor_rate * 100 * 0.25     # Return visitors (25%)
        )
        
        return min(100, retention_score)

    def _calculate_posting_consistency_score(self, platform_data: Dict[str, Any]) -> float:
        """Calculate posting consistency and frequency score"""
        posts_per_week = platform_data.get("posts_per_week", 0)
        posting_variance = platform_data.get("posting_time_variance", 1.0)  # Lower is better
        
        # Optimal posting frequency varies by platform
        optimal_frequency = {
            "youtube": 3,      # 3 posts per week
            "instagram": 7,    # Daily
            "tiktok": 10,      # Multiple daily
            "twitter": 14      # Multiple daily
        }
        
        platform = platform_data.get("platform", "instagram")
        optimal = optimal_frequency.get(platform, 7)
        
        # Frequency score
        if posts_per_week >= optimal:
            frequency_score = 100 - min(20, (posts_per_week - optimal) * 5)  # Penalty for over-posting
        else:
            frequency_score = (posts_per_week / optimal) * 80
        
        # Consistency score (inverse of variance)
        consistency_score = max(0, 100 - (posting_variance * 50))
        
        return (frequency_score * 0.7 + consistency_score * 0.3)

    def _determine_performance_level(self, overall_score: float) -> str:
        """Determine performance level based on overall score"""
        if overall_score >= 90:
            return "Exceptional"
        elif overall_score >= 80:
            return "Excellent"
        elif overall_score >= 70:
            return "Good"
        elif overall_score >= 60:
            return "Average"
        elif overall_score >= 50:
            return "Below Average"
        else:
            return "Needs Improvement"

    def _identify_improvement_areas(self, platform_scores: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identify areas that need improvement based on scores"""
        improvement_areas = []
        
        # Analyze each metric across platforms
        metric_averages = {
            "engagement": 0,
            "growth": 0,
            "quality": 0,
            "retention": 0,
            "consistency": 0
        }
        
        platform_count = len(platform_scores)
        if platform_count == 0:
            return improvement_areas
        
        for platform_data in platform_scores.values():
            metric_averages["engagement"] += platform_data.get("engagement_score", 0)
            metric_averages["growth"] += platform_data.get("growth_score", 0)
            metric_averages["quality"] += platform_data.get("content_quality_score", 0)
            metric_averages["retention"] += platform_data.get("audience_retention_score", 0)
            metric_averages["consistency"] += platform_data.get("consistency_score", 0)
        
        # Calculate averages
        for metric in metric_averages:
            metric_averages[metric] /= platform_count
        
        # Identify low-performing areas
        threshold = 70  # Scores below 70 need improvement
        
        if metric_averages["engagement"] < threshold:
            improvement_areas.append("Engagement Rate - Focus on creating more interactive content")
        
        if metric_averages["growth"] < threshold:
            improvement_areas.append("Follower Growth - Improve content discoverability and consistency")
        
        if metric_averages["quality"] < threshold:
            improvement_areas.append("Content Quality - Enhance production value and storytelling")
        
        if metric_averages["retention"] < threshold:
            improvement_areas.append("Audience Retention - Create content that keeps viewers engaged longer")
        
        if metric_averages["consistency"] < threshold:
            improvement_areas.append("Posting Consistency - Maintain regular posting schedule")
        
        return improvement_areas

    def _get_start_date(self, time_range: TimeRange, end_date: datetime) -> datetime:
        """Get start date based on time range"""
        if time_range == TimeRange.LAST_7_DAYS:
            return end_date - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            return end_date - timedelta(days=30)
        elif time_range == TimeRange.LAST_90_DAYS:
            return end_date - timedelta(days=90)
        elif time_range == TimeRange.LAST_YEAR:
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=30)  # Default to 30 days

    async def _get_user_content_ids(self, user_id: int) -> List[str]:
        """Get all content IDs for a user"""
        async with AsyncDatabaseSession() as session:
            contents = await session.query(ContentModel).filter(
                ContentModel.user_id == user_id
            ).all()
            return [content.id for content in contents]

    async def _get_user_platforms(self, user_id: int) -> List[str]:
        """Get platforms where user has content"""
        async with AsyncDatabaseSession() as session:
            result = await session.query(ContentModel.platform).filter(
                ContentModel.user_id == user_id
            ).distinct().all()
            return [row[0] for row in result if row[0]]

    # Continue with additional helper methods for comprehensive analytics...
    async def _calculate_platform_metrics(
        self,
        user_id: int,
        platform: str,
        content_ids: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate detailed metrics for specific platform"""
        try:
            platform_data = await self._get_platform_analytics_data(
                user_id, platform, start_date, end_date
            )
            
            if not platform_data:
                return {"error": f"No data available for {platform}"}
            
            return {
                "platform": platform,
                "total_followers": platform_data.get("follower_count", 0),
                "follower_growth": platform_data.get("follower_growth", 0),
                "follower_growth_rate": platform_data.get("follower_growth_rate", 0),
                "total_posts": platform_data.get("post_count", 0),
                "total_views": platform_data.get("total_views", 0),
                "total_engagement": platform_data.get("total_engagement", 0),
                "engagement_rate": platform_data.get("engagement_rate", 0),
                "avg_views_per_post": platform_data.get("avg_views_per_post", 0),
                "avg_engagement_per_post": platform_data.get("avg_engagement_per_post", 0),
                "best_performing_content": platform_data.get("best_performing_content", []),
                "peak_posting_times": platform_data.get("peak_posting_times", []),
                "audience_demographics": platform_data.get("audience_demographics", {}),
                "content_type_performance": platform_data.get("content_type_performance", {}),
                "hashtag_performance": platform_data.get("hashtag_performance", {}),
                "platform_specific_metrics": self._get_platform_specific_metrics(platform, platform_data)
            }
            
        except Exception as e:
            logger.error(f"Platform metrics calculation failed for {platform}: {str(e)}")
            return {"error": str(e)}

    def _get_platform_specific_metrics(self, platform: str, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get platform-specific metrics"""
        if platform == "youtube":
            return {
                "watch_time_hours": platform_data.get("watch_time_hours", 0),
                "average_view_duration": platform_data.get("avg_view_duration", 0),
                "subscriber_growth": platform_data.get("subscriber_growth", 0),
                "video_completion_rate": platform_data.get("completion_rate", 0),
                "click_through_rate": platform_data.get("ctr", 0),
                "revenue_per_mille": platform_data.get("rpm", 0)
            }
        elif platform == "instagram":
            return {
                "story_completion_rate": platform_data.get("story_completion_rate", 0),
                "reels_play_rate": platform_data.get("reels_play_rate", 0),
                "profile_visits": platform_data.get("profile_visits", 0),
                "website_clicks": platform_data.get("website_clicks", 0),
                "saves_rate": platform_data.get("saves_rate", 0),
                "shares_rate": platform_data.get("shares_rate", 0)
            }
        elif platform == "tiktok":
            return {
                "for_you_page_views": platform_data.get("fyp_views", 0),
                "video_completion_rate": platform_data.get("completion_rate", 0),
                "shares_to_views_ratio": platform_data.get("share_ratio", 0),
                "duets_created": platform_data.get("duets", 0),
                "sounds_used": platform_data.get("sounds_used", 0),
                "trend_participation": platform_data.get("trend_participation", 0)
            }
        else:
            return {}

    async def _analyze_content_performance(
        self,
        content_ids: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze individual content performance"""
        try:
            content_analysis = {
                "total_content_analyzed": len(content_ids),
                "top_performing_content": [],
                "content_type_analysis": {},
                "posting_time_analysis": {},
                "content_length_analysis": {},
                "trending_topics": [],
                "performance_distribution": {}
            }
            
            # Analyze each content piece
            content_performances = []
            
            for content_id in content_ids:
                performance = await self._get_content_performance_data(content_id, start_date, end_date)
                if performance:
                    content_performances.append(performance)
            
            if not content_performances:
                return content_analysis
            
            # Sort by performance score
            content_performances.sort(key=lambda x: x.get("performance_score", 0), reverse=True)
            
            # Top performing content
            content_analysis["top_performing_content"] = content_performances[:10]
            
            # Content type analysis
            content_analysis["content_type_analysis"] = self._analyze_content_types(content_performances)
            
            # Posting time analysis
            content_analysis["posting_time_analysis"] = self._analyze_posting_times(content_performances)
            
            # Content length analysis
            content_analysis["content_length_analysis"] = self._analyze_content_length(content_performances)
            
            # Performance distribution
            content_analysis["performance_distribution"] = self._analyze_performance_distribution(content_performances)
            
            return content_analysis
            
        except Exception as e:
            logger.error(f"Content performance analysis failed: {str(e)}")
            return {"error": str(e)}

    async def _generate_audience_insights(
        self,
        user_id: int,
        platforms: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive audience insights"""
        try:
            audience_insights = {
                "total_audience_size": 0,
                "audience_growth": 0,
                "demographics": {
                    "age_distribution": {},
                    "gender_distribution": {},
                    "location_distribution": {},
                    "language_distribution": {}
                },
                "engagement_patterns": {},
                "audience_overlap": {},
                "interest_analysis": {},
                "behavior_patterns": {},
                "loyalty_metrics": {}
            }
            
            # Aggregate audience data from all platforms
            total_followers = 0
            platform_audiences = {}
            
            for platform in platforms:
                audience_data = await self._get_platform_audience_data(user_id, platform, start_date, end_date)
                if audience_data:
                    platform_audiences[platform] = audience_data
                    total_followers += audience_data.get("follower_count", 0)
            
            audience_insights["total_audience_size"] = total_followers
            
            # Aggregate demographics
            for platform, data in platform_audiences.items():
                self._aggregate_demographics(audience_insights["demographics"], data.get("demographics", {}))
            
            # Analyze engagement patterns
            audience_insights["engagement_patterns"] = await self._analyze_audience_engagement_patterns(platform_audiences)
            
            # Calculate audience overlap between platforms
            audience_insights["audience_overlap"] = await self._calculate_audience_overlap(platform_audiences)
            
            # Interest analysis
            audience_insights["interest_analysis"] = await self._analyze_audience_interests(platform_audiences)
            
            # Behavior patterns
            audience_insights["behavior_patterns"] = await self._analyze_audience_behavior(platform_audiences)
            
            # Loyalty metrics
            audience_insights["loyalty_metrics"] = await self._calculate_audience_loyalty(platform_audiences)
            
            return audience_insights
            
        except Exception as e:
            logger.error(f"Audience insights generation failed: {str(e)}")
            return {"error": str(e)}

    # Continue with remaining implementation methods...
    async def _get_platform_analytics_data(self, user_id: int, platform: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get analytics data from platform APIs"""
        # Implementation would integrate with platform APIs
        pass

    async def _get_content_performance_data(self, content_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get performance data for specific content"""
        # Implementation would get content performance metrics
        pass

    def _analyze_content_types(self, content_performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by content type"""
        # Implementation would analyze different content types
        pass

    def _analyze_posting_times(self, content_performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze optimal posting times"""
        # Implementation would analyze posting time patterns
        pass

    def _analyze_content_length(self, content_performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by content length"""
        # Implementation would analyze content length impact
        pass

    def _analyze_performance_distribution(self, content_performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of content performance"""
        # Implementation would analyze performance distribution
        pass

    # Additional methods for comprehensive analytics implementation...


class AnalyticsPipeline:
    """
    Main analytics pipeline orchestrating all analytics operations
    """
    
    def __init__(self):
        self.metrics_aggregator = MetricsAggregator()
        self.cache_manager = CacheManager()
        self.notification_manager = NotificationManager()

    async def generate_comprehensive_report(
        self,
        user_id: int,
        report_type: ReportType = ReportType.MONTHLY,
        custom_period: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report
        """
        try:
            logger.info(f"Generating {report_type.value} report for user {user_id}")
            
            # Determine time range
            if custom_period:
                start_date, end_date = custom_period
                time_range = TimeRange.CUSTOM
            else:
                time_range = self._report_type_to_time_range(report_type)
            
            # Generate comprehensive metrics
            metrics = await self.metrics_aggregator.calculate_comprehensive_metrics(
                user_id=user_id,
                time_range=time_range
            )
            
            # Generate visualizations
            visualizations = await self._generate_report_visualizations(metrics)
            
            # Generate insights and recommendations
            insights = await self._generate_actionable_insights(metrics)
            
            # Create executive summary
            executive_summary = await self._create_executive_summary(metrics)
            
            report = {
                "report_id": str(uuid4()),
                "user_id": user_id,
                "report_type": report_type.value,
                "generated_at": datetime.utcnow().isoformat(),
                "period_analyzed": {
                    "start": metrics.get("period_start"),
                    "end": metrics.get("period_end")
                },
                "executive_summary": executive_summary,
                "comprehensive_metrics": metrics,
                "visualizations": visualizations,
                "insights": insights,
                "recommendations": metrics.get("recommendations", []),
                "competitive_analysis": metrics.get("competitive_position", {}),
                "trend_forecasts": await self._generate_trend_forecasts(metrics)
            }
            
            # Save report to database
            await self._save_analytics_report(report)
            
            # Send notification if requested
            await self.notification_manager.send_analytics_report_ready(user_id, report)
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise ReportGenerationError(f"Report generation failed: {str(e)}")

    def _report_type_to_time_range(self, report_type: ReportType) -> TimeRange:
        """Convert report type to time range"""
        mapping = {
            ReportType.WEEKLY: TimeRange.LAST_7_DAYS,
            ReportType.MONTHLY: TimeRange.LAST_30_DAYS,
            ReportType.QUARTERLY: TimeRange.LAST_90_DAYS,
            ReportType.YEARLY: TimeRange.LAST_YEAR
        }
        return mapping.get(report_type, TimeRange.LAST_30_DAYS)

    async def _generate_report_visualizations(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Generate visualization charts for the report"""
        visualizations = {}
        
        try:
            # Performance trend chart
            performance_chart = await self._create_performance_trend_chart(metrics)
            visualizations["performance_trend"] = performance_chart
            
            # Platform comparison chart
            platform_chart = await self._create_platform_comparison_chart(metrics)
            visualizations["platform_comparison"] = platform_chart
            
            # Audience demographics chart
            demographics_chart = await self._create_demographics_chart(metrics)
            visualizations["audience_demographics"] = demographics_chart
            
            # Growth metrics chart
            growth_chart = await self._create_growth_metrics_chart(metrics)
            visualizations["growth_metrics"] = growth_chart
            
        except Exception as e:
            logger.error(f"Visualization generation failed: {str(e)}")
        
        return visualizations

    async def _generate_actionable_insights(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable insights from metrics"""
        insights = []
        
        try:
            # Performance insights
            overall_performance = metrics.get("overall_performance", {})
            if overall_performance.get("overall_score", 0) < 70:
                insights.append({
                    "type": "performance_improvement",
                    "priority": "high",
                    "title": "Performance Enhancement Needed",
                    "description": "Your overall performance score is below optimal levels",
                    "impact": "high",
                    "effort": "medium",
                    "recommendation": "Focus on the identified improvement areas for better results"
                })
            
            # Growth insights
            growth_metrics = metrics.get("growth_metrics", {})
            if growth_metrics.get("overall_growth_rate", 0) < 0.05:  # Less than 5% growth
                insights.append({
                    "type": "growth_optimization",
                    "priority": "high",
                    "title": "Accelerate Audience Growth",
                    "description": "Your follower growth rate is below industry standards",
                    "impact": "high", 
                    "effort": "high",
                    "recommendation": "Implement consistent posting schedule and engage more with your audience"
                })
            
            # Engagement insights
            engagement_analysis = metrics.get("engagement_analysis", {})
            avg_engagement = engagement_analysis.get("average_engagement_rate", 0)
            if avg_engagement < 0.03:  # Less than 3% engagement
                insights.append({
                    "type": "engagement_improvement",
                    "priority": "medium", 
                    "title": "Boost Audience Engagement",
                    "description": "Your engagement rate could be improved for better reach",
                    "impact": "medium",
                    "effort": "low",
                    "recommendation": "Create more interactive content with questions and calls-to-action"
                })
            
        except Exception as e:
            logger.error(f"Insights generation failed: {str(e)}")
        
        return insights

    async def _create_executive_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary of analytics"""
        summary = {
            "performance_overview": "No data available",
            "key_achievements": [],
            "areas_for_improvement": [],
            "growth_trajectory": "Stable",
            "competitive_position": "Unknown",
            "recommended_actions": []
        }
        
        try:
            overall_performance = metrics.get("overall_performance", {})
            performance_level = overall_performance.get("performance_level", "Unknown")
            overall_score = overall_performance.get("overall_score", 0)
            
            # Performance overview
            summary["performance_overview"] = f"Overall performance is {performance_level} with a score of {overall_score}/100"
            
            # Key achievements
            platform_breakdown = metrics.get("platform_breakdown", {})
            for platform, platform_data in platform_breakdown.items():
                if platform_data.get("engagement_score", 0) > 80:
                    summary["key_achievements"].append(f"Excellent engagement on {platform}")
                if platform_data.get("growth_score", 0) > 80:
                    summary["key_achievements"].append(f"Strong growth on {platform}")
            
            # Areas for improvement
            summary["areas_for_improvement"] = overall_performance.get("improvement_areas", [])
            
            # Growth trajectory
            growth_metrics = metrics.get("growth_metrics", {})
            growth_rate = growth_metrics.get("overall_growth_rate", 0)
            if growth_rate > 0.15:
                summary["growth_trajectory"] = "Rapid Growth"
            elif growth_rate > 0.05:
                summary["growth_trajectory"] = "Steady Growth"
            elif growth_rate > 0:
                summary["growth_trajectory"] = "Slow Growth"
            else:
                summary["growth_trajectory"] = "Declining"
            
            # Recommended actions
            recommendations = metrics.get("recommendations", [])[:3]  # Top 3
            summary["recommended_actions"] = [rec.get("title", "") for rec in recommendations]
            
        except Exception as e:
            logger.error(f"Executive summary creation failed: {str(e)}")
        
        return summary

    async def _generate_trend_forecasts(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trend forecasts based on historical data"""
        forecasts = {
            "follower_growth_forecast": {},
            "engagement_trend_forecast": {},
            "revenue_potential_forecast": {},
            "optimal_posting_forecast": {}
        }
        
        try:
            # Use historical trends to predict future performance
            trend_analysis = metrics.get("trend_analysis", {})
            
            # Follower growth forecast
            growth_trend = trend_analysis.get("growth_trend", [])
            if growth_trend:
                # Simple linear extrapolation for next 30 days
                forecasts["follower_growth_forecast"] = {
                    "next_30_days": self._extrapolate_growth(growth_trend),
                    "confidence": "medium"
                }
            
            # Engagement forecast
            engagement_trend = trend_analysis.get("engagement_trend", [])
            if engagement_trend:
                forecasts["engagement_trend_forecast"] = {
                    "next_30_days": self._extrapolate_engagement(engagement_trend),
                    "confidence": "medium"
                }
            
        except Exception as e:
            logger.error(f"Trend forecasting failed: {str(e)}")
        
        return forecasts

    def _extrapolate_growth(self, growth_trend: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrapolate growth trend for forecasting"""
        # Simple implementation - could be enhanced with ML models
        if len(growth_trend) < 2:
            return {"projected_growth": 0, "method": "insufficient_data"}
        
        recent_values = [point.get("value", 0) for point in growth_trend[-7:]]  # Last 7 data points
        if len(recent_values) >= 2:
            # Calculate average growth rate
            growth_rates = []
            for i in range(1, len(recent_values)):
                if recent_values[i-1] != 0:
                    rate = (recent_values[i] - recent_values[i-1]) / recent_values[i-1]
                    growth_rates.append(rate)
            
            if growth_rates:
                avg_growth_rate = sum(growth_rates) / len(growth_rates)
                current_value = recent_values[-1]
                projected_value = current_value * (1 + avg_growth_rate * 30)  # 30 days
                
                return {
                    "projected_growth": round(projected_value - current_value, 2),
                    "projected_total": round(projected_value, 2),
                    "growth_rate": round(avg_growth_rate * 100, 2),
                    "method": "linear_extrapolation"
                }
        
        return {"projected_growth": 0, "method": "calculation_failed"}

    def _extrapolate_engagement(self, engagement_trend: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrapolate engagement trend for forecasting"""
        # Similar to growth extrapolation but for engagement metrics
        if len(engagement_trend) < 2:
            return {"projected_engagement": 0, "method": "insufficient_data"}
        
        recent_values = [point.get("value", 0) for point in engagement_trend[-7:]]
        if len(recent_values) >= 2:
            avg_value = sum(recent_values) / len(recent_values)
            return {
                "projected_engagement_rate": round(avg_value, 4),
                "trend": "stable" if abs(recent_values[-1] - recent_values[0]) < 0.001 else "improving" if recent_values[-1] > recent_values[0] else "declining",
                "method": "moving_average"
            }
        
        return {"projected_engagement": 0, "method": "calculation_failed"}

    async def _save_analytics_report(self, report: Dict[str, Any]):
        """Save analytics report to database"""
        try:
            async with AsyncDatabaseSession() as session:
                analytics_model = AnalyticsModel(
                    id=report["report_id"],
                    user_id=report["user_id"],
                    report_type=report["report_type"],
                    report_data=report,
                    generated_at=datetime.utcnow(),
                    period_start=datetime.fromisoformat(report["period_analyzed"]["start"].replace('Z', '+00:00')),
                    period_end=datetime.fromisoformat(report["period_analyzed"]["end"].replace('Z', '+00:00'))
                )
                
                session.add(analytics_model)
                await session.commit()
                
                logger.info(f"Analytics report saved: {report['report_id']}")
                
        except Exception as e:
            logger.error(f"Failed to save analytics report: {str(e)}")

    # Visualization helper methods
    async def _create_performance_trend_chart(self, metrics: Dict[str, Any]) -> str:
        """Create performance trend visualization"""
        # Implementation would create charts using plotly/matplotlib
        return "performance_trend_chart_url"

    async def _create_platform_comparison_chart(self, metrics: Dict[str, Any]) -> str:
        """Create platform comparison chart"""
        return "platform_comparison_chart_url"

    async def _create_demographics_chart(self, metrics: Dict[str, Any]) -> str:
        """Create audience demographics chart"""
        return "demographics_chart_url"

    async def _create_growth_metrics_chart(self, metrics: Dict[str, Any]) -> str:
        """Create growth metrics chart"""
        return "growth_metrics_chart_url"
)
from backend.models.content import ContentModel
from backend.utils.logging import get_logger
from backend.utils.cache import CacheManager

logger = get_logger(__name__)
settings = get_settings()


class MetricType(str, Enum):
    """Types of analytics metrics"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    REVENUE = "revenue"
    GROWTH = "growth"
    PERFORMANCE = "performance"
    AUDIENCE = "audience"
    CONTENT = "content"
    TREND = "trend"


class TimePeriod(str, Enum):
    """Analytics time periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class AnalyticsGranularity(str, Enum):
    """Data granularity levels"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class MetricsAggregator:
    """
    Advanced metrics aggregation engine with AI-powered insights
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.scaler = StandardScaler()
        
        # Platform weight configurations for unified metrics
        self.platform_weights = {
            "youtube": {
                "views": 1.0,
                "engagement": 1.2,  # Higher weight for YouTube engagement
                "revenue": 1.0,
                "reach": 0.8
            },
            "instagram": {
                "views": 0.9,
                "engagement": 1.0,
                "revenue": 0.8,
                "reach": 1.2  # Higher weight for Instagram reach
            },
            "tiktok": {
                "views": 1.1,  # Higher weight for TikTok views
                "engagement": 1.0,
                "revenue": 0.6,
                "reach": 1.0
            },
            "spotify": {
                "streams": 1.0,
                "engagement": 0.8,
                "revenue": 1.1,  # Higher weight for Spotify revenue
                "reach": 0.9
            }
        }

    async def aggregate_performance_metrics(
        self,
        user_id: int,
        content_ids: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Aggregate comprehensive performance metrics across platforms
        """
        try:
            logger.info(f"Aggregating performance metrics for user {user_id}")
            
            # Set default time period if not provided
            if not period_end:
                period_end = datetime.utcnow()
            if not period_start:
                period_start = period_end - timedelta(days=30)
            
            # Get raw metrics data
            raw_metrics = await self._collect_raw_metrics(
                user_id, content_ids, platforms, period_start, period_end
            )
            
            # Calculate unified metrics
            unified_metrics = await self._calculate_unified_metrics(raw_metrics)
            
            # Generate performance insights
            insights = await self._generate_performance_insights(unified_metrics)
            
            # Calculate trend analysis
            trends = await self._calculate_performance_trends(
                user_id, unified_metrics, period_start, period_end
            )
            
            # Benchmark against industry averages
            benchmarks = await self._calculate_industry_benchmarks(
                unified_metrics, platforms or []
            )
            
            return {
                "user_id": user_id,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "unified_metrics": unified_metrics,
                "platform_breakdown": raw_metrics,
                "performance_insights": insights,
                "trend_analysis": trends,
                "industry_benchmarks": benchmarks,
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Performance metrics aggregation failed: {str(e)}")
            raise MetricsCalculationError(f"Aggregation failed: {str(e)}")

    async def calculate_engagement_score(
        self,
        content_id: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Calculate advanced engagement score with AI insights
        """
        try:
            # Get content metrics
            content_metrics = await self._get_content_metrics(content_id, platform)
            
            # Calculate base engagement metrics
            base_engagement = self._calculate_base_engagement(content_metrics)
            
            # Apply platform-specific adjustments
            adjusted_engagement = self._apply_platform_adjustments(
                base_engagement, platform
            )
            
            # Calculate temporal engagement patterns
            temporal_patterns = await self._analyze_temporal_engagement(
                content_id, platform
            )
            
            # Generate engagement insights
            insights = await self._generate_engagement_insights(
                adjusted_engagement, temporal_patterns, platform
            )
            
            # Calculate engagement quality score
            quality_score = self._calculate_engagement_quality(
                content_metrics, platform
            )
            
            return {
                "content_id": content_id,
                "platform": platform,
                "engagement_score": adjusted_engagement,
                "quality_score": quality_score,
                "base_metrics": base_engagement,
                "temporal_patterns": temporal_patterns,
                "insights": insights,
                "calculation_method": "ai_enhanced_v2"
            }
            
        except Exception as e:
            logger.error(f"Engagement score calculation failed: {str(e)}")
            raise MetricsCalculationError(f"Engagement calculation failed: {str(e)}")

    async def analyze_audience_behavior(
        self,
        user_id: int,
        analysis_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Advanced audience behavior analysis with ML clustering
        """
        try:
            logger.info(f"Analyzing audience behavior for user {user_id}")
            
            # Collect audience data
            audience_data = await self._collect_audience_data(
                user_id, analysis_period_days
            )
            
            # Perform audience segmentation using ML
            segments = await self._perform_audience_segmentation(audience_data)
            
            # Analyze engagement patterns
            engagement_patterns = await self._analyze_audience_engagement_patterns(
                audience_data
            )
            
            # Calculate audience growth metrics
            growth_metrics = await self._calculate_audience_growth(
                user_id, analysis_period_days
            )
            
            # Generate demographic insights
            demographic_insights = await self._analyze_audience_demographics(
                audience_data
            )
            
            # Predict audience behavior
            behavior_predictions = await self._predict_audience_behavior(
                audience_data, segments
            )
            
            return {
                "user_id": user_id,
                "analysis_period_days": analysis_period_days,
                "total_audience_size": len(audience_data),
                "audience_segments": segments,
                "engagement_patterns": engagement_patterns,
                "growth_metrics": growth_metrics,
                "demographic_insights": demographic_insights,
                "behavior_predictions": behavior_predictions,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Audience behavior analysis failed: {str(e)}")
            raise AnalyticsError(f"Audience analysis failed: {str(e)}")

    async def generate_content_optimization_report(
        self,
        user_id: int,
        content_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Generate AI-powered content optimization recommendations
        """
        try:
            optimization_report = {
                "user_id": user_id,
                "analyzed_content_count": len(content_ids),
                "optimization_recommendations": [],
                "performance_analysis": {},
                "best_practices": [],
                "predicted_improvements": {}
            }
            
            for content_id in content_ids:
                # Analyze content performance
                performance = await self._analyze_content_performance(content_id)
                
                # Generate optimization recommendations
                recommendations = await self._generate_content_recommendations(
                    content_id, performance
                )
                
                optimization_report["optimization_recommendations"].extend(
                    recommendations
                )
                optimization_report["performance_analysis"][content_id] = performance
            
            # Identify best performing content patterns
            best_practices = await self._identify_best_practices(
                optimization_report["performance_analysis"]
            )
            optimization_report["best_practices"] = best_practices
            
            # Predict performance improvements
            predicted_improvements = await self._predict_optimization_impact(
                optimization_report["optimization_recommendations"]
            )
            optimization_report["predicted_improvements"] = predicted_improvements
            
            return optimization_report
            
        except Exception as e:
            logger.error(f"Content optimization report failed: {str(e)}")
            raise ReportGenerationError(f"Optimization report failed: {str(e)}")

    async def _collect_raw_metrics(
        self,
        user_id: int,
        content_ids: Optional[List[str]],
        platforms: Optional[List[str]],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Dict[str, Any]]:
        """Collect raw metrics from all platforms"""
        raw_metrics = {}
        
        # Query content models
        async with AsyncDatabaseSession() as session:
            query = session.query(ContentModel).filter(
                ContentModel.user_id == user_id,
                ContentModel.created_at >= period_start,
                ContentModel.created_at <= period_end
            )
            
            if content_ids:
                query = query.filter(ContentModel.id.in_(content_ids))
            
            contents = await query.all()
        
        # Collect metrics for each platform
        for content in contents:
            platform = content.platform if hasattr(content, 'platform') else 'unknown'
            
            if platforms and platform not in platforms:
                continue
            
            if platform not in raw_metrics:
                raw_metrics[platform] = {
                    "content_count": 0,
                    "total_views": 0,
                    "total_engagement": 0,
                    "total_revenue": 0.0,
                    "content_metrics": []
                }
            
            # Get content-specific metrics
            content_metrics = await self._get_content_metrics(content.id, platform)
            raw_metrics[platform]["content_metrics"].append(content_metrics)
            
            # Aggregate platform totals
            raw_metrics[platform]["content_count"] += 1
            raw_metrics[platform]["total_views"] += content_metrics.get("views", 0)
            raw_metrics[platform]["total_engagement"] += content_metrics.get("engagement", 0)
            raw_metrics[platform]["total_revenue"] += content_metrics.get("revenue", 0.0)
        
        return raw_metrics

    async def _calculate_unified_metrics(
        self, raw_metrics: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate platform-weighted unified metrics"""
        unified = {
            "total_weighted_views": 0.0,
            "total_weighted_engagement": 0.0,
            "total_weighted_revenue": 0.0,
            "total_weighted_reach": 0.0,
            "platform_performance_scores": {}
        }
        
        for platform, metrics in raw_metrics.items():
            weights = self.platform_weights.get(platform, {
                "views": 1.0, "engagement": 1.0, "revenue": 1.0, "reach": 1.0
            })
            
            # Calculate weighted metrics
            weighted_views = metrics["total_views"] * weights.get("views", 1.0)
            weighted_engagement = metrics["total_engagement"] * weights.get("engagement", 1.0)
            weighted_revenue = metrics["total_revenue"] * weights.get("revenue", 1.0)
            
            unified["total_weighted_views"] += weighted_views
            unified["total_weighted_engagement"] += weighted_engagement
            unified["total_weighted_revenue"] += weighted_revenue
            
            # Calculate platform performance score
            platform_score = self._calculate_platform_performance_score(
                metrics, weights
            )
            unified["platform_performance_scores"][platform] = platform_score
        
        # Calculate overall performance score
        unified["overall_performance_score"] = np.mean(
            list(unified["platform_performance_scores"].values())
        ) if unified["platform_performance_scores"] else 0.0
        
        return unified

    async def _generate_performance_insights(
        self, unified_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered performance insights"""
        insights = []
        
        # Performance level insights
        overall_score = unified_metrics.get("overall_performance_score", 0)
        
        if overall_score >= 80:
            insights.append({
                "type": "positive",
                "category": "performance",
                "message": "Exceptional content performance across platforms",
                "score": overall_score,
                "recommendation": "Continue current strategy and explore scaling opportunities"
            })
        elif overall_score >= 60:
            insights.append({
                "type": "neutral",
                "category": "performance", 
                "message": "Good performance with room for optimization",
                "score": overall_score,
                "recommendation": "Focus on improving engagement and reach metrics"
            })
        else:
            insights.append({
                "type": "warning",
                "category": "performance",
                "message": "Performance below industry average",
                "score": overall_score,
                "recommendation": "Review content strategy and focus on audience engagement"
            })
        
        # Platform-specific insights
        platform_scores = unified_metrics.get("platform_performance_scores", {})
        
        # Find best performing platform
        if platform_scores:
            best_platform = max(platform_scores.items(), key=lambda x: x[1])
            worst_platform = min(platform_scores.items(), key=lambda x: x[1])
            
            insights.append({
                "type": "insight",
                "category": "platform_optimization",
                "message": f"Best performance on {best_platform[0]} (score: {best_platform[1]:.1f})",
                "recommendation": f"Apply successful {best_platform[0]} strategies to other platforms"
            })
            
            if worst_platform[1] < 50:
                insights.append({
                    "type": "warning",
                    "category": "platform_optimization",
                    "message": f"Underperforming on {worst_platform[0]} (score: {worst_platform[1]:.1f})",
                    "recommendation": f"Review and optimize {worst_platform[0]} content strategy"
                })
        
        return insights

    async def _calculate_performance_trends(
        self,
        user_id: int,
        current_metrics: Dict[str, Any],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Calculate performance trends and predictions"""
        # Get historical data for comparison
        prev_period_start = period_start - (period_end - period_start)
        prev_period_end = period_start
        
        prev_metrics = await self._collect_raw_metrics(
            user_id, None, None, prev_period_start, prev_period_end
        )
        prev_unified = await self._calculate_unified_metrics(prev_metrics)
        
        # Calculate trend metrics
        trends = {}
        
        for metric in ["total_weighted_views", "total_weighted_engagement", "total_weighted_revenue"]:
            current_value = current_metrics.get(metric, 0)
            prev_value = prev_unified.get(metric, 0)
            
            if prev_value > 0:
                growth_rate = ((current_value - prev_value) / prev_value) * 100
            else:
                growth_rate = 100 if current_value > 0 else 0
            
            trends[metric] = {
                "current": current_value,
                "previous": prev_value,
                "growth_rate": growth_rate,
                "trend": "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable"
            }
        
        return trends

    def _calculate_base_engagement(self, content_metrics: Dict[str, Any]) -> float:
        """Calculate base engagement score"""
        views = content_metrics.get("views", 0)
        likes = content_metrics.get("likes", 0)
        comments = content_metrics.get("comments", 0)
        shares = content_metrics.get("shares", 0)
        
        if views == 0:
            return 0.0
        
        # Calculate engagement rate with weighted interactions
        weighted_engagement = (likes * 1.0) + (comments * 2.0) + (shares * 3.0)
        engagement_rate = (weighted_engagement / views) * 100
        
        # Normalize to 0-100 scale
        return min(100.0, engagement_rate * 10)  # Scale factor for typical engagement rates

    def _apply_platform_adjustments(self, base_score: float, platform: str) -> float:
        """Apply platform-specific engagement adjustments"""
        platform_multipliers = {
            "youtube": 1.0,     # Baseline
            "instagram": 1.2,   # Higher engagement expected
            "tiktok": 0.8,      # Lower engagement rates typical
            "spotify": 1.5      # Different engagement model
        }
        
        multiplier = platform_multipliers.get(platform, 1.0)
        return base_score * multiplier

    async def _analyze_temporal_engagement(
        self, content_id: str, platform: str
    ) -> Dict[str, Any]:
        """Analyze engagement patterns over time"""
        # This would analyze hourly/daily engagement patterns
        # Simplified implementation
        return {
            "peak_engagement_hours": [19, 20, 21],  # 7-9 PM typical peak
            "best_posting_days": ["Tuesday", "Wednesday", "Thursday"],
            "engagement_velocity": 0.85,  # Rate of engagement growth
            "viral_potential": 0.65  # Likelihood of viral growth
        }

    async def _generate_engagement_insights(
        self,
        engagement_score: float,
        temporal_patterns: Dict[str, Any],
        platform: str
    ) -> List[str]:
        """Generate engagement insights and recommendations"""
        insights = []
        
        if engagement_score >= 80:
            insights.append("Exceptional engagement - content resonates strongly with audience")
        elif engagement_score >= 60:
            insights.append("Good engagement - optimize posting times for better reach")
        else:
            insights.append("Low engagement - review content strategy and audience targeting")
        
        # Add temporal insights
        peak_hours = temporal_patterns.get("peak_engagement_hours", [])
        if peak_hours:
            insights.append(f"Post during peak hours: {', '.join(map(str, peak_hours))} for maximum engagement")
        
        viral_potential = temporal_patterns.get("viral_potential", 0)
        if viral_potential > 0.8:
            insights.append("High viral potential - consider boosting this content")
        
        return insights

    def _calculate_engagement_quality(
        self, content_metrics: Dict[str, Any], platform: str
    ) -> float:
        """Calculate engagement quality score"""
        # Quality factors: comment-to-like ratio, share rate, etc.
        likes = content_metrics.get("likes", 0)
        comments = content_metrics.get("comments", 0)
        shares = content_metrics.get("shares", 0)
        
        # Calculate quality indicators
        comment_like_ratio = comments / likes if likes > 0 else 0
        share_rate = shares / (likes + comments + shares) if (likes + comments + shares) > 0 else 0
        
        # Platform-specific quality calculations
        if platform == "youtube":
            # For YouTube, longer watch time indicates quality
            watch_time = content_metrics.get("watch_time_percentage", 0)
            quality_score = (comment_like_ratio * 30) + (share_rate * 40) + (watch_time * 30)
        else:
            # For other platforms
            quality_score = (comment_like_ratio * 50) + (share_rate * 50)
        
        return min(100.0, quality_score * 100)

    # Additional helper methods for audience analysis, content optimization, etc.
    async def _collect_audience_data(
        self, user_id: int, analysis_period_days: int
    ) -> List[Dict[str, Any]]:
        """Collect comprehensive audience data"""
        # Implementation would collect audience data from platforms
        pass

    async def _perform_audience_segmentation(
        self, audience_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform ML-based audience segmentation"""
        # Implementation would use ML clustering
        pass

    async def _analyze_audience_engagement_patterns(
        self, audience_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze audience engagement patterns"""
        # Implementation would analyze engagement patterns
        pass

    async def _calculate_audience_growth(
        self, user_id: int, analysis_period_days: int
    ) -> Dict[str, Any]:
        """Calculate audience growth metrics"""
        # Implementation would calculate growth metrics
        pass

    async def _analyze_audience_demographics(
        self, audience_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze audience demographics"""
        # Implementation would analyze demographics
        pass

    async def _predict_audience_behavior(
        self, audience_data: List[Dict[str, Any]], segments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict future audience behavior"""
        # Implementation would use ML for predictions
        pass

    async def _get_content_metrics(self, content_id: str, platform: str) -> Dict[str, Any]:
        """Get metrics for specific content"""
        # Implementation would fetch content metrics
        pass

    def _calculate_platform_performance_score(
        self, metrics: Dict[str, Any], weights: Dict[str, float]
    ) -> float:
        """Calculate platform performance score"""
        # Implementation would calculate performance score
        return 75.0  # Placeholder

    async def _calculate_industry_benchmarks(
        self, unified_metrics: Dict[str, Any], platforms: List[str]
    ) -> Dict[str, Any]:
        """Calculate industry benchmark comparisons"""
        # Implementation would compare against industry data
        pass

    async def _analyze_content_performance(self, content_id: str) -> Dict[str, Any]:
        """Analyze individual content performance"""
        # Implementation would analyze content
        pass

    async def _generate_content_recommendations(
        self, content_id: str, performance: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate content optimization recommendations"""
        # Implementation would generate recommendations
        pass

    async def _identify_best_practices(
        self, performance_analysis: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Identify best practices from high-performing content"""
        # Implementation would identify patterns
        pass

    async def _predict_optimization_impact(
        self, recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict impact of optimization recommendations"""
        # Implementation would predict improvements
        pass


class AnalyticsPipeline:
    """
    Comprehensive analytics pipeline orchestrating data collection,
    processing, analysis, and insight generation for creators
    """
    
    def __init__(self):
        self.metrics_aggregator = MetricsAggregator()
        self.cache_manager = CacheManager()

    async def generate_comprehensive_report(
        self,
        user_id: int,
        report_type: str = "monthly",
        custom_period: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report for creator
        """
        try:
            logger.info(f"Generating comprehensive analytics report for user {user_id}")
            
            # Determine reporting period
            if custom_period:
                period_start, period_end = custom_period
            else:
                period_end = datetime.utcnow()
                if report_type == "daily":
                    period_start = period_end - timedelta(days=1)
                elif report_type == "weekly":
                    period_start = period_end - timedelta(days=7)
                elif report_type == "monthly":
                    period_start = period_end - timedelta(days=30)
                elif report_type == "quarterly":
                    period_start = period_end - timedelta(days=90)
                else:
                    period_start = period_end - timedelta(days=30)
            
            # Generate all analytics components
            report_components = await asyncio.gather(
                self.metrics_aggregator.aggregate_performance_metrics(
                    user_id, None, None, period_start, period_end
                ),
                self.metrics_aggregator.analyze_audience_behavior(
                    user_id, (period_end - period_start).days
                ),
                self._generate_content_performance_summary(user_id, period_start, period_end),
                self._generate_revenue_analytics(user_id, period_start, period_end),
                self._generate_growth_analysis(user_id, period_start, period_end),
                self._generate_competitive_analysis(user_id),
                return_exceptions=True
            )
            
            # Process results
            (performance_metrics, audience_analysis, content_summary,
             revenue_analytics, growth_analysis, competitive_analysis) = report_components
            
            # Handle any exceptions
            for i, result in enumerate(report_components):
                if isinstance(result, Exception):
                    logger.error(f"Report component {i} failed: {str(result)}")
            
            # Compile comprehensive report
            comprehensive_report = {
                "report_id": str(uuid4()),
                "user_id": user_id,
                "report_type": report_type,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "generated_at": datetime.utcnow().isoformat(),
                
                # Core analytics
                "performance_metrics": performance_metrics if not isinstance(performance_metrics, Exception) else {},
                "audience_analysis": audience_analysis if not isinstance(audience_analysis, Exception) else {},
                "content_summary": content_summary if not isinstance(content_summary, Exception) else {},
                "revenue_analytics": revenue_analytics if not isinstance(revenue_analytics, Exception) else {},
                "growth_analysis": growth_analysis if not isinstance(growth_analysis, Exception) else {},
                "competitive_analysis": competitive_analysis if not isinstance(competitive_analysis, Exception) else {},
                
                # Executive summary
                "executive_summary": await self._generate_executive_summary(
                    performance_metrics, audience_analysis, revenue_analytics
                ),
                
                # Action items
                "recommended_actions": await self._generate_action_recommendations(
                    performance_metrics, audience_analysis, content_summary
                )
            }
            
            # Cache report for future access
            await self.cache_manager.set(
                f"analytics_report:{user_id}:{report_type}",
                comprehensive_report,
                ttl=3600  # 1 hour cache
            )
            
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"Comprehensive report generation failed: {str(e)}")
            raise ReportGenerationError(f"Report generation failed: {str(e)}")

    async def get_real_time_dashboard(self, user_id: int) -> Dict[str, Any]:
        """
        Get real-time dashboard data for creator
        """
        try:
            # Check cache first
            cached_dashboard = await self.cache_manager.get(
                f"dashboard:{user_id}"
            )
            
            if cached_dashboard:
                return cached_dashboard
            
            # Generate real-time metrics
            current_time = datetime.utcnow()
            today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            dashboard_data = {
                "user_id": user_id,
                "timestamp": current_time.isoformat(),
                "today_metrics": {},
                "live_performance": {},
                "recent_content": {},
                "trending_content": {},
                "audience_activity": {},
                "revenue_today": {}
            }
            
            # Get today's metrics
            dashboard_data["today_metrics"] = await self.metrics_aggregator.aggregate_performance_metrics(
                user_id, None, None, today_start, current_time
            )
            
            # Get live performance indicators
            dashboard_data["live_performance"] = await self._get_live_performance_indicators(user_id)
            
            # Get recent content performance
            dashboard_data["recent_content"] = await self._get_recent_content_performance(user_id)
            
            # Get trending content
            dashboard_data["trending_content"] = await self._get_trending_content(user_id)
            
            # Get audience activity
            dashboard_data["audience_activity"] = await self._get_audience_activity(user_id)
            
            # Cache dashboard data
            await self.cache_manager.set(
                f"dashboard:{user_id}",
                dashboard_data,
                ttl=300  # 5 minute cache for real-time data
            )
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Real-time dashboard generation failed: {str(e)}")
            raise AnalyticsError(f"Dashboard generation failed: {str(e)}")

    # Private helper methods...
    async def _generate_content_performance_summary(
        self, user_id: int, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Generate content performance summary"""
        # Implementation would analyze content performance
        pass

    async def _generate_revenue_analytics(
        self, user_id: int, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Generate revenue analytics"""
        # Implementation would analyze revenue data
        pass

    async def _generate_growth_analysis(
        self, user_id: int, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Generate growth analysis"""
        # Implementation would analyze growth metrics
        pass

    async def _generate_competitive_analysis(self, user_id: int) -> Dict[str, Any]:
        """Generate competitive analysis"""
        # Implementation would analyze competitive positioning
        pass

    async def _generate_executive_summary(
        self, performance_metrics: Dict[str, Any], 
        audience_analysis: Dict[str, Any],
        revenue_analytics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary of analytics"""
        # Implementation would generate summary
        pass

    async def _generate_action_recommendations(
        self, performance_metrics: Dict[str, Any],
        audience_analysis: Dict[str, Any],
        content_summary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        # Implementation would generate recommendations
        pass

    async def _get_live_performance_indicators(self, user_id: int) -> Dict[str, Any]:
        """Get live performance indicators"""
        # Implementation would get real-time indicators
        pass

    async def _get_recent_content_performance(self, user_id: int) -> Dict[str, Any]:
        """Get recent content performance"""
        # Implementation would get recent content data
        pass

    async def _get_trending_content(self, user_id: int) -> Dict[str, Any]:
        """Get trending content"""
        # Implementation would identify trending content
        pass

    async def _get_audience_activity(self, user_id: int) -> Dict[str, Any]:
        """Get current audience activity"""
        # Implementation would get audience activity
        pass
