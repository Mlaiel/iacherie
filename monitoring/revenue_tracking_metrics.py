"""💰 Revenue Tracking Metrics - Advanced Revenue Analytics
======================================================

Comprehensive revenue tracking and analysis system for the Ainflue platform.
Tracks all revenue streams, analyzes patterns, and provides predictive insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
from collections import defaultdict
import statistics

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class RevenueSource(Enum):
    """Revenue source types"""    LICENSING = "licensing"
    SUBSCRIPTION = "subscription"
    COMMISSION = "commission"
    ADVERTISEMENT = "advertisement"
    PREMIUM_FEATURES = "premium_features"
    API_ACCESS = "api_access"
    DATA_LICENSING = "data_licensing"


@dataclass
class RevenueEvent:
    """Individual revenue event"""    amount: Decimal
    source: RevenueSource
    user_id: Optional[int]
    license_id: Optional[int]
    content_id: Optional[int]
    timestamp: datetime
    currency: str = "EUR"
    metadata: Dict[str, Any] = field(default_factory=dict)


class RevenueTracker:
    """    Advanced revenue tracking system
    
    Features:
    - Multi-source revenue tracking
    - Real-time revenue analytics
    - Revenue forecasting
    - Customer lifetime value analysis
    - Churn impact assessment
    - Revenue optimization recommendations
    """    
    def __init__(self):
        """Initialize revenue tracker"""        
        # Use unique metric names to avoid registry conflicts
        metric_prefix = f"ainflue_revenue_{int(time.time())}"
        
        # Prometheus metrics with unique names
        self.revenue_total = Counter(
            f'{metric_prefix}_total_euros',
            'Total revenue in euros',
            ['source', 'currency']
        )
        
        self.revenue_per_user = Gauge(
            'ainflue_revenue_per_user_euros',
            'Revenue per user in euros',
            ['user_id', 'source']
        )
        
        self.revenue_hourly = Histogram(
            'ainflue_revenue_hourly_euros',
            'Hourly revenue distribution',
            ['source'],
            buckets=[0, 10, 50, 100, 500, 1000, 5000, 10000, float('inf')]
        )
        
        self.revenue_trends = Gauge(
            'ainflue_revenue_trend_percentage',
            'Revenue trend percentage change',
            ['source', 'period']
        )
        
        self.customer_lifetime_value = Gauge(
            'ainflue_customer_lifetime_value_euros',
            'Customer lifetime value in euros',
            ['user_id', 'cohort']
        )
        
        # Revenue data storage
        self.revenue_events: List[RevenueEvent] = []
        self.user_revenue: Dict[int, Dict[str, Any]] = defaultdict(dict)
        self.source_revenue: Dict[RevenueSource, List[RevenueEvent]] = defaultdict(list)
        
        # Analytics cache
        self.analytics_cache: Dict[str, Any] = {}
        self.cache_timestamp = datetime.utcnow()
        self.cache_ttl = timedelta(minutes=5)
        
        logger.info("RevenueTracker initialized successfully")
    
    async def track_revenue(
        self,
        amount: Decimal,
        source: RevenueSource,
        user_id: Optional[int] = None,
        license_id: Optional[int] = None,
        content_id: Optional[int] = None,
        currency: str = "EUR",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """        Track a revenue event
        
        Args:
            amount: Revenue amount
            source: Revenue source
            user_id: Associated user ID
            license_id: Associated license ID
            content_id: Associated content ID
            currency: Currency code
            metadata: Additional metadata
        """        try:
            # Create revenue event
            event = RevenueEvent(
                amount=amount,
                source=source,
                user_id=user_id,
                license_id=license_id,
                content_id=content_id,
                timestamp=datetime.utcnow(),
                currency=currency,
                metadata=metadata or {}
            )
            
            # Store event
            self.revenue_events.append(event)
            self.source_revenue[source].append(event)
            
            # Update user revenue tracking
            if user_id:
                if user_id not in self.user_revenue:
                    self.user_revenue[user_id] = {
                        "total_revenue": Decimal('0'),
                        "first_revenue": event.timestamp,
                        "last_revenue": event.timestamp,
                        "revenue_count": 0,
                        "sources": defaultdict(Decimal)
                    }
                
                user_data = self.user_revenue[user_id]
                user_data["total_revenue"] += amount
                user_data["last_revenue"] = event.timestamp
                user_data["revenue_count"] += 1
                user_data["sources"][source.value] += amount
            
            # Update Prometheus metrics
            self.revenue_total.labels(
                source=source.value,
                currency=currency
            ).inc(float(amount))
            
            if user_id:
                self.revenue_per_user.labels(
                    user_id=str(user_id),
                    source=source.value
                ).set(float(self.user_revenue[user_id]["total_revenue"]))
            
            self.revenue_hourly.labels(source=source.value).observe(float(amount))
            
            # Invalidate cache
            self.analytics_cache.clear()
            
            logger.debug(f"Revenue tracked: {amount} {currency} from {source.value}")
            
        except Exception as e:
            logger.error(f"Error tracking revenue: {e}")
    
    async def get_revenue_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """        Get comprehensive revenue analytics
        
        Args:
            period_days: Analysis period in days
            
        Returns:
            Revenue analytics data
        """        try:
            # Check cache
            cache_key = f"analytics_{period_days}"
            if (cache_key in self.analytics_cache and 
                datetime.utcnow() - self.cache_timestamp < self.cache_ttl):
                return self.analytics_cache[cache_key]
            
            # Calculate analytics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=period_days)
            
            period_events = [
                event for event in self.revenue_events
                if start_time <= event.timestamp <= end_time
            ]
            
            analytics = {
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "days": period_days
                },
                "total_revenue": await self._calculate_total_revenue(period_events),
                "revenue_by_source": await self._calculate_revenue_by_source(period_events),
                "daily_revenue": await self._calculate_daily_revenue(period_events),
                "top_users": await self._calculate_top_users(period_events),
                "trends": await self._calculate_revenue_trends(period_days),
                "forecasts": await self._calculate_revenue_forecasts(period_events),
                "metrics": {
                    "average_revenue_per_user": await self._calculate_arpu(period_events),
                    "revenue_growth_rate": await self._calculate_growth_rate(period_days),
                    "customer_lifetime_value": await self._calculate_clv(),
                    "churn_impact": await self._calculate_churn_impact()
                }
            }
            
            # Cache results
            self.analytics_cache[cache_key] = analytics
            self.cache_timestamp = datetime.utcnow()
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting revenue analytics: {e}")
            return {"error": str(e)}
    
    async def _calculate_total_revenue(self, events: List[RevenueEvent]) -> Dict[str, Any]:
        """Calculate total revenue metrics"""        if not events:
            return {"amount": 0, "currency": "EUR", "count": 0}
        
        total_amount = sum(event.amount for event in events)
        
        return {
            "amount": float(total_amount),
            "currency": events[0].currency,
            "count": len(events),
            "average_per_transaction": float(total_amount / len(events))
        }
    
    async def _calculate_revenue_by_source(self, events: List[RevenueEvent]) -> Dict[str, Any]:
        """Calculate revenue breakdown by source"""        source_data = defaultdict(lambda: {"amount": Decimal('0'), "count": 0})
        
        for event in events:
            source_data[event.source.value]["amount"] += event.amount
            source_data[event.source.value]["count"] += 1
        
        total = sum(data["amount"] for data in source_data.values())
        
        result = {}
        for source, data in source_data.items():
            result[source] = {
                "amount": float(data["amount"]),
                "count": data["count"],
                "percentage": float((data["amount"] / total * 100)) if total > 0 else 0,
                "average_per_transaction": float(data["amount"] / data["count"]) if data["count"] > 0 else 0
            }
        
        return result
    
    async def _calculate_daily_revenue(self, events: List[RevenueEvent]) -> List[Dict[str, Any]]:
        """Calculate daily revenue breakdown"""        daily_revenue = defaultdict(Decimal)
        
        for event in events:
            day_key = event.timestamp.strftime("%Y-%m-%d")
            daily_revenue[day_key] += event.amount
        
        return [
            {
                "date": date,
                "amount": float(amount),
                "formatted_date": datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
            }
            for date, amount in sorted(daily_revenue.items())
        ]
    
    async def _calculate_top_users(self, events: List[RevenueEvent], limit: int = 10) -> List[Dict[str, Any]]:
        """Calculate top revenue-generating users"""        user_revenue = defaultdict(Decimal)
        user_transactions = defaultdict(int)
        
        for event in events:
            if event.user_id:
                user_revenue[event.user_id] += event.amount
                user_transactions[event.user_id] += 1
        
        # Sort by revenue
        sorted_users = sorted(user_revenue.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            {
                "user_id": user_id,
                "total_revenue": float(revenue),
                "transaction_count": user_transactions[user_id],
                "average_per_transaction": float(revenue / user_transactions[user_id])
            }
            for user_id, revenue in sorted_users
        ]
    
    async def _calculate_revenue_trends(self, period_days: int) -> Dict[str, Any]:
        """Calculate revenue trends and patterns"""        try:
            current_period = datetime.utcnow() - timedelta(days=period_days)
            previous_period = current_period - timedelta(days=period_days)
            
            current_revenue = sum(
                event.amount for event in self.revenue_events
                if current_period <= event.timestamp <= datetime.utcnow()
            )
            
            previous_revenue = sum(
                event.amount for event in self.revenue_events
                if previous_period <= event.timestamp <= current_period
            )
            
            # Calculate growth rate
            growth_rate = 0
            if previous_revenue > 0:
                growth_rate = float((current_revenue - previous_revenue) / previous_revenue * 100)
            
            # Update Prometheus metric
            self.revenue_trends.labels(
                source="total",
                period=f"{period_days}d"
            ).set(growth_rate)
            
            return {
                "current_period_revenue": float(current_revenue),
                "previous_period_revenue": float(previous_revenue),
                "growth_rate_percentage": growth_rate,
                "trend": "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable"
            }
            
        except Exception as e:
            logger.error(f"Error calculating revenue trends: {e}")
            return {"error": str(e)}
    
    async def _calculate_revenue_forecasts(self, events: List[RevenueEvent]) -> Dict[str, Any]:
        """Calculate revenue forecasts using simple linear regression"""        try:
            if len(events) < 7:  # Need at least a week of data
                return {"error": "Insufficient data for forecasting"}
            
            # Group by day
            daily_revenue = defaultdict(Decimal)
            for event in events:
                day_key = event.timestamp.strftime("%Y-%m-%d")
                daily_revenue[day_key] += event.amount
            
            # Convert to time series
            dates = sorted(daily_revenue.keys())
            revenues = [float(daily_revenue[date]) for date in dates]
            
            # Simple linear regression
            n = len(revenues)
            x_values = list(range(n))
            
            mean_x = statistics.mean(x_values)
            mean_y = statistics.mean(revenues)
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, revenues))
            denominator = sum((x - mean_x) ** 2 for x in x_values)
            
            if denominator == 0:
                return {"error": "Cannot calculate trend"}
            
            slope = numerator / denominator
            intercept = mean_y - slope * mean_x
            
            # Forecast next 7 days
            forecasts = []
            base_date = datetime.strptime(dates[-1], "%Y-%m-%d")
            
            for i in range(1, 8):  # Next 7 days
                forecast_date = base_date + timedelta(days=i)
                forecast_value = max(0, slope * (n + i - 1) + intercept)
                
                forecasts.append({
                    "date": forecast_date.strftime("%Y-%m-%d"),
                    "predicted_revenue": round(forecast_value, 2)
                })
            
            return {
                "method": "linear_regression",
                "trend_slope": round(slope, 2),
                "forecasts": forecasts,
                "confidence": "low" if abs(slope) < 10 else "medium" if abs(slope) < 100 else "high"
            }
            
        except Exception as e:
            logger.error(f"Error calculating revenue forecasts: {e}")
            return {"error": str(e)}
    
    async def _calculate_arpu(self, events: List[RevenueEvent]) -> float:
        """Calculate Average Revenue Per User"""        user_ids = set(event.user_id for event in events if event.user_id)
        total_revenue = sum(event.amount for event in events)
        
        return float(total_revenue / len(user_ids)) if user_ids else 0
    
    async def _calculate_growth_rate(self, period_days: int) -> float:
        """Calculate revenue growth rate"""        trends = await self._calculate_revenue_trends(period_days)
        return trends.get("growth_rate_percentage", 0)
    
    async def _calculate_clv(self) -> Dict[str, Any]:
        """Calculate Customer Lifetime Value metrics"""        if not self.user_revenue:
            return {"average": 0, "median": 0, "total_users": 0}
        
        clv_values = [
            float(user_data["total_revenue"])
            for user_data in self.user_revenue.values()
        ]
        
        # Update Prometheus metrics for top users
        sorted_users = sorted(
            self.user_revenue.items(),
            key=lambda x: x[1]["total_revenue"],
            reverse=True
        )[:100]  # Top 100 users
        
        for user_id, user_data in sorted_users:
            cohort = user_data["first_revenue"].strftime("%Y-%m")
            self.customer_lifetime_value.labels(
                user_id=str(user_id),
                cohort=cohort
            ).set(float(user_data["total_revenue"]))
        
        return {
            "average": statistics.mean(clv_values),
            "median": statistics.median(clv_values),
            "total_users": len(clv_values),
            "top_10_percent_avg": statistics.mean(sorted(clv_values, reverse=True)[:max(1, len(clv_values)//10)])
        }
    
    async def _calculate_churn_impact(self) -> Dict[str, Any]:
        """Calculate potential churn impact on revenue"""        # This is a simplified churn impact calculation
        # In a real scenario, you'd have more sophisticated churn prediction
        
        recent_users = set()
        old_users = set()
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        for event in self.revenue_events:
            if event.user_id:
                if event.timestamp >= cutoff_date:
                    recent_users.add(event.user_id)
                else:
                    old_users.add(event.user_id)
        
        potentially_churned = old_users - recent_users
        
        # Calculate revenue from potentially churned users
        churned_revenue = sum(
            user_data["total_revenue"]
            for user_id, user_data in self.user_revenue.items()
            if user_id in potentially_churned
        )
        
        total_revenue = sum(
            user_data["total_revenue"]
            for user_data in self.user_revenue.values()
        )
        
        return {
            "potentially_churned_users": len(potentially_churned),
            "churned_revenue_amount": float(churned_revenue),
            "churn_revenue_percentage": float(churned_revenue / total_revenue * 100) if total_revenue > 0 else 0,
            "active_users": len(recent_users),
            "total_users": len(self.user_revenue)
        }
    
    def get_tracker_stats(self) -> Dict[str, Any]:
        """Get revenue tracker statistics"""        total_revenue = sum(event.amount for event in self.revenue_events)
        
        return {
            "total_events": len(self.revenue_events),
            "total_revenue": float(total_revenue),
            "unique_users": len(self.user_revenue),
            "revenue_sources": len(self.source_revenue),
            "cache_entries": len(self.analytics_cache),
            "oldest_event": self.revenue_events[0].timestamp.isoformat() if self.revenue_events else None,
            "newest_event": self.revenue_events[-1].timestamp.isoformat() if self.revenue_events else None
        }


# Export classes
__all__ = [
    "RevenueTracker",
    "RevenueEvent", 
    "RevenueSource"
]