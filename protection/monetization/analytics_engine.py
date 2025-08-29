"""
Analytics Engine - Professional monetization analytics and reporting system.
Provides comprehensive insights into revenue, performance, and optimization opportunities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timedelta, date
from enum import Enum
import asyncio
import logging
import json
from abc import ABC, abstractmethod
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of analytics metrics."""
    REVENUE = "revenue"
    TRANSACTIONS = "transactions"
    USERS = "users"
    CONVERSION = "conversion"
    RETENTION = "retention"
    GROWTH = "growth"
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"


class ReportType(Enum):
    """Types of analytics reports."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class AggregationType(Enum):
    """Data aggregation methods."""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MAX = "max"
    MIN = "min"
    MEDIAN = "median"
    PERCENTILE = "percentile"


@dataclass
class MetricData:
    """Individual metric data point."""
    metric_id: str
    metric_type: MetricType
    value: Union[Decimal, int, float]
    dimensions: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return {
            "metric_id": self.metric_id,
            "metric_type": self.metric_type.value,
            "value": float(self.value) if isinstance(self.value, Decimal) else self.value,
            "dimensions": self.dimensions,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ReportSection:
    """Report section with specific metrics."""
    section_id: str
    title: str
    metrics: List[MetricData] = field(default_factory=list)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def add_metric(self, metric: MetricData) -> None:
        """Add metric to section."""
        self.metrics.append(metric)
    
    def add_insight(self, insight: str) -> None:
        """Add insight to section."""
        self.insights.append(insight)
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add recommendation to section."""
        self.recommendations.append(recommendation)


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report."""
    report_id: str
    title: str
    report_type: ReportType
    period_start: datetime
    period_end: datetime
    sections: List[ReportSection] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_section(self, section: ReportSection) -> None:
        """Add section to report."""
        self.sections.append(section)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "report_id": self.report_id,
            "title": self.title,
            "report_type": self.report_type.value,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "sections": [
                {
                    "section_id": section.section_id,
                    "title": section.title,
                    "metrics": [m.to_dict() for m in section.metrics],
                    "charts": section.charts,
                    "insights": section.insights,
                    "recommendations": section.recommendations
                }
                for section in self.sections
            ],
            "summary": self.summary,
            "generated_at": self.generated_at.isoformat()
        }


class MetricCollector(ABC):
    """Abstract base class for metric collectors."""
    
    @abstractmethod
    async def collect_metrics(
        self, 
        metric_type: MetricType, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MetricData]:
        """Collect metrics for specified period."""
        # Abstract method that must be implemented by subclasses
        # This method should return a list of MetricData objects
        # representing the collected metrics for the specified period
        pass


class RevenueMetricCollector(MetricCollector):
    """Revenue metrics collector."""
    
    def __init__(self, revenue_engine):
        self.revenue_engine = revenue_engine
    
    async def collect_metrics(
        self, 
        metric_type: MetricType, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MetricData]:
        """Collect revenue metrics."""
        if metric_type != MetricType.REVENUE:
            return []
        
        metrics = []
        
        # Daily revenue breakdown
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = datetime.combine(current_date, datetime.max.time())
            
            daily_transactions = [
                t for t in self.revenue_engine.transactions
                if day_start <= t.created_at <= day_end
            ]
            
            daily_revenue = sum(t.amount for t in daily_transactions)
            
            metric = MetricData(
                metric_id=f"daily_revenue_{current_date}",
                metric_type=MetricType.REVENUE,
                value=daily_revenue,
                dimensions={"date": current_date.isoformat()},
                timestamp=day_start
            )
            metrics.append(metric)
            
            current_date += timedelta(days=1)
        
        return metrics


class TransactionMetricCollector(MetricCollector):
    """Transaction metrics collector."""
    
    def __init__(self, revenue_engine):
        self.revenue_engine = revenue_engine
    
    async def collect_metrics(
        self, 
        metric_type: MetricType, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MetricData]:
        """Collect transaction metrics."""
        if metric_type != MetricType.TRANSACTIONS:
            return []
        
        period_transactions = [
            t for t in self.revenue_engine.transactions
            if start_date <= t.created_at <= end_date
        ]
        
        metrics = []
        
        # Total transactions
        total_metric = MetricData(
            metric_id="total_transactions",
            metric_type=MetricType.TRANSACTIONS,
            value=len(period_transactions),
            timestamp=start_date
        )
        metrics.append(total_metric)
        
        # Average transaction value
        if period_transactions:
            avg_value = sum(t.amount for t in period_transactions) / len(period_transactions)
            avg_metric = MetricData(
                metric_id="avg_transaction_value",
                metric_type=MetricType.TRANSACTIONS,
                value=avg_value,
                timestamp=start_date
            )
            metrics.append(avg_metric)
        
        return metrics


class ConversionMetricCollector(MetricCollector):
    """Conversion metrics collector."""
    
    def __init__(self, user_data_source):
        self.user_data_source = user_data_source
    
    async def collect_metrics(
        self, 
        metric_type: MetricType, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MetricData]:
        """Collect conversion metrics."""
        if metric_type != MetricType.CONVERSION:
            return []
        
        # Simulated conversion data
        metrics = []
        
        conversion_rate = MetricData(
            metric_id="overall_conversion_rate",
            metric_type=MetricType.CONVERSION,
            value=0.05,  # 5% conversion rate
            timestamp=start_date
        )
        metrics.append(conversion_rate)
        
        return metrics


class AnalyticsEngine:
    """
    Professional monetization analytics engine.
    Provides comprehensive analytics, reporting, and insights.
    """
    
    def __init__(self):
        self.metric_collectors: Dict[MetricType, MetricCollector] = {}
        self.cached_reports: Dict[str, AnalyticsReport] = {}
        self.metric_storage: List[MetricData] = []
        self.report_templates: Dict[ReportType, Dict[str, Any]] = {}
        self.is_initialized = False
    
    async def initialize(self, revenue_engine, subscription_manager, commission_manager) -> bool:
        """Initialize analytics engine with data sources."""
        try:
            # Initialize metric collectors
            self.metric_collectors[MetricType.REVENUE] = RevenueMetricCollector(revenue_engine)
            self.metric_collectors[MetricType.TRANSACTIONS] = TransactionMetricCollector(revenue_engine)
            self.metric_collectors[MetricType.CONVERSION] = ConversionMetricCollector(None)
            
            # Store references to managers
            self.revenue_engine = revenue_engine
            self.subscription_manager = subscription_manager
            self.commission_manager = commission_manager
            
            # Initialize report templates
            self._initialize_report_templates()
            
            self.is_initialized = True
            logger.info("Analytics engine initialized")
            return True
            
        except Exception as e:
            logger.error(f"Analytics engine initialization failed: {e}")
            return False
    
    async def collect_metrics(
        self, 
        metric_types: List[MetricType], 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MetricData]:
        """Collect metrics for specified types and period."""
        if not self.is_initialized:
            raise RuntimeError("Analytics engine not initialized")
        
        all_metrics = []
        
        for metric_type in metric_types:
            collector = self.metric_collectors.get(metric_type)
            if collector:
                try:
                    metrics = await collector.collect_metrics(metric_type, start_date, end_date)
                    all_metrics.extend(metrics)
                    
                    # Store metrics
                    self.metric_storage.extend(metrics)
                    
                except Exception as e:
                    logger.error(f"Metric collection failed for {metric_type}: {e}")
        
        logger.info(f"Collected {len(all_metrics)} metrics")
        return all_metrics
    
    async def generate_report(
        self, 
        report_type: ReportType, 
        start_date: datetime, 
        end_date: datetime,
        user_id: Optional[str] = None
    ) -> AnalyticsReport:
        """Generate comprehensive analytics report."""
        if not self.is_initialized:
            await self.initialize(None, None, None)  # Basic initialization
        
        try:
            report_id = f"{report_type.value}_{start_date.date()}_{end_date.date()}"
            if user_id:
                report_id += f"_{user_id}"
            
            # Check cache
            if report_id in self.cached_reports:
                cached_report = self.cached_reports[report_id]
                if (datetime.utcnow() - cached_report.generated_at).hours < 1:
                    return cached_report
            
            # Generate new report
            report = AnalyticsReport(
                report_id=report_id,
                title=f"{report_type.value.title()} Analytics Report",
                report_type=report_type,
                period_start=start_date,
                period_end=end_date
            )
            
            # Add revenue section
            revenue_section = await self._generate_revenue_section(start_date, end_date, user_id)
            report.add_section(revenue_section)
            
            # Add transaction section
            transaction_section = await self._generate_transaction_section(start_date, end_date, user_id)
            report.add_section(transaction_section)
            
            # Add subscription section
            subscription_section = await self._generate_subscription_section(start_date, end_date, user_id)
            report.add_section(subscription_section)
            
            # Add commission section
            commission_section = await self._generate_commission_section(start_date, end_date, user_id)
            report.add_section(commission_section)
            
            # Add performance section
            performance_section = await self._generate_performance_section(start_date, end_date, user_id)
            report.add_section(performance_section)
            
            # Generate summary
            report.summary = await self._generate_report_summary(report)
            
            # Cache report
            self.cached_reports[report_id] = report
            
            logger.info(f"Analytics report generated: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            # Return empty report on error
            return AnalyticsReport(
                report_id="error_report",
                title="Error Report",
                report_type=report_type,
                period_start=start_date,
                period_end=end_date
            )
    
    async def get_real_time_metrics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get real-time monetization metrics."""
        try:
            now = datetime.utcnow()
            today_start = datetime.combine(now.date(), datetime.min.time())
            
            # Revenue metrics
            if hasattr(self, 'revenue_engine') and self.revenue_engine:
                daily_transactions = [
                    t for t in self.revenue_engine.transactions
                    if t.created_at >= today_start and (not user_id or t.user_id == user_id)
                ]
                
                daily_revenue = sum(t.amount for t in daily_transactions)
                transaction_count = len(daily_transactions)
            else:
                daily_revenue = Decimal("0")
                transaction_count = 0
            
            # Subscription metrics
            if hasattr(self, 'subscription_manager') and self.subscription_manager:
                active_subs = len([
                    s for s in self.subscription_manager.subscriptions.values()
                    if s.is_active() and (not user_id or s.user_id == user_id)
                ])
            else:
                active_subs = 0
            
            # Commission metrics
            if hasattr(self, 'commission_manager') and self.commission_manager:
                pending_commissions = len([
                    c for c in self.commission_manager.commissions.values()
                    if c.status.value == "pending" and (not user_id or c.affiliate_id == user_id)
                ])
            else:
                pending_commissions = 0
            
            return {
                "timestamp": now.isoformat(),
                "daily_revenue": float(daily_revenue),
                "daily_transactions": transaction_count,
                "active_subscriptions": active_subs,
                "pending_commissions": pending_commissions,
                "conversion_rate": 0.05,  # Placeholder
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Real-time metrics collection failed: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Metrics collection failed"
            }
    
    async def get_trend_analysis(
        self, 
        metric_type: MetricType, 
        days: int = 30,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze trends for specific metrics."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Collect historical data
            metrics = []
            if hasattr(self, 'revenue_engine') and self.revenue_engine and metric_type == MetricType.REVENUE:
                # Calculate daily revenue for trend analysis
                current_date = start_date.date()
                daily_values = []
                
                while current_date <= end_date.date():
                    day_start = datetime.combine(current_date, datetime.min.time())
                    day_end = datetime.combine(current_date, datetime.max.time())
                    
                    daily_transactions = [
                        t for t in self.revenue_engine.transactions
                        if day_start <= t.created_at <= day_end and (not user_id or t.user_id == user_id)
                    ]
                    
                    daily_revenue = float(sum(t.amount for t in daily_transactions))
                    daily_values.append(daily_revenue)
                    
                    current_date += timedelta(days=1)
                
                # Calculate trend
                if len(daily_values) >= 2:
                    trend_direction = "up" if daily_values[-1] > daily_values[0] else "down"
                    if len(daily_values) > 1:
                        avg_change = (daily_values[-1] - daily_values[0]) / len(daily_values)
                    else:
                        avg_change = 0
                else:
                    trend_direction = "stable"
                    avg_change = 0
                
                return {
                    "metric_type": metric_type.value,
                    "period_days": days,
                    "trend_direction": trend_direction,
                    "average_daily_change": avg_change,
                    "total_change": daily_values[-1] - daily_values[0] if daily_values else 0,
                    "data_points": len(daily_values),
                    "daily_values": daily_values,
                    "user_id": user_id
                }
            
            return {
                "metric_type": metric_type.value,
                "period_days": days,
                "error": "Insufficient data for trend analysis"
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {
                "metric_type": metric_type.value,
                "error": str(e)
            }
    
    async def get_performance_insights(self, user_id: Optional[str] = None) -> List[str]:
        """Generate performance insights and recommendations."""
        insights = []
        
        try:
            # Revenue insights
            if hasattr(self, 'revenue_engine') and self.revenue_engine:
                recent_transactions = [
                    t for t in self.revenue_engine.transactions
                    if t.created_at >= datetime.utcnow() - timedelta(days=30) and (not user_id or t.user_id == user_id)
                ]
                
                if recent_transactions:
                    avg_transaction = sum(t.amount for t in recent_transactions) / len(recent_transactions)
                    
                    if avg_transaction < Decimal("10"):
                        insights.append("Consider implementing higher-value content packages to increase average transaction value")
                    
                    if len(recent_transactions) < 10:
                        insights.append("Focus on marketing and user acquisition to increase transaction volume")
                
                # Stream type analysis
                stream_performance = {}
                for transaction in recent_transactions:
                    stream_type = transaction.stream_type
                    if stream_type not in stream_performance:
                        stream_performance[stream_type] = {"revenue": Decimal("0"), "count": 0}
                    stream_performance[stream_type]["revenue"] += transaction.amount
                    stream_performance[stream_type]["count"] += 1
                
                if stream_performance:
                    best_stream = max(stream_performance.items(), key=lambda x: x[1]["revenue"])
                    insights.append(f"Your best performing revenue stream is {best_stream[0].value} - consider expanding this area")
            
            # Subscription insights
            if hasattr(self, 'subscription_manager') and self.subscription_manager:
                user_subs = [
                    s for s in self.subscription_manager.subscriptions.values()
                    if not user_id or s.user_id == user_id
                ]
                
                if not user_subs:
                    insights.append("Consider offering subscription-based services for predictable recurring revenue")
                else:
                    trial_subs = [s for s in user_subs if s.is_trial()]
                    if len(trial_subs) > len(user_subs) * 0.3:
                        insights.append("High trial-to-paid conversion opportunity - optimize onboarding experience")
            
            # Commission insights
            if hasattr(self, 'commission_manager') and self.commission_manager:
                if user_id:
                    affiliate = self.commission_manager.get_affiliate_by_code(user_id)
                    if not affiliate:
                        insights.append("Join our affiliate program to earn additional revenue through referrals")
            
            if not insights:
                insights.append("Your monetization performance is on track - keep up the great work!")
            
        except Exception as e:
            logger.error(f"Performance insights generation failed: {e}")
            insights.append("Unable to generate insights at this time")
        
        return insights
    
    async def export_report(self, report_id: str, format_type: str = "json") -> Optional[str]:
        """Export report in specified format."""
        report = self.cached_reports.get(report_id)
        if not report:
            return None
        
        try:
            if format_type.lower() == "json":
                return json.dumps(report.to_dict(), indent=2, default=str)
            elif format_type.lower() == "csv":
                # Simplified CSV export
                csv_data = "Section,Metric,Value,Timestamp\n"
                for section in report.sections:
                    for metric in section.metrics:
                        csv_data += f"{section.title},{metric.metric_id},{metric.value},{metric.timestamp}\n"
                return csv_data
            else:
                return json.dumps(report.to_dict(), indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Report export failed: {e}")
            return None
    
    async def _generate_revenue_section(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        user_id: Optional[str]
    ) -> ReportSection:
        """Generate revenue analytics section."""
        section = ReportSection(
            section_id="revenue_analytics",
            title="Revenue Analytics"
        )
        
        try:
            if hasattr(self, 'revenue_engine') and self.revenue_engine:
                period_transactions = [
                    t for t in self.revenue_engine.transactions
                    if start_date <= t.created_at <= end_date and (not user_id or t.user_id == user_id)
                ]
                
                total_revenue = sum(t.amount for t in period_transactions)
                
                # Total revenue metric
                revenue_metric = MetricData(
                    metric_id="total_revenue",
                    metric_type=MetricType.REVENUE,
                    value=total_revenue,
                    dimensions={"period": f"{start_date.date()} to {end_date.date()}"}
                )
                section.add_metric(revenue_metric)
                
                # Revenue insights
                if total_revenue > Decimal("1000"):
                    section.add_insight("Strong revenue performance this period")
                elif total_revenue > Decimal("100"):
                    section.add_insight("Good revenue growth potential")
                else:
                    section.add_insight("Focus on revenue optimization opportunities")
                
                # Recommendations
                if len(period_transactions) < 50:
                    section.add_recommendation("Increase marketing efforts to drive more transactions")
        
        except Exception as e:
            logger.error(f"Revenue section generation failed: {e}")
        
        return section
    
    async def _generate_transaction_section(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        user_id: Optional[str]
    ) -> ReportSection:
        """Generate transaction analytics section."""
        section = ReportSection(
            section_id="transaction_analytics",
            title="Transaction Analytics"
        )
        
        try:
            if hasattr(self, 'revenue_engine') and self.revenue_engine:
                period_transactions = [
                    t for t in self.revenue_engine.transactions
                    if start_date <= t.created_at <= end_date and (not user_id or t.user_id == user_id)
                ]
                
                transaction_count = len(period_transactions)
                
                # Transaction count metric
                count_metric = MetricData(
                    metric_id="transaction_count",
                    metric_type=MetricType.TRANSACTIONS,
                    value=transaction_count
                )
                section.add_metric(count_metric)
                
                if transaction_count > 0:
                    avg_value = sum(t.amount for t in period_transactions) / transaction_count
                    avg_metric = MetricData(
                        metric_id="avg_transaction_value",
                        metric_type=MetricType.TRANSACTIONS,
                        value=avg_value
                    )
                    section.add_metric(avg_metric)
        
        except Exception as e:
            logger.error(f"Transaction section generation failed: {e}")
        
        return section
    
    async def _generate_subscription_section(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        user_id: Optional[str]
    ) -> ReportSection:
        """Generate subscription analytics section."""
        section = ReportSection(
            section_id="subscription_analytics",
            title="Subscription Analytics"
        )
        
        try:
            if hasattr(self, 'subscription_manager') and self.subscription_manager:
                user_subs = [
                    s for s in self.subscription_manager.subscriptions.values()
                    if (not user_id or s.user_id == user_id) and 
                    start_date <= s.created_at <= end_date
                ]
                
                active_count = len([s for s in user_subs if s.is_active()])
                
                # Active subscriptions metric
                active_metric = MetricData(
                    metric_id="active_subscriptions",
                    metric_type=MetricType.USERS,
                    value=active_count
                )
                section.add_metric(active_metric)
        
        except Exception as e:
            logger.error(f"Subscription section generation failed: {e}")
        
        return section
    
    async def _generate_commission_section(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        user_id: Optional[str]
    ) -> ReportSection:
        """Generate commission analytics section."""
        section = ReportSection(
            section_id="commission_analytics",
            title="Commission Analytics"
        )
        
        try:
            if hasattr(self, 'commission_manager') and self.commission_manager:
                period_commissions = [
                    c for c in self.commission_manager.commissions.values()
                    if start_date <= c.created_at <= end_date and (not user_id or c.affiliate_id == user_id)
                ]
                
                total_commissions = sum(c.commission_amount for c in period_commissions)
                
                # Total commissions metric
                commission_metric = MetricData(
                    metric_id="total_commissions",
                    metric_type=MetricType.REVENUE,
                    value=total_commissions
                )
                section.add_metric(commission_metric)
        
        except Exception as e:
            logger.error(f"Commission section generation failed: {e}")
        
        return section
    
    async def _generate_performance_section(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        user_id: Optional[str]
    ) -> ReportSection:
        """Generate performance analytics section."""
        section = ReportSection(
            section_id="performance_analytics",
            title="Performance Analytics"
        )
        
        try:
            # Performance score calculation
            performance_score = 75.0  # Placeholder calculation
            
            performance_metric = MetricData(
                metric_id="performance_score",
                metric_type=MetricType.PERFORMANCE,
                value=performance_score
            )
            section.add_metric(performance_metric)
            
            if performance_score > 80:
                section.add_insight("Excellent performance this period")
            elif performance_score > 60:
                section.add_insight("Good performance with room for improvement")
            else:
                section.add_insight("Performance needs attention")
        
        except Exception as e:
            logger.error(f"Performance section generation failed: {e}")
        
        return section
    
    async def _generate_report_summary(self, report: AnalyticsReport) -> Dict[str, Any]:
        """Generate report summary."""
        try:
            summary = {
                "total_sections": len(report.sections),
                "total_metrics": sum(len(section.metrics) for section in report.sections),
                "key_highlights": [],
                "period_summary": {
                    "start": report.period_start.isoformat(),
                    "end": report.period_end.isoformat(),
                    "days": (report.period_end - report.period_start).days
                }
            }
            
            # Extract key metrics for highlights
            for section in report.sections:
                for metric in section.metrics:
                    if metric.metric_id in ["total_revenue", "transaction_count", "active_subscriptions"]:
                        summary["key_highlights"].append({
                            "metric": metric.metric_id,
                            "value": metric.value,
                            "type": metric.metric_type.value
                        })
            
            return summary
            
        except Exception as e:
            logger.error(f"Report summary generation failed: {e}")
            return {"error": "Summary generation failed"}
    
    def _initialize_report_templates(self) -> None:
        """Initialize report templates."""
        self.report_templates = {
            ReportType.DAILY: {
                "sections": ["revenue_analytics", "transaction_analytics"],
                "metrics": [MetricType.REVENUE, MetricType.TRANSACTIONS]
            },
            ReportType.WEEKLY: {
                "sections": ["revenue_analytics", "transaction_analytics", "subscription_analytics"],
                "metrics": [MetricType.REVENUE, MetricType.TRANSACTIONS, MetricType.USERS]
            },
            ReportType.MONTHLY: {
                "sections": ["revenue_analytics", "transaction_analytics", "subscription_analytics", "commission_analytics"],
                "metrics": [MetricType.REVENUE, MetricType.TRANSACTIONS, MetricType.USERS, MetricType.CONVERSION]
            }
        }
