"""Performance Metrics Engine
=========================

Advanced performance metrics calculation and optimization for multi-platform content.
Provides real-time performance tracking, benchmark analysis, and optimization insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized copying, distribution, or modification without explicit written
permission is strictly prohibited and will result in legal action.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from redis import Redis
import json
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error


class PerformanceCategory(Enum):
    """
Performance category enumeration"""

    ENGAGEMENT = "engagement"
    REACH = "reach"
    CONVERSION = "conversion"
    RETENTION = "retention"
    MONETIZATION = "monetization"
    PROTECTION = "protection"
    GROWTH = "growth"
    QUALITY = "quality"


class PlatformType(Enum):
    """Platform type enumeration"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    CUSTOM = "custom"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_id: str
    category: PerformanceCategory
    platform: PlatformType
    value: float
    benchmark: float
    percentile: float
    trend: str  # "increasing", "decreasing", "stable"
    confidence_score: float
    calculation_method: str
    timestamp: datetime


@dataclass
class PerformanceBenchmark:
    """Performance benchmark data"""
    category: PerformanceCategory
    platform: PlatformType
    industry_average: float
    top_quartile: float
    median: float
    bottom_quartile: float
    sample_size: int
    last_updated: datetime


@dataclass
class PerformanceOptimization:
    """
Performance optimization recommendation"""
    category: PerformanceCategory
    current_value: float
    target_value: float
    improvement_potential: float
    action_items: List[str]
    priority: str  # "high", "medium", "low"
    estimated_impact: float
    implementation_difficulty: str


class PerformanceMetrics:
    """
    Professional performance metrics engine for content optimization.
    
    Calculates comprehensive performance metrics, benchmarks against industry standards,
    and provides actionable optimization recommendations for content creators.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        """
        Initialize PerformanceMetrics engine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """
        self.db_session = db_session
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        self.cache_ttl = 3600  # 1 hour cache
        
    async def calculate_engagement_metrics(self, content_id: str, 
                                         platform: PlatformType,
                                         time_period: timedelta = timedelta(days=30)
                                         ) -> Dict[str, float]:
        """
        Calculate comprehensive engagement metrics for content.
        
        Args:
            content_id: Unique content identifier
            platform: Platform where content is published
            time_period: Time period for metric calculation
            
        Returns:
            Dictionary containing engagement metrics
        """
        try:
            cache_key = f"engagement_metrics:{content_id}:{platform.value}:{time_period.days}"
            cached_result = await self._get_cached_result(cache_key)
            
            if cached_result:
                return cached_result
                
            # Fetch engagement data from database
            end_date = datetime.utcnow()
            start_date = end_date - time_period
            
            query = text("""
                SELECT 
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares,
                    SUM(saves) as total_saves,
                    COUNT(*) as total_posts,
                    AVG(session_duration) as avg_session_duration
                FROM content_metrics 
                WHERE content_id = :content_id 
                AND platform = :platform 
                AND created_at BETWEEN :start_date AND :end_date
            """)
            
            result = await self.db_session.execute(
                query, 
                {
                    "content_id": content_id,
                    "platform": platform.value,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            data = result.fetchone()
            
            if not data or not data.total_views:
                return {}
                
            # Calculate engagement metrics
            metrics = {
                "engagement_rate": (data.total_likes + data.total_comments + data.total_shares) / data.total_views * 100,
                "like_rate": data.total_likes / data.total_views * 100,
                "comment_rate": data.total_comments / data.total_views * 100,
                "share_rate": data.total_shares / data.total_views * 100,
                "save_rate": data.total_saves / data.total_views * 100 if data.total_saves else 0,
                "avg_session_duration": float(data.avg_session_duration or 0),
                "posts_frequency": data.total_posts / time_period.days,
                "total_interactions": data.total_likes + data.total_comments + data.total_shares + (data.total_saves or 0)
            }
            
            # Cache results
            await self._cache_result(cache_key, metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement metrics: {str(e)}")
            return {}
    
    async def calculate_reach_metrics(self, user_id: str, 
                                    platform: PlatformType,
                                    time_period: timedelta = timedelta(days=30)
                                    ) -> Dict[str, float]:
        """
        Calculate reach and audience growth metrics.
        
        Args:
            user_id: User identifier
            platform: Platform for analysis
            time_period: Analysis time period
            
        Returns:
            Dictionary containing reach metrics
        """
        try:
            cache_key = f"reach_metrics:{user_id}:{platform.value}:{time_period.days}"
            cached_result = await self._get_cached_result(cache_key)
            
            if cached_result:
                return cached_result
                
            end_date = datetime.utcnow()
            start_date = end_date - time_period
            
            # Fetch reach data
            query = text("""
                WITH daily_metrics AS (
                    SELECT 
                        DATE(created_at) as metric_date,
                        SUM(reach) as daily_reach,
                        SUM(impressions) as daily_impressions,
                        COUNT(DISTINCT viewer_id) as unique_viewers
                    FROM content_metrics cm
                    JOIN content c ON cm.content_id = c.id
                    WHERE c.user_id = :user_id 
                    AND cm.platform = :platform
                    AND cm.created_at BETWEEN :start_date AND :end_date
                    GROUP BY DATE(created_at)
                )
                SELECT 
                    AVG(daily_reach) as avg_daily_reach,
                    MAX(daily_reach) as max_daily_reach,
                    SUM(daily_reach) as total_reach,
                    AVG(daily_impressions) as avg_daily_impressions,
                    SUM(daily_impressions) as total_impressions,
                    AVG(unique_viewers) as avg_unique_viewers,
                    COUNT(*) as active_days
                FROM daily_metrics
            """)
            
            result = await self.db_session.execute(
                query,
                {
                    "user_id": user_id,
                    "platform": platform.value,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            data = result.fetchone()
            
            if not data:
                return {}
                
            # Calculate additional metrics
            reach_consistency = (data.avg_daily_reach / data.max_daily_reach * 100) if data.max_daily_reach else 0
            impression_reach_ratio = (data.total_impressions / data.total_reach) if data.total_reach else 0
            
            metrics = {
                "avg_daily_reach": float(data.avg_daily_reach or 0),
                "max_daily_reach": float(data.max_daily_reach or 0),
                "total_reach": float(data.total_reach or 0),
                "total_impressions": float(data.total_impressions or 0),
                "avg_unique_viewers": float(data.avg_unique_viewers or 0),
                "reach_consistency": reach_consistency,
                "impression_reach_ratio": impression_reach_ratio,
                "active_days": data.active_days,
                "reach_frequency": data.total_reach / time_period.days if data.total_reach else 0
            }
            
            # Calculate growth metrics
            growth_metrics = await self._calculate_growth_metrics(user_id, platform, time_period)
            metrics.update(growth_metrics)
            
            await self._cache_result(cache_key, metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating reach metrics: {str(e)}")
            return {}
    
    async def calculate_conversion_metrics(self, user_id: str,
                                         platform: PlatformType,
                                         time_period: timedelta = timedelta(days=30)
                                         ) -> Dict[str, float]:
        """
        Calculate conversion and monetization performance metrics.
        
        Args:
            user_id: User identifier
            platform: Platform for analysis
            time_period: Analysis time period
            
        Returns:
            Dictionary containing conversion metrics
        """
        try:
            cache_key = f"conversion_metrics:{user_id}:{platform.value}:{time_period.days}"
            cached_result = await self._get_cached_result(cache_key)
            
            if cached_result:
                return cached_result
                
            end_date = datetime.utcnow()
            start_date = end_date - time_period
            
            # Fetch conversion data
            query = text("""
                SELECT 
                    SUM(views) as total_views,
                    SUM(clicks) as total_clicks,
                    SUM(conversions) as total_conversions,
                    SUM(revenue) as total_revenue,
                    COUNT(DISTINCT content_id) as total_content,
                    AVG(cost_per_click) as avg_cpc,
                    AVG(cost_per_conversion) as avg_cpc_conversion
                FROM monetization_metrics mm
                JOIN content c ON mm.content_id = c.id
                WHERE c.user_id = :user_id 
                AND mm.platform = :platform
                AND mm.created_at BETWEEN :start_date AND :end_date
            """)
            
            result = await self.db_session.execute(
                query,
                {
                    "user_id": user_id,
                    "platform": platform.value,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            data = result.fetchone()
            
            if not data or not data.total_views:
                return {}
                
            # Calculate conversion metrics
            click_through_rate = (data.total_clicks / data.total_views * 100) if data.total_views else 0
            conversion_rate = (data.total_conversions / data.total_clicks * 100) if data.total_clicks else 0
            revenue_per_view = (data.total_revenue / data.total_views) if data.total_views else 0
            revenue_per_content = (data.total_revenue / data.total_content) if data.total_content else 0
            
            metrics = {
                "click_through_rate": click_through_rate,
                "conversion_rate": conversion_rate,
                "revenue_per_view": revenue_per_view,
                "revenue_per_content": revenue_per_content,
                "total_revenue": float(data.total_revenue or 0),
                "avg_cost_per_click": float(data.avg_cpc or 0),
                "avg_cost_per_conversion": float(data.avg_cpc_conversion or 0),
                "return_on_investment": self._calculate_roi(data.total_revenue, data.avg_cpc * data.total_clicks)
            }
            
            await self._cache_result(cache_key, metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating conversion metrics: {str(e)}")
            return {}
    
    async def get_performance_benchmarks(self, category: PerformanceCategory,
                                       platform: PlatformType
                                       ) -> Optional[PerformanceBenchmark]:
        """
        Get industry performance benchmarks for comparison.
        
        Args:
            category: Performance category
            platform: Platform type
            
        Returns:
            Performance benchmark data
        """
        try:
            cache_key = f"benchmarks:{category.value}:{platform.value}"
            cached_result = await self._get_cached_result(cache_key)
            
            if cached_result:
                return PerformanceBenchmark(**cached_result)
                
            # Fetch benchmark data from database
            query = text("""
                SELECT 
                    AVG(metric_value) as industry_average,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY metric_value) as top_quartile,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY metric_value) as median,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY metric_value) as bottom_quartile,
                    COUNT(*) as sample_size,
                    MAX(updated_at) as last_updated
                FROM performance_benchmarks 
                WHERE category = :category 
                AND platform = :platform
                AND updated_at >= NOW() - INTERVAL '30 days'
            """)
            
            result = await self.db_session.execute(
                query,
                {
                    "category": category.value,
                    "platform": platform.value
                }
            )
            data = result.fetchone()
            
            if not data or not data.sample_size:
                return None
                
            benchmark = PerformanceBenchmark(
                category=category,
                platform=platform,
                industry_average=float(data.industry_average),
                top_quartile=float(data.top_quartile),
                median=float(data.median),
                bottom_quartile=float(data.bottom_quartile),
                sample_size=data.sample_size,
                last_updated=data.last_updated
            )
            
            # Cache for 24 hours
            await self._cache_result(cache_key, benchmark.__dict__, ttl=86400)
            
            return benchmark
            
        except Exception as e:
            self.logger.error(f"Error fetching performance benchmarks: {str(e)}")
            return None
    
    async def generate_performance_report(self, user_id: str,
                                        time_period: timedelta = timedelta(days=30)
                                        ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report for user.
        
        Args:
            user_id: User identifier
            time_period: Analysis time period
            
        Returns:
            Comprehensive performance report
        """
        try:
            report = {
                "user_id": user_id,
                "period_start": datetime.utcnow() - time_period,
                "period_end": datetime.utcnow(),
                "platforms": {},
                "overall_performance": {},
                "recommendations": []
            }
            
            # Analyze performance for each platform
            for platform in PlatformType:
                platform_metrics = {}
                
                # Engagement metrics
                engagement = await self.calculate_engagement_metrics("", platform, time_period)
                if engagement:
                    platform_metrics["engagement"] = engagement
                
                # Reach metrics
                reach = await self.calculate_reach_metrics(user_id, platform, time_period)
                if reach:
                    platform_metrics["reach"] = reach
                
                # Conversion metrics
                conversion = await self.calculate_conversion_metrics(user_id, platform, time_period)
                if conversion:
                    platform_metrics["conversion"] = conversion
                
                if platform_metrics:
                    report["platforms"][platform.value] = platform_metrics
            
            # Calculate overall performance
            report["overall_performance"] = await self._calculate_overall_performance(report["platforms"])
            
            # Generate recommendations
            report["recommendations"] = await self._generate_performance_recommendations(user_id, report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            return {}
    
    async def _calculate_growth_metrics(self, user_id: str, platform: PlatformType,
                                      time_period: timedelta) -> Dict[str, float]:
        """Calculate growth metrics for reach analysis."""
        try:
            # Split time period into two halves for comparison
            mid_point = datetime.utcnow() - time_period / 2
            end_date = datetime.utcnow()
            start_date = end_date - time_period
            
            # Get metrics for first half
            query_first = text("""
                SELECT AVG(reach) as avg_reach, SUM(views) as total_views
                FROM content_metrics cm
                JOIN content c ON cm.content_id = c.id
                WHERE c.user_id = :user_id AND cm.platform = :platform
                AND cm.created_at BETWEEN :start_date AND :mid_point
            """)
            
            result_first = await self.db_session.execute(
                query_first,
                {
                    "user_id": user_id,
                    "platform": platform.value,
                    "start_date": start_date,
                    "mid_point": mid_point
                }
            )
            first_half = result_first.fetchone()
            
            # Get metrics for second half
            query_second = text("""
                SELECT AVG(reach) as avg_reach, SUM(views) as total_views
                FROM content_metrics cm
                JOIN content c ON cm.content_id = c.id
                WHERE c.user_id = :user_id AND cm.platform = :platform
                AND cm.created_at BETWEEN :mid_point AND :end_date
            """)
            
            result_second = await self.db_session.execute(
                query_second,
                {
                    "user_id": user_id,
                    "platform": platform.value,
                    "mid_point": mid_point,
                    "end_date": end_date
                }
            )
            second_half = result_second.fetchone()
            
            # Calculate growth rates
            reach_growth = 0
            views_growth = 0
            
            if first_half and second_half and first_half.avg_reach and first_half.total_views:
                reach_growth = ((second_half.avg_reach - first_half.avg_reach) / first_half.avg_reach * 100) if second_half.avg_reach else 0
                views_growth = ((second_half.total_views - first_half.total_views) / first_half.total_views * 100) if second_half.total_views else 0
            
            return {
                "reach_growth_rate": reach_growth,
                "views_growth_rate": views_growth
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating growth metrics: {str(e)}")
            return {"reach_growth_rate": 0, "views_growth_rate": 0}
    
    def _calculate_roi(self, revenue: float, cost: float) -> float:
        """Calculate return on investment."""
        if cost == 0:
            return 0
        return ((revenue - cost) / cost * 100)
    
    async def _calculate_overall_performance(self, platforms: Dict) -> Dict[str, float]:
        """
Calculate overall performance metrics across all platforms."""
        try:
            if not platforms:
                return {}
                
            all_engagement_rates = []
            all_reach_values = []
            all_revenue_values = []
            
            for platform_data in platforms.values():
                if "engagement" in platform_data:
                    all_engagement_rates.append(platform_data["engagement"].get("engagement_rate", 0))
                if "reach" in platform_data:
                    all_reach_values.append(platform_data["reach"].get("total_reach", 0))
                if "conversion" in platform_data:
                    all_revenue_values.append(platform_data["conversion"].get("total_revenue", 0))
            
            overall = {}
            
            if all_engagement_rates:
                overall["avg_engagement_rate"] = statistics.mean(all_engagement_rates)
                overall["engagement_consistency"] = 100 - (statistics.stdev(all_engagement_rates) / statistics.mean(all_engagement_rates) * 100) if len(all_engagement_rates) > 1 else 100
            
            if all_reach_values:
                overall["total_reach"] = sum(all_reach_values)
                overall["avg_reach_per_platform"] = statistics.mean(all_reach_values)
            
            if all_revenue_values:
                overall["total_revenue"] = sum(all_revenue_values)
                overall["avg_revenue_per_platform"] = statistics.mean(all_revenue_values)
            
            return overall
            
        except Exception as e:
            self.logger.error(f"Error calculating overall performance: {str(e)}")
            return {}
    
    async def _generate_performance_recommendations(self, user_id: str, report: Dict) -> List[Dict]:
        """Generate actionable performance recommendations."""
        try:
            recommendations = []
            
            # Analyze engagement rates
            for platform, metrics in report["platforms"].items():
                if "engagement" in metrics:
                    engagement_rate = metrics["engagement"].get("engagement_rate", 0)
                    
                    if engagement_rate < 2.0:  # Low engagement threshold
                        recommendations.append({
                            "type": "engagement",
                            "platform": platform,
                            "priority": "high",
                            "title": f"Improve {platform.title()} engagement",
                            "description": f"Current engagement rate ({engagement_rate:.2f}%) is below industry standard",
                            "actions": [
                                "Post at optimal times for your audience",
                                "Use more interactive content formats",
                                "Engage actively with comments and messages",
                                "Analyze top-performing content patterns"
                            ]
                        })
                
                # Analyze reach metrics
                if "reach" in metrics:
                    reach_growth = metrics["reach"].get("reach_growth_rate", 0)
                    
                    if reach_growth < 0:  # Declining reach
                        recommendations.append({
                            "type": "reach",
                            "platform": platform,
                            "priority": "medium",
                            "title": f"Reverse declining reach on {platform.title()}",
                            "description": f"Reach is declining by {abs(reach_growth):.1f}%",
                            "actions": [
                                "Diversify content types and formats",
                                "Collaborate with other creators",
                                "Use trending hashtags and topics",
                                "Optimize posting frequency"
                            ]
                        })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result from Redis."""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached result: {str(e)}")
            return None
    
    async def _cache_result(self, cache_key: str, data: Dict, ttl: int = None) -> None:
        """Cache result in Redis."""
        try:
            cache_ttl = ttl or self.cache_ttl
            self.redis_client.setex(
                cache_key,
                cache_ttl,
                json.dumps(data, default=str)
            )
        except Exception as e:
            self.logger.error(f"Error caching result: {str(e)}")
