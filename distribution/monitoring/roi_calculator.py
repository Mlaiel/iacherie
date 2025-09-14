"""
Roi Calculator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Ainflue Platform - Distribution Monitoring - ROI Calculator
Advanced Return on Investment calculation and financial analytics

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
import numpy as np
from collections import defaultdict
import pandas as pd

logger = logging.getLogger(__name__)

class RevenueStream(Enum):
    """Types of revenue streams"""
    SUBSCRIPTION = "subscription"
    COMMISSION = "commission"
    ADVERTISING = "advertising"
    PREMIUM_FEATURES = "premium_features"
    API_LICENSING = "api_licensing"
    MARKETPLACE_FEES = "marketplace_fees"
    CONSULTING = "consulting"

class InvestmentType(Enum):
    """Types of investments"""
    INFRASTRUCTURE = "infrastructure"
    DEVELOPMENT = "development"
    MARKETING = "marketing"
    PERSONNEL = "personnel"
    PLATFORM_INTEGRATION = "platform_integration"
    SECURITY = "security"
    COMPLIANCE = "compliance"

class ROIMetricType(Enum):
    """Types of ROI metrics"""
    SIMPLE_ROI = "simple_roi"
    ANNUALIZED_ROI = "annualized_roi"
    IRR = "irr"  # Internal Rate of Return
    NPV = "npv"  # Net Present Value
    PAYBACK_PERIOD = "payback_period"
    CUSTOMER_LTV = "customer_ltv"  # Customer Lifetime Value
    CAC_RATIO = "cac_ratio"  # Customer Acquisition Cost ratio

@dataclass
class RevenueEvent:
    """Individual revenue event"""
    timestamp: datetime
    stream: RevenueStream
    amount: float
    customer_id: Optional[str]
    platform: Optional[str]
    metadata: Dict[str, Any] = None

@dataclass
class InvestmentEvent:
    """Individual investment event"""
    timestamp: datetime
    investment_type: InvestmentType
    amount: float
    description: str
    expected_lifetime: Optional[timedelta] = None
    metadata: Dict[str, Any] = None

@dataclass
class ROIAnalysis:
    """ROI analysis result"""
    analysis_id: str
    period_start: datetime
    period_end: datetime
    total_revenue: float
    total_investment: float
    roi_percentage: float
    roi_metrics: Dict[ROIMetricType, float]
    revenue_breakdown: Dict[RevenueStream, float]
    investment_breakdown: Dict[InvestmentType, float]
    customer_metrics: Dict[str, float]
    platform_performance: Dict[str, Dict[str, float]]
    trends: Dict[str, Any]
    recommendations: List[str]

@dataclass
class CustomerMetrics:
    """Customer-related financial metrics"""
    customer_id: str
    first_revenue_date: datetime
    total_revenue: float
    ltv: float  # Lifetime Value
    cac: float  # Customer Acquisition Cost
    months_active: int
    avg_monthly_revenue: float
    churn_probability: float

@dataclass
class PlatformROI:
    """Platform-specific ROI analysis"""
    platform: str
    total_revenue: float
    total_costs: float
    roi_percentage: float
    user_count: int
    revenue_per_user: float
    cost_per_user: float
    profit_margin: float

class DistributionROICalculator:
    """
    Advanced ROI calculator for distribution platform
    Calculates comprehensive financial metrics and provides investment insights
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.revenue_events: List[RevenueEvent] = []
        self.investment_events: List[InvestmentEvent] = []
        self.customer_metrics: Dict[str, CustomerMetrics] = {}
        self.roi_analyses: Dict[str, ROIAnalysis] = {}
        
        # Financial configuration
        self.discount_rate = self.config.get('discount_rate', 0.10)  # 10% discount rate
        self.tax_rate = self.config.get('tax_rate', 0.25)  # 25% tax rate
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self) -> None:
        """Initialize with sample financial data"""
        
        # Generate sample revenue data for the last 12 months
        start_date = datetime.utcnow() - timedelta(days=365)
        
        # Subscription revenue (growing over time)
        for month in range(12):
            date = start_date + timedelta(days=month * 30)
            base_revenue = 50000 + (month * 5000)  # Growing subscription base
            
            self.revenue_events.append(RevenueEvent(
                timestamp=date,
                stream=RevenueStream.SUBSCRIPTION,
                amount=base_revenue,
                customer_id=None,  # Aggregate
                platform=None,
                metadata={'subscribers': 1000 + (month * 100)}
            ))
        
        # Commission revenue from platforms
        platforms = ['youtube', 'instagram', 'tiktok', 'facebook']
        for month in range(12):
            for platform in platforms:
                date = start_date + timedelta(days=month * 30)
                commission = np.random.normal(15000, 3000)  # Variable commission
                
                self.revenue_events.append(RevenueEvent(
                    timestamp=date,
                    stream=RevenueStream.COMMISSION,
                    amount=max(commission, 5000),  # Minimum commission
                    customer_id=None,
                    platform=platform,
                    metadata={'transactions': np.random.randint(200, 500)}
                ))
        
        # Investment events
        investments = [
            (InvestmentType.INFRASTRUCTURE, 100000, "Cloud infrastructure scaling"),
            (InvestmentType.DEVELOPMENT, 200000, "New feature development"),
            (InvestmentType.MARKETING, 80000, "Customer acquisition campaigns"),
            (InvestmentType.PLATFORM_INTEGRATION, 150000, "Additional platform integrations"),
            (InvestmentType.SECURITY, 50000, "Security infrastructure")
        ]
        
        for i, (inv_type, amount, description) in enumerate(investments):
            date = start_date + timedelta(days=i * 60)
            self.investment_events.append(InvestmentEvent(
                timestamp=date,
                investment_type=inv_type,
                amount=amount,
                description=description,
                expected_lifetime=timedelta(days=365 * 3),  # 3 years
                metadata={'approved_by': 'CFO'}
            ))
    
    async def record_revenue(self, stream: RevenueStream, amount: float,
                           customer_id: Optional[str] = None,
                           platform: Optional[str] = None,
                           metadata: Optional[Dict] = None) -> RevenueEvent:
        """
        Record a revenue event
        
        Args:
            stream: Revenue stream type
            amount: Revenue amount
            customer_id: Optional customer identifier
            platform: Optional platform identifier
            metadata: Additional metadata
            
        Returns:
            Created revenue event
        """
        event = RevenueEvent(
            timestamp=datetime.utcnow(),
            stream=stream,
            amount=amount,
            customer_id=customer_id,
            platform=platform,
            metadata=metadata or {}
        )
        
        self.revenue_events.append(event)
        
        # Update customer metrics if customer_id provided
        if customer_id:
            await self._update_customer_metrics(customer_id, event)
        
        logger.debug(f"Recorded revenue: {stream.value} - ${amount:.2f}")
        return event
    
    async def record_investment(self, investment_type: InvestmentType, amount: float,
                              description: str, expected_lifetime: Optional[timedelta] = None,
                              metadata: Optional[Dict] = None) -> InvestmentEvent:
        """
        Record an investment event
        
        Args:
            investment_type: Type of investment
            amount: Investment amount
            description: Investment description
            expected_lifetime: Expected benefit lifetime
            metadata: Additional metadata
            
        Returns:
            Created investment event
        """
        event = InvestmentEvent(
            timestamp=datetime.utcnow(),
            investment_type=investment_type,
            amount=amount,
            description=description,
            expected_lifetime=expected_lifetime,
            metadata=metadata or {}
        )
        
        self.investment_events.append(event)
        
        logger.debug(f"Recorded investment: {investment_type.value} - ${amount:.2f}")
        return event
    
    async def _update_customer_metrics(self, customer_id -> None: str, revenue_event -> None: RevenueEvent) -> None:
        """Update customer metrics with new revenue event"""
        
        if customer_id not in self.customer_metrics:
            # New customer
            self.customer_metrics[customer_id] = CustomerMetrics(
                customer_id=customer_id,
                first_revenue_date=revenue_event.timestamp,
                total_revenue=revenue_event.amount,
                ltv=0.0,  # Will be calculated
                cac=100.0,  # Default CAC
                months_active=0,
                avg_monthly_revenue=0.0,
                churn_probability=0.1
            )
        else:
            # Existing customer
            customer = self.customer_metrics[customer_id]
            customer.total_revenue += revenue_event.amount
        
        # Recalculate metrics
        customer = self.customer_metrics[customer_id]
        months_active = max(1, (datetime.utcnow() - customer.first_revenue_date).days // 30)
        customer.months_active = months_active
        customer.avg_monthly_revenue = customer.total_revenue / months_active
        
        # Calculate LTV (simplified)
        customer.ltv = customer.avg_monthly_revenue * 24 * (1 - customer.churn_probability)
    
    async def calculate_roi_analysis(self, period_start: datetime, 
                                   period_end: datetime) -> ROIAnalysis:
        """
        Calculate comprehensive ROI analysis for a period
        
        Args:
            period_start: Analysis period start
            period_end: Analysis period end
            
        Returns:
            Comprehensive ROI analysis
        """
        analysis_id = f"ROI-{int(time.time())}"
        logger.info(f"Calculating ROI analysis {analysis_id} for period {period_start} to {period_end}")
        
        # Filter events for the period
        period_revenues = [
            event for event in self.revenue_events
            if period_start <= event.timestamp <= period_end
        ]
        
        period_investments = [
            event for event in self.investment_events
            if period_start <= event.timestamp <= period_end
        ]
        
        # Calculate totals
        total_revenue = sum(event.amount for event in period_revenues)
        total_investment = sum(event.amount for event in period_investments)
        
        # Calculate basic ROI
        if total_investment > 0:
            roi_percentage = ((total_revenue - total_investment) / total_investment) * 100
        else:
            roi_percentage = float('inf') if total_revenue > 0 else 0
        
        # Calculate advanced ROI metrics
        roi_metrics = await self._calculate_advanced_roi_metrics(period_revenues, period_investments)
        
        # Revenue breakdown by stream
        revenue_breakdown = defaultdict(float)
        for event in period_revenues:
            revenue_breakdown[event.stream] += event.amount
        
        # Investment breakdown by type
        investment_breakdown = defaultdict(float)
        for event in period_investments:
            investment_breakdown[event.investment_type] += event.amount
        
        # Customer metrics
        customer_metrics = await self._calculate_customer_roi_metrics(period_revenues)
        
        # Platform performance
        platform_performance = await self._calculate_platform_performance(period_revenues)
        
        # Trends analysis
        trends = await self._calculate_financial_trends(period_start, period_end)
        
        # Generate recommendations
        recommendations = self._generate_roi_recommendations(
            roi_percentage, roi_metrics, revenue_breakdown, investment_breakdown
        )
        
        analysis = ROIAnalysis(
            analysis_id=analysis_id,
            period_start=period_start,
            period_end=period_end,
            total_revenue=total_revenue,
            total_investment=total_investment,
            roi_percentage=roi_percentage,
            roi_metrics=roi_metrics,
            revenue_breakdown=dict(revenue_breakdown),
            investment_breakdown=dict(investment_breakdown),
            customer_metrics=customer_metrics,
            platform_performance=platform_performance,
            trends=trends,
            recommendations=recommendations
        )
        
        self.roi_analyses[analysis_id] = analysis
        
        logger.info(f"ROI analysis completed: {roi_percentage:.2f}% ROI")
        return analysis
    
    async def _calculate_advanced_roi_metrics(self, revenues: List[RevenueEvent], 
                                            investments: List[InvestmentEvent]) -> Dict[ROIMetricType, float]:
        """Calculate advanced ROI metrics"""
        
        metrics = {}
        
        total_revenue = sum(event.amount for event in revenues)
        total_investment = sum(event.amount for event in investments)
        
        # Simple ROI
        if total_investment > 0:
            metrics[ROIMetricType.SIMPLE_ROI] = ((total_revenue - total_investment) / total_investment) * 100
        else:
            metrics[ROIMetricType.SIMPLE_ROI] = 0
        
        # Annualized ROI (assuming 1-year period for simplification)
        metrics[ROIMetricType.ANNUALIZED_ROI] = metrics[ROIMetricType.SIMPLE_ROI]
        
        # Net Present Value (simplified)
        cash_flows = []
        if investments:
            cash_flows.append(-total_investment)  # Initial investment
        if revenues:
            # Assume revenue comes at the end of period
            cash_flows.append(total_revenue)
        
        if len(cash_flows) > 1:
            npv = cash_flows[1] / (1 + self.discount_rate) - abs(cash_flows[0])
            metrics[ROIMetricType.NPV] = npv
        else:
            metrics[ROIMetricType.NPV] = 0
        
        # Payback period (simplified - months to break even)
        if total_revenue > 0 and len(revenues) > 0:
            monthly_revenue = total_revenue / max(1, len(set(r.timestamp.strftime('%Y-%m') for r in revenues)))
            if monthly_revenue > 0:
                metrics[ROIMetricType.PAYBACK_PERIOD] = total_investment / monthly_revenue
            else:
                metrics[ROIMetricType.PAYBACK_PERIOD] = float('inf')
        else:
            metrics[ROIMetricType.PAYBACK_PERIOD] = float('inf')
        
        # Customer LTV (average)
        if self.customer_metrics:
            avg_ltv = statistics.mean([customer.ltv for customer in self.customer_metrics.values()])
            metrics[ROIMetricType.CUSTOMER_LTV] = avg_ltv
        else:
            metrics[ROIMetricType.CUSTOMER_LTV] = 0
        
        # CAC Ratio (LTV/CAC)
        if self.customer_metrics:
            avg_cac = statistics.mean([customer.cac for customer in self.customer_metrics.values()])
            if avg_cac > 0 and metrics[ROIMetricType.CUSTOMER_LTV] > 0:
                metrics[ROIMetricType.CAC_RATIO] = metrics[ROIMetricType.CUSTOMER_LTV] / avg_cac
            else:
                metrics[ROIMetricType.CAC_RATIO] = 0
        else:
            metrics[ROIMetricType.CAC_RATIO] = 0
        
        return metrics
    
    async def _calculate_customer_roi_metrics(self, revenues: List[RevenueEvent]) -> Dict[str, float]:
        """Calculate customer-related ROI metrics"""
        
        customer_revenues = [r for r in revenues if r.customer_id]
        
        if not customer_revenues:
            return {
                'total_customers': 0,
                'avg_revenue_per_customer': 0,
                'customer_acquisition_cost': 0,
                'customer_lifetime_value': 0
            }
        
        unique_customers = set(r.customer_id for r in customer_revenues)
        total_customer_revenue = sum(r.amount for r in customer_revenues)
        
        # Calculate marketing investment (approximation)
        marketing_investments = [
            inv for inv in self.investment_events 
            if inv.investment_type == InvestmentType.MARKETING
        ]
        total_marketing = sum(inv.amount for inv in marketing_investments)
        
        avg_cac = total_marketing / max(len(unique_customers), 1)
        
        return {
            'total_customers': len(unique_customers),
            'avg_revenue_per_customer': total_customer_revenue / len(unique_customers),
            'customer_acquisition_cost': avg_cac,
            'customer_lifetime_value': statistics.mean([c.ltv for c in self.customer_metrics.values()]) if self.customer_metrics else 0
        }
    
    async def _calculate_platform_performance(self, revenues: List[RevenueEvent]) -> Dict[str, Dict[str, float]]:
        """Calculate platform-specific performance metrics"""
        
        platform_revenues = defaultdict(float)
        platform_counts = defaultdict(int)
        
        for revenue in revenues:
            if revenue.platform:
                platform_revenues[revenue.platform] += revenue.amount
                platform_counts[revenue.platform] += 1
        
        performance = {}
        for platform, total_revenue in platform_revenues.items():
            # Estimate platform costs (simplified)
            platform_costs = total_revenue * 0.15  # Assume 15% platform costs
            
            performance[platform] = {
                'total_revenue': total_revenue,
                'estimated_costs': platform_costs,
                'profit': total_revenue - platform_costs,
                'roi_percentage': ((total_revenue - platform_costs) / platform_costs) * 100 if platform_costs > 0 else 0,
                'transaction_count': platform_counts[platform],
                'avg_transaction_value': total_revenue / platform_counts[platform] if platform_counts[platform] > 0 else 0
            }
        
        return performance
    
    async def _calculate_financial_trends(self, period_start: datetime, 
                                        period_end: datetime) -> Dict[str, Any]:
        """Calculate financial trends over the period"""
        
        # Group revenues by month
        monthly_revenues = defaultdict(float)
        monthly_investments = defaultdict(float)
        
        for revenue in self.revenue_events:
            if period_start <= revenue.timestamp <= period_end:
                month_key = revenue.timestamp.strftime('%Y-%m')
                monthly_revenues[month_key] += revenue.amount
        
        for investment in self.investment_events:
            if period_start <= investment.timestamp <= period_end:
                month_key = investment.timestamp.strftime('%Y-%m')
                monthly_investments[month_key] += investment.amount
        
        # Calculate trends
        revenue_values = list(monthly_revenues.values())
        investment_values = list(monthly_investments.values())
        
        trends = {
            'revenue_trend': 'growing' if len(revenue_values) > 1 and revenue_values[-1] > revenue_values[0] else 'stable',
            'investment_trend': 'increasing' if len(investment_values) > 1 and investment_values[-1] > investment_values[0] else 'stable',
            'monthly_data': {
                'revenues': dict(monthly_revenues),
                'investments': dict(monthly_investments)
            }
        }
        
        if len(revenue_values) > 1:
            revenue_growth_rate = ((revenue_values[-1] - revenue_values[0]) / revenue_values[0]) * 100
            trends['revenue_growth_rate'] = revenue_growth_rate
        
        return trends
    
    def _generate_roi_recommendations(self, roi_percentage: float, 
                                    roi_metrics: Dict[ROIMetricType, float],
                                    revenue_breakdown: Dict[RevenueStream, float],
                                    investment_breakdown: Dict[InvestmentType, float]) -> List[str]:
        """Generate ROI-based recommendations"""
        
        recommendations = []
        
        # ROI-based recommendations
        if roi_percentage < 20:
            recommendations.append("ROI below target (20%) - review investment allocation and revenue optimization strategies")
        elif roi_percentage > 100:
            recommendations.append("Excellent ROI performance - consider scaling successful initiatives")
        
        # Payback period recommendations
        payback_period = roi_metrics.get(ROIMetricType.PAYBACK_PERIOD, float('inf'))
        if payback_period > 18:  # More than 18 months
            recommendations.append("Long payback period detected - prioritize faster-returning investments")
        
        # Customer metrics recommendations
        ltv = roi_metrics.get(ROIMetricType.CUSTOMER_LTV, 0)
        cac_ratio = roi_metrics.get(ROIMetricType.CAC_RATIO, 0)
        
        if cac_ratio < 3:  # LTV should be at least 3x CAC
            recommendations.append("Customer LTV/CAC ratio below optimal (3:1) - focus on customer retention or reduce acquisition costs")
        
        # Revenue stream recommendations
        total_revenue = sum(revenue_breakdown.values())
        if total_revenue > 0:
            subscription_percentage = revenue_breakdown.get(RevenueStream.SUBSCRIPTION, 0) / total_revenue * 100
            if subscription_percentage < 60:
                recommendations.append("Consider increasing recurring revenue streams for more predictable cash flow")
        
        # Investment recommendations
        total_investment = sum(investment_breakdown.values())
        if total_investment > 0:
            marketing_percentage = investment_breakdown.get(InvestmentType.MARKETING, 0) / total_investment * 100
            if marketing_percentage > 40:
                recommendations.append("High marketing investment percentage - ensure strong customer acquisition ROI")
        
        if not recommendations:
            recommendations.append("Financial performance is meeting targets - continue current strategy")
        
        return recommendations
    
    async def simulate_investment_scenario(self, investment_type: InvestmentType,
                                         amount: float, expected_revenue_increase: float,
                                         timeline_months: int) -> Dict[str, Any]:
        """
        Simulate the ROI impact of a potential investment
        
        Args:
            investment_type: Type of investment
            amount: Investment amount
            expected_revenue_increase: Expected monthly revenue increase
            timeline_months: Timeline for analysis
            
        Returns:
            Investment scenario analysis
        """
        # Calculate total expected revenue over timeline
        total_expected_revenue = expected_revenue_increase * timeline_months
        
        # Calculate ROI
        roi_percentage = ((total_expected_revenue - amount) / amount) * 100 if amount > 0 else 0
        
        # Calculate payback period
        payback_months = amount / expected_revenue_increase if expected_revenue_increase > 0 else float('inf')
        
        # Calculate NPV
        monthly_discount_rate = (1 + self.discount_rate) ** (1/12) - 1
        npv = -amount  # Initial investment
        
        for month in range(1, timeline_months + 1):
            discounted_revenue = expected_revenue_increase / ((1 + monthly_discount_rate) ** month)
            npv += discounted_revenue
        
        # Risk assessment
        risk_level = "low"
        if payback_months > 24:
            risk_level = "high"
        elif payback_months > 12:
            risk_level = "medium"
        
        return {
            'investment_type': investment_type.value,
            'investment_amount': amount,
            'expected_monthly_revenue': expected_revenue_increase,
            'timeline_months': timeline_months,
            'total_expected_revenue': total_expected_revenue,
            'roi_percentage': roi_percentage,
            'payback_period_months': payback_months,
            'npv': npv,
            'risk_level': risk_level,
            'recommendation': 'proceed' if roi_percentage > 20 and payback_months < 18 else 'review_carefully'
        }
    
    async def get_roi_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive ROI dashboard data"""
        
        now = datetime.utcnow()
        
        # Calculate ROI for different periods
        periods = {
            'last_30_days': now - timedelta(days=30),
            'last_90_days': now - timedelta(days=90),
            'last_year': now - timedelta(days=365)
        }
        
        period_analyses = {}
        for period_name, start_date in periods.items():
            analysis = await self.calculate_roi_analysis(start_date, now)
            period_analyses[period_name] = {
                'roi_percentage': analysis.roi_percentage,
                'total_revenue': analysis.total_revenue,
                'total_investment': analysis.total_investment,
                'payback_period': analysis.roi_metrics.get(ROIMetricType.PAYBACK_PERIOD, 0),
                'customer_ltv': analysis.roi_metrics.get(ROIMetricType.CUSTOMER_LTV, 0)
            }
        
        # Top performing platforms
        last_90_days = now - timedelta(days=90)
        recent_analysis = await self.calculate_roi_analysis(last_90_days, now)
        
        top_platforms = sorted(
            recent_analysis.platform_performance.items(),
            key=lambda x: x[1]['roi_percentage'],
            reverse=True
        )[:5]
        
        return {
            'timestamp': now.isoformat(),
            'period_analyses': period_analyses,
            'revenue_streams': recent_analysis.revenue_breakdown,
            'investment_breakdown': recent_analysis.investment_breakdown,
            'top_platforms': {platform: metrics for platform, metrics in top_platforms},
            'customer_metrics': recent_analysis.customer_metrics,
            'recommendations': recent_analysis.recommendations[:5],  # Top 5 recommendations
            'overall_health': 'excellent' if recent_analysis.roi_percentage > 50 else 'good' if recent_analysis.roi_percentage > 20 else 'needs_attention'
        }

# Factory function
def create_roi_calculator(config: Optional[Dict] = None) -> DistributionROICalculator:
    """Create ROI calculator instance"""
    return DistributionROICalculator(config)

# Example usage
async def main() -> None:
    """Example usage of ROI calculator"""
    calculator = create_roi_calculator()
    
    # Record some revenue and investment
    await calculator.record_revenue(RevenueStream.SUBSCRIPTION, 5000.0, customer_id="cust_001")
    await calculator.record_investment(InvestmentType.MARKETING, 1000.0, "Social media campaign")
    
    # Calculate ROI analysis
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    analysis = await calculator.calculate_roi_analysis(start_date, end_date)
    
    print(f"ROI: {analysis.roi_percentage:.2f}%")
    print(f"Total Revenue: ${analysis.total_revenue:,.2f}")
    print(f"Total Investment: ${analysis.total_investment:,.2f}")
    
    # Simulate investment scenario
    scenario = await calculator.simulate_investment_scenario(
        InvestmentType.DEVELOPMENT,
        50000.0,
        5000.0,
        12
    )
    
    print(f"Investment scenario ROI: {scenario['roi_percentage']:.2f}%")
    print(f"Payback period: {scenario['payback_period_months']:.1f} months")

if __name__ == "__main__":
    asyncio.run(main())