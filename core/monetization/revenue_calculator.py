"""Advanced Revenue Calculation Engine
Multi-platform revenue tracking and analysis with AI-powered predictions

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from ...database.models import User, Content, RevenueRecord, Platform
from ...ml.prediction.revenue_predictor import RevenuePredictionModel
from ..analytics.metrics_calculator import MetricsCalculator


class RevenueSource(Enum):
    """Revenue sources"""
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING = "licensing"
    ADVERTISING = "advertising"
    SPONSORSHIP = "sponsorship"
    MERCHANDISE = "merchandise"
    LIVE_EVENTS = "live_events"
    SUBSCRIPTION = "subscription"
    TIPS = "tips"
    COLLABORATION = "collaboration"


class PlatformType(Enum):
    """Supported platforms"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"


class RevenuePeriod(Enum):
    """Revenue calculation periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class PlatformRevenue:
    """Platform-specific revenue data"""
    platform: PlatformType
    gross_revenue: Decimal
    platform_fee: Decimal
    net_revenue: Decimal
    plays_count: int
    engagement_rate: Decimal
    cpm: Decimal  # Cost per mille
    currency: str = "EUR"
    
    def __post_init__(self):
        """Calculate derived metrics"""
        if self.plays_count > 0:
            self.revenue_per_play = self.net_revenue / self.plays_count
        else:
            self.revenue_per_play = Decimal("0")


@dataclass
class RevenueMetrics:
    """Comprehensive revenue metrics"""
    user_id: int
    period_start: datetime
    period_end: datetime
    total_gross_revenue: Decimal = Decimal("0")
    total_net_revenue: Decimal = Decimal("0")
    total_platform_fees: Decimal = Decimal("0")
    total_plays: int = 0
    average_cpm: Decimal = Decimal("0")
    platform_revenues: Dict[PlatformType, PlatformRevenue] = field(default_factory=dict)
    source_breakdown: Dict[RevenueSource, Decimal] = field(default_factory=dict)
    growth_rate: Optional[Decimal] = None
    predicted_next_period: Optional[Decimal] = None
    
    def calculate_totals(self):
        """Calculate total metrics from platform data"""
        self.total_gross_revenue = sum(
            pr.gross_revenue for pr in self.platform_revenues.values()
        )
        self.total_net_revenue = sum(
            pr.net_revenue for pr in self.platform_revenues.values()
        )
        self.total_platform_fees = sum(
            pr.platform_fee for pr in self.platform_revenues.values()
        )
        self.total_plays = sum(
            pr.plays_count for pr in self.platform_revenues.values()
        )
        
        if self.total_plays > 0:
            self.average_cpm = (self.total_gross_revenue * 1000) / self.total_plays


class RevenueCalculationRules:
    """Platform-specific revenue calculation rules"""
    
    PLATFORM_RULES = {
        PlatformType.SPOTIFY: {
            "payout_per_stream": Decimal("0.003"),
            "platform_fee_rate": Decimal("0.30"),
            "minimum_payout": Decimal("10.00"),
            "currency": "EUR"
        },
        PlatformType.YOUTUBE: {
            "cpm_range": (Decimal("1.00"), Decimal("5.00")),
            "platform_fee_rate": Decimal("0.45"),
            "minimum_payout": Decimal("100.00"),
            "currency": "USD"
        },
        PlatformType.INSTAGRAM: {
            "cpm_range": (Decimal("2.00"), Decimal("8.00")),
            "platform_fee_rate": Decimal("0.30"),
            "minimum_payout": Decimal("25.00"),
            "currency": "USD"
        },
        PlatformType.TIKTOK: {
            "creator_fund_rate": Decimal("0.02"),
            "platform_fee_rate": Decimal("0.50"),
            "minimum_payout": Decimal("10.00"),
            "currency": "USD"
        }
    }


class RevenueCalculator:
    """Advanced revenue calculation engine with ML predictions"""
    
    def __init__(self, metrics_calculator: MetricsCalculator):
        self.metrics_calculator = metrics_calculator
        self.logger = logging.getLogger(__name__)
        self.prediction_model = RevenuePredictionModel()
        self.rules = RevenueCalculationRules()
        
    async def calculate_user_revenue(
        self,
        user_id: int,
        period_start: datetime,
        period_end: datetime,
        session: AsyncSession
    ) -> RevenueMetrics:
        """Calculate comprehensive revenue metrics for user"""
        try:
            metrics = RevenueMetrics(
                user_id=user_id,
                period_start=period_start,
                period_end=period_end
            )
            
            # Get user's content and platform data
            user_content = await self._get_user_content(user_id, session)
            
            # Calculate revenue for each platform
            for content in user_content:
                platform_revenues = await self._calculate_platform_revenues(
                    content, period_start, period_end, session
                )
                
                for platform, revenue in platform_revenues.items():
                    if platform in metrics.platform_revenues:
                        existing = metrics.platform_revenues[platform]
                        metrics.platform_revenues[platform] = self._merge_platform_revenue(
                            existing, revenue
                        )
                    else:
                        metrics.platform_revenues[platform] = revenue
            
            # Calculate revenue by source
            metrics.source_breakdown = await self._calculate_revenue_by_source(
                user_id, period_start, period_end, session
            )
            
            # Calculate totals and derived metrics
            metrics.calculate_totals()
            
            # Calculate growth rate
            metrics.growth_rate = await self._calculate_growth_rate(
                user_id, period_start, period_end, session
            )
            
            # Generate ML prediction for next period
            metrics.predicted_next_period = await self._predict_next_period_revenue(
                user_id, metrics, session
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Revenue calculation failed for user {user_id}: {str(e)}")
            raise
    
    async def _get_user_content(
        self, 
        user_id: int, 
        session: AsyncSession
    ) -> List[Content]:
        """Get user's content for revenue calculation"""
        result = await session.execute(
            select(Content).where(Content.user_id == user_id)
        )
        return result.scalars().all()
    
    async def _calculate_platform_revenues(
        self,
        content: Content,
        period_start: datetime,
        period_end: datetime,
        session: AsyncSession
    ) -> Dict[PlatformType, PlatformRevenue]:
        """Calculate revenue for content across platforms"""
        platform_revenues = {}
        
        # Get platform performance data
        platforms_data = await self._get_platform_performance(
            content.id, period_start, period_end, session
        )
        
        for platform_data in platforms_data:
            platform = PlatformType(platform_data.platform_name)
            
            # Calculate revenue based on platform rules
            revenue = await self._calculate_single_platform_revenue(
                platform, platform_data
            )
            
            platform_revenues[platform] = revenue
        
        return platform_revenues
    
    async def _calculate_single_platform_revenue(
        self,
        platform: PlatformType,
        platform_data: Any
    ) -> PlatformRevenue:
        """Calculate revenue for single platform"""
        rules = self.rules.PLATFORM_RULES.get(platform, {})
        
        if platform == PlatformType.SPOTIFY:
            return self._calculate_spotify_revenue(platform_data, rules)
        elif platform == PlatformType.YOUTUBE:
            return self._calculate_youtube_revenue(platform_data, rules)
        elif platform == PlatformType.INSTAGRAM:
            return self._calculate_instagram_revenue(platform_data, rules)
        elif platform == PlatformType.TIKTOK:
            return self._calculate_tiktok_revenue(platform_data, rules)
        else:
            return self._calculate_generic_revenue(platform, platform_data)
    
    def _calculate_spotify_revenue(
        self, 
        platform_data: Any, 
        rules: Dict[str, Any]
    ) -> PlatformRevenue:
        """Calculate Spotify revenue based on streams"""
        payout_per_stream = rules.get("payout_per_stream", Decimal("0.003"))
        platform_fee_rate = rules.get("platform_fee_rate", Decimal("0.30"))
        
        gross_revenue = Decimal(str(platform_data.plays_count)) * payout_per_stream
        platform_fee = gross_revenue * platform_fee_rate
        net_revenue = gross_revenue - platform_fee
        
        # Calculate engagement-based CPM
        engagement_rate = Decimal(str(platform_data.engagement_rate or 0))
        cpm = (gross_revenue * 1000) / max(platform_data.plays_count, 1)
        
        return PlatformRevenue(
            platform=PlatformType.SPOTIFY,
            gross_revenue=gross_revenue,
            platform_fee=platform_fee,
            net_revenue=net_revenue,
            plays_count=platform_data.plays_count,
            engagement_rate=engagement_rate,
            cpm=cpm,
            currency=rules.get("currency", "EUR")
        )
    
    def _calculate_youtube_revenue(
        self, 
        platform_data: Any, 
        rules: Dict[str, Any]
    ) -> PlatformRevenue:
        """Calculate YouTube revenue based on views and CPM"""
        cpm_range = rules.get("cpm_range", (Decimal("1.00"), Decimal("5.00")))
        platform_fee_rate = rules.get("platform_fee_rate", Decimal("0.45"))
        
        # Estimate CPM based on engagement and content quality
        engagement_rate = Decimal(str(platform_data.engagement_rate or 0.02))
        estimated_cpm = self._estimate_cpm(engagement_rate, cpm_range)
        
        gross_revenue = (Decimal(str(platform_data.plays_count)) * estimated_cpm) / 1000
        platform_fee = gross_revenue * platform_fee_rate
        net_revenue = gross_revenue - platform_fee
        
        return PlatformRevenue(
            platform=PlatformType.YOUTUBE,
            gross_revenue=gross_revenue,
            platform_fee=platform_fee,
            net_revenue=net_revenue,
            plays_count=platform_data.plays_count,
            engagement_rate=engagement_rate,
            cpm=estimated_cpm,
            currency=rules.get("currency", "USD")
        )
    
    def _calculate_instagram_revenue(
        self, 
        platform_data: Any, 
        rules: Dict[str, Any]
    ) -> PlatformRevenue:
        """Calculate Instagram revenue from creator fund and brand deals"""
        cpm_range = rules.get("cpm_range", (Decimal("2.00"), Decimal("8.00")))
        platform_fee_rate = rules.get("platform_fee_rate", Decimal("0.30"))
        
        engagement_rate = Decimal(str(platform_data.engagement_rate or 0.03))
        estimated_cpm = self._estimate_cpm(engagement_rate, cpm_range)
        
        # Instagram revenue includes Reels Play Bonus and brand partnerships
        gross_revenue = (Decimal(str(platform_data.plays_count)) * estimated_cpm) / 1000
        
        # Add estimated brand deal revenue based on engagement
        if engagement_rate > Decimal("0.05"):
            brand_deal_bonus = gross_revenue * Decimal("0.2")
            gross_revenue += brand_deal_bonus
        
        platform_fee = gross_revenue * platform_fee_rate
        net_revenue = gross_revenue - platform_fee
        
        return PlatformRevenue(
            platform=PlatformType.INSTAGRAM,
            gross_revenue=gross_revenue,
            platform_fee=platform_fee,
            net_revenue=net_revenue,
            plays_count=platform_data.plays_count,
            engagement_rate=engagement_rate,
            cpm=estimated_cpm,
            currency=rules.get("currency", "USD")
        )
    
    def _calculate_tiktok_revenue(
        self, 
        platform_data: Any, 
        rules: Dict[str, Any]
    ) -> PlatformRevenue:
        """Calculate TikTok Creator Fund revenue"""
        creator_fund_rate = rules.get("creator_fund_rate", Decimal("0.02"))
        platform_fee_rate = rules.get("platform_fee_rate", Decimal("0.50"))
        
        # TikTok pays based on views and engagement
        engagement_rate = Decimal(str(platform_data.engagement_rate or 0.05))
        base_rate = creator_fund_rate * (1 + engagement_rate)
        
        gross_revenue = Decimal(str(platform_data.plays_count)) * base_rate
        platform_fee = gross_revenue * platform_fee_rate
        net_revenue = gross_revenue - platform_fee
        
        cpm = (gross_revenue * 1000) / max(platform_data.plays_count, 1)
        
        return PlatformRevenue(
            platform=PlatformType.TIKTOK,
            gross_revenue=gross_revenue,
            platform_fee=platform_fee,
            net_revenue=net_revenue,
            plays_count=platform_data.plays_count,
            engagement_rate=engagement_rate,
            cpm=cpm,
            currency=rules.get("currency", "USD")
        )
    
    def _calculate_generic_revenue(
        self, 
        platform: PlatformType, 
        platform_data: Any
    ) -> PlatformRevenue:
        """Calculate revenue for platforms without specific rules"""
        # Generic calculation based on industry averages
        estimated_cpm = Decimal("2.50")
        platform_fee_rate = Decimal("0.30")
        
        gross_revenue = (Decimal(str(platform_data.plays_count)) * estimated_cpm) / 1000
        platform_fee = gross_revenue * platform_fee_rate
        net_revenue = gross_revenue - platform_fee
        
        engagement_rate = Decimal(str(platform_data.engagement_rate or 0.03))
        
        return PlatformRevenue(
            platform=platform,
            gross_revenue=gross_revenue,
            platform_fee=platform_fee,
            net_revenue=net_revenue,
            plays_count=platform_data.plays_count,
            engagement_rate=engagement_rate,
            cpm=estimated_cpm
        )
    
    def _estimate_cpm(
        self, 
        engagement_rate: Decimal, 
        cpm_range: Tuple[Decimal, Decimal]
    ) -> Decimal:
        """Estimate CPM based on engagement rate"""
        min_cpm, max_cpm = cpm_range
        
        # Higher engagement = higher CPM
        if engagement_rate >= Decimal("0.10"):
            return max_cpm
        elif engagement_rate >= Decimal("0.05"):
            return min_cpm + (max_cpm - min_cpm) * Decimal("0.7")
        elif engagement_rate >= Decimal("0.02"):
            return min_cpm + (max_cpm - min_cpm) * Decimal("0.4")
        else:
            return min_cpm
    
    def _merge_platform_revenue(
        self, 
        existing: PlatformRevenue, 
        new: PlatformRevenue
    ) -> PlatformRevenue:
        """Merge platform revenue data"""
        return PlatformRevenue(
            platform=existing.platform,
            gross_revenue=existing.gross_revenue + new.gross_revenue,
            platform_fee=existing.platform_fee + new.platform_fee,
            net_revenue=existing.net_revenue + new.net_revenue,
            plays_count=existing.plays_count + new.plays_count,
            engagement_rate=(existing.engagement_rate + new.engagement_rate) / 2,
            cpm=(existing.cpm + new.cpm) / 2,
            currency=existing.currency
        )
    
    async def _calculate_revenue_by_source(
        self,
        user_id: int,
        period_start: datetime,
        period_end: datetime,
        session: AsyncSession
    ) -> Dict[RevenueSource, Decimal]:
        """Calculate revenue breakdown by source"""
        # Get revenue records by source
        result = await session.execute(
            select(
                RevenueRecord.source,
                func.sum(RevenueRecord.amount).label('total')
            ).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.date >= period_start,
                RevenueRecord.date <= period_end
            ).group_by(RevenueRecord.source)
        )
        
        source_breakdown = {}
        for row in result:
            source = RevenueSource(row.source)
            source_breakdown[source] = Decimal(str(row.total))
        
        return source_breakdown
    
    async def _calculate_growth_rate(
        self,
        user_id: int,
        period_start: datetime,
        period_end: datetime,
        session: AsyncSession
    ) -> Optional[Decimal]:
        """Calculate revenue growth rate compared to previous period"""
        try:
            period_length = period_end - period_start
            previous_period_start = period_start - period_length
            previous_period_end = period_start
            
            # Get current period revenue
            current_revenue = await self._get_period_revenue(
                user_id, period_start, period_end, session
            )
            
            # Get previous period revenue
            previous_revenue = await self._get_period_revenue(
                user_id, previous_period_start, previous_period_end, session
            )
            
            if previous_revenue > 0:
                growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
                return Decimal(str(growth_rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Growth rate calculation failed: {str(e)}")
            return None
    
    async def _get_period_revenue(
        self,
        user_id: int,
        period_start: datetime,
        period_end: datetime,
        session: AsyncSession
    ) -> Decimal:
        """Get total revenue for a specific period"""
        result = await session.execute(
            select(func.sum(RevenueRecord.amount)).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.date >= period_start,
                RevenueRecord.date <= period_end
            )
        )
        
        total = result.scalar()
        return Decimal(str(total)) if total else Decimal("0")
    
    async def _predict_next_period_revenue(
        self,
        user_id: int,
        current_metrics: RevenueMetrics,
        session: AsyncSession
    ) -> Optional[Decimal]:
        """Predict next period revenue using ML model"""
        try:
            # Get historical data for prediction
            historical_data = await self._get_historical_revenue_data(user_id, session)
            
            if len(historical_data) < 3:
                return None
            
            # Use ML model to predict
            prediction = await self.prediction_model.predict_revenue(
                user_id=user_id,
                historical_data=historical_data,
                current_metrics=current_metrics
            )
            
            return Decimal(str(prediction)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            self.logger.error(f"Revenue prediction failed: {str(e)}")
            return None
    
    async def _get_historical_revenue_data(
        self, 
        user_id: int, 
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get historical revenue data for ML prediction"""
        # Get last 12 months of revenue data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        result = await session.execute(
            select(
                func.date_trunc('month', RevenueRecord.date).label('month'),
                func.sum(RevenueRecord.amount).label('total_revenue'),
                func.count(RevenueRecord.id).label('transaction_count'),
                func.avg(RevenueRecord.amount).label('avg_transaction')
            ).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.date >= start_date,
                RevenueRecord.date <= end_date
            ).group_by(
                func.date_trunc('month', RevenueRecord.date)
            ).order_by(
                func.date_trunc('month', RevenueRecord.date)
            )
        )
        
        historical_data = []
        for row in result:
            historical_data.append({
                'month': row.month,
                'total_revenue': float(row.total_revenue),
                'transaction_count': row.transaction_count,
                'avg_transaction': float(row.avg_transaction)
            })
        
        return historical_data
    
    async def _get_platform_performance(
        self,
        content_id: str,
        period_start: datetime,
        period_end: datetime,
        session: AsyncSession
    ) -> List[Any]:
        """Get platform performance data for content"""
        # This would typically query platform-specific analytics tables
        # For now, return mock data structure
        return []


class RevenueReportGenerator:
    """Generate comprehensive revenue reports"""
    
    def __init__(self, revenue_calculator: RevenueCalculator):
        self.revenue_calculator = revenue_calculator
        self.logger = logging.getLogger(__name__)
    
    async def generate_monthly_report(
        self,
        user_id: int,
        year: int,
        month: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Generate detailed monthly revenue report"""
        period_start = datetime(year, month, 1)
        if month == 12:
            period_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            period_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        metrics = await self.revenue_calculator.calculate_user_revenue(
            user_id, period_start, period_end, session
        )
        
        return {
            "user_id": user_id,
            "period": f"{year}-{month:02d}",
            "summary": {
                "total_gross_revenue": float(metrics.total_gross_revenue),
                "total_net_revenue": float(metrics.total_net_revenue),
                "total_platform_fees": float(metrics.total_platform_fees),
                "total_plays": metrics.total_plays,
                "average_cpm": float(metrics.average_cpm),
                "growth_rate": float(metrics.growth_rate) if metrics.growth_rate else None,
                "predicted_next_month": float(metrics.predicted_next_period) if metrics.predicted_next_period else None
            },
            "platform_breakdown": {
                platform.value: {
                    "gross_revenue": float(revenue.gross_revenue),
                    "net_revenue": float(revenue.net_revenue),
                    "platform_fee": float(revenue.platform_fee),
                    "plays_count": revenue.plays_count,
                    "engagement_rate": float(revenue.engagement_rate),
                    "cpm": float(revenue.cpm)
                }
                for platform, revenue in metrics.platform_revenues.items()
            },
            "source_breakdown": {
                source.value: float(amount)
                for source, amount in metrics.source_breakdown.items()
            }
        }
