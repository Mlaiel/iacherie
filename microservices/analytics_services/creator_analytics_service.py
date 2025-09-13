#!/usr/bin/env python3
"""
👤 CREATOR ANALYTICS SERVICE
===========================

Advanced creator performance analytics and insights service for the Ainflue platform.
Provides detailed analytics for creator performance, audience insights, and revenue tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import uuid
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreatorType(Enum):
    """Creator type enumeration"""
    MUSICIAN = "musician"
    BLOGGER = "blogger" 
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"

class MetricType(Enum):
    """Metric type enumeration"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    REVENUE = "revenue"
    GROWTH = "growth"
    AUDIENCE = "audience"
    CONTENT = "content"

class TimeFrame(Enum):
    """Time frame enumeration"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class CreatorProfile:
    """Creator profile for analytics"""
    creator_id: str
    username: str
    creator_type: CreatorType
    join_date: datetime
    verified: bool = False
    follower_count: int = 0
    total_content: int = 0
    total_revenue: float = 0.0
    avg_engagement_rate: float = 0.0

@dataclass
class ContentMetrics:
    """Content performance metrics"""
    content_id: str
    creator_id: str
    content_type: str
    title: str
    upload_date: datetime
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    engagement_rate: float = 0.0
    revenue_generated: float = 0.0
    reach: int = 0

@dataclass
class AudienceInsights:
    """Audience insights data"""
    creator_id: str
    timestamp: datetime
    demographics: Dict[str, Any]
    geographic_distribution: Dict[str, float]
    device_breakdown: Dict[str, float]
    peak_activity_hours: List[int]
    interests: List[str]
    retention_rate: float = 0.0

@dataclass
class RevenueAnalytics:
    """Revenue analytics data"""
    creator_id: str
    period: str
    total_revenue: float
    revenue_sources: Dict[str, float]
    average_transaction: float
    transaction_count: int
    growth_rate: float = 0.0
    timestamp: datetime = None

class CreatorAnalyticsService:
    """Advanced creator performance analytics and insights service"""
    
    def __init__(self):
        self.service_name = "CreatorAnalyticsService"
        self.version = "1.0.0"
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.content_metrics: Dict[str, ContentMetrics] = {}
        self.audience_insights: Dict[str, AudienceInsights] = {}
        self.revenue_analytics: Dict[str, List[RevenueAnalytics]] = defaultdict(list)
        self.redis_client: Optional[redis.Redis] = None
        self.analytics_cache: Dict[str, Any] = {}
        self.processing_enabled = True
        self.processing_tasks: List[asyncio.Task] = []
        
        logger.info(f"✅ {self.service_name} v{self.version} initialized")
    
    async def initialize(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize the creator analytics service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            
            # Load existing data
            await self._load_analytics_data()
            
            # Setup demo data for testing
            await self._setup_demo_data()
            
            logger.info(f"👤 {self.service_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.service_name}: {str(e)}")
            return False
    
    async def _setup_demo_data(self):
        """Setup demo creator data for testing"""
        # Demo creator profiles
        demo_creators = [
            CreatorProfile(
                creator_id="creator_001",
                username="MusicMaestro",
                creator_type=CreatorType.MUSICIAN,
                join_date=datetime.now() - timedelta(days=365),
                verified=True,
                follower_count=150000,
                total_content=45,
                total_revenue=25000.0,
                avg_engagement_rate=0.078
            ),
            CreatorProfile(
                creator_id="creator_002", 
                username="TechBlogger",
                creator_type=CreatorType.BLOGGER,
                join_date=datetime.now() - timedelta(days=180),
                verified=False,
                follower_count=75000,
                total_content=120,
                total_revenue=15000.0,
                avg_engagement_rate=0.065
            ),
            CreatorProfile(
                creator_id="creator_003",
                username="PhotoPro",
                creator_type=CreatorType.PHOTOGRAPHER,
                join_date=datetime.now() - timedelta(days=90),
                verified=True,
                follower_count=200000,
                total_content=300,
                total_revenue=40000.0,
                avg_engagement_rate=0.092
            )
        ]
        
        for creator in demo_creators:
            await self.add_creator_profile(creator)
            
            # Generate demo content metrics
            await self._generate_demo_content_metrics(creator.creator_id)
            
            # Generate demo audience insights
            await self._generate_demo_audience_insights(creator.creator_id)
            
            # Generate demo revenue analytics
            await self._generate_demo_revenue_analytics(creator.creator_id)
        
        logger.info(f"🎭 Generated demo data for {len(demo_creators)} creators")
    
    async def _generate_demo_content_metrics(self, creator_id: str):
        """Generate demo content metrics"""
        content_types = ["video", "image", "audio", "blog_post"]
        
        for i in range(10):  # Generate 10 pieces of content per creator
            content = ContentMetrics(
                content_id=f"{creator_id}_content_{i}",
                creator_id=creator_id,
                content_type=np.random.choice(content_types),
                title=f"Content {i+1}",
                upload_date=datetime.now() - timedelta(days=np.random.randint(1, 90)),
                views=np.random.randint(1000, 50000),
                likes=np.random.randint(50, 5000),
                comments=np.random.randint(10, 500),
                shares=np.random.randint(5, 200),
                revenue_generated=np.random.uniform(10, 500),
                reach=np.random.randint(800, 40000)
            )
            
            # Calculate engagement rate
            total_interactions = content.likes + content.comments + content.shares
            content.engagement_rate = total_interactions / content.views if content.views > 0 else 0
            
            await self.add_content_metrics(content)
    
    async def _generate_demo_audience_insights(self, creator_id: str):
        """Generate demo audience insights"""
        insights = AudienceInsights(
            creator_id=creator_id,
            timestamp=datetime.now(),
            demographics={
                "age_groups": {
                    "18-24": 0.25,
                    "25-34": 0.35,
                    "35-44": 0.25,
                    "45-54": 0.10,
                    "55+": 0.05
                },
                "gender": {
                    "male": 0.45,
                    "female": 0.50,
                    "other": 0.05
                }
            },
            geographic_distribution={
                "US": 0.40,
                "UK": 0.15,
                "Canada": 0.12,
                "Australia": 0.08,
                "Germany": 0.10,
                "Others": 0.15
            },
            device_breakdown={
                "mobile": 0.65,
                "desktop": 0.25,
                "tablet": 0.10
            },
            peak_activity_hours=[19, 20, 21, 22],
            interests=["music", "technology", "art", "entertainment", "lifestyle"],
            retention_rate=np.random.uniform(0.70, 0.95)
        )
        
        await self.add_audience_insights(insights)
    
    async def _generate_demo_revenue_analytics(self, creator_id: str):
        """Generate demo revenue analytics"""
        periods = ["2024-12", "2025-01", "2025-02", "2025-03"]
        
        for period in periods:
            revenue = RevenueAnalytics(
                creator_id=creator_id,
                period=period,
                total_revenue=np.random.uniform(1000, 5000),
                revenue_sources={
                    "subscriptions": np.random.uniform(200, 1500),
                    "tips": np.random.uniform(100, 800),
                    "sponsorships": np.random.uniform(500, 2000),
                    "merchandise": np.random.uniform(50, 500),
                    "licensing": np.random.uniform(100, 1000)
                },
                average_transaction=np.random.uniform(15, 150),
                transaction_count=np.random.randint(20, 200),
                growth_rate=np.random.uniform(-0.1, 0.3),
                timestamp=datetime.now()
            )
            
            await self.add_revenue_analytics(revenue)
    
    async def add_creator_profile(self, profile: CreatorProfile):
        """Add a creator profile"""
        self.creator_profiles[profile.creator_id] = profile
        await self._save_creator_profile(profile)
        logger.info(f"👤 Added creator profile: {profile.username}")
    
    async def add_content_metrics(self, metrics: ContentMetrics):
        """Add content metrics"""
        self.content_metrics[metrics.content_id] = metrics
        await self._save_content_metrics(metrics)
        logger.debug(f"📊 Added content metrics: {metrics.content_id}")
    
    async def add_audience_insights(self, insights: AudienceInsights):
        """Add audience insights"""
        self.audience_insights[insights.creator_id] = insights
        await self._save_audience_insights(insights)
        logger.info(f"🎯 Added audience insights for: {insights.creator_id}")
    
    async def add_revenue_analytics(self, revenue: RevenueAnalytics):
        """Add revenue analytics"""
        self.revenue_analytics[revenue.creator_id].append(revenue)
        await self._save_revenue_analytics(revenue)
        logger.debug(f"💰 Added revenue analytics: {revenue.creator_id} - {revenue.period}")
    
    async def get_creator_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive creator dashboard data"""
        if creator_id not in self.creator_profiles:
            return {"error": "Creator not found"}
        
        cache_key = f"dashboard_{creator_id}"
        if cache_key in self.analytics_cache:
            cached_data = self.analytics_cache[cache_key]
            if datetime.now() - cached_data['generated_at'] < timedelta(minutes=15):
                return cached_data['data']
        
        try:
            profile = self.creator_profiles[creator_id]
            
            # Get content performance
            creator_content = [
                content for content in self.content_metrics.values()
                if content.creator_id == creator_id
            ]
            
            # Calculate performance metrics
            total_views = sum(content.views for content in creator_content)
            total_engagement = sum(
                content.likes + content.comments + content.shares 
                for content in creator_content
            )
            avg_engagement_rate = np.mean([content.engagement_rate for content in creator_content]) if creator_content else 0
            
            # Get recent revenue
            recent_revenue = self.revenue_analytics.get(creator_id, [])
            total_revenue = sum(rev.total_revenue for rev in recent_revenue)
            
            # Get audience insights
            audience = self.audience_insights.get(creator_id)
            
            # Top performing content
            top_content = sorted(creator_content, key=lambda x: x.views, reverse=True)[:5]
            
            dashboard_data = {
                "creator_profile": asdict(profile),
                "performance_summary": {
                    "total_views": total_views,
                    "total_engagement": total_engagement,
                    "avg_engagement_rate": avg_engagement_rate,
                    "content_count": len(creator_content),
                    "total_revenue": total_revenue
                },
                "top_content": [asdict(content) for content in top_content],
                "audience_insights": asdict(audience) if audience else None,
                "revenue_trend": [asdict(rev) for rev in recent_revenue[-6:]],  # Last 6 periods
                "growth_metrics": await self._calculate_growth_metrics(creator_id),
                "generated_at": datetime.now().isoformat()
            }
            
            # Cache the dashboard data
            self.analytics_cache[cache_key] = {
                'data': dashboard_data,
                'generated_at': datetime.now()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Error generating dashboard for {creator_id}: {str(e)}")
            return {"error": str(e)}
    
    async def _calculate_growth_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Calculate growth metrics for a creator"""
        try:
            # Get content from last 30 days vs previous 30 days
            current_period = datetime.now() - timedelta(days=30)
            previous_period = datetime.now() - timedelta(days=60)
            
            current_content = [
                content for content in self.content_metrics.values()
                if (content.creator_id == creator_id and 
                    content.upload_date >= current_period)
            ]
            
            previous_content = [
                content for content in self.content_metrics.values()
                if (content.creator_id == creator_id and 
                    previous_period <= content.upload_date < current_period)
            ]
            
            # Calculate metrics
            current_views = sum(content.views for content in current_content)
            previous_views = sum(content.views for content in previous_content)
            
            current_engagement = sum(
                content.likes + content.comments + content.shares 
                for content in current_content
            )
            previous_engagement = sum(
                content.likes + content.comments + content.shares 
                for content in previous_content
            )
            
            # Calculate growth rates
            views_growth = ((current_views - previous_views) / previous_views * 100) if previous_views > 0 else 0
            engagement_growth = ((current_engagement - previous_engagement) / previous_engagement * 100) if previous_engagement > 0 else 0
            
            # Revenue growth
            current_revenue_data = [
                rev for rev in self.revenue_analytics.get(creator_id, [])
                if datetime.strptime(rev.period, "%Y-%m") >= current_period.replace(day=1)
            ]
            current_revenue = sum(rev.total_revenue for rev in current_revenue_data)
            
            previous_revenue_data = [
                rev for rev in self.revenue_analytics.get(creator_id, [])
                if (previous_period.replace(day=1) <= 
                    datetime.strptime(rev.period, "%Y-%m") < 
                    current_period.replace(day=1))
            ]
            previous_revenue = sum(rev.total_revenue for rev in previous_revenue_data)
            
            revenue_growth = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            return {
                "views_growth": views_growth,
                "engagement_growth": engagement_growth,
                "revenue_growth": revenue_growth,
                "content_frequency": len(current_content) / 30,  # Content per day
                "performance_score": (views_growth + engagement_growth + revenue_growth) / 3
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating growth metrics: {str(e)}")
            return {}
    
    async def get_content_performance_analysis(self, creator_id: str, 
                                             timeframe: TimeFrame = TimeFrame.MONTH) -> Dict[str, Any]:
        """Get detailed content performance analysis"""
        try:
            # Get timeframe data
            if timeframe == TimeFrame.DAY:
                start_date = datetime.now() - timedelta(days=1)
            elif timeframe == TimeFrame.WEEK:
                start_date = datetime.now() - timedelta(weeks=1)
            elif timeframe == TimeFrame.MONTH:
                start_date = datetime.now() - timedelta(days=30)
            elif timeframe == TimeFrame.QUARTER:
                start_date = datetime.now() - timedelta(days=90)
            else:
                start_date = datetime.now() - timedelta(days=365)
            
            content_data = [
                content for content in self.content_metrics.values()
                if (content.creator_id == creator_id and 
                    content.upload_date >= start_date)
            ]
            
            if not content_data:
                return {"message": "No content found for the specified timeframe"}
            
            # Content type analysis
            content_by_type = defaultdict(list)
            for content in content_data:
                content_by_type[content.content_type].append(content)
            
            type_performance = {}
            for content_type, contents in content_by_type.items():
                avg_views = np.mean([c.views for c in contents])
                avg_engagement = np.mean([c.engagement_rate for c in contents])
                total_revenue = sum(c.revenue_generated for c in contents)
                
                type_performance[content_type] = {
                    "count": len(contents),
                    "avg_views": avg_views,
                    "avg_engagement_rate": avg_engagement,
                    "total_revenue": total_revenue
                }
            
            # Best performing content
            best_by_views = max(content_data, key=lambda x: x.views)
            best_by_engagement = max(content_data, key=lambda x: x.engagement_rate)
            best_by_revenue = max(content_data, key=lambda x: x.revenue_generated)
            
            # Performance trends
            content_df = pd.DataFrame([
                {
                    'date': content.upload_date.date(),
                    'views': content.views,
                    'engagement_rate': content.engagement_rate,
                    'revenue': content.revenue_generated
                }
                for content in content_data
            ])
            
            daily_performance = content_df.groupby('date').agg({
                'views': 'sum',
                'engagement_rate': 'mean',
                'revenue': 'sum'
            }).to_dict('index')
            
            return {
                "timeframe": timeframe.value,
                "content_count": len(content_data),
                "total_views": sum(c.views for c in content_data),
                "avg_engagement_rate": np.mean([c.engagement_rate for c in content_data]),
                "total_revenue": sum(c.revenue_generated for c in content_data),
                "performance_by_type": type_performance,
                "best_performers": {
                    "by_views": asdict(best_by_views),
                    "by_engagement": asdict(best_by_engagement),
                    "by_revenue": asdict(best_by_revenue)
                },
                "daily_trends": {
                    str(date): metrics for date, metrics in daily_performance.items()
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in content performance analysis: {str(e)}")
            return {"error": str(e)}
    
    async def get_audience_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get detailed audience analytics"""
        try:
            audience = self.audience_insights.get(creator_id)
            if not audience:
                return {"message": "No audience data found"}
            
            # Calculate audience growth (simulated)
            profile = self.creator_profiles.get(creator_id)
            if profile:
                # Estimate growth based on join date
                days_since_join = (datetime.now() - profile.join_date).days
                estimated_daily_growth = profile.follower_count / days_since_join if days_since_join > 0 else 0
                
                growth_projection = {
                    "current_followers": profile.follower_count,
                    "estimated_daily_growth": estimated_daily_growth,
                    "projected_30_day": profile.follower_count + (estimated_daily_growth * 30),
                    "projected_90_day": profile.follower_count + (estimated_daily_growth * 90)
                }
            else:
                growth_projection = {}
            
            # Engagement analysis
            creator_content = [
                content for content in self.content_metrics.values()
                if content.creator_id == creator_id
            ]
            
            engagement_by_hour = defaultdict(list)
            for content in creator_content:
                hour = content.upload_date.hour
                engagement_by_hour[hour].append(content.engagement_rate)
            
            optimal_posting_hours = []
            for hour, rates in engagement_by_hour.items():
                if rates:
                    avg_rate = np.mean(rates)
                    optimal_posting_hours.append((hour, avg_rate))
            
            optimal_posting_hours.sort(key=lambda x: x[1], reverse=True)
            
            return {
                "audience_insights": asdict(audience),
                "growth_projection": growth_projection,
                "optimal_posting_times": optimal_posting_hours[:5],
                "engagement_recommendations": await self._generate_engagement_recommendations(creator_id),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in audience analytics: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_engagement_recommendations(self, creator_id: str) -> List[str]:
        """Generate engagement recommendations for creator"""
        recommendations = []
        
        try:
            # Analyze content performance
            creator_content = [
                content for content in self.content_metrics.values()
                if content.creator_id == creator_id
            ]
            
            if not creator_content:
                return ["Create more content to get personalized recommendations"]
            
            # Analyze by content type
            content_by_type = defaultdict(list)
            for content in creator_content:
                content_by_type[content.content_type].append(content)
            
            best_type = max(content_by_type.items(), 
                          key=lambda x: np.mean([c.engagement_rate for c in x[1]]))
            
            recommendations.append(f"Focus on {best_type[0]} content - it has your highest engagement rate")
            
            # Analyze posting frequency
            recent_content = [
                c for c in creator_content 
                if c.upload_date >= datetime.now() - timedelta(days=30)
            ]
            
            posting_frequency = len(recent_content) / 30
            if posting_frequency < 0.5:
                recommendations.append("Increase posting frequency - aim for at least 3-4 posts per week")
            elif posting_frequency > 2:
                recommendations.append("Consider quality over quantity - focus on high-engagement content")
            
            # Engagement rate analysis
            avg_engagement = np.mean([c.engagement_rate for c in creator_content])
            if avg_engagement < 0.05:
                recommendations.append("Try interactive content like polls, Q&As, or behind-the-scenes content")
            
            # Revenue optimization
            revenue_per_content = np.mean([c.revenue_generated for c in creator_content])
            if revenue_per_content < 50:
                recommendations.append("Explore monetization options like sponsorships or premium content")
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {str(e)}")
            recommendations.append("Unable to generate recommendations at this time")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def get_revenue_report(self, creator_id: str, 
                               periods: int = 6) -> Dict[str, Any]:
        """Get comprehensive revenue report"""
        try:
            revenue_data = self.revenue_analytics.get(creator_id, [])
            
            if not revenue_data:
                return {"message": "No revenue data found"}
            
            # Get recent periods
            recent_revenue = sorted(revenue_data, key=lambda x: x.period, reverse=True)[:periods]
            
            # Calculate totals and trends
            total_revenue = sum(rev.total_revenue for rev in recent_revenue)
            avg_revenue = total_revenue / len(recent_revenue) if recent_revenue else 0
            
            # Revenue source breakdown
            source_totals = defaultdict(float)
            for rev in recent_revenue:
                for source, amount in rev.revenue_sources.items():
                    source_totals[source] += amount
            
            # Growth analysis
            growth_rates = [rev.growth_rate for rev in recent_revenue if rev.growth_rate is not None]
            avg_growth_rate = np.mean(growth_rates) if growth_rates else 0
            
            # Projections
            if len(recent_revenue) >= 2:
                recent_trend = recent_revenue[0].total_revenue - recent_revenue[1].total_revenue
                projected_next_month = recent_revenue[0].total_revenue + recent_trend
            else:
                projected_next_month = avg_revenue
            
            return {
                "creator_id": creator_id,
                "analysis_period": f"Last {len(recent_revenue)} periods",
                "total_revenue": total_revenue,
                "average_monthly_revenue": avg_revenue,
                "revenue_by_source": dict(source_totals),
                "growth_metrics": {
                    "average_growth_rate": avg_growth_rate,
                    "projected_next_month": max(0, projected_next_month),
                    "revenue_stability": np.std([rev.total_revenue for rev in recent_revenue])
                },
                "period_breakdown": [asdict(rev) for rev in recent_revenue],
                "recommendations": await self._generate_revenue_recommendations(creator_id, recent_revenue),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in revenue report: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_revenue_recommendations(self, creator_id: str, 
                                              revenue_data: List[RevenueAnalytics]) -> List[str]:
        """Generate revenue optimization recommendations"""
        recommendations = []
        
        try:
            if not revenue_data:
                return ["Start tracking revenue to get personalized recommendations"]
            
            # Analyze revenue sources
            source_performance = defaultdict(list)
            for rev in revenue_data:
                for source, amount in rev.revenue_sources.items():
                    source_performance[source].append(amount)
            
            # Find best performing source
            best_source = max(source_performance.items(), 
                            key=lambda x: np.mean(x[1]))
            
            recommendations.append(f"Double down on {best_source[0]} - it's your top revenue source")
            
            # Find underperforming sources
            for source, amounts in source_performance.items():
                if np.mean(amounts) < np.mean([np.mean(list(amounts)) for amounts in source_performance.values()]) * 0.5:
                    recommendations.append(f"Optimize {source} strategy - potential for growth")
            
            # Growth analysis
            recent_growth = [rev.growth_rate for rev in revenue_data[:3] if rev.growth_rate is not None]
            if recent_growth and np.mean(recent_growth) < 0:
                recommendations.append("Focus on audience engagement to reverse revenue decline")
            
            # Transaction analysis
            avg_transaction = np.mean([rev.average_transaction for rev in revenue_data])
            if avg_transaction < 25:
                recommendations.append("Consider premium offerings to increase average transaction value")
            
        except Exception as e:
            logger.error(f"❌ Error generating revenue recommendations: {str(e)}")
            recommendations.append("Unable to generate revenue recommendations")
        
        return recommendations[:4]
    
    async def _save_creator_profile(self, profile: CreatorProfile):
        """Save creator profile to storage"""
        if self.redis_client:
            try:
                profile_data = asdict(profile)
                profile_data['join_date'] = profile.join_date.isoformat()
                profile_data['creator_type'] = profile.creator_type.value
                
                await self.redis_client.hset(
                    'creator_analytics:profiles',
                    profile.creator_id,
                    json.dumps(profile_data)
                )
            except Exception as e:
                logger.error(f"❌ Failed to save creator profile: {str(e)}")
    
    async def _save_content_metrics(self, metrics: ContentMetrics):
        """Save content metrics to storage"""
        if self.redis_client:
            try:
                metrics_data = asdict(metrics)
                metrics_data['upload_date'] = metrics.upload_date.isoformat()
                
                await self.redis_client.hset(
                    'creator_analytics:content',
                    metrics.content_id,
                    json.dumps(metrics_data)
                )
            except Exception as e:
                logger.error(f"❌ Failed to save content metrics: {str(e)}")
    
    async def _save_audience_insights(self, insights: AudienceInsights):
        """Save audience insights to storage"""
        if self.redis_client:
            try:
                insights_data = asdict(insights)
                insights_data['timestamp'] = insights.timestamp.isoformat()
                
                await self.redis_client.hset(
                    'creator_analytics:audience',
                    insights.creator_id,
                    json.dumps(insights_data)
                )
            except Exception as e:
                logger.error(f"❌ Failed to save audience insights: {str(e)}")
    
    async def _save_revenue_analytics(self, revenue: RevenueAnalytics):
        """Save revenue analytics to storage"""
        if self.redis_client:
            try:
                revenue_data = asdict(revenue)
                if revenue.timestamp:
                    revenue_data['timestamp'] = revenue.timestamp.isoformat()
                
                await self.redis_client.lpush(
                    f'creator_analytics:revenue:{revenue.creator_id}',
                    json.dumps(revenue_data)
                )
                # Keep only last 24 periods
                await self.redis_client.ltrim(
                    f'creator_analytics:revenue:{revenue.creator_id}', 
                    0, 23
                )
            except Exception as e:
                logger.error(f"❌ Failed to save revenue analytics: {str(e)}")
    
    async def _load_analytics_data(self):
        """Load analytics data from storage"""
        if self.redis_client:
            try:
                # Load creator profiles
                profiles_data = await self.redis_client.hgetall('creator_analytics:profiles')
                for creator_id, profile_json in profiles_data.items():
                    profile_data = json.loads(profile_json)
                    profile_data['join_date'] = datetime.fromisoformat(profile_data['join_date'])
                    profile_data['creator_type'] = CreatorType(profile_data['creator_type'])
                    
                    profile = CreatorProfile(**profile_data)
                    self.creator_profiles[creator_id] = profile
                
                logger.info(f"📂 Loaded {len(self.creator_profiles)} creator profiles")
                
            except Exception as e:
                logger.error(f"❌ Failed to load analytics data: {str(e)}")
    
    async def list_creators(self) -> List[Dict[str, Any]]:
        """List all creators with basic info"""
        creators_list = []
        for creator_id, profile in self.creator_profiles.items():
            creator_info = {
                'creator_id': profile.creator_id,
                'username': profile.username,
                'creator_type': profile.creator_type.value,
                'verified': profile.verified,
                'follower_count': profile.follower_count,
                'total_revenue': profile.total_revenue,
                'avg_engagement_rate': profile.avg_engagement_rate
            }
            creators_list.append(creator_info)
        
        return sorted(creators_list, key=lambda x: x['total_revenue'], reverse=True)
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get creator analytics service health status"""
        return {
            'service': self.service_name,
            'version': self.version,
            'total_creators': len(self.creator_profiles),
            'total_content': len(self.content_metrics),
            'cache_entries': len(self.analytics_cache),
            'processing_enabled': self.processing_enabled,
            'redis_connected': self.redis_client is not None,
            'timestamp': datetime.now().isoformat()
        }

# Service instance
creator_analytics_service = CreatorAnalyticsService()

# Example usage
async def main():
    """Example usage of the creator analytics service"""
    try:
        # Initialize service
        await creator_analytics_service.initialize()
        
        # Get creator dashboard
        dashboard = await creator_analytics_service.get_creator_dashboard("creator_001")
        print(f"Creator dashboard: {json.dumps(dashboard, indent=2, default=str)}")
        
        # Get content performance analysis
        content_analysis = await creator_analytics_service.get_content_performance_analysis(
            "creator_001", TimeFrame.MONTH
        )
        print(f"Content analysis: {json.dumps(content_analysis, indent=2, default=str)}")
        
        # Get audience analytics
        audience_analytics = await creator_analytics_service.get_audience_analytics("creator_001")
        print(f"Audience analytics: {json.dumps(audience_analytics, indent=2, default=str)}")
        
        # Get revenue report
        revenue_report = await creator_analytics_service.get_revenue_report("creator_001")
        print(f"Revenue report: {json.dumps(revenue_report, indent=2, default=str)}")
        
        # List all creators
        creators = await creator_analytics_service.list_creators()
        print(f"All creators: {json.dumps(creators, indent=2)}")
        
        # Service health
        health = await creator_analytics_service.get_service_health()
        print(f"Service health: {json.dumps(health, indent=2)}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())