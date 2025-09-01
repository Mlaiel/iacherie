"""Revenue Metrics Collector - Advanced Financial Analytics
=======================================================

Comprehensive revenue tracking and financial performance analytics
for content monetization optimization and business intelligence.

Features:
- Revenue tracking across all monetization channels
- Financial performance analysis and forecasting
- Creator earnings optimization
- ROI analysis and cost attribution
- Payment processing analytics

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from collections import defaultdict
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, case

from ...core.database import get_database_session
from ...models.monetization import Revenue, Payment, Subscription, Commission
from ...models.content import Content, ContentRevenue
from ...models.users import User
from ...models.protection import ProtectionEvent


class RevenueCategory(Enum):
    """
Revenue analytics categories."""

    TOTAL_REVENUE = "total_revenue"
    CONTENT_REVENUE = "content_revenue"
    SUBSCRIPTION_REVENUE = "subscription_revenue"
    COMMISSION_REVENUE = "commission_revenue"
    PROTECTION_REVENUE = "protection_revenue"
    PAYMENT_ANALYTICS = "payment_analytics"


class RevenueSource(Enum):
    """Revenue source types."""

    CONTENT_LICENSING = "content_licensing"
    SUBSCRIPTION_FEES = "subscription_fees"
    PLATFORM_COMMISSION = "platform_commission"
    PROTECTION_SERVICES = "protection_services"
    PREMIUM_FEATURES = "premium_features"
    ADVERTISING = "advertising"


@dataclass
class RevenueMetric:
    """Structured revenue metric data."""
    metric_name: str
    value: Decimal
    category: RevenueCategory
    source: Optional[RevenueSource]
    timestamp: datetime
    currency: str = "EUR"
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FinancialProfile:
    """Comprehensive financial performance profile."""
    entity_id: str  # User ID or Content ID
    entity_type: str  # 'user' or 'content'
    total_revenue: Decimal
    monthly_recurring_revenue: Decimal
    average_order_value: Decimal
    revenue_growth_rate: float
    profitability_score: float
    revenue_sources: Dict[str, Decimal]
    payment_success_rate: float
    forecasted_revenue: Decimal
    last_updated: datetime


class RevenueMetricsCollector:
    """
    Advanced revenue analytics and financial intelligence system.
    
    Provides comprehensive insights into financial performance,
    monetization effectiveness, and revenue optimization opportunities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._exchange_rates = {"EUR": 1.0, "USD": 0.85, "GBP": 1.15}
        self._revenue_cache = {}
        
    async def collect_revenue_metrics(
        self,
        user_id: Optional[str] = None,
        content_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[RevenueMetric]:
        """
        Collect comprehensive revenue metrics.
        
        Args:
            user_id: Specific user to analyze
            content_id: Specific content to analyze
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            List of revenue metrics
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
            
        try:
            metrics = []
            
            # Collect total revenue metrics
            total_revenue_metrics = await self._collect_total_revenue_metrics(
                user_id, content_id, start_date, end_date
            )
            metrics.extend(total_revenue_metrics)
            
            # Collect content revenue metrics
            content_revenue_metrics = await self._collect_content_revenue_metrics(
                user_id, content_id, start_date, end_date
            )
            metrics.extend(content_revenue_metrics)
            
            # Collect subscription revenue metrics
            subscription_metrics = await self._collect_subscription_revenue_metrics(
                user_id, start_date, end_date
            )
            metrics.extend(subscription_metrics)
            
            # Collect commission metrics
            commission_metrics = await self._collect_commission_metrics(
                user_id, start_date, end_date
            )
            metrics.extend(commission_metrics)
            
            # Collect payment analytics
            payment_metrics = await self._collect_payment_analytics(
                user_id, start_date, end_date
            )
            metrics.extend(payment_metrics)
            
            self.logger.info(f"Collected {len(metrics)} revenue metrics")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting revenue metrics: {e}")
            raise
            
    async def _collect_total_revenue_metrics(
        self,
        user_id: Optional[str],
        content_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueMetric]:
        """Collect total revenue metrics across all sources."""
        
        async with get_database_session() as session:
            # Total revenue query
            base_query = select(
                func.sum(Revenue.amount).label('total_revenue'),
                func.count(Revenue.id).label('revenue_events'),
                func.avg(Revenue.amount).label('avg_revenue_per_event'),
                Revenue.currency,
                Revenue.source,
                func.date(Revenue.created_at).label('revenue_date'),
                func.sum(Revenue.amount).label('daily_revenue')
            ).where(
                and_(
                    Revenue.created_at >= start_date,
                    Revenue.created_at <= end_date,
                    Revenue.status == 'confirmed'
                )
            ).group_by(Revenue.currency, Revenue.source, func.date(Revenue.created_at))
            
            if user_id:
                base_query = base_query.where(Revenue.user_id == user_id)
            if content_id:
                base_query = base_query.where(Revenue.content_id == content_id)
                
            result = await session.execute(base_query)
            revenue_data = result.fetchall()
            
            metrics = []
            
            # Aggregate by currency and source
            currency_totals = defaultdict(Decimal)
            source_totals = defaultdict(Decimal)
            daily_revenues = []
            
            for row in revenue_data:
                amount = Decimal(str(row.total_revenue or 0))
                currency = row.currency or 'EUR'
                source = row.source
                
                # Convert to EUR for aggregation
                eur_amount = amount * Decimal(str(self._exchange_rates.get(currency, 1.0)))
                
                currency_totals[currency] += amount
                source_totals[source] += eur_amount
                daily_revenues.append({
                    'date': row.revenue_date,
                    'amount': eur_amount
                })
                
            # Calculate total revenue in EUR
            total_revenue_eur = sum(source_totals.values())
            
            # Calculate growth rate
            growth_rate = await self._calculate_revenue_growth_rate(
                user_id, content_id, start_date, end_date, session
            )
            
            # Revenue volatility
            revenue_volatility = self._calculate_revenue_volatility(daily_revenues)
            
            metrics.extend([
                RevenueMetric(
                    metric_name="total_revenue",
                    value=total_revenue_eur,
                    category=RevenueCategory.TOTAL_REVENUE,
                    timestamp=datetime.now(),
                    currency="EUR",
                    user_id=user_id,
                    content_id=content_id,
                    metadata={
                        "period_days": (end_date - start_date).days,
                        "currency_breakdown": dict(currency_totals),
                        "source_breakdown": dict(source_totals)
                    }
                ),
                RevenueMetric(
                    metric_name="revenue_growth_rate",
                    value=Decimal(str(growth_rate)),
                    category=RevenueCategory.TOTAL_REVENUE,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    content_id=content_id
                ),
                RevenueMetric(
                    metric_name="revenue_volatility",
                    value=Decimal(str(revenue_volatility)),
                    category=RevenueCategory.TOTAL_REVENUE,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    content_id=content_id
                )
            ])
            
            # Add source-specific metrics
            for source, amount in source_totals.items():
                if amount > 0:
                    try:
                        revenue_source = RevenueSource(source)
                    except ValueError:
                        revenue_source = None
                        
                    metrics.append(
                        RevenueMetric(
                            metric_name=f"revenue_from_{source}",
                            value=amount,
                            category=RevenueCategory.TOTAL_REVENUE,
                            source=revenue_source,
                            timestamp=datetime.now(),
                            user_id=user_id,
                            content_id=content_id
                        )
                    )
                    
            return metrics
            
    async def _calculate_revenue_growth_rate(
        self,
        user_id: Optional[str],
        content_id: Optional[str],
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> float:
        """Calculate revenue growth rate compared to previous period."""
        
        period_length = end_date - start_date
        previous_start = start_date - period_length
        previous_end = start_date
        
        # Current period revenue
        current_query = select(func.sum(Revenue.amount)).where(
            and_(
                Revenue.created_at >= start_date,
                Revenue.created_at <= end_date,
                Revenue.status == 'confirmed'
            )
        )
        
        # Previous period revenue
        previous_query = select(func.sum(Revenue.amount)).where(
            and_(
                Revenue.created_at >= previous_start,
                Revenue.created_at <= previous_end,
                Revenue.status == 'confirmed'
            )
        )
        
        if user_id:
            current_query = current_query.where(Revenue.user_id == user_id)
            previous_query = previous_query.where(Revenue.user_id == user_id)
        if content_id:
            current_query = current_query.where(Revenue.content_id == content_id)
            previous_query = previous_query.where(Revenue.content_id == content_id)
            
        current_result = await session.execute(current_query)
        previous_result = await session.execute(previous_query)
        
        current_revenue = float(current_result.scalar() or 0)
        previous_revenue = float(previous_result.scalar() or 0)
        
        if previous_revenue == 0:
            return 100.0 if current_revenue > 0 else 0.0
            
        growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
        return growth_rate
        
    def _calculate_revenue_volatility(self, daily_revenues: List[Dict]) -> float:
        """
Calculate revenue volatility (standard deviation)."""
        
        if len(daily_revenues) < 2:
            return 0.0
            
        amounts = [float(rev['amount']) for rev in daily_revenues]
        mean_revenue = np.mean(amounts)
        
        if mean_revenue == 0:
            return 0.0
            
        variance = np.var(amounts)
        volatility = (np.sqrt(variance) / mean_revenue) * 100
        
        return volatility
        
    async def _collect_content_revenue_metrics(
        self,
        user_id: Optional[str],
        content_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueMetric]:
        """
Collect content-specific revenue metrics."""
        
        async with get_database_session() as session:
            # Content revenue query
            content_query = select(
                ContentRevenue.content_id,
                Content.title,
                Content.content_type,
                func.sum(ContentRevenue.amount).label('content_revenue'),
                func.count(ContentRevenue.id).label('revenue_events'),
                func.avg(ContentRevenue.amount).label('avg_revenue_per_event'),
                func.count(ContentView.id).label('total_views')
            ).join(Content).outerjoin(ContentView).where(
                and_(
                    ContentRevenue.created_at >= start_date,
                    ContentRevenue.created_at <= end_date,
                    ContentRevenue.status == 'confirmed'
                )
            ).group_by(
                ContentRevenue.content_id, Content.title, Content.content_type
            )
            
            if user_id:
                content_query = content_query.where(Content.user_id == user_id)
            if content_id:
                content_query = content_query.where(ContentRevenue.content_id == content_id)
                
            result = await session.execute(content_query)
            content_data = result.fetchall()
            
            metrics = []
            
            for row in content_data:
                cid = row.content_id
                revenue = Decimal(str(row.content_revenue or 0))
                views = row.total_views or 0
                
                # Revenue per view
                rpv = revenue / max(views, 1)
                
                # Content performance score
                performance_score = self._calculate_content_performance_score(
                    revenue, views, row.revenue_events or 0
                )
                
                metrics.extend([
                    RevenueMetric(
                        metric_name="content_total_revenue",
                        value=revenue,
                        category=RevenueCategory.CONTENT_REVENUE,
                        timestamp=datetime.now(),
                        user_id=user_id,
                        content_id=cid,
                        metadata={
                            "title": row.title,
                            "content_type": row.content_type,
                            "revenue_events": row.revenue_events,
                            "total_views": views
                        }
                    ),
                    RevenueMetric(
                        metric_name="revenue_per_view",
                        value=rpv,
                        category=RevenueCategory.CONTENT_REVENUE,
                        timestamp=datetime.now(),
                        user_id=user_id,
                        content_id=cid
                    ),
                    RevenueMetric(
                        metric_name="content_performance_score",
                        value=Decimal(str(performance_score)),
                        category=RevenueCategory.CONTENT_REVENUE,
                        timestamp=datetime.now(),
                        user_id=user_id,
                        content_id=cid
                    )
                ])
                
            return metrics
            
    def _calculate_content_performance_score(
        self,
        revenue: Decimal,
        views: int,
        revenue_events: int
    ) -> float:
        """Calculate content revenue performance score."""
        
        if views == 0:
            return 0.0
            
        # Revenue per view score (0-50 points)
        rpv = float(revenue) / views
        rpv_score = min(rpv * 10000, 50)  # Normalize to 0-50
        
        # Revenue conversion score (0-30 points)
        conversion_rate = revenue_events / views
        conversion_score = min(conversion_rate * 3000, 30)  # Normalize to 0-30
        
        # Revenue magnitude score (0-20 points)
        magnitude_score = min(float(revenue) / 1000, 20)  # Normalize to 0-20
        
        total_score = rpv_score + conversion_score + magnitude_score
        return min(total_score, 100.0)
        
    async def _collect_subscription_revenue_metrics(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueMetric]:
        """
Collect subscription revenue metrics."""
        
        async with get_database_session() as session:
            # Subscription revenue query
            subscription_query = select(
                func.sum(Subscription.amount).label('subscription_revenue'),
                func.count(Subscription.id).label('active_subscriptions'),
                func.avg(Subscription.amount).label('avg_subscription_value'),
                Subscription.plan_type,
                func.count(
                    case(
                        (Subscription.status == 'active', 1),
                        else_=None
                    )
                ).label('active_count'),
                func.count(
                    case(
                        (Subscription.status == 'cancelled', 1),
                        else_=None
                    )
                ).label('cancelled_count')
            ).where(
                and_(
                    Subscription.created_at >= start_date,
                    Subscription.created_at <= end_date
                )
            ).group_by(Subscription.plan_type)
            
            if user_id:
                subscription_query = subscription_query.where(Subscription.user_id == user_id)
                
            result = await session.execute(subscription_query)
            subscription_data = result.fetchall()
            
            metrics = []
            
            for row in subscription_data:
                revenue = Decimal(str(row.subscription_revenue or 0))
                active_subs = row.active_count or 0
                cancelled_subs = row.cancelled_count or 0
                
                # Churn rate
                total_subs = active_subs + cancelled_subs
                churn_rate = (cancelled_subs / max(total_subs, 1)) * 100
                
                # Monthly recurring revenue (MRR)
                mrr = revenue  # Assuming monthly billing
                
                metrics.extend([
                    RevenueMetric(
                        metric_name="subscription_revenue",
                        value=revenue,
                        category=RevenueCategory.SUBSCRIPTION_REVENUE,
                        source=RevenueSource.SUBSCRIPTION_FEES,
                        timestamp=datetime.now(),
                        user_id=user_id,
                        metadata={
                            "plan_type": row.plan_type,
                            "active_subscriptions": active_subs,
                            "cancelled_subscriptions": cancelled_subs
                        }
                    ),
                    RevenueMetric(
                        metric_name="monthly_recurring_revenue",
                        value=mrr,
                        category=RevenueCategory.SUBSCRIPTION_REVENUE,
                        timestamp=datetime.now(),
                        user_id=user_id
                    ),
                    RevenueMetric(
                        metric_name="subscription_churn_rate",
                        value=Decimal(str(churn_rate)),
                        category=RevenueCategory.SUBSCRIPTION_REVENUE,
                        timestamp=datetime.now(),
                        user_id=user_id
                    )
                ])
                
            return metrics
            
    async def _collect_commission_metrics(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueMetric]:
        """Collect platform commission metrics."""
        
        async with get_database_session() as session:
            # Commission revenue query
            commission_query = select(
                func.sum(Commission.amount).label('commission_revenue'),
                func.count(Commission.id).label('commission_events'),
                func.avg(Commission.rate).label('avg_commission_rate'),
                Commission.commission_type,
                func.sum(Commission.gross_amount).label('gross_revenue')
            ).where(
                and_(
                    Commission.created_at >= start_date,
                    Commission.created_at <= end_date,
                    Commission.status == 'confirmed'
                )
            ).group_by(Commission.commission_type)
            
            if user_id:
                commission_query = commission_query.where(Commission.user_id == user_id)
                
            result = await session.execute(commission_query)
            commission_data = result.fetchall()
            
            metrics = []
            
            for row in commission_data:
                commission_revenue = Decimal(str(row.commission_revenue or 0))
                gross_revenue = Decimal(str(row.gross_revenue or 0))
                avg_rate = float(row.avg_commission_rate or 0)
                
                # Commission efficiency
                efficiency = (float(commission_revenue) / max(float(gross_revenue), 1)) * 100
                
                metrics.extend([
                    RevenueMetric(
                        metric_name="commission_revenue",
                        value=commission_revenue,
                        category=RevenueCategory.COMMISSION_REVENUE,
                        source=RevenueSource.PLATFORM_COMMISSION,
                        timestamp=datetime.now(),
                        user_id=user_id,
                        metadata={
                            "commission_type": row.commission_type,
                            "commission_events": row.commission_events,
                            "gross_revenue": gross_revenue
                        }
                    ),
                    RevenueMetric(
                        metric_name="commission_rate_avg",
                        value=Decimal(str(avg_rate)),
                        category=RevenueCategory.COMMISSION_REVENUE,
                        timestamp=datetime.now(),
                        user_id=user_id
                    ),
                    RevenueMetric(
                        metric_name="commission_efficiency",
                        value=Decimal(str(efficiency)),
                        category=RevenueCategory.COMMISSION_REVENUE,
                        timestamp=datetime.now(),
                        user_id=user_id
                    )
                ])
                
            return metrics
            
    async def _collect_payment_analytics(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueMetric]:
        """Collect payment processing analytics."""
        
        async with get_database_session() as session:
            # Payment analytics query
            payment_query = select(
                func.count(Payment.id).label('total_payments'),
                func.count(
                    case(
                        (Payment.status == 'completed', 1),
                        else_=None
                    )
                ).label('successful_payments'),
                func.count(
                    case(
                        (Payment.status == 'failed', 1),
                        else_=None
                    )
                ).label('failed_payments'),
                func.sum(Payment.amount).label('payment_volume'),
                func.avg(Payment.amount).label('avg_payment_amount'),
                func.sum(Payment.fees).label('total_fees'),
                Payment.payment_method,
                Payment.currency
            ).where(
                and_(
                    Payment.created_at >= start_date,
                    Payment.created_at <= end_date
                )
            ).group_by(Payment.payment_method, Payment.currency)
            
            if user_id:
                payment_query = payment_query.where(Payment.user_id == user_id)
                
            result = await session.execute(payment_query)
            payment_data = result.fetchall()
            
            metrics = []
            
            for row in payment_data:
                total_payments = row.total_payments or 0
                successful_payments = row.successful_payments or 0
                failed_payments = row.failed_payments or 0
                payment_volume = Decimal(str(row.payment_volume or 0))
                total_fees = Decimal(str(row.total_fees or 0))
                
                # Payment success rate
                success_rate = (successful_payments / max(total_payments, 1)) * 100
                
                # Payment failure rate
                failure_rate = (failed_payments / max(total_payments, 1)) * 100
                
                # Fee percentage
                fee_percentage = (float(total_fees) / max(float(payment_volume), 1)) * 100
                
                metrics.extend([
                    RevenueMetric(
                        metric_name="payment_volume",
                        value=payment_volume,
                        category=RevenueCategory.PAYMENT_ANALYTICS,
                        timestamp=datetime.now(),
                        currency=row.currency or 'EUR',
                        user_id=user_id,
                        metadata={
                            "payment_method": row.payment_method,
                            "total_payments": total_payments,
                            "successful_payments": successful_payments
                        }
                    ),
                    RevenueMetric(
                        metric_name="payment_success_rate",
                        value=Decimal(str(success_rate)),
                        category=RevenueCategory.PAYMENT_ANALYTICS,
                        timestamp=datetime.now(),
                        user_id=user_id
                    ),
                    RevenueMetric(
                        metric_name="payment_failure_rate",
                        value=Decimal(str(failure_rate)),
                        category=RevenueCategory.PAYMENT_ANALYTICS,
                        timestamp=datetime.now(),
                        user_id=user_id
                    ),
                    RevenueMetric(
                        metric_name="payment_fee_percentage",
                        value=Decimal(str(fee_percentage)),
                        category=RevenueCategory.PAYMENT_ANALYTICS,
                        timestamp=datetime.now(),
                        user_id=user_id,
                        metadata={
                            "total_fees": total_fees
                        }
                    )
                ])
                
            return metrics
            
    async def generate_financial_profiles(
        self,
        entity_ids: Optional[List[str]] = None,
        entity_type: str = "user"
    ) -> List[FinancialProfile]:
        """Generate comprehensive financial performance profiles."""
        
        try:
            # Collect revenue metrics
            revenue_metrics = await self.collect_revenue_metrics()
            
            # Group metrics by entity
            entity_metrics = defaultdict(list)
            for metric in revenue_metrics:
                if entity_type == "user" and metric.user_id:
                    entity_metrics[metric.user_id].append(metric)
                elif entity_type == "content" and metric.content_id:
                    entity_metrics[metric.content_id].append(metric)
                    
            profiles = []
            
            for entity_id, metrics in entity_metrics.items():
                if entity_ids and entity_id not in entity_ids:
                    continue
                    
                # Calculate profile components
                total_revenue = self._extract_total_revenue(metrics)
                mrr = self._extract_mrr(metrics)
                aov = self._calculate_average_order_value(metrics)
                growth_rate = self._extract_growth_rate(metrics)
                profitability = self._calculate_profitability_score(metrics)
                revenue_sources = self._extract_revenue_sources(metrics)
                payment_success_rate = self._extract_payment_success_rate(metrics)
                forecast = await self._forecast_revenue(entity_id, entity_type, metrics)
                
                profile = FinancialProfile(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    total_revenue=total_revenue,
                    monthly_recurring_revenue=mrr,
                    average_order_value=aov,
                    revenue_growth_rate=growth_rate,
                    profitability_score=profitability,
                    revenue_sources=revenue_sources,
                    payment_success_rate=payment_success_rate,
                    forecasted_revenue=forecast,
                    last_updated=datetime.now()
                )
                
                profiles.append(profile)
                
            self.logger.info(f"Generated {len(profiles)} financial profiles")
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error generating financial profiles: {e}")
            raise
            
    def _extract_total_revenue(self, metrics: List[RevenueMetric]) -> Decimal:
        """Extract total revenue from metrics."""
        for metric in metrics:
            if metric.metric_name == "total_revenue":
                return metric.value
        return Decimal('0')
        
    def _extract_mrr(self, metrics: List[RevenueMetric]) -> Decimal:
        """Extract monthly recurring revenue from metrics."""
        for metric in metrics:
            if metric.metric_name == "monthly_recurring_revenue":
                return metric.value
        return Decimal('0')
        
    def _calculate_average_order_value(self, metrics: List[RevenueMetric]) -> Decimal:
        """Calculate average order value from metrics."""
        total_revenue = Decimal('0')
        total_events = 0
        
        for metric in metrics:
            if "revenue" in metric.metric_name and metric.metadata:
                events = metric.metadata.get('revenue_events', 0)
                if events > 0:
                    total_revenue += metric.value
                    total_events += events
                    
        if total_events > 0:
            return total_revenue / total_events
        return Decimal('0')
        
    def _extract_growth_rate(self, metrics: List[RevenueMetric]) -> float:
        """Extract revenue growth rate from metrics."""
        for metric in metrics:
            if metric.metric_name == "revenue_growth_rate":
                return float(metric.value)
        return 0.0
        
    def _calculate_profitability_score(self, metrics: List[RevenueMetric]) -> float:
        """Calculate profitability score from metrics."""
        total_revenue = Decimal('0')
        total_fees = Decimal('0')
        
        for metric in metrics:
            if metric.metric_name == "total_revenue":
                total_revenue = metric.value
            elif metric.metric_name == "payment_fee_percentage":
                fee_percentage = float(metric.value)
                total_fees = total_revenue * (Decimal(str(fee_percentage)) / 100)
                
        if total_revenue > 0:
            net_revenue = total_revenue - total_fees
            profitability = (float(net_revenue) / float(total_revenue)) * 100
            return max(profitability, 0.0)
        return 0.0
        
    def _extract_revenue_sources(self, metrics: List[RevenueMetric]) -> Dict[str, Decimal]:
        """Extract revenue breakdown by source."""
        sources = {}
        
        for metric in metrics:
            if metric.source and metric.metric_name.startswith("revenue_from_"):
                sources[metric.source.value] = metric.value
                
        return sources
        
    def _extract_payment_success_rate(self, metrics: List[RevenueMetric]) -> float:
        """Extract payment success rate from metrics."""
        for metric in metrics:
            if metric.metric_name == "payment_success_rate":
                return float(metric.value)
        return 100.0  # Default to 100% if no payment data
        
    async def _forecast_revenue(
        self,
        entity_id: str,
        entity_type: str,
        metrics: List[RevenueMetric]
    ) -> Decimal:
        """Forecast future revenue based on historical trends."""
        
        # Simple linear projection based on growth rate
        # In production, this would use more sophisticated ML models
        
        total_revenue = self._extract_total_revenue(metrics)
        growth_rate = self._extract_growth_rate(metrics)
        
        # Project 3 months forward
        months_forward = 3
        monthly_growth = (growth_rate / 100) / 12  # Convert annual to monthly
        
        forecasted_revenue = total_revenue
        for _ in range(months_forward):
            forecasted_revenue *= (1 + Decimal(str(monthly_growth)))
            
        return forecasted_revenue
