"""Platform Analytics - Advanced Multi-Platform Analytics Engine

Provides comprehensive analytics and insights across all connected platforms
including performance tracking, audience analysis, and revenue analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from fastapi import HTTPException

from ...core.config import settings
from ...core.logging import get_logger
from ...models.analytics import AnalyticsMetric, PlatformAnalytics, ContentPerformance
from ...models.platform import Platform, ContentItem
from ...services.ai.predictive_analytics import PredictiveAnalyticsService
from ...services.integrations.youtube_api import YouTubeAPIService
from ...services.integrations.instagram_api import InstagramAPIService
from ...services.integrations.tiktok_api import TikTokAPIService
from ...services.integrations.spotify_api import SpotifyAPIService
from ...utils.analytics_utils import calculate_growth_rate, calculate_engagement_rate

logger = get_logger(__name__)

class MetricType(Enum):
    """Analytics metric types"""
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    CLICKS = "clicks"
    IMPRESSIONS = "impressions"
    REACH = "reach"
    ENGAGEMENT_RATE = "engagement_rate"
    FOLLOWER_GROWTH = "follower_growth"
    REVENUE = "revenue"
    WATCH_TIME = "watch_time"
    CLICK_THROUGH_RATE = "click_through_rate"

class TimeFrame(Enum):
    """Analytics time frames"""
    LAST_24H = "last_24h"
    LAST_7D = "last_7d"
    LAST_30D = "last_30d"
    LAST_90D = "last_90d"
    LAST_YEAR = "last_year"
    ALL_TIME = "all_time"

@dataclass
class MetricData:
    """Individual metric data point"""
    metric_type: MetricType
    value: Union[int, float]
    timestamp: datetime
    platform: str
    content_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    user_id: int
    time_frame: TimeFrame
    platforms: List[str]
    metrics: Dict[str, List[MetricData]]
    insights: List[Dict[str, Any]]
    predictions: Dict[str, Any]
    generated_at: datetime

@dataclass
class CompetitorAnalysis:
    """Competitor analysis data"""
    competitor_name: str
    platform: str
    metrics: Dict[str, Union[int, float]]
    comparison_score: float
    insights: List[str]

class PlatformAnalytics:
    """
    Advanced multi-platform analytics engine
    
    Features:
    - Real-time performance tracking
    - Cross-platform analytics aggregation
    - Audience demographics analysis
    - Predictive analytics and forecasting
    - Competitor benchmarking
    - Revenue and monetization tracking
    - AI-powered insights generation
    """
    
    def __init__(self):
        self.predictive_service = PredictiveAnalyticsService()
        
        # Platform API services for analytics
        self.platform_services = {
            'youtube': YouTubeAPIService(),
            'instagram': InstagramAPIService(),
            'tiktok': TikTokAPIService(),
            'spotify': SpotifyAPIService()
        }
        
        # Analytics cache
        self.analytics_cache = {}
        self.cache_ttl = timedelta(minutes=15)
    
    async def initialize(self) -> bool:
        """
        Initialize analytics engine
        
        Returns:
            bool: Initialization success status
        """
        try:
            logger.info("Initializing Platform Analytics...")
            
            # Initialize platform services
            for platform, service in self.platform_services.items():
                await service.initialize()
                logger.info(f"{platform} analytics service initialized")
            
            # Initialize predictive analytics service
            await self.predictive_service.initialize()
            
            # Start analytics collection
            asyncio.create_task(self._start_analytics_collection())
            
            logger.info("Platform Analytics initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Platform Analytics initialization failed: {e}")
            return False
    
    async def generate_comprehensive_report(
        self,
        user_id: int,
        time_frame: TimeFrame = TimeFrame.LAST_30D,
        platforms: Optional[List[str]] = None,
        session: AsyncSession = None
    ) -> AnalyticsReport:
        """
        Generate comprehensive analytics report
        
        Args:
            user_id: User ID
            time_frame: Analysis time frame
            platforms: Specific platforms (None for all)
            session: Database session
            
        Returns:
            Comprehensive analytics report
        """
        try:
            logger.info(f"Generating analytics report for user {user_id}")
            
            # Get user's connected platforms
            if not platforms:
                platforms = await self._get_user_platforms(user_id, session)
            
            # Collect metrics from all platforms
            all_metrics = {}
            
            for platform in platforms:
                platform_metrics = await self._collect_platform_metrics(
                    user_id, platform, time_frame, session
                )
                all_metrics[platform] = platform_metrics
            
            # Generate AI-powered insights
            insights = await self._generate_insights(all_metrics, time_frame)
            
            # Generate predictions
            predictions = await self._generate_predictions(all_metrics, user_id)
            
            # Create comprehensive report
            report = AnalyticsReport(
                user_id=user_id,
                time_frame=time_frame,
                platforms=platforms,
                metrics=all_metrics,
                insights=insights,
                predictions=predictions,
                generated_at=datetime.utcnow()
            )
            
            # Cache report
            cache_key = f"report_{user_id}_{time_frame.value}"
            self.analytics_cache[cache_key] = {
                'data': report,
                'expires_at': datetime.utcnow() + self.cache_ttl
            }
            
            logger.info(f"Analytics report generated for user {user_id}")
            return report
            
        except Exception as e:
            logger.error(f"Analytics report generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
    
    async def get_content_performance(
        self,
        content_id: int,
        user_id: int,
        time_frame: TimeFrame = TimeFrame.LAST_7D,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Get detailed performance analytics for specific content
        
        Args:
            content_id: Content item ID
            user_id: User ID
            time_frame: Analysis time frame
            session: Database session
            
        Returns:
            Dict containing content performance data
        """
        try:
            # Get content item
            result = await session.execute(
                select(ContentItem).where(
                    and_(
                        ContentItem.id == content_id,
                        ContentItem.user_id == user_id
                    )
                )
            )
            content = result.scalar_one_or_none()
            
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # Get performance metrics from all platforms
            performance_data = {}
            
            for platform in await self._get_content_platforms(content_id, session):
                platform_performance = await self._get_content_platform_performance(
                    content_id, platform, time_frame
                )
                performance_data[platform] = platform_performance
            
            # Calculate aggregated metrics
            aggregated_metrics = await self._calculate_aggregated_metrics(performance_data)
            
            # Generate content insights
            content_insights = await self._generate_content_insights(
                content, performance_data, aggregated_metrics
            )
            
            return {
                'content_id': content_id,
                'title': content.title,
                'content_type': content.content_type,
                'published_at': content.created_at.isoformat(),
                'time_frame': time_frame.value,
                'platform_performance': performance_data,
                'aggregated_metrics': aggregated_metrics,
                'insights': content_insights,
                'recommendations': await self._generate_content_recommendations(
                    content, performance_data
                )
            }
            
        except Exception as e:
            logger.error(f"Content performance analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Performance analysis failed: {str(e)}")
    
    async def get_audience_demographics(
        self,
        user_id: int,
        platform: Optional[str] = None,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Get audience demographics across platforms
        
        Args:
            user_id: User ID
            platform: Specific platform (None for all)
            session: Database session
            
        Returns:
            Dict containing audience demographics data
        """
        try:
            demographics_data = {}
            
            # Get demographics from specific platform or all platforms
            platforms_to_analyze = [platform] if platform else await self._get_user_platforms(user_id, session)
            
            for platform_name in platforms_to_analyze:
                if platform_name in self.platform_services:
                    service = self.platform_services[platform_name]
                    platform_demographics = await service.get_audience_demographics(user_id)
                    demographics_data[platform_name] = platform_demographics
            
            # Aggregate cross-platform demographics
            aggregated_demographics = await self._aggregate_demographics(demographics_data)
            
            return {
                'user_id': user_id,
                'platform_demographics': demographics_data,
                'aggregated_demographics': aggregated_demographics,
                'insights': await self._generate_audience_insights(aggregated_demographics),
                'updated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Audience demographics analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Demographics analysis failed: {str(e)}")
    
    async def get_revenue_analytics(
        self,
        user_id: int,
        time_frame: TimeFrame = TimeFrame.LAST_30D,
        breakdown_by: str = "platform",
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Get detailed revenue analytics
        
        Args:
            user_id: User ID
            time_frame: Analysis time frame
            breakdown_by: Breakdown method (platform, content_type, date)
            session: Database session
            
        Returns:
            Dict containing revenue analytics data
        """
        try:
            # Get revenue data from all monetized platforms
            revenue_data = {}
            
            platforms = await self._get_user_monetized_platforms(user_id, session)
            
            for platform in platforms:
                platform_revenue = await self._collect_platform_revenue(
                    user_id, platform, time_frame
                )
                revenue_data[platform] = platform_revenue
            
            # Calculate revenue metrics
            total_revenue = sum(
                data.get('total_revenue', 0) for data in revenue_data.values()
            )
            
            revenue_growth = await self._calculate_revenue_growth(
                user_id, time_frame, session
            )
            
            # Generate revenue breakdown
            revenue_breakdown = await self._generate_revenue_breakdown(
                revenue_data, breakdown_by
            )
            
            # Revenue predictions
            revenue_predictions = await self.predictive_service.predict_revenue(
                user_id, revenue_data, time_frame
            )
            
            return {
                'user_id': user_id,
                'time_frame': time_frame.value,
                'total_revenue': total_revenue,
                'revenue_growth': revenue_growth,
                'platform_revenue': revenue_data,
                'revenue_breakdown': revenue_breakdown,
                'predictions': revenue_predictions,
                'insights': await self._generate_revenue_insights(revenue_data, revenue_growth),
                'updated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Revenue analytics failed: {e}")
            raise HTTPException(status_code=500, detail=f"Revenue analytics failed: {str(e)}")
    
    async def perform_competitor_analysis(
        self,
        user_id: int,
        competitors: List[str],
        platforms: List[str],
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Perform competitor analysis
        
        Args:
            user_id: User ID
            competitors: List of competitor identifiers
            platforms: Platforms to analyze
            session: Database session
            
        Returns:
            Dict containing competitor analysis data
        """
        try:
            analysis_results = []
            
            for competitor in competitors:
                for platform in platforms:
                    if platform in self.platform_services:
                        competitor_data = await self._analyze_competitor(
                            competitor, platform, user_id
                        )
                        analysis_results.append(competitor_data)
            
            # Generate competitive insights
            competitive_insights = await self._generate_competitive_insights(
                analysis_results, user_id
            )
            
            # Benchmarking analysis
            benchmarks = await self._generate_benchmarks(analysis_results, user_id)
            
            return {
                'user_id': user_id,
                'competitors_analyzed': competitors,
                'platforms': platforms,
                'competitor_data': analysis_results,
                'competitive_insights': competitive_insights,
                'benchmarks': benchmarks,
                'recommendations': await self._generate_competitive_recommendations(
                    analysis_results, user_id
                ),
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Competitor analysis failed: {str(e)}")
    
    async def get_trending_analysis(
        self,
        user_id: int,
        content_type: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Get trending content analysis and opportunities
        
        Args:
            user_id: User ID
            content_type: Specific content type filter
            platforms: Specific platforms to analyze
            session: Database session
            
        Returns:
            Dict containing trending analysis data
        """
        try:
            # Get trending data from platforms
            trending_data = {}
            
            platforms_to_analyze = platforms or await self._get_user_platforms(user_id, session)
            
            for platform in platforms_to_analyze:
                if platform in self.platform_services:
                    service = self.platform_services[platform]
                    platform_trends = await service.get_trending_content(content_type)
                    trending_data[platform] = platform_trends
            
            # Analyze trending opportunities
            opportunities = await self._identify_trending_opportunities(
                trending_data, user_id, content_type
            )
            
            # Generate trend insights
            trend_insights = await self._generate_trend_insights(trending_data, user_id)
            
            return {
                'user_id': user_id,
                'content_type': content_type,
                'platforms': platforms_to_analyze,
                'trending_data': trending_data,
                'opportunities': opportunities,
                'insights': trend_insights,
                'recommendations': await self._generate_trending_recommendations(
                    opportunities, user_id
                ),
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trending analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Trending analysis failed: {str(e)}")
    
    async def _collect_platform_metrics(
        self,
        user_id: int,
        platform: str,
        time_frame: TimeFrame,
        session: AsyncSession
    ) -> List[MetricData]:
        """Collect metrics from specific platform"""
        try:
            if platform not in self.platform_services:
                logger.warning(f"Unsupported platform for analytics: {platform}")
                return []
            
            service = self.platform_services[platform]
            
            # Get raw metrics from platform API
            raw_metrics = await service.get_analytics_data(user_id, time_frame)
            
            # Convert to standardized format
            standardized_metrics = []
            for metric_name, metric_value in raw_metrics.items():
                if metric_name in [m.value for m in MetricType]:
                    metric_data = MetricData(
                        metric_type=MetricType(metric_name),
                        value=metric_value,
                        timestamp=datetime.utcnow(),
                        platform=platform
                    )
                    standardized_metrics.append(metric_data)
            
            return standardized_metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics from {platform}: {e}")
            return []
    
    async def _generate_insights(
        self,
        metrics: Dict[str, List[MetricData]],
        time_frame: TimeFrame
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered insights from metrics"""
        insights = []
        
        try:
            # Performance insights
            best_performing_platform = await self._identify_best_platform(metrics)
            if best_performing_platform:
                insights.append({
                    'type': 'performance',
                    'title': 'Best Performing Platform',
                    'description': f'{best_performing_platform} is your top performing platform',
                    'priority': 'high',
                    'action_items': [
                        f'Focus more content creation on {best_performing_platform}',
                        'Analyze successful content patterns',
                        'Increase posting frequency on this platform'
                    ]
                })
            
            # Growth insights
            growth_trends = await self._analyze_growth_trends(metrics)
            if growth_trends.get('declining_platforms'):
                insights.append({
                    'type': 'growth',
                    'title': 'Declining Performance Alert',
                    'description': 'Some platforms showing declining engagement',
                    'priority': 'medium',
                    'platforms': growth_trends['declining_platforms'],
                    'action_items': [
                        'Review content strategy for declining platforms',
                        'Analyze competitor strategies',
                        'Experiment with new content formats'
                    ]
                })
            
            # Optimization insights
            optimization_opportunities = await self._identify_optimization_opportunities(metrics)
            insights.extend(optimization_opportunities)
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return []
    
    async def _generate_predictions(
        self,
        metrics: Dict[str, List[MetricData]],
        user_id: int
    ) -> Dict[str, Any]:
        """Generate predictive analytics"""
        try:
            predictions = {}
            
            # Growth predictions
            predictions['growth'] = await self.predictive_service.predict_growth(
                user_id, metrics
            )
            
            # Engagement predictions
            predictions['engagement'] = await self.predictive_service.predict_engagement(
                user_id, metrics
            )
            
            # Revenue predictions
            predictions['revenue'] = await self.predictive_service.predict_revenue(
                user_id, metrics
            )
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return {}
    
    async def _start_analytics_collection(self):
        """Start background analytics collection"""
        while True:
            try:
                # Collect analytics for all active users
                await self._collect_analytics_batch()
                
                # Wait 1 hour before next collection
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Analytics collection error: {e}")
                await asyncio.sleep(3600)
    
    async def _collect_analytics_batch(self):
        """Collect analytics for batch of users"""
        # Implementation for batch analytics collection
        logger.info("Running batch analytics collection")
    
    async def _get_user_platforms(self, user_id: int, session: AsyncSession) -> List[str]:
        """Get list of platforms connected for user"""
        # Implementation to get user's connected platforms
        return ['youtube', 'instagram', 'tiktok']  # Placeholder
    
    async def _get_user_monetized_platforms(self, user_id: int, session: AsyncSession) -> List[str]:
        """Get list of monetized platforms for user"""
        # Implementation to get user's monetized platforms
        return ['youtube', 'spotify']  # Placeholder
    
    async def _identify_best_platform(self, metrics: Dict[str, List[MetricData]]) -> Optional[str]:
        """Identify best performing platform"""
        # Implementation for platform performance analysis
        return 'youtube'  # Placeholder
    
    async def _analyze_growth_trends(self, metrics: Dict[str, List[MetricData]]) -> Dict[str, Any]:
        """Analyze growth trends across platforms"""
        # Implementation for growth trend analysis
        return {'declining_platforms': [], 'growing_platforms': []}  # Placeholder
    
    async def _identify_optimization_opportunities(
        self, 
        metrics: Dict[str, List[MetricData]]
    ) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        # Implementation for optimization opportunity identification
        return []  # Placeholder
