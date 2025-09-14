"""
Cost Tracker module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Ainflue Platform - Distribution Monitoring - Cost Tracker
Advanced cost tracking and financial monitoring for distribution infrastructure

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import statistics
from collections import defaultdict
import pandas as pd

logger = logging.getLogger(__name__)

class CostCategory(Enum):
    """Cost categories for tracking"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    API_CALLS = "api_calls"
    THIRD_PARTY = "third_party"
    PLATFORM_FEES = "platform_fees"
    MONITORING = "monitoring"
    SECURITY = "security"
    BACKUP = "backup"

class BillingPeriod(Enum):
    """Billing periods"""
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    PAY_PER_USE = "pay_per_use"

class CostOptimizationAction(Enum):
    """Cost optimization actions"""
    SCALE_DOWN = "scale_down"
    RESERVED_INSTANCES = "reserved_instances"
    SPOT_INSTANCES = "spot_instances"
    DATA_ARCHIVAL = "data_archival"
    CACHE_OPTIMIZATION = "cache_optimization"
    API_OPTIMIZATION = "api_optimization"
    RESOURCE_CONSOLIDATION = "resource_consolidation"

@dataclass
class CostItem:
    """Individual cost item"""
    timestamp: datetime
    category: CostCategory
    service: str
    resource_id: str
    usage_amount: float
    unit_cost: float
    total_cost: float
    billing_period: BillingPeriod
    region: str
    metadata: Dict[str, Any] = None

@dataclass
class CostBudget:
    """Cost budget definition"""
    budget_id: str
    name: str
    category: Optional[CostCategory]
    period: BillingPeriod
    amount: float
    threshold_warning: float  # Percentage of budget
    threshold_critical: float  # Percentage of budget
    start_date: datetime
    end_date: datetime
    notification_emails: List[str]

@dataclass
class CostAlert:
    """Cost alert"""
    alert_id: str
    budget_id: str
    threshold_type: str  # warning, critical, exceeded
    current_spend: float
    budget_amount: float
    percentage_used: float
    period_remaining: timedelta
    projected_total: float
    created_at: datetime

@dataclass
class CostOptimizationRecommendation:
    """Cost optimization recommendation"""
    recommendation_id: str
    action: CostOptimizationAction
    category: CostCategory
    description: str
    potential_savings: float
    implementation_effort: str  # low, medium, high
    risk_level: str  # low, medium, high
    estimated_timeline: str
    prerequisites: List[str]

class DistributionCostTracker:
    """
    Advanced cost tracking system for distribution infrastructure
    Monitors spending, tracks budgets, and provides optimization recommendations
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.cost_items: List[CostItem] = []
        self.budgets: Dict[str, CostBudget] = {}
        self.alerts: List[CostAlert] = []
        self.optimization_recommendations: List[CostOptimizationRecommendation] = []
        
        # Cost tracking configuration
        self.cost_rates = self._load_cost_rates()
        self.resource_mapping = self._load_resource_mapping()
        
        # Initialize with sample data
        self._initialize_sample_data()
        self._initialize_default_budgets()
    
    def _load_cost_rates(self) -> Dict[str, Dict[str, float]]:
        """Load cost rates for different services and regions"""
        return {
            'compute': {
                'us-east-1': {'m5.large': 0.096, 'm5.xlarge': 0.192, 'm5.2xlarge': 0.384},
                'eu-west-1': {'m5.large': 0.105, 'm5.xlarge': 0.210, 'm5.2xlarge': 0.420},
                'ap-southeast-1': {'m5.large': 0.110, 'm5.xlarge': 0.220, 'm5.2xlarge': 0.440}
            },
            'storage': {
                'us-east-1': {'standard': 0.023, 'ssd': 0.10, 'archive': 0.004},
                'eu-west-1': {'standard': 0.025, 'ssd': 0.11, 'archive': 0.0045},
                'ap-southeast-1': {'standard': 0.027, 'ssd': 0.12, 'archive': 0.005}
            },
            'database': {
                'us-east-1': {'db.t3.medium': 0.068, 'db.r5.large': 0.24, 'db.r5.xlarge': 0.48},
                'eu-west-1': {'db.t3.medium': 0.075, 'db.r5.large': 0.264, 'db.r5.xlarge': 0.528},
                'ap-southeast-1': {'db.t3.medium': 0.080, 'db.r5.large': 0.280, 'db.r5.xlarge': 0.560}
            },
            'network': {
                'data_transfer_out': 0.09,
                'data_transfer_regional': 0.02,
                'load_balancer': 0.025
            },
            'api_calls': {
                'youtube': 0.0001,  # Per API call
                'instagram': 0.0002,
                'tiktok': 0.00015,
                'facebook': 0.0001,
                'twitter': 0.0003
            }
        }
    
    def _load_resource_mapping(self) -> Dict[str, str]:
        """Load mapping of resource IDs to services"""
        return {
            'dist-compute-01': 'Distribution API Server',
            'dist-compute-02': 'Distribution Worker Pool',
            'dist-db-01': 'Distribution Database',
            'dist-cache-01': 'Distribution Cache',
            'dist-storage-01': 'Content Storage',
            'dist-lb-01': 'Distribution Load Balancer'
        }
    
    def _initialize_sample_data(self) -> None:
        """Initialize with sample cost data"""
        
        # Generate cost data for the last 30 days
        start_date = datetime.utcnow() - timedelta(days=30)
        
        for day in range(30):
            date = start_date + timedelta(days=day)
            
            # Compute costs
            self.cost_items.append(CostItem(
                timestamp=date,
                category=CostCategory.COMPUTE,
                service='EC2',
                resource_id='dist-compute-01',
                usage_amount=24.0,  # Hours
                unit_cost=0.096,
                total_cost=24.0 * 0.096,
                billing_period=BillingPeriod.HOURLY,
                region='us-east-1',
                metadata={'instance_type': 'm5.large', 'availability_zone': 'us-east-1a'}
            ))
            
            # Storage costs
            self.cost_items.append(CostItem(
                timestamp=date,
                category=CostCategory.STORAGE,
                service='S3',
                resource_id='dist-storage-01',
                usage_amount=1000.0,  # GB
                unit_cost=0.023,
                total_cost=1000.0 * 0.023,
                billing_period=BillingPeriod.MONTHLY,
                region='us-east-1',
                metadata={'storage_class': 'standard', 'requests': 50000}
            ))
            
            # API call costs (varies by day)
            api_calls = 10000 + (day * 200) + (day % 7) * 500  # Growing usage with weekly patterns
            self.cost_items.append(CostItem(
                timestamp=date,
                category=CostCategory.API_CALLS,
                service='Platform APIs',
                resource_id='api-usage-01',
                usage_amount=api_calls,
                unit_cost=0.0001,
                total_cost=api_calls * 0.0001,
                billing_period=BillingPeriod.PAY_PER_USE,
                region='global',
                metadata={'platforms': ['youtube', 'instagram', 'tiktok']}
            ))
    
    def _initialize_default_budgets(self) -> None:
        """Initialize default cost budgets"""
        
        # Monthly compute budget
        self.budgets['monthly_compute'] = CostBudget(
            budget_id='monthly_compute',
            name='Monthly Compute Budget',
            category=CostCategory.COMPUTE,
            period=BillingPeriod.MONTHLY,
            amount=5000.0,
            threshold_warning=80.0,
            threshold_critical=95.0,
            start_date=datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            end_date=datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32),
            notification_emails=['ops@ainflue.com', 'finance@ainflue.com']
        )
        
        # Monthly total budget
        self.budgets['monthly_total'] = CostBudget(
            budget_id='monthly_total',
            name='Total Monthly Budget',
            category=None,  # All categories
            period=BillingPeriod.MONTHLY,
            amount=15000.0,
            threshold_warning=75.0,
            threshold_critical=90.0,
            start_date=datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            end_date=datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32),
            notification_emails=['cfo@ainflue.com', 'ceo@ainflue.com']
        )
    
    async def record_cost(self, category: CostCategory, service: str, resource_id: str,
                         usage_amount: float, unit_cost: float, region: str = 'us-east-1',
                         metadata: Optional[Dict] = None) -> CostItem:
        """
        Record a cost item
        
        Args:
            category: Cost category
            service: Service name
            resource_id: Resource identifier
            usage_amount: Amount of usage
            unit_cost: Cost per unit
            region: AWS region or location
            metadata: Additional metadata
            
        Returns:
            Created cost item
        """
        total_cost = usage_amount * unit_cost
        
        cost_item = CostItem(
            timestamp=datetime.utcnow(),
            category=category,
            service=service,
            resource_id=resource_id,
            usage_amount=usage_amount,
            unit_cost=unit_cost,
            total_cost=total_cost,
            billing_period=BillingPeriod.HOURLY,  # Default
            region=region,
            metadata=metadata or {}
        )
        
        self.cost_items.append(cost_item)
        
        # Check budget alerts
        await self._check_budget_alerts()
        
        logger.debug(f"Recorded cost: {service} - ${total_cost:.4f}")
        return cost_item
    
    async def get_cost_summary(self, start_date: datetime, end_date: datetime,
                             category: Optional[CostCategory] = None) -> Dict[str, Any]:
        """
        Get cost summary for a period
        
        Args:
            start_date: Start of period
            end_date: End of period
            category: Optional category filter
            
        Returns:
            Cost summary data
        """
        # Filter cost items
        filtered_items = [
            item for item in self.cost_items
            if start_date <= item.timestamp <= end_date
        ]
        
        if category:
            filtered_items = [item for item in filtered_items if item.category == category]
        
        if not filtered_items:
            return {
                'total_cost': 0.0,
                'item_count': 0,
                'by_category': {},
                'by_service': {},
                'by_region': {},
                'daily_costs': {}
            }
        
        # Calculate totals
        total_cost = sum(item.total_cost for item in filtered_items)
        
        # Group by category
        by_category = defaultdict(float)
        for item in filtered_items:
            by_category[item.category.value] += item.total_cost
        
        # Group by service
        by_service = defaultdict(float)
        for item in filtered_items:
            by_service[item.service] += item.total_cost
        
        # Group by region
        by_region = defaultdict(float)
        for item in filtered_items:
            by_region[item.region] += item.total_cost
        
        # Daily costs
        daily_costs = defaultdict(float)
        for item in filtered_items:
            day_key = item.timestamp.strftime('%Y-%m-%d')
            daily_costs[day_key] += item.total_cost
        
        return {
            'total_cost': total_cost,
            'item_count': len(filtered_items),
            'by_category': dict(by_category),
            'by_service': dict(by_service),
            'by_region': dict(by_region),
            'daily_costs': dict(daily_costs),
            'average_daily_cost': total_cost / max(1, (end_date - start_date).days),
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat()
        }
    
    async def _check_budget_alerts(self) -> None:
        """Check all budgets for threshold violations"""
        
        for budget_id, budget in self.budgets.items():
            current_spend = await self._calculate_budget_spend(budget)
            percentage_used = (current_spend / budget.amount) * 100
            
            # Check thresholds
            alert_type = None
            if percentage_used >= 100:
                alert_type = 'exceeded'
            elif percentage_used >= budget.threshold_critical:
                alert_type = 'critical'
            elif percentage_used >= budget.threshold_warning:
                alert_type = 'warning'
            
            if alert_type:
                # Check if we already have a recent alert for this budget
                recent_alerts = [
                    alert for alert in self.alerts
                    if alert.budget_id == budget_id and
                    (datetime.utcnow() - alert.created_at) < timedelta(hours=1)
                ]
                
                if not recent_alerts:
                    # Calculate projections
                    period_progress = self._calculate_period_progress(budget)
                    projected_total = current_spend / max(period_progress, 0.1) if period_progress > 0 else current_spend
                    
                    alert = CostAlert(
                        alert_id=f"COST-{budget_id}-{int(time.time())}",
                        budget_id=budget_id,
                        threshold_type=alert_type,
                        current_spend=current_spend,
                        budget_amount=budget.amount,
                        percentage_used=percentage_used,
                        period_remaining=budget.end_date - datetime.utcnow(),
                        projected_total=projected_total,
                        created_at=datetime.utcnow()
                    )
                    
                    self.alerts.append(alert)
                    await self._send_budget_alert(alert, budget)
    
    async def _calculate_budget_spend(self, budget: CostBudget) -> float:
        """Calculate current spending for a budget"""
        
        # Filter cost items for budget period
        budget_items = [
            item for item in self.cost_items
            if budget.start_date <= item.timestamp <= budget.end_date
        ]
        
        # Filter by category if specified
        if budget.category:
            budget_items = [item for item in budget_items if item.category == budget.category]
        
        return sum(item.total_cost for item in budget_items)
    
    def _calculate_period_progress(self, budget: CostBudget) -> float:
        """Calculate how much of the budget period has elapsed"""
        
        now = datetime.utcnow()
        total_duration = budget.end_date - budget.start_date
        elapsed_duration = now - budget.start_date
        
        if total_duration.total_seconds() <= 0:
            return 1.0
        
        return min(1.0, elapsed_duration.total_seconds() / total_duration.total_seconds())
    
    async def _send_budget_alert(self, alert -> None: CostAlert, budget -> None: CostBudget) -> None:
        """Send budget alert notification"""
        
        alert_message = f"""
        💰 BUDGET ALERT: {alert.threshold_type.upper()}
        
        Budget: {budget.name}
        Current Spend: ${alert.current_spend:,.2f}
        Budget Amount: ${alert.budget_amount:,.2f}
        Percentage Used: {alert.percentage_used:.1f}%
        Projected Total: ${alert.projected_total:,.2f}
        
        Time Remaining: {alert.period_remaining.days} days
        """
        
        logger.warning(f"Budget alert: {alert_message}")
    
    async def generate_cost_optimization_recommendations(self) -> List[CostOptimizationRecommendation]:
        """Generate cost optimization recommendations based on usage patterns"""
        
        recommendations = []
        
        # Analyze compute usage for right-sizing opportunities
        compute_costs = [item for item in self.cost_items if item.category == CostCategory.COMPUTE]
        if compute_costs:
            avg_daily_compute = statistics.mean([item.total_cost for item in compute_costs[-7:]])
            
            if avg_daily_compute > 100:  # High compute costs
                recommendations.append(CostOptimizationRecommendation(
                    recommendation_id=f"OPT-{int(time.time())}-COMPUTE",
                    action=CostOptimizationAction.RESERVED_INSTANCES,
                    category=CostCategory.COMPUTE,
                    description="Consider reserved instances for compute resources with consistent usage",
                    potential_savings=avg_daily_compute * 30 * 0.4,  # 40% savings
                    implementation_effort="medium",
                    risk_level="low",
                    estimated_timeline="1-2 weeks",
                    prerequisites=["Usage pattern analysis", "Capacity planning"]
                ))
        
        # Analyze storage costs
        storage_costs = [item for item in self.cost_items if item.category == CostCategory.STORAGE]
        if storage_costs:
            total_storage_cost = sum(item.total_cost for item in storage_costs[-30:])
            
            if total_storage_cost > 500:  # High storage costs
                recommendations.append(CostOptimizationRecommendation(
                    recommendation_id=f"OPT-{int(time.time())}-STORAGE",
                    action=CostOptimizationAction.DATA_ARCHIVAL,
                    category=CostCategory.STORAGE,
                    description="Implement data lifecycle policies to archive old content",
                    potential_savings=total_storage_cost * 0.6,  # 60% savings on archived data
                    implementation_effort="low",
                    risk_level="low",
                    estimated_timeline="3-5 days",
                    prerequisites=["Data access pattern analysis"]
                ))
        
        # Analyze API call patterns
        api_costs = [item for item in self.cost_items if item.category == CostCategory.API_CALLS]
        if api_costs:
            recent_api_costs = [item for item in api_costs[-7:]]
            if recent_api_costs:
                avg_daily_api_cost = statistics.mean([item.total_cost for item in recent_api_costs])
                
                if avg_daily_api_cost > 50:  # High API costs
                    recommendations.append(CostOptimizationRecommendation(
                        recommendation_id=f"OPT-{int(time.time())}-API",
                        action=CostOptimizationAction.API_OPTIMIZATION,
                        category=CostCategory.API_CALLS,
                        description="Optimize API usage through caching and batching",
                        potential_savings=avg_daily_api_cost * 30 * 0.25,  # 25% savings
                        implementation_effort="medium",
                        risk_level="medium",
                        estimated_timeline="2-3 weeks",
                        prerequisites=["API usage audit", "Caching infrastructure"]
                    ))
        
        self.optimization_recommendations.extend(recommendations)
        return recommendations
    
    async def get_cost_forecast(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Generate cost forecast based on historical trends"""
        
        # Get recent cost data (last 30 days)
        recent_start = datetime.utcnow() - timedelta(days=30)
        recent_costs = [
            item for item in self.cost_items
            if item.timestamp >= recent_start
        ]
        
        if not recent_costs:
            return {'error': 'Insufficient historical data for forecasting'}
        
        # Calculate daily averages by category
        daily_costs = defaultdict(lambda: defaultdict(float))
        for item in recent_costs:
            day_key = item.timestamp.strftime('%Y-%m-%d')
            daily_costs[day_key][item.category.value] += item.total_cost
        
        # Calculate trends
        category_trends = {}
        for category in CostCategory:
            category_values = []
            for day_costs in daily_costs.values():
                category_values.append(day_costs.get(category.value, 0))
            
            if category_values:
                avg_daily_cost = statistics.mean(category_values)
                
                # Simple linear trend (could be improved with regression)
                if len(category_values) > 1:
                    recent_avg = statistics.mean(category_values[-7:])  # Last week
                    older_avg = statistics.mean(category_values[:-7])   # Earlier period
                    growth_rate = (recent_avg - older_avg) / max(older_avg, 1) if older_avg > 0 else 0
                else:
                    growth_rate = 0
                
                category_trends[category.value] = {
                    'avg_daily_cost': avg_daily_cost,
                    'growth_rate': growth_rate,
                    'forecasted_daily': avg_daily_cost * (1 + growth_rate)
                }
        
        # Generate forecast
        total_forecasted_daily = sum(trend['forecasted_daily'] for trend in category_trends.values())
        
        return {
            'forecast_period_days': days_ahead,
            'forecasted_total_cost': total_forecasted_daily * days_ahead,
            'forecasted_daily_cost': total_forecasted_daily,
            'category_forecasts': category_trends,
            'confidence_level': 'medium',  # Could be calculated based on variance
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def get_cost_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive cost dashboard data"""
        
        now = datetime.utcnow()
        
        # Current month costs
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_summary = await self.get_cost_summary(month_start, now)
        
        # Last month costs for comparison
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        last_month_end = month_start - timedelta(microseconds=1)
        last_month_summary = await self.get_cost_summary(last_month_start, last_month_end)
        
        # Budget status
        budget_status = {}
        for budget_id, budget in self.budgets.items():
            current_spend = await self._calculate_budget_spend(budget)
            percentage_used = (current_spend / budget.amount) * 100
            
            budget_status[budget_id] = {
                'name': budget.name,
                'current_spend': current_spend,
                'budget_amount': budget.amount,
                'percentage_used': percentage_used,
                'remaining': budget.amount - current_spend,
                'status': 'on_track' if percentage_used < 80 else 'warning' if percentage_used < 95 else 'critical'
            }
        
        # Recent alerts
        recent_alerts = [
            {
                'id': alert.alert_id,
                'type': alert.threshold_type,
                'budget': self.budgets[alert.budget_id].name,
                'percentage_used': alert.percentage_used,
                'created_at': alert.created_at.isoformat()
            }
            for alert in self.alerts[-5:]  # Last 5 alerts
        ]
        
        # Cost forecast
        forecast = await self.get_cost_forecast(30)
        
        return {
            'timestamp': now.isoformat(),
            'current_month': {
                'total_cost': month_summary['total_cost'],
                'daily_average': month_summary['average_daily_cost'],
                'by_category': month_summary['by_category']
            },
            'last_month': {
                'total_cost': last_month_summary['total_cost'],
                'comparison': {
                    'absolute_change': month_summary['total_cost'] - last_month_summary['total_cost'],
                    'percentage_change': ((month_summary['total_cost'] - last_month_summary['total_cost']) / max(last_month_summary['total_cost'], 1)) * 100
                }
            },
            'budget_status': budget_status,
            'recent_alerts': recent_alerts,
            'forecast': forecast,
            'optimization_opportunities': len(self.optimization_recommendations)
        }

# Factory function
def create_cost_tracker(config: Optional[Dict] = None) -> DistributionCostTracker:
    """Create cost tracker instance"""
    return DistributionCostTracker(config)

# Example usage
async def main() -> None:
    """Example usage of cost tracker"""
    tracker = create_cost_tracker()
    
    # Record some costs
    await tracker.record_cost(
        category=CostCategory.COMPUTE,
        service='EC2',
        resource_id='web-server-01',
        usage_amount=24.0,
        unit_cost=0.096
    )
    
    # Get cost summary
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    summary = await tracker.get_cost_summary(start_date, end_date)
    
    print(f"Weekly cost: ${summary['total_cost']:.2f}")
    print(f"Daily average: ${summary['average_daily_cost']:.2f}")
    
    # Generate optimization recommendations
    recommendations = await tracker.generate_cost_optimization_recommendations()
    print(f"Found {len(recommendations)} optimization opportunities")
    
    # Get dashboard data
    dashboard = await tracker.get_cost_dashboard_data()
    print(f"Current month spend: ${dashboard['current_month']['total_cost']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())