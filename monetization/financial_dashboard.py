"""Financial Dashboard Service
Real-time financial analytics and KPI monitoring system.

Author: Fahed Mlaiel <mlaiel@live.de>
⚠️ COPYRIGHT WARNING: Proprietary code - unauthorized use prohibited.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class TimeGranularity(Enum):
    """Time granularity for analytics."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class MetricType(Enum):
    """Financial metric types."""
    REVENUE = "revenue"
    PROFIT = "profit"
    GROWTH = "growth"
    CHURN = "churn"
    RETENTION = "retention"
    LTV = "ltv"
    CAC = "cac"
    ARPU = "arpu"
    MRR = "mrr"
    ARR = "arr"


@dataclass
class FinancialMetric:
    """Financial metric data point."""
    metric_type: MetricType
    value: Decimal
    currency: str
    timestamp: datetime
    granularity: TimeGranularity
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RevenueBreakdown:
    """Revenue breakdown by different dimensions."""
    total_revenue: Decimal
    subscription_revenue: Decimal
    one_time_revenue: Decimal
    refunds: Decimal
    net_revenue: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    breakdown_by_plan: Dict[str, Decimal] = None
    breakdown_by_region: Dict[str, Decimal] = None
    breakdown_by_platform: Dict[str, Decimal] = None

    def __post_init__(self):
        if self.breakdown_by_plan is None:
            self.breakdown_by_plan = {}
        if self.breakdown_by_region is None:
            self.breakdown_by_region = {}
        if self.breakdown_by_platform is None:
            self.breakdown_by_platform = {}


@dataclass
class CohortAnalysis:
    """Cohort analysis data."""
    cohort_month: str
    cohort_size: int
    retention_rates: Dict[int, float]  # month -> retention rate
    revenue_per_cohort: Dict[int, Decimal]  # month -> cumulative revenue
    ltv_estimate: Decimal


@dataclass
class ChurnAnalysis:
    """Churn analysis data."""
    period: str
    total_customers: int
    churned_customers: int
    churn_rate: float
    voluntary_churn: int
    involuntary_churn: int
    churn_reasons: Dict[str, int]
    revenue_impact: Decimal


class FinancialDashboard:
    """Real-time financial dashboard and analytics engine."""

    def __init__(self):
        """Initialize financial dashboard."""
        try:
            logger.info("Initializing FinancialDashboard")
            
            # Metrics storage (in production, use time-series database like InfluxDB)
            self.metrics: Dict[str, List[FinancialMetric]] = defaultdict(list)
            self.revenue_data: List[RevenueBreakdown] = []
            self.cohort_data: Dict[str, CohortAnalysis] = {}
            self.churn_data: List[ChurnAnalysis] = []
            
            # Dashboard configuration
            self.default_currency = "EUR"
            self.supported_currencies = [
                "EUR", "USD", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK"
            ]
            
            # Exchange rates (simplified - in production, use real-time rates)
            self.exchange_rates = {
                "USD": Decimal('0.85'),
                "GBP": Decimal('1.15'),
                "EUR": Decimal('1.00'),
                "CAD": Decimal('0.62'),
                "AUD": Decimal('0.55'),
                "JPY": Decimal('0.0063'),
                "CHF": Decimal('0.95'),
                "SEK": Decimal('0.084'),
                "NOK": Decimal('0.082'),
                "DKK": Decimal('0.134')
            }
            
            # Benchmarking data
            self.industry_benchmarks = {
                "saas_churn_rate": 5.0,      # Monthly churn rate %
                "saas_growth_rate": 20.0,    # Annual growth rate %
                "customer_ltv_months": 24,   # Average LTV in months
                "cac_payback_months": 12,    # CAC payback period
                "gross_margin": 80.0,        # Gross margin %
                "net_revenue_retention": 110.0  # Net revenue retention %
            }
            
            # Alerts configuration
            self.alert_thresholds = {
                "churn_rate_high": 7.0,      # Alert if churn > 7%
                "revenue_drop": -10.0,       # Alert if revenue drops > 10%
                "failed_payments": 15.0,     # Alert if failed payments > 15%
                "mrr_growth_low": 5.0,       # Alert if MRR growth < 5%
                "cac_increase": 50.0         # Alert if CAC increases > 50%
            }
            
            logger.info("FinancialDashboard initialized successfully")
            
        except Exception as e:
            logger.error(f"FinancialDashboard initialization failed: {e}")
            raise

    async def record_metric(
        self,
        metric_type: MetricType,
        value: Decimal,
        currency: str = "EUR",
        granularity: TimeGranularity = TimeGranularity.DAILY,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FinancialMetric:
        """Record a financial metric."""
        try:
            metric = FinancialMetric(
                metric_type=metric_type,
                value=value,
                currency=currency,
                timestamp=datetime.utcnow(),
                granularity=granularity,
                metadata=metadata or {}
            )
            
            metric_key = f"{metric_type.value}_{granularity.value}_{currency}"
            self.metrics[metric_key].append(metric)
            
            # Keep only last 1000 data points per metric
            if len(self.metrics[metric_key]) > 1000:
                self.metrics[metric_key] = self.metrics[metric_key][-1000:]
                
            logger.debug(f"Recorded metric: {metric_type.value} = {value} {currency}")
            return metric
            
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
            raise

    async def calculate_mrr(
        self,
        subscription_data: List[Dict[str, Any]],
        target_currency: str = "EUR"
    ) -> Decimal:
        """Calculate Monthly Recurring Revenue (MRR)."""
        try:
            total_mrr = Decimal('0.00')
            
            for subscription in subscription_data:
                if subscription.get('status') not in ['active', 'trialing']:
                    continue
                    
                plan_price = Decimal(str(subscription.get('plan_price', 0)))
                billing_cycle = subscription.get('billing_cycle', 'monthly')
                currency = subscription.get('currency', 'EUR')
                
                # Convert to monthly amount
                if billing_cycle == 'monthly':
                    monthly_amount = plan_price
                elif billing_cycle == 'quarterly':
                    monthly_amount = plan_price / Decimal('3')
                elif billing_cycle == 'annually':
                    monthly_amount = plan_price / Decimal('12')
                else:  # lifetime
                    monthly_amount = plan_price / Decimal('12')  # Amortize over 12 months
                    
                # Convert currency
                if currency != target_currency:
                    monthly_amount = await self._convert_currency(
                        monthly_amount, currency, target_currency
                    )
                    
                total_mrr += monthly_amount
                
            # Record metric
            await self.record_metric(
                MetricType.MRR,
                total_mrr,
                target_currency
            )
            
            logger.info(f"Calculated MRR: {total_mrr} {target_currency}")
            return total_mrr
            
        except Exception as e:
            logger.error(f"Error calculating MRR: {e}")
            return Decimal('0.00')

    async def calculate_arr(self, mrr: Decimal, currency: str = "EUR") -> Decimal:
        """Calculate Annual Recurring Revenue (ARR)."""
        try:
            arr = mrr * Decimal('12')
            
            await self.record_metric(
                MetricType.ARR,
                arr,
                currency
            )
            
            logger.info(f"Calculated ARR: {arr} {currency}")
            return arr
            
        except Exception as e:
            logger.error(f"Error calculating ARR: {e}")
            return Decimal('0.00')

    async def calculate_churn_rate(
        self,
        start_period_customers: int,
        churned_customers: int,
        granularity: TimeGranularity = TimeGranularity.MONTHLY
    ) -> float:
        """Calculate churn rate."""
        try:
            if start_period_customers == 0:
                return 0.0
                
            churn_rate = (churned_customers / start_period_customers) * 100
            
            await self.record_metric(
                MetricType.CHURN,
                Decimal(str(churn_rate)),
                "PERCENT",
                granularity
            )
            
            # Check alert threshold
            if churn_rate > self.alert_thresholds["churn_rate_high"]:
                await self._trigger_alert(
                    "High churn rate detected",
                    f"Churn rate of {churn_rate:.2f}% exceeds threshold of {self.alert_thresholds['churn_rate_high']}%"
                )
                
            logger.info(f"Calculated churn rate: {churn_rate:.2f}%")
            return churn_rate
            
        except Exception as e:
            logger.error(f"Error calculating churn rate: {e}")
            return 0.0

    async def calculate_ltv(
        self,
        average_monthly_revenue: Decimal,
        average_lifespan_months: float,
        currency: str = "EUR"
    ) -> Decimal:
        """Calculate Customer Lifetime Value (LTV)."""
        try:
            ltv = average_monthly_revenue * Decimal(str(average_lifespan_months))
            
            await self.record_metric(
                MetricType.LTV,
                ltv,
                currency
            )
            
            logger.info(f"Calculated LTV: {ltv} {currency}")
            return ltv
            
        except Exception as e:
            logger.error(f"Error calculating LTV: {e}")
            return Decimal('0.00')

    async def calculate_cac(
        self,
        marketing_spend: Decimal,
        new_customers_acquired: int,
        currency: str = "EUR"
    ) -> Decimal:
        """Calculate Customer Acquisition Cost (CAC)."""
        try:
            if new_customers_acquired == 0:
                return Decimal('0.00')
                
            cac = marketing_spend / Decimal(str(new_customers_acquired))
            
            await self.record_metric(
                MetricType.CAC,
                cac,
                currency
            )
            
            logger.info(f"Calculated CAC: {cac} {currency}")
            return cac
            
        except Exception as e:
            logger.error(f"Error calculating CAC: {e}")
            return Decimal('0.00')

    async def generate_revenue_breakdown(
        self,
        start_date: datetime,
        end_date: datetime,
        currency: str = "EUR"
    ) -> RevenueBreakdown:
        """Generate comprehensive revenue breakdown."""
        try:
            # This would integrate with billing and subscription systems
            # For now, we'll simulate data
            
            total_revenue = Decimal('125000.00')
            subscription_revenue = Decimal('110000.00')
            one_time_revenue = Decimal('15000.00')
            refunds = Decimal('2500.00')
            net_revenue = total_revenue - refunds
            
            breakdown = RevenueBreakdown(
                total_revenue=total_revenue,
                subscription_revenue=subscription_revenue,
                one_time_revenue=one_time_revenue,
                refunds=refunds,
                net_revenue=net_revenue,
                currency=currency,
                period_start=start_date,
                period_end=end_date,
                breakdown_by_plan={
                    "Free": Decimal('0.00'),
                    "Creator": Decimal('35000.00'),
                    "Pro": Decimal('65000.00'),
                    "Enterprise": Decimal('25000.00')
                },
                breakdown_by_region={
                    "Europe": Decimal('62500.00'),
                    "North America": Decimal('37500.00'),
                    "Asia Pacific": Decimal('15000.00'),
                    "Other": Decimal('10000.00')
                },
                breakdown_by_platform={
                    "Web": Decimal('85000.00'),
                    "Mobile": Decimal('35000.00'),
                    "API": Decimal('5000.00')
                }
            )
            
            self.revenue_data.append(breakdown)
            
            logger.info(f"Generated revenue breakdown for {start_date} to {end_date}")
            return breakdown
            
        except Exception as e:
            logger.error(f"Error generating revenue breakdown: {e}")
            raise

    async def perform_cohort_analysis(
        self,
        cohort_month: str,
        customer_data: List[Dict[str, Any]]
    ) -> CohortAnalysis:
        """Perform cohort analysis for customer retention and revenue."""
        try:
            # Filter customers for this cohort
            cohort_customers = [
                customer for customer in customer_data
                if customer.get('signup_month') == cohort_month
            ]
            
            cohort_size = len(cohort_customers)
            retention_rates = {}
            revenue_per_cohort = {}
            
            # Calculate retention and revenue for each month
            for month_offset in range(1, 13):  # 12 months
                active_customers = 0
                total_revenue = Decimal('0.00')
                
                for customer in cohort_customers:
                    customer_months = customer.get('active_months', 0)
                    if customer_months >= month_offset:
                        active_customers += 1
                        monthly_revenue = Decimal(str(customer.get('monthly_revenue', 0)))
                        total_revenue += monthly_revenue
                        
                retention_rate = (active_customers / cohort_size) * 100 if cohort_size > 0 else 0
                retention_rates[month_offset] = retention_rate
                revenue_per_cohort[month_offset] = total_revenue
                
            # Estimate LTV (simplified)
            ltv_estimate = sum(revenue_per_cohort.values())
            
            cohort_analysis = CohortAnalysis(
                cohort_month=cohort_month,
                cohort_size=cohort_size,
                retention_rates=retention_rates,
                revenue_per_cohort=revenue_per_cohort,
                ltv_estimate=ltv_estimate
            )
            
            self.cohort_data[cohort_month] = cohort_analysis
            
            logger.info(f"Performed cohort analysis for {cohort_month}")
            return cohort_analysis
            
        except Exception as e:
            logger.error(f"Error performing cohort analysis: {e}")
            raise

    async def get_real_time_kpis(self, currency: str = "EUR") -> Dict[str, Any]:
        """Get real-time financial KPIs."""
        try:
            now = datetime.utcnow()
            thirty_days_ago = now - timedelta(days=30)
            
            # Get latest metrics
            latest_metrics = {}
            for metric_type in MetricType:
                metric_key = f"{metric_type.value}_daily_{currency}"
                if metric_key in self.metrics and self.metrics[metric_key]:
                    latest_metrics[metric_type.value] = float(self.metrics[metric_key][-1].value)
                else:
                    latest_metrics[metric_type.value] = 0.0
                    
            # Calculate growth rates
            growth_rates = await self._calculate_growth_rates(currency)
            
            # Get payment success rate
            payment_success_rate = await self._get_payment_success_rate()
            
            kpis = {
                "timestamp": now.isoformat(),
                "currency": currency,
                "revenue": {
                    "mrr": latest_metrics.get("mrr", 0.0),
                    "arr": latest_metrics.get("arr", 0.0),
                    "growth_rate": growth_rates.get("revenue", 0.0)
                },
                "customers": {
                    "total_active": await self._get_active_customer_count(),
                    "churn_rate": latest_metrics.get("churn", 0.0),
                    "ltv": latest_metrics.get("ltv", 0.0),
                    "cac": latest_metrics.get("cac", 0.0)
                },
                "payments": {
                    "success_rate": payment_success_rate,
                    "failed_payments_24h": await self._get_failed_payments_count(24),
                    "average_transaction": await self._get_average_transaction_amount(currency)
                },
                "engagement": {
                    "arpu": latest_metrics.get("arpu", 0.0),
                    "retention_rate": await self._get_retention_rate(),
                    "upgrade_rate": await self._get_upgrade_rate()
                },
                "benchmarks": {
                    "vs_industry_churn": latest_metrics.get("churn", 0.0) - self.industry_benchmarks["saas_churn_rate"],
                    "vs_industry_growth": growth_rates.get("revenue", 0.0) - self.industry_benchmarks["saas_growth_rate"],
                    "cac_payback_months": await self._calculate_cac_payback_period()
                }
            }
            
            logger.info("Generated real-time KPIs")
            return kpis
            
        except Exception as e:
            logger.error(f"Error getting real-time KPIs: {e}")
            return {}

    async def generate_financial_forecast(
        self,
        months_ahead: int = 12,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """Generate financial forecast using historical data."""
        try:
            # Get historical MRR data
            mrr_key = f"mrr_monthly_{currency}"
            historical_mrr = []
            
            if mrr_key in self.metrics:
                historical_mrr = [float(m.value) for m in self.metrics[mrr_key][-12:]]
                
            if len(historical_mrr) < 3:
                # Not enough data for meaningful forecast
                return {"error": "Insufficient historical data for forecasting"}
                
            # Simple linear regression for trend
            n = len(historical_mrr)
            x_values = list(range(n))
            sum_x = sum(x_values)
            sum_y = sum(historical_mrr)
            sum_xy = sum(x * y for x, y in zip(x_values, historical_mrr))
            sum_x_squared = sum(x * x for x in x_values)
            
            # Calculate trend
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Generate forecast
            forecast = {}
            last_mrr = historical_mrr[-1]
            
            for month in range(1, months_ahead + 1):
                projected_mrr = last_mrr + (slope * month)
                projected_mrr = max(0, projected_mrr)  # Ensure non-negative
                
                month_date = (datetime.utcnow() + timedelta(days=30 * month)).strftime('%Y-%m')
                forecast[month_date] = {
                    "mrr": round(projected_mrr, 2),
                    "arr": round(projected_mrr * 12, 2),
                    "confidence": max(0.1, 0.9 - (month * 0.05))  # Decreasing confidence
                }
                
            logger.info(f"Generated financial forecast for {months_ahead} months")
            return {
                "currency": currency,
                "forecast_months": months_ahead,
                "historical_trend": slope,
                "projections": forecast
            }
            
        except Exception as e:
            logger.error(f"Error generating financial forecast: {e}")
            return {}

    async def _convert_currency(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str
    ) -> Decimal:
        """Convert amount between currencies."""
        try:
            if from_currency == to_currency:
                return amount
                
            # Convert to EUR first, then to target currency
            if from_currency != "EUR":
                eur_amount = amount * self.exchange_rates.get(from_currency, Decimal('1.0'))
            else:
                eur_amount = amount
                
            if to_currency != "EUR":
                final_amount = eur_amount / self.exchange_rates.get(to_currency, Decimal('1.0'))
            else:
                final_amount = eur_amount
                
            return final_amount
            
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            return amount

    async def _calculate_growth_rates(self, currency: str) -> Dict[str, float]:
        """Calculate growth rates for various metrics."""
        try:
            growth_rates = {}
            
            for metric_type in [MetricType.MRR, MetricType.REVENUE]:
                metric_key = f"{metric_type.value}_monthly_{currency}"
                
                if metric_key in self.metrics and len(self.metrics[metric_key]) >= 2:
                    current = float(self.metrics[metric_key][-1].value)
                    previous = float(self.metrics[metric_key][-2].value)
                    
                    if previous > 0:
                        growth_rate = ((current - previous) / previous) * 100
                        growth_rates[metric_type.value] = growth_rate
                    else:
                        growth_rates[metric_type.value] = 0.0
                else:
                    growth_rates[metric_type.value] = 0.0
                    
            return growth_rates
            
        except Exception as e:
            logger.error(f"Error calculating growth rates: {e}")
            return {}

    async def _get_payment_success_rate(self) -> float:
        """Get payment success rate."""
        try:
            # This would integrate with payment processing system
            # For now, return simulated data
            return 92.5
            
        except Exception as e:
            logger.error(f"Error getting payment success rate: {e}")
            return 0.0

    async def _get_active_customer_count(self) -> int:
        """Get current active customer count."""
        try:
            # This would integrate with subscription system
            # For now, return simulated data
            return 2485
            
        except Exception as e:
            logger.error(f"Error getting active customer count: {e}")
            return 0

    async def _get_failed_payments_count(self, hours: int) -> int:
        """Get failed payments count in last N hours."""
        try:
            # This would integrate with payment processing system
            # For now, return simulated data
            return 12
            
        except Exception as e:
            logger.error(f"Error getting failed payments count: {e}")
            return 0

    async def _get_average_transaction_amount(self, currency: str) -> float:
        """Get average transaction amount."""
        try:
            # This would integrate with payment processing system
            # For now, return simulated data
            return 85.50
            
        except Exception as e:
            logger.error(f"Error getting average transaction amount: {e}")
            return 0.0

    async def _get_retention_rate(self) -> float:
        """Get customer retention rate."""
        try:
            # This would integrate with customer data
            # For now, return simulated data
            return 88.5
            
        except Exception as e:
            logger.error(f"Error getting retention rate: {e}")
            return 0.0

    async def _get_upgrade_rate(self) -> float:
        """Get subscription upgrade rate."""
        try:
            # This would integrate with subscription system
            # For now, return simulated data
            return 15.2
            
        except Exception as e:
            logger.error(f"Error getting upgrade rate: {e}")
            return 0.0

    async def _calculate_cac_payback_period(self) -> float:
        """Calculate CAC payback period in months."""
        try:
            # This would use real CAC and ARPU data
            # For now, return simulated calculation
            return 8.5
            
        except Exception as e:
            logger.error(f"Error calculating CAC payback period: {e}")
            return 0.0

    async def _trigger_alert(self, title: str, message: str):
        """Trigger financial alert."""
        try:
            alert = {
                "timestamp": datetime.utcnow().isoformat(),
                "title": title,
                "message": message,
                "severity": "warning"
            }
            
            # In production, this would send notifications
            logger.warning(f"Financial Alert: {title} - {message}")
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")

    async def export_dashboard_data(
        self,
        start_date: datetime,
        end_date: datetime,
        format_type: str = "json"
    ) -> str:
        """Export dashboard data for external analysis."""
        try:
            dashboard_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "kpis": await self.get_real_time_kpis(),
                "revenue_breakdown": await self.generate_revenue_breakdown(
                    start_date, end_date
                ),
                "cohort_analysis": {
                    cohort: asdict(analysis) 
                    for cohort, analysis in self.cohort_data.items()
                },
                "metrics": {}
            }
            
            # Include relevant metrics
            for metric_key, metric_list in self.metrics.items():
                filtered_metrics = [
                    asdict(m) for m in metric_list
                    if start_date <= m.timestamp <= end_date
                ]
                if filtered_metrics:
                    dashboard_data["metrics"][metric_key] = filtered_metrics
                    
            if format_type == "json":
                import json
                file_path = f"/tmp/financial_dashboard_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
                
                # Convert Decimal objects to float for JSON serialization
                def decimal_handler(obj):
                    if isinstance(obj, Decimal):
                        return float(obj)
                    raise TypeError
                    
                with open(file_path, 'w') as f:
                    json.dump(dashboard_data, f, indent=2, default=decimal_handler)
                    
            else:  # CSV format
                import csv
                file_path = f"/tmp/financial_kpis_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Metric', 'Value', 'Currency', 'Timestamp'])
                    
                    kpis = dashboard_data["kpis"]
                    for category, metrics in kpis.items():
                        if isinstance(metrics, dict):
                            for metric_name, value in metrics.items():
                                writer.writerow([
                                    f"{category}_{metric_name}",
                                    value,
                                    kpis.get("currency", "EUR"),
                                    dashboard_data["export_timestamp"]
                                ])
                                
            logger.info(f"Exported dashboard data to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting dashboard data: {e}")
            raise