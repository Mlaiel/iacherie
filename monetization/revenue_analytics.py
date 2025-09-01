"""Real-Time Revenue Analytics with Predictions
Advanced analytics system for revenue tracking, forecasting, and business intelligence.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import json
import statistics
import math

logger = logging.getLogger(__name__)


class RevenueSource(Enum):
    """Revenue sources"""
    SUBSCRIPTIONS = "subscriptions"
    ONE_TIME_PURCHASES = "one_time_purchases"
    LICENSING = "licensing"
    ADVERTISING = "advertising"
    COMMISSIONS = "commissions"
    PARTNERSHIPS = "partnerships"
    SERVICES = "services"
    OTHER = "other"


class MetricType(Enum):
    """Types of revenue metrics"""
    MRR = "mrr"  # Monthly Recurring Revenue
    ARR = "arr"  # Annual Recurring Revenue
    CHURN_RATE = "churn_rate"
    LTV = "ltv"  # Customer Lifetime Value
    CAC = "cac"  # Customer Acquisition Cost
    ARPU = "arpu"  # Average Revenue Per User
    CONVERSION_RATE = "conversion_rate"
    GROWTH_RATE = "growth_rate"


class PredictionModel(Enum):
    """Prediction model types"""
    LINEAR_REGRESSION = "linear_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"
    MACHINE_LEARNING = "machine_learning"


@dataclass
class RevenueDataPoint:
    """Individual revenue data point"""
    id: str
    timestamp: datetime
    source: RevenueSource
    amount: Decimal
    currency: str
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None
    plan_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MetricCalculation:
    """Calculated metric result"""
    metric_type: MetricType
    value: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    calculation_time: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RevenuePrediction:
    """Revenue prediction result"""
    metric_type: MetricType
    predicted_value: Decimal
    confidence_interval: Tuple[Decimal, Decimal]
    prediction_date: datetime
    prediction_horizon_days: int
    model_used: PredictionModel
    accuracy_score: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RevenueInsight:
    """Business insight from revenue analysis"""
    id: str
    title: str
    description: str
    impact_level: str  # "high", "medium", "low"
    recommendation: str
    supporting_data: Dict[str, Any]
    created_at: datetime


class RevenueAnalyticsEngine:
    """Real-time revenue analytics and prediction system"""
    
    def __init__(self):
        self.revenue_data: List[RevenueDataPoint] = []
        self.metric_cache: Dict[str, MetricCalculation] = {}
        self.predictions: Dict[str, RevenuePrediction] = {}
        self.insights: Dict[str, RevenueInsight] = {}
        self.customer_data: Dict[str, Dict[str, Any]] = {}
        self.subscription_data: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl_minutes = 5  # Cache TTL for real-time metrics
    
    async def record_revenue(
        self,
        source: RevenueSource,
        amount: Decimal,
        currency: str,
        customer_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record a revenue data point"""
        try:
            revenue_id = str(uuid.uuid4())
            
            data_point = RevenueDataPoint(
                id=revenue_id,
                timestamp=datetime.now(),
                source=source,
                amount=amount,
                currency=currency,
                customer_id=customer_id,
                subscription_id=subscription_id,
                plan_id=plan_id,
                metadata=metadata
            )
            
            self.revenue_data.append(data_point)
            
            # Invalidate relevant cache entries
            await self._invalidate_cache()
            
            # Generate real-time insights
            await self._generate_real_time_insights(data_point)
            
            logger.info(f"Revenue recorded: {revenue_id} - {amount} {currency}")
            return {
                "success": True,
                "revenue_id": revenue_id,
                "timestamp": data_point.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recording revenue: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def calculate_mrr(
        self,
        date: Optional[datetime] = None,
        force_refresh: bool = False
    ) -> MetricCalculation:
        """Calculate Monthly Recurring Revenue (MRR)"""
        try:
            cache_key = f"mrr_{date.strftime('%Y-%m') if date else 'current'}"
            
            if not force_refresh and cache_key in self.metric_cache:
                cached_metric = self.metric_cache[cache_key]
                # Check if cache is still valid
                if (datetime.now() - cached_metric.calculation_time).total_seconds() < (self.cache_ttl_minutes * 60):
                    return cached_metric
            
            target_date = date or datetime.now()
            month_start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            # Get subscription revenue for the month
            subscription_revenue = Decimal("0.00")
            
            for data_point in self.revenue_data:
                if (data_point.source == RevenueSource.SUBSCRIPTIONS and
                    month_start <= data_point.timestamp <= month_end):
                    subscription_revenue += data_point.amount
            
            # Calculate active subscriptions and their recurring amounts
            active_subscriptions = await self._get_active_subscriptions(target_date)
            
            mrr = Decimal("0.00")
            for sub_id, sub_data in active_subscriptions.items():
                # Convert to monthly amount based on billing cycle
                monthly_amount = await self._convert_to_monthly_amount(
                    sub_data["amount"], sub_data["billing_cycle"]
                )
                mrr += monthly_amount
            
            metric = MetricCalculation(
                metric_type=MetricType.MRR,
                value=mrr,
                currency="EUR",  # Default currency
                period_start=month_start,
                period_end=month_end,
                calculation_time=datetime.now(),
                metadata={
                    "active_subscriptions": len(active_subscriptions),
                    "subscription_revenue": float(subscription_revenue)
                }
            )
            
            self.metric_cache[cache_key] = metric
            return metric
            
        except Exception as e:
            logger.error(f"Error calculating MRR: {str(e)}")
            return MetricCalculation(
                metric_type=MetricType.MRR,
                value=Decimal("0.00"),
                currency="EUR",
                period_start=datetime.now(),
                period_end=datetime.now(),
                calculation_time=datetime.now(),
                metadata={"error": str(e)}
            )
    
    async def calculate_arr(
        self,
        date: Optional[datetime] = None,
        force_refresh: bool = False
    ) -> MetricCalculation:
        """Calculate Annual Recurring Revenue (ARR)"""
        try:
            mrr_metric = await self.calculate_mrr(date, force_refresh)
            arr_value = mrr_metric.value * 12
            
            target_date = date or datetime.now()
            year_start = target_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            year_end = year_start.replace(year=year_start.year + 1) - timedelta(seconds=1)
            
            return MetricCalculation(
                metric_type=MetricType.ARR,
                value=arr_value,
                currency=mrr_metric.currency,
                period_start=year_start,
                period_end=year_end,
                calculation_time=datetime.now(),
                metadata={
                    "based_on_mrr": float(mrr_metric.value),
                    "mrr_metadata": mrr_metric.metadata
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating ARR: {str(e)}")
            return MetricCalculation(
                metric_type=MetricType.ARR,
                value=Decimal("0.00"),
                currency="EUR",
                period_start=datetime.now(),
                period_end=datetime.now(),
                calculation_time=datetime.now(),
                metadata={"error": str(e)}
            )
    
    async def calculate_churn_rate(
        self,
        period_days: int = 30,
        date: Optional[datetime] = None
    ) -> MetricCalculation:
        """Calculate customer churn rate"""
        try:
            target_date = date or datetime.now()
            period_start = target_date - timedelta(days=period_days)
            
            # Get customers at start of period
            start_customers = await self._get_active_customers(period_start)
            
            # Get customers who churned during period
            churned_customers = await self._get_churned_customers(period_start, target_date)
            
            churn_rate = Decimal("0.00")
            if len(start_customers) > 0:
                churn_rate = Decimal(len(churned_customers)) / Decimal(len(start_customers)) * 100
            
            return MetricCalculation(
                metric_type=MetricType.CHURN_RATE,
                value=churn_rate,
                currency="%",
                period_start=period_start,
                period_end=target_date,
                calculation_time=datetime.now(),
                metadata={
                    "start_customers": len(start_customers),
                    "churned_customers": len(churned_customers),
                    "period_days": period_days
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating churn rate: {str(e)}")
            return MetricCalculation(
                metric_type=MetricType.CHURN_RATE,
                value=Decimal("0.00"),
                currency="%",
                period_start=datetime.now(),
                period_end=datetime.now(),
                calculation_time=datetime.now(),
                metadata={"error": str(e)}
            )
    
    async def calculate_ltv(
        self,
        customer_segment: Optional[str] = None,
        date: Optional[datetime] = None
    ) -> MetricCalculation:
        """Calculate Customer Lifetime Value (LTV)"""
        try:
            target_date = date or datetime.now()
            
            # Get ARPU (Average Revenue Per User)
            arpu_metric = await self.calculate_arpu(date=target_date)
            arpu = arpu_metric.value
            
            # Get churn rate
            churn_metric = await self.calculate_churn_rate(date=target_date)
            monthly_churn_rate = churn_metric.value / 100  # Convert percentage to decimal
            
            # Calculate average customer lifespan
            if monthly_churn_rate > 0:
                avg_lifespan_months = Decimal("1") / monthly_churn_rate
            else:
                avg_lifespan_months = Decimal("60")  # Default to 5 years if no churn
            
            # LTV = ARPU * Average Lifespan
            ltv = arpu * avg_lifespan_months
            
            return MetricCalculation(
                metric_type=MetricType.LTV,
                value=ltv,
                currency="EUR",
                period_start=target_date - timedelta(days=365),
                period_end=target_date,
                calculation_time=datetime.now(),
                metadata={
                    "arpu": float(arpu),
                    "monthly_churn_rate": float(monthly_churn_rate),
                    "avg_lifespan_months": float(avg_lifespan_months),
                    "customer_segment": customer_segment
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating LTV: {str(e)}")
            return MetricCalculation(
                metric_type=MetricType.LTV,
                value=Decimal("0.00"),
                currency="EUR",
                period_start=datetime.now(),
                period_end=datetime.now(),
                calculation_time=datetime.now(),
                metadata={"error": str(e)}
            )
    
    async def calculate_arpu(
        self,
        period_days: int = 30,
        date: Optional[datetime] = None
    ) -> MetricCalculation:
        """Calculate Average Revenue Per User (ARPU)"""
        try:
            target_date = date or datetime.now()
            period_start = target_date - timedelta(days=period_days)
            
            # Get total revenue for period
            total_revenue = Decimal("0.00")
            unique_customers = set()
            
            for data_point in self.revenue_data:
                if period_start <= data_point.timestamp <= target_date:
                    total_revenue += data_point.amount
                    if data_point.customer_id:
                        unique_customers.add(data_point.customer_id)
            
            arpu = Decimal("0.00")
            if len(unique_customers) > 0:
                arpu = total_revenue / Decimal(len(unique_customers))
            
            return MetricCalculation(
                metric_type=MetricType.ARPU,
                value=arpu,
                currency="EUR",
                period_start=period_start,
                period_end=target_date,
                calculation_time=datetime.now(),
                metadata={
                    "total_revenue": float(total_revenue),
                    "unique_customers": len(unique_customers),
                    "period_days": period_days
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating ARPU: {str(e)}")
            return MetricCalculation(
                metric_type=MetricType.ARPU,
                value=Decimal("0.00"),
                currency="EUR",
                period_start=datetime.now(),
                period_end=datetime.now(),
                calculation_time=datetime.now(),
                metadata={"error": str(e)}
            )
    
    async def predict_revenue(
        self,
        metric_type: MetricType,
        prediction_horizon_days: int = 30,
        model: PredictionModel = PredictionModel.LINEAR_REGRESSION
    ) -> RevenuePrediction:
        """Predict future revenue metrics"""
        try:
            # Get historical data for the metric
            historical_data = await self._get_historical_metric_data(metric_type, days=90)
            
            if len(historical_data) < 7:  # Need at least a week of data
                return RevenuePrediction(
                    metric_type=metric_type,
                    predicted_value=Decimal("0.00"),
                    confidence_interval=(Decimal("0.00"), Decimal("0.00")),
                    prediction_date=datetime.now() + timedelta(days=prediction_horizon_days),
                    prediction_horizon_days=prediction_horizon_days,
                    model_used=model,
                    accuracy_score=0.0,
                    metadata={"error": "Insufficient historical data"}
                )
            
            # Apply prediction model
            if model == PredictionModel.LINEAR_REGRESSION:
                prediction_result = await self._linear_regression_prediction(
                    historical_data, prediction_horizon_days
                )
            elif model == PredictionModel.EXPONENTIAL_SMOOTHING:
                prediction_result = await self._exponential_smoothing_prediction(
                    historical_data, prediction_horizon_days
                )
            else:
                # Default to linear regression
                prediction_result = await self._linear_regression_prediction(
                    historical_data, prediction_horizon_days
                )
            
            prediction = RevenuePrediction(
                metric_type=metric_type,
                predicted_value=prediction_result["predicted_value"],
                confidence_interval=prediction_result["confidence_interval"],
                prediction_date=datetime.now() + timedelta(days=prediction_horizon_days),
                prediction_horizon_days=prediction_horizon_days,
                model_used=model,
                accuracy_score=prediction_result["accuracy_score"],
                metadata=prediction_result.get("metadata", {})
            )
            
            # Cache the prediction
            prediction_key = f"{metric_type.value}_{prediction_horizon_days}_{model.value}"
            self.predictions[prediction_key] = prediction
            
            logger.info(f"Revenue prediction generated: {metric_type.value} - {prediction_result['predicted_value']}")
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting revenue: {str(e)}")
            return RevenuePrediction(
                metric_type=metric_type,
                predicted_value=Decimal("0.00"),
                confidence_interval=(Decimal("0.00"), Decimal("0.00")),
                prediction_date=datetime.now() + timedelta(days=prediction_horizon_days),
                prediction_horizon_days=prediction_horizon_days,
                model_used=model,
                accuracy_score=0.0,
                metadata={"error": str(e)}
            )
    
    async def generate_revenue_dashboard(
        self,
        date_range_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive revenue dashboard data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range_days)
            
            # Calculate key metrics
            mrr = await self.calculate_mrr()
            arr = await self.calculate_arr()
            churn_rate = await self.calculate_churn_rate()
            ltv = await self.calculate_ltv()
            arpu = await self.calculate_arpu()
            
            # Get revenue trends
            revenue_trends = await self._get_revenue_trends(start_date, end_date)
            
            # Get predictions
            mrr_prediction = await self.predict_revenue(MetricType.MRR, 30)
            churn_prediction = await self.predict_revenue(MetricType.CHURN_RATE, 30)
            
            # Get insights
            recent_insights = list(self.insights.values())[-5:]  # Last 5 insights
            
            # Calculate growth rates
            growth_rates = await self._calculate_growth_rates()
            
            dashboard_data = {
                "summary": {
                    "mrr": {
                        "value": float(mrr.value),
                        "currency": mrr.currency,
                        "growth_rate": growth_rates.get("mrr_growth", 0.0)
                    },
                    "arr": {
                        "value": float(arr.value),
                        "currency": arr.currency,
                        "growth_rate": growth_rates.get("arr_growth", 0.0)
                    },
                    "churn_rate": {
                        "value": float(churn_rate.value),
                        "unit": "%",
                        "trend": "decreasing" if growth_rates.get("churn_growth", 0) < 0 else "increasing"
                    },
                    "ltv": {
                        "value": float(ltv.value),
                        "currency": ltv.currency
                    },
                    "arpu": {
                        "value": float(arpu.value),
                        "currency": arpu.currency
                    }
                },
                "trends": revenue_trends,
                "predictions": {
                    "mrr_next_month": {
                        "value": float(mrr_prediction.predicted_value),
                        "confidence_interval": [
                            float(mrr_prediction.confidence_interval[0]),
                            float(mrr_prediction.confidence_interval[1])
                        ],
                        "accuracy_score": mrr_prediction.accuracy_score
                    },
                    "churn_next_month": {
                        "value": float(churn_prediction.predicted_value),
                        "confidence_interval": [
                            float(churn_prediction.confidence_interval[0]),
                            float(churn_prediction.confidence_interval[1])
                        ],
                        "accuracy_score": churn_prediction.accuracy_score
                    }
                },
                "insights": [asdict(insight) for insight in recent_insights],
                "generated_at": datetime.now().isoformat()
            }
            
            return {"success": True, "dashboard": dashboard_data}
            
        except Exception as e:
            logger.error(f"Error generating revenue dashboard: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _get_active_subscriptions(self, date: datetime) -> Dict[str, Dict[str, Any]]:
        """Get active subscriptions at a specific date"""
        # In a real implementation, this would query the subscription database
        # For now, simulate with sample data
        return {
            "sub_1": {"amount": Decimal("29.99"), "billing_cycle": "monthly"},
            "sub_2": {"amount": Decimal("99.99"), "billing_cycle": "monthly"},
            "sub_3": {"amount": Decimal("299.99"), "billing_cycle": "annual"}
        }
    
    async def _convert_to_monthly_amount(self, amount: Decimal, billing_cycle: str) -> Decimal:
        """Convert billing amount to monthly equivalent"""
        if billing_cycle == "monthly":
            return amount
        elif billing_cycle == "annual":
            return amount / 12
        elif billing_cycle == "quarterly":
            return amount / 3
        else:
            return amount  # Default to monthly
    
    async def _get_active_customers(self, date: datetime) -> List[str]:
        """Get active customers at a specific date"""
        # Simulate customer data
        return [f"customer_{i}" for i in range(100)]  # 100 active customers
    
    async def _get_churned_customers(self, start_date: datetime, end_date: datetime) -> List[str]:
        """Get customers who churned in the period"""
        # Simulate churn data
        return [f"customer_{i}" for i in range(5)]  # 5 churned customers
    
    async def _get_historical_metric_data(self, metric_type: MetricType, days: int) -> List[Tuple[datetime, Decimal]]:
        """Get historical data for a metric"""
        data = []
        end_date = datetime.now()
        
        for i in range(days):
            date = end_date - timedelta(days=i)
            # Simulate historical data with some growth trend
            base_value = 1000 + (i * 10)  # Growing trend
            noise = (hash(str(date)) % 100 - 50) / 10  # Add some noise
            value = Decimal(str(base_value + noise))
            data.append((date, value))
        
        return list(reversed(data))  # Return in chronological order
    
    async def _linear_regression_prediction(
        self,
        historical_data: List[Tuple[datetime, Decimal]],
        horizon_days: int
    ) -> Dict[str, Any]:
        """Simple linear regression prediction"""
        try:
            if len(historical_data) < 2:
                return {
                    "predicted_value": Decimal("0.00"),
                    "confidence_interval": (Decimal("0.00"), Decimal("0.00")),
                    "accuracy_score": 0.0
                }
            
            # Convert to numeric format for calculation
            x_values = list(range(len(historical_data)))
            y_values = [float(value) for _, value in historical_data]
            
            # Calculate linear regression coefficients
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            
            # Calculate slope (m) and intercept (b)
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator == 0:
                slope = 0
                intercept = sum_y / n
            else:
                slope = (n * sum_xy - sum_x * sum_y) / denominator
                intercept = (sum_y - slope * sum_x) / n
            
            # Predict value
            future_x = len(historical_data) + horizon_days - 1
            predicted_value = Decimal(str(slope * future_x + intercept))
            
            # Calculate confidence interval (simplified)
            if len(y_values) > 1:
                std_dev = statistics.stdev(y_values)
                margin_of_error = Decimal(str(1.96 * std_dev))  # 95% confidence interval
                confidence_interval = (
                    predicted_value - margin_of_error,
                    predicted_value + margin_of_error
                )
            else:
                confidence_interval = (predicted_value, predicted_value)
            
            # Calculate R-squared for accuracy
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in y_values)
            ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(x_values, y_values))
            
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return {
                "predicted_value": max(predicted_value, Decimal("0.00")),  # Ensure non-negative
                "confidence_interval": confidence_interval,
                "accuracy_score": max(0.0, min(1.0, r_squared)),
                "metadata": {
                    "slope": slope,
                    "intercept": intercept,
                    "r_squared": r_squared
                }
            }
            
        except Exception as e:
            logger.error(f"Error in linear regression prediction: {str(e)}")
            return {
                "predicted_value": Decimal("0.00"),
                "confidence_interval": (Decimal("0.00"), Decimal("0.00")),
                "accuracy_score": 0.0,
                "metadata": {"error": str(e)}
            }
    
    async def _exponential_smoothing_prediction(
        self,
        historical_data: List[Tuple[datetime, Decimal]],
        horizon_days: int
    ) -> Dict[str, Any]:
        """Exponential smoothing prediction"""
        try:
            if len(historical_data) < 3:
                return await self._linear_regression_prediction(historical_data, horizon_days)
            
            values = [float(value) for _, value in historical_data]
            alpha = 0.3  # Smoothing parameter
            
            # Initialize
            smoothed_values = [values[0]]
            
            # Calculate smoothed values
            for i in range(1, len(values)):
                smoothed = alpha * values[i] + (1 - alpha) * smoothed_values[i-1]
                smoothed_values.append(smoothed)
            
            # Predict future value
            predicted_value = Decimal(str(smoothed_values[-1]))
            
            # Calculate error for confidence interval
            errors = [abs(values[i] - smoothed_values[i]) for i in range(len(values))]
            avg_error = sum(errors) / len(errors)
            margin_of_error = Decimal(str(1.96 * avg_error))
            
            confidence_interval = (
                predicted_value - margin_of_error,
                predicted_value + margin_of_error
            )
            
            # Calculate accuracy (simplified)
            mape = sum(abs((values[i] - smoothed_values[i]) / values[i]) for i in range(len(values)) if values[i] != 0)
            mape /= len(values)
            accuracy_score = max(0.0, 1.0 - mape)
            
            return {
                "predicted_value": max(predicted_value, Decimal("0.00")),
                "confidence_interval": confidence_interval,
                "accuracy_score": max(0.0, min(1.0, accuracy_score)),
                "metadata": {
                    "alpha": alpha,
                    "avg_error": avg_error,
                    "mape": mape
                }
            }
            
        except Exception as e:
            logger.error(f"Error in exponential smoothing prediction: {str(e)}")
            return await self._linear_regression_prediction(historical_data, horizon_days)
    
    async def _get_revenue_trends(self, start_date: datetime, end_date: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """Get revenue trends over time"""
        trends = {
            "daily_revenue": [],
            "weekly_revenue": [],
            "monthly_revenue": []
        }
        
        # Daily revenue
        current_date = start_date
        while current_date <= end_date:
            daily_total = sum(
                data_point.amount for data_point in self.revenue_data
                if data_point.timestamp.date() == current_date.date()
            )
            
            trends["daily_revenue"].append({
                "date": current_date.strftime("%Y-%m-%d"),
                "value": float(daily_total)
            })
            
            current_date += timedelta(days=1)
        
        return trends
    
    async def _calculate_growth_rates(self) -> Dict[str, float]:
        """Calculate growth rates for key metrics"""
        try:
            # Get current and previous month MRR
            current_mrr = await self.calculate_mrr()
            last_month_mrr = await self.calculate_mrr(datetime.now() - timedelta(days=30))
            
            mrr_growth = 0.0
            if last_month_mrr.value > 0:
                mrr_growth = float((current_mrr.value - last_month_mrr.value) / last_month_mrr.value * 100)
            
            # Calculate ARR growth
            arr_growth = mrr_growth  # ARR growth follows MRR growth
            
            # Get churn rate growth
            current_churn = await self.calculate_churn_rate()
            last_month_churn = await self.calculate_churn_rate(date=datetime.now() - timedelta(days=30))
            
            churn_growth = 0.0
            if last_month_churn.value > 0:
                churn_growth = float((current_churn.value - last_month_churn.value) / last_month_churn.value * 100)
            
            return {
                "mrr_growth": mrr_growth,
                "arr_growth": arr_growth,
                "churn_growth": churn_growth
            }
            
        except Exception as e:
            logger.error(f"Error calculating growth rates: {str(e)}")
            return {"mrr_growth": 0.0, "arr_growth": 0.0, "churn_growth": 0.0}
    
    async def _generate_real_time_insights(self, data_point: RevenueDataPoint):
        """Generate real-time insights from new revenue data"""
        try:
            # Check for significant revenue spike
            recent_revenue = sum(
                dp.amount for dp in self.revenue_data[-10:]  # Last 10 transactions
                if dp.timestamp >= datetime.now() - timedelta(hours=1)
            )
            
            if recent_revenue > Decimal("1000.00"):  # Significant revenue threshold
                insight_id = str(uuid.uuid4())
                insight = RevenueInsight(
                    id=insight_id,
                    title="Significant Revenue Spike Detected",
                    description=f"Revenue spike of {recent_revenue} detected in the last hour",
                    impact_level="high",
                    recommendation="Monitor for sustained growth and consider scaling resources",
                    supporting_data={
                        "recent_revenue": float(recent_revenue),
                        "time_window": "1 hour",
                        "threshold": 1000.00
                    },
                    created_at=datetime.now()
                )
                self.insights[insight_id] = insight
            
            # Check for new customer revenue patterns
            if data_point.customer_id:
                customer_revenue = sum(
                    dp.amount for dp in self.revenue_data
                    if dp.customer_id == data_point.customer_id
                )
                
                if customer_revenue > Decimal("500.00"):  # High-value customer
                    insight_id = str(uuid.uuid4())
                    insight = RevenueInsight(
                        id=insight_id,
                        title="High-Value Customer Identified",
                        description=f"Customer {data_point.customer_id} has generated {customer_revenue} in total revenue",
                        impact_level="medium",
                        recommendation="Consider VIP treatment and retention programs",
                        supporting_data={
                            "customer_id": data_point.customer_id,
                            "total_revenue": float(customer_revenue),
                            "threshold": 500.00
                        },
                        created_at=datetime.now()
                    )
                    self.insights[insight_id] = insight
                    
        except Exception as e:
            logger.error(f"Error generating real-time insights: {str(e)}")
    
    async def _invalidate_cache(self):
        """Invalidate relevant cache entries"""
        # Remove old cache entries
        current_time = datetime.now()
        keys_to_remove = []
        
        for key, metric in self.metric_cache.items():
            if (current_time - metric.calculation_time).total_seconds() > (self.cache_ttl_minutes * 60):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.metric_cache[key]
    
    async def get_revenue_analytics_summary(self) -> Dict[str, Any]:
        """Get summary of revenue analytics system"""
        try:
            total_revenue = sum(dp.amount for dp in self.revenue_data)
            unique_customers = len(set(dp.customer_id for dp in self.revenue_data if dp.customer_id))
            
            revenue_by_source = {}
            for source in RevenueSource:
                source_revenue = sum(
                    dp.amount for dp in self.revenue_data 
                    if dp.source == source
                )
                revenue_by_source[source.value] = float(source_revenue)
            
            return {
                "success": True,
                "summary": {
                    "total_revenue_points": len(self.revenue_data),
                    "total_revenue": float(total_revenue),
                    "unique_customers": unique_customers,
                    "revenue_by_source": revenue_by_source,
                    "cached_metrics": len(self.metric_cache),
                    "predictions": len(self.predictions),
                    "insights": len(self.insights),
                    "data_range": {
                        "earliest": self.revenue_data[0].timestamp.isoformat() if self.revenue_data else None,
                        "latest": self.revenue_data[-1].timestamp.isoformat() if self.revenue_data else None
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue analytics summary: {str(e)}")
            return {"success": False, "error": str(e)}