"""Revenue Analytics Engine
=======================

Advanced revenue tracking, analysis, and optimization for multi-platform monetization.
Provides comprehensive revenue insights, forecasting, and optimization recommendations.

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
from decimal import Decimal

import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from redis import Redis
import json
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


class RevenueStream(Enum):
    """
Revenue stream types"""

    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    SPONSORSHIP = "sponsorship"
    LICENSING = "licensing"
    MERCHANDISE = "merchandise"
    DONATIONS = "donations"
    LIVE_STREAMING = "live_streaming"
    PREMIUM_CONTENT = "premium_content"
    AFFILIATE_MARKETING = "affiliate_marketing"
    BRAND_PARTNERSHIPS = "brand_partnerships"


class PaymentStatus(Enum):
    """Payment status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class RevenueCategory(Enum):
    """Revenue category classification"""

    DIRECT = "direct"
    INDIRECT = "indirect"
    RECURRING = "recurring"
    ONE_TIME = "one_time"
    PERFORMANCE_BASED = "performance_based"


@dataclass
class RevenueMetric:
    """Individual revenue metric"""
    metric_id: str
    user_id: str
    platform: str
    revenue_stream: RevenueStream
    amount: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    growth_rate: float
    forecast_confidence: float
    benchmark_comparison: float


@dataclass
class RevenueBreakdown:
    """
Detailed revenue breakdown"""
    total_revenue: Decimal
    platform_breakdown: Dict[str, Decimal]
    stream_breakdown: Dict[str, Decimal]
    currency_breakdown: Dict[str, Decimal]
    growth_metrics: Dict[str, float]
    top_performers: List[Dict]
    underperformers: List[Dict]


@dataclass
class RevenueForecast:
    """
Revenue forecast data"""
    forecast_period: str
    predicted_revenue: Decimal
    confidence_interval: Tuple[Decimal, Decimal]
    growth_projection: float
    key_drivers: List[str]
    risk_factors: List[str]
    recommendations: List[str]


@dataclass
class RevenueOptimization:
    """
Revenue optimization insights"""
    current_efficiency: float
    optimization_potential: Decimal
    priority_actions: List[Dict]
    expected_improvement: float
    implementation_timeline: str
    required_investment: Decimal


class RevenueAnalytics:
    """
    Professional revenue analytics engine for multi-platform monetization.
    
    Provides comprehensive revenue tracking, forecasting, optimization insights,
    and automated financial reporting for content creators and influencers.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        """
        Initialize RevenueAnalytics engine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """
        self.db_session = db_session
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        self.cache_ttl = 1800  # 30 minutes cache for revenue data
        
    async def calculate_total_revenue(self, user_id: str,
                                    time_period: timedelta = timedelta(days=30),
                                    currency: str = "EUR"
                                    ) -> RevenueBreakdown:
        """
        Calculate comprehensive revenue breakdown for user.
        
        Args:
            user_id: User identifier
            time_period: Analysis time period
            currency: Target currency for conversion
            
        Returns:
            Comprehensive revenue breakdown
        """
        try:
            cache_key = f"revenue_total:{user_id}:{time_period.days}:{currency}"
            cached_result = await self._get_cached_result(cache_key)
            
            if cached_result:
                return RevenueBreakdown(**cached_result)
                
            end_date = datetime.utcnow()
            start_date = end_date - time_period
            
            # Get total revenue data
            query = text("""
                SELECT 
                    SUM(CASE WHEN rm.currency = :currency THEN rm.amount 
                             ELSE rm.amount * er.exchange_rate END) as total_revenue,
                    rm.platform,
                    rm.revenue_stream,
                    rm.currency as original_currency,
                    SUM(rm.amount) as original_amount
                FROM revenue_metrics rm
                LEFT JOIN exchange_rates er ON rm.currency = er.from_currency 
                    AND er.to_currency = :currency
                    AND DATE(er.updated_at) = DATE(rm.created_at)
                WHERE rm.user_id = :user_id 
                AND rm.created_at BETWEEN :start_date AND :end_date
                AND rm.status = 'completed'
                GROUP BY rm.platform, rm.revenue_stream, rm.currency
                ORDER BY total_revenue DESC
            """)
            
            result = await self.db_session.execute(
                query,
                {
                    "user_id": user_id,
                    "currency": currency,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            revenue_data = result.fetchall()
            
            if not revenue_data:
                return RevenueBreakdown(
                    total_revenue=Decimal('0'),
                    platform_breakdown={},
                    stream_breakdown={},
                    currency_breakdown={},
                    growth_metrics={},
                    top_performers=[],
                    underperformers=[]
                )
            
            # Calculate breakdowns
            total_revenue = sum(row.total_revenue or 0 for row in revenue_data)
            
            platform_breakdown = {}
            stream_breakdown = {}
            currency_breakdown = {}
            
            for row in revenue_data:
                # Platform breakdown
                if row.platform in platform_breakdown:
                    platform_breakdown[row.platform] += row.total_revenue or 0
                else:
                    platform_breakdown[row.platform] = row.total_revenue or 0
                
                # Stream breakdown
                if row.revenue_stream in stream_breakdown:
                    stream_breakdown[row.revenue_stream] += row.total_revenue or 0
                else:
                    stream_breakdown[row.revenue_stream] = row.total_revenue or 0
                
                # Currency breakdown
                if row.original_currency in currency_breakdown:
                    currency_breakdown[row.original_currency] += row.original_amount or 0
                else:
                    currency_breakdown[row.original_currency] = row.original_amount or 0
            
            # Calculate growth metrics
            growth_metrics = await self._calculate_revenue_growth(user_id, time_period, currency)
            
            # Identify top performers and underperformers
            sorted_platforms = sorted(platform_breakdown.items(), key=lambda x: x[1], reverse=True)
            top_performers = [{"platform": k, "revenue": v, "percentage": v/total_revenue*100} 
                            for k, v in sorted_platforms[:3]]
            underperformers = [{"platform": k, "revenue": v, "percentage": v/total_revenue*100} 
                             for k, v in sorted_platforms[-2:] if v > 0]
            
            breakdown = RevenueBreakdown(
                total_revenue=Decimal(str(total_revenue)),
                platform_breakdown={k: Decimal(str(v)) for k, v in platform_breakdown.items()},
                stream_breakdown={k: Decimal(str(v)) for k, v in stream_breakdown.items()},
                currency_breakdown={k: Decimal(str(v)) for k, v in currency_breakdown.items()},
                growth_metrics=growth_metrics,
                top_performers=top_performers,
                underperformers=underperformers
            )
            
            # Cache results
            await self._cache_result(cache_key, breakdown.__dict__)
            
            return breakdown
            
        except Exception as e:
            self.logger.error(f"Error calculating total revenue: {str(e)}")
            return RevenueBreakdown(
                total_revenue=Decimal('0'),
                platform_breakdown={},
                stream_breakdown={},
                currency_breakdown={},
                growth_metrics={},
                top_performers=[],
                underperformers=[]
            )
    
    async def generate_revenue_forecast(self, user_id: str,
                                      forecast_days: int = 90,
                                      currency: str = "EUR"
                                      ) -> RevenueForecast:
        """
        Generate revenue forecast using machine learning algorithms.
        
        Args:
            user_id: User identifier
            forecast_days: Number of days to forecast
            currency: Target currency
            
        Returns:
            Revenue forecast with confidence intervals
        """
        try:
            cache_key = f"revenue_forecast:{user_id}:{forecast_days}:{currency}"
            cached_result = await self._get_cached_result(cache_key)
            
            if cached_result:
                return RevenueForecast(**cached_result)
            
            # Get historical revenue data (last 12 months for better prediction)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)
            
            query = text("""
                SELECT 
                    DATE(rm.created_at) as revenue_date,
                    SUM(CASE WHEN rm.currency = :currency THEN rm.amount 
                             ELSE rm.amount * COALESCE(er.exchange_rate, 1) END) as daily_revenue
                FROM revenue_metrics rm
                LEFT JOIN exchange_rates er ON rm.currency = er.from_currency 
                    AND er.to_currency = :currency
                WHERE rm.user_id = :user_id 
                AND rm.created_at BETWEEN :start_date AND :end_date
                AND rm.status = 'completed'
                GROUP BY DATE(rm.created_at)
                ORDER BY revenue_date
            """)
            
            result = await self.db_session.execute(
                query,
                {
                    "user_id": user_id,
                    "currency": currency,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            historical_data = result.fetchall()
            
            if len(historical_data) < 30:  # Need minimum data for forecast
                return RevenueForecast(
                    forecast_period=f"{forecast_days} days",
                    predicted_revenue=Decimal('0'),
                    confidence_interval=(Decimal('0'), Decimal('0')),
                    growth_projection=0.0,
                    key_drivers=[],
                    risk_factors=["Insufficient historical data for accurate forecasting"],
                    recommendations=["Collect more revenue data over time"]
                )
            
            # Prepare data for ML prediction
            df = pd.DataFrame([(row.revenue_date, float(row.daily_revenue)) 
                             for row in historical_data], 
                             columns=['date', 'revenue'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            df = df.resample('D').sum().fillna(0)
            
            # Create features for ML model
            df['day_of_year'] = df.index.dayofyear
            df['day_of_week'] = df.index.dayofweek
            df['month'] = df.index.month
            df['revenue_ma_7'] = df['revenue'].rolling(window=7).mean()
            df['revenue_ma_30'] = df['revenue'].rolling(window=30).mean()
            df['revenue_trend'] = df['revenue'].rolling(window=14).apply(
                lambda x: stats.linregress(range(len(x)), x)[0] if len(x) > 1 else 0
            )
            
            # Remove NaN values
            df = df.dropna()
            
            if len(df) < 20:
                return RevenueForecast(
                    forecast_period=f"{forecast_days} days",
                    predicted_revenue=Decimal('0'),
                    confidence_interval=(Decimal('0'), Decimal('0')),
                    growth_projection=0.0,
                    key_drivers=[],
                    risk_factors=["Insufficient clean data for forecasting"],
                    recommendations=["Improve data quality and consistency"]
                )
            
            # Prepare features and target
            feature_columns = ['day_of_year', 'day_of_week', 'month', 'revenue_ma_7', 'revenue_ma_30', 'revenue_trend']
            X = df[feature_columns].values
            y = df['revenue'].values
            
            # Create polynomial features for better prediction
            poly_features = PolynomialFeatures(degree=2, include_bias=False)
            X_poly = poly_features.fit_transform(X)
            
            # Train model
            model = LinearRegression()
            model.fit(X_poly, y)
            
            # Generate forecast
            last_date = df.index[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days)
            
            forecast_features = []
            for date in forecast_dates:
                features = [
                    date.dayofyear,
                    date.dayofweek,
                    date.month,
                    df['revenue'].tail(7).mean(),  # Recent 7-day average
                    df['revenue'].tail(30).mean(),  # Recent 30-day average
                    df['revenue_trend'].iloc[-1]  # Recent trend
                ]
                forecast_features.append(features)
            
            X_forecast = np.array(forecast_features)
            X_forecast_poly = poly_features.transform(X_forecast)
            
            # Make predictions
            predictions = model.predict(X_forecast_poly)
            predictions = np.maximum(predictions, 0)  # Ensure non-negative revenue
            
            # Calculate confidence intervals (using prediction errors)
            residuals = y - model.predict(X_poly)
            std_error = np.std(residuals)
            confidence_lower = predictions - 1.96 * std_error
            confidence_upper = predictions + 1.96 * std_error
            
            # Aggregate forecast
            total_predicted = sum(predictions)
            total_lower = sum(np.maximum(confidence_lower, 0))
            total_upper = sum(confidence_upper)
            
            # Calculate growth projection
            recent_revenue = df['revenue'].tail(30).sum()
            growth_projection = ((total_predicted - recent_revenue) / recent_revenue * 100) if recent_revenue > 0 else 0
            
            # Identify key drivers and risk factors
            key_drivers = await self._identify_revenue_drivers(user_id)
            risk_factors = await self._identify_risk_factors(user_id, df)
            recommendations = await self._generate_revenue_recommendations(user_id, predictions, df)
            
            forecast = RevenueForecast(
                forecast_period=f"{forecast_days} days",
                predicted_revenue=Decimal(str(round(total_predicted, 2))),
                confidence_interval=(Decimal(str(round(total_lower, 2))), 
                                   Decimal(str(round(total_upper, 2)))),
                growth_projection=growth_projection,
                key_drivers=key_drivers,
                risk_factors=risk_factors,
                recommendations=recommendations
            )
            
            # Cache forecast for 6 hours
            await self._cache_result(cache_key, forecast.__dict__, ttl=21600)
            
            return forecast
            
        except Exception as e:
            self.logger.error(f"Error generating revenue forecast: {str(e)}")
            return RevenueForecast(
                forecast_period=f"{forecast_days} days",
                predicted_revenue=Decimal('0'),
                confidence_interval=(Decimal('0'), Decimal('0')),
                growth_projection=0.0,
                key_drivers=[],
                risk_factors=["Error in forecast generation"],
                recommendations=["Review data quality and try again"]
            )
    
    async def analyze_revenue_optimization(self, user_id: str,
                                         time_period: timedelta = timedelta(days=90)
                                         ) -> RevenueOptimization:
        """
        Analyze revenue optimization opportunities.
        
        Args:
            user_id: User identifier
            time_period: Analysis period
            
        Returns:
            Revenue optimization insights and recommendations
        """
        try:
            cache_key = f"revenue_optimization:{user_id}:{time_period.days}"
            cached_result = await self._get_cached_result(cache_key)
            
            if cached_result:
                return RevenueOptimization(**cached_result)
            
            # Calculate current revenue efficiency
            current_metrics = await self.calculate_total_revenue(user_id, time_period)
            efficiency = await self._calculate_revenue_efficiency(user_id, time_period)
            
            # Identify optimization opportunities
            optimization_potential = await self._calculate_optimization_potential(user_id, time_period)
            priority_actions = await self._identify_priority_actions(user_id, current_metrics)
            
            # Calculate expected improvement
            expected_improvement = min(optimization_potential / float(current_metrics.total_revenue) * 100, 50.0) if current_metrics.total_revenue > 0 else 0
            
            optimization = RevenueOptimization(
                current_efficiency=efficiency,
                optimization_potential=optimization_potential,
                priority_actions=priority_actions,
                expected_improvement=expected_improvement,
                implementation_timeline="2-6 months",
                required_investment=optimization_potential * Decimal('0.1')  # 10% investment ratio
            )
            
            await self._cache_result(cache_key, optimization.__dict__)
            
            return optimization
            
        except Exception as e:
            self.logger.error(f"Error analyzing revenue optimization: {str(e)}")
            return RevenueOptimization(
                current_efficiency=0.0,
                optimization_potential=Decimal('0'),
                priority_actions=[],
                expected_improvement=0.0,
                implementation_timeline="Unknown",
                required_investment=Decimal('0')
            )
    
    async def track_payment_status(self, user_id: str,
                                 payment_ids: Optional[List[str]] = None
                                 ) -> Dict[str, Any]:
        """
        Track payment status and processing information.
        
        Args:
            user_id: User identifier
            payment_ids: Specific payment IDs to track (optional)
            
        Returns:
            Payment status information
        """
        try:
            query_conditions = "WHERE rm.user_id = :user_id"
            query_params = {"user_id": user_id}
            
            if payment_ids:
                query_conditions += " AND rm.payment_id = ANY(:payment_ids)"
                query_params["payment_ids"] = payment_ids
            
            query = text(f"""
                SELECT 
                    rm.payment_id,
                    rm.amount,
                    rm.currency,
                    rm.status,
                    rm.platform,
                    rm.revenue_stream,
                    rm.created_at,
                    rm.updated_at,
                    pp.processing_fee,
                    pp.expected_completion_date
                FROM revenue_metrics rm
                LEFT JOIN payment_processing pp ON rm.payment_id = pp.payment_id
                {query_conditions}
                ORDER BY rm.created_at DESC
                LIMIT 100
            """)
            
            result = await self.db_session.execute(query, query_params)
            payments = result.fetchall()
            
            # Aggregate payment status data
            status_summary = {}
            total_pending = Decimal('0')
            total_processing = Decimal('0')
            total_completed = Decimal('0')
            
            payment_details = []
            
            for payment in payments:
                status = payment.status
                amount = Decimal(str(payment.amount))
                
                if status not in status_summary:
                    status_summary[status] = {"count": 0, "total_amount": Decimal('0')}
                
                status_summary[status]["count"] += 1
                status_summary[status]["total_amount"] += amount
                
                if status == PaymentStatus.PENDING.value:
                    total_pending += amount
                elif status == PaymentStatus.PROCESSING.value:
                    total_processing += amount
                elif status == PaymentStatus.COMPLETED.value:
                    total_completed += amount
                
                payment_details.append({
                    "payment_id": payment.payment_id,
                    "amount": float(amount),
                    "currency": payment.currency,
                    "status": payment.status,
                    "platform": payment.platform,
                    "revenue_stream": payment.revenue_stream,
                    "created_at": payment.created_at.isoformat(),
                    "processing_fee": float(payment.processing_fee or 0),
                    "expected_completion": payment.expected_completion_date.isoformat() if payment.expected_completion_date else None
                })
            
            return {
                "user_id": user_id,
                "summary": {
                    "total_pending": float(total_pending),
                    "total_processing": float(total_processing),
                    "total_completed": float(total_completed),
                    "status_breakdown": {k: {"count": v["count"], "amount": float(v["total_amount"])} 
                                       for k, v in status_summary.items()}
                },
                "payment_details": payment_details,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking payment status: {str(e)}")
            return {"error": str(e)}
    
    async def _calculate_revenue_growth(self, user_id: str, time_period: timedelta, currency: str) -> Dict[str, float]:
        """Calculate revenue growth metrics."""
        try:
            # Get current period revenue
            current_end = datetime.utcnow()
            current_start = current_end - time_period
            
            # Get previous period revenue
            previous_end = current_start
            previous_start = previous_end - time_period
            
            # Current period query
            current_query = text("""
                SELECT SUM(CASE WHEN rm.currency = :currency THEN rm.amount 
                               ELSE rm.amount * COALESCE(er.exchange_rate, 1) END) as revenue
                FROM revenue_metrics rm
                LEFT JOIN exchange_rates er ON rm.currency = er.from_currency 
                WHERE rm.user_id = :user_id 
                AND rm.created_at BETWEEN :start_date AND :end_date
                AND rm.status = 'completed'
            """)
            
            current_result = await self.db_session.execute(
                current_query,
                {
                    "user_id": user_id,
                    "currency": currency,
                    "start_date": current_start,
                    "end_date": current_end
                }
            )
            current_revenue = current_result.scalar() or 0
            
            # Previous period query
            previous_result = await self.db_session.execute(
                current_query,
                {
                    "user_id": user_id,
                    "currency": currency,
                    "start_date": previous_start,
                    "end_date": previous_end
                }
            )
            previous_revenue = previous_result.scalar() or 0
            
            # Calculate growth metrics
            growth_rate = 0
            if previous_revenue > 0:
                growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
            
            # Calculate compound annual growth rate (CAGR) if applicable
            periods_per_year = 365 / time_period.days
            cagr = 0
            if previous_revenue > 0 and current_revenue > 0:
                cagr = (pow(current_revenue / previous_revenue, 1/periods_per_year) - 1) * 100
            
            return {
                "period_growth_rate": growth_rate,
                "compound_annual_growth_rate": cagr,
                "current_period_revenue": current_revenue,
                "previous_period_revenue": previous_revenue,
                "revenue_momentum": "positive" if growth_rate > 0 else "negative" if growth_rate < 0 else "stable"
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating revenue growth: {str(e)}")
            return {}
    
    async def _identify_revenue_drivers(self, user_id: str) -> List[str]:
        """Identify key revenue drivers for forecasting."""
        try:
            # Analyze revenue by stream and platform to identify top drivers
            query = text("""
                SELECT 
                    revenue_stream,
                    platform,
                    SUM(amount) as total_revenue,
                    COUNT(*) as transaction_count,
                    AVG(amount) as avg_transaction_value
                FROM revenue_metrics
                WHERE user_id = :user_id 
                AND created_at >= NOW() - INTERVAL '90 days'
                AND status = 'completed'
                GROUP BY revenue_stream, platform
                ORDER BY total_revenue DESC
                LIMIT 5
            """)
            
            result = await self.db_session.execute(query, {"user_id": user_id})
            top_drivers = result.fetchall()
            
            drivers = []
            for driver in top_drivers:
                drivers.append(f"{driver.revenue_stream} on {driver.platform} (${driver.total_revenue:.2f})")
            
            return drivers or ["Content performance", "Audience engagement", "Platform algorithms"]
            
        except Exception as e:
            self.logger.error(f"Error identifying revenue drivers: {str(e)}")
            return ["Content performance", "Audience engagement", "Platform algorithms"]
    
    async def _identify_risk_factors(self, user_id: str, df: pd.DataFrame) -> List[str]:
        """Identify revenue risk factors."""
        try:
            risk_factors = []
            
            # Check revenue volatility
            revenue_cv = df['revenue'].std() / df['revenue'].mean() if df['revenue'].mean() > 0 else 0
            if revenue_cv > 0.5:
                risk_factors.append("High revenue volatility")
            
            # Check for declining trend
            if len(df) > 7:
                recent_trend = stats.linregress(range(7), df['revenue'].tail(7).values)[0]
                if recent_trend < 0:
                    risk_factors.append("Recent declining revenue trend")
            
            # Check platform concentration
            query = text("""
                SELECT platform, SUM(amount) as revenue
                FROM revenue_metrics
                WHERE user_id = :user_id AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY platform
                ORDER BY revenue DESC
            """)
            
            result = await self.db_session.execute(query, {"user_id": user_id})
            platform_revenues = result.fetchall()
            
            if platform_revenues:
                total = sum(row.revenue for row in platform_revenues)
                top_platform_share = platform_revenues[0].revenue / total if total > 0 else 0
                if top_platform_share > 0.8:
                    risk_factors.append("High dependency on single platform")
            
            return risk_factors or ["Market volatility", "Platform policy changes"]
            
        except Exception as e:
            self.logger.error(f"Error identifying risk factors: {str(e)}")
            return ["Market volatility", "Platform policy changes"]
    
    async def _generate_revenue_recommendations(self, user_id: str, predictions: np.ndarray, df: pd.DataFrame) -> List[str]:
        """Generate revenue optimization recommendations."""
        try:
            recommendations = []
            
            # Analyze prediction trends
            if len(predictions) > 7:
                trend = np.polyfit(range(len(predictions)), predictions, 1)[0]
                if trend > 0:
                    recommendations.append("Revenue forecast shows positive trend - maintain current strategies")
                else:
                    recommendations.append("Revenue forecast shows decline - consider diversification")
            
            # Analyze seasonality
            if len(df) > 30:
                monthly_avg = df.groupby(df.index.month)['revenue'].mean()
                best_month = monthly_avg.idxmax()
                recommendations.append(f"Focus content strategy around month {best_month} patterns")
            
            # Platform diversification
            recommendations.append("Diversify revenue streams across multiple platforms")
            recommendations.append("Implement automated revenue tracking and optimization")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return ["Monitor revenue trends regularly", "Diversify income sources"]
    
    async def _calculate_revenue_efficiency(self, user_id: str, time_period: timedelta) -> float:
        """Calculate revenue efficiency score."""
        try:
            # This is a simplified efficiency calculation
            # In practice, this would consider costs, time investment, etc.
            revenue_breakdown = await self.calculate_total_revenue(user_id, time_period)
            
            # Calculate efficiency based on revenue diversity and growth
            platform_count = len(revenue_breakdown.platform_breakdown)
            stream_count = len(revenue_breakdown.stream_breakdown)
            
            # Base efficiency on diversification
            efficiency = min((platform_count * 20) + (stream_count * 15), 100)
            
            # Adjust for growth
            growth_rate = revenue_breakdown.growth_metrics.get("period_growth_rate", 0)
            if growth_rate > 0:
                efficiency = min(efficiency * (1 + growth_rate / 100), 100)
            
            return max(efficiency, 0)
            
        except Exception as e:
            self.logger.error(f"Error calculating revenue efficiency: {str(e)}")
            return 0.0
    
    async def _calculate_optimization_potential(self, user_id: str, time_period: timedelta) -> Decimal:
        """Calculate potential revenue optimization amount."""
        try:
            current_revenue = await self.calculate_total_revenue(user_id, time_period)
            current_efficiency = await self._calculate_revenue_efficiency(user_id, time_period)
            
            # Estimate optimization potential based on efficiency gap
            efficiency_gap = 100 - current_efficiency
            optimization_multiplier = efficiency_gap / 100 * 0.3  # 30% max improvement
            
            potential = current_revenue.total_revenue * Decimal(str(optimization_multiplier))
            
            return potential
            
        except Exception as e:
            self.logger.error(f"Error calculating optimization potential: {str(e)}")
            return Decimal('0')
    
    async def _identify_priority_actions(self, user_id: str, current_metrics: RevenueBreakdown) -> List[Dict]:
        """Identify priority actions for revenue optimization."""
        try:
            actions = []
            
            # Platform diversification
            if len(current_metrics.platform_breakdown) < 3:
                actions.append({
                    "action": "Expand to additional platforms",
                    "priority": "High",
                    "expected_impact": "20-30% revenue increase",
                    "timeline": "1-2 months"
                })
            
            # Revenue stream diversification
            if len(current_metrics.stream_breakdown) < 3:
                actions.append({
                    "action": "Diversify revenue streams",
                    "priority": "Medium",
                    "expected_impact": "15-25% revenue increase",
                    "timeline": "2-3 months"
                })
            
            # Top performer optimization
            if current_metrics.top_performers:
                top_platform = current_metrics.top_performers[0]['platform']
                actions.append({
                    "action": f"Optimize {top_platform} strategy",
                    "priority": "High",
                    "expected_impact": "10-15% revenue increase",
                    "timeline": "2-4 weeks"
                })
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Error identifying priority actions: {str(e)}")
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
