"""Analytics business service for IA Influencer Agent platform.

This service handles comprehensive analytics for content performance, user engagement,
protection effectiveness, and revenue tracking across all platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.

WARNING: This code is proprietary intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution is strictly
prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..core.database import get_db
from ..models.content import Content
from ..models.user import User
from ..models.analytics import (
    ContentAnalytics, UserEngagement, PlatformMetrics,
    RevenueAnalytics, ProtectionAnalytics
)
from ..utils.time_utils import get_time_periods, calculate_growth_rate
from ..utils.chart_generator import ChartGenerator
from ..integrations.platform_apis import PlatformAPIManager

logger = logging.getLogger(__name__)

class AnalyticsTimeframe(Enum):
    """Analytics timeframe options."""    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class AnalyticsMetricType(Enum):
    """Types of analytics metrics."""    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    REVENUE = "revenue"
    PROTECTION = "protection"
    GROWTH = "growth"
    DEMOGRAPHIC = "demographic"

@dataclass
class AnalyticsInsight:
    """Analytics insight data structure."""    metric: str
    value: float
    trend: str  # "up", "down", "stable"
    change_percentage: float
    recommendation: str
    timestamp: datetime

@dataclass
class ContentPerformanceMetrics:
    """Content performance analytics data."""    content_id: str
    views: int
    likes: int
    shares: int
    comments: int
    engagement_rate: float
    reach: int
    impressions: int
    click_through_rate: float
    conversion_rate: float
    revenue_generated: float

class AnalyticsService:
    """    Comprehensive analytics service for content creators and platform monitoring.
    
    Provides deep insights into content performance, user behavior, revenue tracking,
    and protection effectiveness across all supported platforms.
    """    
    def __init__(self):
        self.chart_generator = ChartGenerator()
        self.platform_apis = PlatformAPIManager()
        self._cache_ttl = timedelta(minutes=15)
        self._cache = {}
    
    async def get_content_analytics(
        self,
        user_id: str,
        content_ids: Optional[List[str]] = None,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTH,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Get comprehensive content analytics for user's content.
        
        Args:
            user_id: User identifier
            content_ids: Specific content IDs to analyze (optional)
            timeframe: Analysis timeframe
            db: Database session
            
        Returns:
            Comprehensive content analytics data
        """        if db is None:
            db = next(get_db())
        
        try:
            # Build content query
            query = db.query(Content).filter(Content.user_id == user_id)
            if content_ids:
                query = query.filter(Content.id.in_(content_ids))
            
            contents = query.all()
            
            analytics_data = {
                "overview": await self._generate_content_overview(contents, timeframe, db),
                "performance": await self._analyze_content_performance(contents, timeframe, db),
                "engagement": await self._analyze_engagement_metrics(contents, timeframe, db),
                "revenue": await self._analyze_revenue_metrics(user_id, content_ids, timeframe, db),
                "protection": await self._analyze_protection_metrics(contents, timeframe, db),
                "trends": await self._analyze_content_trends(contents, timeframe, db),
                "insights": await self._generate_content_insights(contents, timeframe, db),
                "recommendations": await self._generate_content_recommendations(contents, timeframe, db)
            }
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error getting content analytics: {str(e)}")
            raise
    
    async def get_platform_analytics(
        self,
        user_id: str,
        platforms: Optional[List[str]] = None,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTH,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Get platform-specific analytics and cross-platform comparison.
        
        Args:
            user_id: User identifier
            platforms: Specific platforms to analyze
            timeframe: Analysis timeframe
            db: Database session
            
        Returns:
            Platform analytics data
        """        if db is None:
            db = next(get_db())
        
        try:
            platform_data = {}
            
            # Get user's active platforms
            if not platforms:
                platforms = await self._get_user_platforms(user_id, db)
            
            for platform in platforms:
                platform_metrics = await self._get_platform_metrics(
                    user_id, platform, timeframe, db
                )
                platform_data[platform] = {
                    "metrics": platform_metrics,
                    "performance": await self._analyze_platform_performance(
                        user_id, platform, timeframe, db
                    ),
                    "audience": await self._analyze_platform_audience(
                        user_id, platform, timeframe, db
                    ),
                    "content_distribution": await self._analyze_content_distribution(
                        user_id, platform, timeframe, db
                    )
                }
            
            # Cross-platform analysis
            cross_platform_analysis = await self._analyze_cross_platform_performance(
                user_id, platforms, timeframe, db
            )
            
            return {
                "platforms": platform_data,
                "cross_platform": cross_platform_analysis,
                "best_performing_platform": await self._identify_best_platform(
                    platform_data
                ),
                "optimization_opportunities": await self._identify_optimization_opportunities(
                    platform_data
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting platform analytics: {str(e)}")
            raise
    
    async def get_revenue_analytics(
        self,
        user_id: str,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTH,
        currency: str = "EUR",
        db: Session = None
    ) -> Dict[str, Any]:
        """        Get comprehensive revenue analytics and financial insights.
        
        Args:
            user_id: User identifier
            timeframe: Analysis timeframe
            currency: Currency for revenue calculations
            db: Database session
            
        Returns:
            Revenue analytics data
        """        if db is None:
            db = next(get_db())
        
        try:
            revenue_data = {
                "summary": await self._generate_revenue_summary(user_id, timeframe, currency, db),
                "by_platform": await self._analyze_revenue_by_platform(user_id, timeframe, currency, db),
                "by_content": await self._analyze_revenue_by_content(user_id, timeframe, currency, db),
                "trends": await self._analyze_revenue_trends(user_id, timeframe, currency, db),
                "forecasting": await self._forecast_revenue(user_id, timeframe, currency, db),
                "protection_impact": await self._analyze_protection_revenue_impact(
                    user_id, timeframe, currency, db
                ),
                "optimization": await self._generate_revenue_optimization_suggestions(
                    user_id, timeframe, currency, db
                )
            }
            
            return revenue_data
            
        except Exception as e:
            logger.error(f"Error getting revenue analytics: {str(e)}")
            raise
    
    async def get_audience_analytics(
        self,
        user_id: str,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTH,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Get comprehensive audience analytics and demographic insights.
        
        Args:
            user_id: User identifier
            timeframe: Analysis timeframe
            db: Database session
            
        Returns:
            Audience analytics data
        """        if db is None:
            db = next(get_db())
        
        try:
            audience_data = {
                "demographics": await self._analyze_audience_demographics(user_id, timeframe, db),
                "behavior": await self._analyze_audience_behavior(user_id, timeframe, db),
                "engagement_patterns": await self._analyze_engagement_patterns(user_id, timeframe, db),
                "growth": await self._analyze_audience_growth(user_id, timeframe, db),
                "segmentation": await self._segment_audience(user_id, timeframe, db),
                "retention": await self._analyze_audience_retention(user_id, timeframe, db),
                "preferences": await self._analyze_content_preferences(user_id, timeframe, db)
            }
            
            return audience_data
            
        except Exception as e:
            logger.error(f"Error getting audience analytics: {str(e)}")
            raise
    
    async def get_protection_analytics(
        self,
        user_id: str,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTH,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Get comprehensive content protection analytics.
        
        Args:
            user_id: User identifier
            timeframe: Analysis timeframe
            db: Database session
            
        Returns:
            Protection analytics data
        """        if db is None:
            db = next(get_db())
        
        try:
            protection_data = {
                "overview": await self._generate_protection_overview(user_id, timeframe, db),
                "threats_detected": await self._analyze_threats_detected(user_id, timeframe, db),
                "protection_effectiveness": await self._analyze_protection_effectiveness(
                    user_id, timeframe, db
                ),
                "false_positives": await self._analyze_false_positives(user_id, timeframe, db),
                "resolution_rate": await self._calculate_resolution_rate(user_id, timeframe, db),
                "financial_impact": await self._calculate_protection_financial_impact(
                    user_id, timeframe, db
                ),
                "recommendations": await self._generate_protection_recommendations(
                    user_id, timeframe, db
                )
            }
            
            return protection_data
            
        except Exception as e:
            logger.error(f"Error getting protection analytics: {str(e)}")
            raise
    
    async def generate_analytics_report(
        self,
        user_id: str,
        report_type: str = "comprehensive",
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTH,
        format_type: str = "pdf",
        db: Session = None
    ) -> Dict[str, Any]:
        """        Generate comprehensive analytics report.
        
        Args:
            user_id: User identifier
            report_type: Type of report to generate
            timeframe: Analysis timeframe
            format_type: Output format (pdf, json, csv)
            db: Database session
            
        Returns:
            Generated report data and metadata
        """        if db is None:
            db = next(get_db())
        
        try:
            # Gather all analytics data
            report_data = {
                "metadata": {
                    "user_id": user_id,
                    "report_type": report_type,
                    "timeframe": timeframe.value,
                    "generated_at": datetime.utcnow(),
                    "format": format_type
                }
            }
            
            if report_type in ["comprehensive", "content"]:
                report_data["content_analytics"] = await self.get_content_analytics(
                    user_id, timeframe=timeframe, db=db
                )
            
            if report_type in ["comprehensive", "platform"]:
                report_data["platform_analytics"] = await self.get_platform_analytics(
                    user_id, timeframe=timeframe, db=db
                )
            
            if report_type in ["comprehensive", "revenue"]:
                report_data["revenue_analytics"] = await self.get_revenue_analytics(
                    user_id, timeframe=timeframe, db=db
                )
            
            if report_type in ["comprehensive", "audience"]:
                report_data["audience_analytics"] = await self.get_audience_analytics(
                    user_id, timeframe=timeframe, db=db
                )
            
            if report_type in ["comprehensive", "protection"]:
                report_data["protection_analytics"] = await self.get_protection_analytics(
                    user_id, timeframe=timeframe, db=db
                )
            
            # Generate visualizations
            if format_type in ["pdf", "html"]:
                report_data["visualizations"] = await self._generate_report_visualizations(
                    report_data, format_type
                )
            
            # Format output
            formatted_report = await self._format_report(report_data, format_type)
            
            return {
                "report": formatted_report,
                "download_url": await self._store_report(formatted_report, user_id),
                "metadata": report_data["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {str(e)}")
            raise
    
    # Private helper methods
    async def _generate_content_overview(self, contents: List[Content], timeframe: AnalyticsTimeframe, db: Session) -> Dict[str, Any]:
        """Generate content overview statistics."""        total_contents = len(contents)
        
        # Calculate content type distribution
        type_distribution = {}
        for content in contents:
            content_type = content.content_type
            type_distribution[content_type] = type_distribution.get(content_type, 0) + 1
        
        # Calculate performance metrics
        total_views = sum(content.view_count or 0 for content in contents)
        total_likes = sum(content.like_count or 0 for content in contents)
        total_shares = sum(content.share_count or 0 for content in contents)
        
        avg_engagement_rate = np.mean([
            content.engagement_rate or 0 for content in contents
        ]) if contents else 0
        
        return {
            "total_contents": total_contents,
            "content_types": type_distribution,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_shares": total_shares,
            "average_engagement_rate": round(avg_engagement_rate, 2),
            "most_popular_type": max(type_distribution.items(), key=lambda x: x[1])[0] if type_distribution else None
        }
    
    async def _analyze_content_performance(self, contents: List[Content], timeframe: AnalyticsTimeframe, db: Session) -> List[ContentPerformanceMetrics]:
        """Analyze individual content performance."""        performance_data = []
        
        for content in contents:
            metrics = ContentPerformanceMetrics(
                content_id=content.id,
                views=content.view_count or 0,
                likes=content.like_count or 0,
                shares=content.share_count or 0,
                comments=content.comment_count or 0,
                engagement_rate=content.engagement_rate or 0,
                reach=content.reach or 0,
                impressions=content.impressions or 0,
                click_through_rate=content.click_through_rate or 0,
                conversion_rate=content.conversion_rate or 0,
                revenue_generated=content.revenue_generated or 0
            )
            performance_data.append(metrics)
        
        # Sort by performance score
        performance_data.sort(
            key=lambda x: x.engagement_rate * x.views,
            reverse=True
        )
        
        return performance_data
    
    async def _analyze_engagement_metrics(self, contents: List[Content], timeframe: AnalyticsTimeframe, db: Session) -> Dict[str, Any]:
        """Analyze engagement patterns and metrics."""        if not contents:
            return {"error": "No content available for analysis"}
        
        engagement_data = {
            "average_engagement_rate": np.mean([c.engagement_rate or 0 for c in contents]),
            "median_engagement_rate": np.median([c.engagement_rate or 0 for c in contents]),
            "best_performing_content": max(contents, key=lambda x: x.engagement_rate or 0),
            "engagement_by_type": {},
            "engagement_trends": await self._calculate_engagement_trends(contents, timeframe)
        }
        
        # Group by content type
        type_engagement = {}
        for content in contents:
            content_type = content.content_type
            if content_type not in type_engagement:
                type_engagement[content_type] = []
            type_engagement[content_type].append(content.engagement_rate or 0)
        
        for content_type, rates in type_engagement.items():
            engagement_data["engagement_by_type"][content_type] = {
                "average": np.mean(rates),
                "count": len(rates)
            }
        
        return engagement_data
    
    async def _calculate_engagement_trends(self, contents: List[Content], timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Calculate engagement trends over time."""        # Group content by time periods
        time_periods = get_time_periods(timeframe)
        trends = {}
        
        for period in time_periods:
            period_contents = [
                c for c in contents
                if c.created_at >= period["start"] and c.created_at <= period["end"]
            ]
            
            if period_contents:
                avg_engagement = np.mean([c.engagement_rate or 0 for c in period_contents])
                trends[period["label"]] = avg_engagement
        
        return trends
    
    async def _generate_content_insights(self, contents: List[Content], timeframe: AnalyticsTimeframe, db: Session) -> List[AnalyticsInsight]:
        """Generate actionable insights from content data."""        insights = []
        
        if not contents:
            return insights
        
        # Engagement insight
        avg_engagement = np.mean([c.engagement_rate or 0 for c in contents])
        engagement_trend = "stable"  # Simplified - would calculate actual trend
        
        insights.append(AnalyticsInsight(
            metric="engagement_rate",
            value=avg_engagement,
            trend=engagement_trend,
            change_percentage=0.0,  # Simplified
            recommendation="Focus on interactive content to boost engagement",
            timestamp=datetime.utcnow()
        ))
        
        # Content type performance insight
        type_performance = {}
        for content in contents:
            content_type = content.content_type
            if content_type not in type_performance:
                type_performance[content_type] = []
            type_performance[content_type].append(content.engagement_rate or 0)
        
        if type_performance:
            best_type = max(type_performance.items(), key=lambda x: np.mean(x[1]))
            insights.append(AnalyticsInsight(
                metric="content_type_performance",
                value=np.mean(best_type[1]),
                trend="up",
                change_percentage=0.0,
                recommendation=f"Increase {best_type[0]} content production",
                timestamp=datetime.utcnow()
            ))
        
        return insights
    
    async def _generate_content_recommendations(self, contents: List[Content], timeframe: AnalyticsTimeframe, db: Session) -> List[str]:
        """Generate content optimization recommendations."""        recommendations = []
        
        if not contents:
            return ["Start creating content to get personalized recommendations"]
        
        # Analyze content performance patterns
        if len(contents) >= 5:
            engagement_rates = [c.engagement_rate or 0 for c in contents]
            if np.std(engagement_rates) > 0.1:
                recommendations.append("Content engagement varies significantly - analyze top performers")
        
        # Content type recommendations
        type_counts = {}
        for content in contents:
            content_type = content.content_type
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        
        if len(type_counts) == 1:
            recommendations.append("Diversify content types to reach broader audience")
        
        # Frequency recommendations
        if len(contents) < 10:
            recommendations.append("Increase content publishing frequency for better reach")
        
        return recommendations
