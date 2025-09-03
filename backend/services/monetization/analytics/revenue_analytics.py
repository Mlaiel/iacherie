"""Revenue Analytics - Advanced Revenue Analysis and Insights
===========================================================

Comprehensive revenue analytics engine providing deep insights,
forecasting, and optimization recommendations for monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import uuid
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)


class RevenueSource(str, Enum):
    """Revenue source types."""
    SUBSCRIPTIONS = "subscriptions"
    ONE_TIME_PURCHASES = "one_time_purchases"
    LICENSING = "licensing"
    ROYALTIES = "royalties"
    ADVERTISING = "advertising"
    MARKETPLACE = "marketplace"
    CRYPTO_PAYMENTS = "crypto_payments"
    DONATIONS = "donations"


class MetricType(str, Enum):
    """Analytics metric types."""
    REVENUE = "revenue"
    USERS = "users"
    CONVERSIONS = "conversions"
    RETENTION = "retention"
    CHURN = "churn"
    LTV = "ltv"
    CAC = "cac"
    ARPU = "arpu"
    MRR = "mrr"
    ARR = "arr"


class TimeFrame(str, Enum):
    """Time frame options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class RevenueDataPoint:
    """Single revenue data point."""
    timestamp: datetime
    source: RevenueSource
    amount: Decimal
    currency: str = "USD"
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsMetric:
    """Analytics metric with value and metadata."""
    name: str
    value: Union[Decimal, float, int]
    metric_type: MetricType
    period: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueReport:
    """Comprehensive revenue report."""
    report_id: str
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    revenue_by_source: Dict[str, Decimal]
    key_metrics: List[AnalyticsMetric]
    trends: Dict[str, Any]
    forecasts: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RevenueGrowth:
    """Revenue growth analysis."""
    current_period: Decimal
    previous_period: Decimal
    growth_rate: float
    growth_amount: Decimal
    trend: str  # "increasing", "decreasing", "stable"


class RevenueAnalytics:
    """Advanced revenue analytics and insights engine."""
    
    def __init__(self):
        """Initialize revenue analytics."""
        self.revenue_data: List[RevenueDataPoint] = []
        self.cached_metrics: Dict[str, AnalyticsMetric] = {}
        self.reports: Dict[str, RevenueReport] = {}
        
        # Configuration
        self.cache_duration = timedelta(hours=1)
        self.forecasting_enabled = True
        
        logger.info("Revenue analytics engine initialized")
    
    async def record_revenue(
        self,
        amount: Decimal,
        source: RevenueSource,
        user_id: Optional[str] = None,
        content_id: Optional[str] = None,
        currency: str = "USD",
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> RevenueDataPoint:
        """Record a revenue data point.
        
        Args:
            amount: Revenue amount
            source: Revenue source
            user_id: User identifier
            content_id: Content identifier
            currency: Currency code
            metadata: Additional metadata
            timestamp: Revenue timestamp (defaults to now)
            
        Returns:
            Recorded revenue data point
        """
        try:
            data_point = RevenueDataPoint(
                timestamp=timestamp or datetime.now(),
                source=source,
                amount=amount,
                currency=currency,
                user_id=user_id,
                content_id=content_id,
                metadata=metadata or {}
            )
            
            self.revenue_data.append(data_point)
            
            # Clear cached metrics that might be affected
            self._clear_relevant_cache(source)
            
            logger.info(f"Revenue recorded: ${amount} from {source.value}")
            return data_point
            
        except Exception as e:
            logger.error(f"Failed to record revenue: {e}")
            raise
    
    async def get_total_revenue(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source: Optional[RevenueSource] = None,
        currency: str = "USD"
    ) -> Decimal:
        """Get total revenue for specified period and filters.
        
        Args:
            start_date: Period start date
            end_date: Period end date
            source: Revenue source filter
            currency: Currency filter
            
        Returns:
            Total revenue amount
        """
        try:
            filtered_data = self._filter_revenue_data(
                start_date=start_date,
                end_date=end_date,
                source=source,
                currency=currency
            )
            
            total = sum(point.amount for point in filtered_data)
            
            logger.info(f"Total revenue calculated: ${total}")
            return total
            
        except Exception as e:
            logger.error(f"Failed to calculate total revenue: {e}")
            return Decimal("0")
    
    async def get_revenue_by_source(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        currency: str = "USD"
    ) -> Dict[str, Decimal]:
        """Get revenue breakdown by source.
        
        Args:
            start_date: Period start date
            end_date: Period end date
            currency: Currency filter
            
        Returns:
            Revenue amounts by source
        """
        try:
            filtered_data = self._filter_revenue_data(
                start_date=start_date,
                end_date=end_date,
                currency=currency
            )
            
            revenue_by_source = defaultdict(Decimal)
            for point in filtered_data:
                revenue_by_source[point.source.value] += point.amount
            
            return dict(revenue_by_source)
            
        except Exception as e:
            logger.error(f"Failed to calculate revenue by source: {e}")
            return {}
    
    async def get_revenue_growth(
        self,
        timeframe: TimeFrame = TimeFrame.MONTHLY,
        periods: int = 2
    ) -> RevenueGrowth:
        """Calculate revenue growth between periods.
        
        Args:
            timeframe: Time frame for comparison
            periods: Number of periods to compare
            
        Returns:
            Revenue growth analysis
        """
        try:
            now = datetime.now()
            
            # Calculate period duration
            if timeframe == TimeFrame.DAILY:
                period_delta = timedelta(days=1)
            elif timeframe == TimeFrame.WEEKLY:
                period_delta = timedelta(weeks=1)
            elif timeframe == TimeFrame.MONTHLY:
                period_delta = timedelta(days=30)
            elif timeframe == TimeFrame.QUARTERLY:
                period_delta = timedelta(days=90)
            else:  # YEARLY
                period_delta = timedelta(days=365)
            
            # Current period
            current_start = now - period_delta
            current_revenue = await self.get_total_revenue(
                start_date=current_start,
                end_date=now
            )
            
            # Previous period
            previous_start = current_start - period_delta
            previous_revenue = await self.get_total_revenue(
                start_date=previous_start,
                end_date=current_start
            )
            
            # Calculate growth
            if previous_revenue > 0:
                growth_rate = float((current_revenue - previous_revenue) / previous_revenue * 100)
            else:
                growth_rate = 100.0 if current_revenue > 0 else 0.0
            
            growth_amount = current_revenue - previous_revenue
            
            # Determine trend
            if growth_rate > 5:
                trend = "increasing"
            elif growth_rate < -5:
                trend = "decreasing"
            else:
                trend = "stable"
            
            return RevenueGrowth(
                current_period=current_revenue,
                previous_period=previous_revenue,
                growth_rate=growth_rate,
                growth_amount=growth_amount,
                trend=trend
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate revenue growth: {e}")
            return RevenueGrowth(
                current_period=Decimal("0"),
                previous_period=Decimal("0"),
                growth_rate=0.0,
                growth_amount=Decimal("0"),
                trend="stable"
            )
    
    async def get_mrr(self, date: Optional[datetime] = None) -> Decimal:
        """Calculate Monthly Recurring Revenue (MRR).
        
        Args:
            date: Date for MRR calculation
            
        Returns:
            MRR amount
        """
        try:
            target_date = date or datetime.now()
            month_start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            # Get subscription revenue for the month
            subscription_revenue = await self.get_total_revenue(
                start_date=month_start,
                end_date=month_end,
                source=RevenueSource.SUBSCRIPTIONS
            )
            
            logger.info(f"MRR calculated: ${subscription_revenue}")
            return subscription_revenue
            
        except Exception as e:
            logger.error(f"Failed to calculate MRR: {e}")
            return Decimal("0")
    
    async def get_arr(self, date: Optional[datetime] = None) -> Decimal:
        """Calculate Annual Recurring Revenue (ARR).
        
        Args:
            date: Date for ARR calculation
            
        Returns:
            ARR amount
        """
        try:
            # ARR is typically MRR * 12
            mrr = await self.get_mrr(date)
            arr = mrr * 12
            
            logger.info(f"ARR calculated: ${arr}")
            return arr
            
        except Exception as e:
            logger.error(f"Failed to calculate ARR: {e}")
            return Decimal("0")
    
    async def get_top_revenue_sources(
        self,
        limit: int = 5,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top revenue sources ranked by amount.
        
        Args:
            limit: Maximum number of sources to return
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            List of top revenue sources with amounts
        """
        try:
            revenue_by_source = await self.get_revenue_by_source(
                start_date=start_date,
                end_date=end_date
            )
            
            # Sort by revenue amount
            sorted_sources = sorted(
                revenue_by_source.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            top_sources = []
            total_revenue = sum(revenue_by_source.values())
            
            for source, amount in sorted_sources[:limit]:
                percentage = float(amount / total_revenue * 100) if total_revenue > 0 else 0
                
                top_sources.append({
                    "source": source,
                    "revenue": amount,
                    "percentage": percentage
                })
            
            return top_sources
            
        except Exception as e:
            logger.error(f"Failed to get top revenue sources: {e}")
            return []
    
    async def forecast_revenue(
        self,
        forecast_days: int = 30,
        confidence_level: float = 0.8
    ) -> Dict[str, Any]:
        """Forecast future revenue based on historical data.
        
        Args:
            forecast_days: Number of days to forecast
            confidence_level: Confidence level for forecast
            
        Returns:
            Revenue forecast data
        """
        try:
            if not self.forecasting_enabled:
                return {"error": "Forecasting disabled"}
            
            # Get historical data for the last 90 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            historical_data = self._filter_revenue_data(
                start_date=start_date,
                end_date=end_date
            )
            
            if len(historical_data) < 7:  # Need at least a week of data
                return {"error": "Insufficient historical data"}
            
            # Group data by day
            daily_revenue = defaultdict(Decimal)
            for point in historical_data:
                day_key = point.timestamp.date()
                daily_revenue[day_key] += point.amount
            
            # Calculate daily averages and trends
            daily_amounts = list(daily_revenue.values())
            average_daily = statistics.mean(daily_amounts) if daily_amounts else 0
            
            # Simple linear trend calculation
            if len(daily_amounts) > 1:
                # Calculate trend slope (simplified)
                x_values = list(range(len(daily_amounts)))
                trend_slope = self._calculate_trend_slope(x_values, daily_amounts)
            else:
                trend_slope = 0
            
            # Generate forecast
            forecasted_revenue = []
            total_forecast = Decimal("0")
            
            for day in range(forecast_days):
                # Simple forecast: average + trend * day
                forecasted_amount = Decimal(str(average_daily + (trend_slope * day)))
                forecasted_amount = max(forecasted_amount, Decimal("0"))  # No negative revenue
                
                forecast_date = end_date + timedelta(days=day + 1)
                forecasted_revenue.append({
                    "date": forecast_date.date().isoformat(),
                    "forecasted_revenue": forecasted_amount
                })
                
                total_forecast += forecasted_amount
            
            return {
                "forecast_period_days": forecast_days,
                "total_forecasted_revenue": total_forecast,
                "average_daily_forecast": total_forecast / forecast_days,
                "confidence_level": confidence_level,
                "daily_forecast": forecasted_revenue,
                "trend": "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable",
                "historical_average_daily": Decimal(str(average_daily))
            }
            
        except Exception as e:
            logger.error(f"Failed to forecast revenue: {e}")
            return {"error": str(e)}
    
    def _calculate_trend_slope(self, x_values: List[int], y_values: List[Decimal]) -> float:
        """Calculate trend slope using simple linear regression.
        
        Args:
            x_values: X coordinate values
            y_values: Y coordinate values
            
        Returns:
            Trend slope
        """
        try:
            n = len(x_values)
            if n < 2:
                return 0.0
            
            # Convert Decimal to float for calculation
            y_float = [float(y) for y in y_values]
            
            sum_x = sum(x_values)
            sum_y = sum(y_float)
            sum_xy = sum(x * y for x, y in zip(x_values, y_float))
            sum_xx = sum(x * x for x in x_values)
            
            # Calculate slope
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            return slope
            
        except Exception as e:
            logger.error(f"Failed to calculate trend slope: {e}")
            return 0.0
    
    async def generate_revenue_report(
        self,
        start_date: datetime,
        end_date: datetime,
        include_forecast: bool = True
    ) -> RevenueReport:
        """Generate comprehensive revenue report.
        
        Args:
            start_date: Report period start
            end_date: Report period end
            include_forecast: Include revenue forecast
            
        Returns:
            Comprehensive revenue report
        """
        try:
            report_id = str(uuid.uuid4())
            
            # Calculate key metrics
            total_revenue = await self.get_total_revenue(start_date, end_date)
            revenue_by_source = await self.get_revenue_by_source(start_date, end_date)
            revenue_growth = await self.get_revenue_growth()
            mrr = await self.get_mrr(end_date)
            
            key_metrics = [
                AnalyticsMetric(
                    name="Total Revenue",
                    value=total_revenue,
                    metric_type=MetricType.REVENUE,
                    period=f"{start_date.date()} to {end_date.date()}",
                    timestamp=datetime.now()
                ),
                AnalyticsMetric(
                    name="Monthly Recurring Revenue",
                    value=mrr,
                    metric_type=MetricType.MRR,
                    period=end_date.strftime("%B %Y"),
                    timestamp=datetime.now()
                ),
                AnalyticsMetric(
                    name="Revenue Growth Rate",
                    value=revenue_growth.growth_rate,
                    metric_type=MetricType.REVENUE,
                    period="Month-over-month",
                    timestamp=datetime.now()
                )
            ]
            
            # Generate trends analysis
            trends = {
                "revenue_growth": {
                    "rate": revenue_growth.growth_rate,
                    "trend": revenue_growth.trend,
                    "amount_change": revenue_growth.growth_amount
                },
                "top_sources": await self.get_top_revenue_sources(
                    start_date=start_date,
                    end_date=end_date
                )
            }
            
            # Generate forecasts if requested
            forecasts = {}
            if include_forecast:
                forecasts = await self.forecast_revenue()
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                revenue_by_source, revenue_growth, total_revenue
            )
            
            report = RevenueReport(
                report_id=report_id,
                period_start=start_date,
                period_end=end_date,
                total_revenue=total_revenue,
                revenue_by_source=revenue_by_source,
                key_metrics=key_metrics,
                trends=trends,
                forecasts=forecasts,
                recommendations=recommendations
            )
            
            self.reports[report_id] = report
            
            logger.info(f"Revenue report generated: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate revenue report: {e}")
            raise
    
    async def _generate_recommendations(
        self,
        revenue_by_source: Dict[str, Decimal],
        revenue_growth: RevenueGrowth,
        total_revenue: Decimal
    ) -> List[str]:
        """Generate actionable recommendations based on analytics.
        
        Args:
            revenue_by_source: Revenue breakdown by source
            revenue_growth: Revenue growth analysis
            total_revenue: Total revenue amount
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            # Growth-based recommendations
            if revenue_growth.growth_rate < 0:
                recommendations.append(
                    "Revenue is declining. Consider reviewing pricing strategy and customer retention programs."
                )
            elif revenue_growth.growth_rate < 5:
                recommendations.append(
                    "Revenue growth is slow. Explore new revenue streams and optimization opportunities."
                )
            
            # Source diversification recommendations
            if len(revenue_by_source) == 1:
                recommendations.append(
                    "Revenue is concentrated in a single source. Consider diversifying revenue streams to reduce risk."
                )
            
            # Top source recommendations
            if revenue_by_source:
                top_source = max(revenue_by_source.items(), key=lambda x: x[1])
                if top_source[1] / total_revenue > 0.8:
                    recommendations.append(
                        f"Over 80% of revenue comes from {top_source[0]}. Consider expanding other revenue sources."
                    )
            
            # Subscription-specific recommendations
            subscription_revenue = revenue_by_source.get("subscriptions", Decimal("0"))
            if subscription_revenue / total_revenue < 0.3 and total_revenue > 1000:
                recommendations.append(
                    "Subscription revenue is low. Consider introducing or promoting subscription plans for more predictable revenue."
                )
            
            # General recommendations based on total revenue
            if total_revenue < 1000:
                recommendations.append(
                    "Focus on customer acquisition and conversion optimization to scale revenue."
                )
            elif total_revenue > 10000:
                recommendations.append(
                    "Consider implementing advanced analytics and automation to optimize high-volume revenue streams."
                )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Unable to generate recommendations due to data processing error."]
    
    def _filter_revenue_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source: Optional[RevenueSource] = None,
        currency: Optional[str] = None
    ) -> List[RevenueDataPoint]:
        """Filter revenue data based on criteria.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            source: Revenue source filter
            currency: Currency filter
            
        Returns:
            Filtered revenue data points
        """
        filtered_data = self.revenue_data
        
        if start_date:
            filtered_data = [p for p in filtered_data if p.timestamp >= start_date]
        
        if end_date:
            filtered_data = [p for p in filtered_data if p.timestamp <= end_date]
        
        if source:
            filtered_data = [p for p in filtered_data if p.source == source]
        
        if currency:
            filtered_data = [p for p in filtered_data if p.currency == currency]
        
        return filtered_data
    
    def _clear_relevant_cache(self, source: RevenueSource) -> None:
        """Clear cached metrics that might be affected by new data.
        
        Args:
            source: Revenue source that was updated
        """
        # Simple cache clearing - in production, would be more sophisticated
        keys_to_remove = [
            key for key in self.cached_metrics.keys()
            if source.value in key or "total" in key.lower()
        ]
        
        for key in keys_to_remove:
            del self.cached_metrics[key]
    
    async def get_report(self, report_id: str) -> Optional[RevenueReport]:
        """Get revenue report by ID.
        
        Args:
            report_id: Report identifier
            
        Returns:
            Revenue report if found
        """
        return self.reports.get(report_id)