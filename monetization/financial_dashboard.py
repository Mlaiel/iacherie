"""Financial Dashboard Engine
Real-time financial analytics, KPI tracking, and revenue monitoring system
for comprehensive financial oversight and decision-making support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import statistics

logger = logging.getLogger(__name__)


class MetricPeriod(Enum):
    """Time periods for metrics calculation"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class RevenueType(Enum):
    """Revenue categorization"""
    SUBSCRIPTION = "subscription"
    USAGE = "usage"
    LICENSE = "license"
    COMMISSION = "commission"
    ONE_TIME = "one_time"


@dataclass
class RevenueMetric:
    """Revenue metric data point"""
    timestamp: datetime
    amount: Decimal
    currency: str
    revenue_type: RevenueType
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None
    region: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class KPISnapshot:
    """Key Performance Indicator snapshot"""
    timestamp: datetime
    mrr: Decimal
    arr: Decimal
    churn_rate: Decimal
    ltv: Decimal
    cac: Decimal
    active_subscriptions: int
    new_customers: int
    revenue_growth: Decimal
    gross_margin: Decimal


@dataclass
class FinancialForecast:
    """Financial forecast data"""
    period: str
    predicted_mrr: Decimal
    predicted_arr: Decimal
    confidence_interval: Tuple[Decimal, Decimal]
    growth_rate: Decimal
    factors: List[str]


class FinancialDashboard:
    """Comprehensive financial dashboard and analytics engine"""
    
    def __init__(self):
        self.revenue_metrics = []
        self.kpi_snapshots = []
        self.customer_metrics = {}
        self.regional_metrics = {}
        self.cached_metrics = {}
        self.cache_ttl = timedelta(minutes=5)
        
    async def track_revenue(
        self,
        amount: Decimal,
        currency: str,
        revenue_type: RevenueType,
        customer_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        region: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Track new revenue event"""
        try:
            metric = RevenueMetric(
                timestamp=datetime.now(),
                amount=amount,
                currency=currency,
                revenue_type=revenue_type,
                customer_id=customer_id,
                subscription_id=subscription_id,
                region=region,
                metadata=metadata or {}
            )
            
            self.revenue_metrics.append(metric)
            
            # Clear relevant caches
            self._invalidate_cache()
            
            logger.debug(f"Revenue tracked: {amount} {currency} ({revenue_type.value})")
            
        except Exception as e:
            logger.error(f"Error tracking revenue: {str(e)}")
            
    async def get_revenue_overview(
        self,
        period: MetricPeriod = MetricPeriod.MONTH,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """Get comprehensive revenue overview"""
        try:
            cache_key = f"revenue_overview_{period.value}_{currency}"
            if self._is_cached(cache_key):
                return self.cached_metrics[cache_key]["data"]
                
            end_date = datetime.now()
            start_date = self._get_period_start(end_date, period)
            
            # Filter metrics for period and currency
            period_metrics = [
                m for m in self.revenue_metrics
                if (start_date <= m.timestamp <= end_date and 
                    m.currency == currency)
            ]
            
            # Calculate totals by type
            revenue_by_type = {}
            for metric in period_metrics:
                type_key = metric.revenue_type.value
                if type_key not in revenue_by_type:
                    revenue_by_type[type_key] = Decimal('0')
                revenue_by_type[type_key] += metric.amount
                
            total_revenue = sum(revenue_by_type.values())
            
            # Calculate growth compared to previous period
            prev_start = self._get_period_start(start_date, period)
            prev_metrics = [
                m for m in self.revenue_metrics
                if (prev_start <= m.timestamp < start_date and 
                    m.currency == currency)
            ]
            prev_revenue = sum(m.amount for m in prev_metrics)
            
            growth_rate = Decimal('0')
            if prev_revenue > 0:
                growth_rate = ((total_revenue - prev_revenue) / prev_revenue) * 100
                
            # Calculate average transaction value
            avg_transaction = Decimal('0')
            if period_metrics:
                avg_transaction = total_revenue / len(period_metrics)
                
            overview = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "type": period.value
                },
                "total_revenue": float(total_revenue),
                "revenue_by_type": {k: float(v) for k, v in revenue_by_type.items()},
                "growth_rate_percent": float(growth_rate),
                "transaction_count": len(period_metrics),
                "average_transaction_value": float(avg_transaction),
                "currency": currency,
                "generated_at": datetime.now().isoformat()
            }
            
            # Cache the result
            self._cache_result(cache_key, overview)
            
            return overview
            
        except Exception as e:
            logger.error(f"Error getting revenue overview: {str(e)}")
            return {}
            
    async def calculate_mrr_breakdown(self, currency: str = "EUR") -> Dict[str, Any]:
        """Calculate detailed Monthly Recurring Revenue breakdown"""
        try:
            cache_key = f"mrr_breakdown_{currency}"
            if self._is_cached(cache_key):
                return self.cached_metrics[cache_key]["data"]
                
            # Get subscription revenue for last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            subscription_metrics = [
                m for m in self.revenue_metrics
                if (m.revenue_type == RevenueType.SUBSCRIPTION and
                    start_date <= m.timestamp <= end_date and
                    m.currency == currency)
            ]
            
            # Group by subscription for MRR calculation
            subscription_revenue = {}
            for metric in subscription_metrics:
                sub_id = metric.subscription_id or "unknown"
                if sub_id not in subscription_revenue:
                    subscription_revenue[sub_id] = []
                subscription_revenue[sub_id].append(metric)
                
            # Calculate MRR components
            new_mrr = Decimal('0')
            expansion_mrr = Decimal('0')
            contraction_mrr = Decimal('0')
            churned_mrr = Decimal('0')
            net_new_mrr = Decimal('0')
            
            for sub_id, metrics in subscription_revenue.items():
                # Calculate monthly value for this subscription
                monthly_value = sum(m.amount for m in metrics)
                
                # Determine MRR type based on subscription history
                mrr_type = self._classify_mrr_type(sub_id, monthly_value)
                
                if mrr_type == "new":
                    new_mrr += monthly_value
                elif mrr_type == "expansion":
                    expansion_mrr += monthly_value
                elif mrr_type == "contraction":
                    contraction_mrr += monthly_value
                elif mrr_type == "churned":
                    churned_mrr += monthly_value
                    
            net_new_mrr = new_mrr + expansion_mrr - contraction_mrr - churned_mrr
            total_mrr = sum(subscription_revenue[sub_id][0].amount for sub_id in subscription_revenue)
            
            breakdown = {
                "total_mrr": float(total_mrr),
                "new_mrr": float(new_mrr),
                "expansion_mrr": float(expansion_mrr),
                "contraction_mrr": float(contraction_mrr),
                "churned_mrr": float(churned_mrr),
                "net_new_mrr": float(net_new_mrr),
                "mrr_growth_rate": float((net_new_mrr / total_mrr * 100) if total_mrr > 0 else 0),
                "active_subscriptions": len(subscription_revenue),
                "currency": currency,
                "calculated_at": datetime.now().isoformat()
            }
            
            self._cache_result(cache_key, breakdown)
            return breakdown
            
        except Exception as e:
            logger.error(f"Error calculating MRR breakdown: {str(e)}")
            return {}
            
    async def get_customer_lifetime_value(self, currency: str = "EUR") -> Dict[str, Any]:
        """Calculate Customer Lifetime Value (CLV) metrics"""
        try:
            cache_key = f"clv_metrics_{currency}"
            if self._is_cached(cache_key):
                return self.cached_metrics[cache_key]["data"]
                
            # Group revenue by customer
            customer_revenue = {}
            customer_first_purchase = {}
            customer_last_purchase = {}
            
            for metric in self.revenue_metrics:
                if metric.currency != currency or not metric.customer_id:
                    continue
                    
                customer_id = metric.customer_id
                
                if customer_id not in customer_revenue:
                    customer_revenue[customer_id] = Decimal('0')
                    customer_first_purchase[customer_id] = metric.timestamp
                    customer_last_purchase[customer_id] = metric.timestamp
                    
                customer_revenue[customer_id] += metric.amount
                
                if metric.timestamp < customer_first_purchase[customer_id]:
                    customer_first_purchase[customer_id] = metric.timestamp
                if metric.timestamp > customer_last_purchase[customer_id]:
                    customer_last_purchase[customer_id] = metric.timestamp
                    
            if not customer_revenue:
                return {"average_clv": 0, "currency": currency, "customer_count": 0}
                
            # Calculate CLV metrics
            total_revenue = sum(customer_revenue.values())
            customer_count = len(customer_revenue)
            average_revenue_per_customer = total_revenue / customer_count
            
            # Calculate average customer lifespan
            lifespans = []
            for customer_id in customer_revenue:
                lifespan = (customer_last_purchase[customer_id] - customer_first_purchase[customer_id]).days
                lifespans.append(max(lifespan, 1))  # Minimum 1 day
                
            average_lifespan_days = statistics.mean(lifespans) if lifespans else 1
            
            # Calculate purchase frequency
            total_transactions = len(self.revenue_metrics)
            average_purchase_frequency = total_transactions / customer_count if customer_count > 0 else 0
            
            # Simple CLV calculation: Average Revenue Per Customer * Average Lifespan (in months)
            average_clv = average_revenue_per_customer * (average_lifespan_days / 30)
            
            # Calculate CLV distribution
            clv_values = [customer_revenue[c] for c in customer_revenue]
            clv_median = Decimal(str(statistics.median([float(v) for v in clv_values])))
            clv_percentile_75 = Decimal(str(statistics.quantiles([float(v) for v in clv_values], n=4)[2])) if len(clv_values) >= 4 else clv_median
            clv_percentile_25 = Decimal(str(statistics.quantiles([float(v) for v in clv_values], n=4)[0])) if len(clv_values) >= 4 else clv_median
            
            clv_data = {
                "average_clv": float(average_clv),
                "median_clv": float(clv_median),
                "clv_percentile_75": float(clv_percentile_75),
                "clv_percentile_25": float(clv_percentile_25),
                "average_revenue_per_customer": float(average_revenue_per_customer),
                "average_lifespan_days": average_lifespan_days,
                "average_purchase_frequency": average_purchase_frequency,
                "customer_count": customer_count,
                "total_revenue": float(total_revenue),
                "currency": currency,
                "calculated_at": datetime.now().isoformat()
            }
            
            self._cache_result(cache_key, clv_data)
            return clv_data
            
        except Exception as e:
            logger.error(f"Error calculating CLV: {str(e)}")
            return {"average_clv": 0, "currency": currency}
            
    async def calculate_churn_metrics(self) -> Dict[str, Any]:
        """Calculate churn rate and retention metrics"""
        try:
            cache_key = "churn_metrics"
            if self._is_cached(cache_key):
                return self.cached_metrics[cache_key]["data"]
                
            now = datetime.now()
            
            # Define cohorts for churn analysis
            cohort_months = []
            for i in range(12):  # Last 12 months
                month_start = (now - timedelta(days=30 * (i + 1))).replace(day=1)
                cohort_months.append(month_start)
                
            churn_data = {}
            
            for cohort_month in cohort_months:
                cohort_end = (cohort_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                # Get customers who started in this cohort
                cohort_customers = set()
                for metric in self.revenue_metrics:
                    if (metric.customer_id and 
                        cohort_month <= metric.timestamp <= cohort_end):
                        cohort_customers.add(metric.customer_id)
                        
                if not cohort_customers:
                    continue
                    
                # Track retention for subsequent months
                cohort_key = cohort_month.strftime("%Y-%m")
                churn_data[cohort_key] = {
                    "initial_customers": len(cohort_customers),
                    "retention_by_month": {}
                }
                
                for month_offset in range(1, 13):  # Track 12 months
                    check_month = cohort_month + timedelta(days=30 * month_offset)
                    if check_month > now:
                        break
                        
                    check_month_end = (check_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                    
                    # Count customers still active in this month
                    active_customers = set()
                    for metric in self.revenue_metrics:
                        if (metric.customer_id in cohort_customers and
                            check_month <= metric.timestamp <= check_month_end):
                            active_customers.add(metric.customer_id)
                            
                    retention_rate = len(active_customers) / len(cohort_customers) * 100
                    churn_data[cohort_key]["retention_by_month"][f"month_{month_offset}"] = {
                        "active_customers": len(active_customers),
                        "retention_rate": round(retention_rate, 2)
                    }
                    
            # Calculate overall churn metrics
            current_month = now.replace(day=1)
            last_month = (current_month - timedelta(days=1)).replace(day=1)
            
            current_customers = self._get_active_customers_in_period(current_month, now)
            last_month_customers = self._get_active_customers_in_period(last_month, current_month - timedelta(days=1))
            
            churned_customers = last_month_customers - current_customers
            monthly_churn_rate = (len(churned_customers) / len(last_month_customers) * 100) if last_month_customers else 0
            
            summary = {
                "monthly_churn_rate": round(monthly_churn_rate, 2),
                "current_active_customers": len(current_customers),
                "churned_this_month": len(churned_customers),
                "cohort_analysis": churn_data,
                "calculated_at": datetime.now().isoformat()
            }
            
            self._cache_result(cache_key, summary)
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating churn metrics: {str(e)}")
            return {"monthly_churn_rate": 0}
            
    async def get_revenue_forecast(
        self,
        months_ahead: int = 12,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """Generate revenue forecast using historical data"""
        try:
            cache_key = f"revenue_forecast_{months_ahead}_{currency}"
            if self._is_cached(cache_key):
                return self.cached_metrics[cache_key]["data"]
                
            # Get historical monthly revenue
            monthly_revenue = self._get_monthly_revenue_history(currency, 24)  # Last 24 months
            
            if len(monthly_revenue) < 3:
                return {"error": "Insufficient historical data for forecasting"}
                
            # Simple linear regression for trend
            revenue_values = [float(v) for v in monthly_revenue.values()]
            months = list(range(len(revenue_values)))
            
            # Calculate trend
            n = len(revenue_values)
            sum_x = sum(months)
            sum_y = sum(revenue_values)
            sum_xy = sum(x * y for x, y in zip(months, revenue_values))
            sum_x2 = sum(x * x for x in months)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Generate forecasts
            forecasts = []
            last_month_index = len(revenue_values) - 1
            
            for i in range(1, months_ahead + 1):
                future_month_index = last_month_index + i
                predicted_value = slope * future_month_index + intercept
                
                # Add some randomness for confidence interval
                std_dev = statistics.stdev(revenue_values) if len(revenue_values) > 1 else 0
                confidence_lower = max(0, predicted_value - 1.96 * std_dev)
                confidence_upper = predicted_value + 1.96 * std_dev
                
                future_date = datetime.now() + timedelta(days=30 * i)
                
                forecasts.append({
                    "month": future_date.strftime("%Y-%m"),
                    "predicted_revenue": round(predicted_value, 2),
                    "confidence_interval": {
                        "lower": round(confidence_lower, 2),
                        "upper": round(confidence_upper, 2)
                    },
                    "growth_rate": round((predicted_value / revenue_values[-1] - 1) * 100, 2) if revenue_values[-1] > 0 else 0
                })
                
            # Calculate overall forecast summary
            total_forecast = sum(f["predicted_revenue"] for f in forecasts)
            current_monthly_avg = statistics.mean(revenue_values[-3:]) if len(revenue_values) >= 3 else revenue_values[-1]
            projected_growth = ((total_forecast / months_ahead) / current_monthly_avg - 1) * 100 if current_monthly_avg > 0 else 0
            
            forecast_data = {
                "forecasts": forecasts,
                "summary": {
                    "total_forecast_period": round(total_forecast, 2),
                    "average_monthly_forecast": round(total_forecast / months_ahead, 2),
                    "projected_monthly_growth": round(projected_growth, 2),
                    "confidence_level": 95,
                    "forecast_months": months_ahead
                },
                "historical_trend": {
                    "slope": round(slope, 4),
                    "monthly_growth_rate": round(slope / current_monthly_avg * 100, 2) if current_monthly_avg > 0 else 0
                },
                "currency": currency,
                "generated_at": datetime.now().isoformat()
            }
            
            self._cache_result(cache_key, forecast_data)
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error generating revenue forecast: {str(e)}")
            return {"error": str(e)}
            
    async def get_regional_breakdown(self, currency: str = "EUR") -> Dict[str, Any]:
        """Get revenue breakdown by region"""
        try:
            cache_key = f"regional_breakdown_{currency}"
            if self._is_cached(cache_key):
                return self.cached_metrics[cache_key]["data"]
                
            # Group revenue by region
            regional_revenue = {}
            regional_customers = {}
            
            for metric in self.revenue_metrics:
                if metric.currency != currency:
                    continue
                    
                region = metric.region or "Unknown"
                
                if region not in regional_revenue:
                    regional_revenue[region] = Decimal('0')
                    regional_customers[region] = set()
                    
                regional_revenue[region] += metric.amount
                
                if metric.customer_id:
                    regional_customers[region].add(metric.customer_id)
                    
            total_revenue = sum(regional_revenue.values())
            
            # Calculate percentages and metrics
            regional_data = {}
            for region, revenue in regional_revenue.items():
                revenue_percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0
                customer_count = len(regional_customers[region])
                avg_revenue_per_customer = revenue / customer_count if customer_count > 0 else Decimal('0')
                
                regional_data[region] = {
                    "revenue": float(revenue),
                    "revenue_percentage": round(float(revenue_percentage), 2),
                    "customer_count": customer_count,
                    "average_revenue_per_customer": float(avg_revenue_per_customer)
                }
                
            # Sort by revenue
            sorted_regions = sorted(regional_data.items(), key=lambda x: x[1]["revenue"], reverse=True)
            
            breakdown = {
                "total_revenue": float(total_revenue),
                "regions": dict(sorted_regions),
                "top_region": sorted_regions[0][0] if sorted_regions else None,
                "region_count": len(regional_data),
                "currency": currency,
                "generated_at": datetime.now().isoformat()
            }
            
            self._cache_result(cache_key, breakdown)
            return breakdown
            
        except Exception as e:
            logger.error(f"Error getting regional breakdown: {str(e)}")
            return {}
            
    async def generate_financial_summary(self, currency: str = "EUR") -> Dict[str, Any]:
        """Generate comprehensive financial summary"""
        try:
            # Get all key metrics
            revenue_overview = await self.get_revenue_overview(MetricPeriod.MONTH, currency)
            mrr_breakdown = await self.calculate_mrr_breakdown(currency)
            clv_metrics = await self.get_customer_lifetime_value(currency)
            churn_metrics = await self.calculate_churn_metrics()
            regional_breakdown = await self.get_regional_breakdown(currency)
            
            # Calculate additional KPIs
            total_customers = len(set(m.customer_id for m in self.revenue_metrics if m.customer_id and m.currency == currency))
            total_transactions = len([m for m in self.revenue_metrics if m.currency == currency])
            
            # Revenue trends
            current_month_revenue = revenue_overview.get("total_revenue", 0)
            growth_rate = revenue_overview.get("growth_rate_percent", 0)
            
            summary = {
                "overview": {
                    "total_monthly_revenue": current_month_revenue,
                    "monthly_growth_rate": growth_rate,
                    "total_customers": total_customers,
                    "total_transactions": total_transactions,
                    "currency": currency
                },
                "mrr_metrics": mrr_breakdown,
                "customer_metrics": {
                    "lifetime_value": clv_metrics,
                    "churn_rate": churn_metrics.get("monthly_churn_rate", 0),
                    "active_customers": churn_metrics.get("current_active_customers", 0)
                },
                "geographic_distribution": regional_breakdown,
                "revenue_breakdown": revenue_overview.get("revenue_by_type", {}),
                "generated_at": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating financial summary: {str(e)}")
            return {}
            
    def _get_period_start(self, end_date: datetime, period: MetricPeriod) -> datetime:
        """Get start date for given period"""
        if period == MetricPeriod.HOUR:
            return end_date - timedelta(hours=1)
        elif period == MetricPeriod.DAY:
            return end_date - timedelta(days=1)
        elif period == MetricPeriod.WEEK:
            return end_date - timedelta(weeks=1)
        elif period == MetricPeriod.MONTH:
            return end_date - timedelta(days=30)
        elif period == MetricPeriod.QUARTER:
            return end_date - timedelta(days=90)
        elif period == MetricPeriod.YEAR:
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=30)
            
    def _classify_mrr_type(self, subscription_id: str, current_value: Decimal) -> str:
        """Classify MRR type for subscription"""
        # Simplified classification - in production, track subscription history
        return "new"  # Default to new for now
        
    def _get_active_customers_in_period(self, start_date: datetime, end_date: datetime) -> set:
        """Get active customers in given period"""
        customers = set()
        for metric in self.revenue_metrics:
            if (metric.customer_id and 
                start_date <= metric.timestamp <= end_date):
                customers.add(metric.customer_id)
        return customers
        
    def _get_monthly_revenue_history(self, currency: str, months: int) -> Dict[str, Decimal]:
        """Get monthly revenue history"""
        monthly_revenue = {}
        end_date = datetime.now()
        
        for i in range(months):
            month_start = (end_date - timedelta(days=30 * i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_key = month_start.strftime("%Y-%m")
            month_total = Decimal('0')
            
            for metric in self.revenue_metrics:
                if (metric.currency == currency and
                    month_start <= metric.timestamp <= month_end):
                    month_total += metric.amount
                    
            monthly_revenue[month_key] = month_total
            
        return dict(sorted(monthly_revenue.items()))
        
    def _is_cached(self, cache_key: str) -> bool:
        """Check if result is cached and still valid"""
        if cache_key not in self.cached_metrics:
            return False
            
        cache_time = self.cached_metrics[cache_key]["timestamp"]
        return datetime.now() - cache_time < self.cache_ttl
        
    def _cache_result(self, cache_key: str, data: Any):
        """Cache computation result"""
        self.cached_metrics[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
        
    def _invalidate_cache(self):
        """Invalidate all cached results"""
        self.cached_metrics.clear()


# Financial dashboard instance
financial_dashboard = FinancialDashboard()


async def track_revenue_event(
    amount: Decimal,
    currency: str,
    revenue_type: RevenueType,
    customer_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    region: Optional[str] = None,
    metadata: Optional[Dict] = None
):
    """Global function to track revenue events"""
    await financial_dashboard.track_revenue(
        amount=amount,
        currency=currency,
        revenue_type=revenue_type,
        customer_id=customer_id,
        subscription_id=subscription_id,
        region=region,
        metadata=metadata
    )


async def get_dashboard_data(currency: str = "EUR") -> Dict[str, Any]:
    """Get complete dashboard data"""
    return await financial_dashboard.generate_financial_summary(currency)