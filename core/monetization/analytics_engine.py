"""Monetization Analytics Engine
Advanced revenue analytics, predictions, and business intelligence

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from dataclasses import dataclass, field

from ...database.models import User, RevenueRecord, Content, Platform
from ...ml.analytics.revenue_predictor import RevenuePredictionEngine
from ...ml.analytics.trend_analyzer import TrendAnalyzer
from ...core.cache import CacheManager


class AnalyticsTimeframe(Enum):
    """Analytics timeframe options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RevenueMetricType(Enum):
    """Types of revenue metrics"""
    TOTAL_REVENUE = "total_revenue"
    NET_REVENUE = "net_revenue"
    PLATFORM_FEES = "platform_fees"
    AVERAGE_RPM = "average_rpm"  # Revenue per mille
    CONVERSION_RATE = "conversion_rate"
    GROWTH_RATE = "growth_rate"
    PLATFORM_DISTRIBUTION = "platform_distribution"
    SOURCE_BREAKDOWN = "source_breakdown"


class TrendDirection(Enum):
    """Trend direction indicators"""
    UPWARD = "upward"
    DOWNWARD = "downward"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class AnalyticsQuery:
    """Analytics query parameters"""
    user_id: int
    timeframe: AnalyticsTimeframe
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    platforms: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    metrics: List[RevenueMetricType] = field(default_factory=lambda: [RevenueMetricType.TOTAL_REVENUE])
    include_predictions: bool = True
    granularity: str = "daily"
    
    def validate(self) -> bool:
        """Validate query parameters"""
        if self.timeframe == AnalyticsTimeframe.CUSTOM:
            return self.start_date is not None and self.end_date is not None
        return True


@dataclass
class RevenueDataPoint:
    """Single revenue data point"""
    date: datetime
    value: Decimal
    platform: Optional[str] = None
    source: Optional[str] = None
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    direction: TrendDirection
    strength: float  # 0-1 scale
    slope: float
    correlation: float
    confidence: float
    start_value: Decimal
    end_value: Decimal
    peak_value: Decimal
    valley_value: Decimal
    volatility: float


@dataclass
class RevenueInsight:
    """Revenue insight and recommendation"""
    insight_type: str
    title: str
    description: str
    impact_score: float  # 0-1 scale
    confidence: float
    recommended_actions: List[str]
    data_support: Dict[str, Any]
    priority: str  # high, medium, low


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    user_id: int
    query: AnalyticsQuery
    generated_at: datetime
    summary_metrics: Dict[str, Any]
    time_series_data: List[RevenueDataPoint]
    trend_analysis: TrendAnalysis
    platform_breakdown: Dict[str, Decimal]
    source_breakdown: Dict[str, Decimal]
    insights: List[RevenueInsight]
    predictions: Optional[Dict[str, Any]] = None
    benchmarks: Optional[Dict[str, Any]] = None


class MonetizationAnalytics:
    """Advanced monetization analytics engine"""
    
    def __init__(
        self,
        prediction_engine: RevenuePredictionEngine,
        trend_analyzer: TrendAnalyzer,
        cache_manager: CacheManager
    ):
        self.prediction_engine = prediction_engine
        self.trend_analyzer = trend_analyzer
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)
        
    async def generate_revenue_report(
        self,
        query: AnalyticsQuery,
        session: AsyncSession
    ) -> AnalyticsReport:
        """Generate comprehensive revenue analytics report"""
        try:
            # Validate query
            if not query.validate():
                raise ValueError("Invalid analytics query parameters")
            
            # Check cache first
            cache_key = self._generate_cache_key(query)
            cached_report = await self.cache_manager.get(cache_key)
            if cached_report:
                return cached_report
            
            # Determine date range
            start_date, end_date = self._calculate_date_range(query)
            
            # Fetch raw revenue data
            revenue_data = await self._fetch_revenue_data(
                query.user_id, start_date, end_date, session, query
            )
            
            # Calculate summary metrics
            summary_metrics = await self._calculate_summary_metrics(
                revenue_data, query
            )
            
            # Generate time series data
            time_series = await self._generate_time_series(
                revenue_data, query.granularity
            )
            
            # Perform trend analysis
            trend_analysis = await self._analyze_trends(time_series)
            
            # Calculate platform and source breakdowns
            platform_breakdown = await self._calculate_platform_breakdown(revenue_data)
            source_breakdown = await self._calculate_source_breakdown(revenue_data)
            
            # Generate insights
            insights = await self._generate_insights(
                summary_metrics, trend_analysis, platform_breakdown, source_breakdown, query
            )
            
            # Generate predictions if requested
            predictions = None
            if query.include_predictions:
                predictions = await self._generate_predictions(
                    query.user_id, time_series, session
                )
            
            # Get industry benchmarks
            benchmarks = await self._get_industry_benchmarks(query.user_id, session)
            
            # Create report
            report = AnalyticsReport(
                user_id=query.user_id,
                query=query,
                generated_at=datetime.now(),
                summary_metrics=summary_metrics,
                time_series_data=time_series,
                trend_analysis=trend_analysis,
                platform_breakdown=platform_breakdown,
                source_breakdown=source_breakdown,
                insights=insights,
                predictions=predictions,
                benchmarks=benchmarks
            )
            
            # Cache report
            await self.cache_manager.set(
                cache_key, report, ttl=3600  # 1 hour cache
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate revenue report: {str(e)}")
            raise
    
    async def calculate_roi_metrics(
        self,
        user_id: int,
        investment_amount: Decimal,
        timeframe: AnalyticsTimeframe,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Calculate ROI metrics for monetization efforts"""
        try:
            start_date, end_date = self._calculate_date_range(
                AnalyticsQuery(user_id=user_id, timeframe=timeframe)
            )
            
            # Get revenue for period
            total_revenue = await self._get_total_revenue(
                user_id, start_date, end_date, session
            )
            
            # Calculate basic ROI
            roi_percentage = ((total_revenue - investment_amount) / investment_amount) * 100
            
            # Calculate payback period
            payback_period = await self._calculate_payback_period(
                user_id, investment_amount, session
            )
            
            # Calculate lifetime value projection
            ltv_projection = await self._calculate_ltv_projection(
                user_id, session
            )
            
            return {
                "investment_amount": float(investment_amount),
                "total_revenue": float(total_revenue),
                "net_profit": float(total_revenue - investment_amount),
                "roi_percentage": float(roi_percentage),
                "payback_period_months": payback_period,
                "lifetime_value_projection": float(ltv_projection),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate ROI metrics: {str(e)}")
            return {}
    
    async def get_revenue_optimization_suggestions(
        self,
        user_id: int,
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get AI-powered revenue optimization suggestions"""
        try:
            # Analyze recent performance
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # Last 3 months
            
            query = AnalyticsQuery(
                user_id=user_id,
                timeframe=AnalyticsTimeframe.CUSTOM,
                start_date=start_date,
                end_date=end_date
            )
            
            report = await self.generate_revenue_report(query, session)
            
            suggestions = []
            
            # Platform optimization suggestions
            if report.platform_breakdown:
                top_platform = max(report.platform_breakdown, key=report.platform_breakdown.get)
                underperforming_platforms = [
                    platform for platform, revenue in report.platform_breakdown.items()
                    if revenue < report.platform_breakdown[top_platform] * Decimal("0.3")
                ]
                
                if underperforming_platforms:
                    suggestions.append({
                        "type": "platform_optimization",
                        "title": "Optimize Underperforming Platforms",
                        "description": f"Focus on improving performance on {', '.join(underperforming_platforms)}",
                        "potential_impact": "medium",
                        "actions": [
                            "Increase content frequency on underperforming platforms",
                            "Analyze successful content patterns from top platform",
                            "Adjust posting schedule based on audience activity"
                        ]
                    })
            
            # Content strategy suggestions
            if report.trend_analysis.direction == TrendDirection.DOWNWARD:
                suggestions.append({
                    "type": "content_strategy",
                    "title": "Reverse Declining Revenue Trend",
                    "description": "Revenue has been declining - consider content strategy changes",
                    "potential_impact": "high",
                    "actions": [
                        "Analyze top-performing content characteristics",
                        "Experiment with new content formats",
                        "Increase engagement with audience",
                        "Consider collaborations to reach new audiences"
                    ]
                })
            
            # Monetization diversification
            revenue_sources = len(report.source_breakdown)
            if revenue_sources < 3:
                suggestions.append({
                    "type": "monetization_diversification",
                    "title": "Diversify Revenue Sources",
                    "description": f"Currently using {revenue_sources} revenue sources - consider adding more",
                    "potential_impact": "high",
                    "actions": [
                        "Explore licensing opportunities",
                        "Consider brand partnerships",
                        "Add merchandise sales",
                        "Offer premium content subscriptions"
                    ]
                })
            
            # Growth opportunity suggestions
            if report.predictions and report.predictions.get("growth_potential", 0) > 0.5:
                suggestions.append({
                    "type": "growth_opportunity",
                    "title": "High Growth Potential Detected",
                    "description": "AI analysis shows strong growth potential",
                    "potential_impact": "high",
                    "actions": [
                        "Increase content production",
                        "Invest in promoted content",
                        "Expand to new platforms",
                        "Consider professional management"
                    ]
                })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization suggestions: {str(e)}")
            return []
    
    async def compare_period_performance(
        self,
        user_id: int,
        current_start: datetime,
        current_end: datetime,
        comparison_start: datetime,
        comparison_end: datetime,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Compare performance between two time periods"""
        try:
            # Get current period data
            current_revenue = await self._get_total_revenue(
                user_id, current_start, current_end, session
            )
            current_platforms = await self._get_platform_revenue(
                user_id, current_start, current_end, session
            )
            
            # Get comparison period data
            comparison_revenue = await self._get_total_revenue(
                user_id, comparison_start, comparison_end, session
            )
            comparison_platforms = await self._get_platform_revenue(
                user_id, comparison_start, comparison_end, session
            )
            
            # Calculate changes
            revenue_change = current_revenue - comparison_revenue
            revenue_change_percent = (
                (revenue_change / comparison_revenue) * 100
                if comparison_revenue > 0 else 0
            )
            
            # Platform comparisons
            platform_changes = {}
            all_platforms = set(current_platforms.keys()) | set(comparison_platforms.keys())
            
            for platform in all_platforms:
                current_value = current_platforms.get(platform, Decimal("0"))
                comparison_value = comparison_platforms.get(platform, Decimal("0"))
                
                change = current_value - comparison_value
                change_percent = (
                    (change / comparison_value) * 100
                    if comparison_value > 0 else 100 if current_value > 0 else 0
                )
                
                platform_changes[platform] = {
                    "current": float(current_value),
                    "comparison": float(comparison_value),
                    "change": float(change),
                    "change_percent": float(change_percent)
                }
            
            return {
                "current_period": {
                    "start": current_start.isoformat(),
                    "end": current_end.isoformat(),
                    "revenue": float(current_revenue)
                },
                "comparison_period": {
                    "start": comparison_start.isoformat(),
                    "end": comparison_end.isoformat(),
                    "revenue": float(comparison_revenue)
                },
                "changes": {
                    "revenue_change": float(revenue_change),
                    "revenue_change_percent": float(revenue_change_percent),
                    "trend": "positive" if revenue_change > 0 else "negative" if revenue_change < 0 else "stable"
                },
                "platform_changes": platform_changes
            }
            
        except Exception as e:
            self.logger.error(f"Failed to compare period performance: {str(e)}")
            return {}
    
    async def _fetch_revenue_data(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession,
        query: AnalyticsQuery
    ) -> List[RevenueDataPoint]:
        """Fetch raw revenue data for analysis"""
        # Build query conditions
        conditions = [
            RevenueRecord.user_id == user_id,
            RevenueRecord.date >= start_date,
            RevenueRecord.date <= end_date,
            RevenueRecord.status == "confirmed"
        ]
        
        # Add platform filter
        if query.platforms:
            conditions.append(RevenueRecord.platform.in_(query.platforms))
        
        # Execute query
        result = await session.execute(
            select(RevenueRecord).where(and_(*conditions)).order_by(RevenueRecord.date)
        )
        
        records = result.scalars().all()
        
        # Convert to data points
        data_points = []
        for record in records:
            data_points.append(RevenueDataPoint(
                date=record.date,
                value=record.amount,
                platform=record.platform,
                source=record.source,
                content_id=record.content_id,
                metadata={
                    "currency": record.currency,
                    "transaction_id": record.transaction_id
                }
            ))
        
        return data_points
    
    async def _calculate_summary_metrics(
        self,
        revenue_data: List[RevenueDataPoint],
        query: AnalyticsQuery
    ) -> Dict[str, Any]:
        """Calculate summary metrics from revenue data"""
        if not revenue_data:
            return {}
        
        total_revenue = sum(dp.value for dp in revenue_data)
        unique_platforms = len(set(dp.platform for dp in revenue_data if dp.platform))
        unique_sources = len(set(dp.source for dp in revenue_data if dp.source))
        
        # Calculate date range
        dates = [dp.date for dp in revenue_data]
        period_days = (max(dates) - min(dates)).days + 1
        
        return {
            "total_revenue": float(total_revenue),
            "average_daily_revenue": float(total_revenue / period_days) if period_days > 0 else 0,
            "transaction_count": len(revenue_data),
            "average_transaction_value": float(total_revenue / len(revenue_data)),
            "unique_platforms": unique_platforms,
            "unique_revenue_sources": unique_sources,
            "period_days": period_days,
            "first_transaction": min(dates).isoformat(),
            "last_transaction": max(dates).isoformat()
        }
    
    async def _generate_time_series(
        self,
        revenue_data: List[RevenueDataPoint],
        granularity: str
    ) -> List[RevenueDataPoint]:
        """Generate time series data with specified granularity"""
        if not revenue_data:
            return []
        
        # Group data by granularity
        df = pd.DataFrame([
            {
                "date": dp.date,
                "value": float(dp.value),
                "platform": dp.platform,
                "source": dp.source
            }
            for dp in revenue_data
        ])
        
        if granularity == "daily":
            grouped = df.groupby(df['date'].dt.date)
        elif granularity == "weekly":
            grouped = df.groupby(df['date'].dt.to_period('W'))
        elif granularity == "monthly":
            grouped = df.groupby(df['date'].dt.to_period('M'))
        else:
            grouped = df.groupby(df['date'].dt.date)  # Default to daily
        
        time_series = []
        for period, group in grouped:
            time_series.append(RevenueDataPoint(
                date=period if isinstance(period, datetime) else datetime.combine(period, datetime.min.time()),
                value=Decimal(str(group['value'].sum())),
                metadata={
                    "transaction_count": len(group),
                    "platforms": list(group['platform'].unique()),
                    "sources": list(group['source'].unique())
                }
            ))
        
        return sorted(time_series, key=lambda x: x.date)
    
    async def _analyze_trends(
        self,
        time_series: List[RevenueDataPoint]
    ) -> TrendAnalysis:
        """Analyze trends in time series data"""
        if len(time_series) < 2:
            return TrendAnalysis(
                direction=TrendDirection.STABLE,
                strength=0.0,
                slope=0.0,
                correlation=0.0,
                confidence=0.0,
                start_value=Decimal("0"),
                end_value=Decimal("0"),
                peak_value=Decimal("0"),
                valley_value=Decimal("0"),
                volatility=0.0
            )
        
        values = [float(dp.value) for dp in time_series]
        
        # Calculate trend using numpy
        x = np.arange(len(values))
        coefficients = np.polyfit(x, values, 1)
        slope = coefficients[0]
        
        # Calculate correlation
        correlation = np.corrcoef(x, values)[0, 1]
        
        # Determine trend direction
        if slope > 0.1:
            direction = TrendDirection.UPWARD
        elif slope < -0.1:
            direction = TrendDirection.DOWNWARD
        else:
            direction = TrendDirection.STABLE
        
        # Calculate volatility (coefficient of variation)
        mean_value = np.mean(values)
        std_value = np.std(values)
        volatility = std_value / mean_value if mean_value > 0 else 0
        
        if volatility > 0.5:
            direction = TrendDirection.VOLATILE
        
        return TrendAnalysis(
            direction=direction,
            strength=abs(correlation),
            slope=slope,
            correlation=correlation,
            confidence=abs(correlation),
            start_value=time_series[0].value,
            end_value=time_series[-1].value,
            peak_value=max(dp.value for dp in time_series),
            valley_value=min(dp.value for dp in time_series),
            volatility=volatility
        )
    
    async def _calculate_platform_breakdown(
        self,
        revenue_data: List[RevenueDataPoint]
    ) -> Dict[str, Decimal]:
        """Calculate revenue breakdown by platform"""
        platform_revenue = {}
        
        for dp in revenue_data:
            if dp.platform:
                if dp.platform not in platform_revenue:
                    platform_revenue[dp.platform] = Decimal("0")
                platform_revenue[dp.platform] += dp.value
        
        return platform_revenue
    
    async def _calculate_source_breakdown(
        self,
        revenue_data: List[RevenueDataPoint]
    ) -> Dict[str, Decimal]:
        """Calculate revenue breakdown by source"""
        source_revenue = {}
        
        for dp in revenue_data:
            if dp.source:
                if dp.source not in source_revenue:
                    source_revenue[dp.source] = Decimal("0")
                source_revenue[dp.source] += dp.value
        
        return source_revenue
    
    async def _generate_insights(
        self,
        summary_metrics: Dict[str, Any],
        trend_analysis: TrendAnalysis,
        platform_breakdown: Dict[str, Decimal],
        source_breakdown: Dict[str, Decimal],
        query: AnalyticsQuery
    ) -> List[RevenueInsight]:
        """Generate actionable insights from analytics data"""
        insights = []
        
        # Trend insight
        if trend_analysis.direction == TrendDirection.UPWARD:
            insights.append(RevenueInsight(
                insight_type="trend",
                title="Positive Revenue Trend",
                description=f"Revenue is trending upward with {trend_analysis.strength:.1%} correlation",
                impact_score=trend_analysis.strength,
                confidence=trend_analysis.confidence,
                recommended_actions=[
                    "Continue current content strategy",
                    "Scale successful content types",
                    "Consider increasing investment"
                ],
                data_support={"slope": trend_analysis.slope, "correlation": trend_analysis.correlation},
                priority="high" if trend_analysis.strength > 0.7 else "medium"
            ))
        
        # Platform diversification insight
        if platform_breakdown:
            total_revenue = sum(platform_breakdown.values())
            platform_concentration = max(platform_breakdown.values()) / total_revenue
            
            if platform_concentration > Decimal("0.8"):
                insights.append(RevenueInsight(
                    insight_type="diversification",
                    title="High Platform Concentration Risk",
                    description=f"Over 80% of revenue comes from a single platform",
                    impact_score=float(platform_concentration),
                    confidence=0.9,
                    recommended_actions=[
                        "Diversify to additional platforms",
                        "Reduce dependency on single platform",
                        "Build direct audience channels"
                    ],
                    data_support={"concentration": float(platform_concentration)},
                    priority="high"
                ))
        
        # Performance insight
        avg_daily = summary_metrics.get("average_daily_revenue", 0)
        if avg_daily > 100:  # Threshold for good performance
            insights.append(RevenueInsight(
                insight_type="performance",
                title="Strong Daily Revenue Performance",
                description=f"Averaging €{avg_daily:.2f} per day",
                impact_score=min(avg_daily / 1000, 1.0),  # Scale to 0-1
                confidence=0.8,
                recommended_actions=[
                    "Maintain current momentum",
                    "Document successful strategies",
                    "Consider scaling operations"
                ],
                data_support={"daily_average": avg_daily},
                priority="medium"
            ))
        
        return insights
    
    async def _generate_predictions(
        self,
        user_id: int,
        time_series: List[RevenueDataPoint],
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Generate revenue predictions using ML"""
        try:
            # Prepare data for prediction model
            historical_data = [
                {"date": dp.date, "revenue": float(dp.value)}
                for dp in time_series
            ]
            
            # Generate predictions
            predictions = await self.prediction_engine.predict_revenue(
                user_id, historical_data
            )
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Failed to generate predictions: {str(e)}")
            return {}
    
    async def _get_industry_benchmarks(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get industry benchmarks for comparison"""
        # This would typically query benchmark data
        # For now, return mock benchmarks
        return {
            "average_monthly_revenue": 2500.0,
            "top_10_percent_threshold": 10000.0,
            "median_rpm": 5.0,
            "average_platform_count": 3.2
        }
    
    def _calculate_date_range(self, query: AnalyticsQuery) -> Tuple[datetime, datetime]:
        """Calculate date range based on timeframe"""
        end_date = datetime.now()
        
        if query.timeframe == AnalyticsTimeframe.CUSTOM:
            return query.start_date, query.end_date
        elif query.timeframe == AnalyticsTimeframe.DAILY:
            start_date = end_date - timedelta(days=1)
        elif query.timeframe == AnalyticsTimeframe.WEEKLY:
            start_date = end_date - timedelta(weeks=1)
        elif query.timeframe == AnalyticsTimeframe.MONTHLY:
            start_date = end_date - timedelta(days=30)
        elif query.timeframe == AnalyticsTimeframe.QUARTERLY:
            start_date = end_date - timedelta(days=90)
        elif query.timeframe == AnalyticsTimeframe.YEARLY:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to monthly
        
        return start_date, end_date
    
    def _generate_cache_key(self, query: AnalyticsQuery) -> str:
        """Generate cache key for analytics query"""
        import hashlib
        
        key_data = f"{query.user_id}_{query.timeframe.value}_{query.start_date}_{query.end_date}_{query.platforms}_{query.metrics}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _get_total_revenue(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Decimal:
        """Get total revenue for period"""
        result = await session.execute(
            select(func.sum(RevenueRecord.amount)).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.date >= start_date,
                RevenueRecord.date <= end_date,
                RevenueRecord.status == "confirmed"
            )
        )
        
        total = result.scalar()
        return Decimal(str(total)) if total else Decimal("0")
    
    async def _get_platform_revenue(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Dict[str, Decimal]:
        """Get revenue breakdown by platform"""
        result = await session.execute(
            select(
                RevenueRecord.platform,
                func.sum(RevenueRecord.amount).label('total')
            ).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.date >= start_date,
                RevenueRecord.date <= end_date,
                RevenueRecord.status == "confirmed"
            ).group_by(RevenueRecord.platform)
        )
        
        platform_revenue = {}
        for row in result:
            platform_revenue[row.platform] = Decimal(str(row.total))
        
        return platform_revenue
    
    async def _calculate_payback_period(
        self,
        user_id: int,
        investment: Decimal,
        session: AsyncSession
    ) -> Optional[float]:
        """Calculate payback period in months"""
        try:
            # Get monthly revenue trend
            monthly_revenues = []
            for i in range(12):  # Last 12 months
                end_date = datetime.now() - timedelta(days=i*30)
                start_date = end_date - timedelta(days=30)
                
                monthly_revenue = await self._get_total_revenue(
                    user_id, start_date, end_date, session
                )
                monthly_revenues.append(monthly_revenue)
            
            # Calculate average monthly revenue
            avg_monthly = sum(monthly_revenues) / len(monthly_revenues)
            
            if avg_monthly > 0:
                return float(investment / avg_monthly)
            
            return None
            
        except Exception:
            return None
    
    async def _calculate_ltv_projection(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Decimal:
        """Calculate lifetime value projection"""
        try:
            # Simple LTV calculation: average monthly revenue * 24 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # Last year
            
            total_revenue = await self._get_total_revenue(
                user_id, start_date, end_date, session
            )
            
            monthly_average = total_revenue / 12
            ltv_projection = monthly_average * 24  # 2 year projection
            
            return ltv_projection
            
        except Exception:
            return Decimal("0")


class RevenueAnalyzer:
    """High-level revenue analysis interface"""
    
    def __init__(self, analytics_engine: MonetizationAnalytics):
        self.analytics_engine = analytics_engine
        self.logger = logging.getLogger(__name__)
    
    async def get_dashboard_data(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Current month data
            current_query = AnalyticsQuery(
                user_id=user_id,
                timeframe=AnalyticsTimeframe.MONTHLY
            )
            current_report = await self.analytics_engine.generate_revenue_report(
                current_query, session
            )
            
            # Previous month for comparison
            end_date = datetime.now().replace(day=1) - timedelta(days=1)
            start_date = end_date.replace(day=1)
            
            previous_query = AnalyticsQuery(
                user_id=user_id,
                timeframe=AnalyticsTimeframe.CUSTOM,
                start_date=start_date,
                end_date=end_date
            )
            previous_report = await self.analytics_engine.generate_revenue_report(
                previous_query, session
            )
            
            # Calculate month-over-month change
            current_revenue = current_report.summary_metrics.get("total_revenue", 0)
            previous_revenue = previous_report.summary_metrics.get("total_revenue", 0)
            
            change_percent = 0
            if previous_revenue > 0:
                change_percent = ((current_revenue - previous_revenue) / previous_revenue) * 100
            
            return {
                "current_month": current_report.summary_metrics,
                "previous_month": previous_report.summary_metrics,
                "month_over_month_change": change_percent,
                "trend_analysis": current_report.trend_analysis.__dict__,
                "platform_breakdown": {k: float(v) for k, v in current_report.platform_breakdown.items()},
                "top_insights": [insight.__dict__ for insight in current_report.insights[:3]],
                "predictions": current_report.predictions
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {str(e)}")
            return {}
