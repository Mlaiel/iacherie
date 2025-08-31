"""Billing Analytics Engine - Comprehensive billing analytics and insights
=======================================================================

Advanced analytics engine providing deep insights into billing performance,
revenue patterns, payment trends, and business intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException
import json
import numpy as np

logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    """Types of analytics"""
    REVENUE = "revenue"
    PAYMENT_TRENDS = "payment_trends"
    CUSTOMER_BEHAVIOR = "customer_behavior"
    SUBSCRIPTION_METRICS = "subscription_metrics"
    COMMISSION_ANALYSIS = "commission_analysis"

class TimeFrame(Enum):
    """Analytics time frames"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class RevenueMetrics:
    """Revenue analytics metrics"""
    total_revenue: Decimal
    recurring_revenue: Decimal
    one_time_revenue: Decimal
    growth_rate: Decimal
    average_order_value: Decimal
    customer_lifetime_value: Decimal

@dataclass
class PaymentTrendMetrics:
    """Payment trend metrics"""
    success_rate: Decimal
    failure_rate: Decimal
    chargeback_rate: Decimal
    refund_rate: Decimal
    average_processing_time: float
    preferred_payment_methods: Dict[str, int]

class BillingAnalyticsEngine:
    """
    Advanced billing analytics engine providing comprehensive insights
    into revenue patterns, customer behavior, and payment trends.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        
    async def initialize(self) -> None:
        """Initialize billing analytics engine"""
        try:
            await self._setup_database_tables()
            await self._setup_analytics_cache()
            logger.info("Billing Analytics Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Billing Analytics Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for analytics"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics_cache (
                    id SERIAL PRIMARY KEY,
                    cache_key VARCHAR(255) UNIQUE NOT NULL,
                    analytics_type VARCHAR(30) NOT NULL,
                    time_frame VARCHAR(20) NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP NOT NULL,
                    INDEX idx_analytics_cache_key (cache_key, expires_at),
                    INDEX idx_analytics_type_frame (analytics_type, time_frame)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS revenue_snapshots (
                    id SERIAL PRIMARY KEY,
                    snapshot_date DATE NOT NULL,
                    total_revenue DECIMAL(15,2) NOT NULL,
                    recurring_revenue DECIMAL(15,2) NOT NULL,
                    one_time_revenue DECIMAL(15,2) NOT NULL,
                    new_customer_revenue DECIMAL(15,2) NOT NULL,
                    customer_count INTEGER NOT NULL,
                    transaction_count INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(snapshot_date)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics_reports (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(100) UNIQUE NOT NULL,
                    report_type VARCHAR(30) NOT NULL,
                    time_frame VARCHAR(20) NOT NULL,
                    period_start DATE NOT NULL,
                    period_end DATE NOT NULL,
                    report_data JSONB NOT NULL,
                    generated_at TIMESTAMP DEFAULT NOW()
                );
            """)

    async def _setup_analytics_cache(self) -> None:
        """Setup analytics cache settings"""
        try:
            # Cache expiry settings (in seconds)
            cache_settings = {
                'revenue_daily': 3600,      # 1 hour
                'revenue_weekly': 7200,     # 2 hours
                'revenue_monthly': 21600,   # 6 hours
                'payment_trends': 1800,     # 30 minutes
                'customer_behavior': 3600,  # 1 hour
            }
            
            for key, expiry in cache_settings.items():
                self.redis.setex(f"cache_expiry_{key}", 86400, expiry)
                
        except Exception as e:
            logger.error(f"Failed to setup analytics cache: {e}")

    async def generate_revenue_analytics(self, start_date: datetime, end_date: datetime,
                                       time_frame: TimeFrame = TimeFrame.DAILY) -> Dict[str, Any]:
        """Generate comprehensive revenue analytics"""
        try:
            # Check cache first
            cache_key = f"revenue_{time_frame.value}_{start_date.date()}_{end_date.date()}"
            cached_data = await self._get_cached_analytics(cache_key)
            if cached_data:
                return cached_data
            
            async with self.db_pool.acquire() as conn:
                # Revenue summary
                revenue_summary = await self._calculate_revenue_summary(conn, start_date, end_date)
                
                # Time-based revenue breakdown
                time_breakdown = await self._get_revenue_breakdown(conn, start_date, end_date, time_frame)
                
                # Revenue by payment method
                payment_method_revenue = await conn.fetch("""
                    SELECT 
                        payment_method,
                        COUNT(*) as transaction_count,
                        SUM(amount) as total_revenue,
                        AVG(amount) as avg_transaction
                    FROM payments 
                    WHERE created_at BETWEEN $1 AND $2
                    AND payment_status = 'completed'
                    GROUP BY payment_method
                    ORDER BY total_revenue DESC
                """, start_date, end_date)
                
                # Revenue by customer segment
                customer_segments = await conn.fetch("""
                    SELECT 
                        CASE 
                            WHEN customer_lifetime_value >= 1000 THEN 'high_value'
                            WHEN customer_lifetime_value >= 500 THEN 'medium_value'
                            ELSE 'low_value'
                        END as segment,
                        COUNT(DISTINCT customer_id) as customer_count,
                        SUM(amount) as segment_revenue
                    FROM payments p
                    JOIN (
                        SELECT customer_id, SUM(amount) as customer_lifetime_value
                        FROM payments 
                        WHERE payment_status = 'completed'
                        GROUP BY customer_id
                    ) clv ON p.customer_id = clv.customer_id
                    WHERE p.created_at BETWEEN $1 AND $2
                    AND p.payment_status = 'completed'
                    GROUP BY segment
                """, start_date, end_date)
                
                # Growth metrics
                growth_metrics = await self._calculate_growth_metrics(conn, start_date, end_date)
                
                analytics_data = {
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat(),
                        'time_frame': time_frame.value
                    },
                    'revenue_summary': revenue_summary,
                    'time_breakdown': [
                        {
                            'period': period['period'].isoformat() if hasattr(period['period'], 'isoformat') else str(period['period']),
                            'revenue': float(period['revenue']),
                            'transaction_count': int(period['transaction_count']),
                            'avg_transaction': float(period['avg_transaction'])
                        }
                        for period in time_breakdown
                    ],
                    'payment_method_breakdown': [
                        {
                            'method': row['payment_method'],
                            'transaction_count': int(row['transaction_count']),
                            'revenue': float(row['total_revenue']),
                            'avg_transaction': float(row['avg_transaction'])
                        }
                        for row in payment_method_revenue
                    ],
                    'customer_segments': [
                        {
                            'segment': row['segment'],
                            'customer_count': int(row['customer_count']),
                            'revenue': float(row['segment_revenue'])
                        }
                        for row in customer_segments
                    ],
                    'growth_metrics': growth_metrics,
                    'generated_at': datetime.now().isoformat()
                }
                
                # Cache the results
                await self._cache_analytics(cache_key, analytics_data, AnalyticsType.REVENUE)
                
                return analytics_data
                
        except Exception as e:
            logger.error(f"Failed to generate revenue analytics: {e}")
            raise HTTPException(status_code=500, detail="Revenue analytics generation failed")

    async def _calculate_revenue_summary(self, conn, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate revenue summary metrics"""
        summary = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(DISTINCT customer_id) as unique_customers,
                SUM(amount) as total_revenue,
                AVG(amount) as avg_transaction,
                SUM(CASE WHEN payment_type = 'subscription' THEN amount ELSE 0 END) as recurring_revenue,
                SUM(CASE WHEN payment_type = 'one_time' THEN amount ELSE 0 END) as one_time_revenue
            FROM payments 
            WHERE created_at BETWEEN $1 AND $2
            AND payment_status = 'completed'
        """, start_date, end_date)
        
        return {
            'total_transactions': int(summary['total_transactions']) if summary else 0,
            'unique_customers': int(summary['unique_customers']) if summary else 0,
            'total_revenue': float(summary['total_revenue'] or 0),
            'average_transaction': float(summary['avg_transaction'] or 0),
            'recurring_revenue': float(summary['recurring_revenue'] or 0),
            'one_time_revenue': float(summary['one_time_revenue'] or 0),
            'recurring_percentage': float((summary['recurring_revenue'] or 0) / (summary['total_revenue'] or 1) * 100)
        }

    async def _get_revenue_breakdown(self, conn, start_date: datetime, end_date: datetime,
                                   time_frame: TimeFrame) -> List[Dict[str, Any]]:
        """Get revenue breakdown by time frame"""
        if time_frame == TimeFrame.DAILY:
            interval = 'day'
        elif time_frame == TimeFrame.WEEKLY:
            interval = 'week'
        elif time_frame == TimeFrame.MONTHLY:
            interval = 'month'
        else:
            interval = 'day'
        
        breakdown = await conn.fetch(f"""
            SELECT 
                DATE_TRUNC($3, created_at) as period,
                COUNT(*) as transaction_count,
                SUM(amount) as revenue,
                AVG(amount) as avg_transaction
            FROM payments 
            WHERE created_at BETWEEN $1 AND $2
            AND payment_status = 'completed'
            GROUP BY DATE_TRUNC($3, created_at)
            ORDER BY period
        """, start_date, end_date, interval)
        
        return [dict(row) for row in breakdown]

    async def _calculate_growth_metrics(self, conn, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate growth metrics"""
        # Current period revenue
        current_revenue = await conn.fetchval("""
            SELECT COALESCE(SUM(amount), 0)
            FROM payments 
            WHERE created_at BETWEEN $1 AND $2
            AND payment_status = 'completed'
        """, start_date, end_date)
        
        # Previous period for comparison
        period_length = end_date - start_date
        prev_start = start_date - period_length
        prev_end = start_date
        
        previous_revenue = await conn.fetchval("""
            SELECT COALESCE(SUM(amount), 0)
            FROM payments 
            WHERE created_at BETWEEN $1 AND $2
            AND payment_status = 'completed'
        """, prev_start, prev_end)
        
        growth_rate = 0
        if previous_revenue and previous_revenue > 0:
            growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
        
        return {
            'current_period_revenue': float(current_revenue or 0),
            'previous_period_revenue': float(previous_revenue or 0),
            'growth_rate': float(growth_rate),
            'growth_amount': float((current_revenue or 0) - (previous_revenue or 0))
        }

    async def generate_payment_trends_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Generate payment trends analytics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            async with self.db_pool.acquire() as conn:
                # Payment status distribution
                status_dist = await conn.fetch("""
                    SELECT 
                        payment_status,
                        COUNT(*) as count,
                        SUM(amount) as total_amount
                    FROM payments 
                    WHERE created_at >= $1
                    GROUP BY payment_status
                    ORDER BY count DESC
                """, start_date)
                
                # Payment method trends
                method_trends = await conn.fetch("""
                    SELECT 
                        payment_method,
                        DATE_TRUNC('day', created_at) as day,
                        COUNT(*) as transaction_count,
                        SUM(amount) as revenue
                    FROM payments 
                    WHERE created_at >= $1
                    GROUP BY payment_method, DATE_TRUNC('day', created_at)
                    ORDER BY day, payment_method
                """, start_date)
                
                # Processing time analysis
                processing_stats = await conn.fetchrow("""
                    SELECT 
                        AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_processing_time,
                        MIN(EXTRACT(EPOCH FROM (updated_at - created_at))) as min_processing_time,
                        MAX(EXTRACT(EPOCH FROM (updated_at - created_at))) as max_processing_time
                    FROM payments 
                    WHERE created_at >= $1
                    AND payment_status = 'completed'
                    AND updated_at IS NOT NULL
                """, start_date)
                
                # Failure analysis
                failure_analysis = await conn.fetch("""
                    SELECT 
                        failure_reason,
                        COUNT(*) as failure_count,
                        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM payments WHERE created_at >= $1) as failure_percentage
                    FROM payments 
                    WHERE created_at >= $1
                    AND payment_status = 'failed'
                    GROUP BY failure_reason
                    ORDER BY failure_count DESC
                """, start_date)
                
                # Calculate success rates
                total_payments = sum(row['count'] for row in status_dist)
                successful_payments = sum(row['count'] for row in status_dist if row['payment_status'] == 'completed')
                success_rate = (successful_payments / total_payments * 100) if total_payments > 0 else 0
                
                return {
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat(),
                        'days': days
                    },
                    'overall_metrics': {
                        'total_payments': total_payments,
                        'success_rate': round(success_rate, 2),
                        'failure_rate': round(100 - success_rate, 2),
                        'avg_processing_time': float(processing_stats['avg_processing_time'] or 0)
                    },
                    'status_distribution': [
                        {
                            'status': row['payment_status'],
                            'count': int(row['count']),
                            'total_amount': float(row['total_amount']),
                            'percentage': round(row['count'] / total_payments * 100, 2)
                        }
                        for row in status_dist
                    ],
                    'method_trends': self._group_method_trends(method_trends),
                    'processing_stats': {
                        'average': float(processing_stats['avg_processing_time'] or 0),
                        'minimum': float(processing_stats['min_processing_time'] or 0),
                        'maximum': float(processing_stats['max_processing_time'] or 0)
                    },
                    'failure_analysis': [
                        {
                            'reason': row['failure_reason'] or 'unknown',
                            'count': int(row['failure_count']),
                            'percentage': round(float(row['failure_percentage']), 2)
                        }
                        for row in failure_analysis
                    ],
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to generate payment trends analytics: {e}")
            raise HTTPException(status_code=500, detail="Payment trends analytics generation failed")

    def _group_method_trends(self, method_trends: List) -> Dict[str, List]:
        """Group payment method trends by method"""
        grouped = {}
        for row in method_trends:
            method = row['payment_method']
            if method not in grouped:
                grouped[method] = []
            
            grouped[method].append({
                'date': row['day'].isoformat(),
                'transactions': int(row['transaction_count']),
                'revenue': float(row['revenue'])
            })
        
        return grouped

    async def generate_subscription_metrics(self) -> Dict[str, Any]:
        """Generate subscription-specific metrics"""
        try:
            async with self.db_pool.acquire() as conn:
                # Active subscriptions
                active_subs = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_active,
                        SUM(monthly_amount) as monthly_recurring_revenue,
                        AVG(monthly_amount) as avg_subscription_value
                    FROM subscriptions 
                    WHERE status = 'active'
                """)
                
                # Churn analysis
                churn_data = await conn.fetch("""
                    SELECT 
                        DATE_TRUNC('month', cancelled_at) as month,
                        COUNT(*) as churned_subscriptions,
                        COUNT(*) * 100.0 / LAG(COUNT(*)) OVER (ORDER BY DATE_TRUNC('month', cancelled_at)) as churn_rate
                    FROM subscriptions 
                    WHERE status = 'cancelled'
                    AND cancelled_at >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY DATE_TRUNC('month', cancelled_at)
                    ORDER BY month
                """)
                
                # Subscription plan distribution
                plan_dist = await conn.fetch("""
                    SELECT 
                        subscription_plan,
                        COUNT(*) as subscriber_count,
                        SUM(monthly_amount) as plan_revenue
                    FROM subscriptions 
                    WHERE status = 'active'
                    GROUP BY subscription_plan
                    ORDER BY subscriber_count DESC
                """)
                
                return {
                    'active_subscriptions': {
                        'count': int(active_subs['total_active']) if active_subs else 0,
                        'monthly_recurring_revenue': float(active_subs['monthly_recurring_revenue'] or 0),
                        'average_subscription_value': float(active_subs['avg_subscription_value'] or 0)
                    },
                    'churn_analysis': [
                        {
                            'month': row['month'].strftime('%Y-%m'),
                            'churned_count': int(row['churned_subscriptions']),
                            'churn_rate': round(float(row['churn_rate'] or 0), 2)
                        }
                        for row in churn_data
                    ],
                    'plan_distribution': [
                        {
                            'plan': row['subscription_plan'],
                            'subscribers': int(row['subscriber_count']),
                            'revenue': float(row['plan_revenue'])
                        }
                        for row in plan_dist
                    ],
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to generate subscription metrics: {e}")
            raise HTTPException(status_code=500, detail="Subscription metrics generation failed")

    async def _get_cached_analytics(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get analytics data from cache"""
        try:
            async with self.db_pool.acquire() as conn:
                cached = await conn.fetchrow("""
                    SELECT data FROM analytics_cache 
                    WHERE cache_key = $1 AND expires_at > NOW()
                """, cache_key)
                
                return cached['data'] if cached else None
                
        except Exception as e:
            logger.error(f"Failed to get cached analytics: {e}")
            return None

    async def _cache_analytics(self, cache_key: str, data: Dict[str, Any], 
                             analytics_type: AnalyticsType, expiry_hours: int = 1) -> None:
        """Cache analytics data"""
        try:
            expires_at = datetime.now() + timedelta(hours=expiry_hours)
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO analytics_cache 
                    (cache_key, analytics_type, time_frame, data, expires_at)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (cache_key) DO UPDATE SET
                        data = EXCLUDED.data,
                        expires_at = EXCLUDED.expires_at
                """,
                cache_key,
                analytics_type.value,
                'custom',
                json.dumps(data, default=str),
                expires_at
                )
                
        except Exception as e:
            logger.error(f"Failed to cache analytics: {e}")

    async def create_analytics_dashboard(self) -> Dict[str, Any]:
        """Create comprehensive analytics dashboard"""
        try:
            # Get recent revenue analytics
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            revenue_analytics = await self.generate_revenue_analytics(start_date, end_date)
            payment_trends = await self.generate_payment_trends_analytics(30)
            subscription_metrics = await self.generate_subscription_metrics()
            
            return {
                'dashboard_type': 'comprehensive',
                'last_updated': datetime.now().isoformat(),
                'revenue_analytics': revenue_analytics,
                'payment_trends': payment_trends,
                'subscription_metrics': subscription_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to create analytics dashboard: {e}")
            raise HTTPException(status_code=500, detail="Analytics dashboard creation failed")
