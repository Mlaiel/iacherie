"""Revenue Tracker

Enterprise-grade revenue tracking and monetization optimization system for multi-platform content distribution.
Provides comprehensive revenue analytics, prediction models, and optimization strategies.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and protected. Unauthorized use, reproduction, 
or distribution is strictly prohibited and will result in legal action.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import json
from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import aiohttp
import aioredis
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from pydantic import BaseModel, Field, validator

from ....core.database import get_db
from ....core.config import settings
from ....core.logging import get_logger
from ....core.exceptions import RevenueTrackingError, APIError
from ....utils.encryption import encrypt_data, decrypt_data
from ....utils.monitoring import MetricsCollector, track_performance
from ....utils.payment_processing import PaymentProcessor, PayoutCalculator
from ....models.content import ContentModel
from ....models.user import UserModel
from ....models.revenue import (
    RevenueModel,
    PlatformRevenueModel,
    PayoutModel,
    MonetizationSettingsModel,
    RevenueProjectionModel
)
from ....models.analytics import PlatformPerformanceModel
from .platform_manager import PlatformType


logger = get_logger(__name__)
metrics = MetricsCollector("distribution.revenue_tracker")


class RevenueSource(str, Enum):
    """Revenue source types across platforms"""    AD_REVENUE = "ad_revenue"
    SPONSORED_CONTENT = "sponsored_content"
    AFFILIATE_MARKETING = "affiliate_marketing"
    MERCHANDISE_SALES = "merchandise_sales"
    SUBSCRIPTION_FEES = "subscription_fees"
    TIPS_DONATIONS = "tips_donations"
    LICENSING_FEES = "licensing_fees"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    CREATOR_FUND = "creator_fund"
    LIVE_STREAMING = "live_streaming"
    PREMIUM_CONTENT = "premium_content"
    COURSE_SALES = "course_sales"
    NFT_SALES = "nft_sales"
    CROWDFUNDING = "crowdfunding"
    APPEARANCE_FEES = "appearance_fees"


class PayoutFrequency(str, Enum):
    """Payout frequency options"""    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"
    THRESHOLD_BASED = "threshold_based"


class RevenueStatus(str, Enum):
    """Revenue tracking status"""    PENDING = "pending"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    WITHHELD = "withheld"
    PAID = "paid"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


@dataclass
class RevenueRecord:
    """Individual revenue record"""    id: str
    user_id: str
    content_id: Optional[str]
    platform: PlatformType
    source: RevenueSource
    amount: Decimal
    currency: str
    status: RevenueStatus
    date_earned: datetime
    date_paid: Optional[datetime]
    description: str
    metadata: Dict[str, Any]


@dataclass
class RevenueInsight:
    """Revenue analysis insight"""    insight_type: str
    title: str
    description: str
    impact_score: float
    recommendation: str
    data_points: Dict[str, Any]
    confidence: float


@dataclass
class RevenueForecast:
    """Revenue forecasting data"""    period: str
    predicted_amount: Decimal
    confidence_interval: Tuple[Decimal, Decimal]
    growth_rate: float
    influencing_factors: List[str]


class RevenueTracker:
    """Advanced revenue tracking and analytics system"""    
    def __init__(self, db: Session):
        self.db = db
        self.platform_revenue_rates = self._initialize_platform_rates()
        self.currency_converter = self._initialize_currency_converter()
        
    def _initialize_platform_rates(self) -> Dict[PlatformType, Dict[str, float]]:
        """Initialize platform-specific revenue rates"""        return {
            PlatformType.YOUTUBE: {
                "rpm_base": 2.5,  # Revenue per mille (thousand views)
                "subscriber_bonus": 0.1,  # Additional per subscriber
                "premium_multiplier": 1.5,
                "live_stream_rate": 0.01,  # Per minute watched
                "membership_fee": 4.99
            },
            PlatformType.INSTAGRAM: {
                "reel_rate": 0.001,  # Per view
                "story_rate": 0.0005,
                "post_engagement_rate": 0.05,  # Per engagement
                "igtv_rate": 0.002,
                "live_rate": 0.008
            },
            PlatformType.TIKTOK: {
                "creator_fund_rate": 0.02,  # Per 1000 views
                "live_gift_rate": 0.5,  # Platform takes 50%
                "brand_content_bonus": 1.2
            },
            PlatformType.TWITTER: {
                "super_follow_rate": 0.97,  # Platform takes 3%
                "tip_jar_rate": 1.0,  # No platform fee
                "spaces_rate": 0.005  # Per listener minute
            },
            PlatformType.SPOTIFY: {
                "stream_rate": 0.004,  # Per stream
                "premium_rate": 0.006,
                "podcast_rate": 0.02  # Per download
            },
            PlatformType.LINKEDIN: {
                "newsletter_rate": 0.02,  # Per subscriber
                "course_rate": 0.95,  # Platform takes 5%
                "coaching_rate": 0.9   # Platform takes 10%
            }
        }
    
    def _initialize_currency_converter(self) -> Dict[str, float]:
        """Initialize currency conversion rates (simplified)"""        # In production, this would connect to a real currency API
        return {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.73,
            "CAD": 1.25,
            "AUD": 1.35,
            "JPY": 110.0,
            "CHF": 0.92,
            "CNY": 6.45
        }
    
    async def track_revenue(
        self,
        user_id: str,
        content_id: Optional[str],
        platform: PlatformType,
        source: RevenueSource,
        amount: Decimal,
        currency: str = "USD",
        metadata: Optional[Dict[str, Any]] = None
    ) -> RevenueRecord:
        """Track a new revenue entry"""        try:
            # Convert to USD for standardization
            usd_amount = self._convert_to_usd(amount, currency)
            
            # Create revenue record
            revenue_record = RevenueRecord(
                id=f"rev_{datetime.now().timestamp()}_{user_id}",
                user_id=user_id,
                content_id=content_id,
                platform=platform,
                source=source,
                amount=usd_amount,
                currency="USD",
                status=RevenueStatus.PENDING,
                date_earned=datetime.now(),
                date_paid=None,
                description=f"{source.value} from {platform.value}",
                metadata=metadata or {}
            )
            
            # Store in database (encrypted sensitive data)
            await self._store_revenue_record(revenue_record)
            
            # Update user revenue analytics
            await self._update_user_revenue_analytics(user_id, usd_amount, platform, source)
            
            # Check for revenue milestones
            await self._check_revenue_milestones(user_id, usd_amount)
            
            logger.info(f"Revenue tracked: {usd_amount} USD for user {user_id}")
            return revenue_record
            
        except Exception as e:
            logger.error(f"Error tracking revenue: {e}")
            raise
    
    async def get_revenue_summary(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        platform: Optional[PlatformType] = None
    ) -> Dict[str, Any]:
        """Get comprehensive revenue summary"""        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Base query
            query = self.db.query(AnalyticsModel).filter(
                AnalyticsModel.user_id == user_id,
                AnalyticsModel.date >= start_date,
                AnalyticsModel.date <= end_date
            )
            
            if platform:
                query = query.filter(AnalyticsModel.platform == platform.value)
            
            records = query.all()
            
            # Calculate summary metrics
            total_revenue = sum(Decimal(str(r.revenue)) for r in records if r.revenue)
            total_views = sum(r.views for r in records if r.views)
            total_engagement = sum(r.engagement for r in records if r.engagement)
            
            # Revenue by platform
            platform_revenue = {}
            for record in records:
                platform_name = record.platform
                if platform_name not in platform_revenue:
                    platform_revenue[platform_name] = Decimal('0')
                if record.revenue:
                    platform_revenue[platform_name] += Decimal(str(record.revenue))
            
            # Revenue by source
            source_revenue = {}
            for record in records:
                # This would need to be stored in the analytics model
                # For now, we'll estimate based on platform
                source = self._estimate_revenue_source(record.platform)
                if source not in source_revenue:
                    source_revenue[source] = Decimal('0')
                if record.revenue:
                    source_revenue[source] += Decimal(str(record.revenue))
            
            # Calculate growth rates
            previous_period_start = start_date - (end_date - start_date)
            previous_period_end = start_date
            
            previous_records = self.db.query(AnalyticsModel).filter(
                AnalyticsModel.user_id == user_id,
                AnalyticsModel.date >= previous_period_start,
                AnalyticsModel.date < previous_period_end
            ).all()
            
            previous_revenue = sum(Decimal(str(r.revenue)) for r in previous_records if r.revenue)
            
            growth_rate = float(
                ((total_revenue - previous_revenue) / previous_revenue * 100)
                if previous_revenue > 0 else 0
            )
            
            # RPM (Revenue per mille)
            rpm = float(total_revenue / total_views * 1000) if total_views > 0 else 0
            
            # Engagement rate
            engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else 0
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_revenue": float(total_revenue),
                "total_views": total_views,
                "total_engagement": total_engagement,
                "revenue_per_thousand_views": rpm,
                "engagement_rate": engagement_rate,
                "growth_rate": growth_rate,
                "platform_breakdown": {k: float(v) for k, v in platform_revenue.items()},
                "source_breakdown": {k: float(v) for k, v in source_revenue.items()},
                "top_performing_platform": max(platform_revenue.items(), key=lambda x: x[1])[0] if platform_revenue else None,
                "revenue_trend": await self._calculate_revenue_trend(user_id, start_date, end_date)
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue summary: {e}")
            return {}
    
    async def get_revenue_insights(
        self,
        user_id: str,
        timeframe_days: int = 30
    ) -> List[RevenueInsight]:
        """Generate actionable revenue insights"""        try:
            insights = []
            
            # Get recent revenue data
            start_date = datetime.now() - timedelta(days=timeframe_days)
            summary = await self.get_revenue_summary(user_id, start_date)
            
            # Insight 1: Platform Performance
            platform_breakdown = summary.get("platform_breakdown", {})
            if platform_breakdown:
                top_platform = max(platform_breakdown.items(), key=lambda x: x[1])
                worst_platform = min(platform_breakdown.items(), key=lambda x: x[1])
                
                insights.append(RevenueInsight(
                    insight_type="platform_performance",
                    title="Platform Revenue Analysis",
                    description=f"{top_platform[0]} is your highest revenue platform (${top_platform[1]:.2f})",
                    impact_score=0.8,
                    recommendation=f"Focus more content creation on {top_platform[0]} and optimize {worst_platform[0]} strategy",
                    data_points=platform_breakdown,
                    confidence=0.9
                ))
            
            # Insight 2: Growth Opportunity
            growth_rate = summary.get("growth_rate", 0)
            if growth_rate < 0:
                insights.append(RevenueInsight(
                    insight_type="growth_opportunity",
                    title="Revenue Decline Detected",
                    description=f"Revenue decreased by {abs(growth_rate):.1f}% compared to previous period",
                    impact_score=0.9,
                    recommendation="Review content strategy, engagement tactics, and posting schedule",
                    data_points={"growth_rate": growth_rate},
                    confidence=0.85
                ))
            elif growth_rate > 20:
                insights.append(RevenueInsight(
                    insight_type="growth_opportunity",
                    title="Strong Growth Momentum",
                    description=f"Revenue increased by {growth_rate:.1f}% - maintain this momentum",
                    impact_score=0.7,
                    recommendation="Scale successful content formats and increase posting frequency",
                    data_points={"growth_rate": growth_rate},
                    confidence=0.9
                ))
            
            # Insight 3: RPM Optimization
            rpm = summary.get("revenue_per_thousand_views", 0)
            industry_benchmark = await self._get_industry_rpm_benchmark(user_id)
            
            if rpm < industry_benchmark * 0.8:
                insights.append(RevenueInsight(
                    insight_type="rpm_optimization",
                    title="Below Industry RPM",
                    description=f"Your RPM (${rpm:.2f}) is below industry average (${industry_benchmark:.2f})",
                    impact_score=0.8,
                    recommendation="Optimize content for higher engagement, target valuable keywords, improve audience retention",
                    data_points={"current_rpm": rpm, "benchmark": industry_benchmark},
                    confidence=0.8
                ))
            
            # Insight 4: Engagement Impact
            engagement_rate = summary.get("engagement_rate", 0)
            if engagement_rate < 2.0:  # Low engagement threshold
                insights.append(RevenueInsight(
                    insight_type="engagement_optimization",
                    title="Low Engagement Rate",
                    description=f"Engagement rate of {engagement_rate:.1f}% is limiting revenue potential",
                    impact_score=0.7,
                    recommendation="Create more interactive content, ask questions, use trending topics",
                    data_points={"engagement_rate": engagement_rate},
                    confidence=0.8
                ))
            
            # Insight 5: Diversification Opportunity
            source_breakdown = summary.get("source_breakdown", {})
            if len(source_breakdown) < 3:
                insights.append(RevenueInsight(
                    insight_type="diversification",
                    title="Revenue Source Diversification",
                    description="Limited revenue sources create financial risk",
                    impact_score=0.6,
                    recommendation="Explore sponsorships, affiliate marketing, merchandise, or premium content",
                    data_points={"current_sources": len(source_breakdown)},
                    confidence=0.7
                ))
            
            return sorted(insights, key=lambda x: x.impact_score, reverse=True)
            
        except Exception as e:
            logger.error(f"Error generating revenue insights: {e}")
            return []
    
    async def forecast_revenue(
        self,
        user_id: str,
        forecast_days: int = 30
    ) -> RevenueForecast:
        """Generate revenue forecast based on historical data"""        try:
            # Get historical data (last 90 days)
            historical_start = datetime.now() - timedelta(days=90)
            historical_data = self.db.query(AnalyticsModel).filter(
                AnalyticsModel.user_id == user_id,
                AnalyticsModel.date >= historical_start
            ).all()
            
            if not historical_data:
                return RevenueForecast(
                    period=f"{forecast_days} days",
                    predicted_amount=Decimal('0'),
                    confidence_interval=(Decimal('0'), Decimal('0')),
                    growth_rate=0.0,
                    influencing_factors=["Insufficient historical data"]
                )
            
            # Calculate daily revenue averages
            daily_revenues = {}
            for record in historical_data:
                date_key = record.date.date()
                if date_key not in daily_revenues:
                    daily_revenues[date_key] = Decimal('0')
                if record.revenue:
                    daily_revenues[date_key] += Decimal(str(record.revenue))
            
            # Calculate trend using linear regression (simplified)
            dates = sorted(daily_revenues.keys())
            revenues = [daily_revenues[date] for date in dates]
            
            if len(revenues) < 7:  # Need at least a week of data
                avg_daily = sum(revenues) / len(revenues) if revenues else Decimal('0')
                predicted_amount = avg_daily * forecast_days
                confidence_interval = (
                    predicted_amount * Decimal('0.8'),
                    predicted_amount * Decimal('1.2')
                )
                growth_rate = 0.0
            else:
                # Simple linear trend calculation
                n = len(revenues)
                x_values = list(range(n))
                y_values = [float(r) for r in revenues]
                
                # Calculate slope (trend)
                x_mean = sum(x_values) / n
                y_mean = sum(y_values) / n
                
                numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
                denominator = sum((x - x_mean) ** 2 for x in x_values)
                
                slope = numerator / denominator if denominator != 0 else 0
                intercept = y_mean - slope * x_mean
                
                # Forecast
                future_x = n + forecast_days
                predicted_daily = intercept + slope * future_x
                predicted_amount = Decimal(str(max(0, predicted_daily * forecast_days)))
                
                # Calculate confidence interval based on variance
                variance = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(x_values, y_values)) / n
                std_dev = variance ** 0.5
                
                confidence_interval = (
                    max(Decimal('0'), predicted_amount - Decimal(str(std_dev * forecast_days))),
                    predicted_amount + Decimal(str(std_dev * forecast_days))
                )
                
                # Calculate growth rate
                recent_avg = sum(y_values[-7:]) / 7 if len(y_values) >= 7 else y_mean
                growth_rate = ((predicted_daily - recent_avg) / recent_avg * 100) if recent_avg > 0 else 0
            
            # Identify influencing factors
            influencing_factors = await self._identify_influencing_factors(user_id, historical_data)
            
            return RevenueForecast(
                period=f"{forecast_days} days",
                predicted_amount=predicted_amount,
                confidence_interval=confidence_interval,
                growth_rate=growth_rate,
                influencing_factors=influencing_factors
            )
            
        except Exception as e:
            logger.error(f"Error forecasting revenue: {e}")
            return RevenueForecast(
                period=f"{forecast_days} days",
                predicted_amount=Decimal('0'),
                confidence_interval=(Decimal('0'), Decimal('0')),
                growth_rate=0.0,
                influencing_factors=[f"Forecast error: {str(e)}"]
            )
    
    async def optimize_revenue_strategy(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Generate personalized revenue optimization recommendations"""        try:
            # Get user's performance data
            summary = await self.get_revenue_summary(user_id)
            insights = await self.get_revenue_insights(user_id)
            forecast = await self.forecast_revenue(user_id)
            
            # Analyze platform performance
            platform_breakdown = summary.get("platform_breakdown", {})
            top_platforms = sorted(platform_breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Generate optimization strategies
            strategies = []
            
            # Strategy 1: Platform Focus
            if top_platforms:
                strategies.append({
                    "type": "platform_optimization",
                    "priority": "high",
                    "title": "Focus on Top Performing Platforms",
                    "description": f"Allocate 60% of content to {top_platforms[0][0]}",
                    "expected_impact": "15-25% revenue increase",
                    "action_items": [
                        f"Increase posting frequency on {top_platforms[0][0]}",
                        "Study top-performing content formats",
                        "Optimize posting times for maximum engagement"
                    ]
                })
            
            # Strategy 2: Revenue Diversification
            current_sources = len(summary.get("source_breakdown", {}))
            if current_sources < 3:
                strategies.append({
                    "type": "diversification",
                    "priority": "medium",
                    "title": "Diversify Revenue Sources",
                    "description": "Add 2-3 new revenue streams to reduce risk",
                    "expected_impact": "20-40% revenue increase",
                    "action_items": [
                        "Launch affiliate marketing program",
                        "Create premium content offerings",
                        "Explore brand partnership opportunities",
                        "Consider merchandise or course sales"
                    ]
                })
            
            # Strategy 3: Engagement Optimization
            engagement_rate = summary.get("engagement_rate", 0)
            if engagement_rate < 3.0:
                strategies.append({
                    "type": "engagement_boost",
                    "priority": "high",
                    "title": "Boost Audience Engagement",
                    "description": f"Target 5%+ engagement rate (current: {engagement_rate:.1f}%)",
                    "expected_impact": "10-20% revenue increase",
                    "action_items": [
                        "Create more interactive content (polls, Q&A)",
                        "Respond to comments within 2 hours",
                        "Use trending hashtags and topics",
                        "Collaborate with other creators"
                    ]
                })
            
            # Strategy 4: Content Quality Enhancement
            rpm = summary.get("revenue_per_thousand_views", 0)
            industry_benchmark = await self._get_industry_rpm_benchmark(user_id)
            
            if rpm < industry_benchmark:
                strategies.append({
                    "type": "content_quality",
                    "priority": "medium",
                    "title": "Improve Content Monetization",
                    "description": f"Target ${industry_benchmark:.2f} RPM (current: ${rpm:.2f})",
                    "expected_impact": "25-35% revenue increase",
                    "action_items": [
                        "Create longer-form content for better ad placement",
                        "Target high-value keywords in your niche",
                        "Improve video/content retention rates",
                        "Optimize thumbnails and titles for CTR"
                    ]
                })
            
            # Generate implementation timeline
            timeline = self._create_implementation_timeline(strategies)
            
            # Calculate potential revenue impact
            current_monthly = float(summary.get("total_revenue", 0)) * 30 / 30  # Normalize to monthly
            potential_increase = sum(
                current_monthly * (float(s.get("expected_impact", "0%").split("-")[0].rstrip("%")) / 100)
                for s in strategies
            )
            
            return {
                "current_revenue": summary.get("total_revenue", 0),
                "forecast": {
                    "next_30_days": float(forecast.predicted_amount),
                    "growth_rate": forecast.growth_rate,
                    "confidence": "medium" if abs(forecast.growth_rate) < 10 else "high"
                },
                "optimization_strategies": strategies,
                "implementation_timeline": timeline,
                "potential_impact": {
                    "additional_monthly_revenue": potential_increase,
                    "percentage_increase": (potential_increase / current_monthly * 100) if current_monthly > 0 else 0
                },
                "key_insights": [insight.title for insight in insights[:3]],
                "next_actions": [
                    action for strategy in strategies[:2]
                    for action in strategy.get("action_items", [])[:2]
                ]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing revenue strategy: {e}")
            return {}
    
    def _convert_to_usd(self, amount: Decimal, currency: str) -> Decimal:
        """Convert amount to USD"""        if currency == "USD":
            return amount
        
        rate = self.currency_converter.get(currency, 1.0)
        return amount / Decimal(str(rate))
    
    async def _store_revenue_record(self, record: RevenueRecord) -> None:
        """Store revenue record in database (with encryption)"""        # This would store in a dedicated revenue table
        # For now, we'll update the analytics model
        pass
    
    async def _update_user_revenue_analytics(
        self,
        user_id: str,
        amount: Decimal,
        platform: PlatformType,
        source: RevenueSource
    ) -> None:
        """Update user's revenue analytics"""        # This would update aggregated revenue metrics
        pass
    
    async def _check_revenue_milestones(self, user_id: str, amount: Decimal) -> None:
        """Check and trigger revenue milestone notifications"""        # Implementation for milestone checking
        pass
    
    def _estimate_revenue_source(self, platform: str) -> str:
        """Estimate revenue source based on platform"""        source_map = {
            "youtube": "ad_revenue",
            "instagram": "sponsorship",
            "tiktok": "creator_fund",
            "twitter": "subscription",
            "spotify": "streaming",
            "linkedin": "premium_content"
        }
        return source_map.get(platform.lower(), "other")
    
    async def _calculate_revenue_trend(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Calculate daily revenue trend"""        try:
            records = self.db.query(AnalyticsModel).filter(
                AnalyticsModel.user_id == user_id,
                AnalyticsModel.date >= start_date,
                AnalyticsModel.date <= end_date
            ).all()
            
            daily_data = {}
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            # Initialize all dates with zero
            while current_date <= end_date_only:
                daily_data[current_date] = 0.0
                current_date += timedelta(days=1)
            
            # Fill in actual revenue data
            for record in records:
                date_key = record.date.date()
                if record.revenue:
                    daily_data[date_key] += float(record.revenue)
            
            # Convert to list format
            trend = [
                {
                    "date": date.isoformat(),
                    "revenue": revenue
                }
                for date, revenue in sorted(daily_data.items())
            ]
            
            return trend
            
        except Exception as e:
            logger.error(f"Error calculating revenue trend: {e}")
            return []
    
    async def _get_industry_rpm_benchmark(self, user_id: str) -> float:
        """Get industry RPM benchmark for user's niche"""        # This would typically analyze user's content category and provide benchmarks
        # For now, return a general benchmark
        return 2.5  # $2.50 per 1000 views
    
    async def _identify_influencing_factors(
        self,
        user_id: str,
        historical_data: List[AnalyticsModel]
    ) -> List[str]:
        """Identify factors influencing revenue trends"""        factors = []
        
        # Analyze view patterns
        recent_views = [r.views for r in historical_data[-7:] if r.views]
        older_views = [r.views for r in historical_data[-30:-7] if r.views]
        
        if recent_views and older_views:
            recent_avg = sum(recent_views) / len(recent_views)
            older_avg = sum(older_views) / len(older_views)
            
            if recent_avg > older_avg * 1.2:
                factors.append("Increased view count trend")
            elif recent_avg < older_avg * 0.8:
                factors.append("Declining view count trend")
        
        # Analyze engagement patterns
        recent_engagement = [r.engagement for r in historical_data[-7:] if r.engagement]
        if recent_engagement:
            avg_engagement = sum(recent_engagement) / len(recent_engagement)
            if avg_engagement > 1000:
                factors.append("High audience engagement")
            elif avg_engagement < 100:
                factors.append("Low audience engagement")
        
        # Platform distribution
        platform_counts = {}
        for record in historical_data:
            platform_counts[record.platform] = platform_counts.get(record.platform, 0) + 1
        
        if len(platform_counts) == 1:
            factors.append("Single platform dependency")
        elif len(platform_counts) > 3:
            factors.append("Well-diversified platform presence")
        
        # Seasonal factors (simplified)
        current_month = datetime.now().month
        if current_month in [11, 12]:  # Holiday season
            factors.append("Holiday season boost potential")
        elif current_month in [1, 2]:  # Post-holiday
            factors.append("Post-holiday revenue dip possible")
        
        return factors if factors else ["General market trends"]
    
    def _create_implementation_timeline(self, strategies: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Create implementation timeline for strategies"""        timeline = {
            "week_1": [],
            "week_2_4": [],
            "month_2_3": [],
            "ongoing": []
        }
        
        for strategy in strategies:
            priority = strategy.get("priority", "medium")
            strategy_type = strategy.get("type", "")
            
            if priority == "high":
                timeline["week_1"].append(strategy["title"])
            elif strategy_type in ["engagement_boost", "platform_optimization"]:
                timeline["week_2_4"].append(strategy["title"])
            else:
                timeline["month_2_3"].append(strategy["title"])
        
        timeline["ongoing"] = ["Monitor metrics and adjust strategies", "Analyze competitor performance"]
        
        return timeline
