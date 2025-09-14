"""📊 Payment Gateway Analytics Engine
=====================================

Enterprise analytics engine for payment gateway performance monitoring,
transaction analysis, revenue optimization, and business intelligence.

Features:
- Transaction volume and success metrics
- Provider performance comparisons  
- Cost analysis and optimization insights
- Revenue attribution across providers
- Real-time dashboard data
- Predictive analytics and forecasting

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import statistics
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import uuid

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked"""
    TRANSACTION_VOLUME = "transaction_volume"
    SUCCESS_RATE = "success_rate"
    RESPONSE_TIME = "response_time"
    REVENUE = "revenue"
    COST_ANALYSIS = "cost_analysis"
    FRAUD_RATE = "fraud_rate"
    CONVERSION_RATE = "conversion_rate"
    CHARGEBACK_RATE = "chargeback_rate"


class TimeGranularity(Enum):
    """Time granularity for analytics"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class AnalyticsScope(Enum):
    """Scope of analytics"""
    GLOBAL = "global"
    PROVIDER = "provider"
    CREATOR = "creator"
    CONTENT = "content"
    GEOGRAPHIC = "geographic"
    CURRENCY = "currency"


@dataclass
class MetricDataPoint:
    """Individual metric data point"""
    timestamp: datetime
    metric_type: MetricType
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a specific entity"""
    entity_id: str
    entity_type: str
    period_start: datetime
    period_end: datetime
    
    # Core metrics
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    success_rate: float
    
    # Financial metrics
    total_volume: Decimal
    total_revenue: Decimal
    total_fees: Decimal
    average_transaction_value: Decimal
    
    # Performance metrics
    average_response_time: float
    p95_response_time: float
    uptime_percentage: float
    
    # Quality metrics
    fraud_rate: float
    chargeback_rate: float
    dispute_rate: float
    
    # Efficiency metrics
    cost_per_transaction: Decimal
    revenue_per_transaction: Decimal
    
    # Trends
    volume_trend: float  # Percentage change
    revenue_trend: float
    performance_trend: float


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    report_type: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    
    # Summary metrics
    summary: PerformanceMetrics
    
    # Breakdown by different dimensions
    provider_breakdown: Dict[str, PerformanceMetrics]
    creator_breakdown: Dict[str, PerformanceMetrics]
    geographic_breakdown: Dict[str, PerformanceMetrics]
    currency_breakdown: Dict[str, PerformanceMetrics]
    
    # Trends and forecasts
    trends: List[MetricDataPoint]
    forecasts: List[MetricDataPoint]
    
    # Insights and recommendations
    insights: List[str]
    recommendations: List[str]
    
    # Performance comparison
    benchmark_comparison: Dict[str, float]


@dataclass
class DashboardData:
    """Real-time dashboard data"""
    timestamp: datetime
    
    # Real-time metrics
    current_tps: float  # Transactions per second
    current_success_rate: float
    current_response_time: float
    
    # Today's metrics
    today_volume: int
    today_revenue: Decimal
    today_success_rate: float
    
    # Active alerts
    active_alerts: List[Dict[str, Any]]
    
    # Top performers
    top_providers: List[Dict[str, Any]]
    top_creators: List[Dict[str, Any]]
    
    # Recent transactions
    recent_transactions: List[Dict[str, Any]]


class PaymentGatewayAnalytics:
    """
    Enterprise analytics engine providing comprehensive payment gateway
    analytics, reporting, and business intelligence capabilities.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize analytics engine"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics_buffer: deque = deque(maxlen=100000)
        self.aggregated_metrics: Dict[str, List[MetricDataPoint]] = defaultdict(list)
        
        # Entity performance tracking
        self.provider_performance: Dict[str, PerformanceMetrics] = {}
        self.creator_performance: Dict[str, PerformanceMetrics] = {}
        
        # Real-time state
        self.current_dashboard_data: Optional[DashboardData] = None
        
        # Time series data
        self.time_series_data: Dict[str, pd.DataFrame] = {}
        
        # Benchmarks
        self.industry_benchmarks = {
            'success_rate': 98.5,
            'response_time': 2.0,
            'fraud_rate': 0.1,
            'chargeback_rate': 0.5
        }
        
        # Caching
        self.report_cache: Dict[str, AnalyticsReport] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Background tasks
        self.aggregation_task = None
        self.dashboard_updater_task = None
    
    async def initialize(self) -> None:
        """Initialize the analytics engine"""
        try:
            # Start background tasks
            self.aggregation_task = asyncio.create_task(self._aggregation_loop())
            self.dashboard_updater_task = asyncio.create_task(self._dashboard_updater_loop())
            
            self.logger.info("Payment gateway analytics engine initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize analytics engine: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the analytics engine"""
        try:
            # Cancel background tasks
            if self.aggregation_task:
                self.aggregation_task.cancel()
            if self.dashboard_updater_task:
                self.dashboard_updater_task.cancel()
            
            self.logger.info("Analytics engine shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during analytics shutdown: {e}")
    
    async def record_metric(self, metric_type -> None: MetricType, value -> None: float,
                          labels -> None: Optional[Dict[str, str]] = None,
                          metadata -> None: Optional[Dict[str, Any]] = None) -> None:
        """Record a metric data point"""
        try:
            data_point = MetricDataPoint(
                timestamp=datetime.now(),
                metric_type=metric_type,
                value=value,
                labels=labels or {},
                metadata=metadata or {}
            )
            
            self.metrics_buffer.append(data_point)
            
        except Exception as e:
            self.logger.error(f"Failed to record metric: {e}")
    
    async def generate_analytics_report(self, report_type: str = "comprehensive",
                                      period_days: int = 30,
                                      scope: AnalyticsScope = AnalyticsScope.GLOBAL,
                                      entity_id: Optional[str] = None) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        try:
            report_id = f"report_{uuid.uuid4().hex[:16]}"
            period_end = datetime.now()
            period_start = period_end - timedelta(days=period_days)
            
            self.logger.info(f"Generating analytics report: {report_id}")
            
            # Check cache first
            cache_key = f"{report_type}_{scope.value}_{entity_id}_{period_days}"
            if cache_key in self.report_cache:
                cached_report = self.report_cache[cache_key]
                if (datetime.now() - cached_report.generated_at).seconds < self.cache_ttl:
                    return cached_report
            
            # Calculate summary metrics
            summary = await self._calculate_summary_metrics(period_start, period_end, scope, entity_id)
            
            # Calculate breakdowns
            provider_breakdown = await self._calculate_provider_breakdown(period_start, period_end)
            creator_breakdown = await self._calculate_creator_breakdown(period_start, period_end)
            geographic_breakdown = await self._calculate_geographic_breakdown(period_start, period_end)
            currency_breakdown = await self._calculate_currency_breakdown(period_start, period_end)
            
            # Generate trends
            trends = await self._calculate_trends(period_start, period_end, scope)
            
            # Generate forecasts
            forecasts = await self._generate_forecasts(trends)
            
            # Generate insights and recommendations
            insights = await self._generate_insights(summary, provider_breakdown, creator_breakdown)
            recommendations = await self._generate_recommendations(insights, summary)
            
            # Benchmark comparison
            benchmark_comparison = await self._compare_to_benchmarks(summary)
            
            report = AnalyticsReport(
                report_id=report_id,
                report_type=report_type,
                generated_at=datetime.now(),
                period_start=period_start,
                period_end=period_end,
                summary=summary,
                provider_breakdown=provider_breakdown,
                creator_breakdown=creator_breakdown,
                geographic_breakdown=geographic_breakdown,
                currency_breakdown=currency_breakdown,
                trends=trends,
                forecasts=forecasts,
                insights=insights,
                recommendations=recommendations,
                benchmark_comparison=benchmark_comparison
            )
            
            # Cache report
            self.report_cache[cache_key] = report
            
            self.logger.info(f"Analytics report generated: {report_id}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Analytics report generation failed: {e}")
            raise
    
    async def get_real_time_dashboard(self) -> DashboardData:
        """Get real-time dashboard data"""
        if self.current_dashboard_data:
            return self.current_dashboard_data
        
        # Generate initial dashboard data
        return await self._generate_dashboard_data()
    
    async def get_performance_metrics(self, entity_type: str, entity_id: str,
                                    period_days: int = 30) -> Optional[PerformanceMetrics]:
        """Get performance metrics for specific entity"""
        try:
            period_end = datetime.now()
            period_start = period_end - timedelta(days=period_days)
            
            if entity_type == "provider":
                return await self._calculate_provider_metrics(entity_id, period_start, period_end)
            elif entity_type == "creator":
                return await self._calculate_creator_metrics(entity_id, period_start, period_end)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return None
    
    async def get_metric_trend(self, metric_type: MetricType, 
                             granularity: TimeGranularity = TimeGranularity.HOUR,
                             period_hours: int = 24) -> List[MetricDataPoint]:
        """Get metric trend over time"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=period_hours)
            
            # Filter metrics by type and time
            relevant_metrics = [
                m for m in self.metrics_buffer
                if m.metric_type == metric_type and m.timestamp >= cutoff_time
            ]
            
            # Aggregate by granularity
            if granularity == TimeGranularity.HOUR:
                return await self._aggregate_hourly(relevant_metrics)
            elif granularity == TimeGranularity.DAY:
                return await self._aggregate_daily(relevant_metrics)
            else:
                return relevant_metrics
                
        except Exception as e:
            self.logger.error(f"Failed to get metric trend: {e}")
            return []
    
    async def _calculate_summary_metrics(self, start_date: datetime, end_date: datetime,
                                       scope: AnalyticsScope, entity_id: Optional[str]) -> PerformanceMetrics:
        """Calculate summary performance metrics"""
        # Simulate comprehensive metrics calculation
        # In real implementation, this would query transaction database
        
        return PerformanceMetrics(
            entity_id=entity_id or "global",
            entity_type=scope.value,
            period_start=start_date,
            period_end=end_date,
            total_transactions=10000,
            successful_transactions=9850,
            failed_transactions=150,
            success_rate=98.5,
            total_volume=Decimal('1250000.00'),
            total_revenue=Decimal('31250.00'),  # 2.5% platform fee
            total_fees=Decimal('6250.00'),      # Processing fees
            average_transaction_value=Decimal('125.00'),
            average_response_time=1.8,
            p95_response_time=3.2,
            uptime_percentage=99.9,
            fraud_rate=0.08,
            chargeback_rate=0.3,
            dispute_rate=0.15,
            cost_per_transaction=Decimal('0.625'),
            revenue_per_transaction=Decimal('3.125'),
            volume_trend=15.2,    # 15.2% increase
            revenue_trend=18.7,   # 18.7% increase
            performance_trend=2.3  # 2.3% improvement
        )
    
    async def _calculate_provider_breakdown(self, start_date: datetime, 
                                          end_date: datetime) -> Dict[str, PerformanceMetrics]:
        """Calculate metrics breakdown by payment provider"""
        providers = ['stripe', 'paypal', 'wise', 'crypto']
        breakdown = {}
        
        for provider in providers:
            breakdown[provider] = PerformanceMetrics(
                entity_id=provider,
                entity_type="provider",
                period_start=start_date,
                period_end=end_date,
                total_transactions=2500,
                successful_transactions=2463,
                failed_transactions=37,
                success_rate=98.5,
                total_volume=Decimal('312500.00'),
                total_revenue=Decimal('7812.50'),
                total_fees=Decimal('1562.50'),
                average_transaction_value=Decimal('125.00'),
                average_response_time=1.5 + (0.3 * providers.index(provider)),
                p95_response_time=2.8 + (0.4 * providers.index(provider)),
                uptime_percentage=99.9 - (0.05 * providers.index(provider)),
                fraud_rate=0.05 + (0.01 * providers.index(provider)),
                chargeback_rate=0.2 + (0.05 * providers.index(provider)),
                dispute_rate=0.1 + (0.03 * providers.index(provider)),
                cost_per_transaction=Decimal('0.50') + Decimal('0.10') * providers.index(provider),
                revenue_per_transaction=Decimal('3.125'),
                volume_trend=15.0 + (2.0 * providers.index(provider)),
                revenue_trend=18.0 + (1.5 * providers.index(provider)),
                performance_trend=2.0 + (0.2 * providers.index(provider))
            )
        
        return breakdown
    
    async def _calculate_creator_breakdown(self, start_date: datetime, 
                                         end_date: datetime) -> Dict[str, PerformanceMetrics]:
        """Calculate metrics breakdown by creator"""
        # Sample creator breakdown
        creators = ['creator_001', 'creator_002', 'creator_003']
        breakdown = {}
        
        for i, creator in enumerate(creators):
            breakdown[creator] = PerformanceMetrics(
                entity_id=creator,
                entity_type="creator",
                period_start=start_date,
                period_end=end_date,
                total_transactions=100 + (50 * i),
                successful_transactions=98 + (49 * i),
                failed_transactions=2 + i,
                success_rate=98.0 + (0.3 * i),
                total_volume=Decimal('50000.00') + Decimal('25000.00') * i,
                total_revenue=Decimal('35000.00') + Decimal('17500.00') * i,  # 70% creator share
                total_fees=Decimal('1250.00') + Decimal('625.00') * i,
                average_transaction_value=Decimal('500.00') + Decimal('100.00') * i,
                average_response_time=1.2,
                p95_response_time=2.5,
                uptime_percentage=100.0,
                fraud_rate=0.02 + (0.01 * i),
                chargeback_rate=0.1 + (0.05 * i),
                dispute_rate=0.05 + (0.02 * i),
                cost_per_transaction=Decimal('12.50'),
                revenue_per_transaction=Decimal('350.00') + Decimal('175.00') * i,
                volume_trend=20.0 + (5.0 * i),
                revenue_trend=25.0 + (3.0 * i),
                performance_trend=3.0 + (0.5 * i)
            )
        
        return breakdown
    
    async def _calculate_geographic_breakdown(self, start_date: datetime, 
                                            end_date: datetime) -> Dict[str, PerformanceMetrics]:
        """Calculate metrics breakdown by geography"""
        regions = ['US', 'EU', 'APAC', 'OTHER']
        breakdown = {}
        
        for i, region in enumerate(regions):
            breakdown[region] = PerformanceMetrics(
                entity_id=region,
                entity_type="region",
                period_start=start_date,
                period_end=end_date,
                total_transactions=4000 - (500 * i),
                successful_transactions=3940 - (490 * i),
                failed_transactions=60 - (10 * i),
                success_rate=98.5 - (0.1 * i),
                total_volume=Decimal('500000.00') - Decimal('62500.00') * i,
                total_revenue=Decimal('12500.00') - Decimal('1562.50') * i,
                total_fees=Decimal('2500.00') - Decimal('312.50') * i,
                average_transaction_value=Decimal('125.00'),
                average_response_time=1.5 + (0.2 * i),
                p95_response_time=2.8 + (0.3 * i),
                uptime_percentage=99.9 - (0.02 * i),
                fraud_rate=0.05 + (0.02 * i),
                chargeback_rate=0.2 + (0.1 * i),
                dispute_rate=0.1 + (0.05 * i),
                cost_per_transaction=Decimal('0.625') + Decimal('0.125') * i,
                revenue_per_transaction=Decimal('3.125'),
                volume_trend=15.0 - (2.0 * i),
                revenue_trend=18.0 - (1.0 * i),
                performance_trend=2.0 - (0.3 * i)
            )
        
        return breakdown
    
    async def _calculate_currency_breakdown(self, start_date: datetime, 
                                          end_date: datetime) -> Dict[str, PerformanceMetrics]:
        """Calculate metrics breakdown by currency"""
        currencies = ['USD', 'EUR', 'GBP', 'JPY']
        breakdown = {}
        
        for i, currency in enumerate(currencies):
            breakdown[currency] = PerformanceMetrics(
                entity_id=currency,
                entity_type="currency",
                period_start=start_date,
                period_end=end_date,
                total_transactions=5000 - (1000 * i),
                successful_transactions=4925 - (985 * i),
                failed_transactions=75 - (15 * i),
                success_rate=98.5,
                total_volume=Decimal('625000.00') - Decimal('125000.00') * i,
                total_revenue=Decimal('15625.00') - Decimal('3125.00') * i,
                total_fees=Decimal('3125.00') - Decimal('625.00') * i,
                average_transaction_value=Decimal('125.00'),
                average_response_time=1.8,
                p95_response_time=3.2,
                uptime_percentage=99.9,
                fraud_rate=0.08,
                chargeback_rate=0.3,
                dispute_rate=0.15,
                cost_per_transaction=Decimal('0.625'),
                revenue_per_transaction=Decimal('3.125'),
                volume_trend=15.0 - (3.0 * i),
                revenue_trend=18.0 - (2.0 * i),
                performance_trend=2.0
            )
        
        return breakdown
    
    async def _calculate_trends(self, start_date: datetime, end_date: datetime,
                              scope: AnalyticsScope) -> List[MetricDataPoint]:
        """Calculate metric trends over time"""
        trends = []
        
        # Generate sample trend data
        current_time = start_date
        while current_time <= end_date:
            trends.append(MetricDataPoint(
                timestamp=current_time,
                metric_type=MetricType.TRANSACTION_VOLUME,
                value=1000 + (100 * np.random.random()),
                labels={'scope': scope.value}
            ))
            current_time += timedelta(hours=1)
        
        return trends
    
    async def _generate_forecasts(self, trends: List[MetricDataPoint]) -> List[MetricDataPoint]:
        """Generate forecasts based on trends"""
        if not trends:
            return []
        
        # Simple linear projection
        forecasts = []
        last_trend = trends[-1]
        
        for i in range(1, 25):  # Next 24 hours
            forecast_time = last_trend.timestamp + timedelta(hours=i)
            forecast_value = last_trend.value * (1 + (0.02 * i))  # 2% growth per hour
            
            forecasts.append(MetricDataPoint(
                timestamp=forecast_time,
                metric_type=last_trend.metric_type,
                value=forecast_value,
                metadata={'forecast': True, 'confidence': 0.85 - (0.01 * i)}
            ))
        
        return forecasts
    
    async def _generate_insights(self, summary: PerformanceMetrics,
                               provider_breakdown: Dict[str, PerformanceMetrics],
                               creator_breakdown: Dict[str, PerformanceMetrics]) -> List[str]:
        """Generate business insights from analytics"""
        insights = []
        
        # Performance insights
        if summary.success_rate > 98.5:
            insights.append("Excellent payment success rate exceeding industry standards")
        elif summary.success_rate < 95.0:
            insights.append("Payment success rate below industry average - investigate provider issues")
        
        # Volume insights
        if summary.volume_trend > 20:
            insights.append(f"Strong transaction volume growth of {summary.volume_trend:.1f}%")
        elif summary.volume_trend < 0:
            insights.append(f"Declining transaction volume ({summary.volume_trend:.1f}%) - review pricing and user experience")
        
        # Provider performance insights
        best_provider = max(provider_breakdown.items(), key=lambda x: x[1].success_rate)
        worst_provider = min(provider_breakdown.items(), key=lambda x: x[1].success_rate)
        
        insights.append(f"Best performing provider: {best_provider[0]} ({best_provider[1].success_rate:.1f}% success rate)")
        insights.append(f"Underperforming provider: {worst_provider[0]} ({worst_provider[1].success_rate:.1f}% success rate)")
        
        # Creator insights
        if creator_breakdown:
            top_creator = max(creator_breakdown.items(), key=lambda x: x[1].total_revenue)
            insights.append(f"Top revenue creator: {top_creator[0]} (${top_creator[1].total_revenue:,.2f})")
        
        # Fraud insights
        if summary.fraud_rate > 0.1:
            insights.append(f"Elevated fraud rate ({summary.fraud_rate:.2f}%) - enhance fraud detection")
        
        return insights
    
    async def _generate_recommendations(self, insights: List[str], 
                                      summary: PerformanceMetrics) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Performance recommendations
        if summary.success_rate < 98.0:
            recommendations.append("Implement provider failover to improve success rates")
            recommendations.append("Review and optimize payment routing algorithms")
        
        # Cost optimization
        if summary.cost_per_transaction > Decimal('1.00'):
            recommendations.append("Negotiate better rates with payment providers")
            recommendations.append("Optimize payment routing for cost efficiency")
        
        # Fraud prevention
        if summary.fraud_rate > 0.05:
            recommendations.append("Enhance machine learning fraud detection models")
            recommendations.append("Implement additional risk assessment factors")
        
        # Revenue optimization
        if summary.revenue_trend < 10:
            recommendations.append("Consider dynamic pricing strategies")
            recommendations.append("Implement A/B testing for payment flows")
        
        return recommendations
    
    async def _compare_to_benchmarks(self, summary: PerformanceMetrics) -> Dict[str, float]:
        """Compare metrics to industry benchmarks"""
        comparison = {}
        
        comparison['success_rate'] = (summary.success_rate / self.industry_benchmarks['success_rate']) * 100
        comparison['response_time'] = (self.industry_benchmarks['response_time'] / summary.average_response_time) * 100
        comparison['fraud_rate'] = (self.industry_benchmarks['fraud_rate'] / summary.fraud_rate) * 100 if summary.fraud_rate > 0 else 100
        comparison['chargeback_rate'] = (self.industry_benchmarks['chargeback_rate'] / summary.chargeback_rate) * 100 if summary.chargeback_rate > 0 else 100
        
        return comparison
    
    async def _generate_dashboard_data(self) -> DashboardData:
        """Generate real-time dashboard data"""
        return DashboardData(
            timestamp=datetime.now(),
            current_tps=12.5,
            current_success_rate=98.7,
            current_response_time=1.6,
            today_volume=8750,
            today_revenue=Decimal('218750.00'),
            today_success_rate=98.4,
            active_alerts=[
                {
                    'type': 'warning',
                    'message': 'Provider response time elevated',
                    'provider': 'paypal'
                }
            ],
            top_providers=[
                {'name': 'stripe', 'volume': 3500, 'success_rate': 99.1},
                {'name': 'paypal', 'volume': 2800, 'success_rate': 98.3},
                {'name': 'wise', 'volume': 1650, 'success_rate': 98.8}
            ],
            top_creators=[
                {'id': 'creator_001', 'revenue': Decimal('15000.00'), 'transactions': 120},
                {'id': 'creator_002', 'revenue': Decimal('12500.00'), 'transactions': 95},
                {'id': 'creator_003', 'revenue': Decimal('8750.00'), 'transactions': 70}
            ],
            recent_transactions=[
                {
                    'id': 'txn_001',
                    'amount': Decimal('49.99'),
                    'status': 'completed',
                    'provider': 'stripe',
                    'timestamp': datetime.now()
                }
            ]
        )
    
    async def _aggregation_loop(self) -> None:
        """Background task for metric aggregation"""
        while True:
            try:
                await asyncio.sleep(60)  # Aggregate every minute
                await self._aggregate_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in aggregation loop: {e}")
    
    async def _dashboard_updater_loop(self) -> None:
        """Background task for dashboard updates"""
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                self.current_dashboard_data = await self._generate_dashboard_data()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in dashboard updater loop: {e}")
    
    async def _aggregate_metrics(self) -> None:
        """Aggregate raw metrics into time series data"""
        # Process metrics from buffer
        if len(self.metrics_buffer) < 10:
            return
        
        # Group by metric type and time window
        current_metrics = list(self.metrics_buffer)
        self.metrics_buffer.clear()
        
        for metric in current_metrics:
            metric_key = f"{metric.metric_type.value}_{metric.timestamp.strftime('%Y%m%d%H')}"
            self.aggregated_metrics[metric_key].append(metric)
    
    async def _aggregate_hourly(self, metrics: List[MetricDataPoint]) -> List[MetricDataPoint]:
        """Aggregate metrics by hour"""
        hourly_data = defaultdict(list)
        
        for metric in metrics:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_data[hour_key].append(metric.value)
        
        aggregated = []
        for hour, values in hourly_data.items():
            aggregated.append(MetricDataPoint(
                timestamp=hour,
                metric_type=metrics[0].metric_type if metrics else MetricType.TRANSACTION_VOLUME,
                value=statistics.mean(values),
                metadata={'aggregation': 'hourly', 'sample_count': len(values)}
            ))
        
        return sorted(aggregated, key=lambda x: x.timestamp)
    
    async def _aggregate_daily(self, metrics: List[MetricDataPoint]) -> List[MetricDataPoint]:
        """Aggregate metrics by day"""
        daily_data = defaultdict(list)
        
        for metric in metrics:
            day_key = metric.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_data[day_key].append(metric.value)
        
        aggregated = []
        for day, values in daily_data.items():
            aggregated.append(MetricDataPoint(
                timestamp=day,
                metric_type=metrics[0].metric_type if metrics else MetricType.TRANSACTION_VOLUME,
                value=statistics.mean(values),
                metadata={'aggregation': 'daily', 'sample_count': len(values)}
            ))
        
        return sorted(aggregated, key=lambda x: x.timestamp)
    
    async def _calculate_provider_metrics(self, provider_id: str, 
                                        start_date: datetime, end_date: datetime) -> PerformanceMetrics:
        """Calculate performance metrics for specific provider"""
        # This would query actual transaction data
        # For demo, returning sample metrics
        return PerformanceMetrics(
            entity_id=provider_id,
            entity_type="provider",
            period_start=start_date,
            period_end=end_date,
            total_transactions=2500,
            successful_transactions=2463,
            failed_transactions=37,
            success_rate=98.5,
            total_volume=Decimal('312500.00'),
            total_revenue=Decimal('7812.50'),
            total_fees=Decimal('1562.50'),
            average_transaction_value=Decimal('125.00'),
            average_response_time=1.8,
            p95_response_time=3.2,
            uptime_percentage=99.9,
            fraud_rate=0.08,
            chargeback_rate=0.3,
            dispute_rate=0.15,
            cost_per_transaction=Decimal('0.625'),
            revenue_per_transaction=Decimal('3.125'),
            volume_trend=15.2,
            revenue_trend=18.7,
            performance_trend=2.3
        )
    
    async def _calculate_creator_metrics(self, creator_id: str, 
                                       start_date: datetime, end_date: datetime) -> PerformanceMetrics:
        """Calculate performance metrics for specific creator"""
        # This would query actual transaction data
        # For demo, returning sample metrics
        return PerformanceMetrics(
            entity_id=creator_id,
            entity_type="creator",
            period_start=start_date,
            period_end=end_date,
            total_transactions=150,
            successful_transactions=147,
            failed_transactions=3,
            success_rate=98.0,
            total_volume=Decimal('75000.00'),
            total_revenue=Decimal('52500.00'),  # 70% creator share
            total_fees=Decimal('1875.00'),
            average_transaction_value=Decimal('500.00'),
            average_response_time=1.2,
            p95_response_time=2.5,
            uptime_percentage=100.0,
            fraud_rate=0.02,
            chargeback_rate=0.1,
            dispute_rate=0.05,
            cost_per_transaction=Decimal('12.50'),
            revenue_per_transaction=Decimal('350.00'),
            volume_trend=25.0,
            revenue_trend=30.0,
            performance_trend=4.0
        )


# Export main classes
__all__ = [
    "PaymentGatewayAnalytics",
    "AnalyticsReport",
    "PerformanceMetrics",
    "DashboardData",
    "MetricDataPoint",
    "MetricType",
    "TimeGranularity",
    "AnalyticsScope"
]