"""Payment Analytics Module
Advanced analytics and reporting for payment data in IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 - All rights reserved
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging
from collections import defaultdict
import asyncio

from ..models.payment_models import PaymentTransaction, PaymentStatus, PaymentProvider

logger = logging.getLogger(__name__)


class AnalyticsTimeframe(Enum):
    """
Analytics timeframe options"""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class MetricType(Enum):
    """Types of payment metrics"""

    REVENUE = "revenue"
    TRANSACTION_COUNT = "transaction_count"
    SUCCESS_RATE = "success_rate"
    AVERAGE_TRANSACTION = "average_transaction"
    REFUND_RATE = "refund_rate"
    CHARGEBACK_RATE = "chargeback_rate"
    CONVERSION_RATE = "conversion_rate"
    CUSTOMER_LIFETIME_VALUE = "customer_lifetime_value"


@dataclass
class PaymentMetric:
    """Payment metric data structure"""
    name: str
    value: float
    unit: str
    timeframe: AnalyticsTimeframe
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class RevenueBreakdown:
    """
Revenue breakdown structure"""
    total_revenue: Decimal
    gross_revenue: Decimal
    net_revenue: Decimal
    fees: Decimal
    refunds: Decimal
    chargebacks: Decimal
    currency: str
    timeframe: AnalyticsTimeframe


@dataclass
class TransactionAnalytics:
    """
Transaction analytics structure"""
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    pending_transactions: int
    success_rate: float
    failure_rate: float
    average_amount: Decimal
    median_amount: Decimal


class PaymentAnalyticsEngine:
    """
Core analytics engine for payment data"""
    
    def __init__(self):
        self.cache_duration = timedelta(minutes=15)
        self.metrics_cache = {}
        self.last_cache_update = {}
    
    async def calculate_revenue_metrics(
        self,
        transactions: List[PaymentTransaction],
        timeframe: AnalyticsTimeframe,
        currency: str = 'USD'
    ) -> RevenueBreakdown:
        """
Calculate comprehensive revenue metrics"""
        
        # Filter transactions by currency and successful status
        currency_transactions = [
            t for t in transactions 
            if t.currency == currency and t.status == PaymentStatus.COMPLETED
        ]
        
        # Calculate base metrics
        total_revenue = sum(t.amount for t in currency_transactions)
        
        # Calculate fees (approximate - would come from actual provider data)
        estimated_fees = sum(
            self._estimate_transaction_fee(t.amount, t.provider) 
            for t in currency_transactions
        )
        
        # Calculate refunds
        refunded_transactions = [
            t for t in transactions 
            if t.status == PaymentStatus.REFUNDED and t.currency == currency
        ]
        total_refunds = sum(t.amount for t in refunded_transactions)
        
        # Calculate chargebacks
        chargeback_transactions = [
            t for t in transactions 
            if t.status == PaymentStatus.DISPUTED and t.currency == currency
        ]
        total_chargebacks = sum(t.amount for t in chargeback_transactions)
        
        # Calculate net revenue
        net_revenue = total_revenue - estimated_fees - total_refunds - total_chargebacks
        
        return RevenueBreakdown(
            total_revenue=total_revenue,
            gross_revenue=total_revenue,
            net_revenue=net_revenue,
            fees=estimated_fees,
            refunds=total_refunds,
            chargebacks=total_chargebacks,
            currency=currency,
            timeframe=timeframe
        )
    
    async def calculate_transaction_analytics(
        self,
        transactions: List[PaymentTransaction],
        timeframe: AnalyticsTimeframe
    ) -> TransactionAnalytics:
        """
Calculate transaction analytics"""
        
        total_count = len(transactions)
        
        if total_count == 0:
            return TransactionAnalytics(
                total_transactions=0,
                successful_transactions=0,
                failed_transactions=0,
                pending_transactions=0,
                success_rate=0.0,
                failure_rate=0.0,
                average_amount=Decimal('0'),
                median_amount=Decimal('0')
            )
        
        # Count by status
        successful = len([t for t in transactions if t.status == PaymentStatus.COMPLETED])
        failed = len([t for t in transactions if t.status == PaymentStatus.FAILED])
        pending = len([t for t in transactions if t.status == PaymentStatus.PENDING])
        
        # Calculate rates
        success_rate = (successful / total_count) * 100
        failure_rate = (failed / total_count) * 100
        
        # Calculate amount statistics
        amounts = [float(t.amount) for t in transactions if t.status == PaymentStatus.COMPLETED]
        
        if amounts:
            average_amount = Decimal(str(np.mean(amounts)))
            median_amount = Decimal(str(np.median(amounts)))
        else:
            average_amount = median_amount = Decimal('0')
        
        return TransactionAnalytics(
            total_transactions=total_count,
            successful_transactions=successful,
            failed_transactions=failed,
            pending_transactions=pending,
            success_rate=success_rate,
            failure_rate=failure_rate,
            average_amount=average_amount,
            median_amount=median_amount
        )
    
    async def calculate_provider_performance(
        self,
        transactions: List[PaymentTransaction],
        timeframe: AnalyticsTimeframe
    ) -> Dict[PaymentProvider, Dict[str, Any]]:
        """
Calculate performance metrics by payment provider"""
        
        provider_metrics = {}
        
        for provider in PaymentProvider:
            provider_transactions = [t for t in transactions if t.provider == provider]
            
            if not provider_transactions:
                continue
            
            analytics = await self.calculate_transaction_analytics(
                provider_transactions, timeframe
            )
            
            revenue = await self.calculate_revenue_metrics(
                provider_transactions, timeframe
            )
            
            # Calculate average processing time
            processing_times = [
                (t.updated_at - t.created_at).total_seconds()
                for t in provider_transactions
                if t.updated_at and t.status == PaymentStatus.COMPLETED
            ]
            
            avg_processing_time = np.mean(processing_times) if processing_times else 0
            
            provider_metrics[provider] = {
                'transaction_analytics': analytics,
                'revenue_breakdown': revenue,
                'average_processing_time_seconds': avg_processing_time,
                'total_volume': revenue.total_revenue,
                'market_share': 0  # Will be calculated after all providers
            }
        
        # Calculate market share
        total_volume = sum(
            metrics['total_volume'] for metrics in provider_metrics.values()
        )
        
        if total_volume > 0:
            for provider, metrics in provider_metrics.items():
                metrics['market_share'] = float(metrics['total_volume'] / total_volume * 100)
        
        return provider_metrics
    
    async def calculate_cohort_analysis(
        self,
        transactions: List[PaymentTransaction],
        cohort_period: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY
    ) -> Dict[str, Any]:
        """
Perform cohort analysis on customer payment behavior"""
        
        # Group transactions by user and time periods
        user_transactions = defaultdict(list)
        for transaction in transactions:
            if transaction.status == PaymentStatus.COMPLETED:
                user_transactions[transaction.user_id].append(transaction)
        
        cohorts = {}
        
        for user_id, user_txns in user_transactions.items():
            # Sort transactions by date
            user_txns.sort(key=lambda x: x.created_at)
            
            if not user_txns:
                continue
            
            # First transaction defines the cohort
            first_transaction = user_txns[0]
            cohort_period_key = self._get_period_key(first_transaction.created_at, cohort_period)
            
            if cohort_period_key not in cohorts:
                cohorts[cohort_period_key] = {
                    'users': set(),
                    'first_transaction_amounts': [],
                    'total_revenue': Decimal('0'),
                    'repeat_customers': 0,
                    'periods': defaultdict(lambda: {'users': set(), 'revenue': Decimal('0')})
                }
            
            cohort = cohorts[cohort_period_key]
            cohort['users'].add(user_id)
            cohort['first_transaction_amounts'].append(float(first_transaction.amount))
            
            # Track user activity in subsequent periods
            for transaction in user_txns:
                period_key = self._get_period_key(transaction.created_at, cohort_period)
                cohort['periods'][period_key]['users'].add(user_id)
                cohort['periods'][period_key]['revenue'] += transaction.amount
                cohort['total_revenue'] += transaction.amount
            
            # Check if user made repeat purchases
            if len(user_txns) > 1:
                cohort['repeat_customers'] += 1
        
        # Calculate cohort metrics
        cohort_analysis = {}
        
        for period, cohort_data in cohorts.items():
            total_users = len(cohort_data['users'])
            
            if total_users == 0:
                continue
            
            retention_rates = {}
            revenue_per_period = {}
            
            for sub_period, period_data in cohort_data['periods'].items():
                period_users = len(period_data['users'])
                retention_rate = (period_users / total_users) * 100
                
                retention_rates[sub_period] = retention_rate
                revenue_per_period[sub_period] = float(period_data['revenue'])
            
            cohort_analysis[period] = {
                'total_users': total_users,
                'repeat_customer_rate': (cohort_data['repeat_customers'] / total_users) * 100,
                'average_first_transaction': np.mean(cohort_data['first_transaction_amounts']),
                'total_revenue': float(cohort_data['total_revenue']),
                'retention_rates': retention_rates,
                'revenue_per_period': revenue_per_period
            }
        
        return cohort_analysis
    
    async def detect_payment_anomalies(
        self,
        transactions: List[PaymentTransaction],
        lookback_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
Detect anomalies in payment patterns"""
        
        anomalies = []
        
        # Group transactions by day
        daily_data = defaultdict(lambda: {
            'count': 0,
            'revenue': Decimal('0'),
            'failed_count': 0,
            'average_amount': Decimal('0')
        })
        
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        recent_transactions = [
            t for t in transactions 
            if t.created_at >= cutoff_date
        ]
        
        for transaction in recent_transactions:
            day_key = transaction.created_at.date()
            day_data = daily_data[day_key]
            
            day_data['count'] += 1
            
            if transaction.status == PaymentStatus.COMPLETED:
                day_data['revenue'] += transaction.amount
            elif transaction.status == PaymentStatus.FAILED:
                day_data['failed_count'] += 1
        
        # Calculate averages and detect anomalies
        daily_counts = [data['count'] for data in daily_data.values()]
        daily_revenues = [float(data['revenue']) for data in daily_data.values()]
        daily_failure_rates = [
            (data['failed_count'] / data['count'] * 100) if data['count'] > 0 else 0
            for data in daily_data.values()
        ]
        
        if len(daily_counts) > 7:  # Need enough data
            # Calculate statistical thresholds
            count_mean = np.mean(daily_counts)
            count_std = np.std(daily_counts)
            count_threshold_high = count_mean + (2 * count_std)
            count_threshold_low = max(0, count_mean - (2 * count_std))
            
            revenue_mean = np.mean(daily_revenues)
            revenue_std = np.std(daily_revenues)
            revenue_threshold_high = revenue_mean + (2 * revenue_std)
            revenue_threshold_low = max(0, revenue_mean - (2 * revenue_std))
            
            failure_rate_mean = np.mean(daily_failure_rates)
            failure_rate_std = np.std(daily_failure_rates)
            failure_rate_threshold = failure_rate_mean + (2 * failure_rate_std)
            
            # Check each day for anomalies
            for day, data in daily_data.items():
                failure_rate = (data['failed_count'] / data['count'] * 100) if data['count'] > 0 else 0
                
                # High transaction count anomaly
                if data['count'] > count_threshold_high:
                    anomalies.append({
                        'date': day.isoformat(),
                        'type': 'high_transaction_volume',
                        'value': data['count'],
                        'threshold': count_threshold_high,
                        'severity': 'medium'
                    })
                
                # Low transaction count anomaly
                if data['count'] < count_threshold_low and data['count'] > 0:
                    anomalies.append({
                        'date': day.isoformat(),
                        'type': 'low_transaction_volume',
                        'value': data['count'],
                        'threshold': count_threshold_low,
                        'severity': 'low'
                    })
                
                # High revenue anomaly
                if float(data['revenue']) > revenue_threshold_high:
                    anomalies.append({
                        'date': day.isoformat(),
                        'type': 'high_revenue',
                        'value': float(data['revenue']),
                        'threshold': revenue_threshold_high,
                        'severity': 'low'  # High revenue is generally good
                    })
                
                # High failure rate anomaly
                if failure_rate > failure_rate_threshold and failure_rate > 10:  # At least 10% failure rate
                    anomalies.append({
                        'date': day.isoformat(),
                        'type': 'high_failure_rate',
                        'value': failure_rate,
                        'threshold': failure_rate_threshold,
                        'severity': 'high'
                    })
        
        return anomalies
    
    async def generate_forecasting_data(
        self,
        transactions: List[PaymentTransaction],
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """
Generate revenue forecasting data"""
        
        # Group successful transactions by day
        daily_revenue = defaultdict(lambda: Decimal('0'))
        
        for transaction in transactions:
            if transaction.status == PaymentStatus.COMPLETED:
                day_key = transaction.created_at.date()
                daily_revenue[day_key] += transaction.amount
        
        # Convert to time series
        if len(daily_revenue) < 14:  # Need at least 2 weeks of data
            return {
                'forecast': [],
                'confidence_interval': [],
                'error': 'Insufficient data for forecasting'
            }
        
        dates = sorted(daily_revenue.keys())
        revenues = [float(daily_revenue[date]) for date in dates]
        
        # Simple moving average forecast (in production, use more sophisticated models)
        window_size = min(14, len(revenues) // 2)
        moving_averages = []
        
        for i in range(len(revenues)):
            start_idx = max(0, i - window_size + 1)
            avg = np.mean(revenues[start_idx:i+1])
            moving_averages.append(avg)
        
        # Generate forecast
        last_avg = np.mean(revenues[-window_size:])
        trend = (revenues[-1] - revenues[-7]) / 7 if len(revenues) >= 7 else 0
        
        forecast_data = []
        current_date = dates[-1]
        
        for i in range(1, forecast_days + 1):
            forecast_date = current_date + timedelta(days=i)
            forecast_value = last_avg + (trend * i)
            
            # Add some seasonality (simple weekly pattern)
            day_of_week = forecast_date.weekday()
            seasonal_factor = 1.0
            if day_of_week in [5, 6]:  # Weekend
                seasonal_factor = 0.8
            elif day_of_week == 0:  # Monday
                seasonal_factor = 1.2
            
            forecast_value *= seasonal_factor
            
            forecast_data.append({
                'date': forecast_date.isoformat(),
                'predicted_revenue': max(0, forecast_value),
                'confidence_low': max(0, forecast_value * 0.8),
                'confidence_high': forecast_value * 1.2
            })
        
        return {
            'forecast': forecast_data,
            'historical_data': [
                {
                    'date': date.isoformat(),
                    'revenue': float(daily_revenue[date])
                }
                for date in dates
            ],
            'model_accuracy': self._calculate_forecast_accuracy(revenues, moving_averages)
        }
    
    def _estimate_transaction_fee(self, amount: Decimal, provider: PaymentProvider) -> Decimal:
        """
Estimate transaction fee based on provider"""
        fee_rates = {
            PaymentProvider.STRIPE: Decimal('0.029'),  # 2.9% + $0.30
            PaymentProvider.PAYPAL: Decimal('0.034'),  # 3.4% + $0.30
            PaymentProvider.CRYPTO: Decimal('0.01'),   # 1% (network fees vary)
        }
        
        base_fee = {
            PaymentProvider.STRIPE: Decimal('0.30'),
            PaymentProvider.PAYPAL: Decimal('0.30'),
            PaymentProvider.CRYPTO: Decimal('0.00'),
        }
        
        rate = fee_rates.get(provider, Decimal('0.03'))
        base = base_fee.get(provider, Decimal('0.30'))
        
        return (amount * rate) + base
    
    def _get_period_key(self, date: datetime, period: AnalyticsTimeframe) -> str:
        """
Get period key for grouping"""
        if period == AnalyticsTimeframe.DAILY:
            return date.strftime('%Y-%m-%d')
        elif period == AnalyticsTimeframe.WEEKLY:
            return f"{date.year}-W{date.isocalendar()[1]}"
        elif period == AnalyticsTimeframe.MONTHLY:
            return f"{date.year}-{date.month:02d}"
        elif period == AnalyticsTimeframe.QUARTERLY:
            quarter = (date.month - 1) // 3 + 1
            return f"{date.year}-Q{quarter}"
        elif period == AnalyticsTimeframe.YEARLY:
            return str(date.year)
        else:
            return date.strftime('%Y-%m-%d')
    
    def _calculate_forecast_accuracy(self, actual: List[float], predicted: List[float]) -> float:
        """Calculate forecast accuracy using MAPE (Mean Absolute Percentage Error)"""
        if len(actual) != len(predicted) or len(actual) == 0:
            return 0.0
        
        errors = []
        for a, p in zip(actual, predicted):
            if a != 0:
                error = abs((a - p) / a) * 100
                errors.append(error)
        
        if not errors:
            return 0.0
        
        mape = np.mean(errors)
        accuracy = max(0, 100 - mape)
        
        return accuracy


class PaymentReportsGenerator:
    """
Generate comprehensive payment reports"""
    
    def __init__(self, analytics_engine: PaymentAnalyticsEngine):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def generate_executive_summary(
        self,
        transactions: List[PaymentTransaction],
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY
    ) -> Dict[str, Any]:
        """
Generate executive summary report"""
        
        # Calculate key metrics
        revenue_breakdown = await self.analytics.calculate_revenue_metrics(
            transactions, timeframe
        )
        
        transaction_analytics = await self.analytics.calculate_transaction_analytics(
            transactions, timeframe
        )
        
        provider_performance = await self.analytics.calculate_provider_performance(
            transactions, timeframe
        )
        
        anomalies = await self.analytics.detect_payment_anomalies(transactions)
        
        # Calculate key insights
        top_provider = max(
            provider_performance.items(),
            key=lambda x: x[1]['total_volume'],
            default=(None, None)
        )[0] if provider_performance else None
        
        return {
            'report_type': 'executive_summary',
            'timeframe': timeframe.value,
            'generated_at': datetime.now().isoformat(),
            'key_metrics': {
                'total_revenue': float(revenue_breakdown.total_revenue),
                'net_revenue': float(revenue_breakdown.net_revenue),
                'transaction_count': transaction_analytics.total_transactions,
                'success_rate': transaction_analytics.success_rate,
                'average_transaction_value': float(transaction_analytics.average_amount)
            },
            'revenue_breakdown': {
                'gross_revenue': float(revenue_breakdown.gross_revenue),
                'fees': float(revenue_breakdown.fees),
                'refunds': float(revenue_breakdown.refunds),
                'chargebacks': float(revenue_breakdown.chargebacks),
                'net_revenue': float(revenue_breakdown.net_revenue)
            },
            'provider_insights': {
                'top_performing_provider': top_provider.value if top_provider else None,
                'provider_count': len(provider_performance),
                'provider_details': {
                    provider.value: {
                        'market_share': details['market_share'],
                        'success_rate': details['transaction_analytics'].success_rate,
                        'volume': float(details['total_volume'])
                    }
                    for provider, details in provider_performance.items()
                }
            },
            'anomalies': {
                'total_anomalies': len(anomalies),
                'high_severity_count': len([a for a in anomalies if a['severity'] == 'high']),
                'recent_anomalies': anomalies[-5:]  # Last 5 anomalies
            }
        }
    
    async def generate_detailed_financial_report(
        self,
        transactions: List[PaymentTransaction],
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY
    ) -> Dict[str, Any]:
        """
Generate detailed financial report"""
        
        # Group transactions by currency
        currencies = set(t.currency for t in transactions)
        currency_breakdowns = {}
        
        for currency in currencies:
            currency_transactions = [t for t in transactions if t.currency == currency]
            breakdown = await self.analytics.calculate_revenue_metrics(
                currency_transactions, timeframe, currency
            )
            currency_breakdowns[currency] = breakdown
        
        # Calculate forecasting data
        forecast_data = await self.analytics.generate_forecasting_data(transactions)
        
        return {
            'report_type': 'detailed_financial',
            'timeframe': timeframe.value,
            'generated_at': datetime.now().isoformat(),
            'currency_breakdown': {
                currency: {
                    'total_revenue': float(breakdown.total_revenue),
                    'net_revenue': float(breakdown.net_revenue),
                    'fees': float(breakdown.fees),
                    'refunds': float(breakdown.refunds),
                    'chargebacks': float(breakdown.chargebacks)
                }
                for currency, breakdown in currency_breakdowns.items()
            },
            'forecast': forecast_data,
            'financial_ratios': {
                'refund_rate': sum(float(b.refunds) for b in currency_breakdowns.values()) / 
                              sum(float(b.total_revenue) for b in currency_breakdowns.values()) * 100
                              if sum(float(b.total_revenue) for b in currency_breakdowns.values()) > 0 else 0,
                'chargeback_rate': sum(float(b.chargebacks) for b in currency_breakdowns.values()) / 
                                  sum(float(b.total_revenue) for b in currency_breakdowns.values()) * 100
                                  if sum(float(b.total_revenue) for b in currency_breakdowns.values()) > 0 else 0,
                'net_margin': sum(float(b.net_revenue) for b in currency_breakdowns.values()) / 
                             sum(float(b.total_revenue) for b in currency_breakdowns.values()) * 100
                             if sum(float(b.total_revenue) for b in currency_breakdowns.values()) > 0 else 0
            }
        }
    
    async def generate_operational_report(
        self,
        transactions: List[PaymentTransaction],
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY
    ) -> Dict[str, Any]:
        """
Generate operational performance report"""
        
        provider_performance = await self.analytics.calculate_provider_performance(
            transactions, timeframe
        )
        
        anomalies = await self.analytics.detect_payment_anomalies(transactions)
        
        # Calculate operational metrics
        failed_transactions = [t for t in transactions if t.status == PaymentStatus.FAILED]
        failure_reasons = defaultdict(int)
        
        for transaction in failed_transactions:
            reason = getattr(transaction, 'failure_reason', 'unknown')
            failure_reasons[reason] += 1
        
        return {
            'report_type': 'operational',
            'timeframe': timeframe.value,
            'generated_at': datetime.now().isoformat(),
            'provider_performance': {
                provider.value: {
                    'success_rate': details['transaction_analytics'].success_rate,
                    'failure_rate': details['transaction_analytics'].failure_rate,
                    'average_processing_time': details['average_processing_time_seconds'],
                    'total_transactions': details['transaction_analytics'].total_transactions
                }
                for provider, details in provider_performance.items()
            },
            'failure_analysis': {
                'total_failures': len(failed_transactions),
                'failure_reasons': dict(failure_reasons),
                'top_failure_reason': max(failure_reasons.items(), key=lambda x: x[1])[0] 
                                     if failure_reasons else None
            },
            'anomalies': {
                'detected_anomalies': len(anomalies),
                'by_type': {
                    anomaly_type: len([a for a in anomalies if a['type'] == anomaly_type])
                    for anomaly_type in set(a['type'] for a in anomalies)
                },
                'by_severity': {
                    severity: len([a for a in anomalies if a['severity'] == severity])
                    for severity in set(a['severity'] for a in anomalies)
                }
            },
            'recommendations': self._generate_operational_recommendations(
                provider_performance, anomalies, failure_reasons
            )
        }
    
    def _generate_operational_recommendations(
        self,
        provider_performance: Dict[PaymentProvider, Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        failure_reasons: Dict[str, int]
    ) -> List[str]:
        """
Generate operational recommendations"""
        
        recommendations = []
        
        # Provider performance recommendations
        for provider, metrics in provider_performance.items():
            success_rate = metrics['transaction_analytics'].success_rate
            
            if success_rate < 95:
                recommendations.append(
                    f"Review {provider.value} configuration - success rate is {success_rate:.1f}%"
                )
            
            if metrics['average_processing_time_seconds'] > 30:
                recommendations.append(
                    f"Optimize {provider.value} processing time - currently {metrics['average_processing_time_seconds']:.1f}s"
                )
        
        # Anomaly recommendations
        high_severity_anomalies = [a for a in anomalies if a['severity'] == 'high']
        if len(high_severity_anomalies) > 0:
            recommendations.append(
                f"Investigate {len(high_severity_anomalies)} high-severity anomalies immediately"
            )
        
        # Failure reason recommendations
        if failure_reasons:
            top_failure = max(failure_reasons.items(), key=lambda x: x[1])
            if top_failure[1] > 10:  # More than 10 failures of same type
                recommendations.append(
                    f"Address recurring failure: {top_failure[0]} ({top_failure[1]} occurrences)"
                )
        
        return recommendations
